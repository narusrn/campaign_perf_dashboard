import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

now_str = datetime.now().strftime("%d-%b-%y")

st.set_page_config(layout="wide")

BLUE   = "#5470c6"
GREEN  = "#91cc75"
YELLOW = "#fac858"
RED    = "#ee6666"
TEAL   = "#73c0de"
ORANGE = "#fc8452"
COLORS = [BLUE, GREEN, YELLOW, RED, TEAL, ORANGE]

def load_data():
    sheet_id = "1OisRn14n89ZKwTd2LDyZbwR9iZOMkT9JUzEORVhHkrE"
    gid = "0"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

df["Visit"] = (
    df["Visit"]
    .str.replace(",", "", regex=False)
    .str.replace("-", "0", regex=False)
    .astype(float)
)
df["Conversion(Users)"] = (
    df["Conversion(Users)"]
    .str.replace(",", "", regex=False)
    .str.replace("-", "0", regex=False)
    .astype(float)
)

df = df.rename(columns={
    "Conversion(Users)": "Conversion",
    "Brand category": "Brand Category",
    "Conversion_rate": "Conversion Rate",
    "Key event": "Key Event"
})

df["Conversion Rate"] = (
    pd.to_numeric(
        df["Conversion Rate"].astype(str).str.replace("%", "", regex=False).str.strip(),
        errors="coerce"
    )
)

df["Start Date Parsed"] = pd.to_datetime(
    df["Start Date"].replace("-", pd.NaT),
    format="%d-%b-%y",
    errors="coerce"
)

