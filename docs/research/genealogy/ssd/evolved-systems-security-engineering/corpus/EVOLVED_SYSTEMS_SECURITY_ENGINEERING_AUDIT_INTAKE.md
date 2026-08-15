# EVOLVED_SYSTEMS_SECURITY_ENGINEERING_AUDIT_INTAKE

**Analytical label:** `EVOLVED_SYSTEMS_SECURITY_ENGINEERING`  
**Freeze date:** 2026-08-12  
**Scope:** Independent external defensive systems-security engineering corpus. No target system is analysed here.

## Population receipt

- **PROPERTY_POPULATION_TOTAL:** 60
- **PROPERTY_POPULATION_EXAMINED:** 60
- **PROPERTY_COVERAGE:** 60/60
- **Denominator rule:** All admitted, superseded, ceremonial, rejected, domain-specific and contested candidates remain in the denominator. No candidate was silently dropped.
- **Machine-readable authority:** `EVOLVED_SYSTEMS_SECURITY_ENGINEERING_PROPERTY_LEDGER.json`.

## SOURCE_POPULATION_SUMMARY

| Epistemic/source partition | Count | Interpretation |
| --- | --- | --- |
| STANDARD_OR_GUIDANCE_REQUIREMENT | 56 | Establishes current recommended/required practice or assessment expectations; not optimality/outcome proof. |
| EMPIRICAL_OR_DOMAIN_FINDING | 24 | Comparative, observational, field or systematic-review evidence; transferability varies. |
| FORMAL_OR_MODEL_DEPENDENT | 15 | Strong within explicit model/specification/assumptions; environment correspondence remains separate. |
| SOURCE_ESTABLISHED | 9 | Primary historical or mechanism-establishing source. |
| INCIDENT_OR_VULNERABILITY_EVIDENCE | 7 | Mechanism-rich case evidence; selected and non-random. |
| SOURCE_INTERPRETATION | 3 | Analytical interpretation grounded in identified sources. |
| ADVERSARIAL_ASSUMPTION_DEPENDENT | 2 | Conclusion varies strongly with attacker access/capability. |
| HISTORICAL_INFERENCE | 1 | Retrospective lineage claim explicitly marked as inference. |
| TOTAL | 117 | Exact supporting records in the frozen source table. |

The source population spans original computer-security reports and papers, formal policy/security models, current NIST/CISA/ENISA/DoD/ISO/IEC/FDA guidance, peer-reviewed empirical and systematic-review work, and authoritative incident analyses. Eight records are 2026 current-state sources; historical editions are retained where genealogy matters. Vendor material is absent except where a producer incident record or implementation programme is the object of evidence, and no vendor claim is treated as independent effectiveness proof.

## EVIDENCE_STRENGTH_PARTITIONS

| Partition | Frozen judgement | Highest-strength property families | Principal limit |
| --- | --- | --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | High for trusted systems, access control, secure-design principles, cryptography, evaluation and SDL; moderate for newer supply-chain/zero-trust/resilience lineages. | P03–P10, P16–P17, P21–P24, P30–P31 | Documented origin does not prove current effectiveness or direct transmission into every modern practice. |
| FORMAL_OR_MODEL_STRENGTH | Very high for bounded cryptographic, access-control and verified-component claims; moderate/limited for socio-technical and programme claims. | P06–P10, P17, P21–P22, P30, P36–P38 | Proof/model validity is conditional on specification, TCB, toolchain, deployment and adversary assumptions. |
| INCIDENT_OR_VULNERABILITY_CASE_STRENGTH | High to very high for identity/control-plane, supply-chain, update/common-mode, detection and recovery failure mechanisms. | P03, P08, P21, P33–P45 | Incidents are selected, retrospective and do not yield population causal effect sizes. |
| EMPIRICAL_COMPARATIVE_STRENGTH | High for scanner variation, SAST suppression, fuzzing defect discovery, vulnerability exploitation concentration, SBOM inconsistency and usable-security/training limits; limited for integrated programmes. | P11, P27–P29, P31, P33, P35, P47, P52–P56 | Ecosystem, tool, benchmark and organisational selection constrain transfer. |
| FIELD_PRACTICE_STRENGTH | High for identity, key lifecycle, secure update/configuration, incident response and lifecycle practice; moderate for formal assurance, moving target and AI/agent security. | P16–P25, P32–P46 | Widespread adoption is not outcome proof and can reflect regulation/vendor incentives. |
| STANDARD_OR_REGULATORY_STRENGTH | High or very high for current practice definitions across NIST/CISA/ISO/IEC/FDA/ENISA. | P01–P03, P15–P25, P31–P51 | A requirement/recommendation does not establish comparative optimality. |
| ADVERSARIAL_EVALUATION_STRENGTH | High for scoped testing/fuzzing/formal verification and some supply-chain mechanisms; moderate for architecture programmes. | P28–P31, P36–P38 | No evaluation exhausts adaptive attacker space; safety rules and target knowledge constrain tests. |
| TRANSFERABILITY_STRENGTH | High for objectives, bounded threat/trust, least privilege, mediation, compartmentalisation, current evidence and recovery; low for labels/programmes and domain-specific techniques. | P01–P18, P21–P25, P31, P39–P49 | Trigger, cheap path and failure direction remain context-sensitive. |
| ASSUMPTION_SENSITIVITY | High across all adversarial claims; very high for zero trust control planes, provenance, recovery, metrics, diversity and AI. | P02–P03, P18–P21, P30–P31, P36–P44, P47–P49, P59–P60 | Hidden exclusions are a primary false-confidence mechanism. |
| CONTRARY_EVIDENCE_STRENGTH | High for ceremony/proxy candidates and for implementation limits of otherwise retained properties. | P11, P14, P27–P31, P33–P39, P47–P60 | Criticism narrows and refines more properties than it eliminates. |

## TOP_CROSSWALK_PROPERTIES

`TOP_CROSSWALK_PROPERTIES` contains every property judged crosswalk-worthy: P01–P52 and P59–P60. P53–P58 remain in the denominator as explicit anti-properties/ceremonies and appear in the anti-adoption lists rather than as positive target-system requirements.

### P01 — Explicit protected consequence and security objective

- **PROPERTY_ID:** P01
- **PROPERTY_NAME:** Explicit protected consequence and security objective
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevention or bounded acceptance of specified mission, service, safety, privacy, financial, legal or human harms caused through loss of required trustworthiness.
- **THREAT_OR_ADVERSARY_PROFILE:** Any relevant intentional actor or compromised component capable of producing the specified consequence; capability and access must be bounded separately.
- **FAILURE_MODE:** Control accumulation that does not change a consequential adversarial path; protection of the wrong asset; technically secure behaviour that still permits unacceptable mission harm.
- **MATURE_FORM:** A small, current set of consequence-linked objectives with stated tolerance, decision owner, adversary assumptions, measurable evidence and recovery condition.
- **TRIGGER:** Always for consequential systems, new exposed capabilities, material trust-boundary changes, or when risk acceptance is requested.
- **CHEAP_PATH:** For a low-exposure, reversible change, record the protected consequence and a brief invariant/abuse check rather than producing a full control catalogue.
- **TRUST_BOUNDARY_PROFILE:** Identity claims are relevant only insofar as they affect the protected consequence; anonymous or environmental threats must not be excluded by default. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Someone must have authority to declare objectives, tolerances and residual-risk acceptance; implementers cannot silently define them by available tooling. Identity claims are relevant only insofar as they affect the protected consequence; anonymous or environmental threats must not be excluded by default.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Always for consequential systems, new exposed capabilities, material trust-boundary changes, or when risk acceptance is requested. Configuration/provenance: The objective must bind to the actual architecture, deployment, data flows and dependency versions to which it applies. Recovery: Where consequence includes service continuity, recovery criteria and trust-restoration conditions must be stated with the objective.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S102] [S103] [S104].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Evidence must reveal whether the protected invariant is being approached or violated; otherwise objectives remain aspirational. Recovery: Where consequence includes service continuity, recovery criteria and trust-restoration conditions must be stated with the objective.
- **REQUIRED_PRECONDITIONS:** Named decision owner; system/mission context; asset and dependency inventory sufficient to connect technical state to consequence. Identity claims are relevant only insofar as they affect the protected consequence; anonymous or environmental threats must not be excluded by default. Someone must have authority to declare objectives, tolerances and residual-risk acceptance; implementers cannot silently define them by available tooling. The objective must bind to the actual architecture, deployment, data flows and dependency versions to which it applies. Evidence must reveal whether the protected invariant is being approached or violated; otherwise objectives remain aspirational. Where consequence includes service continuity, recovery criteria and trust-restoration conditions must be stated with the objective.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** CIA is useful but incomplete as a universal ontology; objectives can be unknowable, contested or dynamic, and overly broad objectives can justify disproportionate surveillance/control. Contrary evidence: Objectives can conflict and outcome data are sparse; authoritative guidance establishes disciplined practice, not a universally optimal objective taxonomy.
- **ANTI_CEREMONY_BOUNDARY:** A risk register, policy statement or control matrix is optional; the property is an actionable, current consequence-to-claim chain.
- **POSSIBLE_CONFLICTING_PROPERTY:** P49: competing safety, privacy, availability or usability consequence; P47: metric simplification.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **explicit protected consequence and security objective** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for explicit protected consequence and security objective remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Control accumulation that does not change a consequential adversarial path; protection of the wrong asset; technically secure behaviour that still permits unacceptable mission harm. — or would it add ceremony without changing the engineering decision?

### P02 — Bounded adversary and threat model

- **PROPERTY_ID:** P02
- **PROPERTY_NAME:** Bounded adversary and threat model
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Confidence that required objectives remain protected against specified intentional, adaptive and persistent behaviours, including insider and supply-chain positions where relevant.
- **THREAT_OR_ADVERSARY_PROFILE:** Explicit attacker classes, initial access, privileges, knowledge, resources, persistence, collusion, physical proximity and dependency compromise; exclusions are visible assumptions, not impossibilities.
- **FAILURE_MODE:** Designs that are secure only because a decisive attacker path was omitted; assurance that tests a toy adversary; inability to explain residual risk.
- **MATURE_FORM:** A decision-linked, revision-triggered adversary model with explicit exclusions, uncertainty, supplier/identity compromise cases and a lightweight path when consequence is low.
- **TRIGGER:** When a consequential decision depends on what an attacker can do, at new trust boundaries, after major change, or when relying on a control with known bypass conditions.
- **CHEAP_PATH:** For low-consequence changes, a short trust-boundary and plausible-abuse check can be sufficient; do not instantiate a full template if it cannot alter a decision.
- **TRUST_BOUNDARY_PROFILE:** Compromised identity providers, operators, workloads and suppliers must be considered where within scope; 'authenticated user' is not synonymous with benign user. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Authority is required to accept exclusions and residual risk; threat intelligence may inform capability but cannot dictate policy. Compromised identity providers, operators, workloads and suppliers must be considered where within scope; 'authenticated user' is not synonymous with benign user.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: When a consequential decision depends on what an attacker can do, at new trust boundaries, after major change, or when relying on a control with known bypass conditions. Configuration/provenance: The model identifies the exact configuration, deployment and dependency state being analysed and records change invalidators. Recovery: Recovery assumptions must include whether the adversary persists in identities, management planes, update paths or recovery media.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S083] [S084].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Telemetry and incident data should test model assumptions; absence of detection cannot validate absence of attacker capability. Recovery: Recovery assumptions must include whether the adversary persists in identities, management planes, update paths or recovery media.
- **REQUIRED_PRECONDITIONS:** Knowledge of system exposure, dependencies and likely consequence; access to design and operational evidence; an owner for model currency. Compromised identity providers, operators, workloads and suppliers must be considered where within scope; 'authenticated user' is not synonymous with benign user. Authority is required to accept exclusions and residual risk; threat intelligence may inform capability but cannot dictate policy. The model identifies the exact configuration, deployment and dependency state being analysed and records change invalidators. Telemetry and incident data should test model assumptions; absence of detection cannot validate absence of attacker capability. Recovery assumptions must include whether the adversary persists in identities, management planes, update paths or recovery media.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=MODERATE; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Completeness is unattainable; analyst subjectivity and knowledge gaps are material; formal overhead can cause abandonment; intelligence is biased toward observed campaigns. Contrary evidence: No method establishes exhaustive attacker coverage; comparative evidence that one threat-modelling method improves field outcomes remains limited.
- **ANTI_CEREMONY_BOUNDARY:** A threat-model document or STRIDE worksheet is not required; a current, reviewable assumption-to-decision relation is.
- **POSSIBLE_CONFLICTING_PROPERTY:** P48: proportionality and cheap-path cost; P10/P32: transparency versus exploit-window control.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **bounded adversary and threat model** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for bounded adversary and threat model remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Designs that are secure only because a decisive attacker path was omitted; assurance that tests a toy adversary; inability to explain residual risk. — or would it add ceremony without changing the engineering decision?

### P03 — Explicit trust assumptions and trust boundaries

- **PROPERTY_ID:** P03
- **PROPERTY_NAME:** Explicit trust assumptions and trust boundaries
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Integrity, confidentiality, availability and accountable control remain bounded when components, tenants, suppliers or users are hostile or compromised.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversaries may occupy any untrusted domain and, where modelled, a trusted component; trust is a dependency claim, not a moral judgement.
- **FAILURE_MODE:** An apparently separate component is not an independent boundary; transitive trust expands silently; compromise of a shared control plane defeats many controls.
- **MATURE_FORM:** A current authority/data-flow map whose boundaries have explicit guarantees, dependencies, observability, common-mode analysis and reconstitution plan.
- **TRIGGER:** New data/authority flow, tenant or supplier relationship, remote administration, agent/tool integration, or concentration of control in a shared service.
- **CHEAP_PATH:** For simple single-user/offline/reversible work, record the few consequential crossings and rely on existing platform isolation where its assumptions are acceptable.
- **TRUST_BOUNDARY_PROFILE:** Identity assertions are accepted only from stated issuers under bounded proofing/authentication assumptions; identities crossing domains are reinterpreted explicitly. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Each boundary specifies which authority may cross, who can change policy and what delegated authority remains downstream. Identity assertions are accepted only from stated issuers under bounded proofing/authentication assumptions; identities crossing domains are reinterpreted explicitly.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: New data/authority flow, tenant or supplier relationship, remote administration, agent/tool integration, or concentration of control in a shared service. Configuration/provenance: Claims bind to deployed topology, runtime configuration, firmware/platform state and supplier provenance; diagrams alone are insufficient. Recovery: Containment and recovery plans identify which boundaries can be re-established and which trust roots/recovery sources remain clean.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=HIGH; adversarial=HIGH. Critical evidence: [S109] [S111] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Boundary crossings and policy decisions need enough logging/measurement to reveal misuse or enforcement failure. Recovery: Containment and recovery plans identify which boundaries can be re-established and which trust roots/recovery sources remain clean.
- **REQUIRED_PRECONDITIONS:** Accurate architecture/data-flow view; enforcement mechanisms whose behaviour is understood; ownership of cross-boundary contracts. Identity assertions are accepted only from stated issuers under bounded proofing/authentication assumptions; identities crossing domains are reinterpreted explicitly. Each boundary specifies which authority may cross, who can change policy and what delegated authority remains downstream. Claims bind to deployed topology, runtime configuration, firmware/platform state and supplier provenance; diagrams alone are insufficient. Boundary crossings and policy decisions need enough logging/measurement to reveal misuse or enforcement failure. Containment and recovery plans identify which boundaries can be re-established and which trust roots/recovery sources remain clean.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Boundary enumeration can become unbounded; microservice splits may increase attack surface and policy complexity; central identity or policy systems can become catastrophic shared dependencies. Contrary evidence: Some boundaries must rely on shared hardware, identity or cloud infrastructure; perfect independence is impossible and decomposition can increase operational failure.
- **ANTI_CEREMONY_BOUNDARY:** A data-flow or zero-trust diagram is optional; the property is explicit, enforced and testable trust partitioning.
- **POSSIBLE_CONFLICTING_PROPERTY:** P08/P09: shared small mechanisms versus stronger partitioning; P44: degraded interoperation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **explicit trust assumptions and trust boundaries** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for explicit trust assumptions and trust boundaries remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — An apparently separate component is not an independent boundary; transitive trust expands silently; compromise of a shared control plane defeats many controls. — or would it add ceremony without changing the engineering decision?

### P04 — Least privilege and authority minimisation

- **PROPERTY_ID:** P04
- **PROPERTY_NAME:** Least privilege and authority minimisation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduced unauthorised disclosure, modification, execution, administration and lateral consequence; smaller blast radius after credential or component compromise.
- **THREAT_OR_ADVERSARY_PROFILE:** Any principal, process, workload, agent or delegated service may be malicious or compromised while holding legitimate credentials.
- **FAILURE_MODE:** Standing or excessive authority permits actions beyond current intent; stale entitlement survives role/task change; shared admin rights defeat attribution.
- **MATURE_FORM:** Minimise consequential authority across scope, duration, delegation and parameters while preserving a tested path for legitimate work and emergency recovery.
- **TRIGGER:** High-consequence actions, multi-tenant/shared systems, automation/agents, remote administration, production access and broadly reusable credentials.
- **CHEAP_PATH:** For isolated low-consequence work, platform defaults and a coarse role may be cheaper than elaborate fine-grained policy; still avoid unnecessary administrator/root authority.
- **TRUST_BOUNDARY_PROFILE:** Current subject/workload identity, assurance level and session context must support the granularity claimed. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Entitlement grantors and policy administrators are themselves bounded; delegated authority cannot exceed intended scope. Current subject/workload identity, assurance level and session context must support the granularity claimed.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: High-consequence actions, multi-tenant/shared systems, automation/agents, remote administration, production access and broadly reusable credentials. Configuration/provenance: Entitlements must reflect actual resources, APIs, parameters and deployed policy; reviews compare desired with effective authority. Recovery: Break-glass and account-recovery mechanisms must preserve availability without silently recreating permanent broad privilege.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=HIGH; adversarial=HIGH. Critical evidence: [S097] [S098] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Use, denial, elevation and abnormal privilege paths need visible evidence; stale/unexercised privilege should be discoverable. Recovery: Break-glass and account-recovery mechanisms must preserve availability without silently recreating permanent broad privilege.
- **REQUIRED_PRECONDITIONS:** Complete task/authority model; usable elevation and recovery paths; policy enforcement that cannot be bypassed by alternate interfaces. Current subject/workload identity, assurance level and session context must support the granularity claimed. Entitlement grantors and policy administrators are themselves bounded; delegated authority cannot exceed intended scope. Entitlements must reflect actual resources, APIs, parameters and deployed policy; reviews compare desired with effective authority. Use, denial, elevation and abnormal privilege paths need visible evidence; stale/unexercised privilege should be discoverable. Break-glass and account-recovery mechanisms must preserve availability without silently recreating permanent broad privilege.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Least privilege is not 'remove every permission'; excessive friction can damage availability, safety and accountability. Empirical outcome evidence for specific entitlement-review programmes is limited. Contrary evidence: Fine-grained policy can increase complexity and common-mode dependence; not every low-risk operation warrants per-request adaptive authorization.
- **ANTI_CEREMONY_BOUNDARY:** Periodic access-review completion is not the property; current effective authority and bounded use are.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P20: usability, operational agility and emergency access.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **least privilege and authority minimisation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for least privilege and authority minimisation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Standing or excessive authority permits actions beyond current intent; stale entitlement survives role/task change; shared admin rights defeat attribution. — or would it add ceremony without changing the engineering decision?

### P05 — Fail-safe defaults and secure failure policy

- **PROPERTY_ID:** P05
- **PROPERTY_NAME:** Fail-safe defaults and secure failure policy
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevents confidentiality/integrity compromise through permissive error paths while explicitly controlling availability and safety consequences.
- **THREAT_OR_ADVERSARY_PROFILE:** Attackers can induce malformed, delayed or unavailable inputs and exploit exception/error handling; benign failures also occur.
- **FAILURE_MODE:** Unknown or failed authorization becomes allow; cache or fallback expands rights; outage of a policy service blocks a safety-critical function or recovery.
- **MATURE_FORM:** For every consequential operation, choose and test a failure mode that minimises combined adversarial and operational harm, with visible degraded state and bounded exceptions.
- **TRIGGER:** Consequential authorization, untrusted input handling, policy/control-plane outages and any path where errors could grant lasting authority.
- **CHEAP_PATH:** For reversible low-consequence reads, a degraded or cached mode may be acceptable if scope and expiry are bounded; blanket fail-closed is not required.
- **TRUST_BOUNDARY_PROFILE:** Identity/authentication uncertainty must be mapped to the selected failure mode rather than treated uniformly. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Only an authorised policy may choose fail-open/degraded modes; exceptions must be time- and scope-bound. Identity/authentication uncertainty must be mapped to the selected failure mode rather than treated uniformly.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Consequential authorization, untrusted input handling, policy/control-plane outages and any path where errors could grant lasting authority. Configuration/provenance: Failure behaviour must match actual deployment dependencies, caches and policy versions. Recovery: Recovery must restore intended policy without locking out legitimate administrators or preserving emergency broad access.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S113] [S097] [S098].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Operators need visibility into degraded/fallback state, denied critical work and repeated induced failures. Recovery: Recovery must restore intended policy without locking out legitimate administrators or preserving emergency broad access.
- **REQUIRED_PRECONDITIONS:** Known consequence of denial and grant; dependable local enforcement; tested degraded operation; no hidden bypass path. Identity/authentication uncertainty must be mapped to the selected failure mode rather than treated uniformly. Only an authorised policy may choose fail-open/degraded modes; exceptions must be time- and scope-bound. Failure behaviour must match actual deployment dependencies, caches and policy versions. Operators need visibility into degraded/fallback state, denied critical work and repeated induced failures. Recovery must restore intended policy without locking out legitimate administrators or preserving emergency broad access.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Security and availability do not always align. A denial can itself be the protected harm, especially in cyber-physical, medical and emergency contexts. Contrary evidence: No universal fail-safe direction exists; consequence and recovery evidence are domain-specific.
- **ANTI_CEREMONY_BOUNDARY:** A configuration checkbox labelled fail-closed is not sufficient; the property is end-to-end failure semantics.
- **POSSIBLE_CONFLICTING_PROPERTY:** P44/P49: availability and safety can favour bounded degraded operation rather than denial.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **fail-safe defaults and secure failure policy** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for fail-safe defaults and secure failure policy remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Unknown or failed authorization becomes allow; cache or fallback expands rights; outage of a policy service blocks a safety-critical function or recovery. — or would it add ceremony without changing the engineering decision?

### P06 — Complete mediation and current authorization

