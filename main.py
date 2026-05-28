import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_echarts import st_echarts, JsCode
from datetime import datetime

now_str = datetime.now().strftime("%d-%b-%y")

st.set_page_config(layout="wide", page_title="Campaign Performance")

COLORS = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#fc8452", "#9a60b4", "#ea7ccc"]

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        opacity: 0.65;
    }

    h3 {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #5470c6 !important;
        margin-bottom: 0.5rem !important;
    }

    hr { border-color: #eef1f7 !important; margin: 0.75rem 0 !important; }

    section[data-testid="stSidebar"] { background: #f4f7ff !important; }
    section[data-testid="stSidebar"] h3 { color: #5470c6 !important; }
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    sheet_id = "1OisRn14n89ZKwTd2LDyZbwR9iZOMkT9JUzEORVhHkrE"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

df["Visit"] = (
    df["Visit"].str.replace(",", "", regex=False).str.replace("-", "0", regex=False).astype(float)
)
df["Conversion(Users)"] = (
    df["Conversion(Users)"].str.replace(",", "", regex=False).str.replace("-", "0", regex=False).astype(float)
)

df = df.rename(columns={
    "Conversion(Users)": "Conversion",
    "Brand category": "Brand Category",
    "Conversion_rate": "Conversion Rate",
    "Key event": "Key Event",
})

df["Conversion Rate"] = pd.to_numeric(
    df["Conversion Rate"].astype(str).str.replace("%", "", regex=False).str.strip(),
    errors="coerce",
)

df["Start Date Parsed"] = pd.to_datetime(
    df["Start Date"].replace("-", pd.NaT), format="%d-%b-%y", errors="coerce"
)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    dark_mode = st.toggle("🌙 Dark Theme", value=False)
    logo_path = "assets/white-logo.png" if dark_mode else "assets/black-logo.png"

    st.divider()
    st.subheader("• Filters")
    brand_cat_filter = st.multiselect(
        "Brand Category",
        options=df["Brand Category"].dropna().unique(),
        default=df["Brand Category"].dropna().unique(),
    )
    brand_filter = st.multiselect(
        "Brand",
        options=df["Brand"].dropna().unique(),
        default=df["Brand"].dropna().unique(),
    )
    campaign_type_filter = st.multiselect(
        "Campaign Type",
        options=df["Campaign Type"].dropna().unique(),
        default=df["Campaign Type"].dropna().unique(),
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
        max_value=max_date,
    )

# -------------------------
# HEADER
# -------------------------
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image(logo_path, width=80)
with col_title:
    st.title("Campaign Performance Dashboard")

# -------------------------
# FILTER LOGIC
# -------------------------
start_filter, end_filter = (date_range if len(date_range) == 2 else (min_date, max_date))

date_mask = df["Start Date Parsed"].isna() | (
    (df["Start Date Parsed"].dt.date >= start_filter)
    & (df["Start Date Parsed"].dt.date <= end_filter)
)

filtered_df = df[
    df["Brand Category"].isin(brand_cat_filter)
    & df["Brand"].isin(brand_filter)
    & df["Campaign Type"].isin(campaign_type_filter)
    & date_mask
]

st.divider()

# -------------------------
# ROW 1: KPI CARDS
# -------------------------
st.subheader("• Overview KPI")

total_campaigns   = len(filtered_df)
total_visits      = int(filtered_df["Visit"].sum())
total_conversions = int(filtered_df["Conversion"].sum())
avg_conv_rate     = filtered_df["Conversion Rate"].mean()

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
    st_echarts(options={
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
        "legend": {"data": ["Conversion", "Visit"], "top": 0},
        "grid": {"left": "3%", "right": "8%", "bottom": "22%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": df_sorted["Campaign Name"].tolist(),
            "axisLabel": {"rotate": 40, "fontSize": 10, "interval": 0},
        },
        "yAxis": [
            {"type": "value", "name": "Conversion"},
            {"type": "value", "name": "Visit", "splitLine": {"show": False}},
        ],
        "series": [
            {
                "name": "Conversion",
                "type": "bar",
                "barMaxWidth": 35,
                "data": df_sorted["Conversion"].astype(int).tolist(),
                "itemStyle": {
                    "color": JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#91cc75'},{offset:1,color:'#57a661'}])").js_code,
                    "borderRadius": [4, 4, 0, 0],
                },
            },
            {
                "name": "Visit",
                "type": "line",
                "yAxisIndex": 1,
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 6,
                "data": df_sorted["Visit"].astype(int).tolist(),
                "lineStyle": {"color": "#5470c6", "width": 2},
                "itemStyle": {"color": "#5470c6"},
                "areaStyle": {
                    "color": JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(84,112,198,0.25)'},{offset:1,color:'rgba(84,112,198,0.0)'}])").js_code
                },
            },
        ],
    }, height="400px")

with col_r:
    brand_cat = filtered_df["Brand Category"].value_counts().reset_index()
    brand_cat.columns = ["Brand Category", "Count"]
    st_echarts(options={
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "top": "center"},
        "series": [{
            "name": "Brand Category",
            "type": "pie",
            "radius": ["45%", "72%"],
            "center": ["62%", "50%"],
            "avoidLabelOverlap": True,
            "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
            "label": {"show": True, "formatter": "{d}%", "fontSize": 11},
            "emphasis": {
                "label": {"show": True, "fontSize": 14, "fontWeight": "bold"},
                "itemStyle": {"shadowBlur": 12, "shadowColor": "rgba(0,0,0,0.2)"},
            },
            "data": [{"value": int(r["Count"]), "name": r["Brand Category"]} for _, r in brand_cat.iterrows()],
            "color": COLORS,
        }],
    }, height="400px")

st.divider()

# -------------------------
# ROW 3: Campaign Type | Brand | Big Prize
# -------------------------
st.subheader("• Campaign Breakdown")

col1, col2, col3 = st.columns(3)

with col1:
    ct = filtered_df["Campaign Type"].value_counts().reset_index()
    ct.columns = ["Campaign Type", "Count"]
    st_echarts(options={
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "15%", "top": "5%", "bottom": "5%", "containLabel": True},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category", "data": ct["Campaign Type"].tolist(), "axisLabel": {"fontSize": 11}},
        "series": [{
            "type": "bar",
            "data": ct["Count"].tolist(),
            "itemStyle": {
                "color": JsCode("new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#5470c6'},{offset:1,color:'#73c0de'}])").js_code,
                "borderRadius": [0, 6, 6, 0],
            },
            "label": {"show": True, "position": "right", "fontSize": 11},
        }],
    }, height="320px")

with col2:
    brand = filtered_df["Brand"].value_counts().reset_index()
    brand.columns = ["Brand", "Count"]
    st_echarts(options={
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "top": "center", "textStyle": {"fontSize": 10}},
        "series": [{
            "name": "Brand",
            "type": "pie",
            "radius": ["45%", "72%"],
            "center": ["65%", "50%"],
            "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
            "label": {"show": False},
            "emphasis": {
                "label": {"show": True, "fontSize": 13, "fontWeight": "bold"},
                "itemStyle": {"shadowBlur": 12, "shadowColor": "rgba(0,0,0,0.2)"},
            },
            "data": [{"value": int(r["Count"]), "name": r["Brand"]} for _, r in brand.iterrows()],
            "color": COLORS,
        }],
    }, height="320px")

