# Music Agents — PRD outline (recommended wedges)

## Recommended wedge order
1) **Playlisting / Outreach Agent** (fastest to revenue)
2) **Rights & Royalties Ops Agent** (higher-$, more defensible, longer sales)

---

## Wedge A: Playlisting / Outreach Agent (MVP)

### Problem
Indie teams waste time building a relevant lead list (playlists/curators) and running consistent, personalized outreach with follow-ups—then lose track of what worked.

### ICP
Indie artists, managers, small labels (1–20 roster). Freelance promo/publicists.

### KPIs
Response rate, placement rate, time-to-first-response, qualified leads per track, deliverability/bounce rate, pipeline velocity.

### MVP promise (be explicit)
- **Spotify discovery is research-only. MVP does not promise curator emails.**
- Core value is workflow: **upload/import contacts → compliant sequences → reply/outcome tracking**.

### Core flow (MVP)
Track intake → optional research (Spotify) → **contact import (first-class)** → pitch drafting → send + follow-up → outcome tracking.

### Data sources & compliance constraints (MVP)
- **Spotify Web API = metadata + discovery signals only** (playlist/owner IDs, follower counts, basic proximity heuristics).
- Allowed sources list (v1):
  1) **User-provided manual/CSV import** (name/email/platform/notes)
  2) **Approved enrichment vendors under contract** (TBD; ToS-compliant)
  3) First-party inbound leads provided by the user
- Explicitly disallowed (v1): scraping sources that prohibit it, bypassing rate limits/paywalls.
- Contact provenance must be stored: user import vs enrichment vendor.

### MVP features
- Campaign per track
- CRM: contacts, status, notes, history
- Pitch templates + AI draft + user review/approve
- Gmail integration + basic sequences (e.g., 2 follow-ups) + **stop rules**
- Dashboard (sent / replies / placements) + activity log
- Optional research module: Spotify playlist discovery + simple relevance rationale (“why relevant”) without contact promises

### Email compliance & deliverability (MVP requirements)
- Sending model: **send from the user’s connected Gmail mailbox** (OAuth), not a shared blasting domain.
- Mandatory:
  - Unsubscribe mechanism + **suppression list** (unsubscribe/bounce/manual)
  - Stop rules: stop on human reply, unsubscribe, bounce, manual stop
  - Throttling: per-mailbox daily caps + spacing + jitter; scheduling windows
  - Bounce detection + auto-suppress
  - Audit trail: who sent what, when, and which template/version
  - List hygiene: syntax validation, duplicate detection, role-account warnings (admin@, info@), optional per-domain throttling
- Optional (off by default): open/click tracking (jurisdiction-dependent).

### Compliance & privacy (MVP)
- Document lawful basis stance for outreach (GDPR/UK GDPR considerations + CAN-SPAM basics).
- Retention defaults must be explicit (store metadata vs bodies); full-body storage is opt-in.
- Org data export + deletion flows (admin action).

### Non-goals (MVP)
- Guaranteed placements
- Automatic contact acquisition from Spotify alone
- Social DMs automation (IG/Twitter/TikTok)
- Automated placement detection (V1+)

### V1+
Gmail push notifications (Pub/Sub), A/B testing subject/openers, placement monitoring where feasible, team collaboration/approvals, optional enrichment integrations.

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
- B2C vs B2B first?
- Email-only MVP acceptable for outreach?
- Gmail-only MVP acceptable?
- Allowed enrichment vendors and ToS policy?
- Team/multi-org required day one?
