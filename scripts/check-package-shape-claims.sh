#!/usr/bin/env bash
set -euo pipefail

# Validate the current v0.4 package-topology claims against their semantic
# owners. Historical release reports and changelog sections are deliberately
# outside this gate: older standalone-skill evidence remains valid history.
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
    *) fail "unknown argument: $1" ;;
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


def load_object(path: str) -> dict:
    source = Path(path)
    if not source.is_file():
        raise SystemExit(f"missing {path}")
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return value


contract_path = "package/implementaudit-package.json"
codex_path = ".codex-plugin/plugin.json"
claude_path = ".claude-plugin/plugin.json"
contract = load_object(contract_path)
codex = load_object(codex_path)
claude = load_object(claude_path)

expected_contract = {
    "logical_package": "IMPLEMENTAUDIT_PLUGIN",
    "package_name": "implementaudit",
    "public_governor": "implementaudit",
    "public_entrypoint": "/implementaudit",
    "required_skills": ["implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"],
    "internal_skills": [
        {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
        {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
        {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
        {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
    ],
    "host_manifests": {"codex": codex_path, "claude": claude_path},
    "generated_projections": {
        "canonical_plugin": {
            "artifact": "IMPLEMENTAUDIT.plugin.zip",
            "layout": "plugin-root",
        },
        "standalone_compatibility": {
            "artifact": "IMPLEMENTAUDIT.skill",
            "layout": "flattened-skill",
        },
    },
}
for key, expected in expected_contract.items():
    if contract.get(key) != expected:
        raise SystemExit(
            f"{contract_path} {key} mismatch: expected {expected!r}, got {contract.get(key)!r}"
        )

if codex != claude:
    raise SystemExit("Codex and Claude plugin manifests must be identical")
expected_manifest = {
    "name": contract["package_name"],
    "version": contract.get("runtime_version"),
    "description": contract.get("description"),
    "skills": "./skills/",
    "author": contract.get("publisher"),
}
if codex != expected_manifest:
    raise SystemExit(
        "host manifests must exactly match package name/version/description/publisher and skills='./skills/'"
    )

skill_entries = sorted(
    path.parent.name for path in Path("skills").glob("*/SKILL.md") if path.is_file()
)
if skill_entries != sorted(contract["required_skills"]):
    raise SystemExit(
        f"model-facing skill population mismatch: expected {contract['required_skills']!r}, got {skill_entries!r}"
    )

current_docs = {
    "AGENTS.md": [
        "one atomic dual-host plugin package",
        "IMPLEMENTAUDIT.plugin.zip",
        "IMPLEMENTAUDIT.skill",
        "sole stable public/default governor",
        "exactly four model-facing child skills",
        "audit-implement",
        "audit-andon",
        "native host-discovery proof",
    ],
    "README.md": [
        "one atomic dual-host plugin",
        "IMPLEMENTAUDIT.plugin.zip",
        "IMPLEMENTAUDIT.skill",
        "sole stable public/default governor",
        "exactly four child skills",
        "audit-implement",
        "audit-andon",
        "package/implementaudit-package.json",
    ],
    "CONTRIBUTING.md": [
        "package/implementaudit-package.json",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "--check --all dist dist/CHECKSUMS.txt",
    ],
    "docs/portal/pages/package-contents.html": [
        "One atomic package, two generated projections.",
        "IMPLEMENTAUDIT.plugin.zip",
        "IMPLEMENTAUDIT.skill",
        "exactly four child skills",
        "audit-implement",
        "audit-andon",
        "not evidence that marketplace discovery",
    ],
}

violations = []
for path, claims in current_docs.items():
    source = Path(path)
    if not source.is_file():
        violations.append(f"missing {path}")
        continue
    text = source.read_text(encoding="utf-8")
    for claim in claims:
        if claim not in text:
            violations.append(f"{path}: missing current package claim: {claim}")

# These are affirmative current-topology/native-host claims, not historical
# references. Keep the scope narrow so append-only v0.2/v0.3 evidence survives.
current_surfaces = [
    Path("AGENTS.md"),
    Path("CONTRIBUTING.md"),
    Path("docs/portal/site.json"),
    *sorted(Path("docs/portal/pages").glob("*.html")),
]
forbidden = [
    (re.compile(r"IMPLEMENTAUDIT\.skill\s+is\s+the\s+(?:canonical|primary)\s+(?:package|release)", re.I),
     "standalone compatibility artifact promoted to canonical package"),
    (re.compile(r"(?:Codex|Claude)\s+(?:natively\s+)?(?:discovers|loads|installs)\s+(?:the\s+)?plugin", re.I),
     "native host behavior claimed without a bound host witness"),
    (re.compile(r"(?:published|listed)\s+(?:to|on)\s+the\s+marketplace", re.I),
     "marketplace publication claimed without public evidence"),
]
for path in current_surfaces:
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    for pattern, reason in forbidden:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            violations.append(f"{path.as_posix()}:{line}: {reason}")

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-package-shape-claims: ok\n")
PY
