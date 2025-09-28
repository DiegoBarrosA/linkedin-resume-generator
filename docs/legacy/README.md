# LinkedIn Resume Generator

An automated system that scrapes **your own** LinkedIn profile and generates a professional resume hosted on GitHub Pages.

## ⚠️ **CRITICAL LEGAL COMPLIANCE**

### 🚨 **LinkedIn Terms of Service Compliance**

**THIS TOOL IS FOR YOUR OWN PROFILE ONLY**

- **✅ ALLOWED**: Scraping YOUR OWN LinkedIn profile for personal resume generation
- **❌ PROHIBITED**: Storing raw scraped LinkedIn data long-term
- **❌ PROHIBITED**: Redistributing or sharing scraped LinkedIn content
- **❌ PROHIBITED**: Using this tool on other people's profiles

### 🔒 **Built-in Privacy Safeguards**

This tool includes automatic compliance features:
- **Automatic Data Cleanup**: Raw LinkedIn data is processed and immediately deleted
- **Privacy-Safe Processing**: Only final resume output is retained
- **User Confirmation**: Requires explicit confirmation for own-profile use
- **Compliance Logging**: All operations include ToS compliance markers

### 📋 **Legal Requirements**

- **Personal Use Only**: Use exclusively with your own LinkedIn account
- **No Data Retention**: Raw scraped data is automatically cleaned up
- **No Redistribution**: Generated resumes are for your personal use only
- **Compliance Monitoring**: LinkedIn actively monitors and litigates scraping violations

### ⚖️ **Legal Disclaimer**

**IMPORTANT**: LinkedIn's Terms of Service expressly forbid storing scraped profile content or redistributing it. LinkedIn has been actively litigating against scraping practices. This tool is designed with compliance safeguards, but users are solely responsible for ensuring their usage complies with LinkedIn's Terms of Service and all applicable laws.

**USE AT YOUR OWN RISK**: This tool is provided for educational purposes. Users assume full legal responsibility for compliance with LinkedIn's Terms of Service.

## 🚀 Features

- **Personal Profile Scraping**: Automatically extracts ALL skills and data from your own LinkedIn profile
- **Zero Configuration**: No hardcoded skills or manual data entry required
- **Intelligent Categorization**: Automatically organizes skills by technology domains
- **TOTP Authentication Support**: Handles LinkedIn 2FA with TOTP codes
- **Comprehensive Data Extraction**: Skills, experience, education, certifications, projects, and more
- **Professional Resume Generation**: Creates beautifully formatted markdown resumes
- **GitHub Pages Hosting**: Automatically deploys your resume to a public webpage
- **Weekly Auto-Updates**: GitHub Actions runs weekly to keep your resume current
- **Personal Use Tool**: Clone, configure your own credentials, and generate your personal resume

## ✨ Why This is Better

### 🎯 **Personalized for You**
- **No Hardcoding**: Automatically extracts ALL skills from your actual LinkedIn profile
- **Works for Your Profile**: Handles your LinkedIn profile with any skill set or industry
- **Adaptive**: Handles different LinkedIn layouts and profile structures
- **Smart Categorization**: Automatically organizes skills into relevant categories
- **Complete Extraction**: Gets skills, endorsements, experience, education, certifications, projects, and more

### 🔧 **Easy to Use**
1. **Clone** this repository
2. **Set** your LinkedIn credentials in GitHub Secrets  
3. **Run** - that's it! No code changes needed

## 📋 Prerequisites

- GitHub account
- LinkedIn account with email/password login
- Basic knowledge of GitHub repositories and settings

## 🔧 Setup Instructions

### 1. Repository Setup

1. **Fork or clone** this repository to your GitHub account
2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Set Source to "Deploy from a branch"
   - Select branch: `main` and folder: `/ (root)`
   - Save the settings

### 2. Configure GitHub Secrets

Add the following secrets in your repository settings (Settings → Secrets and variables → Actions):

#### Required Secrets:
- `LINKEDIN_EMAIL`: Your LinkedIn login email
- `LINKEDIN_PASSWORD`: Your LinkedIn login password

#### Optional Secrets:
- `LINKEDIN_TOTP_SECRET`: Your TOTP secret key (if you use 2FA)

#### How to add secrets:
1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the exact name shown above

### 3. TOTP Setup (If using 2FA)

If your LinkedIn account uses 2FA with an authenticator app:

