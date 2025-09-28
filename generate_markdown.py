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
        Resume template using Jinja2 templating
        """
        return """# {{ name }}

{{ headline }}

{% if location %}📍 {{ location }}{% endif %}
{% if contact.linkedin_url %}🔗 [LinkedIn Profile]({{ contact.linkedin_url }}){% endif %}

---

## About

{{ about }}

---

## Experience

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

---

## Skills

{% for skill in skills %}
- {{ skill }}
{% endfor %}

---

## Contact

{% if contact.linkedin_url %}
- **LinkedIn**: [{{ contact.linkedin_url }}]({{ contact.linkedin_url }})
{% endif %}

---

*Last updated: {{ updated_date }}*
*Generated from LinkedIn profile data*
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
    
    def format_skills(self, skills: List[str]) -> List[str]:
        """Format and clean skills list"""
        formatted_skills = []
        
        for skill in skills:
            cleaned_skill = self.clean_text(skill)
            if cleaned_skill and cleaned_skill not in formatted_skills:
                formatted_skills.append(cleaned_skill)
        
        return formatted_skills[:20]  # Limit to top 20 skills
    
    def generate_resume(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate markdown resume from LinkedIn profile data
        """
        # Prepare template variables
        template_vars = {
            'name': self.clean_text(profile_data.get('name', 'Your Name')),
            'headline': self.clean_text(profile_data.get('headline', '')),
            'location': self.clean_text(profile_data.get('location', '')),
            'about': self.clean_text(profile_data.get('about', '')),
            'experience': self.format_experience(profile_data.get('experience', [])),
            'education': self.format_education(profile_data.get('education', [])),
            'skills': self.format_skills(profile_data.get('skills', [])),
            'contact': profile_data.get('contact', {}),
            'updated_date': datetime.now().strftime('%B %d, %Y')
        }
        
        # Render template
        template = Template(self.template)
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
        
        # Print summary
        print(f"\nResume Summary:")
        print(f"- Name: {profile_data.get('name', 'N/A')}")
        print(f"- Experience entries: {len(profile_data.get('experience', []))}")
        print(f"- Education entries: {len(profile_data.get('education', []))}")
        print(f"- Skills listed: {len(profile_data.get('skills', []))}")
        
    except Exception as e:
        print(f"Error generating resume: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()