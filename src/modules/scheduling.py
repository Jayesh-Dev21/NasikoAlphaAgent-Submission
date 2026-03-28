"""
Scheduling Module for calendar management and meeting scheduling.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.core.base_module import BaseModule
from src.utils.google_calendar import get_calendar_client
from src.utils.gmail import get_gmail_client
from src.utils.database import Database

logger = logging.getLogger(__name__)


class SchedulingModule(BaseModule):
    """
    Scheduling and calendar management module.
    
    Capabilities:
    - Schedule meetings with Google Calendar integration
    - Find available time slots
    - Send calendar invitations via email
    - Create events with Google Meet links
    - Cancel and update events
    """
    
    def __init__(self, database: Database):
        """Initialize module with database."""
        self.db = database
        self.calendar = get_calendar_client()
        self.gmail = get_gmail_client()
        logger.info("SchedulingModule initialized")
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this module can handle the task type."""
        supported_tasks = [
            "schedule_meeting",
            "find_available_slots",
            "find_slots",
            "create_event",
            "get_event",
            "cancel_event",
            "list_events"
        ]
        return task_type in supported_tasks
    
    def execute(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a scheduling task."""
        logger.info(f"Executing {task_type} with params: {params}")
        
        try:
            if task_type == "schedule_meeting":
                return self._schedule_meeting(params)
            
            elif task_type == "find_available_slots":
                return self._find_available_slots(params)

            elif task_type == "find_slots":
                return self._find_available_slots(params)
            
            elif task_type == "create_event":
                return self._create_event(params)
            
            elif task_type == "get_event":
                return self._get_event(params)
            
            elif task_type == "cancel_event":
                return self._cancel_event(params)
            
            elif task_type == "list_events":
                return self._list_events(params)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
        
        except Exception as e:
            logger.error(f"Error executing {task_type}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return [
            "schedule_meeting",
            "find_available_slots",
            "find_slots",
            "create_event",
            "get_event",
            "cancel_event",
            "list_events"
        ]
    
    # ==================== Private Methods ====================
    
    def _schedule_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a meeting end-to-end:
        1. Create calendar event
        2. Send email invitations
        3. Save to database
        """
        # Required params
        title = self._get_param(params, "title")
        start_time = self._get_param(params, "start_time")
        end_time = self._get_param(params, "end_time")
        attendees = self._get_param(params, "attendees", [])
        
        # Optional params
        description = self._get_param(params, "description")
        location = self._get_param(params, "location")
        add_meet_link = self._get_param(params, "add_meet_link", True)
        
        # Validate required params
        if not title:
            return {"success": False, "error": "title is required"}
        if not start_time:
            return {"success": False, "error": "start_time is required"}
        if not end_time:
            return {"success": False, "error": "end_time is required"}
        
        # Create calendar event
        event = self.calendar.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            attendees=attendees,
            location=location,
            add_meet_link=add_meet_link
        )
        
        if not event:
            return {
                "success": False,
                "error": "Failed to create calendar event"
            }
        
        # Extract event details
        event_id = event.get('id')
        meeting_link = event.get('hangoutLink', '')
        calendar_link = event.get('htmlLink', '')
        
        # Save to database
        db_event_id = self.db.create_event({
            "title": title,
            "description": description or "",
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "location": location or "",
            "meeting_link": meeting_link,
            "calendar_id": event_id,
            "status": "scheduled"
        })
        
        # Send email invitations to attendees
        sent_emails = []
        for attendee in attendees:
            success = self.gmail.send_meeting_invitation(
                to=attendee,
                title=title,
                start_time=start_time,
                end_time=end_time,
                meeting_link=meeting_link,
                description=description
            )
            sent_emails.append({"email": attendee, "sent": success})
        
        return {
            "success": True,
            "event_id": db_event_id,
            "calendar_event_id": event_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "meeting_link": meeting_link,
            "calendar_link": calendar_link,
            "attendees": attendees,
            "emails_sent": sent_emails
        }
    
    def _find_available_slots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find available time slots in calendar."""
        duration_minutes = self._get_param(params, "duration_minutes", 60)
        start_date = self._get_param(params, "start_date")
        end_date = self._get_param(params, "end_date")
        working_hours_start = self._get_param(params, "working_hours_start", 9)
        working_hours_end = self._get_param(params, "working_hours_end", 17)
        
        # Find slots
        slots = self.calendar.find_available_slots(
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date,
            working_hours_start=working_hours_start,
            working_hours_end=working_hours_end
        )
        
        return {
            "success": True,
            "duration_minutes": duration_minutes,
            "slots_found": len(slots),
            "available_slots": slots
        }
    
    def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event (without email notifications)."""
        title = self._get_param(params, "title")
        start_time = self._get_param(params, "start_time")
        end_time = self._get_param(params, "end_time")
        description = self._get_param(params, "description")
        attendees = self._get_param(params, "attendees", [])
        location = self._get_param(params, "location")
        add_meet_link = self._get_param(params, "add_meet_link", False)
        
        if not title or not start_time or not end_time:
            return {
                "success": False,
                "error": "title, start_time, and end_time are required"
            }
        
        # Create event
        event = self.calendar.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            attendees=attendees,
            location=location,
            add_meet_link=add_meet_link
        )
        
        if not event:
            return {"success": False, "error": "Failed to create event"}
        
        # Save to database
        event_id = self.db.create_event({
            "title": title,
            "description": description or "",
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees,
            "location": location or "",
            "meeting_link": event.get('hangoutLink', ''),
            "calendar_id": event.get('id'),
            "status": "scheduled"
        })
        
        return {
            "success": True,
            "event_id": event_id,
            "calendar_event_id": event.get('id'),
            "meeting_link": event.get('hangoutLink'),
            "calendar_link": event.get('htmlLink')
        }
    
    def _get_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get event details."""
        event_id = self._get_param(params, "event_id")
        
        if not event_id:
            return {"success": False, "error": "event_id is required"}
        
        # Get from database
        event = self.db.get_event(event_id)
        
        if not event:
            return {
                "success": False,
                "error": f"Event not found: {event_id}"
            }
        
        return {
            "success": True,
            "event": event
        }
    
    def _cancel_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an event."""
        event_id = self._get_param(params, "event_id")
        send_notifications = self._get_param(params, "send_notifications", True)
        
        if not event_id:
            return {"success": False, "error": "event_id is required"}
        
        # Get event from database
        event = self.db.get_event(event_id)
        
        if not event:
            return {"success": False, "error": f"Event not found: {event_id}"}
        
        # Delete from Google Calendar
        calendar_id = event.get("calendar_id")
        if calendar_id:
            self.calendar.delete_event(calendar_id)
        
        # Update database (mark as cancelled instead of deleting)
        # Note: FileDatabase doesn't have update_event, so we'll just note it
        # In production, you'd add this method to Database interface
        
        # Send cancellation emails if requested
        sent_emails = []
        if send_notifications:
            attendees = event.get("attendees", [])
            for attendee in attendees:
                success = self.gmail.send_email(
                    to=attendee,
                    subject=f"Meeting Cancelled: {event.get('title')}",
                    body=f"The meeting '{event.get('title')}' scheduled for {event.get('start_time')} has been cancelled."
                )
                sent_emails.append({"email": attendee, "sent": success})
        
        return {
            "success": True,
            "event_id": event_id,
            "cancelled": True,
            "notifications_sent": sent_emails
        }
    
    def _list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List upcoming events."""
        max_results = self._get_param(params, "max_results", 10)
        time_min = self._get_param(params, "time_min")
        time_max = self._get_param(params, "time_max")
        
        # Get from calendar
        events = self.calendar.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        
        return {
            "success": True,
            "count": len(events),
            "events": events
        }
