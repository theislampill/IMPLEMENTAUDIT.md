#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-safeguard-restoration: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

final_report="skills/implementaudit/templates/final-report.md"
sidecars_ref="skills/implementaudit/references/sidecars.md"
lean_ref="skills/implementaudit/references/lean-operating-discipline.md"
repo_state_ref="skills/implementaudit/references/repo-state-comparison.md"
phase_ref="skills/implementaudit/references/phase-design.md"
plan_ref="skills/implementaudit/references/plan-lifecycle.md"
routing_ref="skills/implementaudit/references/routing.md"
read_only_template="skills/implementaudit/templates/read-only-plan.md"
skill_file="skills/implementaudit/SKILL.md"
source_label_file=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --final-report)
      [ "$#" -ge 2 ] || fail "--final-report requires a path"
      final_report="$2"
      shift 2
      ;;
    --lean-ref)
      [ "$#" -ge 2 ] || fail "--lean-ref requires a path"
      lean_ref="$2"
      shift 2
      ;;
    --source-label-file)
      [ "$#" -ge 2 ] || fail "--source-label-file requires a path"
      source_label_file="$2"
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

"${py_cmd[@]}" - \
  "$final_report" \
  "$sidecars_ref" \
  "$lean_ref" \
  "$repo_state_ref" \
  "$phase_ref" \
  "$plan_ref" \
  "$routing_ref" \
  "$read_only_template" \
  "$skill_file" \
  "$source_label_file" <<'PY'
import re
import sys
from pathlib import Path

(
    final_report,
    sidecars_ref,
    lean_ref,
    repo_state_ref,
    phase_ref,
    plan_ref,
    routing_ref,
    read_only_template,
    skill_file,
    source_label_file,
) = [Path(p) if p else None for p in sys.argv[1:]]

def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"{path}: file is empty")
    return text

def require(path: Path, text: str, tokens: list[str]) -> None:
    lower = text.lower()
    for token in tokens:
        if token.lower() not in lower:
            raise SystemExit(f"{path}: missing required substance: {token}")

final_text = read(final_report)
require(final_report, final_text, [
    "Verdict",
    "Goal",
    "Input Basis",
    "Findings Ledger",
    "Changed Files",
    "Smoke A",
    "Smoke B",
    "Andon",
    "Hansei",
    "Commands Run",
    "Evidence Boundary",
    "Remaining Caveats",
    "Authorization Boundary",
    "Suggested Commit Message When No Commit Authorized",
    "Terminal Marker Order",
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
])

sidecar_text = read(sidecars_ref)
require(sidecars_ref, sidecar_text, [
    "Graphify is orientation only",
    "Live files remain proof",
    "stale output triggers Andon or fallback",
    "Graphify absence does not block consumer runs",
    "IMPLEMENTAUDIT self-maintenance may use Graphify",
    "no sidecar output enters the release package",
    "detect optional tools",
    "document install or usage commands",
    "install or configure tools only after explicit authorization",
    "index/export/write sidecar outputs only after separate explicit authorization",
    "No silent install",
    "No silent indexing",
])

lean_text = read(lean_ref)
require(lean_ref, lean_text, [
    "5 Whys Loop-Exit Protocol",
    "5 Whys is proportional, not infinite",
    "owner/source actionable",
    "unavailable external information",
    "expand scope beyond the audit object",
    "requires an owner decision",
    "Escalate to Andon or handoff",
    "Do not create arbitrary try caps",
])

repo_state_text = read(repo_state_ref)
require(repo_state_ref, repo_state_text, [
    "Commit Granularity",
    "Commit only with explicit authorization",
    "atomic but not microscopic",
    "one commit per coherent owner/source repair",
    "Do not commit for proof-only local RC",
    "when validation is red",
    "unrelated dirty work",
])

phase_text = read(phase_ref)
require(phase_ref, phase_text, [
    "Broad Rewrite Threshold",
    "more than one logical unit not named in the audit",
    "Owner decision is required",
    "strangler/mixed route",
    "Split phases",
    "Reject scope creep",
])

plan_text = read(plan_ref)
require(plan_ref, plan_text, [
    "Read-Only `plans/` Output Lane",
    "current-state excerpts",
    "planned-at SHA",
    "drift check",
    "STOP conditions",
    "commands with expected outputs",
    "test plan",
    "done criteria",
    "maintenance notes",
    "rejected or deferred findings",
    "Zero source mutation",
])

routing_text = read(routing_ref)
require(routing_ref, routing_text, [
    "LANE-ENTRY TRIGGER",
    "read-only `plans/` output lane",
    ".IMPLEMENTAUDIT/runs/",
    "never performs a mutating",
])

read_only_text = read(read_only_template)
require(read_only_template, read_only_text, [
    "Read-Only Plan Template",
    "Planned At",
    "Current State Excerpts",
    "Drift Check",
    "STOP Conditions",
    "Commands You Will Need",
    "Test Plan",
    "Done Criteria",
    "Maintenance Notes",
    "Rejected / Deferred Findings",
])

skill_text = read(skill_file)
skill_raw = skill_text.encode("utf-8")
if len(skill_text.splitlines()) > 450:
    raise SystemExit(f"{skill_file}: exceeds 450-line bootloader budget")
if len(skill_raw) > 22000:
    raise SystemExit(f"{skill_file}: exceeds 22000-byte bootloader budget")
require(skill_file, skill_text, [
    "Reference Load Map",
    "references/sidecars.md",
    "templates/final-report.md",
    "templates/read-only-plan.md",
    "LANE-ENTRY TRIGGER",
])

manual_detail_forbidden = [
    "one-commit-per-coherent-repair",
    "no-commit-for-proof-only-rc",
    "negative-missing-final-report",
    "negative-missing-5whys-exit",
]
skill_lower = skill_text.lower()
for token in manual_detail_forbidden:
    if token in skill_lower:
        raise SystemExit(f"{skill_file}: manual safeguard detail belongs outside bootloader: {token}")

def check_source_only_labels(paths: list[Path]) -> None:
    pattern = re.compile(
        r"(scripts/(?:check|verify)-[\w./*-]+|bash scripts/check-\*\.sh|bash scripts/verify-package\.sh)"
    )
    violations: list[str] = []
    for path in paths:
        text = read(path)
        for lineno, line in enumerate(text.splitlines(), 1):
            if not pattern.search(line):
                continue
            lower = line.lower()
            if "source repo only" not in lower and "not shipped in runtime payload" not in lower:
                violations.append(
                    f"{path.as_posix()}:{lineno}: source-only checker reference lacks label"
                )
    if violations:
        raise SystemExit("\n".join(violations))

if source_label_file:
    check_source_only_labels([source_label_file])
else:
    docs = [Path("skills/implementaudit/SKILL.md")]
    docs.extend(sorted(Path("skills/implementaudit/references").glob("*.md")))
    docs.extend(sorted(Path("skills/implementaudit/templates").glob("*.md")))
    check_source_only_labels(docs)

for helper in [
    Path("skills/implementaudit/scripts/validate-phase.sh"),
    Path("skills/implementaudit/scripts/validate-run-root.sh"),
    Path("skills/implementaudit/scripts/repo-state.sh"),
    Path("skills/implementaudit/scripts/custody-append.sh"),
]:
    if not helper.is_file():
        raise SystemExit(f"missing regression-fence helper: {helper}")

sys.stdout.write("check-safeguard-restoration: ok\n")
PY
