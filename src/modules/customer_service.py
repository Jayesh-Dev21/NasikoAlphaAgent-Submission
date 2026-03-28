"""
Customer Service Module for support tickets and customer interactions.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import logging
from typing import Dict, Any, List

from src.core.base_module import BaseModule
from src.utils.gmail import get_gmail_client
from src.utils.database import Database

logger = logging.getLogger(__name__)


class CustomerServiceModule(BaseModule):
    """
    Customer service and support module.
    
    Capabilities:
    - Create and manage support tickets
    - Analyze customer sentiment
    - Search FAQ knowledge base
    - Send email notifications to customers
    - Track ticket resolution
    """
    
    def __init__(self, database: Database):
        """Initialize module with database."""
        self.db = database
        self.gmail = get_gmail_client()
        
        # Simple FAQ knowledge base (in production, use vector database)
        self.faq = self._load_faq()
        
        logger.info("CustomerServiceModule initialized")
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this module can handle the task type."""
        supported_tasks = [
            "create_ticket",
            "get_ticket",
            "update_ticket",
            "close_ticket",
            "search_tickets",
            "analyze_sentiment",
            "search_faq"
        ]
        return task_type in supported_tasks
    
    def execute(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a customer service task."""
        logger.info(f"Executing {task_type} with params: {params}")
        
        try:
            if task_type == "create_ticket":
                return self._create_ticket(params)
            
            elif task_type == "get_ticket":
                return self._get_ticket(params)
            
            elif task_type == "update_ticket":
                return self._update_ticket(params)
            
            elif task_type == "close_ticket":
                return self._close_ticket(params)
            
            elif task_type == "search_tickets":
                return self._search_tickets(params)
            
            elif task_type == "analyze_sentiment":
                return self._analyze_sentiment(params)
            
            elif task_type == "search_faq":
                return self._search_faq(params)
            
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
            "create_ticket",
            "get_ticket",
            "update_ticket",
            "close_ticket",
            "search_tickets",
            "analyze_sentiment",
            "search_faq"
        ]
    
    # ==================== Private Methods ====================
    
    def _load_faq(self) -> List[Dict[str, Any]]:
        """Load FAQ knowledge base."""
        # In production, load from database or file
        return [
            {
                "question": "How do I reset my password?",
                "answer": "Click on 'Forgot Password' on the login page and follow the instructions sent to your email.",
                "keywords": ["password", "reset", "login", "forgot"]
            },
            {
                "question": "What are your business hours?",
                "answer": "We are available Monday-Friday, 9 AM - 5 PM EST. For urgent matters, contact emergency support.",
                "keywords": ["hours", "time", "open", "available", "when"]
            },
            {
                "question": "How do I contact support?",
                "answer": "You can email support@company.com, call 1-800-SUPPORT, or create a ticket through the portal.",
                "keywords": ["contact", "support", "help", "reach", "email", "phone"]
            },
            {
                "question": "How do I track my order?",
                "answer": "Log in to your account and go to 'My Orders' to see tracking information.",
                "keywords": ["track", "order", "shipping", "delivery", "where"]
            },
            {
                "question": "What is your refund policy?",
                "answer": "We offer full refunds within 30 days of purchase. Items must be in original condition.",
                "keywords": ["refund", "return", "money back", "cancel"]
            },
            {
                "question": "How do I update my billing information?",
                "answer": "Go to Account Settings > Billing and update your payment method.",
                "keywords": ["billing", "payment", "credit card", "update"]
            }
        ]
    
    def _create_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a support ticket."""
        # Required params
        customer_name = self._get_param(params, "customer_name")
        customer_email = self._get_param(params, "customer_email")
        subject = self._get_param(params, "subject")
        description = self._get_param(params, "description")
        
        # Optional params
        priority = self._get_param(params, "priority", "medium")
        category = self._get_param(params, "category", "general")
        
        # Validate
        if not customer_name:
            return {"success": False, "error": "customer_name is required"}
        if not customer_email:
            return {"success": False, "error": "customer_email is required"}
        if not subject:
            return {"success": False, "error": "subject is required"}
        if not description:
            return {"success": False, "error": "description is required"}
        
        # Analyze sentiment
        sentiment = self._detect_sentiment(description)
        
        # Adjust priority based on sentiment
        if sentiment == "negative" and priority == "medium":
            priority = "high"
        
        # Create ticket in database
        ticket_id = self.db.create_ticket({
            "customer_name": customer_name,
            "customer_email": customer_email,
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category,
            "sentiment": sentiment,
            "status": "open"
        })
        
        # Send confirmation email
        email_sent = self.gmail.send_ticket_notification(
            customer_email=customer_email,
            ticket_id=ticket_id,
            subject=subject,
            status="open"
        )
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "subject": subject,
            "priority": priority,
            "sentiment": sentiment,
            "status": "open",
            "email_sent": email_sent
        }
    
    def _get_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ticket by ID."""
        ticket_id = self._get_param(params, "ticket_id")
        
        if not ticket_id:
            return {"success": False, "error": "ticket_id is required"}
        
        ticket = self.db.get_ticket(ticket_id)
        
        if not ticket:
            return {
                "success": False,
                "error": f"Ticket not found: {ticket_id}"
            }
        
        return {
            "success": True,
            "ticket": ticket
        }
    
    def _update_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a ticket."""
        ticket_id = self._get_param(params, "ticket_id")
        updates = self._get_param(params, "updates", {})
        
        if not ticket_id:
            return {"success": False, "error": "ticket_id is required"}
        
        if not updates:
            return {"success": False, "error": "updates dictionary is required"}
        
        # Update in database
        success = self.db.update_ticket(ticket_id, updates)
        
        if not success:
            return {
                "success": False,
                "error": f"Failed to update ticket: {ticket_id}"
            }
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "updates": updates
        }
    
    def _close_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close a ticket."""
        ticket_id = self._get_param(params, "ticket_id")
        resolution = self._get_param(params, "resolution", "Resolved")
        send_email = self._get_param(params, "send_email", True)
        
        if not ticket_id:
            return {"success": False, "error": "ticket_id is required"}
        
        # Get ticket
        ticket = self.db.get_ticket(ticket_id)
        
        if not ticket:
            return {"success": False, "error": f"Ticket not found: {ticket_id}"}
        
        # Update ticket status
        success = self.db.update_ticket(ticket_id, {
            "status": "closed",
            "resolution": resolution
        })
        
        if not success:
            return {"success": False, "error": "Failed to close ticket"}
        
        # Send closure email
        email_sent = False
        if send_email:
            email_sent = self.gmail.send_email(
                to=ticket.get("customer_email", ""),
                subject=f"Ticket Closed: {ticket_id}",
                body=f"""
