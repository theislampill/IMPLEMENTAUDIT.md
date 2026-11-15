# DG18 dependency-inventory correction: independent review

## Disposition and identity

**No blocking finding in this exact source-CI reporting correction.** The
principal controller may use this review for the already-authorized guarded
source update. Actual hosted execution and result receiving remain separate.
The reviewer performed no publication, source-case rerun, hosted rerun, or
native/protected operation.

| Subject | Exact identity |
| --- | --- |
| Reviewer | `/root/dg18_independent_review` |
| Candidate commit | `5e9bc4b83c167961b68590054b074d02682aee56` |
| Candidate tree | `2cafb6127d1b24a1cc795cbdbf4c6a4291e197fc` |
| Local parent | `c1affd7e192bfc44e80447e4e2ff89d3ffb1fa7b` |
| Parent / second publication tree | `e0e5b510c94f2c75e387e7164afe599323d242ba` |
| Second remote publication | `d917660ae8905ef20971e739a321909a23c87350` |
| Corrected workflow SHA-256 | `a95a2c463696ab07758dcec99200b2491c8b1ca36f6858ce1c0d871e6501183e` |
| Author validation record SHA-256 | `07cfacf466bf1c47cf40446736b429d0900a0c9435ca60e4bc5c616832c0fc51` |
| Focused checker SHA-256 | `f17edf3a12bd02a90a38e036849b9c8992a3de31c077e2a5867c8e25639b06c0` |

## Actual first failing predicate

The reviewer independently retrieved [run 43676180544](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43676180544),
job `132696727554`, the job's steps, and the actual job log through the connected
GitHub tools. The head commit/tree match the identities above and the exact
local parent tree.

Checkout succeeded. Source/interpreter preflight succeeded and printed an empty
failure list. The job log records successful installation of tiktoken 0.13.0.
The subsequent dependency-inventory command raised
`importlib.metadata.PackageNotFoundError` for `charset_normalizer`.

The mandatory tokenizer version assertion precedes the inventory command in
the fail-fast shell script. Reaching the inventory exception establishes that
the earlier assertion did not fail. This is a deduction from command ordering
and `set -e`, rather than a separately printed assertion-success marker.

Tokenizer-data acquisition and the three-source-case step were skipped.
**This run executed zero source cases.** Preserve it as a diagnostic reporting
failure after successful preflight, not a source-case pass or failure. The
reviewer's selected actual-log readback is in
`INVENTORY_FAILED_RUN_READBACK.json`.

The old inventory treated version metadata for every enumerated distribution
as mandatory. Python's [3.12 metadata documentation](https://docs.python.org/3.12/library/importlib.metadata.html#distribution-versions)
defines `PackageNotFoundError` for unavailable distribution metadata and
distinguishes distribution metadata from importable package names. Absence of
this metadata does not identify an alternative Requests decoder, and this
review makes no such claim.

## Correction behavior

Only the existing dependency step's shell body changes. The installation
command is byte-for-byte unchanged. No additional dependency is installed to
fill the diagnostic report.

The hard prerequisite still requires tiktoken version 0.13.0, and now explicitly
imports tiktoken as well. The diagnostic inventory catches only
`PackageNotFoundError`. For the six diagnostic distribution names it records
`UNAVAILABLE`. Missing tiktoken metadata is re-raised, including if it disappears
between the prerequisite and inventory. Other metadata exceptions propagate.

The six metadata lookups are optional reporting inputs; this does not declare
the underlying runtime packages optional. Actual tokenizer import and the
unchanged source consumers retain their functional requirements.

## Independent verification

**69 of 69 targeted review checks passed.** The verification record is
`inventory-correction/VERIFICATION.json`.

The reviewer independently reproduced the first predicate by extracting the
exact old inventory Python fragment from the parent workflow. With explicitly
constructed metadata in which only `charset_normalizer` was absent, it raised
the same `PackageNotFoundError` and produced no inventory output. This did not
install packages or run a source fixture or hosted job.

The reviewer then executed the candidate's exact checker independently.
**All twelve fragment controls passed**, covering:

- All seven inventory names present.
- Each of the six diagnostic metadata entries individually absent.
- Missing tiktoken metadata, wrong tiktoken version, and a failed tiktoken import.
- Required metadata disappearing between the two commands.
- An unexpected metadata-reader exception.

The checker executes Python extracted from the exact workflow against explicit
constructed metadata/imports. Its output matches the author's retained twelve
case results. These are narrow reporting controls, not installed-host or source
consumer qualification.

Additional checks verified every current manifest member; refreshed workflow
and validation pins; the author's job excerpt against actual independently
retrieved log lines; the exact step results; both retained hosted-failure
records; and unchanged original source/native input fields. Complete YAML
comparison proves the dependency step body is the only workflow setting change.
The dependency install command, output-path initialization, source/interpreter
guards, runner, three selected cases, branch/repository conditions, permissions,
action pins, timeout, and artifact allowlist remain unchanged.

Actionlint 1.7.12, using the previously pinned and independently rechecked binary,
returned exit 0 with no stdout/stderr or ignored diagnostics. All four Bash
syntax checks passed. `git diff --check` passed and the tracked worktree remained
clean. The seven-file delta contains only the workflow, evidence/packet updates,
and the narrow checker; no runtime, fixture, peer or package source changed.

## Receiving boundary

Both previous hosted failures remain historical evidence: run 43675724954 had
zero jobs; run 43676180544 reached successful preflight before the reporting
exception. Neither executed the three CLI cases. A later actual hosted result
must be received at its own commit/run identity.

This review does not predict a green hosted run or supply native acceptance,
currentness, a grant, merge/release authority, or issue closure. OR/C02 authentic
inputs, W-FULL prerequisites, N1 owner/store/assignment, and complete independent
cold receiving retain their existing gates. No broader source or package bank
was warranted by this reporting-only correction.
