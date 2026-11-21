# A4 run 44956925804: independent receiving of the pre-worker refusal

**Disposition: RECEIVED_AUTHENTIC_PREWORKER_REFUSAL_ONLY.** The actual hosted
diagnostic failed in Git-path preflight, before its diagnostic output/intent,
product source receiving, Job owner import, or any of its three workers.
There are **zero native memory measurements** and no native compiler-effect,
audit-control, original-method, or threshold result to receive.

Reviewer: `/root/g132_qualification`; source author: `/root/dg18_a4_next`.
This reviewer did not author the A4 candidate, edit its source, run a worker,
change provider/controller state, or issue any replay. This is ordinary
independent advisory receiving, not a formal child-skill activation, Root
admission, original award, readiness decision, or closure.

## Exact operation and evidence received

| Subject | Received identity |
|---|---|
| Run / attempt | `44956925804` / `1` |
| Terminal provider result | `completed` / `failure` |
| Job | `137006995607`, `compile-only-native-diagnostic`, failure |
| Host commit | `01e1be8ea75ea57d57b48bb98c32ec772cf849fe` |
| Host tree | `b8e01ad02c7ee33d1ae84841c9f65068dc4a86ba` |
| Sole product parent | `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` |
| Product tree | `9c3913ceaa95f3f36b0377fe2dba4a302afcba89` |
| Artifact | `14728236298`, `dg18-a4-compiler-memory-44956925804-1` |
| Provider ZIP | 2,173 bytes; SHA-256 `817b8b1b0413111917c08ebd4bd951350de16bbf9e3b5e9034ef9b6a7e624af5` |
| Inner diagnostic ZIP | 1,597 bytes; SHA-256 `a80db07e815f1d61b7a3da55dea2246baca6f584121646d13eaac1f14c27d3c7` |

The mechanical receiver rehashed the complete nine-member source packet and
four-member prior independent review, checked their seals, matched all three
published full-file readbacks to the reviewed source, and received the retained
commit and branch metadata. It independently re-derived the exact additive
host tree from the immutable product-parent tree plus the three reviewed Git
blobs. Git reads disabled lazy fetching, all protocols, and optional locks.

The terminal run, job, artifact and log records all join to the same operation.
The provider artifact digest agrees with its actual ZIP bytes and the digest
printed by the upload step. Both ZIP layers passed complete CRC, unique exact
membership, safe-path and byte/hash receiving. Root's transfer receipt also
matches every materialized member. These are independent checks of Root's
retained provider responses and actual bytes; this reviewer made no new
provider-authentication call or body GET.

The source receiving and mechanical checks are reproducible through
`RECEIVE.py`; results are in `MECHANICAL_RECEIVING.json` and the complete input
descriptor list is `INPUT_EVIDENCE_INDEX.json`. The receiver performs source
parsing only; it does not import the diagnostic or product code.

## What actually failed

The retained traceback is preserved in `FAILURE_TRACEBACK.txt`. It joins these
exact source locations in `compile_memory.py`:

| Location | Operation reached |
|---|---|
| `execute`, line 276 | Calls `host_receiving` before output creation |
| `host_receiving`, line 221 | Provider binding completes, then calls `tool_paths` |
| `tool_paths`, line 184 | Applies `physical` to the first existing candidate Git path |
| `physical`, line 55 | Raises `ValueError: single-link regular file required` |

The failed predicate is:

```python
not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
```

This proves the selected candidate did not pass the combined regular-file /
single-link predicate at that observation. **It does not identify which arm
failed.** No selected path value, `st_mode`, actual `st_nlink`, file ID,
native link count, alias population, or selected Git body digest was retained.
Consequently, a specific hardlink count or known benign hardlink topology is
not established.

The exact candidate population, in order, is:

1. `C:\Program Files\Git\ucrt64\bin\git.exe`
2. `C:\Program Files\Git\mingw64\bin\git.exe`

The generator raises on the first existing candidate that fails `physical`.
It does not skip a rejected candidate and try the next one. The traceback does
not reveal which candidate existed first or whether the other existed.

Earlier in `tool_paths`, both physical-Python checks had returned. The provider
binding function also returned before Git selection. This supports passage
through those executed guards for the parent diagnostic process. It does not
supply a retained Python body digest or a worker image receipt: the tool-digest
return at line 186 was never reached, and no worker was launched.

The logs identify Windows Server 2022, runner image `20261116.370.1`, and setup
of CPython 3.12.10. Actions checkout separately ran
`C:\Program Files\Git\bin\git.exe` and received version
`2.56.1.windows.1`. That path is outside the diagnostic's two-candidate
population. Checkout success establishes that an Actions Git invocation
worked; it does not establish the wrapper's strict physical predicates or
the identity and custody of the native runtime it may invoke.

## Why the memory and worker result is unmeasured

`execute` creates `INTENT.json` and `SOURCE_BEFORE.json` only at line 277,
after the failed host receiving. It loads the Job infrastructure at lines
278–280, enters the fixed mode loop at line 283, and calls `job.measure` at
line 288. All are downstream of the observed exception.

