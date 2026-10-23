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
the live two-leaf reuse interface. Captures without acquisition options use
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

## Explicit full-run input and artifact observations

The `legacy` and `dag` routes accept three independent opt-in contracts:

```bash
/usr/bin/python3 -B scripts/qualify-work-graph-verifier.py dag \
  /absolute/fresh-evidence --retain-repro-assets --empty-stdin --capture-dist
```

Any of the acquisition options above selects `implementaudit.verifier-run.v3`, whose exact
member set includes `child_environment`, `repro_artifacts`, `stdin` and
`dist_namespace`. Unrequested artifact, input or namespace contracts are
null. Historical v1/v2 records keep their original fields and meanings; a
version downgrade carrying incompatible new members refuses. These options
do not change the compiler, registry, command order or shared-shell runner.
They do not enable full-canonical cached reuse.

`--retain-repro-assets` requires the single registered zero-argument
`bash tests/reproducible-release-asset.test.sh` invocation and one of two exact
producer profiles:

| Producer profile | Bytes | SHA-256 |
| --- | ---: | --- |
| Original six-export producer | 11,460 | `7c892c5e84a29bd33d6ed03c97a5610efde51b0d1ad0165f9e9ded0a3bdfb3ad` |
| Additive event-capable producer, capture off | 12,799 | `a27521758cc71e312052d7eaa7c8b488dbbe2dcc5089d6054be0923455763310` |

The original profile remains admitted for historical v3 records. Controlled
real-process comparisons preserve raw stdout, stderr, exit, exports and cleanup
with capture off. All six actual release exports also match across the original,
new capture-off and new capture-on producers when they build the same source
commit. Packages from different commits retain their different inventory source
identities; those identities are not normalized. An inherited
`R0035_REPRO_EVENT_CAPTURE_DIR`, including an empty value, refuses nominal
capture instead of silently adding an event contract to v3.

The producer's existing six exports receive fresh, distinct absolute paths
inside the capture and outside the source worktree:

| Existing environment hook | Retained capture member |
| --- | --- |
| `REPRO_RETAINED_ASSET_A` | `repro-assets/IMPLEMENTAUDIT-A.skill` |
| `REPRO_RETAINED_ASSET_B` | `repro-assets/IMPLEMENTAUDIT-B.skill` |
| `REPRO_RETAINED_PLUGIN_A` | `repro-assets/IMPLEMENTAUDIT-A.plugin.zip` |
| `REPRO_RETAINED_PLUGIN_B` | `repro-assets/IMPLEMENTAUDIT-B.plugin.zip` |
| `REPRO_RETAINED_CHECKSUMS_A` | `repro-assets/CHECKSUMS-A.txt` |
| `REPRO_RETAINED_CHECKSUMS_B` | `repro-assets/CHECKSUMS-B.txt` |

Inherited `REPRO_RETAINED_*` variables or `REPRO_SOURCE_REF`, including empty
values, refuse this option. The source ref remains the producer's existing
`HEAD`; the record binds its commit/tree, exact source and registered command.
The six explicit child overrides and the complete inherited/actual child
environment digests are retained without exporting other environment values.
The observer rechecks source currentness and acquires file kinds, modes,
lengths, hashes and the exact declared population. Each export is bounded to
16 MiB. A successful process requires all six regular files and unchanged
observed source. A failed prefix can retain missing or incomplete outputs,
explicitly labelled `UNQUALIFIED_INCOMPLETE_OR_FAILED_PROCESS`. The durable
process exit is written before a later observation or consumer refusal.

The actual `verified_record` consumer rederives that declaration from the
existing mapping and retained files, including missing, changed, foreign,
role-swapped or mode-altered members. The original literal capture paths and
child environment remain part of identity after transport. Correspondence
compares the raw declared artifacts as well as commands, stdout, stderr and
environment; it never removes temporary paths to manufacture equality. These
are observations of six final exports from the whole process. They do not
authenticate internal producer/consumer events, recover deleted generations,
or establish every dynamic read, write, tool or predecessor effect.

