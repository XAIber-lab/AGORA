#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import warnings
import logging
import torch
import nltk
import numpy as np
from collections import defaultdict
from nltk.tokenize import sent_tokenize
from transformers import logging as transformers_logging

# 1. Setup and Silencing
transformers_logging.set_verbosity_error()
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["CUDA_VISIBLE_DEVICES"] = "" 
os.environ["MOVERSCORE_MODEL"] = "microsoft/deberta-v3-small"

# Ensure NLTK data is present
nltk.download('punkt', quiet=True)

# Import your moverscore_v2 functions
from moverscore_v2 import get_idf_dict, word_mover_score, get_fact_weights

import re

def get_best_sentence_match(summary_text: str, fact: str, threshold: float = 0.70):
    words = [w.strip('.,;:') for w in summary_text.split()]
    fact_words_list = [w.strip('.,;:') for w in fact.split()]
    fact_len = len(fact_words_list)
    
    # --- 1. DYNAMIC CANDIDATE GENERATION ---
    candidates = []
    
    # Define a range of chunk sizes. 
    # This ensures chunks are NOT fixed in size.
    # We check fragments from 4 words up to fact_len + 4.
    min_size = max(4, fact_len - 3)
    max_size = fact_len + 7
    
    for window_size in range(min_size, max_size + 1):
        # Determine the overlap/step dynamically.
        # step = 1 is the most exhaustive (maximum overlap).
        step = 1 
        
        if len(words) >= window_size:
            for i in range(0, len(words) - window_size + 1, step):
                chunk = " ".join(words[i : i + window_size])
                candidates.append(chunk)

    # --- 2. EVALUATION LOGIC ---
    best_score = -1.0
    best_chunk = "N/A"
    #idf_dict = get_fact_weights(fact)
    idf_dict = defaultdict(lambda: 1.)

    
    def normalize_nums(text):
        # Captures integers and decimals
        nums = re.findall(r'\d+(?:\.\d+)?', text)
        return {n[:4] for n in nums} 

    fact_nums_norm = normalize_nums(fact)

    # Set() avoids redundant evaluation of the same string
    for cand in set(candidates):
        cand_word_count = len(cand.split())

        # Strip periods and make lowercase just for the MoverScore calculation
        fact = fact.lower().replace('.', '')
        cand = cand.lower()
        
        # Raw MoverScore
        s = word_mover_score([fact], [cand], idf_dict, idf_dict, n_gram=1, batch_size=1)[0]
        
        # --- IMPROVED NUMERIC BOOST ---
        cand_nums_norm = normalize_nums(cand)
        
        if fact_nums_norm:
            if fact_nums_norm.issubset(cand_nums_norm):
                s += 0.15  # Major reward for exact data match
            elif fact_nums_norm.intersection(cand_nums_norm):
                s += 0.05  # Partial reward
        
        # --- DENSITY REWARD / LENGTH PENALTY ---
        # If a 5-word chunk and a 10-word chunk have the same info,
        # the 5-word chunk should win. We penalize "extra" words.
        size_ratio = cand_word_count / fact_len
        if size_ratio > 1.2:
            s -= 0.03 * (size_ratio) # Penalize dilution

        s = min(1.0, s) 
        
        # Update best match
        if s > best_score:
            best_score = s
            best_chunk = cand
        elif abs(s - best_score) < 0.001:
            # Tie-breaker: if scores are basically equal, prefer the shorter chunk
            if len(cand) < len(best_chunk):
                best_chunk = cand
            
    return float(best_score), best_score >= threshold, best_chunk

import pandas as pd
import os
import re

