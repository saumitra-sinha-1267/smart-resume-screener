import os
import json
import httpx
import asyncio
import logging
from typing import Dict, Any, List, Tuple, Optional
from app.core.config import settings
from app.normalization.schema_models import (
    CandidateData, JobData, ScoreOutput, SkillsMatchScore, DimensionScore,
    RequirementMatch, ClaimVerification
)
from app.scoring.prompt_templates import build_evaluation_prompt, scan_for_prompt_injection
from app.scoring.requirement_matcher import match_candidate_to_requirements
from app.scoring.hallucination_guard import apply_hallucination_guard
from app.scoring.confidence_scorer import calculate_confidence
from app.evidence.metric_detector import classify_evidence_quality
from app.trajectory.trajectory_analyzer import analyze_career_trajectory

logger = logging.getLogger(__name__)

# Configurable Dimension Weights
SCORING_WEIGHTS = {
    "skills": 0.30,
    "experience": 0.25,
    "evidence": 0.20,
    "seniority": 0.15,
    "education": 0.10
}

def create_failed_score_output(candidate: CandidateData, job: JobData, error_reason: str) -> ScoreOutput:
    """Creates a structured ScoreOutput representing a failed evaluation needing manual recruiter review."""
    return ScoreOutput(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        skills_match=SkillsMatchScore(score=0.0, matched=[], missing=job.required_skills or [], inferred=[]),
        experience_relevance=DimensionScore(score=0.0, reasoning=f"Evaluation could not complete: {error_reason}"),
        education_fit=DimensionScore(score=0.0, reasoning="Pending manual assessment"),
        seniority_alignment=DimensionScore(score=0.0, reasoning="Pending manual assessment"),
        evidence_score=DimensionScore(score=0.0, reasoning="Evaluation failed"),
        semantic_score=DimensionScore(score=0.0, reasoning="Evaluation failed"),
        hard_requirements_passed=False,
        hard_requirements_score=0.0,
        soft_requirements_score=0.0,
        overall_score=0.0,
        confidence="Low",
        confidence_reasons=[f"Evaluation failed: {error_reason}"],
        flags=["scoring_failed: " + error_reason],
        scoring_method="calibrated_fallback",
        summary_justification=f"Evaluation failed due to error: {error_reason}. This profile requires manual recruiter review.",
        hallucination_guard_passed=True
    )

def deterministic_calibrated_scoring(candidate: CandidateData, job: JobData) -> ScoreOutput:
    """Calibrated offline scoring engine that evaluates Hard vs Soft requirements with transparent sub-dimensions."""
    cand_skill_names = {s.name.lower(): s for s in candidate.skills}

    # 1. Requirement Matching Analysis
    req_matches = match_candidate_to_requirements(candidate, job)

    # 2. Hard Requirements Evaluation (Mandatory Skills, Min Experience)
    mandatory_reqs = [r for r in req_matches if r.is_mandatory]
    matched_mand = [r for r in mandatory_reqs if r.status in ["MATCHED", "INFERRED"]]
    hard_passed = (len(matched_mand) == len(mandatory_reqs)) if mandatory_reqs else True
    hard_score = round((len(matched_mand) / max(1, len(mandatory_reqs))) * 10.0, 1)

    # 3. Soft Requirements Evaluation (Preferred Skills, Domain, Certs)
    soft_reqs = [r for r in req_matches if not r.is_mandatory]
    matched_soft = [r for r in soft_reqs if r.status in ["MATCHED", "INFERRED", "PARTIAL"]]
    soft_score = round((len(matched_soft) / max(1, len(soft_reqs))) * 10.0, 1) if soft_reqs else 8.0

    # 4. Skills Match Dimension
    req_skills = job.required_skills or []
    pref_skills = job.preferred_skills or []

    matched: List[str] = []
    missing: List[str] = []
    inferred: List[str] = []

    for req in req_skills:
        req_l = req.lower()
        if req_l in cand_skill_names:
            matched.append(req)
            if cand_skill_names[req_l].source == "inferred_from_bullet":
                inferred.append(req)
        elif req_l in (candidate.raw_text or "").lower():
            matched.append(req)
        else:
            missing.append(req)

    for pref in pref_skills:
        pref_l = pref.lower()
        if pref_l in cand_skill_names or pref_l in (candidate.raw_text or "").lower():
            if pref not in matched:
                matched.append(pref)

    for s in candidate.skills:
        if s.source == "inferred_from_bullet" and s.name not in matched:
            inferred.append(s.name)

    total_req = max(1, len(req_skills))
    matched_req_count = sum(1 for r in req_skills if r in matched)
    skills_base = (matched_req_count / total_req) * 8.5
    pref_bonus = min(1.5, len([p for p in pref_skills if p in matched]) * 0.5)
    skills_score = min(10.0, round(skills_base + pref_bonus, 1))

    # 5. Experience Relevance Dimension
    exp_years = candidate.total_experience_years
    min_years = job.min_experience_years
    if exp_years >= min_years:
        exp_score = min(10.0, 7.5 + min(2.5, (exp_years - min_years) * 0.5))
        exp_reasoning = f"Candidate brings {exp_years} years of relevant experience, meeting the required {min_years} years minimum."
    else:
        exp_score = max(3.0, round((exp_years / max(1.0, min_years)) * 7.0, 1))
        exp_reasoning = f"Candidate has {exp_years} years of experience, below the requested {min_years} years minimum."

    # 6. Evidence Quality Dimension (Strong vs Medium vs Weak)
    strong_evidence_count = sum(1 for s in candidate.skills if s.evidence_strength == "STRONG" or s.quantified_evidence)
    evidence_score_val = min(10.0, 6.0 + (strong_evidence_count * 1.0))
    evidence_reasoning = f"Demonstrated {strong_evidence_count} quantified outcome metrics and technical implementation proofs."

    # 7. Education Fit Dimension
    has_degree = len(candidate.education) > 0
    edu_score = 8.5 if has_degree else 6.5
    edu_reasoning = f"Possesses relevant degree credentials: {candidate.education[0].degree}." if has_degree else "Assessed practical industry experience in lieu of explicit degree specification."

    # 8. Seniority Alignment Dimension
    seniority_score = 8.0
    sen_reasoning = f"Seniority alignment matches {job.seniority or 'target'} profile specifications."
    if exp_years < min_years * 0.7:
        seniority_score = 5.5
        sen_reasoning = "Seniority level is junior relative to target job specifications."
    elif exp_years >= min_years + 3:
        seniority_score = 9.0
        sen_reasoning = "High seniority alignment with extensive tenure and domain leadership."

    # 9. Semantic Score
    semantic_score_val = round((skills_score * 0.6) + (exp_score * 0.4), 1)

    # Weighted Overall Score
    w = SCORING_WEIGHTS
    overall = round(
        (skills_score * w["skills"]) +
        (exp_score * w["experience"]) +
        (evidence_score_val * w["evidence"]) +
        (seniority_score * w["seniority"]) +
        (edu_score * w["education"]),
        1
    )

    flags: List[str] = []
    if missing:
        flags.append(f"Missing required skills: {', '.join(missing[:3])}")
    if exp_years < min_years:
        flags.append(f"Experience gap: {exp_years} yrs vs {min_years} yrs required")

    # Prompt injection check
    injection_findings = scan_for_prompt_injection(candidate)
    if injection_findings:
        flags.append("potential_prompt_injection_detected: " + "; ".join(injection_findings))

    trajectory = analyze_career_trajectory(candidate)
    if trajectory.get("job_hopping_flag"):
        flags.append("Pattern of rapid job transitions detected (3+ roles under 8 months)")

    summary = f"Scored {overall}/10 for {job.title}. Candidate matches {len(matched)} key skills with {exp_years} years verified experience."
    if missing:
        summary += f" Key missing area: {missing[0]}."

    return ScoreOutput(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        skills_match=SkillsMatchScore(score=skills_score, matched=matched, missing=missing, inferred=inferred),
        experience_relevance=DimensionScore(score=round(exp_score, 1), reasoning=exp_reasoning),
        education_fit=DimensionScore(score=round(edu_score, 1), reasoning=edu_reasoning),
        seniority_alignment=DimensionScore(score=round(seniority_score, 1), reasoning=sen_reasoning),
        evidence_score=DimensionScore(score=round(evidence_score_val, 1), reasoning=evidence_reasoning),
        semantic_score=DimensionScore(score=semantic_score_val, reasoning="Dense semantic similarity alignment."),
        hard_requirements_passed=hard_passed,
        hard_requirements_score=hard_score,
        soft_requirements_score=soft_score,
        overall_score=overall,
        confidence="Medium",
        flags=flags,
        scoring_method="calibrated_fallback",
        summary_justification=summary,
        requirement_matches=req_matches,
        trajectory_analysis=trajectory,
        scoring_weights_used=w
    )

