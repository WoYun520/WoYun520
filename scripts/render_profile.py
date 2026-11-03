#!/usr/bin/env python3
"""Render the GitHub profile card; optionally refresh public GitHub statistics."""
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OWNER = "WoYun520"
API = "https://api.github.com"


def api_json(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "WoYun520-profile"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(API + path, headers=headers)
    with urlopen(request, timeout=25) as response:
        return json.load(response)


def public_stats():
    owner = quote(OWNER, safe="")
    account = api_json(f"/users/{owner}")
    stars = 0
    page = 1
    while True:
        repositories = api_json(f"/users/{owner}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(repositories, list):
            raise ValueError("GitHub returned an invalid repository list")
        stars += sum(int(repo["stargazers_count"]) for repo in repositories)
        if len(repositories) < 100:
            break
        page += 1
    return {"repos": int(account["public_repos"]), "stars": stars, "followers": int(account["followers"])}


def portrait_lines():
    path = ROOT / "assets" / "avatar.txt"
    if not path.is_file():
        return [
            "", "", "", "", "", "",
            "            .---------------------------.",
            "            |                           |",
            "            |     AVATAR  PORTRAIT      |",
            "            |                           |",
            "            |       awaiting image      |",
            "            |                           |",
            "            '---------------------------'",
        ]
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > 38 or any(len(line) > 58 for line in lines):
        raise ValueError("Avatar text must fit within 58 columns and 38 rows")
    return lines


def fmt(stats, key):
    return f"{stats[key]:,}" if key in stats else "—"


def render(stats=None):
    stats = stats or {}
    art = "\n".join(
        f'<tspan x="45" y="{126 + i * 9.5:.1f}">{escape(line)}</tspan>'
        for i, line in enumerate(portrait_lines())
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="570" viewBox="0 0 960 570" role="img" aria-labelledby="title desc">
<title id="title">Levi 卧云 · GitHub profile</title>
<desc id="desc">Terminal-style profile with a character portrait, current projects and public GitHub statistics.</desc>
<style>
  .bg {{ fill: #fff; stroke: #d8dee4; }}
  .ink {{ fill: #24292f; }} .muted {{ fill: #6e7781; }}
  .blue {{ fill: #0969da; }} .orange {{ fill: #a43f11; }}
  .line {{ stroke: #d8dee4; }} .dots {{ fill: #afb8c1; }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }}
  @media (prefers-color-scheme: dark) {{
    .bg {{ fill: #0d1117; stroke: #30363d; }}
    .ink {{ fill: #e6edf3; }} .muted {{ fill: #8b949e; }}
    .blue {{ fill: #79c0ff; }} .orange {{ fill: #ffa657; }}
    .line {{ stroke: #30363d; }} .dots {{ fill: #484f58; }}
  }}
</style>
<rect class="bg" x="1" y="1" width="958" height="568" rx="14"/>
<circle cx="30" cy="29" r="4" fill="#ff7b72"/><circle cx="45" cy="29" r="4" fill="#e3b341"/><circle cx="60" cy="29" r="4" fill="#56d364"/>
<text class="muted" x="82" y="34" font-size="12" letter-spacing="1">LEVI / PROFILE.SH</text>
<line class="line" x1="22" y1="54" x2="938" y2="54" stroke-width="1"/>
<text class="muted" xml:space="preserve" font-size="9.3" letter-spacing="0">{art}</text>
<text class="muted" x="50" y="515" font-size="11" letter-spacing="1.2">A LITTLE WORLD UNDER THE STARS</text>
<text class="blue" x="407" y="110" font-size="19" font-weight="600">WoYun520@github</text>
<line class="line" x1="620" y1="104" x2="920" y2="104" stroke-width="1.5"/>
<text x="407" y="150" font-size="16"><tspan class="orange">Name:</tspan><tspan class="dots"> ........... </tspan><tspan class="ink">Levi · 卧云</tspan></text>
<text x="407" y="180" font-size="16"><tspan class="orange">Focus:</tspan><tspan class="dots"> .......... </tspan><tspan class="ink">AI tools · creative web</tspan></text>
<text x="407" y="210" font-size="16"><tspan class="orange">Workflow:</tspan><tspan class="dots"> ....... </tspan><tspan class="ink">Codex · Claude Code</tspan></text>
<text class="blue" x="407" y="257" font-size="16">— Projects</text><line class="line" x1="540" y1="251" x2="920" y2="251" stroke-width="1.5"/>
<text x="407" y="289" font-size="15"><tspan class="orange">Project Memory:</tspan><tspan class="dots"> ... </tspan><tspan class="ink">AI project handoff</tspan></text>
<text x="407" y="319" font-size="15"><tspan class="orange">Topic Scan:</tspan><tspan class="dots"> ....... </tspan><tspan class="ink">content discovery</tspan></text>
<text x="407" y="349" font-size="15"><tspan class="orange">Levi Flow:</tspan><tspan class="dots"> ........ </tspan><tspan class="ink">curated feed</tspan></text>
<text class="blue" x="407" y="396" font-size="16">— Connect</text><line class="line" x1="528" y1="390" x2="920" y2="390" stroke-width="1.5"/>
<text x="407" y="428" font-size="16"><tspan class="orange">X:</tspan><tspan class="dots"> .............. </tspan><tspan class="ink">@Leviwoyun</tspan></text>
<text class="blue" x="407" y="475" font-size="16">— GitHub Stats</text><line class="line" x1="570" y1="469" x2="920" y2="469" stroke-width="1.5"/>
<text x="407" y="510" font-size="15"><tspan class="orange">Repos:</tspan><tspan class="ink"> {fmt(stats,"repos")}</tspan><tspan class="dots">   |   </tspan><tspan class="orange">Stars:</tspan><tspan class="ink"> {fmt(stats,"stars")}</tspan><tspan class="dots">   |   </tspan><tspan class="orange">Followers:</tspan><tspan class="ink"> {fmt(stats,"followers")}</tspan></text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true", help="fetch live public GitHub counts before rendering")
    args = parser.parse_args()
    try:
        stats = public_stats() if args.update else {}
        (ROOT / "profile.svg").write_text(render(stats), encoding="utf-8")
    except Exception as exc:
        print(f"Profile update failed: {exc}", file=sys.stderr)
        return 1
    print("profile.svg updated" + (" with public GitHub counts" if args.update else " (preview counts)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
