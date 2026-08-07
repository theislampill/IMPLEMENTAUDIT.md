# Child-Agent Report

Role:

Reviewer attestation:
- reviewer_identity: <host-visible reviewer or task identity>
- requested_model: <requested model>
- actual_model: <model that actually ran>
- authoring_context_reuse: yes | no
- other_reviewer_output_seen: yes | no
- base_sha: <full lowercase 40-hex SHA>
- head_sha: <full lowercase 40-hex SHA>

Required when a cold-review disposition cites this report.

Read-only confirmation:

Scope:

Report state: PARTIAL | FINAL | interrupted-partial

Verdict:

Owned resources:

- Pre-declare browser tabs, containers, listeners, temp roots, worktrees, and
  similar external resources here before acquisition.
- On interruption, preserve an enumerable present / absent / partial / cleaned
  / unknown residue classification.

Successor review (when a predecessor returned no verdict):

- attempt: <positive integer within this failure origin>
- predecessor_failure_origin: <existing Andon class>
- failure_determinism: content-deterministic | transient
- origin_detail: <provider-policy | schema-rejection | rate-limit | interruption | other detail>
- predecessor_occurrence: <resolved transport-infrastructure Andon occurrence, oN>
- predecessor_packet_scope_file: <contained refused packet file>
- predecessor_packet_scope_sha256: <lowercase 64-hex digest of refused packet>
- packet_scope_file: <run-root-relative reviewer-visible packet file>
- packet_scope_sha256: <lowercase 64-hex digest of reviewer-visible scope>
- packet_alteration: <scope-narrowed[+technique-reworded][+evidence-by-reference] | technique-reworded[+evidence-by-reference] | evidence-by-reference | none>
- provisional_findings_carried: <safe-file.md#heading refs | none>

Each provisional finding heading starts with the exact record:

```text
finding-record: id: <heading> | status: provisional
```

Each packet scope file carries exactly one inspectable row:

```text
review-packet-scope: scope: <comma-separated lowercase tokens> | technique: <lowercase token> | evidence_mode: <inline|reference>
```

Normalize those fields for the repo-side run-root check as one exact row:

```text
successor-review: attempt: <N> | predecessor_failure_origin: <class> | failure_determinism: <content-deterministic|transient> | origin_detail: <detail> | predecessor_occurrence: <oN> | predecessor_packet_scope_file: <relative-file> | predecessor_packet_scope_sha256: <64-hex> | packet_scope_file: <relative-file> | packet_scope_sha256: <64-hex> | packet_alteration: <record|none> | andon_class: transport-infrastructure | provisional_findings_carried: <safe-file.md#heading refs|none>
```

For a runtime non-verdict, also record:

```text
lane-status: status: REVIEWER_RUNTIME_NON_VERDICT | predecessor_failure_origin: <class> | failure_determinism: <content-deterministic|transient> | origin_detail: <detail> | predecessor_occurrence: <oN> | provisional_findings: <safe-file.md#heading refs> | substantive_verdict_consumed: no
```

Files inspected:

Commands run:

Andon registration check:

- Required gate failures, hangs, timeouts, shell errors, substitute reruns, and
  replaced evidence were checked for Andon records before closure.
- If this verifier previously missed that invariant, the prior report is marked
  superseded for release proof and this report is the rerun evidence.

## Findings table

Append findings as they are produced. Replace `Report state: PARTIAL` only when
the authorized terminal report exists. `interrupted-partial` rows remain
provisional until independently reproduced and do not consume a substantive
verdict.

| Status | Finding title | Category | Evidence | Impact | Effort | Risk | Confidence | Fix sketch / implementation route | Owner/source | Verification | Rejected/deferred rationale | Remaining risk | Route | Countermeasure | Owner decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Required patches

- TBD

## Required fixtures / canaries

- TBD

## What closes

- TBD

## What remains

- TBD

## Next smallest safe action

- TBD

## Evidence boundary

- This report is review evidence only.
- It does not authorize edits, commits, pushes, installs, indexing, exports,
  releases, publication, provenance, or AGENTS.md changes.
- The main `/implementaudit` agent must inspect live files and normalize
  actionable gaps into the ledger before patching.

## AGENTS_UPDATE_DECISION input

Durable repo-local rule suggested:

Nearest AGENTS scope:

Reason:

Evidence location:
