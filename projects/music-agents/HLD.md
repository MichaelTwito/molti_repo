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

OAuth scopes (MVP):
- Document exact scopes requested (send + minimum read scope needed for reply/bounce signals).
- Plan for Google OAuth verification if needed.

History polling contract:
- Persist `history_id_checkpoint` per mailbox.
- If checkpoint too old/invalid: resync by scanning last N days and rebuilding thread mappings.

Watch contract (V1+):
- Per-org isolated subscription; scheduled renewals; handle expiry and invalid_grant.

Thread correlation:
- Map internal MessageThread ↔ Gmail threadId; store Message-ID and References headers where available.

### Unsubscribe / suppression
- Unsubscribe is org-global by default.
- One-click HTTPS endpoint + List-Unsubscribe headers.
- SuppressionEntry retained long-term for compliance.

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
