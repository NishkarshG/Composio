#!/usr/bin/env python3
"""Build dist/index.html: inline data/guides/*.json and data/directory.json into src/template.html.

Usage: python3 build.py
The result is one self-contained HTML file (fonts load from Google Fonts).
"""
import json
import pathlib

root = pathlib.Path(__file__).parent
guides = [json.loads(p.read_text()) for p in sorted((root / "data" / "guides").glob("*.json"))]
directory = json.loads((root / "data" / "directory.json").read_text())


def js(obj):
    # Escape "</" so embedded text can never close the <script> element.
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


html = (root / "src" / "template.html").read_text()
for marker, value in (("/*__GUIDES__*/[]", js(guides)), ("/*__DIRECTORY__*/{managed:[],byo:[]}", js(directory))):
    assert marker in html, f"marker missing: {marker}"
    html = html.replace(marker, value)

out = root / "dist" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(f"wrote {out} ({len(html) / 1024:.0f} KB), {len(guides)} guides")
