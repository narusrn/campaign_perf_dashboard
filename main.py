import streamlit as st
import pandas as pd
import plotly.express as px
 
st.set_page_config(page_title="Advanced Dashboard", layout="wide")
 
st.title("🚀 Advanced Campaign Dashboard")
 
# ------------------ LOAD DATA ------------------
df = pd.read_csv("data/Campaign_Performance_GA4_2026_CSV.csv")
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
# Clean date
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values("Date")
 
# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Filter")
 
# Date filter
if "Date" in df.columns:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
 
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )
 
    if len(date_range) == 2:
        df = df[(df["Date"] >= pd.to_datetime(date_range[0])) &
                (df["Date"] <= pd.to_datetime(date_range[1]))]
 
# Campaign filter
if "Campaign Name" in df.columns:
    campaign = st.sidebar.multiselect(
        "Campaign",
        df["Campaign Name"].dropna().unique(),
        default=df["Campaign Name"].dropna().unique()
    )
    df = df[df["Campaign Name"].isin(campaign)]
 
# ------------------ KPI ------------------
total_visit = df["Visit"].astype(float).sum()
total_conversion = df["Conversion(Users)"].sum()
cr = total_conversion / total_visit if total_visit > 0 else 0
 
col1, col2, col3 = st.columns(3)
 
col1.metric("👥 Visits", f"{total_visit:,.0f}")
col2.metric("💰 Conversions", f"{total_conversion:,.0f}")
col3.metric("📈 Conversion Rate", f"{cr:.2%}")
 
st.markdown("---")
 
# ------------------ TREND ------------------
col1, col2 = st.columns(2)
 
with col1:
    if "Date" in df.columns:
        fig = px.line(df, x="Date", y="Visit", title="📈 Visit Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
 
with col2:
    if "Date" in df.columns:
        fig = px.line(df, x="Date", y="Conversion(Users)", title="💰 Conversion Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
 
# ------------------ CAMPAIGN PERFORMANCE ------------------
st.markdown("### 🏆 Campaign Performance")
 
campaign_perf = df.groupby("Campaign Name").agg({
    "Visit": "sum",
    "Conversion(Users)": "sum"
}).reset_index()
 
campaign_perf["CR"] = campaign_perf["Conversion(Users)"] / campaign_perf["Visit"]
 
fig2 = px.bar(
    campaign_perf.sort_values(by="Conversion(Users)", ascending=False),
    x="Campaign Name",
    y="Conversion(Users)",
    title="Conversion by Campaign",
    text_auto=True
)
st.plotly_chart(fig2, use_container_width=True)
 
# ------------------ FUNNEL ------------------
st.markdown("### 🔻 Funnel")
 
funnel_df = pd.DataFrame({
    "Stage": ["Visit", "Conversion(Users)"],
    "Value": [total_visit, total_conversion]
})
 
fig3 = px.funnel(funnel_df, x="Value", y="Stage")
st.plotly_chart(fig3, use_container_width=True)
 
# ------------------ INSIGHT ------------------
st.markdown("### 🤖 Insight")
 
top_campaign = campaign_perf.sort_values(by="Conversion(Users)", ascending=False).iloc[0]
 
st.info(f"""
🔥 Campaign ที่ดีที่สุดคือ: **{top_campaign['Campaign Name']}**
 
- Conversion สูงสุด: {top_campaign['Conversion(Users)']:,}
- Conversion Rate: {top_campaign['CR']:.2%}
 
📊 Insight:
- Campaign นี้ outperform ตัวอื่นอย่างชัดเจน
- ควรเพิ่ม budget หรือ scale campaign นี้
""")
 
# ------------------ TABLE ------------------
st.markdown("### 📊 Detail Table")
st.dataframe(campaign_perf.sort_values(by="Conversion(Users)", ascending=False))