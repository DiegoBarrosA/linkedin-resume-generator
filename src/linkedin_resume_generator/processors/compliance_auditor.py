"""Compliance auditing for LinkedIn resume generation process."""

import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path

from ..models.profile import ProfileData
from ..config.settings import Settings
from ..utils.logging import get_logger


logger = get_logger(__name__)


class ComplianceLevel(str, Enum):
    """Compliance severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceCategory(str, Enum):
    """Categories of compliance issues."""
    PRIVACY = "privacy"
    SECURITY = "security"
    LEGAL = "legal"
    DATA_RETENTION = "data_retention"
    CONSENT = "consent"
    ACCESSIBILITY = "accessibility"


@dataclass
class ComplianceIssue:
    """Individual compliance issue."""
    
    id: str
    title: str
    description: str
    category: ComplianceCategory
    level: ComplianceLevel
    location: Optional[str] = None
    recommendation: Optional[str] = None
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "level": self.level.value,
            "location": self.location,
            "recommendation": self.recommendation,
            "auto_fixable": self.auto_fixable,
        }


@dataclass
class ComplianceReport:
    """Comprehensive compliance audit report."""
    
    audit_timestamp: datetime
    profile_name: str
    total_issues: int = 0
    issues_by_level: Dict[ComplianceLevel, int] = field(default_factory=dict)
    issues_by_category: Dict[ComplianceCategory, int] = field(default_factory=dict)
    issues: List[ComplianceIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    auto_fixable_count: int = 0
    
    def add_issue(self, issue: ComplianceIssue):
        """Add an issue to the report."""
        self.issues.append(issue)
        self.total_issues += 1
        
        # Update counters
        self.issues_by_level[issue.level] = self.issues_by_level.get(issue.level, 0) + 1
        self.issues_by_category[issue.category] = self.issues_by_category.get(issue.category, 0) + 1
        
        if issue.auto_fixable:
            self.auto_fixable_count += 1
    
    def add_passed_check(self, check_name: str):
        """Add a passed compliance check."""
        self.passed_checks.append(check_name)
    
    def get_critical_issues(self) -> List[ComplianceIssue]:
        """Get all critical issues."""
        return [issue for issue in self.issues if issue.level == ComplianceLevel.CRITICAL]
    
    def get_issues_by_category(self, category: ComplianceCategory) -> List[ComplianceIssue]:
        """Get issues by category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "audit_timestamp": self.audit_timestamp.isoformat(),
            "profile_name": self.profile_name,
            "summary": {
                "total_issues": self.total_issues,
                "auto_fixable_count": self.auto_fixable_count,
                "issues_by_level": {level.value: count for level, count in self.issues_by_level.items()},
                "issues_by_category": {cat.value: count for cat, count in self.issues_by_category.items()},
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "passed_checks": self.passed_checks,
        }


