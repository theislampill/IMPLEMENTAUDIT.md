# R0035 finite recursive original-command profiles

## Owner and exact original scope

Three explicit catalog entries extend the existing compiler/acquirer/session
boundary. They retain the full original 117-node graph, and each independent
scope records its one actual node and 116 omitted nodes. The original registry,
programs, pipelines, generated fixtures and checker predicates are unchanged.

| Original index | Profile | Original command |
|---:|---|---|
| 69 | `CONTROLLED_TASK_CAPABILITY_LEDGER_V1` | `bash tests/capability-ledger.test.sh` |
| 72 | `CONTROLLED_TASK_ISSUES_DEFERRED_V1` | `bash tests/issues-deferred-gate.test.sh` |
| 97 | `CONTROLLED_TASK_NO_TERMINAL_CAP_V1` | `bash tests/no-terminal-cap.test.sh` |

The catalog admits only these fixed original program identities:

| Program | SHA-256 |
|---|---|
| `tests/capability-ledger.test.sh` | `14e7ce6f591c9dfe1bafdcdb955093e36ebf61a10ec3fb72552849fa6eab8010` |
| `tests/issues-deferred-gate.test.sh` | `a1b1fee495d90a6c8d3c9def8fa27d6c06bd4fa362ef311659e7170904466487` |
| `tests/no-terminal-cap.test.sh` | `95628b0498d8868ec8988620a7022b0b979247cb760d89bd6e5bcbed339e3755` |
| `scripts/check-no-terminal-cap.sh` | `0868f60de64c71d3d1139931bbaaf6b0927574769c0415f5b9884a5fc03e65b9` |

The selection registry remains
`77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`.
Unknown program or registry bytes refuse. There is no second scheduler,
executor, acceptance authority, caller-supplied command or imported receipt.
The existing `_consume` and `_execute_group` methods, runtime acquisition and
actual isolated-leaf launcher retain their behavior.

## Complete recursive acquisition

One new recursive input wrapper uses the existing bounded `snapshot_tree`
reader. It holds physical no-follow ancestors and selected directory descriptors,
acquires complete ordinary bytes and namespace, and then reobserves every
selected tree before closing. It does not enumerate only the initially found
files during that closing read. Additions, removals, earlier-sibling changes,
same-byte inode replacement and ancestor replacement therefore remain visible.
The complete state is acquired again after runtime acquisition, after execution
and on every reuse request through the existing session.

All names, dot members, binary bytes and empty directories are preserved.
Every ordinary file must be single-link mode 0644 or 0755, and selected
directories/ancestors inside the source must be mode 0755. Symlinks, hardlinks,
special files, unsupported metadata/modes, unreadable entries, invalid names
and unstable paths refuse; none become a skipped clean input. Non-UTF-8 file
contents are valid captured bytes. Unsupported filename encodings or control
characters refuse under the existing path contract.

The shared recursive profile bounds are 1 MiB per file, 8 MiB total source,
2,048 entries, depth 40 and 2,048 UTF-8 bytes per image-relative path. The
combined literal-plus-recursive byte total is checked as well. These are finite
supported-input limits, not a promise to admit every possible repository.
The image retains all captured ordinary bytes and empty directories on the
existing read-only sealed mounts. No recursive subtree is excluded by a Git
tracked-file list or a positive-token allowlist.

The scope differs by original command:

| Node | Complete byte inputs | Presence behavior |
|---:|---|---|
| 69 | Whole `skills` tree, `README.md`, `AGENTS.md` | Required; the four actual positive-token operands inside skills must also exist |
| 72 | Whole `skills`, `docs/portal`, `fixtures/audit-object-routing` trees, plus `README.md` | Required; all four actual positive operands must also exist |
| 97 | Whole `skills`, `docs/diagrams`, `docs/portal`, `fixtures` trees, plus `README.md` and `AGENTS.md` | Original optional roots/files have explicit FILE/DIRECTORY/MISSING observations, including missing ancestors |

