# ENDPOINTS.md — user endpoints, storage, and status

This file is the durable index so Rick can ask for "status" even after /new or /reset.

## Canonical key
- For Telegram: **chatId** is the endpoint identity.

## Endpoints

### Family Trip group ("AI טיול")
- Channel: Telegram
- chatId: -1003842252088
- Purpose: Family trip planning (shared with Talia)
- Share policy: Group content is shared by definition; still do not import Talia private-DM content unless she consents.

### Shopping group ("קניות עם molti")
- Channel: Telegram
- chatId: -5297474487
- Purpose: Shared shopping list building (Rick + Talia) + Shufersal ordering
- Skill: `shufersal-order`
- Guardrail: never submit final order/payment without explicit phrase: `מאשר לבצע הזמנה עכשיו`
- Share policy: Group content is shared by definition; do not pull Talia private-DM content into the group unless she consents.

### PromptPrecision PM loop (dev group)
- Channel: Telegram
- chatId: -5288661071
- Purpose: Product iteration loop for PromptPrecision (PM + 3 dev subagents). Status updates each iteration.
- Coordinator prompt: `promptprecision_pm_group_prompt.md`
- Guardrail: never `git push` without explicit approval phrase: `APPROVE_PUSH`

### Rick (you)
- Channel: Telegram
- Storage:
  - Long-term: `USER.md` + curated files
  - Daily logs: `memory/YYYY-MM-DD.md`

### Rick — Garmin endpoint (private)
- Channel: Telegram
- chatId: 5289888689
- Purpose: Personal health/fitness endpoint for Garmin Connect (same person as Rick; full access allowed).
- Coordinator prompt: `garmin_profile_prompt.md`
- Storage:
  - Dedicated folder: `memory/garmin/`
  - Daily logs: `memory/YYYY-MM-DD.md`

### Tsofia (Rick's sister)
- Channel: Telegram
- Handle: @Tsofiatouito
- chatId: 7279866382
- Coordinator prompt: `tsofia_profile_prompt.md`
- Storage:
  - Daily logs: `memory/YYYY-MM-DD.md`
  - Dedicated folder: `memory/tsofia/`
- Share policy: OK to summarize to Rick (she’s coordinating with him), but still avoid secrets.

### Talia (Rick's wife)
- Channel: Telegram
- Endpoint: her private chat
- chatId: 8476960963
- Prompt: `wife_profile_prompt.md`
- Storage:
  - Dedicated folder: `memory/talia/`
  - Base context: `TALIA.md`
- Share policy: **Do not share Talia’s conversation summaries with Rick unless Talia explicitly consents.**
  - Rick can still ask: whether she has contacted; whether a summary is approved; and any admin/technical status.

## How to ask for status (examples)
- "סטטוס צופיה" → last contact + current task + blockers + next step.
- "סטטוס טליה" → admin status only unless consent (e.g., contacted? any agreed-to share?).
