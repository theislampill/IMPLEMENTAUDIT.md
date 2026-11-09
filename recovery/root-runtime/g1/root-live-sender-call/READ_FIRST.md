# Root live sender step helper

This is a callable implementation of the existing recipe, not a new sender,
dispatcher, controller, grant, or receipt authentication mechanism. Developing
and checking this helper made no guest, provider, crypto, or publication call.
Root must independently receive/install its exact final bytes before using it.
The installed helper must be an owned, single-link, xattr-free 0400/0444 file
under the existing private operators base. Root selects its actual fresh path.

Authoritative recipe:
`plans/sol-dg16-staged-execution-20261108/g1-current03-recovered/current04-late-sender/root-orchestration/ROOT_LIVE_SENDER_RECIPE.md`
and `READBACK_SUCCESSOR_ADDENDUM.md`. The addendum selects pipeline v2, binary
v3, file readback and binary driver v3. The helper pins these actual selections.
Its binary Journal dependency remains original `control_process_v3.py` c381d6;
control publication v5 is separately installed under
`/home/agent/dg16-g1-current04-operators/public-receiver-02/root-control-v5/`.

## Calling conventions

`root_live_sender_call.py command STAGE --parameters-json JSON` **only prints**
a JSON object containing an exact PowerShell `command`. It does not execute it.
Root passes that literal command to the existing `tools.exec_command`, with
`login:false`. No shell string concatenation or new tool adapter is needed.
The command captures and hash-checks the selected source through the existing
reviewed FD loader before compiling those captured bytes.

The same API is directly callable from ordinary Windows Python:

```python
selected, argv = helper.stage_argv('issue', actual_parameters)
command = helper.command_for(selected, argv)  # data only
```

Root can emit a command for a helper readback/issuance subcommand with:

```text
python -I -B root_live_sender_call.py helper-command --installed-helper ACTUAL_POSIX_HELPER --helper-sha256 RECEIVED_HELPER_SHA check-late --episode ACTUAL_EPISODE --manifest-sha256 ACTUAL_MANIFEST_SHA
```

The returned command invokes the installed helper through the same captured
source loader. Guest-only readback/issuance refuses Windows, root UID, missing
isolation/no-bytecode, changed pipeline bytes or noncanonical physical inputs.
All guest output paths have existing owned 0700 parents and must be absent.
An already present partial result is retained and refused, never removed/reused.

## Ordered calls and concrete parameters

All `command` parameter dictionaries have **exactly** the listed keys. Every
path is a canonical absolute POSIX path under
`/home/agent/dg16-g1-current04-operators`. Every SHA is an actually received
64-character lowercase SHA256. A `deadline_unix_ms` is an integer.

1. **Five actual late inputs.** `command issue` parameters:
   `session`, `recipient_receipt_sha256`, `publication_receipt`,
   `publication_receipt_sha256`, `episode`.
   Session is the actual retained recipient Session; the receipt SHA is its
   actual RECEIVING.json pin. Publication receiving is actual, not a plan.
   Episode must already be Root-selected/owned 0700 as required by the issuer.
2. **Assemble.** `command assemble` parameters: `episode`.
   This selects the fixed installed stage, host phase, reader, corrected binder,
   private11 and five late inputs; output is exactly `episode/assembled`.
3. **Root source receiving.** Invoke installed helper
   `check-late --episode E --manifest-sha256 M`.
   It reads all installed member bytes, all physical file/dir modes/owners,
   the exact eleven-input index, original operation, fixed packet selection,
   five late input descriptors and request archive join. It checks the live
   original operation again after reading. Output discloses descriptors only.
   After Root actually accepts these results and source/currentness/provenance,
   invoke `receive-late` with the same arguments plus
   `--root-decision-ref ACTUAL_ROOT_NATIVE_DECISION --output FRESH_RECEIPT`.
   This records **source-only** acceptance. It cannot verify Root's identity
   from a string and does not authenticate recipient/provider history.
4. **Dispatcher selection.** `command dispatcher-selection` parameters:
   `episode`, `late_receiving`, `late_receiving_sha256`, `install`, `output`.
   `install` is the final fresh dispatcher directory; no later relocation.
   `command requirements` parameters: `selection`, `output` (fresh directory).
5. **Actual dispatcher admission.** Root independently receives exact
   `DISPATCHER_ADMISSION_REQUIREMENTS.json` and its SHA, then invokes helper:
   `issue-admission --episode E --requirements R --requirements-sha256 S
   --root-decision-ref ACTUAL_ROOT_DECISION --output FRESH_ADMISSION
   --issuance-record FRESH_ISSUANCE_RECORD`.
   This is an explicit Root act: exact `expected_body` bytes are written as the
   consumed admission, and a separate provenance record binds the actual Root
   decision reference, requirements and issued file. The program does not
   promote authority-NONE requirements into authority by itself.
   `command bind` parameters: `selection`, `admission`, `install`.
