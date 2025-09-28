#!/usr/bin/env python3
"""
Universal LinkedIn Skills Extractor

This script demonstrates how the enhanced scraper works and can be used
by anyone to extract ALL their LinkedIn skills automatically.

No hardcoding required - just run and it will extract everything!
"""

import asyncio
import json
from scrape_linkedin import LinkedInScraper

async def test_comprehensive_scraping():
    """Test the comprehensive scraping without hardcoded values"""
    
    print("🚀 Testing Comprehensive LinkedIn Skills Extraction")
    print("=" * 60)
    print("This will extract ALL skills from your LinkedIn profile automatically!")
    print("No hardcoding needed - works for any LinkedIn profile.")
    print()
    
    try:
        scraper = LinkedInScraper()
        profile_data = await scraper.run()
        
        if profile_data:
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
        else:
            print("❌ Failed to scrape profile data")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_usage_instructions():
    """Show how anyone can use this system"""
    print("\n📚 HOW TO USE THIS FOR ANY LINKEDIN PROFILE:")
    print("=" * 50)
    print("1. Set up your environment variables:")
    print("   export LINKEDIN_EMAIL='your-email@example.com'")
    print("   export LINKEDIN_PASSWORD='your-password'")
    print("   export LINKEDIN_TOTP_SECRET='your-totp-secret'  # Optional")
    print()
    print("2. Run the scraper:")
    print("   python3 scrape_linkedin.py")
    print()
    print("3. Generate your resume:")
    print("   python3 generate_markdown.py")
    print()
    print("4. Or run this comprehensive test:")
    print("   python3 test_universal_scraper.py")
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
            asyncio.run(test_comprehensive_scraping())
        else:
            print("\n👍 No problem! You can run it anytime with:")
            print("python3 test_universal_scraper.py")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Run this script anytime to extract your LinkedIn skills.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have set your LinkedIn credentials in environment variables.")