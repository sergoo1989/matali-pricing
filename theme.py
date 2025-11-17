"""
نظام الثيم الموحد
==================
نظام تصميم شامل يوفر:
- ألوان موحدة
- مكونات UI جاهزة
- استايلات CSS محسّنة
"""

import streamlit as st
from typing import Optional, List, Tuple


class MataliTheme:
    """نظام ثيم موحد للتطبيق"""
    
    # نظام الألوان الأساسي
    COLORS = {
        "primary": "#0EA5E9",
        "primary_dark": "#0369A1",
        "primary_light": "#E0F2FE",
        "secondary": "#6366F1",
        "bg_page": "#F3F4F6",
        "bg_card": "#FFFFFF",
        "bg_success": "#F0FDF4",
        "bg_warning": "#FFFBEB",
        "bg_error": "#FEF2F2",
        "border": "#E5E7EB",
        "border_light": "#F1F5F9",
        "text": "#0F172A",
        "text_muted": "#64748B",
        "text_light": "#94A3B8",
        "success": "#22C55E",
        "success_dark": "#16A34A",
        "error": "#EF4444",
        "error_dark": "#DC2626",
        "warning": "#F59E0B",
        "warning_dark": "#D97706"
    }
    
    # نظام الظلال والزوايا
    STYLES = {
        "radius_lg": "18px",
        "radius_md": "12px",
        "radius_sm": "8px",
        "shadow_soft": "0 18px 45px rgba(15, 23, 42, 0.06)",
        "shadow_medium": "0 25px 50px rgba(15, 23, 42, 0.08)",
        "shadow_large": "0 35px 60px rgba(15, 23, 42, 0.1)",
        "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
    }


