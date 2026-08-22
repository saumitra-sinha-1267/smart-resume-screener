import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.evidence.metric_detector import analyze_bullet_metrics, enrich_candidate_with_evidence
from app.evidence.link_checker import check_url_liveness, verify_candidate_links
from app.normalization.schema_models import CandidateData, ExperienceItem, SkillItem, ExternalLinkItem

def test_metric_detection():
    b1 = "Reduced API latency by 45% across 20M requests"
    res1 = analyze_bullet_metrics(b1)
    assert res1["is_quantified"] is True
    assert len(res1["metrics"]) >= 2  # percentage + scale

    b2 = "Worked on database maintenance and general tasks"
    res2 = analyze_bullet_metrics(b2)
    assert res2["is_quantified"] is False

def test_enrich_candidate_evidence():
    candidate = CandidateData(
        skills=[SkillItem(name="PostgreSQL", source="explicit_list", quantified_evidence=False)],
        experience=[
            ExperienceItem(
                title="Backend Engineer",
                bullets=["Optimized PostgreSQL database cutting query latency by 50% for 5M users."]
            )
        ]
    )
    enriched = enrich_candidate_with_evidence(candidate)
    assert enriched.skills[0].quantified_evidence is True

def test_link_checker_github_rate_limit_handling():
    # Verify that a 403 or 429 response results in verified=None rather than False (not dead)
    mock_res = MagicMock()
    mock_res.status_code = 429

    with patch("httpx.AsyncClient.get", return_value=mock_res):
        link = ExternalLinkItem(url="https://github.com/torvalds", link_type="github")
        checked = asyncio.run(check_url_liveness(link))
        assert checked.verified is None
        assert checked.status_code == 429
        assert checked.metadata.get("rate_limited") is True

def test_link_checker_github_success():
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "stargazers_count": 150000,
        "language": "C",
        "pushed_at": "2026-08-01T12:00:00Z"
    }
    with patch("httpx.AsyncClient.get", return_value=mock_res):
        link = ExternalLinkItem(url="https://github.com/torvalds/linux", link_type="github")
        checked = asyncio.run(check_url_liveness(link))
        assert checked.verified is True
        assert checked.status_code == 200
        assert checked.metadata.get("stars") == 150000


def test_ssrf_filter_blocks_private_and_metadata_ips():
    import asyncio
    from app.evidence.link_checker import is_safe_external_url, check_url_liveness

    # 1. Cloud metadata
    is_safe, _ = is_safe_external_url("http://169.254.169.254/latest/meta-data/")
    assert is_safe is False

    # 2. Localhost
    is_safe_local, _ = is_safe_external_url("http://localhost:8000/api/candidates")
    assert is_safe_local is False

    # 3. Loopback IP
    is_safe_loop, _ = is_safe_external_url("http://127.0.0.1:5000/secret")
    assert is_safe_loop is False

    # 4. Check url liveness returns blocked without network call
    link = ExternalLinkItem(url="http://169.254.169.254/secret")
    checked = asyncio.run(check_url_liveness(link))
    assert checked.verified is False
    assert checked.metadata.get("blocked") is True
