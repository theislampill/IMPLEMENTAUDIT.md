# R0035 portable verifier acquisition and reuse

This repository companion continues issue #209 through the existing compiler
and runner. It supports a deliberately finite real execution profile. It does
not register a new canonical verifier family, replace the canonical verifier,
authenticate native campaign execution, or grant conversion, retirement,
certification or closure authority.

## Supported operation

On the supported Linux x86_64 profile, run the repository companion with system
Python, a Git candidate directory, and a fresh evidence directory outside it:

```bash
printf '%s\n' '{"operation":"run"}' '{"operation":"run"}' |
  /usr/bin/python3 -B scripts/qualify-work-graph-verifier.py scoped \
  /absolute/candidate /absolute/fresh-evidence
```

Each input line requests consumption against the currently acquired candidate.
The JSONL interface accepts only that operation. It does not import receipts,
caller-supplied execution results, commands or mutation requests. Two unchanged
requests in the same live process can preserve both successful leaf results;
the second request returns their original receipts and raw output without a
new dispatch. A new process must execute again. The process exits nonzero if
any completed consumption failed, and exits 2 for an acquisition or contract
refusal. No request means no execution or qualification.

The supported leaves are exactly these registry commands, with their complete
script bytes pinned in `VERIFIER_LEAF_CONTRACTS_V1`:

| Command | Semantic reads | Existence probes | Outputs and coupling |
| --- | --- | --- | --- |
| `bash scripts/check-readme-toc.sh` | UTF-8 `README.md` | None beyond the captured checker/runtime | Raw stdout, raw stderr, integer process exit; no semantic file output |
| `bash scripts/check-agents-bootstrap-budget.sh` | `AGENTS.md` bytes and decoded text | The checker itself, `docs/audits/RETENTION.md`, `tests/agents-bootstrap-budget.test.sh` | Raw stdout includes line/byte counts; raw stderr and exit; no semantic file output |

These dependencies come from inspecting the pinned Bash and embedded Python
operations. A filename match alone is insufficient. Argument-bearing calls,
changed checker bytes, unknown dependency contracts and missing tracked
dependency declarations refuse. The existence-only inputs are represented by
typed empty regular files when present; their contents are not read by these
exact checker implementations. Changing an existence input's contents alone
therefore preserves a qualified result, while removing it reruns the affected
checker and exposes its actual failure output.

## Acquisition and evidence consumption

`compile_verifier_reuse_v1` is an additional pure API in the single existing
compiler. It rederives the exact canonical registry mapping and stream seal,
then accepts only the complete two-leaf acquisition schema. It selects
execution or consumption by keys that bind the graph, profile, observer
binding, node, pinned contract and captured input image. Supplying fabricated
JSON to this pure API proves no observation or execution.

`VerifierTaskSession` is the actual repository-side producer and consumer.
It retains the exact loaded compiler and driver bytes and refuses later
source drift. It reads all tracked candidate files and directory modes,
rejects source symlinks, special files, extended metadata and oversized files,
and records the candidate HEAD and tree. All tracked files outside the two
reads and two external existence probes form a global conservative source
guard. Registry or unrelated tracked-source changes invalidate both leaves.

The finite runtime includes Bash, dirname, Python 3.12, the explicitly listed
dynamic libraries and the captured Python standard-library files. Runtime
symlinks are resolved into ordinary retained bytes; a custom runtime root may
not resolve outside itself. A wrapper invokes Python with `-P -S -B`, fixed
hash seed and no site startup. The environment is exactly `PATH=/usr/bin`,
`LANG=C`, `LC_ALL=C`, `TZ=UTC`, `PYTHONHASHSEED=0`. Unsupported environment
changes refuse, including ambient shell or Python startup injection.

The consumer builds content-addressed images, seals every input descriptor
against writing, growing and shrinking, and mounts those retained bytes
through bubblewrap. It gives the leaf a separate shell, empty stdin, no host
root, no proc filesystem, no general device filesystem and no inherited input
descriptors. Only the fresh bounded temporary filesystem, the null device and
observer output streams are writable. The retained x86_64 seccomp filter
blocks additional namespace entry/creation while allowing ordinary child
processes. The profile requires working bubblewrap namespaces and Linux
memfd sealing; no host sysctl or security setting is changed by this tool.

The fixed child limits are 30 CPU seconds, 1 GiB address space, 8 MiB per output
file, 4,096 descriptors, 8 MiB temporary space and 45 wall-clock seconds. The
observer also binds inherited resource limits, actual observer executable
bytes, kernel identity, process identity and null-device identity. A resource
or launch failure does not manufacture a checker start, successful exit or
receipt. A timeout kills only the process group created for that leaf.

