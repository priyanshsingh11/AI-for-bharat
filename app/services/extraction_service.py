import json
import re
from typing import Dict, Any, List, Union
from app.services.llm_service import call_llm, safe_parse

def safe_json_loads(text: str) -> Any:
    """Wrapper around safe_parse for backwards compat."""
    return safe_parse(text)

def combine_pages_to_text(pages: Union[str, List[Dict[str, Any]]]) -> str:
    """Helper to combine a list of page dicts into a single string if necessary."""
    if isinstance(pages, list):
        return " ".join([str(p.get("text", "")) for p in pages])
    return pages

def extract_tender_criteria(pages: Union[str, List[Dict[str, Any]]], retries: int = 1) -> List[Dict[str, Any]]:
    """
    Extracts eligibility criteria from tender text using the LLM.
    """
    text = combine_pages_to_text(pages)
    prompt = f"""Extract eligibility criteria from the following tender text.

Return ONLY valid JSON. Do NOT include:
- explanations or commentary
- markdown or code blocks
- newlines inside string values
- comments

The output MUST be a JSON array of objects with this exact schema:
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
            elif isinstance(data, dict):
                # LLM may wrap the array in a dict e.g. {"criteria": [...]}
                # Find the first list value in the dict
                for v in data.values():
                    if isinstance(v, list):
                        normalized_list = []
                        for item in v:
                            normalized_list.append({
                                "criterion": item.get("criterion"),
                                "operator": item.get("operator"),
                                "value": item.get("value"),
                                "mandatory": item.get("mandatory")
                            })
                        return normalized_list
                raise ValueError("Expected a JSON array or a dict containing a list")
            else:
                raise ValueError("Expected a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON (attempt {attempt + 1}): {e}")
            if attempt == retries:
                return []
    
    return []

def extract_bidder_data(pages: Union[str, List[Dict[str, Any]]], retries: int = 1) -> Dict[str, Any]:
    """
    Extracts bidder information from bidder text using the LLM.
    """
    text = combine_pages_to_text(pages)
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
