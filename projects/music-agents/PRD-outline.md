# Music Agents — PRD outline (recommended wedges)

## Recommended wedge order
1) **Playlisting / Outreach Agent** (fastest to revenue)
2) **Rights & Royalties Ops Agent** (higher-$, more defensible, longer sales)

---

## Wedge A: Playlisting / Outreach Agent (MVP)

### Problem
Indie teams waste time building a relevant lead list (research) and running consistent, compliant outreach with follow-ups—then lose track of what worked.

### ICP
Indie artists, managers, small labels (1–20 roster). Freelance promo/publicists.

### KPIs
Response rate, placement rate, time-to-first-response, qualified leads per track, deliverability/bounce rate, pipeline velocity.

### MVP promise (explicit)
- **Spotify discovery is research-only. MVP does not promise curator emails.**
- **MVP does not attempt to discover, infer, or enrich curator/owner email addresses from Spotify data.**
- Any contact email used for outreach must come from **user-provided import**, **first-party inbound**, or an **explicitly configured approved vendor**.

### Core flow (MVP)
Track intake → optional research (Spotify playlists list + rationale only) → **contact import (first-class)** → pitch drafting → send + follow-up → outcome tracking.

### Data sources & compliance constraints (MVP)
- Spotify Web API is used for metadata and playlist research only.
- Allowed sources list (v1):
  1) **User-provided manual/CSV import**
  2) **Approved enrichment vendors (NOT INCLUDED IN MVP unless explicitly named and enabled)**
  3) First-party inbound leads provided by the user
- User representation: users must attest they have the right/lawful basis to contact imported emails.
- Contact provenance (minimum fields):
  - source_type (import|inbound|vendor)
  - source_ref (import_file_id / inbound_message_id / vendor_batch_id)
  - collected_at
  - collected_by_user_id (if applicable)

### MVP features
- Campaign per track
- CRM: contacts, status, notes, history
- Pitch templates + AI draft + user review/approve
- Gmail integration + basic sequences (e.g., 2 follow-ups) + stop rules
- Dashboard (sent/replies/placements) + activity log

### Email compliance & deliverability (MVP requirements)
- Sending model: send from the user’s connected Gmail mailbox (OAuth).
- Mandatory:
  - Unsubscribe mechanism + suppression list (unsubscribe/bounce/manual)
  - Unsubscribe scope: **global per-organization suppression**
  - Unsubscribe implementation: List-Unsubscribe header + **one-click HTTPS unsubscribe endpoint**
  - Stop rules: stop on human reply, unsubscribe, bounce, manual stop
  - Throttling: per-mailbox daily caps + spacing + jitter; scheduling windows
  - Bounce detection + auto-suppress
  - Audit trail: who sent what, when, and template/version
  - List hygiene: syntax validation, duplicates, role-account warnings

### Compliance & privacy (MVP)
- Document lawful-basis stance (GDPR/UK GDPR considerations + CAN-SPAM basics).
- Default data minimization: store metadata/signals; bodies opt-in.

### Limits / SLOs (MVP defaults)
- Default send caps: 100/day per mailbox, 300/day per org (configurable)
- Reliability target: 99% of scheduled sequence steps executed within ≤10 minutes inside sending window (best-effort when auth/quota issues occur, surfaced in UI).

### Non-goals (MVP)
- Guaranteed placements
- Social DMs automation
- Automated placement detection

---

## Wedge B: Rights & Royalties Ops Agent

### Problem
Splits/contracts/identifiers inconsistent → delayed/missing royalties and disputes.

### MVP features
- Catalog intake (CSV + docs)
- Extraction + review UI
- Validation rules + issue tracker
- Checklist/tasks + reminders
- Export packages

## Open questions
- Gmail-only MVP acceptable?
- Unsubscribe one-click vs reply STOP (decision made above for MVP)
- Team/multi-org required day one?

---

