from typing import List, Dict, Any, Optional

def find_bidder_value(criterion: str, bidder_data: Dict[str, Any]) -> Optional[Any]:
    """
    Looks up the bidder value for a criterion.
    Strategy:
    1. Exact key match (e.g. "turnover" == "turnover")
    2. Bidder key is a substring of criterion (e.g. "turnover" in "annual turnover")
    3. Criterion is a substring of bidder key
    """
    criterion_lower = criterion.lower()

    # 1. Exact match
    if criterion_lower in bidder_data:
        return bidder_data[criterion_lower]

    # 2. Check if any bidder key is contained within the criterion
    for key in bidder_data:
        if key.lower() in criterion_lower:
            print(f"Rule Engine: matched criterion '{criterion_lower}' to bidder key '{key}'")
            return bidder_data[key]

    # 3. Check if the criterion is contained within any bidder key
    for key in bidder_data:
        if criterion_lower in key.lower():
            print(f"Rule Engine: matched criterion '{criterion_lower}' to bidder key '{key}'")
            return bidder_data[key]

    return None

def compare_values(found_val: Any, operator: str, required_val: Any) -> str:
    """
    Applies comparison logic including string-based boolean handling.
    Returns 'pass', 'fail', or 'review'.
    """
    try:
        # Handle boolean-like string comparisons for gst/registration
        if isinstance(required_val, str) and isinstance(found_val, bool):
            # e.g. required "valid" and found True → pass
            if required_val.lower() in ("valid", "true", "yes") and found_val is True:
                return "pass"
            if required_val.lower() in ("invalid", "false", "no") and found_val is False:
                return "pass"
            return "fail"

        if operator == ">=":
            return "pass" if found_val >= required_val else "fail"
        elif operator == ">":
            return "pass" if found_val > required_val else "fail"
        elif operator == "<=":
            return "pass" if found_val <= required_val else "fail"
        elif operator == "<":
            return "pass" if found_val < required_val else "fail"
        elif operator == "==":
            return "pass" if found_val == required_val else "fail"
        elif operator == "!=":
            return "pass" if found_val != required_val else "fail"
    except TypeError:
        pass
    return "review"

def evaluate_bidder(tender_criteria: List[Dict[str, Any]], bidder_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates bidder data against tender criteria using smart key matching.
    Returns a list of evaluation results.
    """
    evaluations = []

    for req in tender_criteria:
        criterion = req.get("criterion", "").lower()
        operator = req.get("operator", "==")
        required_val = req.get("value")
        mandatory = req.get("mandatory", True)

        # Smart lookup: handles "Annual Turnover" → "turnover" key mismatch
        found_val = find_bidder_value(criterion, bidder_data)
        result_status = "review"

        if found_val is None:
            result_status = "fail" if mandatory else "review"
            print(f"Rule Engine: '{criterion}' → NOT FOUND in bidder data, result=fail")
        else:
            result_status = compare_values(found_val, operator, required_val)
            print(f"Rule Engine: '{criterion}' → found={found_val}, required {operator} {required_val}, result={result_status}")

        evaluations.append({
            "criterion": criterion,
            "operator": operator,
            "required": required_val,
            "found": found_val,
            "mandatory": mandatory,
            "result": result_status
        })

    return evaluations
