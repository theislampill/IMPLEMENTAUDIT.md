# EVOLVED_SYSTEMS_SECURITY_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

**Freeze date:** 2026-08-12  
**Purpose:** Citation-ready public explanation of the independent external research corpus. It does not analyse or map to any repository or target system.

## Source-grounded explanation

Systems security engineering is the defensive engineering of systems whose required confidentiality, integrity, availability, authenticity, authority, privacy, safety or mission consequences must remain within stated bounds under intentional adversarial pressure. Its genealogy is plural. Cryptographic systems contributed open-design and key-authority principles; trusted-system and access-control research contributed protection domains, reference monitors, security kernels, confidentiality/integrity/transaction models and least privilege; software-security and secure-development traditions contributed defect prevention, analysis, fuzzing and lifecycle feedback; assurance traditions contributed model-relative proof, evaluation and independent challenge; vulnerability, supply-chain, zero-trust and cyber-resilience traditions added exposure-aware prioritisation, source/build/release provenance, current resource authorization, detection, containment and trustworthy reconstitution. These lineages converged, but no evidence supports treating them as one original method or a single ladder of maturity. [S001–S019] [S061–S065]

The strongest modern synthesis is not 'add more controls'. It is to state the protected consequence and bounded adversary; expose trust and authority assumptions; minimise and compartmentalise privilege, common mechanisms and attack surface; bind identity, authorization, provenance, configuration and evidence to current state; choose assurance that actually discriminates the claim; and prepare to detect, contain, revoke, recover and repair the enabling invariant. Security depth scales with exposure, consequence, irreversibility, novelty and adversary capability. Standards and current guidance strongly support this discipline, while comparative evidence is strongest for particular mechanisms—such as fuzzing, selected formal verification, exploitation-context prioritisation, usable-security effects and observed supply-chain/incident failure modes—and weaker for whole branded programmes. [S018–S020] [S027] [S068–S069] [S076–S077] [S082] [S085–S100] [S109–S120]

## 8–15 strongest surviving defensive engineering properties

### P01 — Explicit protected consequence and security objective
A small, current set of consequence-linked objectives with stated tolerance, decision owner, adversary assumptions, measurable evidence and recovery condition. **Trigger:** Always for consequential systems, new exposed capabilities, material trust-boundary changes, or when risk acceptance is requested. **Cheap path:** For a low-exposure, reversible change, record the protected consequence and a brief invariant/abuse check rather than producing a full control catalogue. **Evidence:** [S001] [S002] [S018] [S019] [S025]

### P02 — Bounded adversary and threat model
A decision-linked, revision-triggered adversary model with explicit exclusions, uncertainty, supplier/identity compromise cases and a lightweight path when consequence is low. **Trigger:** When a consequential decision depends on what an attacker can do, at new trust boundaries, after major change, or when relying on a control with known bypass conditions. **Cheap path:** For low-consequence changes, a short trust-boundary and plausible-abuse check can be sufficient; do not instantiate a full template if it cannot alter a decision. **Evidence:** [S002] [S003] [S079] [S080] [S081]

### P03 — Explicit trust assumptions and trust boundaries
A current authority/data-flow map whose boundaries have explicit guarantees, dependencies, observability, common-mode analysis and reconstitution plan. **Trigger:** New data/authority flow, tenant or supplier relationship, remote administration, agent/tool integration, or concentration of control in a shared service. **Cheap path:** For simple single-user/offline/reversible work, record the few consequential crossings and rely on existing platform isolation where its assumptions are acceptable. **Evidence:** [S002] [S003] [S007] [S008] [S017]

### P04 — Least privilege and authority minimisation
Minimise consequential authority across scope, duration, delegation and parameters while preserving a tested path for legitimate work and emergency recovery. **Trigger:** High-consequence actions, multi-tenant/shared systems, automation/agents, remote administration, production access and broadly reusable credentials. **Cheap path:** For isolated low-consequence work, platform defaults and a coarse role may be cheaper than elaborate fine-grained policy; still avoid unnecessary administrator/root authority. **Evidence:** [S003] [S007] [S008] [S012] [S013]

