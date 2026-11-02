# R0035 finite original-command owner

`scripts/qualify-work-graph-finite-leaf.py` owns four explicit repository-only
profiles. Each acquires and executes one original verifier command through the
existing qualifier's isolated-leaf launcher. The compiler continues to derive
the full original 117-node map and exact command source; each profile records
the other 116 nodes as omitted. Neither a caller-supplied command nor an unknown
future program can become eligible through this catalog.

| Profile | Original index | Exact original command |
|---|---:|---|
| `CONTROLLED_TASK_AUDIT_SPEC_V1` (default) | 57 | `bash tests/audit-spec.test.sh` |
| `CONTROLLED_TASK_ANDON_CLASS_V1` | 25 | `bash tests/andon-class-contract.test.sh` |
| `CONTROLLED_TASK_REGISTRY_WRAPPER_V1` | 113 | `bash tests/validation-registry.test.sh` |
| `CONTROLLED_TASK_MARKER_ORDER_V1` | 45 | `bash tests/marker-order.test.sh` |

Every command above retains its terminating newline. The original registry SHA-256
is `77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`.
The original registry population/order, source programs, compiler, runner and
serial fallback are unchanged. The catalog does not provide canonical
predecessor or successor substitution.

## Shared ownership and source custody

One session implementation retains the existing producer, lock, expiry,
object/evidence custody, runtime acquisition, image owner and actual executor.
Raw parent-traversal components in source or evidence paths refuse before
inherited path resolution or output creation. This preserves the namespace
owner's explicit path boundary rather than allowing normalization to erase it.
Each profile has its own result scope and live issuance key. A result is usable
only while the same producing process owns it and all source, engine, runtime,
output and required input objects remain current. Failed or incomplete results
never become reusable. Imported receipts, claimed status, arbitrary environment,
callback policy and execution plans are not accepted by the run-only interface.

The fixed prefix helper is captured from one buffer and checked against SHA-256
`86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016`
before it is loaded. The common helper itself and every engine file are captured
and rechecked. Source files use no-follow reads, ordinary single-link type checks,
bounded bytes, allowed `0644`/`0755` modes and stable ancestors. Runtime acquisition
is the existing sealed system-tool/Python/library closure. No second executor,
host root, proc mount, Git operation, candidate Python import or native owner is
introduced by these command branches.

The generated Python wrappers set a captured fixed `umask 022` before the existing
isolated-leaf bootstrap. The original command argv/source are unchanged and the
observer's process-global mask is untouched. This is an explicitly closed startup
profile, not arbitrary-observer legacy correspondence. The earlier actual
component discriminator observed child masks `0077` and `0022` with old and fixed
wrappers under launch mask `077`; its constructed scope earns no original-node
credit. All four profiles have actual original-command observations under an
observer process with mask `077`.

## Original node 113: registry wrapper

This profile acquires four literal files:

| File | Role and source SHA-256 |
|---|---|
| `scripts/verify-package.sh` | Exact pinned selection and checker-read source; registry hash above |
| `tests/validation-registry.test.sh` | Pinned wrapper `ac9459ec5485ae550251924f0e2365dec0ff86859e2b74fca44bebdcd752250e` |
| `scripts/check-validation-registry.sh` | Pinned checker `c7c6b0f26111c44c4caaf5e1ffc20979e48cc15ca83600f3fea16514e9d02fee` |
| `.github/workflows/validate.yml` | Acquired mutable data evaluated by the original checker |

The checker also enumerates the current immediate `tests/*.test.sh` names. It does
not read the other test contents. The common helper binds the existing
`_registry_membership_snapshot_v1` from the captured qualifier's trusted base
owner, whose complete file is already engine-bound. That fixed internal
dependency is not a receiving callback argument. The census algorithm is reused
without a copied implementation.

The existing census includes matching dot names and untracked additions, keeps
the complete immediate name population, rejects nonordinary matching types, and
checks held ancestor/member identities and before/after stability. It retains
at most 4096 immediate entries and 1 MiB of encoded name bytes. Both the projection
and currentness records participate in source custody. Other matching contents
remain unread, including contents larger than the literal-file byte bound.

The image mounts the actual registry, wrapper, checker and CI bytes. Other
matching names become empty ordinary-file placeholders because the checker sees
only their names/types. The wrapper is preserved with `setdefault`; it cannot be
overwritten by a placeholder. No historical test count or registry-derived
membership list substitutes for the current namespace.

