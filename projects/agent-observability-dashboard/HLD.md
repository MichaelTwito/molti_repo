# Agent Observability Dashboard — High-level design (Python/Django)

## Architecture
- **Django + DRF**: ingestion + query + diff + policies/approvals APIs
- **Postgres**: runs/steps/policies/approvals/audit (JSONB payloads; redacted-only v1)
- **Celery + Redis**: rollups, diff precompute/cache, retention, notifications
- Optional: **S3** for large artifacts (store references in DB)

## Core data model (tenant-scoped)
- Tenant, Project
- APIKey (hashed)
- Run (denorm fields for listing)
- Step (append-only, seq per run; type/name/payload JSONB + redaction_meta + payload_hash)
- PolicySet (versioned)
- ApprovalRequest + ApprovalDecision (also written as Step)
- AuditLog (append-only)

## API (v1)
- POST /v1/runs
- POST /v1/runs/{run_id}/steps (batch + idempotency)
- GET /v1/runs (cursor pagination + filters)
- GET /v1/runs/{run_id} + /steps
- GET /v1/diff?runA=&runB=&normalize_profile=
- Policies: GET/POST/activate
- Approvals: create/list/approve/deny

## Diff engine (v1)
- Normalization profiles (JSONPath ignore rules)
- Fingerprinting (tool_name + normalized args)
- Alignment (fingerprint match + fallback positional)
- Structured output (summary + per-category JSON patch)
- Cache DiffResult

## Redaction (v1)
- Store **redacted-only** payloads
- SDK annotations + server denylist/pattern rules
- Persist redaction_meta (paths + rule ids)

## Scalability
- batch step ingestion
- strong indexes (tenant_id, started_at), (tenant_id, run_id, seq)
- cursor pagination; cache hot lists
- partition Step table later; retention via partition drops
- optional Postgres RLS for defense-in-depth

## Key open decisions
- enforcement boundary for approvals (SDK local gate vs server authority)
- diff determinism + user-configurable ignore rules
- child runs/subgraphs representation
