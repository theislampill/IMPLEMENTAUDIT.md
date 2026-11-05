# Actual held-host control format

This document defines the prospective format. It is not a review, GO, approval or execution result. Root separately publishes actual reviewer-authored bytes and actual root-authored authorization. The adapter generates neither.

## Exact location and one-shot binding

Repository: `theislampill/IMPLEMENTAUDIT.md`. Control branch: `pro/dg18-r5-h0-control-20261105`. The exact directory is `qualification/h0-control/<actual run_id>-1`, as provided in the actual `HOST_REQUEST.json`. Only first run attempt is eligible. The fixed branch commit is read before validation and again immediately before exclusive dispatch reservation. No automatic retry or reallocation exists.

The host request includes actual workflow/source commits, source tree, preparation SHA256, input manifest SHA256, original physical input-custody SHA256, controller, subject path, fixed allocations, and the bounded hold/execution times. Source commit `481e529b691ed3d21169b07f376e357ae51f1f03` is already published/read back. It must be the workflow commit's sole parent; its exact tree and published Windows predecessor are fixed by code.

## STOP

Publish one regular Git blob `CONTROL.json` only. It must have exactly the following keys: schema (`r5.h0-held-control.v1`), publisher (`/root`), repository (fixed above), run_id (actual string), run_attempt (`1`), workflow_commit (actual40hex), host_request_sha256 (hash of the exact host request bytes), preparation_sha256 (exact host request value), input_custody_sha256 (exact host request value), decision (`STOP`), files (empty object). STOP terminates the hold without dispatch.

## Actual independent review

A GO directory contains exactly three regular100644 Git blobs: `CONTROL.json`, `INDEPENDENT_REVIEW.json` and `ROOT_GO.json`. Each is nonempty and at most65,536bytes.

`INDEPENDENT_REVIEW.json` must be authored by an actual independent reviewer. Required fields: schema `r5.h0-independent-host-review.v1`; decision `PASS`; blocking_findings empty list; host_request_sha256 and preparation_sha256 bound to the actual host request; reviewer the actual `/root/...` agent identity, excluding this author `/root/h0_c02_or` and its descendants. Additional review findings and scope fields may document the real review. A fixed decision string in this format does not create a review.

The review should inspect the actual12-file preparation, the exact source05 independent-review disposition, the public bundle seal, actual system/executable invocation chains, all102input pins and the request's input-custody digest. The authority ceiling is technical observation only. Review does not award original H0/AC05 acceptance or authorize an external provider.

## Actual root GO

`ROOT_GO.json` is authored separately by root. Required fields are schema `r5.h0-root-go.v1`; author `/root`; decision `GO`; one_shot boolean true; host_request_sha256, preparation_sha256 and input_custody_sha256 exact; subject and controller exact; source_commit and source_tree exact; review_sha256 the hash of the actual independent review bytes; allocations the exact ordered11-string array in HOST_REQUEST. Additional root rationale may be retained. Numeric1 is not boolean true.

`CONTROL.json` has the same exact identity fields as STOP, decision `GO`, and files exactly the two authorization names. Each maps to an object containing bytes (actual integer byte count) and sha256 (actual lowercase64hex). Root publishes these original byte sequences after reviewing them; no tool in this bundle manufactures PASS or GO files.

## Publication and retention

The control branch contains no credential or private native/controller history. Fresh subject path and input identities are preparation metadata. The actual GO covers one isolated fixture commit, fresh controller, owned binary, deterministic loopback provider, one native app-server, one necessary fresh compact/resume, existing store/canonical OPEN, seven native MCP occurrences, live original-reader receiving and bounded cleanup. It creates no permission to consume the old pending observation, make a model call, publish raw evidence or claim original acceptance.
