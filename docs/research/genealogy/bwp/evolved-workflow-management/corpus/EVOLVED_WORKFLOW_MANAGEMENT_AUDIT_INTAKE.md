# Evolved Workflow Management — complete neutral audit intake

Revision `EWM-R1-2026-09-06`; research cut-off 6 September 2026. This intake prepares a **later, separate audit of an unspecified real system**. It does not diagnose a present repository, authorise mutation, imply adoption or require one owner/control/tool per property.

## Corpus and accounting

The frozen corpus contains **77 / 77 examined candidates**, 65 `EXAMINED` and 12 `EXAMINED_WITH_EVIDENCE_LIMIT`, across all ten mandatory families. There are 51 source/edition records, including seven metadata/abstract-limited records; 26 criticisms, ten internal tensions, ten domain models, 63 relations, eight alternative configurations and 13 analytical probes. EWM-074 remains unresolved. No sibling corpus was consulted and no cross-trifecta synthesis was performed.

The exact complete IDs and disposition counts below must remain attached to any later crosswalk. A later reviewer may find a property already addressed, inapplicable, sufficiently addressed by a simpler mechanism, unsupported by available target evidence, or genuinely relevant to a gap. The source corpus does not choose among those findings in advance.

| Disposition | Count | IDs |
|---|---:|---|
| STRONGLY_RETAINED | 14 | `EWM-001`, `EWM-002`, `EWM-004`, `EWM-006`, `EWM-018`, `EWM-022`, `EWM-026`, `EWM-030`, `EWM-034`, `EWM-035`, `EWM-036`, `EWM-043`, `EWM-048`, `EWM-058` |
| RETAINED_IN_EVOLVED_FORM | 19 | `EWM-003`, `EWM-005`, `EWM-007`, `EWM-013`, `EWM-014`, `EWM-019`, `EWM-020`, `EWM-021`, `EWM-025`, `EWM-031`, `EWM-032`, `EWM-037`, `EWM-039`, `EWM-042`, `EWM-044`, `EWM-046`, `EWM-055`, `EWM-075`, `EWM-076` |
| CONTEXT_DEPENDENT | 21 | `EWM-008`, `EWM-009`, `EWM-010`, `EWM-011`, `EWM-012`, `EWM-017`, `EWM-023`, `EWM-027`, `EWM-028`, `EWM-033`, `EWM-038`, `EWM-041`, `EWM-049`, `EWM-050`, `EWM-051`, `EWM-052`, `EWM-053`, `EWM-054`, `EWM-061`, `EWM-063`, `EWM-077` |
| ASSUMPTION_SENSITIVE | 9 | `EWM-015`, `EWM-016`, `EWM-024`, `EWM-029`, `EWM-040`, `EWM-047`, `EWM-056`, `EWM-062`, `EWM-073` |
| USEFUL_BUT_EASILY_GAMED | 1 | `EWM-057` |
| USEFUL_BUT_EASILY_BUREAUCRATISED | 0 | None; no candidate with this disposition was identified. |
| DOMAIN_SPECIFIC | 3 | `EWM-045`, `EWM-059`, `EWM-060` |
| SUPERSEDED_BY_STRONGER_FORM | 1 | `EWM-067` |
| DUPLICATE_CANDIDATE | 0 | None; no candidate with this disposition was identified. |
| CEREMONY_NOT_GENERAL_PROPERTY | 1 | `EWM-066` |
| NO_GENERAL_PROPERTY | 3 | `EWM-068`, `EWM-069`, `EWM-071` |
| REJECTED_OR_DISFAVOURED | 4 | `EWM-064`, `EWM-065`, `EWM-070`, `EWM-072` |
| CONTESTED | 0 | None; no candidate with this disposition was identified. |
| UNRESOLVED | 1 | `EWM-074` |

## Evidence rules for the later reviewer

Provenance, formal validity, standards/implementation behaviour, comparative evidence, field evidence, independent replication, contrary findings and transferability are separate partitions in each JSON record. Do not average them into a confidence percentage. A strong theory/weak deployment case can be valuable for a narrow invariant; a field observation can be informative without proving a general effect.

Strong formal but model-bounded examples include EWM-015–017, EWM-029, EWM-040, EWM-048 and EWM-051. A target must establish the exact model, implementation correspondence and environment assumptions rather than attaching a model-checker verdict to an unmodelled real-world claim. EWM-018 has historical implementation-test support, not a current product guarantee. EWM-031 has qualitative field support in a particular workplace programme, not a universal causal estimate. EWM-063 uses an attrition-bearing longitudinal programme whose comparison and denominators are preserved. EWM-061/062/073/074 are especially transfer-sensitive because recent static and controlled-prototype preprint evidence does not establish general runtime safety or benefit.

The target should supply its definition/version and instance semantics, selected correctness predicate, case/message/external-object bindings, resource and authority arrangements, exception/effect boundary, persistence/retry/recovery contract, live migration/version policy, event meaning and result evidence. These are requests for evidence, not demands for particular products or new artefacts. Existing procedures, demonstrations, tests, participant accounts or records may already suffice.

## Reference resolution and domain profiles

Every candidate’s ten-field domain profile is complete in the property ledger. A `MODEL_ID`/`FIELD` reference resolves in `COMPOSITION_MODEL.domain_models[].DOMAIN_PROFILE`, and `PROPERTY_APPLICATION` supplies its particular trigger, mechanism, authority or postcondition. The profiles explicitly cover identity; enabling; data/correlation; resources/authority; correctness model; exceptions/cancellation; external effects/compensation; persistence/recovery; version/migration; and observability. The models explain cheap/manual or irrelevant cases instead of requiring a mechanism for every field.

A criterion is not automatically an operating mechanism. For example, soundness needs a matching representation and checking method; a completion criterion needs an adequate observation and consumer; a work-item protocol needs actual eligible participants. The composition relations specify those couplings and alternatives. A crosswalk must preserve them without installing one separate control per row.

## Complete crosswalk-worthy entries

### EWM-001 — Identity separation: definition, instance, work item and external object

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-001`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Bind each transition to its definition version, case, work item and, where relevant, message attempt and external business object; do not substitute one identifier for all of them. Strongly retain distinction of lifecycles, not a compulsory UUID for every noun. Controlled failure: A valid transition applied to the wrong case, attempt or external transaction.

**Trigger / non-trigger / cheap path.** Concurrent cases, retries, reused business keys, subtasks or definition changes can otherwise be confused. Alternative: A single stable task may use a named record rather than an identifier service; omit separate identifiers when their lifecycles genuinely coincide.

**Prerequisites and domain.** Explicit equality, uniqueness and reuse scopes; a way to resolve an observed event to the intended object. Contextual couplings: No separate candidate dependency is required; the stated preconditions still apply. Domain profile: `EWM-DM01` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Concurrent cases, retries, reused business keys, subtasks or definition changes can otherwise be confused. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A sample event and an in-flight action can be traced to the intended instance and definition without ambiguous aliasing.

**Consumer, authority and communication.** Engine transition evaluator, worklist user and external-application adapter. Identity locates an object; it grants no person or service permission to act on it. Exchange the case/work-item/version references needed by the recipient, without exposing unrelated personal data.

**Evidence needed.** Supply evidence that would establish or falsify: A sample event and an in-flight action can be traced to the intended instance and definition without ambiguous aliasing. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S001; EWM-S002; EWM-S018; EWM-S026]; critical support: [EWM-S045].

**Criticism, conflicts and anti-ceremony boundary.** Over-fragmented identity increases correlation and migration cost; a durable wrong binding persists the mistake. Judgement: Strongly retain distinction of lifecycles, not a compulsory UUID for every noun. Criticisms: Candidate-specific analytical objection above; no independent criticism entry is implied. Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A single stable task may use a named record rather than an identifier service; omit separate identifiers when their lifecycles genuinely coincide.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which aliases may be reused, and how long must references remain resolvable? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-002 — Explicit executable enabling and transition semantics

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-002`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Define the state and event predicates that enable work and the transitions that consume or produce state; distinguish intended notation from the engine implementation. The invariant is explicit meaning when meaning matters, not compulsory automation. Controlled failure: A diagram appears intelligible while implementations enable different actions.

**Trigger / non-trigger / cheap path.** More than one next action is possible or correctness depends on order, conditionality or concurrency. Alternative: For stable one-person work, a short conditional procedure with known next/completion conditions may suffice.

**Prerequisites and domain.** A declared semantic model and knowledge of the implementation subset actually used. Contextual couplings: `EWM-001` Domain profile: `EWM-DM01` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: More than one next action is possible or correctness depends on order, conditionality or concurrency. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The same tested state/event yields the specified enabled set and transition effect for the declared version.

**Consumer, authority and communication.** Modeller, implementer and person deciding whether a next step is admissible. Model-enabled does not mean authorised, feasible or beneficial. Publish the relevant preconditions and resulting state changes to actors who enact or review the transition.

**Evidence needed.** Supply evidence that would establish or falsify: The same tested state/event yields the specified enabled set and transition effect for the declared version. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S002; EWM-S004; EWM-S017; EWM-S027]; critical support: [EWM-S033].

**Criticism, conflicts and anti-ceremony boundary.** Formalisation can encode the wrong purpose precisely and impose unnecessary modelling work. Judgement: The invariant is explicit meaning when meaning matters, not compulsory automation. Criticisms: Candidate-specific analytical objection above; no independent criticism entry is implied. Tensions: `EWM-T001` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. For stable one-person work, a short conditional procedure with known next/completion conditions may suffice.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How much semantic detail can be omitted without changing a consequential decision? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-003 — Completion conditions and residual-work accounting

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-003`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Declare what instance completion establishes, what work may remain and whether residual effects are closed, transferred or explicitly accepted; do not equate terminal status with success. Retain scoped completion accounting, not a universal rule that every child must succeed. Controlled failure: Premature closure, abandoned work, or a successful-looking case whose required effect did not occur.

**Trigger / non-trigger / cheap path.** Parallel work, exceptions, optional/discretionary items or external actions make completion ambiguous. Alternative: A directly inspected result and an agreed completion criterion may replace a formal end-state model.

**Prerequisites and domain.** Declared acceptance predicate, active-work inventory and semantics for terminal-but-unsuccessful states. Contextual couplings: `EWM-001`, `EWM-002` Domain profile: `EWM-DM01` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Parallel work, exceptions, optional/discretionary items or external actions make completion ambiguous. Correctness/observation claim: The candidate’s bounded acceptance evidence is: No unaccounted active work remains under the chosen scope; the result claim states what was and was not established.

**Consumer, authority and communication.** Case owner, requester/recipient and engine completion evaluator. A permitted engine completion is not authority to dismiss somebody else’s unresolved obligation. Communicate the completion claim and its exclusions, including any approved transfer of remaining work.

**Evidence needed.** Supply evidence that would establish or falsify: No unaccounted active work remains under the chosen scope; the result claim states what was and was not established. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S004; EWM-S017; EWM-S019; EWM-S051]; critical support: [EWM-S016; EWM-S041].

**Criticism, conflicts and anti-ceremony boundary.** Overly strong completion rules can keep legitimate cases open indefinitely; CMMN completion deliberately permits specified non-success terminal states. Judgement: Retain scoped completion accounting, not a universal rule that every child must succeed. Criticisms: `EWM-C009`, `EWM-C011`, `EWM-C017` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A directly inspected result and an agreed completion criterion may replace a formal end-state model.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Who may accept residual uncertainty without mislabelling the delivered result? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-004 — Proportional choice of enactment infrastructure

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-004`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `CONDITIONAL_SELECTION_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Select the least costly representation and enactment mechanism adequate to the actual coordination risk and its consumer; revisit it when risk or demand changes. Strong as a selection principle; no empirical claim that the smallest tool always has the best outcome. Controlled failure: Automating ceremony, encoding unstable work prematurely, or losing useful coordination by oversimplifying.

**Trigger / non-trigger / cheap path.** Choosing whether to introduce, expand or retire workflow machinery. Alternative: No engine, a shared record, direct agreement or a short procedure can be adequate where concurrency, duration and recovery risk are small.

**Prerequisites and domain.** An explicit coordination problem and comparison with a credible simpler alternative, including the cost of informal work. Contextual couplings: No separate candidate dependency is required; the stated preconditions still apply. Domain profile: `EWM-DM01` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Choosing whether to introduce, expand or retire workflow machinery. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The selected mechanism has an identified consumer and a stated omission/retirement condition.

**Consumer, authority and communication.** Participants and the person accountable for the operational outcome and operating cost. Technical elegance or a licence purchase does not authorise redesign of other people’s responsibilities. Explain which failure the mechanism controls, to whom, and why a cheaper alternative is insufficient.

**Evidence needed.** Supply evidence that would establish or falsify: The selected mechanism has an identified consumer and a stated omission/retirement condition. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S002; EWM-S009; EWM-S025]; critical support: [EWM-S023; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Least machinery can be false economy when it shifts hidden reconciliation work to staff. Judgement: Strong as a selection principle; no empirical claim that the smallest tool always has the best outcome. Criticisms: `EWM-C001`, `EWM-C002`, `EWM-C025`, `EWM-C026` Tensions: `EWM-T009` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. No engine, a shared record, direct agreement or a short procedure can be adequate where concurrency, duration and recovery risk are small.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What counterfactual cost and failure data would overturn the chosen level of infrastructure? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-005 — Joint control, data, resource and action interpretation

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-005`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Interpret an enabled task jointly with its information inputs, eligible/available actor, interaction obligations and external effect boundary. Retain integrated interpretation but allow selective modelling of irrelevant perspectives. Controlled failure: A sound route requires missing data, an unavailable person or an action the performer cannot lawfully/operatively undertake.

**Trigger / non-trigger / cheap path.** A model is being used to justify real coordination rather than only illustrate a route. Alternative: Keep perspectives in one concise task contract when separate models would duplicate information.

**Prerequisites and domain.** Mappings among the perspectives, not merely four disconnected diagrams. Contextual couplings: `EWM-001`, `EWM-002` Domain profile: `EWM-DM01` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A model is being used to justify real coordination rather than only illustrate a route. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A consequential task’s required input, state, resource and effect assumptions can be examined together.

**Consumer, authority and communication.** Modeller and operational coordinator considering whether a proposed execution can actually proceed. Eligibility, capability and authority are separate checks; the workflow cannot invent any of them. Provide the work item with the data, responsible party and unresolved dependencies needed to act.

**Evidence needed.** Supply evidence that would establish or falsify: A consequential task’s required input, state, resource and effect assumptions can be examined together. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S014; EWM-S015; EWM-S016]; critical support: [EWM-S007; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Cross-perspective state spaces and maintenance costs grow; modelling everything can be counterproductive. Judgement: Retain integrated interpretation but allow selective modelling of irrelevant perspectives. Criticisms: `EWM-C007` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Keep perspectives in one concise task contract when separate models would duplicate information.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which omitted perspective can change an actual decision in the present setting? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-006 — Decision guards with defined ambiguity and absence behaviour

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-006`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Specify whether guards are mutually exclusive, priority-ordered or multi-selecting, and what unknown, missing, stale or conflicting values do. The strongly retained property is declared branch meaning, not universal exclusive choice. Controlled failure: No branch is selected, several incompatible branches are selected, or absent data is silently treated as false.

**Trigger / non-trigger / cheap path.** Conditional routing, including human-entered or external data. Alternative: A human resolves an infrequent ambiguous choice explicitly rather than maintaining a general rules engine.

**Prerequisites and domain.** Guard evaluation time, data bindings and declared default/error behaviour. Contextual couplings: `EWM-002`, `EWM-021` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Conditional routing, including human-entered or external data. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Tests cover true, false, multiple-match and missing-input cases with defined outcomes.

**Consumer, authority and communication.** Routing evaluator and the actor responsible for resolving ambiguous cases. An expression result permits only the modelled route, not a new permission to take the external action. Expose unresolved conditions rather than hiding them behind an arbitrary default.

**Evidence needed.** Supply evidence that would establish or falsify: Tests cover true, false, multiple-match and missing-input cases with defined outcomes. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S014; EWM-S017]; critical support: [EWM-S051].

**Criticism, conflicts and anti-ceremony boundary.** Excessive guard rules can be harder to understand than direct judgement; defaults can conceal defective inputs. Judgement: The strongly retained property is declared branch meaning, not universal exclusive choice. Criticisms: `EWM-C007` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A human resolves an infrequent ambiguous choice explicitly rather than maintaining a general rules engine.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When should ambiguity suspend routing rather than invoke a documented discretionary decision? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-007 — Activation-aware synchronisation and merge semantics

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-007`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Choose join semantics for the actual activation and re-entry model, specifying which branch arrivals are required, which remain possible and when the join resets. Retain precise context-specific synchronisation; do not claim the taxonomy settles every formalisation dispute. Controlled failure: Waiting for a branch never activated, firing early, joining different iterations or firing more than once.

**Trigger / non-trigger / cheap path.** Parallel or inclusive branching followed by convergence. Alternative: A structured split/join pair or explicit list of launched tasks avoids a general non-local join when the work permits it.

**Prerequisites and domain.** Activation identity, branch membership and assumptions about loops, multiplicity and cancellation. Contextual couplings: `EWM-001`, `EWM-002`, `EWM-006` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Parallel or inclusive branching followed by convergence. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Adversarial traces with absent, late, duplicate and re-entered branches yield the specified convergence behaviour.

**Consumer, authority and communication.** Engine designer, workflow modeller and operator diagnosing a stuck join. Join firing establishes a coordination condition, not success of each outside action. Communicate branch activation/completion/cancellation information at the level required by the selected join.

**Evidence needed.** Supply evidence that would establish or falsify: Adversarial traces with absent, late, duplicate and re-entered branches yield the specified convergence behaviour. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S013; EWM-S017; EWM-S051]; critical support: [EWM-S024; EWM-S032].

