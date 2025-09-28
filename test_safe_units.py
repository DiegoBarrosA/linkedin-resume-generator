#!/usr/bin/env python3
"""
Safe unit tests for LinkedIn Resume Generator

These tests verify code structure and imports without requiring live LinkedIn access.
Safe to run in CI/CD environments.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

class TestLinkedInResumeGenerator(unittest.TestCase):
    """Safe tests that don't require live LinkedIn access"""
    
    def test_imports_work(self):
        """Test that all modules can be imported without issues"""
        try:
            # Test imports without triggering live connections
            import enhance_skills
            import generate_markdown
            
            # Test that classes can be instantiated
            organizer = enhance_skills.SkillsOrganizer()
            generator = generate_markdown.ResumeGenerator()
            
            self.assertIsNotNone(organizer)
            self.assertIsNotNone(generator)
            
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_skill_categorization(self):
        """Test skill auto-categorization logic"""
        from enhance_skills import SkillsOrganizer
        
        organizer = SkillsOrganizer()
        
        # Test programming language categorization
        self.assertEqual(organizer.categorize_skill("Python"), "Programming Languages")
        self.assertEqual(organizer.categorize_skill("JavaScript"), "Programming Languages")
        
        # Test cloud categorization
        self.assertEqual(organizer.categorize_skill("Docker"), "Cloud & DevOps")
        self.assertEqual(organizer.categorize_skill("AWS"), "Cloud & DevOps")
        
        # Test Atlassian categorization
        self.assertEqual(organizer.categorize_skill("Jira"), "Atlassian Ecosystem")
        self.assertEqual(organizer.categorize_skill("Confluence"), "Atlassian Ecosystem")
    
    def test_headline_parsing(self):
        """Test LinkedIn headline parsing without live scraping"""
        from enhance_skills import SkillsOrganizer
        
        organizer = SkillsOrganizer()
        
        # Test that hyphens don't break skill names
        headline = "Senior Engineer | Python | Open-Source Advocate | Docker"
        skills = organizer.extract_skills_from_headline(headline)
        
        skill_names = [skill['name'] for skill in skills]
        
        # Verify hyphenated skills are preserved
        self.assertIn("Open-Source Advocate", skill_names)
        self.assertIn("Python", skill_names)
        self.assertIn("Docker", skill_names)
    
    def test_markdown_generation_structure(self):
        """Test markdown generation with mock data"""
        from generate_markdown import ResumeGenerator
        
        generator = ResumeGenerator()
        
        # Mock profile data
        test_data = {
            'name': 'Test User',
            'headline': 'Software Engineer',
            'location': 'Test City',
            'about': 'Test about section',
            'skills': [
                {'name': 'Python', 'endorsements': 5, 'category': 'Programming Languages'},
                {'name': 'Docker', 'endorsements': 3, 'category': 'Cloud & DevOps'}
            ],
            'experience': [],
            'education': [],
            'contact': {'linkedin_url': 'https://linkedin.com/in/test'},
            'certifications': [],
            'languages': [],
            'projects': [],
            'volunteer_experience': [],
            'honors_awards': [],
            'publications': [],
            'recommendations': []
        }
        
        # Generate resume
        markdown = generator.generate_resume(test_data)
        
        # Verify structure
        self.assertIn('Test User', markdown)
        self.assertIn('Software Engineer', markdown)
        self.assertIn('Python', markdown)
        self.assertIn('Docker', markdown)
        self.assertIn('Programming Languages', markdown)
    
    def test_live_scraping_gating(self):
        """Test that live scraping requires explicit opt-in"""
        from test_universal_scraper import comprehensive_scraping_demo
        import asyncio
        
        # Temporarily remove opt-in flag to test gating
        orig_value = os.environ.get('RUN_LIVE_LINKEDIN')
        if 'RUN_LIVE_LINKEDIN' in os.environ:
            del os.environ['RUN_LIVE_LINKEDIN']
        
        try:
            # Test that scraping is blocked without opt-in
            async def test_gating():
                result = await comprehensive_scraping_demo()
                self.assertFalse(result, "Scraping should be blocked without opt-in flag")
            
            asyncio.run(test_gating())
        finally:
            # Restore original environment state
            if orig_value is not None:
                os.environ['RUN_LIVE_LINKEDIN'] = orig_value
    
    def test_privacy_safeguards_exist(self):
        """Test that privacy safeguards are in place"""
        try:
            import privacy_safe_processor
            
            processor = privacy_safe_processor.PrivacySafeProcessor()
            self.assertIsNotNone(processor)
            
            # Test that compliance notice exists
            self.assertIn("LEGAL NOTICE", processor.compliance_notice)
            self.assertIn("Terms of Service", processor.compliance_notice)
            
        except ImportError:
            self.fail("Privacy safe processor not available")

if __name__ == '__main__':
    print("🧪 Running Safe Unit Tests")
    print("=" * 50)
    print("These tests verify functionality without live LinkedIn access.")
    print("Safe to run in CI/CD environments.\n")
    
    unittest.main(verbosity=2)