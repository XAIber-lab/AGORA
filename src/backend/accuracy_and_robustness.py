"""
Robustness + Ground Truth Evaluation Script (Option B: semantic fact matching)

Inputs:
- CSV file (input_csv) with columns: control_id, iteration, recommendation
- GROUND_TRUTHS dict: { control_id: [fact1, fact2, ...], ... }

Outputs:
- ai_evaluation_per_iteration.csv  (one row per AI iteration with all metrics)
- ai_evaluation_summary.csv        (mean + std per control_id)
"""

import csv
import re
import numpy as np
import pandas as pd
from collections import defaultdict

# text / NLP
import nltk
nltk.download("punkt", quiet=True)
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# vectorizers / similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# rouge
from rouge_score import rouge_scorer

# sentence embeddings & bertscore
from sentence_transformers import SentenceTransformer
from bert_score import score as bert_score

# ----------------------- USER CONFIG -----------------------
input_csv = "assessment_security_control_results_robustness_uc1_temp0.5.csv"  # change if needed

# Embedding model for semantic matching & structural similarity
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Semantic match threshold: cosine similarity >= this value => fact considered present
MATCH_THRESHOLD = 0.75

# BLEU smoothing
BLEU_SMOOTHER = SmoothingFunction().method4

# -----------------------------------------------------------

