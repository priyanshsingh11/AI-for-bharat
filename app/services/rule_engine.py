from typing import List, Dict, Any

def evaluate_bidder(tender_criteria: List[Dict[str, Any]], bidder_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates bidder data against tender criteria.
    Returns a list of evaluation results.
    """
    evaluations = []
    
    for req in tender_criteria:
        criterion = req.get("criterion", "").lower()
        operator = req.get("operator", "==")
        required_val = req.get("value")
        mandatory = req.get("mandatory", True)
        
        found_val = bidder_data.get(criterion)
        result_status = "review"
        
        if found_val is None:
            result_status = "fail" if mandatory else "review"
        else:
            try:
                if operator == ">=":
                    result_status = "pass" if found_val >= required_val else "fail"
                elif operator == ">":
                    result_status = "pass" if found_val > required_val else "fail"
                elif operator == "<=":
                    result_status = "pass" if found_val <= required_val else "fail"
                elif operator == "<":
                    result_status = "pass" if found_val < required_val else "fail"
                elif operator == "==":
                    result_status = "pass" if found_val == required_val else "fail"
                elif operator == "!=":
                    result_status = "pass" if found_val != required_val else "fail"
            except TypeError:
                # If types are incomparable
                result_status = "review"
                
        evaluations.append({
            "criterion": criterion,
            "operator": operator,
            "required": required_val,
            "found": found_val,
            "mandatory": mandatory,
            "result": result_status
        })
        
    return evaluations
