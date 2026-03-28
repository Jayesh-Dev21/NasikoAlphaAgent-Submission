"""
Task Executor - Executes tasks sequentially using routed modules

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

import logging
from typing import Any, Dict, List

from src.core.router import TaskRouter

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Executes tasks sequentially using the appropriate modules.
    
    Takes a list of planned tasks and executes them one by one,
    collecting the results for aggregation.
    """

    def __init__(self, router: TaskRouter):
        """
        Initialize executor with a task router.
        
        Args:
            router: TaskRouter instance for module selection
        """
        self.router = router
        logger.info("TaskExecutor initialized")

    def execute_tasks(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Execute a list of tasks sequentially.
        
        Args:
            tasks: List of task dictionaries from the Planner
            
        Returns:
            List of result strings from each task execution
            
        Each task is routed to the appropriate module and executed.
        If a task fails, the error is logged and included in results.
        """
        results: List[str] = []

        logger.info(f"Executing {len(tasks)} tasks...")

        for i, task in enumerate(tasks, 1):
            task_type = task.get("type", "unknown")
            if not isinstance(task_type, str):
                task_type = "unknown"
            task_desc = task.get("description", "No description")
            logger.info(f"Task {i}/{len(tasks)}: {task_type} - {task_desc}")

            try:
                # Route task to appropriate module
                module = self.router.route(task)

                if module is None:
                    error_msg = f"No module available to handle task type: {task_type}"
                    logger.warning(error_msg)
                    results.append(f"❌ Task {i} ({task_type}) failed: {error_msg}")
                    continue

                # Execute task
                logger.debug(f"Executing task with {module.__class__.__name__}")
                result = module.execute(task_type, task.get("params", {}))

                if result.get("success"):
                    results.append(f"✓ Task {i} ({task_type}) succeeded: {result}")
                else:
                    results.append(f"❌ Task {i} ({task_type}) failed: {result.get('error', 'Unknown error')}")
                logger.info(f"Task {i} completed successfully")

            except Exception as e:
                error_msg = f"Task {i} ({task_type}) failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results.append(f"❌ {error_msg}")

        logger.info(f"Execution complete: {len(results)} results")
        return results

    def execute_single(self, task: Dict[str, Any]) -> str:
        """
        Execute a single task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Result string from task execution
        """
        results = self.execute_tasks([task])
        return results[0] if results else "No result"