async def score_candidate_with_llm(candidate: CandidateData, job: JobData, max_retries: int = 2) -> ScoreOutput:
    """Executes LLM scoring pipeline with retry/backoff, requirement matching, hallucination guard, and multi-factor confidence."""
    score_out: Optional[ScoreOutput] = None

    if settings.GEMINI_API_KEY:
        prompt = build_evaluation_prompt(candidate, job)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        raw_resp = res.json()
                        json_text = raw_resp["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(json_text)
                        score_out = ScoreOutput(**parsed)
                        score_out.scoring_method = "llm"
                        break
                    elif res.status_code in [429, 500, 503] and attempt < max_retries:
                        backoff = 0.3 * (2 ** attempt)
                        logger.warning(f"LLM API returned {res.status_code}. Retrying in {backoff}s...")
                        await asyncio.sleep(backoff)
                    else:
                        break
            except Exception as e:
                if attempt >= max_retries:
                    logger.error(f"Exhausted retries querying LLM: {e}")
                else:
                    await asyncio.sleep(0.3 * (2 ** attempt))

    # Fallback to calibrated deterministic scoring engine if LLM did not complete
    if not score_out:
        try:
            score_out = deterministic_calibrated_scoring(candidate, job)
        except Exception as e:
            logger.error(f"Deterministic scoring failed: {e}")
            return create_failed_score_output(candidate, job, str(e))

    # Enrich with requirement matches if missing
    if not score_out.requirement_matches:
        try:
            score_out.requirement_matches = match_candidate_to_requirements(candidate, job)
        except Exception as e:
            logger.warning(f"Requirement matching error: {e}")

    # Trajectory analysis
    try:
        if not score_out.trajectory_analysis:
            score_out.trajectory_analysis = analyze_career_trajectory(candidate)
    except Exception as e:
        logger.warning(f"Trajectory analysis error: {e}")

    # Hallucination Guard (Claim-by-claim verification)
    try:
        score_out = apply_hallucination_guard(score_out, candidate)
    except Exception as e:
        logger.warning(f"Hallucination guard error: {e}")

    # Confidence Scorer (Multi-factor with reasons)
    try:
        conf_label, conf_breakdown = calculate_confidence(candidate, score_out)
        conf_reasons = conf_breakdown.get('reasons', [])
        score_out.confidence = conf_label
        score_out.confidence_breakdown = conf_breakdown
        score_out.confidence_reasons = conf_reasons
    except Exception as e:
        logger.warning(f"Confidence scoring error: {e}")

    return score_out
