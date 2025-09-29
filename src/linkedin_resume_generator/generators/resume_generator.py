"""Resume generation functionality."""

from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

from ..models.profile import ProfileData
from ..utils.logging import get_logger


logger = get_logger(__name__)


class ResumeGenerator:
    """Generate resume documents from LinkedIn profile data."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the resume generator.
        
        Args:
            output_dir: Directory to save generated resumes
        """
        self.output_dir = output_dir or Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_resume(
        self,
        profile_data: ProfileData,
        format_type: str = "markdown",
        template: Optional[str] = None,
        **kwargs
    ) -> Path:
        """Generate a resume from profile data.
        
        Args:
            profile_data: Parsed LinkedIn profile data
            format_type: Output format (markdown, html, pdf, json)
            template: Optional template name to use
            **kwargs: Additional generation options
            
        Returns:
            Path to generated resume file
        """
        logger.info(f"Generating {format_type} resume for {profile_data.name}")
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == "json":
            return await self._generate_json(profile_data, timestamp)
        elif format_type.lower() == "markdown":
            return await self._generate_markdown(profile_data, timestamp, template)
        elif format_type.lower() == "html":
            return await self._generate_html(profile_data, timestamp, template)
        elif format_type.lower() == "pdf":
            return await self._generate_pdf(profile_data, timestamp, template)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    async def _generate_json(self, profile_data: ProfileData, timestamp: str) -> Path:
        """Generate JSON resume."""
        filename = f"resume_{timestamp}.json"
        output_path = self.output_dir / filename
        
        # Convert profile data to dictionary
        resume_data = profile_data.model_dump()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Generated JSON resume: {output_path}")
        return output_path
    
    async def _generate_markdown(
        self, 
        profile_data: ProfileData, 
        timestamp: str, 
        template: Optional[str] = None
    ) -> Path:
        """Generate Markdown resume."""
        filename = f"resume_{timestamp}.md"
        output_path = self.output_dir / filename
        
        # Generate basic Markdown template
        content = self._create_markdown_content(profile_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated Markdown resume: {output_path}")
        return output_path
    
    async def _generate_html(
        self,
        profile_data: ProfileData,
        timestamp: str,
        template: Optional[str] = None
    ) -> Path:
        """Generate HTML resume."""
        filename = f"resume_{timestamp}.html"
        output_path = self.output_dir / filename
        
        # For now, convert markdown to basic HTML
        markdown_content = self._create_markdown_content(profile_data)
        html_content = self._markdown_to_html(markdown_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML resume: {output_path}")
        return output_path
    
    def _create_markdown_content(self, profile_data: ProfileData) -> str:
        """Create markdown content from profile data."""
        lines = []
        
        # Header
        lines.append(f"# {profile_data.name}")
        if profile_data.headline:
            lines.append(f"## {profile_data.headline}")
        lines.append("")
        
        # Contact Information
        if profile_data.contact_info:
            lines.append("## Contact Information")
            contact = profile_data.contact_info
            if contact.email:
                lines.append(f"- **Email:** {contact.email}")
            if contact.phone:
                lines.append(f"- **Phone:** {contact.phone}")
            if contact.location:
                lines.append(f"- **Location:** {contact.location}")
            if contact.linkedin_url:
                lines.append(f"- **LinkedIn:** {contact.linkedin_url}")
            if contact.website:
                lines.append(f"- **Website:** {contact.website}")
            lines.append("")
        
        # Summary
        if profile_data.summary:
            lines.append("## Summary")
            lines.append(profile_data.summary)
            lines.append("")
        
        # Experience
        if profile_data.experience:
            lines.append("## Professional Experience")
            for exp in profile_data.experience:
                lines.append(f"### {exp.title} at {exp.company}")
                if exp.location:
                    lines.append(f"*{exp.location}*")
                if exp.start_date or exp.end_date:
                    date_range = f"{exp.start_date or 'Unknown'} - {exp.end_date or 'Present'}"
                    lines.append(f"*{date_range}*")
                if exp.description:
                    lines.append("")
                    lines.append(exp.description)
                if exp.skills:
                    lines.append("")
                    lines.append(f"**Skills:** {', '.join(exp.skills)}")
                lines.append("")
        
        # Skills
        if profile_data.skills:
            lines.append("## Skills")
            if hasattr(profile_data, 'skills_summary') and profile_data.skills_summary:
                # Group by category
                for category, skills in profile_data.skills_summary.by_category.items():
                    if skills:
                        lines.append(f"### {category.value}")
                        skill_names = [skill.name for skill in skills]
                        lines.append(f"{', '.join(skill_names)}")
                        lines.append("")
            else:
                # Simple list
                skill_names = [skill.name for skill in profile_data.skills]
                lines.append(f"{', '.join(skill_names)}")
                lines.append("")
        
        # Education
        if profile_data.education:
            lines.append("## Education")
            for edu in profile_data.education:
                lines.append(f"### {edu.degree} - {edu.field_of_study}")
                lines.append(f"**{edu.institution}**")
                if edu.start_date or edu.end_date:
                    date_range = f"{edu.start_date or 'Unknown'} - {edu.end_date or 'Unknown'}"
                    lines.append(f"*{date_range}*")
                if edu.grade:
                    lines.append(f"**Grade:** {edu.grade}")
                if edu.description:
                    lines.append("")
                    lines.append(edu.description)
                lines.append("")
        
        # Certifications
        if profile_data.certifications:
            lines.append("## Certifications")
            for cert in profile_data.certifications:
                lines.append(f"### {cert.name}")
                lines.append(f"**{cert.issuing_organization}**")
                if cert.issue_date:
                    lines.append(f"*Issued: {cert.issue_date}*")
                if cert.expiration_date:
                    lines.append(f"*Expires: {cert.expiration_date}*")
                lines.append("")
        
        return "\n".join(lines)
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to basic HTML."""
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "    <meta charset='utf-8'>",
            "    <title>Resume</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }",
            "        h2 { color: #34495e; margin-top: 30px; }",
            "        h3 { color: #7f8c8d; }",
            "        ul { padding-left: 20px; }",
            "    </style>",
            "</head>",
            "<body>",
        ]
        
        # Simple markdown to HTML conversion
        lines = markdown_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                html_lines.append(f"    <h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                html_lines.append(f"    <h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                html_lines.append(f"    <h3>{line[4:]}</h3>")
            elif line.startswith('- '):
                html_lines.append(f"    <li>{line[2:]}</li>")
            elif line.strip() == '':
                html_lines.append("    <br/>")
            else:
                # Handle bold text
                if '**' in line:
                    line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                if '*' in line and not '<strong>' in line:
                    line = line.replace('*', '<em>', 1).replace('*', '</em>', 1)
                html_lines.append(f"    <p>{line}</p>")
        
        html_lines.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_lines)
    
    async def _generate_pdf(
        self,
        profile_data: ProfileData,
        timestamp: str,
        template: Optional[str] = None
    ) -> Path:
        """Generate PDF resume using ReportLab."""
        filename = f"resume_{timestamp}.pdf"
        output_path = self.output_dir / filename
        
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
        except ImportError:
            logger.error("ReportLab not installed. Install with: pip install reportlab")
            raise ImportError("ReportLab is required for PDF generation")
        
        # Create PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles for professional look
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.black,
            borderPadding=4
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # Add content
        # Name
        story.append(Paragraph(profile_data.name, title_style))
        
        # Headline
        if profile_data.headline:
            story.append(Paragraph(profile_data.headline, styles['Heading3']))
        story.append(Spacer(1, 12))
        
        # Contact Information
        if profile_data.contact_info:
            story.append(Paragraph("Contact Information", heading_style))
            contact = profile_data.contact_info
            contact_lines = []
            if contact.email:
                contact_lines.append(f"Email: {contact.email}")
            if contact.phone:
                contact_lines.append(f"Phone: {contact.phone}")
            if contact.location:
                contact_lines.append(f"Location: {contact.location}")
            if contact.linkedin_url:
                contact_lines.append(f"LinkedIn: {contact.linkedin_url}")
            
            for line in contact_lines:
                story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 12))
        
        # Summary
        if profile_data.summary:
            story.append(Paragraph("Professional Summary", heading_style))
            story.append(Paragraph(profile_data.summary, body_style))
            story.append(Spacer(1, 12))
        
        # Experience
        if profile_data.experience:
            story.append(Paragraph("Professional Experience", heading_style))
            for exp in profile_data.experience:
                # Position title and company
                title_text = f"{exp.title} at {exp.company}"
                story.append(Paragraph(title_text, subheading_style))
                
                # Date range
                if exp.start_date or exp.end_date:
                    date_range = f"{exp.start_date or 'Unknown'} - {exp.end_date or 'Present'}"
                    story.append(Paragraph(date_range, body_style))
                
                # Location
                if exp.location:
                    story.append(Paragraph(exp.location, body_style))
                
                # Description
                if exp.description:
                    story.append(Paragraph(exp.description, body_style))
                
                # Skills
                if exp.skills:
                    skills_text = f"Skills: {', '.join(exp.skills)}"
                    story.append(Paragraph(skills_text, body_style))
                
                story.append(Spacer(1, 8))
        
        # Skills
        if profile_data.skills:
            story.append(Paragraph("Skills", heading_style))
            if hasattr(profile_data, 'skills_summary') and profile_data.skills_summary:
                # Group by category
                for category, skills in profile_data.skills_summary.by_category.items():
                    if skills:
                        story.append(Paragraph(f"{category.value}:", subheading_style))
                        skill_names = [skill.name for skill in skills]
                        story.append(Paragraph(', '.join(skill_names), body_style))
            else:
                # Simple list
                skill_names = [skill.name for skill in profile_data.skills]
                story.append(Paragraph(', '.join(skill_names), body_style))
            story.append(Spacer(1, 12))
        
        # Education
        if profile_data.education:
            story.append(Paragraph("Education", heading_style))
            for edu in profile_data.education:
                edu_title = f"{edu.degree} - {edu.field_of_study}"
                story.append(Paragraph(edu_title, subheading_style))
                story.append(Paragraph(edu.institution, body_style))
                
                if edu.start_date or edu.end_date:
                    date_range = f"{edu.start_date or 'Unknown'} - {edu.end_date or 'Unknown'}"
                    story.append(Paragraph(date_range, body_style))
                
                if edu.grade:
                    story.append(Paragraph(f"Grade: {edu.grade}", body_style))
                
                if edu.description:
                    story.append(Paragraph(edu.description, body_style))
                
                story.append(Spacer(1, 8))
        
        # Certifications
        if profile_data.certifications:
            story.append(Paragraph("Certifications", heading_style))
            for cert in profile_data.certifications:
                story.append(Paragraph(cert.name, subheading_style))
                story.append(Paragraph(cert.issuing_organization, body_style))
                
                if cert.issue_date:
                    story.append(Paragraph(f"Issued: {cert.issue_date}", body_style))
                if cert.expiration_date:
                    story.append(Paragraph(f"Expires: {cert.expiration_date}", body_style))
                
                story.append(Spacer(1, 8))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Generated PDF resume: {output_path}")
        return output_path


__all__ = ['ResumeGenerator']