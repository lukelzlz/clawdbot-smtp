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
@click.option('--to', '-t', help='Recipient email address (or group name)')
@click.option('--subject', '-s', help='Email subject')
@click.option('--body', '-b', help='Plain text body')
@click.option('--html', help='HTML body')
@click.option('--template', help='Template name (in templates/)')
@click.option('--preset', '-p', help='Use message preset from config')
@click.option('--context', '-c', help='JSON context for template/preset')
@click.option('--cc', multiple=True, help='CC recipients (can use multiple times)')
@click.option('--bcc', multiple=True, help='BCC recipients (can use multiple times)')
@click.option('--attach', multiple=True, help='Attachments (can use multiple times)')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def send(account, to, subject, body, html, template, preset, context, cc, bcc, attach, as_json):
    """Send an email."""
    config = Config()
    account_config = config.get_account(account)
    smtp = SMTPClient(account_config)
    settings = config.get_settings()

    # Load defaults from settings
    default_cc = settings.get('default_cc', [])
    default_bcc = settings.get('default_bcc', [])

    # Merge CC/BCC with defaults
    final_cc = list(set(list(cc) + default_cc))
    final_bcc = list(set(list(bcc) + default_bcc))

    # Resolve recipient groups
    if to and '@' not in to:
        # It's a group name, not an email address
        recipients = config.get_recipients(to)
        if recipients:
            if len(recipients) == 1:
                to = recipients[0]
            else:
                # Multiple recipients, use first as TO, rest as CC
                to = recipients[0]
                final_cc.extend(recipients[1:])
        else:
            click.echo(f"Warning: Recipient group '{to}' not found", err=True)

    # Handle preset
    if preset:
        preset_data = config.get_message_preset(preset)
        if not preset_data:
            click.echo(f"Error: Preset '{preset}' not found in config", err=True)
            return

        # Use preset subject/body if not provided
        if not subject:
            subject = preset_data.get('subject', '')
        if not body and not html:
            body = preset_data.get('body', '')

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
                cc=final_cc,
                bcc=final_bcc,
                attachments=list(attach) if attach else None
            )
        except Exception as e:
            result = {'success': False, 'error': str(e)}
    else:
        # Handle context for subject/body (Jinja2 rendering)
        if context:
            try:
                from jinja2 import Template
                ctx = parse_context(context)

                if subject:
                    template_obj = Template(subject)
                    subject = template_obj.render(**ctx)

                if body:
                    template_obj = Template(body)
                    body = template_obj.render(**ctx)
            except Exception as e:
                click.echo(f"Error rendering context: {e}", err=True)
                return

        # Regular email
        if not body and not html:
            body = ''  # Empty body allowed
        result = smtp.send_email(
            to=to,
            subject=subject,
            body=body,
            html=html,
            cc=final_cc,
            bcc=final_bcc,
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


@cli.group()
def presets():
    """Manage message presets."""
    pass


@presets.command(name='list')
@click.option('--account', '-a', help='Account name from config')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def list_presets(account, as_json):
    """List all message presets."""
    config = Config()
    presets = config.get_all_presets()

    result = {
        'presets': list(presets.keys()),
        'total': len(presets)
    }

    if as_json:
        click.echo(format_json_output(result))
    else:
        from colorama import Fore, Style

        if result['total'] == 0:
            click.echo("No presets found in config")
            return

        output = f"\n{Fore.CYAN}Available Presets:{Style.RESET_ALL}\n\n"
        for name, preset in presets.items():
            output += f"  {Fore.GREEN}•{Style.RESET_ALL} {name}\n"
            output += f"    Subject: {preset.get('subject', 'N/A')}\n\n"

        click.echo(output)


@presets.command()
@click.option('--account', '-a', help='Account name from config')
@click.option('--name', '-n', required=True, help='Preset name')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def show(account, name, as_json):
    """Show details of a specific preset."""
    config = Config()
    preset = config.get_message_preset(name)

    result = {
        'name': name,
        'preset': preset
    }

    if as_json:
        click.echo(format_json_output(result))
    else:
        from colorama import Fore, Style

        if not preset:
            click.echo(f"{Fore.RED}Preset '{name}' not found{Style.RESET_ALL}", err=True)
            return

        output = f"\n{Fore.CYAN}Preset: {name}{Style.RESET_ALL}\n\n"
        output += f"{Fore.YELLOW}Subject:{Style.RESET_ALL}\n{preset.get('subject', 'N/A')}\n\n"
        output += f"{Fore.YELLOW}Body:{Style.RESET_ALL}\n{preset.get('body', 'N/A')}\n"
        click.echo(output)


@cli.group()
def recipients():
    """Manage recipient groups."""
    pass


@recipients.command(name='list')
@click.option('--account', '-a', help='Account name from config')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def list_recipients(account, as_json):
    """List all recipient groups."""
    config = Config()
    recipients = config.config.get('recipients', {})

    result = {
        'groups': list(recipients.keys()),
        'total': len(recipients)
    }

    if as_json:
        click.echo(format_json_output(result))
    else:
        from colorama import Fore, Style

        if result['total'] == 0:
            click.echo("No recipient groups found in config")
            return

        output = f"\n{Fore.CYAN}Available Groups:{Style.RESET_ALL}\n\n"
        for name, group in recipients.items():
            output += f"  {Fore.GREEN}•{Style.RESET_ALL} {name} ({len(group)} recipients)\n"
            for email in group:
                output += f"    - {email}\n"
            output += "\n"

        click.echo(output)


if __name__ == '__main__':
    cli()
