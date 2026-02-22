# SynthCopilot — PRD outline (MVP)

## One-liner
**Text → Vital patch + 3 variations + 8 performance macros + Ableton mapping recipe**.

## Target (v1)
- Synth: **Vital-first**
- DAW: **Ableton Live-first**

## Personas
- Ableton producer (beginner→intermediate)
- Sound designer (intermediate→advanced)
- Content creator (preset packs)

## Jobs-to-be-done
- Generate a usable sound fast (e.g., “plucky techno bass, mono, snappy, slight grit”).
- Get **8 knobs that always make sense** (cutoff/env/drive/movement/etc.).

## MVP scope
A) **Text → Patch (Vital-first)**
- Input: text prompt + optional tags (genre, mono/poly, brightness, articulation)
- Output:
  - primary preset
  - 3 variations (each declares what changed)
  - 8 macro assignments (names + ranges)
  - short “why” summary

B) **Macro → MIDI mapping (Ableton-first)**
- Output: **mapping recipe** (step-by-step)
- (Later) export rack/templates if feasible

## Non-goals (MVP)
- Audio→patch, huge preset librarian, Serum support, hardware synth support, Eurorack planner

## Key requirements
- Deterministic structure + bounded randomness
- Validators: bounds, mono/poly consistency, avoid silent patches
- Macro templates by category (Bass/Lead/Pluck/Pad/FX)

## Export strategy
- Internal canonical patch JSON → Vital exporter → bundle (preset + README)
- Ableton: mapping recipe text first

## Pricing sketch
- Free: limited generations, no export
- Pro ($9–$15/mo): export + higher limits + saved history
- One-time packs ($49–$99): genre packs + templates

## Open decisions / questions
1) Confirm exact Vital preset format + legal/ToS comfort.
2) Fixed macro semantics across presets (recommended) vs per-patch.
3) Ableton: recipe-only vs rack templates in v1.
4) “Good patch” bar + reference presets to benchmark.