For node 97, a genuinely absent optional path remains absent in the image.
A present path of the wrong type, an alias, or a read failure refuses acquisition.
The original checker catches `OSError` and skips undecodable text; this acquirer
never uses that exception handler to excuse missing captured bytes. Binary
content is retained exactly before the unchanged checker applies its own
UTF-8 interpretation. The optional-absence control is separate from the full
source positive and does not replace it.

## Prospective output and private-resource bounds

The unchanged scratch limit is 32 MiB. The unchanged file and stream limits
are 16 MiB. The new resource predicate checks prospective private allocation,
largest file, stdout and stderr before runtime image launch. It preserves the
old scratch gate for the earlier profiles. Resource estimates cannot grant a
successful scan; only the actual original process and retained result can.

### Node 69

The actual grep pipeline writes no semantic file. Its selected stream is
consumed through the original second grep into `/dev/null`. All recursive
inputs are acquired before either grep can read them. Binary-file diagnostic
space is conservatively reserved per acquired input. The profile introduces
no alternate interpretation of the original grep pipeline.

### Node 72: the conditional output-file hazard

The original conditional pipeline redirects its filtered report to
`/tmp/implementaudit-issue-publication-hit.txt`. A write error could otherwise
make the conditional false and reach the original success line. Source byte
volume alone is therefore insufficient.

For each complete acquired input with B bytes, L LF-delimited records including
an unterminated final record, P filename bytes and D decimal digits in the
largest possible line number, the conservative report contribution is:

`B + L * (P + D + 3)`

This allows every line to match, every filename and line-number prefix, both
separators and an extra newline margin. Subsequent invert-match grep stages
cannot increase the report. The bound also reserves per-file binary diagnostics
and fixed script diagnostics. The complete report must fit both the original
file limit and scratch allocation; the prospective error report must fit the
original stderr/file limits. The private file is later removed by the unchanged
program; no successor consumes it.

At the author baseline, 179 actual read files contain 2,197,439 bytes and 39,198
LF records. Their all-lines report bound is 4,306,588 bytes, with 32,615 bytes
of conservative binary diagnostics. The original command passed using the
captured image. A separate source with 50,000 candidate matching lines and long
actual path prefixes exceeds the unchanged file/stream capacity and refuses
before any original dispatch. That discriminator is retained as a refusal,
not executed and relabeled a semantic success.

### Node 97: fixed private trees and bounded diagnostics

The unchanged original wrapper writes 26 literal fixture files. Conservatively
count all nine possible wrapper here-document spools and all 25 checker
here-document spools simultaneously, even when Bash uses a pipe or releases a
spool earlier. This gives 60 possible files, each below 8 KiB, and 98 created
directories including every ancestor and the enclosing temporary directory.
With the existing 64 KiB allocation granule and 64 KiB metadata allowance per
file/directory, the reservation is 14,286,848 bytes, below 32 MiB.

The live source scan can emit one diagnostic for each applicable original
literal term and the original strike/ladder predicates. The allocation bound
counts each potential literal occurrence per line, ignores all negation
exemptions, and overcounts any line containing `strike` or `ladder`. It includes
actual filename lengths, decimal line numbers and a fixed suffix margin larger
than every original diagnostic. This is an output upper bound only: it does not
copy the original pass predicate or allow an estimated clean scan to become a
result. Invalid UTF-8 bytes remain captured, while the output estimate respects
the original explicit decode-skip branch.

The baseline has 714 read files and 5,712,847 actual bytes. The conservative
potential diagnostic count is 24, bounded by 4,493 message bytes, plus the
fixed 8 KiB diagnostic margin. A newline-rich, long-path source that would
exceed the original stream limit refuses through the same prelaunch gate.
Every original generated positive and negative fixture still runs in the real
original-command positive; none was replaced by a synthetic wrapper result.

### Image capacity

