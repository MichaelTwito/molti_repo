# Marketing Agent (X + communities) — MVP

## Goal
An internal agent that continuously checks relevant communities (starting with X) to validate feasibility of our startup ideas, produce a **daily/weekly situation report**, and draft **human-approved** outbound posts.

## Guardrails
- No automatic posting without explicit Rick approval (default).
- No scraping bypass; respect platform terms.
- Privacy: no sharing private info (Talia DMs, Garmin health data, credentials).
- Rate limits: conservative; cache queries.

## MVP capabilities
1) **Listen**: keyword queries per project (AOD, PromptPrecision, etc.)
2) **Summarize**: what people complain about / ask for / pay for
3) **Score**: a simple feasibility score + confidence + next experiments
4) **Draft**: post ideas + 1–3 concrete tweets (but do not post)

## Inputs
- `projects/index.json` + per-project keywords
- X API tokens in `x_tokens.json` (ignored by git)

## Outputs
- `memory/marketing-agent/YYYY-MM-DD.md` daily report
- Optional: send summary to Telegram group/channel

## Next
- Add connectors: HN (Algolia), Reddit, GitHub
- Add scheduling (cron) + report delivery
