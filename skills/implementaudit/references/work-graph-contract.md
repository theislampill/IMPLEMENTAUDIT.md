# Work graph source and transition contract

R0035 owns this optional compiler contract. It does not change the governor,
four-child population, one-child-per-derivation rule, host policy, canonical
verifier route or campaign state. All projections return authority `NONE`.
Graph consistency, a result envelope, an exit code and a digest are evidence
inputs; they do not grant native currentness, routing, acceptance or closure.

## Compatibility and invocation

The recovered `WORK_GRAPH.json` v1 projection, product/preparation contracts,
proximal modes and `--native-a-g` remain caller-fact interfaces. In particular,
v1 does not read adjacent STATE files. No existing caller is silently upgraded
to native acquisition. Integer-only, signed-64-bit canonical JSON, UTF-8 scalar
strings, duplicate-key rejection and existing event identities remain intact.

For a standalone-diagnostic of explicitly annotated native-format files:

```text
python -B <skill-dir>/scripts/compile-work-graph.py --inspect-native <run-root>
```

This mode labels the result `CONSTRUCTED_FILESYSTEM`, even when the directory
looks like a real run. It cannot authenticate a controller. It creates no graph
file, process, receipt, claim, hook, native state change or output queue.

The following explicit native operations require the existing sibling
`claim-run.sh` to read and verify the actual current controller and continuity
receipt, matching the exact run root. They repeat that read after acquisition:

```text
python -B <skill-dir>/scripts/compile-work-graph.py --native-run <run-root> <repo-root>
python -B <skill-dir>/scripts/compile-work-graph.py --select-native <run-root> <repo-root>
python -B <skill-dir>/scripts/compile-work-graph.py --recursive-native <run-root> <repo-root> <history.json>
python -B <skill-dir>/scripts/compile-work-graph.py --reconcile-native <run-root> <repo-root> <dispatched-graph.json> <dispatch.json> <results.json> <join-id>
```

Missing, stale, foreign or ambiguous continuity refuses with exit 2. These modes
never initialize or resume a controller. The CLI reacquires live files before
result reconciliation. Python result APIs accept explicitly supplied snapshots;
they cannot independently authenticate their caller's claim of a fresh read.
`NATIVE_CONTINUITY_VERIFIED` describes the existing helper's successful read,
not host attribution, actual capacity, package discovery or effect prevention.

Ordinary zero/one/fewer-than-three-cell work, one ready cell, strict dependency
chains and insufficient capacity retain the governor's cheap serial path. The
compiler is not a mandatory artifact for those cases. `cheap_path_v1` reports
the bounded threshold without creating a file or invoking a child. Serial work
still owes the same currentness and consequential JOIN gates.

## Explicit native metadata, not prose inference

This is a proposed opt-in native representation. Existing legacy runs without
it are **unsupported**, not empty or complete. Adoption by the STATE/phase/task
writers remains a serial integration operation. No migration or inference from
summary counts is performed. Do not manufacture an annotated campaign or a
continuity receipt merely to obtain a native-positive test.

The compiler enumerates STATE.md, ROADMAP.md, and every `.md` file recursively
under `plans/`, `phases/` and `tasks/`. It rejects missing required documents,
symlinks, unknown/missing/multiple blocks, duplicate IDs, incomplete inventory,
or contradictory dependency/ancestry facts. Source document paths use ordinary
relative ASCII file/directory names. Other supporting files are outside the
node census; a work specification in another format is not supported by this
version. The native writer must place every obligation in the declared native
specification population before claiming complete intake.

Each source document contains exactly one fenced block named
`implementaudit-work-graph`. Its body is strict canonical-compatible JSON.
All members listed below are required; unknown members are rejected. Prose
outside the block remains captured in source identity and must not supply an
undeclared conflicting execution contract.

| Document | Schema and fields |
|---|---|
| STATE.md | `implementaudit.native-state.v1`: `campaign`, `root`, `original_scope`, complete `nodes` ID array, `event`, `context` |
| ROADMAP.md | `implementaudit.native-roadmap.v1`: `phases`, exactly the phase IDs found in specifications |
| Each specification | `implementaudit.native-spec.v1`: nonempty `nodes` array of the node facts below |

