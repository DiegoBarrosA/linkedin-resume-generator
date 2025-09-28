#!/usr/bin/env python3
"""
Entry point script for LinkedIn Resume Generator.

This script maintains backward compatibility with the old interface
while providing access to the new modular architecture.
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from linkedin_resume_generator.config.settings import get_settings
    from linkedin_resume_generator.scrapers.linkedin_scraper import LinkedInScraper
    from linkedin_resume_generator.utils.logging import Logger, get_logger
    from linkedin_resume_generator.utils.exceptions import LinkedInResumeGeneratorError
    
    MODERN_MODULES_AVAILABLE = True
except ImportError:
    MODERN_MODULES_AVAILABLE = False
    print("Warning: New modular architecture not available. Using legacy mode.")


async def main():
    """Main entry point with backward compatibility."""
    
    if MODERN_MODULES_AVAILABLE:
        # Use new modular architecture
        await run_modern()
    else:
        # Fallback to legacy implementation
        await run_legacy()


async def run_modern():
    """Run using the new modular architecture."""
    try:
        # Load settings
        settings = get_settings()
        
        # Setup logging
        Logger.setup(settings.logging)
        logger = get_logger(__name__)
        
        # Show compliance warning if not in CI mode
        if not settings.ci_mode:
            print("\n⚠️  LINKEDIN ToS COMPLIANCE WARNING ⚠️")
            print("This tool scrapes LinkedIn data for personal resume generation only.")
            print("LinkedIn ToS prohibits storing/redistributing scraped profile content.")
            print("Only use on your OWN profile. Raw data is automatically deleted.")
            
            response = input("\nDo you want to continue? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        logger.info("Starting LinkedIn resume generation")
        
        # Initialize scraper
        async with LinkedInScraper(settings) as scraper:
            profile_data = await scraper.scrape_profile()
            
            print(f"✅ Successfully scraped profile: {profile_data.name}")
            print(f"   📊 {len(profile_data.skills)} skills found")
            print(f"   💼 {len(profile_data.experience)} experience items")
            print(f"   🎓 {len(profile_data.education)} education items")
            
            # Generate resume (import generator when needed)
            from linkedin_resume_generator.generators.resume_generator import ResumeGenerator
            
            generator = ResumeGenerator(settings)
            markdown_content = generator.generate_markdown(profile_data)
            
            output_file = settings.output.output_dir / settings.output.resume_filename
            generator.save_markdown(markdown_content, output_file)
            
            print(f"✅ Resume saved to: {output_file}")
            
            # Privacy cleanup
            if settings.compliance.auto_cleanup:
                from linkedin_resume_generator.processors.privacy_processor import PrivacyProcessor
                processor = PrivacyProcessor(settings)
                await processor.cleanup_raw_data()
                print("✅ Privacy cleanup completed")
        
        print("🎉 Resume generation completed successfully!")
        
    except LinkedInResumeGeneratorError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


async def run_legacy():
    """Run using legacy implementation for backward compatibility."""
    try:
        # Import legacy modules
        import scrape_linkedin
        import enhance_skills
        import generate_markdown
        
        print("Running in legacy mode...")
        
        # Run legacy scraping
        await scrape_linkedin.main()
        
        print("✅ Legacy scraping completed")
        
        # Enhance skills
        enhance_skills.main()
        
        print("✅ Skills enhancement completed")
        
        # Generate markdown
        generate_markdown.main()
        
        print("✅ Resume generation completed")
        
    except ImportError as e:
        print(f"❌ Could not import legacy modules: {e}")
        print("Please ensure all required dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Legacy execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running as CLI with arguments
    if len(sys.argv) > 1:
        # Try to use the new CLI if modern modules are available
        if MODERN_MODULES_AVAILABLE:
            try:
                from linkedin_resume_generator.cli.main import cli
                cli()
            except ImportError as e:
                print(f"❌ CLI import failed: {e}")
                print("💡 This might be due to missing dependencies (click, rich)")
                print("📝 Try: pip install click rich")
                print("🔄 Falling back to legacy interface...")
                
                # Try to run legacy mode with the same arguments
                if len(sys.argv) >= 2 and sys.argv[1] == "scrape":
                    print("🚀 Running legacy scrape mode...")
                    # Remove CLI arguments and run main
                    sys.argv = [sys.argv[0]]  # Keep only script name
                    asyncio.run(main())
                else:
                    print("New CLI not available. Use 'python main.py' (no args) for legacy interface.")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ CLI execution failed: {e}")
                sys.exit(1)
        else:
            print("❌ Modern modules not available. CLI cannot run.")
            print("New CLI not available. Use 'python main.py' (no args) for legacy interface.")
            sys.exit(1)
    else:
        # Run the main application
        asyncio.run(main())