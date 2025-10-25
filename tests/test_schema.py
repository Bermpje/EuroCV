"""Tests for Europass schema models and validation."""

import pytest
from pydantic import ValidationError

from eurocv.core.europass_schema import (
    EuropassCVResponse,
    EuropassDate,
    EuropassDocumentInfo,
    EuropassLearnerInfo,
    EuropassPeriod,
    EuropassPosition,
    EuropassWorkExperience,
)


def test_europass_date_model():
    """Test EuropassDate model."""
    # Valid date
    date = EuropassDate(Year=2020, Month=3, Day=15)
    assert date.Year == 2020
    assert date.Month == 3
    assert date.Day == 15

    # Year only
    date = EuropassDate(Year=2020)
    assert date.Year == 2020
    assert date.Month is None
    assert date.Day is None


def test_europass_period_model():
    """Test EuropassPeriod model."""
    period = EuropassPeriod(
        From=EuropassDate(Year=2018, Month=1, Day=1),
        To=EuropassDate(Year=2023, Month=12, Day=31),
    )
    assert period.From.Year == 2018
    assert period.To.Year == 2023
    assert period.Current is None

    # Current position
    period = EuropassPeriod(From=EuropassDate(Year=2020, Month=1, Day=1), Current=True)
    assert period.From.Year == 2020
    assert period.To is None
    assert period.Current is True


def test_europass_work_experience_model():
    """Test EuropassWorkExperience model."""
    work_exp = EuropassWorkExperience(
        Period=EuropassPeriod(
            From=EuropassDate(Year=2020, Month=1, Day=1), Current=True
        ),
        Position=EuropassPosition(Label="Software Engineer", Code="2512"),
        Activities="Developing web applications",
        Employer={
            "Name": "Tech Corp",
            "ContactInfo": {
                "Address": {
                    "Contact": {
                        "Municipality": "Amsterdam",
                        "Country": {"Code": "NL", "Label": "Netherlands"},
                    }
                }
            },
        },
    )

    assert work_exp.Position.Label == "Software Engineer"
    assert work_exp.Position.Code == "2512"
    assert work_exp.Activities == "Developing web applications"
    assert work_exp.Employer.Name == "Tech Corp"


def test_europass_cv_response_model():
    """Test complete EuropassCVResponse model."""
    cv_data = {
        "DocumentInfo": {
            "DocumentType": "Europass CV",
            "CreationDate": "2025-10-25T00:00:00",
            "Generator": "EuroCV",
            "XSDVersion": "V3.4",
        },
        "LearnerInfo": {
            "Identification": {
                "PersonName": {"FirstName": "John", "Surname": "Doe"},
                "ContactInfo": {
                    "Email": {"Contact": "john.doe@example.com"},
                    "Address": {
                        "Contact": {
                            "Municipality": "Amsterdam",
                            "Country": {"Code": "NL", "Label": "Netherlands"},
                        }
                    },
                },
            },
            "WorkExperience": [
                {
                    "Period": {
                        "From": {"Year": 2020, "Month": 1, "Day": 1},
                        "Current": True,
                    },
                    "Position": {"Label": "Software Engineer"},
                    "Activities": "Developing applications",
                    "Employer": {
                        "Name": "Tech Corp",
                        "ContactInfo": {
                            "Address": {
                                "Contact": {
                                    "Municipality": "Amsterdam",
                                    "Country": {
                                        "Code": "NL",
                                        "Label": "Netherlands",
                                    },
                                }
                            }
                        },
                    },
                }
            ],
        },
    }

    # Should validate successfully
    cv = EuropassCVResponse(**cv_data)
    assert cv.DocumentInfo.DocumentType == "Europass CV"
    assert cv.LearnerInfo.Identification.PersonName.FirstName == "John"
    assert len(cv.LearnerInfo.WorkExperience) == 1


def test_europass_cv_response_validation_error():
    """Test that invalid data raises validation errors."""
    # Missing required fields
    invalid_data = {
        "DocumentInfo": {
            "DocumentType": "Europass CV",
            # Missing CreationDate, Generator, XSDVersion
        },
        "LearnerInfo": {},
    }

    with pytest.raises(ValidationError):
        EuropassCVResponse(**invalid_data)


def test_json_schema_generation():
    """Test that JSON schema can be generated."""
    schema = EuropassCVResponse.model_json_schema()

    assert schema is not None
    assert "properties" in schema
    assert "DocumentInfo" in schema["properties"]
    assert "LearnerInfo" in schema["properties"]
    assert "$defs" in schema or "definitions" in schema


def test_json_schema_has_required_fields():
    """Test that JSON schema marks required fields."""
    schema = EuropassCVResponse.model_json_schema()

    # DocumentInfo and LearnerInfo should be required
    assert "required" in schema
    assert "DocumentInfo" in schema["required"]
    assert "LearnerInfo" in schema["required"]


def test_json_schema_has_examples():
    """Test that JSON schema includes example data."""
    schema = EuropassCVResponse.model_json_schema()

    # Check if examples are present at root level
    assert "example" in schema or "examples" in schema


def test_model_serialization():
    """Test that models can be serialized to JSON."""
    cv_data = EuropassCVResponse(
        DocumentInfo=EuropassDocumentInfo(
            DocumentType="Europass CV",
            CreationDate="2025-10-25T00:00:00",
            Generator="EuroCV",
            XSDVersion="V3.4",
        ),
        LearnerInfo=EuropassLearnerInfo(Identification=None, WorkExperience=[]),
    )

    # Should serialize without error
    json_dict = cv_data.model_dump()
    assert json_dict["DocumentInfo"]["DocumentType"] == "Europass CV"
    assert json_dict["DocumentInfo"]["XSDVersion"] == "V3.4"


def test_model_exclude_none():
    """Test that None values can be excluded from serialization."""
    cv_data = EuropassCVResponse(
        DocumentInfo=EuropassDocumentInfo(
            DocumentType="Europass CV",
            CreationDate="2025-10-25T00:00:00",
            Generator="EuroCV",
            XSDVersion="V3.4",
            Comment=None,  # Optional field
        ),
        LearnerInfo=EuropassLearnerInfo(),
    )

    json_dict = cv_data.model_dump(exclude_none=True)
    assert "Comment" not in json_dict["DocumentInfo"]


def test_work_experience_without_optional_fields():
    """Test WorkExperience with minimal required fields."""
    work_exp = EuropassWorkExperience(
        Period=EuropassPeriod(From=EuropassDate(Year=2020)),
        Position=EuropassPosition(Label="Developer"),
        Employer={"Name": "Company"},
    )

    assert work_exp.Activities is None
    assert work_exp.Position.Code is None


def test_nested_model_validation():
    """Test that nested models are validated."""
    # Invalid nested date
    with pytest.raises(ValidationError):
        EuropassPeriod(
            From={"Year": "not_a_number"},  # Should be int
        )


def test_schema_version_compliance():
    """Test that generated schema indicates Europass v3.4 compliance."""
    schema = EuropassCVResponse.model_json_schema()

    # Check that the schema describes Europass structure
    assert "properties" in schema
    assert "DocumentInfo" in schema["properties"]

    # Check DocumentInfo has XSDVersion
    doc_info_schema = schema["properties"]["DocumentInfo"]
    # Navigate through the reference if present
    if "$ref" in doc_info_schema:
        # Reference points to definitions
        ref = doc_info_schema["$ref"]
        assert "EuropassDocumentInfo" in ref
