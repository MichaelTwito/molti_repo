# HLD — PromptPrecision (Python-first)

## Architecture (MVP)
- CLI-first + optionally a small Django web UI later.
- Training stack: HuggingFace Transformers + PEFT (LoRA).
- Eval stack: custom harness + JSON schema validation + task metrics.

## Core components
1) **TaskSpec** (YAML/JSON)
   - base_model_id
   - IO schema (JSON Schema)
   - label enums
   - evaluation rubric

2) **Dataset**
   - JSONL: `{input_text, output_json, meta}`

3) **Trainer**
   - LoRA config (rank/alpha/dropout)
   - deterministic seeds
   - produces adapter artifact

4) **Evaluator**
   - JSON validity (schema)
   - exact-match / F1 on fields
   - confusion matrix for enums
   - latency benchmarks (tokens/sec) on target hardware profile

5) **Packager**
   - `adapter/` weights
   - `task_spec.json`
   - `eval_report.md`
   - `repro.lock` (pip/conda versions)

## Path to pruning (v2+)
- Collect activation stats on eval set
- Structured pruning candidate units:
  - attention heads
  - MLP channels
- Only ship if it improves: quality AND latency/VRAM

## Risks
- Data scarcity → need a data collection UX.
- Overfitting → must hold out test set.
- Benchmark gaming → define robust rubric.

