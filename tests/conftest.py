"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import Mock, AsyncMock
from pathlib import Path
import tempfile
from datetime import datetime

from linkedin_resume_generator.config.settings import (
    Settings, LinkedInCredentials, ScrapingConfig, 
    OutputConfig, ComplianceConfig, LoggingConfig
)
from linkedin_resume_generator.models.profile import (
    ProfileData, Experience, Education, Skill, 
    ContactInfo, SkillCategory
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_credentials():
    """Mock LinkedIn credentials for testing."""
    return LinkedInCredentials(
        email="test@example.com",
        password="testpass123",
        totp_secret="TESTSECRET123"
    )


@pytest.fixture
def test_settings(mock_credentials, temp_dir):
    """Create test settings configuration."""
    return Settings(
        linkedin=mock_credentials,
        github_token="test_token",
        scraping=ScrapingConfig(
            timeout=30,
            headless=True,
            slow_mo=100
        ),
        output=OutputConfig(
            output_dir=temp_dir,
            resume_filename="test_resume.md",
            index_filename="test_index.md",
            create_github_pages=False
        ),
        compliance=ComplianceConfig(
            auto_cleanup=True,
            audit_enabled=True,
            privacy_mode=True,
            data_retention_hours=0
        ),
        logging=LoggingConfig(
            level="DEBUG",
            file_enabled=False,
            file_path=None
        ),
        environment="testing",
        debug=True,
        ci_mode=True
    )


@pytest.fixture
def sample_contact_info():
    """Sample contact information for testing."""
    return ContactInfo(
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        linkedin_url="https://linkedin.com/in/johndoe",
        location="San Francisco, CA",
        website="https://johndoe.dev"
    )


@pytest.fixture
def sample_skills():
    """Sample skills for testing."""
    return [
        Skill(
            name="Python",
            category=SkillCategory.PROGRAMMING,
            endorsements=15,
            source="skills_section",
            confidence=1.0
        ),
        Skill(
            name="Machine Learning",
            category=SkillCategory.TECHNICAL,
            endorsements=8,
            source="experience_description",
            confidence=0.9
        ),
        Skill(
            name="Docker",
            category=SkillCategory.TOOLS,
            endorsements=5,
            source="skills_section",
            confidence=1.0
        )
    ]


@pytest.fixture
def sample_experience():
    """Sample work experience for testing."""
    return [
        Experience(
            title="Senior Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            start_date="Jan 2020",
            end_date="Present",
            duration="4 years",
            description="Led development of machine learning platform using Python and Docker. Managed team of 5 engineers and delivered 3 major product releases.",
            skills=["Python", "Machine Learning", "Docker", "Leadership"]
        ),
        Experience(
            title="Software Engineer",
            company="Startup Inc",
            location="Palo Alto, CA", 
            start_date="Jun 2018",
            end_date="Dec 2019",
            duration="1 year 6 months",
            description="Built scalable web applications using modern frameworks. Contributed to open source projects.",
            skills=["JavaScript", "React", "Node.js"]
        )
    ]


@pytest.fixture
def sample_education():
    """Sample education for testing."""
    return [
        Education(
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            institution="Stanford University",
            start_date="2014",
            end_date="2018",
            grade="3.8 GPA",
            description="Focus on artificial intelligence and machine learning. Dean's list for 6 semesters."
        )
    ]


@pytest.fixture
def sample_profile_data(sample_contact_info, sample_skills, sample_experience, sample_education):
    """Sample complete profile data for testing."""
    return ProfileData(
        name="John Doe",
        headline="Senior Software Engineer | ML Expert | Python Developer",
        summary="Experienced software engineer with 6+ years developing scalable systems and machine learning solutions. Passionate about clean code and team leadership.",
        location="San Francisco, CA",
        contact_info=sample_contact_info,
        skills=sample_skills,
        experience=sample_experience,
        education=sample_education,
        scraped_at=datetime.utcnow(),
        profile_url="https://linkedin.com/in/johndoe"
    )


@pytest.fixture
def mock_playwright_page():
    """Mock Playwright page object."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.query_selector = AsyncMock()
    page.query_selector_all = AsyncMock()
    page.evaluate = AsyncMock()
    page.screenshot = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser object."""
    browser = AsyncMock()
    browser.new_page = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_playwright_context():
    """Mock Playwright browser context."""
    context = AsyncMock()
    context.new_page = AsyncMock()
    context.close = AsyncMock()
    return context


@pytest.fixture(autouse=True)
def mock_structlog_logger():
    """Mock structlog logger to avoid setup issues in tests."""
    with pytest.MonkeyPatch().context() as m:
        mock_logger = Mock()
        mock_logger.info = Mock()
        mock_logger.debug = Mock()
        mock_logger.warning = Mock()
        mock_logger.error = Mock()
        mock_logger.critical = Mock()
        
        # Mock the get_logger function
        m.setattr("linkedin_resume_generator.utils.logging.get_logger", Mock(return_value=mock_logger))
        yield mock_logger


# Test data constants
SAMPLE_LINKEDIN_HTML = """
<html>
<head><title>John Doe | LinkedIn</title></head>
<body>
    <div class="pv-text-details__left-panel">
        <h1>John Doe</h1>
        <div class="text-body-medium">Senior Software Engineer</div>
    </div>
    <div class="pv-about-section">
        <p>Experienced software engineer...</p>
    </div>
</body>
</html>
"""

SAMPLE_SKILLS_HTML = """
<div class="pvs-list__outer-container">
    <li class="pvs-list__paged-list-item">
        <span class="mr1 t-bold"><span>Python</span></span>
        <span class="t-14 t-black--light">15 endorsements</span>
    </li>
    <li class="pvs-list__paged-list-item">
        <span class="mr1 t-bold"><span>Machine Learning</span></span>
        <span class="t-14 t-black--light">8 endorsements</span>
    </li>
</div>
"""

SAMPLE_EXPERIENCE_HTML = """
<div class="pvs-list__outer-container">
    <li class="pvs-list__item-v2">
        <div class="display-flex flex-column full-width">
            <span class="mr1 hoverable-link-text t-bold">
                <span>Senior Software Engineer</span>
            </span>
            <span class="t-14 t-black--light">
                <span class="visually-hidden">Company name</span>
                <span>Tech Corp</span>
            </span>
        </div>
    </li>
</div>
"""