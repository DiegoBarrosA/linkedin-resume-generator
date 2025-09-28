"""Tests for configuration management."""

import pytest
import os
import tempfile
from pathlib import Path
from pydantic import ValidationError

from linkedin_resume_generator.config.settings import (
    Settings, LinkedInCredentials, ScrapingConfig,
    OutputConfig, ComplianceConfig, LoggingConfig
)


class TestLinkedInCredentials:
    """Test LinkedIn credentials validation."""
    
    def test_valid_credentials(self):
        """Test valid credentials creation."""
        creds = LinkedInCredentials(
            email="test@example.com",
            password="secure_password",
            totp_secret="SECRET123"
        )
        assert creds.email == "test@example.com"
        assert creds.password == "secure_password"
        assert creds.totp_secret == "SECRET123"
    
    def test_required_fields(self):
        """Test required fields validation."""
        # Email is required
        with pytest.raises(ValidationError):
            LinkedInCredentials(password="password")
        
        # Password is required  
        with pytest.raises(ValidationError):
            LinkedInCredentials(email="test@example.com")
    
    def test_optional_totp_secret(self):
        """Test TOTP secret is optional."""
        creds = LinkedInCredentials(
            email="test@example.com",
            password="password"
        )
        assert creds.totp_secret is None


class TestScrapingConfig:
    """Test scraping configuration."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ScrapingConfig()
        assert config.timeout == 30
        assert config.headless is True
        assert config.slow_mo == 100
    
    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid timeout
        config = ScrapingConfig(timeout=60)
        assert config.timeout == 60
        
        # Too small timeout
        with pytest.raises(ValidationError):
            ScrapingConfig(timeout=1)
        
        # Too large timeout
        with pytest.raises(ValidationError):
            ScrapingConfig(timeout=500)


class TestOutputConfig:
    """Test output configuration."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = OutputConfig()
        assert config.output_dir == Path(".")
        assert config.resume_filename == "resume.md"
        assert config.index_filename == "index.md"
        assert config.create_github_pages is True
    
    def test_output_directory_creation(self, temp_dir):
        """Test output directory is created."""
        new_dir = temp_dir / "test_output"
        config = OutputConfig(output_dir=new_dir)
        
        # Directory should be created
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_string_to_path_conversion(self, temp_dir):
        """Test string paths are converted to Path objects."""
        config = OutputConfig(output_dir=str(temp_dir))
        assert isinstance(config.output_dir, Path)
        assert config.output_dir == temp_dir


class TestComplianceConfig:
    """Test compliance configuration."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ComplianceConfig()
        assert config.auto_cleanup is True
        assert config.audit_enabled is True
        assert config.privacy_mode is True
        assert config.data_retention_hours == 0
    
    def test_data_retention_validation(self):
        """Test data retention validation."""
        # Valid values
        ComplianceConfig(data_retention_hours=0)
        ComplianceConfig(data_retention_hours=12)
        ComplianceConfig(data_retention_hours=24)
        
        # Invalid values
        with pytest.raises(ValidationError):
            ComplianceConfig(data_retention_hours=-1)
        
        with pytest.raises(ValidationError):
            ComplianceConfig(data_retention_hours=25)


class TestLoggingConfig:
    """Test logging configuration."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.file_enabled is False
        assert config.file_path is None
    
    def test_level_validation(self):
        """Test logging level validation."""
        # Valid levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config = LoggingConfig(level=level)
            assert config.level == level
        
        # Case insensitive
        config = LoggingConfig(level="debug")
        assert config.level == "DEBUG"
        
        # Invalid level
        with pytest.raises(ValidationError):
            LoggingConfig(level="INVALID")


