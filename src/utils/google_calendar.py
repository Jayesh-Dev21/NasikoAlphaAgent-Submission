"""
Google Calendar utilities for scheduling and event management.

Uses Google Calendar API with OAuth 2.0 authentication.
Includes mock implementation for development.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

# Try to import Google API libraries
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    logger.warning("⚠️  Google API libraries not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarClient:
    """
    Google Calendar client for event management.
    
    Setup:
    1. Enable Google Calendar API in Google Cloud Console
    2. Download credentials.json and place in credentials/
    3. On first run, will open browser for OAuth consent
    4. Token will be saved to credentials/calendar_token.json
    
    Falls back to mock mode if credentials not available.
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize Google Calendar client.
        
        Args:
            use_mock: If True, use mock mode (in-memory events only)
        """
        self.use_mock = use_mock or not CALENDAR_AVAILABLE
        self.service = None
        self.credentials = None
        self.mock_events = {}  # For mock mode
        
        if not self.use_mock:
            self._authenticate()
        else:
            logger.info("ℹ️  Using mock Google Calendar client (events stored in memory)")
    
    def _authenticate(self):
        """Authenticate with Google Calendar API using OAuth 2.0."""
        creds = None
        token_path = 'credentials/calendar_token.json'
        creds_path = 'credentials/calendar_credentials.json'
        
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
            self.service = build('calendar', 'v3', credentials=creds)
            self.credentials = creds
            logger.info("✅ Google Calendar client authenticated")
        except Exception as e:
            logger.error(f"Failed to build Calendar service: {e}")
            logger.info("Falling back to mock mode")
            self.use_mock = True
    
    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None,
        add_meet_link: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create a calendar event.
        
        Args:
            title: Event title
            start_time: Start time (ISO 8601 format, e.g., '2024-03-15T10:00:00')
            end_time: End time (ISO 8601 format)
            description: Event description
            attendees: List of attendee email addresses
            location: Event location
            add_meet_link: If True, add Google Meet link
        
        Returns:
            Created event data or None if failed
        """
        # Mock mode
        if self.use_mock:
            event_id = str(uuid.uuid4())
            event = {
                'id': event_id,
                'summary': title,
                'start': {'dateTime': start_time},
                'end': {'dateTime': end_time},
                'description': description or '',
                'location': location or '',
                'attendees': [{'email': email} for email in (attendees or [])],
                'hangoutLink': f"https://meet.google.com/{event_id[:10]}" if add_meet_link else None,
                'htmlLink': f"https://calendar.google.com/event/{event_id}"
            }
            self.mock_events[event_id] = event
            
            logger.info("=" * 60)
            logger.info("📅 MOCK CALENDAR EVENT CREATED")
            logger.info(f"Title: {title}")
            logger.info(f"Start: {start_time}")
            logger.info(f"End: {end_time}")
            if attendees:
                logger.info(f"Attendees: {', '.join(attendees)}")
            if add_meet_link:
                logger.info(f"Meet Link: {event['hangoutLink']}")
            logger.info("=" * 60)
            
            return event
        
        # Real mode
        try:
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            if add_meet_link:
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': str(uuid.uuid4()),
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1 if add_meet_link else 0
            ).execute()
            
            logger.info(f"✅ Calendar event created: {created_event.get('id')}")
            return created_event
        
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return None
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get event by ID.
        
        Args:
            event_id: Event ID
        
        Returns:
            Event data or None
        """
        if self.use_mock:
            return self.mock_events.get(event_id)
        
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return event
        
        except HttpError as e:
            logger.error(f"Failed to get event: {e}")
            return None
    
    def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List upcoming events.
        
        Args:
            time_min: Start time filter (ISO 8601)
            time_max: End time filter (ISO 8601)
            max_results: Maximum number of events to return
        
        Returns:
            List of events
        """
        if self.use_mock:
            return list(self.mock_events.values())[:max_results]
        
        try:
            # Default to now if no time_min
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
        
        except HttpError as e:
            logger.error(f"Failed to list events: {e}")
            return []
    
    def find_available_slots(
        self,
        duration_minutes: int = 60,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        working_hours_start: int = 9,
        working_hours_end: int = 17
    ) -> List[Dict[str, str]]:
        """
        Find available time slots in calendar.
        
        Args:
            duration_minutes: Required duration in minutes
            start_date: Start date for search (ISO format, defaults to today)
            end_date: End date for search (ISO format, defaults to 7 days from now)
            working_hours_start: Start of working hours (hour, 0-23)
            working_hours_end: End of working hours (hour, 0-23)
        
        Returns:
            List of available slots with start_time and end_time
        """
        # Parse dates
        if not start_date:
            start_dt = datetime.utcnow()
        else:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        if not end_date:
            end_dt = start_dt + timedelta(days=7)
        else:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get existing events
        existing_events = self.list_events(
            time_min=start_dt.isoformat() + 'Z',
            time_max=end_dt.isoformat() + 'Z',
            max_results=100
        )
        
        # Find gaps
        available_slots = []
        current_dt = start_dt
        
        while current_dt < end_dt and len(available_slots) < 10:
            # Check if within working hours
            if current_dt.hour >= working_hours_start and current_dt.hour < working_hours_end:
                slot_end = current_dt + timedelta(minutes=duration_minutes)
                
                # Check for conflicts
                has_conflict = False
                for event in existing_events:
                    event_start = datetime.fromisoformat(
                        event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00')
                    )
                    event_end = datetime.fromisoformat(
                        event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00')
                    )
                    
                    # Check overlap
                    if not (slot_end <= event_start or current_dt >= event_end):
                        has_conflict = True
                        break
                
                if not has_conflict:
                    available_slots.append({
                        'start_time': current_dt.isoformat(),
                        'end_time': slot_end.isoformat()
                    })
            
            # Move to next slot (30-minute increments)
            current_dt += timedelta(minutes=30)
        
        logger.info(f"Found {len(available_slots)} available slots")
        return available_slots
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event.
        
        Args:
            event_id: Event ID
        
        Returns:
            True if deleted successfully
        """
        if self.use_mock:
            if event_id in self.mock_events:
                del self.mock_events[event_id]
                logger.info(f"🗑️  MOCK EVENT DELETED: {event_id}")
                return True
            return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"✅ Event deleted: {event_id}")
            return True
        
        except HttpError as e:
            logger.error(f"Failed to delete event: {e}")
            return False


# Global instance (singleton)
_calendar_client = None


def get_calendar_client(use_mock: bool = False) -> GoogleCalendarClient:
    """
    Get or create Google Calendar client instance (singleton).
    
    Args:
        use_mock: If True, use mock mode
    
    Returns:
        GoogleCalendarClient instance
    """
    global _calendar_client
    
    if _calendar_client is None:
        # Check environment variable
        use_mock_env = os.getenv("USE_MOCK_CALENDAR", "true").lower() == "true"
        _calendar_client = GoogleCalendarClient(use_mock=use_mock or use_mock_env)
    
    return _calendar_client
