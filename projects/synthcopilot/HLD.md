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

#### PatchSpec v1 — minimum required structure (MVP)
- `modules.osc` MUST contain at least 1 oscillator object at index 0.
- `modules.env` MUST contain at least 1 amp envelope at index 0.
- `modules.voicing` MUST exist and include `mode` (mono|poly) and `voices` (int).

#### PatchSpec v1 — canonicalization + determinism rules (normative)
- Numeric quantization: continuous params are stored rounded to 6 fractional digits after clamping.
- Clamping: any generated value MUST be clamped to the parameter’s allowed range before serialization.
- Array order: arrays are semantically ordered and MUST NOT be re-ordered by generators or validators.
- Object keys: serializers SHOULD emit stable key ordering (lexicographic) to support reproducible artifacts.
- Defaults: PatchSpec MUST be fully explicit for any param referenced by macros/modulation/variations.

### Parameter addressing
- All parameters referenced by macros/modulation use **JSON Pointer (RFC 6901)** paths into PatchSpec.
  - Example: `/modules/osc/0/wavetable/position`

### Variation diff
- Variations use **RFC 6902 JSON Patch**.
- `meta/variations_diff.json` stores: `{ schema_version, base_schema_version, variations:[{id,type,patch:[...]}] }`.

#### Variation JSON Patch rules (MVP)
- Allowed ops: `replace` only.
- Forbidden ops: `remove`, `move`, `copy`, `test`, and `add` (until explicitly enabled).
- Each variation MUST apply cleanly to the base PatchSpec (no missing paths).
- Validators run after applying patch:
  - non-silent
  - parameter range compliance
  - requested invariants (mono/poly, pluck constraints, etc.)

## MacroTemplate schema (v1)
- Top-level: `schema_version: "1.0"`, id, name, category, version
- roles[8]:
  - role_id (stable enum)
  - label
  - default (0..1)
  - behavior: curve (linear|log|exp), bipolar, steps
  - targets: [{ path, amount, min, max, curve, weight }]
  - constraints: requires/forbids/invariants (mono_safe, non_silent)
  - conflicts: [role_id]

### MacroTemplate schema (v1) — normative constraints
- `roles` MUST have length exactly 8 and include each role_id exactly once.
- role_id enum:
  - TONE_BRIGHTNESS, AMP_PUNCH, DRIVE, MOVEMENT, SPACE, WIDTH, CHARACTER, FX
- `default`, `min`, `max` are macro knob positions in [0..1] with `min <= default <= max`.
- Each targets[].path MUST resolve to a valid JSON Pointer in PatchSpec.

## Bundle manifest (normative)
`meta/manifest.json`:
- schema_version: "1.0"
- files: [{ path, sha256, bytes }]
- bundle_sha256

## Generation approach (MVP)
- Optional LLM-as-planner returns structured intent (strictly validated)
- Deterministic engine maps intent → bounded parameter ranges
- Variations = explicit JSON Patch deltas

## Idempotency + artifact consistency
- Job key = hash(user_id, prompt, tags, template_id, seed, generator_version)
- If succeeded already, return existing artifacts
- Content-addressed artifact keys (checksum) + DB checksums

## Security + compliance (MVP)
- Prompt retention: 30 days by default; user deletion within 24h
- Share tokens: random 128-bit, revocable, default expiry 7 days
- Zip creation: sanitize filenames; prevent zip-slip; limit bundle size

## Worker limits
- Celery soft timeout 45s + hard timeout 60s
- Memory limits per worker; max retries with backoff
- Cancellation supported for queued/running jobs

## API wire contract (minimal)
- `POST /jobs` accepts request shape defined in PRD.
- Error envelope:
  - `{ error: { code, message, retryable, details? } }`

## Limits (MVP defaults)
- Max prompt length: 4000 chars
- Max tags: 20
- Max concurrent jobs/user: 2
- Max bundle.zip size: 5MB
