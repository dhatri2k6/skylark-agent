from datetime import datetime
import re

DATE_FORMATS = [
    "%a %b %d %Y %H:%M:%S GMT%z (Coordinated Universal Time)",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
]

def clean_date(raw):
    if not raw or not str(raw).strip():
        return None
    raw = str(raw).strip()
    # Strip the "(Coordinated Universal Time)" suffix if present, keep offset
    raw_stripped = re.sub(r"\s*\(Coordinated Universal Time\)", "", raw)
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw_stripped, fmt.replace(" (Coordinated Universal Time)", "")).date().isoformat()
        except ValueError:
            continue
    return None  # couldn't parse — caller should flag this as a data quality issue

def clean_text(raw):
    if raw is None:
        return None
    text = str(raw).strip()
    return text if text else None

def clean_number(raw):
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return float(str(raw).replace(",", "").strip())
    except ValueError:
        return None

def normalize_row(row: dict) -> dict:
    """Cleans a single row dict, flagging missing/unparseable fields."""
    cleaned = {}
    issues = []
    for key, val in row.items():
        key_lower = key.lower()
        if "date" in key_lower:
            cleaned_val = clean_date(val)
            if val and not cleaned_val:
                issues.append(f"Could not parse date in '{key}': {val!r}")
        elif any(w in key_lower for w in ["amount", "value", "quantity"]):
            cleaned_val = clean_number(val)
        else:
            cleaned_val = clean_text(val)
        if cleaned_val is None and val not in (None, ""):
            pass  # kept for visibility, not silently dropped
        cleaned[key] = cleaned_val
    if issues:
        cleaned["_data_quality_notes"] = issues
    return cleaned

def normalize_rows(rows: list) -> list:
    return [normalize_row(r) for r in rows]