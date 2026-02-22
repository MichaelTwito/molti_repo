# Agent Observability Dashboard (Governance-first)

## One-liner
Multi-tenant observability + governance for tool-using AI agents: **runs timeline + run diff + policy/approvals + audit**.

## Core value
- Trace every run (prompt/model/tool/policy/approval/error) in a clean timeline.
- Diff two runs to explain regressions (alignment heuristics + noise normalization).
- Enforce policy gates + approvals with immutable audit trail.

## Wedge
**“Diff + Approvals for tool-using agents in production”** (LangGraph-first).

## MVP (P0)
- Ingest runs + steps
- Runs list + filters
- Run detail timeline
- Run diff (killer)

## Next (P1)
- Policies CRUD + eval steps
- Approvals inbox + approve/deny + audit
- Minimal RBAC + tenant isolation tests

## Key risks
- Competitive market (LangSmith, Langfuse, Phoenix, Weave, etc.) → must differentiate on diff + governance.
- Scope creep across frameworks → stay LangGraph-first.

## References
- PRD: `docs/PRD-agent-observability-dashboard.md`
