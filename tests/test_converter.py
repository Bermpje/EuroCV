"""Tests for converter module."""

import pytest
from unittest.mock import Mock, patch
from eurocv.core.converter import convert_to_europass, extract_resume, map_to_europass
from eurocv.core.models import Resume, PersonalInfo


def test_extract_resume_unsupported_format():
    """Test extraction with unsupported file format."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_resume("test.txt")


@patch('eurocv.core.extract.pdf_extractor.PDFExtractor.extract')
def test_extract_resume_pdf(mock_extract):
    """Test PDF extraction."""
    mock_extract.return_value = Resume()
    
    # Create a temporary PDF file path
    with patch('pathlib.Path.exists', return_value=True):
        resume = extract_resume("test.pdf")
    
    assert isinstance(resume, Resume)
    mock_extract.assert_called_once()


@patch('eurocv.core.extract.docx_extractor.DOCXExtractor.extract')
def test_extract_resume_docx(mock_extract):
    """Test DOCX extraction."""
    mock_extract.return_value = Resume()
    
    with patch('pathlib.Path.exists', return_value=True):
        resume = extract_resume("test.docx")
    
    assert isinstance(resume, Resume)
    mock_extract.assert_called_once()


def test_map_to_europass():
    """Test mapping Resume to Europass."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )
    
    europass = map_to_europass(resume)
    
    assert "DocumentInfo" in europass.to_json()
    assert "LearnerInfo" in europass.to_json()


def test_map_to_europass_with_locale():
    """Test mapping with different locale."""
    resume = Resume()
    
    europass_us = map_to_europass(resume, locale="en-US")
    europass_nl = map_to_europass(resume, locale="nl-NL")
    
    assert isinstance(europass_us.to_json(), dict)
    assert isinstance(europass_nl.to_json(), dict)


def test_map_to_europass_without_photo():
    """Test mapping without photo."""
    resume = Resume()
    
    europass = map_to_europass(resume, include_photo=False)
    
    learner_info = europass.to_json().get("LearnerInfo", {})
    identification = learner_info.get("Identification", {})
    
    assert "Photo" not in identification