with col3:
    prize = filtered_df.groupby("Big Prize")["Conversion"].sum().reset_index()
    prize = prize.sort_values("Conversion", ascending=False)
    st_echarts(options={
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "5%", "top": "8%", "bottom": "18%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": prize["Big Prize"].tolist(),
            "axisLabel": {"rotate": 25, "fontSize": 10},
        },
        "yAxis": {"type": "value"},
        "series": [{
            "type": "bar",
            "data": prize["Conversion"].astype(int).tolist(),
            "itemStyle": {
                "color": JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#fac858'},{offset:1,color:'#fc8452'}])").js_code,
                "borderRadius": [4, 4, 0, 0],
            },
            "label": {"show": True, "position": "top", "fontSize": 10},
        }],
    }, height="320px")

st.divider()

# -------------------------
# ROW 4: Key Features (3) | Campaign Ranking (2)
# -------------------------
st.subheader("• Campaign Performance Details")

col_l, col_r = st.columns([3, 2])

with col_l:
    feat = (
        filtered_df.groupby("Campaign Key Features")["Visit"]
        .sum().reset_index().sort_values("Visit", ascending=False)
    )
    st_echarts(options={
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "5%", "top": "8%", "bottom": "22%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": feat["Campaign Key Features"].tolist(),
            "axisLabel": {"rotate": 30, "fontSize": 10},
        },
        "yAxis": {"type": "value"},
        "series": [{
            "type": "bar",
            "data": feat["Visit"].astype(int).tolist(),
            "itemStyle": {
                "color": JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#73c0de'},{offset:1,color:'#5470c6'}])").js_code,
                "borderRadius": [4, 4, 0, 0],
            },
            "emphasis": {"itemStyle": {"shadowBlur": 8, "shadowColor": "rgba(0,0,0,0.15)"}},
            "label": {"show": True, "position": "top", "fontSize": 10},
        }],
    }, height="340px")

with col_r:
    st.subheader("• Campaign Ranking")
    ranking = (
        filtered_df.sort_values("Conversion Rate", ascending=False)[
            ["Campaign Name", "Conversion Rate", "Key Event"]
        ].reset_index(drop=True)
    )
    ranking.index += 1
    st.dataframe(ranking, use_container_width=True, height=310)

st.divider()

# -------------------------
# ROW 5: Timeline (Full Width)
# -------------------------
st.subheader("• Campaign Timeline")

tl_df = filtered_df.copy()
tl_df["End Date"] = tl_df["End Date"].replace("-", now_str)
tl_df["Start Date"] = pd.to_datetime(tl_df["Start Date"], errors="coerce")
tl_df["End Date"] = pd.to_datetime(tl_df["End Date"])

fig = px.timeline(
    tl_df,
    x_start="Start Date", x_end="End Date",
    y="Campaign Name", color="Brand",
    color_discrete_sequence=COLORS,
)
fig.update_yaxes(autorange="reversed")
fig.update_layout(
    height=520,
    margin=dict(t=30, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------
# ROW 6: Overview Table
# -------------------------
st.subheader("• Overview Table")
st.dataframe(filtered_df, use_container_width=True)