The complete source/runtime image must fit the unchanged descriptor ceiling,
including two launch descriptors and a 64-descriptor observer margin. The
sealed mounted bytes must fit a conservative quarter of the existing 1 GiB
address limit. The existing executor independently checks actual opened
file descriptors before launch. Current full-source images use roughly 60–64 MB
and fewer than 1,500 reserved descriptors, below the existing 4,096 ceiling.
No resource limit, package cap or package reserve was increased.

## Author evidence and recovery

The author source composes public C
`e8edae15345b8ae18d4853fa0671c58b3b982847` with the explicitly not-yet-reviewed
finite-next c7d14be8 and topology 97cbbc18 inputs, followed by this bounded delta.
Later root source changes are not silently covered by these observations.

Three missing-profile admission failures were retained before implementation.
These are capability-gap witnesses, not a claim that the original commands
failed on valid data. The first node 69 admission attempt encountered Git
archive's group-writable export modes. That failed attempt is retained; only
the fixture was corrected to the recorded Git file modes and explicit 0755
directories. The production mode gate was not weakened.

The final source and resource bank has 29 passing controls, with all three live
classes explicitly skipped by default. The source controls require neither
bwrap nor runtime acquisition. They cover complete byte membership, dot/binary
inputs, same-byte replacement, closing-read mutation, ancestor replacement,
unsafe metadata/types, required inputs, optional absence and resource overflow.
A skipped live class earns no actual-command credit.

The actual supported namespace bank has 11 passing controls in 64.308 seconds:
10 original-command dispatches, seven original successes, three actual expected
semantic failures and three unchanged same-receipt reuses. The node 72 capacity
arm dispatches zero processes. Each profile finds a forbidden claim in a new
previously unlisted file, preserving the original failure. Foreign processes,
namespace drift and retained-output tampering refuse. Node 97 also runs its
full literal fixture population with genuinely absent optional inputs, separately
from the full-source positive. All declared engine/test/program bytes were
unchanged across the bank; no timeout or observer failure occurred.

Eight earlier catalog profiles retain identical source contracts, acquired
snapshots/objects, resource reservations and compiler selection. Their runtime,
consume and execution methods remain structurally unchanged; their old live
acceptance populations were not replayed or relabeled.

Closed evidence uses a local pool of 743 new objects / 12,922,931 bytes and
read-only references to 710 already retained topology objects / 57,328,491 bytes.
Every object was hash-verified. The external pool was never written or imported
into live custody: every live session freshly acquired all inputs and executed
its own command. Retention occurs only after a case is terminal. Keep both pool
locators from the evidence index when moving or archiving this packet.

## Receiving gates and original-acceptance limits

Independent non-authoring review remains required for complete namespace
custody/currentness, optional absence, output bounds, private resource counts
and actual result scope. The receiving owner must reconcile these catalog
changes with concurrent literal-profile proposals, add three explicit CLI
modes and the new child-suite/entry registrations, refresh any strict source
pins, then qualify the actual final received source. Do not overwrite a newer
shared helper, Q, prefix or compiler with this lane's older engine.

The source proposals are repository-only helper/test/maintenance files outside
shipped payload roots. Final branch package/install checks, hosted CI and the
separate combined-source package blocker remain owner gates. The canonical
458,752-byte cap and 2,000-byte reserve remain unchanged.

Original R35-V02 C1/C2/C3/C7 obligations advance for nodes 69, 72 and 97 only.
R35-N04/V04/V05 gain finite real-byte/currentness/failure/reuse controls. The
original 117-node population, 48 requirements, 20 cases and all eight raw
comparator REDs remain binding. Relative to a separately qualified 32-node
union, these three would yield 35/117 after receiving review and exact-source
qualification; that conditional count is not an author-issued union update.
No accepted JOIN, C6 successor effect, native source selection, native lifecycle,
Windows, whole-route correspondence, whole-issue closure or Pro-exhaustion
verdict follows from this packet. PR251/253/252 and protected controllers were
not modified.
