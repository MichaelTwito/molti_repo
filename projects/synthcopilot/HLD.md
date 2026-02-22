# SynthCopilot — High-level design (Python)

## Architecture
- **Django + DRF**: API + admin + auth
- **Postgres**: users, jobs, patch specs, templates, entitlements
- **Celery + Redis**: async generation jobs
- **Object storage (S3-compatible)**: bundle artifacts

## Core modules
1) **API/Web (Django/DRF)**
   - auth, billing/entitlements, job create/status, artifact download
2) **Generation orchestrator (Celery)**
   - prompt → patch intent → deterministic engine → variations → exporters
3) **Patch core (domain lib)**
   - versioned `PatchSpec` schema + validators
   - macro roles + `MacroTemplate` schema
4) **Exporters**
   - bundle exporter (zip)
   - Vital preset exporter (optional, versioned)
   - Ableton mapping recipe generator

## PatchSpec (versioned JSON)
- `schema_version`, `engine_version`, `synth_target=vital`
- modules (osc/filter/env/lfo/fx/voicing)
- modulation matrix
- macros (8 roles) + assignments
- parameter addressing convention (internal paths mapped by exporter)

## MacroTemplate schema (minimal)
- id, name, category, version
- roles[8]: role_id, label, targets (parameter paths), range, constraints, conflicts
- engine may enable/disable modules as part of template defaults (decide per template)

## Preset generation approach (MVP)
- Optional **LLM-as-planner** outputs structured intent (validated against schema)
- Deterministic engine maps intent → bounded parameter ranges
- Variations = explicit deltas (store diff for explainability)

## Idempotency + artifact consistency
- Job key = hash(user_id, prompt, tags, template_id, seed, generator_version)
- If succeeded already, return existing artifacts
- Content-addressed artifact keys (checksum) + DB checksums

## Security
- Artifact downloads require authz (owner or explicit share token)
- Signed URLs with short TTL
- Treat any LLM output as untrusted: strict schema validation
- Rate limiting + per-user concurrency limits

## Scalability notes
- Queue-based async generation; per-user quotas
- Separate queues if exporters become heavy
- Version everything (generator, templates) for reproducibility