`--stdin-file PATH` and `--empty-stdin` are mutually exclusive. A file path is
recorded literally; relative paths use the candidate source root as their
declaration context. The observer requires a regular file through no-follow
ancestor descriptors, reads at most 16 MiB once, retains `stdin.bin`, and sends
those same in-memory bytes through the actual child's input pipe. The empty
option sends an empty pipe. The consumer validates retained bytes, length,
mode and the source declaration. This binds supplied bytes, not how many
bytes an application consumed. Without either option, inherited stdin and
its unqualified acquisition status remain unchanged.

V3 also records external PATH resolution and executable byte bindings for
`python`, `python3` and `py`, separately from observer Python. Relative and
empty PATH entries, and Bash/Git version observations, use the actual child
source cwd. The recorded fallback argv describes external resolution only;
shell functions, aliases, startup code and launcher interpreter resolution
remain unqualified. No arbitrary startup or launcher inspection is implied.
The overall environment coverage remains `PARTIAL_NOT_TOOLCHAIN_CLOSURE`.

`--capture-dist` acquires exactly the source root's `dist/` namespace before
and after the process. Missing `dist/` is explicit. An existing namespace must
contain ordinary directories and regular files; symlinks, dangling links,
special files and acquisition races refuse safely. The recursive snapshot
retains complete membership, directory/file modes and raw file bytes, bounded
to 4,096 entries, depth 32, 16 MiB per file and 64 MiB total per snapshot.
Before/after snapshots do not establish intervening event history or acquire
any other ignored namespace.

The consumer rederives both retained snapshots and their inventory. Live
currentness then uses only the qualifier's actual source root: the original
declared source cwd must agree, and current `dist/` must equal the retained
after observation. Imported context text never selects a filesystem to read.
A restored record with unavailable original source retains verifiable
snapshot bytes but refuses currentness; comparison cannot silently rebase it.
This finite namespace matters to existing canonical operations: the recursive
text guards scan extra `dist/` members, and `build-release-asset.sh --check`
first checks the two fixed release assets against live changelog history.
The existing `--check-stale-release-set package <dist> <CHANGELOG>` interface
can exercise that latter predicate without building. Missing assets are not
themselves a stale-publication failure, although a changed declared snapshot
still invalidates its retained currentness binding.

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

The portal's original overwrite/cleanup gap has a separate finite opt-in
interface, described below. A post-run snapshot still cannot recover a
generation that was already deleted without that interface. Historical
endpoint-only records retain that limitation.

The runner acquires its complete command stream through one nonblocking,
no-follow regular-file descriptor, with a 16 MiB bound and before/after file
identity checks. It waits for the acquirer's actual successful exit before
validating framing and the digest or executing any node. A replaced final
symlink, FIFO, oversized file, partial stream or failed acquirer refuses.
Once acquired, replacing the pathname cannot change the retained commands.
This closes the observed final-component check/open race; it does not acquire
the ancestor namespace, Python startup closure or every command's inputs.
The same Bash process still preserves argv, stdin, shell state, traps and
fail-fast behavior. These controls run in `tests/work-graph-stream-cases.py`
through the existing verifier test family.

The whole-run comparator retains raw-byte equality. Two successful full
executions are different evidence from a failed raw comparison. No temporary
path, fixture commit identity, command, result, artifact or meaningful output
is normalized away. Raw equality also does not independently establish
transitive output-artifact semantics. The current source incorporates the
formerly reserved registry, governor load-map/applicability and semantic-pin
repairs through their actual owners. Historical separate-overlay results remain
bound to those overlays. Package and execution results must identify the exact
combined source used; they do not transfer to a later source by description.

## Opt-in portal invocation handoff (C4)

```bash
/usr/bin/python3 -B scripts/qualify-work-graph-verifier.py dag \
  /absolute/fresh-evidence --retain-portal-events
```

