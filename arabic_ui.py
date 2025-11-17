"""
نظام الترجمة العربية لـ Streamlit
===================================
يوفر ترجمات عربية لعناصر Streamlit الافتراضية
"""

import streamlit as st

# قاموس الترجمات
TRANSLATIONS = {
    # قائمة التطبيق
    "Deploy": "نشر",
    "Rerun": "إعادة تشغيل",
    "Settings": "الإعدادات",
    "Print": "طباعة",
    "Record a screencast": "تسجيل الشاشة",
    "Report a bug": "الإبلاغ عن خطأ",
    "Clear cache": "مسح الذاكرة المؤقتة",
    "Developer options": "خيارات المطور",
    
    # الأزرار
    "Download": "تحميل",
    "Upload": "رفع",
    "Submit": "إرسال",
    "Cancel": "إلغاء",
    "Close": "إغلاق",
    
    # الرسائل
    "Running...": "جاري التشغيل...",
    "Loading...": "جاري التحميل...",
    "Error": "خطأ",
    "Warning": "تحذير",
    "Success": "نجاح",
    "Info": "معلومة",
}


def apply_rtl_direction():
    """تطبيق اتجاه RTL على الواجهة"""
    st.markdown("""
    <style>
        /* اتجاه RTL للواجهة */
        .stApp {
            direction: rtl;
            text-align: right;
        }
        
        /* محاذاة القوائم الجانبية */
        [data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        
        /* محاذاة النصوص */
        .stMarkdown, .stText {
            direction: rtl;
            text-align: right;
        }
        
        /* محاذاة الأزرار */
        .stButton {
            direction: rtl;
        }
        
        /* محاذاة حقول الإدخال */
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
        }
        
        /* قائمة الهامبرجر */
        [data-testid="stHeader"] {
            direction: ltr;
        }
    </style>
    """, unsafe_allow_html=True)


def translate_ui():
    """ترجمة عناصر الواجهة إلى العربية"""
    
    # JavaScript لترجمة النصوص
    st.markdown("""
    <script>
    // انتظار تحميل الصفحة
    window.addEventListener('load', function() {
        // ترجمة قائمة Deploy
        const deployButtons = document.querySelectorAll('button');
        deployButtons.forEach(btn => {
            if (btn.textContent === 'Deploy') btn.textContent = 'نشر';
            if (btn.textContent === 'Rerun') btn.textContent = 'إعادة تشغيل';
            if (btn.textContent === 'Settings') btn.textContent = 'الإعدادات';
            if (btn.textContent === 'Clear cache') btn.textContent = 'مسح الذاكرة';
        });
    });
    </script>
    """, unsafe_allow_html=True)