GROUND_TRUTHS = {

    # -----------------------------------------------------
    # Control 148
    # -----------------------------------------------------
    148: [
        # Incident volumes & severities
        "Active incidents decreased from 1963 to 451.",
        "The decrease in active incidents suggests mass incidents in the previous month or a resolved backlog.",
        #"323 closed incidents had high severity.", ->UC1
        #"216 closed incidents had critical severity.", ->UC1
        "7 incidents had critical severity",
        "103 incidents had high severity.",
        "The majority of incidents had low severity.",
        "A mass closure of active incidents began on Friday, June 3.",

        # Compliance metrics
        #"Average process fitness was approximately 0.695", ->UC1
        "Average cost was 0.047 which is in the low process serverity range.",
        "The average SLA was very low with 44.43%.",
        "Average time to resolve incidents was 15 days 3 hours 27 minutes (21807 minutes).",
    ],

    # -----------------------------------------------------
    # Control 149
    # -----------------------------------------------------
    149: [
        # Durations per activity
        "Average detection duration was 4 days 6 hours 35 minutes (6155 minutes). Above the acceptable threshold.",
        
        "Average activation duration was 8 days 18 hours 55 minutes (12655 minutes). Above the acceptable threshold.",

        "Average awaiting duration was 16 days 8 hours 10 minutes (23530 minutes). Above the acceptable threshold.",

        "Average transition time from awaiting to resolution was 8 days 1 hour 19 minutes (11599 minutes).",


        # Explanations for non-compliant transitions
        "The potentially non-compliant detection→awaiting transition is explained by merging into an existing awaiting incident.",
        "The potentially non-compliant detection→resolution transition is explained by temporary whitelisting and merging into already resolved cases."
    ],

    # -----------------------------------------------------
    # Control 150
    # -----------------------------------------------------
    150: [
        #"The most common variant (NRC) (Count 182) is non-compliant due to missing activation", ->UC1
        "The most common variant (NRC) (Count 182) is now considered process compliant due to automatic merge rules.",
        "Variants ARC (count 135) are missing detections and are non-compliant.",
        #"The most frequent variants show repetitive detections before activation.", ->UC1
        "Repetitive detections are no process violation due to potentially multiple triggers",
        #"Variants with awaiting state frequently show repetitive awaiting events.", ->UC1
        "Variants with repetitive awaiting activities are not process violations due to customer or third-party delays."
    ],

    # -----------------------------------------------------
    # Control 151
    # -----------------------------------------------------
    151: [
        # General
        #"Detection, activation, and awaiting activities showed high to critical non-compliance.", ->UC1
        "No process activities showed concering average compliance cost exceeding the individual thresholds.",

        # Detection
        "There were 319 missing detections, that violate threshold",
        #"There were 1777 repetitive detections, that violate the threshold", ->UC1
        "There were 1777 repetitive detections, that do not violate the threshold",
        "There were 0 detection mismatches.",

        # Activation
        #"There were 544 missing activations that violate the threshold", ->UC1
        "There were 544 missing activations caused by merge rules and are not process violations.",
        "There were 1990 repetitive activations, which violate the threshold",
        "There were 115 activation mismatches, which violate the theshold",

        # Awaiting
        #"There were 1653 repetitive awaiting events, that violate the threshold", ->UC1
        "There were 1653 repetitive awaiting events, that do not violate the threshold",
        "There were 4 awaiting mismatches.",

        # Resolution
        "There were 119 repetitive awaiting events, that violate the threshold",
        "45 resolution mismatches violate the threshold and may represent false negatives later reclassified as true positives."
    ],

    # -----------------------------------------------------
    # Control 152
    # -----------------------------------------------------
    152: [
        # Durations with minutes
        "Average detection duration was 4 days 6 hours 35 minutes (6155 minutes). Above the acceptable threshold.",

        "Average activation duration was 8 days 18 hours 55 minutes (12655 minutes). Above the acceptable threshold.",
        
        "Average awaiting duration was 16 days 8 hours 10 minutes (23530 minutes). Above the acceptable threshold.",
        
        "Average resolution duration was 5 days 22 hours 11 minutes (8531 minutes). Above the acceptable threshold.",
        
        # Additional context
        "No unusual temporal spikes were observed.",
        "Weekend periods with no work activity (approximately 2.5 days) partially explain increased durations.",
    ],

    # -----------------------------------------------------
    # Control 153
    # -----------------------------------------------------
    153: [
        #"Several incidents (216) had process fitness of 0.5 and below.", ->UC1
        "Critical process severity incidents are 7 in total",
        #"INC0032450 had the lowest process fitness of 0.19.", ->UC1
        "INC0033952 has the highest assigned compliance cost with 0.81",
        #"Multiple incidents had process fitness between 0.2 and 0.3.", ->UC1
        "INC0025696, INC0026744 and INC0032450 show cost of 0.41",
        "This critical process severity requires deeper individual incident analysis."
    ],

    # -----------------------------------------------------
    # Control 154
    # -----------------------------------------------------
    154: [
        "Low-priority (4) incidents are informational and spam about many symptoms, locations, and categories.",
        "Medium-priority (3) incidents show widely distributed symptoms and affected categories with no clear pattern.",
        "High-priority (2) incidents show repetitive symptom (491), location (161), and categories (46, 42, 53, 57, 61) and require compliance investigation.",
        "Critical-priority (1) incidents show repetitive patterns in symptom (491) and locations (204, 143 and categories (46, 42) and require detailed compliance assessment."
    ]
}

