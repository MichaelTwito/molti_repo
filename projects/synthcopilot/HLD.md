# SynthCopilot — High-level design (Python)

## Architecture
- **Django + DRF**: API + admin + auth
- **Postgres**: users, jobs, patch specs, templates, entitlements
- **Celery + Redis**: async generation jobs
- **Object storage (S3-compatible)**: preset bundles + artifacts

## Core modules
1) **API/Web (Django/DRF)**
   - auth, billing/entitlements, job create/status, artifact download
2) **Generation orchestrator (Celery)**
   - prompt → patch intent → deterministic engine → variations → exporters
3) **Patch core (domain lib)**
   - internal `PatchSpec` model + validators
   - `MacroMap` (8 macro roles) + templates
4) **Exporters**
   - Vital preset exporter
   - Ableton mapping recipe generator

## Data model (suggested)
- User
- Subscription/Entitlement
- PresetJob(status, prompt, targets, seed, generator_version)
- PatchSpec(canonical JSON)
- PresetArtifact(type, storage_url, checksum)
- MacroTemplate(JSON definition)

## Preset generation approach (MVP)
- **LLM-as-planner** (optional) outputs structured intent (timbre/articulation/modulation)
- Deterministic synthesis engine maps intent → valid parameter ranges
- Variations = controlled deltas ("brighter", "darker", "more movement") stored explicitly

## Scalability notes
- Queue-based async generation; per-user quotas
- Cache identical prompt+template outputs (careful with privacy)
- Version everything (generator version, template version) for reproducibility

## Security
- Signed URLs for downloads
- Rate limiting + abuse controls
- Store artifacts + specs for re-download
