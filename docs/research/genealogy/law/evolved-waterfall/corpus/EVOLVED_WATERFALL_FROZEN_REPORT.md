# EVOLVED_WATERFALL — Frozen External Research Report

```text
ANALYTICAL_LABEL                 EVOLVED_WATERFALL
RESEARCH_STATE                   FROZEN
PROPERTY_POPULATION_TOTAL        38
PROPERTY_POPULATION_EXAMINED     38
PROPERTY_COVERAGE                38/38
CROSSWALK_WORTHY_PROPERTIES      33
REJECTED_OR_CEREMONIAL_CANDIDATES 5
ACCESS_DATE                      2026-08-11
IMPLEMENTAUDIT_OR_REPOSITORY_ANALYSIS NOT_PERFORMED
```

## Executive finding

`EVOLVED_WATERFALL` is not supported as a fixed lifecycle or as “Waterfall with a few iterations.” The defensible surviving object is a **risk- and commitment-sensitive assurance architecture**. It keeps authoritative but revisable intent, configuration and interface state; retires uncertainty through working evidence before hard commitments; plans and performs verification at the levels where failure can emerge; validates intended use; distinguishes qualification, acceptance and certification; preserves release and evidence provenance; and applies lifecycle obligations incrementally, concurrently and recursively.

The provisional reversibility claim survives only after correction. Control should not rise merely because a project is later in a nominal phase, nor because a code edit is difficult. Its expected value rises when a change has material consequence, broad coupling, delayed observability, scarce test opportunities, external contractual or regulatory authority, difficult recovery, or hard-to-unwind physical or operational commitments. Irreversibility is one trigger dimension, not a universal cost-of-change law. Added control can itself make change slower, more expensive and less observable.

The historical artefacts—large requirements documents, manual trace matrices, standing change-control boards, fixed review meetings and phase-completion gates—are not general properties. They survive only when they are the lowest-cost truthful mechanism for an actual failure mode. A gate that approves documents without changing a decision, a trace set that is stale, or a controlled specification disconnected from the as-built/as-deployed system is assurance theatre.

## Frozen denominator and adjudication rule

The denominator is frozen at **38 candidates** discovered across the historical, standards, safety, regulatory, empirical and critical literature. Thirty-three are retained for later property-level crosswalk; five are dispositioned as rejected or ceremonial. No candidate is omitted because its evidence is mixed, domain-specific or unresolved. Freezing denotes research sufficiency for adjudication, not proof of universal usefulness.

| STATUS | COUNT |
| --- | --- |
| CEREMONY_NOT_GENERAL_PROPERTY | 2 |
| CONTEXT_DEPENDENT | 9 |
| HIGH_CONSEQUENCE_CONTEXT_PROPERTY | 7 |
| REJECTED_OR_DISFAVOURED | 3 |
| RETAINED_IN_EVOLVED_FORM | 8 |
| STRONGLY_RETAINED | 5 |
| USEFUL_BUT_EASILY_BUREAUCRATISED | 4 |

## Central hypothesis adjudication

```text
HYPOTHESIS:
  stronger baselines, traceability, independent verification, configuration
  control, interface control and acceptance evidence become more valuable as
  changes become expensive, consequential, long-latency or irreversible.

DISPOSITION:
  QUALIFIED_AND_NARROWED

SUPPORTED:
  control value often rises with consequence, coupling, observability latency,
  external commitment, recovery difficulty and scarcity of representative test.

NOT_SUPPORTED:
  a universal monotonic rule; a universal exponential late-change multiplier;
  automatic value from heavier documents, boards, gates or independence.

CORRECTION:
  escalate the minimum truthful evidence and authority needed at a commitment
  boundary, while preserving a cheap exploratory path before that boundary.
```

### Four costs that must not be collapsed

| DIMENSION | QUESTION | WARNING |
| --- | --- | --- |
| EDIT_COST | How costly is the direct change to code, model, document or physical item? | Often the least important cost. |
| PROPAGATION_COST | How many dependent interfaces, tests, analyses, suppliers and evidence items must change? | Requires current dependency/trace knowledge. |
| COMMITMENT_UNWIND_COST | What contracts, tooling, production, certification, migration or political commitments must be reversed? | Can increase before implementation is 'late'. |
| FAILURE_AND_RECOVERY_COST | What harm, outage, loss, recovery effort or irreversible side effect occurs if wrong? | Can be high even when code rollback is easy. |
| OBSERVABILITY_LATENCY | How long before correctness or harm is observable? | Fast iteration is unsafe when feedback is delayed or ambiguous. |
| COUPLING_AND_RADIUS | How broadly can the change propagate technically and organisationally? | Local edit does not imply local impact. |
| EXTERNAL_AUTHORITY | Does a regulator, acquirer, operator or public-risk authority control use? | Legal authority may impose non-negotiable minima. |
| TEST_OPPORTUNITY_SCARCITY | Are representative tests rare, destructive or expensive? | Raises value of modelling/qualification but also uncertainty about evidence. |
| ADVERSARIAL_OR_REMEDIATION_URGENCY | Does delay itself increase security or operational risk? | Heavy approval can be the unsafe choice. |

Technical rollback is not equivalent to reversal of external effect. A release can be easy to redeploy yet have already disclosed private data, actuated unsafe hardware, executed a financial transaction, corrupted durable state, consumed a scarce test opportunity, or changed a certified/contractual state.

## Terminology firewall

| TERM | QUESTION | REFERENCE | DOES_NOT_BY_ITSELF_ESTABLISH |
| --- | --- | --- | --- |
| Verification | Does the realised item satisfy its specified requirements? | Requirement, specification, interface or imposed condition. | That the requirement is the right requirement. |
| Validation | Does the item fulfil intended use and stakeholder need in the intended operational context? | Mission, concept of operations, users and environment. | That every specified requirement is met. |
| Qualification | Has a design, process, type or article demonstrated capability across a defined envelope, often with margin? | Qualification basis, representative article and environments. | Acceptance of every delivered instance. |
| Acceptance | Has the authorised acquirer/operator accepted a specific identified delivery against agreed criteria? | Delivered configuration, acceptance criteria, evidence, exceptions and authority. | Regulatory certification or fitness outside the accepted scope. |
| Certification | Has an empowered authority made the required attestation under a governing regime? | Certification basis, applicable law/standard and approved evidence. | Universal safety, user value or freedom from residual risk. |
| Independent V&V | Has verification/validation received sufficient technical, managerial and financial independence? | Risk, criticality, conflict of interest and assurance scope. | Better outcomes in every project or absence of coordination cost. |
| Inspection or review | What can structured examination reveal before or without execution? | Requirement, design, code, procedure, model or evidence. | Operational suitability. |
| Test | What does controlled execution or measurement demonstrate? | Test article, environment, procedure and expected result. | Completeness of requirements or intended-use validity. |
| Operational evaluation | How does the system perform with representative users, missions and conditions? | Operationally representative context. | Acceptance or certification unless the governing scheme says so. |

The firewall preserves these non-equivalences:

```text
requirements complete != right requirements
implementation matches specification != system solves the need
component verified != integrated system validated
test passed != design qualified for the intended envelope
qualification evidence != this delivered configuration was accepted
document approved != actual implementation or deployment state
acceptance != certification
certification != elimination of residual risk
```

## Research-burden closure

| BURDEN | DISPOSITION | FINDING | EVIDENCE LIMIT |
| --- | --- | --- | --- |
| Exact textbook/transmission history of the Waterfall caricature | CLOSED_TO_DECISION_RELEVANT_LIMIT | Bell and Thayer (1976) are the located primary naming hinge; later pedagogical diagrams often foregrounded distinct stages, while some textbooks simultaneously acknowledged iteration. No single author-to-textbook causal chain is proven. Real procurement, approval and organisational structures materially reinforced the caricature. | A complete bibliometric transmission genealogy was not established and is not required to distinguish Royce, pedagogical simplification and deployed sequentiality. |
| Multiple V-model/Vee genealogies | CLOSED | At least three decision-relevant families must be separated: the software V/V-chart linking definition products to evaluation (Boehm 1979; Rook 1986), the systems-engineering Vee (Forsberg–Mooz 1991, explicitly incremental/evolutionary by 1995), and Germany's V-Modell/V-Modell XT governance framework. Shared geometry does not prove shared ancestry or mechanism. | Earlier diagrammatic antecedents may exist, but they do not change the required three-family distinction. |
| Systems-engineering evolution beyond fixed phase order | CLOSED | Current ISO 15288/12207 and NASA guidance treat lifecycle processes as outcomes and responsibilities applied iteratively, concurrently, recursively and incrementally, with tailoring and no universal phase sequence. | Normative modernisation does not guarantee non-bureaucratic implementation. |
| Configuration-management history and empirical engineering value | CLOSED_WITH_EVIDENCE_LIMIT | The surviving property is configuration identity, integrity, status and change provenance across requirements, models, builds, releases and deployed assets—not freezing or a standing board. Strong domain/failure rationale exists; broad controlled causal return evidence is sparse. | Mostly standards, mishap/audit evidence and qualitative cases; no universal ROI threshold. |
| Interface-control history and empirical engineering value | CLOSED_WITH_CONTEXT_LIMIT | Owned, testable contracts are strongly justified at cross-team, supplier, physical and independently released boundaries. Formal ICD/board machinery is not justified for every local interface. | Direct counterfactual causal studies are limited; support is mechanistic, domain and mishap based. |
| Traceability cost/benefit and stale-traceability failure | CLOSED_MIXED | Controlled experiments show task speed/correctness gains under good traces; observational evidence links completeness with fewer defects; reviews identify link creation/maintenance as the main cost and call for stronger industrial evidence. Selective, queryable, maintained trace is retained; exhaustive manual matrices are not. | No validated general net-benefit threshold; ideal-trace experiments overstate real-world conditions. |
| Independent V&V outcomes and independence conditions | CLOSED_MIXED | Independence can find unique defects and counter incentive bias, but comparative outcome/economic evidence is mixed and older. Scope should rise with criticality; technical, managerial and financial independence trade against access and feedback speed. | Modern causal comparisons and calibrated scope thresholds remain sparse. |
| Qualification, validation, acceptance and certification across domains | CLOSED_WITH_TERMINOLOGY_FIREWALL | Verification addresses specified requirements; validation intended use; qualification a design/type/process envelope; acceptance an authorised decision over a delivered identified item; certification an empowered external attestation against a governing basis. Domain terminology varies, so the applicable regime controls. | No single dictionary overrides domain-specific legal definitions. |
| Safety/assurance-case lineage | CLOSED_MIXED | Goal-setting safety regimes shifted responsibility toward a structured through-life argument and evidence. Current guidance explicitly rejects equating the safety case with its report and records confirmation, staleness, compliance-only and after-the-fact pathologies. | Strong practice rationale, weak comparative outcome evidence. |
| Phase-gate and milestone gaming | CLOSED | The surviving property is a real evidence-backed commitment decision with stop/redirect authority. Fixed calendar gates and document-completion meetings are ceremony; escalation-of-commitment and acquisition evidence show why formal milestones may fail. | Gate effectiveness depends on actual decision power and evidence quality; no universal meeting form. |
| Predictive estimation, sunk cost and false certainty | CLOSED_MIXED | Forecasting remains useful for funding, suppliers and capacity, but mature practice uses ranges, assumptions, outside views, independent estimates and updates from actuals. Point-plan certainty and baseline protection are rejected. | No universally dominant estimation method; behavioural and political distortions remain. |
| Digital engineering/model-authority failure modes | CLOSED_MIXED | Digital models can reduce handoff and enable analysis, but authority ambiguity, interoperability, semantics, access, model validation, staleness and divergence from physical/deployed state are first-order risks. Tool adoption is not a property. | Many benefits are perceived or expected; measured comparisons remain sparse. |
| DevSecOps and continuous-assurance hybrids | CLOSED | Current defence/aerospace practice permits iterative delivery while retaining immutable baselines, traceable evidence, independent evaluation and explicit operational authority. Continuous evidence changes cadence and packaging, not the need to know what was tested and who accepts risk. | Automation can reproduce weak tests and compromised evidence continuously. |
| Reversibility/commitment thresholds across domains | SEARCHED_GENERAL_THRESHOLD_UNRESOLVED | Cross-domain evidence supports graded controls by consequence, safety significance, coupling, external commitment, observability and recovery—not calendar lateness alone. No validated universal threshold function exists. Technical rollback can coexist with irreversible harm; heavy controls can themselves increase latency and sunk cost. | Domain-specific calibration remains necessary. |

Source IDs for each burden are preserved in the machine-readable ledger.

## Source standard and method

The investigation prioritised primary historical papers; current lifecycle and V&V standards; official government, aerospace, nuclear, rail, automotive and medical-device material; authoritative handbooks; peer-reviewed empirical work; and strong criticism. Standards establish required concepts and domain practice, not universal causal effect. Case studies establish real failure mechanisms but retain domain limits. Historical resemblance is not treated as direct lineage without evidence.

Evidence labels used in the ledger:

- `A_*`: strong convergence of primary standards, domain evidence, failure evidence or cross-tradition support.
- `B_*`: strong mechanism or domain support with important generalisation limits.
- `C_*`: mixed empirical evidence, uncertain net benefit or outcome evidence weaker than normative guidance.

## Source register

<a id="source-s001"></a>
### S001 — Production of Large Computer Programs

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/MAHC.1983.10102
- `AUTHOR_OR_ORGANISATION`: Herbert D. Benington
- `DATE_VERSION_EDITION`: Presented 1956; republished with retrospective foreword, 1983
- `SOURCE_CLASS`: PRIMARY_HISTORICAL_PAPER_PLUS_RETROSPECTIVE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: 1983 foreword; original paper Figure 4 and testing/documentation discussion, pp. 350–361
- `CLAIM_SUPPORTED`: Large-system staged engineering, controlled interfaces, successive testing, records and technical leadership pre-dated Royce; the retrospective reports prototyping and evolutionary learning.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: RELATED_PLAN_DRIVEN_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: The prototype and claimed cost saving are retrospective recollections, not controlled evidence.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s002"></a>
### S002 — Software Engineering: Report of a Conference Sponsored by the NATO Science Committee

- `STABLE_URL_OR_LOCATOR`: https://homepages.cs.ncl.ac.uk/brian.randell/NATO/nato1968.PDF
- `AUTHOR_OR_ORGANISATION`: Peter Naur and Brian Randell (eds.)
- `DATE_VERSION_EDITION`: 1968
- `SOURCE_CLASS`: PRIMARY_CONFERENCE_REPORT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Design, simulation, feedback, limited initial systems and acceptance-testing discussions throughout the report
- `CLAIM_SUPPORTED`: The pre-Royce software-engineering conversation already included feedback, simulation, prototypes, limited releases and objective acceptance evidence.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CONVERGENT_ENGINEERING
- `CONTRARY_EVIDENCE_OR_LIMIT`: An edited record of heterogeneous views, not one prescribed method or outcome study.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s003"></a>
### S003 — Managing the Development of Large Software Systems

- `STABLE_URL_OR_LOCATOR`: https://dl.acm.org/doi/10.5555/41765.41801
- `AUTHOR_OR_ORGANISATION`: Winston W. Royce
- `DATE_VERSION_EDITION`: 1970
- `SOURCE_CLASS`: PRIMARY_HISTORICAL_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Figures 2–4; preliminary programme design; documentation; 'do it twice'; test planning; customer involvement
- `CLAIM_SUPPORTED`: Royce used a staged sequence as a problem setup, called the unmodified form risky, and proposed feedback, preliminary design, a pilot, early testing, documentation and customer review.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DIRECT_LINEAGE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Experience-based management argument, not comparative causal evidence; still strongly staged and formal.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s004"></a>
### S004 — Software Requirements: Are They Really a Problem?

- `STABLE_URL_OR_LOCATOR`: https://dl.acm.org/doi/10.5555/800253.807650
- `AUTHOR_OR_ORGANISATION`: Thomas E. Bell and Thomas A. Thayer
- `DATE_VERSION_EDITION`: 1976
- `SOURCE_CLASS`: PRIMARY_CONFERENCE_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Figure 1; sections II–III
- `CLAIM_SUPPORTED`: An early published use of 'waterfall' for the Royce sequence and empirical evidence that requirements defects and changes persisted through development.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DIRECT_LINEAGE_AND_NAMING_HINGE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Does not prove the complete later textbook transmission chain or that the authors endorsed absolute one-pass development.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s005"></a>
### S005 — Guidelines for Verifying and Validating Software Requirements and Design Specifications

- `STABLE_URL_OR_LOCATOR`: https://apps.dtic.mil/sti/pdfs/ADA067646.pdf
- `AUTHOR_OR_ORGANISATION`: Barry W. Boehm
- `DATE_VERSION_EDITION`: 1979
- `SOURCE_CLASS`: PRIMARY_GOVERNMENT_TECHNICAL_REPORT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: pp. 3–6: V-chart, requirement baseline, iterative V&V loops, problem reporting and testability criteria
- `CLAIM_SUPPORTED`: An early software V-chart pairs definition products with evaluation and explicitly includes iterative feedback and baseline correction.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DIRECT_LINEAGE_TO_SOFTWARE_V_FAMILY
- `CONTRARY_EVIDENCE_OR_LIMIT`: A V&V planning representation, not evidence that every V-shaped lifecycle shares this ancestry.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s006"></a>
### S006 — A Rational Design Process: How and Why to Fake It

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/TSE.1986.6312940
- `AUTHOR_OR_ORGANISATION`: David L. Parnas and Paul C. Clements
- `DATE_VERSION_EDITION`: 1986
- `SOURCE_CLASS`: PRIMARY_SCHOLARLY_CRITICISM
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Section II and documentation guidance, pp. 251–257
- `CLAIM_SUPPORTED`: Perfectly rational top-down chronology is impossible, but coherent, current design records still support review, transfer and maintenance.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: REACTION_TO_WATERFALL
- `CONTRARY_EVIDENCE_OR_LIMIT`: Normative and analytic argument rather than comparative project-outcome evidence.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s007"></a>
### S007 — No Silver Bullet—Essence and Accidents of Software Engineering

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/MC.1987.1663532
- `AUTHOR_OR_ORGANISATION`: Frederick P. Brooks Jr.
- `DATE_VERSION_EDITION`: 1987
- `SOURCE_CLASS`: PRIMARY_SCHOLARLY_ESSAY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Sections on requirements, prototyping and incremental development
- `CLAIM_SUPPORTED`: Complex systems require repeated user–designer interaction and evolutionary growth rather than complete one-shot specification.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: REACTION_TO_WATERFALL
- `CONTRARY_EVIDENCE_OR_LIMIT`: Influential expert synthesis, not a controlled lifecycle comparison.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s008"></a>
### S008 — A Spiral Model of Software Development and Enhancement

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/2.59
- `AUTHOR_OR_ORGANISATION`: Barry W. Boehm
- `DATE_VERSION_EDITION`: 1988
- `SOURCE_CLASS`: PRIMARY_SCHOLARLY_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Spiral-cycle quadrants and risk-driven model-selection discussion, pp. 61–72
- `CLAIM_SUPPORTED`: Risk rather than fixed phase order can determine prototyping, simulation, incremental construction and planning activities.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: REACTION_TO_WATERFALL
- `CONTRARY_EVIDENCE_OR_LIMIT`: Does not show that all organisations can estimate or retire risk effectively.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s009"></a>
### S009 — DOD-STD-2167A: Defense System Software Development

- `STABLE_URL_OR_LOCATOR`: https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=301394
- `AUTHOR_OR_ORGANISATION`: United States Department of Defense
- `DATE_VERSION_EDITION`: 1988
- `SOURCE_CLASS`: PRIMARY_STANDARD
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Scope/application, development activities, reviews, configuration management and qualification testing
- `CLAIM_SUPPORTED`: The standard formally allowed tailoring, prototyping, overlap and recursive/iterative application while imposing ordered activities, data, reviews, baselines and approvals.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: REAL_DEPLOYED_PLAN_DRIVEN_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Textual permission to iterate does not establish how contracts and programmes implemented it.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s010"></a>
### S010 — Controlling Software Projects

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1049/sej.1986.0003
- `AUTHOR_OR_ORGANISATION`: Paul Rook
- `DATE_VERSION_EDITION`: 1986
- `SOURCE_CLASS`: PRIMARY_PRACTICE_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Lifecycle control and V-shaped representation
- `CLAIM_SUPPORTED`: One influential software-engineering V-model formulation linked specification/design activities to corresponding test levels.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: SOFTWARE_TEST_PAIRING_V_FAMILY
- `CONTRARY_EVIDENCE_OR_LIMIT`: Shared diagram shape does not establish direct ancestry for systems Vee or German V-Modell.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s011"></a>
### S011 — The Relationship of System Engineering to the Project Cycle

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1002/j.2334-5837.1991.tb01484.x
- `AUTHOR_OR_ORGANISATION`: Kevin Forsberg and Harold Mooz
- `DATE_VERSION_EDITION`: 1991
- `SOURCE_CLASS`: PRIMARY_SYSTEMS_ENGINEERING_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Vee model and project-cycle discussion
- `CLAIM_SUPPORTED`: The systems-engineering Vee relates decomposition and definition to integration, verification and validation and presents systems engineering as through-life rather than a terminal phase.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: RELATED_PLAN_DRIVEN_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: A conceptual model, not causal proof of project performance.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s012"></a>
### S012 — Application of the 'Vee' to Incremental and Evolutionary Development

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1002/j.2334-5837.1995.tb01948.x
- `AUTHOR_OR_ORGANISATION`: Kevin Forsberg and Harold Mooz
- `DATE_VERSION_EDITION`: 1995
- `SOURCE_CLASS`: PRIMARY_SYSTEMS_ENGINEERING_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Incremental/evolutionary Vee variants
- `CLAIM_SUPPORTED`: The systems Vee was explicitly applied to incremental and evolutionary development rather than being confined to one pass.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID
- `CONTRARY_EVIDENCE_OR_LIMIT`: Shows conceptual compatibility, not that every Vee implementation is iterative.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s013"></a>
### S013 — V-Modell XT Bund

- `STABLE_URL_OR_LOCATOR`: https://download.gsb.bund.de/BIT/V-Modell_XT_Bund/V-Modell%20XT%20Bund%20HTML/index.html
- `AUTHOR_OR_ORGANISATION`: German Federal Government / V-Modell XT Bund
- `DATE_VERSION_EDITION`: Current web edition accessed 2026-08-11
- `SOURCE_CLASS`: PRIMARY_GOVERNMENT_PROCESS_FRAMEWORK
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Goals, glossary, tailoring, process modules, product states and conformance
- `CLAIM_SUPPORTED`: The German V-Modell is an integrated governance and project framework with modular tailoring, products, roles, decision points and change/problem management—not merely a V-shaped test diagram.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: SEPARATE_V_MODEL_GENEALOGY
- `CONTRARY_EVIDENCE_OR_LIMIT`: Conformance machinery can itself become process ceremony; current XT form does not prove earlier versions were equally flexible.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s014"></a>
### S014 — Software Development and Documentation: Application and Reference Guidebook for MIL-STD-498

- `STABLE_URL_OR_LOCATOR`: https://www.acqnotes.com/Attachments/MIL-STD-498%20%E2%80%9CApplication%20and%20Reference%20Guidebook%E2%80%9D%203%20Jan%201996.pdf
- `AUTHOR_OR_ORGANISATION`: United States Department of Defense
- `DATE_VERSION_EDITION`: 31 January 1996
- `SOURCE_CLASS`: AUTHORITATIVE_GOVERNMENT_GUIDE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Methodology independence, tailoring, information-item treatment and build strategies
- `CLAIM_SUPPORTED`: Engineering information and assurance obligations can be retained while decoupled from a mandatory document form or lifecycle order; grand-design, incremental and evolutionary builds are supported.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_CORRECTION
- `CONTRARY_EVIDENCE_OR_LIMIT`: A guide to applying a standard, not proof that contracting practice shed documentary burden.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s015"></a>
### S015 — Iterative and Incremental Development: A Brief History

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/MC.2003.1204375
- `AUTHOR_OR_ORGANISATION`: Craig Larman and Victor R. Basili
- `DATE_VERSION_EDITION`: 2003
- `SOURCE_CLASS`: SCHOLARLY_HISTORICAL_SYNTHESIS
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Historical cases and Royce discussion
- `CLAIM_SUPPORTED`: Iterative and incremental development existed in major aerospace/software programmes before the later Agile movement and Royce was widely simplified.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HISTORICAL_SYNTHESIS
- `CONTRARY_EVIDENCE_OR_LIMIT`: Secondary historical account, not causal comparison.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s016"></a>
### S016 — The Waterfall Model in Large-Scale Development

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1007/978-3-642-02152-7_29
- `AUTHOR_OR_ORGANISATION`: Kai Petersen, Claes Wohlin and Dejan Baca
- `DATE_VERSION_EDITION`: 2009
- `SOURCE_CLASS`: PEER_REVIEWED_CASE_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Ericsson case results on requirements, testing, versions and communication
- `CLAIM_SUPPORTED`: A real large-scale Waterfall implementation exhibited requirement waste, version confusion, late testing and organisational handoff problems.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EMPIRICAL_CRITICISM_OF_DEPLOYED_PRACTICE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Single telecom case; cannot establish universal effect sizes.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s017"></a>
### S017 — Achieving Effective Acquisition of Information Technology in the Department of Defense

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.17226/12823
- `AUTHOR_OR_ORGANISATION`: National Research Council
- `DATE_VERSION_EDITION`: 2010
- `SOURCE_CLASS`: AUTHORITATIVE_INSTITUTIONAL_REVIEW
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Chapter 3, acquisition cycle, Waterfall assumptions, reviews and end-user feedback
- `CLAIM_SUPPORTED`: Real acquisition structures could preserve long-latency, approval-heavy Waterfall behaviour even when iterative development was nominally allowed.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CRITIQUE_OF_REAL_DEPLOYED_PRACTICE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Focused on DoD IT acquisition of its period, not all plan-driven engineering.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s018"></a>
### S018 — ISO/IEC/IEEE 15288:2023 — Systems and software engineering — System life cycle processes

- `STABLE_URL_OR_LOCATOR`: https://www.iso.org/standard/81702.html
- `AUTHOR_OR_ORGANISATION`: ISO/IEC/IEEE
- `DATE_VERSION_EDITION`: 2023
- `SOURCE_CLASS`: CURRENT_INTERNATIONAL_STANDARD
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Scope, especially clauses describing iterative, concurrent and recursive use and non-prescription of a lifecycle model
- `CLAIM_SUPPORTED`: Modern systems-engineering lifecycle standards define process outcomes across the full lifecycle without prescribing one phase order, method, model or document format.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: RELATED_PLAN_DRIVEN_TRADITION_EVOLVED
- `CONTRARY_EVIDENCE_OR_LIMIT`: Normative framework; implementation quality and economic payoff depend on tailoring.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s019"></a>
### S019 — ISO/IEC/IEEE 12207:2026 — Systems and software engineering — Software life cycle processes

- `STABLE_URL_OR_LOCATOR`: https://www.iso.org/standard/90219.html
- `AUTHOR_OR_ORGANISATION`: ISO/IEC/IEEE
- `DATE_VERSION_EDITION`: Edition 2, 2026
- `SOURCE_CLASS`: CURRENT_INTERNATIONAL_STANDARD
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Scope, clauses 1 and introductory material on concurrent, iterative, recursive and incremental use and applicability to agile
- `CLAIM_SUPPORTED`: Software lifecycle obligations can be applied iteratively and incrementally and do not imply a fixed lifecycle model.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_MODERN_LIFECYCLE
- `CONTRARY_EVIDENCE_OR_LIMIT`: The standard's statement that agile is believed more affordable/faster is contextual language, not an effect-size finding.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s020"></a>
### S020 — IEEE 1012-2024 — Standard for System, Software, and Hardware Verification and Validation

- `STABLE_URL_OR_LOCATOR`: https://standards.ieee.org/ieee/1012/7324/
- `AUTHOR_OR_ORGANISATION`: IEEE Standards Association
- `DATE_VERSION_EDITION`: 2024
- `SOURCE_CLASS`: CURRENT_STANDARD
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Scope and compatibility statement; integrity-level scaling
- `CLAIM_SUPPORTED`: V&V spans lifecycle processes, includes multiple evaluation methods, is compatible with all lifecycle models and scales by integrity.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EVOLVED_VV_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Standardised requirements do not establish comparative benefit in every low-consequence project.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s021"></a>
### S021 — IEEE 828-2012 — Standard for Configuration Management in Systems and Software Engineering

- `STABLE_URL_OR_LOCATOR`: https://standards.ieee.org/ieee/828/5367/
- `AUTHOR_OR_ORGANISATION`: IEEE Standards Association
- `DATE_VERSION_EDITION`: 2012; inactive-reserved 2023
- `SOURCE_CLASS`: STANDARD
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Scope: identification, acquisition, change control, status, builds and releases
- `CLAIM_SUPPORTED`: Configuration management concerns item identity, change, status, build and release engineering, not merely document freezing.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CONFIGURATION_MANAGEMENT_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Inactive-reserved edition and normative rather than empirical evidence.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s022"></a>
### S022 — NASA Systems Engineering Handbook, NASA/SP-2016-6105 Rev. 2

- `STABLE_URL_OR_LOCATOR`: https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf
- `AUTHOR_OR_ORGANISATION`: NASA
- `DATE_VERSION_EDITION`: 2016
- `SOURCE_CLASS`: AUTHORITATIVE_GOVERNMENT_HANDBOOK
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Sections 2.4, 5.3–5.5, 6.2–6.5 and review appendices
- `CLAIM_SUPPORTED`: Recursive/iterative systems engineering, verification/validation distinctions, qualification and acceptance, transition, requirements, interfaces, technical data and configuration management.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: AEROSPACE_SYSTEMS_ENGINEERING
- `CONTRARY_EVIDENCE_OR_LIMIT`: NASA-specific guidance; formality and depth are explicitly to be tailored.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s023"></a>
### S023 — Configuration Management — NASA Systems Engineering Handbook web chapter

- `STABLE_URL_OR_LOCATOR`: https://www.nasa.gov/reference/6-5-configuration-management/
- `AUTHOR_OR_ORGANISATION`: NASA
- `DATE_VERSION_EDITION`: Current web edition accessed 2026-08-11
- `SOURCE_CLASS`: AUTHORITATIVE_GOVERNMENT_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Section 6.5, especially true representation, integrity and unsafe release warning
- `CLAIM_SUPPORTED`: CM provides visibility of the true product representation and integrity by identifying and controlling baseline changes.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CONFIGURATION_MANAGEMENT
- `CONTRARY_EVIDENCE_OR_LIMIT`: Normative rationale; does not quantify net benefit.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s024"></a>
### S024 — Interface Management — NASA Systems Engineering Handbook web chapter

- `STABLE_URL_OR_LOCATOR`: https://www.nasa.gov/reference/6-3-interface-management/
- `AUTHOR_OR_ORGANISATION`: NASA
- `DATE_VERSION_EDITION`: Current web edition accessed 2026-08-11
- `SOURCE_CLASS`: AUTHORITATIVE_GOVERNMENT_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Section 6.3 outputs: interface documents, approvals, assumptions and anomalies
- `CLAIM_SUPPORTED`: Interface definitions, ownership, approved changes and rationale coordinate separately controlled system elements.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: INTERFACE_CONTROL_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Formal unanimous approval is suitable only where both sides truly share interface authority; it can bottleneck local change.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s025"></a>
### S025 — Mars Climate Orbiter Mishap Investigation Board Phase I Report

- `STABLE_URL_OR_LOCATOR`: https://llis.nasa.gov/llis_lib/pdf/1009464main1_0641-mr.pdf
- `AUTHOR_OR_ORGANISATION`: NASA Mars Climate Orbiter Mishap Investigation Board
- `DATE_VERSION_EDITION`: 1999
- `SOURCE_CLASS`: PRIMARY_MISHAP_REPORT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Root-cause and contributing-cause findings concerning English/metric units, navigation software, communication and verification
- `CLAIM_SUPPORTED`: Interface semantics, cross-team communication and system-level verification can fail despite local component work, with mission-level consequences.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_FAILURE_EVIDENCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: One highly specific mishap; does not prove that an ICD or board alone would have prevented it.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s026"></a>
### S026 — FTP 1050 Rev. 3 — Compliance with DO-178C/ED-12C and DO-278A/ED-109A Using Agile Methodology

- `STABLE_URL_OR_LOCATOR`: https://www.rtca.org/wp-content/uploads/2024/06/FTP1050_3-PUBLICATION.pdf
- `AUTHOR_OR_ORGANISATION`: RTCA Forum for Aeronautical Software / EUROCAE
- `DATE_VERSION_EDITION`: Revision 3, 2024
- `SOURCE_CLASS`: PRIMARY_INDUSTRY_INFORMATION_PAPER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: pp. 3–6: lifecycle neutrality, transition criteria, evidence packaging, baselines, change impact and bidirectional traceability
- `CLAIM_SUPPORTED`: High-assurance aerospace objectives can coexist with iterative development; certification credit remains baseline-, evidence-, trace- and independence-sensitive.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_RESOLUTION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Informational/educational paper, expressly not guidance and not the DO-178C standard itself.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s027"></a>
### S027 — Computer Software Assurance for Production and Quality Management System Software

- `STABLE_URL_OR_LOCATOR`: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software
- `AUTHOR_OR_ORGANISATION`: U.S. Food and Drug Administration
- `DATE_VERSION_EDITION`: Final guidance, February 2026
- `SOURCE_CLASS`: CURRENT_REGULATORY_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Risk-based assurance, least-burdensome evidence, testing versus other assurance activities and continuous monitoring
- `CLAIM_SUPPORTED`: Regulated software assurance can be scaled to intended use and risk rather than maximising scripted evidence uniformly.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_SPECIFIC_RISK_PROPORTIONAL_ASSURANCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Applies to production and quality-management-system software, not all medical-device product software.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s028"></a>
### S028 — ISO 26262 — Road vehicles — Functional safety

- `STABLE_URL_OR_LOCATOR`: https://www.iso.org/publication/PUB200262.html
- `AUTHOR_OR_ORGANISATION`: ISO
- `DATE_VERSION_EDITION`: Second edition family, 2018
- `SOURCE_CLASS`: DOMAIN_STANDARD
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Lifecycle parts covering management, concept, system, hardware, software, production/operation/service/decommission and ASIL-oriented analyses
- `CLAIM_SUPPORTED`: Automotive functional-safety controls scale with hazard classification and span lifecycle, configuration, change and evidence.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_SPECIFIC
- `CONTRARY_EVIDENCE_OR_LIMIT`: Automotive electrical/electronic functional safety; not a general software lifecycle prescription.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s029"></a>
### S029 — UN Regulation No. 156 — Software Update and Software Update Management System

- `STABLE_URL_OR_LOCATOR`: https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update
- `AUTHOR_OR_ORGANISATION`: United Nations Economic Commission for Europe
- `DATE_VERSION_EDITION`: In force from 2021; current consolidated text as applicable
- `SOURCE_CLASS`: DOMAIN_REGULATION
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Software update management system, vehicle identification, update integrity and manufacturer obligations
- `CLAIM_SUPPORTED`: Operational software updates can require controlled identity, compatibility, authority and through-life records even when delivered incrementally.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_SPECIFIC_HYBRID
- `CONTRARY_EVIDENCE_OR_LIMIT`: Type-approval regime for vehicles; does not justify equal controls for ordinary reversible software.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s030"></a>
### S030 — Common Safety Method for Risk Evaluation and Assessment

