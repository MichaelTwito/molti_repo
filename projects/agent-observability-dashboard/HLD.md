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
