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
        """Extract work experience."""
        experiences = []
        
        try:
            # Navigate to experience section or find it on page
            experience_elements = await self.page.query_selector_all(
                ".pv-entity__position-group-pager, .experience-item, .pvs-entity"
            )
            
            for element in experience_elements:
                try:
                    # Extract title
                    title_element = await element.query_selector(
                        ".pv-entity__summary-info h3, .experience-item__title, .mr1.t-bold span"
                    )
                    title = await title_element.text_content() if title_element else ""
                    
                    # Extract company
                    company_element = await element.query_selector(
                        ".pv-entity__secondary-title, .experience-item__subtitle, .t-14.t-normal span"
                    )
                    company = await company_element.text_content() if company_element else ""
                    
                    # Extract duration/dates
                    duration_element = await element.query_selector(
                        ".pv-entity__bullet-item-v2, .experience-item__duration, .pvs-entity__caption-wrapper"
                    )
                    duration = await duration_element.text_content() if duration_element else ""
                    
                    # Extract description
                    desc_element = await element.query_selector(
                        ".pv-entity__description, .experience-item__description"
                    )
                    description = await desc_element.text_content() if desc_element else ""
                    
                    if title and company:
                        experiences.append(Experience(
                            title=title.strip(),
                            company=company.strip(), 
                            duration=duration.strip(),
                            description=description.strip() if description else None
                        ))
                
                except Exception as e:
                    self.logger.debug(f"Error extracting experience item: {e}")
                    continue
            
            self.logger.debug(f"Extracted {len(experiences)} experience items")
            
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