The same option is accepted by `legacy`; it may be combined with the existing
v3 acquisition options and the C5 event option below. It explicitly selects
`implementaudit.verifier-run.v4`, which adds nullable `portal_events` and
`repro_events` to the v3 members. Capture without either event option keeps
its original v2/v3 schema and behavior. The v1–v3 readers remain available at
their original evidence ceilings. Relabelling v4 as an older format refuses.

The qualifier creates one private external `portal-events/` destination and
passes its absolute request path in `IMPLEMENTAUDIT_PORTAL_CAPTURE`. An
inherited value, including an empty value, refuses a new capture. This is a
finite request, not a credential or a callback command. The repo-only
`portal-event-capture.py` helper accepts only the two existing portal operations
and the source-owned test/fixture lifecycle hooks. It is not packaged, installed,
registered as another verifier family, or used by the compiler or runner.

### Exact supported invocation population

The supported profile is `DOCS_PORTAL_TEST_V1`, bound to the exact inspected
builder, checker, docs test and nested verifier source hashes in `SOURCE_PINS`.
It requires the existing zero-argument mapped node
`COMMAND:tests/docs-portal.test.sh:0`. Changed executable/test source refuses
until that finite contract is reviewed and updated. Source data still follows
the real builder and checker; their verdicts are not replaced.

The current successful profile has **49 actual invocations: 17 builds and 32
checker calls**. Eight builds and seven checkers exit zero. Nine builds and 25
checkers intentionally exit one. Each slot independently declares its operation,
expected exit, canonical/fixture/nested source context and original output class.
The fixed population detects a missing final event even if a restored manifest
declares only its surviving records. Expected negative checker exits remain
`FAILURE` results; the enclosing test expectation can be satisfied by them.

The test registers its actual Bash process and fresh private temporary root.
The helper checks live Linux process ancestry against the qualifier and that
registered node, retaining process start ticks and both proc and namespace PID
observations. Copied fixture scripts have one explicitly registered fixture
root. Their literal cwd remains the candidate root, while their effective source
root remains the distinct copied tree. The nested `verify-docs-portal.sh` build
and check belong to the same existing test node.

### What is retained before a caller can delete it

The opt-in entrypoint supervises a real child process. It forks the current
Python interpreter and compiles the acquired exact builder/checker source bytes
in that child with the original argv, cwd and main entrypoint. The request is
removed only from that inner child's environment to avoid recursive capture.
The unchanged oracle produces the actual raw stdout, stderr and integer exit.
The supervisor writes the exit durably before artifact/currentness checks and
later JSON processing, then forwards the raw streams and ordinary exit to the
caller. Stream timing and cross-stream interleaving are not compared.

Each successful build gets an invocation ordinal and distinct generation ID.
Its complete output is copied before the build returns. Rebuilding the same
path cannot replace its earlier retained generation. Each checker input is
copied before the actual checker runs, including the intentional negative
inputs. Membership, ordinary file/directory kinds, modes and raw bytes are
retained, including the original `generated_at` timestamp. The consumer does
not normalize timestamps, paths or inert comments. A missing metadata file or
altered required proof strip fails the actual checker; an inert HTML comment
can pass that checker while still changing the retained artifact identity.

Checker input membership, content, modes and live device/inode/size/mtime/ctime
observations are compared again after the child returns. Ordinary write-and-
restore or path replacement changes those observation stamps and refuses.
This is a bounded observation window, not hostile-kernel or equal-UID writer
authentication. Copied or mutated inputs have their own observed identities.
A produced/consumed link is recorded only for the most recent successful build
at the same original path and source root whose complete artifact equals the
actual checker input. Failed builds never create a successful generation from
an older tree left at that path. The intentional unsafe `--out .` failure has
no output snapshot, so it cannot cause a repository traversal.

The source context includes the exact loaded producer, checker and helper
bytes, the inspected owner scripts, declared portal source observations and
the qualifier's original source/run/node mapping. The actual forked Python
executable, version, flags and environment digests are observations; they do
not establish complete dynamic-library, startup or transitive-read acquisition.
No private inherited environment values are exported.

