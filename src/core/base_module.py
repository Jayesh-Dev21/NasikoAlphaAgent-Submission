"""
Base Module - Abstract interface for all specialized modules

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseModule(ABC):
    """
    Abstract base class that defines the standard interface for all modules.
    
    All specialized modules (CustomerService, DataAnalytics, Finance, etc.)
    must inherit from this class and implement the required methods.
    
    This enables a plug-and-play architecture where modules can be easily
    added, removed, or replaced without affecting the core system.
    """

    def __init__(self, database=None):
        """
        Initialize the module with optional database connection.
        
        Args:
            database: Database instance (MongoDB or file-based)
        """
        self.database = database

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """
        Determine if this module can handle the given task.
        
        Args:
            task_type: Task type string
            
        Returns:
            bool: True if this module can handle the task, False otherwise
            
        Example task type: "create_ticket"
        """
        pass

    @abstractmethod
    def execute(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the given task and return the result.
        
        Args:
            task_type: Task type string
            params: Task parameters
            
        Returns:
            dict: Result of the task execution
            
        Raises:
            Exception: If task execution fails
            
        The result should be a clear, human-readable string that describes
        what was accomplished. It will be combined with other results by
        the Aggregator to form the final response.
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return task types this module can handle.
        
        Returns:
            list: Task type strings, e.g. ["create_ticket", "update_ticket"]
        """
        pass

    def _validate_params(self, params: Dict[str, Any], required_params: List[str]) -> bool:
        """
        Helper method to validate that required parameters are present.
        
        Args:
            params: Parameters dictionary
            required_params: List of required parameter names
            
        Returns:
            bool: True if all required params present, False otherwise
        """
        return all(param in params for param in required_params)

    def _get_param(self, params: Dict[str, Any], param_name: str, default: Any = None) -> Any:
        """
        Helper method to safely get a parameter from a task.
        
        Args:
            params: Parameters dictionary
            param_name: Name of the parameter
            default: Default value if parameter not found
            
        Returns:
            Parameter value or default
        """
        return params.get(param_name, default)
