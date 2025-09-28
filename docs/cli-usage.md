# CLI Usage Guide

Complete reference for the LinkedIn Resume Generator command-line interface.

## Overview

The CLI provides five main commands:
- `scrape` - Extract LinkedIn profile data and generate resume
- `generate` - Create resume from existing profile data  
- `audit` - Run compliance and privacy audits
- `validate` - Validate configuration and credentials
- `cleanup` - Remove old data files

## Global Options

Available for all commands:

```bash
--debug              Enable debug logging
--config-file PATH   Use custom configuration file
--help              Show help message
```

## Commands Reference

### `scrape` - LinkedIn Profile Scraping

Extract profile data from LinkedIn and generate a resume.

```bash
python main.py scrape [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--email TEXT` | LinkedIn email address | Required |
| `--password TEXT` | LinkedIn password | From config |
| `--output PATH` | Output directory | `./output` |
| `--format CHOICE` | Output format (`markdown`, `html`, `json`) | `markdown` |
| `--template PATH` | Custom template file | Built-in template |
| `--privacy-mode CHOICE` | Privacy level (`strict`, `normal`, `minimal`) | `normal` |
| `--keep-raw-data` | Preserve raw scraped data | False |
| `--headless / --no-headless` | Run browser in headless mode | True |
| `--slow-mode` | Use slower, more reliable scraping | False |
| `--timeout INTEGER` | Page timeout in seconds | 30 |

#### Examples

```bash
# Basic scraping with email prompt
python main.py scrape --email john.doe@example.com

# Custom output directory and format  
python main.py scrape --email john.doe@example.com \
  --output ./my_resumes \
  --format html

# Maximum privacy with slow mode
python main.py scrape --email john.doe@example.com \
  --privacy-mode strict \
  --slow-mode

# Keep raw data for analysis
python main.py scrape --email john.doe@example.com \
  --keep-raw-data \
  --format json

# Custom timeout and visible browser
python main.py scrape --email john.doe@example.com \
  --timeout 60 \
  --no-headless
```

### `generate` - Resume Generation

Generate a resume from existing profile data.

```bash
python main.py generate [OPTIONS] PROFILE_DATA_PATH
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output PATH` | Output file path | Auto-generated |
| `--format CHOICE` | Output format | `markdown` |
| `--template PATH` | Custom template file | Built-in |
| `--privacy-mode CHOICE` | Privacy processing level | `normal` |

#### Examples

```bash
# Generate from JSON profile data
python main.py generate profile_20240101_120000.json

# Custom output file and format
python main.py generate profile.json \
  --output my_resume.html \
  --format html

# Use custom template
python main.py generate profile.json \
  --template ./templates/executive.md \
  --output executive_resume.md

# Maximum privacy processing
python main.py generate profile.json \
  --privacy-mode strict
```

### `audit` - Compliance Auditing

Run privacy and compliance audits on profile data.

```bash
python main.py audit [OPTIONS] [PROFILE_DATA_PATH]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--report-format CHOICE` | Report format (`json`, `text`, `html`) | `text` |
| `--output PATH` | Report output file | Console |
| `--fix-issues` | Automatically fix issues where possible | False |
| `--severity CHOICE` | Minimum severity (`low`, `medium`, `high`, `critical`) | `medium` |

#### Examples

```bash
# Audit most recent profile data
python main.py audit

# Audit specific file with JSON report
python main.py audit profile.json \
  --report-format json \
  --output audit_report.json

# Auto-fix issues where possible
python main.py audit profile.json --fix-issues

# Show only high and critical issues
python main.py audit --severity high
```

### `validate` - Configuration Validation

Validate configuration and test credentials.

```bash
python main.py validate [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--test-login` | Test LinkedIn login credentials | False |
| `--check-deps` | Verify all dependencies | False |
| `--verbose` | Show detailed validation results | False |

#### Examples

```bash
# Basic configuration validation
python main.py validate

# Test login credentials
python main.py validate --test-login

# Full validation with dependency check
python main.py validate --check-deps --verbose
```

