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

## Auth / RBAC + access boundaries (MVP, normative)
### Data model (conceptual)
- `Job(user_id, ...)` is the primary tenant boundary.
- `Artifact(job_id, storage_key, sha256, bytes, ...)` inherits access from Job.
- `ShareToken(job_id, token_id, token_hash, created_at, expires_at, revoked_at, created_by)`.
  - Store **only a hash** of the token for lookup; treat the raw token as a bearer secret.

### Authorization rules (normative)
- **Owner** (job.user_id) and **admin** MAY:
  - create/read/cancel jobs
  - read PatchSpec + manifest + bundle
  - create/list/revoke share tokens for that job
- **Other authenticated users** MUST receive 404 (preferred) or 403 when accessing jobs they do not own.
- **Anonymous** MAY ONLY access artifacts if presenting a valid, unexpired, unrevoked share token scoped to that job.

### Share token verification (normative)
- Token is opaque random ≥128 bits, URL-safe base64.
- Verification steps:
  1) hash token → lookup by `token_hash`
  2) confirm not revoked, not expired
  3) confirm requested `job_id` matches token’s `job_id`
- Revocation MUST take effect immediately.

## PatchSpec v1 — minimal module bounds/shapes for validators (normative)
This section defines the **minimum required structure** and **bounds** needed for schema + semantic validators. Generators MAY emit more fields, but MUST NOT violate these constraints.

### Top-level
- `schema_version`: string, MUST equal `"1.0"`
- `engine_version`: string (non-empty)
- `synth_target`: string, MUST equal `"vital"`
- `modules`: object (required)
- `modulation`: object (required)
- `macros`: array (required)

### modules (required object)
Required keys:
- `osc`: array length **1..3**
- `env`: array length **1..4**
- `voicing`: object
Optional keys:
- `filter`: array length **0..2**
- `lfo`: array length **0..8**
- `fx`: object (see below)

#### modules.voicing (required)
- `mode`: enum `mono | poly`
- `voices`: int
  - if `mode=mono` → MUST be 1
  - if `mode=poly` → MUST be 1..16
- Optional: `glide_time`: number (seconds) 0..10

#### modules.osc[i] (i=0..)
Required:
- `enabled`: boolean
- `level`: number 0..1
- `transpose_semitones`: int -48..48
Optional (if present, must validate type/bounds):
- `pan`: number -1..1
- `wavetable`: object with:
  - `position`: number 0..1

#### modules.env[i]
- env[0] is the **amp envelope** (normative convention).
Required fields (all numbers in seconds unless noted):
- `attack`: 0..20
- `decay`: 0..20
- `sustain`: 0..1
- `release`: 0..20
Optional:
- `curve`: number -1..1

#### modules.filter[i] (optional)
Required:
- `enabled`: boolean
- `type`: string (non-empty)
- `cutoff_hz`: number 10..22050
- `resonance`: number 0..1

#### modules.lfo[i] (optional)
Required:
- `enabled`: boolean
- `rate_hz`: number 0..50
- `depth`: number 0..1
Optional:
- `sync`: boolean

#### modules.fx (optional)
If present:
- MUST contain `chain`: array of fx unit objects length 0..16.
- Each fx unit MUST include:
  - `type`: string (non-empty)
  - `enabled`: boolean
  - `params`: object (values must be number|boolean|string; numbers MUST be finite)
- Validators SHOULD enforce `type` is from an allowlist for the target synth version when available.

### modulation (required)
- `routes`: array length 0..64
Each route:
- `source`: object `{ kind: string, id: string }` (non-empty)
- `target`: object `{ path: string (JSON Pointer) }`
- `amount`: number -1..1
Optional:
- `polarity`: enum `unipolar | bipolar`
- `curve`: enum `linear | exp | log`

### macros (required)
- MUST be an array length **exactly 8**.
- Each entry MUST include:
  - `role_id`: enum of the 8 stable roles
  - `label`: string (1..32)
  - `default`, `min`, `max`: numbers in 0..1 with `min <= default <= max`
  - `targets`: array length 1..8
- Each `targets[]` MUST include:
  - `path`: string (JSON Pointer) that resolves to a numeric field in PatchSpec
  - `amount`: number -1..1
Optional:
- `curve`: enum `linear | exp | log`

### JSON Pointer resolution + bounds (normative)
- Any `path` referenced by modulation/macros/variations MUST resolve against the base PatchSpec.
- Validators MUST fail if:
  - pointer does not resolve
  - resolved value is not numeric (for macro/mod amount application)
  - applying a variation patch results in out-of-bounds values per this section

## API wire contract (expanded edges)
### Error envelope (normative)
- `{ "error": { "code": string, "message": string, "retryable": boolean, "details"?: object } }`

### Error codes (normative)
- `AUTH_REQUIRED` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `RATE_LIMITED` (429)
- `PAYLOAD_TOO_LARGE` (413)
- `CONFLICT` (409)
- `VALIDATION_ERROR` (422) — semantic/schema validation failures
- `GENERATION_FAILED` (500/502) — worker failure

### Validation failures (422)
`error.details` MUST be:
- `{ "violations": [ { "path": string, "rule": string, "message": string, "expected"?: any, "actual"?: any } ] }`

### Rate limiting (MVP defaults)
- Enforce per-user and per-token limits at API gateway or DRF throttle:
  - `POST /jobs`: 10/min/user (burst 3)
  - `GET /jobs/*`: 120/min/user
  - Anonymous share token downloads: 60/min/token
- 429 MUST include `Retry-After` (seconds). SHOULD include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

## Limits (MVP defaults)
- Max prompt length: 4000 chars
- Max tags: 20
- Max concurrent jobs/user: 2
- Max bundle.zip size: 5MB
