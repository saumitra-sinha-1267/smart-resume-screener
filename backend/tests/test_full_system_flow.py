import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_complete_recruiter_user_lifecycle_flow():
    """
    Tests the complete end-to-end recruiter workflow:
    1. Upload Resume (Multipart TXT)
    2. Extract Resume & PII Anonymization
    3. Analyze / Parse Job Description via AI
    4. Create Job Position
    5. Screen Candidate against Job Position
    6. Calculate 5-Dimension Score & Hard/Soft Separation
    7. Verify Evidence & Hallucination Guard
    8. Calculate Multi-Factor Confidence
    9. Inspect Candidate Profile Dossier & Reveal PII (Audit logged)
    10. Compare Candidates Side-by-Side
    11. Update Candidate Status (Shortlist -> Interview)
    12. Add Recruiter Notes
    13. Verify Tamper-Evident Audit Trail
    """

    # 1 & 2. Upload & Extract Resume
    sample_resume = """
    Johnathan Davis
    john.davis@cloudsystems.io | (555) 345-6789 | Austin, TX
    GitHub: https://github.com/jdavis-cloud
    
    Professional Summary:
    Lead Backend Engineer with 6 years of experience building cloud-native distributed microservices.
    
    Work Experience:
    Senior Software Engineer | Apex Cloud (2021 - Present)
    - Architected distributed backend services in Python and FastAPI handling 40,000 requests per second.
    - Optimized PostgreSQL query latency by 38% across 15M daily operations using partition indexes.
    - Containerized microservices using Docker and deployed on Kubernetes clusters on AWS.
    - Built asynchronous Kafka event streams reducing latency by 45%.
    
    Software Developer | DataSync Inc (2018 - 2021)
    - Developed backend RESTful APIs with Python and PostgreSQL.
    - Integrated Redis caching and automated CI/CD deployment pipelines.
    
    Education:
    B.S. in Computer Science | University of Texas at Austin
    """

    upload_file = io.BytesIO(sample_resume.encode("utf-8"))
    upload_res = client.post(
        "/api/candidates/upload",
        files=[("files", ("john_davis_resume.txt", upload_file, "text/plain"))]
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    uploaded_candidates = upload_res.json()
    assert len(uploaded_candidates) == 1
    cand = uploaded_candidates[0]
    candidate_id = cand["candidate_id"]

    # Verify PII Anonymization on list endpoint
    cands_list = client.get("/api/candidates?anonymized=true").json()
    matched_cand = next((c for c in cands_list if c["candidate_id"] == candidate_id), None)
    assert matched_cand is not None
    assert matched_cand["anonymized_name"].startswith("Candidate #")
    assert matched_cand["contact"]["email"] is None or matched_cand["contact"]["masked_email"] is not None

    # 3. Analyze Job Description
    raw_jd = """
    Job Title: Staff Infrastructure Engineer
    Department: Platform
    Seniority: Senior
    Minimum Experience: 5+ years
    
    Required:
    - 5+ years of experience with Python, FastAPI, and PostgreSQL.
    - Deep hands-on experience with Docker, Kubernetes, and Microservices.
    
    Preferred:
    - Experience with Kafka, Redis, and AWS.
    """

    parse_res = client.post("/api/jobs/parse", json={"raw_description": raw_jd})
    assert parse_res.status_code == 200
    parsed_jd = parse_res.json()
    assert "Python" in parsed_jd["required_skills"]
    assert "FastAPI" in parsed_jd["required_skills"]
    assert "PostgreSQL" in parsed_jd["required_skills"]

    # 4. Create Job
    create_job_res = client.post("/api/jobs", json=parsed_jd)
    assert create_job_res.status_code == 200
    job = create_job_res.json()
    job_id = job["job_id"]

    # 5, 6, 7, 8. Screen Candidate & Multi-Dimension Scoring
    screen_res = client.post(f"/api/screen/{job_id}?top_n=10")
    assert screen_res.status_code == 200
    screened_list = screen_res.json()
    assert len(screened_list) >= 1

    our_result = next((r for r in screened_list if r["candidate"]["candidate_id"] == candidate_id), None)
    assert our_result is not None
    score = our_result["score"]

    # Assert 5-Dimension scoring & Hard criteria
    assert score["overall_score"] >= 7.0
    assert score["hard_requirements_passed"] is True
    assert score["hard_requirements_score"] >= 7.0
    assert score["skills_match"]["score"] >= 7.0
    assert score["experience_relevance"]["score"] >= 7.0
    assert score["confidence"] in ["High", "Medium"]
    assert score["hallucination_guard_passed"] is True
    assert len(score["requirement_matches"]) >= 3

    # 9. Inspect Candidate Profile & Reveal PII
    reveal_res = client.get(f"/api/candidates/{candidate_id}/reveal")
    assert reveal_res.status_code == 200
    revealed = reveal_res.json()
    assert revealed["raw_name"] == "Johnathan Davis"
    assert revealed["contact"]["email"] == "john.davis@cloudsystems.io"

    # 10. Compare Candidates
    compare_res = client.post(
        "/api/candidates/compare",
        json={"candidate_ids": [candidate_id], "job_id": job_id}
    )
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert len(comp_data["candidates"]) == 1
    assert comp_data["recommendation"] != ""

    # 11. Update Candidate Status: Shortlist -> Interview
    status_shortlist = client.patch(
        f"/api/candidates/{candidate_id}/status",
        json={"status": "SHORTLISTED"}
    )
    assert status_shortlist.status_code == 200
    assert status_shortlist.json()["status"] == "SHORTLISTED"

    status_interview = client.patch(
        f"/api/candidates/{candidate_id}/status",
        json={"status": "INTERVIEW"}
    )
    assert status_interview.status_code == 200
    assert status_interview.json()["status"] == "INTERVIEW"

    # 12. Add Recruiter Note
    note_res = client.post(
        f"/api/candidates/{candidate_id}/notes",
        json={"text": "Candidate excelled at distributed systems round. Approved for Offer.", "author": "Hiring Manager"}
    )
    assert note_res.status_code == 200
    notes = note_res.json()["recruiter_notes"]
    assert len(notes) >= 1
    assert "Approved for Offer" in notes[-1]["text"]

    # 13. Verify Audit Trail
    audit_res = client.get(f"/api/audit-logs?candidate_id={candidate_id}")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 3
    event_types = [l["event_type"] for l in logs]
    assert "PII_REVEALED" in event_types
    assert "STATUS_CHANGED" in event_types
    assert "RECRUITER_NOTE_ADDED" in event_types
