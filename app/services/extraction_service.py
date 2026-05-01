import json
from typing import Dict, Any, List
from app.services.llm_service import call_llm

def safe_json_loads(text: str) -> Any:
    """Helper to safely parse JSON and remove any markdown code block artifacts if the LLM leaked them."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())

def extract_tender_criteria(text: str, retries: int = 1) -> List[Dict[str, Any]]:
    """
    Extracts eligibility criteria from tender text using the LLM.
    """
    prompt = f"""
Extract eligibility criteria from the following tender text.

Return ONLY valid JSON. Do not include explanation.
The output MUST be a JSON array of objects, with this exact schema:
[
    {{
        "criterion": "string (e.g., turnover, experience)",
        "operator": "string (e.g., >=, <=, ==)",
        "value": number or string,
        "mandatory": boolean
    }}
]

If a value is missing, use null. 

Tender text:
{text}
"""
    
    for attempt in range(retries + 1):
        try:
            response_text = call_llm(prompt)
            data = safe_json_loads(response_text)
            
            if isinstance(data, list):
                # Normalize missing keys
                normalized_list = []
                for item in data:
                    normalized_list.append({
                        "criterion": item.get("criterion"),
                        "operator": item.get("operator"),
                        "value": item.get("value"),
                        "mandatory": item.get("mandatory")
                    })
                return normalized_list
            else:
                raise ValueError("Expected a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON (attempt {attempt + 1}): {e}")
            if attempt == retries:
                return []
    
    return []

def extract_bidder_data(text: str, retries: int = 1) -> Dict[str, Any]:
    """
    Extracts bidder information from bidder text using the LLM.
    """
    prompt = f"""
Extract bidder information from the following text.

Return ONLY valid JSON. Do not include explanation.
The output MUST be a JSON object with this exact schema:
{{
    "turnover": number (in INR),
    "gst": boolean,
    "projects": integer
}}

If a value is missing, use null.

Bidder text:
{text}
"""
    
    for attempt in range(retries + 1):
        try:
            response_text = call_llm(prompt)
            data = safe_json_loads(response_text)
            
            if isinstance(data, dict):
                # Validation & Normalization Layer
                turnover = data.get("turnover")
                gst = data.get("gst")
                projects = data.get("projects")
                
                # Ensure turnover is numeric or null
                if turnover is not None and not isinstance(turnover, (int, float)):
                    try:
                        turnover = float(turnover)
                    except ValueError:
                        turnover = None
                        
                # Ensure gst is boolean or null
                if gst is not None and not isinstance(gst, bool):
                    if str(gst).lower() in ["true", "yes", "1"]:
                        gst = True
                    elif str(gst).lower() in ["false", "no", "0"]:
                        gst = False
                    else:
                        gst = None
                        
                # Ensure projects is integer or null
                if projects is not None and not isinstance(projects, int):
                    try:
                        projects = int(float(projects))
                    except ValueError:
                        projects = None
                        
                return {
                    "turnover": turnover,
                    "gst": gst,
                    "projects": projects
                }
            else:
                raise ValueError("Expected a JSON object")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON (attempt {attempt + 1}): {e}")
            if attempt == retries:
                return {
                    "turnover": None,
                    "gst": None,
                    "projects": None
                }

    return {
        "turnover": None,
        "gst": None,
        "projects": None
    }
