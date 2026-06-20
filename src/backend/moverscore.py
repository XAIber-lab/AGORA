#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import warnings
from transformers import logging as transformers_logging

transformers_logging.set_verbosity_error()
warnings.filterwarnings("ignore")

# Set to "" for CPU, or specific ID for GPU. DeBERTa-v3 is recommended for accuracy.
os.environ["CUDA_VISIBLE_DEVICES"] = "" 
os.environ["MOVERSCORE_MODEL"] = "microsoft/deberta-v3-small"

from typing import List, Union, Iterable, Dict
from itertools import zip_longest
from collections import defaultdict
import numpy as np
import sacrebleu
from moverscore_v2 import get_idf_dict, word_mover_score, get_fact_weights


from nltk.tokenize import sent_tokenize


# 1. Defined a standard set of stop words to prevent "the", "is", etc. from inflating scores
STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'and', 'or', 'in', 'of', 'to', 'at', 
    'by', 'from', 'with', 'it', 'its', 'they', 'them', 'that', 'which'
}

def sentence_score(hypothesis: str, references: List[str], trace=0) -> float:
    """
    Computes the MoverScore using unit-weights (IDF=1.0) and stop-word filtering.
    """
    # Use 1.0 weights so every technical word/number is equally important
    idf_dict_ref = get_idf_dict(references) 
    
    # We use a simple frequency count for the hypothesis to balance it
    idf_dict_hyp = get_idf_dict([hypothesis])

    # word_mover_score expects a list of hypotheses matching the length of references
    hypotheses = [hypothesis] * len(references)
    
    scores = word_mover_score(
        references, 
        hypotheses, 
        idf_dict_ref, 
        idf_dict_hyp, 
        stop_words=list(STOP_WORDS), 
        n_gram=1, # Unigrams are best for specific fact/number matching
        remove_subwords=True
    )
    
    final_score = np.mean(scores)
    
    if trace > 0:
        print(f"Score: {final_score:.4f} | Hyp: {hypothesis[:50]}...")
            
    return float(final_score)

def fact_coverage_report(hypothesis: str, ground_truth_facts: List[str]) -> Dict:
    """
    Evaluates how well each individual fact is covered by the hypothesis.
    Returns a detailed breakdown of coverage per fact.
    """
    report = {"facts": [], "overall_coverage": 0.0}
    scores = []

    for fact in ground_truth_facts:
        # We compare the whole hypothesis against one specific fact
        score = sentence_score(hypothesis, [fact])
        scores.append(score)
        
        # Heuristic: MoverScore > 0.6 usually indicates strong semantic alignment
        status = "Covered" if score > 0.6 else "Partial/Missed"
        
        report["facts"].append({
            "fact": fact,
            "score": round(score, 4),
            "status": status
        })

    report["overall_coverage"] = float(np.mean(scores))
    return report

def test_fact_evaluation():
    # Your ground truth divided into atomic facts
    ground_truth_facts = [
        'Active incidents decreased from 1963 to 451.',
        'The decrease in active incidents suggests mass incidents or a resolved backlog.',
        '323 closed incidents had high severity.',
        '216 closed incidents had critical severity.',
        'A mass closure of active incidents began on Friday, June 3.',
        'Average process fitness was approximately 0.695.',
        'The average SLA was very low with 44.43%.',
        'Average time to resolve incidents was 15 days 3 hours 27 minutes.'
    ]

    # The generated summary
    sys_summary = (
        "The incident management process currently exhibits moderate overall compliance "
        "with an average fitness of 0.6948. However, a critically low SLA attainment rate "
        "of 44.43% reveals failures. While active incidents decreased from 1963 to 451, "
        "a substantial portion of closed incidents show poor compliance, with 323 "
        "classified as High and 216 as Critical severity."
    )

    print("--- Fact Coverage Report ---")
    report = fact_coverage_report(sys_summary, ground_truth_facts)
    
    for item in report["facts"]:
        print(f"[{item['status']}] (Score: {item['score']}) {item['fact']}")
    
    print("-" * 30)
    print(f"Total Fact Coverage Score: {report['overall_coverage']:.4f}")

    # Standard BLEU for comparison
    bleu = sacrebleu.sentence_bleu(sys_summary, ground_truth_facts)
    print(f"Reference BLEU (SacreBLEU): {bleu.score:.2f}")