- **PROPERTY_ID:** P06
- **PROPERTY_NAME:** Complete mediation and current authorization
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Ensures each consequential resource/action is authorised for the current subject, context, parameters and policy state.
- **THREAT_OR_ADVERSARY_PROFILE:** Attackers may reuse valid sessions/tokens, find unmediated paths, exploit policy drift or cause one component to act with its own broader authority.
- **FAILURE_MODE:** Authenticated or previously authorised actors perform actions no longer intended; object references bypass checks; network position substitutes for authorization.
- **MATURE_FORM:** All consequential paths are mediated by analysable enforcement whose decision is current enough for the consequence and whose failure/recovery behaviour is explicit.
- **TRIGGER:** Consequential state changes, cross-tenant/data access, delegated service/agent action, privileged APIs and long-lived sessions.
- **CHEAP_PATH:** For public/non-sensitive immutable resources, simple coarse authorization or no authorization can be correct; avoid needless per-request policy complexity.
- **TRUST_BOUNDARY_PROFILE:** Current authenticated identity/device/workload evidence must be sufficient for the claim; authentication alone does not grant action. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Policy decision authority and enforcement authority are explicit; delegates cannot enlarge scope. Current authenticated identity/device/workload evidence must be sufficient for the claim; authentication alone does not grant action.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Consequential state changes, cross-tenant/data access, delegated service/agent action, privileged APIs and long-lived sessions. Configuration/provenance: Policy, token and resource identity/version are bound to current configuration; caches have bounded freshness. Recovery: Recovery paths and offline modes must not become permanently unmediated; emergency authorization is separately governed.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=HIGH; adversarial=HIGH. Critical evidence: [S043] [S044] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Authorization decisions, denials, bypasses and revocation propagation need auditable evidence without exposing sensitive secrets. Recovery: Recovery paths and offline modes must not become permanently unmediated; emergency authorization is separately governed.
- **REQUIRED_PRECONDITIONS:** Complete path inventory; tamper resistance; policy availability; coherence across APIs, asynchronous jobs, caches and recovery tools. Current authenticated identity/device/workload evidence must be sufficient for the claim; authentication alone does not grant action. Policy decision authority and enforcement authority are explicit; delegates cannot enlarge scope. Policy, token and resource identity/version are bound to current configuration; caches have bounded freshness. Authorization decisions, denials, bypasses and revocation propagation need auditable evidence without exposing sensitive secrets. Recovery paths and offline modes must not become permanently unmediated; emergency authorization is separately governed.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Literal checking of every low-risk read can be costly; reference-monitor assumptions can fail in hardware, management plane or deployment environment. Contrary evidence: Complete path knowledge is difficult in distributed systems; re-evaluation cadence and acceptable staleness remain context-dependent.
- **ANTI_CEREMONY_BOUNDARY:** Possession of a gateway, service mesh or zero-trust product does not establish complete mediation.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P18/P44: re-evaluation latency, usability and offline continuity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **complete mediation and current authorization** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for complete mediation and current authorization remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Authenticated or previously authorised actors perform actions no longer intended; object references bypass checks; network position substitutes for authorization. — or would it add ceremony without changing the engineering decision?

### P07 — Separation of privilege and multi-party authorization where consequence warrants

- **PROPERTY_ID:** P07
- **PROPERTY_NAME:** Separation of privilege and multi-party authorization where consequence warrants
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces unilateral misuse and compromise leverage for critical release, key, financial, administrative, safety or recovery operations.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can compromise one authority but not all independent conditions; collusion and common-mode compromise are bounded.
- **FAILURE_MODE:** Nominal dual approval is performed by one person/account, approvals are not bound to exact action/parameters, or all approvers share the same identity/control plane.
- **MATURE_FORM:** The number and independence of required authorities are proportional to consequence; approvals are current and inseparably bound to execution.
- **TRIGGER:** Irreversible/high-blast-radius actions, root/trust-anchor changes, production signing, destructive recovery, high-value transactions and exceptional access.
- **CHEAP_PATH:** For routine reversible low-consequence actions, one accountable authorised actor plus logging is cheaper and usually preferable.
- **TRUST_BOUNDARY_PROFILE:** Distinct current identities and authentication factors must represent genuinely separate principals, not two prompts to one account. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Approvers must have scoped authority; approval is not execution unless explicitly designed; policy changes require separate governance. Distinct current identities and authentication factors must represent genuinely separate principals, not two prompts to one account.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Irreversible/high-blast-radius actions, root/trust-anchor changes, production signing, destructive recovery, high-value transactions and exceptional access. Configuration/provenance: Artifact/action hash, parameters, environment and policy version are bound to approvals. Recovery: Emergency bypass and loss of one authority require tested recovery that does not normalise unilateral control.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S064] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Evidence shows who approved what, when, under which context, and whether execution matched approval. Recovery: Emergency bypass and loss of one authority require tested recovery that does not normalise unilateral control.
- **REQUIRED_PRECONDITIONS:** Independent identities/channels, low-collusion assumption, usable workflow, exact action binding and emergency path. Distinct current identities and authentication factors must represent genuinely separate principals, not two prompts to one account. Approvers must have scoped authority; approval is not execution unless explicitly designed; policy changes require separate governance. Artifact/action hash, parameters, environment and policy version are bound to approvals. Evidence shows who approved what, when, under which context, and whether execution matched approval. Emergency bypass and loss of one authority require tested recovery that does not normalise unilateral control.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Multi-party control adds latency and can obscure accountability; independence is often assumed rather than tested. Contrary evidence: Evidence that dual control reduces field incidents is mostly mechanism- and domain-specific; shared infrastructure can defeat presumed independence.
- **ANTI_CEREMONY_BOUNDARY:** A ticket with two names or a standing committee is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P41/P48: urgent response and low-consequence reversible action.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **separation of privilege and multi-party authorization where consequence warrants** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for separation of privilege and multi-party authorization where consequence warrants remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Nominal dual approval is performed by one person/account, approvals are not bound to exact action/parameters, or all approvers share the same identity/control plane. — or would it add ceremony without changing the engineering decision?

### P08 — Least common mechanism and common-mode exposure minimisation

- **PROPERTY_ID:** P08
- **PROPERTY_NAME:** Least common mechanism and common-mode exposure minimisation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Limits correlated compromise, tenant crossover, covert/unintended channels and systemic blast radius.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can compromise or manipulate a widely shared mechanism; supposedly independent controls may share the same code, credentials, supplier or management plane.
- **FAILURE_MODE:** Defence layers fail together; shared service crosses tenants; central policy/signing/update failure becomes fleet-wide; redundancy is only nominal.
- **MATURE_FORM:** Minimise or explicitly govern common-mode dependencies in proportion to correlated consequence; prefer small, analysable shared mechanisms and genuine recovery independence.
- **TRIGGER:** Multi-tenant systems, fleet-wide management/update, central identity/policy, common libraries, recovery infrastructure and claims of independent defence layers.
- **CHEAP_PATH:** For small systems, vetted platform sharing may reduce complexity more than bespoke isolation; document and accept the common dependency.
- **TRUST_BOUNDARY_PROFILE:** Shared identity issuers and administrators are explicit trust concentrations; local identities may be needed for recovery. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** No single authority silently controls all supposedly independent layers unless consciously accepted. Shared identity issuers and administrators are explicit trust concentrations; local identities may be needed for recovery.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Multi-tenant systems, fleet-wide management/update, central identity/policy, common libraries, recovery infrastructure and claims of independent defence layers. Configuration/provenance: Shared code, service, key, image, pipeline and configuration ancestry are traceable. Recovery: Recovery sources/control paths must not share the compromise domain they are meant to recover.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S001] [S002] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Telemetry distinguishes local from common-mode failure and survives loss of the shared service. Recovery: Recovery sources/control paths must not share the compromise domain they are meant to recover.
- **REQUIRED_PRECONDITIONS:** Architecture/dependency inventory; meaningful isolation; operational capacity to run partitions; evidence about correlated failure. Shared identity issuers and administrators are explicit trust concentrations; local identities may be needed for recovery. No single authority silently controls all supposedly independent layers unless consciously accepted. Shared code, service, key, image, pipeline and configuration ancestry are traceable. Telemetry distinguishes local from common-mode failure and survives loss of the shared service. Recovery sources/control paths must not share the compromise domain they are meant to recover.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Sharing is not inherently bad: small, well-analysed common mechanisms can be safer than many complex variants. Diversity without independent maintenance can worsen security. Contrary evidence: Quantifying correlated cyber failure is difficult; duplicated/diverse stacks can introduce more vulnerabilities and operational errors.
- **ANTI_CEREMONY_BOUNDARY:** A count of layers, vendors or zones is not common-mode analysis.
- **POSSIBLE_CONFLICTING_PROPERTY:** P09/P59: shared simple TCB versus diversity/partition cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **least common mechanism and common-mode exposure minimisation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for least common mechanism and common-mode exposure minimisation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Defence layers fail together; shared service crosses tenants; central policy/signing/update failure becomes fleet-wide; redundancy is only nominal. — or would it add ceremony without changing the engineering decision?

### P09 — Economy of mechanism and analysable trusted computing base

- **PROPERTY_ID:** P09
- **PROPERTY_NAME:** Economy of mechanism and analysable trusted computing base
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Integrity of enforcement and reduction of exploitable privileged implementation; higher confidence in critical isolation/authorization claims.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary targets any flaw in privileged mechanisms; assurance resources are finite and cannot exhaustively cover a vast TCB.
- **FAILURE_MODE:** Security-critical code sprawls across applications, plugins and control planes; 'small' kernel relies on unanalysed firmware/hardware/operations; simplification removes needed checks.
- **MATURE_FORM:** Keep high-consequence enforcement small, specified and provenance-bound enough for proportionate assurance, while explicitly listing excluded assumptions.
- **TRIGGER:** Core enforcement, hypervisor/kernel, cryptographic/update roots, isolation boundaries and high-consequence parsers/protocols.
- **CHEAP_PATH:** For ordinary low-consequence business logic, modular testing and memory-safe platforms may be cheaper than radical minimisation or proof.
- **TRUST_BOUNDARY_PROFILE:** Identity/policy services included in the effective TCB are not excluded merely because external/cloud-managed. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Who may alter TCB code/configuration and deploy it must be tightly bounded. Identity/policy services included in the effective TCB are not excluded merely because external/cloud-managed.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Core enforcement, hypervisor/kernel, cryptographic/update roots, isolation boundaries and high-consequence parsers/protocols. Configuration/provenance: Exact source, build, firmware, configuration and deployment correspondence are prerequisites for assurance. Recovery: Recovery must restore a known TCB and trust roots; a small TCB does not by itself provide reconstitution.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=MODERATE; adversarial=HIGH. Critical evidence: [S092] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Runtime integrity/attestation and failure telemetry should reveal divergence from the assured configuration. Recovery: Recovery must restore a known TCB and trust roots; a small TCB does not by itself provide reconstitution.
- **REQUIRED_PRECONDITIONS:** Clear TCB boundary, stable specification, controlled hardware/toolchain assumptions and operational ownership. Identity/policy services included in the effective TCB are not excluded merely because external/cloud-managed. Who may alter TCB code/configuration and deploy it must be tightly bounded. Exact source, build, firmware, configuration and deployment correspondence are prerequisites for assurance. Runtime integrity/attestation and failure telemetry should reveal divergence from the assured configuration. Recovery must restore a known TCB and trust roots; a small TCB does not by itself provide reconstitution.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=MODERATE; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Smallness is not sufficient for security and can conflict with usability/availability. Industrial formal-method success is selected and costly. Contrary evidence: Formal/model strength can be high while environment correspondence and comparative field evidence remain limited.
- **ANTI_CEREMONY_BOUNDARY:** A microkernel label, code-line count or formal-method badge is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48: rapid evolution and lifecycle speed versus stable minimised proof target.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **economy of mechanism and analysable trusted computing base** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for economy of mechanism and analysable trusted computing base remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Security-critical code sprawls across applications, plugins and control planes; 'small' kernel relies on unanalysed firmware/hardware/operations; simplification removes needed checks. — or would it add ceremony without changing the engineering decision?

### P10 — Open design and secret-minimal architecture

- **PROPERTY_ID:** P10
- **PROPERTY_NAME:** Open design and secret-minimal architecture
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Durable confidentiality/authenticity and reviewable enforcement even when algorithms, architecture and code structure are known.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can learn the mechanism and may obtain documentation/binaries; protected keys and live operational details are not assumed public.
- **FAILURE_MODE:** Proprietary obscurity hides defects; public design is mistaken for secure design; publication leaks active secrets or high-risk operational detail; open components receive no meaningful review.
- **MATURE_FORM:** Assume mechanisms will become known; rely on analysable controls and revocable minimal secrets, while managing time-sensitive disclosure responsibly.
- **TRIGGER:** Cryptography, widely deployed protocols, critical interfaces and designs likely to be exposed or reverse engineered.
- **CHEAP_PATH:** For a local low-consequence mechanism, full public publication is not required; internal independent review and no reliance on obscurity preserve the core.
- **TRUST_BOUNDARY_PROFILE:** Identity and authorization still depend on protected credentials/keys; open design does not remove proofing or compromise risk. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Disclosure/publication authority must distinguish reviewable design from operationally sensitive data. Identity and authorization still depend on protected credentials/keys; open design does not remove proofing or compromise risk.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Cryptography, widely deployed protocols, critical interfaces and designs likely to be exposed or reverse engineered. Configuration/provenance: Reviewed description must correspond to deployed implementation/version; public source alone does not prove build or configuration. Recovery: Compromised secrets require rotation/revocation and trust re-establishment; design openness does not supply recovery.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S064] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Vulnerability reports and telemetry should reveal failures; disclosure channels prevent secrecy from becoming suppression. Recovery: Compromised secrets require rotation/revocation and trust re-establishment; design openness does not supply recovery.
- **REQUIRED_PRECONDITIONS:** Sound secret/key lifecycle, competent review community or assessor, and change control. Identity and authorization still depend on protected credentials/keys; open design does not remove proofing or compromise risk. Disclosure/publication authority must distinguish reviewable design from operationally sensitive data. Reviewed description must correspond to deployed implementation/version; public source alone does not prove build or configuration. Vulnerability reports and telemetry should reveal failures; disclosure channels prevent secrecy from becoming suppression. Compromised secrets require rotation/revocation and trust re-establishment; design openness does not supply recovery.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=MODERATE; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Review attention is uneven; public availability creates no guarantee of inspection. Some operational details legitimately require controlled disclosure. Contrary evidence: Openness can aid attackers and does not assure review quality, source-to-binary correspondence or operational security.
- **ANTI_CEREMONY_BOUNDARY:** An open-source licence or published architecture is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P32/P45/P49: disclosure timing, operational secrecy and privacy.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **open design and secret-minimal architecture** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for open design and secret-minimal architecture remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Proprietary obscurity hides defects; public design is mistaken for secure design; publication leaks active secrets or high-risk operational detail; open components receive no meaningful review. — or would it add ceremony without changing the engineering decision?

### P11 — Psychological acceptability and usable security

- **PROPERTY_ID:** P11
- **PROPERTY_NAME:** Psychological acceptability and usable security
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Security objectives are achieved in the actual socio-technical workflow without transferring unreasonable cost or blame to users/operators.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversaries exploit predictable human attention, recovery and workflow constraints; users are bounded-rational actors with legitimate task goals.
- **FAILURE_MODE:** Users bypass controls; warnings become rote acknowledgement; recovery channels are weaker than authentication; administrators make errors in overly complex policy.
- **MATURE_FORM:** A control's strength is evaluated end-to-end with real users, incentives, accessibility, failure/recovery and bypass paths; design carries primary responsibility.
- **TRIGGER:** Any control that requires repeated human judgement, credential handling, complex administration, warning response or emergency work.
- **CHEAP_PATH:** For low-consequence choices, minimise prompts and use reversible defaults; training or documentation alone is not an adequate substitute for design.
- **TRUST_BOUNDARY_PROFILE:** Identity mechanisms must be usable across normal and recovery contexts; assurance level must not exceed task need without reason. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Users need clear authority boundaries and an attainable legitimate route; otherwise bypass becomes rational. Identity mechanisms must be usable across normal and recovery contexts; assurance level must not exceed task need without reason.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Any control that requires repeated human judgement, credential handling, complex administration, warning response or emergency work. Configuration/provenance: Usability evaluation must use the deployed interface/policy and realistic devices/workflows. Recovery: Recovery is part of the primary design; it must resist impersonation while remaining usable for legitimate loss/failure.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=HIGH; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S047] [S102].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe abandonment, bypass, support load, warning behaviour and recovery failures without surveillance disproportionate to need. Recovery: Recovery is part of the primary design; it must resist impersonation while remaining usable for legitimate loss/failure.
- **REQUIRED_PRECONDITIONS:** User research, task analysis, support/recovery ownership, accessible interfaces and measurement of real outcomes rather than completion. Identity mechanisms must be usable across normal and recovery contexts; assurance level must not exceed task need without reason. Users need clear authority boundaries and an attainable legitimate route; otherwise bypass becomes rational. Usability evaluation must use the deployed interface/policy and realistic devices/workflows. Observe abandonment, bypass, support load, warning behaviour and recovery failures without surveillance disproportionate to need. Recovery is part of the primary design; it must resist impersonation while remaining usable for legitimate loss/failure.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Security burden is context-sensitive; no interface removes all social engineering. Strong controls can still be necessary despite friction. Contrary evidence: Usable-security studies are often context-specific; behavioural endpoints do not directly measure prevented compromise.
- **ANTI_CEREMONY_BOUNDARY:** A training module, warning banner or 'security culture' campaign is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P04/P06/P16: stronger authority controls can add burden; P49: privacy/accessibility.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **psychological acceptability and usable security** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for psychological acceptability and usable security remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Users bypass controls; warnings become rote acknowledgement; recovery channels are weaker than authentication; administrators make errors in overly complex policy. — or would it add ceremony without changing the engineering decision?

### P12 — Attack-surface minimisation

- **PROPERTY_ID:** P12
- **PROPERTY_NAME:** Attack-surface minimisation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces reachable adversarial paths and the amount of mechanism that must be patched, monitored and assured.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can discover and interact with exposed or indirectly reachable interfaces, including through dependencies and compromised insiders.
- **FAILURE_MODE:** Unused features remain enabled; hidden management paths bypass policy; decomposition multiplies interfaces; surface counts ignore consequence and reachability.
- **MATURE_FORM:** Continuously minimise reachable consequential functionality while preserving observability, interoperability and recovery that have explicit consumers.
- **TRIGGER:** Internet/tenant exposure, privileged services, complex parsers, legacy features, broad egress, agent tools and unmaintained dependencies.
- **CHEAP_PATH:** For isolated low-consequence systems, rely on safe platform defaults and remove obvious unused services rather than perform exhaustive attack-surface modelling.
- **TRUST_BOUNDARY_PROFILE:** Exposed authentication/recovery interfaces and machine identities are included, not only network ports. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Administrative and deployment paths count as surface; who can enable features or add integrations is bounded. Exposed authentication/recovery interfaces and machine identities are included, not only network ports.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Internet/tenant exposure, privileged services, complex parsers, legacy features, broad egress, agent tools and unmaintained dependencies. Configuration/provenance: Actual enabled configuration and reachable dependency graph, not product documentation, define the surface. Recovery: Removal must preserve needed recovery/diagnostic paths or provide a controlled replacement.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=HIGH. Critical evidence: [S085] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: External and internal exposure monitoring detects newly reachable services, identities and paths. Recovery: Removal must preserve needed recovery/diagnostic paths or provide a controlled replacement.
- **REQUIRED_PRECONDITIONS:** Accurate runtime/dependency/interface inventory; ability to retire features; owner acceptance of compatibility trade-offs. Exposed authentication/recovery interfaces and machine identities are included, not only network ports. Administrative and deployment paths count as surface; who can enable features or add integrations is bounded. Actual enabled configuration and reachable dependency graph, not product documentation, define the surface. External and internal exposure monitoring detects newly reachable services, identities and paths. Removal must preserve needed recovery/diagnostic paths or provide a controlled replacement.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=MODERATE; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** More components can improve isolation and maintainability; minimality without consequence/reachability analysis can damage resilience. Contrary evidence: Attack-surface measures have weak standardisation and can reward hiding interfaces rather than reducing meaningful exploit paths.
- **ANTI_CEREMONY_BOUNDARY:** A hardening checklist or 'microservice' decomposition is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P40/P44: observability, diagnostics, interoperability and recovery paths may require retained interfaces.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **attack-surface minimisation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for attack-surface minimisation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Unused features remain enabled; hidden management paths bypass policy; decomposition multiplies interfaces; surface counts ignore consequence and reachability. — or would it add ceremony without changing the engineering decision?

### P13 — Isolation, compartmentalisation and blast-radius limitation

- **PROPERTY_ID:** P13
- **PROPERTY_NAME:** Isolation, compartmentalisation and blast-radius limitation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Contains confidentiality/integrity loss, lateral authority and service impact to an explicitly bounded domain.
- **THREAT_OR_ADVERSARY_PROFILE:** At least one compartment may be fully compromised; boundary mechanism and its lower layers remain within stated assumptions.
- **FAILURE_MODE:** Separate processes share credentials/files; containers rely on a compromised host; network segmentation does not constrain application authority; operational bridges defeat partitioning.
- **MATURE_FORM:** Choose compartments by consequence and compromise propagation; enforce and continuously verify crossings, shared roots and recovery independence.
- **TRIGGER:** Multi-tenant data, untrusted code/plugins, high-value secrets, distinct safety/mission domains, supply-chain stages and recovery infrastructure.
- **CHEAP_PATH:** For single-user low-consequence work, standard OS process/account isolation may be sufficient; do not add orchestration layers solely for labels.
- **TRUST_BOUNDARY_PROFILE:** Principals and workload identities are distinct across compartments; shared root accounts defeat the claim. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Each compartment has scoped administration; bridge services cannot act as unconstrained confused deputies. Principals and workload identities are distinct across compartments; shared root accounts defeat the claim.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Multi-tenant data, untrusted code/plugins, high-value secrets, distinct safety/mission domains, supply-chain stages and recovery infrastructure. Configuration/provenance: Runtime topology, mounts, devices, network policy, credentials and host/firmware state match the isolation claim. Recovery: Compromise response can isolate/rebuild one domain and verify that trust has not crossed into recovery sources.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=HIGH; adversarial=HIGH. Critical evidence: [S109] [S111] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Cross-boundary flows, policy denials and resource exhaustion are observable; monitoring itself does not erase separation. Recovery: Compromise response can isolate/rebuild one domain and verify that trust has not crossed into recovery sources.
- **REQUIRED_PRECONDITIONS:** Enforced boundary, bounded shared dependencies, resource isolation, operational ownership and usable cross-domain workflow. Principals and workload identities are distinct across compartments; shared root accounts defeat the claim. Each compartment has scoped administration; bridge services cannot act as unconstrained confused deputies. Runtime topology, mounts, devices, network policy, credentials and host/firmware state match the isolation claim. Cross-boundary flows, policy denials and resource exhaustion are observable; monitoring itself does not erase separation. Compromise response can isolate/rebuild one domain and verify that trust has not crossed into recovery sources.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Isolation is never absolute and can increase latency/cost. Containers, network zones or microservices do not automatically provide security boundaries. Contrary evidence: Strong isolation can be expensive, and empirical comparisons across architectures are sparse.
- **ANTI_CEREMONY_BOUNDARY:** A separate process, container, subnet or account is evidence only after its isolation guarantees and shared dependencies are established.
- **POSSIBLE_CONFLICTING_PROPERTY:** P44/P49: interoperability, efficiency and fail-operational continuity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **isolation, compartmentalisation and blast-radius limitation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for isolation, compartmentalisation and blast-radius limitation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Separate processes share credentials/files; containers rely on a compromised host; network segmentation does not constrain application authority; operational bridges defeat partitioning. — or would it add ceremony without changing the engineering decision?

