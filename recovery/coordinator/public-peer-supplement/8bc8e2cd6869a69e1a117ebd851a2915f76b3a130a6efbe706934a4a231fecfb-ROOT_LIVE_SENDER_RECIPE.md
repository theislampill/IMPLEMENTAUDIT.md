# Root live sender route

This is a Root execution recipe, not an admission or an execution receipt. Sol has performed no provider, sender, encryption, publication or private-input operation. Root owns every actual effect below. Matching source, JSON or hashes does not authenticate an issuer. Keep the original failed attempts and UNKNOWN outcomes; do not restart an uncertain sender, dispatcher ordinal or publisher.

Run the Python commands only through Root's already received Ubuntu / agent / `/usr/bin/python3 -I -B` source loader. Pin the actual installed source before invoking it. The command bodies below describe that loader's real CLI arguments; they are not permission to run an unverified pathname. Use existing actual installations and receipts rather than recreating them.

## Required actual Root inputs

Before issuing the short-lived operation, Root independently receives the current recipient session, its `RECEIVING.json` SHA, and the actual joined host ref/commit/run publication receipt and SHA. The issuer pins host commit `f9ba187e8f5520956f0f16cf13c0a706e8360b96` and tree `8390375505282e602759c7976b6bca82a44d5737`; a different episode must refuse rather than be substituted.

Root also selects and physically receives the current04 stage, host phase, eleven indexed private source bodies, assembler, R378 reader and corrected dispatcher source. Complete source installation and review before starting the recipient-derived operation's clock. No command below generates replacement source during a live episode.

Set these variables to **actual Root-received POSIX paths and actual digests**, not fixture values. An unset value must stop the invocation:

```bash
BASE=/home/agent/dg16-g1-current04-operators
ISSUER="$BASE/root-recipient-issuer-01/issue_recipient_inputs.py"
ASSEMBLER="$BASE/late-assembler-01/assemble_actual.py"
STAGE="$BASE/late-assembler-01/source-stage-01"
HOST_PHASE="$BASE/public-receiver-02/phase"
READER="$BASE/public-receiver-02/author/receiver.py"
PRIVATE11="$BASE/retained-current04-private-inputs"
BINDER="$BASE/dispatcher-templates-02/bind_dispatcher.py"
BINARY_MODULE="$BASE/root-final-operators-01/binary_publish_v2.py"
: "${PIPELINE:?actual pinned root_pipeline_inputs.py}"
: "${SESSION:?actual recipient session directory}"
: "${RECIPIENT_RECEIPT_SHA:?actual RECEIVING.json SHA256}"
: "${PUBLICATION_RECEIPT:?actual host publication receiving file}"
: "${PUBLICATION_SHA:?actual host publication receiving SHA256}"
: "${EPISODE:?Root-selected fresh private episode directory}"
```

Those fixed installation paths were supplied by Root's current native receiving. This document has not probed their runtime contents. `PIPELINE` is a new Root-selected installation, not yet installed merely because its source exists; receive/install its exact reviewed source before issuance. Do not put Root keys, cipher contents or tool wrappers in these variables.

The issuer requires the episode directory already to exist, canonical, owned by the effective nonroot user and mode 0700, underneath `/home/agent/dg16-g1-current04-operators`. Creation and reservation of that directory are Root acts. Its `late-inputs`, `assembled` and dispatcher installation outputs must be fresh. Never delete a partially written output to regain retry credit.

Selected source pins:

| Source | SHA256 |
|---|---|
| `issue_recipient_inputs.py` | `b21469b2ee92a7dd3cf59f09d5e006c6fe143b0b38f1581a588411e748a43053` |
| `assemble_actual.py` | `4201abd63171b53d271fe282d114cdc6ec1de982ec8eafdd218ccab90a5ec39f` |
| `late_sender_current04_v2.py` | `97408df8058e6c8c8bab754ed8f9df8edf3f930ac4f47dd466c16eda9732f3cb` |
| `bind_dispatcher.py` | `d83c761dbc666d78856cf2d52ced4db2b6b8d373742deef4938b2d4b6434938f` |
| R378 `receiver.py` | `378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122` |

## 1. Issue the five actual late inputs

```bash
/usr/bin/python3 -I -B "$ISSUER" \
  "$SESSION" "$RECIPIENT_RECEIPT_SHA" \
  "$PUBLICATION_RECEIPT" "$PUBLICATION_SHA" "$EPISODE"
```

