# DG16 read-only analysis (Fable 5.2, recorded by Opus 5.5), 2026-11-15

Paths are relative to `handoff/dg16-g221-root-execution-inputs/g220-custody/` on the branch `engineering/dg16-root-successor-inputs-20261115`.

## 1. G220 operator (`operator-static-source/`)
**What it is.** A WSL Python process, launched once per role (`live`, `terminal`). Each role runs ten fixed GitHub **read** steps: run, attempt, jobs, commit, workflow, artifacts, download, body, closing-run and closing-artifacts.
- The reads go through the Codex session's tools (`mcp__codex_apps__github_fetch` and `…download_workflow_artifact`). The steps are driven by `event_driver.js` / `codex_callbacks.js` over a file channel.

**Records it writes:**
- `PLAN.json`;
- four records per step: RESERVATION, INTENT, RESULT_NOTE, RECEIVING;
- `ARTIFACT.zip`, `PUBLIC_METADATA.json` and `PROVIDER_RECEIVING.json` at the end;
- `UNKNOWN.json` on any failure. It never retries and never resumes.

**Control branch.** `root-control-source/prepare_live_control.py` only *prepares* the files: CONTROL, INDEPENDENT_REVIEW, ROOT_CONSUMPTION, CreateTree and PUBLICATION_REQUEST. Its PUBLICATION_REQUEST says `ROOT_MUST_PERSIST_EXACT_ONE_SHOT_EFFECT_GRANT_BEFORE_PROVIDER_WRITE`. No code in the static source writes the branch, so the actual push was a separate Root act. This last point is inferred from the code's absence.

**Timing.**
- The hosted job holds for 300 s and polls the control branch at most every 15 s. It accepts only a commit whose sole parent is the workflow commit, with a valid payload, before expiry.
- The operator's admission, plan and driver windows are each 300 s, with at most 45 s per frame.
- So the live role's ten steps, the independent review, the Root input, the preparation and the control push must all fit inside the hold.

**Identity bindings:**
- Astra's thread `01a1cf82…` is a constant in six files: operator_setup, root_operator, public_operator_v2, concrete_root_bridge, event_driver and root_native_history.
- One fixed Codex rollout file is read, with a header-hash check and a thread check. Only matching `codex_apps` tool-completion events are accepted.
- The `wsl.exe` path, the `Ubuntu` distribution, user `agent` and one fixed install root are all pinned.
- The provider actor login and id must equal the binding.

## 2. Hosted image
- Pinned tuples: `20261111.82.6` / `7.0.0-1016-aws` and `20261111.196.1` / `7.0.0-1019-azure`.
- G220 actually ran on `ubuntu-26.04` `20261111.82.6`, AWS us-west-2, kernel `7.0.0-1016-aws`, which is the first tuple.

## 3. G3
- **No G1+G2 join source exists.** `g132-root-preparation/public-tree/qualification/dg16-r5-g1-hosted-episode/g3_receiving.py` (d77406e9…) joins the G1 pair with host-scope receiving. It declares `FULL_G2_RECEIVING` and the overall `DG16_ORIGINAL_RECEIVING` as `permitted=False` future nodes.
- **Review status:** it is part of the G132 whole-host review (`PASS_SOURCE_COMPOSITION_ONLY`, no blocking findings, not operationally ready).
- **Related source:** the G3 v7 create-only callback is publication plumbing only, and it is still awaiting Root review.
- **Inputs it expects:** a live G1 result, scope receiving files, and a Root decision on `pro/dg16-g1-g3-control-32-20261114` (600 s hold). It takes no G2 input.

## Consequence for execution
- Ordinary GitHub API calls cannot replace G221's live-role reads and receiving as they stand. The operator accepts only Codex-session tool events from Astra's own rollout file. A non-Codex executor therefore needs a **reviewed, owner-approved source change** to the operator's evidence channel. That is a protocol amendment for the owner to decide, not a mechanical substitution.
- The final DG16 G1+G2 join needs new source. Today only the G1-side G3 exists.
