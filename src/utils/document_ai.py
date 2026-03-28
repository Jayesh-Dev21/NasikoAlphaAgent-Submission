"""
Document AI utilities for OCR and document processing.

Uses Tesseract OCR for text extraction from images and PDFs.

Team Sleepyhead - Nasiko Hackathon 2026
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("⚠️  Tesseract/PIL not available. Install: pip install pytesseract Pillow")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("⚠️  PyPDF2 not available. Install: pip install PyPDF2")


class DocumentAI:
    """
    Document AI for text extraction and document processing.
    
    Features:
    - Extract text from images (PNG, JPG, etc.) using Tesseract OCR
    - Extract text from PDFs
    - Parse invoices and receipts
    - Extract structured data from documents
    """
    
    def __init__(self):
        """Initialize Document AI."""
        self.tesseract_available = TESSERACT_AVAILABLE
        self.pdf_available = PDF_AVAILABLE
        
        if self.tesseract_available:
            logger.info("✅ Tesseract OCR available")
        
        if self.pdf_available:
            logger.info("✅ PDF processing available")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using Tesseract OCR.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Extracted text
        """
        if not self.tesseract_available:
            logger.error("Tesseract not available")
            return ""
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Extract text with Tesseract
            text = pytesseract.image_to_string(image)
            
            logger.info(f"✅ Extracted {len(text)} characters from {image_path}")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Failed to extract text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Extracted text
        """
        if not self.pdf_available:
            logger.error("PyPDF2 not available")
            return ""
        
        try:
            text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            logger.info(f"✅ Extracted {len(text)} characters from {pdf_path}")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """
        Auto-detect file type and extract text.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Extracted text
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ""
        
        # Get file extension
        ext = Path(file_path).suffix.lower()
        
        # Route to appropriate extractor
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
            return self.extract_text_from_image(file_path)
        else:
            logger.error(f"Unsupported file type: {ext}")
            return ""
    
    def parse_invoice(self, text: str) -> Dict[str, Any]:
        """
        Parse invoice from extracted text.
        
        Extracts:
        - Invoice number
        - Date
        - Vendor/Supplier name
        - Total amount
        - Line items
        
        Args:
            text: Extracted text from invoice
        
        Returns:
            Parsed invoice data
        """
        invoice_data = {
            "invoice_number": None,
            "date": None,
            "vendor": None,
            "total": None,
            "currency": "USD",
            "line_items": [],
            "raw_text": text
        }
        
        try:
            # Extract invoice number
            invoice_patterns = [
                r'Invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
                r'Invoice\s+Number\s*:?\s*([A-Z0-9-]+)',
                r'INV\s*#?\s*:?\s*([A-Z0-9-]+)'
            ]
            
            for pattern in invoice_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    invoice_data["invoice_number"] = match.group(1)
                    break
            
            # Extract date
            date_patterns = [
                r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Invoice\s+Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}/\d{1,2}/\d{2,4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    invoice_data["date"] = match.group(1)
                    break
            
            # Extract vendor name (usually at top, before "Invoice" keyword)
            vendor_section = text[:500]  # Check first 500 chars
            lines = vendor_section.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and len(line) > 3 and not re.match(r'^\d+$', line):
                    # Skip lines that are just numbers or dates
                    if not re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', line):
                        invoice_data["vendor"] = line
                        break
            
            # Extract total amount
            total_patterns = [
                r'Total\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'Amount\s+Due\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'Grand\s+Total\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'Balance\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})'
            ]
            
            for pattern in total_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    invoice_data["total"] = float(amount_str)
                    break
            
            # Detect currency
            if '$' in text or 'USD' in text:
                invoice_data["currency"] = "USD"
            elif '€' in text or 'EUR' in text:
                invoice_data["currency"] = "EUR"
            elif '£' in text or 'GBP' in text:
                invoice_data["currency"] = "GBP"
            elif '₹' in text or 'INR' in text:
                invoice_data["currency"] = "INR"
            
            logger.info(f"✅ Invoice parsed: {invoice_data.get('invoice_number', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error parsing invoice: {e}")
        
        return invoice_data
    
    def parse_receipt(self, text: str) -> Dict[str, Any]:
        """
        Parse receipt from extracted text.
        
        Args:
            text: Extracted text from receipt
        
        Returns:
            Parsed receipt data
        """
        receipt_data = {
            "merchant": None,
            "date": None,
            "total": None,
            "currency": "USD",
            "items": [],
            "payment_method": None,
            "raw_text": text
        }
        
        try:
            # Extract merchant (usually first non-empty line)
            lines = text.split('\n')
            for line in lines[:10]:
                line = line.strip()
                if line and len(line) > 3:
                    receipt_data["merchant"] = line
                    break
            
            # Extract date
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
            if date_match:
                receipt_data["date"] = date_match.group(1)
            
            # Extract total
            total_patterns = [
                r'Total\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'Amount\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'Balance\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})'
            ]
            
            for pattern in total_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    receipt_data["total"] = float(amount_str)
                    break
            
            # Detect currency
            if '$' in text or 'USD' in text:
                receipt_data["currency"] = "USD"
            elif '€' in text or 'EUR' in text:
                receipt_data["currency"] = "EUR"
            
            # Detect payment method
            if 'credit' in text.lower() or 'visa' in text.lower() or 'mastercard' in text.lower():
                receipt_data["payment_method"] = "credit_card"
            elif 'cash' in text.lower():
                receipt_data["payment_method"] = "cash"
            elif 'debit' in text.lower():
                receipt_data["payment_method"] = "debit_card"
            
            logger.info(f"✅ Receipt parsed: {receipt_data.get('merchant', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error parsing receipt: {e}")
        
        return receipt_data
    
    def process_document(
        self,
        file_path: str,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process document: extract text and parse if type is specified.
        
        Args:
            file_path: Path to the document
            document_type: Type of document ('invoice', 'receipt', or None)
        
        Returns:
            Processed document data
        """
        # Extract text
        text = self.extract_text(file_path)
        
        if not text:
            return {
                "success": False,
                "error": "Failed to extract text from document"
            }
        
        result = {
            "success": True,
            "file_path": file_path,
            "file_type": Path(file_path).suffix.lower(),
            "extracted_text": text,
            "document_type": document_type
        }
        
        # Parse based on document type
        if document_type == "invoice":
            result["parsed_data"] = self.parse_invoice(text)
        elif document_type == "receipt":
            result["parsed_data"] = self.parse_receipt(text)
        else:
            result["parsed_data"] = None
        
        return result


# Global instance (singleton)
_document_ai_instance = None


def get_document_ai() -> DocumentAI:
    """Get or create DocumentAI instance (singleton)."""
    global _document_ai_instance
    
    if _document_ai_instance is None:
        _document_ai_instance = DocumentAI()
    
    return _document_ai_instance
