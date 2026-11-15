# PRO-EXECUTOR-01 — DG16 execution record, 2026-11-15

This record describes executed engineering and receiving. It creates no commission,
grant, acceptance, protected episode, release or issue closure. The current owner
message activates Sections A–D of `PRO_UNIFIED_COMMISSION.md` at
`e4cba42cb5704f00b78d64e43f5da88501c28229`; its bytes have SHA-256
`14a305d3d3416b5702961b800059e0a922a535173ee4016d537ea2ae6276621e`.
The principal is PRO-EXECUTOR-01. Historical Astra records were not changed.

## Source and contract receiving

The commission and corrected retrospective were read completely from the exact
published commit. Their Git blob identities were respectively
`604c56b947e81d75c9add72125c9cd1b606389f8` and
`f8338602ce60901a545414cb7f858cf9376266d9`.

The engineering checkout starts at
`fe3be3772d2708647c900a580a26c9cae060cb27`, tree
`8528d27e624df82e2bbeddfdacbfcf93fb973b14`. The substantive G221 receiver
correction remains the published `82f4c3d1a5ca85d88f8cb73672d7244dba4f3316`.
Existing historical custody and runtime source files remain unchanged by this
candidate. `build_universe.py g221` and the existing `check_chain.py` completed
**17 checks, zero failures** before the new evidence-channel work. Its retained
result is `evidence/G221_BASELINE_CHECK_CHAIN.json`. That result covers its
existing source graph, not a future launch's fresh bindings.

The real product used for the producer test is commit
`205aeab7c93299b0666b261485ab5658d8e183de`, tree
`9ffbaf95080092bf4a45b8772a97ed16068544a7`. It is distinct from the engineering
carrier commit. PR #255 was observed open, draft and unmerged at
`5277eb82bac6c10e190238afb54eda112eba284b`. This work did not update it.

## Actual producer-to-receiver integration

The following actual product programs ran at that exact product commit:

```bash
python3 -B tests/cognition-pending-durability.py
python3 -B tests/cognition-pending-loader.py --top-level-counter-controls-only
```

Both returned zero. Durability reported **58 controls and 88 processes**; loader
reported **54 controls and 56 processes**. Their exact stdout is retained here.
The source-only `producer_receiver_check.py` passed those outputs and the actual
produced files through the existing `full_evidence.capture_declared`,
`receive_declared` and corrected `pending_relation.normalize` interfaces.

**28 checks passed; zero failed; 144 actual process rows were received.**
Durability contributed 154 preimages and 295 retained files; loader contributed
105 preimages and 379 retained files. The final capture manifest was 805,436 bytes,
SHA-256 `22e9bc7cf132be48b30c144c20e5b7b3e6cd63bfb9ef5fc6aba7254c313beb8d`.
The capture contained 6,072,762 bytes and both roles. Full details and exact
source hashes are in `evidence/PRODUCER_RECEIVER_RESULT.json`.

The historical G220 receiver rejected these genuine outputs at
`PENDING_CONTROL_POPULATION` and `PENDING_COMMAND_SHAPE`; the corrected receiver
accepted them. Missing, extra, reordered, renamed, case-altered and wrong-role
populations refused. Interpreter substitutions, changed stdout and altered
retained producer bytes also refused. These tests exercised the failure class
that prevented G220 receiving. They did not run the full 119-pair operation,
establish native host acceptance, or award M2.

Earlier local source tests remain distinct: an explicitly selected evidence
directory was correctly rejected by the canonical artifact-root predicate; the
engineering carrier commit was unsuitable for the exact product selection; and
the first harness used `python3` where the actual caller passes the sibling
`python` path. Correcting the harness to the real caller contract produced the
recorded 28-check result. No protected episode was retried.

## Evidence-channel implementation

