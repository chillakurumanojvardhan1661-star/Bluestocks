import os
import sqlite3
import pandas as pd
import numpy as np

# Path definitions
RAW_DIR = "/Users/manojvardhan/Bluestocks/data/raw"
PROCESSED_DIR = "/Users/manojvardhan/Bluestocks/data/processed"
DB_DIR = "/Users/manojvardhan/Bluestocks/data/db"
DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")
SCHEMA_PATH = "/Users/manojvardhan/Bluestocks/sql/schema.sql"

def init_db():
    print("Initializing Database...")
    os.makedirs(DB_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Error removing old DB file: {e}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SCHEMA_PATH, 'r') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()
    conn.close()
    print("Database and tables initialized.")

def clean_fund_master():
    print("Cleaning 01_fund_master.csv...")
    df = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    # Verify/fill missing values
    df['sub_category'] = df['sub_category'].fillna('Unknown')
    df['fund_manager'] = df['fund_manager'].fillna('Unknown')
    # Validate exit load and expense ratio ranges
    df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
    df['exit_load_pct'] = pd.to_numeric(df['exit_load_pct'], errors='coerce')
    
    # Save cleaned
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_fund_master.csv"), index=False)
    return df

def clean_nav_history():
    print("Cleaning 02_nav_history.csv...")
    df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    
    # Parse dates and NAV
    df['date'] = pd.to_datetime(df['date'])
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    df = df.dropna(subset=['amfi_code', 'date', 'nav'])
    df = df[df['nav'] > 0]
    
    # Sort
    df = df.sort_values(by=['amfi_code', 'date']).drop_duplicates(subset=['amfi_code', 'date'])
    
    # Forward-fill weekends/holidays per scheme
    filled_dfs = []
    for code, group in df.groupby('amfi_code'):
        group = group.set_index('date')
        min_date = group.index.min()
        max_date = group.index.max()
        # Generate complete date range (all calendar days)
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        # Reindex and forward fill NAV
        group = group.reindex(all_dates)
        group['amfi_code'] = code
        group['nav'] = group['nav'].ffill()
        # Calculate daily return
        group['daily_return_pct'] = group['nav'].pct_change() * 100
        group['daily_return_pct'] = group['daily_return_pct'].fillna(0.0)
        group = group.reset_index().rename(columns={'index': 'date'})
        filled_dfs.append(group)
        
    df_clean = pd.concat(filled_dfs, ignore_index=True)
    df_clean['date'] = df_clean['date'].dt.strftime('%Y-%m-%d')
    
    # Save cleaned
    df_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"), index=False)
    return df_clean

def clean_investor_transactions():
    print("Cleaning 08_investor_transactions.csv...")
    df = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    
    # Clean and validate
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
    df['amount_inr'] = pd.to_numeric(df['amount_inr'], errors='coerce')
    df = df[df['amount_inr'] > 0]
    df['transaction_type'] = df['transaction_type'].str.strip()
    df['kyc_status'] = df['kyc_status'].str.strip()
    
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_transactions.csv"), index=False)
    return df

def clean_performance():
    print("Cleaning 07_scheme_performance.csv...")
    df = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))
    
    # Convert numeric fields
    numeric_cols = [
        'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 
        'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio', 
        'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct', 
        'aum_crore', 'expense_ratio_pct'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    df.to_csv(os.path.join(PROCESSED_DIR, "clean_performance.csv"), index=False)
    return df

def clean_simple_csv(filename, numeric_cols=None):
    print(f"Cleaning {filename}...")
    df = pd.read_csv(os.path.join(RAW_DIR, filename))
    if numeric_cols:
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    df.to_csv(os.path.join(PROCESSED_DIR, f"clean_{filename.split('_', 1)[-1]}"), index=False)
    return df

def generate_dim_date(nav_dates, tx_dates):
    print("Generating dim_date dimension...")
    all_dates = pd.to_datetime(list(set(nav_dates) | set(tx_dates)))
    all_dates = sorted(all_dates)
    
    date_df = pd.DataFrame({'date': all_dates})
    date_df['date_id'] = date_df['date'].dt.strftime('%Y-%m-%d')
    date_df['date'] = date_df['date_id']
    date_df['year'] = date_df['date'].apply(lambda x: int(x[:4]))
    date_df['month'] = date_df['date'].apply(lambda x: int(x[5:7]))
    date_df['quarter'] = date_df['month'].apply(lambda m: (m - 1) // 3 + 1)
    
    # is_weekday: Mon-Fri is 1, Sat-Sun is 0
    temp_dates = pd.to_datetime(date_df['date_id'])
    date_df['is_weekday'] = temp_dates.dt.dayofweek.apply(lambda x: 1 if x < 5 else 0)
    
    date_df.to_csv(os.path.join(PROCESSED_DIR, "clean_date.csv"), index=False)
    return date_df

def load_to_db(conn, df, table_name):
    print(f"Loading {len(df)} rows into {table_name}...")
    # Get columns of the SQLite table to match
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    db_cols = [row[1] for row in cursor.fetchall()]
    
    # Filter/align df columns
    valid_cols = [col for col in df.columns if col in db_cols]
    df_to_load = df[valid_cols]
    
    # Insert
    df_to_load.to_sql(table_name, conn, if_exists='append', index=False)

def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    init_db()
    
    df_fund = clean_fund_master()
    df_nav = clean_nav_history()
    df_tx = clean_investor_transactions()
    df_perf = clean_performance()
    
    df_aum = clean_simple_csv("03_aum_by_fund_house.csv", ['aum_lakh_crore', 'aum_crore', 'num_schemes'])
    df_sip = clean_simple_csv("04_monthly_sip_inflows.csv", ['sip_inflow_crore', 'active_sip_accounts_crore', 'new_sip_accounts_lakh', 'sip_aum_lakh_crore', 'yoy_growth_pct'])
    df_cat = clean_simple_csv("05_category_inflows.csv")
    df_folio = clean_simple_csv("06_industry_folio_count.csv")
    df_port = clean_simple_csv("09_portfolio_holdings.csv", ['weight_pct', 'market_value_cr', 'current_price_inr'])
    df_bench = clean_simple_csv("10_benchmark_indices.csv")
    
    # Generate dim_date
    df_date = generate_dim_date(df_nav['date'], df_tx['transaction_date'])
    
    # Connect and load
    conn = sqlite3.connect(DB_PATH)
    
    # Load all tables
    load_to_db(conn, df_fund, "dim_fund")
    load_to_db(conn, df_date, "dim_date")
    load_to_db(conn, df_nav.rename(columns={'date': 'nav_date'}), "fact_nav")
    load_to_db(conn, df_tx, "fact_transactions")
    load_to_db(conn, df_perf, "fact_performance")
    load_to_db(conn, df_aum, "fact_aum")
    load_to_db(conn, df_port, "fact_portfolio")
    load_to_db(conn, df_sip, "fact_sip_industry")
    
    conn.close()
    print("ETL Pipeline completed successfully!")

if __name__ == "__main__":
    main()
