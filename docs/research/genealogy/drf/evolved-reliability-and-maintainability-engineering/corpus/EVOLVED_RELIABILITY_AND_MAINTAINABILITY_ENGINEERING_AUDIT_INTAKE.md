# EVOLVED_RELIABILITY_AND_MAINTAINABILITY_ENGINEERING_AUDIT_INTAKE

**State:** `FROZEN`  
**Run date:** `2026-08-12`  
**Population:** 55 examined / 55 frozen; 40 crosswalk-worthy retained/evolved/contextual properties; 15 rejected, ceremonial, superseded or domain-bounded candidates.**

## Intake boundary

This intake transfers external engineering questions, preconditions and evidence burdens. It does not inspect, score or answer questions about any target. Every `QUESTIONS_FOR_REPOSITORY_AUDIT` entry remains a question for a later, separate audit.

The denominator includes negative candidates so that an audit cannot silently resurrect MTBF slogans, five-nines branding, worksheet completion, backup existence, one-off failover, incident counts, green health checks, unbound chaos exercises, universal redundancy, universal predictive maintenance, curve-only growth, zero-failure overclaim or unbounded AI/agentic automation.

## Standard population/source fields

| Field | Frozen value |
|---|---|
| Analytical label | `EVOLVED_RELIABILITY_AND_MAINTAINABILITY_ENGINEERING` |
| Research state | `FROZEN` |
| Property population total/examined | `55 / 55` |
| Crosswalk-worthy properties | `40` |
| Bounded negative/domain candidates | `15` |
| Source population | `85` exact source records |
| Evidence rule | Mathematical/model validity is separated from representative field or mission performance. |
| Informational independence | No target repository or sibling frozen packet was inspected or used. |

## Crosswalk-worthy property intake

<details><summary><strong>ERM-P001 — Explicit required-function and mission semantics</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The named system or service function must meet specified performance, timing, state and consequence criteria for the declared consumer.
- `failure_mode`: Failure is non-performance, untimely performance, erroneous performance or performance below the declared threshold—not merely component death.
**MATURE_FORM**  
A testable, versioned mission contract that binds required function, mode, profile, environment, interval/demand, degraded acceptance and consumer consequence.

**TRIGGER**  
Any reliability, availability, demonstration, redundancy, recovery or service-level claim that could drive design, release, maintenance or acceptance.

**CHEAP_PATH**  
For low-consequence reversible work, use a direct pass/fail functional check and a short observation window rather than a probabilistic programme.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Explicit required-function and mission semantics
- `REQUIRED_FUNCTION`: The named system or service function must meet specified performance, timing, state and consequence criteria for the declared consumer.
- `MISSION_OR_SERVICE`: The named system or service function must meet specified performance, timing, state and consequence criteria for the declared consumer.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Failure is non-performance, untimely performance, erroneous performance or performance below the declared threshold—not merely component death.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Mission owner, service consumer, operator, maintainer, acceptance authority or risk decision-maker.
- `CHEAP_PATH`: For low-consequence reversible work, use a direct pass/fail functional check and a short observation window rather than a probabilistic programme.
- `MATURE_FORM`: A testable, versioned mission contract that binds required function, mode, profile, environment, interval/demand, degraded acceptance and consumer consequence.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Stakeholder/consumer criteria, mission phases, state authority, measurable outputs and an agreed scoring rule.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `LOW_TO_MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `LOW`

**CRITICISMS**  
Requirements can be bureaucratic or falsely precise; rare severe consequences can be hidden by an average success definition.

**ANTI_CEREMONY_BOUNDARY**  
A reliability requirement template is optional; the property is semantic closure on what success and failure mean.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate explicit required-function and mission semantics?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?

</details>
<details><summary><strong>ERM-P002 — Operational-profile, environment and demand definition</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The function in ERM-P001 under the actual or deliberately bounded distribution of demands and conditions.
- `failure_mode`: Evidence or design appears reliable under a convenient profile but fails under real frequency, severity, mode transition or rare consequence-important demand.
**MATURE_FORM**  
A configuration-bound, uncertainty-labelled exposure model that supports both representative sampling and explicit stress/boundary cases.

**TRIGGER**  
Prediction, demonstration, accelerated testing, software testing, SLO definition, capacity planning, maintenance policy or field-transfer claim.

**CHEAP_PATH**  
Use a small set of bounding scenarios when a full probability distribution would not change the decision.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Operational-profile, environment and demand definition
- `REQUIRED_FUNCTION`: The function in ERM-P001 under the actual or deliberately bounded distribution of demands and conditions.
- `MISSION_OR_SERVICE`: The function in ERM-P001 under the actual or deliberately bounded distribution of demands and conditions.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Evidence or design appears reliable under a convenient profile but fails under real frequency, severity, mode transition or rare consequence-important demand.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Test planner, reliability analyst, service owner, maintainer, release authority and mission decision-maker.
- `CHEAP_PATH`: Use a small set of bounding scenarios when a full probability distribution would not change the decision.
- `MATURE_FORM`: A configuration-bound, uncertainty-labelled exposure model that supports both representative sampling and explicit stress/boundary cases.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Operational-profile, environment and demand definition
- `CLAIM`: A configuration-bound, uncertainty-labelled exposure model that supports both representative sampling and explicit stress/boundary cases.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Test planner, reliability analyst, service owner, maintainer, release authority and mission decision-maker.
- `CHEAP_PATH`: Use a small set of bounding scenarios when a full probability distribution would not change the decision.
- `CONTRARY_EVIDENCE`: No fixed profile remains valid after material product, dependency, user or mission change.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A configuration-bound, uncertainty-labelled exposure model that supports both representative sampling and explicit stress/boundary cases.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Telemetry or credible mission analysis, stable definitions, sampling weights and explicit treatment of rare high-consequence demands.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Profiles can encode current behaviour and suppress novel uses; high-consequence rare events may deserve more weight than frequency implies.

**ANTI_CEREMONY_BOUNDARY**  
A workload spreadsheet is optional; the property is evidence about where, how often and under what conditions function is demanded.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate operational-profile, environment and demand definition?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P003 — Explicit complete, partial, intermittent, latent and degraded failure states</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Required function and quality thresholds for each operating mode, including which reduced capabilities remain acceptable and for how long.
- `failure_mode`: A harmful state is classified as “up,” or an acceptable degraded state is counted as complete failure, corrupting decisions and metrics.
**MATURE_FORM**  
A minimal consequence-relevant state model with explicit observation, entry/exit criteria, allowed duration and treatment of latent states.

**TRIGGER**  
Systems with multiple modes, redundancy, standby, partial service, performance thresholds, intermittent faults or hidden protective functions.

**CHEAP_PATH**  
A binary state is sufficient only when the consumer consequence is genuinely binary and the observation tests the complete function.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Explicit complete, partial, intermittent, latent and degraded failure states
- `REQUIRED_FUNCTION`: Required function and quality thresholds for each operating mode, including which reduced capabilities remain acceptable and for how long.
- `MISSION_OR_SERVICE`: Required function and quality thresholds for each operating mode, including which reduced capabilities remain acceptable and for how long.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: A harmful state is classified as “up,” or an acceptable degraded state is counted as complete failure, corrupting decisions and metrics.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Operator, mission owner, service consumer, model builder and incident reviewer.
- `CHEAP_PATH`: A binary state is sufficient only when the consumer consequence is genuinely binary and the observation tests the complete function.
- `MATURE_FORM`: A minimal consequence-relevant state model with explicit observation, entry/exit criteria, allowed duration and treatment of latent states.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Explicit complete, partial, intermittent, latent and degraded failure states
- `INITIATING_FAULT_OR_FAILURE`: A harmful state is classified as “up,” or an acceptable degraded state is counted as complete failure, corrupting decisions and metrics.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: A harmful state is classified as “up,” or an acceptable degraded state is counted as complete failure, corrupting decisions and metrics.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: State observability, mission criteria, transition rules, timing and authority for accepting/ending degradation.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Define state space, observable criteria, transitions, dwell limits, latent conditions, false indications and consumer consequences.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: State observability, mission criteria, transition rules, timing and authority for accepting/ending degradation.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Multi-state models can create false precision and obscure simpler decisive thresholds.

**ANTI_CEREMONY_BOUNDARY**  
A state diagram is optional; the property is unambiguous classification of the states that matter to the mission.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate explicit complete, partial, intermittent, latent and degraded failure states?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?

</details>
<details><summary><strong>ERM-P004 — System boundary and failure-attribution discipline</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The end-to-end function across all components, services, people and support resources inside the declared responsibility/decision boundary.
- `failure_mode`: A mission failure is omitted, double-counted or assigned to an external party so that no owner sees the actual system risk.
**MATURE_FORM**  
A layered boundary model: end-to-end consequence for reliability claims, plus component/dependency attribution for corrective action.

**TRIGGER**  
RBD/FTA/FMEA, SLA/SLO, supplier reliability, incident metrics, field-return analysis or cross-organisation service paths.

**CHEAP_PATH**  
For a local reversible decision, state a narrow boundary explicitly and avoid claiming end-to-end reliability.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: System boundary and failure-attribution discipline
- `REQUIRED_FUNCTION`: The end-to-end function across all components, services, people and support resources inside the declared responsibility/decision boundary.
- `MISSION_OR_SERVICE`: The end-to-end function across all components, services, people and support resources inside the declared responsibility/decision boundary.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: A mission failure is omitted, double-counted or assigned to an external party so that no owner sees the actual system risk.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: System owner, supplier manager, SRE/service owner, maintainer and acceptance authority.
- `CHEAP_PATH`: For a local reversible decision, state a narrow boundary explicitly and avoid claiming end-to-end reliability.
- `MATURE_FORM`: A layered boundary model: end-to-end consequence for reliability claims, plus component/dependency attribution for corrective action.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: System boundary and failure-attribution discipline
- `INITIATING_FAULT_OR_FAILURE`: A mission failure is omitted, double-counted or assigned to an external party so that no owner sees the actual system risk.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: A mission failure is omitted, double-counted or assigned to an external party so that no owner sees the actual system risk.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Dependency inventory, interface contracts, event correlation, shared clocks/identifiers and adjudication rules.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Declare analysis boundary, inclusions/exclusions, interfaces, responsibility versus causal attribution, denominator and disputed cases.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Dependency inventory, interface contracts, event correlation, shared clocks/identifiers and adjudication rules.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Very broad boundaries make measurement and accountability difficult; too-narrow boundaries make claims irrelevant.

**ANTI_CEREMONY_BOUNDARY**  
A service map or fault tree is optional; the property is stable scope and transparent exclusions.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate system boundary and failure-attribution discipline?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?

</details>
<details><summary><strong>ERM-P005 — Separate reliability, availability, maintainability, supportability and durability claims</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: A declared mission interval and restoration/support conditions for the item or service.
- `failure_mode`: A decision substitutes one RAM measure for another and accepts the wrong failure frequency, downtime, repair burden or life limitation.
**MATURE_FORM**  
A small RAM measure set tied to explicit functions, state transitions, total downtime components and decision thresholds.

**TRIGGER**  
Any claim using reliability, uptime, availability, MTBF, MTTR, serviceability, durability or operational readiness.

**CHEAP_PATH**  
Use direct failure count and downtime decomposition when a full stochastic model is unnecessary; never collapse the labels.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Separate reliability, availability, maintainability, supportability and durability claims
- `REQUIRED_FUNCTION`: A declared mission interval and restoration/support conditions for the item or service.
- `MISSION_OR_SERVICE`: A declared mission interval and restoration/support conditions for the item or service.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: A decision substitutes one RAM measure for another and accepts the wrong failure frequency, downtime, repair burden or life limitation.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Mission planner, operator, maintenance/logistics owner, procurement and service consumer.
- `CHEAP_PATH`: Use direct failure count and downtime decomposition when a full stochastic model is unnecessary; never collapse the labels.
- `MATURE_FORM`: A small RAM measure set tied to explicit functions, state transitions, total downtime components and decision thresholds.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Separate reliability, availability, maintainability, supportability and durability claims
- `CLAIM`: A small RAM measure set tied to explicit functions, state transitions, total downtime components and decision thresholds.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Mission planner, operator, maintenance/logistics owner, procurement and service consumer.
- `CHEAP_PATH`: Use direct failure count and downtime decomposition when a full stochastic model is unnecessary; never collapse the labels.
- `CONTRARY_EVIDENCE`: No universal composite “reliability score” preserves all RAM trade-offs.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A small RAM measure set tied to explicit functions, state transitions, total downtime components and decision thresholds.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Consistent clocks, failure/restoration definitions, exposure, repair-completion criteria and support-delay data.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
The vocabulary can become metric-heavy; definitions still need mission consequence and state validity.

**ANTI_CEREMONY_BOUNDARY**  
A RAM dashboard is optional; the property is semantic and denominator integrity across distinct attributes.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate separate reliability, availability, maintainability, supportability and durability claims?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P006 — Systematic failure-mode, effect and propagation challenge</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The function and boundary defined by ERM-P001–P004.
- `failure_mode`: A plausible mode or propagation path remains uncontrolled because analysis stopped at a component label or single failure.
**MATURE_FORM**  
A proportionate, configuration-bound adversarial analysis that links each important failure path to prevention, detection, containment, recovery or accepted residual risk.

**TRIGGER**  
Novel/high-consequence functions, complex interfaces, weak field history, design change, repeated incidents or uncertain propagation.

**CHEAP_PATH**  
Use a focused “what can fail and what happens next?” review for simple reversible systems; do not require a full worksheet.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Systematic failure-mode, effect and propagation challenge
- `INITIATING_FAULT_OR_FAILURE`: A plausible mode or propagation path remains uncontrolled because analysis stopped at a component label or single failure.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: A plausible mode or propagation path remains uncontrolled because analysis stopped at a component label or single failure.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Current architecture/configuration, knowledgeable cross-functional participants, explicit ground rules and closure evidence.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Challenge functions and interfaces with plausible modes; trace local-to-end effects, controls, detectability, combinations and evidence for treatment.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Current architecture/configuration, knowledgeable cross-functional participants, explicit ground rules and closure evidence.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Bottom-up FMEA can miss interactions and multiple failures; FTA can inherit an incomplete top event and independence assumptions.

**ANTI_CEREMONY_BOUNDARY**  
The FMEA/FMECA table is not the property; systematic challenge and verified closure are.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate systematic failure-mode, effect and propagation challenge?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?

</details>
<details><summary><strong>ERM-P007 — Single-point and latent-failure exposure control</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Specified fault tolerance or degraded mission capability under the declared initiating fault set.
- `failure_mode`: One fault, or one fault plus an undetected latent condition, defeats required function.
**MATURE_FORM**  
Explicit minimal failure sets including latent states, with elimination or tested detection/repair intervals matched to consequence.

**TRIGGER**  
Redundancy, standby, protective functions, emergency equipment, rarely demanded recovery paths and maintenance bypasses.

**CHEAP_PATH**  
For simple systems, trace the end-to-end path once and directly exercise the spare/protective function rather than build a full quantitative tree.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Single-point and latent-failure exposure control
- `INITIATING_FAULT_OR_FAILURE`: One fault, or one fault plus an undetected latent condition, defeats required function.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: One fault, or one fault plus an undetected latent condition, defeats required function.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Complete boundary, realistic initial state, demand rate, proof-test interval, detection coverage and restoration plan.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Identify cut sets and latent protective failures; eliminate, isolate, monitor or periodically proof-test them; bound exposure time.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Single-point and latent-failure exposure control
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: Explicit minimal failure sets including latent states, with elimination or tested detection/repair intervals matched to consequence.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Single-point and latent-failure exposure control
- `TARGET_FAULTS_FAILURES`: One fault, or one fault plus an undetected latent condition, defeats required function.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: Explicit minimal failure sets including latent states, with elimination or tested detection/repair intervals matched to consequence.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Complete boundary, realistic initial state, demand rate, proof-test interval, detection coverage and restoration plan.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
“Single failure” focus can distract from correlated multi-fault and systemic conditions.

**ANTI_CEREMONY_BOUNDARY**  
A critical-items list is optional; the property is actual removal or bounded exposure of decisive failure sets.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate single-point and latent-failure exposure control?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?

</details>
<details><summary><strong>ERM-P008 — Common-cause, common-mode and correlated-dependency analysis</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Continued or degraded required function after the claimed fault set.
- `failure_mode`: Several “independent” elements fail together or sequentially from a shared coupling, invalidating the parallel reliability calculation.
**MATURE_FORM**  
A qualitative-plus-quantitative coupling argument that states what is shared, what is separated, the evidence for residual dependence and consequences if the assumption fails.

**TRIGGER**  
Any redundancy, multi-region, multi-vendor, diverse implementation, backup, standby or third-party dependency claim.

**CHEAP_PATH**  
When independence cannot be supported, treat copies as one failure domain for the decision and avoid precision theatre.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Common-cause, common-mode and correlated-dependency analysis
- `REQUIRED_FUNCTION`: Continued or degraded required function after the claimed fault set.
- `MISSION_OR_SERVICE`: Continued or degraded required function after the claimed fault set.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Several “independent” elements fail together or sequentially from a shared coupling, invalidating the parallel reliability calculation.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Architect, reliability modeller, service owner, procurement/supplier manager and mission-risk authority.
- `CHEAP_PATH`: When independence cannot be supported, treat copies as one failure domain for the decision and avoid precision theatre.
- `MATURE_FORM`: A qualitative-plus-quantitative coupling argument that states what is shared, what is separated, the evidence for residual dependence and consequences if the assumption fails.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Common-cause, common-mode and correlated-dependency analysis
- `INITIATING_FAULT_OR_FAILURE`: Several “independent” elements fail together or sequentially from a shared coupling, invalidating the parallel reliability calculation.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Several “independent” elements fail together or sequentially from a shared coupling, invalidating the parallel reliability calculation.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Architecture/dependency visibility, configuration/supplier data, incident linkage and credible dependence parameters or conservative bounds.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Enumerate failure domains and coupling factors; seek empirical CCF data; model dependence; separate shared controls; test correlated scenarios; reduce concentration.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Common-cause, common-mode and correlated-dependency analysis
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: A qualitative-plus-quantitative coupling argument that states what is shared, what is separated, the evidence for residual dependence and consequences if the assumption fails.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Architecture/dependency visibility, configuration/supplier data, incident linkage and credible dependence parameters or conservative bounds.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE_TO_HIGH`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
CCF parameters are uncertain and domain-specific; pessimistic bounding can erase economically useful redundancy.

