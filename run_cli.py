#!/usr/bin/env python3
"""
CLI Runner Script for GitHub Actions

This script provides a reliable way to run the CLI from GitHub Actions
by handling dependency and import issues gracefully.
"""

import sys
import os
from pathlib import Path
import subprocess

def main():
    """Run the CLI with proper error handling."""
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    print("🔧 CLI Runner starting...")
    
    # Check if we can import the CLI
    try:
        from linkedin_resume_generator.cli.main import cli
        print("✅ CLI module imported successfully")
        
        # Run the CLI with passed arguments
        print(f"🚀 Running CLI with args: {sys.argv[1:]}")
        cli()
        
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        
        # Try installing dependencies
        print("📦 Attempting to install CLI dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "click", "rich"])
            print("✅ Dependencies installed, retrying CLI import...")
            
            # Try importing again
            from linkedin_resume_generator.cli.main import cli
            print("✅ CLI module imported after dependency install")
            cli()
            
        except Exception as e2:
            print(f"❌ Dependency installation failed: {e2}")
            print("🔄 Falling back to direct module execution...")
            
            # Try direct module execution
            try:
                cmd = [sys.executable, "-m", "linkedin_resume_generator.cli.main"] + sys.argv[1:]
                result = subprocess.run(cmd, cwd=Path(__file__).parent)
                sys.exit(result.returncode)
                
            except Exception as e3:
                print(f"❌ Direct module execution failed: {e3}")
                print("💡 Please ensure the project is properly installed:")
                print("   pip install -r requirements.txt")
                print("   or")
                print("   pip install .")
                sys.exit(1)
    
    except Exception as e:
        print(f"❌ CLI execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()