# Message Presets and Recipients Guide

This guide explains how to use message presets and recipient groups for quick email sending.

## Overview

Message presets and recipient groups allow you to:
- Save frequently used email templates in your config file
- Define groups of recipients for quick bulk emails
- Use Jinja2 variables for dynamic content
- Avoid typing the same email repeatedly

## Configuration

Add these sections to your `config.json`:

```json
{
  "accounts": { ... },
  "default_account": "primary",

  "message_presets": {
    "welcome": {
      "subject": "Welcome to {{ company }}!",
      "body": "Hi {{ name }},\n\nWelcome to {{ company }}! We're excited to have you on board."
    },
    "meeting_reminder": {
      "subject": "Reminder: {{ meeting_title }}",
      "body": "Hi {{ name }},\n\nMeeting: {{ meeting_title }}\nDate: {{ date }}\nTime: {{ time }}"
    }
  },

  "recipients": {
    "team": ["alice@company.com", "bob@company.com"],
    "managers": ["manager1@company.com", "manager2@company.com"]
  }
}
```

## Using Message Presets

### List Available Presets

```bash
clawdbot-smtp presets list
```

Output:
```
Available Presets:

• welcome
    Subject: Welcome to {{ company }}!

• meeting_reminder
    Subject: Reminder: {{ meeting_title }}
```

### View Preset Details

```bash
clawdbot-smtp presets show --name welcome
```

### Send Using a Preset

```bash
# Simple preset with context
clawdbot-smtp send \
  --to user@example.com \
  --preset welcome \
  --context '{"name": "John", "company": "MyCorp"}'

# Override preset subject
clawdbot-smtp send \
  --to user@example.com \
  --subject "Welcome Aboard!" \
  --preset welcome \
  --context '{"name": "John", "company": "MyCorp"}'
```

## Using Recipient Groups

### List Available Groups

```bash
clawdbot-smtp recipients list
```

Output:
```
Available Groups:

• team (2 recipients)
    - alice@company.com
    - bob@company.com

• managers (2 recipients)
    - manager1@company.com
    - manager2@company.com
```

### Send to a Group

```bash
# Send to first recipient in group
clawdbot-smtp send \
  --to team \
  --subject "Team Update" \
  --body "Here's the latest update"

# First recipient is in TO, rest are CC'd automatically
```

## Advanced Usage

### Combining Presets and Groups

```bash
clawdbot-smtp send \
  --to team \
  --preset meeting_reminder \
  --context '{
    "name": "Team",
    "meeting_title": "Weekly Standup",
    "date": "2024-01-30",
    "time": "10:00 AM"
  }'
```

### Multiple Presets

Create multiple presets for different scenarios:

```json
{
  "message_presets": {
    "daily_report": {
      "subject": "Daily Report - {{ date }}",
      "body": "## Completed\n{{ tasks_done }}\n\n## In Progress\n{{ tasks_in_progress }}"
    },
    "invoice_sent": {
      "subject": "Invoice #{{ invoice_number }}",
      "body": "Dear {{ client_name }},\n\nInvoice #{{ invoice_number }} has been sent.\n\nAmount: {{ amount }}"
    },
    "follow_up": {
      "subject": "Following up: {{ context }}",
      "body": "Hi {{ name }},\n\nJust following up on {{ context }}.\n\nBest,\n{{ my_name }}"
    }
  }
}
```

### Default CC/BCC

Configure default CC/BCC recipients:

```json
{
  "settings": {
    "default_cc": ["archive@company.com"],
    "default_bcc": ["backup@company.com"]
  }
}
```

All emails will automatically include these recipients.

## Examples

### 1. Welcome Email for New Employee

**Config:**
```json
{
  "message_presets": {
    "new_employee": {
      "subject": "Welcome to {{ company }}!",
      "body": "Hi {{ name }},\n\nWelcome to the team!\n\nYour first day is {{ start_date }}.\n\nPlease bring:\n- ID\n- Laptop\n- Signed documents\n\nSee you at {{ time }}!\n\nBest,\n{{ manager_name }}"
    }
  }
}
```

