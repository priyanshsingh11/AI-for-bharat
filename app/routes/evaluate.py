from fastapi import APIRouter, HTTPException
from app.core.pipeline import run_evaluation_pipeline

router = APIRouter()

@router.post("/evaluate")
async def evaluate_data():
    """
    Triggers the evaluation and explainability pipeline.
    Reads extracted JSON from data/extracted/, compares bidder data against
    tender criteria, generates LLM-refined explanations, and saves to data/results/.
    """
    try:
        summary = run_evaluation_pipeline()
        
        if summary.get("errors") and not summary.get("processed_files"):
            raise HTTPException(status_code=500, detail={"message": "Evaluation failed", "errors": summary["errors"]})
            
        return {
            "message": "Evaluation pipeline completed.",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
