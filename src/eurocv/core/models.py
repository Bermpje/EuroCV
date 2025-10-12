"""Data models for resume and Europass CV."""

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# Intermediate Resume Model (parsed from PDF/DOCX)
class PersonalInfo(BaseModel):
    """Personal information."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    photo: Optional[bytes] = None


class WorkExperience(BaseModel):
    """Work experience entry."""

    position: Optional[str] = None
    employer: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current: bool = False
    description: Optional[str] = None
    activities: list[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""

    title: Optional[str] = None
    organization: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current: bool = False
    description: Optional[str] = None
    level: Optional[str] = None  # ISCED level


class Language(BaseModel):
    """Language skill."""

    language: str
    listening: Optional[str] = None  # CEFR level: A1, A2, B1, B2, C1, C2
    reading: Optional[str] = None
    speaking: Optional[str] = None
    writing: Optional[str] = None
    is_native: bool = False


class Skill(BaseModel):
    """General skill."""

    name: str
    level: Optional[str] = None
    category: Optional[str] = None  # e.g., "technical", "soft", etc.


class Certification(BaseModel):
    """Certification model."""

    name: str
    issuer: Optional[str] = None
    date: Optional[date] = None


class Resume(BaseModel):
    """Intermediate resume model."""

    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_text: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# Europass Models (following Europass schema)
class EuropassIdentification(BaseModel):
    """Europass identification section."""

    PersonName: dict[str, str] = Field(default_factory=dict)
    ContactInfo: dict[str, Any] = Field(default_factory=dict)
    Demographics: dict[str, Any] = Field(default_factory=dict)
    Photo: Optional[dict[str, str]] = None


class EuropassWorkExperience(BaseModel):
    """Europass work experience."""

    Period: dict[str, Any]
    Position: dict[str, str]
    Activities: Optional[str] = None
    Employer: dict[str, Any]


class EuropassEducation(BaseModel):
    """Europass education entry."""

    Period: dict[str, Any]
    Title: str
    Organisation: dict[str, Any]
    Level: Optional[str] = None


class EuropassLanguage(BaseModel):
    """Europass language skill."""

    Description: dict[str, str]
    ProficiencyLevel: dict[str, str]


class EuropassSkills(BaseModel):
    """Europass skills section."""

    Communication: Optional[dict[str, str]] = None
    Organisational: Optional[dict[str, str]] = None
    JobRelated: Optional[dict[str, str]] = None
    Computer: Optional[dict[str, str]] = None
    Other: Optional[dict[str, str]] = None


class EuropassCV(BaseModel):
    """Europass CV model (simplified)."""

    DocumentInfo: dict[str, Any] = Field(default_factory=dict)
    LearnerInfo: dict[str, Any] = Field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON dict."""
        return self.model_dump(exclude_none=True)

    def to_xml(self) -> str:
        """Convert to XML string."""
        # This will be implemented in the validate module
        from eurocv.core.validate.schema_validator import convert_to_xml

        return convert_to_xml(self.to_json())


class ConversionResult(BaseModel):
    """Result of conversion."""

    json_data: Optional[dict[str, Any]] = Field(default=None, alias="json")
    xml_data: Optional[str] = Field(default=None, alias="xml")
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    # Provide properties for backward compatibility
    @property
    def json(self) -> Optional[dict[str, Any]]:
        """Get JSON data."""
        return self.json_data

    @property
    def xml(self) -> Optional[str]:
        """Get XML data."""
        return self.xml_data
