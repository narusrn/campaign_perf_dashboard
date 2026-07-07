import base64

import pandas as pd
import streamlit as st

SHEET_ID = "1OisRn14n89ZKwTd2LDyZbwR9iZOMkT9JUzEORVhHkrE"

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


def type_colors(df):
    return {
        t: COLORS[i % len(COLORS)]
        for i, t in enumerate(sorted(df["Campaign Type"].dropna().unique()))
    }


@st.cache_data(ttl=3600)
def load_campaigns():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

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
    return df
