#!/usr/bin/env python3
"""
Markdown Resume Generator

This script converts LinkedIn profile data (JSON) into a formatted markdown resume.
It includes templates and styling for a professional-looking resume.

Usage:
    python generate_markdown.py [input_json] [output_md]
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Template

class ResumeGenerator:
    def __init__(self):
        self.template = self.get_resume_template()
    
    def get_resume_template(self) -> str:
        """
        Comprehensive resume template using Jinja2 templating
        """
        return """# {{ name }}

{% if headline %}**{{ headline }}**{% endif %}

---

## Contact Information

{% if contact.email %}📧 {{ contact.email }}{% endif %}
{% if contact.phone %} | 📱 {{ contact.phone }}{% endif %}
{% if location %} | 📍 {{ location }}{% endif %}
{% if contact.linkedin_url %} | 🔗 [LinkedIn]({{ contact.linkedin_url }}){% endif %}

---

## Professional Summary

{{ about }}

---

## Core Competencies & Skills

{% set skill_categories = skills | groupby('category') %}
{% for category, category_skills in skill_categories %}
{% if category != 'General' %}**{{ category }}:**{% endif %}
{% for skill in category_skills[:10] %}
- {{ skill.name }}{% if skill.endorsements > 0 %} ({{ skill.endorsements }} endorsements){% endif %}
{%- endfor %}

{% endfor %}

---

## Professional Experience

{% for exp in experience %}
### {{ exp.title }}
**{{ exp.company }}** | {{ exp.duration }}

{{ exp.description }}

{% endfor %}

---

## Education

{% for edu in education %}
### {{ edu.degree }}
**{{ edu.school }}** | {{ edu.duration }}

{% endfor %}

{% if certifications %}
---

## Licenses & Certifications

{% for cert in certifications %}
### {{ cert.name }}
**{{ cert.issuer }}**{% if cert.date %} | {{ cert.date }}{% endif %}
{% if cert.credential_id %}*Credential ID: {{ cert.credential_id }}*{% endif %}

{% endfor %}
{% endif %}

{% if projects %}
---

## Notable Projects

{% for project in projects %}
### {{ project.name }}
{% if project.associated_with %}**{{ project.associated_with }}**{% endif %}{% if project.date_range %} | {{ project.date_range }}{% endif %}

{{ project.description }}
{% if project.url %}🔗 [Project Link]({{ project.url }}){% endif %}

{% endfor %}
{% endif %}

{% if volunteer_experience %}
---

## Volunteer Experience

{% for vol in volunteer_experience %}
### {{ vol.role }}
**{{ vol.organization }}** | {{ vol.duration }}

{{ vol.description }}

{% endfor %}
{% endif %}

{% if honors_awards %}
---

## Honors & Awards

{% for award in honors_awards %}
### {{ award.name }}
**{{ award.issuer }}** | {{ award.date }}

{{ award.description }}

{% endfor %}
{% endif %}

{% if publications %}
---

## Publications

{% for pub in publications %}
### {{ pub.title }}
**{{ pub.publisher }}** | {{ pub.date }}

{{ pub.description }}
{% if pub.url %}🔗 [Publication Link]({{ pub.url }}){% endif %}

{% endfor %}
{% endif %}

{% if languages and languages|length > 0 %}
---

## Languages

{% for lang in languages %}
- **{{ lang.language }}**: {{ lang.proficiency }}
{% endfor %}
{% endif %}

{% if recommendations and recommendations|length > 0 %}
---

## Recommendations

{% for rec in recommendations[:3] %}
> "{{ rec.text }}"
> 
> — **{{ rec.recommender }}**, {{ rec.recommender_title }}

{% endfor %}
{% endif %}

---

