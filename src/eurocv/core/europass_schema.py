"""Pydantic models for Europass CV v3.4 schema.

This module provides fully-typed Pydantic models representing the complete
Europass v3.4 schema structure. These models enable:
- Machine-readable schema for API consumers
- Type-safe API responses
- IDE autocomplete and validation
- Client code generation (TypeScript, Python, etc.)

Reference: https://europa.eu/europass/en/europass-tools/developers
"""

from typing import Any, Optional

from pydantic import BaseModel

# ============================================================================
# Basic Building Blocks
# ============================================================================


class EuropassDate(BaseModel):
    """Europass date structure with Year/Month/Day."""

    Year: int
    Month: Optional[int] = None
    Day: Optional[int] = None


class EuropassPeriod(BaseModel):
    """Europass period with start and end dates."""

    From: Optional[EuropassDate] = None
    To: Optional[EuropassDate] = None
    Current: Optional[bool] = None


class EuropassCode(BaseModel):
    """Code/Label pair used throughout Europass schema."""

    Code: str
    Label: Optional[str] = None


class EuropassContact(BaseModel):
    """Generic contact information."""

    Contact: str


class EuropassContactWithUse(BaseModel):
    """Contact information with usage type."""

    Contact: str
    Use: Optional[EuropassCode] = None


# ============================================================================
# Address & Location
# ============================================================================


class EuropassCountry(BaseModel):
    """Country with ISO code and label."""

    Code: str
    Label: Optional[str] = None


class EuropassAddressContact(BaseModel):
    """Address contact details."""

    AddressLine: Optional[str] = None
    AddressLine2: Optional[str] = None
    PostalCode: Optional[str] = None
    Municipality: Optional[str] = None
    Country: Optional[EuropassCountry] = None


class EuropassAddress(BaseModel):
    """Address structure."""

    Contact: EuropassAddressContact


class EuropassContactInfo(BaseModel):
    """Complete contact information."""

    Address: Optional[EuropassAddress] = None
    Email: Optional[EuropassContact] = None
    Telephone: Optional[list[EuropassContactWithUse]] = None
    Website: Optional[list[EuropassContactWithUse]] = None
    InstantMessaging: Optional[list[EuropassContactWithUse]] = None


# ============================================================================
# Identification & Personal Info
# ============================================================================


class EuropassPersonName(BaseModel):
    """Person name structure."""

    Title: Optional[str] = None
    FirstName: str
    Surname: str


class EuropassBirthdate(BaseModel):
    """Birthdate structure."""

    Year: Optional[int] = None
    Month: Optional[int] = None
    Day: Optional[int] = None


class EuropassGender(BaseModel):
    """Gender with code (M/F)."""

    Code: str
    Label: Optional[str] = None


class EuropassNationality(BaseModel):
    """Nationality structure."""

    Code: str
    Label: Optional[str] = None


class EuropassDemographics(BaseModel):
    """Demographic information."""

    Birthdate: Optional[EuropassBirthdate] = None
    Gender: Optional[EuropassGender] = None
    Nationality: Optional[list[EuropassNationality]] = None


class EuropassPhoto(BaseModel):
    """Photo with MIME type and base64 data."""

    MimeType: str
    Data: str
    Metadata: Optional[dict[str, Any]] = None


class EuropassIdentification(BaseModel):
    """Identification section with personal info."""

    PersonName: EuropassPersonName
    ContactInfo: Optional[EuropassContactInfo] = None
    Demographics: Optional[EuropassDemographics] = None
    Photo: Optional[EuropassPhoto] = None


# ============================================================================
# Work Experience
# ============================================================================


class EuropassPosition(BaseModel):
    """Position/job title."""

    Code: Optional[str] = None  # ISCO-08 code
    Label: str


class EuropassEmployerContactInfo(BaseModel):
    """Employer contact information."""

    Address: Optional[EuropassAddress] = None
    Website: Optional[EuropassContact] = None


class EuropassSector(BaseModel):
    """Business sector."""

    Code: Optional[str] = None  # NACE code
    Label: Optional[str] = None


class EuropassEmployer(BaseModel):
    """Employer information."""

    Name: str
    ContactInfo: Optional[EuropassEmployerContactInfo] = None
    Sector: Optional[EuropassSector] = None


class EuropassWorkExperience(BaseModel):
    """Work experience entry."""

    Period: EuropassPeriod
    Position: EuropassPosition
    Activities: Optional[str] = None
    Employer: EuropassEmployer


# ============================================================================
# Education
# ============================================================================


class EuropassOrganisationContactInfo(BaseModel):
    """Organisation contact information."""

    Address: Optional[EuropassAddress] = None
    Website: Optional[EuropassContact] = None


class EuropassOrganisation(BaseModel):
    """Educational organisation."""

    Name: str
    ContactInfo: Optional[EuropassOrganisationContactInfo] = None


class EuropassEducationLevel(BaseModel):
    """Education level (ISCED 2011)."""

    Code: Optional[str] = None
    Label: Optional[str] = None


class EuropassEducation(BaseModel):
    """Education entry."""

    Period: Optional[EuropassPeriod] = None
    Title: str
    Activities: Optional[str] = None
    Skills: Optional[str] = None
    Organisation: Optional[EuropassOrganisation] = None
    Level: Optional[EuropassEducationLevel] = None
    Field: Optional[EuropassCode] = None  # Field of study


