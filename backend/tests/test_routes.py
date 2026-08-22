import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "dense_embeddings" in data["features"]

def test_seed_and_export_endpoints():
    # 1. Seed demo data
    res_seed = client.post("/api/sample-data/seed")
    assert res_seed.status_code == 200
    assert res_seed.json()["status"] == "success"

    # Also test /api/jobs/seed alias
    res_seed_alias = client.post("/api/jobs/seed")
    assert res_seed_alias.status_code == 200

    # 2. Fetch jobs
    res_jobs = client.get("/api/jobs")
    assert res_jobs.status_code == 200
    jobs = res_jobs.json()
    assert len(jobs) > 0
    job_id = jobs[0]["job_id"]

    # 3. Export CSV endpoints (both URL styles)
    res_csv1 = client.get(f"/api/export/{job_id}/csv")
    assert res_csv1.status_code == 200
    assert "text/csv" in res_csv1.headers["content-type"]

    res_csv2 = client.get(f"/api/export/csv/{job_id}")
    assert res_csv2.status_code == 200
    assert "text/csv" in res_csv2.headers["content-type"]


def test_delete_candidate_and_lifecycle_cleanup():
    # 1. Fetch candidates
    res_cands = client.get("/api/candidates")
    assert res_cands.status_code == 200
    cands = res_cands.json()
    assert len(cands) > 0
    target_id = cands[0]["candidate_id"]

    # 2. Delete candidate
    res_del = client.delete(f"/api/candidates/{target_id}")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"

    # 3. Confirm candidate not returned
    res_cand_get = client.get(f"/api/candidates/{target_id}")
    assert res_cand_get.status_code == 404
