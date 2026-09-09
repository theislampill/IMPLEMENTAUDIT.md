# EVOLVED_SOFTWARE_ARCHITECTURE_PUBLIC_DOCUMENTATION_INTAKE

Revision **ESA-2026-09-06-r1** · research cut-off **6 September 2026**.

## Introduction suitable for public documentation

Software Architecture is an established research and engineering tradition concerned with consequential software organisation, interaction, decisions and qualities. Its genealogy is plural: abstraction and information hiding, program families and reuse, conceptual integrity, component-and-connector styles, multiple views, architectural languages, scenario-based evaluation, decision knowledge, conformance and revision address related but different problems. The 1990s architecture literature made those system-level questions explicit without inventing all their earlier mechanisms. Later architecture-description standards organise descriptions; they do not certify the quality of the described system. [ESA-S001, decomposition criteria; ESA-S002, foundations; ESA-S004, styles; ESA-S011/012/065, inspected introductory scope and official abstracts.]

**Evolved Software Architecture** is the analytical name for this study’s criticism-tested reconstruction, not an established academic school. The reconstruction connects consequential concerns to interface and dependency reasoning, measurable quality scenarios, feasible alternatives, accountable decisions, implementation and revisable evidence of real effects. It treats formal models, workshops, diagrams, decision records, microservices and runtime controllers as conditional instruments rather than universal requirements. This composed account is source-grounded analysis; its assembled effectiveness has not been experimentally established.

## What evolved under criticism

The enduring problem behind modularity is not how to maximise component count. It is how to protect selected obligations from likely changes while preserving the semantics on which clients rely. Mismatch experience shows why matching interfaces or separately deployed parts can still carry incompatible assumptions. The mature form therefore couples boundaries to the change, failure or interaction they are supposed to contain. It permits an ordinary module, direct call or modular monolith when distribution supplies no needed independence. [ESA-S001, criteria and worked alternatives; ESA-S026, mismatch case; ESA-S038/039, project accounts.]

Quality reasoning also becomes narrower and stronger under criticism. A quality label must lead to a scenario and observable response; a tactic must have an explanatory mechanism; an apparent improvement must respect other constraints and the actual measurement boundary. Workshops and architecture reviews can improve understanding and expose risks without predicting every operating condition. The examined comparative evidence is too small and setting-bound to support universal method superiority. [ESA-S016/017, tactic and scenario methods; ESA-S020/021, method and risk-theme study; ESA-S023, experiment/results/validity threats.]

Description and governance practices survive when they have a consumer. Kruchten’s 4+1 approach does not require every view in every case. Concise decision records can preserve knowledge without a large architecture repository, but a completed record is not proof that a decision was sound or remains current. Conformance checking can reveal a meaningful deviation, yet a justified improvement may require changing the old rule rather than the new implementation. This is not an argument against documentation or analysis: it is an argument against confusing an artefact with the function it should serve. [ESA-S003, view selection; ESA-S027/029, rationale and records; ESA-S045, mapped conformance.]

Runtime adaptation makes the same distinction operational. A model must correspond to the running system; an action must be allowed and effectively executed; its consequences must then be observed. A controller’s improved local score cannot establish that it preserved an external constraint. Negative robustness experiments demonstrate that architectural-state problems can undermine adaptation. This finding narrows the assurance claim; it does not prove that all self-adaptation fails. [ESA-S051–054, runtime mechanisms and robustness evaluation.]

## The composed account in ordinary language

Start wherever the consequential uncertainty occurs, not necessarily with a prescribed first document. A user concern can expose a quality conflict; a failed deployment can expose a hidden dependency; a new variant can invalidate an old interface assumption; an automated check can expose an obsolete rule. The appropriate actors then investigate the affected choice, compare feasible alternatives and act within their actual authority. A description or decision record communicates what later consumers need. Observation can revise the choice, its explanation, the baseline, or the need for the control itself.

This permits loops, branches and concurrent local work. Analysis, design and evaluation interleave rather than forming a mandatory one-pass pipeline. The smallest coherent form may be a short discussion, an explicit constraint, a local design choice and a focused check of the effect. Richer methods become appropriate when the stakes, uncertainty or coordination problem justify them. One existing mechanism can serve several concerns; a property ledger does not imply one new control or owner per row. [ESA-S025, interleaved design model; ESA-S010, architect roles; ESA-S029, concise records. The combined minimal form is this study’s analytical synthesis.]