The planned `native`, `r2`, and `audit` workers therefore did not start through
this exact invocation. Their native memory sampler, paired product-body
compilations, adapter hit/miss checks, real audit-refusal controls, and Job
completion/cleanup receiving never ran. The interpreter still executed the
diagnostic's own preflight code; the zero statement concerns the planned
workers and product workloads, not all Python or Actions activity.

The exact inner ZIP contains only:

| Member | Bytes | Meaning |
|---|---:|---|
| `FINALIZE_INTENT.json` | 688 | The separate finalizer started |
| `NO_EXECUTION.json` | 651 | The finalizer found no diagnostic output directory and created the explicit no-execution marker |
| `MANIFEST.json` | 992 | Binds the preceding two members, 1,339 bytes total |

There is no execute intent, worker start, command intent, Job record, memory
record, worker result, or complete diagnostic result. `NO_EXECUTION.json`
alone would not prove a universal absence of processes. Here it corroborates
the authenticated traceback and exact source control flow.

The execute step exited 1. Finalization and upload succeeded afterward; they
preserved the failure and do not convert it into successful native execution.
No current working-set value, lifetime peak, comparison with 64 MiB, adapter
benefit, native audit result, or original A4 pass/fail can be inferred.

The context fields in the artifact are static diagnostic declarations. In
particular, the frozen-contract and historical-peak fields are not a new
search result or authority over Root's current contract/custody state.

## Causal evidence: what changed and what remains unknown

The exact retained R2 `capture.py` was received against the 54,727-byte source
pin, SHA-256
`821d32feeb3565650e33bb6bc2d356ca6127d91f7921857af6612bd35026bac7`.
`SOURCE_COMPARISON.json` retains the precise relevant function ASTs.

The older `tools_census` selects the **same two native Git candidates**. Its
`physical(..., directory=False)` rejects link/reparse paths and requires a
regular file, but it does **not** require `st_nlink == 1`. The new compile-only
helper applies that stricter condition to executable tool paths as well as
source/retained files. This is a concrete admission-policy difference that
explains why earlier use of the same path family does not prove compatibility
with the new guard.

That source difference supports a link-count mismatch as a causal candidate.
The actual count and file type were not recorded, so it is not a completed
hardlink diagnosis. Other unsupported file-type/metadata observations cannot
be excluded by this combined error. The old capture is neither proof of a
canonical-wrapper route nor authority to remove the new single-link guard.

## Smallest safe next evidence and correction options

**Recommended next step: obtain a bounded metadata-only receiving record under
a new ordinary diagnostic identity, while preserving the refusal.** This
resolves the ambiguity that currently prevents a justified source correction.
Do not rerun the unchanged three-worker workflow.

The prospective observation should retain, before any worker or selected Git
execution:

- The exact selected spelling and the ordered existence results for the two
  current candidates, plus the observed canonical wrapper
  `C:\Program Files\Git\bin\git.exe` as a separately named finite candidate.
- For each existing candidate, actual regular-file/type bits, `st_mode`,
  `st_nlink`, size, relevant file attributes/reparse status, device/file
  identity, and equivalent held native-file metadata when available. Bound
  the path/ancestor population and record before/after stability.
- If type and reparse checks permit a read, a bounded held-file byte digest
  and length. A refused candidate remains refused; observation is not
  admission, and no unsafe candidate needs to be executed to obtain this data.
- The failing predicate arm and structured preflight phase, plus the actual
  native exit status. Retain these even when ordinary receiving stops.

The minimal reporting repair is to preserve that preflight refusal record
after native-platform/provider binding, without moving any worker launch
ahead of its guards. Use an explicit `PREFLIGHT_ONLY_NO_WORKERS` result for a
metadata-only operation; do not make an existing output directory imply that
a worker ran. This is a proposed engineering change only; no source was edited
in this receiving task.

After that evidence, two bounded directions can be evaluated:

1. **Finite canonical-wrapper selection.** If the named wrapper independently
   passes the existing strict physical checks, a new exact tool-selection
   route could preserve those checks for all source and retained files. The
   wrapper's actual identity, configuration/environment behavior and invoked
   runtime/dependency closure must be received. Actions version output alone
   is insufficient, and selecting a wrapper must not silently bypass an
   unreceived native runtime.
2. **Explicit native hardlink support.** Only if the actual file type, native
   count, aliases and identities establish the required bounded case should
   an independently reviewed tool-specific rule be considered. It must retain
   reparse refusal, stable held identity/bytes and the relevant mutation/custody
   protections. A global removal of `st_nlink != 1`, or borrowing the old
   helper's weaker predicate without new evidence, is not supported.

The first concrete action is the metadata-only observation or equivalently
strong already-authentic retained metadata. Neither current evidence nor this
report authorizes a new hosted execution. Root owns the new source admission,
publication, operation identity and actual receiving.

## Limits and return

This review reverified exact retained provider evidence rather than performing
a new provider query. It did not reproduce Windows file metadata on Linux,
simulate successful native APIs, run qualification controls, execute source
bodies, or mutate any source packet. The only written files are this advisory
receiving packet.

The unchanged 28-method order, original 64 MiB guard, A4-07
`UNKNOWN_NO_REPLAY`, prior awards and all original boundaries remain untouched.
The next causal question is precise: **which finite Git spelling failed, with
what actual file type and link-count/identity metadata?** Until that is
received, native compiler effectiveness remains unmeasured.