## API wire contract (MVP, v1)
> Goal: a minimal, stable HTTP contract for contact import, campaigns, sequences, sends, events, and suppression/unsubscribe.

### Conventions
- Base path: `/v1`
- Auth: `Authorization: Bearer <session-or-api-token>`
- Multi-tenancy: server derives `org_id` from auth context; no cross-org access.
- Content types: `application/json` (uploads use multipart).
- IDs: opaque strings (ULID preferred), e.g. `con_01H...`
- Timestamps: RFC3339 UTC, e.g. `2026-02-22T19:44:00Z`

### Pagination (cursor)
- Request: `?page[limit]=50&page[cursor]=<opaque>`
- Response includes `next_cursor` (or `null`).

### Error envelope (all non-2xx)
```json
{
  "error": {
    "code": "validation_error | unauthorized | forbidden | not_found | conflict | rate_limited | provider_error | internal",
    "message": "Human-readable summary",
    "details": {"field": "..."},
    "request_id": "req_..."
  }
}
```

### Idempotency
- Supported for **POST** endpoints that create side effects: `POST /contacts/imports`, `POST /campaigns`, `POST /sequences`, `POST /sends`, `POST /suppressions`.
- Client may send header: `Idempotency-Key: <uuid-or-random-string>`.
- Semantics:
  - Same `{org_id, endpoint, idempotency_key}` returns the **original** response for 24h.
  - If the body differs for a reused key: return `409 conflict` (`error.code=conflict`).

### Minimal endpoints
#### Contacts: import + list
1) `POST /contacts/imports` (CSV upload)
- Multipart fields:
  - `file` (CSV)
  - `mapping` (JSON string)
  - `list_name` (optional)
- `mapping` schema:
```json
{
  "email": "Email",
  "first_name": "First Name",
  "last_name": "Last Name",
  "company": "Outlet",
  "tags": ["Tag1","Tag2"],
  "notes": "Notes"
}
```
- Response (202):
```json
{ "import": {"id":"imp_...","status":"queued","created_at":"..."} }
```

2) `GET /contacts` (list/search)
- Query: `?q=<text>` (matches email/name/company)
- Response (200):
```json
{
  "data": [
    {
      "id": "con_...",
      "email": "a@b.com",
      "first_name": "A",
      "last_name": "B",
      "company": "Blog",
      "tags": ["curator"],
      "created_at": "...",
      "provenance": {"source_type":"import","source_ref":"imp_...","collected_at":"..."}
    }
  ],
  "next_cursor": null
}
```

#### Campaigns
3) `POST /campaigns`
- Request:
```json
{ "name":"Track — Feb", "track_ref": {"artist":"...","title":"..."}, "mailbox_connection_id":"mbx_..." }
```
- Response (201):
```json
{ "campaign": {"id":"cam_...","status":"draft","created_at":"..."} }
```

4) `GET /campaigns` (list)
- Response: `{ "data": [...], "next_cursor": "..." }`

5) `POST /campaigns/{campaign_id}/prospects:bulk_add`
- Adds contacts to a campaign (creates Prospect rows).
- Request:
```json
{ "contact_ids": ["con_...","con_..."], "dedupe": true }
```
- Response (200):
```json
{ "added": 120, "skipped": 3 }
```

#### Sequences
6) `POST /sequences`
- Request:
```json
{
  "campaign_id":"cam_...",
  "name":"Default 2-followup",
  "steps":[
    {"kind":"initial","delay_minutes":0,"template": {"subject":"...","body":"..."}},
    {"kind":"followup","delay_minutes":2880,"template": {"subject":"Re: ...","body":"..."}}
  ],
  "stop_rules": {"on_reply":true,"on_bounce":true,"on_unsubscribe":true}
}
```
- Response (201): `{ "sequence": {"id":"seq_..."} }`

7) `GET /sequences?campaign_id=cam_...`

