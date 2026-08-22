import json
import os
import sys
from typing import Dict, Any
from evaluation.dataset import BENCHMARK_JOB_BACKEND, BENCHMARK_CANDIDATES, GROUND_TRUTH_BACKEND_RELEVANCE
from evaluation.metrics import (
    precision_at_k, recall_at_k, ndcg_at_k, mean_reciprocal_rank,
    false_positive_rate, false_negative_rate
)
from evaluation.bias_audit import run_bias_consistency_audit
from evaluation.confidence_eval import evaluate_confidence_calibration
from app.scoring.llm_scorer import deterministic_calibrated_scoring

def execute_full_evaluation() -> Dict[str, Any]:
    job = BENCHMARK_JOB_BACKEND
    candidates = BENCHMARK_CANDIDATES
    ground_truth = GROUND_TRUTH_BACKEND_RELEVANCE

    scored_candidates = []
    scores_dict: Dict[str, float] = {}
    all_claims = []

    for cand in candidates:
        sc = deterministic_calibrated_scoring(cand, job)
        scored_candidates.append((cand.candidate_id, sc.overall_score, sc))
        scores_dict[cand.candidate_id] = sc.overall_score
        if sc.verified_claims:
            all_claims.extend(sc.verified_claims)

    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    retrieved_ranking = [cid for cid, _, _ in scored_candidates]

    p_at_5 = precision_at_k(retrieved_ranking, ground_truth, k=5, min_relevance=2)
    r_at_10 = recall_at_k(retrieved_ranking, ground_truth, k=10, min_relevance=2)
    ndcg_10 = ndcg_at_k(retrieved_ranking, ground_truth, k=10)
    mrr_val = mean_reciprocal_rank(retrieved_ranking, ground_truth, min_relevance=2)

    fpr = false_positive_rate(scores_dict, ground_truth, threshold=7.0, min_relevance=2)
    fnr = false_negative_rate(scores_dict, ground_truth, threshold=7.0, min_relevance=2)

    total_claims = len(all_claims)
    verified_claims = sum(1 for c in all_claims if c.verification_status == "VERIFIED")
    unsupported_claims = sum(1 for c in all_claims if c.verification_status != "VERIFIED")
    hallucination_rate = round(unsupported_claims / max(1, total_claims), 4)

    bias_report = run_bias_consistency_audit(candidates, job)
    confidence_report = evaluate_confidence_calibration(candidates, job)

    report = {
        "dataset_size": {
            "total_candidates": len(candidates),
            "relevant_candidates_ground_truth": sum(1 for r in ground_truth.values() if r >= 2),
            "benchmark_job": job.title
        },
        "ranking_metrics": {
            "Precision@5": p_at_5,
            "Recall@10": r_at_10,
            "NDCG@10": ndcg_10,
            "MRR": mrr_val
        },
        "classification_metrics": {
            "False_Positive_Rate": fpr,
            "False_Negative_Rate": fnr,
            "Score_Threshold": 7.0
        },
        "hallucination_evaluation": {
            "total_claims_analyzed": total_claims,
            "verified_claims": verified_claims,
            "unsupported_claims": unsupported_claims,
            "hallucination_rate": hallucination_rate
        },
        "bias_consistency_audit": bias_report,
        "confidence_calibration": confidence_report,
        "actual_ranking": [
            {
                "rank": idx + 1,
                "candidate_id": cid,
                "score": round(score, 2),
                "ground_truth_relevance": ground_truth.get(cid, 0)
            }
            for idx, (cid, score, _) in enumerate(scored_candidates)
        ]
    }

    return report

def main():
    print("=" * 80)
    print("SMART RESUME SCREENER — AI EVALUATION SUITE")
    print("=" * 80)

    report = execute_full_evaluation()

    print(f"\n[1] DATASET OVERVIEW:")
    print(f"  • Total Candidates: {report['dataset_size']['total_candidates']}")
    print(f"  • Ground Truth Relevant (>=2): {report['dataset_size']['relevant_candidates_ground_truth']}")
    print(f"  • Target Benchmark Role: {report['dataset_size']['benchmark_job']}")

    print(f"\n[2] RANKING QUALITY METRICS:")
    print(f"  • Precision@5: {report['ranking_metrics']['Precision@5']:.4f} (Target: > 0.80)")
    print(f"  • Recall@10:   {report['ranking_metrics']['Recall@10']:.4f} (Target: 1.00)")
    print(f"  • NDCG@10:     {report['ranking_metrics']['NDCG@10']:.4f} (Target: > 0.85)")
    print(f"  • MRR:         {report['ranking_metrics']['MRR']:.4f} (Target: 1.00)")

    print(f"\n[3] ERROR & CLASSIFICATION METRICS:")
    print(f"  • False Positive Rate: {report['classification_metrics']['False_Positive_Rate']:.4f}")
    print(f"  • False Negative Rate: {report['classification_metrics']['False_Negative_Rate']:.4f}")

    print(f"\n[4] HALLUCINATION EVALUATION:")
    print(f"  • Total Claims Evaluated: {report['hallucination_evaluation']['total_claims_analyzed']}")
    print(f"  • Verified Claims:        {report['hallucination_evaluation']['verified_claims']}")
    print(f"  • Unsupported Claims:     {report['hallucination_evaluation']['unsupported_claims']}")
    print(f"  • Hallucination Rate:     {report['hallucination_evaluation']['hallucination_rate']:.4f}")

    print(f"\n[5] BIAS & CONSISTENCY AUDIT:")
    print(f"  • Tested Variables: {', '.join(report['bias_consistency_audit']['tested_attributes'])}")
    print(f"  • Mean Absolute Difference: {report['bias_consistency_audit']['mean_absolute_difference']:.4f}")
    print(f"  • Max Delta Observed:       {report['bias_consistency_audit']['max_delta']:.4f}")
    print(f"  • Status: {'PASS (Robust Consistency)' if report['bias_consistency_audit']['is_consistent'] else 'FLAG'}")
    print(f"  • Note: {report['bias_consistency_audit']['disclaimer']}")

    print(f"\n[6] CONFIDENCE CALIBRATION:")
    print(f"  • High Confidence:   {report['confidence_calibration']['high_confidence_count']}")
    print(f"  • Medium Confidence: {report['confidence_calibration']['medium_confidence_count']}")
    print(f"  • Low Confidence:    {report['confidence_calibration']['low_confidence_count']}")
    print(f"  • Unjustified High Rate: {report['confidence_calibration']['unjustified_high_rate']:.4f}")

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETED SUCCESSFULLY")
    print("=" * 80)

    out_json = os.path.join(os.path.dirname(__file__), "evaluation_report.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved report JSON to: {out_json}")

if __name__ == "__main__":
    main()
