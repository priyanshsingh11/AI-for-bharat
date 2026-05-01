import json
from typing import Dict, Any, List
from app.services.llm_service import call_llm
from app.services.extraction_service import safe_json_loads

def generate_base_explanation(eval_result: Dict[str, Any]) -> str:
    """
    Generates a deterministic, rule-based text explanation based on the evaluation result.
    """
    criterion = str(eval_result.get("criterion", "Unknown criterion")).capitalize()
    required = eval_result.get("required")
    found = eval_result.get("found")
    result = eval_result.get("result", "review")
    operator = eval_result.get("operator", "==")
    
    if result == "pass":
        return f"{criterion} meets the requirement (required {operator} {required}, found {found})."
    elif result == "fail":
        if found is None:
            return f"{criterion} is missing from the submitted documents but is mandatory."
        return f"{criterion} does not meet the requirement (required {operator} {required}, found {found})."
    else:
        return f"{criterion} requires manual review (required {operator} {required}, found {found})."

def refine_explanation_with_llm(base_explanation: str) -> str:
    """
    Passes the base explanation to the Groq LLM to rewrite it in a 
    clear, professional, human-readable way for a government procurement officer.
    """
    prompt = f"""
Rewrite the following explanation in a clear, professional, human-readable way for a government procurement officer. 
Do not change facts. Do not add new information.

Return ONLY a valid JSON object with the exact schema:
{{
    "refined_reason": "string"
}}

Explanation:
{base_explanation}
"""
    try:
        response_text = call_llm(prompt)
        data = safe_json_loads(response_text)
        return data.get("refined_reason", base_explanation)
    except Exception as e:
        print(f"Failed to refine explanation with LLM: {e}")
        return base_explanation

def process_evaluations_with_explanations(evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of raw rule-engine evaluations and appends natural language
    explanations to them. To keep it simple, it loops over them. 
    (Could be batched later if needed).
    """
    final_outputs = []
    
    for ev in evaluations:
        base_exp = generate_base_explanation(ev)
        refined_exp = refine_explanation_with_llm(base_exp)
        
        final_outputs.append({
            "criterion": ev.get("criterion"),
            "required": ev.get("required"),
            "found": ev.get("found"),
            "result": ev.get("result"),
            "reason": refined_exp,
            "source": "Extracted from document"
        })
        
    return final_outputs
