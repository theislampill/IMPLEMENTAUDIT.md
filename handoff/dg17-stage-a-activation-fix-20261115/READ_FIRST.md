# DG17 Stage A: preserved failure, driver correction and next episode

**Authority: NONE.** This branch is source-only and starts no workflow. It is based on PR #255 head `5277eb82`.

## What happened (preserved in `failed-stage-a-20261114/`)
- On 2026-11-14 at 23:30:12Z, Root launched the owner-approved Stage A: one fresh private context, at most two turns, 900 s.
- It stopped after 7.6 s at step 07 (`claim-run.sh --resume-controller … --boundary manual-resume`) with "predecessor/custody verification refused".
- It made **0 model turns, 0 thread starts and 0 H0/trust/qualifying effects**. It left 0 surviving processes, and no process escaped containment.
- Status: `STAGE_A_STOPPED_FIRST_REFUSAL_OR_UNKNOWN_NO_RETRY`. The grant and window are **spent**, so this episode must not be retried.
- Excluded from this branch: the isolated Codex home and its authentication material, the Codex binary and zip, and the AUTH_* route records.

## Cause: two defects in the driver (`stage_a.py`), not in the interlock or claim-run
1. Step 06 runs `--controller`, which only *prepares* a pending initialization. Step 07 needs the published controller, which only `--activate-controller` creates. `skills/implementaudit/references/continuity.md` requires `--controller` callers to activate explicitly. The driver never did.
2. The STATE file the driver writes cannot be activated. It uses an absolute `Run root` and `Phase: intake`, and has no `phases/phase-1.md` and no ROADMAP phase table.

## Correction (`driver/`)
`stage_a.step07.patch` (13 lines) produces `stage_a.fixed.py`, which:
- adds step 06a `--inspect-controller-initialization`;
- adds step 06b `--activate-controller --expected-initialization <token>`;
- writes a STATE that can be activated.

`stage_a.original.py` is the preimage.

## Evidence (`fix-evidence/`; offline, fresh clones of b0fcb565, no Codex)
| Case | Result |
|---|---|
| `repro-original` | Step 07 refuses identically |
| `fixed` | 06a, 06b and 07–10 all exit 0 |
| `adverse-no-activate` | Step 07 refuses |
| `adverse-stale-token` | 06b refuses |
| `adverse-tamper-after-prepare` | 06a refuses |

Steps after 10 need the native runtime.

## Next genuine DG17 operation
1. Re-pin. `approved-source-original/OPERATION_A.json` and `parent_launch_a.py` pin `stage_a.py`, so the fix produces a **new operation identity**.
2. The owner issues a **fresh approval** for the new operation. The limits stay as before: one fresh context, two turns at most, 900 s, Stage B only after independent post-A receiving, and `bypassPermissions` limited to the pinned Stop command.
3. Use a **new case path**. `case-native-01` exists, and stage_a refuses an existing case.
4. Run on the owner's Windows PC with the restored official Codex 0.166.0-alpha.5.1 (`6ca87057…`) in its isolated home. **This needs real Codex model turns.** The Codex allowance is exhausted until 2026-11-20 11:36, unless Codex credits are added.
5. Independent post-A receiving, then Stage B, then T12 and original14 receiving and custodian certification.

Claude can perform steps 1, 3 and 4 mechanically on the owner's PC once the owner grants it. The model turns themselves must be Codex.
