"""
Task Router - Routes tasks to appropriate modules

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.base_module import BaseModule

logger = logging.getLogger(__name__)


class TaskRouter:
    """
    Routes tasks to the appropriate specialized module.
    
    Uses a combination of explicit mapping and module capability checking
    to determine which module should handle each task.
    """

    def __init__(self, modules: Optional[List[BaseModule]] = None):
        """
        Initialize router with list of available modules.
        
        Args:
            modules: List of BaseModule instances
        """
        self.modules = modules or []

        # Task type to module mapping
        self.task_map = {
            # Customer Service
            "create_ticket": "CustomerServiceModule",
            "get_ticket": "CustomerServiceModule",
            "update_ticket": "CustomerServiceModule",
            "close_ticket": "CustomerServiceModule",
            "analyze_sentiment": "CustomerServiceModule",
            "search_faq": "CustomerServiceModule",
            # Data Analytics
            "load_dataset": "DataAnalyticsModule",
            "analyze_data": "DataAnalyticsModule",
            "analyze_dataset": "DataAnalyticsModule",
            "generate_report": "DataAnalyticsModule",
            "query_data": "DataAnalyticsModule",
            "detect_patterns": "DataAnalyticsModule",
            # Finance
            "add_expense": "FinanceModule",
            "process_invoice": "FinanceModule",
            "get_expenses": "FinanceModule",
            "financial_report": "FinanceModule",
            "check_budget": "FinanceModule",
            # Scheduling
            "schedule_meeting": "SchedulingModule",
            "find_slots": "SchedulingModule",
            "create_event": "SchedulingModule",
            "cancel_event": "SchedulingModule",
            # Document Processing
            "extract_document": "DocumentProcessorModule",
            "process_document": "DocumentProcessorModule",
            "extract_text": "DocumentProcessorModule",
        }

        logger.info(f"TaskRouter initialized with {len(self.modules)} modules")

    def register_module(self, module: BaseModule):
        """Register a new module with the router."""
        self.modules.append(module)
        logger.info(f"Registered module: {module.__class__.__name__}")

    def route(self, task: Dict[str, Any]) -> Optional[BaseModule]:
        """
        Route a task to the appropriate module.
        
        Args:
            task: Task dictionary with 'type', 'description', 'params', etc.
            
        Returns:
            BaseModule instance that can handle the task, or None if no module found
            
        The routing strategy:
        1. Check explicit task_map for known task types
        2. If not found, ask each module if it can handle the task
        3. Return first module that says it can handle
        """
        task_type = task.get("type", "general_query")

        # Strategy 1: Check explicit mapping
        target_module_name = self.task_map.get(task_type)
        if target_module_name:
            for module in self.modules:
                if module.__class__.__name__ == target_module_name:
                    logger.debug(f"Routed task '{task_type}' to {target_module_name} (explicit mapping)")
                    return module

        # Strategy 2: Ask modules if they can handle
        for module in self.modules:
            try:
                if module.can_handle(task_type):
                    logger.debug(f"Routed task '{task_type}' to {module.__class__.__name__} (capability check)")
                    return module
            except Exception as e:
                logger.warning(f"Error checking {module.__class__.__name__}.can_handle(): {str(e)}")
                continue

        # No module found
        logger.warning(f"No module found to handle task type: {task_type}")
        return None

    def get_all_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get capabilities of all registered modules.
        
        Returns:
            List of capability dictionaries from all modules
        """
        capabilities = []
        for module in self.modules:
            try:
                cap = module.get_capabilities()
                capabilities.append(cap)
            except Exception as e:
                logger.error(f"Error getting capabilities from {module.__class__.__name__}: {str(e)}")
        return capabilities
