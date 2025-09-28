#!/usr/bin/env python3
"""
LinkedIn Profile Scraper - PERSONAL USE ONLY

⚠️  LEGAL COMPLIANCE NOTICE ⚠️
This script is designed EXCLUSIVELY for scraping your OWN LinkedIn profile data.
LinkedIn's Terms of Service prohibit storing or redistributing scraped profile content.

IMPORTANT:
- Use ONLY with YOUR OWN LinkedIn account
- Generated data is for PERSONAL resume creation only
- Raw scraped data should NOT be stored long-term or redistributed
- Comply with LinkedIn's Terms of Service at all times

Environment Variables Required:
- LINKEDIN_EMAIL: Your LinkedIn account email
- LINKEDIN_PASSWORD: Your LinkedIn account password  
- LINKEDIN_TOTP_SECRET: Your TOTP secret for 2FA (optional)

Usage:
    python scrape_linkedin.py
"""

import os
import json
import time
import re
import asyncio
import tempfile
import shutil
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
            await page.fill('input[name="session_key"]', self.email or "")
            await page.fill('input[name="session_password"]', self.password or "")
            
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
        """
        Comprehensive skills scraper that tries multiple selectors and approaches
        to extract ALL skills from LinkedIn profile
        """
        skills = []
        all_skill_names = set()  # Track unique skills
        
        try:
            print("Searching for skills section...")
            
            # Multiple possible selectors for skills section
            skills_selectors = [
                'section:has(h2:has-text("Skills"))',
                'section[data-section="skills"]',
                'section:has([data-field="skill_name"])',
                'div:has(h2:text("Skills"))',
                '.skills-section'
            ]
            
            skills_section = None
            for selector in skills_selectors:
                potential_section = page.locator(selector)
                if await potential_section.count() > 0:
                    skills_section = potential_section.first
                    print(f"Found skills section with selector: {selector}")
                    break
            
            if not skills_section:
                print("No skills section found, trying alternative approach...")
                # Try to find skills anywhere on the page
                await self.extract_skills_from_page_content(page, skills, all_skill_names)
                return skills
            
            # Try to expand skills section
            await self.expand_skills_section(skills_section)
            
            # Multiple approaches to extract skills
            await self.extract_skills_method_1(skills_section, skills, all_skill_names)
            await self.extract_skills_method_2(skills_section, skills, all_skill_names)
            await self.extract_skills_method_3(skills_section, skills, all_skill_names)
            
            # If still no skills found, try broad text extraction
            if not skills:
                await self.extract_skills_from_page_content(page, skills, all_skill_names)
            
            # Auto-categorize skills
            self.auto_categorize_skills(skills)
            
            print(f"Successfully extracted {len(skills)} unique skills")
            
        except Exception as e:
            print(f"Error in comprehensive skills scraping: {e}")
        
        return skills
    
    async def expand_skills_section(self, skills_section):
        """Try to expand/show all skills"""
        try:
            expand_buttons = [
                'button:has-text("Show all")',
                'button:has-text("See all")',
                'button:has-text("View all")',
                'button:has-text("Show more")',
                'button[aria-label*="Show all"]',
                'button[aria-label*="See all"]'
            ]
            
            for button_selector in expand_buttons:
                button = skills_section.locator(button_selector)
                if await button.count() > 0:
                    await button.click()
                    await skills_section.page.wait_for_timeout(2000)
                    print("Expanded skills section")
                    break
        except Exception as e:
            print(f"Could not expand skills section: {e}")
    
    async def extract_skills_method_1(self, skills_section, skills, all_skill_names):
        """Method 1: Standard LinkedIn skills structure"""
        try:
            skill_items = skills_section.locator('li')
            count = await skill_items.count()
            
            for i in range(count):
                item = skill_items.nth(i)
                
                # Try multiple selectors for skill names
                name_selectors = [
                    '.mr1.t-bold span[aria-hidden="true"]',
                    'span[aria-hidden="true"]:first-child',
                    '.skill-name',
                    'h3',
                    '.t-16.t-bold',
                    'strong'
                ]
                
                skill_name = ""
                for selector in name_selectors:
                    try:
                        name_element = item.locator(selector).first
                        if await name_element.count() > 0:
                            skill_name = await name_element.text_content()
                            if skill_name and skill_name.strip():
                                skill_name = skill_name.strip()
                                break
                    except:
                        continue
                
                if skill_name and skill_name.lower() not in all_skill_names:
                    # Extract endorsements
                    endorsements = await self.extract_endorsements(item)
                    
                    skills.append({
                        'name': skill_name,
                        'endorsements': endorsements,
                        'category': 'General'
                    })
                    all_skill_names.add(skill_name.lower())
                    
        except Exception as e:
            print(f"Method 1 failed: {e}")
    
    async def extract_skills_method_2(self, skills_section, skills, all_skill_names):
        """Method 2: Alternative selectors"""
        try:
            # Look for any clickable elements that might be skills
            skill_elements = skills_section.locator('button, a, span').filter(has_text=re.compile(r'^[A-Za-z][A-Za-z0-9\s\.\+\#\-]{1,30}$'))
            count = await skill_elements.count()
            
            for i in range(min(count, 50)):  # Limit to prevent infinite loops
                element = skill_elements.nth(i)
                text = await element.text_content()
                
                if text and text.strip() and self.is_valid_skill_name(text.strip()):
                    skill_name = text.strip()
                    if skill_name.lower() not in all_skill_names:
                        skills.append({
                            'name': skill_name,
                            'endorsements': 0,
                            'category': 'General'
                        })
                        all_skill_names.add(skill_name.lower())
                        
        except Exception as e:
            print(f"Method 2 failed: {e}")
    
    async def extract_skills_method_3(self, skills_section, skills, all_skill_names):
        """Method 3: Text-based extraction"""
        try:
            # Get all text from skills section and parse it
            section_text = await skills_section.text_content()
            
            if section_text:
                # Split by common separators and extract potential skills
                potential_skills = re.findall(r'\b[A-Za-z][A-Za-z0-9\s\.\+\#\-]{1,30}\b', section_text)
                
                for skill in potential_skills:
                    skill = skill.strip()
                    if self.is_valid_skill_name(skill) and skill.lower() not in all_skill_names:
                        # Skip common words
                        if not any(word in skill.lower() for word in ['skills', 'endorsement', 'show', 'see', 'view', 'all', 'more']):
                            skills.append({
                                'name': skill,
                                'endorsements': 0,
                                'category': 'General'
                            })
                            all_skill_names.add(skill.lower())
                            
        except Exception as e:
            print(f"Method 3 failed: {e}")
    
    async def extract_skills_from_page_content(self, page, skills, all_skill_names):
        """Fallback: Extract skills from entire page content"""
        try:
            print("Trying to extract skills from page content...")
            
            # Get page content
            page_content = await page.content()
            
            # Look for common skill patterns in the HTML
            skill_patterns = [
                r'"skill[^"]*"[^>]*>([^<]+)',
                r'data-skill[^>]*>([^<]+)',
                r'aria-label[^>]*skill[^>]*>([^<]+)',
            ]
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    skill_name = re.sub(r'<[^>]+>', '', match).strip()
                    if self.is_valid_skill_name(skill_name) and skill_name.lower() not in all_skill_names:
                        skills.append({
                            'name': skill_name,
                            'endorsements': 0,
                            'category': 'General'
                        })
                        all_skill_names.add(skill_name.lower())
                        
        except Exception as e:
            print(f"Page content extraction failed: {e}")
    
    async def extract_endorsements(self, item):
        """Extract endorsement count from skill item"""
        try:
            endorsement_selectors = [
                '.t-14.t-normal span[aria-hidden="true"]',
                'span:contains("endorsement")',
                '.endorsement-count'
            ]
            
            for selector in endorsement_selectors:
                element = item.locator(selector)
                if await element.count() > 0:
                    text = await element.text_content()
                    if text and 'endorsement' in text.lower():
                        # Strip all non-digit characters to handle comma-separated numbers like "1,234"
                        digits_only = re.sub(r'\D+', '', text)
                        return int(digits_only) if digits_only else 0
            return 0
        except:
            return 0
    
    def is_valid_skill_name(self, name):
        """Check if a string looks like a valid skill name"""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        
        # Skip common non-skill words
        invalid_words = [
            'skills', 'endorsement', 'endorsements', 'show', 'see', 'view', 'all', 'more',
            'experience', 'years', 'year', 'month', 'months', 'day', 'days',
            'click', 'button', 'link', 'page', 'profile', 'linkedin'
        ]
        
        return not any(word in name.lower() for word in invalid_words)
    
    def auto_categorize_skills(self, skills):
        """Automatically categorize skills based on common patterns"""
        categories = {
            "Programming Languages": [
                'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'typescript', 
                'php', 'ruby', 'scala', 'kotlin', 'swift', 'r', 'sql', 'html', 'css'
            ],
            "Cloud & DevOps": [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 
                'ansible', 'ci/cd', 'devops', 'cloud'
            ],
            "Development Tools": [
                'git', 'github', 'gitlab', 'bitbucket', 'vscode', 'intellij', 'postman'
            ],
            "Databases": [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle'
            ],
            "Frameworks & Libraries": [
                'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'spring'
            ],
            "Atlassian": [
                'atlassian', 'jira', 'confluence', 'bamboo', 'bitbucket', 'trello'
            ],
            "Methodologies": [
                'agile', 'scrum', 'kanban', 'itil', 'lean', 'waterfall'
            ]
        }
        
        for skill in skills:
            skill_name_lower = skill['name'].lower()
            categorized = False
            
            for category, keywords in categories.items():
                if any(keyword in skill_name_lower or skill_name_lower in keyword for keyword in keywords):
                    skill['category'] = category
                    categorized = True
                    break
            
            if not categorized:
                skill['category'] = 'Other'
    
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
    """Main function to run the LinkedIn scraper"""
    print("🤖 LinkedIn Profile Scraper")
    print("=" * 50)
    
    # CRITICAL COMPLIANCE WARNING
    print("🚨 LINKEDIN TERMS OF SERVICE COMPLIANCE WARNING 🚨")
    print("=" * 60)
    print("LinkedIn actively pursues legal action against data scrapers.")
    print("This tool is ONLY for extracting YOUR OWN profile data.")
    print("LinkedIn ToS prohibits:")
    print("  • Storing scraped profile content")
    print("  • Redistributing LinkedIn data")
    print("  • Automated collection beyond personal use")
    print()
    print("This tool includes compliance safeguards:")
    print("  ✅ Raw data is processed and immediately deleted")
    print("  ✅ Only final resume output is retained") 
    print("  ✅ Built for personal use only")
    print("=" * 60)
    print()
    
    print("This tool extracts comprehensive profile data from LinkedIn")
    print("including skills, experience, education, certifications, and more.")
    print()
    
    # User confirmation with compliance acknowledgment
    ci_mode = os.getenv('LINKEDIN_CI_MODE', '').lower() == 'true'
    
    if ci_mode:
        print("🤖 CI Mode: Auto-confirming compliance for automated execution")
        print("✅ Operating under assumption this is the repository owner's own LinkedIn profile")
        confirm = 'y'
    else:
        confirm = input("Confirm this is YOUR OWN LinkedIn account and you understand the legal requirements (y/n): ").lower().strip()
        
    if confirm != 'y':
        print("❌ This tool can only be used with your own LinkedIn profile.")
        print("❌ You must acknowledge compliance requirements to proceed.")
        return None
    
    temp_file_path = None
    try:
        scraper = LinkedInScraper()
        profile_data = await scraper.run()
        
        if not profile_data:
            print("❌ No profile data extracted")
            return None
            
        # Create temporary file for processing (guaranteed cleanup)
        temp_fd, temp_file_path = tempfile.mkstemp(suffix='.json', prefix='linkedin_data_')
        
        try:
            # Write data to temporary file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            # Create the expected filename as symlink/copy for compatibility
            if os.path.exists('linkedin_data.json'):
                os.remove('linkedin_data.json')
            shutil.copy2(temp_file_path, 'linkedin_data.json')
            
            print("✅ Profile data extracted successfully")
            print(f"📋 Profile: {profile_data.get('name', 'Unknown')}")
            print("⚠️  Raw data will be processed and then removed for compliance")
            
            return profile_data
            
        finally:
            # Guaranteed cleanup of temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass  # Silently ignore if already removed
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return None
        
    finally:
        # Cleanup main linkedin_data.json file for compliance
        if os.path.exists('linkedin_data.json'):
            try:
                os.remove('linkedin_data.json')
                print("🗑️  Raw LinkedIn data cleaned up for compliance")
            except OSError:
                pass  # Silently ignore if already removed

if __name__ == "__main__":
    asyncio.run(main())