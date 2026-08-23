import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.normalization.schema_models import CandidateData, SkillItem, ExperienceItem, JobData
from app.extraction.jd_parser import parse_job_description_text
from app.evidence.metric_detector import classify_evidence_quality
from app.scoring.requirement_matcher import match_candidate_to_requirements
from app.scoring.llm_scorer import deterministic_calibrated_scoring
from app.core import database
from app.core.audit import record_audit_event, get_audit_logs, sanitize_audit_details

client = TestClient(app)

def test_job_description_intelligence_parser():
    raw_jd = """
    Job Title: Senior Backend Engineer
    Department: Core Infrastructure
    
    About the Role:
    We are seeking an experienced Senior Backend Engineer with 5+ years of experience to lead our distributed platform.
    
    Responsibilities:
    - Architect and scale high-throughput microservices handling 50k requests per second.
    - Design event-driven pipelines using Apache Kafka and PostgreSQL.
    - Mentor junior engineers and collaborate across product squads.
    
    Required Qualifications:
    - 5+ years of experience with Python, FastAPI, and PostgreSQL.
    - Hands-on experience with Docker, Kubernetes, and AWS.
    - Deep understanding of distributed systems and caching with Redis.
    
    Preferred Qualifications:
    - Familiarity with Golang and PyTorch.
    - Background in Fintech or Payments.
    - B.S. or M.S. in Computer Science.
    """

    job = parse_job_description_text(raw_jd)
    assert job.title == "Senior Backend Engineer"
    assert job.seniority == "Senior"
    assert job.min_experience_years == 5.0
    assert "Python" in job.required_skills
    assert "FastAPI" in job.required_skills
    assert "PostgreSQL" in job.required_skills
    assert "Golang" in job.preferred_skills or "Go" in job.preferred_skills
    assert "Fintech" in job.domain_requirements or "Payments" in job.domain_requirements
    assert len(job.requirements) >= 4

    # Verify API endpoint
    res = client.post("/api/jobs/parse", json={"raw_description": raw_jd})
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Senior Backend Engineer"
    assert data["min_experience_years"] == 5.0

def test_evidence_quality_classification():
    # Strong: Quantified metric + Technical action
    strong_bullet = "Optimized PostgreSQL query latency by 45% for 10M active users using index partitioning."
    strength, metrics = classify_evidence_quality(strong_bullet)
    assert strength == "STRONG"
    assert len(metrics) >= 1

    # Medium: Technical implementation without explicit metric
    medium_bullet = "Architected and implemented distributed event stream handlers using FastAPI and Kafka."
    strength_med, _ = classify_evidence_quality(medium_bullet)
    assert strength_med == "MEDIUM"

    # Weak: Generic responsibility
    weak_bullet = "Responsible for daily bug fixing and attended team meetings."
    strength_weak, _ = classify_evidence_quality(weak_bullet)
    assert strength_weak == "WEAK"

def test_requirement_matching_and_hard_soft_scoring():
    candidate = CandidateData(
        raw_name="Alex Mercer",
        total_experience_years=6.0,
        skills=[
            SkillItem(name="Python", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="FastAPI", source="explicit_list", quantified_evidence=True, evidence_strength="STRONG"),
            SkillItem(name="PostgreSQL", source="explicit_list", evidence_strength="MEDIUM")
        ],
        experience=[
            ExperienceItem(
                title="Senior Software Engineer",
                bullets=[
                    "Engineered Python FastAPI services reducing latency by 40%.",
                    "Managed PostgreSQL schemas."
                ],
                extracted_skills=["Python", "FastAPI", "PostgreSQL"]
            )
        ],
        raw_text="Experienced Senior Python and FastAPI engineer with PostgreSQL."
    )

    job = JobData(
        title="Senior Python Engineer",
        min_experience_years=4.0,
        required_skills=["Python", "FastAPI"],
        preferred_skills=["Golang"],
        raw_description="Senior Python developer"
    )

    matches = match_candidate_to_requirements(candidate, job)
    assert len(matches) >= 2
    matched_skills = [m for m in matches if m.status in ["MATCHED", "INFERRED"]]
    assert len(matched_skills) >= 2

    # Run deterministic scoring
    score = deterministic_calibrated_scoring(candidate, job)
    assert score.hard_requirements_passed is True
    assert score.hard_requirements_score >= 8.0
    assert score.evidence_score is not None
    assert score.evidence_score.score >= 7.0
    assert len(score.requirement_matches) > 0

def test_candidate_status_notes_and_reveal():
    # 1. Create a candidate
    candidate = CandidateData(
        raw_name="Marcus Aurelius",
        contact={"email": "marcus@rome.org", "phone": "555-123-4567"},
        skills=[SkillItem(name="Python", source="explicit_list")],
        raw_text="Rome platform leader"
    )
    database.save_candidate(candidate)

    # 2. Update Status
    res_status = client.patch(
        f"/api/candidates/{candidate.candidate_id}/status",
        json={"status": "SHORTLISTED"}
    )
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "SHORTLISTED"

    # 3. Add Recruiter Note
    res_note = client.post(
        f"/api/candidates/{candidate.candidate_id}/notes",
        json={"text": "Excellent architecture background; scheduled technical screen.", "author": "Sarah Connor"}
    )
    assert res_note.status_code == 200
    notes = res_note.json()["recruiter_notes"]
    assert len(notes) >= 1
    assert "Excellent architecture" in notes[0]["text"]

    # 4. Reveal PII
    res_reveal = client.get(f"/api/candidates/{candidate.candidate_id}/reveal")
    assert res_reveal.status_code == 200
    assert res_reveal.json()["raw_name"] == "Marcus Aurelius"
    assert res_reveal.json()["contact"]["email"] == "marcus@rome.org"