**Criticism, conflicts and anti-ceremony boundary.** General joins require non-local reasoning and can create circular dependencies; pattern faithfulness remains disputed in part of the literature. Judgement: Retain precise context-specific synchronisation; do not claim the taxonomy settles every formalisation dispute. Criticisms: `EWM-C003`, `EWM-C004` Tensions: `EWM-T002` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A structured split/join pair or explicit list of launched tasks avoids a general non-local join when the work permits it.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Can the required join be made local without changing observable coordination behaviour? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-008 — Multiple-instance creation and completion accounting

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-008`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Track distinct child instances, permitted dynamic creation, completion threshold and the disposition of remaining children after the threshold is reached. Useful only when multiplicity exists; no reason to manufacture child workflows for a single task. Controlled failure: Lost children, indefinitely open membership, duplicate counting or unintended continuation after a quorum.

**Trigger / non-trigger / cheap path.** Fan-out work or repeated concurrent performance by a varying population. Alternative: An ordinary bounded loop or fixed explicit set of tasks is cheaper when dynamic multiplicity is unnecessary.

**Prerequisites and domain.** Child identity, creation boundary and threshold/cancellation rule. Contextual couplings: `EWM-001`, `EWM-003`, `EWM-007` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Fan-out work or repeated concurrent performance by a varying population. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The parent advances exactly under its declared threshold, with every remaining child accounted for.

**Consumer, authority and communication.** Parent-instance coordinator and child-work performers. Reaching a threshold does not authorise cancelling independently owned work or erasing its effects. Report child creation and completion with their parent activation and relevant status.

**Evidence needed.** Supply evidence that would establish or falsify: The parent advances exactly under its declared threshold, with every remaining child accounted for. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S017; EWM-S051]; critical support: [EWM-S016].

**Criticism, conflicts and anti-ceremony boundary.** Dynamic membership complicates verification, observability and safe cancellation. Judgement: Useful only when multiplicity exists; no reason to manufacture child workflows for a single task. Criticisms: `EWM-C004` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An ordinary bounded loop or fixed explicit set of tasks is cheaper when dynamic multiplicity is unnecessary.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Can child membership be closed before joining, and what happens to late arrivals? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-009 — Deferred choice and event-race arbitration

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-009`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Define which events compete, how a winner is committed and how late losing events are ignored, rejected or routed to another valid state. Conditional coordination mechanism, not a universal requirement for event-driven infrastructure. Controlled failure: Both competing branches act, or a late message reopens a decision already made.

**Trigger / non-trigger / cheap path.** Competing response, timeout, human choice or external signal. Alternative: An explicit actor decision suffices when races are infrequent and responses can be safely held.

**Prerequisites and domain.** Event correlation, an arbitration point and a policy for transient versus persistent signals. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-035` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Competing response, timeout, human choice or external signal. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Near-simultaneous arrivals select behaviour consistent with the declared arbitration rule.

**Consumer, authority and communication.** Event receiver and the participant awaiting the decision. Winning an internal race does not retract a request already accepted elsewhere. Communicate winner, cancellation requests and unresolved late replies to their responsible parties.

**Evidence needed.** Supply evidence that would establish or falsify: Near-simultaneous arrivals select behaviour consistent with the declared arbitration rule. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S051; EWM-S017]; critical support: [EWM-S026].

**Criticism, conflicts and anti-ceremony boundary.** Fairness and external timing remain separate; discarding a losing event may discard important information. Judgement: Conditional coordination mechanism, not a universal requirement for event-driven infrastructure. Criticisms: `EWM-C004`, `EWM-C010` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An explicit actor decision suffices when races are infrequent and responses can be safely held.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which losing responses still create obligations after arbitration? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-010 — Interleaving and mutual-exclusion requirements

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-010`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Identify the actual shared resource or invariant and exclude conflicting overlap at that scope while allowing irrelevant concurrency. Retain only for an actual interference relation; concurrency itself is not a defect. Controlled failure: Concurrent operations violate an invariant despite valid individual task sequences.

**Trigger / non-trigger / cheap path.** Actions interfere through shared data, equipment or a required non-overlap rule. Alternative: Serialise the small conflicting region or allocate independent resources rather than locking the entire process.

**Prerequisites and domain.** Conflict relation, lock/ownership lifetime and recovery behaviour if the holder stops. Contextual couplings: `EWM-005`, `EWM-026` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Actions interfere through shared data, equipment or a required non-overlap rule. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Conflicting actions cannot overlap under the declared cross-case and external scope.

**Consumer, authority and communication.** Resource owner and scheduler or engine enforcing the exclusion. A per-case critical section does not automatically exclude other cases or independent applications. Expose who owns the protected scope and how release or recovery is established.

**Evidence needed.** Supply evidence that would establish or falsify: Conflicting actions cannot overlap under the declared cross-case and external scope. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S018; EWM-S051]; critical support: [EWM-S015].

**Criticism, conflicts and anti-ceremony boundary.** Deadlock, starvation and needless serialisation can dominate the benefit. Judgement: Retain only for an actual interference relation; concurrency itself is not a defect. Criticisms: `EWM-C004` Tensions: `EWM-T007` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Serialise the small conflicting region or allocate independent resources rather than locking the entire process.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Does the intended exclusion include actors outside the engine’s control? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-011 — Iteration, re-entry and recursive scope identity

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-011`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Distinguish repeated activations and recursive parent-child scopes, define exit conditions and separate the existence of an exit path from inevitable termination. Retain as a legitimate coordination form, not a mandatory feature or a promise that every workflow terminates. Controlled failure: Cross-iteration joins, unbounded recursion or assuming that an available exit must eventually be chosen.

**Trigger / non-trigger / cheap path.** Rework, periodic interaction, recursive decomposition or repeated external inquiry. Alternative: A bounded explicit repetition suffices when the number of iterations is known and small.

**Prerequisites and domain.** Activation identity, data carried across iterations and a progress argument when termination is required. Contextual couplings: `EWM-001`, `EWM-007`, `EWM-016` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Rework, periodic interaction, recursive decomposition or repeated external inquiry. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Repetition and exit traces have defined state effects; a claimed termination guarantee has a stronger argument than one reachable exit.

**Consumer, authority and communication.** Modeller, engine and operator responsible for progress. Re-entry does not renew expired external authority automatically. Carry iteration/parent identity and exit or interruption reason into dependent work.

**Evidence needed.** Supply evidence that would establish or falsify: Repetition and exit traces have defined state effects; a claimed termination guarantee has a stronger argument than one reachable exit. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S051; EWM-S042]; critical support: [EWM-S007; EWM-S051].

**Criticism, conflicts and anti-ceremony boundary.** Unbounded cycles defeat simple finite expansion and can increase verification and retention costs. Judgement: Retain as a legitimate coordination form, not a mandatory feature or a promise that every workflow terminates. Criticisms: `EWM-C004`, `EWM-C024` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A bounded explicit repetition suffices when the number of iterations is known and small.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What well-founded measure, bound or fairness condition supports the required progress claim? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-012 — Structured and unstructured model selection

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-012`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `CONDITIONAL_SELECTION_CRITERION`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Select a modelling form that preserves the needed behaviours and supports an affordable verification/explanation method. No universal superiority claim is warranted for either block structure or unrestricted graphs. Controlled failure: Expressive behaviour is lost to a tidy diagram, or an unnecessarily general model becomes unanalysable.

**Trigger / non-trigger / cheap path.** Choosing a representation for complex joins, cycles or nested cancellation. Alternative: Use structured blocks where they express the task clearly; keep unstructured behaviour when forced restructuring would obscure or alter it.

**Prerequisites and domain.** A semantic equivalence criterion for any transformation, not visual neatness alone. Contextual couplings: `EWM-002`, `EWM-017` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Choosing a representation for complex joins, cycles or nested cancellation. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The selected form represents the required cases without unexamined semantic translation.

**Consumer, authority and communication.** Modeller and reviewer who must understand or verify the coordination. Notation choice creates no operational authority. Explain preserved and excluded behaviours when changing representation.

**Evidence needed.** Supply evidence that would establish or falsify: The selected form represents the required cases without unexamined semantic translation. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S006; EWM-S013; EWM-S051]; critical support: [EWM-S008; EWM-S024; EWM-S032].

**Criticism, conflicts and anti-ceremony boundary.** More expressive constructs may have non-local semantics; structured encodings may explode or conceal state. Judgement: No universal superiority claim is warranted for either block structure or unrestricted graphs. Criticisms: `EWM-C003`, `EWM-C004`, `EWM-C006`, `EWM-C016` Tensions: `EWM-T002` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Use structured blocks where they express the task clearly; keep unstructured behaviour when forced restructuring would obscure or alter it.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which concrete behaviour would be lost by the simpler formalism? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-013 — Cancellation-aware convergence of parallel work

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-013`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** When a branch is cancelled, update join obligations according to the declared scope and activation rather than pretending that cancellation produced a success token. Core coupling survives, but there is no universal rule that cancellation satisfies every join. Controlled failure: Deadlock at an AND-join or false success after bypassing unfinished required work.

**Trigger / non-trigger / cheap path.** An interrupted branch can feed a later convergence point. Alternative: Cancel the enclosing unit and restart or adjudicate it as a whole when selective continuation is unnecessary.

**Prerequisites and domain.** Join rule, cancellation scope, current branch state and a distinction between stopped control and external action. Contextual couplings: `EWM-007`, `EWM-034`, `EWM-036` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An interrupted branch can feed a later convergence point. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The cancelled-branch test neither waits for an impossible arrival nor asserts an unachieved result.

**Consumer, authority and communication.** Cancellation handler, join evaluator and responsible operator. Only the actor entitled to change the coordination obligation may dispense with a required branch. Signal whether the branch ceased, may still run, or left an unresolved outside effect.

**Evidence needed.** Supply evidence that would establish or falsify: The cancelled-branch test neither waits for an impossible arrival nor asserts an unachieved result. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S016; EWM-S017; EWM-S051]; critical support: [EWM-S008; EWM-S026].

**Criticism, conflicts and anti-ceremony boundary.** Adding cancellation introduces analysis complexity and residual-effect obligations. Judgement: Core coupling survives, but there is no universal rule that cancellation satisfies every join. Criticisms: `EWM-C004`, `EWM-C006`, `EWM-C010`, `EWM-C011` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Cancel the enclosing unit and restart or adjudicate it as a whole when selective continuation is unnecessary.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which continuation remains legitimate when a mandatory parallel result is unavailable? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-014 — Termination scopes and orphan-work disposition

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-014`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Specify the scope ended by termination and account for live children, subscriptions, pending work items and transferred external obligations. Retain explicit termination meaning, not mandatory synchronised shutdown across every organisation. Controlled failure: Orphan workers or callbacks mutate state after their parent appears closed.

**Trigger / non-trigger / cheap path.** Explicit terminate, case close, parent cancellation or disappearance of future enabled work. Alternative: For a genuinely single task, an explicit final response can replace an elaborate termination protocol.

**Prerequisites and domain.** A containment relation and a policy for independently continuing work. Contextual couplings: `EWM-001`, `EWM-003`, `EWM-034` Domain profile: `EWM-DM02` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Explicit terminate, case close, parent cancellation or disappearance of future enabled work. Correctness/observation claim: The candidate’s bounded acceptance evidence is: No active descendant or late reply is silently assigned an impossible parent lifecycle.

**Consumer, authority and communication.** Engine lifecycle manager and operators responsible for the surviving activity. An enclosing model can terminate only work within its effective control; external parties may need separate requests. Communicate termination scope and any accepted continuation/transfer.

**Evidence needed.** Supply evidence that would establish or falsify: No active descendant or late reply is silently assigned an impossible parent lifecycle. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S017; EWM-S019; EWM-S051]; critical support: [EWM-S026; EWM-S045].

**Criticism, conflicts and anti-ceremony boundary.** Global termination can destroy legitimate work; waiting for all acknowledgements can delay closure indefinitely. Judgement: Retain explicit termination meaning, not mandatory synchronised shutdown across every organisation. Criticisms: `EWM-C004`, `EWM-C010` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. For a genuinely single task, an explicit final response can replace an elaborate termination protocol.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When is transfer of responsibility sufficient to close the parent? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-015 — Model-bounded classical workflow-net soundness

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-015`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Check the exact WF-net definition: every reachable marking has some path to the final marking, final completion leaves no residual tokens, and every transition can occur in some execution. Strong formal evidence within assumptions; retain as assumption-sensitive, not universally mandatory. Controlled failure: Deadlock, leftover tokens or permanently dead tasks in the model.

**Trigger / non-trigger / cheap path.** An ordinary WF-net abstraction is being used for structural assurance. Alternative: For a trivial model, direct reachability reasoning or exhaustive small-state examination may suffice.

**Prerequisites and domain.** A single source/sink WF-net and the relevant initial marking; a faithful abstraction of the property being claimed. Contextual couplings: `EWM-002`, `EWM-018` Domain profile: `EWM-DM03` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An ordinary WF-net abstraction is being used for structural assurance. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A reproducible analysis or proof establishes precisely the selected structural guarantee.

**Consumer, authority and communication.** Formal analyst and modeller reviewing a structural claim. A soundness verdict neither authorises tasks nor supplies resources, deadlines or successful external action. Report the checked net, marking, soundness definition and excluded environmental assumptions.

**Evidence needed.** Supply evidence that would establish or falsify: A reproducible analysis or proof establishes precisely the selected structural guarantee. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S004; EWM-S007]; critical support: [EWM-S008].

**Criticism, conflicts and anti-ceremony boundary.** Model mismatch and state-space growth can make a correct theorem practically misleading. Judgement: Strong formal evidence within assumptions; retain as assumption-sensitive, not universally mandatory. Criticisms: `EWM-C005`, `EWM-C006`, `EWM-C024` Tensions: `EWM-T002` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. For a trivial model, direct reachability reasoning or exhaustive small-state examination may suffice.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Does the actual engine preserve the abstraction and are the omitted constraints decision-relevant? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-016 — Soundness variant and progress-assumption selection

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-016`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Select the initial population and quantifiers explicitly; add fairness, resource, time or ranking assumptions only when the required guarantee actually needs them. Assumption-sensitive selection survives; no single strongest definition is always appropriate. Controlled failure: A weak property is presented as a stronger liveness guarantee, or an irrelevant strong property is imposed.

**Trigger / non-trigger / cheap path.** A claim extends from one case to many, from possible completion to inevitable progress, or to richer cancellation constructs. Alternative: Use classical one-case soundness when it answers the actual question; do not demand stronger variants by prestige.

