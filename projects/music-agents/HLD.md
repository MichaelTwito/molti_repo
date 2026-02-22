# Music Agents — High-level design (Python/Django)

## Architecture (shared core)
- **Django + DRF** API-first
- **Postgres** multi-tenant (org_id on all tables)
- **Celery + Redis** background jobs (sequences, enrichment, parsing)
- **S3-compatible storage** for uploads/attachments (contracts, statements)
- Search: start with Postgres FTS/trigram → OpenSearch later

## Common entities
- Organization (tenant)
- User (role)
- Artist
- Track/Release
- FileAsset
- ActivityEvent (append-only audit)

---

## Wedge A: outreach subsystem

### Core entities
- Campaign
- Prospect (campaign↔contact)
- Contact (email, name, provenance: import|vendor|inbound)
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
  - Reply detection: polling Gmail History API with robust checkpointing + resync path
- Scale path:
  - Gmail `watch` → Google Pub/Sub push notifications → worker fetches thread deltas

### Send correctness + deliverability
- Per-mailbox rate limiting (token bucket) + org-level caps
- Per-domain optional throttling
- Celery queues separated by concern: `send`, `enrich`, `parse`
- Exactly-once-ish semantics for send:
  - idempotency key per (mailbox, campaign, prospect, sequence_step)
  - retry-safe (no double-send)
- Stop rules enforced centrally (reply/unsubscribe/bounce/manual)
- List hygiene checks at ingestion (syntax, duplicates, role accounts)

### OAuth realities
- Minimize scopes; plan for Google OAuth verification depending on scopes.
- Re-auth UX + token refresh failure workflows.
- Per-mailbox health status (ok/degraded/auth_required).

### Data minimization (recommended defaults)
- Default to storing metadata + normalized signals (reply/unsubscribe/bounce) rather than full bodies.
- Full-body storage is opt-in with explicit retention controls.

---

## Wedge B: rights/royalties subsystem

### Entities
- Work vs Recording
- Party, Identifier
- Split, Contract
- ValidationIssue
- Task/checklist

### Workflows
- OCR/extraction pipeline → review/confirm UI → validation rules engine → checklist/tasks/reminders

---

## Security & privacy
- Encrypt OAuth tokens at rest (field-level + KMS where available)
- Least-privilege scopes; revoke/purge path
- Retention policy (message bodies/headers) + org deletion/export support
- Unsubscribe token + List-Unsubscribe support (mailto/https endpoint) + suppression plumbing
- Strong audit logs for sends/edits/exports

## Scalability
- composite indexes by (org_id, status, created_at)
- partition append-only tables later (ActivityEvent, OutboundMessage, SendAttempt)
- quota-aware scheduler: Gmail API quota budgeting per mailbox/org; backoff; dead-letter queue
- observability metrics: sends/day, bounce rate, reply rate, queue depth, step lag
