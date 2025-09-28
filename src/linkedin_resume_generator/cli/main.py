"""Command Line Interface for LinkedIn Resume Generator."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import track
from rich.panel import Panel

from ..config.settings import Settings, get_settings
from ..scrapers.linkedin_scraper import LinkedInScraper
from ..generators.resume_generator import ResumeGenerator
from ..processors.privacy_processor import PrivacyProcessor
from ..utils.logging import Logger, get_logger
from ..utils.exceptions import (
    LinkedInResumeGeneratorError, 
    ConfigurationError,
    AuthenticationError
)


console = Console()
logger = get_logger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--config-file", type=click.Path(exists=True), help="Path to configuration file")
@click.pass_context
def cli(ctx, debug: bool, config_file: Optional[str]):
    """LinkedIn Resume Generator - Professional resume generation from LinkedIn profiles."""
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Load settings
    try:
        settings = get_settings()
        if debug:
            settings.debug = True
            settings.logging.level = "DEBUG"
        
        # Setup logging
        Logger.setup(settings.logging)
        
        ctx.obj["settings"] = settings
        
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--profile-url", help="Specific LinkedIn profile URL to scrape")
@click.option("--output-dir", type=click.Path(), help="Output directory for generated files")
@click.option("--format", type=click.Choice(["markdown", "json", "both"]), default="markdown", help="Output format")
@click.option("--skip-auth", is_flag=True, help="Skip authentication (for testing)")
@click.pass_context
def scrape(ctx, profile_url: Optional[str], output_dir: Optional[str], format: str, skip_auth: bool):
    """Scrape LinkedIn profile and generate resume."""
    
    settings: Settings = ctx.obj["settings"]
    
    if output_dir:
        settings.output.output_dir = Path(output_dir)
    
    asyncio.run(_run_scrape(settings, profile_url, format, skip_auth))


async def _run_scrape(settings: Settings, profile_url: Optional[str], format: str, skip_auth: bool):
    """Run the scraping process."""
    
    try:
        console.print(Panel.fit("🚀 LinkedIn Resume Generator", style="bold blue"))
        
        # Validate credentials unless skipping auth
        if not skip_auth:
            try:
                settings.validate_credentials()
            except ConfigurationError as e:
                console.print(f"[red]❌ {e}[/red]")
                console.print("\n[yellow]Please set your LinkedIn credentials in environment variables:[/yellow]")
                console.print("  LINKEDIN_EMAIL=your-email@example.com")
                console.print("  LINKEDIN_PASSWORD=your-password") 
                console.print("  LINKEDIN_TOTP_SECRET=your-2fa-secret")
                return
        
        # Show compliance warning
        _show_compliance_warning()
        
        if not settings.ci_mode:
            if not click.confirm("\nDo you want to continue?", default=True):
                console.print("[yellow]Operation cancelled.[/yellow]")
                return
        
        # Initialize scraper
        console.print("\n[cyan]Initializing LinkedIn scraper...[/cyan]")
        
        async with LinkedInScraper(settings) as scraper:
            # Scrape profile
            console.print("[cyan]Scraping LinkedIn profile...[/cyan]")
            profile_data = await scraper.scrape_profile(profile_url)
            
            console.print(f"[green]✅ Successfully scraped profile: {profile_data.name}[/green]")
            console.print(f"   📊 {len(profile_data.skills)} skills found")
            console.print(f"   💼 {len(profile_data.experience)} experience items")
            console.print(f"   🎓 {len(profile_data.education)} education items")
            
            # Generate outputs
            if format in ["markdown", "both"]:
                console.print("\n[cyan]Generating markdown resume...[/cyan]")
                generator = ResumeGenerator(settings)
                markdown_content = generator.generate_markdown(profile_data)
                
                output_file = settings.output.output_dir / settings.output.resume_filename
                generator.save_markdown(markdown_content, output_file)
                
                console.print(f"[green]✅ Resume saved to: {output_file}[/green]")
                
                # Create GitHub Pages index if enabled
                if settings.output.create_github_pages:
                    index_file = settings.output.output_dir / settings.output.index_filename
                    generator.create_github_pages_index(markdown_content, index_file)
                    console.print(f"[green]✅ GitHub Pages index saved to: {index_file}[/green]")
            
            if format in ["json", "both"]:
                console.print("\n[cyan]Saving JSON data...[/cyan]")
                json_file = settings.output.output_dir / "profile_data.json"
                with open(json_file, "w") as f:
                    f.write(profile_data.json(indent=2))
                console.print(f"[green]✅ JSON data saved to: {json_file}[/green]")
            
            # Privacy processing if enabled
            if settings.compliance.privacy_mode:
                console.print("\n[cyan]Running privacy-safe processing...[/cyan]")
                processor = PrivacyProcessor(settings)
                await processor.cleanup_raw_data()
                console.print("[green]✅ Privacy processing completed[/green]")
        
        console.print("\n[bold green]🎉 Resume generation completed successfully![/bold green]")
        
    except AuthenticationError as e:
        console.print(f"\n[red]❌ Authentication failed: {e}[/red]")
        console.print("\n[yellow]Tips:[/yellow]")
        console.print("  • Check your LinkedIn credentials")
        console.print("  • Verify 2FA TOTP secret if using 2FA")
        console.print("  • Ensure your LinkedIn account is accessible")
        
    except LinkedInResumeGeneratorError as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        if settings.debug:
            import traceback
            console.print("[dim]" + traceback.format_exc() + "[/dim]")


@cli.command()
@click.pass_context  
def validate(ctx):
    """Validate configuration and credentials."""
    
    settings: Settings = ctx.obj["settings"]
    
    console.print(Panel.fit("🔍 Configuration Validation", style="bold cyan"))
    
    # Check environment
    console.print(f"Environment: [bold]{settings.environment}[/bold]")
    console.print(f"CI Mode: {'✅' if settings.ci_mode else '❌'}")
    console.print(f"Debug: {'✅' if settings.debug else '❌'}")
    
    # Validate credentials
    console.print("\n[cyan]Checking LinkedIn credentials...[/cyan]")
    try:
        settings.validate_credentials()
        console.print("[green]✅ LinkedIn credentials are valid[/green]")
    except ConfigurationError as e:
        console.print(f"[red]❌ {e}[/red]")
    
    # Check output configuration
    console.print(f"\nOutput directory: {settings.output.output_dir}")
    console.print(f"Resume filename: {settings.output.resume_filename}")
    console.print(f"GitHub Pages: {'✅' if settings.output.create_github_pages else '❌'}")
    
    # Check compliance settings
    console.print(f"\nCompliance settings:")
    console.print(f"  Auto cleanup: {'✅' if settings.compliance.auto_cleanup else '❌'}")
    console.print(f"  Privacy mode: {'✅' if settings.compliance.privacy_mode else '❌'}")
    console.print(f"  Audit enabled: {'✅' if settings.compliance.audit_enabled else '❌'}")


@cli.command()
@click.option("--check-violations", is_flag=True, help="Check for ToS violations")
@click.pass_context
def audit(ctx, check_violations: bool):
    """Run compliance audit."""
    
    settings: Settings = ctx.obj["settings"]
    
    console.print(Panel.fit("🔍 LinkedIn ToS Compliance Audit", style="bold yellow"))
    
    try:
        from ..processors.compliance_auditor import ComplianceAuditor
        
        auditor = ComplianceAuditor(settings)
        results = auditor.run_audit()
        
        # Display results
        console.print(f"\n[bold]Audit Status:[/bold] {results['status']}")
        
        if results.get("violations"):
            console.print("\n[red]❌ VIOLATIONS:[/red]")
            for violation in results["violations"]:
                console.print(f"  • {violation}")
        
        if results.get("warnings"):
            console.print(f"\n[yellow]⚠️  WARNINGS ({len(results['warnings'])}):[/yellow]")
            for warning in results["warnings"]:
                console.print(f"  • {warning}")
        
        if results.get("compliant_files"):
            console.print(f"\n[green]✅ COMPLIANT FILES ({len(results['compliant_files'])}):[/green]")
            for file_info in results["compliant_files"]:
                console.print(f"  ✅ {file_info}")
        
        console.print(f"\nAudit log: {results.get('log_file', 'N/A')}")
        
    except ImportError:
        console.print("[yellow]⚠️  Compliance auditor not available[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Audit failed: {e}[/red]")


@cli.command()
@click.pass_context
def cleanup(ctx):
    """Cleanup temporary and raw data files."""
    
    settings: Settings = ctx.obj["settings"]
    
    console.print(Panel.fit("🗑️  Data Cleanup", style="bold red"))
    
    try:
        from ..processors.privacy_processor import PrivacyProcessor
        
        processor = PrivacyProcessor(settings)
        
        console.print("[cyan]Cleaning up raw LinkedIn data files...[/cyan]")
        asyncio.run(processor.cleanup_raw_data())
        
        console.print("[green]✅ Cleanup completed successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Cleanup failed: {e}[/red]")


@cli.command()
@click.argument("template_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def generate(ctx, template_path: str, output: Optional[str]):
    """Generate resume from existing profile data using custom template."""
    
    settings: Settings = ctx.obj["settings"]
    
    console.print(Panel.fit("📝 Resume Generation", style="bold green"))
    
    try:
        # Look for existing profile data
        data_files = ["profile_data.json", "linkedin_data_enhanced.json", "linkedin_data.json"]
        profile_data = None
        
        for filename in data_files:
            data_path = Path(filename)
            if data_path.exists():
                console.print(f"[cyan]Loading profile data from {filename}...[/cyan]")
                
                # Load and validate data
                from ..models.profile import ProfileData
                import json
                
                with open(data_path) as f:
                    data = json.load(f)
                
                # Convert to ProfileData if needed
                if isinstance(data, dict):
                    profile_data = ProfileData(**data)
                
                break
        
        if not profile_data:
            console.print("[red]❌ No profile data found. Run 'scrape' command first.[/red]")
            return
        
        # Generate resume
        generator = ResumeGenerator(settings)
        
        # Load custom template if provided
        with open(template_path) as f:
            template_content = f.read()
        
        markdown_content = generator.generate_with_template(profile_data, template_content)
        
        # Save output
        output_path = Path(output) if output else settings.output.output_dir / "custom_resume.md"
        with open(output_path, "w") as f:
            f.write(markdown_content)
        
        console.print(f"[green]✅ Custom resume generated: {output_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Generation failed: {e}[/red]")


def _show_compliance_warning():
    """Show LinkedIn ToS compliance warning."""
    warning_text = """
⚠️  LINKEDIN ToS COMPLIANCE WARNING ⚠️

This tool scrapes LinkedIn data for personal resume generation only.
LinkedIn's Terms of Service prohibit storing or redistributing scraped profile content.

• Only use on your OWN LinkedIn profile
• Raw scraped data is automatically deleted after processing
• Generated resumes contain only processed, non-proprietary information
• Respect LinkedIn's rate limits and usage policies

By continuing, you acknowledge that you will use this tool responsibly
and in compliance with LinkedIn's Terms of Service.
    """
    
    console.print(Panel(warning_text.strip(), style="bold yellow", title="⚠️  COMPLIANCE WARNING"))


if __name__ == "__main__":
    cli()