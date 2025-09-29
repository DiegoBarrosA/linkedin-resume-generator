#!/bin/bash

# Simple script to generate resume files locally
# Usage: ./generate.sh

echo "🔄 Generating resume files..."

# Check if Python dependencies are installed
python3 -c "import reportlab" 2>/dev/null || {
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
}

# Run the generation script
python3 generate_resume.py

echo "✅ Resume generation complete!"
echo "📁 Files available in docs/:"
echo "   - resume.md (Markdown format)"
echo "   - resume.pdf (PDF format)"