### P14 — Defence in depth with independence and common-mode caveats

- **PROPERTY_ID:** P14
- **PROPERTY_NAME:** Defence in depth with independence and common-mode caveats
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Maintains a protected objective or enables detection/containment when one control fails.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may defeat one layer; remaining layers are sufficiently independent in mechanism, authority, data and failure mode.
- **FAILURE_MODE:** Product stacking creates correlated complexity; all controls trust the same identity, signature, cloud plane or telemetry; layers impede operations but do not block distinct paths.
- **MATURE_FORM:** Use the smallest set of mutually informative mechanisms needed to cover material paths and failure modes, with explicit shared dependencies.
- **TRIGGER:** High-consequence systems, uncertain adversary capability, externally exposed services and unavoidable residual vulnerabilities.
- **CHEAP_PATH:** For low-exposure reversible work, one strong deterministic control plus recovery may outperform many weak layers.
- **TRUST_BOUNDARY_PROFILE:** Identity/control-plane compromise is explicitly tested against every layer. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Policy and administrative authorities are separated or consciously shared; a common administrator is a recorded dependency. Identity/control-plane compromise is explicitly tested against every layer.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: High-consequence systems, uncertain adversary capability, externally exposed services and unavoidable residual vulnerabilities. Configuration/provenance: Layer configuration/provenance and shared components are traceable. Recovery: Recovery remains possible when preventive layers deny or corrupt access.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S003] [S008] [S085] [S086].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Failure of a layer and operation of subsequent detection/containment are observable. Recovery: Recovery remains possible when preventive layers deny or corrupt access.
- **REQUIRED_PRECONDITIONS:** Clear security objective/path model, interaction analysis, operational capacity and evidence that layers are not merely duplicated. Identity/control-plane compromise is explicitly tested against every layer. Policy and administrative authorities are separated or consciously shared; a common administrator is a recorded dependency. Layer configuration/provenance and shared components are traceable. Failure of a layer and operation of subsequent detection/containment are observable. Recovery remains possible when preventive layers deny or corrupt access.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** There is little evidence that arbitrary control counts improve outcomes; complexity is itself attack surface and operational risk. Contrary evidence: Independence is difficult to measure and diverse controls can increase failure probability.
- **ANTI_CEREMONY_BOUNDARY:** A vendor stack, control count or overlapping scanners is not defence in depth.
- **POSSIBLE_CONFLICTING_PROPERTY:** P08/P09/P47/P48: common-mode complexity and tool/process accumulation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **defence in depth with independence and common-mode caveats** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for defence in depth with independence and common-mode caveats remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Product stacking creates correlated complexity; all controls trust the same identity, signature, cloud plane or telemetry; layers impede operations but do not block distinct paths. — or would it add ceremony without changing the engineering decision?

### P15 — Secure defaults and safe configurability

- **PROPERTY_ID:** P15
- **PROPERTY_NAME:** Secure defaults and safe configurability
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevents predictable misconfiguration, exposed management interfaces, weak authentication and unnecessary services at initial and routine operation.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary exploits default credentials/settings, broadly exposed services or operational overrides; operators have limited expertise/time.
- **FAILURE_MODE:** Defaults break legacy workflows, are immediately disabled, hide consequential trade-offs or become stale; 'secure' default blocks recovery/availability.
- **MATURE_FORM:** Default state covers the common consequential case, risky options require informed bounded action, and operators retain tested availability/recovery routes.
- **TRIGGER:** Products/services used at scale, by non-specialists, with internet exposure or complex configurable security.
- **CHEAP_PATH:** For expert-controlled experimental/offline systems, concise documented setup with deterministic checks may substitute for broad default automation.
- **TRUST_BOUNDARY_PROFILE:** Default identity/authentication meets typical consequence; enrolment and recovery do not create universal bypass. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Risky overrides require appropriate authority and cannot be silently inherited. Default identity/authentication meets typical consequence; enrolment and recovery do not create universal bypass.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Products/services used at scale, by non-specialists, with internet exposure or complex configurable security. Configuration/provenance: Actual deployment is compared to versioned baseline; defaults are tied to product/version and updated when threats change. Recovery: Safe rollback and account/service recovery prevent secure defaults becoming lockout or outage traps.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S098] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Overrides, drift and disabled protections are visible to operators and customers. Recovery: Safe rollback and account/service recovery prevent secure defaults becoming lockout or outage traps.
- **REQUIRED_PRECONDITIONS:** Vendor/product ownership of safe baseline; compatibility and recovery testing; clear configuration semantics. Default identity/authentication meets typical consequence; enrolment and recovery do not create universal bypass. Risky overrides require appropriate authority and cannot be silently inherited. Actual deployment is compared to versioned baseline; defaults are tied to product/version and updated when threats change. Overrides, drift and disabled protections are visible to operators and customers. Safe rollback and account/service recovery prevent secure defaults becoming lockout or outage traps.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Secure-by-default claims are mainly guidance/programme commitments; comparative outcome evidence is limited and sector context matters. Contrary evidence: Outcome attribution is difficult; strict defaults can shift costs to interoperability, accessibility and emergency operations.
- **ANTI_CEREMONY_BOUNDARY:** A 'secure mode' label or hardening guide does not satisfy the property if ordinary deployment remains unsafe.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P38/P46/P49: legacy compatibility, forced updates, user autonomy and availability.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **secure defaults and safe configurability** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for secure defaults and safe configurability remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Defaults break legacy workflows, are immediately disabled, hide consequential trade-offs or become stale; 'secure' default blocks recovery/availability. — or would it add ceremony without changing the engineering decision?

### P16 — Identity proofing, authentication and authorization separation

- **PROPERTY_ID:** P16
- **PROPERTY_NAME:** Identity proofing, authentication and authorization separation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevents impersonation and over-authorisation while preserving accountable, context-specific resource access.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may enrol fraudulently, steal/phish authenticators, compromise federation, reuse tokens or be a legitimate principal acting outside authority.
- **FAILURE_MODE:** Authenticated attacker is authorised broadly; recovery bypasses proofing; token audience/context is wrong; federation claims exceed local intent.
- **MATURE_FORM:** Use only necessary identity assurance, then make current resource/parameter authorization explicit; independently secure enrolment, session, delegation, revocation and recovery.
- **TRIGGER:** Personal data/financial/administrative access, remote service, federation, machine/agent actions and any consequential attribution.
- **CHEAP_PATH:** For public or low-consequence pseudonymous services, minimal proofing or anonymous authorization may be correct; do not collect identity unnecessarily.
- **TRUST_BOUNDARY_PROFILE:** Current identity evidence and assurance are appropriate to consequence; claimed identity is not accepted solely from self-assertion. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Local resource owners retain authorization authority; identity providers do not implicitly grant business authority. Current identity evidence and assurance are appropriate to consequence; claimed identity is not accepted solely from self-assertion.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Personal data/financial/administrative access, remote service, federation, machine/agent actions and any consequential attribution. Configuration/provenance: Issuer/audience/policy/key versions and actual enforcement configuration are current and traceable. Recovery: Lost/compromised authenticators and identity-provider outage have tested recovery that does not weaken proofing universally.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=HIGH; adversarial=HIGH. Critical evidence: [S097] [S098] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Enrolment, authentication, recovery, token issuance, denial and privileged action are observable with data minimisation. Recovery: Lost/compromised authenticators and identity-provider outage have tested recovery that does not weaken proofing universally.
- **REQUIRED_PRECONDITIONS:** Trusted issuers, authenticator lifecycle, anti-replay/session protection, local policy and privacy minimisation. Current identity evidence and assurance are appropriate to consequence; claimed identity is not accepted solely from self-assertion. Local resource owners retain authorization authority; identity providers do not implicitly grant business authority. Issuer/audience/policy/key versions and actual enforcement configuration are current and traceable. Enrolment, authentication, recovery, token issuance, denial and privileged action are observable with data minimisation. Lost/compromised authenticators and identity-provider outage have tested recovery that does not weaken proofing universally.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Identity does not establish benign intent; stronger authentication can harm accessibility and availability. Privacy may favour less identity. Contrary evidence: Current guidance is strong, but comparative evidence for many assurance combinations is context-specific.
- **ANTI_CEREMONY_BOUNDARY:** An identity-provider integration or MFA-completion metric is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P49: privacy, accessibility and recovery burden; P44: identity-plane availability.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **identity proofing, authentication and authorization separation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for identity proofing, authentication and authorization separation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Authenticated attacker is authorised broadly; recovery bypasses proofing; token audience/context is wrong; federation claims exceed local intent. — or would it add ceremony without changing the engineering decision?

### P17 — Context- and parameter-bound delegated authority with confused-deputy resistance

- **PROPERTY_ID:** P17
- **PROPERTY_NAME:** Context- and parameter-bound delegated authority with confused-deputy resistance
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevents cross-tenant/object access, unauthorised transactions and escalation through delegated services or automation.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can invoke a legitimate deputy and manipulate object references, destinations, prompts, parameters or token context.
- **FAILURE_MODE:** Valid caller plus valid service yields invalid action; approval is logged but not bound to execution; token audience/scope permits substitution; agent tool call exceeds intent.
- **MATURE_FORM:** Every consequential delegated action carries only the authority needed for that exact resource and parameters, is revalidated at the deputy, and remains revocable/auditable.
- **TRIGGER:** Cross-service delegation, payments/destructive operations, cloud roles, callbacks, agents/tools, file/object references and automation with ambient credentials.
- **CHEAP_PATH:** For an internal low-consequence operation with one resource and no delegation, ordinary local authorization plus input validation may suffice.
- **TRUST_BOUNDARY_PROFILE:** Caller, deputy and target identities are distinct; authenticated caller does not inherit deputy authority. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Delegates can exercise only explicitly conferred rights and cannot re-delegate unless allowed. Caller, deputy and target identities are distinct; authenticated caller does not inherit deputy authority.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Cross-service delegation, payments/destructive operations, cloud roles, callbacks, agents/tools, file/object references and automation with ambient credentials. Configuration/provenance: Token/approval/action refer to exact current resource, environment, policy and code path; replay/substitution is prevented. Recovery: Revocation/recovery reaches downstream delegated sessions and agent/tool credentials.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=HIGH; adversarial=HIGH. Critical evidence: [S109] [S115] [S116].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Log delegation chain, target, parameters and outcome; detect unexpected cross-domain use. Recovery: Revocation/recovery reaches downstream delegated sessions and agent/tool credentials.
- **REQUIRED_PRECONDITIONS:** Canonical resource/action identity, non-ambiguous parameter semantics, local mediation and bounded delegation chain. Caller, deputy and target identities are distinct; authenticated caller does not inherit deputy authority. Delegates can exercise only explicitly conferred rights and cannot re-delegate unless allowed. Token/approval/action refer to exact current resource, environment, policy and code path; replay/substitution is prevented. Log delegation chain, target, parameters and outcome; detect unexpected cross-domain use. Revocation/recovery reaches downstream delegated sessions and agent/tool credentials.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Capability granularity and delegation can be difficult to manage; parameter binding is domain-specific and proofs may omit user-interface deception. Contrary evidence: Implementations are highly context-specific; a formally scoped token can still authorise a semantically deceptive action.
- **ANTI_CEREMONY_BOUNDARY:** A generic 'RBAC role', signed approval record or valid OAuth token is not enough.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P60: semantic clarity/usability of parameter-bound authority, especially for agents.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **context- and parameter-bound delegated authority with confused-deputy resistance** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for context- and parameter-bound delegated authority with confused-deputy resistance remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Valid caller plus valid service yields invalid action; approval is logged but not bound to execution; token audience/scope permits substitution; agent tool call exceeds intent. — or would it add ceremony without changing the engineering decision?

### P18 — Short-lived authority, revocation, expiry and reauthentication

- **PROPERTY_ID:** P18
- **PROPERTY_NAME:** Short-lived authority, revocation, expiry and reauthentication
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces persistence and exposure window after credential compromise or authority change.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can obtain valid credentials/tokens and continue using them; revocation channels may be delayed or unavailable.
- **FAILURE_MODE:** Long-lived keys/tokens; revocation does not propagate; clock/freshness errors; reauthentication is ritual without context change; offline systems cannot operate.
- **MATURE_FORM:** Authority expires at a consequence-proportionate horizon, can be revoked across all dependent planes, and is renewed using current identity/context evidence.
- **TRIGGER:** Privileged, remote, machine, federated and delegated authority; high-value sessions; post-incident containment.
- **CHEAP_PATH:** For low-consequence, offline or availability-critical work, longer bounded credentials may be justified with local containment and later reconciliation.
- **TRUST_BOUNDARY_PROFILE:** Identity remains resolvable and compromise signals are meaningful; device/workload posture evidence is current enough. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Revokers and issuers are trusted and separated as needed; expiry cannot be extended silently by holders. Identity remains resolvable and compromise signals are meaningful; device/workload posture evidence is current enough.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Privileged, remote, machine, federated and delegated authority; high-value sessions; post-incident containment. Configuration/provenance: Credential/token/key versions, issuance source and deployed validation policy are known. Recovery: Outage/recovery allows bounded local authority and restoration of issuer/revocation trust.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=HIGH. Critical evidence: [S097] [S098] [S114].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe issuance, refresh, revocation failure and use after intended expiry without leaking secrets. Recovery: Outage/recovery allows bounded local authority and restoration of issuer/revocation trust.
- **REQUIRED_PRECONDITIONS:** Reliable time/freshness, credential inventory, revocation distribution, identity availability and usable renewal. Identity remains resolvable and compromise signals are meaningful; device/workload posture evidence is current enough. Revokers and issuers are trusted and separated as needed; expiry cannot be extended silently by holders. Credential/token/key versions, issuance source and deployed validation policy are known. Observe issuance, refresh, revocation failure and use after intended expiry without leaking secrets. Outage/recovery allows bounded local authority and restoration of issuer/revocation trust.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Expiry is not revocation and does not remove already-created persistence or downstream effects. Central identity availability becomes a resilience dependency. Contrary evidence: Comparative evidence for optimal lifetimes is sparse; availability/usability costs can outweigh marginal security for low-risk contexts.
- **ANTI_CEREMONY_BOUNDARY:** A password-rotation calendar or token TTL alone is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P20/P44: offline/recovery operation and central issuer dependency.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **short-lived authority, revocation, expiry and reauthentication** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for short-lived authority, revocation, expiry and reauthentication remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Long-lived keys/tokens; revocation does not propagate; clock/freshness errors; reauthentication is ritual without context change; offline systems cannot operate. — or would it add ceremony without changing the engineering decision?

### P19 — Workload, machine and agent identity with bounded delegation

- **PROPERTY_ID:** P19
- **PROPERTY_NAME:** Workload, machine and agent identity with bounded delegation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Authentic service-to-service action, tenant isolation, accountable automation and constrained machine/agent authority.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary can steal workload credentials, launch lookalike instances, compromise orchestration or inject/redirect agent actions.
- **FAILURE_MODE:** Identity outlives workload; image/runtime provenance is unbound; shared keys span fleets; agent identity is confused with user intent; control plane mints arbitrary identity.
- **MATURE_FORM:** Each non-human actor has a unique short-lived identity bound to current execution context and only the delegated authority needed for its task.
- **TRIGGER:** Cloud-native services, ephemeral workloads, CI/CD, service meshes, autonomous agents and machine-to-machine high-consequence operations.
- **CHEAP_PATH:** For a small single-host process tree, OS account/process isolation and local credentials may be sufficient.
- **TRUST_BOUNDARY_PROFILE:** Machine identity does not replace responsible human/organisation ownership; user delegation is separately represented. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Issuers and platform administrators are bounded; agent/tool permissions are attenuated and cannot silently inherit all user authority. Machine identity does not replace responsible human/organisation ownership; user delegation is separately represented.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Cloud-native services, ephemeral workloads, CI/CD, service meshes, autonomous agents and machine-to-machine high-consequence operations. Configuration/provenance: Identity binds to code/image, deployment, environment and version where consequence warrants. Recovery: Rebuild/revoke workloads and issuers without losing all service; retain clean bootstrap roots.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S109] [S111].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe identity issuance, unexpected geography/topology, delegation and use after workload termination. Recovery: Rebuild/revoke workloads and issuers without losing all service; retain clean bootstrap roots.
- **REQUIRED_PRECONDITIONS:** Trusted issuance/orchestration, unique workload lifecycle, key protection, time and local authorization. Machine identity does not replace responsible human/organisation ownership; user delegation is separately represented. Issuers and platform administrators are bounded; agent/tool permissions are attenuated and cannot silently inherit all user authority. Identity binds to code/image, deployment, environment and version where consequence warrants. Observe identity issuance, unexpected geography/topology, delegation and use after workload termination. Rebuild/revoke workloads and issuers without losing all service; retain clean bootstrap roots.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Workload identity centralises trust and cannot prove software benignness. Agent identity/intent semantics remain immature. Contrary evidence: Strong field-practice and guidance support exists for workloads; agentic systems have limited comparative/incident evidence and rapidly changing assumptions.
- **ANTI_CEREMONY_BOUNDARY:** A service account, mesh certificate or agent name is not sufficient.
- **POSSIBLE_CONFLICTING_PROPERTY:** P08/P44/P60: workload issuer/control-plane common mode and agent semantic ambiguity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **workload, machine and agent identity with bounded delegation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for workload, machine and agent identity with bounded delegation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Identity outlives workload; image/runtime provenance is unbound; shared keys span fleets; agent identity is confused with user intent; control plane mints arbitrary identity. — or would it add ceremony without changing the engineering decision?

### P20 — Emergency and break-glass authority with expiry, oversight and recovery

- **PROPERTY_ID:** P20
- **PROPERTY_NAME:** Emergency and break-glass authority with expiry, oversight and recovery
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Preserves availability, safety and recovery while bounding the security risk of exceptional authority.
- **THREAT_OR_ADVERSARY_PROFILE:** Emergency may be genuine or adversary-induced; attacker may trigger or obtain break-glass access; normal identity/policy infrastructure may be unavailable.
- **FAILURE_MODE:** Shared emergency credential leaks; use is unmonitored; exception never expires; trigger is vague; control-plane outage makes both normal and emergency access impossible.
- **MATURE_FORM:** A tested exceptional path that minimises combined safety/availability/security harm and restores normal trust immediately after use.
- **TRIGGER:** Safety/availability-critical operations, incident containment/reconstitution and rare cases where normal policy cannot meet consequence.
- **CHEAP_PATH:** No break-glass path for systems where all actions are easily reversible and normal privileged workflow remains available.
- **TRUST_BOUNDARY_PROFILE:** Emergency identity proofing must work under degraded conditions without a universal weak fallback. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Authority to declare emergency and to exercise access are separated where feasible; all expansions expire. Emergency identity proofing must work under degraded conditions without a universal weak fallback.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Safety/availability-critical operations, incident containment/reconstitution and rare cases where normal policy cannot meet consequence. Configuration/provenance: Emergency policy/configuration is versioned and verified as part of deployment, not improvised. Recovery: Post-emergency rekey/revocation and restoration of normal authority are mandatory.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S097] [S109] [S114].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Use creates high-priority tamper-resistant evidence and triggers review; covert use is a failure. Recovery: Post-emergency rekey/revocation and restoration of normal authority are mandatory.
- **REQUIRED_PRECONDITIONS:** Explicit emergency scenarios, protected/accessible credentials, independent telemetry, policy owner and exercises. Emergency identity proofing must work under degraded conditions without a universal weak fallback. Authority to declare emergency and to exercise access are separated where feasible; all expansions expire. Emergency policy/configuration is versioned and verified as part of deployment, not improvised. Use creates high-priority tamper-resistant evidence and triggers review; covert use is a failure. Post-emergency rekey/revocation and restoration of normal authority are mandatory.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Break-glass creates an attractive bypass and can normalise privilege. Evidence is domain-specific and operational exercises are essential. Contrary evidence: No universal evidence establishes optimal approval or access design; threat and operational context dominate.
- **ANTI_CEREMONY_BOUNDARY:** A documented 'break glass' account without bounded trigger, monitoring and expiry is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P04/P07/P42: least privilege, separation and attacker abuse of emergency paths.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **emergency and break-glass authority with expiry, oversight and recovery** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for emergency and break-glass authority with expiry, oversight and recovery remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Shared emergency credential leaks; use is unmonitored; exception never expires; trigger is vague; control-plane outage makes both normal and emergency access impossible. — or would it add ceremony without changing the engineering decision?

### P21 — Secrets, keys and certificates as an authority lifecycle

