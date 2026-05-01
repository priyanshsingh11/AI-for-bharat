import os
import json
from app.services.extraction_service import extract_tender_criteria, extract_bidder_data

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
EXTRACTED_DIR = os.path.join(PROJECT_ROOT, "data", "extracted")

os.makedirs(EXTRACTED_DIR, exist_ok=True)

def run_extraction_pipeline() -> dict:
    """
    Iterates through all .txt files in data/processed/, calls appropriate
    extraction method based on filename, and saves output to data/extracted/.
    """
    summary = {
        "processed_files": [],
        "errors": []
    }
    
    if not os.path.exists(PROCESSED_DIR):
        summary["errors"].append("Processed directory not found.")
        return summary
        
    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.txt')]
    
    for filename in files:
        file_path = os.path.join(PROCESSED_DIR, filename)
        output_filename = filename.replace('.txt', '.json')
        output_path = os.path.join(EXTRACTED_DIR, output_filename)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
                
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
