# EVOLVED_SYSTEMS_SAFETY_PUBLIC_DOCUMENTATION_INTAKE

Systems-safety traditions grew from industrial accident prevention and military reliability into lifecycle hazard programmes for aerospace, defence, nuclear, process, medical, automotive and rail systems. Their mature common ground is not a universal worksheet. It is the disciplined prevention of unacceptable loss across interacting hardware, software, humans, organisations and environments: identify hazardous states, choose analyses that can represent the relevant causal classes, establish enforceable constraints and authority, and obtain feedback that the intended safe state was actually reached. [S005; S008; S010; S012; S014; S021; S027]

Later reforms exposed limits of component-only and compliance-only reasoning. STAMP/STPA made unsafe control and feedback explicit; safety-case research made assurance arguments visible while also exposing confirmation and staleness hazards; accident investigations showed that accepted components, redundant channels and nominal procedures can compose unsafely. The defensible evolved form is consequence-sensitive and change-aware: deepen independence, assurance, containment and recovery when harm is severe, irreversible, coupled or hard to observe, while preserving a direct cheap path for local reversible work conclusively settled by an authoritative discriminator. [S017; S018; S036; S044; S048; S050; S081–S090; S098]

## Strongest surviving engineering properties

- **ESS-001 — Explicit unacceptable-loss framing:** A concise, current, decision-linked definition of unacceptable loss that bounds later analysis without pretending completeness. Sources: S012, S014, S015, S018, S033.
- **ESS-002 — Hazardous system-state framing distinct from failure:** A current loss-linked hazardous-state model with explicit boundary, exposure and causal assumptions. Sources: S012, S014, S015, S018, S025, S033.
- **ESS-003 — Enforceable safety constraints:** The minimum sufficient constraint is explicit, allocated, enforceable, verified and paired with feedback or bounded assurance. Sources: S012, S015, S018, S029, S100.
- **ESS-008 — Unsafe interaction and unsafe-control analysis:** Explicitly reason about unsafe composition and control context, using the cheapest adequate representation and complementary techniques. Sources: S014, S017, S018, S020, S025, S109.
- **ESS-009 — Closed-loop control and feedback integrity:** Every consequential control has evidence sufficient to establish intended state, or the system treats state as unknown and constrains operation. Sources: S018, S051, S058, S089, S101.
- **ESS-012 — Interface assumptions and safety contracts:** Safety-relevant assumptions are explicit, version-bound, validated and invalidated by change. Sources: S012, S029, S083, S090, S100.
- **ESS-013 — Common-cause, common-mode and dependent-failure reasoning:** Claim independence only after identifying shared causes and monitoring the assumptions that sustain it. Sources: S040, S041, S050, S051, S056, S087.
- **ESS-018 — Traceability from hazards and constraints to implementation and verification:** Maintain only decision-relevant traceability sufficient to show current hazard-to-control-to-evidence closure. Sources: S029, S031, S042, S047, S100.
- **ESS-019 — Uncertainty-aware risk representation rather than score-only governance:** Choose the least elaborate representation that preserves decision-relevant consequence and uncertainty; never call the score the risk. Sources: S034, S036, S037, S038, S039, S040.
- **ESS-020 — Consequence, reversibility, coupling and observability proportionality:** Control strength rises with credible loss and irreversibility/coupling/latency, while deterministic low-risk work remains cheap. Sources: S014, S029, S035, S052, S053, S095, S104.
- **ESS-025 — Informational independence and diversity of assurance evidence:** Require independently informative evidence in proportion to consequence and explicitly disclose shared assumptions and sources. Sources: S044, S046, S049, S050, S099.
- **ESS-028 — Configuration identity binding for safety evidence:** No consequential safety claim is reusable without demonstrating that its configuration, environment and assumptions still match. Sources: S012, S029, S042, S047, S052, S100.
- **ESS-029 — Safety impact analysis and proportionate re-assurance after change:** Re-establish exactly the safety claims whose system, assumptions, controls or evidence may have changed; justify both reuse and new work. Sources: S052, S053, S054, S055, S095, S098.
- **ESS-035 — Containment, isolation and emergency stop with state confirmation:** Containment is achieved only when the hazardous process state is demonstrably bounded, not when a command is issued. Sources: S051, S058, S101, S102, S103.
- **ESS-037 — Recovery, rollback and restart only after restored safety constraints:** Recovery is complete only when relevant safety constraints and feedback are re-established and an authorised owner accepts the remaining uncertainty. Sources: S060, S102, S103, S104, S105.

## Common caricatures and ceremonies to reject