*Last updated: {{ updated_date }}*  
*Generated automatically from LinkedIn profile data*
"""

    def clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = ' '.join(text.split())
        
        # Replace common LinkedIn formatting
        text = text.replace('•', '-')
        text = text.replace('–', '-')
        text = text.replace('—', '-')
        
        return text
    
    def format_experience(self, experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format experience entries"""
        formatted_exp = []
        
        for exp in experience:
            formatted_entry = {
                'title': self.clean_text(exp.get('title', '')),
                'company': self.clean_text(exp.get('company', '')),
                'duration': self.clean_text(exp.get('duration', '')),
                'description': self.clean_text(exp.get('description', ''))
            }
            
            # Only add if we have meaningful content
            if formatted_entry['title'] or formatted_entry['company']:
                formatted_exp.append(formatted_entry)
        
        return formatted_exp
    
    def format_education(self, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format education entries"""
        formatted_edu = []
        
        for edu in education:
            formatted_entry = {
                'school': self.clean_text(edu.get('school', '')),
                'degree': self.clean_text(edu.get('degree', '')),
                'duration': self.clean_text(edu.get('duration', ''))
            }
            
            # Only add if we have meaningful content
            if formatted_entry['school'] or formatted_entry['degree']:
                formatted_edu.append(formatted_entry)
        
        return formatted_edu
    
    def format_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format and clean skills list with categories and endorsements"""
        formatted_skills = []
        seen_skills = set()
        
        for skill in skills:
            if isinstance(skill, str):
                # Handle old format (simple string list)
                cleaned_skill = self.clean_text(skill)
                if cleaned_skill and cleaned_skill.lower() not in seen_skills:
                    formatted_skills.append({
                        'name': cleaned_skill,
                        'endorsements': 0,
                        'category': 'General'
                    })
                    seen_skills.add(cleaned_skill.lower())
            elif isinstance(skill, dict):
                # Handle new format (detailed skill objects)
                cleaned_name = self.clean_text(skill.get('name', ''))
                if cleaned_name and cleaned_name.lower() not in seen_skills:
                    formatted_skills.append({
                        'name': cleaned_name,
                        'endorsements': skill.get('endorsements', 0),
                        'category': skill.get('category', 'General')
                    })
                    seen_skills.add(cleaned_name.lower())
        
        # Sort by endorsements (highest first) and limit to top 30
        formatted_skills.sort(key=lambda x: x['endorsements'], reverse=True)
        return formatted_skills[:30]
    
    def format_certifications(self, certifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format certifications list"""
        formatted_certs = []
        
        for cert in certifications:
            formatted_entry = {
                'name': self.clean_text(cert.get('name', '')),
                'issuer': self.clean_text(cert.get('issuer', '')),
                'date': self.clean_text(cert.get('date', '')),
                'credential_id': self.clean_text(cert.get('credential_id', ''))
            }
            
            if formatted_entry['name'] or formatted_entry['issuer']:
                formatted_certs.append(formatted_entry)
        
        return formatted_certs
    
    def format_languages(self, languages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format languages list"""
        formatted_langs = []
        
        for lang in languages:
            formatted_entry = {
                'language': self.clean_text(lang.get('language', '')),
                'proficiency': self.clean_text(lang.get('proficiency', ''))
            }
            
            if formatted_entry['language']:
                formatted_langs.append(formatted_entry)
        
        return formatted_langs
    
    def format_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format projects list"""
        formatted_projects = []
        
        for project in projects:
            formatted_entry = {
                'name': self.clean_text(project.get('name', '')),
                'associated_with': self.clean_text(project.get('associated_with', '')),
                'date_range': self.clean_text(project.get('date_range', '')),
                'description': self.clean_text(project.get('description', '')),
                'url': project.get('url', '')  # Don't clean URLs
            }
            
            if formatted_entry['name']:
                formatted_projects.append(formatted_entry)
        
        return formatted_projects
    
    def format_volunteer_experience(self, volunteer: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format volunteer experience list"""
        formatted_volunteer = []
        
        for vol in volunteer:
            formatted_entry = {
                'role': self.clean_text(vol.get('role', '')),
                'organization': self.clean_text(vol.get('organization', '')),
                'duration': self.clean_text(vol.get('duration', '')),
                'description': self.clean_text(vol.get('description', ''))
            }
            
            if formatted_entry['role'] or formatted_entry['organization']:
                formatted_volunteer.append(formatted_entry)
        
        return formatted_volunteer
    
    def format_honors_awards(self, honors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format honors and awards list"""
        formatted_honors = []
        
        for honor in honors:
            formatted_entry = {
                'name': self.clean_text(honor.get('name', '')),
                'issuer': self.clean_text(honor.get('issuer', '')),
                'date': self.clean_text(honor.get('date', '')),
                'description': self.clean_text(honor.get('description', ''))
            }
            
            if formatted_entry['name'] or formatted_entry['issuer']:
                formatted_honors.append(formatted_entry)
        
        return formatted_honors
    
    def format_publications(self, publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format publications list"""
        formatted_pubs = []
        
        for pub in publications:
            formatted_entry = {
                'title': self.clean_text(pub.get('title', '')),
                'publisher': self.clean_text(pub.get('publisher', '')),
                'date': self.clean_text(pub.get('date', '')),
                'description': self.clean_text(pub.get('description', '')),
                'url': pub.get('url', '')  # Don't clean URLs
            }
            
            if formatted_entry['title'] or formatted_entry['publisher']:
                formatted_pubs.append(formatted_entry)
        
        return formatted_pubs
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recommendations list"""
        formatted_recs = []
        
        for rec in recommendations:
            formatted_entry = {
                'recommender': self.clean_text(rec.get('recommender', '')),
                'recommender_title': self.clean_text(rec.get('recommender_title', '')),
                'text': self.clean_text(rec.get('text', ''))
            }
            
            if formatted_entry['recommender'] and formatted_entry['text']:
                # Limit recommendation text length for readability
                if len(formatted_entry['text']) > 300:
                    formatted_entry['text'] = formatted_entry['text'][:297] + '...'
                formatted_recs.append(formatted_entry)
        
        return formatted_recs[:3]  # Limit to top 3 recommendations
    
    def generate_resume(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive markdown resume from LinkedIn profile data
        """
        # Prepare template variables with all sections
        template_vars = {
            'name': self.clean_text(profile_data.get('name', 'Your Name')),
            'headline': self.clean_text(profile_data.get('headline', '')),
            'location': self.clean_text(profile_data.get('location', '')),
            'about': self.clean_text(profile_data.get('about', '')),
            'experience': self.format_experience(profile_data.get('experience', [])),
            'education': self.format_education(profile_data.get('education', [])),
            'skills': self.format_skills(profile_data.get('skills', [])),
            'contact': profile_data.get('contact', {}),
            'certifications': self.format_certifications(profile_data.get('certifications', [])),
            'languages': self.format_languages(profile_data.get('languages', [])),
            'projects': self.format_projects(profile_data.get('projects', [])),
            'volunteer_experience': self.format_volunteer_experience(profile_data.get('volunteer_experience', [])),
            'honors_awards': self.format_honors_awards(profile_data.get('honors_awards', [])),
            'publications': self.format_publications(profile_data.get('publications', [])),
            'recommendations': self.format_recommendations(profile_data.get('recommendations', [])),
            'updated_date': datetime.now().strftime('%B %d, %Y')
        }
        
        # Render template with custom filters
        template = Template(self.template)
        
        # Add custom groupby filter for Jinja2
        def groupby_filter(value, attribute):
            """Group items by attribute"""
            from itertools import groupby
            keyfunc = lambda x: x.get(attribute, 'General')
            return [(k, list(g)) for k, g in groupby(sorted(value, key=keyfunc), keyfunc)]
        
        template.globals['groupby'] = groupby_filter
        
        return template.render(**template_vars)
    
    def save_markdown(self, markdown_content: str, output_path: str = 'resume.md'):
        """Save markdown content to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Resume saved to: {output_path}")
        except Exception as e:
            print(f"Error saving markdown: {e}")
            raise
    
    def load_profile_data(self, json_path: str = 'linkedin_data.json') -> Dict[str, Any]:
        """Load profile data from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Profile data file not found: {json_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            raise
    
    def create_github_pages_index(self, markdown_content: str):
        """Create index.md for GitHub Pages"""
        # GitHub Pages specific frontmatter
        github_pages_content = """---
layout: default
title: Resume
---

""" + markdown_content
        
        self.save_markdown(github_pages_content, 'index.md')
        print("GitHub Pages index.md created")

def main():
    """Main function"""
    # Parse command line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'linkedin_data.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'resume.md'
    
    try:
        generator = ResumeGenerator()
        
        # Load profile data
        profile_data = generator.load_profile_data(input_file)
        print(f"Loaded profile data for: {profile_data.get('name', 'Unknown')}")
        
        # Generate resume markdown
        markdown_content = generator.generate_resume(profile_data)
        
        # Save resume
        generator.save_markdown(markdown_content, output_file)
        
        # Create GitHub Pages index
        generator.create_github_pages_index(markdown_content)
        
        print("Resume generation completed successfully!")
        
        # Print comprehensive summary
        print(f"\nResume Summary:")
        print(f"- Name: {profile_data.get('name', 'N/A')}")
        print(f"- Experience entries: {len(profile_data.get('experience', []))}")
        print(f"- Education entries: {len(profile_data.get('education', []))}")
        print(f"- Skills listed: {len(profile_data.get('skills', []))}")
        print(f"- Certifications: {len(profile_data.get('certifications', []))}")
        print(f"- Languages: {len(profile_data.get('languages', []))}")
        print(f"- Projects: {len(profile_data.get('projects', []))}")
        print(f"- Volunteer experiences: {len(profile_data.get('volunteer_experience', []))}")
        print(f"- Honors & Awards: {len(profile_data.get('honors_awards', []))}")
        print(f"- Publications: {len(profile_data.get('publications', []))}")
        print(f"- Recommendations: {len(profile_data.get('recommendations', []))}")
        
    except Exception as e:
        print(f"Error generating resume: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()