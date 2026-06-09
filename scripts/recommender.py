import sys
import pandas as pd
import sqlite3

DB_PATH = "/Users/manojvardhan/Bluestocks/data/db/bluestock_mf.db"

RISK_MAPPING = {
    "low": ["Low"],
    "moderate": ["Moderate", "Moderately High"],
    "high": ["High", "Very High"]
}

def get_recommendation(appetite):
    appetite = appetite.lower().strip()
    if appetite not in RISK_MAPPING:
        print("Invalid appetite. Choose from: Low, Moderate, High")
        return None
        
    allowed_categories = RISK_MAPPING[appetite]
    
    conn = sqlite3.connect(DB_PATH)
    # Query details joining fund master and calculated performance
    query = """
        SELECT f.amfi_code, f.scheme_name, f.fund_house, f.category, f.risk_category, p.sharpe_ratio, p.return_3yr_pct
        FROM dim_fund f
        JOIN fact_performance_computed p ON f.amfi_code = p.amfi_code
        WHERE f.risk_category IN ({})
        ORDER BY p.sharpe_ratio DESC
        LIMIT 3
    """.format(",".join(["'{}'".format(c) for c in allowed_categories]))
    
    df_rec = pd.read_sql_query(query, conn)
    conn.close()
    return df_rec

def main():
    if len(sys.argv) < 2:
        print("Usage: python recommender.py [Low/Moderate/High]")
        sys.exit(1)
        
    appetite = sys.argv[1]
    df_rec = get_recommendation(appetite)
    if df_rec is not None:
        print(f"\nTop 3 Fund Recommendations for '{appetite}' Risk Appetite:")
        print("=" * 70)
        print(df_rec.to_string(index=False))
        print("=" * 70)

if __name__ == "__main__":
    main()
