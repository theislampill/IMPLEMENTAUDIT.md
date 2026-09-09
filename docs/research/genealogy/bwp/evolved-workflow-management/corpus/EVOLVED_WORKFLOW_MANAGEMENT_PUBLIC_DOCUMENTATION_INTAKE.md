# Workflow Management — public-documentation intake

## Introduction suitable for adaptation

Workflow Management is the established study and practice of representing, coordinating and enacting work across people and applications. Its objects include definitions, running instances, work items, data and interactions. Its history is plural: office information systems and document routing, transaction processing, cooperative work, formal workflow nets, language-action approaches and later process-aware systems addressed different coordination problems. The Workflow Management Coalition’s 1995 reference model consolidated terminology and interfaces; it did not invent the whole field. [EWM-S001–S002; EWM-S020; EWM-S034; EWM-S050]

Later work made control semantics more explicit through workflow nets, patterns and executable languages, expanded attention to data, resources and exceptions, and developed adaptive, declarative and case-centred alternatives. Scientific workflows and durable execution translate some of these mechanisms into environments with different recovery, resource and result-validation assumptions. “Evolved Workflow Management” is the name of this packet’s criticism-tested analytical synthesis—not an established historical school or a claim of universal agreement. [EWM-S004–S008; EWM-S013–S016; EWM-S021–S022; EWM-S035–S037; EWM-S041–S044]

## Evolution under criticism

The tradition is not accurately represented as a march towards more rigid automation. Cooperative-work criticism exposes the gap between prescribed procedures and the work people perform to make them useful. Formal analysis exposes deadlocks and residual work but also clarifies its own model boundaries. Pattern and standardisation disputes show why a catalogue or conformance badge cannot substitute for relevant semantic evidence. Longitudinal deployment evidence includes favourable performance in most implemented comparisons, important exceptions and abandonment chiefly associated with organisational/programme change. These findings support conditional selection, participation and proportionate machinery rather than universal automation. [EWM-S009; EWM-S023–S025; EWM-S033–S034]

Exception and recovery research similarly narrows claims rather than promising perfect restoration. A timeout can leave the outside effect unknown; cancellation can have a limited scope; compensation is a further fallible action. Running-instance change needs a valid relation between current state and new semantics, not only a valid new diagram. These distinctions are central to the evolved account. [EWM-S016; EWM-S020–S021; EWM-S026–S028]

## The within-tradition composition

The analytical system connects explicit identity and enabling rules to data conditions, eligible/available actors, communication and actual work. Observations qualify what the system may claim about completion. Exception, cancellation, recovery and revision loops can interrupt ordinary execution; concurrency and repeated work are preserved. A small stable task may need only a concise procedure, an accountable performer and an adequate result check. A long-lived cross-application case may need more precise persistence, retry, version and external-effect contracts.

Two explicitly analytical additions are closure accounting across work and external commitments (EWM-075) and continuity of instance meaning and external references across recovery/version change (EWM-076). They compose established distinctions but are not claimed as separately proved academic results. The system preserves alternatives—prescribed, declarative, case-centred, scientific and replay-based forms—rather than requiring every technique simultaneously.

## Strongest properties and caricatures to avoid

The strongest distinctions concern definition/instance identity; explicit semantics; model-to-engine correspondence; case/message correlation; work-item ownership; authority versus readiness; completion declaration versus achieved effect; interrupt scope; timeout uncertainty; compensation versus rollback; duplicate-effect control; migration validity; and observation limits. The operative implementation must match an actual trigger and consumer. A retained property does not require a new artefact, tool or owner in every host.

Workflow is not universally a serial pipeline or DAG. A sound net is not proof of business correctness, staffing, deadlines or external success. A role is not an available authorised individual. A diagram, log, test-execution status or brand is not automatically the thing it describes. More pattern coverage, more retained events and more automation are not universal maturity measures. Rejecting those caricatures does not prohibit DAGs, standards, logs or automation in their valid scopes.

## Citation-ready factual claims

The following claims are bounded to inspected evidence. They may be cited with the source/locator identifiers; the exact bibliographic records and URLs are in the source table.

