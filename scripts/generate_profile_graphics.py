#!/usr/bin/env python3
"""Generate dependency-free profile activity graphics from GitHub's public API."""

import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

USER = "MansiSuryawanshi"
ROOT = Path(__file__).resolve().parents[1]


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def svg(title, lines, path):
    height = 74 + len(lines) * 24
    escaped = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{height}" viewBox="0 0 880 {height}" role="img">',
        '<style>.t{font:600 18px ui-monospace,SFMono-Regular,Menlo,monospace;fill:#24292f}.l{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;fill:#57606a}@media(prefers-color-scheme:dark){.t{fill:#f0f6fc}.l{fill:#8b949e}}</style>',
        f'<text class="t" x="18" y="30">{escaped(title)}</text>',
    ]
    for i, line in enumerate(lines):
        body.append(f'<text class="l" x="18" y="{65 + i * 24}">{escaped(line)}</text>')
    body.append('</svg>')
    path.write_text("".join(body), encoding="utf-8")


def main():
    repos = api(f"/users/{USER}/repos?per_page=100&sort=updated")
    owned = [r for r in repos if not r.get("fork")]
    languages = Counter(r.get("language") for r in owned if r.get("language"))
    language_lines = [f"{name.lower():<14} {count:>2} repositories" for name, count in languages.most_common(8)]
    recent = [f"{r['name']:<42} ★ {r['stargazers_count']}" for r in owned[:6]]
    svg("LANGUAGES / PUBLIC REPOSITORIES", language_lines or ["No language data yet"], ROOT / "assets/languages.svg")
    svg("RECENTLY UPDATED", recent or ["No repository data yet"], ROOT / "assets/activity.svg")


if __name__ == "__main__":
    main()