### P06 — Complete mediation and current authorization
All consequential paths are mediated by analysable enforcement whose decision is current enough for the consequence and whose failure/recovery behaviour is explicit. **Trigger:** Consequential state changes, cross-tenant/data access, delegated service/agent action, privileged APIs and long-lived sessions. **Cheap path:** For public/non-sensitive immutable resources, simple coarse authorization or no authorization can be correct; avoid needless per-request policy complexity. **Evidence:** [S002] [S003] [S017] [S018] [S022]

### P08 — Least common mechanism and common-mode exposure minimisation
Minimise or explicitly govern common-mode dependencies in proportion to correlated consequence; prefer small, analysable shared mechanisms and genuine recovery independence. **Trigger:** Multi-tenant systems, fleet-wide management/update, central identity/policy, common libraries, recovery infrastructure and claims of independent defence layers. **Cheap path:** For small systems, vetted platform sharing may reduce complexity more than bespoke isolation; document and accept the common dependency. **Evidence:** [S003] [S018] [S019] [S043] [S044]

### P13 — Isolation, compartmentalisation and blast-radius limitation
Choose compartments by consequence and compromise propagation; enforce and continuously verify crossings, shared roots and recovery independence. **Trigger:** Multi-tenant data, untrusted code/plugins, high-value secrets, distinct safety/mission domains, supply-chain stages and recovery infrastructure. **Cheap path:** For single-user low-consequence work, standard OS process/account isolation may be sufficient; do not add orchestration layers solely for labels. **Evidence:** [S007] [S008] [S009] [S018] [S019]

### P15 — Secure defaults and safe configurability
Default state covers the common consequential case, risky options require informed bounded action, and operators retain tested availability/recovery routes. **Trigger:** Products/services used at scale, by non-specialists, with internet exposure or complex configurable security. **Cheap path:** For expert-controlled experimental/offline systems, concise documented setup with deterministic checks may substitute for broad default automation. **Evidence:** [S003] [S032] [S033] [S046] [S047]

### P17 — Context- and parameter-bound delegated authority with confused-deputy resistance
Every consequential delegated action carries only the authority needed for that exact resource and parameters, is revalidated at the deputy, and remains revocable/auditable. **Trigger:** Cross-service delegation, payments/destructive operations, cloud roles, callbacks, agents/tools, file/object references and automation with ambient credentials. **Cheap path:** For an internal low-consequence operation with one resource and no delegation, ordinary local authorization plus input validation may suffice. **Evidence:** [S007] [S008] [S017] [S013] [S022]

### P21 — Secrets, keys and certificates as an authority lifecycle
Treat every secret/key as scoped, expiring authority with known consumers, provenance, revocation propagation and tested loss/compromise recovery. **Trigger:** Any secret that grants consequential access, decrypts durable data, signs software/identity, anchors trust or cannot be cheaply replaced. **Cheap path:** For local low-consequence ephemeral data, platform-provided credential stores and automatic short-lived credentials may be sufficient; avoid custom key infrastructure. **Evidence:** [S014] [S015] [S016] [S040] [S038]

### P24 — Continuous secure lifecycle: security feedback everywhere
Security work occurs wherever a consequential assumption can be introduced or invalidated, with lightweight defaults for ordinary changes and deeper assurance for high-adversarial-pressure claims. **Trigger:** Products/services with ongoing change, exposed attack surface, dependencies and material consequence. **Cheap path:** For low-risk/reversible changes, reuse established secure defaults and deterministic automated checks; escalate only when boundary, authority or consequence changes. **Evidence:** [S018] [S020] [S054] [S058] [S059]

### P31 — Independent, diverse and current-configuration-bound assurance evidence
Use the minimum mutually informative evidence set adequate to consequence; disclose model/environment gaps and automatically invalidate stale state-bound claims. **Trigger:** High-consequence claims, certification, external trust, major releases, common-mode risk and any completeness/security assertion. **Cheap path:** For low-risk reversible change, one high-signal deterministic check plus provenance may be enough; do not multiply checks without expected discrimination. **Evidence:** [S009] [S010] [S011] [S027] [S042]

### P33 — Exposure-, reachability- and consequence-aware vulnerability prioritisation
Use the cheapest context that changes order—known exploitation, exposure, reachable vulnerable function, privilege and consequence—without claiming exact risk probabilities. **Trigger:** Non-trivial backlog, heterogeneous assets, delayed patches, transitive dependencies or conflict between patch urgency and stability. **Cheap path:** For a small inventory with a safely deployable fix and material exposure, patch directly after basic validation; elaborate scoring adds no value. **Evidence:** [S028] [S071] [S072] [S073] [S074]