### Receiving checks, bounds and authority

The real `verified_record` consumer validates the original request, source/node
mapping, exact ordered event population, event chain, actual raw results,
generation links and every retained artifact. The node, fixture, nested-output
and return records are sealed with their original bytes and modes; their
declared process-parent chains are checked for internal consistency. Missing, extra, reordered,
duplicate, stale, foreign, corrupt, symlink or unsupported members refuse.
Nested source observations require their complete typed populations and byte
bounds. Runtime observations require their exact schema, an absolute executable
path, bounded version/flag values and valid digests. Checker identity stamps
must agree with each retained member's kind, mode and byte count. Resealing an
incomplete source context, invalid runtime record or impossible stamp does not
make that record admissible.
Successful outer execution requires the complete profile and successful node
return. Failed or pre-node execution can retain explicit incomplete evidence;
an observer failure leaves the already completed child exit and raw logs in
place without issuing a successful handoff.

The profile requires Linux process observations, POSIX fork and no-follow
directory descriptors. Artifact snapshots are limited to 4,096 entries, depth
32, 16 MiB per file and 64 MiB per tree. Raw streams are limited to 8 MiB each;
declared portal source observations also have a 64 MiB aggregate byte bound;
the executable observation is limited to 128 MiB. A child has a 120-second wall
limit. The session has a 512 MiB retained-artifact/stream bound and at most 64
event slots; the required current profile is the smaller exact 49-slot set.
Concurrent writers to one capture refuse. Exclusive creation prevents silent
replacement of earlier records. Ordinary test and nested-verifier cleanup
continues to remove their temporary output; retained external snapshots remain.

Own-process supervision establishes the stated live invocation/return custody.
Restored or resealed JSON receives **declared integrity/consistency only**. Run
IDs, process IDs, digests and node labels cannot authenticate an imported issuer,
hostile equal-UID process, native controller, route satisfaction or accepted
JOIN. This C4 increment does not qualify C1, C2, C3, C6 or C7, full-canonical
equivalence/reuse, R003A host attribution, conversion, retirement or closure.
The original canonical verifier remains the rollback route.

The finite lifecycle and integrity controls are in the already registered
`tests/work-graph-verifier-cases.py` and `tests/docs-portal.test.sh`. A focused
retained run avoids an unnecessary full legacy/DAG pair:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  tests/work-graph-verifier-cases.py --portal-only \
  --retain-fixtures /absolute/fresh-portal-evidence
```

## Opt-in reproduction invocation handoff (C5)

```bash
/usr/bin/python3 -B scripts/qualify-work-graph-verifier.py dag \
  /absolute/fresh-evidence --retain-repro-events
