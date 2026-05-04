import os
import fitz  # PyMuPDF
from typing import List, Dict, Any

def extract_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from all pages of a PDF using PyMuPDF."""
    pages = []
    try:
        with fitz.open(file_path) as doc:
            for i, page in enumerate(doc):
                pages.append({
                    "page": i + 1,
                    "text": page.get_text().strip()
                })
    except Exception as e:
        print(f"Error extracting from PDF: {e}")
        
    return pages

def extract_text(file_path: str) -> List[Dict[str, Any]]:
    """Detects file type and extracts text from PDFs only."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = file_path.rsplit('.', 1)[-1].lower()
    
    if ext == 'pdf':
        return extract_from_pdf(file_path)
    elif ext in ['jpg', 'jpeg', 'png']:
        # Return a message for images since OCR is disabled for memory efficiency
        return [
            {
                "page": "image",
                "text": "[OCR Disabled: To keep the app fast and within memory limits, image OCR has been disabled. Please upload text-based PDFs instead.]"
            }
        ]
    else:
        raise ValueError(f"Unsupported file format: {ext}")
