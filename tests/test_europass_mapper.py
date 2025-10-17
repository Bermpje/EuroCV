"""Tests for Europass mapper."""

from datetime import date

import pytest

from eurocv.core.map.europass_mapper import EuropassMapper
from eurocv.core.models import (
    Education,
    Language,
    PersonalInfo,
    Resume,
    Skill,
    WorkExperience,
)


@pytest.fixture
def sample_resume():
    """Create a sample resume for testing."""
    return Resume(
        personal_info=PersonalInfo(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+31612345678",
            city="Amsterdam",
            country="Netherlands",
        ),
        work_experience=[
            WorkExperience(
                position="Software Engineer",
                employer="Tech Corp",
                city="Amsterdam",
                country="Netherlands",
                start_date=date(2020, 1, 1),
                end_date=date(2023, 12, 31),
                description="Developed software solutions",
            )
        ],
        education=[
            Education(
                title="Bachelor of Science",
                organization="University of Amsterdam",
                start_date=date(2016, 9, 1),
                end_date=date(2020, 6, 30),
            )
        ],
        languages=[
            Language(language="English", is_native=True),
            Language(
                language="Dutch",
                listening="C1",
                reading="C1",
                speaking="B2",
                writing="B2",
            ),
        ],
        skills=[
            Skill(name="Python", category="technical"),
            Skill(name="JavaScript", category="technical"),
            Skill(name="Communication", category="soft"),
        ],
        summary="Experienced software developer",
    )


def test_mapper_initialization():
    """Test mapper initialization."""
    mapper = EuropassMapper(locale="nl-NL", include_photo=False)

    assert mapper.locale == "nl-NL"
    assert not mapper.include_photo


def test_map_basic_resume(sample_resume):
    """Test mapping a basic resume."""
    mapper = EuropassMapper()
    europass = mapper.map(sample_resume)

    data = europass.to_json()

    assert "DocumentInfo" in data
    assert "LearnerInfo" in data
    assert data["DocumentInfo"]["DocumentType"] == "Europass CV"


def test_map_identification(sample_resume):
    """Test mapping personal information."""
    mapper = EuropassMapper()
    europass = mapper.map(sample_resume)

    data = europass.to_json()
    identification = data["LearnerInfo"]["Identification"]

    assert identification["PersonName"]["FirstName"] == "John"
    assert identification["PersonName"]["Surname"] == "Doe"
    assert identification["ContactInfo"]["Email"]["Contact"] == "john.doe@example.com"


def test_map_work_experience(sample_resume):
    """Test mapping work experience."""
    mapper = EuropassMapper()
    europass = mapper.map(sample_resume)

    data = europass.to_json()
    work_exp = data["LearnerInfo"]["WorkExperience"][0]

    assert work_exp["Position"]["Label"] == "Software Engineer"
    assert work_exp["Employer"]["Name"] == "Tech Corp"
    assert "Period" in work_exp


def test_map_education(sample_resume):
    """Test mapping education."""
    mapper = EuropassMapper()
    europass = mapper.map(sample_resume)

    data = europass.to_json()
    education = data["LearnerInfo"]["Education"][0]

    assert education["Title"] == "Bachelor of Science"
    assert education["Organisation"]["Name"] == "University of Amsterdam"


def test_map_languages(sample_resume):
    """Test mapping languages."""
    mapper = EuropassMapper()
    europass = mapper.map(sample_resume)

    data = europass.to_json()
    linguistic = data["LearnerInfo"]["Skills"]["Linguistic"]

    assert len(linguistic["MotherTongue"]) == 1
    assert len(linguistic["ForeignLanguage"]) == 1
    assert linguistic["MotherTongue"][0]["Description"]["Label"] == "English"


def test_map_skills(sample_resume):
    """Test mapping skills."""
    mapper = EuropassMapper()
    europass = mapper.map(sample_resume)

    data = europass.to_json()
    skills = data["LearnerInfo"]["Skills"]

    assert "Computer" in skills
    assert "Python" in skills["Computer"]["Description"]
    assert "JavaScript" in skills["Computer"]["Description"]


def test_map_without_photo():
    """Test mapping without photo."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User", photo=b"fake_photo_data")
    )

    mapper = EuropassMapper(include_photo=False)
    europass = mapper.map(resume)

    data = europass.to_json()
    identification = data["LearnerInfo"]["Identification"]

    assert "Photo" not in identification


def test_map_empty_resume():
    """Test mapping an empty resume."""
    resume = Resume()
    mapper = EuropassMapper()
    europass = mapper.map(resume)

    data = europass.to_json()

    assert "DocumentInfo" in data
    assert "LearnerInfo" in data
