# PRD (outline) — PromptPrecision

## 1) Problem
Small teams want the cost/privacy benefits of small open models, but get unacceptable error/hallucination rates on their specific task.

## 2) Goal
Produce **task-specialized** model packages with **measurable improvement**.

## 3) Non-goals
- Competing with frontier models on general IQ.
- Arbitrary “prompt → pruned weights” with no eval proof.

## 4) Target users (MVP)
- Teams using open-weight models for a **single recurring task**.
- They can provide a small labeled dataset (or will accept a data-collection workflow).

## 5) Wedge use case (MVP)
### Support / Ops triage → JSON
Input: ticket/email text (+ optional metadata)
Output JSON:
- `category` (enum)
- `urgency` (low|med|high)
- `entities` (order_id, product, etc.)
- `next_action` (enum)

## 6) Product flow
1) Define task (schema + rubric)
2) Collect dataset (min 200–2,000 examples)
3) Baseline eval on base model
4) Train adapter (LoRA)
5) Re-eval + produce report
6) Export package (adapter + config + model card)

## 7) Acceptance criteria
- Report includes: accuracy/F1, JSON validity rate, hallucination proxy metric, latency/cost estimate.
- Export is reproducible with pinned versions.

## 8) Pricing hypothesis
- Per-project package + optional subscription for continuous improvement.

## 9) Open questions
- How we define “hallucination” for extraction tasks.
- Hosting vs on-prem only.

