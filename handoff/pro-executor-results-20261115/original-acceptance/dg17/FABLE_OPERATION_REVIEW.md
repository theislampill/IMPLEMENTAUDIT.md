# DG17 selected operation: distinct source and issuer review

**Disposition: PASS for the bounded operation/issuer rebind and its consuming-code contract.** This is a static source and received-evidence review of the exact operation below. It is not a native grant, native qualification, T12/T13 acceptance, original-14 custody receiving, or programme closure. No true operation-rebind or consuming-code blocker was found in this review.

Reviewer: `/root/dg17_fable_operation_review`, a distinct reviewer with no participation in authoring this candidate. Principal executor/issuer: `PRO-EXECUTOR-01`; no historical Astra identity is adopted. This is the user-directed ordinary distinct operation review, not an internal `audit-assess` dispatch or an additional governance framework.

## Exact reviewed subject

| Identity | Received value |
|---|---|
| Repository / intake commit | `theislampill/IMPLEMENTAUDIT.md` / `fee1768b449483843bb35ade23790d212b3abf0d` |
| Published candidate | `handoff/fable-local-support-20261115/dg17-issuer-rebound-candidate/author/OPERATION_A.json` |
| Operation length / SHA-256 | **19,215 bytes** / **`aa93fda5c8335a892e0dcd1f022375f53aeab53a1350ab54cc943de182234cf7`** |
| Candidate `PINS.json` | 4,535 bytes / `c79ec08d91d19a8f2bce397f237f2e5e77dbdf7841624361e3915c48e5fa9fa2` |
| Actual final author directory | `C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\issuer-rebound\author` |
| Source HEAD / tree | `a297957be11feb494c0ec467235794a1e0c54751` / `b08dc4ecf4028beeedb579a312eccae23cb5d863` |
| Canonical package | 588,580 bytes / `706afde44df992282a43d59e3affa412f0e9ca2dc09f0de1dfc212223751f1e2` |
| Selected issuer | `PRO-EXECUTOR-01` |
| Received candidate `FINAL_HOST_READBACK.json` | SHA-256 `e328edbaeb2520c3689e4a45e11f8b1b14805ce3a392d3329678a8ffbd8736f1` |
| Retained comparison operation | 18,597 bytes / `ec5051ddea4b79bcd2e9980b90e47351fcf62536f00e2649fde43a7fce7a7c9c` |

The local review worktree was detached at the exact intake commit and clean. Both requested READMEs were read completely at that commit: the handoff root `README.md` and the candidate `README.md`. All ten published candidate author members match the candidate PINS sizes and SHA-256 values. The retained ten-member comparison also matches its published PINS. These were receipt checks of published bytes, not a rebuild or repetition of host qualification.

Source citations below are relative to `handoff/fable-local-support-20261115/dg17-issuer-rebound-candidate/` at the exact intake commit unless stated otherwise.

## Smallest reviewed delta

The candidate differs from the retained final Windows record in exactly three author files:

| Member | Actual delta |
|---|---|
| `author/OPERATION_A.json` | Issuer changes from `01a1cf82-cdd6-7053-b7b7-32f5c3d93d21` to `PRO-EXECUTOR-01`; adds the explicit prospective `issuer_rebinding` metadata; forwards author-member paths into `issuer-rebound\author`; records the rebound base as the preparation predecessor. |
| `author/parent_launch_a.py` | Only the `OP_SHA` literal changes from `ec5051dd…` to `aa93fda5…`. |
| `author/bind_stage_b.py` | Only the `A_SHA` literal changes from `ec5051dd…` to `aa93fda5…`. |

The other seven author members are byte-identical: `PROFILE.toml`, `native_rpc.py`, `parent_launch_b.py`, `positive_hook_constructor.py`, `source_setup.py`, `stage_a.py`, and `stage_b.py`. Source HEAD/tree/worktree/branch, source pins, package pin, owner-carrier pin, and the complete limits object are equal between the two final records.

