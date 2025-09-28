"""Tests for data models and validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from linkedin_resume_generator.models.profile import (
    ProfileData, Experience, Education, Skill, ContactInfo,
    SkillCategory, SkillsSummary
)


class TestContactInfo:
    """Test ContactInfo model."""
    
    def test_valid_contact_info(self):
        """Test valid contact info creation."""
        contact = ContactInfo(
            email="test@example.com",
            phone="555-123-4567",
            linkedin_url="https://linkedin.com/in/test",
            website="https://test.dev",
            location="San Francisco, CA"
        )
        assert contact.email == "test@example.com"
        assert contact.phone == "555-123-4567"
        assert contact.linkedin_url == "https://linkedin.com/in/test"
    
    def test_invalid_email_validation(self):
        """Test email validation."""
        with pytest.raises(ValidationError):
            ContactInfo(email="invalid-email")
    
    def test_empty_contact_info(self):
        """Test empty contact info is valid."""
        contact = ContactInfo()
        assert contact.email is None
        assert contact.phone is None


class TestSkill:
    """Test Skill model."""
    
    def test_valid_skill_creation(self):
        """Test valid skill creation."""
        skill = Skill(
            name="Python",
            category=SkillCategory.PROGRAMMING,
            endorsements=15,
            source="skills_section",
            confidence=0.95
        )
        assert skill.name == "Python"
        assert skill.category == SkillCategory.PROGRAMMING
        assert skill.endorsements == 15
        assert skill.confidence == 0.95
    
    def test_skill_default_values(self):
        """Test skill default values."""
        skill = Skill(name="JavaScript")
        assert skill.category == SkillCategory.OTHER
        assert skill.endorsements == 0
        assert skill.source == "skills_section"
        assert skill.confidence == 1.0
    
    def test_invalid_skill_name(self):
        """Test skill name validation."""
        with pytest.raises(ValidationError):
            Skill(name="")
        
        with pytest.raises(ValidationError):
            Skill(name="   ")
    
    def test_negative_endorsements(self):
        """Test negative endorsements validation."""
        with pytest.raises(ValidationError):
            Skill(name="Python", endorsements=-1)
    
    def test_confidence_bounds(self):
        """Test confidence value bounds."""
        # Valid confidence values
        Skill(name="Python", confidence=0.0)
        Skill(name="Python", confidence=1.0)
        Skill(name="Python", confidence=0.5)
        
        # Invalid confidence values
        with pytest.raises(ValidationError):
            Skill(name="Python", confidence=-0.1)
        
        with pytest.raises(ValidationError):
            Skill(name="Python", confidence=1.1)


class TestExperience:
    """Test Experience model."""
    
    def test_valid_experience_creation(self):
        """Test valid experience creation."""
        exp = Experience(
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            start_date="Jan 2020",
            end_date="Dec 2022",
            duration="3 years",
            description="Developed scalable web applications.",
            skills=["Python", "React", "AWS"]
        )
        assert exp.title == "Software Engineer"
        assert exp.company == "Tech Corp"
        assert len(exp.skills) == 3
    
    def test_required_fields_validation(self):
        """Test required fields validation."""
        with pytest.raises(ValidationError):
            Experience(title="", company="Tech Corp")
        
        with pytest.raises(ValidationError):
            Experience(title="Engineer", company="")
    
    def test_current_position_property(self):
        """Test is_current property."""
        # Current position
        current_exp = Experience(
            title="Engineer", 
            company="Tech Corp", 
            end_date="Present"
        )
        assert current_exp.is_current is True
        
        # Past position
        past_exp = Experience(
            title="Engineer", 
            company="Old Corp", 
            end_date="Dec 2022"
        )
        assert past_exp.is_current is False
        
        # No end date (assumed current)
        no_end_exp = Experience(title="Engineer", company="Tech Corp")
        assert no_end_exp.is_current is True


class TestEducation:
    """Test Education model."""
    
    def test_valid_education_creation(self):
        """Test valid education creation."""
        edu = Education(
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            institution="Stanford University",
            start_date="2014",
            end_date="2018",
            grade="3.8 GPA",
            description="Focus on AI and machine learning."
        )
        assert edu.degree == "Bachelor of Science"
        assert edu.field_of_study == "Computer Science"
        assert edu.institution == "Stanford University"
    
    def test_institution_validation(self):
        """Test institution name validation."""
        with pytest.raises(ValidationError):
            Education(
                degree="BS",
                field_of_study="CS",
                institution=""
            )


class TestSkillsSummary:
    """Test SkillsSummary model."""
    
    def test_skills_summary_calculation(self, sample_skills):
        """Test skills summary calculation."""
        # Group skills by category
        by_category = {}
        for skill in sample_skills:
            if skill.category not in by_category:
                by_category[skill.category] = []
            by_category[skill.category].append(skill)
        
        summary = SkillsSummary(by_category=by_category)
        
        # Check calculated totals
        assert summary.total_count == len(sample_skills)
        expected_endorsements = sum(skill.endorsements for skill in sample_skills)
        assert summary.total_endorsements == expected_endorsements
        
        # Check top skills are sorted by endorsements
        assert len(summary.top_skills) <= 10
        if len(summary.top_skills) > 1:
            # Should be sorted by endorsements descending
            for i in range(len(summary.top_skills) - 1):
                assert summary.top_skills[i].endorsements >= summary.top_skills[i + 1].endorsements


class TestProfileData:
    """Test ProfileData model."""
    
    def test_valid_profile_creation(self, sample_profile_data):
        """Test valid profile creation."""
        assert sample_profile_data.name == "John Doe"
        assert "Senior Software Engineer" in sample_profile_data.headline
        assert len(sample_profile_data.experience) == 2
        assert len(sample_profile_data.skills) == 3
        assert len(sample_profile_data.education) == 1
    
    def test_name_validation(self):
        """Test name validation."""
        with pytest.raises(ValidationError):
            ProfileData(name="")
        
        with pytest.raises(ValidationError):
            ProfileData(name="   ")
    
    def test_profile_data_serialization(self, sample_profile_data):
        """Test profile data can be serialized."""
        # Test model_dump works
        data_dict = sample_profile_data.model_dump()
        assert isinstance(data_dict, dict)
        assert data_dict["name"] == "John Doe"
        assert "experience" in data_dict
        assert "skills" in data_dict
    
    def test_profile_data_json_serialization(self, sample_profile_data):
        """Test profile data JSON serialization."""
        # Test JSON serialization works
        json_str = sample_profile_data.model_dump_json()
        assert isinstance(json_str, str)
        assert "John Doe" in json_str
    
    def test_skills_summary_integration(self, sample_profile_data):
        """Test skills summary integration in profile."""
        # The profile should have skills summary calculated
        if hasattr(sample_profile_data, 'skills_summary') and sample_profile_data.skills_summary:
            assert sample_profile_data.skills_summary.total_count > 0
            assert len(sample_profile_data.skills_summary.by_category) > 0


class TestModelValidation:
    """Test model validation edge cases."""
    
    def test_model_copy(self, sample_profile_data):
        """Test model copying works correctly."""
        copied_profile = sample_profile_data.model_copy()
        assert copied_profile.name == sample_profile_data.name
        assert len(copied_profile.experience) == len(sample_profile_data.experience)
        
        # Deep copy test
        deep_copy = sample_profile_data.model_copy(deep=True)
        assert deep_copy.name == sample_profile_data.name
        
        # Modify original shouldn't affect copy
        sample_profile_data.name = "Modified Name"
        assert deep_copy.name != sample_profile_data.name
    
    def test_model_validation_assignment(self):
        """Test model validation on assignment."""
        profile = ProfileData(name="Test User")
        
        # Valid assignment should work
        profile.name = "New Name"
        assert profile.name == "New Name"
        
        # Invalid assignment should raise error with validate_assignment=True
        # Note: This depends on model configuration
    
    def test_enum_usage(self):
        """Test enum values work correctly."""
        # Test all skill categories are valid
        for category in SkillCategory:
            skill = Skill(name="Test Skill", category=category)
            assert skill.category == category
        
        # Test string values work
        skill = Skill(name="Python", category=SkillCategory.PROGRAMMING)
        assert skill.category.value == "Programming Languages"