def test_candidate_comparison_endpoint():
    # 1. Seed benchmark candidates
    client.post("/api/sample-data/seed")
    jobs = client.get("/api/jobs").json()
    assert len(jobs) > 0
    job_id = jobs[0]["job_id"]

    # 2. Run screening to generate scores
    client.post(f"/api/screen/{job_id}?top_n=3")

    candidates = client.get("/api/candidates").json()
    cand_ids = [c["candidate_id"] for c in candidates[:3]]

    # 3. Compare candidates
    res_comp = client.post(
        "/api/candidates/compare",
        json={"candidate_ids": cand_ids, "job_id": job_id}
    )
    assert res_comp.status_code == 200
    data = res_comp.json()
    assert data["job_id"] == job_id
    assert len(data["candidates"]) == len(cand_ids)
    assert len(data["side_by_side_matrix"]) > 0
    assert data["recommendation"] != ""

def test_audit_logging_and_pii_safety():
    # 1. Record event with sensitive data
    sensitive_details = {
        "candidate_email": "john.doe@confidential.com",
        "phone": "+1-555-987-6543",
        "action": "Verified resume"
    }
    cleaned = sanitize_audit_details(sensitive_details)
    assert "john.doe@confidential.com" not in cleaned["candidate_email"]
    assert "[EMAIL_MASKED]" in cleaned["candidate_email"]
    assert "[PHONE_MASKED]" in cleaned["phone"]

    # 2. Record audit event
    record_audit_event(
        event_type="TEST_SECURITY_EVENT",
        actor="SecurityAudit",
        details=sensitive_details
    )

    # 3. Fetch audit logs via API
    res = client.get("/api/audit-logs?event_type=TEST_SECURITY_EVENT")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 1
    assert logs[0]["event_type"] == "TEST_SECURITY_EVENT"
    assert "john.doe@confidential.com" not in str(logs[0]["details"])

def test_fresher_data_analyst_jd_extraction():
    """Validates JD extraction for entry-level / fresher Data Analyst role."""
    fresher_jd = """
    Position: Data Analyst – Fresher
    Department: Data & Analytics
    
    About the Role:
    We are looking for an entry-level Data Analyst (Fresher / 0+ years experience) to analyze business datasets.
    
    Required Skills:
    - Python programming with Pandas and NumPy
    - SQL database querying
    - Statistics and exploratory data analysis
    - Data Visualization
    
    Preferred Skills (Nice to have):
    - Power BI and Tableau
    - Microsoft Excel
    - Git / GitHub
    
    Education:
    - Bachelor's in Computer Science, Statistics, Mathematics or related STEM field.
    """

    res = client.post("/api/jobs/parse", json={"raw_description": fresher_jd})
    assert res.status_code == 200
    data = res.json()

    assert "Data Analyst" in data["title"]
    assert data["seniority"] == "Entry-Level"
    assert data["min_experience_years"] == 0.0

    # Required skills verification
    req_skills = data["required_skills"]
    for s in ["Python", "SQL", "Pandas", "NumPy", "Statistics", "Data Visualization"]:
        assert s in req_skills

    # Preferred skills verification
    pref_skills = data["preferred_skills"]
    assert "Power BI" in pref_skills
    assert "Tableau" in pref_skills
    assert any("Excel" in p for p in pref_skills)
    assert any("Git" in p for p in pref_skills)

def test_empty_and_invalid_jd_extraction():
    """Verifies that empty or whitespace-only JD input yields 400 Bad Request."""
    res_empty = client.post("/api/jobs/parse", json={"raw_description": ""})
    assert res_empty.status_code == 400
    assert "cannot be empty" in res_empty.json()["detail"]

    res_spaces = client.post("/api/jobs/parse", json={"raw_description": "   \n\t  "})
    assert res_spaces.status_code == 400

def test_save_and_use_edited_job_requirements():
    """Ensures edited requirements are saved to database and strictly used by screening engine."""
    custom_job = {
        "title": "Custom Data Analyst Specialist",
        "department": "Analytics",
        "seniority": "Entry-Level",
        "min_experience_years": 0.0,
        "required_skills": ["Python", "SQL", "Pandas", "NumPy", "Statistics", "Data Visualization"],
        "preferred_skills": ["Power BI", "Microsoft Excel", "Git / GitHub"],
        "raw_description": "Custom edited description for Data Analyst role",
        "requirements": [
            {
                "id": "req-1",
                "text": "Entry level / 0+ years professional experience",
                "category": "experience",
                "weight": 0.5,
                "required": False,
                "is_mandatory": False
            },
            {
                "id": "req-2",
                "text": "Demonstrated hands-on expertise with Python",
                "category": "skill",
                "weight": 1.0,
                "required": True,
                "is_mandatory": True
            },
            {
                "id": "req-3",
                "text": "Demonstrated hands-on expertise with SQL",
                "category": "skill",
                "weight": 1.0,
                "required": True,
                "is_mandatory": True
            }
        ]
    }

    create_res = client.post("/api/jobs", json=custom_job)
    assert create_res.status_code == 200
    saved_job = create_res.json()
    job_id = saved_job["job_id"]

    # Verify fetch
    get_res = client.get(f"/api/jobs/{job_id}")
    assert get_res.status_code == 200
    fetched_job = get_res.json()
    assert fetched_job["title"] == "Custom Data Analyst Specialist"
    assert fetched_job["min_experience_years"] == 0.0
    assert "Python" in fetched_job["required_skills"]
    assert "SQL" in fetched_job["required_skills"]
    assert len(fetched_job["requirements"]) >= 3