# --------------------- GROUND TRUTHS -----------------------
# Fill in your ground truth facts (atomic facts) for control IDs 148..154
GROUND_TRUTHS = {

    # -----------------------------------------------------
    # Control 148
    # -----------------------------------------------------
    148: [
        # Incident volumes & severities
        "Active incidents decreased from 1963 to 451.",
        "The decrease in active incidents suggests mass incidents in the previous month or a resolved backlog.",
        #"Most closed incidents had low or moderate process severity.",
        #"323 closed incidents had high severity.",
        #"216 closed incidents had critical severity.",
        "7 incidents had critical process severity"
        "103 incidents had high process severity.",
        "The majority of incidents had low process severity.",
        "A mass closure of active incidents began on Friday, June 3.",
        "Incidents closed later in June showed higher process severity.",

        # Compliance metrics
        #"Average process fitness was approximately 0.695, indicating moderate concerns.",
        "Average cost was 0.047 which is in the low process serverity range.",
        "The average SLA was very low with 44.43% and must be considered critical.",
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

        "Average transition times were mostly acceptable.",

        "Transition time from awaiting to resolution was 8 days 1 hour 19 minutes (11599 minutes).",


        # Explanations for non-compliant transitions
        #"The potentially non-compliant detection→awaiting transition is explained by merging into an existing awaiting incident.",
        #"The potentially non-compliant detection→resolution transition is explained by temporary whitelisting and merging into already resolved cases."
    ],

    # -----------------------------------------------------
    # Control 150
    # -----------------------------------------------------
    150: [
        #"The most common variant (NRC) (Count 182) is non-compliant due to missing activation",
        "The most common variant (NRC) (Count 182) is now considered process compliant due to automatic merge rules",
        "Variants ARC (count 135) are missing detections and are non-compliant.",
        #"The most frequent variants show repetitive detections before activation.",
        "Repetitive detections are no process violation due to potentially multiple triggers",
        #"Variants with awaiting state frequently show repetitive awaiting events.",
        "Variants with repetitive awaiting activities are not process violations due to customer or third-party delays.",
    ],

    # -----------------------------------------------------
    # Control 151
    # -----------------------------------------------------
    151: [
        # General
        #"Detection, activation, and awaiting activities showed high to critical non-compliance and require further assessment.",
        "No process activities showed concering average compliance cost exceeding the individual thresholds.",

        # Detection
        "There were 319 missing detections, that violate threshold",
        #"There were 1777 repetitive detections, that violate the threshold",
        "There were 1777 repetitive detections, that do not violate the threshold",
        "There were 0 detection mismatches.",

        # Activation
        #"There were 544 missing activations that violate the threshold",
        "There were 544 missing activations caused by merge rules and are not process violations.",
        "There were 1990 repetitive activations, which violate the threshold",
        "There were 115 activation mismatches, which violate the theshold",

        # Awaiting
        #"There were 1653 repetitive awaiting events, that violate the threshold",
        "There were 1653 repetitive awaiting events, that do not violate the threshold",
        "There were 4 awaiting mismatches, a negligible amount.",

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
        #"Several incidents (216) had process fitness of 0.5 and below.",
        "Critical process severity incidents are 7 in total"
        #"INC0032450 had the lowest process fitness of 0.19.",
        "INC0033952 has the highest assigned compliance cost with 0.81"
        #"Multiple incidents had process fitness between 0.2 and 0.3.",
        "INC0025696, INC0026744 and INC0032450 show cost of 0.41"
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

# -----------------------------------------------------------

# -------------------- UTILITY FUNCTIONS --------------------

def normalize_text(t: str) -> str:
    """Lowercase and collapse whitespace; keep punctuation minimally for BLEU/ROUGE."""
    if t is None:
        return ""
    return re.sub(r"\s+", " ", t.strip())

def split_sentences(text: str):
    """Split into sentences (NLTK punkt is available)."""
    if not text:
        return []
    return [s.strip() for s in nltk.tokenize.sent_tokenize(text) if s.strip()]

# -------------------- METRIC FUNCTIONS ---------------------

# TF-IDF cosine similarity between two documents
def cosine_tfidf(doc_a: str, doc_b: str) -> float:
    vect = TfidfVectorizer().fit([doc_a, doc_b])
    mat = vect.transform([doc_a, doc_b])
    sim = cosine_similarity(mat[0], mat[1])[0][0]
    return float(np.clip(sim, 0.0, 1.0))

# ROUGE-L F1 using rouge_score
rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
def rouge_l_f1(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    sc = rouge.score(a, b)["rougeL"]
    return float(sc.fmeasure)

# BLEU (sentence-level, reference = GT merged text)
def compute_bleu(reference: str, hypothesis: str) -> float:
    ref_tokens = reference.split()
    hyp_tokens = hypothesis.split()
    if len(hyp_tokens) == 0:
        return 0.0
    return float(sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=BLEU_SMOOTHER))

# Load embedding model once
embed_model = SentenceTransformer(EMBEDDING_MODEL)

# Structural similarity: encode sentences and compute alignment (average best-match)
def structural_similarity(textA: str, textB: str) -> float:
    sA = split_sentences(textA)
    sB = split_sentences(textB)
    if not sA or not sB:
        # fallback: embed whole docs
        emb = embed_model.encode([textA, textB], convert_to_numpy=True)
        return float(cosine_similarity([emb[0]], [emb[1]])[0][0])
    # embed all sentences together for consistent vector space
    all_sents = sA + sB
    embs = embed_model.encode(all_sents, convert_to_numpy=True)
    A = embs[:len(sA)]
    B = embs[len(sA):]
    sim = cosine_similarity(A, B)
    # average bidirectional best matches
    score = float((sim.max(axis=1).mean() + sim.max(axis=0).mean()) / 2)
    return float(np.clip(score, 0.0, 1.0))

# BERTScore F1 (wrap bert_score)
def compute_bertscore(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    P, R, F1 = bert_score([a], [b], lang="en", rescale_with_baseline=True, verbose=False)
    return float(F1[0].cpu().numpy()) if hasattr(F1[0], "cpu") else float(F1[0])

# ---------------- FACT MATCHING (Option B: semantic) ----------------
# For each ground-truth fact, compute embedding; for each AI sentence compute embedding;
# consider a GT fact matched if any AI sentence has cosine >= MATCH_THRESHOLD.
# Also count matched AI sentences for precision calculation.

def semantic_fact_matching(gt_facts, ai_text, model=embed_model, threshold=MATCH_THRESHOLD):
    """
    Returns:
      matched_gt_indices: set of indices of gt_facts matched
      matched_ai_sentence_indices: set of indices of AI sentences that matched any gt
      total_ai_sentences: total sentences in AI text
    """
    gt_facts = [normalize_text(f) for f in gt_facts]
    ai_sentences = split_sentences(ai_text)
    total_ai_sentences = len(ai_sentences)

    if len(gt_facts) == 0:
        return set(), set(), total_ai_sentences

    # Compute embeddings
    # embed GT facts and AI sentences in same space
    to_embed = gt_facts + ai_sentences if ai_sentences else gt_facts
    embs = model.encode(to_embed, convert_to_numpy=True)
    gt_embs = embs[:len(gt_facts)]
    ai_embs = embs[len(gt_facts):] if ai_sentences else np.zeros((0, embs.shape[1]))

    matched_gt = set()
    matched_ai_sent = set()

    if ai_sentences:
        sim_mat = cosine_similarity(gt_embs, ai_embs)  # shape (n_gt, n_ai)
        for i_gt in range(sim_mat.shape[0]):
            for j_ai in range(sim_mat.shape[1]):
                if sim_mat[i_gt, j_ai] >= threshold:
                    matched_gt.add(i_gt)
                    matched_ai_sent.add(j_ai)
    else:
        # no AI sentences -> nothing matches
        pass

    return matched_gt, matched_ai_sent, total_ai_sentences

# Precision/Recall/F1 computations using semantic matching
def compute_prf(gt_facts, ai_text, threshold=MATCH_THRESHOLD):
    matched_gt, matched_ai_sent, total_ai_sentences = semantic_fact_matching(gt_facts, ai_text, model=embed_model, threshold=threshold)
    tp = len(matched_gt)  # true positives = number of distinct GT facts matched
    fn = max(len(gt_facts) - tp, 0)
    # For precision denominator: number of AI claims. We use total_ai_sentences (could be >0)
    denom = total_ai_sentences if total_ai_sentences > 0 else 1
    precision = tp / denom
    recall = tp / len(gt_facts) if len(gt_facts) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "true_positives": int(tp),
        "gt_count": int(len(gt_facts)),
        "ai_claims": int(total_ai_sentences),
        "matched_ai_claims": int(len(matched_ai_sent))
    }

# --------------------- MAIN EVALUATION PIPELINE ---------------------

def evaluate_all(input_csv_path):
    # load CSV
    rows = []
    with open(input_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "control_id": int(r["control_id"]),
                "iteration": int(r["iteration"]),
                "recommendation": r["recommendation"]
            })

    per_iter_results = []
    for row in rows:
        cid = row["control_id"]
        if cid not in GROUND_TRUTHS:
            # Skip or warn
            continue
        ai_text = normalize_text(row["recommendation"])
        gt_facts = GROUND_TRUTHS[cid]

        # metrics vs merged GT text
        gt_text = " ".join(gt_facts)

        cos_tfidf = cosine_tfidf(ai_text, gt_text)
        rouge_l = rouge_l_f1(ai_text, gt_text)
        bleu = compute_bleu(gt_text, ai_text)
        struct_sim = structural_similarity(ai_text, gt_text)
        bert_f1 = compute_bertscore(ai_text, gt_text)

        # precision/recall/f1 by semantic fact matching
        prf = compute_prf(gt_facts, row["recommendation"], threshold=MATCH_THRESHOLD)

        per_iter_results.append({
            "control_id": cid,
            "iteration": row["iteration"],
            "cosine_tfidf": cos_tfidf,
            "rouge_l_f1": rouge_l,
            "bleu": bleu,
            "structural_similarity": struct_sim,
            "bertscore_f1": bert_f1,
            "precision": prf["precision"],
            "recall": prf["recall"],
            "f1": prf["f1"],
            "true_positives": prf["true_positives"],
            "gt_count": prf["gt_count"],
            "ai_claims": prf["ai_claims"],
            "matched_ai_claims": prf["matched_ai_claims"]
        })

    df = pd.DataFrame(per_iter_results)

    # aggregate mean and std per control_id
    agg = df.groupby("control_id").agg(
        cosine_mean=("cosine_tfidf", "mean"),
        cosine_std=("cosine_tfidf", "std"),
        rouge_mean=("rouge_l_f1", "mean"),
        rouge_std=("rouge_l_f1", "std"),
        bleu_mean=("bleu", "mean"),
        bleu_std=("bleu", "std"),
        structural_mean=("structural_similarity", "mean"),
        structural_std=("structural_similarity", "std"),
        bertscore_mean=("bertscore_f1", "mean"),
        bertscore_std=("bertscore_f1", "std"),
        precision_mean=("precision", "mean"),
        precision_std=("precision", "std"),
        recall_mean=("recall", "mean"),
        recall_std=("recall", "std"),
        f1_mean=("f1", "mean"),
        f1_std=("f1", "std"),
        # Add integer metrics
        true_positives=("true_positives", "sum"),
        gt_count=("gt_count", "sum"),
        ai_claims=("ai_claims", "sum"),
        matched_ai_claims=("matched_ai_claims", "sum"),
        iterations=("iteration", "count")
    ).reset_index()

    return df, agg


# ------------------------- TXT REPORT GENERATION -------------------------
def generate_txt_report(per_iter_df: pd.DataFrame, summary_df: pd.DataFrame, filename="ai_evaluation_report.txt"):
    metrics_cols = [
        "cosine_tfidf", "rouge_l_f1", "bleu", "structural_similarity",
        "bertscore_f1", "precision", "recall", "f1",
        "true_positives", "gt_count", "ai_claims", "matched_ai_claims"
    ]

    metric_to_summary_cols = {
        "cosine_tfidf": ("cosine_mean", "cosine_std"),
        "rouge_l_f1": ("rouge_mean", "rouge_std"),
        "bleu": ("bleu_mean", "bleu_std"),
        "structural_similarity": ("structural_mean", "structural_std"),
        "bertscore_f1": ("bertscore_mean", "bertscore_std"),
        "precision": ("precision_mean", "precision_std"),
        "recall": ("recall_mean", "recall_std"),
        "f1": ("f1_mean", "f1_std"),
        "true_positives": ("true_positives", None),
        "gt_count": ("gt_count", None),
        "ai_claims": ("ai_claims", None),
        "matched_ai_claims": ("matched_ai_claims", None)
    }

    with open(filename, "w", encoding="utf-8") as f:
        f.write("AI Recommendation Robustness and Ground Truth Evaluation Report\n")
        f.write("="*100 + "\n\n")

        f.write("Per Control Metrics (Iterations as table):\n")
        f.write("-"*100 + "\n")

        # Per-control table
        for cid, group in per_iter_df.groupby("control_id"):
            f.write(f"Control ID: {cid}\n")
            # Table header
            header = "Iteration | " + " | ".join(metrics_cols)
            f.write(header + "\n")
            f.write("-"*len(header) + "\n")
            # Table rows
            for _, row in group.iterrows():
                values = []
                for col in metrics_cols:
                    val = row[col]
                    if col in ["true_positives", "gt_count", "ai_claims", "matched_ai_claims"]:
                        values.append(f"{int(val)}")
                    else:
                        values.append(f"{val:.3f}")
                f.write(f"{row['iteration']}        | " + " | ".join(values) + "\n")
            f.write("\n")

        f.write("="*100 + "\n")
        f.write("Per Control Summary (Mean ± Std):\n")
        f.write("-"*100 + "\n")

        # Summary per control
        for _, summary_row in summary_df.iterrows():
            cid = summary_row["control_id"]
            iterations = summary_row.get("iterations", "N/A")
            f.write(f"Control ID: {cid} | Iterations: {iterations}\n")
            for col in metrics_cols:
                mean_col, std_col = metric_to_summary_cols[col]
                mean_val = summary_row[mean_col]
                if std_col:
                    std_val = summary_row[std_col]
                    f.write(f"  {col}: {mean_val:.3f} ± {std_val:.3f}\n")
                else:
                    f.write(f"  {col}: {int(mean_val)}\n")
            f.write("-"*100 + "\n")

    print(f"Detailed TXT report saved as '{filename}'")

# ------------------------- RUN & SAVE -------------------------
if __name__ == "__main__":
    per_iter_df, summary_df = evaluate_all(input_csv)
    per_iter_df.to_csv("ai_evaluation_per_iteration.csv", index=False)
    summary_df.to_csv("ai_evaluation_summary.csv", index=False)
    print("Saved ai_evaluation_per_iteration.csv and ai_evaluation_summary.csv")
    print("Parameters: EMBEDDING_MODEL =", EMBEDDING_MODEL, "MATCH_THRESHOLD =", MATCH_THRESHOLD)

    generate_txt_report(per_iter_df, summary_df, filename="ai_evaluation_report_temp0.5.txt")
    print("Generated detailed TXT report: ai_evaluation_report_temp0.5.txt")