Receipts remain in the live producer's memory; producer IDs and disk JSON are
not credentials. The consumer verifies original stdout, stderr, durable exit,
receipt, image and dispatch bytes and every required retained input object
before considering reuse. It checks for missing input objects before a later
acquisition could recreate them. Changed or missing output evidence rejects
that cached result. Failed and incomplete executions are never admitted.
Receipt age must be within the configured positive integer lifetime of at
most 3,600 seconds. The plan is refreshed at each actual consumption boundary
so expiration after the initial plan still causes execution.

Each leaf's source and acquired inputs are checked before and after
consumption. A concurrent source/runtime change is preserved as a currentness
refusal, even if the retained earlier bytes executed successfully. The actual
subprocess exit is written before later receipt processing; a later observer
error must leave that completed exit intact. Every aggregate result records
the plan actually consumed for each node and concatenates the original raw
streams. Both selected obligations must succeed for the aggregate to pass.
This two-obligation aggregation makes no canonical fail-fast or shared-shell
claim.

HEAD and tree are retained provenance and are checked within each consumption
transaction. The cross-generation key for these Git-free leaves depends on
their acquired execution inputs and source guard, rather than using commit
metadata as an unconditional invalidator. This does not relax the separate
native candidate/currentness contract, which continues to invalidate globally.

## Full-run observation and retained-record integrity

The existing `legacy`, `dag` and `compare` interfaces remain separate from
the live two-leaf reuse interface. New captures use
`implementaudit.verifier-run.v2`. They observe the current Git HEAD, symbolic
HEAD, refs, staged index projection, tracked files and non-ignored untracked
files. File observations include kind, mode and content digest where regular
bytes are available, plus the opened root and ancestor directory modes.
Source symlink targets are hashed as link text and are not followed. Missing,
unsupported and incompletely acquired members remain explicit. Ignored
namespace contents, arbitrary Git configuration and transitive Git object
closure are not implied by these observations.

The full-run environment record retains its established safe fields and the
two actual CI branch inputs, `GITHUB_BASE_REF` and `GITHUB_ACTIONS`. It binds
the entire inherited environment by digest without exporting other variable
values. It observes the selected Python, Bash, Git, Node and npx executable
bytes where present, process user/group identities, inherited resource limits
and the current umask where supported. These are observations of the ambient
invocation. They do not claim complete loader, library, Python startup,
renderer/browser, network or host filesystem acquisition. A changed recorded
input makes the correspondence check fail; an absent broader acquisition
contract continues to forbid full-canonical cached reuse.

Source acquisition requires supported no-follow directory descriptors and
nonblocking regular-file acquisition. Unsupported platforms refuse this
capture path explicitly. The canonical verifier itself remains available
through its existing direct interface. The observer checks the actual loaded
driver and compiler paths against their retained loaded bytes before launch
and after exit, including when a test points the candidate root at another
directory. Its durable process exit is written before later currentness,
trace or result validation can fail.

For the DAG route, one strict parser accepts only the original source-ordered
`START`/`PASS` sequence or a legal terminal prefix. A zero exit requires the
complete sequence. A nonzero exit may follow an unfinished node, precede all
nodes, or follow all node passes when a shell EXIT trap fails. These cases
retain distinct process and node results. Missing, duplicate, foreign,
out-of-order or malformed events refuse; stored status and boolean terminal
fields must match the derived trace exactly. New captures bind the retained
trace bytes and length, retain the actual command stream and complete argv,
and validate them again through the existing `verified_record` consumer.
Transport restoration preserves the original recorded paths rather than
rewriting their identities to a new extraction directory.

Historical v1 records remain historical. A DAG record must still have its
actual retained trace, and the current consumer checks that trace against its
stored node projection. This re-read does not create an original trace seal,
loaded-engine binding or full argv record that the old producer did not
write. A legacy record has no separately observed node passes. Exact schema
members prevent a v2 record from silently retaining its new fields while
claiming the old format. The comparator reports the coverage of each record
and preserves raw stdout/stderr comparison without normalization.

Trace consistency is not exclusive-writer authentication: the current runner
uses a writable trace descriptor in the shared shell. It does not supply an
authenticated per-node producer for importing arbitrary completion claims.
Before/after ambient observations likewise do not rule out an input changing
and being restored during execution. The isolated two-leaf consumer has its
own stricter acquisition and live-custody contract; full-run observations do
not inherit that contract merely because they use the same compiler.

## Qualification and limits

The explicit successor harness is:

```bash
/usr/bin/python3 -B tests/work-graph-reuse-cases.py /absolute/fresh-evidence
```

