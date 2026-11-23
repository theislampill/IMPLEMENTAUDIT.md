# P06 L5 audit-fix 1

IMPLEMENTAUDIT_PHASE_START
Task: Repair only blocking finding P06-CASEFOLD-01.
Type: brownfield
Run root: .IMPLEMENTAUDIT/runs/dg17-p06-exact-candidate-audit-fix-convergence-n8liZr
Baseline ref: bb781f62f1e61542ad733e1b1b652d0831e2af24
Owner/source: release-catalog.json in the actual claimed run
Audit object: original P06 structural run
Depends on phases: 1

## Work

Preserve the complete failing catalog and both lower and audit captures. Replace
only the standalone role's colliding filename with Compatibility.zip. Repeat
the unchanged per-role and case-folded uniqueness checkers before a fresh L5 round.

## Implementation steps (ordered)

- Preserve the catalog and exact failing result in the run evidence.
- Change only the conflicting standalone filename in release-catalog.json.
- Repeat both checkers on the new bytes and preserve their actual outputs.

## Acceptance criteria

- [x] Exactly one owner field changes.
- [x] The previously successful per-role check still passes.
- [x] The formerly failing uniqueness check passes and its original witness remains intact.

## Rollback / defer path

Keep both versions and withhold closure on any new failure. This fix grants no publication authority.

IMPLEMENTAUDIT_PHASE_VERIFY
Both actual reruns exited zero. The original failing input and result remain in evidence.

IMPLEMENTAUDIT_PHASE_DONE
Status: done
