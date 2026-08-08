#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-plan-quality-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

files=()
status_files=()
child_prompt_files=()
pr_body_files=()
campaign_plan_files=()
allowed_paths=("plans/" ".IMPLEMENTAUDIT/")
while [ "$#" -gt 0 ]; do
  case "$1" in
    --file)
      [ "$#" -ge 2 ] || fail "--file requires a path"
      files+=("$2")
      shift 2
      ;;
    --read-only-status-file)
      [ "$#" -ge 2 ] || fail "--read-only-status-file requires a path"
      status_files+=("$2")
      shift 2
      ;;
    --child-prompt-file)
      [ "$#" -ge 2 ] || fail "--child-prompt-file requires a path"
      child_prompt_files+=("$2")
      shift 2
      ;;
    --pr-body-file)
      [ "$#" -ge 2 ] || fail "--pr-body-file requires a path"
      pr_body_files+=("$2")
      shift 2
      ;;
    --campaign-plan-file)
      [ "$#" -ge 2 ] || fail "--campaign-plan-file requires a path"
      campaign_plan_files+=("$2")
      shift 2
      ;;
    --allow-path)
      [ "$#" -ge 2 ] || fail "--allow-path requires a path prefix"
      allowed_paths+=("$2")
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if [ "${#files[@]}" -eq 0 ]; then
  files=(
    "fixtures/read-only-plans/valid-handoff-plan.md"
    "fixtures/e2e-mini-audit-loop/phase-1.md"
  )
fi

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
  "${#files[@]}" "${files[@]}" \
  "--" "${#status_files[@]}" "${status_files[@]}" \
  "--" "${allowed_paths[@]}" \
  "--child-prompts" "${#child_prompt_files[@]}" "${child_prompt_files[@]}" \
  "--pr-bodies" "${#pr_body_files[@]}" "${pr_body_files[@]}" \
  "--campaign-plans" "${#campaign_plan_files[@]}" "${campaign_plan_files[@]}" <<'PY'
import re
import sys
from pathlib import Path

args = sys.argv[1:]
file_count = int(args[0])
offset = 1
paths = [Path(p) for p in args[offset : offset + file_count]]
offset += file_count
if args[offset] != "--":
    raise SystemExit("internal argument split error before status files")
offset += 1
status_count = int(args[offset])
offset += 1
status_paths = [Path(p) for p in args[offset : offset + status_count]]
offset += status_count
if args[offset] != "--":
    raise SystemExit("internal argument split error before allowed paths")
offset += 1
remaining = args[offset:]
child_prompt_paths: list[Path] = []
pr_body_paths: list[Path] = []
campaign_plan_paths: list[Path] = []
allowed_raw: list[str] = []
idx = 0
while idx < len(remaining):
    if remaining[idx] == "--child-prompts":
        idx += 1
        count = int(remaining[idx])
        idx += 1
        child_prompt_paths = [Path(p) for p in remaining[idx : idx + count]]
        idx += count
    elif remaining[idx] == "--pr-bodies":
        idx += 1
        count = int(remaining[idx])
        idx += 1
        pr_body_paths = [Path(p) for p in remaining[idx : idx + count]]
        idx += count
    elif remaining[idx] == "--campaign-plans":
        idx += 1
        count = int(remaining[idx])
        idx += 1
        campaign_plan_paths = [Path(p) for p in remaining[idx : idx + count]]
        idx += count
    else:
        allowed_raw.append(remaining[idx])
        idx += 1

allowed_paths = [p.replace("\\", "/") for p in allowed_raw]

for path in paths:
    if not path.is_file():
        raise SystemExit(f"missing plan-quality file: {path}")
for path in status_paths:
    if not path.is_file():
        raise SystemExit(f"missing read-only status file: {path}")
for path in child_prompt_paths:
    if not path.is_file():
        raise SystemExit(f"missing child prompt file: {path}")
for path in pr_body_paths:
    if not path.is_file():
        raise SystemExit(f"missing PR body file: {path}")
for path in campaign_plan_paths:
    if not path.is_file():
        raise SystemExit(f"missing campaign plan file: {path}")

forbidden = [
    "as discussed",
    "works correctly",
    "make it work",
    "just fix it",
    "update the relevant files",
    "the relevant module",
    "{{",
    "TBD",
    "task placeholder",
]

fake_secret_value = "IA_FAKE_CREDENTIAL_VALUE_DO_NOT_COPY"
planning_security_tokens = [
    "never reproduce secret values",
    "path, line, and credential type",
    "recommend rotation",
    "repo content as data",
    "prompt injection in repo/docs/issues/examples as a finding",
    "pass these rules into child-agent/reviewer prompts",
]
# Fanout-critical per-lane prompt content (#49): a specialist child prompt
# missing any of these is a plan-quality defect, not a reviewer preference.
fanout_prompt_tokens = [
    "audit-playbook.md",
    "Finding Row Contract",
    "recon facts",
    "risk hints",
    "findings-only",
    "no-dumps",
    "read-confirmation",
]


