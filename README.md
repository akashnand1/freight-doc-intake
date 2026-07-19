# freight-doc-intake

Turns the messy front door of a logistics business, WhatsApp voice notes and photographed documents, into structured orders. Rebuilt from scratch on mock data, offline, zero keys.

I shipped voice-note and OCR document handling into production intake workflows. The interesting part was never the transcription or the OCR. It was what happens after: how much do you trust an extraction, and what do you do when you should not.

## The product thinking

Freight demand in emerging markets does not arrive as clean form submissions. It arrives as a 40-second voice note in mixed Arabic and English, a photo of a trade license, a forwarded PDF of last month's rate agreement. If your product only accepts clean input, your product only sees the demand your competitors did not want.

The pipeline has one governing rule: **extraction is cheap, wrong orders are expensive.** Every extracted field carries a confidence score. An order books itself only when every required field clears its threshold. Anything less lands in a review queue with the specific uncertain fields highlighted, so a human confirms two fields in ten seconds instead of retyping the whole order.

## What it does

- `intake.py` normalizes the three inbound shapes (voice transcript, OCR text, free text) into one message format.
- `extract.py` pulls origin, destination, truck type, quantity, commodity and pickup date, each with a confidence score. Deterministic rules stand in for the model; the LLM seam is one function (`extract_with_model`) you can swap in. The interface, and everything downstream, does not change.
- `triage.py` decides: AUTO_BOOK (all fields confident), REVIEW (booking-critical gaps, human confirms the flagged fields) or REJECT (not an order at all). Fails closed: no confident order, no booking.
- `eval_harness.py` scores triage against labeled messages and prints the confusion matrix. The number that matters is false AUTO_BOOK, and it has to be zero.

## Run it

```bash
python demo.py            # 6 sample messages end to end
python eval_harness.py    # extraction accuracy + triage confusion matrix
python -m unittest -v     # tests
```

## Sample output

```
MSG-02 (voice)  "yes hello need three flatbed jebel ali to riyadh uh sunday i"
    origin=Jebel Ali (0.85)   destination=Riyadh (0.85)   truck_type=flatbed (0.81)
    commodity=cement (0.77)   pickup_date=Sunday (0.54)
    -> REVIEW  (human confirms 2 fields: quantity, pickup_date)

EVAL  triage accuracy 1.00 · false AUTO_BOOK: 0 of 18
```

## Boundaries

Personal project. All messages are invented, the place names are public geography, and nothing here is company code. What I kept is the design conviction: confidence thresholds and a review queue are not overhead on the AI, they are the product.

MIT licensed.
