import pandas as pd
import numpy as np
import os

def compute_granular_fact_stats(uc1_csv, uc2_csv):
    """
    Computes and prints mean/std for every individual fact (proposition) 
    across all 10 iterations for both UC1 and UC2.
    """
    
    def process_file(file_path, label):
        if not os.path.exists(file_path):
            print(f"\n[!] Error: {file_path} not found.")
            return
        
        df = pd.read_csv(file_path)
        
        # Group by Control ID AND Fact Text (or Fact Index) 
        # to see how each specific fact performed across the 10 iterations
        fact_stats = df.groupby(['control_id', 'fact_index', 'fact_text'])['mover_score'].agg(['mean', 'std']).reset_index()
        
        print(f"\n{'='*100}")
        print(f"{'GRANULAR FACT ANALYSIS: ' + label:^100}")
        print(f"{'='*100}")
        print(f"{'ID':<6} | {'Fact #':<6} | {'Mean':<8} | {'± StdDev':<10} | {'Fact Text Snippet'}")
        print(f"{'-'*100}")
        
        for _, row in fact_stats.iterrows():
            # Handle cases where StdDev might be NaN (if only 1 iteration exists)
            std_val = row['std'] if pd.notna(row['std']) else 0.0
            snippet = (row['fact_text'][:55] + '...') if len(row['fact_text']) > 55 else row['fact_text']
            
            print(f"{int(row['control_id']):<6} | "
                  f"{int(row['fact_index']):<6} | "
                  f"{row['mean']:<8.4f} | "
                  f"±{std_val:<8.4f} | "
                  f"{snippet}")
        print(f"{'='*100}")

    # Process both Use Cases
    process_file(uc1_csv, "USE CASE 1 (TEMP 1.0)")
    process_file(uc2_csv, "USE CASE 2 (TEMP 1.0)")

def main():
    # Your specified file paths
    UC1_RESULTS = "fact_check_stats_for_interpretation_UC1_temp1.csv"
    UC2_RESULTS = "fact_check_stats_for_interpretation_UC2_temp1.csv"
    
    # Run the granular console computation
    compute_granular_fact_stats(UC1_RESULTS, UC2_RESULTS)

if __name__ == "__main__":
    main()