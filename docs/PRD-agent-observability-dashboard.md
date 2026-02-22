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

## 7) APIs (v1)
### Core ingestion/query
- POST /v1/runs
- POST /v1/runs/{run_id}/steps
- POST /v1/runs/{run_id}:finish (idempotent)
- GET /v1/runs (cursor)
- GET /v1/runs/{run_id}
- GET /v1/runs/{run_id}/steps

### Diff
- GET /v1/diff

### Policies
- POST /v1/policies
- GET /v1/policies
- POST /v1/policies/{policy_id}:activate

### Approvals
- POST /v1/approvals
- GET /v1/approvals
- POST /v1/approvals/{approval_id}:approve
- POST /v1/approvals/{approval_id}:deny

---

## 8) Diff API (v1) — request/response, limits, errors

### GET `/v1/diff`
Compute a deterministic, redaction-aware diff between two runs.

Query params:
- `runA` (required, uuid)
- `runB` (required, uuid)
- `normalize_profile` (optional, string; default `"strict"`)
  - `"strict"`: diff raw stored values (post-redaction)
  - `"semantic"`: normalize known-noisy fields (timestamps, ids) using server rules
- `mode` (optional, string; default `"steps"`)
  - `"steps"`: compare step streams (recommended v1)
  - `"summary"`: summary only
- `cursor` (optional, opaque string)
- `limit` (optional int; default `200`, max `1000`)

Response `200`:
```json
{
  "runA": {"run_id":"uuid","started_at":"RFC3339","finished_at":"RFC3339|null","status":"running|succeeded|failed|canceled"},
  "runB": {"run_id":"uuid","started_at":"RFC3339","finished_at":"RFC3339|null","status":"running|succeeded|failed|canceled"},
  "normalize_profile": "strict|semantic",
  "mode": "steps|summary",
  "summary": {
    "aligned_steps": 120,
    "only_in_A": 3,
    "only_in_B": 5,
    "changed": 17,
    "redaction_opaque": 4
  },
  "items": [
    {
      "kind": "step_added|step_removed|field_changed|field_redacted|order_changed",
      "severity": "info|warn",
      "path": "$.steps[42].payload.tool_args.prompt",
      "stepA": {"step_id":"uuid","seq":42,"ts":"RFC3339","type":"tool","name":"open_url"},
      "stepB": {"step_id":"uuid","seq":41,"ts":"RFC3339","type":"tool","name":"open_url"},
      "before": {"type":"string","value":"..."},
      "after":  {"type":"string","value":"..."},
      "redaction": {"opaque": false, "reason": null}
    }
  ],
  "page": {"next_cursor": "opaque|null", "has_more": true}
}
```

Value encoding rules:
- Fully redacted field: `{ "type": "redacted", "value": null }`
- When server cannot safely compare due to redaction: emit `kind:"field_redacted"` and set `redaction.opaque=true`

Determinism rules:
- Deterministic for the same stored data + `normalize_profile`.
- Ordering uses `(seq, step_id)` as stable tiebreak.

Limits (v1 defaults):
- Max compared steps per run: `50_000` (beyond that: `413 diff_too_large`)
- Max compute time: `5s` soft budget
- Runs must be within same tenant; cross-tenant always `404`

Errors:
- `400 invalid_request`
- `404 not_found`
- `413 diff_too_large`
- `422 diff_incompatible`
- `429 rate_limited` (with `Retry-After`)

---

## 9) Policies APIs (v1) — schemas, endpoints, RBAC

### Policy object (v1)
```json
{
  "policy_id": "uuid",
  "project_id": "uuid",
  "name": "string",
  "description": "string|null",
  "status": "draft|active|archived",
  "version": 1,
  "scope": {
    "tool_names": ["string"],
    "tool_name_prefixes": ["string"],
    "tags_any": {"env": "prod"},
    "applies_to": "ingest_only|enforcement"
  },
  "rules": [
    {
      "rule_id": "string",
      "effect": "allow|require_approval|block",
      "when": {
        "tool_args_jsonpath_exists": ["$.url"],
        "tool_args_size_gt_bytes": 4096
      },
      "message": "string|null"
    }
  ],
  "created_at": "RFC3339",
  "created_by": {"user_id": "string", "email": "string|null"},
  "updated_at": "RFC3339",
  "activated_at": "RFC3339|null",
  "activated_by": {"user_id": "string", "email": "string|null"}
}
```

Notes:
- One active policy per `(tenant, project_id)` in v1.

