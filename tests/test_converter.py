"""Tests for converter module."""

from unittest.mock import patch

import pytest

from eurocv.core.converter import convert_to_europass, extract_resume, map_to_europass
from eurocv.core.models import PersonalInfo, Resume


def test_extract_resume_unsupported_format():
    """Test extraction with unsupported file format."""
    with pytest.raises(ValueError, match="No suitable extractor found"):
        extract_resume("test.txt")


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
def test_extract_resume_pdf(mock_extract):
    """Test PDF extraction."""
    mock_extract.return_value = Resume()

    # Create a temporary PDF file path
    with patch("pathlib.Path.exists", return_value=True):
        resume = extract_resume("test.pdf")

    assert isinstance(resume, Resume)
    mock_extract.assert_called_once()


@patch("eurocv.core.extract.docx_extractor.DOCXExtractor.extract")
def test_extract_resume_docx(mock_extract):
    """Test DOCX extraction."""
    mock_extract.return_value = Resume()

    with patch("pathlib.Path.exists", return_value=True):
        resume = extract_resume("test.docx")

    assert isinstance(resume, Resume)
    mock_extract.assert_called_once()


def test_map_to_europass():
    """Test mapping Resume to Europass."""
    resume = Resume(personal_info=PersonalInfo(first_name="Test", last_name="User"))

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


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("eurocv.core.map.europass_mapper.EuropassMapper.map")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_json(mock_exists, mock_map, mock_extract):
    """Test full conversion to JSON."""
    from eurocv.core.models import EuropassCV

    mock_resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )
    mock_extract.return_value = mock_resume

    mock_europass = EuropassCV()
    mock_map.return_value = mock_europass

    result = convert_to_europass("test.pdf", output_format="json", validate=False)

    assert isinstance(result, dict)


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("eurocv.core.map.europass_mapper.EuropassMapper.map")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_xml(mock_exists, mock_map, mock_extract):
    """Test full conversion to XML."""
    from eurocv.core.models import EuropassCV

    mock_resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )
    mock_extract.return_value = mock_resume

    mock_europass = EuropassCV()
    mock_map.return_value = mock_europass

    result = convert_to_europass("test.pdf", output_format="xml", validate=False)

    assert isinstance(result, str)


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("eurocv.core.map.europass_mapper.EuropassMapper.map")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_both(mock_exists, mock_map, mock_extract):
    """Test full conversion to both formats."""
    from eurocv.core.models import ConversionResult, EuropassCV

    mock_resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )
    mock_extract.return_value = mock_resume

    mock_europass = EuropassCV()
    mock_map.return_value = mock_europass

    result = convert_to_europass("test.pdf", output_format="both", validate=False)

    assert isinstance(result, ConversionResult)
    assert result.json_data is not None
    assert result.xml_data is not None


def test_convert_to_europass_file_not_found():
    """Test conversion with non-existent file."""
    with pytest.raises(FileNotFoundError):
        convert_to_europass("nonexistent.pdf")
