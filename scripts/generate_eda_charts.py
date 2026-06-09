import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setup plotting style
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

DB_PATH = "/Users/manojvardhan/Bluestocks/data/db/bluestock_mf.db"
FIG_DIR = "/Users/manojvardhan/Bluestocks/reports/figures"
os.makedirs(FIG_DIR, exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH)

def generate_charts():
    conn = get_connection()
    
    # Sleek palette
    palette = sns.color_palette("muted")
    
    # 1. NAV Trends (selected funds)
    print("Generating Chart 1: NAV Trends...")
    df_nav = pd.read_sql_query("""
        SELECT nav_date, nav, f.scheme_name
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        WHERE f.amfi_code IN ('119551', '120503', '118632', '119092', '120841')
    """, conn)
    df_nav['nav_date'] = pd.to_datetime(df_nav['nav_date'])
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_nav, x='nav_date', y='nav', hue='scheme_name', palette="viridis")
    plt.title("Daily NAV Trends (2022 - 2026) for Target Bluechip Funds")
    plt.xlabel("Date")
    plt.ylabel("NAV (Rs.)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "01_nav_trends.png"))
    plt.close()

    # 2. AUM Growth by AMC
    print("Generating Chart 2: AUM Growth...")
    df_aum = pd.read_sql_query("SELECT date, fund_house, aum_crore FROM fact_aum", conn)
    df_aum['year'] = pd.to_datetime(df_aum['date']).dt.year
    df_aum_annual = df_aum.groupby(['year', 'fund_house'])['aum_crore'].mean().reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_aum_annual, x='year', y='aum_crore', hue='fund_house', palette="tab10")
    plt.title("Quarterly AUM Trends by Fund House (2022 - 2025)")
    plt.xlabel("Year")
    plt.ylabel("AUM (Rs. Crore)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "02_aum_growth.png"))
    plt.close()

    # 3. SIP Inflow Trend
    print("Generating Chart 3: SIP Inflow Trend...")
    df_sip = pd.read_sql_query("SELECT month, sip_inflow_crore FROM fact_sip_industry", conn)
    df_sip['month_dt'] = pd.to_datetime(df_sip['month'] + "-01")
    plt.figure(figsize=(10, 5))
    plt.plot(df_sip['month_dt'], df_sip['sip_inflow_crore'], marker='o', color='#3b82f6', linewidth=2)
    plt.axhline(31002, color='red', linestyle='--', alpha=0.7, label='Dec 2025 Peak (31,002 Cr)')
    plt.title("Monthly SIP Inflows (Rs. Crore)")
    plt.xlabel("Month")
    plt.ylabel("Inflow (Rs. Crore)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "03_sip_inflow_trend.png"))
    plt.close()

    # 4. Category Inflows Heatmap
    print("Generating Chart 4: Category Heatmap...")
    df_cat = pd.read_csv("/Users/manojvardhan/Bluestocks/data/processed/clean_category_inflows.csv")
    pivot_cat = df_cat.pivot(index='category', columns='month', values='net_inflow_crore')
    plt.figure(figsize=(14, 6))
    sns.heatmap(pivot_cat, cmap="YlGnBu", annot=False, cbar_kws={'label': 'Net Inflow (Rs. Crore)'})
    plt.title("Net Inflow by Category across Months")
    plt.xlabel("Month")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "04_category_inflows_heatmap.png"))
    plt.close()

    # 5. Investor Age Distribution
    print("Generating Chart 5: Investor Age...")
    df_tx = pd.read_sql_query("SELECT age_group, amount_inr, state, city_tier, gender, annual_income_lakh, transaction_type, payment_mode, kyc_status FROM fact_transactions", conn)
    plt.figure(figsize=(6, 6))
    df_tx['age_group'].value_counts().plot.pie(autopct='%1.1f%%', colors=sns.color_palette("pastel"), startangle=90)
    plt.title("Investor Age Group Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "05_investor_age_dist.png"))
    plt.close()

    # 6. SIP Amount by Age
    print("Generating Chart 6: SIP by Age Boxplot...")
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df_tx[df_tx['transaction_type'] == 'SIP'], x='age_group', y='amount_inr', palette="Set2")
    plt.title("SIP Transaction Amounts across Age Groups")
    plt.xlabel("Age Group")
    plt.ylabel("SIP Amount (Rs.)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "06_sip_amount_by_age.png"))
    plt.close()

    # 7. SIP by State
    print("Generating Chart 7: SIP by State...")
    state_sum = df_tx.groupby('state')['amount_inr'].sum().sort_values(ascending=False).reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=state_sum, x='amount_inr', y='state', palette="coolwarm")
    plt.title("Total Transaction Volume by State")
    plt.xlabel("Total Investment (Rs.)")
    plt.ylabel("State")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "07_sip_by_state.png"))
    plt.close()

    # 8. City Tier Split
    print("Generating Chart 8: City Tier Split...")
    plt.figure(figsize=(6, 6))
    df_tx['city_tier'].value_counts().plot.pie(autopct='%1.1f%%', colors=['#60a5fa', '#f87171'], wedgeprops=dict(width=0.4))
    plt.title("Transaction Splits: T30 vs B30 Cities")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "08_city_tier_split.png"))
    plt.close()

    # 9. Folio Count Growth
    print("Generating Chart 9: Folio Growth...")
    df_folio_c = pd.read_csv("/Users/manojvardhan/Bluestocks/data/processed/clean_industry_folio_count.csv")
    df_folio_c['month_dt'] = pd.to_datetime(df_folio_c['month'] + "-01")
    plt.figure(figsize=(10, 5))
    plt.plot(df_folio_c['month_dt'], df_folio_c['total_folios_crore'], label='Total Folios', marker='o')
    plt.plot(df_folio_c['month_dt'], df_folio_c['equity_folios_crore'], label='Equity Folios', marker='x')
    plt.plot(df_folio_c['month_dt'], df_folio_c['debt_folios_crore'], label='Debt Folios', marker='s')
    plt.plot(df_folio_c['month_dt'], df_folio_c['hybrid_folios_crore'], label='Hybrid Folios', marker='d')
    plt.title("Industry Folio Count Growth (Crore)")
    plt.xlabel("Date")
    plt.ylabel("Folios (Crores)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "09_folio_count_growth.png"))
    plt.close()

    # 10. NAV Returns Correlation Matrix
    print("Generating Chart 10: Returns Correlation...")
    df_nav_piv = pd.read_sql_query("""
        SELECT nav_date, amfi_code, daily_return_pct
        FROM fact_nav
        WHERE amfi_code IN ('119551', '120503', '118632', '119092', '120841', '125497')
    """, conn)
    pivot_nav = df_nav_piv.pivot(index='nav_date', columns='amfi_code', values='daily_return_pct')
    corr = pivot_nav.corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix of Target Funds Daily Returns")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "10_nav_returns_correlation.png"))
    plt.close()

    # 11. Sector Allocation
    print("Generating Chart 11: Sector Allocation...")
    df_port = pd.read_sql_query("SELECT sector, weight_pct FROM fact_portfolio", conn)
    sector_sum = df_port.groupby('sector')['weight_pct'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(8, 8))
    sector_sum.plot.pie(autopct='%1.1f%%', colors=sns.color_palette("Set3"), startangle=140)
    plt.title("Top 10 Sectors Allocation Weight")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "11_sector_allocation.png"))
    plt.close()

    # 12. Transaction Type Split
    print("Generating Chart 12: Transaction Split...")
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df_tx, x='transaction_type', palette="Set1")
    plt.title("Transaction Count by Type")
    plt.xlabel("Transaction Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "12_transaction_type_split.png"))
    plt.close()

    # 13. Income vs SIP
    print("Generating Chart 13: Income vs SIP...")
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df_tx.sample(500), x='annual_income_lakh', y='amount_inr', hue='transaction_type', alpha=0.7)
    plt.title("Income vs Transaction Amount (Sample of 500)")
    plt.xlabel("Annual Income (Rs. Lakh)")
    plt.ylabel("Transaction Amount (Rs.)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "13_income_vs_sip.png"))
    plt.close()

    # 14. Payment Mode Split
    print("Generating Chart 14: Payment Modes...")
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df_tx, x='payment_mode', palette="Accent")
    plt.title("Transaction Distribution by Payment Mode")
    plt.xlabel("Payment Mode")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "14_payment_mode_split.png"))
    plt.close()

    # 15. KYC Status Split
    print("Generating Chart 15: KYC Status...")
    plt.figure(figsize=(6, 6))
    df_tx['kyc_status'].value_counts().plot.pie(autopct='%1.1f%%', colors=['#4ade80', '#fca5a5'])
    plt.title("KYC Verification Status")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "15_kyc_status_split.png"))
    plt.close()

    # 16. Schemes per Risk Category
    print("Generating Chart 16: Schemes per Risk Grade...")
    df_fund = pd.read_sql_query("SELECT risk_category FROM dim_fund", conn)
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df_fund, x='risk_category', palette="magma", order=df_fund['risk_category'].value_counts().index)
    plt.title("Number of Schemes per SEBI Risk Designation")
    plt.xlabel("Risk Category")
    plt.ylabel("Number of Funds")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "16_risk_category_count.png"))
    plt.close()

    conn.close()
    print("All 16 charts generated and saved in reports/figures/.")

if __name__ == "__main__":
    generate_charts()
