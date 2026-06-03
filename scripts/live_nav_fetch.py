import requests
import json
import pandas as pd
import os

SCHEMES = {
    "125497": "HDFC_Top_100",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

OUTPUT_DIR = "/Users/manojvardhan/Bluestocks/data/raw"

def fetch_nav(scheme_code, name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching NAV data for {name} ({scheme_code})...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        meta = data.get("meta", {})
        nav_list = data.get("data", [])
        
        if not nav_list:
            print(f"No NAV data found for {scheme_code}")
            return
        
        df = pd.DataFrame(nav_list)
        df["amfi_code"] = scheme_code
        df["fund_house"] = meta.get("fund_house")
        df["scheme_name"] = meta.get("scheme_name")
        
        # Reorder columns
        df = df[["amfi_code", "date", "nav", "fund_house", "scheme_name"]]
        
        filename = os.path.join(OUTPUT_DIR, f"live_nav_{scheme_code}.csv")
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} rows to {filename}")
        
    except Exception as e:
        print(f"Error fetching data for {scheme_code}: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for code, name in SCHEMES.items():
        fetch_nav(code, name)

if __name__ == "__main__":
    main()
