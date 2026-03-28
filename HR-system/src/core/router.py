"""
Task router for directing tasks to appropriate modules.
"""
from typing import Dict, Any, Optional, List
from core.base_module import BaseModule


class TaskRouter:
    """Routes tasks to appropriate modules."""
    
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
    
    def register_module(self, module: BaseModule):
        """Register a module with the router."""
        self.modules[module.name] = module
    
    def route(self, task: Dict[str, Any]) -> Optional[BaseModule]:
        """Find the best module to handle a task."""
        task_type = task.get("type", "general")
        
        # Direct mapping for known task types
        type_to_module = {
            "schedule": "calendar_manager",
            "recruit": "recruiter",
            "research": "researcher",
            "interview_prep": "interview_coach",
            "culture_fit": "culture_analyzer"
        }
        
        module_name = type_to_module.get(task_type)
        if module_name and module_name in self.modules:
            return self.modules[module_name]
        
        # Fallback: ask each module if it can handle the task
        for module in self.modules.values():
            if module.can_handle(task):
                return module
        
        return None
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities from all registered modules."""
        return {
            name: module.get_capabilities()
            for name, module in self.modules.items()
        }
