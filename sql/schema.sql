-- SQLite Schema for Bluestock Mutual Fund Analytics Platform
-- Star Schema Design

-- Dimension: Fund Master
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- Dimension: Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_id TEXT PRIMARY KEY, -- YYYY-MM-DD format
    date TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekday INTEGER NOT NULL -- 1 if weekday, 0 if weekend
);

-- Fact: Daily NAV History
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code TEXT NOT NULL,
    nav_date TEXT NOT NULL,
    nav REAL NOT NULL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, nav_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (nav_date) REFERENCES dim_date(date_id)
);

-- Fact: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    amfi_code TEXT NOT NULL,
    transaction_type TEXT NOT NULL, -- SIP / Lumpsum / Redemption
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_id)
);

-- Fact: Fund Performance Metrics
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code TEXT PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    plan TEXT,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Fact: AUM by Fund House
CREATE TABLE IF NOT EXISTS fact_aum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT NOT NULL,
    date TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER
);

-- Fact: Scheme Portfolio Holdings
CREATE TABLE IF NOT EXISTS fact_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL NOT NULL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Fact: Aggregate Industry SIP Inflows
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month TEXT PRIMARY KEY, -- YYYY-MM format
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);
