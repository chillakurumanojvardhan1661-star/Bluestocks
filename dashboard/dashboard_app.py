import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# Page setup
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title {
        font-family: 'Outfit', sans-serif;
        color: #1e3a8a;
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #1e293b;
    }
    .metric-label {
        font-size: 14px;
        color: #64748b;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "/Users/manojvardhan/Bluestocks/data/db/bluestock_mf.db"
PROCESSED_DIR = "/Users/manojvardhan/Bluestocks/data/processed"

def get_connection():
    return sqlite3.connect(DB_PATH)

# Sidebar navigation
st.sidebar.image("https://bluestock.in/images/logo.png", width=150)
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Industry Overview", "Fund Performance & Scorecard", "Investor Analytics", "SIP & Market Trends"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Capstone Project**")
st.sidebar.markdown("Prepared for: *Bluestock Fintech*")

# ----------------- PAGE 1: Industry Overview -----------------
if page == "Industry Overview":
    st.markdown('<div class="main-title">Industry Overview & AUM Growth</div>', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">Rs. 81L Cr</div>
                <div class="metric-label">Total Industry AUM (Dec 2025)</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">Rs. 31,002 Cr</div>
                <div class="metric-label">Monthly SIP Inflow (Dec 2025 Peak)</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">26.12 Cr</div>
                <div class="metric-label">Total Investor Folios</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">40 Schemes</div>
                <div class="metric-label">Monitored schemes</div>
            </div>
        """, unsafe_allow_html=True)

    conn = get_connection()
    df_aum = pd.read_sql_query("SELECT date, fund_house, aum_crore FROM fact_aum", conn)
    df_sip = pd.read_sql_query("SELECT month, sip_inflow_crore, active_sip_accounts_crore FROM fact_sip_industry", conn)
    conn.close()

    # Visualizations
    st.markdown("### 📈 AUM Growth & SIP Trends")
    c1, c2 = st.columns(2)
    
    with c1:
        # AUM Growth Bar Chart
        df_aum['year'] = pd.to_datetime(df_aum['date']).dt.year
        aum_year = df_aum.groupby(['year', 'fund_house'])['aum_crore'].mean().reset_index()
        fig_aum = px.bar(
            aum_year, x='year', y='aum_crore', color='fund_house',
            title="AUM Growth by Fund House (2022 - 2025)",
            labels={'aum_crore': 'AUM (Rs. Crore)', 'year': 'Year'},
            barmode='group'
        )
        st.plotly_chart(fig_aum, use_container_width=True)
        
    with c2:
        # SIP Inflow Line
        fig_sip = px.line(
            df_sip, x='month', y='sip_inflow_crore',
            title="Monthly SIP Inflow Trend (Rs. Crore)",
            labels={'sip_inflow_crore': 'SIP Inflow (Cr)', 'month': 'Month'},
            markers=True
        )
        st.plotly_chart(fig_sip, use_container_width=True)

# ----------------- PAGE 2: Fund Performance -----------------
elif page == "Fund Performance & Scorecard":
    st.markdown('<div class="main-title">Mutual Fund Performance & Scorecard</div>', unsafe_allow_html=True)
    
    # Load scorecard
    scorecard_path = os.path.join(PROCESSED_DIR, "fund_scorecard.csv")
    if os.path.exists(scorecard_path):
        df_score = pd.read_csv(scorecard_path)
    else:
        st.error("Scorecard file not found! Please run the metrics calculation first.")
        st.stop()
        
    # Filters
    categories = ['All'] + sorted(df_score['category'].unique().tolist())
    selected_cat = st.selectbox("Filter by Category:", categories)
    
    df_filtered = df_score.copy()
    if selected_cat != 'All':
        df_filtered = df_filtered[df_filtered['category'] == selected_cat]
        
    st.markdown("### 🏆 Composite Scorecard Ranking (Top 10)")
    st.dataframe(df_filtered.head(10)[['amfi_code', 'category', 'composite_score', 'return_3yr_pct', 'sharpe_ratio', 'alpha', 'beta', 'max_drawdown_pct', 'expense_ratio_pct']])
    
    # Scatter plot Return vs Risk
    st.markdown("### 📊 Return vs Risk Analysis")
    fig_scatter = px.scatter(
        df_filtered, x='std_dev_ann_pct', y='return_3yr_pct',
        color='category', size='composite_score', hover_name='amfi_code',
        title="3-Year Annualized Return vs Volatility (Size = Composite Score)",
        labels={'std_dev_ann_pct': 'Annualized Volatility (%)', 'return_3yr_pct': '3-Year Return (%)'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------- PAGE 3: Investor Analytics -----------------
elif page == "Investor Analytics":
    st.markdown('<div class="main-title">Investor Behavior & Cohort Insights</div>', unsafe_allow_html=True)
    
    conn = get_connection()
    df_tx = pd.read_sql_query("SELECT state, city_tier, age_group, amount_inr, transaction_type, payment_mode, kyc_status FROM fact_transactions", conn)
    conn.close()
    
    c1, c2 = st.columns(2)
    with c1:
        # State-wise distribution
        state_tx = df_tx.groupby('state')['amount_inr'].sum().reset_index().sort_values('amount_inr', ascending=False)
        fig_state = px.bar(
            state_tx.head(10), x='amount_inr', y='state', orientation='h',
            title="Top 10 States by Total Investment Volume (INR)",
            labels={'amount_inr': 'Total Invested (Rs)', 'state': 'State'}
        )
        st.plotly_chart(fig_state, use_container_width=True)
        
    with c2:
        # Age group split
        age_tx = df_tx['age_group'].value_counts().reset_index()
        fig_age = px.pie(
            age_tx, values='count', names='age_group',
            title="Investor Age Group Distribution"
        )
        st.plotly_chart(fig_age, use_container_width=True)

    # Demographic breakdown
    st.markdown("### 🏦 Payment Mode & KYC Verification Splits")
    c3, c4 = st.columns(2)
    with c3:
        fig_pay = px.histogram(df_tx, x='payment_mode', color='transaction_type', barmode='group', title="Payment Mode by Transaction Type")
        st.plotly_chart(fig_pay, use_container_width=True)
    with c4:
        fig_kyc = px.pie(df_tx['kyc_status'].value_counts().reset_index(), values='count', names='kyc_status', title="KYC Status Summary")
        st.plotly_chart(fig_kyc, use_container_width=True)

# ----------------- PAGE 4: SIP & Market Trends -----------------
elif page == "SIP & Market Trends":
    st.markdown('<div class="main-title">SIP & Market Index Trends</div>', unsafe_allow_html=True)
    
    # Category heatmap
    st.markdown("### 📂 Category Net Inflows (FY 2024-25)")
    df_cat = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_category_inflows.csv"))
    pivot_cat = df_cat.pivot(index='category', columns='month', values='net_inflow_crore')
    
    fig_heat = px.imshow(
        pivot_cat, color_continuous_scale='YlGnBu',
        title="Net Monthly Inflow by Category (Rs. Crore)",
        labels=dict(x="Month", y="Category", color="Inflow (Cr)")
    )
    st.plotly_chart(fig_heat, use_container_width=True)