Hello {ticket.get('customer_name', 'Customer')},

Your support ticket has been resolved and closed.

Ticket ID: {ticket_id}
Subject: {ticket.get('subject', '')}
Resolution: {resolution}

Thank you for contacting us.

Best regards,
Support Team
""".strip()
            )
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": "closed",
            "resolution": resolution,
            "email_sent": email_sent
        }
    
    def _search_tickets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search tickets by criteria."""
        query = self._get_param(params, "query", {})
        
        # Search in database
        tickets = self.db.search_tickets(query)
        
        return {
            "success": True,
            "count": len(tickets),
            "tickets": tickets
        }
    
    def _analyze_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        text = self._get_param(params, "text")
        
        if not text:
            return {"success": False, "error": "text is required"}
        
        sentiment = self._detect_sentiment(text)
        
        return {
            "success": True,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": sentiment
        }
    
    def _detect_sentiment(self, text: str) -> str:
        """
        Detect sentiment from text (simple keyword-based).
        
        In production, use proper NLP library or API.
        """
        text_lower = text.lower()
        
        # Negative keywords
        negative_keywords = [
            "angry", "frustrated", "terrible", "horrible", "worst", "hate",
            "disappointed", "useless", "broken", "doesn't work", "never",
            "awful", "disaster", "unacceptable", "disgusted", "furious"
        ]
        
        # Positive keywords
        positive_keywords = [
            "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "perfect", "best", "awesome", "brilliant", "happy",
            "satisfied", "thank", "appreciate", "impressed"
        ]
        
        # Count matches
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        
        # Determine sentiment
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    def _search_faq(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search FAQ knowledge base."""
        query = self._get_param(params, "query", "").lower()
        
        if not query:
            return {"success": False, "error": "query is required"}
        
        # Search FAQ by keywords
        results = []
        query_words = set(query.split())
        
        for faq_item in self.faq:
            # Check if any query word matches keywords
            keywords = set(faq_item.get("keywords", []))
            
            # Calculate match score
            matches = query_words.intersection(keywords)
            score = len(matches)
            
            # Also check if query words are in question
            question_lower = faq_item["question"].lower()
            for word in query_words:
                if word in question_lower:
                    score += 1
            
            if score > 0:
                results.append({
                    "question": faq_item["question"],
                    "answer": faq_item["answer"],
                    "score": score
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "success": True,
            "query": query,
            "results_found": len(results),
            "results": results[:5]  # Top 5 results
        }
