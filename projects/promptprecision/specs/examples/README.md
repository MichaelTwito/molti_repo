# Invoice MVP example (schema-aligned)

Files:
- Example JSON: `invoice-mvp.taskspec.example.json`
- JSON Schema: `../invoice-mvp.taskspec.schema.json`

## What this is
A realistic invoice object that matches the **Invoice MVP TaskSpec schema** fields:
- `invoiceNumber`, `issueDate`, `dueDate`, `currency`
- `seller`, `buyer`
- `lineItems` (2–3 items)
- `taxes` (rate-based)
- optional: `notes`, `paymentInstructions`, `metadata`

## How to validate
### Option A — Python (jsonschema)
```bash
python - <<'PY'
import json
from jsonschema import Draft202012Validator

schema = json.load(open('projects/promptprecision/specs/invoice-mvp.taskspec.schema.json'))
example = json.load(open('projects/promptprecision/specs/examples/invoice-mvp.taskspec.example.json'))

Draft202012Validator(schema).validate(example)
print('OK: example validates against schema')
PY
```

### Option B — AJV (Node)
```bash
npx ajv validate \
  -s projects/promptprecision/specs/invoice-mvp.taskspec.schema.json \
  -d projects/promptprecision/specs/examples/invoice-mvp.taskspec.example.json
```

Notes:
- The schema is strict (`additionalProperties: false`) for nested objects like `seller`, `buyer`, `lineItems`, and `taxes`.
- `taxes` is **rate-based** here (uses `rate` not `amount`).
- `metadata` values must be primitive JSON types (string/number/boolean/null).