- `STABLE_URL_OR_LOCATOR`: https://www.era.europa.eu/domains/safety-management/common-safety-method-risk-evaluation-and-assessment-csm-ra_en
- `AUTHOR_OR_ORGANISATION`: European Union Agency for Railways
- `DATE_VERSION_EDITION`: Current ERA guidance and Regulation (EU) No 402/2013 as amended
- `SOURCE_CLASS`: DOMAIN_REGULATORY_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Significant-change assessment, hazard record, risk acceptance and independent assessment-body guidance
- `CLAIM_SUPPORTED`: Rail changes are assessed for significance and risk, with independent assessment intensity proportionate to risk and evidence extending beyond paperwork.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_SPECIFIC_RISK_BASED_CHANGE_CONTROL
- `CONTRARY_EVIDENCE_OR_LIMIT`: Rail-specific legal scheme; 'significance' tests and assessment roles are not universal.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s031"></a>
### S031 — 10 CFR 50.59 — Changes, Tests, and Experiments

- `STABLE_URL_OR_LOCATOR`: https://www.nrc.gov/reading-rm/doc-collections/cfr/part050/part050-0059
- `AUTHOR_OR_ORGANISATION`: U.S. Nuclear Regulatory Commission
- `DATE_VERSION_EDITION`: Current regulation accessed 2026-08-11
- `SOURCE_CLASS`: DOMAIN_REGULATION
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Evaluation criteria distinguishing changes allowed without prior approval from those requiring licence amendment
- `CLAIM_SUPPORTED`: Nuclear configuration change control is graded: licensees may make some evaluated changes without prior regulator approval, while threshold-crossing changes require it.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_SPECIFIC_RISK_PROPORTIONAL_CONTROL
- `CONTRARY_EVIDENCE_OR_LIMIT`: A nuclear licensing rule; not evidence that all changes need a standing external board.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s032"></a>
### S032 — DOE O 425.1E — Verification of Readiness to Start Up or Restart Nuclear Facilities

- `STABLE_URL_OR_LOCATOR`: https://www.energy.gov/media/357713
- `AUTHOR_OR_ORGANISATION`: U.S. Department of Energy
- `DATE_VERSION_EDITION`: 2024
- `SOURCE_CLASS`: DOMAIN_GOVERNMENT_ORDER
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Applicability, contractor/DOE readiness reviews, scope and startup/restart approval
- `CLAIM_SUPPORTED`: High-hazard nuclear startup/restart requires evidence that the actual facility, people, procedures and controls are ready before operational authority is granted.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HIGH_CONSEQUENCE_OPERATIONAL_READINESS
- `CONTRARY_EVIDENCE_OR_LIMIT`: High-hazard nuclear facilities only; exact ceremony should not be transplanted.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s033"></a>
### S033 — Manual of Air System Safety Cases (MASSC), Issue 3

- `STABLE_URL_OR_LOCATOR`: https://assets.publishing.service.gov.uk/media/642283502fa848000cec0c63/MASSC_Issue_3.pdf
- `AUTHOR_OR_ORGANISATION`: UK Military Aviation Authority
- `DATE_VERSION_EDITION`: Issue 3, 2023
- `SOURCE_CLASS`: CURRENT_GOVERNMENT_SAFETY_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Chapters 1–3, especially safety-case theory, argument/evidence primacy, through-life use and implementation pathologies
- `CLAIM_SUPPORTED`: A safety case is a living structured argument and evidence, not merely its report; static, compliance-only, self-confirming and late-created cases are recognised failure modes.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: SAFETY_CASE_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Guidance documents benefits and pathologies but does not supply strong comparative outcome estimates.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s034"></a>
### S034 — SP 800-218 — Secure Software Development Framework (SSDF) Version 1.1

- `STABLE_URL_OR_LOCATOR`: https://csrc.nist.gov/pubs/sp/800/218/final
- `AUTHOR_OR_ORGANISATION`: National Institute of Standards and Technology
- `DATE_VERSION_EDITION`: 2022
- `SOURCE_CLASS`: CURRENT_GOVERNMENT_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Framework scope and practice groups
- `CLAIM_SUPPORTED`: Security practices are high-level outcomes designed for integration into any SDLC rather than a separate mandatory phase sequence.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_CONVERGENT_ENGINEERING
- `CONTRARY_EVIDENCE_OR_LIMIT`: Practice framework, not proof that checklist adoption achieves security.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s035"></a>
### S035 — Software Developmental Test and Evaluation in DevSecOps Guidebook

- `STABLE_URL_OR_LOCATOR`: https://www.cto.mil/wp-content/uploads/2025/01/Software_DTE_DEVSECOPS_GB_Jan2025_Signed.pdf
- `AUTHOR_OR_ORGANISATION`: U.S. Department of Defense, OUSD(R&E)
- `DATE_VERSION_EDITION`: January 2025
- `SOURCE_CLASS`: CURRENT_GOVERNMENT_GUIDE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Executive summary; sections 1.1–1.4; continuous T&E, roles, data reuse, independent OT&E
- `CLAIM_SUPPORTED`: Testing can become an early, continuous, automated continuum while preserving decision authority and independent operational evaluation.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_RESOLUTION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Guidance and intended operating model; actual programme adoption and outcome evidence vary.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s036"></a>
### S036 — DevSecOps Continuous Authorization to Operate (cATO) Implementation Guide

- `STABLE_URL_OR_LOCATOR`: https://dodcio.defense.gov/Portals/0/Documents/Library/DoDCIO-ContinuousAuthorizationImplementationGuide.pdf
- `AUTHOR_OR_ORGANISATION`: U.S. Department of Defense Chief Information Officer
- `DATE_VERSION_EDITION`: Current guide accessed 2026-08-11
- `SOURCE_CLASS`: CURRENT_GOVERNMENT_GUIDE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Continuous risk determination, evidence dashboards, risk tolerances, authorising official and residual-risk roles
- `CLAIM_SUPPORTED`: Operational authorisation can consume continuous evidence and monitoring rather than rely only on episodic packages, while retaining explicit risk acceptance authority.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_RESOLUTION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Continuous evidence can continuously reproduce weak controls; authority and measurement quality remain critical.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s037"></a>
### S037 — Systems Engineering Guidebook

- `STABLE_URL_OR_LOCATOR`: https://www.cto.mil/wp-content/uploads/2024/05/SE-Guidebook-Feb2022.pdf
- `AUTHOR_OR_ORGANISATION`: U.S. Department of Defense
- `DATE_VERSION_EDITION`: February 2022
- `SOURCE_CLASS`: CURRENT_GOVERNMENT_GUIDE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Tailoring, technical baselines, event-driven technical reviews, entrance/exit criteria and digital engineering
- `CLAIM_SUPPORTED`: Modern defence systems engineering treats reviews as event/evidence driven and lifecycle processes as tailored rather than fixed calendar phases.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EVOLVED_SYSTEMS_ENGINEERING
- `CONTRARY_EVIDENCE_OR_LIMIT`: Programme implementation may still game milestones or duplicate reviews.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s038"></a>
### S038 — Authoritative Sources of Truth Study (WRT-1051) Final Technical Report

- `STABLE_URL_OR_LOCATOR`: https://sercuarc.org/wp-content/uploads/2023/12/SERC-WRT-1051-Final-Technical-Report.pdf
- `AUTHOR_OR_ORGANISATION`: Systems Engineering Research Center
- `DATE_VERSION_EDITION`: 2023
- `SOURCE_CLASS`: GOVERNMENT_SPONSORED_RESEARCH_REPORT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Findings on 'authoritative source of truth' ambiguity, interoperability, governance, workflows and culture
- `CLAIM_SUPPORTED`: Digital-authority initiatives can fail through ambiguous authority, tool interoperability, semantics, access and governance rather than document format alone.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CRITICAL_DIGITAL_ENGINEERING_EVIDENCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Exploratory research and practice synthesis rather than controlled outcome evaluation.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s039"></a>
### S039 — Value and Benefits of Model-Based Systems Engineering (MBSE): Evidence from the Literature

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1002/sys.21566
- `AUTHOR_OR_ORGANISATION`: Kaitlin Henderson and Alejandro Salado
- `DATE_VERSION_EDITION`: 2021
- `SOURCE_CLASS`: PEER_REVIEWED_SYSTEMATIC_REVIEW
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Results and evidence-classification sections, Systems Engineering 24(1), pp. 51–66
- `CLAIM_SUPPORTED`: Many claimed MBSE benefits are perceived or expected rather than measured; measured comparative evidence is sparse.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CRITICAL_EVIDENCE_ON_DIGITAL_ENGINEERING
- `CONTRARY_EVIDENCE_OR_LIMIT`: Publication evidence may omit internal programme metrics and newer implementations.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s040"></a>
### S040 — Systematic Literature Review: How Is Model-Based Systems Engineering Justified?

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.2172/1561164
- `AUTHOR_OR_ORGANISATION`: Edward R. Carroll and Robert J. Malins
- `DATE_VERSION_EDITION`: 2016
- `SOURCE_CLASS`: GOVERNMENT_LAB_SYSTEMATIC_REVIEW
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Case-study coding and evidence tables
- `CLAIM_SUPPORTED`: MBSE case literature reports many benefits, but metric quality and case comparability are heterogeneous.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: MIXED_EVIDENCE_ON_DIGITAL_ENGINEERING
- `CONTRARY_EVIDENCE_OR_LIMIT`: Review included practitioner cases of variable rigour and predates current toolchains.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s041"></a>
### S041 — Assessing the Effect of Requirements Traceability for Software Maintenance

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/ICSM.2012.6405269
- `AUTHOR_OR_ORGANISATION`: Patrick Mäder and Alexander Egyed
- `DATE_VERSION_EDITION`: 2012
- `SOURCE_CLASS`: CONTROLLED_EXPERIMENT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Method and results: 52 participants, 315 maintenance tasks
- `CLAIM_SUPPORTED`: Under experimentally supplied, correct and complete links, traceability improved task speed and correctness.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EMPIRICAL_SUPPORT_FOR_TRACEABILITY
- `CONTRARY_EVIDENCE_OR_LIMIT`: Mostly students, unfamiliar systems, ideal traces and no full measurement of trace-creation/maintenance cost.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s042"></a>
### S042 — Do Developers Benefit from Requirements Traceability When Evolving and Maintaining a Software System?

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1007/s10664-014-9314-z
- `AUTHOR_OR_ORGANISATION`: Patrick Mäder and Alexander Egyed
- `DATE_VERSION_EDITION`: 2015
- `SOURCE_CLASS`: CONTROLLED_EXPERIMENT_REPLICATION
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Empirical Software Engineering 20, experimental results
- `CLAIM_SUPPORTED`: Replication found participants with traceability approximately 24% faster and solutions approximately 50% more correct.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EMPIRICAL_SUPPORT_FOR_TRACEABILITY
- `CONTRARY_EVIDENCE_OR_LIMIT`: Task-level laboratory evidence; link quality and lifecycle maintenance costs remain external.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s043"></a>
### S043 — Preventing Defects: The Impact of Requirements Traceability Completeness on Software Quality

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/TSE.2016.2622264
- `AUTHOR_OR_ORGANISATION`: Patrick Rempel and Patrick Mäder
- `DATE_VERSION_EDITION`: 2017
- `SOURCE_CLASS`: PEER_REVIEWED_OBSERVATIONAL_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: 24 open-source projects, 610 components; trace-completeness/defect analyses
- `CLAIM_SUPPORTED`: Completeness for several development activities was statistically associated with lower defect rates.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EMPIRICAL_SUPPORT_FOR_TRACEABILITY
- `CONTRARY_EVIDENCE_OR_LIMIT`: Observational association, project selection and confounding prevent a simple causal claim.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s044"></a>
### S044 — The Impact of Traceability on Software Maintenance and Evolution: A Mapping Study

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1002/smr.2374
- `AUTHOR_OR_ORGANISATION`: Fangchao Tian, Tianlu Wang, Peng Liang, Chong Wang, Arif Ali Khan and Muhammad Ali Babar
- `DATE_VERSION_EDITION`: 2021
- `SOURCE_CLASS`: SYSTEMATIC_MAPPING_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Synthesis of 63 studies published 2000–2020
- `CLAIM_SUPPORTED`: Change management is the most common benefit; establishing and maintaining links is the principal cost; strong industrial evidence remains needed.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: MIXED_TRACEABILITY_EVIDENCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Maps heterogeneous studies and does not yield universal cost-benefit thresholds.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s045"></a>
### S045 — Software Verification and Validation: Its Role in Computer Assurance and Its Relationship with Software Project Management Standards

- `STABLE_URL_OR_LOCATOR`: https://www.govinfo.gov/content/pkg/GOVPUB-C13-eb032eca81be246ff48b064f71b62618/pdf/GOVPUB-C13-eb032eca81be246ff48b064f71b62618.pdf
- `AUTHOR_OR_ORGANISATION`: Dolores R. Wallace and Roger U. Fujii, NIST
- `DATE_VERSION_EDITION`: NIST SP 500-165, 1989
- `SOURCE_CLASS`: GOVERNMENT_TECHNICAL_REPORT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Recommended V&V tasks and comparative-study discussion, especially pp. 7 and 16
- `CLAIM_SUPPORTED`: V&V should start early and focus on critical areas; comparative case results show both possible savings and substantial cost/coordination burdens.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: MIXED_EMPIRICAL_IVV_EVIDENCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Older projects, non-equivalent comparisons and substantial methodological uncertainty.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s046"></a>
### S046 — An Assessment of Space Shuttle Flight Software Development Processes

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.17226/2222
- `AUTHOR_OR_ORGANISATION`: National Research Council
- `DATE_VERSION_EDITION`: 1993
- `SOURCE_CLASS`: AUTHORITATIVE_INDEPENDENT_REVIEW
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Chapter 2, IV&V objectives, scope and independence
- `CLAIM_SUPPORTED`: IV&V scope should scale to criticality and latent-error consequence; technical, managerial and financial independence trade against timeliness and access.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: IVV_CONDITIONS_AND_CRITIQUE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Committee judgement and testimony, not a clean causal estimate.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s047"></a>
### S047 — Error Cost Escalation Through the Project Life Cycle

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1002/j.2334-5837.2004.tb00608.x
- `AUTHOR_OR_ORGANISATION`: Bill Haskins, Jonette Stecklein, Brandon Dick, Gregory Moroney, Randy Lovell and James Dabney
- `DATE_VERSION_EDITION`: 2004
- `SOURCE_CLASS`: DOMAIN_EMPIRICAL_AND_MODELLED_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Three methods and correction-cost multipliers for aerospace-like systems
- `CLAIM_SUPPORTED`: Correction costs can rise steeply where hardware/software system commitments, rework and verification accumulate.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: SUPPORT_FOR_COMMITMENT_COST_HYPOTHESIS
- `CONTRARY_EVIDENCE_OR_LIMIT`: Multipliers vary enormously by method and domain and are not a universal software law.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s048"></a>
### S048 — Are Delayed Issues Harder to Resolve? Revisiting Cost-to-Fix of Defects throughout the Lifecycle

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1007/s10664-016-9469-x
- `AUTHOR_OR_ORGANISATION`: Tim Menzies, William Nichols, Forrest Shull and Lucas Layman
- `DATE_VERSION_EDITION`: 2017
- `SOURCE_CLASS`: MULTI_PROJECT_EMPIRICAL_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: 171 software projects, delay/cost analyses and conclusions
- `CLAIM_SUPPORTED`: No consistent, substantial global delayed-issue effect was found; late discovery is not automatically exponentially expensive.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: COUNTEREVIDENCE_TO_UNIVERSAL_COST_OF_CHANGE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Issue-tracker measures do not capture every physical, certification, contractual or operational consequence.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s049"></a>
### S049 — What's Next? After Stage-Gate

- `STABLE_URL_OR_LOCATOR`: https://media.transformanceadvisors.com/pdfs/After-Stage-Gate.pdf
- `AUTHOR_OR_ORGANISATION`: Robert G. Cooper
- `DATE_VERSION_EDITION`: 2014
- `SOURCE_CLASS`: PRIMARY_METHOD_EVOLUTION_ARTICLE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Critique of traditional linear/bureaucratic Stage-Gate and next-generation overlapping, adaptive, risk-based forms
- `CLAIM_SUPPORTED`: Even the Stage-Gate tradition recognised bureaucratic linearity and evolved toward context-specific, overlapping, build-test-feedback operation.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EVOLUTION_UNDER_CRITICISM
- `CONTRARY_EVIDENCE_OR_LIMIT`: Written by the method's principal advocate; outcome evidence is not independently established by the article.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s050"></a>
### S050 — Why Software Projects Escalate: An Empirical Analysis and Test of Four Theoretical Models

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.2307/3250950
- `AUTHOR_OR_ORGANISATION`: Mark Keil, Joan Mann and Arun Rai
- `DATE_VERSION_EDITION`: 2000
- `SOURCE_CLASS`: PEER_REVIEWED_EMPIRICAL_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: MIS Quarterly 24(4), escalation-model tests
- `CLAIM_SUPPORTED`: Sunk cost, project factors and psychological/social dynamics can sustain failing software projects.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CRITIQUE_OF_GATE_AND_PREDICTIVE_GOVERNANCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Does not show that all formal reviews increase escalation; effective stop authority may reduce it.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s051"></a>
### S051 — A Systematic Review of Software Development Cost Estimation Studies

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/TSE.2007.256943
- `AUTHOR_OR_ORGANISATION`: Magne Jørgensen and Martin Shepperd
- `DATE_VERSION_EDITION`: 2007
- `SOURCE_CLASS`: SYSTEMATIC_LITERATURE_REVIEW
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Review of 304 estimation papers
- `CLAIM_SUPPORTED`: Software-estimation research is fragmented and context-dependent; no single predictive technique warrants universal confidence.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: CRITIQUE_OF_FALSE_PREDICTIVE_CERTAINTY
- `CONTRARY_EVIDENCE_OR_LIMIT`: Literature through 2004; does not imply that forecasting is useless.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s052"></a>
### S052 — Evidence-Based Guidelines for Assessment of Software Development Cost Uncertainty

- `STABLE_URL_OR_LOCATOR`: https://web-backend.simula.no/sites/default/files/publications/Jorgensen.2005.5.pdf
- `AUTHOR_OR_ORGANISATION`: Magne Jørgensen
- `DATE_VERSION_EDITION`: 2005
- `SOURCE_CLASS`: PEER_REVIEWED_SYNTHESIS
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Guidelines and empirical basis for overconfidence, outside views, multiple sources and feedback
- `CLAIM_SUPPORTED`: Point estimates and narrow intervals are often overconfident; structured uncertainty, independent views and feedback improve decision quality.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EVOLVED_PREDICTIVE_PLANNING
- `CONTRARY_EVIDENCE_OR_LIMIT`: Guidelines improve epistemic discipline but do not eliminate political or irreducible uncertainty.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s053"></a>
### S053 — GAO Cost Estimating and Assessment Guide: Best Practices for Developing and Managing Program Costs

- `STABLE_URL_OR_LOCATOR`: https://www.gao.gov/products/gao-20-195g
- `AUTHOR_OR_ORGANISATION`: U.S. Government Accountability Office
- `DATE_VERSION_EDITION`: GAO-20-195G, 2020
- `SOURCE_CLASS`: AUTHORITATIVE_GOVERNMENT_GUIDE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Risk/sensitivity analysis, assumptions, independent estimate and update-with-actuals practices
- `CLAIM_SUPPORTED`: Mature predictive planning uses explicit assumptions, uncertainty, risk, independent challenge and actuals rather than treating one baseline estimate as truth.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EVOLVED_PREDICTIVE_PLANNING
- `CONTRARY_EVIDENCE_OR_LIMIT`: Best-practice guidance; compliance with the guide does not assure forecast accuracy.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s054"></a>
### S054 — Continuous Integration, Delivery and Deployment: A Systematic Review on Approaches, Tools, Challenges and Practices

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1109/ACCESS.2017.2685629
- `AUTHOR_OR_ORGANISATION`: Mojtaba Shahin, Muhammad Ali Babar and Liming Zhu
- `DATE_VERSION_EDITION`: 2017
- `SOURCE_CLASS`: SYSTEMATIC_LITERATURE_REVIEW
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Synthesis of 69 studies
- `CLAIM_SUPPORTED`: CI/CD provides rapid integration and feedback but depends on automation, test quality, architecture, environments and organisational capability.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: ADAPTIVE_IMPORT_AND_HYBRID
- `CONTRARY_EVIDENCE_OR_LIMIT`: Heterogeneous evidence and publication bias; continuous delivery does not itself establish assurance.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s055"></a>
### S055 — Continuous Integration and Delivery: A Systematic Review

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1016/j.jss.2021.111113
- `AUTHOR_OR_ORGANISATION`: Eliezio Soares and colleagues
- `DATE_VERSION_EDITION`: 2021
- `SOURCE_CLASS`: SYSTEMATIC_REVIEW_OF_EMPIRICAL_STUDIES
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Review of empirical CI/CD studies, benefits and challenges
- `CLAIM_SUPPORTED`: CI/CD can improve feedback and release performance, but infrastructure, flaky tests, integration complexity and adoption costs are recurrent constraints.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: HYBRID_EMPIRICAL_EVIDENCE
- `CONTRARY_EVIDENCE_OR_LIMIT`: Effects depend on context and measurement; not a safety-certification study.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s056"></a>
### S056 — SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems

- `STABLE_URL_OR_LOCATOR`: https://csrc.nist.gov/pubs/sp/800/34/r1/final
- `AUTHOR_OR_ORGANISATION`: National Institute of Standards and Technology
- `DATE_VERSION_EDITION`: 2010
- `SOURCE_CLASS`: GOVERNMENT_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Business impact analysis, recovery strategies, plans, testing and maintenance
- `CLAIM_SUPPORTED`: Recovery and contingency are engineering capabilities that require preconditions and exercises, not merely an emergency document.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: OPERATIONAL_RESILIENCE_TRADITION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Federal information-system focus and older edition.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s057"></a>
### S057 — Operational Readiness Review — Systems Engineering Handbook Appendix

- `STABLE_URL_OR_LOCATOR`: https://www.nasa.gov/reference/system-engineering-handbook-appendix/
- `AUTHOR_OR_ORGANISATION`: NASA
- `DATE_VERSION_EDITION`: Current web edition accessed 2026-08-11
- `SOURCE_CLASS`: AUTHORITATIVE_GOVERNMENT_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Operational Readiness Review definition and success criteria
- `CLAIM_SUPPORTED`: Readiness concerns the actual deployed hardware, software, people, procedures, support and user documentation—not document approval alone.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: OPERATIONAL_READINESS
- `CONTRARY_EVIDENCE_OR_LIMIT`: NASA review form is not universally required; the underlying actual-state readiness property is.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s058"></a>
### S058 — Weapon System Sustainment: DOD's Sustainment Reviews and Cost-Growth Information

- `STABLE_URL_OR_LOCATOR`: https://files.gao.gov/reports/GAO-26-108140/index.html
- `AUTHOR_OR_ORGANISATION`: U.S. Government Accountability Office
- `DATE_VERSION_EDITION`: GAO-26-108140, 2026
- `SOURCE_CLASS`: CURRENT_GOVERNMENT_AUDIT
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Findings on sustainment baselines, cost-growth determination and causes
- `CLAIM_SUPPORTED`: Absent or weak sustainment baselines can prevent authorities from determining growth and acting on obsolescence, supply and support problems.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EMPIRICAL_INSTITUTIONAL_EVIDENCE_FOR_SUSTAINMENT_BASELINES
- `CONTRARY_EVIDENCE_OR_LIMIT`: Defence weapon-system setting; baseline reporting can itself be gamed or burdensome.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s059"></a>
### S059 — Managing Change in the Delivery of Complex Projects: Configuration Management, Asset Information and 'Big Data'

- `STABLE_URL_OR_LOCATOR`: https://doi.org/10.1016/j.ijproman.2015.02.006
- `AUTHOR_OR_ORGANISATION`: Jennifer Whyte, Anna Stasis and Carmel Lindkvist
- `DATE_VERSION_EDITION`: 2016
- `SOURCE_CLASS`: PEER_REVIEWED_CROSS_CASE_STUDY
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Cross-case analysis involving complex aerospace/infrastructure organisations
- `CLAIM_SUPPORTED`: Digital asset information becomes a contractual/operational deliverable and configuration/change practices coordinate complex project state.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: EMPIRICAL_SUPPORT_FOR_CONFIGURATION_INFORMATION
- `CONTRARY_EVIDENCE_OR_LIMIT`: Qualitative cross-case research; does not quantify causal return.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s060"></a>
### S060 — Weapon Systems Annual Assessment and Knowledge-Based Acquisition Series

- `STABLE_URL_OR_LOCATOR`: https://www.gao.gov/products/gao-25-107569
- `AUTHOR_OR_ORGANISATION`: U.S. Government Accountability Office
- `DATE_VERSION_EDITION`: Representative current report GAO-25-107569, 2025
- `SOURCE_CLASS`: RECURRING_GOVERNMENT_AUDIT_SERIES
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Knowledge at programme start, design maturity, production and testing findings
- `CLAIM_SUPPORTED`: Large physical programmes incur risk when technology, design, supplier and production commitments outrun demonstrated knowledge.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_EVIDENCE_FOR_STAGED_COMMITMENT
- `CONTRARY_EVIDENCE_OR_LIMIT`: Association in defence acquisitions; stage labels and reviews alone do not create knowledge.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s061"></a>
### S061 — Quality Management System Regulation (QMSR)

- `STABLE_URL_OR_LOCATOR`: https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr
- `AUTHOR_OR_ORGANISATION`: U.S. Food and Drug Administration
- `DATE_VERSION_EDITION`: Effective 2 February 2026
- `SOURCE_CLASS`: CURRENT_REGULATORY_FRAMEWORK
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Effective-date, ISO 13485 incorporation, lifecycle/design controls and risk-management discussion
- `CLAIM_SUPPORTED`: Medical-device quality controls are through-life and risk-based within a regulatory authority framework.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: DOMAIN_SPECIFIC
- `CONTRARY_EVIDENCE_OR_LIMIT`: Regulatory applicability is limited to covered device manufacturers and products.
- `ACCESS_DATE`: 2026-08-11

<a id="source-s062"></a>
### S062 — Independent Verification and Validation (IV&V) Overview

- `STABLE_URL_OR_LOCATOR`: https://www.nasa.gov/ivv-overview/
- `AUTHOR_OR_ORGANISATION`: NASA
- `DATE_VERSION_EDITION`: Current web edition accessed 2026-08-11
- `SOURCE_CLASS`: AUTHORITATIVE_PROGRAMME_GUIDANCE
- `EXACT_SECTION_PAGE_OR_LOCATOR`: Technical, managerial and financial independence dimensions
- `CLAIM_SUPPORTED`: Independence is multidimensional and cannot be inferred from a different reviewer name alone.
- `RELATION_TO_PROPERTY_OR_GENEALOGY`: IVV_INDEPENDENCE_CONDITIONS
- `CONTRARY_EVIDENCE_OR_LIMIT`: Programme rationale, not comparative economics.
- `ACCESS_DATE`: 2026-08-11

# EVOLVED_WATERFALL_TIMELINE

| DATE | EVENT | CLASSIFICATION |
| --- | --- | --- |
| 1956 / 1983 publication | Benington's SAGE account combines staged production, interface discipline, independent testing and records; the 1983 foreword reports an experimental prototype and criticises specification before detailed knowledge. | RELATED_PLAN_DRIVEN_TRADITION |
| 1968 | NATO conference records simulation, feedback, limited initial systems, user interaction and objective acceptance as active software-engineering concerns. | CONVERGENT_ENGINEERING |
| 1970 | Royce presents the staged sequence, calls the unmodified version risky, and adds preliminary design, a pilot, early test planning, documentation and customer control. | DIRECT_LINEAGE |
| 1976 | Bell and Thayer attach 'waterfall' terminology to Royce's sequence while documenting continuing requirements problems. | DIRECT_LINEAGE_NAMING_HINGE |
| 1979 | Boehm's software V-chart pairs requirements/design baselines with verification and validation activities and includes iterative problem feedback. | SOFTWARE_V_FAMILY |
| 1986 | Parnas and Clements reject a perfectly rational top-down chronology but defend coherent current design records; Rook publishes an influential software V-model; Germany's V-Modell lineage begins separately. | REACTION_PLUS_MULTIPLE_V_LINEAGES |
| 1988 | Boehm's spiral makes risk drive lifecycle activity; DOD-STD-2167A formalises reviews/baselines while nominally allowing tailoring, prototyping and iteration. | REACTION_AND_REAL_DEPLOYED_PRACTICE |
| 1991–1995 | Forsberg and Mooz develop the systems-engineering Vee and then explicitly apply it to incremental and evolutionary development. | RELATED_PLAN_DRIVEN_TRADITION_HYBRIDISED |
| 1996 | MIL-STD-498 application guidance separates engineering information from fixed document forms and supports grand-design, incremental and evolutionary builds. | HYBRID_CORRECTION |
| 2000s | Escalation/estimation research challenges false certainty; historical and case research shows both longstanding iteration and real large-scale Waterfall failures. | CRITICISM_AND_EMPIRICAL_EPOCH |
| 2010s | Modern lifecycle and safety practice increasingly treats processes as tailored obligations, while CI/CD, MBSE and digital engineering alter evidence cadence and representation. | HYBRID_AND_CONVERGENT_ENGINEERING |
| 2022–2024 | DoD, ISO/IEC/IEEE, IEEE 1012 and RTCA sources emphasise event-driven reviews, iterative/concurrent lifecycle use, integrity-scaled V&V and lifecycle-neutral aerospace assurance objectives. | MODERN_EVOLVED_ASSURANCE |
| 2025–2026 | DoD DevSecOps guidance, ISO 12207:2026, FDA risk-based software assurance and cATO show continuous/iterative evidence integrated with baselines, independent evaluation and explicit authority. | CONTINUOUS_ASSURANCE_HYBRID |

The source mappings for every row are in the YAML ledger; the principal genealogy sources are S001–S019.

# EVOLVED_WATERFALL_GENEALOGY

| NODE | PARENTS | DESCENDANTS | CLASSIFICATION | CORE |
| --- | --- | --- | --- | --- |
| G1 Early large-system engineering |  | G2; G5 | RELATED_PLAN_DRIVEN_TRADITION | Specifications, interfaces, technical authority, configuration records, staged testing, prototypes and system evaluation coexist. |
| G2 Royce risk-mitigated staged development | G1 | G3; G4 | DIRECT_LINEAGE | Staging plus feedback, pilot development, preliminary architecture, test planning, documentation and customer control. |
| G3 Waterfall naming and pedagogical simplification | G2 | G4 | DIRECT_LINEAGE_THEN_CARICATURE | Bell–Thayer naming foregrounds the phase sequence; later diagrams and teaching frequently abstract away Royce's corrections. |
| G4 Contractual/institutional sequentiality | G2; G3; G1 | G6; G7 | REAL_DEPLOYED_PRACTICE | Reviews, data deliveries, funding, approvals and organisational handoffs turn logical dependencies into long feedback cycles. |
| G5 Software V/V-chart family | G1 | G8 | RELATED_PLAN_DRIVEN_TRADITION | Definition products are paired with evaluation levels; early forms include feedback and baseline correction. |
| G6 Systems-engineering Vee family | G1 | G8 | RELATED_PLAN_DRIVEN_TRADITION | Decomposition and definition are related to integration, verification and validation through the system hierarchy; later explicitly incremental. |
| G7 German V-Modell family | G4 | G8 | SEPARATE_GOVERNANCE_GENEALOGY | A modular/tailorable government process framework of products, roles, decision points and conformance—not merely a test V. |
| G8 Iterative/risk-driven correction | G4; G5; G6 | G9; G10 | REACTION_TO_WATERFALL_AND_HYBRID | Spiral, incremental Vee, evolutionary acquisition and methodology-neutral standards retain assurance obligations while changing ordering and cadence. |
| G9 Domain assurance traditions | G1; G5; G6; G8 | G10 | DOMAIN_SPECIFIC_AND_CONVERGENT | Aerospace, medical, automotive, rail and nuclear regimes scale qualification, independence, change, safety and authority to domain consequences. |
| G10 Digital/DevSecOps continuous assurance | G8; G9 |  | HYBRID | Automated, configuration-linked continuous evidence and monitoring coexist with release identity, independent evaluation and external/operational authority. |

The V-shaped traditions are explicitly non-identical: Boehm/Rook’s software V/V relation, Forsberg–Mooz’s systems-engineering Vee and Germany’s V-Modell/V-Modell XT are separate decision-relevant families. A common diagram does not establish a common method.

# WATERFALL_CARICATURE_VS_HISTORY

| CLAIM | HISTORY | CATEGORY |
| --- | --- | --- |
| Royce prescribed a single pass with no iteration. | False. The bare sequence is explicitly diagnosed as risky; Royce adds feedback, pilot development, preliminary design, early testing and customer involvement. | LATER_TEXTBOOK_CARICATURE |
| All later Waterfall criticism is therefore a straw man. | False. Real contracts, milestones, handoffs and review structures created long-latency sequential practice even where standards allowed iteration. | CRITIQUE_OF_REAL_DEPLOYED_PRACTICE |
| Iteration appeared only as a later Agile correction. | False. Prototypes, simulation, limited releases and iterative/incremental programmes pre-date Royce and Agile. | HISTORICAL_SOURCE |
| The V-model is one direct Waterfall descendant. | False as a general claim. Software V/V charts, the systems Vee and German V-Modell are distinct families with different purposes and partially separate genealogies. | GENEALOGICAL_CORRECTION |
| V-shaped models necessarily defer testing until the right side. | Misleading. Their useful idea is early pairing of claims with evaluation; mature forms can integrate and evaluate incrementally. | CRITIQUE_OF_CARICATURE |
| Plan-driven engineering requires a fixed phase order. | False in current lifecycle standards. ISO 15288 and 12207 explicitly allow concurrent, iterative, recursive and incremental application and prescribe no lifecycle model. | LATER_DESCENDANT |
| Documentation, traceability, baselines and review are either all Waterfall or all bureaucracy. | False dichotomy. Their underlying properties can be valuable, while fixed document/meeting/manual forms can be ceremony. | PROPERTY_VS_ARTEFACT |
| High-assurance standards require Waterfall. | Overgeneralised. RTCA's DO-178C informational paper says no lifecycle method is mandated, but certification objectives still require baseline-specific evidence, change impact and traceability. | HYBRID_RESOLUTION |
| Late changes are universally exponentially expensive. | False. Aerospace-like systems show large but variable escalation; a 171-project software study found no consistent substantial global delay effect. | REJECTED_GENERALISATION |
| Digital engineering removes documentation and authority problems. | False. It changes representation; model authority, validation, interoperability, access, staleness and as-deployed reconciliation remain. | MODERN_CARICATURE |

Final historical disposition: the one-pass textbook Waterfall is an inaccurate account of Royce’s complete proposal, but rigid sequentiality was a real organisational and acquisition failure mode. Criticism of the caricature and criticism of deployed plan-driven properties must therefore remain separate.

# EVOLVED_WATERFALL_PROPERTY_LEDGER

This is the frozen 38-candidate denominator. Every entry contains the extraction contract requested for later independent audit. Additional lineage, adaptive-relation and reversibility fields are included but do not alter the denominator.

<a id="property-ew-p001"></a>
### EW-P001 — Authoritative, revisable intent and requirements state