| Component | Responsibility |
|---|---|
| `qualification/dg16-github-evidence/channel.js` | Invoke the actual GitHub connector on selected read-only endpoints; bind source/operator/run/branch/commit/parent/action/result/current authority; perform separate fresh provider receiving |
| `qualification/dg16-github-evidence/journal.py` | Create and read back durable, exclusive operation/action records before calls; reject spent subjects |
| `platform_artifact.py` | Receive the actual download wrapper through the original no-echo frame; acquire one selected public archive through explicit platform egress; verify digest/length and unchanged original parser/decoder/metadata contracts |
| `operator_session.js` | Compose metadata acquisition, the pinned isolated body process, one actual download call, one ephemeral frame and same-process observation under complete external admission |

The new channel uses the actual tools available to this conversation. It creates
no Codex events and does not assume Astra's thread identity. It preserves the
meaning of independently authenticated acquisition: self-consistent JSON or
unequal actor labels cannot supply real authority, source loading or independence.
Actual host/controller admission and the actual distinct receiver remain external
trust boundaries. A serialized approval value cannot replace the callback.

The archive transport is an explicit amendment for this cloud host. The old
direct, no-proxy helper cannot resolve the connector's storage host here. The new
transport uses only the configured loopback HTTPS proxy, retains TLS verification,
the **262,144-byte cap**, **45-second bound**, no redirects and one GET. It refuses
proxy bypass, including port-qualified `NO_PROXY`. A durable intent cannot permit
a GET after expiry. No private/cipher archive, key, decryption or protected replay
is implemented.

The final independently reviewed source pins are:

| File | SHA-256 |
|---|---|
| `channel.js` | `b7c087ce21761b01fa8b5d2e0fd8409f73a402469371511a4df4e92215018e7c` |
| `journal.py` | `9cbac140ff23f1df36867a0eca5fe65c94fd3cea27f52292e094f59d9a4e36db` |
| `platform_artifact.py` | `35ea21a75c8f7da3614454a384ebf53d30c132ac597cbdd86d39017161393389` |
| `operator_session.js` | `974287a4b2eca91d5e7da3ecab7196c5f08219b6bc75495062f5c61c9bdced50` |

Independent reviewer `/root/dg16_independent_review` reported no unresolved
critical or important finding in its final 14-file review. The final report is
retained in `independent-review/INDEPENDENT_REVIEW.json`, SHA-256
`9d990bea3d0df25b53b3392992c914f56eed3d8fdc6bfaa72575cdecfd768828`.
Independent results are **43/43 channel tests, 25/25 transport tests and 7/7
composition controls**, with the stated controlled boundaries. Exact logs are
retained. The source manifest also pins every unchanged original helper used.

The retained RED test log contains the test runner's trailing spaces on blank
diagnostic lines. Those original evidence bytes are intentionally unchanged.
Whitespace checking passes for the source and documentation; the raw-log
diagnostics are recorded rather than silently normalized or described as a
clean whole-diff check.

Review caught and corrected parent-receipt expiry during receiving, deadline
loss while persisting the GET intent, and implicit proxy bypass. Each defect
has a failing predecessor control and a passing corrected control. A final
durable-write overrun returns `UNKNOWN_NO_RETRY`; a retained `FINAL.json` cannot
override that failed return. The spent slot is never reopened.

## Genuine public GitHub and archive observations

The principal actually invoked the pre-correction channel on the historical,
already-terminal **G219** run `43623218185`, attempt 1, commit
`837cf5050264acc287c5c9f5bfa4d49b84117e1f`, tree
`59d957260311a75dcd95d1caa1859ae7d8d5cdae`. Eleven actual connector reads completed
in **10,022 ms**. The result retained **conclusion: failure** and
**original_acceptance: false**. Its receipt digest is
`0284fbfa927f3ecd57ed0a15976db4454a554e2ec9828bfcb180f5d49bb72f71`.

