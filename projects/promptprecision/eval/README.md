# PromptPrecision eval

This folder contains the **EvalReport v1** schema plus templates and example reports.

- JSON Schema: `eval-report.v1.schema.json`
- Canonical JSON template: `eval-report-template.eval-report.json`
- Example report: `examples/2026-02-23__invoice_mvp_extract_v1__run-001.eval-report.json`

## Quickstart: TaskSpec → EvalReport (5 steps)
1) Pick a TaskSpec JSON (or create one):
   - usually: `projects/promptprecision/specs/examples/*.taskspec.json`
2) Run the task/prompt once (one report **per run**) and save the raw artifacts:
   - exact prompt text used
   - inputs (text + attachments)
   - outputs (model response, parsed JSON, logs/errors)
3) Create a new report file from the template:
   - copy: `eval-report-template.eval-report.json`
   - to: `examples/YYYY-MM-DD__<task-or-prompt-id>__run-<N>.eval-report.json`
4) Fill the report:
   - set `task.taskSpecPath` to the TaskSpec you used
   - paste the **exact** prompt into `task.promptText`
   - add atomic `checks[]` derived from the TaskSpec rubric / acceptance criteria
   - set `overallResult.status` (PASS/FAIL) + evidence
5) Validate (optional but recommended):
   - validate the JSON against `eval-report.v1.schema.json` using your preferred JSON Schema tool.

## Naming convention
- Markdown template (optional): `eval-report-template.md`
- JSON report (recommended): `examples/YYYY-MM-DD__<task-or-prompt-id>__run-<N>.eval-report.json`

### File extension
Prefer the canonical extension: `*.eval-report.json`.

For backwards compatibility, existing reports may still use older variants (e.g. `*.evalreport.json`).