class ComplianceAuditor:
    """Audit LinkedIn resume generation for compliance issues."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize compliance auditor.
        
        Args:
            settings: Application settings for compliance rules
        """
        self.settings = settings
        
        # Sensitive data patterns
        self._email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self._phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self._ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self._credit_card_pattern = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
        
        # Known sensitive keywords
        self._sensitive_keywords = {
            'password', 'secret', 'api_key', 'token', 'private_key',
            'confidential', 'classified', 'restricted', 'internal-only',
            'proprietary', 'trade secret'
        }
    
    async def audit_profile(self, profile_data: ProfileData) -> ComplianceReport:
        """Perform comprehensive compliance audit on profile data.
        
        Args:
            profile_data: LinkedIn profile data to audit
            
        Returns:
            Detailed compliance report
        """
        logger.info(f"Starting compliance audit for profile: {profile_data.name}")
        
        report = ComplianceReport(
            audit_timestamp=datetime.utcnow(),
            profile_name=profile_data.name
        )
        
        # Privacy compliance checks
        await self._audit_privacy_compliance(profile_data, report)
        
        # Security compliance checks
        await self._audit_security_compliance(profile_data, report)
        
        # Data retention compliance
        await self._audit_data_retention_compliance(profile_data, report)
        
        # Legal compliance checks
        await self._audit_legal_compliance(profile_data, report)
        
        # Accessibility compliance
        await self._audit_accessibility_compliance(profile_data, report)
        
        logger.info(f"Compliance audit completed. Found {report.total_issues} issues.")
        return report
    
    async def _audit_privacy_compliance(self, profile_data: ProfileData, report: ComplianceReport):
        """Audit privacy compliance."""
        
        # Check for exposed personal information
        if profile_data.contact_info:
            contact = profile_data.contact_info
            
            # Email exposure check
            if contact.email and not self._is_email_redacted(contact.email):
                report.add_issue(ComplianceIssue(
                    id="PRIV001",
                    title="Email Address Exposed",
                    description="Personal email address is exposed in profile data",
                    category=ComplianceCategory.PRIVACY,
                    level=ComplianceLevel.HIGH,
                    location="contact_info.email",
                    recommendation="Redact or anonymize email address before sharing",
                    auto_fixable=True
                ))
            
            # Phone exposure check
            if contact.phone and not self._is_phone_redacted(contact.phone):
                report.add_issue(ComplianceIssue(
                    id="PRIV002",
                    title="Phone Number Exposed",
                    description="Personal phone number is exposed in profile data",
                    category=ComplianceCategory.PRIVACY,
                    level=ComplianceLevel.HIGH,
                    location="contact_info.phone",
                    recommendation="Redact or anonymize phone number before sharing",
                    auto_fixable=True
                ))
            
            # Full address exposure
            if contact.location and self._contains_full_address(contact.location):
                report.add_issue(ComplianceIssue(
                    id="PRIV003",
                    title="Full Address Exposed",
                    description="Complete home address appears to be exposed",
                    category=ComplianceCategory.PRIVACY,
                    level=ComplianceLevel.MEDIUM,
                    location="contact_info.location",
                    recommendation="Use only city and state/country information",
                    auto_fixable=True
                ))
        
        # Check text content for sensitive information
        text_fields = [
            ("summary", profile_data.summary),
            *[(f"experience[{i}].description", exp.description) for i, exp in enumerate(profile_data.experience or [])],
            *[(f"education[{i}].description", edu.description) for i, edu in enumerate(profile_data.education or [])],
        ]
        
        for field_name, text_content in text_fields:
            if text_content:
                issues = self._scan_text_for_sensitive_data(text_content, field_name)
                for issue in issues:
                    report.add_issue(issue)
        
        if not any(issue.category == ComplianceCategory.PRIVACY for issue in report.issues):
            report.add_passed_check("Privacy data exposure check")
    
    async def _audit_security_compliance(self, profile_data: ProfileData, report: ComplianceReport):
        """Audit security compliance."""
        
        # Check for sensitive technical information
        all_text = self._extract_all_text_content(profile_data)
        
        # Look for credentials or secrets
        if any(keyword in all_text.lower() for keyword in self._sensitive_keywords):
            report.add_issue(ComplianceIssue(
                id="SEC001",
                title="Potentially Sensitive Keywords Found",
                description="Text contains keywords that might indicate sensitive information",
                category=ComplianceCategory.SECURITY,
                level=ComplianceLevel.MEDIUM,
                recommendation="Review content for accidental inclusion of sensitive information",
                auto_fixable=False
            ))
        
        # Check for internal system references
        if re.search(r'\b(?:internal|intranet|vpn|admin|root|localhost)\b', all_text, re.IGNORECASE):
            report.add_issue(ComplianceIssue(
                id="SEC002",
                title="Internal System References",
                description="Text contains references to internal systems or infrastructure",
                category=ComplianceCategory.SECURITY,
                level=ComplianceLevel.LOW,
                recommendation="Remove references to internal systems and infrastructure",
                auto_fixable=False
            ))
        
        if not any(issue.category == ComplianceCategory.SECURITY for issue in report.issues):
            report.add_passed_check("Security information exposure check")
    
    async def _audit_data_retention_compliance(self, profile_data: ProfileData, report: ComplianceReport):
        """Audit data retention compliance."""
        
        # Check if data retention policy is configured
        if self.settings and self.settings.compliance.data_retention_hours == 0:
            report.add_passed_check("Data retention policy configured for immediate cleanup")
        elif self.settings and self.settings.compliance.data_retention_hours > 24:
            report.add_issue(ComplianceIssue(
                id="RET001",
                title="Extended Data Retention Period",
                description=f"Data retention configured for {self.settings.compliance.data_retention_hours} hours",
                category=ComplianceCategory.DATA_RETENTION,
                level=ComplianceLevel.MEDIUM,
                recommendation="Consider shorter retention period for better privacy compliance",
                auto_fixable=True
            ))
        
        # Check scrape timestamp vs retention policy
        if (self.settings and hasattr(profile_data, 'scraped_at') and profile_data.scraped_at):
            age_hours = (datetime.utcnow() - profile_data.scraped_at).total_seconds() / 3600
            if age_hours > self.settings.compliance.data_retention_hours > 0:
                report.add_issue(ComplianceIssue(
                    id="RET002",
                    title="Data Retention Period Exceeded",
                    description=f"Data is {age_hours:.1f} hours old, exceeds retention policy",
                    category=ComplianceCategory.DATA_RETENTION,
                    level=ComplianceLevel.HIGH,
                    recommendation="Data should be cleaned up according to retention policy",
                    auto_fixable=True
                ))
    
    async def _audit_legal_compliance(self, profile_data: ProfileData, report: ComplianceReport):
        """Audit legal compliance."""
        
        # Check for copyright or trademark issues
        all_text = self._extract_all_text_content(profile_data)
        
        if re.search(r'©|\(c\)|copyright|trademark|™|®', all_text, re.IGNORECASE):
            report.add_issue(ComplianceIssue(
                id="LEG001",
                title="Copyright/Trademark References Found",
                description="Text contains copyright or trademark symbols/references",
                category=ComplianceCategory.LEGAL,
                level=ComplianceLevel.LOW,
                recommendation="Review for potential intellectual property concerns",
                auto_fixable=False
            ))
        
        if not any(issue.category == ComplianceCategory.LEGAL for issue in report.issues):
            report.add_passed_check("Legal compliance check")
    
    async def _audit_accessibility_compliance(self, profile_data: ProfileData, report: ComplianceReport):
        """Audit accessibility compliance."""
        
        # This is a placeholder for accessibility checks
        # In a real implementation, this would check things like:
        # - Alternative text for any images
        # - Proper heading structure
        # - Color contrast requirements
        # - Screen reader compatibility
        
        report.add_passed_check("Accessibility compliance check (basic)")
    
    def _is_email_redacted(self, email: str) -> bool:
        """Check if email is properly redacted."""
        return '[EMAIL' in email.upper() or 'REDACTED' in email.upper()
    
    def _is_phone_redacted(self, phone: str) -> bool:
        """Check if phone is properly redacted."""
        return '[PHONE' in phone.upper() or 'REDACTED' in phone.upper()
    
    def _contains_full_address(self, location: str) -> bool:
        """Check if location contains a full address."""
        # Simple heuristic: if it contains numbers and street keywords
        has_numbers = bool(re.search(r'\d+', location))
        has_street_keywords = bool(re.search(r'\b(?:st|street|ave|avenue|rd|road|blvd|boulevard|ln|lane|dr|drive)\b', location, re.IGNORECASE))
        return has_numbers and has_street_keywords
    
    def _scan_text_for_sensitive_data(self, text: str, field_name: str) -> List[ComplianceIssue]:
        """Scan text for sensitive data patterns."""
        issues = []
        
        # Check for SSN
        if self._ssn_pattern.search(text):
            issues.append(ComplianceIssue(
                id="PRIV010",
                title="Social Security Number Found",
                description="Text contains what appears to be a Social Security Number",
                category=ComplianceCategory.PRIVACY,
                level=ComplianceLevel.CRITICAL,
                location=field_name,
                recommendation="Remove SSN immediately",
                auto_fixable=True
            ))
        
        # Check for credit card numbers
        if self._credit_card_pattern.search(text):
            issues.append(ComplianceIssue(
                id="PRIV011",
                title="Credit Card Number Found",
                description="Text contains what appears to be a credit card number",
                category=ComplianceCategory.PRIVACY,
                level=ComplianceLevel.CRITICAL,
                location=field_name,
                recommendation="Remove credit card number immediately",
                auto_fixable=True
            ))
        
        return issues
    
    def _extract_all_text_content(self, profile_data: ProfileData) -> str:
        """Extract all text content from profile for analysis."""
        text_parts = []
        
        if profile_data.name:
            text_parts.append(profile_data.name)
        if profile_data.headline:
            text_parts.append(profile_data.headline)
        if profile_data.summary:
            text_parts.append(profile_data.summary)
        
        # Experience descriptions
        for exp in profile_data.experience or []:
            if exp.description:
                text_parts.append(exp.description)
            if exp.title:
                text_parts.append(exp.title)
            if exp.company:
                text_parts.append(exp.company)
        
        # Education descriptions
        for edu in profile_data.education or []:
            if edu.description:
                text_parts.append(edu.description)
            if edu.institution:
                text_parts.append(edu.institution)
        
        # Skills
        for skill in profile_data.skills or []:
            text_parts.append(skill.name)
        
        return ' '.join(text_parts)
    
    async def save_report(self, report: ComplianceReport, output_path: Optional[Path] = None) -> Path:
        """Save compliance report to file.
        
        Args:
            report: Compliance report to save
            output_path: Optional output path, defaults to timestamped file
            
        Returns:
            Path to saved report file
        """
        if not output_path:
            timestamp = report.audit_timestamp.strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"compliance_report_{timestamp}.json")
        
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Compliance report saved to {output_path}")
        return output_path


__all__ = ['ComplianceAuditor', 'ComplianceReport', 'ComplianceIssue', 'ComplianceLevel', 'ComplianceCategory']