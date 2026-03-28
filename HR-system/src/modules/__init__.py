# src/modules/__init__.py

from .calendar_manager import CalendarManager
from .recruiter import Recruiter
from .researcher import Researcher

__all__ = [
    "CalendarManager",
    "Recruiter",
    "Researcher"
]