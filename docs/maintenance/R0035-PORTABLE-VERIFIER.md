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
behaviour. Those nodes have unqualified dynamic reads/writes, resource
dependencies, output artifacts and predecessor effects. No complete trusted
producer currently supplies those observations to a matching authenticating
consumer. Their conservative no-reuse fallback remains required. Extending
this profile requires inspected executable semantics, a complete acquisition
contract and supported actual execution/consumer evidence; adding filenames
or caller assertions is insufficient.

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
