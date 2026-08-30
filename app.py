import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# ============================================================
# 1. إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="Riyadh Real Estate Live Radar",
    page_icon="🟢",
    layout="wide"
)

# ============================================================
# 2. إعدادات API
# ============================================================

API_BASE_URL = "https://prod-srem-business-api-srem.moj.gov.sa"

# ============================================================
# 3. جلب البيانات من البورصة العقارية
# ============================================================

def get_live_transactions():

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://srem.moj.gov.sa/"
    }

    # نحاول أولاً الوصول إلى الـ API الرسمي
    possible_endpoints = [
        "/api/v1/Transaction",
        "/api/v1/Transactions",
        "/api/v1/transactions",
        "/api/v1/RealEstateTransaction",
        "/api/v1/RealEstateTransactions"
    ]

    last_error = None

    for endpoint in possible_endpoints:

        try:

            url = API_BASE_URL + endpoint

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:

                try:
                    data = response.json()
                except Exception:
                    continue

                # --------------------------------------------
                # التعامل مع أشكال JSON المختلفة
                # --------------------------------------------

                if isinstance(data, dict):

                    for key in [
                        "data",
                        "items",
                        "result",
                        "results",
                        "transactions"
                    ]:
                        if key in data and isinstance(data[key], list):
                            data = data[key]
                            break

                if isinstance(data, list) and len(data) > 0:

                    df = pd.DataFrame(data)

                    return normalize_transactions(df)

        except Exception as e:
            last_error = e

    raise RuntimeError(
        "لم يتم العثور على Endpoint عام للصفقات بدون توثيق. "
        "قد يتطلب API مفتاح وصول أو Token."
    )


# ============================================================
# 4. تنظيف وتحويل بيانات API
# ============================================================

