#!/usr/bin/env python3
"""Test Pandoc PDF generation in CI/CD environments."""

import subprocess
import tempfile
import shutil
from pathlib import Path

def test_pandoc_availability():
    """Test if Pandoc is available and working."""
    try:
        # Check if pandoc is available
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Pandoc is available:")
        print(result.stdout.split('\n')[0])  # First line with version
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pandoc is not available")
        return False

def test_latex_engines():
    """Test which LaTeX engines are available."""
    engines = ['pdflatex', 'xelatex', 'lualatex']
    available_engines = []
    
    for engine in engines:
        try:
            result = subprocess.run([engine, '--version'], 
                                  capture_output=True, text=True, check=True)
            available_engines.append(engine)
            print(f"✅ {engine} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {engine} is not available")
    
    return available_engines

def test_pandoc_pdf_generation():
    """Test actual PDF generation with Pandoc."""
    if not shutil.which('pandoc'):
        print("⏭️  Skipping PDF test - Pandoc not available")
        return False
    
    # Simple test markdown
    test_markdown = """# Test Resume
## Contact Information
- **Email:** test@example.com
- **Location:** Test City

## Summary
This is a test resume for validating Pandoc PDF generation.

## Skills
- Python
- LaTeX
- Pandoc
"""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
            # Add YAML front matter
            enhanced_content = f"""---
geometry: "margin=1in"
fontsize: 11pt
colorlinks: false
---

{test_markdown}
"""
            temp_md.write(enhanced_content)
            temp_md_path = temp_md.name
        
        # Try to generate PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        # Test with available engines
        engines = ['xelatex', 'pdflatex']
        for engine in engines:
            if shutil.which(engine) or engine == 'pdflatex':  # pdflatex usually comes with pandoc
                cmd = [
                    'pandoc',
                    temp_md_path,
                    '-o', temp_pdf_path,
                    f'--pdf-engine={engine}',
                    '--variable', 'geometry:margin=1in',
                    '--variable', 'fontsize=11pt',
                    '--standalone'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    pdf_size = Path(temp_pdf_path).stat().st_size
                    print(f"✅ PDF generated successfully with {engine} ({pdf_size} bytes)")
                    
                    # Cleanup
                    Path(temp_md_path).unlink()
                    Path(temp_pdf_path).unlink()
                    return True
                else:
                    print(f"❌ PDF generation failed with {engine}: {result.stderr}")
        
        # Cleanup on failure
        Path(temp_md_path).unlink()
        if Path(temp_pdf_path).exists():
            Path(temp_pdf_path).unlink()
        return False
        
    except Exception as e:
        print(f"❌ Error during PDF generation test: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing Pandoc availability and PDF generation...\n")
    
    pandoc_available = test_pandoc_availability()
    print()
    
    if pandoc_available:
        print("🔍 Testing LaTeX engines...")
        available_engines = test_latex_engines()
        print()
        
        if available_engines:
            print("🔍 Testing PDF generation...")
            pdf_success = test_pandoc_pdf_generation()
            print()
            
            if pdf_success:
                print("🎉 All tests passed! Pandoc PDF generation is ready for CI/CD")
                return True
        else:
            print("⚠️  No LaTeX engines available - PDF generation will not work")
    
    print("ℹ️  Pandoc not fully available - will fall back to other methods")
    return False

if __name__ == "__main__":
    main()