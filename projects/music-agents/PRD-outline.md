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

### Core flow (MVP)
Track intake → **lead list discovery/scoring** → contact import/enrichment → pitch drafting → send + follow-up → outcome tracking.

### Data sources & compliance constraints (MVP)
- **Spotify Web API = metadata + discovery signals only** (playlist/owner IDs, follower counts, genre-ish signals). It does **not** reliably provide curator contact emails.
- Supported contact sources in MVP:
  1) **User-provided manual/CSV import** (name/email/platform/notes)
  2) Optional enrichment provider integrations (TBD, ToS-compliant)
- **No scraping of sources that disallow it**; “allowed sources” must be explicitly documented.

### MVP features
- Campaign per track
- Playlist/lead discovery (Spotify search + similarity heuristics) + relevance scoring (“why relevant”)
- CRM: contacts, status, notes, history
- Pitch templates + AI draft + user review/approve
- Gmail integration + basic sequences (e.g., 2 follow-ups) + **stop rules**
- Dashboard (sent / replies / placements) + activity log

### Email compliance & deliverability (MVP requirements)
- Sending model: **send from the user’s connected Gmail mailbox** (OAuth), not a shared blasting domain.
- Mandatory:
  - Unsubscribe mechanism + **suppression list** (unsubscribe/bounce/manual)
  - Stop rules: stop on human reply, unsubscribe, bounce, manual stop
  - Throttling: per-mailbox daily caps + spacing + jitter; scheduling windows
  - Bounce detection + auto-suppress
  - Audit trail: who sent what, when, and which template/version
- Optional (off by default): open/click tracking.

### Non-goals (MVP)
- Guaranteed placements
- Automatic contact acquisition from Spotify alone
- Social DMs automation (IG/Twitter/TikTok)
- Automated placement detection (V1+)

### V1+
Multi-channel (non-automated links), A/B testing subject/openers, placement monitoring where feasible, team collaboration/approvals.

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
- Allowed data sources (Spotify-only vs Chartmetric/Songstats) and ToS policy?
- Team/multi-org required day one?