# -------------------------
# SIDEBAR FILTERS
# -------------------------
with st.sidebar:
    dark_mode = st.toggle("🌙 Dark Theme", value=False)
    logo_path = "assets/white-logo.png" if dark_mode else "assets/black-logo.png"

    st.divider()
    st.subheader("• Filters")
    brand_cat_filter = st.multiselect(
        "Brand Category",
        options=df["Brand Category"].dropna().unique(),
        default=df["Brand Category"].dropna().unique()
    )
    brand_filter = st.multiselect(
        "Brand",
        options=df["Brand"].dropna().unique(),
        default=df["Brand"].dropna().unique()
    )
    campaign_type_filter = st.multiselect(
        "Campaign Type",
        options=df["Campaign Type"].dropna().unique(),
        default=df["Campaign Type"].dropna().unique()
    )

    st.divider()
    st.subheader("• Date Range")
    valid_dates = df["Start Date Parsed"].dropna()
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    date_range = st.date_input(
        "Start Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# -------------------------
# HEADER
# -------------------------
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image(logo_path, width=80)
with col_title:
    st.title("Campaign Performance Dashboard")

if len(date_range) == 2:
    start_filter, end_filter = date_range
else:
    start_filter, end_filter = min_date, max_date

date_mask = (
    df["Start Date Parsed"].isna() |
    (
        (df["Start Date Parsed"].dt.date >= start_filter) &
        (df["Start Date Parsed"].dt.date <= end_filter)
    )
)

filtered_df = df[
    (df["Brand Category"].isin(brand_cat_filter)) &
    (df["Brand"].isin(brand_filter)) &
    (df["Campaign Type"].isin(campaign_type_filter)) &
    date_mask
]


# -------------------------
# ROW 1: KPI CARDS
# -------------------------
st.subheader("• Overview KPI")

total_campaigns  = len(filtered_df)
total_visits     = int(filtered_df["Visit"].sum())
total_conversions = int(filtered_df["Conversion"].sum())
avg_conv_rate = filtered_df["Conversion Rate"].mean()

k1, k2, k3, k4 = st.columns(4)
with k1:
    with st.container(border=True):
        st.metric("Total Campaigns", f"{total_campaigns:,}")
with k2:
    with st.container(border=True):
        st.metric("Total Visits", f"{total_visits:,}")
with k3:
    with st.container(border=True):
        st.metric("Total Conversions", f"{total_conversions:,}")
with k4:
    with st.container(border=True):
        st.metric("Avg Conversion Rate", f"{avg_conv_rate:.2f}%" if pd.notna(avg_conv_rate) else "N/A")

st.divider()

# -------------------------
# ROW 2: Traffic vs Conversion (3) | Brand Category Donut (2)
# -------------------------
st.subheader("• Traffic & Brand Overview")

col_l, col_r = st.columns([3, 2])

with col_l:
    df_sorted = filtered_df.sort_values("Visit", ascending=False).head(20)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["Campaign Name"], y=df_sorted["Conversion"],
        name="Conversion", marker_color=GREEN, yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=df_sorted["Campaign Name"], y=df_sorted["Visit"],
        mode="lines+markers", name="Visit",
        line=dict(color=BLUE, width=2), yaxis="y2"
    ))
    fig.update_layout(
        title="Traffic vs Conversion per Campaign",
        xaxis=dict(tickangle=-45),
        yaxis=dict(title="Conversion"),
        yaxis2=dict(title="Visit", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400, margin=dict(t=60)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    brand_cat = filtered_df["Brand Category"].value_counts().reset_index()
    brand_cat.columns = ["Brand Category", "Count"]
    fig = px.pie(brand_cat, names="Brand Category", values="Count", hole=0.5,
                 title="Brand Category Distribution",
                 color_discrete_sequence=COLORS)
    fig.update_layout(height=400, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# ROW 3: Campaign Type (1) | Brand Donut (1) | Big Prize (1)
# -------------------------
st.subheader("• Campaign Breakdown")

col1, col2, col3 = st.columns(3)

with col1:
    campaign_type = filtered_df["Campaign Type"].value_counts().reset_index()
    campaign_type.columns = ["Campaign Type", "Count"]
    fig = px.bar(campaign_type, x="Count", y="Campaign Type", orientation="h",
                 title="Campaign Type Distribution",
                 color="Count",
                 color_continuous_scale=[[0, TEAL], [1, BLUE]])
    fig.update_layout(height=350, coloraxis_showscale=False, margin=dict(t=50))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    brand = filtered_df["Brand"].value_counts().reset_index()
    brand.columns = ["Brand", "Count"]
    fig = px.pie(brand, names="Brand", values="Count", hole=0.5,
                 title="Brand Distribution",
                 color_discrete_sequence=COLORS)
    fig.update_layout(height=350, margin=dict(t=50))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    prize_group = filtered_df.groupby("Big Prize")["Conversion"].sum().reset_index()
    fig = px.bar(prize_group, x="Big Prize", y="Conversion",
                 title="Big Prize vs Conversion",
                 color="Conversion",
                 color_continuous_scale=[[0, YELLOW], [1, ORANGE]])
    fig.update_layout(height=350, coloraxis_showscale=False, margin=dict(t=50))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# ROW 4: Key Features (3) | Campaign Ranking Table (2)
# -------------------------
st.subheader("• Campaign Performance Details")

col_l, col_r = st.columns([3, 2])

with col_l:
    feature_group = (
        filtered_df
        .groupby("Campaign Key Features")["Visit"]
        .sum()
        .reset_index()
        .sort_values("Visit", ascending=False)
    )
    fig = px.bar(feature_group, x="Campaign Key Features", y="Visit",
                 title="Campaign Key Features vs Visit",
                 color="Visit",
                 color_continuous_scale=[[0, TEAL], [1, BLUE]])
    fig.update_layout(height=350, coloraxis_showscale=False, margin=dict(t=50))
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown("**• Campaign Ranking**")
    ranking = (
        filtered_df
        .sort_values("Conversion Rate", ascending=False)[
            ["Campaign Name", "Conversion Rate", "Key Event"]
        ]
        .reset_index(drop=True)
    )
    ranking.index += 1
    st.dataframe(ranking, use_container_width=True, height=320)

st.divider()

# -------------------------
# ROW 5: Timeline (Full Width)
# -------------------------
st.subheader("• Campaign Timeline")

filtered_df = filtered_df.copy()
filtered_df["End Date"] = filtered_df["End Date"].replace("-", now_str)
filtered_df["Start Date"] = pd.to_datetime(filtered_df["Start Date"], errors="coerce")
filtered_df["End Date"] = pd.to_datetime(filtered_df["End Date"])

fig = px.timeline(
    filtered_df,
    x_start="Start Date", x_end="End Date",
    y="Campaign Name", color="Brand",
    color_discrete_sequence=COLORS
)
fig.update_yaxes(autorange="reversed")
fig.update_layout(height=500, margin=dict(t=40))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# ROW 6: Overview Table (Full Width)
# -------------------------
st.subheader("• Overview Table")
st.dataframe(filtered_df, use_container_width=True)
