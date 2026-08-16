# Historical Absorption Baseline

This is a read-only viability census over the frozen 658-row IMPLEMENTAUDIT crosswalk occurrence identified in `SOURCE_IDENTITY.json`. It preserves prior dispositions without re-adjudicating them. It is outside the repository-neutral genealogy corpus because it is target-specific integration evidence.

## Historical disposition census

| Classification | Count |
|---|---:|
| `HISTORICALLY_ABSORBED_COMPLETE` | 221 |
| `HISTORICALLY_ABSORBED_PARTIAL` | 41 |
| `HISTORICALLY_EXISTING_OWNER_NEEDS_AMENDMENT` | 114 |
| `HISTORICALLY_LINEAGE_NATIVE_RESIDUAL` | 59 |
| `HISTORICALLY_IMPLEMENTATION_OR_REACHABILITY_GAP` | 2 |
| `HISTORICALLY_BEHAVIOURAL_PROOF_GAP` | 8 |
| `HISTORICALLY_ASSUMPTION_BOUND` | 40 |
| `HISTORICALLY_DOMAIN_BOUND` | 77 |
| `HISTORICALLY_REJECTED_OR_SUPERSEDED` | 79 |
| `HISTORICALLY_UNRESOLVED` | 17 |
| **Total** | **658** |

The JSON ledger records the exact source-disposition mapping used for this exhaustive normalisation and a source-row digest/locator for every property.

## Explicit historical constraint indicators

| Indicator | Properties |
|---|---:|
| `MONOLITHIC_CONTEXT_COST` | 0 |
| `ABSENT_PROGRESSIVE_DISCLOSURE_ROUTE` | 0 |
| `ABSENT_STATE_REPRESENTATION` | 0 |
| `ABSENT_DETERMINISTIC_DISCRIMINATOR` | 15 |
| `ABSENT_AUTHORITY_OR_CURRENTNESS_MECHANISM` | 0 |
| `ABSENT_COMPOSABLE_COGNITIVE_OWNER` | 0 |
| `EXCESSIVE_CEREMONY_OR_COST` | 28 |

These are conservative evidence tags over explicit historical implementation, reachability, amendment, residual, delta or source-status fields. A zero means the selected frozen fields do not explicitly establish that causal constraint; it is not evidence that the constraint had no value or could never have mattered. The 15 deterministic-discriminator rows consist of explicit missing-native-predicate, deterministic-fixture-gap or source-static-proof-gap evidence. The 28 ceremony/cost rows carry an explicit `CEREMONY_NOT_GENERAL_PROPERTY` or `FROZEN_CEREMONY` source status.

Generic path reachability was not relabelled as absent progressive disclosure, and unrelated uses of “monolithic” in systems/modelling evidence were not relabelled as model-context cost.

## Deferral boundary

Every row states:

```text
V0400_CHANGE_DISPOSITION=DEFER_TO_V0410_BASELINE
```

Whether the exact released v0.4.0.0 architecture changes any historical disposition, removes any constraint, creates a new transfer path, or alters owner/reachability/activation/proof status requires the later v0.4.1 baseline and reabsorption audit. No such decision is made here.
