"""
LinkedIn Resume Generator

A professional tool for generating resumes from LinkedIn profiles with
comprehensive compliance safeguards and modular architecture.
"""

__version__ = "2.0.0"
__author__ = "Diego Barros"
__email__ = "your-email@example.com"

from .config.settings import Settings
from .models.profile import ProfileData
from .scrapers.linkedin_scraper import LinkedInScraper
from .generators.resume_generator import ResumeGenerator

__all__ = [
    "Settings",
    "ProfileData", 
    "LinkedInScraper",
    "ResumeGenerator",
]