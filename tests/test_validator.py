"""Tests for schema validator."""

import pytest
from eurocv.core.validate.schema_validator import SchemaValidator, convert_to_xml


@pytest.fixture
def valid_europass_json():
    """Create a valid Europass JSON structure."""
    return {
        "DocumentInfo": {
            "DocumentType": "Europass CV",
            "CreationDate": "2024-01-01T00:00:00",
            "Generator": "EuroCV",
            "XSDVersion": "V3.3"
        },
        "LearnerInfo": {
            "Identification": {
                "PersonName": {
                    "FirstName": "John",
                    "Surname": "Doe"
                }
            }
        }
    }


def test_validator_initialization():
    """Test validator initialization."""
    validator = SchemaValidator()
    assert validator.schema_dir.exists()


def test_validate_valid_json(valid_europass_json):
    """Test validation of valid JSON."""
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(valid_europass_json)
    
    assert is_valid
    assert len(errors) == 0


def test_validate_missing_document_info():
    """Test validation with missing DocumentInfo."""
    data = {"LearnerInfo": {}}
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    assert not is_valid
    assert any("DocumentInfo" in error for error in errors)


def test_validate_missing_learner_info():
    """Test validation with missing LearnerInfo."""
    data = {"DocumentInfo": {}}
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    assert not is_valid
    assert any("LearnerInfo" in error for error in errors)


def test_validate_invalid_person_name():
    """Test validation with invalid PersonName."""
    data = {
        "DocumentInfo": {},
        "LearnerInfo": {
            "Identification": {
                "PersonName": "Invalid"  # Should be dict, not string
            }
        }
    }
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    assert not is_valid


def test_convert_to_xml_basic():
    """Test basic XML conversion."""
    data = {
        "DocumentInfo": {
            "DocumentType": "Europass CV"
        }
    }
    
    xml_string = convert_to_xml(data)
    
    assert xml_string is not None
    assert isinstance(xml_string, str)
    assert "Europass" in xml_string
    assert "DocumentInfo" in xml_string


def test_convert_to_xml_with_nested_data():
    """Test XML conversion with nested data."""
    data = {
        "DocumentInfo": {
            "DocumentType": "Europass CV",
            "CreationDate": "2024-01-01"
        },
        "LearnerInfo": {
            "Identification": {
                "PersonName": {
                    "FirstName": "John"
                }
            }
        }
    }
    
    xml_string = convert_to_xml(data)
    
    assert "FirstName" in xml_string
    assert "John" in xml_string


def test_validate_xml_invalid_syntax():
    """Test XML validation with invalid syntax."""
    validator = SchemaValidator()
    xml_string = "<Invalid><XML"
    
    is_valid, errors = validator.validate_xml(xml_string)
    
    assert not is_valid
    assert len(errors) > 0

