#!/usr/bin/env python3
"""
Email checker for Clawdbot cron integration.
Checks for unread emails and sends notification summary.
"""

import subprocess
import json
import os
import sys


def check_emails(limit: int = 10, folder: str = 'INBOX') -> dict:
    """Check for unread emails."""
    # Change to email_cli directory
    email_cli_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(email_cli_dir)

    # Run list command for unread emails
    result = subprocess.run([
        'python', '-m', 'email_cli', 'list',
        '--folder', folder,
        '--unread',
        '--limit', str(limit),
        '--json'
    ], capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        return {
            'success': False,
            'error': result.stderr
        }

    return json.loads(result.stdout)


def format_summary(emails: dict) -> str:
    """Format email summary for notification."""
    total = emails.get('total', 0)

    if total == 0:
        return "📬 No new unread emails."

    summary = f"📬 You have **{total} unread email(s)** in {emails['folder']}:\n\n"

    for idx, email in enumerate(emails['emails'], 1):
        from_name = email.get('from', 'Unknown').split('<')[0].strip()
        subject = email.get('subject', 'No Subject')

        # Truncate long subjects
        if len(subject) > 50:
            subject = subject[:47] + '...'

        summary += f"{idx}. From: **{from_name}**\n"
        summary += f"   Subject: {subject}\n"
        summary += f"   Date: {email.get('date', 'Unknown')}\n\n"

    return summary


def main():
    """Main function."""
    try:
        # Parse arguments
        limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        folder = sys.argv[2] if len(sys.argv) > 2 else 'INBOX'

        # Check emails
        emails = check_emails(limit=limit, folder=folder)

        if not emails.get('success', True):
            print(f"Error checking emails: {emails.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

        # Format and output summary
        summary = format_summary(emails)
        print(summary)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
