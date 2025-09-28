# Quick Start Guide

Get your first resume generated in just a few minutes!

## 🚀 Quick Start

### Step 1: Basic Setup

Ensure you have completed the [installation](setup.md) and have your LinkedIn credentials configured in `.env`:

```bash
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
```

### Step 2: Generate Your Resume

The simplest way to generate a resume:

```bash
# Scrape your LinkedIn profile and generate a resume
python main.py scrape --email your.email@example.com
```

This will:
1. 🔍 Scrape your LinkedIn profile data
2. 🛡️ Process it for privacy compliance  
3. 📄 Generate a professional Markdown resume
4. 🗂️ Save output to `./output/` directory

### Step 3: View Your Resume

Check the generated files:
```bash
ls output/
# resume_YYYYMMDD_HHMMSS.md
# profile_data_YYYYMMDD_HHMMSS.json (if enabled)
```

## 📋 Command Examples

### Basic Scraping
```bash
# Scrape and generate with default settings
python main.py scrape --email your.email@example.com

# Scrape with custom output directory
python main.py scrape --email your.email@example.com --output ./my_resumes/

# Scrape with specific format
python main.py scrape --email your.email@example.com --format html
```

### Generate from Existing Data
```bash
# Generate from previously scraped data
python main.py generate profile_data.json

# Generate with custom template
python main.py generate profile_data.json --output custom_resume.md
```

### Privacy & Compliance
```bash
# Run compliance audit
python main.py audit

# Clean up old data files
python main.py cleanup --older-than 24h
```

### Configuration Management
```bash
# Validate your configuration
python main.py validate

# Run with debug logging
python main.py --debug scrape --email your.email@example.com
```

## 🎯 Output Formats

### Markdown (Default)
```bash
python main.py scrape --email your.email@example.com --format markdown
```
- Clean, readable format
- GitHub-compatible
- Easy to edit and version control

### HTML
```bash
python main.py scrape --email your.email@example.com --format html
```
- Web-ready format
- Styled output
- Easy to share and print

### JSON
```bash
python main.py scrape --email your.email@example.com --format json
```
- Structured data format
- API integration ready
- Custom processing friendly

## ⚙️ Configuration Options

### Environment Variables
```bash
# Set output preferences
OUTPUT_FORMAT=markdown
OUTPUT_DIR=./resumes
CREATE_GITHUB_PAGES=true

# Privacy settings
PRIVACY_MODE=true
AUTO_CLEANUP=true
DATA_RETENTION_HOURS=0

# Scraping behavior
SCRAPING_TIMEOUT=30
SCRAPING_HEADLESS=true
```

### Configuration File
Create `config.yaml` for persistent settings:
```yaml
linkedin:
  email: your.email@example.com
  
output:
  format: markdown
  directory: ./resumes
  
privacy:
  mode: true
  auto_cleanup: true
  data_retention_hours: 0

scraping:
  timeout: 30
  headless: true
```

Use with:
```bash
python main.py --config-file config.yaml scrape
```

## 🛡️ Privacy Best Practices

The tool includes built-in privacy features:

### Default Privacy Processing
- ✅ Email addresses redacted
- ✅ Phone numbers redacted  
- ✅ Full addresses anonymized
- ✅ Sensitive keywords filtered
- ✅ Automatic data cleanup

### Manual Privacy Control
```bash
# Generate with maximum privacy
python main.py scrape --email your.email@example.com --privacy-mode strict

# Keep raw data for analysis (not recommended)
python main.py scrape --email your.email@example.com --keep-raw-data
```

## 🔍 Verification Steps

After your first run, verify everything works:

1. **Check Output Files**
   ```bash
   ls -la output/
   ```

2. **Validate Generated Resume**
   - Open the `.md` file in any text editor
   - Check that personal information is appropriately handled
   - Verify all sections are populated correctly

3. **Run Compliance Audit**
   ```bash
   python main.py audit
   ```

## 🚨 Common Issues

### Issue: "No profile data found"
**Solution**: Verify your LinkedIn profile is public or semi-public

### Issue: "Authentication failed" 
**Solution**: Check credentials and 2FA settings in `.env`

### Issue: "Rate limited"
**Solution**: Wait a few minutes and try again with `--slow-mode`

## 📚 Next Steps

- **Customize Output**: Learn about [templates and customization](templates.md)
- **Privacy Settings**: Review [privacy and compliance](privacy.md) options
- **Advanced Usage**: Explore the complete [CLI reference](cli-usage.md)
- **Integration**: Set up [automated workflows](workflows.md)

## 💡 Pro Tips

1. **Regular Updates**: Update your resume monthly by re-running the scraper
2. **Multiple Formats**: Generate both Markdown and HTML for different use cases  
3. **Privacy First**: Always run compliance audits before sharing
4. **Backup Data**: Keep profile JSON files for quick regeneration
5. **Custom Templates**: Create templates for different job applications

---

🎉 **Congratulations!** You've generated your first professional resume from LinkedIn data. The tool handles privacy, compliance, and formatting automatically so you can focus on your career growth!