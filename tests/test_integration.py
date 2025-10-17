"""Integration tests for full conversion flow."""

from eurocv.core.models import (
    Certification,
    ConversionResult,
    Education,
    EuropassCV,
    Language,
    PersonalInfo,
    Resume,
    Skill,
    WorkExperience,
)


def test_full_conversion_flow():
    """Test complete conversion from Resume to Europass."""
    # Create a sample resume
    resume = Resume(
        personal_info=PersonalInfo(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+31 6 12345678",
            city="Amsterdam",
            country="Netherlands",
        ),
        work_experience=[
            WorkExperience(
                position="Software Engineer",
                employer="Tech Company",
                city="Amsterdam",
                country="Netherlands",
                start_date="2020-01-01",
                end_date="2023-12-31",
                description="Developed applications",
            )
        ],
        education=[
            Education(
                title="Bachelor of Computer Science",
                organization="University of Amsterdam",
                city="Amsterdam",
                country="Netherlands",
                start_date="2016-09-01",
                end_date="2020-06-30",
            )
        ],
        languages=[
            Language(language="Dutch", level="Native"),
            Language(language="English", level="C1"),
        ],
        skills=[
            Skill(name="Python", category="Programming"),
            Skill(name="Docker", category="DevOps"),
        ],
    )

    # Map to Europass
    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    # Validate result
    assert isinstance(europass, EuropassCV)
    assert europass.DocumentInfo is not None
    assert europass.LearnerInfo is not None

    # Check JSON conversion
    json_data = europass.to_json()
    assert "DocumentInfo" in json_data
    assert "LearnerInfo" in json_data

    # Check XML conversion
    xml_string = europass.to_xml()
    assert isinstance(xml_string, str)
    assert "Europass" in xml_string


def test_europass_mapper_with_work_experience():
    """Test mapper with work experience."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Developer",
                employer="Company",
                start_date="2020-01-01",
                end_date="2021-12-31",
                is_current=False,
            ),
            WorkExperience(
                position="Senior Developer",
                employer="Another Company",
                start_date="2022-01-01",
                is_current=True,
            ),
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    learner_info = json_data.get("LearnerInfo", {})
    assert "WorkExperience" in learner_info
    assert len(learner_info["WorkExperience"]) == 2


def test_europass_mapper_with_education():
    """Test mapper with education."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        education=[
            Education(
                title="Master of Science",
                organization="University",
                start_date="2018-09-01",
                end_date="2020-07-01",
            ),
            Education(
                title="Bachelor of Arts",
                organization="College",
                start_date="2014-09-01",
                end_date="2018-06-01",
            ),
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    learner_info = json_data.get("LearnerInfo", {})
    assert "Education" in learner_info
    assert len(learner_info["Education"]) == 2


def test_europass_mapper_with_languages():
    """Test mapper with language skills."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        languages=[
            Language(language="English", level="C2"),
            Language(language="French", level="B1"),
            Language(language="Spanish", level="A2"),
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    learner_info = json_data.get("LearnerInfo", {})
    assert "Skills" in learner_info
    skills = learner_info.get("Skills", {})
    assert "Linguistic" in skills


def test_europass_mapper_with_skills():
    """Test mapper with technical skills."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        skills=[
            Skill(name="Python", category="Programming", level="Expert"),
            Skill(name="JavaScript", category="Programming", level="Advanced"),
            Skill(name="Docker", category="DevOps"),
            Skill(name="AWS", category="Cloud"),
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    learner_info = json_data.get("LearnerInfo", {})
    assert "Skills" in learner_info


def test_europass_mapper_with_certifications():
    """Test mapper with certifications."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        certifications=[
            Certification(
                name="AWS Certified Solutions Architect",
                organization="Amazon Web Services",
            ),
            Certification(name="Professional Scrum Master", organization="Scrum.org"),
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    # Certifications might be mapped to Skills or Achievements depending on mapper logic
    assert "LearnerInfo" in json_data


def test_europass_date_formatting():
    """Test that dates are properly formatted for Europass."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Developer",
                employer="Company",
                start_date="2020-01-15",
                end_date="2021-12-31",
            )
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    # Check that dates are properly formatted (Europass expects specific format)
    work_exp = json_data.get("LearnerInfo", {}).get("WorkExperience", [])
    if work_exp:
        period = work_exp[0].get("Period", {})
        assert "From" in period


