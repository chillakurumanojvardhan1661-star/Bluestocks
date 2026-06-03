-- 10 Analytical SQL Queries for Mutual Fund Capstone Project

-- 1. Top 5 funds by AUM (from fact_performance)
SELECT amfi_code, scheme_name, fund_house, category, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for HDFC Top 100 Direct (125497) in 2024
SELECT d.year, d.month, AVG(n.nav) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.nav_date = d.date_id
WHERE n.amfi_code = '125497' AND d.year = 2024
GROUP BY d.year, d.month
ORDER BY d.month;

-- 3. Monthly SIP inflow YoY growth (comparing 2024 vs 2025)
SELECT 
    t1.month AS month_2024, 
    t1.sip_inflow_crore AS inflow_2024,
    t2.month AS month_2025, 
    t2.sip_inflow_crore AS inflow_2025,
    ((t2.sip_inflow_crore - t1.sip_inflow_crore) / t1.sip_inflow_crore) * 100 AS yoy_growth_pct
FROM fact_sip_industry t1
JOIN fact_sip_industry t2 ON SUBSTR(t1.month, 6, 2) = SUBSTR(t2.month, 6, 2)
WHERE SUBSTR(t1.month, 1, 4) = '2024' AND SUBSTR(t2.month, 1, 4) = '2025'
ORDER BY SUBSTR(t1.month, 6, 2);

-- 4. Total transaction amount (INR) and count by investor state
SELECT state, COUNT(*) AS tx_count, SUM(amount_inr) AS total_invested_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_invested_inr DESC;

-- 5. Funds with expense ratio < 1.0% sorted by expense ratio
SELECT amfi_code, scheme_name, fund_house, category, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Transactions count and average amount by city tier (T30 vs B30)
SELECT city_tier, COUNT(*) AS tx_count, AVG(amount_inr) AS avg_tx_amount
FROM fact_transactions
GROUP BY city_tier;

-- 7. Top 5 sectors by weighted portfolio representation across all funds
SELECT sector, SUM(weight_pct) AS total_weight_pct
FROM fact_portfolio
GROUP BY sector
ORDER BY total_weight_pct DESC
LIMIT 5;

-- 8. Monthly transaction counts and amounts for 2025
SELECT d.year, d.month, COUNT(*) AS tx_count, SUM(t.amount_inr) AS total_amount_inr
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date_id
WHERE d.year = 2025
GROUP BY d.year, d.month
ORDER BY d.month;

-- 9. Top 3 performing funds in the 'Equity' category (based on dim_fund category) by 3-year return
SELECT p.amfi_code, p.scheme_name, p.fund_house, p.return_3yr_pct, p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.category = 'Equity'
ORDER BY p.return_3yr_pct DESC
LIMIT 3;

-- 10. KYC Verified vs Pending transaction summary (total count and amount)
SELECT kyc_status, COUNT(*) AS tx_count, SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY kyc_status;