#### Sends (schedule/execute)
8) `POST /sends`
- Purpose: create (or enqueue) a single send attempt for a specific prospect + step.
- Request:
```json
{
  "campaign_id":"cam_...",
  "prospect_id":"pro_...",
  "sequence_id":"seq_...",
  "step_index": 0,
  "scheduled_for": "2026-02-23T09:10:00Z"
}
```
- Response (201):
```json
{
  "send": {
    "id":"snd_...",
    "status":"queued | sent | failed | skipped",
    "scheduled_for":"...",
    "provider": {"name":"gmail","message_id":null,"thread_id":null}
  }
}
```

#### Events (activity stream)
9) `GET /events`
- Query: `?campaign_id=cam_...&contact_id=con_...&types=send.sent,thread.reply,suppression.unsubscribed`
- Response:
```json
{
  "data": [
    {
      "id":"evt_...",
      "type":"send.sent | send.failed | thread.reply | thread.bounce | suppression.unsubscribed",
      "occurred_at":"...",
      "entity": {"kind":"send","id":"snd_..."},
      "payload": {"gmail_thread_id":"..."}
    }
  ],
  "next_cursor": null
}
```

#### Suppression & unsubscribe
10) `POST /suppressions`
- Request:
```json
{ "email":"a@b.com", "reason":"unsubscribe | bounce | manual", "source":"user | system | webhook" }
```
- Response (201): `{ "suppression": {"id":"sup_..."} }`

11) `GET /suppressions?email=a@b.com`
- Response (200):
```json
{ "data": [{"email":"a@b.com","reason":"unsubscribe","created_at":"..."}], "next_cursor": null }
```

12) `POST /public/unsubscribe`
- Auth: none. One-click endpoint.
- Request:
```json
{ "token":"unsub_opaque" }
```
- Response (200): `{ "status": "unsubscribed" }`

---

## Gmail OAuth scopes + reply/bounce detection (MVP contract)
### OAuth scopes (least privilege)
Request **only**:
- `https://www.googleapis.com/auth/gmail.send` (send email)
- `https://www.googleapis.com/auth/gmail.metadata` (read message/thread metadata + headers for reply/bounce detection; no bodies)

Notes:
- These scopes are sufficient for `users.messages.send` and for polling `users.history.list` + fetching messages in `format=metadata`.
- Do **not** request `gmail.modify` in MVP unless we decide to apply labels/mark read.

### Signal definitions (what counts as what)
- **Human reply**: an inbound message detected in the same Gmail thread as an outbound message where:
  - `From` is not the sender mailbox, AND
  - message is not classified as auto-response (below).
- **Bounce (delivery failure)**: an inbound message that indicates non-delivery of an outbound message, detected by either:
  - presence of typical DSN senders (`MAILER-DAEMON`, `postmaster`, `mailer-daemon@`) OR
  - `Auto-Submitted: auto-replied` + subject/body patterns like "Delivery Status Notification" / "Undelivered Mail Returned to Sender" / SMTP status codes.
- **Auto-response (NOT a human reply)**: messages with headers indicating automation:
  - `Auto-Submitted: auto-replied` or `auto-generated`
  - `X-Autoreply`, `X-Autorespond`, `Precedence: bulk|junk|list`
  - (Optional) Gmail category/label heuristics

### Triggers (stop rules)
On detecting:
- `thread.reply` → stop all future sequence steps for that prospect
- `thread.bounce` → add suppression(reason=`bounce`) and stop
- `suppression.unsubscribed` → add suppression(reason=`unsubscribe`) and stop

### Failure modes (must be visible in UI)
- `invalid_grant` / revoked token → mailbox status `disconnected`; scheduled sends pause.
- History checkpoint too old / `404` from history → run resync: scan last N days for threads for known outbound Message-IDs.
- Gmail quota / 429 → backoff, retry; do not drop events; surface degraded polling.
- User deleted thread / message → may miss reply; show "signals unavailable" for that thread.
