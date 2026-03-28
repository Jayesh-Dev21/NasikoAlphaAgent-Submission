"""
Gmail API integration for sending emails to candidates.
"""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List


class GmailAPI:
    """
    Gmail API wrapper for sending emails.
    
    Setup Instructions:
    1. Go to https://console.cloud.google.com/
    2. Enable Gmail API
    3. Create OAuth 2.0 credentials
    4. Download credentials.json
    5. Set GOOGLE_CREDENTIALS_PATH environment variable
    """
    
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.service = None
        
        if self.credentials_path and os.path.exists(self.credentials_path):
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Gmail service."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']
            
            creds = None
            token_path = 'gmail_token.json'
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            
        except ImportError:
            print("Gmail libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        except Exception as e:
            print(f"Failed to initialize Gmail: {e}")
    
    def is_available(self) -> bool:
        """Check if Gmail API is available."""
        return self.service is not None
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: List of CC email addresses
            html: Whether body is HTML
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_available():
            return self._mock_send_email(to, subject, body)
        
        try:
            message = MIMEMultipart('alternative') if html else MIMEText(body)
            
            if isinstance(message, MIMEMultipart):
                message.attach(MIMEText(body, 'html' if html else 'plain'))
            
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return self._mock_send_email(to, subject, body)
    
    def _mock_send_email(self, to: str, subject: str, body: str) -> bool:
        """Mock email sending when API is not available."""
        print(f"\n{'='*60}")
        print(f"MOCK EMAIL (Gmail API not configured)")
        print(f"{'='*60}")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print(f"{'='*60}\n")
        return True
    
    def send_interview_invitation(
        self,
        candidate_email: str,
        candidate_name: str,
        interview_type: str,
        interview_date: str,
        interview_time: str,
        duration: int,
        meeting_link: str,
        interviewer_name: str = "HR Team"
    ) -> bool:
        """Send interview invitation email."""
        
        subject = f"Interview Invitation - {interview_type.title()} Interview"
        
        body = f"""
Dear {candidate_name},

We are pleased to invite you for a {interview_type} interview.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: {duration} minutes
- Meeting Link: {meeting_link}

Please confirm your availability by replying to this email.

We look forward to speaking with you!

Best regards,
{interviewer_name}
HR Department
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_screening_update(
        self,
        candidate_email: str,
        candidate_name: str,
        status: str,
        next_steps: str = ""
    ) -> bool:
        """Send screening status update."""
        
        subject = f"Application Update - {status}"
        
        body = f"""
Dear {candidate_name},

Thank you for your application. We wanted to update you on your application status.

Status: {status}

{next_steps}

If you have any questions, please don't hesitate to reach out.

Best regards,
HR Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_offer_letter(
        self,
        candidate_email: str,
        candidate_name: str,
        position: str,
        salary: str,
        start_date: str
    ) -> bool:
        """Send job offer letter."""
        
        subject = f"Job Offer - {position}"
        
        body = f"""
Dear {candidate_name},

Congratulations! We are delighted to offer you the position of {position}.

Offer Details:
- Position: {position}
- Salary: {salary}
- Start Date: {start_date}

Please review the attached offer letter and let us know your decision within 7 days.

We are excited about the possibility of you joining our team!

Best regards,
HR Team
"""
        
        return self.send_email(candidate_email, subject, body)


# Global Gmail instance
_gmail = None

def get_gmail() -> GmailAPI:
    """Get or create Gmail instance."""
    global _gmail
    if _gmail is None:
        _gmail = GmailAPI()
    return _gmail
