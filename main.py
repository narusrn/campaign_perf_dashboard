import streamlit as st
import pandas as pd
import base64
from streamlit_echarts import st_echarts, JsCode
from datetime import datetime
from dotenv import load_dotenv

from ai_summary import generate_ai_summary

load_dotenv()

now_str = datetime.now().strftime("%d-%b-%y")

cached_ai_summary = st.cache_data(ttl=86400, show_spinner="กำลังวิเคราะห์แคมเปญ...")(generate_ai_summary)

st.set_page_config(layout="wide", page_title="Campaign Performance")

def img_to_html(path, height=50):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f'<img src="data:image/png;base64,{encoded}" style="height:{height}px;width:auto;display:block;">'

def kpi_card(label, value, c1, c2):
    return f'''<div style="
        background:linear-gradient(135deg,{c1},{c2});
        border-radius:16px;padding:22px 20px;color:white;
        box-shadow:0 4px 18px rgba(0,0,0,0.13);
        display:flex;flex-direction:column;gap:10px;">
        <div style="font-size:0.75rem;font-weight:700;opacity:0.88;
                    text-transform:uppercase;letter-spacing:0.1em;">{label}</div>
        <div style="font-size:2.2rem;font-weight:800;line-height:1.0;">{value}</div>
    </div>'''

COLORS = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#fc8452", "#9a60b4", "#ea7ccc"]

BRAND_COLORS = {
    "Unilever": "#0606A2",
    "Comfort":  "#043677",
    "Breeze":   "#00BD00",
    "Hygiene":  "#0606A2",
    "Downy":    "#0606A2",
    "Vaseline": "#00B0E9",
    "Lipon F":  "#0606A2",
    "Rexona":   "#00CFD3",
    "OMO":      "#0606A2",
    "Fineline": "#0606A2",
    "Sunlight": "#FFE700",
    "Knorr":    "#007624",
    "Ponds":    "#F874AF",
    "Axe":      "#201D1D",
    "LUX":               "#B07C65",
    "Unilever Brand Range": "#0606A2",
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
with open(logo_path, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()
st.markdown(
    f'<div style="display:flex;align-items:center;gap:14px;padding:48px 0 12px 0;">'
    f'<img src="data:image/png;base64,{logo_b64}" style="height:52px;width:auto;">'
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
# ROW 2: Traffic vs Conversion (3) | Brand Category Donut (2)
# -------------------------
st.subheader("• Traffic & Brand Overview")

col_l, col_r = st.columns([3, 2])

with col_l:
    with st.container(border=True):
        df_sorted = filtered_df.sort_values("Visit", ascending=False).head(20)
        st_echarts(options={
            "title": {"text": "Traffic vs Conversion  ·  Top 20 Campaigns", "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "legend": {"data": ["Conversion", "Visit"], "top": 28},
            "grid": {"left": "3%", "right": "8%", "bottom": "16%", "top": "14%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": df_sorted["Campaign Name"].tolist(),
                "axisLabel": {"rotate": 40, "fontSize": 11, "interval": 0, "overflow": "truncate", "width": 80},
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
        }, height="330px")

with col_r:
    with st.container(border=True):
        brand_cat = filtered_df["Brand Category"].value_counts().reset_index()
        brand_cat.columns = ["Brand Category", "Count"]
        st_echarts(options={
            "title": {"text": "Brand Category Mix", "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
            "legend": {"orient": "vertical", "left": "left", "top": "center"},
            "series": [{
                "name": "Brand Category",
                "type": "pie",
                "radius": ["45%", "72%"],
                "center": ["62%", "50%"],
                "avoidLabelOverlap": True,
                "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": True, "formatter": "{d}%", "fontSize": 13},
                "emphasis": {
                    "label": {"show": True, "fontSize": 16, "fontWeight": "bold"},
                    "itemStyle": {"shadowBlur": 12, "shadowColor": "rgba(0,0,0,0.2)"},
                },
                "data": [{"value": int(r["Count"]), "name": r["Brand Category"]} for _, r in brand_cat.iterrows()],
                "color": COLORS,
            }],
        }, height="330px")

st.divider()

# -------------------------
# ROW 3: Campaign Type | Brand | Big Prize
# -------------------------
st.subheader("• Campaign Breakdown")

col1, col2, col3 = st.columns(3)

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
                    "color": JsCode("new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#5470c6'},{offset:1,color:'#73c0de'}])").js_code,
                    "borderRadius": [0, 6, 6, 0],
                },
                "label": {"show": True, "position": "right", "fontSize": 13},
            }],
        }, height="460px")