### P36 — Source/build provenance, build isolation and source-to-binary correspondence
Artifact acceptance depends on verified provenance and bounded builder authority appropriate to consequence, with explicit residual toolchain/hardware assumptions. **Trigger:** Externally distributed or privileged artifacts, automated deployments, high-value supply chains, third-party builds and recovery images. **Cheap path:** For a small internal low-risk tool, a clean controlled build, pinned hashes and recorded source/artifact digest may suffice; full SLSA infrastructure is optional. **Evidence:** [S034] [S035] [S036] [S061] [S062]

### P43 — Recovery and reconstitution from trusted sources with trust re-establishment
Recovery succeeds only when required service returns and current objectives/invariants are re-established from independently trustworthy material under a bounded residual-risk decision. **Trigger:** Ransomware/destructive attack, management/identity/supply-chain compromise, uncertain fleet state or critical corruption. **Cheap path:** For a small reversible stateless service, rebuild from verified source/artifact and restore minimal data with a targeted integrity check. **Evidence:** [S019] [S030] [S037] [S065] [S114]

## Common caricatures and ceremonies to reject

| Caricature/ceremony | Public correction | Evidence |
| --- | --- | --- |
| Security means patch vulnerabilities. | Patching is one response; mature work prioritises exact affected exposure, reachability, exploitation, consequence and safe rollout. | S028; S071–S077 |
| Passing compliance means secure. | Compliance maps obligations and evidence; it cannot prove current adversarial effectiveness or absence of compromise. | S009–S011; S025–S027 |
| More controls/products mean more security. | Layers help only when they cover distinct paths and do not share decisive failure modes. | S018–S019; S085–S087; S109; S113 |
| Zero trust means trust nothing. | It means no implicit authorisation from location; identity, policy, hardware, telemetry and recovery assumptions remain. | S022–S024 |
| A penetration test proves security. | A test samples one bounded target, period, access level and adversary approximation. | S042; S085–S086 |
| An SBOM proves supply-chain trust. | It may describe components; completeness, provenance, affectedness, build authority and currentness are separate. | S049; S067–S070 |
| CVSS is risk. | CVSS is technical severity information; local risk includes exposure, reachability, exploit evidence, consequence and uncertainty. | S071–S077 |
| Encryption solves trust. | Cryptography protects a bounded property under key/endpoint assumptions; authorization, build, availability and recovery remain. | S014–S016; S040; S109 |
| Users are the weakest link. | Burden, incentives and design shape behaviour; safe defaults, phishing resistance, usable recovery and producer responsibility are stronger general lessons. | S097–S102 |
| A signed update is safe. | A signature authenticates origin under a key; a compromised signer or defective authorised update can still cause compromise/outage. | S065; S109; S113 |

## Important criticisms and limits

| Limit | What it changes | Evidence |
| --- | --- | --- |
| Threat models are subjective, manual and often stale. | Retain decision-linked assumptions with change triggers; do not mandate template completion. | S081–S084 |
| Scanners and static analyses have class/tool-specific blind spots and noise. | Use calibrated bounded evidence and disclose overlap/suppressions; a clean dashboard is not security. | S085–S087 |
| Formal proof is conditional on specification and environment correspondence. | Use it for narrow high-consequence claims and publish assumptions. | S090–S093 |
| Vulnerability severity/findings poorly approximate real exploitation or consequence. | Join technical severity to current exposure/path/context and uncertainty. | S071–S077 |
| SBOM tools disagree and inventory does not establish affectedness/provenance. | Treat inventory quality and source/build evidence as separate claims. | S067–S070 |
| Security training and repeated warnings can have weak or decaying effects. | Design out routine human decisions and train only residual role-specific work. | S097–S100 |
| Central identity, signing, policy, build and update planes create common-mode risk. | Bound authority, observe control planes and prepare independent clean recovery. | S109; S111–S113 |
| Secure controls can damage privacy, safety, availability and recoverability. | Engineer hybrid failure/degraded modes and test both sides of the consequence. | S045; S113; S117 |
| Compliance and maturity scores can reward artifact production rather than outcomes. | Separate obligation evidence from adversarial claims and monitor proxy gaming. | S009–S011; S103–S104 |
| AI/agent security evidence is frequently benchmark- and assumption-bound. | Treat it as a domain translation with realistic system authority/provenance/operation evidence. | S021; S115–S116 |

