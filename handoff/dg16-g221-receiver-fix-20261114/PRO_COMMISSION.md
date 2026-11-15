# ChatGPT Pro executor commission: DG16–DG18 continuity (draft for the owner to send)

You are the ChatGPT Pro execution successor for IMPLEMENTAUDIT DG16–DG18 in `theislampill/IMPLEMENTAUDIT.md`. The integration PR is #255, whose head is `5277eb82bac6c10e190238afb54eda112eba284b`. Codex is unavailable until 2026-11-20. Work only with tools you can actually see and use in this conversation.

## 1. Verify your capabilities first, and report them
- List the GitHub tools exposed to you. Say which you can call successfully: read file/commit, create blob/tree/commit, create branch, guarded ref update, read workflow runs/jobs/artifacts, and whether you can trigger a workflow.
- If you are in Work, state whether execution is in the cloud or has permissioned access to the owner's desktop. Do not assume either.
- You do not have Codex's native identity, the owner's private keys, or Root authority unless the owner grants it in writing in this conversation.

## 2. Independently receive the G221 correction
- Fetch branch `engineering/dg16-g221-receiver-fix-20261114` and read `handoff/dg16-g221-receiver-fix-20261114/READ_FIRST.md`.
- Verify that commit `82f4c3d1a5ca85d88f8cb73672d7244dba4f3316` has parent `ce144b1d06f81bda3225b48d3bab32374515cff5` and tree `a7a17de3675fdbce11cc258b9bdc4aab49e8cded`.
- Verify that its diff from the parent is exactly the 7 listed files.
- Confirm from the source that `pending_relation.py`:
  - requires exact ordered equality with `CONTROL_NAMES` (58 and 54 names);
  - requires the exact `<runtime-bin>/python3` interpreter;
  - has no other predicate changed.
- Compare `CONTROL_NAMES` with the producers `tests/cognition-pending-durability.py` and `tests/cognition-pending-loader.py` at `205aeab7`, as far as your tools allow.
- Record PASS or FAIL with evidence. Do not trust the handoff's conclusions without checking them.

## 3. GitHub work you may do
- Read-only inspection, including runs, jobs and artifacts.
- Any further source correction on new `engineering/*` branches only. Use guarded, non-force ref creation, then read the result back.
- Before any write, inspect every workflow trigger in the target tree, and never create a branch that a workflow triggers on.
- Assess, as a written proposal, how the correction could be integrated selectively into PR #255. The G2 packet path does not exist on PR #255's head.

## 4. Do NOT, without a separate written owner grant naming the exact act
- Push any `pro/dg16-*host*` or `*control*` branch, or dispatch or re-run any workflow.
- Issue or adopt a recipient, author Root decisions, review selections or seals, or perform the 300-second Root consumption.
- Use keys, decrypt, replay UNKNOWN effects, merge, release, close issues, or claim original acceptance.
- Touch G131 WRITE0, G212/G213, 421189, or the spent DG17 Stage A episode (case-native-01, operation 9b871228…).

## 5. Root succession, for the owner to decide
The original protocol attributes these acts to Root (issuer thread `01a1cf82-cdd6-7053-b7b7-32f5c3d93d21`, author `/root`):
- recipient adoption;
- the four decision bodies;
- the candidate, review and composition seals;
- review selection;
- publication of the host branch;
- `ROOT_CONSUMPTION.json` in the live window;
- final acceptance.

The receivers check these as labels, not signatures. A successor therefore needs an explicit owner designation stating:
- the successor's identity label;
- which of these acts it may perform;
- for which G-number;
- whether historical records must name it instead of `/root`.

The independent live reviewer must be a distinct agent, not in `live_control.CURRENT_AUTHORS`.

## 6. What remains
| Item | Status |
|---|---|
| DG16 G221 | Steps 1–7 in READ_FIRST. A fresh recipient (owner-held key) and Root acts are required. |
| DG16 G132 → G3 | Not launched. G131's spent effects must not be reused. |
| DG17 | Stage A ran at 2026-11-14 23:30Z and stopped at its step 07 with no model turns. The cause is a driver defect; a fix exists locally on the owner's PC (`RECOVERY/DG17_STEP07`), not yet on GitHub. A new episode needs a new operation identity, a fresh owner approval and Codex model turns (available 2026-11-20, or with Codex credits). |
| DG18 | B2 and D18-1 are integrated. E/F, W-FULL, N1, OR, C02 and cold receiving all require Codex-native operation. N1 also requires its real continuity owner selection. |

Report what you verified, what you changed (with exact commit, tree and readback), and what is still blocked and why.