```

`legacy` accepts the same option. It can accompany `--retain-portal-events`,
`--retain-repro-assets` and the other explicit acquisition options. C5-only
capture uses v4 with `portal_events=null`; C4-only capture has
`repro_events=null`. The exact v1–v3 field sets remain unchanged. The parent
passes one fresh absolute external `repro-events/` destination through
`R0035_REPRO_EVENT_CAPTURE_DIR`. Ambient capture and `REPRO_SOURCE_REF`
overrides refuse before launching the verifier. This option requires the exact
event-capable producer above, an acquired tracked capture helper, and the
existing registered zero-argument reproduction test node.

The finite `REPRODUCIBLE_RELEASE_ASSET_C5_V1` profile retains the original
nineteen child invocations in order: two builds, three release-file comparisons,
two checksum checks, two plugin-manifest producers and their comparison, two
skill-manifest producers and their comparison, and six hash producers. Counts
alone do not establish completeness. The receiving helper checks the required
roles, actual argv and stdin, source identities, cwd, exit codes, retained
operands and output semantics. Successful comparisons must agree with their
inputs; successful manifest, checksum and hash outputs must describe the actual
retained artifacts. An expected or unexpected failed child remains a failed
event with its actual exit and raw streams.

The inner record uses `implementaudit.repro-events.v2`. Immediately after a
child returns, an exclusively created and synced `processes/NN.json` preserves
its actual integer exit, raw base64 stdout/stderr, invocation, stdin, timing,
run and source binding. This happens before post-child input, output, source,
executable or artifact acquisition. A later observer failure retains that
receipt and an explicit failed handoff; it cannot silently retry or satisfy a
complete profile. Partial acquired blobs remain bounded and inventoried as
`unhanded_blobs`. The record always declares `process_results`,
`handoff_failures` and `unhanded_blobs`; a complete profile requires nineteen
matching process receipts and events, with no failed handoffs or unhanded blobs.

The input observer refuses a FIFO, alias, special file or unsupported nested
namespace before dispatch, recording `NOT_STARTED_UNSUPPORTED_INPUT` and a
null exit. An ordinary-file comparison still retains its actual unequal exit
1 or missing-operand exit 2. Each raw stream is limited to 8 MiB; the explicit
26,563,928-byte process-receipt bound accommodates both base64 streams and
bounded metadata. Process receipts and acquired blobs share a 128 MiB total
bound. These bounds do not turn a failed acquisition into successful evidence.

Successful build and manifest generations are retained before their existing
cleanup. Every consuming child receives its original operands; the helper
records their bytes, modes, membership and ordinary live identity stamps before
and after consumption. The original cleanup still runs. Partial/failing profiles
remain explicitly incomplete, and no failed build's residual directory is
promoted to a successful generation. Ordinary write-and-restore changes ctime
and is detected within the observation window. These checks do not authenticate
an imported issuer or protect against a hostile kernel or equal-UID writer.

The qualifier's receiving boundary reacquires the exact helper bytes used for
readback and compares them with the captured source owner. It binds the C5
record and session to the outer source commit/tree, producer/helper identities,
registered node, literal original output and original repository cwd. Missing,
corrupt, stale, foreign, incomplete-success or unsupported records refuse. If a
failed canonical prefix never reaches the reproduction node, its absent capture
is retained as `UNQUALIFIED_PARTIAL_OR_FAILED_PROCESS`; it is not a completed C5
profile. The actual outer exit is durable before these receiving checks.

The comparator compares the raw event declarations, including paths and run
identities. It does not normalize two independent captures into equality.
Imported readback remains **declared integrity/consistency only**. Source pins,
run IDs and successful readback do not establish native currentness, authenticated
effect admission, governed dispatch, accepted JOIN or release authority.

The helper is repo-only, and its controls run through the existing
`tests/work-graph-verifier.test.sh` family. `ProfileCases`, `FailureCases` and
`DurabilityCases`
exercise actual finite child execution, integrity and failure handling;
`QualifierCases` exercises both legacy/DAG v4 handoffs, receiving mutations,
partial failures, ambient refusal and the additive v3 profile. The separate
`Lifecycle` case executes the actual official package producer.

C4 and C5 close their finite internal-generation observation gaps. Full canonical
runtime/startup acquisition (C1), execution namespace/Git acquisition (C2),
mutable resource contracts (C3), shared-shell effect transfer and protected
receipt custody (C6), and full acquire/execute/consume currentness (C7) retain
their separate qualification requirements. They remain portable engineering
work where executable semantics permit; they are not relabelled native-only.
The complete canonical registry retains its serial no-reuse fallback until
those requirements and actual consumer evidence support a wider admission.

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

The shared selection loop charges each selected or ACTIVE entry
`max(1, resource_demand)` capacity units. A zero declared demand remains a valid
source value; it cannot erase the entry's occupied slot. Positive demand keeps
its existing charge, including an ACTIVE demand exceeding current capacity.
The same rule applies to the original supplied-fact A/G consumer and the
native-format frontier. Constructed controls cover zero host capacity, an
explicit zero ceiling, an absent ceiling, reserve, mixed demands and occupied
ACTIVE entries. They do not authenticate an actual host roster.

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