| Claim | Source and locator | Boundary |
|---|---|---|
| The archived reference-model draft is dated 29 November 1994, while the final WfMC release is dated 19 January 1995. | EWM-S001-L01; EWM-S002-L01 | Do not substitute an archive upload or printing date for publication. |
| The reference model distinguishes build-time definition from run-time enactment and interaction with people/applications. | EWM-S001-L01; EWM-S002-L01 | It is a reference architecture, not empirical proof of benefit. |
| Classical workflow-net soundness includes possible completion from reachable states, proper completion and absence of dead tasks. | EWM-S004-L01; EWM-S007-L01 | Possible continuation is not inevitable termination of every execution. |
| The 2006 revised control-flow report revisits twenty patterns and adds twenty-three, giving 43. | EWM-S051-L01 | This is a catalogue count, not a universal required property count. |
| Workflow pattern research explicitly extends beyond control flow to data, resource and exception perspectives. | EWM-S014-L01; EWM-S015-L01; EWM-S016-L01 | Taxonomy and historical product comparison do not establish deployment frequencies. |
| The original Sagas discussion includes failures of compensation and other errors beyond the ideal recovery path. | EWM-S020-L01 | Compensation does not universally recreate the original world. |
| ADEPTflex couples structural workflow changes to current state/data preconditions. | EWM-S021-L01 | A sound target definition alone does not establish safe live migration. |
| Declarative constraints can interact to create conflicts or dead activities. | EWM-S035-L01 | Freedom of ordering does not eliminate verification or progress obligations. |
| CMMN 1.1 stage-completion conditions admit specified terminal child states, including Failed, and are not an all-children-success guarantee. | EWM-S019-L01 | Business acceptance needs a separately declared interpretation. |
| The longitudinal study distinguishes ten organisations/25 intended processes, five implementing organisations/seven enacted processes and five validated simulation comparisons. | EWM-S025-L01 | These are nested evidence populations, not independent successful replications. |
| Historical BPMN engine tests found incomplete support and regressions across tested versions. | EWM-S033-L01 | Not a current engine ranking or proof that all missing features matter equally. |
| Yevis test-execution success does not establish that the resulting outputs are expected or scientifically correct. | EWM-S041-L01 | The appropriate output oracle depends on the scientific task. |
| The inspected Taverna account includes iteration and streaming in scientific workflow execution. | EWM-S042-L01 | Scientific workflow is not uniformly DAG-only. |
| ExoFlow’s exactly-once DAG result has explicit task, determinism/idempotence or rollback and persistence assumptions. | EWM-S044-L01 | Do not generalise the guarantee to arbitrary uncooperative external effects. |
| The 2026 semantic-isolation audit reports four exposure-positive projects among 54 classified durable, within 100 selected eligible projects. | EWM-S030-L01 | Static exposure is not an observed harmful-incident rate or independent validation. |
| The 2026 n8n study analyses more than 6,000 public templates and distinguishes execution wiring from AI configuration. | EWM-S031-L01 | The inspected exact final denominator is not supplied; static templates are not runtime evidence. |

## Evidence limits and current frontier

The packet contains 77 examined candidate records rather than only a favourable summary. It separates provenance, theory, standards/implementation, comparisons, field evidence, replication, contrary findings and transferability. Seven source records are metadata/abstract-limited; the original technical critique and some workflow-decay methods are not represented as fully read. A recent distributed-fault presentation is not silently substituted for its inaccessible full proceedings methods. The JSON records preserve these limits and common evidence programmes.

Current questions concern changing external/semantic environments, hidden actions in visual or learned workflows, result-validation oracles, recovery/effect boundaries and actual human/organisational payoff. Current-year preprints include controlled anomaly-prevention experiments as well as static audits; these are meaningful within their assumptions but do not establish general safe autonomous optimisation. EWM-074 remains unresolved. The 13 composed test cases are analytical probes, not empirical validation.

## Suggested page outline

1. Define Workflow Management and distinguish definitions, instances, engines, organisational processes and event evidence.
2. Present the plural genealogy and the problems each branch addressed, with original/edition dates.
3. Explain the control/data/resource/interaction coupling, including loops, concurrency and interruptions.
4. Show model, implementation, authority and outside-effect boundaries through one carefully labelled analytical case.
5. Explain alternatives and proportional adoption, followed by criticism and evidence limits.
6. Introduce this packet’s analytical composition and link the complete 77-ID denominator, sources and open questions.

## Claims not to make

Do not claim invented origins, a single universally agreed workflow ontology, an established historical school named Evolved Workflow Management, or guarantees outside their model/environment assumptions. Do not equate formal soundness with every actual run terminating, output correctness, sufficient capacity or legitimate authority. Do not convert a selected deployment, static template audit or fault presentation into universal benefit or incidence. Do not equate popularity, standardisation, more automation or more agents with maturity. Do not imply that an unspecified host system has adopted or implemented any property. Do not present the two composition-induced invariants or the test probes as independently validated academic results.