### `cleanup` - Data Cleanup

Remove old data files and temporary files.

```bash
python main.py cleanup [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--older-than TEXT` | Remove files older than (e.g., '24h', '7d', '30d') | `24h` |
| `--dry-run` | Show what would be deleted without deleting | False |
| `--include-backups` | Also remove backup files | False |
| `--force` | Skip confirmation prompts | False |

#### Examples

```bash
# Clean up files older than 24 hours
python main.py cleanup

# See what would be cleaned (dry run)
python main.py cleanup --older-than 7d --dry-run

# Force cleanup without prompts
python main.py cleanup --older-than 30d --force

# Include backup files in cleanup
python main.py cleanup --include-backups
```

## Configuration File Usage

### YAML Configuration

Create `config.yaml`:

```yaml
linkedin:
  email: john.doe@example.com
  password: ${LINKEDIN_PASSWORD}
  totp_secret: ${LINKEDIN_TOTP_SECRET}

output:
  directory: ./resumes
  format: markdown
  create_github_pages: true

scraping:
  timeout: 30
  headless: true
  slow_mode: false

privacy:
  mode: normal
  auto_cleanup: true
  data_retention_hours: 0

logging:
  level: INFO
  file_enabled: false
```

Use with any command:
```bash
python main.py --config-file config.yaml scrape
```

### Environment Variables

Set via `.env` file or environment:

```bash
# LinkedIn credentials
LINKEDIN_EMAIL=john.doe@example.com
LINKEDIN_PASSWORD=secure_password
LINKEDIN_TOTP_SECRET=SECRET123

# Output settings  
OUTPUT_DIR=./resumes
OUTPUT_FORMAT=markdown
CREATE_GITHUB_PAGES=true

# Privacy settings
PRIVACY_MODE=normal
AUTO_CLEANUP=true
DATA_RETENTION_HOURS=0

# Scraping settings
SCRAPING_TIMEOUT=30
SCRAPING_HEADLESS=true

# General settings
ENVIRONMENT=production
DEBUG=false
CI_MODE=false
```

## Exit Codes

The CLI returns standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments or configuration |
| `3` | Authentication failure |
| `4` | Network or scraping error |
| `5` | File I/O error |
| `6` | Privacy/compliance violation |

## Advanced Usage

### Scripting and Automation

```bash
#!/bin/bash
# Monthly resume update script

# Set error handling
set -e

# Activate virtual environment
source .venv/bin/activate

# Validate configuration
python main.py validate --test-login

# Generate resume with timestamp
TIMESTAMP=$(date +%Y%m%d)
python main.py scrape --email $LINKEDIN_EMAIL \
  --output "./resumes/monthly" \
  --format markdown

# Run compliance audit
python main.py audit --severity medium \
  --report-format json \
  --output "./reports/audit_$TIMESTAMP.json"

# Cleanup old files
python main.py cleanup --older-than 30d --force

echo "✅ Monthly resume update complete!"
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Resume Generation
on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly

jobs:
  generate-resume:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: pip install -r requirements.txt
        
      - name: Generate resume
        env:
          LINKEDIN_EMAIL: ${{ secrets.LINKEDIN_EMAIL }}
          LINKEDIN_PASSWORD: ${{ secrets.LINKEDIN_PASSWORD }}
        run: |
          python main.py validate
          python main.py scrape --format markdown
          python main.py audit --severity high
          
      - name: Upload resume
        uses: actions/upload-artifact@v3
        with:
          name: resume
          path: output/
```

## Troubleshooting CLI Issues

### Common Problems

**Command not found**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
python main.py --help
```

**Permission errors**
```bash
# Check file permissions
chmod +x main.py
```

**Import errors**
```bash
# Verify installation
pip list | grep pydantic
python -c "import linkedin_resume_generator"
```

**Configuration errors**
```bash
# Validate configuration
python main.py validate --verbose
```

For more troubleshooting help, see the [setup guide](setup.md) or [create an issue](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues).