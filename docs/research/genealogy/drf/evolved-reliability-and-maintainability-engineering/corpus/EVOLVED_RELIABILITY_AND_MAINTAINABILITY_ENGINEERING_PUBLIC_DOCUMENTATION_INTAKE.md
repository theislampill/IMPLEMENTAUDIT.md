# EVOLVED_RELIABILITY_AND_MAINTAINABILITY_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

**State:** `FROZEN`  
**Run date:** `2026-08-12`

## Source-grounded explanation

Reliability and maintainability engineering did not arise as one method. Statistical life-data and renewal theory asked how failures and repairs are distributed; wartime and post-war electronics programmes joined requirements, parts, environment, prediction and test; FMEA/FMECA and fault trees examined failure paths; maintainability and supportability addressed diagnosis, access, repair and logistics; reliability growth and FRACAS connected failures to corrective action; fault-tolerant computing designed continuation and recovery despite activated faults. These lineages later converged in dependability and mission-success practice without becoming interchangeable. [SRC-001](https://doi.org/10.1115/1.4010337), [SRC-002](https://catalog.hathitrust.org/Search/Home?lookfor=%22Reliability%20of%20Military%20Electronic%20Equipment%22&type=title), [SRC-004](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=37027), [SRC-005](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0492/), [SRC-009](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=54046), [SRC-020](https://doi.org/10.1109/TDSC.2004.2).

Modern service reliability/SRE, chaos engineering, PHM and AI-enabled operations are translations or hybrids, not automatic endpoints. Current NASA and IEC guidance centres required performance, lifecycle objectives, maintainability/supportability and justified confidence; contemporary incident and review evidence keeps common-cause failure, recovery validity, operational-profile transfer, SLO adoption, RUL uncertainty and automated authority open as engineering burdens. [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-030](https://tc56.iec.ch/dependability-standards/), [SRC-031](https://tc56.iec.ch/dependability-standards/), [SRC-056](https://doi.org/10.6028/NIST.SP.800-184), [SRC-066](https://www.usenix.org/publications/loginonline/what-sre-could-be), [SRC-070](https://doi.org/10.1145/3777375), [SRC-072](https://doi.org/10.1016/j.ress.2025.112110).

## Strongest surviving engineering properties

### ERM-P001 — Explicit required-function and mission semantics
A testable, versioned mission contract that binds required function, mode, profile, environment, interval/demand, degraded acceptance and consumer consequence.  
**Trigger:** Any reliability, availability, demonstration, redundancy, recovery or service-level claim that could drive design, release, maintenance or acceptance.  
**Cheap path:** For low-consequence reversible work, use a direct pass/fail functional check and a short observation window rather than a probabilistic programme.  
**Evidence:** [SRC-002](https://catalog.hathitrust.org/Search/Home?lookfor=%22Reliability%20of%20Military%20Electronic%20Equipment%22&type=title), [SRC-004](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=37027), [SRC-020](https://doi.org/10.1109/TDSC.2004.2), [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-030](https://tc56.iec.ch/dependability-standards/)

### ERM-P002 — Operational-profile, environment and demand definition
A configuration-bound, uncertainty-labelled exposure model that supports both representative sampling and explicit stress/boundary cases.  
**Trigger:** Prediction, demonstration, accelerated testing, software testing, SLO definition, capacity planning, maintenance policy or field-transfer claim.  
**Cheap path:** Use a small set of bounding scenarios when a full probability distribution would not change the decision.  
**Evidence:** [SRC-019](https://doi.org/10.1109/52.199724), [SRC-033](https://tc56.iec.ch/dependability-standards/), [SRC-040](https://www.itl.nist.gov/div898/handbook/apr/apr.htm), [SRC-080](https://doi.org/10.1109/ISSRE.1992.285850)

### ERM-P003 — Explicit complete, partial, intermittent, latent and degraded failure states
A minimal consequence-relevant state model with explicit observation, entry/exit criteria, allowed duration and treatment of latent states.  
**Trigger:** Systems with multiple modes, redundancy, standby, partial service, performance thresholds, intermittent faults or hidden protective functions.  
**Cheap path:** A binary state is sufficient only when the consumer consequence is genuinely binary and the observation tests the complete function.  
**Evidence:** [SRC-004](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=37027), [SRC-020](https://doi.org/10.1109/TDSC.2004.2), [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-036](https://tc56.iec.ch/dependability-standards/)

### ERM-P005 — Separate reliability, availability, maintainability, supportability and durability claims
A small RAM measure set tied to explicit functions, state transitions, total downtime components and decision thresholds.  
**Trigger:** Any claim using reliability, uptime, availability, MTBF, MTTR, serviceability, durability or operational readiness.  
**Cheap path:** Use direct failure count and downtime decomposition when a full stochastic model is unnecessary; never collapse the labels.  
**Evidence:** [SRC-009](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=54046), [SRC-021](https://books.google.com/books?id=0VxRAAAAMAAJ), [SRC-022](https://epubs.siam.org/doi/book/10.1137/1.9781611971194), [SRC-030](https://tc56.iec.ch/dependability-standards/), [SRC-031](https://tc56.iec.ch/dependability-standards/)

### ERM-P006 — Systematic failure-mode, effect and propagation challenge
A proportionate, configuration-bound adversarial analysis that links each important failure path to prevention, detection, containment, recovery or accepted residual risk.  
**Trigger:** Novel/high-consequence functions, complex interfaces, weak field history, design change, repeated incidents or uncertain propagation.  
**Cheap path:** Use a focused “what can fail and what happens next?” review for simple reversible systems; do not require a full worksheet.  
**Evidence:** [SRC-003](https://www.ntnu.edu/documents/624876/1277590549/chapt03-fmeca.pdf/ecf0c289-bc19-492f-88ef-6a197ad4a9f1), [SRC-004](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=37027), [SRC-005](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0492/), [SRC-035](https://tc56.iec.ch/dependability-standards/), [SRC-079](https://doi.org/10.1016/j.cosrev.2015.03.001)

### ERM-P008 — Common-cause, common-mode and correlated-dependency analysis
A qualitative-plus-quantitative coupling argument that states what is shared, what is separated, the evidence for residual dependence and consequences if the assumption fails.  
**Trigger:** Any redundancy, multi-region, multi-vendor, diverse implementation, backup, standby or third-party dependency claim.  
**Cheap path:** When independence cannot be supported, treat copies as one failure domain for the decision and avoid precision theatre.  
**Evidence:** [SRC-014](https://doi.org/10.1109/TSE.1986.6312924), [SRC-015](https://doi.org/10.1109/TSE.1985.231895), [SRC-052](https://www.nrc.gov/reading-rm/doc-collections/nuregs/contract/cr6268/), [SRC-053](https://ntrs.nasa.gov/api/citations/20000070463/downloads/20000070463.pdf), [SRC-055](https://doi.org/10.1016/j.ress.2006.09.004)

### ERM-P009 — Redundancy only with credible independence, coverage and switchover
A fault-tolerance claim stated as tolerated fault set × coverage × independence × transfer/state/capacity evidence, with residual common-cause risk.  
**Trigger:** N+1/N+2, TMR, replicas, active-active, hot/warm/cold standby, alternate path, multi-region or recovery-block claim.  
**Cheap path:** Prefer one simple, observable system or a manual spare when added redundancy creates more coupling than risk reduction.  
**Evidence:** [SRC-011](https://www.rand.org/pubs/papers/P817.html), [SRC-012](https://doi.org/10.1109/TSE.1975.6312842), [SRC-013](https://doi.org/10.1109/TSE.1985.231893), [SRC-023](https://ntrs.nasa.gov/api/citations/19720006837/downloads/19720006837.pdf), [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291)

### ERM-P011 — Fault detection coverage tied to required function
A coverage claim indexed by fault class, operating mode, latency and end-to-end consequence, validated independently of the monitored component.  
**Trigger:** Automatic failover, latent protective functions, remote operation, SLO alerting, PHM or any claim using “coverage.”  
**Cheap path:** A direct manual functional test may dominate elaborate monitoring for infrequent, low-cost, reversible decisions.  
**Evidence:** [SRC-024](https://doi.org/10.1016/j.arcontrol.2004.12.002), [SRC-025](https://doi.org/10.1016/j.ymssp.2005.09.012), [SRC-027](https://standards.ieee.org/ieee/1856/5844/), [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-064](https://sre.google/sre-book/monitoring-distributed-systems/)

### ERM-P014 — Graceful degradation with explicit mission priorities
A tested degradation contract specifying protected functions, sacrificed functions, consumer impact, observability, duration and exit criteria.  
**Trigger:** Capacity loss, partial dependency failure, redundancy exhaustion or missions where some function is better than none.  
**Cheap path:** Stop safely when degraded operation has no defensible acceptance criteria or adds greater consequence than interruption.  
**Evidence:** [SRC-020](https://doi.org/10.1109/TDSC.2004.2), [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-063](https://sre.google/workbook/implementing-slos/), [SRC-083](https://sre.google/sre-book/table-of-contents/)

### ERM-P016 — Recovery closes on required function and state postconditions
A recovery case with explicit preconditions, authoritative state, functional/data/dependency postconditions, independent validation and fallback.  
**Trigger:** Restart, retry, failover, rollback, restore, rebuild, repair, workaround or disaster recovery.  
**Cheap path:** For stateless, low-consequence functions, a direct end-to-end transaction after restart may be sufficient.  
**Evidence:** [SRC-012](https://doi.org/10.1109/TSE.1975.6312842), [SRC-020](https://doi.org/10.1109/TDSC.2004.2), [SRC-056](https://doi.org/10.6028/NIST.SP.800-184), [SRC-057](https://doi.org/10.6028/NIST.SP.1339), [SRC-082](https://doi.org/10.1145/844128.844132)

### ERM-P019 — Repairability and maintainability by design
Field-demonstrated restoration capability spanning detection, access, repair/replacement, configuration/state preservation, validation and return to service.  
**Trigger:** Repairable/high-value/long-life systems, remote sites, tight restoration bounds, repeated service intervention or obsolescence exposure.  
**Cheap path:** For low-cost short-life items, replacement or graceful discard may dominate elaborate repairability.  
**Evidence:** [SRC-009](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=54046), [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-031](https://tc56.iec.ch/dependability-standards/), [SRC-038](https://www.cto.mil/sea/rm/)

### ERM-P025 — Corrective-action effectiveness and recurrence control
A bounded causal claim supported by mechanism-targeted tests, deployment evidence and exposure-normalised recurrence surveillance.  
**Trigger:** Repeated incidents, fleet-wide defect, common supplier/configuration, high-severity failure or claimed reliability growth.  
**Cheap path:** For a simple deterministic defect, a regression/functional test plus configuration deployment proof may suffice.  
**Evidence:** [SRC-010](https://quicksearch.dla.mil/qsSearch.aspx?q=MIL-HDBK-2155), [SRC-048](https://doi.org/10.17226/18987), [SRC-084](https://quicksearch.dla.mil/qsSearch.aspx?q=MIL-HDBK-189C)

### ERM-P026 — Reliability demonstration with explicit confidence, population and assumptions
A decision-calibrated evidence statement: claim, denominator, configuration/profile, model/assumptions, uncertainty, coverage and expiry.  
**Trigger:** Contractual acceptance, launch/release, supplier qualification, life claim, safety/mission decision or expensive design trade-off.  
**Cheap path:** Use deterministic functional verification or a coarse bound when probability precision cannot change the decision.  
**Evidence:** [SRC-040](https://www.itl.nist.gov/div898/handbook/apr/apr.htm), [SRC-043](https://www.itl.nist.gov/div898/handbook/apr/section3/apr311.htm), [SRC-049](https://www.iapsam.org/PSAM16/papers/DA21-PSAM16.pdf), [SRC-050](https://doi.org/10.1080/08982112.2014.964413)

### ERM-P029 — Reliability evidence bound to current configuration and change
A live claim-evidence-configuration graph with explicit inheritance rationale, invalidation triggers, targeted checks and field confirmation.  
**Trigger:** Any material design, software, data/model, supplier, infrastructure, maintenance-procedure or support change.  
**Cheap path:** For a small reversible change, run a targeted functional/regression check and explicitly narrow the inherited claim.  
**Evidence:** [SRC-028](https://standards.nasa.gov/standard/NASA/NASA-STD-87291), [SRC-033](https://tc56.iec.ch/dependability-standards/), [SRC-038](https://www.cto.mil/sea/rm/), [SRC-061](https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/)

### ERM-P031 — User-journey and consumer-consequence service reliability
A small set of end-to-end, cohort-aware, consequence-linked measures with diagnostic drill-down and explicit blind spots.  
**Trigger:** Externally consumed software/service whose important outcomes span components, dependencies or multiple steps.  
**Cheap path:** For simple single-step services, one end-to-end functional probe plus incident review may be sufficient.  
**Evidence:** [SRC-063](https://sre.google/workbook/implementing-slos/), [SRC-064](https://sre.google/sre-book/monitoring-distributed-systems/), [SRC-083](https://sre.google/sre-book/table-of-contents/)

## Common caricatures and ceremonies to reject

- MTBF presented as the universal meaning of reliability.
- “Five nines” without a named consumer, indicator, denominator, window and exclusions.
- A completed FMEA/FMECA worksheet presented as proof that modes are controlled.
- A redundancy diagram or copy count presented as independence evidence.
- A green component health check presented as end-to-end functional availability.
- Backup completion presented as restoration capability.
- A single failover/game-day/chaos exercise presented as general resilience proof.
- An incident-count or growth-curve trend presented as causal reliability improvement.
- Predictive-maintenance or AI branding presented as net dependability evidence.

## Important criticisms and limits

- **CR-01 — MTBF used without a defined mission/process or with an untested constant-hazard assumption.** Later disposition: `REFINED`; mature response: Retain means only as one statistic; require failure process, interval/demand and tails. Sources: SRC-040, SRC-043, SRC-046.
- **CR-02 — The bathtub curve is overgeneralised from selected populations and mechanisms.** Later disposition: `NARROWED`; mature response: Use mechanism- and population-specific hazard evidence; mixtures and maintenance are explicit. Sources: SRC-008, SRC-041, SRC-046.
- **CR-03 — Handbook part-count/stress prediction is treated as field truth despite input/model uncertainty.** Later disposition: `REPLACED`; mature response: Use as conditional comparative input at most; calibrate with test and field evidence. Sources: SRC-039, SRC-047, SRC-048.
- **CR-04 — FMEA becomes a worksheet/checklist with subjective ranks and no verified control closure.** Later disposition: `REFINED`; mature response: Retain systematic failure challenge; strip the mandatory form and link modes to evidence. Sources: SRC-004, SRC-035, SRC-079.
- **CR-05 — FTA completeness and quantification inherit top-event, boundary and independence omissions.** Later disposition: `REFINED`; mature response: Use explicit ground rules, common-cause events, dynamic analysis and empirical challenge. Sources: SRC-005, SRC-052, SRC-053, SRC-079.
- **CR-06 — Common-cause failures defeat nominally redundant channels.** Later disposition: `GENERALIZED`; mature response: Count failure domains and shared causes; qualify redundancy benefit conditionally. Sources: SRC-052, SRC-054, SRC-055.
- **CR-07 — Standby/switchover is latent-bad, too slow, capacity-deficient or state-incompatible.** Later disposition: `REFINED`; mature response: Treat takeover as a complete diagnostic/state/capacity recovery path. Sources: SRC-028, SRC-056, SRC-058–SRC-060.
- **CR-08 — N-version software failures are correlated despite independent teams.** Later disposition: `NARROWED`; mature response: Diversity is only conditional common-mode mitigation with empirical independence evidence. Sources: SRC-013–SRC-015.
- **CR-09 — Alarm/health status is substituted for fault isolation or end-function truth.** Later disposition: `GENERALIZED`; mature response: Separate detection, diagnosis, recovery coverage and independent functional checks. Sources: SRC-024–SRC-027, SRC-064.
- **CR-10 — Scheduled preventive maintenance is applied without age relation and can induce failure.** Later disposition: `NARROWED`; mature response: Use age-based work only with a valid age mechanism and net consequence benefit. Sources: SRC-008, SRC-076, SRC-077.
- **CR-11 — Predictive maintenance overclaims transfer, RUL precision and universal superiority.** Later disposition: `DOMAIN_SPECIFIC`; mature response: Require observable precursor, calibrated uncertainty, actionable lead time and comparison with simpler policies. Sources: SRC-025, SRC-026, SRC-071, SRC-072.
- **CR-12 — Growth curves are fitted after selected fixes and interpreted causally.** Later disposition: `REFINED`; mature response: Retain trend models but require prospective fixes, stable exposure and recurrence evidence. Sources: SRC-006, SRC-007, SRC-048, SRC-084.

## How the tradition evolved under criticism

The strongest evolution was not “more prediction” or “more redundancy.” Component means were narrowed by mission semantics, hazard-shape and repair-process distinctions. Redundancy was conditioned on common cause, coverage, state and capacity. Failure prevention was expanded to detection, containment, acceptable degradation, repair and validated recovery. Maintenance schedules were narrowed by failure mechanism and consequence. Prediction and growth models were subordinated to uncertainty, field calibration, configuration identity and corrective-action recurrence. Service objectives and chaos experiments were retained only as scoped decision instruments.

## Citation-ready factual claims

- **PUB-C01.** Weibull’s 1951 distribution permits different hazard shapes; fitting it does not by itself identify a physical mechanism. Sources: [SRC-001](https://doi.org/10.1115/1.4010337)
- **PUB-C02.** The 1957 AGREE report is a key institutional marker in U.S. military-electronics reliability engineering. Sources: [SRC-002](https://catalog.hathitrust.org/Search/Home?lookfor=%22Reliability%20of%20Military%20Electronic%20Equipment%22&type=title)
- **PUB-C03.** MIL-STD-1629A defines FMECA procedures but its worksheet completion is not evidence that identified controls work. Sources: [SRC-004](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=37027)
- **PUB-C04.** Fault-tree results are conditional on the chosen top event, system boundary, event definitions and dependence assumptions. Sources: [SRC-005](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0492/), [SRC-053](https://ntrs.nasa.gov/api/citations/20000070463/downloads/20000070463.pdf), [SRC-079](https://doi.org/10.1016/j.cosrev.2015.03.001)
- **PUB-C05.** Nowlan and Heap documented multiple age–reliability patterns and conditioned scheduled maintenance on failure behaviour and consequence. Sources: [SRC-008](https://apps.dtic.mil/sti/pdfs/ADA066579.pdf)
- **PUB-C06.** Mathematical redundancy can improve reliability under specified stochastic assumptions; shared causes can defeat that benefit. Sources: [SRC-011](https://www.rand.org/pubs/papers/P817.html), [SRC-052](https://www.nrc.gov/reading-rm/doc-collections/nuregs/contract/cr6268/), [SRC-054](https://ntrs.nasa.gov/citations/20240013667)
- **PUB-C07.** Independent software-development teams do not guarantee independent version failures. Sources: [SRC-013](https://doi.org/10.1109/TSE.1985.231893), [SRC-014](https://doi.org/10.1109/TSE.1986.6312924), [SRC-015](https://doi.org/10.1109/TSE.1985.231895)
- **PUB-C08.** Dependability taxonomies distinguish faults, errors and failures and preserve reliability, availability and maintainability as related but non-identical attributes. Sources: [SRC-020](https://doi.org/10.1109/TDSC.2004.2)
- **PUB-C09.** Current IEC guidance defines dependability management around justified confidence that an item will perform as and when required. Sources: [SRC-030](https://tc56.iec.ch/dependability-standards/)
- **PUB-C10.** Maintainability and supportability require design and organisational/logistics capability, not merely a low active repair-time estimate. Sources: [SRC-009](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=54046), [SRC-031](https://tc56.iec.ch/dependability-standards/), [SRC-032](https://tc56.iec.ch/dependability-standards/)
- **PUB-C11.** Constant-rate/exponential MTBF inference is a model choice, not a universal law of product life. Sources: [SRC-040](https://www.itl.nist.gov/div898/handbook/apr/apr.htm), [SRC-043](https://www.itl.nist.gov/div898/handbook/apr/section3/apr311.htm), [SRC-046](https://doi.org/10.1109/TR.2002.804492)
- **PUB-C12.** Zero observed failures can support a bounded reliability statement under declared assumptions, but not zero failure probability or an identified lifetime distribution. Sources: [SRC-049](https://www.iapsam.org/PSAM16/papers/DA21-PSAM16.pdf), [SRC-050](https://doi.org/10.1080/08982112.2014.964413)
- **PUB-C13.** Recovery guidance requires realistic exercises and validation of restored systems/data, not only backup creation or service restart. Sources: [SRC-056](https://doi.org/10.6028/NIST.SP.800-184), [SRC-057](https://doi.org/10.6028/NIST.SP.1339)
- **PUB-C14.** Major AWS, Meta, GitLab and CrowdStrike events demonstrate the reliability importance of shared dependencies, control paths, recovery sources and correlated change. Sources: [SRC-058](https://aws.amazon.com/message/41926/), [SRC-059](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/), [SRC-060](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/), [SRC-061](https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/), [SRC-062](https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/)
- **PUB-C15.** SLIs/SLOs and error budgets can govern service decisions, but adoption and indicator validity are organisational and measurement problems rather than automatic reliability proof. Sources: [SRC-063](https://sre.google/workbook/implementing-slos/), [SRC-065](https://sre.google/workbook/error-budget-policy/), [SRC-066](https://www.usenix.org/publications/loginonline/what-sre-could-be), [SRC-067](https://www.usenix.org/conference/srecon23americas/presentation/goins)
- **PUB-C16.** Chaos engineering contributes evidence only for bounded hypotheses, faults, configurations and decision contexts. Sources: [SRC-068](https://doi.org/10.1109/MS.2016.60), [SRC-069](https://principlesofchaos.org/), [SRC-070](https://doi.org/10.1145/3777375)
- **PUB-C17.** Recent PHM/RUL reviews continue to identify uncertainty, transferability and decision-integration burdens. Sources: [SRC-071](https://doi.org/10.7717/peerj-cs.1943), [SRC-072](https://doi.org/10.1016/j.ress.2025.112110)
- **PUB-C18.** Current AI/autonomy assurance sources treat postdeployment monitoring, coverage, uncertainty and authority as live challenges, not solved general reliability properties. Sources: [SRC-074](https://doi.org/10.6028/NIST.AI.800-4), [SRC-075](https://doi.org/10.1109/TR.2024.3366814)

## Evidence limits and claims not to make

- Do not claim that one lifetime distribution, hazard shape, prediction handbook or RBD/FTA/FMEA method is generally sufficient.
- Do not convert a model fit, standard-compliant artefact, tool output, zero-failure test or successful demonstration into a field-reliability claim without its assumptions and scope.
- Do not claim redundancy benefit without failure-domain, common-cause, coverage, state, capacity and switchover evidence.
- Do not call a restart, ticket closure, backup copy or failover control event “recovery” until required function and authoritative state are validated.
- Do not present SRE as the final form of reliability engineering; it is a software/service translation with useful mechanisms and distinct limits.
- Do not claim predictive maintenance universally outperforms age-based, inspection or run-to-failure policies.
- Do not claim AI/ML/agentic automation is a general reliability property; current evidence is use-case-specific and assurance burdens remain active.
- Do not infer documentary transmission from conceptual similarity; several lineages converged independently or through shared engineering problems.

## Direct lineage, convergence and domain translation

| Relationship | Public explanation |
|---|---|
| `RELIABILITY_ENGINEERING_NATIVE` | Mission reliability, life/failure evidence, failure analysis and growth are direct reliability lineages. |
| `MAINTAINABILITY_NATIVE` | Access, testability, repair-time distribution, support resources and maintenance capability form a distinct native lineage. |
| `STATISTICAL_RELIABILITY_ANCESTRY` | Lifetime, renewal, recurrent-event and demonstration methods supply conditional evidence—not engineering meaning by themselves. |
| `FAULT_TOLERANCE_IMPORT_OR_SHARED_ANCESTRY` | Redundancy, containment, diversity and rollback translate reliability objectives into computing structures. |
| `SERVICE_RELIABILITY_TRANSLATION` | SLOs, observability, on-call and error budgets translate selected properties into software-service operations. |
| `CONVERGENT_PROPERTY` | Required function, explicit assumptions, configuration freshness and end-to-end validation recur across lineages; similarity alone does not prove historical transmission. |
| `DOMAIN_TRANSLATION` | Aviation human factors, OT recovery and AI/autonomy add domain-specific constraints and cannot be universalised without evidence. |

## Current state and frontier notes

- Current authoritative practice is objectives- and lifecycle-oriented rather than a single handbook calculation: required performance, maintainability, supportability, field data and evidence all remain explicit.
- Common-cause and dependency failure remain central because modern systems share power, networks, control planes, state, suppliers, tooling, operators and change channels.
- Recovery engineering is moving from backup/restart language toward reconstitution, state validation, dependency readiness and recurring realistic exercises.
- Service-reliability practice is moving from aggregate uptime toward important journeys, cohorts, burn rates and action policies, while adoption and proxy gaming remain material limitations.
- PHM and predictive maintenance continue to advance, but RUL uncertainty, transfer, sensor drift, false actions and comparison with simpler policies prevent a universal superiority claim.
- AI/agentic operations remain an emerging domain translation. Net dependability requires bounded authority, calibrated uncertainty, postdeployment monitoring, reversible action, independent functional checks and fallback.

## Suggested public page outline

1. What reliability and maintainability do—and do not—mean
2. The plural historical lineages
3. Required function, mission, profile and failure semantics
4. Reliability, availability, maintainability and supportability
5. Failure propagation, common cause and conditional redundancy
6. Detection, diagnosis, degradation and recovery
7. Maintainability and maintenance policy
8. Reliability growth, demonstration and evidence freshness
9. Software/service reliability, SLOs and chaos engineering
10. Ceremonies, proxy failure and field lessons
11. Strongest surviving properties and cheap paths
12. Current frontier and unresolved questions

## Public-intake receipt

- `PUBLIC_DOCUMENTATION_INTAKE`: `COMPLETE`
- `SOURCE_GROUNDED`: `YES`
- `PROPERTY_COUNT_FEATURED`: `15`
- `CITATION_READY_CLAIM_COUNT`: `18`
- `HYPE_BOUNDARIES_EXPLICIT`: `YES`
