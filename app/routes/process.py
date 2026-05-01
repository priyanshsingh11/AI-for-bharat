import os
from fastapi import APIRouter, HTTPException
from app.services.ocr_service import extract_text

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "uploads")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@router.post("/process")
async def process_documents():
    """
    Reads all files from data/uploads/, extracts text,
    and saves the output as .txt in data/processed/.
    """
    processed_files = []
    output_paths = []
    
    try:
        files = os.listdir(UPLOAD_DIR)
        
        # Filter out .gitkeep or other hidden files if needed
        files = [f for f in files if not f.startswith('.')]
        
        if not files:
            return {"message": "No files found to process."}

        for filename in files:
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Skip if it's a directory
            if os.path.isdir(file_path):
                continue
                
            try:
                # Extract text
                extracted_text = extract_text(file_path)
                
                # Save to processed dir
                base_name = filename.rsplit('.', 1)[0]
                output_filename = f"{base_name}.txt"
                output_path = os.path.join(PROCESSED_DIR, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                    
                processed_files.append(filename)
                output_paths.append(f"data/processed/{output_filename}")
                
            except ValueError as ve:
                # Log unsupported types but continue processing
                print(f"Skipping {filename}: {ve}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

        return {
            "message": "Processing completed.",
            "processed_files": processed_files,
            "output_paths": output_paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
