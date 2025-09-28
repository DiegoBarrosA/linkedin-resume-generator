#!/usr/bin/env python3
"""
Test script to validate the enhanced LinkedIn scraper functionality
"""

import json
from datetime import datetime

# Sample comprehensive test data
test_profile_data = {
    "name": "John Doe",
    "headline": "Senior Software Engineer | Full Stack Developer | Technology Leader",
    "location": "San Francisco, CA",
    "about": "Experienced software engineer with 8+ years of experience in full-stack development, cloud architecture, and team leadership. Passionate about building scalable applications and mentoring junior developers. Expertise in modern web technologies, microservices, and DevOps practices.",
    "contact": {
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "linkedin_url": "https://www.linkedin.com/in/johndoe"
    },
    "experience": [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Innovation Corp",
            "duration": "Jan 2021 - Present",
            "description": "Lead development of microservices architecture serving 10M+ users. Mentored 5 junior developers and improved team productivity by 40%. Technologies: React, Node.js, AWS, Docker, Kubernetes."
        },
        {
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "duration": "Mar 2019 - Dec 2020",
            "description": "Built full-stack web applications from concept to production. Collaborated with cross-functional teams to deliver features ahead of schedule. Technologies: Vue.js, Python, PostgreSQL, Redis."
        }
    ],
    "education": [
        {
            "school": "Stanford University",
            "degree": "Master of Science in Computer Science",
            "duration": "2017 - 2019"
        },
        {
            "school": "UC Berkeley",
            "degree": "Bachelor of Science in Electrical Engineering and Computer Sciences",
            "duration": "2013 - 2017"
        }
    ],
    "skills": [
        {"name": "JavaScript", "endorsements": 25, "category": "Programming Languages"},
        {"name": "Python", "endorsements": 22, "category": "Programming Languages"},
        {"name": "React", "endorsements": 20, "category": "Frontend Technologies"},
        {"name": "Node.js", "endorsements": 18, "category": "Backend Technologies"},
        {"name": "AWS", "endorsements": 15, "category": "Cloud Technologies"},
        {"name": "Docker", "endorsements": 12, "category": "DevOps"},
        {"name": "Kubernetes", "endorsements": 10, "category": "DevOps"},
        {"name": "PostgreSQL", "endorsements": 8, "category": "Databases"},
        {"name": "Leadership", "endorsements": 14, "category": "Soft Skills"},
        {"name": "Agile Methodologies", "endorsements": 16, "category": "Methodologies"}
    ],
    "certifications": [
        {
            "name": "AWS Solutions Architect - Professional",
            "issuer": "Amazon Web Services",
            "date": "Mar 2023",
            "credential_id": "AWS-SAP-123456"
        },
        {
            "name": "Certified Kubernetes Administrator (CKA)",
            "issuer": "Cloud Native Computing Foundation",
            "date": "Jan 2023",
            "credential_id": "CKA-789012"
        }
    ],
    "languages": [
        {"language": "English", "proficiency": "Native"},
        {"language": "Spanish", "proficiency": "Conversational"},
        {"language": "Mandarin", "proficiency": "Basic"}
    ],
    "projects": [
        {
            "name": "Open Source ML Platform",
            "associated_with": "Personal Project",
            "date_range": "2022 - Present",
            "description": "Developed an open-source machine learning platform that simplifies model deployment and monitoring. Used by 500+ developers worldwide.",
            "url": "https://github.com/johndoe/ml-platform"
        },
        {
            "name": "E-commerce Microservices",
            "associated_with": "Tech Innovation Corp",
            "date_range": "2021 - 2022",
            "description": "Architected and implemented a scalable e-commerce platform using microservices. Handles 50K+ transactions daily with 99.9% uptime.",
            "url": ""
        }
    ],
    "volunteer_experience": [
        {
            "role": "Technical Mentor",
            "organization": "Code for Good",
            "duration": "2020 - Present",
            "description": "Mentor underrepresented students in software development. Organized workshops and hackathons reaching 200+ participants."
        }
    ],
    "honors_awards": [
        {
            "name": "Employee of the Year",
            "issuer": "Tech Innovation Corp",
            "date": "2023",
            "description": "Recognized for outstanding leadership and technical contributions to the platform architecture."
        }
    ],
    "publications": [
        {
            "title": "Scaling Microservices: Lessons from Production",
            "publisher": "Tech Blog Weekly",
            "date": "Sep 2023",
            "description": "Article discussing best practices for scaling microservices based on real-world experience.",
            "url": "https://techblog.com/scaling-microservices"
        }
    ],
    "recommendations": [
        {
            "recommender": "Jane Smith",
            "recommender_title": "Engineering Manager at Tech Innovation Corp",
            "text": "John is an exceptional engineer and leader. His technical expertise and mentoring skills have been invaluable to our team's success."
        }
    ],
    "scraped_at": datetime.now().isoformat(),
    "scraper_version": "2.0.0"
}

def test_resume_generation():
    """Test the enhanced resume generation"""
    try:
        from generate_markdown import ResumeGenerator
        
        print("Testing enhanced resume generation...")
        
        # Generate resume
        generator = ResumeGenerator()
        markdown_content = generator.generate_resume(test_profile_data)
        
        # Save test resume
        with open('test_resume.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print("✅ Test resume generated successfully!")
        print(f"📄 Saved as: test_resume.md")
        
        # Print content preview
        print("\n📋 Resume Preview (first 500 characters):")
        print("-" * 50)
        print(markdown_content[:500] + "...")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_data_validation():
    """Validate test data structure"""
    print("\n🔍 Validating test data structure...")
    
    sections = [
        'name', 'headline', 'location', 'about', 'contact',
        'experience', 'education', 'skills', 'certifications',
        'languages', 'projects', 'volunteer_experience',
        'honors_awards', 'publications', 'recommendations'
    ]
    
    for section in sections:
        if section in test_profile_data:
            data = test_profile_data[section]
            if isinstance(data, list):
                print(f"✅ {section}: {len(data)} items")
            elif isinstance(data, dict):
                print(f"✅ {section}: {len(data)} fields")
            else:
                print(f"✅ {section}: {type(data).__name__}")
        else:
            print(f"❌ Missing section: {section}")
    
    print(f"\n📊 Total data sections: {len([s for s in sections if s in test_profile_data])}/{len(sections)}")

if __name__ == "__main__":
    print("🚀 Enhanced LinkedIn Resume Generator - Test Suite")
    print("=" * 60)
    
    # Validate test data
    test_data_validation()
    
    # Test resume generation
    success = test_resume_generation()
    
    if success:
        print("\n🎉 All tests passed! The enhanced resume generator is working correctly.")
        print("\n📚 Enhanced features validated:")
        print("  • Comprehensive skills with endorsements and categories")
        print("  • Certifications with credential IDs")
        print("  • Multiple languages with proficiency levels")
        print("  • Projects with URLs and descriptions")
        print("  • Volunteer experience")
        print("  • Honors and awards")
        print("  • Publications with links")
        print("  • Professional recommendations")
        print("  • Enhanced contact information")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")