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
