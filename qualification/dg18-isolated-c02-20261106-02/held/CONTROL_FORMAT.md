# Actual root control for one isolated C02 held job

The root-owned public control branch is `pro/dg18-isolated-c02-control-20261106-02` in `theislampill/IMPLEMENTAUDIT.md`, separate from the workflow branch. Branch possession and the `publisher`/`author` strings do not prove reviewer identity. The governor must route a genuine independent review to `/root/c02_cold_review`; the adapter's exact string check only binds that required identity.

This document supplies no review, GO, host request, or runtime authority. Hash the exact actual `HOST_REQUEST.json`, `SEALED_PREPARATION.json`, review and GO bytes without reformatting. The request's fresh nonce and actual run ID/attempt prevent reuse of an earlier request's grant. The request also binds the original private 92-input physical custody census through `input_custody_sha256` and `input_custody_count: 92`. That baseline is never refreshed after review.

## Exact directory and population

The directory is exactly the actual request's `control_path`: `dg18-c02-iso-02/<actual-run-id>/1/`. A GO directory contains exactly three regular `100644` Git blobs, published atomically in one root-owned control commit:

1. `CONTROL.json`
2. `INDEPENDENT_TECHNICAL_REVIEW.json`
3. `ROOT_GO.json`

No commands, extra files, archives, symlinks or subdirectories are accepted. Absence means keep waiting. A present incomplete, invalid or mismatched packet stops without dispatch. Movement of the control branch after final input revalidation causes refusal even if unrelated to this job.

## CONTROL.json

The exact allowed keys are listed below; extra keys are rejected.

| Key | Required value |
| --- | --- |
| `schema` | `implementaudit.r5.c02-held-control.v1` |
| `publisher` | `/root` |
| `repository` | `theislampill/IMPLEMENTAUDIT.md` |
| `run_id` | Actual request's string run ID |
| `run_attempt` | String `1` |
| `workflow_commit` | Actual request's exact 40-hex workflow commit |
| `request_sha256` | SHA-256 of exact actual request bytes |
| `preparation_sha256` | Actual request's preparation seal digest |
| `input_manifest_sha256` | Actual request's input-manifest digest |
| `code_bundle_sha256` | `e595724ee31fbab8e4d0622b056b1f30e0697eac657c1d8e1fb3a244383d0273` |
| `held_adapter_seal_sha256` | Exact adapter-seal digest in the actual request |
| `decision` | `GO` after actual disposition, or `STOP` |
| `files` | For GO, exactly the two authorization filenames, each with exactly `sha256` and `bytes` for its actual payload |

The two authorization filenames are `INDEPENDENT_TECHNICAL_REVIEW.json` and `ROOT_GO.json`. Each file is bounded at 65,536 bytes. Duplicate JSON keys, nonfinite numbers, wrong field values and changed byte payloads fail closed.

A root STOP contains only `CONTROL.json`, with all binding fields matching the actual request, `decision: STOP`, and `files: {}`. STOP does not dispatch or allocate the subject/native process.

## Actual independent host review

The retained review schema is `implementaudit.r5.c02-native-tail-independent-review.v1`. The required fields are an actual `decision: PASS`, `blocking_findings: []`, the exact actual `preparation_sha256`, `host_request_sha256`, and `reviewer: /root/c02_cold_review`. No author-side check or review of different bytes satisfies this gate. This author `/root/c02_diagnostic_engineering`, composition author `/root`, the old authors, and any other reviewer string cannot pass the exact reviewer requirement.

The review must cover this explicitly native35bf-scoped host packet. Publication parent current0d does not resolve the seven-member cumulative C02 applicability residual. Additional public-safe findings/context fields are allowed by the retained gate; credentials and private history must stay outside the public control channel.

## Actual root GO

The retained root-GO schema is `implementaudit.r5.c02-native-tail-root-go.v1`. Root must supply `author: /root`, actual `decision: GO`, the exact fresh subject/controller/owned binary, preparation digest, source commit/tree at 35bf, `one_shot: true`, the exact ten-element `allocation_authorized` array in `AUTHORIZATION_FORMATS.json`, and the digest of the exact actual independent review bytes.

The held adapter additionally requires `host_request_sha256` for the exact actual request and `isolated_fixture_git_commit_authorized: true`. This is a truthful scope acknowledgement for the existing fixture-only operation, not authority for a project repository commit, remote publication, credential access or broader allocation. No GO is inferred from workflow success, an environment variable, a template, a prior grant, or an author fixture.

The adapter rechecks original identities, full hashes, modes, ancestors and invocation chains across the hold and before exclusive dispatch reservation. Only after all checks succeed are the actual authorization bytes copied into the held preparation. The original driver validates the GO hash, review, sealed files and pinned inputs again before its first allocation.

## Expiry, scheduling and uncertainty

The 1,500-second hold begins when the actual request is sealed and uses the same host's monotonic clock. Publication near or after expiry can be refused. Run attempts above one fail before preparation. A new dispatch needs its own fresh nonce/request, actual host review and exact root GO; it never resumes an uncertain prior effect automatically.

The preceding H0 and C02 attempts have terminal, independently received results and consumed grants. This fresh C02 subject may enter the sole DG18 native slot only after exact candidate review, fresh supported host preparation, actual independent host review and a separately issued root GO binding its append, correction and later-boundary authority. No automatic retry, original acceptance, authentic OR, child JOIN, release or closure is supplied by this code packet.

The control channel cannot alter source, expand the 92 inputs, select a different binary/provider/model, override custody, publish raw controller evidence, or award cumulative current0d C02 qualification, original acceptance, authentic OR, child JOIN, release or closure.

## Bounded first-ingress discriminator

The new first-ingress row contains only method_sha256 and a closed scope code in addition to its existing category and reason. The method digest covers only an exact bounded UTF-8 method string. It exposes no raw method, parameters or IDs. NO_THREAD preserves the original short-circuit and does not inspect threadId. Every accepting predicate, guard invocation, operation order, cleanup path and byte cap remains unchanged. The preceding run42188281432 and GO0805f2a4c6af1e1cb33c57c760a171fbf3f2bfc80e54972e2b288505b9729f26 remain consumed, with offending method/payload unknown. This packet is a fresh diagnostic subject, not a repair or replay of that run.
