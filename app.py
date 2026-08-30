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

df = fetch_live_deals()

# المؤشرات الحية
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Live Active Deals", len(df))
kpi2.metric("Total Volume (SAR)", f"{df['Price_SAR'].sum():,}")
kpi3.metric("Avg Price / m²", f"{df['Price_Per_Sqm'].mean():,.0f} SAR")
kpi4.metric("Last Transaction Price", f"{df['Price_SAR'].iloc[-1]:,} SAR")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Price Distribution Across Active Districts")
    fig_bar = px.bar(
        df,
        x="District",
        y="Price_SAR",
        color="Property_Type",
        barmode="group",
        labels={"Price_SAR": "Price (SAR)", "District": "District"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("📈 Live Deals Stream by Area vs. Price")
    fig_scatter = px.scatter(
        df,
        x="Area_Sqm",
        y="Price_SAR",
        color="District",
        size="Price_Per_Sqm",
        hover_data=["Property_Type", "Time"]
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

st.subheader("📋 Live Real-Time Transactions Stream")
st.dataframe(df, use_container_width=True)