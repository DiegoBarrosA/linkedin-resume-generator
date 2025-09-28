# LinkedIn Resume Generator v2.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **⚠️ COMPLIANCE NOTICE:** This tool is designed for personal use only. It scrapes LinkedIn data exclusively from your own profile for resume generation. Raw scraped data is automatically deleted after processing to comply with LinkedIn's Terms of Service.

## 🚀 What's New in v2.0

- **🏗️ Modular Architecture**: Clean separation of concerns with dedicated modules
- **🔧 Type Safety**: Full Pydantic integration for data validation
- **📋 Rich CLI**: Modern command-line interface with helpful feedback
- **⚡ Async/Await**: Improved performance with async operations  
- **🔒 Enhanced Compliance**: Automated compliance checking and data cleanup
- **🧪 Better Testing**: Comprehensive test suite with proper mocking
- **📖 Configuration Management**: Centralized, validated configuration system
- **🛡️ Error Handling**: Structured exceptions and logging

## 📦 Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/DiegoBarrosA/diego-barros-resume-generator.git
cd diego-barros-resume-generator

# Install dependencies
pip install -r requirements.txt

# Install browser for Playwright
playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your LinkedIn credentials
```

### Development Installation

```bash
# Install in development mode
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 🔧 Configuration

Create a `.env` file with your LinkedIn credentials:

```env
# LinkedIn Authentication
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
LINKEDIN_TOTP_SECRET=your-2fa-secret-key

# Optional Configuration
ENVIRONMENT=production
DEBUG=false
LINKEDIN_CI_MODE=false

# Output Configuration
OUTPUT_DIR=.
RESUME_FILENAME=resume.md
INDEX_FILENAME=index.md

# Compliance Settings
AUTO_CLEANUP=true
PRIVACY_MODE=true
AUDIT_ENABLED=true
```

## 📖 Usage

### Command Line Interface (Recommended)

```bash
# Generate resume with new CLI
python main.py scrape

# Validate configuration
python main.py validate

# Run compliance audit
python main.py audit

# Cleanup temporary files
python main.py cleanup

# Generate from custom template
python main.py generate custom_template.md -o custom_resume.md

# Get help
python main.py --help
```

### Legacy Compatibility

```bash
# Run with legacy interface (backward compatibility)
python run_legacy.py

# Direct module execution (old method still works)
python scrape_linkedin.py  # if available
```

### Programmatic Usage

```python
import asyncio
from linkedin_resume_generator import LinkedInScraper, ResumeGenerator, get_settings

async def generate_resume():
    settings = get_settings()
    
    async with LinkedInScraper(settings) as scraper:
        profile_data = await scraper.scrape_profile()
        
        generator = ResumeGenerator(settings)
        resume_content = generator.generate_markdown(profile_data)
        
        with open("resume.md", "w") as f:
            f.write(resume_content)

# Run the async function
asyncio.run(generate_resume())
```

## 🏗️ Architecture Overview

```
src/linkedin_resume_generator/
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # Pydantic settings with validation
├── models/                # Data models
│   ├── __init__.py
│   └── profile.py         # Pydantic models for profile data
├── scrapers/              # Web scraping components
│   ├── __init__.py
│   ├── authentication.py  # LinkedIn authentication handler
│   ├── skill_extractor.py # Universal skill extraction
│   └── linkedin_scraper.py # Main scraper coordinator
├── processors/            # Data processors
│   ├── __init__.py
│   ├── privacy_processor.py # Privacy-safe data processing
│   └── compliance_auditor.py # ToS compliance checking
├── generators/            # Resume generators
│   ├── __init__.py
│   └── resume_generator.py # Markdown resume generation
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── exceptions.py      # Custom exceptions
│   └── logging.py         # Structured logging
├── cli/                   # Command line interface
│   ├── __init__.py
│   └── main.py           # Click-based CLI
└── __init__.py           # Package initialization
```

## ✨ Key Features

### 🎯 Universal Skill Extraction
- **Dynamic Detection**: No hardcoded skill lists
- **Multiple Sources**: Skills from descriptions, headlines, and sections
- **Smart Categorization**: Automatic skill grouping
- **Confidence Scoring**: Reliability metrics for extracted skills

### 🔐 Compliance & Privacy
- **Automatic Cleanup**: Raw data deleted immediately after processing
- **Compliance Auditing**: Automated ToS violation checking
- **Privacy Mode**: Safe data processing without storing sensitive info
- **Git Protection**: Enhanced `.gitignore` patterns