The actual public artifact `14124644875`,
`dg16-full-registry-43623218185-1`, was then acquired with one download invocation
and **one body GET**. Its 12,857 bytes match provider SHA-256
`3c7913493f366a0e27fc380b7269b7bfb4560f31b9cdfeb5652632274a11c634`.
The unchanged original archive decoder received seven terminal members and the
unchanged `metadata_bindings` consumer passed. Its scope remains provided-data
binding, with authenticity independently received. The exact public ZIP,
metadata, intents and safe outcomes are retained. No signed URL or raw download
wrapper was saved.

The authentic smoke used channel SHA-256 `0b19e735...` and transport
SHA-256 `80eebf4e...`, **before** the later review corrections. Exact source
snapshots are retained under `evidence/`; it is not relabeled as an authentic
execution of the final revision. Later source controls and independent review
qualify the final revision without repeating that spent observation.

The independent agent's first actual `channel.receive` attempt remains
`UNKNOWN_NO_RETRY`, **zero provider invocations**. Its adapter incorrectly
required every currentness action to be a string. That first predicate and the
spent journal were preserved. The corrected ordered action helper was qualified
offline and incorporated into the revised channel and composition. The failed
attempt was not repaired or retried.

The independent agent subsequently made three ordinary read-only GitHub
observations for its source review. They independently matched the run,
workflow commit and artifact catalogue; the retained archive also matched the
fresh provider descriptor and original consumers. Those checks are retained
separately. They are not a successful `channel.receive` return.

An earlier G220 public-artifact probe returned `REFUSED_OR_UNCERTAIN`. Its initial
probe did not retain the failing stage. No body retry occurred. A later harmless
origin-connectivity diagnostic demonstrated the direct DNS versus configured
proxy difference; it did not retroactively resolve that unknown request. G220
acceptance cannot be recovered from this work or from its lost private evidence.

## Original acceptance frontier

| Obligation | Actual advancement | Remaining original requirement |
|---|---|---|
| M1 | G132 source dependencies and queued-run interference identified | Fresh eligible G132 contained G1, actual admission and receiving |
| M2 | Existing 17/17 chain; real producer/capture/receiver correction qualified; reviewed alternative public acquisition components | Separate owner use approval, final bound composition, fresh public recipient certificate, live independent reviewer, current prelaunch gates, explicit go, G221 computation/live consumption/terminal receiving |
| M3 | Original in-job G132 G3 contract preserved | Exact local G132 operator sources and both actual same-job consuming decisions |
| M4 | Complete natural-transition predicates retained | Actual qualifying natural material transition; no automatic credit from source work |
| M5 | Source/package identity requirements preserved | Exact canonical package identities, both roles and four disposable Linux runtime routes under original budgets |
| M6 | Independent source review and evidence custody advanced | Accepted G1/G2 results, independent final cross-result receiving, all 48 dispositions, actual CI/delivery and owner receiving |

The source-qualified public acquisition components are not complete original
G221/G132 operator closure. Full bound `public_receiver.inspect`, terminal log
joining, live proof review, separate Root consumption/control publication,
same-job closing readback, final original-route pin closure and live-window
feasibility remain explicit gates. They have not been weakened or awarded.

G132's authentic 98-file public operator set, its 151-file interface evidence and
unpublished host overlay are local to the owner's WSL/Windows custody. The exact
public operator pin manifest is recorded in the original G132 state as SHA-256
`d850a9ca36d4ef0c4b5aa6dddedb9eaa84aa010ef07a333cdad7f969bdadb6af`
under `/home/agent/pr255-g132-root-20261114-01/public-tools-source-01/`.
No private input directory was accessed. The historical queued G1 run
`43098152901` was still queued on current readback; owner cancellation or explicit
concurrence remains required before a fresh protected G132 effect. The standalone
pre-sender gate's floor remains an owner decision.

The parallel DG17 and DG18 branches contain their separate source corrections,
independent review and source-only hosted receiving. Their native grants, actual
model turns, custodian records and original receiving remain distinct. This
record declares none of the three original cells accepted.