The distinction among understanding, authorisation and success is essential. Discovering a risk does not authorise an architect to accept it for others. Approval does not show that an implementation occurred. A successful change under one workload does not establish performance under another. Software architecture contributes to those judgements without becoming a universal organisational or political decision rule.

## Strongest surviving properties

The strongest retentions are consequence-linked concerns; distinguishing architecture, description and belief; change-oriented information hiding; semantic interface assumptions; typed dependencies; measurable quality scenarios; explicit quality trade-offs; representative operating observations; and correspondence among views and realisation. Their IDs are **ESA-002, ESA-003, ESA-007, ESA-008, ESA-010, ESA-014, ESA-017, ESA-018 and ESA-021**.

These are strongest as bounded functions, not as universal effect sizes. Other useful mechanisms remain conditional: evaluation methods, rationale records, conceptual integrity, architecture debt analysis, incremental migration, conformance checks, fitness functions, family design, REST/service constraints, runtime adaptation and appropriate deployment boundaries. Formal connector reasoning has a particularly clear model-relative guarantee, but its assumptions and implementation mapping must survive transfer. [ESA-S015, §8/Theorem 1; complete source/property records for the other mechanisms.]

## Caricatures and ceremonies to avoid

Do not present architecture as all important work, compulsory central approval, a full 4+1 document set, the largest possible number of services, or the absence of emergent design. Do not treat a risk review as an operating-quality certificate, a description standard as a design-quality guarantee, a smell score as architectural truth, or a historical deviation as automatically harmful erosion. Do not equate organisational correlation with a deterministic law.

The alternative is not “no reasoning”. It is proportionate reasoning with an actual consumer, an observable consequence and a retirement condition. Documents, meetings and formal models can be the economical choice when turnover, high consequences, difficult interactions or many independent participants make informal alternatives inadequate.

## Citation-ready factual claims

The following factual formulations are bounded to the inspected sources. They can be used with the named source IDs and locators; the source table supplies exact bibliographic records and URLs. Statements of this study’s synthesis are separately labelled.

| Claim | Source and inspected locator | Necessary qualification |
|---|---|---|
| Parnas’s modularisation account contrasts processing-oriented decomposition with responsibility allocation that hides design choices expected to change. | ESA-S001, pp. 1053–1058, alternatives and criteria. | A worked mechanism illustration, not a representative industrial effect estimate. |
| The uses relation in the examined family-design work is not simply a procedure-call relation. | ESA-S006, uses relation and extension/contraction discussion. | The relevant relation depends on the architectural question. |
| Perry and Wolf’s account treats architectural elements, form and rationale as related subjects. | ESA-S002, foundations/model discussion. | One foundational account, not the only accepted definition. |
| Kruchten’s 4+1 description allows unnecessary views to be omitted. | ESA-S003, view selection and iterative approach. | The scheme is not a universal five-artefact obligation. |
| Architectural mismatch can arise from assumptions carried by otherwise reusable components. | ESA-S026, Aesop experience and mismatch categories. | Repeated publications of this case are not independent replications. |
| The examined Wright result is conditional on well-formedness and compatibility assumptions. | ESA-S015, §8, Theorem 1 and counterexample. | Compatibility alone is insufficient; the result concerns a CSP model. |
| The SEI risk-theme study examines 18 ATAM reports containing 99 themes. | ESA-S021, sample/method and risk-theme analysis. | It does not randomise review treatments or establish downstream operating benefit. |
| The 2017 internal replication uses 16 convenience-sampled practitioner students and does not detect an efficiency/ease advantage for the compared method. | ESA-S023, experimental design, results and threats. | A small task study; absence of detection is not a precise estimate of no effect everywhere. |
| The inspected rationale survey contains 81 valid responses. | ESA-S027, methodology and results of the actual 2005 report. | Reported perceptions and practices are not causal documentation benefits. |
| The socio-technical congruence study examines modification requests within one organisation. | ESA-S031, study design and statistical analysis. | Observational association, not proof that reorganising teams causes a particular architecture. |
| Reflexion models depend on mappings between a high-level account and extracted source relations. | ESA-S045, mapping/reflexion model definition. | They do not automatically recover intended rationale or every runtime relation. |
| Istio’s consolidation account concerns its control plane while retaining separate data-plane proxies. | ESA-S039, istiod motivation and architecture description. | It is not a general demonstration against microservices. |
| The examined architecture-debt study develops a qualitative model across seven sites in five companies. | ESA-S050, methods and model development. | It does not establish universal monetary debt interest. |
| The 2024 microservice survey combines 35 earlier responses and 18 new ones. | ESA-S060, survey design and sample construction. | New-question denominators can be 18; responses are not all independent new observations. |
| EcoFaaS evaluates energy and latency under declared workloads and SLO assumptions, with mean-latency costs relative to a baseline. | ESA-S061, evaluation setup and latency/energy results. | Measured component energy is not whole-lifecycle carbon. |
| The 2026 architectural-pattern study uses one execution per configuration and identifies unreliable self-reported metrics. | ESA-S062, experiment, metric analysis and threats. | It does not establish deployed autonomous architectural competence. |
| The inspected IEEE/ISO materials concern architecture description. | ESA-S065/012 official abstracts; ESA-S011 introductory preview. | No unread normative clause or design-quality certification is claimed. |

