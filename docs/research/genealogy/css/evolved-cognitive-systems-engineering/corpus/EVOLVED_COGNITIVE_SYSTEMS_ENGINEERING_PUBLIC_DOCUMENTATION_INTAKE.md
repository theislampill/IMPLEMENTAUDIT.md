# EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

## Source-grounded explanation

Cognitive systems engineering grew from—but is not identical with—classical human factors. Early human factors addressed the fit among human capabilities, displays, controls, workspaces, selection and training. Supervisory-control and automation research then exposed a deeper problem: moving work to machines does not remove cognition; it redistributes monitoring, diagnosis, coordination, exception handling and recovery. CSE, Cognitive Work Analysis, ecological interface design and distributed-cognition traditions responded by analysing cognitive work in context, including tools, representations, constraints and other participants. [S001] [S003] [S005] [S006] [S007] [S025] [S027]

The strongest evolved synthesis treats the consequential unit as a bounded joint work system. It asks whether people and automation can obtain decision-relevant state in time; predict modes, transitions and likely effects; understand limits and uncertainty; exercise authority that matches capability; transfer control and obligations without false common ground; allocate scarce attention; and recover from surprise. This does **not** imply that every task needs a dashboard, CWA study, situation-awareness score, human approval or AI explanation. The implementation must be proportional, outcome-tested and tied to a live decision consumer. [S008] [S009] [S010] [S012] [S038] [S039] [S048] [S076]

## Strongest surviving engineering properties

