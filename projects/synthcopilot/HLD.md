# SynthCopilot — High-level design (Python)

## Architecture
- **Django + DRF**: API + admin + auth
- **Postgres**: users, jobs, patch specs, templates, entitlements
- **Celery + Redis**: async generation jobs
- **Object storage (S3-compatible)**: bundle artifacts

## Schemas (normative)
### PatchSpec v1
Required top-level fields:
- `schema_version`: "1.0"
- `engine_version`: string
- `synth_target`: "vital"
- `modules`: object (osc[], filter[], env[], lfo[], fx[], voicing)
- `modulation`: { routes: [ { source, target, amount, polarity, curve } ] }
- `macros`: [ { role_id, label, default, min, max, targets:[{path, amount, curve}] } ]

### Parameter addressing
- All parameters referenced by macros/modulation use **JSON Pointer (RFC 6901)** paths into PatchSpec.
  - Example: `/modules/osc/0/wavetable/position`

### Variation diff
- Variations use **RFC 6902 JSON Patch**.
- `meta/variations_diff.json` stores: `{ base_schema_version, variations:[{id,type,patch:[...]}] }`.

## MacroTemplate schema (v1)
- id, name, category, version
- roles[8]:
  - role_id (stable enum)
  - label
  - default (0..1)
  - behavior: curve (linear|log|exp), bipolar, steps
  - targets: [{ path, amount, min, max, curve, weight }]
  - constraints: requires/forbids/invariants (mono_safe, non_silent)
  - conflicts: [role_id]

## Generation approach (MVP)
- Optional LLM-as-planner returns structured intent (strictly validated)
- Deterministic engine maps intent → bounded parameter ranges
- Variations = explicit JSON Patch deltas

## Idempotency + artifact consistency
- Job key = hash(user_id, prompt, tags, template_id, seed, generator_version)
- If succeeded already, return existing artifacts
- Content-addressed artifact keys (checksum) + DB checksums

## Security + compliance (MVP)
- Prompt retention policy (default X days) + user deletion endpoint
- Share tokens: random 128-bit, revocable, optional expiry
- Zip creation: sanitize filenames; prevent zip-slip; limit bundle size

## Worker limits
- Celery soft timeout (e.g., 45s) + hard timeout (e.g., 60s)
- Memory limits per worker; max retries with backoff
- Cancellation: user can cancel queued/running job; tasks check cancellation flag

## Scalability notes
- Rate limiting + per-user concurrency limits
- Queue separation if needed (`generate`, `export`)
- Version everything (engine/templates) for reproducibility
