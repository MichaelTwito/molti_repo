# Decision Memos (Internal) — 2026-02-23

Goal: internal **build / don’t build** decision support.
Scope: English-only. Sources: HN (Algolia), GitHub, targeted web fetch. (X excluded due to credits.)

---

## Memo 1 — AOD (Agent Observability Dashboard)

### Decision framing
We will **only build** if we can carve out a defensible wedge that is not “another tracing UI”.

### Market reality (what’s already strong)
The space is crowded and active:
- Langfuse (OSS LLM engineering platform): https://github.com/langfuse/langfuse
- Helicone (gateway + observability + sessions): https://github.com/Helicone/helicone
- OpenLLMetry (OTel-based instrumentation): https://github.com/traceloop/openllmetry
- OpenLIT (OTel-native platform): https://github.com/openlit/openlit
- “OTel should be the standard” narrative is widely repeated: https://signoz.io/blog/llm-observability-opentelemetry/

Implication: a generic “observability dashboard” is unlikely to win.

### Proposed wedge (what we build that others don’t)
**Agent Run Governance & Audit** on top of traces:
- run/step contracts
- approvals / gates (pre/post conditions)
- policy evaluation
- redaction rules
- immutable audit + retention invariants
- exportable compliance artifacts

Positioning line: **“Govern and audit agent actions in production.”**

### ICP hypotheses (who would pay)
- Teams deploying agentic workflows that touch **customer data**, **financial actions**, or **operational permissions**.
- Regulated-ish environments or security-conscious orgs.

### Build plan (lean MVP)
Deliver a governance-first minimal product:
1) Minimal event schema + SDK (run/step/finish)
2) Policy engine (simple rules) + approvals (manual)
3) Audit log + redaction layer
4) Basic UI: run timeline + policy decisions + approvals

### Kill criteria (stop if true)
Stop after 7–10 days if we cannot get:
- **3 design partners** who agree this is their top-3 pain, AND
- at least **one** concrete workflow where approvals/audit is a blocker today.

### Next 10 conversations (targets)
- Agentic support / ops teams (customer support automation)
- Security/compliance engineers supporting AI features
- Platform engineers responsible for observability + governance

### Recommendation
**BUILD — conditional.** Proceed only if design partners confirm governance/audit as a must-have and not “nice-to-have”.

---

## Memo 2 — PromptPrecision

### Decision framing
We build only if we can productize this into a repeatable pipeline (not bespoke consulting).

### Problem signals
Structured outputs and JSON schema reliability are real pain:
- Litmus: spec-testing structured LLM outputs (accuracy/latency/throughput): https://github.com/lukecarr/litmus
- JSONSchemaBench: structured output benchmark: https://github.com/guidance-ai/jsonschemabench

Implication: people care about measurable correctness, not just “prompt vibes”.

### Proposed wedge
“Prompt → **Specialized small open model package** + **eval report**”
- TaskSpec (schema + rubric)
- dataset format
- LoRA adapter
- reproducible lock
- benchmark report (schema validity, per-field F1, latency)

Positioning line: **“Turn a prompt into a measurable small-model upgrade.”**

### ICP hypotheses
- Teams that need:
  - offline/edge/self-host constraints
  - IP control (open weights + adapters)
  - predictable structured extraction at scale

### Build plan (lean MVP)
1) One demo task (structured extraction) with a clean eval harness
2) 2–3 base small models + 1 adapter training path
3) Output bundle: adapter + spec + report

### Kill criteria (stop if true)
Stop after 7–10 days if we cannot show:
- consistent improvement vs prompt-only baseline on a held-out set, OR
- a workflow that feels repeatable across 3 different tasks.

### Next 10 conversations (targets)
- Engineers running extraction/ETL-like LLM workflows
- Teams doing document processing with strict schemas
- Folks who already tried fine-tuning and got burned by eval complexity

### Recommendation
**BUILD — lean MVP.** The wedge is credible; the key risk is collapsing into a services business.
