import re
from typing import Dict, List

SECTION_KEYWORDS = {
    "CONTACT": [r"contact(\s+information|\s+details)?", r"personal\s+info", r"get\s+in\s+touch"],
    "SUMMARY": [r"summary", r"professional\s+summary", r"profile", r"executive\s+summary", r"about(\s+me)?", r"objective"],
    "SKILLS": [r"technical\s+skills", r"skills(\s+&\s+competencies)?", r"core\s+competencies", r"tech\s+stack", r"tools(\s+&\s+technologies)?", r"technologies", r"areas\s+of\s+expertise"],
    "EXPERIENCE": [r"work\s+experience", r"professional\s+experience", r"employment\s+history", r"experience", r"work\s+history", r"career\s+history"],
    "EDUCATION": [r"education", r"academic\s+background", r"qualifications", r"degrees", r"academic\s+credentials"],
    "PROJECTS": [r"projects", r"key\s+projects", r"personal\s+projects", r"open\s+source\s+projects", r"featured\s+work"],
    "CERTIFICATIONS": [r"certifications", r"certificates", r"licenses", r"awards(\s+&\s+honors)?", r"achievements"]
}

def split_sections(text: str) -> Dict[str, str]:
    if not text:
        return {}
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {
        "HEADER": [],
        "CONTACT": [],
        "SUMMARY": [],
        "SKILLS": [],
        "EXPERIENCE": [],
        "EDUCATION": [],
        "PROJECTS": [],
        "CERTIFICATIONS": []
    }
    current_section = "HEADER"
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        matched_section = None
        if len(stripped.split()) <= 5 and len(stripped) <= 40:
            for sec_name, patterns in SECTION_KEYWORDS.items():
                for pat in patterns:
                    if re.match(r"^(" + pat + r")[:\s]*$", stripped, re.IGNORECASE):
                        matched_section = sec_name
                        break
                if matched_section:
                    break
        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(stripped)
    result: Dict[str, str] = {}
    for k, v in sections.items():
        if v:
            result[k] = "\n".join(v)
    return result
