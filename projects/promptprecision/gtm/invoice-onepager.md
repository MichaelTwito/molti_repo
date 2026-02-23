# PromptPrecision — Invoice Extraction (One-pager)

## One-liner
Turn messy invoices (PDF/image/email) into **validated JSON** with confidence scores + an eval report you can trust.

## Who it’s for (ICP)
- SMB → mid-market processing **500–20,000 invoices/month**
- Lean AP teams, AP outsourcing providers, bookkeeping firms, property management, logistics, construction suppliers

## The wedge
Not “AI does invoices” — **measured, schema-valid extraction**:
1) validated JSON contract
2) accuracy scorecard on *your* invoices
3) human review only when needed
4) auditable prompt/versioning & error taxonomy

## What it outputs
- JSON (strict schema) + confidence per field
- Validation errors + reconciliation checks (totals vs subtotal+tax)
- Optional: CSV export / push to QuickBooks or Xero

## MVP scope
- Input: PDF (digital + scanned), images; optional email attachments
- Output: typed JSON + validation + confidence
- Human-in-the-loop: review queue for low-confidence fields
- Connectors: webhook + Drive/Dropbox watch or Zapier/Make

## Success metrics (what we report)
- Schema validity rate
- Doc pass rate (required fields + accounting equation)
- Review rate (% docs requiring human touch)
- Vendor-holdout generalization (new vendor layouts)
- Latency p50/p95 + cost per invoice

## Pilot (2 weeks)
Week 1: Evaluate on 200–500 historical invoices → scorecard.
Week 2: Shadow mode + export pipeline → measure review rate.

## Pricing hypothesis
- Paid pilot: **$500–$2,000** (credited toward first month)
- Subscription: usage tiers (e.g., $199/mo incl 1k, $0.06/invoice overage)

## Next 10 targets
Bookkeeping firms; AP outsourcing/BPO; property management; logistics; construction; wholesale; clinics; ecommerce brands; MSP/IT resellers.
