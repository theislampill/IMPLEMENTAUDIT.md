IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 - Mini source milestone proof
Task: Prove a deterministic mini audit loop can validate a deliverable
Type: brownfield / proof-fixture
Run root: .IMPLEMENTAUDIT/runs/mini-e2e-proof
Baseline ref: mini-baseline-ref
Owner/source: fixtures/e2e-mini-audit-loop/phase-1.md
Audit object: .IMPLEMENTAUDIT/runs/mini-e2e-proof/ROADMAP.md
Auditing operation: deterministic source-repo mini loop
Terminal object state to prove: repo-state deliverable check sees a new proof file
Thinking ref: .IMPLEMENTAUDIT/runs/mini-e2e-proof/THINKING.md
Mandatory commands: bash skills/implementaudit/scripts/validate-phase.sh fixtures/e2e-mini-audit-loop/phase-1.md
Acceptance criteria: 2
Evidence required: validate-phase output, repo-state deliverable output
Depends on phases: none

## Why

This fixture proves a tiny audit loop can read a phase spec, validate it, create
one deliverable, and verify the deliverable against the complete working tree.

## Current state excerpts

- `skills/implementaudit/scripts/validate-phase.sh` requires IMPLEMENTAUDIT markers, owner/source, baseline, current-state excerpts, expected command outputs, rollback, and maintenance notes.
- `skills/implementaudit/scripts/repo-state.sh deliverable <baseline> <path>` reports a new untracked deliverable as present.

## Work

- Copy this phase spec into a temporary run root for the mini-loop test.
- Create `src-mini-proof.txt` in the temporary repository.

## Acceptance criteria (all must pass - verify each in transcript)

- `bash skills/implementaudit/scripts/validate-phase.sh fixtures/e2e-mini-audit-loop/phase-1.md` exits 0.
- `bash .IMPLEMENTAUDIT/runs/mini/repo-state.sh deliverable <baseline> src-mini-proof.txt` reports present.

## Mandatory commands (run each; include expected success shape, surface last ~10 lines + exit code in transcript)

- bash skills/implementaudit/scripts/validate-phase.sh fixtures/e2e-mini-audit-loop/phase-1.md - property: structural; scope: spec shape only, not work correctness; expected: exit 0 with `validate-phase: ok`.
- bash .IMPLEMENTAUDIT/runs/mini/repo-state.sh deliverable <baseline> src-mini-proof.txt - property: behavioral; scope: the deliverable file exists in the working tree after the work; expected: exit 0 with `present`.

## Evidence required in transcript

- validate-phase command output with exit 0.
- repo-state deliverable output with exit 0.

## Rollback / defer path

Delete the temporary repository created by the test trap. No tracked source
rollback is required for the runtime fixture.

## Graphify / ActiveGraph / Markdown fallback status

Graphify: skipped
ActiveGraph: skipped
Markdown fallback: yes

## Cleanliness override, if any

None.

## Maintenance notes

- Keep this fixture small; it is a deterministic fallback, not a full live
  model dogfood transcript.

## Notes

This source repo fixture intentionally uses a temporary repo so it performs no
commit, push, release, issue creation, real-home install, publication, or
provenance action.

---

IMPLEMENTAUDIT_PHASE_VERIFY

Phase 1 acceptance criteria:
- [pass] validate-phase exits 0: validate-phase: ok
- [pass] repo-state deliverable reports present: present - untracked new file

Mandatory commands:
- validate-phase exit 0: validate-phase: ok

Cleanliness (.IMPLEMENTAUDIT/runs/mini/repo-state.sh added-lines mini-baseline-ref):
- Debug prints added: 0
- Session debug-markers added (todo/fixme/xxx): 0
- Dead imports added: 0

Sidecar: Graphify skipped; ActiveGraph skipped; Markdown fallback yes
Remaining risk: fixture only; no live model behavior claimed
Trust-prior count: 0
Re-verified count: 2

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: The fixture adds a test guard, not a durable repo instruction.
Scope: N/A
Evidence location: tests/e2e-mini-audit-loop.test.sh
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: none
Reason: No non-obvious user or project preference is learned by this fixture.
Evidence boundary: source repo fixture only

IMPLEMENTAUDIT_PHASE_DONE

Status: done
Evidence: validate-phase and repo-state checks pass in the test
Follow-up: none
