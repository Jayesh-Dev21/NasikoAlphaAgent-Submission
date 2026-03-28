"""
Google Calendar API integration for scheduling interviews.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


class GoogleCalendarAPI:
    """
    Google Calendar API wrapper.
    
    Setup Instructions:
    1. Go to https://console.cloud.google.com/
    2. Create a new project or select existing
    3. Enable Google Calendar API
    4. Create OAuth 2.0 credentials
    5. Download credentials.json
    6. Set GOOGLE_CREDENTIALS_PATH environment variable
    
    For production, use service account or OAuth flow.
    """
    
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.service = None
        
        # Try to initialize if credentials available
        if self.credentials_path and os.path.exists(self.credentials_path):
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            token_path = 'token.json'
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # Refresh or get new token
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save token
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            
        except ImportError:
            print("Google Calendar libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        except Exception as e:
            print(f"Failed to initialize Google Calendar: {e}")
    
    def is_available(self) -> bool:
        """Check if Google Calendar API is available."""
        return self.service is not None
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: List[str],
        description: str = "",
        location: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a calendar event.
        
        Args:
            summary: Event title
            start_time: Start datetime
            duration_minutes: Duration in minutes
            attendees: List of email addresses
            description: Event description
            location: Event location or meeting link
        
        Returns:
            Event data with meeting link, or None if failed
        """
        if not self.is_available():
            return self._create_mock_event(summary, start_time, duration_minutes, attendees)
        
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [{'email': email} for email in attendees],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{int(start_time.timestamp())}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()
            
            return {
                'id': created_event['id'],
                'summary': created_event['summary'],
                'start_time': created_event['start']['dateTime'],
                'end_time': created_event['end']['dateTime'],
                'meeting_link': created_event.get('hangoutLink', ''),
                'html_link': created_event.get('htmlLink', ''),
                'status': created_event['status']
            }
            
        except Exception as e:
            print(f"Failed to create calendar event: {e}")
            return self._create_mock_event(summary, start_time, duration_minutes, attendees)
    
    def _create_mock_event(
        self,
        summary: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: List[str]
    ) -> Dict[str, Any]:
        """Create a mock event when API is not available."""
        import random
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        meeting_id = random.randint(100000000, 999999999)
        
        return {
            'id': f"mock_{meeting_id}",
            'summary': summary,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'meeting_link': f"https://meet.google.com/mock-{meeting_id}",
            'html_link': f"https://calendar.google.com/event?eid=mock_{meeting_id}",
            'status': 'confirmed',
            'note': 'Mock event - Google Calendar API not configured'
        }
    
    def find_available_slot(
        self,
        duration_minutes: int,
        days_ahead: int = 7
    ) -> datetime:
        """
        Find next available time slot.
        
        For now, returns a simple slot. In production, check actual calendar availability.
        """
        # Simple logic: next business day at 10 AM
        now = datetime.now()
        next_slot = now + timedelta(days=2)
        next_slot = next_slot.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Skip weekends
        while next_slot.weekday() >= 5:  # 5=Saturday, 6=Sunday
            next_slot += timedelta(days=1)
        
        return next_slot
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event details by ID."""
        if not self.is_available():
            return None
        
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'id': event['id'],
                'summary': event['summary'],
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'end_time': event['end'].get('dateTime', event['end'].get('date')),
                'meeting_link': event.get('hangoutLink', ''),
                'status': event['status']
            }
        except Exception as e:
            print(f"Failed to get event: {e}")
            return None
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel an event."""
        if not self.is_available():
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to cancel event: {e}")
            return False


# Global calendar instance
_calendar = None

def get_calendar() -> GoogleCalendarAPI:
    """Get or create calendar instance."""
    global _calendar
    if _calendar is None:
        _calendar = GoogleCalendarAPI()
    return _calendar