**ANTI_CEREMONY_BOUNDARY**  
A “multi-AZ” label or beta-factor entry is not the property; credible domain separation and dependence evidence are.

**POSSIBLE_CONFLICTING_PROPERTY**  
Redundancy versus added complexity, correlated dependency and common-cause exposure.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate common-cause, common-mode and correlated-dependency analysis?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?

</details>
<details><summary><strong>ERM-P009 — Redundancy only with credible independence, coverage and switchover</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Full or declared degraded mission function after the fault class and within the transfer deadline.
- `failure_mode`: Both paths fail together, the spare is latent-bad, switchover does not occur, transfer corrupts state, capacity is insufficient or adjudication selects the wrong output.
**MATURE_FORM**  
A fault-tolerance claim stated as tolerated fault set × coverage × independence × transfer/state/capacity evidence, with residual common-cause risk.

**TRIGGER**  
N+1/N+2, TMR, replicas, active-active, hot/warm/cold standby, alternate path, multi-region or recovery-block claim.

**CHEAP_PATH**  
Prefer one simple, observable system or a manual spare when added redundancy creates more coupling than risk reduction.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Redundancy only with credible independence, coverage and switchover
- `REQUIRED_FUNCTION`: Full or declared degraded mission function after the fault class and within the transfer deadline.
- `MISSION_OR_SERVICE`: Full or declared degraded mission function after the fault class and within the transfer deadline.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Both paths fail together, the spare is latent-bad, switchover does not occur, transfer corrupts state, capacity is insufficient or adjudication selects the wrong output.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Architect, operator, mission owner and acceptance authority.
- `CHEAP_PATH`: Prefer one simple, observable system or a manual spare when added redundancy creates more coupling than risk reduction.
- `MATURE_FORM`: A fault-tolerance claim stated as tolerated fault set × coverage × independence × transfer/state/capacity evidence, with residual common-cause risk.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Redundancy only with credible independence, coverage and switchover
- `INITIATING_FAULT_OR_FAILURE`: Both paths fail together, the spare is latent-bad, switchover does not occur, transfer corrupts state, capacity is insufficient or adjudication selects the wrong output.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Both paths fail together, the spare is latent-bad, switchover does not occur, transfer corrupts state, capacity is insufficient or adjudication selects the wrong output.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: ERM-P008 common-cause analysis, diagnostic coverage, switchover reliability, compatible state, spare capacity and maintainable configuration.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Specify tolerated faults; isolate domains; monitor standby; validate detection/decision/transfer/state/capacity; test under representative load and failed-control conditions.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Redundancy only with credible independence, coverage and switchover
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: A fault-tolerance claim stated as tolerated fault set × coverage × independence × transfer/state/capacity evidence, with residual common-cause risk.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Redundancy only with credible independence, coverage and switchover
- `INITIATING_FAILURE`: Both paths fail together, the spare is latent-bad, switchover does not occur, transfer corrupts state, capacity is insufficient or adjudication selects the wrong output.
- `RECOVERY_ACTION`: Specify tolerated faults; isolate domains; monitor standby; validate detection/decision/transfer/state/capacity; test under representative load and failed-control conditions.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Full or declared degraded mission function after the fault class and within the transfer deadline.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A fault-tolerance claim stated as tolerated fault set × coverage × independence × transfer/state/capacity evidence, with residual common-cause risk.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: ERM-P008 common-cause analysis, diagnostic coverage, switchover reliability, compatible state, spare capacity and maintainable configuration.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `VERY_HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
Redundancy adds components, interfaces, operational modes and maintenance burden; diversity can impair maintainability.

**ANTI_CEREMONY_BOUNDARY**  
A redundancy diagram is optional; the property is an evidenced alternate path that actually assumes the mission.

**POSSIBLE_CONFLICTING_PROPERTY**  
Availability gain versus switchover/state-synchronisation complexity.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate redundancy only with credible independence, coverage and switchover?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P010 — Fault containment regions and propagation barriers</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Critical function remains available, degrades within criteria or can be restored without contamination beyond the region.
- `failure_mode`: Shared state, control, resource pools, retries, maintenance or deployment bypass the intended boundary.
**MATURE_FORM**  
A tested containment argument covering state, control, resources, dependencies, maintenance and recovery—not merely data-plane topology.

**TRIGGER**  
High fan-out dependencies, untrusted/rapid changes, fault tolerance, multi-tenant resources, recovery sources and high-consequence functions.

**CHEAP_PATH**  
Use simple rate limits, manual change gates or one-way isolation when full cell architecture is disproportionate.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Fault containment regions and propagation barriers
- `INITIATING_FAULT_OR_FAILURE`: Shared state, control, resource pools, retries, maintenance or deployment bypass the intended boundary.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Shared state, control, resource pools, retries, maintenance or deployment bypass the intended boundary.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Known propagation mechanisms, independent controls, observability at boundaries and recovery capacity outside the failed region.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Partition state/resources/control; enforce quotas and circuit boundaries; stage deployment; isolate maintenance; define escape paths; test boundary breach.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Fault containment regions and propagation barriers
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: A tested containment argument covering state, control, resources, dependencies, maintenance and recovery—not merely data-plane topology.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Fault containment regions and propagation barriers
- `INITIATING_FAILURE`: Shared state, control, resource pools, retries, maintenance or deployment bypass the intended boundary.
- `RECOVERY_ACTION`: Partition state/resources/control; enforce quotas and circuit boundaries; stage deployment; isolate maintenance; define escape paths; test boundary breach.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Critical function remains available, degrades within criteria or can be restored without contamination beyond the region.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A tested containment argument covering state, control, resources, dependencies, maintenance and recovery—not merely data-plane topology.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Known propagation mechanisms, independent controls, observability at boundaries and recovery capacity outside the failed region.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Partitioning increases cost, consistency and operational complexity; false isolation can hide accumulating latent faults.

**ANTI_CEREMONY_BOUNDARY**  
A cell diagram or “bulkhead” label is optional; the property is measured containment of specified propagation.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate fault containment regions and propagation barriers?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P011 — Fault detection coverage tied to required function</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Timely recognition that the required function or a protective/recovery path has entered a defined failed/degraded state.
- `failure_mode`: A green component signal coexists with broken end-to-end function, or the target fault is outside the monitor’s coverage.
**MATURE_FORM**  
A coverage claim indexed by fault class, operating mode, latency and end-to-end consequence, validated independently of the monitored component.

**TRIGGER**  
Automatic failover, latent protective functions, remote operation, SLO alerting, PHM or any claim using “coverage.”

**CHEAP_PATH**  
A direct manual functional test may dominate elaborate monitoring for infrequent, low-cost, reversible decisions.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Fault detection coverage tied to required function
- `REQUIRED_FUNCTION`: Timely recognition that the required function or a protective/recovery path has entered a defined failed/degraded state.
- `MISSION_OR_SERVICE`: Timely recognition that the required function or a protective/recovery path has entered a defined failed/degraded state.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: A green component signal coexists with broken end-to-end function, or the target fault is outside the monitor’s coverage.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Operator, maintainer, automated recovery controller and mission owner.
- `CHEAP_PATH`: A direct manual functional test may dominate elaborate monitoring for infrequent, low-cost, reversible decisions.
- `MATURE_FORM`: A coverage claim indexed by fault class, operating mode, latency and end-to-end consequence, validated independently of the monitored component.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Fault detection coverage tied to required function
- `INITIATING_FAULT_OR_FAILURE`: A green component signal coexists with broken end-to-end function, or the target fault is outside the monitor’s coverage.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: A green component signal coexists with broken end-to-end function, or the target fault is outside the monitor’s coverage.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Observable consequences, representative fault injection/field labels, threshold calibration, independent monitoring dependencies and action path.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Define the fault/failure population; map each to observables and latency; measure misses/false alarms; include end-to-end functional probes and dormant paths.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Fault detection coverage tied to required function
- `TARGET_FAULTS_FAILURES`: A green component signal coexists with broken end-to-end function, or the target fault is outside the monitor’s coverage.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: A coverage claim indexed by fault class, operating mode, latency and end-to-end consequence, validated independently of the monitored component.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Observable consequences, representative fault injection/field labels, threshold calibration, independent monitoring dependencies and action path.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE_TO_HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Coverage numbers are often generated from an incomplete fault list and can be falsely precise.

**ANTI_CEREMONY_BOUNDARY**  
A health dashboard is optional; the property is known detection performance over the relevant failure population.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate fault detection coverage tied to required function?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?

</details>
<details><summary><strong>ERM-P012 — Diagnostic isolation, ambiguity and confidence discipline</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Identify a cause set at the resolution needed for safe containment, repair or recovery within the mission deadline.
- `failure_mode`: Premature root-cause certainty, unresolved ambiguity, confounded dependency symptoms or diagnosis drift triggers ineffective action.
**MATURE_FORM**  
Decision-sufficient diagnosis: calibrated cause set, evidence, ambiguity, latency and reversible action—not forced single-cause certainty.

**TRIGGER**  
Multiple plausible causes, costly/irreversible repair, automatic remediation, dependency failures or repeated “no fault found.”

**CHEAP_PATH**  
When several causes share the same safe reversible remedy, act on the symptom and defer exact root cause.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Diagnostic isolation, ambiguity and confidence discipline
- `INITIATING_FAULT_OR_FAILURE`: Premature root-cause certainty, unresolved ambiguity, confounded dependency symptoms or diagnosis drift triggers ineffective action.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Premature root-cause certainty, unresolved ambiguity, confounded dependency symptoms or diagnosis drift triggers ineffective action.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Causal/functional model, sensor validity, fault labels, access to dependency state, time budget and action-cost model.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Maintain hypotheses/ambiguity groups; seek discriminating observations; calibrate confidence; match action reversibility and authority to uncertainty.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Diagnostic isolation, ambiguity and confidence discipline
- `TARGET_FAULTS_FAILURES`: Premature root-cause certainty, unresolved ambiguity, confounded dependency symptoms or diagnosis drift triggers ineffective action.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: Decision-sufficient diagnosis: calibrated cause set, evidence, ambiguity, latency and reversible action—not forced single-cause certainty.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Diagnostic isolation, ambiguity and confidence discipline
- `INITIATING_FAILURE`: Premature root-cause certainty, unresolved ambiguity, confounded dependency symptoms or diagnosis drift triggers ineffective action.
- `RECOVERY_ACTION`: Maintain hypotheses/ambiguity groups; seek discriminating observations; calibrate confidence; match action reversibility and authority to uncertainty.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Identify a cause set at the resolution needed for safe containment, repair or recovery within the mission deadline.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: Decision-sufficient diagnosis: calibrated cause set, evidence, ambiguity, latency and reversible action—not forced single-cause certainty.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Causal/functional model, sensor validity, fault labels, access to dependency state, time budget and action-cost model.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `MODERATE_TO_HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Root-cause analysis can become post-hoc narrative; exact isolation may cost more time than safe restoration permits.

**ANTI_CEREMONY_BOUNDARY**  
A root-cause label is not the property; discriminating evidence and action-relevant confidence are.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate diagnostic isolation, ambiguity and confidence discipline?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P013 — Explicit false-positive, false-negative and action cost</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: A monitoring/diagnostic decision that minimises mission-relevant expected loss under declared consequences and constraints.
- `failure_mode`: A threshold is selected from model accuracy alone without the cost of unnecessary action, delay, missed failure or operator saturation.
**MATURE_FORM**  
A decision-calibrated coverage argument with uncertainty, base rates, action costs, drift checks and safe fallback.

**TRIGGER**  
Anomaly detection, PHM, health checks, alerting, automatic failover/remediation or costly inspection/replacement.

**CHEAP_PATH**  
Use a conservative rule or human confirmation when event rate is low and labels cannot support fine calibration.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Explicit false-positive, false-negative and action cost
- `INITIATING_FAULT_OR_FAILURE`: A threshold is selected from model accuracy alone without the cost of unnecessary action, delay, missed failure or operator saturation.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: A threshold is selected from model accuracy alone without the cost of unnecessary action, delay, missed failure or operator saturation.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Ground truth or adjudicated outcomes, base rates, representative profile, action-cost model and feedback after action.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Estimate conditional errors by mode/profile; attach action/consequence costs; calibrate thresholds; monitor drift; permit abstention/manual review.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Explicit false-positive, false-negative and action cost
- `TARGET_FAULTS_FAILURES`: A threshold is selected from model accuracy alone without the cost of unnecessary action, delay, missed failure or operator saturation.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: A decision-calibrated coverage argument with uncertainty, base rates, action costs, drift checks and safe fallback.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Explicit false-positive, false-negative and action cost
- `CLAIM`: A decision-calibrated coverage argument with uncertainty, base rates, action costs, drift checks and safe fallback.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Operator, maintainer, service owner and automated-action authority.
- `CHEAP_PATH`: Use a conservative rule or human confirmation when event rate is low and labels cannot support fine calibration.
- `CONTRARY_EVIDENCE`: Where a direct deterministic functional check exists, statistical threshold optimisation is unnecessary.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A decision-calibrated coverage argument with uncertainty, base rates, action costs, drift checks and safe fallback.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Ground truth or adjudicated outcomes, base rates, representative profile, action-cost model and feedback after action.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `MODERATE_TO_HIGH`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Monetising severe consequences can be ethically or practically difficult; uncertain costs can create false optimisation.

