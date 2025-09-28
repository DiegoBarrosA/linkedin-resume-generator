#!/usr/bin/env python3
"""
Universal LinkedIn Skills Extractor

This script demonstrates how the enhanced scraper works and can be used
by anyone to extract ALL their LinkedIn skills automatically.

No hardcoding required - just run and it will extract everything!
"""

import asyncio
import json
import os

# Optional pytest import for test environments
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    
    # Mock pytest for environments without it
    import inspect
    
    class MockPytestMark:
        def skipif(self, condition, reason=""):
            def decorator(func):
                if condition:
                    # Check if the function is a coroutine (async function)
                    if inspect.iscoroutinefunction(func):
                        async def async_wrapper(*args, **kwargs):
                            print(f"⏭️  Skipped: {reason}")
                            return None
                        return async_wrapper
                    else:
                        def sync_wrapper(*args, **kwargs):
                            print(f"⏭️  Skipped: {reason}")
                            return None
                        return sync_wrapper
                return func
            return decorator
    
    class MockPytest:
        mark = MockPytestMark()
        
        @staticmethod
        def skip(reason):
            print(f"⏭️  Skipped: {reason}")
            return None
    
    pytest = MockPytest()

async def comprehensive_scraping_demo():
    """Demo the comprehensive scraping - requires explicit opt-in to run"""
    
    # Check for explicit opt-in environment variable
    if not os.getenv('RUN_LIVE_LINKEDIN'):
        print("⚠️  Live LinkedIn scraping requires opt-in")
        print("Set environment variable: RUN_LIVE_LINKEDIN=true")
        print("This prevents accidental execution in CI/test environments.")
        return False
    
    print("🚀 Testing Comprehensive LinkedIn Skills Extraction")
    print("=" * 60)
    print("This will extract ALL skills from your LinkedIn profile automatically!")
    print("No hardcoding needed - works for any LinkedIn profile.")
    print()
    
    try:
        from scrape_linkedin import LinkedInScraper
        scraper = LinkedInScraper()
        profile_data = await scraper.run()
        
        if not profile_data:
            raise AssertionError("Failed to scrape profile data - scraper returned empty/null data")
            
        print("✅ Profile scraped successfully!")
        print(f"📊 Extracted Data Summary:")
        print(f"  • Name: {profile_data.get('name', 'N/A')}")
        print(f"  • Skills found: {len(profile_data.get('skills', []))}")
        print(f"  • Experience entries: {len(profile_data.get('experience', []))}")
        print(f"  • Education entries: {len(profile_data.get('education', []))}")
        print(f"  • Certifications: {len(profile_data.get('certifications', []))}")
        print(f"  • Projects: {len(profile_data.get('projects', []))}")
        
        # Show skills breakdown
        skills = profile_data.get('skills', [])
        if skills:
            print("\n🎯 Skills Breakdown by Category:")
            categories = {}
            for skill in skills:
                cat = skill.get('category', 'Other')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(skill['name'])
            
            for category, skill_list in categories.items():
                print(f"\n📂 {category} ({len(skill_list)} skills):")
                for skill in skill_list[:8]:  # Show first 8
                    print(f"  • {skill}")
                if len(skill_list) > 8:
                    print(f"  ... and {len(skill_list) - 8} more")
        
        print("\n🔄 Generating resume with extracted data...")
        
        # Generate resume
        from generate_markdown import ResumeGenerator
        generator = ResumeGenerator()
        markdown_content = generator.generate_resume(profile_data)
        
        # Save files
        generator.save_markdown(markdown_content, 'resume.md')
        generator.create_github_pages_index(markdown_content)
        
        print("✅ Resume generated successfully!")
        print(f"📄 Files created: resume.md, index.md")
        
        return True
            
    except Exception as e:
        print(f"❌ Error during LinkedIn scraping: {e}")
        # Re-raise the exception so the test fails properly
        raise AssertionError(f"LinkedIn scraping failed with error: {str(e)}") from e

@pytest.mark.skipif(
    not os.getenv('RUN_LIVE_LINKEDIN'), 
    reason="Live LinkedIn scraping requires RUN_LIVE_LINKEDIN=true environment variable"
)
async def test_linkedin_scraping():
    """Pytest test for LinkedIn scraping - skipped by default for CI safety"""
    # comprehensive_scraping_demo now raises exceptions on failure instead of returning False
    # If it completes without raising an exception, the test passes
    result = await comprehensive_scraping_demo()
    # result should be True if successful, but the main validation is that no exception was raised
    assert result is True, "LinkedIn scraping should complete successfully and return True"

def show_usage_instructions():
    """Show how anyone can use this system"""
    print("\n📚 HOW TO USE THIS FOR ANY LINKEDIN PROFILE:")
    print("=" * 50)
    print("1. Set up your environment variables:")
    print("   export LINKEDIN_EMAIL='your-email@example.com'")
    print("   export LINKEDIN_PASSWORD='your-password'")
    print("   export LINKEDIN_TOTP_SECRET='your-totp-secret'  # Optional")
    print()
    print("2. For live scraping, enable opt-in flag:")
    print("   export RUN_LIVE_LINKEDIN=true")
    print()
    print("3. Run the scraper:")
    print("   python3 scrape_linkedin.py")
    print()
    print("4. Generate your resume:")
    print("   python3 generate_markdown.py")
    print()
    print("5. Or run this comprehensive test:")
    print("   RUN_LIVE_LINKEDIN=true python3 test_universal_scraper.py")
    print()
    print("✨ NO HARDCODING REQUIRED!")
    print("The system automatically:")
    print("  • Extracts ALL your skills from LinkedIn")
    print("  • Categorizes them intelligently")
    print("  • Generates a professional resume")
    print("  • Works for any LinkedIn profile")
    print("  • Handles different LinkedIn layouts")
    print("  • Adapts to profile structure changes")

if __name__ == "__main__":
    print("🌟 Universal LinkedIn Resume Generator")
    print("Works for ANYONE without modifications!")
    print()
    
    # Show instructions first
    show_usage_instructions()
    
    print("\n" + "=" * 60)
    
    # Ask user if they want to test
    try:
        response = input("\n🤔 Do you want to test the scraper now? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            # Set opt-in flag for this session
            os.environ['RUN_LIVE_LINKEDIN'] = 'true'
            asyncio.run(comprehensive_scraping_demo())
        else:
            print("\n👍 No problem! You can run it anytime with:")
            print("RUN_LIVE_LINKEDIN=true python3 test_universal_scraper.py")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Run this script anytime to extract your LinkedIn skills.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have set your LinkedIn credentials in environment variables.")