with col2:
    with st.container(border=True):
        brand = filtered_df["Brand"].value_counts().reset_index()
        brand.columns = ["Brand", "Count"]
        st_echarts(options={
            "title": {"text": "By Brand", "left": "center", "top": 4, "textStyle": {"fontSize": 12, "fontWeight": "600", "color": "#64748b"}},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
            "legend": {"orient": "vertical", "left": "left", "top": "middle", "textStyle": {"fontSize": 12}},
            "series": [{
                "name": "Brand",
                "type": "pie",
                "radius": ["45%", "72%"],
                "center": ["65%", "50%"],
                "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": False},
                "emphasis": {
                    "label": {"show": True, "fontSize": 15, "fontWeight": "bold"},
                    "itemStyle": {"shadowBlur": 12, "shadowColor": "rgba(0,0,0,0.2)"},
                },
                "data": [{"value": int(r["Count"]), "name": r["Brand"], "itemStyle": {"color": BRAND_COLORS.get(r["Brand"], COLORS[i % len(COLORS)])}} for i, (_, r) in enumerate(brand.iterrows())],
            }],
        }, height="460px")

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
                    "color": JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#fac858'},{offset:1,color:'#fc8452'}])").js_code,
                    "borderRadius": [4, 4, 0, 0],
                },
                "label": {"show": True, "position": "top", "fontSize": 12},
            }],
        }, height="460px")

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
                    "color": JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#73c0de'},{offset:1,color:'#5470c6'}])").js_code,
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
            "grid": {"left": "3%", "right": "18%", "top": "3%", "bottom": "3%", "containLabel": True},
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
                    "color": JsCode("new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#5470c6'},{offset:1,color:'#91cc75'}])").js_code,
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

        render_item = JsCode("""
        function(params, api) {
            var idx   = api.value(0);
            var start = api.coord([api.value(1), idx]);
            var end   = api.coord([api.value(2), idx]);
            var h     = api.size([0, 1])[1] * 0.8;
            return {
                type: 'rect',
                shape: { x: start[0], y: start[1] - h / 2,
                         width: Math.max(end[0] - start[0], 2), height: h },
                style: api.style()
            };
        }
        """).js_code

        tooltip_fmt = JsCode("""
        function(params) {
            var s = new Date(params.value[1]);
            var e = new Date(params.value[2]);
            var months = ['Jan','Feb','Mar','Apr','May','Jun',
                          'Jul','Aug','Sep','Oct','Nov','Dec'];
            var fmt = function(d) {
                return ('0'+d.getDate()).slice(-2) + ' ' +
                       months[d.getMonth()] + ' ' + d.getFullYear();
            };
            return '<b>' + params.value[3] + '</b><br/>' +
                   'Brand: ' + params.seriesName + '<br/>' +
                   'Start: ' + fmt(s) + '<br/>' +
                   'End: '   + fmt(e);
        }
        """).js_code

        series = []
        for i, brand in enumerate(brands_list):
            bdf = tl_df[tl_df["Brand"] == brand]
            data = []
            for _, row in bdf.iterrows():
                data.append({"value": [
                    campaigns_order.index(row["Campaign Name"]),
                    int(row["Start Date Ts"].timestamp() * 1000),
                    int(row["End Date Ts"].timestamp() * 1000),
                    row["Campaign Name"],
                ]})
            series.append({
                "type": "custom",
                "name": brand,
                "renderItem": render_item,
                "itemStyle": {"color": BRAND_COLORS.get(brand, COLORS[i % len(COLORS)])},
                "encode": {"x": [1, 2], "y": 0},
                "data": data,
            })

        st_echarts(options={
            "tooltip": {"formatter": tooltip_fmt},
            "legend": {"data": brands_list, "top": 4, "type": "scroll", "textStyle": {"fontSize": 12}},
            "grid": {"left": "2%", "right": "2%", "top": "12%", "bottom": "4%", "containLabel": True},
            "xAxis": {
                "type": "time",
                "axisLabel": {"fontSize": 11},
                "minInterval": 28 * 24 * 3600 * 1000,
                "maxInterval": 31 * 24 * 3600 * 1000,
                "splitLine": {
                    "show": True,
                    "lineStyle": {"type": "dashed", "color": "#cbd5e1", "width": 1},
                },
            },
            "yAxis": {
                "type": "category",
                "data": campaigns_order[::-1],
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

st.divider()

# -------------------------
# ROW 7: AI Summary
# -------------------------
st.subheader("• AI Summary")
with st.container(border=True):
    st.markdown(cached_ai_summary(filtered_df))
