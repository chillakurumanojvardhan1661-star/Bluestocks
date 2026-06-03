# Bluestock Mutual Fund Analytics Platform
**Capstone Project - End-to-End Data Engineering & ETL Pipeline**

## Project Overview
This repository contains the first two days of the Mutual Fund Analytics Capstone Project for Bluestock Fintech. 

The goal of this phase is to construct a robust ETL pipeline that fetches live mutual fund NAV data from the `mfapi.in` public API, consolidates and cleans 10 historical datasets, designs a normalized SQL database schema, and loads the data into SQLite.

## Folder Structure
```
bluestock_mf_capstone/
├── data/
│   ├── raw/             ← Original downloaded files & live fetches
│   ├── processed/       ← Cleaned, transformed CSV files
│   └── db/              ← SQLite Database (bluestock_mf.db)
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   └── 02_data_cleaning.ipynb
├── scripts/
│   ├── etl_pipeline.py  ← Master ETL execution script
│   └── live_nav_fetch.py← Ingestion script from mfapi.in API
├── sql/
│   ├── schema.sql       ← Relational Star Schema DDL definitions
│   └── queries.sql      ← 10 Analytical queries
├── data_dictionary.md   ← Columns, data types, and source mappings
└── README.md            ← Setup and documentation guide
```

## Setup & Running Guide

### 1. Requirements
Ensure you have Python 3.10+ installed. Install dependencies:
```bash
pip install pandas numpy requests sqlalchemy
```

### 2. Running Ingestion & ETL Pipeline
1. Run the live NAV fetcher to pull the newest NAV records from `mfapi.in` API:
   ```bash
   python3 scripts/live_nav_fetch.py
   ```
2. Run the main ETL script to clean raw CSV files and load tables into the SQLite DB:
   ```bash
   python3 scripts/etl_pipeline.py
   ```

### 3. Querying the Database
The database is stored locally in `data/db/bluestock_mf.db`. You can query it using sqlite CLI or python:
```bash
sqlite3 data/db/bluestock_mf.db < sql/queries.sql
```
