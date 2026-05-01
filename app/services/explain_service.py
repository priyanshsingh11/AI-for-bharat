from typing import Dict, Any, List
from app.utils.formatters import format_value

def generate_base_explanation(eval_result: Dict[str, Any]) -> str:
    """
    Generates a professional, human-readable explanation using formatted values.
    """
    criterion = str(eval_result.get("criterion", "Unknown criterion")).capitalize()
    required = eval_result.get("required")
    found = eval_result.get("found")
    result = eval_result.get("result", "review")
    operator = eval_result.get("operator", "==")

    fmt_required = format_value(required, criterion)
    fmt_found = format_value(found, criterion)

    operator_text = {
        ">=": "at least",
        ">": "more than",
        "<=": "at most",
        "<": "less than",
        "==": "",
        "!=": "not equal to"
    }.get(operator, operator)

    if result == "pass":
        if isinstance(found, bool) or (isinstance(required, str)):
            return f"{criterion} is valid and meets the requirement."
        return f"{criterion} requirement satisfied (Required: {fmt_required}, Found: {fmt_found})."
    elif result == "fail":
        if found is None:
            return f"{criterion} is missing from the submitted documents but is mandatory."
        if isinstance(found, bool) or isinstance(required, str):
            return f"{criterion} does not meet the requirement."
        return f"{criterion} is below the required threshold (Required: {fmt_required}, Found: {fmt_found})."
    else:
        return f"{criterion} requires manual review (Required: {fmt_required}, Found: {fmt_found})."

def compute_confidence(eval_result: Dict[str, Any], evidence_page) -> float:
    """
    Heuristic confidence score based on result certainty and evidence availability.
    """
    result = eval_result.get("result", "review")
    if result == "pass":
        return 0.95 if evidence_page else 0.78
    elif result == "fail":
        found = eval_result.get("found")
        return 0.92 if found is None else 0.88
    return 0.55  # review

def generate_value_variants(value: Any) -> List[str]:
    """Generates variants of a numeric value for more robust string matching."""
    variants = []
    if value is None:
        return variants
    str_val = str(value).lower()
    variants.append(str_val)
    try:
        num_val = float(value)
        if num_val >= 10000000:
            crores = num_val / 10000000
            if crores.is_integer():
                crores = int(crores)
            variants.extend([
                f"{crores} crore", f"{crores} cr",
                f"₹{crores} crore", f"rs {crores} crore",
                f"rs. {crores} cr", f"inr {crores} crore"
            ])
            if isinstance(crores, int):
                variants.extend([f"{float(crores)} crore", f"{float(crores)} cr"])
        elif num_val >= 100000:
            lakhs = num_val / 100000
            if lakhs.is_integer():
                lakhs = int(lakhs)
            variants.extend([f"{lakhs} lakh", f"{lakhs} lakhs", f"{lakhs} l"])
    except ValueError:
        pass
    return list(set(variants))

def extract_evidence_with_page(pages: List[Dict[str, Any]], value: Any, keyword: str, window: int = 80) -> Dict[str, Any]:
    """Extracts a snippet of evidence surrounding a found value or keyword."""
    variants = generate_value_variants(value)
    print(f"Generated variants for {value}: {variants}")

    # 1. Try to match any value variant
    if variants:
        for page in pages:
            page_text = str(page.get("text", "")).lower()
            page_num = page.get("page")
            for variant in variants:
                idx = page_text.find(variant)
                if idx != -1:
                    print(f"Match found for value '{variant}' on page {page_num}")
                    start = max(0, idx - window)
                    end = min(len(page_text), idx + len(variant) + window)
                    snippet = page_text[start:end].replace("\n", " ").strip()
                    return {"snippet": f"...{snippet}...", "page": page_num}

    # 2. Fallback to keyword match
    if keyword:
        kw = keyword.lower()
        for page in pages:
            page_text = str(page.get("text", "")).lower()
            page_num = page.get("page")
            idx = page_text.find(kw)
            if idx != -1:
                print(f"Match found for keyword '{kw}' on page {page_num}")
                start = max(0, idx - window)
                end = min(len(page_text), idx + len(kw) + window)
                snippet = page_text[start:end].replace("\n", " ").strip()
                return {"snippet": f"...{snippet}...", "page": page_num}

    print(f"No match found for value variants or keyword '{keyword}'")
    return {"snippet": "No direct match found", "page": None}

def process_evaluations_with_explanations(evaluations: List[Dict[str, Any]], pages: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Attaches professional explanations, evidence and confidence to each evaluation.
    """
    final_outputs = []
    if pages is None:
        pages = []

    for ev in evaluations:
        reason = generate_base_explanation(ev)
        found_val = ev.get("found")
        criterion = ev.get("criterion", "")
        required = ev.get("required")

        evidence_data = extract_evidence_with_page(pages, found_val, criterion)
        page_num = evidence_data.get("page")
        confidence = compute_confidence(ev, page_num)

        source = f"Page {page_num} - Extracted from document" if page_num else "Evidence not found"

        # Format display values for UI
        fmt_required = format_value(required, criterion)
        fmt_found = format_value(found_val, criterion)

        final_outputs.append({
            "criterion": criterion,
            "required": required,
            "required_display": fmt_required,
            "found": found_val,
            "found_display": fmt_found,
            "result": ev.get("result"),
            "reason": reason,
            "evidence": evidence_data.get("snippet"),
            "page": page_num,
            "source": source,
            "confidence": round(confidence, 2)
        })

    return final_outputs
