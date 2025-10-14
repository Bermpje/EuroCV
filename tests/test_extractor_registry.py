"""Tests for extractor registry and auto-detection."""

from unittest.mock import MagicMock, patch

import pytest

from eurocv.core.extract.docx_extractor import DOCXExtractor
from eurocv.core.extract.generic_pdf_extractor import GenericPDFExtractor
from eurocv.core.extract.linkedin_pdf_extractor import LinkedInPDFExtractor
from eurocv.core.extract.registry import EXTRACTORS, get_extractor


def test_registry_has_extractors():
    """Test that registry has extractors registered."""
    assert len(EXTRACTORS) > 0
    assert LinkedInPDFExtractor in EXTRACTORS
    assert GenericPDFExtractor in EXTRACTORS
    assert DOCXExtractor in EXTRACTORS


def test_registry_priority_order():
    """Test that extractors are in correct priority order."""
    # LinkedIn should be first (most specific)
    assert EXTRACTORS[0] == LinkedInPDFExtractor
    # Generic PDF should be last (fallback)
    assert EXTRACTORS[-1] == GenericPDFExtractor


@patch("fitz.open")
def test_auto_detect_linkedin_pdf(mock_fitz_open):
    """Test auto-detection of LinkedIn PDF."""
    # Mock a PDF with LinkedIn metadata
    mock_doc = MagicMock()
    mock_doc.metadata = {"producer": "LinkedIn PDF Generator"}
    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    extractor = get_extractor("resume.pdf")

    assert isinstance(extractor, LinkedInPDFExtractor)
    assert extractor.name == "LinkedIn PDF"


@patch("fitz.open")
def test_auto_detect_generic_pdf(mock_fitz_open):
    """Test auto-detection of generic PDF."""
    # Mock a PDF without LinkedIn markers
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Regular resume content"
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    extractor = get_extractor("resume.pdf")

    assert isinstance(extractor, GenericPDFExtractor)
    assert extractor.name == "Generic PDF"


def test_auto_detect_docx():
    """Test auto-detection of DOCX files."""
    extractor = get_extractor("resume.docx")

    assert isinstance(extractor, DOCXExtractor)
    assert extractor.name == "DOCX"


def test_auto_detect_doc():
    """Test auto-detection of DOC files."""
    extractor = get_extractor("resume.doc")

    assert isinstance(extractor, DOCXExtractor)


def test_unsupported_format():
    """Test that unsupported format raises error."""
    with pytest.raises(ValueError, match="No suitable extractor found"):
        get_extractor("resume.txt")


@patch("fitz.open")
def test_get_extractor_with_ocr(mock_fitz_open):
    """Test that use_ocr parameter is passed to extractors."""
    # Mock a PDF without LinkedIn markers
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Regular resume content"
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    extractor = get_extractor("resume.pdf", use_ocr=True)

    assert isinstance(extractor, GenericPDFExtractor)
    assert extractor.use_ocr is True


def test_docx_extractor_no_ocr_param():
    """Test that DOCX extractor works without use_ocr parameter."""
    # DOCX extractor doesn't have use_ocr parameter
    extractor = get_extractor("resume.docx", use_ocr=True)

    assert isinstance(extractor, DOCXExtractor)
    # Should not have use_ocr attribute
    assert not hasattr(extractor, "use_ocr")


@patch("fitz.open")
def test_linkedin_detection_by_content(mock_fitz_open):
    """Test LinkedIn detection by page content."""
    # Mock a PDF with linkedin.com in content
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "John Doe\nlinkedin.com/in/johndoe\nSoftware Engineer"
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    extractor = get_extractor("resume.pdf")

    assert isinstance(extractor, LinkedInPDFExtractor)


@patch("fitz.open")
def test_extractors_tried_in_order(mock_fitz_open):
    """Test that extractors are tried in priority order."""
    # Mock a PDF that both LinkedIn and Generic can handle
    # But Generic should only be used if LinkedIn can't handle it
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.__len__.return_value = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Regular content"
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz_open.return_value.__enter__.return_value = mock_doc

    extractor = get_extractor("resume.pdf")

    # Should get Generic since LinkedIn markers aren't present
    assert isinstance(extractor, GenericPDFExtractor)
    # But if LinkedIn markers were present, it would get LinkedIn first