- **Risk-matrix cell treated as objective risk or sufficient decision evidence:** NO_GENERAL_PROPERTY in the claim that a matrix score is risk; retain explicit, uncertainty-aware and decision-linked risk representation instead.
- **Maximal safety process on every change:** NO_GENERAL_PROPERTY in uniform maximal treatment; apply only the control depth needed to discriminate and control the credible loss.
- **Compliance or certification treated as proof of current system safety:** Certification is a bounded governance/evidence decision, not a guarantee that all hazards are identified, controlled or unchanged.
- **Zero observed incidents treated as proof that controls work:** NO_GENERAL_PROPERTY in incident-free proof; require evidence proportionate to rarity, exposure and causal control state.
- **Human error used as the root-cause endpoint:** Human action is analysed as part of a sociotechnical control system; “error” alone never closes causal or corrective-action burdens.
- **More redundancy treated as automatically safer:** Use the minimum architecture that controls the hazard with demonstrable independence and manageable interaction complexity.
- **Reviewer or evidence-item count treated as assurance strength:** Assurance strength depends on relevance, validity, currentness and independently informative failure modes—not artefact or reviewer count.
- **Complete safety case treated as proof the system is safe:** A case is a defeasible justification for a bounded decision, never a proof that all system hazards are absent or controlled.
- **One universal hazard-analysis technique:** Use the minimum complementary method set needed to represent credible causal classes and make decisions; declare what remains outside.
- **Zero-risk or absolute-safety requirement as a general engineering target:** NO_GENERAL_PROPERTY in absolute safety; engineer against specified unacceptable losses with bounded evidence and transparent residual uncertainty.

## Important criticisms and limits

- **Component-centric analysis misses unsafe interactions.** Retain failure analysis but add system interaction/control/interface reasoning. Sources: S017; S018; S083; S084; S088; S089.
- **FMEA can become mechanical row completion.** Hazard-relevant scope, credible modes/effects and action closure; use complements. Sources: S007; S038.
- **Fault trees omit unknown, dynamic, software or organisational interactions.** Use within represented logic, expose dependencies/uncertainty and complement with scenario/control methods. Sources: S008; S009; S017; S109.
- **Risk matrices are inconsistent and falsely precise.** Separate consequence and uncertainty; use scores only as transparent non-dispositive prompts. Sources: S036; S037; S038.
- **Rare-event probabilities are unsupported by data.** State epistemic limits, sensitivity and alternatives; use constraints/monitoring where quantification cannot decide. Sources: S039; S040; S041.
- **SIL, ASIL and DAL are read as direct probabilities of total safety.** Use hazard-derived graded rigour within domain scope and complement interaction/intended-function analyses. Sources: S021; S023; S024; S025; S029.
- **Hazard logs go stale and reward entry count.** Configuration-aware current hazard/control/decision state with ownership and retirement. Sources: S012; S042; S047; S048.
- **Safety cases become paperwork and confirmation bias.** Living, defeater-led, provenance-aware cases tied to a live decision. Sources: S044; S045; S046; S047; S048; S108.
- **Nominally independent evidence is correlated.** Map common sources/oracles/incentives and require independently informative evidence. Sources: S050; S048.
- **Compliance with a standard replaces hazard control.** Treat compliance as bounded evidence and preserve current hazard/control authority. Sources: S012; S029; S048; S082; S089.

## From component failure toward unsafe system interaction and control

FMEA/FMECA and fault trees remain valuable where component/function failures and logical combinations dominate. They do not establish that locally correct components, software, operators and organisations will compose safely. System-safety programmes already contained system/interface/operational hazard analyses; STAMP/STPA made the control formulation more explicit by asking which actions are unsafe in context, whether actions are mistimed or missing, whether controller process models match the process, and whether feedback establishes the achieved state. ISO 21448’s intended-function scope and major software/automation accidents independently reinforce the same boundary. The public claim should therefore be complementarity: failure analysis plus interaction/control reasoning selected by causal coverage, not STPA replacing all prior methods. [S012; S014; S017; S018; S019; S020; S025; S083; S084; S088; S089]

## Citation-ready factual claims

