"""
Finance Module for expense tracking and invoice processing.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.core.base_module import BaseModule
from src.utils.document_ai import get_document_ai
from src.utils.gmail import get_gmail_client
from src.utils.database import Database

logger = logging.getLogger(__name__)


class FinanceModule(BaseModule):
    """
    Finance and accounting module.
    
    Capabilities:
    - Track expenses and categorize transactions
    - Process invoices with OCR
    - Check budgets and spending limits
    - Generate financial reports
    """
    
    def __init__(self, database: Database):
        """Initialize module with database."""
        self.db = database
        self.doc_ai = get_document_ai()
        self.gmail = get_gmail_client()
        
        # Default budget limits (in production, load from config/database)
        self.budget_limits = {
            "monthly": 20000.0,
            "office_supplies": 5000.0,
            "travel": 10000.0,
            "software": 3000.0,
            "general": 2000.0
        }
        
        logger.info("FinanceModule initialized")
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this module can handle the task type."""
        supported_tasks = [
            "add_expense",
            "create_expense",
            "get_expenses",
            "process_invoice",
            "financial_report",
            "generate_financial_report",
            "check_budget",
            "categorize_expense"
        ]
        return task_type in supported_tasks
    
    def execute(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a finance task."""
        logger.info(f"Executing {task_type} with params: {params}")
        
        try:
            if task_type == "add_expense":
                return self._add_expense(params)
            elif task_type == "create_expense":
                return self._add_expense(params)
            elif task_type == "get_expenses":
                return self._get_expenses(params)
            elif task_type == "process_invoice":
                return self._process_invoice(params)
            elif task_type == "check_budget":
                return self._check_budget(params)
            elif task_type == "generate_financial_report":
                return self._generate_report(params)
            elif task_type == "financial_report":
                return self._generate_report(params)
            elif task_type == "categorize_expense":
                return self._categorize_expense(params)
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            logger.error(f"Error executing {task_type}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return ["add_expense", "get_expenses", "process_invoice", "check_budget", "generate_financial_report", "categorize_expense"]
    
    # ==================== Private Methods ====================
    
    def _add_expense(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an expense."""
        amount = self._get_param(params, "amount")
        category = self._get_param(params, "category", "general")
        vendor = self._get_param(params, "vendor", "")
        description = self._get_param(params, "description", "")
        date = self._get_param(params, "date", datetime.now().isoformat())
        
        if not amount:
            return {"success": False, "error": "amount is required"}
        
        expense_id = self.db.create_expense({
            "amount": float(amount),
            "category": category,
            "vendor": vendor,
            "description": description,
            "date": date,
            "status": "pending"
        })
        
        return {"success": True, "expense_id": expense_id, "amount": amount, "category": category}
    
    def _get_expenses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get expenses with optional filters."""
        filters = self._get_param(params, "filters", {})
        expenses = self.db.get_expenses(filters)
        
        total = sum(e.get("amount", 0) for e in expenses)
        
        return {"success": True, "count": len(expenses), "total": total, "expenses": expenses}
    
    def _process_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice with OCR."""
        file_path = self._get_param(params, "file_path")
        
        if not file_path:
            return {"success": False, "error": "file_path is required"}
        
        # Extract and parse invoice
        result = self.doc_ai.process_document(file_path, document_type="invoice")
        
        if not result.get("success"):
            return result
        
        invoice_data = result.get("parsed_data", {})
        
        # Create expense from invoice
        if invoice_data.get("total"):
            expense_id = self.db.create_expense({
                "amount": invoice_data.get("total", 0),
                "vendor": invoice_data.get("vendor", "Unknown"),
                "description": f"Invoice {invoice_data.get('invoice_number', 'N/A')}",
                "date": invoice_data.get("date", datetime.now().isoformat()),
                "category": "invoices",
                "status": "pending"
            })
            result["expense_id"] = expense_id
        
        return result
    
    def _check_budget(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check budget status."""
        category = self._get_param(params, "category", "monthly")
        period = self._get_param(params, "period", "month")  # month, week, year
        
        # Calculate date range
        now = datetime.now()
        if period == "month":
            start_date = now.replace(day=1).isoformat()
        elif period == "week":
            start_date = (now - timedelta(days=7)).isoformat()
        else:
            start_date = now.replace(month=1, day=1).isoformat()
        
        # Get expenses in period
        expenses = self.db.get_expenses({})  # In production, filter by date
        period_expenses = [e for e in expenses if e.get("date", "") >= start_date]
        
        # Calculate total spending
        if category == "monthly":
            total_spent = sum(e.get("amount", 0) for e in period_expenses)
        else:
            total_spent = sum(e.get("amount", 0) for e in period_expenses if e.get("category") == category)
        
        budget_limit = self.budget_limits.get(category, 0)
        remaining = budget_limit - total_spent
        percentage_used = (total_spent / budget_limit * 100) if budget_limit > 0 else 0
        
        status = "ok" if percentage_used < 80 else "warning" if percentage_used < 100 else "over_budget"
        
        return {
            "success": True,
            "category": category,
            "period": period,
            "budget_limit": budget_limit,
            "total_spent": total_spent,
            "remaining": remaining,
            "percentage_used": round(percentage_used, 2),
            "status": status,
            "expense_count": len(period_expenses)
        }
    
    def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial report."""
        period = self._get_param(params, "period", "month")
        
        expenses = self.db.get_expenses({})
        expense_items = list(expenses)
        
        # Calculate totals by category
        by_category = {}
        for expense in expense_items:
            category = expense.get("category", "general")
            by_category[category] = by_category.get(category, 0) + expense.get("amount", 0)
        
        total = sum(expense.get("amount", 0) for expense in expense_items)
        
        return {
            "success": True,
            "period": period,
            "total_expenses": total,
            "expense_count": len(expense_items),
            "by_category": by_category,
            "top_categories": sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _categorize_expense(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-categorize an expense based on description."""
        description = self._get_param(params, "description", "").lower()
        vendor = self._get_param(params, "vendor", "").lower()
        
        # Simple keyword-based categorization
        if any(word in description + vendor for word in ["office", "supplies", "paper", "pen"]):
            category = "office_supplies"
        elif any(word in description + vendor for word in ["flight", "hotel", "travel", "uber", "airbnb"]):
            category = "travel"
        elif any(word in description + vendor for word in ["software", "saas", "subscription", "cloud"]):
            category = "software"
        else:
            category = "general"
        
        return {"success": True, "category": category, "confidence": "medium"}
