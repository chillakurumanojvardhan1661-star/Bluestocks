import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "/Users/manojvardhan/Bluestocks/data/db/bluestock_mf.db"
PROCESSED_DIR = "/Users/manojvardhan/Bluestocks/data/processed"

def get_connection():
    return sqlite3.connect(DB_PATH)

def run_advanced_analytics():
    conn = get_connection()
    
    # 1. Historical VaR (95%) and CVaR
    print("Calculating Value at Risk (VaR) & CVaR...")
    df_nav = pd.read_sql_query("SELECT amfi_code, daily_return_pct FROM fact_nav", conn)
    
    var_results = []
    for amfi_code, group in df_nav.groupby('amfi_code'):
        returns = group['daily_return_pct'].dropna().values
        if len(returns) < 30:
            continue
        # Historical VaR 95% is the 5th percentile
        var_95 = np.percentile(returns, 5)
        # CVaR 95% is the mean of returns below the VaR 95% threshold
        cvar_95 = np.mean(returns[returns <= var_95])
        
        var_results.append({
            'amfi_code': str(amfi_code),
            'var_95_pct': var_95,
            'cvar_95_pct': cvar_95
        })
        
    df_var = pd.DataFrame(var_results)
    df_var.to_csv(os.path.join(PROCESSED_DIR, "var_cvar_report.csv"), index=False)
    
    # 2. Sector Concentration Index (HHI)
    print("Calculating Sector HHI...")
    df_port = pd.read_sql_query("SELECT amfi_code, sector, weight_pct FROM fact_portfolio", conn)
    hhi_results = []
    for amfi_code, group in df_port.groupby('amfi_code'):
        # Calculate sum of squared sector weights
        sector_weights = group.groupby('sector')['weight_pct'].sum()
        # Normalize weights so they sum to 100 or 1
        total_w = sector_weights.sum()
        if total_w > 0:
            norm_weights = sector_weights / total_w
            hhi = np.sum((norm_weights * 100) ** 2)
        else:
            hhi = 0.0
            
        hhi_results.append({
            'amfi_code': str(amfi_code),
            'sector_hhi': hhi
        })
    df_hhi = pd.DataFrame(hhi_results)
    df_hhi.to_csv(os.path.join(PROCESSED_DIR, "sector_hhi.csv"), index=False)
    
    # 3. Investor Cohort Analysis
    print("Performing Cohort Analysis...")
    df_tx = pd.read_sql_query("SELECT investor_id, transaction_date, amount_inr, transaction_type FROM fact_transactions", conn)
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    
    # Cohort is defined by first transaction year-month
    first_tx = df_tx.groupby('investor_id')['transaction_date'].min().reset_index()
    first_tx['cohort'] = first_tx['transaction_date'].dt.to_period('M').astype(str)
    
    df_tx = pd.merge(df_tx, first_tx[['investor_id', 'cohort']], on='investor_id', how='left')
    
    cohort_summary = df_tx.groupby('cohort').agg(
        total_invested=('amount_inr', 'sum'),
        average_tx=('amount_inr', 'mean'),
        active_investors=('investor_id', 'nunique'),
        tx_count=('amount_inr', 'count')
    ).reset_index()
    
    cohort_summary.to_csv(os.path.join(PROCESSED_DIR, "cohort_analysis.csv"), index=False)
    
    # 4. SIP Continuation / At-Risk Analysis
    print("Performing SIP Continuation Analysis...")
    df_sip_tx = df_tx[df_tx['transaction_type'] == 'SIP'].copy()
    df_sip_tx = df_sip_tx.sort_values(by=['investor_id', 'transaction_date'])
    
    sip_continuity = []
    for investor_id, group in df_sip_tx.groupby('investor_id'):
        if len(group) < 6:
            continue # Only investors with 6+ SIPs
            
        # Compute days gap between consecutive transactions
        dates = group['transaction_date'].values
        gaps = np.diff(dates) / np.timedelta64(1, 'D')
        
        max_gap = np.max(gaps) if len(gaps) > 0 else 0
        avg_gap = np.mean(gaps) if len(gaps) > 0 else 0
        
        # Gaps > 35 days flagged as 'at-risk'
        status = 'At-Risk' if max_gap > 35 else 'Active'
        
        sip_continuity.append({
            'investor_id': investor_id,
            'sip_count': len(group),
            'avg_gap_days': avg_gap,
            'max_gap_days': max_gap,
            'status': status
        })
        
    df_sip_cont = pd.DataFrame(sip_continuity)
    df_sip_cont.to_csv(os.path.join(PROCESSED_DIR, "sip_continuity.csv"), index=False)
    
    conn.close()
    print("Advanced analytics completed successfully.")

if __name__ == "__main__":
    run_advanced_analytics()
