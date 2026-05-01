import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "data", "results")

class ReviewRequest(BaseModel):
    bidder: str
    human_status: Literal["Eligible", "Not Eligible", "Needs Review"]

@router.post("/review")
async def human_review(request: ReviewRequest):
    """
    Accepts a human reviewer's final decision for a bidder.
    Updates the evaluation JSON to lock in the final status without deleting the AI's evidence.
    """
    bidder_filename = request.bidder
    if not bidder_filename.endswith(".json"):
        bidder_filename += ".json"
        
    file_path = os.path.join(RESULTS_DIR, bidder_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Result file for bidder '{request.bidder}' not found.")
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Ensure it's the new wrapped dictionary structure
        if not isinstance(data, dict) or "evaluations" not in data:
            raise HTTPException(status_code=400, detail="Result file is not in the correct format for review.")
            
        previous_status = data.get("final_status", data.get("ai_status", "Unknown"))
        
        # Update fields
        data["human_status"] = request.human_status
        data["final_status"] = request.human_status
        data["reviewed"] = True
        data["review_timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Save back to disk
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        print(f"Human Review Log: {request.bidder} | Prev: {previous_status} -> New: {request.human_status}")
        
        return {
            "message": "Review submitted successfully.",
            "bidder": request.bidder,
            "final_status": data["final_status"],
            "timestamp": data["review_timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