**ANTI_CEREMONY_BOUNDARY**  
An ROC/AUC chart or alert count is not the property; decision loss under the actual profile is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate explicit false-positive, false-negative and action cost?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P014 — Graceful degradation with explicit mission priorities</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Preserve prioritised critical function within degraded performance, time and consequence limits until repair/recovery or safe stop.
- `failure_mode`: The degraded state violates unstated dependencies, hides data loss, starves a user class, exceeds duration or cannot be exited.
**MATURE_FORM**  
A tested degradation contract specifying protected functions, sacrificed functions, consumer impact, observability, duration and exit criteria.

**TRIGGER**  
Capacity loss, partial dependency failure, redundancy exhaustion or missions where some function is better than none.

**CHEAP_PATH**  
Stop safely when degraded operation has no defensible acceptance criteria or adds greater consequence than interruption.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Graceful degradation with explicit mission priorities
- `REQUIRED_FUNCTION`: Preserve prioritised critical function within degraded performance, time and consequence limits until repair/recovery or safe stop.
- `MISSION_OR_SERVICE`: Preserve prioritised critical function within degraded performance, time and consequence limits until repair/recovery or safe stop.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: The degraded state violates unstated dependencies, hides data loss, starves a user class, exceeds duration or cannot be exited.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Mission owner, user populations, operator and incident commander.
- `CHEAP_PATH`: Stop safely when degraded operation has no defensible acceptance criteria or adds greater consequence than interruption.
- `MATURE_FORM`: A tested degradation contract specifying protected functions, sacrificed functions, consumer impact, observability, duration and exit criteria.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Graceful degradation with explicit mission priorities
- `INITIATING_FAULT_OR_FAILURE`: The degraded state violates unstated dependencies, hides data loss, starves a user class, exceeds duration or cannot be exited.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: The degraded state violates unstated dependencies, hides data loss, starves a user class, exceeds duration or cannot be exited.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Mission prioritisation, state model, resource reservation, independent observability, operator/user communication and recovery path.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Predefine capability tiers, priorities, admission/load shedding, observability, annunciation, time limits, exit/escalation and recovery tests.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Graceful degradation with explicit mission priorities
- `INITIATING_FAILURE`: The degraded state violates unstated dependencies, hides data loss, starves a user class, exceeds duration or cannot be exited.
- `RECOVERY_ACTION`: Predefine capability tiers, priorities, admission/load shedding, observability, annunciation, time limits, exit/escalation and recovery tests.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Preserve prioritised critical function within degraded performance, time and consequence limits until repair/recovery or safe stop.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A tested degradation contract specifying protected functions, sacrificed functions, consumer impact, observability, duration and exit criteria.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Mission prioritisation, state model, resource reservation, independent observability, operator/user communication and recovery path.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE_TO_HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
“Graceful” is value-laden; degradation may shift harm to less visible consumers or conflict with safety/security constraints.

**ANTI_CEREMONY_BOUNDARY**  
A feature flag or “degraded mode” label is not the property; controlled consequence and exit are.

**POSSIBLE_CONFLICTING_PROPERTY**  
Continuity and reduced capability versus hidden unacceptable or unsafe degradation.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate graceful degradation with explicit mission priorities?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P015 — Contextual selection of fail-safe, fail-stop and fail-operational objectives</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The action after fault must minimise mission/consumer consequence under the applicable safety, integrity, availability and recoverability priorities.
- `failure_mode`: A universal availability objective continues corrupt/unsafe operation, or a universal stop policy destroys a time-critical mission that could tolerate degradation.
**MATURE_FORM**  
A source-grounded, explicitly prioritised transition policy rather than a generic “always available” or “always fail safe” rule.

**TRIGGER**  
Functions where interruption and continued erroneous operation have materially different consequences.

**CHEAP_PATH**  
Default to a simple safe stop for reversible low-consequence work when continued correctness cannot be established.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Contextual selection of fail-safe, fail-stop and fail-operational objectives
- `REQUIRED_FUNCTION`: The action after fault must minimise mission/consumer consequence under the applicable safety, integrity, availability and recoverability priorities.
- `MISSION_OR_SERVICE`: The action after fault must minimise mission/consumer consequence under the applicable safety, integrity, availability and recoverability priorities.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: A universal availability objective continues corrupt/unsafe operation, or a universal stop policy destroys a time-critical mission that could tolerate degradation.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Mission authority, operator, affected users and cross-functional assurance owners.
- `CHEAP_PATH`: Default to a simple safe stop for reversible low-consequence work when continued correctness cannot be established.
- `MATURE_FORM`: A source-grounded, explicitly prioritised transition policy rather than a generic “always available” or “always fail safe” rule.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Contextual selection of fail-safe, fail-stop and fail-operational objectives
- `INITIATING_FAULT_OR_FAILURE`: A universal availability objective continues corrupt/unsafe operation, or a universal stop policy destroys a time-critical mission that could tolerate degradation.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: A universal availability objective continues corrupt/unsafe operation, or a universal stop policy destroys a time-critical mission that could tolerate degradation.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Consequence model, state observability, independent protection, degraded criteria and cross-discipline constraints.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Perform consequence- and mode-specific objective selection; define trigger, authority, state confidence, tolerated duration and fallback.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Consequence model, state observability, independent protection, degraded criteria and cross-discipline constraints.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `LOW_WITHOUT_CONTEXT`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
No reliability-only rule resolves the value trade-off; evidence from one domain cannot set another domain’s objective.

**ANTI_CEREMONY_BOUNDARY**  
A “fail-safe” label is not the property; the consequence-based transition and evidence are.

**POSSIBLE_CONFLICTING_PROPERTY**  
Fail-operational continuity versus fail-safe/fail-stop containment.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate contextual selection of fail-safe, fail-stop and fail-operational objectives?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?

</details>
<details><summary><strong>ERM-P016 — Recovery closes on required function and state postconditions</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Re-establish the ERM-P001 required function, authoritative state and dependency readiness within the declared restoration bound.
- `failure_mode`: Process starts but user/mission function is wrong, incomplete, too slow, unauthorised or vulnerable to immediate recurrence.
**MATURE_FORM**  
A recovery case with explicit preconditions, authoritative state, functional/data/dependency postconditions, independent validation and fallback.

**TRIGGER**  
Restart, retry, failover, rollback, restore, rebuild, repair, workaround or disaster recovery.

**CHEAP_PATH**  
For stateless, low-consequence functions, a direct end-to-end transaction after restart may be sufficient.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Recovery closes on required function and state postconditions
- `REQUIRED_FUNCTION`: Re-establish the ERM-P001 required function, authoritative state and dependency readiness within the declared restoration bound.
- `MISSION_OR_SERVICE`: Re-establish the ERM-P001 required function, authoritative state and dependency readiness within the declared restoration bound.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Process starts but user/mission function is wrong, incomplete, too slow, unauthorised or vulnerable to immediate recurrence.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Operator, incident commander, mission owner, user and return-to-service authority.
- `CHEAP_PATH`: For stateless, low-consequence functions, a direct end-to-end transaction after restart may be sufficient.
- `MATURE_FORM`: A recovery case with explicit preconditions, authoritative state, functional/data/dependency postconditions, independent validation and fallback.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Recovery closes on required function and state postconditions
- `INITIATING_FAULT_OR_FAILURE`: Process starts but user/mission function is wrong, incomplete, too slow, unauthorised or vulnerable to immediate recurrence.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Process starts but user/mission function is wrong, incomplete, too slow, unauthorised or vulnerable to immediate recurrence.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Valid source, diagnosis/containment, state semantics, acceptance criteria, independent observability and fallback.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Define recovery source/authority, reconcile state, verify dependencies/capacity, perform independent end-to-end functional checks and control return to service.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Recovery closes on required function and state postconditions
- `TARGET_FAULTS_FAILURES`: Process starts but user/mission function is wrong, incomplete, too slow, unauthorised or vulnerable to immediate recurrence.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: A recovery case with explicit preconditions, authoritative state, functional/data/dependency postconditions, independent validation and fallback.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Recovery closes on required function and state postconditions
- `INITIATING_FAILURE`: Process starts but user/mission function is wrong, incomplete, too slow, unauthorised or vulnerable to immediate recurrence.
- `RECOVERY_ACTION`: Define recovery source/authority, reconcile state, verify dependencies/capacity, perform independent end-to-end functional checks and control return to service.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Re-establish the ERM-P001 required function, authoritative state and dependency readiness within the declared restoration bound.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A recovery case with explicit preconditions, authoritative state, functional/data/dependency postconditions, independent validation and fallback.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Valid source, diagnosis/containment, state semantics, acceptance criteria, independent observability and fallback.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
Exhaustive post-recovery validation can delay urgent service; checks must be risk- and time-proportionate.

**ANTI_CEREMONY_BOUNDARY**  
A closed incident or successful command is not the property; observed re-establishment of required function is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Restoration speed versus diagnostic confidence, state correctness and evidence preservation.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate recovery closes on required function and state postconditions?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P017 — Backup, restore and reconstitution paths must be exercised and validated</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Restore required data/state and application function to a trusted, current-enough configuration within RPO/RTO and consequence limits.
- `failure_mode`: Backup job reports success but restore cannot complete, recovered data is inconsistent, required tools/docs are unavailable or the same cause contaminates sources.
**MATURE_FORM**  
A periodically refreshed restore/reconstitution demonstration closing on functional and state postconditions for the current configuration.

**TRIGGER**  
Any claim of backup, disaster recovery, spare image, replicated state, rebuild-from-code or clean-room recovery.

