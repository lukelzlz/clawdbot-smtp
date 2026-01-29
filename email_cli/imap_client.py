"""IMAP client for managing emails."""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional
import json


class IMAPClient:
    """IMAP client for managing emails."""

    def __init__(self, account: Dict[str, Any]):
        self.host = account['imap_host']
        self.port = account['imap_port']
        self.username = account['username']
        self.password = account['password']
        self.use_ssl = account.get('use_ssl', True)

    def connect(self):
        """Connect to IMAP server."""
        if self.use_ssl:
            server = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            server = imaplib.IMAP4(self.host, self.port)

        server.login(self.username, self.password)
        return server

    def list_emails(
        self,
        folder: str = 'INBOX',
        limit: int = 10,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """List emails in folder."""
        result = {
            'folder': folder,
            'total': 0,
            'emails': []
        }

        try:
            with self.connect() as server:
                server.select(folder)

                # Build search criteria
                criteria = 'UNSEEN' if unread_only else 'ALL'

                # Search for emails
                status, messages = server.search(None, criteria)

                if status != 'OK':
                    result['error'] = f"Search failed: {status}"
                    return result

                # Get message IDs
                email_ids = messages[0].split()
                result['total'] = len(email_ids)

                # Fetch limited emails
                for idx, email_id in enumerate(email_ids[-limit:]):
                    email_data = self._fetch_email(server, email_id)
                    result['emails'].append(email_data)

        except Exception as e:
            result['error'] = str(e)

        return result

    def read_email(self, folder: str, email_id: str) -> Dict[str, Any]:
        """Read a specific email."""
        result = {
            'folder': folder,
            'email_id': email_id,
            'success': False,
            'error': None
        }

        try:
            with self.connect() as server:
                server.select(folder)
                email_data = self._fetch_email(server, email_id)
                result['email'] = email_data
                result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def search_emails(
        self,
        folder: str = 'INBOX',
        query: str = '',
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search emails with IMAP query."""
        result = {
            'folder': folder,
            'query': query,
            'total': 0,
            'emails': []
        }

        try:
            with self.connect() as server:
                server.select(folder)

                # Search with query
                status, messages = server.search(None, query)

                if status != 'OK':
                    result['error'] = f"Search failed: {status}"
                    return result

                email_ids = messages[0].split()
                result['total'] = len(email_ids)

                # Fetch limited emails
                for idx, email_id in enumerate(email_ids[-limit:]):
                    email_data = self._fetch_email(server, email_id)
                    result['emails'].append(email_data)

        except Exception as e:
            result['error'] = str(e)

        return result

    def delete_email(self, folder: str, email_id: str) -> Dict[str, Any]:
        """Delete an email."""
        result = {
            'folder': folder,
            'email_id': email_id,
            'success': False,
            'error': None
        }

        try:
            with self.connect() as server:
                server.select(folder)

                # Mark for deletion
                server.store(email_id, '+FLAGS', '\\Deleted')

                # Expunge to permanently delete
                server.expunge()

                result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def list_folders(self) -> Dict[str, Any]:
        """List all folders."""
        result = {
            'folders': [],
            'error': None
        }

        try:
            with self.connect() as server:
                status, folders = server.list()

                if status == 'OK':
                    for folder in folders:
                        # Parse folder name (it's in a weird format)
                        folder_data = folder.decode()
                        parts = folder_data.split('"')
                        if len(parts) >= 3:
                            folder_name = parts[-2] if parts[-2] else parts[-3]
                            result['folders'].append(folder_name)

        except Exception as e:
            result['error'] = str(e)

        return result

    def create_folder(self, folder_name: str) -> Dict[str, Any]:
        """Create a new folder."""
        result = {
            'folder': folder_name,
            'success': False,
            'error': None
        }

        try:
            with self.connect() as server:
                server.create(folder_name)
                result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def _fetch_email(self, server: imaplib.IMAP4, email_id: str) -> Dict[str, Any]:
        """Fetch and parse an email."""
        # Fetch email
        status, msg_data = server.fetch(email_id, '(RFC822)')

        if status != 'OK':
            return {
                'id': email_id,
                'error': f"Fetch failed: {status}"
            }

        # Parse email
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Extract email data
        email_data = {
            'id': email_id,
            'from': self._decode_header(email_message['From']),
            'to': self._decode_header(email_message['To']),
            'subject': self._decode_header(email_message['Subject']),
            'date': email_message['Date'],
            'body': '',
            'attachments': []
        }

        # Extract body and attachments
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    # It's an attachment
                    filename = part.get_filename()
                    if filename:
                        email_data['attachments'].append(self._decode_header(filename))
                elif content_type == "text/plain":
                    # Plain text body
                    try:
                        body = part.get_payload(decode=True)
                        email_data['body'] = body.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html":
                    # HTML body (if no plain text found)
                    if not email_data['body']:
                        try:
                            body = part.get_payload(decode=True)
                            import re
                            text = re.sub('<[^<]+?>', '', body.decode('utf-8', errors='ignore'))
                            email_data['body'] = text.strip()
                        except:
                            pass
        else:
            # Single part message
            try:
                body = email_message.get_payload(decode=True)
                email_data['body'] = body.decode('utf-8', errors='ignore')
            except:
                pass

        return email_data

    def _decode_header(self, header: Optional[str]) -> str:
        """Decode email header."""
        if not header:
            return ''

        decoded = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                try:
                    decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
                except:
                    decoded.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded.append(part)

        return ''.join(decoded)
