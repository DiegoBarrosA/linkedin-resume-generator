"""Custom exceptions for LinkedIn Resume Generator."""

from typing import Optional, Dict, Any


class LinkedInResumeGeneratorError(Exception):
    """Base exception for LinkedIn Resume Generator."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(LinkedInResumeGeneratorError):
    """Raised when there are configuration issues."""
    pass


class AuthenticationError(LinkedInResumeGeneratorError):
    """Raised when LinkedIn authentication fails."""
    pass


class ScrapingError(LinkedInResumeGeneratorError):
    """Raised when scraping fails."""
    
    def __init__(self, message: str, page_url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.page_url = page_url


class TwoFactorAuthError(AuthenticationError):
    """Raised when 2FA authentication fails."""
    pass


class ProfileNotFoundError(ScrapingError):
    """Raised when LinkedIn profile is not found."""
    pass


class ElementNotFoundError(ScrapingError):
    """Raised when expected page elements are not found."""
    
    def __init__(self, message: str, selector: Optional[str] = None, page_url: Optional[str] = None):
        super().__init__(message, page_url)
        self.selector = selector


class DataValidationError(LinkedInResumeGeneratorError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value


class ProcessingError(LinkedInResumeGeneratorError):
    """Raised when data processing fails."""
    pass


class GenerationError(LinkedInResumeGeneratorError):
    """Raised when resume generation fails."""
    pass


class ComplianceError(LinkedInResumeGeneratorError):
    """Raised when compliance violations are detected."""
    
    def __init__(self, message: str, violations: Optional[list] = None):
        super().__init__(message)
        self.violations = violations or []


class RateLimitError(ScrapingError):
    """Raised when LinkedIn rate limits are hit."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class NetworkError(ScrapingError):
    """Raised when network issues occur."""
    pass


class TimeoutError(ScrapingError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: Optional[int] = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds