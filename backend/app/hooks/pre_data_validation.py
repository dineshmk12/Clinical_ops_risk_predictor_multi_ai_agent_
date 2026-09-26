"""Hook 01: pre_data_validation — validates incoming data before an agent
uses it (missing values, duplicate records, data freshness)."""
from datetime import date, timedelta

FRESHNESS_WINDOW_DAYS = 90


def validate(records: list[dict], date_field: str | None = None, required_fields: list[str] | None = None) -> dict:
    issues = []

    if not records:
        return {"valid": False, "issues": ["no records available"]}

    required_fields = required_fields or []
    for field in required_fields:
        missing = [r for r in records if r.get(field) is None]
        if missing:
            issues.append(f"{len(missing)} record(s) missing required field '{field}'")

    seen = set()
    duplicates = 0
    for r in records:
        key = tuple(sorted(r.items(), key=lambda kv: kv[0]))
        if key in seen:
            duplicates += 1
        seen.add(key)
    if duplicates:
        issues.append(f"{duplicates} duplicate record(s) detected")

    if date_field:
        dates = [r.get(date_field) for r in records if r.get(date_field)]
        if dates:
            latest = max(date.fromisoformat(d) if isinstance(d, str) else d for d in dates)
            if (date.today() - latest).days > FRESHNESS_WINDOW_DAYS:
                issues.append(f"data staleness: most recent record is {(date.today() - latest).days} days old")

    return {"valid": len(issues) == 0, "issues": issues}
