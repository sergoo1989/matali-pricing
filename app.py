import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import warnings
from cma_pricing_model import CMAPricingModel
from advanced_pricing_model import AdvancedPricingModel
from enterprise_pricing_model import EnterprisePricingModel, PricingRecommendationEngine, create_sample_sales_data
from predictive_pricing_ai import PredictivePricingAI
from comprehensive_pricing_system import (
    ComprehensivePricingEcosystem,
    QualityComplianceSystem,
    CrisisManagementSystem,
    AdaptiveLearningSystem,
    SupplierRelationshipManagement,
    SustainabilityPricingSystem,
    KnowledgeManagementSystem,
    PricingAutomationSystem
)
from smart_pricing_engine import SmartPricingEngine, AdvancedPricingEngine
from order_data_processor import OrderDataProcessor, PricingOptimizer, get_memory_usage, get_data_summary
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title="نظام متالي للتسعير الذكي",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .positive-metric {
        border-left: 4px solid #2ecc71;
    }
    .negative-metric {
        border-left: 4px solid #e74c3c;
    }
    .section-header {
        background: linear-gradient(90deg, #1f77b4, #4a90e2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
    }
    .profit-positive {
        color: #2ecc71;
        font-weight: bold;
    }
    .profit-negative {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class MataliPricingSystem:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.setup_file_paths()
        self.initialize_default_data()
    
    def setup_file_paths(self):
        """إعداد مسارات الملفات"""
        self.capacity_file = self.data_dir / "capacity_config.xlsx"
        self.pricing_file = self.data_dir / "pricing_tiers.xlsx"
        self.quotes_file = self.data_dir / "quotes_history.xlsx"
        self.services_file = self.data_dir / "service_master.xlsx"
        self.cost_alloc_file = self.data_dir / "cost_allocations.xlsx"
    
    def initialize_default_data(self):
        """تهيئة البيانات الافتراضية - فارغة"""
        # بيانات فارغة - يجب على المستخدم إدخال البيانات
        self.capacity_defaults = []
        self.pricing_defaults = []
        self.pricing_columns = [
            "service_key", "tier_name", "min_volume", "max_volume", "unit_price"
        ]

    def ensure_capacity_columns(self, df):
        """ضمان وجود الأعمدة الأساسية وحساب القيم المطلوبة"""
        required_cols = [
            "service_key", "service_group", "service_name", "unit_name",
            "capacity_type", "daily_capacity", "static_capacity", 
            "working_days", "monthly_cost", "monthly_capacity", "cost_per_unit"
        ]
        
        for col in required_cols:
            if col not in df.columns:
                if col in ["service_key", "service_group", "service_name", "unit_name", "capacity_type"]:
                    df[col] = ""
                else:
                    df[col] = 0.0
        
        # حساب الطاقة الشهرية
        def calc_monthly_capacity(row):
            if row['capacity_type'] == 'static':
                return row['static_capacity']
            else:
                return row['daily_capacity'] * row['working_days']
        
        df['monthly_capacity'] = df.apply(calc_monthly_capacity, axis=1)
        
        # حساب تكلفة الوحدة
        def calc_cost_per_unit(row):
            if row['monthly_capacity'] > 0:
                return row['monthly_cost'] / row['monthly_capacity']
            return 0.0
        
        df['cost_per_unit'] = df.apply(calc_cost_per_unit, axis=1)
        
        return df

    def ensure_pricing_columns(self, df):
        """ضمان أعمدة بيانات التسعير حتى في حالة غياب البيانات"""
        required_cols = {
            "service_key": "",
            "tier_name": "",
            "min_volume": 0.0,
            "max_volume": 0.0,
            "unit_price": 0.0
        }

        for col, default in required_cols.items():
            if col not in df.columns:
                df[col] = default
            else:
                if col in ["min_volume", "max_volume", "unit_price"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)
                else:
                    df[col] = df[col].fillna(default).astype(str)

        ordered_cols = list(required_cols.keys())
        extra_cols = [col for col in df.columns if col not in ordered_cols]
        return df[ordered_cols + extra_cols]

    def load_capacity_data(self):
        """تحميل بيانات الطاقة"""
        if self.capacity_file.exists():
            df = pd.read_excel(self.capacity_file)
        else:
            df = pd.DataFrame(self.capacity_defaults)
        
        return self.ensure_capacity_columns(df)

    def save_capacity_data(self, df):
        """حفظ بيانات الطاقة"""
        df = self.ensure_capacity_columns(df)
        df.to_excel(self.capacity_file, index=False)
        return df

    def load_pricing_data(self):
        """تحميل بيانات شرائح الأسعار"""
        if self.pricing_file.exists():
            df = pd.read_excel(self.pricing_file)
        else:
            df = pd.DataFrame(columns=getattr(self, "pricing_columns", []))
            df.to_excel(self.pricing_file, index=False)

        return self.ensure_pricing_columns(df)

    def save_pricing_data(self, df):
        """حفظ بيانات شرائح الأسعار"""
        df = self.ensure_pricing_columns(df)
        df.to_excel(self.pricing_file, index=False)
        return df

    def get_unit_price(self, service_key, volume, pricing_df):
        """الحصول على سعر الوحدة بناءً على الشريحة"""
        service_tiers = pricing_df[pricing_df['service_key'] == service_key]
        
        for _, tier in service_tiers.iterrows():
            min_vol = tier['min_volume']
            max_vol = tier['max_volume']
            
            if volume >= min_vol and (max_vol == 0 or volume <= max_vol):
                return tier['unit_price']
        
        return 0.0

    def calculate_service_pricing(self, service_data, volume, pricing_df):
        """حساب تسعير الخدمة الواحدة"""
        service_key = service_data['service_key']
        monthly_capacity = service_data['monthly_capacity']
        cost_per_unit = service_data['cost_per_unit']
        
        volume = float(volume) if volume else 0.0
        
        # حساب مؤشرات الطاقة
        if monthly_capacity > 0:
            utilization = (volume / monthly_capacity) * 100
            waste_units = max(monthly_capacity - volume, 0)
        else:
            utilization = 0.0
            waste_units = 0.0
        
        # الحصول على سعر الوحدة
        unit_price = self.get_unit_price(service_key, volume, pricing_df)
        
        # الحسابات المالية
        revenue = volume * unit_price
        cost_used = volume * cost_per_unit
        cost_waste = waste_units * cost_per_unit
        total_cost = cost_used + cost_waste
        
        margin_used = revenue - cost_used
        margin_total = revenue - total_cost
        
        margin_used_pct = (margin_used / revenue * 100) if revenue > 0 else 0
        margin_total_pct = (margin_total / revenue * 100) if revenue > 0 else 0
        
        return {
            'service_key': service_key,
            'service_name': service_data['service_name'],
            'unit_name': service_data['unit_name'],
            'volume': volume,
            'monthly_capacity': monthly_capacity,
            'utilization_pct': utilization,
            'waste_units': waste_units,
            'cost_per_unit': cost_per_unit,
            'unit_price': unit_price,
            'revenue': revenue,
            'cost_used': cost_used,
            'cost_waste': cost_waste,
            'total_cost': total_cost,
            'margin_used': margin_used,
            'margin_used_pct': margin_used_pct,
            'margin_total': margin_total,
            'margin_total_pct': margin_total_pct
        }

# إنشاء النظام
pricing_system = MataliPricingSystem()

def show_capacity_setup():
    """صفحة إعداد الطاقة الاستيعابية"""
    st.markdown('<div class="section-header"><h2>⚙️ إعداد الطاقة الاستيعابية</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هي الطاقة الاستيعابية؟ ولماذا مهمة؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        **الطاقة الاستيعابية** هي الحد الأقصى للخدمات التي يمكنك تقديمها في فترة زمنية معينة.
        
        ### 🎯 الأهمية:
        - تحديد تكلفة كل وحدة من الخدمة بدقة
        - معرفة نسبة الاستغلال والهدر
        - حساب الأسعار بناءً على التكاليف الفعلية
        - تخطيط أفضل للموارد
        
        ### 📋 أنواع الطاقة:
        
        **1. الطاقة اليومية (Daily):**
        - للخدمات التي تتكرر يومياً
        - مثال: استلام 44 طبلية يومياً
        - مثال: تجهيز 810 طلب يومياً
        
        **2. الطاقة الثابتة (Static):**
        - للخدمات التخزينية الثابتة
        - مثال: تخزين 468 طبلية شهرياً
        - مثال: 100 رف تخزين متاح
        
        ### ⚙️ كيف تحسب التكلفة:
        ```
        التكلفة لكل وحدة = التكلفة الشهرية ÷ الطاقة الشهرية
        ```
        
        **مثال:**
        - خدمة استلام: تكلفة شهرية 15,000 ر.س
        - طاقة يومية: 44 طبلية
        - أيام العمل: 26 يوم
        - الطاقة الشهرية = 44 × 26 = 1,144 طبلية
        - **تكلفة الطبلية الواحدة = 15,000 ÷ 1,144 = 13.11 ر.س**
        """)
    
    capacity_df = pricing_system.load_capacity_data()
    
    # رسالة تحذيرية إذا لم يكن هناك بيانات
    if capacity_df.empty:
        st.warning("""
        ⚠️ **لا توجد بيانات للطاقة الاستيعابية!**
        
        يرجى:
        1. استخدام تبويب "إضافة خدمة جديدة" لإضافة خدمات يدوياً
        2. أو تحميل قالب Excel من صفحة "📥 قوالب Excel" وتعبئته ثم رفعه
        """)
    
    tab1, tab2 = st.tabs(["📝 تعديل البيانات", "➕ إضافة خدمة جديدة"])
    
    with tab1:
        st.markdown("### تعديل بيانات الطاقة الحالية")
        
        if capacity_df.empty:
            st.info("📋 لا توجد بيانات حالياً. استخدم تبويب 'إضافة خدمة جديدة' أو ارفع ملف Excel")
        else:
            edited_df = st.data_editor(
                capacity_df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "service_key": st.column_config.TextColumn("مفتاح الخدمة", required=True),
                    "service_group": st.column_config.SelectboxColumn(
                        "المجموعة",
                        options=["Receiving", "Storage", "Fulfillment", "Shipping", "Value Added"],
                        required=True
                    ),
                    "service_name": st.column_config.TextColumn("اسم الخدمة", required=True),
                    "unit_name": st.column_config.TextColumn("وحدة القياس", required=True),
                    "capacity_type": st.column_config.SelectboxColumn(
                        "نوع الطاقة",
                        options=["daily", "static"],
                        required=True
                    ),
                    "daily_capacity": st.column_config.NumberColumn("الطاقة اليومية", min_value=0),
                    "static_capacity": st.column_config.NumberColumn("الطاقة الثابتة", min_value=0),
                    "working_days": st.column_config.NumberColumn("أيام العمل", min_value=1, max_value=31),
                    "monthly_cost": st.column_config.NumberColumn("التكلفة الشهرية", min_value=0, format="%.2f"),
                    "monthly_capacity": st.column_config.NumberColumn("الطاقة الشهرية", disabled=True),
                    "cost_per_unit": st.column_config.NumberColumn("تكلفة الوحدة", disabled=True, format="%.2f")
                },
                hide_index=True
            )
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("💾 حفظ التغييرات", type="primary", use_container_width=True):
                    pricing_system.save_capacity_data(edited_df)
                    st.success("✅ تم حفظ البيانات بنجاح!")
                    st.rerun()
    
    with tab2:
        st.markdown("### إضافة خدمة جديدة")
        
        with st.form("new_service_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_service_key = st.text_input("مفتاح الخدمة (بالإنجليزية)", placeholder="example_service")
                new_service_name = st.text_input("اسم الخدمة", placeholder="خدمة جديدة")
                new_service_group = st.selectbox(
                    "المجموعة",
                    ["Receiving", "Storage", "Fulfillment", "Shipping", "Value Added"]
                )
                new_unit_name = st.text_input("وحدة القياس", placeholder="وحدة")
            
            with col2:
                new_capacity_type = st.selectbox("نوع الطاقة", ["daily", "static"])
                new_daily_capacity = st.number_input("الطاقة اليومية", min_value=0.0, value=0.0)
                new_static_capacity = st.number_input("الطاقة الثابتة", min_value=0.0, value=0.0)
                new_working_days = st.number_input("أيام العمل الشهرية", min_value=1, max_value=31, value=26)
                new_monthly_cost = st.number_input("التكلفة الشهرية", min_value=0.0, value=0.0)
            
            submitted = st.form_submit_button("➕ إضافة الخدمة", type="primary", use_container_width=True)
            
            if submitted:
                new_service = {
                    "service_key": new_service_key,
                    "service_group": new_service_group,
                    "service_name": new_service_name,
                    "unit_name": new_unit_name,
                    "capacity_type": new_capacity_type,
                    "daily_capacity": new_daily_capacity,
                    "static_capacity": new_static_capacity,
                    "working_days": new_working_days,
                    "monthly_cost": new_monthly_cost,
                    "monthly_capacity": 0.0,
                    "cost_per_unit": 0.0
                }
                
                new_df = pd.concat([capacity_df, pd.DataFrame([new_service])], ignore_index=True)
                pricing_system.save_capacity_data(new_df)
                st.success(f"✅ تمت إضافة الخدمة '{new_service_name}' بنجاح!")
                st.rerun()

def show_pricing_tiers():
    """صفحة إعداد شرائح الأسعار"""
    st.markdown('<div class="section-header"><h2>💵 إعداد شرائح الأسعار</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هي شرائح الأسعار؟ ولماذا نستخدمها؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        **شرائح الأسعار** هي أسعار مختلفة لنفس الخدمة بناءً على الكمية المطلوبة.
        
        ### 🎯 الفائدة:
        - **للعميل**: خصومات على الكميات الكبيرة
        - **لك**: تشجيع العملاء على طلب كميات أكبر
        - **للجميع**: عدالة في التسعير حسب الحجم
        
        ### 📊 مثال عملي:
        
        **خدمة تجهيز الطلبات:**
        
        | الشريحة | من | إلى | السعر/طلب |
        |---------|-----|------|-----------|
        | شريحة 1 | 0 | 1,000 | 6.00 ر.س |
        | شريحة 2 | 1,001 | 5,000 | 5.00 ر.س ← خصم 17% |
        | شريحة 3 | 5,001 | 10,000 | 4.50 ر.س ← خصم 25% |
        | شريحة 4 | 10,001+ | لا حد | 4.20 ر.س ← خصم 30% |
        
        ### ✨ كيف يعمل:
        - عميل يطلب **500 طلب** شهرياً ← يدفع 6.00 ر.س للطلب
        - عميل يطلب **3,000 طلب** شهرياً ← يدفع 5.00 ر.س للطلب
        - عميل يطلب **15,000 طلب** شهرياً ← يدفع 4.20 ر.س للطلب
        
        ### 💡 نصيحة:
        استخدم صفحة **"🤖 التسعير الديناميكي"** لحساب الأسعار تلقائياً بناءً على:
        - تكلفة الخدمة
        - نسبة الاستغلال المتوقعة
        - هامش الربح المستهدف
        """)
    
    pricing_df = pricing_system.load_pricing_data()
    capacity_df = pricing_system.load_capacity_data()
    
    # رسالة تحذيرية إذا لم يكن هناك خدمات
    if capacity_df.empty:
        st.error("""
        ❌ **لا يمكن إضافة شرائح أسعار!**
        
        يجب أولاً إضافة الخدمات في صفحة "⚙️ إعداد الطاقة"
        """)
        return
    
    # رسالة تحذيرية إذا لم يكن هناك شرائح أسعار
    if pricing_df.empty:
        st.warning("""
        ⚠️ **لا توجد شرائح أسعار!**
        
        يرجى:
        1. استخدام تبويب "إضافة شريحة جديدة" لإضافة شرائح يدوياً
        2. أو استخدام صفحة "🤖 التسعير الديناميكي" لحساب الأسعار تلقائياً
        3. أو تحميل قالب Excel من صفحة "📥 قوالب Excel" وتعبئته ثم رفعه
        """)
    
    tab1, tab2 = st.tabs(["📝 تعديل الشرائح", "➕ إضافة شريحة جديدة"])
    
    with tab1:
        st.markdown("### تعديل شرائح الأسعار الحالية")
        
        if pricing_df.empty:
            st.info("📋 لا توجد شرائح أسعار حالياً. استخدم تبويب 'إضافة شريحة جديدة'")
        else:
            edited_pricing_df = st.data_editor(
                pricing_df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "service_key": st.column_config.SelectboxColumn(
                        "مفتاح الخدمة",
                        options=capacity_df['service_key'].tolist(),
                        required=True
                    ),
                    "tier_name": st.column_config.TextColumn("اسم الشريحة", required=True),
                    "min_volume": st.column_config.NumberColumn("الحد الأدنى", min_value=0, required=True),
                    "max_volume": st.column_config.NumberColumn("الحد الأقصى (0 = بدون حد)", min_value=0),
                    "unit_price": st.column_config.NumberColumn("سعر الوحدة", min_value=0.0, format="%.2f", required=True)
                },
                hide_index=True
            )
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("💾 حفظ التغييرات", type="primary", use_container_width=True):
                    pricing_system.save_pricing_data(edited_pricing_df)
                    st.success("✅ تم حفظ شرائح الأسعار بنجاح!")
                    st.rerun()
    
    with tab2:
        st.markdown("### إضافة شريحة سعر جديدة")
        
        with st.form("new_tier_form"):
            tier_service_key = st.selectbox(
                "اختر الخدمة",
                options=capacity_df['service_key'].tolist(),
                format_func=lambda x: capacity_df[capacity_df['service_key'] == x]['service_name'].iloc[0]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                tier_name = st.text_input("اسم الشريحة", placeholder="شريحة 1")
                min_volume = st.number_input("الحد الأدنى للكمية", min_value=0, value=0)
            
            with col2:
                max_volume = st.number_input("الحد الأقصى للكمية (0 = بدون حد)", min_value=0, value=0)
                unit_price = st.number_input("سعر الوحدة", min_value=0.0, value=0.0, format="%.2f")
            
            submitted = st.form_submit_button("➕ إضافة الشريحة", type="primary", use_container_width=True)
            
            if submitted:
                new_tier = {
                    "service_key": tier_service_key,
                    "tier_name": tier_name,
                    "min_volume": min_volume,
                    "max_volume": max_volume,
                    "unit_price": unit_price
                }
                
                new_pricing_df = pd.concat([pricing_df, pd.DataFrame([new_tier])], ignore_index=True)
                pricing_system.save_pricing_data(new_pricing_df)
                st.success(f"✅ تمت إضافة الشريحة '{tier_name}' بنجاح!")
                st.rerun()

def show_new_quote():
    """صفحة إنشاء عرض سعر جديد"""
    st.markdown('<div class="section-header"><h2>📋 إنشاء عرض سعر جديد</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 كيف تنشئ عرض سعر احترافي؟", expanded=False):
        st.markdown("""
        ### 💡 الغرض من هذه الصفحة:
        إنشاء عروض أسعار شاملة للعملاء مع حساب تلقائي للتكاليف والأرباح.
        
        ### 📝 خطوات إنشاء العرض:
        
        **1️⃣ معلومات العميل:**
        - أدخل اسم العميل/الشركة
        - حدد تاريخ العرض
        - حدد مدة صلاحية العرض (عادة 30 يوم)
        
        **2️⃣ اختيار الخدمات:**
        - افتح كل خدمة من القائمة
        - أدخل الكمية الشهرية المطلوبة
        - النظام يحسب السعر تلقائياً حسب الشرائح
        - يمكنك اختيار عدة خدمات
        
        **3️⃣ معلومات المشروع:**
        - أدخل اسم المشروع (اختياري)
        - حدد تاريخ البداية والنهاية
        - النظام يحسب عدد الأشهر وإجمالي العرض
        
        ### 💰 ما يحسبه النظام تلقائياً:
        
        **لكل خدمة:**
        - السعر المناسب حسب الكمية (من الشرائح)
        - إجمالي الإيراد = الكمية × السعر
        - التكلفة = الكمية × تكلفة الوحدة
        - الربح = الإيراد - التكلفة
        - هامش الربح %
        
        **للعرض الكامل:**
        - إجمالي الإيرادات الشهرية
        - إجمالي التكاليف الشهرية
        - صافي الربح الشهري
        - هامش الربح الإجمالي
        - **القيمة الكلية للعقد** (شهري × عدد الأشهر)
        
        ### ✅ بعد المراجعة:
        - احفظ العرض في النظام
        - يمكنك مراجعته لاحقاً من "📜 سجل العروض"
        - يمكنك تحليل ربحية العروض في "📊 الداشبورد"
        
        ### 💡 نصائح:
        - تأكد من إدخال الكميات الحقيقية المتوقعة
        - راجع هامش الربح للتأكد من مناسبته
        - يمكنك تعديل الأسعار في "💵 شرائح الأسعار" إذا لزم الأمر
        """)
    
    capacity_df = pricing_system.load_capacity_data()
    pricing_df = pricing_system.load_pricing_data()
    
    # معلومات العميل
    st.markdown("### 👤 معلومات العميل")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        customer_name = st.text_input("اسم العميل", placeholder="اسم الشركة")
    with col2:
        quote_date = st.date_input("تاريخ العرض", value=datetime.now())
    with col3:
        quote_validity = st.number_input("صلاحية العرض (أيام)", min_value=1, value=30)
    
    # اختيار الخدمات
    st.markdown("### 🛒 اختيار الخدمات والكميات")
    
    selected_services = []
    results = []
    
    for idx, service in capacity_df.iterrows():
        with st.expander(f"📦 {service['service_name']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**المجموعة:** {service['service_group']}")
                st.write(f"**الوحدة:** {service['unit_name']}")
                st.write(f"**الطاقة الشهرية:** {service['monthly_capacity']:,.0f}")
            
            with col2:
                st.write(f"**تكلفة الوحدة:** {service['cost_per_unit']:.2f} ر.س")
            
            with col3:
                volume = st.number_input(
                    f"الكمية ({service['unit_name']})",
                    min_value=0.0,
                    value=0.0,
                    key=f"vol_{service['service_key']}"
                )
            
            if volume > 0:
                result = pricing_system.calculate_service_pricing(service, volume, pricing_df)
                results.append(result)
                selected_services.append(service['service_name'])
    
    # عرض النتائج
    if results:
        st.markdown("### 📊 ملخص عرض السعر")
        
        results_df = pd.DataFrame(results)
        
        # المؤشرات الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        
        total_revenue = results_df['revenue'].sum()
        total_cost_used = results_df['cost_used'].sum()
        total_margin = results_df['margin_used'].sum()
        margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
        
        with col1:
            st.metric("إجمالي الإيراد", f"{total_revenue:,.2f} ر.س")
        with col2:
            st.metric("إجمالي التكلفة", f"{total_cost_used:,.2f} ر.س")
        with col3:
            st.metric("إجمالي الربح", f"{total_margin:,.2f} ر.س")
        with col4:
            st.metric("هامش الربح", f"{margin_pct:.1f}%")
        
        # جدول تفصيلي
        st.markdown("#### تفاصيل الخدمات")
        display_df = results_df[[
            'service_name', 'volume', 'unit_name', 'unit_price', 
            'revenue', 'cost_used', 'margin_used', 'margin_used_pct'
        ]].copy()
        
        display_df.columns = [
            'الخدمة', 'الكمية', 'الوحدة', 'سعر الوحدة',
            'الإيراد', 'التكلفة', 'الربح', 'هامش الربح %'
        ]
        
        st.dataframe(
            display_df.style.format({
                'الكمية': '{:,.0f}',
                'سعر الوحدة': '{:,.2f} ر.س',
                'الإيراد': '{:,.2f} ر.س',
                'التكلفة': '{:,.2f} ر.س',
                'الربح': '{:,.2f} ر.س',
                'هامش الربح %': '{:.2f}%'
            }),
            use_container_width=True
        )
        
        # حفظ العرض
        st.markdown("### 💾 حفظ عرض السعر")
        
        if st.button("💾 حفظ العرض", type="primary", use_container_width=True):
            quote_data = {
                'quote_date': quote_date,
                'customer_name': customer_name,
                'validity_days': quote_validity,
                'total_revenue': total_revenue,
                'total_cost': total_cost_used,
                'total_margin': total_margin,
                'margin_pct': margin_pct,
                'services_count': len(results),
                'services': ', '.join(selected_services)
            }
            
            # حفظ في ملف Excel
            if pricing_system.quotes_file.exists():
                quotes_df = pd.read_excel(pricing_system.quotes_file)
                quotes_df = pd.concat([quotes_df, pd.DataFrame([quote_data])], ignore_index=True)
            else:
                quotes_df = pd.DataFrame([quote_data])
            
            quotes_df.to_excel(pricing_system.quotes_file, index=False)
            st.success("✅ تم حفظ عرض السعر بنجاح!")

def show_quotes_history():
    """صفحة عرض سجل العروض"""
    st.markdown('<div class="section-header"><h2>📜 سجل عروض الأسعار</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما فائدة سجل العروض؟", expanded=False):
        st.markdown("""
        ### 💡 الغرض من هذه الصفحة:
        مراجعة جميع عروض الأسعار السابقة وتحليل أدائها.
        
        ### 📊 ما تعرضه الصفحة:
        
        **1️⃣ إحصائيات سريعة:**
        - عدد العروض الإجمالي
        - إجمالي الإيرادات المتوقعة
        - متوسط قيمة العرض
        - متوسط هامش الربح
        
        **2️⃣ جدول تفصيلي بكل العروض:**
        - اسم العميل والمشروع
        - تاريخ العرض ومدة الصلاحية
        - الإيرادات والتكاليف
        - صافي الربح وهامش الربح
        - حالة العرض (معلق/مقبول/مرفوض)
        
        ### 💰 كيف تستفيد منه:
        
        **تحليل الأداء:**
        - معرفة أي العملاء الأكثر ربحية
        - مقارنة هوامش الربح بين العروض
        - تتبع معدل قبول العروض
        
        **التخطيط:**
        - توقع الإيرادات المستقبلية
        - تحديد العملاء المحتملين
        - تحسين استراتيجية التسعير
        
        **المتابعة:**
        - مراجعة العروض المعلقة
        - تحديث حالة العروض
        - تحليل أسباب القبول/الرفض
        
        ### 🔍 الفلترة والبحث:
        يمكنك فلترة العروض حسب:
        - اسم العميل
        - تاريخ محدد
        - نطاق القيمة
        - حالة العرض
        
        ### 📈 استخدم مع الداشبورد:
        - اذهب إلى "📊 الداشبورد المتقدم"
        - ستجد تحليلات مفصلة عن العروض
        - رسوم بيانية توضح الاتجاهات
        """)
    
    if pricing_system.quotes_file.exists():
        quotes_df = pd.read_excel(pricing_system.quotes_file)
        
        if len(quotes_df) > 0:
            # إحصائيات سريعة
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("عدد العروض", len(quotes_df))
            with col2:
                st.metric("إجمالي الإيرادات", f"{quotes_df['total_revenue'].sum():,.0f} ر.س")
            with col3:
                st.metric("متوسط قيمة العرض", f"{quotes_df['total_revenue'].mean():,.0f} ر.س")
            with col4:
                st.metric("متوسط هامش الربح", f"{quotes_df['margin_pct'].mean():.1f}%")
            
            # عرض الجدول
            st.markdown("### جميع العروض")
            st.dataframe(
                quotes_df.style.format({
                    'total_revenue': '{:,.2f} ر.س',
                    'total_cost': '{:,.2f} ر.س',
                    'total_margin': '{:,.2f} ر.س',
                    'margin_pct': '{:.2f}%'
                }),
                use_container_width=True,
                height=400
            )
        else:
            st.info("📭 لا توجد عروض أسعار محفوظة حتى الآن")
    else:
        st.info("📭 لا توجد عروض أسعار محفوظة حتى الآن")

def show_excel_template():
    """صفحة قوالب Excel"""
    st.markdown('<div class="section-header"><h2>📥 قوالب Excel</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 لماذا نستخدم قوالب Excel؟", expanded=False):
        st.markdown("""
        ### 💡 الغرض من قوالب Excel:
        تسهيل إدخال البيانات بكميات كبيرة بدلاً من الإدخال اليدوي واحدة تلو الأخرى.
        
        ### 🎯 متى تستخدم قوالب Excel:
        
        **عند البداية:**
        - لديك الكثير من الخدمات للإدخال
        - تريد توفير الوقت
        - تفضل العمل على Excel
        
        **للتحديث:**
        - تريد تعديل عدة خدمات دفعة واحدة
        - تحتاج لمراجعة البيانات خارج البرنامج
        - تريد مشاركة البيانات مع الفريق
        
        ### 📥 تبويب "تحميل القوالب":
        
        **قالب الطاقة الاستيعابية:**
        - يحتوي على جميع الأعمدة المطلوبة
        - إذا كان لديك بيانات، سيتم تحميلها
        - إذا كنت تبدأ من الصفر، سيكون القالب فارغاً
        - الأعمدة المطلوبة:
          - `service_key`: مفتاح الخدمة (بالإنجليزية، بدون مسافات)
          - `service_group`: المجموعة (Receiving/Storage/Fulfillment/Shipping/Value Added)
          - `service_name`: اسم الخدمة (بأي لغة)
          - `unit_name`: وحدة القياس (طبلية، طلب، رف، إلخ)
          - `capacity_type`: نوع الطاقة (daily أو static)
          - `daily_capacity`: الطاقة اليومية
          - `static_capacity`: الطاقة الثابتة
          - `working_days`: أيام العمل الشهرية
          - `monthly_cost`: التكلفة الشهرية
        
        **قالب شرائح الأسعار:**
        - يحتوي على الشرائح الحالية
        - أو يكون فارغاً للبداية
        - الأعمدة المطلوبة:
          - `service_key`: مفتاح الخدمة (يجب أن يطابق المفاتيح في الطاقة)
          - `tier_name`: اسم الشريحة (شريحة 1، شريحة 2، إلخ)
          - `min_volume`: الحد الأدنى للكمية
          - `max_volume`: الحد الأقصى (0 = بدون حد أقصى)
          - `unit_price`: سعر الوحدة
        
        ### ⬆️ تبويب "رفع الملفات":
        
        **الخطوات:**
        1. حمّل القالب من تبويب "تحميل القوالب"
        2. افتحه في Excel أو Google Sheets
        3. أضف/عدّل البيانات
        4. احفظ الملف
        5. ارفعه هنا
        6. راجع المعاينة للتأكد من صحة البيانات
        7. اضغط "حفظ" لاستيراد البيانات
        
        ### ⚠️ ملاحظات مهمة:
        
        **عند التعبئة:**
        - ✅ لا تغير أسماء الأعمدة
        - ✅ لا تحذف الأعمدة
        - ✅ استخدم نفس التنسيق (daily/static للطاقة)
        - ✅ تأكد من `service_key` فريد لكل خدمة
        - ✅ في شرائح الأسعار، `service_key` يجب أن يطابق الخدمات الموجودة
        
        **الأخطاء الشائعة:**
        - ❌ تغيير أسماء الأعمدة
        - ❌ ترك خلايا فارغة في الأعمدة المطلوبة
        - ❌ استخدام `service_key` مختلف بين الطاقة والأسعار
        - ❌ كتابة نصوص في خانات الأرقام
        
        ### 💡 نصيحة:
        إذا كنت مبتدئاً، ابدأ بإضافة خدمة واحدة يدوياً من صفحة "⚙️ إعداد الطاقة"، ثم حمّل القالب لترى التنسيق الصحيح!
        """)
    
    tab1, tab2 = st.tabs(["⬇️ تحميل القوالب", "⬆️ رفع الملفات"])
    
    with tab1:
        st.markdown("""
        ### تحميل القوالب الجاهزة
        
        يمكنك تحميل القوالب التالية لإدارة بيانات النظام:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 قالب الطاقة الاستيعابية")
            st.write("قالب لإدخال وتحديث بيانات الطاقة الاستيعابية للخدمات")
            
            capacity_df = pricing_system.load_capacity_data()
            
            # إنشاء قالب فارغ إذا لم يكن هناك بيانات
            if capacity_df.empty:
                capacity_df = pd.DataFrame(columns=[
                    "service_key", "service_group", "service_name", "unit_name",
                    "capacity_type", "daily_capacity", "static_capacity", 
                    "working_days", "monthly_cost"
                ])
            
            # حفظ في buffer للتحميل المباشر
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                capacity_df.to_excel(writer, sheet_name='الطاقة الاستيعابية', index=False)
            buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل قالب الطاقة",
                data=buffer,
                file_name="capacity_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 💵 قالب شرائح الأسعار")
            st.write("قالب لإدخال وتحديث شرائح الأسعار للخدمات المختلفة")
            
            pricing_df = pricing_system.load_pricing_data()
            
            # إنشاء قالب فارغ إذا لم يكن هناك بيانات
            if pricing_df.empty:
                pricing_df = pd.DataFrame(columns=[
                    "service_key", "tier_name", "min_volume", "max_volume", "unit_price"
                ])
            
            # حفظ في buffer للتحميل المباشر
            buffer2 = BytesIO()
            with pd.ExcelWriter(buffer2, engine='openpyxl') as writer:
                pricing_df.to_excel(writer, sheet_name='شرائح الأسعار', index=False)
            buffer2.seek(0)
            
            st.download_button(
                label="📥 تحميل قالب الأسعار",
                data=buffer2,
                file_name="pricing_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab2:
        st.markdown("### ⬆️ رفع ملفات Excel")
        st.info("""
        📝 **تعليمات الرفع:**
        1. حمّل القالب المناسب من تبويب "تحميل القوالب"
        2. املأ البيانات في ملف Excel
        3. ارفع الملف هنا لاستيراد البيانات
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 رفع ملف الطاقة الاستيعابية")
            capacity_file = st.file_uploader(
                "اختر ملف Excel للطاقة",
                type=['xlsx', 'xls'],
                key="capacity_upload"
            )
            
            if capacity_file is not None:
                try:
                    uploaded_capacity_df = pd.read_excel(capacity_file)
                    st.success(f"✅ تم قراءة الملف بنجاح! ({len(uploaded_capacity_df)} صف)")
                    
                    st.markdown("##### معاينة البيانات:")
                    st.dataframe(uploaded_capacity_df.head(), use_container_width=True)
                    
                    if st.button("💾 حفظ بيانات الطاقة", type="primary", key="save_capacity"):
                        pricing_system.save_capacity_data(uploaded_capacity_df)
                        st.success("✅ تم حفظ بيانات الطاقة الاستيعابية بنجاح!")
                        st.balloons()
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
        
        with col2:
            st.markdown("#### 💵 رفع ملف شرائح الأسعار")
            pricing_file = st.file_uploader(
                "اختر ملف Excel للأسعار",
                type=['xlsx', 'xls'],
                key="pricing_upload"
            )
            
            if pricing_file is not None:
                try:
                    uploaded_pricing_df = pd.read_excel(pricing_file)
                    st.success(f"✅ تم قراءة الملف بنجاح! ({len(uploaded_pricing_df)} صف)")
                    
                    st.markdown("##### معاينة البيانات:")
                    st.dataframe(uploaded_pricing_df.head(), use_container_width=True)
                    
                    if st.button("💾 حفظ شرائح الأسعار", type="primary", key="save_pricing"):
                        pricing_system.save_pricing_data(uploaded_pricing_df)
                        st.success("✅ تم حفظ شرائح الأسعار بنجاح!")
                        st.balloons()
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ خطأ في قراءة الملف: {str(e)}")

def show_dynamic_pricing():
    """صفحة التسعير الديناميكي الذكي"""
    st.markdown('<div class="section-header"><h2>🤖 التسعير الديناميكي الذكي</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو التسعير الديناميكي؟ وكيف يعمل؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        **التسعير الديناميكي** هو حساب الأسعار تلقائياً بناءً على التكاليف الفعلية والأرباح المستهدفة.
        
        ### 🎯 لماذا هو مهم؟
        - **دقة عالية**: يحسب التكلفة الحقيقية شاملة الهدر
        - **توفير الوقت**: لا حاجة لحسابات يدوية
        - **ذكي**: يأخذ في الاعتبار الطاقة غير المستغلة
        - **مرن**: يمكنك تعديل المعايير وفقاً لظروفك
        
        ### 🔢 كيف يحسب السعر؟
        
        **الخطوة 1: حساب تكلفة الهدر**
        ```
        تكلفة الهدر = (التكلفة الأساسية × نسبة عدم الاستغلال) ÷ نسبة الاستغلال × نسبة الاسترداد
        ```
        
        **الخطوة 2: التكلفة الكلية**
        ```
        التكلفة الكلية = التكلفة الأساسية + تكلفة الهدر
        ```
        
        **الخطوة 3: السعر المقترح**
        ```
        السعر = التكلفة الكلية × (1 + هامش الربح)
        ```
        
        ### 📊 مثال عملي:
        
        **خدمة تجهيز الطلبات:**
        - التكلفة الأساسية: 2.14 ر.س/طلب
        - نسبة الاستغلال المتوقعة: 70%
        - نسبة استرداد تكلفة الهدر: 50%
        - هامش الربح المستهدف: 25%
        
        **الحسابات:**
        1. تكلفة الهدر = (2.14 × 30%) ÷ 70% × 50% = 0.46 ر.س
        2. التكلفة الكلية = 2.14 + 0.46 = 2.60 ر.س
        3. **السعر المقترح = 2.60 × 1.25 = 3.25 ر.س**
        
        ### ⚙️ المعايير القابلة للتعديل:
        
        **1. هامش الربح (10-100%):**
        - نسبة الربح المطلوب تحقيقها
        - مثال: 25% يعني ربح ربع السعر
        
        **2. نسبة الاستغلال (30-100%):**
        - كم نسبة الطاقة المتوقع استخدامها؟
        - 70% = ستستخدم 70% من طاقتك
        
        **3. استرداد تكلفة الهدر (0-100%):**
        - كم نسبة تكلفة الطاقة غير المستغلة تريد تحميلها على السعر؟
        - 50% = نصف تكلفة الهدر على السعر
        - 100% = كل تكلفة الهدر على السعر
        - 0% = تتحمل أنت تكلفة الهدر
        
        ### ✅ بعد الحساب:
        - يعرض النظام جدول مفصل بالأسعار المقترحة
        - يمكنك مراجعة الأسعار قبل الحفظ
        - عند الحفظ، ينشئ النظام 4 شرائح تلقائياً:
          - شريحة 1: السعر الكامل
          - شريحة 2: خصم 10%
          - شريحة 3: خصم 15%
          - شريحة 4: خصم 20%
        """)
    
    st.markdown("""
    ### 💡 كيف يعمل التسعير الديناميكي؟
    
    يتم حساب السعر تلقائياً بناءً على:
    - **التكلفة الفعلية** للخدمة
    - **نسبة الاستخدام المتوقعة** من الطاقة
    - **تكلفة الهدر** (الطاقة غير المستخدمة)
    - **هامش الربح المستهدف**
    """)
    
    capacity_df = pricing_system.load_capacity_data()
    
    # التحقق من وجود بيانات
    if capacity_df.empty:
        st.error("""
        ❌ **لا يمكن حساب الأسعار الديناميكية!**
        
        يجب أولاً إضافة بيانات الطاقة الاستيعابية في صفحة "⚙️ إعداد الطاقة"
        """)
        return
    
    # إعدادات التسعير
    st.markdown("### ⚙️ إعدادات التسعير")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        target_margin = st.slider(
            "هامش الربح المستهدف (%)",
            min_value=10,
            max_value=100,
            value=25,
            step=5,
            help="النسبة المئوية للربح المطلوب تحقيقه"
        )
    
    with col2:
        expected_utilization = st.slider(
            "نسبة الاستخدام المتوقعة (%)",
            min_value=30,
            max_value=100,
            value=70,
            step=5,
            help="النسبة المتوقعة من الطاقة التي سيتم استخدامها"
        )
    
    with col3:
        waste_recovery = st.slider(
            "نسبة استرداد تكلفة الهدر (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=10,
            help="نسبة تكلفة الهدر التي سيتم تحميلها على السعر"
        )
    
    st.markdown("---")
    
    # حساب الأسعار الديناميكية
    st.markdown("### 💰 الأسعار المحسوبة تلقائياً")
    
    pricing_results = []
    
    for idx, service in capacity_df.iterrows():
        # التكلفة الأساسية للوحدة
        base_cost = service['cost_per_unit']
        
        # حساب تكلفة الهدر للوحدة الواحدة
        waste_per_unit = (base_cost * (100 - expected_utilization) / expected_utilization) * (waste_recovery / 100)
        
        # التكلفة الكلية شاملة الهدر
        total_cost_per_unit = base_cost + waste_per_unit
        
        # السعر المقترح (التكلفة + هامش الربح)
        suggested_price = total_cost_per_unit * (1 + target_margin / 100)
        
        # حساب الربح
        profit_per_unit = suggested_price - total_cost_per_unit
        actual_margin = (profit_per_unit / suggested_price * 100) if suggested_price > 0 else 0
        
        # الإيراد والربح المتوقع شهرياً
        expected_volume = service['monthly_capacity'] * (expected_utilization / 100)
        expected_revenue = expected_volume * suggested_price
        expected_profit = expected_volume * profit_per_unit
        
        pricing_results.append({
            'service_name': service['service_name'],
            'service_group': service['service_group'],
            'unit_name': service['unit_name'],
            'monthly_capacity': service['monthly_capacity'],
            'expected_volume': expected_volume,
            'base_cost': base_cost,
            'waste_cost': waste_per_unit,
            'total_cost': total_cost_per_unit,
            'suggested_price': suggested_price,
            'profit_per_unit': profit_per_unit,
            'margin_pct': actual_margin,
            'expected_revenue': expected_revenue,
            'expected_profit': expected_profit
        })
    
    results_df = pd.DataFrame(pricing_results)
    
    # التحقق من وجود نتائج
    if results_df.empty:
        st.warning("⚠️ لا توجد نتائج لعرضها. تأكد من إدخال بيانات الطاقة والتكاليف")
        return
    
    # عرض المؤشرات الإجمالية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "إجمالي الإيراد المتوقع",
            f"{results_df['expected_revenue'].sum():,.0f} ر.س"
        )
    
    with col2:
        st.metric(
            "إجمالي الربح المتوقع",
            f"{results_df['expected_profit'].sum():,.0f} ر.س"
        )
    
    with col3:
        total_cost = capacity_df['monthly_cost'].sum()
        st.metric(
            "إجمالي التكاليف",
            f"{total_cost:,.0f} ر.س"
        )
    
    with col4:
        overall_margin = (results_df['expected_profit'].sum() / results_df['expected_revenue'].sum() * 100) if results_df['expected_revenue'].sum() > 0 else 0
        st.metric(
            "هامش الربح الفعلي",
            f"{overall_margin:.1f}%"
        )
    
    # جدول الأسعار التفصيلي
    st.markdown("#### 📋 جدول الأسعار المقترحة")
    
    display_df = results_df[[
        'service_name', 'unit_name', 'monthly_capacity', 'expected_volume',
        'base_cost', 'waste_cost', 'total_cost', 'suggested_price', 
        'profit_per_unit', 'margin_pct'
    ]].copy()
    
    display_df.columns = [
        'الخدمة', 'الوحدة', 'الطاقة الشهرية', 'الحجم المتوقع',
        'التكلفة الأساسية', 'تكلفة الهدر', 'التكلفة الكلية', 'السعر المقترح',
        'الربح/وحدة', 'هامش الربح %'
    ]
    
    st.dataframe(
        display_df.style.format({
            'الطاقة الشهرية': '{:,.0f}',
            'الحجم المتوقع': '{:,.0f}',
            'التكلفة الأساسية': '{:,.2f} ر.س',
            'تكلفة الهدر': '{:,.2f} ر.س',
            'التكلفة الكلية': '{:,.2f} ر.س',
            'السعر المقترح': '{:,.2f} ر.س',
            'الربح/وحدة': '{:,.2f} ر.س',
            'هامش الربح %': '{:.1f}%'
        }).background_gradient(subset=['السعر المقترح'], cmap='Greens'),
        use_container_width=True,
        height=500
    )
    
    # رسم بياني مقارن
    st.markdown("#### 📊 تحليل بصري للأسعار")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # مقارنة التكلفة vs السعر
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='التكلفة الكلية',
            x=results_df['service_name'],
            y=results_df['total_cost'],
            marker_color='lightcoral'
        ))
        
        fig.add_trace(go.Bar(
            name='السعر المقترح',
            x=results_df['service_name'],
            y=results_df['suggested_price'],
            marker_color='lightgreen'
        ))
        
        fig.update_layout(
            title='مقارنة التكلفة والسعر',
            xaxis_title='الخدمة',
            yaxis_title='ر.س',
            barmode='group',
            height=400
        )
        fig.update_xaxes(tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # توزيع هامش الربح
        fig = px.bar(
            results_df,
            x='service_name',
            y='margin_pct',
            color='service_group',
            title='هامش الربح لكل خدمة (%)',
            labels={'margin_pct': 'هامش الربح %', 'service_name': 'الخدمة'}
        )
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # حفظ الأسعار
    st.markdown("### 💾 حفظ الأسعار المحسوبة")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        ⚠️ **ملاحظة:** سيتم إنشاء شرائح تسعير تلقائية بناءً على الأحجام المختلفة:
        - شريحة 1: 0 - 1000 وحدة
        - شريحة 2: 1001 - 5000 وحدة (خصم 10%)
        - شريحة 3: 5001 - 10000 وحدة (خصم 15%)
        - شريحة 4: أكثر من 10000 وحدة (خصم 20%)
        """)
    
    with col2:
        if st.button("💾 حفظ كشرائح أسعار", type="primary", use_container_width=True):
            new_tiers = []
            
            for _, row in results_df.iterrows():
                service_key = capacity_df[capacity_df['service_name'] == row['service_name']]['service_key'].iloc[0]
                base_price = row['suggested_price']
                
                # إنشاء 4 شرائح
                new_tiers.extend([
                    {
                        'service_key': service_key,
                        'tier_name': 'شريحة 1',
                        'min_volume': 0,
                        'max_volume': 1000,
                        'unit_price': base_price
                    },
                    {
                        'service_key': service_key,
                        'tier_name': 'شريحة 2',
                        'min_volume': 1001,
                        'max_volume': 5000,
                        'unit_price': base_price * 0.9
                    },
                    {
                        'service_key': service_key,
                        'tier_name': 'شريحة 3',
                        'min_volume': 5001,
                        'max_volume': 10000,
                        'unit_price': base_price * 0.85
                    },
                    {
                        'service_key': service_key,
                        'tier_name': 'شريحة 4',
                        'min_volume': 10001,
                        'max_volume': 0,
                        'unit_price': base_price * 0.8
                    }
                ])
            
            new_pricing_df = pd.DataFrame(new_tiers)
            pricing_system.save_pricing_data(new_pricing_df)
            st.success("✅ تم حفظ الأسعار كشرائح تسعير بنجاح!")
            st.balloons()

def show_cma_pricing():
    """صفحة التسعير الإداري CMA"""
    st.markdown('<div class="section-header"><h2>📊 نموذج التسعير الإداري (CMA)</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو نموذج CMA للتسعير الإداري؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        **CMA (Certified Management Accountant) Pricing Model** هو نموذج تسعير شامل يستخدم في المحاسبة الإدارية لتحليل التكاليف والأرباح واتخاذ قرارات التسعير.
        
        ### 🎯 الفرق بينه وبين التسعير الديناميكي:
        
        | التسعير الديناميكي | نموذج CMA |
        |-------------------|-----------|
        | يركز على الطاقة الاستيعابية | يركز على التكاليف الثابتة والمتغيرة |
        | للخدمات اللوجستية | لأي منتج أو خدمة |
        | حساب سريع | تحليل شامل ومفصل |
        | يشمل تكلفة الهدر | يشمل تحليل نقطة التعادل |
        
        ### 📊 ما يقدمه نموذج CMA:
        
        **1. Cost-Plus Pricing (التسعير بإضافة هامش)**
        - حساب السعر بإضافة نسبة ربح للتكلفة
        - تجربة نسب ربح مختلفة (30%, 50%)
        
        **2. Target Pricing (التسعير المستهدف)**
        - تحديد السعر المستهدف في السوق
        - حساب التكلفة المطلوبة لتحقيق الربح المستهدف
        - معرفة الفجوة بين التكلفة الحالية والمستهدفة
        
        **3. Break-Even Analysis (تحليل نقطة التعادل)**
        - عدد الوحدات المطلوب بيعها لتغطية جميع التكاليف
        - هامش الأمان (كم وحدة فوق نقطة التعادل)
        - هامش المساهمة
        
        **4. Price Elasticity Analysis (تحليل مرونة الطلب)**
        - تأثير تغيير السعر على الكمية المباعة
        - تأثير ذلك على الإيرادات
        
        **5. Profitability Analysis (تحليل الربحية)**
        - مقارنة عدة سيناريوهات أسعار
        - إيجاد السعر الأمثل لأعلى ربح
        
        ### 🔢 المدخلات المطلوبة:
        
        **بيانات التكاليف:**
        - التكلفة المتغيرة للوحدة
        - إجمالي التكاليف الثابتة
        - الوحدات المتوقع بيعها
        - الطاقة الإنتاجية
        
        **بيانات السوق:**
        - سعر السوق الحالي
        - أسعار المنافسين
        - مرونة الطلب السعرية
        - هامش الربح المستهدف
        """)
    
    st.markdown("---")
    
    # إنشاء نموذج CMA
    if 'cma_model' not in st.session_state:
        st.session_state.cma_model = CMAPricingModel()
    
    cma = st.session_state.cma_model
    
    # إدخال البيانات
    st.markdown("### 📝 إدخال البيانات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 بيانات التكاليف")
        variable_cost = st.number_input(
            "التكلفة المتغيرة للوحدة (ر.س)",
            min_value=0.0,
            value=50.0,
            step=1.0,
            help="التكلفة التي تتغير مع كل وحدة (مواد خام، عمالة مباشرة، إلخ)"
        )
        
        fixed_cost = st.number_input(
            "إجمالي التكاليف الثابتة (ر.س/شهر)",
            min_value=0.0,
            value=100000.0,
            step=1000.0,
            help="التكاليف التي لا تتغير بتغير الإنتاج (إيجار، رواتب إدارية، إلخ)"
        )
        
        expected_units = st.number_input(
            "الوحدات المتوقع بيعها (شهرياً)",
            min_value=1,
            value=10000,
            step=100,
            help="عدد الوحدات التي تتوقع بيعها شهرياً"
        )
        
        capacity_units = st.number_input(
            "الطاقة الإنتاجية القصوى (شهرياً)",
            min_value=1,
            value=15000,
            step=100,
            help="أقصى عدد من الوحدات يمكنك إنتاجه/تقديمه شهرياً"
        )
    
    with col2:
        st.markdown("#### 📈 بيانات السوق")
        market_price = st.number_input(
            "سعر السوق الحالي (ر.س)",
            min_value=0.0,
            value=80.0,
            step=1.0,
            help="السعر السائد في السوق حالياً"
        )
        
        st.markdown("**أسعار المنافسين (ر.س):**")
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            comp1 = st.number_input("منافس 1", min_value=0.0, value=75.0, step=1.0)
            comp2 = st.number_input("منافس 2", min_value=0.0, value=85.0, step=1.0)
        with comp_col2:
            comp3 = st.number_input("منافس 3", min_value=0.0, value=82.0, step=1.0)
            comp4 = st.number_input("منافس 4", min_value=0.0, value=78.0, step=1.0)
        
        competitor_prices = [comp1, comp2, comp3, comp4]
        
        price_elasticity = st.slider(
            "مرونة الطلب السعرية",
            min_value=-5.0,
            max_value=0.0,
            value=-1.5,
            step=0.1,
            help="تأثير تغيير السعر على الكمية المباعة. -1.5 يعني: زيادة السعر 10% = انخفاض الكمية 15%"
        )
        
        target_profit_margin = st.slider(
            "هامش الربح المستهدف (%)",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help="النسبة المئوية للربح المستهدف من السعر"
        ) / 100
    
    # زر الحساب
    if st.button("🧮 احسب التوصيات", type="primary", use_container_width=True):
        # إدخال البيانات في النموذج
        cma.input_cost_data(variable_cost, fixed_cost, expected_units, capacity_units)
        cma.input_market_data(market_price, competitor_prices, price_elasticity, target_profit_margin)
        
        # توليد التوصيات
        results = cma.generate_pricing_recommendation()
        
        st.markdown("---")
        st.markdown("## 📊 نتائج التحليل")
        
        # ملخص التوصية
        summary = results['summary']
        st.success(f"""
        ### 🎯 التوصية النهائية
        
        **السعر الأمثل:** {summary['best_price']:.2f} ر.س  
        **الربح المتوقع:** {summary['best_profit']:,.2f} ر.س  
        **هامش الربح:** {summary['profit_margin']:.2f}%
        
        **📊 مؤشرات الأداء:**
        - نقطة التعادل: {summary['break_even_units']:.0f} وحدة
        - هامش الأمان: {summary['margin_of_safety']:.1f}%
        - هامش المساهمة: {summary['contribution_margin']:.1f}%
        """)
        
        # التوصيات التفصيلية
        st.markdown("### 📋 توصيات التسعير")
        
        tab1, tab2, tab3 = st.tabs(["التسعير على أساس التكلفة", "التسعير المستهدف", "تحليل الربحية"])
        
        with tab1:
            st.markdown("#### Cost-Plus Pricing")
            for rec in results['recommendations'][:2]:  # أول اثنين هم cost-plus
                if rec['method'] == 'Cost-Plus Pricing':
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("السعر المحسوب", f"{rec['calculated_price']:.2f} ر.س")
                    with col2:
                        st.metric("تكلفة الوحدة", f"{rec['cost_per_unit']:.2f} ر.س")
                    with col3:
                        st.metric("الربح/وحدة", f"{rec['profit_per_unit']:.2f} ر.س")
                    st.info(f"📊 نسبة الربح: {rec['markup_percentage']*100:.0f}%")
                    st.markdown("---")
        
        with tab2:
            st.markdown("#### Target Pricing Analysis")
            target = results['recommendations'][2]  # الثالث هو target pricing
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("سعر السوق", f"{target['market_price']:.2f} ر.س")
                st.metric("التكلفة المستهدفة", f"{target['target_cost']:.2f} ر.س")
            with col2:
                st.metric("التكلفة الحالية", f"{target['current_cost']:.2f} ر.س")
                st.metric("الفجوة", f"{target['cost_gap']:.2f} ر.س")
            
            if target['cost_gap'] > 0:
                st.warning(f"⚠️ يجب تخفيض التكلفة بنسبة {target['required_cost_reduction_percentage']:.1f}% لتحقيق الربح المستهدف")
            else:
                st.success("✅ التكلفة الحالية تحقق الربح المستهدف!")
        
        with tab3:
            st.markdown("#### تحليل الربحية عند أسعار مختلفة")
            
            # جدول المقارنة
            comparison_data = []
            for analysis in results['profitability_analysis']:
                if 'error' not in analysis['break_even_analysis']:
                    comparison_data.append({
                        'السعر': f"{analysis['selling_price']:.2f} ر.س",
                        'الإيراد': f"{analysis['total_revenue']:,.0f} ر.س",
                        'التكلفة': f"{analysis['total_cost']:,.0f} ر.س",
                        'الربح': f"{analysis['total_profit']:,.0f} ر.س",
                        'هامش الربح %': f"{analysis['profit_margin_percentage']:.1f}%",
                        'نقطة التعادل': f"{analysis['break_even_analysis']['break_even_units']:.0f} وحدة"
                    })
            
            if comparison_data:
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)
                
                # رسم بياني
                fig = go.Figure()
                for analysis in results['profitability_analysis']:
                    if 'error' not in analysis['break_even_analysis']:
                        fig.add_trace(go.Bar(
                            name=f"{analysis['selling_price']:.0f} ر.س",
                            x=['الإيراد', 'التكلفة', 'الربح'],
                            y=[analysis['total_revenue'], analysis['total_cost'], analysis['total_profit']]
                        ))
                
                fig.update_layout(
                    title="مقارنة السيناريوهات المختلفة",
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # تحليل المرونة
        if results['elasticity_analysis']:
            st.markdown("### 🔄 تحليل تأثير تغيير السعر (Price Elasticity)")
            
            elasticity_data = []
            for change, analysis in results['elasticity_analysis'].items():
                if 'error' not in analysis:
                    elasticity_data.append({
                        'تغيير السعر': change,
                        'السعر الجديد': f"{analysis['new_price']:.2f} ر.س",
                        'تغيير الكمية': f"{analysis['quantity_change_percentage']:.1f}%",
                        'الكمية الجديدة': f"{analysis['new_quantity']:.0f} وحدة",
                        'الإيراد الجديد': f"{analysis['new_revenue']:,.0f} ر.س",
                        'تغيير الإيراد': f"{analysis['revenue_change_percentage']:.1f}%"
                    })
            
            if elasticity_data:
                df_elasticity = pd.DataFrame(elasticity_data)
                st.dataframe(df_elasticity, use_container_width=True)
                
                st.info("""
                💡 **كيف تقرأ الجدول:**
                - تغيير السعر بـ -10% (تخفيض) يزيد الكمية المباعة
                - تغيير السعر بـ +10% (زيادة) يقلل الكمية المباعة
                - راقب تغيير الإيراد لمعرفة التأثير الكلي
                """)

def show_advanced_pricing():
    """صفحة نموذج التسعير المتقدم"""
    st.markdown('<div class="section-header"><h2>🎯 نموذج التسعير المتقدم</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو نموذج التسعير المتقدم؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        نموذج شامل يجمع **10+ استراتيجية تسعير** مختلفة في مكان واحد.
        
        ### 🎯 الاستراتيجيات المتاحة:
        
        **1️⃣ Lifecycle Pricing (تسعير دورة الحياة)**
        - تسعير حسب مرحلة المنتج (تقديم، نمو, نضج، انحدار)
        - كل مرحلة لها استراتيجية مختلفة
        
        **2️⃣ Psychological Pricing (التسعير النفسي)**
        - أسعار تنتهي بـ 9.99
        - تسعير متميز (أرقام كاملة)
        - تسعير جذاب
        
        **3️⃣ Discount Strategies (استراتيجيات الخصم)**
        - خصومات الكمية (10, 50, 100+ وحدة)
        - خصومات موسمية
        - خصومات التجارة
        
        **4️⃣ Scenario Analysis (تحليل السيناريوهات)**
        - إنشاء سيناريوهات متعددة
        - مقارنة بين الخيارات
        - تحليل الحساسية
        
        **5️⃣ Competitor Analysis (تحليل المنافسين)**
        - إضافة بيانات منافسين
        - مقارنة الأسعار والحصص السوقية
        
        ### 📊 الفرق عن النماذج الأخرى:
        
        | الميزة | تسعير ديناميكي | CMA | متقدم |
        |--------|----------------|-----|-------|
        | الاستراتيجيات | 1 | 5 | 10+ |
        | دورة الحياة | ❌ | ❌ | ✅ |
        | التسعير النفسي | ❌ | ❌ | ✅ |
        | السيناريوهات | ❌ | ✅ | ✅ |
        | المنافسين | ❌ | ❌ | ✅ |
        | الخصومات | ✅ | ❌ | ✅ |
        
        ### ⚙️ المدخلات المطلوبة:
        
        **التكاليف المفصلة:**
        - مواد مباشرة
        - عمالة مباشرة
        - تكاليف متغيرة إضافية
        - تكاليف ثابتة (إنتاج، بحث وتطوير، تسويق، إدارة)
        
        **بيانات السوق:**
        - السعر الحالي
        - مرونة الطلب
        - معدل نمو السوق
        - مرحلة دورة الحياة
        """)
    
    st.markdown("---")
    
    # إنشاء النموذج
    if 'adv_model' not in st.session_state:
        st.session_state.adv_model = None
    
    # اسم المنتج
    product_name = st.text_input("اسم المنتج/الخدمة", value="منتج جديد", key="adv_product_name")
    
    if st.session_state.adv_model is None or st.button("🔄 إعادة تعيين"):
        st.session_state.adv_model = AdvancedPricingModel(product_name)
        st.success("✅ تم إنشاء نموذج جديد")
    
    model = st.session_state.adv_model
    
    # تبويبات الإدخال
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 التكاليف المفصلة",
        "📈 بيانات السوق",
        "🏆 المنافسون",
        "🎭 السيناريوهات"
    ])
    
    with tab1:
        st.markdown("### إدخال التكاليف المفصلة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### التكاليف المباشرة (للوحدة)")
            direct_materials = st.number_input("مواد خام مباشرة (ر.س)", min_value=0.0, value=100.0, step=1.0)
            direct_labor = st.number_input("عمالة مباشرة (ر.س)", min_value=0.0, value=25.0, step=1.0)
            variable_overhead = st.number_input("تكاليف متغيرة إضافية (ر.س)", min_value=0.0, value=15.0, step=1.0)
        
        with col2:
            st.markdown("#### التكاليف الثابتة (شهرياً)")
            fixed_overhead = st.number_input("تكاليف إنتاج ثابتة (ر.س)", min_value=0.0, value=500000.0, step=1000.0)
            rnd_costs = st.number_input("بحث وتطوير (ر.س)", min_value=0.0, value=200000.0, step=1000.0)
            marketing_costs = st.number_input("تسويق (ر.س)", min_value=0.0, value=300000.0, step=1000.0)
            administrative_costs = st.number_input("إدارية (ر.س)", min_value=0.0, value=150000.0, step=1000.0)
        
        st.markdown("#### بيانات الإنتاج")
        col1, col2, col3 = st.columns(3)
        with col1:
            expected_units = st.number_input("الوحدات المتوقعة (شهرياً)", min_value=1, value=25000, step=100)
        with col2:
            capacity_units = st.number_input("الطاقة القصوى (شهرياً)", min_value=1, value=30000, step=100)
        with col3:
            production_cycle = st.number_input("دورة الإنتاج (أيام)", min_value=1, value=30, step=1)
        
        if st.button("💾 حفظ التكاليف", type="primary", key="save_costs"):
            cost_structure = {
                'direct_materials': direct_materials,
                'direct_labor': direct_labor,
                'variable_overhead': variable_overhead,
                'fixed_overhead': fixed_overhead,
                'rnd_costs': rnd_costs,
                'marketing_costs': marketing_costs,
                'administrative_costs': administrative_costs,
                'expected_units': expected_units,
                'capacity_units': capacity_units,
                'production_cycle_days': production_cycle
            }
            model.input_detailed_cost_data(cost_structure)
            st.success("✅ تم حفظ بيانات التكاليف!")
            
            # عرض ملخص
            st.info(f"""
            **ملخص التكاليف:**
            - التكلفة المتغيرة/وحدة: {model.cost_data['variable_cost_per_unit']:.2f} ر.س
            - التكلفة الثابتة/وحدة: {model.cost_data['fixed_cost_per_unit']:.2f} ر.س
            - **التكلفة الكلية/وحدة: {model.cost_data['total_cost_per_unit']:.2f} ر.س**
            """)
    
    with tab2:
        st.markdown("### بيانات السوق والتحليل")
        
        col1, col2 = st.columns(2)
        
        with col1:
            market_price = st.number_input("سعر السوق الحالي (ر.س)", min_value=0.0, value=450.0, step=1.0)
            price_elasticity = st.slider("مرونة الطلب السعرية", min_value=-5.0, max_value=0.0, value=-1.8, step=0.1)
            market_growth = st.slider("معدل نمو السوق (%)", min_value=0, max_value=50, value=8, step=1) / 100
        
        with col2:
            lifecycle_stage = st.selectbox(
                "مرحلة دورة حياة المنتج",
                ["introduction", "growth", "maturity", "decline"],
                format_func=lambda x: {
                    "introduction": "🌱 تقديم",
                    "growth": "📈 نمو",
                    "maturity": "⚖️ نضج",
                    "decline": "📉 انحدار"
                }[x]
            )
            market_share_target = st.slider("الحصة السوقية المستهدفة (%)", min_value=1, max_value=50, value=15, step=1) / 100
            seasonality = st.slider("عامل الموسمية", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
        
        if st.button("💾 حفظ بيانات السوق", type="primary", key="save_market"):
            market_analysis = {
                'current_market_price': market_price,
                'price_elasticity': price_elasticity,
                'market_growth_rate': market_growth,
                'market_share_target': market_share_target,
                'product_lifecycle_stage': lifecycle_stage,
                'seasonality_factor': seasonality
            }
            model.input_market_analysis(market_analysis)
            st.success("✅ تم حفظ بيانات السوق!")
    
    with tab3:
        st.markdown("### إضافة بيانات المنافسين")
        
        with st.form("competitor_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                comp_name = st.text_input("اسم المنافس", placeholder="منافس 1")
            with col2:
                comp_price = st.number_input("سعره (ر.س)", min_value=0.0, value=400.0, step=1.0)
            with col3:
                comp_share = st.slider("حصته السوقية (%)", min_value=0, max_value=100, value=20, step=1) / 100
            
            submitted = st.form_submit_button("➕ إضافة منافس", type="primary")
            if submitted and comp_name:
                model.add_competitor(comp_name, comp_price, comp_share)
                st.success(f"✅ تم إضافة {comp_name}")
        
        if model.competitor_data:
            st.markdown("#### المنافسون الحاليون")
            comp_df = pd.DataFrame(model.competitor_data)
            comp_df.columns = ['الاسم', 'السعر', 'الحصة السوقية', 'هيكل التكاليف']
            st.dataframe(comp_df[['الاسم', 'السعر', 'الحصة السوقية']], use_container_width=True)
    
    with tab4:
        st.markdown("### إنشاء سيناريوهات التسعير")
        
        with st.form("scenario_form"):
            scenario_name = st.text_input("اسم السيناريو", placeholder="سيناريو متحفظ")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                scenario_price = st.number_input("السعر (ر.س)", min_value=0.0, value=420.0, step=1.0)
            with col2:
                scenario_volume = st.number_input("الكمية المتوقعة", min_value=1, value=20000, step=100)
            with col3:
                scenario_condition = st.selectbox("ظروف السوق", ["stable", "competitive", "penetration", "premium"])
            
            submitted_scenario = st.form_submit_button("➕ إضافة سيناريو", type="primary")
            if submitted_scenario and scenario_name:
                scenario_result = model.create_pricing_scenario(scenario_name, {
                    'base_price': scenario_price,
                    'volume': scenario_volume,
                    'market_conditions': scenario_condition
                })
                st.success(f"✅ تم إضافة سيناريو: {scenario_name}")
        
        if model.scenarios:
            st.markdown("#### السيناريوهات الحالية")
            for name, data in model.scenarios.items():
                analysis = data['analysis']
                st.info(f"""
                **{name}**
                - السعر: {analysis['base_price']:.2f} ر.س
                - الربح: {analysis['profit']:,.0f} ر.س
                - هامش الربح: {analysis['profit_margin']:.1f}%
                - نقطة التعادل: {analysis['break_even_point']:.0f} وحدة
                """)
    
    # زر توليد التقرير
    st.markdown("---")
    if st.button("📊 توليد التقرير الشامل", type="primary", use_container_width=True):
        report = model.generate_comprehensive_report()
        
        if 'error' in report:
            st.error(report['error'])
        else:
            st.success("✅ تم توليد التقرير بنجاح!")
            
            # عرض النتائج
            st.markdown("## 📋 التقرير الشامل")
            
            # التكاليف
            st.markdown("### 💰 تحليل التكاليف")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("التكلفة المتغيرة/وحدة", f"{report['cost_analysis']['variable_cost_per_unit']:.2f} ر.س")
            with col2:
                st.metric("التكلفة الثابتة/وحدة", f"{report['cost_analysis']['fixed_cost_per_unit']:.2f} ر.س")
            with col3:
                st.metric("التكلفة الكلية/وحدة", f"{report['cost_analysis']['total_cost_per_unit']:.2f} ر.س")
            
            # تسعير دورة الحياة
            st.markdown("### 🔄 تسعير دورة الحياة")
            lifecycle = report['lifecycle_pricing']
            st.info(f"""
            **المرحلة:** {lifecycle['strategy']}
            
            **التركيز:** {lifecycle['focus']}
            
            **نطاق السعر المقترح:**
            - الحد الأدنى: {lifecycle['price_range']['min']:.2f} ر.س
            - الحد الأقصى: {lifecycle['price_range']['max']:.2f} ر.س
            
            **نطاق هامش الربح المقترح:** {lifecycle['recommended_markup_range']}
            """)
            
            # التسعير النفسي
            st.markdown("### 🎭 التسعير النفسي")
            psych_data = []
            for strategy, details in report['recommendations']['psychological_pricing'].items():
                psych_data.append({
                    'الاستراتيجية': details['description'],
                    'السعر المقترح': f"{details['price']:.2f} ر.س",
                    'القيمة المدركة': details['perceived_value']
                })
            st.dataframe(pd.DataFrame(psych_data), use_container_width=True)
            
            # الخصومات
            st.markdown("### 🎁 استراتيجيات الخصم")
            
            # خصومات الكمية
            st.markdown("#### خصومات الكمية")
            qty_discounts = report['recommendations']['discount_strategies'].get('quantity_discounts', {})
            if qty_discounts:
                qty_data = []
                for tier, details in qty_discounts.items():
                    qty_data.append({
                        'الشريحة': tier,
                        'الحد الأدنى': details['conditions']['min_quantity'],
                        'الخصم': f"{details['discount_percentage']:.0f}%",
                        'السعر بعد الخصم': f"{details['discounted_price']:.2f} ر.س"
                    })
                st.dataframe(pd.DataFrame(qty_data), use_container_width=True)
            
            # السيناريوهات
            if model.scenarios:
                st.markdown("### 🎯 مقارنة السيناريوهات")
                scenario_comparison = []
                for name, data in model.scenarios.items():
                    analysis = data['analysis']
                    scenario_comparison.append({
                        'السيناريو': name,
                        'السعر': f"{analysis['base_price']:.2f} ر.س",
                        'الحجم': analysis['expected_volume'],
                        'الإيراد': f"{analysis['revenue']:,.0f} ر.س",
                        'الربح': f"{analysis['profit']:,.0f} ر.س",
                        'هامش الربح': f"{analysis['profit_margin']:.1f}%"
                    })
                
                df_scenarios = pd.DataFrame(scenario_comparison)
                st.dataframe(df_scenarios, use_container_width=True)
                
                # رسم بياني
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='الإيراد',
                    x=[s['السيناريو'] for s in scenario_comparison],
                    y=[float(s['الإيراد'].replace(' ر.س', '').replace(',', '')) for s in scenario_comparison],
                    marker_color='lightblue'
                ))
                fig.add_trace(go.Bar(
                    name='الربح',
                    x=[s['السيناريو'] for s in scenario_comparison],
                    y=[float(s['الربح'].replace(' ر.س', '').replace(',', '')) for s in scenario_comparison],
                    marker_color='lightgreen'
                ))
                fig.update_layout(
                    title='مقارنة السيناريوهات',
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

def show_enterprise_pricing():
    """صفحة نموذج التسعير المؤسسي المتقدم"""
    st.markdown('<div class="section-header"><h2>🏢 نموذج التسعير المؤسسي</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو نموذج التسعير المؤسسي؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        نموذج تسعير **شامل للمؤسسات الكبيرة** يجمع جميع الاستراتيجيات المتقدمة في مكان واحد.
        
        ### 🎯 المميزات الرئيسية:
        
        **1️⃣ تحليل شرائح العملاء**
        - تقسيم العملاء إلى شرائح (Premium, Standard, Budget)
        - تسعير مختلف لكل شريحة
        - تحسين السعر حسب استعداد الدفع
        
        **2️⃣ الحملات الترويجية**
        - تقييم تأثير الخصومات
        - حساب ROI للحملات
        - تحليل الزيادة في الطلب
        
        **3️⃣ التوافق التنظيمي**
        - فحص القيود القانونية
        - التحقق من هوامش الربح المسموح بها
        - اقتراحات التعديل للتوافق
        
        **4️⃣ تقييم المخاطر**
        - مخاطر تنافسية
        - مخاطر الطلب
        - مخاطر تنظيمية
        - مخاطر سلسلة التوريد
        
        **5️⃣ محاكاة السيناريوهات الاقتصادية**
        - سيناريو الركود
        - سيناريو النمو
        - سيناريو التضخم
        
        **6️⃣ توصيات الذكاء الاصطناعي**
        - تحليل تلقائي متعدد الأبعاد
        - توصيات مخصصة
        - درجة ثقة لكل توصية
        
        ### 📊 متى تستخدم هذا النموذج؟
        - مؤسسات كبيرة بمنتجات متعددة
        - أسواق معقدة بمنافسة عالية
        - قيود تنظيمية صارمة
        - حاجة لتحليلات متقدمة
        """)
    
    st.markdown("---")
    
    # إنشاء النموذج
    if 'ent_model' not in st.session_state:
        st.session_state.ent_model = None
    
    # اسم المنتج
    product_name = st.text_input("اسم المنتج/الخدمة", value="منتج مؤسسي", key="ent_product_name")
    
    if st.session_state.ent_model is None or st.button("🔄 إعادة تعيين النموذج", key="reset_ent"):
        st.session_state.ent_model = EnterprisePricingModel(product_name)
        st.session_state.ent_segments = {}
        st.session_state.ent_campaigns = []
        st.success("✅ تم إنشاء نموذج جديد")
    
    model = st.session_state.ent_model
    
    # تبويبات رئيسية
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💰 البيانات الأساسية",
        "👥 شرائح العملاء",
        "📢 الحملات الترويجية",
        "⚖️ التوافق التنظيمي",
        "📊 تقييم المخاطر",
        "🤖 توصيات AI"
    ])
    
    with tab1:
        st.markdown("### إدخال البيانات الأساسية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💵 التكاليف")
            direct_materials = st.number_input("مواد خام (ر.س)", min_value=0.0, value=80.0, step=1.0, key="ent_mat")
            direct_labor = st.number_input("عمالة (ر.س)", min_value=0.0, value=20.0, step=1.0, key="ent_labor")
            variable_overhead = st.number_input("تكاليف متغيرة (ر.س)", min_value=0.0, value=15.0, step=1.0, key="ent_var")
            fixed_overhead = st.number_input("تكاليف ثابتة (ر.س)", min_value=0.0, value=300000.0, step=1000.0, key="ent_fixed")
        
        with col2:
            st.markdown("#### 📈 بيانات السوق")
            market_price = st.number_input("سعر السوق (ر.س)", min_value=0.0, value=180.0, step=1.0, key="ent_price")
            price_elasticity = st.slider("مرونة الطلب", min_value=-5.0, max_value=0.0, value=-2.0, step=0.1, key="ent_elast")
            market_growth = st.slider("نمو السوق (%)", min_value=0, max_value=50, value=6, step=1, key="ent_growth") / 100
            expected_units = st.number_input("الوحدات المتوقعة", min_value=1, value=20000, step=100, key="ent_units")
        
        if st.button("💾 حفظ البيانات الأساسية", type="primary", key="save_ent_basic"):
            cost_structure = {
                'direct_materials': direct_materials,
                'direct_labor': direct_labor,
                'variable_overhead': variable_overhead,
                'fixed_overhead': fixed_overhead,
                'rnd_costs': 150000,
                'marketing_costs': 200000,
                'administrative_costs': 100000,
                'expected_units': expected_units,
                'capacity_units': int(expected_units * 1.25),
                'production_cycle_days': 30
            }
            model.input_detailed_cost_data(cost_structure)
            
            market_analysis = {
                'current_market_price': market_price,
                'price_elasticity': price_elasticity,
                'market_growth_rate': market_growth,
                'market_share_target': 0.12,
                'product_lifecycle_stage': 'growth'
            }
            model.input_market_analysis(market_analysis)
            
            st.success("✅ تم حفظ البيانات!")
            st.info(f"**التكلفة الإجمالية/وحدة:** {model.cost_data.get('total_cost_per_unit', 0):.2f} ر.s")
    
    with tab2:
        st.markdown("### 👥 إدارة شرائح العملاء")
        
        st.info("""
        **شرائح العملاء** تساعدك على:
        - تحديد أسعار مختلفة لكل شريحة
        - زيادة الأرباح من العملاء المستعدين للدفع أكثر
        - جذب شرائح جديدة بأسعار منافسة
        """)
        
        # إضافة شريحة جديدة
        with st.form("segment_form"):
            st.markdown("#### إضافة شريحة جديدة")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                seg_name = st.text_input("اسم الشريحة", placeholder="Premium")
            with col2:
                seg_size = st.number_input("حجم الشريحة", min_value=1, value=1000, step=10)
            with col3:
                seg_wtp = st.slider("استعداد الدفع", min_value=0.5, max_value=2.0, value=1.5, step=0.1)
            with col4:
                seg_sensitivity = st.slider("حساسية السعر", min_value=0.1, max_value=2.0, value=0.8, step=0.1)
            
            submitted_seg = st.form_submit_button("➕ إضافة شريحة", type="primary")
            if submitted_seg and seg_name:
                if 'ent_segments' not in st.session_state:
                    st.session_state.ent_segments = {}
                
                st.session_state.ent_segments[seg_name] = {
                    'size': seg_size,
                    'willingness_to_pay_multiplier': seg_wtp,
                    'price_sensitivity': seg_sensitivity
                }
                model.define_customer_segments(st.session_state.ent_segments)
                st.success(f"✅ تم إضافة شريحة: {seg_name}")
                st.rerun()
        
        # عرض الشرائح الحالية
        if 'ent_segments' in st.session_state and st.session_state.ent_segments:
            st.markdown("#### الشرائح الحالية")
            segments_df = pd.DataFrame([
                {
                    'الشريحة': name,
                    'الحجم': data['size'],
                    'استعداد الدفع': f"{data['willingness_to_pay_multiplier']:.1f}x",
                    'حساسية السعر': f"{data['price_sensitivity']:.1f}"
                }
                for name, data in st.session_state.ent_segments.items()
            ])
            st.dataframe(segments_df, use_container_width=True)
            
            # حساب التسعير المتمايز
            if st.button("🎯 حساب الأسعار المثلى للشرائح", key="calc_seg"):
                segmented_pricing = model.calculate_segmented_pricing()
                
                if 'error' not in segmented_pricing:
                    st.markdown("#### 📊 الأسعار المقترحة")
                    for seg_name, seg_data in segmented_pricing.items():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"{seg_name} - السعر", f"{seg_data['optimal_price']:.2f} ر.س")
                        with col2:
                            st.metric("هامش الربح", f"{seg_data['target_margin']:.1f}%")
                        with col3:
                            st.metric("الحجم المتوقع", f"{seg_data['expected_volume']:,}")
                else:
                    st.error(segmented_pricing['error'])
    
    with tab3:
        st.markdown("### 📢 الحملات الترويجية")
        
        st.info("""
        **الحملات الترويجية** تساعدك على:
        - تقييم تأثير الخصومات على المبيعات
        - حساب عائد الاستثمار (ROI)
        - اتخاذ قرارات مبنية على البيانات
        """)
        
        with st.form("campaign_form"):
            st.markdown("#### إنشاء حملة جديدة")
            
            col1, col2 = st.columns(2)
            with col1:
                camp_name = st.text_input("اسم الحملة", placeholder="حملة رمضان")
                camp_discount = st.slider("نسبة الخصم (%)", min_value=0, max_value=50, value=15, step=1)
                camp_duration = st.number_input("مدة الحملة (أيام)", min_value=1, value=30, step=1)
            
            with col2:
                camp_reach = st.slider("نسبة الوصول (%)", min_value=1, max_value=100, value=10, step=1) / 100
                camp_cost = st.number_input("تكلفة الحملة (ر.س)", min_value=0.0, value=50000.0, step=1000.0)
            
            submitted_camp = st.form_submit_button("➕ إنشاء حملة", type="primary")
            if submitted_camp and camp_name:
                campaign = {
                    'name': camp_name,
                    'discount_percentage': camp_discount,
                    'duration_days': camp_duration,
                    'reach_percentage': camp_reach,
                    'additional_costs': camp_cost
                }
                model.add_promotional_campaign(campaign)
                
                # عرض تقييم الحملة
                impact = model.promotional_campaigns[-1]['impact_assessment']
                st.success(f"✅ تم إنشاء حملة: {camp_name}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("زيادة الطلب", f"{impact['expected_demand_increase']:.0f} وحدة")
                with col2:
                    st.metric("تأثير الإيراد", f"{impact['revenue_impact']:,.0f} ر.س")
                with col3:
                    roi_value = impact['campaign_roi']
                    roi_display = f"{roi_value:.1%}" if roi_value != float('inf') else "∞"
                    st.metric("ROI", roi_display)
        
        # عرض الحملات السابقة
        if model.promotional_campaigns:
            st.markdown("#### الحملات السابقة")
            for i, camp in enumerate(model.promotional_campaigns):
                with st.expander(f"📢 {camp.get('name', f'حملة {i+1}')}"):
                    impact = camp['impact_assessment']
                    st.write(f"**الخصم:** {camp['discount_percentage']}%")
                    st.write(f"**المدة:** {camp['duration_days']} يوم")
                    st.write(f"**زيادة الطلب:** {impact['expected_demand_increase']:.0f} وحدة")
                    st.write(f"**تأثير الإيراد:** {impact['revenue_impact']:,.0f} ر.س")
    
    with tab4:
        st.markdown("### ⚖️ التوافق التنظيمي")
        
        st.info("""
        **التوافق التنظيمي** يضمن:
        - الالتزام بالقوانين المحلية
        - عدم تجاوز هوامش الربح المسموح بها
        - تجنب التسعير الافتراسي
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            max_margin = st.slider("الحد الأقصى لهامش الربح (%)", min_value=10, max_value=100, value=40, step=5, key="max_margin")
            min_ratio = st.slider("الحد الأدنى (× التكلفة)", min_value=1.0, max_value=2.0, value=1.1, step=0.05, key="min_ratio")
        
        with col2:
            proposed_price_check = st.number_input("السعر المقترح للفحص (ر.س)", min_value=0.0, value=180.0, step=1.0, key="price_check")
        
        if st.button("🔍 فحص التوافق", type="primary", key="check_compliance"):
            constraints = {
                'max_profit_margin': max_margin,
                'min_price_ratio_to_cost': min_ratio
            }
            model.set_regulatory_constraints(constraints)
            
            compliance = model.check_regulatory_compliance(proposed_price_check)
            
            if compliance['is_compliant']:
                st.success("✅ السعر متوافق مع جميع القيود التنظيمية")
            else:
                st.error("❌ السعر غير متوافق!")
                
                st.markdown("**المخالفات:**")
                for violation in compliance['violations']:
                    st.warning(f"⚠️ {violation}")
                
                if compliance['required_adjustments']:
                    st.markdown("**التعديلات المقترحة:**")
                    for adjustment in compliance['required_adjustments']:
                        st.info(f"💡 {adjustment}")
    
    with tab5:
        st.markdown("### 📊 تقييم المخاطر الشامل")
        
        if st.button("🎲 تقييم المخاطر", type="primary", key="assess_risks"):
            risks = model.assess_market_risks()
            
            # عرض درجة المخاطر الإجمالية
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(
                    "درجة المخاطر الإجمالية",
                    f"{risks['overall_risk_score']:.1f}/10",
                    delta=None
                )
                
                risk_level = risks['risk_level']
                if risk_level == 'منخفض':
                    st.success(f"✅ مستوى المخاطرة: {risk_level}")
                elif risk_level == 'متوسط':
                    st.warning(f"⚠️ مستوى المخاطرة: {risk_level}")
                else:
                    st.error(f"❌ مستوى المخاطرة: {risk_level}")
            
            with col2:
                # رسم بياني للمخاطر
                risk_categories = ['تنافسية', 'الطلب', 'تنظيمية', 'سلسلة التوريد']
                risk_scores = [
                    risks['competitive_risks']['score'],
                    risks['demand_risks']['score'],
                    risks['regulatory_risks']['score'],
                    risks['supply_chain_risks']['score']
                ]
                
                fig = go.Figure(data=[
                    go.Bar(x=risk_categories, y=risk_scores, marker_color=['#ff6b6b', '#ffd93d', '#6bcf7f', '#4d96ff'])
                ])
                fig.update_layout(
                    title='تحليل المخاطر حسب الفئة',
                    yaxis_title='درجة المخاطر (0-10)',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # تفاصيل كل نوع مخاطر
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 المخاطر التنافسية")
                st.metric("الدرجة", f"{risks['competitive_risks']['score']:.1f}/10")
                for factor in risks['competitive_risks']['factors']:
                    st.write(f"• {factor}")
                
                st.markdown("#### ⚖️ المخاطر التنظيمية")
                st.metric("الدرجة", f"{risks['regulatory_risks']['score']:.1f}/10")
                for factor in risks['regulatory_risks']['factors']:
                    st.write(f"• {factor}")
            
            with col2:
                st.markdown("#### 📈 مخاطر الطلب")
                st.metric("الدرجة", f"{risks['demand_risks']['score']:.1f}/10")
                for factor in risks['demand_risks']['factors']:
                    st.write(f"• {factor}")
                
                st.markdown("#### 🚚 مخاطر سلسلة التوريد")
                st.metric("الدرجة", f"{risks['supply_chain_risks']['score']:.1f}/10")
                for factor in risks['supply_chain_risks']['factors']:
                    st.write(f"• {factor}")
        
        # محاكاة السيناريوهات
        st.markdown("---")
        st.markdown("### 🔄 محاكاة السيناريوهات الاقتصادية")
        
        if st.button("🎭 تشغيل محاكاة السيناريوهات", key="run_scenarios"):
            scenarios = {
                'الركود الاقتصادي': {'demand_shock': -0.3, 'growth_change': -0.04},
                'النمو القوي': {'demand_shock': 0.2, 'growth_change': 0.03},
                'التضخم المرتفع': {'demand_shock': -0.1, 'growth_change': -0.01}
            }
            
            scenario_results = model.simulate_economic_scenarios(scenarios)
            
            st.markdown("#### 📊 نتائج المحاكاة")
            
            scenario_data = []
            for scenario_name, results in scenario_results.items():
                scenario_data.append({
                    'السيناريو': scenario_name,
                    'السعر المقترح': f"{results['recommended_price']:.2f} ر.س",
                    'تغير الربح المتوقع': results['expected_profit_change'],
                    'مستوى المخاطرة': results['risk_level']
                })
            
            df_scenarios = pd.DataFrame(scenario_data)
            st.dataframe(df_scenarios, use_container_width=True)
    
    with tab6:
        st.markdown("### 🤖 توصيات الذكاء الاصطناعي")
        
        st.info("""
        **محرك التوصيات الذكي** يحلل:
        - كفاءة هيكل التكاليف
        - الموقف التنافسي في السوق
        - سلوك العملاء
        - ويقدم توصيات مخصصة بأولويات واضحة
        """)
        
        if st.button("✨ توليد التوصيات", type="primary", key="gen_ai_rec"):
            ai_results = model.generate_ai_pricing_recommendations()
            
            # درجة الثقة
            confidence = ai_results['confidence_score']
            st.metric(
                "درجة الثقة في التوصيات",
                f"{confidence:.1%}",
                delta=None
            )
            
            # التوصيات حسب الأولوية
            st.markdown("#### 🎯 التوصيات المرتبة حسب الأولوية")
            
            for i, rec in enumerate(ai_results['implementation_priority'], 1):
                priority_color = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec['priority'], '⚪')
                
                with st.expander(f"{priority_color} توصية {i}: {rec['action']}", expanded=(i == 1)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**النوع:** {rec['type']}")
                        st.write(f"**الأولوية:** {rec['priority']}")
                    with col2:
                        st.write(f"**التأثير المتوقع:** {rec['expected_impact']}")
            
            # تحليل العوامل
            st.markdown("---")
            st.markdown("#### 📊 تحليل العوامل")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**كفاءة التكاليف**")
                cost_factor = ai_results['factors_analysis']['cost_structure']
                st.metric("الدرجة", f"{cost_factor['score']:.1%}")
                st.write(f"التقييم: {cost_factor['rating']}")
                for suggestion in cost_factor['suggestions']:
                    st.info(f"💡 {suggestion}")
                
                st.markdown("**المشهد التنافسي**")
                comp_factor = ai_results['factors_analysis']['competitive_landscape']
                st.metric("الدرجة", f"{comp_factor['score']:.1%}")
                st.write(f"التقييم: {comp_factor['rating']}")
            
            with col2:
                st.markdown("**الموقف السوقي**")
                market_factor = ai_results['factors_analysis']['market_position']
                st.metric("الدرجة", f"{market_factor['score']:.1%}")
                st.write(f"التقييم: {market_factor['rating']}")
                
                st.markdown("**سلوك العملاء**")
                customer_factor = ai_results['factors_analysis']['customer_behavior']
                st.metric("الدرجة", f"{customer_factor['score']:.1%}")
                st.write(f"التقييم: {customer_factor['rating']}")

def show_predictive_ai():
    """صفحة التسعير التنبؤي بالذكاء الاصطناعي"""
    st.markdown('<div class="section-header"><h2>🤖 التسعير التنبؤي بالذكاء الاصطناعي</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو التسعير التنبؤي بالذكاء الاصطناعي؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        نموذج متقدم يستخدم **التعلم الآلي** و**التعلم العميق** للتنبؤ بالأسعار المثلى والطلب المستقبلي.
        
        ### 🎯 التقنيات المستخدمة:
        
        **1️⃣ Random Forest (الغابات العشوائية)**
        - التنبؤ بالسعر الأمثل
        - تحديد أهمية كل عامل
        - دقة عالية (>85%)
        
        **2️⃣ ARIMA (السلاسل الزمنية)**
        - التنبؤ بالطلب المستقبلي
        - اكتشاف الاتجاهات
        - التنبؤ لـ 30 يوم قادم
        
        **3️⃣ تحليل المرونة السعرية**
        - تعلم من البيانات التاريخية
        - فهم حساسية العملاء للسعر
        
        **4️⃣ اكتشاف الأنماط الموسمية**
        - تحديد الأشهر الذروة
        - التخطيط للحملات
        
        **5️⃣ التسعير الديناميكي**
        - توصيات فورية
        - بناءً على الحالة الراهنة
        
        ### 📊 متى تستخدم هذا النموذج؟
        - لديك بيانات تاريخية (50+ سجل)
        - تريد تنبؤات دقيقة
        - تحتاج قرارات آلية
        - سوق سريع التغير
        """)
    
    st.markdown("---")
    
    # إنشاء النموذج
    if 'ai_model' not in st.session_state:
        st.session_state.ai_model = PredictivePricingAI()
    
    ai_model = st.session_state.ai_model
    
    # تبويبات رئيسية
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 إعداد البيانات",
        "🤖 تدريب النموذج",
        "🎯 التنبؤ بالأسعار",
        "📈 التنبؤ بالطلب",
        "⚡ التسعير الديناميكي"
    ])
    
    with tab1:
        st.markdown("### 📊 إعداد بيانات التدريب")
        
        st.info("""
        **البيانات المطلوبة للتدريب:**
        - التكلفة (cost)
        - أسعار المنافسين (competitor_price)
        - الطلب (demand)
        - الموسمية (seasonality)
        - الترويج (promotion)
        - السعر الأمثل (optimal_price) - الهدف
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### خيار 1: توليد بيانات نموذجية")
            n_samples = st.number_input("عدد العينات", min_value=50, max_value=1000, value=200, step=50)
            
            if st.button("🔄 توليد بيانات تجريبية", type="primary"):
                sample_data = ai_model.generate_sample_data(n_samples)
                st.session_state.training_data = sample_data
                st.success(f"✅ تم توليد {len(sample_data)} عينة")
                st.dataframe(sample_data.head(10), use_container_width=True)
        
        with col2:
            st.markdown("#### خيار 2: رفع ملف Excel")
            uploaded_file = st.file_uploader("رفع ملف البيانات", type=['xlsx', 'csv'])
            
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.xlsx'):
                        data = pd.read_excel(uploaded_file)
                    else:
                        data = pd.read_csv(uploaded_file)
                    
                    st.session_state.training_data = data
                    st.success(f"✅ تم رفع {len(data)} سجل")
                    st.dataframe(data.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"خطأ في قراءة الملف: {str(e)}")
        
        # عرض إحصائيات البيانات
        if 'training_data' in st.session_state:
            st.markdown("---")
            st.markdown("#### 📈 إحصائيات البيانات")
            
            data = st.session_state.training_data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("عدد السجلات", len(data))
            with col2:
                st.metric("عدد الأعمدة", len(data.columns))
            with col3:
                if 'optimal_price' in data.columns:
                    st.metric("متوسط السعر", f"{data['optimal_price'].mean():.2f} ر.س")
            with col4:
                if 'demand' in data.columns:
                    st.metric("متوسط الطلب", f"{data['demand'].mean():.0f}")
    
    with tab2:
        st.markdown("### 🤖 تدريب نموذج التعلم الآلي")
        
        if 'training_data' not in st.session_state:
            st.warning("⚠️ يرجى إعداد البيانات في التبويب الأول")
        else:
            st.info("""
            **خطوات التدريب:**
            1. تقسيم البيانات (80% تدريب، 20% اختبار)
            2. تدريب نموذج Random Forest
            3. تقييم الدقة
            4. حساب أهمية المتغيرات
            """)
            
            if st.button("🚀 بدء التدريب", type="primary", use_container_width=True):
                with st.spinner("جاري التدريب... قد يستغرق بضع ثوانٍ"):
                    result = ai_model.integrate_machine_learning(st.session_state.training_data)
                    
                    if 'success' in result:
                        st.success("✅ تم التدريب بنجاح!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("الدقة", f"{result['accuracy']:.1%}")
                        with col2:
                            st.metric("متوسط الخطأ", f"{result['mae']:.2f} ر.س")
                        with col3:
                            st.metric("R² Score", f"{result['r2_score']:.3f}")
                        
                        # رسم أهمية المتغيرات
                        st.markdown("#### 📊 أهمية المتغيرات")
                        
                        importance_df = pd.DataFrame({
                            'المتغير': list(result['feature_importance'].keys()),
                            'الأهمية': list(result['feature_importance'].values())
                        }).sort_values('الأهمية', ascending=False)
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                x=importance_df['الأهمية'],
                                y=importance_df['المتغير'],
                                orientation='h',
                                marker_color='lightblue'
                            )
                        ])
                        fig.update_layout(
                            title='أهمية كل متغير في التنبؤ بالسعر',
                            xaxis_title='الأهمية',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.session_state.model_trained = True
                    else:
                        st.error(f"❌ {result.get('error', 'فشل التدريب')}")
    
    with tab3:
        st.markdown("### 🎯 التنبؤ بالسعر الأمثل")
        
        if not st.session_state.get('model_trained', False):
            st.warning("⚠️ يرجى تدريب النموذج أولاً")
        else:
            st.info("أدخل الظروف الحالية للحصول على السعر الأمثل المتنبأ به")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cost = st.number_input("التكلفة (ر.س)", min_value=0.0, value=100.0, step=1.0)
                competitor_price = st.number_input("سعر المنافسين (ر.س)", min_value=0.0, value=180.0, step=1.0)
                demand = st.number_input("الطلب المتوقع", min_value=0, value=1500, step=10)
            
            with col2:
                seasonality = st.slider("عامل الموسمية", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
                promotion = st.selectbox("حملة ترويجية؟", [0, 1], format_func=lambda x: "نعم" if x == 1 else "لا")
            
            if st.button("🔮 التنبؤ بالسعر", type="primary", use_container_width=True):
                conditions = {
                    'cost': cost,
                    'competitor_price': competitor_price,
                    'demand': demand,
                    'seasonality': seasonality,
                    'promotion': promotion
                }
                
                prediction = ai_model.predict_optimal_price(conditions)
                
                if 'predicted_price' in prediction:
                    st.markdown("---")
                    st.markdown("### 📊 النتيجة")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("السعر المتنبأ به", f"{prediction['predicted_price']:.2f} ر.س")
                    with col2:
                        margin = ((prediction['predicted_price'] - cost) / prediction['predicted_price'] * 100)
                        st.metric("هامش الربح", f"{margin:.1f}%")
                    with col3:
                        st.metric("الانحراف المعياري", f"±{prediction['std_deviation']:.2f}")
                    
                    st.info(f"""
                    **نطاق الثقة 95%:**  
                    {prediction['confidence_range']} ر.س
                    
                    هذا يعني أن السعر الفعلي سيكون ضمن هذا النطاق بنسبة 95%.
                    """)
                else:
                    st.error(prediction.get('error', 'فشل التنبؤ'))
    
    with tab4:
        st.markdown("### 📈 التنبؤ بالطلب المستقبلي")
        
        st.info("""
        **نموذج ARIMA** للسلاسل الزمنية:
        - يحلل البيانات التاريخية
        - يكتشف الاتجاهات والأنماط
        - يتنبأ بالطلب للأيام القادمة
        """)
        
        if 'training_data' in st.session_state and 'demand' in st.session_state.training_data.columns:
            forecast_days = st.slider("عدد الأيام للتنبؤ", min_value=7, max_value=90, value=30, step=7)
            
            if st.button("📊 التنبؤ بالطلب", type="primary", use_container_width=True):
                with st.spinner("جاري التحليل والتنبؤ..."):
                    demand_data = st.session_state.training_data['demand']
                    forecast_result = ai_model.demand_forecasting(demand_data, steps=forecast_days)
                    
                    if 'success' in forecast_result:
                        st.success("✅ تم التنبؤ بنجاح!")
                        
                        # عرض المعلومات
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("AIC", f"{forecast_result['model_summary']['aic']:.0f}")
                        with col2:
                            st.metric("BIC", f"{forecast_result['model_summary']['bic']:.0f}")
                        with col3:
                            st.metric("النموذج", f"ARIMA{forecast_result['model_summary']['order']}")
                        
                        # رسم التنبؤات
                        forecast_df = pd.DataFrame({
                            'اليوم': range(1, forecast_days + 1),
                            'التنبؤ': forecast_result['forecast'],
                            'الحد الأدنى': forecast_result['confidence_intervals']['lower'],
                            'الحد الأقصى': forecast_result['confidence_intervals']['upper']
                        })
                        
                        fig = go.Figure()
                        
                        # خط التنبؤ
                        fig.add_trace(go.Scatter(
                            x=forecast_df['اليوم'],
                            y=forecast_df['التنبؤ'],
                            mode='lines+markers',
                            name='التنبؤ',
                            line=dict(color='blue', width=2)
                        ))
                        
                        # نطاق الثقة
                        fig.add_trace(go.Scatter(
                            x=forecast_df['اليوم'].tolist() + forecast_df['اليوم'].tolist()[::-1],
                            y=forecast_df['الحد الأعلى'].tolist() + forecast_df['الحد الأدنى'].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(0,100,250,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='نطاق الثقة 95%'
                        ))
                        
                        fig.update_layout(
                            title='التنبؤ بالطلب للأيام القادمة',
                            xaxis_title='اليوم',
                            yaxis_title='الطلب المتوقع',
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # جدول التنبؤات
                        st.markdown("#### 📋 جدول التنبؤات")
                        st.dataframe(forecast_df, use_container_width=True)
                    else:
                        st.error(forecast_result.get('error', 'فشل التنبؤ'))
        else:
            st.warning("⚠️ يرجى إعداد البيانات أولاً")
    
    with tab5:
        st.markdown("### ⚡ استراتيجيات التسعير الديناميكي")
        
        st.info("""
        **التسعير الديناميكي** يقترح تعديلات فورية للسعر بناءً على:
        - مستوى الطلب
        - أسعار المنافسين
        - الموسمية
        - الطاقة الاستيعابية
        """)
        
        st.markdown("#### 📊 الحالة الحالية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_demand = st.number_input("الطلب الحالي", min_value=0, value=1200, step=10, key="dyn_demand")
            capacity = st.number_input("الطاقة القصوى", min_value=1, value=1500, step=10, key="dyn_capacity")
            current_price = st.number_input("السعر الحالي (ر.س)", min_value=0.0, value=180.0, step=1.0, key="dyn_price")
        
        with col2:
            competitor_avg = st.number_input("متوسط أسعار المنافسين (ر.س)", min_value=0.0, value=175.0, step=1.0, key="dyn_comp")
            season_factor = st.slider("عامل الموسمية الحالي", min_value=0.5, max_value=2.0, value=1.0, step=0.1, key="dyn_season")
        
        if st.button("🎯 احصل على التوصيات", type="primary", use_container_width=True):
            current_state = {
                'demand': current_demand,
                'capacity': capacity,
                'current_price': current_price,
                'competitor_avg_price': competitor_avg,
                'seasonality': season_factor
            }
            
            strategies = ai_model.dynamic_pricing_strategy(current_state)
            
            st.markdown("---")
            st.markdown("### 💡 التوصيات")
            
            if strategies['count'] > 0:
                for i, strategy in enumerate(strategies['strategies'], 1):
                    priority_colors = {
                        'عالية': '🔴',
                        'متوسطة': '🟡',
                        'منخفضة': '🟢'
                    }
                    
                    priority_icon = priority_colors.get(strategy['priority'], '⚪')
                    
                    with st.expander(f"{priority_icon} {strategy['type']}: {strategy['action']}", expanded=(i == 1)):
                        st.write(f"**السبب:** {strategy['reason']}")
                        
                        if 'suggested_increase' in strategy:
                            st.write(f"**الزيادة المقترحة:** {strategy['suggested_increase']}")
                        if 'suggested_decrease' in strategy:
                            st.write(f"**التخفيض المقترح:** {strategy['suggested_decrease']}")
                        if 'suggested_price' in strategy:
                            st.write(f"**السعر المقترح:** {strategy['suggested_price']:.2f} ر.س")
                        
                        st.write(f"**الأولوية:** {strategy['priority']}")
                
                # التوصية الرئيسية
                if strategies['recommended_action']:
                    st.success(f"""
                    **✅ التوصية الرئيسية:**  
                    {strategies['recommended_action']['action']} - {strategies['recommended_action']['reason']}
                    """)
            else:
                st.info("✅ السعر الحالي مناسب - لا حاجة لتعديلات")

def show_comprehensive_system():
    """صفحة النظام الشامل المتكامل"""
    st.markdown('<div class="section-header"><h2>🏆 النظام الشامل المتكامل</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو النظام الشامل المتكامل؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        نظام متكامل يجمع **جميع جوانب إدارة التسعير الاحترافية** في مكان واحد.
        
        ### 🎯 المكونات الرئيسية (7 أنظمة فرعية):
        
        **1️⃣ إدارة الجودة والامتثال**
        - معايير ISO للتسعير
        - قوائم مراجعة الجودة
        - إدارة المخاطر التنظيمية
        
        **2️⃣ إدارة الأزمات والطوارئ**
        - سيناريوهات الأزمات المحتملة
        - بروتوكولات الاستجابة السريعة
        - خطط الطوارئ
        
        **3️⃣ التعلم الآلي والتكيف**
        - تحليل الأداء التاريخي
        - التحسين المستمر
        - التوصيات الذكية
        
        **4️⃣ إدارة علاقات الموردين**
        - تقييم أداء الموردين
        - التخطيط التعاوني
        - إدارة المخاطر
        
        **5️⃣ الاستدامة والتأثير الاجتماعي**
        - حساب التكاليف البيئية
        - التسعير المسؤول اجتماعياً
        - شهادات الاستدامة
        
        **6️⃣ إدارة المعرفة والتدريب**
        - مناهج تدريبية
        - أفضل الممارسات
        - قاعدة معرفية
        
        **7️⃣ الأتمتة والروبوتات**
        - قواعد الأتمتة
        - العمليات الآلية
        - المراقبة المستمرة
        
        ### 📊 متى تستخدم هذا النظام؟
        - مؤسسات كبيرة متعددة الأقسام
        - حاجة لإدارة شاملة ومتكاملة
        - متطلبات امتثال عالية
        - رغبة في التميز التشغيلي
        """)
    
    st.markdown("---")
    
    # إنشاء النظام الشامل
    if 'comp_ecosystem' not in st.session_state:
        st.session_state.comp_ecosystem = ComprehensivePricingEcosystem("شركتك")
    
    ecosystem = st.session_state.comp_ecosystem
    
    # تبويبات النظام
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 لوحة التحكم الرئيسية",
        "✅ الجودة والامتثال",
        "🚨 إدارة الأزمات",
        "🌱 الاستدامة",
        "📚 المعرفة والتدريب"
    ])
    
    with tab1:
        st.markdown("### 🎯 لوحة التحكم الرئيسية")
        
        # نظرة عامة على النظام
        overview = ecosystem.get_system_overview()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الأنظمة الفرعية", overview['total_systems'])
        with col2:
            st.metric("مستوى التكامل", overview['integration_level'])
        with col3:
            st.metric("الحالة", overview['status'])
        
        # عرض الأنظمة الفرعية
        st.markdown("#### 📋 الأنظمة الفرعية")
        for system in overview['systems']:
            st.success(f"✅ {system}")
        
        # زر المراجعة الشاملة
        if st.button("🔍 تشغيل المراجعة الشاملة", type="primary", use_container_width=True):
            with st.spinner("جاري إجراء المراجعة الشاملة..."):
                audit = ecosystem.run_comprehensive_audit()
                
                st.success("✅ اكتملت المراجعة الشاملة!")
                
                st.markdown("### 📊 نتائج المراجعة")
                
                # عرض نتائج كل نظام
                for system_name, results in audit.items():
                    with st.expander(f"📌 {system_name}"):
                        if isinstance(results, dict):
                            if 'completion_rate' in results:
                                st.metric("نسبة الإنجاز", f"{results['completion_rate']:.1f}%")
                            elif 'success_rate' in results:
                                st.metric("نسبة النجاح", f"{results['success_rate']:.1f}%")
                            elif 'overall_score' in results:
                                st.metric("الدرجة الكلية", f"{results['overall_score']:.1%}")
                            
                            # عرض التفاصيل
                            for key, value in results.items():
                                if key not in ['completion_rate', 'success_rate', 'overall_score']:
                                    if isinstance(value, (int, float)):
                                        st.write(f"**{key}:** {value}")
                                    elif isinstance(value, dict):
                                        st.json(value)
                        elif isinstance(results, list):
                            for item in results:
                                st.write(f"• {item}")
        
        # خطة الطريق الاستراتيجية
        st.markdown("---")
        if st.button("🗺️ عرض خطة الطريق الاستراتيجية", use_container_width=True):
            roadmap = ecosystem.generate_strategic_roadmap()
            
            st.markdown("### 🗺️ خطة الطريق الاستراتيجية")
            
            for phase, goals in roadmap.items():
                phase_names = {
                    'immediate_actions': '⚡ الإجراءات الفورية',
                    'short_term_goals': '📅 الأهداف قصيرة المدى',
                    'medium_term_goals': '🎯 الأهداف متوسطة المدى',
                    'long_term_vision': '🚀 الرؤية طويلة المدى'
                }
                
                with st.expander(phase_names.get(phase, phase), expanded=True):
                    for goal in goals:
                        st.write(f"• {goal}")
    
    with tab2:
        st.markdown("### ✅ الجودة والامتثال")
        
        quality_sys = ecosystem.quality_system
        
        # معايير ISO
        st.markdown("#### 📜 معايير ISO للتسعير")
        iso_standards = quality_sys.implement_iso_pricing_standards()
        
        for standard, details in iso_standards.items():
            with st.expander(f"📋 {standard.upper()}", expanded=False):
                st.write(f"**مستوى الأمان:** {details.get('security_level', 'N/A')}")
                st.write(f"**التوثيق مطلوب:** {'نعم' if details.get('documentation_required') else 'لا'}")
                
                st.markdown("**المتطلبات:**")
                for req in details['requirements']:
                    st.write(f"• {req}")
        
        # قائمة مراجعة الجودة
        st.markdown("---")
        st.markdown("#### 📋 قائمة مراجعة الجودة")
        
        if st.button("🔍 إجراء فحص الجودة", type="primary"):
            checklist_result = quality_sys.quality_control_checklist({})
            
            st.metric("نسبة الإنجاز", f"{checklist_result['completion_rate']:.1f}%")
            st.info(f"**الحالة:** {checklist_result['approval_status']}")
            
            # عرض تفاصيل الفحص
            col1, col2 = st.columns(2)
            items = list(checklist_result['checklist'].items())
            mid = len(items) // 2
            
            with col1:
                for item, status in items[:mid]:
                    icon = "✅" if status else "❌"
                    st.write(f"{icon} {item.replace('_', ' ').title()}")
            
            with col2:
                for item, status in items[mid:]:
                    icon = "✅" if status else "❌"
                    st.write(f"{icon} {item.replace('_', ' ').title()}")
    
    with tab3:
        st.markdown("### 🚨 إدارة الأزمات والطوارئ")
        
        crisis_sys = ecosystem.crisis_system
        
        # سيناريوهات الأزمات
        st.markdown("#### 📋 سيناريوهات الأزمات المحددة")
        scenarios = crisis_sys.define_crisis_scenarios()
        
        for scenario_id, scenario_data in scenarios.items():
            priority_colors = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            priority_icon = priority_colors.get(scenario_data['priority'], '⚪')
            
            with st.expander(f"{priority_icon} {scenario_data['trigger']}", expanded=False):
                st.write(f"**الاستجابة:** {scenario_data['response']}")
                st.write(f"**الأولوية:** {scenario_data['priority']}")
                
                if 'actions' in scenario_data:
                    st.markdown("**الإجراءات:**")
                    for action in scenario_data['actions']:
                        st.write(f"• {action}")
        
        # بروتوكول الطوارئ
        st.markdown("---")
        st.markdown("#### ⚡ بروتوكول الاستجابة للطوارئ")
        
        col1, col2 = st.columns(2)
        with col1:
            crisis_type = st.selectbox(
                "نوع الأزمة",
                list(scenarios.keys()),
                format_func=lambda x: scenarios[x]['trigger']
            )
        with col2:
            severity = st.select_slider(
                "مستوى الخطورة",
                options=['low', 'medium', 'high'],
                value='medium'
            )
        
        if st.button("🚨 تفعيل بروتوكول الطوارئ", type="primary"):
            protocol = crisis_sys.emergency_pricing_protocol(crisis_type, severity)
            
            st.error(f"**الإجراء المطلوب:** {protocol['action']}")
            st.warning(f"**الموافقة المطلوبة من:** {protocol['approval_required']}")
            st.info(f"**خطة الاتصال:** {protocol['communication_plan']}")
            st.success(f"**الإطار الزمني:** {protocol['timeline']}")
    
    with tab4:
        st.markdown("### 🌱 الاستدامة والتأثير الاجتماعي")
        
        sustainability_sys = ecosystem.sustainability_system
        
        # التكاليف البيئية
        st.markdown("#### 🌍 التكاليف البيئية")
        env_costs = sustainability_sys.calculate_environmental_costs()
        
        env_df = pd.DataFrame([
            {'البند': key.replace('_', ' ').title(), 'التكلفة': f"{value} ر.س"}
            for key, value in env_costs.items()
        ])
        st.dataframe(env_df, use_container_width=True)
        
        # التأثير الاجتماعي
        st.markdown("---")
        st.markdown("#### 👥 اعتبارات التأثير الاجتماعي")
        social_impact = sustainability_sys.social_impact_pricing()
        
        social_df = pd.DataFrame([
            {
                'المعيار': key.replace('_', ' ').title(),
                'التأثير': f"{value:+.1%}" if value != 0 else "0%",
                'النوع': 'علاوة' if value > 0 else 'خصم' if value < 0 else 'محايد'
            }
            for key, value in social_impact.items()
        ])
        st.dataframe(social_df, use_container_width=True)
        
        # شهادات الاستدامة
        st.markdown("---")
        st.markdown("#### 🏅 تأثير شهادات الاستدامة")
        certifications = sustainability_sys.sustainability_certification_impact()
        
        for cert_name, cert_data in certifications.items():
            with st.expander(f"🏅 {cert_name.replace('_', ' ').title()}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("علاوة السعر", f"{cert_data['price_premium']:.0%}")
                with col2:
                    st.write(f"**الوصول للسوق:** {cert_data['market_access']}")
                st.write(f"**شريحة العملاء:** {cert_data['customer_segment']}")
    
    with tab5:
        st.markdown("### 📚 إدارة المعرفة والتدريب")
        
        knowledge_sys = ecosystem.knowledge_system
        
        # المنهج التدريبي
        st.markdown("#### 🎓 منهج التدريب على التسعير")
        curriculum = knowledge_sys.pricing_training_curriculum()
        
        for level, details in curriculum.items():
            with st.expander(f"📖 {details['level']} - {details['duration']}", expanded=False):
                st.markdown("**المواضيع:**")
                for topic in details['topics']:
                    st.write(f"• {topic}")
        
        # أفضل الممارسات
        st.markdown("---")
        st.markdown("#### ⭐ مستودع أفضل الممارسات")
        best_practices = knowledge_sys.best_practices_repository()
        
        practices_df = pd.DataFrame([
            {
                'الممارسة': data['practice'],
                'الفائدة': data['benefit'],
                'سهولة التطبيق': data['implementation']
            }
            for name, data in best_practices.items()
        ])
        st.dataframe(practices_df, use_container_width=True)
        
        # نظام الأتمتة
        st.markdown("---")
        st.markdown("#### 🤖 قواعد الأتمتة المفعّلة")
        
        automation_sys = ecosystem.automation_system
        automation_rules = automation_sys.define_automation_rules()
        
        for rule_name, rule_data in automation_rules.items():
            notification_icon = "🔔" if rule_data.get('notification') else ""
            approval_icon = "✋" if rule_data.get('approval_required') else "✅"
            
            st.info(f"""
            {approval_icon} {notification_icon} **{rule_name.replace('_', ' ').title()}**
            
            **الشرط:** {rule_data['condition']}  
            **الإجراء:** {rule_data['action']}  
            **موافقة مطلوبة:** {'نعم' if rule_data['approval_required'] else 'لا'}
            """)

def show_data_driven_pricing():
    """صفحة التسعير المبني على البيانات"""
    st.markdown('<div class="section-header"><h2>📊 التسعير المبني على البيانات</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو التسعير المبني على البيانات؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        نظام تسعير ذكي يحلل **بيانات الأرباح والخسائر (P&L)** الفعلية لشركتك لتوليد أسعار دقيقة.
        
        ### 🎯 المميزات الرئيسية:
        
        **1️⃣ تحليل التكاليف التاريخية**
        - استخراج التكاليف الفعلية من بيانات P&L
        - تحليل تكاليف كل خدمة (تجهيز، شحن، تخزين، الخ)
        - حساب التكاليف التشغيلية الحقيقية
        
        **2️⃣ هوامش الربح الذكية**
        - حساب هوامش الربح التاريخية
        - تطبيق هوامش ربح واقعية على الأسعار
        - ضمان الربحية بناءً على البيانات الفعلية
        
        **3️⃣ تحليل ربحية العملاء**
        - معرفة العملاء الأكثر ربحية
        - تصنيف العملاء (VIP, ممتاز, عادي, خاسر)
        - تسعير مخصص لكل شريحة
        
        **4️⃣ التسعير الديناميكي**
        - أسعار تتغير حسب حجم الطلب
        - خصومات تلقائية للطلبات الكبيرة
        - تسعير حسب درجة الأهمية (عادي، مستعجل، طارئ)
        
        **5️⃣ مقارنة الاستراتيجيات**
        - مقارنة الأسعار لمختلف مراكز التكلفة
        - اختيار أفضل استراتيجية تسعير
        - توصيات ذكية مبنية على البيانات
        
        ### 📋 كيف تستخدم هذه الصفحة؟
        1. **حمّل ملف P&L** (Excel) - البيانات المالية الفعلية
        2. النظام يحلل البيانات تلقائياً
        3. استخدم الأدوات المختلفة للتسعير والتحليل
        4. احصل على توصيات ذكية للأسعار
        
        ### 💼 متى تستخدم هذا النظام؟
        - لديك بيانات مالية تاريخية (P&L)
        - تريد أسعار دقيقة مبنية على أرقام حقيقية
        - تحتاج فهم عميق لربحية العملاء
        - تريد أتمتة التسعير بذكاء
        """)
    
    st.markdown("---")
    
    # تحميل بيانات P&L
    st.markdown("### 📤 الخطوة 1: تحميل بيانات P&L")
    
    uploaded_file = st.file_uploader(
        "حمّل ملف P&L (Excel)",
        type=['xlsx', 'xls'],
        help="ملف Excel يحتوي على بيانات الأرباح والخسائر"
    )
    
    if uploaded_file is not None:
        try:
            # قراءة البيانات
            with st.spinner("جاري تحميل وتحليل البيانات..."):
                df = pd.read_excel(uploaded_file)
                
                # عرض معلومات الملف
                st.success(f"✅ تم تحميل الملف بنجاح! ({len(df)} صف)")
                
                # عرض البيانات
                with st.expander("📋 معاينة البيانات المحملة", expanded=False):
                    st.dataframe(df.head(20), use_container_width=True)
                    st.info(f"**الأعمدة المتوفرة:** {', '.join(df.columns.tolist())}")
                
                # إنشاء محركات التسعير
                if 'basic_engine' not in st.session_state or st.button("🔄 إعادة تحليل البيانات"):
                    st.session_state.basic_engine = SmartPricingEngine(df)
                    st.session_state.advanced_engine = AdvancedPricingEngine(df)
                    st.success("✅ تم تحليل البيانات بنجاح!")
                
                # التبويبات
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 لوحة التحكم",
                    "💰 حاسبة الأسعار",
                    "🎯 التسعير الديناميكي",
                    "👥 تحليل العملاء",
                    "📈 مقارنة الاستراتيجيات"
                ])
                
                with tab1:
                    st.markdown("### 📊 لوحة التحكم - نظرة عامة")
                    
                    engine = st.session_state.basic_engine
                    
                    # المقاييس الرئيسية
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "إجمالي الإيرادات",
                            f"{engine.profit_margins['total_income']:,.0f} ر.س"
                        )
                    with col2:
                        st.metric(
                            "إجمالي المصروفات",
                            f"{engine.profit_margins['total_expense']:,.0f} ر.س"
                        )
                    with col3:
                        st.metric(
                            "صافي الربح",
                            f"{engine.profit_margins['net_profit']:,.0f} ر.س"
                        )
                    with col4:
                        st.metric(
                            "هامش الربح",
                            f"{engine.profit_margins['historical_margin']:.1f}%"
                        )
                    
                    st.markdown("---")
                    
                    # تحليل التكاليف
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💵 تحليل التكاليف")
                        cost_df = pd.DataFrame([
                            {'البند': key.replace('_', ' ').title(), 'التكلفة': f"{value:.2f} ر.س"}
                            for key, value in engine.cost_analysis.items()
                        ])
                        st.dataframe(cost_df, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### 📈 إحصائيات الخدمات")
                        service_data = []
                        for service, stats in engine.service_stats.items():
                            service_data.append({
                                'الخدمة': service.replace('_', ' ').title(),
                                'المتوسط': f"{stats['avg']:.2f} ر.س",
                                'الأقصى': f"{stats['max']:.2f} ر.س",
                                'الأدنى': f"{stats['min']:.2f} ر.س",
                                'العدد': stats['count']
                            })
                        st.dataframe(pd.DataFrame(service_data), use_container_width=True)
                
                with tab2:
                    st.markdown("### 💰 حاسبة الأسعار")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        service_type = st.selectbox(
                            "نوع الخدمة",
                            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام']
                        )
                        
                        cost_center = st.selectbox(
                            "مركز التكلفة",
                            ['متجر صفوة', 'متجر بيست شيلد', 'متجر تكنو مارت', 'شركة تازيا']
                        )
                    
                    with col2:
                        quantity = st.number_input("الكمية", min_value=1, value=1, step=1)
                        complexity = st.slider("معامل التعقيد", 0.5, 2.0, 1.0, 0.1)
                    
                    if st.button("💵 احسب السعر", type="primary", use_container_width=True):
                        result = engine.calculate_price(service_type, cost_center, quantity, complexity)
                        
                        st.success("✅ تم حساب السعر بنجاح!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("السعر الأساسي", f"{result['base_price']:.2f} ر.س")
                        with col2:
                            st.metric("سعر الوحدة", f"{result['unit_price']:.2f} ر.س")
                        with col3:
                            st.metric("السعر الإجمالي", f"{result['total_price']:.2f} ر.س")
                        
                        with st.expander("📋 تفاصيل السعر"):
                            st.json(result)
                
                with tab3:
                    st.markdown("### 🎯 التسعير الديناميكي")
                    
                    advanced_engine = st.session_state.advanced_engine
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        service_type_dyn = st.selectbox(
                            "نوع الخدمة",
                            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام'],
                            key='service_dyn'
                        )
                        
                        customer = st.text_input("اسم العميل", "متجر صفوة")
                    
                    with col2:
                        volume = st.number_input("حجم الطلب", min_value=1, value=100, step=10)
                        urgency = st.selectbox(
                            "مستوى الأهمية",
                            ['low', 'normal', 'high', 'urgent'],
                            format_func=lambda x: {
                                'low': 'منخفض',
                                'normal': 'عادي',
                                'high': 'عالي',
                                'urgent': 'طارئ'
                            }[x]
                        )
                    
                    if st.button("🎯 احسب السعر الديناميكي", type="primary", use_container_width=True):
                        result = advanced_engine.dynamic_pricing(service_type_dyn, customer, volume, urgency)
                        
                        st.success("✅ تم حساب السعر الديناميكي!")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("السعر الأساسي", f"{result['base_unit_price']:.2f} ر.س")
                        with col2:
                            st.metric("السعر الديناميكي", f"{result['dynamic_unit_price']:.2f} ر.س")
                        with col3:
                            st.metric("السعر الإجمالي", f"{result['total_price']:.2f} ر.س")
                        with col4:
                            st.metric("التوفير", f"{result['savings']:.2f} ر.س")
                        
                        st.info(f"**شريحة العميل:** {result['customer_tier']}")
                        st.info(f"**خصم الحجم:** {result['volume_discount']}")
                        
                        # التوصيات
                        st.markdown("---")
                        st.markdown("#### 💡 التوصيات الذكية")
                        recommendations = advanced_engine.get_pricing_recommendations(
                            service_type_dyn, customer, volume
                        )
                        
                        for rec in recommendations:
                            if rec['priority'] == 'critical':
                                st.error(f"🚨 **{rec['type']}:** {rec['message']}")
                            elif rec['priority'] == 'high':
                                st.warning(f"⚠️ **{rec['type']}:** {rec['message']}")
                            else:
                                st.info(f"ℹ️ **{rec['type']}:** {rec['message']}")
                
                with tab4:
                    st.markdown("### 👥 تحليل ربحية العملاء")
                    
                    advanced_engine = st.session_state.advanced_engine
                    
                    if advanced_engine.customer_profitability:
                        # جدول ربحية العملاء
                        customer_df = pd.DataFrame([
                            {
                                'العميل': customer,
                                'الإيرادات': f"{data['income']:,.2f} ر.س",
                                'المصروفات': f"{data['expenses']:,.2f} ر.س",
                                'صافي الربح': f"{data['net_profit']:,.2f} ر.س",
                                'هامش الربح %': f"{data['profitability']:.1f}%",
                                'التصنيف': 'VIP' if data['profitability'] > 30 else 
                                            'ممتاز' if data['profitability'] > 20 else
                                            'جيد' if data['profitability'] > 10 else
                                            'عادي' if data['profitability'] > 0 else 'خاسر'
                            }
                            for customer, data in advanced_engine.customer_profitability.items()
                        ])
                        
                        st.dataframe(customer_df, use_container_width=True)
                        
                        # رسم بياني
                        st.markdown("---")
                        fig = px.bar(
                            customer_df,
                            x='العميل',
                            y='صافي الربح',
                            title='صافي الربح لكل عميل',
                            color='التصنيف',
                            color_discrete_map={
                                'VIP': '#00b894',
                                'ممتاز': '#0984e3',
                                'جيد': '#fdcb6e',
                                'عادي': '#636e72',
                                'خاسر': '#d63031'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("⚠️ لا توجد بيانات عملاء في ملف P&L")
                
                with tab5:
                    st.markdown("### 📈 مقارنة استراتيجيات التسعير")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        service_compare = st.selectbox(
                            "نوع الخدمة",
                            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام'],
                            key='service_compare'
                        )
                    with col2:
                        quantity_compare = st.number_input(
                            "الكمية",
                            min_value=1,
                            value=100,
                            step=10,
                            key='quantity_compare'
                        )
                    
                    if st.button("📊 مقارنة الاستراتيجيات", type="primary", use_container_width=True):
                        strategies = advanced_engine.compare_pricing_strategies(
                            service_compare,
                            quantity_compare
                        )
                        
                        # جدول المقارنة
                        compare_df = pd.DataFrame([
                            {
                                'مركز التكلفة': center,
                                'السعر الأساسي': f"{data['base_price']:.2f} ر.س",
                                'سعر الوحدة': f"{data['unit_price']:.2f} ر.س",
                                'السعر الإجمالي': f"{data['total_price']:.2f} ر.س",
                                'هامش الربح': f"{data['profit_margin']:.1f}%"
                            }
                            for center, data in strategies.items()
                        ])
                        
                        st.dataframe(compare_df, use_container_width=True)
                        
                        # رسم بياني
                        st.markdown("---")
                        fig = px.bar(
                            compare_df,
                            x='مركز التكلفة',
                            y='السعر الإجمالي',
                            title=f'مقارنة الأسعار - {service_compare}',
                            text='السعر الإجمالي'
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
            st.info("تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
    
    else:
        st.info("📤 قم بتحميل ملف P&L للبدء في التحليل والتسعير")
        
        # معلومات إضافية
        with st.expander("ℹ️ متطلبات ملف P&L"):
            st.markdown("""
            يجب أن يحتوي ملف Excel على الأعمدة التالية:
            
            - **Account Level 1**: تصنيف الحساب (income/expense)
            - **Account Level 2**: نوع الخدمة (ايراد التجهيز، مصاريف تجهيز، الخ)
            - **Account Level 3**: تفاصيل إضافية (شحن داخل/خارج الرياض، الخ)
            - **net_amount**: المبلغ الصافي
            - **Customer** (اختياري): اسم العميل لتحليل الربحية
            
            **مثال:**
            | Account Level 1 | Account Level 2 | Account Level 3 | net_amount | Customer |
            |----------------|----------------|----------------|-----------|----------|
            | income | ايراد التجهيز | - | 5000 | متجر صفوة |
            | expense | مصاريف تجهيز | - | -2000 | متجر صفوة |
            """)

def show_orders_processor():
    """صفحة معالجة بيانات الطلبات"""
    st.markdown('<div class="section-header"><h2>📦 معالج بيانات الطلبات</h2></div>', unsafe_allow_html=True)
    
    # شرح الصفحة
    with st.expander("📖 ما هو معالج بيانات الطلبات؟", expanded=False):
        st.markdown("""
        ### 💡 التعريف:
        نظام متقدم لمعالجة وتحليل **بيانات الطلبات الكبيرة** من أنظمة التجارة الإلكترونية.
        
        ### 🎯 المميزات الرئيسية:
        
        **1️⃣ معالجة البيانات الكبيرة بكفاءة**
        - معالجة الملفات الضخمة (حتى مئات الآلاف من السجلات)
        - تحسين استخدام الذاكرة (توفير حتى 90%)
        - معالجة على دفعات (Chunks) لتجنب نفاد الذاكرة
        - تنظيف وتحويل البيانات تلقائياً
        
        **2️⃣ تحليل تكاليف الشحن**
        - تحليل تكاليف الشحن لكل مدينة
        - متوسط التكلفة لكل شريك شحن
        - أنماط التكلفة حسب الوزن والمنطقة
        
        **3️⃣ تحليل الأداء الإقليمي**
        - متوسط قيمة الطلب لكل منطقة
        - أكثر المناطق ربحية
        - طرق الدفع المفضلة حسب المنطقة
        
        **4️⃣ تقييم شركاء الشحن**
        - ترتيب الشركاء حسب الأداء
        - تحليل التكلفة مقابل الجودة
        - توصيات ذكية لاختيار الشريك
        
        **5️⃣ حساب التسعير الشامل**
        - سعر الخدمة + الشحن + التكاليف الإضافية
        - حساب رسوم COD تلقائياً
        - رسوم التغليف والمناولة والتأمين
        
        ### 📋 الاستخدامات:
        - معالجة ملفات الطلبات من منصات التجارة الإلكترونية
        - تحليل أداء الشحن والتكاليف
        - تحسين استراتيجيات التسعير
        - اختيار أفضل شركاء الشحن
        
        ### 💼 البيانات المطلوبة:
        - ORDER ID
        - DESTINATION CITY
        - SHIPPING COST
        - SHIPMENT WEIGHT
        - ORDER AMOUNT
        - PAYMENT METHOD
        - SHIPPING PARTNER
        """)
    
    st.markdown("---")
    
    # تحميل بيانات الطلبات
    st.markdown("### 📤 الخطوة 1: تحميل بيانات الطلبات")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "حمّل ملف الطلبات (CSV أو Excel)",
            type=['csv', 'xlsx', 'xls'],
            help="ملف يحتوي على بيانات الطلبات من منصة التجارة الإلكترونية"
        )
    
    with col2:
        sample_size = st.number_input(
            "حجم العينة (0 = الكل)",
            min_value=0,
            max_value=1000000,
            value=0,
            step=1000,
            help="لتسريع المعالجة، يمكنك أخذ عينة من البيانات"
        )
    
    if uploaded_file is not None:
        try:
            # قراءة البيانات
            with st.spinner("جاري تحميل ومعالجة البيانات..."):
                processor = OrderDataProcessor(dataframe=None)
                
                # حفظ الملف مؤقتاً
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                processor.file_path = tmp_path
                sample = sample_size if sample_size > 0 else None
                df = processor.load_data(sample_size=sample)
                
                if df.empty:
                    st.error("❌ فشل تحميل البيانات")
                    return
                
                # عرض معلومات الملف
                summary = get_data_summary(df)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("إجمالي الصفوف", f"{summary['total_rows']:,}")
                with col2:
                    st.metric("الأعمدة", summary['total_columns'])
                with col3:
                    st.metric("استخدام الذاكرة", summary['memory_usage'])
                with col4:
                    if summary['date_range']:
                        st.metric("نطاق التواريخ", summary['date_range'])
                
                # عرض البيانات
                with st.expander("📋 معاينة البيانات", expanded=False):
                    st.dataframe(df.head(20), use_container_width=True)
                    st.info(f"**الأعمدة المتوفرة:** {', '.join(df.columns.tolist())}")
                
                # إنشاء المحسن
                if st.button("🔍 تحليل البيانات وإنشاء محسن التسعير", type="primary"):
                    with st.spinner("جاري التحليل..."):
                        optimizer = PricingOptimizer(df)
                        st.session_state.orders_optimizer = optimizer
                        st.session_state.orders_data = df
                        st.success("✅ تم تحليل البيانات بنجاح!")
                
                # التبويبات
                if 'orders_optimizer' in st.session_state:
                    optimizer = st.session_state.orders_optimizer
                    
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 لوحة التحكم",
                        "🚚 تحليل الشحن",
                        "🗺️ التحليل الإقليمي",
                        "💰 حاسبة التسعير الشامل"
                    ])
                    
                    with tab1:
                        st.markdown("### 📊 لوحة التحكم - نظرة عامة")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        # إحصائيات عامة
                        if 'ORDER AMOUNT' in df.columns:
                            total_revenue = df['ORDER AMOUNT'].sum()
                            avg_order = df['ORDER AMOUNT'].mean()
                            
                            with col1:
                                st.metric("إجمالي الإيرادات", f"{total_revenue:,.2f} ر.س")
                            with col2:
                                st.metric("متوسط قيمة الطلب", f"{avg_order:,.2f} ر.س")
                        
                        if 'SHIPPING COST' in df.columns:
                            total_shipping = df['SHIPPING COST'].sum()
                            avg_shipping = df['SHIPPING COST'].mean()
                            
                            with col3:
                                st.metric("متوسط تكلفة الشحن", f"{avg_shipping:,.2f} ر.س")
                        
                        st.markdown("---")
                        
                        # إحصائيات إضافية
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if 'PAYMENT METHOD' in df.columns:
                                st.markdown("#### 💳 طرق الدفع")
                                payment_counts = df['PAYMENT METHOD'].value_counts()
                                fig = px.pie(
                                    values=payment_counts.values,
                                    names=payment_counts.index,
                                    title='توزيع طرق الدفع'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            if 'SHIPPING PARTNER' in df.columns:
                                st.markdown("#### 🚚 شركاء الشحن")
                                partner_counts = df['SHIPPING PARTNER'].value_counts().head(5)
                                fig = px.bar(
                                    x=partner_counts.index,
                                    y=partner_counts.values,
                                    title='أكثر 5 شركاء شحن استخداماً',
                                    labels={'x': 'الشريك', 'y': 'عدد الشحنات'}
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        st.markdown("### 🚚 تحليل الشحن")
                        
                        if not optimizer.shipping_analysis.empty:
                            st.dataframe(optimizer.shipping_analysis, use_container_width=True)
                            
                            # رسم بياني
                            if 'DESTINATION CITY' in optimizer.shipping_analysis.columns:
                                top_cities = optimizer.shipping_analysis.nlargest(10, 'ORDER ID')
                                fig = px.bar(
                                    top_cities,
                                    x='DESTINATION CITY',
                                    y='SHIPPING COST',
                                    title='متوسط تكلفة الشحن - أكثر 10 مدن',
                                    labels={'DESTINATION CITY': 'المدينة', 'SHIPPING COST': 'التكلفة'}
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("⚠️ لا توجد بيانات كافية لتحليل الشحن")
                        
                        # تحليل شركاء الشحن
                        st.markdown("---")
                        st.markdown("#### 📊 أداء شركاء الشحن")
                        
                        if not optimizer.partner_performance.empty:
                            st.dataframe(optimizer.partner_performance, use_container_width=True)
                        else:
                            st.info("لا توجد بيانات شركاء الشحن")
                    
                    with tab3:
                        st.markdown("### 🗺️ التحليل الإقليمي")
                        
                        if not optimizer.regional_analysis.empty:
                            st.dataframe(optimizer.regional_analysis, use_container_width=True)
                            
                            # رسم بياني للمناطق
                            if 'ORDER AMOUNT_mean' in optimizer.regional_analysis.columns:
                                top_regions = optimizer.regional_analysis.nlargest(10, 'ORDER ID_count')
                                fig = px.scatter(
                                    top_regions,
                                    x='ORDER AMOUNT_mean',
                                    y='SHIPPING COST_mean',
                                    size='ORDER ID_count',
                                    hover_name='DESTINATION CITY',
                                    title='تحليل المناطق: قيمة الطلب vs تكلفة الشحن',
                                    labels={
                                        'ORDER AMOUNT_mean': 'متوسط قيمة الطلب',
                                        'SHIPPING COST_mean': 'متوسط تكلفة الشحن',
                                        'ORDER ID_count': 'عدد الطلبات'
                                    }
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("⚠️ لا توجد بيانات إقليمية كافية")
                    
                    with tab4:
                        st.markdown("### 💰 حاسبة التسعير الشامل")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # الحصول على قائمة المدن
                            cities = df['DESTINATION CITY'].unique().tolist() if 'DESTINATION CITY' in df.columns else ['الرياض']
                            selected_city = st.selectbox("المدينة", cities)
                            
                            weight = st.number_input("الوزن (كجم)", min_value=0.1, value=2.0, step=0.1)
                            order_value = st.number_input("قيمة الطلب (ر.س)", min_value=0.0, value=300.0, step=10.0)
                        
                        with col2:
                            payment_method = st.selectbox(
                                "طريقة الدفع",
                                ['PREPAID', 'POSTPAID'],
                                format_func=lambda x: 'مدفوع مسبقاً' if x == 'PREPAID' else 'الدفع عند الاستلام'
                            )
                            
                            service_type = st.selectbox(
                                "نوع الخدمة",
                                ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام']
                            )
                        
                        if st.button("💵 احسب التسعير الشامل", type="primary", use_container_width=True):
                            # حساب سعر الشحن
                            shipping_price = optimizer.calculate_optimal_shipping_price(
                                city=selected_city,
                                weight=weight,
                                order_value=order_value,
                                payment_method=payment_method
                            )
                            
                            # حساب التكاليف الإضافية
                            additional = optimizer.calculate_additional_costs(
                                weight=weight,
                                payment_method=payment_method,
                                order_value=order_value
                            )
                            
                            # توصية الشريك
                            recommended_partner = optimizer.recommend_shipping_partner(
                                city=selected_city,
                                weight=weight
                            )
                            
                            # عرض النتائج
                            st.success("✅ تم حساب التسعير!")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("سعر الشحن", f"{shipping_price:.2f} ر.س")
                            with col2:
                                st.metric("التكاليف الإضافية", f"{additional['total_additional']:.2f} ر.س")
                            with col3:
                                total = shipping_price + additional['total_additional']
                                st.metric("الإجمالي", f"{total:.2f} ر.س")
                            
                            # تفاصيل التكاليف
                            with st.expander("📋 تفاصيل التكاليف الإضافية"):
                                for key, value in additional.items():
                                    if key != 'total_additional':
                                        st.write(f"**{key.replace('_', ' ').title()}:** {value:.2f} ر.س")
                            
                            st.info(f"**🚚 الشريك الموصى به:** {recommended_partner}")
        
        except Exception as e:
            st.error(f"❌ خطأ في المعالجة: {str(e)}")
            import traceback
            with st.expander("تفاصيل الخطأ"):
                st.code(traceback.format_exc())
    
    else:
        st.info("📤 قم بتحميل ملف الطلبات للبدء في التحليل")
        
        # معلومات إضافية
        with st.expander("ℹ️ متطلبات ملف الطلبات"):
            st.markdown("""
            ### الأعمدة المطلوبة (أو المشابهة):
            
            #### أساسية:
            - **ORDER ID**: معرّف الطلب
            - **DESTINATION CITY**: مدينة الوجهة
            - **SHIPPING COST**: تكلفة الشحن
            - **ORDER AMOUNT**: قيمة الطلب
            
            #### اختيارية (لتحليلات متقدمة):
            - **SHIPMENT WEIGHT**: وزن الشحنة
            - **SHIPPING PARTNER**: شريك الشحن
            - **PAYMENT METHOD**: طريقة الدفع (PREPAID/POSTPAID)
            - **ORDER CREATED AT**: تاريخ إنشاء الطلب
            - **ORDER DELIVERED AT**: تاريخ التسليم
            - **COD FEE**: رسوم الدفع عند الاستلام
            
            ### نصائح للأداء:
            - للملفات الكبيرة (>100,000 صف)، استخدم حجم عينة أصغر للتجربة
            - تأكد من أن الأسماء باللغة الإنجليزية
            - CSV أسرع من Excel للملفات الكبيرة
            """)

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # الشريط الجانبي
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=MATALI+PRO", use_container_width=True)
        st.markdown("---")
        
        page = st.radio(
            "📌 القائمة الرئيسية",
            [
                "🏠 الصفحة الرئيسية",
                "📊 الداشبورد المتقدم",
                "⚙️ إعداد الطاقة",
                "💵 شرائح الأسعار",
                "🤖 التسعير الديناميكي",
                "📐 نموذج التسعير CMA",
                "🎯 التسعير المتقدم",
                "🏢 التسعير المؤسسي",
                "🔮 التسعير التنبؤي AI",
                "📊 التسعير المبني على البيانات",
                "📦 معالج بيانات الطلبات",
                "🏆 النظام الشامل المتكامل",
                "📋 عرض سعر جديد",
                "📜 سجل العروض",
                "📥 قوالب Excel"
            ]
        )
        
        st.markdown("---")
        
        # دليل الاستخدام السريع
        with st.expander("📖 دليل الاستخدام السريع"):
            st.markdown("""
            ### 🚀 خطوات البدء:
            
            **1️⃣ أضف بيانات الطاقة**
            - اذهب إلى "⚙️ إعداد الطاقة"
            - أدخل خدماتك وطاقتها الاستيعابية
            
            **2️⃣ حدد الأسعار**
            - استخدم "🤖 التسعير الديناميكي" (مُوصى)
            - أو أدخلها يدوياً في "💵 شرائح الأسعار"
            
            **3️⃣ أنشئ عروض الأسعار**
            - اذهب إلى "📋 عرض سعر جديد"
            - احسب التكاليف والأرباح تلقائياً
            
            **4️⃣ راجع التحليلات**
            - تابع الأداء في "📊 الداشبورد المتقدم"
            """)
        
        st.markdown("---")
        st.markdown("### ℹ️ معلومات النظام")
        st.info("""
        **نظام متالى للتسعير الذكي**
        
        الإصدار: 1.0
        
        © 2025 نظام متالي
        """)
    
    # عرض الصفحة المطلوبة
    if page == "🏠 الصفحة الرئيسية":
        st.markdown('<div class="main-header">🏠 الصفحة الرئيسية</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ## مرحباً بك في نظام متالى للتسعير الذكي
        
        نظام متكامل لإدارة الطاقة الاستيعابية والتسعير الديناميكي للخدمات اللوجستية
        """)
        
        # إرشادات البداية السريعة
        capacity_df = pricing_system.load_capacity_data()
        pricing_df = pricing_system.load_pricing_data()
        
        if capacity_df.empty:
            st.warning("""
            ### 👋 مرحباً! يبدو أنك تستخدم النظام لأول مرة
            
            **لا توجد بيانات حالياً** - وهذا طبيعي! اتبع الخطوات التالية:
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                ### 1️⃣ الخطوة الأولى: أضف الخدمات
                
                اذهب إلى **"⚙️ إعداد الطاقة"** وأضف:
                - خدمات الاستلام (Receiving)
                - خدمات التخزين (Storage)
                - خدمات التجهيز (Fulfillment)
                - خدمات الشحن (Shipping)
                - الخدمات الإضافية (Value Added)
                
                💡 **نصيحة:** حمّل قالب Excel من صفحة "📥 قوالب Excel" واملأه ثم ارفعه
                """)
            
            with col2:
                st.info("""
                ### 2️⃣ الخطوة الثانية: حدد الأسعار
                
                بعد إضافة الخدمات:
                - استخدم **"🤖 التسعير الديناميكي"** لحساب الأسعار تلقائياً
                - أو أدخلها يدوياً في **"💵 شرائح الأسعار"**
                
                💡 **نصيحة:** التسعير الديناميكي يحسب الأسعار بناءً على التكاليف والطاقة والأرباح المستهدفة
                """)
        else:
            st.success("✅ رائع! لديك بيانات في النظام")
        
        st.markdown("""
        ---
        ### 🎯 شرح الصفحات:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### ⚙️ إعداد الطاقة
            **الغرض:** إدخال بيانات الخدمات وطاقتها الاستيعابية
            - أضف خدمات جديدة
            - حدد الطاقة اليومية أو الثابتة
            - أدخل التكاليف الشهرية
            - النظام يحسب تكلفة الوحدة تلقائياً
            
            #### 💵 شرائح الأسعار
            **الغرض:** تحديد أسعار الخدمات حسب الكميات
            - أسعار مختلفة للكميات الصغيرة والكبيرة
            - خصومات تلقائية للكميات الأكبر
            - مرونة في التسعير
            
            #### 🤖 التسعير الديناميكي
            **الغرض:** حساب الأسعار تلقائياً بذكاء
            - يحسب تكلفة الهدر (الطاقة غير المستغلة)
            - يضيف هامش الربح المطلوب
            - ينشئ 4 شرائح أسعار تلقائياً
            - يوفر الوقت والدقة
            - **مناسب للخدمات اللوجستية**
            
            #### 📐 نموذج التسعير CMA
            **الغرض:** تحليل تسعير شامل للمحاسبة الإدارية
            - تحليل التكاليف الثابتة والمتغيرة
            - حساب نقطة التعادل وهامش الأمان
            - تحليل مرونة الطلب السعرية
            - مقارنة سيناريوهات أسعار مختلفة
            - **مناسب لأي منتج أو خدمة**
            
            #### 📋 عرض سعر جديد
            **الغرض:** إنشاء عروض أسعار للعملاء
            - اختر الخدمات والكميات
            - النظام يحسب الأسعار تلقائياً
            - يعرض إجمالي التكاليف والأرباح
            - يحفظ العروض للمراجعة لاحقاً
            """)
        
        with col2:
            st.markdown("""
            #### 📜 سجل العروض
            **الغرض:** مراجعة جميع العروض السابقة
            - قائمة بكل عروض الأسعار
            - فلترة حسب العميل أو التاريخ
            - تحليل الأرباح والإيرادات
            - تتبع حالة العروض
            
            #### 📊 الداشبورد المتقدم
            **الغرض:** تحليلات شاملة للأداء
            - مؤشرات الأداء الرئيسية (KPIs)
            - تحليل الربحية والإيرادات
            - تحليل استغلال الطاقة والهدر
            - تنبيهات وتوصيات ذكية
            - تقارير جاهزة للتحميل
            
            #### 📥 قوالب Excel
            **الغرض:** تسهيل إدخال البيانات بالجملة
            - تحميل قوالب Excel فارغة
            - تعبئتها خارج البرنامج
            - رفعها لاستيراد البيانات دفعة واحدة
            - توفير الوقت عند إدخال بيانات كثيرة
            """)
        
        st.markdown("---")
        
        # عرض بعض الإحصائيات السريعة
        capacity_df = pricing_system.load_capacity_data()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card positive-metric">
                <h3>الخدمات النشطة</h3>
                <h2>{}</h2>
            </div>
            """.format(len(capacity_df)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>الطاقة الإجمالية</h3>
                <h2>{:,.0f}</h2>
            </div>
            """.format(capacity_df['monthly_capacity'].sum()), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>التكاليف الشهرية</h3>
                <h2>{:,.0f} ر.س</h2>
            </div>
            """.format(capacity_df['monthly_cost'].sum()), unsafe_allow_html=True)
    
    elif page == "📊 الداشبورد المتقدم":
        from advanced_dashboard import AdvancedDashboard
        dashboard = AdvancedDashboard(pricing_system)
        dashboard.show_professional_dashboard()
    
    elif page == "⚙️ إعداد الطاقة":
        show_capacity_setup()
    
    elif page == "💵 شرائح الأسعار":
        show_pricing_tiers()
    
    elif page == "🤖 التسعير الديناميكي":
        show_dynamic_pricing()
    
    elif page == "📐 نموذج التسعير CMA":
        show_cma_pricing()
    
    elif page == "🎯 التسعير المتقدم":
        show_advanced_pricing()
    
    elif page == "🏢 التسعير المؤسسي":
        show_enterprise_pricing()
    
    elif page == "🔮 التسعير التنبؤي AI":
        show_predictive_ai()
    
    elif page == "📊 التسعير المبني على البيانات":
        show_data_driven_pricing()
    
    elif page == "📦 معالج بيانات الطلبات":
        show_orders_processor()
    
    elif page == "🏆 النظام الشامل المتكامل":
        show_comprehensive_system()
    
    elif page == "📋 عرض سعر جديد":
        show_new_quote()
    
    elif page == "📜 سجل العروض":
        show_quotes_history()
    
    elif page == "📥 قوالب Excel":
        show_excel_template()

if __name__ == "__main__":
    main()
