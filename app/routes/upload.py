import os
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.file_service import save_files

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def validate_file_extension(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@router.post("/upload")
async def upload_files(
    tender_file: UploadFile = File(...),
    bidder_files: List[UploadFile] = File(...)
):
    # Validate tender file
    if not validate_file_extension(tender_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for tender_file. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    # Validate bidder files
    for file in bidder_files:
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for bidder_files ({file.filename}). Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    try:
        tender_path = await save_files(tender_file)
        
        bidder_paths = []
        for file in bidder_files:
            path = await save_files(file)
            bidder_paths.append(path)
            
        return {
            "message": "Files uploaded successfully",
            "tender_file_path": tender_path,
            "bidder_file_paths": bidder_paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving files: {str(e)}")
