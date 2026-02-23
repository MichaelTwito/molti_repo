# Marketing Feasibility Reports — 2026-02-23

Scope: English-only. Goal: internal decision (build / don't build) for two ideas:
- Agent Observability Dashboard (AOD)
- PromptPrecision

Sources: HN (Algolia search), GitHub repo search, targeted web_fetch.
Note: X API search was blocked by CreditsDepleted (no credits), so X is excluded.

---

## 1) AOD — Agent Observability Dashboard

### What the market is already buying / using
Signals from HN + GitHub show a crowded but active LLM/agent observability space:
- **Langfuse** (open source, very popular): https://github.com/langfuse/langfuse
- **Helicone** (OSS + gateway + observability): https://github.com/Helicone/helicone
- **OpenLLMetry / Traceloop** (OpenTelemetry-based instrumentation): https://github.com/traceloop/openllmetry
- **OpenLIT** (OTel-native platform + dashboard + prompt mgmt): https://github.com/openlit/openlit

HN also surfaces OTel as the dominant “meta-standard” framing for observability:
- “LLM Observability in the Wild – Why OpenTelemetry Should Be the Standard”: https://signoz.io/blog/llm-observability-opentelemetry/

### What’s missing / wedge opportunities
Despite many tools, the common center of gravity is still **tracing + debugging LLM calls**.
AOD’s strongest wedge is **governance-first agent runs**:
- Explicit **run/step contracts** (inputs/outputs, tool calls, events)
- **Policies + approvals** (pre/post conditions)
- **Redaction & audit** (who saw what, retention, exports)
- “Production hygiene”: caps/limits, retention invariants

This is meaningfully different from “observe my LLM calls” and maps to regulated / high-stakes workflows.

### Competitive posture (positioning suggestion)
Position as “Agent Run Governance & Audit” layered on top of OTel traces:
- Ingest OTel + provider traces, but add:
  - approvals
  - redaction rules
  - immutable audit
  - retention & invariants

### Cheap validation experiments (1 week)
1) **Landing page + 3 positioning A/Bs**: “Agent Run Governance”, “Agent Approval Workflows”, “Audit for AI Actions”
2) **Design partner outreach** (5–10): companies shipping agentic workflows (support, ops, compliance)
3) **Open-source wedge**: publish a minimal spec + SDK for run/step events + redaction hooks.

### Build vs don’t build (preliminary)
- **Build if** we can own “governance/audit” as a distinct category and quickly secure 3–5 design partners.
- **Don’t build** if the market only wants cheaper tracing and won’t pay for policy/approval/audit.

Provisional recommendation: **BUILD (conditional)** — but only with a governance-first MVP and design partners.

---

## 2) PromptPrecision

### What the market is already doing
Signals show demand for structured-output reliability + eval tooling:
HN surfaced projects explicitly about spec-testing structured outputs:
- **Litmus** — “Specification testing for structured LLM outputs” (accuracy/latency/throughput): https://github.com/lukecarr/litmus
- **JSONSchemaBench** — benchmark for structured outputs: https://github.com/guidance-ai/jsonschemabench

This validates that “structured output correctness” is a concrete pain.

### What’s missing / wedge opportunities
PromptPrecision’s wedge isn’t “fine-tune” (that’s crowded). It’s:
- Turn a task prompt into a **package**:
  - TaskSpec (schema + rubric)
  - Adapter (LoRA)
  - Repro lock
  - Eval report
- Focus on **measurable improvements** for a narrow task: schema-validity, per-field F1, latency.

If we can make this feel like a repeatable product (not a consultancy), it becomes a “prompt → model package” pipeline.

### Competitive risk
- Many platforms already offer: datasets, evals, prompt mgmt, fine-tuning integrations (e.g., Helicone mentions fine-tuning partners; Langfuse has datasets/evals).
- So PromptPrecision must be framed as a **packaging + measurement + specialization** product, not a generic fine-tuning tool.

### Cheap validation experiments (1 week)
1) Create a demo repo: “Prompt → adapter + report in 30 minutes” for a single structured extraction task.
2) Ask 10 practitioners what they’d pay for:
   - reliability guarantee? latency reduction? offline deployment? IP control?
3) Benchmark 2–3 small open models vs baseline prompts; publish the results.

### Build vs don’t build (preliminary)
- **Build if** we can show a repeatable 80/20 workflow that reliably improves structured output on small models and produces an audit-able report.
- **Don’t build** if it collapses into a services business or can’t beat prompt-only approaches.

Provisional recommendation: **BUILD (lean MVP)** focused on “structured-output reliability + eval report + packaging”.
