import pandas as pd
import math
import os
from nltk.tokenize import sent_tokenize
from moverscore_v2 import get_fact_weights, word_mover_score
from moverscore import get_best_sentence_match

# 1. Define your Ground Truth Facts
facts = [
    'Active incidents decreased from 1963 to 451.',
    'The decrease in active incidents suggests mass incidents or a resolved backlog.',
    '323 closed incidents had high severity.',
    '216 closed incidents had critical severity.',
    'A mass closure of active incidents began on Friday, June 3.',
    'Average process fitness was approximately 0.695.',
    'The average SLA was very low with 44.43%.',
    'Average time to resolve incidents was 15 days 3 hours 27 minutes.'
]

def process_batch_evaluation(csv_input, report_output):
    # Load the summaries
    df = pd.read_csv(csv_input)

    # FILTER: Only process rows where control_id is 148
    df_filtered = df[df['control_id'] == 148]
    
    if df_filtered.empty:
        print("No data found for Control ID 148.")
        return
    
    report_content = []
    report_content.append("="*80)
    report_content.append("BATCH FACT-CHECKING REPORT")
    report_content.append("="*80 + "\n")

    # Iterate over each summary in the CSV
    for index, row in df_filtered.iterrows():
        cid = row['control_id']
        iteration = row['iteration']
        summary_text = str(row['recommendation'])
        
        report_content.append(f"ID: {cid} | Iteration: {iteration}")
        report_content.append("-" * 40)
        
        found_count = 0
        
        for fact in facts:
            # Evaluate current fact against current summary
            score, found = get_best_sentence_match(summary_text, fact)
            
            if found:
                found_count += 1
                status = "✅ FOUND"
            else:
                status = "❌ MISSED"
            
            # Format the line for the report
            report_content.append(f"Fact: {fact[:45]:<45} | Score: {score:.4f} | {status}")
        
        # Calculate summary-level statistics
        coverage = (found_count / len(facts)) * 100
        report_content.append(f"\n>> SUMMARY RESULT: {found_count}/{len(facts)} Facts Found ({coverage:.2f}% Coverage)")
        report_content.append("\n" + "="*80 + "\n")
        
        # Print progress to console
        print(f"Processed Control {cid} (Iteration {iteration}) - Coverage: {coverage:.1f}%")

    # Save the final report to a text file
    with open(report_output, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
    
    print(f"\nDone! Full report saved to: {report_output}")

if __name__ == "__main__":
    # Ensure name.csv exists in the directory
    if os.path.exists("assessment_security_control_results_robustness.csv"):
        process_batch_evaluation("assessment_security_control_results_robustness.csv", "mover_score_evaluation_report.txt")
    else:
        print("Error: 'assessment_security_control_results_robustness.csv' not found.")