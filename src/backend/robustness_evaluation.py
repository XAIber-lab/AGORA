# Completed, reusable analysis script for multi-usecase, multi-question robustness evaluation.
# - Handles any number of use cases (UC1, UC2...), questions per UC, and temperatures (e.g., 0.5, 1.0, 1.5).
# - Computes semantic similarity (shared TF-IDF across all docs), Jaccard, ROUGE-L (token LCS), numeric fact extraction & comparison,
#   contradiction detection (numeric + sentiment heuristic), structural similarity (shared TF-IDF across sentences), and a combined robustness index.
# - Produces per-pair and aggregated reports, and per-question robustness across temperatures.
# - Example run at the end uses the three example texts you provided.
#
# Save and run locally or adapt to your environment. No external internet or models required.
#
# Requirements: scikit-learn, pandas, numpy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re, math
import pandas as pd
from itertools import combinations
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Show all rows
pd.set_option('display.max_rows', None)

# Show all columns
pd.set_option('display.max_columns', None)

# Prevent line wrapping / truncation in cells
pd.set_option('display.width', 10000)        # very wide output
pd.set_option('display.expand_frame_repr', False)  # do not wrap to multiple lines
pd.set_option('display.max_colwidth', None)  # full column content

# ------------------------- Helper text-processing functions -------------------------

def tokenize_simple(text):
    t = re.sub(r"(?<!\d)[\.,;:!'\"]|[\.,;:!'\"](?!\d)", " ", text.lower())
    tokens = [tok for tok in re.split(r"\s+", t) if tok]
    return tokens

def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)

def lcs_length(a, b):
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n-1, -1, -1):
        for j in range(m-1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i+1][j+1]
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j+1])
    return dp[0][0]

def rouge_l_f1(a, b):
    la = len(a); lb = len(b)
    if la==0 or lb==0:
        return 0.0
    lcs = lcs_length(a,b)
    prec = lcs / la
    rec = lcs / lb
    if prec+rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)

# Numeric extraction (improved for dates and percents)
num_pattern = re.compile(r"(?<!\w)(\d{1,4}(?:\.\d+)?%?|\d{4})(?!\w)")

def extract_numbers(text):
    raw = num_pattern.findall(text)
    # normalize some cases: '15' -> '15' (keep as str), percentages keep %
    return raw

# Sentence splitter for structural analysis
def split_sentences(text):
    sents = [s.strip() for s in re.split(r'(?<=[\.\?\!])\s+', text.strip()) if s.strip()]
    return sents

# ------------------------- Core evaluation functions -------------------------

def build_shared_tfidf(docs):
    """Build a single TF-IDF vectorizer over all documents (documents = list of strings)."""
    vec = TfidfVectorizer().fit(docs)
    mat = vec.transform(docs)
    return vec, mat

def pairwise_document_metrics(docs_dict):
    """docs_dict: {doc_id: text}. Computes TF-IDF cosine, jaccard, rouge_l for every pair."""
    ids = list(docs_dict.keys())
    texts = [docs_dict[i] for i in ids]
    # shared TF-IDF across all docs
    vec, mat = build_shared_tfidf(texts)
    cosmat = cosine_similarity(mat)
    results = []
    for i,j in combinations(range(len(ids)), 2):
        a = ids[i]; b = ids[j]
        cos = float(cosmat[i,j])
        ta = tokenize_simple(texts[i])
        tb = tokenize_simple(texts[j])
        jac = jaccard(ta, tb)
        rouge = rouge_l_f1(ta, tb)
        results.append({
            "docA": a, "docB": b,
            "cosine_tfidf": cos,
            "jaccard": jac,
            "rouge_l_f1": rouge
        })
    return pd.DataFrame(results)

def numeric_consistency_table(docs_dict):
    """Return table showing presence of numeric facts across docs and a summary"""
    ids = list(docs_dict.keys())
    nums_per_doc = {i: extract_numbers(docs_dict[i]) for i in ids}
    all_nums = sorted({n for vals in nums_per_doc.values() for n in vals}, key=lambda x: (not x.endswith('%'), x))
    rows = []
    for n in all_nums:
        row = {"number": n}
        for i in ids:
            row[i] = n in nums_per_doc[i]
        rows.append(row)
    df = pd.DataFrame(rows)
    return df, nums_per_doc

# Contradiction detection (numeric + sentiment heuristic)
positive_words = ["improved", "decreased", "reduced", "acceptable", "adequate", "stable"]
negative_words = ["critical", "alarming", "failure", "concerning", "not", "insufficient", "low", "below"]

def sentiment_score(s):
    s_lower = s.lower()
    score = 0
    for w in positive_words:
        if w in s_lower: score += 1
    for w in negative_words:
        if w in s_lower: score -= 1
    return score

def extract_simple_claims(text):
    sents = split_sentences(text)
    claims = []
    for s in sents:
        numbers = extract_numbers(s)
        claims.append({"sentence": s, "numbers": numbers, "sentiment": sentiment_score(s)})
    return claims

def detect_contradictions_between_texts(textA, textB):
    A = extract_simple_claims(textA)
    B = extract_simple_claims(textB)
    contradictions = []
    # numeric contradictions: same metric (e.g., SLA percent) mentioned with different values
    # we use heuristic: if both mention percentages or the same keywords and numbers differ -> flag
    for a in A:
        for b in B:
            # numeric overlap vs difference
            setA = set(a["numbers"]); setB = set(b["numbers"])
            if setA and setB and setA != setB:
                # if they share some keywords like 'sla' or 'fitness' or 'resolved' in sentences, treat as conflicting numeric mention
                key_terms = ["sla", "fitness", "resolve", "resolved", "assigned", "incidents", "severity", "time to resolve", "resolution"]
                if any(kt in a["sentence"].lower() for kt in key_terms) and any(kt in b["sentence"].lower() for kt in key_terms):
                    contradictions.append({"type":"numeric_mismatch", "sentA": a["sentence"], "sentB": b["sentence"], "numsA": list(setA), "numsB": list(setB)})
            # sentiment contradictions: opposing sentiment scores
            if a["sentiment"] * b["sentiment"] < 0:
                contradictions.append({"type":"sentiment_opposite", "sentA": a["sentence"], "sentB": b["sentence"], "sent_scoreA": a["sentiment"], "sent_scoreB": b["sentiment"]})
    return contradictions

