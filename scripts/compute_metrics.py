import os
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import linregress

DB_PATH = "/Users/manojvardhan/Bluestocks/data/db/bluestock_mf.db"
PROCESSED_DIR = "/Users/manojvardhan/Bluestocks/data/processed"
Rf = 0.065 # 6.5% Risk Free Rate

def load_data():
    conn = sqlite3.connect(DB_PATH)
    
    # Load daily nav
    df_nav = pd.read_sql_query("SELECT amfi_code, nav_date, nav, daily_return_pct FROM fact_nav", conn)
    df_nav['nav_date'] = pd.to_datetime(df_nav['nav_date'])
    
    # Load fund metadata
    df_fund = pd.read_sql_query("SELECT amfi_code, category, expense_ratio_pct FROM dim_fund", conn)
    
    # Load benchmark index prices
    df_bench = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_benchmark_indices.csv"))
    df_bench['date'] = pd.to_datetime(df_bench['date'])
    
    conn.close()
    return df_nav, df_fund, df_bench

def compute_metrics():
    df_nav, df_fund, df_bench = load_data()
    
    # Calculate Nifty 100 daily returns
    nifty100 = df_bench[df_bench['index_name'] == 'NIFTY100'].sort_values('date').copy()
    nifty100['bench_return'] = nifty100['close_value'].pct_change()
    nifty100 = nifty100.dropna(subset=['bench_return'])
    
    results = []
    
    for amfi_code, group in df_nav.groupby('amfi_code'):
        group = group.sort_values('nav_date')
        if len(group) < 10:
            continue
            
        navs = group['nav'].values
        dates = group['nav_date'].values
        returns = group['daily_return_pct'].values / 100.0
        
        # 1. CAGR calculations
        # n_years = total trading days / 252
        total_days = (pd.to_datetime(dates[-1]) - pd.to_datetime(dates[0])).days
        years = total_days / 365.25
        
        cagr_total = (navs[-1] / navs[0]) ** (1.0 / years) - 1 if years > 0 else 0.0
        
        # 1-Year return
        one_year_ago = dates[-1] - pd.Timedelta(days=365)
        nav_1y_start = group[group['nav_date'] >= one_year_ago]['nav'].values[0] if len(group[group['nav_date'] >= one_year_ago]) > 0 else navs[0]
        return_1yr = (navs[-1] / nav_1y_start) - 1
        
        # 3-Year CAGR
        three_years_ago = dates[-1] - pd.Timedelta(days=3 * 365)
        group_3y = group[group['nav_date'] >= three_years_ago]
        if len(group_3y) > 0:
            years_3y = (pd.to_datetime(dates[-1]) - pd.to_datetime(group_3y['nav_date'].values[0])).days / 365.25
            cagr_3yr = (navs[-1] / group_3y['nav'].values[0]) ** (1.0 / years_3y) - 1 if years_3y > 0 else cagr_total
        else:
            cagr_3yr = cagr_total
            
        # 5-Year CAGR (or max available)
        five_years_ago = dates[-1] - pd.Timedelta(days=5 * 365)
        group_5y = group[group['nav_date'] >= five_years_ago]
        if len(group_5y) > 0:
            years_5y = (pd.to_datetime(dates[-1]) - pd.to_datetime(group_5y['nav_date'].values[0])).days / 365.25
            cagr_5yr = (navs[-1] / group_5y['nav'].values[0]) ** (1.0 / years_5y) - 1 if years_5y > 0 else cagr_total
        else:
            cagr_5yr = cagr_total
            
        # 2. Risk Metrics: Sharpe & Sortino
        ann_return = cagr_3yr
        ann_vol = np.std(returns) * np.sqrt(252)
        
        sharpe = (ann_return - Rf) / ann_vol if ann_vol > 0 else 0.0
        
        # Downside Volatility
        downside_returns = returns[returns < 0]
        downside_vol = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else ann_vol
        sortino = (ann_return - Rf) / downside_vol if downside_vol > 0 else 0.0
        
        # 3. Alpha & Beta vs NIFTY100
        # Align dates
        fund_ret_df = pd.DataFrame({'date': dates, 'fund_return': returns})
        aligned = pd.merge(fund_ret_df, nifty100[['date', 'bench_return']], on='date', how='inner')
        
        if len(aligned) > 10:
            slope, intercept, r_val, p_val, std_err = linregress(aligned['bench_return'], aligned['fund_return'])
            beta = slope
            # Annualized Alpha (Jensen's Alpha)
            alpha = intercept * 252
        else:
            beta = 1.0
            alpha = 0.0
            
        # 4. Max Drawdown
        running_max = np.maximum.accumulate(navs)
        drawdowns = (navs - running_max) / running_max
        max_dd = np.min(drawdowns)
        
        results.append({
            'amfi_code': str(amfi_code),
            'return_1yr_pct': return_1yr * 100,
            'return_3yr_pct': cagr_3yr * 100,
            'return_5yr_pct': cagr_5yr * 100,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'alpha': alpha * 100,
            'beta': beta,
            'max_drawdown_pct': max_dd * 100,
            'std_dev_ann_pct': ann_vol * 100
        })
        
    df_res = pd.DataFrame(results)
    
    # Merge with fund master metadata
    df_m = pd.merge(df_res, df_fund, on='amfi_code', how='left')
    
    # Build Fund Scorecard (0-100 composite score)
    # Score = 30% * 3yr_return_rank + 25% * Sharpe_rank + 20% * Alpha_rank + 15% * (inverse expense_ratio_rank) + 10% * (inverse max_dd_rank)
    df_m['rank_3yr'] = df_m['return_3yr_pct'].rank(pct=True)
    df_m['rank_sharpe'] = df_m['sharpe_ratio'].rank(pct=True)
    df_m['rank_alpha'] = df_m['alpha'].rank(pct=True)
    df_m['rank_expense'] = df_m['expense_ratio_pct'].rank(pct=True, ascending=False) # Lower is better
    df_m['rank_max_dd'] = df_m['max_drawdown_pct'].rank(pct=True, ascending=False) # Less negative is better
    
    # Weighted Score
    df_m['composite_score'] = (
        0.30 * df_m['rank_3yr'] + 
        0.25 * df_m['rank_sharpe'] + 
        0.20 * df_m['rank_alpha'] + 
        0.15 * df_m['rank_expense'] + 
        0.10 * df_m['rank_max_dd']
    ) * 100
    
    # Drop intermediate ranks
    df_m = df_m.drop(columns=['rank_3yr', 'rank_sharpe', 'rank_alpha', 'rank_expense', 'rank_max_dd'])
    df_m = df_m.sort_values(by='composite_score', ascending=False)
    
    output_path = os.path.join(PROCESSED_DIR, "fund_scorecard.csv")
    df_m.to_csv(output_path, index=False)
    print(f"Metrics calculations complete! Fund scorecard saved to {output_path}")
    
    # Save to SQLite
    print("Loading scorecard to SQLite fact_performance_computed table...")
    conn = sqlite3.connect(DB_PATH)
    # Ensure table exists
    with open("/Users/manojvardhan/Bluestocks/sql/schema.sql", "r") as f:
        sql = f.read()
    conn.cursor().executescript(sql)
    # Load
    df_m.to_sql('fact_performance_computed', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Scorecard loaded to SQLite.")

if __name__ == "__main__":
    compute_metrics()
