# PromptPrecision — Invoice Extraction Eval Report (Template)

- **Report date:** YYYY-MM-DD
- **Owner:** @name
- **Model / version:** (e.g., gpt-4.1-mini, build sha)
- **Prompt / chain version:** (prompt id, commit)
- **Parser version:** (schema + post-processing)
- **Run id:** (optional)

## 1) Goal & Scope
Describe what “success” means for this evaluation.

- **Use-case:** Invoice → structured JSON fields
- **Languages / locales:** (e.g., EN/DE, currency formats)
- **Doc types included:** (PDF native, scanned images, multi-page)
- **Out of scope:** (credit notes, POs, receipts, etc.)

## 2) Dataset
### 2.1 Source & Split
- **Dataset name:**
- **Size:** N documents
- **Split:** train/dev/test or time-based; provide counts
- **Selection criteria:** (e.g., top vendors, edge cases)
- **PII handling:** (redaction, access controls)

### 2.2 Ground Truth
- **Labeling process:** (who, how)
- **Schema version:**
- **Inter-annotator agreement (if available):**
- **Known label issues / exclusions:**

## 3) Output Schema (what we extract)
List the required fields and any constraints.

**Header fields (examples)**
- vendor_name
- invoice_number
- invoice_date (ISO-8601)
- due_date (ISO-8601)
- currency (ISO 4217)
- subtotal, tax_total, total (numbers)

**Line items (examples)**
- description
- quantity
- unit_price
- line_total
- tax_rate / tax_amount

**Metadata**
- doc_language
- confidence / extraction_notes (if used)

## 4) Evaluation Protocol
### 4.1 Run Configuration
- **Temperature / decoding:**
- **Context strategy:** (full text, OCR text, chunking)
- **OCR engine + settings (if any):**
- **Tools:** (PDF text extraction, image preprocessing)
- **Retries / self-checks:**
- **Validation:** (JSON schema validation, numeric checks)

### 4.2 Matching & Normalization Rules
Define how predictions are compared to ground truth.

- **String normalization:** trim, casefold, unicode normalize, remove punctuation?
- **Date normalization:** parse and compare ISO dates; timezone assumptions
- **Number normalization:** remove thousands separators; decimal separators; currency symbols
- **Tolerance:** (e.g., absolute ≤ 0.01 or relative ≤ 0.1%)
- **Vendor aliases:** (mapping list / fuzzy matching rule)

## 5) Metrics (Definitions)
> Keep metrics definitions stable across reports.

### 5.1 Field-Level Metrics
For each field `f` evaluated across documents:

- **Field Exact Match (FEM):**
  - `FEM_f = correct_exact_f / eligible_f`
  - Correct when normalized predicted value == normalized ground-truth.

- **Field Within Tolerance (FWT) (numeric/date):**
  - `FWT_f = correct_within_tol_f / eligible_f`
  - Correct when `|pred - gt| <= tol` (or date difference within rule).

- **Missing Rate (MISS):**
  - `MISS_f = missing_pred_f / eligible_f`
  - “Missing” = null/empty/not present.

- **Over-Extraction / Hallucination Rate (HALL):**
  - `HALL_f = predicted_when_should_be_empty_f / ineligible_f`
  - Only for fields that are *sometimes absent* in ground truth.

### 5.2 Document-Level Metrics
- **Doc Valid JSON Rate (JSON_OK):**
  - `JSON_OK = valid_json_docs / total_docs`

- **Doc Schema Valid Rate (SCHEMA_OK):**
  - Passes JSON Schema + required fields present.

- **Doc All-Critical-Fields Correct (DOC_CRIT_OK):**
  - A document is correct if all *critical fields* meet match rules.
  - `DOC_CRIT_OK = docs_all_crit_correct / total_docs`

- **Doc Total Consistency (TOTAL_CONSIST):**
  - Checks relationships like `subtotal + tax_total == total` within tolerance.
  - `TOTAL_CONSIST = docs_passing_consistency / docs_with_applicable_fields`

### 5.3 Line-Item Metrics (if applicable)
- **Line-Item Alignment Rate (LI_ALIGN):**
  - % of documents where line items can be matched to ground truth (by index, key, or assignment).

- **Line-Item Field Accuracy (LI_FEM / LI_FWT):**
  - Same as field-level but aggregated over matched line items.

### 5.4 Efficiency Metrics
- **Latency (P50 / P95):** end-to-end per document.
- **Token usage:** prompt / completion averages.
- **Cost per document:** (USD or internal units).

## 6) Results (Fill In)
### 6.1 Summary
- **Total docs evaluated:** N
- **JSON_OK:** xx%
- **SCHEMA_OK:** xx%
- **DOC_CRIT_OK:** xx%
- **Latency P50 / P95:** xx s / xx s
- **Cost / doc:** $xx

### 6.2 Critical Fields Scorecard
Define the critical fields used for DOC_CRIT_OK.

Critical fields: (e.g., vendor_name, invoice_number, invoice_date, currency, total)

| Field | FEM | FWT (if used) | MISS | Notes |
|---|---:|---:|---:|---|
| vendor_name |  |  |  |  |
| invoice_number |  |  |  |  |
| invoice_date |  |  |  |  |
| currency |  |  |  |  |
| total |  |  |  |  |

### 6.3 Non-Critical Fields (Optional)
| Field | FEM | FWT | MISS | HALL | Notes |
|---|---:|---:|---:|---:|---|
| due_date |  |  |  |  |  |
| subtotal |  |  |  |  |  |
| tax_total |  |  |  |  |  |

### 6.4 Line Items (Optional)
| Metric | Value | Notes |
|---|---:|---|
| LI_ALIGN |  |  |
| LI_FEM (description) |  |  |
| LI_FWT (amounts) |  |  |

### 6.5 Breakdown Slices (Optional)
Provide slices that matter operationally.

- **By input type:** native PDF vs scanned
- **By language/locale:** EN vs DE; decimal comma
- **By vendor:** top 10 vendors
- **By page count:** 1 vs 2–3 vs 4+

| Slice | N | DOC_CRIT_OK | JSON_OK | Notes |
|---|---:|---:|---:|---|
| native_pdf |  |  |  |  |
| scanned |  |  |  |  |

## 7) Error Analysis
### 7.1 Top Failure Modes (ranked)
For each: description, frequency, examples, suspected cause.

1. **(e.g., invoice_number misread)** — N cases
2. **(e.g., currency inferred incorrectly)** — N cases
3. **(e.g., totals inconsistent)** — N cases

### 7.2 Representative Examples
Include 3–10 examples with:
- doc id
- ground truth vs prediction
- what went wrong
- fix idea

### 7.3 Boundary / Policy Issues
List any ambiguous cases needing product decision:
- multiple invoice numbers
- pro-forma vs invoice
- credit note formats

## 8) Changes Since Last Run
- Prompt changes:
- Parsing/normalization changes:
- Dataset changes:

## 9) Recommendations & Next Steps
- **Immediate fixes (1–2 days):**
- **Medium-term (1–2 weeks):**
- **Long-term:**

## Appendix A — Reproducibility
- Command / script used:
- Git commit(s):
- Environment:
- Random seeds:

## Appendix B — Metric Details (Optional)
- Exact normalization functions
- Tolerance values
- Field eligibility rules
