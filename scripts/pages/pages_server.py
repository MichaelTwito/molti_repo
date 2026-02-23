#!/usr/bin/env python3
"""LAN-only static server for the repo, kept in sync with origin/main.

- Serves from a *clean deploy clone* (not the dev workspace).
- Auto-sync: git fetch + reset --hard to origin/main on a fixed interval.

Defaults:
- Repo URL: git@github.com:MichaelTwito/molti_repo.git
- Deploy dir: /home/michael/.openclaw/pages_repo
- Branch: main
- Port: 18790
- Bind: 0.0.0.0 (LAN)
- Sync every: 3600s

Usage:
  python3 scripts/pages/pages_server.py
  PAGES_REPO_URL=... PAGES_DIR=... SYNC_EVERY_SEC=600 python3 scripts/pages/pages_server.py
"""

import os
import subprocess
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

REPO_URL = os.environ.get('PAGES_REPO_URL', 'git@github.com:MichaelTwito/molti_repo.git')
PAGES_DIR = Path(os.environ.get('PAGES_DIR', '/home/michael/.openclaw/pages_repo'))
BRANCH = os.environ.get('PAGES_BRANCH', 'main')
BIND = os.environ.get('PAGES_BIND', '0.0.0.0')
PORT = int(os.environ.get('PAGES_PORT', '18790'))
SYNC_EVERY_SEC = int(os.environ.get('SYNC_EVERY_SEC', '3600'))


def run(cmd: list[str], cwd: Path | None = None) -> str:
    r = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed ({r.returncode}): {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return (r.stdout + r.stderr).strip()


def ensure_clone() -> None:
    if (PAGES_DIR / '.git').exists():
        return
    PAGES_DIR.parent.mkdir(parents=True, exist_ok=True)
    run(['git', 'clone', '--depth', '1', '--branch', BRANCH, REPO_URL, str(PAGES_DIR)])


def sync_once() -> None:
    ensure_clone()
    # Clean, deterministic deploy: exactly origin/main
    run(['git', 'fetch', 'origin', BRANCH], cwd=PAGES_DIR)
    run(['git', 'reset', '--hard', f'origin/{BRANCH}'], cwd=PAGES_DIR)
    # Remove untracked files that could accumulate
    run(['git', 'clean', '-fd'], cwd=PAGES_DIR)


def sync_loop() -> None:
    # First sync immediately
    while True:
        try:
            sync_once()
            print(f"[pages] synced at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"[pages] sync error: {e}")
        time.sleep(SYNC_EVERY_SEC)


def main() -> None:
    # Start sync thread
    t = threading.Thread(target=sync_loop, daemon=True)
    t.start()

    # Serve files
    os.chdir(str(PAGES_DIR))
    httpd = ThreadingHTTPServer((BIND, PORT), SimpleHTTPRequestHandler)
    print(f"[pages] serving {PAGES_DIR} on http://{BIND}:{PORT} (sync every {SYNC_EVERY_SEC}s)")
    httpd.serve_forever()


if __name__ == '__main__':
    main()
