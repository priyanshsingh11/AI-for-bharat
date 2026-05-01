import os
import shutil
from fastapi import UploadFile

# Use an absolute path based on the project root to avoid cwd issues
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "uploads")

# Ensure directory is created
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_files(file: UploadFile) -> str:
    """Saves the uploaded file to the data/uploads directory."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return a relative path for the API response
    return f"data/uploads/{file.filename}"