The original wrapper first validates that current namespace, then runs six more
cases using three literal private trees. Its full seven cases include the real
and private positives plus orphan-test, require-file-only, CI-only coverage,
missing canonical route and duplicate direct route negatives. The private trees
contain fourteen files and sixteen directories. Maximum per-path sizes across
all literal overwrites total 575 bytes; the largest file is 92 bytes. Fixed source
pins bind this temporary-write proof.

Actual controls retained the original positive and unchanged reuse with one
dispatch. An added hidden unregistered member produced the original checker
diagnostic and actual exit 1; removing the canonical CI route independently
produced its original diagnostic and exit 1. Failed results were not issued.
A membership addition after a positive/reuse pair refused the stale result
without another dispatch. Admission controls separately cover additions,
deletions, dot names, matching links/directories/FIFOs, missing CI, changed program
bytes, file bounds, unread member contents and insufficient temporary capacity.

## Original node 45: marker-order wrapper

Its only subject inputs are the pinned original wrapper and checker:

| File | SHA-256 |
|---|---|
| `tests/marker-order.test.sh` | `1736083571f60936b1fbddf3c038a75c4b866432f7fe242161e0939b13182691` |
| `scripts/check-marker-order.sh` | `9764979aa3e1324e217828684e45ef67f40f14427537502a62ce3d66b6872b31` |

The registry is an acquisition input used for selection only. The wrapper writes
thirteen literal transcripts into one private temporary directory: 1247 bytes
total and 259 bytes at most per file. Every checker invocation supplies an
explicit private path. Its no-argument default repository fixtures are therefore
unreachable and are absent from the image.

The original wrapper runs three positive and ten semantic negative cases. They
cover phase/final order, exclusive handoff/completion, preceding Andon probe,
escalation progress fields, pause order and gaps after completion. The actual
original command completed all thirteen, printed its three checker-success lines
and own success line, and reused the same receipt without another dispatch.
Changing the checker afterward refused before another launch. Changed wrapper
and checker bytes also refuse initial admission.

There is no mutable external semantic data in this exact closure. Its original
internal negative calls provide the semantic negative controls; an altered test
is not admitted to manufacture a further negative result or coverage claim.

## Resource and receiving boundaries

All subject source is read-only. Audit-spec, registry-wrapper and marker-order
normalize file modes to `0444`. Andon preserves admitted file modes on read-only
mounts so the unchanged `cp` can create writable private copies. All profiles
retain the existing private 32 MiB scratch ceiling. Admission proves a
conservative scratch reservation in 64 KiB allocation units with per-file and
per-directory overhead; it refuses before runtime acquisition if that amount
cannot fit.

| Profile | Private write set | Baseline scratch reservation |
|---|---|---:|
| Audit-spec | One temporary file, maximum acquired fixture size | 131072 bytes |
| Andon-class | Three copies of the three acquired documents, nine files and sixteen directories | 2424832 bytes |
| Registry-wrapper | Fourteen fixed files and sixteen directories | 2883584 bytes |
| Marker-order | Thirteen literal files and one directory | 1769472 bytes |

The first two reservations derive from current data sizes; the latter two derive
from the exact pinned literal outputs. Registry diagnostics are bounded by twice
the acquired name bytes plus fixed text per member and a constant error allowance;
the existing census bounds keep this below the inherited 16 MiB stream limits.
The original setup writes remain subject to their unchanged shell failure
semantics. Private files are discarded and no successor-visible effect is
claimed.

The new batch's bounded controls are:

```bash
/usr/bin/python3 -B tests/work-graph-finite-batch-cases.py -v
R0035_FINITE_BATCH_LIVE=1 /usr/bin/python3 -B \
  tests/work-graph-finite-batch-cases.py -v
```

The actual namespace command requires the established supported host environment.
Optional `R0035_FINITE_BATCH_EVIDENCE` and `R0035_FINITE_BATCH_OBJECTS` retain exact
completed-case evidence and deduplicate input objects after the case ends. They
do not import historical live authority. The missing-profile RED, admission
results, actual integer exits/streams, source preimages and earlier failed author
attempts are preserved separately.

The final batch passed eleven admission and four actual original-command controls.
The affected audit-spec and andon profiles received fresh final-source admission
and actual positive/reuse checks. Their earlier complete packets remain frozen;
previous semantic-negative or startup controls are not relabeled as new runs.

These are author observations awaiting independent review and receiving
integration. They do not increase the accepted original-node count by themselves,
close prefix24's proc-mount limitation, establish full canonical composition,
qualify native scheduling/currentness, or establish installed product loading.
The helper, tests and maintenance notes are repository-only; no payload cap,
reserve, compressor or packaged compiler API is changed. Final integrated engine
identity and package provenance remain receiving checks.