- **PROPERTY_ID:** P21
- **PROPERTY_NAME:** Secrets, keys and certificates as an authority lifecycle
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Confidentiality, authenticity and bounded control of identities, updates, transactions and protected data across the full system lifecycle.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may steal credentials, compromise issuers/signers or management planes, observe accidental exposure, or exploit obsolete algorithms/protocols.
- **FAILURE_MODE:** Long-lived shared secrets; secret in source/logs/images; one key serves many purposes; untested rotation; revocation does not propagate; lost key destroys availability; compromised signer remains trusted.
- **MATURE_FORM:** Treat every secret/key as scoped, expiring authority with known consumers, provenance, revocation propagation and tested loss/compromise recovery.
- **TRIGGER:** Any secret that grants consequential access, decrypts durable data, signs software/identity, anchors trust or cannot be cheaply replaced.
- **CHEAP_PATH:** For local low-consequence ephemeral data, platform-provided credential stores and automatic short-lived credentials may be sufficient; avoid custom key infrastructure.
- **TRUST_BOUNDARY_PROFILE:** Each secret is tied to a known principal/workload and assurance level; anonymous shared secrets are exceptional. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Key holders/issuers/signers have scoped authority and separation where consequence warrants. Each secret is tied to a known principal/workload and assurance level; anonymous shared secrets are exceptional.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Any secret that grants consequential access, decrypts durable data, signs software/identity, anchors trust or cannot be cheaply replaced. Configuration/provenance: Key identity/version, algorithm, environment, artifact/data scope and dependent configurations are traceable. Recovery: Loss/compromise scenarios have tested rekey, data recovery and trust re-establishment; backups do not recreate revoked authority.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=HIGH; adversarial=HIGH. Critical evidence: [S064] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Key identity/version, algorithm, environment, artifact/data scope and dependent configurations are traceable.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Use, anomalous access, issuance, expiry and failed rotation are observable without logging secret material. Recovery: Loss/compromise scenarios have tested rekey, data recovery and trust re-establishment; backups do not recreate revoked authority.
- **REQUIRED_PRECONDITIONS:** Accurate authority/secret inventory, trustworthy entropy/time, protected issuers/storage, deployable rotation and ownership. Each secret is tied to a known principal/workload and assurance level; anonymous shared secrets are exceptional. Key holders/issuers/signers have scoped authority and separation where consequence warrants. Key identity/version, algorithm, environment, artifact/data scope and dependent configurations are traceable. Use, anomalous access, issuance, expiry and failed rotation are observable without logging secret material. Loss/compromise scenarios have tested rekey, data recovery and trust re-establishment; backups do not recreate revoked authority.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Cryptography relocates rather than eliminates trust. Hardware protection and certificate automation do not secure compromised issuers or authorised misuse. Contrary evidence: Optimal rotation intervals and storage mechanisms are context-specific; stronger protection can increase availability and recovery concentration.
- **ANTI_CEREMONY_BOUNDARY:** A vault, HSM, encryption-at-rest badge or rotation ticket is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P40/P43/P49: forensics, recoverability and availability versus confidentiality/key revocation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **secrets, keys and certificates as an authority lifecycle** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for secrets, keys and certificates as an authority lifecycle remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Long-lived shared secrets; secret in source/logs/images; one key serves many purposes; untested rotation; revocation does not propagate; lost key destroys availability; compromised signer remains trusted. — or would it add ceremony without changing the engineering decision?

### P22 — Security requirements, invariants and unacceptable states

- **PROPERTY_ID:** P22
- **PROPERTY_NAME:** Security requirements, invariants and unacceptable states
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Preservation of precisely stated confidentiality, integrity, authority, availability, authenticity, privacy or mission constraints.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary intentionally seeks boundary cases, composition gaps and state transitions omitted from ordinary functional requirements.
- **FAILURE_MODE:** Requirement only names a control; invariant omits exceptional/recovery states; conflicts are hidden; test oracle is unavailable; requirement is stale.
- **MATURE_FORM:** A minimal, current set of decision-relevant security invariants with explicit assumptions, negative states and lifecycle evidence.
- **TRIGGER:** High-consequence features, trust-boundary transitions, ambiguous policy, formal assurance targets and acceptance decisions.
- **CHEAP_PATH:** For low-risk reversible features, a few executable negative checks and clear authorization rules can replace a large specification.
- **TRUST_BOUNDARY_PROFILE:** Identity and principal semantics are explicit enough to state who may act. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Policy owner and risk acceptor are named; implementers cannot reinterpret obligation silently. Identity and principal semantics are explicit enough to state who may act.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: High-consequence features, trust-boundary transitions, ambiguous policy, formal assurance targets and acceptance decisions. Configuration/provenance: Requirement version maps to current design, code, deployment and supplier state. Recovery: Recovery and degraded states are part of the requirement, not assumed outside normal operation.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=LIMITED; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S081] [S082] [S090] [S091].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Runtime/test evidence can discriminate invariant satisfaction; unknown/untestable claims are marked. Recovery: Recovery and degraded states are part of the requirement, not assumed outside normal operation.
- **REQUIRED_PRECONDITIONS:** Protected consequence, bounded model, stable terminology, decision authority and feasible evidence/oracle. Identity and principal semantics are explicit enough to state who may act. Policy owner and risk acceptor are named; implementers cannot reinterpret obligation silently. Requirement version maps to current design, code, deployment and supplier state. Runtime/test evidence can discriminate invariant satisfaction; unknown/untestable claims are marked. Recovery and degraded states are part of the requirement, not assumed outside normal operation.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Complete security specification is infeasible; adversarial creativity and emergent composition limit closure. Contrary evidence: Formal precision does not guarantee correct or complete objectives; empirical comparative evidence for requirements methods is limited.
- **ANTI_CEREMONY_BOUNDARY:** A requirements document, traceability matrix or compliance statement is optional and insufficient by itself.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48: precision/assurance depth versus change speed and low consequence.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **security requirements, invariants and unacceptable states** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for security requirements, invariants and unacceptable states remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Requirement only names a control; invariant omits exceptional/recovery states; conflicts are hidden; test oracle is unavailable; requirement is stale. — or would it add ceremony without changing the engineering decision?

### P23 — Security architecture and design review

- **PROPERTY_ID:** P23
- **PROPERTY_NAME:** Security architecture and design review
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevents structural confidentiality, integrity, availability and blast-radius failures and creates an assurance/recovery design that can be implemented.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary exploits composition and authority paths, shared dependencies and exceptional states rather than only individual code defects.
- **FAILURE_MODE:** Review occurs after decisions are irreversible; reviewers lack deployment context; checklist replaces adversarial reasoning; findings are not owned; architecture drifts.
- **MATURE_FORM:** Depth scales to consequence and novelty; every material trust/authority change receives independent-enough challenge, with decisions, assumptions and evidence consumers recorded.
- **TRIGGER:** New system, material boundary/identity/dependency change, high-consequence feature, major migration or repeated incident class.
- **CHEAP_PATH:** For a small reversible change within an established boundary, a focused differential review of changed assumptions/interfaces is the cheap path.
- **TRUST_BOUNDARY_PROFILE:** Identity issuers, proofing, workload identity and recovery are part of architecture, not external boxes. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Review establishes who grants/changes authority and where enforcement occurs. Identity issuers, proofing, workload identity and recovery are part of architecture, not external boxes.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: New system, material boundary/identity/dependency change, high-consequence feature, major migration or repeated incident class. Configuration/provenance: Design reviewed must map to deployed configuration/build/dependency state; deviations are tracked. Recovery: Containment/reconstitution and safe degraded operation are design subjects.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S109] [S110] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Review specifies evidence needed to observe boundary violations and control failure. Recovery: Containment/reconstitution and safe degraded operation are design subjects.
- **REQUIRED_PRECONDITIONS:** Current architecture, capable reviewers, authority to change design and explicit review questions linked to consequences. Identity issuers, proofing, workload identity and recovery are part of architecture, not external boxes. Review establishes who grants/changes authority and where enforcement occurs. Design reviewed must map to deployed configuration/build/dependency state; deviations are tracked. Review specifies evidence needed to observe boundary violations and control failure. Containment/reconstitution and safe degraded operation are design subjects.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Architecture review effectiveness is difficult to isolate empirically; excessive process can overwhelm low-risk change. Contrary evidence: Mostly guidance and case-based support; controlled outcome evidence for design-review regimes is sparse.
- **ANTI_CEREMONY_BOUNDARY:** A standing security review board or template is not required.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48: review depth versus delivery; P31: reviewer independence cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **security architecture and design review** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for security architecture and design review remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Review occurs after decisions are irreversible; reviewers lack deployment context; checklist replaces adversarial reasoning; findings are not owned; architecture drifts. — or would it add ceremony without changing the engineering decision?

### P24 — Continuous secure lifecycle: security feedback everywhere

- **PROPERTY_ID:** P24
- **PROPERTY_NAME:** Continuous secure lifecycle: security feedback everywhere
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces preventable vulnerabilities and preserves security claims as systems and threats change.
- **THREAT_OR_ADVERSARY_PROFILE:** Adaptive attackers exploit design, implementation, dependency, deployment, identity, operations and recovery weaknesses.
- **FAILURE_MODE:** 'Shift left' becomes scanner insertion; security gates delay delivery but runtime drift remains; ownership fragments; findings do not change architecture.
- **MATURE_FORM:** Security work occurs wherever a consequential assumption can be introduced or invalidated, with lightweight defaults for ordinary changes and deeper assurance for high-adversarial-pressure claims.
- **TRIGGER:** Products/services with ongoing change, exposed attack surface, dependencies and material consequence.
- **CHEAP_PATH:** For low-risk/reversible changes, reuse established secure defaults and deterministic automated checks; escalate only when boundary, authority or consequence changes.
- **TRUST_BOUNDARY_PROFILE:** Identity/credential lifecycle is included from enrolment through revocation and retirement. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Security decisions and exceptions have owners and expiries across phases. Identity/credential lifecycle is included from enrolment through revocation and retirement.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Products/services with ongoing change, exposed attack surface, dependencies and material consequence. Configuration/provenance: Source/build/release/deployment identity and change history support evidence continuity. Recovery: Patch, rollback, reconstitution and decommissioning paths are engineered and exercised.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S087] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Telemetry, disclosure intake and incident learning close the feedback loop. Recovery: Patch, rollback, reconstitution and decommissioning paths are engineered and exercised.
- **REQUIRED_PRECONDITIONS:** Product security ownership, version/configuration/provenance traceability, feedback channels and authority to remediate. Identity/credential lifecycle is included from enrolment through revocation and retirement. Security decisions and exceptions have owners and expiries across phases. Source/build/release/deployment identity and change history support evidence continuity. Telemetry, disclosure intake and incident learning close the feedback loop. Patch, rollback, reconstitution and decommissioning paths are engineered and exercised.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=MODERATE; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Integrated-programme benefits are often asserted by guidance/case studies rather than causal trials; mature practice must avoid tool/process accumulation. Contrary evidence: Comparative field evidence across complete lifecycle programmes remains limited and confounded by organisation size/capability.
- **ANTI_CEREMONY_BOUNDARY:** A DevSecOps platform, SDL checklist or 'shift left' slogan is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P48: process depth and cheap path; P09/P30: stable high-assurance components versus rapid change.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **continuous secure lifecycle: security feedback everywhere** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for continuous secure lifecycle: security feedback everywhere remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — 'Shift left' becomes scanner insertion; security gates delay delivery but runtime drift remains; ownership fragments; findings do not change architecture. — or would it add ceremony without changing the engineering decision?

### P25 — Change-aware threat-model and security-claim currentness

- **PROPERTY_ID:** P25
- **PROPERTY_NAME:** Change-aware threat-model and security-claim currentness
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Preserves relevance of design and assurance decisions under continuous system and threat change.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary exploits newly introduced paths, stale trust or delayed detection; change may be legitimate, malicious or environmental.
- **FAILURE_MODE:** Annual review misses drift; model version not linked to deployment; updates add dependencies/permissions; external service semantics change silently.
- **MATURE_FORM:** Security models and evidence identify the state they cover, their invalidators and last discriminating review; low-risk changes inherit only within stated envelopes.
- **TRIGGER:** Boundary, privilege, dependency, exposed API, cryptographic, identity, deployment or recovery change; new exploitation/incident evidence.
- **CHEAP_PATH:** Routine change entirely within a proven envelope uses automated invariant checks and records why the model remains valid.
- **TRUST_BOUNDARY_PROFILE:** Identity issuer/policy/recovery changes are model changes even without application-code change. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Changes to who can approve/deploy/administer are first-class triggers. Identity issuer/policy/recovery changes are model changes even without application-code change.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Boundary, privilege, dependency, exposed API, cryptographic, identity, deployment or recovery change; new exploitation/incident evidence. Configuration/provenance: Claims carry version/commit/artifact/deployment/dependency identifiers and freshness metadata. Recovery: Rollback/recovery changes are included; previous secure state is not assumed recoverable without proof.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S109] [S110] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Claims carry version/commit/artifact/deployment/dependency identifiers and freshness metadata.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Continuous monitoring reveals divergence and model assumptions have observable proxies where possible. Recovery: Rollback/recovery changes are included; previous secure state is not assumed recoverable without proof.
- **REQUIRED_PRECONDITIONS:** Change inventory, configuration/provenance identity, ownership and an analysable security baseline. Identity issuer/policy/recovery changes are model changes even without application-code change. Changes to who can approve/deploy/administer are first-class triggers. Claims carry version/commit/artifact/deployment/dependency identifiers and freshness metadata. Continuous monitoring reveals divergence and model assumptions have observable proxies where possible. Rollback/recovery changes are included; previous secure state is not assumed recoverable without proof.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=MODERATE; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Complete semantic change detection is impossible; stable components can still face new adversary techniques without local change. Contrary evidence: Research on continuous threat-model maintenance is immature; operational burden and false-trigger rates are not well characterised.
- **ANTI_CEREMONY_BOUNDARY:** Updating a document date or rerunning the same scanner is not model currentness.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48: model-maintenance cost and trigger flood.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **change-aware threat-model and security-claim currentness** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for change-aware threat-model and security-claim currentness remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Annual review misses drift; model version not linked to deployment; updates add dependencies/permissions; external service semantics change silently. — or would it add ceremony without changing the engineering decision?

### P26 — Secure implementation and memory-safe construction where justified

- **PROPERTY_ID:** P26
- **PROPERTY_NAME:** Secure implementation and memory-safe construction where justified
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces implementation vulnerabilities that permit code execution, data/authority violation or denial of service.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary controls malformed inputs or execution timing and targets implementation undefined behaviour; legacy/toolchain constraints apply.
- **FAILURE_MODE:** Rules are untestable; unsafe escape hatches dominate; rewrite introduces semantic defects; memory safety is mistaken for complete security; generated code/dependencies remain unsafe.
- **MATURE_FORM:** Use construction techniques that deterministically remove material defect classes where exposure, consequence and maintenance horizon justify migration; assure residual unsafe boundaries.
- **TRIGGER:** Internet-facing parsers, privileged code, high-consequence components, new codebases and components with recurring memory-safety defects.
- **CHEAP_PATH:** For low-exposure scripts or constrained legacy patches, focused safe APIs, review and sandboxing may beat a rewrite; migration depth scales to consequence and lifecycle.
- **TRUST_BOUNDARY_PROFILE:** Implementation must preserve identity and authorization semantics; memory safety does not prevent authorised misuse. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Unsafe/privileged operations require explicit authority and review. Implementation must preserve identity and authorization semantics; memory safety does not prevent authorised misuse.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Internet-facing parsers, privileged code, high-consequence components, new codebases and components with recurring memory-safety defects. Configuration/provenance: Compiler/toolchain/build provenance and actual deployment protections are known. Recovery: Migration and rollback preserve service; compromised legacy components can be isolated/rebuilt.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=HIGH; adversarial=HIGH. Critical evidence: [S087] [S088] [S092].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Crash/sanitiser/fuzzing/telemetry reveal residual classes; production logging does not expose secrets. Recovery: Migration and rollback preserve service; compromised legacy components can be isolated/rebuilt.
- **REQUIRED_PRECONDITIONS:** Supported toolchain/ecosystem, skilled developers, performance/real-time validation and accurate unsafe-code/dependency inventory. Implementation must preserve identity and authorization semantics; memory safety does not prevent authorised misuse. Unsafe/privileged operations require explicit authority and review. Compiler/toolchain/build provenance and actual deployment protections are known. Crash/sanitiser/fuzzing/telemetry reveal residual classes; production logging does not expose secrets. Migration and rollback preserve service; compromised legacy components can be isolated/rebuilt.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Memory safety does not solve logic, authorization, cryptographic, social or configuration flaws; comparative field estimates are ecosystem-dependent. Contrary evidence: Cross-language causal comparisons and rewrite risk are difficult; memory-safe platforms can still contain unsafe runtimes/FFI and logic defects.
- **ANTI_CEREMONY_BOUNDARY:** A language mandate, secure-coding training completion or linter pass is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48/P49: rewrite cost, performance, stability and legacy/safety constraints.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **secure implementation and memory-safe construction where justified** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for secure implementation and memory-safe construction where justified remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Rules are untestable; unsafe escape hatches dominate; rewrite introduces semantic defects; memory safety is mistaken for complete security; generated code/dependencies remain unsafe. — or would it add ceremony without changing the engineering decision?

### P27 — Code review and static analysis as bounded evidence

- **PROPERTY_ID:** P27
- **PROPERTY_NAME:** Code review and static analysis as bounded evidence
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces known implementation, dependency/API misuse, secret exposure and policy violations within the analysed scope.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary exploits defects represented in source/intermediate forms; tool rules and reviewers have bounded coverage and shared assumptions.
- **FAILURE_MODE:** False positives create suppression; false negatives/unsupported frameworks; reviewer fatigue; generated/build code differs; clean result becomes security proof.
- **MATURE_FORM:** Use deterministic high-signal static checks and risk-focused human review where they can change a decision; treat output as version-bound evidence, never a completeness claim.
- **TRIGGER:** Changes to exposed/privileged code, known dangerous patterns, policy/configuration and high-consequence authorization/crypto/update logic.
- **CHEAP_PATH:** For small low-risk changes, compiler/type checks and a focused peer review may be enough; do not run broad noisy suites with no decision consumer.
- **TRUST_BOUNDARY_PROFILE:** Review includes identity/authority logic rather than treating successful authentication as proof. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Reviewers can block/escalate consequential defects; suppressions/exceptions have scoped authority and expiry. Review includes identity/authority logic rather than treating successful authentication as proof.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Changes to exposed/privileged code, known dangerous patterns, policy/configuration and high-consequence authorization/crypto/update logic. Configuration/provenance: Tool version/configuration/source revision are recorded; generated/dependency/runtime configuration gaps are explicit. Recovery: Release/recovery process can revert a bad change and feed discovered classes back into rules/design.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=HIGH; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S085] [S086].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Track actionable yield, escaped defects, suppression reasons and remediation—not raw findings alone. Recovery: Release/recovery process can revert a bad change and feed discovered classes back into rules/design.
- **REQUIRED_PRECONDITIONS:** Accurate language/framework model, maintained rules, reviewer competence, triage/remediation capacity and source provenance. Review includes identity/authority logic rather than treating successful authentication as proof. Reviewers can block/escalate consequential defects; suppressions/exceptions have scoped authority and expiry. Tool version/configuration/source revision are recorded; generated/dependency/runtime configuration gaps are explicit. Track actionable yield, escaped defects, suppression reasons and remediation—not raw findings alone. Release/recovery process can revert a bad change and feed discovered classes back into rules/design.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Scanner effectiveness varies materially by tool/class; suppression may be rational. Static evidence cannot establish runtime configuration or absence of adversarial paths. Contrary evidence: Outcome evidence is tool/language/project-specific; disciplined static analysis can be highly effective for narrow classes despite broad averages.
- **ANTI_CEREMONY_BOUNDARY:** A green SAST dashboard or two-person approval is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P47/P48: alert burden, marginal evidence and process cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **code review and static analysis as bounded evidence** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for code review and static analysis as bounded evidence remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — False positives create suppression; false negatives/unsupported frameworks; reviewer fatigue; generated/build code differs; clean result becomes security proof. — or would it add ceremony without changing the engineering decision?

### P28 — Dynamic testing and fuzzing as bounded evidence

- **PROPERTY_ID:** P28
- **PROPERTY_NAME:** Dynamic testing and fuzzing as bounded evidence
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Finds concrete exploitable or reliability-relevant implementation defects before or after deployment within reachable tested states.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary controls inputs/timing/state; harness and oracle approximate real execution; unreachable environment paths remain outside evidence.
- **FAILURE_MODE:** Poor harness never reaches critical code; crash count replaces severity; nondeterminism; sanitiser-only environment; fixed bugs do not repair root class; corpus stagnates.
- **MATURE_FORM:** Use fuzzing where a realistic harness and consequential oracle exist; report tested scope and remaining semantic/environment gaps.
- **TRIGGER:** Untrusted parsers/protocols, memory-unsafe or complex stateful code, high-volume interfaces and components with suitable oracles.
- **CHEAP_PATH:** For simple deterministic code with exhaustive input domain, property/unit tests or proof may be cheaper; low-exposure changes can reuse existing corpus.
- **TRUST_BOUNDARY_PROFILE:** Authentication/authorization state and identities used by tests must reflect relevant paths. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Test infrastructure cannot exercise production authority or secrets unsafely; remediation decisions have owners. Authentication/authorization state and identities used by tests must reflect relevant paths.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Untrusted parsers/protocols, memory-unsafe or complex stateful code, high-volume interfaces and components with suitable oracles. Configuration/provenance: Exact binary, instrumentation and environment are recorded; differences from production are explicit. Recovery: Failed deployment can be rolled back; regression corpus protects repaired behaviour.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=HIGH; incident=MODERATE; adversarial=HIGH. Critical evidence: [S090] [S091].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Coverage, unique defects, time-to-triage and escaped classes are observed without equating coverage with security. Recovery: Failed deployment can be rolled back; regression corpus protects repaired behaviour.
- **REQUIRED_PRECONDITIONS:** Representative build/configuration, harness, oracle/sanitiser, compute budget, triage ownership and reproducible failures. Authentication/authorization state and identities used by tests must reflect relevant paths. Test infrastructure cannot exercise production authority or secrets unsafely; remediation decisions have owners. Exact binary, instrumentation and environment are recorded; differences from production are explicit. Coverage, unique defects, time-to-triage and escaped classes are observed without equating coverage with security. Failed deployment can be rolled back; regression corpus protects repaired behaviour.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=MODERATE; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Fuzzing cannot prove absence and may miss semantic authorization/business-logic flaws; empirical success is concentrated in fuzzable software. Contrary evidence: Selection bias favours projects amenable to fuzzing; defect counts do not directly measure prevented compromise.
- **ANTI_CEREMONY_BOUNDARY:** A high execution count or zero crashes is not proof of security.
- **POSSIBLE_CONFLICTING_PROPERTY:** P30/P48: empirical exploration versus proof and compute/triage cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **dynamic testing and fuzzing as bounded evidence** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for dynamic testing and fuzzing as bounded evidence remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Poor harness never reaches critical code; crash count replaces severity; nondeterminism; sanitiser-only environment; fixed bugs do not repair root class; corpus stagnates. — or would it add ceremony without changing the engineering decision?

