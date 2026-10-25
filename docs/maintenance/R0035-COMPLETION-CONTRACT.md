# R0035 portable completion consumer

`scripts/work-graph-completion.py` is a repository companion for the original
R0035 completion/history/frontier contract. It does not execute tasks, issue
acceptance, route children, or authorize native dispatch. The installed
compiler owns readiness, selection and JOIN normalization. The companion owns
fresh filesystem observation, declared-result applicability and retained
contract history. No installed path depends on this repository-only companion.

## What is implemented

`CompletionContract(run_root, journal_root, input_root=...)` reads the actual
native-format run documents and declared input files through the compiler's
constructed-filesystem observation. The source/input closing guards finish
before an issued frontier or journal update is returned. The compiler is
loaded from the fixed physical path by executing exactly the captured buffer;
its physical identity and bytes are rechecked on every operation. This profile
requires POSIX file locking and no-follow file operations.

The original source graph remains immutable. `derive_completion_frontier_v1`
validates and rederives it, applies a separate non-authoritative completion
projection, and uses the existing readiness and capacity/conflict/context
selection. It preserves source authorization, effect-executor, route,
independence, missing-input and logical-delivery holds. Unrelated ACTIVE
occupancy remains occupied. A source DONE label without bound completion
history is held by this stricter companion; the original public graph API
retains its previous source-declaration semantics.

The companion accepts only individually scoped TASK result envelopes from a
frontier object it actually issued. It preserves each original graph,
dispatch, input and consumer identity. Partial returns from one dispatch may
arrive separately, provided fresh source checks and the originally consumed
prerequisite result identities still apply. Changed source, input, acceptance
premise or global continuity binding invalidates affected use. Unaffected
accepted contract results remain available. Supplied JOIN result envelopes
are refused.

### Live pending settlement

An accepted `PENDING` envelope retains a live settlement slot on the exact
original issued frontier object. The same `CompletionContract` instance may
later accept one terminal envelope for that contributor through `accept()`.
It must retain the original dispatch, graph, input, single-node scope, consumer
and independence identity, the original required/optional predecessor result
identities, and an exact current `expected_old` history digest. Fresh source
and input checks must still apply; the only current node hold that this path
may settle is `COMPLETION_PENDING`. A second otherwise equal frontier object,
a copied projection or a reissued frontier cannot take over that pending slot.

Settlement appends a new BATCH event. The original pending event remains
unchanged in the hash-linked history. The current live result and recursive
completion projection use the terminal record; neither treats the old pending
record as a second completion. Other contributors from a partially returned
frontier can still arrive independently. Repeated pending returns, nonterminal
replacements and terminal replay refuse without appending history. A terminal
failure may settle a pending contributor, but it cannot satisfy a successful
required JOIN. A stale expected-old refusal does not itself consume the live
pending slot; retry still requires fresh applicability and custody checks.

This is declared-result settlement within one live receiver. The companion
does not start, wait for or authenticate a producer. Its caller remains
responsible for actual execution and process cleanup. Reopening the journal
does not reconstruct the issued object or pending custody, and no JSON import
or retry API is added. The resource bounds and native authority ceiling below
continue to apply.

`join(consumer, expected_old=...)` accumulates contributors across batches and
calls the compiler's existing JOIN verdict implementation. Missing, failed,
partial, pending, nonverdict, correlated and contradictory contributions do
not produce a completed required JOIN. Declared optional omission adds no
credit. A new JOIN completion must itself be selected by the existing
capacity, ACTIVE-resource, and context-cost rules. A previously recorded
unchanged JOIN returns its existing completion identity without another event.
A completed JOIN can make the source-declared successor eligible under the
portable contract; it cannot mark a PLAN, PHASE or campaign complete.

## Completion-aware recursive transition

`transition()` is an argument-free alternative to `frontier()` for a receiver
that needs recursive reconsideration. Both methods use the same freshly derived
completion frontier, dispatch identity, selection, capacity, conflict rules and
live-frontier custody. The transition can be passed directly to `accept()`;
a copied, modified or caller-resealed projection cannot replace the exact
issued object. The source and input closing guards finish before either method
issues a result. Calling either method alone records no execution or consumption.

The existing compiler owns the shared ancestry, direction and bounded-consumer
enrichment. Its original `compile_recursive_transition_v1(graph, history)`
entry retains its native-source selection and supplied-history semantics. The
new repository consumer does not substitute a completion list into that native
entry, alter the original source graph or introduce another selector.

A completion transition retains the current source event and complete
same-campaign root, original scope, source graph identity, INWARD/OUTWARD/FORWARD/
BACKWARD projections and actual selected consumers. It additionally projects
only journal records that remain applicable in this live completion session.
Each projected journal event retains its original and currently retained scope;
each record retains its own dispatch, source graph, input, result digest,
required/optional predecessors, effect/authority description and future consumer.
`retained_ancestry` follows each such record through the current source ancestry
to the explicitly named campaign root, and `retained_directions` preserves its
own four directional projections. A material return from another branch is not
collapsed into the current source event's local subtree. A partially invalidated batch cannot
turn its surviving contributor into whole-batch or ancestor completion.

