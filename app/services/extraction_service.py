import json
from typing import Dict, Any, List
from app.services.llm_service import call_llm

def extract_tender_criteria(text: str) -> List[Dict[str, Any]]:
    """
    Extracts eligibility criteria from tender text.
    """
    prompt = f"""
    Extract eligibility criteria from the following tender text.
    Return ONLY a valid JSON list of objects, where each object has the keys:
    - 'criterion' (string)
    - 'operator' (string, e.g., '>=', '<=', '==')
    - 'value' (number or string)
    - 'mandatory' (boolean)
    
    Tender text:
    {text}
    """
    response_text = call_llm(prompt)
    
    try:
        data = json.loads(response_text)
        if isinstance(data, list):
            # Normalize missing keys
            normalized_list = []
            for item in data:
                normalized_list.append({
                    "criterion": item.get("criterion", None),
                    "operator": item.get("operator", None),
                    "value": item.get("value", None),
                    "mandatory": item.get("mandatory", None)
                })
            return normalized_list
        return []
    except json.JSONDecodeError:
        return []

def extract_bidder_data(text: str) -> Dict[str, Any]:
    """
    Extracts bidder information from bidder text.
    """
    prompt = f"""
    Extract bidder information from the following text.
    Return ONLY a valid JSON object with the keys:
    - 'turnover' (number)
    - 'gst' (boolean)
    - 'projects' (integer)
    
    Bidder text:
    {text}
    """
    response_text = call_llm(prompt)
    
    try:
        data = json.loads(response_text)
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
    except json.JSONDecodeError:
        pass
        
    return {
        "turnover": None,
        "gst": None,
        "projects": None
    }
