import pytest
from unittest.mock import patch, MagicMock
from app.extraction.section_splitter import split_sections
from app.extraction.bullet_chunker import split_into_bullets
from app.extraction.pdf_extractor import (
    parse_resume_to_candidate,
    extract_raw_text_from_pdf,
    perform_ocr_fallback
)

SAMPLE_RESUME_TEXT = """
Jane Doe
jane.doe@example.com | (555) 123-4567 | San Francisco, CA | github.com/janedoe

SUMMARY
Experienced software engineer specializing in scalable distributed backends.

TECHNICAL SKILLS
Python, PostgreSQL, Kubernetes, Redis, Docker, FastAPI, Go

WORK EXPERIENCE
Senior Backend Engineer | CloudTech
Jan 2021 - Present
• Designed low-latency microservices handling 15M daily requests using Python and FastAPI.
• Optimized PostgreSQL query performance, reducing p99 latency by 35%.
• Led a cross-functional squad of 5 engineers.

EDUCATION
B.S. in Computer Science | UC Berkeley
Graduated 2019
"""

def test_section_splitter():
    sections = split_sections(SAMPLE_RESUME_TEXT)
    assert "SKILLS" in sections
    assert "EXPERIENCE" in sections
    assert "EDUCATION" in sections
    assert "Python" in sections["SKILLS"]

def test_bullet_chunker():
    bullets = split_into_bullets("""
    • Designed low-latency microservices handling 15M daily requests.
    • Optimized PostgreSQL query performance, reducing p99 latency by 35%.
    • Led a cross-functional squad of 5 engineers.
    """)
    assert len(bullets) == 3
    assert "15M daily requests" in bullets[0]
    assert "p99 latency by 35%" in bullets[1]

def test_parse_resume_to_candidate():
    candidate = parse_resume_to_candidate(SAMPLE_RESUME_TEXT, "jane_doe_resume.pdf")
    assert candidate.raw_name == "Jane Doe"
    assert candidate.contact.email == "jane.doe@example.com"
    assert len(candidate.experience) >= 1
    assert len(candidate.skills) >= 4

def test_ocr_fallback_on_scanned_pdf():
    # Mock pypdf returning near-empty text and mock pdf2image + pytesseract returning valid OCR text
    ocr_mock_text = """John Scanned
john.scanned@example.com | (555) 999-0000 | New York, NY

TECHNICAL SKILLS
Python, Docker, AWS, PostgreSQL

WORK EXPERIENCE
Backend Developer | Scanned Corp
2020 - Present
• Built data ingestion pipelines in Python.
"""
    with patch("app.extraction.pdf_extractor.PdfReader") as mock_pdf_reader, \
         patch("app.extraction.pdf_extractor.perform_ocr_fallback", return_value=ocr_mock_text) as mock_ocr:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "   " # near empty
        mock_pdf_reader.return_value.pages = [mock_page]

        text, is_scanned = extract_raw_text_from_pdf("dummy_scanned.pdf")
        assert is_scanned is True
        assert "John Scanned" in text
        assert mock_ocr.called

        # Verify parsed candidate from OCR text
        candidate = parse_resume_to_candidate(text, "dummy_scanned.pdf")
        assert candidate.raw_name == "John Scanned"
        assert candidate.contact.email == "john.scanned@example.com"
        assert any(s.name == "Python" for s in candidate.skills)

def test_ocr_fallback_graceful_on_missing_binaries():
    # Verify perform_ocr_fallback doesn't crash when binaries fail
    with patch("pdf2image.convert_from_path", side_effect=Exception("poppler not installed")):
        result = perform_ocr_fallback("non_existent.pdf")
        assert result == ""


def test_sanitize_filename():
    from app.api.candidates import sanitize_filename
    assert sanitize_filename("../../secret.pdf") == "secret.pdf"
    assert sanitize_filename("..\\..\\boot.ini") == "boot.ini"
    assert sanitize_filename("normal_resume.pdf") == "normal_resume.pdf"
    assert sanitize_filename("../../../malicious_file/resume.pdf") == "resume.pdf"
    assert sanitize_filename("") == "resume_upload.pdf"

def test_upload_validation_logic():
    from app.api.candidates import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES
    assert ".pdf" in ALLOWED_EXTENSIONS
    assert ".txt" in ALLOWED_EXTENSIONS
    assert ".exe" not in ALLOWED_EXTENSIONS
    assert MAX_FILE_SIZE_BYTES == 10 * 1024 * 1024