These journal events are portable result-contract evidence. They do not claim
authentic native RETURN/JOIN occurrence or an accepting issuer. A reopened
journal contributes no live completion event or retained-ancestry credit and
keeps its recovery holds. Current FAIL or PARTIAL records remain visible as
such; they cannot satisfy a required successful JOIN. Changed inputs or premises
invalidate affected use while independent retained evidence, ACTIVE occupancy,
resource conflicts, authority blocks and useful unrelated preparation remain
under the compiler's existing rules.

The schema is `implementaudit.completion-transition.v1`, with evidence scope
`PORTABLE_DECLARED_COMPLETION_TRANSITION`, `authority: NONE`,
`native_dispatch_authorized: false` and `native_campaign_proven: false`.
The transition is a source-bound receiving projection, not a new execution loop,
native event source, lifecycle controller, persistent-cache credential or
positive external-effect recovery grant. PLAN/PHASE/campaign completion remains
outside the companion's TASK/JOIN projection.

## Custody and interruption

The journal is a bounded, hash-linked historical record with a cooperating
single-writer file lock and a per-instance operation lock. Each append checks
an exact expected-old identity, writes and fsyncs a new pending file, rechecks
the old journal, replaces it, and fsyncs the directory. A pending transaction,
torn record, foreign run identity, changed physical path or stale preimage
refuses. Failed transactions and old history are not silently repaired.

The live receiver and journal are bound to their creating process. An inherited
instance after `fork()` refuses use before acquiring the inherited thread lock
or reading/appending journal state; inherited frontier objects carry no
settlement custody in the child. Threads in the original process continue to
share the serialized receiver. `close()` in an inheriting child is cleanup only:
it closes that child's descriptor without acquiring the inherited thread lock
or explicitly unlocking the shared writer gate. It does not release the
original parent's gate or restore custody. The original live parent can still
settle its pending results after that cleanup.

A restarted process retains the historical evidence but does not restore
completion authority from JSON. Previously recorded nodes are held as
`RECOVERY_CUSTODY_UNVERIFIED`; unrelated preparation can remain eligible. The
receiving producer must reestablish custody before an operational receiver can
resume those scopes. This companion supplies no import/recovery credential or
external-effect retry command. It cannot recover an external producer's
unobserved execution or make observation and later external effects atomic.

Each session bounds history to 1,024 events and 64 MiB, each issued frontier
or recursive projection to 64 MiB, and retained issued frontiers to 1,024. Exceeding a resource bound refuses; it does not grant
completion or omit contributors. These bounds are companion resource limits,
not the original acceptance denominator or a runtime fanout policy.

## Evidence ceiling

All general results are labeled `PORTABLE_DECLARED_RESULT_CONTRACT`,
`authority: NONE`, and `native_dispatch_authorized: false`. A caller's PASS,
subprocess exit or output digest is not an authentic native acceptance issuer.
The process-backed tests exercise actual child outputs and a successor over
constructed graph sources; they do not replace the original native cases.

`observe_fixed_native_completion(run_root, repo_root, input_root=...)` is a
separate fixed-source reader. It accepts no graph, result, producer callback,
policy or native-mode flag. It invokes the existing enclosing native episode
observation, waits for its closing guards, and preserves only the exact
ordinary receiver and exact singleton consumer. It does not promote the
reviewed cognition result into receiving completion, extend the required set,
change `lifecycle_credit: NONE`, restore journal authority, or enable a generic
successor. The current unbound selection/absent producer remains unavailable.

A general native continuation still requires an explicitly admitted existing
producer for each result scope, authentic acceptance/consumption, and an
existing executor that accepts the resulting current frontier. No second
scheduler, execution controller or authority source is added here.

## Verification and original obligations

Run the additive controls with:

```sh
/usr/bin/python3 -B tests/work-graph-completion-cases.py
/usr/bin/python3 -B tests/work-graph-pending-settlement-cases.py
/usr/bin/python3 -B tests/work-graph-completion-transition-cases.py
bash tests/native-work-graph.test.sh
```

The pending-settlement controls keep actual read-only child processes alive
behind a pipe gate, record PENDING while those children are live, then consume
their observed terminal output. They pair this path with a terminal-only
control, preserve pending history, reap every owned child, and discriminate
stale inputs/premises/predecessors, changed consumer/independence, competing
frontier objects, expected-old races, terminal failure/replay, atomic batches
and journal restart. A bounded fork control also requires inherited operations
to refuse while another parent thread holds the receiver lock, preserves the
parent's writer gate during child cleanup, reaps the fork child, and proves
that the original parent can still settle. These controls qualify the portable
receiver only.

The source increment advances portable portions of R35-N04, D01, D02, D05,
D06, D07 and D08, plus the corresponding P01, N01/N02/N04/N05/N06 and
H01/H02/H03/H04 case contracts. Capacity, semantic-conflict and context holds
are tested through the unchanged compiler rules. These statements describe
source/consumer scope, not full original-criterion acceptance. The original
48 requirements, 20 cases, 117 verifier nodes, eight raw-comparator failures,
native populations and authentic acceptance gates remain binding.
