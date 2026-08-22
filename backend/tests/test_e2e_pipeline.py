import pytest
from app.sample_data.sample_generator import SAMPLE_JOBS, generate_sample_candidates
from app.semantic.vector_store import CandidateVectorIndex
from app.scoring.llm_scorer import deterministic_calibrated_scoring

def test_end_to_end_screening_ranking():
    job = SAMPLE_JOBS[0] # Senior Backend Engineer
    candidates = generate_sample_candidates()
    
    # 1. Vector Pre-filter
    v_index = CandidateVectorIndex()
    prefiltered = v_index.prefilter_top_candidates(job, candidates, top_n=5)
    assert len(prefiltered) == len(candidates)
    
    # Top prefiltered candidate should be the Senior Backend candidate (Alex Mercer)
    top_cand, top_score = prefiltered[0]
    assert top_cand.candidate_id == "cand-alex-001"
    
    # 2. Score Candidates
    scored_list = []
    for cand, pref_sc in prefiltered:
        score = deterministic_calibrated_scoring(cand, job)
        scored_list.append((cand, score))
        
    scored_list.sort(key=lambda x: x[1].overall_score, reverse=True)
    
    # Senior Backend candidate should rank highest
    best_candidate, best_score = scored_list[0]
    assert best_candidate.candidate_id == "cand-alex-001"
    assert best_score.overall_score >= 8.0
    assert "Python" in best_score.skills_match.matched
    assert "PostgreSQL" in best_score.skills_match.matched


def test_idempotent_rescreening():
    import asyncio
    from app.core import database
    from app.sample_data.sample_generator import SAMPLE_JOBS, generate_sample_candidates
    from app.api.screening import run_screening_pipeline

    # Ensure sample data loaded
    job = SAMPLE_JOBS[0]
    database.save_job(job)
    candidates = generate_sample_candidates()
    for c in candidates:
        database.save_candidate(c)

    # First screening run
    res1 = asyncio.run(run_screening_pipeline(job.job_id, top_n=5, anonymized=True))
    count1 = len(database.get_screenings_for_job(job.job_id))

    # Second screening run (same job)
    res2 = asyncio.run(run_screening_pipeline(job.job_id, top_n=5, anonymized=True))
    count2 = len(database.get_screenings_for_job(job.job_id))

    assert len(res1) == len(res2) == 5
    assert count1 == count2  # No duplicate rows created in database
