"""
Document Processor Module for OCR and document processing.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import logging
from typing import Dict, Any, List

from src.core.base_module import BaseModule
from src.utils.document_ai import get_document_ai
from src.utils.database import Database

logger = logging.getLogger(__name__)


class DocumentProcessorModule(BaseModule):
    """
    Document processing module.
    
    Capabilities:
    - Extract text from images and PDFs using OCR
    - Parse invoices and receipts
    - Validate documents
    - Batch process multiple documents
    """
    
    def __init__(self, database: Database):
        """Initialize module with database."""
        self.db = database
        self.doc_ai = get_document_ai()
        logger.info("DocumentProcessorModule initialized")
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this module can handle the task type."""
        supported_tasks = [
            "extract_text",
            "extract_document",
            "process_document",
            "parse_invoice",
            "parse_receipt",
            "validate_document",
            "batch_process_documents"
        ]
        return task_type in supported_tasks
    
    def execute(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a document processing task."""
        logger.info(f"Executing {task_type} with params: {params}")
        
        try:
            if task_type == "extract_text":
                return self._extract_text(params)

            elif task_type == "extract_document":
                return self._extract_text(params)
            
            elif task_type == "process_document":
                return self._process_document(params)
            
            elif task_type == "parse_invoice":
                return self._parse_invoice(params)
            
            elif task_type == "parse_receipt":
                return self._parse_receipt(params)
            
            elif task_type == "validate_document":
                return self._validate_document(params)
            
            elif task_type == "batch_process_documents":
                return self._batch_process(params)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
        
        except Exception as e:
            logger.error(f"Error executing {task_type}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return [
            "extract_text",
            "extract_document",
            "process_document",
            "parse_invoice",
            "parse_receipt",
            "validate_document",
            "batch_process_documents"
        ]
    
    # ==================== Private Methods ====================
    
    def _extract_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from a document."""
        file_path = self._get_param(params, "file_path")
        
        if not file_path:
            return {"success": False, "error": "file_path is required"}
        
        # Extract text
        text = self.doc_ai.extract_text(file_path)
        
        if not text:
            return {
                "success": False,
                "error": "Failed to extract text from document"
            }
        
        # Save to database
        doc_id = self.db.save_document({
            "file_name": file_path.split('/')[-1],
            "file_path": file_path,
            "file_type": file_path.split('.')[-1] if '.' in file_path else "unknown",
            "extracted_text": text,
            "document_type": "text_extraction"
        })
        
        return {
            "success": True,
            "doc_id": doc_id,
            "text": text,
            "length": len(text)
        }
    
    def _process_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a document with optional type-specific parsing."""
        file_path = self._get_param(params, "file_path")
        document_type = self._get_param(params, "document_type")  # invoice, receipt, or None
        
        if not file_path:
            return {"success": False, "error": "file_path is required"}
        
        # Process document
        result = self.doc_ai.process_document(file_path, document_type)
        
        if not result.get("success"):
            return result
        
        # Save to database
        doc_id = self.db.save_document({
            "file_name": file_path.split('/')[-1],
            "file_path": file_path,
            "file_type": result.get("file_type", "unknown"),
            "extracted_text": result.get("extracted_text", ""),
            "document_type": document_type or "general",
            "metadata": result.get("parsed_data", {})
        })
        
        result["doc_id"] = doc_id
        return result
    
    def _parse_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse an invoice document."""
        # Can accept either file_path or text
        file_path = self._get_param(params, "file_path")
        text = self._get_param(params, "text")
        
        if not file_path and not text:
            return {"success": False, "error": "Either file_path or text is required"}
        
        # Extract text if needed
        if not text:
            text = self.doc_ai.extract_text(file_path)
        
        if not text:
            return {"success": False, "error": "Failed to extract text"}
        
        # Parse invoice
        invoice_data = self.doc_ai.parse_invoice(text)
        
        # Save to database
        doc_id = self.db.save_document({
            "file_name": file_path.split('/')[-1] if file_path else "text_input",
            "file_path": file_path or "",
            "file_type": "invoice",
            "extracted_text": text,
            "document_type": "invoice",
            "metadata": invoice_data
        })
        
        return {
            "success": True,
            "doc_id": doc_id,
            "invoice_data": invoice_data
        }
    
    def _parse_receipt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a receipt document."""
        file_path = self._get_param(params, "file_path")
        text = self._get_param(params, "text")
        
        if not file_path and not text:
            return {"success": False, "error": "Either file_path or text is required"}
        
        # Extract text if needed
        if not text:
            text = self.doc_ai.extract_text(file_path)
        
        if not text:
            return {"success": False, "error": "Failed to extract text"}
        
        # Parse receipt
        receipt_data = self.doc_ai.parse_receipt(text)
        
        # Save to database
        doc_id = self.db.save_document({
            "file_name": file_path.split('/')[-1] if file_path else "text_input",
            "file_path": file_path or "",
            "file_type": "receipt",
            "extracted_text": text,
            "document_type": "receipt",
            "metadata": receipt_data
        })
        
        return {
            "success": True,
            "doc_id": doc_id,
            "receipt_data": receipt_data
        }
    
    def _validate_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a document."""
        doc_id = self._get_param(params, "doc_id")
        
        if not doc_id:
            return {"success": False, "error": "doc_id is required"}
        
        # Get document from database
        doc = self.db.get_document(doc_id)
        
        if not doc:
            return {"success": False, "error": f"Document not found: {doc_id}"}
        
        # Basic validation
        is_valid = True
        errors = []
        
        # Check if text was extracted
        if not doc.get("extracted_text"):
            is_valid = False
            errors.append("No text extracted")
        
        # Check if metadata exists for typed documents
        doc_type = doc.get("document_type")
        if doc_type in ["invoice", "receipt"]:
            if not doc.get("metadata"):
                is_valid = False
                errors.append("No metadata parsed")
        
        return {
            "success": True,
            "doc_id": doc_id,
            "is_valid": is_valid,
            "errors": errors,
            "document": doc
        }
    
    def _batch_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple documents."""
        file_paths = self._get_param(params, "file_paths", [])
        document_type = self._get_param(params, "document_type")
        
        if not file_paths:
            return {"success": False, "error": "file_paths list is required"}
        
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            try:
                result = self._process_document({
                    "file_path": file_path,
                    "document_type": document_type
                })
                
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
                
                results.append({
                    "file_path": file_path,
                    "result": result
                })
            
            except Exception as e:
                failed += 1
                results.append({
                    "file_path": file_path,
                    "result": {"success": False, "error": str(e)}
                })
        
        return {
            "success": True,
            "total": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results
        }