**Prerequisites and domain.** A stated progress/correctness question and a net class for which the chosen analysis applies. Contextual couplings: `EWM-015` Domain profile: `EWM-DM03` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A claim extends from one case to many, from possible completion to inevitable progress, or to richer cancellation constructs. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Counterexamples distinguish “can finish”, “all chosen runs finish” and any multi-case guarantee.

**Consumer, authority and communication.** Assurance reviewer and the consumer of a progress claim. Fairness assumptions concern execution policy/environment; a proof cannot compel a human to perform work. State the guarantee in quantifiers or equivalent precise language, not just “sound”.

**Evidence needed.** Supply evidence that would establish or falsify: Counterexamples distinguish “can finish”, “all chosen runs finish” and any multi-case guarantee. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S007; EWM-S008; EWM-S051]; critical support: [EWM-S051].

**Criticism, conflicts and anti-ceremony boundary.** Stronger variants can cost much more to decide and still leave external success unmodelled. Judgement: Assumption-sensitive selection survives; no single strongest definition is always appropriate. Criticisms: `EWM-C005`, `EWM-C006`, `EWM-C024` Tensions: `EWM-T002` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Use classical one-case soundness when it answers the actual question; do not demand stronger variants by prestige.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which observed scheduler or environment conditions justify the assumed progress policy? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-017 — Verification by state analysis, reduction and justified composition

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-017`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Choose an analysis method that preserves the target property and record abstraction, reduction and compositional assumptions; complement it with implementation tests where needed. Conditional method; verification must earn its cost and cannot replace environmental evidence. Controlled failure: A proof about a reduced or component model is incorrectly transferred to the real composition.

**Trigger / non-trigger / cheap path.** State interaction is too complex for reliable unaided inspection or consequences justify formal assurance. Alternative: A reviewed small model or direct test may dominate heavyweight verification for low-risk bounded work.

**Prerequisites and domain.** Property-preserving translation/reduction and declared component interfaces. Contextual couplings: `EWM-002`, `EWM-015`, `EWM-018` Domain profile: `EWM-DM03` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: State interaction is too complex for reliable unaided inspection or consequences justify formal assurance. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The verdict can be reproduced and its link to the enacted version explained.

**Consumer, authority and communication.** Verification specialist and engineering decision-maker using the result. Verification approves a stated model claim, not uncontrolled operational changes. Deliver the analysed artefact, property, method and limits alongside the verdict.

**Evidence needed.** Supply evidence that would establish or falsify: The verdict can be reproduced and its link to the enacted version explained. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S004; EWM-S005; EWM-S007; EWM-S013]; critical support: [EWM-S008; EWM-S033].

**Criticism, conflicts and anti-ceremony boundary.** State explosion, unsound abstraction and unsupported constructs can erode assurance. Judgement: Conditional method; verification must earn its cost and cannot replace environmental evidence. Criticisms: `EWM-C005`, `EWM-C006` Tensions: `EWM-T002` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A reviewed small model or direct test may dominate heavyweight verification for low-risk bounded work.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What property could be lost by the selected reduction or decomposition? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-018 — Model-to-engine semantic correspondence

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-018`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Check the employed constructs and combinations against actual engine/version behaviour, including regressions, extensions and replay constraints. Strongly retain the distinction and checking obligation where a model verdict is relied upon; no current engine ranking is inferred. Controlled failure: “Compliant” tooling silently implements a different join, event, data-binding or lifecycle rule.

**Trigger / non-trigger / cheap path.** A formal/specification claim is used to justify execution, interchange or upgrade. Alternative: A small conformance test set for the used subset is often enough; exhaustive language support is unnecessary.

**Prerequisites and domain.** Expected traces or semantic oracle, precise engine version and representative combinations. Contextual couplings: `EWM-002` Domain profile: `EWM-DM03` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A formal/specification claim is used to justify execution, interchange or upgrade. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Used behaviours match their declared semantics under relevant fault, race and upgrade probes.

**Consumer, authority and communication.** Engine integrator, modeller and upgrade approver. Product branding is not an authority to assert untested semantics. Expose the tested subset, deviations and version-specific exceptions to consumers of the model.

**Evidence needed.** Supply evidence that would establish or falsify: Used behaviours match their declared semantics under relevant fault, race and upgrade probes. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S017; EWM-S027; EWM-S033]; critical support: [EWM-S024; EWM-S032; EWM-S033].

**Criticism, conflicts and anti-ceremony boundary.** Finite tests do not prove arbitrary models; tests can reproduce a mistaken oracle. Judgement: Strongly retain the distinction and checking obligation where a model verdict is relied upon; no current engine ranking is inferred. Criticisms: `EWM-C003`, `EWM-C013`, `EWM-C026` Tensions: `EWM-T009` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A small conformance test set for the used subset is often enough; exhaustive language support is unnecessary.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which high-consequence behaviour remains outside the tested subset? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-019 — Resource and time feasibility beyond control-flow soundness

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-019`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Assess whether eligible resources and time assumptions can support the enabled work, and specify what happens when they cannot. Retain where progress depends on scarce resources; no claim that every workflow requires an optimiser. Controlled failure: A structurally sound process waits forever or misses a necessary deadline.

**Trigger / non-trigger / cheap path.** Human/service capacity, calendars or deadlines determine whether work can progress. Alternative: An explicit availability check or manual rescheduling may suffice for a small workload.

**Prerequisites and domain.** Demand, eligibility, capacity and time constraints at the scope of the progress claim. Contextual couplings: `EWM-005`, `EWM-015`, `EWM-028` Domain profile: `EWM-DM03` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Human/service capacity, calendars or deadlines determine whether work can progress. Correctness/observation claim: The candidate’s bounded acceptance evidence is: An unavailable-resource scenario produces a truthful wait/escalation/adaptation outcome rather than a false completion guarantee.

**Consumer, authority and communication.** Operational scheduler and owner of the promised service/result. Availability cannot be conjured by assigning a role; escalating does not grant competence or permission. Communicate waiting reason, expected availability and the decision needed to change it.

**Evidence needed.** Supply evidence that would establish or falsify: An unavailable-resource scenario produces a truthful wait/escalation/adaptation outcome rather than a false completion guarantee. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S007; EWM-S015; EWM-S040; EWM-S049]; critical support: [EWM-S025; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Scheduling complexity and stale availability data; local utilisation optimisation can harm end-to-end service. Judgement: Retain where progress depends on scarce resources; no claim that every workflow requires an optimiser. Criticisms: `EWM-C005`, `EWM-C008`, `EWM-C021` Tensions: `EWM-T007` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An explicit availability check or manual rescheduling may suffice for a small workload.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How accurate must availability and duration estimates be for the promised outcome? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-020 — Data-flow defect detection and control-data consistency

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-020`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Check that every needed input is defined, appropriately scoped and usable when its consumer is enabled, including paths introduced by exceptions or change. Retain information availability and binding checks; do not pretend this packet proves arbitrary data semantics. Controlled failure: Missing, uninitialised or incompatible data reaches an otherwise valid activity.

**Trigger / non-trigger / cheap path.** Data-dependent routing or action can proceed on a path lacking required information. Alternative: A small typed form or explicit input checklist suffices when data flow is simple.

**Prerequisites and domain.** Producer/consumer bindings, absence semantics and the relevant path/state model. Contextual couplings: `EWM-005`, `EWM-021` Domain profile: `EWM-DM04` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Data-dependent routing or action can proceed on a path lacking required information. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Tests or analysis cover each consequential input on normal, skipped and migrated paths.

**Consumer, authority and communication.** Data consumer, modeller and migration reviewer. Readability of data does not grant permission to use it for an unrelated action. Expose input provenance and missing-input status to the consumer, not only a generic task-ready flag.

**Evidence needed.** Supply evidence that would establish or falsify: Tests or analysis cover each consequential input on normal, skipped and migrated paths. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S014; EWM-S017; EWM-S021]; critical support: [EWM-S007; EWM-S046].

**Criticism, conflicts and anti-ceremony boundary.** A sound data-flow model can still carry false or stale values; recent Maude lead was inaccessible and supplies no additional proof here. Judgement: Retain information availability and binding checks; do not pretend this packet proves arbitrary data semantics. Criticisms: `EWM-C007`, `EWM-C015` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A small typed form or explicit input checklist suffices when data flow is simple.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which value-level correctness conditions are absent from the workflow type/binding model? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-021 — Data scope, bindings, ownership and access

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-021`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Define who reads/writes each relevant value, when binding occurs and whether values are copied, shared or referenced across scopes. Conditional on shared/passed data; strict global data exposure is not retained. Controlled failure: Unintended data leakage, overwritten state or a consumer reading a different value than the producer intended.

**Trigger / non-trigger / cheap path.** Multiple activities or actors share data or pass it through subprocess/service boundaries. Alternative: A single immutable task input/output document can replace general shared-variable infrastructure.

**Prerequisites and domain.** Ownership and lifetime semantics plus applicable access constraints supplied externally. Contextual couplings: `EWM-001` Domain profile: `EWM-DM04` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Multiple activities or actors share data or pass it through subprocess/service boundaries. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The value read at a task boundary has a known scope, owner and binding time.

**Consumer, authority and communication.** Data owner, task performer and integration adapter. Workflow scope is not legal or organisational authority; access policy needs its own basis. Pass only the information needed for the action, with binding and freshness context.

**Evidence needed.** Supply evidence that would establish or falsify: The value read at a task boundary has a known scope, owner and binding time. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S014; EWM-S018; EWM-S039]; critical support: [EWM-S019].

**Criticism, conflicts and anti-ceremony boundary.** Excessive sharing hides coupling; excessive copying introduces staleness and reconciliation cost. Judgement: Conditional on shared/passed data; strict global data exposure is not retained. Criticisms: `EWM-C007` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A single immutable task input/output document can replace general shared-variable infrastructure.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which references remain valid when the underlying business object changes? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-022 — Case, message and business-object correlation

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-022`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Validate correlation keys and their scopes before accepting a message or callback as a transition for a case; distinguish deduplication from correct association. Strongly retain correct association whenever asynchronous or multi-case work exists. Controlled failure: Correct local actions update the wrong case or duplicate business transaction.

**Trigger / non-trigger / cheap path.** Asynchronous replies, overlapping cases, reused business keys or interorganisational messages. Alternative: A verified human lookup is sufficient at low volume when ambiguity is explicitly resolved.

**Prerequisites and domain.** An unambiguous matching rule, treatment of unmatched/ambiguous messages and knowledge of identifier reuse. Contextual couplings: `EWM-001`, `EWM-021` Domain profile: `EWM-DM04` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Asynchronous replies, overlapping cases, reused business keys or interorganisational messages. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Late, duplicated, unmatched and ambiguous messages are associated or held according to declared rules.

**Consumer, authority and communication.** Message receiver and the owner of the affected business object. Correct routing neither authenticates the sender nor establishes its authority to request a change. Exchange the minimal contractually required correlation and sender/context evidence.

**Evidence needed.** Supply evidence that would establish or falsify: Late, duplicated, unmatched and ambiguous messages are associated or held according to declared rules. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S018; EWM-S026; EWM-S039; EWM-S045]; critical support: [EWM-S038].

**Criticism, conflicts and anti-ceremony boundary.** Overly weak keys cross cases; overly strict keys strand valid responses after version or identity changes. Judgement: Strongly retain correct association whenever asynchronous or multi-case work exists. Criticisms: `EWM-C007`, `EWM-C012` Tensions: `EWM-T003` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A verified human lookup is sufficient at low volume when ambiguity is explicitly resolved.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How is a legitimate correlation change communicated to all relevant participants? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-023 — Data-centric and interacting-object lifecycle coordination

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-023`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Use available case data or interacting business-object states to determine permissible work when a single activity route would hide essential relationships. Retain for fitting object structures; reject the claim that all workflows should be recast as one artefact model. Controlled failure: One artificial case sequence obscures many-to-many dependencies or forces irrelevant tasks.

**Trigger / non-trigger / cheap path.** Multiple related objects evolve asynchronously or work is naturally case/data-driven. Alternative: An activity-centred process with explicit data bindings is preferable when it already represents the relationships clearly.

**Prerequisites and domain.** Object identity, lifecycle constraints and rules relating interacting objects. Contextual couplings: `EWM-001`, `EWM-020`, `EWM-021` Domain profile: `EWM-DM04` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Multiple related objects evolve asynchronously or work is naturally case/data-driven. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A change in one object enables/constrains related work without losing its own identity or lifecycle obligations.

**Consumer, authority and communication.** Case worker and the coordinator of interacting business objects. Object existence does not imply authority to modify its state. Communicate relevant object/state changes to affected task and case consumers.

**Evidence needed.** Supply evidence that would establish or falsify: A change in one object enables/constrains related work without losing its own identity or lifecycle obligations. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S022; EWM-S039]; critical support: [EWM-S034; EWM-S007].

**Criticism, conflicts and anti-ceremony boundary.** Cross-object interactions may enlarge the state space; wholesale case visibility can disclose excessive information. Judgement: Retain for fitting object structures; reject the claim that all workflows should be recast as one artefact model. Criticisms: `EWM-C007` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An activity-centred process with explicit data bindings is preferable when it already represents the relationships clearly.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which cross-object relationships cannot be represented adequately by the simpler case model? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-024 — Freshness and concurrent update control for routing data

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-024`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Choose binding/snapshot, conflict-detection or synchronisation rules sufficient for decisions that depend on mutable data; record when freshness cannot be established. Assumption-sensitive because the necessary consistency level depends on the decision and external cooperation. Controlled failure: An action is valid for an obsolete input but wrong for the current object.

**Trigger / non-trigger / cheap path.** Data may change between enablement, claim and external action, or concurrent children update shared values. Alternative: Read-and-confirm immediately before a low-volume action or use immutable inputs instead of broad transactional machinery.

**Prerequisites and domain.** A relevance-specific freshness requirement and access to a version, timestamp or reliable source of current state. Contextual couplings: `EWM-006`, `EWM-021`, `EWM-044` Domain profile: `EWM-DM04` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Data may change between enablement, claim and external action, or concurrent children update shared values. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Races either preserve the declared consistency rule or become visible for retry/adjudication.

**Consumer, authority and communication.** Task performer and data consistency owner. An engine cannot declare an external database current merely because its own copy is durable. Provide the version or freshness uncertainty on which the decision relies.

**Evidence needed.** Supply evidence that would establish or falsify: Races either preserve the declared consistency rule or become visible for retry/adjudication. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S017; EWM-S018; EWM-S039]; critical support: [EWM-S030].

**Criticism, conflicts and anti-ceremony boundary.** Stronger isolation increases latency/contention and still does not prove that the source value is true. Judgement: Assumption-sensitive because the necessary consistency level depends on the decision and external cooperation. Criticisms: `EWM-C007`, `EWM-C023` Tensions: `EWM-T010` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Read-and-confirm immediately before a low-volume action or use immutable inputs instead of broad transactional machinery.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How stale can the value become before the decision’s justification fails? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-025 — Role eligibility separated from operative authority

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-025`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Separate role eligibility, current authorisation, competence and availability; obtain each needed condition from an appropriate authority rather than from a worklist label. Retain the distinction; the required proof of authority is domain-specific and outside this neutral corpus. Controlled failure: A task is assigned to someone who is named by a role but unable or not permitted to perform it.

**Trigger / non-trigger / cheap path.** Work is assigned to roles, substitutes or automated principals. Alternative: A known qualified individual with an explicit agreement may need no organisational directory integration.

**Prerequisites and domain.** Applicable role/permission rules and a trustworthy basis for current ability to act. Contextual couplings: `EWM-005` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Work is assigned to roles, substitutes or automated principals. Correctness/observation claim: The candidate’s bounded acceptance evidence is: An assigned performer can explain and evidence the relevant eligibility and authority boundary.

**Consumer, authority and communication.** Allocator and intended performer. Workflow assignment records do not create external legal, professional or organisational authority. Tell the performer what is offered, under whose delegation and with which constraints.

**Evidence needed.** Supply evidence that would establish or falsify: An assigned performer can explain and evidence the relevant eligibility and authority boundary. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S015; EWM-S019; EWM-S040]; critical support: [EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Stale directories, inappropriate substitutions and over-broad role memberships. Judgement: Retain the distinction; the required proof of authority is domain-specific and outside this neutral corpus. Criticisms: `EWM-C001`, `EWM-C008`, `EWM-C009` Tensions: `EWM-T007` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A known qualified individual with an explicit agreement may need no organisational directory integration.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When do roles or credentials expire during a long-running item? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-026 — Work-item lifecycle and accountable ownership

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-026`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Use only the lifecycle states needed to establish current responsibility, exclusivity or permissible reassignment, and transition them consistently with the work being performed. Strongly retain accountable ownership when responsibility may otherwise be ambiguous. Controlled failure: Double claiming, lost work or a withdrawn item still being acted on without acknowledgement.

