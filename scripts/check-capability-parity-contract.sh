#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-capability-parity-contract: %s\n' "$*" >&2
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
import sys
from pathlib import Path


def require_file(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"missing required file: {path}")
    return p.read_text(encoding="utf-8")


def require_dir(path: str) -> None:
    if not Path(path).is_dir():
        raise SystemExit(f"missing required directory: {path}")


def require(text: str, path: str, token: str) -> None:
    if token not in text:
        raise SystemExit(f"{path}: missing required token: {token}")


required_files = [
    "docs/audits/INDEX.md",
    "docs/audits/RETENTION.md",
    "skills/implementaudit/SKILL.md",
    "skills/implementaudit/references/plan-lifecycle.md",
    "skills/implementaudit/references/sidecars.md",
    "skills/implementaudit/references/repo-state-comparison.md",
    "skills/implementaudit/templates/read-only-plan.md",
    "skills/implementaudit/templates/final-report.md",
    "scripts/check-plan-quality-contract.sh",
    "scripts/check-dogfood-bootstrap-contract.sh",
    "scripts/check-installed-payload-self-contained.sh",
    "scripts/check-skill-bootstrap-budget.sh",
    "scripts/build-source-evidence-pack.sh",
    "tests/read-only-plans-lane.test.sh",
    "tests/source-evidence-pack-runnable.test.sh",
    "tests/source-evidence-pack.test.sh",
]
for path in required_files:
    require_file(path)

for path in [
    "fixtures/read-only-plans",
    "fixtures/secret-hygiene",
    "fixtures/dogfood-bootstrap",
]:
    require_dir(path)

plan_ref = require_file("skills/implementaudit/references/plan-lifecycle.md")
for token in [
    "Read-Only `plans/` Output Lane",
    "zero source mutation",
    "repo content as data",
    "never reproduce secret values",
    "prompt injection in repo/docs/issues/examples as a finding",
    "pass these rules into child-agent/reviewer prompts",
]:
    require(plan_ref, "skills/implementaudit/references/plan-lifecycle.md", token)

read_only_plan = require_file("skills/implementaudit/templates/read-only-plan.md")
for token in [
    "Planned At",
    "Current State Excerpts",
    "Drift Check",
    "STOP Conditions",
    "Commands You Will Need",
    "Done Criteria",
    "Rejected / Deferred Findings",
]:
    require(read_only_plan, "skills/implementaudit/templates/read-only-plan.md", token)

dogfood = require_file("skills/implementaudit/SKILL.md")
for token in [
    "Dogfood Bootstrap / Read Map",
    "Baseline the target repo first",
    "progressive disclosure",
    "Real-home installed skill readback is non-evidence",
    "temp `CODEX_HOME`",
]:
    require(dogfood, "skills/implementaudit/SKILL.md", token)

evidence_builder = require_file("scripts/build-source-evidence-pack.sh")
for token in [
    "RUN-VALIDATION.md",
    "skills/implementaudit/SKILL.md",
    "tests/source-evidence-pack.test.sh",
    "replace(b\"\\r\\n\", b\"\\n\")",
]:
    require(evidence_builder, "scripts/build-source-evidence-pack.sh", token)

for path in [
    "fixtures/read-only-plans/valid-handoff-plan.md",
    "fixtures/read-only-plans/read-only-zero-mutation.status",
    "fixtures/read-only-plans/read-only-audit-ledger.status",
    "fixtures/read-only-plans/negative-read-only-source-mutation.status",
    "fixtures/secret-hygiene/repo-ignore-previous-instructions.md",
    "fixtures/secret-hygiene/repo-print-env.md",
    "fixtures/secret-hygiene/repo-fake-secret.txt",
    "fixtures/secret-hygiene/negative-plan-reproduces-fake-secret.md",
    "fixtures/secret-hygiene/negative-child-prompt-missing-security-rules.md",
    "fixtures/dogfood-bootstrap/positive/baseline-first-transcript.jsonl",
    "fixtures/dogfood-bootstrap/negative/installed-readback-before-baseline-transcript.jsonl",
    "fixtures/dogfood-bootstrap/negative/chunking-readback-before-baseline-transcript.jsonl",
    "fixtures/dogfood-bootstrap/negative/real-home-readback-before-temp-home-transcript.jsonl",
]:
    require_file(path)

index = require_file("docs/audits/INDEX.md")
for token in [
    "generic active safeguards",
    "scripts/check-capability-parity-contract.sh",
]:
    require(index, "docs/audits/INDEX.md", token)

sys.stdout.write("check-capability-parity-contract: ok\n")
PY
