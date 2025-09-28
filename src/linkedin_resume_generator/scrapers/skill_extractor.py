"""Skill extraction logic for LinkedIn profiles."""

import re
from typing import List, Set, Dict, Any
from playwright.async_api import Page, ElementHandle

from ..models.profile import Skill, SkillCategory
from ..utils.exceptions import ScrapingError
from ..utils.logging import get_logger


logger = get_logger(__name__)


class SkillExtractor:
    """Extracts and categorizes skills from LinkedIn profiles."""
    
    def __init__(self):
        self.logger = logger.bind(component="skill_extractor")
        self._skill_categories = self._initialize_skill_categories()
    
    def _initialize_skill_categories(self) -> Dict[str, SkillCategory]:
        """Initialize skill categorization mappings."""
        return {
            # Programming Languages
            "python": SkillCategory.PROGRAMMING,
            "javascript": SkillCategory.PROGRAMMING,
            "java": SkillCategory.PROGRAMMING,
            "c++": SkillCategory.PROGRAMMING,
            "c#": SkillCategory.PROGRAMMING,
            "go": SkillCategory.PROGRAMMING,
            "rust": SkillCategory.PROGRAMMING,
            "typescript": SkillCategory.PROGRAMMING,
            "php": SkillCategory.PROGRAMMING,
            "ruby": SkillCategory.PROGRAMMING,
            "kotlin": SkillCategory.PROGRAMMING,
            "swift": SkillCategory.PROGRAMMING,
            "scala": SkillCategory.PROGRAMMING,
            
            # Frameworks & Libraries
            "react": SkillCategory.FRAMEWORKS,
            "angular": SkillCategory.FRAMEWORKS,
            "vue.js": SkillCategory.FRAMEWORKS,
            "django": SkillCategory.FRAMEWORKS,
            "flask": SkillCategory.FRAMEWORKS,
            "spring": SkillCategory.FRAMEWORKS,
            "express.js": SkillCategory.FRAMEWORKS,
            "tensorflow": SkillCategory.FRAMEWORKS,
            "pytorch": SkillCategory.FRAMEWORKS,
            "pandas": SkillCategory.FRAMEWORKS,
            "numpy": SkillCategory.FRAMEWORKS,
            
            # Databases
            "postgresql": SkillCategory.DATABASES,
            "mysql": SkillCategory.DATABASES,
            "mongodb": SkillCategory.DATABASES,
            "redis": SkillCategory.DATABASES,
            "elasticsearch": SkillCategory.DATABASES,
            "cassandra": SkillCategory.DATABASES,
            "dynamodb": SkillCategory.DATABASES,
            "sqlite": SkillCategory.DATABASES,
            
            # Cloud Platforms
            "aws": SkillCategory.CLOUD,
            "azure": SkillCategory.CLOUD,
            "gcp": SkillCategory.CLOUD,
            "google cloud": SkillCategory.CLOUD,
            "kubernetes": SkillCategory.CLOUD,
            "docker": SkillCategory.CLOUD,
            "terraform": SkillCategory.CLOUD,
            
            # Tools & Platforms
            "git": SkillCategory.TOOLS,
            "jenkins": SkillCategory.TOOLS,
            "jira": SkillCategory.TOOLS,
            "confluence": SkillCategory.TOOLS,
            "figma": SkillCategory.TOOLS,
            "sketch": SkillCategory.TOOLS,
            "photoshop": SkillCategory.TOOLS,
            
            # Professional Skills
            "project management": SkillCategory.PROFESSIONAL,
            "agile": SkillCategory.PROFESSIONAL,
            "scrum": SkillCategory.PROFESSIONAL,
            "leadership": SkillCategory.PROFESSIONAL,
            "team management": SkillCategory.PROFESSIONAL,
            "communication": SkillCategory.PROFESSIONAL,
            "problem solving": SkillCategory.PROFESSIONAL,
        }
    
    async def extract_skills(self, page: Page) -> List[Skill]:
        """
        Extract skills using multiple methods for comprehensive coverage.
        
        Args:
            page: Playwright page instance
            
        Returns:
            List of extracted skills
        """
        try:
            self.logger.info("Starting skill extraction")
            
            skills = []
            extracted_names = set()
            
            # Navigate to profile if not already there
            await self._ensure_profile_page(page)
            
            # Method 1: Extract from skills section
            skills_section_skills = await self._extract_from_skills_section(page)
            for skill in skills_section_skills:
                if skill.name.lower() not in extracted_names:
                    skills.append(skill)
                    extracted_names.add(skill.name.lower())
            
            # Method 2: Extract from experience descriptions
            experience_skills = await self._extract_from_experience(page)
            for skill in experience_skills:
                if skill.name.lower() not in extracted_names:
                    skills.append(skill)
                    extracted_names.add(skill.name.lower())
            
            # Method 3: Extract from headline
            headline_skills = await self._extract_from_headline(page)
            for skill in headline_skills:
                if skill.name.lower() not in extracted_names:
                    skills.append(skill)
                    extracted_names.add(skill.name.lower())
            
            self.logger.info(f"Extracted {len(skills)} unique skills")
            return skills
            
        except Exception as e:
            raise ScrapingError(f"Skill extraction failed: {e}")
    
    async def _ensure_profile_page(self, page: Page) -> None:
        """Ensure we're on the profile page."""
        current_url = page.url
        if "/in/" not in current_url:
            # Navigate to profile page
            await page.goto(f"{current_url.split('/')[0]}//{current_url.split('/')[2]}/in/")
            await page.wait_for_load_state("networkidle")
    
    async def _extract_from_skills_section(self, page: Page) -> List[Skill]:
        """Extract skills from the dedicated skills section."""
        skills = []
        
        try:
            # Find and expand skills section
            skills_section = await page.query_selector(".pv-skill-categories-section, .skills-section")
            if not skills_section:
                self.logger.debug("Skills section not found")
                return skills
            
            # Try to expand the section
            await self._expand_skills_section(page, skills_section)
            
            # Extract individual skills
            skill_elements = await skills_section.query_selector_all(
                ".pv-skill-category-entity, .skill-card-container, .skill-entity"
            )
            
            for element in skill_elements:
                skill = await self._extract_skill_from_element(element, "skills_section")
                if skill:
                    skills.append(skill)
            
            self.logger.debug(f"Extracted {len(skills)} skills from skills section")
            
        except Exception as e:
            self.logger.warning(f"Error extracting from skills section: {e}")
        
        return skills
    
    async def _expand_skills_section(self, page: Page, skills_section: ElementHandle) -> None:
        """Expand the skills section to show all skills."""
        try:
            # Look for expand buttons
            expand_selectors = [
                ".pv-skills-section__additional-skills button",
                ".skill-category-expansion button",
                "button[aria-label*='Show more']"
            ]
            
            for selector in expand_selectors:
                button = await skills_section.query_selector(selector)
                if button:
                    await button.click()
                    await page.wait_for_timeout(1000)
                    
        except Exception as e:
            self.logger.debug(f"Could not expand skills section: {e}")
    
    async def _extract_skill_from_element(self, element: ElementHandle, source: str) -> Skill:
        """Extract skill information from a DOM element."""
        try:
            # Get skill name
            name_selectors = [
                ".pv-skill-category-entity__name-text",
                ".skill-entity__skill-name",
                ".skill-card-name"
            ]
            
            skill_name = None
            for selector in name_selectors:
                name_element = await element.query_selector(selector)
                if name_element:
                    skill_name = await name_element.text_content()
                    break
            
            if not skill_name or not self._is_valid_skill_name(skill_name):
                return None
            
            # Get endorsements count
            endorsements = await self._extract_endorsements(element)
            
            # Categorize skill
            category = self._categorize_skill(skill_name)
            
            return Skill(
                name=skill_name.strip(),
                category=category,
                endorsements=endorsements,
                source=source,
                confidence=1.0
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting skill from element: {e}")
            return None
    
    async def _extract_endorsements(self, element: ElementHandle) -> int:
        """Extract endorsement count from skill element."""
        try:
            endorsement_selectors = [
                ".pv-skill-category-entity__endorsement-count",
                ".skill-entity__endorsement-count",
                ".endorsement-count"
            ]
            
            for selector in endorsement_selectors:
                count_element = await element.query_selector(selector)
                if count_element:
                    count_text = await count_element.text_content()
                    # Extract number from text like "99+ endorsements"
                    match = re.search(r"(\d+)", count_text or "")
                    if match:
                        return int(match.group(1))
            
            return 0
            
        except Exception:
            return 0
    
    async def _extract_from_experience(self, page: Page) -> List[Skill]:
        """Extract skills mentioned in experience descriptions."""
        skills = []
        
        try:
            experience_sections = await page.query_selector_all(
                ".pv-entity__position-group-pager, .experience-section .experience-item"
            )
            
            for section in experience_sections:
                # Get description text
                desc_element = await section.query_selector(
                    ".pv-entity__description, .experience-item__description"
                )
                
                if desc_element:
                    description = await desc_element.text_content()
                    if description:
                        extracted_skills = self._extract_skills_from_text(description, "experience")
                        skills.extend(extracted_skills)
            
            self.logger.debug(f"Extracted {len(skills)} skills from experience")
            
        except Exception as e:
            self.logger.warning(f"Error extracting from experience: {e}")
        
        return skills
    
    async def _extract_from_headline(self, page: Page) -> List[Skill]:
        """Extract skills from profile headline."""
        skills = []
        
        try:
            headline_element = await page.query_selector(
                ".text-body-medium, .pv-text-details__left-panel h1 + div"
            )
            
            if headline_element:
                headline = await headline_element.text_content()
                if headline:
                    skills = self._extract_skills_from_text(headline, "headline")
            
            self.logger.debug(f"Extracted {len(skills)} skills from headline")
            
        except Exception as e:
            self.logger.warning(f"Error extracting from headline: {e}")
        
        return skills
    
    def _extract_skills_from_text(self, text: str, source: str) -> List[Skill]:
        """Extract known skills from text content."""
        skills = []
        text_lower = text.lower()
        
        # Look for known skills in the text
        for skill_name, category in self._skill_categories.items():
            if skill_name in text_lower:
                skills.append(Skill(
                    name=skill_name.title(),
                    category=category,
                    endorsements=0,
                    source=source,
                    confidence=0.8  # Lower confidence for text extraction
                ))
        
        return skills
    
    def _is_valid_skill_name(self, name: str) -> bool:
        """Validate if a skill name is valid."""
        if not name or len(name.strip()) < 2:
            return False
        
        # Filter out common non-skill phrases
        invalid_phrases = [
            "show more", "show less", "see more", "see less",
            "endorsements", "connections", "followers",
            "view profile", "message", "connect"
        ]
        
        name_lower = name.lower().strip()
        return not any(phrase in name_lower for phrase in invalid_phrases)
    
    def _categorize_skill(self, skill_name: str) -> SkillCategory:
        """Categorize a skill based on its name."""
        skill_lower = skill_name.lower()
        
        # Try exact match first
        if skill_lower in self._skill_categories:
            return self._skill_categories[skill_lower]
        
        # Try partial matches for compound skills
        for known_skill, category in self._skill_categories.items():
            if known_skill in skill_lower or skill_lower in known_skill:
                return category
        
        # Default category
        return SkillCategory.OTHER