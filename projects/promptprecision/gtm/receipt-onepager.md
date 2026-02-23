# PromptPrecision — Receipt Extraction (One-pager)

## One-liner
Extract messy receipts into **validated JSON** (totals + line items) with confidence + audit trail — not just OCR text.

## Who it’s for (ICP)
- Expense management platforms
- Bookkeeping automation tools
- Corporate card/spend platforms (receipt↔transaction matching)
- BPO / outsourced bookkeeping (high volume)

## The wedge
- Strict schema + reconciliation checks
- Confidence + “needs review” detection
- Evidence spans (where the value came from)

## MVP scope
- Async API: `POST /receipts` → `GET /receipts/{id}` + webhook
- JSON output: merchant/date/currency/totals + optional line items
- Validation flags + error taxonomy (blur/cutoff/glare)
- Basic dedupe

## Success metrics
- Field accuracy (date/currency/merchant/total/tax/tip)
- Reconciliation success rate
- “Needs review” calibration
- Latency + cost per receipt

## Pricing hypothesis
Usage-based tiers (typically lower ACV than invoices but high volume):
- Starter $49–$199/mo + $0.02–$0.06/receipt overage
- Growth $499–$1,999/mo + $0.01–$0.03/receipt

## Pilot idea
Run 1,000 receipts in shadow mode; pay only if total+date+merchant hit a target accuracy threshold.