**Trigger / non-trigger / cheap path.** Multiple potential performers, asynchronous human work, failure or reassignment. Alternative: One accountable performer and a clear ready/done exchange can suffice when no claiming or handover race exists.

**Prerequisites and domain.** Identity and a declared ownership/claim rule, including crash or absence handling. Contextual couplings: `EWM-001`, `EWM-025` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Multiple potential performers, asynchronous human work, failure or reassignment. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The current responsible party and permitted next lifecycle transition are knowable for each consequential open item.

**Consumer, authority and communication.** Worklist user, allocator and recovery operator. Owning a work item establishes coordination responsibility only within the assignment’s authority. Communicate claim, handover, suspension and completion in the terms required by other actors.

**Evidence needed.** Supply evidence that would establish or falsify: The current responsible party and permitted next lifecycle transition are knowable for each consequential open item. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S015; EWM-S026; EWM-S045]; critical support: [EWM-S016].

**Criticism, conflicts and anti-ceremony boundary.** An elaborate lifecycle can burden users and encourage status updates detached from actual work. Judgement: Strongly retain accountable ownership when responsibility may otherwise be ambiguous. Criticisms: `EWM-C008` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. One accountable performer and a clear ready/done exchange can suffice when no claiming or handover race exists.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How is abandoned or secretly continuing work detected after reassignment? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-027 — Delegation and substitution without silently losing constraints

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-027`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Check that reassignment preserves required duty constraints, state, information access and accountability, or explicitly define a safe restart. Context-specific mechanism; no universal obligation to support arbitrary delegation. Controlled failure: A delegate repeats an action, lacks necessary context or violates a separation-of-duty constraint.

**Trigger / non-trigger / cheap path.** Absence, workload balancing, specialist substitution or handover. Alternative: Wait for the original performer when delay is cheaper and safer than transfer.

**Prerequisites and domain.** Permitted substitute, state-handover semantics and knowledge of actions already taken. Contextual couplings: `EWM-025`, `EWM-026`, `EWM-029`, `EWM-044` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Absence, workload balancing, specialist substitution or handover. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The delegate can continue or restart under an explicit valid state and assignment.

**Consumer, authority and communication.** Current performer, allocator and delegate. Delegation may transfer coordination responsibility but cannot enlarge the delegator’s powers. Send what was done, what remains, applicable constraints and unresolved external effects.

**Evidence needed.** Supply evidence that would establish or falsify: The delegate can continue or restart under an explicit valid state and assignment. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S015; EWM-S019]; critical support: [EWM-S040].

**Criticism, conflicts and anti-ceremony boundary.** Handover overhead and conflicting accounts of in-flight activity. Judgement: Context-specific mechanism; no universal obligation to support arbitrary delegation. Criticisms: `EWM-C008` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Wait for the original performer when delay is cheaper and safer than transfer.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Can the original performer still act after the handover becomes effective? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-028 — Capacity, calendars, priorities and escalation

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-028`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Relate queue policy and escalation to actual capacity, calendars and service needs; surface starvation and overload rather than optimising only local throughput. Conditional; no particular fairness metric or scheduling algorithm is universally justified. Controlled failure: Nominally eligible work remains indefinitely unperformed or urgent work is crowded out.

**Trigger / non-trigger / cheap path.** Competing cases or time-sensitive work contend for limited people or services. Alternative: A visible queue and periodic human review suffice where load is modest and priorities stable.

**Prerequisites and domain.** Workload measures, priority meaning and a responsible decision-maker able to change allocation. Contextual couplings: `EWM-019`, `EWM-025`, `EWM-026` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Competing cases or time-sensitive work contend for limited people or services. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Long waits and overload lead to an accountable decision or an explicitly accepted service limitation.

**Consumer, authority and communication.** Scheduler, team and recipients bearing waiting costs. Escalation requests a decision; it does not authorise bypassing duty or competence requirements. Share queue condition and the reason for priority changes with affected performers.

**Evidence needed.** Supply evidence that would establish or falsify: Long waits and overload lead to an accountable decision or an explicitly accepted service limitation. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S015; EWM-S040; EWM-S049]; critical support: [EWM-S025; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Priority gaming, surveillance burden and local efficiency at the expense of fairness. Judgement: Conditional; no particular fairness metric or scheduling algorithm is universally justified. Criticisms: `EWM-C002`, `EWM-C008`, `EWM-C021` Tensions: `EWM-T007` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A visible queue and periodic human review suffice where load is modest and priorities stable.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which workloads or people systematically bear the costs of the policy? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-029 — Duty constraints and assignment satisfiability

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-029`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Check assignment satisfiability under the stated constraint language; recheck when users, roles or prior assignments change. Strong model-level basis with narrow assumptions; retain as assumption-sensitive. Controlled failure: Each task has an eligible performer individually but no globally valid combination exists.

**Trigger / non-trigger / cheap path.** Rules relate multiple task performers or sharply constrain who may act. Alternative: Direct examination of a small assignment can replace a solver.

**Prerequisites and domain.** Accurate authorisation sets, constraint semantics and the initial/past assignment state. Contextual couplings: `EWM-025`, `EWM-026` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Rules relate multiple task performers or sharply constrain who may act. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A proposed assignment satisfies the declared rules, or infeasibility is surfaced.

**Consumer, authority and communication.** Policy author, allocator and security/operations reviewer. A satisfying assignment is permission-consistent in the model, not proof of current availability or real-world authority. Explain unsatisfied constraints rather than silently weakening them to make an assignment.

**Evidence needed.** Supply evidence that would establish or falsify: A proposed assignment satisfies the declared rules, or infeasibility is surfaced. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S015; EWM-S040]; critical support: [EWM-S007].

**Criticism, conflicts and anti-ceremony boundary.** General hardness, stale policy and excessive constraints can make useful work impossible. Judgement: Strong model-level basis with narrow assumptions; retain as assumption-sensitive. Criticisms: `EWM-C005`, `EWM-C008` Tensions: `EWM-T007` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Direct examination of a small assignment can replace a solver.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What legitimate policy change, rather than unauthorised bypass, resolves an infeasible assignment? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-030 — Human task completion distinguished from achieved effect

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-030`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Define what evidence is sufficient for the claimed result and distinguish performer declaration, recipient acceptance and independently established effect. Strongly retain the distinction, not universal distrust of human reports. Controlled failure: Clicking complete produces a successful status while the intended object or recipient remains unchanged.

**Trigger / non-trigger / cheap path.** A person can mark an item complete without the intended result occurring. Alternative: For low-consequence trusted work, a declaration may be adequate evidence; do not mandate independent witnessing of everything.

**Prerequisites and domain.** A specific consequence claim and a proportionate observation/acceptance rule. Contextual couplings: `EWM-003`, `EWM-025`, `EWM-058`, `EWM-077` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A person can mark an item complete without the intended result occurring. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The completion evidence supports the exact claim being made, with unresolved uncertainty visible.

**Consumer, authority and communication.** Requester, recipient or other accountable result consumer. Acceptance is an authorised judgement within a stated scope, not a metaphysical guarantee or substitute for consent. State whether the item records a claim of performance, an acknowledgement or a verified outcome.

**Evidence needed.** Supply evidence that would establish or falsify: The completion evidence supports the exact claim being made, with unresolved uncertainty visible. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S009; EWM-S019; EWM-S041; EWM-S050]; critical support: [EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Over-verification can become surveillance, delay or ritual; formal acceptance can be coerced or uninformed. Judgement: Strongly retain the distinction, not universal distrust of human reports. Criticisms: `EWM-C001`, `EWM-C009`, `EWM-C017`, `EWM-C020` Tensions: `EWM-T008` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. For low-consequence trusted work, a declaration may be adequate evidence; do not mandate independent witnessing of everything.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What evidence would reveal that an accepted completion claim was wrong? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-031 — Participatory discretion and coordination work outside the engine

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-031`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Include participants in defining and revising workflow support, and provide a way to handle legitimate work outside the prescription without pretending it never happened. Retain participant-informed discretion; foundational original texts have access limits but later primary studies were inspected. Controlled failure: Rigid automation blocks necessary action or moves coordination into invisible workarounds.

**Trigger / non-trigger / cheap path.** Knowledge-intensive work or observed workarounds reveal an inadequate representation. Alternative: Direct coordination without an engine can be preferable for small, changing cooperative tasks.

**Prerequisites and domain.** Access to participants’ actual work, an effective feedback channel and a decision-maker able to alter support. Contextual couplings: `EWM-004`, `EWM-025`, `EWM-033` Domain profile: `EWM-DM05` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Knowledge-intensive work or observed workarounds reveal an inadequate representation. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A legitimate unanticipated situation has an explicit route for judgement and feedback rather than only noncompliance labels.

**Consumer, authority and communication.** People doing and receiving the work, not only process designers. Discretion has boundaries; recognising situated work does not authorise every deviation. Exchange reasons for exceptions, practical constraints and consequences with those affected.

**Evidence needed.** Supply evidence that would establish or falsify: A legitimate unanticipated situation has an explicit route for judgement and feedback rather than only noncompliance labels. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S009; EWM-S034; EWM-S050]; critical support: [EWM-S010; EWM-S011; EWM-S025].

**Criticism, conflicts and anti-ceremony boundary.** Informal flexibility can conceal unsafe improvisation or shift burdens to less powerful participants. Judgement: Retain participant-informed discretion; foundational original texts have access limits but later primary studies were inspected. Criticisms: `EWM-C001` Tensions: `EWM-T001` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Direct coordination without an engine can be preferable for small, changing cooperative tasks.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Whose workaround is useful adaptation and whose cost or risk does it conceal? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-032 — Anticipated exceptions with defined handlers

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-032`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Specify detected exception classes, handler scope, allowed continuation and the resulting state of both current and dependent work. Retain explicit anticipated handling where failures matter; automation is conditional. Controlled failure: An error arrow exists but leaves running work or recovery obligations undefined.

**Trigger / non-trigger / cheap path.** A foreseeable failure, deadline, escalation or interrupt can alter normal coordination. Alternative: A documented operator response suffices when automated handling adds little benefit.

**Prerequisites and domain.** Detection mechanism, exception classification and a handler whose preconditions fit the current state. Contextual couplings: `EWM-005`, `EWM-034`, `EWM-036` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A foreseeable failure, deadline, escalation or interrupt can alter normal coordination. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The handler leaves a defined state from which permitted continuation or closure is clear.

**Consumer, authority and communication.** Engine handler and operator responsible for the case. The handler can only perform actions within its supplied authority and external capabilities. Convey exception type, affected scope and what recovery has or has not established.

**Evidence needed.** Supply evidence that would establish or falsify: The handler leaves a defined state from which permitted continuation or closure is clear. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S016; EWM-S017; EWM-S018]; critical support: [EWM-S026].

**Criticism, conflicts and anti-ceremony boundary.** Misclassification, undetected failures and a growing matrix of handlers can overwhelm the model. Judgement: Retain explicit anticipated handling where failures matter; automation is conditional. Criticisms: `EWM-C010` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A documented operator response suffices when automated handling adds little benefit.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which plausible exception cannot be detected soon enough for the chosen handler? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-033 — Unanticipated deviation and repair with bounded authority

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-033`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Route unmodelled situations to an actor who can examine current state, authorise a bounded repair and record its consequences before resuming or revising the definition. Conditional and authority-sensitive; the packet supplies no universal emergency powers. Controlled failure: Operators secretly patch state, losing assumptions or repeating irreversible actions.

**Trigger / non-trigger / cheap path.** An exception is outside known handlers or a valid next step is not representable. Alternative: Stop the affected activity and make a direct case-specific decision rather than installing a general adaptation subsystem.

**Prerequisites and domain.** Current state/effects visibility and a legitimate authority for the proposed repair. Contextual couplings: `EWM-031`, `EWM-032`, `EWM-044`, `EWM-048` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An exception is outside known handlers or a valid next step is not representable. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Resumption or closure is tied to an intelligible accepted state, not merely a successful administrative edit.

**Consumer, authority and communication.** Case worker, repair decision-maker and affected external participants. The ability to edit state is not permission to change business obligations or other people’s work. Record the deviation’s reason, authorisation and resulting state sufficiently for later actors to continue safely.

**Evidence needed.** Supply evidence that would establish or falsify: Resumption or closure is tied to an intelligible accepted state, not merely a successful administrative edit. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S009; EWM-S021; EWM-S036; EWM-S037]; critical support: [EWM-S016; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Repair can normalise bypasses, accumulate exceptional rules and undermine comparability of cases. Judgement: Conditional and authority-sensitive; the packet supplies no universal emergency powers. Criticisms: `EWM-C001`, `EWM-C015`, `EWM-C018` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Stop the affected activity and make a direct case-specific decision rather than installing a general adaptation subsystem.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When does repeated repair justify changing the definition rather than accepting more exceptions? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-034 — Interrupt versus non-interrupt semantics and cancellation scope

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-034`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Specify whether the original work continues, what is cancelled or suspended, and how partial acknowledgement or inability to stop is represented. Strong distinction whenever interruption exists; no universal cancellation implementation is prescribed. Controlled failure: Duplicate continuations, silently live work or a model that assumes a request already stopped an external activity.

**Trigger / non-trigger / cheap path.** Boundary events, cancellation requests, timeout escalation or user intervention. Alternative: A direct stop/continue agreement may suffice for an immediately observable human task.

**Prerequisites and domain.** Effective cancellation scope and knowledge of whether running work cooperates with interruption. Contextual couplings: `EWM-001`, `EWM-026`, `EWM-032` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Boundary events, cancellation requests, timeout escalation or user intervention. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The post-interrupt enabled work and unresolved running actions match the declared scope.

**Consumer, authority and communication.** Handler, performer and parent-instance coordinator. A cancellation request is not control over an independent participant or an irreversible effect. Distinguish requested, acknowledged and observed interruption states where the distinction changes decisions.

**Evidence needed.** Supply evidence that would establish or falsify: The post-interrupt enabled work and unresolved running actions match the declared scope. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S016; EWM-S017; EWM-S026; EWM-S051]; critical support: [EWM-S008].

**Criticism, conflicts and anti-ceremony boundary.** Cancellation acknowledgement can be delayed or ignored; forcing stop can corrupt partial work. Judgement: Strong distinction whenever interruption exists; no universal cancellation implementation is prescribed. Criticisms: `EWM-C006`, `EWM-C010` Tensions: `EWM-T002` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A direct stop/continue agreement may suffice for an immediately observable human task.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which actions can continue after the engine has recorded cancellation? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-035 — Timeout interpreted as uncertainty rather than external failure

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-035`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Treat a timed-out action’s effect as unknown until the relevant protocol, idempotency boundary or reconciliation establishes what happened. Strongly retain epistemic distinction; no blanket rule against retries. Controlled failure: Retry or compensation repeats or reverses an action on a false assumption of failure.

**Trigger / non-trigger / cheap path.** A response is missing after an action may have been accepted or committed. Alternative: Wait or query the authoritative service rather than immediately retrying when delay is safer than duplication.

**Prerequisites and domain.** Action identity, knowledge of delivery/commit semantics and a way to decide under remaining uncertainty. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-043`, `EWM-044` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A response is missing after an action may have been accepted or committed. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The committed-before-timeout case cannot silently produce an unjustified duplicate effect.

**Consumer, authority and communication.** Recovery coordinator and owner of the external action. Timeout does not authorise a conflicting second action or unilateral reversal. Communicate “response absent/effect unknown” rather than “did not happen” when that is all the evidence supports.

