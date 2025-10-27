"""Configuration management using Pydantic Settings."""

import os
from typing import Optional
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LinkedInCredentials(BaseModel):
    """LinkedIn authentication credentials."""
    
    email: str = Field(default="", description="LinkedIn login email")
    password: str = Field(default="", description="LinkedIn password") 
    totp_secret: Optional[str] = Field(default=None, description="TOTP secret for 2FA")


class ScrapingConfig(BaseModel):
    """Configuration for scraping behavior."""
    
    timeout: int = Field(default=30, description="Page timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    slow_mo: int = Field(default=100, description="Slow motion delay in milliseconds")
    
    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        if v < 5 or v > 300:
            raise ValueError("Timeout must be between 5 and 300 seconds")
        return v


class OutputConfig(BaseModel):
    """Configuration for output generation."""
    
    output_dir: Path = Field(default=Path("."), description="Output directory")
    resume_filename: str = Field(default="resume.md", description="Resume filename")
    index_filename: str = Field(default="index.md", description="GitHub Pages index filename")
    create_github_pages: bool = Field(default=True, description="Create GitHub Pages index")
    
    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


class ComplianceConfig(BaseModel):
    """Configuration for compliance and privacy."""
    
    auto_cleanup: bool = Field(default=True, description="Automatically clean up raw data")
    audit_enabled: bool = Field(default=True, description="Enable compliance auditing")
    privacy_mode: bool = Field(default=True, description="Enable privacy-safe processing")
    data_retention_hours: int = Field(default=0, description="Hours to retain raw data (0=immediate cleanup)")
    
    @field_validator("data_retention_hours")
    @classmethod
    def validate_retention(cls, v):
        if v < 0 or v > 24:
            raise ValueError("Data retention must be between 0 and 24 hours")
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    file_enabled: bool = Field(default=False, description="Enable file logging")
    file_path: Optional[Path] = Field(None, description="Log file path")
    
    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="production", description="Environment (development/production)")
    ci_mode: bool = Field(default=False, description="CI/non-interactive mode")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Credentials  
    linkedin: LinkedInCredentials = Field(default_factory=LinkedInCredentials)
    
    # Configuration sections
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # GitHub configuration
    github_token: Optional[str] = Field(default=None, description="GitHub token for API access")
    github_pages_enabled: bool = Field(default=False, description="Enable GitHub Pages deployment")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields (like LINKEDIN_EMAIL) during construction
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ["development", "production", "testing"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v
    
    def validate_credentials(self) -> bool:
        """Validate that required credentials are present."""
        if not self.linkedin.email:
            raise ValueError("LinkedIn email is required")
        if not self.linkedin.password:
            raise ValueError("LinkedIn password is required")
        return True
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"


def get_settings() -> Settings:
    """Get application settings with proper credential handling."""
    # Load .env file explicitly since BaseSettings might not do it automatically
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create settings from BaseSettings (reads .env file automatically)
    settings = Settings()
    
    # Handle legacy environment variable names and populate nested linkedin model
    if os.getenv("LINKEDIN_EMAIL"):
        settings.linkedin.email = os.getenv("LINKEDIN_EMAIL", "")
    if os.getenv("LINKEDIN_PASSWORD"):
        settings.linkedin.password = os.getenv("LINKEDIN_PASSWORD", "")
    if os.getenv("LINKEDIN_TOTP_SECRET"):
        settings.linkedin.totp_secret = os.getenv("LINKEDIN_TOTP_SECRET")
    
    # Handle CI mode
    if os.getenv("LINKEDIN_CI_MODE"):
        settings.ci_mode = os.getenv("LINKEDIN_CI_MODE", "false").lower() == "true"
    
    return settings