**CHEAP_PATH**  
For reproducible stateless artefacts, verify rebuild and one functional check instead of elaborate backup infrastructure.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Backup, restore and reconstitution paths must be exercised and validated
- `REQUIRED_FUNCTION`: Restore required data/state and application function to a trusted, current-enough configuration within RPO/RTO and consequence limits.
- `MISSION_OR_SERVICE`: Restore required data/state and application function to a trusted, current-enough configuration within RPO/RTO and consequence limits.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Backup job reports success but restore cannot complete, recovered data is inconsistent, required tools/docs are unavailable or the same cause contaminates sources.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Service/data owner, operator, mission continuity authority and affected users.
- `CHEAP_PATH`: For reproducible stateless artefacts, verify rebuild and one functional check instead of elaborate backup infrastructure.
- `MATURE_FORM`: A periodically refreshed restore/reconstitution demonstration closing on functional and state postconditions for the current configuration.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Backup, restore and reconstitution paths must be exercised and validated
- `INITIATING_FAULT_OR_FAILURE`: Backup job reports success but restore cannot complete, recovered data is inconsistent, required tools/docs are unavailable or the same cause contaminates sources.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Backup job reports success but restore cannot complete, recovered data is inconsistent, required tools/docs are unavailable or the same cause contaminates sources.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Configuration manifests, credentials, tools, dependencies, capacity, state consistency, acceptance criteria and staff capability.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Inventory sources, isolate/protect them, verify integrity/freshness, rehearse non-production restore, validate application semantics and reconstitution logistics.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Backup, restore and reconstitution paths must be exercised and validated
- `INITIATING_FAILURE`: Backup job reports success but restore cannot complete, recovered data is inconsistent, required tools/docs are unavailable or the same cause contaminates sources.
- `RECOVERY_ACTION`: Inventory sources, isolate/protect them, verify integrity/freshness, rehearse non-production restore, validate application semantics and reconstitution logistics.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Restore required data/state and application function to a trusted, current-enough configuration within RPO/RTO and consequence limits.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A periodically refreshed restore/reconstitution demonstration closing on functional and state postconditions for the current configuration.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Backup, restore and reconstitution paths must be exercised and validated
- `CLAIM`: A periodically refreshed restore/reconstitution demonstration closing on functional and state postconditions for the current configuration.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Service/data owner, operator, mission continuity authority and affected users.
- `CHEAP_PATH`: For reproducible stateless artefacts, verify rebuild and one functional check instead of elaborate backup infrastructure.
- `CONTRARY_EVIDENCE`: A single successful restore does not establish all future restores, configurations or correlated disaster conditions.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A periodically refreshed restore/reconstitution demonstration closing on functional and state postconditions for the current configuration.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Configuration manifests, credentials, tools, dependencies, capacity, state consistency, acceptance criteria and staff capability.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `VERY_HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Frequent full rehearsals are costly and can create production risk; representative, isolated exercises and cheaper checks should be chosen by decision value.

**ANTI_CEREMONY_BOUNDARY**  
A backup icon, policy or DR document is not the property; a valid exercised recovery path is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Fast restoration versus backup integrity, freshness and reconstitution validation.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate backup, restore and reconstitution paths must be exercised and validated?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P018 — Conditional validity of retry, restart, rollback and checkpoint recovery</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Complete the intended operation or restore service/state without duplicate side effects, overload, corruption or recurrence.
- `failure_mode`: Retry storm, non-idempotent duplicate, domino rollback, stale checkpoint, incompatible rollback, restart loop or hidden dependency failure.
**MATURE_FORM**  
A fault-class-specific recovery policy with bounded attempts, consistency/compatibility proof, load protection, observation and fallback.

**TRIGGER**  
Transient faults, process crashes, failed releases or recoverable state loss where operation semantics and state are known.

**CHEAP_PATH**  
Do not retry deterministic validation errors or overload; fail clearly and preserve evidence.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Conditional validity of retry, restart, rollback and checkpoint recovery
- `REQUIRED_FUNCTION`: Complete the intended operation or restore service/state without duplicate side effects, overload, corruption or recurrence.
- `MISSION_OR_SERVICE`: Complete the intended operation or restore service/state without duplicate side effects, overload, corruption or recurrence.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Retry storm, non-idempotent duplicate, domino rollback, stale checkpoint, incompatible rollback, restart loop or hidden dependency failure.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Service owner, operator, recovery controller and users.
- `CHEAP_PATH`: Do not retry deterministic validation errors or overload; fail clearly and preserve evidence.
- `MATURE_FORM`: A fault-class-specific recovery policy with bounded attempts, consistency/compatibility proof, load protection, observation and fallback.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Conditional validity of retry, restart, rollback and checkpoint recovery
- `INITIATING_FAULT_OR_FAILURE`: Retry storm, non-idempotent duplicate, domino rollback, stale checkpoint, incompatible rollback, restart loop or hidden dependency failure.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Retry storm, non-idempotent duplicate, domino rollback, stale checkpoint, incompatible rollback, restart loop or hidden dependency failure.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Idempotency/deduplication, state consistency, checkpoint freshness, dependency capacity, rollback artefacts and stop conditions.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Classify fault transience; bound retries/backoff; establish idempotency; coordinate checkpoints; validate rollback compatibility; circuit-break and escalate.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Conditional validity of retry, restart, rollback and checkpoint recovery
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: A fault-class-specific recovery policy with bounded attempts, consistency/compatibility proof, load protection, observation and fallback.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Conditional validity of retry, restart, rollback and checkpoint recovery
- `INITIATING_FAILURE`: Retry storm, non-idempotent duplicate, domino rollback, stale checkpoint, incompatible rollback, restart loop or hidden dependency failure.
- `RECOVERY_ACTION`: Classify fault transience; bound retries/backoff; establish idempotency; coordinate checkpoints; validate rollback compatibility; circuit-break and escalate.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Complete the intended operation or restore service/state without duplicate side effects, overload, corruption or recurrence.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A fault-class-specific recovery policy with bounded attempts, consistency/compatibility proof, load protection, observation and fallback.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Idempotency/deduplication, state consistency, checkpoint freshness, dependency capacity, rollback artefacts and stop conditions.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Recovery primitives can mask design defects and create correlated cascades; their success rate is workload- and fault-specific.

**ANTI_CEREMONY_BOUNDARY**  
A restart button, retry library or checkpoint file is not the property; valid semantics and successful postconditions are.

**POSSIBLE_CONFLICTING_PROPERTY**  
Rapid retry/restart versus overload, duplicate effects and corrupt-state recurrence.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate conditional validity of retry, restart, rollback and checkpoint recovery?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P019 — Repairability and maintainability by design</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Restore the defined function safely within the total downtime bound under actual field support conditions.
- `failure_mode`: Procedure exists but access, isolation, tools, spares, skills, state/configuration transfer or verification make repair infeasible or error-prone.
**MATURE_FORM**  
Field-demonstrated restoration capability spanning detection, access, repair/replacement, configuration/state preservation, validation and return to service.

**TRIGGER**  
Repairable/high-value/long-life systems, remote sites, tight restoration bounds, repeated service intervention or obsolescence exposure.

**CHEAP_PATH**  
For low-cost short-life items, replacement or graceful discard may dominate elaborate repairability.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Repairability and maintainability by design
- `INITIATING_FAULT_OR_FAILURE`: Procedure exists but access, isolation, tools, spares, skills, state/configuration transfer or verification make repair infeasible or error-prone.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Procedure exists but access, isolation, tools, spares, skills, state/configuration transfer or verification make repair infeasible or error-prone.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Maintenance concept, field observations, human factors, logistics, tools, documentation, configuration control and testability.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Design for access, isolation, modular replacement, test points, diagnostics, standard interfaces, safe handling, configuration/state transfer and repair verification.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Repairability and maintainability by design
- `TARGET_FAULTS_FAILURES`: Procedure exists but access, isolation, tools, spares, skills, state/configuration transfer or verification make repair infeasible or error-prone.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: Field-demonstrated restoration capability spanning detection, access, repair/replacement, configuration/state preservation, validation and return to service.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Repairability and maintainability by design
- `INITIATING_FAILURE`: Procedure exists but access, isolation, tools, spares, skills, state/configuration transfer or verification make repair infeasible or error-prone.
- `RECOVERY_ACTION`: Design for access, isolation, modular replacement, test points, diagnostics, standard interfaces, safe handling, configuration/state transfer and repair verification.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Restore the defined function safely within the total downtime bound under actual field support conditions.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: Field-demonstrated restoration capability spanning detection, access, repair/replacement, configuration/state preservation, validation and return to service.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Maintenance concept, field observations, human factors, logistics, tools, documentation, configuration control and testability.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Optimising predicted MTTR can ignore diagnosis, logistics and validation; modularity can add failure points.

**ANTI_CEREMONY_BOUNDARY**  
A maintainability prediction is not the property; repair performed correctly under real support constraints is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Modular replaceability versus interface/configuration/state complexity.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate repairability and maintainability by design?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P020 — Supportability, logistics and operational maintenance capability</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The complete support system restores required function within the operational downtime bound across deployed locations and mission conditions.
- `failure_mode`: Low bench repair time is overwhelmed by waiting, access, approval, supplier lead time, obsolete parts, unavailable expertise or incompatible configuration.
**MATURE_FORM**  
A tested support concept with total-downtime data, resource/configuration identity, alternatives and explicit risk acceptance for uncovered sites/times.

**TRIGGER**  
Distributed fleets, remote/contested sites, long-life assets, supplier concentration, strict availability or disaster recovery.

**CHEAP_PATH**  
For low-criticality items, accept longer restoration or stock simple replacements rather than build a complex support network.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Supportability, logistics and operational maintenance capability
- `REQUIRED_FUNCTION`: The complete support system restores required function within the operational downtime bound across deployed locations and mission conditions.
- `MISSION_OR_SERVICE`: The complete support system restores required function within the operational downtime bound across deployed locations and mission conditions.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Low bench repair time is overwhelmed by waiting, access, approval, supplier lead time, obsolete parts, unavailable expertise or incompatible configuration.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Fleet/asset owner, logistics organisation, operator, maintainer and mission planner.
- `CHEAP_PATH`: For low-criticality items, accept longer restoration or stock simple replacements rather than build a complex support network.
- `MATURE_FORM`: A tested support concept with total-downtime data, resource/configuration identity, alternatives and explicit risk acceptance for uncovered sites/times.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Supportability, logistics and operational maintenance capability
- `INITIATING_FAULT_OR_FAILURE`: Low bench repair time is overwhelmed by waiting, access, approval, supplier lead time, obsolete parts, unavailable expertise or incompatible configuration.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Low bench repair time is overwhelmed by waiting, access, approval, supplier lead time, obsolete parts, unavailable expertise or incompatible configuration.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Demand rates, repair-level policy, supply data, workforce readiness, transport/access, contracts, configuration and obsolescence monitoring.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Model and measure total downtime; provision/position resources; exercise escalation; manage obsolescence; sustain documentation, credentials and skills.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Supportability, logistics and operational maintenance capability
- `INITIATING_FAILURE`: Low bench repair time is overwhelmed by waiting, access, approval, supplier lead time, obsolete parts, unavailable expertise or incompatible configuration.
- `RECOVERY_ACTION`: Model and measure total downtime; provision/position resources; exercise escalation; manage obsolescence; sustain documentation, credentials and skills.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: The complete support system restores required function within the operational downtime bound across deployed locations and mission conditions.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A tested support concept with total-downtime data, resource/configuration identity, alternatives and explicit risk acceptance for uncovered sites/times.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Demand rates, repair-level policy, supply data, workforce readiness, transport/access, contracts, configuration and obsolescence monitoring.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Stocking and spare capacity are costly; forecasts are uncertain; overprovisioning can create obsolescence and maintenance burden.

**ANTI_CEREMONY_BOUNDARY**  
A logistics plan or SLA is not the property; actual timely access to the right resources is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate supportability, logistics and operational maintenance capability?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P021 — Maintenance-induced failure and maintenance human factors as system mechanisms</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Maintenance must preserve or restore the required function without creating a new latent, common-cause or interface failure.
- `failure_mode`: Wrong part/configuration, omitted step, damage during access, common calibration error, simultaneous channel disablement or ineffective verification.
**MATURE_FORM**  
Maintenance treated as an operational mode with its own hazards, dependencies, state transitions, common-cause controls and post-maintenance functional proof.

**TRIGGER**  
Intrusive maintenance, repeated “no fault found,” common-channel work, difficult access, night/remote work, complex software/configuration changes.

**CHEAP_PATH**  
Eliminate unnecessary maintenance or replace a fragile manual step with a simple poka-yoke/functional check where that is safer.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Maintenance-induced failure and maintenance human factors as system mechanisms
- `INITIATING_FAULT_OR_FAILURE`: Wrong part/configuration, omitted step, damage during access, common calibration error, simultaneous channel disablement or ineffective verification.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Wrong part/configuration, omitted step, damage during access, common calibration error, simultaneous channel disablement or ineffective verification.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Work-as-done observation, maintainability design, staffing/fatigue controls, independent verification, event reporting and organisational learning.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Design out error opportunities; control configuration; isolate channels; use usable procedures/tools; manage fatigue/communication; verify function after work; learn without individual blame substitution.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Maintenance-induced failure and maintenance human factors as system mechanisms
- `TARGET_FAULTS_FAILURES`: Wrong part/configuration, omitted step, damage during access, common calibration error, simultaneous channel disablement or ineffective verification.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: Maintenance treated as an operational mode with its own hazards, dependencies, state transitions, common-cause controls and post-maintenance functional proof.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Work-as-done observation, maintainability design, staffing/fatigue controls, independent verification, event reporting and organisational learning.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE_TO_HIGH`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
“Human error” can become a residual label that hides design and organisational causes; added checks can create workload and new failure modes.

**ANTI_CEREMONY_BOUNDARY**  
A sign-off or training record is not the property; reduced error opportunity and verified post-work function are.

**POSSIBLE_CONFLICTING_PROPERTY**  
Preventive/corrective intervention versus maintenance-induced failure.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate maintenance-induced failure and maintenance human factors as system mechanisms?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?

</details>
<details><summary><strong>ERM-P022 — Age-based preventive maintenance only for valid age-related mechanisms</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Reduce mission failure or lifecycle consequence by acting before a demonstrable age-related risk rise.
- `failure_mode`: A convenient age limit is imposed without a dominant wear-out mode, stable age relationship or evidence that overhaul restores resistance.
**MATURE_FORM**  
A maintenance interval justified by a causal degradation mechanism, exposure model, uncertainty, task effectiveness and net-consequence comparison.

**TRIGGER**  
Dominant wear-out, fatigue, corrosion, consumable depletion or legally/physically bounded life with observable age/exposure.

**CHEAP_PATH**  
Run to failure, inspect condition or use simple replacement-on-failure when consequence and restoration support permit.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Age-based preventive maintenance only for valid age-related mechanisms
- `CLAIM`: A maintenance interval justified by a causal degradation mechanism, exposure model, uncertainty, task effectiveness and net-consequence comparison.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Maintenance planner, asset/fleet owner and mission-risk authority.
- `CHEAP_PATH`: Run to failure, inspect condition or use simple replacement-on-failure when consequence and restoration support permit.
- `CONTRARY_EVIDENCE`: Strong wear-out mechanisms and finite-life items provide robust contexts where age-based replacement is retained.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A maintenance interval justified by a causal degradation mechanism, exposure model, uncertainty, task effectiveness and net-consequence comparison.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Mechanism-specific life data, exposure rather than calendar age where appropriate, restoration-effect evidence and maintenance quality.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `MODERATE`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
The famous RCM pattern proportions are aircraft-specific; they justify mechanism testing, not a universal claim that age never matters.

**ANTI_CEREMONY_BOUNDARY**  
A preventive-maintenance calendar is not the property; intervention before a validated age-linked risk is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Scheduled replacement versus induced work, downtime and needless part replacement.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate age-based preventive maintenance only for valid age-related mechanisms?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P023 — Condition-based and predictive maintenance only with observable precursors and decision value</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Detect actionable degradation with enough lead time and confidence that intervention reduces expected mission/lifecycle loss.
- `failure_mode`: No stable precursor; sensor drift; domain shift; uncertain RUL ignored; maintenance action ineffective; false alarms dominate; lead time shorter than logistics delay.
**MATURE_FORM**  
A field-calibrated, uncertainty-aware precursor and intervention case compared against a cheap baseline under the actual loss function.

**TRIGGER**  
Failure mechanisms with measurable deterioration, sufficient lead time, meaningful consequence and an effective intervention.

**CHEAP_PATH**  
Use inspection, fixed replacement or run-to-failure when a simple policy performs similarly or data/precursors are inadequate.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Condition-based and predictive maintenance only with observable precursors and decision value
- `INITIATING_FAULT_OR_FAILURE`: No stable precursor; sensor drift; domain shift; uncertain RUL ignored; maintenance action ineffective; false alarms dominate; lead time shorter than logistics delay.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: No stable precursor; sensor drift; domain shift; uncertain RUL ignored; maintenance action ineffective; false alarms dominate; lead time shorter than logistics delay.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Reliable sensing, labelled/field failure data, calibrated uncertainty, domain representativeness, maintenance capacity and action-cost model.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Validate precursor-to-failure relation, sensor chain, uncertainty, lead-time distribution and intervention effect; optimise against simple policies; monitor drift.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Condition-based and predictive maintenance only with observable precursors and decision value
- `TARGET_FAULTS_FAILURES`: No stable precursor; sensor drift; domain shift; uncertain RUL ignored; maintenance action ineffective; false alarms dominate; lead time shorter than logistics delay.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: A field-calibrated, uncertainty-aware precursor and intervention case compared against a cheap baseline under the actual loss function.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Condition-based and predictive maintenance only with observable precursors and decision value
- `CLAIM`: A field-calibrated, uncertainty-aware precursor and intervention case compared against a cheap baseline under the actual loss function.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Maintenance planner, asset owner, operator and logistics manager.
- `CHEAP_PATH`: Use inspection, fixed replacement or run-to-failure when a simple policy performs similarly or data/precursors are inadequate.
- `CONTRARY_EVIDENCE`: Well-instrumented monotonic degradation with proven intervention can yield strong value; the result remains mechanism-specific.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A field-calibrated, uncertainty-aware precursor and intervention case compared against a cheap baseline under the actual loss function.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Reliable sensing, labelled/field failure data, calibrated uncertainty, domain representativeness, maintenance capacity and action-cost model.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MIXED`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `MODERATE_TO_HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `LOW_TO_MODERATE`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE_TO_HIGH`

**CRITICISMS**  
The literature is heterogeneous and often laboratory/dataset-centric; no evidence supports universal superiority over simpler policies.

**ANTI_CEREMONY_BOUNDARY**  
A “predictive maintenance” platform or RUL number is not the property; demonstrated earlier/better decisions are.

**POSSIBLE_CONFLICTING_PROPERTY**  
Sensitivity/early warning versus false maintenance and model drift.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate condition-based and predictive maintenance only with observable precursors and decision value?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P024 — Closed-loop test–analyse–fix and FRACAS</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Remove or bound recurrent failure mechanisms in the current design/support configuration and verify the changed mission outcome.
- `failure_mode`: Selective reporting; “no trouble found”; delayed fixes; fix not configuration-bound; no retest; curve fit substitutes for causal closure.
**MATURE_FORM**  
A proportionate closed loop in which every material failure is tied to exposure, cause confidence, corrective change, verification and recurrence outcome.

**TRIGGER**  
Development test failures, repeated field events, unexplained downtime, reliability-growth commitments or high-cost maintenance families.

**CHEAP_PATH**  
For isolated low-consequence failures, make the obvious reversible correction and verify function without standing up a heavy FRACAS board.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Closed-loop test–analyse–fix and FRACAS
- `INITIATING_FAULT_OR_FAILURE`: Selective reporting; “no trouble found”; delayed fixes; fix not configuration-bound; no retest; curve fit substitutes for causal closure.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Selective reporting; “no trouble found”; delayed fixes; fix not configuration-bound; no retest; curve fit substitutes for causal closure.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Data quality, ownership, change authority, configuration traceability, representative retest and recurrence horizon.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Unique failure identity; exposure/context capture; causal analysis; prioritised design/process correction; independent retest; recurrence monitoring; fleet/configuration propagation.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Closed-loop test–analyse–fix and FRACAS
- `CLAIM`: A proportionate closed loop in which every material failure is tied to exposure, cause confidence, corrective change, verification and recurrence outcome.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Design authority, reliability manager, maintainer, fleet/service owner and acceptance authority.
- `CHEAP_PATH`: For isolated low-consequence failures, make the obvious reversible correction and verify function without standing up a heavy FRACAS board.
- `CONTRARY_EVIDENCE`: Growth can plateau or reverse when exposure changes, fixes interact or new complexity is introduced.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A proportionate closed loop in which every material failure is tied to exposure, cause confidence, corrective change, verification and recurrence outcome.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Data quality, ownership, change authority, configuration traceability, representative retest and recurrence horizon.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
FRACAS can become labour-intensive bureaucracy and reliability-growth models can reward test selection or delayed fixes.

**ANTI_CEREMONY_BOUNDARY**  
The database or review board is not the property; verified reduction of the causal failure mechanism is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate closed-loop test–analyse–fix and fracas?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P025 — Corrective-action effectiveness and recurrence control</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The relevant failure family no longer occurs, or its frequency/consequence is demonstrably reduced, across the intended population and configuration.
- `failure_mode`: Fix addresses only one manifestation; test cannot reproduce cause; exposure disappears; sibling systems unpatched; workaround becomes permanent.
**MATURE_FORM**  
A bounded causal claim supported by mechanism-targeted tests, deployment evidence and exposure-normalised recurrence surveillance.

**TRIGGER**  
Repeated incidents, fleet-wide defect, common supplier/configuration, high-severity failure or claimed reliability growth.

**CHEAP_PATH**  
For a simple deterministic defect, a regression/functional test plus configuration deployment proof may suffice.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Corrective-action effectiveness and recurrence control
- `INITIATING_FAULT_OR_FAILURE`: Fix addresses only one manifestation; test cannot reproduce cause; exposure disappears; sibling systems unpatched; workaround becomes permanent.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Fix addresses only one manifestation; test cannot reproduce cause; exposure disappears; sibling systems unpatched; workaround becomes permanent.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Failure taxonomy, causal evidence, population/configuration inventory, exposure denominator, change deployment and follow-up period.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Define recurrence family and causal claim; propagate change; reproduce or challenge mechanism; monitor normalised recurrence and unintended effects.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Corrective-action effectiveness and recurrence control
- `CLAIM`: A bounded causal claim supported by mechanism-targeted tests, deployment evidence and exposure-normalised recurrence surveillance.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Design owner, service/fleet owner, acceptance authority and users exposed to recurrence.
- `CHEAP_PATH`: For a simple deterministic defect, a regression/functional test plus configuration deployment proof may suffice.
- `CONTRARY_EVIDENCE`: Absence of recurrence is weak when exposure is small or configuration/profile changed.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A bounded causal claim supported by mechanism-targeted tests, deployment evidence and exposure-normalised recurrence surveillance.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Failure taxonomy, causal evidence, population/configuration inventory, exposure denominator, change deployment and follow-up period.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE_TO_HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Causal certainty may be unattainable for rare complex failures; monitoring can delay closure indefinitely.

**ANTI_CEREMONY_BOUNDARY**  
A “root cause” field or closed status is not the property; changed recurrence risk is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate corrective-action effectiveness and recurrence control?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P026 — Reliability demonstration with explicit confidence, population and assumptions</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Bound the probability of the ERM-P001 functional failure for a defined population/profile/configuration at a declared uncertainty level.
- `failure_mode`: Zero failures treated as certainty; dependent trials; post-hoc stopping; excluded failures; nonrepresentative loads; mean used for a tail requirement.
**MATURE_FORM**  
A decision-calibrated evidence statement: claim, denominator, configuration/profile, model/assumptions, uncertainty, coverage and expiry.

**TRIGGER**  
Contractual acceptance, launch/release, supplier qualification, life claim, safety/mission decision or expensive design trade-off.

**CHEAP_PATH**  
Use deterministic functional verification or a coarse bound when probability precision cannot change the decision.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Reliability demonstration with explicit confidence, population and assumptions
- `REQUIRED_FUNCTION`: Bound the probability of the ERM-P001 functional failure for a defined population/profile/configuration at a declared uncertainty level.
- `MISSION_OR_SERVICE`: Bound the probability of the ERM-P001 functional failure for a defined population/profile/configuration at a declared uncertainty level.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Zero failures treated as certainty; dependent trials; post-hoc stopping; excluded failures; nonrepresentative loads; mean used for a tail requirement.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Acceptance authority, mission owner, designer, regulator/procurer and service owner.
- `CHEAP_PATH`: Use deterministic functional verification or a coarse bound when probability precision cannot change the decision.
- `MATURE_FORM`: A decision-calibrated evidence statement: claim, denominator, configuration/profile, model/assumptions, uncertainty, coverage and expiry.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Reliability demonstration with explicit confidence, population and assumptions
- `CLAIM`: A decision-calibrated evidence statement: claim, denominator, configuration/profile, model/assumptions, uncertainty, coverage and expiry.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Acceptance authority, mission owner, designer, regulator/procurer and service owner.
- `CHEAP_PATH`: Use deterministic functional verification or a coarse bound when probability precision cannot change the decision.
- `CONTRARY_EVIDENCE`: Under stable assumptions and representative sampling, demonstration tests provide strong and interpretable evidence.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A decision-calibrated evidence statement: claim, denominator, configuration/profile, model/assumptions, uncertainty, coverage and expiry.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Stable configuration, representative units/profile, independent or modelled dependence, calibrated instruments and failure adjudication.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `VERY_HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `VERY_HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `HIGH`
- `TRANSFERABILITY_STRENGTH`: `HIGH_WHEN_ASSUMPTIONS_HOLD`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Classical confidence may be misread; large samples can be unaffordable; model-based claims remain assumption-sensitive.

**ANTI_CEREMONY_BOUNDARY**  
A qualification certificate is not the property; the bounded evidence claim is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate reliability demonstration with explicit confidence, population and assumptions?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P027 — Accelerated evidence only under failure-mechanism equivalence</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Estimate or discover the field-relevant failure mechanism and life under the declared environment/profile.
- `failure_mode`: Stress changes mechanism, multiple mechanisms mix, model form is wrong, specimens differ, or HALT discovery is reported as a life demonstration.
**MATURE_FORM**  
A mechanism-linked acceleration case with failure-mode confirmation, model diagnostics, uncertainty and explicit non-transfer regions.

**TRIGGER**  
Known stress-accelerable degradation, long life, design comparison or mechanism discovery.

**CHEAP_PATH**  
Use direct field-like stress, engineering margin or targeted destructive test when quantitative acceleration adds no decision value.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Accelerated evidence only under failure-mechanism equivalence
- `CLAIM`: A mechanism-linked acceleration case with failure-mode confirmation, model diagnostics, uncertainty and explicit non-transfer regions.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Reliability engineer, design/materials owner, qualification authority and maintenance planner.
- `CHEAP_PATH`: Use direct field-like stress, engineering margin or targeted destructive test when quantitative acceleration adds no decision value.
- `CONTRARY_EVIDENCE`: When mechanism and acceleration relation are validated, ALT has strong formal and industrial value.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A mechanism-linked acceleration case with failure-mode confirmation, model diagnostics, uncertainty and explicit non-transfer regions.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Mechanism knowledge, stress control, representative specimens, sufficient failures/censoring data, covariates and uncertainty propagation.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `VERY_HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE_TO_HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
Acceleration models are often selected for convenience and validated over too narrow a stress range.

**ANTI_CEREMONY_BOUNDARY**  
A chamber test, HALT or ESS label is not the property; decision-relevant evidence about the field mechanism is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate accelerated evidence only under failure-mechanism equivalence?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P028 — Field-data feedback, model calibration and explicit uncertainty</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Maintain a current evidence distribution for mission failure, recurrence, downtime and repair under field conditions.
- `failure_mode`: Returns lack exposure; under-reporting; mixed configurations; warranty bias; changed profile; point estimates without intervals; incidents not linked to denominator.
**MATURE_FORM**  
A continuously quality-checked, configuration/profile-stratified field evidence process that can falsify prior predictions and expire stale claims.

**TRIGGER**  
Fielded system, changing use/environment, prediction-dependent decisions, sparse test evidence or repeated surprise failures.

