#!/bin/bash
# Uninstallation script for Clawdbot SMTP Tool

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🗑️  Clawdbot SMTP Tool - Uninstaller"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Please run as root or with sudo${NC}"
    exit 1
fi

# Confirm uninstallation
echo -e "${RED}This will remove the Clawdbot SMTP Tool from your system.${NC}"
echo -e "${YELLOW}Your configuration files in /etc/clawdbot-smtp will NOT be removed.${NC}"
read -p "Are you sure? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Remove executable
echo "Removing /usr/local/bin/clawdbot-smtp..."
rm -f /usr/local/bin/clawdbot-smtp

# Ask about data files
echo ""
read -p "Remove data directory /var/lib/clawdbot-smtp? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing /var/lib/clawdbot-smtp..."
    rm -rf /var/lib/clawdbot-smtp
fi

# Ask about config files
echo ""
read -p "Remove configuration directory /etc/clawdbot-smtp? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing /etc/clawdbot-smtp..."
    rm -rf /etc/clawdbot-smtp
fi

echo ""
echo -e "${GREEN}✓ Uninstallation complete!${NC}"
