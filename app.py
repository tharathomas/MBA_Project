import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="Security Alerts Dashboard",
    page_icon="🚨",
    layout="wide"
)

# ==========================================
# GOOGLE SHEET ID
# ==========================================

SHEET_ID = "1a3NsUwxRp63NYsX-9w2mk58J-3uS-kHKPcXJIYvpWjc"

# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data(ttl=30)
def load_data():

    alerts_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=alerts"
    )

    usecases_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=usecases"
    )

    alerts = pd.read_csv(alerts_url)
    usecases = pd.read_csv(usecases_url)

    return alerts, usecases

# ==========================================
# REFRESH SECTION
# ==========================================

col1, col2 = st.columns([1, 4])

with col1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.success(
        f"Last Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}"
    )

alerts, usecases = load_data()

# ==========================================
# TITLE
# ==========================================

st.title("🚨 Security Alerts Dashboard")

# ==========================================
# KPI CALCULATIONS
# ==========================================

total_alerts = len(alerts)

critical_alerts = len(
    alerts[
        alerts["Severity"]
        .astype(str)
        .str.upper()
        .eq("CRITICAL")
    ]
)

high_alerts = len(
    alerts[
        alerts["Severity"]
        .astype(str)
        .str.upper()
        .eq("HIGH")
    ]
)

open_alerts = len(
    alerts[
        alerts["Status"]
        .astype(str)
        .isin(
            [
                "In Progress",
                "Review",
                "Received"
            ]
        )
    ]
)

enabled_usecases = len(
    usecases[
        usecases["is_enabled"]
        .astype(str)
        .str.upper()
        .eq("T")
    ]
)

# ==========================================
# KPI CARDS
# ==========================================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Alerts", total_alerts)
c2.metric("Critical Alerts", critical_alerts)
c3.metric("High Alerts", high_alerts)
c4.metric("Open Alerts", open_alerts)
c5.metric("Enabled Use Cases", enabled_usecases)

st.divider()

# ==========================================
# FILTERS
# ==========================================

st.sidebar.header("Filters")

severity_filter = st.sidebar.multiselect(
    "Severity",
    alerts["Severity"].dropna().unique(),
    default=alerts["Severity"].dropna().unique()
)

status_filter = st.sidebar.multiselect(
    "Status",
    alerts["Status"].dropna().unique(),
    default=alerts["Status"].dropna().unique()
)

filtered_alerts = alerts[
    alerts["Severity"].isin(severity_filter)
]

filtered_alerts = filtered_alerts[
    filtered_alerts["Status"].isin(status_filter)
]

# ==========================================
# CHARTS
# ==========================================

left, right = st.columns(2)

with left:

    fig1 = px.pie(
        filtered_alerts,
        names="Severity",
        title="Alerts By Severity"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with right:

    status_count = (
        filtered_alerts
        .groupby("Status")
        .size()
        .reset_index(name="Count")
    )

    fig2 = px.bar(
        status_count,
        x="Status",
        y="Count",
        color="Status",
        title="Alerts By Status"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ==========================================
# CATEGORY TREEMAP
# ==========================================

category_count = (
    filtered_alerts
    .groupby("Category")
    .size()
    .reset_index(name="Count")
)

fig3 = px.treemap(
    category_count,
    path=["Category"],
    values="Count",
    title="Alerts By Category"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ==========================================
# USE CASE STATUS
# ==========================================

st.subheader("Use Case Status")

usecases["Enabled Status"] = (
    usecases["is_enabled"]
    .astype(str)
    .apply(
        lambda x:
        "Enabled"
        if x.upper() == "T"
        else "Disabled"
    )
)

fig4 = px.pie(
    usecases,
    names="Enabled Status",
    title="Enabled vs Disabled Use Cases"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# ==========================================
# ALERTS TABLE
# ==========================================

st.subheader("Recent Alerts")

st.dataframe(
    filtered_alerts,
    use_container_width=True,
    height=450
)

# ==========================================
# DOWNLOAD CSV
# ==========================================

csv = filtered_alerts.to_csv(
    index=False
)

st.download_button(
    label="📥 Download Filtered Alerts",
    data=csv,
    file_name="filtered_alerts.csv",
    mime="text/csv"
)