## From perimeter/vulnerability/compliance security to lifecycle trustworthiness

Perimeter security assumed that topology correlated with trust; vulnerability-centric programmes assumed that listed flaws and technical severity were the principal actionable state; compliance programmes made standardised obligations and evidence administrable. Each contributed useful mechanisms, but distributed services, identity and supply-chain compromise, continuous delivery and incident evidence exposed their limits. The evolved form uses topology only as a containment signal, treats authentication as distinct from current resource/parameter authorization, treats CVE/CVSS/SBOM/certificates as bounded evidence inputs, and binds security claims to exact identity, authority, dependency, build, artifact, configuration and deployment state. Prevention remains essential, but trustworthy operation also requires detection, containment, revocation, clean recovery and incident-driven repair. [S018–S025] [S033–S049] [S071–S078] [S109–S114]

## Citation-ready factual claims

- **C01:** The 1972 Anderson report defined a reference monitor as tamper-resistant, always invoked and small enough for analysis/testing, while explicitly assuming malicious users and bounded physical, communications and hardware conditions. [S002]
- **C02:** Saltzer and Schroeder's 1975 paper articulated least privilege, fail-safe defaults, complete mediation, economy of mechanism, open design, separation of privilege, least common mechanism and psychological acceptability as design principles rather than a compliance catalogue. [S003]
- **C03:** Bell–LaPadula, Biba and Clark–Wilson addressed materially different confidentiality, integrity and commercial-transaction policy problems; they are not interchangeable stages of one universal access-control model. [S004–S006]
- **C04:** NIST SP 800-160 Vol. 1 Rev. 1 treats security as an emergent system property requiring systems engineering across the lifecycle, not merely component controls. [S018]
- **C05:** NIST SP 800-160 Vol. 2 Rev. 1 organises cyber-resilience engineering around anticipating, withstanding, recovering and adapting under adverse conditions. [S019]
- **C06:** NIST's zero-trust architecture removes implicit trust based on network location but still depends on identity, policy, enforcement, telemetry and administrative trust assumptions. [S022–S024]
- **C07:** Current NIST digital-identity guidance separates identity proofing, authentication/authenticator management and federation; these do not themselves determine resource authorization. [S038–S039]
- **C08:** Recent empirical threat-modelling research in open-source projects reports largely ad hoc practice and recurring problems of overhead, completeness, coordination and currentness. [S082]
- **C09:** A 2022 peer-reviewed comparison of 24 web vulnerability scanners across 11 vulnerability classes found materially varying detection performance, so multiple scanners do not imply independent or complete assurance. [S086]
- **C10:** An FSE 2025 empirical study of 7,357 static-analysis suppressions across 46 Python projects found that suppressions reflect false positives, tool/configuration limitations and actionability trade-offs; many suppressions affected no current warning. [S087]
- **C11:** An empirical study of 23,907 OSS-Fuzz bugs across 316 projects supports continuous fuzzing as a strong defect-discovery technique while not establishing absence of semantic or environmental vulnerabilities. [S088]
- **C12:** seL4 demonstrates high-strength implementation-level formal verification for a real kernel, while the project's published assumptions show why model, hardware, toolchain and environment boundaries must remain explicit. [S090–S091]
- **C13:** CVSS v4 guidance explicitly distinguishes technical severity from risk; KEV, EPSS, exposure, reachability and consequence are separate prioritisation inputs. [S071–S075]
- **C14:** A large 2026 SBOM study generated 55,444 SBOMs with six tools from 3,287 repositories and reported very low cross-tool package and licence consistency, demonstrating that artifact existence is not inventory agreement. [S068]
- **C15:** The 2026 multi-agency SBOM minimum-elements guidance adds generation context, tool identity/version, hashes, signatures, versioning, currentness and explicit unknowns—features consistent with treating SBOMs as evidence inputs rather than trust conclusions. [S049]
- **C16:** SolarWinds, XZ and Storm-0558 incident evidence shows that repository/build/maintainer/signing/identity control paths can invalidate otherwise legitimate-looking software or sessions. [S109; S111–S112]
- **C17:** The 2024 CrowdStrike incident demonstrates that a trusted security-content update can become a fleet-wide common-mode availability failure, so signed/authorised updates still require staged safety, observability and recovery. [S113]
- **C18:** Longitudinal warning research found declining attention/adherence under repeated warnings, and a 19,500-person field study found limited effects for common embedded phishing-training conditions. [S099–S100]
- **C19:** Current CISA and ENISA secure-by-design guidance shifts responsibility toward producers, secure defaults and iterative decision-linked threat modelling; this is normative/current practice evidence, not proof that programme branding alone improves outcomes. [S046–S052]
- **C20:** Current ransomware guidance continues to call for offline, immutable, segmented and tested backups because recovery sources and credentials are adversary targets. [S114; S120]

