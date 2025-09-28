#!/usr/bin/env python3
"""
Enhanced Skills Organizer for LinkedIn Resume Generator

This script helps organize and structure LinkedIn skills based on common categories
and can supplement the automated scraper with manual skill organization.
"""

import json
import re
from typing import Dict, List, Any
from datetime import datetime

class SkillsOrganizer:
    def __init__(self):
        # Define skill categories based on common IT/Tech classifications
        self.skill_categories = {
            "Programming Languages": [
                "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "TypeScript", 
                "PHP", "Ruby", "Scala", "Kotlin", "Swift", "Objective-C", "R", "MATLAB",
                "SQL", "NoSQL", "GraphQL", "HTML", "CSS", "SCSS", "Sass"
            ],
            "Cloud & DevOps": [
                "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Jenkins",
                "GitLab CI", "GitHub Actions", "Terraform", "Ansible", "Puppet", "Chef",
                "CircleCI", "Travis CI", "Helm", "Istio", "Prometheus", "Grafana",
                "EKS", "AKS", "GKE", "CloudFormation", "CDK"
            ],
            "Development Tools": [
                "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "VS Code", "IntelliJ",
                "Eclipse", "Vim", "Emacs", "Postman", "Insomnia", "Swagger", "OpenAPI"
            ],
            "Databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
                "DynamoDB", "Oracle", "SQL Server", "SQLite", "Neo4j", "InfluxDB",
                "MariaDB", "CouchDB", "Amazon RDS", "Azure SQL"
            ],
            "Frameworks & Libraries": [
                "React", "Vue.js", "Angular", "Node.js", "Express", "Django", "Flask",
                "Spring", "Spring Boot", "Laravel", "Symfony", ".NET", "ASP.NET",
                "jQuery", "Bootstrap", "Tailwind CSS", "Material UI", "Ant Design"
            ],
            "Atlassian Ecosystem": [
                "Atlassian", "Jira", "Confluence", "Bitbucket", "Bamboo", "Crowd",
                "Jira Service Management", "Jira Align", "Trello", "Statuspage",
                "Opsgenie", "Compass", "Atlassian Cloud", "Atlassian Server", "Atlassian DC"
            ],
            "ITSM & Methodologies": [
                "ITIL", "ITIL v4", "Agile", "Scrum", "Kanban", "DevOps", "CI/CD",
                "Test-Driven Development", "Behavior-Driven Development", "Microservices",
                "Service Management", "Incident Management", "Change Management",
                "Problem Management", "Release Management"
            ],
            "Operating Systems": [
                "Linux", "Ubuntu", "CentOS", "RedHat", "SUSE", "Debian", "Windows Server",
                "macOS", "Unix", "AIX", "Solaris", "Windows", "Windows 10", "Windows 11"
            ],
            "Networking & Security": [
                "TCP/IP", "DNS", "DHCP", "VPN", "Firewall", "Load Balancing", "SSL/TLS",
                "OAuth", "SAML", "Active Directory", "LDAP", "Cybersecurity", "Penetration Testing",
                "Vulnerability Assessment", "Network Security", "Information Security"
            ],
            "Monitoring & Analytics": [
                "Prometheus", "Grafana", "New Relic", "Datadog", "Splunk", "ELK Stack",
                "Elasticsearch", "Logstash", "Kibana", "Nagios", "Zabbix", "SolarWinds",
                "Application Performance Monitoring", "Infrastructure Monitoring"
            ],
            "Soft Skills": [
                "Leadership", "Team Management", "Project Management", "Technical Writing",
                "Problem Solving", "Communication", "Mentoring", "Training", "Consulting",
                "Customer Service", "Stakeholder Management", "Technical Consultation"
            ]
        }
    
    def extract_skills_from_headline(self, headline: str) -> List[Dict[str, Any]]:
        """Extract skills mentioned in the LinkedIn headline"""
        skills = []
        if not headline:
            return skills
        
        # First, handle hyphen-separated items (only when hyphen acts as divider)
        # Split on " - " (hyphen with spaces) to preserve hyphenated words like "Problem-Solving"
        parts = [p.strip() for p in headline.split(' - ')]
        
        # Common separators in headlines (hyphen handled separately above)
        separators = ["|", "•", "·", ",", "&", "and", "—", "–"]
        
        # Split headline parts by remaining separators
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend([p.strip() for p in part.split(sep)])
            parts = new_parts
        
        # Clean and extract potential skills
        for part in parts:
            part = part.strip()
            if len(part) > 1 and not any(word in part.lower() for word in ['engineer', 'consultant', 'expert', 'senior', 'junior']):
                # Check if it matches known skills
                category = self.categorize_skill(part)
                if category != "Other":
                    skills.append({
                        "name": part,
                        "endorsements": 0,
                        "category": category,
                        "source": "headline"
                    })
        
        return skills
    
    def categorize_skill(self, skill_name: str) -> str:
        """Categorize a skill based on predefined categories"""
        skill_lower = skill_name.lower()
        
        # First pass: exact matches
        for category, skills_list in self.skill_categories.items():
            if any(known_skill.lower() == skill_lower for known_skill in skills_list):
                return category
        
        # Second pass: substring matches, but only for skills longer than 2 characters
        # to avoid false positives like "R" matching "Docker"
        if len(skill_lower) > 2:
            for category, skills_list in self.skill_categories.items():
                if any(known_skill.lower() in skill_lower or 
                       (len(known_skill) > 2 and skill_lower in known_skill.lower()) 
                       for known_skill in skills_list):
                    return category
        
        return "Other"
    
    def enhance_skills_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the skills data with better categorization and additional skills"""
        enhanced_data = profile_data.copy()
        
        # Get existing skills
        existing_skills = enhanced_data.get('skills', [])
        enhanced_skills = []
        
        # Process existing skills with better categorization
        for skill in existing_skills:
            if isinstance(skill, str):
                skill_obj = {
                    "name": skill,
                    "endorsements": 0,
                    "category": self.categorize_skill(skill)
                }
            else:
                skill_obj = skill.copy()
                skill_obj['category'] = self.categorize_skill(skill.get('name', ''))
            
            enhanced_skills.append(skill_obj)
        
        # Extract skills from headline
        headline_skills = self.extract_skills_from_headline(
            enhanced_data.get('headline', '')
        )
        
        # Merge skills, avoiding duplicates
        existing_names = {skill['name'].lower() for skill in enhanced_skills}
        for skill in headline_skills:
            if skill['name'].lower() not in existing_names:
                enhanced_skills.append(skill)
        
        # No hardcoded skills - purely extract from LinkedIn and headline only
        
        # Sort skills by category and endorsements
        enhanced_skills.sort(key=lambda x: (x.get('category', 'Other'), -x.get('endorsements', 0)))
        
        enhanced_data['skills'] = enhanced_skills
        return enhanced_data
    
    def generate_skills_summary(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of skills by category"""
        summary = {}
        
        for skill in skills:
            category = skill.get('category', 'Other')
            if category not in summary:
                summary[category] = {
                    'count': 0,
                    'skills': [],
                    'total_endorsements': 0
                }
            
            summary[category]['count'] += 1
            summary[category]['skills'].append(skill['name'])
            summary[category]['total_endorsements'] += skill.get('endorsements', 0)
        
        return summary

