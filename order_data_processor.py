"""
معالج بيانات الطلبات الكبيرة
Order Data Processor for Large Datasets

يوفر معالجة فعالة لملفات الطلبات الكبيرة مع:
- تحسين استخدام الذاكرة
- معالجة على دفعات (chunks)
- تحليل شامل للشحن والمناطق
- تحسين التسعير بناءً على البيانات الفعلية
"""

import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from pathlib import Path
import pickle


class OrderDataProcessor:
    """معالج بيانات الطلبات مع تحسين الذاكرة"""
    
    def __init__(self, file_path=None, dataframe=None, chunksize=10000):
        """
        تهيئة المعالج
        
        Parameters:
        -----------
        file_path : str
            مسار ملف البيانات
        dataframe : pd.DataFrame
            DataFrame جاهز (اختياري)
        chunksize : int
            حجم الدفعة للمعالجة
        """
        self.file_path = file_path
        self.chunksize = chunksize
        
        if dataframe is not None:
            self.df = dataframe
        elif file_path is not None:
            self.df = self.load_data()
        else:
            self.df = None
    
    def load_data(self, sample_size=None):
        """
        تحميل البيانات بكفاءة
        
        Parameters:
        -----------
        sample_size : int
            عدد الصفوف لأخذ عينة (None = كل البيانات)
        
        Returns:
        --------
        pd.DataFrame
            البيانات المحملة
        """
        try:
            if str(self.file_path).endswith('.csv'):
                # ملفات سلة: UTF-16 LE مع Tab separator
                # محاولة UTF-16 أولاً (ملفات سلة 2024-2025)
                try:
                    chunks = []
                    
                    for chunk in pd.read_csv(
                        self.file_path,
                        chunksize=self.chunksize,
                        encoding='utf-16',
                        sep='\t',  # Tab-separated في ملفات سلة
                        low_memory=False
                    ):
                        # تنظيف كل دفعة
                        chunk = self.clean_orders_data(chunk)
                        chunks.append(chunk)
                        
                        # إذا كان هناك حد للعينة
                        if sample_size and len(pd.concat(chunks, ignore_index=True)) >= sample_size:
                            break
                    
                    df = pd.concat(chunks, ignore_index=True)
                    
                    if sample_size:
                        df = df.sample(min(sample_size, len(df)))
                
                except (UnicodeDecodeError, pd.errors.ParserError):
                    # إذا فشل UTF-16، جرب UTF-8 العادي
                    try:
                        chunks = []
                        
                        for chunk in pd.read_csv(
                            self.file_path,
                            chunksize=self.chunksize,
                            encoding='utf-8',
                            low_memory=False
                        ):
                            chunk = self.clean_orders_data(chunk)
                            chunks.append(chunk)
                            
                            if sample_size and len(pd.concat(chunks, ignore_index=True)) >= sample_size:
                                break
                        
                        df = pd.concat(chunks, ignore_index=True)
                        
                        if sample_size:
                            df = df.sample(min(sample_size, len(df)))
                    
                    except Exception as e:
                        st.error(f"فشل قراءة الملف: {str(e)}")
                        return pd.DataFrame()
                
            else:  # Excel
                df = pd.read_excel(self.file_path)
                df = self.clean_orders_data(df)
                
                if sample_size:
                    df = df.sample(min(sample_size, len(df)))
            
            return self.optimize_memory(df)
            
        except Exception as e:
            st.error(f"خطأ في تحميل البيانات: {str(e)}")
            return pd.DataFrame()
    
    def clean_orders_data(self, df):
        """
        تنظيف بيانات الطلبات
        
        Parameters:
        -----------
        df : pd.DataFrame
            البيانات الخام
        
        Returns:
        --------
        pd.DataFrame
            البيانات المنظفة
        """
        # تحويل التواريخ
        date_columns = [col for col in df.columns if 'AT' in col.upper() or 'DATE' in col.upper()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # ================================
        # حساب وقت تجهيز الطلب (prep time)
        # ================================
        created_col = None
        packed_col = None
        
        # البحث عن أعمدة التاريخ
        for col in df.columns:
            col_upper = col.upper()
            if 'CREATED' in col_upper and 'AT' in col_upper:
                created_col = col
            if 'PACKED' in col_upper and 'AT' in col_upper:
                packed_col = col
        
        if created_col and packed_col:
            # حساب الفرق بالدقائق
            df['prep_time_minutes'] = (
                (df[packed_col] - df[created_col]).dt.total_seconds() / 60
            )
            
            # تنظيف القيم السالبة والشاذة
            df.loc[df['prep_time_minutes'] < 0, 'prep_time_minutes'] = np.nan
            df.loc[df['prep_time_minutes'] > 1440, 'prep_time_minutes'] = np.nan  # أكثر من يوم
        
        # تنظيف الأوزان
        if 'SHIPMENT WEIGHT' in df.columns:
            df['SHIPMENT WEIGHT'] = df['SHIPMENT WEIGHT'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
        
        # تنظيف المبالغ
        amount_columns = [col for col in df.columns if any(x in col.upper() for x in ['AMOUNT', 'COST', 'FEE', 'PRICE'])]
        for col in amount_columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
        
        return df
    
    def optimize_memory(self, df):
        """
        تحسين استخدام الذاكرة
        
        Parameters:
        -----------
        df : pd.DataFrame
            البيانات
        
        Returns:
        --------
        pd.DataFrame
            البيانات المحسنة
        """
        # تحويل النصوص لـ category (يوفر 90% من الذاكرة)
        for col in df.select_dtypes(include=['object']).columns:
            num_unique = df[col].nunique()
            num_total = len(df[col])
            
            if num_unique / num_total < 0.5:  # إذا كان التكرار عالي
                df[col] = df[col].astype('category')
        
        # تحسين الأرقام الصحيحة
        for col in df.select_dtypes(include=['int']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # تحسين الأرقام العشرية
        for col in df.select_dtypes(include=['float']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    def analyze_prep_time(self):
        """
        تحليل وقت تجهيز الطلبات
        
        Returns:
        --------
        dict
            تحليل شامل لوقت التجهيز
        """
        if self.df is None or 'prep_time_minutes' not in self.df.columns:
            return {
                'avg_prep_time': 0,
                'median_prep_time': 0,
                'min_prep_time': 0,
                'max_prep_time': 0,
                'by_customer': pd.DataFrame(),
                'distribution': {}
            }
        
        # إزالة القيم الفارغة
        valid_data = self.df.dropna(subset=['prep_time_minutes'])
        
        if len(valid_data) == 0:
            return {
                'avg_prep_time': 0,
                'median_prep_time': 0,
                'min_prep_time': 0,
                'max_prep_time': 0,
                'by_customer': pd.DataFrame(),
                'distribution': {}
            }
        
        # الإحصائيات العامة
        avg_prep = valid_data['prep_time_minutes'].mean()
        median_prep = valid_data['prep_time_minutes'].median()
        min_prep = valid_data['prep_time_minutes'].min()
        max_prep = valid_data['prep_time_minutes'].max()
        
        # التحليل حسب العميل
        customer_col = None
        for col in valid_data.columns:
            if 'CUSTOMER' in col.upper() and 'PHONE' in col.upper():
                customer_col = col
                break
        
        by_customer = pd.DataFrame()
        if customer_col:
            by_customer = (
                valid_data.groupby(customer_col)['prep_time_minutes']
                .agg(['mean', 'count', 'min', 'max'])
                .reset_index()
            )
            by_customer.columns = ['customer', 'avg_prep_time', 'order_count', 'min_prep', 'max_prep']
            by_customer = by_customer.sort_values('avg_prep_time', ascending=False)
        
        # توزيع الأوقات
        distribution = {
            'very_fast': len(valid_data[valid_data['prep_time_minutes'] <= 30]),  # أقل من 30 دقيقة
            'fast': len(valid_data[(valid_data['prep_time_minutes'] > 30) & (valid_data['prep_time_minutes'] <= 60)]),  # 30-60 دقيقة
            'normal': len(valid_data[(valid_data['prep_time_minutes'] > 60) & (valid_data['prep_time_minutes'] <= 120)]),  # 1-2 ساعة
            'slow': len(valid_data[(valid_data['prep_time_minutes'] > 120) & (valid_data['prep_time_minutes'] <= 240)]),  # 2-4 ساعات
            'very_slow': len(valid_data[valid_data['prep_time_minutes'] > 240])  # أكثر من 4 ساعات
        }
        
        return {
            'avg_prep_time': avg_prep,
            'median_prep_time': median_prep,
            'min_prep_time': min_prep,
            'max_prep_time': max_prep,
            'by_customer': by_customer,
            'distribution': distribution,
            'total_orders': len(valid_data)
        }


class PricingOptimizer:
    """محسّن التسعير بناءً على بيانات الطلبات الفعلية"""
    
    def __init__(self, orders_data):
        """
        تهيئة المحسّن
        
        Parameters:
        -----------
        orders_data : pd.DataFrame
            بيانات الطلبات
        """
        self.orders = orders_data
        self.shipping_analysis = self.analyze_shipping_costs()
        self.regional_analysis = self.analyze_regional_patterns()
        self.partner_performance = self.analyze_partner_performance()
    
    def analyze_shipping_costs(self):
        """تحليل تكاليف الشحن من البيانات الفعلية"""
        try:
            # التحقق من الأعمدة المتاحة
            available_cols = self.orders.columns.tolist()
            
            # الأعمدة المطلوبة (مرنة)
            city_col = next((col for col in available_cols if 'DESTINATION' in col.upper() and 'CITY' in col.upper()), None)
            
            # البحث عن عمود التكلفة
            cost_col = None
            for col in ['SHIPPING COST', 'COD FEE', 'DELIVERY FEE', 'SHIPPING FEE']:
                if col in available_cols:
                    cost_col = col
                    break
            
            # إذا لم يوجد عمود تكلفة، نستخدم ORDER AMOUNT كمقياس بديل
            if not cost_col and 'ORDER AMOUNT' in available_cols:
                st.info("💡 لم يتم العثور على عمود تكلفة الشحن، سيتم استخدام ORDER AMOUNT")
                cost_col = 'ORDER AMOUNT'
            
            if not city_col or not cost_col:
                st.warning("⚠️ الأعمدة المطلوبة غير موجودة. تأكد من وجود DESTINATION CITY و SHIPPING COST")
                return pd.DataFrame()
            
            agg_dict = {
                cost_col: 'mean',
                'ORDER ID': 'count'
            }
            
            # إضافة الأعمدة الاختيارية إن وجدت
            if 'SHIPMENT WEIGHT' in available_cols:
                agg_dict['SHIPMENT WEIGHT'] = 'mean'
            if 'ORDER AMOUNT' in available_cols and cost_col != 'ORDER AMOUNT':
                agg_dict['ORDER AMOUNT'] = 'mean'
            if 'COD FEE' in available_cols:
                agg_dict['COD FEE'] = 'mean'
            
            group_cols = [city_col]
            if 'SHIPPING PARTNER' in available_cols:
                group_cols.append('SHIPPING PARTNER')
            elif 'COURIER PARTNER' in available_cols:
                group_cols.append('COURIER PARTNER')
            
            shipping_data = self.orders.groupby(group_cols).agg(agg_dict).reset_index()
            shipping_data.columns = [col if isinstance(col, str) else col[0] for col in shipping_data.columns]
            
            return shipping_data
            
        except Exception as e:
            st.warning(f"خطأ في تحليل الشحن: {str(e)}")
            return pd.DataFrame()
    
    def analyze_regional_patterns(self):
        """تحليل أنماط الطلبات حسب المنطقة"""
        try:
            # البحث عن عمود المدينة
            city_col = next((col for col in self.orders.columns 
                           if 'DESTINATION' in col.upper() and 'CITY' in col.upper()), None)
            
            if not city_col:
                st.warning("⚠️ لم يتم العثور على عمود DESTINATION CITY")
                return pd.DataFrame()
            
            agg_dict = {'ORDER ID': 'count'}
            
            # إضافة الأعمدة المتاحة
            if 'ORDER AMOUNT' in self.orders.columns:
                agg_dict['ORDER AMOUNT'] = ['mean', 'median', 'sum']
            if 'SHIPPING COST' in self.orders.columns:
                agg_dict['SHIPPING COST'] = 'mean'
            if 'COD FEE' in self.orders.columns:
                agg_dict['COD FEE'] = ['mean', 'sum']
            if 'SHIPMENT WEIGHT' in self.orders.columns:
                agg_dict['SHIPMENT WEIGHT'] = 'mean'
            
            regional_stats = self.orders.groupby(city_col).agg(agg_dict)
            regional_stats.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col 
                                     for col in regional_stats.columns.values]
            
            return regional_stats.reset_index()
            
        except Exception as e:
            st.warning(f"خطأ في التحليل الإقليمي: {str(e)}")
            return pd.DataFrame()
    
    def analyze_partner_performance(self):
        """تحليل أداء شركاء الشحن"""
        try:
            if 'SHIPPING PARTNER' not in self.orders.columns:
                return pd.DataFrame()
            
            partner_stats = self.orders.groupby('SHIPPING PARTNER').agg({
                'ORDER ID': 'count',
                'SHIPPING COST': 'mean'
            }).reset_index()
            
            partner_stats.columns = ['Partner', 'Order_Count', 'Avg_Cost']
            partner_stats['Performance_Score'] = (
                partner_stats['Order_Count'] / partner_stats['Avg_Cost']
            )
            
            return partner_stats.sort_values('Performance_Score', ascending=False)
            
        except Exception as e:
            st.warning(f"خطأ في تحليل الشركاء: {str(e)}")
            return pd.DataFrame()
    
    def calculate_optimal_shipping_price(self, city, weight, order_value, payment_method='PREPAID'):
        """
        حساب سعر الشحن الأمثل بناءً على البيانات التاريخية
        
        Parameters:
        -----------
        city : str
            المدينة
        weight : float
            الوزن
        order_value : float
            قيمة الطلب
        payment_method : str
            طريقة الدفع
        
        Returns:
        --------
        float
            سعر الشحن المحسوب
        """
        if self.shipping_analysis.empty:
            # سعر افتراضي
            return 25.0
        
        # بيانات الشحن للمدينة
        city_data = self.shipping_analysis[
            self.shipping_analysis['DESTINATION CITY'] == city
        ]
        
        if len(city_data) > 0:
            avg_shipping_cost = city_data['SHIPPING COST'].mean()
            avg_weight = city_data.get('SHIPMENT WEIGHT', pd.Series([1.0])).mean()
        else:
            # استخدام المتوسط العام
            avg_shipping_cost = self.shipping_analysis['SHIPPING COST'].mean()
            avg_weight = self.shipping_analysis.get('SHIPMENT WEIGHT', pd.Series([1.0])).mean()
        
        # تعديل حسب الوزن
        weight_factor = max(0.5, min(2.0, weight / max(avg_weight, 0.5)))
        
        # تعديل حسب قيمة الطلب (خصم للطلبات الكبيرة)
        order_value_factor = 1.0
        if order_value > 500:
            order_value_factor = 0.8
        elif order_value > 200:
            order_value_factor = 0.9
        
        # تعديل حسب طريقة الدفع
        payment_factor = 0.9 if payment_method == 'PREPAID' else 1.1
        
        # السعر الأساسي + هامش ربح
        base_price = avg_shipping_cost * weight_factor
        profit_margin = 0.25  # 25% هامش ربح
        
        final_price = base_price * order_value_factor * payment_factor * (1 + profit_margin)
        
        return round(final_price, 2)
    
    def recommend_shipping_partner(self, city, weight=None, urgency='normal'):
        """
        توصية شريك شحن بناءً على الأداء السابق
        
        Parameters:
        -----------
        city : str
            المدينة
        weight : float
            الوزن (اختياري)
        urgency : str
            مستوى الاستعجال
        
        Returns:
        --------
        str
            اسم الشريك الموصى به
        """
        if self.shipping_analysis.empty or 'SHIPPING PARTNER' not in self.shipping_analysis.columns:
            return "الشريك الافتراضي"
        
        city_partners = self.shipping_analysis[
            self.shipping_analysis['DESTINATION CITY'] == city
        ]
        
        if len(city_partners) > 0:
            # ترتيب الشركاء حسب التكلفة والموثوقية
            city_partners = city_partners.copy()
            city_partners['score'] = (
                city_partners['SHIPPING COST'] * 0.6 +
                (1 / city_partners['ORDER ID'].clip(lower=1)) * 0.4
            )
            
            best_partner = city_partners.loc[city_partners['score'].idxmin()]
            return best_partner['SHIPPING PARTNER']
        
        # إرجاع الشريك الأفضل عموماً
        if not self.partner_performance.empty:
            return self.partner_performance.iloc[0]['Partner']
        
        return "الشريك الافتراضي"
    
    def calculate_additional_costs(self, weight, payment_method, order_value=0):
        """
        حساب التكاليف الإضافية
        
        Parameters:
        -----------
        weight : float
            الوزن
        payment_method : str
            طريقة الدفع
        order_value : float
            قيمة الطلب
        
        Returns:
        --------
        dict
            التكاليف الإضافية مفصلة
        """
        # رسوم الدفع عند الاستلام
        cod_fee = 16.52 if payment_method == 'POSTPAID' else 0
        
        # رسوم التغليف (حسب الوزن)
        packaging_fee = max(5, weight * 2)
        
        # رسوم المناولة
        handling_fee = 3.0
        
        # رسوم التأمين (للطلبات الكبيرة)
        insurance_fee = order_value * 0.01 if order_value > 1000 else 0
        
        return {
            'cod_fee': round(cod_fee, 2),
            'packaging_fee': round(packaging_fee, 2),
            'handling_fee': round(handling_fee, 2),
            'insurance_fee': round(insurance_fee, 2),
            'total_additional': round(cod_fee + packaging_fee + handling_fee + insurance_fee, 2)
        }
    
    def save_cache(self, cache_file='pricing_cache.pkl'):
        """حفظ التحليلات للتسريع"""
        try:
            cache_data = {
                'shipping_analysis': self.shipping_analysis,
                'regional_analysis': self.regional_analysis,
                'partner_performance': self.partner_performance
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            return True
        except Exception as e:
            st.warning(f"خطأ في حفظ الكاش: {str(e)}")
            return False
    
    @staticmethod
    def load_cache(cache_file='pricing_cache.pkl'):
        """تحميل التحليلات المحفوظة"""
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            st.warning(f"خطأ في تحميل الكاش: {str(e)}")
            return None


def get_memory_usage(df):
    """حساب استخدام الذاكرة لـ DataFrame"""
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_mb = memory_bytes / (1024 ** 2)
    return f"{memory_mb:.2f} MB"


def get_data_summary(df):
    """ملخص شامل للبيانات"""
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage': get_memory_usage(df),
        'date_range': None,
        'missing_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum()
    }
    
    # نطاق التواريخ
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) > 0:
        first_date = df[date_cols[0]].min()
        last_date = df[date_cols[0]].max()
        summary['date_range'] = f"{first_date.date()} إلى {last_date.date()}"
    
    return summary
