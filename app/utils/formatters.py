from typing import Any

def format_inr(value: Any) -> str:
    """Format a number as a human-readable Indian currency string."""
    if value is None:
        return "N/A"
    try:
        num = float(value)
        if num >= 10000000:  # >= 1 Crore
            crores = num / 10000000
            label = int(crores) if crores.is_integer() else round(crores, 2)
            return f"₹{label} Cr"
        elif num >= 100000:  # >= 1 Lakh
            lakhs = num / 100000
            label = int(lakhs) if lakhs.is_integer() else round(lakhs, 2)
            return f"₹{label} L"
        else:
            return f"₹{int(num):,}"
    except (ValueError, TypeError):
        return str(value)

def format_value(value: Any, criterion: str = "") -> str:
    """Smart formatter: uses INR format for turnover-like fields, else str."""
    criterion_lower = (criterion or "").lower()
    numeric_criteria = ["turnover", "revenue", "value", "amount", "income"]
    if any(k in criterion_lower for k in numeric_criteria):
        return format_inr(value)
    if isinstance(value, bool):
        return "Valid" if value else "Invalid"
    if value is None:
        return "N/A"
    return str(value)