**CHEAP_PATH**  
Use direct trend/stratified counts with honest uncertainty when complex Bayesian or parametric models do not improve decisions.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Field-data feedback, model calibration and explicit uncertainty
- `REQUIRED_FUNCTION`: Maintain a current evidence distribution for mission failure, recurrence, downtime and repair under field conditions.
- `MISSION_OR_SERVICE`: Maintain a current evidence distribution for mission failure, recurrence, downtime and repair under field conditions.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Returns lack exposure; under-reporting; mixed configurations; warranty bias; changed profile; point estimates without intervals; incidents not linked to denominator.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Design owner, fleet/service operator, maintainer, supplier manager and mission authority.
- `CHEAP_PATH`: Use direct trend/stratified counts with honest uncertainty when complex Bayesian or parametric models do not improve decisions.
- `MATURE_FORM`: A continuously quality-checked, configuration/profile-stratified field evidence process that can falsify prior predictions and expire stale claims.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Field-data feedback, model calibration and explicit uncertainty
- `CLAIM`: A continuously quality-checked, configuration/profile-stratified field evidence process that can falsify prior predictions and expire stale claims.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Design owner, fleet/service operator, maintainer, supplier manager and mission authority.
- `CHEAP_PATH`: Use direct trend/stratified counts with honest uncertainty when complex Bayesian or parametric models do not improve decisions.
- `CONTRARY_EVIDENCE`: Field data can be less informative than controlled tests for rare mechanisms when exposure and reporting are poor; hybrid evidence is needed.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A continuously quality-checked, configuration/profile-stratified field evidence process that can falsify prior predictions and expire stale claims.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Telemetry/reporting, population inventory, exposure, configuration identity, failure adjudication, privacy/access and model governance.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `VERY_HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `HIGH`
- `TRANSFERABILITY_STRENGTH`: `HIGH_WITH_STRATIFICATION`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Field data are observational and confounded; frequent updating can overreact to noise or encode operational inequity.

**ANTI_CEREMONY_BOUNDARY**  
A data lake or reliability report is not the property; calibrated decision evidence with usable denominators is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate field-data feedback, model calibration and explicit uncertainty?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P029 — Reliability evidence bound to current configuration and change</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: The reliability claim remains valid for the exact deployed configuration and its current profile/dependencies.
- `failure_mode`: Stale qualification; partial rollout; hidden supplier substitution; model/data update; configuration drift; recovery artefact incompatible; mixed fleet denominator.
**MATURE_FORM**  
A live claim-evidence-configuration graph with explicit inheritance rationale, invalidation triggers, targeted checks and field confirmation.

**TRIGGER**  
Any material design, software, data/model, supplier, infrastructure, maintenance-procedure or support change.

**CHEAP_PATH**  
For a small reversible change, run a targeted functional/regression check and explicitly narrow the inherited claim.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Reliability evidence bound to current configuration and change
- `REQUIRED_FUNCTION`: The reliability claim remains valid for the exact deployed configuration and its current profile/dependencies.
- `MISSION_OR_SERVICE`: The reliability claim remains valid for the exact deployed configuration and its current profile/dependencies.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Stale qualification; partial rollout; hidden supplier substitution; model/data update; configuration drift; recovery artefact incompatible; mixed fleet denominator.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Release/change authority, reliability owner, operator, supplier manager and acceptance authority.
- `CHEAP_PATH`: For a small reversible change, run a targeted functional/regression check and explicitly narrow the inherited claim.
- `MATURE_FORM`: A live claim-evidence-configuration graph with explicit inheritance rationale, invalidation triggers, targeted checks and field confirmation.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Reliability evidence bound to current configuration and change
- `CLAIM`: A live claim-evidence-configuration graph with explicit inheritance rationale, invalidation triggers, targeted checks and field confirmation.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Release/change authority, reliability owner, operator, supplier manager and acceptance authority.
- `CHEAP_PATH`: For a small reversible change, run a targeted functional/regression check and explicitly narrow the inherited claim.
- `CONTRARY_EVIDENCE`: Some robust mechanisms transfer across versions; transfer must be argued, not prohibited by default.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A live claim-evidence-configuration graph with explicit inheritance rationale, invalidation triggers, targeted checks and field confirmation.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Unique identities, bill/configuration/dependency inventory, change detection, evidence links, rollout state and rollback/recovery artefacts.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Overly strict binding can block useful evidence transfer and slow iteration; impact analysis must be proportional.

**ANTI_CEREMONY_BOUNDARY**  
A configuration-management database is not the property; knowing which evidence still applies is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate reliability evidence bound to current configuration and change?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P030 — Software reliability under an operational input profile</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Probability/intensity of software-caused functional failure for the current version under the declared input/state/workload profile.
- `failure_mode`: Fault-content model treated as literal; perfect fix assumed; test inputs unrepresentative; interactions/dependencies omitted; version changes invalidate growth curve.
**MATURE_FORM**  
A version- and profile-bound software functional-failure claim triangulated by targeted tests, field exposure and uncertainty—not a generic “software MTBF.”

**TRIGGER**  
Software-dominated function with enough repeated operations/failures for an estimable question and a stable release/profile window.

**CHEAP_PATH**  
Use targeted functional, property, stress and regression tests when a numerical software failure-rate model will not change the decision.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Software reliability under an operational input profile
- `REQUIRED_FUNCTION`: Probability/intensity of software-caused functional failure for the current version under the declared input/state/workload profile.
- `MISSION_OR_SERVICE`: Probability/intensity of software-caused functional failure for the current version under the declared input/state/workload profile.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Fault-content model treated as literal; perfect fix assumed; test inputs unrepresentative; interactions/dependencies omitted; version changes invalidate growth curve.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Software/reliability engineer, release authority, service owner and mission owner.
- `CHEAP_PATH`: Use targeted functional, property, stress and regression tests when a numerical software failure-rate model will not change the decision.
- `MATURE_FORM`: A version- and profile-bound software functional-failure claim triangulated by targeted tests, field exposure and uncertainty—not a generic “software MTBF.”

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Software reliability under an operational input profile
- `CLAIM`: A version- and profile-bound software functional-failure claim triangulated by targeted tests, field exposure and uncertainty—not a generic “software MTBF.”
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Software/reliability engineer, release authority, service owner and mission owner.
- `CHEAP_PATH`: Use targeted functional, property, stress and regression tests when a numerical software failure-rate model will not change the decision.
- `CONTRARY_EVIDENCE`: For stable narrow programs with controlled profiles, SRGMs can support planning; transfer beyond those assumptions is weak.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A version- and profile-bound software functional-failure claim triangulated by targeted tests, field exposure and uncertainty—not a generic “software MTBF.”

**REQUIRED_PRECONDITIONS**
- `dependencies`: Current version/configuration, input/state distribution, failure oracle, exposure, fix history and dependency environment.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `VERY_HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MIXED`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `MODERATE`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `LOW_TO_MODERATE`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
Many growth models fit historical curves similarly yet extrapolate poorly; model selection after seeing data invites overfit.

**ANTI_CEREMONY_BOUNDARY**  
A software reliability growth chart is optional; representative evidence about the current executable behaviour is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate software reliability under an operational input profile?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P031 — User-journey and consumer-consequence service reliability</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Named consumer journey achieves correct, timely, sufficiently fresh/durable outcome over the relevant window and dependencies.
- `failure_mode`: Request-weighted average hides a small user cohort, tail latency, dependency path, stale data, partial outage or repeated short disruptions.
**MATURE_FORM**  
A small set of end-to-end, cohort-aware, consequence-linked measures with diagnostic drill-down and explicit blind spots.

**TRIGGER**  
Externally consumed software/service whose important outcomes span components, dependencies or multiple steps.

**CHEAP_PATH**  
For simple single-step services, one end-to-end functional probe plus incident review may be sufficient.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: User-journey and consumer-consequence service reliability
- `REQUIRED_FUNCTION`: Named consumer journey achieves correct, timely, sufficiently fresh/durable outcome over the relevant window and dependencies.
- `MISSION_OR_SERVICE`: Named consumer journey achieves correct, timely, sufficiently fresh/durable outcome over the relevant window and dependencies.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Request-weighted average hides a small user cohort, tail latency, dependency path, stale data, partial outage or repeated short disruptions.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: End users, mission/business owner, service owner and on-call operator.
- `CHEAP_PATH`: For simple single-step services, one end-to-end functional probe plus incident review may be sufficient.
- `MATURE_FORM`: A small set of end-to-end, cohort-aware, consequence-linked measures with diagnostic drill-down and explicit blind spots.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: User-journey and consumer-consequence service reliability
- `INITIATING_FAULT_OR_FAILURE`: Request-weighted average hides a small user cohort, tail latency, dependency path, stale data, partial outage or repeated short disruptions.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Request-weighted average hides a small user cohort, tail latency, dependency path, stale data, partial outage or repeated short disruptions.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Consumer definitions, telemetry across journey, privacy-preserving correlation, state correctness, dependency observability and denominator governance.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Define journey-level outcomes; stratify consumers and consequence; include tails/freshness/durability; measure dependency and degraded-state success.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: User-journey and consumer-consequence service reliability
- `TARGET_FAULTS_FAILURES`: Request-weighted average hides a small user cohort, tail latency, dependency path, stale data, partial outage or repeated short disruptions.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: A small set of end-to-end, cohort-aware, consequence-linked measures with diagnostic drill-down and explicit blind spots.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: User-journey and consumer-consequence service reliability
- `CLAIM`: A small set of end-to-end, cohort-aware, consequence-linked measures with diagnostic drill-down and explicit blind spots.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: End users, mission/business owner, service owner and on-call operator.
- `CHEAP_PATH`: For simple single-step services, one end-to-end functional probe plus incident review may be sufficient.
- `CONTRARY_EVIDENCE`: No single user-journey metric covers all consequences; qualitative incident evidence and targeted tests remain necessary.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A small set of end-to-end, cohort-aware, consequence-linked measures with diagnostic drill-down and explicit blind spots.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Consumer definitions, telemetry across journey, privacy-preserving correlation, state correctness, dependency observability and denominator governance.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE_TO_HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
User happiness is multidimensional and difficult to reduce to a ratio; measurement itself can be incomplete or inequitable.

**ANTI_CEREMONY_BOUNDARY**  
A dashboard or “golden signals” panel is not the property; current evidence that consumers receive required outcomes is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate user-journey and consumer-consequence service reliability?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P032 — SLI/SLO and error-budget governance as a scoped decision aid</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: A user/mission-relevant outcome remains within an agreed loss budget over a declared denominator/window, with action when exhausted.
- `failure_mode`: Easy metric chosen; time/event denominator mismatch; cohort/tail hidden; maintenance excluded; budget treated as permission; chronic exhaustion creates nonsense.
**MATURE_FORM**  
A revisable, consumer-grounded governance instrument used alongside incident, dependency and tail evidence—not a universal reliability score.

**TRIGGER**  
Repeatable online service with measurable consumer outcomes and cross-functional authority to act on budget state.

**CHEAP_PATH**  
Use direct incident/change judgement for small or low-volume services where a stable ratio is misleading.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: SLI/SLO and error-budget governance as a scoped decision aid
- `REQUIRED_FUNCTION`: A user/mission-relevant outcome remains within an agreed loss budget over a declared denominator/window, with action when exhausted.
- `MISSION_OR_SERVICE`: A user/mission-relevant outcome remains within an agreed loss budget over a declared denominator/window, with action when exhausted.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Easy metric chosen; time/event denominator mismatch; cohort/tail hidden; maintenance excluded; budget treated as permission; chronic exhaustion creates nonsense.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Service owner, product/change authority, on-call and users represented by the SLI.
- `CHEAP_PATH`: Use direct incident/change judgement for small or low-volume services where a stable ratio is misleading.
- `MATURE_FORM`: A revisable, consumer-grounded governance instrument used alongside incident, dependency and tail evidence—not a universal reliability score.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: SLI/SLO and error-budget governance as a scoped decision aid
- `CLAIM`: A revisable, consumer-grounded governance instrument used alongside incident, dependency and tail evidence—not a universal reliability score.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Service owner, product/change authority, on-call and users represented by the SLI.
- `CHEAP_PATH`: Use direct incident/change judgement for small or low-volume services where a stable ratio is misleading.
- `CONTRARY_EVIDENCE`: No robust multi-organisation evidence establishes one SLO formula or error-budget policy as universally optimal.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A revisable, consumer-grounded governance instrument used alongside incident, dependency and tail evidence—not a universal reliability score.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Reliable telemetry, user-journey mapping, stakeholder agreement, release authority, dependency awareness and review cadence.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
Boolean ratios fit request/response better than many other services; correct error-budget response and alert thresholds remain contested.

**ANTI_CEREMONY_BOUNDARY**  
The SLO dashboard and error-budget ritual are optional; the property is a valid current decision boundary and agreed response.

**POSSIBLE_CONFLICTING_PROPERTY**  
SLO strictness/reliability protection versus change velocity and useful experimentation.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate sli/slo and error-budget governance as a scoped decision aid?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P033 — End-to-end health checks and symptom-versus-cause separation</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Detect end-to-end functional loss quickly while preserving a separate evidence path for causal diagnosis.
- `failure_mode`: Shallow probe; cached/static response; monitor bypasses dependency/state/authentication; probe shares failure; symptom automatically labelled root cause.
**MATURE_FORM**  
A documented coverage stack: user/mission outcome detection, diagnostic signals, independent probe health and post-recovery validation.

**TRIGGER**  
Remote automated service, failover, load balancer health, readiness/liveness, synthetic transactions or auto-remediation.

**CHEAP_PATH**  
A direct user-visible transaction is often cheaper and stronger than many internal health bits.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: End-to-end health checks and symptom-versus-cause separation
- `REQUIRED_FUNCTION`: Detect end-to-end functional loss quickly while preserving a separate evidence path for causal diagnosis.
- `MISSION_OR_SERVICE`: Detect end-to-end functional loss quickly while preserving a separate evidence path for causal diagnosis.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Shallow probe; cached/static response; monitor bypasses dependency/state/authentication; probe shares failure; symptom automatically labelled root cause.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: On-call operator, automated traffic manager, incident commander and users.
- `CHEAP_PATH`: A direct user-visible transaction is often cheaper and stronger than many internal health bits.
- `MATURE_FORM`: A documented coverage stack: user/mission outcome detection, diagnostic signals, independent probe health and post-recovery validation.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: End-to-end health checks and symptom-versus-cause separation
- `INITIATING_FAULT_OR_FAILURE`: Shallow probe; cached/static response; monitor bypasses dependency/state/authentication; probe shares failure; symptom automatically labelled root cause.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Shallow probe; cached/static response; monitor bypasses dependency/state/authentication; probe shares failure; symptom automatically labelled root cause.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Representative journey, safe test account/data, independent monitoring path, timing and known blind spots.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Use layered probes: end-to-end outcome for impact, component/dependency signals for diagnosis; test probe coverage/failure; validate after recovery.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: End-to-end health checks and symptom-versus-cause separation
- `TARGET_FAULTS_FAILURES`: Shallow probe; cached/static response; monitor bypasses dependency/state/authentication; probe shares failure; symptom automatically labelled root cause.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: A documented coverage stack: user/mission outcome detection, diagnostic signals, independent probe health and post-recovery validation.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Representative journey, safe test account/data, independent monitoring path, timing and known blind spots.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Deep probes can be costly, create load or mutate state; they cannot cover all semantic outcomes.

**ANTI_CEREMONY_BOUNDARY**  
A green checkmark is not the property; observed required function plus understood coverage is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate end-to-end health checks and symptom-versus-cause separation?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- Can the health check remain green while an important user or mission path is unavailable, stale, corrupt or capacity-starved?

</details>
<details><summary><strong>ERM-P034 — Explicit dependency, correlation and hidden single-point mapping</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Every dependency necessary for the critical function or its recovery is identified with consequence, alternatives and correlation.
- `failure_mode`: Unknown transitive dependency; fallback uses same provider/control; SLA substitutes for observed performance; human/on-call or logistics bottleneck omitted.
**MATURE_FORM**  
A decision-focused dependency model refreshed by telemetry and incidents, including recovery dependencies and credible fallback evidence.

**TRIGGER**  
End-to-end service, outsourced/supplier component, multi-region design, recovery plan, shared platform or long logistics chain.

**CHEAP_PATH**  
For simple systems, trace one critical user/mission path and its recovery path rather than build a universal service map.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Explicit dependency, correlation and hidden single-point mapping
- `REQUIRED_FUNCTION`: Every dependency necessary for the critical function or its recovery is identified with consequence, alternatives and correlation.
- `MISSION_OR_SERVICE`: Every dependency necessary for the critical function or its recovery is identified with consequence, alternatives and correlation.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Unknown transitive dependency; fallback uses same provider/control; SLA substitutes for observed performance; human/on-call or logistics bottleneck omitted.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Architect, service/fleet owner, supplier manager, operator, continuity planner and mission owner.
- `CHEAP_PATH`: For simple systems, trace one critical user/mission path and its recovery path rather than build a universal service map.
- `MATURE_FORM`: A decision-focused dependency model refreshed by telemetry and incidents, including recovery dependencies and credible fallback evidence.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Explicit dependency, correlation and hidden single-point mapping
- `INITIATING_FAULT_OR_FAILURE`: Unknown transitive dependency; fallback uses same provider/control; SLA substitutes for observed performance; human/on-call or logistics bottleneck omitted.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Unknown transitive dependency; fallback uses same provider/control; SLA substitutes for observed performance; human/on-call or logistics bottleneck omitted.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Telemetry/tracing, contracts plus observed data, architecture and support knowledge, ownership and change notifications.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Discover runtime and organisational dependencies; classify criticality/failure domains; test fallback; record correlated change/maintenance; monitor supplier performance.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Explicit dependency, correlation and hidden single-point mapping
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: A decision-focused dependency model refreshed by telemetry and incidents, including recovery dependencies and credible fallback evidence.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Telemetry/tracing, contracts plus observed data, architecture and support knowledge, ownership and change notifications.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `VERY_HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Maps go stale quickly and can become inventory ceremony; causal dependence is richer than static edges.

**ANTI_CEREMONY_BOUNDARY**  
A service map is not the property; knowing which shared dependency can defeat required function and what is done about it is.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate explicit dependency, correlation and hidden single-point mapping?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?

</details>
<details><summary><strong>ERM-P035 — Hypothesis-bound fault injection and chaos experimentation</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Discriminate a live reliability uncertainty for a specified fault, profile, boundary and decision without causing disproportionate harm.
- `failure_mode`: Random breakage; nonrepresentative fault; weak oracle; no decision consumer; production risk exceeds value; repeated ritual after claim already established.
**MATURE_FORM**  
A sparse portfolio of claim-bound experiments chosen by expected information value and closed through recovery validation and engineering action.

**TRIGGER**  
Material integrated uncertainty not cheaply resolved by static analysis, simulation, staging or direct functional test.