### P29 — Penetration testing and red teaming as scoped adversarial challenge

- **PROPERTY_ID:** P29
- **PROPERTY_NAME:** Penetration testing and red teaming as scoped adversarial challenge
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Discovers concrete exploitable paths, tests detection/response and challenges assumptions under bounded conditions.
- **THREAT_OR_ADVERSARY_PROFILE:** Testers approximate specified adversary capability, access and time; legal/safety scope constrains action; absence of finding is not absence of path.
- **FAILURE_MODE:** Narrow scope/window; known target; safe techniques omit destructive paths; report finding count; annual pass becomes certificate; fixes are local; red team shares intelligence/tools.
- **MATURE_FORM:** Use adversarial testing only when it can discriminate a material claim; state scope/time/access, treat findings as samples and require durable control learning.
- **TRIGGER:** Externally exposed/high-consequence systems, major architecture change, material uncertainty, regulatory/contractual requirement, or need to exercise response.
- **CHEAP_PATH:** For low-risk reversible changes, targeted abuse tests or deterministic checks are cheaper; do not commission a broad annual ritual with no decision path.
- **TRUST_BOUNDARY_PROFILE:** Test identities/credentials and insider positions must match model; social techniques remain high-level and controlled. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Authorisation protects systems/users and defines stop conditions; testers must not possess hidden ability to declare the system secure. Test identities/credentials and insider positions must match model; social techniques remain high-level and controlled.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Externally exposed/high-consequence systems, major architecture change, material uncertainty, regulatory/contractual requirement, or need to exercise response. Configuration/provenance: Target build/deployment/configuration, seeded access and tool versions are recorded. Recovery: Exercises include restoration/revocation where safe, and findings feed architecture and playbooks.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=MODERATE; incident=MODERATE; adversarial=HIGH. Critical evidence: [S085] [S086] [S095] [S096].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Detection/response observers distinguish missed, detected and contained actions; evidence is protected. Recovery: Exercises include restoration/revocation where safe, and findings feed architecture and playbooks.
- **REQUIRED_PRECONDITIONS:** Rules of engagement, safe environment, capable/independent testers, current configuration, remediation ownership and operational coordination. Test identities/credentials and insider positions must match model; social techniques remain high-level and controlled. Authorisation protects systems/users and defines stop conditions; testers must not possess hidden ability to declare the system secure. Target build/deployment/configuration, seeded access and tool versions are recorded. Detection/response observers distinguish missed, detected and contained actions; evidence is protected. Exercises include restoration/revocation where safe, and findings feed architecture and playbooks.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Attack space is effectively unbounded, testers are not the real adversary, and independence can be nominal. Comparative outcome evidence is limited. Contrary evidence: Strong evidence exists for finding real defects, but evidence that annual tests/certificates reduce system-level loss is weak.
- **ANTI_CEREMONY_BOUNDARY:** A pentest report, badge or zero-finding result is not a security proof.
- **POSSIBLE_CONFLICTING_PROPERTY:** P10/P32/P48: openness/scope safety and cost; P31: independence.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **penetration testing and red teaming as scoped adversarial challenge** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for penetration testing and red teaming as scoped adversarial challenge remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Narrow scope/window; known target; safe techniques omit destructive paths; report finding count; annual pass becomes certificate; fixes are local; red team shares intelligence/tools. — or would it add ceremony without changing the engineering decision?

### P30 — Formal and property-based assurance for high-consequence claims

- **PROPERTY_ID:** P30
- **PROPERTY_NAME:** Formal and property-based assurance for high-consequence claims
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** High confidence in narrowly specified confidentiality, integrity, isolation, policy or functional-correctness properties.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary exploits any behaviour inside the formal scope; hardware, compiler, specification, environment and operational assumptions are explicitly outside or included.
- **FAILURE_MODE:** Wrong/incomplete specification; model–implementation gap; proof excludes deployment/hardware/side channels; verified component used in unverified system; proof goes stale.
- **MATURE_FORM:** Apply the strongest formal method to the smallest high-consequence claim where exhaustive evidence changes a decision; publish assumptions and maintain correspondence.
- **TRIGGER:** Very high consequence, small stable trusted components, protocols/policies with tractable state, repeated defect classes or claims for which sampled testing is inadequate.
- **CHEAP_PATH:** For ordinary low-consequence or rapidly changing code, type systems, deterministic tests, fuzzing and review may provide better value; prove the smallest necessary kernel/property.
- **TRUST_BOUNDARY_PROFILE:** Principal/authority semantics must be faithfully formalised; proof of authentication protocol is not authorization correctness. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Who may change specification, proof assumptions and deployed policy is controlled. Principal/authority semantics must be faithfully formalised; proof of authentication protocol is not authorization correctness.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Very high consequence, small stable trusted components, protocols/policies with tractable state, repeated defect classes or claims for which sampled testing is inadequate. Configuration/provenance: Source/tool/compiler/build/configuration correspondence and proof artefact provenance are known. Recovery: Recovery/reconfiguration states are included or explicitly invalidate the proof.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=VERY_HIGH; empirical=MODERATE; incident=LIMITED; adversarial=HIGH. Critical evidence: [S010] [S011] [S027].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Runtime attestation/monitoring can detect departure from proved envelope; model assumptions remain visible. Recovery: Recovery/reconfiguration states are included or explicitly invalidate the proof.
- **REQUIRED_PRECONDITIONS:** Stable formal specification, skilled team/toolchain, bounded TCB/environment, provenance and maintenance commitment. Principal/authority semantics must be faithfully formalised; proof of authentication protocol is not authorization correctness. Who may change specification, proof assumptions and deployed policy is controlled. Source/tool/compiler/build/configuration correspondence and proof artefact provenance are known. Runtime attestation/monitoring can detect departure from proved envelope; model assumptions remain visible. Recovery/reconfiguration states are included or explicitly invalidate the proof.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=VERY_HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=LIMITED; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=MODERATE; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Formal proof is not empirical security and cannot establish adversary/environment facts outside the model. Industrial adoption evidence is strong in cases but not universal. Contrary evidence: Comparative causal outcome and cost-effectiveness evidence is limited; specification completeness and deployment reality remain dominant uncertainties.
- **ANTI_CEREMONY_BOUNDARY:** A model, theorem-prover use or certification claim is not whole-system assurance.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P31/P48: proof maintenance, environment correspondence and opportunity cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **formal and property-based assurance for high-consequence claims** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for formal and property-based assurance for high-consequence claims remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Wrong/incomplete specification; model–implementation gap; proof excludes deployment/hardware/side channels; verified component used in unverified system; proof goes stale. — or would it add ceremony without changing the engineering decision?

### P31 — Independent, diverse and current-configuration-bound assurance evidence

- **PROPERTY_ID:** P31
- **PROPERTY_NAME:** Independent, diverse and current-configuration-bound assurance evidence
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces false confidence and gives decision-makers evidence that discriminates materially different failure hypotheses.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary benefits from correlated blind spots, evaluator incentives and changes after assessment; evidence producers may be compromised or mistaken.
- **FAILURE_MODE:** Nominally independent assessors use identical scanners/checklists; tests share oracle; certificate covers old version; evidence author also owns acceptance; multiple weak signals are aggregated as certainty.
- **MATURE_FORM:** Use the minimum mutually informative evidence set adequate to consequence; disclose model/environment gaps and automatically invalidate stale state-bound claims.
- **TRIGGER:** High-consequence claims, certification, external trust, major releases, common-mode risk and any completeness/security assertion.
- **CHEAP_PATH:** For low-risk reversible change, one high-signal deterministic check plus provenance may be enough; do not multiply checks without expected discrimination.
- **TRUST_BOUNDARY_PROFILE:** Identity of evidence producer, signer and tested principals is known; evaluator identity alone does not establish independence. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Acceptance authority is distinct enough from implementation/evidence production for consequence; exceptions are visible. Identity of evidence producer, signer and tested principals is known; evaluator identity alone does not establish independence.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: High-consequence claims, certification, external trust, major releases, common-mode risk and any completeness/security assertion. Configuration/provenance: Every result records source/build/artifact/deployment/policy/tool/version and validity conditions. Recovery: Rollback/recovery evidence is exercised separately from preventive evidence where its failure mode differs.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=HIGH; incident=MODERATE; adversarial=HIGH. Critical evidence: [S085] [S086] [S087] [S091].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Every result records source/build/artifact/deployment/policy/tool/version and validity conditions.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Evidence freshness, coverage, disagreements and invalidation triggers are observable. Recovery: Rollback/recovery evidence is exercised separately from preventive evidence where its failure mode differs.
- **REQUIRED_PRECONDITIONS:** Explicit claim, evidence consumers, source identities, configuration/provenance mapping, assessor authority and conflict-of-interest disclosure. Identity of evidence producer, signer and tested principals is known; evaluator identity alone does not establish independence. Acceptance authority is distinct enough from implementation/evidence production for consequence; exceptions are visible. Every result records source/build/artifact/deployment/policy/tool/version and validity conditions. Evidence freshness, coverage, disagreements and invalidation triggers are observable. Rollback/recovery evidence is exercised separately from preventive evidence where its failure mode differs.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** True independence is expensive and sometimes impossible where all evidence depends on the same hardware/cloud/toolchain. More evidence can reduce rather than increase decision clarity. Contrary evidence: Independence and marginal information are hard to quantify; standards largely prescribe assessment discipline rather than prove optimal portfolios.
- **ANTI_CEREMONY_BOUNDARY:** A certificate, assessor logo, tool count or 'independent review' statement is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48: evidence diversity/independence cost and release latency.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **independent, diverse and current-configuration-bound assurance evidence** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for independent, diverse and current-configuration-bound assurance evidence remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Nominally independent assessors use identical scanners/checklists; tests share oracle; certificate covers old version; evidence author also owns acceptance; multiple weak signals are aggregated as certainty. — or would it add ceremony without changing the engineering decision?

### P32 — Vulnerability discovery and coordinated disclosure intake

- **PROPERTY_ID:** P32
- **PROPERTY_NAME:** Vulnerability discovery and coordinated disclosure intake
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Faster recognition and remediation of real vulnerabilities while balancing user protection, transparency and exploit window.
- **THREAT_OR_ADVERSARY_PROFILE:** Benign researchers, customers and adversaries may discover the same issue; reports can be malicious, mistaken or sensitive.
- **FAILURE_MODE:** No monitored channel; legal threats suppress reporting; triage backlog; duplicate/invalid reports dominate; disclosure dates detach from patch readiness; bounty incentives favour quantity.
- **MATURE_FORM:** A reliable, respectful intake-to-protection loop whose metrics centre affected users, remediation and recurrence—not bounty/CVE counts.
- **TRIGGER:** Externally used products/services, complex supply chains, security-relevant APIs and organisations likely to receive independent findings.
- **CHEAP_PATH:** For a tiny private system, a clear internal contact and response procedure may suffice; a paid public bounty is not mandatory.
- **TRUST_BOUNDARY_PROFILE:** Reporter identity may remain pseudonymous; authenticity of advisories and affected product identity are critical. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Only authorised owners accept risk or disclose; researchers do not silently gain production authority. Reporter identity may remain pseudonymous; authenticity of advisories and affected product identity are critical.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Externally used products/services, complex supply chains, security-relevant APIs and organisations likely to receive independent findings. Configuration/provenance: Reports bind to exact product/version/configuration and resulting fix/advisory provenance. Recovery: Emergency remediation, rollback and user recovery plans exist before public exposure when feasible.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=MODERATE; incident=HIGH; adversarial=HIGH. Critical evidence: [S028] [S032].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Track acknowledgement, validation, time to protective action, recurrence and affected deployment—not report count alone. Recovery: Emergency remediation, rollback and user recovery plans exist before public exposure when feasible.
- **REQUIRED_PRECONDITIONS:** Response team, legal/process clarity, secure communication, inventory/affectedness, patch/update capability and user notification. Reporter identity may remain pseudonymous; authenticity of advisories and affected product identity are critical. Only authorised owners accept risk or disclose; researchers do not silently gain production authority. Reports bind to exact product/version/configuration and resulting fix/advisory provenance. Track acknowledgement, validation, time to protective action, recurrence and affected deployment—not report count alone. Emergency remediation, rollback and user recovery plans exist before public exposure when feasible.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Bug bounties favour discoverable defect classes and popular products; disclosure timing has genuine competing risks; report volume is not security. Contrary evidence: Field causal evidence on disclosure-policy design is limited and selection effects are strong.
- **ANTI_CEREMONY_BOUNDARY:** A vulnerability disclosure policy page, CVE assignment or bounty programme is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P10/P38/P45/P49: transparency versus active exploitation and patch readiness.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **vulnerability discovery and coordinated disclosure intake** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for vulnerability discovery and coordinated disclosure intake remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — No monitored channel; legal threats suppress reporting; triage backlog; duplicate/invalid reports dominate; disclosure dates detach from patch readiness; bounty incentives favour quantity. — or would it add ceremony without changing the engineering decision?

### P33 — Exposure-, reachability- and consequence-aware vulnerability prioritisation

- **PROPERTY_ID:** P33
- **PROPERTY_NAME:** Exposure-, reachability- and consequence-aware vulnerability prioritisation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Faster reduction of meaningful exploit paths and harm under finite remediation capacity.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary chooses reachable and useful weaknesses, may chain lower-severity flaws and adapts to public exploit/patch information.
- **FAILURE_MODE:** Component version detection is wrong; vulnerable code is unreachable yet consumes effort; low-score chain ignored; asset inventory stale; KEV/EPSS treated as certainty; patch risk omitted.
- **MATURE_FORM:** Use the cheapest context that changes order—known exploitation, exposure, reachable vulnerable function, privilege and consequence—without claiming exact risk probabilities.
- **TRIGGER:** Non-trivial backlog, heterogeneous assets, delayed patches, transitive dependencies or conflict between patch urgency and stability.
- **CHEAP_PATH:** For a small inventory with a safely deployable fix and material exposure, patch directly after basic validation; elaborate scoring adds no value.
- **TRUST_BOUNDARY_PROFILE:** Privilege/identity needed for exploitation is represented; assumed unauthenticated/authenticated access is current. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Risk acceptance and exceptions have named authority and expiry. Privilege/identity needed for exploitation is represented; assumed unauthenticated/authenticated access is current.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Non-trivial backlog, heterogeneous assets, delayed patches, transitive dependencies or conflict between patch urgency and stability. Configuration/provenance: Version/configuration/dependency and deployed patch status are verified rather than inferred from ticket state. Recovery: Rollback/mitigation is prepared where patch can damage availability; containment supports delayed remediation.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=HIGH; incident=HIGH; adversarial=HIGH. Critical evidence: [S068] [S069] [S104].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe exploit attempts, exposure, patch rollout, exceptions and residual vulnerable paths. Recovery: Rollback/mitigation is prepared where patch can damage availability; containment supports delayed remediation.
- **REQUIRED_PRECONDITIONS:** Current inventory, topology/runtime reachability, consequence model, vulnerability data quality and patch/change authority. Privilege/identity needed for exploitation is represented; assumed unauthenticated/authenticated access is current. Risk acceptance and exceptions have named authority and expiry. Version/configuration/dependency and deployed patch status are verified rather than inferred from ticket state. Observe exploit attempts, exposure, patch rollout, exceptions and residual vulnerable paths. Rollback/mitigation is prepared where patch can damage availability; containment supports delayed remediation.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Severity remains useful as a portable technical input but is not organisational risk. Reachability tools can create false negatives; exploitation can change rapidly. Contrary evidence: Predictive/reachability evidence is ecosystem- and time-dependent; unknown exploitation and chained paths remain.
- **ANTI_CEREMONY_BOUNDARY:** A CVSS threshold, vulnerability count or closed ticket is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P38/P49: patch urgency versus service/safety validation; P47: score gaming.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **exposure-, reachability- and consequence-aware vulnerability prioritisation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for exposure-, reachability- and consequence-aware vulnerability prioritisation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Component version detection is wrong; vulnerable code is unreachable yet consumes effort; low-score chain ignored; asset inventory stale; KEV/EPSS treated as certainty; patch risk omitted. — or would it add ceremony without changing the engineering decision?

### P34 — Remediation verification and security-exception expiry

- **PROPERTY_ID:** P34
- **PROPERTY_NAME:** Remediation verification and security-exception expiry
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Prevents persistent known exposure, incomplete fleet remediation and permanent emergency exceptions.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary continues exploiting unpatched/incorrectly patched instances or waits for compensating controls/exceptions to lapse.
- **FAILURE_MODE:** Patch applied to wrong version; vulnerable code remains in image/cache; scanner false negative; mitigation bypass; exception auto-renewed; rollback reintroduces flaw.
- **MATURE_FORM:** Closure requires evidence about the current deployed exposure and affected consequence; exceptions are temporary hypotheses with explicit invalidators.
- **TRIGGER:** Material vulnerability, broad fleet, complex dependency/update paths, compensating mitigation or any deferred remediation.
- **CHEAP_PATH:** For a small controlled deployment, a version/hash/config check and one targeted regression test may settle closure.
- **TRUST_BOUNDARY_PROFILE:** Credential/identity changes are verified across all sessions/tokens/issuers where part of remediation. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Only named risk authority can accept residual exposure; operational tickets cannot silently do so. Credential/identity changes are verified across all sessions/tokens/issuers where part of remediation.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Material vulnerability, broad fleet, complex dependency/update paths, compensating mitigation or any deferred remediation. Configuration/provenance: Fix source, build artifact, signature/provenance, deployed version/config and rollback image are linked. Recovery: Rollback/failure plan avoids choosing between unknown security state and unavailable service.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S113] [S110].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Fix source, build artifact, signature/provenance, deployed version/config and rollback image are linked.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Coverage of rollout, residual vulnerable instances, control operation and exception age are visible. Recovery: Rollback/failure plan avoids choosing between unknown security state and unavailable service.
- **REQUIRED_PRECONDITIONS:** Accurate affectedness, deployment inventory, update authority, test oracle, exception governance and observability. Credential/identity changes are verified across all sessions/tokens/issuers where part of remediation. Only named risk authority can accept residual exposure; operational tickets cannot silently do so. Fix source, build artifact, signature/provenance, deployed version/config and rollback image are linked. Coverage of rollout, residual vulnerable instances, control operation and exception age are visible. Rollback/failure plan avoids choosing between unknown security state and unavailable service.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Verification costs can delay urgent fixes; no test proves absence of alternate paths. Patch and service stability trade-offs are real. Contrary evidence: Optimal verification depth depends on urgency, exploit activity and deployment reversibility; empirical evidence on exception governance is limited.
- **ANTI_CEREMONY_BOUNDARY:** A status field 'remediated' or scanner disappearance alone is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P38/P49: verification depth versus urgent mitigation and availability.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **remediation verification and security-exception expiry** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for remediation verification and security-exception expiry remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Patch applied to wrong version; vulnerable code remains in image/cache; scanner false negative; mitigation bypass; exception auto-renewed; rollback reintroduces flaw. — or would it add ceremony without changing the engineering decision?

### P35 — Dependency identity, current inventory and affectedness

- **PROPERTY_ID:** P35
- **PROPERTY_NAME:** Dependency identity, current inventory and affectedness
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Rapid, accurate response to supplier compromise/vulnerability/licence-support events and reduced ungoverned transitive trust.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may compromise maintainers/registries/dependencies or exploit known defects; inventory generators and metadata may be incomplete or manipulated.
- **FAILURE_MODE:** SBOM omits generated/vendored/runtime dependencies; tools disagree; version/identity aliases; inventory goes stale; presence is mistaken for reachable affectedness.
- **MATURE_FORM:** Dependency identity can be reconstructed for the exact artifact/state, quality/unknowns are explicit, and inventory directly supports change/vulnerability/supplier decisions.
- **TRIGGER:** Third-party code, large dependency graph, externally distributed products, regulated sectors, rapid vulnerability response or supplier due diligence.
- **CHEAP_PATH:** For a small vendored/pinned codebase, deterministic lockfile/hash plus documented manual dependencies may be cheaper than a formal SBOM exchange.
- **TRUST_BOUNDARY_PROFILE:** Supplier/maintainer identities are recorded but do not prove trustworthiness. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Who may add/update dependencies and approve unresolved/abandoned components is bounded. Supplier/maintainer identities are recorded but do not prove trustworthiness.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Third-party code, large dependency graph, externally distributed products, regulated sectors, rapid vulnerability response or supplier due diligence. Configuration/provenance: Inventory binds to source/build/artifact/deployment and generator/version; currentness/coverage and unknown fields are explicit. Recovery: Recovery/rebuild can replace compromised dependencies from trusted sources and revoke affected releases.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=HIGH; incident=HIGH; adversarial=MODERATE. Critical evidence: [S110] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Inventory binds to source/build/artifact/deployment and generator/version; currentness/coverage and unknown fields are explicit.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Detect newly introduced, missing, end-of-life and vulnerable dependencies and observe deployment affectedness. Recovery: Recovery/rebuild can replace compromised dependencies from trusted sources and revoke affected releases.
- **REQUIRED_PRECONDITIONS:** Reproducible dependency resolution, component identifiers/hashes, build/runtime visibility, ownership and update process. Supplier/maintainer identities are recorded but do not prove trustworthiness. Who may add/update dependencies and approve unresolved/abandoned components is bounded. Inventory binds to source/build/artifact/deployment and generator/version; currentness/coverage and unknown fields are explicit. Detect newly introduced, missing, end-of-life and vulnerable dependencies and observe deployment affectedness. Recovery/rebuild can replace compromised dependencies from trusted sources and revoke affected releases.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** SBOM existence does not establish completeness, provenance, exploitability or trust. Recent empirical evidence shows severe cross-tool inconsistency. Contrary evidence: Empirical studies cover selected ecosystems/tools and one is a preprint; inventory remains valuable despite quality limits.
- **ANTI_CEREMONY_BOUNDARY:** An SBOM file or standard format alone is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P36/P47/P48: inventory quality/provenance depth versus tooling cost/noise.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **dependency identity, current inventory and affectedness** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for dependency identity, current inventory and affectedness remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — SBOM omits generated/vendored/runtime dependencies; tools disagree; version/identity aliases; inventory goes stale; presence is mistaken for reachable affectedness. — or would it add ceremony without changing the engineering decision?

### P36 — Source/build provenance, build isolation and source-to-binary correspondence

