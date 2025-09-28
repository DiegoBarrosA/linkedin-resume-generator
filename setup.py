"""Setup script for LinkedIn Resume Generator."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements and separate runtime from dev dependencies
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
dev_packages = {
    'pytest', 'pytest-asyncio', 'pytest-mock', 'pytest-cov',
    'black', 'isort', 'flake8', 'mypy', 'pre-commit', 'tox',
    'coverage', 'bandit', 'safety'
}

if requirements_path.exists():
    all_requirements = requirements_path.read_text().strip().split('\n')
    # Filter out comments and empty lines
    all_requirements = [req.strip() for req in all_requirements if req.strip() and not req.startswith('#')]
    
    # Split runtime and dev requirements
    for req in all_requirements:
        # Extract package name (handle version specifiers like ==, >=, etc.)
        package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()
        
        # Only include non-dev packages in runtime requirements
        if package_name.lower() not in dev_packages:
            requirements.append(req)

setup(
    name="linkedin-resume-generator",
    version="2.0.0",
    author="Diego Barros",
    author_email="your-email@example.com",
    description="Professional resume generator from LinkedIn profiles with compliance safeguards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DiegoBarrosA/diego-barros-resume-generator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "linkedin-resume-generator=linkedin_resume_generator.cli.main:cli",
            "lrg=linkedin_resume_generator.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)