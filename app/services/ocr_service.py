import os
import fitz  # PyMuPDF
import easyocr

# Initialize EasyOCR Reader.
# 'en' for English. Setting gpu=False by default to avoid issues on machines without CUDA,
# though it can be changed to True if GPU is available.
reader = easyocr.Reader(['en'], gpu=False)

def extract_from_pdf(file_path: str) -> str:
    """Extract text from all pages of a PDF."""
    text_content = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_content.append(page.get_text())
    return "\n".join(text_content)

def extract_from_image(file_path: str) -> str:
    """Extract text from an image using EasyOCR."""
    # The reader returns a list of tuples: (bbox, text, confidence)
    results = reader.readtext(file_path)
    text_content = [res[1] for res in results]
    return " ".join(text_content)

def extract_text(file_path: str) -> str:
    """Detects file type and extracts text accordingly."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = file_path.rsplit('.', 1)[-1].lower()
    
    if ext == 'pdf':
        return extract_from_pdf(file_path)
    elif ext in ['jpg', 'jpeg', 'png']:
        return extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file format for OCR: {ext}")
