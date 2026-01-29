#!/bin/bash
# Installation script for Clawdbot SMTP Tool on Linux

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Clawdbot SMTP Tool - Linux Installer"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. This is optional but recommended for system-wide installation.${NC}"
fi

# Detect package manager
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt-get"
    INSTALL_CMD="sudo apt-get install -y"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    INSTALL_CMD="sudo yum install -y"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    INSTALL_CMD="sudo dnf install -y"
else
    echo -e "${RED}Error: No supported package manager found (apt-get, yum, dnf)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Package manager detected: $PKG_MANAGER${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Installing Python 3...${NC}"
    $INSTALL_CMD python3 python3-pip
else
    echo -e "${GREEN}✓ Python 3 found${NC}"
fi

# Install pip if needed
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}Installing pip...${NC}"
    python3 -m ensurepip --upgrade || $INSTALL_CMD python3-pip
else
    echo -e "${GREEN}✓ pip found${NC}"
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Install PyInstaller for building
echo ""
echo "📦 Installing PyInstaller..."
pip3 install --user pyinstaller

# Build the executable
echo ""
echo "🔨 Building standalone executable..."
./packaging/build.sh

# Install to system
echo ""
echo "📥 Installing to /usr/local/bin/..."
if [ "$EUID" -eq 0 ]; then
    cp dist/clawdbot-smtp /usr/local/bin/
    chmod +x /usr/local/bin/clawdbot-smtp
else
    sudo cp dist/clawdbot-smtp /usr/local/bin/
    sudo chmod +x /usr/local/bin/clawdbot-smtp
fi

# Create config directory
CONFIG_DIR="/etc/clawdbot-smtp"
echo ""
echo "📁 Creating config directory: $CONFIG_DIR"
if [ "$EUID" -eq 0 ]; then
    mkdir -p $CONFIG_DIR
    cp config.example.json $CONFIG_DIR/config.json
    chmod 600 $CONFIG_DIR/config.json
else
    sudo mkdir -p $CONFIG_DIR
    sudo cp config.example.json $CONFIG_DIR/config.json
    sudo chmod 600 $CONFIG_DIR/config.json
fi

# Create data directory for templates
DATA_DIR="/var/lib/clawdbot-smtp"
echo "📁 Creating data directory: $DATA_DIR"
if [ "$EUID" -eq 0 ]; then
    mkdir -p $DATA_DIR/templates
    cp email_cli/templates/* $DATA_DIR/templates/
else
    sudo mkdir -p $DATA_DIR/templates
    sudo cp email_cli/templates/* $DATA_DIR/templates/
fi

# Verify installation
echo ""
echo "🧪 Verifying installation..."
if command -v clawdbot-smtp &> /dev/null; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
    echo ""
    echo "📝 Configuration file: $CONFIG_DIR/config.json"
    echo "📝 Templates directory: $DATA_DIR/templates/"
    echo ""
    echo "🚀 To get started:"
    echo "  1. Edit $CONFIG_DIR/config.json with your email credentials"
    echo "  2. Run: clawdbot-smtp --help"
    echo ""
    echo "💡 Quick test:"
    echo "  clawdbot-smtp --help"
else
    echo -e "${RED}✗ Installation failed${NC}"
    exit 1
fi
