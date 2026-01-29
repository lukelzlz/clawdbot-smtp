# Clawdbot Integration Guide

This document explains how to integrate the email_cli tool with Clawdbot.

## Overview

The email_cli tool provides deep integration with Clawdbot through:
- JSON output format for easy parsing
- Command-line interface compatible with Clawdbot's exec tool
- Environment variable support for secure configuration
- Template system for automated email generation

## Installation in Clawdbot Workspace

```bash
# Clone into your Clawdbot workspace
cd /root/clawd
git clone https://github.com/lukelzlz/clawdbot-smtp.git

# Install dependencies
cd clawdbot-smtp
pip install -r requirements.txt
```

## Configuration

### Environment Variables (Recommended)

Add to your Clawdbot environment or `.env` file:

```bash
# Gmail example
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export IMAP_HOST=imap.gmail.com
export IMAP_PORT=993
export SMTP_USERNAME=your@gmail.com
export SMTP_PASSWORD=your-app-password

# Outlook example
export SMTP_HOST=smtp.office365.com
export SMTP_PORT=587
export IMAP_HOST=outlook.office365.com
export IMAP_PORT=993
export SMTP_USERNAME=your@outlook.com
export SMTP_PASSWORD=your-password
```

### Config File

Alternatively, create `config.json`:

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

## Usage from Clawdbot

### Basic Commands

Clawdbot can execute email commands using the `exec` tool:

```python
# Send email
exec("cd /root/clawd/clawdbot-smtp && python -m email_cli send --to user@example.com --subject 'Hello' --body 'Test'")

# List emails with JSON output
exec("cd /root/clawd/clawdbot-smtp && python -m email_cli list --limit 5 --json")
```

### Integration with Message Tool

Send email notifications to Discord/Telegram:

```python
import subprocess
import json

# Check emails
result = subprocess.run([
    'python', '-m', 'email_cli', 'list',
    '--folder', 'INBOX',
    '--unread',
    '--json'
], cwd='/root/clawd/clawdbot-smtp',
capture_output=True, text=True)

emails = json.loads(result.stdout)

if emails['total'] > 0:
    # Send notification to Discord
    message(
        action='send',
        channel='discord',
        target=channel_id,
        message=f"📬 You have {emails['total']} unread emails!\n\n" +
                "\n".join([f"- {e['subject']}" for e in emails['emails']])
    )
```

### Template-Based Emailing

```python
import subprocess

# Send welcome email using template
subprocess.run([
    'python', '-m', 'email_cli', 'send',
    '--to', 'new-user@example.com',
    '--subject', 'Welcome!',
    '--template', 'welcome',
    '--context', json.dumps({
        'name': 'John Doe',
        'company': 'My Company',
        'year': 2024
    })
], cwd='/root/clawd/clawdbot-smtp')
```

## Cron Integration

Schedule email tasks using Clawdbot's cron system:

### Hourly Email Check

```bash
# Create a check script
cat > /root/clawd/clawdbot-smtp/check_emails.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import json
import os

os.chdir('/root/clawd/clawdbot-smtp')

result = subprocess.run([
    'python', '-m', 'email_cli', 'list',
    '--folder', 'INBOX',
    '--unread',
    '--json'
], capture_output=True, text=True)

emails = json.loads(result.stdout)

if emails['total'] > 0:
    summary = f"📬 Unread emails: {emails['total']}\n"
    for email in emails['emails']:
        summary += f"\nFrom: {email['from']}\nSubject: {email['subject']}\n"

    # Send to Clawdbot's message system
    # This would be called by the cron job
    print(summary)
EOF

chmod +x /root/clawd/clawdbot-smtp/check_emails.py

# Add to Clawdbot cron (run every hour)
clawdbot cron add \
  --id email-check \
  --schedule "0 * * * *" \
  --command "cd /root/clawd/clawdbot-smtp && python check_emails.py | clawdbot message send --to discord --target YOUR_CHANNEL_ID"
```

### Scheduled Reports

