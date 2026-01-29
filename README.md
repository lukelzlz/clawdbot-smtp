# Clawdbot SMTP/IMAP Tool

Deeply integrated SMTP/IMAP CLI tool for Clawdbot - manage emails with templates and cron support.

## 🌟 Features

- 📤 **SMTP Sending** - Send emails with attachments, HTML, or plain text
- 📥 **IMAP Management** - List, read, search, and delete emails
- 🎨 **Template System** - Jinja2-based email templates
- 👥 **Multi-Account** - Manage multiple email accounts
- 🔧 **Clawdbot Integration** - JSON output, message tool integration
- ⏰ **Cron Support** - Schedule email tasks via Clawdbot cron
- 🐧 **Linux Package** - Standalone executable, easy installation
- 🔐 **Secure** - Environment-based configuration, no hardcoded secrets

## 📦 Installation

### Linux (Standalone Package) - Recommended

```bash
# One-line installation
curl -sSL https://raw.githubusercontent.com/lukelzlz/clawdbot-smtp/main/packaging/install.sh | bash

# Or download and install manually
wget https://github.com/lukelzlz/clawdbot-smtp/releases/latest/download/clawdbot-smtp-linux-x86_64.tar.gz
tar -xzf clawdbot-smtp-linux-x86_64.tar.gz
cd release
sudo ./install.sh
```

### Development / Python

```bash
# Clone and install
git clone https://github.com/lukelzlz/clawdbot-smtp.git
cd clawdbot-smtp
pip install -r requirements.txt

# Configure accounts
cp config.example.json config.json
# Edit config.json with your account details
```

## ⚙️ Configuration

After installation, edit the configuration file:

```bash
sudo nano /etc/clawdbot-smtp/config.json
```

### Gmail Example

```json
{
  "accounts": {
    "primary": {
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "imap_host": "imap.gmail.com",
      "imap_port": 993,
      "username": "your@gmail.com",
      "password": "your-app-password",
      "use_ssl": true
    }
  },
  "default_account": "primary"
}
```

**Gmail Note:** Must enable 2FA and create an app-specific password (not your account password).

### Outlook Example

```json
{
  "accounts": {
    "primary": {
      "smtp_host": "smtp.office365.com",
      "smtp_port": 587,
      "imap_host": "outlook.office365.com",
      "imap_port": 993,
      "username": "your@outlook.com",
      "password": "your-password",
      "use_ssl": true
    }
  },
  "default_account": "primary"
}
```

### Environment Variables (Alternative)

```bash
# Gmail
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export IMAP_HOST=imap.gmail.com
export IMAP_PORT=993
export SMTP_USERNAME=your@gmail.com
export SMTP_PASSWORD=your-app-password
```

## 🚀 Usage

### Basic Commands

```bash
# Send email
clawdbot-smtp send --to recipient@example.com --subject "Test" --body "Hello, World!"

# Send with attachment
clawdbot-smtp send --to recipient@example.com --subject "Report" --body "See attachment" --attach report.pdf

# Send with template
clawdbot-smtp send --to recipient@example.com --subject "Welcome" --template welcome --context '{"name": "John", "company": "ACME"}'

# List emails
clawdbot-smtp list --limit 10

# List unread emails
clawdbot-smtp list --unread

# Read email
clawdbot-smtp read --id 123

# Search emails
clawdbot-smtp search --query "FROM:boss@example.com urgent"

# Delete email
clawdbot-smtp delete --id 123

# Manage folders
clawdbot-smtp folders list
clawdbot-smtp folders create --name "Important"
```

### JSON Output (for Clawdbot Integration)

```bash
# All commands support --json flag
clawdbot-smtp list --limit 5 --json
```

## 📝 Templates

Templates are located in `/var/lib/clawdbot-smtp/templates/` (installed) or `email_cli/templates/` (development).

**welcome.html**
```html
<!DOCTYPE html>
<html>
<body>
  <h1>Welcome, {{ name }}!</h1>
  <p>Thanks for joining {{ company }}.</p>
</body>
</html>
```

Use with context variables:
```bash
clawdbot-smtp send --to user@example.com --subject "Welcome" --template welcome --context '{"name": "Alice", "company": "TechCorp"}'
```

## 🔗 Clawdbot Integration

### From Discord/Telegram

```
!email send to:user@example.com subject:Hello body:World
!email list limit:5
!email read id:123
!email search from:boss@example.com
```

### With Message Tool

```python
import subprocess
import json

# Check emails
result = subprocess.run([
    'clawdbot-smtp', 'list',
    '--folder', 'INBOX',
    '--limit', '5',
    '--json'
], capture_output=True, text=True)

emails = json.loads(result.stdout)

# Send notification to Discord
if emails['total'] > 0:
    # Use Clawdbot's message tool
    pass
```

### Cron Integration

```bash
# Add cron job to check emails every hour
clawdbot cron add \
  --id email-check \
  --schedule "0 * * * *" \
  --command "/var/lib/clawdbot-smtp/email_check.py 10 INBOX | clawdbot message send --to discord --target YOUR_CHANNEL_ID"
```

## 🛠️ Building from Source

```bash
# Install build dependencies
pip install -r requirements.txt

# Build standalone executable
cd packaging
./build.sh

# Create release package
./release.sh 1.0.0
```

## 📂 File Locations

**Standalone Package:**
- **Executable:** `/usr/local/bin/clawdbot-smtp`
- **Config:** `/etc/clawdbot-smtp/config.json`
- **Templates:** `/var/lib/clawdbot-smtp/templates/`
- **Docs:** `/usr/share/doc/clawdbot-smtp/`

**Development:**
- **Module:** `email_cli/`
- **Config:** `config.json`
- **Templates:** `email_cli/templates/`

## 🔐 Security

- Never commit `config.json` to git
- Use `.env` file or environment variables
- Use app-specific passwords for Gmail
- Enable 2FA on your email accounts
- Set file permissions: `chmod 600 config.json`

## 🧪 Troubleshooting

### Authentication Failures

**Gmail:**
- Enable 2FA: https://myaccount.google.com/security
- Create app password: https://myaccount.google.com/apppasswords
- Use the app password in config, not your account password

**Outlook:**
- Enable IMAP access in Outlook settings
- Check "Allow less secure apps" or use OAuth

### Connection Issues

```bash
# Test SMTP connection
clawdbot-smtp send --to yourself@example.com --subject Test --body "Test connection"

# Test IMAP connection
clawdbot-smtp list --limit 1
```

### Permission Issues

```bash
# Fix config permissions
sudo chmod 600 /etc/clawdbot-smtp/config.json
sudo chown root:root /etc/clawdbot-smtp/config.json
```

## 🌍 Supported Email Services

- ✅ Gmail
- ✅ Outlook/Office365
- ✅ Yahoo Mail
- ✅ Corporate Email (Exchange)
- ✅ Custom SMTP/IMAP servers

## 📚 Documentation

- [Full README](README.md)
- [中文文档](README_CN.md)
- [Clawdbot Integration Guide](clawdbot_integration/README.md)

## 🗑️ Uninstallation

```bash
sudo /var/lib/clawdbot-smtp/uninstall.sh
```

## 📄 License

MIT License

## 🤝 Contributing

PRs welcome! This is a tool for the Clawdbot community.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🌐 Community

- 🐛 Issues: https://github.com/lukelzlz/clawdbot-smtp/issues
- 💬 Discord: https://discord.gg/clawd
- 📚 Docs: https://docs.clawd.bot
