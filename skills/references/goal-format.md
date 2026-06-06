# Goal Format

Use this reference when goal synthesis mode needs to return a ready-to-paste
goal runner handoff.

## Embedded governance rule

If the current session is already inside a supplied `/goal using /implementaudit`
run, do not print a second `/goal`. Continue governing the active target.

## Ready-to-paste shape

```text
/goal Using /implementaudit, in <repo path>, implement <bounded target>.

Input basis:
- <audit/handoff/checklist/review/gap source>

Owner/source candidates:
- <files/artifacts to inspect first>

Required phases:
- Phase 1: <smallest coherent slice>
- Phase 2: <next coherent slice, if needed>

Safety boundaries:
- No commit.
- No push.
- No tag.
- No release.
- No publication.
- No provenance claim.
- No optional tool install/index/setup/export unless separately authorized.

Required checks:
- Smoke A: <baseline command or inspection>
- Smoke B: <post-change command or inspection>
- Complete repo-state comparison: <baseline ref or reason unavailable>

Final audit:
- Print AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE.
- Print AUDIT_HANDOFF only when gaps, blockers, or handoff-required caveats remain.
- Close every ledger item terminally.
```

Slash commands fire only from user input. Agent text containing `/goal ...` is a
handoff for the user to paste, not automatic dispatch.

## Full phased handoff condition

Use this fuller form when Stage 5 produced `.IMPLEMENTAUDIT` runtime artifacts:

```text
/goal Using /implementaudit, in <repo path>, execute the phased audit plan in
.IMPLEMENTAUDIT/ROADMAP.md.

First read .IMPLEMENTAUDIT/PROTOCOL.md, .IMPLEMENTAUDIT/STATE.md,
.IMPLEMENTAUDIT/THINKING.md, and the applicable .IMPLEMENTAUDIT/phases/phase-N.md
files. Execute phases sequentially. For each phase, print
IMPLEMENTAUDIT_PHASE_START, then do the work, then print
IMPLEMENTAUDIT_PHASE_VERIFY with acceptance criteria, Smoke B, evidence type,
complete repo-state comparison, and remaining risk. Print AGENTS_UPDATE_DECISION
and IMPLEMENTAUDIT_PHASE_DONE before moving to the next phase.

If a phase criterion fails, follow the failure protocol in
.IMPLEMENTAUDIT/PROTOCOL.md and use FAILURE_PROBE, FAILURE_ESCALATE, or
FAILURE_HANDOFF as required. Do not print IMPLEMENTAUDIT_RUN_COMPLETE after
FAILURE_HANDOFF.

After the last phase, run the final audit in .IMPLEMENTAUDIT/PROTOCOL.md:
re-read ROADMAP.md, re-run deduplicated mandatory checks, spot-check
acceptance criteria, check deliverables against the baseline with complete
working-tree evidence, and write an audit-fix phase if gaps are found. Print
AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE. Print AUDIT_HANDOFF only
when gaps, blockers, or handoff-required caveats remain; never print it with
IMPLEMENTAUDIT_RUN_COMPLETE.

Done only when IMPLEMENTAUDIT_RUN_COMPLETE appears after AUDIT_COMPLETE, every
phase has IMPLEMENTAUDIT_PHASE_DONE, every ledger item is terminally closed, and
no FAILURE_HANDOFF or AUDIT_HANDOFF appears in this run.
```

This is still an audit-governed handoff. It does not authorize commit, push,
tag, release, publication, provenance, optional tool install/index/setup/export,
or host install verification unless the user separately and explicitly grants
those actions and repo policy allows them.