- **PROPERTY_ID:** P36
- **PROPERTY_NAME:** Source/build provenance, build isolation and source-to-binary correspondence
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Integrity and traceability of software/firmware from source through build and distribution, enabling compromise detection and reconstruction.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may control repository, maintainer, CI worker, dependency registry, toolchain, build secret or artifact store.
- **FAILURE_MODE:** Self-attested provenance; compromised issuer; mutable build environment; hidden network input; unreproducible artifact; reproducibility confirms malicious source; source review not linked to binary.
- **MATURE_FORM:** Artifact acceptance depends on verified provenance and bounded builder authority appropriate to consequence, with explicit residual toolchain/hardware assumptions.
- **TRIGGER:** Externally distributed or privileged artifacts, automated deployments, high-value supply chains, third-party builds and recovery images.
- **CHEAP_PATH:** For a small internal low-risk tool, a clean controlled build, pinned hashes and recorded source/artifact digest may suffice; full SLSA infrastructure is optional.
- **TRUST_BOUNDARY_PROFILE:** Builder/maintainer identities are distinct and revocable; identity alone does not establish process integrity. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Build, release and policy authorities are separated/limited according to consequence. Builder/maintainer identities are distinct and revocable; identity alone does not establish process integrity.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Externally distributed or privileged artifacts, automated deployments, high-value supply chains, third-party builds and recovery images. Configuration/provenance: All inputs, tool versions, build steps, environment, outputs and attestations bind cryptographically to exact artifact. Recovery: Clean-room rebuild and key/pipeline reconstitution can restore trusted production after compromise.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S064] [S111] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** All inputs, tool versions, build steps, environment, outputs and attestations bind cryptographically to exact artifact.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Verification failures, unexpected inputs/network access and provenance gaps are visible; logs are protected. Recovery: Clean-room rebuild and key/pipeline reconstitution can restore trusted production after compromise.
- **REQUIRED_PRECONDITIONS:** Protected source and build identities, deterministic dependency resolution, trustworthy time/signing, verifier policy and ownership. Builder/maintainer identities are distinct and revocable; identity alone does not establish process integrity. Build, release and policy authorities are separated/limited according to consequence. All inputs, tool versions, build steps, environment, outputs and attestations bind cryptographically to exact artifact. Verification failures, unexpected inputs/network access and provenance gaps are visible; logs are protected. Clean-room rebuild and key/pipeline reconstitution can restore trusted production after compromise.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Provenance records facts claimed by an issuer; they do not prove source benignness or builder honesty unless independently anchored. Reproducibility is equivalence, not security. Contrary evidence: Field evidence is incident- and practice-led; comparative causal evidence for individual framework levels is limited.
- **ANTI_CEREMONY_BOUNDARY:** A provenance record, SLSA level or reproducible-build badge alone is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P38/P48: build verification versus release latency; P59: diversity/toolchain complexity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **source/build provenance, build isolation and source-to-binary correspondence** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for source/build provenance, build isolation and source-to-binary correspondence remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Self-attested provenance; compromised issuer; mutable build environment; hidden network input; unreproducible artifact; reproducibility confirms malicious source; source review not linked to binary. — or would it add ceremony without changing the engineering decision?

### P37 — Artifact and release authenticity with signer/build-authority validation

- **PROPERTY_ID:** P37
- **PROPERTY_NAME:** Artifact and release authenticity with signer/build-authority validation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Integrity/authenticity of deployed software, configuration, policy and firmware plus accountable release authority.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may tamper in transit/storage, steal signing keys, compromise release account/build plane, replay/rollback older signed artifacts or abuse delegated signing.
- **FAILURE_MODE:** Signature checked but signer authority/audience/channel/version not; key compromise; transparency not monitored; signing happens on developer workstation; malicious signed update; rollback to vulnerable release.
- **MATURE_FORM:** Accept artifacts only when bytes, provenance, intended channel/version and current bounded signer authority all satisfy policy.
- **TRIGGER:** Distributed software/configuration, privileged agents, firmware, recovery media and cross-organisational delivery.
- **CHEAP_PATH:** For local low-risk artifacts, authenticated repository plus hash/provenance and controlled deployment may suffice; public PKI/transparency not always needed.
- **TRUST_BOUNDARY_PROFILE:** Signer/build-service identity is current and distinct from arbitrary developer identity. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Release authority is scoped by product/channel/environment and separated from build/policy where consequence warrants. Signer/build-service identity is current and distinct from arbitrary developer identity.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Distributed software/configuration, privileged agents, firmware, recovery media and cross-organisational delivery. Configuration/provenance: Signature covers exact bytes/metadata and is linked to provenance, dependency/configuration and intended environment. Recovery: Compromise response revokes signer, identifies affected releases and reconstitutes clean signing/update roots.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S109] [S111] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Signature covers exact bytes/metadata and is linked to provenance, dependency/configuration and intended environment.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Unexpected signer, key use, log inconsistency, downgrade and deployment divergence are observable. Recovery: Compromise response revokes signer, identifies affected releases and reconstitutes clean signing/update roots.
- **REQUIRED_PRECONDITIONS:** Key lifecycle, canonical artifact identity, protected release process, verifier policy and update/recovery mechanism. Signer/build-service identity is current and distinct from arbitrary developer identity. Release authority is scoped by product/channel/environment and separated from build/policy where consequence warrants. Signature covers exact bytes/metadata and is linked to provenance, dependency/configuration and intended environment. Unexpected signer, key use, log inconsistency, downgrade and deployment divergence are observable. Compromise response revokes signer, identifies affected releases and reconstitutes clean signing/update roots.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Signing establishes origin under a key, not build/source security. Central signing services are high-value common mode and offline availability complicates revocation. Contrary evidence: Strong cryptographic mechanism evidence contrasts with limited comparative evidence for operational signing programmes and documented adoption barriers.
- **ANTI_CEREMONY_BOUNDARY:** A signature badge or signed file alone is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P21/P38/P44: revocation/freshness versus offline availability and recovery.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **artifact and release authenticity with signer/build-authority validation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for artifact and release authenticity with signer/build-authority validation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Signature checked but signer authority/audience/channel/version not; key compromise; transparency not monitored; signing happens on developer workstation; malicious signed update; rollback to vulnerable release. — or would it add ceremony without changing the engineering decision?

### P38 — Secure update, rollback/downgrade protection and staged rollout

- **PROPERTY_ID:** P38
- **PROPERTY_NAME:** Secure update, rollback/downgrade protection and staged rollout
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Timely remediation without unauthorised code/configuration, systemic outage or persistent downgrade.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may block/freeze, replay, substitute or compromise updates; benign defective updates are also material system threats.
- **FAILURE_MODE:** Signature only; no version freshness; central update pushes globally; canary unrepresentative; rollback uses vulnerable image; emergency patch bypasses validation; clients cannot update.
- **MATURE_FORM:** Use consequence-proportionate validation and staged exposure while preserving rapid containment; rollback policy distinguishes availability recovery from unsafe downgrade.
- **TRIGGER:** Externally exposed or fleet software, privileged agents, firmware/OT/medical devices and urgent vulnerabilities.
- **CHEAP_PATH:** For a small reversible service with immutable deployment, one controlled update plus health/security check and known-good image may be enough.
- **TRUST_BOUNDARY_PROFILE:** Update service/client identities and channel authorisation are current; device ownership/recovery is defined. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Who may release, stage, halt, rollback or override is separated/bounded. Update service/client identities and channel authorisation are current; device ownership/recovery is defined.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Externally exposed or fleet software, privileged agents, firmware/OT/medical devices and urgent vulnerabilities. Configuration/provenance: Update metadata, artifact, signer, build provenance, target environment and installed state are linked. Recovery: Known-good recovery sources are protected and not vulnerable to the same compromise; downgrade exceptions are explicit.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=HIGH; empirical=MODERATE; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S110] [S113] [S117].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Update metadata, artifact, signer, build provenance, target environment and installed state are linked.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Rollout coverage, failures, security regressions, unexpected signer/version and blocked clients are observable. Recovery: Known-good recovery sources are protected and not vulnerable to the same compromise; downgrade exceptions are explicit.
- **REQUIRED_PRECONDITIONS:** Asset/version inventory, release provenance, protected update channel, representative tests, monitoring, operational authority and recovery capacity. Update service/client identities and channel authorisation are current; device ownership/recovery is defined. Who may release, stage, halt, rollback or override is separated/bounded. Update metadata, artifact, signer, build provenance, target environment and installed state are linked. Rollout coverage, failures, security regressions, unexpected signer/version and blocked clients are observable. Known-good recovery sources are protected and not vulnerable to the same compromise; downgrade exceptions are explicit.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=HIGH; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Urgent patching and thorough validation conflict; no rollout strategy eliminates zero-day or common-mode risk. Update availability varies by sector. Contrary evidence: Incident evidence is strong; comparative evidence for rollout configurations and optimal patch delay is context-specific.
- **ANTI_CEREMONY_BOUNDARY:** A signed update, successful CI build or 'patch applied' ticket is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P33/P34/P43/P49: exposure urgency, regression risk, rollback security and service continuity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **secure update, rollback/downgrade protection and staged rollout** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for secure update, rollback/downgrade protection and staged rollout remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Signature only; no version freshness; central update pushes globally; canary unrepresentative; rollback uses vulnerable image; emergency patch bypasses validation; clients cannot update. — or would it add ceremony without changing the engineering decision?

### P39 — Secure configuration baselines, desired state and drift detection

- **PROPERTY_ID:** P39
- **PROPERTY_NAME:** Secure configuration baselines, desired state and drift detection
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Preserves intended authorization, isolation, update and observability properties in the real environment.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may alter configuration or exploit benign drift; operators and automated platforms also introduce unreviewed differences.
- **FAILURE_MODE:** Baseline copied without context; compliance reports syntactic state not effective authority; IaC differs from runtime; auto-remediation causes outage; exceptions persist; ephemeral resources evade inventory.
- **MATURE_FORM:** Maintain the minimum secure state needed for current objectives, verify actual effect, and retire controls/settings whose threat or consumer has disappeared.
- **TRIGGER:** Production/privileged/shared systems, regulated baselines, large fleets, cloud/containers, frequent deployment and repeated misconfiguration.
- **CHEAP_PATH:** For a simple isolated system, a small versioned config plus deterministic startup check may suffice; full policy-as-code platform is optional.
- **TRUST_BOUNDARY_PROFILE:** Identity/authorization configuration is included, including effective transitive roles and recovery settings. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Only authorised changes can modify desired/actual state; automation identity is least-privileged. Identity/authorization configuration is included, including effective transitive roles and recovery settings.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Production/privileged/shared systems, regulated baselines, large fleets, cloud/containers, frequent deployment and repeated misconfiguration. Configuration/provenance: Baseline, policy code, environment, image/artifact and deployed observations are traceable. Recovery: Rollback/rebuild uses protected baseline and does not erase incident evidence or restore obsolete insecurity.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=MODERATE. Critical evidence: [S113] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Baseline, policy code, environment, image/artifact and deployed observations are traceable.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Drift, failed reconciliation, emergency overrides and effective policy outcomes are visible. Recovery: Rollback/rebuild uses protected baseline and does not erase incident evidence or restore obsolete insecurity.
- **REQUIRED_PRECONDITIONS:** Known system inventory, configuration ownership, reliable state collection, tested remediation and availability constraints. Identity/authorization configuration is included, including effective transitive roles and recovery settings. Only authorised changes can modify desired/actual state; automation identity is least-privileged. Baseline, policy code, environment, image/artifact and deployed observations are traceable. Drift, failed reconciliation, emergency overrides and effective policy outcomes are visible. Rollback/rebuild uses protected baseline and does not erase incident evidence or restore obsolete insecurity.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Baseline compliance does not prove runtime safety or security; strict uniformity can harm resilience and domain operations. Contrary evidence: Semantic drift and outcome evidence are difficult; automated enforcement can produce correlated failure.
- **ANTI_CEREMONY_BOUNDARY:** A benchmark percentage, configuration checklist or IaC repository is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P44/P49: strict uniformity versus adaptation/local operation; P08: central policy common mode.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **secure configuration baselines, desired state and drift detection** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for secure configuration baselines, desired state and drift detection remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Baseline copied without context; compliance reports syntactic state not effective authority; IaC differs from runtime; auto-remediation causes outage; exceptions persist; ephemeral resources evade inventory. — or would it add ceremony without changing the engineering decision?

### P40 — Runtime detection, observability and tamper-resistant security evidence

- **PROPERTY_ID:** P40
- **PROPERTY_NAME:** Runtime detection, observability and tamper-resistant security evidence
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Shorter detection/decision time, accountable operations, evidence-preserving response and validation of threat/control assumptions.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may evade, disable, forge or flood telemetry; legitimate high-volume events create noise; logging itself can leak secrets/privacy.
- **FAILURE_MODE:** Logs omit identity/parameters; central collector compromised; alerts overwhelm; anomaly model drifts; coverage unknown; data retention violates privacy; alert firing is mistaken for containment.
- **MATURE_FORM:** Observe the smallest security-relevant evidence set that can discriminate material states and drive authorised action, while protecting data and monitoring the monitor.
- **TRIGGER:** High-value authority, exposed boundaries, privileged/admin actions, update/build systems, regulated evidence and recovery/forensics needs.
- **CHEAP_PATH:** For low-consequence local work, structured audit of consequential state changes and deterministic integrity checks may be enough; avoid broad behavioural surveillance.
- **TRUST_BOUNDARY_PROFILE:** Events carry trustworthy principal/workload/session identity; identity-system compromise is detectable or an explicit blind spot. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Who may change logging/detection and who may suppress alerts is bounded and independently observable where warranted. Events carry trustworthy principal/workload/session identity; identity-system compromise is detectable or an explicit blind spot.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: High-value authority, exposed boundaries, privileged/admin actions, update/build systems, regulated evidence and recovery/forensics needs. Configuration/provenance: Telemetry identifies system/configuration/artifact/policy version; gaps after change invalidate coverage claims. Recovery: Evidence survives containment/rebuild; recovery systems retain necessary forensic/decision records without restoring compromised collectors.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S099] [S109] [S111].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Coverage, data loss, alert quality, response latency and blind spots are measured; detection is regularly challenged. Recovery: Evidence survives containment/rebuild; recovery systems retain necessary forensic/decision records without restoring compromised collectors.
- **REQUIRED_PRECONDITIONS:** Defined detection consumers/playbooks, trustworthy clocks/identities, protected collection, retention/privacy policy and operational triage capacity. Events carry trustworthy principal/workload/session identity; identity-system compromise is detectable or an explicit blind spot. Who may change logging/detection and who may suppress alerts is bounded and independently observable where warranted. Telemetry identifies system/configuration/artifact/policy version; gaps after change invalidate coverage claims. Coverage, data loss, alert quality, response latency and blind spots are measured; detection is regularly challenged. Evidence survives containment/rebuild; recovery systems retain necessary forensic/decision records without restoring compromised collectors.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Detection cannot compensate for weak prevention and may create surveillance/privacy/security risk. Outcome attribution and anomaly false-positive rates are context-dependent. Contrary evidence: Detection effectiveness varies with threat, data and staffing; sparse ground truth limits comparative claims.
- **ANTI_CEREMONY_BOUNDARY:** A SIEM deployment, log volume or alert count is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P10/P11/P49: confidentiality, privacy, usability and telemetry concentration.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **runtime detection, observability and tamper-resistant security evidence** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for runtime detection, observability and tamper-resistant security evidence remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Logs omit identity/parameters; central collector compromised; alerts overwhelm; anomaly model drifts; coverage unknown; data retention violates privacy; alert firing is mistaken for containment. — or would it add ceremony without changing the engineering decision?

### P41 — Incident declaration, response authority and containment

- **PROPERTY_ID:** P41
- **PROPERTY_NAME:** Incident declaration, response authority and containment
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Limits adversary dwell, blast radius and consequential harm while preserving accountable service/safety decisions.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary is active, adaptive and may exploit coordination delay, ambiguous ownership and response tooling; false alarms also impose cost.
- **FAILURE_MODE:** Alert never becomes incident; roles conflict; containment destroys evidence or safety; communications leak; playbook assumes unavailable identity/network; business owner blocks necessary action.
- **MATURE_FORM:** Decision rights, communication and containment options are designed before crisis, exercised under degraded trust, and scaled to consequence.
- **TRIGGER:** Material indication of compromise, control loss, high-confidence exploit activity, supplier compromise or unexplained security invariant violation.
- **CHEAP_PATH:** For a small low-consequence event, one accountable operator can isolate, preserve minimal evidence and escalate; a full command structure is unnecessary.
- **TRUST_BOUNDARY_PROFILE:** Responder identities and privileged credentials remain available and distinguishable during compromise. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Declaration, isolation, shutdown, disclosure and restoration authorities are explicit and proportionate. Responder identities and privileged credentials remain available and distinguishable during compromise.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Material indication of compromise, control loss, high-confidence exploit activity, supplier compromise or unexplained security invariant violation. Configuration/provenance: Playbooks/tooling match current architecture/configuration and can operate when primary systems are unavailable. Recovery: Containment is selected with reconstitution and service continuity in mind; clean channels and recovery resources exist.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=MODERATE; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S109] [S110] [S111].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Telemetry reaches decision-makers; response actions and evidence custody are recorded. Recovery: Containment is selected with reconstitution and service continuity in mind; clean channels and recovery resources exist.
- **REQUIRED_PRECONDITIONS:** Current contacts/asset dependencies, exercised playbooks, containment mechanisms, executive/risk support, legal/privacy/safety coordination. Responder identities and privileged credentials remain available and distinguishable during compromise. Declaration, isolation, shutdown, disclosure and restoration authorities are explicit and proportionate. Playbooks/tooling match current architecture/configuration and can operate when primary systems are unavailable. Telemetry reaches decision-makers; response actions and evidence custody are recorded. Containment is selected with reconstitution and service continuity in mind; clean channels and recovery resources exist.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Formal incident processes can slow obvious containment; aggressive isolation can create availability/safety harm. Incident labels and timing metrics are gameable. Contrary evidence: Incident studies are rich but selected and retrospective; controlled comparative evidence on response structures is limited.
- **ANTI_CEREMONY_BOUNDARY:** An incident-response plan, retained consultant or closed incident ticket is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P40/P43/P49: evidence preservation and safety/availability versus rapid containment.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **incident declaration, response authority and containment** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for incident declaration, response authority and containment remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Alert never becomes incident; roles conflict; containment destroys evidence or safety; communications leak; playbook assumes unavailable identity/network; business owner blocks necessary action. — or would it add ceremony without changing the engineering decision?

### P42 — Credential and authority revocation across control planes

- **PROPERTY_ID:** P42
- **PROPERTY_NAME:** Credential and authority revocation across control planes
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Stops continued authorised-looking action after identity/authority compromise and bounds containment time.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary already controls valid authority and may have minted derivatives, altered policy or established persistence.
- **FAILURE_MODE:** Directory account disabled but sessions remain; signing key revoked but artifacts accepted; federated issuer continues; emergency access persists; downstream agent credentials unknown.
- **MATURE_FORM:** Containment proves that all material derived authority is expired/revoked or isolated, then rebuilds identity trust from clean roots.
- **TRIGGER:** Credential theft, insider departure, identity/provider compromise, supplier/signing compromise, privilege error or incident containment.
- **CHEAP_PATH:** For a single local account with no derived credentials, disable, rotate and verify one enforcement point.
- **TRUST_BOUNDARY_PROFILE:** Compromised identities and legitimate replacement identities are distinguishable; recovery proofing is sound. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Revocation authority is protected and cannot be blocked/overridden by the compromised principal. Compromised identities and legitimate replacement identities are distinguishable; recovery proofing is sound.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Credential theft, insider departure, identity/provider compromise, supplier/signing compromise, privilege error or incident containment. Configuration/provenance: Token/key/policy/artifact versions and all dependent deployments are traceable. Recovery: Clean identity/keys and bounded service restoration exist; revocation does not permanently lock out recovery.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S109] [S111] [S114].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Use after revocation, propagation failures and unexpected issuances are visible. Recovery: Clean identity/keys and bounded service restoration exist; revocation does not permanently lock out recovery.
- **REQUIRED_PRECONDITIONS:** Authority/dependency graph, issuer/enforcer control, emergency access, reliable propagation and clean administrative channel. Compromised identities and legitimate replacement identities are distinguishable; recovery proofing is sound. Revocation authority is protected and cannot be blocked/overridden by the compromised principal. Token/key/policy/artifact versions and all dependent deployments are traceable. Use after revocation, propagation failures and unexpected issuances are visible. Clean identity/keys and bounded service restoration exist; revocation does not permanently lock out recovery.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Global instantaneous revocation is often impossible; central revocation creates availability/common-mode risk. Contrary evidence: Revocation completeness and propagation are architecture-specific; evidence is mostly mechanism/incident based.
- **ANTI_CEREMONY_BOUNDARY:** An account-disabled status or password reset is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P18/P20/P44: global revocation versus offline/emergency continuity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **credential and authority revocation across control planes** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for credential and authority revocation across control planes remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Directory account disabled but sessions remain; signing key revoked but artifacts accepted; federated issuer continues; emergency access persists; downstream agent credentials unknown. — or would it add ceremony without changing the engineering decision?

### P43 — Recovery and reconstitution from trusted sources with trust re-establishment