import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

def get_best_sentence_match(summary_text: str, fact: str, threshold: float = 0.35):
    import nltk
    from nltk.tokenize import sent_tokenize
    

    # 1. Candidate Generation: Sentence Level
    summary_sentences = sent_tokenize(summary_text)
    candidates = summary_sentences.copy()
    
    # 2. Candidate Generation: Fine-Grained Sliding Window
    # We split by words and create chunks of 10-15 words.
    # This is small enough to ignore 'unrelated' context in the summary.
    words = summary_text.split()
    fact_len = len(fact.split())
    
    # Set window size to roughly the same size as the fact (+/- 7 words)
    window_size = fact_len + 7
    step_size = 2
    
    if len(words) > window_size:
        for i in range(0, len(words) - window_size + 1, step_size):
            chunk = " ".join(words[i : i + window_size])
            candidates.append(chunk)

    # 3. Smart Filtering: Only score candidates that share a number or key noun
    # This ignores completely irrelevant parts of the summary
    fact_words = set(w.lower() for w in fact.split() if len(w) > 2)
    
    best_score = 0.0
    idf_dict = get_fact_weights(fact)

    for cand in set(candidates):
        # Quick heuristic: if the candidate and fact don't share ANY words/numbers,
        # don't waste time running the expensive BERT model.
        cand_words = set(w.lower() for w in cand.split())
        if not fact_words.intersection(cand_words):
            continue
            
        # Score the fragment
        s = word_mover_score([fact], [cand], idf_dict, idf_dict, n_gram=1, batch_size=1)[0]
        
        # Calculate "Overlapping Anchors"
        fact_nums = set(filter(lambda x: any(c.isdigit() for c in x), fact.split()))
        cand_nums = set(filter(lambda x: any(c.isdigit() for c in x), cand.split()))

        # If they share the exact same numbers, give a 15% bonus to the score
        if fact_nums and fact_nums.issubset(cand_nums):
            s += 0.15 

        # Ensure score doesn't exceed 1.0
        s = min(1.0, s)
        
        if s > best_score:
            best_score = s
            
    # 4. Interpret
    return best_score, best_score >= threshold


if __name__ == '__main__':
    # 1. Silence logs
    import logging
    import nltk
    logging.getLogger("transformers").setLevel(logging.ERROR)
    nltk.download('punkt', quiet=True)

    # 2. Your test data
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

    # Updated summary
    sys_summary = (
        "The incident management process currently exhibits moderate overall compliance "
        "with an average fitness of 0.6948. However, a critically low SLA attainment rate "
        "of 44.43% reveals failures. While active incidents decreased from 1963 to 451, "
        "a substantial portion of closed incidents show poor compliance, with 323 "
        "classified as High and 216 as Critical severity."
    )

    print("--- Starting Evaluation ---")
    
    found_count = 0
    total_facts = len(facts)

    for fact in facts:
        # UNPACK BOTH VALUES HERE:
        score, found = get_best_sentence_match(sys_summary, fact)
        
        if found:
            found_count += 1
            status = "✅ FOUND "
        else:
            status = "❌ MISSED"
            
        print(f"Fact: {fact[:40]:<40} | Score: {score:.4f} | {status}")

    # --- FINAL METRICS ---
    coverage_ratio = found_count / total_facts if total_facts > 0 else 0
    
    print("-" * 75)
    print(f"Summary Statistics:")
    print(f"Total Facts Evaluated: {total_facts}")
    print(f"Total Facts Found:     {found_count}")
    print(f"Final Coverage Score:  {coverage_ratio:.2%} ({found_count}/{total_facts})")
    print("-" * 75)