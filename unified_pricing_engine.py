"""
محرك التسعير الموحد المتكامل
Unified Integrated Pricing Engine

نظام تسعير عالمي احترافي يدمج جميع مصادر البيانات والتحليلات في مكان واحد
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import streamlit as st

# استيراد جميع المحركات المتقدمة
try:
    from cma_pricing_model import CMAPricingModel
except:
    CMAPricingModel = None

try:
    from advanced_pricing_model import AdvancedPricingModel
except:
    AdvancedPricingModel = None

try:
    from enterprise_pricing_model import EnterprisePricingModel
except:
    EnterprisePricingModel = None

try:
    from predictive_pricing_ai import PredictivePricingAI
except:
    PredictivePricingAI = None

try:
    from market_analyzer import MarketDataAnalyzer
except:
    MarketDataAnalyzer = None

try:
    from data_extractor import DataExtractor
except:
    DataExtractor = None


class UnifiedPricingEngine:
    """
    محرك التسعير الموحد - نقطة واحدة لكل عمليات التسعير
    
    يدمج:
    - بيانات الطاقة والتكاليف
    - بيانات P&L التاريخية
    - بيانات الطلبات الفعلية
    - التحليلات التنبؤية
    - قواعد التسعير الذكية
    """
    
    def __init__(self, data_dir="data"):
        """تهيئة المحرك الموحد"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # مصادر البيانات الموحدة
        self.capacity_data = None
        self.pricing_tiers = None
        self.pnl_data = None
        self.orders_data = None
        self.quotes_history = None
        
        # بيانات إضافية متقدمة
        self.competitors_data = None      # بيانات المنافسين لـ CMA
        self.customers_data = None        # بيانات العملاء التفصيلية
        self.seasonality_data = None      # بيانات الموسمية
        self.sales_history = None         # بيانات المبيعات التاريخية
        self.market_data = None           # بيانات السوق العامة
        self.suppliers_data = None        # بيانات الموردين وشركات الشحن
        
        # التحليلات المحسوبة
        self.cost_analysis = {}
        self.profit_margins = {}
        self.service_stats = {}
        self.regional_analysis = {}
        self.customer_profitability = {}
        self.supplier_comparison = {}
        
        # المحركات المتقدمة المدمجة
        self.cma_model = CMAPricingModel() if CMAPricingModel else None
        self.advanced_model = AdvancedPricingModel() if AdvancedPricingModel else None
        self.enterprise_model = EnterprisePricingModel() if EnterprisePricingModel else None
        self.ai_model = PredictivePricingAI() if PredictivePricingAI else None
        
        # تحميل البيانات إن وجدت
        self.load_all_data()
    
    def load_all_data(self):
        """تحميل جميع مصادر البيانات المتاحة"""
        # تحميل بيانات الطاقة
        capacity_file = self.data_dir / "capacity_config.xlsx"
        if capacity_file.exists():
            self.capacity_data = pd.read_excel(capacity_file)
        
        # تحميل شرائح الأسعار
        pricing_file = self.data_dir / "pricing_tiers.xlsx"
        if pricing_file.exists():
            self.pricing_tiers = pd.read_excel(pricing_file)
        
        # تحميل سجل العروض
        quotes_file = self.data_dir / "quotes_history.xlsx"
        if quotes_file.exists():
            self.quotes_history = pd.read_excel(quotes_file)
    
    def integrate_capacity_data(self, capacity_df):
        """
        دمج بيانات الطاقة في النظام
        
        Parameters:
        -----------
        capacity_df : pd.DataFrame
            بيانات الطاقة الإنتاجية (service_name, capacity_per_month, monthly_cost)
        """
        self.capacity_data = capacity_df
        
        # حساب تكلفة الوحدة لكل خدمة
        if 'capacity_per_month' in capacity_df.columns and 'monthly_cost' in capacity_df.columns:
            capacity_df['cost_per_unit'] = capacity_df['monthly_cost'] / capacity_df['capacity_per_month'].replace(0, 1)
        
        return self
    
    def integrate_pnl_data(self, pnl_df):
        """
        دمج بيانات P&L في النظام
        
        Parameters:
        -----------
        pnl_df : pd.DataFrame
            بيانات الأرباح والخسائر
        """
        self.pnl_data = pnl_df
        
        # تحليل التكاليف من P&L
        self.cost_analysis = self._analyze_costs_from_pnl()
        
        # حساب هوامش الربح
        self.profit_margins = self._calculate_margins_from_pnl()
        
        # إحصائيات الخدمات
        self.service_stats = self._calculate_service_stats_from_pnl()
        
        # تحليل ربحية العملاء
        self.customer_profitability = self._analyze_customer_profitability()
        
        return self
    
    def integrate_orders_data(self, orders_df):
        """
        دمج بيانات الطلبات في النظام
        
        Parameters:
        -----------
        orders_df : pd.DataFrame
            بيانات الطلبات الفعلية
        """
        self.orders_data = orders_df
        
        # تحليل الشحن من الطلبات
        self.regional_analysis = self._analyze_regional_patterns()
        
        # تحليل وقت التجهيز
        self.prep_time_analysis = self._analyze_prep_time()
        
        # 🚀 استخراج تلقائي لكل البيانات من الطلبات
        if DataExtractor and orders_df is not None and not orders_df.empty:
            try:
                extractor = DataExtractor(orders_df, self.pnl_data)
                
                # استخراج بيانات المنافسين تلقائياً
                competitors = extractor.extract_competitors_data()
                if competitors is not None:
                    self.competitors_data = competitors
                
                # استخراج بيانات العملاء تلقائياً
                customers = extractor.extract_customers_data()
                if customers is not None:
                    self.customers_data = customers
                
                # استخراج بيانات المبيعات تلقائياً
                sales = extractor.extract_sales_history()
                if sales is not None:
                    self.sales_history = sales
                
                # استخراج بيانات الموسمية تلقائياً
                seasonality = extractor.extract_seasonality_data()
                if seasonality is not None:
                    self.seasonality_data = seasonality
            
            except Exception as e:
                pass  # فشل الاستخراج التلقائي - لا مشكلة
        
        # تحليل السوق التلقائي من بيانات الطلبات
        if MarketDataAnalyzer and orders_df is not None and not orders_df.empty:
            try:
                market_analyzer = MarketDataAnalyzer(orders_df)
                self.market_data = market_analyzer.analyze_market()
                self.market_analyzer = market_analyzer
            except Exception as e:
                self.market_data = None
                self.market_analyzer = None
        
        return self
    
    def integrate_competitors_data(self, competitors_df):
        """
        دمج بيانات المنافسين في النظام
        
        Parameters:
        -----------
        competitors_df : pd.DataFrame
            بيانات أسعار المنافسين (Columns: service_name, competitor_1, competitor_2, competitor_3)
        """
        self.competitors_data = competitors_df
        return self
    
    def integrate_customers_data(self, customers_df):
        """
        دمج بيانات العملاء التفصيلية
        
        Parameters:
        -----------
        customers_df : pd.DataFrame
            بيانات العملاء (Columns: customer_name, type, tier, monthly_volume, contract_type)
        """
        self.customers_data = customers_df
        
        # دمج مع تحليل الربحية الموجود
        if not self.customer_profitability:
            self.customer_profitability = {}
        
        for _, row in customers_df.iterrows():
            customer = row['customer_name']
            if customer not in self.customer_profitability:
                self.customer_profitability[customer] = {}
            
            self.customer_profitability[customer].update({
                'type': row.get('type', 'Standard'),
                'tier': row.get('tier', 'Standard'),
                'monthly_volume': row.get('monthly_volume', 0),
                'contract_type': row.get('contract_type', 'Monthly')
            })
        
        return self
    
    def integrate_seasonality_data(self, season_df):
        """
        دمج بيانات الموسمية
        
        Parameters:
        -----------
        season_df : pd.DataFrame
            بيانات الموسمية (Columns: month, season_type, demand_level, price_multiplier)
        """
        self.seasonality_data = season_df
        return self
    
    def integrate_sales_history(self, sales_df):
        """
        دمج بيانات المبيعات التاريخية
        
        Parameters:
        -----------
        sales_df : pd.DataFrame
            بيانات المبيعات (Columns: date, service, quantity, price, revenue)
        """
        self.sales_history = sales_df
        
        # تدريب نموذج AI إذا كان متوفراً
        if self.ai_model and len(sales_df) > 100:
            try:
                self.ai_model.train_on_historical_data(sales_df)
            except:
                pass
        
        return self
    
    def integrate_market_data(self, market_df):
        """
        دمج بيانات السوق العامة
        
        Parameters:
        -----------
        market_df : pd.DataFrame
            بيانات السوق (Columns: date, market_size, growth_rate, price_index)
        """
        self.market_data = market_df
        return self
    
    def integrate_suppliers_data(self, suppliers_df):
        """
        دمج بيانات الموردين وشركات الشحن
        
        Parameters:
        -----------
        suppliers_df : pd.DataFrame
            بيانات الموردين (Columns: supplier_name, service_type, city_range, base_price, etc.)
        """
        self.suppliers_data = suppliers_df
        
        # تحليل مقارنة الموردين
        self.supplier_comparison = self._analyze_suppliers()
        
        return self
    
    def _analyze_suppliers(self):
        """تحليل ومقارنة الموردين"""
        if self.suppliers_data is None or len(self.suppliers_data) == 0:
            return {}
        
        comparison = {}
        
        # مقارنة موردي الشحن
        shipping_suppliers = self.suppliers_data[
            self.suppliers_data['service_type'] == 'shipping'
        ]
        
        if len(shipping_suppliers) > 0:
            comparison['shipping'] = {
                'count': len(shipping_suppliers),
                'avg_price_inside_riyadh': shipping_suppliers['price_inside_riyadh'].mean(),
                'avg_price_outside_riyadh': shipping_suppliers['price_outside_riyadh'].mean(),
                'min_price_inside': shipping_suppliers['price_inside_riyadh'].min(),
                'min_price_outside': shipping_suppliers['price_outside_riyadh'].min(),
                'max_price_inside': shipping_suppliers['price_inside_riyadh'].max(),
                'max_price_outside': shipping_suppliers['price_outside_riyadh'].max(),
                'suppliers': shipping_suppliers['supplier_name'].tolist()
            }
        
        # مقارنة موردي التجهيز
        fulfillment_suppliers = self.suppliers_data[
            self.suppliers_data['service_type'] == 'fulfillment'
        ]
        
        if len(fulfillment_suppliers) > 0:
            comparison['fulfillment'] = {
                'count': len(fulfillment_suppliers),
                'avg_price': fulfillment_suppliers['base_price'].mean(),
                'outsourcing_available': len(fulfillment_suppliers[
                    fulfillment_suppliers['is_fulfillment_provider'] == 'yes'
                ]) > 0,
                'suppliers': fulfillment_suppliers['supplier_name'].tolist()
            }
        
        # مقارنة موردي التخزين
        storage_suppliers = self.suppliers_data[
            self.suppliers_data['service_type'] == 'storage'
        ]
        
        if len(storage_suppliers) > 0:
            comparison['storage'] = {
                'count': len(storage_suppliers),
                'avg_price': storage_suppliers['base_price'].mean(),
                'suppliers': storage_suppliers['supplier_name'].tolist()
            }
        
        return comparison
    
    def _analyze_costs_from_pnl(self):
        """استخراج التكاليف من P&L"""
        if self.pnl_data is None:
            return {}
        
        costs = {}
        try:
            # تكاليف التجهيز
            processing_costs = self.pnl_data[
                self.pnl_data['Account Level 2'].str.contains('تجهيز', na=False, case=False)
            ]['net_amount'].values
            costs['processing'] = abs(np.mean(processing_costs)) if len(processing_costs) > 0 else 50
            
            # تكاليف الشحن
            shipping_costs = self.pnl_data[
                self.pnl_data['Account Level 2'].str.contains('شحن', na=False, case=False)
            ]['net_amount'].values
            costs['shipping'] = abs(np.mean(shipping_costs)) if len(shipping_costs) > 0 else 30
            
            # تكاليف التخزين
            storage_costs = self.pnl_data[
                self.pnl_data['Account Level 2'].str.contains('تخزين', na=False, case=False)
            ]['net_amount'].values
            costs['storage'] = abs(np.mean(storage_costs)) if len(storage_costs) > 0 else 20
            
            # تكاليف الاستلام
            receiving_costs = self.pnl_data[
                self.pnl_data['Account Level 2'].str.contains('استلام', na=False, case=False)
            ]['net_amount'].values
            costs['receiving'] = abs(np.mean(receiving_costs)) if len(receiving_costs) > 0 else 15
            
        except Exception as e:
            st.warning(f"خطأ في تحليل التكاليف: {str(e)}")
        
        return costs
    
    def calculate_advanced_cost_allocation(self):
        """
        حساب توزيع التكاليف المتقدم بناءً على P&L والطاقة والطلبات
        يطبق نفس منطق الكود المطلوب:
        1. استخراج التكاليف من P&L
        2. توزيع G&A على الخدمات حسب السعة
        3. حساب التكلفة الشهرية النهائية
        
        Returns:
        --------
        pd.DataFrame
            جدول التكاليف النهائي لكل خدمة
        """
        if self.pnl_data is None or self.capacity_data is None:
            return None
        
        try:
            # =============================================
            # 1) تنظيف عمود المبالغ في P&L
            # =============================================
            pnl = self.pnl_data.copy()
            
            # البحث عن عمود المبلغ
            amount_col = None
            for col in pnl.columns:
                if any(x in col.lower() for x in ['amount', 'net', 'مبلغ', 'صافي']):
                    amount_col = col
                    break
            
            if amount_col:
                pnl["net_amount_clean"] = (
                    pnl[amount_col]
                    .astype(str)
                    .str.replace(",", "")
                    .str.replace(" ", "")
                    .str.replace("−", "-")
                    .astype(float, errors='ignore')
                )
            else:
                st.warning("⚠️ لم يتم العثور على عمود المبالغ في P&L")
                return None
            
            # =============================================
            # 2) استخراج التكاليف الشهرية الرئيسية
            # =============================================
            cost_fulfillment = abs(pnl[
                pnl["Account Level 2"].str.contains("تجهيز", na=False, case=False)
            ]["net_amount_clean"].sum())
            
            cost_shipping = abs(pnl[
                pnl["Account Level 2"].str.contains("شحن", na=False, case=False)
            ]["net_amount_clean"].sum())
            
            cost_storage = abs(pnl[
                pnl["Account Level 2"].str.contains("تخزين", na=False, case=False)
            ]["net_amount_clean"].sum())
            
            # عمومية وإدارية (G&A)
            cost_gna = abs(pnl[
                pnl["Account Level 2"].str.contains("عمومية|إدارية|اداريه", na=False, case=False)
            ]["net_amount_clean"].sum())
            
            # =============================================
            # 3) حساب عدد الطلبات الشهري
            # =============================================
            orders_count = len(self.orders_data) if self.orders_data is not None else 0
            
            # =============================================
            # 4) توزيع G&A على الخدمات بناءً على السعة
            # =============================================
            capacity = self.capacity_data.copy()
            
            # البحث عن عمود السعة
            capacity_col = None
            for col in capacity.columns:
                if any(x in col.lower() for x in ['capacity', 'سعة', 'طاقة']):
                    capacity_col = col
                    break
            
            if not capacity_col:
                st.warning("⚠️ لم يتم العثور على عمود السعة")
                return None
            
            total_capacity = capacity[capacity_col].sum()
            
            if total_capacity > 0:
                capacity["gna_alloc"] = (capacity[capacity_col] / total_capacity) * cost_gna
            else:
                capacity["gna_alloc"] = 0
            
            # =============================================
            # 5) بناء التكلفة الشهرية لكل خدمة
            # =============================================
            # مطابقة الخدمات مع التكاليف
            service_costs_map = {
                0: cost_fulfillment,   # تجهيز
                1: cost_shipping,      # شحن
                2: cost_storage,       # تخزين
                3: 0,                  # إدارة المخزون (يدوي)
                4: 0                   # القيمة المضافة (يدوي)
            }
            
            capacity["monthly_cost_before_gna"] = capacity.index.map(service_costs_map)
            capacity["monthly_cost_after_gna"] = capacity["monthly_cost_before_gna"] + capacity["gna_alloc"]
            
            # =============================================
            # 6) بناء الجدول النهائي
            # =============================================
            result = pd.DataFrame({
                "service_name": capacity.get("service_name", [
                    "تجهيز الطلبات",
                    "شحن",
                    "تخزين",
                    "إدارة المخزون",
                    "خدمات القيمة المضافة"
                ]),
                "capacity_per_month": capacity[capacity_col],
                "monthly_cost_before_gna": capacity["monthly_cost_before_gna"],
                "gna_allocation": capacity["gna_alloc"],
                "monthly_cost_after_gna": capacity["monthly_cost_after_gna"],
                "orders_per_month": orders_count,
                "cost_per_order": capacity["monthly_cost_after_gna"] / orders_count if orders_count > 0 else 0
            })
            
            # حفظ في session للاستخدام لاحقاً
            self.advanced_cost_allocation = result
            
            return result
            
        except Exception as e:
            st.error(f"❌ خطأ في حساب توزيع التكاليف: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def _calculate_margins_from_pnl(self):
        """حساب هوامش الربح من P&L"""
        if self.pnl_data is None:
            return {'historical_margin': 20.0, 'total_income': 0, 'total_expense': 0}
        
        try:
            total_income = abs(self.pnl_data[
                self.pnl_data['Account Level 1'].str.contains('income', na=False, case=False)
            ]['net_amount'].sum())
            
            total_expense = abs(self.pnl_data[
                self.pnl_data['Account Level 1'].str.contains('expense', na=False, case=False)
            ]['net_amount'].sum())
            
            margin = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 20.0
            
            return {
                'historical_margin': max(0, margin),
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': total_income - total_expense
            }
        except Exception as e:
            return {'historical_margin': 20.0, 'total_income': 0, 'total_expense': 0}
    
    def _calculate_service_stats_from_pnl(self):
        """إحصائيات الخدمات من P&L"""
        if self.pnl_data is None:
            return {}
        
        stats = {}
        services = {
            'processing': 'ايراد التجهيز',
            'shipping': 'ايراد الشحن',
            'storage': 'ايراد التخزين',
            'receiving': 'ايراد الاستلام'
        }
        
        for key, search_term in services.items():
            try:
                income = self.pnl_data[
                    self.pnl_data['Account Level 2'].str.contains(search_term, na=False, case=False)
                ]['net_amount'].values
                
                if len(income) > 0:
                    stats[key] = {
                        'avg': abs(np.mean(income)),
                        'max': abs(np.max(income)),
                        'min': abs(np.min(income)),
                        'count': len(income)
                    }
                else:
                    stats[key] = {'avg': 100, 'max': 200, 'min': 50, 'count': 0}
            except:
                stats[key] = {'avg': 100, 'max': 200, 'min': 50, 'count': 0}
        
        return stats
    
    def _analyze_customer_profitability(self):
        """تحليل ربحية العملاء من P&L"""
        if self.pnl_data is None or 'Customer' not in self.pnl_data.columns:
            return {}
        
        profitability = {}
        
        for customer in self.pnl_data['Customer'].unique():
            if pd.notna(customer) and customer != '':
                income = abs(self.pnl_data[
                    (self.pnl_data['Customer'] == customer) & 
                    (self.pnl_data['Account Level 1'].str.contains('income', na=False, case=False))
                ]['net_amount'].sum())
                
                expense = abs(self.pnl_data[
                    (self.pnl_data['Customer'] == customer) & 
                    (self.pnl_data['Account Level 1'].str.contains('expense', na=False, case=False))
                ]['net_amount'].sum())
                
                if income > 0:
                    margin = ((income - expense) / income) * 100
                    profitability[customer] = {
                        'income': income,
                        'expense': expense,
                        'profit': income - expense,
                        'margin': margin,
                        'tier': self._get_customer_tier(margin)
                    }
        
        return profitability
    
    def _get_customer_tier(self, margin):
        """تحديد شريحة العميل"""
        if margin > 30:
            return 'VIP'
        elif margin > 20:
            return 'Premium'
        elif margin > 10:
            return 'Good'
        elif margin > 0:
            return 'Standard'
        else:
            return 'Loss'
    
    def _analyze_regional_patterns(self):
        """تحليل الأنماط الإقليمية من الطلبات"""
        if self.orders_data is None or 'DESTINATION CITY' not in self.orders_data.columns:
            return {}
        
        regional = {}
        
        for city in self.orders_data['DESTINATION CITY'].unique():
            city_data = self.orders_data[self.orders_data['DESTINATION CITY'] == city]
            
            regional[city] = {
                'order_count': len(city_data),
                'avg_order_value': city_data['ORDER AMOUNT'].mean() if 'ORDER AMOUNT' in city_data.columns else 0,
                'avg_shipping_cost': city_data['SHIPPING COST'].mean() if 'SHIPPING COST' in city_data.columns else 0,
                'avg_weight': city_data['SHIPMENT WEIGHT'].mean() if 'SHIPMENT WEIGHT' in city_data.columns else 1.0
            }
        
        return regional
    
    def _analyze_prep_time(self):
        """
        تحليل وقت تجهيز الطلبات من البيانات
        
        Returns:
        --------
        dict
            إحصائيات وقت التجهيز
        """
        if self.orders_data is None or 'prep_time_minutes' not in self.orders_data.columns:
            return {
                'avg_prep_time': 0,
                'median_prep_time': 0,
                'min_prep_time': 0,
                'max_prep_time': 0,
                'total_orders_analyzed': 0
            }
        
        # إزالة القيم الفارغة
        valid_data = self.orders_data.dropna(subset=['prep_time_minutes'])
        
        if len(valid_data) == 0:
            return {
                'avg_prep_time': 0,
                'median_prep_time': 0,
                'min_prep_time': 0,
                'max_prep_time': 0,
                'total_orders_analyzed': 0
            }
        
        # حساب الإحصائيات
        prep_stats = {
            'avg_prep_time': valid_data['prep_time_minutes'].mean(),
            'median_prep_time': valid_data['prep_time_minutes'].median(),
            'min_prep_time': valid_data['prep_time_minutes'].min(),
            'max_prep_time': valid_data['prep_time_minutes'].max(),
            'std_prep_time': valid_data['prep_time_minutes'].std(),
            'total_orders_analyzed': len(valid_data)
        }
        
        # تحليل حسب العميل
        customer_col = None
        for col in self.orders_data.columns:
            if 'CUSTOMER' in col.upper() and 'PHONE' in col.upper():
                customer_col = col
                break
        
        if customer_col:
            prep_stats['by_customer'] = (
                valid_data.groupby(customer_col)['prep_time_minutes']
                .agg(['mean', 'count'])
                .reset_index()
                .sort_values('mean', ascending=False)
                .head(20)  # أعلى 20 عميل
            )
        
        # توزيع الأوقات
        prep_stats['distribution'] = {
            'very_fast_pct': (len(valid_data[valid_data['prep_time_minutes'] <= 30]) / len(valid_data) * 100),
            'fast_pct': (len(valid_data[(valid_data['prep_time_minutes'] > 30) & (valid_data['prep_time_minutes'] <= 60)]) / len(valid_data) * 100),
            'normal_pct': (len(valid_data[(valid_data['prep_time_minutes'] > 60) & (valid_data['prep_time_minutes'] <= 120)]) / len(valid_data) * 100),
            'slow_pct': (len(valid_data[(valid_data['prep_time_minutes'] > 120) & (valid_data['prep_time_minutes'] <= 240)]) / len(valid_data) * 100),
            'very_slow_pct': (len(valid_data[valid_data['prep_time_minutes'] > 240]) / len(valid_data) * 100)
        }
        
        return prep_stats
    
    def calculate_comprehensive_price(self, 
                                     service_type,
                                     quantity=1,
                                     customer=None,
                                     city=None,
                                     weight=None,
                                     order_value=0,
                                     payment_method='PREPAID',
                                     urgency='normal'):
        """
        حساب سعر شامل يدمج جميع مصادر البيانات
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        quantity : int
            الكمية
        customer : str
            العميل (اختياري)
        city : str
            المدينة (للشحن)
        weight : float
            الوزن
        order_value : float
            قيمة الطلب
        payment_method : str
            طريقة الدفع
        urgency : str
            مستوى الأهمية
        
        Returns:
        --------
        dict
            تفاصيل السعر الشامل
        """
        result = {
            'service_type': service_type,
            'quantity': quantity,
            'breakdown': {}
        }
        
        # 1. السعر الأساسي من الطاقة
        base_price = self._get_base_price_from_capacity(service_type, quantity)
        result['breakdown']['base_service'] = base_price
        
        # 2. تعديل حسب P&L
        pnl_adjustment = self._get_pnl_adjustment(service_type)
        result['breakdown']['pnl_adjustment'] = pnl_adjustment
        
        # 3. تعديل حسب العميل
        customer_discount = 0
        if customer and customer in self.customer_profitability:
            customer_discount = self._get_customer_discount(customer, base_price)
            result['breakdown']['customer_discount'] = customer_discount
            result['customer_tier'] = self.customer_profitability[customer]['tier']
        
        # 4. تكلفة الشحن (إن وجدت)
        shipping_cost = 0
        if city and weight:
            shipping_cost = self._calculate_shipping_cost(city, weight, order_value, payment_method)
            result['breakdown']['shipping'] = shipping_cost
        
        # 5. التكاليف الإضافية
        additional_costs = self._calculate_additional_costs(weight or 1.0, payment_method, order_value)
        result['breakdown']['additional'] = additional_costs
        
        # 6. تعديل حسب الأهمية
        urgency_multiplier = {'low': 0.9, 'normal': 1.0, 'high': 1.3, 'urgent': 1.5}[urgency]
        
        # الحساب النهائي
        subtotal = base_price + pnl_adjustment - customer_discount
        service_total = subtotal * urgency_multiplier
        
        grand_total = service_total + shipping_cost + additional_costs
        
        result['subtotal'] = round(subtotal, 2)
        result['service_total'] = round(service_total, 2)
        result['grand_total'] = round(grand_total, 2)
        result['urgency_multiplier'] = urgency_multiplier
        
        return result
    
    def _get_base_price_from_capacity(self, service_type, quantity):
        """الحصول على السعر الأساسي من بيانات الطاقة"""
        # خريطة الخدمات
        service_map = {
            'ايراد التجهيز': 'preparation_team',
            'ايراد الشحن': 'shipping_cost',
            'ايراد التخزين': 'storage_fee',
            'ايراد الاستلام': 'receiving_service'
        }
        
        # محاولة من pricing_tiers أولاً
        if self.pricing_tiers is not None and not self.pricing_tiers.empty:
            service_key = service_map.get(service_type, 'preparation_team')
            
            # البحث عن الخدمة المطلوبة
            service_prices = self.pricing_tiers[
                self.pricing_tiers['service_key'] == service_key
            ]
            
            if not service_prices.empty:
                # إيجاد الشريحة المناسبة بناءً على الكمية
                matching_tier = service_prices[
                    (service_prices['min_volume'] <= quantity) & 
                    (service_prices['max_volume'] >= quantity)
                ]
                if not matching_tier.empty:
                    return matching_tier.iloc[0]['unit_price'] * quantity
        
        # إذا لم تُوجد، استخدم service_stats من P&L
        pnl_service_map = {
            'ايراد التجهيز': 'processing',
            'ايراد الشحن': 'shipping',
            'ايراد التخزين': 'storage',
            'ايراد الاستلام': 'receiving'
        }
        
        service_stat_key = pnl_service_map.get(service_type, 'processing')
        if service_stat_key in self.service_stats:
            return self.service_stats[service_stat_key]['avg'] * quantity
        
        # سعر افتراضي
        return 100 * quantity
    
    def _get_pnl_adjustment(self, service_type):
        """تعديل حسب هامش الربح من P&L"""
        if not self.profit_margins:
            return 0
        
        target_margin = max(20, self.profit_margins.get('historical_margin', 20))
        # إضافة هامش الربح المستهدف
        return 0  # يتم حسابه في السعر الأساسي
    
    def _get_customer_discount(self, customer, base_price):
        """حساب خصم العميل"""
        if customer not in self.customer_profitability:
            return 0
        
        tier = self.customer_profitability[customer]['tier']
        discount_rates = {
            'VIP': 0.15,
            'Premium': 0.10,
            'Good': 0.05,
            'Standard': 0,
            'Loss': -0.20  # زيادة سعر
        }
        
        return base_price * discount_rates.get(tier, 0)
    
    def _calculate_shipping_cost(self, city, weight, order_value, payment_method):
        """حساب تكلفة الشحن من بيانات الطلبات أو الموردين"""
        
        # أولاً: محاولة الحصول على السعر من الموردين
        if self.suppliers_data is not None and len(self.suppliers_data) > 0:
            from supplier_data_processor import SupplierDataProcessor
            
            processor = SupplierDataProcessor(self.suppliers_data)
            is_cod = (payment_method == 'POSTPAID')
            
            best_supplier = processor.get_best_shipping_supplier(
                city, weight, order_value, is_cod
            )
            
            if best_supplier:
                # إضافة هامش ربح 25%
                return round(best_supplier['total_cost'] * 1.25, 2)
        
        # البديل: حساب من بيانات الطلبات
        if city in self.regional_analysis:
            avg_cost = self.regional_analysis[city]['avg_shipping_cost']
            avg_weight = self.regional_analysis[city]['avg_weight']
            
            weight_factor = max(0.5, min(2.0, weight / max(avg_weight, 0.5)))
            base_cost = avg_cost * weight_factor
        else:
            base_cost = 25  # افتراضي
        
        # تعديل حسب قيمة الطلب
        if order_value > 500:
            base_cost *= 0.8
        elif order_value > 200:
            base_cost *= 0.9
        
        # تعديل حسب طريقة الدفع
        if payment_method == 'PREPAID':
            base_cost *= 0.9
        
        # هامش ربح الشحن
        return round(base_cost * 1.25, 2)
    
    def _calculate_additional_costs(self, weight, payment_method, order_value):
        """حساب التكاليف الإضافية"""
        cod_fee = 16.52 if payment_method == 'POSTPAID' else 0
        packaging = max(5, weight * 2)
        handling = 3.0
        insurance = order_value * 0.01 if order_value > 1000 else 0
        
        return round(cod_fee + packaging + handling + insurance, 2)
    
    def generate_quote(self, customer_name, service_type, monthly_volume, requirements):
        """
        توليد عرض سعر ذكي
        
        Parameters:
        -----------
        customer_name : str
            اسم العميل
        service_type : str
            نوع الخدمة (fulfillment, shipping, storage, VAS)
        monthly_volume : int
            عدد الطلبات الشهرية
        requirements : dict
            متطلبات إضافية
            
        Returns:
        --------
        dict
            عرض السعر الكامل مع التفاصيل
        """
        try:
            # حساب السعر الأساسي حسب الحجم
            if monthly_volume <= 1000:
                base_price = 25.0
                tier = "Standard"
            elif monthly_volume <= 5000:
                base_price = 22.0
                tier = "Professional"
            elif monthly_volume <= 15000:
                base_price = 19.0
                tier = "Business"
            else:
                base_price = 16.0
                tier = "Enterprise"
            
            # حساب التكلفة الفعلية من P&L
            cost_per_order = 0
            if self.profit_margins and self.profit_margins.get('total_expense'):
                total_expense = abs(self.profit_margins.get('total_expense', 0))
                
                # استخدام عدد الطلبات الفعلي من البيانات التاريخية
                if self.orders_data is not None and len(self.orders_data) > 0:
                    # عدد الطلبات الفعلي في البيانات
                    historical_orders = len(self.orders_data)
                    cost_per_order = total_expense / historical_orders
                elif self.profit_margins.get('total_orders'):
                    # إذا كان محفوظ في profit_margins
                    cost_per_order = total_expense / self.profit_margins.get('total_orders')
                else:
                    # استخدام تقدير معقول (افتراض 10,000 طلب شهرياً)
                    cost_per_order = total_expense / 10000
            
            # إذا لم تتوفر بيانات P&L، استخدم تقدير معقول
            if cost_per_order == 0 or cost_per_order > 100:
                # تكلفة معقولة بناءً على السوق السعودي
                if monthly_volume <= 1000:
                    cost_per_order = 15.0  # Standard
                elif monthly_volume <= 5000:
                    cost_per_order = 12.0  # Professional
                elif monthly_volume <= 15000:
                    cost_per_order = 10.0  # Business
                else:
                    cost_per_order = 8.0   # Enterprise
            
            # حساب هامش الربح المستهدف
            target_margin = 0.25  # 25% هامش ربح
            if self.profit_margins.get('historical_margin'):
                target_margin = max(0.20, min(0.35, self.profit_margins['historical_margin'] / 100))
            
            # السعر النهائي
            final_price = cost_per_order / (1 - target_margin)
            
            # تفاصيل التكلفة
            cost_breakdown = {
                'cost_per_order': round(cost_per_order, 2),
                'shipping_cost': round(cost_per_order * 0.40, 2),
                'fulfillment_cost': round(cost_per_order * 0.35, 2),
                'packaging_cost': round(cost_per_order * 0.15, 2),
                'overhead_cost': round(cost_per_order * 0.10, 2),
                'target_margin': round(target_margin * 100, 1),
                'profit_per_order': round(final_price - cost_per_order, 2)
            }
            
            quote = {
                'customer_name': customer_name,
                'tier': tier,
                'service_type': service_type,
                'monthly_volume': monthly_volume,
                'price': round(final_price, 2),
                'cost_breakdown': cost_breakdown,
                'created_at': datetime.now().isoformat()
            }
            
            return quote
            
        except Exception as e:
            print(f"Error generating quote: {str(e)}")
            return None
    
    def save_quote(self, quote_data):
        """حفظ عرض سعر جديد"""
        quote_df = pd.DataFrame([{
            'quote_id': f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'date': datetime.now(),
            'service_type': quote_data['service_type'],
            'quantity': quote_data['quantity'],
            'customer': quote_data.get('customer', ''),
            'total_price': quote_data['grand_total'],
            **quote_data['breakdown']
        }])
        
        quotes_file = self.data_dir / "quotes_history.xlsx"
        if quotes_file.exists():
            existing = pd.read_excel(quotes_file)
            updated = pd.concat([existing, quote_df], ignore_index=True)
        else:
            updated = quote_df
        
        updated.to_excel(quotes_file, index=False)
        self.quotes_history = updated
        
        return quote_df.iloc[0]['quote_id']
    
    def get_analytics_dashboard(self):
        """الحصول على لوحة تحكم تحليلية شاملة"""
        dashboard = {
            'data_sources': {
                'capacity': self.capacity_data is not None,
                'pricing_tiers': self.pricing_tiers is not None,
                'pnl': self.pnl_data is not None,
                'orders': self.orders_data is not None,
                'quotes': self.quotes_history is not None
            },
            'metrics': {}
        }
        
        # مقاييس من P&L
        if self.profit_margins:
            dashboard['metrics']['profit'] = self.profit_margins
        
        # عدد العملاء
        dashboard['metrics']['customers'] = {
            'total': len(self.customer_profitability),
            'by_tier': {}
        }
        
        for customer, data in self.customer_profitability.items():
            tier = data['tier']
            dashboard['metrics']['customers']['by_tier'][tier] = \
                dashboard['metrics']['customers']['by_tier'].get(tier, 0) + 1
        
        # مقاييس المناطق
        if self.regional_analysis:
            dashboard['metrics']['regions'] = {
                'total_cities': len(self.regional_analysis),
                'top_city': max(self.regional_analysis.items(), 
                              key=lambda x: x[1]['order_count'])[0] if self.regional_analysis else None
            }
        
        return dashboard
    
    def calculate_cma_price(self, service_type, quantity, competitor_prices=None):
        """
        حساب السعر حسب نموذج CMA (دراسة السوق)
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        quantity : int
            الكمية
        competitor_prices : list
            أسعار المنافسين
        
        Returns:
        --------
        dict
            نتيجة التسعير حسب CMA
        """
        if not self.cma_model:
            return {'error': 'نموذج CMA غير متاح'}
        
        try:
            result = self.cma_model.calculate_market_based_price(
                service_type=service_type,
                quantity=quantity,
                competitor_prices=competitor_prices or [100, 120, 110]
            )
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_predictive_price(self, service_type, quantity, historical_data=None):
        """
        حساب السعر التنبؤي بالذكاء الاصطناعي
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        quantity : int
            الكمية
        historical_data : pd.DataFrame
            البيانات التاريخية
        
        Returns:
        --------
        dict
            نتيجة التسعير التنبؤي
        """
        if not self.ai_model:
            return {'error': 'نموذج الذكاء الاصطناعي غير متاح'}
        
        try:
            # استخدام بيانات P&L إن وجدت
            if historical_data is None and self.pnl_data is not None:
                historical_data = self.pnl_data
            
            result = self.ai_model.predict_optimal_price(
                service_type=service_type,
                quantity=quantity,
                historical_data=historical_data
            )
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_enterprise_price(self, service_type, quantity, customer_type='Standard'):
        """
        حساب السعر حسب نموذج المؤسسات
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        quantity : int
            الكمية
        customer_type : str
            نوع العميل
        
        Returns:
        --------
        dict
            نتيجة تسعير المؤسسات
        """
        if not self.enterprise_model:
            return {'error': 'نموذج المؤسسات غير متاح'}
        
        try:
            result = self.enterprise_model.calculate_enterprise_price(
                service_type=service_type,
                quantity=quantity,
                customer_tier=customer_type
            )
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_advanced_dynamic_price(self, service_type, quantity, 
                                        demand_level='normal', season='normal'):
        """
        حساب السعر الديناميكي المتقدم
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        quantity : int
            الكمية
        demand_level : str
            مستوى الطلب (low, normal, high, peak)
        season : str
            الموسم (low, normal, high, peak)
        
        Returns:
        --------
        dict
            نتيجة التسعير الديناميكي
        """
        if not self.advanced_model:
            return {'error': 'النموذج المتقدم غير متاح'}
        
        try:
            result = self.advanced_model.calculate_dynamic_price(
                service_type=service_type,
                quantity=quantity,
                demand_level=demand_level,
                season=season
            )
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def get_pricing_comparison(self, service_type, quantity, **kwargs):
        """
        مقارنة جميع نماذج التسعير
        
        Returns:
        --------
        dict
            مقارنة شاملة لجميع النماذج
        """
        comparison = {}
        
        # التسعير الأساسي
        comparison['basic'] = self.calculate_comprehensive_price(
            service_type=service_type,
            quantity=quantity,
            **kwargs
        )
        
        # نموذج CMA
        if self.cma_model:
            comparison['cma'] = self.calculate_cma_price(
                service_type=service_type,
                quantity=quantity
            )
        
        # التسعير التنبؤي
        if self.ai_model:
            comparison['predictive'] = self.calculate_predictive_price(
                service_type=service_type,
                quantity=quantity
            )
        
        # تسعير المؤسسات
        if self.enterprise_model:
            comparison['enterprise'] = self.calculate_enterprise_price(
                service_type=service_type,
                quantity=quantity
            )
        
        # التسعير الديناميكي
        if self.advanced_model:
            comparison['dynamic'] = self.calculate_advanced_dynamic_price(
                service_type=service_type,
                quantity=quantity
            )
        
        return comparison

