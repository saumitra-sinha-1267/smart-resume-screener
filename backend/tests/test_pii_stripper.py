import pytest
from app.normalization.pii_stripper import (
    strip_pii_from_text,
    mask_email,
    mask_phone,
    mask_linkedin_url,
    anonymize_candidate,
    generate_anonymized_id
)
from app.normalization.schema_models import CandidateData, ContactInfo, EducationItem, ExternalLinkItem

def test_linkedin_url_name_stripping():
    text = "Profile available at https://www.linkedin.com/in/john-doe-12345 or linkedin.com/in/mary-jane-smith/"
    cleaned = strip_pii_from_text(text)
    assert "john-doe-12345" not in cleaned
    assert "mary-jane-smith" not in cleaned
    assert "linkedin.com/in/[NAME_MASKED]" in cleaned

def test_unusual_name_formats():
    # Hyphenated names
    t1 = "Authored architecture doc by Mary Jane Watson-Parker for the team."
    c1 = strip_pii_from_text(t1, candidate_name="Mary Jane Watson-Parker")
    assert "Watson-Parker" not in c1
    assert "Mary" not in c1
    assert "[NAME_MASKED]" in c1

    # Name with Title / Prefix
    t2 = "Dr. Jean-Luc Picard led the distributed telemetry project."
    c2 = strip_pii_from_text(t2, candidate_name="Dr. Jean-Luc Picard")
    assert "Jean-Luc" not in c2
    assert "Picard" not in c2
    assert "[NAME_MASKED]" in c2

    # Name with Apostrophe
    t3 = "Code reviewed by Sean O'Connor before release."
    c3 = strip_pii_from_text(t3, candidate_name="Sean O'Connor")
    assert "O'Connor" not in c3
    assert "Sean" not in c3

def test_international_phone_formats():
    # UK Phone
    uk_text = "Call me on +44 20 7946 0958 or 020 7946 0958 for interview."
    cleaned_uk = strip_pii_from_text(uk_text)
    assert "+44 20 7946 0958" not in cleaned_uk
    assert "[PHONE_MASKED]" in cleaned_uk

    # India Phone
    in_text = "Mobile: +91 98765 43210 (available on WhatsApp)"
    cleaned_in = strip_pii_from_text(in_text)
    assert "98765 43210" not in cleaned_in
    assert "[PHONE_MASKED]" in cleaned_in

    # Germany Phone
    de_text = "Telefon: +49 30 123456"
    cleaned_de = strip_pii_from_text(de_text)
    assert "123456" not in cleaned_de or "[PHONE_MASKED]" in cleaned_de

def test_embedded_emails():
    text = "contact:john.doe+work@company.co.uk and (reach out at jane_doe@sub.domain.org)"
    cleaned = strip_pii_from_text(text)
    assert "john.doe+work@company.co.uk" not in cleaned
    assert "jane_doe@sub.domain.org" not in cleaned
    assert "[EMAIL_MASKED]" in cleaned

def test_anonymize_candidate_deep_link_and_raw_text():
    cand = CandidateData(
        raw_name="Dr. Alex O'Connor",
        contact=ContactInfo(email="alex.oconnor+test@domain.co.uk", phone="+44 7700 900077", location="London"),
        external_links=[
            ExternalLinkItem(url="https://www.linkedin.com/in/alex-oconnor-8899", link_type="linkedin", verified=True)
        ],
        education=[EducationItem(degree="Ph.D. in Computer Science", original_year="2020")],
        raw_text="Dr. Alex O'Connor based in London. Email: alex.oconnor+test@domain.co.uk, Phone: +44 7700 900077. LinkedIn: https://www.linkedin.com/in/alex-oconnor-8899"
    )

    anon = anonymize_candidate(cand, strip=True)
    assert anon.raw_name == "[REDACTED]"
    assert anon.contact.email is None
    assert anon.contact.masked_email.startswith("al***@")
    assert anon.contact.phone is None
    assert anon.external_links[0].url == "https://www.linkedin.com/in/[REDACTED_PROFILE]"
    assert "Alex" not in anon.raw_text
    assert "O'Connor" not in anon.raw_text
    assert "London" not in anon.raw_text
