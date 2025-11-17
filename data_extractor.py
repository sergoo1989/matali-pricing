"""
مستخرج البيانات التلقائي من الطلبات و P&L
Auto Data Extractor from Orders and P&L

يستخرج تلقائياً كل ما يمكن استخراجه من البيانات الأساسية:
- بيانات المنافسين من الطلبات
- بيانات العملاء من الطلبات
- بيانات المبيعات من الطلبات
- بيانات الموسمية من الطلبات
- تحليل السوق (موجود بالفعل في market_analyzer.py)
"""

import pandas as pd
import numpy as np
from datetime import datetime


class DataExtractor:
    """مستخرج البيانات التلقائي"""
    
    def __init__(self, orders_df=None, pnl_df=None):
        """
        Parameters:
        -----------
        orders_df : pd.DataFrame
            بيانات الطلبات الفعلية
        pnl_df : pd.DataFrame
            بيانات P&L
        """
        self.orders_df = orders_df
        self.pnl_df = pnl_df
    
    def extract_competitors_data(self):
        """
        استخراج بيانات المنافسين من الطلبات
        
        يحلل:
        - متوسط أسعار السوق من الطلبات المرفوضة أو المقارنة
        - نطاقات الأسعار التنافسية
        - شرائح الخدمات والأسعار
        
        Returns:
        --------
        pd.DataFrame
            بيانات المنافسين المستخرجة
        """
        if self.orders_df is None or self.orders_df.empty:
            return None
        
        df = self.orders_df.copy()
        
        # استخراج بيانات المنافسين من العواميد الموجودة
        competitors_data = []
        
        # تجميع حسب نوع الخدمة والمنطقة
        if 'service_type' in df.columns and 'selling_price' in df.columns:
            
            # داخل الرياض
            if 'shipping_inside_riyadh' in df.columns:
                riyadh_stats = df.groupby('service_type').agg({
                    'shipping_inside_riyadh': ['mean', 'min', 'max', 'std'],
                    'order_number': 'count'
                }).reset_index()
                
                for _, row in riyadh_stats.iterrows():
                    service = row['service_type']
                    avg_price = row['shipping_inside_riyadh']['mean']
                    min_price = row['shipping_inside_riyadh']['min']
                    max_price = row['shipping_inside_riyadh']['max']
                    std_price = row['shipping_inside_riyadh']['std']
                    sample_size = row['order_number']['count']
                    
                    competitors_data.append({
                        'competitor_name': 'متوسط السوق (من بيانات فعلية)',
                        'service_type': service,
                        'region': 'داخل الرياض',
                        'price': avg_price,
                        'min_price': min_price,
                        'max_price': max_price,
                        'price_std': std_price,
                        'sample_size': sample_size,
                        'competitive_level': self._calculate_competitive_level(std_price, avg_price)
                    })
            
            # خارج الرياض
            if 'shipping_outside_riyadh' in df.columns:
                outside_stats = df.groupby('service_type').agg({
                    'shipping_outside_riyadh': ['mean', 'min', 'max', 'std'],
                    'order_number': 'count'
                }).reset_index()
                
                for _, row in outside_stats.iterrows():
                    service = row['service_type']
                    avg_price = row['shipping_outside_riyadh']['mean']
                    min_price = row['shipping_outside_riyadh']['min']
                    max_price = row['shipping_outside_riyadh']['max']
                    std_price = row['shipping_outside_riyadh']['std']
                    sample_size = row['order_number']['count']
                    
                    competitors_data.append({
                        'competitor_name': 'متوسط السوق (من بيانات فعلية)',
                        'service_type': service,
                        'region': 'خارج الرياض',
                        'price': avg_price,
                        'min_price': min_price,
                        'max_price': max_price,
                        'price_std': std_price,
                        'sample_size': sample_size,
                        'competitive_level': self._calculate_competitive_level(std_price, avg_price)
                    })
        
        if competitors_data:
            return pd.DataFrame(competitors_data)
        
        return None
    
    def extract_customers_data(self):
        """
        استخراج بيانات العملاء من الطلبات
        
        يحلل:
        - حجم كل عميل (عدد الطلبات)
        - متوسط قيمة الطلب
        - أنواع الخدمات المفضلة
        - وقت التجهيز المعتاد
        - درجة الرضا (من معدل الإلغاء)
        
        Returns:
        --------
        pd.DataFrame
            بيانات العملاء المستخرجة
        """
        if self.orders_df is None or self.orders_df.empty:
            return None
        
        df = self.orders_df.copy()
        
        if 'customer_name' not in df.columns:
            return None
        
        # تجميع بيانات العملاء
        customer_stats = df.groupby('customer_name').agg({
            'order_number': 'count',  # عدد الطلبات
            'selling_price': 'mean',  # متوسط قيمة الطلب
            'service_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],  # الخدمة الأكثر استخدامًا
        }).reset_index()
        
        customer_stats.columns = ['customer_name', 'total_orders', 'avg_order_value', 'preferred_service']
        
        # حساب الحجم الشهري (افتراض البيانات لمدة معينة)
        if 'date' in df.columns or 'order_date' in df.columns:
            date_col = 'date' if 'date' in df.columns else 'order_date'
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # حساب عدد الأشهر في البيانات
            months_span = (df[date_col].max() - df[date_col].min()).days / 30
            months_span = max(months_span, 1)  # على الأقل شهر واحد
            
            customer_stats['volume_monthly'] = (customer_stats['total_orders'] / months_span).round(0).astype(int)
        else:
            customer_stats['volume_monthly'] = customer_stats['total_orders']
        
        # حساب درجة الرضا (من 1-10)
        # الافتراض: كلما زادت الطلبات، زاد الرضا
        customer_stats['satisfaction_score'] = customer_stats['total_orders'].apply(
            lambda x: min(10, 5 + (x / customer_stats['total_orders'].max() * 5))
        ).round(1)
        
        # تقدير تاريخ انتهاء العقد (بعد 6 أشهر من آخر طلب)
        if 'date' in df.columns or 'order_date' in df.columns:
            last_order = df.groupby('customer_name')[date_col].max().reset_index()
            last_order.columns = ['customer_name', 'last_order_date']
            customer_stats = customer_stats.merge(last_order, on='customer_name', how='left')
            customer_stats['contract_end_date'] = customer_stats['last_order_date'] + pd.DateOffset(months=6)
        else:
            customer_stats['contract_end_date'] = pd.Timestamp.now() + pd.DateOffset(months=6)
        
        # إضافة السعر الحالي
        current_price = df.groupby('customer_name')['selling_price'].last().reset_index()
        current_price.columns = ['customer_name', 'current_price']
        customer_stats = customer_stats.merge(current_price, on='customer_name', how='left')
        
        # إضافة تصنيف العميل
        customer_stats['customer_segment'] = customer_stats['total_orders'].apply(
            lambda x: 'عميل VIP' if x > customer_stats['total_orders'].quantile(0.75) else
                     'عميل متوسط' if x > customer_stats['total_orders'].quantile(0.25) else
                     'عميل جديد'
        )
        
        return customer_stats
    
    def extract_sales_history(self):
        """
        استخراج بيانات المبيعات التاريخية من الطلبات
        
        Returns:
        --------
        pd.DataFrame
            بيانات المبيعات التاريخية
        """
        if self.orders_df is None or self.orders_df.empty:
            return None
        
        df = self.orders_df.copy()
        
        # التأكد من وجود عمود التاريخ
        date_col = None
        for col in ['date', 'order_date', 'created_date', 'Date', 'ORDER_DATE']:
            if col in df.columns:
                date_col = col
                break
        
        if date_col is None:
            return None
        
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # إنشاء أعمدة السنة والشهر
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['year_month'] = df[date_col].dt.to_period('M').astype(str)
        
        # تجميع حسب السنة والشهر
        sales_history = df.groupby(['year', 'month', 'year_month']).agg({
            'order_number': 'count',
            'selling_price': 'sum'
        }).reset_index()
        
        sales_history.columns = ['year', 'month', 'year_month', 'total_orders', 'total_revenue']
        
        # حساب متوسط قيمة الطلب
        sales_history['avg_order_value'] = sales_history['total_revenue'] / sales_history['total_orders']
        
        # حساب معدل النمو الشهري
        sales_history = sales_history.sort_values('year_month')
        sales_history['growth_rate'] = sales_history['total_revenue'].pct_change() * 100
        
        return sales_history
    
    def extract_seasonality_data(self):
        """
        استخراج بيانات الموسمية من الطلبات
        
        Returns:
        --------
        pd.DataFrame
            بيانات الموسمية الشهرية
        """
        if self.orders_df is None or self.orders_df.empty:
            return None
        
        df = self.orders_df.copy()
        
        # التأكد من وجود عمود التاريخ
        date_col = None
        for col in ['date', 'order_date', 'created_date', 'Date', 'ORDER_DATE']:
            if col in df.columns:
                date_col = col
                break
        
        if date_col is None:
            return None
        
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        # استخراج الشهر
        df['month'] = df[date_col].dt.month
        df['month_name'] = df[date_col].dt.strftime('%B')
        
        # تجميع حسب الشهر
        seasonality = df.groupby(['month', 'month_name']).agg({
            'order_number': 'count',
            'selling_price': 'sum'
        }).reset_index()
        
        seasonality.columns = ['month', 'month_name', 'total_orders', 'total_revenue']
        
        # حساب متوسط الطلبات والإيرادات
        avg_orders = seasonality['total_orders'].mean()
        avg_revenue = seasonality['total_revenue'].mean()
        
        # حساب مؤشر الموسمية (1.0 = متوسط)
        seasonality['seasonality_index'] = seasonality['total_orders'] / avg_orders
        seasonality['revenue_index'] = seasonality['total_revenue'] / avg_revenue
        
        # تصنيف الموسمية
        seasonality['season_type'] = seasonality['seasonality_index'].apply(
            lambda x: 'ذروة' if x > 1.2 else
                     'مرتفع' if x > 1.0 else
                     'متوسط' if x > 0.8 else
                     'منخفض'
        )
        
        # ترتيب حسب الشهر
        seasonality = seasonality.sort_values('month')
        
        return seasonality
    
    def _calculate_competitive_level(self, std, mean):
        """حساب مستوى المنافسة بناءً على التشتت"""
        if mean == 0 or pd.isna(std):
            return 'غير محدد'
        
        cv = (std / mean) * 100  # معامل الاختلاف
        
        if cv < 10:
            return 'منافسة عالية (أسعار متقاربة)'
        elif cv < 20:
            return 'منافسة متوسطة'
        else:
            return 'منافسة منخفضة (أسعار متباعدة)'
    
    def extract_all(self):
        """
        استخراج جميع البيانات دفعة واحدة
        
        Returns:
        --------
        dict
            قاموس يحتوي على جميع البيانات المستخرجة
        """
        return {
            'competitors': self.extract_competitors_data(),
            'customers': self.extract_customers_data(),
            'sales_history': self.extract_sales_history(),
            'seasonality': self.extract_seasonality_data()
        }
