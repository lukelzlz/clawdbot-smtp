"""SMTP client for sending emails."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import json


class SMTPClient:
    """SMTP client for sending emails."""

    def __init__(self, account: Dict[str, Any]):
        self.host = account['smtp_host']
        self.port = account['smtp_port']
        self.username = account['username']
        self.password = account['password']
        self.use_ssl = account.get('use_ssl', True)

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send an email."""
        result = {
            'success': False,
            'to': to,
            'subject': subject,
            'message_id': None,
            'error': None
        }

        try:
            # Create message
            msg = MIMEMultipart('alternative')

            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Add plain text body
            part1 = MIMEText(body, 'plain')
            msg.attach(part1)

            # Add HTML body if provided
            if html:
                part2 = MIMEText(html, 'html')
                msg.attach(part2)

            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    self._add_attachment(msg, attachment_path)

            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_ssl:
                    server.starttls()

                server.login(self.username, self.password)

                recipients = [to]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)

                server.send_message(msg, from_addr=self.username, to_addrs=recipients)

            result['success'] = True
            result['message_id'] = str(hash(f"{to}{subject}"))

        except Exception as e:
            result['error'] = str(e)

        return result

    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add attachment to email."""
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        filename = os.path.basename(file_path)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )

        msg.attach(part)

    def send_template_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send email from template."""
        from .utils import render_template

        html = render_template(template_name, context)
        plain_text = self._html_to_plain_text(html)

        return self.send_email(
            to=to,
            subject=subject,
            body=plain_text,
            html=html,
            cc=cc,
            bcc=bcc,
            attachments=attachments
        )

    def _html_to_plain_text(self, html: str) -> str:
        """Convert HTML to plain text (simple version)."""
        # Very basic HTML to text conversion
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = text.replace('&nbsp;', ' ')
        return text.strip()