`event` has `id`, `kind` (`RETURN`, `JOIN`, `REDERIVE`, `REMINDER`,
`INTERRUPTION`) and `subject`. Root, campaign, scope and subject are explicit,
nonblank identities. Every node reaches that one root through `parent`; cycles
and foreign roots refuse. All dependency edges are checked for unknown IDs,
cycles and required/optional overlap. A source DONE with an open required
dependency refuses rather than being relabelled to close the arithmetic.

Each node has these fields:

| Fields | Meaning |
|---|---|
| `id`, `parent`, `kind` | Stable identity; parent ID or null for the plan root; `PLAN`, `PHASE`, `TASK`, `JOIN` |
| `state`, `done_evidence` | Source `OPEN`, `ACTIVE`, `DONE`; DONE requires its source evidence SHA-256, other states use null |
| `requires`, `optional` | Complete mandatory and explicitly optional contributor IDs; optional omission gives no stronger evidence |
| `reads`, `writes`, `acceptance`, `resources`, `authority` | Arrays of typed `path:relative/posix/path`, `semantic:owner`, or `scope:boundary` identities |
| `effect`, `authorization`, `independence` | `READ_ONLY`/`PREPARATION`/`MUTATION`/`EXTERNAL`; `PERMITTED`/`MISSING`/`UNKNOWN`; `KNOWN`/`UNKNOWN` |
| `resource_demand`, `rank` | Nonnegative integer occupancy and signed integer stable preference |
| `route_scopes`, `logical_delivery` | Exact declared route scopes; logical delivery identity or null, independent of transaction IDs |
| `future_consumer` | Null or exact `{node, condition}`; mandatory for preparation |
| `invalidators`, `independent_results` | Named external invalidators and whether a JOIN requires independent result sources |
| `context` | `locality` (`GOVERNOR`, `CHILD`, `EITHER`), nonnegative `governor_cost`, `child_cost`, `return_cost`, `useful_value` |

Arrays are sets without duplicate members. Path prefixes conflict hierarchically;
semantic owners conflict even across different filenames. Read/read sharing
alone does not create a writer exclusion. Capacity context has `host_capacity`,
`operator_ceiling` (null, zero or positive), `reserve`, `route_facts` and
`outstanding_deliveries`. Effective capacity is host capacity minus reserve,
then bounded by a present operator ceiling; occupied ACTIVE demand is subtracted.
The declared host/operator evidence is an input, not physical roster attestation.

Every graph binds exact source bytes, document inventory, candidate commit/tree,
worktree digest and continuity where available. Declared `path:` reads and path
invalidators are read and hashed, including directory membership and modes,
before and after compilation. Native mode resolves them under the exact
repository; constructed inspection resolves them under the run root (the Python
API can name a separate constructed input root). Missing reads remain explicit
`MISSING_INPUT`; symlinks and nonregular inputs refuse. Changed input bytes
invalidate their dependent consumers even when specification text is unchanged.
Unresolved semantic read identities conservatively bind the whole native
worktree digest; this is not a proof of a closed dynamic read set.
Final bindings require exactly every declared path read/invalidator, with a
known MISSING/PRESENT_FILE/PRESENT_DIRECTORY record and the corresponding
null/content digest. Acquisition-only parsing cannot yield a dispatchable
graph. POSIX file and directory identities include their own permission and
special mode bits; directory identities also include sorted descendant facts.
This does not qualify Windows permissions or filesystem ACL semantics.
Source documents are included
so serialized projections can be rederived rather than trusting a resealed
READY/count field. These documents may contain private run data: keep native
outputs in the existing controlled evidence boundary. Source SHA-256 is not
proof of ownership or truth. No public/native transcript is produced by default.

## Selection, constraints and placement

