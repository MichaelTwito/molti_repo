# Music Agents — High-level design (Python/Django)

## Architecture (shared core)
- Django + DRF API-first
- Postgres multi-tenant (org_id on all tables)
- Celery + Redis background jobs (sequences, enrichment, parsing)
- S3-compatible storage for uploads/attachments

## RBAC (MVP)
- OrgAdmin: manage org settings, suppression, export/delete, enable vendors, manage members
- Sender: connect mailbox, create campaigns, send sequences
- Viewer: read-only analytics/CRM

Mailbox rules:
- A mailbox can only be used by users with Sender role in the same org.
- OrgAdmin can revoke MailboxConnection; sends stop immediately.

## Common entities
- Organization
- User
- Artist
- Track/Release
- FileAsset
- ActivityEvent (append-only audit)

---

## Outreach subsystem (Wedge A)

### Core entities
- Campaign
- Contact (email, name, provenance: import|inbound|vendor)
- Prospect (campaign↔contact)
- MailboxConnection (OAuth identity, provider, email, status)
- MessageThread (external thread IDs)
- OutboundMessage (subject/body/template version)
- SequenceStep (scheduled follow-ups)
- Outcome
- SuppressionEntry (email, reason: unsubscribe|bounce|manual)
- MessageSendAttempt (idempotency key, provider msg id, error category)

### Gmail integration
- MVP (beta):
  - Send: Gmail API `users.messages.send`
  - Reply/bounce detection: polling Gmail History API with checkpointing + resync path
- Scale path:
  - Gmail `watch` → Google Pub/Sub push notifications → worker fetches thread deltas

OAuth scopes (MVP, least privilege):
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.metadata`

Rationale:
- `gmail.metadata` permits reading labels + headers (via `format=metadata`) without message bodies, sufficient for correlation + reply/bounce signals.
- `users.watch` accepts `gmail.metadata` (or `gmail.readonly`/`gmail.modify`), so we can scale to push without expanding scopes.

History polling contract:
- Persist `history_id_checkpoint` per mailbox.
- Poll `users.history.list` with `startHistoryId=checkpoint`.
- Request `historyTypes`: at minimum `messageAdded` and `labelAdded` (if used).
- For each new message ID, fetch via `users.messages.get(format=metadata, metadataHeaders=[From,To,Cc,Date,Message-Id,In-Reply-To,References,Subject,Auto-Submitted,Precedence,X-Autoreply])`.
- Correlate to outbound:
  - Prefer `threadId` match to known outbound Gmail `threadId`.
  - Fallback: match `In-Reply-To` / `References` against stored outbound `Message-Id`.
- Classify event types:
  - `thread.reply` when inbound is from a non-sender and not auto-response.
  - `thread.bounce` when inbound resembles DSN/non-delivery (MAILER-DAEMON/postmaster) or strong DSN headers/patterns.
  - `thread.autoresponse` when `Auto-Submitted`/`Precedence`/`X-Autoreply` indicate automation (does NOT stop sequence unless configured).
- Update checkpoint only after durable processing.

Resync path (checkpoint invalid/too old):
- If Gmail returns `404` for history or indicates invalid startHistoryId:
  - Scan last N days (config: 7–14) of messages for each known outbound threadId/Message-Id.
  - Rebuild internal thread mappings and emit any missed reply/bounce events.
  - Record resync run in ActivityEvent.

Watch contract (V1+):
- Per-org isolated subscription; scheduled renewals; handle expiry and invalid_grant.

Thread correlation:
- Map internal MessageThread ↔ Gmail threadId; store Message-ID and References headers where available.

### Unsubscribe / suppression
- Unsubscribe is org-global by default.
- One-click HTTPS endpoint + List-Unsubscribe headers.
- SuppressionEntry retained long-term for compliance.

Unsubscribe mechanics:
- Outbound messages include:
  - `List-Unsubscribe: <https://api.example.com/v1/public/unsubscribe?token=...>`
  - `List-Unsubscribe-Post: List-Unsubscribe=One-Click`
- Unsubscribe token is an HMAC-signed, opaque blob encoding `{org_id, email, mailbox_connection_id?, campaign_id?, issued_at}` with an expiry (e.g., 180 days). Even if expired, UI may still allow manual suppression.

### Retention defaults (MVP)
- OutboundMessage bodies: not stored by default; if enabled, retain 90 days.
- Message metadata (thread IDs, timestamps, outcome signals): 12 months.
- ActivityEvent audit log: 24 months.
- SuppressionEntry: retained indefinitely.
- Org deletion: hard-delete within 30 days (best effort immediate; backups SLA documented separately).

### Send correctness + deliverability
- Per-mailbox rate limiting + org caps; optional per-domain throttling
- Queues separated: send/enrich/parse
- Exactly-once-ish send semantics via idempotency key per step
- Stop rules enforced centrally
- List hygiene: syntax validation, duplicates, role accounts

Idempotency (server-side):
- Accept `Idempotency-Key` for side-effecting POSTs (import, create campaign/sequence, schedule send, create suppression).
- Store `{org_id, endpoint, key, request_hash, response_blob, created_at}`.
- If key reused with same hash within TTL (24h) → return stored response.
- If reused with different hash → `409 conflict`.

Pagination (API):
- Cursor pagination across list endpoints (`/contacts`, `/campaigns`, `/events`, `/suppressions`).
- Stable ordering: `created_at` then `id`.

Error envelope (API):
```json
{
  "error": {
    "code": "validation_error | unauthorized | forbidden | not_found | conflict | rate_limited | provider_error | internal",
    "message": "...",
    "details": {},
    "request_id": "req_..."
  }
}
```

### API surface (v1, minimal)
Resource/endpoint list (MVP):
- Contacts
  - `POST /v1/contacts/imports` (multipart CSV → async import job)
  - `GET /v1/contacts` (cursor list + `q=` search)
- Campaigns
  - `POST /v1/campaigns`
  - `GET /v1/campaigns`
  - `POST /v1/campaigns/{id}/prospects:bulk_add`
- Sequences
  - `POST /v1/sequences` (includes steps)
  - `GET /v1/sequences?campaign_id=...`
- Sends
  - `POST /v1/sends` (enqueue one send attempt for `{prospect, step}`)
- Events (activity stream)
  - `GET /v1/events` (filterable + cursor)
- Suppression/unsubscribe
  - `POST /v1/suppressions` (manual/system create)
  - `GET /v1/suppressions` (list + optional `email=` filter)
  - `POST /v1/public/unsubscribe` (one-click)

Implementation notes:
- Prefer append-only ActivityEvent rows for state transitions; derive dashboards from events + current state tables.
- Use server-generated tokens for public endpoints (unsubscribe) and never expose internal IDs.

### Observability / SLOs
- Default caps: 100/day per mailbox, 300/day per org (configurable)
- Target: 99% scheduled sends within 10 minutes inside sending window (best-effort when quota/auth issues)

---

## Rights/Royalties subsystem (Wedge B)
- Work vs Recording
- Party, Identifier
- Split, Contract
- ValidationIssue
- Task/checklist

Workflows: OCR/extraction → review UI → validation → tasks/reminders.

## Security & privacy
- Encrypt OAuth tokens at rest; least privilege; revoke/purge path
- Data minimization defaults; bodies opt-in
- Audit logs for sends/edits/exports
