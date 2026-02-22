# SynthCopilot — PRD outline (MVP)

## One-liner
**Text → Vital patch + 3 variations + 8 performance macros + Ableton mapping recipe**.

## Target (v1)
- Synth: **Vital-first**
- DAW: **Ableton Live-first**

## Definitions
- **PatchSpec**: versioned canonical JSON describing the patch (modules + modulation + macros).
- **Macro role**: one of 8 stable “knobs that matter” IDs (not arbitrary names).
- **Variation**: a constrained delta over the primary patch that preserves core constraints.

## Personas
- Ableton producer (beginner→intermediate)
- Sound designer (intermediate→advanced)
- Content creator (preset packs)

## Jobs-to-be-done
- Generate a usable sound fast (e.g., “plucky techno bass, mono, snappy, slight grit”).
- Get **8 knobs that always make sense**.

## MVP scope
A) **Text → Patch (Vital-first)**
- Input: prompt + optional tags (genre, mono/poly, brightness, articulation)
- Output:
  - primary patch
  - 3 variations (each declares what changed)
  - macros (8 roles with labels + ranges)
  - short “why” summary

B) **Macro → MIDI mapping (Ableton-first)**
- Output: deterministic **mapping recipe** (text)
  - Mode A: Instrument Rack macros
  - Mode B: direct MIDI mapping
- (Later) rack/templates export if feasible

## Macro roles (recommended stable set)
1) TONE / BRIGHTNESS
2) ENV AMOUNT / PUNCH
3) DRIVE
4) MOVEMENT (LFO depth)
5) SPACE (reverb/delay mix)
6) WIDTH
7) CHARACTER (FM/wavetable pos)
8) FX (chorus/phaser/etc)

## Variation contract (MVP)
- Fixed variation types:
  1) Brighter
  2) Darker
  3) More movement
- Each variation must:
  - list changed parameters (diff)
  - preserve constraints (e.g., still mono pluck bass)
  - pass validators

## Acceptance criteria (MVP)
### Patch validity
- Patch is not silent by default (amp env + output levels valid).
- No out-of-range parameters; mono/poly settings match intent.
- Macros reference existing parameters and have safe ranges.

### Job lifecycle
- `POST /jobs` returns `job_id` quickly.
- `GET /jobs/{id}` returns `queued|running|succeeded|failed`.
- On success returns artifacts for primary + variations + PatchSpec + macro list + mapping recipe.

### Mapping recipe
- Includes exact steps and parameter names users can find in Vital/Ableton.

## Export strategy (MVP-safe default)
- Always export a **bundle.zip** with:
  - `meta/patchspec.json`, `meta/macros.json`, `meta/variations_diff.json`, `meta/generation.json`
  - `README.md` (mapping recipe)
- Vital preset file export is **optional v1** until format/legal is confirmed.

## Pricing sketch
- Free: limited generations, no export
- Pro ($9–$15/mo): export + higher limits + saved history
- One-time packs ($49–$99): genre packs + templates

## Open decisions / questions
1) Vital export: exact preset file format + ToS/legal comfort.
2) Validation: parameter-only vs any audio-based checks.
3) Ableton: recipe-only in v1 vs shipping rack templates.
4) Reproducibility promise: deterministic by (prompt,tags,template,seed,generator_version).
