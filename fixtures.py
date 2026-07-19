"""Invented messages. Mixed quality on purpose; that is the point of intake."""

MESSAGES = [
    {"id": "MSG-01", "channel": "text",
     "body": "Need 2 flatbed trucks from Jebel Ali to Riyadh on 22/07, cement, please quote"},
    {"id": "MSG-02", "channel": "voice",
     "body": "yes hello need three flatbed jebel ali to riyadh uh sunday inshallah cement bags"},
    {"id": "MSG-03", "channel": "ocr",
     "body": "TRANSPORT REQUEST  Origin: Dammam  Destination: Dubai  Qty: 5 reefer trailer  Date: 25/07/2026  Commodity: food"},
    {"id": "MSG-04", "channel": "voice",
     "body": "salam do you have a truck available tomorrow from sharjah"},
    {"id": "MSG-05", "channel": "text",
     "body": "thanks for the invoice will pay next week"},
    {"id": "MSG-06", "channel": "ocr",
     "body": "DELIVERY NOTE  received 12 pallets in good condition signature illegible"},
]

# labeled triage expectations for the eval harness
LABELS = {
    "MSG-01": "AUTO_BOOK",
    "MSG-02": "REVIEW",      # weekday, not a date
    "MSG-03": "REVIEW",     # OCR base confidence demands one human confirmation
    "MSG-04": "REVIEW",      # one place, no quantity confidence, vague time
    "MSG-05": "REJECT",
    "MSG-06": "REJECT",
}
