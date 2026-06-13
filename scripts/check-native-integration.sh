#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-native-integration: %s\n' "$*" >&2
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

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

require_text() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" || fail "missing in $file: $text"
}

runtime_forbidden='Donor Finding Format Contract|Advisor-only / read-only|Advisor-Only|advisor-only/read-only|advisor-only|external-advisor|donor-shaped slash mode|donor command identity|[Dd]onor|Improve Parity|Improve parity|Improve parity support reference|Category Surpass Contract|SURPASSED'
hit_file="$(mktemp)"
scan_targets=(skills)
if [ -d fixtures/audit-object-routing ]; then
  scan_targets+=(fixtures/audit-object-routing)
fi
scan_targets+=(fixtures/native-integration)
if grep -RInE "$runtime_forbidden" "${scan_targets[@]}" >"$hit_file"; then
  cat "$hit_file" >&2
  rm -f "$hit_file"
  fail "runtime still contains standalone comparator-lane wording"
fi
rm -f "$hit_file"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required for native-integration hygiene checks"
fi

"${py_cmd[@]}" - <<'PY'
import re
import sys
from pathlib import Path

allowed = ("REDACTED", "EXAMPLE", "DO_NOT_USE", "credential-type-only")
patterns = [
    (re.compile(r"\bhunter2\b", re.I), "toy password that normalizes secret copying"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS-looking access key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "GitHub-looking token"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API-looking secret key"),
    (re.compile(r"password\s+(?:is|=|:)\s*['\"]?[^'\"\n<` ]{6,}", re.I), "realistic password value"),
    (re.compile(r"api[_-]?key\s*(?:=|:)\s*['\"]?[A-Za-z0-9_./+=-]{16,}", re.I), "realistic API key value"),
]

roots = [Path("fixtures"), Path("docs/portal"), Path("skills")]
files = [Path("README.md"), Path("AGENTS.md")]
for root in roots:
    if root.is_dir():
        files.extend(p for p in root.rglob("*") if p.is_file())

violations = []
for path in files:
    if not path.is_file():
        continue
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        continue
    for lineno, line in enumerate(lines, 1):
        if any(token in line for token in allowed):
            continue
        for pattern, label in patterns:
            if pattern.search(line):
                violations.append(f"{path.as_posix()}:{lineno}: {label}")

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)
PY

hit_file="$(mktemp)"
if grep -RInE '/implementaudit (quick|deep|security|next|features|roadmap)' skills \
  | grep -v "Do not add" \
  | grep -v "Do not advertise" \
  >"$hit_file"; then
  cat "$hit_file" >&2
  rm -f "$hit_file"
  fail "runtime advertises comparator-shaped command identity"
fi
rm -f "$hit_file"

require_text skills/references/audit-category-matrix.md "native IMPLEMENTAUDIT classifier"
require_text skills/references/audit-category-matrix.md "tdqyq-audit-object"
require_text skills/references/audit-category-matrix.md "ydqyq-audit-action"
require_text skills/references/audit-category-matrix.md "DMAIC for brownfield"
require_text skills/references/audit-category-matrix.md "DMADV direction/design routing"
require_text skills/references/audit-category-matrix.md "Smoke A/B"
require_text skills/references/audit-category-matrix.md "Andon"
require_text skills/references/audit-category-matrix.md "final-audit status"
require_text skills/references/audit-category-matrix.md "Finding Row Contract"
require_text skills/references/audit-playbook.md "## Finding Row Contract"
require_text skills/templates/THINKING.md "Audit category matrix"
require_text skills/templates/phase-goal.txt "Audit categories:"
require_text skills/templates/PROTOCOL.md "default category matrix"

fixtures=(
  fixtures/native-integration/p0-correctness-native-route.md
  fixtures/native-integration/p0-security-native-route.md
  fixtures/native-integration/p0-performance-native-route.md
  fixtures/native-integration/p0-test-coverage-native-route.md
  fixtures/native-integration/p0-architecture-native-route.md
  fixtures/native-integration/p0-dependencies-native-route.md
  fixtures/native-integration/p0-dx-tooling-native-route.md
  fixtures/native-integration/p0-docs-handoff-native-route.md
  fixtures/native-integration/p0-direction-native-route.md
  fixtures/native-integration/single-plan-native-route.md
)

for fixture in "${fixtures[@]}"; do
  require_file "$fixture"
  for text in \
    "Native route:" \
    "tdqyq-audit-object" \
    "ydqyq-audit-action" \
    "Owner/source" \
    "Smoke A/B" \
    "Andon" \
    "Final audit" \
    "Finding title" \
    "Category" \
    "Evidence" \
    "Impact" \
    "Effort" \
    "Risk" \
    "Confidence" \
    "Fix sketch / implementation route" \
    "Acceptance criteria" \
    "Verification" \
    "Rollback / Plan Closure" \
    "Rejected/deferred rationale" \
    "Remaining risk" \
    "Route:" \
    "Negative control:" \
    "False parity to reject"
  do
    require_text "$fixture" "$text"
  done
