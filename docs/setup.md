# Installation & Setup

This guide will help you get the LinkedIn Resume Generator up and running on your system.

## Prerequisites

- **Python 3.9+** - Check with `python --version`
- **Git** - For cloning the repository
- **LinkedIn Account** - For profile scraping

## Installation Methods

### Method 1: Clone and Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/DiegoBarrosA/diego-barros-resume-generator.git
cd diego-barros-resume-generator

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Development Installation

```bash
# Clone and install in development mode
git clone https://github.com/DiegoBarrosA/diego-barros-resume-generator.git
cd diego-barros-resume-generator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,test]"
```

## Configuration

### 1. Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Required: LinkedIn Credentials
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_secure_password

# Optional: Two-Factor Authentication
LINKEDIN_TOTP_SECRET=your_totp_secret_key

# Optional: GitHub Integration  
GITHUB_TOKEN=your_github_personal_access_token

# Optional: Environment Configuration
ENVIRONMENT=development
DEBUG=true
```

### 2. Verify Installation

Test your installation:

```bash
# Check if the CLI works
python main.py --help

# Validate your configuration
python main.py validate
```

## Dependencies

### Core Dependencies
- `pydantic>=2.11.9` - Data validation and settings
- `click>=8.1.8` - Command-line interface
- `rich>=14.1.0` - Rich terminal output
- `playwright>=1.40.0` - Web scraping
- `structlog>=25.4.0` - Structured logging

### Development Dependencies
- `pytest>=7.4.0` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking
- `pre-commit` - Git hooks

## Troubleshooting

### Common Issues

**1. Python Version Error**
```
Error: Python 3.9+ required
```
**Solution**: Install Python 3.9 or later from [python.org](https://python.org)

**2. Playwright Installation**
```
Error: Playwright browsers not found
```
**Solution**: Install Playwright browsers:
```bash
playwright install chromium
```

**3. Permission Errors**
```
Error: Permission denied
```
**Solution**: Use virtual environment and check file permissions

**4. LinkedIn Authentication Issues**
```
Error: Invalid credentials
```
**Solution**: 
- Verify credentials in `.env` file
- Check if 2FA is enabled and configure TOTP secret
- Ensure account is not locked

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search [existing issues](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues)
3. Create a [new issue](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues/new)

## Next Steps

Once installed, continue with the [Quick Start Guide](quickstart.md) to generate your first resume!