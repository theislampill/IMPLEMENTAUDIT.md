# Independent M6 increment review

Reviewer: `/root/recover_terminal`; author reviewed: `/root/recover_remaining`.

**PASS for the five explicit portable component claims in revision 2.** One real test-discrimination finding was identified, corrected with one added line, and independently rechecked. No product change was required. No full original row or whole cell is awarded by this review.

## Exact reviewed packet

- Packet: 8,727 bytes, SHA-256 `a72615e51b04058786da80d6405c4968c3738e4e9df725504e091c5a1383628b`; all 26 member bindings verified.
- New increment: 110 added lines, 8,794-byte patch, SHA-256 `33d890371921b56d5032b9318f9cd47cf8949f3a8f028e84e833a56ba6dbc8a7`.
- Combined with the retained 87-line proposal: 197 added lines, 14,933-byte patch, SHA-256 `d8bb44293419e14b6e0eb4aad6d5fe2a54ea55f961e54ac3c2d4cbbedad8204a`.
- Product subject: V21 `338c4c36d2ac95ca24345bc92fe8c53d66eaa15d`; test-only base `89eceda6d7bb591bef17f4fce7cf0205c9fdb569`.

The previous packet remains preserved at SHA-256 `881f3234cd32fdfba57c5ba9e0ef9390ba6a5d2865a1a154b8ea1f4eddfe26e0`. This is newly gathered portable evidence, not a reconstruction of the lost earlier package or its execution history. The retained 87-line B03/L05 proposal is not re-awarded or restamped here.

## Finding and resolution

The original strict-chain test had host capacity one. I removed only B's dependency on A in memory; the test still passed because the capacity limit independently forced A then B. It therefore did not discriminate the claimed strict-chain cause of serialization.

The author added exactly one line setting capacity to two. The real chain and all existing JOIN assertions remain unchanged. I independently reran the revised positive: it passes. Removing only the dependency now fails at the intended first frontier assertion, `['A', 'B'] != ['A']`. Both the original surviving negative and the revised detected negative are retained. No product file or candidate test file was changed by this reviewer.

## Claim-level disposition

| Original row | Scope supported by this increment | Scope not established by this increment alone |
|---|---|---|
| R35-N02 | Valid nine-node census followed by refusal of duplicate nodes within one source document, across documents, and in STATE references. Retained in-memory duplicate-guard mutation is detected. | Whole exhaustive census, every missing/unknown/stale/contradictory control, or an authentic native campaign. |
| R35-N04 | Changed registry refuses an old graph; a rebuilt graph adds one node and invalidates both old issued leaf keys; an unsupported acquisition schema refuses. | Actual cached execution, native currentness, and all source/dependency/writer/resource/evidence invalidation limbs. |
| R35-N05 | A→B dependency with capacity two preserves serial cheap path; required JOIN remains consequential; NEXT is blocked until JOIN and ROOT is not falsely DONE. Missing-dependency negative now discriminates. | Every other cheap-path condition or the separate serial drift/currentness limbs. |
| R35-D05 | Optional arm is declared before the new consumer and dispatch; B remains required; optional omission retains only A/B scope; optional remains blocked and source Markdown stays unchanged. | All malformed, foreign, stale, schema, sole-writer and common-cause adverse combinations. |
| R35-D06 | Actual output subprocesses return PASS prose and exit zero while B's declared PARTIAL is preserved. Both arrival orders settle the required inputs but yield NONVERDICT and block completion. | Authentic independent actor identity, every status variant, or correlated/common-source refusal beyond existing separate evidence. |

These are meaningful maintained-consumer discriminators at the declared portable scopes. The new tests do not supply host containment, historical occurrence, an operational native receiver or programme closure.

## N04 correction is justified

The initial N04 run failed because the assertion expected the word `schema`, while the maintained compiler uses the same guard for schema and scope and raises `unsupported verifier acquisition scope`. The source confirms this. Correcting only that diagnostic regex preserves the actual refusal, old-graph rejection and fresh-graph re-execution assertions. The initial failure remains in the frozen packet rather than being discarded.

## Verification and independence

I verified both packet manifests, inspected the exact new tests and their maintained pure consumer, and executed only the new focused positive cases plus the strict-chain adversarial variants. The five bounded controls pass; revision 2's missing-dependency negative fails where required. I ran no canonical suite, changed no product code, issued no original acceptance, and authored no candidate implementation. The advisory uses independent/adversarial assessment boundaries; it does not claim a mechanically issued internal governor-route receipt.

`REVIEW_RECEIPT.json` contains the bounded machine-readable result. `INITIAL_FINDING.json`, the independent stdout/stderr captures, `FOCUSED_RESULTS.json`, `N05_REVISION_DIFF.patch` and `V2_FOCUSED_READBACK.json` preserve the entire finding and resolution. The parent can now receive this exact test-only increment and assess each remaining original row using its other retained evidence.
