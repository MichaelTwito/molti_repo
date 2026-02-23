#!/usr/bin/env python3
"""Listen on X: run a set of queries and save results.

Usage:
  python3 scripts/marketing/listen_x.py --project promptprecision --query "(lora OR peft) eval harness" --max 20

Writes JSON to tmp/marketing/x_<project>_<slug>.json
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from scripts.x import x_client

WS = Path('/home/michael/.openclaw/workspace')
OUTDIR = WS / 'tmp' / 'marketing'


def slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:60] or 'q'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--project', required=True)
    ap.add_argument('--query', required=True)
    ap.add_argument('--max', type=int, default=20)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Ask for author_id + created_at + text. Keep minimal.
    params = {
        'query': args.query,
        'max_results': str(max(10, min(args.max, 100))),
        'tweet.fields': 'created_at,author_id,lang,public_metrics',
    }

    status, body = x_client.get('https://api.x.com/2/tweets/search/recent', params=params)

    payload = {
        'ts': datetime.utcnow().isoformat() + 'Z',
        'project': args.project,
        'query': args.query,
        'status': status,
        'body': None,
        'error': None,
    }

    try:
        payload['body'] = json.loads(body)
    except Exception:
        payload['error'] = body[:2000]

    path = OUTDIR / f"x_{args.project}_{slug(args.query)}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(path))


if __name__ == '__main__':
    main()
