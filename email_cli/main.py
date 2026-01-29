"""Main CLI entry point for email_cli."""

import click
import json
from .config import Config
from .smtp_client import SMTPClient
from .imap_client import IMAPClient
from .utils import render_template, parse_context, format_json_output, format_table_output


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Clawdbot SMTP/IMAP CLI Tool - Manage emails with templates."""
    pass


@cli.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--to', '-t', required=True, help='Recipient email address')
@click.option('--subject', '-s', required=True, help='Email subject')
@click.option('--body', '-b', help='Plain text body')
@click.option('--html', help='HTML body')
@click.option('--template', help='Template name (in templates/)')
@click.option('--context', '-c', help='JSON context for template')
@click.option('--cc', multiple=True, help='CC recipients (can use multiple times)')
@click.option('--bcc', multiple=True, help='BCC recipients (can use multiple times)')
@click.option('--attach', multiple=True, help='Attachments (can use multiple times)')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def send(account, to, subject, body, html, template, context, cc, bcc, attach, as_json):
    """Send an email."""
    config = Config()
    account_config = config.get_account(account)
    smtp = SMTPClient(account_config)

    # Validate inputs
    if template and body:
        click.echo("Error: Cannot specify both --template and --body", err=True)
        return

    # Handle template
    if template:
        if not context:
            click.echo("Error: --context required when using --template", err=True)
            return
        try:
            ctx = parse_context(context)
            result = smtp.send_template_email(
                to=to,
                subject=subject,
                template_name=template,
                context=ctx,
                cc=list(cc) if cc else None,
                bcc=list(bcc) if bcc else None,
                attachments=list(attach) if attach else None
            )
        except Exception as e:
            result = {'success': False, 'error': str(e)}
    else:
        # Regular email
        if not body and not html:
            body = ''  # Empty body allowed
        result = smtp.send_email(
            to=to,
            subject=subject,
            body=body,
            html=html,
            cc=list(cc) if cc else None,
            bcc=list(bcc) if bcc else None,
            attachments=list(attach) if attach else None
        )

    # Output
    if as_json:
        click.echo(format_json_output(result))
    else:
        output = format_table_output(result)
        click.echo(output)


@cli.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--folder', '-f', default='INBOX', help='Folder name')
@click.option('--limit', '-l', default=10, help='Number of emails to list')
@click.option('--unread', is_flag=True, help='Only show unread emails')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def list_emails(account, folder, limit, unread, as_json):
    """List emails in a folder."""
    config = Config()
    account_config = config.get_account(account)
    imap = IMAPClient(account_config)

    result = imap.list_emails(folder=folder, limit=limit, unread_only=unread)

    if as_json:
        click.echo(format_json_output(result))
    else:
        output = format_table_output(result)
        click.echo(output)


@cli.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--folder', '-f', default='INBOX', help='Folder name')
@click.option('--id', 'email_id', required=True, help='Email ID')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def read(account, folder, email_id, as_json):
    """Read a specific email."""
    config = Config()
    account_config = config.get_account(account)
    imap = IMAPClient(account_config)

    result = imap.read_email(folder=folder, email_id=email_id)

    if as_json:
        click.echo(format_json_output(result))
    else:
        from colorama import Fore, Style

        if result['success']:
            email = result['email']
            output = f"\n{Fore.CYAN}From:{Style.RESET_ALL} {email['from']}\n"
            output += f"{Fore.CYAN}To:{Style.RESET_ALL} {email['to']}\n"
            output += f"{Fore.CYAN}Subject:{Style.RESET_ALL} {email['subject']}\n"
            output += f"{Fore.CYAN}Date:{Style.RESET_ALL} {email['date']}\n"
            output += f"{Fore.CYAN}Attachments:{Style.RESET_ALL} {', '.join(email['attachments']) if email['attachments'] else 'None'}\n\n"
            output += f"{Fore.CYAN}Body:{Style.RESET_ALL}\n{email['body']}\n"
            click.echo(output)
        else:
            click.echo(format_table_output(result))


@cli.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--folder', '-f', default='INBOX', help='Folder name')
@click.option('--query', '-q', required=True, help='IMAP search query')
@click.option('--limit', '-l', default=10, help='Number of emails to return')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def search(account, folder, query, limit, as_json):
    """Search emails with IMAP query."""
    config = Config()
    account_config = config.get_account(account)
    imap = IMAPClient(account_config)

    result = imap.search_emails(folder=folder, query=query, limit=limit)

    if as_json:
        click.echo(format_json_output(result))
    else:
        output = format_table_output(result)
        click.echo(output)


@cli.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--folder', '-f', default='INBOX', help='Folder name')
@click.option('--id', 'email_id', required=True, help='Email ID')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def delete(account, folder, email_id, as_json, yes):
    """Delete an email."""
    if not yes:
        click.confirm(f'Delete email {email_id} from {folder}?', abort=True)

    config = Config()
    account_config = config.get_account(account)
    imap = IMAPClient(account_config)

    result = imap.delete_email(folder=folder, email_id=email_id)

    if as_json:
        click.echo(format_json_output(result))
    else:
        output = format_table_output(result)
        click.echo(output)


@cli.group()
def folders():
    """Manage email folders."""
    pass


@folders.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def list(account, as_json):
    """List all folders."""
    config = Config()
    account_config = config.get_account(account)
    imap = IMAPClient(account_config)

    result = imap.list_folders()

    if as_json:
        click.echo(format_json_output(result))
    else:
        output = format_table_output(result)
        click.echo(output)


@folders.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--name', '-n', required=True, help='Folder name')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def create(account, name, as_json):
    """Create a new folder."""
    config = Config()
    account_config = config.get_account(account)
    imap = IMAPClient(account_config)

    result = imap.create_folder(folder_name=name)

    if as_json:
        click.echo(format_json_output(result))
    else:
        output = format_table_output(result)
        click.echo(output)


if __name__ == '__main__':
    cli()