**Command:**
```bash
clawdbot-smtp send \
  --to new-hire@company.com \
  --preset new_employee \
  --context '{
    "name": "Alice",
    "company": "TechCorp",
    "start_date": "2024-02-01",
    "time": "9:00 AM",
    "manager_name": "Bob"
  }'
```

### 2. Weekly Team Update

**Config:**
```json
{
  "message_presets": {
    "weekly_update": {
      "subject": "Weekly Update - Week {{ week_number }}",
      "body": "## Weekly Update\n\n### Highlights\n{{ highlights }}\n\n### Completed\n{{ completed }}\n\n### Next Week\n{{ next_week }}"
    }
  }
}
```

**Command:**
```bash
clawdbot-smtp send \
  --to team \
  --preset weekly_update \
  --context '{
    "week_number": "4",
    "highlights": "Launched new feature\nFixed critical bugs",
    "completed": "Feature A, Feature B",
    "next_week": "Start Feature C"
  }'
```

### 3. Invoice Notification

**Config:**
```json
{
  "message_presets": {
    "invoice_notification": {
      "subject": "Invoice #{{ invoice_id }} - {{ client_name }}",
      "body": "Hi {{ client_contact }},\n\nInvoice #{{ invoice_id }} for {{ amount }} has been sent.\n\nDue Date: {{ due_date }}\n\nPlease find the invoice attached.\n\nThank you for your business!\n\nBest regards,\n{{ company_name }}"
    }
  }
}
```

**Command:**
```bash
clawdbot-smtp send \
  --to client@example.com \
  --preset invoice_notification \
  --attach invoice.pdf \
  --context '{
    "invoice_id": "INV-2024-001",
    "client_name": "Acme Corp",
    "client_contact": "John Doe",
    "amount": "$5,000",
    "due_date": "2024-02-15",
    "company_name": "MyCompany"
  }'
```

## Best Practices

1. **Use meaningful preset names** - `welcome` instead of `email1`
2. **Document your variables** - Keep a list of required variables for each preset
3. **Test before bulk sending** - Send to yourself first
4. **Use groups carefully** - Large groups may trigger spam filters
5. **Keep presets updated** - Review and update regularly
6. **Use JSON context** - Pass complex data as JSON for easier management

## Creating New Presets

1. Edit your config file:
```bash
sudo nano /etc/clawdbot-smtp/config.json
```

2. Add to `message_presets` section:
```json
{
  "message_presets": {
    "my_preset": {
      "subject": "Your Subject Here",
      "body": "Your email body here with {{ variables }}"
    }
  }
}
```

3. List presets to verify:
```bash
clawdbot-smtp presets list
```

4. Test it:
```bash
clawdbot-smtp send \
  --to yourself@example.com \
  --preset my_preset \
  --context '{"variable": "value"}'
```

## Integration with Clawdbot

```bash
# From Clawdbot - send preset notification
clawdbot-smtp send \
  --to team \
  --preset meeting_reminder \
  --context '{
    "name": "Team",
    "meeting_title": "Emergency Meeting",
    "date": "2024-01-29",
    "time": "3:00 PM"
  }'

# JSON output for parsing
clawdbot-smtp send \
  --to user@example.com \
  --preset welcome \
  --context '{"name": "User", "company": "Corp"}' \
  --json
```

## Troubleshooting

### Preset Not Found

Check the preset name matches exactly:
```bash
clawdbot-smtp presets list
```

### Variables Not Replaced

Ensure you're using `--context` with proper JSON:
```bash
# Correct
--context '{"name": "John"}'

# Wrong
--context "name: John"
```

### Group Not Found

List groups to check:
```bash
clawdbot-smtp recipients list
```
