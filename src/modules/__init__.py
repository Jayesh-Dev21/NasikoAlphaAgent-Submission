"""Specialized business modules for Unified Business Agent."""

from src.modules.customer_service import CustomerServiceModule
from src.modules.data_analytics import DataAnalyticsModule
from src.modules.finance import FinanceModule
from src.modules.scheduling import SchedulingModule
from src.modules.document_processor import DocumentProcessorModule

__all__ = [
    "CustomerServiceModule",
    "DataAnalyticsModule",
    "FinanceModule",
    "SchedulingModule",
    "DocumentProcessorModule",
]
