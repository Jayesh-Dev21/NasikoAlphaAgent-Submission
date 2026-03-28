"""
Data Analytics Module for data processing and analysis.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import os
import logging
from typing import Dict, Any, List
import hashlib

from src.core.base_module import BaseModule
from src.utils.database import Database

logger = logging.getLogger(__name__)

# Try to import data libraries
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("⚠️  pandas not available. Install: pip install pandas")

try:
    import openpyxl  # For Excel support
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class DataAnalyticsModule(BaseModule):
    """
    Data analytics and processing module.
    
    Capabilities:
    - Load datasets (CSV, Excel, JSON)
    - Perform statistical analysis
    - Generate reports
    - Query data
    - Detect patterns
    """
    
    def __init__(self, database: Database):
        """Initialize module with database."""
        self.db = database
        self.datasets = {}  # In-memory cache
        logger.info("DataAnalyticsModule initialized")
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this module can handle the task type."""
        supported_tasks = [
            "load_dataset",
            "analyze_dataset",
            "analyze_data",
            "generate_report",
            "query_data",
            "detect_patterns"
        ]
        return task_type in supported_tasks
    
    def execute(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data analytics task."""
        logger.info(f"Executing {task_type} with params: {params}")
        
        try:
            if task_type == "load_dataset":
                return self._load_dataset(params)
            elif task_type == "analyze_dataset":
                return self._analyze_dataset(params)
            elif task_type == "analyze_data":
                return self._analyze_dataset(params)
            elif task_type == "generate_report":
                return self._generate_report(params)
            elif task_type == "query_data":
                return self._query_data(params)
            elif task_type == "detect_patterns":
                return self._detect_patterns(params)
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            logger.error(f"Error executing {task_type}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return ["load_dataset", "analyze_dataset", "analyze_data", "generate_report", "query_data", "detect_patterns"]
    
    # ==================== Private Methods ====================
    
    def _load_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load a dataset from file."""
        file_path = self._get_param(params, "file_path")
        
        if not file_path:
            return {"success": False, "error": "file_path is required"}
        
        if not PANDAS_AVAILABLE:
            return {"success": False, "error": "pandas library not available"}
        
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        
        try:
            # Detect file type
            ext = file_path.split('.')[-1].lower()
            
            if ext == 'csv':
                df = pd.read_csv(file_path)
            elif ext in ['xlsx', 'xls']:
                if not EXCEL_AVAILABLE:
                    return {"success": False, "error": "openpyxl library not available for Excel files"}
                df = pd.read_excel(file_path)
            elif ext == 'json':
                df = pd.read_json(file_path)
            else:
                return {"success": False, "error": f"Unsupported file type: {ext}"}
            
            # Generate dataset ID
            dataset_id = hashlib.md5(file_path.encode()).hexdigest()[:12]
            
            # Cache in memory
            self.datasets[dataset_id] = df
            
            # Save metadata to database
            self.db.save_dataset(dataset_id, {
                "name": os.path.basename(file_path),
                "file_path": file_path,
                "file_type": ext,
                "rows": len(df),
                "columns": df.columns.tolist()
            })
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "rows": len(df),
                "columns": df.columns.tolist(),
                "file_type": ext
            }
        
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a dataset."""
        dataset_id = self._get_param(params, "dataset_id")
        
        if not dataset_id:
            return {"success": False, "error": "dataset_id is required"}
        
        if dataset_id not in self.datasets:
            return {"success": False, "error": f"Dataset not loaded: {dataset_id}"}
        
        df = self.datasets[dataset_id]
        
        # Basic statistics
        analysis = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "summary_stats": {}
        }
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            analysis["summary_stats"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "std": float(df[col].std())
            }
        
        return {"success": True, "dataset_id": dataset_id, "analysis": analysis}
    
    def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a report from dataset."""
        dataset_id = self._get_param(params, "dataset_id")
        report_type = self._get_param(params, "report_type", "summary")
        
        if not dataset_id:
            return {"success": False, "error": "dataset_id is required"}
        
        if dataset_id not in self.datasets:
            return {"success": False, "error": f"Dataset not loaded: {dataset_id}"}
        
        df = self.datasets[dataset_id]
        
        report = {
            "dataset_id": dataset_id,
            "report_type": report_type,
            "generated_at": pd.Timestamp.now().isoformat(),
            "rows": len(df)
        }
        
        if report_type == "summary":
            report["summary"] = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "sample_data": df.head(5).to_dict('records')
            }
        
        return {"success": True, "report": report}
    
    def _query_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query dataset."""
        dataset_id = self._get_param(params, "dataset_id")
        query = self._get_param(params, "query")
        
        if not dataset_id:
            return {"success": False, "error": "dataset_id is required"}
        
        if dataset_id not in self.datasets:
            return {"success": False, "error": f"Dataset not loaded: {dataset_id}"}
        
        df = self.datasets[dataset_id]
        
        # Simple query: return top N rows
        limit = self._get_param(params, "limit", 10)
        results = df.head(limit).to_dict('records')
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "results_count": len(results),
            "results": results
        }
    
    def _detect_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns in dataset."""
        dataset_id = self._get_param(params, "dataset_id")
        
        if not dataset_id:
            return {"success": False, "error": "dataset_id is required"}
        
        if dataset_id not in self.datasets:
            return {"success": False, "error": f"Dataset not loaded: {dataset_id}"}
        
        df = self.datasets[dataset_id]
        patterns = []
        
        # Find duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            patterns.append({"type": "duplicates", "count": int(duplicates)})
        
        # Find columns with many missing values
        missing = df.isnull().sum()
        high_missing = missing[missing > len(df) * 0.5]
        if len(high_missing) > 0:
            patterns.append({
                "type": "high_missing_values",
                "columns": high_missing.index.tolist()
            })
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "patterns_found": len(patterns),
            "patterns": patterns
        }
