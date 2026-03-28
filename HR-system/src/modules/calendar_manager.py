"""
Calendar management module for scheduling meetings and interviews.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from core.base_module import BaseModule
from utils.google_calendar import get_calendar
from utils.gmail import get_gmail
from utils.database import get_database


class CalendarManager(BaseModule):
    """Manages scheduling of meetings, interviews, and events."""
    
    def __init__(self):
        super().__init__("calendar_manager")
        self.calendar_api = get_calendar()
        self.gmail_api = get_gmail()
        self.db = get_database()
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if this module can handle the task."""
        task_type = task.get("type", "")
        keywords = ["schedule", "meeting", "interview", "calendar", "appointment"]
        description = task.get("description", "").lower()
        
        return task_type == "schedule" or any(kw in description for kw in keywords)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scheduling task with real Google Calendar API."""
        params = task.get("params", {})
        description = task.get("description", "")
        
        # Extract scheduling parameters
        duration = params.get("duration", 60)
        meeting_type = params.get("type", "technical")
        candidate_name = params.get("candidate_name", "Candidate")
        candidate_email = params.get("candidate_email", "")

        # Auto-fetch email if missing
        if not candidate_email and candidate_name:
            candidate = self.db.get_candidate(candidate_name)
            if candidate:
                candidate_email = candidate.get("email", "")
        
        # NEW: Extract and parse the requested date_time if provided
        date_time_str = params.get("date_time", "")
        start_time = None
        
        if date_time_str:
            try:
                # Parse the ISO format string sent by the AI
                clean_date_str = date_time_str.replace('Z', '')
                start_time = datetime.fromisoformat(clean_date_str)
            except ValueError:
                print(f"⚠️ Could not parse requested time: {date_time_str}")
        
        # Fallback to finding an available slot if no valid time was requested
        if not start_time:
            start_time = self.calendar_api.find_available_slot(duration)
        
        # Create event title
        event_title = f"{meeting_type.title()} Interview - {candidate_name}"
        
        # Attendees list
        attendees =[]
        if candidate_email:
            attendees.append(candidate_email)
        
        # Add default interviewer email if configured
        interviewer_email = params.get("interviewer_email", "hr@company.com")
        attendees.append(interviewer_email)
        
        # Create calendar event (real API call or mock)
        event = self.calendar_api.create_event(
            summary=event_title,
            start_time=start_time,
            duration_minutes=duration,
            attendees=attendees,
            description=f"{meeting_type.title()} interview with {candidate_name}",
            location="Google Meet"
        )
        
        if not event:
            return {
                "success": False,
                "message": "Failed to create calendar event",
                "error": "Calendar API error"
            }
        
        # Store interview in database
        if candidate_email:
            candidate = self.db.get_candidate(candidate_email)
            if candidate:
                self.db.add_interview(candidate_email, {
                    "type": meeting_type,
                    "scheduled_at": event['start_time'],
                    "duration": duration,
                    "meeting_link": event['meeting_link'],
                    "status": "scheduled"
                })
        
        # Send email invitation to candidate
        print("Candidate email:", candidate_email)
        print("Gmail available:", self.gmail_api.is_available())
        if candidate_email and self.gmail_api.is_available():
            self.gmail_api.send_interview_invitation(
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                interview_type=meeting_type,
                interview_date=start_time.strftime("%B %d, %Y"),
                interview_time=start_time.strftime("%I:%M %p"),
                duration=duration,
                meeting_link=event['meeting_link']
            )
        
        return {
            "success": True,
            "event": event,
            "message": f"Successfully scheduled {meeting_type} interview with {candidate_name}",
            "details": {
                "event_id": event['id'],
                "date": start_time.strftime("%B %d, %Y"),
                "time": start_time.strftime("%I:%M %p"),
                "duration": f"{duration} minutes",
                "meeting_link": event['meeting_link'],
                "calendar_link": event.get('html_link', ''),
                "attendees": attendees,
                "email_sent": candidate_email != ""
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Return module capabilities."""
        capabilities = [
            "Schedule interviews",
            "Book meetings",
            "Find available time slots",
            "Manage calendar events"
        ]
        
        if self.calendar_api.is_available():
            capabilities.append("✅ Google Calendar integration active")
            capabilities.append("Generate Google Meet links")
        else:
            capabilities.append("⚠️ Google Calendar not configured (using mock)")
        
        if self.gmail_api.is_available():
            capabilities.append("✅ Gmail integration active")
            capabilities.append("Send email invitations")
        else:
            capabilities.append("⚠️ Gmail not configured (using mock)")
        
        return capabilities