**Evidence needed.** Supply evidence that would establish or falsify: The committed-before-timeout case cannot silently produce an unjustified duplicate effect. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S026; EWM-S020; EWM-S044]; critical support: [EWM-S029].

**Criticism, conflicts and anti-ceremony boundary.** Uncertainty may require human adjudication or long waits; querying can itself fail. Judgement: Strongly retain epistemic distinction; no blanket rule against retries. Criticisms: `EWM-C010` Tensions: `EWM-T004` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Wait or query the authoritative service rather than immediately retrying when delay is safer than duplication.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What evidence is available when the external participant cannot report the original outcome? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-036 — Compensation distinguished from rollback

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-036`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Describe compensation as another action with its own preconditions and result, and identify which effects it can offset rather than claim universal world restoration. Strongly retain rollback/compensation distinction; no compulsory compensator for actions with no meaningful inverse. Controlled failure: Cancellation is treated as undo, or a nominal compensator fails to remedy the actual consequence.

**Trigger / non-trigger / cheap path.** An earlier committed effect must be addressed after later failure or cancellation. Alternative: Use a real atomic transaction inside a suitable boundary, or a case-specific remedial action, when those are cheaper and more faithful.

**Prerequisites and domain.** Known prior effects, an available compensating operation and authority to invoke it. Contextual couplings: `EWM-035`, `EWM-044` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An earlier committed effect must be addressed after later failure or cancellation. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The remedy’s achieved effect is distinguished from the original transaction’s state and from complete restoration.

**Consumer, authority and communication.** Business/service owner and recovery coordinator. The original actor’s permission need not include permission to compensate; new approval may be required. Communicate original effect, proposed remedy and any residual differences.

**Evidence needed.** Supply evidence that would establish or falsify: The remedy’s achieved effect is distinguished from the original transaction’s state and from complete restoration. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S020; EWM-S016; EWM-S018]; critical support: [EWM-S026].

**Criticism, conflicts and anti-ceremony boundary.** Non-equivalence, intervening activity, compensation failure and irreversible real-world effects. Judgement: Strongly retain rollback/compensation distinction; no compulsory compensator for actions with no meaningful inverse. Criticisms: `EWM-C011` Tensions: `EWM-T004` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Use a real atomic transaction inside a suitable boundary, or a case-specific remedial action, when those are cheaper and more faithful.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which residual consequence remains even after the compensating action succeeds? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-037 — Compensation failure and irreversible residual obligations

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-037`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Track outstanding remedies and their uncertainty separately from the stopped process, with a permitted retry, alternative remedy, transfer or accepted residual outcome. Retain proportionate residual accounting; legitimate transfer can close an engine case without claiming the world was restored. Controlled failure: Original work is marked closed while failed compensation disappears from view.

**Trigger / non-trigger / cheap path.** A compensator fails, an effect is irreversible, or a repair cannot finish before case closure. Alternative: A named unresolved-obligation record and human decision can replace an automated compensation tree.

**Prerequisites and domain.** Observation of remedy status, responsible recipient and authority for any disposition. Contextual couplings: `EWM-003`, `EWM-036`, `EWM-044` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A compensator fails, an effect is irreversible, or a repair cannot finish before case closure. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Every claimed completed remedy has evidence; every other material residue has a visible accepted disposition.

**Consumer, authority and communication.** Owner of the consequence and the person accepting residual risk or transferred responsibility. An engine cannot waive external commitments by deleting failed compensation state. Deliver the unresolved consequence and evidence to the actor able to decide its next disposition.

**Evidence needed.** Supply evidence that would establish or falsify: Every claimed completed remedy has evidence; every other material residue has a visible accepted disposition. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S020; EWM-S016; EWM-S044]; critical support: [EWM-S029].

**Criticism, conflicts and anti-ceremony boundary.** Unbounded retry loops, repeated remediation damage and permanent administrative cases. Judgement: Retain proportionate residual accounting; legitimate transfer can close an engine case without claiming the world was restored. Criticisms: `EWM-C011` Tensions: `EWM-T004` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A named unresolved-obligation record and human decision can replace an automated compensation tree.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What is an adequate terminal disposition when no technical remedy exists? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-038 — Orchestration and choreography with participant boundaries

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-038`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Declare which participant controls each action and what the global interaction view omits; keep local execution and shared communication contracts distinct. Contextual architecture choice, not an ideology favouring all-central or all-distributed control. Controlled failure: A central-looking picture falsely implies power to direct all participants or knowledge of their private state.

**Trigger / non-trigger / cheap path.** Work crosses independently controlled applications or organisations. Alternative: A bilateral agreement and two simple local procedures may suffice without a global orchestration engine.

**Prerequisites and domain.** Participant boundaries and a protocol or commitment description intelligible to both sides. Contextual couplings: `EWM-022`, `EWM-025`, `EWM-039`, `EWM-077` Domain profile: `EWM-DM07` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Work crosses independently controlled applications or organisations. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Every external action is attributed to the participant that can actually perform and answer for it.

**Consumer, authority and communication.** Each participant and the designer of their shared interface. No choreography picture creates a central authority; orchestration only controls its own effective scope. Exchange commitments, requests and acknowledgements at the agreed boundary rather than exposing unnecessary internal detail.

**Evidence needed.** Supply evidence that would establish or falsify: Every external action is attributed to the participant that can actually perform and answer for it. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S018; EWM-S038; EWM-S050]; critical support: [EWM-S003].

**Criticism, conflicts and anti-ceremony boundary.** Global visibility can compromise autonomy; local secrecy complicates compatibility diagnosis. Judgement: Contextual architecture choice, not an ideology favouring all-central or all-distributed control. Criticisms: `EWM-C012` Tensions: `EWM-T003` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A bilateral agreement and two simple local procedures may suffice without a global orchestration engine.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What minimum public behaviour is needed to coordinate without revealing private internals? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-039 — Message contracts, delivery states and interaction compatibility

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-039`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Define message types, correlation, ordering, error responses and the evidence needed for received, accepted, performed or satisfied states. Retain explicit meanings for consequential boundary messages; no universal message taxonomy is imposed. Controlled failure: A sent message is taken as proof that a recipient understood or acted upon it.

**Trigger / non-trigger / cheap path.** An interaction’s success depends on more than local send completion. Alternative: Acknowledged human exchange is adequate when volume and ambiguity do not warrant protocol machinery.

**Prerequisites and domain.** Shared interpretation of messages and observable responses within the participants’ actual control. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-038`, `EWM-077` Domain profile: `EWM-DM07` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An interaction’s success depends on more than local send completion. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Lost, duplicate, reordered or rejected messages have declared consequences for the local and shared states.

**Consumer, authority and communication.** Sender, receiver and the consumer of the promised outcome. Receipt is not consent; acceptance must be made by an appropriate participant under the relevant rules. Exchange the distinctions the downstream decision consumes; avoid acknowledgements with unclear meaning.

**Evidence needed.** Supply evidence that would establish or falsify: Lost, duplicate, reordered or rejected messages have declared consequences for the local and shared states. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S018; EWM-S038; EWM-S045; EWM-S050]; critical support: [EWM-S026].

**Criticism, conflicts and anti-ceremony boundary.** Protocol complexity and premature formalisation; formal acknowledgements may still mask substantive misunderstanding. Judgement: Retain explicit meanings for consequential boundary messages; no universal message taxonomy is imposed. Criticisms: `EWM-C012` Tensions: `EWM-T003` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Acknowledged human exchange is adequate when volume and ambiguity do not warrant protocol machinery.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which state changes can only the other participant legitimately attest? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-040 — Global compatibility beyond locally correct workflows

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-040`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Analyse the shared protocol and local behaviours together under explicit message ordering, delivery and partner assumptions; check global deadlocks and incompatible expectations. Strong formal basis for the distinction; global guarantees remain assumption-sensitive. Controlled failure: Each participant is locally valid but their composition waits forever or violates the intended protocol.

**Trigger / non-trigger / cheap path.** Independent participants wait on or trigger one another. Alternative: For a small bilateral exchange, enumerate the possible message orders and failure responses rather than use a general choreography tool.

**Prerequisites and domain.** Observable local interfaces, compatible correlation and a model of the communication medium. Contextual couplings: `EWM-015`, `EWM-022`, `EWM-038`, `EWM-039` Domain profile: `EWM-DM07` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Independent participants wait on or trigger one another. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A published-model-style locally-correct/global-deadlock counterexample is excluded or explicitly tolerated by the chosen protocol.

**Consumer, authority and communication.** Interface designers and participants accepting the cross-boundary service. Compatibility does not make an unwilling or unavailable participant cooperate. Agree the public sequence/partial-order constraints and how non-response or rejection is handled.

**Evidence needed.** Supply evidence that would establish or falsify: A published-model-style locally-correct/global-deadlock counterexample is excluded or explicitly tolerated by the chosen protocol. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S038; EWM-S004]; critical support: [EWM-S007].

**Criticism, conflicts and anti-ceremony boundary.** Abstraction hides data and resources; open strategic environments violate cooperative-partner assumptions. Judgement: Strong formal basis for the distinction; global guarantees remain assumption-sensitive. Criticisms: `EWM-C005`, `EWM-C012` Tensions: `EWM-T003` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. For a small bilateral exchange, enumerate the possible message orders and failure responses rather than use a general choreography tool.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which partner and communication assumptions can actually be monitored or enforced? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-041 — Interchange and portability at a declared semantic level

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-041`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `CONDITIONAL_SELECTION_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Declare the portability layer—diagram, interchange syntax, executable subset, data bindings or runtime interaction—and test the layer actually relied upon. Conditional economic/design property; universal cross-engine portability is not retained. Controlled failure: Import succeeds syntactically while execution, ownership or external interaction changes.

**Trigger / non-trigger / cheap path.** Engine replacement, cross-tool exchange, outsourcing or avoiding lock-in. Alternative: A maintained mapping or documented manual transition may be cheaper than requiring complete round-trip portability.

**Prerequisites and domain.** Known source/target semantics, extensions, bindings and lifecycle behaviour. Contextual couplings: `EWM-018`, `EWM-021`, `EWM-039`, `EWM-047` Domain profile: `EWM-DM07` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Engine replacement, cross-tool exchange, outsourcing or avoiding lock-in. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Representative used behaviour survives the intended interchange or its loss is accepted before reliance.

**Consumer, authority and communication.** Integrator and the organisation considering replacement or interoperability. A standard name is not evidence of conformance at every layer or permission to move data. Communicate unsupported constructs, transformations and lost information explicitly.

**Evidence needed.** Supply evidence that would establish or falsify: Representative used behaviour survives the intended interchange or its loss is accepted before reliance. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S002; EWM-S003; EWM-S017; EWM-S018; EWM-S033]; critical support: [EWM-S023].

**Criticism, conflicts and anti-ceremony boundary.** Lowest-common-denominator restrictions can remove useful capabilities; proprietary extensions may be economically rational. Judgement: Conditional economic/design property; universal cross-engine portability is not retained. Criticisms: `EWM-C013` Tensions: `EWM-T009` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A maintained mapping or documented manual transition may be cheaper than requiring complete round-trip portability.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What is the real exit cost, including code, data, history and in-flight instances? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-042 — Durable instance state and crash-recovery continuity

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-042`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Persist enough committed coordination state to resume the same instance claim after failure, with a declared boundary between durable orchestration and separately executed work. Retain when continuity matters; not every simple task needs a durable execution platform. Controlled failure: An acknowledged transition is forgotten or recovery starts a conflicting duplicate instance.

**Trigger / non-trigger / cheap path.** Execution outlives a process, machine or short database transaction. Alternative: A single atomic transaction or restartable manual record suffices when the coordination has no consequential in-flight state.

**Prerequisites and domain.** Durable identity, commit ordering and a defined recovery procedure. Contextual couplings: `EWM-001`, `EWM-026`, `EWM-043`, `EWM-046` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Execution outlives a process, machine or short database transaction. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Crash tests resume or safely adjudicate the declared instance without silently discarding established state.

**Consumer, authority and communication.** Runtime operator and the actors relying on continuity of the case. Durability of an engine record does not establish the current state of an outside service. Preserve and expose the last established coordination state and any uncertain in-flight actions.

**Evidence needed.** Supply evidence that would establish or falsify: Crash tests resume or safely adjudicate the declared instance without silently discarding established state. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S002; EWM-S020; EWM-S027; EWM-S044]; critical support: [EWM-S026].

**Criticism, conflicts and anti-ceremony boundary.** Persistence overhead, storage failure and the gap between recording intent and external commit. Judgement: Retain when continuity matters; not every simple task needs a durable execution platform. Criticisms: `EWM-C010`, `EWM-C014` Tensions: `EWM-T004` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A single atomic transaction or restartable manual record suffices when the coordination has no consequential in-flight state.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which acknowledged fact would be lost at each crash point? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-043 — Retries and duplicate external-effect control

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-043`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Control repeated effects through a suitable combination of idempotency, deduplication with durable keys, atomic participation, rollback support or explicit reconciliation. Strongly retain duplicate-effect control wherever repetition is possible; no single technique is universally necessary. Controlled failure: Duplicate payment, message, file mutation or human action after recovery.

**Trigger / non-trigger / cheap path.** Lost responses, crashes, worker replacement or at-least-once delivery can repeat an action. Alternative: Disable automatic retry and adjudicate the uncommon ambiguous case when the action has no safe repeat protocol.

**Prerequisites and domain.** A precise effect boundary and a stable operation identity understood by the participant that performs the effect. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-035`, `EWM-044` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Lost responses, crashes, worker replacement or at-least-once delivery can repeat an action. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Repeated delivery or execution produces the declared business effect count, or ambiguity is surfaced rather than hidden.

**Consumer, authority and communication.** Activity implementer and the owner of the external business operation. An orchestrator cannot impose idempotency on an uncooperative external service. Carry operation keys and distinguish retry attempts from new intended business operations.

**Evidence needed.** Supply evidence that would establish or falsify: Repeated delivery or execution produces the declared business effect count, or ambiguity is surfaced rather than hidden. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S020; EWM-S026; EWM-S044]; critical support: [EWM-S029].

**Criticism, conflicts and anti-ceremony boundary.** Deduplication key errors, retention expiry and non-idempotent compensators can themselves corrupt outcomes. Judgement: Strongly retain duplicate-effect control wherever repetition is possible; no single technique is universally necessary. Criticisms: `EWM-C010`, `EWM-C014` Tensions: `EWM-T004`, `EWM-T006` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Disable automatic retry and adjudicate the uncommon ambiguous case when the action has no safe repeat protocol.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How long must deduplication evidence survive retries and manual re-execution? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-044 — Recovery reconciled with external applications

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-044`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Reconcile intent, recorded acknowledgement and authoritative external outcome before a recovery decision that would otherwise assume the world matches engine history. Retain conditional reconciliation rather than a requirement to query every pure task after every restart. Controlled failure: Recovery repeats, omits or compensates an action based on an incorrect internal record.

**Trigger / non-trigger / cheap path.** An action may have committed outside the persisted workflow transition or a human acted outside the system. Alternative: An authoritative query or human confirmation may be more appropriate than a distributed transaction.

**Prerequisites and domain.** External action identity and a trustworthy observation or an explicit decision under unavoidable uncertainty. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-035`, `EWM-058` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An action may have committed outside the persisted workflow transition or a human acted outside the system. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The next recovery step states which external facts are established and which remain uncertain.

**Consumer, authority and communication.** Recovery operator, external service owner and result consumer. The reconciler may observe without being authorised to mutate; discrepancies require the right decision-maker. Exchange evidence of actual outcome, not merely duplicate copies of the original request.

**Evidence needed.** Supply evidence that would establish or falsify: The next recovery step states which external facts are established and which remain uncertain. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S020; EWM-S026; EWM-S044]; critical support: [EWM-S029; EWM-S041].

**Criticism, conflicts and anti-ceremony boundary.** External queries may be stale, unavailable or non-authoritative; reconciliation can become a costly second workflow. Judgement: Retain conditional reconciliation rather than a requirement to query every pure task after every restart. Criticisms: `EWM-C010`, `EWM-C014` Tensions: `EWM-T004` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An authoritative query or human confirmation may be more appropriate than a distributed transaction.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What decision remains safe when neither success nor failure can be established? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-045 — Deterministic replay boundary for nondeterministic work

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-045`. **Disposition:** `DOMAIN_SPECIFIC`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Keep replay-sensitive decisions within the deterministic contract and isolate or record nondeterministic inputs and effects through the supported interfaces. Retain only for replay-based implementations and clearly delimited deterministic components. Controlled failure: Replay emits a different command sequence or repeats nondeterministic work as if it were pure control logic.

