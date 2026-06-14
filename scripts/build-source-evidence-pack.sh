#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'build-source-evidence-pack: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

output="${1:-dist/IMPLEMENTAUDIT-SOURCE-EVIDENCE.zip}"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$output" <<'PY'
import stat
import sys
import zipfile
from pathlib import Path

repo = Path.cwd()
output = Path(sys.argv[1]).resolve()

include_roots = [
    ".claude-plugin",
    ".github/workflows",
    "docs/diagrams",
    "docs/portal",
    "fixtures",
    "scripts",
    "skills",
    "tests",
]
include_files = [
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "README.md",
    "docs/audits/INDEX.md",
    "docs/audits/RETENTION.md",
]
blocked_parts = {
    ".git",
    ".IMPLEMENTAUDIT",
    ".activegraph",
    ".graphify",
    "dist",
    "graphify-out",
    "plans",
}
blocked_names = {
    "auth.json",
    "config.toml",
    "custody.db",
    "graph.json",
    "quickstart_demo_run.db",
}
blocked_suffixes = (".db", ".sqlite", ".sqlite3", ".log", ".tmp", ".pyc")

run_validation = """# Source Evidence Pack Validation

This pack is local RC evidence only. It is not a release, tag, publication,
marketplace claim, provenance artifact, issue publication, license selection,
or real-home install proof.

Extract the zip, then run from the extracted pack root:

| Suite | Command | Expected exit | Expected last line |
|---|---|---:|---|
| Safeguards | `bash scripts/check-safeguard-restoration.sh` | 0 | `check-safeguard-restoration: ok` |
| Safeguard test | `bash tests/safeguard-restoration.test.sh` | 0 | `safeguard-restoration.test: ok` |
| Bootloader budget | `bash scripts/check-skill-bootstrap-budget.sh` | 0 | `check-skill-bootstrap-budget: ok (...)` |
| Plan-quality lane | `bash tests/plan-quality-contract.test.sh` | 0 | `plan-quality-contract.test: ok` |
| AGENTS bootloader budget | `bash tests/agents-bootstrap-budget.test.sh` | 0 | `agents-bootstrap-budget.test: ok` |
| Audit retention | `bash scripts/check-audit-retention.sh` | 0 | `check-audit-retention: ok` |
| Audit retention test | `bash tests/audit-retention.test.sh` | 0 | `audit-retention.test: ok` |
| Validation registry | `bash scripts/check-validation-registry.sh` | 0 | `check-validation-registry: ok (...)` |
| Source-evidence pack | `bash tests/source-evidence-pack.test.sh` | 0 | `source-evidence-pack.test: ok` |

Use Git Bash or another Bash-compatible shell. The source pack preserves real
repo-relative paths (`skills/`, `scripts/`, `tests/`, `fixtures/`) so tests
resolve the files they exercise.
"""

def blocked(rel: Path) -> bool:
    text = rel.as_posix()
    if any(part in blocked_parts for part in rel.parts):
        return True
    if rel.name in blocked_names:
        return True
    if text.startswith(".env"):
        return True
    return text.endswith(blocked_suffixes)

entries: list[tuple[Path, bytes, int]] = []

for file_name in include_files:
    path = repo / file_name
    if not path.is_file():
        raise SystemExit(f"missing source evidence file: {file_name}")
    entries.append((Path(file_name), path.read_bytes(), 0o644))

for root_name in include_roots:
    root = repo / root_name
    if not root.exists():
        raise SystemExit(f"missing source evidence root: {root_name}")
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo)
        if blocked(rel):
            raise SystemExit(f"blocked file selected for source evidence: {rel.as_posix()}")
        mode = 0o755 if rel.as_posix().startswith("scripts/") or rel.as_posix().startswith("tests/") else 0o644
        entries.append((rel, path.read_bytes(), mode))

entries.append((Path("RUN-VALIDATION.md"), run_validation.encode("utf-8"), 0o644))

names = [rel.as_posix() for rel, _, _ in entries]
if len(names) != len(set(names)):
    raise SystemExit("duplicate source evidence archive entries")

for required in [
    "skills/implementaudit/SKILL.md",
    "skills/implementaudit/references/sidecars.md",
    "skills/implementaudit/templates/final-report.md",
    "skills/implementaudit/templates/read-only-plan.md",
    "scripts/check-safeguard-restoration.sh",
    "scripts/check-agents-bootstrap-budget.sh",
    "tests/safeguard-restoration.test.sh",
    "tests/agents-bootstrap-budget.test.sh",
    "fixtures/safeguards/negative-missing-final-report.md",
    "docs/audits/RETENTION.md",
    "RUN-VALIDATION.md",
]:
    if required not in names:
        raise SystemExit(f"source evidence archive missing required entry: {required}")

output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel, data, mode in entries:
        info = zipfile.ZipInfo(rel.as_posix())
        info.external_attr = (stat.S_IFREG | mode) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        if rel.suffix.lower() in {".md", ".txt", ".sh", ".json", ".yml", ".yaml", ".html", ".css", ".js"}:
            data = data.replace(b"\r\n", b"\n")
        zf.writestr(info, data)

with zipfile.ZipFile(output) as zf:
    names = set(zf.namelist())
    for name in names:
        rel = Path(name)
        if blocked(rel):
            raise SystemExit(f"blocked file found in source evidence archive: {name}")
    for forbidden in [
        ".IMPLEMENTAUDIT/",
        "plans/",
        "graphify-out/",
        "docs/audits/archive/",
        ".git/",
    ]:
        if any(name.startswith(forbidden) for name in names):
            raise SystemExit(f"forbidden source evidence prefix included: {forbidden}")
    for name in names:
        if not name.endswith(".sh"):
            continue
        data = zf.read(name)
        if b"\r\n" in data:
            raise SystemExit(f"CRLF shell script found in source evidence archive: {name}")

sys.stdout.write(f"build-source-evidence-pack: wrote {output}\n")
sys.stdout.write("build-source-evidence-pack: ok\n")
PY