`make_rebound_base.py` explains the two literal updates: it preserves the ten-member base while changing issuer/metadata and replacing the old base-operation hash exactly once in each dependent consumer. The existing builder then forwards final location and source pins. No builder or test change is part of this candidate. The candidate prose remains explicitly prospective; selecting these exact bytes and recording the independent review does not require editing that prose or rebuilding the operation.

## Consuming-code findings

1. **The rebind reaches both stages.** `parent_launch_a.py:38–48` and `stage_a.py:62–64` require the grant issuer to equal the operation issuer and its operation hash to equal the actual operation bytes. The parent pins `aa93fda5…`. `bind_stage_b.py:5,11,18–24` pins the same A operation and copies its issuer into the actual post-A B operation. `parent_launch_b.py:32–37` and `stage_b.py:157–160` then require B grant equality against that actual bound B operation. No historical issuer remains as an executable authority literal in the two changed consumers.

2. **The reported builder refusals are not launch-admission failures.** The parent's `capture()` compares descriptor/path identity without cross-comparing their `st_mode`; it checks mode stability separately within each API and does not require `git.exe` to have one hard link. Its exact size/hash and physical-file checks remain. The operation's `preparation.unverified_inputs` is descriptive builder history, not a predicate read by these consumers. The actual constructor's pinned reader similarly checks mode stability within each API; it does not recreate the builder's `.exe` cross-API mode comparison. Its pinned executable inputs are Python and Bash, not the hard-linked Git executable. See `parent_launch_a.py:13–31`, `parent_launch_b.py:9–27`, and `positive_hook_constructor.py:26–38,78–83`.

3. **The received Windows readback is applicable at its stated ceiling.** The published receipt reports host `3701Media`, Python 3.11.9, the pinned interpreter, the selected `aa93fda5…` operation, and 34/34 PASS rows. Its 29 operation-readset rows plus operation, A driver, RPC, Job helper, and B driver account for the 34 entries. `../dg17-final-operation/readback_with_parent_capture.py` obtains the generated parent functions from their AST and runs those exact `capture()` functions. The receipt also records the isolated home present and all seven fixed native output locations absent. This review received that evidence; it did not re-run the captures or convert that historical readback into a claim about a later launch-time state.

4. **Fresh admission remains mandatory.** The 1,634-byte carrier `05a0767e4a4a72eb7ff13f11bf9341a270b46954bab0e8e57e3e6c7bfa411aff` is retained as an input. Its original one-episode statement and the spent 2026-11-14 Stage A do not issue a new grant. Neither the issuer metadata nor this review supplies one. An actual authenticated isolated route is checked before `thread/start`, and no authentication material is copied (`stage_a.py:41–58`).

5. **Stage B is still conditional and shares the original clock.** A has zero H0/trust/qualifying effects and must return its actual principal, turn, claim/currentness, hook proposal, preimages, and idle cleanup receipt. The binder requires the actual successful A receipt and an independently pinned post-A receipt. The B parent and driver require the same A window and refuse B admission at or after A start + 570 seconds. B resumes the same principal; it does not create another one. Semantic independent PASS and authentic native provenance remain the principal's original receiving duty, as explicitly stated by `bind_stage_b.py:16`; a hash alone is insufficient.

## Original contract and ceilings preserved

The complete limits object remains unchanged: one A appserver, one A model turn, one `thread/start`, two total model turns for the case, zero automatic retries, a single 900-second episode including independent review and cleanup, A work cutoff at 810 seconds, cleanup cutoff at 895 seconds, a 180-second preliminary turn including RPC, a 4 MiB wire-frame bound, and a 16 MiB journal bound. The existing B work/first-event/terminal-receipt and cleanup deadlines are unchanged.

The unchanged code still requires read-only/network-off model execution, the actual supported permission profile, the selected local five-skill plugin, no unselected active hook, no active MCP/app/subagent route, and only the declared isolated-home and new case effects. Stage B retains a fresh user+SYSTEM-only protected Windows store, refusal of Administrators access, exact initial binding, only the three approved config leaves, first selected Stop identity and timing, and actual teardown/tombstone/idle receiving. No original-14 protected replay is admitted.

