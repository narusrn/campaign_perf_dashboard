import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts, JsCode
from datetime import datetime
from dotenv import load_dotenv

from ai_summary import generate_ai_summary
from common import BRAND_COLORS, COLORS, img_to_html, kpi_card, load_campaigns, stable_colors

load_dotenv()

now_str = datetime.now().strftime("%d-%b-%y")

cached_ai_summary = st.cache_data(ttl=86400, show_spinner="กำลังวิเคราะห์แคมเปญ...")(generate_ai_summary)

st.set_page_config(layout="wide", page_title="Campaign Performance")

def _lighten(hex_color, factor):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c + (255 - c) * factor) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def nested_brand_donut(df, title, inner_col, inner_colors):
    center = ["50%", "58%"]

    inner_counts = df[inner_col].value_counts()
    inner, outer = [], []
    for group, count in inner_counts.items():
        group_color = inner_colors.get(group, "#94a3b8")
        inner.append({"value": int(count), "name": group, "itemStyle": {"color": group_color}})
        brand_counts = df.loc[df[inner_col] == group, "Brand"].value_counts()
        for j, (brand, bcount) in enumerate(brand_counts.items()):
            outer.append({
                "value": int(bcount),
                "name": brand,
                "itemStyle": {"color": _lighten(group_color, min(0.55, 0.1 * j))},
            })

    return {
        "title": [
            {"text": title, "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
        ],
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {
            "orient": "horizontal", "left": "center", "top": 26,
            "textStyle": {"fontSize": 11}, "data": inner_counts.index.tolist(),
        },
        "series": [
            {
                "name": inner_col,
                "type": "pie",
                "radius": ["0%", "32%"],
                "center": center,
                "minAngle": 4,
                "itemStyle": {"borderRadius": 4, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": True, "position": "inner", "formatter": "{b}", "fontSize": 11, "color": "#fff", "fontWeight": "600"},
                "emphasis": {"scale": True, "scaleSize": 6, "itemStyle": {"shadowBlur": 14, "shadowColor": "rgba(0,0,0,0.25)"}},
                "data": inner,
            },
            {
                "name": "Brand",
                "type": "pie",
                "radius": ["40%", "58%"],
                "center": center,
                "minAngle": 3,
                "avoidLabelOverlap": True,
                "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 2},
                "label": {
                    "show": True, "position": "outside", "formatter": "{b}",
                    "fontSize": 10, "color": "#334155",
                },
                "labelLine": {"show": True, "length": 6, "length2": 6, "lineStyle": {"color": "#cbd5e1"}},
                "emphasis": {"scale": True, "scaleSize": 6, "itemStyle": {"shadowBlur": 14, "shadowColor": "rgba(0,0,0,0.25)"}},
                "data": outer,
            },
        ],
    }


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: 'Inter', sans-serif !important;
}

.stApp { background: #f0f4f8 !important; }
.block-container { padding-top: 0.5rem !important; padding-bottom: 1rem; }

h3 {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #1e293b !important;
    margin-bottom: 0.3rem !important;
    margin-top: 0.2rem !important;
    padding-left: 12px !important;
    border-left: 4px solid #5470c6 !important;
}

hr { border-color: #e2e8f0 !important; margin: 0.35rem 0 !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
section[data-testid="stSidebar"] h3 {
    color: #1e293b !important;
    border-left-color: #5470c6 !important;
}
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.07) !important;
    border: 1px solid #e2e8f0 !important;
    background: white !important;
    height: 100% !important;
    box-sizing: border-box !important;
}

[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}

[data-testid="column"] > div:first-child {
    height: 100% !important;
}

@media print {
    section[data-testid="stSidebar"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header { display: none !important; }

    .stApp, .block-container {
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        width: 100% !important;
        gap: 12px !important;
        break-inside: avoid !important;
    }

    [data-testid="column"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        break-inside: avoid !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
        box-shadow: none !important;
        border: 1px solid #e2e8f0 !important;
    }

    iframe {
        width: 100% !important;
    }

    h3 {
        break-after: avoid !important;
        page-break-after: avoid !important;
    }

    hr {
        break-after: avoid !important;
        page-break-after: avoid !important;
    }

    [data-testid="stVerticalBlock"] {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
    }
}

</style>
""", unsafe_allow_html=True)


df = load_campaigns()
TYPE_COLORS = stable_colors(df, "Campaign Type")
CATEGORY_COLORS = stable_colors(df, "Brand Category")

# -------------------------
# SIDEBAR
# -------------------------
logo_path = "assets/black-logo.png"

with st.sidebar:
    st.markdown(img_to_html("assets/black-logo.png", height=36), unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)
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
    valid_dates = df["Start Date Parsed"].dropna()
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )


# -------------------------
# HEADER
# -------------------------
st.markdown(
    f'<div style="display:flex;align-items:center;gap:14px;padding:48px 0 12px 0;">'
    f'{img_to_html(logo_path, height=52)}'
    f'<div>'
    f'<div style="font-size:2rem;font-weight:800;color:#1e293b;line-height:1.1;'
    f'font-family:Inter,sans-serif;letter-spacing:-0.02em;">Campaign Performance Dashboard</div>'
    f'<div style="font-size:0.82rem;color:#64748b;margin-top:3px;font-family:Inter,sans-serif;">'
    f'As of {now_str}</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

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
active_campaigns  = filtered_df[filtered_df["Conversion"] > 0]
avg_conv_per_campaign = (
    active_campaigns["Conversion"].sum() / len(active_campaigns) if len(active_campaigns) else 0
)
avg_conv_rate     = filtered_df["Conversion Rate"].mean()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_card("Total Campaigns", f"{total_campaigns:,}", "#5470c6", "#73c0de"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Total Visits", f"{total_visits:,}", "#57a661", "#91cc75"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Avg Conversion by Campaign", f"{avg_conv_per_campaign:,.1f}", "#e07b39", "#fac858"), unsafe_allow_html=True)
with k4:
    conv_val = f"{avg_conv_rate:.2f}%" if pd.notna(avg_conv_rate) else "N/A"
    st.markdown(kpi_card("Avg Conversion Rate", conv_val, "#9a60b4", "#ea7ccc"), unsafe_allow_html=True)

st.divider()

# -------------------------
# AI Summary
# -------------------------
st.subheader("• AI Summary")
with st.container(border=True):
    st.markdown(cached_ai_summary(filtered_df))

st.divider()

# -------------------------
# ROW 2: Traffic vs Conversion (3) | Brand Category Donut (2)
# -------------------------
st.subheader("• Traffic & Brand Overview")

col_l, col_r = st.columns([3, 2])

with col_l:
    with st.container(border=True):
        df_sorted = filtered_df.sort_values("Visit", ascending=False).head(20)
        # ponytail: truncate in Python, not via echarts axisLabel overflow — containLabel
        # sizes the grid off the full untruncated string, leaving a big blank margin
        # once the label actually renders short. Truncating the data itself keeps what's
        # measured and what's shown in sync.
        short_names = [n if len(n) <= 16 else n[:15] + "…" for n in df_sorted["Campaign Name"]]
        clicked_index = st_echarts(options={
            "title": {"text": "Traffic vs Conversion  ·  Top 20 Campaigns", "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "legend": {"data": ["Conversion", "Visit"], "top": 28},
            "grid": {"left": "3%", "right": "8%", "bottom": "16%", "top": "14%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": short_names,
                "axisLabel": {"rotate": 40, "fontSize": 11, "interval": 0},
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
                        "color": "#57a661",
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
                        "color": "rgba(84,112,198,0.15)"
                    },
                },
            ],
        }, height="400px", events={"click": "function(params) { return params.dataIndex; }"})
    st.caption("💡 คลิกที่แคมเปญในกราฟเพื่อดูรายละเอียดเพิ่มเติม")
    if clicked_index is not None:
        st.session_state["selected_campaign"] = df_sorted.iloc[int(clicked_index)]["Campaign Name"]
        st.switch_page("pages/1_Campaign_Detail.py")

with col_r:
    with st.container(border=True):
        st_echarts(
            options=nested_brand_donut(filtered_df, "Brand Category → Brand", "Brand Category", CATEGORY_COLORS),
            height="400px",
        )

st.divider()

# -------------------------
# ROW 3: Campaign Type | Brand | Big Prize
# -------------------------
st.subheader("• Campaign Breakdown")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    with st.container(border=True):
        ct = filtered_df["Campaign Type"].value_counts().reset_index()
        ct.columns = ["Campaign Type", "Count"]
        st_echarts(options={
            "title": {"text": "By Campaign Type", "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "3%", "right": "15%", "top": "16%", "bottom": "8%", "containLabel": True},
            "xAxis": {"type": "value", "name": "Campaigns", "nameLocation": "end", "nameTextStyle": {"fontSize": 11, "color": "#94a3b8"}},
            "yAxis": {"type": "category", "data": ct["Campaign Type"].tolist(), "axisLabel": {"fontSize": 13}},
            "series": [{
                "type": "bar",
                "data": ct["Count"].tolist(),
                "itemStyle": {
                    "color": "#5470c6",
                    "borderRadius": [0, 6, 6, 0],
                },
                "label": {"show": True, "position": "right", "fontSize": 13},
            }],
        }, height="360px")

with col2:
    with st.container(border=True):
        st_echarts(
            options=nested_brand_donut(filtered_df, "Campaign Type → Brand", "Campaign Type", TYPE_COLORS),
            height="360px",
        )

with col3:
    with st.container(border=True):
        prize = filtered_df.groupby("Big Prize")["Conversion"].sum().reset_index()
        prize = prize.sort_values("Conversion", ascending=False)
        st_echarts(options={
            "title": {"text": "Conversions by Prize Theme", "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "3%", "right": "5%", "top": "18%", "bottom": "20%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": prize["Big Prize"].tolist(),
                "axisLabel": {"rotate": 25, "fontSize": 12},
            },
            "yAxis": {"type": "value", "name": "Conversions", "nameTextStyle": {"fontSize": 11, "color": "#94a3b8"}},
            "series": [{
                "type": "bar",
                "data": prize["Conversion"].astype(int).tolist(),
                "itemStyle": {
                    "color": "#fc8452",
                    "borderRadius": [4, 4, 0, 0],
                },
                "label": {"show": True, "position": "top", "fontSize": 12},
            }],
        }, height="360px")

st.divider()

# -------------------------
# ROW 4: Key Features (3) | Campaign Ranking (2)
# -------------------------
col_labels = st.columns([3, 2])
col_labels[0].subheader("• Campaign Key Features vs Visit")
col_labels[1].subheader("• Campaign Ranking")

col_l, col_r = st.columns([3, 2])

with col_l:
    with st.container(border=True):
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
                "axisLabel": {"rotate": 30, "fontSize": 12},
            },
            "yAxis": {"type": "value", "name": "Total Visits", "nameTextStyle": {"fontSize": 11, "color": "#94a3b8"}},
            "series": [{
                "type": "bar",
                "data": feat["Visit"].astype(int).tolist(),
                "itemStyle": {
                    "color": "#73c0de",
                    "borderRadius": [4, 4, 0, 0],
                },
                "emphasis": {"itemStyle": {"shadowBlur": 8, "shadowColor": "rgba(0,0,0,0.15)"}},
                "label": {"show": True, "position": "top", "fontSize": 12},
            }],
        }, height="390px")

with col_r:
    with st.container(border=True):
        ranking = (
            filtered_df.sort_values("Conversion Rate", ascending=False)
            .head(10)[["Campaign Name", "Conversion Rate"]]
            .reset_index(drop=True)
        )
        st_echarts(options={
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "formatter": JsCode("function(p){return p[0].name + '<br/>Conversion Rate: <b>' + p[0].value + '%</b>'}").js_code,
            },
            "grid": {"left": "126px", "right": "16%", "top": "3%", "bottom": "3%"},
            "xAxis": {"type": "value", "name": "Conversion Rate (%)", "nameLocation": "end", "nameTextStyle": {"fontSize": 11, "color": "#94a3b8"}, "axisLabel": {"formatter": "{value}%"}},
            "yAxis": {
                "type": "category",
                "data": ranking["Campaign Name"].tolist()[::-1],
                "axisLabel": {"fontSize": 12, "width": 120, "overflow": "truncate"},
            },
            "series": [{
                "type": "bar",
                "data": ranking["Conversion Rate"].round(2).tolist()[::-1],
                "itemStyle": {
                    "color": "#5470c6",
                    "borderRadius": [0, 6, 6, 0],
                },
                "label": {"show": True, "position": "right", "fontSize": 12, "formatter": "{c}%"},
            }],
        }, height="390px")

st.divider()

# -------------------------
# ROW 5: Timeline (Full Width)
# -------------------------
st.subheader("• Campaign Timeline")

with st.container(border=True):
    tl_df = filtered_df.copy()
    tl_df["End Date"] = tl_df["End Date"].replace("-", now_str)
    tl_df["Start Date Ts"] = pd.to_datetime(tl_df["Start Date"], errors="coerce")
    tl_df["End Date Ts"] = pd.to_datetime(tl_df["End Date"], errors="coerce")

    n_total    = len(filtered_df)
    n_upcoming = int((filtered_df["Start Date"] == "-").sum())

    tl_df = tl_df.dropna(subset=["Start Date Ts", "End Date Ts"])

    if not tl_df.empty:
        today     = pd.Timestamp.now().normalize()
        n_running = int(((tl_df["Start Date Ts"] <= today) & (tl_df["End Date Ts"] >= today)).sum())
        n_closed  = int((tl_df["End Date Ts"] < today).sum())

        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap;">
            <div style="flex:1;min-width:110px;background:#f8fafc;border:1px solid #e2e8f0;
                        border-radius:10px;padding:12px 16px;">
                <div style="font-size:0.7rem;font-weight:700;color:#64748b;text-transform:uppercase;
                            letter-spacing:0.08em;">Total</div>
                <div style="font-size:1.6rem;font-weight:800;color:#1e293b;line-height:1.1;">{n_total}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#f0fdf4;border:1px solid #bbf7d0;
                        border-radius:10px;padding:12px 16px;">
                <div style="font-size:0.7rem;font-weight:700;color:#16a34a;text-transform:uppercase;
                            letter-spacing:0.08em;">Running</div>
                <div style="font-size:1.6rem;font-weight:800;color:#15803d;line-height:1.1;">{n_running}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#fff7ed;border:1px solid #fed7aa;
                        border-radius:10px;padding:12px 16px;">
                <div style="font-size:0.7rem;font-weight:700;color:#ea580c;text-transform:uppercase;
                            letter-spacing:0.08em;">Upcoming</div>
                <div style="font-size:1.6rem;font-weight:800;color:#c2410c;line-height:1.1;">{n_upcoming}</div>
            </div>
            <div style="flex:1;min-width:110px;background:#f8fafc;border:1px solid #e2e8f0;
                        border-radius:10px;padding:12px 16px;">
                <div style="font-size:0.7rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
                            letter-spacing:0.08em;">Closed</div>
                <div style="font-size:1.6rem;font-weight:800;color:#64748b;line-height:1.1;">{n_closed}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        campaigns_order = tl_df["Campaign Name"].unique().tolist()
        brands_list = tl_df["Brand"].dropna().unique().tolist()
        y_categories = campaigns_order[::-1]
        rows_by_campaign = {row["Campaign Name"]: row for _, row in tl_df.iterrows()}

        axis_min = int((tl_df["Start Date Ts"].min() - pd.Timedelta(days=3)).timestamp() * 1000)
        axis_max = int((tl_df["End Date Ts"].max() + pd.Timedelta(days=3)).timestamp() * 1000)

        # ponytail: JsCode must be single-line here — this frontend's placeholder
        # regex doesn't match across newlines, so a pretty multi-line function
        # silently fails to evaluate and renders as literal text instead.
        axis_label_fmt = JsCode(
            "function(val) { var d = new Date(val); var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; "
            "return ('0'+d.getDate()).slice(-2) + ' ' + months[d.getMonth()]; }"
        ).js_code

        tooltip_fmt = JsCode(
            "function(params) { if (!params.data || params.data.value == null) { return ''; } "
            "var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; "
            "var fmt = function(ts) { var d = new Date(ts); return ('0'+d.getDate()).slice(-2) + ' ' + months[d.getMonth()] + ' ' + d.getFullYear(); }; "
            "return '<b>' + params.data.campaign + '</b><br/>' + 'Brand: ' + params.seriesName + '<br/>' + "
            "'Start: ' + fmt(params.data.start) + '<br/>' + 'End: ' + fmt(params.data.end); }"
        ).js_code

        # ponytail: stacked bar (invisible offset + visible duration) instead of a
        # "custom" renderItem series — the bundled echarts build here doesn't
        # support api.size() in custom series, so a plain bar+stack Gantt is used.
        series = []
        for i, brand in enumerate(brands_list):
            color = _lighten(BRAND_COLORS.get(brand, COLORS[i % len(COLORS)]), 0.45)
            offset_data, duration_data = [], []
            for campaign in y_categories:
                row = rows_by_campaign[campaign]
                if row["Brand"] == brand:
                    start_ms = int(row["Start Date Ts"].timestamp() * 1000)
                    end_ms = int(row["End Date Ts"].timestamp() * 1000)
                    offset_data.append(start_ms)
                    duration_data.append({
                        "value": max(end_ms - start_ms, 86400000),
                        "start": start_ms, "end": end_ms, "campaign": campaign,
                    })
                else:
                    offset_data.append(0)
                    duration_data.append(0)
            series.append({
                "name": f"{brand}__offset", "type": "bar", "stack": "gantt",
                "silent": True, "itemStyle": {"color": "transparent"}, "data": offset_data,
            })
            series.append({
                "name": brand, "type": "bar", "stack": "gantt", "barMaxWidth": 22,
                "itemStyle": {"color": color, "borderRadius": [3, 3, 3, 3]},
                "data": duration_data,
            })

        st_echarts(options={
            "tooltip": {"trigger": "item", "formatter": tooltip_fmt},
            "legend": {"data": brands_list, "top": 4, "type": "scroll", "textStyle": {"fontSize": 12}},
            "grid": {"left": "170px", "right": "2%", "top": "12%", "bottom": "4%"},
            "xAxis": {
                "type": "value",
                "min": axis_min,
                "max": axis_max,
                "axisLabel": {"fontSize": 11, "formatter": axis_label_fmt},
                "splitLine": {
                    "show": True,
                    "lineStyle": {"type": "dashed", "color": "#cbd5e1", "width": 1},
                },
            },
            "yAxis": {
                "type": "category",
                "data": y_categories,
                "axisLabel": {"fontSize": 11, "width": 160, "overflow": "truncate"},
            },
            "series": series,
        }, height="520px")

st.divider()

# -------------------------
# ROW 6: Overview Table
# -------------------------
st.subheader("• Overview Table")
with st.container(border=True):
    st.dataframe(filtered_df, use_container_width=True)