The single bounded selection core serves the old A–G and new native interfaces.
New source states produce a closed DONE/ACTIVE/READY/BLOCKED population. ACTIVE
occupancy survives other returns, interruption and unrelated blockage. OPEN
becomes READY only after required source-DONE dependencies and its declared
authorization, independence and route conditions. Containers remain census
members without being automatically dispatched.

Selection is deterministic by rank then stable ID; it respects semantic
read/write, acceptance, authority and resource exclusions against both active
and newly selected work. Capacity zero dispatches nothing even for zero-demand
cells. Placement compares governor cost against child plus return cost, subject
to declared locality and useful value. `DELEGATED_EXECUTOR_CANDIDATE` is an
advisory placement, not a child route or effect-capability admission. R0036 and
the existing governor remain responsible for actual delegation and containment.

MUTATION and EXTERNAL stay blocked with `EFFECT_EXECUTOR_UNAVAILABLE` in this
portable implementation. A prompt's permission assertion cannot clear this
physical gate. Pending/unknown/committed logical delivery holds block matching
delivery identities across transaction labels. They do not impose a global
mutex on unrelated reads or preparation. Clearing a delivery hold belongs to
its effect owner, not this compiler.

## Scoped route facts: proposed consumer interface

R0033 owns current obligation facts. The pinned available route-result v1
producer does not expose a graph-ready blocking-scope fact. Therefore the
following consumer format is **proposed and unaccepted** until the real
producer/consumer pair qualifies it. An offline fact object does not establish
current route satisfaction or support a PreToolUse prevention claim.

`implementaudit.work-graph-route-fact.v1` contains exactly `scope`, `obligation`,
`generation`, `binding`, `continuity`, `status`, `satisfaction`,
`expected_satisfaction` and `source_digest`, plus `schema`. Status is `BLOCKED`,
`SATISFIED`, `NOT_REQUIRED` or `UNKNOWN`. SATISFIED requires the nonnull current
satisfaction to equal the expected current receipt. Missing facts remain
unsatisfied. Changed scoped producer identities invalidate affected consumers;
unrelated preparation retains its input identity. The producer must derive the
expected receipt from its current owner state, never echo the caller's receipt.
`obligation` may be null only for NOT_REQUIRED. The portable constructed reducer
tests this proposed vocabulary. In native acquisition, every scoped node stays
blocked with `ROUTE_PRODUCER_UNAVAILABLE`, including a STATE scalar claiming
SATISFIED or NOT_REQUIRED: this version has no admitted authenticated producer.
Unscoped independent work remains eligible. Removing this hold requires the
real producer/consumer qualification, not a new caller-supplied receipt field.

No hook adapter is installed. Stable node/graph identity, current R003A host
binding, R0036 task/executor mapping, authenticated R0033 facts, authority,
effect capability, exact covered tool path, trusted enabled hook and qualified
failure semantics remain necessary for any future conditional interlock. Pure
reads, currentness/route support and containment are not blanket blocked by a
new universal firewall.

## Results, scoped JOIN and changed source

`implementaudit.work-result.v1` has exactly `node`, `dispatch_id`, `graph_digest`,
`input_digest`, `status`, `terminal`, `exit_code`, `evidence_digest`,
`independence_key`, `scope`, plus `schema`. Status is PASS, FAIL, PARTIAL,
NONVERDICT, UNKNOWN, PENDING, INTERRUPTED or TRANSPORT_FAILURE. PASS requires
terminal=true, exit=0 and a SHA-256 evidence identity. A PASS-like message or
zero subprocess exit alone is not such a result. Scope is exactly the returned
node; it cannot grant its parent or another contributor's credit.

Unknown, duplicate, undispatched, stale and contradictory results refuse. Missing
or nonterminal required results remain PENDING. All required contributors must
settle; failure remains failure, and partial/interrupted/nonverdict returns
cannot satisfy the JOIN. Independence-required JOINs reject identical evidence,
correlation keys and declared common reads/dependencies as independent proof.
The comparison includes each contributor's transitive required and optional
source closure, inherited read/invalidator overlap and repeated DONE evidence.
Without separate evidence of optional consumption, every declared optional
source is conservatively included. This evidence check does not turn ordinary
read/read scheduling into a mutex.
The successful status is `SATISFIED_AT_DECLARED_RESULT_CONTRACT`, with authority
and lifecycle credit NONE. The actual consumer still must inspect evidence and
perform its independently authorized accepting operation.

