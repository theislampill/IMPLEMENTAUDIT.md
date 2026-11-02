# R0035 constructed process and logical-delivery controls

`tests/work-graph-process-delivery-cases.py` adds five bounded controls over the
existing repository `CompletionContract` and unchanged compiler. It reuses the
gated read-only producer from `tests/work-graph-pending-settlement-cases.py`.
It adds no scheduler, executor, governor, delivery adapter or acceptance issuer.

The evidence acquisition remains `CONSTRUCTED_FILESYSTEM`. The owned child
processes are real, but the source declarations of capacity, ACTIVE state,
semantic resource claims and logical-delivery holds are constructed test data.
They are not an authenticated native process roster or delivery ledger. All
completion and JOIN results retain authority `NONE`, native dispatch false and
no lifecycle credit. These controls do not change the original acceptance
population or qualify a natural original case.

## Actual process overlap and current selection

The three process controls obtain an existing completion frontier selecting A
and B, start two separate read-only gated children, and observe both alive
before accepting their individually scoped PENDING results. Their observed
lifetimes are then reflected in physically written ACTIVE source declarations.
The existing compiler rereads those documents when deriving occupancy and
selection; no caller-supplied accepted history or alternate selector is used.

One child finishes and is reaped while the other remains observably alive.
Before settling the finished child's original pending frontier, the fixture
restores that node's original OPEN declaration. Changing a node to ACTIVE
changes its source identity, so the test does not bypass that invalidation or
claim that the earlier result remained applicable during the ACTIVE source
change. The unfinished child's ACTIVE declaration remains in the fresh source.

The controls exercise three distinct contrasts:

| Control | Observed relationship |
|---|---|
| Overlap and partial return | Two children overlap; A finishes while B remains alive; independent preparation completes before B returns. |
| Capacity | Two observed ACTIVE children occupy a declared capacity of two; at the same occupancy, declared capacity three makes one preparation slot available. |
| Semantic conflict | With free capacity, an overlapping semantic resource claim defers one preparation while disjoint preparation completes; removing only that overlap makes the first preparation eligible. |

Both original required contributors ultimately settle through their original
frontier. The existing JOIN reducer consumes their scoped result envelopes;
the retained JOIN predecessor identities and evidence digests are checked
against the actual child outputs. In the overlap control, an actual successor
also reads the retained A/B bytes from its declared input. Original pending
events remain in history, and no ancestor or campaign completion is inferred.

All children are owned by the test fixture. Each successful producer is waited
for and reaped, and cleanup terminates and reaps a still-live child if a control
fails. The existing producer code and process-owner custody checks are reused.

## Fixed no-effect ledger and current bytes

The two delivery controls own one private JSON file at
`inputs/no-effect-ledger.json`. Its fixed schema labels the fixture's effect as
`NONE`; it records a logical-delivery identity and distinct transaction/event
IDs with PENDING or UNKNOWN states. No send, network operation, external effect,
retry or operational delivery adapter exists in this fixture.

The fixture writes the ledger, reads those physical bytes back, and derives
the existing source hold's `source_digest` from that read buffer. Both read-only
delivery probes also declare the ledger path as an input. The compiler's fresh
read-set identity is checked against the actual ledger bytes and file mode.
The source event and hold are explicit constructed projections of the owned
ledger, not authenticated assertions about an external delivery service.

Before adding a hold, both read-only probes must be selected. PENDING and
UNKNOWN entries with different transaction/event IDs then hold both probes
through the same logical-delivery identity. Unrelated preparation remains
eligible, actually completes, and retains its result after the transaction
changes. A separate genuinely EXTERNAL node remains refused specifically by
`EFFECT_EXECUTOR_UNAVAILABLE`; that independent refusal cannot satisfy the
read-only hold assertions.

The currentness control changes the physical ledger during an existing compiler
observation and requires its closing guard to refuse the changed input. Before
updating the source hold projection, a fresh read must already bind the changed
ledger bytes. The read-only probe is still READY at that point, but its old
terminal envelope must refuse because its original input identity is stale.
Only afterward does the fixture publish the current ledger-derived hold and
reacquire it. This distinguishes byte currentness from a result that merely
fails because a hold or unavailable external executor already blocked it.

The compiler does not acquire or authenticate a service-specific ledger here.
The controlled projection and file input establish only this bounded portable
source contract. Genuine external delivery outcomes remain with their existing
effect owner, and historical JSON never restores live completion custody.

## Focused invocation and receiving boundary

Run only the five additive controls with:

```sh
/usr/bin/python3 -B tests/work-graph-process-delivery-cases.py -v
```

The test depends on the reviewed pending-settlement fixture and process-bound
completion owner. Receiving integration must retain those exact prerequisites
and add this Python child to the existing native-work-graph test wrapper under
the canonical registry. The tests themselves do not modify the wrapper or any
source pin. No namespace execution or broad package bank is needed for their
ordinary read-only children.
