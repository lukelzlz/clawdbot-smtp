"""Configuration management for email_cli."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load .env file if exists
load_dotenv()


class Config:
    """Manage email configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.environ.get(
            'EMAIL_CONFIG',
            os.path.join(os.path.dirname(__file__), '../config.json')
        )
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables."""
        config = {}

        # Try to load from file
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # Use environment variables
            config = self._load_from_env()

        return config

    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {
            'accounts': {
                'primary': {
                    'smtp_host': os.environ.get('SMTP_HOST'),
                    'smtp_port': int(os.environ.get('SMTP_PORT', 587)),
                    'imap_host': os.environ.get('IMAP_HOST'),
                    'imap_port': int(os.environ.get('IMAP_PORT', 993)),
                    'username': os.environ.get('SMTP_USERNAME') or os.environ.get('IMAP_USERNAME'),
                    'password': os.environ.get('SMTP_PASSWORD') or os.environ.get('IMAP_PASSWORD'),
                    'use_ssl': os.environ.get('USE_SSL', 'true').lower() == 'true'
                }
            },
            'default_account': 'primary'
        }
        return config

    def get_account(self, account_name: Optional[str] = None) -> Dict[str, Any]:
        """Get account configuration."""
        if account_name is None:
            account_name = self.config.get('default_account', 'primary')

        accounts = self.config.get('accounts', {})
        if account_name not in accounts:
            raise ValueError(f"Account '{account_name}' not found in configuration")

        return accounts[account_name]

    def get_all_accounts(self) -> Dict[str, Any]:
        """Get all accounts."""
        return self.config.get('accounts', {})
