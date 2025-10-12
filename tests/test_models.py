"""Tests for core models."""

import pytest
from datetime import date
from eurocv.core.models import (
    PersonalInfo, WorkExperience, Education, Language, Skill, Resume
)


def test_personal_info_creation():
    """Test PersonalInfo model creation."""
    info = PersonalInfo(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+31612345678"
    )
    
    assert info.first_name == "John"
    assert info.last_name == "Doe"
    assert str(info.email) == "john.doe@example.com"
    assert info.phone == "+31612345678"


def test_work_experience_creation():
    """Test WorkExperience model creation."""
    exp = WorkExperience(
        position="Software Engineer",
        employer="Tech Corp",
        city="Amsterdam",
        country="Netherlands",
        start_date=date(2020, 1, 1),
        end_date=date(2023, 12, 31),
        description="Developed software solutions"
    )
    
    assert exp.position == "Software Engineer"
    assert exp.employer == "Tech Corp"
    assert exp.start_date == date(2020, 1, 1)
    assert not exp.current


def test_education_creation():
    """Test Education model creation."""
    edu = Education(
        title="Bachelor of Science",
        organization="University of Amsterdam",
        city="Amsterdam",
        country="Netherlands",
        start_date=date(2016, 9, 1),
        end_date=date(2020, 6, 30)
    )
    
    assert edu.title == "Bachelor of Science"
    assert edu.organization == "University of Amsterdam"


def test_language_creation():
    """Test Language model creation."""
    lang = Language(
        language="Dutch",
        listening="C1",
        reading="C2",
        speaking="C1",
        writing="B2"
    )
    
    assert lang.language == "Dutch"
    assert lang.listening == "C1"
    assert not lang.is_native


def test_language_native():
    """Test native language."""
    lang = Language(language="English", is_native=True)
    
    assert lang.is_native
    assert lang.listening is None


def test_skill_creation():
    """Test Skill model creation."""
    skill = Skill(name="Python", level="Expert", category="technical")
    
    assert skill.name == "Python"
    assert skill.level == "Expert"
    assert skill.category == "technical"


def test_resume_creation():
    """Test Resume model creation."""
    resume = Resume()
    
    assert resume.personal_info is not None
    assert isinstance(resume.work_experience, list)
    assert isinstance(resume.education, list)
    assert isinstance(resume.languages, list)
    assert isinstance(resume.skills, list)
    assert resume.summary is None


def test_resume_with_data():
    """Test Resume with populated data."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Jane", last_name="Smith"),
        work_experience=[
            WorkExperience(position="Developer", employer="Company A")
        ],
        education=[
            Education(title="MSc Computer Science", organization="TU Delft")
        ],
        languages=[
            Language(language="English", is_native=True)
        ],
        skills=[
            Skill(name="Python"),
            Skill(name="JavaScript")
        ],
        summary="Experienced software developer"
    )
    
    assert resume.personal_info.first_name == "Jane"
    assert len(resume.work_experience) == 1
    assert len(resume.education) == 1
    assert len(resume.languages) == 1
    assert len(resume.skills) == 2
    assert resume.summary == "Experienced software developer"

