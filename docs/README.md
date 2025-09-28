# LinkedIn Resume Generator Documentation

Welcome to the LinkedIn Resume Generator documentation! This tool helps you create professional resumes from LinkedIn profile data with privacy compliance and modern best practices.

## 📚 Documentation Structure

### Getting Started
- [Installation & Setup](setup.md)
- [Quick Start Guide](quickstart.md)
- [Configuration](configuration.md)

### User Guides  
- [CLI Usage](cli-usage.md)
- [Privacy & Compliance](privacy.md)
- [Templates & Customization](templates.md)

### Developer Documentation
- [API Reference](api/)
- [Architecture Overview](architecture.md)
- [Contributing Guide](contributing.md)
- [Testing Guide](testing.md)

### Examples & Demos
- [Sample Resume Output](resume.md)
- [Configuration Examples](examples/)

### Legacy Documentation
- [Previous Version Docs](legacy/)

## 🚀 Quick Links

- **Main Repository**: [GitHub](https://github.com/DiegoBarrosA/diego-barros-resume-generator)
- **Issues & Support**: [GitHub Issues](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues)
- **Latest Release**: Check [Releases](https://github.com/DiegoBarrosA/diego-barros-resume-generator/releases)

## 📋 Features Overview

### ✅ Core Features
- **Automated LinkedIn Scraping** - Extract profile data safely and efficiently
- **Multiple Output Formats** - Markdown, HTML, JSON with extensible template system
- **Privacy Compliance** - Built-in privacy processing and compliance auditing
- **Professional CLI** - Rich command-line interface with comprehensive options
- **Type Safety** - Full Pydantic v2 validation and type checking
- **Async Architecture** - Modern async/await patterns for better performance

### 🔒 Privacy & Security
- **Data Redaction** - Automatic removal of sensitive information
- **Compliance Auditing** - Built-in compliance checks for various regulations
- **Configurable Retention** - Automatic cleanup with configurable data retention
- **Safe Processing** - Privacy-first design with secure defaults

### 🛠️ Developer Experience
- **Modern Python** - Python 3.9+ with full type hints
- **Modular Architecture** - Clean separation of concerns with plugin support
- **Comprehensive Testing** - Full test suite with fixtures and mocking
- **CI/CD Ready** - GitHub Actions integration and pre-commit hooks
- **Extensible Design** - Easy to add new generators, processors, and scrapers

## 🏗️ Architecture

The application follows a clean, modular architecture:

```
src/linkedin_resume_generator/
├── config/         # Configuration management
├── models/         # Data models and validation
├── scrapers/       # LinkedIn scraping components
├── processors/     # Privacy and compliance processing  
├── generators/     # Resume generation
├── utils/          # Shared utilities
└── cli/           # Command-line interface
```

## 📞 Support

- **Documentation Issues**: [File an issue](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues/new?labels=documentation)
- **Feature Requests**: [Request a feature](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues/new?labels=enhancement)
- **Bug Reports**: [Report a bug](https://github.com/DiegoBarrosA/diego-barros-resume-generator/issues/new?labels=bug)

---

*Last updated: September 2025*