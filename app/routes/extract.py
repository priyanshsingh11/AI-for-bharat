from fastapi import APIRouter, HTTPException
from app.core.pipeline import run_extraction_pipeline

router = APIRouter()

@router.post("/extract")
async def extract_data():
    """
    Triggers the extraction pipeline.
    Reads text files from data/processed/, extracts structured JSON using the LLM,
    and saves the JSON into data/extracted/.
    """
    try:
        summary = run_extraction_pipeline()
        
        # If there were errors but also successes, we might want to return 207 Multi-Status
        # For simplicity, if everything failed, return 500, otherwise 200.
        if summary.get("errors") and not summary.get("processed_files"):
            raise HTTPException(status_code=500, detail={"message": "Extraction failed", "errors": summary["errors"]})
            
        return {
            "message": "Extraction pipeline completed.",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