def normalize_transactions(df):

    # نسخة مستقلة
    df = df.copy()

    # أسماء محتملة للحقول
    column_mapping = {

        # رقم الصفقة
        "transactionId": "رقم الصفقة",
        "transactionID": "رقم الصفقة",
        "id": "رقم الصفقة",

        # الحي
        "district": "الحي",
        "districtName": "الحي",
        "neighborhood": "الحي",
        "neighborhoodName": "الحي",

        # نوع العقار
        "propertyType": "نوع العقار",
        "propertyTypeName": "نوع العقار",
        "realEstateType": "نوع العقار",

        # المساحة
        "area": "المساحة (م²)",
        "propertyArea": "المساحة (م²)",
        "space": "المساحة (م²)",

        # سعر المتر
        "pricePerMeter": "سعر المتر (SAR)",
        "meterPrice": "سعر المتر (SAR)",
        "pricePerSquareMeter": "سعر المتر (SAR)",

        # إجمالي الصفقة
        "price": "إجمالي الصفقة (SAR)",
        "transactionPrice": "إجمالي الصفقة (SAR)",
        "totalPrice": "إجمالي الصفقة (SAR)",

        # التاريخ
        "transactionDate": "التاريخ",
        "date": "التاريخ",

        # الوقت
        "transactionTime": "الوقت",
        "time": "الوقت"
    }

    df = df.rename(columns=column_mapping)

    # ========================================================
    # محاولة استخراج الحي من البيانات المتداخلة
    # ========================================================

    if "الحي" not in df.columns:

        possible_columns = [
            "property",
            "realEstate",
            "location",
            "address"
        ]

        for col in possible_columns:

            if col in df.columns:

                try:

                    df["الحي"] = df[col].apply(
                        lambda x:
                        x.get("districtName")
                        if isinstance(x, dict)
                        else None
                    )

                except Exception:
                    pass

                if "الحي" in df.columns:
                    break

    # ========================================================
    # فلترة الرياض
    # ========================================================

    riyadh_keywords = [
        "الرياض",
        "Riyadh",
        "RIYADH"
    ]

    # إذا وجد حقل المدينة
    city_columns = [
        "city",
        "cityName",
        "region",
        "regionName",
        "المدينة",
        "المنطقة"
    ]

    city_column = None

    for col in city_columns:
        if col in df.columns:
            city_column = col
            break

    if city_column:

        df = df[
            df[city_column]
            .astype(str)
            .str.contains(
                "|".join(riyadh_keywords),
                case=False,
                na=False
            )
        ]

    # ========================================================
    # تحويل الأرقام
    # ========================================================

    numeric_columns = [
        "المساحة (م²)",
        "سعر المتر (SAR)",
        "إجمالي الصفقة (SAR)"
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # ========================================================
    # حساب سعر المتر إذا لم يكن موجوداً
    # ========================================================

    if (
        "سعر المتر (SAR)" not in df.columns
        and "المساحة (م²)" in df.columns
        and "إجمالي الصفقة (SAR)" in df.columns
    ):

        df["سعر المتر (SAR)"] = (
            df["إجمالي الصفقة (SAR)"]
            / df["المساحة (م²)"]
        )

    # ========================================================
    # ترتيب الأعمدة
    # ========================================================

    preferred_columns = [
        "رقم الصفقة",
        "التاريخ",
        "الوقت",
        "الحي",
        "نوع العقار",
        "المساحة (م²)",
        "سعر المتر (SAR)",
        "إجمالي الصفقة (SAR)"
    ]

    existing_columns = [
        col for col in preferred_columns
        if col in df.columns
    ]

    other_columns = [
        col for col in df.columns
        if col not in existing_columns
    ]

    df = df[
        existing_columns + other_columns
    ]

    return df


# ============================================================
# 5. الهيدر
# ============================================================

st.title(
    "🟢 Riyadh Real Estate Live Transaction Radar"
)

col_header, col_btn = st.columns([3, 1])

with col_header:

    st.caption(
        f"⚡ Real Estate Exchange Feed • "
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

with col_btn:

    refresh = st.button(
        "🔄 جلب الصفقات الآن",
        use_container_width=True
    )


# ============================================================
# 6. جلب البيانات
# ============================================================

if "data" not in st.session_state:

    try:

        with st.spinner("جاري الاتصال بالبورصة العقارية..."):

            st.session_state["data"] = get_live_transactions()

        st.session_state["api_error"] = None

    except Exception as e:

        st.session_state["data"] = pd.DataFrame()

        st.session_state["api_error"] = str(e)


elif refresh:

    try:

        with st.spinner("جاري تحديث الصفقات..."):

            st.session_state["data"] = get_live_transactions()

        st.session_state["api_error"] = None

        st.success("تم تحديث البيانات.")

    except Exception as e:

        st.session_state["api_error"] = str(e)


df = st.session_state["data"]


# ============================================================
# 7. رسالة API
# ============================================================

if st.session_state.get("api_error"):

    st.error(
        "⚠️ لم يتم جلب البيانات الحقيقية من API البورصة العقارية."
    )

    st.warning(
        st.session_state["api_error"]
    )

    st.info(
        "الواجهة تعمل، لكن يجب تحديد Endpoint البيانات العام "
        "أو إضافة بيانات الاعتماد الخاصة بالـAPI."
    )

    st.stop()


# ============================================================
# 8. التأكد من وجود بيانات
# ============================================================

if df.empty:

    st.warning(
        "لا توجد صفقات متاحة حالياً من المصدر."
    )

    st.stop()


# ============================================================
# 9. KPIs
# ============================================================

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "عدد الصفقات",
    f"{len(df):,}"
)

if "إجمالي الصفقة (SAR)" in df.columns:

    total_volume = df[
        "إجمالي الصفقة (SAR)"
    ].sum()

    k2.metric(
        "إجمالي حجم التداول",
        f"{total_volume:,.0f} ريال"
    )

else:

    k2.metric(
        "إجمالي حجم التداول",
        "غير متاح"
    )


if "سعر المتر (SAR)" in df.columns:

    avg_price = df[
        "سعر المتر (SAR)"
    ].dropna().mean()

    k3.metric(
        "متوسط سعر المتر",
        f"{avg_price:,.0f} ريال/م²"
    )

else:

    k3.metric(
        "متوسط سعر المتر",
        "غير متاح"
    )


if "إجمالي الصفقة (SAR)" in df.columns:

    latest_price = df[
        "إجمالي الصفقة (SAR)"
    ].iloc[0]

    k4.metric(
        "أحدث صفقة",
        f"{latest_price:,.0f} ريال"
    )

else:

    k4.metric(
        "أحدث صفقة",
        "غير متاح"
    )


st.markdown("---")


# ============================================================
# 10. الرسوم البيانية
# ============================================================

c1, c2 = st.columns(2)


with c1:

    st.subheader(
        "📊 أعلى 10 أحياء حسب سعر المتر"
    )

    if (
        "الحي" in df.columns
        and "سعر المتر (SAR)" in df.columns
    ):

        avg_price = (
            df.groupby("الحي")[
                "سعر المتر (SAR)"
            ]
            .mean()
            .reset_index()
            .sort_values(
                "سعر المتر (SAR)",
                ascending=False
            )
            .head(10)
        )

        fig_bar = px.bar(
            avg_price,
            x="الحي",
            y="سعر المتر (SAR)",
            color="سعر المتر (SAR)",
            color_continuous_scale="Viridis"
        )

        fig_bar.update_layout(
            xaxis_title="الحي",
            yaxis_title="سعر المتر (SAR)"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    else:

        st.info(
            "بيانات الحي أو سعر المتر غير متوفرة من المصدر."
        )


with c2:

    st.subheader(
        "📈 توزيع المساحة مقابل السعر"
    )

    required_columns = [
        "المساحة (م²)",
        "إجمالي الصفقة (SAR)"
    ]

    if all(
        col in df.columns
        for col in required_columns
    ):

        scatter_kwargs = {
            "data_frame": df,
            "x": "المساحة (م²)",
            "y": "إجمالي الصفقة (SAR)"
        }

        if "نوع العقار" in df.columns:

            scatter_kwargs[
                "color"
            ] = "نوع العقار"

        if "سعر المتر (SAR)" in df.columns:

            scatter_kwargs[
                "size"
            ] = "سعر المتر (SAR)"

        hover_columns = []

        if "الحي" in df.columns:
            hover_columns.append("الحي")

        if "التاريخ" in df.columns:
            hover_columns.append("التاريخ")

        if "الوقت" in df.columns:
            hover_columns.append("الوقت")

        scatter_kwargs[
            "hover_data"
        ] = hover_columns

        fig_scatter = px.scatter(
            **scatter_kwargs
        )

        fig_scatter.update_layout(
            xaxis_title="المساحة (م²)",
            yaxis_title="إجمالي الصفقة (SAR)"
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )

    else:

        st.info(
            "بيانات المساحة أو قيمة الصفقة غير متوفرة."
        )


# ============================================================
# 11. جدول الصفقات
# ============================================================

st.markdown("---")

st.subheader(
    "📋 جدول الإفراغات والصفقات الحية"
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