- **PROPERTY_ID:** P43
- **PROPERTY_NAME:** Recovery and reconstitution from trusted sources with trust re-establishment
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Restores mission/service availability and integrity after compromise without reintroducing the adversary or untrusted state.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary may corrupt/encrypt backups, recovery credentials, images, update channels and logs or persist in identity/management planes.
- **FAILURE_MODE:** Restore point already compromised; backup untested; clean room shares identity; rebuilding host leaves cloud tokens/policy; urgency skips validation; forensics blocks recovery or vice versa.
- **MATURE_FORM:** Recovery succeeds only when required service returns and current objectives/invariants are re-established from independently trustworthy material under a bounded residual-risk decision.
- **TRIGGER:** Ransomware/destructive attack, management/identity/supply-chain compromise, uncertain fleet state or critical corruption.
- **CHEAP_PATH:** For a small reversible stateless service, rebuild from verified source/artifact and restore minimal data with a targeted integrity check.
- **TRUST_BOUNDARY_PROFILE:** Recovery identities/keys are separate, protected and usable offline/degraded; compromised identities are not reused. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Authority to select restore point, destroy/rebuild and reconnect is explicit. Recovery identities/keys are separate, protected and usable offline/degraded; compromised identities are not reused.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Ransomware/destructive attack, management/identity/supply-chain compromise, uncertain fleet state or critical corruption. Configuration/provenance: Recovery images/data/configuration/build inputs have known provenance/version and are tested. Recovery: This property is itself the recovery prerequisite: exercises verify time, completeness, isolation and trust restoration.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=VERY_HIGH; adversarial=HIGH. Critical evidence: [S109] [S111] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Recovery images/data/configuration/build inputs have known provenance/version and are tested.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Recovery progress, integrity checks, residual compromise and reconnection decisions are auditable. Recovery: This property is itself the recovery prerequisite: exercises verify time, completeness, isolation and trust restoration.
- **REQUIRED_PRECONDITIONS:** Protected backups, clean bootstrap roots, source/build provenance, asset/dependency map, recovery objectives, staffing and alternate communications. Recovery identities/keys are separate, protected and usable offline/degraded; compromised identities are not reused. Authority to select restore point, destroy/rebuild and reconnect is explicit. Recovery images/data/configuration/build inputs have known provenance/version and are tested. Recovery progress, integrity checks, residual compromise and reconnection decisions are auditable. This property is itself the recovery prerequisite: exercises verify time, completeness, isolation and trust restoration.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Recovery is expensive and domain-specific; immutable backups can impede privacy deletion or rapid update. Trust can rarely be proven absolutely after deep hardware/identity compromise. Contrary evidence: Strong guidance and incident support; comparative evidence for clean-room architectures and trust-restoration metrics is limited.
- **ANTI_CEREMONY_BOUNDARY:** A backup, rebuilt host or service-up metric is not proof that trust is restored.
- **POSSIBLE_CONFLICTING_PROPERTY:** P21/P40/P45/P49: key/data availability, forensics and rapid restoration.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **recovery and reconstitution from trusted sources with trust re-establishment** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for recovery and reconstitution from trusted sources with trust re-establishment remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Restore point already compromised; backup untested; clean room shares identity; rebuilding host leaves cloud tokens/policy; urgency skips validation; forensics blocks recovery or vice versa. — or would it add ceremony without changing the engineering decision?

### P44 — Cyber resilience and graceful degradation

- **PROPERTY_ID:** P44
- **PROPERTY_NAME:** Cyber resilience and graceful degradation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Continuity of essential service, bounded harm and timely trustworthy recovery during/after attack.
- **THREAT_OR_ADVERSARY_PROFILE:** Adaptive adversary may compromise components, disrupt dependencies, deceive monitoring and target recovery; benign faults coexist.
- **FAILURE_MODE:** Resilience becomes vague excuse for preventable vulnerabilities; redundancy shares common mode; degraded mode violates security/safety; recovery objective untested; adaptation expands attack surface.
- **MATURE_FORM:** Resilience is specified in terms of essential consequence, adversary model, allowable degradation, trusted fallback and tested restoration—not generic uptime.
- **TRIGGER:** High mission/availability consequence, persistent adversary, critical infrastructure, cloud concentration or systems that cannot simply stop.
- **CHEAP_PATH:** For low-consequence/recreatable services, rapid immutable rebuild and acceptable outage may be cheaper than complex fail-operational architecture.
- **TRUST_BOUNDARY_PROFILE:** Degraded identity/authorization semantics are designed; offline/local control is bounded. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Who can enter/exit degraded modes and adapt controls is explicit. Degraded identity/authorization semantics are designed; offline/local control is bounded.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: High mission/availability consequence, persistent adversary, critical infrastructure, cloud concentration or systems that cannot simply stop. Configuration/provenance: Fallback systems, data, code and configuration have current provenance and do not preserve obsolete vulnerabilities. Recovery: Recovery/reconstitution objectives and clean roots are central, not appendices.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=VERY_HIGH; adversarial=MODERATE. Critical evidence: [S109] [S113] [S120].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe degradation, resource health, adversarial adaptation and whether essential functions remain within bounds. Recovery: Recovery/reconstitution objectives and clean roots are central, not appendices.
- **REQUIRED_PRECONDITIONS:** Explicit mission priorities, dependency/common-mode analysis, operational exercises, recovery resources and authority. Degraded identity/authorization semantics are designed; offline/local control is bounded. Who can enter/exit degraded modes and adapt controls is explicit. Fallback systems, data, code and configuration have current provenance and do not preserve obsolete vulnerabilities. Observe degradation, resource health, adversarial adaptation and whether essential functions remain within bounds. Recovery/reconstitution objectives and clean roots are central, not appendices.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Resilience can normalise weak prevention and its metrics are immature; diversity/complexity can worsen security. Contrary evidence: Field/incident support is strong; quantitative resilience measures and comparative architecture evidence remain weak.
- **ANTI_CEREMONY_BOUNDARY:** A resilience strategy, backup count or high-availability topology is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P05/P13/P39/P49/P59: security strictness, isolation, baseline uniformity and complexity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **cyber resilience and graceful degradation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for cyber resilience and graceful degradation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Resilience becomes vague excuse for preventable vulnerabilities; redundancy shares common mode; degraded mode violates security/safety; recovery objective untested; adaptation expands attack surface. — or would it add ceremony without changing the engineering decision?

### P45 — Incident learning and root-invariant repair

- **PROPERTY_ID:** P45
- **PROPERTY_NAME:** Incident learning and root-invariant repair
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces recurrence and transfers hard-won adversarial evidence into design, assurance, detection and recovery.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversaries repeat or vary proven techniques; organisational incentives favour rapid closure and narrow attribution.
- **FAILURE_MODE:** Blame individual; confidential report never reaches engineering; local fix; lessons too generic; metrics reward closure time; recommendations unowned/stale.
- **MATURE_FORM:** Closure requires verified repair or explicit acceptance of the exploited invariant, not merely eradication of the observed instance.
- **TRIGGER:** Material incident, repeated vulnerability class, near miss with high potential consequence, assurance escape or recovery exercise failure.
- **CHEAP_PATH:** For a small isolated defect, add a regression test and repair the narrow root class; a formal postmortem is unnecessary.
- **TRUST_BOUNDARY_PROFILE:** Identity/authority misuse and recovery paths are included rather than attributing all events to user error. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Owners can change architecture/process and accept unresolved systemic risk. Identity/authority misuse and recovery paths are included rather than attributing all events to user error.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Material incident, repeated vulnerability class, near miss with high potential consequence, assurance escape or recovery exercise failure. Configuration/provenance: Lessons bind to affected products/configurations/dependencies and identify broader population. Recovery: Exercises validate that containment/recovery changes work under the learned scenario.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=MODERATE; incident=VERY_HIGH; adversarial=MODERATE. Critical evidence: [S109] [S110] [S111] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Corrective action and recurrence indicators are observable; sensitive evidence remains protected. Recovery: Exercises validate that containment/recovery changes work under the learned scenario.
- **REQUIRED_PRECONDITIONS:** Evidence preservation, psychological/legal safety, cross-functional authority, action ownership and longitudinal tracking. Identity/authority misuse and recovery paths are included rather than attributing all events to user error. Owners can change architecture/process and accept unresolved systemic risk. Lessons bind to affected products/configurations/dependencies and identify broader population. Corrective action and recurrence indicators are observable; sensitive evidence remains protected. Exercises validate that containment/recovery changes work under the learned scenario.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=VERY_HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=MODERATE; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Post-incident recommendations are observational and can overfit one event; transparency and operational secrecy conflict. Contrary evidence: Retrospective evidence is subject to incomplete observability and selection; outcome validation of recommendations is often absent.
- **ANTI_CEREMONY_BOUNDARY:** A postmortem document, lesson-learned meeting or closed action list is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P10/P32/P41: disclosure, evidence sensitivity and rapid closure.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **incident learning and root-invariant repair** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for incident learning and root-invariant repair remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Blame individual; confidential report never reaches engineering; local fix; lessons too generic; metrics reward closure time; recommendations unowned/stale. — or would it add ceremony without changing the engineering decision?

### P46 — Secure-by-design and secure-by-default product responsibility

- **PROPERTY_ID:** P46
- **PROPERTY_NAME:** Secure-by-design and secure-by-default product responsibility
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Fleet-scale reduction of preventable defects, unsafe setup and operational burden; clearer lifecycle support and disclosure responsibility.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversaries exploit widely deployed default/design weaknesses and long-tail customers unable to harden quickly.
- **FAILURE_MODE:** Marketing pledge without engineering change; security feature is paid add-on; legacy compatibility preserved indefinitely; vendor metrics opaque; customer assumes all risk transferred.
- **MATURE_FORM:** The producer removes foreseeable classes/default hazards and provides verifiable secure operation/recovery, while customers retain context-specific configuration and consequence ownership.
- **TRIGGER:** Mass-market, internet-facing, critical, enterprise platform or component whose producer controls architecture/defaults/update channel.
- **CHEAP_PATH:** For bespoke internal low-risk tools, local owner responsibility may be sufficient; formal public pledge/regulatory programme is optional.
- **TRUST_BOUNDARY_PROFILE:** Strong authentication/recovery is available by default; identity burden is not shifted to customer configuration alone. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Vendor executives/product owners hold authority to change defaults and retire unsafe compatibility; customers retain local risk decisions. Strong authentication/recovery is available by default; identity burden is not shifted to customer configuration alone.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Mass-market, internet-facing, critical, enterprise platform or component whose producer controls architecture/defaults/update channel. Configuration/provenance: Default/support claims identify product/version/configuration and supply-chain evidence. Recovery: Support/update/recovery commitments allow customers to restore and migrate; end-of-life is explicit.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S097] [S098] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Vendor can observe vulnerability/incident patterns and customer adoption without disproportionate data collection. Recovery: Support/update/recovery commitments allow customers to restore and migrate; end-of-life is explicit.
- **REQUIRED_PRECONDITIONS:** Product governance, lifecycle funding, engineering competence, customer feedback and ability to update safely. Strong authentication/recovery is available by default; identity burden is not shifted to customer configuration alone. Vendor executives/product owners hold authority to change defaults and retire unsafe compatibility; customers retain local risk decisions. Default/support claims identify product/version/configuration and supply-chain evidence. Vendor can observe vulnerability/incident patterns and customer adoption without disproportionate data collection. Support/update/recovery commitments allow customers to restore and migrate; end-of-life is explicit.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Current programmes are largely normative; optimal allocation of liability/cost and causal outcome evidence remain contested. Contrary evidence: Most direct evidence is policy, economics and incidents rather than controlled comparisons; producer responsibility can centralise control/privacy risk.
- **ANTI_CEREMONY_BOUNDARY:** A pledge, trust centre, certification or premium security SKU is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P15/P38/P49: vendor control/forced updates/privacy and customer autonomy.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **secure-by-design and secure-by-default product responsibility** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for secure-by-design and secure-by-default product responsibility remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Marketing pledge without engineering change; security feature is paid add-on; legacy compatibility preserved indefinitely; vendor metrics opaque; customer assumes all risk transferred. — or would it add ceremony without changing the engineering decision?

### P47 — Security metrics and proxy-gaming resistance

- **PROPERTY_ID:** P47
- **PROPERTY_NAME:** Security metrics and proxy-gaming resistance
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** More reliable prioritisation and governance; prevention of false confidence and resource diversion.
- **THREAT_OR_ADVERSARY_PROFILE:** Adaptive organisations and vendors game visible metrics; sparse/biased incident data and changing adversaries weaken inference.
- **FAILURE_MODE:** CVSS becomes risk; scanner/tool changes improve dashboard; suppressed findings hidden; MTTR encourages premature closure; phishing click rate blames users; maturity score lacks outcome validity.
- **MATURE_FORM:** No metric may stand in for security: it must identify population, state, decision, uncertainty, incentives and independent validation.
- **TRIGGER:** Any metric that allocates resources, declares security, compares units/vendors or creates incentives.
- **CHEAP_PATH:** For a local deterministic state, measure the state directly (e.g. signed artifact hash, revocation propagation) rather than invent a maturity score.
- **TRUST_BOUNDARY_PROFILE:** Identity of subjects/tools/assets is consistent; privacy-preserving aggregation avoids harmful surveillance. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Metric owner cannot redefine thresholds/denominators silently; acceptance authority sees uncertainty. Identity of subjects/tools/assets is consistent; privacy-preserving aggregation avoids harmful surveillance.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Any metric that allocates resources, declares security, compares units/vendors or creates incentives. Configuration/provenance: Data binds to current population/configuration/tool version and records missing/unknown cases. Recovery: Metrics include recovery/availability costs where they govern security decisions.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=HIGH; incident=HIGH; adversarial=MODERATE. Critical evidence: [S068] [S069] [S100].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Monitor data quality, denominator coverage, behavioural response and divergence from incidents/outcomes. Recovery: Metrics include recovery/availability costs where they govern security decisions.
- **REQUIRED_PRECONDITIONS:** Explicit consumer/decision, trustworthy data provenance, stable definitions, adversarial/gaming review and ability to act. Identity of subjects/tools/assets is consistent; privacy-preserving aggregation avoids harmful surveillance. Metric owner cannot redefine thresholds/denominators silently; acceptance authority sees uncertainty. Data binds to current population/configuration/tool version and records missing/unknown cases. Monitor data quality, denominator coverage, behavioural response and divergence from incidents/outcomes. Metrics include recovery/availability costs where they govern security decisions.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=MODERATE; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=VERY_HIGH
- **CRITICISMS:** Cyber outcome data are sparse and selected; many metrics are useful locally but not transferable. Quantitative models can still aid decisions when uncertainty is explicit. Contrary evidence: Direct cyber loss and counterfactual data are limited; rejecting all metrics would also impair learning and prioritisation.
- **ANTI_CEREMONY_BOUNDARY:** A dashboard, scorecard, risk matrix, CVSS distribution or maturity level is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P40/P49: measurement requires data but can create surveillance; P48: quantification cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **security metrics and proxy-gaming resistance** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for security metrics and proxy-gaming resistance remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — CVSS becomes risk; scanner/tool changes improve dashboard; suppressed findings hidden; MTTR encourages premature closure; phishing click rate blames users; maturity score lacks outcome validity. — or would it add ceremony without changing the engineering decision?

### P48 — Risk, uncertainty and security-depth proportionality with a cheap path

- **PROPERTY_ID:** P48
- **PROPERTY_NAME:** Risk, uncertainty and security-depth proportionality with a cheap path
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Maximum marginal security value under finite resources without converting low-risk work into compliance queues.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversaries concentrate where payoff/exposure is high; uncertainty and rare tail outcomes remain; process itself can create availability/delivery risk.
- **FAILURE_MODE:** Risk matrix false precision; 'low risk' used to avoid controls; high risk triggers every tool; cheap path lacks guardrails; reversible changes have irreversible data/authority effects.
- **MATURE_FORM:** Every change gets a minimal security invariant/provenance check; depth escalates only for stated consequence, threat, trust-boundary, irreversibility or uncertainty triggers.
- **TRIGGER:** All work, with deep paths for high consequence/exposure/irreversibility, novel trust/authority, weak observability or persistent capable adversaries.
- **CHEAP_PATH:** Established low-exposure, easily rolled-back change within a proven envelope uses secure defaults, provenance, focused tests and monitoring—no bespoke threat model/pentest board.
- **TRUST_BOUNDARY_PROFILE:** Identity/authority changes usually escalate even when code delta is small. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Risk/exception authority is separated from convenience incentives and decisions expire. Identity/authority changes usually escalate even when code delta is small.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: All work, with deep paths for high consequence/exposure/irreversibility, novel trust/authority, weak observability or persistent capable adversaries. Configuration/provenance: Cheap path requires exact change/artifact/configuration identity and proof that assumptions remain inside envelope. Recovery: Reversibility is tested and includes data, authority, supplier and customer effects—not only code rollback.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S082] [S098] [S113].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Post-deployment signals can reveal misclassification and trigger escalation. Recovery: Reversibility is tested and includes data, authority, supplier and customer effects—not only code rollback.
- **REQUIRED_PRECONDITIONS:** Reliable consequence/threat classification, bounded change envelope, rollback/recovery and authority that cannot self-exempt silently. Identity/authority changes usually escalate even when code delta is small. Risk/exception authority is separated from convenience incentives and decisions expire. Cheap path requires exact change/artifact/configuration identity and proof that assumptions remain inside envelope. Post-deployment signals can reveal misclassification and trigger escalation. Reversibility is tested and includes data, authority, supplier and customer effects—not only code rollback.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Rare events and sparse data make proportionality uncertain; formal proof may be cheap for some properties while manual review is not. There is no universal depth formula. Contrary evidence: Empirical data cannot supply universal thresholds; proportionality is governance-sensitive and gameable.
- **ANTI_CEREMONY_BOUNDARY:** A risk score, tier label or blanket waiver is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** All deeper properties: proportionality can under-trigger them if governance is weak.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **risk, uncertainty and security-depth proportionality with a cheap path** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for risk, uncertainty and security-depth proportionality with a cheap path remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Risk matrix false precision; 'low risk' used to avoid controls; high risk triggers every tool; cheap path lacks guardrails; reversible changes have irreversible data/authority effects. — or would it add ceremony without changing the engineering decision?

### P49 — Explicit security–privacy–safety–availability–usability tension adjudication

- **PROPERTY_ID:** P49
- **PROPERTY_NAME:** Explicit security–privacy–safety–availability–usability tension adjudication
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Preserves combined mission/human trustworthiness and prevents security controls from becoming another hazardous failure source.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversaries may exploit both weak protection and defensive responses; benign failures and human constraints interact.
- **FAILURE_MODE:** Fail closed blocks care/control; logging leaks secrets/PII; rapid patch breaks service; segmentation blocks emergency coordination; encryption defeats recovery; telemetry centralises sensitive data.
- **MATURE_FORM:** For each material conflict, identify failure directions, context favouring each property, bounded hybrid, monitoring and unresolved risk; scale process to consequence.
- **TRIGGER:** Cyber-physical/medical/OT, critical availability, sensitive personal data, central identity/telemetry, strict isolation or irreversible key/update decisions.
- **CHEAP_PATH:** For ordinary systems with aligned objectives, record the relevant side constraint and use established defaults; no multi-board process needed.
- **TRUST_BOUNDARY_PROFILE:** Identity and logging use only necessary personal data; emergency proofing remains possible. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** No single discipline can silently waive another's protected consequence; residual conflict has authorised owner. Identity and logging use only necessary personal data; emergency proofing remains possible.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Cyber-physical/medical/OT, critical availability, sensitive personal data, central identity/telemetry, strict isolation or irreversible key/update decisions. Configuration/provenance: Control/configuration versions and operating modes are traceable. Recovery: Recovery plans reconcile evidence preservation with rapid restoration and key/data availability.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=MODERATE; incident=HIGH; adversarial=MODERATE. Critical evidence: [S113] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe both security and competing outcomes, including denial, bypass, privacy exposure and safety effect. Recovery: Recovery plans reconcile evidence preservation with rapid restoration and key/data availability.
- **REQUIRED_PRECONDITIONS:** Cross-domain expertise, consequence ownership, realistic scenarios, conflict escalation and evidence of trade-off performance. Identity and logging use only necessary personal data; emergency proofing remains possible. No single discipline can silently waive another's protected consequence; residual conflict has authorised owner. Control/configuration versions and operating modes are traceable. Observe both security and competing outcomes, including denial, bypass, privacy exposure and safety effect. Recovery plans reconcile evidence preservation with rapid restoration and key/data availability.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=MODERATE; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** No universal optimum exists and values/legal duties differ. Joint process can become bureaucratic without decision authority. Contrary evidence: Trade-off resolutions are domain- and value-dependent; empirical generalisation is limited.
- **ANTI_CEREMONY_BOUNDARY:** A policy statement that all requirements are 'balanced' is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** Every involved property remains valid in its own consequence domain; conflict resolution cannot erase non-negotiable obligations.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **explicit security–privacy–safety–availability–usability tension adjudication** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for explicit security–privacy–safety–availability–usability tension adjudication remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Fail closed blocks care/control; logging leaks secrets/PII; rapid patch breaks service; segmentation blocks emergency coordination; encryption defeats recovery; telemetry centralises sensitive data. — or would it add ceremony without changing the engineering decision?

### P50 — Lifecycle retirement, decommissioning and stale-control removal

- **PROPERTY_ID:** P50
- **PROPERTY_NAME:** Lifecycle retirement, decommissioning and stale-control removal
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Reduces residual attack surface, data exposure, maintenance burden and misleading assurance while preserving required records/recovery.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary discovers forgotten systems/accounts/domains/keys/dependencies; decommissioning itself can leak data or break needed services.
- **FAILURE_MODE:** Asset still reachable; DNS/cloud storage takeover; secret in backup; dependency unsupported; retention violated; removal breaks hidden consumer; stale control retained for audit score.
- **MATURE_FORM:** Every security-relevant object/control has owner, consumer, support horizon and retirement condition; decommissioning closes authority and verifies residual state.
- **TRIGGER:** End-of-life product/service, unused integration/account, unsupported dependency, expired exception, changed threat/obligation or control with no decision consumer.
- **CHEAP_PATH:** For ephemeral resources, automatic expiry and reconciled desired state are the cheap path.
- **TRUST_BOUNDARY_PROFILE:** All human/workload/service identities and recovery channels tied to retired object are closed or reassigned deliberately. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Owner authorises decommissioning and accepts residual archival obligations. All human/workload/service identities and recovery channels tied to retired object are closed or reassigned deliberately.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: End-of-life product/service, unused integration/account, unsupported dependency, expired exception, changed threat/obligation or control with no decision consumer. Configuration/provenance: Actual deployed instances, artifacts, backups, DNS/registries and downstream copies are traced. Recovery: Recovery/archival needs are preserved without retaining live exploitable authority.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S073] [S112].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Actual deployed instances, artifacts, backups, DNS/registries and downstream copies are traced.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Post-retirement scanning/monitoring detects residual access, credentials or resurrection. Recovery: Recovery/archival needs are preserved without retaining live exploitable authority.
- **REQUIRED_PRECONDITIONS:** Inventory/dependency map, data/legal retention rules, owner authority, deletion/revocation capability and rollback contingency. All human/workload/service identities and recovery channels tied to retired object are closed or reassigned deliberately. Owner authorises decommissioning and accepts residual archival obligations. Actual deployed instances, artifacts, backups, DNS/registries and downstream copies are traced. Post-retirement scanning/monitoring detects residual access, credentials or resurrection. Recovery/archival needs are preserved without retaining live exploitable authority.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MODERATE
- **CRITICISMS:** Secure deletion/retirement can conflict with forensics, legal retention, resilience and historical reproducibility. Contrary evidence: Empirical outcome data on decommissioning programmes are sparse; complete erasure across replicas/backups is technically and legally difficult.
- **ANTI_CEREMONY_BOUNDARY:** An asset marked decommissioned or archived ticket is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P40/P43/P49: evidence/retention/recovery versus removal and privacy.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **lifecycle retirement, decommissioning and stale-control removal** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for lifecycle retirement, decommissioning and stale-control removal remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Asset still reachable; DNS/cloud storage takeover; secret in backup; dependency unsupported; retention violated; removal breaks hidden consumer; stale control retained for audit score. — or would it add ceremony without changing the engineering decision?