| PROPERTY_ID | PROPERTY_NAME | CURRENT_STATUS | TRIGGER | CHEAP_PATH | MATURE_FORM | KEY_SOURCES |
| --- | --- | --- | --- | --- | --- | --- |
| ECSE-01 | Joint cognitive work system as the unit of design | JOINT_COGNITIVE_SYSTEM_PROPERTY | Consequential work in which decisions, representations, authority or control are distributed across two or more participants or artefacts. | For a low-consequence, single-actor, transparent deterministic operation, document the actor, state and effect without constructing a full joint-system model. | Define the work system boundary, cognitive functions, authority, information flows, dependencies, timing and adaptation; test joint performance, not merely component usability. | [S005], [S006], [S007], [S025], [S026], [S027] |
| ECSE-04 | Coordination design beyond function allocation | JOINT_COGNITIVE_SYSTEM_PROPERTY | Any consequential split of work between humans, automation, teams or agents. | A fully encapsulated, deterministic service with verified input/output contracts may need only interface and failure semantics rather than rich teaming protocol. | Use function allocation as an input, then close the coordination contracts, transitions, feedback and recovery for the joint activity. | [S002], [S003], [S014], [S015], [S016], [S038] |
| ECSE-06 | Residual-task and workload-migration analysis | STRONGLY_RETAINED | Any automation proposal that claims workload reduction, staffing reduction or safer human oversight. | For a transparent deterministic substitution with no material residual task, record the proof and avoid a heavyweight study. | Accept automation only with an explicit residual-work account, peak-load evaluation and named owner for newly created cognitive work. | [S008], [S010], [S013], [S014], [S015], [S017] |
| ECSE-07 | Decision-relevant state, mode, intent and consequence legibility | STATE_MODE_LEGIBILITY_PROPERTY | Whenever automation state changes the meaning, effect or permissibility of a consequential action. | For a stateless or single-mode operation, show the immediate action/effect and omit a mode apparatus. | Provide consequence-oriented mode legibility at the decision point, validated under realistic attention, stress and transition conditions. | [S009], [S011], [S012], [S076], [S077], [S078] |
| ECSE-08 | Transition, pending-action and commitment visibility | STATE_MODE_LEGIBILITY_PROPERTY | Asynchronous, delayed, queued, autonomous or multi-stage consequential actions. | For atomic local actions with immediate direct physical feedback, the effect itself may be sufficient. | Close each consequential transition with status, timing, owner and world-effect evidence proportional to risk. | [S009], [S012], [S038], [S052], [S076], [S079] |
| ECSE-10 | Command-to-world feedback closure | STATE_MODE_LEGIBILITY_PROPERTY | Remote, automated, safety-critical, delayed or externally coupled actions where acceptance is not equivalent to success. | For direct reversible manipulation with immediate reliable perceptual feedback, the world effect can close the loop without additional reporting. | Define completion in terms of the intended state and provide independent effect evidence proportional to consequence. | [S001], [S003], [S007], [S012], [S038], [S052] |
| ECSE-11 | Authority, responsibility, observability and capability alignment | AUTHORITY_HANDOFF_PROPERTY | Consequential automation, delegated decisions, multi-party control and exception recovery. | For reversible low-consequence suggestions, ordinary user choice and clear undo may be sufficient. | Use state-dependent authority contracts that specify who decides, who acts, who verifies, who may stop, and what capability evidence is required. | [S011], [S012], [S038], [S039], [S052], [S053] |
| ECSE-12 | Genuine human intervention capability rather than ceremonial oversight | AUTHORITY_HANDOFF_PROPERTY | Only when human intervention is claimed as a control for consequential automation. | Remove the approval step when risk is low or intervention cannot be made real; use engineered automatic constraints or independent safeguards instead. | Treat human oversight as a tested control relationship with explicit preconditions and failure criteria, not a ritual placement. | [S008], [S010], [S011], [S012], [S038], [S045] |
| ECSE-13 | Explicit and verified handoff of state, authority and obligations | AUTHORITY_HANDOFF_PROPERTY | Cross-person, cross-agent, cross-session or cross-shift transfer of consequential work or control. | For trivial same-context continuation with visible shared state, a brief acknowledgement or no formal handoff may suffice. | Use a proportional handoff contract with explicit ownership, acceptance, verification and discrepancy repair; distinguish transmitted claims from checked state. | [S037], [S038], [S052], [S065], [S067], [S068] |
| ECSE-14 | Takeover and re-entry readiness with state reacquisition and time budget | AUTHORITY_HANDOFF_PROPERTY | Whenever a human is the fallback for rare automation limits or failures. | Do not claim human fallback when the time budget or readiness cannot be sustained; use fail-safe automation, controlled degradation or another continuously engaged controller. | Design graded handback with early warning, compact state reconstruction, safe transition envelope, practice and demonstrated recovery performance. | [S008], [S010], [S049], [S050], [S054], [S055] |
| ECSE-16 | Calibrated reliance and verifiability rather than maximal trust | HUMAN_AUTOMATION_CONTEXT_PROPERTY | When automation advice or action is fallible and users can choose to rely, verify, override or abstain. | For deterministic, independently enforced functions, avoid trust messaging and expose simple guarantees/failure semantics. | Optimise appropriate reliance and decision quality, not subjective trust level; make verification cheaper where consequences are high. | [S013], [S039], [S040], [S041], [S042], [S043] |
| ECSE-18 | Actionable, prioritised, routed and escalated alerting | STRONGLY_RETAINED | Conditions requiring attention or intervention that would not otherwise be reliably perceived in time. | Use passive status, batching, audit logs or no notification when no immediate decision consumer or action exists. | Engineer alert portfolios as attention-allocation systems with lifecycle ownership, scenario/flood tests and outcome-linked escalation. | [S059], [S060], [S061], [S062], [S087], [S086] |
| ECSE-21 | Peak workload, transition load and reserve-capacity engineering | STRONGLY_RETAINED | Time-critical, multi-task or interruption-prone work where overload can delay or distort consequential action. | For low-pace work with ample slack, use direct task performance and simple staffing evidence rather than elaborate workload instrumentation. | Engineer peak demand and reserve capacity using converging performance, behavioural and subjective evidence, not a single average score. | [S008], [S017], [S050], [S056], [S057], [S058] |
| ECSE-32 | Learning from coordination failures, near misses and automation surprises | STRONGLY_RETAINED | Incidents, near misses, unexpected automation behaviour, workarounds or recurrent handoff/alert failures. | For trivial reversible errors, a local correction and lightweight pattern check may be enough. | Use mechanism-centred learning that can change architecture, representations, procedures, staffing, automation policy or training, with closure evidence. | [S009], [S070], [S071], [S072], [S073], [S076] |
| ECSE-41 | Decision-centred evaluation of joint-system performance | STRONGLY_RETAINED | Any claim that a new interface, automation policy, explanation or teaming arrangement improves consequential work. | For low-risk design iteration, task completion/error observation may be enough; reserve full comparative trials for material claims. | Make joint decision/action performance the primary endpoint and use cognitive constructs as explanatory measures with stated validity limits. | [S017], [S035], [S036], [S044], [S045], [S046] |

