from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

DOC = Path("/home/michael/.openclaw/workspace/docs/ideas.html")


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        d = dict(attrs)
        href = d.get("href")
        if href:
            self.links.append(href)


def main() -> None:
    html = DOC.read_text(encoding="utf-8")
    lp = LinkParser()
    lp.feed(html)

    bad: list[tuple[str, str]] = []
    for href in lp.links:
        if href.startswith("http://") or href.startswith("https://") or href.startswith("#"):
            continue
        target = (DOC.parent / href).resolve()
        if not target.exists():
            bad.append((href, str(target)))

    print(f"ideas.html links={len(lp.links)} bad={len(bad)}")
    for href, target in bad:
        print(f"BAD {href} -> {target}")


if __name__ == "__main__":
    main()
