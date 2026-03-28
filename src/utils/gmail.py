"""
Gmail utilities for sending emails and notifications.

Uses Google Gmail API with OAuth 2.0 authentication.
Includes mock implementation for development.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import os
import logging
import base64
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Try to import Google API libraries
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logger.warning("⚠️  Google API libraries not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailClient:
    """
    Gmail client for sending emails.
    
    Setup:
    1. Enable Gmail API in Google Cloud Console
    2. Download credentials.json and place in credentials/
    3. On first run, will open browser for OAuth consent
    4. Token will be saved to credentials/gmail_token.json
    
    Falls back to mock mode if credentials not available.
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize Gmail client.
        
        Args:
            use_mock: If True, use mock mode (console output only)
        """
        self.use_mock = use_mock or not GMAIL_AVAILABLE
        self.service = None
        self.credentials = None
        
        if not self.use_mock:
            self._authenticate()
        else:
            logger.info("ℹ️  Using mock Gmail client (emails will be logged, not sent)")
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0."""
        creds = None
        token_path = 'credentials/gmail_token.json'
        creds_path = 'credentials/gmail_credentials.json'
        
        # Check if token exists
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}")
                    creds = None
            
            if not creds:
                if os.path.exists(creds_path):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        logger.error(f"Failed to authenticate: {e}")
                        logger.info("Falling back to mock mode")
                        self.use_mock = True
                        return
                else:
                    logger.warning(f"Credentials file not found: {creds_path}")
                    logger.info("Falling back to mock mode")
                    self.use_mock = True
                    return
            
            # Save token
            if creds:
                try:
                    os.makedirs('credentials', exist_ok=True)
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.warning(f"Failed to save token: {e}")
        
        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.credentials = creds
            logger.info("✅ Gmail client authenticated")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            logger.info("Falling back to mock mode")
            self.use_mock = True
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is treated as HTML
            cc: List of CC recipients
            bcc: List of BCC recipients
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Mock mode: just log
        if self.use_mock:
            logger.info("=" * 60)
            logger.info("📧 MOCK EMAIL")
            logger.info(f"To: {to}")
            if cc:
                logger.info(f"CC: {', '.join(cc)}")
            if bcc:
                logger.info(f"BCC: {', '.join(bcc)}")
            logger.info(f"Subject: {subject}")
            logger.info("-" * 60)
            logger.info(body)
            logger.info("=" * 60)
            return True
        
        # Real mode: send via Gmail API
        try:
            # Create message
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            if html:
                message.attach(MIMEText(body, 'html'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"✅ Email sent to {to}: {send_message['id']}")
            return True
        
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_ticket_notification(
        self,
        customer_email: str,
        ticket_id: str,
        subject: str,
        status: str = "open"
    ) -> bool:
        """
        Send ticket notification to customer.
        
        Args:
            customer_email: Customer's email
            ticket_id: Ticket ID
            subject: Ticket subject
            status: Ticket status
        
        Returns:
            True if sent successfully
        """
        body = f"""
Hello,

Your support ticket has been received.

Ticket ID: {ticket_id}
Subject: {subject}
Status: {status}

We will get back to you shortly.

Best regards,
Support Team
""".strip()
        
        return self.send_email(
            to=customer_email,
            subject=f"Support Ticket Created: {ticket_id}",
            body=body
        )
    
    def send_meeting_invitation(
        self,
        to: str,
        title: str,
        start_time: str,
        end_time: str,
        meeting_link: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Send meeting invitation email.
        
        Args:
            to: Attendee email
            title: Meeting title
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            meeting_link: Meeting link (Google Meet, Zoom, etc.)
            description: Optional meeting description
        
        Returns:
            True if sent successfully
        """
        body = f"""
You have been invited to a meeting:

Title: {title}
Start: {start_time}
End: {end_time}
Link: {meeting_link}
"""
        
        if description:
            body += f"\nDescription:\n{description}"
        
        body += "\n\nPlease mark your calendar."
        
        return self.send_email(
            to=to,
            subject=f"Meeting Invitation: {title}",
            body=body.strip()
        )
    
    def send_invoice_notification(
        self,
        to: str,
        invoice_number: str,
        amount: float,
        vendor: str,
        due_date: Optional[str] = None
    ) -> bool:
        """
        Send invoice notification.
        
        Args:
            to: Recipient email
            invoice_number: Invoice number
            amount: Total amount
            vendor: Vendor name
            due_date: Optional due date
        
        Returns:
            True if sent successfully
        """
        body = f"""
Invoice Processed:

Invoice Number: {invoice_number}
Vendor: {vendor}
Amount: ${amount:.2f}
"""
        
        if due_date:
            body += f"Due Date: {due_date}\n"
        
        body += "\nPlease review and approve."
        
        return self.send_email(
            to=to,
            subject=f"Invoice Processed: {invoice_number}",
            body=body.strip()
        )


# Global instance (singleton)
_gmail_client = None


def get_gmail_client(use_mock: bool = False) -> GmailClient:
    """
    Get or create Gmail client instance (singleton).
    
    Args:
        use_mock: If True, use mock mode
    
    Returns:
        GmailClient instance
    """
    global _gmail_client
    
    if _gmail_client is None:
        # Check environment variable
        use_mock_env = os.getenv("USE_MOCK_GMAIL", "true").lower() == "true"
        _gmail_client = GmailClient(use_mock=use_mock or use_mock_env)
    
    return _gmail_client
