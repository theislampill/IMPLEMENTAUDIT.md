# DG17 native Stop advisory: selected-source and component findings

## Root disposition

RECEIVE_COMPONENT_FINDINGS_ONLY. The architecture remains unchanged. No native Stop or session episode was executed or accepted by this investigation. No product source was corrected.

The selected integration source is commit `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`. The binding amendment was freshly received from Issue #211, comment 5343276081:
https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/211#issuecomment-5343276081

The retained source pins and original comment bodies are part of this packet. An initial orientation used the distinct G132 source; an exact Git comparison exposed the difference. Every finding below uses the subsequently extracted immutable integration source. The earlier G132 source is not substituted for DG17 applicability.

## 1. Disposition transitions

The selected `host-stop-interlock.py::selected_disposition` returns NONTERMINAL_YIELD for a v1 policy and refuses a disposition field in that policy. A v2 policy selects one exact disposition; closure and handoff require an in-run record path and SHA-256, whereas yield cannot consume a terminal record.

Six actual ordinary selector controls completed in command 41693e/0. Three v2 controls selected their corresponding yield, closure and handoff branches. Three v1 controls continued to select yield for progress, handoff and closure response categories. These are selection controls, not valid lifecycle episodes: the closure/handoff record contents are explicitly ordinary fixture data, and the selector does not itself consume response claims.

The immutable lifecycle validator refuses requested yield when actual handoff or terminal claims are present, with the source predicate “requested yield cannot downgrade actual claims.” That fence protects the lifecycle owner and must remain intact.

This confirms the component premise behind the advisory. It does not establish whether an initially yield-only policy can legitimately remain selected when an admitted native session reaches a valid audited handoff or closure. The admitted policy producer, trusted installation/currentness, event delivery and legitimate policy-transition path still require authentic qualification.

Before complete original Stop acceptance, the campaign must independently discriminate valid nonterminal yield, valid audited handoff and valid terminal closure, including a valid handoff reached after initial yield-only selection. Separate matching-policy episodes may earn only their exact scopes. They do not dispose of a reachable unsupported transition. Any repair must consume the authoritative lifecycle predicate and exact current record pins; it must not weaken the claimed-disposition validator or give the hook lifecycle authority.

## 2. Failed activation versus stale or lost binding

The selected adapter reads its exact policy and performs read-only binding lookup. A lookup result other than a valid exact BOUND object causes “selected Stop has no active exact binding.”

Two actual isolated script processes ran with controlled schema-valid event data and fresh empty stores. Both exited 0 and produced the native-wire response:
`{"decision":"block","reason":"selected Stop has no active exact binding"}`.
The `stop_hook_active` values differed (false and true); neither escaped refusal. Both stores remained empty.

These controls did not create an authentic governed activation attempt, establish host trust in the supplied policy, authenticate a native event, or reach the Windows native enforcement path. They therefore establish the component refusal, not admitted failed-activation reachability or a complete amendment violation.

The binding owner creates an activation-attempt marker before completing the binding pair. Its retained marker identifies owner, host and session; by itself it does not distinguish an activation that never finished from a binding pair later lost. Partial pairs, stale/foreign/ambiguous state and missing-after-bound must continue to refuse. An absent pair must not become a general allow path.

The amendment requires truthful HOST_NATIVE_STOP_ENFORCEMENT=UNAVAILABLE reporting and normative fallback when governed activation never successfully established a binding. The selected native wire deliberately allows only decision, reason and systemMessage, so extra status fields cannot simply be added to that wire. Original qualification must verify a supported reporting/fallback path with authentic activation provenance and separately verify every mandatory stale/lost-binding refusal.

## Scope and evidence

- Source extraction: 1ecb65/0, exact source bodies and SOURCE_PINS.json retained.
- Fresh amendment receiving: f7cb94/0; exact comment body 19,189 bytes, SHA-256 7f39828c5f76683d74531bd49c2ec9a6a2c84bc4d59e52ba8d7a07c251c8c38e.
- Ordinary component probes: 41693e/0; exact script, inputs, raw outputs and RESULT.json retained.
- Root receiving after continuity recovery: 77ebe2/0 and ec9629/0.
- Native Stop events: 0. Original awards: none. Product source changes: none.
- Full valid lifecycle consumer controls and authentic native transition episodes have not been performed by this packet.
- No retry-count or stop_hook_active bypass, relaxed session validation, assumed authentication, recreated historical episode or architecture redesign was introduced.

## Other advisory boundaries

The R0033 ordinary-session compaction interference concern remains prospective. No actual native interference was demonstrated and no source correction is justified by this record alone. Genuine and ambiguous governed recovery remain protected.

M09 remains the newly accepted original DG17 family published in results37. M12, N01 and all prior accepted scopes remain preserved. The original 36 cases, 14 mutation families and 17 terminal clauses are unchanged. Whole DG acceptance remains 0/3.
