# Data Dictionary — Bluestock Mutual Fund Analytics Platform

This document describes the schema of the Normalized Star Schema database loaded in SQLite (`bluestock_mf.db`).

---

## 1. Table: `dim_fund`
Stores metadata and details about the mutual fund schemes.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `amfi_code` (PK) | TEXT | AMFI unique scheme identifier code. |
| `fund_house` | TEXT | Asset Management Company (AMC) name. |
| `scheme_name` | TEXT | Official name of the mutual fund scheme. |
| `category` | TEXT | Asset category: Equity / Debt / Hybrid. |
| `sub_category` | TEXT | Sub-category (e.g. Large Cap, Mid Cap, Small Cap, Liquid). |
| `plan` | TEXT | Dividend option / plan: Regular or Direct. |
| `launch_date` | TEXT | Launch date of the fund (YYYY-MM-DD). |
| `benchmark` | TEXT | Benchmark index (e.g., Nifty 50, Nifty Midcap 150). |
| `expense_ratio_pct` | REAL | Total Expense Ratio (TER) in percentage. |
| `exit_load_pct` | REAL | Exit load percentage applied on redemptions. |
| `min_sip_amount` | REAL | Minimum SIP investment amount. |
| `min_lumpsum_amount`| REAL | Minimum Lumpsum investment amount. |
| `fund_manager` | TEXT | Name of the primary fund manager. |
| `risk_category` | TEXT | Risk label assigned by SEBI (Low to Very High). |
| `sebi_category_code`| TEXT | Internal SEBI category code (e.g., EC01, DC01). |

---

## 2. Table: `dim_date`
Calculated Date dimension for time-series and transaction grouping.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `date_id` (PK) | TEXT | Date string key in YYYY-MM-DD format. |
| `date` | TEXT | Date string. |
| `year` | INTEGER | Year of the date. |
| `month` | INTEGER | Month of the date (1-12). |
| `quarter` | INTEGER | Calendar Quarter (1-4). |
| `is_weekday` | INTEGER | Binary flag: 1 if Monday-Friday, 0 if Saturday-Sunday. |

---

## 3. Table: `fact_nav`
Stores daily Net Asset Value (NAV) time-series data for the schemes.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `amfi_code` (PK, FK) | TEXT | AMFI code referencing `dim_fund`. |
| `nav_date` (PK, FK) | TEXT | Date referencing `dim_date`. |
| `nav` | REAL | Net Asset Value (NAV) in Indian Rupees. |
| `daily_return_pct` | REAL | Percentage daily return computed as $(NAV_t - NAV_{t-1}) / NAV_{t-1} \times 100$. |

---

## 4. Table: `fact_transactions`
Contains transaction records for mutual fund investors.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `tx_id` (PK) | INTEGER | Auto-incrementing primary key. |
| `investor_id` | TEXT | Unique investor identifier. |
| `transaction_date` (FK)| TEXT | Date referencing `dim_date`. |
| `amfi_code` (FK) | TEXT | AMFI code referencing `dim_fund`. |
| `transaction_type` | TEXT | SIP / Lumpsum / Redemption. |
| `amount_inr` | REAL | Transaction amount in INR. |
| `state` | TEXT | Indian State of the investor. |
| `city` | TEXT | City of the investor. |
| `city_tier` | TEXT | City tier (T30 or B30). |
| `age_group` | TEXT | Age bracket of the investor. |
| `gender` | TEXT | Gender of the investor. |
| `annual_income_lakh`| REAL | Annual income of the investor in Lakhs (INR). |
| `payment_mode` | TEXT | Payment mode (e.g. UPI, Net Banking, Mandate). |
| `kyc_status` | TEXT | Status: Verified or Pending. |

---

## 5. Table: `fact_performance`
Calculated fund performance and risk-adjusted return metrics.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `amfi_code` (PK, FK) | TEXT | AMFI code referencing `dim_fund`. |
| `scheme_name` | TEXT | Name of the scheme. |
| `fund_house` | TEXT | Asset Management Company name. |
| `category` | TEXT | Category designation. |
| `plan` | TEXT | Direct or Regular. |
| `return_1yr_pct` | REAL | 1-year absolute return percentage. |
| `return_3yr_pct` | REAL | 3-year CAGR percentage. |
| `return_5yr_pct` | REAL | 5-year CAGR percentage. |
| `benchmark_3yr_pct` | REAL | 3-year CAGR percentage of the benchmark index. |
| `alpha` | REAL | Return above benchmark index. |
| `beta` | REAL | Risk/sensitivity compared to market benchmark. |
| `sharpe_ratio` | REAL | Risk-adjusted return measure (Sharpe Ratio). |
| `sortino_ratio` | REAL | Sortino Ratio (downside risk-adjusted). |
| `std_dev_ann_pct` | REAL | Annualized standard deviation of daily returns (%). |
| `max_drawdown_pct` | REAL | Worst peak-to-trough drop percentage. |
| `aum_crore` | REAL | Scheme-level assets under management (AUM) in Rs. Crore. |
| `expense_ratio_pct` | REAL | Expense ratio percentage. |
| `morningstar_rating`| INTEGER | Rating stars from 1 to 5. |
| `risk_grade` | TEXT | SEBI Risk designation. |

---

## 6. Table: `fact_aum`
Quarterly Assets Under Management (AUM) of the top fund houses.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` (PK) | INTEGER | Auto-incrementing primary key. |
| `fund_house` | TEXT | Asset Management Company name. |
| `date` | TEXT | Reporting date or quarter end date. |
| `aum_lakh_crore` | REAL | Total AUM in Lakh Crores (INR). |
| `aum_crore` | REAL | Total AUM in Crores (INR). |
| `num_schemes` | INTEGER | Number of active schemes. |

---

## 7. Table: `fact_portfolio`
Detailed equity stock holdings of the mutual funds.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `id` (PK) | INTEGER | Auto-incrementing primary key. |
| `amfi_code` (FK) | TEXT | AMFI code referencing `dim_fund`. |
| `stock_symbol` | TEXT | Ticker symbol of the stock. |
| `stock_name` | TEXT | Name of the public company. |
| `sector` | TEXT | Industry sector of the company (e.g. Banking, IT, Pharma). |
| `weight_pct` | REAL | Weight allocation percentage of this stock in the fund. |
| `market_value_cr` | REAL | Market value of holdings in Crores (INR). |
| `current_price_inr` | REAL | Current price of the stock in INR. |
| `portfolio_date` | TEXT | Date of the portfolio snapshot. |

---

## 8. Table: `fact_sip_industry`
Aggregate industry-wide monthly SIP transaction inflows and growth.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `month` (PK) | TEXT | Year-Month string (YYYY-MM). |
| `sip_inflow_crore` | REAL | Total SIP inflows in Rs. Crore. |
| `active_sip_accounts_crore`| REAL | Count of active SIP accounts in Crore. |
| `new_sip_accounts_lakh` | REAL | New monthly SIP registrations in Lakh accounts. |
| `sip_aum_lakh_crore` | REAL | Total SIP assets under management in Lakh Crores. |
| `yoy_growth_pct` | REAL | YoY growth rate of SIP inflows in percentage. |