## Common caricatures and ceremonies to reject

- “Human factors means make the UI easier.”
- “Keep a human in the loop and the system is safe.”
- “Automation removes the human workload assigned to the machine.”
- “The mode name is visible, so the operator understands the mode.”
- “More information, alerts or explanation creates more awareness.”
- “Trust is good; maximise it.”
- “A second reviewer, signature or agent vote is independent verification.”
- “Acknowledgement or checklist completion proves understanding and resolution.”
- “A manual override proves takeover is feasible.”
- “A NASA-TLX, SAGAT or trust score establishes cognitive fit.”

## Important criticisms and limits

- Static function-allocation lists ignore coordination, residual work and changing capability.
- Situation awareness has competing individual, team and distributed ontologies, and its measures have uneven psychometric support.
- CWA and EID can be expensive, analyst-dependent, difficult to maintain and supported mainly in selected complex-control settings.
- Trust, workload and team-cognition scores are proxies whose relationship to consequential outcomes is context-dependent.
- Explanations may persuade without being faithful or improving decisions.
- Adaptive automation can create new mode and authority surprises when triggers and transitions are opaque.
- Handoffs and checklists are implementation-sensitive and can become rote completion rituals.
- Distributed/system accounts can become too broad to assign actionable responsibility.
- Interface and training interventions cannot compensate for fundamentally unobservable, uncontrollable or time-infeasible architecture.
- Human–AI combinations do not automatically outperform the better human or AI component.

## Shift from isolated optimisation to joint cognitive work

The historical shift is not a clean replacement of one school by another. Classical human factors continues to supply essential knowledge about perception, workload, displays and controls. The mature extension changes the **unit and object of design**: from optimising a person at an interface to engineering how cognitive functions, information, authority, timing and adaptation are coupled across people, automation, procedures and representations. Function allocation therefore becomes a coordination question; “awareness” becomes a set of state-access and prediction obligations; and human oversight becomes a tested control relationship rather than presence. [S005] [S007] [S015] [S025] [S027] [S038] [S052]

## Citation-ready factual claims

