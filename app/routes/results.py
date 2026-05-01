import os
import json
from fastapi import APIRouter

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "data", "results")

@router.get("/results")
async def get_results():
    """Returns all evaluation results for display in the frontend."""
    if not os.path.exists(RESULTS_DIR):
        return {"results": []}
    
    results = []
    for filename in sorted(os.listdir(RESULTS_DIR)):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(RESULTS_DIR, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append({"filename": filename, "data": data})
        except Exception:
            continue
    
    return {"results": results}