## Direct-lineage, convergence and domain-translation distinctions

| Classification | Public wording | Examples |
| --- | --- | --- |
| DIRECT/TRUSTED_SYSTEMS_ANCESTRY | Documented historical transmission from trusted-system, protection-domain, reference-monitor or evaluation work. | P03, P06, P09, P13, P30–P31; S001–S009 |
| CRYPTOGRAPHIC_SYSTEMS_IMPORT | Strong bounded mechanisms imported into system identity, signing and key lifecycle. | P10, P21, P37; S014–S016; S040 |
| SOFTWARE_SECURITY_IMPORT_OR_SHARED_ANCESTRY | Implementation and secure-development practices integrated into the larger lifecycle. | P24, P26–P29; S020; S050–S051; S085–S089 |
| CONVERGENT_PROPERTY | Similar engineering need emerged through multiple traditions without proof of one direct line. | P01, P11, P47–P49. |
| RELIABILITY_OR_RESILIENCE_IMPORT | Continuity/recovery ideas altered by an adaptive adversary and common-mode targeting. | P43–P45; S019; S030. |
| SAFETY_SECURITY_COENGINEERING | Domain-specific joint treatment where physical safety/availability changes security failure direction. | P05, P38, P49; S045; S117. |
| DOMAIN_TRANSLATION | Established security properties applied to cloud/container/OT/medical/AI/agent contexts with additional assumptions. | P19, P45, P59–P60; S043–S045; S115–S118. |
| ONLY_ANALOGOUS | Retrospective similarity without documented lineage or sufficient mechanism equivalence; do not claim ancestry. | Rejected rhetoric/labels where applicable. |

## Current-state and frontier notes