def main():
    """Enhance the existing LinkedIn data with better skills organization"""
    try:
        # Load existing data
        with open('linkedin_data.json', 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        print("🔄 Enhancing skills organization...")
        
        # Enhance skills
        organizer = SkillsOrganizer()
        enhanced_data = organizer.enhance_skills_data(profile_data)
        
        # Generate skills summary
        skills_summary = organizer.generate_skills_summary(enhanced_data['skills'])
        
        # Save enhanced data
        with open('linkedin_data_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        # Replace original data
        with open('linkedin_data.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Skills enhancement completed!")
        print(f"\n📊 Skills Summary:")
        print(f"Total skills: {len(enhanced_data['skills'])}")
        
        for category, info in skills_summary.items():
            print(f"\n📂 {category} ({info['count']} skills):")
            for skill in info['skills'][:5]:  # Show first 5 skills
                print(f"  • {skill}")
            if len(info['skills']) > 5:
                print(f"  ... and {len(info['skills']) - 5} more")
        
        # Regenerate the resume
        print("\n🔄 Regenerating resume with enhanced skills...")
        import subprocess
        result = subprocess.run(['python', 'generate_markdown.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Resume regenerated successfully!")
        else:
            print(f"❌ Error regenerating resume: {result.stderr}")
        
    except FileNotFoundError:
        print("❌ linkedin_data.json not found. Please run the scraper first.")
    except Exception as e:
        print(f"❌ Error enhancing skills: {e}")

if __name__ == "__main__":
    main()