class ThemeManager:
    """مدير الثيم المركزي"""
    
    @staticmethod
    def inject_global_theme():
        """حقن الثيم العالمي مع CSS محسن"""
        c = MataliTheme.COLORS
        s = MataliTheme.STYLES
        
        st.markdown(f"""
        <style>
        /* ===== متغيرات CSS العالمية ===== */
        :root {{
            /* الألوان الأساسية */
            --matali-primary: {c['primary']};
            --matali-primary-dark: {c['primary_dark']};
            --matali-primary-light: {c['primary_light']};
            --matali-secondary: {c['secondary']};
            
            /* خلفيات */
            --matali-bg-page: {c['bg_page']};
            --matali-bg-card: {c['bg_card']};
            --matali-bg-success: {c['bg_success']};
            --matali-bg-warning: {c['bg_warning']};
            --matali-bg-error: {c['bg_error']};
            
            /* النصوص */
            --matali-text: {c['text']};
            --matali-text-muted: {c['text_muted']};
            --matali-text-light: {c['text_light']};
            
            /* الحالات */
            --matali-success: {c['success']};
            --matali-success-dark: {c['success_dark']};
            --matali-error: {c['error']};
            --matali-error-dark: {c['error_dark']};
            --matali-warning: {c['warning']};
            --matali-warning-dark: {c['warning_dark']};
            
            /* التصميم */
            --matali-border: {c['border']};
            --matali-border-light: {c['border_light']};
            --matali-radius-lg: {s['radius_lg']};
            --matali-radius-md: {s['radius_md']};
            --matali-radius-sm: {s['radius_sm']};
            --matali-shadow-soft: {s['shadow_soft']};
            --matali-shadow-medium: {s['shadow_medium']};
            --matali-shadow-large: {s['shadow_large']};
            --matali-transition: {s['transition']};
        }}

        /* ===== إعدادات الخطوط الأساسية ===== */
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;600;700;800&display=swap');
        
        * {{
            font-family: "Tajawal", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        /* ===== خلفية بسيطة ===== */
        .stApp {{
            background: white;
            font-family: "Tajawal", system-ui, sans-serif;
        }}
        
        /* تأكد من أن المحتوى فوق الخلفية */
        .block-container {{
            position: relative;
            z-index: 10;
        }}
        
        /* تأكد من أن جميع عناصر Streamlit فوق الخلفية */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        section[data-testid="stSidebar"],
        .main {{
            position: relative;
            z-index: 10;
        }}

        /* ===== تحسينات التخطيط الأساسية ===== */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1280px;
        }}

        /* ===== هيدر الصفحة الرئيسي ===== */
        .matali-page-header {{
            margin-bottom: 2.5rem;
            padding: 2rem 2.5rem;
            border-radius: var(--matali-radius-lg);
            background: linear-gradient(135deg, {c['primary']} 0%, {c['secondary']} 100%);
            color: white;
            display: flex;
            align-items: center;
            gap: 1.5rem;
            box-shadow: 0 20px 60px rgba(14, 165, 233, 0.3);
            position: relative;
            overflow: hidden;
            animation: slideInDown 0.6s ease-out;
        }}

        @keyframes slideInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .matali-page-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
            pointer-events: none;
            animation: pulse 3s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 0.5;
            }}
            50% {{
                opacity: 0.8;
            }}
        }}

        .matali-page-header-title {{
            font-size: 1.6rem;
            font-weight: 800;
            margin: 0;
            position: relative;
        }}

        .matali-page-header-subtitle {{
            font-size: 1rem;
            opacity: 0.9;
            margin: 0.25rem 0 0 0;
            font-weight: 400;
            position: relative;
        }}

        .matali-page-header-icon {{
            font-size: 2.2rem;
            position: relative;
        }}

        /* ===== أقسام المحتوى الرئيسية ===== */
        .matali-section {{
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: var(--matali-radius-lg);
            border: 1px solid rgba(255, 255, 255, 0.6);
            box-shadow: 0 8px 32px rgba(15, 23, 42, 0.08), 
                        0 4px 16px rgba(14, 165, 233, 0.05),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9);
            padding: 1.75rem 2rem;
            margin-bottom: 2rem;
            transition: var(--matali-transition);
            position: relative;
        }}

        .matali-section:hover {{
            box-shadow: 0 12px 48px rgba(15, 23, 42, 0.12),
                        0 8px 24px rgba(14, 165, 233, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 1);
            transform: translateY(-4px);
            border-color: rgba(14, 165, 233, 0.3);
        }}

        .matali-section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .matali-section-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--matali-primary-dark);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 0;
        }}

        .matali-section-subtitle {{
            font-size: 0.9rem;
            color: var(--matali-text-muted);
            margin: 0.25rem 0 0 0;
        }}

        /* ===== كروت القوالب ===== */
        .matali-template-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}

        .matali-template-card {{
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: var(--matali-radius-lg);
            border: 1px solid rgba(255, 255, 255, 0.5);
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9);
        }}

        .matali-template-card::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 6px;
            height: 100%;
            background: linear-gradient(180deg, {c['primary']}, {c['secondary']});
            transform: scaleY(0);
            transform-origin: top;
            transition: transform 0.4s ease;
        }}
        
        .matali-template-card::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(99, 102, 241, 0.05));
            opacity: 0;
            transition: opacity 0.4s ease;
            pointer-events: none;
        }}

        .matali-template-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 60px rgba(14, 165, 233, 0.2),
                        0 8px 32px rgba(99, 102, 241, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 1);
            border-color: rgba(14, 165, 233, 0.4);
            background: rgba(255, 255, 255, 0.95);
        }}
        
        .matali-template-card:hover::before {{
            transform: scaleY(1);
        }}
        
        .matali-template-card:hover::after {{
            opacity: 1;
        }}

        .matali-template-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--matali-text);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .matali-template-description {{
            font-size: 0.9rem;
            color: var(--matali-text-muted);
            line-height: 1.7;
            margin-bottom: 1.5rem;
            min-height: 3.5rem;
        }}

        .matali-template-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }}

        .matali-template-format {{
            background: linear-gradient(135deg, {c['primary']}, {c['secondary']});
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 50px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        }}

        /* ===== أزرار محسنة ===== */
        .stButton > button {{
            border-radius: 50px;
            padding: 0.875rem 2.5rem;
            font-weight: 700;
            font-size: 0.95rem;
            border: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 24px rgba(14, 165, 233, 0.2);
            position: relative;
            overflow: hidden;
        }}

        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }}

        .stButton > button:hover::before {{
            width: 300px;
            height: 300px;
        }}

        .stButton > button:first-child {{
            background: linear-gradient(135deg, {c['primary']} 0%, {c['secondary']} 100%);
            color: white;
        }}

        .stButton > button:first-child:hover {{
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 40px rgba(14, 165, 233, 0.35);
        }}

        .stButton > button:active {{
            transform: translateY(-1px) scale(0.98);
        }}

        /* زر الخطر */
        .matali-danger-btn > button {{
            background: linear-gradient(135deg, var(--matali-error), var(--matali-error-dark)) !important;
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3) !important;
        }}

        /* زر ثانوي */
        .matali-secondary-btn > button {{
            background: var(--matali-bg-card) !important;
            color: var(--matali-primary) !important;
            border: 2px solid var(--matali-primary) !important;
        }}

        /* ===== البادجات ===== */
        .matali-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1.25rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 700;
            margin: 0.25rem 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}
        
        .matali-badge:hover {{
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
        }}

        .matali-badge-success {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border: none;
        }}

        .matali-badge-warning {{
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            border: none;
        }}

        .matali-badge-error {{
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            border: none;
        }}

        /* ===== التبويبات ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            padding: 0.5rem;
            background: var(--matali-bg-card);
            border-radius: var(--matali-radius-lg);
            border: 1px solid var(--matali-border-light);
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: var(--matali-radius-md);
            padding: 0.75rem 1.5rem;
            background: transparent;
            color: var(--matali-text-muted);
            font-weight: 600;
            transition: var(--matali-transition);
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--matali-primary), var(--matali-secondary));
            color: white;
            box-shadow: var(--matali-shadow-soft);
        }}

        /* ===== مربعات التنبيه ===== */
        .matali-alert {{
            padding: 1.5rem 2rem;
            border-radius: var(--matali-radius-lg);
            margin-bottom: 2rem;
            border-right: 6px solid;
            font-size: 0.95rem;
            line-height: 1.7;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.5);
            animation: slideInRight 0.5s ease-out;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }}
        
        @keyframes slideInRight {{
            from {{
                opacity: 0;
                transform: translateX(30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        .matali-alert-info {{
            background: linear-gradient(135deg, 
                        rgba(224, 242, 254, 0.9) 0%, 
                        rgba(186, 230, 253, 0.85) 100%);
            border-right-color: {c['primary']};
            color: #0369a1;
        }}

        .matali-alert-warning {{
            background: linear-gradient(135deg, 
                        rgba(254, 243, 199, 0.9) 0%, 
                        rgba(253, 230, 138, 0.85) 100%);
            border-right-color: {c['warning']};
            color: #92400e;
        }}

        .matali-alert-success {{
            background: linear-gradient(135deg, 
                        rgba(209, 250, 229, 0.9) 0%, 
                        rgba(167, 243, 208, 0.85) 100%);
            border-right-color: {c['success']};
            color: #065f46;
        }}

        .matali-alert-error {{
            background: linear-gradient(135deg, 
                        rgba(254, 226, 226, 0.9) 0%, 
                        rgba(254, 202, 202, 0.85) 100%);
            border-right-color: {c['error']};
            color: #991b1b;
        }}

        /* ===== الجداول ===== */
        .matali-table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: var(--matali-radius-lg);
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(15, 23, 42, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.5);
        }}

        .matali-table th {{
            background: linear-gradient(135deg, 
                        rgba(224, 242, 254, 0.9), 
                        rgba(186, 230, 253, 0.85));
            color: var(--matali-primary-dark);
            padding: 1rem;
            text-align: right;
            font-weight: 600;
            font-size: 0.85rem;
            border-bottom: 2px solid rgba(14, 165, 233, 0.2);
        }}

        .matali-table td {{
            padding: 0.875rem 1rem;
            border-bottom: 1px solid rgba(226, 232, 240, 0.5);
            font-size: 0.9rem;
            background: rgba(255, 255, 255, 0.4);
        }}

        .matali-table tr:last-child td {{
            border-bottom: none;
        }}

        .matali-table tr:hover td {{
            background: rgba(224, 242, 254, 0.5);
        }}

        /* ===== تحسين Streamlit الأصلية ===== */
        
        /* تعريب القوائم */
        [data-testid="stSidebarNav"] {{
            direction: rtl;
        }}
        
        /* تعريب أزرار Streamlit */
        button[kind="header"]::after {{
            content: " ☰";
        }}
        
        /* إخفاء شعار Streamlit */
        #MainMenu {{
            visibility: hidden;
        }}
        
        footer {{
            visibility: hidden;
        }}
        
        /* تعريب قائمة الهامبرجر */
        [data-testid="stToolbar"] {{
            direction: rtl;
        }}
        
        /* إزالة الحواف الإضافية */
        .big-title {{
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin: 1rem 0;
        }}
        
        .section-header {{
            background: linear-gradient(90deg, #1f77b4, #4a90e2);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }}
        
        .metric-box {{
            background: #f0f2f6;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #1f77b4;
            margin: 1rem 0;
        }}
        
        .success-box {{
            border-left-color: #2ecc71;
        }}
        
        .warning-box {{
            border-left-color: #f39c12;
        }}
        
        .danger-box {{
            border-left-color: #e74c3c;
        }}

        /* ===== تحسينات الاستجابة ===== */
        @media (max-width: 768px) {{
            .matali-template-grid {{
                grid-template-columns: 1fr;
            }}
            
            .matali-page-header {{
                padding: 1.5rem 1.75rem;
            }}
            
            .matali-section {{
                padding: 1.5rem 1.75rem;
            }}
            
            .matali-page-header-title {{
                font-size: 1.3rem;
            }}
        }}
        
        /* ===== أيقونات ملونة للأقسام ===== */
        .icon-primary {{
            color: {c['primary']};
            font-size: 2rem;
            filter: drop-shadow(0 4px 8px rgba(14, 165, 233, 0.3));
        }}
        
        .icon-success {{
            color: {c['success']};
            filter: drop-shadow(0 4px 8px rgba(34, 197, 94, 0.3));
        }}
        
        .icon-warning {{
            color: {c['warning']};
            filter: drop-shadow(0 4px 8px rgba(245, 158, 11, 0.3));
        }}
        
        /* ===== تأثيرات حركية إضافية ===== */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.6s ease-in;
        }}
        
        /* ===== تحسين Sidebar ===== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, 
                        rgba(248, 250, 252, 0.95) 0%, 
                        rgba(241, 245, 249, 0.95) 50%,
                        rgba(248, 250, 252, 0.95) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-left: 1px solid rgba(255, 255, 255, 0.6);
            box-shadow: -4px 0 24px rgba(15, 23, 42, 0.08);
        }}
        
        [data-testid="stSidebar"]::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(14, 165, 233, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(99, 102, 241, 0.04) 0%, transparent 50%);
            pointer-events: none;
        }}
        
        [data-testid="stSidebar"] .css-1d391kg {{
            padding-top: 2rem;
        }}
        
        /* تحسين عناصر Sidebar */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            background: rgba(255, 255, 255, 0.6);
            border-radius: var(--matali-radius-md);
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(14, 165, 233, 0.1);
            transition: all 0.3s ease;
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:hover {{
            background: rgba(255, 255, 255, 0.8);
            border-color: rgba(14, 165, 233, 0.3);
            transform: translateX(-4px);
        }}
        
        /* ===== تحسين العناوين ===== */
        h1, h2, h3 {{
            font-weight: 700;
            color: var(--matali-text);
        }}
        
        /* ===== Divider محسن ===== */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--matali-border), transparent);
            margin: 2rem 0;
        }}
        </style>
        """, unsafe_allow_html=True)


