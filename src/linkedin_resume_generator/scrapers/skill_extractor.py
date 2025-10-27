"""Skill extraction logic for LinkedIn profiles."""

import re
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urlparse
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
            
            # Method 1: Navigate to skills details page for complete skills list
            skills_details_skills = await self._extract_from_skills_details_page(page)
            for skill in skills_details_skills:
                if skill.name.lower() not in extracted_names:
                    skills.append(skill)
                    extracted_names.add(skill.name.lower())
            
            # Method 2: Extract from skills section on main page (fallback)
            skills_section_skills = await self._extract_from_skills_section(page)
            for skill in skills_section_skills:
                if skill.name.lower() not in extracted_names:
                    skills.append(skill)
                    extracted_names.add(skill.name.lower())
            
            # Method 3: Extract from experience descriptions
            experience_skills = await self._extract_from_experience(page)
            for skill in experience_skills:
                if skill.name.lower() not in extracted_names:
                    skills.append(skill)
                    extracted_names.add(skill.name.lower())
            
            # Method 4: Extract from headline
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
        """Ensure we're on a valid LinkedIn profile page."""
        current_url = page.url
        
        # Check for invalid starting URLs
        if not current_url or current_url == "about:blank":
            raise ScrapingError("No starting URL available - page is blank or empty")
        
        # Parse the URL to extract components safely
        try:
            parsed_url = urlparse(current_url)
        except Exception as e:
            raise ScrapingError(f"Invalid URL format: {current_url}")
        
        # Validate that we're on LinkedIn
        if not parsed_url.netloc.endswith('linkedin.com'):
            raise ScrapingError(f"Not a LinkedIn URL: {current_url}")
        
        # Check if we're already on a valid profile page
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'in' and path_parts[1]:
            # Already on a valid "/in/<slug>" path with non-empty slug
            return
        
        # If we're not on a valid profile path, raise an error
        # Don't attempt to construct a bare "/in/" path
        raise ScrapingError(
            f"Current URL does not point to a valid LinkedIn profile (/in/<slug> pattern). "
            f"Please provide a concrete profile URL. Current URL: {current_url}"
        )
    
    async def _extract_from_skills_details_page(self, page: Page) -> List[Skill]:
        """Extract skills from the skills details page."""
        skills = []
        
        try:
            # Navigate to skills details page
            base_url = page.url.split('/in/')[0] if '/in/' in page.url else page.url
            profile_slug = page.url.split('/in/')[1].split('/')[0] if '/in/' in page.url else 'me'
            
            skills_url = f"{base_url}/in/{profile_slug}/details/skills/"
            
            self.logger.debug(f"Navigating to skills details page: {skills_url}")
            await page.goto(skills_url, wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Wait for skills list to load
            await page.wait_for_selector(
                ".pvs-list, .pvs-list__paged-list-item",
                timeout=10000
            )
            
            # Try to expand "Show more" button
            try:
                expand_buttons = await page.query_selector_all(
                    'button[aria-label*="Show more"], button[aria-label*="See more"], '
                    '.pvs-see-more-container button'
                )
                
                for button in expand_buttons:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    self.logger.debug("Clicked expand button on skills page")
            except Exception as e:
                self.logger.debug(f"Could not expand skills section: {e}")
            
            # Extract skills using updated selectors
            skill_elements = await page.query_selector_all(
                "li.pvs-list__paged-list-item, li.pvs-entity"
            )
            
            self.logger.debug(f"Found {len(skill_elements)} skill items on details page")
            
            for element in skill_elements:
                skill = await self._extract_skill_from_details_element(element)
                if skill:
                    skills.append(skill)
            
            self.logger.debug(f"Extracted {len(skills)} skills from details page")
            
        except Exception as e:
            self.logger.warning(f"Error extracting from skills details page: {e}")
        
        return skills
    
    async def _extract_skill_from_details_element(self, element: ElementHandle) -> Optional[Skill]:
        """Extract skill from a details page element."""
        try:
            # Extract skill name from t-bold span
            name_elements = await element.query_selector_all(
                ".t-bold span[aria-hidden='true'], h3.t-bold span"
            )
            
            skill_name = None
            for elem in name_elements:
                text = await elem.text_content() if elem else ""
                if text and text.strip():
                    skill_name = text.strip()
                    break
            
            if not skill_name:
                return None
            
            # Extract endorsement count
            endorsement_text = await element.text_content()
            endorsements = 0
            if endorsement_text:
                # Look for patterns like "50 endorsements" or "50+"
                match = re.search(r'(\d+)\s*\+?', endorsement_text)
                if match:
                    endorsements = int(match.group(1))
            
            # Categorize skill
            category = self._categorize_skill(skill_name)
            
            return Skill(
                name=skill_name,
                category=category,
                endorsements=endorsements,
                source="skills_details_page",
                confidence=1.0
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting skill from details element: {e}")
            return None
    
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
                    # Extract number from text like "99+ endorsements", "1,234 endorsements", "12 345 endorsements"
                    if count_text:
                        # Remove all non-digit characters (commas, spaces, plus signs, etc.)
                        cleaned_digits = re.sub(r'[^\d]', '', count_text)
                        if cleaned_digits:
                            try:
                                return int(cleaned_digits)
                            except ValueError:
                                pass  # Fall through to continue trying other selectors
            
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
        """Extract known skills from text content using word boundary matching."""
        skills = []
        text_lower = text.lower()
        
        # Look for known skills in the text using regex word boundaries
        for skill_name, category in self._skill_categories.items():
            # Escape the skill name for safe regex usage
            escaped_skill = re.escape(skill_name.lower())
            
            # Use sophisticated boundary detection to avoid false positives
            if re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', skill_name):
                # Pure alphanumeric skill starting with letter - use strict word boundaries
                pattern = rf'\b{escaped_skill}\b'
            elif re.match(r'^[\w\s.+-]+$', skill_name):
                # Skill with common symbols - use word/non-word boundaries
                pattern = rf'(?<!\w){escaped_skill}(?!\w)'
            else:
                # Complex skill with special characters - use non-alphanumeric boundaries
                pattern = rf'(?<![a-zA-Z0-9]){escaped_skill}(?![a-zA-Z0-9])'
            
            # Perform case-insensitive search
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            if matches:
                # Additional context filtering for common ambiguous terms
                should_include = True
                
                # Apply context-based filtering for highly ambiguous single-letter or common words
                if skill_name.lower() in ['go', 'python'] and category == 'Programming':
                    should_include = self._is_programming_context(text_lower, matches, skill_name.lower())
                
                if should_include:
                    skills.append(Skill(
                        name=skill_name.title(),
                        category=category,
                        endorsements=0,
                        source=source,
                        confidence=0.8  # Lower confidence for text extraction
                    ))
        
        return skills
    
    def _is_programming_context(self, text: str, matches: List, skill_name: str) -> bool:
        """Check if the skill mention appears in a programming context."""
        # Programming context indicators
        programming_indicators = [
            'programming', 'language', 'code', 'coding', 'development', 'developer',
            'software', 'script', 'scripting', 'framework', 'library', 'api',
            'backend', 'frontend', 'fullstack', 'engineer', 'engineering',
            'application', 'system', 'database', 'web', 'mobile', 'app'
        ]
        
        # Exclude patterns that indicate non-programming context
        exclude_patterns = [
            r"let'?s\s+go\s+to",  # "let's go to"
            r"go\s+to\s+",        # "go to"
            r"monty\s+python",    # "monty python"
            r"python\s+(movie|film|show)"  # "python movie/film/show"
        ]
        
        for match in matches:
            start, end = match.span()
            
            # First check for exclusion patterns in wider context
            context_start = max(0, start - 20)
            context_end = min(len(text), end + 20)
            wide_context = text[context_start:context_end]
            
            # If any exclude pattern matches, skip this occurrence
            if any(re.search(pattern, wide_context, re.IGNORECASE) for pattern in exclude_patterns):
                continue
            
            # Check programming context around the match (±50 characters)
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            context = text[context_start:context_end]
            
            # If any programming indicator is found in the context, include it
            if any(indicator in context for indicator in programming_indicators):
                return True
            
            # Special case: if it's "Go" followed by technical terms
            if skill_name == 'go':
                go_context = text[start:min(len(text), end + 30)]
                if any(term in go_context for term in ['team', 'lang', 'google', 'programming', 'dev']):
                    return True
        
        return False
    
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