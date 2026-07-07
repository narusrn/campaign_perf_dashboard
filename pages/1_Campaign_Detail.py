import pandas as pd
import streamlit as st

from common import BRAND_COLORS, kpi_card, load_campaigns

st.set_page_config(layout="wide", page_title="Campaign Detail")


def _val(v, placeholder="_No data available_"):
    if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() in ("", "-", "nan"):
        return placeholder
    return v


selected = st.session_state.get("selected_campaign")

if not selected:
    st.subheader("• Campaign Detail")
    st.info("ยังไม่ได้เลือกแคมเปญ กรุณาคลิกที่แคมเปญในกราฟ Traffic & Brand Overview ที่หน้า Dashboard ก่อน")
    st.page_link("main.py", label="⟵ กลับไปที่ Dashboard")
    st.stop()

df = load_campaigns()
rows = df[df["Campaign Name"] == selected]

if rows.empty:
    st.warning(f"ไม่พบข้อมูลแคมเปญ '{selected}'")
    st.page_link("main.py", label="⟵ กลับไปที่ Dashboard")
    st.stop()

row = rows.iloc[0]
brand_color = BRAND_COLORS.get(row["Brand"], "#5470c6")

st.page_link("main.py", label="⟵ กลับไปที่ Dashboard")

# -------------------------
# Section: Brand Category, Brand, Campaign Name, Period
# -------------------------
st.markdown(
    f'<div style="display:flex;align-items:center;gap:14px;padding:12px 0;">'
    f'<div style="width:10px;height:48px;border-radius:6px;background:{brand_color};"></div>'
    f'<div>'
    f'<div style="font-size:1.6rem;font-weight:800;color:#1e293b;">{row["Campaign Name"]}</div>'
    f'<div style="font-size:0.85rem;color:#64748b;">{_val(row["Brand Category"])} · {_val(row["Brand"])} · {_val(row["Campaign Type"])}</div>'
    f'</div></div>',
    unsafe_allow_html=True,
)
st.caption(
    f"Period: {_val(row['Start Date'])} – {_val(row['End Date'])}  |  "
    f"Duration: {_val(row.get('Campaign Duration (days)'))} days"
)

st.divider()

# -------------------------
# Section: Campaign description, Reward
# -------------------------
st.subheader("• Campaign Overview")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("**Description**")
        st.write(_val(row.get("Campaign Description"), "_No description available_"))
with c2:
    with st.container(border=True):
        st.markdown("**Reward**")
        st.write(_val(row.get("Big Prize"), "_No reward info available_"))

st.divider()

# -------------------------
# Section: Total visitor, visitor trend line
# -------------------------
st.subheader("• Visitor")
v1, v2 = st.columns([1, 3])
with v1:
    st.markdown(kpi_card("Total Visitor", f'{int(row["Visit"]):,}', "#5470c6", "#73c0de"), unsafe_allow_html=True)
with v2:
    with st.container(border=True):
        st.caption("Visitor trend line — no daily/time-series data available yet")

st.divider()

# -------------------------
# Section: Total conversion, conversion trend line
# -------------------------
st.subheader("• Conversion")
cv1, cv2 = st.columns([1, 3])
with cv1:
    st.markdown(kpi_card("Total Conversion", f'{int(row["Conversion"]):,}', "#e07b39", "#fac858"), unsafe_allow_html=True)
with cv2:
    with st.container(border=True):
        st.caption("Conversion trend line — no daily/time-series data available yet")

st.divider()

# -------------------------
# Section: Leaderboard, time of the day
# -------------------------
st.subheader("• Leaderboard")
l1, l2 = st.columns(2)
with l1:
    with st.container(border=True):
        ranking = df.sort_values("Conversion Rate", ascending=False).reset_index(drop=True)
        rank = ranking.index[ranking["Campaign Name"] == selected].tolist()
        if rank:
            st.metric("Rank by Conversion Rate", f"#{rank[0] + 1} of {len(ranking)}")
        st.dataframe(
            ranking.head(10)[["Campaign Name", "Conversion Rate"]],
            use_container_width=True, hide_index=True,
        )
with l2:
    with st.container(border=True):
        st.caption("Time of the day — no hourly data available yet")