The issuer reconstructs recipient receiving through the actual R378 session and independently checks the publication joins. It writes exactly:

```text
EPISODE/late-inputs/ROOT_SENDER_ASSEMBLY_SELECTION.json
EPISODE/late-inputs/PRO_SENDER_OPERATION.json
EPISODE/late-inputs/PRO_SENDER_ADMISSION.json
EPISODE/late-inputs/ROOT_REQUEST_ARTIFACT.zip
EPISODE/late-inputs/HOST_PUBLICATION_ROOT_RECEIVING.json
```

It selects `EPISODE/assembled/packet` as the fixed packet. The operation expiry is the earlier of the actual request expiry and issuance plus the binding's acquisition interval. Assembly, sender, dispatcher and publisher must remain within their existing applicable bounds. No grace, reconstructed nonce or renewed operation is provided here.

## 2. Assemble; independently receive the exact output

```bash
/usr/bin/python3 -I -B "$ASSEMBLER" \
  --stage "$STAGE" --host-phase "$HOST_PHASE" \
  --root-reader "$READER" --dispatcher-source "$BINDER" \
  --private-inputs "$PRIVATE11" \
  --late-inputs "$EPISODE/late-inputs" --output "$EPISODE/assembled"
```

The output includes `root_sender_entry.py`, `packet/`, `ROOT_SENDER_INSTALL_MANIFEST.json`, the retained request archive/publication bodies and the root transport delta. This command starts no sender, metadata call or encryption.

**Root receiving gate:** independently read back the selected output tree against the actual install manifest, effective identity/modes, private input index, actual request and issuer bodies. Retain a real Root late-sender receiving body and its SHA outside the assembled tree. Stdout's descriptor/count and authority-NONE manifest do not replace this receiving. Do not issue dispatcher admission or start the sender until this gate is complete.

## 3. Select, require, admit and bind the dispatcher

The exact selection has five fields: `entry_path`, `operation_path`, `helper_path`, `python_path`, `late_sender_receiving_path`. The entry is `EPISODE/assembled/root_sender_entry.py`; operation is `EPISODE/assembled/packet/carrier/PRO_SENDER_OPERATION.json`; Python is `/usr/bin/python3`. Select the helper's **final** pathname now. The binder's fresh output directory must be exactly that helper pathname's parent; do not bind one path and later relocate the helper.

The utility pins the actual Root late receipt and binds the final helper location:

```bash
: "${LATE_RECEIVING:?actual independent Root assembled-source receiving file}"
: "${LATE_RECEIVING_SHA:?actual independent receiving SHA256}"
: "${DISPATCH_SELECTION:?actual utility-produced selection JSON}"
: "${DISPATCH_REQUIREMENTS_DIR:?fresh Root-selected requirements directory}"
: "${DISPATCH_ADMISSION:?actual separately issued Root admission JSON}"
: "${DISPATCH_INSTALL:?fresh final selected helper parent directory}"
/usr/bin/python3 -I -B "$PIPELINE" dispatcher-selection \
  --episode "$EPISODE" \
  --late-receiving "$LATE_RECEIVING" --late-receiving-sha256 "$LATE_RECEIVING_SHA" \
  --install "$DISPATCH_INSTALL" --output "$DISPATCH_SELECTION"
/usr/bin/python3 -I -B "$BINDER" requirements \
  "$DISPATCH_SELECTION" "$DISPATCH_REQUIREMENTS_DIR"
```

Root independently receives the requirements and actual late-source evidence, authenticates current authority and issues exactly its `expected_body` as the actual dispatcher admission. Copying requirements to an admission filename is not issuance. This admission is one sequential 18-read dispatch; it grants no new crypto/native authority.

```bash
/usr/bin/python3 -I -B "$BINDER" bind \
  "$DISPATCH_SELECTION" "$DISPATCH_ADMISSION" "$DISPATCH_INSTALL"
```

The binder outputs `dispatcher_entry.py`, `dispatch.js`, `DISPATCHER_BINDING.json`, `DISPATCHER_ADMISSION.json`, `ROOT_LATE_RECEIVING.json`, `INSTALL_MANIFEST.json`. Root independently receives these exact bytes, helper path, ownership, mode 0400 files and mode 0700 directory. The bound helper SHA and operation expiry in `dispatch.js` must match the installed bytes and operation. Keep the underlying original source and failed outputs unchanged.