**Trigger / non-trigger / cheap path.** The selected runtime rebuilds orchestration by replay. Alternative: A state-machine snapshot engine, explicit persisted state or a short transaction may not require this particular programming discipline.

**Prerequisites and domain.** The runtime’s command-matching rules, deterministic API constraints and separation of activities from orchestration. Contextual couplings: `EWM-018`, `EWM-042`, `EWM-047` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: The selected runtime rebuilds orchestration by replay. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Replaying a supported history under compatible code preserves the required command sequence.

**Consumer, authority and communication.** Workflow-code author and runtime operator. Replay consistency is not permission to repeat an external action or proof that its returned value was correct. Expose which values were recorded and which computations are re-executed.

**Evidence needed.** Supply evidence that would establish or falsify: Replaying a supported history under compatible code preserves the required command sequence. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S027; EWM-S028; EWM-S044]; critical support: [EWM-S030].

**Criticism, conflicts and anti-ceremony boundary.** Abstraction leaks, prohibited APIs and recorded bad inputs; deterministic wrong behaviour remains wrong. Judgement: Retain only for replay-based implementations and clearly delimited deterministic components. Criticisms: `EWM-C014`, `EWM-C023` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A state-machine snapshot engine, explicit persisted state or a short transaction may not require this particular programming discipline.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which library, configuration or environment changes can alter emitted commands? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-046 — Sufficient recovery history and bounded retention

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-046`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Determine the minimum retained state, history and external references required for specified recovery, review and continuity claims; retire records only after those consumers and obligations are addressed. Retain explicit retention rationale, not any fixed duration or compulsory event sourcing. Controlled failure: Deletion prevents safe recovery or deduplication, or unlimited retention imposes avoidable cost and exposure.

**Trigger / non-trigger / cheap path.** History growth, archival cost, long duration or retention-sensitive data. Alternative: A compact snapshot plus necessary operation references may replace full event retention when its sufficiency is established.

**Prerequisites and domain.** Enumerated recovery and evidence consumers and a preservation/compaction argument. Contextual couplings: `EWM-042`, `EWM-043`, `EWM-055` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: History growth, archival cost, long duration or retention-sensitive data. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The retained material supports the declared claims and no discarded material is silently assumed to exist.

**Consumer, authority and communication.** Runtime operator, evidence consumer and applicable data custodian. This is not legal retention advice; applicable obligations must be supplied by the relevant authority. Communicate which reconstruction and verification claims survive compaction or retirement.

**Evidence needed.** Supply evidence that would establish or falsify: The retained material supports the declared claims and no discarded material is silently assumed to exist. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S027; EWM-S045; EWM-S044]; critical support: [EWM-S030].

**Criticism, conflicts and anti-ceremony boundary.** Compaction can erase useful causal detail; indefinite retention can retain misleading or sensitive data without a consumer. Judgement: Retain explicit retention rationale, not any fixed duration or compulsory event sourcing. Criticisms: `EWM-C014`, `EWM-C019`, `EWM-C025` Tensions: `EWM-T006` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A compact snapshot plus necessary operation references may replace full event retention when its sufficiency is established.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What is the longest legitimate retry, migration or dispute horizon that the retained identifiers must support? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-047 — Running code-version and replay compatibility

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-047`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Bind in-flight work to a compatible implementation/definition version and test upgrade or routing strategies against real persisted states before replacing them. Assumption-sensitive because compatibility differs across engines and external dependencies. Controlled failure: An upgrade makes history unreplayable or interprets an existing work item differently.

**Trigger / non-trigger / cheap path.** Engine, code, dependency or workflow-definition changes while instances remain active. Alternative: Pin old instances to the old version until they finish when that is safer and affordable.

**Prerequisites and domain.** Version identity, compatibility criteria and access to representative histories/current states. Contextual couplings: `EWM-001`, `EWM-018`, `EWM-045`, `EWM-048` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Engine, code, dependency or workflow-definition changes while instances remain active. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Existing cases either continue under compatible semantics or undergo an explicit approved transition.

**Consumer, authority and communication.** Deployer, runtime maintainer and owner of continuing cases. Deployment access does not authorise changing the meaning of commitments already made. Communicate version selection and exceptions to operators and dependent services.

**Evidence needed.** Supply evidence that would establish or falsify: Existing cases either continue under compatible semantics or undergo an explicit approved transition. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S027; EWM-S028; EWM-S044]; critical support: [EWM-S030; EWM-S033].

**Criticism, conflicts and anti-ceremony boundary.** Version proliferation, security fixes deferred by pinning and inaccessible old dependencies. Judgement: Assumption-sensitive because compatibility differs across engines and external dependencies. Criticisms: `EWM-C013`, `EWM-C014`, `EWM-C015`, `EWM-C023` Tensions: `EWM-T010` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Pin old instances to the old version until they finish when that is safer and affordable.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When can a security or operational change no longer safely wait for old cases to finish? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-048 — State-sensitive running-instance migration

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-048`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Check the actual marking, data, completed work, pending interactions and relevant constraints when migrating an instance; a sound new definition alone is insufficient. Strongly retain the distinction when migration is attempted; checked migration is not compulsory for every release. Controlled failure: A newly required step lies behind the current state, a required input has no producer, or pending work is orphaned.

**Trigger / non-trigger / cheap path.** An existing case is moved to a changed process rather than merely starting new cases differently. Alternative: Leave the old case on its original definition or explicitly close/restart it with consequence accounting when migration adds no value.

**Prerequisites and domain.** A supported state transformation and an argument for preserved or deliberately changed obligations. Contextual couplings: `EWM-001`, `EWM-020`, `EWM-022`, `EWM-033`, `EWM-047` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: An existing case is moved to a changed process rather than merely starting new cases differently. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The migrated case has a valid current state and a permissible future under the new definition, with past external effects preserved as facts.

**Consumer, authority and communication.** Migration approver, engine and affected case participants. Migration permission must cover changed obligations, not just permission to edit a diagram. Explain what completed actions remain valid, what new work is required and how outstanding responses will be interpreted.

**Evidence needed.** Supply evidence that would establish or falsify: The migrated case has a valid current state and a permissible future under the new definition, with past external effects preserved as facts. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S021; EWM-S035; EWM-S036]; critical support: [EWM-S016].

**Criticism, conflicts and anti-ceremony boundary.** State-space and cross-version reasoning cost; model-valid changes may still invalidate business commitments. Judgement: Strongly retain the distinction when migration is attempted; checked migration is not compulsory for every release. Criticisms: `EWM-C015`, `EWM-C026` Tensions: `EWM-T005` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Leave the old case on its original definition or explicitly close/restart it with consequence accounting when migration adds no value.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which already performed action or promised result changes meaning under the target definition? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-049 — Definition coexistence and deployment selection

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-049`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Declare deployment selection and permit coexistence where appropriate, with clear routing of new work, events and operators to the right version. Conditional alternative that can dominate migration, not a universal architecture requirement. Controlled failure: New cases use obsolete rules or old callbacks are routed to an incompatible new definition.

**Trigger / non-trigger / cheap path.** A definition changes but immediate migration of all cases is unnecessary or unsafe. Alternative: Drain a short-lived workload before replacement when coexistence would cost more than a brief pause.

**Prerequisites and domain.** Version-aware creation and event routing plus a retirement condition for old versions. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-047`, `EWM-048` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A definition changes but immediate migration of all cases is unnecessary or unsafe. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Every active instance has an explicit governing version and a valid update/retirement path.

**Consumer, authority and communication.** Deployer, case creator and integration adapter. Coexistence must not silently violate externally required rule changes; those obligations need separate judgement. Publish which population follows which definition and when each version can retire.

**Evidence needed.** Supply evidence that would establish or falsify: Every active instance has an explicit governing version and a valid update/retirement path. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S021; EWM-S028; EWM-S036]; critical support: [EWM-S030].

**Criticism, conflicts and anti-ceremony boundary.** Multiple versions duplicate maintenance and can fragment operational reporting. Judgement: Conditional alternative that can dominate migration, not a universal architecture requirement. Criticisms: `EWM-C015` Tensions: `EWM-T005` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Drain a short-lived workload before replacement when coexistence would cost more than a brief pause.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What event or deadline makes continued operation of an old definition unacceptable? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-050 — Flexibility by design, deviation, underspecification and change

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-050`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `CONDITIONAL_SELECTION_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Select the flexibility mechanism according to whether variation is anticipated, temporarily tolerated, deliberately left open or requires a changed definition/state. Retain the discriminating taxonomy as a selection aid, not a maturity ladder. Controlled failure: “Flexible” is used as a slogan while legitimate variation remains blocked or constraints disappear.

**Trigger / non-trigger / cheap path.** Observed variation cannot be handled adequately by a single fixed route. Alternative: Explicitly enumerate a few stable alternatives when that is clearer than a general adaptive mechanism.

**Prerequisites and domain.** Knowledge of why the variation occurs and which constraints remain non-negotiable. Contextual couplings: `EWM-004`, `EWM-031`, `EWM-033`, `EWM-048` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Observed variation cannot be handled adequately by a single fixed route. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The selected strategy states what is variable, who decides and what evidence justifies the choice.

**Consumer, authority and communication.** Participants, modeller and operator choosing an adaptation strategy. Freedom to choose a next step does not authorise changing the constraints that make it acceptable. Distinguish case-specific deviation from a new general definition.

**Evidence needed.** Supply evidence that would establish or falsify: The selected strategy states what is variable, who decides and what evidence justifies the choice. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S036; EWM-S009; EWM-S021; EWM-S035]; critical support: [EWM-S025].

**Criticism, conflicts and anti-ceremony boundary.** Freedom increases explanation and verification burden; enumerating all possibilities can be equally unmanageable. Judgement: Retain the discriminating taxonomy as a selection aid, not a maturity ladder. Criticisms: `EWM-C016`, `EWM-C018` Tensions: `EWM-T001`, `EWM-T005` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Explicitly enumerate a few stable alternatives when that is clearer than a general adaptive mechanism.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Is the recurring variation genuinely uncertain, or merely insufficiently understood? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-051 — Declarative constraints with consistency and progress analysis

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-051`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Express necessary temporal/data constraints, analyse their consistency and progress implications, and explain which obligations remain pending before completion. Conditional method, not a universal replacement for sequences or proof of user comprehension. Controlled failure: Individually reasonable rules conflict, disable all useful actions or permit apparent completion with pending obligations.

**Trigger / non-trigger / cheap path.** Many valid sequences share a small set of important constraints. Alternative: Use an imperative route for stable routine sections or a short set of human-understood rules when a declarative engine adds no value.

**Prerequisites and domain.** Constraint semantics, finite-trace completion interpretation and an interface usable by the relevant actors. Contextual couplings: `EWM-002`, `EWM-016`, `EWM-017`, `EWM-050` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Many valid sequences share a small set of important constraints. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The rule set admits the intended cases and rejects specified violations, including terminal response obligations.

**Consumer, authority and communication.** Constraint author, case worker and verification consumer. An allowed trace is not automatically authorised or wise; external powers remain separately supplied. Expose why an action is allowed/blocked and which obligations remain to be fulfilled.

**Evidence needed.** Supply evidence that would establish or falsify: The rule set admits the intended cases and rejects specified violations, including terminal response obligations. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S035; EWM-S036]; critical support: [EWM-S024; EWM-S032].

**Criticism, conflicts and anti-ceremony boundary.** Constraint interactions can be hard to explain; permissiveness and complexity may overwhelm users. Judgement: Conditional method, not a universal replacement for sequences or proof of user comprehension. Criticisms: `EWM-C003`, `EWM-C016` Tensions: `EWM-T001`, `EWM-T005` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Use an imperative route for stable routine sections or a short set of human-understood rules when a declarative engine adds no value.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Can participants predict the consequences of a permitted action well enough to use the flexibility? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-052 — Case handling based on available data and accountable discretion

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-052`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Expose relevant case data and permissible operations so an accountable actor can select the next justified action without inventing a full predetermined sequence. Retain for appropriate uncertainty and skill conditions; no general outcome superiority is established. Controlled failure: A rigid route blocks necessary inquiry or encourages fictitious completion of irrelevant tasks.

**Trigger / non-trigger / cheap path.** Knowledge-intensive cases whose next valid action depends on evolving context. Alternative: An informal case record and an experienced worker may be adequate at low scale; stable work can remain prescribed.

**Prerequisites and domain.** Relevant information, skilled actors, explicit constraints and a recipient for the result. Contextual couplings: `EWM-021`, `EWM-023`, `EWM-025`, `EWM-031`, `EWM-050` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Knowledge-intensive cases whose next valid action depends on evolving context. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A non-predetermined but legitimate next step can be selected with an intelligible rationale and observable result.

**Consumer, authority and communication.** Case worker and the person affected by the case outcome. Discretion is exercised within the actor’s actual authority; broad data access is not automatically justified. Explain the chosen next action and relevant case changes sufficiently for collaboration and review.

**Evidence needed.** Supply evidence that would establish or falsify: A non-predetermined but legitimate next step can be selected with an intelligible rationale and observable result. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S022; EWM-S034; EWM-S039]; critical support: [EWM-S025].

**Criticism, conflicts and anti-ceremony boundary.** Inconsistent judgements, excessive information exposure and reliance on scarce expertise. Judgement: Retain for appropriate uncertainty and skill conditions; no general outcome superiority is established. Criticisms: `EWM-C001`, `EWM-C016`, `EWM-C017` Tensions: `EWM-T001` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An informal case record and an experienced worker may be adequate at low scale; stable work can remain prescribed.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? How will another qualified worker understand or continue the case without recreating all tacit knowledge? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-053 — Discretionary case planning and explicit completion criteria

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-053`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Separate the available plan from selected work, declare who may add/activate items, and define completion without equating every terminal item state with success. Conditional case-management mechanism; no compulsory CMMN adoption. Controlled failure: Discretionary work becomes silently mandatory, or failed required work is misreported as successful because a stage closed.

**Trigger / non-trigger / cheap path.** Case workers add or activate work during a case. Alternative: A small case plan with explicit decisions can replace a full case-management notation.

**Prerequisites and domain.** Planning authority, entry/exit criteria and a meaningful interpretation of required/discretionary states. Contextual couplings: `EWM-003`, `EWM-025`, `EWM-030`, `EWM-052` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Case workers add or activate work during a case. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A closed case states its actual outcome and selected-work disposition, not merely its engine lifecycle label.

**Consumer, authority and communication.** Case planner, worker and completion consumer. Planning tables express permitted roles in a model; they do not establish external authority. Communicate what was available, chosen, declined, completed or otherwise terminated.

**Evidence needed.** Supply evidence that would establish or falsify: A closed case states its actual outcome and selected-work disposition, not merely its engine lifecycle label. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S019; EWM-S022]; critical support: [EWM-S016].

