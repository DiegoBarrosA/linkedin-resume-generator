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
                    lines.append("**Skills:**")
                    for skill in exp.skills:
                        lines.append(f"- {skill}")
                lines.append("")
        
        # Skills
        if profile_data.skills:
            lines.append("## Skills")
            if hasattr(profile_data, 'skills_summary') and profile_data.skills_summary:
                # Group by category
                for category, skills in profile_data.skills_summary.by_category.items():
                    if skills:
                        lines.append(f"### {category.value}")
                        for skill in skills:
                            lines.append(f"- {skill.name}")
                        lines.append("")
            else:
                # Simple list as markdown bullets
                for skill in profile_data.skills:
                    lines.append(f"- {skill.name}")
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
        """Generate ATS-optimized PDF resume using Pandoc + LaTeX for professional output."""
        filename = f"resume_{timestamp}.pdf"
        output_path = self.output_dir / filename
        
        # Generate the markdown content
        markdown_content = self._create_markdown_content(profile_data)
        
        # Try Pandoc first (best quality, CI/CD optimized)
        try:
            return await self._generate_pdf_pandoc(markdown_content, output_path)
        except (ImportError, FileNotFoundError, OSError) as e:
            logger.info(f"Pandoc not available ({e}), trying markdown2...")
            try:
                return await self._generate_pdf_markdown2(markdown_content, output_path)
            except ImportError:
                logger.info("markdown2 not available, trying weasyprint...")
                try:
                    return await self._generate_pdf_weasyprint(markdown_content, output_path)
                except (ImportError, OSError) as e:
                    logger.info(f"WeasyPrint not available ({e}), trying pdfkit...")
                    try:
                        return await self._generate_pdf_pdfkit(markdown_content, output_path)
                    except ImportError:
                        logger.info("PDFKit not available, falling back to basic ReportLab...")
                        return await self._generate_pdf_fallback(profile_data, timestamp)

    async def _generate_pdf_pandoc(self, markdown_content: str, output_path: Path) -> Path:
        """Generate ATS-optimized PDF using Pandoc + LaTeX (best quality, CI/CD friendly)."""
        import subprocess
        import shutil
        import tempfile
        import os
        
        # Check if pandoc is available
        if not shutil.which('pandoc'):
            raise FileNotFoundError("Pandoc not found in PATH")
        
        try:
            # Create temporary markdown file with enhanced content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                # Add YAML front matter for better Pandoc processing
                enhanced_content = f"""---
title: "Resume"
author: "Resume"
date: ""
geometry: "margin=1in"
fontsize: 11pt
fontfamily: "helvet"
colorlinks: false
linkcolor: black
urlcolor: black
---

{markdown_content}
"""
                temp_md.write(enhanced_content)
                temp_md_path = temp_md.name
            
            # Use Pandoc to convert markdown to PDF with ATS-optimized LaTeX settings
            pandoc_cmd = [
                'pandoc',
                temp_md_path,
                '-o', str(output_path),
                '--pdf-engine=xelatex',  # XeLaTeX for better font handling
                '--variable', 'geometry:margin=1in',  # Standard 1-inch margins
                '--variable', 'fontsize=11pt',  # Professional font size
                '--variable', 'mainfont=Arial',  # ATS-friendly font
                '--variable', 'sansfont=Arial',  # Consistent sans-serif
                '--variable', 'monofont=Courier New',  # Monospace font
                '--variable', 'colorlinks=false',  # No colored links for ATS
                '--variable', 'linkcolor=black',  # Black links
                '--variable', 'urlcolor=black',   # Black URLs
                '--variable', 'citecolor=black',  # Black citations
                '--variable', 'toccolor=black',   # Black TOC
                '--variable', 'linestretch=1.2',  # Readable line spacing
                '--variable', 'indent=false',     # No paragraph indentation
                '--strip-comments',  # Remove comments
                '--standalone',      # Create standalone document
                '--from=markdown+yaml_metadata_block'  # Enable YAML front matter
            ]
            
            # Execute pandoc
            result = subprocess.run(
                pandoc_cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=os.path.dirname(temp_md_path)
            )
            
            # Clean up temporary file
            os.unlink(temp_md_path)
            
            if result.returncode == 0:
                logger.info(f"Generated ATS-optimized PDF resume using Pandoc+LaTeX: {output_path}")
                return output_path
            else:
                # Try with pdflatex as fallback
                logger.warning(f"XeLaTeX failed, trying pdflatex: {result.stderr}")
                return await self._generate_pdf_pandoc_pdflatex(markdown_content, output_path)
                
        except Exception as e:
            logger.error(f"Error generating PDF with Pandoc: {e}")
            raise
    
    async def _generate_pdf_pandoc_pdflatex(self, markdown_content: str, output_path: Path) -> Path:
        """Fallback Pandoc method using pdflatex instead of xelatex."""
        import subprocess
        import shutil
        import tempfile
        import os
        
        try:
            # Create temporary markdown file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                # Simpler YAML front matter for pdflatex compatibility
                enhanced_content = f"""---
geometry: "margin=1in"
fontsize: 11pt
colorlinks: false
---

{markdown_content}
"""
                temp_md.write(enhanced_content)
                temp_md_path = temp_md.name
            
            # Use pdflatex with more basic settings
            pandoc_cmd = [
                'pandoc',
                temp_md_path,
                '-o', str(output_path),
                '--pdf-engine=pdflatex',  # Standard pdflatex
                '--variable', 'geometry:margin=1in',
                '--variable', 'fontsize=11pt',
                '--variable', 'colorlinks=false',
                '--strip-comments',
                '--standalone'
            ]
            
            # Execute pandoc
            result = subprocess.run(
                pandoc_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Clean up temporary file
            os.unlink(temp_md_path)
            
            if result.returncode == 0:
                logger.info(f"Generated ATS-optimized PDF resume using Pandoc+pdflatex: {output_path}")
                return output_path
            else:
                logger.error(f"Pandoc pdflatex failed: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, pandoc_cmd, result.stderr)
                
        except Exception as e:
            logger.error(f"Error generating PDF with Pandoc pdflatex: {e}")
            raise
    
    async def _generate_pdf_markdown2(self, markdown_content: str, output_path: Path) -> Path:
        """Generate PDF using markdown2 + ReportLab (most reliable option)."""
        try:
            import markdown2
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT
            import re
        except ImportError as e:
            raise ImportError(f"markdown2 and reportlab required: {e}")
        
        # Try to use BeautifulSoup for better HTML parsing, fall back to regex
        try:
            from bs4 import BeautifulSoup
            use_bs4 = True
        except ImportError:
            use_bs4 = False
            logger.info("BeautifulSoup not available, using simple text parsing")
        
        # Convert markdown to clean text, preserving formatting cues
        html_content = markdown2.markdown(markdown_content)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path), 
            pagesize=letter,
            leftMargin=72, rightMargin=72,
            topMargin=72, bottomMargin=72
        )
        story = []
        
        # ATS-optimized styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ATSTitle', parent=styles['Normal'],
            fontSize=16, spaceAfter=12, alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'ATSHeading', parent=styles['Normal'],
            fontSize=12, spaceBefore=12, spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'ATSBody', parent=styles['Normal'],
            fontSize=10, spaceAfter=4, fontName='Helvetica'
        )
        
        if use_bs4:
            # Parse the HTML and extract clean content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li']):
                text = element.get_text().strip()
                if not text:
                    continue
                    
                if element.name == 'h1':
                    story.append(Paragraph(text, title_style))
                elif element.name == 'h2':
                    story.append(Paragraph(text.upper(), heading_style))
                elif element.name == 'h3':
                    story.append(Paragraph(text, body_style))
                elif element.name == 'li':
                    story.append(Paragraph(f"• {text}", body_style))
                elif element.name == 'p':
                    story.append(Paragraph(text, body_style))
        else:
            # Simple regex-based parsing as fallback
            def clean_html_tags(text: str) -> str:
                """Remove HTML tags and decode entities."""
                text = re.sub(r'<[^>]+>', '', text)
                text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                return text.strip()
            
            # Parse line by line
            for line in html_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('<h1>'):
                    text = clean_html_tags(line)
                    if text:
                        story.append(Paragraph(text, title_style))
                elif line.startswith('<h2>'):
                    text = clean_html_tags(line)
                    if text:
                        story.append(Paragraph(text.upper(), heading_style))
                elif line.startswith('<h3>'):
                    text = clean_html_tags(line)
                    if text:
                        story.append(Paragraph(text, body_style))
                elif line.startswith('<li>'):
                    text = clean_html_tags(line)
                    if text:
                        story.append(Paragraph(f"• {text}", body_style))
                elif line.startswith('<p>'):
                    text = clean_html_tags(line)
                    if text:
                        story.append(Paragraph(text, body_style))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Generated ATS-optimized PDF using markdown2+ReportLab: {output_path}")
        return output_path

    async def _generate_pdf_weasyprint(self, markdown_content: str, output_path: Path) -> Path:
        """Generate PDF using WeasyPrint (GitHub Actions friendly)."""
        try:
            import markdown2
            from weasyprint import HTML, CSS
        except ImportError:
            raise ImportError("WeasyPrint and markdown2 required: pip install weasyprint markdown2")
        
        # Convert markdown to HTML with proper formatting
        html_content = markdown2.markdown(
            markdown_content,
            extras=['fenced-code-blocks', 'tables', 'break-on-newline']
        )
        
        # Add ATS-optimized CSS
        css_content = """
        @page {
            size: letter;
            margin: 1in;
        }
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: black;
            max-width: none;
        }
        h1 {
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 0.5em;
            page-break-after: avoid;
        }
        h2 {
            font-size: 12pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.3em;
            page-break-after: avoid;
        }
        h3 {
            font-size: 11pt;
            font-weight: bold;
            margin-top: 0.8em;
            margin-bottom: 0.2em;
            page-break-after: avoid;
        }
        p, li {
            margin-bottom: 0.2em;
        }
        ul {
            padding-left: 1em;
            margin: 0.3em 0;
        }
        strong {
            font-weight: bold;
        }
        em {
            font-style: italic;
        }
        """
        
        # Wrap in full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Resume</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=full_html).write_pdf(
            str(output_path),
            stylesheets=[CSS(string=css_content)]
        )
        
        logger.info(f"Generated ATS-optimized PDF resume using WeasyPrint: {output_path}")
        return output_path
    
    async def _generate_pdf_pdfkit(self, markdown_content: str, output_path: Path) -> Path:
        """Generate PDF using pdfkit (wkhtmltopdf wrapper)."""
        try:
            import markdown2
            import pdfkit
        except ImportError:
            raise ImportError("PDFKit and markdown2 required: pip install pdfkit markdown2")
        
        # Convert markdown to HTML
        html_content = markdown2.markdown(
            markdown_content,
            extras=['fenced-code-blocks', 'tables']
        )
        
        # Add simple styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 11pt; line-height: 1.4; }}
                h1 {{ font-size: 16pt; }}
                h2 {{ font-size: 12pt; margin-top: 1em; }}
                h3 {{ font-size: 11pt; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # PDF options for ATS compatibility
        options = {
            'page-size': 'Letter',
            'margin-top': '1in',
            'margin-right': '1in',
            'margin-bottom': '1in',
            'margin-left': '1in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        pdfkit.from_string(styled_html, str(output_path), options=options)
        
        logger.info(f"Generated ATS-optimized PDF resume using PDFKit: {output_path}")
        return output_path
    
    async def _generate_pdf_fallback(
        self,
        profile_data: ProfileData,
        timestamp: str
    ) -> Path:
        """Fallback PDF generation using ReportLab when Pandoc is not available."""
        filename = f"resume_{timestamp}.pdf"
        output_path = self.output_dir / filename
        
        # Generate the markdown content
        markdown_content = self._create_markdown_content(profile_data)
        
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT
        except ImportError:
            logger.error("ReportLab not installed. Install with: pip install reportlab")
            raise ImportError("ReportLab is required for PDF generation")
        
        # Create PDF document with ATS-friendly settings
        doc = SimpleDocTemplate(
            str(output_path), 
            pagesize=letter,
            leftMargin=72,    # 1 inch margins
            rightMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        story = []
        
        # ATS-optimized styles (simple, standard fonts)
        styles = getSampleStyleSheet()
        
        # Simple, ATS-friendly styles
        title_style = ParagraphStyle(
            'ATSTitle',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'ATSHeading',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'ATSBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            fontName='Helvetica'
        )
        
        def clean_markdown_formatting(text: str) -> str:
            """Remove markdown formatting for ATS compatibility."""
            import re
            # Remove bold formatting but keep the text
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            # Remove italic formatting but keep the text
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            return text
        
        # Parse markdown and convert to ATS-friendly format
        lines = markdown_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle headers
            if line.startswith('# '):
                # Main title (name)
                clean_title = clean_markdown_formatting(line[2:])
                story.append(Paragraph(clean_title, title_style))
            elif line.startswith('## '):
                # Section headers
                current_section = clean_markdown_formatting(line[3:])
                story.append(Paragraph(current_section.upper(), heading_style))
            elif line.startswith('### '):
                # Subsection headers (job titles, etc.)
                clean_subtitle = clean_markdown_formatting(line[4:])
                story.append(Paragraph(clean_subtitle, body_style))
            elif line.startswith('- '):
                # List items - convert to simple text for ATS compatibility
                skill_text = clean_markdown_formatting(line[2:])
                story.append(Paragraph(f"• {skill_text}", body_style))
            else:
                # Regular paragraph text - clean all markdown formatting
                if line:
                    clean_text = clean_markdown_formatting(line)
                    story.append(Paragraph(clean_text, body_style))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Generated fallback PDF resume: {output_path}")
        return output_path


__all__ = ['ResumeGenerator']