# 🎨 دليل نظام الثيم الموحد - Matali Pro

## نظرة عامة

تم إنشاء نظام ثيم موحد ومتكامل لـ Matali Pro يوفر:
- ✅ تصميم عصري ومتناسق
- ✅ مكونات UI جاهزة للاستخدام
- ✅ نظام ألوان موحد
- ✅ استجابة كاملة للأجهزة المختلفة

---

## 📁 الملفات الأساسية

### 1. `.streamlit/config.toml`
ملف إعدادات Streamlit الأساسي:
```toml
[theme]
base="light"
primaryColor="#0EA5E9"
backgroundColor="#F3F4F6"
secondaryBackgroundColor="#FFFFFF"
textColor="#0F172A"
font="sans serif"

[server]
port = 8509
```

### 2. `theme.py`
نظام الثيم الكامل مع المكونات الجاهزة

---

## 🎨 نظام الألوان

```python
from theme import MataliTheme

# الألوان الأساسية
primary = "#0EA5E9"      # أزرق سماوي
secondary = "#6366F1"    # بنفسجي
success = "#22C55E"      # أخضر
warning = "#F59E0B"      # برتقالي
error = "#EF4444"        # أحمر
```

---

## 🧩 المكونات الجاهزة

### 1. هيدر الصفحة
```python
from theme import page_header

page_header(
    title="مركز البيانات",
    subtitle="منصة متكاملة لإدارة البيانات",
    icon="📊"
)
```

### 2. أقسام المحتوى
```python
from theme import section, close_section

section(
    title="القوالب الجاهزة",
    subtitle="اختر القالب المناسب",
    icon="📥"
)

# محتوى القسم هنا...

close_section()
```

### 3. التنبيهات
```python
from theme import alert

alert("رسالة معلوماتية", "info")
alert("رسالة تحذيرية", "warning")
alert("رسالة نجاح", "success")
alert("رسالة خطأ", "error")
```

### 4. البادجات
```python
from theme import badge

badge("تم الرفع", "success")
badge("في الانتظار", "warning")
badge("خطأ", "error")
```

---

## 📦 CSS Classes الجاهزة

### كروت القوالب
```html
<div class="matali-template-card">
    <h3 class="matali-template-title">عنوان القالب</h3>
    <p class="matali-template-description">وصف القالب</p>
    <div class="matali-template-meta">
        <span class="matali-template-format">XLSX</span>
    </div>
</div>
```

### الأقسام
```html
<div class="matali-section">
    <div class="matali-section-header">
        <h2 class="matali-section-title">📊 العنوان</h2>
    </div>
    <!-- المحتوى -->
</div>
```

### التنبيهات
```html
<div class="matali-alert matali-alert-info">
    <strong>ℹ️</strong> رسالة معلوماتية
</div>
```

---

## 🚀 الاستخدام في الصفحات

### مثال كامل:

```python
import streamlit as st
from theme import ThemeManager, page_header, section, alert, badge

# إعداد الصفحة
st.set_page_config(
    page_title="المركز | Matali Pro",
    page_icon="📊",
    layout="wide"
)

# تطبيق الثيم
ThemeManager.inject_global_theme()

# الهيدر الرئيسي
page_header(
    title="مركز البيانات",
    subtitle="إدارة شاملة لجميع البيانات",
    icon="📊"
)

# تنبيه
alert("يرجى تحميل القوالب أولاً", "info")

# قسم
section(
    title="القوالب الجاهزة",
    subtitle="اختر ما يناسبك",
    icon="📥"
)

# محتوى القسم
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="matali-template-card">
        <h3 class="matali-template-title">💰 P&L</h3>
        <p class="matali-template-description">قائمة الدخل</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button("تحميل", data=..., file_name="pnl.xlsx")
    badge("تم الرفع", "success")
```

---

## 🎯 متغيرات CSS المخصصة

يمكنك استخدام المتغيرات التالية في أي CSS مخصص:

```css
/* الألوان */
var(--matali-primary)
var(--matali-secondary)
var(--matali-success)
var(--matali-warning)
var(--matali-error)

/* الخلفيات */
var(--matali-bg-card)
var(--matali-bg-page)

/* النصوص */
var(--matali-text)
var(--matali-text-muted)

/* التصميم */
var(--matali-radius-lg)
var(--matali-shadow-soft)
var(--matali-transition)
```

---

## ✨ المميزات

1. **تصميم متناسق**: نفس الاستايل في جميع الصفحات
2. **سهولة الاستخدام**: مكونات جاهزة بدون كتابة HTML/CSS
3. **استجابة كاملة**: يعمل بشكل مثالي على جميع الأحجام
4. **أداء محسّن**: CSS محسّن ومنظم
5. **قابل للتخصيص**: متغيرات CSS قابلة للتعديل

---

## 📱 الاستجابة

النظام يدعم جميع أحجام الشاشات:
- 💻 Desktop (1280px+)
- 💻 Tablet (768px - 1280px)
- 📱 Mobile (<768px)

تلقائياً يتم:
- تحويل Grid إلى عمود واحد في الموبايل
- تصغير الخطوط والمسافات
- إخفاء/إظهار عناصر معينة

---

## 🔧 التخصيص المتقدم

### إضافة لون مخصص:

```python
# في theme.py
COLORS = {
    # ... الألوان الموجودة
    "custom": "#YOUR_COLOR"
}
```

### إضافة مكون جديد:

```python
def custom_component(text: str):
    """مكون مخصص"""
    st.markdown(
        f"""
        <div class="matali-custom">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )
```

---

## 📝 ملاحظات مهمة

1. **استيراد الثيم دائماً**: يجب استدعاء `ThemeManager.inject_global_theme()` في بداية كل صفحة
2. **استخدم المكونات الجاهزة**: بدلاً من كتابة HTML مباشرة
3. **الخطوط**: يستخدم النظام خط Tajawal للعربية
4. **التوافق**: متوافق مع Streamlit 1.28.0+

---

## 🎓 أمثلة متقدمة

### كارت مع حالة:
```python
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="matali-template-card">...</div>', 
                unsafe_allow_html=True)
    
    status = db.load_dataframe('pnl')
    if status is not None:
        badge("✅ تم الرفع", "success")
    else:
        badge("⏳ في الانتظار", "warning")
```

### جدول مخصص:
```python
st.markdown("""
<table class="matali-table">
    <thead>
        <tr>
            <th>الاسم</th>
            <th>القيمة</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>البند 1</td>
            <td>100 ر.س</td>
        </tr>
    </tbody>
</table>
""", unsafe_allow_html=True)
```

---

## 🔗 روابط مفيدة

- [Streamlit Documentation](https://docs.streamlit.io)
- [CSS Variables Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Google Fonts - Tajawal](https://fonts.google.com/specimen/Tajawal)

---

تم التطوير بواسطة **Matali Pro Team** 🚀
