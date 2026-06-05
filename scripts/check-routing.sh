#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-routing: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" <<'PY'
from pathlib import Path

ROOT = Path(".")
failures = []


def read(path):
    p = ROOT / path
    if not p.is_file():
        failures.append(f"missing required file: {path}")
        return ""
    return p.read_text(encoding="utf-8").lower()


def require(text, needle, label, path):
    if needle.lower() not in text:
        failures.append(f"{path}: missing {label}: {needle}")


def require_any(text, needles, label, path):
    if not any(needle.lower() in text for needle in needles):
        failures.append(f"{path}: missing {label}: {' | '.join(needles)}")


routing_path = "skills/references/routing.md"
routing = read(routing_path)

for needle in [
    "greenfield audit-governed work",
    "brownfield audit-governed work",
    "mixed-mode work",
    "default to brownfield when an existing repo is present",
    "new file",
]:
    require(routing, needle, "routing definition", routing_path)

for needle in [
    "owner/source of truth",
    "scope and non-scope",
    "constraints and invariants",
    "acceptance criteria",
    "rollback or removal path",
    "evidence plan",
    "generated artifact plan",
    "graphify / activegraph sidecar status",
    "canonical-vs-sidecar statement",
]:
    require(routing, needle, "greenfield intake field", routing_path)

for needle in [
    "existing owner/source",
    "documented contracts and invariants",
    "tests, smokes, and checkers",
    "generated artifacts",
    "regression surface",
    "rollback path",
    "andon or `unverified` caveat",
]:
    require(routing, needle, "brownfield inspection field", routing_path)

for needle in [
    "graphify may aid brownfield terrain inspection",
    "absent, stale, or unauthorized graphify falls back",
    "activegraph may preserve sidecar custody",
    "absent activegraph falls back to markdown ledgers",
    "neither sidecar replaces repo-local owners",
]:
    require(routing, needle, "sidecar boundary", routing_path)

for path in ["README.md", routing_path, "AGENTS.md"]:
    text = read(path)
    require(text, "audit-governed", "positive identity anchor", path)
    require(text, "owner/source", "positive identity anchor", path)
    require(text, "evidence plan", "positive identity anchor", path)
    require(text, "rollback", "positive identity anchor", path)

valid_fixtures = {
    "fixtures/routing/greenfield-goal-synthesis/EXPECTED.md": [
        "classification: mixed",
        "owner/source of truth",
        "scope",
        "non-scope",
        "constraints/invariants",
        "acceptance criteria",
        "rollback/removal path",
        "evidence plan",
        "generated artifact plan",
        "graphify / activegraph sidecar status",
        "canonical-vs-sidecar statement",
    ],
    "fixtures/routing/brownfield-audit-closure/EXPECTED.md": [
        "classification: brownfield",
        "governing files",
        "existing owner/source",
        "contracts/invariants",
        "tests/smokes/checkers",
        "generated artifacts",
        "graphify / activegraph sidecars",
        "regression surface",
        "rollback path",
        "patch owner/source only after inspection",
    ],
    "fixtures/routing/mixed-greenfield-in-brownfield/EXPECTED.md": [
        "classification: mixed",
        "brownfield shell",
        "greenfield intake for new artifacts",
        "owner/source of truth",
        "acceptance criteria",
        "rollback/removal path",
        "evidence plan",
        "graphify / activegraph sidecar status",
    ],
}

for path, needles in valid_fixtures.items():
    text = read(path)
    for needle in needles:
        require(text, needle, "valid fixture requirement", path)

invalid_fixtures = {
    "fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md": [
        "owner/source of truth",
        "rollback/removal path",
        "evidence plan",
    ],
    "fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md": [
        "existing owner/source inspection",
        "tests/smokes/checkers inspection",
        "regression surface",
        "rollback path",
    ],
}

for path, required_absent in invalid_fixtures.items():
    text = read(path)
    for needle in required_absent:
        if needle in text:
            failures.append(f"{path}: invalid fixture unexpectedly contains pass field: {needle}")

scan_paths = [
    "README.md",
    "AGENTS.md",
    "skills/references/routing.md",
    "skills/references/planning-depth.md",
    "skills/references/goal-format.md",
    "skills/references/phase-design.md",
    "skills/SKILL.md",
]
forbidden_phrases = [
    "autonomously build a software task " + "end-to-end",
    "generic autonomous " + "build runner",
    "one paste " + "and done",
    "plan and " + "ship " + "anything",
    "ship " + "anything",
    "don't stop " + "until done",
    "fully autonomous " + "builder",
    "generic " + "build runner",
]
negative_context = (
    "not ",
    "not a ",
    "must not",
    "do not",
    "does not",
    "forbidden",
    "anti-pattern",
    "cannot",
    "never",
)

for path in scan_paths:
    text = read(path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for phrase in forbidden_phrases:
            if phrase in line and not any(context in line for context in negative_context):
                failures.append(f"{path}:{line_no}: endorsed generic-runner wording: {phrase}")

if failures:
    raise SystemExit("\n".join(failures))

print("check-routing: ok")
PY
