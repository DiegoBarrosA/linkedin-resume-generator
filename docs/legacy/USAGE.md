# LinkedIn Resume Generator - Usage Guide

## System Overview

This project automatically generates professional resumes by scraping LinkedIn profiles and converting them to markdown format. It includes comprehensive compliance safeguards to respect LinkedIn's Terms of Service.

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd diego-barros-resume-generator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see Configuration section)
```

### 2. Configuration

Create a `.env` file with:

```env
# LinkedIn Credentials
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
TOTP_SECRET=your-2fa-secret

# GitHub Configuration (for automated workflow)
GITHUB_TOKEN=your-github-token

# Test Configuration
LINKEDIN_CI_MODE=false  # Set to true for non-interactive execution
```

### 3. Manual Usage

```bash
# Run the scraper manually
python3 scrape_linkedin.py

# Check compliance status
python3 compliance_auditor.py

# Process with privacy safeguards
python3 privacy_safe_processor.py
```

## Features

### ✅ Universal Skill Extraction
- **Dynamic Detection**: Automatically extracts skills without hardcoding
- **Multiple Sources**: Skills from experience descriptions, headlines, and skill sections
- **Smart Categorization**: Groups skills by type (Technical, Professional, etc.)
- **Fallback Methods**: Multiple extraction strategies for reliability

### ✅ LinkedIn ToS Compliance
- **Privacy-Safe Processing**: Automatic cleanup of raw LinkedIn data
- **Compliance Auditing**: Automated checks for ToS violations
- **Git Protection**: Enhanced `.gitignore` to prevent accidental commits
- **Warning System**: Clear notifications about compliance requirements

### ✅ GitHub Actions Integration
- **Automated Workflow**: Scheduled resume updates via GitHub Actions
- **CI Mode**: Non-interactive execution for automation
- **Error Handling**: Trap-based cleanup and proper error reporting
- **Artifact Management**: Safe handling of generated files

### ✅ Professional Output
- **Markdown Generation**: Clean, professional resume format
- **GitHub Pages Ready**: Automatic deployment to GitHub Pages
- **Customizable Templates**: Easy modification of output format

## Automation Setup

### GitHub Actions Workflow

The project includes a GitHub Actions workflow that:

1. **Securely runs** the LinkedIn scraper using encrypted secrets
2. **Processes data** with privacy safeguards automatically
3. **Generates** updated resume in markdown format
4. **Deploys** to GitHub Pages automatically
5. **Cleans up** all temporary files and raw data
6. **Audits compliance** and reports any issues

### Required Secrets

Configure these in your GitHub repository settings:

```
LINKEDIN_EMAIL          # Your LinkedIn login email
LINKEDIN_PASSWORD       # Your LinkedIn password  
TOTP_SECRET            # Your 2FA TOTP secret
GITHUB_TOKEN           # GitHub token for Pages deployment
```

## Compliance Guidelines

### ⚠️ Important Notice

This tool is designed to help you create resumes from your own LinkedIn profile. Please:

1. **Only use on your own profile** - Never scrape other users' profiles
2. **Respect rate limits** - Don't run excessively frequently
3. **Review LinkedIn ToS** - Ensure your usage complies with current terms
4. **Monitor for changes** - LinkedIn may update their terms or structure

### Compliance Features

- **Automatic cleanup** of raw LinkedIn data
- **Privacy-safe processing** that removes sensitive information
- **Compliance auditing** that checks for ToS violations
- **Git protection** that prevents accidental data commits

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Test specific components
pytest test_safe_units.py  # Safe unit tests (always run)
pytest test_universal_scraper.py  # Integration tests (gated by env var)
```

### Test Gating

Integration tests that interact with LinkedIn are gated by environment variables:

```bash
# Enable live testing (use carefully)
export ENABLE_LINKEDIN_TESTING=true
pytest test_universal_scraper.py
```

## File Structure

```
diego-barros-resume-generator/
├── scrape_linkedin.py          # Main scraper with universal skill extraction
├── enhance_skills.py           # Skill categorization and processing
├── generate_markdown.py        # Resume markdown generation
├── privacy_safe_processor.py   # Compliance-safe data processing
├── compliance_auditor.py       # Automated compliance checking
├── .github/workflows/          # GitHub Actions automation
├── tests/                      # Test suite
├── COMPLIANCE.md              # Compliance documentation
├── USAGE.md                   # This usage guide
└── README.md                  # Project overview
```

## Troubleshooting

### Common Issues

1. **2FA Problems**: Ensure your TOTP secret is correct and properly formatted
2. **Skill Extraction Issues**: The system uses multiple fallback methods
3. **Compliance Warnings**: Review the compliance audit output for guidance
4. **GitHub Actions Failures**: Check secrets configuration and logs

### Debug Mode

Enable verbose logging by setting:

```bash
export LINKEDIN_DEBUG=true
python3 scrape_linkedin.py
```

### CI Mode

For automated/non-interactive execution:

```bash
export LINKEDIN_CI_MODE=true
python3 scrape_linkedin.py
```

## Support

- Review the compliance documentation in `COMPLIANCE.md`
- Check the automated compliance audit output
- Ensure all environment variables are properly configured
- Verify GitHub secrets are correctly set up

## Version History

- **v1.0**: Initial implementation with basic scraping
- **v1.1**: Added universal skill extraction
- **v1.2**: Implemented comprehensive compliance framework  
- **v1.3**: Enhanced GitHub Actions integration with CI mode
- **v1.4**: Added trap-based cleanup and improved error handling

---

**Remember**: This tool is for creating resumes from your own LinkedIn profile. Always respect LinkedIn's Terms of Service and use responsibly.
</content>