# ===== دوال مساعدة للمكونات =====

def page_header(title: str, subtitle: str = "", icon: str = "📊"):
    """هيدر صفحة محسن مع جرادينت وإضاءة"""
    st.markdown(
        f"""
        <div class="matali-page-header">
            <div class="matali-page-header-icon">{icon}</div>
            <div>
                <h1 class="matali-page-header-title">{title}</h1>
                {f'<p class="matali-page-header-subtitle">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section(title: str, subtitle: str = "", icon: str = "📁") -> None:
    """قسم محتوى مع تأثيرات hover"""
    st.markdown(
        f"""
        <div class="matali-section">
            <div class="matali-section-header">
                <h2 class="matali-section-title">
                    {icon} {title}
                </h2>
            </div>
            {f'<p class="matali-section-subtitle">{subtitle}</p>' if subtitle else ''}
        """,
        unsafe_allow_html=True
    )


def close_section():
    """إغلاق القسم"""
    st.markdown("</div>", unsafe_allow_html=True)


def alert(message: str, alert_type: str = "info"):
    """مربع تنبيه محسن"""
    icons = {
        "info": "ℹ️",
        "warning": "⚠️", 
        "success": "✅",
        "error": "❌"
    }
    
    icon = icons.get(alert_type, "ℹ️")
    
    st.markdown(
        f"""
        <div class="matali-alert matali-alert-{alert_type}">
            <strong>{icon}</strong> {message}
        </div>
        """,
        unsafe_allow_html=True
    )


def badge(text: str, status: str = "warning"):
    """بادج ذو ستايل موحد"""
    icons = {
        "success": "✅",
        "warning": "⚠️", 
        "error": "❌",
        "info": "ℹ️"
    }
    
    st.markdown(
        f"""
        <div class="matali-badge matali-badge-{status}">
            {icons.get(status, '')} {text}
        </div>
        """,
        unsafe_allow_html=True
    )


def template_card(title: str, description: str, file_format: str, download_button_key: str):
    """كارت قالب محسّن"""
    return f"""
    <div class="matali-template-card">
        <h3 class="matali-template-title">{title}</h3>
        <p class="matali-template-description">{description}</p>
        <div class="matali-template-meta">
            <span class="matali-template-format">{file_format}</span>
        </div>
    </div>
    """


def metric_card(label: str, value: str, delta: str = "", icon: str = "📊"):
    """كارت مؤشر مالي"""
    delta_html = f'<div style="color: #22C55E; font-size: 0.85rem; margin-top: 0.25rem;">{delta}</div>' if delta else ''
    
    st.markdown(
        f"""
        <div class="matali-section" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 0.85rem; color: var(--matali-text-muted); margin-bottom: 0.5rem;">{label}</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: var(--matali-primary);">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )
