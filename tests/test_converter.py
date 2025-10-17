"""Tests for converter module."""

from unittest.mock import patch

import pytest

from eurocv.core.converter import convert_to_europass, extract_resume, map_to_europass
from eurocv.core.models import ConversionResult, PersonalInfo, Resume


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


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("eurocv.core.validate.schema_validator.SchemaValidator.validate_json")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_with_validation_errors(
    mock_exists, mock_validate_json, mock_extract
):
    """Test conversion with validation errors."""
    from eurocv.core.models import PersonalInfo

    mock_extract.return_value = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )
    mock_validate_json.return_value = (
        False,
        ["Validation error 1", "Validation error 2"],
    )

    result = convert_to_europass("test.pdf", output_format="both", validate=True)

    # Should return result with validation errors
    assert isinstance(result, ConversionResult)
    assert len(result.validation_errors) > 0


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("eurocv.core.validate.schema_validator.SchemaValidator.validate_xml")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_xml_validation_errors(
    mock_exists, mock_validate_xml, mock_extract
):
    """Test conversion with XML validation errors."""
    from eurocv.core.models import PersonalInfo

    mock_extract.return_value = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )
    mock_validate_xml.return_value = (False, ["XML validation error"])

    result = convert_to_europass("test.pdf", output_format="xml", validate=True)

    # Should still return XML even with validation errors
    assert isinstance(result, str)


def test_validate_europass_json():
    """Test validate_europass with JSON data."""
    from eurocv.core.converter import validate_europass

    # Simple valid structure
    data = {"DocumentInfo": {}, "LearnerInfo": {}}

    is_valid, errors = validate_europass(data)

    # Should attempt validation (may or may not be valid depending on schema)
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_validate_europass_xml():
    """Test validate_europass with XML data."""
    from eurocv.core.converter import validate_europass

    # Simple XML string
    xml_data = '<?xml version="1.0"?><root></root>'

    is_valid, errors = validate_europass(xml_data)

    # Should attempt validation
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_validate_europass_invalid_type():
    """Test validate_europass with invalid data type."""
    from eurocv.core.converter import validate_europass

    # Invalid data type (not dict or str)
    is_valid, errors = validate_europass([1, 2, 3])

    # Should return False with error message
    assert is_valid is False
    assert len(errors) > 0
    assert "Invalid data type" in errors[0]


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_both_format(mock_exists, mock_extract):
    """Test conversion with 'both' output format."""
    from eurocv.core.models import PersonalInfo

    mock_extract.return_value = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )

    result = convert_to_europass("test.pdf", output_format="both", validate=False)

    # Should return ConversionResult with both json and xml
    assert isinstance(result, ConversionResult)
    assert result.json_data is not None
    assert result.xml_data is not None


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("pathlib.Path.exists", return_value=True)
def test_convert_to_europass_xml_only(mock_exists, mock_extract):
    """Test conversion with 'xml' output format."""
    from eurocv.core.models import PersonalInfo

    mock_extract.return_value = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User")
    )

    result = convert_to_europass("test.pdf", output_format="xml", validate=False)

    # Should return XML string
    assert isinstance(result, str)
    assert len(result) > 0


@patch("eurocv.core.extract.generic_pdf_extractor.GenericPDFExtractor.extract")
@patch("pathlib.Path.exists", return_value=True)
def test_extract_resume_with_ocr(mock_exists, mock_extract):
    """Test extract_resume with OCR enabled."""
    mock_extract.return_value = Resume()

    resume = extract_resume("test.pdf", use_ocr=True)

    # Should extract and return Resume
    assert isinstance(resume, Resume)
