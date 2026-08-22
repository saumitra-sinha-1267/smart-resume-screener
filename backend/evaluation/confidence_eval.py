from typing import List, Dict, Any
from app.normalization.schema_models import CandidateData, JobData
from app.scoring.llm_scorer import deterministic_calibrated_scoring

def evaluate_confidence_calibration(candidates: List[CandidateData], job: JobData) -> Dict[str, Any]:
    total = len(candidates)
    high_conf_count = 0
    med_conf_count = 0
    low_conf_count = 0
    unjustified_high_flags = []

    for cand in candidates:
        sc = deterministic_calibrated_scoring(cand, job)
        conf = sc.confidence

        if conf == "High":
            high_conf_count += 1
        elif conf == "Medium":
            med_conf_count += 1
        else:
            low_conf_count += 1

        strong_bullets = sum(
            1 for e in cand.experience for b in e.bullets
            if any(m in b for m in ["%", "ms", "k", "m", "$", "team of"])
        )
        if conf == "High" and (strong_bullets == 0 and len(cand.skills) < 3):
            unjustified_high_flags.append({
                "candidate_id": cand.candidate_id,
                "confidence": conf,
                "reason": "High confidence assigned despite 0 quantified metrics and sparse skill profile."
            })

    return {
        "total_evaluated": total,
        "high_confidence_count": high_conf_count,
        "medium_confidence_count": med_conf_count,
        "low_confidence_count": low_conf_count,
        "unjustified_high_count": len(unjustified_high_flags),
        "unjustified_high_rate": round(len(unjustified_high_flags) / max(1, total), 4),
        "is_calibrated": len(unjustified_high_flags) == 0,
        "flags": unjustified_high_flags
    }
