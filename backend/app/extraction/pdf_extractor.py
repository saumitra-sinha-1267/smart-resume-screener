import re
import os
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from pypdf import PdfReader
from app.extraction.section_splitter import split_sections
from app.extraction.bullet_chunker import split_into_bullets
from app.normalization.taxonomy import normalize_skill, extract_explicit_skills, infer_skills_from_bullet
from app.normalization.pii_stripper import EMAIL_REGEX, PHONE_REGEX, URL_REGEX, generate_anonymized_id, mask_email, mask_phone
from app.normalization.schema_models import CandidateData, ContactInfo, SkillItem, ExperienceItem, EducationItem, ExternalLinkItem

logger = logging.getLogger(__name__)

def perform_ocr_fallback(file_path: str) -> str:
    """Attempts to convert PDF pages to images and extract text via pytesseract with graceful binary error handling."""
    ocr_text = ""
    try:
        from pdf2image import convert_from_path
        import pytesseract

        # Convert pages to images
        images = convert_from_path(file_path)
        page_texts = []
        for i, img in enumerate(images):
            try:
                page_t = pytesseract.image_to_string(img)
                if page_t.strip():
                    page_texts.append(page_t.strip())
            except Exception as tess_err:
                logger.warning(f"Tesseract OCR failed on page {i+1} of {file_path}: {tess_err}")

        ocr_text = "\n\n".join(page_texts)
    except Exception as e:
        logger.warning(f"OCR fallback via pdf2image/pytesseract unavailable or failed for {file_path}: {e}. (Ensure poppler and tesseract binaries are installed on system).")

    return ocr_text.strip()

def extract_raw_text_from_pdf(file_path: str) -> Tuple[str, bool]:
    """Extracts raw text from PDF and falls back to OCR if text content is near-empty (<50 chars)."""
    raw_text = ""
    is_scanned = False
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            t = page.extract_text() or ""
            raw_text += t + "\n"
    except Exception as e:
        logger.warning(f"Error reading PDF {file_path} with PdfReader: {e}")
        raw_text = ""

    # Scanned PDF check (< 50 chars)
    if len(raw_text.strip()) < 50:
        is_scanned = True
        ocr_result = perform_ocr_fallback(file_path)
        if ocr_result:
            raw_text = ocr_result
        else:
            raw_text = f"[Scanned Resume: {os.path.basename(file_path)} - OCR binary not present on host]"

    return raw_text.strip(), is_scanned

def parse_contact_info(text: str) -> ContactInfo:
    email_match = re.search(EMAIL_REGEX, text)
    phone_match = re.search(PHONE_REGEX, text)
    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0) if phone_match else None
    return ContactInfo(
        email=email,
        phone=phone,
        masked_email=mask_email(email) if email else None,
        masked_phone=mask_phone(phone) if phone else None,
        location=None,
        masked_location="[LOCATION_MASKED]"
    )

def parse_external_links(text: str) -> List[ExternalLinkItem]:
    found_urls = re.findall(URL_REGEX, text)
    links: List[ExternalLinkItem] = []
    seen = set()
    for u in found_urls:
        u_clean = u.rstrip(".,;)")
        if u_clean.startswith("http") or "github.com" in u_clean or "linkedin.com" in u_clean:
            if not u_clean.startswith("http"):
                u_clean = "https://" + u_clean
            if u_clean not in seen:
                seen.add(u_clean)
                l_type = "other"
                if "github.com" in u_clean:
                    l_type = "github"
                elif "linkedin.com" in u_clean:
                    l_type = "linkedin"
                links.append(ExternalLinkItem(url=u_clean, link_type=l_type, verified=False))
    return links

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

