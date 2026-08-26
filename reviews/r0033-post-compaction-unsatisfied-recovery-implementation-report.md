# R0033 post-compaction UNSATISFIED recovery implementation report

## Scope and identity

- Parent commit: `1f6e1e1259e86a499bc57a0c972856a85845cde4`
- Parent tree: `0f088290f5afaf304c4e39f99a8c95dfd8a1d35d`
- Owner: existing R0033 route-transaction and route-obligation contract surfaces
- Scope: later-compaction recovery of one stale `REQUIRED/UNSATISFIED` route into a fresh `STALE_CONTEXT_RECONSTRUCTION -> audit-state` obligation
- Explicit exclusions: transaction-scoped multi-child concurrency, installation, live controller/ref/run-root mutation, STATE/ROADMAP/graph changes, push, tag, release, and acceptance

## Causal failure

The selected G09 fixture created an immutable `REQUIRED/UNSATISFIED` audit-assess route, performed no OPEN or RETURN, relocated the package without changing child bytes, advanced through a complete four-transition continuity/H0 chain, and attempted a current `STALE_CONTEXT_RECONSTRUCTION` decision against the stale record.

Unchanged production failed before the route-ref effect with:

```text
route-obligation-contract.test: active-route recovery causal RED (G09/UNSATISFIED): {"advance_allowed": false, "decision": "REQUIRED", "enforcement_available": false, "error": "an active same-controller route obligation cannot be downgraded or replaced in H2A", "schema": "implementaudit.route-transaction-result.v1", "status": "UNAVAILABLE"}
```

The first attempted run stopped earlier in the selected-case whitelist and was not counted as the causal RED. A later test-only failure showed the inherited `foreign-owner` tamper equalled G09's claim; changing it to a genuinely foreign claim made that control discriminating.

## Correction

`decide` now classifies a stale `REQUIRED/UNSATISFIED` record as a recovery candidate only when its continuity receipt or host-binding generation is no longer the current context. It then uses the same exact recovery predicate as OPEN/RETURNED:

- immutable canonical predecessor bytes;
- same controller, claim, run, host, and host session;
- complete bounded contiguous v3 receipt and retained H0 binding chain;
- distinct current boundary event and digest;
- exact current inputs and current package;
- mechanically required `STALE_CONTEXT_RECONSTRUCTION` mapped solely to current-package `audit-state`.

The predecessor stays immutable and contributes no lifecycle, child, packet, return, governor decision, obligation, transaction, completion, or satisfaction credit. Same-generation exact replay retains its existing idempotent behavior; same-generation replacement or downgrade remains forbidden. OPEN and RETURNED recovery continue through the same predicate.

## Verification

- Focused G09: `FILTERED_NON_QUALIFYING case=G09 selected-case-only` (exit 0).
- Full route matrix: request-free matrix GREEN; G01-G40 matrix GREEN; `61/61` plus HC-H2B route/return/completion/replay and later-boundary UNSATISFIED/OPEN/RETURNED recovery (exit 0).
- H0 host-session binding: `ok (15/15 live R003A cases)`.
- Compact interlock: `ok (fixed namespace + H0 binding + compact stop)`.
- Interruption durability: `ok`.
- Operational evidence: `ok`.
- Continuity contract: `CONTINUITY_TASK6_GREEN=PASS` and terminal `ok`.
- Continuity: `ok (38/38)`.
- Turn disposition: `ok (TY-1..TY-6 + binding + R0033 + strict decoding + HC-H7B Stop integration)`.
- Validation registry: canonical 86-test and 3-test checks `ok`; terminal `validation-registry.test: ok`.
- Python compilation, shell syntax, and `git diff --check` passed before the full matrix; final hygiene is rerun after this report is added.

## Concerns and next evidence

- Independent review, installation, and a live G0164-class retry remain outside this implementation result.
- Recovery fails closed if any retained continuity receipt or H0 binding-chain record is absent or malformed.
- The existing continuity traversal remains bounded to 64 transitions.
- The compact interlock source was not changed; its gate remains GREEN. The observed deadlock was route recovery reachability after correct invalidation, not a compact-hook invalidation failure.
- This report records implementation evidence only and does not claim acceptance.
