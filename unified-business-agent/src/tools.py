"""
Tools for the Unified Business Agent.

LangChain tools that bridge the agent to the modular pipeline and database.

Team Sleepyhead - Nasiko Hackathon 2026
"""

from typing import List, Optional
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# ==================== Global References ====================
# These are set by the agent on initialization

_planner = None
_executor = None
_aggregator = None
_database = None


def set_modular_components(planner, executor, aggregator, database):
    """Set the modular components for tools to use."""
    global _planner, _executor, _aggregator, _database
    _planner = planner
    _executor = executor
    _aggregator = aggregator
    _database = database
    logger.info("Modular components set for tools")


def get_all_tools() -> List:
    """Return all available tools for the agent."""
    return [
        # Customer Service tools
        create_ticket,
        get_ticket,
        update_ticket,
        close_ticket,
        analyze_sentiment,
        search_faq,
        
        # Data Analytics tools
        load_dataset,
        analyze_dataset,
        generate_report,
        query_data,
        
        # Finance tools
        add_expense,
        get_expenses,
        process_invoice,
        check_budget,
        
        # Scheduling tools
        schedule_meeting,
        find_available_slots,
        
        # Document Processing tools
        extract_text_from_document,
        process_invoice_ocr,
        
        # Multi-step workflow tool
        handle_complex_task
    ]


# ==================== CUSTOMER SERVICE TOOLS ====================

@tool
def create_ticket(
    customer_name: str,
    customer_email: str,
    subject: str,
    description: str,
    priority: str = "medium",
    category: str = "general"
) -> str:
    """
    Create a customer support ticket.
    
    Use this when a customer reports an issue, asks for help, or submits a complaint.
    Automatically analyzes sentiment and sends email confirmation.
    
    Args:
        customer_name: Customer's full name
        customer_email: Customer's email address
        subject: Brief subject/title of the issue
        description: Detailed description of the issue
        priority: Priority level - "low", "medium", or "high" (default: "medium")
        category: Category - "general", "technical", "billing", "shipping" (default: "general")
    
    Returns:
        Success message with ticket ID or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        # Use CustomerServiceModule
        from src.modules.customer_service import CustomerServiceModule
        module = CustomerServiceModule(_database)
        
        result = module.execute("create_ticket", {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category
        })
        
        if result.get("success"):
            ticket_id = result.get("ticket_id")
            sentiment = result.get("sentiment", "neutral")
            email_status = "✉️ Email sent" if result.get("email_sent") else "⚠️ Email failed"
            
            return f"""✅ Support ticket created successfully!
            
Ticket ID: {ticket_id}
Customer: {customer_name} ({customer_email})
Subject: {subject}
Priority: {priority.upper()}
Sentiment: {sentiment.upper()}
Status: {email_status}

