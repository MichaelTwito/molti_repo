# PRD: Agent Observability Dashboard (Runs, Diff, Policies, Approvals)

## 0) TL;DR
Build a **multi-tenant observability + governance dashboard for AI agents**.

Core value:
- Trace every run (timeline)
- Diff two runs
- Enforce policy gates + approvals with audit

---

## 1) Problem statement
Teams deploying agentic systems struggle with debugging, reproducibility, and governance.

---

## 2) Goals / Success criteria
- Clear run timeline
- Run Diff
- Policy + approvals
- Tenant isolation + redaction

---

## 3) Non-goals
- Full infra APM
- Model-weight interpretability

---

## 4) Functional requirements (summary)
- Runs list + filters
- Run timeline
- Diff
- Policies + approvals
- RBAC
- Redaction

---

## 5) Enforcement boundary (MUST)
- For tools marked require_approval/block, the server is the source of truth.
- SDK must obtain a signed DecisionToken before executing the tool.
- Tool execution events include DecisionToken nonce/id to bind “approved” → “executed”.
- Break-glass: Admin only, always audited.

---

## 6) Wire contracts (v1) — request/response shapes

### Common
- Auth: `Authorization: Bearer <token>`
- `tenant_id` is derived from auth context (NOT accepted from client in request body)

Error envelope:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {"field": "message"},
    "retryable": true
  }
}
```

### Run object
```json
{
  "run_id": "uuid",
  "project_id": "uuid",
  "status": "running|succeeded|failed|canceled",
  "started_at": "RFC3339",
  "finished_at": "RFC3339|null",
  "duration_ms": 1234,
  "trace_id": "string|null",
  "parent_run_id": "uuid|null",
  "tags": {"env": "prod", "release": "..."},
  "model_names": ["..."],
  "tool_count": 12,
  "cost_usd": 0.123
}
```

### Step object (append-only)
```json
{
  "step_id": "uuid",
  "run_id": "uuid",
  "seq": 42,
  "ts": "RFC3339",
  "type": "prompt|model|tool|policy|approval|error|artifact",
  "name": "string",
  "schema_version": 1,
  "payload": {"redacted": true},
  "payload_hash": "sha256:hex",
  "redaction_meta": {
    "paths": ["$.headers.authorization"],
    "rules": [{"rule_id": "denylist.auth", "reason": "secret"}]
  },
  "tool_name": "string|null",
  "model_name": "string|null",
  "trace_id": "string|null",
  "span_id": "string|null",
  "decision_token_id": "string|null"
}
```

### POST /v1/runs/{run_id}/steps (batch)
Request:
```json
{ "steps": [ {"type":"tool","schema_version":1,"name":"...","ts":"...","payload":{}} ] }
```

Response:
```json
{
  "run_id": "uuid",
  "assigned": [
    {"index": 0, "step_id": "uuid", "seq": 100},
    {"index": 1, "step_id": "uuid", "seq": 101}
  ]
}
```

---

## 7) APIs (v1 minimal)
- POST /v1/runs
- POST /v1/runs/{run_id}/steps
- POST /v1/runs/{run_id}:finish (idempotent)
- GET /v1/runs (cursor)
- GET /v1/runs/{run_id}
- GET /v1/runs/{run_id}/steps
- GET /v1/diff?runA=&runB=&normalize_profile=
- Policies: GET/POST/activate
- Approvals: create/list/approve/deny

---

## 8) RBAC (v1 minimal)
Auth types:
- Ingest API keys: scoped to (tenant, project) and ingestion endpoints only.
- UI users: session/JWT with RBAC roles.

Matrix:
- Viewer: GET runs/steps/diff, GET policies, GET approvals
- Approver: Viewer + POST approvals/{id}:approve|deny
- Admin: Approver + POST/activate policies, manage keys, retention, break-glass

---

## 9) Retention & audit (v1)
- Runs/steps: hard delete per plan.
- AuditLog: retained longer (default 1 year) and may retain tombstones/hashes.
- Optional: hash-chain audit rows for tamper evidence.

---

## 10) Rate limiting + pagination contract
- 429 includes `Retry-After` seconds.
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- Cursor is opaque; ordering: started_at desc + run_id tiebreak.

