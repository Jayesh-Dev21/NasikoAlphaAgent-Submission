"""
Database abstraction layer for Unified Business Agent.

Supports both MongoDB (production) and file-based storage (development).

Team Sleepyhead - Nasiko Hackathon 2026
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Global database instance (singleton pattern)
_db_instance = None


def get_database():
    """
    Get database instance (singleton pattern).
    
    Priority:
    1. MongoDB (if MONGODB_URI is set and USE_MONGODB=true)
    2. File-based (fallback for development)
    
    Returns:
        Database: Database instance (MongoDB or file-based)
    """
    global _db_instance
    
    # Return existing instance if available
    if _db_instance is not None:
        return _db_instance
    
    # Check configuration
    mongodb_uri = os.getenv("MONGODB_URI")
    use_mongodb = os.getenv("USE_MONGODB", "true").lower() == "true"
    
    # Try MongoDB first (if configured)
    if use_mongodb and mongodb_uri:
        try:
            from src.utils.mongodb_database import MongoDatabase
            db = MongoDatabase(mongodb_uri)
            if db.is_connected():
                _db_instance = db
                logger.info("✅ Using MongoDB database")
                return _db_instance
        except ImportError:
            logger.warning("⚠️  MongoDB libraries not installed. Run: pip install pymongo")
        except Exception as e:
            logger.warning(f"⚠️  MongoDB connection failed: {e}")
    
    # Fallback to file-based database
    fallback_path = os.getenv("FALLBACK_DB_PATH", "/tmp/business_agent_db.json")
    logger.info(f"ℹ️  Using file-based database (development mode): {fallback_path}")
    _db_instance = FileDatabase(fallback_path)
    return _db_instance


def get_storage_debug_info() -> Dict[str, Any]:
    """Return safe runtime information about active storage backend."""
    db = get_database()
    use_mongodb = os.getenv("USE_MONGODB", "true").lower() == "true"
    mongodb_uri_set = bool(os.getenv("MONGODB_URI"))
    fallback_path = os.getenv("FALLBACK_DB_PATH", "/tmp/business_agent_db.json")

    backend = "mongodb" if db.__class__.__name__ == "MongoDatabase" else "file"

    info: Dict[str, Any] = {
        "active_backend": backend,
        "connected": db.is_connected(),
        "config": {
            "use_mongodb": use_mongodb,
            "mongodb_uri_set": mongodb_uri_set,
            "fallback_db_path": fallback_path,
        },
    }

    if backend == "mongodb":
        info["mongodb"] = {
            "database": getattr(db, "database_name", os.getenv("MONGODB_DATABASE", "business_agent")),
            "uri_configured": mongodb_uri_set,
        }
    else:
        info["file_database"] = {
            "path": getattr(db, "db_path", fallback_path),
        }

    return info


class Database(ABC):
    """Abstract base class for database implementations."""
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if database is available."""
        pass
    
    # Tickets (Customer Service)
    @abstractmethod
    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create a support ticket."""
        pass
    
    @abstractmethod
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket by ID."""
        pass
    
    @abstractmethod
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Update ticket."""
        pass
    
    @abstractmethod
    def search_tickets(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search tickets by criteria."""
        pass
    
    # Datasets (Data Analytics)
    @abstractmethod
    def save_dataset(self, dataset_id: str, metadata: Dict[str, Any]) -> bool:
        """Save dataset metadata."""
        pass
    
    @abstractmethod
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset metadata."""
        pass
    
    @abstractmethod
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets."""
        pass
    
    # Expenses (Finance)
    @abstractmethod
    def create_expense(self, expense_data: Dict[str, Any]) -> str:
        """Create expense record."""
        pass
    
    @abstractmethod
    def get_expenses(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get expenses with optional filters."""
        pass
    
    @abstractmethod
    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update expense."""
        pass
    
    # Events (Scheduling)
    @abstractmethod
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create calendar event."""
        pass
    
    @abstractmethod
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        pass
    
    @abstractmethod
    def get_events(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get events with optional filters."""
        pass
    
    # Documents (Document Processing)
    @abstractmethod
    def save_document(self, doc_data: Dict[str, Any]) -> str:
        """Save processed document."""
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        pass
    
    @abstractmethod
    def search_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search documents."""
        pass


class FileDatabase(Database):
    """
    Simple file-based database for development.
    
    Data is stored in JSON format at /tmp/business_agent_db.json
    
    Collections:
    - tickets: Support tickets
    - datasets: Dataset metadata
    - expenses: Financial transactions
    - events: Calendar events
    - documents: Processed documents
    - system: System metadata (counters, etc.)
    """
    
    def __init__(self, db_path: str = "/tmp/business_agent_db.json"):
        self.db_path = db_path
        self._ensure_db_exists()
        logger.info(f"File database initialized at {db_path}")
    
    def is_connected(self) -> bool:
        """Check if database file is accessible."""
        return os.path.exists(self.db_path)
    
    def _ensure_db_exists(self):
        """Create database file with empty collections if it doesn't exist."""
        if not os.path.exists(self.db_path):
            initial_data = {
                "tickets": {},
                "datasets": {},
                "expenses": {},
                "events": {},
                "documents": {},
                "system": {
                    "ticket_counter": 1000,
                    "expense_counter": 1000,
                    "event_counter": 1000,
                    "document_counter": 1000
                }
            }
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def _load_db(self) -> Dict:
        """Load database from file."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            # Return fresh structure on error
            return {
                "tickets": {},
                "datasets": {},
                "expenses": {},
                "events": {},
                "documents": {},
                "system": {
                    "ticket_counter": 1000,
                    "expense_counter": 1000,
                    "event_counter": 1000,
                    "document_counter": 1000
                }
            }
    
    def _save_db(self, data: Dict):
        """Save database to file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            raise
    
    def _get_next_id(self, counter_name: str) -> int:
        """Get next ID for a collection."""
        db = self._load_db()
        next_id = db["system"].get(counter_name, 1000)
        db["system"][counter_name] = next_id + 1
        self._save_db(db)
        return next_id
    
    # Tickets Implementation
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create a support ticket."""
        ticket_id = f"TICKET-{self._get_next_id('ticket_counter')}"
        db = self._load_db()
        
        ticket = {
            "ticket_id": ticket_id,
            "customer_name": ticket_data.get("customer_name", ""),
            "customer_email": ticket_data.get("customer_email", ""),
            "subject": ticket_data.get("subject", ""),
            "description": ticket_data.get("description", ""),
            "priority": ticket_data.get("priority", "medium"),
            "status": ticket_data.get("status", "open"),
            "category": ticket_data.get("category", "general"),
            "sentiment": ticket_data.get("sentiment", None),
            "assigned_to": ticket_data.get("assigned_to", None),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "notes": []
        }
        
        db["tickets"][ticket_id] = ticket
        self._save_db(db)
        
        return ticket_id
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket by ID."""
        db = self._load_db()
        return db["tickets"].get(ticket_id)
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Update ticket."""
        db = self._load_db()
        
        if ticket_id not in db["tickets"]:
            return False
        
        db["tickets"][ticket_id].update(updates)
        db["tickets"][ticket_id]["updated_at"] = datetime.now().isoformat()
        
        if updates.get("status") == "closed":
            db["tickets"][ticket_id]["resolved_at"] = datetime.now().isoformat()
        
        self._save_db(db)
        return True
    
    def search_tickets(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search tickets by criteria."""
        db = self._load_db()
        results = []
        
        for ticket in db["tickets"].values():
            match = True
            for key, value in query.items():
                if key not in ticket or ticket[key] != value:
                    match = False
                    break
            if match:
                results.append(ticket)
        
        return results
    
    # Datasets Implementation
    
    def save_dataset(self, dataset_id: str, metadata: Dict[str, Any]) -> bool:
        """Save dataset metadata."""
        db = self._load_db()
        
        dataset = {
            "dataset_id": dataset_id,
            "name": metadata.get("name", dataset_id),
            "file_path": metadata.get("file_path", ""),
            "file_type": metadata.get("file_type", ""),
            "rows": metadata.get("rows", 0),
            "columns": metadata.get("columns", []),
            "uploaded_at": datetime.now().isoformat(),
            "summary": metadata.get("summary", {})
        }
        
        db["datasets"][dataset_id] = dataset
        self._save_db(db)
        return True
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset metadata."""
        db = self._load_db()
        return db["datasets"].get(dataset_id)
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets."""
        db = self._load_db()
        return list(db["datasets"].values())
    
    # Expenses Implementation
    
    def create_expense(self, expense_data: Dict[str, Any]) -> str:
        """Create expense record."""
        expense_id = f"EXP-{self._get_next_id('expense_counter')}"
        db = self._load_db()
        
        expense = {
            "expense_id": expense_id,
            "amount": expense_data.get("amount", 0.0),
            "currency": expense_data.get("currency", "USD"),
            "category": expense_data.get("category", "general"),
            "vendor": expense_data.get("vendor", ""),
            "description": expense_data.get("description", ""),
            "date": expense_data.get("date", datetime.now().isoformat()),
            "payment_method": expense_data.get("payment_method", ""),
            "receipt_url": expense_data.get("receipt_url", ""),
            "status": expense_data.get("status", "pending"),
            "created_at": datetime.now().isoformat(),
            "notes": expense_data.get("notes", "")
        }
        
        db["expenses"][expense_id] = expense
        self._save_db(db)
        
        return expense_id
    
    def get_expenses(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get expenses with optional filters."""
        db = self._load_db()
        expenses = list(db["expenses"].values())
        
        if not filters:
            return expenses
        
        # Apply filters
        filtered = []
        for expense in expenses:
            match = True
            for key, value in filters.items():
                if key not in expense or expense[key] != value:
                    match = False
                    break
            if match:
                filtered.append(expense)
        
        return filtered
    
    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update expense."""
        db = self._load_db()
        
        if expense_id not in db["expenses"]:
            return False
        
        db["expenses"][expense_id].update(updates)
        self._save_db(db)
        return True
    
    # Events Implementation
    
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create calendar event."""
        event_id = f"EVENT-{self._get_next_id('event_counter')}"
        db = self._load_db()
        
        event = {
            "event_id": event_id,
            "title": event_data.get("title", ""),
            "description": event_data.get("description", ""),
            "start_time": event_data.get("start_time", ""),
            "end_time": event_data.get("end_time", ""),
            "attendees": event_data.get("attendees", []),
            "location": event_data.get("location", ""),
            "meeting_link": event_data.get("meeting_link", ""),
            "calendar_id": event_data.get("calendar_id", ""),
            "created_at": datetime.now().isoformat(),
            "status": event_data.get("status", "scheduled")
        }
        
        db["events"][event_id] = event
        self._save_db(db)
        
        return event_id
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        db = self._load_db()
        return db["events"].get(event_id)
    
    def get_events(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get events with optional filters."""
        db = self._load_db()
        events = list(db["events"].values())
        
        if not filters:
            return events
        
        # Apply filters
        filtered = []
        for event in events:
            match = True
            for key, value in filters.items():
                if key not in event or event[key] != value:
                    match = False
                    break
            if match:
                filtered.append(event)
        
        return filtered
    
    # Documents Implementation
    
    def save_document(self, doc_data: Dict[str, Any]) -> str:
        """Save processed document."""
        doc_id = f"DOC-{self._get_next_id('document_counter')}"
        db = self._load_db()
        
        document = {
            "doc_id": doc_id,
            "file_name": doc_data.get("file_name", ""),
            "file_type": doc_data.get("file_type", ""),
            "file_path": doc_data.get("file_path", ""),
            "extracted_text": doc_data.get("extracted_text", ""),
            "document_type": doc_data.get("document_type", ""),  # invoice, receipt, etc.
            "metadata": doc_data.get("metadata", {}),
            "processed_at": datetime.now().isoformat(),
            "status": doc_data.get("status", "processed")
        }
        
        db["documents"][doc_id] = document
        self._save_db(db)
        
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        db = self._load_db()
        return db["documents"].get(doc_id)
    
    def search_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search documents."""
        db = self._load_db()
        results = []
        
        for doc in db["documents"].values():
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                results.append(doc)
        
        return results
