#!/bin/bash
# Release script for creating distribution packages

set -e

VERSION=${1:-"1.0.0"}
ARCH=$(uname -m)
DISTRO="linux"

echo "📦 Creating release package..."
echo "Version: $VERSION"
echo "Arch: $ARCH"
echo ""

# Clean
rm -rf release/

# Create release directory
mkdir -p release
mkdir -p release/usr/local/bin
mkdir -p release/etc/clawdbot-smtp
mkdir -p release/var/lib/clawdbot-smtp/templates
mkdir -p release/share/doc/clawdbot-smtp

# Build executable
./packaging/build.sh

# Copy files
cp dist/clawdbot-smtp release/usr/local/bin/
cp config.example.json release/etc/clawdbot-smtp/config.json
cp email_cli/templates/*.html release/var/lib/clawdbot-smtp/templates/
cp README.md release/share/doc/clawdbot-smtp/
cp LICENSE release/share/doc/clawdbot-smtp/
cp clawdbot_integration/README.md release/share/doc/clawdbot-smtp/INTEGRATION.md
cp clawdbot_integration/email_check.py release/var/lib/clawdbot-smtp/

# Copy install script
cp packaging/install.sh release/install.sh
cp packaging/uninstall.sh release/uninstall.sh

# Create tar.gz package
cd release
tar -czf ../clawdbot-smtp-${VERSION}-${DISTRO}-${ARCH}.tar.gz *
cd ..

echo "✅ Release package created: clawdbot-smtp-${VERSION}-${DISTRO}-${ARCH}.tar.gz"

# Calculate checksum
if command -v sha256sum &> /dev/null; then
    sha256sum clawdbot-smtp-${VERSION}-${DISTRO}-${ARCH}.tar.gz > clawdbot-smtp-${VERSION}-${DISTRO}-${ARCH}.tar.gz.sha256
    echo "📋 Checksum: clawdbot-smtp-${VERSION}-${DISTRO}-${ARCH}.tar.gz.sha256"
fi

echo ""
echo "To install on a target system:"
echo "  tar -xzf clawdbot-smtp-${VERSION}-${DISTRO}-${ARCH}.tar.gz"
echo "  cd release"
echo "  sudo ./install.sh"