def parse_date_str(d_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Returns (year, month) from date string."""
    if not d_str:
        return None, None
    s = d_str.strip().lower()
    yr = None
    mo = None
    
    m_yr = re.search(r"\b(19|20\d{2})\b", s)
    if m_yr:
        yr = int(m_yr.group(0))
        
    for m_name, m_num in MONTH_MAP.items():
        if re.search(r"\b" + m_name + r"\b", s):
            mo = m_num
            break
    if not mo:
        # Check digit month e.g. 06/2023
        m_dig = re.search(r"\b(0?[1-9]|1[0-2])[\/\.-]\b", s)
        if m_dig:
            mo = int(m_dig.group(1))
            
    return yr, mo

def calculate_duration_years(start_str: str, end_str: str) -> float:
    """Calculates realistic tenure duration in years from start and end dates."""
    start_yr, start_mo = parse_date_str(start_str)
    if not start_yr:
        return 0.0

    is_present = any(p in (end_str or "").lower() for p in ["present", "current", "now", "ongoing"])
    if is_present:
        end_yr, end_mo = 2026, 8
    else:
        end_yr, end_mo = parse_date_str(end_str)
        if not end_yr:
            end_yr = start_yr
            end_mo = start_mo or 12

    if start_mo and end_mo:
        months = (end_yr - start_yr) * 12 + (end_mo - start_mo) + 1
        return max(0.1, round(months / 12.0, 1))
    else:
        if end_yr > start_yr:
            return round(float(end_yr - start_yr), 1)
        elif end_yr == start_yr:
            return 0.5
        else:
            return 0.0

def parse_experience_blocks(exp_text: str) -> List[ExperienceItem]:
    if not exp_text or len(exp_text.strip()) < 10:
        return []
    items: List[ExperienceItem] = []
    lines = [l.strip() for l in exp_text.splitlines() if l.strip()]
    current_title = "Experience Role"
    current_company = "Organization"
    current_start = ""
    current_end = ""
    current_bullets_text = []
    date_pat = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|\d{1,2})?\s*[\/\.-]?\s*\b(19|20)\d{2}\b)\s*(?:-|–|—|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|\d{1,2})?\s*[\/\.-]?\s*\b(19|20)\d{2}\b|Present|Current|Now)"

    for line in lines:
        d_match = re.search(date_pat, line, re.IGNORECASE)
        if d_match:
            if current_bullets_text or current_start:
                bullets = split_into_bullets("\n".join(current_bullets_text)) if current_bullets_text else []
                skills = []
                for b in bullets:
                    skills.extend(extract_explicit_skills(b))
                items.append(ExperienceItem(
                    title=current_title,
                    company=current_company,
                    start_date=current_start or "Unspecified",
                    end_date=current_end or "Unspecified",
                    bullets=bullets,
                    extracted_skills=sorted(list(set(skills)))
                ))
                current_bullets_text = []
            line_without_date = re.sub(date_pat, "", line, flags=re.IGNORECASE).strip()
            parts = [p.strip() for p in re.split(r"[|•\-@,]", line_without_date) if p.strip()]
            if parts:
                current_title = parts[0]
                current_company = parts[1] if len(parts) > 1 else "Organization"
            else:
                current_title = "Role"
                current_company = "Organization"
            current_start = d_match.group(1).strip()
            current_end = d_match.group(3).strip()
        else:
            current_bullets_text.append(line)

    if current_bullets_text or current_start:
        bullets = split_into_bullets("\n".join(current_bullets_text)) if current_bullets_text else []
        skills = []
        for b in bullets:
            skills.extend(extract_explicit_skills(b))
        items.append(ExperienceItem(
            title=current_title,
            company=current_company,
            start_date=current_start or "Unspecified",
            end_date=current_end or "Unspecified",
            bullets=bullets,
            extracted_skills=sorted(list(set(skills)))
        ))
    return items

def parse_education_blocks(edu_text: str) -> List[EducationItem]:
    if not edu_text:
        return []
    items: List[EducationItem] = []
    lines = edu_text.splitlines()
    degree_pats = [r"B\.?S\.?|B\.?Tech|B\.?E\.?|Bachelor|Master|M\.?S\.?|M\.?Tech|Ph\.?D|Associate|Diploma"]
    for line in lines:
        for p in degree_pats:
            if re.search(p, line, re.IGNORECASE):
                items.append(EducationItem(degree=line.strip(), year_masked=True))
                break
    if not items and edu_text:
        items.append(EducationItem(degree=edu_text.splitlines()[0][:60], year_masked=True))
    return items

def parse_resume_to_candidate(raw_text: str, filename: str = "") -> CandidateData:
    candidate_id = str(uuid.uuid4())
    sections = split_sections(raw_text)
    header_text = sections.get("HEADER", "")
    lines = [l.strip() for l in header_text.splitlines() if l.strip()]
    raw_name = lines[0] if lines and len(lines[0].split()) <= 4 else os.path.splitext(filename)[0]
    anonymized_name = generate_anonymized_id(raw_name, candidate_id)
    contact = parse_contact_info(raw_text)
    links = parse_external_links(raw_text)
    experience = parse_experience_blocks(sections.get("EXPERIENCE", ""))
    education = parse_education_blocks(sections.get("EDUCATION", ""))

    skills_map: Dict[str, SkillItem] = {}
    skills_text = sections.get("SKILLS", "")
    explicit_skills = extract_explicit_skills(skills_text)
    for s in explicit_skills:
        skills_map[s] = SkillItem(name=s, source="explicit_list", quantified_evidence=False)

    for exp in experience:
        for b in exp.bullets:
            exp_s = extract_explicit_skills(b)
            for s in exp_s:
                if s not in skills_map or skills_map[s].source == "inferred_from_bullet":
                    skills_map[s] = SkillItem(name=s, source="experience_mention", original_text=b, quantified_evidence=False)
            inferred = infer_skills_from_bullet(b)
            for inf_s, reason in inferred:
                if inf_s not in skills_map:
                    skills_map[inf_s] = SkillItem(
                        name=inf_s,
                        source="inferred_from_bullet",
                        original_text=b,
                        quantified_evidence=False
                    )

    # Calculate strictly verified experience years (0.0 if no verified dates)
    total_years = 0.0
    for exp in experience:
        if exp.start_date and exp.start_date != "Unspecified":
            dur = calculate_duration_years(exp.start_date, exp.end_date)
            total_years += dur

    total_exp = round(total_years, 1)

    return CandidateData(
        candidate_id=candidate_id,
        raw_name=raw_name,
        anonymized_name=anonymized_name,
        contact=contact,
        pii_stripped=True,
        skills=list(skills_map.values()),
        experience=experience,
        education=education,
        external_links=links,
        total_experience_years=total_exp,
        raw_text=raw_text
    )
