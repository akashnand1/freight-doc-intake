"""Field extraction with per-field confidence.

Deterministic rules stand in for the model so the repo runs offline.
The LLM seam is `extract_with_model`: swap it for a model call and
nothing downstream changes, because downstream trusts the confidence
numbers, not the extractor.
"""
import re

KNOWN_PLACES = [
    "jebel ali", "riyadh", "dammam", "jeddah", "dubai", "abu dhabi",
    "sharjah", "muscat", "doha", "kuwait city", "manama", "neom",
]
TRUCK_TYPES = {
    "flatbed": ["flatbed", "flat bed"],
    "curtainside": ["curtainside", "curtain side", "tautliner"],
    "reefer": ["reefer", "refrigerated", "chiller"],
    "box": ["box truck", "closed truck", "dyna"],
    "lowbed": ["lowbed", "low bed"],
}
COMMODITIES = ["cement", "steel", "food", "furniture", "electronics",
               "chemicals", "aggregate", "packaging"]
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday"]
VAGUE_TIME = ["asap", "urgent", "today", "tomorrow"] + WEEKDAYS

FIELDS = ("origin", "destination", "truck_type", "quantity", "commodity", "pickup_date")


def _find_places(body: str) -> list:
    hits = []
    for place in KNOWN_PLACES:
        idx = body.find(place)
        if idx >= 0:
            hits.append((idx, place.title()))
    return [p for _, p in sorted(hits)]


def extract_with_model(message: dict) -> dict:
    """The seam. Offline: rules. Online: replace the body of this function
    with a model call returning the same {field: (value, confidence)} shape."""
    body = message["body"].lower()
    base = message["base_confidence"]
    out = {}

    places = _find_places(body)
    if len(places) >= 2:
        out["origin"] = (places[0], round(0.95 * base, 2))
        out["destination"] = (places[1], round(0.95 * base, 2))
    elif len(places) == 1:
        out["destination"] = (places[0], round(0.55 * base, 2))  # which end is it?

    for truck, aliases in TRUCK_TYPES.items():
        if any(a in body for a in aliases):
            out["truck_type"] = (truck, round(0.9 * base, 2))
            break

    qty = re.search(r"\b(\d{1,3})\s*(?:x\s*)?(?:truck|trailer|flatbed|reefer|load|unit)", body)
    if qty:
        out["quantity"] = (int(qty.group(1)), round(0.9 * base, 2))
    elif re.search(r"\b(a|one)\s+(truck|load)\b", body):
        out["quantity"] = (1, round(0.7 * base, 2))

    for c in COMMODITIES:
        if c in body:
            out["commodity"] = (c, round(0.85 * base, 2))
            break

    date = re.search(r"\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b", body)
    if date:
        out["pickup_date"] = (date.group(1), round(0.9 * base, 2))
    else:
        for word in VAGUE_TIME:
            if word in body:
                # a weekday or "asap" is a hint, not a date. Low confidence on purpose.
                out["pickup_date"] = (word.title(), round(0.6 * base, 2))
                break
    return out


def extract(message: dict) -> dict:
    """Full extraction record: every field present, None where nothing found."""
    found = extract_with_model(message)
    return {f: found.get(f, (None, 0.0)) for f in FIELDS}
