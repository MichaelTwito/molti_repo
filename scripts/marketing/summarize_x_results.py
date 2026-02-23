#!/usr/bin/env python3
"""Summarize X query JSON dumps into a short report (no LLM).

Usage:
  python3 scripts/marketing/summarize_x_results.py tmp/marketing/x_promptprecision_*.json
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def main(paths: list[str]) -> None:
    all_text = []
    langs = Counter()
    n = 0
    for p in paths:
        obj = json.loads(Path(p).read_text(encoding='utf-8'))
        body = obj.get('body') or {}
        for t in body.get('data', []) or []:
            n += 1
            txt = (t.get('text') or '').strip()
            if txt:
                all_text.append(txt)
            langs[t.get('lang') or ''] += 1

    print(f"Collected {n} posts")
    if langs:
        top = ', '.join([f"{k}:{v}" for k,v in langs.most_common(6) if k])
        print(f"Languages: {top}")

    # Very naive keyword extraction
    words = Counter()
    for txt in all_text:
        for w in txt.lower().split():
            w = ''.join(ch for ch in w if ch.isalnum() or ch in ('-', '_'))
            if len(w) < 4:
                continue
            if w.startswith('http'):
                continue
            words[w] += 1

    print("Top terms:")
    for w,c in words.most_common(25):
        print(f"- {w}: {c}")


if __name__ == '__main__':
    main(sys.argv[1:])