**CHEAP_PATH**  
Use unit/integration test, simulation, replay or nonproduction exercise when it resolves the same uncertainty more safely/cheaply.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Hypothesis-bound fault injection and chaos experimentation
- `REQUIRED_FUNCTION`: Discriminate a live reliability uncertainty for a specified fault, profile, boundary and decision without causing disproportionate harm.
- `MISSION_OR_SERVICE`: Discriminate a live reliability uncertainty for a specified fault, profile, boundary and decision without causing disproportionate harm.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Random breakage; nonrepresentative fault; weak oracle; no decision consumer; production risk exceeds value; repeated ritual after claim already established.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Service/mission owner, operator, reliability engineer and change authority.
- `CHEAP_PATH`: Use unit/integration test, simulation, replay or nonproduction exercise when it resolves the same uncertainty more safely/cheaply.
- `MATURE_FORM`: A sparse portfolio of claim-bound experiments chosen by expected information value and closed through recovery validation and engineering action.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Hypothesis-bound fault injection and chaos experimentation
- `INITIATING_FAULT_OR_FAILURE`: Random breakage; nonrepresentative fault; weak oracle; no decision consumer; production risk exceeds value; repeated ritual after claim already established.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Random breakage; nonrepresentative fault; weak oracle; no decision consumer; production risk exceeds value; repeated ritual after claim already established.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Containment, observability, recovery readiness, representative load/state, authorisation, abort/fallback and post-experiment analysis.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: State hypothesis/steady-state metric; choose representative fault and blast radius; predefine abort; observe full recovery/postconditions; record decision/update.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Hypothesis-bound fault injection and chaos experimentation
- `CLAIM`: A sparse portfolio of claim-bound experiments chosen by expected information value and closed through recovery validation and engineering action.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Service/mission owner, operator, reliability engineer and change authority.
- `CHEAP_PATH`: Use unit/integration test, simulation, replay or nonproduction exercise when it resolves the same uncertainty more safely/cheaply.
- `CONTRARY_EVIDENCE`: A successful experiment proves only the tested conditions; it never establishes general resilience.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A sparse portfolio of claim-bound experiments chosen by expected information value and closed through recovery validation and engineering action.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Containment, observability, recovery readiness, representative load/state, authorisation, abort/fallback and post-experiment analysis.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE_TO_HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `LOW_TO_MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH_FOR_TESTED_CLAIM`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `MODERATE_TO_HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `LOW_WITHOUT_MATCH`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `HIGH`

**CRITICISMS**  
Industrial evidence is advocacy-heavy; systematic review still finds evaluation and adoption gaps; production experimentation creates ethical/operational risk.

**ANTI_CEREMONY_BOUNDARY**  
“Chaos day,” monkey tooling or periodic failure ritual is not the property; decision-relevant falsification is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Failure-learning value versus production/mission risk and evidence cost.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate hypothesis-bound fault injection and chaos experimentation?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?
- Will another fault-injection experiment discriminate a live uncertainty and change a decision, or would it be ceremony?

</details>
<details><summary><strong>ERM-P036 — Overload-aware recovery: capacity margin, load shedding and bounded retries</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Protect priority function and recover without unstable positive feedback or exhaustion of the remaining fault-tolerant capacity.
- `failure_mode`: Retry storm; thundering herd; failover target underprovisioned; cache cold start; load shedding removes critical work; no admission control.
**MATURE_FORM**  
A measured stability envelope and failure-mode-specific overload policy, including consumer consequences and recovery postconditions.

**TRIGGER**  
Elastic/queued services, failover, regional loss, dependency slowdown, mass restart or bursty demand.

**CHEAP_PATH**  
Reject clearly and early rather than queue/retry when capacity is exhausted and work is safely repeatable later.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Overload-aware recovery: capacity margin, load shedding and bounded retries
- `REQUIRED_FUNCTION`: Protect priority function and recover without unstable positive feedback or exhaustion of the remaining fault-tolerant capacity.
- `MISSION_OR_SERVICE`: Protect priority function and recover without unstable positive feedback or exhaustion of the remaining fault-tolerant capacity.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Retry storm; thundering herd; failover target underprovisioned; cache cold start; load shedding removes critical work; no admission control.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Operator, service owner, priority users and incident commander.
- `CHEAP_PATH`: Reject clearly and early rather than queue/retry when capacity is exhausted and work is safely repeatable later.
- `MATURE_FORM`: A measured stability envelope and failure-mode-specific overload policy, including consumer consequences and recovery postconditions.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Overload-aware recovery: capacity margin, load shedding and bounded retries
- `INITIATING_FAULT_OR_FAILURE`: Retry storm; thundering herd; failover target underprovisioned; cache cold start; load shedding removes critical work; no admission control.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Retry storm; thundering herd; failover target underprovisioned; cache cold start; load shedding removes critical work; no admission control.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Demand/capacity observability, priority semantics, idempotency, queue limits, fallback and consumer communication.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Reserve margin; classify load; cap/constrain retries; exponential backoff/jitter; circuit break; shed by priority; ramp recovery; test cold/failed capacity.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Overload-aware recovery: capacity margin, load shedding and bounded retries
- `INITIATING_FAILURE`: Retry storm; thundering herd; failover target underprovisioned; cache cold start; load shedding removes critical work; no admission control.
- `RECOVERY_ACTION`: Reserve margin; classify load; cap/constrain retries; exponential backoff/jitter; circuit break; shed by priority; ramp recovery; test cold/failed capacity.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Protect priority function and recover without unstable positive feedback or exhaustion of the remaining fault-tolerant capacity.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: A measured stability envelope and failure-mode-specific overload policy, including consumer consequences and recovery postconditions.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Demand/capacity observability, priority semantics, idempotency, queue limits, fallback and consumer communication.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Spare capacity costs money/energy; load shedding can externalise harm and obscure underinvestment.

**ANTI_CEREMONY_BOUNDARY**  
A circuit-breaker library or autoscaler is not the property; stable protected operation under the target loss is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Spare capacity and load shedding versus cost/efficiency and service completeness.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate overload-aware recovery: capacity margin, load shedding and bounded retries?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?

</details>
<details><summary><strong>ERM-P037 — Observability and evidence preservation during failure and recovery</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Retain sufficient trustworthy evidence to determine impact, state, likely causes, actions and post-recovery correctness within time/privacy constraints.
- `failure_mode`: Logs share failed control plane; clocks diverge; restart erases state; auto-remediation loops; high volume drops key evidence; recovery contaminates artefacts.
**MATURE_FORM**  
Decision-focused observability resilient to the target failure, with known coverage, integrity, retention and evidence-preserving automation.

**TRIGGER**  
Complex automated systems, correlated outages, remote repair, stateful recovery or rare high-consequence events.

**CHEAP_PATH**  
For simple deterministic faults, record the minimal causal/action evidence rather than instrument everything.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Observability and evidence preservation during failure and recovery
- `REQUIRED_FUNCTION`: Retain sufficient trustworthy evidence to determine impact, state, likely causes, actions and post-recovery correctness within time/privacy constraints.
- `MISSION_OR_SERVICE`: Retain sufficient trustworthy evidence to determine impact, state, likely causes, actions and post-recovery correctness within time/privacy constraints.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Logs share failed control plane; clocks diverge; restart erases state; auto-remediation loops; high volume drops key evidence; recovery contaminates artefacts.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Operator, maintainer, incident investigator, design owner and return-to-service authority.
- `CHEAP_PATH`: For simple deterministic faults, record the minimal causal/action evidence rather than instrument everything.
- `MATURE_FORM`: Decision-focused observability resilient to the target failure, with known coverage, integrity, retention and evidence-preserving automation.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Observability and evidence preservation during failure and recovery
- `INITIATING_FAULT_OR_FAILURE`: Logs share failed control plane; clocks diverge; restart erases state; auto-remediation loops; high volume drops key evidence; recovery contaminates artefacts.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Logs share failed control plane; clocks diverge; restart erases state; auto-remediation loops; high volume drops key evidence; recovery contaminates artefacts.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Independent power/network/storage where warranted, data quality, clocks, access, retention, privacy and incident procedures.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Independent/remote telemetry paths; durable event/action records; time/identity correlation; bounded snapshots; evidence-preserving recovery mode; privacy/access governance.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `PROPERTY`: Observability and evidence preservation during failure and recovery
- `TARGET_FAULTS_FAILURES`: Logs share failed control plane; clocks diverge; restart erases state; auto-remediation loops; high volume drops key evidence; recovery contaminates artefacts.
- `OBSERVABLES`: Function outputs, timing, state, residuals, dependency signals and user/mission outcomes.
- `DETECTION_COVERAGE`: Coverage is stated for an enumerated fault/failure population, operating mode and latency window.
- `FALSE_ALARM_COST`: Unnecessary maintenance, failover, shutdown, operator load or customer disruption.
- `MISSED_DETECTION_COST`: Continued propagation, latent damage, missed recovery window or false assurance.
- `ISOLATION_RESOLUTION`: Replaceable unit, functional region, dependency or ambiguity group appropriate to the action.
- `AMBIGUITY_GROUPS`: Plausible causes producing the same symptom are preserved until discriminated.
- `LATENCY`: Detection and isolation time are bounded relative to propagation and recovery deadlines.
- `CONFIDENCE_CALIBRATION`: Uncertainty, thresholds, drift and out-of-distribution conditions are exposed.
- `OPERATOR_OR_AUTOMATION_ACTION`: Action is authority-bounded, reversible where feasible and matched to diagnosis confidence.
- `RECOVERY_COVERAGE`: A detected fault counts only if the prescribed action restores or contains the target failure with known coverage.
- `MATURE_FORM`: Decision-focused observability resilient to the target failure, with known coverage, integrity, retention and evidence-preserving automation.

**RECOVERY_RESTORATION_PROFILE**
- `PROPERTY`: Observability and evidence preservation during failure and recovery
- `INITIATING_FAILURE`: Logs share failed control plane; clocks diverge; restart erases state; auto-remediation loops; high volume drops key evidence; recovery contaminates artefacts.
- `RECOVERY_ACTION`: Independent/remote telemetry paths; durable event/action records; time/identity correlation; bounded snapshots; evidence-preserving recovery mode; privacy/access governance.
- `AUTHORITY_SOURCE`: The designated current configuration/state authority and authorised operator or controller.
- `CHECKPOINT_BACKUP_SPARE_OR_ALTERNATE`: Declared checkpoint, replica, backup, spare, rebuild source or manual workaround.
- `RPO_OR_STATE_LOSS_BOUND`: Explicit allowed state/data loss or “none” for state-continuous functions.
- `RTO_OR_RESTORATION_BOUND`: Explicit time-to-restoration bound including diagnosis, logistics, repair and validation.
- `STATE_RECONCILIATION`: Resolve divergent, stale, partial or replayed state before authoritative service resumes.
- `FUNCTIONAL_POSTCONDITIONS`: Retain sufficient trustworthy evidence to determine impact, state, likely causes, actions and post-recovery correctness within time/privacy constraints.
- `DATA_STATE_POSTCONDITIONS`: Integrity, completeness, freshness, ordering and authority appropriate to the mission.
- `DEPENDENCY_POSTCONDITIONS`: Critical dependencies and capacity are verified rather than assumed from local restart.
- `VALIDATION`: Independent end-to-end functional and state checks under representative demand.
- `RETURN_TO_SERVICE_AUTHORITY`: Named human or automated authority with explicit acceptance criteria.
- `ROLLBACK_OR_FALLBACK`: A bounded fallback when restoration validation fails or the original cause persists.
- `MATURE_FORM`: Decision-focused observability resilient to the target failure, with known coverage, integrity, retention and evidence-preserving automation.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Observability and evidence preservation during failure and recovery
- `CLAIM`: Decision-focused observability resilient to the target failure, with known coverage, integrity, retention and evidence-preserving automation.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Operator, maintainer, incident investigator, design owner and return-to-service authority.
- `CHEAP_PATH`: For simple deterministic faults, record the minimal causal/action evidence rather than instrument everything.
- `CONTRARY_EVIDENCE`: In some failures independent physical inspection or direct test is more informative than extensive telemetry.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: Decision-focused observability resilient to the target failure, with known coverage, integrity, retention and evidence-preserving automation.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Independent power/network/storage where warranted, data quality, clocks, access, retention, privacy and incident procedures.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Enumerated fault/failure population, observable signals, calibrated thresholds, isolation resolution, false-alarm and missed-detection costs.
- `recovery_or_repair`: A valid recovery source, authorised action, state/data reconciliation, dependency readiness and independently checked return-to-service postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `VERY_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Observability can be costly, intrusive and security/privacy-sensitive; more data does not guarantee diagnosis.

**ANTI_CEREMONY_BOUNDARY**  
A logging stack is not the property; reliable evidence for live decisions and recurrence learning is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Diagnostic evidence and transparency versus privacy, legal constraints and rapid restoration.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate observability and evidence preservation during failure and recovery?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Which enumerated failures can the diagnostic detect and isolate within the required latency, and what are the false-positive and false-negative costs?
- Does recovery close on independently checked required function, state and dependency postconditions rather than process restart or procedure completion?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P038 — Proportional cheap path and deterministic functional check</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Obtain enough trustworthy evidence for the actual decision at proportionate cost and risk.
- `failure_mode`: Mandatory artefact regardless of consequence; model precision without decision sensitivity; repeated test after result cannot change action; analysis delays simple fix.
**MATURE_FORM**  
A documented minimum-sufficient path with escalation criteria, not a blanket waiver or blanket process.

**TRIGGER**  
Every proposed reliability activity; especially low-consequence, reversible, small-scope or already-observable work.

**CHEAP_PATH**  
This property is the cheap path: simplest evidence/mechanism that resolves the live decision while preserving critical assumptions.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Proportional cheap path and deterministic functional check
- `REQUIRED_FUNCTION`: Obtain enough trustworthy evidence for the actual decision at proportionate cost and risk.
- `MISSION_OR_SERVICE`: Obtain enough trustworthy evidence for the actual decision at proportionate cost and risk.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Mandatory artefact regardless of consequence; model precision without decision sensitivity; repeated test after result cannot change action; analysis delays simple fix.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: Decision owner, mission/service owner and engineering team.
- `CHEAP_PATH`: This property is the cheap path: simplest evidence/mechanism that resolves the live decision while preserving critical assumptions.
- `MATURE_FORM`: A documented minimum-sufficient path with escalation criteria, not a blanket waiver or blanket process.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Proportional cheap path and deterministic functional check
- `CLAIM`: A documented minimum-sufficient path with escalation criteria, not a blanket waiver or blanket process.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: Decision owner, mission/service owner and engineering team.
- `CHEAP_PATH`: This property is the cheap path: simplest evidence/mechanism that resolves the live decision while preserving critical assumptions.
- `CONTRARY_EVIDENCE`: High-consequence irreversible missions often justify expensive evidence even when probability is low.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: A documented minimum-sufficient path with escalation criteria, not a blanket waiver or blanket process.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Clear decision consumer, consequence, reversibility, uncertainty and authority to tailor.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE_TO_HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `MODERATE`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `MODERATE`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Proportionality is judgement-sensitive and can rationalise weak assurance; explicit rationale and triggers for escalation are needed.

**ANTI_CEREMONY_BOUNDARY**  
No named artefact is privileged; only the evidence/mechanism needed for the decision survives.

**POSSIBLE_CONFLICTING_PROPERTY**  
Proportional assurance cost versus the risk of under-analysing apparently simple work.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate proportional cheap path and deterministic functional check?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?
- Could a cheaper deterministic end-to-end functional check establish the needed state with less modelling and operational risk?

</details>
<details><summary><strong>ERM-P039 — Retirement of stale controls, metrics, support and reliability claims</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: Only current, decision-relevant reliability controls and support capabilities govern the current system.
- `failure_mode`: Obsolete spare/tool; unsupported dependency; stale profile; dead alert; inherited “nine”; old backup format; handbook rate for changed technology.
**MATURE_FORM**  
Every material reliability control has a current consumer, evidence basis, configuration scope, expiry and safe retirement/replacement path.

**TRIGGER**  
Technology/configuration/profile/consumer change, repeated false alarms, unused metric, support deprecation or expired evidence.

**CHEAP_PATH**  
Delete a stale metric/control when no consumer or decision can be named; retain a simple direct check if still useful.

**MISSION_RELIABILITY_PROFILE**
- `PROPERTY`: Retirement of stale controls, metrics, support and reliability claims
- `REQUIRED_FUNCTION`: Only current, decision-relevant reliability controls and support capabilities govern the current system.
- `MISSION_OR_SERVICE`: Only current, decision-relevant reliability controls and support capabilities govern the current system.
- `OPERATING_PROFILE`: Declared demands, workload mix, duty cycle, mode changes and maintenance states.
- `ENVIRONMENT`: Declared physical, software, organisational and dependency environment.
- `FAILURE_DEFINITION`: Obsolete spare/tool; unsupported dependency; stale profile; dead alert; inherited “nine”; old backup format; handbook rate for changed technology.
- `DEGRADED_ACCEPTABLE_STATE`: Only states explicitly accepted by mission/consumer criteria; otherwise none.
- `MISSION_TIME_OR_DEMAND`: Specified interval, number of demands or service-measurement window.
- `CONSUMER`: System/service owner, maintainer, operator, procurement and assurance authority.
- `CHEAP_PATH`: Delete a stale metric/control when no consumer or decision can be named; retain a simple direct check if still useful.
- `MATURE_FORM`: Every material reliability control has a current consumer, evidence basis, configuration scope, expiry and safe retirement/replacement path.

