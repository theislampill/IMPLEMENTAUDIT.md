#!/usr/bin/env bash
set -euo pipefail

# Public/doc package-shape gate. Source uses skills/implementaudit/ while the
# built .skill archive remains flat with SKILL.md at archive root and generated
# archive metadata skills="./"; repo docs must keep that distinction explicit.
#
# Usage: check-package-shape-claims.sh [--scan-root <dir>]

fail() {
  printf 'check-package-shape-claims: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scan_root="$repo_root"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --scan-root)
      [ "$#" -ge 2 ] || fail "--scan-root requires a directory argument"
      scan_root="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

cd "$scan_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - <<'PY'
import json
import re
import sys
from pathlib import Path

manifest_path = Path(".claude-plugin/plugin.json")
if not manifest_path.is_file():
    raise SystemExit("missing .claude-plugin/plugin.json")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest.get("skills") != "./skills/":
    raise SystemExit('source plugin manifest skills path must be "./skills/"')

scanned = [
    Path("AGENTS.md"),
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path("CONTRIBUTING.md"),
    Path("docs/portal/site.json"),
]

for base in [Path("skills"), Path("docs/portal/pages")]:
    if base.is_dir():
        scanned.extend(p for p in sorted(base.rglob("*")) if p.is_file())

for required in ["AGENTS.md"]:
    if not Path(required).is_file():
        raise SystemExit(f"missing {required}")

bad_patterns = [
    (re.compile(r'source\s+manifest.{0,80}skills:\s*["`]?\./["`]', re.I), 'source manifest must not claim archive-root skills: "./"'),
    (re.compile(r'artifact contains .*skills/', re.I), "stale archive contains skills/ claim"),
    (re.compile(r'must include the `skills/` layout', re.I), "stale required skills/ layout claim"),
    (re.compile(r'everything under `skills/`', re.I), "stale consumer payload scope claim"),
    (re.compile(r'package includes `skills/(?:references|templates|scripts)/', re.I), "stale installed package path uses skills/ prefix"),
    (re.compile(r'packaged templates under `skills/implementaudit/templates/`', re.I), "stale installed template path uses skills/ prefix"),
]

bad_document_patterns = [
    (re.compile(r'artifact\s+contains.{0,160}?old\s+skills/', re.I | re.S), "stale archive contains skills/ claim"),
    (re.compile(r'must\s+include\s+the\s+`skills/`\s+layout', re.I | re.S), "stale required skills/ layout claim"),
    (re.compile(r'everything\s+under\s+`skills/`', re.I | re.S), "stale consumer payload scope claim"),
    (
        re.compile(
            r'zip-format\s+archive\s+containing.{0,260}?```(?:text)?\s*skills/\s*\.claude-plugin/',
            re.I | re.S,
        ),
        "stale release-archive tree claims skills/ at archive root",
    ),
    (
        re.compile(r'```(?:text)?\s*skills/\s*\.claude-plugin/\s*```', re.I | re.S),
        "stale bare release-archive tree claims skills/ at archive root",
    ),
    (
        re.compile(r'package\s+includes\s+`skills/(?:references|templates|scripts)/', re.I | re.S),
        "stale installed package path uses skills/ prefix",
    ),
    (
        re.compile(r'packaged\s+templates\s+under\s+`skills/implementaudit/templates/`', re.I | re.S),
        "stale installed template path uses skills/ prefix",
    ),
]

violations = []
for path in scanned:
    if not path.is_file():
        continue
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        continue
    for lineno, line in enumerate(lines, 1):
        for pattern, reason in bad_patterns:
            if pattern.search(line):
                violations.append(f"{path.as_posix()}:{lineno}: {reason}: {line.strip()}")
    joined = "\n".join(lines)
    for pattern, reason in bad_document_patterns:
        if pattern.search(joined):
            violations.append(f"{path.as_posix()}: document-level: {reason}")

agents = Path("AGENTS.md").read_text(encoding="utf-8")
required_claims = [
    'Source plugin metadata declares `skills: "./skills/"`',
    'archive-local metadata with `skills: "./"`',
    "flat archive",
    "SKILL.md at archive root",
    "skills/implementaudit/",
]
for claim in required_claims:
    if claim not in agents:
        violations.append(f"AGENTS.md: missing required package-shape claim: {claim}")

readme = Path("README.md")
if readme.is_file():
    readme_text = readme.read_text(encoding="utf-8")
    for claim in [
        "SKILL.md",
        "references/",
        "scripts/",
        "templates/",
        '.claude-plugin/plugin.json  (skills: "./")',
        "Source layout vs release archive layout",
    ]:
        if claim not in readme_text:
            violations.append(f"README.md: missing release-asset tree claim: {claim}")

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-package-shape-claims: ok\n")
PY
