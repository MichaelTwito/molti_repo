#!/usr/bin/env python3
"""Minimal X API v2 client using OAuth2 user access token.

Reads tokens from /home/michael/.openclaw/workspace/x_tokens.json.

This is intentionally tiny and dependency-free (urllib).
"""

import json
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

WS = Path('/home/michael/.openclaw/workspace')
TOKENS = WS / 'x_tokens.json'


def _token() -> str:
    obj = json.loads(TOKENS.read_text(encoding='utf-8'))
    return obj['access_token']


def request(method: str, url: str, params: dict | None = None, json_body: dict | None = None):
    if params:
        url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)

    data = None
    headers = {
        'Authorization': 'Bearer ' + _token(),
    }

    if json_body is not None:
        data = json.dumps(json_body).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            body = r.read().decode('utf-8', 'replace')
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace') if hasattr(e, 'read') else ''
        return e.code, body


def get(url: str, params: dict | None = None):
    return request('GET', url, params=params)


def post(url: str, json_body: dict):
    return request('POST', url, json_body=json_body)
