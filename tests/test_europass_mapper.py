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
        personal_info=PersonalInfo(
            first_name="Test", last_name="User", photo=b"fake_photo_data"
        )
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


# Phase B Tests: EuropassMapper Coverage Improvements


def test_map_null_dates():
    """Test B8: Mapping with null dates (current work experience)."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Software Engineer",
                employer="Current Corp",
                start_date=date(2022, 1, 1),
                end_date=None,  # Current position
                current=True,
            )
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    work_exp = data["LearnerInfo"]["WorkExperience"][0]
    assert "Period" in work_exp
    # Current positions should have start date but no explicit end date (or marked as current)
    assert work_exp["Period"]["From"]["Year"] == 2022


def test_map_empty_fields():
    """Test B8: Mapping with empty/missing fields."""
    resume = Resume(
        personal_info=PersonalInfo(
            first_name="Test",
            last_name="User",
            email=None,  # Missing email
            phone=None,  # Missing phone
        ),
        work_experience=[
            WorkExperience(
                position="Developer",
                employer=None,  # Missing employer
                start_date=date(2020, 1, 1),
            )
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    # Should not crash and should create valid structure
    assert "DocumentInfo" in data
    assert "LearnerInfo" in data


def test_map_address_components():
    """Test B8: Mapping with full address components."""
    resume = Resume(
        personal_info=PersonalInfo(
            first_name="Test",
            last_name="User",
            street="Test Street 123",
            postal_code="1234 AB",
            city="Amsterdam",
            country="Netherlands",
        )
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    contact_info = data["LearnerInfo"]["Identification"]["ContactInfo"]
    address = contact_info["Address"]["Contact"]

    # Check that address components are present (structure may vary)
    assert "Municipality" in address or "Municipality" in str(address)
    assert "Amsterdam" in str(address)
    assert "Netherlands" in str(address)


def test_map_multiple_work_experiences():
    """Test B8: Mapping with multiple work experiences."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Senior Developer",
                employer="Company A",
                start_date=date(2022, 1, 1),
                end_date=None,
                current=True,
                description="Lead developer for web applications",
            ),
            WorkExperience(
                position="Junior Developer",
                employer="Company B",
                start_date=date(2019, 6, 1),
                end_date=date(2021, 12, 31),
                description="Backend development",
            ),
            WorkExperience(
                position="Intern",
                employer="Company C",
                start_date=date(2018, 9, 1),
                end_date=date(2019, 5, 31),
            ),
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    work_exps = data["LearnerInfo"]["WorkExperience"]
    assert len(work_exps) == 3
    assert work_exps[0]["Position"]["Label"] == "Senior Developer"
    assert work_exps[1]["Position"]["Label"] == "Junior Developer"
    assert work_exps[2]["Position"]["Label"] == "Intern"


def test_map_multiple_education_entries():
    """Test B8: Mapping with multiple education entries."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        education=[
            Education(
                title="Master of Science in Computer Science",
                field_of_study="Computer Science",
                organization="University of Amsterdam",
                start_date=date(2020, 9, 1),
                end_date=date(2022, 6, 30),
                description="cum laude",
            ),
            Education(
                title="Bachelor of Science",
                organization="Hogeschool Rotterdam",
                start_date=date(2016, 9, 1),
                end_date=date(2020, 6, 30),
            ),
            Education(
                title="High School Diploma",
                organization="Local High School",
                start_date=date(2010, 9, 1),
                end_date=date(2016, 6, 30),
            ),
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    education_entries = data["LearnerInfo"]["Education"]
    assert len(education_entries) == 3
    assert education_entries[0]["Title"] == "Master of Science in Computer Science"
    assert education_entries[1]["Title"] == "Bachelor of Science"
    assert education_entries[2]["Title"] == "High School Diploma"


def test_map_date_formatting():
    """Test B8: Mapping with various date formats."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Developer",
                employer="Test Corp",
                start_date=date(2020, 1, 15),  # Mid-month
                end_date=date(2023, 12, 1),  # Start of month
            )
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    work_exp = data["LearnerInfo"]["WorkExperience"][0]
    period = work_exp["Period"]

    assert period["From"]["Year"] == 2020
    # Month may be formatted as string ("--01") or int (1)
    assert period["From"]["Month"] in [1, "--01", "01"]
    assert period["To"]["Year"] == 2023
    assert period["To"]["Month"] in [12, "--12", "12"]


def test_map_work_experience_without_dates():
    """Test B8: Mapping work experience without dates."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Consultant",
                employer="Various Clients",
                description="Freelance consulting work",
                # No dates provided
            )
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    # Should not crash
    work_exp = data["LearnerInfo"]["WorkExperience"][0]
    assert work_exp["Position"]["Label"] == "Consultant"


def test_map_education_with_field_of_study():
    """Test B8: Mapping education with separate field of study."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        education=[
            Education(
                title="Master in Data Science",
                field_of_study="Data Science and AI",
                organization="Technical University",
                start_date=date(2019, 9, 1),
                end_date=date(2021, 8, 31),
            )
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    education = data["LearnerInfo"]["Education"][0]
    assert education["Title"] == "Master in Data Science"
    # Field of study should be included in the structure


def test_map_skills_without_categories():
    """Test B8: Mapping skills without explicit categories."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        skills=[
            Skill(name="Python"),  # No category
            Skill(name="Docker"),
            Skill(name="AWS"),
        ],
    )

    mapper = EuropassMapper()
    europass = mapper.map(resume)
    data = europass.to_json()

    # Should still map to Computer skills by default
    skills = data["LearnerInfo"]["Skills"]
    assert "Computer" in skills
