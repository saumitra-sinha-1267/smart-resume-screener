from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from app.core import database
from app.core.audit import record_audit_event
from app.normalization.schema_models import JobData
from app.extraction.jd_parser import parse_job_description_text
from app.sample_data.sample_generator import SAMPLE_JOBS

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class ParseJobRequest(BaseModel):
    raw_description: str
    title: Optional[str] = None

@router.get("", response_model=List[JobData])
def list_jobs():
    jobs = database.list_jobs()
    if not jobs:
        for sj in SAMPLE_JOBS:
            database.save_job(sj)
        jobs = database.list_jobs()
    return jobs

@router.get("/{job_id}", response_model=JobData)
def get_job(job_id: str):
    job = database.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return job

@router.post("/parse", response_model=JobData)
def parse_job_description_endpoint(req: ParseJobRequest):
    """Converts a raw unstructured job description into structured requirements for recruiter review/editing."""
    if not req.raw_description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="raw_description cannot be empty")
    parsed_job = parse_job_description_text(req.raw_description, custom_title=req.title)
    record_audit_event(
        event_type="JOB_DESCRIPTION_PARSED",
        job_id=parsed_job.job_id,
        actor="Recruiter",
        details={"title": parsed_job.title, "requirements_count": len(parsed_job.requirements)}
    )
    return parsed_job

@router.post("", response_model=JobData)
def create_job(job: JobData):
    """Creates or updates a job opening with structured criteria."""
    # If requirements empty but raw_description present, auto-parse
    if not job.requirements and job.raw_description:
        parsed = parse_job_description_text(job.raw_description, custom_title=job.title)
        job.requirements = parsed.requirements
        if not job.required_skills:
            job.required_skills = parsed.required_skills
        if not job.preferred_skills:
            job.preferred_skills = parsed.preferred_skills
        if not job.mandatory_requirements:
            job.mandatory_requirements = parsed.mandatory_requirements
        if not job.preferred_requirements:
            job.preferred_requirements = parsed.preferred_requirements

    database.save_job(job)
    record_audit_event(
        event_type="JOB_CREATED",
        job_id=job.job_id,
        actor="Recruiter",
        details={"title": job.title, "department": job.department, "min_exp": job.min_experience_years}
    )
    return job