| Frontier | Public-safe current statement | Evidence limit | Sources |
| --- | --- | --- | --- |
| Systems-security engineering and resilience | NIST SP 800-160 Vols. 1–2 remain the strongest current authoritative integration of trustworthy-system and cyber-resilience concepts. | Operationally established guidance; not comparative proof of optimal integrated method. | S018–S019 |
| Secure-by-design/default producer responsibility | CISA/partners and ENISA increasingly place burden on product design/defaults and treat threat modelling as iterative/decision-linked. | Strong normative/operational programme; field causal evidence and liability allocation remain limited. | S046–S052 |
| Current digital identity and zero trust | NIST 800-63-4 and implemented ZTA guidance refine proofing/authentication/federation, workload/resource policy and current authorization. | Architecturally mature; central control-plane resilience/privacy/legacy costs remain. | S022–S024; S038–S039 |
| Supply-chain provenance | SLSA/in-toto/Sigstore/TUF and NIST C-SCRM offer strong mechanism/guidance families for builds, signing and updates. | Mechanisms operationally established; verifier trust, toolchain roots and source-to-binary evidence remain assumption-sensitive. | S034–S036; S061–S066 |
| SBOM quality and affectedness | The 2026 minimum elements add generation/tool/version/hash/signature/currentness/unknown context, while recent studies expose tool inconsistency and false-positive affectedness. | Useful inventory practice; quality/reachability evidence mixed and ecosystem-specific. | S049; S067–S070 |
| Memory safety | CISA/NSA roadmaps treat migration as strategic defect-class reduction, especially for new high-exposure code. | Strong mechanism and incident-class rationale; migration economics and comparative field outcomes vary. | S050–S051 |
| Assurance portfolios | Formal verification, fuzzing, static/dynamic testing and adversarial challenge each support different claims and failure hypotheses. | Strong technique-specific evidence; independence and marginal information are under-measured. | S085–S094 |
| Vulnerability prioritisation | CVSS v4, KEV, EPSS and empirical exploitation work support separation of technical severity from current risk. | Operationally established inputs; predictions/reachability can be wrong or stale. | S071–S077 |
| Recovery and reconstitution | Current NIST/CISA guidance increasingly treats clean recovery, separated backups and trust re-establishment as engineering, not disaster-plan paperwork. | Strong incident/guidance support; trust-restoration evidence and metrics remain immature. | S030; S037; S114; S120 |
| Cloud common-mode dependency | Storm-0558 and fleet update incidents expose identity/signing/control/update concentration as contemporary system-level failure modes. | Strong incident evidence, weak population-level comparative architecture data. | S109; S113 |
| Usable/phishing-resistant security | Current identity guidance plus longitudinal/field studies support reducing prompts/advice and designing safer workflows. | Strong task-level evidence; direct incident reduction and accessible recovery trade-offs require more study. | S038–S039; S097–S100 |
| AI/ML/agentic security | NIST/partner guidance now frames data/model/software/tool lifecycle threats, but many evaluations remain model- or benchmark-centred. | Promising/domain-specific and assumption-sensitive, not mature universal practice. | S021; S115–S116 |
| Sector cyber-physical co-engineering | OT and 2026 FDA guidance make safety, availability, secure update, SBOM and monitoring interactions explicit. | Domain-established guidance; device/sector evidence and legacy constraints vary. | S045; S117 |
| Quantitative cyber risk and maturity metrics | Risk models remain constrained by sparse, selected and incompatible loss/incident data. | Useful for explicit scenarios; hype-prone when converted to precise universal scores. | S103–S104 |

## Explicit evidence limits and claims not to make

- Do not claim that one formal methodology called Evolved Systems Security Engineering exists; the label is analytical.
- Do not claim that control count, audit/certificate status, scanner cleanliness, zero findings, an SBOM, a signature, a provenance record, an encryption badge or a zero-trust programme proves security.
- Do not claim that a formal proof establishes properties outside its specification, TCB, hardware/toolchain and deployment assumptions.
- Do not claim that recent guidance is empirically optimal merely because it is current or authoritative.
- Do not universalise effect sizes from selected tools, ecosystems, organisations or incidents.
- Do not claim that confidentiality–integrity–availability is a complete objective taxonomy for every mission, privacy, safety or authority problem.
- Do not claim that humans are inherently the weakest link or that training can substitute for safe design/defaults and phishing-resistant controls.
- Do not claim that resilience excuses preventable defects or that restored availability means trust/integrity has been re-established.
- Do not claim that zero trust eliminates trust; it relocates and makes some assumptions explicit while potentially centralising others.
- Do not claim that AI/ML/agentic security has mature deployment-predictive evidence across systems; many results remain domain- and adversary-assumption sensitive.

## Suggested public page outline

1. Definition and scope: protected consequences under intentional adversarial pressure.  
2. Plural genealogy: cryptographic systems; trusted systems/access control; architecture; software/lifecycle; assurance; vulnerability; supply chain; identity/zero trust; resilience.  
3. The strongest surviving properties.  
4. Trust, identity, authorization and delegation.  
5. Provenance, configuration and current-state evidence.  
6. Assurance: what tests, proofs and adversarial exercises can and cannot establish.  
7. Detection, containment, recovery and incident learning.  
8. Security usability and tensions with privacy, safety and availability.  
9. Ceremonies and proxies to reject.  
10. Current frontiers and evidence limits.  
11. Source notes keyed to the frozen source table.

## Public-documentation freeze note

The wording above is bounded to the 60-property frozen denominator and 117-source supporting table. Public condensation must not silently remove the anti-properties, assumption limits or distinction between guidance, formal evidence, incidents and empirical comparison.

EVOLVED_SYSTEMS_SECURITY_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 60
PROPERTY_POPULATION_EXAMINED: 60
PROPERTY_COVERAGE: 60/60
EVOLVED_SYSTEMS_SECURITY_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES