import pytest
from app.normalization.taxonomy import normalize_skill, extract_explicit_skills, infer_skills_from_bullet
from app.normalization.pii_stripper import anonymize_candidate, strip_pii_from_text
from app.normalization.schema_models import CandidateData, ContactInfo, SkillItem

def test_skill_taxonomy_mapping():
    assert normalize_skill("python3") == "Python"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("react.js") == "React"

def test_bullet_skill_inference():
    bullet1 = "Led a cross-functional squad of 6 engineers to rebuild the data platform"
    inferred1 = infer_skills_from_bullet(bullet1)
    skills = [s[0] for s in inferred1]
    assert "Team Leadership" in skills
    
    bullet2 = "Optimized complex SQL queries reducing p99 response time by 40%"
    inferred2 = infer_skills_from_bullet(bullet2)
    skills2 = [s[0] for s in inferred2]
    assert "Performance Optimization" in skills2

def test_pii_stripping():
    candidate = CandidateData(
        raw_name="Sarah Connor",
        contact=ContactInfo(email="sarah@cyberdyne.com", phone="555-0199-281", location="Los Angeles, CA"),
        pii_stripped=False,
        raw_text="Sarah Connor contact at sarah@cyberdyne.com, phone 555-0199-281 in Los Angeles."
    )
    
    anonymized = anonymize_candidate(candidate, strip=True)
    assert anonymized.pii_stripped is True
    assert "Candidate #" in anonymized.anonymized_name
    assert "sarah@cyberdyne.com" not in anonymized.contact.masked_email
    assert "[EMAIL_MASKED]" in anonymized.raw_text
    assert "[PHONE_MASKED]" in anonymized.raw_text