The candidate PINS retain `original14_custody_unknown_differences: 14`. All fourteen remain UNKNOWN. `OPERATION_A.json:89,95,111–116` explicitly prevents A/source/plugin-copy evidence from becoming full native acceptance. The original #211 acceptance requirements for applicable native discovery/prompt-independent routing and bounded live corroboration remain intact; this selection earns neither T12 nor T13 credit. Source equality, package/metadata discovery, this review, or eventual one-episode success must not be promoted into wider acceptance. Reference: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/211, original acceptance items 12–15.

The received hosted Windows 14/14 qualification remains prior evidence. The handoff's non-elevated local fixture result is 13/14 with the wrong-owner case still requiring elevation; its variant is explicitly local fixture evidence. This review neither re-ran either qualification nor introduced an elevation/fixture/builder repair as a new gate.

## Exact minimum admission and native invocation

**Current disposition:** operation selection and independent source review are ready to return to the principal. A fresh owner grant naming the exact selected operation has not been supplied, and availability of two authentic Codex turns has not been established by this review. Those are the existing remaining admission conditions, not a new engineering task.

The owner's one written grant should cover one fresh DG17 Windows Stop/T12/original-14 episode on `3701Media` at the exact `aa93fda5…` record, with `PRO-EXECUTOR-01` as principal A/B issuer, the original bounds and exclusions, and B conditional on original independent post-A receiving. The programme remains open. The existing A/B principal-grant files are implementation of that one conditional owner authorization, not requests for two owner grants.

The following is the **unissued code-minimal A grant shape**. It may be issued only on the real fresh owner authorization and actual resource acknowledgement; `true` is the consumer-required value, not a resource fact established here:

```json
{
  "issuer": "PRO-EXECUTOR-01",
  "stage": "A",
  "operation_sha256": "aa93fda5c8335a892e0dcd1f022375f53aeab53a1350ab54cc943de182234cf7",
  "owner_approval_sha256": "05a0767e4a4a72eb7ff13f11bf9341a270b46954bab0e8e57e3e6c7bfa411aff",
  "resource_ack_received": true
}
```

If the actual grant is supplied at the following absolute path, Fable's already-selected native invocation is:

```powershell
& 'C:\Users\theis\AppData\Local\Programs\Python\Python311\python.exe' -I -S -B 'C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\issuer-rebound\author\parent_launch_a.py' --execute --grant 'C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\issuer-rebound\GRANT_A_PRO_EXECUTOR_01.json'
```

Do not insert a rebuild, re-review, qualification rerun, source-setup rerun, or standalone 34-capture rerun between the final grant and that native launch. The selected parent's existing input, grant, freshness, interpreter, and resource predicates are the launch path itself. `source_setup.py --prepare` is unnecessary for the received state: the isolated home already exists, and that command expressly refuses an existing home.

After actual A succeeds, only the already-required independent post-A receiving, actual B data binding, and principal B admission may proceed within the same clock. The B grant's exact minimum fields consumed are:

```json
{
  "issuer": "PRO-EXECUTOR-01",
  "stage": "B",
  "operation_sha256": "<SHA-256 of actual OPERATION_B_BOUND.json>",
  "post_A_sha256": "<actual POST_A.json SHA-256>",
  "owner_approval_sha256": "05a0767e4a4a72eb7ff13f11bf9341a270b46954bab0e8e57e3e6c7bfa411aff",
  "independent_post_A": {
    "path": "<absolute actual independent post-A receipt path>",
    "sha256": "<actual independent post-A receipt SHA-256>"
  }
}
```

Those actual-result fields cannot be prefilled honestly. The original B native command, once its original conditions have passed, is:

```powershell
& 'C:\Users\theis\AppData\Local\Programs\Python\Python311\python.exe' -I -S -B 'C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\issuer-rebound\author\parent_launch_b.py' --execute --grant 'C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\issuer-rebound\GRANT_B_PRO_EXECUTOR_01.json'
```

No grant file was written and neither command was run by this reviewer. No build, host test, native capture, protected/model call, source change, or launch occurred. The only authored output is this report. Return to the principal for the one exact-record owner grant when the original resource condition is satisfied, then the selected native invocation.