6. **Receive final dispatcher.** Helper `check-dispatcher --install D
   --install-manifest-sha256 M --selection S --selection-sha256 H`.
   This reads all six exact installed files, modes/group/owner and final path;
   joins helper SHA/expiry/actual admission, and compares the complete outputs
   with the captured hash-checked frozen binder's pure binding function. This
   mechanical same-source comparison is not another independent reviewer.
7. **Start the single sender nonblocking.** Helper `sender-command --episode E
   --manifest-sha256 M` returns the exact captured-source-loader command with
   **no sender arguments**. Root starts that command once via the existing
   actual native process/session interface, e.g. `tools.exec_command` with
   `login:false, tty:true, yield_time_ms:1000`; retain its returned actual session
   and terminal custody. Do not wait for completion before driving the broker.
   Root then executes the complete already received bound `dispatch.js` in
   Root's own `functions.exec`. No generated substitute, custom loop or source
   modification is supplied here. Its exact eighteen calls and LF wire format
   remain unchanged. Dispatcher completion is not sender terminal completion.
8. **Actual terminal component receiving.** Retain the original complete
   `dg16.root-sender-terminal-export.v1` and actual owned terminal/exit/native
   history. After receiving that evidence Root may invoke helper
   `receive-sender-terminal --terminal T --terminal-sha256 H
   --native-session-id ACTUAL_ID --actual-exit-code 0
   --root-decision-ref ACTUAL_ROOT_TERMINAL_RECEIVING --output FRESH_RECEIPT`.
   This explicitly records only PAYLOAD_READY/cleanup/no-publication terminal
   component receiving. Its session/exit claims require genuine Root native
   history; the helper cannot derive them from stdout. Original OUTCOME and
   ciphertext joins remain required in the frozen publication-inputs owner.
9. **Binary PLAN/purpose preparation.** Root separately receives the actual
   supported current parent-ref result and its native provenance. `command
   publication-inputs` parameters: `episode`, `sender_terminal`,
   `sender_terminal_sha256`, `sender_receiving`, `sender_receiving_sha256`,
   `parent_ref_result`, `parent_ref_sha256`, `journal_directory`,
   `deadline_unix_ms`, `output`.
   This invokes only the received pipeline v2, which calls captured entry
   `inputs()` after the actual outcome and never calls `sender()`.
10. **Read prepared inputs outside publisher TTY.** Helper `check-prepared
    --prepared P --prepared-manifest-sha256 H` reads exact five files and joins
    purpose, plan and deadline. Root independently receives complete PLAN raw
    bytes/SHA, purpose and current admission requirements. Then invoke helper
    `issue-admission` as in step 5, adding `--prepared P
    --prepared-manifest-sha256 H`. Its binary branch requires the exact v2
    requirements, current source/context and the unchanged original deadline.
    `command publication-config` parameters: `prepared`,
    `prepared_manifest_sha256`, `admission`, `admission_sha256`, `output`.
11. **Select, do not auto-publish.** Helper `binary-selection --prepared P
    --prepared-manifest-sha256 H --configuration C --configuration-sha256 S`
    returns the actual `selection`, `trustedPlanRaw`, plan descriptor, purpose
    and deadline for the **existing** binary driver v3:
    `runBinaryWithSelection(tools, native, selection, trustedPlanRaw,
    plan.sha256, deadline_unix_ms, Base, purpose)`.
    Root supplies its already received Base and actual supported first-party
    surface, including base64 `github_fetch_file`. Invoke once only; do not also
    run the standalone binary CLI. This helper never invokes the binary driver.

## Clock, failures and limits

Complete installations, source receiving and templates before the live clock.
The actual request and operation set the existing absolute deadline (at most
600 seconds); neither this helper nor a receipt renews it. Binary deadline is
capped by that operation; its existing 45-second frames and 8192-byte chunks
remain unchanged. The sender starts once, dispatcher performs eighteen fixed
read calls, binary publication remains five writes/six readbacks. None grants
another host run, recipient, issuer, nonce, retry or original acceptance.

Any refusal/partial output/ambiguous launch/expired return stops advancement.
Retain actual returned safe data, actual process/native custody, and first
failure; do not delete partial evidence or use another fresh suffix to retry.
Root still owns any live effects, authentic decisions and closing receiving.
The helper makes no cleanup, timing, cost, native, or whole-cell award.

## Verification boundary

`python -I -B test_inert_helper.py` exercises only this private helper's pure
command framing and in-memory issuance functions. No frozen target module,
guest, session, sender, dispatcher, publisher, crypto, provider or host was run.
Guest physical execution/readback of this new helper is **not yet qualified**.
