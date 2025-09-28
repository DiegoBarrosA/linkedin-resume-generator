"""Pydantic models for LinkedIn profile data."""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


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
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class Skill(BaseModel):
    """Individual skill with metadata."""
    name: str = Field(..., description="Skill name")
    category: SkillCategory = Field(default=SkillCategory.OTHER, description="Skill category")
    endorsements: int = Field(default=0, ge=0, description="Number of endorsements")
    source: str = Field(default="skills_section", description="Where the skill was extracted from")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Skill name cannot be empty")
        return v.strip()


class Experience(BaseModel):
    """Work experience entry."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    skills: List[str] = Field(default_factory=list, description="Skills extracted from description")
    
    @field_validator("title", "company")
    @classmethod
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Title and company are required")
        return v.strip()
    
    @property
    def is_current(self) -> bool:
        """Check if this is a current position."""
        return not self.end_date or self.end_date.lower() in ["present", "current"]


class Education(BaseModel):
    """Education entry."""
    institution: str = Field(..., description="Institution name")
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    activities: Optional[str] = None
    description: Optional[str] = None
    
    @field_validator("institution")
    @classmethod
    def validate_institution(cls, v):
        if not v or not v.strip():
            raise ValueError("Institution name is required")
        return v.strip()


class Certification(BaseModel):
    """Certification entry."""
    name: str = Field(..., description="Certification name")
    issuing_organization: str = Field(..., description="Issuing organization")
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    
    @field_validator("name", "issuing_organization")
    @classmethod
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Name and issuing organization are required")
        return v.strip()
    
    @property
    def is_expired(self) -> bool:
        """Check if certification is expired."""
        if not self.expiration_date:
            return False
        # Simple check - in real implementation, parse dates properly
        return "expired" in self.expiration_date.lower()


class Language(BaseModel):
    """Language proficiency."""
    name: str = Field(..., description="Language name")
    proficiency: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Language name is required")
        return v.strip()


class Project(BaseModel):
    """Project entry."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Project name is required")
        return v.strip()


class VolunteerExperience(BaseModel):
    """Volunteer experience."""
    organization: str = Field(..., description="Organization name")
    role: str = Field(..., description="Volunteer role")
    cause: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    
    @field_validator("organization", "role")
    @classmethod
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Organization and role are required")
        return v.strip()


class Honor(BaseModel):
    """Honor or award."""
    title: str = Field(..., description="Honor/award title")
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    description: Optional[str] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Honor title is required")
        return v.strip()


class Publication(BaseModel):
    """Publication entry."""
    title: str = Field(..., description="Publication title")
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Publication title is required")
        return v.strip()


class SkillsSummary(BaseModel):
    """Skills organized by category."""
    by_category: Dict[SkillCategory, List[Skill]] = Field(default_factory=dict)
    total_count: int = Field(default=0, ge=0)
    total_endorsements: int = Field(default=0, ge=0)
    top_skills: List[Skill] = Field(default_factory=list)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_totals(cls, values):
        """Calculate summary statistics."""
        by_category = values.get("by_category", {})
        all_skills = []
        total_endorsements = 0
        
        for skills in by_category.values():
            all_skills.extend(skills)
            total_endorsements += sum(skill.endorsements for skill in skills)
        
        values["total_count"] = len(all_skills)
        values["total_endorsements"] = total_endorsements
        values["top_skills"] = sorted(all_skills, key=lambda x: x.endorsements, reverse=True)[:10]
        
        return values


class ProfileData(BaseModel):
    """Complete LinkedIn profile data."""
    
    # Basic info
    name: str = Field(..., description="Full name")
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    
    # Contact info
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    
    # Profile sections
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    skills_summary: SkillsSummary = Field(default_factory=SkillsSummary)
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    volunteer_experience: List[VolunteerExperience] = Field(default_factory=list)
    honors_awards: List[Honor] = Field(default_factory=list)
    publications: List[Publication] = Field(default_factory=list)
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    profile_url: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name is required")
        return v.strip()
    
    @model_validator(mode='before')
    @classmethod
    def update_skills_summary(cls, values):
        """Update skills summary when skills change."""
        skills = values.get("skills", [])
        if skills:
            # Group skills by category
            by_category = {}
            for skill in skills:
                category = skill.category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(skill)
            
            values["skills_summary"] = SkillsSummary(by_category=by_category)
        
        return values
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }