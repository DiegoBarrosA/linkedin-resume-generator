"""Simplified Pydantic models for LinkedIn profile data - v1 compatibility."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for basic compatibility
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
        
        def dict(self):
            return self.__dict__
        
        def json(self, indent=None):
            import json
            return json.dumps(self.dict(), indent=indent, default=str)


class SkillCategory(str, Enum):
    """Skill categories."""
    TECHNICAL = "Technical Skills"
    PROGRAMMING = "Programming Languages" 
    FRAMEWORKS = "Frameworks & Libraries"
    TOOLS = "Tools & Platforms"
    DATABASES = "Databases"
    CLOUD = "Cloud Platforms"
    PROFESSIONAL = "Professional Skills"
    CERTIFICATIONS = "Certifications"
    LANGUAGES = "Languages"
    OTHER = "Other"


class ContactInfo(BaseModel):
    """Contact information."""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None


class Skill(BaseModel):
    """Individual skill with metadata."""
    name: str
    category: str = "Other"
    endorsements: int = 0
    source: str = "skills_section"
    confidence: float = 1.0


class Experience(BaseModel):
    """Work experience entry."""
    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    skills: List[str] = []
    
    @property
    def is_current(self) -> bool:
        """Check if this is a current position."""
        return not self.end_date or self.end_date.lower() in ["present", "current"]


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    activities: Optional[str] = None
    description: Optional[str] = None


class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuing_organization: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        if not self.expiration_date:
            return False
        return "expired" in self.expiration_date.lower()


class Language(BaseModel):
    """Language proficiency."""
    name: str
    proficiency: Optional[str] = None


class Project(BaseModel):
    """Project entry."""
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    skills: List[str] = []


class VolunteerExperience(BaseModel):
    """Volunteer experience."""
    organization: str
    role: str
    cause: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class Honor(BaseModel):
    """Honor or award."""
    title: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    description: Optional[str] = None


class Publication(BaseModel):
    """Publication entry."""
    title: str
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class SkillsSummary(BaseModel):
    """Skills organized by category."""
    by_category: Dict[str, List[Skill]] = {}
    total_count: int = 0
    total_endorsements: int = 0
    top_skills: List[Skill] = []


class ProfileData(BaseModel):
    """Complete LinkedIn profile data."""
    
    # Basic info
    name: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    
    # Contact info
    contact_info: Optional[ContactInfo] = None
    
    # Profile sections
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    skills_summary: Optional[SkillsSummary] = None
    certifications: List[Certification] = []
    languages: List[Language] = []
    projects: List[Project] = []
    volunteer_experience: List[VolunteerExperience] = []
    honors_awards: List[Honor] = []
    publications: List[Publication] = []
    
    # Metadata
    scraped_at: Optional[datetime] = None
    profile_url: Optional[str] = None
    
    def __init__(self, **data):
        # Set defaults
        if 'contact_info' not in data:
            data['contact_info'] = ContactInfo()
        if 'scraped_at' not in data:
            data['scraped_at'] = datetime.utcnow()
        
        super().__init__(**data)