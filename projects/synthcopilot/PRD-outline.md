# SynthCopilot — PRD outline (MVP)

## One-liner
**Text → Vital patch + 3 variations + 8 performance macros + Ableton mapping recipe**.

## Target (v1)
- Synth: **Vital-first**
- DAW: **Ableton Live-first**

## Closed decisions (normative)
1) **Canonical parameter path spec**: JSON Pointer (RFC 6901) for all parameter references inside PatchSpec and MacroTemplate.
2) **Diff format for variations**: JSON Patch (RFC 6902). Variations are stored as patches against the base PatchSpec.
3) **Ableton mapping default**: Rack Macros mapping recipe is default. Direct MIDI mapping is optional and marked experimental.
4) **Retention/deletion (MVP)**:
   - Default retention: 30 days for prompts + generated artifacts (PatchSpec + bundle).
   - User deletion endpoint: deletes prompts + PatchSpec + bundles within 24h.
   - Share links default expiry: 7 days (configurable).

## Definitions
- **PatchSpec**: versioned canonical JSON describing the patch (modules + modulation + macros).
- **Macro role**: one of 8 stable “knobs that matter” IDs.
- **Variation**: a constrained delta over the primary patch.

## MVP scope
A) Text → Patch (Vital-first)
- Output: primary patch + 3 variations + macros + “why” summary

B) Macro → MIDI mapping (Ableton-first)
- Output: deterministic mapping recipe (Rack macros default + direct MIDI optional)

## Macro roles (stable IDs)
1) TONE_BRIGHTNESS
2) AMP_PUNCH
3) DRIVE
4) MOVEMENT
5) SPACE
6) WIDTH
7) CHARACTER
8) FX

## Variation contract (MVP)
- Variation types: Brighter, Darker, More movement
- Each variation must:
  - be reproducible by applying its JSON Patch to the base PatchSpec
  - preserve invariants requested by the job (mono, pluck, etc.)
  - pass validators

## Acceptance criteria (MVP)
### Determinism / reproducibility
- Given identical (prompt, tags, template_id, seed, generator_version), the produced PatchSpec is semantically identical.
- Bundle includes `meta/generation.json` with seed + versions.

### Patch validity
- Patch is not silent by default.
- No out-of-range parameters; mono/poly settings match intent.

### Macro quality
- Each macro role maps to at least one valid parameter path.
- Macro min/max positions keep patch non-silent and within safe output bounds.
- WIDTH role is mono-safe when mono is requested.

### Export bundle contract
- `bundle.zip` always contains:
  - `meta/patchspec.json`
  - `meta/macros.json`
  - `meta/variations_diff.json`
  - `meta/generation.json`
  - `meta/manifest.json`
  - `README.md`
- Every `meta/*.json` includes `schema_version`.

## Export strategy (strict MVP boundary)
- MVP guarantees **bundle export only**.
- Vital preset export is **not** an MVP deliverable; if implemented it is behind a feature flag and labeled experimental with tested Vital version.

## Job API contract (MVP, normative)
### POST /jobs
Request JSON:
- prompt: string (1..4000 chars)
- tags: string[] (0..20, each 1..64 chars)
- template_id: string
- seed: int (optional; if omitted server generates and returns it)
- synth_target: "vital"
- daw_target: "ableton"
- options: { mono?: boolean, poly_voices?: int, style?: string }

Response JSON (200):
- job_id: string
- status: queued|running|succeeded|failed
- deduped: boolean
- seed: int
- generator_version: string

### GET /jobs/{id}
Response JSON (200):
- job_id, status
- progress: 0..1 (optional)
- error: { code, message } (only if failed)
- artifacts: { bundle_url, manifest_url } (only if succeeded)

### POST /jobs/{id}/cancel
- transitions queued|running → canceled (best effort).

## Limits (MVP defaults)
- Max concurrent jobs/user: 2
- Max bundle.zip size: 5MB
- Max modulation routes: 64
- Max macro targets per role: 8

