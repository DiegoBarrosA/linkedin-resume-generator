# GitHub Actions CLI Troubleshooting

## Issue: CLI Command Failing in GitHub Actions

If you see this error in GitHub Actions:

```
New CLI not available. Use 'python main.py' for legacy interface.
```

This means the CLI dependencies are not installed in the GitHub Actions environment.

## Solutions

### Option 1: Install Dependencies First (Recommended)

Update your GitHub Actions workflow to install dependencies before running the CLI:

```yaml
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Run LinkedIn Resume Generator
  run: python main.py scrape --format both
```

### Option 2: Use the CLI Runner Script

Use the provided `run_cli.py` script which handles dependency installation automatically:

```yaml
- name: Run LinkedIn Resume Generator
  run: python run_cli.py scrape --format both
```

### Option 3: Install Package and Use Entry Point

Install the package and use the entry point:

```yaml
- name: Install package
  run: pip install .

- name: Run LinkedIn Resume Generator  
  run: linkedin-resume-generator scrape --format both
```

### Option 4: Direct Module Execution

Run the CLI module directly:

```yaml
- name: Install dependencies
  run: pip install click rich

- name: Run LinkedIn Resume Generator
  run: python -m linkedin_resume_generator.cli.main scrape --format both
```

## Environment Variables

Ensure these environment variables are set in your GitHub Actions secrets:

- `LINKEDIN_EMAIL`: Your LinkedIn login email
- `LINKEDIN_PASSWORD`: Your LinkedIn password  
- `LINKEDIN_TOTP_SECRET`: Your TOTP secret (if using 2FA)
- `LINKEDIN_CI_MODE=true`: Bypass interactive prompts

## CLI Usage

The CLI supports these commands:

```bash
# Scrape and generate resume
python main.py scrape --format both

# Generate from existing data
python main.py generate --template custom

# Validate configuration
python main.py validate

# Cleanup temporary files
python main.py cleanup

# Run compliance audit
python main.py audit
```

## Troubleshooting

1. **Import errors**: Install dependencies with `pip install -r requirements.txt`
2. **Permission errors**: Ensure GitHub Actions has write permissions
3. **Authentication errors**: Verify LinkedIn credentials in secrets
4. **Path errors**: Use absolute paths or ensure working directory is correct