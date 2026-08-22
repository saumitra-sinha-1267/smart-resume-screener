import pytest
from evaluation.dataset import BENCHMARK_CANDIDATES, BENCHMARK_JOB_BACKEND, GROUND_TRUTH_BACKEND_RELEVANCE
from evaluation.metrics import (
    precision_at_k, recall_at_k, ndcg_at_k, mean_reciprocal_rank,
    false_positive_rate, false_negative_rate
)
from evaluation.bias_audit import run_bias_consistency_audit
from evaluation.confidence_eval import evaluate_confidence_calibration
from evaluation.run import execute_full_evaluation

def test_metrics_math():
    gt = {"c1": 3, "c2": 2, "c3": 1, "c4": 0}
    p5 = precision_at_k(["c1", "c2", "c3", "c4"], gt, k=2, min_relevance=2)
    assert p5 == 1.0

    r = recall_at_k(["c1", "c3"], gt, k=2, min_relevance=2)
    assert r == 0.5

    mrr = mean_reciprocal_rank(["c4", "c1", "c2"], gt, min_relevance=2)
    assert mrr == 0.5

    ndcg = ndcg_at_k(["c1", "c2", "c3", "c4"], gt, k=4)
    assert ndcg == 1.0

def test_bias_consistency_audit():
    res = run_bias_consistency_audit(BENCHMARK_CANDIDATES, BENCHMARK_JOB_BACKEND)
    assert res["audit_name"] == "Bias/Consistency Audit"
    assert res["mean_absolute_difference"] == 0.0
    assert res["max_delta"] == 0.0
    assert res["is_consistent"] is True

def test_confidence_calibration_audit():
    res = evaluate_confidence_calibration(BENCHMARK_CANDIDATES, BENCHMARK_JOB_BACKEND)
    assert res["total_evaluated"] == len(BENCHMARK_CANDIDATES)
    assert res["unjustified_high_count"] == 0
    assert res["is_calibrated"] is True

def test_full_evaluation_execution():
    report = execute_full_evaluation()
    assert report["dataset_size"]["total_candidates"] == len(BENCHMARK_CANDIDATES)
    assert report["ranking_metrics"]["Precision@5"] >= 0.80
    assert report["ranking_metrics"]["NDCG@10"] >= 0.85
    assert report["ranking_metrics"]["MRR"] == 1.0
    assert report["hallucination_evaluation"]["hallucination_rate"] <= 0.10
