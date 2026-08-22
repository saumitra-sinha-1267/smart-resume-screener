import logging
from typing import Tuple, List, Dict, Any, Set
from app.normalization.schema_models import CandidateData, ScoreOutput, ClaimVerification
from app.normalization.taxonomy import SKILL_SYNONYMS
from app.evidence.metric_detector import classify_evidence_quality

logger = logging.getLogger(__name__)

def build_ground_truth_skills(candidate: CandidateData) -> Set[str]:
    """Builds a comprehensive set of verified skills and terms present in the candidate's resume."""
    truth: Set[str] = set()

    for s in candidate.skills:
        truth.add(s.name.lower())
        if s.original_text:
            truth.add(s.original_text.lower())

    for exp in candidate.experience:
        truth.add(exp.title.lower())
        for sk in exp.extracted_skills:
            truth.add(sk.lower())
        for b in exp.bullets:
            truth.add(b.lower())

    expanded = set(truth)
    for t in truth:
        for alias, canonical in SKILL_SYNONYMS.items():
            if alias in t or canonical.lower() in t:
                expanded.add(alias)
                expanded.add(canonical.lower())

    return expanded

def apply_hallucination_guard(score: ScoreOutput, candidate: CandidateData) -> ScoreOutput:
    """Verifies LLM's matched skills and claims against ground-truth extracted data and penalizes hallucinated claims."""
    ground_truth = build_ground_truth_skills(candidate)
    full_resume_text = (candidate.raw_text or "").lower()

    verified_matched: List[str] = []
    unverified_claims: List[Dict[str, Any]] = []
    claim_verifications: List[ClaimVerification] = []

    # Map bullets for fast quote lookup
    all_bullets = []
    for exp in candidate.experience:
        for b in exp.bullets:
            all_bullets.append(b)

    for skill in score.skills_match.matched:
        sk_lower = skill.lower()
        is_verified = False
        supporting_bullet = ""

        # Check direct match in truth
        if sk_lower in ground_truth or sk_lower in full_resume_text:
            is_verified = True
            # Find supporting bullet quote
            for b in all_bullets:
                if sk_lower in b.lower():
                    supporting_bullet = b
                    break
        elif sk_lower in ["data visualization", "data visualisation", "visualization"]:
            viz_tools = ["plotly", "power bi", "tableau", "matplotlib", "seaborn", "streamlit"]
            for tool in viz_tools:
                if tool in full_resume_text:
                    is_verified = True
                    for b in all_bullets:
                        if tool in b.lower():
                            supporting_bullet = b
                            break
                    if is_verified:
                        break
        elif sk_lower in ["statistics", "statistical analysis"]:
            stat_tools = ["hypothesis testing", "regression", "a/b testing", "statistical modeling", "anova"]
            for tool in stat_tools:
                if tool in full_resume_text:
                    is_verified = True
                    for b in all_bullets:
                        if tool in b.lower():
                            supporting_bullet = b
                            break
                    if is_verified:
                        break
        else:
            # Check canonical alias
            for alias, canonical in SKILL_SYNONYMS.items():
                if (alias == sk_lower or canonical.lower() == sk_lower) and (alias in full_resume_text or canonical.lower() in full_resume_text):
                    is_verified = True
                    for b in all_bullets:
                        if alias in b.lower() or canonical.lower() in b.lower():
                            supporting_bullet = b
                            break
                    break

        if is_verified:
            verified_matched.append(skill)
            strength, _ = classify_evidence_quality(supporting_bullet) if supporting_bullet else ("MEDIUM", [])
            
            # Realistic confidence calibrated against evidence strength
            if supporting_bullet:
                if strength == "STRONG":
                    conf_val = 0.95
                elif strength == "MEDIUM":
                    conf_val = 0.82
                else:
                    conf_val = 0.65
            else:
                strength = "MEDIUM"
                conf_val = 0.75

            claim_verifications.append(ClaimVerification(
                claim=f"Candidate possesses verified skill '{skill}'",
                evidence=supporting_bullet or f"Explicitly evidenced in structured skills.",
                verification_status="VERIFIED",
                confidence=conf_val,
                evidence_strength=strength
            ))
        else:
            unverified_claims.append({
                "claimed_skill": skill,
                "reason": "Not found in extracted candidate text or structured skills",
                "penalty_applied": 0.5
            })
            claim_verifications.append(ClaimVerification(
                claim=f"Candidate possesses skill '{skill}'",
                evidence="No textual evidence found in resume body.",
                verification_status="UNCONFIRMED",
                confidence=0.0,
                evidence_strength="NONE"
            ))

    score.verified_claims = claim_verifications

    # If hallucinated claims exist
    if unverified_claims:
        score.hallucination_guard_passed = False
        score.hallucination_audit = unverified_claims
        score.skills_match.matched = verified_matched

        for u in unverified_claims:
            claim = u["claimed_skill"]
            if claim not in score.skills_match.missing:
                score.skills_match.missing.append(claim)
            score.flags.append(f"Hallucination Guard: Claimed skill '{claim}' could not be verified in resume")

        # Re-adjust scores
        penalty = min(2.5, len(unverified_claims) * 0.6)
        logger.warning(f"Hallucination Guard penalizing candidate {candidate.candidate_id}: {len(unverified_claims)} unverified claims, penalty={penalty}, claims={[u['claimed_skill'] for u in unverified_claims]}")
        score.skills_match.score = max(0.0, round(score.skills_match.score - penalty, 1))

        # Recalculate overall score
        score.overall_score = max(0.0, round(
            (score.skills_match.score * 0.30) +
            (score.experience_relevance.score * 0.25) +
            ((score.evidence_score.score if score.evidence_score else 7.0) * 0.20) +
            (score.seniority_alignment.score * 0.15) +
            (score.education_fit.score * 0.10),
            1
        ))
    else:
        score.hallucination_guard_passed = True
        score.hallucination_audit = []

    return score
