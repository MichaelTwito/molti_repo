# PromptPrecision (working name)

**One-liner:** Turn a task prompt into a *measurably better* small open-weight model package (adapter now; pruning/distill later) + an eval report.

## Why this exists
Teams want:
- lower latency and cost
- on-prem / privacy
- fewer hallucinations for a narrow recurring task

## MVP deliverable
Given:
- a base model (e.g., 3B–8B)
- a task definition (prompt + IO schema)
- a small dataset (or synthetic + human-reviewed)

Return:
- an **adapter** (LoRA) + routing config (optional)
- an **eval report** (before/after)
- a reproducible deployment recipe (Ollama/vLLM/TFM)

## Project status
- **Current iteration status:** `projects/promptprecision/status.md`
- **Append-only iteration log:** `projects/promptprecision/iteration_log.md`

## Wedge (MVP)
**Structured extraction / classification** for SMB/indie teams (support inbox, sales triage, ops):
- Input: email/ticket/text
- Output: JSON with category, urgency, entities, next_action
- Success metric: accuracy + low hallucination + latency

## Guardrails
- No magical claims without evals.
- Privacy-by-default: run locally; datasets never leave unless user opts in.

## Invoice extraction pipeline (CLI usage — stub)
This is the **intended** end-to-end interface for the invoice MVP. It documents **inputs/outputs** and how to get **reproducible runs**. (Implementation may be partial/nonexistent in this repo right now.)

### Inputs
- **Task spec / schema:** `specs/invoice-mvp.taskspec.schema.json`
- **Documents to extract from:** PDFs/images/text (one file per example)
- **Optional ground truth:** a JSON/JSONL file aligned to the documents for evaluation

Suggested dataset layout:

```text
data/invoices/
  docs/
    inv_0001.pdf
    inv_0002.png
  truth.jsonl          # optional (one JSON object per doc)
  manifest.jsonl       # optional (doc_id → path, metadata)
```

### Outputs
All outputs go under a single run directory so you can diff, archive, and reproduce:

```text
runs/invoice-mvp/<run_id>/
  config.json          # frozen config used for the run (seed, model ids, etc.)
  preds.jsonl          # extracted invoice JSON per document
  metrics.json         # aggregate eval metrics (if truth provided)
  errors.jsonl         # parse/model failures
  artifacts/
    adapter/           # LoRA adapter (if training/fine-tuning is enabled)
    report.md          # human-readable summary
```

### Reproducible run (example)
Pin your environment (recommended approaches):
- run inside a container with a fixed image digest, or
- use a lockfile (e.g., `uv.lock` / `poetry.lock`) and record `pip freeze` into the run dir.

Then run (placeholder CLI name):

```bash
# Example: deterministic-ish extraction + optional evaluation
export PP_SEED=1337
export PP_DETERMINISTIC=1

pp-invoice run \
  --task-spec projects/promptprecision/specs/invoice-mvp.taskspec.schema.json \
  --input-dir data/invoices/docs \
  --truth data/invoices/truth.jsonl \
  --out runs/invoice-mvp/$(date -u +%Y%m%dT%H%M%SZ) \
  --model "open-weight-3b" \
  --temperature 0 \
  --max-docs 200
```

### Notes (what makes it reproducible)
- **Seed + temperature=0** recorded into `config.json`.
- Save the **exact model identifier** (and adapter hash, if any).
- Record **tool versions** (OCR, PDF renderer, tokenizer, etc.) into `config.json`.
- Keep the raw inputs immutable; treat `runs/...` as append-only artifacts.

