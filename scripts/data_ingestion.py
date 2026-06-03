import os
import pandas as pd

RAW_DIR = "/Users/manojvardhan/Bluestocks/data/raw"

def print_separator(title):
    print("\n" + "=" * 50)
    print(f" {title} ")
    print("=" * 50)

def main():
    print("Loading Day 1 CSV Datasets...")
    files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith('.csv') and not f.startswith('live_nav')])
    
    datasets = {}
    for f in files:
        name = f.split('.')[0]
        path = os.path.join(RAW_DIR, f)
        df = pd.read_csv(path)
        datasets[name] = df
        
        print_separator(f"Dataset: {f}")
        print(f"Shape: {df.shape}")
        print("\nDatatypes:")
        print(df.dtypes)
        print("\nHead (First 3 rows):")
        print(df.head(3))

    # Exploration of fund master
    print_separator("Fund Master Exploration")
    fm = datasets.get('01_fund_master')
    if fm is not None:
        print("Unique Fund Houses count:", fm['fund_house'].nunique())
        print("Categories distribution:")
        print(fm['category'].value_counts())
        print("\nSub-categories distribution:")
        print(fm['sub_category'].value_counts())
        print("\nRisk Categories distribution:")
        print(fm['risk_category'].value_counts())
    
    # Validation of AMFI codes
    print_separator("Data Quality Summary & Code Validation")
    nh = datasets.get('02_nav_history')
    if fm is not None and nh is not None:
        master_codes = set(fm['amfi_code'].unique())
        nav_codes = set(nh['amfi_code'].unique())
        missing_codes = master_codes - nav_codes
        
        print(f"Unique AMFI codes in fund_master: {len(master_codes)}")
        print(f"Unique AMFI codes in nav_history: {len(nav_codes)}")
        print(f"Missing codes in nav_history: {missing_codes}")
        
        if len(missing_codes) == 0:
            print("Validation PASSED: All fund codes in master list exist in the NAV history.")
        else:
            print("Validation FAILED: Some fund codes are missing NAV history.")
            
if __name__ == "__main__":
    main()
