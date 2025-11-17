"""
نظام عرض السعر الجديد المتكامل
يدمج مع قاعدة البيانات ومحرك التسعير الموحد
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from unified_pricing_engine import UnifiedPricingEngine


def calculate_inclusive_prices(edited_df, avg_skus, included_skus):
    """حساب السعر الشامل من الجدول اليدوي"""
    def get_price(service_name):
        row = edited_df[edited_df["الخدمة"] == service_name]
        return float(row["السعر بعد الخصم"].iloc[0]) if not row.empty else 0.0
    
    pick_base = get_price("تجهيز الطلب الأساسي")
    pick_extra = get_price("تجهيز منتجات إضافية")
    pack_std = get_price("التغليف العادي")
    ship_in = get_price("الشحن داخل الرياض")
    ship_out = get_price("الشحن خارج الرياض")
    
    extra_skus_cost = max(avg_skus - included_skus, 0) * pick_extra
    inside = pick_base + extra_skus_cost + pack_std + ship_in
    outside = pick_base + extra_skus_cost + pack_std + ship_out
    
    return inside, outside


def show_new_quote_system(engine: UnifiedPricingEngine, db):
    """عرض السعر الجديد المتكامل"""
    
    st.markdown('<div class="big-title">🧾 إنشاء عرض سعر جديد</div>', unsafe_allow_html=True)
    
    # التحقق من البيانات المحملة
    data_status_cols = st.columns(4)
    
    with data_status_cols[0]:
        pnl_ok = engine.profit_margins is not None and len(engine.profit_margins) > 0
        st.metric("P&L", "✅ محملة" if pnl_ok else "❌ غير محملة")
    
    with data_status_cols[1]:
        capacity_ok = engine.capacity_data is not None
        st.metric("الطاقة", "✅ محملة" if capacity_ok else "❌ غير محملة")
    
    with data_status_cols[2]:
        orders_ok = engine.orders_data is not None
        st.metric("الطلبات", "✅ محملة" if orders_ok else "❌ غير محملة")
    
    with data_status_cols[3]:
        suppliers_ok = engine.suppliers_data is not None
        st.metric("الموردين", "✅ محملة" if suppliers_ok else "❌ غير محملة")
    
    st.markdown("---")
    
    # ========================
    # بيانات العميل المشتركة
    # ========================
    st.markdown('<div class="section-header"><h2>📋 بيانات العميل</h2></div>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            client_name = st.text_input(
                "اسم المتجر / العميل *",
                placeholder="أدخل اسم العميل الكامل...",
                help="اسم العميل أو المتجر كما سيظهر في عرض السعر"
            )
        
        with col2:
            tier = st.selectbox(
                "تصنيف العميل *",
                ["Standard", "Preferred", "Strategic"],
                help="اختر مستوى العميل للحصول على الخصومات المناسبة"
            )
            discount_percent_str = {"Standard": "0%", "Preferred": "10%", "Strategic": "20%"}[tier]
            st.markdown(f'<span style="background:#ffd700; padding:0.25rem 0.5rem; border-radius:15px; font-weight:bold;">خصم: {discount_percent_str}</span>', unsafe_allow_html=True)
        
        with col3:
            free_pallets = st.number_input(
                "عدد الطبلات المجانية شهرياً",
                min_value=0,
                step=5,
                value=0,
                help="عدد الطبلات التي لا يتم احتساب رسوم تخزين عليها"
            )
    
    with st.container():
        col4, col5, col6 = st.columns(3)
        
        with col4:
            orders_total = st.number_input(
                "إجمالي الطلبات الشهرية *",
                min_value=0,
                step=50,
                value=1000,
                help="إجمالي عدد الطلبات المتوقعة شهريًا"
            )
        
        with col5:
            orders_riyadh = st.number_input(
                "الطلبات داخل الرياض *",
                min_value=0,
                step=50,
                value=600,
                help="عدد الطلبات المخصصة للتوصيل داخل الرياض"
            )
        
        with col6:
            avg_skus = st.number_input(
                "متوسط عدد المنتجات (SKUs) في الطلب *",
                min_value=1.0,
                max_value=50.0,
                step=0.5,
                value=3.0,
                help="متوسط عدد المنتجات المختلفة في كل طلب"
            )
    
    with st.container():
        col7, col8 = st.columns(2)
        
        with col7:
            included_skus = st.slider(
                "عدد الـ SKUs المشمولة في السعر الأساسي للتجهيز",
                min_value=1,
                max_value=10,
                value=4,
                help="عدد المنتجات المشمولة في السعر الأساسي لتجهيز الطلب"
            )
        
        with col8:
            st.write("**وحدة تسعير استلام المخزون**")
            inbound_unit = st.radio(
                "اختر الوحدة",
                ["طبلية", "SKU"],
                horizontal=True,
                help="اختر طريقة احتساب تكلفة استلام المخزون",
                label_visibility="collapsed"
            )
    
    orders_outside = max(orders_total - orders_riyadh, 0)
    
    if orders_total > 0:
        st.info(
            f"**ملخص الطلبات:** إجمالي {orders_total:,} طلب → داخل الرياض: {orders_riyadh:,} "
            f"({orders_riyadh/orders_total*100:.1f}%) | خارج الرياض: {orders_outside:,} "
            f"({orders_outside/orders_total*100:.1f}%)"
        )
    
    st.markdown("---")
    
    # ========================
    # Tabs: يدوي / ذكي
    # ========================
    tab_manual, tab_smart = st.tabs(["📝 عرض سعر يدوي", "🤖 تسعير ذكي تلقائي"])
    
    # ========================
    # صفحة عرض سعر يدوي
    # ========================
    with tab_manual:
        st.markdown('<div class="section-header"><h2>💰 جدول تسعير الخدمات (يدوي)</h2></div>', unsafe_allow_html=True)
        
        # بيانات الخدمات
        services_data = {
            "خدمات التجهيز والتخزين": [
                ["PICK_BASE", "تجهيز الطلب الأساسي", f"يشمل حتى {included_skus} SKU", 5.0,
                 f"تجهيز كامل للطلب يشمل حتى {included_skus} منتج مختلف"],
                ["PICK_EXTRA", "تجهيز منتجات إضافية", "لكل SKU إضافي", 0.30,
                 "أي منتج إضافي عن العدد الأساسي المتفق عليه"],
                ["STOR_PALLET", "تخزين الطبلات", "طبلية / يوم", 3.0,
                 f"التخزين اليومي للطبلات (أول {free_pallets} طبلية مجانًا شهريًا)"],
                ["STOR_SHELF", "تخزين الرفوف", "شيلف / يوم", 1.5,
                 "لتخزين المنتجات المتوسطة الحجم على الرفوف"],
                ["STOR_BIN", "تخزين الصناديق", "بن / يوم", 0.5,
                 "لتخزين المنتجات صغيرة الحجم في صناديق مخصصة"],
            ],
            "خدمات الشحن والتوصيل": [
                ["SHIP_RIYADH", "الشحن داخل الرياض", "طلب", 15.0, "توصيل الطلبات داخل نطاق مدينة الرياض"],
                ["SHIP_OUTSIDE", "الشحن خارج الرياض", "طلب", 20.0, "توصيل الطلبات للمدن الأخرى داخل المملكة"],
                ["EXTRA_WEIGHT", "وزن إضافي", "كجم إضافي", 2.0,
                 "لكل كيلو جرام إضافي بعد الحد المسموح (15 كجم)"],
            ],
            "خدمات الدعم والإضافية": [
                ["IN_PALLET", "استلام المخزون - طبلية", "طبلية", 10.0, "استلام وفحص وتدقيق الطبلات الواردة"],
                ["IN_SKU", "استلام المخزون - منتج", "SKU", 0.10, "استلام وفحص كل صنف على حدة"],
                ["PACK_STD", "التغليف العادي", "طلب", 0.35, "تغليف قياسي وفق معايير متالي برو"],
                ["PACK_PREMIUM", "تغليف مميز", "طلب", 2.0, "تغليف هدايا أو تغليف خاص بالعلامة التجارية"],
                ["RETURN_ORDER", "إدارة المرتجعات", "طلب مرتجع", 5.0, "معالجة كاملة للطلبات المرتجعة"],
                ["COD_FEE", "تحصيل الدفع نقداً", "طلب COD", 5.0, "عمولة تحصيل المبالغ نقداً عند التسليم"],
                ["GATEWAY_FEE", "عمولة الدفع الإلكتروني", "% من قيمة الطلب", 2.2,
                 "عمولة معالجة المدفوعات الإلكترونية"],
            ]
        }
        
        all_services = []
        for category, services in services_data.items():
            for service in services:
                service.append(category)
                all_services.append(service)
        
        df_services = pd.DataFrame(
            all_services,
            columns=["الكود", "الخدمة", "وحدة التسعير", "السعر الأساسي", "وصف الخدمة", "الفئة"]
        )
        
        discount_map = {"Standard": 0.0, "Preferred": 0.10, "Strategic": 0.20}
        discount_rate = discount_map[tier]
        
        df_services["نسبة الخصم %"] = 0.0
        picking_mask = df_services["الكود"].isin(["PICK_BASE", "PICK_EXTRA"])
        shipping_mask = df_services["الكود"].isin(["SHIP_RIYADH", "SHIP_OUTSIDE"])
        
        df_services.loc[picking_mask, "نسبة الخصم %"] = discount_rate * 100
        df_services.loc[shipping_mask, "نسبة الخصم %"] = discount_rate * 100
        
        df_services["السعر بعد الخصم"] = df_services["السعر الأساسي"] * (1 - df_services["نسبة الخصم %"] / 100)
        
        if inbound_unit == "طبلية":
            display_df = df_services[df_services["الكود"] != "IN_SKU"].copy()
        else:
            display_df = df_services[df_services["الكود"] != "IN_PALLET"].copy()
        
        # تبويبات داخلية
        manual_tab1, manual_tab2, manual_tab3 = st.tabs(["🎯 جميع الخدمات", "📊 ملخص التكاليف", "📈 مقارنة الأسعار"])
        
        with manual_tab1:
            st.subheader("تسعير الخدمات (قابل للتعديل)")
            
            edited_df = st.data_editor(
                display_df[["الخدمة", "وحدة التسعير", "السعر الأساسي", "نسبة الخصم %", "السعر بعد الخصم", "وصف الخدمة"]],
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "نسبة الخصم %": st.column_config.NumberColumn(format="%.1f %%"),
                    "السعر الأساسي": st.column_config.NumberColumn(format="%.2f ﷼"),
                    "السعر بعد الخصم": st.column_config.NumberColumn(format="%.2f ﷼"),
                },
                key="manual_editor_new"
            )
        
        with manual_tab2:
            st.subheader("ملخص التكاليف الشهرية المتوقعة")
            
            if edited_df is not None:
                def get_price(service_name):
                    row = edited_df[edited_df["الخدمة"] == service_name]
                    return float(row["السعر بعد الخصم"].iloc[0]) if not row.empty else 0.0
                
                monthly_costs = []
                
                pick_base_cost = get_price("تجهيز الطلب الأساسي") * orders_total
                extra_skus = max(avg_skus - included_skus, 0)
                pick_extra_cost = get_price("تجهيز منتجات إضافية") * extra_skus * orders_total
                
                ship_riyadh_cost = get_price("الشحن داخل الرياض") * orders_riyadh
                ship_outside_cost = get_price("الشحن خارج الرياض") * orders_outside
                
                monthly_costs.extend([
                    ["تجهيز الطلبات الأساسي", pick_base_cost],
                    ["تجهيز المنتجات الإضافية", pick_extra_cost],
                    ["شحن داخل الرياض", ship_riyadh_cost],
                    ["شحن خارج الرياض", ship_outside_cost]
                ])
                
                cost_df = pd.DataFrame(monthly_costs, columns=["البند", "التكلفة الشهرية"])
                fig = px.pie(cost_df, values="التكلفة الشهرية", names="البند",
                             title="توزيع التكاليف الشهرية المتوقعة")
                st.plotly_chart(fig, use_container_width=True)
                
                total_monthly = cost_df["التكلفة الشهرية"].sum()
                st.metric("إجمالي التكاليف الشهرية المتوقعة", f"{total_monthly:,.2f} ريال")
        
        with manual_tab3:
            st.subheader("مقارنة الأسعار قبل وبعد الخصم")
            
            comp_df = df_services[["الخدمة", "السعر الأساسي", "السعر بعد الخصم"]].melt(
                id_vars=["الخدمة"],
                var_name="نوع السعر",
                value_name="القيمة"
            )
            fig = px.bar(comp_df, x="الخدمة", y="القيمة", color="نوع السعر",
                         barmode="group", title="مقارنة الأسعار قبل وبعد الخصم")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # السعر الشامل + تحليل الربح
        st.markdown('<div class="section-header"><h2>🎯 السعر الشامل + هامش الربح</h2></div>', unsafe_allow_html=True)
        
        all_inclusive = st.checkbox(
            "تفعيل السعر الشامل لكل طلب",
            help="السعر الشامل يشمل التجهيز + التغليف العادي + الشحن"
        )
        
        if all_inclusive and edited_df is not None:
            st.success("✅ تم حساب السعر الشامل من الجدول اليدوي")
            
            inside_price, outside_price = calculate_inclusive_prices(edited_df, avg_skus, included_skus)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("السعر الشامل للطلب داخل الرياض", f"{inside_price:,.2f} ريال")
            with col2:
                st.metric("السعر الشامل للطلب خارج الرياض", f"{outside_price:,.2f} ريال")
            
            # تحليل هامش الربح من engine
            if pnl_ok and capacity_ok:
                # حساب التكلفة من المحرك
                sample_quote = engine.generate_quote("عميل عينة", "fulfillment", orders_total, {})
                
                if sample_quote and 'cost_breakdown' in sample_quote:
                    cost_per_order = sample_quote['cost_breakdown'].get('cost_per_order', 0)
                    
                    margin_in = inside_price - cost_per_order
                    margin_out = outside_price - cost_per_order
                    
                    margin_in_pct = (margin_in / inside_price * 100) if inside_price > 0 else 0
                    margin_out_pct = (margin_out / outside_price * 100) if outside_price > 0 else 0
                    
                    st.subheader("تحليل هامش الربح بناءً على التكلفة الفعلية")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("تكلفة الطلب (فعلية)", f"{cost_per_order:,.2f} ريال")
                    with c2:
                        st.metric("هامش الربح - داخل الرياض", f"{margin_in:,.2f} ريال", f"{margin_in_pct:,.1f} %")
                    with c3:
                        st.metric("هامش الربح - خارج الرياض", f"{margin_out:,.2f} ريال", f"{margin_out_pct:,.1f} %")
        
        # حفظ عرض السعر
        st.markdown("---")
        st.markdown('<div class="section-header"><h2>📄 حفظ عرض السعر</h2></div>', unsafe_allow_html=True)
        
        if st.button("💾 حفظ عرض السعر (يدوي)", type="primary", use_container_width=True):
            if not client_name:
                st.error("⚠️ يرجى إدخال اسم العميل أولاً")
            else:
                # حفظ في قاعدة البيانات
                quote_data = {
                    'customer': client_name,
                    'tier': tier,
                    'service_type': 'manual',
                    'orders_total': orders_total,
                    'orders_riyadh': orders_riyadh,
                    'avg_skus': avg_skus,
                    'grand_total': inside_price * orders_riyadh + outside_price * orders_outside if all_inclusive else 0,
                    'created_at': datetime.now().isoformat()
                }
                
                quote_id = db.save_quote(quote_data)
                if quote_id:
                    st.success(f"✅ تم حفظ عرض السعر برقم: {quote_id}")
                else:
                    st.error("❌ فشل حفظ عرض السعر")
    
    # ========================
    # صفحة تسعير ذكي
    # ========================
    with tab_smart:
        st.markdown('<div class="section-header"><h2>🤖 تسعير ذكي بناءً على البيانات الفعلية</h2></div>', unsafe_allow_html=True)
        
        if not (pnl_ok and capacity_ok):
            st.error("⚠️ يجب تحميل بيانات P&L والطاقة أولاً من مركز البيانات")
            st.info("""
            **💡 ملاحظة هامة:**
            - التسعير الذكي يعتمد على بيانات P&L الفعلية لحساب التكلفة الحقيقية
            - يجب أن تحتوي بيانات P&L على إجمالي المصروفات الشهرية
            - كما يجب رفع بيانات الطلبات لمعرفة عدد الطلبات الفعلي
            """)
        else:
            # عرض معلومات توضيحية
            with st.expander("ℹ️ كيف يعمل التسعير الذكي؟", expanded=False):
                st.markdown("""
                **📊 طريقة الحساب:**
                
                1. **التكلفة الفعلية:**
                   - يتم حساب التكلفة من بيانات P&L الفعلية
                   - المعادلة: `إجمالي المصروفات ÷ عدد الطلبات التاريخية`
                   - مثال: إذا كانت المصروفات 60,000 ر.س وعدد الطلبات 16,000 = 3.75 ر.س للطلب
                
                2. **هامش الربح:**
                   - يتم حساب هامش الربح من بيانات P&L التاريخية
                   - النطاق: 20% - 35%
                   - يتم تعديله تلقائياً حسب حجم الطلبات
                
                3. **السعر النهائي:**
                   - المعادلة: `التكلفة ÷ (1 - هامش الربح)`
                   - مثال: 3.75 ÷ (1 - 0.25) = 5 ر.س
                
                **⚠️ مهم:** إذا لم تكن قد رفعت بيانات الطلبات، قد تكون الأسعار غير دقيقة!
                """)
            
            # توليد عرض سعر ذكي
            quote = engine.generate_quote(
                customer_name=client_name or "عميل جديد",
                service_type="fulfillment",
                monthly_volume=orders_total,
                requirements={}
            )
            
            if quote:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("السعر المقترح | Proposed Price", f"{quote.get('price', 0):,.2f} ريال")
                with col2:
                    st.metric("التكلفة الفعلية | Actual Cost", f"{quote.get('cost_breakdown', {}).get('cost_per_order', 0):,.2f} ريال")
                with col3:
                    margin = quote.get('price', 0) - quote.get('cost_breakdown', {}).get('cost_per_order', 0)
                    margin_pct = (margin / quote.get('price', 1) * 100) if quote.get('price', 0) > 0 else 0
                    st.metric("هامش الربح | Profit Margin", f"{margin:,.2f} ريال", f"{margin_pct:.1f}%")
                
                # تفاصيل التكلفة
                if 'cost_breakdown' in quote:
                    st.markdown("#### 📊 تفاصيل التكلفة")
                    
                    # إنشاء DataFrame مع أسماء عربي/إنجليزي
                    breakdown_data = {
                        'البيان | Item': [
                            'التكلفة الإجمالية | Cost Per Order',
                            'تكلفة الشحن | Shipping Cost',
                            'تكلفة التجهيز | Fulfillment Cost',
                            'تكلفة التغليف | Packaging Cost',
                            'التكاليف العامة | Overhead Cost',
                            'هامش الربح المستهدف | Target Margin',
                            'الربح لكل طلب | Profit Per Order'
                        ],
                        'القيمة | Value': [
                            f"{quote['cost_breakdown'].get('cost_per_order', 0):,.2f} ريال",
                            f"{quote['cost_breakdown'].get('shipping_cost', 0):,.2f} ريال",
                            f"{quote['cost_breakdown'].get('fulfillment_cost', 0):,.2f} ريال",
                            f"{quote['cost_breakdown'].get('packaging_cost', 0):,.2f} ريال",
                            f"{quote['cost_breakdown'].get('overhead_cost', 0):,.2f} ريال",
                            f"{quote['cost_breakdown'].get('target_margin', 0):.1f}%",
                            f"{quote['cost_breakdown'].get('profit_per_order', 0):,.2f} ريال"
                        ]
                    }
                    breakdown_df = pd.DataFrame(breakdown_data)
                    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
                
                # أزرار الحفظ والطباعة
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 حفظ عرض السعر (ذكي)", type="primary", use_container_width=True):
                        if not client_name:
                            st.error("⚠️ يرجى إدخال اسم العميل أولاً")
                        else:
                            quote_data = {
                                'customer': client_name,
                                'tier': tier,
                                'service_type': 'smart',
                                'orders_total': orders_total,
                                'price': quote.get('price', 0),
                                'grand_total': quote.get('price', 0) * orders_total,
                                'created_at': datetime.now().isoformat(),
                                'quote_details': quote
                            }
                            
                            quote_id = db.save_quote(quote_data)
                            if quote_id:
                                st.success(f"✅ تم حفظ عرض السعر الذكي برقم: {quote_id}")
                            else:
                                st.error("❌ فشل حفظ عرض السعر")
                
                with col2:
                    if st.button("🖨️ طباعة عرض السعر (ذكي)", type="secondary", use_container_width=True):
                        if not client_name:
                            st.error("⚠️ يرجى إدخال اسم العميل أولاً")
                        else:
                            # إنشاء HTML لعرض السعر الذكي
                            html_content = f"""
                            <html dir="rtl">
                            <head>
                                <meta charset="utf-8">
                                <style>
                                    body {{
                                        font-family: Arial, sans-serif;
                                        direction: rtl;
                                        padding: 20px;
                                    }}
                                    .header {{
                                        text-align: center;
                                        border-bottom: 3px solid #2563eb;
                                        padding-bottom: 20px;
                                        margin-bottom: 30px;
                                    }}
                                    .company-name {{
                                        font-size: 32px;
                                        font-weight: bold;
                                        color: #1e40af;
                                        margin-bottom: 10px;
                                    }}
                                    .quote-title {{
                                        font-size: 24px;
                                        color: #374151;
                                        margin-top: 10px;
                                    }}
                                    .info-section {{
                                        background: #f3f4f6;
                                        padding: 15px;
                                        border-radius: 8px;
                                        margin: 20px 0;
                                    }}
                                    .info-row {{
                                        display: flex;
                                        justify-content: space-between;
                                        padding: 8px 0;
                                        border-bottom: 1px solid #e5e7eb;
                                    }}
                                    .info-label {{
                                        font-weight: bold;
                                        color: #374151;
                                    }}
                                    .info-value {{
                                        color: #1f2937;
                                    }}
                                    .pricing-section {{
                                        margin: 30px 0;
                                    }}
                                    .price-box {{
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        padding: 20px;
                                        border-radius: 12px;
                                        text-align: center;
                                        margin: 20px 0;
                                    }}
                                    .price-label {{
                                        font-size: 18px;
                                        margin-bottom: 10px;
                                    }}
                                    .price-value {{
                                        font-size: 36px;
                                        font-weight: bold;
                                    }}
                                    .breakdown-table {{
                                        width: 100%;
                                        border-collapse: collapse;
                                        margin: 20px 0;
                                    }}
                                    .breakdown-table th {{
                                        background: #2563eb;
                                        color: white;
                                        padding: 12px;
                                        text-align: right;
                                        font-weight: bold;
                                    }}
                                    .breakdown-table td {{
                                        padding: 10px;
                                        border-bottom: 1px solid #e5e7eb;
                                        text-align: right;
                                    }}
                                    .breakdown-table tr:nth-child(even) {{
                                        background: #f9fafb;
                                    }}
                                    .total-row {{
                                        background: #dbeafe !important;
                                        font-weight: bold;
                                        font-size: 18px;
                                    }}
                                    .footer {{
                                        margin-top: 50px;
                                        text-align: center;
                                        color: #6b7280;
                                        font-size: 12px;
                                        border-top: 2px solid #e5e7eb;
                                        padding-top: 20px;
                                    }}
                                    .highlight {{
                                        background: #fef3c7;
                                        padding: 15px;
                                        border-right: 4px solid #f59e0b;
                                        margin: 20px 0;
                                    }}
                                    @media print {{
                                        body {{
                                            padding: 0;
                                        }}
                                        .no-print {{
                                            display: none;
                                        }}
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <div class="company-name">🏢 شركة متالي للخدمات اللوجستية</div>
                                    <div class="quote-title">📋 عرض سعر ذكي بناءً على البيانات الفعلية</div>
                                </div>
                                
                                <div class="info-section">
                                    <div class="info-row">
                                        <span class="info-label">👤 اسم العميل:</span>
                                        <span class="info-value">{client_name}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">📅 تاريخ العرض:</span>
                                        <span class="info-value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">🏆 الفئة:</span>
                                        <span class="info-value">{tier}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">📦 عدد الطلبات الشهرية:</span>
                                        <span class="info-value">{orders_total:,} طلب</span>
                                    </div>
                                </div>
                                
                                <div class="pricing-section">
                                    <div class="price-box">
                                        <div class="price-label">💰 السعر المقترح للطلب الواحد</div>
                                        <div class="price-value">{quote.get('price', 0):.2f} ريال</div>
                                    </div>
                                    
                                    <div class="highlight">
                                        <strong>💡 هامش الربح:</strong> {quote['cost_breakdown'].get('target_margin', 0)}%
                                        <br>
                                        <strong>📊 الربح لكل طلب:</strong> {quote['cost_breakdown'].get('profit_per_order', 0):.2f} ريال
                                    </div>
                                </div>
                                
                                <h3 style="color: #1e40af; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">📊 تفاصيل التكلفة</h3>
                                <table class="breakdown-table">
                                    <thead>
                                        <tr>
                                            <th>البيان</th>
                                            <th>القيمة (ريال)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>💵 التكلفة الإجمالية للطلب</td>
                                            <td>{quote['cost_breakdown'].get('cost_per_order', 0):.2f}</td>
                                        </tr>
                                        <tr>
                                            <td>🚚 تكلفة الشحن</td>
                                            <td>{quote['cost_breakdown'].get('shipping_cost', 0):.2f}</td>
                                        </tr>
                                        <tr>
                                            <td>📦 تكلفة التجهيز</td>
                                            <td>{quote['cost_breakdown'].get('fulfillment_cost', 0):.2f}</td>
                                        </tr>
                                        <tr>
                                            <td>📦 تكلفة التغليف</td>
                                            <td>{quote['cost_breakdown'].get('packaging_cost', 0):.2f}</td>
                                        </tr>
                                        <tr>
                                            <td>🏭 التكاليف العامة</td>
                                            <td>{quote['cost_breakdown'].get('overhead_cost', 0):.2f}</td>
                                        </tr>
                                        <tr class="total-row">
                                            <td>💰 السعر النهائي (شامل الربح)</td>
                                            <td>{quote.get('price', 0):.2f}</td>
                                        </tr>
                                    </tbody>
                                </table>
                                
                                <div class="info-section" style="margin-top: 30px;">
                                    <h4 style="color: #1e40af; margin-bottom: 15px;">📈 ملخص الإجماليات</h4>
                                    <div class="info-row">
                                        <span class="info-label">السعر لكل طلب:</span>
                                        <span class="info-value">{quote.get('price', 0):.2f} ريال</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">عدد الطلبات الشهرية:</span>
                                        <span class="info-value">{orders_total:,} طلب</span>
                                    </div>
                                    <div class="info-row" style="background: #dbeafe; font-weight: bold; font-size: 18px;">
                                        <span class="info-label">💰 الإجمالي الشهري:</span>
                                        <span class="info-value">{quote.get('price', 0) * orders_total:,.2f} ريال</span>
                                    </div>
                                </div>
                                
                                <div class="footer">
                                    <p>🏢 شركة متالي للخدمات اللوجستية</p>
                                    <p>📧 info@matali.com | 📱 +966 XX XXX XXXX</p>
                                    <p style="margin-top: 10px; font-size: 10px;">تم إنشاء هذا العرض تلقائياً بواسطة نظام متالي للتسعير الذكي V2.0</p>
                                </div>
                            </body>
                            </html>
                            """
                            
                            # عرض زر الطباعة
                            st.components.v1.html(
                                f"""
                                <script>
                                    function printQuote() {{
                                        var printWindow = window.open('', '', 'height=800,width=800');
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
                            st.success("✅ تم فتح نافذة الطباعة!")