```python
# Send daily report at 9 AM
import subprocess
from datetime import datetime

def send_daily_report():
    # Generate report content
    report = f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    report += "Emails received today: ...\n"
    report += "Tasks completed: ...\n"

    subprocess.run([
        'python', '-m', 'email_cli', 'send',
        '--to', 'manager@company.com',
        '--subject', f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}",
        '--body', report
    ], cwd='/root/clawd/clawdbot-smtp')

# Schedule via cron
# clawdbot cron add --id daily-report --schedule "0 9 * * *" --command "python -c 'import report; report.send_daily_report()'"
```

## Advanced Patterns

### Email to Message Routing

Forward important emails to Discord/Telegram:

```python
import subprocess
import json
import re

def check_and_forward_emails():
    os.chdir('/root/clawd/clawdbot-smtp')

    result = subprocess.run([
        'python', '-m', 'email_cli', 'search',
        '--query', 'FROM:boss@example.com',
        '--limit', '10',
        '--json'
    ], capture_output=True, text=True)

    emails = json.loads(result.stdout)

    for email in emails['emails']:
        # Check if already forwarded (you'd track this)
        if is_urgent(email):
            message(
                action='send',
                channel='discord',
                target=urgent_channel,
                message=f"🚨 URGENT EMAIL\n\n" +
                        f"From: {email['from']}\n" +
                        f"Subject: {email['subject']}\n\n" +
                        f"{email['body'][:500]}..."
            )
```

### Email Notifications for Events

```python
def send_event_notification(event_name, attendee, details):
    subprocess.run([
        'python', '-m', 'email_cli', 'send',
        '--to', attendee['email'],
        '--subject', f"Event Confirmation: {event_name}",
        '--template', 'event_confirmation',
        '--context', json.dumps({
            'name': attendee['name'],
            'event': event_name,
            'date': details['date'],
            'location': details['location']
        })
    ], cwd='/root/clawd/clawdbot-smtp')
```

## Error Handling

```python
import subprocess
import json

def safe_email_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            cwd='/root/clawd/clawdbot-smtp',
            capture_output=True,
            text=True,
            timeout=30
        )

        if '--json' in cmd:
            return json.loads(result.stdout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return {'error': 'Command timed out'}
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON response'}
    except Exception as e:
        return {'error': str(e)}
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables or `.env` files
2. **Use app-specific passwords** - For Gmail, 2FA + app password is required
3. **Limit file permissions** - `chmod 600 config.json`
4. **Audit access logs** - Monitor who's sending emails
5. **Rate limiting** - Don't send too many emails too quickly

## Troubleshooting

### Authentication Failures

- Gmail: Enable 2FA and create app-specific password
- Outlook: Check "Allow less secure apps" or use OAuth
- Custom SMTP: Verify credentials and SSL/TLS settings

### Connection Issues

```bash
# Test SMTP connection
python -m email_cli send --to yourself@example.com --subject Test --body "Test"

# Test IMAP connection
python -m email_cli list --limit 1
```

### Template Not Found

```bash
# List available templates
ls email_cli/templates/

# Check template syntax
python -c "from email_cli.utils import render_template; print(render_template('welcome', {'name': 'Test'}))"
```

## Example Skills Integration

Create a skill that uses email_cli:

```yaml
# skills/email-notifications/SKILL.md
---
name: email-notifications
description: Send email notifications using email_cli. Use when the user needs to send automated emails, reports, or notifications.
---

# Email Notifications

## Quick Start

Send an email:
```bash
cd /root/clawd/clawdbot-smtp
python -m email_cli send --to user@example.com --subject "Subject" --body "Message"
```

## Templates

Use templates for consistent emails:
- `welcome` - Welcome emails for new users
- `event_confirmation` - Event registration confirmations
- `report` - Automated reports

## Example

Send welcome email:
```python
import subprocess
import json

subprocess.run([
    'python', '-m', 'email_cli', 'send',
    '--to', 'new-user@example.com',
    '--subject', 'Welcome!',
    '--template', 'welcome',
    '--context', json.dumps({'name': 'Alice', 'company': 'My Company'})
], cwd='/root/clawd/clawdbot-smtp')
```
```
