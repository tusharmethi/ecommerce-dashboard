import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from scripts.clean_data import clean_data
from scripts.sql_analysis import load_to_sqlite
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .kpi-label { font-size: 13px; opacity: 0.8; margin-bottom: 4px; letter-spacing: 1px; text-transform: uppercase; }
    .kpi-value { font-size: 28px; font-weight: 700; }
    .kpi-delta { font-size: 13px; margin-top: 4px; opacity: 0.85; }
    .section-title { font-size: 18px; font-weight: 600; margin: 1rem 0 0.5rem 0; color: #1e3a5f; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists("data/orders_clean.csv"):
        clean_data()
    if not os.path.exists("data/orders.db"):
        load_to_sqlite()
    df = pd.read_csv("data/orders_clean.csv", parse_dates=["order_date"])
    return df

@st.cache_data
def query(_conn, sql):
    return pd.read_sql_query(sql, _conn)

df_full = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=60)
st.sidebar.title("🔍 Filters")

years = sorted(df_full["year"].unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)

regions = sorted(df_full["region"].unique())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(df_full["category"].unique())
sel_categories = st.sidebar.multiselect("Category", categories, default=categories)

segments = sorted(df_full["segment"].unique())
sel_segments = st.sidebar.multiselect("Segment", segments, default=segments)

st.sidebar.markdown("---")
st.sidebar.markdown("**📦 Dataset**")
st.sidebar.markdown(f"- Rows: `{len(df_full):,}`")
st.sidebar.markdown(f"- Period: `2022 – 2023`")
st.sidebar.markdown(f"- Source: Kaggle Retail Orders")

