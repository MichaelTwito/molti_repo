# Agent Observability Dashboard — High-level design (Python/Django)

## Architecture
- **Django + DRF**: ingestion + query + diff + policies/approvals APIs
- **Postgres**: runs/steps/policies/approvals/audit (JSONB payloads; redacted-only v1)
- **Celery + Redis**: rollups, diff precompute/cache, retention, notifications
- Optional: **S3** for large artifacts (store references in DB)

## Policies/Approvals (enforcement boundary) — v1 decision
V1 is **enforcing** for gated tools:
- Server evaluates policy and issues a signed DecisionToken.
- SDK MUST present a valid DecisionToken to proceed with tool execution.
- All decisions (including break-glass) are written to AuditLog and as Steps.

DecisionToken requirements:
- Signed with Ed25519 (preferred) or HMAC-SHA256
- Claims: tenant_id, project_id, run_id, step_id, tool_name, payload_hash, decision, issued_at, exp, nonce
- Replay protection: store nonce in DB with UNIQUE constraint until exp
- Key rotation: support multiple active signing keys with `kid`

## Ingestion contract (v1 defaults)
- Steps are **append-only** (no mutation). Late-arriving info becomes a new step.
- Server assigns monotonic `seq` per run; supports concurrent writers.
- `POST /v1/runs/{run_id}/steps` is batch + idempotent:
  - `Idempotency-Key` required; scoped to (tenant, project, run)
  - TTL: 7 days
  - replay w/ same payload returns stored response
  - replay w/ different payload returns 409
- Batch semantics: **all-or-nothing** transaction.
- Hard limits: max 200 steps/batch; max 256KB JSON per step; max 10MB request.
- Run lifecycle: `POST /runs` creates status=running; `POST /runs/{id}:finish` finalizes status/timestamps.

## Idempotency (implementation detail)
Create table `ingest_idempotency_keys`:
- tenant_id, project_id, run_id
- key (text)
- request_hash (sha256 of canonicalized request body)
- first_seen_at, expires_at
- response_json (assigned seq range + created step_ids)
Constraints:
- UNIQUE(tenant_id, project_id, run_id, key)

## Step ordering / concurrency (Postgres)
To assign monotonic `seq` per run under concurrency:
- Maintain `runs.next_seq` integer column.
- Ingest transaction:
  1) SELECT run FOR UPDATE
  2) allocate [next_seq, next_seq + batch_len - 1]
  3) update runs.next_seq += batch_len
  4) insert steps with assigned seq

## Core data model (tenant-scoped)
- Tenant, Project
- APIKey (hashed)
- Run (denorm fields for listing/filtering)
- Step (seq unique per run; type/name/payload JSONB + redaction_meta + payload_hash)
- PolicySet (versioned)
- ApprovalRequest + ApprovalDecision (also written as Step)
- AuditLog (append-only)

## API (v1)
- POST /v1/runs
- POST /v1/runs/{run_id}/steps
- POST /v1/runs/{run_id}:finish
- GET /v1/runs (cursor pagination + filters)
- GET /v1/runs/{run_id} + /steps
- GET /v1/diff?runA=&runB=&normalize_profile=
- Policies: GET/POST/activate
- Approvals: create/list/approve/deny

## Diff engine (v1)
- Deterministic diff for same inputs + normalize profile
- Normalization profiles (JSONPath ignore rules)
- Fingerprinting (tool_name + normalized args)
- Alignment (fingerprint match + fallback positional)
- Redaction-aware diffs: show “changed (redacted)” via payload_hash deltas
- Cache DiffResult (per runA/runB/profile)

## Postgres indexing & JSONB strategy
Required indexes (v1):
- runs: (tenant_id, project_id, started_at DESC), (tenant_id, project_id, status, started_at DESC)
- steps: UNIQUE(run_id, seq), (tenant_id, run_id, seq), (tenant_id, ts)
- approvals: (tenant_id, project_id, status, created_at DESC)
Strategy:
- Denormalize filterable fields into columns (tool_name, model_name, env, agent_version)
- Keep full payload in JSONB for display; avoid deep JSON queries in hot paths
Partitioning (v1.5):
- Partition steps by time; retention via partition drops

## Tenant isolation (defense-in-depth)
- Enforce tenant_id scoping in every queryset + endpoint tests
- Enable Postgres RLS in production

## Redaction (v1)
- Store **redacted-only** payloads
- Server is authoritative: denylist keys/pattern rules + optional SDK annotations
- Persist redaction_meta (paths + rule ids)

## Operational NFRs (suggested)
- Rate limits / quotas per tenant/project; backpressure via 429 + retry-after
- p95 ingest latency target (typical batch) + p95 runs list latency
- retention policy: reconcile run deletion vs audit immutability (tombstones or longer audit retention)
- artifacts contract: store refs (uri, sha256, size, content_type) + optional S3