It uses a constructed Git candidate populated with the real pinned checker
bytes and current repository inputs. It exercises the actual producer,
runner, raw evidence and consumer; the positive reuse and selective
invalidation results have that scope. The namespace probe and deliberately
scheduled failure controls are separately labelled constructed executor
controls, and are not admitted to the two-checker reuse interface. The harness
retains its exact source, per-control records, mutation witnesses and fixture
Git bundle. An outer invocation must retain its own command, raw streams and
actual exit; reaching an intermediate control is not an outer harness pass.

Older recovered qualification bundles have a preserved discrepancy in an
embedded row-10 exit field, while their durable receipts differ from that
field. Their missing original harness and outer completion records remain
missing. The successor harness copies results when recording each row so a
later returned-object mutation cannot alter an earlier report. It does not
rewrite or retrospectively validate those historical outer runs.

The existing full verifier mapping still binds every registry byte and
preserves original order, stdin, shared-shell state, traps and fail-fast
behaviour. Its expanded observations distinguish available source, ref,
environment, tool and resource changes. They do not close each node's dynamic
read/write set or predecessor effects. In particular, substituting a node in
the shared shell needs the state and effects its actual successor consumes;
an isolated successful subprocess is insufficient. Unqualified nodes retain
the serial no-reuse fallback. Extending the admitted scope requires inspected
executable semantics, a complete acquisition contract and supported actual
execution/consumer evidence; adding filenames or caller assertions is
insufficient.

The portal builder's existing `--out` interface supports a narrower retained
artifact operation without a new compiler or oracle. A task can retain its
explicit output directory, producer inputs and raw result, then invoke the
existing `check-docs-portal.py` against those exact files. Missing metadata or
a changed required proof strip affects that real consumer. Its structural
acceptance of an inert HTML comment does not make raw artifact bytes equal.
This operation does not reconstruct the canonical test's original generated
trees: `tests/docs-portal.test.sh` overwrites some generations and removes its
temporary tree on EXIT, while nested `verify-docs-portal.sh` removes another
tree before returning. The qualifier receives control after those boundaries.
Retaining the original canonical artifacts and consumer events needs an
owner-supplied retention/callback interface at those producer and consumer
operations. A post-run snapshot cannot recover already deleted generations.

The whole-run comparator retains raw-byte equality. Two successful full
executions are different evidence from a failed raw comparison. No temporary
path, fixture commit identity, command, result, artifact or meaningful output
is normalized away. Raw equality also does not independently establish
transitive output-artifact semantics. Shared registry/governor integration
remains a separate owner patch set and must be measured and tested on its own
exact combined overlay; overlay results are not results for the published PR
tree.

## Completed native-format prerequisites

The portable native-format reader preserves a source node's `declared_state`
and `done_evidence`. A current blocking reason, including a missing acquired
read or invalidator, projects a declared DONE node as BLOCKED. Required
consumers also block, including a chain of previously declared DONE nodes.
The compiler does not automatically rerun that completed work. Restoring the
same complete input projection permits the prior declared completion again
at this source-fact contract. A source DONE assertion that requires a source
OPEN or ACTIVE node remains a contradiction and refuses. An ACTIVE node keeps
its resource occupancy even when a current blocking reason appears.

`done_evidence` is a source-declared digest, not an authenticated accepted
result with its historical input binding. Present-but-changed input bytes
change the graph and invalidate affected consumers through
`diff_native_graphs_v1`; a fresh projection alone cannot establish that the
old completion was proved for those bytes. Native use still needs the
governor/R0036 accepted-result producer and currentness contract. The missing
input regression is a constructed portable control and supplies neither that
producer nor native lifecycle acceptance.

## Reminder consumption history

The existing pure `check_recursive_execution_v1` consumer now includes its
source graph in a receipt only after nonempty execution and consumption have
both passed. History intake rederives that retained graph from its original
source documents and checks the exact event, dispatch and complete selection.
An unchanged `REMINDER` with a different event ID can then preserve the consumed
selection when the original scope, subject, context and every relevant input
remain unchanged. Changed inputs or context trigger ordinary reconsideration.
The implementation does not distribute partial historical receipts across a
new selection or give old results new input identities.

Old four-field receipts remain usable for their original same-event replay
check. An overlapping cross-event reminder without a retained source graph
refuses because the original consumption cannot be compared. Inconsistent or
duplicate history refuses even if another receipt looks usable. No-op returns
have `event_receipt: null`; the caller keeps the original consumed receipt.
This avoids manufacturing a new history token for work that did not execute.

The registered native-format fixture exercises this path through actual PREP
and SIB subprocess output and the existing manifest consumers. Its optional
fresh-directory argument retains source facts, raw commands, outputs, exits,
graphs and the no-op receiving result. These are constructed portable controls.
Retained source documents make the pure comparison checkable; authentic native
accepted-history custody remains an input from the existing governor/producer.
