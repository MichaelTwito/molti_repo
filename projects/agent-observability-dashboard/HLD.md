# Agent Observability Dashboard — High-level design (Python/Django)

## Architecture
- **Django + DRF**: ingestion + query + diff + policies/approvals APIs
- **Postgres**: runs/steps/policies/approvals/audit (JSONB payloads; redacted-only v1)
- **Celery + Redis**: rollups, diff precompute/cache, retention, notifications
- Optional: **S3** for large artifacts (store references in DB)

## Ingestion contract (proposed v1 defaults)
- Steps are **append-only** (no mutation). Late-arriving info becomes a new step.
- Server assigns monotonic `seq` per run; supports concurrent writers.
- `POST /v1/runs/{run_id}/steps` is **batch** and supports idempotency:
  - `Idempotency-Key` required for batches; scoped to (tenant, project, run)
  - TTL suggested: 7 days; replay returns same assigned seq range
- Batch semantics (v1): **all-or-nothing** transaction.
- Hard limits (suggested): max 200 steps/batch; max 256KB JSON per step; max 10MB request.
- Run lifecycle: `POST /runs` creates status=running; `POST /runs/{id}:finish` finalizes status/timestamps.

## Core data model (tenant-scoped)
- Tenant, Project
- APIKey (hashed)
- Run (denorm fields for listing)
- Step (seq unique per run; type/name/payload JSONB + redaction_meta + payload_hash)
- PolicySet (versioned)
- ApprovalRequest + ApprovalDecision (also written as Step)
- AuditLog (append-only)

## API (v1)
- POST /v1/runs
- POST /v1/runs/{run_id}/steps (batch + idempotency)
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

## Policies/Approvals (enforcement boundary)
- v1 must choose: **audit-only** vs **enforcing**.
- If enforcing: server issues signed decision token (includes run_id/step_id/tool_name/payload_hash/expiry/nonce) and SDK must present it before executing.

## Redaction (v1)
- Store **redacted-only** payloads
- Server is authoritative: denylist keys/pattern rules + optional SDK annotations
- Persist redaction_meta (paths + rule ids)

## Scalability
- strong indexes (tenant_id, started_at), (tenant_id, run_id, seq)
- cursor pagination; cache hot lists
- partition Step table later; retention via partition drops
- optional Postgres RLS for defense-in-depth

## Operational NFRs (suggested)
- Rate limits / quotas per tenant/project; backpressure via 429 + retry-after
- p95 ingestion latency target (batch typical) + p95 runs list latency
- retention policy: reconcile run deletion vs audit immutability (tombstones or longer audit retention)
- artifacts contract: store refs (uri, sha256, size, content_type) + optional S3