# ── Apply Filters ─────────────────────────────────────────────────────────────
df = df_full[
    df_full["year"].isin(sel_years) &
    df_full["region"].isin(sel_regions) &
    df_full["category"].isin(sel_categories) &
    df_full["segment"].isin(sel_segments)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🛒 E-Commerce Sales Analytics Dashboard")
st.markdown("Interactive KPI tracker built with Python · Pandas · SQL · Streamlit · Plotly")
st.markdown("---")

if df.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_revenue  = df["revenue"].sum()
total_profit   = df["profit"].sum()
total_orders   = df["order_id"].nunique()
aov            = df["revenue"].sum() / df["quantity"].sum()
profit_margin  = (total_profit / total_revenue) * 100

col1, col2, col3, col4, col5 = st.columns(5)

def kpi_card(col, label, value, delta=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta">{delta}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(col1, "Total Revenue",  f"${total_revenue/1e6:.2f}M", f"{total_orders:,} orders")
kpi_card(col2, "Total Profit",   f"${total_profit/1e3:.0f}K",  f"Margin: {profit_margin:.1f}%")
kpi_card(col3, "Avg Order Value",f"${aov:.0f}",               "per unit")
kpi_card(col4, "Profit Margin",  f"{profit_margin:.1f}%",      "revenue → profit")
kpi_card(col5, "Total Orders",   f"{total_orders:,}",          f"{len(df):,} line items")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Monthly Trend + Regional Performance ───────────────────────────────
col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown('<div class="section-title">📈 Monthly Revenue & Profit Trend</div>', unsafe_allow_html=True)
    monthly = (df.groupby("year_month")
                 .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
                 .reset_index()
                 .sort_values("year_month"))

    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly["year_month"], y=monthly["revenue"],
        name="Revenue", marker_color="#2d6a9f", opacity=0.85
    ))
    fig_monthly.add_trace(go.Scatter(
        x=monthly["year_month"], y=monthly["profit"],
        name="Profit", mode="lines+markers",
        line=dict(color="#f0a500", width=2.5),
        marker=dict(size=5)
    ))
    fig_monthly.update_layout(
        height=320, margin=dict(t=10, b=40, l=10, r=10),
        legend=dict(orientation="h", y=1.1),
        xaxis_tickangle=-45, plot_bgcolor="white",
        yaxis=dict(gridcolor="#eee"), xaxis=dict(gridcolor="#eee")
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title">🗺️ Revenue by Region</div>', unsafe_allow_html=True)
    regional = (df.groupby("region")
                  .agg(revenue=("revenue","sum"), profit=("profit","sum"))
                  .reset_index()
                  .sort_values("revenue", ascending=True))

    fig_region = go.Figure(go.Bar(
        x=regional["revenue"], y=regional["region"],
        orientation="h", marker_color=["#4a90d9","#2d6a9f","#1e3a5f","#f0a500"],
        text=[f"${v/1e3:.0f}K" for v in regional["revenue"]],
        textposition="outside"
    ))
    fig_region.update_layout(
        height=320, margin=dict(t=10, b=20, l=10, r=60),
        plot_bgcolor="white", xaxis=dict(gridcolor="#eee", showticklabels=False)
    )
    st.plotly_chart(fig_region, use_container_width=True)

# ── Row 2: Category Breakdown + Top Products ──────────────────────────────────
col_l2, col_r2 = st.columns([2, 3])

with col_l2:
    st.markdown('<div class="section-title">🗂️ Revenue by Category</div>', unsafe_allow_html=True)
    cat_df = (df.groupby("category")
                .agg(revenue=("revenue","sum"))
                .reset_index())

    fig_pie = px.pie(
        cat_df, values="revenue", names="category",
        color_discrete_sequence=["#1e3a5f","#2d6a9f","#f0a500"],
        hole=0.45
    )
    fig_pie.update_traces(textinfo="label+percent", textfont_size=13)
    fig_pie.update_layout(
        height=320, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_r2:
    st.markdown('<div class="section-title">🏆 Top 10 Sub-Categories by Revenue</div>', unsafe_allow_html=True)
    subcat = (df.groupby("sub_category")
                .agg(revenue=("revenue","sum"), profit=("profit","sum"))
                .reset_index()
                .sort_values("revenue", ascending=False)
                .head(10)
                .sort_values("revenue", ascending=True))

    fig_subcat = go.Figure()
    fig_subcat.add_trace(go.Bar(
        x=subcat["revenue"], y=subcat["sub_category"],
        orientation="h", name="Revenue", marker_color="#2d6a9f",
        text=[f"${v/1e3:.0f}K" for v in subcat["revenue"]], textposition="outside"
    ))
    fig_subcat.add_trace(go.Bar(
        x=subcat["profit"], y=subcat["sub_category"],
        orientation="h", name="Profit", marker_color="#f0a500",
        text=[f"${v/1e3:.0f}K" for v in subcat["profit"]], textposition="outside"
    ))
    fig_subcat.update_layout(
        barmode="overlay", height=320,
        margin=dict(t=10, b=20, l=10, r=60),
        plot_bgcolor="white", legend=dict(orientation="h", y=1.1),
        xaxis=dict(gridcolor="#eee", showticklabels=False)
    )
    st.plotly_chart(fig_subcat, use_container_width=True)

# ── Row 3: Segment Analysis + YoY ────────────────────────────────────────────
col_l3, col_r3 = st.columns(2)

with col_l3:
    st.markdown('<div class="section-title">👥 Customer Segment Performance</div>', unsafe_allow_html=True)
    seg_df = (df.groupby("segment")
                .agg(revenue=("revenue","sum"), profit=("profit","sum"), orders=("order_id","nunique"))
                .reset_index())

    fig_seg = px.bar(
        seg_df, x="segment", y=["revenue","profit"],
        barmode="group",
        color_discrete_sequence=["#2d6a9f","#f0a500"],
        labels={"value":"Amount ($)", "variable":"Metric"}
    )
    fig_seg.update_layout(
        height=300, margin=dict(t=10, b=20, l=10, r=10),
        plot_bgcolor="white", yaxis=dict(gridcolor="#eee"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_seg, use_container_width=True)

with col_r3:
    st.markdown('<div class="section-title">📅 Year-over-Year Comparison</div>', unsafe_allow_html=True)
    yoy = (df.groupby("year")
             .agg(revenue=("revenue","sum"), profit=("profit","sum"), orders=("order_id","nunique"))
             .reset_index())
    yoy["year"] = yoy["year"].astype(str)

    fig_yoy = px.bar(
        yoy, x="year", y=["revenue","profit"],
        barmode="group",
        color_discrete_sequence=["#1e3a5f","#f0a500"],
        text_auto=".2s"
    )
    fig_yoy.update_layout(
        height=300, margin=dict(t=10, b=20, l=10, r=10),
        plot_bgcolor="white", yaxis=dict(gridcolor="#eee"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

# ── Raw Data Table ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">📋 Raw Data Explorer</div>', unsafe_allow_html=True)
cols_show = ["order_id","order_date","region","category","sub_category","segment","quantity","revenue","profit","discount_percent"]
st.dataframe(
    df[cols_show].sort_values("order_date", ascending=False).head(500),
    use_container_width=True, height=280
)

st.caption("Data Source: Kaggle Retail Orders Dataset · Built with Python, Pandas, SQL, Streamlit, Plotly")
