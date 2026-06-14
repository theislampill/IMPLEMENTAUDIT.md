#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

dest="$tmp/codex home/skills/implementaudit"
mkdir -p "$dest"
cp -R skills/implementaudit/. "$dest/"

for file in \
  SKILL.md \
  references/planning-depth.md \
  references/phase-design.md \
  references/goal-format.md \
  references/transcript-contract.md \
  references/routing.md \
  references/repo-state-comparison.md \
  references/sidecars.md \
  references/child-agents.md \
  references/lean-operating-discipline.md \
  references/audit-category-matrix.md \
  references/audit-playbook.md \
  references/plan-lifecycle.md \
  scripts/claim-run.sh \
  scripts/detect-env.sh \
  scripts/detect-stack.sh \
  scripts/repo-state.sh \
  scripts/summarize-repo.sh \
  scripts/validate-audit-spec.sh \
  scripts/validate-phase.sh \
  scripts/validate-run-root.sh \
  scripts/custody-append.sh \
  templates/ROADMAP.md \
  templates/STATE.md \
  templates/THINKING.md \
  templates/phase-goal.txt \
  templates/child-agent-report.md \
  templates/final-report.md \
  templates/read-only-plan.md \
  templates/PROTOCOL.md \
  templates/sidecars.md \
  templates/tools.md \
  templates/context.md
do
  [ -f "$dest/$file" ] || {
    printf 'install-copy-smoke.test: missing copied file: %s\n' "$file" >&2
    exit 1
  }
done

# Verify the installed validator accepts a filled-in (non-placeholder) spec.
# The template has placeholder content by design and is not a valid target for
# content checks; use an inline smoke spec instead.
smoke_spec="$tmp/smoke-spec.md"
cat > "$smoke_spec" <<'SPEC'
IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — install smoke
Task: Verify installed validate-phase.sh accepts a filled spec
Type: smoke
Run root: .IMPLEMENTAUDIT/runs/install-smoke-abc123
Baseline ref: abc123def456
Owner/source: scripts/validate-phase.sh
Mandatory commands: bash scripts/validate-phase.sh smoke-spec.md
Acceptance criteria: 1
Evidence required: exit code 0
Depends on phases: none

## Why

Verify the installed validator script executes and accepts a valid spec.

## Current state excerpts

- Installed `scripts/validate-phase.sh` is present in the copied skill payload.
- This smoke spec is generated in a temporary directory and does not mutate repo source.

## Work

- Run validate-phase.sh against this spec

## Acceptance criteria (all must pass — verify each in transcript)

- validate-phase.sh exits 0 on this filled spec

## Mandatory commands (run each; surface last ~10 lines + exit code in transcript)

- bash scripts/validate-phase.sh smoke-spec.md — expected: exit 0 and prints validate-phase: ok

## Evidence required in transcript

- exit code 0 from validate-phase.sh

## Rollback / defer path

No rollback needed; this is a read-only validation smoke.

## Graphify / ActiveGraph / Markdown fallback status

Graphify: absent
ActiveGraph: absent
Markdown fallback: yes

## Cleanliness override, if any

## Maintenance notes

- Keep this smoke spec aligned with validate-phase.sh structural requirements.

## Notes

Install smoke spec; not a real phase.

---

IMPLEMENTAUDIT_PHASE_VERIFY

Phase 1 acceptance criteria:
- [pass] validate-phase.sh exits 0: confirmed

Mandatory commands:
- bash scripts/validate-phase.sh smoke-spec.md exit 0: ok

Cleanliness:
- Debug prints added: 0
- Session debug-markers added (todo/fixme/xxx): 0
- Dead imports added: 0

Sidecar: Graphify skipped; ActiveGraph skipped; Markdown fallback yes
Remaining risk: none
Trust-prior count: 0
Re-verified count: 1

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: Smoke test only.
Scope: N/A
Evidence location: N/A
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: none
Reason: N/A
Evidence boundary: N/A

IMPLEMENTAUDIT_PHASE_DONE

Status: done
Evidence: exit 0
Follow-up: none
SPEC

bash "$dest/scripts/validate-phase.sh" "$smoke_spec"

printf 'install-copy-smoke.test: ok\n'
