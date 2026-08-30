import streamlit as st
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from src.live_fetcher import fetch_live_deals

st.set_page_config(
    page_title="Riyadh Live Real Estate Radar",
    page_icon="🟢",
    layout="wide"
)

# تحديث الصفحة تلقائياً كل 10 ثوانٍ
st_autorefresh(interval=10000, key="realtime_counter")

st.title("🟢 Riyadh Real Estate Live Transaction Radar")
st.caption(f"⚡ Live Feed Connected • Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Auto-refreshes every 10s)")

# جلب وتجهيز البيانات
df = fetch_live_deals()

if not df.empty:
    # ── 1. المؤشرات الحية (KPIs) ───────────────────────────
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Live Active Deals", f"{len(df)} Deals")
    kpi2.metric("Total Volume (SAR)", f"{df['Price_SAR'].sum():,}")
    kpi3.metric("Avg Price / m²", f"{int(df['Price_Per_Sqm'].mean()):,} SAR")
    kpi4.metric("Latest Deal Price", f"{df['Price_SAR'].iloc[0]:,} SAR")

    st.markdown("---")

    # ── 2. الرسوم البيانية التفاعلية ────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Average Price/m² by District")
        avg_district = df.groupby("District")["Price_Per_Sqm"].mean().reset_index().sort_values("Price_Per_Sqm", ascending=False).head(10)
        fig_bar = px.bar(
            avg_district,
            x="District",
            y="Price_Per_Sqm",
            color="Price_Per_Sqm",
            color_continuous_scale="Viridis",
            labels={"Price_Per_Sqm": "SAR / m²", "District": "District"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("📈 Deal Price vs. Area (m²)")
        fig_scatter = px.scatter(
            df,
            x="Area_Sqm",
            y="Price_SAR",
            color="Property_Type",
            size="Price_Per_Sqm",
            hover_data=["District", "Time"],
            labels={"Area_Sqm": "Area (m²)", "Price_SAR": "Price (SAR)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # ── 3. جدول الصفقات المباشر ────────────────────────────
    st.subheader("📋 Real-Time Transaction Log")
    st.dataframe(
        df[["Transaction_ID", "Time", "District", "Property_Type", "Area_Sqm", "Price_Per_Sqm", "Price_SAR"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Connecting to data stream... Please wait.")