done

require_text fixtures/native-integration/p0-correctness-native-route.md "wrong result"
require_text fixtures/native-integration/p0-correctness-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-security-native-route.md "no-secret"
require_text fixtures/native-integration/p0-security-native-route.md "repo-content-as-data"
require_text fixtures/native-integration/p0-security-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-performance-native-route.md "N+1"
require_text fixtures/native-integration/p0-performance-native-route.md "measurement-or-static-evidence"
require_text fixtures/native-integration/p0-performance-native-route.md "CI-feedback"
require_text fixtures/native-integration/p0-performance-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-test-coverage-native-route.md "characterization-test-first"
require_text fixtures/native-integration/p0-test-coverage-native-route.md "missing verification"
require_text fixtures/native-integration/p0-test-coverage-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-architecture-native-route.md "god module"
require_text fixtures/native-integration/p0-architecture-native-route.md "owner/source boundary"
require_text fixtures/native-integration/p0-architecture-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-architecture-native-route.md "DMADV"
require_text fixtures/native-integration/p0-dependencies-native-route.md "deprecated/EOL"
require_text fixtures/native-integration/p0-dependencies-native-route.md "lockfile drift"
require_text fixtures/native-integration/p0-dependencies-native-route.md "no hidden install/update"
require_text fixtures/native-integration/p0-dependencies-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-dx-tooling-native-route.md "typecheck"
require_text fixtures/native-integration/p0-dx-tooling-native-route.md "lint"
require_text fixtures/native-integration/p0-dx-tooling-native-route.md "onboarding"
require_text fixtures/native-integration/p0-dx-tooling-native-route.md "AGENTS"
require_text fixtures/native-integration/p0-dx-tooling-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-docs-handoff-native-route.md "contradicts runtime"
require_text fixtures/native-integration/p0-docs-handoff-native-route.md "public-claim truth"
require_text fixtures/native-integration/p0-docs-handoff-native-route.md "DMAIC"
require_text fixtures/native-integration/p0-direction-native-route.md "what next"
require_text fixtures/native-integration/p0-direction-native-route.md "DMADV"
require_text fixtures/native-integration/p0-direction-native-route.md "separated from defects"
require_text fixtures/native-integration/p0-direction-native-route.md "owner/source"
require_text fixtures/native-integration/p0-direction-native-route.md "generic idea-slop"
require_text fixtures/native-integration/p0-direction-native-route.md "Acceptance criteria"

generic_negative=fixtures/native-integration/negative-generic-roadmap.md
require_file "$generic_negative"
for text in \
  "Negative fixture" \
  "generic roadmap prose" \
  "Reject" \
  "DMADV direction/design" \
  "repo evidence" \
  "owner/source" \
  "separated from defects" \
  "acceptance criteria" \
  "verification" \
  "rollback"
do
  require_text "$generic_negative" "$text"
done

single_plan=fixtures/native-integration/single-plan-native-route.md
for text in \
  "Exact single-plan native route" \
  "user already knows the desired plan" \
  "skips broad category survey" \
  "recon investigates only enough" \
  "ambiguity is resolved from repo files first" \
  "exactly one self-contained native IMPLEMENTAUDIT phase/plan artifact" \
  "owner/source" \
  "drift check" \
  "scope/non-scope" \
  "STOP conditions" \
  "expected outputs" \
  "verification commands" \
  "rollback/removal path" \
  "evidence boundary" \
  "does not use root plans/ as canonical" \
  "does not use external-lane phrasing"
do
  require_text "$single_plan" "$text"
done

canary=fixtures/native-integration/transcripts/audit-object-route-canary-transcript.md
require_file "$canary"
for text in \
  "AUDIT_START" \
  "AUDIT_VERIFY" \
  "AUDIT_GAPS" \
  "AUDIT_COMPLETE" \
  "IMPLEMENTAUDIT_RUN_COMPLETE" \
  "correctness / bugs" \
  "security / privacy" \
  "performance / scale" \
  "tests / validation" \
  "architecture / tech debt" \
  "dependencies / migrations" \
  "DX / tooling" \
  "docs / handoff" \
  "direction / design / next" \
  "quick/bounded" \
  "deep pressure" \
  "security pressure" \
  "branch/diff" \
  "dispatch-review" \
  "reconcile" \
  "issue publication deferred"
do
  require_text "$canary" "$text"
done

printf 'check-native-integration: ok\n'