The customer has been notified via email."""
        
        return f"❌ Failed to create ticket: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        logger.error(f"Error creating ticket: {e}", exc_info=True)
        return f"❌ Error creating ticket: {str(e)}"


@tool
def get_ticket(ticket_id: str) -> str:
    """
    Retrieve ticket information by ticket ID.
    
    Args:
        ticket_id: The ticket ID (e.g., "TICKET-1001")
    
    Returns:
        Ticket details or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.customer_service import CustomerServiceModule
        module = CustomerServiceModule(_database)
        
        result = module.execute("get_ticket", {"ticket_id": ticket_id})
        
        if result.get("success"):
            ticket = result.get("ticket", {})
            return f"""📋 Ticket Details:

ID: {ticket.get('ticket_id')}
Customer: {ticket.get('customer_name')} ({ticket.get('customer_email')})
Subject: {ticket.get('subject')}
Description: {ticket.get('description')}
Priority: {ticket.get('priority', 'medium').upper()}
Status: {ticket.get('status', 'open').upper()}
Sentiment: {ticket.get('sentiment', 'neutral').upper()}
Created: {ticket.get('created_at')}
Updated: {ticket.get('updated_at')}"""
        
        return f"❌ {result.get('error', 'Ticket not found')}"
    
    except Exception as e:
        logger.error(f"Error getting ticket: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def update_ticket(ticket_id: str, status: Optional[str] = None, priority: Optional[str] = None, notes: Optional[str] = None) -> str:
    """
    Update a support ticket's status, priority, or add notes.
    
    Args:
        ticket_id: The ticket ID to update
        status: New status - "open", "in_progress", "waiting", "closed"
        priority: New priority - "low", "medium", "high"
        notes: Additional notes to add
    
    Returns:
        Success or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.customer_service import CustomerServiceModule
        module = CustomerServiceModule(_database)
        
        updates = {}
        if status:
            updates["status"] = status
        if priority:
            updates["priority"] = priority
        if notes:
            updates["notes"] = notes
        
        if not updates:
            return "❌ No updates provided. Specify status, priority, or notes."
        
        result = module.execute("update_ticket", {"ticket_id": ticket_id, "updates": updates})
        
        if result.get("success"):
            return f"✅ Ticket {ticket_id} updated successfully: {', '.join(updates.keys())}"
        
        return f"❌ {result.get('error', 'Failed to update ticket')}"
    
    except Exception as e:
        logger.error(f"Error updating ticket: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def close_ticket(ticket_id: str, resolution: str = "Resolved") -> str:
    """
    Close a support ticket with a resolution.
    
    Sends closure email to customer.
    
    Args:
        ticket_id: The ticket ID to close
        resolution: Resolution summary (default: "Resolved")
    
    Returns:
        Success or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.customer_service import CustomerServiceModule
        module = CustomerServiceModule(_database)
        
        result = module.execute("close_ticket", {
            "ticket_id": ticket_id,
            "resolution": resolution,
            "send_email": True
        })
        
        if result.get("success"):
            email_status = "✉️ Email sent" if result.get("email_sent") else "⚠️ Email failed"
            return f"✅ Ticket {ticket_id} closed. Resolution: {resolution}. {email_status}"
        
        return f"❌ {result.get('error', 'Failed to close ticket')}"
    
    except Exception as e:
        logger.error(f"Error closing ticket: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of text (positive, negative, or neutral).
    
    Useful for understanding customer mood from messages or feedback.
    
    Args:
        text: The text to analyze
    
    Returns:
        Sentiment analysis result
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.customer_service import CustomerServiceModule
        module = CustomerServiceModule(_database)
        
        result = module.execute("analyze_sentiment", {"text": text})
        
        if result.get("success"):
            sentiment = result.get("sentiment", "neutral")
            emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(sentiment, "😐")
            return f"{emoji} Sentiment: {sentiment.upper()}"
        
        return f"❌ {result.get('error', 'Failed to analyze sentiment')}"
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def search_faq(query: str) -> str:
    """
    Search the FAQ knowledge base for answers to common questions.
    
    Use this to quickly answer customer questions without creating tickets.
    
    Args:
        query: The question or keywords to search for
    
    Returns:
        FAQ results or message if no results found
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.customer_service import CustomerServiceModule
        module = CustomerServiceModule(_database)
        
        result = module.execute("search_faq", {"query": query})
        
        if result.get("success"):
            results = result.get("results", [])
            
            if not results:
                return f"❌ No FAQ results found for: {query}"
            
            output = f"📚 FAQ Results for '{query}':\n\n"
            for i, item in enumerate(results[:3], 1):
                output += f"{i}. Q: {item['question']}\n   A: {item['answer']}\n\n"
            
            return output.strip()
        
        return f"❌ {result.get('error', 'Failed to search FAQ')}"
    
    except Exception as e:
        logger.error(f"Error searching FAQ: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


# ==================== DATA ANALYTICS TOOLS ====================

@tool
def load_dataset(file_path: str) -> str:
    """
    Load a dataset from a file (CSV, Excel, or JSON).
    
    Returns a dataset ID that can be used for analysis.
    
    Args:
        file_path: Path to the dataset file (e.g., "/data/sales.csv")
    
    Returns:
        Dataset ID and basic info, or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.data_analytics import DataAnalyticsModule
        module = DataAnalyticsModule(_database)
        
        result = module.execute("load_dataset", {"file_path": file_path})
        
        if result.get("success"):
            dataset_id = result.get("dataset_id")
            rows = result.get("rows")
            columns = result.get("columns", [])
            
            return f"""✅ Dataset loaded successfully!

Dataset ID: {dataset_id}
Rows: {rows:,}
Columns: {len(columns)}
Column names: {', '.join(columns[:10])}{"..." if len(columns) > 10 else ""}

Use this dataset_id for analysis."""
        
        return f"❌ {result.get('error', 'Failed to load dataset')}"
    
    except Exception as e:
        logger.error(f"Error loading dataset: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def analyze_dataset(dataset_id: str) -> str:
    """
    Perform statistical analysis on a loaded dataset.
    
    Provides summary statistics, missing values, and data types.
    
    Args:
        dataset_id: The dataset ID from load_dataset
    
    Returns:
        Analysis results or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.data_analytics import DataAnalyticsModule
        module = DataAnalyticsModule(_database)
        
        result = module.execute("analyze_dataset", {"dataset_id": dataset_id})
        
        if result.get("success"):
            analysis = result.get("analysis", {})
            
            output = f"""📊 Dataset Analysis (ID: {dataset_id})

Rows: {analysis.get('rows', 0):,}
Columns: {analysis.get('columns', 0)}

Summary Statistics (numeric columns):"""
            
            stats = analysis.get("summary_stats", {})
            for col, values in list(stats.items())[:5]:
                output += f"\n\n{col}:"
                output += f"\n  Mean: {values.get('mean', 0):.2f}"
                output += f"\n  Median: {values.get('median', 0):.2f}"
                output += f"\n  Min: {values.get('min', 0):.2f}"
                output += f"\n  Max: {values.get('max', 0):.2f}"
            
            return output
        
        return f"❌ {result.get('error', 'Failed to analyze dataset')}"
    
    except Exception as e:
        logger.error(f"Error analyzing dataset: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def generate_report(dataset_id: str, report_type: str = "summary") -> str:
    """
    Generate a report from a dataset.
    
    Args:
        dataset_id: The dataset ID
        report_type: Type of report - "summary", "detailed" (default: "summary")
    
    Returns:
        Generated report or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.data_analytics import DataAnalyticsModule
        module = DataAnalyticsModule(_database)
        
        result = module.execute("generate_report", {
            "dataset_id": dataset_id,
            "report_type": report_type
        })
        
        if result.get("success"):
            report = result.get("report", {})
            return f"""📈 {report_type.upper()} REPORT

Dataset: {dataset_id}
Generated: {report.get('generated_at', 'N/A')}
Rows: {report.get('rows', 0):,}

Report saved and ready for review."""
        
        return f"❌ {result.get('error', 'Failed to generate report')}"
    
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def query_data(dataset_id: str, limit: int = 10) -> str:
    """
    Query data from a loaded dataset.
    
    Args:
        dataset_id: The dataset ID
        limit: Maximum number of rows to return (default: 10)
    
    Returns:
        Query results or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.data_analytics import DataAnalyticsModule
        module = DataAnalyticsModule(_database)
        
        result = module.execute("query_data", {"dataset_id": dataset_id, "limit": limit})
        
        if result.get("success"):
            count = result.get("results_count", 0)
            return f"✅ Retrieved {count} rows from dataset {dataset_id}"
        
        return f"❌ {result.get('error', 'Failed to query data')}"
    
    except Exception as e:
        logger.error(f"Error querying data: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


# ==================== FINANCE TOOLS ====================

@tool
def add_expense(
    amount: float,
    category: str = "general",
    vendor: str = "",
    description: str = ""
) -> str:
    """
    Add an expense record.
    
    Args:
        amount: Expense amount in dollars
        category: Category - "general", "office_supplies", "travel", "software"
        vendor: Vendor/merchant name
        description: Description of the expense
    
    Returns:
        Success message with expense ID or error
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.finance import FinanceModule
        module = FinanceModule(_database)
        
        result = module.execute("add_expense", {
            "amount": amount,
            "category": category,
            "vendor": vendor,
            "description": description
        })
        
        if result.get("success"):
            expense_id = result.get("expense_id")
            return f"✅ Expense recorded: {expense_id} | ${amount:.2f} | {category} | {vendor or 'N/A'}"
        
        return f"❌ {result.get('error', 'Failed to add expense')}"
    
    except Exception as e:
        logger.error(f"Error adding expense: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def get_expenses(category: Optional[str] = None) -> str:
    """
    Get expense records with optional filtering.
    
    Args:
        category: Optional category filter
    
    Returns:
        List of expenses or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.finance import FinanceModule
        module = FinanceModule(_database)
        
        filters = {"category": category} if category else {}
        result = module.execute("get_expenses", {"filters": filters})
        
        if result.get("success"):
            count = result.get("count", 0)
            total = result.get("total", 0)
            return f"💰 Found {count} expenses totaling ${total:.2f}" + (f" in category '{category}'" if category else "")
        
        return f"❌ {result.get('error', 'Failed to get expenses')}"
    
    except Exception as e:
        logger.error(f"Error getting expenses: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def process_invoice(file_path: str) -> str:
    """
    Process an invoice using OCR to extract amount, vendor, and date.
    
    Automatically creates an expense record from the invoice.
    
    Args:
        file_path: Path to the invoice file (image or PDF)
    
    Returns:
        Extracted invoice data or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.finance import FinanceModule
        module = FinanceModule(_database)
        
        result = module.execute("process_invoice", {"file_path": file_path})
        
        if result.get("success"):
            invoice_data = result.get("parsed_data", {})
            expense_id = result.get("expense_id")
            
            return f"""✅ Invoice processed successfully!

Invoice #: {invoice_data.get('invoice_number', 'N/A')}
Vendor: {invoice_data.get('vendor', 'Unknown')}
Amount: ${invoice_data.get('total', 0):.2f}
Date: {invoice_data.get('date', 'N/A')}
Expense ID: {expense_id}

Expense record created automatically."""
        
        return f"❌ {result.get('error', 'Failed to process invoice')}"
    
    except Exception as e:
        logger.error(f"Error processing invoice: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def check_budget(category: str = "monthly", period: str = "month") -> str:
    """
    Check budget status and remaining balance.
    
    Args:
        category: Budget category - "monthly", "office_supplies", "travel", "software"
        period: Time period - "month", "week", "year"
    
    Returns:
        Budget status and remaining balance
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.finance import FinanceModule
        module = FinanceModule(_database)
        
        result = module.execute("check_budget", {"category": category, "period": period})
        
        if result.get("success"):
            budget_limit = result.get("budget_limit", 0)
            total_spent = result.get("total_spent", 0)
            remaining = result.get("remaining", 0)
            percentage = result.get("percentage_used", 0)
            status = result.get("status", "ok")
            
            status_emoji = {"ok": "✅", "warning": "⚠️", "over_budget": "🚨"}.get(status, "ℹ️")
            
            return f"""{status_emoji} Budget Status: {category.upper()} ({period})

Budget: ${budget_limit:.2f}
Spent: ${total_spent:.2f} ({percentage:.1f}%)
Remaining: ${remaining:.2f}
Status: {status.upper().replace('_', ' ')}"""
        
        return f"❌ {result.get('error', 'Failed to check budget')}"
    
    except Exception as e:
        logger.error(f"Error checking budget: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


# ==================== SCHEDULING TOOLS ====================

@tool
def schedule_meeting(
    title: str,
    start_time: str,
    end_time: str,
    attendees: str,
    description: str = "",
    add_meet_link: bool = True
) -> str:
    """
    Schedule a meeting with Google Calendar integration.
    
    Creates calendar event, generates Google Meet link, and sends email invitations.
    
    Args:
        title: Meeting title
        start_time: Start time in ISO format (e.g., "2024-03-15T10:00:00")
        end_time: End time in ISO format
        attendees: Comma-separated email addresses
        description: Optional meeting description
        add_meet_link: Whether to add Google Meet link (default: True)
    
    Returns:
        Meeting details with links or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.scheduling import SchedulingModule
        module = SchedulingModule(_database)
        
        attendees_list = [email.strip() for email in attendees.split(",")]
        
        result = module.execute("schedule_meeting", {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees_list,
            "description": description,
            "add_meet_link": add_meet_link
        })
        
        if result.get("success"):
            event_id = result.get("event_id")
            meeting_link = result.get("meeting_link", "N/A")
            
            output = f"""✅ Meeting scheduled successfully!

Title: {title}
Time: {start_time} to {end_time}
Attendees: {', '.join(attendees_list)}
Event ID: {event_id}"""
            
            if meeting_link and meeting_link != "N/A":
                output += f"\nGoogle Meet: {meeting_link}"
            
            emails_sent = result.get("emails_sent", [])
            sent_count = sum(1 for e in emails_sent if e.get("sent"))
            output += f"\n\n✉️ Invitations sent: {sent_count}/{len(attendees_list)}"
            
            return output
        
        return f"❌ {result.get('error', 'Failed to schedule meeting')}"
    
    except Exception as e:
        logger.error(f"Error scheduling meeting: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def find_available_slots(duration_minutes: int = 60, days_ahead: int = 7) -> str:
    """
    Find available time slots in the calendar.
    
    Args:
        duration_minutes: Required meeting duration in minutes (default: 60)
        days_ahead: How many days ahead to search (default: 7)
    
    Returns:
        List of available time slots or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.scheduling import SchedulingModule
        module = SchedulingModule(_database)
        
        result = module.execute("find_available_slots", {
            "duration_minutes": duration_minutes
        })
        
        if result.get("success"):
            slots = result.get("available_slots", [])
            count = result.get("slots_found", 0)
            
            if count == 0:
                return "❌ No available slots found in the specified timeframe"
            
            output = f"📅 Found {count} available slots ({duration_minutes} min):\n\n"
            for i, slot in enumerate(slots[:5], 1):
                output += f"{i}. {slot['start_time']} to {slot['end_time']}\n"
            
            return output.strip()
        
        return f"❌ {result.get('error', 'Failed to find available slots')}"
    
    except Exception as e:
        logger.error(f"Error finding slots: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


# ==================== DOCUMENT PROCESSING TOOLS ====================

@tool
def extract_text_from_document(file_path: str) -> str:
    """
    Extract text from a document using OCR.
    
    Supports images (PNG, JPG) and PDFs.
    
    Args:
        file_path: Path to the document file
    
    Returns:
        Extracted text or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.document_processor import DocumentProcessorModule
        module = DocumentProcessorModule(_database)
        
        result = module.execute("extract_text", {"file_path": file_path})
        
        if result.get("success"):
            doc_id = result.get("doc_id")
            text = result.get("text", "")
            length = result.get("length", 0)
            
            preview = text[:300] + "..." if len(text) > 300 else text
            
            return f"""✅ Text extracted successfully!

Document ID: {doc_id}
Characters: {length:,}

Preview:
{preview}"""
        
        return f"❌ {result.get('error', 'Failed to extract text')}"
    
    except Exception as e:
        logger.error(f"Error extracting text: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@tool
def process_invoice_ocr(file_path: str) -> str:
    """
    Process an invoice with OCR and extract structured data.
    
    Extracts: invoice number, vendor, amount, date.
    
    Args:
        file_path: Path to the invoice file
    
    Returns:
        Parsed invoice data or error message
    """
    try:
        if not _database:
            return "❌ Database not initialized"
        
        from src.modules.document_processor import DocumentProcessorModule
        module = DocumentProcessorModule(_database)
        
        result = module.execute("parse_invoice", {"file_path": file_path})
        
        if result.get("success"):
            invoice_data = result.get("invoice_data", {})
            doc_id = result.get("doc_id")
            
            return f"""✅ Invoice processed with OCR!

Document ID: {doc_id}
Invoice #: {invoice_data.get('invoice_number', 'N/A')}
Vendor: {invoice_data.get('vendor', 'Unknown')}
Amount: ${invoice_data.get('total', 0):.2f} {invoice_data.get('currency', 'USD')}
Date: {invoice_data.get('date', 'N/A')}"""
        
        return f"❌ {result.get('error', 'Failed to process invoice')}"
    
    except Exception as e:
        logger.error(f"Error processing invoice OCR: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


# ==================== MULTI-STEP WORKFLOW TOOL ====================

@tool
def handle_complex_task(task_description: str) -> str:
    """
    Handle complex multi-step tasks using the modular pipeline.
    
    This tool automatically:
    1. Plans the task into steps (Planner)
    2. Routes each step to the appropriate module (Router)
    3. Executes all steps (Executor)
    4. Aggregates results into a coherent response (Aggregator)
    
    Use this for requests that require multiple operations across different domains,
    such as "Process this invoice and check if we're over budget" or
    "Create a ticket, analyze sentiment, and schedule a follow-up call".
    
    Args:
        task_description: Natural language description of the complex task
    
    Returns:
        Aggregated result from all steps or error message
    """
    try:
        if not _planner or not _executor or not _aggregator:
            return "❌ Modular pipeline not initialized"
        
        logger.info(f"Handling complex task: {task_description}")
        
        # 1. Plan the task
        tasks = _planner.plan(task_description)
        
        if not tasks:
            return "❌ Failed to plan the task. Please rephrase your request."
        
        logger.info(f"Planned {len(tasks)} steps")
        
        # 2. Execute all tasks
        results = _executor.execute_tasks(tasks)
        
        if not results:
            return "❌ Failed to execute the task steps."
        
        # 3. Aggregate results
        final_response = _aggregator.aggregate(results)
        
        return final_response
    
    except Exception as e:
        logger.error(f"Error in complex task handling: {e}", exc_info=True)
        return f"❌ Error handling complex task: {str(e)}"
