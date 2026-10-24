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

`join(consumer, expected_old=...)` accumulates contributors across batches and
calls the compiler's existing JOIN verdict implementation. Missing, failed,
partial, pending, nonverdict, correlated and contradictory contributions do
not produce a completed required JOIN. Declared optional omission adds no
credit. A new JOIN completion must itself be selected by the existing
capacity, ACTIVE-resource, and context-cost rules. A previously recorded
unchanged JOIN returns its existing completion identity without another event.
A completed JOIN can make the source-declared successor eligible under the
portable contract; it cannot mark a PLAN, PHASE or campaign complete.

## Custody and interruption

The journal is a bounded, hash-linked historical record with a cooperating
single-writer file lock and a per-instance operation lock. Each append checks
an exact expected-old identity, writes and fsyncs a new pending file, rechecks
the old journal, replaces it, and fsyncs the directory. A pending transaction,
torn record, foreign run identity, changed physical path or stale preimage
refuses. Failed transactions and old history are not silently repaired.

A restarted process retains the historical evidence but does not restore
completion authority from JSON. Previously recorded nodes are held as
`RECOVERY_CUSTODY_UNVERIFIED`; unrelated preparation can remain eligible. The
receiving producer must reestablish custody before an operational receiver can
resume those scopes. This companion supplies no import/recovery credential or
external-effect retry command. It cannot recover an external producer's
unobserved execution or make observation and later external effects atomic.

Each session bounds history to 1,024 events and 64 MiB, and retained issued
frontiers to 1,024. Exceeding a resource bound refuses; it does not grant
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
bash tests/native-work-graph.test.sh
```

The source increment advances portable portions of R35-N04, D01, D02, D05,
D06, D07 and D08, plus the corresponding P01, N01/N02/N04/N05/N06 and
H01/H02/H03/H04 case contracts. Capacity, semantic-conflict and context holds
are tested through the unchanged compiler rules. These statements describe
source/consumer scope, not full original-criterion acceptance. The original
48 requirements, 20 cases, 117 verifier nodes, eight raw-comparator failures,
native populations and authentic acceptance gates remain binding.