1. Military/aerospace system safety is a lifecycle engineering programme concerned with hazards across hardware, software, operations and interfaces, not merely component reliability. **Source IDs:** S012; S014; S015; S016.
2. FMECA originated as a structured military method for examining failure modes, effects and criticality and remains bounded to failure-oriented reasoning. **Source IDs:** S005; S006; S007.
3. Fault-tree analysis is a top-down logical method for combinations leading to a defined top event; its result depends on the selected boundary, events and dependence model. **Source IDs:** S008; S009.
4. HAZOP emerged from process-industry multidisciplinary deviation analysis and uses guidewords to challenge design intent. **Source IDs:** S010; S011.
5. IEC 61508 distinguishes functional safety from total safety and addresses random hardware and systematic causes through safety functions and lifecycle measures. **Source IDs:** S021; S022; S023.
6. ISO 21448 addresses hazards from insufficiencies in intended functionality even when no E/E malfunction exists, marking a boundary of malfunction-centric functional safety. **Source IDs:** S024; S025.
7. STAMP/STPA reformulates safety around constraints, control actions, process models and feedback and can represent hazardous interactions without component failure. **Source IDs:** S017; S018.
8. Published reviews and FAA-sponsored evaluation support STPA’s usefulness while leaving scalability, subjectivity and broad comparative effectiveness unresolved. **Source IDs:** S019; S020.
9. Common severity-likelihood matrices can have ranking and range-compression defects and should not be treated as objective risk. **Source IDs:** S036; S037; S038.
10. A safety case is an argument for a bounded decision, not proof that every hazard is controlled; the Nimrod Review shows catastrophic divergence between accepted paper assurance and actual condition. **Source IDs:** S042; S044; S048.
11. Nominally independent software versions or reviews may share common assumptions and errors, so evidence independence is informational as well as organisational. **Source IDs:** S050.
12. Ariane 5 Flight 501 and Therac-25 illustrate losses involving software assumptions and system interactions rather than simple random hardware failure. **Source IDs:** S083; S084.
13. Challenger, Columbia, Texas City and Fukushima investigations identify organisational decision, communication, production-pressure or common-mode mechanisms. **Source IDs:** S081; S082; S085; S087.
14. Modern change regimes in aviation, rail, nuclear safety and medical devices assess affected scope and permit justified reuse rather than requiring universal full re-certification. **Source IDs:** S052; S053; S054; S055.
15. Alarm systems require a timely actionable consumer and burden control because nuisance and alarm floods can degrade safety. **Source IDs:** S074; S075.
16. Human error is not a sufficient causal endpoint; mature investigation examines local rationality, context, system defences and actionable upstream mechanisms. **Source IDs:** S063; S064; S076; S077.
17. NTSB and CSB track recommendation implementation, reflecting the distinction between issuing an analysis and closing the causal-control loop. **Source IDs:** S078; S079; S093; S115.
18. Safety and cybersecurity share control, feedback, availability and configuration pathways in cyber-physical systems and therefore require coordinated analysis and change authority. **Source IDs:** S026; S028; S061.

## Explicit evidence limits and claims not to make

- Do not claim that one formal methodology called “Evolved Systems Safety” exists; the label is an analytical synthesis.
- Do not claim a single direct lineage from early accident prevention through every modern school.
- Do not claim that STPA is universally superior, complete or validated as a replacement for FMEA, FTA, HAZOP or domain methods.
- Do not claim that standards or certification empirically prove optimal implementation or eliminate operational risk.
- Do not interpret SIL, ASIL or DAL as the probability that an entire system is safe.
- Do not describe a risk-matrix score as objective risk or proof of acceptability.
- Do not claim that safety cases, independent reviewers, redundancy or evidence volume automatically increase safety.
- Do not treat zero incidents, generic safety-culture scores or resilience language as direct evidence of effective hazard control.
- Do not generalise nuclear, aviation, automotive, medical or rail certification artefacts outside their applicability without a mechanism-level justification.
- Do not claim empirical comparative effect sizes where the packet records only historical, formal, accident-case, standard or expert-practice support.

## Suggested public page outline

1. Scope and analytical status of `EVOLVED_SYSTEMS_SAFETY`.
2. Dated plural genealogy: reliability, process safety, system safety, functional safety, assurance, organisational critique, control theory and resilience.
3. The core distinction: component failure versus hazardous system interaction/control.
4. Strongest surviving properties and their consequence/reversibility triggers.
5. Hazard-analysis methods as complementary representations.
6. Risk and uncertainty without matrix-as-truth.
7. Assurance, configuration, change and living evidence.
8. Containment, degraded operation, recovery and restart.
9. Human/organisational control and incident learning.
10. Ceremonies, rejected simplifications and evidence limits.
11. Source register and claim-to-source table.

## Direct-lineage, convergent and domain-specific distinctions

- **SYSTEM_SAFETY_NATIVE:** lifecycle loss/hazard framing, hazard analyses, control hierarchy, risk acceptance and programme authority from military/aerospace system safety.
- **RELIABILITY_ANCESTRY:** FMEA/FMECA, FTA, dependence/common-cause and redundancy reasoning.
- **HUMAN_FACTORS_IMPORT_OR_SHARED_ANCESTRY:** local rationality, usability, workload, automation mode and just reporting.
- **SYSTEMS_ENGINEERING_IMPORT_OR_SHARED_ANCESTRY:** configuration, interfaces, requirements allocation, integration and lifecycle transitions.
- **QUALITY_OR_STATISTICAL_IMPORT:** event/exposure data, measurement discipline and quantitative reliability/risk where supported; no other research lane is imported.
- **CONTROL_THEORETIC_REFORMULATION:** safety constraints, unsafe control actions, process models and feedback in STAMP/STPA.
- **HYBRID_RESOLUTION:** safety-security co-engineering, living assurance, runtime envelopes, action verification and change-aware evidence reuse.
- **CONVERGENT_PROPERTY:** multiple domains independently support consequence proportionality, configuration identity, state-confirmed control and action closure.
- **DOMAIN_TRANSLATION:** SIL/ASIL/DAL, nuclear defence-in-depth, aviation certification objectives, medical submissions and rail CSM.
- **ONLY_ANALOGOUS:** generic Swiss-cheese or resilience metaphors when not tied to an explicit causal/control mechanism.
- **UNRESOLVED_TENSION:** comparative effectiveness, hazard completeness, adaptive-system assurance and the exact balance of independence, speed and service availability.
