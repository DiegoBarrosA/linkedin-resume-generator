"""Privacy-safe data processing for LinkedIn profiles."""

import re
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass

from ..models.profile import ProfileData, Experience, Education, Skill
from ..utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class PrivacyConfig:
    """Configuration for privacy processing."""
    
    # Personal data redaction
    redact_email: bool = True
    redact_phone: bool = True
    redact_full_address: bool = True
    redact_personal_websites: bool = False
    
    # Professional data
    anonymize_company_names: bool = False
    anonymize_school_names: bool = False
    redact_dates: bool = False
    redact_specific_locations: bool = False
    
    # Content filtering
    remove_personal_projects: bool = False
    filter_sensitive_skills: bool = False
    redact_salary_info: bool = True
    
    # Replacement strategies
    use_generic_replacements: bool = True
    preserve_structure: bool = True


class PrivacyProcessor:
    """Process LinkedIn profile data for privacy compliance."""
    
    def __init__(self, config: Optional[PrivacyConfig] = None):
        """Initialize privacy processor.
        
        Args:
            config: Privacy configuration settings
        """
        self.config = config or PrivacyConfig()
        self._company_mapping: Dict[str, str] = {}
        self._school_mapping: Dict[str, str] = {}
        self._location_mapping: Dict[str, str] = {}
        
        # Patterns for sensitive information
        self._email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self._phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self._ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self._salary_patterns = [
            re.compile(r'\$\s*\d+[,\d]*(?:\.\d{2})?(?:\s*k|\s*thousand|\s*million)?', re.IGNORECASE),
            re.compile(r'\b\d+[,\d]*\s*(?:dollars?|USD|salary|compensation|pay)\b', re.IGNORECASE),
            re.compile(r'\b(?:salary|compensation|pay|wage):\s*\$?\d+', re.IGNORECASE),
        ]
        
        # Sensitive skill keywords
        self._sensitive_skills = {
            'internal tools', 'proprietary', 'confidential', 'classified',
            'secret', 'restricted', 'company-specific', 'internal-only'
        }
    
    async def process_profile(self, profile_data: ProfileData) -> ProfileData:
        """Process profile data for privacy compliance.
        
        Args:
            profile_data: Original profile data
            
        Returns:
            Privacy-processed profile data
        """
        logger.info(f"Processing profile for privacy compliance: {profile_data.name}")
        
        # Create a copy to avoid modifying original data
        processed_data = profile_data.model_copy(deep=True)
        
        # Process contact information
        if processed_data.contact_info and self.config.redact_email:
            processed_data.contact_info.email = self._redact_email(processed_data.contact_info.email)
        
        if processed_data.contact_info and self.config.redact_phone:
            processed_data.contact_info.phone = self._redact_phone(processed_data.contact_info.phone)
        
        if processed_data.contact_info and self.config.redact_full_address:
            processed_data.contact_info.location = self._anonymize_location(
                processed_data.contact_info.location
            )
        
        # Process experience
        if processed_data.experience:
            processed_data.experience = [
                self._process_experience(exp) for exp in processed_data.experience
            ]
        
        # Process education
        if processed_data.education:
            processed_data.education = [
                self._process_education(edu) for edu in processed_data.education
            ]
        
        # Process skills
        if processed_data.skills:
            processed_data.skills = [
                skill for skill in processed_data.skills
                if not self._is_sensitive_skill(skill)
            ]
        
        # Process text fields for sensitive content
        processed_data.summary = self._clean_text_content(processed_data.summary)
        processed_data.location = self._anonymize_location(processed_data.location)
        
        logger.info("Privacy processing completed")
        return processed_data
    
    def _process_experience(self, experience: Experience) -> Experience:
        """Process experience entry for privacy."""
        # Copy the experience
        processed_exp = experience.model_copy(deep=True)
        
        # Anonymize company names if configured
        if self.config.anonymize_company_names:
            processed_exp.company = self._anonymize_company(processed_exp.company)
        
        # Redact dates if configured
        if self.config.redact_dates:
            processed_exp.start_date = "[REDACTED]" if processed_exp.start_date else None
            processed_exp.end_date = "[REDACTED]" if processed_exp.end_date else None
        
        # Process location
        if self.config.redact_specific_locations:
            processed_exp.location = self._anonymize_location(processed_exp.location)
        
        # Clean description
        processed_exp.description = self._clean_text_content(processed_exp.description)
        
        return processed_exp
    
    def _process_education(self, education: Education) -> Education:
        """Process education entry for privacy."""
        processed_edu = education.model_copy(deep=True)
        
        # Anonymize school names if configured
        if self.config.anonymize_school_names:
            processed_edu.institution = self._anonymize_school(processed_edu.institution)
        
        # Redact dates if configured
        if self.config.redact_dates:
            processed_edu.start_date = "[REDACTED]" if processed_edu.start_date else None
            processed_edu.end_date = "[REDACTED]" if processed_edu.end_date else None
        
        # Clean description
        processed_edu.description = self._clean_text_content(processed_edu.description)
        
        return processed_edu
    
    def _redact_email(self, email: Optional[str]) -> Optional[str]:
        """Redact email addresses."""
        if not email:
            return email
        
        if self.config.use_generic_replacements:
            return "[EMAIL_REDACTED]"
        else:
            return self._email_pattern.sub("[EMAIL]", email)
    
    def _redact_phone(self, phone: Optional[str]) -> Optional[str]:
        """Redact phone numbers."""
        if not phone:
            return phone
        
        if self.config.use_generic_replacements:
            return "[PHONE_REDACTED]"
        else:
            return self._phone_pattern.sub("[PHONE]", phone)
    
    def _anonymize_location(self, location: Optional[str]) -> Optional[str]:
        """Anonymize location information."""
        if not location:
            return location
        
        if not self.config.redact_specific_locations:
            return location
        
        # Cache mapping for consistency
        if location in self._location_mapping:
            return self._location_mapping[location]
        
        # Extract general area (city/state) and anonymize specifics
        parts = location.split(',')
        if len(parts) >= 2:
            # Keep city and state/country, remove specific addresses
            anonymized = f"{parts[-2].strip()}, {parts[-1].strip()}"
        else:
            anonymized = "[LOCATION_REDACTED]"
        
        self._location_mapping[location] = anonymized
        return anonymized
    
    def _anonymize_company(self, company: str) -> str:
        """Anonymize company names."""
        if company in self._company_mapping:
            return self._company_mapping[company]
        
        # Generate consistent anonymized name
        company_id = len(self._company_mapping) + 1
        anonymized = f"Technology Company {company_id}"
        
        # Try to preserve company type/industry
        company_lower = company.lower()
        if any(word in company_lower for word in ['bank', 'financial', 'finance']):
            anonymized = f"Financial Services Company {company_id}"
        elif any(word in company_lower for word in ['health', 'medical', 'hospital']):
            anonymized = f"Healthcare Company {company_id}"
        elif any(word in company_lower for word in ['university', 'college', 'school']):
            anonymized = f"Educational Institution {company_id}"
        elif any(word in company_lower for word in ['government', 'federal', 'state']):
            anonymized = f"Government Agency {company_id}"
        
        self._company_mapping[company] = anonymized
        return anonymized
    
    def _anonymize_school(self, school: str) -> str:
        """Anonymize school names."""
        if school in self._school_mapping:
            return self._school_mapping[school]
        
        # Generate consistent anonymized name
        school_id = len(self._school_mapping) + 1
        anonymized = f"University {school_id}"
        
        # Try to preserve school type
        school_lower = school.lower()
        if any(word in school_lower for word in ['community', 'college']):
            anonymized = f"Community College {school_id}"
        elif 'institute' in school_lower or 'tech' in school_lower:
            anonymized = f"Technical Institute {school_id}"
        
        self._school_mapping[school] = anonymized
        return anonymized
    
    def _clean_text_content(self, text: Optional[str]) -> Optional[str]:
        """Clean text content of sensitive information."""
        if not text:
            return text
        
        cleaned = text
        
        # Remove email addresses
        cleaned = self._email_pattern.sub("[EMAIL]", cleaned)
        
        # Remove phone numbers
        cleaned = self._phone_pattern.sub("[PHONE]", cleaned)
        
        # Remove SSN patterns
        cleaned = self._ssn_pattern.sub("[SSN]", cleaned)
        
        # Remove salary information
        if self.config.redact_salary_info:
            for pattern in self._salary_patterns:
                cleaned = pattern.sub("[SALARY_INFO]", cleaned)
        
        return cleaned
    
    def _is_sensitive_skill(self, skill: Skill) -> bool:
        """Check if skill should be filtered out."""
        if not self.config.filter_sensitive_skills:
            return False
        
        skill_name_lower = skill.name.lower()
        return any(sensitive in skill_name_lower for sensitive in self._sensitive_skills)
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate a report of privacy processing actions taken."""
        return {
            "companies_anonymized": len(self._company_mapping),
            "schools_anonymized": len(self._school_mapping),
            "locations_anonymized": len(self._location_mapping),
            "config": {
                "redact_email": self.config.redact_email,
                "redact_phone": self.config.redact_phone,
                "anonymize_companies": self.config.anonymize_company_names,
                "anonymize_schools": self.config.anonymize_school_names,
                "redact_dates": self.config.redact_dates,
            }
        }


__all__ = ['PrivacyProcessor', 'PrivacyConfig']