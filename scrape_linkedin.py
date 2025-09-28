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
        Scrape comprehensive profile information from the current user's LinkedIn profile
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
            
            # About section (Professional Summary)
            try:
                about_section = page.locator('section:has(h2:has-text("About"))')
                if await about_section.count() > 0:
                    about_text = await about_section.locator('.display-flex.full-width').text_content()
                    profile_data['about'] = about_text.strip() if about_text else ""
                else:
                    profile_data['about'] = ""
            except:
                profile_data['about'] = ""
            
            # Core sections
            profile_data['experience'] = await self.scrape_experience(page)
            profile_data['education'] = await self.scrape_education(page)
            profile_data['skills'] = await self.scrape_skills(page)
            profile_data['contact'] = await self.scrape_contact_info(page)
            
            # Additional comprehensive sections
            profile_data['certifications'] = await self.scrape_certifications(page)
            profile_data['languages'] = await self.scrape_languages(page)
            profile_data['projects'] = await self.scrape_projects(page)
            profile_data['volunteer_experience'] = await self.scrape_volunteer_experience(page)
            profile_data['honors_awards'] = await self.scrape_honors_awards(page)
            profile_data['publications'] = await self.scrape_publications(page)
            profile_data['recommendations'] = await self.scrape_recommendations(page)
            
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
        """Scrape skills section with endorsements and categories"""
        skills = []
        try:
            skills_section = page.locator('section:has(h2:has-text("Skills"))')
            if await skills_section.count() > 0:
                # Try to click "Show all skills" if available
                try:
                    show_all_button = skills_section.locator('button:has-text("Show all")')
                    if await show_all_button.count() > 0:
                        await show_all_button.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
                
                skill_items = skills_section.locator('li.artdeco-list__item')
                count = await skill_items.count()
                
                for i in range(min(count, 30)):  # Limit to top 30 skills
                    item = skill_items.nth(i)
                    skill_data = {}
                    
                    # Skill name
                    try:
                        name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        skill_data['name'] = name.strip() if name else ""
                    except:
                        skill_data['name'] = ""
                    
                    # Endorsement count
                    try:
                        endorsements = await item.locator('.t-14.t-normal span[aria-hidden="true"]').text_content()
                        if endorsements and 'endorsement' in endorsements.lower():
                            # Extract number from endorsement text
                            import re
                            numbers = re.findall(r'\d+', endorsements)
                            skill_data['endorsements'] = int(numbers[0]) if numbers else 0
                        else:
                            skill_data['endorsements'] = 0
                    except:
                        skill_data['endorsements'] = 0
                    
                    # Category (if available)
                    try:
                        # Skills might be grouped under categories
                        category_header = item.locator('preceding-sibling::*').filter(has_text='span:has-text("Industry Knowledge")')
                        if await category_header.count() > 0:
                            skill_data['category'] = 'Industry Knowledge'
                        else:
                            skill_data['category'] = 'General'
                    except:
                        skill_data['category'] = 'General'
                    
                    if skill_data['name']:
                        skills.append(skill_data)
                
                # If we couldn't get detailed skills, fall back to simple text extraction
                if not skills:
                    simple_skills = skills_section.locator('.mr1.t-bold span[aria-hidden="true"]')
                    simple_count = await simple_skills.count()
                    
                    for i in range(min(simple_count, 30)):
                        skill = await simple_skills.nth(i).text_content()
                        if skill and skill.strip():
                            skills.append({
                                'name': skill.strip(),
                                'endorsements': 0,
                                'category': 'General'
                            })
                            
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
                
            # Try to click contact info button and get additional details
            try:
                contact_button = page.locator('button:has-text("Contact info")')
                if await contact_button.count() > 0:
                    await contact_button.click()
                    await page.wait_for_timeout(2000)
                    
                    # Extract email if available
                    email_elements = page.locator('a[href^="mailto:"]')
                    if await email_elements.count() > 0:
                        email_href = await email_elements.first.get_attribute('href')
                        if email_href:
                            contact['email'] = email_href.replace('mailto:', '')
                    
                    # Extract phone if available
                    phone_elements = page.locator('span:has-text("Phone")')
                    if await phone_elements.count() > 0:
                        phone_parent = phone_elements.first.locator('..')
                        phone_text = await phone_parent.text_content()
                        if phone_text and 'Phone' in phone_text:
                            contact['phone'] = phone_text.replace('Phone', '').strip()
                    
                    # Close modal
                    close_button = page.locator('button[aria-label="Dismiss"]')
                    if await close_button.count() > 0:
                        await close_button.click()
                        
            except Exception as e:
                print(f"Could not access contact info modal: {e}")
                
        except Exception as e:
            print(f"Error scraping contact info: {e}")
        
        return contact
    
    async def scrape_certifications(self, page: Page) -> list:
        """Scrape licenses and certifications section"""
        certifications = []
        try:
            cert_section = page.locator('section:has(h2:has-text("Licenses & certifications"))')
            if await cert_section.count() > 0:
                cert_items = cert_section.locator('li.artdeco-list__item')
                count = await cert_items.count()
                
                for i in range(count):
                    item = cert_items.nth(i)
                    cert_data = {}
                    
                    # Certification name
                    try:
                        name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        cert_data['name'] = name.strip() if name else ""
                    except:
                        cert_data['name'] = ""
                    
                    # Issuing organization
                    try:
                        org = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        cert_data['issuer'] = org.strip() if org else ""
                    except:
                        cert_data['issuer'] = ""
                    
                    # Issue date
                    try:
                        date = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        cert_data['date'] = date.strip() if date else ""
                    except:
                        cert_data['date'] = ""
                    
                    # Credential ID
                    try:
                        cred_id = await item.locator('.t-14.t-normal:has-text("Credential ID")').text_content()
                        if cred_id:
                            cert_data['credential_id'] = cred_id.replace('Credential ID', '').strip()
                    except:
                        cert_data['credential_id'] = ""
                    
                    if cert_data['name'] or cert_data['issuer']:
                        certifications.append(cert_data)
                        
        except Exception as e:
            print(f"Error scraping certifications: {e}")
        
        return certifications
    
    async def scrape_languages(self, page: Page) -> list:
        """Scrape languages section"""
        languages = []
        try:
            lang_section = page.locator('section:has(h2:has-text("Languages"))')
            if await lang_section.count() > 0:
                lang_items = lang_section.locator('li.artdeco-list__item')
                count = await lang_items.count()
                
                for i in range(count):
                    item = lang_items.nth(i)
                    lang_data = {}
                    
                    # Language name
                    try:
                        name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        lang_data['language'] = name.strip() if name else ""
                    except:
                        lang_data['language'] = ""
                    
                    # Proficiency level
                    try:
                        level = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        lang_data['proficiency'] = level.strip() if level else ""
                    except:
                        lang_data['proficiency'] = ""
                    
                    if lang_data['language']:
                        languages.append(lang_data)
                        
        except Exception as e:
            print(f"Error scraping languages: {e}")
        
        return languages
    
    async def scrape_projects(self, page: Page) -> list:
        """Scrape projects section"""
        projects = []
        try:
            proj_section = page.locator('section:has(h2:has-text("Projects"))')
            if await proj_section.count() > 0:
                proj_items = proj_section.locator('li.artdeco-list__item')
                count = await proj_items.count()
                
                for i in range(count):
                    item = proj_items.nth(i)
                    proj_data = {}
                    
                    # Project name
                    try:
                        name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        proj_data['name'] = name.strip() if name else ""
                    except:
                        proj_data['name'] = ""
                    
                    # Associated with
                    try:
                        associated = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        proj_data['associated_with'] = associated.strip() if associated else ""
                    except:
                        proj_data['associated_with'] = ""
                    
                    # Date range
                    try:
                        date_range = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        proj_data['date_range'] = date_range.strip() if date_range else ""
                    except:
                        proj_data['date_range'] = ""
                    
                    # Description
                    try:
                        desc = await item.locator('.t-14.t-normal.t-black span[aria-hidden="true"]').text_content()
                        proj_data['description'] = desc.strip() if desc else ""
                    except:
                        proj_data['description'] = ""
                    
                    # Project URL
                    try:
                        url_link = item.locator('a[href*="http"]')
                        if await url_link.count() > 0:
                            url = await url_link.get_attribute('href')
                            proj_data['url'] = url if url else ""
                    except:
                        proj_data['url'] = ""
                    
                    if proj_data['name']:
                        projects.append(proj_data)
                        
        except Exception as e:
            print(f"Error scraping projects: {e}")
        
        return projects
    
    async def scrape_volunteer_experience(self, page: Page) -> list:
        """Scrape volunteer experience section"""
        volunteer = []
        try:
            vol_section = page.locator('section:has(h2:has-text("Volunteering"))')
            if await vol_section.count() > 0:
                vol_items = vol_section.locator('li.artdeco-list__item')
                count = await vol_items.count()
                
                for i in range(count):
                    item = vol_items.nth(i)
                    vol_data = {}
                    
                    # Role
                    try:
                        role = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        vol_data['role'] = role.strip() if role else ""
                    except:
                        vol_data['role'] = ""
                    
                    # Organization
                    try:
                        org = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        vol_data['organization'] = org.strip() if org else ""
                    except:
                        vol_data['organization'] = ""
                    
                    # Duration
                    try:
                        duration = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        vol_data['duration'] = duration.strip() if duration else ""
                    except:
                        vol_data['duration'] = ""
                    
                    # Description
                    try:
                        desc = await item.locator('.t-14.t-normal.t-black span[aria-hidden="true"]').text_content()
                        vol_data['description'] = desc.strip() if desc else ""
                    except:
                        vol_data['description'] = ""
                    
                    if vol_data['role'] or vol_data['organization']:
                        volunteer.append(vol_data)
                        
        except Exception as e:
            print(f"Error scraping volunteer experience: {e}")
        
        return volunteer
    
    async def scrape_honors_awards(self, page: Page) -> list:
        """Scrape honors and awards section"""
        honors = []
        try:
            honors_section = page.locator('section:has(h2:has-text("Honors & awards"))')
            if await honors_section.count() > 0:
                honor_items = honors_section.locator('li.artdeco-list__item')
                count = await honor_items.count()
                
                for i in range(count):
                    item = honor_items.nth(i)
                    honor_data = {}
                    
                    # Award name
                    try:
                        name = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        honor_data['name'] = name.strip() if name else ""
                    except:
                        honor_data['name'] = ""
                    
                    # Issuer
                    try:
                        issuer = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        honor_data['issuer'] = issuer.strip() if issuer else ""
                    except:
                        honor_data['issuer'] = ""
                    
                    # Date
                    try:
                        date = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        honor_data['date'] = date.strip() if date else ""
                    except:
                        honor_data['date'] = ""
                    
                    # Description
                    try:
                        desc = await item.locator('.t-14.t-normal.t-black span[aria-hidden="true"]').text_content()
                        honor_data['description'] = desc.strip() if desc else ""
                    except:
                        honor_data['description'] = ""
                    
                    if honor_data['name'] or honor_data['issuer']:
                        honors.append(honor_data)
                        
        except Exception as e:
            print(f"Error scraping honors and awards: {e}")
        
        return honors
    
    async def scrape_publications(self, page: Page) -> list:
        """Scrape publications section"""
        publications = []
        try:
            pub_section = page.locator('section:has(h2:has-text("Publications"))')
            if await pub_section.count() > 0:
                pub_items = pub_section.locator('li.artdeco-list__item')
                count = await pub_items.count()
                
                for i in range(count):
                    item = pub_items.nth(i)
                    pub_data = {}
                    
                    # Publication title
                    try:
                        title = await item.locator('.mr1.t-bold span[aria-hidden="true"]').first.text_content()
                        pub_data['title'] = title.strip() if title else ""
                    except:
                        pub_data['title'] = ""
                    
                    # Publisher
                    try:
                        publisher = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        pub_data['publisher'] = publisher.strip() if publisher else ""
                    except:
                        pub_data['publisher'] = ""
                    
                    # Date
                    try:
                        date = await item.locator('.t-14.t-normal.t-black--light span[aria-hidden="true"]').first.text_content()
                        pub_data['date'] = date.strip() if date else ""
                    except:
                        pub_data['date'] = ""
                    
                    # Description
                    try:
                        desc = await item.locator('.t-14.t-normal.t-black span[aria-hidden="true"]').text_content()
                        pub_data['description'] = desc.strip() if desc else ""
                    except:
                        pub_data['description'] = ""
                    
                    # URL if available
                    try:
                        url_link = item.locator('a[href*="http"]')
                        if await url_link.count() > 0:
                            url = await url_link.get_attribute('href')
                            pub_data['url'] = url if url else ""
                    except:
                        pub_data['url'] = ""
                    
                    if pub_data['title'] or pub_data['publisher']:
                        publications.append(pub_data)
                        
        except Exception as e:
            print(f"Error scraping publications: {e}")
        
        return publications
    
    async def scrape_recommendations(self, page: Page) -> list:
        """Scrape recommendations section"""
        recommendations = []
        try:
            rec_section = page.locator('section:has(h2:has-text("Recommendations"))')
            if await rec_section.count() > 0:
                rec_items = rec_section.locator('li.artdeco-list__item')
                count = min(await rec_items.count(), 5)  # Limit to 5 recommendations
                
                for i in range(count):
                    item = rec_items.nth(i)
                    rec_data = {}
                    
                    # Recommender name
                    try:
                        name = await item.locator('.t-16.t-black.t-bold span[aria-hidden="true"]').first.text_content()
                        rec_data['recommender'] = name.strip() if name else ""
                    except:
                        rec_data['recommender'] = ""
                    
                    # Recommender title/relationship
                    try:
                        title = await item.locator('.t-14.t-normal span[aria-hidden="true"]').first.text_content()
                        rec_data['recommender_title'] = title.strip() if title else ""
                    except:
                        rec_data['recommender_title'] = ""
                    
                    # Recommendation text
                    try:
                        text = await item.locator('.t-14.t-normal.t-black span[aria-hidden="true"]').text_content()
                        rec_data['text'] = text.strip() if text else ""
                    except:
                        rec_data['text'] = ""
                    
                    if rec_data['recommender'] and rec_data['text']:
                        recommendations.append(rec_data)
                        
        except Exception as e:
            print(f"Error scraping recommendations: {e}")
        
        return recommendations
    
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