1. **Get your TOTP secret**:
   - Go to LinkedIn Security settings
   - When setting up 2FA, LinkedIn will show a QR code
   - Look for the manual entry option to get the secret key
   - Or scan the QR code with a TOTP app and export the secret

2. **Add the secret**:
   - Add the secret key as `LINKEDIN_TOTP_SECRET` in GitHub Secrets
   - The secret should be a base32-encoded string (usually 16-32 characters)

### 4. Test the Workflow

1. **Manual run**:
   - Go to Actions tab in your repository
   - Select "Update LinkedIn Resume" workflow
   - Click "Run workflow" → "Run workflow"

2. **Check the results**:
   - Monitor the workflow execution
   - Check if files are generated and committed
   - Visit your GitHub Pages URL (usually `https://yourusername.github.io/repository-name`)

## 📁 Project Structure

```
├── .github/workflows/
│   └── scrape-linkedin.yml    # GitHub Actions workflow
├── scrape_linkedin.py         # LinkedIn scraping script
├── generate_markdown.py       # Markdown resume generator
├── requirements.txt          # Python dependencies
├── _config.yml              # GitHub Pages configuration
├── index.md                 # GitHub Pages homepage
└── README.md               # This file
```

## 🔄 How It Works

1. **Scheduled Execution**: GitHub Actions runs every Sunday at 6 AM UTC
2. **LinkedIn Scraping**: The workflow logs into LinkedIn and scrapes profile data
3. **Data Processing**: Profile data is cleaned and structured
4. **Resume Generation**: Markdown resume is generated from the structured data
5. **Deployment**: Files are committed to the repository and GitHub Pages auto-deploys

## 📝 Generated Files

The workflow generates these files:

- `linkedin_data.json`: Raw scraped profile data
- `resume.md`: Formatted markdown resume
- `index.md`: GitHub Pages homepage with the resume

## ⚙️ Customization

### Resume Template

Edit the template in `generate_markdown.py` to customize:
- Resume sections and order
- Formatting and styling
- Additional data fields

### Scraping Frequency

Modify the cron schedule in `.github/workflows/scrape-linkedin.yml`:
```yaml
schedule:
  - cron: '0 6 * * 0'  # Sunday at 6 AM UTC
```

### GitHub Pages Theme

Change the theme in `_config.yml`:
```yaml
theme: minima  # or jekyll-theme-minimal, etc.
```

## 🚨 Legal and Ethical Considerations

### LinkedIn Terms of Service

- **Review LinkedIn's ToS**: Ensure your usage complies with LinkedIn's Terms of Service
- **Rate Limiting**: The script includes delays to avoid aggressive scraping
- **Personal Use**: This tool is designed for scraping your own profile data
- **Respect robots.txt**: LinkedIn's robots.txt should be considered

### Privacy and Security

- **Secure Credentials**: Always use GitHub Secrets for sensitive information
- **2FA Recommended**: Enable 2FA on both GitHub and LinkedIn accounts
- **Regular Updates**: Keep dependencies updated for security patches

### Disclaimer

This tool is provided as-is for educational and personal use. Users are responsible for ensuring compliance with all applicable terms of service and laws.

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Verify GitHub Secrets are set correctly
   - Check if LinkedIn requires additional verification
   - Try running the workflow manually for debugging

2. **Scraping Errors**:
   - LinkedIn may have changed their HTML structure
   - Check workflow logs for specific error messages
   - Update selectors in `scrape_linkedin.py` if needed

3. **GitHub Pages Not Updating**:
   - Ensure GitHub Pages is enabled
   - Check that files are being committed
   - Verify the `index.md` file is generated

4. **TOTP Issues**:
   - Verify the TOTP secret is correct
   - Check that the time on GitHub Actions matches your TOTP app
   - Try regenerating TOTP secret in LinkedIn

### Debugging

Enable debug mode by setting `headless=False` in `scrape_linkedin.py`:
```python
browser = await p.chromium.launch(headless=False)
```

## 📞 Support

If you encounter issues:

1. Check the GitHub Actions logs for detailed error messages
2. Review LinkedIn's current HTML structure if selectors fail
3. Verify all secrets are configured correctly
4. Consider opening an issue in the repository

## 📄 License

This project is available under the MIT License. See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🔄 Version History

- **v1.0.0**: Initial release with basic LinkedIn scraping and GitHub Pages deployment
- Added TOTP authentication support
- Added comprehensive error handling and logging

---

**Note**: This tool scrapes your own LinkedIn profile data. Ensure you comply with LinkedIn's Terms of Service and use responsibly.