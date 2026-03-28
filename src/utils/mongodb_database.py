"""
MongoDB database implementation for Unified Business Agent.

Collections:
- tickets: Customer support tickets
- datasets: Dataset metadata
- expenses: Financial transactions
- events: Calendar events
- documents: Processed documents

Team Sleepyhead - Nasiko Hackathon 2026
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError

from src.utils.database import Database

logger = logging.getLogger(__name__)


class MongoDatabase(Database):
    """
    MongoDB database implementation.
    
    Setup:
    1. Install MongoDB: https://www.mongodb.com/docs/manual/installation/
    2. Start MongoDB locally: mongod --dbpath /path/to/data
    3. Set environment variables:
       - MONGODB_URI (default: mongodb://localhost:27017/)
       - MONGODB_DATABASE (default: business_agent)
    
    Or use MongoDB Atlas (cloud):
    - MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
    """
    
    def __init__(self, uri: Optional[str] = None, database_name: Optional[str] = None):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = database_name or os.getenv("MONGODB_DATABASE", "business_agent")
        
        self.client = None
        self.db = None
        
        # Collections
        self.tickets = None
        self.datasets = None
        self.expenses = None
        self.events = None
        self.documents = None
        self.system = None
        
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB and initialize collections."""
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=30000,  # 30 seconds
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,
                w='majority'
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            
            # Initialize collections
            self.tickets = self.db.tickets
            self.datasets = self.db.datasets
            self.expenses = self.db.expenses
            self.events = self.db.events
            self.documents = self.db.documents
            self.system = self.db.system
            
            # Create indexes for performance
            self._create_indexes()
            
            # Initialize system counters
            self._init_system_counters()
            
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            logger.error("Make sure MongoDB is running and MONGODB_URI is correct")
            self.client = None
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            self.client = None
            raise
    
    def _create_indexes(self):
        """Create database indexes for better query performance."""
        if not self.is_connected():
            return
        
        try:
            # Tickets indexes
            self.tickets.create_index("ticket_id", unique=True)
            self.tickets.create_index("customer_email")
            self.tickets.create_index("status")
            self.tickets.create_index("priority")
            self.tickets.create_index([("created_at", DESCENDING)])
            
            # Datasets indexes
            self.datasets.create_index("dataset_id", unique=True)
            self.datasets.create_index("file_type")
            self.datasets.create_index([("uploaded_at", DESCENDING)])
            
            # Expenses indexes
            self.expenses.create_index("expense_id", unique=True)
            self.expenses.create_index("category")
            self.expenses.create_index("status")
            self.expenses.create_index([("date", DESCENDING)])
            self.expenses.create_index([("amount", DESCENDING)])
            
            # Events indexes
            self.events.create_index("event_id", unique=True)
            self.events.create_index("calendar_id")
            self.events.create_index([("start_time", ASCENDING)])
            self.events.create_index("status")
            
            # Documents indexes
            self.documents.create_index("doc_id", unique=True)
            self.documents.create_index("document_type")
            self.documents.create_index([("processed_at", DESCENDING)])
            
            logger.info("✅ Database indexes created")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    def _init_system_counters(self):
        """Initialize system counters for ID generation."""
        if not self.is_connected():
            return
        
        try:
            # Check if system document exists
            system_doc = self.system.find_one({"_id": "counters"})
            
            if not system_doc:
                # Create initial counters
                self.system.insert_one({
                    "_id": "counters",
                    "ticket_counter": 1000,
                    "expense_counter": 1000,
                    "event_counter": 1000,
                    "document_counter": 1000
                })
                logger.info("✅ System counters initialized")
        
        except Exception as e:
            logger.error(f"Failed to initialize counters: {e}")
    
    def _get_next_id(self, counter_name: str) -> int:
        """Get next ID from counter."""
        if not self.is_connected():
            return 1000
        
        try:
            result = self.system.find_one_and_update(
                {"_id": "counters"},
                {"$inc": {counter_name: 1}},
                return_document=True
            )
            return result[counter_name]
        
        except Exception as e:
            logger.error(f"Failed to get next ID: {e}")
            return 1000
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        return self.client is not None
    
    # ==================== TICKETS (Customer Service) ====================
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """Create a support ticket."""
        if not self.is_connected():
            raise ConnectionError("MongoDB not connected")
        
        try:
            ticket_id = f"TICKET-{self._get_next_id('ticket_counter')}"
            
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
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "resolved_at": None,
                "notes": []
            }
            
            self.tickets.insert_one(ticket)
            logger.info(f"✅ Ticket created: {ticket_id}")
            
            return ticket_id
        
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
            raise
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket by ID."""
        if not self.is_connected():
            return None
        
        try:
            ticket = self.tickets.find_one({"ticket_id": ticket_id})
            
            if ticket:
                ticket["_id"] = str(ticket["_id"])
            
            return ticket
        
        except Exception as e:
            logger.error(f"Failed to get ticket: {e}")
            return None
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Update ticket."""
        if not self.is_connected():
            return False
        
        try:
            updates["updated_at"] = datetime.utcnow()
            
            # If closing ticket, set resolved_at
            if updates.get("status") == "closed":
                updates["resolved_at"] = datetime.utcnow()
            
            result = self.tickets.update_one(
                {"ticket_id": ticket_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"Failed to update ticket: {e}")
            return False
    
    def search_tickets(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search tickets by criteria."""
        if not self.is_connected():
            return []
        
        try:
            tickets = list(self.tickets.find(query))
            
            # Convert ObjectId to string
            for ticket in tickets:
                ticket["_id"] = str(ticket["_id"])
            
            return tickets
        
        except Exception as e:
            logger.error(f"Failed to search tickets: {e}")
            return []
    
    # ==================== DATASETS (Data Analytics) ====================
    
    def save_dataset(self, dataset_id: str, metadata: Dict[str, Any]) -> bool:
        """Save dataset metadata."""
        if not self.is_connected():
            return False
        
        try:
            dataset = {
                "dataset_id": dataset_id,
                "name": metadata.get("name", dataset_id),
                "file_path": metadata.get("file_path", ""),
                "file_type": metadata.get("file_type", ""),
                "rows": metadata.get("rows", 0),
                "columns": metadata.get("columns", []),
                "uploaded_at": datetime.utcnow(),
                "summary": metadata.get("summary", {})
            }
            
            # Upsert (insert or update)
            self.datasets.update_one(
                {"dataset_id": dataset_id},
                {"$set": dataset},
                upsert=True
            )
            
            logger.info(f"✅ Dataset saved: {dataset_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save dataset: {e}")
            return False
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset metadata."""
        if not self.is_connected():
            return None
        
        try:
            dataset = self.datasets.find_one({"dataset_id": dataset_id})
            
            if dataset:
                dataset["_id"] = str(dataset["_id"])
            
            return dataset
        
        except Exception as e:
            logger.error(f"Failed to get dataset: {e}")
            return None
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets."""
        if not self.is_connected():
            return []
        
        try:
            datasets = list(self.datasets.find().sort("uploaded_at", DESCENDING))
            
            for dataset in datasets:
                dataset["_id"] = str(dataset["_id"])
            
            return datasets
        
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return []
    
    # ==================== EXPENSES (Finance) ====================
    
    def create_expense(self, expense_data: Dict[str, Any]) -> str:
        """Create expense record."""
        if not self.is_connected():
            raise ConnectionError("MongoDB not connected")
        
        try:
            expense_id = f"EXP-{self._get_next_id('expense_counter')}"
            
            expense = {
                "expense_id": expense_id,
                "amount": expense_data.get("amount", 0.0),
                "currency": expense_data.get("currency", "USD"),
                "category": expense_data.get("category", "general"),
                "vendor": expense_data.get("vendor", ""),
                "description": expense_data.get("description", ""),
                "date": expense_data.get("date", datetime.utcnow()),
                "payment_method": expense_data.get("payment_method", ""),
                "receipt_url": expense_data.get("receipt_url", ""),
                "status": expense_data.get("status", "pending"),
                "created_at": datetime.utcnow(),
                "notes": expense_data.get("notes", "")
            }
            
            self.expenses.insert_one(expense)
            logger.info(f"✅ Expense created: {expense_id}")
            
            return expense_id
        
        except Exception as e:
            logger.error(f"Failed to create expense: {e}")
            raise
    
    def get_expenses(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get expenses with optional filters."""
        if not self.is_connected():
            return []
        
        try:
            query = filters or {}
            expenses = list(self.expenses.find(query).sort("date", DESCENDING))
            
            for expense in expenses:
                expense["_id"] = str(expense["_id"])
            
            return expenses
        
        except Exception as e:
            logger.error(f"Failed to get expenses: {e}")
            return []
    
    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update expense."""
        if not self.is_connected():
            return False
        
        try:
            result = self.expenses.update_one(
                {"expense_id": expense_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"Failed to update expense: {e}")
            return False
    
    # ==================== EVENTS (Scheduling) ====================
    
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create calendar event."""
        if not self.is_connected():
            raise ConnectionError("MongoDB not connected")
        
        try:
            event_id = f"EVENT-{self._get_next_id('event_counter')}"
            
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
                "created_at": datetime.utcnow(),
                "status": event_data.get("status", "scheduled")
            }
            
            self.events.insert_one(event)
            logger.info(f"✅ Event created: {event_id}")
            
            return event_id
        
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        if not self.is_connected():
            return None
        
        try:
            event = self.events.find_one({"event_id": event_id})
            
            if event:
                event["_id"] = str(event["_id"])
            
            return event
        
        except Exception as e:
            logger.error(f"Failed to get event: {e}")
            return None
    
    def get_events(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get events with optional filters."""
        if not self.is_connected():
            return []
        
        try:
            query = filters or {}
            events = list(self.events.find(query).sort("start_time", ASCENDING))
            
            for event in events:
                event["_id"] = str(event["_id"])
            
            return events
        
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    # ==================== DOCUMENTS (Document Processing) ====================
    
    def save_document(self, doc_data: Dict[str, Any]) -> str:
        """Save processed document."""
        if not self.is_connected():
            raise ConnectionError("MongoDB not connected")
        
        try:
            doc_id = f"DOC-{self._get_next_id('document_counter')}"
            
            document = {
                "doc_id": doc_id,
                "file_name": doc_data.get("file_name", ""),
                "file_type": doc_data.get("file_type", ""),
                "file_path": doc_data.get("file_path", ""),
                "extracted_text": doc_data.get("extracted_text", ""),
                "document_type": doc_data.get("document_type", ""),  # invoice, receipt, etc.
                "metadata": doc_data.get("metadata", {}),
                "processed_at": datetime.utcnow(),
                "status": doc_data.get("status", "processed")
            }
            
            self.documents.insert_one(document)
            logger.info(f"✅ Document saved: {doc_id}")
            
            return doc_id
        
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        if not self.is_connected():
            return None
        
        try:
            doc = self.documents.find_one({"doc_id": doc_id})
            
            if doc:
                doc["_id"] = str(doc["_id"])
            
            return doc
        
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None
    
    def search_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search documents."""
        if not self.is_connected():
            return []
        
        try:
            docs = list(self.documents.find(query).sort("processed_at", DESCENDING))
            
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            
            return docs
        
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []


# Factory function for backward compatibility
def get_database(uri: Optional[str] = None, database_name: Optional[str] = None) -> MongoDatabase:
    """Get MongoDB database instance."""
    return MongoDatabase(uri, database_name)