class TestSettings:
    """Test main Settings class."""
    
    def test_settings_creation(self, mock_credentials):
        """Test settings creation with required fields."""
        settings = Settings(
            linkedin=mock_credentials,
            github_token="test_token"
        )
        assert settings.linkedin.email == "test@example.com"
        assert settings.github_token == "test_token"
    
    def test_default_configurations(self, mock_credentials):
        """Test default sub-configurations are created."""
        settings = Settings(
            linkedin=mock_credentials,
            github_token="test_token"
        )
        
        # Default configs should be created
        assert isinstance(settings.scraping, ScrapingConfig)
        assert isinstance(settings.output, OutputConfig)
        assert isinstance(settings.compliance, ComplianceConfig)
        assert isinstance(settings.logging, LoggingConfig)
    
    def test_environment_validation(self, mock_credentials):
        """Test environment validation."""
        # Valid environments
        valid_envs = ["development", "production", "testing"]
        for env in valid_envs:
            settings = Settings(
                linkedin=mock_credentials,
                github_token="test_token",
                environment=env
            )
            assert settings.environment == env
        
        # Invalid environment
        with pytest.raises(ValidationError):
            Settings(
                linkedin=mock_credentials,
                github_token="test_token",
                environment="invalid"
            )
    
    def test_credentials_validation_method(self, mock_credentials):
        """Test credentials validation method."""
        settings = Settings(
            linkedin=mock_credentials,
            github_token="test_token"
        )
        
        # Should not raise with valid credentials
        assert settings.validate_credentials() is True
        
        # Test with invalid credentials
        invalid_creds = LinkedInCredentials(email="", password="test")
        settings_invalid = Settings(
            linkedin=invalid_creds,
            github_token="test_token"
        )
        
        with pytest.raises(ValueError):
            settings_invalid.validate_credentials()


class TestSettingsFromEnvironment:
    """Test settings creation from environment variables."""
    
    def test_from_env_method(self):
        """Test creating settings from environment variables."""
        # Set environment variables
        env_vars = {
            "LINKEDIN_EMAIL": "env@example.com",
            "LINKEDIN_PASSWORD": "env_password",
            "GITHUB_TOKEN": "env_github_token",
            "ENVIRONMENT": "testing",
            "DEBUG": "true",
            "LINKEDIN_CI_MODE": "true"
        }
        
        # Patch environment
        with pytest.MonkeyPatch().context() as m:
            for key, value in env_vars.items():
                m.setenv(key, value)
            
            settings = Settings.from_env()
            
            assert settings.linkedin.email == "env@example.com"
            assert settings.linkedin.password == "env_password"
            assert settings.github_token == "env_github_token"
            assert settings.environment == "testing"
            assert settings.debug is True
            assert settings.ci_mode is True
    
    def test_env_file_loading(self, temp_dir):
        """Test loading from .env file."""
        env_file = temp_dir / ".env"
        env_content = """
LINKEDIN_EMAIL=file@example.com
LINKEDIN_PASSWORD=file_password
GITHUB_TOKEN=file_github_token
ENVIRONMENT=development
DEBUG=false
"""
        env_file.write_text(env_content)
        
        # Change to temp directory to test .env loading
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            settings = Settings.from_env()
            
            assert settings.linkedin.email == "file@example.com"
            assert settings.linkedin.password == "file_password"
            assert settings.github_token == "file_github_token"
            assert settings.environment == "development"
            assert settings.debug is False
        finally:
            os.chdir(original_cwd)
    
    def test_nested_env_variables(self):
        """Test nested environment variable mapping."""
        env_vars = {
            "LINKEDIN_EMAIL": "test@example.com",
            "LINKEDIN_PASSWORD": "password",
            "GITHUB_TOKEN": "token",
            "COMPLIANCE__AUTO_CLEANUP": "false",
            "COMPLIANCE__PRIVACY_MODE": "false",
            "LOGGING__LEVEL": "ERROR",
            "SCRAPING__TIMEOUT": "60"
        }
        
        with pytest.MonkeyPatch().context() as m:
            for key, value in env_vars.items():
                m.setenv(key, value)
            
            settings = Settings.from_env()
            
            # Check nested configurations
            assert settings.compliance.auto_cleanup is False
            assert settings.compliance.privacy_mode is False
            assert settings.logging.level == "ERROR"
            assert settings.scraping.timeout == 60


class TestConfigurationEdgeCases:
    """Test configuration edge cases and error handling."""
    
    def test_missing_required_credentials(self):
        """Test missing required credentials."""
        with pytest.raises(ValidationError):
            Settings(github_token="token")  # Missing linkedin
    
    def test_invalid_path_handling(self):
        """Test invalid path handling."""
        # Test with invalid path characters (platform dependent)
        try:
            config = OutputConfig(output_dir="/invalid\0path")
            # If no exception, the path was accepted
        except (ValidationError, OSError, ValueError):
            # Expected for invalid paths
            pass
    
    def test_configuration_serialization(self, test_settings):
        """Test configuration can be serialized."""
        # Test model_dump
        config_dict = test_settings.model_dump()
        assert isinstance(config_dict, dict)
        assert "linkedin" in config_dict
        assert "scraping" in config_dict
        
        # Test JSON serialization
        json_str = test_settings.model_dump_json()
        assert isinstance(json_str, str)
        assert "linkedin" in json_str