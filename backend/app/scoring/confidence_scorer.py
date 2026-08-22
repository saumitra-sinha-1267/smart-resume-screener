from typing import Dict, Any, Tuple, List
from app.normalization.schema_models import CandidateData, ScoreOutput

def calculate_confidence(candidate: CandidateData, score: ScoreOutput) -> Tuple[str, Dict[str, Any]]:
    """Calculates multi-dimensional confidence score with structured reasoning."""
    reasons: List[str] = []

    # 1. Data Completeness (0 to 1.0)
    has_contact = 1.0 if (candidate.contact.email or candidate.contact.phone or candidate.contact.masked_email) else 0.4
    has_experience = 1.0 if len(candidate.experience) >= 2 else (0.5 if len(candidate.experience) == 1 else 0.0)
    has_education = 1.0 if candidate.education else 0.5
    has_skills = 1.0 if len(candidate.skills) >= 4 else (0.5 if candidate.skills else 0.2)

    completeness_score = (has_contact * 0.15) + (has_experience * 0.45) + (has_education * 0.15) + (has_skills * 0.25)
    if completeness_score >= 0.85:
        reasons.append("Complete resume structure with verified contact, multi-tenure experience, and education.")
    elif completeness_score < 0.5:
        reasons.append("Sparse resume data; limited work history or contact details.")

    # 2. Evidence Density & Quality
    total_bullets = sum(len(e.bullets) for e in candidate.experience)
    strong_bullets = 0
    for exp in candidate.experience:
        for b in exp.bullets:
            if any(m in b for m in ["%", "ms", "k", "m", "$", "team of"]):
                strong_bullets += 1

    evidence_ratio = min(1.0, (strong_bullets / max(1, total_bullets)) * 2.0) if total_bullets > 0 else 0.2
    if strong_bullets >= 2:
        reasons.append(f"Strong evidence backing: {strong_bullets} quantified metric achievements detected.")
    else:
        reasons.append("Limited quantified evidence; relies predominantly on qualitative bullet descriptions.")

    # 3. Requirement Coverage
    req_matches = score.requirement_matches
    if req_matches:
        mand_reqs = [r for r in req_matches if r.is_mandatory]
        matched_mand = [r for r in mand_reqs if r.status in ["MATCHED", "INFERRED"]]
        req_coverage = len(matched_mand) / max(1, len(mand_reqs))
        if req_coverage >= 0.8:
            reasons.append(f"High mandatory requirement coverage ({len(matched_mand)}/{len(mand_reqs)} matched).")
        else:
            reasons.append(f"Mandatory requirement gaps ({len(mand_reqs) - len(matched_mand)} missing criteria).")
    else:
        req_coverage = 0.7

    # 4. External Link Verification
    total_links = len(candidate.external_links)
    verified_links = sum(1 for l in candidate.external_links if l.verified is True)
    link_score = (verified_links / total_links) if total_links > 0 else 0.7
    if verified_links > 0:
        reasons.append(f"External exhibits confirmed ({verified_links} verified GitHub/portfolio link).")

    # 5. Hallucination Check Impact
    guard_penalty = 0.0 if score.hallucination_guard_passed else 0.30
    if not score.hallucination_guard_passed:
        reasons.append("Hallucination guard detected and penalized unverified skill claims.")

    # Composite Confidence Index
    composite_index = (
        (completeness_score * 0.30) +
        (req_coverage * 0.30) +
        (evidence_ratio * 0.25) +
        (link_score * 0.15) -
        guard_penalty
    )
    composite_index = max(0.0, min(1.0, composite_index))

    if composite_index >= 0.70:
        confidence_label = "High"
    elif composite_index >= 0.45:
        confidence_label = "Medium"
    else:
        confidence_label = "Low"

    breakdown = {
        "composite_index": round(composite_index, 2),
        "data_completeness": round(completeness_score, 2),
        "requirement_coverage": round(req_coverage, 2),
        "evidence_density": round(evidence_ratio, 2),
        "link_verification_rate": round(link_score, 2),
        "total_bullets_analyzed": total_bullets,
        "strong_bullets_count": strong_bullets,
        "reasons": reasons
    }

    return confidence_label, breakdown
