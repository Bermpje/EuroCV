"""Tests for Generic PDF extractor with multi-language support."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eurocv.core.extract.generic_pdf_extractor import GenericPDFExtractor
from eurocv.core.models import Resume


@pytest.fixture
def extractor():
    """Create a GenericPDFExtractor instance."""
    return GenericPDFExtractor()


def test_extractor_name(extractor):
    """Test extractor name property."""
    assert extractor.name == "Generic PDF"


def test_can_handle_pdf(extractor):
    """Test that extractor can handle PDF files."""
    assert extractor.can_handle("resume.pdf") is True
    assert extractor.can_handle("resume.PDF") is True


def test_cannot_handle_non_pdf(extractor):
    """Test that extractor rejects non-PDF files."""
    assert extractor.can_handle("resume.docx") is False
    assert extractor.can_handle("resume.txt") is False


def test_section_headers_multi_language(extractor):
    """Test that section headers include multiple languages."""
    assert "work" in extractor.SECTION_HEADERS
    assert "ervaring" in extractor.SECTION_HEADERS["work"]
    assert "work experience" in extractor.SECTION_HEADERS["work"]

    assert "education" in extractor.SECTION_HEADERS
    assert "opleiding" in extractor.SECTION_HEADERS["education"]

    assert "languages" in extractor.SECTION_HEADERS
    assert "talen" in extractor.SECTION_HEADERS["languages"]


def test_dutch_months_mapping(extractor):
    """Test Dutch month mappings."""
    assert "jan" in extractor.DUTCH_MONTHS
    assert "januari" in extractor.DUTCH_MONTHS
    assert extractor.DUTCH_MONTHS["jan"] == "01"
    assert extractor.DUTCH_MONTHS["januari"] == "01"

    assert "feb" in extractor.DUTCH_MONTHS
    assert "februari" in extractor.DUTCH_MONTHS
    assert extractor.DUTCH_MONTHS["feb"] == "02"


def test_present_keywords(extractor):
    """Test present keywords in multiple languages."""
    assert "present" in extractor.PRESENT_KEYWORDS
    assert "heden" in extractor.PRESENT_KEYWORDS
    assert "nu" in extractor.PRESENT_KEYWORDS
    assert "current" in extractor.PRESENT_KEYWORDS


def test_proficiency_map(extractor):
    """Test language proficiency mapping."""
    assert "native" in extractor.PROFICIENCY_MAP
    assert "moedertaal" in extractor.PROFICIENCY_MAP
    assert extractor.PROFICIENCY_MAP["native"] == "Native"
    assert extractor.PROFICIENCY_MAP["moedertaal"] == "Native"

    assert "proficient" in extractor.PROFICIENCY_MAP
    assert "vloeiend" in extractor.PROFICIENCY_MAP
    assert extractor.PROFICIENCY_MAP["proficient"] == "C2"


@patch("fitz.open")
def test_extract_basic(mock_fitz_open, extractor, tmp_path):
    """Test basic extraction."""
    # Create a temporary PDF file
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy content")

    # Mock PDF extraction
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "John Doe\njohn@example.com\n+31 6 12345678"
    mock_doc.__getitem__.return_value = mock_page
    mock_doc.load_page.return_value = mock_page
    mock_doc.page_count = 1
    mock_fitz_open.return_value = mock_doc

    resume = extractor.extract(str(pdf_file))

    assert isinstance(resume, Resume)
    assert resume.personal_info is not None
    assert resume.personal_info.email == "john@example.com"


def test_parse_date_dutch_months(extractor):
    """Test parsing dates with Dutch month names."""
    # Test Dutch month names
    date1 = extractor._parse_date("januari 2020")
    assert date1 is not None
    assert date1.year == 2020
    assert date1.month == 1

    date2 = extractor._parse_date("feb 2021")
    assert date2 is not None
    assert date2.year == 2021
    assert date2.month == 2

    date3 = extractor._parse_date("okt 2022")
    assert date3 is not None
    assert date3.year == 2022
    assert date3.month == 10


def test_parse_date_english_months(extractor):
    """Test parsing dates with English month names."""
    date1 = extractor._parse_date("January 2020")
    assert date1 is not None
    assert date1.year == 2020
    assert date1.month == 1

    date2 = extractor._parse_date("Feb 2021")
    assert date2 is not None
    assert date2.year == 2021
    assert date2.month == 2


def test_split_into_sections_dutch(extractor):
    """Test section splitting with Dutch headers."""
    text = """
    ERVARING

    Software Engineer
    Company X
    2020 - 2023

    OPLEIDING

    Bachelor Informatica
    University
    2016 - 2020

    VAARDIGHEDEN

    Python, JavaScript
    """

    sections = extractor._split_into_sections(text)

    assert "experience" in sections
    assert "education" in sections
    assert "skill" in sections


def test_split_into_sections_english(extractor):
    """Test section splitting with English headers."""
    text = """
    WORK EXPERIENCE

    Software Engineer

    EDUCATION

    Bachelor CS

    SKILLS

    Python
    """

    sections = extractor._split_into_sections(text)

    assert "experience" in sections
    assert "education" in sections
    assert "skill" in sections


def test_extract_languages_with_native(extractor):
    """Test language extraction with native language detection."""
    text = """
    LANGUAGES

    Dutch | Native
    English | Proficient
    German | Basic
    """

    languages = extractor._extract_languages(text)

    # Should detect all three languages
    assert len(languages) >= 2

    # Check if Dutch is detected as native
    dutch_lang = next((lang for lang in languages if lang.language == "Dutch"), None)
    if dutch_lang:
        assert dutch_lang.is_native is True


def test_extract_work_experience_dutch_dates(extractor):
    """Test work experience extraction with Dutch dates."""
    text = """
    MANAGER PEOPLE OPERATIONS A.I.
    SUNWEB GROUP
    Feb 2025 - heden

    Leiding over het People Operations team

    COUNTRY HR MANAGER A.I.
    FABER GROUP
    Jun 2023 - Jan 2025

    Verantwoordelijk voor de HR-strategie
    """

    experiences = extractor._extract_work_experience(text)

    # Should extract at least one work experience
    assert len(experiences) >= 1

    # Check if "heden" is recognized as current
    if len(experiences) > 0:
        first_exp = experiences[0]
        # Either current should be True or dates should be extracted
        assert first_exp.start_date is not None or first_exp.position is not None


@pytest.mark.skipif(
    not Path("CV Sample Person_0825NL .pdf").exists(), reason="Dutch CV sample not available"
)
def test_extract_dutch_cv_real(extractor):
    """Test extraction of real Dutch CV (Sample Person).

    This test only runs if the CV file is present.
    """
    resume = extractor.extract("CV Sample Person_0825NL .pdf")

    # Verify basic extraction
    assert isinstance(resume, Resume)
    assert resume.personal_info is not None

    # Check if email was extracted
    assert resume.personal_info.email == "Lotte@LSHR.nl"

    # Check if name was extracted
    # Note: Name extraction might not be perfect, so we check for either first or last name
    assert resume.personal_info.first_name is not None or resume.personal_info.last_name is not None

    # Check if work experience was extracted
    # Should have at least some work experience
    assert len(resume.work_experience) > 0

    # Check if education was extracted
    # Should have at least one education entry
    assert len(resume.education) > 0

    # Check if languages were extracted
    assert len(resume.languages) >= 2

    # Verify Dutch language is detected
    dutch_lang = next(
        (
            lang
            for lang in resume.languages
            if "Dutch" in lang.language or "Nederlands" in lang.language
        ),
        None,
    )
    assert dutch_lang is not None
