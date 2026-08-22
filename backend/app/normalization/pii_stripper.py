import re
import hashlib
from typing import Dict, Any, Tuple, Optional, List
from app.normalization.schema_models import CandidateData, ContactInfo, ExternalLinkItem

# Email regex supporting subdomains, + tags, uk/global TLDs
EMAIL_REGEX = r"[a-zA-Z0-9_.+%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# International and domestic phone regexes
PHONE_REGEX = r"(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}(?:[\s.-]?\d{1,5})?"

YEAR_REGEX = r"\b(19\d{2}|20[0-2]\d)\b"
URL_REGEX = r"https?://[^\s<>]+|www\.[^\s<>]+|github\.com/[^\s<>]+|linkedin\.com/in/[^\s<>]+"
LINKEDIN_PROFILE_REGEX = r"((?:https?://)?(?:www\.)?linkedin\.com/in/)([a-zA-Z0-9_-]+)"

LOCATION_PATTERNS = [
    r"\b(San Francisco|Los Angeles|New York|Seattle|Austin|Boston|London|Berlin|Toronto|Bangalore|Bengaluru|Tokyo|Sydney|Chicago|Singapore|Denver|San Jose|CA|NY|WA|TX|MA|CO|IL|USA|UK|India|Germany|Canada|France|Japan|Australia)\b",
    r"\b\d{5}(-\d{4})?\b",
    r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b"
]

NAME_PREFIXES = ["Dr.", "Dr", "Mr.", "Mr", "Ms.", "Ms", "Mrs.", "Mrs", "Prof.", "Prof", "Eng."]

def mask_email(email: Optional[str]) -> str:
    if not email:
        return "[EMAIL_MASKED]"
    parts = email.split("@")
    if len(parts) == 2:
        return f"{parts[0][:2]}***@{parts[1]}"
    return "[EMAIL_MASKED]"

def mask_phone(phone: Optional[str]) -> str:
    if not phone:
        return "[PHONE_MASKED]"
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "[PHONE_MASKED]"

def mask_linkedin_url(url: str) -> str:
    if not url:
        return url
    return re.sub(LINKEDIN_PROFILE_REGEX, r"\1[REDACTED_PROFILE]", url, flags=re.IGNORECASE)

def generate_anonymized_id(raw_name: str, fallback_id: str) -> str:
    if raw_name and raw_name.strip():
        clean_raw = raw_name.strip()
        for p in NAME_PREFIXES:
            if clean_raw.startswith(p):
                clean_raw = clean_raw[len(p):].strip()
        hash_val = hashlib.md5(clean_raw.encode("utf-8")).hexdigest()[:6].upper()
        return f"Candidate #{hash_val}"
    return f"Candidate #{fallback_id[:6].upper()}"

def strip_pii_from_text(text: str, candidate_name: str = "") -> str:
    """Strips emails, phones, LinkedIn user slugs, candidate names, and known locations from free-form text."""
    if not text:
        return ""
    cleaned = text

    # 1. Strip emails FIRST (before name replacement can break email strings like 'sarah@...')
    cleaned = re.sub(EMAIL_REGEX, "[EMAIL_MASKED]", cleaned)

    # 2. Strip LinkedIn profile identifiers
    cleaned = re.sub(LINKEDIN_PROFILE_REGEX, r"\1[NAME_MASKED]", cleaned, flags=re.IGNORECASE)

    # 3. Strip international and standard phones
    def phone_replacer(match):
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) >= 7:
            return "[PHONE_MASKED]"
        return match.group(0)

    cleaned = re.sub(PHONE_REGEX, phone_replacer, cleaned)

    # 4. Strip Candidate Name tokens
    if candidate_name and len(candidate_name.strip()) >= 2:
        clean_name = candidate_name.strip()
        for p in NAME_PREFIXES:
            if clean_name.startswith(p):
                clean_name = clean_name[len(p):].strip()

        cleaned = re.sub(re.escape(candidate_name.strip()), "[NAME_MASKED]", cleaned, flags=re.IGNORECASE)
        if clean_name != candidate_name.strip():
            cleaned = re.sub(re.escape(clean_name), "[NAME_MASKED]", cleaned, flags=re.IGNORECASE)

        tokens = [t.strip(".,()[]") for t in re.split(r"[\s\-]+", clean_name) if len(t.strip(".,()[]")) >= 3]
        for t in tokens:
            if t.lower() not in ["and", "the", "for", "with", "from", "van", "von", "del", "der", "san"]:
                cleaned = re.sub(r"\b" + re.escape(t) + r"\b", "[NAME_MASKED]", cleaned, flags=re.IGNORECASE)

    # 5. Strip locations
    for loc_pat in LOCATION_PATTERNS:
        cleaned = re.sub(loc_pat, "[LOCATION_MASKED]", cleaned, flags=re.IGNORECASE)

    return cleaned

def anonymize_candidate(candidate: CandidateData, strip: bool = True) -> CandidateData:
    """Deep-copies candidate and strictly sanitizes/masks all personal identifying fields when strip=True."""
    c_copy = candidate.model_copy(deep=True)
    c_copy.pii_stripped = strip

    if strip:
        # Hide raw name
        c_copy.raw_name = "[REDACTED]"
        if not c_copy.anonymized_name or c_copy.anonymized_name == "Candidate":
            c_copy.anonymized_name = generate_anonymized_id(candidate.raw_name or "", c_copy.candidate_id)

        # Sanitize contact fields
        if candidate.contact.email:
            c_copy.contact.masked_email = mask_email(candidate.contact.email)
            c_copy.contact.email = None
        if candidate.contact.phone:
            c_copy.contact.masked_phone = mask_phone(candidate.contact.phone)
            c_copy.contact.phone = None
        if candidate.contact.location:
            c_copy.contact.masked_location = "[LOCATION_MASKED]"
            c_copy.contact.location = None

        # Mask graduation years
        for edu in c_copy.education:
            edu.year_masked = True
            edu.original_year = None

        # Mask LinkedIn profile handles in external links
        sanitized_links = []
        for l in c_copy.external_links:
            l_copy = l.model_copy(deep=True)
            if "linkedin.com/in/" in l_copy.url.lower():
                l_copy.url = mask_linkedin_url(l_copy.url)
            sanitized_links.append(l_copy)
        c_copy.external_links = sanitized_links

        # Sanitize raw_text so it never leaks unmasked PII
        if c_copy.raw_text:
            c_copy.raw_text = strip_pii_from_text(c_copy.raw_text, candidate.raw_name or "")
    else:
        c_copy.raw_name = candidate.raw_name
        c_copy.contact.masked_email = candidate.contact.email
        c_copy.contact.masked_phone = candidate.contact.phone
        c_copy.contact.masked_location = candidate.contact.location
        c_copy.contact.email = candidate.contact.email
        c_copy.contact.phone = candidate.contact.phone
        c_copy.contact.location = candidate.contact.location
        for idx, edu in enumerate(c_copy.education):
            edu.year_masked = False
            if idx < len(candidate.education):
                edu.original_year = candidate.education[idx].original_year

    return c_copy
