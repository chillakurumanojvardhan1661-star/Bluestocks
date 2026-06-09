import subprocess
import sys

def run_script(script_path, args=None):
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    print(f"\n>>> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"Error executing {script_path}. Exiting.")
        sys.exit(1)

def main():
    print("=" * 60)
    print("      BLUESTOCK MUTUAL FUND ANALYTICS PIPELINE ENGINE      ")
    print("=" * 60)
    
    # Step 1: Live NAV Ingestion
    run_script("/Users/manojvardhan/Bluestocks/scripts/live_nav_fetch.py")
    
    # Step 2: ETL Pipeline & SQLite DB loading
    run_script("/Users/manojvardhan/Bluestocks/scripts/etl_pipeline.py")
    
    # Step 3: EDA Charts Generation
    run_script("/Users/manojvardhan/Bluestocks/scripts/generate_eda_charts.py")
    
    # Step 4: Compute Performance Metrics
    run_script("/Users/manojvardhan/Bluestocks/scripts/compute_metrics.py")
    
    # Step 5: Advanced Risk Metrics
    run_script("/Users/manojvardhan/Bluestocks/scripts/advanced_analytics.py")
    
    print("\n" + "=" * 60)
    print("Pipeline Execution Completed Successfully!")
    print("All processed data loaded to SQLite. Run dashboard via:")
    print("streamlit run dashboard/dashboard_app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