**FAILURE_PROPAGATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct propagation claim is made by this candidate.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property does not itself claim redundancy benefit; any redundant implementation must invoke ERM-P008/ERM-P009.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `PROPERTY`: Retirement of stale controls, metrics, support and reliability claims
- `CLAIM`: Every material reliability control has a current consumer, evidence basis, configuration scope, expiry and safe retirement/replacement path.
- `POPULATION_OR_DENOMINATOR`: Declared units, missions, demands, requests, users, time windows or recurrent-event process.
- `CONFIGURATION_IDENTITY`: Exact hardware, software, data, model, dependency and procedure versions.
- `OPERATIONAL_PROFILE`: Representative demand/workload/environment with consequence-important rare cases identified.
- `TEST_OR_OBSERVATION_DESIGN`: Predeclared sampling/censoring, failure scoring, exposure and stopping rules.
- `MODEL`: Model selected for the stated estimand: life distribution, recurrent-event process, binomial demand, availability state model or direct functional check.
- `ASSUMPTIONS`: Independence, stationarity, censoring, repair effectiveness, acceleration, coverage and representativeness are explicit.
- `CONFIDENCE_OR_UNCERTAINTY`: Intervals, posterior uncertainty or bounded qualitative confidence; point estimates alone are insufficient.
- `CENSORING_AND_MISSINGNESS`: Right/interval censoring, unreported events, lost telemetry and excluded windows are recorded.
- `COVERAGE`: Claim coverage is limited to tested/observed failure modes, environments and paths.
- `DECISION_OR_CONSUMER`: System/service owner, maintainer, operator, procurement and assurance authority.
- `CHEAP_PATH`: Delete a stale metric/control when no consumer or decision can be named; retain a simple direct check if still useful.
- `CONTRARY_EVIDENCE`: Long-lived controls may encode rare lessons; deletion without historical analysis can reintroduce old failure modes.
- `EXPIRY_OR_FRESHNESS`: Evidence expires when configuration, profile, environment, support organisation or dependencies materially change.
- `MATURE_FORM`: Every material reliability control has a current consumer, evidence basis, configuration scope, expiry and safe retirement/replacement path.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Inventory and ownership, configuration/dependency change signals, evidence lineage and authority to retire contractual/process residue.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: No redundancy premise is needed; if redundancy appears in the implementation, common-cause and switchover assumptions must be analysed separately.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: Access, modularity, safe isolation, procedures, test equipment, spares, tools, skills, logistics, configuration data and time under actual field conditions.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `MODERATE`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `MODERATE`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH`
- `DEMONSTRATION_TEST_STRENGTH`: `MODERATE`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `MODERATE_TO_HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `HIGH`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `LOW_TO_MODERATE`
- `TRANSFERABILITY_STRENGTH`: `HIGH`
- `ASSUMPTION_SENSITIVITY`: `HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `MODERATE`

**CRITICISMS**  
Frequent change can erode comparability and institutional memory; retirement needs archival trace and consequence check.

**ANTI_CEREMONY_BOUNDARY**  
Keeping a metric because it exists is ceremony; deliberate retention or retirement is the property.

**POSSIBLE_CONFLICTING_PROPERTY**  
No single universal conflict; check local cost, consequence, coupling and competing system objectives.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate retirement of stale controls, metrics, support and reliability claims?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- What population, denominator, model, confidence, censoring rule and expiry condition bound the reliability claim?

</details>
<details><summary><strong>ERM-P040 — Design diversity as conditional common-mode mitigation</strong></summary>

**REQUIRED_FUNCTION_OR_FAILURE_MODE**
- `required_function_or_mission`: At least one/adjudicated implementation remains correct for the target input/fault class without shared specification/model/tool failure.
- `failure_mode`: Common specification ambiguity; difficult inputs induce similar errors; shared algorithm/library/data/model; voter/acceptance test wrong; diversity overwhelms maintenance.
**MATURE_FORM**  
A quantified/argued diversity case naming which common modes are reduced, which remain shared, adjudication coverage and maintenance/recovery consequences.

**TRIGGER**  
Systematic design/software/model failure dominates and consequence justifies multiple implementations.

**CHEAP_PATH**  
Prefer one simple implementation plus strong specification/tests when diversity cost and shared assumptions erase benefit.

**MISSION_RELIABILITY_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is a supporting mechanism or rejected proxy rather than a standalone mission claim.

**FAILURE_PROPAGATION_PROFILE**
- `PROPERTY`: Design diversity as conditional common-mode mitigation
- `INITIATING_FAULT_OR_FAILURE`: Common specification ambiguity; difficult inputs induce similar errors; shared algorithm/library/data/model; voter/acceptance test wrong; diversity overwhelms maintenance.
- `LOCAL_EFFECT`: Loss, corruption, delay, false indication or degraded performance at the initiating item.
- `NEXT_LEVEL_EFFECT`: Effect on the enclosing function, dependency path or maintenance process.
- `END_EFFECT`: Common specification ambiguity; difficult inputs induce similar errors; shared algorithm/library/data/model; voter/acceptance test wrong; diversity overwhelms maintenance.
- `PROPAGATION_PATH`: Functional, physical, state, timing, control, resource or organisational coupling.
- `CONTAINMENT_BOUNDARY`: A declared fault-containment region or explicit stop/degradation boundary.
- `DEPENDENCIES`: Clear specification/oracle, adjudication, independent causal pathways, configuration control, joint-failure evidence and maintenance capacity.
- `COMMON_CAUSE_OR_SHARED_COUPLING`: Shared specification, environment, supplier, control plane, state, maintenance or operator path must be challenged.
- `LATENT_CONDITION`: Standby, monitoring, repair or dependency defects may remain latent until demand.
- `DETECTION`: Outcome- or function-relevant observation, not a component heartbeat alone.
- `CONTROL`: Diversify selected causal dimensions; analyse shared assumptions; use independent evidence/teams/tools where valuable; test coincident errors; preserve diagnosability and update compatibility.
- `RESIDUAL_RISK`: Unmodelled combinations, dependence, coverage gaps and changed configuration remain.

**REDUNDANCY_COMMON_CAUSE_PROFILE**
- `PROPERTY`: Design diversity as conditional common-mode mitigation
- `REDUNDANCY_FORM`: Active, standby, voting, diverse, replicated or alternate-path redundancy as explicitly declared.
- `CLAIMED_TOLERANCE`: The specified number/class of faults tolerated while meeting required function or an accepted degraded state.
- `FAILURE_DOMAINS`: Physical, power, network, control-plane, state, software, supplier, operator and maintenance domains.
- `INDEPENDENCE_EVIDENCE`: Evidence must address shared causes rather than infer independence from copy count or labels.
- `COMMON_CAUSE_COUPLINGS`: Specification, design, implementation, environment, supplier, maintenance, configuration and operational coupling.
- `STANDBY_LATENCY_OR_DORMANCY`: Dormant faults, activation delay and cold/warm/hot readiness are measured when applicable.
- `SWITCHOVER_COVERAGE`: Detection, decision, transfer, state synchronisation and post-transfer functional success.
- `STATE_CONSISTENCY`: The takeover state and authority must be current, complete and semantically valid.
- `DEGRADED_MODE`: Declared reduced capability and exit conditions.
- `TEST_OR_FIELD_EVIDENCE`: Representative failover/failure tests plus field or incident evidence where available.
- `MATURE_FORM`: A quantified/argued diversity case naming which common modes are reduced, which remain shared, adjudication coverage and maintenance/recovery consequences.

**DIAGNOSTIC_COVERAGE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The candidate is not a diagnostic claim; outcome observation may still be required by its evidence profile.

**RECOVERY_RESTORATION_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: No distinct recovery claim is made by this candidate.

**RELIABILITY_EVIDENCE_PROFILE**
- `APPLICABLE`: `false`
- `REASON`: The property is primarily a design/operation mechanism; its validation still follows ERM-P026–P029.

**REQUIRED_PRECONDITIONS**
- `dependencies`: Clear specification/oracle, adjudication, independent causal pathways, configuration control, joint-failure evidence and maintenance capacity.
- `operational_profile`: A declared and sufficiently representative operating profile, environment, duty cycle, mission phase and maintenance state.
- `failure_model`: A failure model appropriate to the estimand; distinguish non-repairable life, recurrent repairable events, demand failures, software activation and service outcomes.
- `redundancy_common_cause`: Credible failure-domain independence, common-cause analysis, standby condition, switchover coverage and state compatibility.
- `diagnostic_coverage`: Observable functional outcomes sufficient to determine whether the claimed property actually holds.
- `recovery_or_repair`: No recovery premise is inherent; any claim that depends on restoration must invoke explicit recovery postconditions.
- `maintainability`: The design and support system must not make verification or corrective action infeasible.

**EVIDENCE_STRENGTH**
- `HISTORICAL_PROVENANCE_STRENGTH`: `HIGH`
- `FORMAL_OR_PROBABILISTIC_STRENGTH`: `HIGH`
- `LIFE_DATA_OR_FIELD_STRENGTH`: `HIGH_FOR_SOFTWARE_EXPERIMENT`
- `DEMONSTRATION_TEST_STRENGTH`: `HIGH`
- `INCIDENT_OR_FAILURE_CASE_STRENGTH`: `HIGH`
- `OPERATIONAL_PRACTICE_STRENGTH`: `MODERATE`
- `REPLICATION_OR_MULTI_STUDY_STRENGTH`: `MODERATE`
- `TRANSFERABILITY_STRENGTH`: `CONTEXT_DEPENDENT`
- `ASSUMPTION_SENSITIVITY`: `VERY_HIGH`
- `CONTRARY_EVIDENCE_STRENGTH`: `VERY_HIGH`

**CRITICISMS**  
Knight–Leveson and Eckhardt–Lee directly undermine naïve independence; “different code” is not “independent failure.”

**ANTI_CEREMONY_BOUNDARY**  
Separate teams or languages are not the property; reduced joint failure for identified causes is.

**POSSIBLE_CONFLICTING_PROPERTY**  
Design diversity versus maintainability, verification cost and shared-specification error.

**QUESTIONS_FOR_REPOSITORY_AUDIT**
- Does the target define the required function, failure threshold, consumer and operating conditions needed to evaluate design diversity as conditional common-mode mitigation?
- Is the evidence for this property bound to the current configuration and a representative operational profile rather than inherited from a label, template or prior version?
- Are the supposed redundant channels actually separate failure domains, and is detection, switchover, state transfer and degraded capacity covered?

</details>

## Required population partitions

### CEREMONIES_TO_NOT_BLINDLY_ADOPT

- ERM-P041 MTBF as a universal scalar
- ERM-P042 “five nines” without scope/denominator
- ERM-P044 handbook prediction presented as field proof
- ERM-P045 completed FMEA as control proof
- ERM-P046 backup-presence badge
- ERM-P047 one-off failover/DR pass
- ERM-P048 incident-count target
- ERM-P049 local green health check
- ERM-P050 unbound chaos day
- ERM-P053 reliability-growth curve as causal certificate
- ERM-P054 zero-failure badge
- ERM-P055 “AI-powered reliability” branding

### CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

- Low-consequence, reversible work where a direct functional check establishes the needed state.
- Stable simple items for which elaborate stochastic or fault-tree models would not change a decision.
- Fault injection when no live uncertainty, decision consumer, safe abort or representative fault hypothesis exists.
- Predictive maintenance where no observable precursor or actionable lead time exists.
- Redundancy where shared failure domains dominate and a simpler robust component or recovery path is cheaper and safer.
- Probabilistic demonstration when deterministic inspection or functional proof can establish the required condition.

### PROPERTIES_REQUIRING_OPERATIONAL_PROFILE

- ERM-P001
- ERM-P002
- ERM-P003
- ERM-P005
- ERM-P014
- ERM-P022
- ERM-P023
- ERM-P026
- ERM-P027
- ERM-P028
- ERM-P030
- ERM-P031
- ERM-P032
- ERM-P033
- ERM-P035
- ERM-P036
- ERM-P039
- ERM-P040

### PROPERTIES_REQUIRING_COMMON_CAUSE_ANALYSIS

- ERM-P007
- ERM-P008
- ERM-P009
- ERM-P010
- ERM-P014
- ERM-P016
- ERM-P017
- ERM-P018
- ERM-P034
- ERM-P036
- ERM-P040

### PROPERTIES_REQUIRING_DIAGNOSTIC_COVERAGE

- ERM-P007
- ERM-P009
- ERM-P010
- ERM-P011
- ERM-P012
- ERM-P013
- ERM-P014
- ERM-P016
- ERM-P017
- ERM-P018
- ERM-P019
- ERM-P021
- ERM-P023
- ERM-P024
- ERM-P025
- ERM-P033
- ERM-P035
- ERM-P036
- ERM-P037
- ERM-P055

### PROPERTIES_REQUIRING_RECOVERY_OR_REPAIR_EVIDENCE

- ERM-P009
- ERM-P010
- ERM-P014
- ERM-P015
- ERM-P016
- ERM-P017
- ERM-P018
- ERM-P019
- ERM-P020
- ERM-P021
- ERM-P024
- ERM-P025
- ERM-P031
- ERM-P033
- ERM-P034
- ERM-P035
- ERM-P036
- ERM-P037
- ERM-P039
- ERM-P040

### PROPERTIES_WITH_STRONG_MODEL_BUT_WEAK_FIELD_TRANSFER

- ERM-P009 redundancy formulae under independence
- ERM-P022 age-based policy models outside established mechanisms
- ERM-P026 zero-/few-failure demonstrations beyond their designed population
- ERM-P027 accelerated tests beyond the validated acceleration mechanism
- ERM-P040 diversity models where development/specification dependence is unknown

### PROPERTIES_WITH_STRONG_FIELD_OR_INCIDENT_SUPPORT

- ERM-P001
- ERM-P003
- ERM-P004
- ERM-P005
- ERM-P006
- ERM-P008
- ERM-P009
- ERM-P016
- ERM-P017
- ERM-P020
- ERM-P021
- ERM-P025
- ERM-P031
- ERM-P033
- ERM-P034
- ERM-P036
- ERM-P037

### PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

- ERM-P023 predictive maintenance transfer and net decision value
- ERM-P032 error-budget effects outside well-instrumented service organisations
- ERM-P035 chaos-engineering effectiveness beyond individual case evidence
- ERM-P040 software design-diversity independence
- ERM-P055 autonomous/agentic diagnosis and remediation as net dependability improvement

### UNRESOLVED_PROPERTIES

- ERM-P055 remains domain-specific and contested; no general autonomous-agent reliability property is admitted.
- Optimal aggregation of reliability across unequal consumers and rare high-consequence journeys remains unresolved.
- Prospective causal attribution of reliability growth under continuously changing configurations remains unresolved.
- Reliable estimation of rare common-cause dependence from sparse field data remains unresolved.

## Denominator exclusions and bounded candidates

| ID | Property | Status | Main lineage | Primary evidence |
|---|---|---|---|---|
| ERM-P041 | MTBF as a universal scalar for reliability | `CEREMONY_NOT_GENERAL_PROPERTY` | HARDWARE_RELIABILITY_LINEAGE | SRC-043, SRC-044 |
| ERM-P042 | “Five nines” as a universal service-reliability claim | `CEREMONY_NOT_GENERAL_PROPERTY` | SERVICE_RELIABILITY_OR_SRE_TRANSLATION | SRC-063, SRC-083 |
| ERM-P043 | Universal bathtub-curve assumption | `REJECTED_OR_DISFAVOURED` | LIFE_DATA_AND_STATISTICAL_RELIABILITY_LINEAGE | SRC-041, SRC-046 |
| ERM-P044 | Handbook reliability prediction as field-reliability proof | `CEREMONY_NOT_GENERAL_PROPERTY` | HARDWARE_RELIABILITY_LINEAGE | SRC-002, SRC-039 |
| ERM-P045 | Completed FMEA/FMECA as proof that failure modes are controlled | `CEREMONY_NOT_GENERAL_PROPERTY` | FAILURE_ANALYSIS_LINEAGE | SRC-004, SRC-035 |
| ERM-P046 | Backup existence as proof that recovery is solved | `REJECTED_OR_DISFAVOURED` | AVAILABILITY_AND_REPAIRABLE_SYSTEMS_LINEAGE | SRC-056, SRC-057 |
| ERM-P047 | One failover test as proof of disaster recovery | `REJECTED_OR_DISFAVOURED` | AVAILABILITY_AND_REPAIRABLE_SYSTEMS_LINEAGE | SRC-056, SRC-057, SRC-059 |
| ERM-P048 | No incidents or lower incident count as proof of reliability improvement | `CEREMONY_NOT_GENERAL_PROPERTY` | SERVICE_RELIABILITY_OR_SRE_TRANSLATION | SRC-010, SRC-024, SRC-028 |
| ERM-P049 | Green health check as proof that required function is available | `REJECTED_OR_DISFAVOURED` | DIAGNOSTICS_AND_PHM_LINEAGE | SRC-024, SRC-064 |
| ERM-P050 | Chaos exercise as general proof of resilience | `CEREMONY_NOT_GENERAL_PROPERTY` | FAULT_INJECTION_OR_CHAOS_TRANSLATION | SRC-068, SRC-069 |
| ERM-P051 | More redundancy always improves reliability | `REJECTED_OR_DISFAVOURED` | HARDWARE_RELIABILITY_LINEAGE | SRC-011, SRC-023 |
| ERM-P052 | Predictive maintenance universally outperforms simpler policies | `REJECTED_OR_DISFAVOURED` | DIAGNOSTICS_AND_PHM_LINEAGE | SRC-025, SRC-071, SRC-072 |
| ERM-P053 | Reliability-growth curve alone proves causal design improvement | `REJECTED_OR_DISFAVOURED` | RELIABILITY_GROWTH_LINEAGE | SRC-006, SRC-007, SRC-084 |
| ERM-P054 | Zero observed failures means zero failure probability or an unlimited reliability claim | `REJECTED_OR_DISFAVOURED` | LIFE_DATA_AND_STATISTICAL_RELIABILITY_LINEAGE | SRC-049, SRC-050, SRC-043 |
| ERM-P055 | AI/ML/agentic diagnosis or auto-remediation as a general reliability property | `DOMAIN_SPECIFIC` | DOMAIN_SPECIFIC | SRC-026, SRC-027, SRC-071, SRC-072 |

These 15 candidates remain in the machine-readable denominator. `DOMAIN_SPECIFIC` does not mean useless: ERM-P055 permits narrowly validated diagnostic/remediation mechanisms but rejects a general “AI makes systems reliable” property.

## Source handoff

The exact identities, locators, evidence classes, claim relationships and contrary-evidence notes are in `EVOLVED_RELIABILITY_AND_MAINTAINABILITY_ENGINEERING_SOURCE_TABLE.json`. Property records cite source IDs rather than relying on search snippets or unstable prose summaries.

## Intake receipt

- `AUDIT_INTAKE_STATE`: `COMPLETE`
- `CROSSWALK_WORTHY_PROPERTY_COUNT`: `40`
- `QUESTIONS_ANSWERED_HERE`: `0`
- `TARGET_ANALYSIS_PERFORMED`: `NO`
- `PROPERTY_POPULATION_FROZEN`: `YES`
