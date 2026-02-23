# PromptPrecision specs (MVP)

This folder holds early **schemas and examples**.

## TaskSpec (task definition)
- Schema (v1): `taskspec.v1.schema.json`
- Invoice extraction TaskSpec (example): `examples/invoice-mvp.taskspec.json`

The TaskSpec defines:
- what the model should do (system prompt + instruction template)
- what valid output looks like (`io_schema`)
- how we score it (`rubric`)
- how we split datasets (`eval_split`)

### Quick: produce an EvalReport from a TaskSpec (5 steps)
1) Choose the TaskSpec you’re running (example: `examples/invoice-mvp.taskspec.json`).
2) Execute one run of the task (using the prompt + IO contract from the TaskSpec).
3) Copy the EvalReport template:
   - from: `../eval/eval-report-template.eval-report.json`
   - to: `../eval/examples/YYYY-MM-DD__<task-or-prompt-id>__run-<N>.eval-report.json`
4) Fill `task.taskSpecPath` + paste the exact prompt into `task.promptText`.
5) Turn the TaskSpec rubric/criteria into atomic `checks[]`, record evidence, set PASS/FAIL.

## Invoice object schema (example output contract)
- Invoice object JSON Schema: `invoice-mvp.taskspec.schema.json`
- Notes: `invoice-mvp.taskspec.NOTES.md`

Despite the filename, **`invoice-mvp.taskspec.schema.json` is the schema for an invoice-shaped JSON object** (parties + line items + taxes). It can be used as an `io_schema` for tasks that output an invoice object.

## Examples
- TaskSpec example: `examples/invoice-mvp.taskspec.json`
- Invoice object examples:
  - `examples/invoice-mvp.taskspec.example.json`
  - `invoice-mvp.taskspec.example.json` (alternate example; may be consolidated later)

## EvalReport (evaluation run report)
- EvalReport JSON Schema (v1): `../eval/eval-report.v1.schema.json`
- Example EvalReport JSON: `../eval/examples/2026-02-23__invoice-mvp__run-003.eval-report.json`
