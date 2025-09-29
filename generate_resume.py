#!/usr/bin/env python3
"""Generate resume files (MD and PDF) from sample data."""

import asyncio
from pathlib import Path
from datetime import datetime
from src.linkedin_resume_generator.generators.resume_generator import ResumeGenerator
from src.linkedin_resume_generator.models.profile import (
    ProfileData, ContactInfo, Experience, Education, Skill, Certification
)

def create_sample_profile() -> ProfileData:
    """Create sample profile data for Diego Barros."""
    
    contact = ContactInfo(
        email="contact@diegobarrosaraya.com",
        location="Santiago, Santiago Metropolitan Region, Chile",
        linkedin_url="https://www.linkedin.com/in/diegobarrosaraya"
    )
    
    experience = [
        Experience(
            title="Senior IT Engineer & Technical Consultant",
            company="Freelance",
            location="Chile",
            start_date="2020",
            end_date="Present",
            description="With a strong foundation in computer science and over a decade of experience as a Linux user, I focus on implementing scalable, automated solutions in cloud-native environments (Docker, OCI) and embedded systems. My expertise also includes Atlassian products, and I have a proven track record of executing technical projects and collaborating with global technology teams to deliver efficient, high-performance IT solutions.",
            skills=["Docker", "Linux", "Atlassian", "Python", "DevOps", "Cloud Computing"]
        )
    ]
    
    skills = [
        Skill(name="Docker"),
        Skill(name="Linux"),
        Skill(name="Python"),
        Skill(name="Git"),
        Skill(name="Atlassian"),
        Skill(name="Jira"),
        Skill(name="Confluence"),
        Skill(name="AWS"),
        Skill(name="Kubernetes"),
        Skill(name="CI/CD"),
        Skill(name="Node.js"),
        Skill(name="React"),
        Skill(name="DevOps"),
        Skill(name="Open Source")
    ]
    
    certifications = [
        Certification(
            name="Atlassian Certified Professional - Enterprise (ACP-EE)",
            issuing_organization="Atlassian",
            issue_date="2024"
        ),
        Certification(
            name="ITIL v4 Foundation",
            issuing_organization="AXELOS",
            issue_date="2024"
        )
    ]
    
    return ProfileData(
        name="Diego Pablo Barros Araya",
        headline="Senior IT Engineer & Technical Consultant | Atlassian Certified Expert (ACP-EE) | ITIL v4 | Python | Docker | Git | Open-Source Advocate",
        summary="With a strong foundation in computer science and over a decade of experience as a Linux user, I focus on implementing scalable, automated solutions in cloud-native environments (Docker, OCI) and embedded systems. My expertise also includes Atlassian products, and I have a proven track record of executing technical projects and collaborating with global technology teams to deliver efficient, high-performance IT solutions. As a Senior Engineer, I bring a track record of leading technical teams, driving project execution, and managing stakeholders in high-impact environments. My consulting experience has allowed me to collaborate with global technology leaders, helping them streamline workflows, enhance productivity, and achieve strategic IT goals. Beyond my professional work, I'm an avid explorer of both legacy Unix systems and cutting-edge Linux distributions, driven by a passion for open-source technology and continuous learning.",
        contact_info=contact,
        experience=experience,
        skills=skills,
        certifications=certifications
    )

async def generate_resume_files():
    """Generate both MD and PDF resume files."""
    
    # Create output directory in docs
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Initialize generator with docs directory
    generator = ResumeGenerator(output_dir=docs_dir)
    
    # Create sample profile
    profile = create_sample_profile()
    
    # Generate markdown resume
    md_path = await generator.generate_resume(profile, "markdown")
    
    # Rename to standard filename
    final_md_path = docs_dir / "resume.md"
    if md_path.exists():
        if final_md_path.exists():
            final_md_path.unlink()
        md_path.rename(final_md_path)
        print(f"✅ Generated Markdown resume: {final_md_path}")
    
    # Generate PDF resume
    try:
        pdf_path = await generator.generate_resume(profile, "pdf")
        
        # Rename to standard filename
        final_pdf_path = docs_dir / "resume.pdf"
        if pdf_path.exists():
            if final_pdf_path.exists():
                final_pdf_path.unlink()
            pdf_path.rename(final_pdf_path)
            print(f"✅ Generated PDF resume: {final_pdf_path}")
    except ImportError as e:
        print(f"⚠️  PDF generation skipped: {e}")
        print("   Install reportlab with: pip install reportlab")

if __name__ == "__main__":
    asyncio.run(generate_resume_files())