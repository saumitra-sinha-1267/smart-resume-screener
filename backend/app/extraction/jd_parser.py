import re
import uuid
from typing import Dict, Any, List, Optional
from app.normalization.schema_models import JobData, JobRequirement
from app.normalization.taxonomy import SKILL_SYNONYMS, extract_explicit_skills

SENIORITY_KEYWORDS = {
    "fresher": "Entry-Level",
    "intern": "Entry-Level",
    "internship": "Entry-Level",
    "entry": "Entry-Level",
    "entry-level": "Entry-Level",
    "graduate": "Entry-Level",
    "junior": "Junior",
    "associate": "Associate",
    "mid": "Mid-Level",
    "senior": "Senior",
    "sr": "Senior",
    "staff": "Staff",
    "principal": "Principal",
    "lead": "Lead",
    "manager": "Manager",
    "director": "Director",
    "head": "Head of Engineering",
    "vp": "VP of Engineering"
}

EDUCATION_PATTERNS = [
    r"\b(?:bachelor'?s?|b\.s\.?|b\.a\.?|b\.tech|b\.e\.?|master'?s?|m\.s\.?|m\.tech|ph\.?d\.?|degree)\s+(?:in|of)?\s+[a-zA-Z\s]{3,30}\b",
    r"\b(?:computer science|software engineering|information technology|electrical engineering|mathematics|data science|statistics)\b"
]

CERTIFICATION_PATTERNS = [
    r"\b(?:aws certified|azure certified|gcp certified|ckad?|cissp|pmp|comptia|scrum master|hashicorp certified)\b"
]

DOMAIN_KEYWORDS = [
    "fintech", "payments", "banking", "healthcare", "healthtech", "ecommerce", "e-commerce",
    "saas", "distributed systems", "cloud infrastructure", "cybersecurity", "ai/ml", "robotics",
    "telecom", "adtech", "gaming", "automotive", "crypto", "blockchain", "analytics", "data analytics"
]