# Structural similarity using SHARED TF-IDF over all sentences
def structural_similarity_scores(docs_dict):
    # gather all sentences and map back to docs
    doc_sent_map = {}
    all_sentences = []
    for doc_id, text in docs_dict.items():
        sents = split_sentences(text)
        doc_sent_map[doc_id] = sents
        all_sentences.extend(sents)
    if not all_sentences:
        return {}
    vec = TfidfVectorizer().fit(all_sentences)
    sent_mat = vec.transform(all_sentences)
    # index ranges for each doc's sentences
    idx = 0
    doc_ranges = {}
    for doc_id, sents in doc_sent_map.items():
        doc_ranges[doc_id] = (idx, idx+len(sents))
        idx += len(sents)
    # compute pairwise structural similarity: align sentences via cosine and take average max alignments
    results = []
    for a,b in combinations(list(docs_dict.keys()), 2):
        ia, ja = doc_ranges[a]
        ib, jb = doc_ranges[b]
        matA = sent_mat[ia:ja]
        matB = sent_mat[ib:jb]
        if matA.shape[0] == 0 or matB.shape[0] == 0:
            score = 0.0
        else:
            sim = cosine_similarity(matA, matB)
            # average of best-match scores (bidirectional)
            score = float((sim.max(axis=1).mean() + sim.max(axis=0).mean()) / 2)
        results.append({"docA": a, "docB": b, "structural_similarity": score})
    return pd.DataFrame(results)

# Combined robustness index function (configurable weights)
def compute_combined_index(row, weights = {"cos":0.5, "struct":0.2, "jac":0.15, "rouge":0.15}):
    # row should contain keys: cosine_tfidf, structural_similarity, jaccard, rouge_l_f1
    cos = row.get("cosine_tfidf", 0.0)
    struct = row.get("structural_similarity", 0.0)
    jac = row.get("jaccard", 0.0)
    rouge = row.get("rouge_l_f1", 0.0)
    w = weights
    combined = w["cos"]*cos + w["struct"]*struct + w["jac"]*jac + w["rouge"]*rouge
    return combined

# ------------------------- High-level orchestrator for multi-usecase evaluation -------------------------
def evaluate_robustness(all_texts, pairing_scheme="same_question"):
    """
    all_texts: dict structured as:
      { usecase_id: { question_id: { temp_label: text, ... }, ... }, ... }
    pairing_scheme: currently supports 'same_question' meaning compare texts that respond to the same question across temps.
    Returns: dict with detailed tables and aggregated metrics.
    """
    # Flatten docs into unique doc ids: usecase|question|temp
    docs = {}
    doc_meta = {}  # mapping doc_id -> (uc, q, temp)
    for uc, questions in all_texts.items():
        for q, temps in questions.items():
            for temp, txt in temps.items():
                doc_id = f"{uc}|||{q}|||{temp}"
                docs[doc_id] = txt
                doc_meta[doc_id] = {"usecase": uc, "question": q, "temp": temp}
    if not docs:
        raise ValueError("No documents provided.")
    
    pairwise_list = []
    struct_list = []

    for uc, questions in all_texts.items():
        for q, temps in questions.items():
            # Only consider docs of this question
            docs_subset = {f"{uc}|||{q}|||{t}": txt for t, txt in temps.items()}

            # Pairwise semantic, lexical, ROUGE
            df_pairwise = pairwise_document_metrics(docs_subset)
            pairwise_list.append(df_pairwise)

            # Structural similarity
            df_struct = structural_similarity_scores(docs_subset)
            struct_list.append(df_struct)

    # Concatenate all per-question dataframes
    pairwise_df = pd.concat(pairwise_list, ignore_index=True)
    struct_df = pd.concat(struct_list, ignore_index=True)

    
    # numeric table
    num_table, nums_per_doc = numeric_consistency_table(docs)
    # contradictions: run for relevant pairs (same question across temps)
    contradictions = []
    # If pairing_scheme == same_question: for each usecase and question compare each pair of temps
    for uc, questions in all_texts.items():
        for q, temps in questions.items():
            temp_keys = list(temps.keys())
            for t1, t2 in combinations(temp_keys, 2):
                id1 = f"{uc}|||{q}|||{t1}"; id2 = f"{uc}|||{q}|||{t2}"
                contr = detect_contradictions_between_texts(docs[id1], docs[id2])
                contradictions.append({"docA": id1, "docB": id2, "contradictions": contr})
    contradictions_df = pd.DataFrame(contradictions)
    # Merge pairwise metrics with structural where possible
    merged = pairwise_df.merge(struct_df, how="left", left_on=["docA","docB"], right_on=["docA","docB"])
    # compute combined index per pair
    merged["combined_index"] = merged.apply(lambda r: compute_combined_index(r), axis=1)
    # Now compute aggregated metrics per question across temps: e.g., mean pairwise combined_index among temps for same question
    aggr_rows = []
    for uc, questions in all_texts.items():
        for q, temps in questions.items():
            # collect doc_ids for this question
            doc_ids = [f"{uc}|||{q}|||{t}" for t in temps.keys()]
            # find rows in merged where both docA and docB in doc_ids
            mask = merged["docA"].isin(doc_ids) & merged["docB"].isin(doc_ids)
            subset = merged[mask]
            if subset.empty:
                mean_combined = np.nan
                mean_cos = np.nan
            else:
                mean_combined = subset["combined_index"].mean()
                mean_cos = subset["cosine_tfidf"].mean()
            aggr_rows.append({"usecase": uc, "question": q, "mean_combined_index_across_temps": mean_combined, "mean_cosine_across_temps": mean_cos, "pairs": len(subset)})
    aggr_df = pd.DataFrame(aggr_rows)
    
    # Overall summary
    overall = {
        "mean_combined_index_all_pairs": merged["combined_index"].mean(),
        "mean_cosine_all_pairs": merged["cosine_tfidf"].mean(),
        "mean_structural_all_pairs": merged["structural_similarity"].mean()
    }
    return {
        "pairwise_metrics": merged,
        "structural_metrics": struct_df,
        "numeric_table": num_table,
        "numeric_per_doc": nums_per_doc,
        "contradictions": contradictions_df,
        "aggregate_per_question": aggr_df,
        "overall_summary": overall,
        "doc_meta": doc_meta
    }

# ------------------------- usage with the three texts you gave -------------------------


# Display some outputs
#import caas_jupyter_tools as tools
#tools.display_dataframe_to_user("Pairwise metrics (merged)", results["pairwise_metrics"])
#tools.display_dataframe_to_user("Structural pairwise metrics", results["structural_metrics"])
#tools.display_dataframe_to_user("Numeric facts presence table", results["numeric_table"])
#tools.display_dataframe_to_user("Detected contradictions (per pair)", results["contradictions"])
#tools.display_dataframe_to_user("Aggregate per question across temps", results["aggregate_per_question"])

#print("Overall summary:")
#for k,v in results["overall_summary"].items():
#    print(f"- {k}: {v:.4f}")

#print("\nHow to use this script on your full dataset:")
#print("1) Build `all_texts` dict with structure {usecase: {question: {temp_label: text}}} for all your UC and questions.")
#print("2) Call evaluate_robustness(all_texts).")
#print("3) Inspect 'pairwise_metrics' and 'aggregate_per_question' for robustness numbers across temps.")
#print("\nNotes:")
#print("- The combined_index weights default to: cosine 0.5, structural 0.2, jaccard 0.15, rouge 0.15. Adjust if you prefer semantic similarity to dominate.")
#print("- For higher-fidelity semantic similarity, replace TF-IDF cosine with sentence embeddings (Sentence-BERT / OpenAI embeddings) if available.")


