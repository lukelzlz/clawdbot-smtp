#!/bin/bash
# Build script for creating standalone Linux executable

set -e

echo "📦 Building Clawdbot SMTP Tool for Linux..."

# Clean previous builds
rm -rf build/ dist/

# Build with PyInstaller
pyinstaller \
    --name="clawdbot-smtp" \
    --onefile \
    --add-data "email_cli/templates:email_cli/templates" \
    --hidden-import=jinja2 \
    --hidden-import=click \
    --hidden-import=dotenv \
    --hidden-import=colorama \
    --clean \
    email_cli/main.py

echo "✅ Build complete!"
echo "📍 Executable: dist/clawdbot-smtp"
echo ""
echo "To install system-wide:"
echo "  sudo cp dist/clawdbot-smtp /usr/local/bin/"
echo "  sudo chmod +x /usr/local/bin/clawdbot-smtp"
echo ""
echo "To test:"
echo "  ./dist/clawdbot-smtp --help"