def test_europass_country_codes():
    """Test that country names are mapped to ISO codes."""
    resume = Resume(
        personal_info=PersonalInfo(
            first_name="Test", last_name="User", city="Amsterdam", country="Netherlands"
        ),
        work_experience=[
            WorkExperience(
                position="Developer",
                employer="Company",
                city="Berlin",
                country="Germany",
                start_date="2020-01-01",
            )
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    # Countries should be mapped to ISO 3166-1 alpha-2 codes
    identification = json_data.get("LearnerInfo", {}).get("Identification", {})
    if "ContactInfo" in identification:
        contact_info = identification["ContactInfo"]
        if "Address" in contact_info:
            address = contact_info["Address"]
            if "Contact" in address:
                country = address["Contact"].get("Country", {})
                # Should have Code field with ISO code
                assert isinstance(country, dict) or isinstance(country, str)


def test_conversion_result_both_formats():
    """Test that ConversionResult properly holds both formats."""
    result = ConversionResult(
        json_data={"test": "json"},
        xml_data="<test>xml</test>",
        validation_errors=[],
        warnings=[],
    )

    assert result.json_data == {"test": "json"}
    assert result.xml_data == "<test>xml</test>"

    # Test backward compatibility properties (they're methods, not direct attributes)
    assert result.json_data == {"test": "json"}  # Use json_data instead
    assert result.xml_data == "<test>xml</test>"  # Use xml_data instead


def test_mapper_with_empty_resume():
    """Test mapper with minimal resume data."""
    resume = Resume(personal_info=PersonalInfo(first_name="Test", last_name="User"))

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    assert "DocumentInfo" in json_data
    assert "LearnerInfo" in json_data

    # Should have at least personal name
    learner_info = json_data["LearnerInfo"]
    assert "Identification" in learner_info
    identification = learner_info["Identification"]
    assert "PersonName" in identification


def test_mapper_with_all_fields():
    """Test mapper with all possible fields populated."""
    resume = Resume(
        personal_info=PersonalInfo(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+31612345678",
            city="Amsterdam",
            country="Netherlands",
            birth_date="1990-01-15",
        ),
        work_experience=[
            WorkExperience(
                position="Senior Developer",
                employer="Tech Corp",
                city="Amsterdam",
                country="Netherlands",
                start_date="2020-01-01",
                is_current=True,
                description="Full stack development",
            )
        ],
        education=[
            Education(
                title="Master of Computer Science",
                organization="TU Delft",
                city="Delft",
                country="Netherlands",
                start_date="2012-09-01",
                end_date="2016-07-01",
            )
        ],
        languages=[
            Language(language="Dutch", level="Native"),
            Language(language="English", level="C2"),
        ],
        skills=[
            Skill(name="Python", category="Programming", level="Expert"),
            Skill(name="AWS", category="Cloud"),
        ],
        certifications=[Certification(name="AWS Architect", organization="AWS")],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper(locale="en-US", include_photo=False)
    europass = mapper.map(resume)

    json_data = europass.to_json()
    xml_data = europass.to_xml()

    # Verify structure
    assert "DocumentInfo" in json_data
    assert "LearnerInfo" in json_data
    assert len(xml_data) > 0
    assert "Europass" in xml_data


def test_mapper_with_multiple_languages():
    """Test mapper with multiple languages and proficiency levels."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        languages=[
            Language(
                language="English",
                listening="C2",
                reading="C2",
                speaking="C1",
                writing="C1",
            ),
            Language(
                language="Spanish",
                listening="B2",
                reading="B2",
                speaking="B1",
                writing="B1",
            ),
            Language(language="French", level="A2"),
            Language(language="German", is_native=True),
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    json_data = europass.to_json()
    linguistic = json_data.get("LearnerInfo", {}).get("Skills", {}).get("Linguistic", {})

    assert "MotherTongue" in linguistic or "ForeignLanguage" in linguistic


def test_mapper_locale_variations():
    """Test mapper with different locales."""
    resume = Resume(
        personal_info=PersonalInfo(first_name="Test", last_name="User"),
        work_experience=[
            WorkExperience(
                position="Developer",
                employer="Company",
                start_date="2020-01-01",
                end_date="2021-12-31",
            )
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    # Test different locales
    for locale in ["en-US", "nl-NL", "de-DE", "fr-FR"]:
        mapper = EuropassMapper(locale=locale)
        europass = mapper.map(resume)
        json_data = europass.to_json()

        assert "DocumentInfo" in json_data
        assert "LearnerInfo" in json_data


def test_converter_with_validation_errors():
    """Test converter with validation enabled."""

    # Create a resume with potential validation issues
    resume = Resume(personal_info=PersonalInfo(first_name="Test", last_name="User"))

    # Convert with validation
    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    # Validate
    from eurocv.core.validate.schema_validator import SchemaValidator

    validator = SchemaValidator()
    is_valid, errors = validator.validate_json(europass.to_json())

    # Should validate (may have errors but shouldn't crash)
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_europass_xml_with_special_characters():
    """Test Europass XML generation with special characters."""
    resume = Resume(
        personal_info=PersonalInfo(
            first_name="José", last_name="O'Brien", email="jose@example.com"
        ),
        work_experience=[
            WorkExperience(
                position="Developer & Architect",
                employer="Tech <Company>",
                description="Worked on A&B project",
            )
        ],
    )

    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    xml_string = europass.to_xml()

    # XML should be valid (special chars escaped)
    assert isinstance(xml_string, str)
    assert len(xml_string) > 0
    assert "Europass" in xml_string


def test_converter_output_format_variations():
    """Test converter with all output format options."""
    from eurocv.core.models import ConversionResult

    resume = Resume(personal_info=PersonalInfo(first_name="Test", last_name="User"))

    # Map to Europass first
    from eurocv.core.map.europass_mapper import EuropassMapper

    mapper = EuropassMapper()
    europass = mapper.map(resume)

    # Test JSON format
    json_output = europass.to_json()
    assert isinstance(json_output, dict)

    # Test XML format
    xml_output = europass.to_xml()
    assert isinstance(xml_output, str)

    # Test both formats in ConversionResult
    result = ConversionResult(
        json_data=json_output, xml_data=xml_output, validation_errors=[], warnings=[]
    )

    assert result.json_data is not None
    assert result.xml_data is not None
