"""
Task executor for running tasks through appropriate modules.
"""
from typing import List, Dict, Any
from core.router import TaskRouter
import logging

logger = logging.getLogger(__name__)


class Executor:
    """Executes tasks using the appropriate modules."""
    
    def __init__(self, router: TaskRouter):
        self.router = router
    
    def execute(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a list of tasks and return results."""
        results = []
        
        for task in tasks:
            try:
                module = self.router.route(task)
                
                if module:
                    logger.info(f"Executing task '{task.get('description')}' with {module.name}")
                    result = module.execute(task)
                    results.append({
                        "task": task,
                        "status": "success",
                        "result": result,
                        "module": module.name
                    })
                else:
                    logger.warning(f"No module found for task: {task}")
                    results.append({
                        "task": task,
                        "status": "no_handler",
                        "result": {"message": "No module available to handle this task"},
                        "module": None
                    })
            except Exception as e:
                logger.error(f"Error executing task: {e}", exc_info=True)
                results.append({
                    "task": task,
                    "status": "error",
                    "result": {"error": str(e)},
                    "module": None
                })
        
        return results
