import math
from typing import List, Dict

def precision_at_k(retrieved_ids: List[str], ground_truth: Dict[str, int], k: int = 5, min_relevance: int = 2) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(1 for cid in top_k if ground_truth.get(cid, 0) >= min_relevance)
    return round(relevant_count / len(top_k), 4)

def recall_at_k(retrieved_ids: List[str], ground_truth: Dict[str, int], k: int = 10, min_relevance: int = 2) -> float:
    total_relevant = sum(1 for rel in ground_truth.values() if rel >= min_relevance)
    if total_relevant == 0:
        return 1.0
    top_k = retrieved_ids[:k]
    retrieved_relevant = sum(1 for cid in top_k if ground_truth.get(cid, 0) >= min_relevance)
    return round(retrieved_relevant / total_relevant, 4)

def ndcg_at_k(retrieved_ids: List[str], ground_truth: Dict[str, int], k: int = 10) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0

    dcg = 0.0
    for i, cid in enumerate(top_k):
        rel = ground_truth.get(cid, 0)
        dcg += (math.pow(2, rel) - 1.0) / math.log2(i + 2)

    ideal_rels = sorted(ground_truth.values(), reverse=True)[:k]
    idcg = 0.0
    for i, rel in enumerate(ideal_rels):
        idcg += (math.pow(2, rel) - 1.0) / math.log2(i + 2)

    if idcg == 0.0:
        return 1.0
    return round(dcg / idcg, 4)

def mean_reciprocal_rank(retrieved_ids: List[str], ground_truth: Dict[str, int], min_relevance: int = 2) -> float:
    for i, cid in enumerate(retrieved_ids):
        if ground_truth.get(cid, 0) >= min_relevance:
            return round(1.0 / (i + 1), 4)
    return 0.0

def false_positive_rate(scores: Dict[str, float], ground_truth: Dict[str, int], threshold: float = 7.0, min_relevance: int = 2) -> float:
    negatives = [cid for cid, rel in ground_truth.items() if rel < min_relevance]
    if not negatives:
        return 0.0
    false_positives = sum(1 for cid in negatives if scores.get(cid, 0.0) >= threshold)
    return round(false_positives / len(negatives), 4)

def false_negative_rate(scores: Dict[str, float], ground_truth: Dict[str, int], threshold: float = 7.0, min_relevance: int = 2) -> float:
    positives = [cid for cid, rel in ground_truth.items() if rel >= min_relevance]
    if not positives:
        return 0.0
    false_negatives = sum(1 for cid in positives if scores.get(cid, 0.0) < threshold)
    return round(false_negatives / len(positives), 4)
