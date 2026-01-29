"""Utility functions for email_cli."""

import os
import json
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any


# Setup template environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True
)


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template with context."""
    try:
        template = env.get_template(template_name)
        return template.render(**context)
    except:
        # Try with .html extension
        try:
            template = env.get_template(f"{template_name}.html")
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"Template '{template_name}' not found or error rendering: {e}")


def parse_context(context_str: str) -> Dict[str, Any]:
    """Parse JSON context string."""
    try:
        return json.loads(context_str)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON context: {context_str}")


def format_json_output(data: Dict[str, Any], pretty: bool = True) -> str:
    """Format output as JSON."""
    indent = 2 if pretty else None
    return json.dumps(data, indent=indent, ensure_ascii=False)


def format_table_output(data: Any) -> str:
    """Format output as table (for human reading)."""
    from colorama import Fore, Style

    if isinstance(data, dict):
        if 'emails' in data:
            # Email list
            output = f"\n{Fore.CYAN}Folder: {data.get('folder', 'INBOX')}{Style.RESET_ALL}\n"
            output += f"{Fore.CYAN}Total: {data.get('total', 0)}{Style.RESET_ALL}\n\n"

            for idx, email in enumerate(data['emails'], 1):
                output += f"{Fore.GREEN}[{idx}]{Style.RESET_ALL} "
                output += f"{Fore.YELLOW}From:{Style.RESET_ALL} {email.get('from', 'Unknown')}\n"
                output += f"      {Fore.YELLOW}Subject:{Style.RESET_ALL} {email.get('subject', 'No Subject')}\n"
                output += f"      {Fore.YELLOW}Date:{Style.RESET_ALL} {email.get('date', 'Unknown')}\n\n"

            return output

        elif 'success' in data:
            # Operation result
            if data['success']:
                return f"{Fore.GREEN}✓ Success{Style.RESET_ALL}"
            else:
                return f"{Fore.RED}✗ Failed: {data.get('error', 'Unknown error')}{Style.RESET_ALL}"

        elif 'folders' in data:
            # Folder list
            output = f"\n{Fore.CYAN}Folders:{Style.RESET_ALL}\n"
            for folder in data['folders']:
                output += f"  {Fore.GREEN}•{Style.RESET_ALL} {folder}\n"
            return output

    # Default JSON-like pretty print
    return json.dumps(data, indent=2, ensure_ascii=False)
