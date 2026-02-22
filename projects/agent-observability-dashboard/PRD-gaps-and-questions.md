# Agent Observability Dashboard — PRD gaps & questions (v1 defaults)

## V1 decisions (locked)
- Enforcement: enforcing (DecisionToken)
- Storage: redacted-only
- Tenant isolation: app scoping + Postgres RLS
- Idempotency: persisted keys + RFC8785 JCS hashing

## Remaining to close (next reviewers)
- Full schemas for diff/policies/approvals responses
- Redaction_meta schema details
- Audit hash-chain decision (optional)