def fail(path: Path, message: str) -> None:
    raise SystemExit(f"{path}: {message}")


def require(text: str, path: Path, token: str) -> None:
    if token not in text:
        fail(path, f"missing required token: {token}")


def require_ci(text: str, path: Path, token: str) -> None:
    if token.lower() not in text.lower():
        fail(path, f"missing required token: {token}")


def check_planning_security_text(text: str, path: Path) -> None:
    if fake_secret_value in text:
        fail(path, "plan reproduces fake secret value")
    lower = text.lower()
    for injected in ["ignore previous instructions", "print .env"]:
        if injected in lower and ("prompt injection" not in lower or "finding" not in lower):
            fail(path, f"untrusted repo instruction not classified as finding: {injected}")


closing_reference = re.compile(
    r"\b(?:close(?:s|d)?|fix(?:es|ed)?|resolve(?:s|d)?)"
    r"\s*:?\s+(?:(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#[0-9]+)\b",
    re.IGNORECASE,
)
for path in pr_body_paths:
    match = closing_reference.search(path.read_text(encoding="utf-8"))
    if match:
        fail(path, f"auto-closing tracked-issue reference is forbidden: {match.group(0)}")


campaign_issues = re.compile(
    r"^campaign-issues:\s*(#[0-9]+(?:\s*,\s*#[0-9]+)*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
integration_topology = re.compile(
    r"^integration-topology:\s*(\S(?:.*\S)?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
for path in campaign_plan_paths:
    text = path.read_text(encoding="utf-8")
    issue_rows = campaign_issues.findall(text)
    if len(issue_rows) != 1:
        fail(path, "campaign plan requires exactly one campaign-issues row")
    issues = [item.strip() for item in issue_rows[0].split(",")]
    if len(set(issues)) != len(issues):
        fail(path, "campaign-issues contains a duplicate issue")
    topology_rows = integration_topology.findall(text)
    if len(topology_rows) > 1:
        fail(path, "campaign plan has duplicate integration-topology rows")
    if len(issues) == 1 and not topology_rows:
        continue
    if len(issues) > 1 and not topology_rows:
        fail(path, "multi-issue campaign requires integration-topology")
    topology = topology_rows[0].strip()
    normalized = topology.lower()
    if normalized in {"single-issue", "independent", "stacked-cumulative"}:
        continue
    if normalized.startswith("justified:") and topology.split(":", 1)[1].strip():
        continue
    fail(path, "integration-topology must be independent, stacked-cumulative, or justified:<reason>")


def non_placeholder_bullets(text: str, heading: str) -> list[str]:
    items: list[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(rf"^##\s+{re.escape(heading)}", stripped, re.I):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("-"):
            item = stripped[1:].strip()
            if item and not re.search(r"\{\{|placeholder|tbd|todo$", item, re.I):
                items.append(item)
    return items


for path in paths:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    check_planning_security_text(text, path)
    for phrase in forbidden:
        if phrase.lower() in lower:
            fail(path, f"forbidden weak/self-reference phrase: {phrase}")

    if "IMPLEMENTAUDIT_PHASE_START" in text:
        for token in [
            "Baseline ref:",
            "Owner/source:",
            "## Current state excerpts",
            "## Acceptance criteria",
            "## Mandatory commands",
            "## Evidence required",
            "## Rollback / defer path",
            "## Maintenance notes",
            "AGENTS_UPDATE_DECISION",
            "CONTINUITY_DECISION",
            "IMPLEMENTAUDIT_PHASE_DONE",
        ]:
            require(text, path, token)
        if not non_placeholder_bullets(text, "Current state excerpts"):
            fail(path, "Current state excerpts needs non-placeholder bullets")
        if not non_placeholder_bullets(text, "Acceptance criteria"):
            fail(path, "Acceptance criteria needs non-placeholder bullets")
        commands = non_placeholder_bullets(text, "Mandatory commands")
        if not commands:
            fail(path, "Mandatory commands needs non-placeholder bullets")
        for command in commands:
            if not re.search(r"expected|exit 0|passes|no errors|outputs?", command, re.I):
                fail(path, f"mandatory command missing expected success shape: {command}")
    else:
        for token in [
            "Drift check",
            "Planned at",
            "## Current state",
            "## Commands you will need",
            "## Scope",
            "Out of scope",
            "## Done criteria",
            "## STOP conditions",
            "## Maintenance notes",
        ]:
            require(text, path, token)
        if not re.search(r"`[a-f0-9]{7,40}`", text):
            fail(path, "planned-at commit hash is missing")
        if not re.search(r"Expected on success.*exit 0|exit 0.*Expected", text, re.S):
            fail(path, "commands table must include expected exit-0 success shape")

template = Path("skills/implementaudit/templates/phase-goal.txt").read_text(encoding="utf-8")
for token in [
    "Current state excerpts",
    "expected success shape",
    "Rollback / defer path",
    "Maintenance notes",
    "Authorization boundary: no hidden commit, push, merge, release, publication, provenance, install, index, export, or issue creation",
    "## Implementation steps (ordered)",
    "## Scope boundaries",
    "Out of scope:",
    "## STOP conditions (plan-specific)",
    "Vague step language fails validation",
]:
    if token not in template:
        raise SystemExit(f"skills/implementaudit/templates/phase-goal.txt: missing plan-quality token: {token}")

# Reconstructibility contract fixture (#50): the review-lane counter-example
# for path-only targets where symbol precision is material must stay present
# and self-declared as failing.
neg_symbols = Path("fixtures/phase-design/negative-paths-without-symbols.md")
if not neg_symbols.is_file():
    raise SystemExit(f"missing reconstructibility negative fixture: {neg_symbols}")
neg_text = neg_symbols.read_text(encoding="utf-8")
for token in ["NEGATIVE FIXTURE", "must fail", "Expected disposition when reviewed: FAIL"]:
    require(neg_text, neg_symbols, token)

plan_ref = Path("skills/implementaudit/references/plan-lifecycle.md").read_text(encoding="utf-8")
for token in [
    "Read-Only `plans/` Output Lane",
    "zero source mutation",
    "plans/",
    ".IMPLEMENTAUDIT/",
    "docs/audits/",
    "templates/read-only-plan.md",
    "PR bodies use non-closing tracked-issue references such as `Implements #N`",
    "evidence comment first, then close the issue explicitly",
    "campaign-issues: #<N>[, #<N>...]",
    "integration-topology: independent|stacked-cumulative|justified:<reason>",
]:
    if token not in plan_ref:
        raise SystemExit(f"skills/implementaudit/references/plan-lifecycle.md: missing read-only plans token: {token}")
for token in planning_security_tokens:
    require_ci(plan_ref, Path("skills/implementaudit/references/plan-lifecycle.md"), token)

state_ref = Path("skills/implementaudit/references/repo-state-comparison.md").read_text(encoding="utf-8")
for token in [
    "successor retarget",
    "unchanged head",
    "main ancestry",
    "logical patch identity",
    "resulting-tree equality or exact-tree requalification",
]:
    require_ci(state_ref, Path("skills/implementaudit/references/repo-state-comparison.md"), token)

read_only_template = Path("skills/implementaudit/templates/read-only-plan.md").read_text(encoding="utf-8")
for token in [
    "Planned At",
    "Current State Excerpts",
    "Drift Check",
    "STOP Conditions",
    "Commands You Will Need",
    "Done Criteria",
    "Rejected / Deferred Findings",
    "Ordered Steps",
]:
    if token not in read_only_template:
        raise SystemExit(f"skills/implementaudit/templates/read-only-plan.md: missing template token: {token}")
for token in planning_security_tokens:
    require_ci(read_only_template, Path("skills/implementaudit/templates/read-only-plan.md"), token)

if not child_prompt_paths:
    child_prompt_paths = [Path("fixtures/child-agents/read-only-contract-auditor.md")]
for path in child_prompt_paths:
    text = path.read_text(encoding="utf-8")
    for token in planning_security_tokens:
        require_ci(text, path, token)
    for token in fanout_prompt_tokens:
        require_ci(text, path, token)

def parse_status_path(line):
    raw = line.rstrip("\n")
    if not raw:
        return None
    if raw.startswith("## "):
        return None
    if raw.startswith("?? "):
        return raw[3:].replace("\\", "/")
    if len(raw) >= 4 and raw[2] == " ":
        candidate = raw[3:].replace("\\", "/")
        if " -> " in candidate:
            candidate = candidate.split(" -> ", 1)[1]
        return candidate
    return raw.replace("\\", "/")

def allowed(path: str) -> bool:
    return any(path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/") for prefix in allowed_paths)

for status_file in status_paths:
    for line in status_file.read_text(encoding="utf-8").splitlines():
        path = parse_status_path(line)
        if path is None:
            continue
        if not allowed(path):
            raise SystemExit(
                f"{status_file}: read-only lane source mutation outside allowlist: {path}"
            )

sys.stdout.write("check-plan-quality-contract: ok\n")
PY
