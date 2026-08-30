import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(
    page_title="Riyadh Real Estate Live Radar",
    page_icon="🟢",
    layout="wide"
)

# 2. توليد البيانات الحية داخلياً بدون أي ملف خارجي
RIYADH_DISTRICTS = [
    "الملقا", "النرجس", "الياسمين", "الصحافة", "العقيق", "حطين", "القيروان",
    "العارض", "الربيع", "الندى", "الرمال", "المونسية", "قرطبة", "اليرموك",
    "القادسية", "الروضة", "الحمراء", "العليا", "السليمانية", "الملز", "المربع",
    "طويق", "لبن", "المهدية", "عرقة", "السويدي", "الشفا", "بدر", "العزيزية"
]

PROPERTY_TYPES = ["فيلا", "شقة", "أرض سكنية", "أرض تجارية", "دور سكني", "عمارة سكنية"]

def get_live_transactions():
    now_str = datetime.now().strftime("%H:%M:%S")
    n = 30
    
    districts = np.random.choice(RIYADH_DISTRICTS, n)
    props = np.random.choice(PROPERTY_TYPES, n)
    areas = np.random.randint(120, 850, n)
    sqm_prices = np.random.randint(3200, 12500, n)
    total_prices = areas * sqm_prices
    
    return pd.DataFrame({
        "رقم الصفقة": np.random.randint(100000, 999999, n),
        "الوقت": [now_str] * n,
        "الحي": districts,
        "نوع العقار": props,
        "المساحة (م²)": areas,
        "سعر المتر (SAR)": sqm_prices,
        "إجمالي الصفقة (SAR)": total_prices
    })

# 3. الهيدر وزر التحديث الفوري
st.title("🟢 Riyadh Real Estate Live Transaction Radar")
col_header, col_btn = st.columns([3, 1])

with col_header:
    st.caption(f"⚡ Live Feed Connected • Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_btn:
    if st.button("🔄 جلب صفقات جديدة اللحظة", use_container_width=True):
        st.session_state["data"] = get_live_transactions()

if "data" not in st.session_state:
    st.session_state["data"] = get_live_transactions()

df = st.session_state["data"]

# 4. كروت المؤشرات الأساسية (KPIs)
k1, k2, k3, k4 = st.columns(4)
k1.metric("عدد الصفقات اللحظية", f"{len(df)} صفقة")
k2.metric("إجمالي حجم التداول", f"{df['إجمالي الصفقة (SAR)'].sum():,} ريال")
k3.metric("متوسط سعر المتر", f"{int(df['سعر المتر (SAR)'].mean()):,} ريال/م²")
k4.metric("أحدث صفقة مسجلة", f"{df['إجمالي الصفقة (SAR)'].iloc[0]:,} ريال")

st.markdown("---")

# 5. الرسوم البيانية التفاعلية
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 أعلى 10 أحياء نشاطاً في سعر المتر")
    avg_price = df.groupby("الحي")["سعر المتر (SAR)"].mean().reset_index().sort_values("سعر المتر (SAR)", ascending=False).head(10)
    fig_bar = px.bar(
        avg_price,
        x="الحي",
        y="سعر المتر (SAR)",
        color="سعر المتر (SAR)",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("📈 توزيع المساحة مقابل السعر الإجمالي")
    fig_scatter = px.scatter(
        df,
        x="المساحة (م²)",
        y="إجمالي الصفقة (SAR)",
        color="نوع العقار",
        size="سعر المتر (SAR)",
        hover_data=["الحي", "الوقت"]
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# 6. جدول الصفقات المباشر
st.subheader("📋 جدول الإفراغات والصفقات الحية")
st.dataframe(df, use_container_width=True, hide_index=True)
