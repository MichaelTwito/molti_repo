# Agent Observability Dashboard — High-level design (Python/Django)

## Architecture
- Django + DRF: ingestion + query + diff + policies/approvals
- Postgres: runs/steps/policies/approvals/audit (JSONB payloads; redacted-only v1)
- Celery + Redis: rollups, diff cache, retention, notifications
- Optional S3: large artifacts by reference

## Policies/Approvals — enforcing (v1)
V1 is enforcing for gated tools:
- Server evaluates policy and issues a signed DecisionToken.
- SDK must present a valid DecisionToken to proceed with tool execution.

DecisionToken format (v1):
- JWT (JWS) with alg=EdDSA when using Ed25519.
- JWKS: GET /v1/keys/jwks.json
- Max lifetime: 10 minutes; allow 60s skew.

Replay protection:
- nonce is consumed at tool-execution time.
- UNIQUE(tenant_id, nonce) until exp; reuse => 409 token_replay.

## Ingestion contract (v1)
- Steps append-only; late info becomes new step.
- Server assigns monotonic seq per run.
- Batch ingest is idempotent via Idempotency-Key.

## Idempotency (implementation detail)
Table ingest_idempotency_keys:
- tenant_id, project_id, run_id, key
- request_hash (sha256)
- response_json
- expires_at

Hashing:
- request_hash = SHA-256 over RFC 8785 JSON Canonicalization Scheme (JCS) of request body.

Semantics:
- same key + same hash => return stored response
- same key + different hash => 409

## Step ordering / concurrency
- runs has next_seq integer
- ingest transaction: SELECT run FOR UPDATE → allocate seq range → update next_seq → insert steps.

## Indexing strategy
- steps: UNIQUE(run_id, seq), (tenant_id, run_id, seq), (tenant_id, ts)
- runs: (tenant_id, project_id, started_at desc), (tenant_id, project_id, status, started_at desc)
- approvals: (tenant_id, project_id, status, created_at desc)
- Denormalize filter fields into columns; keep full payload JSONB for display.

## Tenant isolation
- Enforce tenant scoping in every queryset + tests.
- Enable Postgres RLS in production.

## Operational contracts
- Rate limits: 429 + Retry-After + X-RateLimit-* headers.
- Cursor pagination only.
- Retention: hard delete runs/steps per plan; audit longer with tombstones/hashes.

---

## Diff endpoint — implementation notes (v1)

API contract:
- GET `/v1/diff?runA=&runB=&normalize_profile=&mode=&cursor=&limit=`
- Pagination is cursor-based over deterministic ordering of diff items.

Algorithm (steps-mode):
- Load steps ordered by `(seq, step_id)`.
- Align by seq; gaps produce `step_added/step_removed`.
- Field diff: JSON structural diff on `payload`.
- Redaction-aware:
  - Any path in `redaction_meta.paths` is treated as opaque; emit `field_redacted`.
  - Never attempt to infer original values.

Caching:
- Optional: Redis pages keyed by `(tenant, runA, runB, normalize_profile)` with short TTL.

Limits:
- Hard cap steps compared; return `413 diff_too_large`.
- Cross-tenant runs always `404`.

---

## Policies endpoints + RBAC enforcement (v1)
Endpoints:
- POST `/v1/policies` (Admin)
- GET `/v1/policies` (Viewer+)
- POST `/v1/policies/{policy_id}:activate` (Admin)

Storage:
- partial unique index: `UNIQUE(tenant_id, project_id) WHERE status='active'`.

RBAC:
- Enforced via DRF permissions + project scoping in queryset.

---

## Approvals endpoints — idempotency + DecisionToken issuance (v1)
Endpoints:
- POST `/v1/approvals` (SDK ingest key allowed; also Admin for UI)
- GET `/v1/approvals` (Viewer+)
- POST `/v1/approvals/{id}:approve` (Approver/Admin) → returns DecisionToken JWT
- POST `/v1/approvals/{id}:deny` (Approver/Admin)

Idempotency:
- Apply persisted Idempotency-Key keyed by `(tenant_id, project_id, endpoint, key)`.
- Hash via RFC8785 JCS; conflict => `409`.

State machine:
- `pending` → `approved` (mint token) or `denied`
- `pending` → `expired` via TTL job

DecisionToken:
- Claims include `jti`, `nonce`, tenant/project/run/tool/tool_args_hash, approval_id, policy_id, exp/iat.
- Replay protection via `decision_token_nonces` table; consume on tool execution.

---

## `redaction_meta` — storage and how it affects diff/query (v1)
- Steps store **redacted JSONB only**.
- Store `redaction_meta` alongside payload.
- Diff compares stored payloads; redacted paths are opaque.
- Do not support server-side filtering on redacted paths.
