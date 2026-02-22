# Agent Observability Dashboard — PRD gaps & questions (with proposed defaults)

## Ingestion / SDK contract
- Append-only vs mutable steps?
  - **Proposed default:** append-only; late-arriving info is a new step.
- Idempotency keys for step batches?
  - **Default:** required for step batches; TTL 7 days.
- Canonical step schema/versioning per type?
  - **Default:** payload has `schema_version` per step type.
- Child runs/subgraphs?
  - **Default:** support optional `trace_id` + `span_id` + `parent_run_id`.
- Streaming outputs representation?
  - **Default:** v1 store final only; v1.5 add chunk steps.

## Diff semantics
- Who defines noise/ignore rules?
  - **Default:** product defaults + per-project normalize profiles.
- Alignment rules for repeated tool calls?
  - **Default:** fingerprint match with LCS-like alignment + fallback positional.
- Definition of “prompt stack”?
  - **Default:** ordered messages + retrieved context blocks as separate steps.
- Diff on redacted-only payloads?
  - **Default:** yes; show “changed (redacted)” using payload_hash deltas.

## Policies/Approvals enforcement
- Enforcement authority or audit recorder?
  - **Default recommendation:** enforcing mode for governance-first positioning.
- SDK handshake?
  - **Default:** create approval request + poll; proceed only with server decision token.
- Signed decisions?
  - **Default:** yes (HMAC or Ed25519) with expiry + nonce.
- Break-glass overrides?
  - **Default:** yes; audited as special decision type.

## Auth/RBAC/Tenant isolation
- UI auth method?
  - **Default:** Django session auth in v1; SSO later.
- Minimal RBAC matrix?
  - **Default:** Viewer(read), Approver(approve), Admin(keys/policies/retention).
- Shared DB vs hard isolation?
  - **Default:** shared DB with tenant_id; consider Postgres RLS as defense-in-depth.

## Redaction
- Store redacted-only?
  - **Default:** yes.
- Default secret denylist + patterns?
  - **Default:** authorization/cookie/token/api_key + JWT-like patterns.
- Show redaction reason + JSON paths?
  - **Default:** yes via redaction_meta.

## Scale/Retention
- Expected runs/day, steps/run, payload sizes?
- Retention hard delete vs immutable audit?
  - **Default:** hard delete run data by plan; keep audit longer or leave tombstones.