**Criticism, conflicts and anti-ceremony boundary.** Planning complexity, hidden obligations and over-reading of “required” flags. Judgement: Conditional case-management mechanism; no compulsory CMMN adoption. Criticisms: `EWM-C009`, `EWM-C017` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A small case plan with explicit decisions can replace a full case-management notation.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which failed or disabled items are legitimately compatible with the claimed case outcome? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-054 — Late-bound worklets and contextual exception reuse

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-054`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Select a bounded subworkflow for the current case context and preserve the selection rationale and exception precedence when extending the rule base. Conditional adaptive mechanism; demonstration scenarios do not prove general deployment benefit. Controlled failure: The selected variant fits a superficial condition but violates the actual case’s constraints.

**Trigger / non-trigger / cheap path.** Repeated contextual variation is better handled by reusable subworkflows than by one expanding monolithic route. Alternative: A human-selected procedure or a small explicit variant list may be easier to maintain.

**Prerequisites and domain.** Case attributes relevant to selection, compatible subworkflow interfaces and authorised rule extension. Contextual couplings: `EWM-020`, `EWM-033`, `EWM-048`, `EWM-050` Domain profile: `EWM-DM09` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Repeated contextual variation is better handled by reusable subworkflows than by one expanding monolithic route. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The selected/replaced worklet is appropriate to the current context and leaves a usable parent state.

**Consumer, authority and communication.** Case worker, rule maintainer and parent-workflow consumer. The ability to add a worklet does not authorise changing parent commitments or external privileges. Explain the rule path and communicate input/output and exception expectations to the selected worklet.

**Evidence needed.** Supply evidence that would establish or falsify: The selected/replaced worklet is appropriate to the current context and leaves a usable parent state. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S037; EWM-S036]; critical support: [EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Rule accretion, precedence opacity and reused exceptions with invalid assumptions. Judgement: Conditional adaptive mechanism; demonstration scenarios do not prove general deployment benefit. Criticisms: `EWM-C018` Tensions: `EWM-T005` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A human-selected procedure or a small explicit variant list may be easier to maintain.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When should accumulated exceptions trigger redesign rather than another local rule? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-055 — Execution histories with defined event semantics

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-055`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Define event meaning, identity, ordering and observation scope so histories can support the particular recovery, monitoring or review question. Retain histories when they have a real consumer; recording every event is not required. Controlled failure: A log entry is interpreted as a stronger action or causal fact than the recorder observed.

**Trigger / non-trigger / cheap path.** Later actors rely on an execution history rather than direct memory of the work. Alternative: A concise result/decision record may suffice when detailed event reconstruction has no consumer.

**Prerequisites and domain.** Event schema, case/attempt identity and declared clock/order assumptions. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-046`, `EWM-058` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Later actors rely on an execution history rather than direct memory of the work. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A reviewer can distinguish request, start, acknowledgement, completion and externally established effect where those distinctions matter.

**Consumer, authority and communication.** Operator, analyst and the person relying on a past-state claim. Logging access is not authority to observe every human activity or retain all personal data. Provide event definitions and known omissions along with the history.

**Evidence needed.** Supply evidence that would establish or falsify: A reviewer can distinguish request, start, acknowledgement, completion and externally established effect where those distinctions matter. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S045; EWM-S043; EWM-S027]; critical support: [EWM-S041; EWM-S049].

**Criticism, conflicts and anti-ceremony boundary.** Instrumentation burden, inconsistent clocks, missing manual work and misleadingly complete-looking logs. Judgement: Retain histories when they have a real consumer; recording every event is not required. Criticisms: `EWM-C019`, `EWM-C025` Tensions: `EWM-T006`, `EWM-T008` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A concise result/decision record may suffice when detailed event reconstruction has no consumer.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which downstream decisions depend on an event distinction the recorder does not actually observe? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-056 — Conformance observations as bounded evidence

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-056`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Check log-to-case/activity/order assumptions and the model’s intended scope before interpreting deviations or conformance as evidence about enactment. Assumption-sensitive interface with process mining; no sibling synthesis was consulted. Controlled failure: Unlogged work appears absent, recording errors appear as misconduct, or high fitness is mistaken for a good process.

**Trigger / non-trigger / cheap path.** A workflow is being monitored or assessed against an expected model. Alternative: Directly review a small set of consequential traces instead of imposing a general mining pipeline.

**Prerequisites and domain.** A meaningful model, appropriate event abstraction and known coverage/selection limits. Contextual couplings: `EWM-002`, `EWM-022`, `EWM-055`, `EWM-058` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A workflow is being monitored or assessed against an expected model. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Conformance claims state what was observed and distinguish model, logging and real-work deviations.

**Consumer, authority and communication.** Operational reviewer and participants asked to explain deviations. A detected mismatch is a question for adjudication, not automatic authority to sanction or repair. Present the observed trace, alignment assumptions and plausible recording/model explanations.

**Evidence needed.** Supply evidence that would establish or falsify: Conformance claims state what was observed and distinguish model, logging and real-work deviations. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S043; EWM-S045]; critical support: [EWM-S009; EWM-S031].

**Criticism, conflicts and anti-ceremony boundary.** Metric gaming, model overfit and loss of many-object interactions in a single-case projection. Judgement: Assumption-sensitive interface with process mining; no sibling synthesis was consulted. Criticisms: `EWM-C019`, `EWM-C022` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Directly review a small set of consequential traces instead of imposing a general mining pipeline.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What alternate event abstraction would change the interpretation of the same case? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-057 — Operational monitoring with a decision consumer

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-057`. **Disposition:** `USEFUL_BUT_EASILY_GAMED`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Connect each monitored quantity to a decision-maker and a possible action, while preserving scope, uncertainty and incentives. Useful but easily gamed; fault frequency and resource impact need not rank problems the same way. Controlled failure: Dashboards accumulate while no one can act, or people optimise status metrics instead of results.

**Trigger / non-trigger / cheap path.** Waiting, failures or resource use can be acted on before or after outcomes deteriorate. Alternative: A visible queue and periodic review can replace dashboards and continuous instrumentation.

**Prerequisites and domain.** A signal whose meaning is understood, timely access and an actor able to respond. Contextual couplings: `EWM-019`, `EWM-028`, `EWM-055`, `EWM-058` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Waiting, failures or resource use can be acted on before or after outcomes deteriorate. Correctness/observation claim: The candidate’s bounded acceptance evidence is: A material signal results in an appropriate decision, including justified non-intervention.

**Consumer, authority and communication.** Operational coordinator, affected workers and service recipients. Monitoring does not authorise intervention beyond the responsible actor’s powers. Communicate the actionable condition and competing explanations rather than only a red/green indicator.

**Evidence needed.** Supply evidence that would establish or falsify: A material signal results in an appropriate decision, including justified non-intervention. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S045; EWM-S025; EWM-S049]; critical support: [EWM-S031; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Surveillance, alert fatigue, gaming and over-prioritisation of frequent but low-cost errors. Judgement: Useful but easily gamed; fault frequency and resource impact need not rank problems the same way. Criticisms: `EWM-C002`, `EWM-C019`, `EWM-C021` Tensions: `EWM-T007`, `EWM-T008` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A visible queue and periodic review can replace dashboards and continuous instrumentation.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which important harm could worsen while the selected metric improves? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-058 — Observation completeness and event-to-world correspondence

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-058`. **Disposition:** `STRONGLY_RETAINED`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Identify the observation boundary and connect consequential claims to an appropriate external or participant source; preserve uncertainty when correspondence cannot be checked. Strongly retain the distinction; no general demand for omniscient observation. Controlled failure: A complete log is mistaken for complete reality, including manual work or downstream outcomes.

**Trigger / non-trigger / cheap path.** Completion, conformance, recovery or effectiveness is inferred from internal history. Alternative: A trustworthy participant report is sufficient when the consequence and risk justify it; independent sensing is not universal.

**Prerequisites and domain.** A specific claim, a suitable observation source and knowledge of its failure/coverage limits. Contextual couplings: `EWM-030`, `EWM-044`, `EWM-055` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Completion, conformance, recovery or effectiveness is inferred from internal history. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The claim’s evidence boundary is visible and no external success is asserted solely from an inadequate internal event.

**Consumer, authority and communication.** Result consumer, recovery decision-maker and reviewer. An observer need not have authority to act, and a model’s certainty cannot replace a participant’s legitimate judgement. State whether evidence concerns a recorded event, a communicated commitment or an observed consequence.

**Evidence needed.** Supply evidence that would establish or falsify: The claim’s evidence boundary is visible and no external success is asserted solely from an inadequate internal event. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S009; EWM-S041; EWM-S045; EWM-S050]; critical support: [EWM-S031; EWM-S049].

**Criticism, conflicts and anti-ceremony boundary.** Observation can be costly, intrusive, stale or circular when it merely repeats the same source. Judgement: Strongly retain the distinction; no general demand for omniscient observation. Criticisms: `EWM-C009`, `EWM-C019`, `EWM-C020`, `EWM-C022`, `EWM-C026` Tensions: `EWM-T008` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A trustworthy participant report is sufficient when the consequence and risk justify it; independent sensing is not universal.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When are two corroborating records actually copies of one fallible observation? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-059 — Scientific workflow provenance and reproducibility boundary

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-059`. **Disposition:** `DOMAIN_SPECIFIC`. **Kind:** `CORRECTNESS_OR_EVIDENCE_CRITERION`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Preserve the workflow, relevant input/dependency/environment identity and provenance needed for a declared rerun or result-comparison claim; choose an appropriate output oracle. Retain for scientific reuse; decay-study full texts remain access-limited, so no decay rate is exported. Controlled failure: The workflow runs successfully but cannot reproduce or justify the claimed scientific result.

**Trigger / non-trigger / cheap path.** A scientific computation is shared, rerun or interpreted as evidence. Alternative: A small script with pinned inputs and a clear method record may be adequate; a workflow suite is not compulsory.

**Prerequisites and domain.** Accessible inputs/dependencies and a scientific criterion for equivalent or acceptable outputs. Contextual couplings: `EWM-001`, `EWM-021`, `EWM-046`, `EWM-058` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A scientific computation is shared, rerun or interpreted as evidence. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The claimed reproducibility level is supported by retained artefacts and a suitable result check, not just exit status.

**Consumer, authority and communication.** Scientist, collaborator and reviewer of the result. Workflow execution is not scientific authority and metadata completeness does not validate an inference. Share provenance and conditions of reuse, including known inaccessible or changing services.

**Evidence needed.** Supply evidence that would establish or falsify: The claimed reproducibility level is supported by retained artefacts and a suitable result check, not just exit status. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S042; EWM-S041]; critical support: [EWM-S047; EWM-S048].

**Criticism, conflicts and anti-ceremony boundary.** Decaying services, evolving datasets, nondeterministic methods and the cost of preserving environments. Judgement: Retain for scientific reuse; decay-study full texts remain access-limited, so no decay rate is exported. Criticisms: `EWM-C020` Tensions: `EWM-T006` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A small script with pinned inputs and a clear method record may be adequate; a workflow suite is not compulsory.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What counts as equivalent output for the scientific question rather than byte identity? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-060 — Scientific workflow execution under data and environment constraints

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-060`. **Disposition:** `DOMAIN_SPECIFIC`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Model the data availability, placement, execution capability and failure/recovery boundary relevant to the scientific task, without equating a scheduler graph with the whole scientific process. Contextual scientific execution property; no universal cloud or engine choice follows. Controlled failure: Valid computational tasks cannot obtain inputs/resources or repeated movement/execution wastes substantial effort.

**Trigger / non-trigger / cheap path.** Distributed data movement or heterogeneous resources dominate execution feasibility and cost. Alternative: Local execution or a simple scheduler may dominate when data and resources are already co-located.

**Prerequisites and domain.** Resource and input identities, site capabilities, movement costs and a scoped recovery policy. Contextual couplings: `EWM-019`, `EWM-024`, `EWM-042`, `EWM-043`, `EWM-059` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Distributed data movement or heterogeneous resources dominate execution feasibility and cost. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The execution claim includes resource/data assumptions and identifies unresolved external failures.

**Consumer, authority and communication.** Scientific operator and resource allocator. Scheduling authority is limited to allocated resources and permitted data movement. Expose execution-site, data-transfer and reported-error provenance to diagnosis and recovery consumers.

**Evidence needed.** Supply evidence that would establish or falsify: The execution claim includes resource/data assumptions and identifies unresolved external failures. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S042; EWM-S044; EWM-S049]; critical support: [EWM-S041; EWM-S047].

**Criticism, conflicts and anti-ceremony boundary.** Heterogeneous failures and data movement can dominate control-flow costs; fault reports may overlap and mislocalise causes. Judgement: Contextual scientific execution property; no universal cloud or engine choice follows. Criticisms: `EWM-C020`, `EWM-C021` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Local execution or a simple scheduler may dominate when data and resources are already co-located.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which failure category is costly enough to justify a more elaborate recovery mechanism? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-061 — Low-code abstraction and portability limits

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-061`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `CONDITIONAL_SELECTION_CRITERION`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Inspect the used abstraction’s execution, data, extension and exit boundaries before relying on visual simplicity or claimed portability. Conditional; current static studies do not establish universal benefit or failure rates. Controlled failure: Hidden code or vendor-specific behaviour defeats validation, portability or operator understanding.

**Trigger / non-trigger / cheap path.** A low-code/visual system is used for consequential automation or replacement is contemplated. Alternative: A simple script or manual procedure may be clearer; visual tooling may also be the cheaper adequate option.

**Prerequisites and domain.** Access to actual definitions, extension behaviour and the semantic subset relied upon. Contextual couplings: `EWM-004`, `EWM-018`, `EWM-041`, `EWM-058` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A low-code/visual system is used for consequential automation or replacement is contemplated. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Used behaviours and replacement costs are understood beyond the canvas appearance.

**Consumer, authority and communication.** Builder, operator and future maintainer. An accessible editor does not authorise the user to automate every connected action. Document the hidden boundaries and provide meaningful explanations to the people responsible for results.

**Evidence needed.** Supply evidence that would establish or falsify: Used behaviours and replacement costs are understood beyond the canvas appearance. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S017; EWM-S033; EWM-S031]; critical support: [EWM-S023; EWM-S025].

**Criticism, conflicts and anti-ceremony boundary.** Abstraction leaks, credential concentration, lock-in and static-template evidence mistaken for operational performance. Judgement: Conditional; current static studies do not establish universal benefit or failure rates. Criticisms: `EWM-C013`, `EWM-C022` Tensions: `EWM-T009` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A simple script or manual procedure may be clearer; visual tooling may also be the cheaper adequate option.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which control exists only in hidden code or outside the exported definition? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-062 — Agent-generated coordination under separately enforced constraints

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-062`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Treat generated routes or decisions as proposals under separately established semantic, authority, effect and observation constraints; distinguish configuration links from actual execution paths. Assumption-sensitive; preprints/static corpora do not validate general autonomous reliability. Controlled failure: A plausible generated plan violates a constraint or appears checked only because another node repeats its claim.

**Trigger / non-trigger / cheap path.** A learned component may change task selection, data interpretation or external action. Alternative: Use a fixed route or a human decision where learned flexibility has no demonstrated value.

**Prerequisites and domain.** Explicit action boundary, inspectable decisions and a means of evaluating consequences appropriate to the task. Contextual couplings: `EWM-002`, `EWM-025`, `EWM-030`, `EWM-043`, `EWM-058`, `EWM-073` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A learned component may change task selection, data interpretation or external action. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Invalid or unsubstantiated proposed actions can be rejected without relying on the same model’s assertion of safety.

**Consumer, authority and communication.** Operator, affected participant and the consumer accepting the outcome. An agent’s generated instruction is not self-authorising; external permissions and approval remain separate. Expose the decision basis, selected action and unresolved uncertainty to the appropriate consumer.

**Evidence needed.** Supply evidence that would establish or falsify: Invalid or unsubstantiated proposed actions can be rejected without relying on the same model’s assertion of safety. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S030; EWM-S031]; critical support: [EWM-S033; EWM-S041].

