# Actual root control input for one held job

The fixed public control branch is `pro/dg16-dg18-r5-c02-control-20261105` in `theislampill/IMPLEMENTAUDIT.md`. It is a narrow root-operated control channel, independent of the workflow/source branch. Root must remain the authorized publisher of that branch. The adapter treats its contents as bounded data; Git ref possession and the `publisher`/`author` strings are not independent proof of reviewer identity. Root's governor owns real reviewer independence and authorization.

After downloading the in-progress preparation artifact, hash the **exact bytes** of `HOST_REQUEST.json`, `SEALED_PREPARATION.json`, and the actual review/GO files. Do not reformat the received request or seal before hashing. The nonce inside the request and the actual run ID/attempt bind this host and prevent reuse of a prior run's GO.

In C02-08 the request also contains `input_custody_sha256`, a lowercase 64-hex digest of the original private 92-input physical custody census, and `input_custody_count: 92`. The request-hash fields below bind this census without adding a new CONTROL or original GO field. Its baseline is never refreshed after review. The adapter compares the original file identities, full streamed hashes, modes, ancestors and resolved system invocation chains before and after the final pure check and again before exclusive dispatch reservation. A code review of 08 is not the later actual host-packet review, and an earlier request/review/GO cannot authorize this new request.

## Directory and atomic publication

The directory is exactly the `control_path` in the actual host request: `c02-06/<actual-run-id>/1/`. It may have exactly three100644 Git blobs for GO:

1. `CONTROL.json`
2. `INDEPENDENT_TECHNICAL_REVIEW.json`
3. `ROOT_GO.json`

Publish them in one Git commit. No commands, archives, extra files, symlinks or subdirectories are accepted there. A control directory absent from an observed commit means keep waiting. A present but incomplete, invalid or mismatched control packet stops without dispatch. The control branch is read again after input revalidation; movement of its head before dispatch causes refusal, even if the move is unrelated to this job.

## CONTROL.json exact fields

No sample GO or PASS file is shipped. Root creates the actual record only after the real review and root disposition. The following table defines the exact allowed keys; extra keys are rejected.

| Key | Required value |
| --- | --- |
| `schema` | `implementaudit.r5.c02-held-control.v1` |
| `publisher` | `/root` |
| `repository` | `theislampill/IMPLEMENTAUDIT.md` |
| `run_id` | Actual request's string `run_id` |
| `run_attempt` | String `1` |
| `workflow_commit` | Actual request's exact40-hex workflow commit |
| `request_sha256` | SHA256 of exact actual `HOST_REQUEST.json` bytes |
| `preparation_sha256` | Actual request's exact preparation seal SHA256 |
| `input_manifest_sha256` | Actual request's exact input-manifest SHA256 |
| `code_bundle_sha256` | `ec088dc3f69b77afec88536f617354da73be72277f54e157ce34925f2cb5a058` |
| `held_adapter_seal_sha256` | Exact adapter-seal SHA256 in the actual request |
| `decision` | `GO` only after actual disposition, or `STOP` |
| `files` | For GO, exactly two filename keys, each with exactly `sha256` and `bytes` for its actual byte payload |

The `files` keys are `INDEPENDENT_TECHNICAL_REVIEW.json` and `ROOT_GO.json`. Byte counts must match the actual files exactly. Each file is limited to65536 bytes. Duplicate JSON keys, nonfinite numbers and invalid field types fail closed.

For a root STOP, the directory contains only `CONTROL.json`, its binding fields still match the actual request, `decision` is `STOP` and `files` is an empty object. A STOP never allocates the subject or native process.

## Actual independent technical review

The actual reviewer uses the original C02-06 schema `implementaudit.r5.c02-native-tail-independent-review.v1`. Its required original fields are `decision: PASS`, `blocking_findings: []`, `preparation_sha256` equal to the actual seal, and `reviewer` equal to the actual independent routed identity beginning `/root/`. Both `/root/h0_c02_or` and `/root/r5_c02_successor_prepare` are excluded.

The held adapter additionally requires `host_request_sha256` equal to the exact actual request digest. Any review that is not actually PASS cannot be used to dispatch. Do not relabel a review of the unbound template or this adapter as a review of a different bound host packet. Additional public-safe findings/context fields are allowed by the original review gate; keep private history and credentials out of this public control channel.

## Exact actual ROOT_GO.json

The original required keys and values in the bound preparation's `AUTHORIZATION_FORMATS.json` remain unchanged: exact schema, author `/root`, decision `GO`, subject/controller/binary, preparation digest, source commit/tree, `one_shot: true`, and the exact ten-element `allocation_authorized` array. `independent_review_sha256` must hash the exact actual review bytes.

The adapter additionally requires:

- `host_request_sha256`: SHA256 of the exact actual request bytes.
- `isolated_fixture_git_commit_authorized: true`: root's truthful scope acknowledgement of the existing continuing owner authorization. It does not grant a project repository commit or any remote mutation, and it does not ask the user for generic permission again.

The generated GO is never inferred from an environment variable, workflow success, public comment, prior acceptance, or a template. The control files are copied byte-for-byte into the still-held preparation only after every binding and custody check succeeds. The original driver then validates that same GO hash, exact independent review, all sealed artifacts and all pinned inputs again before its first allocation.

## Expiry and uncertainty

The1500-second hold starts when the actual request is sealed, before preparation upload. It is enforced using the same host's monotonic clock. Publication near or after expiry may be refused even when otherwise valid. No workflow rerun is eligible: run attempts greater than1 fail before preparation. A new dispatch produces a new nonce/request and needs its own actual host-packet review and root GO. It never resumes an uncertain prior effect automatically.

The control branch can acknowledge only this reviewed bounded operation. It cannot modify source, expand the92 inputs, select another binary/provider/model, award original acceptance, assert authentic OR, admit child JOIN, publish raw controller evidence, or override custody.
