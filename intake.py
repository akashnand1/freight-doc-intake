"""Normalize inbound shapes into one message format.

Voice transcripts, OCR text and free text differ in noise profile, not
in meaning. Downstream code should never care which door a message
came through, only how much to trust it.
"""

CHANNEL_BASE_CONFIDENCE = {
    "text": 1.00,    # typed by a human who meant it
    "voice": 0.90,   # transcription noise, code-switching, filler words
    "ocr": 0.85,     # skew, stamps, coffee stains
}


def normalize(raw: dict) -> dict:
    channel = raw.get("channel", "text")
    if channel not in CHANNEL_BASE_CONFIDENCE:
        raise ValueError(f"unknown channel: {channel}")
    body = " ".join(raw.get("body", "").split())  # collapse whitespace/newlines
    return {
        "id": raw["id"],
        "channel": channel,
        "body": body,
        "base_confidence": CHANNEL_BASE_CONFIDENCE[channel],
    }
