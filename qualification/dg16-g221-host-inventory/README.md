# G221 prelaunch host inventory

This is one observation of the existing selected-host contract before protected
publication. Its owner is the unchanged `qualification/dg16-r5-full-g2/run.py`
`inventory(u)` entry point, with `u = load_utility()`. The need is RUNBOOK F5 and
step 22 in `handoff/dg16-g221-root-execution-inputs/RUNBOOK.md`: the current
selected image and host must be applicable before a protected G221 publication.

## Scope and result

The wrapper loads the original adapter as a module. It never invokes its CLI,
episode `execute`, provisioning, `observe_host`, protected preflight, request
validation, banks, native tests, M5, model turns, or receiving. It creates no
request, adoption, recipient, product checkout, or episode state. It performs no
installation or repair. Credentials are the public numeric real/effective/saved
UID/GID tuple returned by the original `getresuid/getresgid` reader; no credential
store or key is read. The original `trusted('bwrap')` reads the binary and custody
metadata; it does not execute it.

All eight modules in the adapter's inventory import closure are pinned before
owner code execution. `run.py` executes from checked held bytes. Its unchanged
loaders hash the held bytes they compile; `load_native` also performs closing
reads. The wrapper closes every held source member after the observation. The
workflow pins and executes held observer bytes using `/usr/bin/python3 -I -S -B`.
The wrapper rejects selected process/network and filesystem mutation audit
events while importing/calling the owner code. This narrow check supplements
the inspected, pinned call graph; it is not a general sandbox.

The workflow has one exact engineering branch push trigger, expected repository,
created/nondeleted branch guards, attempt 1, `contents: read`, and no persisted
checkout credentials. It uses the same pinned checkout/upload actions as the
original workflow. It has one source checkout and no source publication step.

The complete actual host passes through unchanged `current_host.target_host`.
Canonical equality uses unchanged `evidence_io.encode` against
`current_host.SELECTED_HOSTS`. A match exits 0 with
`SELECTED_TUPLE_MATCH_OBSERVED`; its scope remains a prelaunch observation.
A mismatch or unsupported inventory exits nonzero with the first original
refusal. When inventory refuses before returning, `host`, `selected_tuple`, and
`selected_match` remain null. No partial or invented host is substituted.

Every result explicitly leaves same-job earned qualification, currentness,
future G221 acceptance, and effect grants false. A later protected job still
needs its original checks on its own actual host. These artifact/log bytes are
observations and confer no authority.

## Public transport

`OBSERVATION.json` contains canonical ASCII JSON with sorted keys, compact
separators, and one final LF. `OBSERVATION.sha256` binds those exact bytes.
Source rows give repository-relative paths, byte counts, SHA-256 and Git blob
identities. The source-base commit/tree describe the unchanged owners; the
provider SHA identifies the workflow event and is independently checked when
receiving provider evidence. This wrapper does not claim provider authentication.

The only retained provider environment identifiers are repository, ref, SHA,
run ID, attempt, and event. Invalid/missing values are null. There is no general
environment dump. The artifact upload runs with `always()`, including failure.
An observer bootstrap pin failure emits a separate explicit refusal schema and
exits nonzero. Checkout failure or runner loss can prevent any observation from
being produced; upload then fails on missing files and does not imply success.

The exact body is also a single log line:

```text
DG16_G221_HOST_INVENTORY sha256=<64 lowercase hex> base64=<canonical bytes including LF>
```

An independent receiver can decode that line from the GitHub log API, require
canonical encoding and matching SHA-256, then reconcile artifact bytes and
provider run/commit identity. No receiving or acceptance machinery is added here.

## Focused local qualification

```bash
/usr/bin/python3 -I -S -B qualification/dg16-g221-host-inventory/test_observe.py
/usr/bin/python3 -I -S -B qualification/dg16-g221-host-inventory/observe.py --local --output <fresh-declared-evidence-directory>
```

The tests check the new closure, inert imports, direct owner call boundaries,
source-change refusal, provider guards, environment allowlist, effect filter,
safe error reporting, workflow pins and bootstrap syntax. Synthetic validator
inputs are marked `TEST_ONLY` and never installed as provider/host evidence.
No test constructs a selected-host success. `--local` is a real read-only host
observation with an explicit unhosted context and always exits nonzero. Its
expected first refusal on a different host must remain visible.

Rollback is removal of these new observation-only sources before publication.
No previously accepted suite or owner source is changed or rerun by this work.