# ============================================================================
# Languages
# ============================================================================


class EuropassMotherTongue(BaseModel):
    """Mother tongue language."""

    Description: EuropassCode  # ISO 639-1 code


class EuropassProficiencyLevel(BaseModel):
    """Language proficiency levels (CEFR)."""

    Listening: Optional[str] = None  # A1, A2, B1, B2, C1, C2
    Reading: Optional[str] = None
    SpokenInteraction: Optional[str] = None
    SpokenProduction: Optional[str] = None
    Writing: Optional[str] = None


class EuropassLanguageCertificate(BaseModel):
    """Language certificate."""

    Title: str
    AwardingBody: Optional[str] = None
    Date: Optional[EuropassDate] = None
    Level: Optional[str] = None


class EuropassForeignLanguage(BaseModel):
    """Foreign language with proficiency."""

    Description: EuropassCode  # ISO 639-1 code
    ProficiencyLevel: Optional[EuropassProficiencyLevel] = None
    Certificate: Optional[list[EuropassLanguageCertificate]] = None
    Experience: Optional[list[dict[str, Any]]] = None
    VerifiedBy: Optional[dict[str, Any]] = None


class EuropassLinguisticSkills(BaseModel):
    """Linguistic skills section."""

    MotherTongue: Optional[list[EuropassMotherTongue]] = None
    ForeignLanguage: Optional[list[EuropassForeignLanguage]] = None


# ============================================================================
# Skills
# ============================================================================


class EuropassSkillDescription(BaseModel):
    """Skill description."""

    Label: str


class EuropassDrivingSkill(BaseModel):
    """Driving license information."""

    Description: str


class EuropassSkills(BaseModel):
    """Skills section."""

    Linguistic: Optional[EuropassLinguisticSkills] = None
    Communication: Optional[EuropassSkillDescription] = None
    Organisational: Optional[EuropassSkillDescription] = None
    JobRelated: Optional[EuropassSkillDescription] = None
    Computer: Optional[EuropassSkillDescription] = None
    Driving: Optional[list[EuropassDrivingSkill]] = None
    Other: Optional[EuropassSkillDescription] = None


# ============================================================================
# Achievements & Certifications
# ============================================================================


class EuropassAchievementTitle(BaseModel):
    """Achievement title."""

    Code: Optional[str] = None
    Label: str


class EuropassAchievement(BaseModel):
    """Achievement/certification entry."""

    Title: EuropassAchievementTitle
    Date: Optional[EuropassDate] = None
    Description: Optional[str] = None
    IssuedBy: Optional[str] = None


# ============================================================================
# Headline
# ============================================================================


class EuropassHeadlineType(BaseModel):
    """Headline type."""

    Code: str  # e.g., 'preferred', 'position_applied_for'
    Label: Optional[str] = None


class EuropassHeadlineDescription(BaseModel):
    """Headline description."""

    Label: str


class EuropassHeadline(BaseModel):
    """Professional headline."""

    Type: EuropassHeadlineType
    Description: EuropassHeadlineDescription


# ============================================================================
# Document Info
# ============================================================================


class EuropassDocumentInfo(BaseModel):
    """Document metadata."""

    DocumentType: str  # e.g., 'Europass CV', 'ECV'
    CreationDate: str  # ISO 8601 datetime
    LastUpdateDate: Optional[str] = None
    XSDVersion: str  # e.g., 'V3.3', 'V3.4'
    Generator: str
    Comment: Optional[str] = None


# ============================================================================
# Learner Info (Main Container)
# ============================================================================


class EuropassLearnerInfo(BaseModel):
    """Main container for all CV content."""

    Identification: Optional[EuropassIdentification] = None
    Headline: Optional[EuropassHeadline] = None
    WorkExperience: Optional[list[EuropassWorkExperience]] = None
    Education: Optional[list[EuropassEducation]] = None
    Skills: Optional[EuropassSkills] = None
    Achievement: Optional[list[EuropassAchievement]] = None
    ReferenceTo: Optional[list[dict[str, Any]]] = None  # References/attachments
    Documentation: Optional[list[dict[str, Any]]] = None  # Additional documentation


# ============================================================================
# Root Model
# ============================================================================


class EuropassCVResponse(BaseModel):
    """Complete Europass CV response structure.

    This is the root model for the Europass CV format, containing
    document metadata and all learner information.
    """

    DocumentInfo: EuropassDocumentInfo
    LearnerInfo: EuropassLearnerInfo

    model_config = {
        "json_schema_extra": {
            "example": {
                "DocumentInfo": {
                    "DocumentType": "Europass CV",
                    "CreationDate": "2025-10-25T00:00:00",
                    "Generator": "EuroCV",
                    "XSDVersion": "V3.4",
                },
                "LearnerInfo": {
                    "Identification": {
                        "PersonName": {"FirstName": "John", "Surname": "Doe"},
                        "ContactInfo": {"Email": {"Contact": "john.doe@example.com"}},
                    },
                    "WorkExperience": [
                        {
                            "Period": {
                                "From": {"Year": 2020, "Month": 1, "Day": 1},
                                "Current": True,
                            },
                            "Position": {"Label": "Software Engineer"},
                            "Activities": "Developing web applications",
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
        }
    }
