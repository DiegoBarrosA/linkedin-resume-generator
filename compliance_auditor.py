#!/usr/bin/env python3
"""
LinkedIn ToS Compliance Verification Script

This script verifies that no LinkedIn data is being inappropriately stored
and provides a compliance audit trail.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

class ComplianceAuditor:
    def __init__(self):
        self.compliance_report = {
            'audit_timestamp': datetime.now().isoformat(),
            'violations': [],
            'warnings': [],
            'compliant_files': [],
            'status': 'UNKNOWN'
        }
    
    def check_data_retention_violations(self) -> List[str]:
        """Check for prohibited LinkedIn data files"""
        violations = []
        
        # Files that should NOT exist (LinkedIn ToS violations)
        prohibited_files = [
            'linkedin_data.json',
            'linkedin_data_enhanced.json', 
            'linkedin_raw.json',
            'profile_data.json',
            'scraped_linkedin.json'
        ]
        
        for file_path in prohibited_files:
            if os.path.exists(file_path):
                violations.append(f"VIOLATION: {file_path} contains raw LinkedIn data")
                
        return violations
    
    def check_gitignore_protection(self) -> List[str]:
        """Verify .gitignore blocks LinkedIn data"""
        warnings = []
        
        if not os.path.exists('.gitignore'):
            warnings.append("WARNING: No .gitignore file found")
            return warnings
            
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        protected_patterns = [
            'linkedin_data.json',
            'linkedin_data_enhanced.json'
        ]
        
        for pattern in protected_patterns:
            if pattern not in gitignore_content:
                warnings.append(f"WARNING: {pattern} not in .gitignore")
                
        return warnings
    
    def check_compliant_files(self) -> List[str]:
        """List files that are compliance-safe"""
        compliant = []
        
        safe_files = [
            'resume.md',
            'index.md',
            'README.md',
            'COMPLIANCE.md',
            'privacy_safe_processor.py',
            'requirements.txt',
            '.gitignore'
        ]
        
        for file_path in safe_files:
            if os.path.exists(file_path):
                compliant.append(f"✅ {file_path} - Safe for version control")
                
        return compliant
    
    def verify_workflow_compliance(self) -> List[str]:
        """Check GitHub Actions workflow for compliance"""
        warnings = []
        
        workflow_path = '.github/workflows/scrape-linkedin.yml'
        if not os.path.exists(workflow_path):
            warnings.append("WARNING: No GitHub Actions workflow found")
            return warnings
            
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()
            
        # Check for compliance safeguards
        required_safeguards = [
            'rm -f linkedin_data.json',
            'COMPLIANCE WARNING',
            'ToS compliant'
        ]
        
        for safeguard in required_safeguards:
            if safeguard not in workflow_content:
                warnings.append(f"WARNING: Missing workflow safeguard: {safeguard}")
                
        # Check that artifacts don't include raw data
        if 'linkedin_data.json' in workflow_content and 'path:' in workflow_content:
            # This is complex to parse properly, but flag for manual review
            warnings.append("WARNING: Review workflow artifacts - ensure no raw LinkedIn data")
            
        return warnings
    
    def run_compliance_audit(self) -> Dict[str, Any]:
        """Run complete compliance audit"""
        print("🔍 Running LinkedIn ToS Compliance Audit")
        print("=" * 50)
        
        # Check for violations
        violations = self.check_data_retention_violations()
        self.compliance_report['violations'] = violations
        
        # Check for warnings
        warnings = []
        gitignore_warnings = self.check_gitignore_protection()
        warnings.extend(gitignore_warnings)
        warnings.extend(self.verify_workflow_compliance())
        self.compliance_report['warnings'] = warnings
        
        # Store gitignore protection status (True if no gitignore warnings)
        self.compliance_report['gitignore_check'] = len(gitignore_warnings) == 0
        
        # List compliant files
        compliant = self.check_compliant_files()
        self.compliance_report['compliant_files'] = compliant
        
        # Determine overall status
        if violations:
            self.compliance_report['status'] = 'VIOLATION_DETECTED'
        elif warnings:
            self.compliance_report['status'] = 'WARNINGS_PRESENT'
        else:
            self.compliance_report['status'] = 'COMPLIANT'
            
        return self.compliance_report
    
    def print_audit_report(self, report: Dict[str, Any]):
        """Print human-readable audit report"""
        
        print(f"\n📊 Compliance Audit Report")
        print(f"Timestamp: {report['audit_timestamp']}")
        print(f"Status: {report['status']}")
        print("-" * 50)
        
        if report['violations']:
            print("\n🚨 VIOLATIONS DETECTED:")
            for violation in report['violations']:
                print(f"  {violation}")
            print("\n⚠️  ACTION REQUIRED: Remove prohibited files immediately!")
                
        if report['warnings']:
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  {warning}")
                
        if report['compliant_files']:
            print(f"\n✅ COMPLIANT FILES ({len(report['compliant_files'])}):")
            for file_info in report['compliant_files']:
                print(f"  {file_info}")
                
        print(f"\n📋 COMPLIANCE CHECKLIST:")
        print(f"  {'✅' if not report['violations'] else '❌'} No raw LinkedIn data files")
        print(f"  {'✅' if report.get('gitignore_check', False) else '⚠️ '} .gitignore protection")
        print(f"  {'✅' if report['status'] != 'VIOLATION_DETECTED' else '❌'} Overall compliance")
        
        if report['status'] == 'COMPLIANT':
            print(f"\n🎉 All LinkedIn ToS compliance checks PASSED!")
        elif report['status'] == 'WARNINGS_PRESENT':
            print(f"\n⚠️  Compliance warnings detected - review and address")
        else:
            print(f"\n🚨 COMPLIANCE VIOLATIONS - IMMEDIATE ACTION REQUIRED!")
            
def main():
    """Run compliance audit"""
    auditor = ComplianceAuditor()
    report = auditor.run_compliance_audit()
    auditor.print_audit_report(report)
    
    # Save audit log
    log_file = f"compliance_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Audit log saved to: {log_file}")
    
    return report['status'] == 'COMPLIANT'

if __name__ == "__main__":
    compliant = main()
    exit(0 if compliant else 1)