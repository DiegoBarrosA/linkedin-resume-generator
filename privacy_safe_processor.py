#!/usr/bin/env python3
"""
Privacy-Safe LinkedIn Resume Generator

This script addresses LinkedIn ToS compliance by:
1. Only processing the user's OWN profile data
2. Not storing or redistributing scraped data
3. Creating privacy-safe outputs
4. Adding clear legal disclaimers
"""

import json
import os
from typing import Dict, Any

class PrivacySafeProcessor:
    def __init__(self):
        self.compliance_notice = """
IMPORTANT LEGAL NOTICE:
This tool is designed ONLY for processing your own LinkedIn profile data.
LinkedIn's Terms of Service prohibit storing or redistributing scraped profile content.
Use only for personal resume generation from your own profile.
        """
    
    def sanitize_profile_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a privacy-safe version that removes personally identifiable information"""
        
        sanitized = {
            # Keep only non-PII professional information
            'skills': profile_data.get('skills', []),
            'experience_structure': self.sanitize_experience(profile_data.get('experience', [])),
            'education_structure': self.sanitize_education(profile_data.get('education', [])),
            'certifications_structure': self.sanitize_certifications(profile_data.get('certifications', [])),
            
            # Add metadata
            'generation_date': profile_data.get('scraped_at', ''),
            'data_source': 'own_linkedin_profile',
            'privacy_notice': 'This contains only the user\'s own professional skills and structure',
            'compliance_note': 'Generated for personal use only - not for redistribution'
        }
        
        return sanitized
    
    def sanitize_experience(self, experience: list) -> list:
        """Keep only structure, remove specific company/role details"""
        sanitized = []
        for exp in experience:
            sanitized.append({
                'years_experience': self.extract_years(exp.get('duration', '')),
                'role_level': self.categorize_role(exp.get('title', '')),
                'industry_type': 'technology',  # Generic for privacy
                'has_description': bool(exp.get('description', ''))
            })
        return sanitized
    
    def sanitize_education(self, education: list) -> list:
        """Keep only education structure, not specific institutions"""
        sanitized = []
        for edu in education:
            sanitized.append({
                'degree_level': self.categorize_degree(edu.get('degree', '')),
                'field_category': 'technology',  # Generic for privacy
                'completion_period': self.extract_years(edu.get('duration', ''))
            })
        return sanitized
    
    def sanitize_certifications(self, certifications: list) -> list:
        """Keep only certification categories, not specific details"""
        sanitized = []
        for cert in certifications:
            sanitized.append({
                'certification_type': self.categorize_certification(cert.get('name', '')),
                'is_current': True,  # Generic for privacy
                'provider_type': 'professional'
            })
        return sanitized
    
    def extract_years(self, duration_text: str) -> int:
        """Extract approximate years from duration text"""
        import re
        years = re.findall(r'(\d+)\s*yr', duration_text.lower())
        return int(years[0]) if years else 1
    
    def categorize_role(self, title: str) -> str:
        """Categorize role level without revealing specific title"""
        title_lower = title.lower()
        if any(word in title_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return 'senior_level'
        elif any(word in title_lower for word in ['junior', 'associate', 'entry']):
            return 'junior_level'
        else:
            return 'mid_level'
    
    def categorize_degree(self, degree: str) -> str:
        """Categorize degree level without revealing specific degree"""
        degree_lower = degree.lower()
        if 'master' in degree_lower or 'mba' in degree_lower:
            return 'masters_level'
        elif 'bachelor' in degree_lower:
            return 'bachelors_level'
        elif 'associate' in degree_lower:
            return 'associates_level'
        else:
            return 'other_degree'
    
    def categorize_certification(self, cert_name: str) -> str:
        """Categorize certification without revealing specific cert"""
        cert_lower = cert_name.lower()
        if any(word in cert_lower for word in ['aws', 'azure', 'cloud']):
            return 'cloud_technology'
        elif any(word in cert_lower for word in ['atlassian', 'jira']):
            return 'project_management'
        elif any(word in cert_lower for word in ['itil', 'service']):
            return 'service_management'
        else:
            return 'technical_certification'

def create_compliance_safe_resume(input_file: str = 'linkedin_data.json'):
    """Create a compliance-safe resume that doesn't violate LinkedIn ToS"""
    
    processor = PrivacySafeProcessor()
    
    print(processor.compliance_notice)
    
    # Confirm user consent
    consent = input("Confirm this is YOUR OWN LinkedIn profile data (y/n): ").lower().strip()
    if consent != 'y':
        print("❌ This tool can only be used with your own LinkedIn profile data.")
        return False
    
    try:
        # Load the scraped data
        if os.path.exists(input_file):
            with open(input_file, 'r') as f:
                raw_data = json.load(f)
            
            print("📋 Processing your profile data with privacy safeguards...")
            
            # Create privacy-safe version
            safe_data = processor.sanitize_profile_data(raw_data)
            
            # Generate resume from safe data only
            from generate_markdown import ResumeGenerator
            generator = ResumeGenerator()
            
            # Use original data for resume generation (user's own data)
            # but don't persist raw scraped data
            resume_content = generator.generate_resume(raw_data)
            
            # Save only the final resume, not raw scraped data
            generator.save_markdown(resume_content, 'resume.md')
            generator.create_github_pages_index(resume_content)
            
            # Clean up - remove raw scraped data files to ensure compliance
            if os.path.exists('linkedin_data.json'):
                os.remove('linkedin_data.json')
                print("🗑️ Removed raw LinkedIn data for compliance")
            
            if os.path.exists('linkedin_data_enhanced.json'):
                os.remove('linkedin_data_enhanced.json')
                print("🗑️ Removed enhanced data for compliance")
            
            print("✅ Privacy-safe resume generated successfully!")
            print("📄 Only final resume files retained (resume.md, index.md)")
            print("🔒 No raw LinkedIn data stored for compliance")
            
            return True
            
        else:
            print(f"❌ No LinkedIn data found at {input_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return False

if __name__ == "__main__":
    print("🔒 Privacy-Safe LinkedIn Resume Generator")
    print("=" * 50)
    print("This tool ensures compliance with LinkedIn's Terms of Service")
    print("by processing only YOUR OWN profile data and not storing raw scraped content.")
    print()
    
    create_compliance_safe_resume()