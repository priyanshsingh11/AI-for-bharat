import json

def call_llm(prompt: str) -> str:
    """
    Mock LLM service that returns a predefined JSON string
    based on keywords found in the prompt.
    """
    prompt_lower = prompt.lower()
    
    # Check if the prompt is asking for tender criteria
    if "criterion" in prompt_lower or "operator" in prompt_lower:
        tender_mock_response = [
            {
                "criterion": "turnover",
                "operator": ">=",
                "value": 50000000,
                "mandatory": True
            }
        ]
        return json.dumps(tender_mock_response)
        
    # Check if the prompt is asking for bidder data
    elif "turnover" in prompt_lower or "gst" in prompt_lower or "projects" in prompt_lower:
        bidder_mock_response = {
            "turnover": 30000000,
            "gst": True,
            "projects": 2
        }
        return json.dumps(bidder_mock_response)
        
    # Default fallback
    return "{}"