- `PROPERTY_ID`: EW-P001
- `PROPERTY_NAME`: Authoritative, revisable intent and requirements state
- `HISTORICAL_ORIGIN`: Early large-system specifications; Royce; defence/aerospace requirements management; modern ISO/NASA lifecycle processes.
- `ORIGINAL_FORM`: Approved requirements specifications and controlled revisions, often document-centred.
- `PROBLEM_IT_ADDRESSED`: Multiple groups need to know what behaviour, constraints and obligations currently govern.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Conflicting interpretations, invisible requirement drift, implementation against obsolete intent, or unowned requirements.
- `MECHANISM`: Identify the current authoritative requirement state, its version, owners, rationale, assumptions, status and approved changes; preserve history without treating the baseline as immutable truth.
- `TRIGGER_OR_CONTEXT`: Shared or externally committed intent; multiple teams or suppliers; long-lived product; acceptance, safety or regulatory obligations; non-local change impact.
- `NON_TRIGGER_OR_CHEAP_PATH`: For a single team exploring a local reversible feature, a lightweight backlog item, executable example and version history may be enough; do not baseline speculative detail merely to appear complete.
- `DEPENDENCIES_OR_PRECONDITIONS`: Named authority; accessible current representation; change path; stakeholder participation; ability to mark uncertainty and supersession; configuration linkage.
- `EXPECTED_ENGINEERING_PAYOFF`: Fewer version disputes, clearer design/test basis, visible scope change and more reliable impact analysis.
- `KNOWN_FAILURE_MODES`: Baselining wrong or premature requirements; stale authorised documents; shadow requirements in chat or tickets; authority so centralised that learning stalls.
- `IMPORTANT_CRITICISMS`: Requirements cannot be fully known up front; a stable baseline can preserve error and create political resistance to change.
- `HOW_THE_PROPERTY_EVOLVED`: From presumed-complete giant specifications to incremental, revisable, uncertainty-aware requirement authority linked to evidence and releases.
- `MATURE_OR_EVOLVED_FORM`: A living authoritative requirement state that distinguishes proposed, approved, implemented, verified and retired obligations and allows risk-proportional change.
- `CEREMONY_VS_PROPERTY`: The property is authority and state identity; a single giant requirements document, fixed template or requirements-complete gate is not required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: B_STRONG_PRIMARY_AND_DOMAIN_SUPPORT
- `PRIMARY_SOURCES`: [S001](#source-s001), [S003](#source-s003), [S004](#source-s004), [S018](#source-s018), [S019](#source-s019), [S022](#source-s022)
- `CRITICAL_SOURCES`: [S006](#source-s006), [S007](#source-s007), [S016](#source-s016), [S017](#source-s017)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Bell–Thayer and the Ericsson case show requirements defects and version confusion; aerospace and regulated regimes retain identified requirement states but permit iteration.
- `OPEN_QUESTIONS`: How much structure pays off at each scale? When should an exploratory statement acquire authoritative status?
- `REVERSIBILITY_PROFILE`: R1–R4: value rises with shared scope, external commitment, coupling and evidence obligations; R0 generally needs only lightweight versioned intent.
- `LINEAGE_CLASSIFICATION`: DIRECT_LINEAGE; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p002"></a>
### EW-P002 — Explicit requirements uncertainty, assumptions and learning obligations

- `PROPERTY_ID`: EW-P002
- `PROPERTY_NAME`: Explicit requirements uncertainty, assumptions and learning obligations
- `HISTORICAL_ORIGIN`: NATO-era simulation/prototyping; Bell–Thayer defect evidence; Parnas/Clements; spiral risk management.
- `ORIGINAL_FORM`: Uncertainty was often hidden inside provisional specifications or handled through informal redesign.
- `PROBLEM_IT_ADDRESSED`: Teams must distinguish known obligations from hypotheses, assumptions, unresolved choices and environmental uncertainty.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: False completeness, premature contractual/design commitment, unplanned rework and validation against assumptions nobody remembers.
- `MECHANISM`: Record uncertainty, confidence, assumptions, decision deadlines, owners and planned evidence-generating activities; promote items to baseline only when warranted.
- `TRIGGER_OR_CONTEXT`: Novel problem, volatile environment, ambiguous user need, uncertain technology, emergent operations or weak observability.
- `NON_TRIGGER_OR_CHEAP_PATH`: Routine replacement with stable, externally specified behaviour can use a short assumption list and normal change handling.
- `DEPENDENCIES_OR_PRECONDITIONS`: Psychological safety to admit uncertainty; decision owners; access to prototypes/users/data; expiry and review mechanisms.
- `EXPECTED_ENGINEERING_PAYOFF`: Better experiment selection, preserved options, less false precision and earlier discovery of invalid premises.
- `KNOWN_FAILURE_MODES`: An uncertainty register that never changes decisions; endless analysis; treating every requirement as tentative; unowned assumptions.
- `IMPORTANT_CRITICISMS`: Can become administrative risk-register theatre or an excuse to avoid commitment.
- `HOW_THE_PROPERTY_EVOLVED`: From pretending specification completion to making uncertainty an explicit governed engineering object tied to evidence and decisions.
- `MATURE_OR_EVOLVED_FORM`: An assumption/uncertainty ledger integrated with requirements, architecture, hazards and experiments, with expiry and promotion/retirement rules.
- `CEREMONY_VS_PROPERTY`: The property is explicit epistemic status and planned learning; a standing risk meeting or large spreadsheet is optional.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_HISTORICAL_AND_MECHANISTIC_SUPPORT
- `PRIMARY_SOURCES`: [S002](#source-s002), [S004](#source-s004), [S006](#source-s006), [S008](#source-s008)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S050](#source-s050)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Historical and case evidence repeatedly shows requirements continue to change; spiral and modern iterative standards operationalise risk-driven learning.
- `OPEN_QUESTIONS`: Empirical thresholds for the optimal amount of uncertainty bookkeeping remain weak.
- `REVERSIBILITY_PROFILE`: R0–R3: most valuable before hard commitment; should shrink or change form as evidence and external obligations accumulate.
- `LINEAGE_CLASSIFICATION`: REACTION_TO_WATERFALL; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: ADAPTIVE_IMPORT

<a id="property-ew-p003"></a>
### EW-P003 — Early architecture and feasibility before hard commitment

- `PROPERTY_ID`: EW-P003
- `PROPERTY_NAME`: Early architecture and feasibility before hard commitment
- `HISTORICAL_ORIGIN`: Royce preliminary programme design; SAGE interface discipline; systems Vee and knowledge-based acquisition.
- `ORIGINAL_FORM`: Preliminary and critical design work before full implementation or production commitment.
- `PROBLEM_IT_ADDRESSED`: Some cross-cutting constraints—timing, mass, power, safety, data, interfaces, manufacturability—cannot be resolved by local implementation alone.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Committing requirements, suppliers, tooling or production before the system concept can satisfy dominant constraints.
- `MECHANISM`: Perform enough cross-disciplinary architecture, trade study, modelling and interface analysis to falsify high-cost assumptions and expose system budgets.
- `TRIGGER_OR_CONTEXT`: High coupling; hardware/physical constraints; scarce test facilities; safety; long lead items; multiple suppliers; expensive migration or platform commitment.
- `NON_TRIGGER_OR_CHEAP_PATH`: Local, modular, quickly deployable software can use a thin architecture sketch, automated fitness functions and evolutionary design.
- `DEPENDENCIES_OR_PRECONDITIONS`: Representative constraints/data; accountable system architect or integrator; willingness to change requirements; prototypes/models validated for the question asked.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier discovery of infeasible combinations, protected interfaces and reduced commitment-unwind cost.
- `KNOWN_FAILURE_MODES`: Big Design Up Front; architecture prestige without executable evidence; premature standardisation; models detached from implementation.
- `IMPORTANT_CRITICISMS`: Up-front architecture can delay learning and lock in wrong abstractions; architecture documents may become authority without reality.
- `HOW_THE_PROPERTY_EVOLVED`: From complete design before coding to risk-targeted architecture before specific irreversible commitments, revisited incrementally.
- `MATURE_OR_EVOLVED_FORM`: Minimum sufficient architecture and constraint evidence, paired with prototypes and continuously reconciled with the realised system.
- `CEREMONY_VS_PROPERTY`: The property is early falsification of system-level constraints; a fixed CDR package or months-long architecture phase is not inherently required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_SUPPORT_MIXED_GENERAL_EVIDENCE
- `PRIMARY_SOURCES`: [S003](#source-s003), [S011](#source-s011), [S012](#source-s012), [S037](#source-s037), [S060](#source-s060)
- `CRITICAL_SOURCES`: [S006](#source-s006), [S039](#source-s039), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: GAO defence acquisition work repeatedly links immature technology/design to later cost and schedule exposure; the strongest evidence is for complex physical systems.
- `OPEN_QUESTIONS`: How can architecture effort be calibrated before the relevant commitment rather than by programme size alone?
- `REVERSIBILITY_PROFILE`: R0 light; R1 targeted; R2–R4 increasingly valuable where downstream physical, supplier or regulatory commitments are costly.
- `LINEAGE_CLASSIFICATION`: DIRECT_LINEAGE; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p004"></a>
### EW-P004 — Executable risk retirement through prototypes, pilots, simulation and thin increments

- `PROPERTY_ID`: EW-P004
- `PROPERTY_NAME`: Executable risk retirement through prototypes, pilots, simulation and thin increments
- `HISTORICAL_ORIGIN`: Benington/SAGE prototype; NATO simulation; Royce 'do it twice'; Boehm spiral; evolutionary acquisition.
- `ORIGINAL_FORM`: A separate pilot or prototype before the delivered system, sometimes a substantial miniature lifecycle.
- `PROBLEM_IT_ADDRESSED`: Critical operational, performance, interface and usability assumptions may remain invisible in documents and component tests.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Late discovery of infeasibility, wrong user need, integration behaviour or operational mismatch after most options are gone.
- `MECHANISM`: Choose the cheapest representative executable experiment that can discriminate the material risk: prototype, simulation, hardware-in-the-loop, pilot, test article or thin deployed increment.
- `TRIGGER_OR_CONTEXT`: Novelty, uncertainty, difficult integration, unproven technology, weak requirements confidence, expensive final test or high consequence.
- `NON_TRIGGER_OR_CHEAP_PATH`: For known repeat builds or low-risk local changes, ordinary automated tests or a small spike may suffice; avoid a ceremonial prototype that cannot affect the design.
- `DEPENDENCIES_OR_PRECONDITIONS`: Explicit hypothesis and decision; representative enough environment; protected budget/time; criteria for learning; no confusion between prototype evidence and qualified product evidence.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier risk retirement, better requirements and architecture, reduced late surprise and preserved options.
- `KNOWN_FAILURE_MODES`: Prototype becomes production without hardening; demo optimism; unrepresentative environment; pilot treated as schedule theatre; repeated experimentation without decision.
- `IMPORTANT_CRITICISMS`: A prototype may create false confidence and duplicate cost; not every project needs a separate full pilot.
- `HOW_THE_PROPERTY_EVOLVED`: From Royce's formal second pass to continuous risk-targeted experiments and incremental operational learning.
- `MATURE_OR_EVOLVED_FORM`: Executable evidence is selected by risk and commitment, with clear limits on what the experiment proves and explicit promotion criteria.
- `CEREMONY_VS_PROPERTY`: The property is empirical discrimination before commitment; a mandated prototype phase or 'MVP' label is not required.
- `CURRENT_STATUS`: STRONGLY_RETAINED
- `EVIDENCE_STRENGTH`: A_STRONG_HISTORICAL_DOMAIN_AND_CROSS_METHOD_SUPPORT
- `PRIMARY_SOURCES`: [S001](#source-s001), [S002](#source-s002), [S003](#source-s003), [S008](#source-s008), [S060](#source-s060)
- `CRITICAL_SOURCES`: [S047](#source-s047), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Historical aerospace practice, spiral, iterative development and modern acquisition all converge on early executable learning; effect size remains context-specific.
- `OPEN_QUESTIONS`: How representative must an experiment be for each risk, and when does pilot evidence become qualification evidence?
- `REVERSIBILITY_PROFILE`: R0–R4: useful throughout, but experiment cost and evidential rigour rise as consequences and commitments rise.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; REACTION_TO_WATERFALL; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p005"></a>
### EW-P005 — Current, transferable engineering knowledge and decision rationale

- `PROPERTY_ID`: EW-P005
- `PROPERTY_NAME`: Current, transferable engineering knowledge and decision rationale
- `HISTORICAL_ORIGIN`: Royce documentation; Benington records; Parnas/Clements rational design records; modern technical-data/model practices.
- `ORIGINAL_FORM`: Large specifications, design descriptions, review records and manuals.
- `PROBLEM_IT_ADDRESSED`: Complex systems outlive individuals and cross organisational boundaries; decisions and constraints must remain understandable.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Tacit rationale loss, repeated mistakes, unsafe maintenance, inability to review or transfer responsibility, and divergence between intent and implementation.
- `MECHANISM`: Capture current decisions, rationale, assumptions, interfaces, evidence and operating constraints in accessible forms linked to the relevant configuration.
- `TRIGGER_OR_CONTEXT`: Long-lived systems; turnover; suppliers; safety/certification; difficult maintenance; asynchronous or geographically distributed work.
- `NON_TRIGGER_OR_CHEAP_PATH`: Small co-located reversible work can rely on tests, code, short decision records and version history; document only durable or non-obvious knowledge.
- `DEPENDENCIES_OR_PRECONDITIONS`: Information ownership; update triggers; integration with work; discoverability; configuration links; deletion/retirement discipline.
- `EXPECTED_ENGINEERING_PAYOFF`: Faster review and maintenance, continuity across handoffs, auditable decisions and less reconstruction error.
- `KNOWN_FAILURE_MODES`: Documentation debt; write-only repositories; prose duplicated from code/models; volume obscures critical facts; rationale rationalised after the fact.
- `IMPORTANT_CRITICISMS`: Documentation can consume resources, slow feedback and create false assurance if it is approved but stale.
- `HOW_THE_PROPERTY_EVOLVED`: From prescribed volumes to information-item outcomes, living models/data, concise records and automated evidence.
- `MATURE_OR_EVOLVED_FORM`: Minimum sufficient, current and configuration-linked engineering knowledge whose maintenance cost is justified by future decisions.
- `CEREMONY_VS_PROPERTY`: The property is durable usable knowledge; page count, template completion and separate document ownership are not the property.
- `CURRENT_STATUS`: USEFUL_BUT_EASILY_BUREAUCRATISED
- `EVIDENCE_STRENGTH`: B_STRONG_MECHANISTIC_AND_DOMAIN_SUPPORT
- `PRIMARY_SOURCES`: [S003](#source-s003), [S006](#source-s006), [S014](#source-s014), [S018](#source-s018), [S019](#source-s019)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S039](#source-s039), [S040](#source-s040)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Modern standards explicitly separate required information from format; evidence for optimal documentation amount is weak and highly contextual.
- `OPEN_QUESTIONS`: What information has enough expected future value to maintain, and how can staleness be detected automatically?
- `REVERSIBILITY_PROFILE`: R0 minimal; R1 concise; R2–R4 stronger where lifetime, handoffs, hazards and authority increase.
- `LINEAGE_CLASSIFICATION`: DIRECT_LINEAGE; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p006"></a>
### EW-P006 — Configuration identification and baseline authority

- `PROPERTY_ID`: EW-P006
- `PROPERTY_NAME`: Configuration identification and baseline authority
- `HISTORICAL_ORIGIN`: Military/aerospace configuration management; formal baselines; later IEEE/NASA CM; software version and release engineering.
- `ORIGINAL_FORM`: Named configuration items, approved baselines, status accounting, audits and formal change control.
- `PROBLEM_IT_ADDRESSED`: Teams must know exactly which requirement, design, component, build and evidence set constitutes a proposed, tested, released or accepted system.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Wrong or unapproved item released; incompatible evidence; inability to reproduce a build; hidden drift; version disputes.
- `MECHANISM`: Identify configuration items and immutable or reproducible versions; record baseline purpose/status; control promotion and preserve provenance.
- `TRIGGER_OR_CONTEXT`: Multiple deployable versions; supplier or physical items; safety/certification; regulated evidence; long-lived support; distributed teams.
- `NON_TRIGGER_OR_CHEAP_PATH`: For ephemeral local work, ordinary version control branches and automated build identity are enough; not every intermediate file needs formal CI status.
- `DEPENDENCIES_OR_PRECONDITIONS`: Versionable artefacts; reproducible build/deployment process; named authority; status model; access control; retention policy.
- `EXPECTED_ENGINEERING_PAYOFF`: Reproducibility, controlled release, reliable evidence attribution, safer change and clearer responsibility.
- `KNOWN_FAILURE_MODES`: Baseline becomes freeze; documents controlled but live system not; too many configuration items; manual status accounting; shadow releases.
- `IMPORTANT_CRITICISMS`: Heavy CM can impede harmless change and create bureaucratic latency without preserving actual integrity.
- `HOW_THE_PROPERTY_EVOLVED`: From document baselines and boards to version control, immutable builds, signed artefacts, automated inventories and risk-triggered approval.
- `MATURE_OR_EVOLVED_FORM`: Authoritative identity across intent, source/model, build, test evidence and release, with proportionate promotion controls.
- `CEREMONY_VS_PROPERTY`: The property is identifiable authoritative state; a paper baseline, standing CCB or universal freeze is not required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: A_STRONG_MULTI_DOMAIN_NORMATIVE_AND_FAILURE_SUPPORT
- `PRIMARY_SOURCES`: [S009](#source-s009), [S021](#source-s021), [S023](#source-s023), [S026](#source-s026), [S029](#source-s029)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: NASA warns improper CM can release incorrect or unsafe products; regulatory and software-update regimes require identified configurations, while software supplies cheaper automation.
- `OPEN_QUESTIONS`: How fine should configuration-item granularity be, and how long should evidence/configurations be retained?
- `REVERSIBILITY_PROFILE`: R1–R4; R0 uses normal VCS. Value rises with multiple representations, releases, suppliers, certification and rollback difficulty.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; CONVERGENT_ENGINEERING; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p007"></a>
### EW-P007 — As-designed, as-built, as-tested and as-deployed reconciliation

- `PROPERTY_ID`: EW-P007
- `PROPERTY_NAME`: As-designed, as-built, as-tested and as-deployed reconciliation
- `HISTORICAL_ORIGIN`: Configuration audits, acceptance data packages, installation/checkout, operational readiness and digital-authority initiatives.
- `ORIGINAL_FORM`: Physical configuration audits, release records, installation audits and as-built drawings.
- `PROBLEM_IT_ADDRESSED`: Controlled plans or models can diverge from the item actually fabricated, tested, installed or operating.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Evidence proves a different system; field modifications are invisible; operations use unknown state; rollback or incident analysis is unreliable.
- `MECHANISM`: Continuously or at commitment points reconcile intended, realised, tested and deployed states; record deviations, waivers and environment identity.
- `TRIGGER_OR_CONTEXT`: Physical construction; fielded fleets; infrastructure; data migrations; certified releases; complex deployment environments.
- `NON_TRIGGER_OR_CHEAP_PATH`: For stateless, automatically deployed services, deployment manifests, telemetry and immutable image identity may supply the cheap path.
- `DEPENDENCIES_OR_PRECONDITIONS`: Observable deployed state; trustworthy inventory/telemetry; configuration identifiers; authority to resolve drift; environment capture.
- `EXPECTED_ENGINEERING_PAYOFF`: Acceptance evidence applies to reality, safer operations and maintenance, faster incident reconstruction, fewer undocumented modifications.
- `KNOWN_FAILURE_MODES`: Digital twin/model assumed correct without readback; inventory lag; manual audits only; uncontrolled emergency fixes; environment excluded.
- `IMPORTANT_CRITICISMS`: Reconciliation can be expensive or impossible under partial observability; excessive audit frequency can become theatre.
- `HOW_THE_PROPERTY_EVOLVED`: From occasional physical audits to automated provenance, software bills of materials, deployment attestations, telemetry and periodic physical confirmation.
- `MATURE_OR_EVOLVED_FORM`: Evidence-backed correspondence among authoritative models/data and actual built, tested and operating configurations, with explicit residual unknowns.
- `CEREMONY_VS_PROPERTY`: The property is correspondence to reality; an 'as-built' document or authoritative-source label is insufficient.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_SUPPORT_LIMITED_GENERAL_EMPIRICS
- `PRIMARY_SOURCES`: [S023](#source-s023), [S026](#source-s026), [S032](#source-s032), [S057](#source-s057), [S059](#source-s059)
- `CRITICAL_SOURCES`: [S038](#source-s038), [S039](#source-s039)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Operational-readiness and configuration guidance explicitly require actual-state correspondence; digital-engineering research identifies authority and interoperability gaps.
- `OPEN_QUESTIONS`: How should confidence be represented when deployed or physical state cannot be fully observed?
- `REVERSIBILITY_PROFILE`: R2–R4 strongest; R1 often automated; R0 generally unnecessary beyond normal build/run identity.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; HYBRID; CONVERGENT_ENGINEERING
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p008"></a>
### EW-P008 — Change visibility, impact analysis and risk-proportional authorisation

- `PROPERTY_ID`: EW-P008
- `PROPERTY_NAME`: Change visibility, impact analysis and risk-proportional authorisation
- `HISTORICAL_ORIGIN`: Formal change control and CCBs; configuration management; nuclear graded-change rules; modern automated dependency analysis.
- `ORIGINAL_FORM`: Change requests evaluated and approved by a standing board before baseline modification.
- `PROBLEM_IT_ADDRESSED`: Consequential changes can propagate across interfaces, evidence, suppliers, operations and regulatory commitments.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Unseen side effects, invalidated qualification/certification, incompatible releases, unauthorised risk acceptance or loss of provenance.
- `MECHANISM`: Expose proposed change, affected configurations/dependencies/evidence, consequence and rollback; route authority according to thresholds rather than uniformly.
- `TRIGGER_OR_CONTEXT`: Shared baselines; high coupling; external interfaces; safety/security/privacy; certified state; expensive recovery; contractual commitments.
- `NON_TRIGGER_OR_CHEAP_PATH`: Local reversible changes with strong automated tests can be pre-authorised under policy and merged through normal peer review/CI.
- `DEPENDENCIES_OR_PRECONDITIONS`: Dependency/trace information; clear delegated authority; risk criteria; timely reviewers; emergency path; audit trail.
- `EXPECTED_ENGINEERING_PAYOFF`: Safer consequential change, less surprise, preserved external commitments and clearer accountability.
- `KNOWN_FAILURE_MODES`: Standing board bottleneck; rubber-stamp approvals; impact analysis based on stale links; hidden workarounds; change avoidance; security patch delay.
- `IMPORTANT_CRITICISMS`: Change control can cost more than the change and can turn adaptation into exception processing.
- `HOW_THE_PROPERTY_EVOLVED`: From universal board approval to delegated, automated and risk-triggered control with post-change monitoring.
- `MATURE_OR_EVOLVED_FORM`: Policy-based change classes, automated impact evidence, named escalation thresholds and explicit acceptance of residual risk.
- `CEREMONY_VS_PROPERTY`: The property is visible authorised consequence management; a standing committee and meeting are not generally required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_DOMAIN_NORMATIVE_SUPPORT
- `PRIMARY_SOURCES`: [S021](#source-s021), [S023](#source-s023), [S024](#source-s024), [S031](#source-s031), [S036](#source-s036)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S050](#source-s050)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Nuclear rules explicitly permit some evaluated changes without prior regulator approval, demonstrating graded rather than universal control; DevSecOps uses automated evidence and continuous risk.
- `OPEN_QUESTIONS`: Reliable quantitative escalation thresholds remain unresolved; cyber urgency may invert normal approval timing.
- `REVERSIBILITY_PROFILE`: R0 pre-authorised; R1 automated/peer controlled; R2–R4 increasing analysis and authority, but emergency response must remain fast.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p009"></a>
### EW-P009 — Interface definition, ownership and compatibility control

- `PROPERTY_ID`: EW-P009
- `PROPERTY_NAME`: Interface definition, ownership and compatibility control
- `HISTORICAL_ORIGIN`: SAGE interface policing; aerospace/defence ICD traditions; systems engineering interface management; modular/open systems.
- `ORIGINAL_FORM`: Formal interface requirements and ICDs controlled by interface-control working groups or boards.
- `PROBLEM_IT_ADDRESSED`: Components developed by different teams, suppliers or disciplines must agree on semantics, units, timing, physical, data and operational contracts.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Late integration incompatibility, unsafe assumptions, responsibility gaps, local optimisation and cascading redesign.
- `MECHANISM`: Identify externally consequential interfaces, their semantics and owners; verify both sides; version changes; test compatibility in representative integration environments.
- `TRIGGER_OR_CONTEXT`: Organisational/supplier boundary; independently released components; fixed physical interfaces; long integration latency; safety or interoperability consequence.
- `NON_TRIGGER_OR_CHEAP_PATH`: Private local interfaces can evolve through code, types and tests without formal cross-organisational approval.
- `DEPENDENCIES_OR_PRECONDITIONS`: Two-sided ownership and access; semantic precision; change notification; configuration links; integration testability; dispute authority.
- `EXPECTED_ENGINEERING_PAYOFF`: Fewer integration surprises, parallel work with clearer contracts and contained change impact.
- `KNOWN_FAILURE_MODES`: ICD becomes stale; unanimous approval blocks evolution; interface is specified syntactically but not behaviourally; undocumented operational coupling.
- `IMPORTANT_CRITICISMS`: Formal interface control can over-centralise architecture and slow local refactoring; documents cannot replace integration tests.
- `HOW_THE_PROPERTY_EVOLVED`: From static ICDs and boards to versioned schemas/APIs, contract tests, compatibility policies, shared models and targeted governance.
- `MATURE_OR_EVOLVED_FORM`: Authoritative, testable and owned contracts for consequential boundaries, with automated compatibility evidence where possible.
- `CEREMONY_VS_PROPERTY`: The property is controlled compatibility at real boundaries; every internal function does not need an ICD or interface board.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: A_STRONG_MECHANISTIC_AND_DOMAIN_FAILURE_SUPPORT
- `PRIMARY_SOURCES`: [S001](#source-s001), [S024](#source-s024), [S025](#source-s025), [S037](#source-s037)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S038](#source-s038)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Mars Climate Orbiter is a concrete interface/units/system-verification failure; NASA guidance treats interface change as shared authority.
- `OPEN_QUESTIONS`: How to identify hidden socio-technical interfaces and avoid freezing modular evolution?
- `REVERSIBILITY_PROFILE`: R1 at independently released software boundary; R2–R4 strong where suppliers, physical fit, units, timing or safety matter; R0 cheap.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; CONVERGENT_ENGINEERING; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p010"></a>
### EW-P010 — Verification planning and requirement testability

- `PROPERTY_ID`: EW-P010
- `PROPERTY_NAME`: Verification planning and requirement testability
- `HISTORICAL_ORIGIN`: Royce early test planning; Boehm V-chart; V-model traditions; IEEE/NASA V&V.
- `ORIGINAL_FORM`: Verification plans and procedures prepared against baselined requirements before final test.
- `PROBLEM_IT_ADDRESSED`: Requirements may be ambiguous, infeasible or unevaluable until too late; environments, fixtures and data may have long lead times.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Unverifiable requirements, missing evidence, late test redesign, false pass criteria and qualification schedule collapse.
- `MECHANISM`: For each consequential requirement, define evaluation method, level, article/configuration, environment, success criteria and independence early enough to change the requirement/design.
- `TRIGGER_OR_CONTEXT`: Acceptance/certification obligation; difficult environment; scarce facility; performance/safety margin; supplier evidence; long test lead.
- `NON_TRIGGER_OR_CHEAP_PATH`: Low-risk software can encode acceptance examples and automated tests alongside implementation without a separate verification plan document.
- `DEPENDENCIES_OR_PRECONDITIONS`: Testable requirement; representative environment; instrumentation; configuration identity; resources; ownership; anomaly process.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier ambiguity detection, planned evidence coverage, lower late test surprise and more meaningful completion criteria.
- `KNOWN_FAILURE_MODES`: Test plan mirrors bad requirements; test design overfits expected behaviour; coverage matrix substitutes for challenge; expensive plans become stale.
- `IMPORTANT_CRITICISMS`: Planning tests early can prematurely lock the design or optimise only for stated requirements.
- `HOW_THE_PROPERTY_EVOLVED`: From a final test phase to evaluation planning during definition and continuous updating of executable evidence.
- `MATURE_OR_EVOLVED_FORM`: Risk-proportional verification design integrated with requirements and architecture, with automated evidence where appropriate.
- `CEREMONY_VS_PROPERTY`: The property is planned evaluability and evidence sufficiency; a monolithic master test plan is not universally required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: A_STRONG_PRIMARY_STANDARD_AND_DOMAIN_SUPPORT
- `PRIMARY_SOURCES`: [S003](#source-s003), [S005](#source-s005), [S020](#source-s020), [S022](#source-s022), [S026](#source-s026)
- `CRITICAL_SOURCES`: [S006](#source-s006), [S016](#source-s016)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Standards and domain practice consistently pair definition with planned evaluation; empirical effect size is less directly measured.
- `OPEN_QUESTIONS`: When does early test definition constrain beneficial requirement discovery or invite teaching to the test?
- `REVERSIBILITY_PROFILE`: R0 executable examples; R1 continuous tests; R2–R4 formal environment/article/evidence planning.
- `LINEAGE_CLASSIFICATION`: DIRECT_LINEAGE; SOFTWARE_V_FAMILY; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p011"></a>
### EW-P011 — Multi-level verification and integration evidence

- `PROPERTY_ID`: EW-P011
- `PROPERTY_NAME`: Multi-level verification and integration evidence
- `HISTORICAL_ORIGIN`: Independent staged testing in SAGE; Royce integrated-test concern; software V-chart; systems Vee.
- `ORIGINAL_FORM`: Unit, component, subsystem, integration and system tests conducted in progressively broader environments.
- `PROBLEM_IT_ADDRESSED`: Local conformance does not establish interactions, timing, load, emergent behaviour or end-to-end correctness.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Components pass alone but fail together; local phase completion is mistaken for system readiness; integration arrives too late.
- `MECHANISM`: Evaluate at the level where the relevant failure can manifest, integrate early and repeatedly, and preserve evidence linking failures to configuration and interfaces.
- `TRIGGER_OR_CONTEXT`: Distributed components; cyber-physical behaviour; performance/load; external services; multiple suppliers; system-of-systems.
- `NON_TRIGGER_OR_CHEAP_PATH`: For a small monolith or local change, one automated end-to-end path plus focused component tests may be enough.
- `DEPENDENCIES_OR_PRECONDITIONS`: Integration environment; representative data/load; observability; version identity; interface contracts; anomaly handling.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier cross-component failure detection, credible system evidence and reduced final-integration surprise.
- `KNOWN_FAILURE_MODES`: Test pyramid dogma; duplicated evidence; brittle environments; integration theatre with mocks; system tests too slow to guide development.
- `IMPORTANT_CRITICISMS`: More levels do not automatically add information; slow suites can delay feedback and encourage batching.
- `HOW_THE_PROPERTY_EVOLVED`: From terminal integration/test phases to continuous integration plus staged representative system and operational evaluation.
- `MATURE_OR_EVOLVED_FORM`: Layered evidence selected by failure observability, with fast lower-level feedback and periodic higher-fidelity integration.
- `CEREMONY_VS_PROPERTY`: The property is evaluation at the correct system level; a fixed number of test phases or a V diagram is not required.
- `CURRENT_STATUS`: STRONGLY_RETAINED
- `EVIDENCE_STRENGTH`: A_STRONG_HISTORICAL_DOMAIN_AND_MODERN_SUPPORT
- `PRIMARY_SOURCES`: [S001](#source-s001), [S003](#source-s003), [S005](#source-s005), [S011](#source-s011), [S022](#source-s022), [S035](#source-s035)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S048](#source-s048), [S054](#source-s054)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Historical failures and modern DevSecOps guidance converge on early integration; exact optimal cadence is system-specific.
- `OPEN_QUESTIONS`: How should slow, scarce or destructive integration tests be scheduled against fast local feedback?
- `REVERSIBILITY_PROFILE`: R0–R1 continuous and cheap; R2–R4 staged higher-fidelity evidence added where interactions and consequences demand it.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; SOFTWARE_V_FAMILY; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p012"></a>
### EW-P012 — Intended-use and operational-context validation

- `PROPERTY_ID`: EW-P012
- `PROPERTY_NAME`: Intended-use and operational-context validation
- `HISTORICAL_ORIGIN`: Early customer/operational evaluation; Royce customer involvement; Boehm V&V distinction; NASA/IEEE validation.
- `ORIGINAL_FORM`: Formal validation or acceptance testing after implementation against a concept of operations.
- `PROBLEM_IT_ADDRESSED`: A system can satisfy its specification yet fail stakeholder need, mission, workflow or actual environment.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Correct implementation of wrong requirements; unusable or operationally unsuitable system; hidden human/environment assumptions.
- `MECHANISM`: Evaluate representative users, missions, workflows, environments and outcomes throughout development and again on the integrated system.
- `TRIGGER_OR_CONTEXT`: Novel user need; socio-technical change; safety/mission consequence; operational environment unlike development; procurement handoff.
- `NON_TRIGGER_OR_CHEAP_PATH`: For familiar low-risk changes, telemetry, user tests and rapid reversible deployment can supply continuous validation.
- `DEPENDENCIES_OR_PRECONDITIONS`: Real stakeholders and operators; representative context; explicit intended use; outcome measures; ability to change requirements.
- `EXPECTED_ENGINEERING_PAYOFF`: Reduced wrong-system risk, better operational fit and clearer distinction between conformance and usefulness.
- `KNOWN_FAILURE_MODES`: Proxy users; scripted demonstration; confirmation bias; validation too late; stakeholder sign-off obtained without representative use.
- `IMPORTANT_CRITICISMS`: Users may ask for local preferences rather than system value; validation can become acceptance theatre.
- `HOW_THE_PROPERTY_EVOLVED`: From final customer demonstration to continuous discovery, simulation, operational experiments and independent operational evaluation.
- `MATURE_OR_EVOLVED_FORM`: Repeated context-validity evidence, with final claims tied to an identified configuration and intended-use envelope.
- `CEREMONY_VS_PROPERTY`: The property is evidence of fitness for intended purpose; a UAT meeting or customer signature alone is not enough.
- `CURRENT_STATUS`: STRONGLY_RETAINED
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_DOMAIN_CONCEPTUAL_AND_PRACTICE_SUPPORT
- `PRIMARY_SOURCES`: [S002](#source-s002), [S003](#source-s003), [S005](#source-s005), [S020](#source-s020), [S022](#source-s022), [S035](#source-s035)
- `CRITICAL_SOURCES`: [S006](#source-s006), [S007](#source-s007), [S016](#source-s016)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Definitions are stable across modern NASA/IEEE practice; direct comparative lifecycle evidence is limited but wrong-system failures are well established.
- `OPEN_QUESTIONS`: How representative must operational evaluation be, and how should conflicting stakeholder goals be adjudicated?
- `REVERSIBILITY_PROFILE`: R0 continuous cheap validation; R1 operational telemetry; R2–R4 increasingly representative and independently witnessed contexts.
- `LINEAGE_CLASSIFICATION`: DIRECT_LINEAGE; SOFTWARE_V_FAMILY; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p013"></a>
### EW-P013 — Qualification envelope and margin evidence

- `PROPERTY_ID`: EW-P013
- `PROPERTY_NAME`: Qualification envelope and margin evidence
- `HISTORICAL_ORIGIN`: Aerospace test traditions; environmental qualification; safety-critical hardware/software assurance.
- `ORIGINAL_FORM`: Qualification test articles exposed to environmental/performance extremes, often once per design type.
- `PROBLEM_IT_ADDRESSED`: A design may pass nominal tests yet fail across required environmental, load, timing or durability envelopes.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Field failure outside nominal conditions; manufacturing/design margin unknown; certification basis unsupported.
- `MECHANISM`: Demonstrate that a design or type meets a defined envelope and margin using analysis, test, similarity or inspection on representative configurations.
- `TRIGGER_OR_CONTEXT`: Safety/mission-critical product; physical environment; production of multiple units; scarce opportunities for field correction; certification requirement.
- `NON_TRIGGER_OR_CHEAP_PATH`: Ordinary web/software features with reversible deployment do not need a separate qualification programme; targeted performance/security tests may suffice.
- `DEPENDENCIES_OR_PRECONDITIONS`: Defined envelope and margins; representative article; validated models; configuration control; calibrated equipment; anomaly disposition.
- `EXPECTED_ENGINEERING_PAYOFF`: Confidence that the design, not merely one unit, can tolerate required conditions; reusable basis for accepting later units.
- `KNOWN_FAILURE_MODES`: Over-testing unrepresentative articles; destructive expense; qualification invalidated by design drift; passing envelope treated as proof of all use.
- `IMPORTANT_CRITICISMS`: Domain-specific and expensive; qualification can delay safer incremental improvements and is not synonymous with validation.
- `HOW_THE_PROPERTY_EVOLVED`: From one terminal campaign to staged component/system qualification, model-supported evidence and incremental requalification after bounded change.
- `MATURE_OR_EVOLVED_FORM`: Configuration-linked evidence for a defined design envelope, with explicit assumptions, margins and change-trigger rules.
- `CEREMONY_VS_PROPERTY`: The property is demonstrated capability over an envelope; a fixed test campaign or one qualification document is domain-specific.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_STANDARD_AND_PRACTICE_SUPPORT
- `PRIMARY_SOURCES`: [S022](#source-s022), [S026](#source-s026), [S028](#source-s028), [S032](#source-s032)
- `CRITICAL_SOURCES`: [S039](#source-s039), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: NASA explicitly distinguishes qualification from acceptance; aerospace/automotive regimes retain design-envelope evidence.
- `OPEN_QUESTIONS`: How much model-based credit is justified, and which changes invalidate prior qualification?
- `REVERSIBILITY_PROFILE`: Mostly R3–R4; selected R2 performance/security contexts. Usually no trigger for R0–R1 ordinary software.
- `LINEAGE_CLASSIFICATION`: DOMAIN_SPECIFIC; RELATED_PLAN_DRIVEN_TRADITION
- `RELATION_TO_ADAPTIVE_METHODS`: PLAN_DRIVEN_NATIVE

<a id="property-ew-p014"></a>
### EW-P014 — Acceptance criteria, authority and provenance

- `PROPERTY_ID`: EW-P014
- `PROPERTY_NAME`: Acceptance criteria, authority and provenance
- `HISTORICAL_ORIGIN`: Contractual acceptance, acceptance testing, flight-unit acceptance and transition-to-service practices.
- `ORIGINAL_FORM`: Formal customer acceptance test and signed delivery against a specified baseline.
- `PROBLEM_IT_ADDRESSED`: Delivery status can be ambiguous when technical evidence, contractual scope, exceptions and authority are disconnected.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Unauthorised declaration of completion; acceptance of wrong configuration; unresolved exceptions hidden; later dispute over obligations.
- `MECHANISM`: Name the acceptance authority, criteria, evidence, accepted configuration, exceptions/waivers and effective transition of responsibility.
- `TRIGGER_OR_CONTEXT`: External acquirer/operator; regulated or safety system; contractual deliverable; irreversible cutover; transfer between organisations.
- `NON_TRIGGER_OR_CHEAP_PATH`: Internal reversible software release can use automated release criteria and product-owner/operational approval without a separate ceremony.
- `DEPENDENCIES_OR_PRECONDITIONS`: Identified deliverable; criteria agreed before decision; verification/validation evidence; authority; exception disposition; audit trail.
- `EXPECTED_ENGINEERING_PAYOFF`: Clear transfer of custody and obligations, fewer disputes, operational accountability and evidence provenance.
- `KNOWN_FAILURE_MODES`: Signature without technical understanding; acceptance used to force schedule; criteria changed retrospectively; accepted documents differ from deployed system.
- `IMPORTANT_CRITICISMS`: Acceptance can be legal/formal rather than engineering truth; buyer sign-off does not prove fitness or certification.
- `HOW_THE_PROPERTY_EVOLVED`: From one final event to incremental acceptance of capability/configurations and continuous service-level acceptance evidence.
- `MATURE_OR_EVOLVED_FORM`: Explicit, configuration-specific decision by empowered authority, based on current evidence and recorded residual obligations.
- `CEREMONY_VS_PROPERTY`: The property is authorised transfer over an identified state; a final meeting, certificate or customer signature form is not inherently sufficient.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_CONTRACTUAL_SUPPORT
- `PRIMARY_SOURCES`: [S002](#source-s002), [S022](#source-s022), [S026](#source-s026), [S057](#source-s057)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S017](#source-s017)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: NASA distinguishes acceptance of each flight unit from design qualification; procurement failures show that formal milestones can lack operational evidence.
- `OPEN_QUESTIONS`: How should continuous services represent partial, conditional or revocable acceptance?
- `REVERSIBILITY_PROFILE`: R2–R4 strong where custody, liability or operations transfer; R0–R1 can use lightweight automated promotion.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; DOMAIN_SPECIFIC; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p015"></a>
### EW-P015 — Certification basis and regulatory-authority coupling

- `PROPERTY_ID`: EW-P015
- `PROPERTY_NAME`: Certification basis and regulatory-authority coupling
- `HISTORICAL_ORIGIN`: Airworthiness, nuclear licensing, medical-device regulation, rail safety and other external assurance regimes.
- `ORIGINAL_FORM`: Evidence package and formal application demonstrating compliance with prescribed objectives to an empowered authority.
- `PROBLEM_IT_ADDRESSED`: Some systems create public/third-party risk that cannot be accepted solely by the developer or acquirer.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Operating without legal authority; evidence not aligned to certification basis; changes invalidate approval; authority sees changes too late.
- `MECHANISM`: Identify applicable certification basis, means of compliance, authority interfaces, evidence/configuration boundaries and change/reapproval triggers.
- `TRIGGER_OR_CONTEXT`: Legally regulated system; safety or environmental externality; airworthiness/type approval/licensing; public infrastructure.
- `NON_TRIGGER_OR_CHEAP_PATH`: No trigger where no empowered external certification regime applies; do not invent an internal 'certification' label.
- `DEPENDENCIES_OR_PRECONDITIONS`: Correct legal/domain expertise; early authority agreement; configuration/evidence trace; independent assessment where required; change visibility.
- `EXPECTED_ENGINEERING_PAYOFF`: Reduced approval surprise, lawful operation, clearer public-risk accountability and reusable compliance evidence.
- `KNOWN_FAILURE_MODES`: Compliance theatre; regulator capture; certification treated as proof of zero risk; excessive conservatism; obsolete rules; duplicated evidence.
- `IMPORTANT_CRITICISMS`: Domain-specific obligations cannot be generalised; authority approval may lag technical reality or inhibit beneficial change.
- `HOW_THE_PROPERTY_EVOLVED`: From terminal dossiers toward early authority engagement, modular/incremental evidence, update-management systems and continuous monitoring—without eliminating legal decisions.
- `MATURE_OR_EVOLVED_FORM`: Lifecycle-neutral engineering that satisfies a specific certification basis for identified configurations and maintains authority after change.
- `CEREMONY_VS_PROPERTY`: The property is alignment with an actual empowered regime; an internal badge, generic compliance checklist or 'certified' document is not general engineering.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_LEGAL_AND_STANDARD_SUPPORT
- `PRIMARY_SOURCES`: [S026](#source-s026), [S027](#source-s027), [S028](#source-s028), [S029](#source-s029), [S030](#source-s030), [S031](#source-s031), [S061](#source-s061)
- `CRITICAL_SOURCES`: [S033](#source-s033), [S039](#source-s039)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Current aerospace, automotive, medical, rail and nuclear regimes vary but all bind evidence/configuration/change to external authority.
- `OPEN_QUESTIONS`: How far can certification become continuous without weakening independent public authority?
- `REVERSIBILITY_PROFILE`: R3–R4; sometimes R2 for regulated digital services. No general R0–R1 trigger.
- `LINEAGE_CLASSIFICATION`: DOMAIN_SPECIFIC; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONTEXT_SWITCH

<a id="property-ew-p016"></a>
### EW-P016 — Independent technical challenge and IV&V

- `PROPERTY_ID`: EW-P016
- `PROPERTY_NAME`: Independent technical challenge and IV&V
- `HISTORICAL_ORIGIN`: Independent testing in SAGE; defence/nuclear IV&V; IEEE 1012; independent operational test and safety assessment.
- `ORIGINAL_FORM`: Separate organisation performs verification/validation with technical, managerial and financial independence.
- `PROBLEM_IT_ADDRESSED`: Developer incentives, familiarity and group assumptions can suppress or miss consequential defects and invalid claims.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Self-confirming evidence, conflicted risk acceptance, unchallenged assumptions, management pressure and false closure.
- `MECHANISM`: Provide technically competent challenge with sufficient separation of responsibility and authority, focused on critical claims, while preserving timely access and feedback.
- `TRIGGER_OR_CONTEXT`: High criticality; novel or complex system; public/third-party risk; strong schedule incentives; many suppliers; opaque evidence; regulatory mandate.
- `NON_TRIGGER_OR_CHEAP_PATH`: Low-consequence reversible work can use peer review, rotation, automated checks and occasional external review rather than a standing IV&V organisation.
- `DEPENDENCIES_OR_PRECONDITIONS`: Access to products/data; competence; protected escalation; technical/managerial/financial independence proportionate to risk; coordination and feedback channel.
- `EXPECTED_ENGINEERING_PAYOFF`: Unique defect discovery, reduced confirmation bias, stronger evidence credibility and independent information for authorities.
- `KNOWN_FAILURE_MODES`: 10–30% added cost in older studies; duplicate work; paperwork; late findings; adversarial separation; reviewers lack context; nominal independence without authority.
- `IMPORTANT_CRITICISMS`: Comparative outcome and return-on-cost evidence are mixed; independence can reduce feedback speed and may not improve reliability.
- `HOW_THE_PROPERTY_EVOLVED`: From universal separate organisation to integrity/risk-scaled scopes, embedded-independent roles, focused IV&V and continuous independent operational evaluation.
- `MATURE_OR_EVOLVED_FORM`: Independence is a designed property—responsibility, incentives, funding, reporting and corrective-action authority—scaled to consequence and integrated early.
- `CEREMONY_VS_PROPERTY`: The property is credible independent challenge; a different team name, audit meeting or mandatory full duplicate lifecycle is not sufficient.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: C_MIXED_EMPIRICAL_STRONG_DOMAIN_RATIONALE
- `PRIMARY_SOURCES`: [S020](#source-s020), [S045](#source-s045), [S046](#source-s046), [S062](#source-s062), [S035](#source-s035)
- `CRITICAL_SOURCES`: [S045](#source-s045), [S046](#source-s046)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Small NASA-project evidence found earlier detection but no reliability/fix-cost gain and lower productivity; larger defence/avionics cases reported substantial early detection and possible cost recovery, with weak comparability.
- `OPEN_QUESTIONS`: Which independence dimensions and scope yield net value by risk class? Modern comparative evidence remains sparse.
- `REVERSIBILITY_PROFILE`: R3–R4 strongest; R2 where security/public risk or conflict exists; R0–R1 usually lightweight challenge.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; DOMAIN_SPECIFIC; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONTEXT_SWITCH

<a id="property-ew-p017"></a>
### EW-P017 — Demonstrable bidirectional traceability

- `PROPERTY_ID`: EW-P017
- `PROPERTY_NAME`: Demonstrable bidirectional traceability
- `HISTORICAL_ORIGIN`: Requirements-to-design/code/test matrices in defence/aerospace; V-model correspondence; modern linked lifecycle data.
- `ORIGINAL_FORM`: Manual traceability matrices showing forward and backward links among requirements, design, implementation and tests.
- `PROBLEM_IT_ADDRESSED`: Authorities and maintainers need to know why an element exists, what a change affects and whether obligations have evidence.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Orphan requirements, unexplained implementation, untested obligations, missed impact and evidence attached to wrong requirement/configuration.
- `MECHANISM`: Maintain decision-useful, queryable and configuration-aware relations among consequential intent, design, implementation, hazards, changes and evidence; monitor link quality and decay.
- `TRIGGER_OR_CONTEXT`: Certification; high coupling; long-lived system; supplier handoff; safety/hazard chains; expensive impact analysis; many variants.
- `NON_TRIGGER_OR_CHEAP_PATH`: For small rapidly changing software, issue/commit/test naming, executable specifications, types and dependency graphs may provide sufficient native trace.
- `DEPENDENCIES_OR_PRECONDITIONS`: Stable identifiers; clear semantics; automated capture where possible; ownership; quality checks; actual use in decisions; cost budget.
- `EXPECTED_ENGINEERING_PAYOFF`: Faster and more correct maintenance/impact tasks, coverage visibility, evidence provenance and defect prevention in some settings.
- `KNOWN_FAILURE_MODES`: Stale or false links; exhaustive matrices no one uses; high creation/maintenance cost; link-count compliance; generated links overwhelm users.
- `IMPORTANT_CRITICISMS`: Laboratory benefits assume correct complete traces; industrial causal evidence and net lifecycle return remain limited.
- `HOW_THE_PROPERTY_EVOLVED`: From manual matrices to selective, automated, queryable graph relations with staleness detection and use-based scope.
- `MATURE_OR_EVOLVED_FORM`: Trace the claims whose loss would impair a real decision; maintain evidence of link quality rather than maximising link count.
- `CEREMONY_VS_PROPERTY`: The property is demonstrable relation for a decision; a spreadsheet or universal end-to-end matrix is not required.
- `CURRENT_STATUS`: USEFUL_BUT_EASILY_BUREAUCRATISED
- `EVIDENCE_STRENGTH`: C_MIXED_EMPIRICAL_SUPPORT
- `PRIMARY_SOURCES`: [S005](#source-s005), [S026](#source-s026), [S041](#source-s041), [S042](#source-s042), [S043](#source-s043), [S044](#source-s044)
- `CRITICAL_SOURCES`: [S039](#source-s039), [S044](#source-s044)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Controlled studies report roughly 21–24% faster tasks and 50–60% more correct solutions under ideal traces; an observational study associates completeness with fewer defects; reviews identify maintenance cost and weak general industrial evidence.
- `OPEN_QUESTIONS`: What is the minimum valuable trace set, how should decay be measured, and when do native executable links outperform explicit links?
- `REVERSIBILITY_PROFILE`: R0 native/light; R1 selective; R2–R4 stronger where impact/evidence decisions are costly, but maintenance burden also rises.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p018"></a>
### EW-P018 — Safety and hazard analysis with tracked risk controls

- `PROPERTY_ID`: EW-P018
- `PROPERTY_NAME`: Safety and hazard analysis with tracked risk controls
- `HISTORICAL_ORIGIN`: System-safety engineering, nuclear/aerospace hazard analyses, automotive functional safety and rail risk assessment.
- `ORIGINAL_FORM`: Hazard analyses, safety requirements, control verification and hazard logs maintained through staged reviews.
- `PROBLEM_IT_ADDRESSED`: Normal requirements and tests may omit hazardous interactions, misuse, degraded modes and organisational/operational causes.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Catastrophic harm despite specification compliance; safety control lost during change; hazard accepted without authority.
- `MECHANISM`: Identify hazards and causal scenarios; assign controls across design, operation and organisation; verify controls; track residual risk and changes through life.
- `TRIGGER_OR_CONTEXT`: Potential death/injury, environmental harm, major public loss, high-energy physical system, safety-related software or infrastructure.
- `NON_TRIGGER_OR_CHEAP_PATH`: No trigger for ordinary low-consequence functionality; proportionate product/security risk analysis may replace formal system-safety machinery.
- `DEPENDENCIES_OR_PRECONDITIONS`: Competent multidisciplinary analysis; operational input; authority; configuration/trace links; incident learning; credible severity/likelihood treatment.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier hazard elimination, explicit safety constraints, visible residual risk and change-sensitive protection.
- `KNOWN_FAILURE_MODES`: Checklist hazard analysis; implausible probabilities; paper controls not implemented; hazard log stale; safety treated as separate team.
- `IMPORTANT_CRITICISMS`: Formal analyses can create false precision and omit unknown/organisational hazards; compliance can displace real challenge.
- `HOW_THE_PROPERTY_EVOLVED`: From one-time hazard reports to through-life hazard records, model-based analyses, operational monitoring and risk-triggered reassessment.
- `MATURE_OR_EVOLVED_FORM`: Living hazard/control claims tied to actual configurations, operations, evidence and residual-risk authority.
- `CEREMONY_VS_PROPERTY`: The property is active hazard control; a hazard-log template or safety review board is not sufficient.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_LEGAL_AND_FAILURE_SUPPORT
- `PRIMARY_SOURCES`: [S028](#source-s028), [S030](#source-s030), [S031](#source-s031), [S032](#source-s032), [S033](#source-s033)
- `CRITICAL_SOURCES`: [S025](#source-s025), [S039](#source-s039)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Multiple high-consequence domains require hazard/risk control and independent assessment; outcome attribution to specific artefacts is difficult.
- `OPEN_QUESTIONS`: How should unknown hazards and socio-technical interactions be represented without false quantification?
- `REVERSIBILITY_PROFILE`: R4 primary; R3 where public/regulated consequences; selected R2 security/privacy. No general R0 trigger.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; DOMAIN_SPECIFIC
- `RELATION_TO_ADAPTIVE_METHODS`: PLAN_DRIVEN_NATIVE

<a id="property-ew-p019"></a>
### EW-P019 — Assurance or safety case as a living claims–argument–evidence structure

- `PROPERTY_ID`: EW-P019
- `PROPERTY_NAME`: Assurance or safety case as a living claims–argument–evidence structure
- `HISTORICAL_ORIGIN`: UK goal-setting safety regulation; nuclear/offshore/defence safety cases; assurance-case research.
- `ORIGINAL_FORM`: Large safety-case report or dossier submitted at programme milestones.
- `PROBLEM_IT_ADDRESSED`: Complex safety/assurance conclusions depend on many heterogeneous claims, assumptions and evidence that a checklist cannot expose.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Evidence warehouse without a coherent claim; unsupported leaps; hidden assumptions; authority cannot see why evidence is sufficient.
- `MECHANISM`: Maintain an explicit, challengeable argument linking top claims, contexts, defeaters/uncertainty and configuration-specific evidence throughout life.
- `TRIGGER_OR_CONTEXT`: Novel high-consequence system; non-prescriptive regulation; heterogeneous evidence; residual risk requiring an accountable judgement.
- `NON_TRIGGER_OR_CHEAP_PATH`: Stable low-risk products can use concise control/evidence summaries; do not construct a graphical assurance case merely to satisfy a style.
- `DEPENDENCIES_OR_PRECONDITIONS`: Claims with scope; credible evidence; independent challenge; configuration/version links; operational updates; willingness to record doubt and counterevidence.
- `EXPECTED_ENGINEERING_PAYOFF`: Transparent reasoning, focused evidence gaps, through-life risk decisions and better communication across disciplines and authority.
- `KNOWN_FAILURE_MODES`: Persuasive brief rather than inquiry; confirmation bias; after-the-fact rationalisation; static report; duplicated document warehouse; graphical complexity.
- `IMPORTANT_CRITICISMS`: Direct comparative outcome evidence is weak; a polished argument can launder weak premises and consume disproportionate effort.
- `HOW_THE_PROPERTY_EVOLVED`: From terminal report to living, configuration-linked, falsification-oriented assurance reasoning with continuous evidence.
- `MATURE_OR_EVOLVED_FORM`: Use structured argument only where it changes risk decisions, expose assumptions/defeaters, and distinguish the case from its report.
- `CEREMONY_VS_PROPERTY`: The property is challengeable assurance reasoning; a large report, graphical notation or fixed milestone submission is not inherently required.
- `CURRENT_STATUS`: USEFUL_BUT_EASILY_BUREAUCRATISED
- `EVIDENCE_STRENGTH`: C_STRONG_DOMAIN_GUIDANCE_WEAK_OUTCOME_EVIDENCE
- `PRIMARY_SOURCES`: [S033](#source-s033), [S036](#source-s036)
- `CRITICAL_SOURCES`: [S033](#source-s033), [S039](#source-s039)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: MOD guidance explicitly records both intended benefits and pathologies: compliance-only production, stale reports, process-focused audits and late apologetic cases.
- `OPEN_QUESTIONS`: Does a structured case measurably outperform well-designed hazard/evidence management, and how should uncertainty/defeaters be represented?
- `REVERSIBILITY_PROFILE`: R3–R4; sometimes R2 for consequential security/AI/public systems. Usually no R0–R1 trigger.
- `LINEAGE_CLASSIFICATION`: DOMAIN_SPECIFIC; CONVERGENT_ENGINEERING; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p020"></a>
### EW-P020 — Anomaly, problem-report, deviation, waiver and corrective-action provenance

- `PROPERTY_ID`: EW-P020
- `PROPERTY_NAME`: Anomaly, problem-report, deviation, waiver and corrective-action provenance
- `HISTORICAL_ORIGIN`: SAGE problem records; Royce test control; defence problem reports; quality/safety corrective-action systems.
- `ORIGINAL_FORM`: Formal problem reports, discrepancy review boards, waivers/deviations and corrective-action records.
- `PROBLEM_IT_ADDRESSED`: Failures, accepted exceptions and recurring causes must remain visible across releases and authority changes.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Defect silently deferred; waiver applied to wrong configuration; recurring failure; test pass obtained by changing expectation; root cause never addressed.
- `MECHANISM`: Give each material anomaly identity, affected configuration, severity, evidence, disposition, authority, corrective action and verification of closure; retain accepted residuals.
- `TRIGGER_OR_CONTEXT`: Safety/mission/quality consequence; repeated releases; supplier defects; certification/acceptance exceptions; operational incidents.
- `NON_TRIGGER_OR_CHEAP_PATH`: Low-risk local bugs can use an issue tracker and automated regression test; do not convene a discrepancy board for every defect.
- `DEPENDENCIES_OR_PRECONDITIONS`: Non-punitive reporting; configuration identity; severity criteria; closure authority; root-cause competence; feedback into requirements/hazards/tests.
- `EXPECTED_ENGINEERING_PAYOFF`: Prevents silent loss, supports recurrence analysis, preserves exceptions and demonstrates closure on the correct state.
- `KNOWN_FAILURE_MODES`: Ticket closure without fix; backlog graveyard; root-cause theatre; excessive paperwork; waiver normalisation; metrics gaming.
- `IMPORTANT_CRITICISMS`: Formal corrective-action systems can prioritise closure statistics over learning and impose disproportionate burden.
- `HOW_THE_PROPERTY_EVOLVED`: From paper discrepancy boards to integrated issue/evidence/provenance systems, automated regression and risk-triggered escalation.
- `MATURE_OR_EVOLVED_FORM`: One material problem identity from detection through authorised disposition and verified correction, linked to configuration and evidence.
- `CEREMONY_VS_PROPERTY`: The property is durable problem/exception provenance and closure; a standing board or mandatory form is not required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: B_STRONG_CROSS_DOMAIN_MECHANISTIC_SUPPORT
- `PRIMARY_SOURCES`: [S001](#source-s001), [S005](#source-s005), [S022](#source-s022), [S026](#source-s026), [S033](#source-s033)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S050](#source-s050)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Historical and current assurance regimes consistently preserve anomaly and corrective-action records; controlled net-benefit evidence is limited.
- `OPEN_QUESTIONS`: How should organisations prevent backlog and waiver normalisation without over-classifying minor defects?
- `REVERSIBILITY_PROFILE`: R1–R4 progressively stronger; R0 normal issue/test path.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; CONVERGENT_ENGINEERING; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p021"></a>
### EW-P021 — Evidence-backed, event-driven commitment reviews

- `PROPERTY_ID`: EW-P021
- `PROPERTY_NAME`: Evidence-backed, event-driven commitment reviews
- `HISTORICAL_ORIGIN`: Design reviews, phase gates, acquisition milestones and technical review traditions.
- `ORIGINAL_FORM`: Calendar-scheduled preliminary/critical design reviews and phase-gate meetings approving documents before the next phase.
- `PROBLEM_IT_ADDRESSED`: Large commitments need explicit decisions, but calendar progress and document completion are weak proxies for technical readiness.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Production, deployment, procurement or certification commitment without enough knowledge; gate passes because stopping is politically impossible.
- `MECHANISM`: Define the irreversible decision, entrance/exit evidence, residual risks and decision rights; review when evidence is ready and preserve a real stop/redirect option.
- `TRIGGER_OR_CONTEXT`: Capital, production, long-lead procurement, fleet deployment, irreversible migration, safety authority, major supplier or contractual commitment.
- `NON_TRIGGER_OR_CHEAP_PATH`: Continuous low-risk software work can use automated promotion rules and lightweight asynchronous review; no milestone meeting is needed.
- `DEPENDENCIES_OR_PRECONDITIONS`: Decision authority able to stop/change course; independent challenge; current actual-state evidence; transparent criteria; no automatic schedule pass.
- `EXPECTED_ENGINEERING_PAYOFF`: Better-timed commitment, risk visibility, option preservation and accountability for residual uncertainty.
- `KNOWN_FAILURE_MODES`: Milestone gaming; slideware; sunk-cost escalation; duplicate boards; criteria waived at the meeting; gate after commitment already made.
- `IMPORTANT_CRITICISMS`: Phase gates can certify documents rather than products, batch feedback and reward concealment; the review may add no new decision information.
- `HOW_THE_PROPERTY_EVOLVED`: From fixed phase completion to event-driven, risk-based knowledge points, continuous evidence and overlapping work.
- `MATURE_OR_EVOLVED_FORM`: A commitment decision—not a lifecycle phase—whose strength matches the cost and consequence of being wrong.
- `CEREMONY_VS_PROPERTY`: The property is a consequential decision based on discriminating evidence with real authority; a board, meeting, colour status or named review is optional.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_CRITICAL_SUPPORT
- `PRIMARY_SOURCES`: [S003](#source-s003), [S037](#source-s037), [S049](#source-s049), [S060](#source-s060)
- `CRITICAL_SOURCES`: [S017](#source-s017), [S050](#source-s050), [S016](#source-s016)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: GAO and DoD guidance favour knowledge/event-driven reviews; escalation research and institutional reports show that formal milestones can reinforce sunk cost.
- `OPEN_QUESTIONS`: Which decision criteria predict better outcomes, and how often do gates truly stop or redirect programmes?
- `REVERSIBILITY_PROFILE`: R3–R4 primary; selected R2 cutovers. R0–R1 should normally use continuous policy gates.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; REFINED; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p022"></a>
### EW-P022 — Staged and incremental commitment with option preservation

- `PROPERTY_ID`: EW-P022
- `PROPERTY_NAME`: Staged and incremental commitment with option preservation
- `HISTORICAL_ORIGIN`: Pilot systems, spiral risk management, evolutionary acquisition, incremental Vee and knowledge-based product development.
- `ORIGINAL_FORM`: Sequentially commit requirements, design, production and deployment after major reviews.
- `PROBLEM_IT_ADDRESSED`: Uncertainty and irreversible downstream choices make all-at-once commitment hazardous, yet unlimited provisional work prevents coordination.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Too much capital/supplier/design commitment before evidence; or endless experimentation without converging on an operational system.
- `MECHANISM`: Break commitments into independently valuable or risk-retiring increments; delay irreversible choices until evidence warrants them; explicitly price retained options.
- `TRIGGER_OR_CONTEXT`: High uncertainty plus expensive downstream commitment; modular capability; long lead; production tooling; migration waves; certification increments.
- `NON_TRIGGER_OR_CHEAP_PATH`: For cheap reversible changes, ship/test/revert directly rather than inventing formal commitment stages.
- `DEPENDENCIES_OR_PRECONDITIONS`: Modular architecture or separable decisions; incremental acceptance/evidence; funding and contracts that permit revision; explicit option-expiry decisions.
- `EXPECTED_ENGINEERING_PAYOFF`: Reduced exposure to wrong assumptions, earlier value/learning and bounded cancellation or redesign cost.
- `KNOWN_FAILURE_MODES`: Pseudo-increments that integrate only at end; permanent temporary architecture; partial capability with full overhead; option preservation used to avoid decisions.
- `IMPORTANT_CRITICISMS`: Incrementalisation can increase integration and certification overhead or be impossible for tightly coupled physical systems.
- `HOW_THE_PROPERTY_EVOLVED`: From one large phase sequence to risk-ordered increments, progressive baselines, modular certification and rolling investment decisions.
- `MATURE_OR_EVOLVED_FORM`: Commit evidence, money and authority in slices sized by uncertainty, coupling and reversibility, while preserving coherent system integration.
- `CEREMONY_VS_PROPERTY`: The property is bounded commitment and retained alternatives; arbitrary phases, quarterly gates or a fixed increment length are not required.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_TRADITION_AND_DOMAIN_SUPPORT
- `PRIMARY_SOURCES`: [S008](#source-s008), [S012](#source-s012), [S014](#source-s014), [S018](#source-s018), [S019](#source-s019), [S060](#source-s060)
- `CRITICAL_SOURCES`: [S017](#source-s017), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Spiral, incremental Vee, current lifecycle standards and acquisition evidence converge; exact economic benefit depends on separability and overhead.
- `OPEN_QUESTIONS`: How should option value and increment boundaries be measured in tightly coupled systems?
- `REVERSIBILITY_PROFILE`: Useful from R1–R4; strongest before R3–R4 commitment. R0 naturally preserves options without formal staging.
- `LINEAGE_CLASSIFICATION`: REACTION_TO_WATERFALL; HYBRID; RELATED_PLAN_DRIVEN_TRADITION
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p023"></a>
### EW-P023 — Incremental, concurrent and recursive lifecycle application

- `PROPERTY_ID`: EW-P023
- `PROPERTY_NAME`: Incremental, concurrent and recursive lifecycle application
- `HISTORICAL_ORIGIN`: Early iterative practice; spiral; incremental Vee; MIL-STD-498; modern ISO lifecycle standards.
- `ORIGINAL_FORM`: Apply one sequence of requirements, design, implementation and test once to the whole system.
- `PROBLEM_IT_ADDRESSED`: Systems contain levels, increments and elements at different maturity; a single project-wide phase order batches learning and hides recursive dependencies.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: One giant final integration, subsystem handoffs, local completion without system progress and inability to adapt lifecycle to element risk.
- `MECHANISM`: Apply lifecycle responsibilities concurrently, iteratively and recursively at system, element, increment and sustainment levels; coordinate their baselines and evidence.
- `TRIGGER_OR_CONTEXT`: Any non-trivial system with elements/increments, especially differing technologies, suppliers or release cadences.
- `NON_TRIGGER_OR_CHEAP_PATH`: A tiny product need not model recursive lifecycle structure explicitly; normal iterative work can realise the property.
- `DEPENDENCIES_OR_PRECONDITIONS`: Clear system boundaries; integration cadence; shared configuration/evidence; ownership across levels; tailored coordination.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier learning, parallel progress, repeated integration and preservation of assurance responsibilities without a fixed global phase sequence.
- `KNOWN_FAILURE_MODES`: Fractal process bureaucracy; each subsystem creates full document stack; asynchronous increments drift; local optimisation.
- `IMPORTANT_CRITICISMS`: Concurrency can create rework and coordination load; recursion is not free and does not eliminate architecture dependencies.
- `HOW_THE_PROPERTY_EVOLVED`: Explicitly incorporated into ISO 15288/12207, incremental Vee and hybrid safety/DevSecOps practice.
- `MATURE_OR_EVOLVED_FORM`: Lifecycle processes are obligations and feedback loops applied where needed, not calendar phases traversed once.
- `CEREMONY_VS_PROPERTY`: The property is repeated/recursive fulfilment of responsibilities; separate mini-waterfalls and duplicated stage artefacts are not required.
- `CURRENT_STATUS`: STRONGLY_RETAINED
- `EVIDENCE_STRENGTH`: A_STRONG_PRIMARY_STANDARDS_AND_HISTORICAL_SUPPORT
- `PRIMARY_SOURCES`: [S008](#source-s008), [S012](#source-s012), [S014](#source-s014), [S018](#source-s018), [S019](#source-s019), [S035](#source-s035)
- `CRITICAL_SOURCES`: [S016](#source-s016)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Current system/software lifecycle standards explicitly allow concurrent, iterative, recursive and incremental use.
- `OPEN_QUESTIONS`: How should cross-level cadence and evidence inheritance be optimised in very large systems?
- `REVERSIBILITY_PROFILE`: All bands; degree of formal coordination increases from R1 to R4.
- `LINEAGE_CLASSIFICATION`: HYBRID; RELATED_PLAN_DRIVEN_TRADITION; REACTION_TO_WATERFALL
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p024"></a>
### EW-P024 — Tailoring and proportionality

- `PROPERTY_ID`: EW-P024
- `PROPERTY_NAME`: Tailoring and proportionality
- `HISTORICAL_ORIGIN`: Royce cost caveat; defence standard tailoring; V-Modell XT; ISO lifecycle standards; integrity/risk-based assurance.
- `ORIGINAL_FORM`: Programme-specific tailoring of standard activities, documents and reviews, often requiring formal approval.
- `PROBLEM_IT_ADDRESSED`: Uniform process imposes low-value burden on small/reversible work and may under-control novel/high-consequence work.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Ceremony independent of risk; skipped critical evidence because template says optional; inconsistent tailoring hidden from authorities.
- `MECHANISM`: Scale depth, independence, documentation, traceability, review and authority to consequence, uncertainty, coupling, reversibility, feedback latency and external obligation; record rationale.
- `TRIGGER_OR_CONTEXT`: Always as a meta-property whenever a lifecycle or assurance control is considered.
- `NON_TRIGGER_OR_CHEAP_PATH`: Default lightweight path for local reversible work, with pre-defined escalation triggers rather than case-by-case bureaucracy.
- `DEPENDENCIES_OR_PRECONDITIONS`: Credible risk/context classification; authority to tailor; feedback on whether controls work; minimum non-tailorable legal obligations identified.
- `EXPECTED_ENGINEERING_PAYOFF`: Lower process waste, stronger focus on critical risks and greater legitimacy/compliance with necessary controls.
- `KNOWN_FAILURE_MODES`: 'Tailoring' means deleting unpopular checks without analysis; approval to tailor is itself heavy; risk scores manipulated; over-customisation destroys comparability.
- `IMPORTANT_CRITICISMS`: Risk classification is uncertain and can be gamed; proportionality can become vague permission for inconsistency.
- `HOW_THE_PROPERTY_EVOLVED`: From selecting documents from a standard to dynamic, policy-based assurance profiles and integrity levels.
- `MATURE_OR_EVOLVED_FORM`: A transparent control-selection rule with cheap defaults, explicit escalation factors, mandatory legal minima and post-outcome learning.
- `CEREMONY_VS_PROPERTY`: The property is proportional control selection; a tailoring plan or approval board is not inherently required.
- `CURRENT_STATUS`: STRONGLY_RETAINED
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_STANDARD_AND_DOMAIN_CONVERGENCE
- `PRIMARY_SOURCES`: [S003](#source-s003), [S009](#source-s009), [S013](#source-s013), [S014](#source-s014), [S018](#source-s018), [S019](#source-s019), [S020](#source-s020), [S027](#source-s027), [S030](#source-s030)
- `CRITICAL_SOURCES`: [S045](#source-s045), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Multiple independent standards and regulatory regimes converge on tailoring/integrity/risk scaling; exact thresholds remain underdetermined.
- `OPEN_QUESTIONS`: How can trigger thresholds be calibrated and audited without recreating universal process?
- `REVERSIBILITY_PROFILE`: Meta-profile across R0–R4; establishes the cheap path and escalation.
- `LINEAGE_CLASSIFICATION`: DIRECT_LINEAGE; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p025"></a>
### EW-P025 — Rolling planning, estimate uncertainty and outside-view challenge

- `PROPERTY_ID`: EW-P025
- `PROPERTY_NAME`: Rolling planning, estimate uncertainty and outside-view challenge
- `HISTORICAL_ORIGIN`: Predictive programme planning, cost/schedule baselines, later empirical estimation research and reference-class forecasting.
- `ORIGINAL_FORM`: Detailed up-front work breakdown, deterministic schedule/cost baseline and variance control.
- `PROBLEM_IT_ADDRESSED`: Funding, suppliers and coordination require forecasts, but uncertain development cannot be represented honestly by one precise plan.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: False certainty, narrow intervals, political estimates, local optimism, plan treated as contract with reality, and continued funding because baseline sunk cost is large.
- `MECHANISM`: Use ranges, assumptions, scenarios, base rates/reference classes, independent estimates and rolling updates from actual performance; separate target, forecast and commitment.
- `TRIGGER_OR_CONTEXT`: Budget or contract decision; long lead; portfolio trade-off; external dependency; irreversible investment; capacity planning.
- `NON_TRIGGER_OR_CHEAP_PATH`: Small reversible work can use short-horizon forecasts and throughput history; avoid elaborate earned-value machinery.
- `DEPENDENCIES_OR_PRECONDITIONS`: Comparable data; transparent assumptions; incentives to report bad news; update cadence; distinction between estimate and target; independent challenge.
- `EXPECTED_ENGINEERING_PAYOFF`: More honest decisions, visible uncertainty, earlier replan and less surprise from deterministic commitments.
- `KNOWN_FAILURE_MODES`: Pseudo-precision; reference class chosen strategically; ranges ignored; baseline used to punish learning; constant replanning hides lack of progress.
- `IMPORTANT_CRITICISMS`: Estimation evidence is fragmented; outside views do not remove novelty or strategic behaviour; planning overhead may exceed value.
- `HOW_THE_PROPERTY_EVOLVED`: From fixed master plan to probabilistic, rolling and evidence-updated forecasts coupled to staged commitment.
- `MATURE_OR_EVOLVED_FORM`: A decision model that exposes uncertainty and changes with evidence, while retaining accountable external commitments where necessary.
- `CEREMONY_VS_PROPERTY`: The property is decision-relevant forecasting and uncertainty; a massive schedule, single completion date or mandated estimation method is not required.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_CRITICAL_LITERATURE_WEAK_UNIVERSAL_PREDICTION
- `PRIMARY_SOURCES`: [S051](#source-s051), [S052](#source-s052), [S053](#source-s053)
- `CRITICAL_SOURCES`: [S050](#source-s050), [S051](#source-s051)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Systematic review shows fragmented methods; uncertainty research documents overconfidence; GAO guidance requires risk, sensitivity, independent review and actuals.
- `OPEN_QUESTIONS`: Which estimation practices improve real decisions rather than reported calibration, especially in novel programmes?
- `REVERSIBILITY_PROFILE`: R2–R4 stronger because coordination/commitment needs forecasts; R0–R1 short-horizon lightweight.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; REFINED
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p026"></a>
### EW-P026 — Supplier, long-lead and dependency coordination

- `PROPERTY_ID`: EW-P026
- `PROPERTY_NAME`: Supplier, long-lead and dependency coordination
- `HISTORICAL_ORIGIN`: Aerospace/defence systems integration, acquisition/supply processes, interface/configuration management and production planning.
- `ORIGINAL_FORM`: Contract specifications, supplier reviews, data-item deliveries, interface boards and long-lead procurement approvals.
- `PROBLEM_IT_ADDRESSED`: Independent organisations and physical lead times create commitments and information boundaries that local team practices cannot dissolve.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Supplier builds to obsolete baseline; data rights missing; long-lead purchase before design maturity; integration mismatch; single-source obsolescence.
- `MECHANISM`: Identify external dependencies, owners, lead times, data/rights, interface and evidence obligations; synchronise baselines and stage procurement by demonstrated knowledge.
- `TRIGGER_OR_CONTEXT`: Multiple legal organisations/suppliers; custom hardware; long lead; scarce materials; safety evidence from vendors; sustainment dependence.
- `NON_TRIGGER_OR_CHEAP_PATH`: Single-team commodity/software dependencies can use lockfiles, service contracts, automated compatibility tests and normal vendor management.
- `DEPENDENCIES_OR_PRECONDITIONS`: Commercial/legal authority; accessible technical data; interface/configuration identity; supplier incentives; alternative/contingency analysis.
- `EXPECTED_ENGINEERING_PAYOFF`: Reduced integration and schedule surprise, clearer accountability, protected sustainment and less premature procurement commitment.
- `KNOWN_FAILURE_MODES`: Prime-contractor bureaucracy; data-item overload; supplier lock-in; approvals conceal poor technical visibility; local autonomy destroyed.
- `IMPORTANT_CRITICISMS`: Heavy supplier governance can reduce innovation and competition; requirements may be frozen to protect contracts.
- `HOW_THE_PROPERTY_EVOLVED`: Toward modular/open interfaces, digital data exchange, incremental contracts, shared evidence and risk-based supplier surveillance.
- `MATURE_OR_EVOLVED_FORM`: Govern external dependency commitments and evidence at the boundary, while minimising imposed internal process.
- `CEREMONY_VS_PROPERTY`: The property is cross-authority dependency control; supplier meetings, mandated data volumes and a universal prime/sub hierarchy are not inherently required.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_INSTITUTIONAL_SUPPORT
- `PRIMARY_SOURCES`: [S018](#source-s018), [S024](#source-s024), [S059](#source-s059), [S060](#source-s060)
- `CRITICAL_SOURCES`: [S017](#source-s017), [S038](#source-s038)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Complex acquisition audits and cross-case infrastructure/aerospace research show supplier, interface, data and long-lead exposure; causal isolation is difficult.
- `OPEN_QUESTIONS`: Which contract and data-right structures preserve learning without transferring uncontrolled risk?
- `REVERSIBILITY_PROFILE`: R3–R4 primary; R2 for external cloud/services; R0–R1 usually cheap.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; CONVERGENT_ENGINEERING
- `RELATION_TO_ADAPTIVE_METHODS`: CONTEXT_SWITCH

<a id="property-ew-p027"></a>
### EW-P027 — Transition, operational readiness and cutover control

- `PROPERTY_ID`: EW-P027
- `PROPERTY_NAME`: Transition, operational readiness and cutover control
- `HISTORICAL_ORIGIN`: Installation/checkout, acceptance, flight/mission readiness reviews, commissioning and transition-to-service practice.
- `ORIGINAL_FORM`: Formal operational readiness review before launch, startup, fielding or handover.
- `PROBLEM_IT_ADDRESSED`: A technically verified product can fail because deployment, data, people, procedures, support or operational authority are unready.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Successful component/system test followed by failed cutover, unsafe startup, missing support, wrong configuration or untrained operators.
- `MECHANISM`: Evaluate the actual deployment configuration, environment, data, people, procedures, support, unresolved anomalies and authority; rehearse critical transitions.
- `TRIGGER_OR_CONTEXT`: Irreversible or high-impact cutover; physical startup; safety/mission operations; major migration; transfer to a separate operations organisation.
- `NON_TRIGGER_OR_CHEAP_PATH`: Small reversible deployments can use automated readiness checks, canaries and on-call confirmation without a review meeting.
- `DEPENDENCIES_OR_PRECONDITIONS`: As-deployed identity; rollback/contingency; operational owner; realistic rehearsal; support resources; decision authority.
- `EXPECTED_ENGINEERING_PAYOFF`: Fewer transition failures, clearer operational ownership, verified support and safer startup.
- `KNOWN_FAILURE_MODES`: Checklist meeting after deployment decision; nominal training; staged demo; readiness package detached from live environment; issues accepted by schedule pressure.
- `IMPORTANT_CRITICISMS`: Readiness reviews can batch releases and become sign-off theatre; continuous services may never have a single transition moment.
- `HOW_THE_PROPERTY_EVOLVED`: From one handover event to progressive delivery, rehearsed migration waves, automated readiness evidence and continuous operational acceptance.
- `MATURE_OR_EVOLVED_FORM`: A risk-scaled decision that actual capability and enabling system are ready, with explicit rollback and residual-risk authority.
- `CEREMONY_VS_PROPERTY`: The property is actual operational readiness; an ORR meeting, slide deck or ceremonial handover is not required.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_AND_FAILURE_MECHANISM_SUPPORT
- `PRIMARY_SOURCES`: [S022](#source-s022), [S032](#source-s032), [S057](#source-s057), [S035](#source-s035)
- `CRITICAL_SOURCES`: [S017](#source-s017), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: NASA and DOE explicitly require correspondence among actual system, people, procedures and deployed state before operation in high-consequence contexts.
- `OPEN_QUESTIONS`: How should continuous services represent readiness when deployment is frequent and partial?
- `REVERSIBILITY_PROFILE`: R2–R4; strength rises with cutover irreversibility, data effects, hazard and recovery time.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; DOMAIN_SPECIFIC; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p028"></a>
### EW-P028 — Rollback, contingency and recovery readiness

- `PROPERTY_ID`: EW-P028
- `PROPERTY_NAME`: Rollback, contingency and recovery readiness
- `HISTORICAL_ORIGIN`: Contingency planning, mission abort/backup, disaster recovery and modern progressive-delivery practice.
- `ORIGINAL_FORM`: Contingency plans, backup systems and recovery procedures prepared before operation.
- `PROBLEM_IT_ADDRESSED`: Some failures cannot be prevented economically; control value depends on whether damage can be contained and service restored.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Change is labelled reversible but rollback loses data, worsens hazard, depends on unavailable people/tools or has never been tested.
- `MECHANISM`: Define recovery objectives, backups, fallback/abort paths, state reconciliation and decision authority; test them under representative conditions.
- `TRIGGER_OR_CONTEXT`: Operational/data change; service dependency; cyber threat; migration; remote/physical operation; significant outage or safety consequence.
- `NON_TRIGGER_OR_CHEAP_PATH`: Truly stateless low-impact experiments may need only one-click revert and normal version history.
- `DEPENDENCIES_OR_PRECONDITIONS`: Known state model; backups/alternate capability; observability; access; rehearsals; ownership; time and safety limits.
- `EXPECTED_ENGINEERING_PAYOFF`: Reduced failure/recovery cost, safer experimentation, bounded outages and honest reversibility classification.
- `KNOWN_FAILURE_MODES`: Untested plan; backup corrupt or inaccessible; rollback incompatible with migrated data; fallback shares same failure; recovery metrics unrealistic.
- `IMPORTANT_CRITICISMS`: Redundancy and rehearsal cost can be high; fallback can increase complexity and attack surface.
- `HOW_THE_PROPERTY_EVOLVED`: From static disaster-recovery binders to automated rollback, canary/progressive delivery, chaos exercises and continuously tested recovery.
- `MATURE_OR_EVOLVED_FORM`: Demonstrated recovery capability whose evidence is tied to the current architecture, data and operational configuration.
- `CEREMONY_VS_PROPERTY`: The property is working recoverability; a contingency document, checkbox backup or claimed rollback is not enough.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_RESILIENCE_PRACTICE_SUPPORT
- `PRIMARY_SOURCES`: [S056](#source-s056), [S035](#source-s035), [S036](#source-s036)
- `CRITICAL_SOURCES`: [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: NIST and modern delivery practice require recovery strategies and tests; comparative thresholds are context-specific.
- `OPEN_QUESTIONS`: How should recovery tests cover correlated and irreversible data/physical effects?
- `REVERSIBILITY_PROFILE`: Central to classifying R1–R3; R4 often cannot be rolled back and needs prevention/containment instead.
- `LINEAGE_CLASSIFICATION`: CONVERGENT_ENGINEERING; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p029"></a>
### EW-P029 — Sustainment, obsolescence and support continuity

- `PROPERTY_ID`: EW-P029
- `PROPERTY_NAME`: Sustainment, obsolescence and support continuity
- `HISTORICAL_ORIGIN`: Full-lifecycle systems engineering, logistics/product support, configuration management and maintenance.
- `ORIGINAL_FORM`: Logistics support plans, technical manuals, spares, depot arrangements and periodic sustainment reviews.
- `PROBLEM_IT_ADDRESSED`: Delivery/acceptance is not the end of system life; support data, skills, suppliers and components decay.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Unsupportable fielded system, obsolete components, missing data rights, unknown fleet configurations, cost growth invisible without baseline.
- `MECHANISM`: Plan and monitor support concept, technical data, configuration fleet state, skills, obsolescence, supply chain, service levels and retirement; update from operations.
- `TRIGGER_OR_CONTEXT`: Long-lived asset; fleet; regulated/safety system; custom hardware; external supplier; high replacement/cutover cost.
- `NON_TRIGGER_OR_CHEAP_PATH`: Short-lived commodity software can rely on maintained dependencies, observability and explicit end-of-life policy.
- `DEPENDENCIES_OR_PRECONDITIONS`: Lifecycle ownership/funding; operational data; configuration baseline; supplier/data rights; retirement authority.
- `EXPECTED_ENGINEERING_PAYOFF`: Higher availability, controlled lifecycle cost, safer maintenance, upgradeability and deliberate retirement.
- `KNOWN_FAILURE_MODES`: Support plan written before real operations; cost baseline absent; sustainment deferred to future owner; vendor lock-in; obsolete documentation.
- `IMPORTANT_CRITICISMS`: Long-range sustainment plans are highly uncertain and may entrench legacy systems; review metrics can be gamed.
- `HOW_THE_PROPERTY_EVOLVED`: From static logistics plans to telemetry-informed product support, modular/open systems, continuous patching and explicit decommissioning.
- `MATURE_OR_EVOLVED_FORM`: Through-life ownership and evidence for maintaining, modifying and retiring the actual fielded configuration.
- `CEREMONY_VS_PROPERTY`: The property is continuing capability and authority; a logistics document or annual review alone is not sufficient.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_CURRENT_AUDIT_SUPPORT
- `PRIMARY_SOURCES`: [S018](#source-s018), [S022](#source-s022), [S029](#source-s029), [S058](#source-s058), [S060](#source-s060)
- `CRITICAL_SOURCES`: [S058](#source-s058)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: GAO reports show missing sustainment baselines can prevent cost-growth determination and identify obsolescence/supply problems.
- `OPEN_QUESTIONS`: Which early design/supplier controls reliably reduce lifecycle cost without locking in speculative forecasts?
- `REVERSIBILITY_PROFILE`: R3–R4 primary; R2 for durable platforms/services; R0–R1 minimal.
- `LINEAGE_CLASSIFICATION`: RELATED_PLAN_DRIVEN_TRADITION; DOMAIN_SPECIFIC; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONVERGENT_PROPERTY

<a id="property-ew-p030"></a>
### EW-P030 — Digital authoritative engineering environment and model governance

- `PROPERTY_ID`: EW-P030
- `PROPERTY_NAME`: Digital authoritative engineering environment and model governance
- `HISTORICAL_ORIGIN`: Technical-data management, CAD/CAE, MBSE, digital engineering and authoritative-source initiatives.
- `ORIGINAL_FORM`: Replace or supplement document sets with integrated models and a designated authoritative source of truth.
- `PROBLEM_IT_ADDRESSED`: Disconnected documents and tools produce handoff loss, duplicate data and inconsistent views of system state.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Different disciplines act on incompatible models; model is stale or unvalidated; authority is ambiguous; proprietary tool blocks access; model approval substitutes for reality.
- `MECHANISM`: Govern authoritative data/model domains, semantics, ownership, versioning, validation, interoperability, access and reconciliation to built/deployed state.
- `TRIGGER_OR_CONTEXT`: Many disciplines/models; complex interfaces; long lifecycle; supplier data exchange; expensive manual consistency checking.
- `NON_TRIGGER_OR_CHEAP_PATH`: Small software products can use source, tests, schemas and deployment manifests as native authoritative artefacts without an MBSE platform.
- `DEPENDENCIES_OR_PRECONDITIONS`: Clear authority boundaries; common identifiers/semantics; tool interoperability; model validation; configuration management; culture/workflow adoption; physical readback.
- `EXPECTED_ENGINEERING_PAYOFF`: Earlier consistency checks, reusable data, reduced handoff duplication, computational analysis and more current evidence.
- `KNOWN_FAILURE_MODES`: 'Single source of truth' slogan; federated models silently disagree; visual completeness; vendor lock-in; access barriers; model/data debt.
- `IMPORTANT_CRITICISMS`: Systematic reviews find many benefits are perceived rather than measured; digital models can become more opaque ceremony than documents.
- `HOW_THE_PROPERTY_EVOLVED`: From one central database ideal to governed federations of authoritative sources, digital threads and explicit confidence/reconciliation.
- `MATURE_OR_EVOLVED_FORM`: A configuration-controlled, queryable engineering evidence environment with scoped authority and verified correspondence to reality.
- `CEREMONY_VS_PROPERTY`: The property is governed authoritative information and consistency; buying an MBSE tool, drawing SysML or declaring an ASoT is not the property.
- `CURRENT_STATUS`: USEFUL_BUT_EASILY_BUREAUCRATISED
- `EVIDENCE_STRENGTH`: C_MIXED_EMPIRICAL_AND_PRACTICE_EVIDENCE
- `PRIMARY_SOURCES`: [S037](#source-s037), [S038](#source-s038), [S039](#source-s039), [S040](#source-s040)
- `CRITICAL_SOURCES`: [S038](#source-s038), [S039](#source-s039)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Reviews report many claimed benefits but sparse measured comparisons; government-sponsored work identifies authority, interoperability and cultural failure modes.
- `OPEN_QUESTIONS`: What measurable decision/outcome improvements justify model cost, and how should confidence and physical/deployed divergence be represented?
- `REVERSIBILITY_PROFILE`: R2–R4 more likely to justify investment; R0–R1 usually native code/data tools.
- `LINEAGE_CLASSIFICATION`: CONVERGENT_ENGINEERING; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p031"></a>
### EW-P031 — Continuous integration, automated evidence and continuous assurance

- `PROPERTY_ID`: EW-P031
- `PROPERTY_NAME`: Continuous integration, automated evidence and continuous assurance
- `HISTORICAL_ORIGIN`: Incremental development, software configuration management, CI/CD, DevSecOps and continuous authorisation.
- `ORIGINAL_FORM`: Periodic builds, formal test campaigns and manually assembled evidence packages at release gates.
- `PROBLEM_IT_ADDRESSED`: Late integration and episodic assurance delay defects and make evidence stale relative to rapidly changing software.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Assurance package proves an old build; integration errors accumulate; security/operational feedback arrives after release; manual evidence cannot keep pace.
- `MECHANISM`: Continuously integrate identified configurations, run risk-relevant automated evaluation, preserve provenance, monitor operations and feed evidence to promotion/authority decisions.
- `TRIGGER_OR_CONTEXT`: Frequent software change; automatable tests; digital deployment; cyber threat; many integrations; need for rapid remediation.
- `NON_TRIGGER_OR_CHEAP_PATH`: Where deployment is rare/physical and tests cannot be automated, use periodic integration but automate provenance and repeatable analyses where possible.
- `DEPENDENCIES_OR_PRECONDITIONS`: Reliable tests and environments; reproducible builds; secure pipeline; evidence semantics; observability; segregation/authority where needed; human review of non-automatable claims.
- `EXPECTED_ENGINEERING_PAYOFF`: Shorter feedback, less stale evidence, faster safe delivery and reuse of test/compliance results.
- `KNOWN_FAILURE_MODES`: Fast pipeline for wrong tests; flaky suites; automation monoculture; compromised pipeline; dashboard theatre; production monitoring used to justify under-testing.
- `IMPORTANT_CRITICISMS`: CI/CD empirical evidence is heterogeneous; continuous does not mean complete, independent or certified, and infrastructure cost can be large.
- `HOW_THE_PROPERTY_EVOLVED`: Plan-driven evidence obligations are generated continuously and attached to immutable releases; independent and regulatory decisions consume rather than recreate evidence.
- `MATURE_OR_EVOLVED_FORM`: Continuous, configuration-linked evidence with explicit coverage limits, risk gates, monitoring and human/independent authority at consequential boundaries.
- `CEREMONY_VS_PROPERTY`: The property is fresh reproducible evidence and rapid integration; a branded DevSecOps platform, dashboard or 'continuous compliance' claim is not enough.
- `CURRENT_STATUS`: RETAINED_IN_EVOLVED_FORM
- `EVIDENCE_STRENGTH`: B_STRONG_MODERN_GUIDANCE_MIXED_EMPIRICAL_OUTCOMES
- `PRIMARY_SOURCES`: [S026](#source-s026), [S034](#source-s034), [S035](#source-s035), [S036](#source-s036), [S054](#source-s054), [S055](#source-s055)
- `CRITICAL_SOURCES`: [S039](#source-s039), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: DoD and RTCA explicitly combine iterative delivery with baselines/evidence/independence; systematic reviews report benefits and recurring technical/organisational constraints.
- `OPEN_QUESTIONS`: Which assurance claims can safely be automated, and how should evidence independence and tool qualification be handled?
- `REVERSIBILITY_PROFILE`: R1–R3 strongest for software; supports R4 evidence but cannot remove physical/certification constraints.
- `LINEAGE_CLASSIFICATION`: HYBRID; ADAPTIVE_IMPORT; CONVERGENT_ENGINEERING
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p032"></a>
### EW-P032 — Risk ownership, residual-risk decision and operational authority

- `PROPERTY_ID`: EW-P032
- `PROPERTY_NAME`: Risk ownership, residual-risk decision and operational authority
- `HISTORICAL_ORIGIN`: Safety cases, acquisition decision authority, acceptance/certification, nuclear readiness and ATO/cATO.
- `ORIGINAL_FORM`: Named programme manager, safety authority, certification authority or operational commander signs risk/acceptance decision.
- `PROBLEM_IT_ADDRESSED`: Evidence cannot eliminate all uncertainty; someone empowered and accountable must decide whether remaining risk is tolerable for a specific use/configuration.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Risk implicitly accepted by developers, responsibility diffused, authority signs without evidence, or operation continues outside approved context.
- `MECHANISM`: Name risk owners and decision authority; state scope/configuration, residual risk, conditions, expiry and monitoring; separate evidence production from acceptance where warranted.
- `TRIGGER_OR_CONTEXT`: Material safety, security, privacy, mission, financial or public risk; operation beyond local team; conditional/temporary approval.
- `NON_TRIGGER_OR_CHEAP_PATH`: Low-consequence reversible changes can operate under pre-authorised risk tolerances with automated monitoring.
- `DEPENDENCIES_OR_PRECONDITIONS`: Authority actually controls operation/resources; current evidence; transparent criteria; escalation/stop power; operational monitoring; independence where needed.
- `EXPECTED_ENGINEERING_PAYOFF`: Clear accountability, explicit residuals, bounded authority and faster action when conditions change.
- `KNOWN_FAILURE_MODES`: Signature shield; authority too remote; risk language vague; ownership without power; permanent temporary waivers; risk accepted after de facto deployment.
- `IMPORTANT_CRITICISMS`: Individual sign-off can centralise power, encourage blame and add latency; no authority can make unknown risk safe by declaration.
- `HOW_THE_PROPERTY_EVOLVED`: From episodic approval to bounded, revocable and continuously informed authority with delegated tolerances.
- `MATURE_OR_EVOLVED_FORM`: Configuration- and context-specific authority that consumes fresh evidence, records residual risk and can stop or constrain operation.
- `CEREMONY_VS_PROPERTY`: The property is accountable authority over real operation; a signature block or governance title alone is not enough.
- `CURRENT_STATUS`: HIGH_CONSEQUENCE_CONTEXT_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_DOMAIN_AUTHORITY_SUPPORT
- `PRIMARY_SOURCES`: [S030](#source-s030), [S031](#source-s031), [S032](#source-s032), [S033](#source-s033), [S036](#source-s036)
- `CRITICAL_SOURCES`: [S050](#source-s050)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Rail, nuclear, defence safety and cATO schemes all preserve explicit independent/operational risk authority while varying cadence and form.
- `OPEN_QUESTIONS`: How should authority be distributed to preserve speed while preventing conflicted self-approval?
- `REVERSIBILITY_PROFILE`: R2–R4 according to consequence; R0–R1 usually delegated tolerances.
- `LINEAGE_CLASSIFICATION`: DOMAIN_SPECIFIC; RELATED_PLAN_DRIVEN_TRADITION; HYBRID
- `RELATION_TO_ADAPTIVE_METHODS`: CONTEXT_SWITCH

<a id="property-ew-p033"></a>
### EW-P033 — Reversibility- and commitment-sensitive control strength

- `PROPERTY_ID`: EW-P033
- `PROPERTY_NAME`: Reversibility- and commitment-sensitive control strength
- `HISTORICAL_ORIGIN`: Royce late-integration argument; spiral risk; graded nuclear/rail/medical assurance; modern continuous delivery and recovery practice.
- `ORIGINAL_FORM`: Increase formality by project phase, size or prescribed safety class, often using a presumed rising cost-of-change curve.
- `PROBLEM_IT_ADDRESSED`: Neither universal heavy control nor universal rapid change is rational: the value of evidence and authority depends on what can be undone and what harm can occur.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Over-control cheap experiments; under-control irreversible/public changes; confuse edit cost with propagation, commitment-unwind or failure/recovery cost.
- `MECHANISM`: Classify a decision/change by consequence, reversibility/recovery, coupling, observability latency, external commitment, test scarcity and adversarial urgency; select the least burdensome control that closes the failure mode.
- `TRIGGER_OR_CONTEXT`: This is a meta-property applied whenever choosing baseline, trace, review, independence, qualification or authorisation strength.
- `NON_TRIGGER_OR_CHEAP_PATH`: Default pre-authorised path for local, low-consequence, rapidly observable and genuinely reversible work.
- `DEPENDENCIES_OR_PRECONDITIONS`: Operational definition of reversibility; tested recovery; impact visibility; clear thresholds; feedback on false positives/negatives; legal minima.
- `EXPECTED_ENGINEERING_PAYOFF`: Controls concentrate where mistakes are costly while preserving learning and flow elsewhere.
- `KNOWN_FAILURE_MODES`: Risk scoring theatre; reversibility claimed without data/side-effect analysis; consequence ignored because rollback is easy; all high-risk work receives every control; thresholds manipulated.
- `IMPORTANT_CRITICISMS`: Evidence does not support one universal monotonic formula; irreversible systems can still be harmed by bureaucracy, and reversible software can create irreversible disclosure or transaction effects.
- `HOW_THE_PROPERTY_EVOLVED`: From calendar-phase severity and universal late-change curves to multidimensional commitment/risk profiles and dynamic evidence.
- `MATURE_OR_EVOLVED_FORM`: A falsifiable control-selection policy: identify the failure mode, trigger dimensions, cheap path, required evidence and residual risk; re-evaluate after operational feedback.
- `CEREMONY_VS_PROPERTY`: The property is proportional selection tied to a real failure mode; a risk matrix, phase label or 'high assurance' designation is not sufficient.
- `CURRENT_STATUS`: CONTEXT_DEPENDENT
- `EVIDENCE_STRENGTH`: B_STRONG_CROSS_DOMAIN_CONVERGENCE_THRESHOLD_UNRESOLVED
- `PRIMARY_SOURCES`: [S003](#source-s003), [S008](#source-s008), [S027](#source-s027), [S030](#source-s030), [S031](#source-s031), [S047](#source-s047), [S048](#source-s048)
- `CRITICAL_SOURCES`: [S048](#source-s048), [S045](#source-s045)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: High-consequence domains scale controls by safety/risk significance; Menzies et al. refute a universal delayed-software-defect law; aerospace-like systems show large but variable commitment costs.
- `OPEN_QUESTIONS`: No validated general threshold function exists. Domain-specific calibration, interactions and automation effects remain unresolved.
- `REVERSIBILITY_PROFILE`: Meta-profile R0–R4; consequence, coupling and irreversible effects can override technical rollback.
- `LINEAGE_CLASSIFICATION`: HISTORICAL_INFERENCE; HYBRID; CONVERGENT_ENGINEERING
- `RELATION_TO_ADAPTIVE_METHODS`: HYBRID_RESOLUTION

<a id="property-ew-p034"></a>
### EW-P034 — Fixed one-pass lifecycle sequencing

- `PROPERTY_ID`: EW-P034
- `PROPERTY_NAME`: Fixed one-pass lifecycle sequencing
- `HISTORICAL_ORIGIN`: Later simplifications of staged development and some real contract/organisation implementations.
- `ORIGINAL_FORM`: Requirements complete, then design complete, then implementation, then testing, with phases closed against return.
- `PROBLEM_IT_ADDRESSED`: Attempted to create management order and contractual predictability in large projects.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Its own failure mode is late feedback, late integration, frozen error, handoff loss and inability to learn.
- `MECHANISM`: Predetermine one global phase order and treat return as exception.
- `TRIGGER_OR_CONTEXT`: No general trigger established; logical dependencies may exist, but they do not justify one global calendar sequence.
- `NON_TRIGGER_OR_CHEAP_PATH`: Use iterative, concurrent and recursive lifecycle obligations; preserve only real dependency/commitment order.
- `DEPENDENCIES_OR_PRECONDITIONS`: Would require stable complete knowledge and negligible learning value—conditions rarely true for non-trivial novel development.
- `EXPECTED_ENGINEERING_PAYOFF`: Can simplify scheduling for genuinely repeatable production, but that is production planning rather than a general development lifecycle.
- `KNOWN_FAILURE_MODES`: All canonical sequentiality failures; local phase completion without system evidence; change suppression.
- `IMPORTANT_CRITICISMS`: Royce himself called the unmodified form risky; current ISO standards do not prescribe it; empirical cases show requirements/testing/handoff problems.
- `HOW_THE_PROPERTY_EVOLVED`: Rejected as a universal development model; replaced by tailored iterative/incremental lifecycles and event-driven commitments.
- `MATURE_OR_EVOLVED_FORM`: No mature general form. Preserve actual causal dependencies and commitment boundaries, not the phase diagram.
- `CEREMONY_VS_PROPERTY`: The Waterfall diagram is not a surviving engineering property.
- `CURRENT_STATUS`: REJECTED_OR_DISFAVOURED
- `EVIDENCE_STRENGTH`: A_STRONG_HISTORICAL_STANDARDS_AND_CRITICAL_SUPPORT
- `PRIMARY_SOURCES`: [S003](#source-s003), [S018](#source-s018), [S019](#source-s019)
- `CRITICAL_SOURCES`: [S006](#source-s006), [S016](#source-s016), [S017](#source-s017)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Historical sources and current standards reject the universal one-pass interpretation; deployed sequential practice produced documented failures.
- `OPEN_QUESTIONS`: A narrow repeat-production context may still have ordered work, but that does not rehabilitate the development caricature.
- `REVERSIBILITY_PROFILE`: No general profile; harmful especially where uncertainty and feedback value are high.
- `LINEAGE_CLASSIFICATION`: LATER_TEXTBOOK_CARICATURE; REAL_DEPLOYED_PRACTICE
- `RELATION_TO_ADAPTIVE_METHODS`: REJECTED

<a id="property-ew-p035"></a>
### EW-P035 — Complete up-front requirements as a precondition to development

- `PROPERTY_ID`: EW-P035
- `PROPERTY_NAME`: Complete up-front requirements as a precondition to development
- `HISTORICAL_ORIGIN`: Contractual specification practices and simplified Waterfall pedagogy.
- `ORIGINAL_FORM`: Freeze a complete requirement set before architecture, implementation or user feedback.
- `PROBLEM_IT_ADDRESSED`: Attempted to bound scope and enable contract, design and test planning.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Wrong or unknowable requirements become authoritative; learning is treated as non-compliance; validation arrives too late.
- `MECHANISM`: Delay implementation/evidence until requirement completeness is declared.
- `TRIGGER_OR_CONTEXT`: No general development trigger; externally imposed fixed obligations may be baselined, but unknowns must remain explicit.
- `NON_TRIGGER_OR_CHEAP_PATH`: Baseline only stable constraints and next-decision intent; use prototypes and incremental validation for uncertain needs.
- `DEPENDENCIES_OR_PRECONDITIONS`: Would require a stable environment, fully knowable need and negligible feedback value.
- `EXPECTED_ENGINEERING_PAYOFF`: May aid repeat procurement against a mature product, but not novel development.
- `KNOWN_FAILURE_MODES`: False completeness, requirement churn hidden as defects, costly contract changes, specification–implementation divergence.
- `IMPORTANT_CRITICISMS`: Contradicted by Bell–Thayer, Parnas/Clements, Brooks, spiral and modern lifecycle standards.
- `HOW_THE_PROPERTY_EVOLVED`: Superseded by authoritative but revisable requirements plus explicit uncertainty and staged commitment.
- `MATURE_OR_EVOLVED_FORM`: EW-P001 and EW-P002 replace this candidate.
- `CEREMONY_VS_PROPERTY`: A requirements-complete gate or giant signed specification is not a general property.
- `CURRENT_STATUS`: REJECTED_OR_DISFAVOURED
- `EVIDENCE_STRENGTH`: A_STRONG_HISTORICAL_AND_CRITICAL_SUPPORT
- `PRIMARY_SOURCES`: [S004](#source-s004), [S006](#source-s006), [S007](#source-s007), [S008](#source-s008)
- `CRITICAL_SOURCES`: [S016](#source-s016), [S017](#source-s017)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Historical and empirical sources repeatedly document requirement learning after development begins.
- `OPEN_QUESTIONS`: Stable regulatory or interface constraints remain real; the rejected claim is completeness as a universal prerequisite.
- `REVERSIBILITY_PROFILE`: Most harmful before R0–R2 learning; stable R3–R4 obligations still require controlled change rather than fictional completeness.
- `LINEAGE_CLASSIFICATION`: LATER_TEXTBOOK_CARICATURE; REAL_DEPLOYED_PRACTICE
- `RELATION_TO_ADAPTIVE_METHODS`: REJECTED

<a id="property-ew-p036"></a>
### EW-P036 — Document-completion phase gates and fixed review ceremonies

- `PROPERTY_ID`: EW-P036
- `PROPERTY_NAME`: Document-completion phase gates and fixed review ceremonies
- `HISTORICAL_ORIGIN`: Formal design reviews, procurement milestones and Stage-Gate implementations.
- `ORIGINAL_FORM`: Named board/meeting at a calendar phase approves a prescribed document set.
- `PROBLEM_IT_ADDRESSED`: Attempted to create oversight and prevent premature progression.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Documents pass while system evidence is weak; milestone gaming; batch latency; decision already irreversible.
- `MECHANISM`: Use document completion and meeting approval as proxy for readiness.
- `TRIGGER_OR_CONTEXT`: No general trigger for the artefact; only EW-P021's underlying commitment decision may trigger.
- `NON_TRIGGER_OR_CHEAP_PATH`: Asynchronous evidence review, automated policy gates or no gate where no consequential commitment exists.
- `DEPENDENCIES_OR_PRECONDITIONS`: For any benefit, a real decision, stop authority and discriminating evidence would be required—turning it into EW-P021.
- `EXPECTED_ENGINEERING_PAYOFF`: Can convene cross-disciplinary attention, but the meeting/document form has no independent general payoff.
- `KNOWN_FAILURE_MODES`: Slideware, rubber stamp, duplicate governance, sunk-cost escalation, calendar pressure.
- `IMPORTANT_CRITICISMS`: NRC/GAO and Stage-Gate's own evolution recognise linearity and bureaucracy.
- `HOW_THE_PROPERTY_EVOLVED`: Superseded by event-driven, evidence-backed and risk-proportional commitment decisions.
- `MATURE_OR_EVOLVED_FORM`: EW-P021; the fixed ceremony itself is not retained.
- `CEREMONY_VS_PROPERTY`: This candidate is the ceremony, not the property.
- `CURRENT_STATUS`: CEREMONY_NOT_GENERAL_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_CRITICAL_AND_EVOLUTIONARY_SUPPORT
- `PRIMARY_SOURCES`: [S037](#source-s037), [S049](#source-s049)
- `CRITICAL_SOURCES`: [S017](#source-s017), [S050](#source-s050)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Institutional reviews and Stage-Gate evolution document gate bureaucracy and milestone pathologies.
- `OPEN_QUESTIONS`: Some high-consequence decisions still benefit from synchronous challenge; format remains contextual.
- `REVERSIBILITY_PROFILE`: Only justified indirectly at R3–R4 commitments, never merely by phase/calendar.
- `LINEAGE_CLASSIFICATION`: REAL_DEPLOYED_PRACTICE; CEREMONIAL_COMPLIANCE
- `RELATION_TO_ADAPTIVE_METHODS`: REPLACED

<a id="property-ew-p037"></a>
### EW-P037 — Uniform exhaustive manual traceability and central change-board control

- `PROPERTY_ID`: EW-P037
- `PROPERTY_NAME`: Uniform exhaustive manual traceability and central change-board control
- `HISTORICAL_ORIGIN`: Document-heavy defence/regulated implementations of traceability and configuration control.
- `ORIGINAL_FORM`: Trace every artefact to every neighbouring artefact in spreadsheets and route every baseline change through a standing CCB.
- `PROBLEM_IT_ADDRESSED`: Attempted to guarantee coverage, impact visibility and authority.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Link decay, matrix maintenance burden, rubber-stamp approval, workarounds, delayed remediation and false completeness.
- `MECHANISM`: Maximise explicit links and central approvals regardless of consequence or reversibility.
- `TRIGGER_OR_CONTEXT`: No general trigger; selective traceability and risk-proportional authorisation survive separately as EW-P017 and EW-P008.
- `NON_TRIGGER_OR_CHEAP_PATH`: Native version/test/dependency links and pre-authorised change paths for reversible work.
- `DEPENDENCIES_OR_PRECONDITIONS`: Would require low maintenance cost and uniformly high consequence, conditions not generally present.
- `EXPECTED_ENGINEERING_PAYOFF`: May provide coverage in a bounded certification scope, but exhaustive/manual/central form is not independently justified.
- `KNOWN_FAILURE_MODES`: Stale links, approval queues, change avoidance, link-count compliance, authority disconnected from actual deployment.
- `IMPORTANT_CRITICISMS`: Traceability studies expose maintenance cost and ideal-link assumptions; nuclear practice itself uses graded change thresholds.
- `HOW_THE_PROPERTY_EVOLVED`: Replaced by selective automated relations, policy-based promotion and risk-triggered escalation.
- `MATURE_OR_EVOLVED_FORM`: EW-P008 and EW-P017.
- `CEREMONY_VS_PROPERTY`: Manual matrix and standing board are artefacts, not universal properties.
- `CURRENT_STATUS`: CEREMONY_NOT_GENERAL_PROPERTY
- `EVIDENCE_STRENGTH`: A_STRONG_MIXED_EMPIRICAL_AND_DOMAIN_SUPPORT
- `PRIMARY_SOURCES`: [S031](#source-s031), [S041](#source-s041), [S042](#source-s042), [S044](#source-s044)
- `CRITICAL_SOURCES`: [S044](#source-s044), [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Traceability has task benefits under good links, but maintenance is its main cost; graded nuclear change control disproves universal prior approval.
- `OPEN_QUESTIONS`: Certain certification schemas may still require dense explicit traces; the general artefact claim remains rejected.
- `REVERSIBILITY_PROFILE`: Disproportionate in R0–R1; selective value rises R2–R4.
- `LINEAGE_CLASSIFICATION`: REAL_DEPLOYED_PRACTICE; CEREMONIAL_COMPLIANCE
- `RELATION_TO_ADAPTIVE_METHODS`: REPLACED

<a id="property-ew-p038"></a>
### EW-P038 — Universal exponential late-change cost rule

- `PROPERTY_ID`: EW-P038
- `PROPERTY_NAME`: Universal exponential late-change cost rule
- `HISTORICAL_ORIGIN`: Popularised lifecycle cost-of-change curves and retrospective defect-cost claims.
- `ORIGINAL_FORM`: Assume every change or defect becomes exponentially more expensive with each later phase, justifying maximal up-front control.
- `PROBLEM_IT_ADDRESSED`: Attempted to motivate early defect prevention and planning.
- `FAILURE_MODE_IT_TRIES_TO_PREVENT`: Misallocates control, discourages cheap late improvement, confuses code edit with propagation, commitment-unwind and failure/recovery cost.
- `MECHANISM`: Use calendar lateness or phase as a universal proxy for change cost.
- `TRIGGER_OR_CONTEXT`: None; context-specific commitment and consequence evidence must be measured instead.
- `NON_TRIGGER_OR_CHEAP_PATH`: Assess edit, propagation, commitment-unwind and failure/recovery cost separately.
- `DEPENDENCIES_OR_PRECONDITIONS`: A universal law would require stable cross-domain cost definitions and effects, which evidence does not supply.
- `EXPECTED_ENGINEERING_PAYOFF`: The warning is directionally useful in some hardware/certification contexts, but the universal curve is false.
- `KNOWN_FAILURE_MODES`: BDUF, sunk-cost protection, avoidance of beneficial change, inflated process burden.
- `IMPORTANT_CRITICISMS`: Aerospace-like studies show large but wildly variable escalation; 171 software projects found no consistent substantial delayed-issue effect.
- `HOW_THE_PROPERTY_EVOLVED`: Replaced by EW-P033's multidimensional reversibility/commitment profile.
- `MATURE_OR_EVOLVED_FORM`: No universal curve; use domain-specific evidence and tested recovery.
- `CEREMONY_VS_PROPERTY`: Citing a generic cost curve is not engineering evidence for a control.
- `CURRENT_STATUS`: REJECTED_OR_DISFAVOURED
- `EVIDENCE_STRENGTH`: A_STRONG_DIRECT_COUNTEREVIDENCE_TO_UNIVERSALITY
- `PRIMARY_SOURCES`: [S047](#source-s047), [S048](#source-s048)
- `CRITICAL_SOURCES`: [S048](#source-s048)
- `EMPIRICAL_OR_DOMAIN_EVIDENCE`: Haskins et al. support escalation in aerospace-like systems with multipliers varying from 29 to over 1,500 by method; Menzies et al. reject a global software effect.
- `OPEN_QUESTIONS`: Domain-specific thresholds remain open and are retained under EW-P033.
- `REVERSIBILITY_PROFILE`: Replaced by R0–R4 profiles; calendar phase alone is not a trigger.
- `LINEAGE_CLASSIFICATION`: LATER_SIMPLIFICATION; PREDICTIVE_ESTIMATION
- `RELATION_TO_ADAPTIVE_METHODS`: REJECTED

# EVOLVED_WATERFALL_CEREMONY_STRIPPING_LEDGER

| PRACTICE_OR_ARTEFACT | UNDERLYING_PROPERTY | WHAT_IT_BUYS | WHEN_IT_FAILS | WHETHER_THE_ARTEFACT_IS_REQUIRED | ALTERNATIVE_IMPLEMENTATIONS | MODERN_DISPOSITION |
| --- | --- | --- | --- | --- | --- | --- |
| Giant requirements specification | EW-P001 authoritative revisable intent | A shared basis for design, contract and verification. | Volume hides uncertainty; stale document outranks reality; readers cannot find governing detail. | NO | Structured requirements data, executable examples, models, versioned decisions, smaller specifications. | Retain authority and versioning; reject document size as evidence. |
| Requirements-complete gate | EW-P001 plus EW-P002 | A declared scope boundary. | Unknowns are relabelled as settled and later learning becomes non-compliance. | NO_GENERAL_PROPERTY | Baseline stable obligations; mark hypotheses and next evidence explicitly. | REJECTED_OR_DISFAVOURED. |
| Preliminary/Critical Design Review meeting | EW-P003 and EW-P021 | Cross-disciplinary challenge before commitment. | Slideware and document maturity substitute for tested constraints; decision is already made. | NO | Asynchronous model/code/evidence review, focused review panel, automated constraint evidence. | Use only around a real expensive commitment. |
| Fixed phase gate | EW-P021 evidence-backed commitment decision | Potential stop/redirect point. | Calendar, sunk cost and political commitments predetermine passage. | NO | Event-driven knowledge point; automated policy gate; incremental funding decision. | Replace phase completion with commitment-specific evidence. |
| Traceability matrix spreadsheet | EW-P017 demonstrable relations | Coverage and impact visibility. | Links decay, are copied for compliance, or are never used in a decision. | NO | Linked identifiers, graph queries, executable specifications, code/test/issue relations, generated evidence. | Selective, automated and quality-checked. |
| Standing Change-Control Board | EW-P008 authorised impact evaluation | Shared consequence review and authority. | Every harmless change queues centrally; board rubber-stamps stale impact analyses. | CONTEXT_DEPENDENT | Delegated thresholds, policy as code, peer approval, emergency path, post-change audit. | Reserve synchronous board action for cross-authority/high-consequence change. |
| Static configuration baseline document | EW-P006 configuration identity | Known approved state. | Document is controlled while source, build or deployed system drifts. | NO | Immutable version tags, signed artefacts, reproducible builds, deployment manifests, model baselines. | Baseline actual configurations and status, not paper alone. |
| Interface Control Document | EW-P009 owned testable interface | Agreement across independently controlled boundaries. | Syntax is documented but semantics/units/timing are not tested; document goes stale. | NO | Versioned schema/API, contract test, shared model, physical drawing, compatibility policy. | Use form appropriate to boundary and consequence. |
| Interface Control Working Group/Board | EW-P009 shared interface authority | Cross-party change negotiation. | Unanimity blocks evolution or participants lack technical ownership. | ONLY_WHERE_SHARED_AUTHORITY_REQUIRES_IT | Named bilateral owners, automated compatibility rules, delegated semantic-version policy. | Escalate only consequential cross-authority changes. |
| Monolithic final test phase | EW-P010–EW-P012 evaluation | Integrated evidence. | Evidence arrives after options and schedule are exhausted. | NO | Continuous lower-level verification, repeated integration, staged high-fidelity and operational evaluation. | REJECTED as sole evaluation strategy. |
| Independent V&V organisation | EW-P016 independent challenge | Separation of incentives and a second technical view. | Duplicate work, slow feedback, weak context, nominal independence or no corrective authority. | HIGH_CONSEQUENCE_OR_REGULATORY_CONTEXT | Focused IV&V, independent assessor, rotating reviewer, external lab, independent OT&E. | Scale dimensions and scope of independence to risk. |
| Safety-case report / GSN diagram | EW-P019 challengeable assurance argument | Visible relationship between claims and evidence. | Persuasive static dossier, after-the-fact rationalisation, graphical complexity and stale evidence. | NO_GENERAL_FORM | Living claim/evidence graph, concise argument, risk register plus explicit justification. | Use only where argument changes assurance decisions. |
| Formal evidence package | EW-P006, EW-P010–EW-P015 evidence provenance | Reproducible basis for acceptance/certification. | Assembled retrospectively, detached from exact configuration, duplicated across authorities. | THE_EVIDENCE_MAY_BE; PACKAGING_NEED_NOT_BE | Continuously accumulated configuration-linked evidence and authority-specific views. | Automate provenance and reuse; preserve legal packaging where mandated. |
| Pilot project / MVP phase | EW-P004 executable risk retirement | Evidence before full commitment. | Demo does not test decisive risk, becomes production accidentally or cannot affect plan. | NO | Simulation, spike, test article, thin increment, shadow operation, hardware-in-loop. | Choose experiment by hypothesis, not label. |
| Qualification campaign | EW-P013 envelope/margin evidence | Design-type confidence across required conditions. | Unrepresentative article, invalidated by change, nominal pass treated as all-purpose validation. | DOMAIN_SPECIFIC | Analysis, similarity, incremental/component qualification, validated simulation. | Retain where an envelope/type claim exists. |
| Acceptance certificate/signature | EW-P014 acceptance authority | Transfer of responsibility over an identified item. | Signer cannot identify configuration, exceptions or operational evidence. | LEGAL_OR_CONTRACT_SPECIFIC | Signed digital decision, automated promotion plus recorded authority, conditional acceptance record. | Retain decision provenance, not paper symbolism. |
| Operational Readiness Review meeting | EW-P027 actual readiness | Cross-functional go/no-go before operation. | Checklist/slide review after irreversible cutover; actual data, people or support not examined. | NO_GENERAL_FORM | Automated readiness checks, rehearsal, canary, incident exercise, focused authority review. | Use strength proportional to cutover consequence and recovery. |
| Contingency/rollback plan document | EW-P028 demonstrated recovery | Prepared response. | Never exercised; backup shares failure; rollback ignores data/physical side effects. | NO | Automated rollback, recovery test, chaos exercise, alternate operation, rehearsed runbook. | Evidence of recovery matters more than prose. |
| MBSE platform / 'single source of truth' | EW-P030 governed authoritative engineering data | Consistency, analysis and reduced handoffs. | Authority is ambiguous; tools do not interoperate; model is stale or unvalidated; vendor lock-in. | NO | Federated authoritative sources, source/tests/schemas, lightweight models, data contracts. | Adopt only for measurable decisions and govern model-to-reality correspondence. |
| Continuous-compliance dashboard | EW-P031 fresh evidence and EW-P032 authority | Low-latency status and evidence reuse. | Green metrics cover weak controls, stale scope or compromised pipeline; no one owns residual risk. | NO | Signed evidence store, risk-specific alerts, sampled independent evaluation, release attestations. | Treat as evidence interface, never as automatic assurance truth. |

# EVOLVED_WATERFALL_CRITICISM_LEDGER

| CRITICISM | TARGET | EVIDENCE | ACCEPTED | SURVIVING_RESPONSE | RESIDUAL_RISK |
| --- | --- | --- | --- | --- | --- |
| Requirements cannot be fully known up front. | UP_FRONT_COMMITMENT | Historical analysis, practitioner reports and case study. | YES | EW-P001, P002, P004, P012, P022. | Stable external obligations still need authority; endless provisionality is also harmful. |
| Late integration reveals invalid assumptions. | SEQUENTIALITY | Royce, mishap/case evidence and modern continuous integration guidance. | YES | EW-P003, P004, P009, P011, P023, P031. | High-fidelity integration may remain scarce/slow. |
| Late user/operational feedback builds the wrong system. | VALIDATION_LATENCY | NATO, Brooks, NRC and modern V&V definitions. | YES | EW-P012 and incremental operational evaluation. | Representative users/environments may be unavailable or conflicting. |
| Documentation becomes excessive and stale. | DOCUMENTATION | Parnas distinction, MIL-STD-498, safety-case and MBSE evidence. | YES | EW-P005 living minimum-sufficient knowledge; EW-P030 governed data. | Automation can produce more stale material faster. |
| Formal approval certifies documents, not system state. | FORMAL_APPROVAL | Institutional acquisition review and safety-case pathologies. | YES | EW-P007, P021, P027. | Evidence itself can be selected/gamed. |
| Baselines freeze wrong requirements. | BASELINING | Requirements criticism and deployed cases. | PARTLY | EW-P001 and P006 are authoritative but revisable; P002 marks uncertainty. | Any authority can become political lock-in. |
| Without baselines, teams cannot identify authoritative state. | ANTI_BASELINING | Version confusion, configuration standards and certification practice. | COUNTERCRITICISM_ACCEPTED | EW-P006/P007. | Granularity and promotion cost must be proportional. |
| Traceability becomes stale theatre. | TRACEABILITY | Mapping reviews and maintenance cost; ideal-trace experiment limits. | YES | EW-P017 selective, automated, decision-linked trace. | No universal net-benefit threshold. |
| Change control becomes a bottleneck. | CHANGE_CONTROL | Institutional practice and graded regulatory alternatives. | YES | EW-P008 risk-proportional authorisation with cheap paths. | Impact thresholds can be gamed or miss systemic effects. |
| Independent V&V adds latency, paperwork and cost. | INDEPENDENT_VV | Mixed older comparative studies and independence analysis. | YES_AS_CONDITION | EW-P016 scoped independence at high consequence. | Modern causal evidence remains sparse. |
| Organisational handoffs lose context. | ORGANISATIONAL_HANDOFF | Ericsson case, acquisition and digital-authority studies. | YES | EW-P005, P009, P023, P026, P030. | Shared tools do not create shared understanding automatically. |
| Predictive plans create false certainty. | PREDICTIVE_ESTIMATION | Systematic estimation review, uncertainty research and escalation studies. | YES | EW-P025 rolling ranges/outside views/actuals. | Political targets can still masquerade as forecasts. |
| Phase gates and milestones are gamed. | PHASE_GATE | Acquisition reviews, Stage-Gate evolution and escalation research. | YES | EW-P021 event-driven commitment decisions. | Stop authority and evidence quality are organisational, not procedural, properties. |
| Safety/assurance cases are compliance theatre. | ASSURANCE_CASE | Current MOD guidance catalogues this failure explicitly. | YES | EW-P019 living falsification-oriented argument. | Outcome evidence remains weak; argument may remain persuasive rather than diagnostic. |
| Digital models become new stale documents. | DIGITAL_ENGINEERING | Systematic reviews and government-sponsored authority/interoperability study. | YES | EW-P030 scoped authority, model validation and as-deployed reconciliation. | Vendor/tool/culture and model confidence remain difficult. |
| Continuous delivery weakens assurance and authority. | DEVSECOPS | RTCA/DoD sources demonstrate lifecycle-neutral objectives and continuous T&E/cATO. | NOT_AS_GENERAL_CLAIM | EW-P031 continuous evidence plus immutable configurations, independent evaluation and P032 authority. | Automation quality and certification latency remain. |
| Late change is always exponentially expensive. | COST_OF_CHANGE_GENERALISATION | Directly mixed cross-domain empirical evidence. | REJECTED_AS_UNIVERSAL_RULE | EW-P033 multidimensional commitment/reversibility profile. | Domain-specific escalation can still be severe. |
| Plan-driven controls cannot respond quickly to security/operations. | DOMAIN_MISAPPLICATION | Continuous DevSecOps/SSDF/cATO guidance. | YES_WHEN_CONTROLS_ARE_EPISODIC | EW-P008 emergency paths, P031 continuous evidence and P028 recovery. | Fast pipelines can propagate compromised evidence or unsafe changes. |

# EVOLVED_WATERFALL_EVOLUTION_UNDER_CRITICISM

| CRITICISM_OR_PRESSURE | EARLIER_FORM | EVOLUTION | CLASSIFICATION | SURVIVING_PROPERTIES |
| --- | --- | --- | --- | --- |
| Unknowable complete requirements | Complete requirements before design/implementation | Prototypes, spiral, explicit assumptions, incremental requirements and repeated validation | REJECTED_AND_REPLACED | EW-P001; EW-P002; EW-P004; EW-P012 |
| Late integration | Component completion followed by terminal integration | Continuous integration, early system threads, simulation, staged high-fidelity integration | HYBRIDISED | EW-P004; EW-P009; EW-P011; EW-P031 |
| Testing too late | Test phase after implementation | V-shaped early evaluation planning, test-driven design, continuous T&E and operational evaluation | REFINED | EW-P010; EW-P011; EW-P012; EW-P031 |
| One giant final baseline | Single requirements/design/product baseline | Incremental baselines and immutable release identities with formalisation at certification/acceptance boundaries | REFINED | EW-P006; EW-P022; EW-P023 |
| Document handoff and staleness | Prescribed document volumes | Information-item outcomes, living decision records, integrated data/models and automated evidence | REPLACED_IN_FORM | EW-P005; EW-P030; EW-P031 |
| Change-board latency | All baseline changes require central board approval | Risk classes, delegated authority, automated impact evidence and emergency paths | NARROWED_AND_REFINED | EW-P008; EW-P024; EW-P033 |
| Traceability maintenance burden | Exhaustive manual matrices | Selective decision-linked traces, automation, link-quality and decay checks | NARROWED | EW-P017 |
| Review/gate bureaucracy | Calendar phase and document completion | Event-driven commitment decisions with real stop/redirect authority and continuous evidence | REPLACED | EW-P021; EW-P022 |
| IV&V separation slows feedback | Full duplicated lifecycle by separate organisation | Integrity-scaled focused IV&V, early access, independent OT&E and multidimensional independence | NARROWED_AND_HYBRIDISED | EW-P016 |
| Qualification and certification delay | One terminal evidence campaign | Component/incremental qualification, model/similarity credit, iterative builds with baseline-specific certification evidence | HYBRIDISED_BUT_DOMAIN_BOUND | EW-P013; EW-P015; EW-P031 |
| Safety case assembled too late | Final report defending completed design | Through-life argument/evidence that informs design and operation | REFINED | EW-P018; EW-P019 |
| Rigid global lifecycle | One project-wide sequence | Concurrent, iterative, recursive and incremental process application | REJECTED_AND_GENERALIZED | EW-P023; EW-P024 |
| Predictive overconfidence | Single-point baseline and variance policing | Ranges, assumptions, reference classes, independent challenge and actual-driven updates | REFINED | EW-P025 |
| Model/document divergence | Approved design representation presumed authoritative | Scoped authoritative sources plus validation and reconciliation to as-built/as-tested/as-deployed state | REFINED | EW-P007; EW-P030 |
| Slow security/operational feedback | Periodic test/compliance package and release board | CI/CD, continuous testing/monitoring, cATO and progressive delivery while retaining release identity and authority | HYBRIDISED | EW-P006; EW-P028; EW-P031; EW-P032 |
| Universal cost-of-change rhetoric | Later phase means exponentially higher cost | Separate edit, propagation, commitment-unwind and failure/recovery cost; use multidimensional triggers | REJECTED_AND_REPLACED | EW-P033 |

# EVOLVED_WATERFALL_REVERSIBILITY_PROFILES

## Control bands

| BAND | DESCRIPTION | DEFAULT_CONTROL | ESCALATORS | EXAMPLES |
| --- | --- | --- | --- | --- |
| R0_EXPLORATORY_LOCAL | Local, low-consequence, no external promise, rapidly observable and trivially discarded. | Version history, focused test, peer feedback; no formal baseline/gate/board. | Privacy/security exposure, irreversible external transaction, hidden shared dependency. | Local spike, disposable simulation, feature experiment with isolated data. |
| R1_SHARED_REVERSIBLE_SOFTWARE | Shared code/service state with automated rollback but non-trivial coupling. | Immutable build/release identity, CI tests, peer/policy approval, telemetry and tested rollback. | Large blast radius, customer/data migration, security boundary, independent consumers. | Service release, shared API, internal platform change. |
| R2_OPERATIONAL_OR_DATA_COMMITMENT | Users, operations, persistent data, external interfaces or service continuity make rollback incomplete or costly. | Impact analysis, staged rollout/canary, readiness, recovery evidence, acceptance/operational authority. | Safety/public impact, legal commitment, long observability latency, cross-organisation dependency. | Production migration, public API change, infrastructure cutover. |
| R3_EXTERNAL_CONTRACTUAL_REGULATORY_LONG_LEAD | Supplier contracts, long-lead purchases, certification evidence, fixed interfaces or scarce facilities create costly unwind. | Authoritative baselines, interface/configuration control, staged commitment, qualification planning, independent challenge and formal authority. | Physical irreversibility, major safety consequence, no representative test opportunity. | Custom hardware order, regulated software baseline, multi-supplier integration. |
| R4_PHYSICAL_SAFETY_CRITICAL_OR_IRREVERSIBLE | Physical actuation/fabrication, human/environmental safety, nuclear startup, flight, infrastructure or one-way consequences. | Hazard control, qualification, independent assessment, actual-state readiness, certification/operational authority, contingency and through-life evidence. | Unknown hazards, weak observability, single opportunity, catastrophic consequence. | Launch, reactor restart, autonomous safety actuation, permanent construction/cutover. |

## Domain profiles

| DOMAIN | TRIGGER_PATTERN | VALUABLE_PROPERTIES | CHEAP_PATH | COUNTEREVIDENCE |
| --- | --- | --- | --- | --- |
| Rapidly reversible software | Usually R0–R1; consequence, persistent data, privacy/security and external API can raise to R2/R3. | P006, P008, P011, P012, P020, P024, P028, P031, P033. | VCS, CI, immutable artefacts, automated tests, canary, telemetry, one-click/tested recovery. | No universal late-defect cost; heavy boards and exhaustive traces can reduce feedback and remediation speed. |
| Aerospace/space | Long lead, scarce test, flight safety, certification and physical integration often R3–R4. | P003, P004, P006–P019, P021–P024, P026–P033. | Early simulations/prototypes and informal iterative builds before evidence is used for certification credit. | DO-178C does not mandate a lifecycle; certification artefacts have flexible packaging; IV&V economics are mixed. |
| Medical devices/quality-system software | Patient/product risk and regulatory intended use; not every tool function has equal risk. | P001, P006, P008, P010–P015, P018, P020, P024, P032, P033. | FDA least-burdensome risk-based assurance, unscripted or continuous methods where justified. | Testing alone may be insufficient; more paperwork is not automatically more assurance. |
| Automotive | ASIL/hazard classification, fleet/update management, physical actuation and type approval. | P006–P020, P024, P029, P031–P033. | Classify non-safety functions lower, reuse automated evidence and manage updates incrementally. | ISO 26262 is functional-safety/domain specific, not a general development process. |
| Rail | Significant technical/operational/organisational change and system safety; independent assessment scaled by risk. | P008, P009, P012, P015–P020, P024, P027, P032, P033. | Risk-significance screening and sampled/vertical-slice independent assessment rather than 100% review. | Formal documentation alone is insufficient; assessment is expected to address actual implementation. |
| Nuclear/high-hazard infrastructure | Safety significance, licence basis, physical configuration and startup/restart authority, generally R4. | P006–P021, P024, P027–P033. | 10 CFR 50.59 demonstrates evaluated changes can be made without prior NRC approval below defined thresholds. | High hazard does not justify universal external pre-approval; readiness/CM paperwork can still diverge from plant state. |
| Large infrastructure/data migration | Physical construction or persistent data, multi-supplier interfaces, cutover and long recovery, R2–R4. | P003, P006–P009, P021–P030, P033. | Pilot segments, rehearsals, progressive migration, automated reconciliation and delegated local changes. | Digital asset models and gates are not valuable if authority and as-built correspondence are weak. |

## Final reversibility rule

There is no evidence-backed universal scalar threshold. The mature decision rule is multi-dimensional and comparative: add control only when the expected reduction in failure, ambiguity or unauthorised commitment exceeds the control’s delay, maintenance, coordination and false-confidence cost. Prefer controls that remain continuous, automated and close to the actual system. Escalate independent authority or formal evidence only when consequence, conflict of interest or external governance requires it.

# EVOLVED_WATERFALL_INTERNAL_TENSIONS

| TENSION | SIDE_A_PROPERTY | SIDE_B_PROPERTY | CONTEXT_THAT_FAVOURS_A | CONTEXT_THAT_FAVOURS_B | KNOWN_HYBRID_RESOLUTION | UNRESOLVED_RISK |
| --- | --- | --- | --- | --- | --- | --- |
| Stability versus adaptability | P001/P006 authoritative baselines | P002/P004/P031 learning and rapid change | External commitments, many independent actors, safety/certification, long lifecycle. | Uncertain need, reversible experiments, rapid observability. | Baseline only decision-relevant state; use incremental baselines and cheap experimental branches. | Promotion from experiment to authority may be mistimed. |
| Assurance versus delivery latency | P010–P019, P021 | P031 continuous delivery | Catastrophic/public consequence, scarce test, external authority. | Fast threat/market/operational feedback and reversible releases. | Automated continuous evidence plus risk-triggered independent/legal decisions. | Automation may validate wrong assumptions; authority may remain slower than risk. |
| Traceability versus maintenance burden | P017 | P024/P031 proportional flow | Certification, complex impact, long life, supplier handoff. | Small rapidly changing system with native executable links. | Trace only decision-critical claims; automate and measure decay. | Minimum valuable trace set is not generally known. |
| Architecture commitment versus learning | P003/P009 | P004/P022 | Physical constraints, fixed interfaces, long lead, high coupling. | Novel need, modular/reversible software, uncertain technology. | Minimum sufficient architecture, executable risk tests and delayed irreversible choices. | Architecture work can itself create sunk cost and political lock-in. |
| Independent challenge versus feedback speed | P016 | P031 and integrated teams | Conflicted incentives, public risk, high criticality, opaque evidence. | Low consequence and need for continuous context-rich feedback. | Focused early IV&V, embedded-but-protected reviewers, independent OT&E using shared evidence. | Optimal independence dimensions and scope lack modern causal evidence. |
| Configuration control versus developer flow | P006/P008 | P031 | Certified releases, multiple variants/suppliers, difficult rollback. | Local branches, automated tests, high deployment frequency. | Unrestricted exploratory states; controlled promotion to immutable authoritative releases. | Promotion boundary may be too early or too late. |
| Formal acceptance versus continuous service | P014/P032 | P031 continuous deployment | Transfer of custody/liability, contractual delivery, operational authority. | Continuously evolving service with reversible release. | Conditional, incremental, service-level and revocable acceptance over identified releases. | Legal/contract language may not support continuous partial acceptance. |
| Supplier coordination versus local autonomy | P009/P026 | P023/P031 local iteration | Long lead, fixed physical fit, multiple legal organisations, data-right dependence. | Modular teams with automated compatibility and replaceable dependencies. | Govern boundary products/interfaces/evidence, not supplier internal process. | Contract incentives can still freeze wrong interfaces. |
| Exhaustive planning versus uncertainty | P025/P026 | P002/P004 | Funding, capacity, procurement and long lead commitments. | Novel work where detailed forecasts lack basis. | Rolling ranges and scenario plans tied to staged commitment and experiments. | Targets continue to be mistaken for forecasts. |
| Documentation continuity versus documentation debt | P005/P029 | P024/P031 | Long-lived systems, turnover, safety and maintenance. | Short-lived local software and self-describing executable artefacts. | Capture durable/non-obvious knowledge; automate provenance; delete superseded representations. | Future information value is hard to predict. |
| Safety stability versus security remediation urgency | P013/P015/P018 | P008/P031 rapid patching | Change may invalidate qualification or create physical hazard. | Known exploitable vulnerability where delay raises harm. | Pre-authorised emergency change classes, bounded patch evidence, monitoring and rapid post-change requalification. | No universal balance; adversarial timing can defeat normal approval. |
| Single authority versus federated truth | P006/P030/P032 | Local domain ownership and tool autonomy | Need for final configuration/operational decision and legal accountability. | Many disciplines with specialised models and rapid local change. | Federated authoritative sources with scoped ownership, shared identifiers and explicit reconciliation. | Federated disagreement and semantic mismatch can remain invisible. |

# EVOLVED_WATERFALL_HYBRIDISATION_PRESSURES

| PRESSURE | NATIVE_SIDE | IMPORTED_SIDE | RESOLUTION | PROPERTIES |
| --- | --- | --- | --- | --- |
| Need for early feedback without losing release identity | PLAN_DRIVEN_NATIVE: baseline and evidence provenance | ADAPTIVE_IMPORT: frequent integration and deployment | HYBRID_RESOLUTION: immutable incremental releases with CI evidence | P006; P011; P031 |
| Requirements learning under contractual authority | Authoritative requirement state | Incremental discovery and user feedback | Revisable baselines, uncertainty ledger and staged commitment | P001; P002; P012; P022 |
| Regulatory evidence under iterative development | Certification basis, trace and independent objectives | Iterative builds and continuous requirements refinement | Baseline-specific formalisation and evidence for certification credit | P006; P015; P017; P031 |
| Fast security remediation under controlled change | Impact/authority and configuration integrity | Rapid pipeline and continuous monitoring | Pre-authorised policy paths, automated evidence, residual-risk authority | P008; P028; P031; P032 |
| System architecture under uncertainty | Early cross-cutting feasibility and interfaces | Emergent design and executable learning | Minimum sufficient architecture plus risk-targeted prototypes | P003; P004; P009 |
| Independent assurance without organisational wall | Segregation of incentives and authority | Cross-functional continuous collaboration | Focused, early, protected independence using shared live evidence | P016; P031 |
| Formal readiness under continuous delivery | Acceptance/operational authority | Canary/progressive deployment | Automated readiness, incremental acceptance and revocable authority | P014; P027; P028; P032 |
| Document continuity under model/code-native work | Transferable technical knowledge | Working system and executable artefacts | Information outcomes in native forms with generated views | P005; P030; P031 |
| Long-lead suppliers under evolving design | Contract, interface and baseline control | Iterative specification and modular delivery | Boundary-focused contracts, options and incremental commitments | P009; P022; P026 |
| Full-lifecycle assurance under changing operations | Qualification, safety case, sustainment | Telemetry and operational learning | Through-life evidence, monitoring and change-triggered reassessment | P013; P018; P019; P029; P031 |

These classifications record source-described hybridisation only. They do not import conclusions from any separate Agile research lane.

# EVOLVED_WATERFALL_STRONGEST_SURVIVING_PROPERTIES

The following properties have the strongest general or cross-domain survival after criticism. Their artefact forms remain tailorable:

- **EW-P004 — Executable risk retirement through prototypes, pilots, simulation and thin increments**: Executable evidence is selected by risk and commitment, with clear limits on what the experiment proves and explicit promotion criteria. Evidence: `A_STRONG_HISTORICAL_DOMAIN_AND_CROSS_METHOD_SUPPORT`.
- **EW-P006 — Configuration identification and baseline authority**: Authoritative identity across intent, source/model, build, test evidence and release, with proportionate promotion controls. Evidence: `A_STRONG_MULTI_DOMAIN_NORMATIVE_AND_FAILURE_SUPPORT`.
- **EW-P008 — Change visibility, impact analysis and risk-proportional authorisation**: Policy-based change classes, automated impact evidence, named escalation thresholds and explicit acceptance of residual risk. Evidence: `A_STRONG_CROSS_DOMAIN_NORMATIVE_SUPPORT`.
- **EW-P009 — Interface definition, ownership and compatibility control**: Authoritative, testable and owned contracts for consequential boundaries, with automated compatibility evidence where possible. Evidence: `A_STRONG_MECHANISTIC_AND_DOMAIN_FAILURE_SUPPORT`.
- **EW-P010 — Verification planning and requirement testability**: Risk-proportional verification design integrated with requirements and architecture, with automated evidence where appropriate. Evidence: `A_STRONG_PRIMARY_STANDARD_AND_DOMAIN_SUPPORT`.
- **EW-P011 — Multi-level verification and integration evidence**: Layered evidence selected by failure observability, with fast lower-level feedback and periodic higher-fidelity integration. Evidence: `A_STRONG_HISTORICAL_DOMAIN_AND_MODERN_SUPPORT`.
- **EW-P012 — Intended-use and operational-context validation**: Repeated context-validity evidence, with final claims tied to an identified configuration and intended-use envelope. Evidence: `A_STRONG_CROSS_DOMAIN_CONCEPTUAL_AND_PRACTICE_SUPPORT`.
- **EW-P020 — Anomaly, problem-report, deviation, waiver and corrective-action provenance**: One material problem identity from detection through authorised disposition and verified correction, linked to configuration and evidence. Evidence: `B_STRONG_CROSS_DOMAIN_MECHANISTIC_SUPPORT`.
- **EW-P023 — Incremental, concurrent and recursive lifecycle application**: Lifecycle processes are obligations and feedback loops applied where needed, not calendar phases traversed once. Evidence: `A_STRONG_PRIMARY_STANDARDS_AND_HISTORICAL_SUPPORT`.
- **EW-P024 — Tailoring and proportionality**: A transparent control-selection rule with cheap defaults, explicit escalation factors, mandatory legal minima and post-outcome learning. Evidence: `A_STRONG_CROSS_STANDARD_AND_DOMAIN_CONVERGENCE`.
- **EW-P031 — Continuous integration, automated evidence and continuous assurance**: Continuous, configuration-linked evidence with explicit coverage limits, risk gates, monitoring and human/independent authority at consequential boundaries. Evidence: `B_STRONG_MODERN_GUIDANCE_MIXED_EMPIRICAL_OUTCOMES`.

The meta-property EW-P033 is not placed in this strongest set because the direction of escalation is supported but no portable quantitative threshold or universal formula was found.

# EVOLVED_WATERFALL_CONTEXT_SPECIFIC_PROPERTIES

- **EW-P002 — Explicit requirements uncertainty, assumptions and learning obligations** — `CONTEXT_DEPENDENT`. Trigger: Novel problem, volatile environment, ambiguous user need, uncertain technology, emergent operations or weak observability. Cheap path: Routine replacement with stable, externally specified behaviour can use a short assumption list and normal change handling.
- **EW-P005 — Current, transferable engineering knowledge and decision rationale** — `USEFUL_BUT_EASILY_BUREAUCRATISED`. Trigger: Long-lived systems; turnover; suppliers; safety/certification; difficult maintenance; asynchronous or geographically distributed work. Cheap path: Small co-located reversible work can rely on tests, code, short decision records and version history; document only durable or non-obvious knowledge.
- **EW-P007 — As-designed, as-built, as-tested and as-deployed reconciliation** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: Physical construction; fielded fleets; infrastructure; data migrations; certified releases; complex deployment environments. Cheap path: For stateless, automatically deployed services, deployment manifests, telemetry and immutable image identity may supply the cheap path.
- **EW-P009 — Interface definition, ownership and compatibility control** — `CONTEXT_DEPENDENT`. Trigger: Organisational/supplier boundary; independently released components; fixed physical interfaces; long integration latency; safety or interoperability consequence. Cheap path: Private local interfaces can evolve through code, types and tests without formal cross-organisational approval.
- **EW-P013 — Qualification envelope and margin evidence** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: Safety/mission-critical product; physical environment; production of multiple units; scarce opportunities for field correction; certification requirement. Cheap path: Ordinary web/software features with reversible deployment do not need a separate qualification programme; targeted performance/security tests may suffice.
- **EW-P014 — Acceptance criteria, authority and provenance** — `CONTEXT_DEPENDENT`. Trigger: External acquirer/operator; regulated or safety system; contractual deliverable; irreversible cutover; transfer between organisations. Cheap path: Internal reversible software release can use automated release criteria and product-owner/operational approval without a separate ceremony.
- **EW-P015 — Certification basis and regulatory-authority coupling** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: Legally regulated system; safety or environmental externality; airworthiness/type approval/licensing; public infrastructure. Cheap path: No trigger where no empowered external certification regime applies; do not invent an internal 'certification' label.
- **EW-P016 — Independent technical challenge and IV&V** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: High criticality; novel or complex system; public/third-party risk; strong schedule incentives; many suppliers; opaque evidence; regulatory mandate. Cheap path: Low-consequence reversible work can use peer review, rotation, automated checks and occasional external review rather than a standing IV&V organisation.
- **EW-P017 — Demonstrable bidirectional traceability** — `USEFUL_BUT_EASILY_BUREAUCRATISED`. Trigger: Certification; high coupling; long-lived system; supplier handoff; safety/hazard chains; expensive impact analysis; many variants. Cheap path: For small rapidly changing software, issue/commit/test naming, executable specifications, types and dependency graphs may provide sufficient native trace.
- **EW-P018 — Safety and hazard analysis with tracked risk controls** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: Potential death/injury, environmental harm, major public loss, high-energy physical system, safety-related software or infrastructure. Cheap path: No trigger for ordinary low-consequence functionality; proportionate product/security risk analysis may replace formal system-safety machinery.
- **EW-P019 — Assurance or safety case as a living claims–argument–evidence structure** — `USEFUL_BUT_EASILY_BUREAUCRATISED`. Trigger: Novel high-consequence system; non-prescriptive regulation; heterogeneous evidence; residual risk requiring an accountable judgement. Cheap path: Stable low-risk products can use concise control/evidence summaries; do not construct a graphical assurance case merely to satisfy a style.
- **EW-P021 — Evidence-backed, event-driven commitment reviews** — `CONTEXT_DEPENDENT`. Trigger: Capital, production, long-lead procurement, fleet deployment, irreversible migration, safety authority, major supplier or contractual commitment. Cheap path: Continuous low-risk software work can use automated promotion rules and lightweight asynchronous review; no milestone meeting is needed.
- **EW-P025 — Rolling planning, estimate uncertainty and outside-view challenge** — `CONTEXT_DEPENDENT`. Trigger: Budget or contract decision; long lead; portfolio trade-off; external dependency; irreversible investment; capacity planning. Cheap path: Small reversible work can use short-horizon forecasts and throughput history; avoid elaborate earned-value machinery.
- **EW-P026 — Supplier, long-lead and dependency coordination** — `CONTEXT_DEPENDENT`. Trigger: Multiple legal organisations/suppliers; custom hardware; long lead; scarce materials; safety evidence from vendors; sustainment dependence. Cheap path: Single-team commodity/software dependencies can use lockfiles, service contracts, automated compatibility tests and normal vendor management.
- **EW-P027 — Transition, operational readiness and cutover control** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: Irreversible or high-impact cutover; physical startup; safety/mission operations; major migration; transfer to a separate operations organisation. Cheap path: Small reversible deployments can use automated readiness checks, canaries and on-call confirmation without a review meeting.
- **EW-P028 — Rollback, contingency and recovery readiness** — `CONTEXT_DEPENDENT`. Trigger: Operational/data change; service dependency; cyber threat; migration; remote/physical operation; significant outage or safety consequence. Cheap path: Truly stateless low-impact experiments may need only one-click revert and normal version history.
- **EW-P029 — Sustainment, obsolescence and support continuity** — `CONTEXT_DEPENDENT`. Trigger: Long-lived asset; fleet; regulated/safety system; custom hardware; external supplier; high replacement/cutover cost. Cheap path: Short-lived commodity software can rely on maintained dependencies, observability and explicit end-of-life policy.
- **EW-P030 — Digital authoritative engineering environment and model governance** — `USEFUL_BUT_EASILY_BUREAUCRATISED`. Trigger: Many disciplines/models; complex interfaces; long lifecycle; supplier data exchange; expensive manual consistency checking. Cheap path: Small software products can use source, tests, schemas and deployment manifests as native authoritative artefacts without an MBSE platform.
- **EW-P032 — Risk ownership, residual-risk decision and operational authority** — `HIGH_CONSEQUENCE_CONTEXT_PROPERTY`. Trigger: Material safety, security, privacy, mission, financial or public risk; operation beyond local team; conditional/temporary approval. Cheap path: Low-consequence reversible changes can operate under pre-authorised risk tolerances with automated monitoring.
- **EW-P033 — Reversibility- and commitment-sensitive control strength** — `CONTEXT_DEPENDENT`. Trigger: This is a meta-property applied whenever choosing baseline, trace, review, independence, qualification or authorisation strength. Cheap path: Default pre-authorised path for local, low-consequence, rapidly observable and genuinely reversible work.

# EVOLVED_WATERFALL_REJECTED_OR_SUPERSEDED_PRACTICES

- **EW-P034 — Fixed one-pass lifecycle sequencing** — `REJECTED_OR_DISFAVOURED`. Disposition: No mature general form. Preserve actual causal dependencies and commitment boundaries, not the phase diagram. Reason: Royce himself called the unmodified form risky; current ISO standards do not prescribe it; empirical cases show requirements/testing/handoff problems.
- **EW-P035 — Complete up-front requirements as a precondition to development** — `REJECTED_OR_DISFAVOURED`. Disposition: EW-P001 and EW-P002 replace this candidate. Reason: Contradicted by Bell–Thayer, Parnas/Clements, Brooks, spiral and modern lifecycle standards.
- **EW-P036 — Document-completion phase gates and fixed review ceremonies** — `CEREMONY_NOT_GENERAL_PROPERTY`. Disposition: EW-P021; the fixed ceremony itself is not retained. Reason: NRC/GAO and Stage-Gate's own evolution recognise linearity and bureaucracy.
- **EW-P037 — Uniform exhaustive manual traceability and central change-board control** — `CEREMONY_NOT_GENERAL_PROPERTY`. Disposition: EW-P008 and EW-P017. Reason: Traceability studies expose maintenance cost and ideal-link assumptions; nuclear practice itself uses graded change thresholds.
- **EW-P038 — Universal exponential late-change cost rule** — `REJECTED_OR_DISFAVOURED`. Disposition: No universal curve; use domain-specific evidence and tested recovery. Reason: Aerospace-like studies show large but wildly variable escalation; 171 software projects found no consistent substantial delayed-issue effect.

# EVOLVED_WATERFALL_OPEN_QUESTIONS

| ID | QUESTION | DISPOSITION | RELATED |
| --- | --- | --- | --- |
| OQ-01 | What quantitative, domain-portable control-escalation function could combine consequence, reversibility, coupling, observability, external authority and recovery? | UNRESOLVED; evidence supports dimensions, not a universal formula. | P024; P033 |
| OQ-02 | What is the minimum trace set that yields positive net value in real industrial settings, including maintenance and decay cost? | UNRESOLVED; controlled task benefits and observational quality associations exist, but general ROI thresholds do not. | P017 |
| OQ-03 | Which technical, managerial and financial independence profiles produce net IV&V benefit in modern continuous delivery? | UNRESOLVED; older evidence is mixed and context-sensitive. | P016; P031 |
| OQ-04 | Do living assurance cases improve safety outcomes beyond good hazard/evidence management, or mainly improve communication/auditability? | UNRESOLVED; practice rationale strong, comparative outcome evidence weak. | P019 |
| OQ-05 | Which MBSE/digital-engineering benefits survive controlled comparison after tool, training and model-maintenance cost? | UNRESOLVED; many claims are perceived or expected. | P030 |
| OQ-06 | How should formal certification credit be reused across frequent incremental changes without unsafe evidence inheritance? | DOMAIN-SPECIFIC OPEN ENGINEERING QUESTION. | P013; P015; P031 |
| OQ-07 | How can organisations detect that a baseline or gate has become sunk-cost protection rather than decision support? | PARTIALLY ANSWERED by real stop authority, independent challenge and actual-state evidence; no robust universal indicator. | P021; P025 |
| OQ-08 | How should hidden organisational, data and semantic interfaces be discovered before integration failure? | OPEN; formal ICDs cover known boundaries better than emergent socio-technical coupling. | P009; P030 |
| OQ-09 | When does architecture effort preserve options, and when does it itself create irreversibility? | CONTEXTUAL AND EMPIRICALLY UNDER-SPECIFIED. | P003; P004; P022 |
| OQ-10 | How should readiness and acceptance be represented for continuously changing services with no singular handover? | PARTIALLY RESOLVED by incremental/revocable authority; legal and contractual practice varies. | P014; P027; P032 |
| OQ-11 | Which evidence can be generated and assessed automatically without tool-chain common-mode failure or loss of independence? | OPEN; continuous assurance requires assurance of the evidence system itself. | P031 |
| OQ-12 | How should emergency security changes be bounded when normal qualification or regulatory latency is itself dangerous? | DOMAIN-SPECIFIC OPEN TENSION. | P008; P013; P015; P031 |
| OQ-13 | What forms of supplier contract preserve options, data rights and iterative learning while still making long-lead commitments governable? | OPEN; strong institutional evidence of the problem, weaker causal contract-design evidence. | P022; P026 |
| OQ-14 | How can as-deployed/as-built confidence be represented under partial observability and unauthorised field changes? | OPEN; reconciliation mechanisms exist but confidence metrics are weak. | P007; P030 |
| OQ-15 | Can exact historical diffusion of the one-pass Waterfall caricature be reconstructed beyond the Bell–Thayer naming hinge? | HISTORICALLY OPEN BUT NO LONGER DECISION-BLOCKING. | P034 |

These questions are frozen as explicit evidence limits. They do not prevent property-level repository adjudication because the packet records triggers, cheap paths, criticisms and uncertainty rather than converting unknown thresholds into rules.

# EVOLVED_WATERFALL_AUDIT_INTAKE

```text
PROPERTY_POPULATION_TOTAL: 38
PROPERTY_POPULATION_EXAMINED: 38
PROPERTY_COVERAGE: 38/38
CROSSWALK_WORTHY_PROPERTY_TOTAL: 33
REJECTED_OR_CEREMONIAL_CANDIDATE_TOTAL: 5
```

## TOP_CROSSWALK_PROPERTIES

- [EW-P001](#property-ew-p001) — Authoritative, revisable intent and requirements state
- [EW-P004](#property-ew-p004) — Executable risk retirement through prototypes, pilots, simulation and thin increments
- [EW-P006](#property-ew-p006) — Configuration identification and baseline authority
- [EW-P007](#property-ew-p007) — As-designed, as-built, as-tested and as-deployed reconciliation
- [EW-P008](#property-ew-p008) — Change visibility, impact analysis and risk-proportional authorisation
- [EW-P009](#property-ew-p009) — Interface definition, ownership and compatibility control
- [EW-P010](#property-ew-p010) — Verification planning and requirement testability
- [EW-P011](#property-ew-p011) — Multi-level verification and integration evidence
- [EW-P012](#property-ew-p012) — Intended-use and operational-context validation
- [EW-P017](#property-ew-p017) — Demonstrable bidirectional traceability
- [EW-P020](#property-ew-p020) — Anomaly, problem-report, deviation, waiver and corrective-action provenance
- [EW-P021](#property-ew-p021) — Evidence-backed, event-driven commitment reviews
- [EW-P022](#property-ew-p022) — Staged and incremental commitment with option preservation
- [EW-P023](#property-ew-p023) — Incremental, concurrent and recursive lifecycle application
- [EW-P024](#property-ew-p024) — Tailoring and proportionality
- [EW-P027](#property-ew-p027) — Transition, operational readiness and cutover control
- [EW-P028](#property-ew-p028) — Rollback, contingency and recovery readiness
- [EW-P031](#property-ew-p031) — Continuous integration, automated evidence and continuous assurance
- [EW-P032](#property-ew-p032) — Risk ownership, residual-risk decision and operational authority
- [EW-P033](#property-ew-p033) — Reversibility- and commitment-sensitive control strength

## Crosswalk-worthy properties

### EW-P001 — Authoritative, revisable intent and requirements state

- `FAILURE_MODE`: Conflicting interpretations, invisible requirement drift, implementation against obsolete intent, or unowned requirements.
- `MATURE_FORM`: A living authoritative requirement state that distinguishes proposed, approved, implemented, verified and retired obligations and allows risk-proportional change.
- `TRIGGER`: Shared or externally committed intent; multiple teams or suppliers; long-lived product; acceptance, safety or regulatory obligations; non-local change impact.
- `CHEAP_PATH`: For a single team exploring a local reversible feature, a lightweight backlog item, executable example and version history may be enough; do not baseline speculative detail merely to appear complete.
- `REVERSIBILITY_PROFILE`: R1–R4: value rises with shared scope, external commitment, coupling and evidence obligations; R0 generally needs only lightweight versioned intent.
- `REQUIRED_PRECONDITIONS`: Named authority; accessible current representation; change path; stakeholder participation; ability to mark uncertainty and supersession; configuration linkage.
- `EVIDENCE_STRENGTH`: B_STRONG_PRIMARY_AND_DOMAIN_SUPPORT
- `CRITICISMS`: Requirements cannot be fully known up front; a stable baseline can preserve error and create political resistance to change.
- `ANTI_CEREMONY_BOUNDARY`: The property is authority and state identity; a single giant requirements document, fixed template or requirements-complete gate is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P002 adaptability; EW-P024 tailoring; excessive stability can conflict with rapid learning.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Is there one discoverable authoritative intent state, or do specifications, tickets and implementation disagree?
  - Does the system distinguish proposed, approved, implemented and retired requirements without freezing discovery?

### EW-P002 — Explicit requirements uncertainty, assumptions and learning obligations

- `FAILURE_MODE`: False completeness, premature contractual/design commitment, unplanned rework and validation against assumptions nobody remembers.
- `MATURE_FORM`: An assumption/uncertainty ledger integrated with requirements, architecture, hazards and experiments, with expiry and promotion/retirement rules.
- `TRIGGER`: Novel problem, volatile environment, ambiguous user need, uncertain technology, emergent operations or weak observability.
- `CHEAP_PATH`: Routine replacement with stable, externally specified behaviour can use a short assumption list and normal change handling.
- `REVERSIBILITY_PROFILE`: R0–R3: most valuable before hard commitment; should shrink or change form as evidence and external obligations accumulate.
- `REQUIRED_PRECONDITIONS`: Psychological safety to admit uncertainty; decision owners; access to prototypes/users/data; expiry and review mechanisms.
- `EVIDENCE_STRENGTH`: B_STRONG_HISTORICAL_AND_MECHANISTIC_SUPPORT
- `CRITICISMS`: Can become administrative risk-register theatre or an excuse to avoid commitment.
- `ANTI_CEREMONY_BOUNDARY`: The property is explicit epistemic status and planned learning; a standing risk meeting or large spreadsheet is optional.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P001 baseline authority; EW-P022 staged commitment; too much tentativeness can undermine coordination.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Are assumptions and unknowns visible as such, or silently encoded as requirements?
  - Does each material uncertainty have a decision owner and an economical path to evidence?

### EW-P003 — Early architecture and feasibility before hard commitment

- `FAILURE_MODE`: Committing requirements, suppliers, tooling or production before the system concept can satisfy dominant constraints.
- `MATURE_FORM`: Minimum sufficient architecture and constraint evidence, paired with prototypes and continuously reconciled with the realised system.
- `TRIGGER`: High coupling; hardware/physical constraints; scarce test facilities; safety; long lead items; multiple suppliers; expensive migration or platform commitment.
- `CHEAP_PATH`: Local, modular, quickly deployable software can use a thin architecture sketch, automated fitness functions and evolutionary design.
- `REVERSIBILITY_PROFILE`: R0 light; R1 targeted; R2–R4 increasingly valuable where downstream physical, supplier or regulatory commitments are costly.
- `REQUIRED_PRECONDITIONS`: Representative constraints/data; accountable system architect or integrator; willingness to change requirements; prototypes/models validated for the question asked.
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_SUPPORT_MIXED_GENERAL_EVIDENCE
- `CRITICISMS`: Up-front architecture can delay learning and lock in wrong abstractions; architecture documents may become authority without reality.
- `ANTI_CEREMONY_BOUNDARY`: The property is early falsification of system-level constraints; a fixed CDR package or months-long architecture phase is not inherently required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P004 executable learning; EW-P022 option preservation; can conflict with emergent design and feedback speed.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does architecture work retire a named expensive risk, or merely produce preferred diagrams?
  - Are architectural claims tested and reconciled with the implementation before the relevant commitment?

### EW-P004 — Executable risk retirement through prototypes, pilots, simulation and thin increments

- `FAILURE_MODE`: Late discovery of infeasibility, wrong user need, integration behaviour or operational mismatch after most options are gone.
- `MATURE_FORM`: Executable evidence is selected by risk and commitment, with clear limits on what the experiment proves and explicit promotion criteria.
- `TRIGGER`: Novelty, uncertainty, difficult integration, unproven technology, weak requirements confidence, expensive final test or high consequence.
- `CHEAP_PATH`: For known repeat builds or low-risk local changes, ordinary automated tests or a small spike may suffice; avoid a ceremonial prototype that cannot affect the design.
- `REVERSIBILITY_PROFILE`: R0–R4: useful throughout, but experiment cost and evidential rigour rise as consequences and commitments rise.
- `REQUIRED_PRECONDITIONS`: Explicit hypothesis and decision; representative enough environment; protected budget/time; criteria for learning; no confusion between prototype evidence and qualified product evidence.
- `EVIDENCE_STRENGTH`: A_STRONG_HISTORICAL_DOMAIN_AND_CROSS_METHOD_SUPPORT
- `CRITICISMS`: A prototype may create false confidence and duplicate cost; not every project needs a separate full pilot.
- `ANTI_CEREMONY_BOUNDARY`: The property is empirical discrimination before commitment; a mandated prototype phase or 'MVP' label is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P003 architecture; EW-P013 qualification; rapid experiments can conflict with formal evidence boundaries.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Are the highest-cost assumptions tested by executable evidence before commitment?
  - Does each prototype have a decision it can change and an explicit limit on what it proves?

### EW-P005 — Current, transferable engineering knowledge and decision rationale

- `FAILURE_MODE`: Tacit rationale loss, repeated mistakes, unsafe maintenance, inability to review or transfer responsibility, and divergence between intent and implementation.
- `MATURE_FORM`: Minimum sufficient, current and configuration-linked engineering knowledge whose maintenance cost is justified by future decisions.
- `TRIGGER`: Long-lived systems; turnover; suppliers; safety/certification; difficult maintenance; asynchronous or geographically distributed work.
- `CHEAP_PATH`: Small co-located reversible work can rely on tests, code, short decision records and version history; document only durable or non-obvious knowledge.
- `REVERSIBILITY_PROFILE`: R0 minimal; R1 concise; R2–R4 stronger where lifetime, handoffs, hazards and authority increase.
- `REQUIRED_PRECONDITIONS`: Information ownership; update triggers; integration with work; discoverability; configuration links; deletion/retirement discipline.
- `EVIDENCE_STRENGTH`: B_STRONG_MECHANISTIC_AND_DOMAIN_SUPPORT
- `CRITICISMS`: Documentation can consume resources, slow feedback and create false assurance if it is approved but stale.
- `ANTI_CEREMONY_BOUNDARY`: The property is durable usable knowledge; page count, template completion and separate document ownership are not the property.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 automation; EW-P030 model authority; continuity competes with maintenance burden.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Can a new maintainer reconstruct why consequential decisions were made and which configuration they govern?
  - Is documentation generated and checked against live state, or independently approved and stale?

### EW-P006 — Configuration identification and baseline authority

- `FAILURE_MODE`: Wrong or unapproved item released; incompatible evidence; inability to reproduce a build; hidden drift; version disputes.
- `MATURE_FORM`: Authoritative identity across intent, source/model, build, test evidence and release, with proportionate promotion controls.
- `TRIGGER`: Multiple deployable versions; supplier or physical items; safety/certification; regulated evidence; long-lived support; distributed teams.
- `CHEAP_PATH`: For ephemeral local work, ordinary version control branches and automated build identity are enough; not every intermediate file needs formal CI status.
- `REVERSIBILITY_PROFILE`: R1–R4; R0 uses normal VCS. Value rises with multiple representations, releases, suppliers, certification and rollback difficulty.
- `REQUIRED_PRECONDITIONS`: Versionable artefacts; reproducible build/deployment process; named authority; status model; access control; retention policy.
- `EVIDENCE_STRENGTH`: A_STRONG_MULTI_DOMAIN_NORMATIVE_AND_FAILURE_SUPPORT
- `CRITICISMS`: Heavy CM can impede harmless change and create bureaucratic latency without preserving actual integrity.
- `ANTI_CEREMONY_BOUNDARY`: The property is identifiable authoritative state; a paper baseline, standing CCB or universal freeze is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P008 rapid change; EW-P031 continuous delivery; control can conflict with developer flow if promotion boundaries are unclear.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Can the system identify exactly what was proposed, built, tested, deployed and accepted?
  - Can an evidence result be tied to a reproducible configuration rather than a mutable branch or document set?

### EW-P007 — As-designed, as-built, as-tested and as-deployed reconciliation

- `FAILURE_MODE`: Evidence proves a different system; field modifications are invisible; operations use unknown state; rollback or incident analysis is unreliable.
- `MATURE_FORM`: Evidence-backed correspondence among authoritative models/data and actual built, tested and operating configurations, with explicit residual unknowns.
- `TRIGGER`: Physical construction; fielded fleets; infrastructure; data migrations; certified releases; complex deployment environments.
- `CHEAP_PATH`: For stateless, automatically deployed services, deployment manifests, telemetry and immutable image identity may supply the cheap path.
- `REVERSIBILITY_PROFILE`: R2–R4 strongest; R1 often automated; R0 generally unnecessary beyond normal build/run identity.
- `REQUIRED_PRECONDITIONS`: Observable deployed state; trustworthy inventory/telemetry; configuration identifiers; authority to resolve drift; environment capture.
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_SUPPORT_LIMITED_GENERAL_EMPIRICS
- `CRITICISMS`: Reconciliation can be expensive or impossible under partial observability; excessive audit frequency can become theatre.
- `ANTI_CEREMONY_BOUNDARY`: The property is correspondence to reality; an 'as-built' document or authoritative-source label is insufficient.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P030 digital model authority; EW-P031 speed; reconciliation depth can conflict with delivery latency.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does controlled documentation describe the actual running/built system, and what evidence establishes that correspondence?
  - Are emergency or field changes reconciled into authority before their evidence is reused?

### EW-P008 — Change visibility, impact analysis and risk-proportional authorisation

- `FAILURE_MODE`: Unseen side effects, invalidated qualification/certification, incompatible releases, unauthorised risk acceptance or loss of provenance.
- `MATURE_FORM`: Policy-based change classes, automated impact evidence, named escalation thresholds and explicit acceptance of residual risk.
- `TRIGGER`: Shared baselines; high coupling; external interfaces; safety/security/privacy; certified state; expensive recovery; contractual commitments.
- `CHEAP_PATH`: Local reversible changes with strong automated tests can be pre-authorised under policy and merged through normal peer review/CI.
- `REVERSIBILITY_PROFILE`: R0 pre-authorised; R1 automated/peer controlled; R2–R4 increasing analysis and authority, but emergency response must remain fast.
- `REQUIRED_PRECONDITIONS`: Dependency/trace information; clear delegated authority; risk criteria; timely reviewers; emergency path; audit trail.
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_DOMAIN_NORMATIVE_SUPPORT
- `CRITICISMS`: Change control can cost more than the change and can turn adaptation into exception processing.
- `ANTI_CEREMONY_BOUNDARY`: The property is visible authorised consequence management; a standing committee and meeting are not generally required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 flow and fast feedback; EW-P033 proportional control; authority can conflict with responsiveness.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Are harmless reversible changes pre-authorised while consequential changes receive real impact analysis?
  - Can the change process handle urgent remediation without bypassing identity and post-change evidence?

### EW-P009 — Interface definition, ownership and compatibility control

- `FAILURE_MODE`: Late integration incompatibility, unsafe assumptions, responsibility gaps, local optimisation and cascading redesign.
- `MATURE_FORM`: Authoritative, testable and owned contracts for consequential boundaries, with automated compatibility evidence where possible.
- `TRIGGER`: Organisational/supplier boundary; independently released components; fixed physical interfaces; long integration latency; safety or interoperability consequence.
- `CHEAP_PATH`: Private local interfaces can evolve through code, types and tests without formal cross-organisational approval.
- `REVERSIBILITY_PROFILE`: R1 at independently released software boundary; R2–R4 strong where suppliers, physical fit, units, timing or safety matter; R0 cheap.
- `REQUIRED_PRECONDITIONS`: Two-sided ownership and access; semantic precision; change notification; configuration links; integration testability; dispute authority.
- `EVIDENCE_STRENGTH`: A_STRONG_MECHANISTIC_AND_DOMAIN_FAILURE_SUPPORT
- `CRITICISMS`: Formal interface control can over-centralise architecture and slow local refactoring; documents cannot replace integration tests.
- `ANTI_CEREMONY_BOUNDARY`: The property is controlled compatibility at real boundaries; every internal function does not need an ICD or interface board.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P003 architecture; EW-P008 change flow; strict interface stability can conflict with refactoring.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Which interfaces cross authority or release boundaries and who owns compatibility on both sides?
  - Are interface semantics verified in integration, or only recorded in a document?

### EW-P010 — Verification planning and requirement testability

- `FAILURE_MODE`: Unverifiable requirements, missing evidence, late test redesign, false pass criteria and qualification schedule collapse.
- `MATURE_FORM`: Risk-proportional verification design integrated with requirements and architecture, with automated evidence where appropriate.
- `TRIGGER`: Acceptance/certification obligation; difficult environment; scarce facility; performance/safety margin; supplier evidence; long test lead.
- `CHEAP_PATH`: Low-risk software can encode acceptance examples and automated tests alongside implementation without a separate verification plan document.
- `REVERSIBILITY_PROFILE`: R0 executable examples; R1 continuous tests; R2–R4 formal environment/article/evidence planning.
- `REQUIRED_PRECONDITIONS`: Testable requirement; representative environment; instrumentation; configuration identity; resources; ownership; anomaly process.
- `EVIDENCE_STRENGTH`: A_STRONG_PRIMARY_STANDARD_AND_DOMAIN_SUPPORT
- `CRITICISMS`: Planning tests early can prematurely lock the design or optimise only for stated requirements.
- `ANTI_CEREMONY_BOUNDARY`: The property is planned evaluability and evidence sufficiency; a monolithic master test plan is not universally required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P002 uncertainty; EW-P012 validation; specification compliance can crowd out user-need learning.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Can every consequential requirement be evaluated with a named method, configuration and criterion?
  - Did verification planning reveal requirements that are ambiguous or infeasible before commitment?

### EW-P011 — Multi-level verification and integration evidence

- `FAILURE_MODE`: Components pass alone but fail together; local phase completion is mistaken for system readiness; integration arrives too late.
- `MATURE_FORM`: Layered evidence selected by failure observability, with fast lower-level feedback and periodic higher-fidelity integration.
- `TRIGGER`: Distributed components; cyber-physical behaviour; performance/load; external services; multiple suppliers; system-of-systems.
- `CHEAP_PATH`: For a small monolith or local change, one automated end-to-end path plus focused component tests may be enough.
- `REVERSIBILITY_PROFILE`: R0–R1 continuous and cheap; R2–R4 staged higher-fidelity evidence added where interactions and consequences demand it.
- `REQUIRED_PRECONDITIONS`: Integration environment; representative data/load; observability; version identity; interface contracts; anomaly handling.
- `EVIDENCE_STRENGTH`: A_STRONG_HISTORICAL_DOMAIN_AND_MODERN_SUPPORT
- `CRITICISMS`: More levels do not automatically add information; slow suites can delay feedback and encourage batching.
- `ANTI_CEREMONY_BOUNDARY`: The property is evaluation at the correct system level; a fixed number of test phases or a V diagram is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 delivery speed; EW-P013 qualification; higher-fidelity testing can be slow and scarce.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does the evidence exercise the level at which the claimed behaviour can fail?
  - Are system integration results early enough to change architecture rather than merely qualify the finished design?

### EW-P012 — Intended-use and operational-context validation

- `FAILURE_MODE`: Correct implementation of wrong requirements; unusable or operationally unsuitable system; hidden human/environment assumptions.
- `MATURE_FORM`: Repeated context-validity evidence, with final claims tied to an identified configuration and intended-use envelope.
- `TRIGGER`: Novel user need; socio-technical change; safety/mission consequence; operational environment unlike development; procurement handoff.
- `CHEAP_PATH`: For familiar low-risk changes, telemetry, user tests and rapid reversible deployment can supply continuous validation.
- `REVERSIBILITY_PROFILE`: R0 continuous cheap validation; R1 operational telemetry; R2–R4 increasingly representative and independently witnessed contexts.
- `REQUIRED_PRECONDITIONS`: Real stakeholders and operators; representative context; explicit intended use; outcome measures; ability to change requirements.
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_DOMAIN_CONCEPTUAL_AND_PRACTICE_SUPPORT
- `CRITICISMS`: Users may ask for local preferences rather than system value; validation can become acceptance theatre.
- `ANTI_CEREMONY_BOUNDARY`: The property is evidence of fitness for intended purpose; a UAT meeting or customer signature alone is not enough.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P001 requirement authority; EW-P014 acceptance; stakeholder feedback can conflict with stable external commitments.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does the system separately establish conformance to requirements and fitness for actual use?
  - Are real operators/environments represented before final acceptance?

### EW-P013 — Qualification envelope and margin evidence

- `FAILURE_MODE`: Field failure outside nominal conditions; manufacturing/design margin unknown; certification basis unsupported.
- `MATURE_FORM`: Configuration-linked evidence for a defined design envelope, with explicit assumptions, margins and change-trigger rules.
- `TRIGGER`: Safety/mission-critical product; physical environment; production of multiple units; scarce opportunities for field correction; certification requirement.
- `CHEAP_PATH`: Ordinary web/software features with reversible deployment do not need a separate qualification programme; targeted performance/security tests may suffice.
- `REVERSIBILITY_PROFILE`: Mostly R3–R4; selected R2 performance/security contexts. Usually no trigger for R0–R1 ordinary software.
- `REQUIRED_PRECONDITIONS`: Defined envelope and margins; representative article; validated models; configuration control; calibrated equipment; anomaly disposition.
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_STANDARD_AND_PRACTICE_SUPPORT
- `CRITICISMS`: Domain-specific and expensive; qualification can delay safer incremental improvements and is not synonymous with validation.
- `ANTI_CEREMONY_BOUNDARY`: The property is demonstrated capability over an envelope; a fixed test campaign or one qualification document is domain-specific.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P004 prototype speed; EW-P031 continuous change; qualification stability can conflict with frequent releases.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Is there a defined operational/environmental envelope that must be demonstrated beyond nominal tests?
  - Can the system state exactly which design changes invalidate or require supplementation of qualification evidence?

### EW-P014 — Acceptance criteria, authority and provenance

- `FAILURE_MODE`: Unauthorised declaration of completion; acceptance of wrong configuration; unresolved exceptions hidden; later dispute over obligations.
- `MATURE_FORM`: Explicit, configuration-specific decision by empowered authority, based on current evidence and recorded residual obligations.
- `TRIGGER`: External acquirer/operator; regulated or safety system; contractual deliverable; irreversible cutover; transfer between organisations.
- `CHEAP_PATH`: Internal reversible software release can use automated release criteria and product-owner/operational approval without a separate ceremony.
- `REVERSIBILITY_PROFILE`: R2–R4 strong where custody, liability or operations transfer; R0–R1 can use lightweight automated promotion.
- `REQUIRED_PRECONDITIONS`: Identified deliverable; criteria agreed before decision; verification/validation evidence; authority; exception disposition; audit trail.
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_CONTRACTUAL_SUPPORT
- `CRITICISMS`: Acceptance can be legal/formal rather than engineering truth; buyer sign-off does not prove fitness or certification.
- `ANTI_CEREMONY_BOUNDARY`: The property is authorised transfer over an identified state; a final meeting, certificate or customer signature form is not inherently sufficient.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P012 validation; EW-P015 certification; formal acceptance can conflict with continuous deployment.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Who is empowered to accept which exact configuration, under what criteria and exceptions?
  - Is acceptance evidence separate from verification, validation and certification rather than collapsed into 'passed tests'?

### EW-P015 — Certification basis and regulatory-authority coupling

- `FAILURE_MODE`: Operating without legal authority; evidence not aligned to certification basis; changes invalidate approval; authority sees changes too late.
- `MATURE_FORM`: Lifecycle-neutral engineering that satisfies a specific certification basis for identified configurations and maintains authority after change.
- `TRIGGER`: Legally regulated system; safety or environmental externality; airworthiness/type approval/licensing; public infrastructure.
- `CHEAP_PATH`: No trigger where no empowered external certification regime applies; do not invent an internal 'certification' label.
- `REVERSIBILITY_PROFILE`: R3–R4; sometimes R2 for regulated digital services. No general R0–R1 trigger.
- `REQUIRED_PRECONDITIONS`: Correct legal/domain expertise; early authority agreement; configuration/evidence trace; independent assessment where required; change visibility.
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_LEGAL_AND_STANDARD_SUPPORT
- `CRITICISMS`: Domain-specific obligations cannot be generalised; authority approval may lag technical reality or inhibit beneficial change.
- `ANTI_CEREMONY_BOUNDARY`: The property is alignment with an actual empowered regime; an internal badge, generic compliance checklist or 'certified' document is not general engineering.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 delivery speed; EW-P008 change control; legal authority can conflict with rapid iteration.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Is an actual external authority and certification basis present, or is 'certification' being used rhetorically?
  - Are changes mapped to reapproval/continued-authority obligations for the exact deployed configuration?

### EW-P016 — Independent technical challenge and IV&V

- `FAILURE_MODE`: Self-confirming evidence, conflicted risk acceptance, unchallenged assumptions, management pressure and false closure.
- `MATURE_FORM`: Independence is a designed property—responsibility, incentives, funding, reporting and corrective-action authority—scaled to consequence and integrated early.
- `TRIGGER`: High criticality; novel or complex system; public/third-party risk; strong schedule incentives; many suppliers; opaque evidence; regulatory mandate.
- `CHEAP_PATH`: Low-consequence reversible work can use peer review, rotation, automated checks and occasional external review rather than a standing IV&V organisation.
- `REVERSIBILITY_PROFILE`: R3–R4 strongest; R2 where security/public risk or conflict exists; R0–R1 usually lightweight challenge.
- `REQUIRED_PRECONDITIONS`: Access to products/data; competence; protected escalation; technical/managerial/financial independence proportionate to risk; coordination and feedback channel.
- `EVIDENCE_STRENGTH`: C_MIXED_EMPIRICAL_STRONG_DOMAIN_RATIONALE
- `CRITICISMS`: Comparative outcome and return-on-cost evidence are mixed; independence can reduce feedback speed and may not improve reliability.
- `ANTI_CEREMONY_BOUNDARY`: The property is credible independent challenge; a different team name, audit meeting or mandatory full duplicate lifecycle is not sufficient.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 team flow; EW-P024 proportionality; separation can conflict with rapid collaborative feedback.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Could the people making the claim suppress, redefine or accept their own failure evidence?
  - Is reviewer independence sufficient for challenge but close enough for timely access and feedback?

### EW-P017 — Demonstrable bidirectional traceability

- `FAILURE_MODE`: Orphan requirements, unexplained implementation, untested obligations, missed impact and evidence attached to wrong requirement/configuration.
- `MATURE_FORM`: Trace the claims whose loss would impair a real decision; maintain evidence of link quality rather than maximising link count.
- `TRIGGER`: Certification; high coupling; long-lived system; supplier handoff; safety/hazard chains; expensive impact analysis; many variants.
- `CHEAP_PATH`: For small rapidly changing software, issue/commit/test naming, executable specifications, types and dependency graphs may provide sufficient native trace.
- `REVERSIBILITY_PROFILE`: R0 native/light; R1 selective; R2–R4 stronger where impact/evidence decisions are costly, but maintenance burden also rises.
- `REQUIRED_PRECONDITIONS`: Stable identifiers; clear semantics; automated capture where possible; ownership; quality checks; actual use in decisions; cost budget.
- `EVIDENCE_STRENGTH`: C_MIXED_EMPIRICAL_SUPPORT
- `CRITICISMS`: Laboratory benefits assume correct complete traces; industrial causal evidence and net lifecycle return remain limited.
- `ANTI_CEREMONY_BOUNDARY`: The property is demonstrable relation for a decision; a spreadsheet or universal end-to-end matrix is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 automation; EW-P005 documentation burden; exhaustive traceability conflicts with change speed.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Which concrete decisions consume each trace relation, and what happens if it is stale?
  - Can trace completeness and correctness be checked against live configurations rather than a manually maintained matrix?

### EW-P018 — Safety and hazard analysis with tracked risk controls

- `FAILURE_MODE`: Catastrophic harm despite specification compliance; safety control lost during change; hazard accepted without authority.
- `MATURE_FORM`: Living hazard/control claims tied to actual configurations, operations, evidence and residual-risk authority.
- `TRIGGER`: Potential death/injury, environmental harm, major public loss, high-energy physical system, safety-related software or infrastructure.
- `CHEAP_PATH`: No trigger for ordinary low-consequence functionality; proportionate product/security risk analysis may replace formal system-safety machinery.
- `REVERSIBILITY_PROFILE`: R4 primary; R3 where public/regulated consequences; selected R2 security/privacy. No general R0 trigger.
- `REQUIRED_PRECONDITIONS`: Competent multidisciplinary analysis; operational input; authority; configuration/trace links; incident learning; credible severity/likelihood treatment.
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_LEGAL_AND_FAILURE_SUPPORT
- `CRITICISMS`: Formal analyses can create false precision and omit unknown/organisational hazards; compliance can displace real challenge.
- `ANTI_CEREMONY_BOUNDARY`: The property is active hazard control; a hazard-log template or safety review board is not sufficient.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 speed; EW-P019 assurance case; formal safety burden can conflict with adaptation.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Are material hazards linked to implemented controls and evidence on the actual system?
  - Who is authorised to accept residual risk, and is that acceptance revisited after change or operational evidence?

### EW-P019 — Assurance or safety case as a living claims–argument–evidence structure

- `FAILURE_MODE`: Evidence warehouse without a coherent claim; unsupported leaps; hidden assumptions; authority cannot see why evidence is sufficient.
- `MATURE_FORM`: Use structured argument only where it changes risk decisions, expose assumptions/defeaters, and distinguish the case from its report.
- `TRIGGER`: Novel high-consequence system; non-prescriptive regulation; heterogeneous evidence; residual risk requiring an accountable judgement.
- `CHEAP_PATH`: Stable low-risk products can use concise control/evidence summaries; do not construct a graphical assurance case merely to satisfy a style.
- `REVERSIBILITY_PROFILE`: R3–R4; sometimes R2 for consequential security/AI/public systems. Usually no R0–R1 trigger.
- `REQUIRED_PRECONDITIONS`: Claims with scope; credible evidence; independent challenge; configuration/version links; operational updates; willingness to record doubt and counterevidence.
- `EVIDENCE_STRENGTH`: C_STRONG_DOMAIN_GUIDANCE_WEAK_OUTCOME_EVIDENCE
- `CRITICISMS`: Direct comparative outcome evidence is weak; a polished argument can launder weak premises and consume disproportionate effort.
- `ANTI_CEREMONY_BOUNDARY`: The property is challengeable assurance reasoning; a large report, graphical notation or fixed milestone submission is not inherently required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 continuous evidence; EW-P005 documentation burden; argument completeness can conflict with delivery latency.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Is the assurance case a live argument that can reveal a failed claim, or a static persuasive dossier?
  - Are evidence and assumptions tied to the current configuration and operational context?

### EW-P020 — Anomaly, problem-report, deviation, waiver and corrective-action provenance

- `FAILURE_MODE`: Defect silently deferred; waiver applied to wrong configuration; recurring failure; test pass obtained by changing expectation; root cause never addressed.
- `MATURE_FORM`: One material problem identity from detection through authorised disposition and verified correction, linked to configuration and evidence.
- `TRIGGER`: Safety/mission/quality consequence; repeated releases; supplier defects; certification/acceptance exceptions; operational incidents.
- `CHEAP_PATH`: Low-risk local bugs can use an issue tracker and automated regression test; do not convene a discrepancy board for every defect.
- `REVERSIBILITY_PROFILE`: R1–R4 progressively stronger; R0 normal issue/test path.
- `REQUIRED_PRECONDITIONS`: Non-punitive reporting; configuration identity; severity criteria; closure authority; root-cause competence; feedback into requirements/hazards/tests.
- `EVIDENCE_STRENGTH`: B_STRONG_CROSS_DOMAIN_MECHANISTIC_SUPPORT
- `CRITICISMS`: Formal corrective-action systems can prioritise closure statistics over learning and impose disproportionate burden.
- `ANTI_CEREMONY_BOUNDARY`: The property is durable problem/exception provenance and closure; a standing board or mandatory form is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 flow; EW-P024 proportionality; full provenance can burden minor issue handling.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Can every accepted deviation or unresolved anomaly be tied to the exact configuration and authority?
  - Is closure verified by evidence, or inferred from ticket status and meeting approval?

### EW-P021 — Evidence-backed, event-driven commitment reviews

- `FAILURE_MODE`: Production, deployment, procurement or certification commitment without enough knowledge; gate passes because stopping is politically impossible.
- `MATURE_FORM`: A commitment decision—not a lifecycle phase—whose strength matches the cost and consequence of being wrong.
- `TRIGGER`: Capital, production, long-lead procurement, fleet deployment, irreversible migration, safety authority, major supplier or contractual commitment.
- `CHEAP_PATH`: Continuous low-risk software work can use automated promotion rules and lightweight asynchronous review; no milestone meeting is needed.
- `REVERSIBILITY_PROFILE`: R3–R4 primary; selected R2 cutovers. R0–R1 should normally use continuous policy gates.
- `REQUIRED_PRECONDITIONS`: Decision authority able to stop/change course; independent challenge; current actual-state evidence; transparent criteria; no automatic schedule pass.
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_CRITICAL_SUPPORT
- `CRITICISMS`: Phase gates can certify documents rather than products, batch feedback and reward concealment; the review may add no new decision information.
- `ANTI_CEREMONY_BOUNDARY`: The property is a consequential decision based on discriminating evidence with real authority; a board, meeting, colour status or named review is optional.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 flow; EW-P004 experimentation; strong gates can conflict with short feedback and option exploration.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - What irreversible or externally consequential commitment does each gate control?
  - Could the review genuinely stop or redirect work, and does its evidence describe the actual system rather than completed documents?

### EW-P022 — Staged and incremental commitment with option preservation

- `FAILURE_MODE`: Too much capital/supplier/design commitment before evidence; or endless experimentation without converging on an operational system.
- `MATURE_FORM`: Commit evidence, money and authority in slices sized by uncertainty, coupling and reversibility, while preserving coherent system integration.
- `TRIGGER`: High uncertainty plus expensive downstream commitment; modular capability; long lead; production tooling; migration waves; certification increments.
- `CHEAP_PATH`: For cheap reversible changes, ship/test/revert directly rather than inventing formal commitment stages.
- `REVERSIBILITY_PROFILE`: Useful from R1–R4; strongest before R3–R4 commitment. R0 naturally preserves options without formal staging.
- `REQUIRED_PRECONDITIONS`: Modular architecture or separable decisions; incremental acceptance/evidence; funding and contracts that permit revision; explicit option-expiry decisions.
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_TRADITION_AND_DOMAIN_SUPPORT
- `CRITICISMS`: Incrementalisation can increase integration and certification overhead or be impossible for tightly coupled physical systems.
- `ANTI_CEREMONY_BOUNDARY`: The property is bounded commitment and retained alternatives; arbitrary phases, quarterly gates or a fixed increment length are not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P009 interface stability; EW-P013 qualification; increment overhead can conflict with economies of scale.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does the lifecycle delay the specific irreversible choices that uncertainty makes dangerous?
  - Are increments independently integrable/evaluable, or merely administrative slices of one late integration?

### EW-P023 — Incremental, concurrent and recursive lifecycle application

- `FAILURE_MODE`: One giant final integration, subsystem handoffs, local completion without system progress and inability to adapt lifecycle to element risk.
- `MATURE_FORM`: Lifecycle processes are obligations and feedback loops applied where needed, not calendar phases traversed once.
- `TRIGGER`: Any non-trivial system with elements/increments, especially differing technologies, suppliers or release cadences.
- `CHEAP_PATH`: A tiny product need not model recursive lifecycle structure explicitly; normal iterative work can realise the property.
- `REVERSIBILITY_PROFILE`: All bands; degree of formal coordination increases from R1 to R4.
- `REQUIRED_PRECONDITIONS`: Clear system boundaries; integration cadence; shared configuration/evidence; ownership across levels; tailored coordination.
- `EVIDENCE_STRENGTH`: A_STRONG_PRIMARY_STANDARDS_AND_HISTORICAL_SUPPORT
- `CRITICISMS`: Concurrency can create rework and coordination load; recursion is not free and does not eliminate architecture dependencies.
- `ANTI_CEREMONY_BOUNDARY`: The property is repeated/recursive fulfilment of responsibilities; separate mini-waterfalls and duplicated stage artefacts are not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P006 baseline coordination; EW-P031 cadence; concurrency can conflict with stable shared interfaces.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Are lifecycle obligations applied per risk/increment/element, or imposed as one project-wide phase sequence?
  - Can evidence and baselines be inherited or reused without duplicating full process stacks?

### EW-P024 — Tailoring and proportionality

- `FAILURE_MODE`: Ceremony independent of risk; skipped critical evidence because template says optional; inconsistent tailoring hidden from authorities.
- `MATURE_FORM`: A transparent control-selection rule with cheap defaults, explicit escalation factors, mandatory legal minima and post-outcome learning.
- `TRIGGER`: Always as a meta-property whenever a lifecycle or assurance control is considered.
- `CHEAP_PATH`: Default lightweight path for local reversible work, with pre-defined escalation triggers rather than case-by-case bureaucracy.
- `REVERSIBILITY_PROFILE`: Meta-profile across R0–R4; establishes the cheap path and escalation.
- `REQUIRED_PRECONDITIONS`: Credible risk/context classification; authority to tailor; feedback on whether controls work; minimum non-tailorable legal obligations identified.
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_STANDARD_AND_DOMAIN_CONVERGENCE
- `CRITICISMS`: Risk classification is uncertain and can be gamed; proportionality can become vague permission for inconsistency.
- `ANTI_CEREMONY_BOUNDARY`: The property is proportional control selection; a tailoring plan or approval board is not inherently required.
- `POSSIBLE_CONFLICTING_PROPERTY`: Potentially conflicts with standardisation, comparability and segregation of duties if tailoring authority is unchecked.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does every control have a cheap non-trigger path and an explicit escalation rationale?
  - Are legal/safety minima distinguished from optional inherited ceremony?

### EW-P025 — Rolling planning, estimate uncertainty and outside-view challenge

- `FAILURE_MODE`: False certainty, narrow intervals, political estimates, local optimism, plan treated as contract with reality, and continued funding because baseline sunk cost is large.
- `MATURE_FORM`: A decision model that exposes uncertainty and changes with evidence, while retaining accountable external commitments where necessary.
- `TRIGGER`: Budget or contract decision; long lead; portfolio trade-off; external dependency; irreversible investment; capacity planning.
- `CHEAP_PATH`: Small reversible work can use short-horizon forecasts and throughput history; avoid elaborate earned-value machinery.
- `REVERSIBILITY_PROFILE`: R2–R4 stronger because coordination/commitment needs forecasts; R0–R1 short-horizon lightweight.
- `REQUIRED_PRECONDITIONS`: Comparable data; transparent assumptions; incentives to report bad news; update cadence; distinction between estimate and target; independent challenge.
- `EVIDENCE_STRENGTH`: B_STRONG_CRITICAL_LITERATURE_WEAK_UNIVERSAL_PREDICTION
- `CRITICISMS`: Estimation evidence is fragmented; outside views do not remove novelty or strategic behaviour; planning overhead may exceed value.
- `ANTI_CEREMONY_BOUNDARY`: The property is decision-relevant forecasting and uncertainty; a massive schedule, single completion date or mandated estimation method is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P002 uncertainty; EW-P021 commitment; forecast stability can conflict with adaptation.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Are targets, commitments and probabilistic forecasts explicitly different objects?
  - Are estimates updated from actuals and challenged by outside/base-rate evidence rather than protected as sunk commitments?

### EW-P026 — Supplier, long-lead and dependency coordination

- `FAILURE_MODE`: Supplier builds to obsolete baseline; data rights missing; long-lead purchase before design maturity; integration mismatch; single-source obsolescence.
- `MATURE_FORM`: Govern external dependency commitments and evidence at the boundary, while minimising imposed internal process.
- `TRIGGER`: Multiple legal organisations/suppliers; custom hardware; long lead; scarce materials; safety evidence from vendors; sustainment dependence.
- `CHEAP_PATH`: Single-team commodity/software dependencies can use lockfiles, service contracts, automated compatibility tests and normal vendor management.
- `REVERSIBILITY_PROFILE`: R3–R4 primary; R2 for external cloud/services; R0–R1 usually cheap.
- `REQUIRED_PRECONDITIONS`: Commercial/legal authority; accessible technical data; interface/configuration identity; supplier incentives; alternative/contingency analysis.
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_INSTITUTIONAL_SUPPORT
- `CRITICISMS`: Heavy supplier governance can reduce innovation and competition; requirements may be frozen to protect contracts.
- `ANTI_CEREMONY_BOUNDARY`: The property is cross-authority dependency control; supplier meetings, mandated data volumes and a universal prime/sub hierarchy are not inherently required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P002 learning; EW-P009 interface stability; contracts can conflict with requirement evolution.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Which dependencies cross organisational/legal boundaries, and what commitments become costly before evidence exists?
  - Can suppliers exchange authoritative interface/configuration/evidence data without adopting all internal ceremony?

### EW-P027 — Transition, operational readiness and cutover control

- `FAILURE_MODE`: Successful component/system test followed by failed cutover, unsafe startup, missing support, wrong configuration or untrained operators.
- `MATURE_FORM`: A risk-scaled decision that actual capability and enabling system are ready, with explicit rollback and residual-risk authority.
- `TRIGGER`: Irreversible or high-impact cutover; physical startup; safety/mission operations; major migration; transfer to a separate operations organisation.
- `CHEAP_PATH`: Small reversible deployments can use automated readiness checks, canaries and on-call confirmation without a review meeting.
- `REVERSIBILITY_PROFILE`: R2–R4; strength rises with cutover irreversibility, data effects, hazard and recovery time.
- `REQUIRED_PRECONDITIONS`: As-deployed identity; rollback/contingency; operational owner; realistic rehearsal; support resources; decision authority.
- `EVIDENCE_STRENGTH`: A_STRONG_DOMAIN_AND_FAILURE_MECHANISM_SUPPORT
- `CRITICISMS`: Readiness reviews can batch releases and become sign-off theatre; continuous services may never have a single transition moment.
- `ANTI_CEREMONY_BOUNDARY`: The property is actual operational readiness; an ORR meeting, slide deck or ceremonial handover is not required.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 deployment cadence; EW-P014 acceptance; readiness control can conflict with continuous flow.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does readiness evidence cover the actual deployment, people, data, procedures and support—not just product test results?
  - Is there a credible abort/rollback decision before the cutover's irreversible point?

### EW-P028 — Rollback, contingency and recovery readiness

- `FAILURE_MODE`: Change is labelled reversible but rollback loses data, worsens hazard, depends on unavailable people/tools or has never been tested.
- `MATURE_FORM`: Demonstrated recovery capability whose evidence is tied to the current architecture, data and operational configuration.
- `TRIGGER`: Operational/data change; service dependency; cyber threat; migration; remote/physical operation; significant outage or safety consequence.
- `CHEAP_PATH`: Truly stateless low-impact experiments may need only one-click revert and normal version history.
- `REVERSIBILITY_PROFILE`: Central to classifying R1–R3; R4 often cannot be rolled back and needs prevention/containment instead.
- `REQUIRED_PRECONDITIONS`: Known state model; backups/alternate capability; observability; access; rehearsals; ownership; time and safety limits.
- `EVIDENCE_STRENGTH`: B_STRONG_RESILIENCE_PRACTICE_SUPPORT
- `CRITICISMS`: Redundancy and rehearsal cost can be high; fallback can increase complexity and attack surface.
- `ANTI_CEREMONY_BOUNDARY`: The property is working recoverability; a contingency document, checkbox backup or claimed rollback is not enough.
- `POSSIBLE_CONFLICTING_PROPERTY`: Redundancy/complexity can conflict with simplicity and cost; rollback may conflict with forward-only migrations.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - What evidence shows rollback or recovery works for the current state, including data and dependencies?
  - Does the claimed reversibility stop at an irreversible side effect such as disclosure, physical action or external transaction?

### EW-P029 — Sustainment, obsolescence and support continuity

- `FAILURE_MODE`: Unsupportable fielded system, obsolete components, missing data rights, unknown fleet configurations, cost growth invisible without baseline.
- `MATURE_FORM`: Through-life ownership and evidence for maintaining, modifying and retiring the actual fielded configuration.
- `TRIGGER`: Long-lived asset; fleet; regulated/safety system; custom hardware; external supplier; high replacement/cutover cost.
- `CHEAP_PATH`: Short-lived commodity software can rely on maintained dependencies, observability and explicit end-of-life policy.
- `REVERSIBILITY_PROFILE`: R3–R4 primary; R2 for durable platforms/services; R0–R1 minimal.
- `REQUIRED_PRECONDITIONS`: Lifecycle ownership/funding; operational data; configuration baseline; supplier/data rights; retirement authority.
- `EVIDENCE_STRENGTH`: B_STRONG_DOMAIN_AND_CURRENT_AUDIT_SUPPORT
- `CRITICISMS`: Long-range sustainment plans are highly uncertain and may entrench legacy systems; review metrics can be gamed.
- `ANTI_CEREMONY_BOUNDARY`: The property is continuing capability and authority; a logistics document or annual review alone is not sufficient.
- `POSSIBLE_CONFLICTING_PROPERTY`: Long-term stability can conflict with rapid technology refresh; sustainment investment competes with replacement.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Who owns support, obsolescence and retirement after initial acceptance?
  - Can the current fielded fleet/configuration and its support obligations be reconstructed?

### EW-P030 — Digital authoritative engineering environment and model governance

- `FAILURE_MODE`: Different disciplines act on incompatible models; model is stale or unvalidated; authority is ambiguous; proprietary tool blocks access; model approval substitutes for reality.
- `MATURE_FORM`: A configuration-controlled, queryable engineering evidence environment with scoped authority and verified correspondence to reality.
- `TRIGGER`: Many disciplines/models; complex interfaces; long lifecycle; supplier data exchange; expensive manual consistency checking.
- `CHEAP_PATH`: Small software products can use source, tests, schemas and deployment manifests as native authoritative artefacts without an MBSE platform.
- `REVERSIBILITY_PROFILE`: R2–R4 more likely to justify investment; R0–R1 usually native code/data tools.
- `REQUIRED_PRECONDITIONS`: Clear authority boundaries; common identifiers/semantics; tool interoperability; model validation; configuration management; culture/workflow adoption; physical readback.
- `EVIDENCE_STRENGTH`: C_MIXED_EMPIRICAL_AND_PRACTICE_EVIDENCE
- `CRITICISMS`: Systematic reviews find many benefits are perceived rather than measured; digital models can become more opaque ceremony than documents.
- `ANTI_CEREMONY_BOUNDARY`: The property is governed authoritative information and consistency; buying an MBSE tool, drawing SysML or declaring an ASoT is not the property.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P005 maintenance burden; EW-P031 lightweight tooling; central model authority can conflict with local autonomy.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Which data/model is authoritative for which claim, and how is disagreement reconciled?
  - What proves that the model corresponds to the as-built/as-deployed system rather than only to approved intent?

### EW-P031 — Continuous integration, automated evidence and continuous assurance

- `FAILURE_MODE`: Assurance package proves an old build; integration errors accumulate; security/operational feedback arrives after release; manual evidence cannot keep pace.
- `MATURE_FORM`: Continuous, configuration-linked evidence with explicit coverage limits, risk gates, monitoring and human/independent authority at consequential boundaries.
- `TRIGGER`: Frequent software change; automatable tests; digital deployment; cyber threat; many integrations; need for rapid remediation.
- `CHEAP_PATH`: Where deployment is rare/physical and tests cannot be automated, use periodic integration but automate provenance and repeatable analyses where possible.
- `REVERSIBILITY_PROFILE`: R1–R3 strongest for software; supports R4 evidence but cannot remove physical/certification constraints.
- `REQUIRED_PRECONDITIONS`: Reliable tests and environments; reproducible builds; secure pipeline; evidence semantics; observability; segregation/authority where needed; human review of non-automatable claims.
- `EVIDENCE_STRENGTH`: B_STRONG_MODERN_GUIDANCE_MIXED_EMPIRICAL_OUTCOMES
- `CRITICISMS`: CI/CD empirical evidence is heterogeneous; continuous does not mean complete, independent or certified, and infrastructure cost can be large.
- `ANTI_CEREMONY_BOUNDARY`: The property is fresh reproducible evidence and rapid integration; a branded DevSecOps platform, dashboard or 'continuous compliance' claim is not enough.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P016 independence; EW-P015 certification; cadence can conflict with review and qualification latency.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Is evidence generated from the exact immutable release and kept fresh as it changes?
  - Which high-consequence claims still require independent or non-automated judgement beyond pipeline pass/fail?

### EW-P032 — Risk ownership, residual-risk decision and operational authority

- `FAILURE_MODE`: Risk implicitly accepted by developers, responsibility diffused, authority signs without evidence, or operation continues outside approved context.
- `MATURE_FORM`: Configuration- and context-specific authority that consumes fresh evidence, records residual risk and can stop or constrain operation.
- `TRIGGER`: Material safety, security, privacy, mission, financial or public risk; operation beyond local team; conditional/temporary approval.
- `CHEAP_PATH`: Low-consequence reversible changes can operate under pre-authorised risk tolerances with automated monitoring.
- `REVERSIBILITY_PROFILE`: R2–R4 according to consequence; R0–R1 usually delegated tolerances.
- `REQUIRED_PRECONDITIONS`: Authority actually controls operation/resources; current evidence; transparent criteria; escalation/stop power; operational monitoring; independence where needed.
- `EVIDENCE_STRENGTH`: A_STRONG_CROSS_DOMAIN_AUTHORITY_SUPPORT
- `CRITICISMS`: Individual sign-off can centralise power, encourage blame and add latency; no authority can make unknown risk safe by declaration.
- `ANTI_CEREMONY_BOUNDARY`: The property is accountable authority over real operation; a signature block or governance title alone is not enough.
- `POSSIBLE_CONFLICTING_PROPERTY`: EW-P031 flow; EW-P024 delegated tailoring; authority can conflict with team autonomy.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Who can accept residual risk for the exact operation/configuration, and do they possess stop authority?
  - Is approval bounded by conditions, expiry and monitoring, or treated as permanent absolution?

### EW-P033 — Reversibility- and commitment-sensitive control strength

- `FAILURE_MODE`: Over-control cheap experiments; under-control irreversible/public changes; confuse edit cost with propagation, commitment-unwind or failure/recovery cost.
- `MATURE_FORM`: A falsifiable control-selection policy: identify the failure mode, trigger dimensions, cheap path, required evidence and residual risk; re-evaluate after operational feedback.
- `TRIGGER`: This is a meta-property applied whenever choosing baseline, trace, review, independence, qualification or authorisation strength.
- `CHEAP_PATH`: Default pre-authorised path for local, low-consequence, rapidly observable and genuinely reversible work.
- `REVERSIBILITY_PROFILE`: Meta-profile R0–R4; consequence, coupling and irreversible effects can override technical rollback.
- `REQUIRED_PRECONDITIONS`: Operational definition of reversibility; tested recovery; impact visibility; clear thresholds; feedback on false positives/negatives; legal minima.
- `EVIDENCE_STRENGTH`: B_STRONG_CROSS_DOMAIN_CONVERGENCE_THRESHOLD_UNRESOLVED
- `CRITICISMS`: Evidence does not support one universal monotonic formula; irreversible systems can still be harmed by bureaucracy, and reversible software can create irreversible disclosure or transaction effects.
- `ANTI_CEREMONY_BOUNDARY`: The property is proportional selection tied to a real failure mode; a risk matrix, phase label or 'high assurance' designation is not sufficient.
- `POSSIBLE_CONFLICTING_PROPERTY`: Stability versus adaptability; assurance latency versus threat/feedback speed; standardisation versus tailoring.
- `QUESTIONS_FOR_REPOSITORY_AUDIT`:
  - Does control strength rise because a named failure becomes harder or more consequential—not merely because a phase is later?
  - Is there a genuinely cheap path for local reversible work, and are irreversible side effects distinguished from code rollback?

## CEREMONIES_TO_NOT_BLINDLY_ADOPT

- Giant requirements specification
- Requirements-complete gate
- Preliminary/Critical Design Review meeting
- Fixed phase gate
- Traceability matrix spreadsheet
- Standing Change-Control Board
- Static configuration baseline document
- Interface Control Document
- Interface Control Working Group/Board
- Monolithic final test phase
- Independent V&V organisation
- Safety-case report / GSN diagram
- Formal evidence package
- Pilot project / MVP phase
- Qualification campaign
- Acceptance certificate/signature
- Operational Readiness Review meeting
- Contingency/rollback plan document
- MBSE platform / 'single source of truth'
- Continuous-compliance dashboard

## CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

- Disposable local exploration with no external promise, shared dependency, persistent data effect or material consequence.
- Changes that are rapidly observable, automatically verifiable and genuinely reversible in both technical state and external effect.
- Low-coupling work where ordinary version control, tests and peer review already provide the required identity and evidence.
- Exploratory requirements or architectures not yet promoted to an authoritative commitment.
- Situations where the control would delay security, safety or operational remediation more than it reduces risk.
- Contexts lacking the preconditions that make the evidence truthful—current configuration identity, maintained links, competent reviewers or an actual acceptance authority.

## HIGH_CONSEQUENCE_ONLY_PROPERTIES

- [EW-P007](#property-ew-p007) — As-designed, as-built, as-tested and as-deployed reconciliation
- [EW-P013](#property-ew-p013) — Qualification envelope and margin evidence
- [EW-P015](#property-ew-p015) — Certification basis and regulatory-authority coupling
- [EW-P016](#property-ew-p016) — Independent technical challenge and IV&V
- [EW-P018](#property-ew-p018) — Safety and hazard analysis with tracked risk controls
- [EW-P019](#property-ew-p019) — Assurance or safety case as a living claims–argument–evidence structure
- [EW-P027](#property-ew-p027) — Transition, operational readiness and cutover control
- [EW-P032](#property-ew-p032) — Risk ownership, residual-risk decision and operational authority

## PROPERTIES_WITH_STRONG_EMPIRICAL_OR_DOMAIN_SUPPORT

- [EW-P004](#property-ew-p004) — Executable risk retirement through prototypes, pilots, simulation and thin increments
- [EW-P006](#property-ew-p006) — Configuration identification and baseline authority
- [EW-P008](#property-ew-p008) — Change visibility, impact analysis and risk-proportional authorisation
- [EW-P009](#property-ew-p009) — Interface definition, ownership and compatibility control
- [EW-P010](#property-ew-p010) — Verification planning and requirement testability
- [EW-P011](#property-ew-p011) — Multi-level verification and integration evidence
- [EW-P012](#property-ew-p012) — Intended-use and operational-context validation
- [EW-P013](#property-ew-p013) — Qualification envelope and margin evidence
- [EW-P015](#property-ew-p015) — Certification basis and regulatory-authority coupling
- [EW-P018](#property-ew-p018) — Safety and hazard analysis with tracked risk controls
- [EW-P022](#property-ew-p022) — Staged and incremental commitment with option preservation
- [EW-P023](#property-ew-p023) — Incremental, concurrent and recursive lifecycle application
- [EW-P024](#property-ew-p024) — Tailoring and proportionality
- [EW-P027](#property-ew-p027) — Transition, operational readiness and cutover control
- [EW-P032](#property-ew-p032) — Risk ownership, residual-risk decision and operational authority

## PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

- [EW-P016](#property-ew-p016) — Independent technical challenge and IV&V
- [EW-P017](#property-ew-p017) — Demonstrable bidirectional traceability
- [EW-P019](#property-ew-p019) — Assurance or safety case as a living claims–argument–evidence structure
- [EW-P030](#property-ew-p030) — Digital authoritative engineering environment and model governance
- [EW-P025](#property-ew-p025) — Rolling planning, estimate uncertainty and outside-view challenge
- [EW-P033](#property-ew-p033) — Reversibility- and commitment-sensitive control strength

## UNRESOLVED_PROPERTIES

- **EW-P016 — Independent technical challenge and IV&V**: Which independence dimensions and scope yield net value by risk class? Modern comparative evidence remains sparse.
- **EW-P017 — Demonstrable bidirectional traceability**: What is the minimum valuable trace set, how should decay be measured, and when do native executable links outperform explicit links?
- **EW-P019 — Assurance or safety case as a living claims–argument–evidence structure**: Does a structured case measurably outperform well-designed hazard/evidence management, and how should uncertainty/defeaters be represented?
- **EW-P025 — Rolling planning, estimate uncertainty and outside-view challenge**: Which estimation practices improve real decisions rather than reported calibration, especially in novel programmes?
- **EW-P030 — Digital authoritative engineering environment and model governance**: What measurable decision/outcome improvements justify model cost, and how should confidence and physical/deployed divergence be represented?
- **EW-P033 — Reversibility- and commitment-sensitive control strength**: No validated general threshold function exists. Domain-specific calibration, interactions and automation effects remain unresolved.

## Final crosswalk instruction

The later repository auditor should test each property natively rather than searching for traditional names or artefacts. It should ask whether an existing mechanism already closes the failure mode; whether authority is connected to live implementation; whether verification, validation, qualification, acceptance and certification remain distinct; whether control strength changes with real consequence and commitment; and whether a proposed addition changes a decision or merely adds ceremony. This external lane does not answer those target-system questions.

```text
EVOLVED_WATERFALL_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 38
PROPERTY_POPULATION_EXAMINED: 38
PROPERTY_COVERAGE: 38/38
EVOLVED_WATERFALL_AUDIT_INTAKE: COMPLETE
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
```
