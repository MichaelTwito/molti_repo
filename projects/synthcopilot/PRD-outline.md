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

## Auth / RBAC + access boundaries (MVP, normative)
### Actors
- **Authenticated user**: owns jobs they create.
- **Admin**: full read access for support/abuse handling (audited).
- **Anonymous via share token**: limited read-only access to a single shared job’s exported artifacts.

### Ownership + tenancy
- Every `job` has exactly one **owner** (`user_id`).
- Jobs, PatchSpecs, and artifacts are **tenant-isolated**: by default only the owner (or admin) can read them.

### Access rules (wire contract)
- **Create job**: requires authenticated user.
  - `POST /jobs` → 401 if not authenticated.
- **Read job**:
  - `GET /jobs/{id}` → 200 for owner/admin; 403 for non-owner; 404 if not found (do not leak existence).
- **Cancel job**:
  - `POST /jobs/{id}/cancel` → 200/202 for owner/admin; 403 for non-owner; 409 if not cancelable.
- **Download artifacts** (`bundle_url`, `manifest_url`):
  - Owner/admin can always access while retained.
  - Anonymous access ONLY via a valid share token (see below).

### Share tokens (read-only links)
- Scope: a share token is bound to **one job_id** (and its exported bundle).
- Permissions: **read-only**; grants access to:
  - bundle download (`bundle.zip`)
  - manifest (`meta/manifest.json`)
  - optional: a minimal public job view (`GET /share/{token}`) containing non-sensitive fields (status, synth_target, daw_target, created_at)
- Prohibitions: share token MUST NOT allow job cancel, regeneration, template listing, or access to other jobs.

Endpoints (normative):
- `POST /jobs/{id}/share-tokens`
  - Creates a new share token (owner/admin only).
  - Request: `{ "expires_in_days": 1..30 (optional; default 7) }`
  - Response (201): `{ "token": string, "share_url": string, "expires_at": RFC3339 }`
- `GET /jobs/{id}/share-tokens`
  - Lists active tokens (owner/admin only).
  - Response (200): `{ "tokens": [ {"token_id": string, "created_at": RFC3339, "expires_at": RFC3339, "revoked": boolean } ] }`
- `DELETE /jobs/{id}/share-tokens/{token_id}`
  - Revokes a token (owner/admin only). Response: 204.

Token presentation (normative):
- Share token MAY be presented either as:
  - query param `?share_token=...` on artifact URLs, OR
  - header `Authorization: ShareToken <token>`.

## API edge contracts (MVP, normative)
### Status codes (by category)
- 200: successful GET, cancel accepted/processed
- 201: resource created (e.g., share token)
- 202: accepted for async processing (optional for cancel)
- 400: malformed JSON / wrong types
- 401: authentication required/failed
- 403: authenticated but not permitted
- 404: not found (or intentionally indistinguishable from forbidden)
- 409: conflict (e.g., cancel not allowed in current state, idempotency conflict)
- 410: expired or revoked share token (when using `/share/{token}` style endpoints)
- 413: payload too large (prompt/tags)
- 422: semantic validation failed (PatchSpec / macro / variation constraints)
- 429: rate limit exceeded
- 5xx: server failures

### Error envelope (all non-2xx)
`{ "error": { "code": string, "message": string, "retryable": boolean, "details"?: object } }`

### Validation error details (422)
- `error.code = "VALIDATION_ERROR"`
- `error.details` shape (normative):
  - `{ "violations": [ { "path": string (JSON Pointer), "rule": string, "message": string, "expected"?: any, "actual"?: any } ] }`

### Rate limits (MVP defaults)
- Authenticated users:
  - `POST /jobs`: **10 requests/min/user** (burst 3)
  - `GET /jobs/{id}`: **120 requests/min/user**
- Anonymous (share token):
  - artifact downloads: **60 requests/min/token**
- 429 responses MUST include `Retry-After` (seconds) and may include `X-RateLimit-*` headers.

## Limits (MVP defaults)
- Max concurrent jobs/user: 2
- Max bundle.zip size: 5MB
- Max modulation routes: 64
- Max macro targets per role: 8

