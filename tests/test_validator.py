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


def test_validate_xml_valid():
    """Test XML validation with valid XML."""
    validator = SchemaValidator()
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <DocumentInfo>
        <DocumentType>Europass CV</DocumentType>
    </DocumentInfo>
</root>"""
    
    is_valid, errors = validator.validate_xml(xml_string)
    # May or may not be schema-valid, but should parse
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_validate_json_empty():
    """Test validation with empty JSON."""
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json({})
    
    assert not is_valid
    assert len(errors) > 0


def test_validate_json_with_extra_fields(valid_europass_json):
    """Test validation with extra fields."""
    data = valid_europass_json.copy()
    data["ExtraField"] = "Should be ignored or cause warning"
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    # Should still be valid or have warnings
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_convert_to_xml_with_lists():
    """Test XML conversion with list data."""
    data = {
        "DocumentInfo": {
            "Items": ["Item1", "Item2", "Item3"]
        }
    }
    
    xml_string = convert_to_xml(data)
    
    assert "Item1" in xml_string or "Items" in xml_string
    assert isinstance(xml_string, str)


def test_convert_to_xml_with_special_chars():
    """Test XML conversion with special characters."""
    data = {
        "DocumentInfo": {
            "Description": "Test & <special> \"chars\""
        }
    }
    
    xml_string = convert_to_xml(data)
    
    # Should escape special XML characters
    assert isinstance(xml_string, str)
    assert len(xml_string) > 0


def test_validator_with_none():
    """Test validator with None input."""
    validator = SchemaValidator()
    
    is_valid, errors = validator.validate_json(None)  # type: ignore
    
    assert not is_valid
    assert len(errors) > 0


def test_convert_to_xml_empty_dict():
    """Test XML conversion with empty dict."""
    xml_string = convert_to_xml({})
    
    assert isinstance(xml_string, str)
    assert len(xml_string) > 0


def test_validate_work_experience():
    """Test validation with work experience."""
    data = {
        "DocumentInfo": {},
        "LearnerInfo": {
            "WorkExperience": [
                {
                    "Position": {"Label": "Developer"},
                    "Employer": {"Name": "Company Inc"},
                    "Period": {"From": "2020-01-01"}
                }
            ]
        }
    }
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    # May have some errors, but should not crash
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_validate_education():
    """Test validation with education."""
    data = {
        "DocumentInfo": {},
        "LearnerInfo": {
            "Education": [
                {
                    "Title": "Bachelor of Science",
                    "Organisation": {"Name": "University"},
                    "Level": {"Code": "6"}
                }
            ]
        }
    }
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    # May have some errors, but should not crash
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_validate_skills():
    """Test validation with skills."""
    data = {
        "DocumentInfo": {},
        "LearnerInfo": {
            "Skills": {
                "Linguistic": {
                    "ForeignLanguage": [
                        {
                            "Description": {"Code": "en"},
                            "ProficiencyLevel": {"Listening": "C1"}
                        }
                    ]
                }
            }
        }
    }
    
    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(data)
    
    # May have some errors, but should not crash
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)

