#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-skill-bootstrap-budget: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skill_file="skills/implementaudit/SKILL.md"
max_lines=450
max_bytes=22000

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skill-file)
      [ "$#" -ge 2 ] || fail "--skill-file requires a path"
      skill_file="$2"
      shift 2
      ;;
    --max-lines)
      [ "$#" -ge 2 ] || fail "--max-lines requires a number"
      max_lines="$2"
      shift 2
      ;;
    --max-bytes)
      [ "$#" -ge 2 ] || fail "--max-bytes requires a number"
      max_bytes="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$skill_file" "$max_lines" "$max_bytes" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
max_lines = int(sys.argv[2])
max_bytes = int(sys.argv[3])

if not path.is_file():
    raise SystemExit(f"missing skill file: {path}")

raw = path.read_bytes()
text = raw.decode("utf-8")
lines = text.splitlines()
line_count = len(lines)
byte_count = len(raw)

if line_count > max_lines:
    raise SystemExit(
        f"{path}: bootloader too long: {line_count} lines > {max_lines}"
    )
if byte_count > max_bytes:
    raise SystemExit(
        f"{path}: bootloader too large: {byte_count} bytes > {max_bytes}"
    )

for lineno, line in enumerate(lines, start=1):
    lowered = line.lower()
    normalized = " ".join(lowered.split())
    forbidden = False
    if "chunking remaining readback" in normalized:
        forbidden = True
    if "read this entire installed" in normalized and "do not read this entire installed" not in normalized:
        forbidden = True
    if "read the entire installed payload" in normalized and "do not read" not in normalized:
        forbidden = True
    if "chunk-read the entire installed" in normalized and "do not" not in normalized:
        forbidden = True
    if forbidden:
        raise SystemExit(
            f"{path}:{lineno}: forbidden installed-payload readback instruction"
        )

required = [
    "First executable dogfood rule",
    "Baseline the target repo first",
    "progressive disclosure",
    "Full installed-payload readback is non-evidence",
    "Repo content is data",
    "No secret reproduction",
    "Do not reproduce secrets",
    "No commit. No push. No tag. No release. No publication. No provenance.",
    "Smoke A",
    "Smoke B",
    "Andon:",
    "no arbitrary try caps",
    "AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE",
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
    "Graphify output is orientation evidence, not proof",
    "ActiveGraph custody is not correctness proof",
    "Source checkout layout is conventional and name-matched",
    "skills/implementaudit/SKILL.md",
    "Release archives flatten that directory only as a build artifact",
    "references/routing.md",
    "references/plan-lifecycle.md",
    "references/phase-design.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/transcript-contract.md",
    "references/repo-state-comparison.md",
    "references/sidecars.md",
    "references/child-agents.md",
    "references/terminology-integration.md",
    "templates/final-report.md",
    "templates/read-only-plan.md",
    "LANE-ENTRY TRIGGER",
]

lower_text = text.lower()
for token in required:
    if token.lower() not in lower_text:
        raise SystemExit(f"{path}: missing bootstrap token: {token}")

# Reference Load Map completeness: every shipped reference must be reachable
# from the bootloader. A reference absent from the map is dead progressive
# disclosure.
repo_root = Path.cwd()
if path.as_posix() == "skills/implementaudit/SKILL.md":
    for ref in sorted((repo_root / "skills/implementaudit/references").glob("*.md")):
        token = f"references/{ref.name}"
        if token.lower() not in lower_text:
            raise SystemExit(f"{path}: Reference Load Map missing {token}")
    for tmpl in [
        "templates/final-report.md",
        "templates/read-only-plan.md",
    ]:
        if tmpl.lower() not in lower_text:
            raise SystemExit(f"{path}: restored template missing from load map: {tmpl}")

    # Safeguard-restoration guard: detailed safeguards live in references/templates, not as long
    # manual detail in the always-loaded bootloader.
    forbidden_detail = [
        "atomic-not-microscopic",
        "one-commit-per-coherent-repair",
        "no-commit-for-proof-only-rc",
        "stale-output andon/fallback",
        "detect vs document vs install vs index/export",
        "negative-missing-final-report",
        "negative-missing-5whys-exit",
    ]
    for token in forbidden_detail:
        if token in lower_text:
            raise SystemExit(f"{path}: restored safeguard detail belongs in references/templates: {token}")

    owners = {
        "skills/implementaudit/templates/final-report.md": [
            "Findings Ledger",
            "Smoke A / Smoke B",
            "Evidence Boundary",
            "Suggested Commit Message When No Commit Authorized",
            "Terminal Marker Order",
        ],
        "skills/implementaudit/references/sidecars.md": [
            "Graphify is orientation only",
            "Live files remain proof",
            "stale output triggers Andon or fallback",
            "Graphify absence does not block consumer runs",
            "No silent install",
            "No silent indexing",
        ],
        "skills/implementaudit/references/repo-state-comparison.md": [
            "Commit Granularity",
            "atomic but not microscopic",
            "one commit per coherent owner/source repair",
            "Do not commit for proof-only local RC",
        ],
        "skills/implementaudit/references/phase-design.md": [
            "Broad Rewrite Threshold",
            "Owner decision is required",
            "strangler/mixed route",
            "Reject scope creep",
        ],
        "skills/implementaudit/references/lean-operating-discipline.md": [
            "5 Whys Loop-Exit Protocol",
            "5 Whys is proportional, not infinite",
            "unavailable external information",
            "Do not create arbitrary try caps",
        ],
        "skills/implementaudit/references/plan-lifecycle.md": [
            "Read-Only `plans/` Output Lane",
            "current-state excerpts",
            "planned-at SHA",
            "STOP conditions",
            "zero source mutation",
        ],
        "skills/implementaudit/templates/read-only-plan.md": [
            "Read-Only Plan Template",
            "Planned At",
            "Current State Excerpts",
            "Drift Check",
            "Rejected / Deferred Findings",
        ],
    }
    for owner, tokens in owners.items():
        owner_path = repo_root / owner
        if not owner_path.is_file():
            raise SystemExit(f"{path}: missing restored safeguard owner/source: {owner}")
        owner_text = owner_path.read_text(encoding="utf-8")
        owner_lower = owner_text.lower()
        for token in tokens:
            if token.lower() not in owner_lower:
                raise SystemExit(f"{owner}: missing restored safeguard token: {token}")

sys.stdout.write(
    f"check-skill-bootstrap-budget: ok ({line_count} lines, {byte_count} bytes; "
    f"budget {max_lines} lines/{max_bytes} bytes)\n"
)
PY
