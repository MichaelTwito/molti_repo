# SynthCopilot — PRD outline (MVP)

## One-liner
**Text → Vital patch + 3 variations + 8 performance macros + Ableton mapping recipe**.

## Target (v1)
- Synth: **Vital-first**
- DAW: **Ableton Live-first**

## Definitions
- **PatchSpec**: versioned canonical JSON describing the patch (modules + modulation + macros).
- **Macro role**: one of 8 stable “knobs that matter” IDs.
- **Variation**: a constrained delta over the primary patch.

## MVP scope
A) Text → Patch (Vital-first)
- Output: primary patch + 3 variations + macros + “why” summary

B) Macro → MIDI mapping (Ableton-first)
- Output: deterministic mapping recipe (Rack macros + direct MIDI modes)

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
  - be reproducible by applying its diff to the base patch
  - preserve invariants requested by the job (mono, pluck, etc.)
  - pass validators

## Acceptance criteria (MVP)
### Determinism / reproducibility
- Given identical (prompt, tags, template_id, seed, generator_version) the produced PatchSpec is semantically identical.
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
  - `README.md`
- Every meta file includes `schema_version`.

### Job lifecycle
- `POST /jobs` returns `job_id` quickly.
- `GET /jobs/{id}` returns `queued|running|succeeded|failed`.

## Export strategy (strict MVP boundary)
- MVP guarantees bundle export only.
- Vital preset export is **not** an MVP deliverable; if implemented it is behind a feature flag and labeled experimental with tested Vital version.

## Open decisions
1) Canonical parameter path spec: adopt JSON Pointer for all references?
2) Diff format for variations: JSON Patch (RFC 6902)?
3) Ableton mapping: default to Rack macros or direct MIDI?
4) Retention/deletion requirements for prompts/artifacts.