Before consumption, a changed graph yields `RECOMPUTE_REQUIRED`, with affected
and preserved evidence identities. Per-node input identity includes source,
required/optional dependency closure and scoped route/delivery facts. Parent
summaries also reconsider. Candidate/continuity owner changes invalidate use
globally; local changes retain demonstrably unaffected nodes. This retains
evidence, not authority to accept it under a new graph. Multi-event/batched
accepted-result reuse requires the existing governor/R0036 custody consumer;
the same-dispatch pure JOIN API does not invent that missing acceptance chain.

## Recursive transition and portable execution evidence

On material RETURN/JOIN/re-derivation, the compiler traverses the subject's
whole named ancestry and enumerates INWARD children, OUTWARD siblings at every
ancestor, FORWARD preparation with actual future consumers, and BACKWARD JOINs.
The same source graph supplies selection; direction labels do not dispatch work.
An effect block does not remove a separately eligible preparation edge.

Each selected output has a named consumer and accepting condition. The portable
execution checker takes the exact graph and event history and rederives the
complete transition before consuming it. Resealing omitted ancestors, siblings
or selections cannot satisfy that check. It requires one matching execution and a digest-matched,
decision-changing consumption for every selected edge. Empty execution with
eligible selected work fails even if a separate source-consistency checker is
green. Capacity, conflict and context deferrals are explicitly derived by the
selector; a missing execution is not silently converted into a valid deferral.
The checker validates supplied execution records; it does not attest an
unobserved process or native consumer. The regression harness separately runs
real bounded subprocess work over each selected node's exact acquired inputs
and inspects its actual output bytes. Execution records bind node, dispatch,
graph, input digest, input-root identity, exact path read set, output SHA-256
and integer exit. Consumption records bind the same input identity/read-set
digest, output SHA-256, named consumer/condition and changed decision. Foreign
roots and input changes refuse at the actual portable consumer.
The pure checker reports `PORTABLE_RECORDS_CONSUMED`, explicitly limited to
source-bound records; process attestation remains external to it.

An exact consumed event receipt suppresses redispatch. Reused event identity
with changed graph or incomplete consumption refuses; a genuine changed event
requires fresh source derivation. No graph source or campaign ledger is written.
Natural campaign-transition acceptance remains separate from the portable test.
Replay reports `NO_REDISPATCH_AT_SUPPLIED_HISTORY`, not new execution credit;
native history custody remains the governor's accepting responsibility.

Source relation graphs, guarded triads and pairwise green reports are not
executable work cells or global liveness proof. TC07 still needs the actual
joint configuration and progress witness. TC06 transfer/retirement still owes
all supported consumers, in-flight descendants and recovery obligations.

## Verifier graph boundary

The same compiler maps the complete canonical verifier bytes into a composed
prelude, ordered command nodes and final operations. It derives test membership
from the current registry and checks the exact population; no fixed historical
test count is used. Prelude inline assertions, shell state, conditional release
checks and cleanup retain their canonical owner. Unknown tail grammar or stale,
missing or duplicate obligations refuse. The optional qualification transport
executes the mapped chunks in one shell and records raw streams, process exit
and node start/end observations without switching canonical execution.
The transport receives the rederived stream digest and validates the entire
frame population before execution. It closes its dedicated framing descriptor
before running commands and preserves caller stdin. The capture persists the
nested integer process exit before later recording work, and uses integer
`elapsed_ms` so canonical JSON cannot lose a completed result to a float.

All verifier nodes initially retain serial order and shared repository/shell
constraints. Transitive dynamic shell read/write sets and evidence-artifact
semantics are unqualified; selective cached verifier reuse therefore refuses.
Generic native-graph selective invalidation is not a claim that verifier read
sets are independently closed. Raw observable correspondence, reviewed route
conversion and legacy retirement are three distinct accepting operations.
