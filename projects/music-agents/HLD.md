# Music Agents — High-level design (Python/Django)

## Architecture (shared core)
- **Django + DRF** API-first
- **Postgres** multi-tenant (org_id on all tables)
- **Celery + Redis** background jobs (enrichment, sequences, parsing)
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
- Curator
- Playlist
- Prospect (campaign↔curator/playlist)
- **MailboxConnection** (OAuth identity, provider, email, status)
- MessageThread (external thread IDs)
- OutboundMessage (subject/body/template version)
- SequenceStep (scheduled follow-ups)
- Outcome
- **SuppressionEntry** (email, reason: unsubscribe/bounce/manual)
- **MessageSendAttempt** (idempotency key, provider msg id, error category)

### Gmail integration (MVP)
- Send: Gmail API `users.messages.send`
- Reply detection: periodic polling via Gmail History API (or thread fetch), keyed by Gmail `threadId`
- Store mapping: internal MessageThread ↔ Gmail threadId
- Heuristics handling: bounces/OOO/auto-replies; mark + suppress.

### Send correctness + deliverability
- Per-mailbox rate limiting (token bucket) + org-level caps
- Celery queues separated by concern: `send`, `enrich`, `parse`
- Exactly-once-ish semantics for send:
  - idempotency key per (mailbox, campaign, prospect, sequence_step)
  - retry-safe (no double-send)
- Stop rules enforced centrally (reply/unsubscribe/bounce/manual)

### Discovery reality
- Spotify yields lead metadata; **contacts come from CSV/manual import** or approved enrichment providers.

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
- Strong audit logs for sends/edits/exports

## Scalability
- composite indexes by (org_id, status, created_at)
- partition append-only tables later (ActivityEvent, OutboundMessage, SendAttempt)
- observability metrics: sends/day, bounce rate, reply rate, queue depth, step lag
