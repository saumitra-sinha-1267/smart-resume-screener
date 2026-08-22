import csv
import io
from fastapi import APIRouter, HTTPException, Response
from app.core import database
from app.sample_data.sample_generator import SAMPLE_JOBS, generate_sample_candidates

router = APIRouter(tags=["Export & Seed"])

def generate_csv_response(job_id: str):
    job = database.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    scores = database.get_screenings_for_job(job_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate ID", "Candidate Name", "Overall Score (0-10)", "Confidence",
        "Skills Match (0-10)", "Matched Skills", "Missing Skills",
        "Experience Relevance (0-10)", "Experience Years",
        "Seniority Alignment (0-10)", "Education Fit (0-10)",
        "Flags / Warnings", "Summary Justification"
    ])
    for idx, sc in enumerate(scores):
        cand = database.get_candidate(sc.candidate_id)
        name = cand.anonymized_name if cand else f"Candidate #{sc.candidate_id[:6]}"
        exp_yrs = cand.total_experience_years if cand else 0.0
        writer.writerow([
            idx + 1,
            sc.candidate_id,
            name,
            sc.overall_score,
            sc.confidence,
            sc.skills_match.score,
            ", ".join(sc.skills_match.matched),
            ", ".join(sc.skills_match.missing),
            sc.experience_relevance.score,
            exp_yrs,
            sc.seniority_alignment.score,
            sc.education_fit.score,
            "; ".join(sc.flags),
            sc.summary_justification
        ])
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=shortlist_{job.title.replace(' ', '_')}.csv"}
    )

@router.get("/export/{job_id}/csv")
def export_shortlist_csv_v1(job_id: str):
    return generate_csv_response(job_id)

@router.get("/export/csv/{job_id}")
def export_shortlist_csv_v2(job_id: str):
    return generate_csv_response(job_id)

@router.post("/sample-data/seed")
@router.post("/jobs/seed")
def seed_sample_data():
    for j in SAMPLE_JOBS:
        database.save_job(j)
    cands = generate_sample_candidates()
    for c in cands:
        database.save_candidate(c)
    return {
        "status": "success",
        "seeded_jobs_count": len(SAMPLE_JOBS),
        "seeded_candidates_count": len(cands),
        "message": "Successfully seeded sample jobs and resumes for instant live demo."
    }
