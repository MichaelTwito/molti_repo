#!/usr/bin/env python3
"""Run the initial X listening queries for AOD and PromptPrecision.

Writes dumps under tmp/marketing/.
"""

import json
import re
import ssl
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

WS = Path('/home/michael/.openclaw/workspace')
TOKENS = WS / 'x_tokens.json'
OUTDIR = WS / 'tmp' / 'marketing'


def _get(url: str, params: dict) -> tuple[int, str]:
    url = url + '?' + urllib.parse.urlencode(params)
    tok = json.loads(TOKENS.read_text(encoding='utf-8'))['access_token']
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + tok})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')


def _slug(q: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', q.lower()).strip('-')
    return (s[:60] or 'q')


def run(project: str, query: str, max_results: int = 20) -> Path:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    params = {
        'query': query,
        'max_results': str(max(10, min(max_results, 100))),
        'tweet.fields': 'created_at,author_id,lang,public_metrics',
    }
    status, body = _get('https://api.x.com/2/tweets/search/recent', params)
    payload = {
        'ts': datetime.utcnow().isoformat() + 'Z',
        'project': project,
        'query': query,
        'status': status,
    }
    try:
        payload['body'] = json.loads(body)
    except Exception:
        payload['error'] = body[:2000]

    path = OUTDIR / f"x_{project}_{_slug(query)}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


def main() -> None:
    queries = [
        ('aod', 'agent observability tracing telemetry approval policy audit'),
        ('aod', 'langsmith agent tracing evals'),
        ('aod', 'agentops helicone pricing'),
        ('promptprecision', 'lora peft eval harness json schema structured output'),
        ('promptprecision', 'small model 7b finetune benchmark evals'),
        ('promptprecision', 'structured output json schema reliability'),
    ]

    for project, q in queries:
        p = run(project, q, 25)
        print(p)


if __name__ == '__main__':
    main()
