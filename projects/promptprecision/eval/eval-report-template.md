# Invoice MVP — Eval Report Template

Optional machine-readable format (recommended):
- JSON Schema: `projects/promptprecision/eval/eval-report.v1.schema.json`
- Canonical JSON template: `projects/promptprecision/eval/eval-report-template.eval-report.json`
- Example: `projects/promptprecision/eval/examples/2026-02-23__invoice-mvp__run-003.eval-report.json`

> Prefer the canonical extension: `*.eval-report.json`.
> For backwards compatibility, older variants like `*.evalreport.json` may exist.


> Use one report **per run** (prompt/task execution).
>
> **Option A (Markdown):** copy this file, fill in, and save as:
> `YYYY-MM-DD__<task-or-prompt-id>__run-<N>.md`
>
> **Option B (JSON, recommended):** create an EvalReport v1 JSON payload that validates against:
> `projects/promptprecision/eval/eval-report.v1.schema.json`
>
> Save it as:
> `projects/promptprecision/eval/examples/YYYY-MM-DD__<task-or-prompt-id>__run-<N>.eval-report.json`
>
> See example:
> `projects/promptprecision/eval/examples/2026-02-23__invoice-mvp__run-003.eval-report.json`

## Metadata
- **Date/time started (local):** 
- **Date/time ended (local):** 
- **Elapsed:** 
- **Evaluator:** 
- **Run ID:** 
- **Environment:** (model/version, app build, dataset version, OS/browser, etc.)

## Task / Prompt
- **Task name:** 
- **Goal (1 sentence):** 
- **Prompt / Instructions used:**

```text
<PASTE EXACT PROMPT HERE>
```

## Inputs
Record everything the system received.

- **User input(s):**
  - 
- **Files / attachments provided:**
  - 
- **Assumptions / config:** (currency, locale, rounding, tax rules, invoice numbering, etc.)
  - 

## Outputs
Record everything the system produced.

- **Primary output(s):** (generated invoice JSON/PDF/text, extracted fields, etc.)
  - 
- **Side effects:** (files written, records created/updated, emails drafted/sent, etc.)
  - 
- **Logs / errors / warnings:**
  - 

## Checks (Acceptance Criteria)
List the checks you performed and the outcome.

> Tip: keep checks *atomic* (one expectation each).

| # | Check | Method (manual/auto) | Result (pass/fail) | Evidence / notes |
|---:|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

## Overall Result
- **Pass/Fail:** 
- **If fail:** severity (blocker/major/minor) + brief reason

## Timing Breakdown (optional)
- **Setup:** 
- **Run:** 
- **Verification:** 

## Notes / Observations
- What was confusing, brittle, or surprising?
- What would you change in the prompt/task spec?
- Any follow-ups / bugs to file?

---

# Example (filled)

## Metadata
- **Date/time started (local):** 2026-02-23 16:05
- **Date/time ended (local):** 2026-02-23 16:12
- **Elapsed:** 7m
- **Evaluator:** Dev C
- **Run ID:** INV-EVAL-003
- **Environment:** model=gpt-5.2, app=Invoice MVP v0.3.1, locale=en-IL

## Task / Prompt
- **Task name:** Generate invoice from line items
- **Goal (1 sentence):** Produce a correct invoice summary with totals including VAT.
- **Prompt / Instructions used:**

```text
Create an invoice for ACME Ltd. Items: (1) "Design" 3 hours @ 200 ILS/hour, (2) "Hosting" 1 month @ 50 ILS. VAT 17%. Output JSON with subtotal, vat, total.
```

## Inputs
- **User input(s):**
  - Customer: ACME Ltd.
  - Line items: Design (3×200 ILS), Hosting (1×50 ILS)
  - VAT: 17%
- **Files / attachments provided:** none
- **Assumptions / config:** currency=ILS, rounding=2 decimals

## Outputs
- **Primary output(s):**
  - JSON produced with subtotal=650.00, vat=110.50, total=760.50
- **Side effects:** none
- **Logs / errors / warnings:** none

## Checks (Acceptance Criteria)
| # | Check | Method (manual/auto) | Result (pass/fail) | Evidence / notes |
|---:|---|---|---|---|
| 1 | Subtotal equals sum(line totals) | manual | pass | 3×200 + 1×50 = 650 |
| 2 | VAT equals 17% of subtotal | manual | pass | 0.17×650 = 110.5 |
| 3 | Total equals subtotal + VAT | manual | pass | 650 + 110.5 = 760.5 |
| 4 | Currency preserved as ILS | manual | pass | JSON fields in ILS |

## Overall Result
- **Pass/Fail:** PASS

## Notes / Observations
- Output format was correct and numeric rounding consistent.
- Next: add check for invoice number/date formatting once implemented.