## 4. Start the exact sender once; perform 18 Root calls

Root starts the existing entry directly through its pinned loader, with **no entry arguments**, retaining the actual owned process/session identity:

```bash
/usr/bin/python3 -I -B "$EPISODE/assembled/root_sender_entry.py"
```

Do not wait synchronously for sender completion before driving its broker: the sender waits for the Root dispatcher. Preserve the owned process ID/session and all actual terminal results. Do not launch a second sender after an ambiguous start or timeout.

In Root's own `functions.exec`, execute the exact independently received **bound** `dispatch.js` body. It already invokes `await dispatch()` and uses Root's actual `tools` surface. Do not run the unbound template, manufacture native IDs or replace calls with GH/curl. It initializes the external journal, waits for each committed request marker, reserves both intents, then makes exactly one actual `mcp__codex_apps__github_fetch` call for each ordinal. No automatic retry exists.

The order is OPENING, PRE_ENCRYPTION, CLOSING, each containing `run`, `attempt`, `jobs`, `artifact`, `artifacts`, `workflow`. The selected artifact is represented by fresh artifact-list calls; do not substitute artifact/download endpoints. The returned wrapper is retained completely as the dispatcher's existing `JSON.stringify(actual)+'\n'` UTF8 serialization, separate from actual native provenance. That literal serialization is specific to this dispatcher and must not silently become the other callbacks' no-LF wire format.

After all 18 published responses, dispatcher `finish` reports `DISPATCH_18_COMPLETE_SENDER_TERMINAL_SEPARATE`. That does not certify sender termination, ciphertext, cleanup or publication. Continue observing only the already owned sender until its genuine terminal response; do not restart it. Keep fixed-error/UNKNOWN custody and actual native tool history on any failure.

## 5. Receive actual sender terminal and single-encryption outputs

Root durably retains the actual bounded terminal export from the owned sender process together with session/exit/provenance. Require `dg16.root-sender-terminal-export.v1`, `PAYLOAD_READY`, `cleanup_complete:true`, `publication_performed:false`, empty original awards and actual successful terminal exit. Stdout JSON alone is not authenticated receiving.

Root independently joins the exact entry/install manifest and current request to the private session's original `OUTCOME.json` and its exact `CONTROL.json` / `INPUTS.cms` byte descriptors. The publication utility is permitted to call frozen `entry.inputs()` only after that actual outcome; it must never call `sender()` or re-encrypt. Keep keys/private source plaintext out of commands, output and logs. A missing/failed/uncertain sender outcome stops this path.

## 6. Prepare, admit and invoke the binary publisher

Root obtains a genuine current ref result for the selected control branch/expected parent through its actual supported tool and independently retains the complete result/provenance. The publisher does not guess a branch or parent from TTY output.

The frozen utility's `publication-inputs` command consumes actual terminal/source receiving and pinned sender outputs. It derives the actual binary PLAN and separate purpose, plus authority-NONE admission requirements/config template. Root independently receives/authenticates the PLAN bytes/SHA and purpose `{request_nonce,recipient_sha256,input_index_sha256}` **outside** the publisher TTY. The utility cannot issue an admission.

```bash
: "${SENDER_TERMINAL:?actual durable terminal export file}"
: "${SENDER_TERMINAL_SHA:?actual terminal export SHA256}"
: "${SENDER_RECEIVING:?actual independent Root sender result receiving file}"
: "${SENDER_RECEIVING_SHA:?actual independent sender receiving SHA256}"
: "${PARENT_REF_RESULT:?actual complete supported ref response file}"
: "${PARENT_REF_SHA:?actual complete ref response SHA256}"
: "${BINARY_JOURNAL:?fresh final publisher private journal path}"
: "${BINARY_PREPARED:?fresh Root-selected prepared input directory}"
: "${BINARY_DEADLINE_MS:?existing absolute deadline inside original operation expiry}"
/usr/bin/python3 -I -B "$PIPELINE" publication-inputs \
  --episode "$EPISODE" \
  --sender-terminal "$SENDER_TERMINAL" --sender-terminal-sha256 "$SENDER_TERMINAL_SHA" \
  --sender-receiving "$SENDER_RECEIVING" --sender-receiving-sha256 "$SENDER_RECEIVING_SHA" \
  --parent-ref-result "$PARENT_REF_RESULT" --parent-ref-sha256 "$PARENT_REF_SHA" \
  --journal-directory "$BINARY_JOURNAL" --deadline-unix-ms "$BINARY_DEADLINE_MS" \
  --output "$BINARY_PREPARED"
```