#### POST `/v1/policies` (create draft)
RBAC: **Admin only**

Request: `{ project_id, name, description?, scope, rules }`

Response `201`: `{ "policy": { /* Policy */ } }`

#### GET `/v1/policies`
RBAC: Viewer/Approver/Admin

Query: `project_id?`, `status?`, `cursor?`, `limit?`

Response `200`:
```json
{ "items": [ {"policy": {} } ], "page": {"next_cursor":"opaque|null","has_more":false} }
```

#### POST `/v1/policies/{policy_id}:activate`
RBAC: **Admin only**

Request: `{ "note": "string|null" }`

Response `200`: `{ "policy": { /* active */ }, "replaced_policy_id": "uuid|null" }`

---

## 10) Approvals APIs (v1) — schemas, idempotency, DecisionToken issuance

### Approval object (v1)
```json
{
  "approval_id": "uuid",
  "project_id": "uuid",
  "status": "pending|approved|denied|expired|canceled",
  "run_id": "uuid",
  "step_id": "uuid|null",
  "tool_name": "string",
  "tool_args_hash": "sha256:hex",
  "tool_args_redaction_meta": {"version":1,"redacted":true,"paths":["$.headers.authorization"],"rules":[{"rule_id":"denylist.auth","action":"remove","reason":"secret"}]},
  "policy_id": "uuid|null",
  "policy_rule_id": "string|null",
  "requested_at": "RFC3339",
  "requested_by": {"subject":"string","type":"sdk|user"},
  "expires_at": "RFC3339",
  "decided_at": "RFC3339|null",
  "decided_by": {"user_id":"string","email":"string|null"},
  "decision": "approve|deny|null",
  "decision_note": "string|null",
  "decision_token_id": "string|null"
}
```

#### POST `/v1/approvals` (create)
RBAC: ingest key (SDK) **or** Admin (UI).

Idempotency:
- Supports `Idempotency-Key`.
- Same key + same canonical body => same approval.
- Body mismatch => `409 idempotency_conflict`.

Response `201`: `{ "approval": { /* Approval */ } }`

#### GET `/v1/approvals`
RBAC: Viewer/Approver/Admin (cursor pagination)

#### POST `/v1/approvals/{approval_id}:approve`
RBAC: **Approver or Admin**

Response `200`:
```json
{
  "approval": {},
  "decision_token": {
    "token": "string(JWT)",
    "token_id": "string(jti)",
    "nonce": "string",
    "issued_at": "RFC3339",
    "expires_at": "RFC3339",
    "run_id": "uuid",
    "project_id": "uuid",
    "tool_name": "string",
    "tool_args_hash": "sha256:hex",
    "policy_id": "uuid|null",
    "approval_id": "uuid"
  }
}
```

#### POST `/v1/approvals/{approval_id}:deny`
RBAC: **Approver or Admin**

DecisionToken binding requirements:
- Tool execution step MUST include `decision_token_id` (JWT `jti`) and `nonce`.
- Server enforces single-use nonce consumption at tool-execution time.

---

## 11) `redaction_meta` (v1) — schema and behavior in diff/query

Schema:
```json
{
  "version": 1,
  "redacted": true,
  "method": "remove|mask|hash|truncate",
  "paths": ["$.headers.authorization"],
  "rules": [
    {"rule_id":"string","action":"remove|mask|hash|truncate","reason":"string|null"}
  ],
  "notes": "string|null"
}
```

Behavior:
- Diff operates on **stored values** (already redacted in v1).
- If a path is redacted in either run, emit `field_redacted` and mark as opaque when needed.
- Server MUST NOT support filtering on redacted-only fields.

---

## 12) RBAC (v1 minimal)
Auth types:
- Ingest API keys: scoped to (tenant, project) and ingestion endpoints only.
- UI users: session/JWT with RBAC roles.

Matrix:
- Viewer: GET runs/steps/diff, GET policies, GET approvals
- Approver: Viewer + POST approvals/{id}:approve|deny
- Admin: Approver + POST/activate policies, manage keys, retention, break-glass

---

## 13) Retention & audit (v1)
- Runs/steps: hard delete per plan.
- AuditLog: retained longer (default 1 year) and may retain tombstones/hashes.
- Optional: hash-chain audit rows for tamper evidence.

---

## 14) Rate limiting + pagination contract
- 429 includes `Retry-After` seconds.
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- Cursor is opaque; ordering: started_at desc + run_id tiebreak.

