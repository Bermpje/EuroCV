"""Data models for resume and Europass CV."""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


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
    activities: List[str] = Field(default_factory=list)


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


class Resume(BaseModel):
    """Intermediate resume model."""
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Europass Models (following Europass schema)
class EuropassIdentification(BaseModel):
    """Europass identification section."""
    PersonName: Dict[str, str] = Field(default_factory=dict)
    ContactInfo: Dict[str, Any] = Field(default_factory=dict)
    Demographics: Dict[str, Any] = Field(default_factory=dict)
    Photo: Optional[Dict[str, str]] = None


class EuropassWorkExperience(BaseModel):
    """Europass work experience."""
    Period: Dict[str, Any]
    Position: Dict[str, str]
    Activities: Optional[str] = None
    Employer: Dict[str, Any]


class EuropassEducation(BaseModel):
    """Europass education entry."""
    Period: Dict[str, Any]
    Title: str
    Organisation: Dict[str, Any]
    Level: Optional[str] = None


class EuropassLanguage(BaseModel):
    """Europass language skill."""
    Description: Dict[str, str]
    ProficiencyLevel: Dict[str, str]


class EuropassSkills(BaseModel):
    """Europass skills section."""
    Communication: Optional[Dict[str, str]] = None
    Organisational: Optional[Dict[str, str]] = None
    JobRelated: Optional[Dict[str, str]] = None
    Computer: Optional[Dict[str, str]] = None
    Other: Optional[Dict[str, str]] = None


class EuropassCV(BaseModel):
    """Europass CV model (simplified)."""
    DocumentInfo: Dict[str, Any] = Field(default_factory=dict)
    LearnerInfo: Dict[str, Any] = Field(default_factory=dict)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON dict."""
        return self.model_dump(exclude_none=True)
    
    def to_xml(self) -> str:
        """Convert to XML string."""
        # This will be implemented in the validate module
        from eurocv.core.validate.schema_validator import convert_to_xml
        return convert_to_xml(self.to_json())


class ConversionResult(BaseModel):
    """Result of conversion."""
    json: Optional[Dict[str, Any]] = None
    xml: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