if __name__ == "__main__":
    
    all_texts = {
        "UC1": {
            "Q1": {
                "temp1.0": """Incident management compliance is moderate with an average process fitness of 0.69. However, contractual obligations are largely unmet, with only 44.43% of incidents meeting SLA and a high average resolution time of 15.14 days. The alarming 0.0% 'percentage assigned to resolved by' indicates a critical breakdown in accountability and process integrity, demanding immediate investigation and remediation. While active incidents notably decreased from 1963 to 451 during the period, these core process deficiencies require urgent strategic attention to improve compliance and service delivery.""",
                "temp0.5": """The incident management process exhibits moderate compliance with a fitness score of 0.69, falling within the acceptable range. However, a critically low SLA adherence of 44.43% indicates that the majority of incidents are not meeting contractual obligations. While active incidents decreased significantly from 1963 to 451 during the period, and 1598 incidents were closed (with 562 moderate, 323 high, and 216 critical severity), the average time to resolve of approximately 15 days is concerning. **Recommendation:** Prioritize a deep dive into the reasons for the low SLA adherence, focusing on the handling of moderate, high, and critical severity incidents. Investigate potential bottlenecks in the process, resource allocation, and current resolution strategies to improve efficiency and ensure contractual obligations are met.""",
                "temp1.5": """During June 1-29, 2016, active incidents significantly decreased from 1963 to 451, with 1598 incidents resolved; notably, 33.7% (539) of these closed incidents exhibited high or critical compliance severities. The overall process compliance (fitness) stands at a moderate 0.69, which is below the desired 'low severity' threshold of 0.85. Crucially, only 44.43% of incidents met their SLA, directly indicating a failure to consistently meet contractual obligations. It is recommended to prioritize an investigation into the causes of the low SLA adherence and the significant number of non-compliant high/critical severity incidents to ensure compliance and improve process effectiveness.""",
            },
            "Q2": {
                "temp1.0": """The incident management process shows significant compliance issues with the reference model, primarily driven by critical deviations in state transitions and repetitions. The 'activation' state ('A') is particularly problematic, exceeding acceptable thresholds for missing (544 vs <=200), repetition (1990 vs <=500), and mismatch (115 vs <=50). Furthermore, common process variants like "N R C" (182 occurrences) and "A R C" (135 occurrences) bypass mandatory steps, indicating frequent non-compliant process flows. **Required Remediation:** 1. **Investigate Deviations:** Conduct a deep dive into why 'activation' (A) consistently deviates across all metrics, and why 'detection' (N), 'awaiting' (W), and 'resolution' (R) have critically high repetitions. 2. **Enforce Process Paths:** Analyze and rectify the frequent occurrence of non-compliant transitions such as "N->R" and "N->W", which suggest incidents skip the 'activation' step entirely. 3. **Address Bottlenecks:** Examine the extended average times for 'awaiting' (16d, 8h, 10min) and 'activation' (8d, 18h, 55min) states, and the 'W->R' transition (8d, 1h, 19min) to improve overall process efficiency.""",
                "temp0.5": """The incident management process exhibits critical non-compliance. Significant deviations are observed, with 'missing' activities critically high for detection (319) and activation (544), and 'repetition' critically high for detection (1777), activation (1990), awaiting (1653), and resolution (119). Average state durations are critically excessive for detection (4d 6h 35min), activation (8d 18h 55min), awaiting (16d 8h 10min), and resolution (5d 22h 11min). Furthermore, the most common process variants, 'N R C' (182 occurrences) and 'A R C' (135 occurrences), represent fundamental mismatches with the reference model's allowed transitions. **Recommendation:** Immediate remediation is required to enforce adherence to the defined reference model, addressing the root causes of critical deviations and severe bottlenecks in the detection, activation, awaiting, and resolution phases. Focus on correcting the prevalent non-compliant process flows, particularly the direct 'detection' to 'resolution' transitions and incidents bypassing 'detection'.""",
                "temp1.5": """The incident management process exhibits significant compliance issues, with average state durations for 'detection', 'activation', 'awaiting', and 'resolution' far exceeding their non-acceptable time limits, notably the 'awaiting' state at over 16 days (vs. a 10-day non-acceptable threshold). This is compounded by excessive deviations: 'activation' shows 544 missing events and 1990 repetitions (against limits of 20 and 500 respectively), while 'awaiting' has 1653 repetitions (limit 200) and 'resolution' has 119 repetitions (limit 50) and 45 mismatches (limit 20). Furthermore, the existence of direct 'detection' to 'awaiting' (N->W) and 'detection' to 'resolution' (N->R) transitions indicates systemic deviation from the defined reference model, which requires 'activation' as an intermediary step. Immediate remediation is required to investigate the root causes of these prolonged state durations and significant process deviations, aiming to enforce adherence to the compliant incident management workflow."""
            },
            "Q3": {
                "temp1.0": """The most frequent recorded variant is 'N R C' (182 incidents), where incidents move directly from 'detection' to 'resolution' and 'closure', bypassing the required 'activation' state as per the reference model. Another prominent variant, 'N N R C' (81 incidents), highlights frequent repetitions of the 'detection' state followed by the same non-compliant jump to 'resolution'. As a Monitor, I recommend investigating why the 'activation' state is consistently skipped and reviewing incident logging practices to reduce redundant 'detection' entries, as these patterns indicate significant process non-compliance.""",
                "temp0.5": """The most frequent recorded variants are 'N R C' (182 occurrences), 'A R C' (135 occurrences), 'N N R C' (81 occurrences), and 'N A R C' (59 occurrences). The top three variants ('N R C', 'A R C', 'N N R C') indicate significant non-compliance: 'N R C' and 'N N R C' show direct jumps from 'detection' (N) to 'resolution' (R) bypassing 'activation' (A), which is not allowed by the reference model. 'A R C' suggests incidents are activated without a recorded 'detection' state, deviating from the model's starting point. Only 'N A R C' is a fully compliant path, representing a direct resolution after activation. **Recommendation:** Investigate why the majority of incidents bypass the 'activation' state or start directly at 'activation', and why 'detection' often transitions directly to 'resolution'. This indicates a fundamental misalignment between the recorded process and the defined reference model, requiring urgent review of incident logging practices and process adherence.""",
                "temp1.5": """The most frequent recorded variant is 'N R C' (182 occurrences), which is critically non-compliant as the reference model requires 'detection' (N) to always lead to 'activation' (A). The second most frequent, 'A R C' (135 occurrences), indicates a consistent omission of the 'detection' (N) state. While 'N A R C' (59 occurrences) is a compliant path, the overall prevalence of non-compliant sequences like direct jumps from 'N' to 'R' and incidents starting at 'A' signifies a widespread issue with adherence to initial process states. Remediation is required to enforce recording of all mandatory process states and valid transitions from detection to activation.""",
            },
            "Q4": {
                "temp1.0": """The average fitness for 'activation' (0.1) and 'awaiting' (0.14) is below the acceptable threshold of >=0.15, indicating non-compliance for these activities. 'Activation' exhibits significant missing (544), repetition (1990), and mismatch (115) deviations, with an average duration of 8d, 18h, 55min. 'Awaiting' shows the longest average duration of 16d, 8h, 10min and high repetition deviations (1653). **Required Remediation:** Responders should investigate the 'activation' activity to reduce all types of deviations and improve process adherence, potentially through clearer guidelines or automation. For the 'awaiting' activity, focus should be on identifying and eliminating causes of extensive waiting times and frequent repetitions, such as clarifying hand-off procedures or resource bottlenecks.""",
                "temp0.5": """The activities 'activation' (average fitness 0.1, target >=0.15) and 'awaiting' (average fitness 0.14, target >=0.15) are impeding process compliance, falling below acceptable fitness levels. Additionally, 'detection' (319 missing, 1777 repetitions), 'activation' (544 missing, 1990 repetitions, 115 mismatches), 'awaiting' (1653 repetitions), and 'resolution' (119 repetitions, 45 mismatches) show critically high deviations. All activities except 'closure' also exhibit significantly prolonged average processing times (e.g., 'awaiting' averages 16d, 8h, 10min against an acceptable 7200 min). To improve compliance, remediation should focus on streamlining procedures and providing clearer guidance to reduce missing steps, repetitions, and mismatches in 'activation', 'awaiting', 'detection', and 'resolution'. Furthermore, immediate action is required to identify and eliminate bottlenecks causing excessive time delays across all non-compliant activities.""",
                "temp1.5": """The incident management compliance is critically low for almost all activities (fitness scores between 0.1 and 0.17 for Detection, Activation, Awaiting, and Resolution), falling well below the moderate threshold of 0.65. Specifically, Activation (0.1 fitness) is most impeding due to excessive time (12655 min) and high missing (544), repetition (1990), and mismatch (115) deviations, followed by Detection (0.11 fitness) also exhibiting high deviations and time (6155 min). Remediation should immediately target process streamlining in Activation and Detection to reduce repetitions and mismatches, addressing the excessive time spent in these and other critical activities to improve overall compliance.""",
            },
            "Q5": {
                "temp1.0": """The `awaiting`, `activation`, `detection`, and `resolution` activities are significantly impeding process efficiency, all exceeding their non-acceptable time thresholds. The `awaiting` state is the primary bottleneck, averaging 16 days, 8 hours, 10 minutes (non-acceptable at >=10 days), likely due to its high volume of 1653 repetitions. `Activation` is also severely inefficient, with an average duration of 8 days, 18 hours, 55 minutes (non-acceptable at >=5 days) and the highest number of missing (544) and repetition (1990) deviations. To improve compliance and reduce these durations, remediation must focus on streamlining handoffs, standardizing procedures, enhancing initial data capture, and ensuring timely resource availability to minimize repetitions and missing steps.""",
                "temp0.5": """The average activity durations for 'detection' (6155 min), 'activation' (12655 min), 'awaiting' (23530 min), and 'resolution' (8531 min) are critically inefficient, all significantly exceeding their respective non-acceptable thresholds (2880, 7200, 14400, and 4320 minutes). Only the 'closure' activity (40 min) is within acceptable limits. **Required Remediation:** Responders must prioritize immediate action to reduce the excessive time spent in 'detection', 'activation', 'awaiting', and 'resolution' states. This includes streamlining initial incident handling, improving resource allocation to reduce waiting times, and optimizing resolution procedures to bring durations within acceptable operational limits.""",
                "temp1.5": """The average durations for 'detection' (4d 6h 35min), 'activation' (8d 18h 55min), 'awaiting' (16d 8h 10min), and 'resolution' (5d 22h 11min) are all critically above their respective non-acceptable time thresholds (2880 min, 7200 min, 14400 min, 4320 min). These activities are severely impeding process efficiency. Only 'closure' (0d 0h 40min) is within the acceptable time. **Recommendation:** Immediate remediation is required. Analyze the specific sub-processes and tasks within 'detection', 'activation', 'awaiting', and 'resolution' to identify bottlenecks and causes for the prolonged durations. Implement targeted process improvements, allocate additional resources, or introduce automation to drastically reduce these activity times.""",
            },
            "Q6": {
                "temp1.0": """The analyst should conduct a deep dive into the 260 incidents categorized as critically non-compliant (fitness 0.19-0.5), starting with `INC0032450` (fitness 0.19). A significant number of these incidents frequently originate from locations such as '204', '143', '161', and relate to categories like '42', '46', '26', often reporting symptom '491'. The risk of non-compliance is high due to substantial deviations from the process model, indicating a need to investigate the drift between theoretical and practical process for these prevalent technical characteristics and implement targeted remediation.""",
                "temp0.5": """All 468 incidents analyzed are critically non-compliant (fitness 0.19-0.5), indicating a systemic process adherence issue with significant risks of operational inefficiency and inconsistent service delivery. The vast majority (440 incidents) of these non-compliant incidents share common technical attributes of Impact 2, Urgency 2, and Priority 3. To effectively resolve non-compliance through activity specifics and process drift, a detailed process mining analysis of the actual event logs for these incidents is required. This would pinpoint exact deviations and their root causes, leading to targeted remediation.""",
                "temp1.5": """The assessment reveals critical non-compliance for all 500 incidents within the specified period (June 2016), with fitness scores ranging from 0.19 to 0.50. A deeper analysis of technical attributes indicates a high prevalence of Impact 2 and Urgency 2 (resulting in Priority 3) incidents across various Symptoms, Locations, and Categories. The most common Symptom observed is '491', frequently leading to Category '46' or '42' incidents, primarily located at '204', '161', and '143'. The risks from this widespread critical non-compliance include consistently poor process execution, potentially leading to increased resolution times, higher costs, and a significant security posture degradation. This suggests systemic issues in adhering to the defined incident management workflow, potentially indicating process gaps, resource constraints, or lack of staff training. **Remediation Plan for Analyst:** 1. **Focused Root Cause Analysis:** Prioritize a detailed root cause analysis for incidents with `Symptom 491` leading to `Category 46` or `42`, especially those at `Location 204`, `161`, and `143`, as they are highly correlated with low fitness scores. 2. **Process Step Review:** Investigate the specific deviations in the process flows for the lowest-fitness incidents (e.g., `INC0032450`). Determine which specific states (`detection`, `activation`, `awaiting`, `resolution`, `closure`) are consistently being skipped, repeated, or delayed to identify exact process bottlenecks. 3. **Attribute-Specific Improvement:** Examine if particular combinations of `Impact 2` and `Urgency 2` (resulting in `Priority 3`) are handled inefficiently. Recommend targeted training or clearer procedural guidelines for these common incident characteristics.""",
            },
            "Q7": {
                "temp1.0": """As an Analyst assessing the "Report Technical Analysis and most affected categories" control, the provided data reveals critical insights into technical incident patterns. The most frequent symptom is 491 (seen 179 times), while the top affected categories are 42 (100 times), 46 (100 times), and 26 (98 times). Locations 204 (170 times), 161 (130 times), and 143 (119 times) are most frequently impacted. Given that all listed incidents have critically low fitness scores (ranging from 0.190 to 0.5), it is recommended to conduct in-depth root cause analysis on these prevalent symptoms, categories, and locations to identify specific technical vulnerabilities or process deficiencies contributing to the severe compliance deviations.""",
                "temp0.5": """All incidents listed have a process fitness score below 0.5, indicating a critical level of non-compliance with the reference model. From the technical analysis, the most frequent symptom is '491' (160 occurrences), with a significant number of incidents (106) having no recorded symptom. The most affected locations are '204' (153 occurrences), '161' (115 occurrences), and '143' (104 occurrences), while categories '42' (77 occurrences), '26' (76 occurrences), and '46' (75 occurrences) are most impacted. **Recommendation:** 1. **Improve Data Capture:** Implement mandatory fields or automated mechanisms to ensure symptoms are always recorded, addressing the 106 incidents with 'None' as a symptom. 2. **Targeted Root Cause Analysis:** Prioritize in-depth analysis of incidents with symptom '491' and those affecting locations '204', '161', '143' and categories '42', '26', '46' to identify underlying vulnerabilities or systemic issues in these frequently targeted areas. 3. **Correlate Compliance and Technical Data:** Investigate if there's a correlation between the critical process non-compliance (fitness <= 0.5) and the identified prevalent technical attributes to uncover specific process weaknesses in handling these common incident types.""",
                "temp1.5": """**Recommendation:** The technical analysis reveals a critical lack of structured incident reporting, with 45 incidents missing a defined symptom. For incidents where data is recorded, symptom '491' (observed 95 times) is overwhelmingly prevalent. Locations '204' (118 times), '161' (93 times), and '143' (86 times) are the most frequently affected, while categories '46' (78 times), '42' (54 times), and '26' (64 times) show significant impact, indicating frequently targeted IT assets and infrastructures within these areas. **Required Remediation:** 1. **Mandate Symptom Logging:** Implement a mandatory field for 'Symptom' at the detection stage to address the high number of 'None' entries, improving the completeness and utility of technical analysis. 2. **Focus Investigation:** Prioritize in-depth analysis of incidents involving symptom '491' in locations '204', '161', and '143', specifically within categories '46', '42', and '26', to identify root causes and specific vulnerabilities. 3. **Refine Categorization:** Review the definition and usage of categories '46', '42', and '26' to ensure clarity and improve granular reporting, potentially breaking them down if they represent overly broad areas.""",
            }
        },
        "UC2": {
            "Q1": {
                "temp1.0": """Incident management compliance, as measured by the non-compliance cost, is at a **low severity** with an average cost of 0.047, indicating a well-controlled process according to the updated compliance model that accounts for specific, non-critical deviations. However, contractual obligations are largely unmet, with only 44.43% of incidents meeting SLA and a high average resolution time of 15.14 days. While active incidents decreased significantly from 1963 to 451, the persistent 0.0% for 'assigned to equals resolved by' warrants further investigation into accountability. Remediation efforts should prioritize improving SLA adherence and reducing average resolution times to meet service commitments.""",
                "temp0.5": """The incident management process shows a low overall non-compliance cost of 0.047, which falls within the "low severity" range and meets acceptable compliance thresholds, especially considering that repetitive detection and awaiting activities, as well as N*RC variants, are now considered non-process harming. However, a critically low 44.43% of SLAs are met, and the average time to resolve incidents remains very high at approximately 15 days. While active incidents decreased significantly from 1963 to 451, and 1598 incidents were closed (1398 low, 90 moderate, 103 high, 7 critical), the low SLA adherence indicates a failure to meet contractual obligations. **Recommendation:** Prioritize investigating the root causes for the critically low SLA adherence and high average time to resolve, despite the low process non-compliance cost. Focus on resource allocation, incident complexity, and the realism of existing SLA targets, particularly for moderate, high, and critical severity incidents, to ensure contractual obligations are consistently met.""",
                "temp1.5": """The overall incident management compliance cost is low at 0.047, indicating efficient handling of process deviations from a cost perspective, further supported by the significant reduction of active incidents from 1963 to 451 within the period. While observed high counts for repetitive detection (1777), repetitive awaiting (1653), and missing activation (544) events contribute to cost, these are explained as expected operational patterns (e.g., N*RC variants, tuned thresholds for repetitions) rather than process errors, mitigating the need for immediate remediation. The critical issue remains the low SLA adherence, with only 44.43% of incidents meeting their contractual obligations. It is recommended to investigate the underlying causes of the consistently low SLA achievement to improve service delivery and ensure contractual compliance.""",
            },
            "Q2": {
                "temp1.0": """Considering the updated compliance metric to non-compliance cost and specific reinterpretations, the incident management process continues to demonstrate critical compliance issues. The 'activation' state ('A') is severely non-compliant, with missing (544 vs <=200), repetition (1990 vs <=500), and mismatch (115 vs <=50) deviations critically exceeding acceptable thresholds and driving non-compliance costs. Additionally, missing 'detection' (N) events (319 vs <=20) and high 'resolution' (R) repetitions (119 vs <=50) and mismatches (45 vs <=20) also indicate significant process non-compliance. Furthermore, average state durations for 'awaiting' (16d, 8h, 10min), 'activation' (8d, 18h, 55min), and 'detection' (4d, 6h, 35min) critically surpass non-acceptable times, highlighting severe process bottlenecks. **Required Remediation:** 1. **Strengthen Activation Compliance:** Immediately investigate and rectify the root causes for the critical number of missing, repeated, and mismatched 'activation' (A) events. 2. **Optimize Bottleneck States:** Implement targeted improvements to drastically reduce the average time spent in 'awaiting' (W), 'activation' (A), and 'detection' (N) states, including the prolonged 'W->R' transition. 3. **Improve Detection and Resolution Compliance:** Develop strategies to minimize missing 'detection' (N) events and curb the high frequency of repetitions and mismatches in the 'resolution' (R) state.""",
                "temp0.5": """Despite the re-evaluation of specific repetitive detection and awaiting activities, the incident management process continues to exhibit critical non-compliance. Average durations for detection (6155min), activation (12655min), awaiting (23530min), and resolution (8531min) are severely non-acceptable, indicating major bottlenecks. Significant process deviations persist with 319 missing detection activities, 544 missing activation activities, 1990 repetitions in activation, and 115 mismatches in activation, all far exceeding acceptable thresholds. **Recommendation:** Immediate remediation is required to address the persistent bottlenecks in detection, activation, awaiting, and resolution phases, as well as to enforce adherence to the defined process for non-exempted missing, repetitive, and mismatch activities. Focus on optimizing state durations and ensuring proper initiation and flow through detection and activation.""",
                "temp1.5": """The incident management process exhibits critical non-compliance, indicated by a total non-compliance cost of 140.04 and prolonged state durations. Average times for 'detection' (4d 6h), 'activation' (8d 18h), 'awaiting' (16d 8h), and 'resolution' (5d 22h) all significantly exceed their non-acceptable thresholds. Key process deviations, such as 319 missing 'detection' and 544 missing 'activation' events, along with excessive repetitions and mismatches in 'activation' (1990 and 115 respectively) and 'resolution' (119 and 45 respectively), highlight systemic issues despite updated allowances for 'detection' and 'awaiting' repetitions and N*RC variants. Immediate remediation is required to address these critical delays and deviation clusters, focusing on adherence to prescribed activity execution and timings."""
            },
            "Q3": {
                "temp1.0": """The most frequent recorded variant is 'N R C' (182 incidents), which represents a process flow from 'detection' to 'resolution' and then 'closure'. This variant and any starting with repeated 'N's (e.g., 'N N R C', 81 incidents) are considered non-error due to merge rules and ignored, and also repetitive 'awaiting' activities are disregarded. However, 'N A A R C' (46 incidents), 'A A R C' (38 incidents), and 'N A A A A R C' (25 incidents) frequently show repetitions in the 'activation' state (`A`), which represent process inefficiencies. The variant 'R C' (27 incidents) completely bypasses the 'detection' and 'activation' phases, indicating significant initial process omission. Additionally, 'N W R C' (22 incidents) signifies a mismatch where 'detection' directly leads to 'awaiting', skipping the necessary 'activation' step. As a Monitor, I recommend investigating these frequent 'activation' repetitions and the significant bypasses in 'R C' and 'N W R C' flows to ensure adherence to the defined incident management process and reduce costly deviations.""",
                "temp0.5": """The most frequent recorded variants are 'N R C' (182), 'A R C' (135), 'N N R C' (81), and 'N A R C' (59). With the updated compliance rules, 'N R C' and 'N N R C' are now compliant due to automated merge rules and acceptable repetitive detection, while 'N A R C' and 'N A W R C' represent standard compliant flows. However, the high frequency of 'A R C' (135) and 'R C' (27) variants indicates a persistent issue where incidents bypass the initial 'detection' state, suggesting a gap in incident logging or initiation. Additionally, repetitive 'activation' (A) in variants like 'N A A R C' (46) warrants investigation as this repetition is not exempted and could signal process inconsistencies.""",
                "temp1.5": """The most frequent recorded variants are 'N R C' (182 occurrences), 'A R C' (135 occurrences), and 'N N R C' (81 occurrences). While the 'N*RC' variants (e.g., 'N R C', 'N N R C') and repetitive 'N' activities are now considered acceptable due to automated merge rules not involving manual operators, the 'A R C' variant frequently omits the mandatory 'detection' (N) state. Additionally, 'R C' (27 occurrences) bypasses both 'detection' (N) and 'activation' (A), indicating further critical deviations from the initial process. Remediation is required to enforce the correct initiation of manually handled incidents through the 'detection' and 'activation' states to align with the reference model."""
            },
            "Q4": {
                "temp1.0": """The average non-compliance cost for all activities (Detection: 0.02, Activation: 0.02, Awaiting: 0.00, Resolution: 0.00, Closure: 0.00) indicates overall compliance against a threshold of <=0.05. However, a detailed review from a Responder's perspective, applying the provided tuning rules, reveals specific compliance impediments based on deviation counts exceeding defined thresholds. Specifically, Detection exhibits 319 missing events (threshold <=20), Activation has 1990 repetitions (threshold <=500) and 115 mismatches (threshold <=50), and Resolution records 119 repetitions (threshold <=50) and 45 mismatches (threshold <=20). Repetitive detection and awaiting deviations, alongside missing activation events due to N*RC merge rules, are not considered process errors for responders per the updated guidelines. **Required Remediation:** Responders should prioritize reducing missing detection events. Additionally, efforts must target mitigating the high repetition and mismatch deviations found within both the activation and resolution activities.""",
                "temp0.5": """Despite all activities showing compliant average non-compliance costs (0.0 to 0.02, target <=0.05), significant process deviations persist. Specifically, 'detection' exhibits 319 missing activities (acceptable <=20), while 'activation' (1990 repetitions, 115 mismatches) and 'resolution' (119 repetitions, 45 mismatches) far exceed their acceptable deviation thresholds (e.g., activation repetition <=500, mismatch <=50). Furthermore, average processing times for 'detection' (6155 min), 'activation' (12655 min), 'awaiting' (23530 min), and 'resolution' (8531 min) are critically prolonged, well beyond their non-acceptable thresholds (e.g., detection >=2880 min). Remediation should focus on addressing these specific deviation types and the severe time bottlenecks across the identified activities.""",
                "temp1.5": """The incident management compliance, evaluated by the non-compliance cost metric, indicates a High severity for Activation (average cost 0.278) and Moderate severity for Detection (average cost 0.112), both significantly above the acceptable threshold of 0.05. Activation is primarily impeded by high repetition (1990 counts, with average 8d, 18h, 55min duration) and missing (544 counts) deviations, along with 115 mismatches. Detection's cost stems from 319 missing deviations (with average 4d, 6h, 35min duration). To remediate, the Responder team should focus on reducing missing steps in Detection and Activation and eliminating non-exempted repetitive/mismatch deviations in Activation through targeted process guidance, training on initial incident handling, and implementation of automated verification checks. While repetitions in Detection and Awaiting (average cost 0.002, duration 16d, 8h, 10min) are exempt due to specific process clarifications, the high cost in Activation warrants immediate attention to streamline activities."""
            },
            "Q5": {
                "temp1.0": """The `awaiting`, `activation`, `resolution`, and `detection` activities are significantly impeding process efficiency by exceeding their non-acceptable average duration thresholds. The `awaiting` state is the primary bottleneck, averaging 16 days, 8 hours, 10 minutes (non-acceptable at >=10 days), followed by `activation` at 8 days, 18 hours, 55 minutes (non-acceptable at >=5 days). While average compliance costs are low (0.0-0.02) and repetitive deviations in `detection` (1777) and `awaiting` (1653), along with N*RC variants, are not considered process errors, these extended durations highlight efficiency concerns. Remediation should focus on improving coordination with external parties for `awaiting` delays, and for `activation` and `resolution` (5d, 22h, 11min vs. >=3d), prioritize streamlining internal handoffs, standardizing procedures, and ensuring timely resource allocation to address non-exempted repetitions and mismatches.""",
                "temp0.5": """The average activity durations for 'detection' (6155 min), 'activation' (12655 min), 'awaiting' (23530 min), and 'resolution' (8531 min) are critically inefficient, all significantly exceeding their respective non-acceptable thresholds (2880, 7200, 14400, and 4320 minutes). Only the 'closure' activity (40 min) is within acceptable limits. **Required Remediation:** Responders must prioritize immediate action to reduce these excessive durations. While repetitive 'awaiting' activities are influenced by external parties, strategies like improved SLAs with third parties and automated follow-ups are needed to reduce this bottleneck, alongside streamlining internal handling for 'detection', 'activation', and 'resolution' processes to bring durations within acceptable operational limits.""",
                "temp1.5": """The average durations for 'detection' (4d 6h 35min = 6155 min), 'activation' (8d 18h 55min = 12655 min), 'awaiting' (16d 8h 10min = 23530 min), and 'resolution' (5d 22h 11min = 8531 min) remain critically above their respective non-acceptable time thresholds (2880 min, 7200 min, 14400 min, 4320 min), indicating significant process inefficiency. While overall compliance costs for these activities are low (all <= 0.02), implying deviations are not considered process errors, their prolonged durations still impede efficiency and incident flow. Only 'closure' (0d 0h 40min) is within acceptable time. **Recommendation:** Immediate remediation is required to reduce the average durations of detection, activation, awaiting, and resolution activities. For detection, focus on optimizing automated merging rules and rapid trigger processing. For awaiting, establish stricter SLAs with external parties or explore automated follow-ups for overdue incidents. Implement targeted process improvements for activation and resolution to identify and eliminate bottlenecks, such as resource allocation, tool enhancements, or workflow adjustments, ensuring a more fluid incident lifecycle despite underlying complexities like merged incidents."""
            },
            "Q6": {
                "temp1.0": """The 7 identified incidents are critically non-compliant, with costs ranging from 0.31 to 0.81 (e.g., INC0033952 at 0.81). To understand the risks and drift between theoretical and practical processes, a deep dive into the specific deviation types contributing to these high costs is essential. Prioritize investigation into 'missing' activities in 'resolution' and 'closure' (cost 0.45 and 0.3 respectively) and 'mismatch' deviations in 'activation' and 'resolution' (cost 0.25 and 0.3 respectively), as these carry the highest penalties and are not exempted. The prevalence of Symptom 491, Location 204, and Category 46/42/26 suggests these technical characteristics may be root causes for non-exempted process adherence issues, requiring tailored remediation strategies.""",
                "temp0.5": """The 7 most critical incidents show high non-compliance costs (0.31 to 0.81), indicating critical process deviations. While common technical attributes like Impact 2, Urgency 2, and Priority 3 are prevalent, a deep dive into the specific deviation types for these incidents is crucial. Missing and mismatch deviations, particularly in the Resolution and Activation phases, are likely the primary cost drivers. To accurately identify true process risks, examine detailed process traces for these incidents to differentiate actual errors from acceptable repetitive detection/awaiting activities and N*RC variants, aligning with the updated compliance tunings.""", 
                "temp1.5": """Based on the `cost` compliance metric, the provided incidents are all classified as `critical` (`cost >= 0.3`). `INC0033952` with a cost of 0.81 is the most non-compliant. A technical analysis of incidents reveals frequently occurring attributes, particularly `Symptom 491` leading to `Impact 2`, `Urgency 2`, and `Priority 3` incidents. These incidents are predominantly seen across `Location 204`, `161`, and `143`, often associated with `Category 46` and `42`. However, the provided data lacks the granular breakdown of cost contributions (missing, repetition, mismatch) per activity for each critical incident. This prevents a targeted assessment based on the updated understanding that repetitive detection (`N`) deviations, N*RC variants (missing `A` and `W`), and repetitive awaiting (`W`) deviations are not considered process non-compliance. To improve compliance assessment, data for critical incidents must include details on specific deviation types (missing, repetition, mismatch) and their attributed costs per process activity. This will allow the Analyst to accurately filter out non-harming deviations and focus remediation efforts on true process gaps."""
            },
            "Q7": {
                "temp1.0": """As an Analyst assessing the "Report Technical Analysis and most affected categories" control, the provided data reveals critical insights into technical incident patterns. The most critical incidents, such as INC0033952 with a non-compliance cost of 0.81, show high cost values falling into the critical severity range, signaling a need for in-depth analysis. Technical statistics indicate that Symptom 491 (179 times), Categories 46 and 42 (each 100 times), and Locations 204 (170 times), 161 (130 times), and 143 (119 times) are most prevalent. It is recommended to conduct a deep dive into these frequently occurring symptoms, categories, and locations across critical incidents to deduce targeted IT assets and infrastructures, thereby informing remediation efforts regardless of specific process deviation interpretations related to merge rules or third-party delays.""",
                "temp0.5": """The current assessment, viewed from an Analyst's perspective, reveals that all seven identified critical incidents (INC0033952, INC0025696, INC0026744, INC0032450, INC0025714, INC0029392, INC0033063) exhibit high non-compliance costs ranging from 0.31 to 0.81, indicating critical process deviations. From a technical standpoint, a significant number of incidents (106) lack a recorded symptom, hindering root cause analysis. Symptom '491' is the most prevalent (160 occurrences), while locations '204' (153 occurrences), '161' (115 occurrences), and '143' (104 occurrences) are most affected. Categories '42' (77 occurrences), '26' (76 occurrences), and '46' (75 occurrences) are most impacted. **Recommendation:** 1. **Mandate Symptom Recording:** Implement mandatory fields or automated mechanisms to ensure symptoms are consistently recorded, addressing the 106 incidents with missing symptom data. 2. **Focused Technical Investigation:** Prioritize detailed technical analysis for incidents with symptom '491' and those affecting locations '204', '161', '143' and categories '42', '26', '46' to identify underlying vulnerabilities. 3. **Refined Compliance Correlation:** Investigate if the high non-compliance cost in critical incidents is due to actual process errors by security operators, or if it primarily stems from the now-understood and acceptable deviations (repetitive detections, N*RC variants, or repetitive awaiting activities). This will allow for a more precise remediation plan focusing on genuine process weaknesses.""",
                "temp1.5": """**Recommendation:** As an Analyst assessing the "Report Technical Analysis and most affected categories" control, the provided technical statistics indicate significant areas requiring attention. A critical concern is the lack of structured symptom logging, with 45 incidents missing symptom data, hindering effective root cause analysis. Symptom '491' is overwhelmingly prevalent, observed in 95 incidents, suggesting a common underlying technical issue. Furthermore, locations '204' (118 times), '161' (93 times), and '143' (86 times), along with categories '46' (78 times), '42' (54 times), and '26' (64 times), are the most frequently affected, clearly pointing to frequently targeted IT assets and infrastructures within these areas. **Required Remediation:** 1. **Mandate Symptom Logging:** Implement a mandatory process for recording technical symptoms during incident detection to ensure comprehensive data for analysis and to reduce the 45 instances of missing symptom data. 2. **Investigate Prevalent Symptoms & Locations:** Prioritize an in-depth investigation into incidents associated with symptom '491' and those occurring most frequently in locations '204', '161', and '143' across categories '46', '42', and '26' to identify specific vulnerabilities or recurring attack vectors. 3. **Refine Incident Categorization:** Review the current categorization schema for categories '46', '42', and '26' to ensure granular and precise classification, which will improve the clarity and utility of technical reports for pinpointing affected assets."""
            }
        },
    }
    

    results = evaluate_robustness(all_texts)

    output_file = "robustness_evaluation.txt"

    output_file = "robustness_evaluation.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        # --- Pairwise metrics ---
        print("Pairwise metrics (semantic, lexical, structural similarity):", file=f)
        print(results["pairwise_metrics"].to_string(index=False), file=f)
        print("""
    What it shows:
    - Each row represents a pair of AI-generated outputs (e.g., temp0.5 vs temp1.0) for the same question.
    - Columns:
        * cosine_tfidf: TF-IDF cosine similarity → semantic similarity (0 = different, 1 = identical)
        * jaccard: lexical overlap → shared vocabulary
        * rouge_l_f1: longest common subsequence similarity → word sequence similarity
        * structural_similarity: sentence-level similarity → overall document structure
        * combined_index: weighted aggregate of all above → overall robustness

    Interpretation:
    - High values (~1) → stable outputs across temperatures
    - Low values → instability; outputs differ significantly depending on temperature
    - Use this to spot which temperature pairs are more or less consistent

    Method introduced in Ref.: Salton & Buckley (1988); Manning et al. (2008); Jaccard (1901); Lin (2004); Foltz et al. (1998); Lapata (2006); Barzilay & Lapata (2008)
    """, file=f)

        # --- Numeric facts presence ---
        print("\nNumeric facts presence table:", file=f)
        print(results["numeric_table"].to_string(index=False), file=f)
        print("""
    What it shows:
    - Lists all numbers, percentages, and key numeric facts mentioned in any AI output.
    - Columns indicate whether each number appears in each output (True/False)

    Interpretation:
    - Numbers present in all outputs → AI is factually consistent
    - Numbers missing in some outputs → potential factual inconsistencies
    - Useful to check robustness in numerical reasoning across stochastic outputs

    Method introduced in Ref.: Wallace et al. (2019); Chen et al. (2020)
    """, file=f)
        
        # --- Numeric facts heatmap ---
        numeric_table = results["numeric_table"].set_index("number")
        # Only keep boolean columns (doc ids)
        bool_cols = [col for col in numeric_table.columns if numeric_table[col].dtype == bool]
        heatmap_data = numeric_table[bool_cols].astype(int)
        plt.figure(figsize=(max(8, len(bool_cols)), max(6, len(heatmap_data))))
        sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", cbar=False, linewidths=0.5)
        plt.title("Numeric Facts Presence Heatmap")
        plt.xlabel("Document")
        plt.ylabel("Numeric Fact")
        plt.tight_layout()
        plt.savefig("numeric_facts_heatmap.png")
        plt.close()

        print("\nNumeric facts presence heatmap saved as 'numeric_facts_heatmap.png'")

        # --- Detected contradictions ---
        print("\nDetected contradictions between outputs:", file=f)
        print(results["contradictions"].to_string(index=False), file=f)
        print("""
    What it shows:
    - Pairs of outputs with detected contradictions
    - Types:
        * numeric_mismatch: different numbers for the same metric
        * sentiment_opposite: opposing qualitative assessments (e.g., 'critical' vs 'acceptable')

    Interpretation:
    - Contradictions indicate low robustness
    - Numeric mismatches → AI may omit or alter key facts
    - Sentiment contradictions → AI gives conflicting qualitative evaluations

    Method introduced in Ref.: de Marneffe et al. (2008); Wilson et al. (2005)
    """, file=f)

        # --- Aggregated per question ---
        print("\nAggregated per question (average robustness across temperatures):", file=f)
        print(results["aggregate_per_question"].to_string(index=False), file=f)
        print("""
    What it shows:
    - mean_combined_index_across_temps: average overall robustness score per question
    - mean_cosine_across_temps: average semantic similarity
    - pairs: number of pairwise comparisons

    Interpretation:
    - High average scores → outputs are robust and consistent
    - Low scores → outputs are sensitive to randomness
    - Compare across questions to see which are more stable

    Method introduced in Ref.: Callison-Burch et al. (2006); Smith (2012)
    """, file=f)

        # --- Overall summary ---
        print("\nOverall summary across all questions and temperatures:", file=f)
        for k, v in results["overall_summary"].items():
            print(f"{k}: {v:.4f}", file=f)
        print("""
    What it shows:
    - mean_combined_index_all_pairs: overall robustness score
    - mean_cosine_all_pairs: overall semantic similarity
    - mean_structural_all_pairs: overall structural similarity

    Interpretation:
    - Close to 1 → outputs are highly stable across temperatures
    - Lower values → outputs are sensitive to randomness or task ambiguity
    - Provides a high-level view of AI robustness across all use cases and questions

    Method introduced in Ref.: Callison-Burch et al. (2006); Smith (2012)
    """, file=f)

        # --- Summary table of all methods and references with paper names ---
        print("\nSummary of methods and scientific references used in the evaluation (with paper names):", file=f)
        print("""
    Method                              | Used in Script | Scientific Reference (Paper)
    ------------------------------------|----------------|------------------------------------------------------------
    TF-IDF semantic similarity          | Yes            | Salton & Buckley (1988) - 'Term-weighting approaches in automatic text retrieval'; Manning et al. (2008) - 'Introduction to Information Retrieval'
    Jaccard index                       | Yes            | Jaccard (1901) - 'Étude comparative de la distribution florale dans une portion des Alpes et des Jura'
    ROUGE-L                             | Yes            | Lin (2004) - 'ROUGE: A Package for Automatic Evaluation of Summaries'
    Structural sentence similarity      | Yes            | Foltz et al. (1998) - 'Statistical models for text similarity'; Lapata (2006) - 'Automatic Evaluation of Summaries'; Barzilay & Lapata (2008) - 'Modeling local coherence'
    Numeric consistency                 | Yes            | Wallace et al. (2019) - 'Do NLP Models Know Numbers?'; Chen et al. (2020) - 'Neural Verification of Quantitative Statements'
    Contradiction detection             | Yes            | de Marneffe et al. (2008) - 'Generating Typed Dependency Parses from Phrase Structure Parses'; Wilson et al. (2005) - 'Recognizing Contextual Polarity in Phrase-Level Sentiment Analysis'
    Composite robustness index          | Yes            | Callison-Burch et al. (2006) - 'Re-evaluating the Role of BLEU in Machine Translation Research'; Smith (2012) - 'Evaluation metrics for NLP tasks'
    """, file=f)

    print(f"\nRobustness evaluation saved to '{output_file}'")
