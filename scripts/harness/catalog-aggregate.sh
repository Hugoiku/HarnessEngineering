#!/usr/bin/env bash
# Regenerate Layer A aggregate stats in docs/knowledge/catalog.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CATALOG="$ROOT/docs/knowledge/catalog.md"
python3 - "$ROOT" "$CATALOG" <<'PY'
import pathlib, re, sys
root, catalog_path = sys.argv[1], pathlib.Path(sys.argv[2])
sections = [
    ("team-conventions", "team-conventions/catalog.md"),
    ("tech-wiki", "tech-wiki/catalog.md"),
    ("project", "project/catalog.md"),
]
rows = []
for name, rel in sections:
    p = root / "docs/knowledge" / rel
    count = proven = verified = draft = 0
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and not line.startswith("| ID") and not line.startswith("|----"):
                cols = [c.strip() for c in line.strip("|").split("|")]
                if len(cols) >= 4 and cols[0]:
                    count += 1
                    mat = cols[3].lower()
                    if mat == "proven": proven += 1
                    elif mat == "verified": verified += 1
                    elif mat == "draft": draft += 1
    rows.append(f"| {name} | {count} | {proven} | {verified} | {draft} | `{rel}` |")
text = catalog_path.read_text(encoding="utf-8")
block = "\n".join(rows)
new = re.sub(
    r"<!-- AGGREGATE_START -->.*?<!-- AGGREGATE_END -->",
    "<!-- AGGREGATE_START -->\n| Section | Entries | proven | verified | draft | B catalog |\n|---------|---------|--------|----------|-------|-----------|\n" + block + "\n<!-- AGGREGATE_END -->",
    text,
    flags=re.S,
)
catalog_path.write_text(new, encoding="utf-8")
print("Updated Layer A aggregate in", catalog_path)
PY