### 🚀 Modern Development
- **Type Safety**: Full type hints with Pydantic validation
- **Async Operations**: Non-blocking I/O for better performance
- **Structured Logging**: Rich, filterable logs with context
- **Error Handling**: Custom exceptions with detailed context

### 🧪 Testing & Quality
- **Comprehensive Tests**: Unit and integration test suites
- **Environment Gating**: Safe testing without live LinkedIn calls
- **Code Quality**: Black, isort, flake8, mypy integration
- **Pre-commit Hooks**: Automated code quality checks

## 🔄 Migration from v1.x

### Automatic Migration

The system includes backward compatibility:

```bash
# Old usage still works
python scrape_linkedin.py  # Falls back to legacy mode

# New usage (recommended)
python main.py scrape
```

### Configuration Migration

Old `.env` variables are automatically mapped:

```env
# Old (still works)
LINKEDIN_EMAIL=...
LINKEDIN_PASSWORD=...
TOTP_SECRET=...

# New (same variables, enhanced validation)
LINKEDIN_EMAIL=...
LINKEDIN_PASSWORD=...
LINKEDIN_TOTP_SECRET=...
```

### Code Migration

```python
# Old way
from scrape_linkedin import LinkedInScraper
scraper = LinkedInScraper()

# New way
from linkedin_resume_generator import LinkedInScraper, get_settings
settings = get_settings()
async with LinkedInScraper(settings) as scraper:
    # Use scraper
```

## 🤖 GitHub Actions

The workflow automatically adapts to the new architecture:

```yaml
- name: Generate Resume
  run: |
    export LINKEDIN_CI_MODE=true
    
    # Tries new CLI first, falls back to legacy
    if python -c "import src.linkedin_resume_generator" 2>/dev/null; then
      python main.py scrape --format both
    else
      python run_legacy.py
    fi
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests (requires environment setup)
ENABLE_LINKEDIN_TESTING=true pytest tests/integration/

# Run specific test file
pytest tests/unit/test_skill_extractor.py -v
```

## 🛠️ Development

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code  
flake8 src/ tests/
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Project Structure

- **Configuration**: Centralized in `src/linkedin_resume_generator/config/`
- **Models**: Pydantic models in `src/linkedin_resume_generator/models/`  
- **Business Logic**: Scrapers, processors, generators in dedicated modules
- **CLI**: Rich command-line interface in `src/linkedin_resume_generator/cli/`
- **Tests**: Comprehensive test suite in `tests/`

## 📋 CLI Reference

### Commands

- `scrape` - Scrape LinkedIn profile and generate resume
- `validate` - Validate configuration and credentials
- `audit` - Run compliance audit
- `cleanup` - Clean up temporary files
- `generate` - Generate resume from existing data with custom template

### Options

- `--debug` - Enable debug logging
- `--config-file` - Specify config file path
- `--profile-url` - Specific LinkedIn profile URL
- `--output-dir` - Output directory
- `--format` - Output format (markdown/json/both)

## ⚠️ Compliance Guidelines

### Important Notes

1. **Personal Use Only**: Only scrape your own LinkedIn profile
2. **Respect Rate Limits**: Don't run excessively frequently
3. **Data Cleanup**: Raw data is automatically deleted after processing
4. **ToS Compliance**: Regularly review LinkedIn's Terms of Service

### Compliance Features

- **Automated Auditing**: Built-in compliance checking
- **Privacy Processing**: Safe data handling without storing sensitive info
- **Git Protection**: Prevents accidental commits of raw data
- **Cleanup Verification**: Ensures no raw data remains

## 🔧 Troubleshooting

### Common Issues

**Authentication Problems**
```bash
# Validate credentials
python main.py validate

# Check 2FA setup
echo $LINKEDIN_TOTP_SECRET
```

**Module Import Errors**
```bash
# Install in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

**Skill Extraction Issues**
- The system uses multiple fallback methods
- Skills are extracted from headlines, descriptions, and skill sections
- Check debug logs with `--debug` flag

### Debug Mode

```bash
# Enable verbose logging
python main.py --debug scrape

# Check configuration
python main.py --debug validate
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -e .[dev]`
4. Set up pre-commit: `pre-commit install`
5. Make your changes and add tests
6. Run quality checks: `pre-commit run --all-files`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Playwright** for reliable browser automation
- **Pydantic** for robust data validation
- **Click** for the excellent CLI framework
- **Rich** for beautiful terminal output

---

**Remember**: This tool is designed to help you create professional resumes from your own LinkedIn profile. Always respect LinkedIn's Terms of Service and use responsibly.