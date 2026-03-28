"""
Base module interface for the modular agent architecture.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseModule(ABC):
    """Base class for all agent modules."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Determine if this module can handle the given task."""
        pass
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task and return results."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this module provides."""
        return []
