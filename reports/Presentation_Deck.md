# Bluestock Mutual Fund Analytics — Presentation Deck
**Internship Capstone Project**  
**Presented by**: Intern / Data Analyst — Bluestock Fintech  
**Date**: June 2026

---

## Slide 1: Title & Introduction
- **Project**: Mutual Fund Analytics Platform
- **Focus**: End-to-End Data Engineering, ETL Pipeline, & Interactive Dashboard
- **Host AMC**: Bluestock Fintech Pvt. Ltd.

---

## Slide 2: Problem Statement
- **Fragmented Data**: NAV, AUM, and transactions are scattered in multiple formats.
- **Comparison Gap**: Hard to evaluate mutual funds on a risk-adjusted basis.
- **Solution**: A unified SQLite database with automated metrics calculations.

---

## Slide 3: Project Objectives
- **O1**: Automate data ingestion and API connections.
- **O2**: Design a normalized database schema.
- **O3**: Compute risk metrics: Sharpe, Sortino, Alpha, Beta, VaR, HHI.
- **O4**: Build an interactive web dashboard.

---

## Slide 4: Data Sources
- **AMFI India**: Public mutual fund scheme details.
- **mfapi.in**: Rest API for daily NAV records.
- **NSE/BSE**: Index prices for Nifty 50 and Nifty 100.
- **Internal Datasets**: Simulated transactions and portfolio holdings.

---

## Slide 5: System Architecture
- **Layer 1**: Extract (API & CSV parsing)
- **Layer 2**: Transform (Pandas processing, forward-fill holidays)
- **Layer 3**: Load (SQLite relational database)
- **Layer 4**: Analyze (Math risk metrics calculation)
- **Layer 5**: Visualize (Streamlit application)

---

## Slide 6: Database Star Schema
- **Dimensions**: `dim_fund`, `dim_date`.
- **Facts**: `fact_nav` (daily return), `fact_transactions` (demographics), `fact_performance`, `fact_aum`, `fact_portfolio`.

---

## Slide 7: Exploratory Data Analysis (EDA)
- **AUM**: SBI MF dominates at Rs. 12.5 lakh crore.
- **SIP**: Inflows hit record Rs. 31,002 crore in December 2025.
- **Geographics**: Maharashtra and Gujarat represent the largest investment volume.

---

## Slide 8: Fund Performance & Ranks
- **Methodology**: Composite scorecard ranking (Weighted 3yr CAGR, Sharpe, Alpha, Expense, Max DD).
- **Leaders**: Mid-cap and Small-cap funds lead performance metrics.

---

## Slide 9: Advanced Risk Analytics
- **Value at Risk (VaR 95%)**: High-risk equity funds present a ~2.0% daily maximum loss ceiling.
- **Concentration**: HHI sector analysis shows IT and Banking as highly concentrated sectors.

---

## Slide 10: Investor Analytics & Cohorts
- **Age Demographic**: 26-45 years represents the highest volume of investors.
- **Continuation**: 8% of SIP accounts identified as 'At-Risk' due to payment gaps > 35 days.

---

## Slide 11: Interactive Dashboard (Streamlit)
- **Multi-page Layout**: Industry Overview, Performance Scorecard, Investor Cohorts, and SIP Trends.
- **Feature**: Filters for Category, State, Age Group, and City Tiers.

---

## Slide 12: Conclusion & Future Scope
- **Achievement**: Built a robust, automated pipeline processing over 100K data rows.
- **Future Scope**: Integrate portfolio optimization module (Markowitz Frontier) and real-time alerts.
