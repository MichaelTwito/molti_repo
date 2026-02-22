# PRD: Agent Observability Dashboard (Runs, Diff, Policies, Approvals)

## 0) TL;DR
Build a **multi-tenant observability + governance dashboard for AI agents**.

Core value:
- **Trace every run** (prompt stack, tool calls, artifacts, costs)
- **Diff two runs** to explain regressions
- **Enforce policy gates** (require approval / block) and keep an **audit log**

Target users are developers/operators running agentic workflows in production (LangGraph-first).

---

## 1) Problem statement
Teams deploying agentic systems struggle with:
- **Debugging**: “Why did the agent do this?” and “What changed?”
- **Reproducibility**: prompt/context/tool outputs vary and are hard to compare
- **Governance**: tool actions can be risky; approvals need to be enforced and auditable
- **Multi-tenant isolation**: traces and artifacts must not leak across customers

Existing logs are unstructured, scattered, and non-comparable.

---

## 2) Goals / Success criteria
### Goals
1. Provide a clear, searchable **run timeline** with structured events.
2. Provide first-class **Run Diff** to identify changes across runs.
3. Support **Policy evaluation** and **Approval gates** with immutable audit trail.
4. Enforce **multi-tenant isolation** and data redaction.
5. Be usable with minimal integration friction (LangGraph-first SDK).

### Success criteria (measurable)
- Time-to-root-cause for common incidents drops from hours → minutes.
- Users can answer, from the UI:
  - “Which prompt/tool output caused this?”
  - “Which tool calls were blocked/approved and by whom?”
- Zero cross-tenant data leakage (tested + monitored).

---

## 3) Non-goals
- Model-weight interpretability (neurons/attention/causal tracing) in v1.
- Full APM/infra monitoring (CPU, memory, traces across microservices).
- Building a full agent framework. This product observes/governs runs.

---

## 4) Primary users (personas)
1. **Agent Developer (Dev)**
2. **Agent Operator (Ops/On-call)**
3. **Security/Compliance (GRC-lite)**

---

## 5) Core user journeys
### Journey A: Debug a bad response
Filter runs → open timeline → inspect steps → diff vs good run.

### Journey B: Regression after prompt/tool change
Select runA/runB → diff highlights prompt/tools/model/metadata changes.

### Journey C: Risky action requires approval
Risky tool call triggers approval request → approver decides → decision is audited and bound to execution.

---

## 6) Functional requirements

### 6.1 Runs list (Search / Filters)
MUST:
- List runs with: status, start time, duration, project, tenant, model(s), cost, tool count.
- Filter by: time range, status, tool name, model, tenant_id, tags.
- Pagination and stable ordering.

### 6.2 Run detail (Timeline)
MUST:
- Timeline of steps: prompt/model/tool/policy/approval/error.
- JSON view + redaction indicators.

### 6.3 Run Diff (Two-run comparison)
MUST:
- Diff categories: prompt stack, tool calls, model config, metadata/tags.
- **Deterministic output** for same inputs + normalize profile.
- Redaction-aware diffs: show “changed (redacted)” based on hashes when needed.

SHOULD:
- Normalize noise fields via profiles.
- Step alignment heuristics.

### 6.4 Policies
MUST:
- Versioned policy sets per project.
- Record policy eval event in run.

### 6.5 Approvals
MUST:
- Approval request object includes tenant/project/run/step + action summary + risk label + payload hash.
- Approve/deny + immutable audit log.

### 6.6 Multi-tenant isolation & RBAC
MUST:
- Tenant isolation enforced at query + storage layers.
- RBAC roles (v1 minimal): Admin, Approver, Viewer (Developer optional).

### 6.7 Redaction & secrets handling
MUST:
- Store **redacted-only** payloads in v1.
- Never store cookies/auth headers by default.

---

## 7) UX / Information architecture
Projects → Runs / Policies / Approvals / Settings.

---

## 8) Data model (v1 conceptual)
- Tenant, Project, User
- Run
- Step (append-only)
- PolicySet (versioned)
- ApprovalRequest + ApprovalDecision
- AuditLog (append-only)

---

## 9) APIs (v1 minimal)
### Ingest
- `POST /v1/runs` create run
- `POST /v1/runs/{run_id}/steps` append steps (batch)
- `POST /v1/runs/{run_id}:finish` finalize status/timestamps (**idempotent**)

### Query
- `GET /v1/runs` list with filters
- `GET /v1/runs/{run_id}` run details
- `GET /v1/runs/{run_id}/steps`
- `GET /v1/diff?runA=...&runB=...`

### Approvals
- `POST /v1/approvals` create approval request
- `POST /v1/approvals/{id}:approve`
- `POST /v1/approvals/{id}:deny`

### Policies
- `GET /v1/policies`
- `POST /v1/policies`

---

## 10) Security, privacy, and compliance

### Enforcement boundary (MUST)
- For tools marked require_approval/block, the server is the source of truth.
- SDK must obtain a signed DecisionToken before executing the tool.
- Tool execution events include DecisionToken nonce/id to bind “approved” → “executed”.
- Break-glass is supported for Admins only and always audited.

### RBAC (v1 minimal) (MUST)
- Viewer: read runs/steps/diff
- Approver: Viewer + approve/deny approvals
- Admin: manage API keys, policies, retention settings, break-glass

### Retention & deletion (MUST)
- Run/Step payloads follow plan retention (e.g., 7/30/90 days) and are hard-deleted.
- AuditLog retention is >= run retention (default 1 year) and may retain tombstones/hashes.

### Search (MUST)
- Only index/search whitelisted metadata fields (env, release, agent_version, tool_name, model_name, status).
- Do not full-text search raw step payloads in v1.

---

## 11) Performance / scale targets (initial)
- Ingestion: handle bursts (e.g., 100 steps/sec per tenant) without UI degradation.
- Query: runs list p95 <2s typical tenant (last 24h, <10k runs).

---

## 12) Rollout plan
Alpha: timeline+search → Beta: multi-tenant+diff → Beta+: policies+approvals → GA: quotas/retention/RBAC hardening.

---

## 13) Open questions / decisions
- Storage: Postgres JSONB v1; partitioning later.
- Diff alignment heuristics.
- Approval UX + notifications.

---

## 14) Milestones & Backlog (P0/P1/P2)
(See previous version; unchanged in intent.)

## 15) Acceptance criteria (v1)
- Can ingest demo run end-to-end.
- Can view timeline.
- Can diff two runs with meaningful deltas.
- Tenant isolation validated with automated tests.
