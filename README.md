# Workspace Utility Scripts

## Startup ideas index
- Repo page: `docs/ideas.html`
- Canonical list: `startup_ideas.md`

This workspace adds a handful of helper scripts that enforce and validate the workflows described in `periodic_ideas.jsonl` (and how those ideas get promoted into tasks).

## Agent health summary

- **What it does:** reads `agents_status.json`, summarizes each agent's reporting status, and writes a human-friendly `AGENTS_STATUS.md`.
- **How to use:** run `node scripts/generate_agents_status_summary.js` after updating `agents_status.json` (this is what the daily cron job should do).

## Cron heartbeat tracking

- **Purpose:** every cron-driven agent should call `node scripts/update_cron_heartbeat.js --agent=<name> [--status=healthy] [--note="something short"]` after it finishes successfully.
- **Output:** updates `cron/cron_heartbeats.json` plus a Markdown snapshot at `cron/CRON_HEARTBEAT.md`.

## Skill template scaffolder

- **Command:** `node scripts/create_skill_template.js <skill-name> [--description="..."`] creates `skills/<skill-name>/SKILL.md`, a placeholder test file, and sample tool calls.
- **Why it's useful:** gives a consistent starting point whenever a new AgentSkill topic is added.

Keep these scripts in mind the next time you regenerate agent summaries, audit cron jobs, or scaffold new skills.

## Agent reflection job

- **What it does:** runs `node scripts/agent_reflection.js` to summarize any failing agents from `agents_status.json` into `reflection/agent_reflection.md`, and lists next actions for the operations team.
- **Suggested cadence:** schedule this as a daily cron job (after the status summary job) so that the reflection always sees the latest data; it can live in the same cron entry as the status refresh.

## Task tagging

- **Convention:** use `tasks.jsonl` for short action items and give each one a `tags` array with values like `#cron`, `#manual`, `#debug`, or `#reflection` so multi-agent routing and filtering stay clear.
- **Example:** the file already contains entries for the agent status summary, the reflection job, and the travel planner handoff.

## Agent playbook

- See `docs/agents-playbook.md` for each agent's responsibility, triggers, and failure modes so that you can triage incidents without digging through transcripts.