**Analytical claim, not an established empirical finding:** the examined mechanisms can be composed into a conditional system that links concerns, choice, legitimate action and observed consequences while selecting rather than accumulating architecture machinery. The composition’s definitions, guards and cases appear in the frozen report and machine-readable model.

## Evidence limits and current research frontier

The corpus contains 68 examined candidates and 66 exact source records, not 68 requirements or 66 independent experiments. Fifty-five candidates are crosswalk-worthy under their triggers. Thirteen are rejected, ceremonial, non-general, superseded or unresolved. Every candidate remains in the denominator; favourable summaries do not replace the full ledger.

Historical arguments and standards can establish concepts without demonstrating outcomes. Formal validity can be strong inside an inadequate model. Field accounts can show a useful possibility or failure without identifying prevalence. Small comparisons can reveal a discriminating result without settling general effectiveness. Shared programmes, reused datasets, selected benchmarks, incomplete communication logs, proxy metrics and publication/selection bias all limit transfer. Inaccessible texts are disclosed access limits, not evidence that a claim is false.

Current work includes LLM-assisted evaluation and design, automated reconstruction/decomposition, architecture for learned systems, self-adaptation and sustainability. The 2026 evidence examined here is useful but narrower than the strongest promotional claims. Open-ended autonomous architecting remains **ESA-060: UNRESOLVED**. This is an examined uncertainty, not a proof of impossibility or a deferred literature search. [ESA-S047; ESA-S055–056; ESA-S058–063.]

## Suggested public page outline

1. What software architecture studies, with the distinction from architecture description.
2. A plural genealogy: decomposition, styles, qualities, decisions, correspondence and revision.
3. The conditional composed account and its smallest coherent form.
4. A few discriminating cases: hidden shared state, obsolete conformance rules and quality trade-offs.
5. Optional branches and their triggers, including formal models and runtime adaptation.
6. Criticism, evidence boundaries and current open questions.
7. Links to the complete candidate ledger, source table and composition model.

## Claims not to make

Do not invent an academic origin or consensus for “Evolved Software Architecture”. Do not claim that the composition has demonstrated universal superiority, that a formal model guarantees an unmodelled deployment, or that a review predicts every workload. Do not infer economic or sustainability superiority from isolated field cases, popularity, a brand or a standard.

Do not describe every microservice as independent, every bounded context as a service, every deviation as erosion, or every imperfection as technical debt. Do not present all original books or full standard clauses as read. Do not treat the number of sources as the number of independent replications. Do not present generated diagrams, confident rationale or self-reported metrics as operating validation. Do not assert adoption, implementation or benefit in an unexamined host system.

Public documentation may explain the tradition and this analytical synthesis. Adoption and target-specific outcomes require a separate evidence-bearing account.

## Packet references

[Full report](EVOLVED_SOFTWARE_ARCHITECTURE_FROZEN_REPORT.md) · [Complete property ledger](EVOLVED_SOFTWARE_ARCHITECTURE_PROPERTY_LEDGER.json) · [Exact source table](EVOLVED_SOFTWARE_ARCHITECTURE_SOURCE_TABLE.json) · [Composition model](EVOLVED_SOFTWARE_ARCHITECTURE_COMPOSITION_MODEL.json) · [Research coverage and critical registers](EVOLVED_SOFTWARE_ARCHITECTURE_RESEARCH_COVERAGE.json).
