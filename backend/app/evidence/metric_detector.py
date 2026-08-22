import re
from typing import Dict, Any, List, Tuple, Literal
from app.normalization.schema_models import CandidateData, SkillItem

METRIC_PATTERNS = [
    ("percentage", r"\b\d+(?:\.\d+)?%\b", "Percentage improvement or ratio"),
    ("latency_speed", r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds|seconds|mins|minutes|x|fold)\b", "Latency or speed metric"),
    ("scale_volume", r"\b\d+(?:\.\d+)?\s*(?:k|m|b|million|billion|thousand|tb|gb|pb|qps|rps|dau|mau|tps|users|concurrent|requests)\b", "Scale or volume metric"),
    ("financial", r"(?:[\$€£₹]\s*\d+(?:\.\d+)?\s*(?:k|m|b|million|thousand)?|\b\d+(?:\.\d+)?\s*(?:million|k)\s*(?:dollars|usd|eur))", "Financial or budget impact"),
    ("team_headcount", r"\b(?:led|managed|mentored|scaled|grew)\s+(?:a\s+)?(?:team|squad|group|org|pod)?\s*(?:of\s+)?\d+\s*(?:engineers|developers|reports|people|members|directs)\b", "Team size or headcount leadership"),
    ("count_metric", r"\b(?:from|to|by)\s+\d+(?:\.\d+)?\b", "Quantitative transition measure")
]

GENERIC_WEAK_PHRASES = [
    r"\bresponsible\s+for\b",
    r"\bassisted\s+(?:with|in)\b",
    r"\bparticipated\s+in\b",
    r"\bhelped\s+(?:with|the)\b",
    r"\bworked\s+on\b",
    r"\battended\s+meetings\b",
    r"\bduties\s+included\b"
]

TECHNICAL_ACTION_VERBS = [
    "architected", "engineered", "implemented", "deployed", "refactored", "optimized",
    "built", "designed", "spearheaded", "developed", "automated", "migrated", "sharded",
    "benchmarked", "integrated", "containerized", "fine-tuned", "scaled"
]

def classify_evidence_quality(bullet: str) -> Tuple[Literal["STRONG", "MEDIUM", "WEAK"], List[Dict[str, str]]]:
    """Classifies bullet evidence into STRONG (quantified + technical), MEDIUM (specific technical), or WEAK (generic)."""
    found_metrics: List[Dict[str, str]] = []
    bullet_lower = bullet.lower()

    for cat, pattern, desc in METRIC_PATTERNS:
        matches = list(re.finditer(pattern, bullet, re.IGNORECASE))
        for m in matches:
            found_metrics.append({
                "category": cat,
                "value": m.group(0),
                "description": desc,
                "span": [m.start(), m.end()]
            })

    has_metrics = len(found_metrics) > 0
    has_tech_action = any(re.search(r"\b" + re.escape(v) + r"\b", bullet_lower) for v in TECHNICAL_ACTION_VERBS)
    is_generic = any(re.search(p, bullet_lower) for p in GENERIC_WEAK_PHRASES)

    if has_metrics:
        return "STRONG", found_metrics
    elif has_tech_action and not is_generic:
        return "MEDIUM", found_metrics
    elif is_generic:
        return "WEAK", found_metrics
    else:
        return "MEDIUM" if len(bullet.split()) >= 8 else "WEAK", found_metrics

def analyze_bullet_metrics(bullet: str) -> Dict[str, Any]:
    strength, found_metrics = classify_evidence_quality(bullet)
    return {
        "is_quantified": len(found_metrics) > 0,
        "metrics_count": len(found_metrics),
        "metrics": found_metrics,
        "evidence_strength": strength,
        "text": bullet
    }

def enrich_candidate_with_evidence(candidate: CandidateData) -> CandidateData:
    c_copy = candidate.model_copy(deep=True)
    total_bullets = 0
    quantified_bullets = 0

    for exp in c_copy.experience:
        for b in exp.bullets:
            total_bullets += 1
            analysis = analyze_bullet_metrics(b)
            if analysis["is_quantified"]:
                quantified_bullets += 1
                for sk in c_copy.skills:
                    if sk.name.lower() in b.lower() or (sk.original_text and sk.original_text == b):
                        sk.quantified_evidence = True
                        sk.evidence_strength = "STRONG"

    for sk in c_copy.skills:
        if sk.original_text:
            analysis = analyze_bullet_metrics(sk.original_text)
            if analysis["is_quantified"]:
                sk.quantified_evidence = True
                sk.evidence_strength = "STRONG"
            elif analysis["evidence_strength"] == "WEAK":
                sk.evidence_strength = "WEAK"

    return c_copy
