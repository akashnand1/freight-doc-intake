"""Triage: AUTO_BOOK, REVIEW or REJECT.

Fails closed. AUTO_BOOK requires every booking-critical field above its
threshold. REVIEW lists exactly which fields a human must confirm, so
review is a ten-second confirmation, not a re-keying job.
"""

THRESHOLDS = {
    "origin": 0.8,
    "destination": 0.8,
    "truck_type": 0.75,
    "quantity": 0.75,
    "pickup_date": 0.8,
    # commodity is nice to have; it never blocks a booking
}
MIN_SIGNAL = 2  # fewer than this many extracted fields = not an order


def triage(extraction: dict) -> dict:
    found = {f: v for f, (v, c) in extraction.items() if v is not None}
    if len(found) < MIN_SIGNAL:
        return {"decision": "REJECT",
                "why": f"only {len(found)} extractable field(s); not an order"}

    weak = [f for f, threshold in THRESHOLDS.items()
            if extraction[f][1] < threshold]
    if not weak:
        return {"decision": "AUTO_BOOK", "why": "all booking-critical fields confident"}
    return {"decision": "REVIEW", "confirm": weak,
            "why": f"human confirms {len(weak)} field(s): {', '.join(weak)}"}
