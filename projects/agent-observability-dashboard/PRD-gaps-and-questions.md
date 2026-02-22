# Agent Observability Dashboard — PRD gaps & questions (v1 defaults)

## V1 decisions (locked)
- Enforcement mode: **ENFORCING** (server is authority for gated actions)
- Storage: **REDACTED-ONLY** payloads in Postgres; artifacts by reference (S3 optional)
- Tenant isolation: app-layer scoping + **Postgres RLS enabled in production**
- Idempotency: persisted idempotency keys with request_hash; conflicts return 409

## Ingestion / SDK contract
- Append-only vs mutable steps? **Append-only**.
- Idempotency keys for step batches? **Required**, TTL 7d.
- Canonical step schema/versioning per type? **Yes** (`schema_version` per step type).
- Child runs/subgraphs? **Support** trace_id/span_id/parent_run_id.
- Streaming outputs? **v1 final-only**; later add chunk steps.

## Diff semantics
- Noise/ignore rules: product defaults + per-project normalize profiles.
- Alignment: fingerprint + LCS-like, fallback positional.
- Prompt stack: ordered messages + retrieved context blocks as separate steps.
- Redacted diffs: show “changed (redacted)” via payload_hash deltas.

## Auth/RBAC/Tenant isolation
- UI auth: Django sessions/JWT acceptable; SSO later.
- Minimal RBAC: Viewer(read), Approver(approve), Admin(keys/policies/retention).
- Shared DB with tenant_id + RLS.

## Redaction
- Store redacted-only.
- Default denylist keys/patterns (authorization/cookie/token/api_key + JWT-like patterns).
- Show redaction reason + JSON paths via redaction_meta.

## Scale/Retention (defaults to validate)
- Target (per tenant): 50k runs/day, p95 200 steps/run, p95 payload 8KB (redacted)
- Burst ingest: 500 steps/sec sustained for 5 minutes
- SLOs:
  - ingest p95 < 300ms for 50-step batch
  - runs list p95 < 1.5s for last 24h up to 10k runs
- Postgres:
  - require connection pooling (pgBouncer)
  - partition steps once table > ~50M rows
- Retention & audit:
  - hard delete run/step payloads per plan
  - keep audit longer or keep tombstones/hashes for integrity
