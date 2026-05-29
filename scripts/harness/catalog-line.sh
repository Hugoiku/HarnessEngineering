#!/usr/bin/env bash
# Generate one B-layer catalog table row from a C-layer markdown file frontmatter.
set -euo pipefail

ENTRY_FILE="${1:?usage: catalog-line.sh <entry.md>}"
python3 - "$ENTRY_FILE" <<'PY'
import re, sys, pathlib
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---", text, re.S)
if not m:
    sys.exit("missing frontmatter")
fm = {}
for line in m.group(1).splitlines():
    if ":" in line:
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip('"')
required = ["id", "title", "type", "maturity", "tags"]
for k in required:
    if k not in fm:
        sys.exit(f"missing frontmatter field: {k}")
tags = fm["tags"].strip("[]")
summary = fm.get("summary", fm["title"])
print(f"| {fm['id']} | {fm['title']} | {fm['type']} | {fm['maturity']} | {tags} | {summary} |")
PY
