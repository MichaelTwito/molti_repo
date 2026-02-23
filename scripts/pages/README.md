# Pages server (LAN)

This is a small static server intended for LAN browsing (phone-friendly) that always serves the latest `origin/main`.

## Why
Serving directly from the dev workspace is messy (untracked files, local edits). Instead we keep a clean deploy clone under:
- `/home/michael/.openclaw/pages_repo`

## Run
```bash
python3 scripts/pages/pages_server.py
```

Env overrides:
- `PAGES_REPO_URL` (default: `git@github.com:MichaelTwito/molti_repo.git`)
- `PAGES_DIR` (default: `/home/michael/.openclaw/pages_repo`)
- `PAGES_BRANCH` (default: `main`)
- `PAGES_BIND` (default: `0.0.0.0`)
- `PAGES_PORT` (default: `18790`)
- `SYNC_EVERY_SEC` (default: `3600`)

## Notes
- Sync uses `git fetch` + `git reset --hard origin/main` + `git clean -fd`.
- The viewer pages are under `docs/` (e.g. `/docs/ideas.html`).