def parse_job_description_text(raw_text: str, custom_title: Optional[str] = None) -> JobData:
    """Intelligently converts raw job description text into a rich structured JobData model with classified requirements."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return JobData(title=custom_title or "Untitled Role", raw_description=raw_text)

    # 1. Infer Title
    title = custom_title or ""
    if not title:
        # Check first line or 'Title:' label
        for line in lines[:5]:
            m = re.search(r"(?:job\s+title|role|position):\s*(.+)", line, re.IGNORECASE)
            if m:
                title = m.group(1).strip()
                break
        if not title:
            # Fallback to the first prominent line
            first_line = lines[0].strip("#* ")
            if len(first_line) < 80 and not any(w in first_line.lower() for w in ["about us", "overview", "description", "summary"]):
                title = first_line
            else:
                title = "Senior Software Engineer"

    # 2. Infer Seniority (Title takes strict precedence)
    seniority = "Mid-Senior"
    title_lower = title.lower()
    for kw, val in SENIORITY_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", title_lower):
            seniority = val
            break

    if seniority == "Mid-Senior":
        # Check first 300 chars of body
        for kw, val in SENIORITY_KEYWORDS.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", raw_text[:300].lower()):
                seniority = val
                break

    # 3. Infer Department
    dept = "Engineering"
    if any(k in raw_text.lower() for k in ["data science", "data analyst", "data analysis", "machine learning", "ai researcher"]):
        dept = "Data & Analytics"
    elif any(k in raw_text.lower() for k in ["devops", "sre", "infrastructure", "platform engineer"]):
        dept = "Platform & Infrastructure"
    elif any(k in raw_text.lower() for k in ["product manager", "product design", "ui/ux"]):
        dept = "Product"
    elif any(k in raw_text.lower() for k in ["security engineer", "soc", "infosec"]):
        dept = "Cybersecurity"

    # 4. Infer Minimum Experience Years
    min_exp = 0.0
    is_fresher = any(re.search(r"\b" + re.escape(w) + r"\b", raw_text.lower()) for w in ["fresher", "0 years", "0-1 years", "0+ years", "0 to 1 years", "no experience", "entry level", "entry-level", "intern", "internship", "graduate"])
    if is_fresher or seniority == "Entry-Level":
        min_exp = 0.0
    else:
        exp_matches = re.findall(r"\b(\d+)(?:\s*-\s*\d+)?\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:relevant\s+)?experience\b", raw_text, re.IGNORECASE)
        if exp_matches:
            try:
                min_exp = float(exp_matches[0])
            except Exception:
                min_exp = 3.0
        else:
            # Default based on seniority
            if seniority in ["Staff", "Principal", "Director", "VP"]:
                min_exp = 8.0
            elif seniority in ["Senior", "Lead", "Manager"]:
                min_exp = 5.0
            elif seniority in ["Junior", "Associate"]:
                min_exp = 1.0
            elif seniority == "Entry-Level":
                min_exp = 0.0
            else:
                min_exp = 2.0

    # 5. Extract Skills by section (Required vs Preferred)
    raw_lower = raw_text.lower()
    req_section_text = raw_text
    pref_section_text = ""

    pref_start = -1
    for pref_hdr in ["preferred", "nice to have", "bonus", "desirable", "good to have"]:
        pos = raw_lower.find(pref_hdr)
        if pos != -1 and (pref_start == -1 or pos < pref_start):
            pref_start = pos

    if pref_start != -1:
        req_section_text = raw_text[:pref_start]
        pref_section_text = raw_text[pref_start:]

    required_skills = extract_explicit_skills(req_section_text)
    preferred_skills = [s for s in extract_explicit_skills(pref_section_text) if s not in required_skills]

    # 6. Extract Education requirements
    education_reqs = []
    for pat in EDUCATION_PATTERNS:
        for m in re.finditer(pat, raw_text, re.IGNORECASE):
            edu_str = m.group(0).strip()
            if edu_str.title() not in education_reqs:
                education_reqs.append(edu_str.title())

    # 7. Extract Certifications
    certifications = []
    for pat in CERTIFICATION_PATTERNS:
        for m in re.finditer(pat, raw_text, re.IGNORECASE):
            cert_str = m.group(0).strip().upper()
            if cert_str not in certifications:
                certifications.append(cert_str)

    # 8. Extract Domain requirements
    domains = []
    for dom in DOMAIN_KEYWORDS:
        if re.search(r"\b" + re.escape(dom) + r"\b", raw_lower):
            domains.append(dom.title())

    # 9. Extract Responsibilities bullets
    responsibilities = []
    is_resp = False
    for line in lines:
        line_clean = line.strip(" -*•")
        if any(h in line.lower() for h in ["responsibilities", "what you'll do", "what you will do", "duties", "day to day"]):
            is_resp = True
            continue
        if is_resp and (line.startswith("#") or line.endswith(":") or any(h in line.lower() for h in ["qualifications", "requirements", "about you"])):
            is_resp = False
            continue
        if is_resp and len(line_clean) > 15:
            responsibilities.append(line_clean)

    # 10. Generate structured JobRequirements list
    structured_requirements: List[JobRequirement] = []

    # Add experience requirement
    if min_exp == 0.0:
        structured_requirements.append(JobRequirement(
            text="Entry level / 0+ years professional experience",
            category="experience",
            weight=0.5,
            required=False,
            is_mandatory=False
        ))
    else:
        structured_requirements.append(JobRequirement(
            text=f"{min_exp}+ years of professional engineering experience",
            category="experience",
            weight=1.5,
            required=True,
            is_mandatory=True
        ))

    # Add mandatory skills
    mandatory_req_strings = []
    for s in required_skills:
        req_item = JobRequirement(
            text=f"Demonstrated hands-on expertise with {s}",
            category="skill",
            weight=1.0,
            required=True,
            is_mandatory=True
        )
        structured_requirements.append(req_item)
        mandatory_req_strings.append(f"Expertise in {s}")

    # Add preferred skills
    preferred_req_strings = []
    for s in preferred_skills:
        req_item = JobRequirement(
            text=f"Experience or familiarity with {s}",
            category="skill",
            weight=0.5,
            required=False,
            is_mandatory=False
        )
        structured_requirements.append(req_item)
        preferred_req_strings.append(f"Familiarity with {s}")

    # Add domain requirements if any
    for d in domains:
        req_item = JobRequirement(
            text=f"Domain background in {d}",
            category="domain",
            weight=0.8,
            required=False,
            is_mandatory=False
        )
        structured_requirements.append(req_item)
        preferred_req_strings.append(f"Domain in {d}")

    # Add education requirement if any
    if education_reqs:
        structured_requirements.append(JobRequirement(
            text=f"Academic credential or equivalent: {education_reqs[0]}",
            category="education",
            weight=0.7,
            required=False,
            is_mandatory=False
        ))

    return JobData(
        title=title,
        department=dept,
        seniority=seniority,
        min_experience_years=min_exp,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        education_requirements=education_reqs,
        certifications=certifications,
        domain_requirements=domains,
        responsibilities=responsibilities[:8],
        mandatory_requirements=mandatory_req_strings,
        preferred_requirements=preferred_req_strings,
        requirements=structured_requirements,
        raw_description=raw_text
    )
