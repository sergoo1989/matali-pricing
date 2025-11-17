"""
محلل بيانات السوق التلقائي
Automatic Market Data Analyzer

يستخلص دراسة السوق من بيانات الطلبات الفعلية
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional


class MarketDataAnalyzer:
    """محلل بيانات السوق من الطلبات"""
    
    def __init__(self, orders_df: pd.DataFrame):
        """
        تهيئة المحلل
        
        Parameters:
        -----------
        orders_df : pd.DataFrame
            بيانات الطلبات
        """
        self.orders_df = orders_df
        self.market_analysis = None
    
    def analyze_market(self) -> Dict:
        """
        تحليل شامل للسوق من بيانات الطلبات
        
        Returns:
        --------
        dict
            تحليل كامل للسوق
        """
        if self.orders_df is None or self.orders_df.empty:
            return None
        
        analysis = {
            'overview': self._analyze_overview(),
            'seasonal': self._analyze_seasonality(),
            'geographic': self._analyze_geography(),
            'customer_behavior': self._analyze_customer_behavior(),
            'product_trends': self._analyze_product_trends(),
            'growth': self._analyze_growth(),
            'competition': self._estimate_competition()
        }
        
        self.market_analysis = analysis
        return analysis
    
    def _analyze_overview(self) -> Dict:
        """تحليل عام للسوق"""
        df = self.orders_df.copy()
        
        # حجم السوق
        total_orders = len(df)
        
        # القيمة الإجمالية
        if 'ORDER AMOUNT' in df.columns:
            total_value = df['ORDER AMOUNT'].sum()
            avg_order_value = df['ORDER AMOUNT'].mean()
        else:
            total_value = 0
            avg_order_value = 0
        
        # معدل النمو الشهري (إذا كانت هناك بيانات زمنية)
        growth_rate = self._calculate_growth_rate(df)
        
        return {
            'total_orders': int(total_orders),
            'total_value': float(total_value),
            'avg_order_value': float(avg_order_value),
            'monthly_growth_rate': float(growth_rate) if growth_rate else 0,
            'market_size_estimate': total_value * 12 if total_value > 0 else 0  # تقدير سنوي
        }
    
    def _analyze_seasonality(self) -> Dict:
        """تحليل الموسمية"""
        df = self.orders_df.copy()
        
        # محاولة استخراج التاريخ
        date_col = None
        for col in ['ORDER DATE', 'ORDER CREATED AT', 'CREATED AT', 'Date']:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            return {
                'has_seasonal_data': False,
                'peak_months': [],
                'low_months': [],
                'seasonality_index': 0
            }
        
        try:
            df['date'] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=['date'])
            
            if df.empty:
                return {'has_seasonal_data': False}
            
            # تحليل شهري
            df['month'] = df['date'].dt.month
            df['month_name'] = df['date'].dt.strftime('%B')
            
            monthly_orders = df.groupby(['month', 'month_name']).size().reset_index(name='orders')
            monthly_orders = monthly_orders.sort_values('orders', ascending=False)
            
            # أعلى 3 أشهر
            peak_months = monthly_orders.head(3)[['month_name', 'orders']].to_dict('records')
            
            # أقل 3 أشهر
            low_months = monthly_orders.tail(3)[['month_name', 'orders']].to_dict('records')
            
            # مؤشر الموسمية (الانحراف المعياري / المتوسط)
            seasonality_index = float(monthly_orders['orders'].std() / monthly_orders['orders'].mean())
            
            return {
                'has_seasonal_data': True,
                'peak_months': peak_months,
                'low_months': low_months,
                'seasonality_index': seasonality_index,
                'monthly_distribution': monthly_orders.to_dict('records')
            }
            
        except Exception:
            return {'has_seasonal_data': False}
    
    def _analyze_geography(self) -> Dict:
        """تحليل جغرافي للسوق"""
        df = self.orders_df.copy()
        
        # البحث عن عمود المدينة
        city_col = None
        for col in ['DESTINATION CITY', 'CITY', 'City', 'المدينة']:
            if col in df.columns:
                city_col = col
                break
        
        if not city_col:
            return {'has_geographic_data': False}
        
        # تحليل المدن
        city_analysis = df.groupby(city_col).agg({
            city_col: 'count'
        }).rename(columns={city_col: 'orders'}).reset_index()
        city_analysis.columns = ['city', 'orders']
        
        # حساب النسب
        total_orders = city_analysis['orders'].sum()
        city_analysis['percentage'] = (city_analysis['orders'] / total_orders * 100).round(2)
        
        # إضافة القيمة إذا كانت متوفرة
        if 'ORDER AMOUNT' in df.columns:
            city_value = df.groupby(city_col)['ORDER AMOUNT'].sum().reset_index()
            city_value.columns = ['city', 'total_value']
            city_analysis = city_analysis.merge(city_value, on='city', how='left')
        
        # ترتيب حسب عدد الطلبات
        city_analysis = city_analysis.sort_values('orders', ascending=False)
        
        # أكبر 5 مدن
        top_cities = city_analysis.head(5).to_dict('records')
        
        # نسبة التركز (أكبر 3 مدن)
        concentration_ratio = float(city_analysis.head(3)['percentage'].sum())
        
        return {
            'has_geographic_data': True,
            'total_cities': len(city_analysis),
            'top_cities': top_cities,
            'concentration_ratio': concentration_ratio,
            'all_cities': city_analysis.to_dict('records')
        }
    
    def _analyze_customer_behavior(self) -> Dict:
        """تحليل سلوك العملاء"""
        df = self.orders_df.copy()
        
        behavior = {}
        
        # طريقة الدفع
        if 'PAYMENT METHOD' in df.columns:
            payment_dist = df['PAYMENT METHOD'].value_counts(normalize=True).to_dict()
            behavior['payment_methods'] = {k: float(v*100) for k, v in payment_dist.items()}
        
        # COD vs غير COD
        if 'COD FEE' in df.columns:
            cod_orders = (df['COD FEE'] > 0).sum()
            non_cod_orders = (df['COD FEE'] == 0).sum()
            total = cod_orders + non_cod_orders
            
            behavior['cod_percentage'] = float(cod_orders / total * 100) if total > 0 else 0
            behavior['non_cod_percentage'] = float(non_cod_orders / total * 100) if total > 0 else 0
        
        # متوسط قيمة الطلب
        if 'ORDER AMOUNT' in df.columns:
            behavior['avg_order_value'] = float(df['ORDER AMOUNT'].mean())
            behavior['median_order_value'] = float(df['ORDER AMOUNT'].median())
            behavior['max_order_value'] = float(df['ORDER AMOUNT'].max())
            behavior['min_order_value'] = float(df['ORDER AMOUNT'].min())
            
            # تقسيم العملاء حسب قيمة الطلب
            q1 = df['ORDER AMOUNT'].quantile(0.25)
            q2 = df['ORDER AMOUNT'].quantile(0.50)
            q3 = df['ORDER AMOUNT'].quantile(0.75)
            
            behavior['customer_segments'] = {
                'low_value': float((df['ORDER AMOUNT'] <= q1).sum() / len(df) * 100),
                'medium_value': float(((df['ORDER AMOUNT'] > q1) & (df['ORDER AMOUNT'] <= q3)).sum() / len(df) * 100),
                'high_value': float((df['ORDER AMOUNT'] > q3).sum() / len(df) * 100)
            }
        
        return behavior
    
    def _analyze_product_trends(self) -> Dict:
        """تحليل اتجاهات المنتجات"""
        df = self.orders_df.copy()
        
        trends = {}
        
        # متوسط عدد المنتجات في الطلب
        product_cols = [col for col in df.columns if 'SKU' in col.upper() or 'PRODUCT' in col.upper()]
        
        if product_cols:
            # حساب متوسط عدد المنتجات
            trends['avg_products_per_order'] = float(len(product_cols))
        
        # تحليل الوزن
        if 'WEIGHT' in df.columns or 'ORDER WEIGHT' in df.columns:
            weight_col = 'WEIGHT' if 'WEIGHT' in df.columns else 'ORDER WEIGHT'
            trends['avg_weight'] = float(df[weight_col].mean())
            trends['median_weight'] = float(df[weight_col].median())
        
        # تحليل تكلفة الشحن
        if 'SHIPPING COST' in df.columns:
            trends['avg_shipping_cost'] = float(df['SHIPPING COST'].mean())
            trends['total_shipping_revenue'] = float(df['SHIPPING COST'].sum())
        
        return trends
    
    def _analyze_growth(self) -> Dict:
        """تحليل النمو والاتجاهات"""
        df = self.orders_df.copy()
        
        # البحث عن عمود التاريخ
        date_col = None
        for col in ['ORDER DATE', 'ORDER CREATED AT', 'CREATED AT', 'Date']:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            return {'has_growth_data': False}
        
        try:
            df['date'] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=['date'])
            
            if df.empty or len(df) < 2:
                return {'has_growth_data': False}
            
            # تحليل شهري
            df['year_month'] = df['date'].dt.to_period('M')
            monthly_stats = df.groupby('year_month').agg({
                'date': 'count'
            }).rename(columns={'date': 'orders'})
            
            if len(monthly_stats) < 2:
                return {'has_growth_data': False}
            
            # حساب معدل النمو الشهري
            monthly_stats['growth_rate'] = monthly_stats['orders'].pct_change() * 100
            
            # القيمة إذا متوفرة
            if 'ORDER AMOUNT' in df.columns:
                monthly_value = df.groupby('year_month')['ORDER AMOUNT'].sum()
                monthly_stats['total_value'] = monthly_value
                monthly_stats['value_growth_rate'] = monthly_stats['total_value'].pct_change() * 100
            
            return {
                'has_growth_data': True,
                'avg_monthly_growth': float(monthly_stats['growth_rate'].mean()),
                'current_trend': 'نمو' if monthly_stats['growth_rate'].iloc[-1] > 0 else 'انخفاض',
                'monthly_data': monthly_stats.reset_index().to_dict('records')
            }
            
        except Exception:
            return {'has_growth_data': False}
    
    def _estimate_competition(self) -> Dict:
        """تقدير المنافسة في السوق"""
        df = self.orders_df.copy()
        
        # تقدير بناءً على تنوع المنتجات والمناطق
        city_col = None
        for col in ['DESTINATION CITY', 'CITY']:
            if col in df.columns:
                city_col = col
                break
        
        if not city_col:
            return {'competition_level': 'غير محدد'}
        
        # عدد المدن
        num_cities = df[city_col].nunique()
        
        # تنوع الأسعار
        price_variance = 0
        if 'ORDER AMOUNT' in df.columns:
            price_variance = float(df['ORDER AMOUNT'].std() / df['ORDER AMOUNT'].mean())
        
        # تقدير مستوى المنافسة
        if num_cities > 20 and price_variance > 0.5:
            competition_level = 'عالية'
            competition_score = 8
        elif num_cities > 10:
            competition_level = 'متوسطة'
            competition_score = 5
        else:
            competition_level = 'منخفضة'
            competition_score = 3
        
        return {
            'competition_level': competition_level,
            'competition_score': competition_score,
            'market_coverage': num_cities,
            'price_variance': price_variance
        }
    
    def _calculate_growth_rate(self, df: pd.DataFrame) -> Optional[float]:
        """حساب معدل النمو"""
        date_col = None
        for col in ['ORDER DATE', 'ORDER CREATED AT', 'CREATED AT']:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            return None
        
        try:
            df['date'] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=['date'])
            
            if len(df) < 2:
                return None
            
            # أول وآخر شهر
            df['year_month'] = df['date'].dt.to_period('M')
            monthly_orders = df.groupby('year_month').size()
            
            if len(monthly_orders) < 2:
                return None
            
            # معدل النمو بين أول وآخر شهر
            first_month = monthly_orders.iloc[0]
            last_month = monthly_orders.iloc[-1]
            
            growth_rate = ((last_month - first_month) / first_month * 100)
            return float(growth_rate)
            
        except Exception:
            return None
    
    def generate_market_report(self) -> pd.DataFrame:
        """
        توليد تقرير سوق شامل
        
        Returns:
        --------
        pd.DataFrame
            تقرير بيانات السوق
        """
        if self.market_analysis is None:
            self.analyze_market()
        
        if self.market_analysis is None:
            return pd.DataFrame()
        
        # إنشاء تقرير موحد
        report_data = []
        
        # نظرة عامة
        overview = self.market_analysis.get('overview', {})
        report_data.append({
            'category': 'حجم السوق',
            'metric': 'إجمالي الطلبات',
            'value': overview.get('total_orders', 0),
            'unit': 'طلب'
        })
        report_data.append({
            'category': 'حجم السوق',
            'metric': 'القيمة الإجمالية',
            'value': overview.get('total_value', 0),
            'unit': 'ر.س'
        })
        report_data.append({
            'category': 'حجم السوق',
            'metric': 'متوسط قيمة الطلب',
            'value': overview.get('avg_order_value', 0),
            'unit': 'ر.س'
        })
        
        # الموسمية
        seasonal = self.market_analysis.get('seasonal', {})
        if seasonal.get('has_seasonal_data'):
            report_data.append({
                'category': 'الموسمية',
                'metric': 'مؤشر الموسمية',
                'value': seasonal.get('seasonality_index', 0),
                'unit': 'نسبة'
            })
        
        # الجغرافيا
        geographic = self.market_analysis.get('geographic', {})
        if geographic.get('has_geographic_data'):
            report_data.append({
                'category': 'التوزيع الجغرافي',
                'metric': 'عدد المدن',
                'value': geographic.get('total_cities', 0),
                'unit': 'مدينة'
            })
            report_data.append({
                'category': 'التوزيع الجغرافي',
                'metric': 'نسبة التركز',
                'value': geographic.get('concentration_ratio', 0),
                'unit': '%'
            })
        
        # النمو
        growth = self.market_analysis.get('growth', {})
        if growth.get('has_growth_data'):
            report_data.append({
                'category': 'النمو',
                'metric': 'معدل النمو الشهري',
                'value': growth.get('avg_monthly_growth', 0),
                'unit': '%'
            })
        
        # المنافسة
        competition = self.market_analysis.get('competition', {})
        report_data.append({
            'category': 'المنافسة',
            'metric': 'مستوى المنافسة',
            'value': competition.get('competition_level', 'غير محدد'),
            'unit': ''
        })
        
        return pd.DataFrame(report_data)
