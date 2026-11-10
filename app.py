import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Security Alerts Dashboard",
    page_icon="🚨",
    layout="wide"
)

# Load Excel
@st.cache_data
def load_data():
    alerts = pd.read_excel("project alerts.xlsx", sheet_name="alerts")
    usecases = pd.read_excel("project alerts.xlsx", sheet_name="usecases")
    return alerts, usecases

alerts, usecases = load_data()

st.title("🚨 Security Alerts Dashboard")

# ----------------------------
# KPI SECTION
# ----------------------------

total_alerts = len(alerts)
critical_alerts = len(alerts[alerts["Severity"] == "Critical"])
high_alerts = len(alerts[alerts["Severity"] == "High"])

open_alerts = len(
    alerts[
        alerts["Status"].isin(
            ["In Progress", "Review", "Received"]
        )
    ]
)

enabled_usecases = len(usecases[usecases["is_enabled"] == "T"])

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Alerts", total_alerts)
col2.metric("Critical", critical_alerts)
col3.metric("High", high_alerts)
col4.metric("Open Alerts", open_alerts)
col5.metric("Enabled Use Cases", enabled_usecases)

st.divider()

# ----------------------------
# FILTERS
# ----------------------------

col1, col2 = st.columns(2)

severity_filter = col1.multiselect(
    "Severity",
    alerts["Severity"].dropna().unique(),
    default=alerts["Severity"].dropna().unique()
)

status_filter = col2.multiselect(
    "Status",
    alerts["Status"].dropna().unique(),
    default=alerts["Status"].dropna().unique()
)

filtered_alerts = alerts[
    (alerts["Severity"].isin(severity_filter))
    &
    (alerts["Status"].isin(status_filter))
]

# ----------------------------
# CHARTS
# ----------------------------

c1, c2 = st.columns(2)

with c1:
    fig = px.pie(
        filtered_alerts,
        names="Severity",
        title="Alerts by Severity"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    status_count = filtered_alerts.groupby("Status").size().reset_index(name="Count")

    fig = px.bar(
        status_count,
        x="Status",
        y="Count",
        color="Status",
        title="Alerts by Status"
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# CATEGORY CHART
# ----------------------------

category_count = (
    filtered_alerts.groupby("Category")
    .size()
    .reset_index(name="Count")
)

fig = px.treemap(
    category_count,
    path=["Category"],
    values="Count",
    title="Alerts by Category"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# USE CASES
# ----------------------------

st.subheader("Use Case Status")

usecases["Enabled Status"] = usecases["is_enabled"].apply(
    lambda x: "Enabled" if x == "T" else "Disabled"
)

fig = px.pie(
    usecases,
    names="Enabled Status",
    title="Enabled vs Disabled Use Cases"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# ALERT TABLE
# ----------------------------

st.subheader("Recent Alerts")

st.dataframe(
    filtered_alerts.sort_values(
        "Observation Time",
        ascending=False
    ),
    use_container_width=True
)

# ----------------------------
# USE CASE TABLE
# ----------------------------

st.subheader("Use Cases")

st.dataframe(
    usecases[
        [
            "Name",
            "severity",
            "is_enabled"
        ]
    ],
    use_container_width=True
)