| CLAIM_ID | CLAIM | SOURCE_IDS | EVIDENCE_LABEL |
| --- | --- | --- | --- |
| PC-01 | Human factors emerged from wartime and post-war problems involving displays, controls, workspaces, selection, training and system design—not merely ease-of-use styling. | S001 S002 | SOURCE_ESTABLISHED |
| PC-02 | The Fitts list is historically influential, but later function-allocation research criticises static human-versus-machine matching as insufficient for coordination. | S002 S015 S016 | SOURCE_ESTABLISHED; SOURCE_INTERPRETATION |
| PC-03 | Bainbridge identified that automation can leave people responsible for monitoring and rare recovery while removing the practice needed to do those tasks well. | S008 | SOURCE_ESTABLISHED |
| PC-04 | Cognitive systems engineering shifted analysis toward cognitive work with tools and, later, the joint cognitive system rather than the isolated operator. | S005 S007 S027 S028 | SOURCE_ESTABLISHED |
| PC-05 | Distributed-cognition studies show that functional memory and calculation can be realised across people, procedures and external representations. | S025 S026 | SOURCE_ESTABLISHED; EMPIRICAL_OR_DOMAIN_FINDING |
| PC-06 | Mode-error and automation-surprise research shows that current mode must be understood in terms of consequences and expectations, not merely annunciated by name. | S009 S079 S076 | SOURCE_ESTABLISHED; ACCIDENT_OR_INCIDENT_EVIDENCE |
| PC-07 | The Atlas Air 3591 investigation found that mode indications and other cues were present although neither pilot effectively recognised the automated mode change. | S076 | ACCIDENT_OR_INCIDENT_EVIDENCE |
| PC-08 | Out-of-the-loop experiments and takeover meta-analyses support treating human fallback as a timed capability involving state reacquisition and control quality, not just access to manual mode. | S010 S054 S055 | EMPIRICAL_OR_DOMAIN_FINDING |
| PC-09 | Trust research distinguishes appropriate reliance from misuse and disuse; high trust is not an engineering objective in itself. | S013 S039 S040 S041 | SOURCE_ESTABLISHED; EMPIRICAL_OR_DOMAIN_FINDING |
| PC-10 | Automation-bias and cognitive-forcing research supports mechanism-specific verification rather than generic warnings to “stay vigilant.” | S042 S045 | EMPIRICAL_OR_DOMAIN_FINDING |
| PC-11 | Alarm research and current domain practice treat alerting as prioritisation and management of scarce attention, including false/nuisance alarms and lifecycle review. | S059 S060 S061 S062 S087 | EMPIRICAL_OR_DOMAIN_FINDING; DOMAIN_PRACTICE |
| PC-12 | A handoff programme can reduce selected medical errors, but checklist evidence varies by implementation and setting, so the transferable property is verified state/authority transfer rather than a named form. | S065 S068 S069 | EMPIRICAL_OR_DOMAIN_FINDING |
| PC-13 | Situation awareness remains a contested construct whose measures have heterogeneous validity; narrower state-access, prediction and coordination properties can survive the dispute. | S032 S033 S034 S036 S090 | CONTESTED; CONSTRUCT_OR_MEASUREMENT_DEPENDENT |
| PC-14 | Ecological interface design represents work-domain constraints and means-ends relations to support diagnosis beyond memorised procedures, but evidence is concentrated in selected complex-control domains. | S018 S021 S022 S023 | SOURCE_ESTABLISHED; EMPIRICAL_OR_DOMAIN_FINDING |
| PC-15 | Cognitive Work Analysis can expose constraints and strategy/role possibilities, but its cost, analyst dependence and maintenance burden argue for proportional use. | S006 S019 S020 S024 | SOURCE_ESTABLISHED; CRITIQUE_OF_IMPLEMENTATION |
| PC-16 | Explanation and interpretability experiments do not establish that more explanation uniformly improves decision quality; timing, faithfulness, actionability and cognitive effort matter. | S044 S045 S046 S047 | EMPIRICAL_OR_DOMAIN_FINDING |
| PC-17 | A 2024 meta-analysis found that human–AI combinations did not exhibit average synergy against the better solo component, so pairing a human with AI is not evidence of improved performance. | S048 | EMPIRICAL_OR_DOMAIN_FINDING |
| PC-18 | Current FAA and NASA human-system guidance treats interface and system behaviour as lifecycle engineering concerns involving normal and non-normal operation, error management and integrated human-system performance. | S012 S074 | DOMAIN_PRACTICE |
| PC-19 | Local-rationality and work-as-done approaches reject “human error” as a sufficient terminal explanation while preserving the possibility of evidence-based individual accountability. | S070 S071 S072 | SOURCE_ESTABLISHED; SOURCE_INTERPRETATION |
| PC-20 | Mature joint-work design requires a live consumer, owner, freshness/update rule and retirement criterion for alerts, procedures, displays and analytical artefacts. | S024 S061 S062 S071 S086 | SOURCE_INTERPRETATION; CONVERGENT_PROPERTY |

