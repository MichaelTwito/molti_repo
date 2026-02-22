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

## Wedge (MVP)
**Structured extraction / classification** for SMB/indie teams (support inbox, sales triage, ops):
- Input: email/ticket/text
- Output: JSON with category, urgency, entities, next_action
- Success metric: accuracy + low hallucination + latency

## Guardrails
- No magical claims without evals.
- Privacy-by-default: run locally; datasets never leave unless user opts in.

