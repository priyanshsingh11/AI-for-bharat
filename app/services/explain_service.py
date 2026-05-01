from typing import Dict, Any, List

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
            variants.append(f"{crores} crore")
            variants.append(f"{crores} cr")
            variants.append(f"₹{crores} crore")
            variants.append(f"rs {crores} crore")
            variants.append(f"rs. {crores} cr")
            if isinstance(crores, int):
                variants.append(f"{float(crores)} crore")
                variants.append(f"{float(crores)} cr")
        elif num_val >= 100000:
            lakhs = num_val / 100000
            if lakhs.is_integer():
                lakhs = int(lakhs)
            variants.append(f"{lakhs} lakh")
            variants.append(f"{lakhs} lakhs")
            variants.append(f"{lakhs} l")
    except ValueError:
        pass
        
    # Remove duplicates
    return list(set(variants))

def extract_evidence_with_page(pages: List[Dict[str, Any]], value: Any, keyword: str, window: int = 60) -> Dict[str, Any]:
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
                    return {
                        "snippet": f"...{snippet}...",
                        "page": page_num
                    }
                    
    # 2. If not found, try to match the keyword
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
                return {
                    "snippet": f"...{snippet}...",
                    "page": page_num
                }
                
    # 3. No match found
    print(f"No match found for value variants or keyword '{keyword}'")
    return {
        "snippet": "No direct match found, keyword-based approximation used",
        "page": None
    }

def process_evaluations_with_explanations(evaluations: List[Dict[str, Any]], pages: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Takes a list of raw rule-engine evaluations and appends natural language
    explanations and physical page evidence to them.
    """
    final_outputs = []
    if pages is None:
        pages = []
        
    for ev in evaluations:
        base_exp = generate_base_explanation(ev)
        
        found_val = ev.get("found")
        criterion = ev.get("criterion", "")
        
        evidence_data = extract_evidence_with_page(pages, found_val, criterion)
        page_num = evidence_data.get("page")
        
        source = f"Page {page_num} - Extracted from document" if page_num else "Evidence not found"
        
        final_outputs.append({
            "criterion": criterion,
            "required": ev.get("required"),
            "found": found_val,
            "result": ev.get("result"),
            "reason": base_exp,
            "evidence": evidence_data.get("snippet"),
            "page": page_num,
            "source": source
        })
        
    return final_outputs
