#!/usr/bin/env python3
"""
LinkedIn Profile Scraper

This script logs into LinkedIn using email/password authentication with TOTP support
and scrapes profile information to generate a resume.

Environment Variables Required:
- LINKEDIN_EMAIL: LinkedIn account email
- LINKEDIN_PASSWORD: LinkedIn account password  
- LINKEDIN_TOTP_SECRET: TOTP secret for 2FA (optional)

Usage:
    python scrape_linkedin.py
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

import pyotp
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInScraper:
    def __init__(self):
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.totp_secret = os.getenv('LINKEDIN_TOTP_SECRET')
        
        if not self.email or not self.password:
            raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables are required")
        
        self.profile_data = {}
        
    async def authenticate(self, page: Page) -> bool:
        """
        Authenticate with LinkedIn using email/password and optional TOTP
        """
        try:
            print("Navigating to LinkedIn login page...")
            await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            
            # Fill in email and password
            await page.fill('input[name="session_key"]', self.email)
            await page.fill('input[name="session_password"]', self.password)
            
            # Click login button
            await page.click('button[type="submit"]')
            
            # Wait a moment for page to load
            await page.wait_for_timeout(3000)
            
            # Check if we need TOTP
            if await page.is_visible('input[name="pin"]') or await page.is_visible('input[id="input__phone_verification_pin"]'):
                if not self.totp_secret:
                    print("TOTP required but LINKEDIN_TOTP_SECRET not provided")
                    return False
                    
                print("TOTP verification required...")
                totp = pyotp.TOTP(self.totp_secret)
                verification_code = totp.now()
                
                # Try different possible selectors for TOTP input
                totp_selectors = [
                    'input[name="pin"]',
                    'input[id="input__phone_verification_pin"]',
                    'input[placeholder*="verification"]',
                    'input[aria-label*="verification"]'
                ]
                
                for selector in totp_selectors:
                    if await page.is_visible(selector):
                        await page.fill(selector, verification_code)
                        break
                
                # Submit TOTP
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Verify")'
                ]
                
                for selector in submit_selectors:
                    if await page.is_visible(selector):
                        await page.click(selector)
                        break
                
                await page.wait_for_timeout(3000)
            
            # Check if login was successful
            await page.wait_for_timeout(2000)
            
            # If we're redirected to the feed or profile, login was successful
            current_url = page.url
            if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
                print("Successfully logged in to LinkedIn")
                return True
            elif "linkedin.com/challenge" in current_url:
                print("LinkedIn security challenge detected - manual intervention may be required")
                return False
            else:
                print(f"Login may have failed - current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    async def scrape_profile(self, page: Page) -> Dict[str, Any]:
        """
        Scrape profile information from the current user's LinkedIn profile
        """
        try:
            print("Navigating to profile...")
            # Go to the user's own profile
            await page.goto("https://www.linkedin.com/in/me/", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            profile_data = {}
            
            # Basic Info
            try:
                name = await page.text_content('h1')
                profile_data['name'] = name.strip() if name else ""
            except:
                profile_data['name'] = ""
            
            try:
                headline = await page.text_content('.text-body-medium.break-words')
                profile_data['headline'] = headline.strip() if headline else ""
            except:
                profile_data['headline'] = ""
            
            try:
                location = await page.text_content('.text-body-small.inline.t-black--light.break-words')
                profile_data['location'] = location.strip() if location else ""
            except:
                profile_data['location'] = ""
            
            # About section
            try:
                about_section = page.locator('section:has(h2:has-text("About"))')
                if await about_section.count() > 0:
                    about_text = await about_section.locator('.display-flex.full-width').text_content()
                    profile_data['about'] = about_text.strip() if about_text else ""
                else:
                    profile_data['about'] = ""
            except:
                profile_data['about'] = ""
            
            # Experience
            profile_data['experience'] = await self.scrape_experience(page)
            
            # Education
            profile_data['education'] = await self.scrape_education(page)
            
            # Skills
            profile_data['skills'] = await self.scrape_skills(page)
            
            # Contact info (if available)
            profile_data['contact'] = await self.scrape_contact_info(page)
            
            print("Profile scraping completed successfully")
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile: {e}")
            return {}
    
    async def scrape_experience(self, page: Page) -> list:
        """Scrape work experience section"""
        experience = []
        try:
            exp_section = page.locator('section:has(h2:has-text("Experience"))')
            if await exp_section.count() > 0:
                # Get all experience items
                exp_items = exp_section.locator('li.artdeco-list__item')
                count = await exp_items.count()
                
                for i in range(count):
                    item = exp_items.nth(i)
                    exp_data = {}
                    
                    # Job title
                    try:
                        title = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        exp_data['title'] = title.strip() if title else ""
                    except:
                        exp_data['title'] = ""
                    
                    # Company name
                    try:
                        company = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        exp_data['company'] = company.strip() if company else ""
                    except:
                        exp_data['company'] = ""
                    
                    # Duration
                    try:
                        duration = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        exp_data['duration'] = duration.strip() if duration else ""
                    except:
                        exp_data['duration'] = ""
                    
                    # Description
                    try:
                        desc = await item.locator('.t-14.t-normal.t-black span[aria-hidden="true"]').text_content()
                        exp_data['description'] = desc.strip() if desc else ""
                    except:
                        exp_data['description'] = ""
                    
                    if exp_data['title'] or exp_data['company']:
                        experience.append(exp_data)
        except Exception as e:
            print(f"Error scraping experience: {e}")
        
        return experience
    
    async def scrape_education(self, page: Page) -> list:
        """Scrape education section"""
        education = []
        try:
            edu_section = page.locator('section:has(h2:has-text("Education"))')
            if await edu_section.count() > 0:
                edu_items = edu_section.locator('li.artdeco-list__item')
                count = await edu_items.count()
                
                for i in range(count):
                    item = edu_items.nth(i)
                    edu_data = {}
                    
                    # School name
                    try:
                        school = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        edu_data['school'] = school.strip() if school else ""
                    except:
                        edu_data['school'] = ""
                    
                    # Degree
                    try:
                        degree = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        edu_data['degree'] = degree.strip() if degree else ""
                    except:
                        edu_data['degree'] = ""
                    
                    # Duration
                    try:
                        duration = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        edu_data['duration'] = duration.strip() if duration else ""
                    except:
                        edu_data['duration'] = ""
                    
                    if edu_data['school'] or edu_data['degree']:
                        education.append(edu_data)
        except Exception as e:
            print(f"Error scraping education: {e}")
        
        return education
    
    async def scrape_skills(self, page: Page) -> list:
        """Scrape skills section"""
        skills = []
        try:
            skills_section = page.locator('section:has(h2:has-text("Skills"))')
            if await skills_section.count() > 0:
                skill_items = skills_section.locator('.mr1.t-bold span[aria-hidden="true"]')
                count = await skill_items.count()
                
                for i in range(min(count, 20)):  # Limit to top 20 skills
                    skill = await skill_items.nth(i).text_content()
                    if skill and skill.strip():
                        skills.append(skill.strip())
        except Exception as e:
            print(f"Error scraping skills: {e}")
        
        return skills
    
    async def scrape_contact_info(self, page: Page) -> dict:
        """Scrape contact information"""
        contact = {}
        try:
            # Try to get profile URL
            current_url = page.url
            if "/in/" in current_url:
                contact['linkedin_url'] = current_url
        except Exception as e:
            print(f"Error scraping contact info: {e}")
        
        return contact
    
    async def run(self) -> Dict[str, Any]:
        """
        Main method to run the scraping process
        """
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--disable-extensions'
                ]
            )
            
            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                # Authenticate
                if not await self.authenticate(page):
                    raise Exception("Authentication failed")
                
                # Scrape profile
                profile_data = await self.scrape_profile(page)
                
                # Add metadata
                profile_data['scraped_at'] = datetime.now().isoformat()
                profile_data['scraper_version'] = "1.0.0"
                
                return profile_data
                
            finally:
                await browser.close()

async def main():
    """Main function"""
    try:
        scraper = LinkedInScraper()
        profile_data = await scraper.run()
        
        # Save raw data
        with open('linkedin_data.json', 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        print("LinkedIn data saved to linkedin_data.json")
        print(f"Scraped profile for: {profile_data.get('name', 'Unknown')}")
        
        return profile_data
        
    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())