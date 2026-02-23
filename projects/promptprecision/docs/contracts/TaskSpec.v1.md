# TaskSpec v1 (PromptPrecision) — Contract

**Location (canonical):** `projects/promptprecision/specs/taskspec.v1.schema.json`

A **TaskSpec** is the single source of truth for a prompt-based task:
- *What to do* (system prompt + instruction template)
- *What to return* (an output JSON Schema contract: `io_schema`)
- *How to evaluate* (rubric + scoring guidance)
- *How to split datasets* (eval split config)

This doc is intentionally aligned with the **Invoice MVP** workflow (extract invoice fields from text/OCR and score correctness).

---

## 1) File layout recommendation

For PromptPrecision projects, keep things in three places:

- **Contracts (schemas):**
  - TaskSpec schema: `projects/promptprecision/specs/taskspec.v1.schema.json`
  - Output schema(s) (domain objects): `projects/promptprecision/specs/*.schema.json`
  - Eval report schema: `projects/promptprecision/eval/eval-report.v1.schema.json`

- **Examples (instances):**
  - TaskSpec examples: `projects/promptprecision/specs/examples/*.taskspec*.json`
  - Output examples: `projects/promptprecision/specs/examples/*.output*.json`
  - Eval report examples: `projects/promptprecision/eval/examples/*.eval-report.json`

- **Docs (human-readable):**
  - This folder: `projects/promptprecision/docs/…`

---

## 2) Quickstart: write a TaskSpec (and where it lives)

1) Create a new file under:
- `projects/promptprecision/specs/examples/`

2) Name it like:
- `<domain>-<task>.taskspec.json`

3) Start from a working example and edit `task_id`, `base_model_id`, prompts, schema, and rubric.

Minimal skeleton (v1 fields):

```json
{
  "task_id": "invoice_mvp_extract_v1",
  "task_version": "1.0.0",
  "base_model_id": "Qwen/Qwen2.5-3B-Instruct",
  "system_prompt": "...",
  "instruction_template": "... {{input_text}} ...",
  "io_schema": { "type": "object", "additionalProperties": false, "properties": {} },
  "rubric": { "checks": [] },
  "eval_split": { "strategy": "random", "seed": 42 }
}
```

## 3) TaskSpec v1: required fields

### `task_id` (string)
Stable identifier for the task.
- Recommended: `snake_case`.
- Example: `invoice_mvp_extract_v1`

### `task_version` (semver string)
Version of the *task contract*.
- Example: `1.0.0`

### `base_model_id` (string)
Which model the TaskSpec was authored against.
- Example: `Qwen/Qwen2.5-3B-Instruct`

### `system_prompt` (string)
Global rules and behavior constraints.
Invoice MVP pattern:
- “Output ONLY valid JSON”
- “No markdown”
- “Do not add keys not in schema”

### `instruction_template` (string)
Template used per input item.
- Must include a placeholder (implementation-defined) like `{{input_text}}`.
- Keep it explicit about missing/unknown behavior (Invoice MVP uses `null` instead of guessing).

### `io_schema` (object)
**JSON Schema** that the model output must validate against.
- Can be Draft-07 or 2020-12 (task-defined).
- Strongly recommended: `additionalProperties: false` to avoid silent junk keys.

### `rubric` (object)
How you will judge correctness.
MVP rubric should at least specify:
- schema validity required?
- additional keys forbidden?
- null-when-missing policy?
- arithmetic / consistency checks (totals, line-items sum)
- scoring weights (optional)

### `eval_split` (object)
How datasets are split for eval.
- MVP currently supports `strategy: "random"` + optional `seed`.

**Ratio rules (when provided):**
- If you set any of `train_ratio`, `val_ratio`, or `test_ratio`, you **must set all three**.
- The three ratios **must sum to 1.0**.

Example:
```json
{
  "eval_split": {
    "strategy": "random",
    "train_ratio": 0.8,
    "val_ratio": 0.1,
    "test_ratio": 0.1,
    "seed": 42
  }
}
```

---

## 3) Optional fields

### `label_enums` (object)
Optional enums for constrained fields.
- Useful for generation and scoring.
- Example: `{ "currency": ["USD","EUR","GBP","ILS"] }`

### `example` (object)
One *inline* example to sanity-check prompt + schema quickly.
- `example.input_text`
- `example.output_json`

---

## 4) Invoice MVP: recommended invariants

When designing invoice extraction tasks, prefer these invariants:

1. **Output is JSON only** (no prose).
2. **Strict schema** (`additionalProperties: false`).
3. **Unknown → null** (never invent IDs/dates/tax IDs).
4. **Arithmetic sanity checks** with tolerances:
   - `total ≈ subtotal + tax_total + shipping - discount`
   - `subtotal ≈ sum(line_items[*].line_total)`

---

## 5) Pointers to canonical examples

- Full TaskSpec (Invoice MVP extraction):
  - `projects/promptprecision/specs/examples/invoice-mvp.taskspec.json`
- Realistic TaskSpec example (same shape; safe to copy/edit):
  - `projects/promptprecision/specs/examples/invoice-mvp.taskspec.realistic.json`
- Minimal TaskSpec (same task, smallest useful surface; may omit some v1-required fields):
  - `projects/promptprecision/specs/examples/invoice-mvp.taskspec.min.json`

---

## 6) How to test (validate contracts locally)

### A) Validate a TaskSpec against the TaskSpec schema (AJV)
```bash
npx -y ajv-cli@5 validate --spec=draft2020 \
  -s projects/promptprecision/specs/taskspec.v1.schema.json \
  -d projects/promptprecision/specs/examples/invoice-mvp.taskspec.json
```

### B) Validate a sample output against the TaskSpec’s `io_schema`
Because the output schema is stored *inline* inside the TaskSpec, the simplest repeatable approach is a small Node script:

```bash
node - <<'NODE'
const fs = require('fs');
const Ajv = require('ajv');

const taskSpec = JSON.parse(fs.readFileSync('projects/promptprecision/specs/examples/invoice-mvp.taskspec.json','utf8'));
const exampleOut = taskSpec.example.output_json;

const ajv = new Ajv({ allErrors: true, strict: false });
const validate = ajv.compile(taskSpec.io_schema);

const ok = validate(exampleOut);
if (!ok) {
  console.error(validate.errors);
  process.exit(1);
}
console.log('OK: example.output_json validates against TaskSpec.io_schema');
NODE
```

### C) Validate an EvalReport JSON against the EvalReport schema
```bash
npx -y ajv-cli@5 validate --spec=draft2020 \
  -s projects/promptprecision/eval/eval-report.v1.schema.json \
  -d projects/promptprecision/eval/examples/2026-02-23__invoice-mvp__run-003.eval-report.json
```