**Criticism, conflicts and anti-ceremony boundary.** Semantic drift, hallucinated evidence, opaque template structure and unmeasured human review burden. Judgement: Assumption-sensitive; preprints/static corpora do not validate general autonomous reliability. Criticisms: `EWM-C022`, `EWM-C023`, `EWM-C026` Tensions: `EWM-T010` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Use a fixed route or a human decision where learned flexibility has no demonstrated value.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What external evidence discriminates a genuine benefit from a plausible-looking generated workflow? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-063 — Contextual economic and organisational effectiveness

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-063`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `CONDITIONAL_SELECTION_CRITERION`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Evaluate the actual setting, comparison, implementation attrition and distribution of costs before claiming improvement attributable to workflow support. Conditional evidence practice; the available longitudinal study does not justify universal economic claims. Controlled failure: Adoption, simulated gains or survivor performance is presented as a universal causal benefit.

**Trigger / non-trigger / cheap path.** A business or organisational benefit claim justifies adoption or expansion. Alternative: A bounded trial, credible baseline and participant review may be enough; do not require a large experiment for every small decision.

**Prerequisites and domain.** Meaningful outcome measures, a defensible counterfactual and inclusion of unsuccessful deployments. Contextual couplings: `EWM-004`, `EWM-031`, `EWM-057`, `EWM-058` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A business or organisational benefit claim justifies adoption or expansion. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The benefit claim fits its study design and setting and includes adverse or null outcomes.

**Consumer, authority and communication.** Participants and the decision-maker bearing implementation and operating costs. A measured efficiency gain does not authorise shifting unacceptable burdens to others. Report who improved, who paid, what failed and what the comparison cannot establish.

**Evidence needed.** Supply evidence that would establish or falsify: The benefit claim fits its study design and setting and includes adverse or null outcomes. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S025; EWM-S034]; critical support: [EWM-S009; EWM-S033].

**Criticism, conflicts and anti-ceremony boundary.** Confounding, survivor bias, simulation calibration and metrics that omit hidden coordination work. Judgement: Conditional evidence practice; the available longitudinal study does not justify universal economic claims. Criticisms: `EWM-C001`, `EWM-C002`, `EWM-C021`, `EWM-C026` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. A bounded trial, credible baseline and participant review may be enough; do not require a large experiment for every small decision.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Would the same change improve outcomes without the engine, or with a simpler intervention? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-073 — Semantic-environment binding for durable AI execution

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-073`. **Disposition:** `ASSUMPTION_SENSITIVE`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED_WITH_EVIDENCE_LIMIT`.

**Mature form and controlled failure.** Bind and disclose the environment needed to interpret a decision or continuation, and evaluate declared compatibility before combining outputs from changed environments. Assumption-sensitive proposal with positive controlled prototype evidence; closed-world pinning remains a supported cheaper alternative. No established consensus or universal correctness/effect guarantee is inferred. Controlled failure: The workflow resumes durably while the meaning of its inputs or decisions has changed.

**Trigger / non-trigger / cheap path.** A long-lived learned workflow spans model, prompt, tool or retrieval changes that can alter meaning without changing control code. Alternative: For a closed dependency set, pin the relevant environment or require explicit review at a change boundary. The inspected prototype also prevents its closed-world anomalies with static pinning; online extension is justified only by genuinely late-discovered dependencies and a valid compatibility contract.

**Prerequisites and domain.** Identifiable semantic inputs and compatibility rules whose adequacy can be examined externally. Contextual couplings: `EWM-024`, `EWM-045`, `EWM-047`, `EWM-058`, `EWM-062` Domain profile: `EWM-DM10` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A long-lived learned workflow spans model, prompt, tool or retrieval changes that can alter meaning without changing control code. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Continuation states which environment it depends on and which compatibility claims remain assumptions.

**Consumer, authority and communication.** AI-workflow author, continuation operator and result consumer. A compatibility declaration is not proof of correctness and cannot authorise its own acceptance. Communicate relevant environment/version changes and the basis for accepting continued work.

**Evidence needed.** Supply evidence that would establish or falsify: Continuation states which environment it depends on and which compatibility claims remain assumptions. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S030; EWM-S027; EWM-S028]; critical support: [EWM-S031].

**Criticism, conflicts and anti-ceremony boundary.** Incomplete environment inventories, expensive pinning and contracts that assert rather than establish equivalence. Judgement: Assumption-sensitive proposal with positive controlled prototype evidence; closed-world pinning remains a supported cheaper alternative. No established consensus or universal correctness/effect guarantee is inferred. Criticisms: `EWM-C023`, `EWM-C026` Tensions: `EWM-T010` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. For a closed dependency set, pin the relevant environment or require explicit review at a change boundary. The inspected prototype also prevents its closed-world anomalies with static pinning; online extension is justified only by genuinely late-discovered dependencies and a valid compatibility contract.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What observable test can falsify a declared semantic compatibility contract? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-075 — Closure accounting across work and external obligations

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-075`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `ANALYTICAL_COMPOSITION_INVARIANT`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Before asserting closure, reconcile the local terminal state with the disposition of work and material external obligations: fulfilled, legitimately waived, transferred or explicitly unresolved under an accepted closure policy. Retain as a reasoned composition-induced criterion, with source-supported parts and no claim of empirical validation of the combined scheme. Controlled failure: Every local mechanism works but their composition drops the obligation between stopping work and satisfying the recipient.

**Trigger / non-trigger / cheap path.** Local cancellation/completion can coexist with still-running work or unremedied effects. Alternative: An explicit handover or acknowledged residual-obligation note can be sufficient; do not require one engine to own the whole world.

**Prerequisites and domain.** Closure claim, current work/effect inventory and authority for waiver, transfer or residual acceptance. Contextual couplings: `EWM-003`, `EWM-013`, `EWM-014`, `EWM-030`, `EWM-034`, `EWM-036`, `EWM-037`, `EWM-058`, `EWM-077` Domain profile: `EWM-DM06` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Local cancellation/completion can coexist with still-running work or unremedied effects. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The case may close without every action succeeding, but no material residue is silently recast as fulfilled.

**Consumer, authority and communication.** Case-closing actor, affected recipient and any successor responsible for residual work. Local terminal status is not unilateral permission to waive another participant’s commitment. Communicate closure’s meaning and obtain the relevant acknowledgement for transferred obligations.

**Evidence needed.** Supply evidence that would establish or falsify: The case may close without every action succeeding, but no material residue is silently recast as fulfilled. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S003; EWM-S016; EWM-S019; EWM-S020; EWM-S026; EWM-S050]; critical support: [EWM-S041].

**Criticism, conflicts and anti-ceremony boundary.** Accounting can turn into permanent bureaucracy if every hypothetical effect is tracked; scope by consequential claims and actual consumers. Judgement: Retain as a reasoned composition-induced criterion, with source-supported parts and no claim of empirical validation of the combined scheme. Criticisms: `EWM-C011`, `EWM-C017` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. An explicit handover or acknowledged residual-obligation note can be sufficient; do not require one engine to own the whole world.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? Which residual obligations are material enough that local closure needs an explicit disposition? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-076 — Recovery continuity across version, instance and external references

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-076`. **Disposition:** `RETAINED_IN_EVOLVED_FORM`. **Kind:** `ANALYTICAL_COMPOSITION_INVARIANT`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Recover or revise an instance only with a coherent account of its governing version, current state, pending work, message/effect identities and known external outcomes. Retain as analytical synthesis, not a newly proven universal theorem; downgrade automation when its prerequisites cannot be met. Controlled failure: Replay succeeds locally while callbacks, external effects or new definition semantics refer to a different logical execution.

**Trigger / non-trigger / cheap path.** A crash or migration crosses a definition/code or external-interaction boundary. Alternative: Continue the old version or perform a bounded manual reconciliation when a general automated migration/replay bridge is unnecessary.

**Prerequisites and domain.** Resolvable version/instance/action references and a validated mapping of continuing obligations. Contextual couplings: `EWM-001`, `EWM-022`, `EWM-042`, `EWM-043`, `EWM-044`, `EWM-046`, `EWM-047`, `EWM-048`, `EWM-049` Domain profile: `EWM-DM08` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: A crash or migration crosses a definition/code or external-interaction boundary. Correctness/observation claim: The candidate’s bounded acceptance evidence is: The resumed case’s next action is justified by a coherent state/effect/version account or is explicitly held for adjudication.

**Consumer, authority and communication.** Runtime recovery/migration operator and the participants relying on continuity. Continuity does not grant authority to modify prior commitments or fabricate missing evidence. Transmit preserved identity and unresolved state across version, worker and organisation boundaries.

**Evidence needed.** Supply evidence that would establish or falsify: The resumed case’s next action is justified by a coherent state/effect/version account or is explicitly held for adjudication. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S018; EWM-S021; EWM-S027; EWM-S028; EWM-S044; EWM-S045]; critical support: [EWM-S030].

**Criticism, conflicts and anti-ceremony boundary.** Cross-version contracts and old-state support add substantial maintenance cost; perfect reconstruction may be impossible. Judgement: Retain as analytical synthesis, not a newly proven universal theorem; downgrade automation when its prerequisites cannot be met. Criticisms: `EWM-C014`, `EWM-C015`, `EWM-C023` Tensions: No distinct named tension beyond the listed assumptions/costs. Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Continue the old version or perform a bounded manual reconciliation when a general automated migration/replay bridge is unnecessary.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? What is the minimum sufficient continuity record for this recovery claim? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

### EWM-077 — Explicit request, commitment, declaration and acceptance transitions

**Global key:** `EVOLVED_WORKFLOW_MANAGEMENT::EWM-077`. **Disposition:** `CONTEXT_DEPENDENT`. **Kind:** `OPERATING_MECHANISM`. **Examination:** `EXAMINED`.

**Mature form and controlled failure.** Use explicit request, commitment, declaration and acceptance distinctions when different participants need to agree what work is owed and whether it has been satisfied. Contextual operating mechanism with a real consumer; no claim that every workflow must implement its four phases. Controlled failure: A delivered request is treated as a promise, or a performer’s declaration is treated as recipient satisfaction.

**Trigger / non-trigger / cheap path.** Cooperative work depends on negotiated responsibilities rather than transport acknowledgement alone. Alternative: Ordinary conversation and a clear confirmation can suffice; do not impose a four-form ritual on every exchange.

**Prerequisites and domain.** Participants able to make the relevant commitments, shared meaning and a genuine opportunity to clarify or reject. Contextual couplings: `EWM-025`, `EWM-030`, `EWM-038`, `EWM-039`, `EWM-058` Domain profile: `EWM-DM07` plus all ten candidate-specific resolved fields in `EVOLVED_WORKFLOW_MANAGEMENT_PROPERTY_LEDGER.json`. Identity/application scope: Apply the model’s identity distinctions to this scope: Cooperative work depends on negotiated responsibilities rather than transport acknowledgement alone. Correctness/observation claim: The candidate’s bounded acceptance evidence is: Participants can distinguish what was requested, accepted, declared performed and accepted as satisfactory.

**Consumer, authority and communication.** Requester/customer and performer in the specific interaction. A recorded acceptance does not prove uncoerced consent, objective correctness or authority outside the relationship. Exchange the commitment and satisfaction conditions, including changed expectations and disagreement.

**Evidence needed.** Supply evidence that would establish or falsify: Participants can distinguish what was requested, accepted, declared performed and accepted as satisfactory. Distinguish the model/configuration, performed action and external result when they differ. Source support: [EWM-S050; EWM-S018]; critical support: [EWM-S009; EWM-S034].

**Criticism, conflicts and anti-ceremony boundary.** Rigid speech-act categories can oversimplify work and embed power asymmetries; material consequences remain separately observable. Judgement: Contextual operating mechanism with a real consumer; no claim that every workflow must implement its four phases. Criticisms: `EWM-C001`, `EWM-C009`, `EWM-C012` Tensions: `EWM-T003`, `EWM-T008` Retire or omit the extra machinery when the trigger, consumer or relevant dependency disappears, after settling/transferring the outstanding work or evidence that still relies on it. Ordinary conversation and a clear confirmation can suffice; do not impose a four-form ritual on every exchange.

**Neutral audit questions.** Does the actual system encounter this trigger, and what current mechanism or simpler arrangement already handles it? What evidence supports the stated postcondition, and what remains outside its observation or authority? When does formal acceptance obscure rather than resolve substantive disagreement? Would an omission, substitution or retirement preserve the protected outcome at lower total cost?

**Permitted findings:** already addressed; inapplicable; simpler mechanism sufficient; evidence insufficient; relevant improvement candidate requiring separate justification. No answer is supplied for the target.

## Non-retained and unresolved candidates — not unconditional obligations

**EWM-064 — Workflow restricted universally to a serial pipeline or DAG (`REJECTED_OR_DISFAVOURED`).** Rejected as a general property, while DAGs remain useful domain-specific forms. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: No general mechanism survives this restriction; select a DAG only for a scope whose behaviour is genuinely acyclic, or label it a finite expansion of a richer process. Evidence: [EWM-S006; EWM-S017; EWM-S042; EWM-S051; EWM-S013; EWM-S035]

**EWM-065 — Unqualified exactly-once effects outside the declared cooperative boundary (`REJECTED_OR_DISFAVOURED`).** Reject only the unqualified claim, not the formal results of cooperative systems. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: Replace the unqualified claim with an explicit effect boundary and validated idempotency, rollback, persistence or participation assumptions. Evidence: [EWM-S026; EWM-S044; EWM-S020; EWM-S029]

**EWM-066 — Diagram or conformance brand as sufficient correctness (`CEREMONY_NOT_GENERAL_PROPERTY`).** Ceremony, not a general property; EWM-018 carries the stronger corresponding obligation. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: No independent correctness mechanism is supplied by the artefact’s presence; retain only the communication or executable-semantic function it demonstrably serves. Evidence: [EWM-S017; EWM-S033; EWM-S023; EWM-S024]

**EWM-067 — Sound target definition as sufficient safe migration (`SUPERSEDED_BY_STRONGER_FORM`).** Superseded, retained in the denominator to prevent reintroduction of the weaker rule. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: Supersede definition-only approval with EWM-048’s current-state, data and outstanding-interaction migration check. Evidence: [EWM-S021; EWM-S035; EWM-S036]

**EWM-068 — Complete engine history as complete external truth (`NO_GENERAL_PROPERTY`).** No general property; valid scoped histories remain useful. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: No such general property exists; scope the history to observed events and couple stronger claims to appropriate external evidence. Evidence: [EWM-S045; EWM-S041; EWM-S050; EWM-S009; EWM-S031]

**EWM-069 — Compensation as universal restoration of the original world (`NO_GENERAL_PROPERTY`).** No general property of world restoration follows from a compensation handler. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: No universal inverse exists; record the compensator’s own effect and residual differences. Evidence: [EWM-S020; EWM-S016; EWM-S044]

**EWM-070 — Full pattern coverage as universal product-selection optimum (`REJECTED_OR_DISFAVOURED`).** Reject feature-maximality as a general property; pattern vocabulary remains useful. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: Replace feature-count maximisation with fit to required behaviours, semantic fidelity and total operating cost. Evidence: [EWM-S023; EWM-S051; EWM-S024; EWM-S033]

**EWM-071 — Automation as universal economic improvement (`NO_GENERAL_PROPERTY`).** No universal engineering property of improvement is established. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: No universal improvement guarantee is established; use EWM-063’s contextual evaluation, retain measured gains and include failed implementations without treating organisational cancellation as proof of engine malfunction. Evidence: [EWM-S025; EWM-S034; EWM-S009; EWM-S033]

**EWM-072 — Indefinite retention of all execution events as universal obligation (`REJECTED_OR_DISFAVOURED`).** Reject the universal requirement, not long retention where justified. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: Replace unlimited retention with claim-relative sufficient state and a justified retirement rule. Evidence: [EWM-S045; EWM-S027; EWM-S030]

**EWM-074 — Autonomous workflow optimisation with generally safe semantic preservation (`UNRESOLVED`).** Unresolved general effectiveness/guarantee claim, not an unexamined topic and not a prohibition on bounded experiments. Do not require this as a general control. Neutral question: is the actual claim scoped by the stronger form, or does the target evidence genuinely justify more? Relevant stronger form: Treat proposed optimisation as an unvalidated change requiring an external objective, semantic constraints, authority, evaluation and continuity checks; no general guarantee is supplied. Evidence: [EWM-S030; EWM-S031; EWM-S025; EWM-S033; EWM-S041]

## Cross-property adjudication

Use the exact relation guards, not the appearance of a dependency list, to determine obligations. A sound-control claim and a resource-feasibility claim may be complementary; pinning and migration can be alternatives; duty constraints and current capacity can conflict; termination and accepted residual transfer can coexist. Reconcile evidence shared by multiple properties once without erasing their separate genealogy or criticisms. The 13 analytical cases in the composed model provide neutral probes, not claims that the later target fails.

Preserve the original 77-ID denominator and source identities in any new crosswalk revision. Target evidence, findings, proposed changes and authorisation belong to that separate crosswalk. None is established by this packet.
