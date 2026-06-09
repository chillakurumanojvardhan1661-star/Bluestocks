# Mutual Fund Analytics Platform — Final Capstone Report
**Prepared by**: Intern / Data Analyst — Bluestock Fintech  
**Date**: June 2026

---

## 1. Executive Summary
The Indian mutual fund industry has seen tremendous growth, with AUM reaching Rs. 81 lakh crore in December 2025. However, fragmented data across multiple sites (AMFI, NSE, APIs) hinders retail and institutional decision-making. 

This project successfully constructs an end-to-end data engineering pipeline and interactive dashboard. The pipeline automates the ingestion of raw data (historical CSVs & live NAV API calls), applies strict data validation and cleaning (including forward-filling holiday NAV gaps), models the data into a normalized SQLite star schema, and delivers an interactive Streamlit Dashboard displaying performance and demographic risk metrics.

---

## 2. System Architecture & ETL Pipeline
The system utilizes a 5-layer architecture mirroring professional fintech production pipelines:
1. **Data Sources (Extract)**: 
   - Public AMFI daily notes, historical datasets, and live REST API calls (`api.mfapi.in`).
2. **Data Processing (Transform)**:
   - Pandas cleaning scripts to normalize dates, handle transaction types, remove duplicates, and calculate rolling performance metrics.
   - Forward-filled weekends/holidays to maintain historical continuity for time-series computations.
3. **Data Storage (Load)**:
   - Normalised Star Schema built inside SQLite (`bluestock_mf.db`) containing:
     - `dim_fund`, `dim_date`
     - `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `fact_portfolio`, `fact_sip_industry`, `fact_performance_computed`
4. **Analytics Engine (Analyse)**:
   - Mathematical calculations of CAGR, Sharpe (Rf=6.5%), Sortino, Jensen's Alpha, Beta, Max Drawdowns, HHI, and Value at Risk (VaR 95% / CVaR).
5. **Interactive Visualization (Visualise)**:
   - A multi-page Streamlit Web Dashboard displaying industry metrics, scatter plots of return vs. risk, demographic breakdowns, and category heatmaps.

---

## 3. Performance & Risk-Adjusted Analytics
Using the mathematical engine, all funds were ranked to form a composite scorecard (Weighted combination of 3-yr return, Sharpe, Alpha, lower expense ratio, and Max Drawdown):

### Top Performing Schemes (Sample)
- **Axis Midcap Fund - Regular - Growth**: Sharpe ratio of **1.76**, showing excellent risk-adjusted performance.
- **HDFC Mid-Cap Opportunities Fund**: Sharpe ratio of **1.62**, with strong 3-year return metrics.

### Advanced Risk Metrics Summary
- **Sector Concentration (HHI)**: Mid-cap and Small-cap funds show high concentration indices in Banking, IT, and Pharmaceuticals.
- **Value at Risk (VaR 95%)**: High-risk equity funds present a daily VaR of ~1.8% to 2.2%, indicating that on 95% of trading days, losses do not exceed this threshold.

---

## 4. Key EDA & Investor Behavior Insights
1. **AUM Dominance**: SBI Mutual Fund maintains the largest market share (Rs. 12.5 lakh crore as of Dec 2025).
2. **Demographics**: Investors in the 26-35 and 36-45 age brackets account for over 58% of total transactions.
3. **At-Risk Cohorts**: Gap analysis of SIP cycles identified that roughly 8% of active SIP investors have transaction gaps exceeding 35 days and are flagged as 'At-Risk' for drop-outs.