### P51 — Compliance mapping with outcome/evidence separation

- **PROPERTY_ID:** P51
- **PROPERTY_NAME:** Compliance mapping with outcome/evidence separation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Demonstrable obligation coverage, accountable governance and reusable evidence while preserving independent judgement about actual risk.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary does not respect compliance scope; assessors and organisations may optimise auditable artifacts; systems change after evidence collection.
- **FAILURE_MODE:** Control matrix has no configuration binding; scope excludes critical suppliers; inherited control assumptions false; exceptions hidden; audit pass overrides incident evidence.
- **MATURE_FORM:** Use compliance as a bounded source of obligations and evidence discipline; separately establish adversarial claims and current effectiveness.
- **TRIGGER:** Regulated/contractual environments, external assurance, complex obligation sets or shared controls.
- **CHEAP_PATH:** For an unregulated small system, record relevant legal/customer requirements directly in objectives; no large control matrix is needed.
- **TRUST_BOUNDARY_PROFILE:** Identity of assessed organisation/system/evidence producer is precise; certification scope is not assumed transitive. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Compliance assessor does not silently accept security risk; waivers and residual risk have authorised owners. Identity of assessed organisation/system/evidence producer is precise; certification scope is not assumed transitive.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Regulated/contractual environments, external assurance, complex obligation sets or shared controls. Configuration/provenance: Evidence links to exact configuration, artifact, period and inherited provider state. Recovery: Obligations include incident/recovery and evidence retention where applicable.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=HIGH; adversarial=LIMITED. Critical evidence: [S102] [S103] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Continuous monitoring and incidents can invalidate compliant status; missing coverage is visible. Recovery: Obligations include incident/recovery and evidence retention where applicable.
- **REQUIRED_PRECONDITIONS:** Authoritative obligation interpretation, system scope/population, evidence provenance, assessment competence and risk authority. Identity of assessed organisation/system/evidence producer is precise; certification scope is not assumed transitive. Compliance assessor does not silently accept security risk; waivers and residual risk have authorised owners. Evidence links to exact configuration, artifact, period and inherited provider state. Continuous monitoring and incidents can invalidate compliant status; missing coverage is visible. Obligations include incident/recovery and evidence retention where applicable.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=HIGH; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=VERY_HIGH; ADVERSARIAL_EVALUATION_STRENGTH=LIMITED; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Standards/certificates establish requirements or assessment processes, not empirical optimality or absence of compromise. Compliance can still be necessary and valuable. Contrary evidence: Comparative certification-outcome studies are confounded and mixed; compliance may improve baseline governance without proving security.
- **ANTI_CEREMONY_BOUNDARY:** A certificate, audit pass, control coverage percentage or completed matrix is not a general security property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24/P48: compliance burden versus engineering speed; P31/P47: evidence/score over-reading.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **compliance mapping with outcome/evidence separation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for compliance mapping with outcome/evidence separation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Control matrix has no configuration binding; scope excludes critical suppliers; inherited control assumptions false; exceptions hidden; audit pass overrides incident evidence. — or would it add ceremony without changing the engineering decision?

### P52 — Security training and awareness as supplementary control

- **PROPERTY_ID:** P52
- **PROPERTY_NAME:** Security training and awareness as supplementary control
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Improves recognition, reporting and correct use of remaining human-mediated controls while supporting secure organisational coordination.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary targets human cognition/workflow; training transfer decays and attackers adapt; participants have legitimate task pressures.
- **FAILURE_MODE:** Completion is outcome; generic annual content; simulated-phish punishment; click metrics; overtraining habituates; training substitutes for phishing-resistant authentication or safe defaults.
- **MATURE_FORM:** Use training only for decisions that remain legitimately human; pair it with phishing-resistant/default controls and treat recurrent errors as design evidence.
- **TRIGGER:** Residual human judgement, privileged operations, incident reporting, secure development tasks and new threat/control changes.
- **CHEAP_PATH:** If a deterministic safe default or phishing-resistant mechanism removes the decision, use that instead; low-risk users need concise just-in-time guidance.
- **TRUST_BOUNDARY_PROFILE:** Training cannot compensate for weak proofing/authentication; recovery and support staff need role-specific identity knowledge. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** People must have legitimate authority/path to act; otherwise awareness without capability is futile. Training cannot compensate for weak proofing/authentication; recovery and support staff need role-specific identity knowledge.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Residual human judgement, privileged operations, incident reporting, secure development tasks and new threat/control changes. Configuration/provenance: Training content matches actual deployed tools/policies and is updated after changes/incidents. Recovery: Exercises include degraded/incident roles and recovery; training itself is not a recovery capability.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=LIMITED; empirical=HIGH; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S102] [S047].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe reporting, task performance, near misses and support/workaround patterns—not just attendance or simulated clicks. Recovery: Exercises include degraded/incident roles and recovery; training itself is not a recovery capability.
- **REQUIRED_PRECONDITIONS:** Usable controls, management support, reporting safety, realistic content, privacy-respecting evaluation and remediation authority. Training cannot compensate for weak proofing/authentication; recovery and support staff need role-specific identity knowledge. People must have legitimate authority/path to act; otherwise awareness without capability is futile. Training content matches actual deployed tools/policies and is updated after changes/incidents. Observe reporting, task performance, near misses and support/workaround patterns—not just attendance or simulated clicks. Exercises include degraded/incident roles and recovery; training itself is not a recovery capability.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=LIMITED; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=HIGH; FIELD_PRACTICE_STRENGTH=HIGH; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=MODERATE; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Large field evidence shows some common training forms have limited effects; behavioural improvement does not directly establish reduced compromise. Contrary evidence: Training interventions and outcome measures are heterogeneous; some targeted programmes may work well in specific roles.
- **ANTI_CEREMONY_BOUNDARY:** Completion certificates, click-rate targets or 'security culture' scores are not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P46/P58: training burden and blame versus deterministic design responsibility.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **security training and awareness as supplementary control** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for security training and awareness as supplementary control remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Completion is outcome; generic annual content; simulated-phish punishment; click metrics; overtraining habituates; training substitutes for phishing-resistant authentication or safe defaults. — or would it add ceremony without changing the engineering decision?

### P59 — Diversity and moving-target mechanisms

- **PROPERTY_ID:** P59
- **PROPERTY_NAME:** Diversity and moving-target mechanisms
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Potential reduction of correlated compromise and attacker dwell/predictability in selected high-pressure environments.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary's exploit is implementation/configuration-specific and cannot cheaply adapt; diversity mechanisms themselves remain secure and operable.
- **FAILURE_MODE:** Variants share source/toolchain; complexity/misconfiguration grows; least-patched variant dominates; motion breaks observability/recovery; attacker adapts; performance/latency cost.
- **MATURE_FORM:** Use only when a specified common-mode adversarial path and evidence justify cost beyond simpler isolation, patching or recovery.
- **TRIGGER:** Fleet/common-mode high consequence, persistent capable adversary, high-value moving exposure and environments that can operate/test variants.
- **CHEAP_PATH:** For most systems, patching, compartmentalisation, least privilege and reliable recovery are cheaper and better supported.
- **TRUST_BOUNDARY_PROFILE:** Identity/policy consistency must survive variation without recreating common mode. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Authority to introduce/change variants is bounded; diversity control plane is protected. Identity/policy consistency must survive variation without recreating common mode.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: Fleet/common-mode high consequence, persistent capable adversary, high-value moving exposure and environments that can operate/test variants. Configuration/provenance: Variant provenance/configuration and shared ancestry are known. Recovery: Recovery supports each variant and avoids restoring common vulnerable state.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=MODERATE; adversarial=MODERATE. Critical evidence: [S113] [S109].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** At minimum, bind the claim to the exact software, dependency, configuration and deployment state; deeper supplier/build evidence triggers when the property depends on external artifacts or opaque services.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe differential failures, attacker adaptation and operational defects; motion does not erase evidence. Recovery: Recovery supports each variant and avoids restoring common vulnerable state.
- **REQUIRED_PRECONDITIONS:** Independent implementations/maintenance, automated configuration, interoperability testing, telemetry and operational capacity. Identity/policy consistency must survive variation without recreating common mode. Authority to introduce/change variants is bounded; diversity control plane is protected. Variant provenance/configuration and shared ancestry are known. Observe differential failures, attacker adaptation and operational defects; motion does not erase evidence. Recovery supports each variant and avoids restoring common vulnerable state.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=MODERATE; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=MODERATE; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=LIMITED; STANDARD_OR_REGULATORY_STRENGTH=MODERATE; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=LOW; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Evidence is domain-specific and often simulation/testbed-led; adaptive adversaries and maintenance cost can erase benefit. Contrary evidence: Comparative production evidence and transferable metrics are weak; benefits are highly assumption-sensitive.
- **ANTI_CEREMONY_BOUNDARY:** No general requirement to add variants or motion.
- **POSSIBLE_CONFLICTING_PROPERTY:** P08/P09/P39/P48: diversity versus common platform simplicity, maintainability and cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **diversity and moving-target mechanisms** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for diversity and moving-target mechanisms remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Variants share source/toolchain; complexity/misconfiguration grows; least-patched variant dominates; motion breaks observability/recovery; attacker adapts; performance/latency cost. — or would it add ceremony without changing the engineering decision?

### P60 — AI/ML and agentic systems security as a domain translation

- **PROPERTY_ID:** P60
- **PROPERTY_NAME:** AI/ML and agentic systems security as a domain translation
- **SECURITY_OBJECTIVE_OR_PROTECTED_CONSEQUENCE:** Protects model/service confidentiality, integrity, availability, privacy, decision quality and bounded agent authority under specified AI-specific threats.
- **THREAT_OR_ADVERSARY_PROFILE:** Adversary capability depends on query/access, training data/pipeline, model weights, tools, deployment context and adaptive knowledge; toy benchmarks often omit system composition.
- **FAILURE_MODE:** Benchmark-only robustness; static model card; untrusted data becomes instruction; agent inherits ambient credentials; guardrail bypass; model update/provenance drift; monitoring lacks ground truth; safety/security conflated.
- **MATURE_FORM:** Treat AI as a component/domain with explicit new threat assumptions; do not replace ordinary identity, supply-chain, isolation, assurance and recovery engineering with AI branding.
- **TRIGGER:** AI/ML affects consequential decisions, handles sensitive data, exposes models, ingests untrusted content, trains on third-party data or can invoke tools/actions.
- **CHEAP_PATH:** For low-consequence assistive/offline use with no authority and easy verification, sandboxing, data minimisation, provenance and output review may suffice.
- **TRUST_BOUNDARY_PROFILE:** Human, model, agent, tool, service and data-source identities/roles are distinct; model output is not identity proof. Boundary claims must identify enforcement and shared dependencies rather than infer separation from component labels.
- **AUTHORITY_IDENTITY_PROFILE:** Agent authority is explicit, parameter-bound, least-privileged and revocable; human approval is bound to action where consequential. Human, model, agent, tool, service and data-source identities/roles are distinct; model output is not identity proof.
- **SECURE_LIFECYCLE_PROFILE:** Trigger/change binding: AI/ML affects consequential decisions, handles sensitive data, exposes models, ingests untrusted content, trains on third-party data or can invoke tools/actions. Configuration/provenance: Training data/model/code/dependency/build/deployment versions and evaluation correspondence are traceable. Recovery: Rollback model/policy, revoke tool credentials, isolate compromised data/model and restore known-good pipeline.
- **ASSURANCE_PROFILE:** Claim evidence must match the mechanism and assumptions, be current-state bound and disclose false-confidence risk. Formal/model=MODERATE; empirical=LIMITED; incident=LIMITED; adversarial=MODERATE. Critical evidence: [S082] [S093].
- **SUPPLY_CHAIN_PROVENANCE_PROFILE:** Training data/model/code/dependency/build/deployment versions and evaluation correspondence are traceable.
- **DETECTION_CONTAINMENT_RECOVERY_PROFILE:** Observability: Observe model/tool actions, abuse, drift and control bypass with privacy and adversarial-evasion limits. Recovery: Rollback model/policy, revoke tool credentials, isolate compromised data/model and restore known-good pipeline.
- **REQUIRED_PRECONDITIONS:** Representative threat model, evaluation data/current model, secure ML/software pipeline, tool isolation, model/version provenance and operational ownership. Human, model, agent, tool, service and data-source identities/roles are distinct; model output is not identity proof. Agent authority is explicit, parameter-bound, least-privileged and revocable; human approval is bound to action where consequential. Training data/model/code/dependency/build/deployment versions and evaluation correspondence are traceable. Observe model/tool actions, abuse, drift and control bypass with privacy and adversarial-evasion limits. Rollback model/policy, revoke tool credentials, isolate compromised data/model and restore known-good pipeline.
- **EVIDENCE_STRENGTH:** HISTORICAL_PROVENANCE_STRENGTH=LOW; FORMAL_OR_MODEL_STRENGTH=MODERATE; INCIDENT_OR_VULNERABILITY_CASE_STRENGTH=LIMITED; EMPIRICAL_COMPARATIVE_STRENGTH=LIMITED; FIELD_PRACTICE_STRENGTH=MODERATE; STANDARD_OR_REGULATORY_STRENGTH=HIGH; ADVERSARIAL_EVALUATION_STRENGTH=MODERATE; TRANSFERABILITY_STRENGTH=LOW; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Evidence for many AI security controls is early, benchmark-heavy and assumption-sensitive; standard taxonomies/guidance do not establish field effectiveness. Contrary evidence: Rapidly changing models and attacks make transferability low; some traditional mechanisms may not capture stochastic/semantic failure.
- **ANTI_CEREMONY_BOUNDARY:** AI security framework/model card/red-team benchmark is not a general property or proof.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P17/P19/P31/P40/P49: agent usability/intent, authority, evidence, privacy and stochastic behaviour.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system implement **ai/ml and agentic systems security as a domain translation** as a current, consequence-linked mechanism, or merely name an artefact/control?
  - Can evidence for ai/ml and agentic systems security as a domain translation remain apparently green after the identity, authority, dependency, build, configuration or deployment state it covers changes?
  - Would another review, scanner, test or approval discriminate the failure mode — Benchmark-only robustness; static model card; untrusted data becomes instruction; agent inherits ambient credentials; guardrail bypass; model update/provenance drift; monitoring lacks ground truth; safety/security conflated. — or would it add ceremony without changing the engineering decision?

## CEREMONIES_TO_NOT_BLINDLY_ADOPT

| Candidate | Disposition | Retained underlying property |
| --- | --- | --- |
| Threat-model template | Do not require form completion absent a decision/change trigger. | P02, P22–P25 |
| Annual penetration test/pass letter | Do not infer security or attack-space coverage. | P29, P31, P55 |
| SBOM file/format | Do not infer completeness, provenance, affectedness or trust. | P35–P36, P53 |
| Zero-trust product stack/maturity label | Do not infer current resource authorization or resilient identity control plane. | P03, P06, P16–P19, P54 |
| Compliance control percentage/certificate | Do not infer current adversarial effectiveness. | P31, P51, P55 |
| SAST/DAST/scanner dashboard | Do not infer completeness or independent corroboration. | P27–P31, P47 |
| CVSS threshold/vulnerability count | Do not equate with system risk. | P33, P47, P56 |
| Security review board/two approvals | Do not infer technical challenge or independent authority. | P07, P23, P31 |
| Signed release/provenance badge | Do not infer trustworthy build/source/signer authority. | P21, P36–P38 |
| Security training completion/phishing click score | Do not infer behaviour, culture or compromise reduction. | P11, P46, P52, P58 |
| Hardening benchmark percentage | Do not infer effective runtime authority or safe state. | P15, P39 |
| Incident plan/backups on inventory | Do not infer exercised containment or trustworthy recovery. | P41–P44 |

## CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

| Property/deep form | Non-trigger or cheap path |
| --- | --- |
| P05 Fail-safe/secure failure | Direction of safe failure depends on whether unauthorised action or denial/safety loss dominates. |
| P07 Separation of privilege | Worth the latency and coordination cost mainly for high-consequence or irreversible transitions with credible independence. |
| P20 Break-glass authority | Required only where normal controls can block essential work or recovery; otherwise it creates an avoidable bypass. |
| P26 Memory-safe migration | Strong for new/exposed/long-lived code and recurring memory defects; rewrite/legacy/performance context matters. |
| P29 Penetration/red-team depth | Triggers when scoped adversarial challenge can change a material claim; not every change. |
| P30 Formal assurance | High payoff for small stable high-consequence claims; prohibitive or low-value for broad fast-changing systems. |
| P44 Fail-operational cyber resilience | Needed where essential service cannot simply stop; rapid rebuild/outage may be cheaper for low-consequence systems. |
| P48 Risk-scaled depth | Universal as a tailoring principle, but thresholds and cheap path are context/governance sensitive. |
| P49 Cross-property adjudication | Triggered by real security/privacy/safety/availability/usability conflict; not a standing multi-board ceremony. |
| P51 Compliance mapping | Required by obligations and complex evidence inheritance, not as a universal outcome proof. |
| P52 Training | Supplementary where people retain consequential judgement; remove the decision/design flaw first where possible. |
| P59 Diversity/moving target | Only when a specified common mode and adaptive-threat model justify maintenance/complexity cost. |
| P60 AI/ML/agentic security | Domain translation whose additional mechanisms depend on model access, data pipeline, tool authority and consequence. |

## PROPERTIES_REQUIRING_EXPLICIT_THREAT_MODEL

P02, P03, P05–P09, P12–P14, P17–P21, P23, P25, P29–P31, P33, P36–P38, P40–P44, P48–P49, P59–P60. The model may be lightweight, but attacker capability, trust assumptions and excluded conditions must be visible before these claims can be judged.

## PROPERTIES_REQUIRING_CURRENT_IDENTITY_OR_AUTHORITY

P04–P07, P16–P21, P29, P37–P44 and P60. Authentication, authorization, delegation, signer/build authority, emergency privilege and revocation must bind to the current resource/action/context rather than merely to a valid account or historical approval.

## PROPERTIES_REQUIRING_SUPPLY_CHAIN_OR_PROVENANCE_EVIDENCE

P09–P10, P21, P25, P27–P31, P34–P39, P43, P50 and P60. At minimum, evidence must identify the source/artifact/configuration/deployment it covers; P35–P38 require the deeper dependency/build/release chain.

## PROPERTIES_REQUIRING_INDEPENDENT_ADVERSARIAL_ASSURANCE

P09, P14, P23, P27–P31, P34, P36–P40, P43–P45, P59 and P60 when the protected consequence is high. Independence means different failure hypotheses and sufficiently distinct people/method/data/control planes—not simply different vendor names.

## HIGH_ADVERSARIAL_PRESSURE_ONLY_PROPERTIES

- **P30 formal/property-based assurance at full depth:** trigger for small stable high-consequence mechanisms or claims where exhaustive model-relative evidence changes acceptance.
- **P59 diversity/moving-target mechanisms:** trigger only for a specified common-mode/adaptive threat and after comparison with simpler containment/update/recovery.
- **Deep P31 assurance portfolios and production red-team exercises:** trigger when consequence, novelty, irreversibility or uncertainty justifies independent challenge; the property itself still has a lightweight form.

## SECURITY_SAFETY_PRIVACY_AVAILABILITY_TENSIONS

| Tension | Security-side property | Competing property | Mature hybrid |
| --- | --- | --- | --- |
| Fail closed vs availability/safety | P05/P06 | P20/P44/P49 | Per-operation bounded deny/degrade/local mode with visible state and tested reconciliation. |
| Logging/detection vs privacy/confidentiality | P40 | P10/P11/P49 | Purpose-bound minimal tamper-resistant evidence, separated access and retention. |
| Rapid patch vs stability/safety | P33/P38 | P43/P44/P49 | Immediate containment plus staged update, representative checks and secure rollback/forward fix. |
| Least privilege vs task/emergency completion | P04/P18 | P11/P20 | Usable just-in-time elevation and scenario-specific expiring break-glass. |
| Segmentation/isolation vs interoperability | P13 | P44/P49 | Narrow mediated bridges/capabilities and tested degraded operation. |
| Central identity/policy vs resilience | P16–P19/P54 | P08/P20/P42–P44 | Bounded issuer authority, local/offline policy and clean-root reconstitution. |
| Transparency/disclosure vs exploit window | P10/P32/P45 | P38/P49 | Open mechanisms and coordinated time-bounded vulnerability detail. |
| Encryption/revocation vs recovery/forensics | P21/P42 | P40/P43/P49 | Separated recovery keys, audit, rekeying and explicit evidence/restoration trade-off. |
| Supply-chain verification vs release latency | P35–P37 | P38/P48 | Automated protected pipeline and deeper independent rebuild only for high consequence. |
| Assurance depth vs reversible low-risk change | P29–P31 | P24/P48 | Minimum invariant/provenance check plus explicit escalation triggers. |

## PROPERTIES_WITH_STRONG_INCIDENT_OR_EMPIRICAL_SUPPORT

P03–P04, P08, P11, P13, P21, P27–P29, P31, P33–P45, P47, P52, P53 and P56 have strong mechanism-rich incident or comparative empirical support for at least one material claim. This does **not** mean every implementation is strongly supported; the property ledger partitions strength by claim type.

## PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

P02 (method effectiveness, not necessity of assumptions), P07, P15 (programme outcome), P20, P23–P25 (integrated programme/currentness effects), P30 (cost-effectiveness outside selected successes), P46, P48–P51, P59 and P60. These remain admitted where mechanism, guidance or formal evidence is strong, but empirical transfer/optimality is limited or assumption-sensitive.

## UNRESOLVED_PROPERTIES

No property carries `CURRENT_STATUS: UNRESOLVED`. P59 and P60 are explicitly `DOMAIN_SPECIFIC`; P02 is `ASSUMPTION_SENSITIVE`; several retained properties contain unresolved implementation/effect-size questions. Those evidence limits are preserved in each `OPEN_QUESTIONS` field and in the frozen report rather than being promoted to false certainty.

## Audit-use boundary

This intake supplies external questions and evidence. It does not determine whether any target system already owns, partially owns, conflicts with, redundantly implements or should adopt a property. Crosswalk questions must remain questions until grounded in target-system evidence.

## Frozen intake receipt

EVOLVED_SYSTEMS_SECURITY_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 60
PROPERTY_POPULATION_EXAMINED: 60
PROPERTY_COVERAGE: 60/60
EVOLVED_SYSTEMS_SECURITY_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES