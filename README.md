# Clawdbot SMTP/IMAP Tool

Deeply integrated SMTP/IMAP CLI tool for Clawdbot - manage emails with templates and cron support.

## Features

- 📤 **SMTP Sending** - Send emails with attachments, HTML, or plain text
- 📥 **IMAP Management** - List, read, search, and delete emails
- 🎨 **Template System** - Jinja2-based email templates
- 👥 **Multi-Account** - Manage multiple email accounts
- 🔧 **Clawdbot Integration** - JSON output, message tool integration
- ⏰ **Cron Support** - Schedule email tasks via Clawdbot cron
- 🔐 **Secure** - Environment-based configuration, no hardcoded secrets

## Installation

```bash
# Clone and install
git clone https://github.com/lukelzlz/clawdbot-smtp.git
cd clawdbot-smtp
pip install -r requirements.txt

# Configure accounts
cp config.example.json config.json
# Edit config.json with your account details
```

## Configuration

Create `config.json` or use environment variables:

```json
{
  "accounts": {
    "primary": {
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "imap_host": "imap.gmail.com",
      "imap_port": 993,
      "username": "your@email.com",
      "password": "your-app-password",
      "use_ssl": true
    }
  },
  "default_account": "primary"
}
```

### Environment Variables (Preferred)

```bash
# Primary account
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export IMAP_HOST=imap.gmail.com
export IMAP_PORT=993
export SMTP_USERNAME=your@email.com
export SMTP_PASSWORD=your-app-password

# Or use .env file
echo "SMTP_HOST=smtp.gmail.com" > .env
echo "SMTP_PORT=587" >> .env
# ... (add other variables)
```

## Usage

### Basic Commands

```bash
# Send email
python -m email_cli send \
  --to recipient@example.com \
  --subject "Test Email" \
  --body "Hello, this is a test!"

# Send with template
python -m email_cli send \
  --to recipient@example.com \
  --template welcome \
  --context '{"name": "John", "company": "ACME"}'

# List emails
python -m email_cli list --folder INBOX --limit 10

# Read email
python -m email_cli read --id 123

# Search emails
python -m email_cli search --query "FROM:boss@example.com urgent"

# Delete email
python -m email_cli delete --id 123

# Manage folders
python -m email_cli folders --list
python -m email_cli folders --create "Important"
```

### JSON Output (for Clawdbot integration)

```bash
# All commands support --json flag
python -m email_cli list --limit 5 --json
```

## Templates

Create templates in `email_cli/templates/`:

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
python -m email_cli send \
  --to user@example.com \
  --template welcome \
  --context '{"name": "Alice", "company": "TechCorp"}'
```

## Clawdbot Integration

### From Discord/Telegram

```
!email send to:user@example.com subject:Hello body:World
!email list limit:5
!email read id:123
!email search from:boss@example.com
```

### Example with Message Tool

```python
# Send email notification to Discord
import subprocess
import json

result = subprocess.run([
    'python', '-m', 'email_cli', 'list',
    '--folder', 'INBOX',
    '--limit', '5',
    '--json'
], capture_output=True, text=True)

emails = json.loads(result.stdout)
# Send to Discord via message tool
```

### Cron Integration

Schedule periodic email checks:
```bash
# Add cron job to check emails every hour
clawdbot cron add --id email-check \
  --schedule "0 * * * *" \
  --command "python -m email_cli list --folder INBOX --unread --json | email_summary.py"
```

## Advanced Usage

### Sending Attachments

```bash
python -m email_cli send \
  --to recipient@example.com \
  --subject "Report" \
  --body "Here's the report" \
  --attach report.pdf invoice.docx
```

### HTML Email

```bash
python -m email_cli send \
  --to recipient@example.com \
  --subject "Newsletter" \
  --html "<h1>Hello!</h1><p>This is HTML.</p>"
```

### Multi-Account

```bash
# Use specific account
python -m email_cli send \
  --account work \
  --to colleague@work.com \
  --subject "Meeting Notes"
```

## Security

- Never commit `config.json` to git
- Use `.env` file or environment variables
- Use app-specific passwords for Gmail
- Enable 2FA on your email accounts

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## License

MIT License

## Contributing

PRs welcome! This is a tool for the Clawdbot community.
