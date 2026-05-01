import os
import json
from app.services.extraction_service import extract_tender_criteria, extract_bidder_data

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
EXTRACTED_DIR = os.path.join(PROJECT_ROOT, "data", "extracted")

os.makedirs(EXTRACTED_DIR, exist_ok=True)

def run_extraction_pipeline() -> dict:
    """
    Iterates through all .json files in data/processed/, calls appropriate
    extraction method based on filename, and saves output to data/extracted/.
    """
    summary = {
        "processed_files": [],
        "errors": []
    }
    
    if not os.path.exists(PROCESSED_DIR):
        summary["errors"].append("Processed directory not found.")
        return summary
        
    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.json')]
    
    for filename in files:
        file_path = os.path.join(PROCESSED_DIR, filename)
        output_filename = filename
        output_path = os.path.join(EXTRACTED_DIR, output_filename)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                pages_data = json.load(f)
                
            # Convert JSON array of pages to a single string for LLM extraction context
            text_content = ""
            for page_data in pages_data:
                text_content += f"Page {page_data.get('page', 'Unknown')}:\n{page_data.get('text', '')}\n\n"
                
            # Truncate text to avoid sending excessively large context to the LLM (e.g. max 15000 chars)
            max_chars = 15000
            if len(text_content) > max_chars:
                print(f"Truncating {filename} from {len(text_content)} to {max_chars} characters.")
                text_content = text_content[:max_chars]
                
            print(f"Processing file: {filename} for extraction...")
            
            # Detect file type
            if "tender" in filename.lower():
                extracted_data = extract_tender_criteria(text_content)
                print(f"Extracted tender criteria from {filename}")
            else:
                extracted_data = extract_bidder_data(text_content)
                print(f"Extracted bidder data from {filename}")
                
            # Save extracted JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=4)
                
            summary["processed_files"].append(output_filename)
            print(f"Successfully saved extraction to {output_filename}")
            
        except Exception as e:
            error_msg = f"Failed to extract data from {filename}: {str(e)}"
            summary["errors"].append(error_msg)
            print(error_msg)
            
    return summary

def run_evaluation_pipeline() -> dict:
    """
    Cross-references extracted tender criteria with extracted bidder data,
    evaluates them, generates LLM-refined explanations, and saves to data/results/.
    """
    from app.services.rule_engine import evaluate_bidder
    from app.services.explain_service import process_evaluations_with_explanations
    
    summary = {
        "processed_files": [],
        "errors": []
    }
    
    RESULTS_DIR = os.path.join(PROJECT_ROOT, "data", "results")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    if not os.path.exists(EXTRACTED_DIR):
        summary["errors"].append("Extracted directory not found.")
        return summary
        
    files = [f for f in os.listdir(EXTRACTED_DIR) if f.endswith('.json')]
    
    # 1. Find tender criteria
    tender_file = next((f for f in files if "tender" in f.lower()), None)
    if not tender_file:
        summary["errors"].append("No tender JSON found in extracted data.")
        return summary
        
    with open(os.path.join(EXTRACTED_DIR, tender_file), "r", encoding="utf-8") as f:
        tender_criteria = json.load(f)
        
    if not isinstance(tender_criteria, list):
        summary["errors"].append("Tender criteria must be a JSON array.")
        return summary
        
    # 2. Find and evaluate bidder data
    bidder_files = [f for f in files if "tender" not in f.lower()]
    
    for bidder_file in bidder_files:
        try:
            with open(os.path.join(EXTRACTED_DIR, bidder_file), "r", encoding="utf-8") as f:
                bidder_data = json.load(f)
                
            # Load the original processed pages for evidence extraction
            pages_data = []
            processed_file_path = os.path.join(PROCESSED_DIR, bidder_file)
            if os.path.exists(processed_file_path):
                with open(processed_file_path, "r", encoding="utf-8") as f:
                    pages_data = json.load(f)
                
            print(f"Evaluating {bidder_file} against tender criteria...")
            
            # Rule Engine Base Evaluation
            eval_results = evaluate_bidder(tender_criteria, bidder_data)
            
            # Explainability Layer with Evidence Extraction
            evaluations_list = process_evaluations_with_explanations(eval_results, pages=pages_data)
            
            # Compute AI Status
            ai_status = "Eligible"
            passed = sum(1 for e in evaluations_list if e.get("result") == "pass")
            failed = sum(1 for e in evaluations_list if e.get("result") == "fail")
            review = sum(1 for e in evaluations_list if e.get("result") == "review")
            total = len(evaluations_list)
            for ev in evaluations_list:
                if ev.get("result") == "fail":
                    ai_status = "Not Eligible"
                    break
                elif ev.get("result") == "review":
                    ai_status = "Needs Review"

            final_output = {
                "ai_status": ai_status,
                "human_status": None,
                "final_status": ai_status,
                "reviewed": False,
                "review_timestamp": None,
                "summary": f"{passed}/{total} criteria passed",
                "passed": passed,
                "failed": failed,
                "needs_review": review,
                "total": total,
                "evaluations": evaluations_list
            }
            
            # Save final results
            output_path = os.path.join(RESULTS_DIR, bidder_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_output, f, indent=4)
                
            summary["processed_files"].append(bidder_file)
            print(f"Successfully saved evaluation for {bidder_file}")
            
        except Exception as e:
            error_msg = f"Failed to evaluate {bidder_file}: {str(e)}"
            summary["errors"].append(error_msg)
            print(error_msg)
            
    return summary
