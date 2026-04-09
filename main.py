import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
 
st.set_page_config(layout="wide")
 
# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/Campaign_Performance_GA4_2026_CSV.csv")
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
df = df.rename(columns={"Conversion(Users)": "Conversion", "Brand category": "Brand Category"})
# -------------------------
# FILTER BAR
# -------------------------
st.title("📊 Campaign Performance Dashboard")
 
st.subheader("🔎 Filters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    brand_cat_filter = st.multiselect(
        "Brand Category",
        options=df['Brand Category'].dropna().unique(),
        default=df['Brand Category'].dropna().unique()
    )
 
with col2:
    brand_filter = st.multiselect(
        "Brand",
        options=df['Brand'].dropna().unique(),
        default=df['Brand'].dropna().unique()
    )
 
with col3:
    campaign_type_filter = st.multiselect(
        "Campaign Type",
        options=df['Campaign Type'].dropna().unique(),
        default=df['Campaign Type'].dropna().unique()
    )
 
# APPLY FILTER
filtered_df = df[
    (df['Brand Category'].isin(brand_cat_filter)) &
    (df['Brand'].isin(brand_filter)) &
    (df['Campaign Type'].isin(campaign_type_filter))
]
 
# -------------------------
# KPI
# -------------------------
st.subheader("📌 Overview KPI")
 
col1, col2, col3 = st.columns(3)
col1.metric("Total Campaign", len(filtered_df))
col2.metric("Total Visit", int(filtered_df['Visit'].sum()))
col3.metric("Total Conversion", int(filtered_df['Conversion'].sum()))
 
# -------------------------
# 1. Donut - Brand Category
# -------------------------
st.subheader("🍩 Brand Category Distribution")
 
brand_cat = filtered_df['Brand Category'].value_counts().reset_index()
brand_cat.columns = ['Brand Category', 'Count']
 
fig1 = px.pie(brand_cat, names='Brand Category', values='Count', hole=0.5)
st.plotly_chart(fig1, use_container_width=True)
 
# -------------------------
# 2. Donut - Brand
# -------------------------
st.subheader("🍩 Brand Distribution")
 
brand = filtered_df['Brand'].value_counts().reset_index()
brand.columns = ['Brand', 'Count']
 
fig2 = px.pie(brand, names='Brand', values='Count', hole=0.5)
st.plotly_chart(fig2, use_container_width=True)
 
# -------------------------
# 3. Horizontal Bar
# -------------------------
st.subheader("📊 Campaign Type Distribution")
 
campaign_type = filtered_df['Campaign Type'].value_counts().reset_index()
campaign_type.columns = ['Campaign Type', 'Count']
 
fig3 = px.bar(
    campaign_type,
    x='Count',
    y='Campaign Type',
    orientation='h'
)
 
st.plotly_chart(fig3, use_container_width=True)
 
# -------------------------
# 4. Combo Chart
# -------------------------
st.subheader("📈 Traffic vs Conversion per Campaign")
 
df_sorted = filtered_df.sort_values(by='Visit', ascending=False)
 
fig4 = go.Figure()
 
fig4.add_trace(go.Bar(
    x=df_sorted['Campaign Name'],
    y=df_sorted['Conversion'],
    name='Conversion'
))
 
fig4.add_trace(go.Scatter(
    x=df_sorted['Campaign Name'],
    y=df_sorted['Visit'],
    mode='lines+markers',
    name='Visit'
))
 
fig4.update_layout(
    xaxis_title="Campaign",
    yaxis_title="Value",
    barmode='group'
)
 
st.plotly_chart(fig4, use_container_width=True)
 
# -------------------------
# 5. Ranking Table
# -------------------------
st.subheader("🏆 Campaign Ranking")
 
ranking = filtered_df.sort_values(by='Conversion Rate', ascending=False)[
    ['Campaign Name', 'Conversion Rate', 'Key Event']
]
 
st.dataframe(ranking, use_container_width=True)
 
# -------------------------
# 6. Line - Key Features
# -------------------------
st.subheader("📈 Campaign Key Features vs Visit")
 
feature_group = filtered_df.groupby('Campaign Key Features')['Visit'].sum().reset_index()
 
fig6 = px.line(
    feature_group,
    x='Campaign Key Features',
    y='Visit',
    markers=True
)
 
st.plotly_chart(fig6, use_container_width=True)
 
# -------------------------
# 7. Line - Prize
# -------------------------
st.subheader("📈 Big Prize vs Conversion")
 
prize_group = filtered_df.groupby('Prize')['Conversion'].sum().reset_index()
 
fig7 = px.line(
    prize_group,
    x='Prize',
    y='Conversion',
    markers=True
)
 
st.plotly_chart(fig7, use_container_width=True)
 
# -------------------------
# 8. Overview Table
# -------------------------
st.subheader("📋 Overview Table")
st.dataframe(filtered_df, use_container_width=True)
 
# -------------------------
# 9. Timeline
# -------------------------
st.subheader("🗓️ Campaign Timeline")
 
filtered_df['Start Date'] = pd.to_datetime(filtered_df['Start Date'])
filtered_df['End Date'] = pd.to_datetime(filtered_df['End Date'])
 
fig9 = px.timeline(
    filtered_df,
    x_start="Start Date",
    x_end="End Date",
    y="Campaign Name",
    color="Brand"
)
 
fig9.update_yaxes(autorange="reversed")
 
st.plotly_chart(fig9, use_container_width=True)
