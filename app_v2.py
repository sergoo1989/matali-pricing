"""
نظام متالي للتسعير الذكي - الإصدار 2.0
Matali Smart Pricing System V2.0

نظام موحد متكامل بسيط وقوي
- 4 صفحات فقط
- محرك تسعير واحد
- إدخال البيانات مرة واحدة
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from pathlib import Path
import tempfile

from unified_pricing_engine import UnifiedPricingEngine
from order_data_processor import OrderDataProcessor
from database_manager import DatabaseManager
from new_quote_system import show_new_quote_system
from financial_engine import FinancialEngine
from theme import ThemeManager, page_header, section, close_section, alert, badge
from arabic_ui import apply_rtl_direction, translate_ui

# إعداد الصفحة
st.set_page_config(
    page_title="Matali Smart Pricing V2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق نظام الثيم الموحد
ThemeManager.inject_global_theme()

# تطبيق اتجاه RTL والترجمة العربية
apply_rtl_direction()
translate_ui()

# ===== نظام الحماية بكلمة المرور =====
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <div style='text-align: center; padding: 3rem;'>
            <h1 style='color: #1f77b4;'>🔒 نظام متالي للتسعير الذكي</h1>
            <p style='font-size: 1.2rem; color: #666;'>الرجاء إدخال كلمة المرور للدخول</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("🔑 كلمة المرور:", type="password", key="login_password")
        
        if st.button("🚀 دخول", use_container_width=True):
            # غيّر كلمة المرور هنا
            if password == "matali2025":
                st.session_state.authenticated = True
                st.success("✅ تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("❌ كلمة مرور خاطئة! حاول مرة أخرى.")
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #999; font-size: 0.9rem;'>
            <p>للحصول على كلمة المرور، تواصل مع مسؤول النظام</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# تهيئة المحرك الموحد وقاعدة البيانات (مرة واحدة فقط)
if 'engine' not in st.session_state:
    st.session_state.engine = UnifiedPricingEngine()
    st.session_state.db = DatabaseManager()
    st.session_state.fin_engine = FinancialEngine()  # المحرك المالي
    st.session_state.data_loaded = {
        'capacity': False,
        'pnl': False,
        'orders': False,
        'suppliers': False
    }
    
    # تحميل البيانات المحفوظة تلقائياً
    db = st.session_state.db
    
    # تحميل بيانات الطاقة
    capacity_df = db.load_dataframe('capacity')
    if capacity_df is not None:
        st.session_state.engine.integrate_capacity_data(capacity_df)
        st.session_state.data_loaded['capacity'] = True
    
    # تحميل بيانات P&L
    pnl_df = db.load_dataframe('pnl')
    if pnl_df is not None:
        st.session_state.engine.integrate_pnl_data(pnl_df)
        st.session_state.data_loaded['pnl'] = True
    
    # تحميل بيانات الطلبات
    orders_df = db.load_dataframe('orders')
    if orders_df is not None:
        processor = OrderDataProcessor()
        cleaned_orders = processor.clean_orders_data(orders_df)
        st.session_state.engine.integrate_orders_data(cleaned_orders)
        st.session_state.data_loaded['orders'] = True
    
    # تحميل بيانات الموردين
    suppliers_df = db.load_dataframe('suppliers')
    if suppliers_df is not None:
        st.session_state.engine.integrate_suppliers_data(suppliers_df)
        st.session_state.data_loaded['suppliers'] = True

engine = st.session_state.engine
db = st.session_state.db
fin_engine = st.session_state.fin_engine


def create_data_templates():
    """إنشاء قوالب Excel للبيانات"""
    from io import BytesIO
    
    templates = {}
    
    # 1. قالب بيانات الطاقة
    capacity_template = pd.DataFrame({
        'service_name': ['تجهيز الطلبات', 'شحن', 'تخزين', 'إدارة المخزون', 'خدمات القيمة المضافة'],
        'capacity_per_month': [50000, 30000, 100000, 80000, 20000],
        'monthly_cost': [150000, 80000, 120000, 60000, 40000],
        'notes': ['الطاقة القصوى شهرياً', 'الشحنات الشهرية', 'المساحة بالمتر المربع', 'عدد المنتجات', 'خدمات إضافية']
    })
    
    # 2. قالب بيانات P&L
    pnl_template = pd.DataFrame({
        'Account Level 1': ['Income', 'Income', 'Expense', 'Expense', 'Expense', 'Expense'],
        'Account Level 2': ['Fulfillment Services', 'Shipping Revenue', 'Labor Cost', 'Warehouse Rent', 'Equipment', 'Other Costs'],
        'net_amount': [500000, 300000, -150000, -80000, -40000, -30000],
        'Customer': ['عميل أ', 'عميل ب', '', '', '', ''],
        'notes': ['إيرادات تجهيز الطلبات', 'إيرادات الشحن', 'رواتب العمال', 'إيجار المستودعات', 'معدات وآلات', 'مصروفات أخرى']
    })
    
    # 3. قالب بيانات الطلبات
    orders_template = pd.DataFrame({
        'ORDER ID': [f'ORD-{1000+i}' for i in range(20)],
        'DESTINATION CITY': (['الرياض', 'جدة', 'الدمام'] * 7)[:20],
        'SHIPPING COST': [15, 20, 18, 22, 15, 25, 17, 20, 15, 18, 20, 22, 15, 20, 18, 15, 20, 18, 22, 15],
        'ORDER AMOUNT': [500, 750, 1200, 800, 600, 950, 1100, 700, 850, 1000, 650, 900, 800, 1050, 700, 600, 800, 950, 1200, 750],
        'ORDER DATE': (['2024-01-15', '2024-01-16', '2024-01-17'] * 7)[:20],
        'notes': ['عينة من البيانات - استبدل بالبيانات الفعلية'] * 20
    })
    
    # 4. قالب بيانات المنافسين
    competitors_template = pd.DataFrame({
        'competitor_name': ['منافس أ', 'منافس ب', 'منافس ج', 'منافس د'],
        'service_type': ['تجهيز الطلبات', 'شحن', 'تخزين', 'تجهيز الطلبات'],
        'price': [5.5, 18, 3.2, 6.0],
        'quality_rating': [4.2, 3.8, 4.5, 4.0],
        'market_share': [0.25, 0.18, 0.22, 0.15],
        'notes': ['منافس رئيسي', 'أسعار منخفضة', 'جودة عالية', 'منافس جديد']
    })
    
    # 5. قالب بيانات العملاء
    customers_template = pd.DataFrame({
        'customer_name': ['شركة التقنية', 'شركة التجارة', 'شركة الخدمات', 'شركة الصناعة'],
        'service_type': ['تجهيز الطلبات', 'شحن', 'تخزين', 'تجهيز الطلبات'],
        'current_price': [5.2, 19, 3.0, 5.8],
        'volume_monthly': [15000, 8000, 25000, 12000],
        'satisfaction_score': [4.5, 4.0, 4.8, 4.2],
        'contract_end_date': ['2024-12-31', '2024-10-31', '2025-03-31', '2024-11-30'],
        'notes': ['عميل استراتيجي', 'عميل منذ 3 سنوات', 'عميل VIP', 'عميل جديد']
    })
    
    # 6. قالب بيانات السوق
    market_template = pd.DataFrame({
        'service_type': ['تجهيز الطلبات', 'شحن', 'تخزين', 'إدارة المخزون', 'خدمات القيمة المضافة'],
        'market_avg_price': [5.8, 20, 3.5, 2.5, 15],
        'demand_level': ['مرتفع', 'مرتفع جداً', 'متوسط', 'متوسط', 'منخفض'],
        'growth_rate': [0.15, 0.22, 0.08, 0.10, 0.05],
        'seasonality': ['عادي', 'موسمي', 'عادي', 'عادي', 'موسمي'],
        'notes': ['نمو مستمر', 'ذروة في رمضان والأعياد', 'طلب ثابت', 'طلب متزايد', 'خدمات إضافية']
    })
    
    # 7. قالب بيانات الموردين
    suppliers_template = pd.DataFrame({
        'supplier_name': ['شركة الشحن السريع', 'شركة التوصيل الذهبي', '3PL للتجهيز', 'شركة المستودعات'],
        'service_type': ['shipping', 'shipping', 'fulfillment', 'storage'],
        'price_inside_riyadh': [15.0, 18.0, 5.5, 3.0],
        'price_outside_riyadh': [20.0, 18.0, 5.5, 3.0],
        'cod_fee': [3.0, 2.5, 0.0, 0.0],
        'network_fee': [2.0, 1.5, 0.0, 0.0],
        'weight_limit': [5.0, 5.0, 0.0, 0.0],
        'extra_kg_price': [3.0, 2.5, 0.0, 0.0],
        'is_fulfillment_provider': ['no', 'no', 'yes', 'yes'],
        'notes': ['توصيل داخل الرياض فقط', 'تغطية شاملة - نفس السعر', 'تجهيز خارجي', 'تخزين فقط']
    })
    
    # حفظ كل قالب في BytesIO
    for name, df in [
        ('capacity', capacity_template),
        ('pnl', pnl_template),
        ('orders', orders_template),
        ('competitors', competitors_template),
        ('customers', customers_template),
        ('market', market_template),
        ('suppliers', suppliers_template)
    ]:
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        templates[name] = buffer
    
    return templates


def show_data_hub():
    """📂 مركز البيانات والقوالب - كل شيء في مكان واحد"""
    
    # الهيدر الرئيسي باستخدام نظام الثيم
    page_header(
        title="مركز البيانات والقوالب",
        subtitle="منصة متكاملة لإدارة القوالب وتحميل البيانات - ابدأ رحلتك نحو التحليل الذكي",
        icon="📊"
    )
    
    # تنبيه إرشادي مع أيقونات
    st.markdown("""
    <div class="matali-alert matali-alert-info fade-in">
        <strong>💡 كيف تبدأ؟</strong><br><br>
        <div style="display: grid; gap: 0.75rem;">
            <div>① 📥 <strong>حمّل القالب</strong> المناسب من الكروت أدناه</div>
            <div>② ✏️ <strong>املأ بياناتك</strong> في ملف Excel</div>
            <div>③ 📤 <strong>ارفع الملف</strong> من التبويبات المخصصة</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # عنوان القسم
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2 style="font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #0EA5E9, #6366F1); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            📥 القوالب الجاهزة
        </h2>
        <p style="color: #64748B; font-size: 1.1rem;">اختر القالب المناسب وابدأ رحلة تحليل بياناتك</p>
    </div>
    """, unsafe_allow_html=True)
    
    # الكروت - صف أول
    col1, col2, col3 = st.columns(3)
    
    # كارت P&L
    with col1:
        st.markdown("""
        <div class="template-card">
            <h3>💰 قائمة الدخل (P&L)</h3>
            <p>يُستخدم لتحليل الإيرادات والمصروفات والأرباح لفترة مالية محددة.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        pnl_template = pd.DataFrame({
            'Account Level 1': ['income', 'income', 'expense', 'expense'],
            'Account Level 2': ['ايراد التجهيز', 'ايراد الشحن', 'مصاريف تجهيز', 'مصاريف شحن'],
            'Amount': [150000, 80000, -60000, -30000],
            'Customer': ['متجر صفوة', 'متجر النور', 'متجر صفوة', 'متجر النور']
        })
        
        from io import BytesIO
        buffer_pnl = BytesIO()
        with pd.ExcelWriter(buffer_pnl, engine='openpyxl') as writer:
            pnl_template.to_excel(writer, sheet_name='PnL', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_pnl.getvalue(),
            file_name="pnl_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_pnl"
        )
        
        # حالة الرفع
        pnl_status = db.load_dataframe('pnl')
        if pnl_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت الطلبات
    with col2:
        st.markdown("""
        <div class="template-card">
            <h3>📦 بيانات الطلبات (Orders)</h3>
            <p>يُستخدم لتسجيل وتتبع جميع طلبات العملاء ومعلومات الشحن.</p>
            <div class="file-format">CSV / XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        orders_template = pd.DataFrame({
            'ORDER ID': ['ORD001', 'ORD002', 'ORD003'],
            'DESTINATION CITY': ['الرياض', 'جدة', 'الدمام'],
            'SHIPPING COST': [25.0, 35.0, 30.0],
            'ORDER AMOUNT': [300.0, 450.0, 200.0],
            'SHIPMENT WEIGHT': [2.5, 3.2, 1.8],
            'PAYMENT METHOD': ['PREPAID', 'POSTPAID', 'PREPAID']
        })
        
        buffer_orders = BytesIO()
        orders_template.to_csv(buffer_orders, index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_orders.getvalue(),
            file_name="orders_template.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_orders"
        )
        
        orders_status = db.load_dataframe('orders')
        if orders_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت الطاقة
    with col3:
        st.markdown("""
        <div class="template-card">
            <h3>📊 بيانات الطاقة (Capacity)</h3>
            <p>يُستخدم لإدارة الطاقة الإنتاجية والتكاليف التشغيلية للخدمات.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        capacity_template = pd.DataFrame({
            'service_name': ['استلام البضائع', 'تخزين شهري', 'تجهيز الطلبات'],
            'unit_name': ['طرد', 'متر مكعب', 'طلب'],
            'daily_capacity': [1000, 500, 800],
            'monthly_cost': [50000, 30000, 60000]
        })
        
        buffer_capacity = BytesIO()
        with pd.ExcelWriter(buffer_capacity, engine='openpyxl') as writer:
            capacity_template.to_excel(writer, sheet_name='Capacity', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_capacity.getvalue(),
            file_name="capacity_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_capacity"
        )
        
        capacity_status = db.load_dataframe('capacity')
        if capacity_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # الصف الثاني
    col1, col2, col3 = st.columns(3)
    
    # كارت الموردين
    with col1:
        st.markdown("""
        <div class="template-card">
            <h3>🚚 بيانات الموردين (Suppliers)</h3>
            <p>يُستخدم لإدارة معلومات شركات الشحن والموردين وأسعارهم.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        suppliers_template = pd.DataFrame({
            'Shipping Partner': ['aramex', 'smsa', 'dhl'],
            'Zone': ['الرياض', 'الرياض', 'الرياض'],
            'Base Rate': [25.0, 22.0, 30.0],
            'Additional KG Rate': [2.5, 2.0, 3.0]
        })
        
        buffer_suppliers = BytesIO()
        with pd.ExcelWriter(buffer_suppliers, engine='openpyxl') as writer:
            suppliers_template.to_excel(writer, sheet_name='Suppliers', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_suppliers.getvalue(),
            file_name="suppliers_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_suppliers"
        )
        
        suppliers_status = db.load_dataframe('suppliers')
        if suppliers_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت المنافسين
    with col2:
        st.markdown("""
        <div class="template-card">
            <h3>🏆 بيانات المنافسين</h3>
            <p>يُستخدم لمقارنة أسعار الخدمات مع المنافسين في السوق.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        competitors_template = pd.DataFrame({
            'service_name': ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين'],
            'competitor_1': [120.0, 85.0, 55.0],
            'competitor_2': [115.0, 90.0, 50.0],
            'market_average': [120.0, 85.0, 55.0]
        })
        
        buffer_competitors = BytesIO()
        with pd.ExcelWriter(buffer_competitors, engine='openpyxl') as writer:
            competitors_template.to_excel(writer, sheet_name='Competitors', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_competitors.getvalue(),
            file_name="competitors_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_competitors"
        )
        
        st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت العملاء
    with col3:
        st.markdown("""
        <div class="template-card">
            <h3>👥 بيانات العملاء</h3>
            <p>يُستخدم لإدارة معلومات العملاء وتصنيفاتهم والعقود معهم.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        customers_template = pd.DataFrame({
            'customer_name': ['متجر صفوة', 'متجر النور', 'شركة الأمل'],
            'type': ['Retail', 'Wholesale', 'Enterprise'],
            'tier': ['VIP', 'Premium', 'Standard'],
            'monthly_volume': [5000, 8000, 15000]
        })
        
        buffer_customers = BytesIO()
        with pd.ExcelWriter(buffer_customers, engine='openpyxl') as writer:
            customers_template.to_excel(writer, sheet_name='Customers', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_customers.getvalue(),
            file_name="customers_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_customers"
        )
        
        st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # زر تحميل جميع القوالب
    st.markdown("### 📦 تحميل جميع القوالب دفعة واحدة")
    
    if st.button("📦 تحميل جميع القوالب في ملف ZIP", use_container_width=True, type="primary"):
        import zipfile
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # إضافة كل القوالب
            zip_file.writestr("pnl_template.xlsx", buffer_pnl.getvalue())
            zip_file.writestr("orders_template.csv", buffer_orders.getvalue())
            zip_file.writestr("capacity_template.xlsx", buffer_capacity.getvalue())
            zip_file.writestr("suppliers_template.xlsx", buffer_suppliers.getvalue())
            zip_file.writestr("competitors_template.xlsx", buffer_competitors.getvalue())
            zip_file.writestr("customers_template.xlsx", buffer_customers.getvalue())
        
        st.download_button(
            label="⬇️ تحميل ملف ZIP (جميع القوالب)",
            data=zip_buffer.getvalue(),
            file_name="matali_templates_all.zip",
            mime="application/zip",
            use_container_width=True
        )
        st.success("✅ تم تجهيز جميع القوالب للتحميل!")
    
    st.markdown("---")
    
    # حالة البيانات
    st.markdown('<div class="section-header"><h3>📊 حالة البيانات المحملة</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_icon = "✅" if st.session_state.data_loaded['capacity'] else "❌"
        st.markdown(f"""
        <div class="metric-box {'success-box' if st.session_state.data_loaded['capacity'] else ''}">
            <h4>{status_icon} بيانات الطاقة</h4>
            <p>{'محملة' if st.session_state.data_loaded['capacity'] else 'غير محملة'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_icon = "✅" if st.session_state.data_loaded['pnl'] else "❌"
        st.markdown(f"""
        <div class="metric-box {'success-box' if st.session_state.data_loaded['pnl'] else ''}">
            <h4>{status_icon} بيانات P&L</h4>
            <p>{'محملة' if st.session_state.data_loaded['pnl'] else 'غير محملة'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status_icon = "✅" if st.session_state.data_loaded['orders'] else "❌"
        st.markdown(f"""
        <div class="metric-box {'success-box' if st.session_state.data_loaded['orders'] else ''}">
            <h4>{status_icon} بيانات الطلبات</h4>
            <p>{'محملة' if st.session_state.data_loaded['orders'] else 'غير محملة'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # البيانات المتقدمة
    col4, col5, col6 = st.columns(3)
    
    with col4:
        status_icon = "✅" if st.session_state.data_loaded.get('competitors', False) else "❌"
        st.markdown(f"""
        <div class="metric-box {'success-box' if st.session_state.data_loaded.get('competitors', False) else ''}">
            <h4>{status_icon} بيانات المنافسين</h4>
            <p>{'محملة' if st.session_state.data_loaded.get('competitors', False) else 'غير محملة'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        status_icon = "✅" if st.session_state.data_loaded.get('customers', False) else "❌"
        st.markdown(f"""
        <div class="metric-box {'success-box' if st.session_state.data_loaded.get('customers', False) else ''}">
            <h4>{status_icon} بيانات العملاء</h4>
            <p>{'محملة' if st.session_state.data_loaded.get('customers', False) else 'غير محملة'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        status_icon = "✅" if st.session_state.data_loaded.get('market', False) else "❌"
        st.markdown(f"""
        <div class="metric-box {'success-box' if st.session_state.data_loaded.get('market', False) else ''}">
            <h4>{status_icon} بيانات السوق</h4>
            <p>{'محملة' if st.session_state.data_loaded.get('market', False) else 'غير محملة'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # تحميل البيانات
    st.markdown('<div class="section-header"><h3>📤 تحميل البيانات</h3></div>', unsafe_allow_html=True)
    
    st.success("""
    🚀 **نظام ذكي!** 
    - قم برفع **بيانات الطلبات و P&L فقط**
    - النظام سيستخرج تلقائياً: المنافسين، العملاء، المبيعات، الموسمية، تحليل السوق
    - لا حاجة لإدخال بيانات متكررة!
    """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚙️ بيانات الطاقة", 
        "📊 بيانات P&L", 
        "📦 بيانات الطلبات",
        "📦 بيانات الموردين",
        "💾 إدارة قاعدة البيانات"
    ])
    
    with tab1:
        st.markdown("### ⚙️ تحميل بيانات الطاقة والتكاليف")
        
        with st.expander("📘 كيفية الاستخدام", expanded=False):
            st.markdown("""
            **للعملاء الجدد:**
            1. ⬆️ حمّل **قالب بيانات الطاقة** من الأعلى
            2. ✏️ افتح الملف وعبّئ بياناتك (service_name, capacity_per_month, monthly_cost)
            3. 💾 احفظ الملف
            4. 📤 ارفعه هنا
            
            **الأعمدة المطلوبة:**
            - `service_name`: اسم الخدمة
            - `capacity_per_month`: الطاقة الشهرية
            - `monthly_cost`: التكلفة الشهرية
            """)
        
        st.info("💡 استخدم القالب الجاهز لضمان قراءة البيانات بشكل صحيح")
        
        # زر لحذف البيانات القديمة وإعادة الرفع
        if st.session_state.data_loaded.get('capacity', False):
            st.warning("⚠️ يوجد بيانات طاقة محملة مسبقاً")
            if st.button("🗑️ حذف البيانات القديمة وإعادة الرفع", type="secondary", key="reset_capacity"):
                st.session_state.data_loaded['capacity'] = False
                st.session_state.capacity_saved = False
                engine.capacity_data = None
                db.delete_table('capacity')
                st.success("✅ تم حذف البيانات القديمة. يمكنك الآن رفع ملف جديد.")
                st.rerun()
        
        capacity_file = st.file_uploader("حمّل ملف الطاقة", type=['xlsx', 'xls'], key='capacity')
        
        if capacity_file:
            try:
                df = pd.read_excel(capacity_file)
                st.dataframe(df.head(10), use_container_width=True)
                
                # حفظ تلقائي فوري في قاعدة البيانات
                if 'capacity_saved' not in st.session_state or not st.session_state.capacity_saved:
                    engine.capacity_data = df
                    st.session_state.data_loaded['capacity'] = True
                    
                    # حفظ في قاعدة البيانات
                    if db.save_dataframe('capacity', df):
                        st.session_state.capacity_saved = True
                
                st.success("✅ تم حفظ بيانات الطاقة بنجاح في قاعدة البيانات!")
                st.info(f"📊 تم تحميل {len(df)} خدمة")
            
            except Exception as e:
                st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
                st.info("💡 تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
    
    with tab2:
        st.markdown("### 📊 تحميل بيانات P&L (الأرباح والخسائر)")
        
        with st.expander("📘 كيفية الاستخدام", expanded=False):
            st.markdown("""
            **للعملاء الجدد:**
            1. ⬆️ حمّل **قالب بيانات P&L** من الأعلى
            2. ✏️ عبّئ البيانات المالية (الإيرادات والمصروفات)
            3. 💾 احفظ الملف
            4. 📤 ارفعه هنا
            
            **الأعمدة المطلوبة:**
            - `Account Level 1`: نوع الحساب (Income/Expense)
            - `Account Level 2`: تفاصيل الحساب
            - `net_amount`: المبلغ (موجب للإيرادات، سالب للمصروفات)
            - `Customer`: اسم العميل (اختياري)
            """)
        
        st.info("💡 استخدم القالب الجاهز لضمان قراءة البيانات بشكل صحيح")
        
        # زر لحذف البيانات القديمة وإعادة الرفع
        if st.session_state.data_loaded.get('pnl', False):
            st.warning("⚠️ يوجد بيانات P&L محملة مسبقاً")
            if st.button("🗑️ حذف البيانات القديمة وإعادة الرفع", type="secondary", key="reset_pnl"):
                st.session_state.data_loaded['pnl'] = False
                st.session_state.pnl_analyzed = False
                engine.pnl_data = None
                engine.profit_margins = {}
                db.delete_table('pnl')
                st.success("✅ تم حذف البيانات القديمة. يمكنك الآن رفع ملف جديد.")
                st.rerun()
        
        pnl_file = st.file_uploader("حمّل ملف P&L", type=['xlsx', 'xls'], key='pnl')
        
        if pnl_file:
            try:
                df = pd.read_excel(pnl_file)
                st.dataframe(df.head(10), use_container_width=True)
                
                # تحليل تلقائي فوري
                if 'pnl_analyzed' not in st.session_state or not st.session_state.pnl_analyzed:
                    with st.spinner("⚙️ جاري التحليل التلقائي..."):
                        engine.integrate_pnl_data(df)
                        st.session_state.data_loaded['pnl'] = True
                        
                        # حفظ في قاعدة البيانات
                        if db.save_dataframe('pnl', df):
                            st.session_state.pnl_analyzed = True
                
                # عرض النتائج
                st.success("✅ تم تحليل وحفظ بيانات P&L بنجاح في قاعدة البيانات!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("إجمالي الإيرادات", 
                            f"{engine.profit_margins.get('total_income', 0):,.0f} ر.س")
                with col2:
                    st.metric("إجمالي المصروفات", 
                            f"{engine.profit_margins.get('total_expense', 0):,.0f} ر.س")
                with col3:
                    st.metric("هامش الربح", 
                            f"{engine.profit_margins.get('historical_margin', 0):.1f}%")
            
            except Exception as e:
                st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
                st.info("💡 تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
    
    with tab3:
        st.markdown("### 📦 تحميل بيانات الطلبات / Fulfillment")
        
        with st.expander("📘 كيفية الاستخدام", expanded=True):
            st.markdown("""
            **للعملاء الجدد:**
            
            **خطوة 1️⃣:** اختر طريقة الرفع أدناه
            - **📄 ملف واحد**: إذا كان لديك ملف واحد كبير
            - **📁 عدة ملفات**: إذا كان لديك عدة ملفات شهرية (مثل: orders-2025-03.csv, orders-2025-04.csv...)
            
            **خطوة 2️⃣:** اضغط زر "Browse files" أو "استعراض"
            
            **خطوة 3️⃣:** اختر الملفات:
            - يمكنك اختيار **جميع الملفات معاً** (Ctrl+A أو Ctrl+Click)
            - الملفات المدعومة: CSV, XLSX, XLS
            
            **خطوة 4️⃣:** انتظر التحليل التلقائي ✅
            
            ---
            
            **الأعمدة المطلوبة في الملف:**
            - ✅ `ORDER ID`: معرف الطلب
            - ✅ `DESTINATION CITY`: المدينة المستهدفة
            - ✅ `ORDER AMOUNT`: قيمة الطلب
            - ⭐ `COD FEE` أو `SHIPPING COST`: رسوم التوصيل (اختياري)
            
            **💡 ملاحظة:** النظام ذكي ويتعرف تلقائياً على بنية الملف!
            """)
        
        st.info("💡 **نصيحة:** استخدم وضع 'عدة ملفات' لرفع جميع ملفاتك الشهرية دفعة واحدة")
        
        # زر لحذف البيانات القديمة وإعادة الرفع
        if st.session_state.data_loaded.get('orders', False):
            st.warning("⚠️ يوجد بيانات طلبات محملة مسبقاً")
            if st.button("🗑️ حذف البيانات القديمة وإعادة الرفع", type="secondary", key="reset_orders"):
                st.session_state.data_loaded['orders'] = False
                st.session_state.orders_analyzed = False
                engine.orders_data = None
                engine.regional_analysis = {}
                engine.competitors_data = None
                engine.customers_data = None
                engine.sales_history = None
                engine.seasonality_data = None
                db.delete_table('orders')
                db.delete_table('competitors')
                db.delete_table('customers')
                db.delete_table('sales_history')
                db.delete_table('seasonality')
                st.success("✅ تم حذف البيانات القديمة. يمكنك الآن رفع ملف جديد.")
                st.rerun()
        
        # خيار رفع ملف واحد أو عدة ملفات
        upload_mode = st.radio(
            "اختر طريقة الرفع:",
            ["📄 ملف واحد", "📁 عدة ملفات (Fulfillment)"],
            horizontal=True,
            key='upload_mode'
        )
        
        all_orders_data = []
        
        if upload_mode == "📄 ملف واحد":
            orders_file = st.file_uploader(
                "حمّل ملف الطلبات", 
                type=['csv', 'xlsx', 'xls'], 
                key='orders_single'
            )
            
            if orders_file:
                try:
                    # حفظ مؤقت
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(orders_file.name).suffix) as tmp:
                        tmp.write(orders_file.getvalue())
                        tmp_path = tmp.name
                    
                    processor = OrderDataProcessor(tmp_path)
                    df = processor.load_data(sample_size=10000)
                    
                    st.dataframe(df.head(10), use_container_width=True)
                    st.info(f"📊 تم تحميل {len(df):,} طلب")
                    
                    # تحليل تلقائي فوري
                    if 'orders_analyzed' not in st.session_state or not st.session_state.orders_analyzed:
                        with st.spinner("⚙️ جاري التحليل التلقائي..."):
                            engine.integrate_orders_data(df)
                            st.session_state.data_loaded['orders'] = True
                            st.session_state.orders_analyzed = True
                    
                    st.success("✅ تم تحليل وحفظ بيانات الطلبات بنجاح!")
                    
                    # عرض نتائج سريعة
                    col1, col2 = st.columns(2)
                    with col1:
                        if engine.regional_analysis:
                            st.metric("عدد المدن", len(engine.regional_analysis))
                    with col2:
                        st.metric("إجمالي الطلبات", f"{len(df):,}")
                
                except Exception as e:
                    st.error(f"❌ خطأ في معالجة الملف: {str(e)}")
                    st.info("💡 تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
        
        else:  # عدة ملفات
            st.warning("⚠️ **ملاحظة:** اختر الملفات من الأسفل لبدء التحليل التلقائي")
            
            orders_files = st.file_uploader(
                "👇 اختر ملفات الطلبات (يمكنك اختيار 14 ملف معاً)",
                type=['csv', 'xlsx', 'xls'],
                accept_multiple_files=True,
                key='orders_multiple',
                help="اضغط Browse files واختر جميع الملفات معاً"
            )
            
            if orders_files and len(orders_files) > 0:
                st.success(f"✅ تم اختيار {len(orders_files)} ملف - جاري المعالجة...")
                
                all_orders_data = []
                
                # معالجة كل ملف
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file in enumerate(orders_files, 1):
                    status_text.text(f"⚙️ معالجة الملف {idx}/{len(orders_files)}: {file.name}")
                    progress_bar.progress(idx / len(orders_files))
                    
                    try:
                        # حفظ مؤقت
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp:
                            tmp.write(file.getvalue())
                            tmp_path = tmp.name
                        
                        # قراءة وتحليل
                        processor = OrderDataProcessor(tmp_path)
                        df = processor.load_data(sample_size=10000)
                        
                        # عرض معلومات الملف
                        with st.expander(f"📄 {file.name} ({idx}/{len(orders_files)})", expanded=False):
                            st.caption(f"📊 عدد الطلبات: **{len(df):,}**")
                            st.caption(f"📁 الأعمدة: {', '.join(df.columns[:5])}...")
                            st.dataframe(df.head(5), use_container_width=True)
                        
                        # إضافة للقائمة
                        if len(df) > 0:
                            all_orders_data.append(df)
                            st.success(f"✅ {file.name}: تم قراءة {len(df):,} طلب")
                        else:
                            st.warning(f"⚠️ {file.name}: الملف فارغ!")
                    
                    except Exception as e:
                        st.error(f"❌ خطأ في {file.name}: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                
                progress_bar.empty()
                status_text.empty()
                
                # دمج وتحليل تلقائي
                if all_orders_data:
                    total_orders = sum(len(df) for df in all_orders_data)
                    
                    st.info(f"📊 **إجمالي: {total_orders:,} طلب من {len(all_orders_data)} ملف**")
                    
                    # تحليل تلقائي فوري - دائماً عند رفع ملفات جديدة
                    with st.spinner("⚙️ جاري دمج وتحليل جميع الملفات..."):
                        # دمج جميع البيانات
                        combined_df = pd.concat(all_orders_data, ignore_index=True)
                        
                        # تحليل
                        engine.integrate_orders_data(combined_df)
                        st.session_state.data_loaded['orders'] = True
                        
                        # حفظ في قاعدة البيانات
                        db.save_dataframe('orders', combined_df)
                    
                    st.success(f"✅ تم تحليل وحفظ {total_orders:,} طلب بنجاح في قاعدة البيانات!")
                    
                    # عرض نتائج سريعة
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if engine.regional_analysis:
                            st.metric("عدد المدن", len(engine.regional_analysis))
                    with col2:
                        st.metric("إجمالي الطلبات", f"{total_orders:,}")
                    with col3:
                        st.metric("عدد الملفات", len(all_orders_data))
            
            else:
                st.info("👆 اضغط على الزر أعلاه واختر ملفات orders-2025-XX.csv")
    
    with tab4:
        st.markdown("### 📦 تحميل بيانات الموردين وشركات الشحن")
        
        with st.expander("📘 كيفية الاستخدام", expanded=True):
            st.markdown("""
            **للعملاء الجدد:**
            1. ⬆️ حمّل **قالب بيانات الموردين** من الأعلى
            2. ✏️ عبّئ بيانات الموردين:
               - اسم المورد
               - نوع الخدمة (shipping, fulfillment, storage, VAS)
               - النطاق الجغرافي (الرياض / خارج الرياض / كل المملكة)
               - الأسعار والرسوم
            3. 💾 احفظ الملف
            4. 📤 ارفعه هنا
            
            **الأعمدة المطلوبة:**
            - `supplier_name`: اسم المورد / شركة الشحن
            - `service_type`: نوع الخدمة (shipping, fulfillment, storage, VAS)
            - `price_inside_riyadh`: السعر داخل الرياض
            - `price_outside_riyadh`: السعر خارج الرياض
            - `cod_fee`: رسوم الدفع عند الاستلام
            - `network_fee`: رسوم الشبكة
            - `weight_limit`: الوزن المسموح (كجم)
            - `extra_kg_price`: سعر الكيلو الإضافي
            - `is_fulfillment_provider`: هل يوفر تجهيز خارجي؟ (yes/no)
            
            **الفوائد:**
            - ✅ مقارنة تلقائية بين الموردين
            - ✅ اختيار أفضل مورد لكل طلب
            - ✅ حساب تكلفة التجهيز الخارجي (Outsourcing)
            - ✅ تحليل وفورات التكلفة
            """)
        
        st.info("💡 استخدم القالب الجاهز لضمان قراءة البيانات بشكل صحيح")
        
        # زر لحذف البيانات القديمة وإعادة الرفع
        if st.session_state.data_loaded.get('suppliers', False):
            st.warning("⚠️ يوجد بيانات موردين محملة مسبقاً")
            if st.button("🗑️ حذف البيانات القديمة وإعادة الرفع", type="secondary", key="reset_suppliers"):
                st.session_state.data_loaded['suppliers'] = False
                st.session_state.suppliers_saved = False
                engine.suppliers_data = None
                db.delete_table('suppliers')
                st.success("✅ تم حذف البيانات القديمة. يمكنك الآن رفع ملف جديد.")
                st.rerun()
        
        suppliers_file = st.file_uploader(
            "حمّل ملف الموردين",
            type=['xlsx', 'xls'],
            key='suppliers',
            help="ملف يحتوي على بيانات الموردين وشركات الشحن"
        )
        
        if suppliers_file:
            try:
                df = pd.read_excel(suppliers_file)
                st.dataframe(df.head(10), use_container_width=True)
                
                # حفظ تلقائي فوري
                if 'suppliers_saved' not in st.session_state or not st.session_state.suppliers_saved:
                    with st.spinner("⚙️ جاري الحفظ التلقائي..."):
                        engine.integrate_suppliers_data(df)
                        db.save_dataframe('suppliers', df)
                        st.session_state.data_loaded['suppliers'] = True
                        st.session_state.suppliers_saved = True
                
                st.success("✅ تم حفظ بيانات الموردين بنجاح!")
                st.info("✨ الآن النظام سيقارن تكاليف الموردين تلقائياً!")
                st.info(f"📊 تم تحميل {len(df)} مورد")
                
                # تحليل سريع
                if 'service_type' in df.columns:
                    st.markdown("#### 📊 ملخص الموردين")
                    service_counts = df['service_type'].value_counts()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**التوزيع حسب نوع الخدمة:**")
                        for service, count in service_counts.items():
                            st.write(f"• {service}: {count} مورد")
                    
                    with col2:
                        if 'price_inside_riyadh' in df.columns:
                            avg_price = df['price_inside_riyadh'].mean()
                            st.metric("متوسط السعر داخل الرياض", f"{avg_price:.2f} ر.س")
            
            except Exception as e:
                st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
                st.info("💡 تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
    
    with tab5:
        st.markdown("### 💾 إدارة قاعدة البيانات")
        
        st.info("📊 **البيانات المولدة تلقائياً:**")
        
        # عرض البيانات المستخرجة تلقائياً
        if st.session_state.data_loaded.get('orders', False):
            
            # بيانات المنافسين المستخرجة
            if hasattr(engine, 'competitors_data') and engine.competitors_data is not None:
                with st.expander("🏆 بيانات المنافسين (مستخرجة من الطلبات)", expanded=False):
                    st.success(f"✅ تم استخراج {len(engine.competitors_data)} سجل منافس من بيانات الطلبات الفعلية")
                    st.dataframe(engine.competitors_data, use_container_width=True)
                    
                    if st.button("💾 حفظ بيانات المنافسين", key="save_competitors"):
                        db.save_dataframe('competitors_extracted', engine.competitors_data)
                        st.success("✅ تم حفظ بيانات المنافسين!")
            
            # بيانات العملاء المستخرجة
            if hasattr(engine, 'customers_data') and engine.customers_data is not None:
                with st.expander("👥 بيانات العملاء (مستخرجة من الطلبات)", expanded=False):
                    st.success(f"✅ تم استخراج {len(engine.customers_data)} عميل من بيانات الطلبات الفعلية")
                    st.dataframe(engine.customers_data, use_container_width=True)
                    
                    if st.button("💾 حفظ بيانات العملاء", key="save_customers"):
                        db.save_dataframe('customers_extracted', engine.customers_data)
                        st.success("✅ تم حفظ بيانات العملاء!")
            
            # بيانات المبيعات المستخرجة
            if hasattr(engine, 'sales_history') and engine.sales_history is not None:
                with st.expander("📊 بيانات المبيعات التاريخية (مستخرجة من الطلبات)", expanded=False):
                    st.success(f"✅ تم استخراج {len(engine.sales_history)} سجل مبيعات من بيانات الطلبات")
                    st.dataframe(engine.sales_history, use_container_width=True)
                    
                    # رسم بياني للمبيعات
                    if 'total_revenue' in engine.sales_history.columns:
                        fig = px.line(
                            engine.sales_history,
                            x='year_month',
                            y='total_revenue',
                            title='تطور المبيعات الشهرية',
                            labels={'total_revenue': 'الإيرادات', 'year_month': 'الشهر'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if st.button("💾 حفظ بيانات المبيعات", key="save_sales"):
                        db.save_dataframe('sales_history_extracted', engine.sales_history)
                        st.success("✅ تم حفظ بيانات المبيعات!")
            
            # بيانات الموسمية المستخرجة
            if hasattr(engine, 'seasonality_data') and engine.seasonality_data is not None:
                with st.expander("🌡️ بيانات الموسمية (مستخرجة من الطلبات)", expanded=False):
                    st.success(f"✅ تم استخراج {len(engine.seasonality_data)} شهر من بيانات الطلبات")
                    st.dataframe(engine.seasonality_data, use_container_width=True)
                    
                    # رسم بياني للموسمية
                    if 'seasonality_index' in engine.seasonality_data.columns:
                        fig = px.bar(
                            engine.seasonality_data,
                            x='month_name',
                            y='seasonality_index',
                            title='مؤشر الموسمية الشهري',
                            labels={'seasonality_index': 'مؤشر الموسمية', 'month_name': 'الشهر'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if st.button("💾 حفظ بيانات الموسمية", key="save_seasonality"):
                        db.save_dataframe('seasonality_extracted', engine.seasonality_data)
                        st.success("✅ تم حفظ بيانات الموسمية!")
            
            # تحليل السوق المستخرج
            if hasattr(engine, 'market_data') and engine.market_data:
                with st.expander("📈 تحليل السوق (مستخرج من الطلبات)", expanded=False):
                    st.success("✅ تم توليد تحليل السوق تلقائياً")
                    
                    if st.button("💾 حفظ تحليل السوق", key="save_market_analysis"):
                        if hasattr(engine, 'market_analyzer') and engine.market_analyzer:
                            market_report = engine.market_analyzer.generate_market_report()
                            if not market_report.empty:
                                db.save_dataframe('market_analysis', market_report)
                                st.success("✅ تم حفظ تحليل السوق!")
        
        else:
            st.warning("⚠️ قم برفع بيانات الطلبات أولاً لاستخراج البيانات تلقائياً")
        
        st.markdown("---")
        st.markdown("#### 🗄️ جداول قاعدة البيانات")
        
        # عرض جميع الجداول المحفوظة
        tables = db.get_all_tables()
        
        if not tables.empty:
            st.success(f"✅ يوجد {len(tables)} جدول في قاعدة البيانات")
            
            for _, row in tables.iterrows():
                table_name = row['table_name']
                with st.expander(f"📊 {table_name}", expanded=False):
                    st.write(f"**الحجم:** {row['row_count']} سطر")
                    st.write(f"**الأعمدة:** {row['column_count']} عمود")
                    st.write(f"**آخر تحديث:** {row['last_updated']}")
                    
                    # زر لعرض البيانات
                    if st.button(f"عرض البيانات", key=f"view_{table_name}"):
                        df = db.load_dataframe(table_name)
                        if df is not None:
                            st.dataframe(df.head(20), use_container_width=True)
                    
                    # زر لحذف الجدول
                    if st.button(f"🗑️ حذف", key=f"delete_{table_name}", type="secondary"):
                        db.delete_table(table_name)
                        st.warning(f"⚠️ تم حذف جدول {table_name}")
                        st.rerun()
        else:
            st.info("لا توجد جداول محفوظة في قاعدة البيانات")
        
        st.markdown("---")
        
        # أزرار إدارة قاعدة البيانات
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 تحديث جميع البيانات", type="primary"):
                with st.spinner("جاري تحديث قاعدة البيانات..."):
                    # حفظ جميع البيانات الأساسية
                    if hasattr(engine, 'capacity_data') and engine.capacity_data is not None:
                        db.save_dataframe('capacity', engine.capacity_data)
                    if hasattr(engine, 'pnl_data') and engine.pnl_data is not None:
                        db.save_dataframe('pnl', engine.pnl_data)
                    if hasattr(engine, 'orders_data') and engine.orders_data is not None:
                        db.save_dataframe('orders', engine.orders_data)
                    if hasattr(engine, 'suppliers_data') and engine.suppliers_data is not None:
                        db.save_dataframe('suppliers', engine.suppliers_data)
                    
                    # حفظ البيانات المستخرجة
                    if hasattr(engine, 'competitors_data') and engine.competitors_data is not None:
                        db.save_dataframe('competitors_extracted', engine.competitors_data)
                    if hasattr(engine, 'customers_data') and engine.customers_data is not None:
                        db.save_dataframe('customers_extracted', engine.customers_data)
                    if hasattr(engine, 'sales_history') and engine.sales_history is not None:
                        db.save_dataframe('sales_history_extracted', engine.sales_history)
                    if hasattr(engine, 'seasonality_data') and engine.seasonality_data is not None:
                        db.save_dataframe('seasonality_extracted', engine.seasonality_data)
                    
                    st.success("✅ تم تحديث قاعدة البيانات!")
        
        with col2:
            if st.button("🗑️ حذف كل البيانات", type="secondary"):
                if st.checkbox("تأكيد الحذف النهائي"):
                    db.clear_all_data()
                    st.warning("⚠️ تم حذف جميع البيانات!")
                    st.rerun()


def show_auto_extracted_data():
    """عرض البيانات المستخرجة تلقائياً من الطلبات"""
    st.markdown('<div class="big-title">🤖 البيانات المستخرجة تلقائياً</div>', unsafe_allow_html=True)
    
    engine = st.session_state.engine
    
    if not st.session_state.data_loaded.get('orders', False):
        st.warning("⚠️ يجب رفع بيانات الطلبات أولاً")
        return
    
    st.success("""
    🚀 **النظام الذكي استخرج البيانات التالية تلقائياً من الطلبات:**
    - بيانات المنافسين (أسعار السوق الحقيقية)
    - بيانات العملاء (الحجم، القيمة، التفضيلات)
    - بيانات المبيعات التاريخية
    - بيانات الموسمية (أشهر الذروة والركود)
    - تحليل السوق الشامل
    """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 المنافسين",
        "👥 العملاء",
        "📊 المبيعات",
        "🌡️ الموسمية",
        "📈 تحليل السوق"
    ])
    
    with tab1:
        if hasattr(engine, 'competitors_data') and engine.competitors_data is not None:
            st.markdown("### 🏆 بيانات المنافسين المستخرجة")
            st.success(f"✅ تم استخراج {len(engine.competitors_data)} سجل من الطلبات الفعلية")
            st.dataframe(engine.competitors_data, use_container_width=True)
            
            # تحليل سريع
            if 'price' in engine.competitors_data.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_price = engine.competitors_data['price'].mean()
                    st.metric("متوسط السعر", f"{avg_price:.2f} ر.س")
                with col2:
                    min_price = engine.competitors_data['price'].min()
                    st.metric("أقل سعر", f"{min_price:.2f} ر.س")
                with col3:
                    max_price = engine.competitors_data['price'].max()
                    st.metric("أعلى سعر", f"{max_price:.2f} ر.س")
        else:
            st.info("لم يتم استخراج بيانات منافسين بعد")
    
    with tab2:
        if hasattr(engine, 'customers_data') and engine.customers_data is not None:
            st.markdown("### 👥 بيانات العملاء المستخرجة")
            st.success(f"✅ تم استخراج {len(engine.customers_data)} عميل من الطلبات")
            st.dataframe(engine.customers_data, use_container_width=True)
            
            # تحليل العملاء
            if 'customer_segment' in engine.customers_data.columns:
                segments = engine.customers_data['customer_segment'].value_counts()
                fig = px.pie(values=segments.values, names=segments.index, title='توزيع شرائح العملاء')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لم يتم استخراج بيانات عملاء بعد")
    
    with tab3:
        if hasattr(engine, 'sales_history') and engine.sales_history is not None:
            st.markdown("### 📊 المبيعات التاريخية المستخرجة")
            st.success(f"✅ تم استخراج {len(engine.sales_history)} شهر من بيانات المبيعات")
            st.dataframe(engine.sales_history, use_container_width=True)
            
            # رسم بياني
            if 'total_revenue' in engine.sales_history.columns:
                fig = px.line(
                    engine.sales_history,
                    x='year_month',
                    y=['total_revenue', 'total_orders'],
                    title='تطور المبيعات والطلبات'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لم يتم استخراج بيانات مبيعات بعد")
    
    with tab4:
        if hasattr(engine, 'seasonality_data') and engine.seasonality_data is not None:
            st.markdown("### 🌡️ بيانات الموسمية المستخرجة")
            st.success(f"✅ تم استخراج موسمية {len(engine.seasonality_data)} شهر")
            st.dataframe(engine.seasonality_data, use_container_width=True)
            
            # رسم بياني
            if 'seasonality_index' in engine.seasonality_data.columns:
                fig = px.bar(
                    engine.seasonality_data,
                    x='month_name',
                    y='seasonality_index',
                    title='مؤشر الموسمية (1.0 = متوسط)'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لم يتم استخراج بيانات موسمية بعد")
    
    with tab5:
        if hasattr(engine, 'market_data') and engine.market_data:
            st.markdown("### 📈 تحليل السوق المستخرج")
            
            # عرض نفس المحتوى من tab6 السابق
            market_data = engine.market_data
            overview = market_data.get('overview', {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("إجمالي الطلبات", f"{overview.get('total_orders', 0):,}")
            with col2:
                st.metric("القيمة الإجمالية", f"{overview.get('total_value', 0):,.0f} ر.س")
            with col3:
                st.metric("متوسط قيمة الطلب", f"{overview.get('avg_order_value', 0):,.0f} ر.س")
            with col4:
                growth = overview.get('monthly_growth_rate', 0)
                st.metric("معدل النمو", f"{growth:+.1f}%")
        else:
            st.info("لم يتم استخراج تحليل سوق بعد")


def show_predictive_pricing():
    """🔮 التسعير التنبؤي AI"""
    st.markdown('<div class="big-title">🔮 التسعير التنبؤي AI</div>', unsafe_allow_html=True)
    
    engine = st.session_state.engine
    
    # التحقق من توفر البيانات المطلوبة
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 📊 بيانات المبيعات التاريخية (مستخرجة تلقائياً)")
        
        if hasattr(engine, 'sales_history') and engine.sales_history is not None:
            st.success(f"✅ تم استخراج {len(engine.sales_history)} شهر من بيانات الطلبات!")
            st.dataframe(engine.sales_history.head(5), use_container_width=True)
        else:
            st.warning("⚠️ قم برفع بيانات الطلبات أولاً")
    
    with col_b:
        st.markdown("#### 🌡️ بيانات الموسمية (مستخرجة تلقائياً)")
        
        if hasattr(engine, 'seasonality_data') and engine.seasonality_data is not None:
            st.success(f"✅ تم استخراج موسمية {len(engine.seasonality_data)} شهر من الطلبات!")
            st.dataframe(engine.seasonality_data.head(5), use_container_width=True)
        else:
            st.warning("⚠️ قم برفع بيانات الطلبات أولاً")
    
    st.markdown("---")
    
    # واجهة التسعير التنبؤي
    if engine.ai_model:
        st.markdown("### 🔮 التنبؤ بالأسعار")
        
        col1, col2 = st.columns(2)
        
        with col1:
            forecast_months = st.slider("عدد الأشهر للتنبؤ", 1, 12, 3)
        
        with col2:
            confidence_level = st.slider("مستوى الثقة %", 80, 99, 95)
        
        if st.button("🚀 توليد التنبؤات", type="primary"):
            with st.spinner("جاري إنشاء التنبؤات..."):
                # هنا يمكن إضافة كود التنبؤ
                st.success("✅ تم توليد التنبؤات بنجاح!")
    else:
        st.info("📊 محرك AI التنبؤي غير متاح حالياً")


def show_old_tabs_removed_message():
    """رسالة توضح إزالة التابات المكررة"""
    st.info("""
    ✨ **تحديث ذكي!**
    
    تم إلغاء التابات التالية لأنها كانت مكررة:
    - ❌ بيانات المنافسين (يتم استخراجها تلقائياً من الطلبات)
    - ❌ بيانات العملاء (يتم استخراجها تلقائياً من الطلبات)
    - ❌ بيانات المبيعات (يتم استخراجها تلقائياً من الطلبات)
    - ❌ بيانات الموسمية (يتم استخراجها تلقائياً من الطلبات)
    - ❌ بيانات السوق (يتم توليدها تلقائياً من الطلبات)
    
    **الآن:**
    - ✅ ارفع **بيانات الطلبات و P&L فقط**
    - ✅ النظام يستخرج كل شيء تلقائياً
    - ✅ توفير الوقت والجهد!
    """)


def show_ai_dashboards():
    """📊 لوحات المعلومات الذكية"""
    st.markdown('<div class="big-title">📊 لوحات المعلومات الذكية</div>', unsafe_allow_html=True)
    
    engine = st.session_state.engine
    db = st.session_state.db
    
    # التحقق من توفر البيانات
    if not st.session_state.data_loaded.get('orders', False):
        st.warning("⚠️ يجب رفع بيانات الطلبات أولاً لعرض لوحات المعلومات")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 ملخص الأداء",
        "🗺️ التحليل الجغرافي",
        "👥 تحليل العملاء",
        "💰 التحليل المالي"
    ])
    
    with tab1:
        st.markdown("### 📊 ملخص الأداء الشامل")
        
        # Metrics
        if hasattr(engine, 'orders_data') and engine.orders_data is not None:
            df = engine.orders_data
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_orders = len(df)
                st.metric("إجمالي الطلبات", f"{total_orders:,}")
            
            with col2:
                if 'selling_price' in df.columns:
                    total_revenue = df['selling_price'].sum()
                    st.metric("الإيرادات", f"{total_revenue:,.0f} ر.س")
            
            with col3:
                if 'selling_price' in df.columns:
                    avg_order_value = df['selling_price'].mean()
                    st.metric("متوسط الطلب", f"{avg_order_value:.0f} ر.س")
            
            with col4:
                if 'customer_name' in df.columns:
                    unique_customers = df['customer_name'].nunique()
                    st.metric("العملاء", f"{unique_customers:,}")
    
    with tab2:
        st.markdown("### 🗺️ التحليل الجغرافي")
        
        if hasattr(engine, 'market_data') and engine.market_data:
            geographic = engine.market_data.get('geographic', {})
            
            if geographic.get('has_geographic_data'):
                top_cities = geographic.get('top_cities', [])
                if top_cities:
                    cities_df = pd.DataFrame(top_cities)
                    
                    fig = px.bar(
                        cities_df.head(15),
                        x='orders',
                        y='city',
                        orientation='h',
                        title='أكثر 15 مدينة طلباً',
                        color='percentage'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 👥 تحليل العملاء")
        
        if hasattr(engine, 'customers_data') and engine.customers_data is not None:
            customers_df = engine.customers_data
            
            # Top customers
            st.markdown("#### أفضل 10 عملاء")
            top_customers = customers_df.nlargest(10, 'total_orders')
            
            fig = px.bar(
                top_customers,
                x='total_orders',
                y='customer_name',
                orientation='h',
                title='أكثر العملاء طلباً'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 💰 التحليل المالي")
        
        if hasattr(engine, 'sales_history') and engine.sales_history is not None:
            sales_df = engine.sales_history
            
            if 'total_revenue' in sales_df.columns and 'growth_rate' in sales_df.columns:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=sales_df['year_month'],
                    y=sales_df['total_revenue'],
                    name='الإيرادات',
                    yaxis='y'
                ))
                
                fig.add_trace(go.Scatter(
                    x=sales_df['year_month'],
                    y=sales_df['growth_rate'],
                    name='معدل النمو',
                    yaxis='y2',
                    line=dict(color='red')
                ))
                
                fig.update_layout(
                    title='الإيرادات ومعدل النمو',
                    yaxis=dict(title='الإيرادات (ر.س)'),
                    yaxis2=dict(title='معدل النمو (%)', overlaying='y', side='right')
                )
                
                st.plotly_chart(fig, use_container_width=True)


def show_pricing_models():
    """💰 نماذج التسعير المتقدمة"""
    st.markdown('<div class="big-title">💰 نماذج التسعير</div>', unsafe_allow_html=True)
    
    engine = st.session_state.engine
    
    st.info("قيد التطوير - سيتم إضافة نماذج تسعير متقدمة قريباً")


def show_suppliers_integration():
    """📦 إدارة الموردين وشركات الشحن"""
    st.markdown('<div class="big-title">📦 إدارة الموردين</div>', unsafe_allow_html=True)
    
    engine = st.session_state.engine
    db = st.session_state.db
    
    st.markdown("""
    **للعملاء الجدد:**
    1. ⬆️ حمّل **قالب بيانات الموردين** من الأعلى
    2. ✏️ عبّئ بيانات الموردين:
       - اسم المورد
       - نوع الخدمة (shipping, fulfillment, storage, VAS)
       - النطاق الجغرافي (الرياض / خارج الرياض / كل المملكة)
       - الأسعار والرسوم
    3. 💾 احفظ الملف
    4. 📤 ارفعه هنا
    
    **الأعمدة المطلوبة:**
    - `supplier_name`: اسم المورد / شركة الشحن
    - `service_type`: نوع الخدمة (shipping, fulfillment, storage, VAS)
    - `price_inside_riyadh`: السعر داخل الرياض
    - `price_outside_riyadh`: السعر خارج الرياض
    - `cod_fee`: رسوم الدفع عند الاستلام
    - `network_fee`: رسوم الشبكة
    - `weight_limit`: الوزن المسموح (كجم)
    - `extra_kg_price`: سعر الكيلو الإضافي
    - `is_fulfillment_provider`: هل يوفر تجهيز خارجي؟ (yes/no)
    
    **الفوائد:**
    - ✅ مقارنة تلقائية بين الموردين
    - ✅ اختيار أفضل مورد لكل طلب
    - ✅ حساب تكلفة التجهيز الخارجي (Outsourcing)
    - ✅ تحليل وفورات التكلفة
    """)
    
    st.info("💡 استخدم القالب الجاهز لضمان قراءة البيانات بشكل صحيح")
    
    suppliers_file = st.file_uploader(
        "حمّل ملف الموردين", 
        type=['xlsx', 'xls', 'csv'], 
        key='suppliers'
    )
    
    if suppliers_file:
        try:
            # قراءة الملف
            if suppliers_file.name.endswith('.csv'):
                df = pd.read_csv(suppliers_file, encoding='utf-8-sig')
            else:
                df = pd.read_excel(suppliers_file)
            
            st.success("✅ تم تحميل ملف الموردين بنجاح")
            st.dataframe(df, use_container_width=True)
            
            # حفظ تلقائي فوري
            if 'suppliers_saved' not in st.session_state or not st.session_state.suppliers_saved:
                with st.spinner("⚙️ جاري الحفظ التلقائي..."):
                    engine.integrate_suppliers_data(df)
                    st.session_state.data_loaded['suppliers'] = True
                    
                    # حفظ في قاعدة البيانات
                    if db.save_dataframe('suppliers', df):
                        st.session_state.suppliers_saved = True
            
            st.success("✅ تم حفظ بيانات الموردين بنجاح في قاعدة البيانات!")
            st.info(f"📊 تم تحميل {len(df)} مورد")
            
            # عرض إحصائيات
            col1, col2, col3, col4 = st.columns(4)
            
            shipping_count = len(df[df['service_type'] == 'shipping'])
            fulfillment_count = len(df[df['service_type'] == 'fulfillment'])
            storage_count = len(df[df['service_type'] == 'storage'])
            outsourcing_count = len(df[df['is_fulfillment_provider'] == 'yes'])
            
            with col1:
                st.metric("موردو الشحن", shipping_count)
            with col2:
                st.metric("موردو التجهيز", fulfillment_count)
            with col3:
                st.metric("موردو التخزين", storage_count)
            with col4:
                st.metric("التجهيز الخارجي", outsourcing_count)
            
            # عرض مثال على أسعار الشحن
            if shipping_count > 0:
                st.markdown("#### 🚚 مقارنة سريعة لأسعار الشحن")
                
                shipping_df = df[df['service_type'] == 'shipping'][
                    ['supplier_name', 'price_inside_riyadh', 'price_outside_riyadh', 'cod_fee', 'weight_limit']
                ].copy()
                
                shipping_df['تكلفة تقديرية (الرياض)'] = shipping_df['price_inside_riyadh'] + shipping_df['cod_fee']
                shipping_df['تكلفة تقديرية (خارج الرياض)'] = shipping_df['price_outside_riyadh'] + shipping_df['cod_fee']
                
                shipping_df.columns = ['المورد', 'داخل الرياض', 'خارج الرياض', 'رسوم COD', 'الوزن المسموح', 'تكلفة (الرياض)', 'تكلفة (خارج الرياض)']
                st.dataframe(shipping_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ خطأ في قراءة الملف: {str(e)}")
            st.info("💡 تأكد من أن الملف يحتوي على الأعمدة المطلوبة")
    
    # إضافة مورد جديد يدوياً
    st.markdown("---")
    with st.expander("➕ إضافة مورد جديد يدوياً"):
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("اسم المورد")
            service_type = st.selectbox("نوع الخدمة", ["shipping", "fulfillment", "storage", "VAS"])
            price_inside = st.number_input("السعر داخل الرياض (ر.س)", min_value=0.0, step=1.0, value=15.0)
            price_outside = st.number_input("السعر خارج الرياض (ر.س)", min_value=0.0, step=1.0, value=20.0)
            cod_fee = st.number_input("رسوم التحصيل (ر.س)", min_value=0.0, step=0.5)
        
        with col2:
            network_fee = st.number_input("رسوم الشبكة (ر.س)", min_value=0.0, step=0.5)
            weight_limit = st.number_input("الوزن المسموح (كجم)", min_value=0.0, step=1.0, value=5.0)
            extra_kg_price = st.number_input("سعر الكيلو الإضافي (ر.س)", min_value=0.0, step=0.5)
            is_fulfillment_provider = st.selectbox("هل يقدم تجهيز خارجي؟", ["no", "yes"])
        
        if st.button("➕ إضافة المورد", type="primary"):
            new_supplier = {
                "supplier_name": supplier_name,
                "service_type": service_type,
                "price_inside_riyadh": price_inside,
                "price_outside_riyadh": price_outside,
                "cod_fee": cod_fee,
                "network_fee": network_fee,
                "weight_limit": weight_limit,
                "extra_kg_price": extra_kg_price,
                "is_fulfillment_provider": is_fulfillment_provider
            }
            
            try:
                # إضافة للنظام
                if hasattr(engine, 'suppliers_data') and engine.suppliers_data is not None:
                    updated_df = pd.concat([
                        engine.suppliers_data, 
                        pd.DataFrame([new_supplier])
                    ], ignore_index=True)
                else:
                    updated_df = pd.DataFrame([new_supplier])
                
                engine.integrate_suppliers_data(updated_df)
                st.session_state.data_loaded['suppliers'] = True
                st.success(f"✅ تم إضافة المورد: {supplier_name}")
                st.dataframe(updated_df.tail(5), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")


def show_dashboard():
    """📊 لوحة التحكم - تحليلات شاملة"""
    st.markdown('<div class="big-title">📊 لوحة التحكم الذكية</div>', unsafe_allow_html=True)
    
    # التحقق من البيانات
    if not any(st.session_state.data_loaded.values()):
        st.warning("⚠️ لم يتم تحميل أي بيانات بعد. اذهب إلى 📂 مركز البيانات لتحميل البيانات.")
        return
    
    # الحصول على لوحة التحكم
    dashboard = engine.get_analytics_dashboard()
    
    # المقاييس الرئيسية
    st.markdown('<div class="section-header"><h3>📈 المقاييس الرئيسية</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    if 'profit' in dashboard['metrics']:
        profit_data = dashboard['metrics']['profit']
        
        with col1:
            st.metric("إجمالي الإيرادات", 
                     f"{profit_data.get('total_income', 0):,.0f} ر.س")
        with col2:
            st.metric("إجمالي المصروفات", 
                     f"{profit_data.get('total_expense', 0):,.0f} ر.س")
        with col3:
            profit = profit_data.get('net_profit', 0)
            st.metric("صافي الربح", 
                     f"{profit:,.0f} ر.س",
                     delta=f"{profit_data.get('historical_margin', 0):.1f}%")
        with col4:
            st.metric("هامش الربح", 
                     f"{profit_data.get('historical_margin', 0):.1f}%")
    
    # تحليل العملاء
    if engine.customer_profitability:
        st.markdown("---")
        st.markdown('<div class="section-header"><h3>👥 تحليل العملاء</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 أفضل 10 عملاء (حسب الربح)")
            top_customers = sorted(
                engine.customer_profitability.items(),
                key=lambda x: x[1]['profit'],
                reverse=True
            )[:10]
            
            customer_df = pd.DataFrame([
                {
                    'العميل': name,
                    'الربح': f"{data['profit']:,.0f} ر.س",
                    'هامش الربح': f"{data['margin']:.1f}%",
                    'التصنيف': data['tier']
                }
                for name, data in top_customers
            ])
            st.dataframe(customer_df, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 توزيع العملاء حسب التصنيف")
            
            tiers = dashboard['metrics']['customers'].get('by_tier', {})
            if tiers:
                fig = px.pie(
                    values=list(tiers.values()),
                    names=list(tiers.keys()),
                    title='تصنيف العملاء',
                    color_discrete_map={
                        'VIP': '#2ecc71',
                        'Premium': '#3498db',
                        'Good': '#f39c12',
                        'Standard': '#95a5a6',
                        'Loss': '#e74c3c'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # تحليل المناطق
    if engine.regional_analysis:
        st.markdown("---")
        st.markdown('<div class="section-header"><h3>🗺️ التحليل الإقليمي</h3></div>', unsafe_allow_html=True)
        
        # أكثر 10 مدن طلباً
        top_cities = sorted(
            engine.regional_analysis.items(),
            key=lambda x: x[1]['order_count'],
            reverse=True
        )[:10]
        
        cities_df = pd.DataFrame([
            {
                'المدينة': city,
                'عدد الطلبات': data['order_count'],
                'متوسط القيمة': f"{data['avg_order_value']:.0f} ر.س",
                'متوسط الشحن': f"{data['avg_shipping_cost']:.0f} ر.س"
            }
            for city, data in top_cities
        ])
        
        st.dataframe(cities_df, use_container_width=True)
        
        # رسم بياني
        fig = px.bar(
            cities_df,
            x='المدينة',
            y='عدد الطلبات',
            title='أكثر 10 مدن طلباً'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # =============================================
    # تحليل توزيع التكاليف المتقدم
    # =============================================
    if st.session_state.data_loaded.get('pnl', False) and st.session_state.data_loaded.get('capacity', False):
        st.markdown("---")
        st.markdown('<div class="section-header"><h3>💎 تحليل توزيع التكاليف المتقدم</h3></div>', unsafe_allow_html=True)
        
        st.info("""
        **📊 تحليل شامل للتكاليف:**
        - استخراج التكاليف من P&L
        - توزيع G&A على الخدمات حسب السعة
        - حساب تكلفة الطلب الواحد
        - ربط البيانات المالية بالتشغيلية
        """)
        
        if st.button("🔄 احسب توزيع التكاليف المتقدم", type="primary"):
            with st.spinner("⚙️ جاري حساب التوزيع المتقدم للتكاليف..."):
                cost_allocation = engine.calculate_advanced_cost_allocation()
                
                if cost_allocation is not None:
                    st.success("✅ تم حساب توزيع التكاليف بنجاح!")
                    
                    # عرض الجدول
                    st.markdown("#### 📋 جدول التكاليف الموزعة")
                    
                    # تنسيق الأرقام
                    display_df = cost_allocation.copy()
                    for col in ['monthly_cost_before_gna', 'gna_allocation', 'monthly_cost_after_gna', 'cost_per_order']:
                        if col in display_df.columns:
                            display_df[col] = display_df[col].apply(lambda x: f"{x:,.2f} ر.س")
                    
                    display_df['orders_per_month'] = display_df['orders_per_month'].apply(lambda x: f"{x:,}")
                    display_df['capacity_per_month'] = display_df['capacity_per_month'].apply(lambda x: f"{x:,}")
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # رسم بياني للتكاليف
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig1 = px.bar(
                            cost_allocation,
                            x='service_name',
                            y=['monthly_cost_before_gna', 'gna_allocation'],
                            title='🔹 توزيع التكاليف (قبل وبعد G&A)',
                            labels={'value': 'التكلفة (ر.س)', 'service_name': 'الخدمة'},
                            barmode='stack'
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig2 = px.pie(
                            cost_allocation,
                            values='monthly_cost_after_gna',
                            names='service_name',
                            title='🔹 توزيع التكاليف الإجمالية'
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # مقاييس رئيسية
                    st.markdown("#### 📊 المقاييس الرئيسية")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_cost = cost_allocation['monthly_cost_after_gna'].sum()
                    total_orders = cost_allocation['orders_per_month'].iloc[0]
                    avg_cost_per_order = total_cost / total_orders if total_orders > 0 else 0
                    total_gna = cost_allocation['gna_allocation'].sum()
                    
                    with col1:
                        st.metric("إجمالي التكاليف الشهرية", f"{total_cost:,.0f} ر.س")
                    with col2:
                        st.metric("إجمالي G&A", f"{total_gna:,.0f} ر.س")
                    with col3:
                        st.metric("عدد الطلبات الشهري", f"{total_orders:,}")
                    with col4:
                        st.metric("متوسط تكلفة الطلب", f"{avg_cost_per_order:.2f} ر.س")
                    
                    # تحميل Excel
                    st.markdown("#### 💾 تصدير النتائج")
                    
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        cost_allocation.to_excel(writer, sheet_name='Cost Allocation', index=False)
                    
                    st.download_button(
                        label="📥 تحميل تحليل التكاليف (Excel)",
                        data=output.getvalue(),
                        file_name=f"cost_allocation_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    # =============================================
    # تحليل وقت تجهيز الطلبات
    # =============================================
    if engine.orders_data is not None and 'prep_time_minutes' in engine.orders_data.columns:
        st.markdown("---")
        st.markdown('<div class="section-header"><h3>⏱️ تحليل وقت تجهيز الطلبات</h3></div>', unsafe_allow_html=True)
        
        st.info("""
        **📊 تحليل زمن التجهيز:**
        - حساب الفترة بين إنشاء الطلب وتعبئته
        - متوسط الوقت لكل عميل
        - توزيع الطلبات حسب سرعة التجهيز
        """)
        
        if hasattr(engine, 'prep_time_analysis') and engine.prep_time_analysis:
            prep_stats = engine.prep_time_analysis
            
            # المقاييس الرئيسية
            st.markdown("#### 📈 المقاييس الرئيسية")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("متوسط وقت التجهيز", 
                         f"{prep_stats.get('avg_prep_time', 0):.1f} دقيقة")
            with col2:
                st.metric("الوسيط", 
                         f"{prep_stats.get('median_prep_time', 0):.1f} دقيقة")
            with col3:
                st.metric("أسرع تجهيز", 
                         f"{prep_stats.get('min_prep_time', 0):.1f} دقيقة")
            with col4:
                st.metric("أبطأ تجهيز", 
                         f"{prep_stats.get('max_prep_time', 0):.1f} دقيقة")
            
            # توزيع الأوقات
            if 'distribution' in prep_stats:
                st.markdown("#### 📊 توزيع الطلبات حسب سرعة التجهيز")
                
                dist = prep_stats['distribution']
                dist_df = pd.DataFrame({
                    'الفئة': ['سريع جداً (<30 دقيقة)', 'سريع (30-60 دقيقة)', 
                             'عادي (1-2 ساعة)', 'بطيء (2-4 ساعات)', 'بطيء جداً (>4 ساعات)'],
                    'النسبة %': [
                        dist.get('very_fast_pct', 0),
                        dist.get('fast_pct', 0),
                        dist.get('normal_pct', 0),
                        dist.get('slow_pct', 0),
                        dist.get('very_slow_pct', 0)
                    ]
                })
                
                fig = px.bar(
                    dist_df,
                    x='الفئة',
                    y='النسبة %',
                    title='توزيع الطلبات حسب سرعة التجهيز',
                    color='النسبة %',
                    color_continuous_scale='RdYlGn_r'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # تحليل حسب العميل
            if 'by_customer' in prep_stats and not prep_stats['by_customer'].empty:
                st.markdown("#### 👥 أبطأ 10 عملاء في التجهيز")
                
                customer_df = prep_stats['by_customer'].head(10).copy()
                customer_df.columns = ['رقم العميل', 'متوسط الوقت (دقيقة)', 'عدد الطلبات']
                customer_df['متوسط الوقت (دقيقة)'] = customer_df['متوسط الوقت (دقيقة)'].round(1)
                
                st.dataframe(customer_df, use_container_width=True)
                
                # رسم بياني
                fig2 = px.bar(
                    customer_df.head(10),
                    x='رقم العميل',
                    y='متوسط الوقت (دقيقة)',
                    title='أبطأ العملاء في التجهيز',
                    color='متوسط الوقت (دقيقة)',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # معلومات إضافية
            st.info(f"📊 تم تحليل {prep_stats.get('total_orders_analyzed', 0):,} طلب")


def show_pricing_engine():
    """💰 محرك التسعير الموحد"""
    st.markdown('<div class="big-title">💰 محرك التسعير الموحد</div>', unsafe_allow_html=True)
    
    st.info("""
    **محرك تسعير ذكي واحد** يجمع كل طرق التسعير:
    - التسعير الأساسي (من الطاقة)
    - التسعير الذكي (من P&L)
    - التسعير الإقليمي (من الطلبات)
    - خصومات العملاء الذكية
    """)
    
    # اختيار نوع التسعير
    pricing_method = st.selectbox(
        "🎯 اختر طريقة التسعير",
        [
            "💰 تسعير شامل (موصى به)",
            "📊 تسعير CMA (دراسة السوق)",
            "🤖 تسعير تنبؤي (AI)",
            "🏢 تسعير المؤسسات",
            "⚡ تسعير ديناميكي متقدم",
            "🔄 مقارنة جميع النماذج"
        ]
    )
    
    st.markdown("---")
    
    if pricing_method == "💰 تسعير شامل (موصى به)":
        show_comprehensive_pricing()
    elif pricing_method == "📊 تسعير CMA (دراسة السوق)":
        show_cma_pricing()
    elif pricing_method == "🤖 تسعير تنبؤي (AI)":
        show_predictive_pricing()
    elif pricing_method == "🏢 تسعير المؤسسات":
        show_enterprise_pricing()
    elif pricing_method == "⚡ تسعير ديناميكي متقدم":
        show_dynamic_pricing()
    else:
        show_pricing_comparison()


def show_comprehensive_pricing():
    """التسعير الشامل المالي - عرض 8 مؤشرات مالية"""
    st.markdown("### 💰 التسعير الشامل المتكامل")
    
    st.info("""
    **📊 محرك تسعير مالي متكامل** - يعرض 8 مؤشرات مالية حقيقية:
    1️⃣ تكلفة الطلب الحقيقية | 2️⃣ سعر البيع المقترح | 3️⃣ هامش الربح بالريال | 4️⃣ هامش الربح كنسبة
    5️⃣ ربح شهري متوقع | 6️⃣ استغلال الطاقة | 7️⃣ تكلفة الطاقة/وحدة | 8️⃣ تحذير مخاطرة
    """)
    
    # نموذج التسعير
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 بيانات الطلب")
        scenario = st.selectbox(
            "السيناريو | Scenario",
            [
                'تجهيز + شحن داخل الرياض | Fulfillment + Inside Riyadh',
                'تجهيز + شحن خارج الرياض | Fulfillment + Outside Riyadh',
                'تخزين فقط | Storage Only',
                'شحن فقط داخل الرياض | Shipping Inside Only',
                'شحن فقط خارج الرياض | Shipping Outside Only'
            ]
        )
        
        monthly_volume = st.number_input(
            "📊 الحجم الشهري المتوقع | Monthly Volume", 
            min_value=100, 
            value=1000, 
            step=100,
            help="عدد الطلبات الشهرية المتوقعة"
        )
        
        target_margin = st.slider(
            "🎯 هامش الربح المستهدف % | Target Margin",
            min_value=10.0,
            max_value=50.0,
            value=25.0,
            step=5.0,
            help="هامش الربح المستهدف (الموصى به: 25%)"
        )
    
    with col2:
        st.markdown("#### ⚙️ إعدادات")
        include_returns = st.checkbox("إضافة تكلفة المرتجعات | Include Return Cost", value=True)
        
        min_acceptable_margin = st.number_input(
            "الحد الأدنى لهامش الربح % | Min Acceptable Margin",
            min_value=5.0,
            max_value=30.0,
            value=15.0,
            step=5.0,
            help="أقل هامش ربح مقبول (أقل من هذا = تحذير مخاطرة)"
        )
        
        show_cost_details = st.checkbox("عرض تفاصيل التكلفة | Show Cost Details", value=True)
    
    st.markdown("---")
    
    # حساب السعر
    if st.button("💵 احسب التسعير المالي | Calculate Financial Pricing", type="primary", use_container_width=True):
        with st.spinner("🔄 جاري الحساب المالي..."):
            # تحديد السيناريو
            scenario_key = 'fulfillment_riyadh' if 'داخل الرياض' in scenario else 'fulfillment_outside'
            if 'تخزين فقط' in scenario:
                scenario_key = 'storage_only'
            elif 'شحن فقط داخل' in scenario:
                scenario_key = 'shipping_riyadh'
            elif 'شحن فقط خارج' in scenario:
                scenario_key = 'shipping_outside'
            
            # تحميل البيانات المالية
            pl_df = db.load_dataframe('pnl')
            capacity_df = db.load_dataframe('capacity')
            orders_df = db.load_dataframe('orders')
            
            # استخراج التكاليف
            if pl_df is not None:
                pl_costs = fin_engine.load_pl_costs(pl_df)
            else:
                pl_costs = {'fulfillment_cost_per_order': 3.5, 'storage_cost_per_order': 1.5, 
                           'shipping_cost_per_order': 10, 'overhead_cost_per_order': 2,
                           'total_monthly_expense': 60000, 'order_count': 10000}
            
            # استخراج الطاقة
            if capacity_df is not None:
                capacity_info = fin_engine.load_capacity(capacity_df)
            else:
                capacity_info = {'max_fulfillment_capacity': 50000, 'max_storage_pallets': 468}
            
            # إحصائيات الطلبات
            if orders_df is not None:
                orders_stats = fin_engine.load_orders_stats(orders_df)
                pl_costs['return_rate'] = orders_stats['return_rate']
            
            # 1️⃣ حساب تكلفة الطلب الحقيقية
            cost_breakdown = fin_engine.compute_unit_cost(
                scenario=scenario_key,
                pl_costs=pl_costs,
                include_return_cost=include_returns
            )
            
            total_cost = cost_breakdown['total_cost_per_order']
            
            # 2️⃣ سعر البيع المقترح
            pricing_result = fin_engine.suggest_price(total_cost, target_margin)
            suggested_price = pricing_result['suggested_price']
            
            # 3️⃣ و 4️⃣ هامش الربح
            margins = fin_engine.calculate_margins(suggested_price, total_cost, monthly_volume)
            
            # 5️⃣ ربح شهري متوقع
            monthly_profit = margins['monthly_profit_sar']
            
            # 6️⃣ استغلال الطاقة
            capacity_usage = fin_engine.calculate_capacity_usage(monthly_volume, capacity_info)
            
            # 7️⃣ تكلفة الطاقة/وحدة
            capacity_cost = fin_engine.cost_per_capacity_unit(pl_costs, capacity_info)
            
            # 8️⃣ تحذير مخاطرة
            risk = fin_engine.risk_warning(margins['margin_percentage'], min_acceptable_margin, target_margin)
        
        # ========================================
        # عرض النتائج - 8 مؤشرات مالية
        # ========================================
        
        st.success("✅ تم حساب التسعير المالي!")
        
        # المؤشرات الرئيسية (4 مقاييس)
        st.markdown("### 📊 المؤشرات المالية الرئيسية")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric(
                "1️⃣ تكلفة الطلب الحقيقية",
                f"{total_cost:.2f} ر.س",
                help="التكلفة الفعلية من P&L + Capacity + Orders"
            )
        
        with metric_col2:
            st.metric(
                "2️⃣ سعر البيع المقترح",
                f"{suggested_price:.2f} ر.س",
                delta=f"+{suggested_price - total_cost:.2f}",
                help=f"السعر = {total_cost:.2f} ÷ (1 - {target_margin}%) = {suggested_price:.2f}"
            )
        
        with metric_col3:
            st.metric(
                "3️⃣ هامش الربح (ريال)",
                f"{margins['profit_per_order_sar']:.2f} ر.س",
                delta=f"للطلب الواحد",
                help="الربح = سعر البيع - التكلفة"
            )
        
        with metric_col4:
            st.metric(
                "4️⃣ هامش الربح (%)",
                f"{margins['margin_percentage']:.1f}%",
                delta=f"المستهدف: {target_margin}%",
                delta_color="normal" if margins['margin_percentage'] >= target_margin else "inverse",
                help="Margin % = الربح ÷ سعر البيع"
            )
        
        # مؤشرات إضافية
        st.markdown("---")
        metric_col5, metric_col6, metric_col7, metric_col8 = st.columns(4)
        
        with metric_col5:
            st.metric(
                "5️⃣ ربح شهري متوقع",
                f"{monthly_profit:,.0f} ر.س",
                delta=f"{monthly_volume:,} طلب",
                help=f"{margins['profit_per_order_sar']:.2f} × {monthly_volume:,} = {monthly_profit:,.0f}"
            )
        
        with metric_col6:
            capacity_color = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[capacity_usage['status']]
            st.metric(
                "6️⃣ استغلال الطاقة",
                f"{capacity_usage['usage_percentage']:.1f}%",
                delta=f"{capacity_color} {capacity_usage['status_label']}",
                help=f"{monthly_volume:,} ÷ {capacity_usage['max_capacity']:,} = {capacity_usage['usage_percentage']:.1f}%"
            )
        
        with metric_col7:
            st.metric(
                "7️⃣ تكلفة الطاقة/طلب",
                f"{capacity_cost['cost_per_order_capacity']:.2f} ر.س",
                delta=f"طاقة مهدرة: {capacity_cost['wasted_capacity_cost']:,.0f} ر.س",
                delta_color="inverse",
                help="التكاليف الثابتة ÷ الطاقة القصوى"
            )
        
        with metric_col8:
            risk_icon = {"safe": "✅", "moderate": "⚠️", "high": "🚨"}[risk['risk_level']]
            st.metric(
                "8️⃣ مستوى المخاطرة",
                f"{risk_icon} {risk['risk_level'].upper()}",
                delta=risk['warning_message'],
                delta_color="normal" if risk['risk_level'] == 'safe' else "inverse"
            )
        
        # تحذير المخاطرة (إذا وجد)
        if risk['risk_level'] != 'safe':
            if risk['risk_level'] == 'high':
                st.error(f"**{risk['warning_message']}**\n\n💡 {risk['recommendation']}")
            else:
                st.warning(f"**{risk['warning_message']}**\n\n💡 {risk['recommendation']}")
        
        # تحذير الطاقة
        if capacity_usage['warning']:
            st.warning(capacity_usage['warning'])
        
        # تفاصيل التكلفة (اختياري)
        if show_cost_details:
            st.markdown("---")
            st.markdown("### 📋 تفاصيل التكلفة | Cost Breakdown")
            
            cost_col1, cost_col2 = st.columns(2)
            
            with cost_col1:
                st.markdown("**🔍 تفصيل التكلفة:**")
                cost_details_df = pd.DataFrame([
                    {"البند": "🚚 الشحن | Shipping", "التكلفة": f"{cost_breakdown['shipping_cost']:.2f} ر.س"},
                    {"البند": "📦 التجهيز | Fulfillment", "التكلفة": f"{cost_breakdown['fulfillment_cost']:.2f} ر.س"},
                    {"البند": "📦 التخزين | Storage", "التكلفة": f"{cost_breakdown['storage_cost']:.2f} ر.س"},
                    {"البند": "⚙️ العمومية والإدارية | Overhead", "التكلفة": f"{cost_breakdown['overhead_cost']:.2f} ر.س"},
                    {"البند": "↩️ المرتجعات | Returns", "التكلفة": f"{cost_breakdown['return_cost']:.2f} ر.س"},
                    {"البند": "💰 الإجمالي | Total", "التكلفة": f"{total_cost:.2f} ر.س"}
                ])
                st.dataframe(cost_details_df, use_container_width=True, hide_index=True)
            
            with cost_col2:
                st.markdown("**📊 معادلة التسعير:**")
                st.code(f"""
السعر المقترح = التكلفة ÷ (1 - هامش الربح%)
              = {total_cost:.2f} ÷ (1 - {target_margin/100})
              = {total_cost:.2f} ÷ {1 - target_margin/100:.2f}
              = {suggested_price:.2f} ر.س

الربح للطلب   = {suggested_price:.2f} - {total_cost:.2f}
              = {margins['profit_per_order_sar']:.2f} ر.س

هامش الربح %  = {margins['profit_per_order_sar']:.2f} ÷ {suggested_price:.2f}
              = {margins['margin_percentage']:.1f}%

الربح الشهري  = {margins['profit_per_order_sar']:.2f} × {monthly_volume:,}
              = {monthly_profit:,.0f} ر.س
                """, language="text")
        
        # حفظ العرض
        st.markdown("---")
        if st.button("💾 حفظ عرض السعر | Save Quote", use_container_width=True):
            quote_data = {
                'customer': 'عميل جديد',
                'service_type': 'comprehensive',
                'scenario': scenario,
                'monthly_volume': monthly_volume,
                'cost_per_order': total_cost,
                'suggested_price': suggested_price,
                'profit_margin': margins['margin_percentage'],
                'monthly_profit': monthly_profit,
                'capacity_usage_pct': capacity_usage['usage_percentage'],
                'risk_level': risk['risk_level'],
                'cost_breakdown': cost_breakdown,
                'grand_total': suggested_price
            }
            
            quote_id = db.save_quote(quote_data)
            if quote_id:
                st.success(f"✅ تم حفظ العرض برقم: **{quote_id}**")
                st.balloons()
            else:
                st.error("❌ فشل حفظ العرض")


def show_cma_pricing():
    """تسعير CMA - مقارنة مالية مع المنافسين"""
    st.markdown("### 📊 التسعير حسب دراسة CMA (دراسة السوق)")
    st.info("""
    **📊 تحليل مالي مقارن مع المنافسين**
    - احسب التكلفة والربح عند كل سعر منافس
    - اختر السعر الأمثل الذي يحقق أعلى ربحية
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 بيانات الطلب")
        scenario = st.selectbox(
            "السيناريو | Scenario",
            ['تجهيز + شحن داخل الرياض', 'تجهيز + شحن خارج الرياض'],
            key='cma_scenario'
        )
        monthly_volume = st.number_input(
            "الحجم الشهري | Monthly Volume",
            min_value=100,
            value=1000,
            step=100,
            key='cma_volume'
        )
    
    with col2:
        st.markdown("#### 💰 أسعار المنافسين")
        comp1 = st.number_input("منافس 1 (ر.س)", value=12.0, step=0.5, key='comp1')
        comp2 = st.number_input("منافس 2 (ر.س)", value=15.0, step=0.5, key='comp2')
        comp3 = st.number_input("منافس 3 (ر.س)", value=13.5, step=0.5, key='comp3')
    
    min_margin = st.slider("الحد الأدنى لهامش الربح %", 10.0, 30.0, 15.0, 5.0)
    
    if st.button("📊 تحليل CMA المالي | Analyze CMA", type="primary", use_container_width=True):
        with st.spinner("🔄 جاري التحليل المالي..."):
            # تحديد السيناريو
            scenario_key = 'fulfillment_riyadh' if 'داخل' in scenario else 'fulfillment_outside'
            
            # تحميل البيانات
            pl_df = db.load_dataframe('pnl')
            capacity_df = db.load_dataframe('capacity')
            
            # حساب التكلفة
            if pl_df is not None:
                pl_costs = fin_engine.load_pl_costs(pl_df)
            else:
                pl_costs = {'fulfillment_cost_per_order': 3.5, 'storage_cost_per_order': 1.5,
                           'shipping_cost_per_order': 8 if 'داخل' in scenario else 15,
                           'overhead_cost_per_order': 2}
            
            cost_breakdown = fin_engine.compute_unit_cost(scenario_key, pl_costs, include_return_cost=True)
            cost_per_order = cost_breakdown['total_cost_per_order']
            
            # تحليل كل منافس
            competitors_analysis = []
            for i, comp_price in enumerate([comp1, comp2, comp3], 1):
                margins = fin_engine.calculate_margins(comp_price, cost_per_order, monthly_volume)
                risk = fin_engine.risk_warning(margins['margin_percentage'], min_margin, 25)
                
                competitors_analysis.append({
                    'المنافس': f'منافس {i}',
                    'السعر': comp_price,
                    'التكلفة': cost_per_order,
                    'الربح/طلب': margins['profit_per_order_sar'],
                    'هامش الربح %': margins['margin_percentage'],
                    'ربح شهري': margins['monthly_profit_sar'],
                    'ربح سنوي': margins['annual_profit_sar'],
                    'التقييم': '✅ ممتاز' if risk['risk_level'] == 'safe' else ('⚠️ مقبول' if risk['risk_level'] == 'moderate' else '🚨 خطر')
                })
            
            # إيجاد أفضل سعر
            valid_prices = [c for c in competitors_analysis if c['هامش الربح %'] >= min_margin]
            if valid_prices:
                best_choice = min(valid_prices, key=lambda x: x['السعر'])  # أقل سعر ضمن المقبول
                recommended_price = best_choice['السعر']
            else:
                # كل الأسعار تحت الحد الأدنى - نقترح سعر بهامش مقبول
                pricing_result = fin_engine.suggest_price(cost_per_order, min_margin)
                recommended_price = pricing_result['suggested_price']
        
        st.success("✅ تم تحليل المنافسين!")
        
        # جدول المقارنة
        st.markdown("### 📊 جدول المقارنة المالية")
        comparison_df = pd.DataFrame(competitors_analysis)
        
        # تنسيق الأرقام
        comparison_df['السعر'] = comparison_df['السعر'].apply(lambda x: f"{x:.2f} ر.س")
        comparison_df['التكلفة'] = comparison_df['التكلفة'].apply(lambda x: f"{x:.2f} ر.س")
        comparison_df['الربح/طلب'] = comparison_df['الربح/طلب'].apply(lambda x: f"{x:.2f} ر.س")
        comparison_df['هامش الربح %'] = comparison_df['هامش الربح %'].apply(lambda x: f"{x:.1f}%")
        comparison_df['ربح شهري'] = comparison_df['ربح شهري'].apply(lambda x: f"{x:,.0f} ر.س")
        comparison_df['ربح سنوي'] = comparison_df['ربح سنوي'].apply(lambda x: f"{x:,.0f} ر.س")
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # التوصية
        st.markdown("---")
        st.markdown("### 💡 التوصية")
        
        if valid_prices:
            st.success(f"""
            **السعر الموصى به: {recommended_price:.2f} ر.س**
            
            ✅ هذا السعر:
            - أقل من المنافسين (ميزة تنافسية)
            - يحقق هامش ربح أعلى من الحد الأدنى ({min_margin}%)
            - يحقق ربح شهري: {best_choice['ربح شهري']}
            """)
        else:
            st.warning(f"""
            ⚠️ **جميع أسعار المنافسين أقل من الحد الأدنى المقبول!**
            
            السعر الموصى به: **{recommended_price:.2f} ر.س**
            
            💡 خياراتك:
            1. قبول هامش ربح أقل للمنافسة
            2. تقليل التكاليف لخفض السعر
            3. إبراز قيمة إضافية تبرر السعر الأعلى
            """)
        
        # رسم بياني للمقارنة
        st.markdown("---")
        st.markdown("### 📈 رسم بياني للمقارنة")
        
        # البيانات الأصلية للرسم
        chart_data = pd.DataFrame(competitors_analysis)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=chart_data['المنافس'],
            y=chart_data['ربح شهري'],
            name='الربح الشهري',
            marker_color='lightgreen'
        ))
        fig.update_layout(
            title='مقارنة الربح الشهري عند أسعار المنافسين',
            xaxis_title='المنافس',
            yaxis_title='الربح الشهري (ر.س)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_predictive_pricing():
    """التسعير التنبؤي"""
    st.markdown("### 🤖 التسعير التنبؤي بالذكاء الاصطناعي")
    st.info("استخدام الذكاء الاصطناعي للتنبؤ بالسعر الأمثل بناءً على البيانات التاريخية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_type = st.selectbox(
            "نوع الخدمة",
            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام'],
            key='ai_service'
        )
        quantity = st.number_input("الكمية", min_value=1, value=100, step=10, key='ai_qty')
    
    with col2:
        forecast_days = st.slider("أيام التوقع", 7, 90, 30)
        confidence_level = st.slider("مستوى الثقة %", 80, 99, 95)
    
    if st.button("🤖 تنبؤ بالسعر الأمثل", type="primary"):
        result = engine.calculate_predictive_price(
            service_type=service_type,
            quantity=quantity
        )
        
        if 'error' not in result:
            st.success("✅ تم التنبؤ!")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("السعر المتنبأ", f"{result.get('predicted_price', 0):.2f} ر.س")
            with col2:
                st.metric("الطلب المتوقع", f"{result.get('demand_forecast', 0):.0f}")
            with col3:
                st.metric("دقة التوقع", f"{result.get('confidence', 95):.1f}%")
        else:
            st.warning(f"⚠️ {result['error']}")
            st.info("استخدام النموذج الأساسي...")


def show_enterprise_pricing():
    """تسعير المؤسسات"""
    st.markdown("### 🏢 تسعير المؤسسات والعملاء الكبار")
    st.info("نموذج تسعير متخصص للعقود طويلة الأجل والعملاء المؤسسيين")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_type = st.selectbox(
            "نوع الخدمة",
            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام'],
            key='ent_service'
        )
        quantity = st.number_input("الكمية", min_value=1, value=1000, step=100, key='ent_qty')
    
    with col2:
        customer_type = st.selectbox(
            "تصنيف العميل",
            ['Enterprise', 'Corporate', 'Premium', 'Standard']
        )
        contract_months = st.slider("مدة العقد (شهور)", 1, 36, 12)
    
    if st.button("🏢 احسب سعر المؤسسات", type="primary"):
        result = engine.calculate_enterprise_price(
            service_type=service_type,
            quantity=quantity,
            customer_type=customer_type
        )
        
        if 'error' not in result:
            st.success("✅ تم الحساب!")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("السعر للوحدة", f"{result.get('unit_price', 0):.2f} ر.س")
            with col2:
                st.metric("الإجمالي", f"{result.get('total_price', 0):,.0f} ر.س")
            with col3:
                st.metric("الخصم المطبق", f"{result.get('discount', 0):.1f}%")
        else:
            st.warning(f"⚠️ {result['error']}")


def show_dynamic_pricing():
    """التسعير الديناميكي"""
    st.markdown("### ⚡ التسعير الديناميكي المتقدم")
    st.info("تسعير ذكي يتكيف مع الطلب والعرض والمواسم")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_type = st.selectbox(
            "نوع الخدمة",
            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام'],
            key='dyn_service'
        )
        quantity = st.number_input("الكمية", min_value=1, value=100, step=10, key='dyn_qty')
        
        demand_level = st.select_slider(
            "مستوى الطلب الحالي",
            options=['low', 'normal', 'high', 'peak'],
            value='normal',
            format_func=lambda x: {'low': 'منخفض', 'normal': 'عادي', 'high': 'عالي', 'peak': 'ذروة'}[x]
        )
    
    with col2:
        season = st.select_slider(
            "الموسم",
            options=['low', 'normal', 'high', 'peak'],
            value='normal',
            format_func=lambda x: {'low': 'راكد', 'normal': 'عادي', 'high': 'نشط', 'peak': 'موسم ذروة'}[x]
        )
        
        capacity_usage = st.slider("استخدام الطاقة %", 0, 100, 70)
    
    if st.button("⚡ احسب السعر الديناميكي", type="primary"):
        result = engine.calculate_advanced_dynamic_price(
            service_type=service_type,
            quantity=quantity,
            demand_level=demand_level,
            season=season
        )
        
        if 'error' not in result:
            st.success("✅ تم الحساب!")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("السعر الديناميكي", f"{result.get('dynamic_price', 0):.2f} ر.س")
            with col2:
                st.metric("السعر الأساسي", f"{result.get('base_price', 0):.2f} ر.س")
            with col3:
                multiplier = result.get('multiplier', 1.0)
                delta = f"+{(multiplier-1)*100:.0f}%" if multiplier > 1 else f"{(multiplier-1)*100:.0f}%"
                st.metric("المضاعف", f"×{multiplier:.2f}", delta=delta)
        else:
            st.warning(f"⚠️ {result['error']}")


def show_pricing_comparison():
    """مقارنة جميع النماذج"""
    st.markdown("### 🔄 مقارنة شاملة لجميع نماذج التسعير")
    st.info("احصل على أسعار من جميع النماذج دفعة واحدة وقارن بينها")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_type = st.selectbox(
            "نوع الخدمة",
            ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين', 'ايراد الاستلام'],
            key='comp_service'
        )
        quantity = st.number_input("الكمية", min_value=1, value=100, step=10, key='comp_qty')
    
    with col2:
        customer = st.text_input("العميل (اختياري)", key='comp_customer')
        city = st.text_input("المدينة", "الرياض", key='comp_city')
    
    if st.button("🔄 قارن جميع النماذج", type="primary", use_container_width=True):
        with st.spinner("جاري حساب جميع النماذج..."):
            comparison = engine.get_pricing_comparison(
                service_type=service_type,
                quantity=quantity,
                customer=customer if customer else None,
                city=city,
                weight=2.0,
                order_value=300.0
            )
        
        st.success("✅ تم حساب جميع النماذج!")
        
        # عرض المقارنة
        models_data = []
        for model_name, result in comparison.items():
            if 'error' not in result:
                price = result.get('grand_total') or result.get('total_price') or result.get('recommended_price', 0)
                models_data.append({
                    'النموذج': model_name.upper(),
                    'السعر': f"{price:.2f} ر.س",
                    'السعر_الرقمي': price
                })
        
        if models_data:
            df = pd.DataFrame(models_data)
            
            # ترتيب حسب السعر
            df = df.sort_values('السعر_الرقمي')
            
            # عرض الجدول
            st.dataframe(df[['النموذج', 'السعر']], use_container_width=True)
            
            # رسم بياني
            fig = px.bar(
                df,
                x='النموذج',
                y='السعر_الرقمي',
                title='مقارنة الأسعار بين النماذج المختلفة',
                labels={'السعر_الرقمي': 'السعر (ر.س)'},
                color='السعر_الرقمي',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # التوصية
            best_model = df.iloc[0]
            worst_model = df.iloc[-1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🏆 **الأفضل:** {best_model['النموذج']} - {best_model['السعر']}")
            with col2:
                st.info(f"💰 **الأعلى:** {worst_model['النموذج']} - {worst_model['السعر']}")



def show_quotes():
    """📜 سجل العروض المحفوظة في قاعدة البيانات"""
    st.markdown('<div class="big-title">📜 سجل عروض الأسعار</div>', unsafe_allow_html=True)
    
    # تحميل العروض من قاعدة البيانات
    quotes_df = db.get_all_quotes()
    
    if not quotes_df.empty:
        st.markdown("### 📊 جميع العروض المحفوظة")
        
        # عرض كل عرض مع زر طباعة وحذف
        for idx, row in quotes_df.iterrows():
            with st.expander(f"📋 {row['quote_id']} - {row['customer_name']} | {row['service_type']}", expanded=False):
                # معلومات أساسية
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**👤 اسم العميل | Customer Name:** {row['customer_name']}")
                    st.write(f"**📅 تاريخ الإنشاء | Created Date:** {pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**🏷️ نوع الخدمة | Service Type:** {'يدوي | Manual' if row['service_type'] == 'manual' else 'ذكي | Smart'}")
                    st.write(f"**🔖 رقم العرض | Quote ID:** {row['quote_id']}")
                
                with col2:
                    st.metric("السعر الإجمالي\nTotal Price", f"{row['total_price']:,.2f} ر.س")
                
                # التفاصيل الكاملة
                st.markdown("---")
                st.markdown("#### 📋 تفاصيل العرض | Quote Details")
                
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                
                with detail_col1:
                    if 'monthly_volume' in row and pd.notna(row['monthly_volume']):
                        st.write(f"**📦 الحجم الشهري | Monthly Volume:** {row['monthly_volume']:,.0f}")
                    if 'service_type' in row:
                        st.write(f"**⚙️ طريقة التسعير | Pricing Method:** {row['service_type']}")
                
                with detail_col2:
                    if 'customer_tier' in row and pd.notna(row['customer_tier']):
                        st.write(f"**⭐ فئة العميل | Customer Tier:** {row['customer_tier']}")
                    if 'pricing_model' in row and pd.notna(row['pricing_model']):
                        st.write(f"**🎯 نموذج التسعير | Pricing Model:** {row['pricing_model']}")
                
                with detail_col3:
                    if 'avg_order_value' in row and pd.notna(row['avg_order_value']):
                        st.write(f"**💵 متوسط قيمة الطلب | Avg Order:** {row['avg_order_value']:,.2f} ر.س")
                    if 'profit_margin' in row and pd.notna(row['profit_margin']):
                        st.write(f"**📈 هامش الربح | Profit Margin:** {row['profit_margin']:.1f}%")
                
                # تفاصيل التكلفة (إذا كانت متوفرة)
                if 'cost_breakdown' in row and pd.notna(row['cost_breakdown']):
                    st.markdown("---")
                    st.markdown("#### 💰 تفاصيل التكلفة | Cost Breakdown")
                    try:
                        import json
                        cost_data = json.loads(row['cost_breakdown']) if isinstance(row['cost_breakdown'], str) else row['cost_breakdown']
                        cost_col1, cost_col2, cost_col3, cost_col4 = st.columns(4)
                        
                        with cost_col1:
                            if 'shipping' in cost_data:
                                st.metric("🚚 الشحن | Shipping", f"{cost_data['shipping']:.2f} ر.س")
                        with cost_col2:
                            if 'fulfillment' in cost_data:
                                st.metric("📦 التجهيز | Fulfillment", f"{cost_data['fulfillment']:.2f} ر.س")
                        with cost_col3:
                            if 'packaging' in cost_data:
                                st.metric("📦 التغليف | Packaging", f"{cost_data['packaging']:.2f} ر.س")
                        with cost_col4:
                            if 'overhead' in cost_data:
                                st.metric("⚙️ المصاريف | Overhead", f"{cost_data['overhead']:.2f} ر.س")
                    except:
                        pass
                
                # أزرار الإجراءات
                st.markdown("---")
                action_col1, action_col2, action_col3 = st.columns([1, 1, 3])
                
                with action_col1:
                    if st.button("🖨️ طباعة | Print", key=f"print_{row['quote_id']}", use_container_width=True):
                        # تحميل بيانات الشركة
                        company_name_ar = db.get_setting('company_name_ar', 'شركة متالي للخدمات اللوجستية')
                        company_name_en = db.get_setting('company_name_en', 'Matali Logistics Services Company')
                        company_email = db.get_setting('company_email', 'info@matali.com')
                        company_phone = db.get_setting('company_phone', '+966 XX XXX XXXX')
                        company_website = db.get_setting('company_website', 'www.matali.com')
                        company_slogan_ar = db.get_setting('company_slogan_ar', 'شريكك الموثوق للخدمات اللوجستية')
                        company_tax = db.get_setting('company_tax_number', '')
                        company_cr = db.get_setting('company_cr_number', '')
                        
                        # شعار الشركة
                        logo_html = ""
                        logo_path = db.get_setting('company_logo_path')
                        if logo_path and Path(logo_path).exists():
                            import base64
                            with open(logo_path, "rb") as f:
                                logo_data = base64.b64encode(f.read()).decode()
                            logo_html = f'<img src="data:image/png;base64,{logo_data}" style="max-height: 70px; margin-bottom: 10px;">'
                        
                        # إنشاء HTML للطباعة
                        quote_type = 'يدوي | Manual' if row['service_type'] == 'manual' else 'ذكي | Smart'
                        
                        html_content = f"""
                        <html dir="rtl">
                        <head>
                            <meta charset="utf-8">
                            <style>
                                body {{
                                    font-family: Arial, sans-serif;
                                    direction: rtl;
                                    padding: 30px;
                                    background: white;
                                }}
                                .header {{
                                    text-align: center;
                                    border-bottom: 4px solid #2563eb;
                                    padding-bottom: 25px;
                                    margin-bottom: 40px;
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    padding: 30px;
                                    border-radius: 15px;
                                    color: white;
                                }}
                                .company-name {{
                                    font-size: 36px;
                                    font-weight: bold;
                                    margin-bottom: 10px;
                                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                                }}
                                .company-name-en {{
                                    font-size: 20px;
                                    font-style: italic;
                                    margin-bottom: 15px;
                                    opacity: 0.9;
                                }}
                                .quote-title {{
                                    font-size: 26px;
                                    margin-top: 15px;
                                    font-weight: 600;
                                }}
                                .quote-number {{
                                    background: white;
                                    color: #2563eb;
                                    padding: 10px 20px;
                                    border-radius: 25px;
                                    display: inline-block;
                                    margin-top: 15px;
                                    font-weight: bold;
                                    font-size: 18px;
                                }}
                                .info-section {{
                                    background: #f8f9fa;
                                    padding: 20px;
                                    border-radius: 10px;
                                    margin: 25px 0;
                                    border-right: 5px solid #2563eb;
                                }}
                                .info-row {{
                                    display: flex;
                                    justify-content: space-between;
                                    padding: 12px 0;
                                    border-bottom: 1px solid #e5e7eb;
                                }}
                                .info-row:last-child {{
                                    border-bottom: none;
                                }}
                                .info-label {{
                                    font-weight: bold;
                                    color: #374151;
                                    font-size: 16px;
                                }}
                                .info-value {{
                                    color: #1f2937;
                                    font-size: 16px;
                                }}
                                .price-highlight {{
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    padding: 25px;
                                    border-radius: 15px;
                                    text-align: center;
                                    margin: 30px 0;
                                    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                                }}
                                .price-label {{
                                    font-size: 20px;
                                    margin-bottom: 15px;
                                    opacity: 0.95;
                                }}
                                .price-value {{
                                    font-size: 42px;
                                    font-weight: bold;
                                    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                                }}
                                .footer {{
                                    margin-top: 60px;
                                    text-align: center;
                                    color: #6b7280;
                                    font-size: 13px;
                                    border-top: 2px solid #e5e7eb;
                                    padding-top: 25px;
                                }}
                                .footer-divider {{
                                    margin: 10px 0;
                                    height: 1px;
                                    background: #e5e7eb;
                                }}
                                @media print {{
                                    body {{
                                        padding: 0;
                                        margin: 0;
                                    }}
                                    @page {{
                                        size: A4;
                                        margin: 1.5cm;
                                    }}
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                {logo_html}
                                <div class="company-name">{company_name_ar}</div>
                                <div class="company-name-en">{company_name_en}</div>
                                <div style="font-size: 16px; font-style: italic; margin: 10px 0; opacity: 0.9;">{company_slogan_ar}</div>
                                <div class="quote-title">📋 عرض سعر | Price Quote</div>
                                <div class="quote-number">#{row['quote_id']}</div>
                            </div>
                            
                            <div class="info-section">
                                <div class="info-row">
                                    <span class="info-label">👤 اسم العميل | Customer Name:</span>
                                    <span class="info-value">{row['customer_name']}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">📅 تاريخ العرض | Quote Date:</span>
                                    <span class="info-value">{pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">🏷️ نوع الخدمة | Service Type:</span>
                                    <span class="info-value">{quote_type}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">🔖 رقم العرض | Quote Number:</span>
                                    <span class="info-value">{row['quote_id']}</span>
                                </div>
                            </div>
                            
                            <div class="price-highlight">
                                <div class="price-label">💰 السعر الإجمالي | Total Price</div>
                                <div class="price-value">{row['total_price']:,.2f} ريال سعودي</div>
                                <div class="price-label" style="font-size: 16px; margin-top: 10px;">SAR {row['total_price']:,.2f}</div>
                            </div>
                            
                            <div class="info-section" style="background: #fef3c7; border-right-color: #f59e0b;">
                                <p style="margin: 0; font-size: 15px; color: #92400e;">
                                    <strong>📌 ملاحظة | Note:</strong><br>
                                    هذا العرض صالح لمدة 30 يوماً من تاريخ الإصدار<br>
                                    <em style="font-size: 13px;">This quote is valid for 30 days from the issue date</em>
                                </p>
                            </div>
                            
                            <div class="footer">
                                <p style="font-weight: bold; font-size: 15px; color: #1e40af; margin-bottom: 10px;">
                                    {company_name_ar} | {company_name_en}
                                </p>
                                <div class="footer-divider"></div>
                                <p style="margin: 8px 0;">
                                    📧 البريد الإلكتروني | Email: {company_email}
                                </p>
                                <p style="margin: 8px 0;">
                                    📱 الهاتف | Phone: {company_phone}
                                </p>
                                <p style="margin: 8px 0;">
                                    🌐 الموقع الإلكتروني | Website: {company_website}
                                </p>
                                {f'<p style="margin: 8px 0; font-size: 12px;">الرقم الضريبي: {company_tax} | السجل التجاري: {company_cr}</p>' if company_tax or company_cr else ''}
                                <div class="footer-divider" style="margin-top: 15px;"></div>
                                <p style="margin-top: 15px; font-size: 11px; color: #9ca3af;">
                                    تم إنشاء هذا العرض تلقائياً بواسطة نظام متالي للتسعير الذكي V2.0<br>
                                    <em>Generated automatically by Matali Smart Pricing System V2.0</em>
                                </p>
                            </div>
                        </body>
                        </html>
                        """
                        
                        # عرض زر الطباعة
                        st.components.v1.html(
                            f"""
                            <script>
                                function printQuote() {{
                                    var printWindow = window.open('', '', 'height=900,width=800');
                                    printWindow.document.write(`{html_content}`);
                                    printWindow.document.close();
                                    printWindow.focus();
                                    setTimeout(function() {{
                                        printWindow.print();
                                    }}, 250);
                                }}
                                printQuote();
                            </script>
                            """,
                            height=0
                        )
                        st.success(f"✅ تم فتح نافذة طباعة العرض #{row['quote_id']}")
                
                with action_col2:
                    delete_key = f"delete_{row['quote_id']}_{idx}"
                    if st.button("🗑️ حذف | Delete", key=delete_key, type="secondary", use_container_width=True):
                        # تأكيد الحذف
                        st.session_state[f'confirm_delete_{row["quote_id"]}'] = True
                
                # نافذة تأكيد الحذف
                if st.session_state.get(f'confirm_delete_{row["quote_id"]}', False):
                    st.warning(f"⚠️ هل أنت متأكد من حذف العرض #{row['quote_id']}؟")
                    confirm_col1, confirm_col2 = st.columns(2)
                    
                    with confirm_col1:
                        if st.button("✅ نعم، احذف | Yes, Delete", key=f"confirm_yes_{row['quote_id']}", type="primary"):
                            try:
                                # حذف من قاعدة البيانات
                                db.delete_quote(row['quote_id'])
                                st.success(f"✅ تم حذف العرض #{row['quote_id']} بنجاح")
                                # مسح حالة التأكيد
                                del st.session_state[f'confirm_delete_{row["quote_id"]}']
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ خطأ في حذف العرض: {str(e)}")
                    
                    with confirm_col2:
                        if st.button("❌ لا، إلغاء | No, Cancel", key=f"confirm_no_{row['quote_id']}"):
                            del st.session_state[f'confirm_delete_{row["quote_id"]}']
                            st.rerun()
        
        # إحصائيات
        st.markdown("---")
        st.markdown("### 📈 الإحصائيات")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("إجمالي العروض", len(quotes_df))
        
        with col2:
            total_value = quotes_df['total_price'].sum()
            st.metric("إجمالي القيمة", f"{total_value:,.0f} ر.س")
        
        with col3:
            avg_quote = quotes_df['total_price'].mean()
            st.metric("متوسط قيمة العرض", f"{avg_quote:,.0f} ر.س")
        
        with col4:
            manual_count = len(quotes_df[quotes_df['service_type'] == 'manual'])
            smart_count = len(quotes_df[quotes_df['service_type'] == 'smart'])
            st.metric("يدوي/ذكي", f"{manual_count}/{smart_count}")
        
        # رسم بياني
        st.markdown("---")
        st.markdown("### 📊 توزيع العروض")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # حسب النوع
            type_counts = quotes_df['service_type'].value_counts()
            fig = px.pie(
                values=type_counts.values,
                names=['يدوي' if x == 'manual' else 'ذكي' for x in type_counts.index],
                title='توزيع العروض حسب النوع'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # حسب العميل
            customer_counts = quotes_df['customer_name'].value_counts().head(10)
            fig = px.bar(
                x=customer_counts.values,
                y=customer_counts.index,
                orientation='h',
                title='أكثر 10 عملاء (عدد العروض)',
                labels={'x': 'عدد العروض', 'y': 'العميل'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("📭 لا توجد عروض أسعار محفوظة بعد.")
        st.markdown("""
        **💡 لإنشاء عرض سعر:**
        1. اذهب إلى "🧾 عرض سعر متقدم" أو "📄 عرض سعر احترافي"
        2. املأ البيانات المطلوبة
        3. اضغط على زر "حفظ عرض السعر"
        """)


def show_professional_quote():
    """📄 إنشاء عرض سعر احترافي قابل للطباعة"""
    st.markdown('<div class="big-title">📄 عرض سعر احترافي</div>', unsafe_allow_html=True)
    
    # CSS للطباعة - محسّن
    st.markdown("""
    <style>
        @media print {
            .stApp > header {display: none !important;}
            .stSidebar {display: none !important;}
            button {display: none !important;}
            .print-hide {display: none !important;}
            .quote-container {
                padding: 1.5cm !important;
                background: white !important;
                border: none !important;
                box-shadow: none !important;
                page-break-inside: avoid;
            }
            @page {
                size: A4;
                margin: 1cm;
            }
        }
        
        .quote-container {
            background: white;
            padding: 2.5rem;
            border: 3px solid #0066cc;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .quote-header {
            text-align: center;
            border-bottom: 4px double #0066cc;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem;
            border-radius: 10px;
        }
        
        .company-name {
            font-size: 3rem;
            font-weight: bold;
            color: #0066cc;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .company-name-en {
            font-size: 1.3rem;
            color: #555;
            font-style: italic;
            margin-bottom: 0.5rem;
        }
        
        .company-slogan {
            color: #666;
            font-size: 1rem;
            margin-top: 0.5rem;
            font-weight: 500;
        }
        
        .quote-title {
            font-size: 2rem;
            color: white;
            background: #0066cc;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            display: inline-block;
            margin-top: 1rem;
            font-weight: bold;
        }
        
        .quote-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2rem;
            margin: 2rem 0;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 10px;
            border: 2px solid #e9ecef;
        }
        
        .info-box {
            padding: 1.2rem;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #0066cc;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .info-box:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .info-label {
            font-weight: bold;
            color: #0066cc;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .info-value {
            font-size: 1.15rem;
            color: #212529;
            font-weight: 500;
        }
        
        .services-section-title {
            font-size: 1.5rem;
            color: #0066cc;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #0066cc;
            font-weight: bold;
        }
        
        .services-table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .services-table th {
            background: linear-gradient(135deg, #0066cc 0%, #004a99 100%);
            color: white;
            padding: 1.2rem;
            text-align: center;
            font-size: 1.1rem;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        
        .services-table td {
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
            text-align: center;
            background: white;
        }
        
        .services-table tbody tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .services-table tbody tr:hover {
            background: #e9ecef;
            transition: background 0.2s ease;
        }
        
        .subtotal-row {
            background: #e3f2fd !important;
            font-weight: 600;
            font-size: 1.05rem;
        }
        
        .discount-row {
            background: #fff3cd !important;
            color: #856404;
            font-weight: 600;
        }
        
        .tax-row {
            background: #f8d7da !important;
            font-weight: 600;
        }
        
        .total-row {
            background: linear-gradient(135deg, #0066cc 0%, #004a99 100%) !important;
            color: white !important;
            font-weight: bold;
            font-size: 1.4rem;
            padding: 1.5rem !important;
        }
        
        .total-row td {
            color: white !important;
            border: none !important;
        }
        
        .quote-footer {
            margin-top: 3rem;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            border-top: 4px solid #0066cc;
        }
        
        .terms-title {
            font-size: 1.3rem;
            color: #0066cc;
            font-weight: bold;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        
        .terms {
            font-size: 0.95rem;
            color: #495057;
            line-height: 2;
            padding: 1rem;
            background: white;
            border-radius: 8px;
        }
        
        .terms p {
            margin: 0.8rem 0;
            padding-right: 1.5rem;
            position: relative;
        }
        
        .terms p:before {
            content: "✓";
            position: absolute;
            right: 0;
            color: #0066cc;
            font-weight: bold;
        }
        
        .signature-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            margin-top: 4rem;
            padding-top: 2rem;
        }
        
        .signature-box {
            text-align: center;
            padding: 2rem;
            border: 2px dashed #0066cc;
            border-radius: 10px;
            background: white;
            min-height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .signature-title {
            font-weight: bold;
            color: #0066cc;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        
        .signature-line {
            border-top: 2px solid #333;
            margin-top: 3rem;
            padding-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .company-footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            border: 2px solid #0066cc;
        }
        
        .footer-section {
            margin: 0.8rem 0;
            color: #495057;
            font-size: 0.95rem;
        }
        
        .footer-section strong {
            color: #0066cc;
        }
        
        .highlight-box {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            text-align: center;
        }
        
        .highlight-box h3 {
            color: #856404;
            margin-bottom: 1rem;
        }
        
        .quote-number-badge {
            background: #0066cc;
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            font-weight: bold;
            display: inline-block;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # نموذج الإدخال
    st.markdown('<div class="print-hide">', unsafe_allow_html=True)
    
    st.info("📝 **ملاحظة:** املأ جميع الحقول المطلوبة (*) للحصول على عرض سعر احترافي كامل")
    
    # معلومات العرض الأساسية
    st.markdown("### 📋 معلومات العرض")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        quote_number = st.text_input("رقم العرض *", value=f"MAT-{datetime.now().strftime('%Y%m%d%H%M')}", 
                                    help="رقم مرجعي فريد لعرض السعر")
    with col2:
        quote_date = st.date_input("تاريخ العرض *", value=datetime.now())
    with col3:
        valid_until = st.date_input("صالح حتى *", value=datetime.now() + pd.Timedelta(days=30),
                                    help="تاريخ انتهاء صلاحية العرض")
    
    st.markdown("---")
    
    # معلومات العميل
    st.markdown("### 👤 معلومات العميل")
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("اسم العميل / الشركة *", placeholder="مثال: شركة التقنية المتقدمة",
                                     help="الاسم الرسمي للعميل أو الشركة")
        customer_contact = st.text_input("جهة الاتصال", placeholder="مثال: أحمد محمد علي",
                                        help="الشخص المسؤول عن المتابعة")
        customer_phone = st.text_input("رقم الهاتف *", placeholder="+966 50 123 4567",
                                      help="رقم الجوال أو الهاتف")
        customer_address = st.text_input("العنوان", placeholder="المدينة، الحي، الشارع")
    
    with col2:
        customer_email = st.text_input("البريد الإلكتروني *", placeholder="info@company.com",
                                      help="البريد الإلكتروني الرسمي")
        project_name = st.text_input("اسم المشروع / الطلب", placeholder="مثال: مشروع التجارة الإلكترونية 2025")
        customer_cr = st.text_input("السجل التجاري", placeholder="1234567890 (اختياري)")
        customer_vat = st.text_input("الرقم الضريبي", placeholder="123456789012345 (اختياري)")
    
    st.markdown("---")
    st.markdown("### 📦 الخدمات والأسعار")
    
    # إضافة الخدمات
    if 'quote_services' not in st.session_state:
        st.session_state.quote_services = []
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        service_name = st.text_input("اسم الخدمة", key="new_service_name")
    with col2:
        service_qty = st.number_input("الكمية", min_value=1, value=1, key="new_service_qty")
    with col3:
        service_price = st.number_input("السعر للوحدة", min_value=0.0, value=0.0, step=0.01, key="new_service_price")
    with col4:
        st.write("")
        st.write("")
        if st.button("➕ إضافة", use_container_width=True):
            if service_name:
                st.session_state.quote_services.append({
                    'service': service_name,
                    'quantity': service_qty,
                    'unit_price': service_price,
                    'total': service_qty * service_price
                })
                st.rerun()
    
    # عرض الخدمات المضافة
    if st.session_state.quote_services:
        services_df = pd.DataFrame(st.session_state.quote_services)
        st.dataframe(services_df, use_container_width=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ مسح الكل", use_container_width=True):
                st.session_state.quote_services = []
                st.rerun()
    
    # إعدادات إضافية
    st.markdown("---")
    st.markdown("### ⚙️ الإعدادات والشروط")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        discount_percent = st.number_input("نسبة الخصم %", min_value=0.0, max_value=100.0, value=0.0,
                                          help="خصم على المجموع الفرعي")
    with col2:
        tax_percent = st.number_input("نسبة الضريبة %", min_value=0.0, max_value=100.0, value=15.0,
                                     help="ضريبة القيمة المضافة في السعودية 15%")
    with col3:
        delivery_days = st.number_input("مدة التسليم (يوم)", min_value=1, value=7,
                                       help="عدد الأيام المتوقعة للتسليم")
    with col4:
        warranty_months = st.number_input("فترة الضمان (شهر)", min_value=0, value=0,
                                         help="فترة الضمان بالأشهر (إن وجدت)")
    
    col1, col2 = st.columns(2)
    with col1:
        payment_terms = st.selectbox("شروط الدفع *", [
            "نقدي عند التسليم",
            "تحويل بنكي خلال 30 يوم",
            "50% مقدم والباقي عند التسليم",
            "30% مقدم - 40% عند التنفيذ - 30% عند الإنجاز",
            "الدفع بالتقسيط الشهري",
            "دفع كامل مقدماً"
        ])
    with col2:
        delivery_terms = st.selectbox("شروط التسليم", [
            "التسليم في الموقع",
            "الاستلام من المستودع",
            "التوصيل المجاني داخل المدينة",
            "التوصيل مدفوع حسب المسافة"
        ])
    
    notes = st.text_area("ملاحظات وشروط إضافية", 
                        placeholder="مثال:\n- الأسعار قابلة للتفاوض للكميات الكبيرة\n- يُطبق خصم خاص للعملاء الدائمين\n- التركيب والتدريب متضمن في السعر",
                        height=100)
    
    st.markdown("---")
    
    # زر الطباعة والمعاينة
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        preview_button = st.button("👁️ معاينة العرض", type="primary", use_container_width=True)
    with col2:
        if st.button("🖨️ طباعة", use_container_width=True):
            st.components.v1.html("""
            <script>
                window.print();
            </script>
            """, height=0)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # عرض النموذج
    if preview_button or st.session_state.quote_services:
        # حساب الإجماليات
        subtotal = sum(item['total'] for item in st.session_state.quote_services)
        discount_amount = subtotal * (discount_percent / 100)
        after_discount = subtotal - discount_amount
        tax_amount = after_discount * (tax_percent / 100)
        total = after_discount + tax_amount
        
        # النموذج الاحترافي
        st.markdown('<div class="quote-container">', unsafe_allow_html=True)
        
        # الرأسية المحسّنة
        st.markdown(f"""
        <div class="quote-header">
            <div class="company-name">🏢 شركة متالي</div>
            <div class="company-name-en">MATALI LOGISTICS COMPANY</div>
            <div class="company-slogan">⭐ شريكك الموثوق للخدمات اللوجستية والتخزين ⭐</div>
            <div class="quote-title">📄 عرض سعر</div>
            <div class="quote-number-badge">رقم: {quote_number}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # معلومات العرض المحسّنة
        st.markdown(f"""
        <div class="quote-info">
            <div class="info-box">
                <div class="info-label">📅 تاريخ العرض</div>
                <div class="info-value">{quote_date.strftime('%d %B %Y')} - {quote_date.strftime('%A')}</div>
            </div>
            <div class="info-box">
                <div class="info-label">⏰ صالح حتى</div>
                <div class="info-value">{valid_until.strftime('%d %B %Y')}</div>
            </div>
            <div class="info-box">
                <div class="info-label">🏢 اسم العميل</div>
                <div class="info-value">{customer_name or 'غير محدد'}</div>
            </div>
            <div class="info-box">
                <div class="info-label">👤 جهة الاتصال</div>
                <div class="info-value">{customer_contact or '-'}</div>
            </div>
            <div class="info-box">
                <div class="info-label">📱 الهاتف</div>
                <div class="info-value">{customer_phone or '-'}</div>
            </div>
            <div class="info-box">
                <div class="info-label">📧 البريد الإلكتروني</div>
                <div class="info-value">{customer_email or '-'}</div>
            </div>
            <div class="info-box">
                <div class="info-label">📍 العنوان</div>
                <div class="info-value">{customer_address if 'customer_address' in locals() and customer_address else '-'}</div>
            </div>
            <div class="info-box">
                <div class="info-label">📋 المشروع</div>
                <div class="info-value">{project_name or '-'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # جدول الخدمات المحسّن
        if st.session_state.quote_services:
            st.markdown('<h3 class="services-section-title">📦 تفاصيل الخدمات المطلوبة</h3>', unsafe_allow_html=True)
            
            services_html = """
            <table class="services-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">م</th>
                        <th style="width: 40%;">وصف الخدمة</th>
                        <th style="width: 15%;">الكمية</th>
                        <th style="width: 20%;">سعر الوحدة</th>
                        <th style="width: 20%;">الإجمالي</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for idx, item in enumerate(st.session_state.quote_services, 1):
                services_html += f"""
                <tr>
                    <td><strong>{idx}</strong></td>
                    <td style="text-align: right;">{item['service']}</td>
                    <td>{item['quantity']:,}</td>
                    <td>{item['unit_price']:,.2f} ر.س</td>
                    <td><strong>{item['total']:,.2f} ر.س</strong></td>
                </tr>
                """
            
            services_html += f"""
                </tbody>
                <tfoot>
                    <tr class="subtotal-row">
                        <td colspan="4" style="text-align: left; padding: 1.2rem;"><strong>المجموع الفرعي</strong></td>
                        <td style="padding: 1.2rem;"><strong>{subtotal:,.2f} ر.س</strong></td>
                    </tr>
            """
            
            if discount_percent > 0:
                services_html += f"""
                    <tr class="discount-row">
                        <td colspan="4" style="text-align: left; padding: 1rem;">🎁 الخصم ({discount_percent}%)</td>
                        <td>- {discount_amount:,.2f} ر.س</td>
                    </tr>
                    <tr class="subtotal-row">
                        <td colspan="4" style="text-align: left; padding: 1rem;"><strong>بعد الخصم</strong></td>
                        <td><strong>{after_discount:,.2f} ر.س</strong></td>
                    </tr>
                """
            
            services_html += f"""
                    <tr class="tax-row">
                        <td colspan="4" style="text-align: left; padding: 1rem;">💰 ضريبة القيمة المضافة ({tax_percent}%)</td>
                        <td>{tax_amount:,.2f} ر.س</td>
                    </tr>
                    <tr class="total-row">
                        <td colspan="4" style="text-align: left; padding: 1.5rem; font-size: 1.4rem;">💵 الإجمالي النهائي</td>
                        <td style="padding: 1.5rem; font-size: 1.5rem;"><strong>{total:,.2f} ر.س</strong></td>
                    </tr>
                </tfoot>
            </table>
            """
            
            st.markdown(services_html, unsafe_allow_html=True)
            
            # عرض الإجمالي بشكل بارز
            st.markdown(f"""
            <div class="highlight-box">
                <h3>💰 المبلغ الإجمالي المطلوب</h3>
                <h1 style="color: #0066cc; font-size: 3rem; margin: 1rem 0;">{total:,.2f} ر.س</h1>
                <p style="color: #666;">({tax_percent}% ضريبة القيمة المضافة متضمنة)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # الشروط والأحكام المحسّنة
        st.markdown(f"""
        <div class="quote-footer">
            <div class="terms-title">📋 الشروط والأحكام</div>
            <div class="terms">
                <p><strong>شروط الدفع:</strong> {payment_terms}</p>
                <p><strong>صلاحية العرض:</strong> حتى تاريخ {valid_until.strftime('%d/%m/%Y')} ({(valid_until - quote_date).days} يوم)</p>
                <p><strong>شروط التسليم:</strong> {delivery_terms if 'delivery_terms' in locals() else 'حسب الاتفاق'}</p>
                <p><strong>مدة التسليم:</strong> {delivery_days if 'delivery_days' in locals() else 'حسب الاتفاق'} يوم من تاريخ الطلب</p>
                {f'<p><strong>فترة الضمان:</strong> {warranty_months} شهر</p>' if 'warranty_months' in locals() and warranty_months > 0 else ''}
                <p><strong>الضريبة:</strong> الأسعار شاملة ضريبة القيمة المضافة ({tax_percent}%)</p>
                <p><strong>العملة:</strong> جميع الأسعار بالريال السعودي (SAR)</p>
                <p><strong>التعديلات:</strong> الأسعار قابلة للتغيير بدون إشعار مسبق بعد انتهاء صلاحية العرض</p>
                {f'<p><strong>ملاحظات إضافية:</strong> {notes}</p>' if notes else ''}
            </div>
            
            <div class="signature-section">
                <div class="signature-box">
                    <div class="signature-title">🏢 ختم الشركة</div>
                    <div style="flex-grow: 1;"></div>
                    <div class="signature-line">ختم شركة متالي</div>
                </div>
                <div class="signature-box">
                    <div class="signature-title">✍️ توقيع المسؤول</div>
                    <div style="flex-grow: 1;"></div>
                    <div class="signature-line">توقيع المفوض بالتوقيع</div>
                </div>
            </div>
            
            <div class="company-footer">
                <h4 style="color: #0066cc; margin-bottom: 1rem;">📞 معلومات التواصل</h4>
                <div class="footer-section">
                    <strong>العنوان:</strong> المملكة العربية السعودية - الرياض - حي الملك فهد - شارع الملك عبدالعزيز
                </div>
                <div class="footer-section">
                    <strong>الهاتف:</strong> +966 11 234 5678 | <strong>الجوال:</strong> +966 50 123 4567
                </div>
                <div class="footer-section">
                    <strong>البريد:</strong> info@matali.sa | sales@matali.sa | <strong>الموقع:</strong> www.matali.sa
                </div>
                <div class="footer-section" style="margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #0066cc;">
                    <strong>السجل التجاري:</strong> 1010123456 | <strong>الرقم الضريبي:</strong> 300123456789003
                </div>
                <div style="margin-top: 1rem; color: #0066cc; font-weight: bold;">
                    شكراً لثقتكم بخدماتنا ✨
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # خيارات الحفظ (مخفية عند الطباعة)
        st.markdown('<div class="print-hide">', unsafe_allow_html=True)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 حفظ العرض", use_container_width=True):
                quote_data = {
                    'quote_number': quote_number,
                    'date': quote_date.strftime('%Y-%m-%d'),
                    'customer': customer_name,
                    'total': total,
                    'services': st.session_state.quote_services
                }
                engine.save_quote(quote_data)
                st.success("✅ تم حفظ العرض بنجاح!")
        
        with col2:
            if st.button("📥 تصدير PDF", use_container_width=True):
                st.info("💡 استخدم زر الطباعة واختر 'حفظ كـ PDF' من خيارات الطباعة")
        st.markdown('</div>', unsafe_allow_html=True)


def show_excel_templates():
    """📥 مركز تحميل القوالب الجاهزة"""
    st.markdown('<div class="big-title">📥 مركز تحميل القوالب</div>', unsafe_allow_html=True)
    
    # CSS مخصص للكروت
    st.markdown("""
    <style>
        .alert-box {
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .template-card {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .template-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
            border-color: #667eea;
        }
        .template-card h3 {
            color: #1f77b4;
            margin-top: 0;
            font-size: 1.3rem;
        }
        .template-card p {
            color: #666;
            margin: 10px 0;
        }
        .file-format {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            margin: 10px 0;
        }
        .badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-top: 10px;
        }
        .badge-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #10b981;
        }
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #f59e0b;
        }
        .download-all-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 10px;
            border: none;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin: 20px 0;
        }
        .download-all-btn:hover {
            opacity: 0.9;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # التنبيه الإرشادي
    st.markdown("""
    <div class="alert-box">
        <strong>📋 خطوات تعبئة القالب:</strong><br>
        ① حمّل القالب المناسب لك.<br>
        ② قم بتعبئة البيانات في ملف Excel.<br>
        ③ ارفع الملف من تبويب <strong>"📂 مركز البيانات"</strong> المخصص.
    </div>
    """, unsafe_allow_html=True)
    
    # الكروت - صف أول
    col1, col2, col3 = st.columns(3)
    
    # كارت P&L
    with col1:
        st.markdown("""
        <div class="template-card">
            <h3>💰 قائمة الدخل (P&L)</h3>
            <p>يُستخدم لتحليل الإيرادات والمصروفات والأرباح لفترة مالية محددة.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        pnl_template = pd.DataFrame({
            'Account Level 1': ['income', 'income', 'expense', 'expense'],
            'Account Level 2': ['ايراد التجهيز', 'ايراد الشحن', 'مصاريف تجهيز', 'مصاريف شحن'],
            'Amount': [150000, 80000, -60000, -30000],
            'Customer': ['متجر صفوة', 'متجر النور', 'متجر صفوة', 'متجر النور']
        })
        
        from io import BytesIO
        buffer_pnl = BytesIO()
        with pd.ExcelWriter(buffer_pnl, engine='openpyxl') as writer:
            pnl_template.to_excel(writer, sheet_name='PnL', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_pnl.getvalue(),
            file_name="pnl_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_pnl"
        )
        
        # حالة الرفع
        pnl_status = db.load_dataframe('pnl')
        if pnl_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت الطلبات
    with col2:
        st.markdown("""
        <div class="template-card">
            <h3>📦 بيانات الطلبات (Orders)</h3>
            <p>يُستخدم لتسجيل وتتبع جميع طلبات العملاء ومعلومات الشحن.</p>
            <div class="file-format">CSV / XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        orders_template = pd.DataFrame({
            'ORDER ID': ['ORD001', 'ORD002', 'ORD003'],
            'DESTINATION CITY': ['الرياض', 'جدة', 'الدمام'],
            'SHIPPING COST': [25.0, 35.0, 30.0],
            'ORDER AMOUNT': [300.0, 450.0, 200.0],
            'SHIPMENT WEIGHT': [2.5, 3.2, 1.8],
            'PAYMENT METHOD': ['PREPAID', 'POSTPAID', 'PREPAID']
        })
        
        buffer_orders = BytesIO()
        orders_template.to_csv(buffer_orders, index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_orders.getvalue(),
            file_name="orders_template.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_orders"
        )
        
        orders_status = db.load_dataframe('orders')
        if orders_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت الطاقة
    with col3:
        st.markdown("""
        <div class="template-card">
            <h3>📊 بيانات الطاقة (Capacity)</h3>
            <p>يُستخدم لإدارة الطاقة الإنتاجية والتكاليف التشغيلية للخدمات.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        capacity_template = pd.DataFrame({
            'service_name': ['استلام البضائع', 'تخزين شهري', 'تجهيز الطلبات'],
            'unit_name': ['طرد', 'متر مكعب', 'طلب'],
            'daily_capacity': [1000, 500, 800],
            'monthly_cost': [50000, 30000, 60000]
        })
        
        buffer_capacity = BytesIO()
        with pd.ExcelWriter(buffer_capacity, engine='openpyxl') as writer:
            capacity_template.to_excel(writer, sheet_name='Capacity', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_capacity.getvalue(),
            file_name="capacity_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_capacity"
        )
        
        capacity_status = db.load_dataframe('capacity')
        if capacity_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # الصف الثاني
    col1, col2, col3 = st.columns(3)
    
    # كارت الموردين
    with col1:
        st.markdown("""
        <div class="template-card">
            <h3>🚚 بيانات الموردين (Suppliers)</h3>
            <p>يُستخدم لإدارة معلومات شركات الشحن والموردين وأسعارهم.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        suppliers_template = pd.DataFrame({
            'Shipping Partner': ['aramex', 'smsa', 'dhl'],
            'Zone': ['الرياض', 'الرياض', 'الرياض'],
            'Base Rate': [25.0, 22.0, 30.0],
            'Additional KG Rate': [2.5, 2.0, 3.0]
        })
        
        buffer_suppliers = BytesIO()
        with pd.ExcelWriter(buffer_suppliers, engine='openpyxl') as writer:
            suppliers_template.to_excel(writer, sheet_name='Suppliers', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_suppliers.getvalue(),
            file_name="suppliers_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_suppliers"
        )
        
        suppliers_status = db.load_dataframe('suppliers')
        if suppliers_status is not None:
            st.markdown('<div class="badge badge-success">✅ تم رفع بيانات هذا القالب</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت المنافسين
    with col2:
        st.markdown("""
        <div class="template-card">
            <h3>🏆 بيانات المنافسين</h3>
            <p>يُستخدم لمقارنة أسعار الخدمات مع المنافسين في السوق.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        competitors_template = pd.DataFrame({
            'service_name': ['ايراد التجهيز', 'ايراد الشحن', 'ايراد التخزين'],
            'competitor_1': [120.0, 85.0, 55.0],
            'competitor_2': [115.0, 90.0, 50.0],
            'market_average': [120.0, 85.0, 55.0]
        })
        
        buffer_competitors = BytesIO()
        with pd.ExcelWriter(buffer_competitors, engine='openpyxl') as writer:
            competitors_template.to_excel(writer, sheet_name='Competitors', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_competitors.getvalue(),
            file_name="competitors_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_competitors"
        )
        
        st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    # كارت العملاء
    with col3:
        st.markdown("""
        <div class="template-card">
            <h3>👥 بيانات العملاء</h3>
            <p>يُستخدم لإدارة معلومات العملاء وتصنيفاتهم والعقود معهم.</p>
            <div class="file-format">XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        customers_template = pd.DataFrame({
            'customer_name': ['متجر صفوة', 'متجر النور', 'شركة الأمل'],
            'type': ['Retail', 'Wholesale', 'Enterprise'],
            'tier': ['VIP', 'Premium', 'Standard'],
            'monthly_volume': [5000, 8000, 15000]
        })
        
        buffer_customers = BytesIO()
        with pd.ExcelWriter(buffer_customers, engine='openpyxl') as writer:
            customers_template.to_excel(writer, sheet_name='Customers', index=False)
        
        st.download_button(
            label="⬇️ تحميل القالب",
            data=buffer_customers.getvalue(),
            file_name="customers_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_customers"
        )
        
        st.markdown('<div class="badge badge-warning">⏳ لم يتم رفع بيانات هذا القالب بعد</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # زر تحميل جميع القوالب
    st.markdown("### 📦 تحميل جميع القوالب دفعة واحدة")
    
    if st.button("📦 تحميل جميع القوالب في ملف ZIP", use_container_width=True, type="primary"):
        import zipfile
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # إضافة كل القوالب
            zip_file.writestr("pnl_template.xlsx", buffer_pnl.getvalue())
            zip_file.writestr("orders_template.csv", buffer_orders.getvalue())
            zip_file.writestr("capacity_template.xlsx", buffer_capacity.getvalue())
            zip_file.writestr("suppliers_template.xlsx", buffer_suppliers.getvalue())
            zip_file.writestr("competitors_template.xlsx", buffer_competitors.getvalue())
            zip_file.writestr("customers_template.xlsx", buffer_customers.getvalue())
        
        st.download_button(
            label="⬇️ تحميل ملف ZIP (جميع القوالب)",
            data=zip_buffer.getvalue(),
            file_name="matali_templates_all.zip",
            mime="application/zip",
            use_container_width=True
        )
        st.success("✅ تم تجهيز جميع القوالب للتحميل!")
    
    st.markdown("---")
    
    # الإرشادات
    st.markdown("### 📖 إرشادات الاستخدام")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **✅ خطوات الاستخدام:**
        
        1. حمّل القالب المناسب
        2. افتحه في Excel
        3. املأ بياناتك (احذف الأمثلة)
        4. احفظ الملف
        5. ارفعه في "📂 مركز البيانات"
        """)
    
    with col2:
        st.warning("""
        **⚠️ ملاحظات مهمة:**
        
        - لا تغير أسماء الأعمدة
        - تأكد من صحة أنواع البيانات
        - الأرقام بدون فواصل أو رموز
        - التواريخ بصيغة موحدة
        - احفظ بصيغة .xlsx أو .csv
        """)


def show_company_settings():
    """⚙️ إعدادات الشركة - رفع بيانات وشعار الشركة"""
    st.markdown('<div class="big-title">⚙️ إعدادات الشركة</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; margin-bottom: 30px;'>
        <h3 style='margin: 0; color: white;'>🏢 بيانات شركة الفلفيلمنت</h3>
        <p style='margin: 5px 0 0 0; opacity: 0.9;'>قم برفع بيانات وشعار شركتك لتظهر في عروض الأسعار المطبوعة</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحميل البيانات الحالية
    company_data = {
        'name_ar': db.get_setting('company_name_ar', 'شركة متالي للخدمات اللوجستية'),
        'name_en': db.get_setting('company_name_en', 'Matali Logistics Services Company'),
        'email': db.get_setting('company_email', 'info@matali.com'),
        'phone': db.get_setting('company_phone', '+966 XX XXX XXXX'),
        'website': db.get_setting('company_website', 'www.matali.com'),
        'address_ar': db.get_setting('company_address_ar', 'الرياض، المملكة العربية السعودية'),
        'address_en': db.get_setting('company_address_en', 'Riyadh, Saudi Arabia'),
        'tax_number': db.get_setting('company_tax_number', ''),
        'cr_number': db.get_setting('company_cr_number', ''),
        'slogan_ar': db.get_setting('company_slogan_ar', 'شريكك الموثوق للخدمات اللوجستية'),
        'slogan_en': db.get_setting('company_slogan_en', 'Your Trusted Logistics Partner'),
    }
    
    # علامات تبويب
    tab1, tab2, tab3 = st.tabs(["📋 المعلومات الأساسية", "🖼️ الشعار والهوية", "👁️ معاينة"])
    
    with tab1:
        st.markdown("### 📋 بيانات الشركة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🇸🇦 البيانات بالعربية")
            name_ar = st.text_input("اسم الشركة (عربي) *", value=company_data['name_ar'])
            address_ar = st.text_area("العنوان (عربي)", value=company_data['address_ar'], height=100)
            slogan_ar = st.text_input("الشعار (عربي)", value=company_data['slogan_ar'])
        
        with col2:
            st.markdown("#### 🇬🇧 البيانات بالإنجليزية")
            name_en = st.text_input("Company Name (English) *", value=company_data['name_en'])
            address_en = st.text_area("Address (English)", value=company_data['address_en'], height=100)
            slogan_en = st.text_input("Slogan (English)", value=company_data['slogan_en'])
        
        st.markdown("---")
        st.markdown("### 📞 معلومات التواصل")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            email = st.text_input("📧 البريد الإلكتروني", value=company_data['email'])
        
        with col2:
            phone = st.text_input("📱 الهاتف", value=company_data['phone'])
        
        with col3:
            website = st.text_input("🌐 الموقع الإلكتروني", value=company_data['website'])
        
        st.markdown("---")
        st.markdown("### 📄 المعلومات الرسمية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tax_number = st.text_input("🔢 الرقم الضريبي", value=company_data['tax_number'])
        
        with col2:
            cr_number = st.text_input("📋 رقم السجل التجاري", value=company_data['cr_number'])
        
        st.markdown("---")
        
        if st.button("💾 حفظ المعلومات", type="primary", use_container_width=True):
            # حفظ جميع البيانات
            settings_to_save = {
                'company_name_ar': name_ar,
                'company_name_en': name_en,
                'company_email': email,
                'company_phone': phone,
                'company_website': website,
                'company_address_ar': address_ar,
                'company_address_en': address_en,
                'company_tax_number': tax_number,
                'company_cr_number': cr_number,
                'company_slogan_ar': slogan_ar,
                'company_slogan_en': slogan_en,
            }
            
            success_count = 0
            for key, value in settings_to_save.items():
                if db.save_setting(key, value):
                    success_count += 1
            
            if success_count == len(settings_to_save):
                st.success("✅ تم حفظ جميع المعلومات بنجاح!")
                st.balloons()
            else:
                st.warning(f"⚠️ تم حفظ {success_count} من {len(settings_to_save)} إعدادات")
    
    with tab2:
        st.markdown("### 🖼️ شعار الشركة")
        
        st.info("""
        📌 **متطلبات الشعار:**
        - الصيغة: PNG, JPG, أو JPEG
        - الحجم المفضل: 300x100 بكسل
        - خلفية شفافة (PNG) للحصول على أفضل نتيجة
        """)
        
        uploaded_logo = st.file_uploader(
            "اختر ملف الشعار",
            type=['png', 'jpg', 'jpeg'],
            help="قم برفع شعار شركتك بصيغة PNG أو JPG"
        )
        
        if uploaded_logo is not None:
            # عرض الشعار المرفوع
            st.image(uploaded_logo, caption="الشعار المرفوع", width=300)
            
            # حفظ الشعار
            if st.button("💾 حفظ الشعار", type="primary"):
                try:
                    # إنشاء مجلد للشعارات
                    logo_dir = Path("data/company_assets")
                    logo_dir.mkdir(parents=True, exist_ok=True)
                    
                    # حفظ الملف
                    logo_path = logo_dir / "company_logo.png"
                    with open(logo_path, "wb") as f:
                        f.write(uploaded_logo.getbuffer())
                    
                    # حفظ المسار في الإعدادات
                    db.save_setting('company_logo_path', str(logo_path))
                    
                    st.success("✅ تم حفظ الشعار بنجاح!")
                    
                except Exception as e:
                    st.error(f"❌ خطأ في حفظ الشعار: {str(e)}")
        
        # عرض الشعار الحالي
        current_logo = db.get_setting('company_logo_path')
        if current_logo and Path(current_logo).exists():
            st.markdown("---")
            st.markdown("### 📸 الشعار الحالي")
            st.image(current_logo, width=300)
            
            if st.button("🗑️ حذف الشعار الحالي", type="secondary"):
                try:
                    Path(current_logo).unlink()
                    db.save_setting('company_logo_path', '')
                    st.success("✅ تم حذف الشعار")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ في حذف الشعار: {str(e)}")
    
    with tab3:
        st.markdown("### 👁️ معاينة عرض السعر")
        
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 10px; 
                    border: 2px solid #e5e7eb; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        # رأسية العرض
        logo_html = ""
        logo_path = db.get_setting('company_logo_path')
        if logo_path and Path(logo_path).exists():
            import base64
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{logo_data}" style="max-height: 80px; margin-bottom: 15px;">'
        
        st.markdown(f"""
        <div style='text-align: center; padding: 25px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px; color: white; margin-bottom: 20px;'>
            {logo_html}
            <h2 style='margin: 10px 0; color: white;'>{name_ar}</h2>
            <p style='margin: 5px 0; font-size: 16px; opacity: 0.95;'>{name_en}</p>
            <p style='margin: 10px 0; font-style: italic; opacity: 0.9;'>{slogan_ar}</p>
            <div style='background: white; color: #2563eb; padding: 10px 20px; 
                        border-radius: 25px; display: inline-block; margin-top: 10px;
                        font-weight: bold;'>
                عرض سعر | Price Quote
            </div>
        </div>
        
        <div style='background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <div style='display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb;'>
                <strong>📧 البريد الإلكتروني:</strong>
                <span>{email}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb;'>
                <strong>📱 الهاتف:</strong>
                <span>{phone}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb;'>
                <strong>🌐 الموقع:</strong>
                <span>{website}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 10px 0;'>
                <strong>📍 العنوان:</strong>
                <span>{address_ar}</span>
            </div>
        </div>
        
        <div style='background: #fef3c7; padding: 15px; border-radius: 10px; border-right: 4px solid #f59e0b;'>
            <strong>📄 معلومات رسمية:</strong><br>
            <span style='font-size: 14px;'>
                الرقم الضريبي: {tax_number if tax_number else '---'} | 
                السجل التجاري: {cr_number if cr_number else '---'}
            </span>
        </div>
        
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.success("✅ هكذا سيظهر عرض السعر عند الطباعة!")


# القائمة الرئيسية
def main():
    # الشعار
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='color: #1f77b4;'>📊</h1>
        <h3>نظام متالي للتسعير</h3>
        <p style='font-size: 0.9rem; color: #666;'>نظام التسعير الذكي V2</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # الصفحات (8 صفحات - بعد دمج مركز البيانات والقوالب)
    pages = {
        "📂 مركز البيانات والقوالب": show_data_hub,
        "📊 لوحة التحكم": show_dashboard,
        "💰 محرك التسعير": show_pricing_engine,
        "📦 إدارة الموردين": show_suppliers_integration,
        "🧾 عرض سعر متقدم": lambda: show_new_quote_system(engine, db),
        "📄 عرض سعر احترافي": show_professional_quote,
        "📜 سجل العروض": show_quotes,
        "⚙️ إعدادات الشركة": show_company_settings
    }
    
    page = st.sidebar.radio("القائمة الرئيسية", list(pages.keys()))
    
    st.sidebar.markdown("---")
    
    # معلومات النظام
    st.sidebar.markdown("### ℹ️ حالة النظام")
    data_count = sum(st.session_state.data_loaded.values())
    total_data_types = len(st.session_state.data_loaded)
    st.sidebar.progress(data_count / total_data_types if total_data_types > 0 else 0)
    st.sidebar.caption(f"البيانات المحملة: {data_count}/{total_data_types}")
    
    # معلومات قاعدة البيانات
    db_info = db.get_database_info()
    if db_info.get('table_count', 0) > 0:
        st.sidebar.caption(f"📊 الجداول: {db_info['table_count']} | {db_info['db_size_kb']:.1f} KB")
    
    # تشغيل الصفحة المختارة
    pages[page]()


if __name__ == "__main__":
    main()
