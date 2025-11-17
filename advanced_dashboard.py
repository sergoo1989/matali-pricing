import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

class AdvancedDashboard:
    def __init__(self, pricing_system):
        self.ps = pricing_system
    
    def show_professional_dashboard(self):
        """عرض الداشبورد الاحترافي المتكامل"""
        
        st.markdown("""
        <style>
            .big-font { font-size: 3rem !important; font-weight: bold; }
            .medium-font { font-size: 1.5rem !important; }
            .kpi-card { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                color: white;
                margin: 10px;
            }
            .warning-card { 
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px;
                border-radius: 15px;
                color: white;
                margin: 10px;
            }
            .success-card { 
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 20px;
                border-radius: 15px;
                color: white;
                margin: 10px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # العنوان الرئيسي
        st.markdown('<div class="main-header">📊 الداشبورد الاحترافي - متالى للتسعير</div>', unsafe_allow_html=True)
        
        # شرح الداشبورد
        with st.expander("📖 كيف تقرأ وتستفيد من الداشبورد؟", expanded=False):
            st.markdown("""
            ### 💡 ما هو الداشبورد؟
            **الداشبورد** هو لوحة تحكم شاملة تعرض جميع مؤشرات الأداء والتحليلات في مكان واحد.
            
            ### 📊 الأقسام الستة:
            
            #### 1️⃣ المؤشرات الرئيسية (KPIs)
            **ماذا تعرض:**
            - عدد الخدمات النشطة
            - إجمالي الطاقة الشهرية
            - التكاليف الشهرية
            - متوسط تكلفة الوحدة
            
            **كيف تستفيد:**
            - نظرة سريعة على حجم عملياتك
            - معرفة التكاليف الإجمالية
            - مقارنة بين الفترات المختلفة
            
            #### 2️⃣ تحليل الربحية
            **ماذا تعرض:**
            - توزيع الإيرادات حسب الخدمة
            - مقارنة التكاليف vs الإيرادات
            - اتجاه نمو الإيرادات
            
            **كيف تستفيد:**
            - تحديد الخدمات الأكثر ربحية
            - اكتشاف فرص النمو
            - تحسين استراتيجية التسعير
            
            #### 3️⃣ تحليل الطاقة والاستغلال
            **ماذا تعرض:**
            - نسبة استغلال كل خدمة
            - الهدر في الطاقة
            - توصيات لزيادة الاستغلال
            
            **كيف تستفيد:**
            - معرفة الخدمات ذات الاستغلال المنخفض
            - تحديد فرص تحسين الكفاءة
            - حساب تكلفة الهدر
            
            #### 4️⃣ تحليل الخدمات
            **ماذا تعرض:**
            - أداء كل خدمة
            - المساهمة في الإيرادات
            - هامش الربح لكل خدمة
            
            **كيف تستفيد:**
            - تحديد الخدمات ذات القيمة العالية
            - اكتشاف الخدمات التي تحتاج تحسين
            - إعادة تقييم الأسعار
            
            #### 5️⃣ التنبيهات والتوصيات
            **ماذا تعرض:**
            - تحذيرات عن الخدمات ذات هامش ربح منخفض
            - توصيات لزيادة الإيرادات
            - نصائح لتحسين الكفاءة
            
            **كيف تستفيد:**
            - اتخاذ قرارات مبنية على البيانات
            - تحسين العمليات
            - زيادة الربحية
            
            #### 6️⃣ التقارير السريعة
            **ماذا تعرض:**
            - تقارير Excel جاهزة للتحميل
            - ملخص الأداء
            - تفاصيل الخدمات
            
            **كيف تستفيد:**
            - مشاركة التقارير مع الإدارة
            - حفظ نسخ احتياطية
            - التحليل الخارجي
            
            ### 🎯 نصائح للاستفادة القصوى:
            
            **يومياً:**
            - راجع المؤشرات الرئيسية
            - تابع التنبيهات الجديدة
            
            **أسبوعياً:**
            - راجع تحليل الربحية
            - تحقق من استغلال الطاقة
            
            **شهرياً:**
            - راجع جميع الأقسام بالتفصيل
            - حمّل التقارير للأرشفة
            - قارن الأداء بالأشهر السابقة
            
            ### ⚠️ تذكير:
            الداشبورد يعتمد على البيانات المدخلة. كلما كانت بياناتك دقيقة، كانت التحليلات أكثر فائدة!
            """)
        
        # تحميل البيانات
        capacity_df = self.ps.load_capacity_data()
        pricing_df = self.ps.load_pricing_data()
        
        # التحقق من وجود بيانات
        if capacity_df.empty:
            st.error("""
            ❌ **لا توجد بيانات لعرضها في الداشبورد!**
            
            يرجى إضافة بيانات الخدمات أولاً من صفحة "⚙️ إعداد الطاقة"
            """)
            return
        
        # مؤشرات الأداء الرئيسية (KPIs)
        self._show_main_kpis(capacity_df)
        
        # تحليل الربحية
        self._show_profitability_analysis(capacity_df, pricing_df)
        
        # تحليل الطاقة والهدر
        self._show_capacity_analysis(capacity_df)
        
        # تحليل الخدمات
        self._show_services_analysis(capacity_df)
        
        # الإنذارات والتوصيات
        self._show_alerts_recommendations(capacity_df)
        
        # التقارير السريعة
        self._show_quick_reports(capacity_df, pricing_df)
    
    def _show_main_kpis(self, capacity_df):
        """عرض مؤشرات الأداء الرئيسية"""
        
        st.markdown("### 📈 مؤشرات الأداء الرئيسية (KPIs)")
        
        # حساب المؤشرات
        total_monthly_capacity = capacity_df['monthly_capacity'].sum()
        total_monthly_cost = capacity_df['monthly_cost'].sum()
        total_services = len(capacity_df)
        estimated_revenue = total_monthly_cost * 1.3  # تقدير الإيراد
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="medium-font">الطاقة الإجمالية</div>
                <div class="big-font">{total_monthly_capacity:,.0f}</div>
                <div>وحدة/شهر</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="medium-font">التكاليف الشهرية</div>
                <div class="big-font">{total_monthly_cost:,.0f}</div>
                <div>ريال سعودي</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="success-card">
                <div class="medium-font">الإيراد المتوقع</div>
                <div class="big-font">{estimated_revenue:,.0f}</div>
                <div>ريال سعودي</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="medium-font">الخدمات النشطة</div>
                <div class="big-font">{total_services}</div>
                <div>خدمة</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _show_profitability_analysis(self, capacity_df, pricing_df):
        """تحليل الربحية"""
        st.markdown("### 💰 تحليل الربحية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # رسم بياني دائري للتكاليف حسب المجموعة
            cost_by_group = capacity_df.groupby('service_group')['monthly_cost'].sum().reset_index()
            fig = px.pie(
                cost_by_group, 
                values='monthly_cost', 
                names='service_group',
                title='توزيع التكاليف حسب المجموعة',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # رسم بياني للطاقة حسب المجموعة
            capacity_by_group = capacity_df.groupby('service_group')['monthly_capacity'].sum().reset_index()
            fig = px.bar(
                capacity_by_group,
                x='service_group',
                y='monthly_capacity',
                title='الطاقة الإجمالية حسب المجموعة',
                color='monthly_capacity',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # جدول تحليل الربحية حسب الخدمة
        st.markdown("#### تحليل تفصيلي حسب الخدمة")
        analysis_df = capacity_df[['service_name', 'service_group', 'monthly_capacity', 'monthly_cost', 'cost_per_unit']].copy()
        analysis_df['estimated_revenue'] = analysis_df['monthly_cost'] * 1.25
        analysis_df['estimated_profit'] = analysis_df['estimated_revenue'] - analysis_df['monthly_cost']
        analysis_df['profit_margin_%'] = (analysis_df['estimated_profit'] / analysis_df['estimated_revenue'] * 100).round(2)
        
        st.dataframe(
            analysis_df.style.format({
                'monthly_capacity': '{:,.0f}',
                'monthly_cost': '{:,.2f} ر.س',
                'cost_per_unit': '{:,.2f} ر.س',
                'estimated_revenue': '{:,.2f} ر.س',
                'estimated_profit': '{:,.2f} ر.س',
                'profit_margin_%': '{:.2f}%'
            }),
            use_container_width=True,
            height=400
        )
    
    def _show_capacity_analysis(self, capacity_df):
        """تحليل الطاقة والهدر"""
        st.markdown("### 📊 تحليل الطاقة والهدر")
        
        # حساب الاستخدام الافتراضي (70%)
        capacity_df_analysis = capacity_df.copy()
        capacity_df_analysis['assumed_usage'] = capacity_df_analysis['monthly_capacity'] * 0.7
        capacity_df_analysis['waste_capacity'] = capacity_df_analysis['monthly_capacity'] - capacity_df_analysis['assumed_usage']
        capacity_df_analysis['waste_cost'] = capacity_df_analysis['waste_capacity'] * capacity_df_analysis['cost_per_unit']
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_waste_cost = capacity_df_analysis['waste_cost'].sum()
            st.markdown(f"""
            <div class="warning-card">
                <div class="medium-font">تكلفة الهدر المتوقعة</div>
                <div class="big-font">{total_waste_cost:,.0f}</div>
                <div>ريال سعودي/شهر (بافتراض 70% استخدام)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_utilization = 70.0
            st.markdown(f"""
            <div class="kpi-card">
                <div class="medium-font">معدل الاستخدام المفترض</div>
                <div class="big-font">{avg_utilization:.0f}%</div>
                <div>من الطاقة الكلية</div>
            </div>
            """, unsafe_allow_html=True)
        
        # رسم بياني للهدر حسب الخدمة
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='الطاقة المستخدمة',
            x=capacity_df_analysis['service_name'],
            y=capacity_df_analysis['assumed_usage'],
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='الطاقة المهدرة',
            x=capacity_df_analysis['service_name'],
            y=capacity_df_analysis['waste_capacity'],
            marker_color='salmon'
        ))
        
        fig.update_layout(
            title='تحليل الطاقة المستخدمة vs المهدرة',
            xaxis_title='الخدمة',
            yaxis_title='الطاقة',
            barmode='stack',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # جدول تفصيلي للهدر
        st.markdown("#### تفاصيل الهدر حسب الخدمة")
        waste_df = capacity_df_analysis[['service_name', 'monthly_capacity', 'assumed_usage', 'waste_capacity', 'cost_per_unit', 'waste_cost']].copy()
        waste_df = waste_df.sort_values('waste_cost', ascending=False)
        
        st.dataframe(
            waste_df.style.format({
                'monthly_capacity': '{:,.0f}',
                'assumed_usage': '{:,.0f}',
                'waste_capacity': '{:,.0f}',
                'cost_per_unit': '{:,.2f} ر.س',
                'waste_cost': '{:,.2f} ر.س'
            }),
            use_container_width=True
        )
    
    def _show_services_analysis(self, capacity_df):
        """تحليل الخدمات"""
        st.markdown("### 🛠️ تحليل الخدمات")
        
        # تحليل حسب نوع الطاقة
        capacity_type_analysis = capacity_df.groupby('capacity_type').agg({
            'service_key': 'count',
            'monthly_capacity': 'sum',
            'monthly_cost': 'sum'
        }).reset_index()
        capacity_type_analysis.columns = ['نوع الطاقة', 'عدد الخدمات', 'الطاقة الإجمالية', 'التكلفة الإجمالية']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### التوزيع حسب نوع الطاقة")
            st.dataframe(
                capacity_type_analysis.style.format({
                    'الطاقة الإجمالية': '{:,.0f}',
                    'التكلفة الإجمالية': '{:,.2f} ر.س'
                }),
                use_container_width=True
            )
        
        with col2:
            # رسم بياني دائري لتوزيع الخدمات حسب المجموعة
            group_count = capacity_df.groupby('service_group').size().reset_index(name='count')
            fig = px.pie(
                group_count,
                values='count',
                names='service_group',
                title='توزيع الخدمات حسب المجموعة'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # مقارنة تكلفة الوحدة
        st.markdown("#### مقارنة تكلفة الوحدة")
        cost_comparison = capacity_df[['service_name', 'service_group', 'cost_per_unit', 'monthly_capacity']].copy()
        cost_comparison = cost_comparison.sort_values('cost_per_unit', ascending=False)
        
        fig = px.bar(
            cost_comparison,
            x='service_name',
            y='cost_per_unit',
            color='service_group',
            title='تكلفة الوحدة لكل خدمة',
            labels={'cost_per_unit': 'تكلفة الوحدة (ر.س)', 'service_name': 'الخدمة'}
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def _show_alerts_recommendations(self, capacity_df):
        """الإنذارات والتوصيات"""
        st.markdown("### ⚠️ الإنذارات والتوصيات")
        
        alerts = []
        recommendations = []
        
        # تحليل التكاليف العالية
        high_cost_services = capacity_df[capacity_df['cost_per_unit'] > capacity_df['cost_per_unit'].mean()]
        if len(high_cost_services) > 0:
            alerts.append({
                'type': 'warning',
                'title': 'خدمات ذات تكلفة وحدة عالية',
                'message': f'يوجد {len(high_cost_services)} خدمات تكلفة وحدتها أعلى من المتوسط'
            })
            recommendations.append({
                'title': 'تحسين الكفاءة',
                'message': 'مراجعة الخدمات ذات التكلفة العالية وإيجاد طرق لتقليل التكاليف'
            })
        
        # تحليل الطاقة المنخفضة
        low_capacity_services = capacity_df[capacity_df['monthly_capacity'] < 100]
        if len(low_capacity_services) > 0:
            alerts.append({
                'type': 'info',
                'title': 'خدمات ذات طاقة منخفضة',
                'message': f'يوجد {len(low_capacity_services)} خدمات بطاقة شهرية أقل من 100 وحدة'
            })
        
        # تحليل التكاليف الإجمالية
        total_cost = capacity_df['monthly_cost'].sum()
        if total_cost > 150000:
            alerts.append({
                'type': 'warning',
                'title': 'تكاليف شهرية مرتفعة',
                'message': f'التكاليف الشهرية الإجمالية: {total_cost:,.0f} ر.س'
            })
            recommendations.append({
                'title': 'مراجعة هيكل التكاليف',
                'message': 'النظر في إمكانية تحسين هيكل التكاليف أو زيادة الأسعار'
            })
        
        # عرض الإنذارات
        if alerts:
            st.markdown("#### 🚨 الإنذارات")
            for alert in alerts:
                if alert['type'] == 'warning':
                    st.warning(f"**{alert['title']}**: {alert['message']}")
                else:
                    st.info(f"**{alert['title']}**: {alert['message']}")
        
        # عرض التوصيات
        if recommendations:
            st.markdown("#### 💡 التوصيات")
            for i, rec in enumerate(recommendations, 1):
                st.success(f"**{i}. {rec['title']}**: {rec['message']}")
        
        if not alerts and not recommendations:
            st.success("✅ لا توجد إنذارات أو تحذيرات في الوقت الحالي")
    
    def _show_quick_reports(self, capacity_df, pricing_df):
        """التقارير السريعة"""
        st.markdown("### 📄 التقارير السريعة")
        
        report_type = st.selectbox(
            "اختر نوع التقرير",
            ["تقرير شامل", "تقرير التكاليف", "تقرير الطاقة", "تقرير الأسعار"]
        )
        
        from io import BytesIO
        
        if report_type == "تقرير شامل":
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                capacity_df.to_excel(writer, sheet_name='الطاقة الاستيعابية', index=False)
                pricing_df.to_excel(writer, sheet_name='شرائح الأسعار', index=False)
                
                # تقرير ملخص
                summary = pd.DataFrame({
                    'المؤشر': [
                        'إجمالي الطاقة الشهرية',
                        'إجمالي التكاليف الشهرية',
                        'عدد الخدمات',
                        'متوسط تكلفة الوحدة'
                    ],
                    'القيمة': [
                        f"{capacity_df['monthly_capacity'].sum():,.0f}",
                        f"{capacity_df['monthly_cost'].sum():,.2f} ر.س",
                        len(capacity_df),
                        f"{capacity_df['cost_per_unit'].mean():,.2f} ر.س"
                    ]
                })
                summary.to_excel(writer, sheet_name='الملخص التنفيذي', index=False)
            buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل التقرير الشامل",
                data=buffer,
                file_name="comprehensive_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        elif report_type == "تقرير التكاليف":
            cost_report = capacity_df[['service_name', 'service_group', 'monthly_cost', 'cost_per_unit']].copy()
            buffer = BytesIO()
            cost_report.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل تقرير التكاليف",
                data=buffer,
                file_name="cost_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        elif report_type == "تقرير الطاقة":
            capacity_report = capacity_df[['service_name', 'capacity_type', 'daily_capacity', 'monthly_capacity']].copy()
            buffer = BytesIO()
            capacity_report.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل تقرير الطاقة",
                data=buffer,
                file_name="capacity_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        elif report_type == "تقرير الأسعار":
            buffer = BytesIO()
            pricing_df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            
            st.download_button(
                label="📥 تحميل تقرير الأسعار",
                data=buffer,
                file_name="pricing_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        # معاينة البيانات
        st.markdown("#### معاينة البيانات")
        preview_tab1, preview_tab2 = st.tabs(["بيانات الطاقة", "بيانات الأسعار"])
        
        with preview_tab1:
            st.dataframe(capacity_df, use_container_width=True, height=400)
        
        with preview_tab2:
            st.dataframe(pricing_df, use_container_width=True, height=400)
