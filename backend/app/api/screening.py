import asyncio
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from app.core import database
from app.core.config import settings
from app.core.audit import record_audit_event
from app.normalization.schema_models import ScreeningResult, ScoreOutput
from app.normalization.pii_stripper import anonymize_candidate
from app.semantic.vector_store import CandidateVectorIndex
from app.scoring.llm_scorer import score_candidate_with_llm, create_failed_score_output

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/screen", tags=["Screening"])

@router.post("/{job_id}", response_model=List[ScreeningResult])
async def run_screening_pipeline(
    job_id: str,
    top_n: int = Query(15, description="Number of pre-filtered candidates for deep LLM evaluation"),
    anonymized: bool = Query(True, description="Mask candidate PII in returned payload")
):
    job = database.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    all_candidates = database.list_candidates()
    if not all_candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidates found. Please upload resumes or seed benchmark data."
        )

    record_audit_event(
        event_type="SCREENING_STARTED",
        job_id=job_id,
        actor="Recruiter",
        details={"candidate_pool_size": len(all_candidates), "top_n": top_n}
    )

    vector_index = CandidateVectorIndex()
    prefiltered = vector_index.prefilter_top_candidates(job, all_candidates, top_n=top_n)

    async def evaluate_single_candidate(cand, rank, prefilter_score) -> ScreeningResult:
        try:
            score = await score_candidate_with_llm(cand, job)
        except Exception as e:
            logger.error(f"Unhandled error scoring candidate {cand.candidate_id}: {e}")
            score = create_failed_score_output(cand, job, str(e))

        try:
            database.save_screening(score)
            # Update candidate status to SCREENED if currently NEW
            if cand.status == "NEW":
                database.update_candidate_status(cand.candidate_id, "SCREENED")
                cand.status = "SCREENED"
        except Exception as db_err:
            logger.error(f"Failed to persist screening result for candidate {cand.candidate_id}: {db_err}")

        # Audit score
        record_audit_event(
            event_type="SCORE_CALCULATED",
            candidate_id=cand.candidate_id,
            job_id=job_id,
            actor="system",
            details={
                "overall_score": score.overall_score,
                "method": score.scoring_method,
                "confidence": score.confidence,
                "hard_passed": score.hard_requirements_passed
            }
        )

        return ScreeningResult(
            candidate=anonymize_candidate(cand, strip=anonymized),
            score=score,
            semantic_similarity_rank=rank,
            prefilter_score=prefilter_score
        )

    tasks = [
        evaluate_single_candidate(cand, idx + 1, score)
        for idx, (cand, score) in enumerate(prefiltered)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=False)
    results.sort(key=lambda r: r.score.overall_score, reverse=True)
    return results

@router.get("/{job_id}/results", response_model=List[ScreeningResult])
def get_existing_screening_results(job_id: str, anonymized: bool = Query(True)):
    job = database.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    scores = database.get_screenings_for_job(job_id)
    results: List[ScreeningResult] = []
    for idx, sc in enumerate(scores):
        cand = database.get_candidate(sc.candidate_id)
        if cand:
            results.append(ScreeningResult(
                candidate=anonymize_candidate(cand, strip=anonymized),
                score=sc,
                semantic_similarity_rank=idx + 1
            ))
    return results
