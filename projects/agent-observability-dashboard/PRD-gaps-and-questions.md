# Agent Observability Dashboard — PRD gaps & questions

## Ingestion / SDK contract
- Append-only vs mutable steps?
- Idempotency keys for step batches?
- Canonical step schema/versioning per type?
- Child runs/subgraphs?
- Streaming outputs representation?

## Diff semantics
- Who defines noise/ignore rules (defaults vs per-tenant/project)?
- Alignment rules for repeated tool calls?
- Definition of “prompt stack”?
- Diff on redacted-only payloads?

## Policies/Approvals enforcement
- Is the system an enforcement authority or audit recorder?
- SDK handshake: create approval request + poll/wait?
- Signed decisions (HMAC) verified by SDK?
- Break-glass overrides?

## Auth/RBAC/Tenant isolation
- UI auth method (session/JWT/OAuth)?
- Minimal RBAC matrix per action
- Shared DB vs hard isolation plans

## Redaction
- Confirm store redacted-only
- Default secret denylist + pattern rules
- Show redaction reason + JSON paths?

## Scale/Retention
- Expected runs/day, steps/run, payload sizes
- Retention hard delete vs immutable audit requirements