## Explicit evidence limits and claims not to make

- Do not claim that one formal methodology called “Evolved Cognitive Systems Engineering” exists; the label is an analytical synthesis.
- Do not claim that all human factors evolved linearly into CSE, or that CWA, EID, distributed cognition, situation awareness, CRM and resilience are one genealogy.
- Do not claim that the joint-system framing guarantees synergy; human–AI combinations can underperform the better component.
- Do not claim that situation awareness is a settled unitary construct or that SAGAT is universally valid.
- Do not claim that CWA or EID is always cost-effective, scalable or superior to lighter alternatives.
- Do not claim that more trust, transparency, explanation, information, alerts or automation is monotonically better.
- Do not claim that a human approval, override or monitoring role is a safety control without capability and timing evidence.
- Do not claim that checklist, CRM or handoff findings transfer unchanged across domains.
- Do not claim that accident cases alone quantify the effect of a property; they establish mechanisms and plausibility, not universal effect size.
- Do not claim that organisational/system analysis eliminates individual agency or accountability.
- Do not claim that adaptive autonomy or workload-triggered authority has mature general field evidence.
- Do not present chain-of-thought or narrative rationale as inherently faithful model transparency.

## Suggested public page outline

- 1. What the analytical label means—and does not mean.
- 2. Historical origins: classical human factors, supervisory control and the automation problem.
- 3. The unit-of-analysis shift: cognitive work, distributed representations and joint cognitive systems.
- 4. Why static function allocation failed: residual work, monitoring and transition debt.
- 5. State, mode, intent, uncertainty and effect closure.
- 6. Authority, capability, handoff and rare takeover.
- 7. Attention, alarms, workload peaks and underload.
- 8. Reliance, verification and the limits of trust/transparency.
- 9. Constraint-oriented representation, procedures and adaptation.
- 10. Ceremony stripping: properties versus dashboards, questionnaires, checklists and human-in-loop rituals.
- 11. Evidence limits, contested constructs and domain-specific practices.
- 12. Strongest surviving properties and questions for later system audit.

## Direct-lineage versus convergence and domain translation

| ITEM | CLASSIFICATION | PUBLIC EXPLANATION |
| --- | --- | --- |
| Joint cognitive system, work demands, constraint modelling | CSE_NATIVE | Directly grounded in CSE/JCS/CWA primary literature. |
| Displays, controls, workload, human performance | CLASSICAL_HUMAN_FACTORS_ANCESTRY | Core ancestry retained; not reduced to interface aesthetics. |
| Supervisory control, levels, adaptive automation | CONTROL_THEORY_IMPORT_OR_SHARED_ANCESTRY / HUMAN_AUTOMATION_LINEAGE | Direct adjacent lineage; taxonomies are descriptive, not sufficient design rules. |
| Grounding, common ground, team-player requirements | TEAM_COGNITION_IMPORT | Imported/hybridised where interdependence requires communication and repair. |
| Graceful adaptation and work-as-done | RESILIENCE_IMPORT_OR_HYBRID | Related and partly overlapping authorship, but not collapsed into one genealogy. |
| Feedback closure, provenance, alarm lifecycle | CONVERGENT_PROPERTY | Compatible engineering properties also established outside CSE. |
| CRM, I-PASS, nuclear EID, automated-driving takeover | DOMAIN_TRANSLATION | Evidence and implementation forms are domain-specific; mechanisms may transfer. |
| Explainable AI and modern agent supervision | DOMAIN_TRANSLATION / ONLY_ANALOGOUS where lineage is absent | Admit only coordination-relevant properties; do not invent historical descent. |

## Public-documentation intake receipt

```text
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
CITATION_READY_CLAIMS: 20
PROPERTY_DENOMINATOR_LINKED: 62/62
```
