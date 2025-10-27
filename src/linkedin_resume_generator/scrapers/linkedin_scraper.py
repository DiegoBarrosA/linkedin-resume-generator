"""Main LinkedIn scraper coordinating all scraping components."""

import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from ..config.settings import Settings
from ..models.profile import ProfileData, ContactInfo, Experience, Education, Certification
from ..utils.exceptions import ScrapingError, NetworkError, TimeoutError
from ..utils.logging import get_logger
from .authentication import AuthenticationHandler
from .skill_extractor import SkillExtractor


logger = get_logger(__name__)


class LinkedInScraper:
    """Main LinkedIn scraper with modular components."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logger.bind(component="linkedin_scraper")
        
        # Initialize components
        self.auth_handler = AuthenticationHandler(settings.linkedin, settings)
        self.skill_extractor = SkillExtractor()
        
        # Browser management
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup_browser()
    
    async def scrape_profile(self, profile_url: Optional[str] = None) -> ProfileData:
        """
        Scrape LinkedIn profile data.
        
        Args:
            profile_url: Optional specific profile URL
            
        Returns:
            Complete profile data
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            self.logger.info("Starting LinkedIn profile scraping")
            
            if not self.page:
                await self._initialize_browser()
            
            # Authenticate
            await self.auth_handler.authenticate(self.page)
            
            # Navigate to profile
            await self._navigate_to_profile(profile_url)
            
            # Extract basic profile info
            basic_info = await self._extract_basic_info()
            
            # Extract contact info
            contact_info = await self._extract_contact_info()
            
            # Extract skills
            skills = await self.skill_extractor.extract_skills(self.page)
            
            # Extract experience
            experience = await self._extract_experience()
            
            # Extract education
            education = await self._extract_education()
            
            # Extract certifications
            certifications = await self._extract_certifications()
            
            # Create profile data
            profile_data = ProfileData(
                name=basic_info.get("name", ""),
                headline=basic_info.get("headline"),
                summary=basic_info.get("summary"),
                location=basic_info.get("location"),
                contact_info=contact_info,
                experience=experience,
                education=education,
                skills=skills,
                certifications=certifications,
                profile_url=self.page.url
            )
            
            self.logger.info(f"Successfully scraped profile: {profile_data.name}")
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Profile scraping failed: {e}")
            if isinstance(e, ScrapingError):
                raise
            raise ScrapingError(f"Unexpected scraping error: {e}")
    
    async def _initialize_browser(self) -> None:
        """Initialize browser with optimal settings."""
        try:
            playwright = await async_playwright().start()
            
            # Configure browser
            browser_options = {
                "headless": self.settings.scraping.headless,
                "slow_mo": self.settings.scraping.slow_mo,
                "args": [
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-dev-shm-usage"
                ]
            }
            
            if self.settings.is_production():
                # Additional production settings
                browser_options["args"].extend([
                    "--disable-gpu",
                    "--no-first-run",
                    "--no-default-browser-check"
                ])
            
            self.browser = await playwright.chromium.launch(**browser_options)
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US"
            )
            
            # Configure context
            await self.context.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9"
            })
            
            # Create page
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.settings.scraping.timeout * 1000)
            
            self.logger.debug("Browser initialized successfully")
            
        except Exception as e:
            raise ScrapingError(f"Failed to initialize browser: {e}")
    
    async def _cleanup_browser(self) -> None:
        """Cleanup browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
                
            self.logger.debug("Browser cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Browser cleanup error: {e}")
    
    async def _navigate_to_profile(self, profile_url: Optional[str] = None) -> None:
        """Navigate to LinkedIn profile."""
        try:
            if profile_url:
                url = profile_url
            else:
                # Navigate to own profile
                url = "https://www.linkedin.com/in/me/"
            
            await self.page.goto(url, wait_until="networkidle")
            
            # Wait for profile content to load
            await self.page.wait_for_selector(
                ".pv-text-details__left-panel, .profile-header", 
                timeout=self.settings.scraping.timeout * 1000
            )
            
            self.logger.debug(f"Navigated to profile: {url}")
            
        except Exception as e:
            raise ScrapingError(f"Failed to navigate to profile: {e}")
    
    async def _navigate_to_details_section(self, section: str) -> None:
        """Navigate to a specific detail section page.
        
        Args:
            section: Section name (experience, skills, education, certifications)
        """
        try:
            base_url = self.page.url.split('/in/')[0] if '/in/' in self.page.url else self.page.url
            profile_slug = self.page.url.split('/in/')[1].split('/')[0] if '/in/' in self.page.url else 'me'
            
            details_url = f"{base_url}/in/{profile_slug}/details/{section}/"
            
            self.logger.debug(f"Navigating to details page: {details_url}")
            await self.page.goto(details_url, wait_until="networkidle")
            
            # Wait for content to load
            await self.page.wait_for_timeout(2000)
            
            self.logger.debug(f"Successfully navigated to {section} details page")
            
        except Exception as e:
            self.logger.warning(f"Failed to navigate to {section} details page: {e}")
            # Return to main profile if navigation fails
            if '/details/' in self.page.url:
                await self._navigate_to_profile()
    
    async def _parse_date_range(self, date_text: str) -> tuple[Optional[str], Optional[str]]:
        """Parse date range text into start_date and end_date.
        
        Args:
            date_text: Raw date string like "Jan 2020 - Present" or "2020 - 2024"
            
        Returns:
            Tuple of (start_date, end_date) or (None, None) if parsing fails
        """
        try:
            if not date_text or not date_text.strip():
                return None, None
            
            date_text = date_text.strip()
            
            # Handle various date range formats
            if " - " in date_text or "–" in date_text or "—" in date_text:
                # Split on various dash types
                separator = " - " if " - " in date_text else ("–" if "–" in date_text else "—")
                parts = date_text.split(separator, 1)
                
                start_date = parts[0].strip()
                end_date = parts[1].strip() if len(parts) > 1 else None
                
                # Normalize "Present" or "Current" to None for current positions
                if end_date and end_date.lower() in ["present", "current", "now"]:
                    end_date = None
                
                return start_date, end_date
            else:
                # Single date (likely current position)
                return date_text, None
                
        except Exception as e:
            self.logger.debug(f"Error parsing date range '{date_text}': {e}")
            return None, None
    
    async def _expand_section(self) -> None:
        """Expand collapsible sections on the page."""
        try:
            # Look for "Show more" or "See more" buttons
            expand_buttons = await self.page.query_selector_all(
                'button[aria-label*="Show more"], button[aria-label*="See more"], '
                '.pvs-see-more-container button, .artdeco-button--secondary'
            )
            
            for button in expand_buttons:
                try:
                    await button.click()
                    await self.page.wait_for_timeout(1500)
                    self.logger.debug("Clicked expand button")
                except Exception as e:
                    self.logger.debug(f"Could not click expand button: {e}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error expanding section: {e}")
    
    async def _extract_basic_info(self) -> Dict[str, str]:
        """Extract basic profile information."""
        try:
            info = {}
            
            # Extract name
            name_selectors = [
                "h1.text-heading-xlarge",
                ".pv-text-details__left-panel h1",
                ".profile-header__name"
            ]
            
            for selector in name_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    info["name"] = (await element.text_content()).strip()
                    break
            
            # Extract headline
            headline_selectors = [
                ".text-body-medium.break-words",
                ".pv-text-details__left-panel .text-body-medium",
                ".profile-header__headline"
            ]
            
            for selector in headline_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    info["headline"] = (await element.text_content()).strip()
                    break
            
            # Extract location
            location_selectors = [
                ".text-body-small.inline.t-black--light.break-words",
                ".pv-text-details__left-panel .text-body-small",
                ".profile-header__location"
            ]
            
            for selector in location_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    location_text = (await element.text_content()).strip()
                    if location_text and "connections" not in location_text.lower():
                        info["location"] = location_text
                        break
            
            # Extract summary/about
            summary_element = await self.page.query_selector(
                ".pv-about__text, .about-section .about-section__text"
            )
            if summary_element:
                info["summary"] = (await summary_element.text_content()).strip()
            
            return info
            
        except Exception as e:
            self.logger.warning(f"Error extracting basic info: {e}")
            return {}
    
    async def _extract_contact_info(self) -> ContactInfo:
        """Extract contact information."""
        contact_info = ContactInfo()
        
        try:
            # Try to access contact info section
            contact_button = await self.page.query_selector(
                "a[href*='contact-info'], button[aria-label*='Contact']"
            )
            
            if contact_button:
                await contact_button.click()
                await self.page.wait_for_timeout(2000)
                
                # Extract email
                email_element = await self.page.query_selector(
                    "a[href^='mailto:'], .ci-email .pv-contact-info__contact-type"
                )
                if email_element:
                    email_text = await email_element.text_content()
                    if "@" in email_text:
                        contact_info.email = email_text.strip()
                
                # Close modal if opened
                close_button = await self.page.query_selector(
                    "button[aria-label*='Dismiss'], .artdeco-modal__dismiss"
                )
                if close_button:
                    await close_button.click()
            
            # Set LinkedIn URL
            contact_info.linkedin_url = self.page.url
            
        except Exception as e:
            self.logger.debug(f"Could not extract contact info: {e}")
        
        return contact_info
    
    async def _extract_experience(self) -> list[Experience]:
        """Extract work experience with proper company names and position details."""
        experiences = []
        
        try:
            # Navigate to experience details page for more complete data
            await self._navigate_to_details_section("experience")
            
            # Wait for the experience list to load
            await self.page.wait_for_selector(
                ".pvs-list, .pvs-list__paged-list-item",
                timeout=self.settings.scraping.timeout * 1000
            )
            
            self.logger.debug("Starting experience extraction from details page")
            
            # Try to expand "Show more" button if it exists
            await self._expand_section()
            
            # Get all experience items (both company containers and positions)
            experience_items = await self.page.query_selector_all(
                "li.pvs-list__paged-list-item, li.pvs-entity"
            )
            
            self.logger.debug(f"Found {len(experience_items)} experience items")
            
            # Process each experience item
            for item in experience_items:
                try:
                    title = ""
                    company = ""
                    duration = ""
                    location = ""
                    
                    # Extract title - try multiple selectors
                    title_selectors = [
                        ".mr1.hoverable-link-text.t-bold span[aria-hidden='true']",
                        "h3.t-bold span[aria-hidden='true']",
                        ".pvs-entity__summary-info h3 span",
                        "span[data-field='title']",
                        ".entity-lockup__title span[aria-hidden='true']"
                    ]
                    
                    for selector in title_selectors:
                        title_elem = await item.query_selector(selector)
                        if title_elem:
                            text = await title_elem.text_content()
                            if text:
                                title = text.strip()
                                break
                    
                    # Extract company - this is often in a link or span after the title
                    company_selectors = [
                        ".t-14.t-normal.t-black span[aria-hidden='true']",
                        ".pv-entity__secondary-title",
                        ".entity-lockup__subtitle a",
                        "span[data-field='company']",
                        ".pvs-entity__summary-info .t-14.t-normal span"
                    ]
                    
                    all_texts = []
                    for selector in company_selectors:
                        elements = await item.query_selector_all(selector)
                        for elem in elements:
                            text = await elem.text_content()
                            if text:
                                all_texts.append(text.strip())
                    
                    # Filter out employment types and dates from company candidates
                    self.logger.debug(f"Company candidate texts: {all_texts}")
                    for text in all_texts:
                        lower_text = text.lower()
                        # Skip employment type keywords
                        if lower_text in ["full-time", "part-time", "contract", "internship", "freelance", "self-employed"]:
                            self.logger.debug(f"Skipping employment type: {text}")
                            continue
                        # Skip if it looks like a date
                        if any(month in lower_text for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                            self.logger.debug(f"Skipping date: {text}")
                            continue
                        # Skip if it's too long (likely a description)
                        if len(text) > 100:
                            self.logger.debug(f"Skipping too long text: {text[:50]}...")
                            continue
                        # If we found something, use it
                        if text and not company:
                            company = text
                            self.logger.debug(f"Selected company: {company}")
                    
                    # Extract date range from caption wrapper
                    date_selectors = [
                        ".pvs-entity__caption-wrapper span[aria-hidden='true']",
                        ".t-14.t-normal.t-black--light span[aria-hidden='true']",
                        ".pv-entity__bullet-item-v2",
                        ".date-range span"
                    ]
                    
                    for selector in date_selectors:
                        elements = await item.query_selector_all(selector)
                        for elem in elements:
                            text = await elem.text_content()
                            if text:
                                text = text.strip()
                                # Look for date patterns
                                if any(indicator in text.lower() for indicator in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "present", "current", "-", "year"]):
                                    if len(text) < 50:  # Filter out descriptions
                                        duration = text
                                        break
                        if duration:
                            break
                    
                    # Parse dates
                    start_date, end_date = await self._parse_date_range(duration)
                    
                    # Extract location
                    location_selectors = [
                        ".t-14.t-normal.t-black--light",
                        ".pv-entity__location",
                        "span[data-field='location']"
                    ]
                    
                    for selector in location_selectors:
                        elements = await item.query_selector_all(selector)
                        for elem in elements:
                            text = await elem.text_content()
                            if text:
                                text = text.strip()
                                # Location usually has comma or common location indicators
                                if "," in text or any(location_word in text.lower() for location_word in ["remote", "hybrid", "on-site"]):
                                    location = text
                                    break
                        if location:
                            break
                    
                    # Extract description
                    description = ""
                    desc_selectors = [
                        ".pvs-list__outer-container",
                        ".pvs-entity__extra-details",
                        ".show-more-less-text"
                    ]
                    
                    for selector in desc_selectors:
                        desc_elem = await item.query_selector(selector)
                        if desc_elem:
                            text = await desc_elem.text_content()
                            if text and len(text) > 50 and text not in [title, company, duration, location]:
                                description = text.strip()
                                break
                    
                    # Only add if we have valid data
                    if title and company:
                        # Log extracted data for debugging
                        self.logger.debug(f"Extracted: {title} at {company} ({start_date} - {end_date})")
                        
                        experiences.append(Experience(
                            title=title.strip(),
                            company=company.strip(),
                            location=location.strip() if location else None,
                            start_date=start_date,
                            end_date=end_date,
                            duration=duration.strip() if duration else None,
                            description=description.strip() if description else None
                        ))
                
                except Exception as e:
                    self.logger.debug(f"Error extracting experience item: {e}")
                    continue
            
            self.logger.debug(f"Successfully extracted {len(experiences)} experience items")
            
        except Exception as e:
            self.logger.warning(f"Error extracting experience: {e}")
        
        return experiences
    
    async def _extract_education(self) -> list[Education]:
        """Extract education information."""
        education_items = []
        
        try:
            education_elements = await self.page.query_selector_all(
                ".pv-education-entity, .education-item, .pvs-entity"
            )
            
            for element in education_elements:
                try:
                    # Extract institution
                    institution_element = await element.query_selector(
                        ".pv-entity__school-name, .education-item__school-name, .mr1.hoverable-link-text.t-bold span"
                    )
                    institution = await institution_element.text_content() if institution_element else ""
                    
                    # Extract degree
                    degree_element = await element.query_selector(
                        ".pv-entity__degree-name, .education-item__degree, .t-14.t-normal span"
                    )
                    degree = await degree_element.text_content() if degree_element else ""
                    
                    # Extract field of study
                    field_element = await element.query_selector(
                        ".pv-entity__fos, .education-item__field-of-study"
                    )
                    field_of_study = await field_element.text_content() if field_element else ""
                    
                    if institution:
                        education_items.append(Education(
                            institution=institution.strip(),
                            degree=degree.strip() if degree else None,
                            field_of_study=field_of_study.strip() if field_of_study else None
                        ))
                
                except Exception as e:
                    self.logger.debug(f"Error extracting education item: {e}")
                    continue
            
            self.logger.debug(f"Extracted {len(education_items)} education items")
            
        except Exception as e:
            self.logger.warning(f"Error extracting education: {e}")
        
        return education_items
    
    async def _extract_certifications(self) -> list[Certification]:
        """Extract certifications."""
        certifications = []
        
        try:
            cert_elements = await self.page.query_selector_all(
                ".pv-accomplishments-block .pv-accomplishments-block__content li, .certifications-section .certification-item"
            )
            
            for element in cert_elements:
                try:
                    # Extract certification name and organization
                    text_content = await element.text_content()
                    if text_content and ":" in text_content:
                        parts = text_content.split(":", 1)
                        name = parts[0].strip()
                        organization = parts[1].strip() if len(parts) > 1 else ""
                        
                        if name:
                            certifications.append(Certification(
                                name=name,
                                issuing_organization=organization or "Unknown"
                            ))
                
                except Exception as e:
                    self.logger.debug(f"Error extracting certification item: {e}")
                    continue
            
            self.logger.debug(f"Extracted {len(certifications)} certifications")
            
        except Exception as e:
            self.logger.warning(f"Error extracting certifications: {e}")
        
        return certifications