This writes exactly `PLAN.json`, `PURPOSE.json`, `CONFIG_INPUTS.json`, `ADMISSION_REQUIREMENTS.json` and `PREPARED_MANIFEST.json` in the fresh prepared directory. Root independently receives the prepared manifest's actual SHA and verifies its four pinned members along with actual purpose/provenance. All input/output paths must be canonical under `BASE`; output parents must already be Root-owned mode 0700. It does not create the future publisher journal. It reads actual ciphertext only after verifying the single sender terminal/outcome; its DER ContentInfo check is a pure parser, not encryption/decryption or authenticated interoperability.

Root independently issues the actual binary admission after verifying exact context, request, both file byte/SHA/Git IDs, tiny tree, selected branch/sole parent, actual sender receiving/terminal/install manifest, actual parent result, journal and deadline. The utility's `publication-config` command checks the actual issued admission against the requirements and produces a pinned configuration.

```bash
: "${BINARY_ADMISSION:?actual separately issued Root binary admission file}"
: "${BINARY_ADMISSION_SHA:?actual issued admission SHA256}"
: "${BINARY_CONFIG:?fresh final selected configuration file}"
: "${PREPARED_MANIFEST_SHA:?independently received PREPARED_MANIFEST.json SHA256}"
/usr/bin/python3 -I -B "$PIPELINE" publication-config \
  --prepared "$BINARY_PREPARED" --prepared-manifest-sha256 "$PREPARED_MANIFEST_SHA" \
  --admission "$BINARY_ADMISSION" --admission-sha256 "$BINARY_ADMISSION_SHA" \
  --output "$BINARY_CONFIG"
```

Independently receive the returned configuration path/SHA as `BINARY_CONFIG_SHA`. Recheck actual source/context/admission currentness; do not treat the utility's authority-NONE output as Root authentication.

The publisher source command is:

```bash
: "${BINARY_MODULE:?actual pinned binary_publish_v2.py}"
: "${BINARY_CONFIG:?actual utility-produced admitted configuration}"
: "${BINARY_CONFIG_SHA:?independently received configuration SHA256}"
/usr/bin/python3 -I -B "$BINARY_MODULE" publish \
  --configuration "$BINARY_CONFIG" --configuration-sha256 "$BINARY_CONFIG_SHA"
```

Do not launch this standalone command and separately launch another publisher. The actual Root V8 `runBinaryWithSelection` invocation owns this one launch through its received secure loader and supplies the exact module/config selection. Root loads/adopts the frozen Windows IO, SHA helper and binary driver; supplies actual first-party tools, independent PLAN raw/SHA, actual purpose and existing absolute deadline; then invokes that API exactly once. It fetches argument chunks through the existing fixed CLI into memory and validates their complete hash and independent intended call before every effect. No large ciphertext argument goes into shell command text.

Expected result: exactly five writes (two blobs, tiny tree, sole-parent commit, compare-and-update-ref with `force:false`) and six readbacks (ref, commit, tree, both actual blob bodies, closing ref). Require actual publisher receiving and genuine terminal/custody, with exact source/context/purpose/readback joins. A native return after expiry is evidence to retain, not permission for the next call; if its role is extinct, keep the safe result descriptor/native history and UNKNOWN local receiving. Do not retry an uncertain effect.

## Remaining qualification

The exact utility argparse interfaces above were read from `root_pipeline_inputs.py`. They prepare/validate local files; they do not perform provider/crypto/publication calls or authenticate Root from JSON. Source review does not physically install the new utility. Root receives its actual bytes and dependencies before using the route.

Root still owns exact utility/source review and physical installation, actual recipient/publication/currentness, source/dispatcher/binary receiving and admissions, actual supported calls and native history, owned process custody, runtime/noecho/chunk qualification and final original G1/G3 semantics. This recipe and source PASS receipts award no original/native/whole-cell acceptance.