def process_batch_evaluation(csv_input, report_output, stats_csv_output):
    if not os.path.exists(csv_input):
        print(f"Error: '{csv_input}' not found.")
        return
        
    df = pd.read_csv(
    csv_input, 
    quotechar='"',          # Recognizes text wrapped in double quotes
    doublequote=True,       # Handles internal quotes within the text
    skipinitialspace=True,  # Cleans up whitespace after commas
    encoding='utf-8',       # Ensures special characters are read correctly
    on_bad_lines='warn'     # Prevents crashing if a line is still malformed
    )

    stats_rows = []
    last_cid = None
    
    report_content = ["="*100, f"{'ROBUSTNESS EVALUATION REPORT':^100}", "="*100, ""]

    for index, row in df.iterrows():
        cid = row['control_id']
        iteration = row['iteration']

        if cid != last_cid:
            header = f"\n{'#'*100}\n### NEW CONTROL UNIT: {cid} ###\n{'#'*100}\n"
            report_content.append(header)
            print(header) # Print header to console too
            last_cid = cid

        summary_text = str(row['recommendation']) if pd.notna(row['recommendation']) else ""
        current_facts = GROUND_TRUTHS.get(cid)
        
        if current_facts is None:
            continue

        iter_header = f"\n>> STARTING ID: {cid} | ITERATION: {iteration}"
        report_content.append(iter_header)
        print(iter_header)
        print("-" * 80)
        
        row_found_count = 0
        
        for f_idx, fact in enumerate(current_facts):
            score, is_found, best_chunk = get_best_sentence_match(summary_text, fact)
            
            # Determine status label
            if score >= 0.85:
                status = "✅ FOUND"
                row_found_count += 1
            elif score >= 0.60:
                status = "🟡 INDICATED"
            else:
                status = "⚪ MISSING"

            # --- CONSOLE PRINT FOR EVERY FACT ---
            print(f"Fact {f_idx+1}: {status} | Score: {score:.4f}")
            print(f"  Target: {fact[:80]}...")
            print(f"  Evidence: \"{best_chunk}\"")
            print("  " + "."*40)

            # Record to statistical list
            stats_rows.append({
                'control_id': cid,
                'iteration': iteration,
                'fact_index': f_idx + 1,
                'mover_score': round(score, 4),
                'is_found_binary': 1 if score >= 0.85 else 0,
                'status': status.split()[-1], # Strip emoji for CSV
                'fact_text': fact,
                'evidence_found': best_chunk
            })

            # Add detailed fact info to the TEXT REPORT
            report_content.append(f"Fact {f_idx+1}: {status} | Score: {score:.4f}")
            report_content.append(f"  Ground Truth: {fact}")
            report_content.append(f"  Best Chunk:   {best_chunk}")
            report_content.append("-" * 40)

        # Summary logging for the console
        coverage = (row_found_count / len(current_facts)) * 100
        coverage_summary = f"\n[SUMMARY] ID {cid} | Iter {iteration} | Total Coverage: {coverage:.1f}% ({row_found_count}/{len(current_facts)})"
        
        report_content.append(coverage_summary)
        report_content.append("="*100)
        print(coverage_summary)
        print("="*80)

    # Save outputs
    stats_df = pd.DataFrame(stats_rows)
    stats_df.to_csv(stats_csv_output, index=False)
    
    with open(report_output, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))

    print(f"\nDONE: {len(stats_df)} fact-check observations exported to {stats_csv_output}")

if __name__ == "__main__":
    process_batch_evaluation(
        csv_input="assessment_security_control_results_robustness_uc2.csv",
        report_output="mover_score_detailed_report_UC2_temp1.txt",
        stats_csv_output="fact_check_stats_for_interpretation_UC2_temp1.csv"
    )
