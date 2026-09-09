# Evolved Process Mining
## Independent tradition study and criticism-tested within-tradition synthesis

**Analytical label:** `EVOLVED_PROCESS_MINING`  
**Revision:** `EPM-R1-2026-09-06`  
**Research cut-off and declared run date:** 6 September 2026  
**Status:** Frozen analytical corpus, subject to the scope and evidence limits below. The manifest supplies the exact-byte inventory and verification record.

“Evolved Process Mining” is the name of this study’s analytical synthesis. It is not presented as the historical name of a recognised academic school. Process Mining is the established subject. The provisional grouping with Business Process Management and Workflow Management organises a possible later comparison; no sibling corpus was consulted and no cross-tradition synthesis or target adoption is established.

## Executive judgement

Process mining’s strongest contribution is not a particular diagram, algorithm or promise of organisational transparency. It is the disciplined relation between **event evidence and explicit process representations**: reconstructing behaviour under a declared model language, comparing records with a reference, and using the resulting distinctions to investigate actual work. The field’s founding and later literature contains several different ways to establish those relations. Its scope includes discovery, conformance and enhancement, with organisational, performance and operational-support perspectives. A directly-follows graph is one useful view, not the definition of the whole tradition. [EPM-S001, brochure pp. 1–3; EPM-S002; EPM-S005; EPM-S009]

The surviving system is conditional. An interpretable event population and a justified case or object notion are prior evidential burdens, not facts created by successful import. A discovery guarantee has a model class and assumptions. A conformance result has a reference, mapping and comparison semantics. A delay has recorded endpoints before it has a causal explanation. A prediction must use information available at its declared decision time. A recommendation needs feasibility, authority and effect evidence beyond predictive accuracy. These distinctions are individually supported by the sources; their explicit composition into one account is this study’s contribution. [EPM-S014; EPM-S022; EPM-S039; EPM-S046; EPM-S050; EPM-S027; EPM-S030]

The denominator is **84 candidates, all examined**, including unfavourable outcomes. Twenty-eight are strongly retained, eleven retained in evolved form, fifteen context-dependent, fourteen assumption-sensitive, one domain-specific and one useful but easily gamed. These **70 crosswalk-worthy candidates are not 70 unconditional obligations**. Five candidates are rejected or disfavoured; four have no general property; one is ceremonial; one is a linked duplicate; one unrestricted default is superseded; and two transfer questions remain unresolved. The initial consolidation contained 83 candidates. Composition exposed a distinct additional mechanism, EPM-084, without renumbering or dropping anything.

The two unresolved records concern **broad realised causal benefit of prescription** and **broad external validity of uncertain object-centric analysis**. They are researched limits, not unexamined work. Current methods offer meaningful formal, retrospective and simulation-based results, but those kinds of evidence cannot be substituted for independent operational validation. This corpus found no adequate basis for universal return, universal object-centric superiority, universal deep-model superiority, or an inference from model competence to autonomous operative authority. [EPM-S026; EPM-S027; EPM-S028; EPM-S030; EPM-S043; EPM-S044]

## 1. What the tradition studies—and what it does not

A process-mining analysis relates event evidence to an explicit account of how work can or did unfold. In discovery, the representation is inferred from records. In conformance, records are compared with a supplied or discovered reference. Enhancement uses event evidence to annotate, diagnose or revise a model. These relations distinguish the field from general business metrics, from a workflow engine that enacts a model, and from process modelling based solely on interviews. The boundaries are permeable: useful studies combine these methods. Nevertheless, carrying out a transaction query does not automatically make an activity process mining, and deploying an engine does not establish that its actual executions correspond to the intended model. [EPM-S001, scope and three mining types; EPM-S009; EPM-S036]

The field’s objects are not simply rows. A row may record a status update, an activity completion, an administrative correction, a person’s entry of someone else’s work, or a retrospective summary. Event identity, occurrence time, recording time, lifecycle phase and object participation can therefore differ. A case may be an order, item, encounter, application or some other analytical unit. The process a miner discovers can change when that unit changes, even though no real work has changed. Database extraction and object-centric research make this representational dependence explicit. [EPM-S014, extraction and convergence/divergence; EPM-S024, data model; EPM-S039, timestamp examples]

This matters because the most important error can precede the algorithm. A perfectly implemented miner applied to a convenient but misinterpreted extract can return exactly the model its input supports and still misdescribe work. A successful schema validation establishes structural properties of the representation. An exact hash establishes the identity of bytes. Neither establishes the event-to-work interpretation. The evolved response is not an impossible demand for complete observation. It is to ask which deficiencies matter to the particular claim and whether a narrower, cheaper question can be answered adequately. [EPM-S014; EPM-S016; EPM-S045; analytical adjudication EPM-001–EPM-011]

## 2. A plural historical reconstruction

The early history is not adequately described as one author inventing the entire field and everyone else extending a single algorithm. Cook and Wolf’s 1998 software-process work examines several event-based inference techniques. Agrawal, Gunopulos and Leymann’s 1998 workflow-log paper and Datta’s 1998 probabilistic and algorithmic AS-IS discovery paper provide distinct contemporaneous formulations. Their exact contributions are not made interchangeable: this study accessed the latter two only at abstract and metadata level, so it does not infer their omitted proofs or experimental details. Their presence is sufficient to defeat a single-founder caricature, not to settle every priority dispute. [EPM-S002; EPM-S003, abstract/metadata; EPM-S004, abstract/metadata]

Van der Aalst and collaborators made major contributions to formal workflow mining, conformance, social/resource analysis, research infrastructure, event-data extraction, object-centric approaches and the field’s public articulation. The alpha paper is particularly important because it makes the log-to-model inference and its assumptions explicit. Its value is not that it solved unrestricted reconstruction. The original result concerns a defined model and log setting; later work addresses limitations or chooses different trade-offs. The genealogy therefore records substantial contribution without assigning all later approaches to one undifferentiated lineage. [EPM-S005; EPM-S012; EPM-S014; EPM-S031; EPM-S035; EPM-S036]

The responses to alpha-era limitations are plural. Heuristic discovery uses frequency-sensitive relations to cope with noisy records. Genetic mining searches populations of models under an explicit fitness objective. Fuzzy Mining changes the presentation and abstraction of complex behaviour. Region/ILP discovery formulates a different synthesis problem. Inductive discovery obtains important structural properties through a restricted constructive representation. These mechanisms do not line up on a single maturity ladder: an understandable local view may be preferable to an expensive global model, and a sound structured model may omit a distinction that a more expressive representation can retain. [EPM-S006; EPM-S007; EPM-S008; EPM-S013; EPM-S038; EPM-S049]

Declarative discovery is another important alternative. Rather than prescribe one comprehensive path, it describes behaviour through constraints. This is useful for flexible work, but introduces its own problems: a constraint can appear satisfied because it was never meaningfully activated; a large rule set can be redundant, difficult to understand or problematic in combination. MINERful and semantic-vacuity work belong in the genealogy as mechanisms and criticism, not as evidence that the declarative school universally superseded procedural models. [EPM-S011; EPM-S041; EPM-S042]

Conformance developed in parallel with discovery rather than as an optional score attached to a discovered map. Token replay exposes discrepancies through execution-like accounting. Alignments search for a best correspondence between log and model behaviour under a cost function. Multi-perspective checking brings data guards and other conditions into the comparison. Model repair uses mismatch evidence to revise a model while trying to preserve useful existing structure. The methodological gain is real, but a “best” alignment remains best under the chosen semantics and costs, and repairing a descriptive model does not authorise changing an obligation. [EPM-S009; EPM-S010; EPM-S046; EPM-S047]

The Manifesto consolidated this already plural field and articulated major challenges; it did not create all its mechanisms. Later work expanded the observational object itself: streams rather than completed logs, changing processes rather than one static model, interacting objects rather than one case notion, uncertain events rather than one unquestioned trace, and textual sources rather than ready-made structured records. Each expansion solves some representational problems while adding new assumptions, costs and validation obligations. [EPM-S001; EPM-S025; EPM-S034; EPM-S035; EPM-S037; EPM-S055]

## 3. Reconstructing a usable evidence base

The source chain has two transformations worth keeping distinct. Recording converts aspects of work into records. Extraction converts records into the event representation used by the analysis. Both can omit, duplicate, delay, abstract or correlate information. Reproducing the second transformation cannot establish the first. Conversely, finding one imperfection does not invalidate every question that could be asked of the data. A completion-only log can support a bounded account of recorded milestones while failing to support active service-time estimates. [EPM-S014; EPM-S039; EPM-S045; EPM-S048]

A mature extraction therefore identifies the target question, population, inclusion rules, source keys, relevant joins, lifecycle interpretation and observation window. The analyst should be able to explain a surprising result through selected contributing records, not merely rerun a dashboard. The extent of this trace-back is proportionate: a single source query and a short mapping can suffice for a small inquiry. A large provenance architecture is not a universal prerequisite. The protected function is the ability to investigate the consequential claim. [EPM-S014; EPM-S016; EPM-S036; analytical synthesis EPM-002–EPM-003]

Timestamp quality deserves special attention because event order and interval interpretation are often treated as unproblematic. The timestamp study distinguishes multiple quality dimensions and levels; the digital-hospital study gives concrete manifestations of recording imperfections in one emergency-department dataset. These do not establish a universal defect rate. They establish plausible and observed mechanisms by which time fields can fail to represent the assumed chronology. Arbitrarily breaking ties may be acceptable as an implementation convention, but it must not be silently promoted into a fact about which activity occurred first. [EPM-S039; EPM-S045]

The response to noise is similarly conditional. Cleaning that merely raises conformance can be circular: the process may genuinely depart from the reference, or the reference may be obsolete. A rare path may be a recording error, an important exception or an emerging change. The evolved form preserves a recoverable original, justifies material repairs and tests how conclusions depend on them. Sometimes the proper response is an uncertainty annotation or a narrower question, not an invented replacement event. [EPM-S006; EPM-S025; EPM-S039; EPM-S045]

Event-data standardisation supports interchange, not semantic omniscience. The inspected IEEE record identifies the 2023 XES standard and its scope; the full normative text was not available here, so no unseen clause obligation is asserted. OCEL 2.0 explicitly supports object-centric relationships and changing attributes. A receiving tool still has to preserve the required meanings, and an expressive file can contain erroneous source interpretation just as faithfully as a simple one. Standards are retained for their interoperability function, not as proof of analytical truth or economic superiority. [EPM-S015, official scope/metadata only; EPM-S024]

## 4. Case notions, discovery bias and identifiability

Case-centric logs are powerful when one defensible identifier captures the relation under investigation. They become distorting when shared events are copied across cases or when interacting entities are collapsed into one trace. Convergence and divergence are not merely visual inconveniences: they can alter frequency, apparent rework and time attribution. The correct response is not “always use object-centric mining”, but “identify what the projection preserves and destroys for this question”. [EPM-S014; EPM-S035; EPM-S050]

Object-centric representations retain event identity while linking events to multiple typed objects. Current work also addresses dynamic identity relationships and stronger execution guarantees. Yet object identity must still be established, a representation still selects which relations exist, and different formal models mean different things by soundness. The inspected 2021 preprint and the 2026 identifier-aware construction cannot be treated as one interchangeable theorem. The former’s ambiguous proof-status presentation is not certified in this packet. The latter’s construction provides a scoped guarantee, not a general certificate of correct organisational modelling. [EPM-S024; EPM-S026; EPM-S043; EPM-S044]

Discovery then adds a second layer of selection. A miner chooses a model from a language using an objective and assumptions. A heuristic miner’s threshold, an inductive miner’s construct class, a declarative miner’s templates and an evolutionary miner’s fitness all shape what can be returned. A realistic-looking result is not evidence that this bias disappeared. The comparison study and subsequent methodology work show why model-class differences, failed computations and metric definitions belong in the interpretation, rather than only in technical appendices. [EPM-S019; EPM-S053; EPM-S056]

There is also a basic identification limit. Consider two observed sequences, `ab` and `ba`. They are compatible with concurrent execution of one `a` and one `b`. They are also compatible with an exclusive choice between two sequential branches, one producing `ab` and the other `ba`. This is an analytical probe, not a result about a specific organisation. It illustrates why observing both orders does not, without additional model assumptions, identify the internal mechanism. It does not refute a rediscovery theorem whose admissible class excludes one candidate. The mature conclusion is to preserve what is actually identified and ask for discriminating evidence only when the distinction matters. [Formal scope: EPM-S005; methodological context: EPM-S053; analytical probe EPM-PROBE14 and domain model EPM-DM03]

## 5. Conformance as evidence, not an all-purpose verdict

A conformance result has at least a log, reference, mapping and comparison semantics. An alignment additionally has admissible moves and costs; an approximation has a search or computation limit. A reference can be a description of typical behaviour, an intended process, a technical specification or a model of an externally authorised rule. The same numerical mismatch can therefore mean different things. An analyst must not substitute one interpretation for another merely because the software reports a fitness percentage. [EPM-S009; EPM-S010; EPM-S017; EPM-S046]

The difference is operational. Suppose a required manual check is not recorded by the system. The observed trace contains payment but no check. That is a model–log discrepancy under the stipulated mapping. It does not establish that the check was omitted in the world. A missing record, an obsolete reference, an execution failure and a legitimate exception remain different hypotheses requiring different evidence and remedies. A richer alignment may sharpen the comparison but cannot generate evidence about an unobserved task. [Recording problems: EPM-S045; comparison semantics: EPM-S010; analytical probe EPM-PROBE02]

Uncertain-event methods can represent admitted alternatives and compute bounds on conformance. A robust violation across every admitted realisation is a different finding from a violation only under one ordering or event-presence interpretation. These are useful distinctions, but the uncertainty set must itself be defensible. Minimum and maximum costs do not supply probabilities, and a set omitting the true history gives misleading reassurance. The appropriate mature form includes abstention when the bounds are too broad to support the intended decision. [EPM-S025]

Model repair is useful when the description is inadequate. It may be less disruptive than rediscovering everything, but small edits are not inherently correct and can preserve a globally flawed model. More importantly, making a descriptive model fit observed work is not the same as deciding that the observed work should become the norm. Descriptive revision, process correction and authorised reference revision remain distinct branches. This separation allows learning without letting a harmful deviation acquire authority merely by becoming frequent. [EPM-S047; EPM-S017; analytical composition EPM-031, EPM-036, EPM-038 and EPM-058]

## 6. What counts as a good model—and a good experiment

Fitness, precision, generalisation and simplicity are valuable questions, not a universally sufficient four-number score. Fitness concerns observed behaviour admitted by a model. Precision attempts to assess additional permitted behaviour under a specified definition. Generalisation concerns valid behaviour beyond the observed sample. Simplicity concerns the burden and intelligibility of the representation, which depends on the consumer and task. Different definitions and formal properties can change rankings, so a number must retain its meaning. [EPM-S001; EPM-S018; EPM-S019; EPM-S020]

The flower-model counterexample is decisive against perfect-fitness sufficiency. A model admitting every finite sequence over the activity alphabet admits every observed trace. Its perfect fit does not establish that it excludes unsupported behaviour, identifies the process or supplies a useful normative reference. This is not an argument against fitness; it is an argument against treating one necessary or useful property as a complete certificate. Similarly, a model can be stable under noise because it says almost nothing. Stability is useful evidence about sensitivity, not truth. [EPM-S056, example and discussion; analytical probe EPM-PROBE03]

Generalisation is particularly dependent on the observation process. A richer estimator may fail to improve on a simpler one when representativeness changes. Synthetic ground truth is useful because the generating model is known; it lets researchers examine the estimator’s behaviour under controlled assumptions. It does not establish that the same assumptions describe a real organisation. The 2025 study strengthens the requirement to describe what generalisation is being estimated and what the sample makes knowable. [EPM-S020]

Empirical denominators also need discipline. Twenty-four tasks from nine logs are not twenty-four independent organisations. Thousands of detector runs are not thousands of independent process changes. Repeated prefixes of one case can cross evaluation boundaries and leak information. A benchmark can become biased by excluding cases whose outcomes were not yet observable, by trimming difficult long cases or by dropping metrics that failed to compute. The packet retains units, exclusions, uncertainty and dependence rather than treating a large execution count as external replication. [EPM-S021; EPM-S022; EPM-S023; EPM-S056]

The resulting experimental principle is claim-matched design, not a universal train/test ritual. A grouped random split can be appropriate for an explicitly exchangeable retrospective target. A future-deployment claim needs a design respecting decision-time availability, temporal changes and the intended population. The mere presence of a checklist, statistical test or reproducibility bundle does not ensure that the experiment measures the advertised thing. This criticism changes the dispositions: aggregate ranking is not a general property, precision remains easily gamed, and executable custody is retained without being equated with correctness. [EPM-S018; EPM-S022; EPM-S056]

## 7. Performance, people and real consequences

A logged duration is first an interval between records. Calling it waiting time, service time or effort requires additional lifecycle and context evidence. Shared resources, batches, overtaking, calendars, unrecorded prerequisites and case mix can all alter interpretation. Fine-grained and object-centric performance methods recover useful distinctions, but they do not make the original timestamps or omitted activities correct. The title of a method using the word “unbiased” must not be expanded into a claim that all source data and causal attributions are unbiased. [EPM-S039; EPM-S045; EPM-S048; EPM-S050]

The same restraint applies to people. An account identifier may denote several workers, a role or an automated service. An event-derived handoff can be meaningful operational evidence without being a social relationship, influence measure or assessment of personal worth. Early organisational mining already encountered shared accounts. Responsible-use work adds fairness, accountability, confidentiality and transparency concerns, but that framework is not a controlled trial showing that a particular institutional safeguard works everywhere. [EPM-S012; EPM-S017]

A concrete field case is valuable precisely when its actual outcome is preserved. The RWS invoice study reports that project leaders were informed and agreed to prioritise invoice handling. That establishes an important communication and organisational-response step. It does not establish a controlled causal reduction in delay, a quantified economic return or a general effect of process mining. Conversely, lack of that stronger evidence does not make the reported interaction worthless. The evolved account separates finding, agreement, implemented action and measured consequence so that each can be credited without being inflated. [EPM-S032, reported response]

This is how the system remains genuinely operative rather than merely internal information processing. Analysts can communicate evidence to people who understand recording practice or own a decision. Those actors can correct a source, change a model, allocate attention, revise a policy or alter real work within their actual mandate. Their actions change the environment and later observations. The analytical system does not acquire those powers simply by representing them. It needs an external interface and evidence of what actually happened after a decision. [Field/practitioner basis: EPM-S016 and EPM-S032; analytical composition EPM-053, EPM-065 and EPM-084]

## 8. Change, prediction and intervention

Drift detection compares event-derived behaviour over time. A change can arise from work, policy, demand, case mix, recording or extraction. The detector generally does not identify which one occurred. The 2023 evaluation shows that detector performance depends on the change characteristics. Streaming methods add explicit trade-offs between latency, memory, forgetting and incomplete-case semantics. Neither a universal detector threshold nor a mandate to stream every process survives the critique. [EPM-S021; EPM-S034; EPM-S037]

The revision problem is therefore not “adapt or remain static”. It is “which object has been shown to need revision, under whose authority, and with what continuity requirement?” An instrumentation change may require a mapping correction. A genuine change may justify a new descriptive model. A violation of a continuing rule may justify process correction. An obsolete rule may require authorised revision. The evolved system preserves all these routes, including no change while the cause remains unresolved. [EPM-S039; EPM-S045; EPM-S047; analytical synthesis EPM-054–EPM-059]

Predictive process monitoring has a further temporal obligation: use only information available at the declared prediction occasion. A final case row can contain attributes updated after the outcome. Truncating the visible event sequence does not automatically remove this leakage. The benchmark-construction critique also shows why completed-case selection and end-of-log censoring matter. A high retrospective score can therefore fail to estimate the task the deployment would actually face. [EPM-S022; EPM-S023]

Uncertainty can support a better decision, but only if its meaning is preserved. Probability calibration, predictive discrimination, conformal set coverage and case-specific uncertainty are distinct targets. The 2025 sepsis-log study provides a bounded retrospective application; it explicitly does not establish deployment readiness. External conformal theory clarifies that basic marginal coverage depends on conditions such as exchangeability and the relevant algorithm construction, not on a perfectly calibrated base classifier. Extensions under distribution shift bound losses under additional assumptions; they do not make arbitrary drift harmless. A prediction set containing both outcomes can correctly express insufficient discrimination, but then a real human-review or abstention path is needed. [EPM-S057, evaluation and limitations; EPM-S058, Theorem 1 and non-exchangeable bounds]

Prediction is still not intervention. The fact that an action occurs with better outcomes does not establish what would happen if the action were recommended more often. Confounding, treatment support, resource competition and sequential decisions can change the answer. Resource-constrained prescription and SCOPE make the causal and decision problem more explicit; their inspected evidence nevertheless remains bounded by retrospective, simulated or semi-synthetic settings and identification assumptions. Broad deployed causal benefit remains unresolved rather than presumed. [EPM-S027; EPM-S030]

Acted-upon advice changes later data. A policy that prioritises predicted delays can alter completion times, workloads and which cases receive attention. The original benchmark then becomes evidence about an earlier regime. Renewed evaluation is required for a current predictive or causal claim; merely observing a better average after adoption can still be confounded. The mature system therefore links recommendations to actual action records, temporal identity and re-evaluation, while permitting a simpler human-supported or no-intervention alternative. [EPM-S022; EPM-S027; EPM-S030; analytical EPM-066]

## 9. Current frontiers without promotion into guarantees

The accessible 2026 object-centric research manifesto is particularly useful because it recognises conceptual differences and integration challenges instead of treating a shared label as a completed unification. Its future nominal issue date is not counted as an already completed publication event or as replication. The 2026 identifier-sound discovery paper contributes a more specific construction. The collaborative-prediction preprint explores object context under stated task interpretations. These works change the frontier but do not eliminate identity, compatibility, interpretation and external-validity questions. [EPM-S026; EPM-S028; EPM-S044]

Privacy-preserving and federated mining similarly require precise boundaries. A protocol may protect raw inputs during computation while still revealing identifiers, trace lengths or information through the output. The 2025 federated directly-follows study compares variants with different disclosure and cost properties. Group-based privacy methods depend on an adversary’s background knowledge and transformations that can remove analytically important detail. “Encrypted” and “anonymised” are therefore not sufficient descriptions of what is protected. [EPM-S033; EPM-S040]

LLM assistance can help with explanation, coding or extracting event candidates from text. The evidence does not justify accepting fluent output as process truth. The task benchmark has evaluation and judge dependencies. The 2026 text-to-OCEL extension uses synthetic text derived from six OCEL datasets and natural-text demonstrations; it explicitly does not report a fully operational business deployment. The extension is not an independent replication of its conference ancestor, and changes in model versions and matching procedures complicate causal attribution of score improvements. The appropriate retained property is checkable, bounded assistance, with text-derived events kept as hypotheses until their meaning is supported. [EPM-S029; EPM-S054, abstract/metadata; EPM-S055, methods, evaluation and limitations]

## 10. Method of this study and the meaning of completeness

The study uses 58 exact source records, distinguishes evidence roles and preserves materially different publication versions. It opened primary papers, official specifications or metadata, author/institutional copies and relevant current manuscripts. Full text at claim-relevant sections was available for 53 records; five records have explicitly narrower access. This is not a claim that every page of every full-text work was read, nor that abstracts reveal omitted methods. Claim locators identify what was actually inspected.

The acquisition account is a reconstructed thematic search log, not an invented verbatim browser transcript or a PRISMA census. It covers the ten mandatory domain families, historical and forward tracing, negative and methodological criticism, field limitations and current work. Follow-up acquisition changed real judgements: the full 2026 text-extraction paper narrowed its transfer claim, the experimentation paper strengthened the anti-ceremony critique, and calibration theory prevented a mistaken reliability inference. Composition then produced EPM-084. The stopping judgement is bounded decision saturation, not attainment of a preset source or property count.

Completeness here means that every mandatory family and registered candidate has an examined disposition; unresolved questions and access limits remain visible. It does not mean every publication was retrieved, every theorem certified, every deployment independently inspected or every transfer claim settled. No live mining algorithm, private event log, organisational intervention or comparative user study was executed in this research run. The analytical probes test logical distinctions in the composed account, not empirical effectiveness. The later JSON and archive checks establish the integrity of this packet, not the truth of every environmental assumption it discusses.


## Corpus navigation

The full records, evidence partitions, exact access levels and machine-resolvable relationships are in [PROPERTY_LEDGER.json](EVOLVED_PROCESS_MINING_PROPERTY_LEDGER.json), [SOURCE_TABLE.json](EVOLVED_PROCESS_MINING_SOURCE_TABLE.json), [COMPOSITION_MODEL.json](EVOLVED_PROCESS_MINING_COMPOSITION_MODEL.json) and [RESEARCH_COVERAGE.json](EVOLVED_PROCESS_MINING_RESEARCH_COVERAGE.json). The three intakes are separate payloads for later audit, public explanation and synthesis. No source PDFs or unrelated repositories are included.

| Primary disposition | Candidates |
| --- | --- |
| ASSUMPTION_SENSITIVE | 14 |
| CEREMONY_NOT_GENERAL_PROPERTY | 1 |
| CONTEXT_DEPENDENT | 15 |
| DOMAIN_SPECIFIC | 1 |
| DUPLICATE_CANDIDATE | 1 |
| NO_GENERAL_PROPERTY | 4 |
| REJECTED_OR_DISFAVOURED | 5 |
| RETAINED_IN_EVOLVED_FORM | 11 |
| STRONGLY_RETAINED | 28 |
| SUPERSEDED_BY_STRONGER_FORM | 1 |
| UNRESOLVED | 2 |
| USEFUL_BUT_EASILY_GAMED | 1 |

Examination: **74 EXAMINED**, **10 EXAMINED_WITH_EVIDENCE_LIMIT**. Every candidate and all ten mandatory families have an examined disposition. “With evidence limit” is not a claim that the question was settled or the missing evidence was inspected.

## EVOLVED_PROCESS_MINING_TIMELINE

### EPM-G001 — Before and during the 1990s: Imported formal and learning foundations

How can event sequences constrain an explicit behavioural model? Automata/grammar inference, Markov models, Petri-net semantics and later region-based synthesis provide different representational starting points. The field is not ancestry-free; process-specific mining imports established modelling and inference devices.

**Limit and continuation.** This packet inspects those foundations through their use and explanation in primary mining papers; it does not claim to have inspected the original Petri thesis or to adjudicate every precursor. Different foundations remain visible in later competing schools rather than collapsing into a single linear lineage. [EPM-S002; EPM-S005; EPM-S008]

### EPM-G002 — 1998: Software-process inference

Observed software work often diverges from assumed process descriptions. Cook and Wolf compare RNet, Ktail and Markov approaches to recovering software-process models from event data. A primary early formulation centred on process evidence rather than only business transaction metrics.

**Limit and continuation.** The paper’s setting and model assumptions do not establish a universal reconstruction method. Its problem orientation belongs in the plural genealogy; no documentary claim that it caused every later business-process branch is made. [EPM-S002]

### EPM-G003 — 1998: Workflow-log and probabilistic business-process discovery

Recover process structure from execution records rather than modelling exclusively by interview. Agrawal, Gunopulos and Leymann formulate workflow-log mining; Datta studies probabilistic and algorithmic AS-IS discovery. Distinct contemporaneous founding contributions prevent attributing the whole field to one author.

**Limit and continuation.** Only abstracts and metadata were available for these exact works; detailed theorem or experiment claims are not made. They establish early problem formulations. Specific influence edges beyond documented later citations are not invented. [EPM-S003; EPM-S004]

### EPM-G004 — 2004: Alpha workflow mining

Infer a Petri-net workflow structure from event-order relations. Relations over activities identify candidate causal, parallel and choice structure under explicit net/log assumptions. A clear formal link between event logs and process models, with scoped rediscovery reasoning.

**Limit and continuation.** The theorem is not unrestricted process recovery; noise, loops, non-free-choice constructs and sampling conditions matter. Later extensions and alternative miners respond to specific limitations. [EPM-S005]

### EPM-G005 — 2005: Organisational mining and research infrastructure

Study recorded resource interaction and make multiple mining algorithms accessible. Event-derived social relations and ProM’s plug-in framework. Expands beyond control flow and supports a plural research-tool ecosystem.

**Limit and continuation.** Account semantics and informal work limit social interpretation; a tool framework does not establish effectiveness. Organisational and multi-perspective branches persist, alongside responsibility critiques. [EPM-S012; EPM-S036]

### EPM-G006 — 2006–2007: Heuristic, evolutionary and abstraction-oriented discovery

Real logs are noisy and complex; local exact reconstruction or unreadable maps can be inadequate. Frequency/dependency heuristics, population-based global search, and significance/correlation-based visual abstraction. Several non-equivalent responses to noise, search complexity and human comprehension.

**Limit and continuation.** Threshold bias, stochastic cost, fitness-objective limitations and suppressed exceptions remain. These are alternatives, not simply superseded stages on the way to one best miner. [EPM-S006; EPM-S013; EPM-S038]

### EPM-G007 — 2007: Alpha extensions and industrial application

Address non-free-choice structure and test mining in an actual organisational process. Alpha++-lineage mechanisms address implicit dependencies; RWS invoice analysis connects models and findings to staff. Formal refinement and field inquiry are distinct kinds of contribution.

**Limit and continuation.** One industrial response does not establish causal improvement or universal adoption value. The industrial study provides concrete communication/action ancestry without erasing its limited outcome evidence. [EPM-S031; EPM-S032]

### EPM-G008 — 2008: Region/ILP discovery and token-based conformance

Obtain suitable net places and quantify mismatch between a model and observed behaviour. Region constraints formulated as ILP; token replay and appropriateness measures. Strengthens explicit construction and model–log comparison.

**Limit and continuation.** Objectives, model classes and replay choices bound interpretations. Alignment-based and multi-perspective methods later refine some diagnostic limitations; replay remains a usable cheaper branch. [EPM-S008; EPM-S009]

### EPM-G009 — 2011–2012: Cost-based alignments and Manifesto consolidation

Need principled mismatch explanations and a public account of the field’s scope and challenges. Costed log/model moves; community articulation of discovery, conformance, enhancement and event-data principles. Consolidates a field already containing multiple contributors and methods.

**Limit and continuation.** A manifesto is guidance and agenda, not empirical evidence of universal benefit; optimum alignment is cost-relative. The document’s loops and operational-support aspirations inform synthesis but do not mandate a serial lifecycle. [EPM-S001; EPM-S010]

### EPM-G010 — 2012–2015: Declarative mining, model repair and MINERful

Flexible work may be more intelligible through restrictions than a complete prescribed path; models also need targeted revision. Template-based constraint discovery, efficient rule extraction and alignment-guided local repair. Adds alternatives for flexible behaviour and preservation of unaffected model intent.

**Limit and continuation.** Vacuity, redundancy and descriptive-versus-normative repair need further treatment. Semantic criticism refines rule interpretation; repair remains separate from authority to amend obligations. [EPM-S011; EPM-S041; EPM-S047]

### EPM-G011 — 2013: Inductive discovery

Guarantee structurally meaningful executable models by construction. Recursive decomposition into block-structured models with scoped formal properties. A robust route to sound models within a chosen representation.

**Limit and continuation.** Soundness is not unrestricted identifiability, precision or truth about actual work. Later variants extend practical handling; this study does not transfer all variant claims to the original theorem. [EPM-S007]

### EPM-G012 — 2013–2014: Process concept drift

A single static model hides changing behaviour. Features, windows and statistical comparisons detect changes in event-derived behaviour. Makes temporal validity an explicit process-mining object.

**Limit and continuation.** Detection does not identify whether work, instrumentation or population changed. Streaming and later benchmarking refine the performance/response trade-offs. [EPM-S037]

### EPM-G013 — 2015–2016: Relational extraction, multi-perspective checking and semantic vacuity

Case flattening distorts relations; control-only diagnosis misses guards; unactivated rules appear satisfied. Explicit extraction analysis, joint perspective alignments and activation-aware declarative semantics. Different critiques expose hidden assumptions at interfaces between data, representation and interpretation.

**Limit and continuation.** Richer methods create new data and computation requirements. These are central ancestors for EPM-084’s analytical handoff invariant, not proof that this new synthesis already existed. [EPM-S014; EPM-S042; EPM-S046]

### EPM-G014 — 2016–2018: Local models, fine-grained performance and streaming

Whole-process views, case averages and batch-only methods miss useful local or timely distinctions. Local behavioural fragments, context-aware timing and bounded streaming state. Adds economical or specialised configurations instead of one mandatory full model.

**Limit and continuation.** Local/global compatibility, missing intervals, forgetting and incomplete-case semantics remain. Later object-centric and drift methods extend these concerns without eliminating them. [EPM-S048; EPM-S049; EPM-S052]

### EPM-G015 — 2017–2019: Evaluation criticism and predictive benchmarks

How should model quality and running-case prediction be compared? Precision counterexamples; broad discovery and outcome-prediction comparisons. Shows that operationalisation, model class, log reuse and task definition matter.

**Limit and continuation.** Benchmarks are not field effectiveness trials; repeated tasks and logs are not independent deployments. Later leakage, data-quality and methodology work challenge simplistic rankings. [EPM-S018; EPM-S019; EPM-S023]

### EPM-G016 — 2019–2021: Uncertain events, object-centric nets and privacy

Single definite traces and case identifiers cannot express all relevant uncertainty, interactions or privacy risks. Possible realisations, object-centric nets and background-knowledge-aware privacy transformations. Broadens represented evidence and scoped guarantees.

**Limit and continuation.** Uncertainty sets need justification; soundness notions differ; privacy trades off utility. Modern identity-aware, federated and responsible-use work continues these tensions. [EPM-S025; EPM-S035; EPM-S040; EPM-S043]

### EPM-G017 — 2021–2022: Prediction leakage, resource-constrained prescription and responsibility

Prospective scores can leak future information; advice competes for resources; organisational use can harm people. Temporal data construction, causal/decision formulations, explicit responsibility concerns and object-aware performance. Separates methodological promise from justified use and deployable benefit.

**Limit and continuation.** Offline estimates and conceptual frameworks do not establish broad realised effects. Sequential causal work and current calibration studies retain substantial transfer obligations. [EPM-S017; EPM-S022; EPM-S030; EPM-S034; EPM-S050]

### EPM-G018 — 2023–2024: Drift benchmarking, practitioner evidence and revised event interchange

Need empirical knowledge of analyst work, detector limits and richer event relationships. Drift comparison; interviews/survey; hospital data study; XES 2023 and OCEL 2.0 specification. Deepens the evidence about assumptions, human work and representational boundaries.

**Limit and continuation.** The full normative XES text was not inspected; qualitative findings do not estimate universal frequencies. Supports a question-relative, versioned and participant-aware synthesis rather than a frictionless automation story. [EPM-S015; EPM-S016; EPM-S021; EPM-S024; EPM-S045]

### EPM-G019 — 2024–2025: Experimentation methodology, generalisation, LLM benchmarks and federation

Need valid comparisons, shared-data analysis and bounded language assistance. Claim-oriented experimentation; data-quality-aware estimation; judge-mediated LLM tasks; cryptographic joint discovery; text extraction and uncertainty calibration. Expands capability and strengthens criticism of benchmark-to-world transfer.

**Limit and continuation.** Checklist completion, secure computation and benchmark scores can each be overinterpreted. Richer forms remain selected mechanisms with explicit costs and evidence limits. [EPM-S020; EPM-S029; EPM-S033; EPM-S054; EPM-S056; EPM-S057]

### EPM-G020 — 2026, accessible by 6 September: Dynamic object identity, text-to-event models and causal/collaborative frontiers

Represent richer interactions, extract evidence from text and improve sequential decisions. Identifier-sound discovery; heuristic/generative text extraction; sequential causal optimisation and collaborative object-centric prediction. Current work changes concrete mechanisms and exposes additional compatibility and evaluation obligations.

**Limit and continuation.** S026 has a future October issue date but an accessible manuscript; S027/S028 are preprints and S028 is under review. None is counted as completed independent deployment replication. Useful frontier directions, not evidence that all object, uncertainty, causal and language components already form a unified mature method. [EPM-S026; EPM-S027; EPM-S028; EPM-S044; EPM-S055]


## EVOLVED_PROCESS_MINING_GENEALOGY

The dated nodes above are plural branches, not a progress ladder. Edges below distinguish explicit extension, documented import, criticism/response, hybridisation and convergence. A similar vocabulary or a shared author is not by itself evidence of derivation. The early abstract-only and original-foundation access limits remain part of the genealogy.

| Edge | From → to | Class | Documentary basis and limit |
| --- | --- | --- | --- |
| EPM-GE001 | EPM-G001 → EPM-G002 | DOCUMENTED_IMPORT | Cook/Wolf explicitly formulate and compare learning/automata/Markov approaches. This establishes use of foundations, not exclusive origin of process mining. [EPM-S002] |
| EPM-GE002 | EPM-G001 → EPM-G004 | DOCUMENTED_IMPORT | Alpha is defined in workflow/Petri-net terms. The original Petri-net historical documents were not independently reconstructed here. [EPM-S005] |
| EPM-GE003 | EPM-G002 → EPM-G003 | CONVERGENT_DEVELOPMENT | Primary works address event-based process inference in distinct 1998 settings. No direct transmission among all three is asserted from contemporaneity alone. [EPM-S002; EPM-S003; EPM-S004] |
| EPM-GE004 | EPM-G004 → EPM-G007 | EXPLICIT_EXTENSION | The non-free-choice paper explicitly extends the alpha-lineage problem. Improved coverage is scoped; it is not universal replacement. [EPM-S005; EPM-S031] |
| EPM-GE005 | EPM-G004 → EPM-G006 | CRITICISM_AND_RESPONSE | Later methods identify practical noise/complexity/search issues and propose distinct responses. This classifies stated problem responses, not exclusive causal derivation from alpha. [EPM-S006; EPM-S013; EPM-S038] |
| EPM-GE006 | EPM-G001 → EPM-G008 | DOCUMENTED_IMPORT | ILP discovery explicitly uses region-based synthesis ideas. Solver use does not establish empirical superiority. [EPM-S008] |
| EPM-GE007 | EPM-G008 → EPM-G009 | CRITICISM_AND_RESPONSE | Cost-based alignment changes how best-fitting model behaviour is sought relative to replay diagnostics. Token replay is not universally obsolete. [EPM-S009; EPM-S010] |
| EPM-GE008 | EPM-G008 → EPM-G013 | EXPLICIT_EXTENSION | Balanced multi-perspective checking addresses limitations of control-flow-first comparison. Requires meaningful extra attributes and compatible formal semantics. [EPM-S046] |
| EPM-GE009 | EPM-G009 → EPM-G010 | EXPLICIT_EXTENSION | Model repair uses conformance/alignment evidence to modify affected behaviour. Repair is descriptive unless separate authority changes the reference. [EPM-S047] |
| EPM-GE010 | EPM-G010 → EPM-G013 | CRITICISM_AND_RESPONSE | Semantic vacuity work refines interpretation of discovered declarative constraints. Does not imply every earlier constraint was meaningless. [EPM-S041; EPM-S042] |
| EPM-GE011 | EPM-G006 → EPM-G011 | CONVERGENT_DEVELOPMENT | Inductive construction offers a distinct guarantee-oriented response within the discovery field. No simple successor relation to all heuristic/evolutionary mechanisms is asserted. [EPM-S006; EPM-S007; EPM-S038] |
| EPM-GE012 | EPM-G012 → EPM-G014 | EXPLICIT_EXTENSION | Streaming methods address changing and continuously arriving event data under bounded state. Streaming and drift detection are related but not identical tasks. [EPM-S034; EPM-S052] |
| EPM-GE013 | EPM-G013 → EPM-G016 | EXPLICIT_EXTENSION | Object-centric discovery explicitly addresses relational/convergence-divergence limitations of flattening. Does not remove identity and extraction judgement. [EPM-S014; EPM-S035] |
| EPM-GE014 | EPM-G014 → EPM-G017 | EXPLICIT_EXTENSION | Object-centric performance revisits timing when events affect multiple objects. Scoped examples do not establish universal unbiased performance inference. [EPM-S048; EPM-S050] |
| EPM-GE015 | EPM-G015 → EPM-G017 | CRITICISM_AND_RESPONSE | Predictive benchmark construction critique identifies leakage and complete-case selection problems. Not a retrospective invalidation of every prior benchmark. [EPM-S022; EPM-S023] |
| EPM-GE016 | EPM-G015 → EPM-G019 | CRITICISM_AND_RESPONSE | Later generalisation and methodology work refines evaluation under data-quality and operationalisation concerns. Methodological guidance is not independently validated organisational benefit. [EPM-S018; EPM-S020; EPM-S053; EPM-S056] |
| EPM-GE017 | EPM-G016 → EPM-G018 | EXPLICIT_EXTENSION | OCEL 2.0 adds explicit relation qualifiers and object attribute dynamics to the object-centric data interface. Specification is not adoption or proof that all tools preserve semantics. [EPM-S024; EPM-S035] |
| EPM-GE018 | EPM-G016 → EPM-G020 | EXPLICIT_EXTENSION | Identifier-aware 2026 discovery develops guarantees for a richer dynamic relation setting. Different exact soundness definitions are not silently equated. [EPM-S043; EPM-S044] |
| EPM-GE019 | EPM-G016 → EPM-G019 | HYBRIDISATION | Federated mining combines process relations with cryptographic privacy mechanisms. Group-based anonymisation and federated encryption are alternatives at different boundaries, not one universal mechanism. [EPM-S033; EPM-S040] |
| EPM-GE020 | EPM-G017 → EPM-G020 | EXPLICIT_EXTENSION | Sequential causal optimisation develops intervention policies beyond static per-case predictive scoring. Simulation/retrospective progress does not establish general realised benefit. [EPM-S027; EPM-S030] |
| EPM-GE021 | EPM-G019 → EPM-G020 | EXPLICIT_EXTENSION | The 2026 text-extraction article explicitly extends the conference programme. Model-version and matching changes mean differences cannot be attributed to one isolated new mechanism. [EPM-S054; EPM-S055] |
| EPM-GE022 | EPM-G019 → EPM-G020 | HYBRIDISATION | Object-centric predictive and language-assisted methods combine process representations with learned models. No evidence that all these components share one compatible semantics or can be safely unified by concatenation. [EPM-S028; EPM-S029; EPM-S055] |


## EVOLVED_PROCESS_MINING_SCOPE_AND_CARICATURES

The scope includes event-data validity, case/object semantics, procedural and declarative discovery, conformance, quality evaluation, performance and organisational interpretation, drift/streams, prediction/prescription, reproducibility and responsible frontier use. It does not treat every data dashboard as process mining, every process model as executable, or every recorded regularity as a legitimate rule. Formal results retain their model assumptions; empirical results retain their unit and setting.

| Caricature | Correction and candidate consequences |
| --- | --- |
| The log shows the whole process. | Recording, extraction and selection are investigated; EPM-001–EPM-008. A bounded evidence gap is legitimate. |
| Process mining means drawing a directly-follows graph. | A graph is one view. Discovery, conformance, enhancement, organisational and operational methods remain distinct branches. |
| There is one best miner. | EPM-019 retains explicit bias and guarded alternatives; EPM-020 replaces only the unrestricted alpha default. |
| Object-centric methods remove modelling judgement. | EPM-012–EPM-016 preserve identity and representation assumptions; EPM-018 has no general property. |
| A perfect fit is a valid model. | EPM-045 rejected; precision, generalisation, simplicity and source validity remain separate. |
| A deviation proves wrongdoing. | EPM-031 and EPM-036 require reference interpretation and rival causes; EPM-037 rejected. |
| A delay or handoff identifies effort or social merit. | EPM-046–EPM-051 constrain timing and people-related interpretation. |
| Adaptation should update the compliance standard automatically. | EPM-058 retains separate descriptive/reference continuity; EPM-059 rejected. |
| Prediction supplies a causal redesign strategy. | EPM-064 requires interventional evidence; EPM-068 remains unresolved at broad deployment scale. |
| Tool possession, cryptography or fluent language guarantees quality. | EPM-073 is ceremony; EPM-076/EPM-078 specify privacy boundaries; EPM-079/EPM-081 require checked assistance. |
| More complete documentation proves the conclusion. | EPM-074 separates auditability and correctness; EPM-084 protects consequential handoffs. |


## EVOLVED_PROCESS_MINING_PROPERTY_LEDGER

**The complete denominator follows: 84 stable IDs.** Full records contain all common fields, all ten domain-profile dimensions, criticism, evidence partitions, authority boundaries, cheap/non-trigger paths, relationship links and open questions in [PROPERTY_LEDGER.json](EVOLVED_PROCESS_MINING_PROPERTY_LEDGER.json). The JSON `properties` array is ordered by ID. EPM-017 remains a duplicate record; EPM-084 was added during composition. Neither rejection nor uncertainty removes a row.

| ID | Candidate | Primary disposition | Examination |
| --- | --- | --- | --- |
| EPM-001 | Meaningful event identity | STRONGLY_RETAINED | EXAMINED |
| EPM-002 | Source provenance and trace-back | STRONGLY_RETAINED | EXAMINED |
| EPM-003 | Semantically justified extraction | STRONGLY_RETAINED | EXAMINED |
| EPM-004 | Activity abstraction with retained mappings | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-005 | Lifecycle-aware event interpretation | STRONGLY_RETAINED | EXAMINED |
| EPM-006 | Ordering proportional to temporal evidence | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-007 | Quality repair without erasing uncertainty | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-008 | Question-relative population adequacy | STRONGLY_RETAINED | EXAMINED |
| EPM-009 | Proportionate logging and collection | CONTEXT_DEPENDENT | EXAMINED |
| EPM-010 | Syntactic validity as sufficient process truth | REJECTED_OR_DISFAVOURED | EXAMINED |
| EPM-011 | Versioned event-data interoperability | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-012 | Question-dependent case notion | STRONGLY_RETAINED | EXAMINED |
| EPM-013 | Explicit typed object interactions | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-014 | Flattening distortion checks | STRONGLY_RETAINED | EXAMINED |
| EPM-015 | Object-centric discovery with model obligations | ASSUMPTION_SENSITIVE | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-016 | Representation complexity as a selection cost | CONTEXT_DEPENDENT | EXAMINED |
| EPM-017 | Activity-level refinement as a separate obligation | DUPLICATE_CANDIDATE | EXAMINED |
| EPM-018 | Universal superiority of object-centricity | NO_GENERAL_PROPERTY | EXAMINED |
| EPM-019 | Explicit discovery and representation bias | STRONGLY_RETAINED | EXAMINED |
| EPM-020 | Alpha as the default general-purpose miner | SUPERSEDED_BY_STRONGER_FORM | EXAMINED |
| EPM-021 | Heuristic discovery with threshold sensitivity | CONTEXT_DEPENDENT | EXAMINED |
| EPM-022 | Sound-by-construction inductive discovery | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-023 | Region and ILP discovery | DOMAIN_SPECIFIC | EXAMINED |
| EPM-024 | Declarative discovery with activation and consistency checks | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-025 | Global evolutionary discovery | CONTEXT_DEPENDENT | EXAMINED |
| EPM-026 | Purposeful process-map simplification | CONTEXT_DEPENDENT | EXAMINED |
| EPM-027 | Protection of material infrequent behaviour | STRONGLY_RETAINED | EXAMINED |
| EPM-028 | Non-identifiability-aware inference | STRONGLY_RETAINED | EXAMINED |
| EPM-029 | Domain-guided discovery with explicit input authority | CONTEXT_DEPENDENT | EXAMINED |
| EPM-030 | Local or decomposed discovery with boundary obligations | CONTEXT_DEPENDENT | EXAMINED |
| EPM-031 | Defensible reference origin and authority | STRONGLY_RETAINED | EXAMINED |
| EPM-032 | Token replay as bounded diagnosis | CONTEXT_DEPENDENT | EXAMINED |
| EPM-033 | Alignment cost and approximation transparency | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-034 | Multi-perspective conformance | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-035 | Uncertain-event conformance bounds | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-036 | Plural explanations of deviation | STRONGLY_RETAINED | EXAMINED |
| EPM-037 | Conformance as sufficient legality or fairness | REJECTED_OR_DISFAVOURED | EXAMINED |
| EPM-038 | Authorised model repair versus process correction | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-039 | Separate model-quality dimensions | STRONGLY_RETAINED | EXAMINED |
| EPM-040 | Measure-specific precision interpretation | USEFUL_BUT_EASILY_GAMED | EXAMINED |
| EPM-041 | Representativeness-aware generalisation | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-042 | Consumer-relative simplicity | CONTEXT_DEPENDENT | EXAMINED |
| EPM-043 | Evaluation units and splits matched to the claim | STRONGLY_RETAINED | EXAMINED |
| EPM-044 | Universal aggregate model-quality ranking | NO_GENERAL_PROPERTY | EXAMINED |
| EPM-045 | Perfect fitness as sufficient validity | REJECTED_OR_DISFAVOURED | EXAMINED |
| EPM-046 | Elapsed time distinguished from effort | STRONGLY_RETAINED | EXAMINED |
| EPM-047 | Bottleneck explanations checked against omitted prerequisites | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-048 | Inter-case resource and queueing context | CONTEXT_DEPENDENT | EXAMINED |
| EPM-049 | Verified resource identity semantics | STRONGLY_RETAINED | EXAMINED |
| EPM-050 | Social-network interpretation restraint | CONTEXT_DEPENDENT | EXAMINED |
| EPM-051 | Case-mix and subgroup comparability | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-052 | Simulation as conditional scenario analysis | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-053 | Consequential consumer and measured outcome | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-054 | Temporal identity of logs models and expectations | STRONGLY_RETAINED | EXAMINED |
| EPM-055 | Drift detection with latency and false-alarm costs | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-056 | Instrumentation change distinguished from process change | STRONGLY_RETAINED | EXAMINED |
| EPM-057 | Streaming with explicit forgetting and incomplete-case semantics | CONTEXT_DEPENDENT | EXAMINED |
| EPM-058 | Adaptive description separated from stable obligations | STRONGLY_RETAINED | EXAMINED |
| EPM-059 | Automatic normative normalisation of detected drift | REJECTED_OR_DISFAVOURED | EXAMINED |
| EPM-060 | Prediction-time information availability | STRONGLY_RETAINED | EXAMINED |
| EPM-061 | Leakage- and censoring-aware predictive evaluation | STRONGLY_RETAINED | EXAMINED |
| EPM-062 | Calibrated uncertainty and abstention | ASSUMPTION_SENSITIVE | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-063 | Timely resource-aware decision utility | CONTEXT_DEPENDENT | EXAMINED |
| EPM-064 | Causal identification before interventional claims | STRONGLY_RETAINED | EXAMINED |
| EPM-065 | Feasible and authorised recommendations | CONTEXT_DEPENDENT | EXAMINED |
| EPM-066 | Evaluation renewal after intervention feedback | STRONGLY_RETAINED | EXAMINED |
| EPM-067 | Universal superiority of deep predictive models | NO_GENERAL_PROPERTY | EXAMINED |
| EPM-068 | General deployed causal benefit of prescription | UNRESOLVED | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-069 | Reproducible executable analysis | STRONGLY_RETAINED | EXAMINED |
| EPM-070 | Robustness to plausible analytical alternatives | STRONGLY_RETAINED | EXAMINED |
| EPM-071 | Domain challenge and participant validation | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-072 | Dependence-aware evidence accounting | STRONGLY_RETAINED | EXAMINED |
| EPM-073 | Dashboard possession as evidence of analytical quality | CEREMONY_NOT_GENERAL_PROPERTY | EXAMINED |
| EPM-074 | Auditability distinguished from correctness | STRONGLY_RETAINED | EXAMINED |
| EPM-075 | Non-use and retirement when mining has no adequate purpose | STRONGLY_RETAINED | EXAMINED |
| EPM-076 | Privacy protection matched to an explicit attacker | ASSUMPTION_SENSITIVE | EXAMINED |
| EPM-077 | Fairness and contestable people-related inference | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| EPM-078 | Federated mining within security and output boundaries | ASSUMPTION_SENSITIVE | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-079 | Checked LLM assistance rather than asserted competence | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-080 | Autonomous operative authority inferred from event logs | REJECTED_OR_DISFAVOURED | EXAMINED |
| EPM-081 | Text-derived event semantics retained as hypotheses | ASSUMPTION_SENSITIVE | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-082 | Broad external validity of uncertain object-centric analysis | UNRESOLVED | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-083 | Universal positive economic return on mining | NO_GENERAL_PROPERTY | EXAMINED_WITH_EVIDENCE_LIMIT |
| EPM-084 | Validity-preserving analytical handoffs | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |

### What the dispositions mean operationally

Strong retention refers to the importance of a distinction or mechanism under its trigger, not to a claimed universally measured benefit. Context-dependent and assumption-sensitive records require their local conditions. EPM-023 is a specialised alternative; EPM-040 is useful but vulnerable to metric gaming. Non-retained candidates are not unconditional audit obligations. EPM-068 and EPM-082 export questions and limits, not presumed capabilities.


## EVOLVED_PROCESS_MINING_DOMAIN_MODELS

### EPM-DM01 — Event-data validity (PM1)

**Objects/state.** Let W denote in-scope work occurrences, R recorded observations, X an extraction transformation, and L the resulting event representation. Recording is a potentially incomplete, many-to-many correspondence ρ⊆W×R: an occurrence may have no matched record, and an administrative record may have no matched in-scope occurrence. X acts on the record collection to produce L and may select, join, correlate and abstract. Neither correspondence nor transformation is assumed invertible; recorded timestamps may differ from occurrence times.

**Argument and limit.** A result computed on L is a claim about W only through justified recording and extraction assumptions. Exact identity of L and reproducibility of X do not validate the correspondence ρ. Adequacy is relative to a declared question Q, target unit U and window T; a defect matters when it changes the claim required by Q.

**Operation.** Investigate event classes and source examples, reconcile material transformations and population boundaries, then preserve the remaining uncertainty in the chosen analysis. A surprising result can return directly to source interpretation. Correction, narrowing and non-use are legitimate branches, not failed completion of a pipeline.

**Discriminating failure.** A status transition is logged on form submission at the end of a shift: a sequence miner faithfully orders records but the interpreted work chronology is false. Correct schema and checksums do not cure this.

**Smallest adequate form.** One bounded question, a tested event dictionary or small semantic sample, a reproducible query and explicit exclusions. Rich quality metrics are triggered by heterogeneity or consequential defects. [EPM-S001; EPM-S014; EPM-S024; EPM-S039; EPM-S045]

### EPM-DM02 — Case/object semantics (PM2)

**Objects/state.** Represent events E, objects O, object types τ and participation R⊆E×O. A case-centric projection πc maps events to traces under case notion c; one event may participate in several objects. Attributes and object relationships can change over time, which must be represented when consequential.

**Argument and limit.** Projection changes the represented relation. Two case notions may yield different frequencies and directly-follows edges without any change in E or W. Object-centric representations preserve selected relations but do not remove identity or abstraction assumptions. Type-level and identifier-aware nets have different guarantee domains.

**Operation.** Select the relation needed by the question; test convergence/divergence and shared-event duplication; use an object-aware representation only when it retains a consequential relation. For executable models, name the exact formalism and establish its supported soundness properties. Revisit the representation when interpretation cost or uncertainty dominates its gain.

**Discriminating failure.** An invoice shared by two orders becomes two copied events in a flattened order log. Counting those copies as two invoice executions is a representational error, not discovered rework.

**Smallest adequate form.** A case log with an explicit chosen identifier and a small cardinality check. A typed event–object table is the next step when interactions matter; an executable object-centric net is a further, separately justified choice. [EPM-S014; EPM-S024; EPM-S026; EPM-S035; EPM-S043; EPM-S044; EPM-S050]

### EPM-DM03 — Discovery and identifiability (PM3)

**Objects/state.** A discovery procedure Dθ maps an event representation L to a model M in a chosen class C. θ includes thresholds, objective, noise handling and implementation settings. The observed log is a finite sample; the model language ℒ(M) can contain unobserved behaviours.

**Argument and limit.** A construction guarantee such as soundness is a property of M under its formal semantics. Rediscovery additionally assumes a compatible generating class and adequate observations. Neither entails unique reconstruction of the organisational mechanism. Different algorithms expose different structures and biases: procedural, declarative, region-based, evolutionary, abstract or local.

**Operation.** Choose representation and purpose, disclose bias, compare adequate alternatives and investigate material exceptions. Domain knowledge can guide the search if its provenance is visible. Use local views without global claims where sufficient. Revise or withhold a structural inference when alternate models cannot be discriminated.

**Discriminating failure.** The finite traces ab and ba support both a concurrent two-task mechanism and an exclusive choice between two sequential branches. Log agreement alone cannot identify which internal mechanism produced them.

**Smallest adequate form.** A labelled directly-follows relation or one explicit constraint can answer a narrow question. Executable discovery is triggered by a need to reason about allowed behaviour, execution or richer conformance. [EPM-S002; EPM-S003; EPM-S004; EPM-S005; EPM-S006; EPM-S007; EPM-S008; EPM-S011; EPM-S013; EPM-S019; EPM-S031; EPM-S038; EPM-S041; EPM-S042; EPM-S049; EPM-S053; EPM-S056]

### EPM-DM04 — Conformance and authority (PM4)

**Objects/state.** Conformance relates a log L, reference M, mapping a, semantics s and, where used, costs c. Alignments minimise a defined cost over allowed model/log moves; token replay counts token discrepancies under its own replay semantics. An uncertain log U may denote a set of admitted realisations.

**Argument and limit.** The result establishes a relation under (M,a,s,c), not an all-purpose verdict. Minimum cost is not the true causal history. For uncertain data, a minimum and maximum over U bound only the declared set of possibilities, not a probability. Normative force depends on the origin and authority of M, not on the optimiser.

**Operation.** Establish reference provenance, choose the least costly adequate comparison, expose approximation and interpret mismatch through rival data/model/execution/exception causes. A confirmed problem branches to data correction, model repair, process change or authorised rule revision. Preserve unresolved explanations when evidence cannot discriminate.

**Discriminating failure.** A mandatory manual check occurs but is never logged. The observed trace deviates from the reference, yet the alignment alone cannot distinguish omitted recording from omitted work.

**Smallest adequate form.** One explicitly interpreted rule and a traceable event check. Token replay, exact alignments, multi-perspective constraints and uncertainty bounds are richer alternatives selected by diagnostic need. [EPM-S009; EPM-S010; EPM-S017; EPM-S025; EPM-S046; EPM-S047]

### EPM-DM05 — Model evaluation (PM5)

**Objects/state.** Let Q(M,L,P,T,u) denote a vector of claim-specific evaluations under population P, time T and consumer task u, not a universal scalar. Fitness concerns observed behaviour admitted; precision concerns excess permitted behaviour under a definition; generalisation concerns unseen valid behaviour; simplicity concerns usable representation/cost.

**Argument and limit.** No component logically entails all others. A model with ℒ(M)=Σ* has perfect language-inclusion fitness for every L while admitting arbitrary sequences. Measure definitions and representation choices affect comparisons. Train/test design identifies a target performance only under its sampling and dependence assumptions.

**Operation.** State the evaluation question and units, select applicable measures and baselines, isolate test information and disclose unavailable measures. Inspect sensitivity to data quality, representation and parameter choices. A decision-specific trade-off can select a model, but it must not masquerade as a context-free ranking.

**Discriminating failure.** A benchmark reports only successful metric computations, thereby dropping the large or difficult logs on which a method fails. The resulting average answers a selected problem, not the advertised common comparison.

**Smallest adequate form.** A few explicit behavioural tests plus a relevant complexity/usefulness check may suffice for a local question. Broad empirical comparisons require a fuller experimental design. [EPM-S001; EPM-S018; EPM-S019; EPM-S020; EPM-S022; EPM-S053; EPM-S056]

### EPM-DM06 — Performance and organisational inference (PM6)

**Objects/state.** Observed times define intervals between recorded lifecycle events. Resource attributes denote accounts, roles, people or systems according to source semantics. Context includes case mix, load, queues, object relations, batching, calendars and unobserved prerequisites.

**Argument and limit.** Δt between two records is an elapsed interval; active effort or waiting attribution requires additional phase and context evidence. A handoff relation constructed from a trace is an operational relation, not necessarily collaboration or influence. A diagnosed bottleneck is a hypothesis about a mechanism, not an automatically identified cause.

**Operation.** Use timing and interaction patterns to focus inquiry, validate resource and lifecycle meanings, compare relevant contexts and consult participants. Distinguish communicated findings, agreed action, implemented action and measured outcome. Scenario analysis is conditional on a model and does not establish achieved benefit.

**Discriminating failure.** A long interval before approval is attributed to the approver, while an unlogged prerequisite or batch-recording policy explains it. A shared account then wrongly concentrates the apparent delay on one person.

**Smallest adequate form.** A traceable elapsed-time comparison and a focused operational conversation can be enough. Queueing, object-centric timing and simulation are triggered by a consequential contextual dependency. [EPM-S012; EPM-S016; EPM-S017; EPM-S032; EPM-S039; EPM-S045; EPM-S048; EPM-S050]

### EPM-DM07 — Drift and temporal revision (PM7)

**Objects/state.** A monitored feature distribution Pt is affected by work, population, instrumentation and extraction. A detector compares windows or maintains adaptive state; it has finite memory, delay and false-alarm behaviour. A descriptive model Mt and authorised reference Rt need not change together.

**Argument and limit.** A detected distributional change does not identify which underlying component changed. A forgotten event is not disproved behaviour. Updating Mt to describe new observations does not authorise changing Rt. A stable reference can still require an explicit, legitimate revision when circumstances change.

**Operation.** Monitor only when timely response matters; investigate alarms through rival observation/process explanations; version the data and models; choose batch or streaming according to latency and cost. Branch to model revision, instrumentation correction, process action or no change. Preserve prior reference meaning where continuity matters.

**Discriminating failure.** A software release splits one activity label into two, causing a drift alarm. Automatically retraining the compliance standard would normalise a logging change rather than evaluate the work.

**Smallest adequate form.** A dated snapshot and periodic comparison with a known source-change log. Streaming is triggered by meaningful latency or resource constraints, not by novelty. [EPM-S021; EPM-S034; EPM-S037; EPM-S039; EPM-S045; EPM-S047]

### EPM-DM08 — Prediction and intervention (PM8)

**Objects/state.** At decision time t, It denotes available information and At feasible actions. Prediction estimates an outcome conditional on It; an intervention claim concerns outcomes under a specified action or policy. Prefixes of one case and cases sharing resources may be dependent. Calibration data and policy versions are part of the state.

**Argument and limit.** P(Y|A=a,It) need not equal an interventional outcome distribution because action selection can be confounded. Prediction-time availability is a precondition for prospective evaluation. Conformal coverage is marginal under its conditions, not individual certainty, and policy feedback can alter the distribution on which earlier evidence depended.

**Operation.** Define the decision occasion and available features, evaluate against adequate baselines using valid splits and censoring treatment, and expose useful uncertainty. Recommendations additionally require causal identification or explicit hypothesis status, feasible authorised action and new outcome evidence. Re-evaluate after intervention changes exposure or behaviour; abstain when no useful decision can be supported.

**Discriminating failure.** A predictor reads the final resolution code from a completed case record while claiming to predict resolution early. Removing the field may destroy its benchmark advantage; deployment has not disproved learning, but the evaluation never tested the advertised task.

**Smallest adequate form.** A transparent prediction or prioritisation rule with correct temporal inputs and a real consumer. Causal policy optimisation, calibration layers and automation each require a separate trigger and justification. [EPM-S022; EPM-S023; EPM-S027; EPM-S028; EPM-S030; EPM-S057; EPM-S058]

### EPM-DM09 — Reproducibility and evidence custody (PM9)

**Objects/state.** An analytical result has a chain of source snapshot, extraction, transformations, model/algorithm versions, parameters, evaluation and interpretation. Evidence also has dependence across repeated logs, sites, synthetic generators and publication versions.

**Argument and limit.** Re-running the same computation establishes repeatability of a declared transformation, not the truth of its assumptions. Stable results across selected parameters do not establish semantic validity. Repeated runs and publications on one log increase analysis depth, not the number of independent organisational replications.

**Operation.** Preserve the minimal executable and interpretive chain, allow material trace-back, challenge plausible alternatives and record failed/negative results. Use domain participation as evidence, not an oracle. Where data cannot be shared, describe the blocked claim and avoid calling a substitute experiment an exact replication.

**Discriminating failure.** A complete script repeatedly reproduces a false personal ranking because the resource field denotes a shared service account. Computational custody makes the mistake inspectable but does not cure it.

**Smallest adequate form.** A reproducible query/script, identified data and versions, meaningful exclusions and a short interpretation note. More elaborate evidence infrastructure is justified only by scale, longevity, sensitivity or consequence. [EPM-S016; EPM-S019; EPM-S021; EPM-S022; EPM-S023; EPM-S036; EPM-S053; EPM-S056]

### EPM-DM10 — Responsible use and frontier boundaries (PM10)

**Objects/state.** The analytical setting includes participants, custodians, consumers, permissions, disclosure boundaries, model assistants and possible harms. Emerging representations and tools add hypotheses and costs as well as capabilities. Some research questions have no adequate practical evidence yet.

**Argument and limit.** Secure computation is not necessarily private output; pseudonyms are not anonymity; fluent generated text is not validated process evidence. An expressive or mathematically sound method is not necessarily externally useful. Non-use and retirement can be positive dispositions when there is no adequate or proportionate question.

**Operation.** State purpose and threat/decision boundaries, choose only the necessary data and methods, check generated or inferred content and provide contestability where people are affected. Evaluate current work by exact version and access level. Keep researched transfer questions unresolved instead of forcing universal adoption.

**Discriminating failure.** A federated protocol hides raw logs but reveals identifying trace lengths; an LLM extracts an event absent from the narrative; a dashboard triggers sanctions without a defensible reference. Each is a different failure requiring a different check.

**Smallest adequate form.** A bounded, non-identifying analysis or an alternative non-mining method. Federation, LLM assistance, rich object identity and new collection require demonstrable value and independently checked constraints. [EPM-S016; EPM-S017; EPM-S024; EPM-S026; EPM-S029; EPM-S033; EPM-S040; EPM-S043; EPM-S044; EPM-S054; EPM-S055]

The ten common profile dimensions are instantiated for every property, not merely named here. They carry event meaning, case/object unit, transformation/order, quality/selection, model bias, reference semantics, evaluation, time, causal boundary and human/privacy/consumer conditions. Shared domain-model text is expanded into each JSON record and its central dimension has a record-specific application.

## EVOLVED_PROCESS_MINING_CEREMONY_STRIPPING_LEDGER

Every retained mechanism has an individual stripping record in `ceremony_stripping_ledger` in [COMPOSITION_MODEL.json](EVOLVED_PROCESS_MINING_COMPOSITION_MODEL.json). The following complete index gives its cheaper adequate path. The full rows also name the protected failure, actual consumer, prerequisites, fuller-form trigger, simplification cost and omission/retirement conditions. A simpler mechanism is adequate only if it preserves the stated postcondition; minimality is not an instruction to delete useful models, meetings or documentation.

| Record / property | Minimal adequate alternative or non-trigger |
| --- | --- |
| EPM-CS001 / EPM-001 | Reuse a tested event dictionary when the recording mechanism has not changed. For a question about recorded transactions only, explicitly narrow the claim instead of reconstructing an entire process. |
| EPM-CS002 / EPM-002 | A query identifier, immutable extract and short mapping may suffice for a one-off local analysis; a full enterprise provenance platform is not required. |
| EPM-CS003 / EPM-003 | A simple, documented query is adequate where one source already contains the required event semantics. Do not build a generic integration layer merely to perform one bounded query. |
| EPM-CS004 / EPM-004 | Use the native activity labels when they already answer the question. A small manually checked mapping can dominate an automated abstraction model. |
| EPM-CS005 / EPM-005 | Report elapsed time between recorded milestones when service-time evidence is absent; do not impute a work interval merely to fill a dashboard. |
| EPM-CS006 / EPM-006 | Ignore order for an order-insensitive question, or flag the few ambiguous pairs instead of enumerating every possible trace. |
| EPM-CS007 / EPM-007 | Annotate an isolated uncertain record, narrow a claim, or tolerate a known harmless defect rather than rebuild the whole log. |
| EPM-CS008 / EPM-008 | Restrict the claim to the observed extract when that is enough; a census of all organisational activity is not necessary for every local question. |
| EPM-CS009 / EPM-009 | Use an existing coarse extract, a small sample, aggregates or no mining if they sufficiently answer the question. |
| EPM-CS011 / EPM-011 | A simple documented table is adequate within a bounded analysis where no interchange requires a larger standard. |
| EPM-CS012 / EPM-012 | Use one established case identifier when it captures the required relation and produces no material flattening distortion. |
| EPM-CS013 / EPM-013 | A relational join or explicit shared-event table may be enough; an executable object-centric net is not mandatory. |
| EPM-CS014 / EPM-014 | A small cardinality and trace sample check may establish that a chosen projection is harmless for this question. |
| EPM-CS015 / EPM-015 | Use an object-centric directly-follows view or a relational diagnostic when sound executable behaviour is not required. |
| EPM-CS016 / EPM-016 | Retain a tested existing view when added expressiveness would not change a decision. |
| EPM-CS019 / EPM-019 | For a directly-follows summary, state that it is a relation summary and do not claim executable semantics or complete process recovery. |
| EPM-CS021 / EPM-021 | A transparent frequency table or unfiltered directly-follows graph may be enough for a descriptive question. |
| EPM-CS022 / EPM-022 | Use a relation map or selected constraints when executable semantics add no useful distinction. |
| EPM-CS023 / EPM-023 | A simpler structured or heuristic miner is adequate when it preserves the relevant behaviour at lower cost. |
| EPM-CS024 / EPM-024 | A few manually specified, authorised constraints can be sufficient; mining a complete template universe is unnecessary. |
| EPM-CS025 / EPM-025 | A deterministic structured or heuristic method may dominate when it already supplies an adequate result. |
| EPM-CS026 / EPM-026 | Filter a small relevant segment, annotate a few events or use a table rather than adopting a large map-building ritual. |
| EPM-CS027 / EPM-027 | A small exception list linked to the main analysis may be sufficient; no additional model is needed for harmless isolated artefacts. |
| EPM-CS028 / EPM-028 | Report the observed directly-follows relation or a descriptive model without making an identification claim. |
| EPM-CS029 / EPM-029 | A focused conversation about one ambiguous event class may suffice; a standing modelling committee is unnecessary. |
| EPM-CS030 / EPM-030 | Analyse the relevant event subset or a single constraint without promising whole-process reconstruction. |
| EPM-CS031 / EPM-031 | For a purely descriptive comparison, say that the log differs from a model and make no normative allegation. |
| EPM-CS032 / EPM-032 | For a simple precedence rule, a direct trace check may be clearer and cheaper than a replay engine. |
| EPM-CS033 / EPM-033 | Use a simple constraint check or replay when it answers the question with acceptable ambiguity. |
| EPM-CS034 / EPM-034 | Use a single-perspective check for a genuinely single-perspective question; do not add attributes merely because they are available. |
| EPM-CS035 / EPM-035 | Flag a local ambiguity or withhold the affected judgement when full realisation analysis would not change a decision. |
| EPM-CS036 / EPM-036 | For an inconsequential exploratory discrepancy, record uncertainty without opening a full investigation. |
| EPM-CS038 / EPM-038 | Correct one extraction rule or annotate one justified exception when this closes the issue; rediscovery is not obligatory. |
| EPM-CS039 / EPM-039 | Evaluate only the dimensions material to a tightly bounded question, explaining exclusions instead of manufacturing a four-score dashboard. |
| EPM-CS040 / EPM-040 | For an obvious flower model or simple local question, an explicit behavioural counterexample may be clearer than a fragile aggregate metric. |
| EPM-CS041 / EPM-041 | Restrict the model to descriptive use when unseen-behaviour inference is not needed; use a simple estimate if a richer estimator has no demonstrated advantage. |
| EPM-CS042 / EPM-042 | A short trace, constraint or table may communicate the result better than any general process model. |
| EPM-CS043 / EPM-043 | A small controlled example can establish possibility or a counterexample if labelled as such; it need not imitate a deployment study. |
| EPM-CS046 / EPM-046 | Report a milestone-to-milestone elapsed interval without claiming a service-time decomposition when start or enablement events are unavailable. |
| EPM-CS047 / EPM-047 | A targeted examination of a few delayed cases may answer the question; a complete simulation or staffing model is unnecessary if the prerequisite is directly verifiable. |
| EPM-CS048 / EPM-048 | A small load or queue stratification may suffice; a full queueing or object-centric executable model is not always needed. |
| EPM-CS049 / EPM-049 | Analyse roles, teams or technical accounts at the level actually supported; omit personal attribution if it is unnecessary. |
| EPM-CS050 / EPM-050 | A process-level handoff count may be enough; do not construct a personal social network for an unrelated performance question. |
| EPM-CS051 / EPM-051 | Report separate descriptive distributions or refrain from ranking rather than fit an unjustified adjustment model. |
| EPM-CS052 / EPM-052 | A transparent analytical bound or small controlled pilot can dominate an elaborate simulator; no simulation is necessary for an already observable factual question. |
| EPM-CS053 / EPM-053 | A bounded explanation or confirmation that no change is needed can be a valid result; another dashboard is not obligatory. |
| EPM-CS054 / EPM-054 | One dated snapshot and model version may suffice for a one-off historical question. |
| EPM-CS055 / EPM-055 | A scheduled comparison of a few interpretable indicators can suffice for slow or low-consequence change. |
| EPM-CS056 / EPM-056 | Checking a deployment note and a few paired records may resolve the issue without retraining or process redesign. |
| EPM-CS057 / EPM-057 | Periodic batch analysis with explicit windows is adequate when near-real-time decisions are unnecessary. |
| EPM-CS058 / EPM-058 | A dated descriptive snapshot plus an unchanged reference may suffice; separate software services or new organisational owners are not required. |
| EPM-CS060 / EPM-060 | A historical description may use complete traces if it is labelled retrospective and makes no prospective-performance claim. |
| EPM-CS061 / EPM-061 | For an explicitly exchangeable retrospective question, a grouped random split can be acceptable; temporal splitting is not a ritual for unrelated claims. |
| EPM-CS062 / EPM-062 | A conservative rule, broad interval or human review may be preferable to a complex calibration layer whose assumptions cannot be justified. |
| EPM-CS063 / EPM-063 | A simple prioritisation rule may be adequate, or no prediction is warranted if no timely action is possible. |
| EPM-CS064 / EPM-064 | Use prediction for preparation or communicate a descriptive association without claiming a causal redesign benefit. |
| EPM-CS065 / EPM-065 | Present a small set of options or a human-reviewed hypothesis rather than automatic execution. |
| EPM-CS066 / EPM-066 | For unused exploratory predictions, no intervention-driven re-evaluation is needed beyond ordinary temporal checks. |
| EPM-CS069 / EPM-069 | A short script, query and immutable extract can suffice; a large reproducibility platform is not an intrinsic requirement. |
| EPM-CS070 / EPM-070 | Test a small set of material alternatives, not an exhaustive Cartesian product of every parameter. |
| EPM-CS071 / EPM-071 | One well-chosen knowledgeable participant or a small targeted check can be adequate for a narrow question; broad meetings are not mandatory. |
| EPM-CS072 / EPM-072 | A compact dependence note is sufficient where only a few sources share one public log. |
| EPM-CS073 / EPM-073 | A query, table, script or focused conversation can satisfy the real analytical function. |
| EPM-CS074 / EPM-074 | One explicit limitation statement tied to the result can defeat an overclaim; no duplicate review layer is required. |
| EPM-CS075 / EPM-075 | Use ordinary transaction queries, interviews, process modelling, direct observation or no intervention where those methods answer the question more adequately. |
| EPM-CS076 / EPM-076 | Use access restriction, aggregation, a smaller lawful extract or no release when these meet the purpose more safely than elaborate transformation. |
| EPM-CS077 / EPM-077 | Use non-identifying process-level evidence or refrain from personal ranking when individual attribution is unnecessary. |
| EPM-CS078 / EPM-078 | Separate local analyses or a negotiated aggregate may suffice; federation is not a default for a single trusted dataset. |
| EPM-CS079 / EPM-079 | A deterministic query, template or manual review may be cheaper and more reliable for a small stable task. |
| EPM-CS081 / EPM-081 | Manual annotation of a small corpus or a simple deterministic extraction can be adequate; full generative extraction is not mandatory. |
| EPM-CS084 / EPM-084 | A short explicit qualification in the existing result or conversation may suffice. No dedicated new protocol, service, committee or form is required for every property. |

Retirement is an actual system option. Remove a control whose risk, consumer or required distinction has disappeared, or substitute an already adequate mechanism. Preserve justified evidence for past consequential decisions. A retained capability may be supplied by one existing script, institution or conversation alongside several others; this corpus does not require one new artefact or owner per property.

## EVOLVED_PROCESS_MINING_CRITICISM_LEDGER

### EPM-C001 — EPM-001, EPM-003, EPM-005, EPM-006, EPM-007, EPM-010

**Strongest objection.** Correctly formatted records can encode delayed, coarse or administrative observations rather than assumed work events.

**Evidence and locator.** Timestamp metrics and a single-hospital imperfection study reveal concrete recording mechanisms; no universal defect prevalence is inferred. [EPM-S039; EPM-S045] — S039 quality dimensions and examples; S045 §§4–6.

**Response and current judgement.** Validate event meaning and repair only with evidence; preserve uncertainty. Raises semantic adequacy above successful import; EPM-010 rejected. **REFINED**.

**Residual uncertainty.** Unrecorded work may be unrecoverable.

### EPM-C002 — EPM-002, EPM-069, EPM-074, EPM-084

**Strongest objection.** An exact reproducible computation may be semantically wrong or evaluate a different task.

**Evidence and locator.** Primary methodological critiques show that custody and checklists do not establish the premises of the inference. [EPM-S014; EPM-S022; EPM-S056] — S014 extraction discussion; S022 leakage analysis; S056 §6.3.

**Response and current judgement.** Keep auditability and correctness separate; inspect claim-specific assumptions at handoffs. Adds a composition-induced handoff obligation EPM-084 rather than more documentation by default. **GENERALISED**.

**Residual uncertainty.** Effectiveness of the whole handoff design is not independently tested.

### EPM-C003 — EPM-008, EPM-041, EPM-043, EPM-061

**Strongest objection.** Sampling and censoring can make model or predictor evaluations unrepresentative.

**Evidence and locator.** Controlled data-quality experiments and benchmark construction analysis; synthetic ground truth does not establish real-population validity. [EPM-S020; EPM-S022; EPM-S053] — S020 experimental sections; S022 §§5.3–5.7; S053 guarantee experiments.

**Response and current judgement.** Declare target and selection; compare appropriate simple baselines and expose exclusions. Generalisation remains assumption-sensitive; no universal longest-case trimming rule retained. **NARROWED**.

**Residual uncertainty.** Unknown selection mechanisms can prevent external claims.

### EPM-C004 — EPM-012, EPM-013, EPM-014, EPM-018, EPM-046

**Strongest objection.** Flattening interacting objects manufactures repeated work and duration artefacts.

**Evidence and locator.** OPerA demonstrates distortion on a filtered loan/application–offer log; analysis is not independent truth about all interactions. [EPM-S014; EPM-S050] — S014 convergence/divergence; S050 §5.2.

**Response and current judgement.** Use typed relations or validate the chosen projection against the actual question. Object-centric mechanisms retained; universal superiority EPM-018 rejected. **GENERALISED**.

**Residual uncertainty.** Identity and relation extraction can still be wrong.

### EPM-C005 — EPM-015, EPM-018, EPM-082

**Strongest objection.** Object-centric approaches disagree about semantics and soundness; guarantees do not automatically transfer.

**Evidence and locator.** Exact formalisms differ, including type-level tokens versus identifier-aware dynamic relations. The 2021 preprint proof-status ambiguity is not certified. [EPM-S026; EPM-S043; EPM-S044] — S026 conceptual distinctions; S043 soundness definitions; S044 formal construction.

**Response and current judgement.** Name the formalism and its assumptions; preserve incompatible alternatives. EPM-015 assumption-sensitive and EPM-082 unresolved, not a single settled object-centric guarantee. **STILL_CONTESTED**.

**Residual uncertainty.** Broad scalable empirical validation across uncertainty and identity semantics is missing in the inspected corpus.

### EPM-C006 — EPM-019, EPM-020, EPM-028

**Strongest objection.** Finite logs and restricted model classes do not support unrestricted reconstruction of a unique process.

**Evidence and locator.** Original theorem conditions and explicit extensions delimit the claim; analytical observational-equivalence probe illustrates underdetermination. [EPM-S005; EPM-S031; EPM-S053] — S005 definitions/theorem; S031 extension; S053 guarantee hierarchy.

**Response and current judgement.** Distinguish sound construction, scoped rediscovery and real-world identification. Original alpha survives historically and as a baseline; its universal-default practice is superseded. **REPLACED**.

**Residual uncertainty.** No universal successor dominates all model objectives.

### EPM-C007 — EPM-021, EPM-026, EPM-027, EPM-070

**Strongest objection.** Filtering can optimise appearance or scores by deleting important behaviour.

**Evidence and locator.** Frequency-based methods explicitly select what is represented; later experiments show stability and correctness are distinct. [EPM-S006; EPM-S013; EPM-S056] — S006 thresholds; S013 abstraction; S056 noise experiment.

**Response and current judgement.** Test material exceptions and plausible settings; keep a route to suppressed evidence. Noise tolerance retained, not a universal threshold or least-detail rule. **REFINED**.

**Residual uncertainty.** Unrecognised rare failures remain vulnerable to suppression.

### EPM-C008 — EPM-022, EPM-023, EPM-025

**Strongest objection.** Formal sophistication or expensive search can produce a sound but unhelpful, costly or metric-optimised model.

**Evidence and locator.** Comparisons include computational failures and different quality outcomes; global search does not prove global operational correctness. [EPM-S019; EPM-S053; EPM-S056] — S019 benchmark methods/results; S053 §5; S056 §§1,5.

**Response and current judgement.** Select by task, formalism and cost; preserve simple alternatives. Inductive, ILP and evolutionary methods remain guarded alternatives. **NARROWED**.

**Residual uncertainty.** External utility cannot be read off an algorithm guarantee.

### EPM-C009 — EPM-024

**Strongest objection.** High support can reflect absent activation, while constraint sets can be redundant or hard to interpret.

**Evidence and locator.** Formal finite-trace semantics distinguishes vacuous satisfaction from activated compliance. [EPM-S041; EPM-S042] — S041 constraint discovery; S042 activation and semantic vacuity.

**Response and current judgement.** Report activation basis and assess consistency/redundancy. Declarative discovery retained in an activation-aware form, not as automatically authorised rules. **REFINED**.

**Residual uncertainty.** Large data-rich constraint systems may remain costly to validate.

### EPM-C010 — EPM-030, EPM-084

**Strongest objection.** A collection of useful local results may fail to form one globally coherent process.

**Evidence and locator.** Local models deliberately cover fragments; different model semantics introduce unresolved interfaces. The general composition criticism is analytical. [EPM-S049; EPM-S026; EPM-S056] — S049 local model scope; S026 integration challenges; S056 claim design.

**Response and current judgement.** Preserve fragment boundaries and demand evidence for consequential global claims. Local discovery remains conditional; handoff obligations are explicitly added. **NARROWED**.

**Residual uncertainty.** Whole-process reconstruction may not be warranted or needed.

### EPM-C011 — EPM-031, EPM-036, EPM-037, EPM-038, EPM-058

**Strongest objection.** Making observations fit a reference or repairing the reference does not establish that either is desirable or authorised.

**Evidence and locator.** Model repair changes descriptive behaviour; normative judgement is not part of an alignment optimum. [EPM-S017; EPM-S047] — S017 responsible-use framework; S047 repair objective.

**Response and current judgement.** Identify reference authority and diagnose cause before choosing data, model, process or rule revision. EPM-037 rejected; descriptive and normative revision kept distinct. **REFINED**.

**Residual uncertainty.** Disputed obligations require external interpretation.

### EPM-C012 — EPM-032, EPM-033, EPM-034

**Strongest objection.** Replay and alignment diagnostics depend on search choices, costs and included perspectives.

**Evidence and locator.** Multi-perspective examples show control-first diagnosis can differ from joint diagnosis. Optimality is cost-relative. [EPM-S009; EPM-S010; EPM-S046] — S009 replay; S010 move/cost semantics; S046 §2.

**Response and current judgement.** Disclose costs, approximation and perspective requirements; use cheaper checks when adequate. Comparison mechanisms retained as scoped evidence, not unique causal explanations. **REFINED**.

**Residual uncertainty.** Equal optima and computational limits can leave diagnosis unresolved.

### EPM-C013 — EPM-035, EPM-082

**Strongest objection.** Uncertainty bounds can be wide or exclude the true realisation, and do not become probabilities.

**Evidence and locator.** Formal set-of-realisations approach provides scoped extrema rather than externally calibrated likelihoods. [EPM-S025; EPM-S043] — S025 §§3–5; S043 model semantics.

**Response and current judgement.** State the admitted set, approximation and what is robust across it; abstain if uninformative. Uncertain conformance assumption-sensitive; broad object-centric transfer unresolved. **NARROWED**.

**Residual uncertainty.** Scalability and completeness of the uncertainty representation remain limits.

### EPM-C014 — EPM-039, EPM-040, EPM-044, EPM-045

**Strongest objection.** Quality measures can violate expected properties and rankings can depend on the operationalisation.

**Evidence and locator.** Specific precision counterexamples and a methodology study challenge universal best-model claims. [EPM-S018; EPM-S056] — S018 counterexamples; S056 §§1,5–6.

**Response and current judgement.** Separate dimensions, definitions, baselines and decision preferences. Precision easily gamed; universal aggregate ranking and perfect-fit sufficiency rejected. **REFINED**.

**Residual uncertainty.** No one metric family settles every representation and task.

### EPM-C015 — EPM-041

**Strongest objection.** More sophisticated generalisation estimation does not necessarily improve estimates when input representativeness changes.

**Evidence and locator.** Controlled experiments with known generating processes; not organisational effectiveness trials. [EPM-S020] — S020 experiments and discussion.

**Response and current judgement.** Match estimator to target and data quality; keep simpler baselines. Generalisation assessment remains assumption-sensitive, not an automatic scalar. **NARROWED**.

**Residual uncertainty.** Real generating behaviour is often unknown.

### EPM-C016 — EPM-043, EPM-069, EPM-070, EPM-073

**Strongest objection.** An experimental checklist can be answered mechanically while its reasoning is wrong.

**Evidence and locator.** Authors demonstrate their own methodology; they do not independently validate checklist effectiveness or promise correctness. [EPM-S056] — S056 §5 example and §6.2–6.3 limitations.

**Response and current judgement.** Require coherent claims, measurements and interpretations, not yes/no paperwork. Reproducibility retained; dashboard/checklist possession stripped of sufficiency. **REFINED**.

**Residual uncertainty.** Independent evaluation of methodological aids is limited.

### EPM-C017 — EPM-046, EPM-047, EPM-048

**Strongest objection.** Elapsed delay can be misattributed to effort, worker performance or a missing prerequisite; perfect replay may conceal missing events.

**Evidence and locator.** Performance papers and the hospital study show the dependence on lifecycle/context; OPerA acknowledges problems with nonconforming or missing observations. [EPM-S039; EPM-S045; EPM-S048; EPM-S050] — S039 timestamp semantics; S045 recording examples; S048 context; S050 §6.

**Response and current judgement.** Separate interval from explanation and test source/context alternatives. Performance analysis retained; no causal bottleneck verdict inferred from timing alone. **NARROWED**.

**Residual uncertainty.** Unobserved manual work may remain inaccessible.

### EPM-C018 — EPM-049, EPM-050, EPM-051, EPM-077

**Strongest objection.** Resource logs can misrepresent people and power relations, producing false objectivity or surveillance.

**Evidence and locator.** Early social mining itself encounters shared identifiers; responsible-use work articulates normative risks rather than a controlled mitigation trial. [EPM-S012; EPM-S017] — S012 shared-account example; S017 FACT concerns.

**Response and current judgement.** Verify resource units, narrow social claims, provide contestability and minimise unnecessary identity. Organisational analysis is conditional and people-related use constrained. **REFINED**.

**Residual uncertainty.** Effectiveness of institutional contestability mechanisms is not established by the framework alone.

### EPM-C019 — EPM-053, EPM-068, EPM-083

**Strongest objection.** Success stories and a reported agreement do not identify realised causal or economic benefit.

**Evidence and locator.** RWS reports an operational response; interviews report costs and challenges. Neither estimates universal return or failure prevalence. [EPM-S016; EPM-S032] — S016 interview/survey method and challenges; S032 reported priority response.

**Response and current judgement.** Separate finding, agreement, action and consequence; require a local comparison for stronger benefit claims. Universal economic return rejected; broad prescription benefit unresolved. **NARROWED**.

**Residual uncertainty.** Negative deployment outcomes are underrepresented and private evidence limits prevalence claims.

### EPM-C020 — EPM-054, EPM-055, EPM-056, EPM-057

**Strongest objection.** A drift detector can miss relevant change, alarm on instrumentation or forget consequential history.

**Evidence and locator.** Benchmark effects vary by change type; streaming explicitly trades history for resources and latency. [EPM-S021; EPM-S034; EPM-S037; EPM-S039] — S021 §6 benchmark; S034 windows/prefixes; S039 imperfections.

**Response and current judgement.** Evaluate relevant drift classes and investigate alarms before revision. Streaming remains conditional; drift detection is assumption-sensitive. **REFINED**.

**Residual uncertainty.** Compound changes and undocumented instrumentation may be inseparable.

### EPM-C021 — EPM-058, EPM-059

**Strongest objection.** Automatic adaptation can make harmful deviations the new reference.

**Evidence and locator.** This is an analytical criticism of combining valid descriptive mechanisms without an authority boundary, not a claim that a specific deployment did so. [EPM-S017; EPM-S037; EPM-S047] — S017 responsibility; S037 drift; S047 descriptive repair.

**Response and current judgement.** Separate descriptive model updates from authorised expectation revision. Automatic normative normalisation rejected; two-track continuity retained. **REJECTED**.

**Residual uncertainty.** Stable references can also become obsolete and need a real revision route.

### EPM-C022 — EPM-060, EPM-061, EPM-067

**Strongest objection.** Predictive superiority can be manufactured by future information, dependent prefixes and biased complete-case selection.

**Evidence and locator.** Primary benchmark criticism identifies leakage and censoring mechanisms; outcome benchmarks remain task-bound. [EPM-S022; EPM-S023] — S022 §§5.3–5.7; S023 benchmark design.

**Response and current judgement.** Reconstruct decision-time inputs, split units and selection; compare adequate baselines. No universal deep-model superiority retained. **REFINED**.

**Residual uncertainty.** Source overwrite can make prospective reconstruction impossible.

### EPM-C023 — EPM-062

**Strongest objection.** Confidence, probability calibration and marginal coverage are different; neither implies individual safety under arbitrary drift.

**Evidence and locator.** One static sepsis-log comparison and external conformal theory with explicit assumptions. [EPM-S057; EPM-S058] — S057 §4.6 and limitations; S058 Theorem 1 and §4.

**Response and current judgement.** Separate uncertainty targets and provide useful abstention/review; qualify drift transfer. Uncertainty-aware support retained as an assumption-sensitive statistical import. **NARROWED**.

**Residual uncertainty.** Dependent case prefixes and changing policies require additional validation.

### EPM-C024 — EPM-052, EPM-063, EPM-064, EPM-065, EPM-066, EPM-068

**Strongest objection.** Estimated or simulated treatment gains may fail under confounding, resource competition, feedback or implementation differences.

**Evidence and locator.** Recent methods make progress but the inspected evidence is not a broad independently replicated field benefit. [EPM-S027; EPM-S030] — S027 evaluation/limitations; S030 resource-constrained formulation.

**Response and current judgement.** State causal identification, feasibility, authority and policy-specific evaluation; renew evidence after feedback. Causal boundary strongly retained; broad deployed benefit unresolved. **NARROWED**.

**Residual uncertainty.** Multi-site prospective effects and adverse consequences remain insufficiently established here.

### EPM-C025 — EPM-072

**Strongest objection.** Repeated public logs, bootstrap samples and paper versions inflate apparent independence.

**Evidence and locator.** Examples include 200 bootstrap resamples of one sepsis dataset and conference/journal text-extraction versions from one programme. [EPM-S016; EPM-S019; EPM-S021; EPM-S023; EPM-S055; EPM-S057] — Methods and dataset descriptions in each work.

**Response and current judgement.** Record dependencies without assuming shared authors imply shared sites. Dependence-aware evidence accounting retained. **REFINED**.

**Residual uncertainty.** Private log identities may remain undisclosed.

### EPM-C026 — EPM-076, EPM-078

**Strongest objection.** Privacy protection depends on the attacker and release boundary; encryption does not hide all output-derived information.

**Evidence and locator.** Federated trace-based discovery exposes identifiers/lengths; group methods trade detail for protection under stated background knowledge. [EPM-S033; EPM-S040] — S033 protocol variants; S040 threat/background-knowledge models.

**Response and current judgement.** Assess processing and output disclosure separately and compare simple alternatives. Privacy/federation retained as assumption-sensitive mechanisms, not universal secrecy. **NARROWED**.

**Residual uncertainty.** Auxiliary information and repeated releases can change exposure.

### EPM-C027 — EPM-079, EPM-080, EPM-081

**Strongest objection.** Fluent generated answers, judge-dependent benchmarks and synthetic extraction tests do not establish autonomous or deployed competence.

**Evidence and locator.** LLM-judge dependence and the 2026 extraction paper’s explicit absence of a fully operational business deployment constrain claims. [EPM-S029; EPM-S055] — S029 Tables 4–5; S055 §§5–6.

**Response and current judgement.** Use checkable bounded assistance and preserve text provenance; retain external authority. LLM use conditional, text extraction assumption-sensitive, autonomous authority inference rejected. **NARROWED**.

**Residual uncertainty.** Net productivity gain after checking and privacy costs needs independent field evidence.

### EPM-C028 — EPM-075, EPM-083

**Strongest objection.** Mining can cost more, expose more people or produce less useful evidence than a simpler method.

**Evidence and locator.** Practitioner obstacles and normative analysis support the need for alternatives, not a universal failure estimate. [EPM-S016; EPM-S017] — S016 challenges; S017 responsible-use framing.

**Response and current judgement.** Permit no mining or retirement with a stated evidence/value reason and reconsideration trigger. Non-use becomes a legitimate branch of the composed system. **REFINED**.

**Residual uncertainty.** Non-use can also conceal important problems; justification must be challengeable.

### EPM-C029 — EPM-084

**Strongest objection.** Correct components can be joined through incompatible units, semantics or temporal claims.

**Evidence and locator.** No direct trial of this composed Evolved system exists. Component mismatches supply examples and analytical grounds for the handoff invariant. [EPM-S014; EPM-S022; EPM-S026; EPM-S046; EPM-S050; EPM-S056] — Cross-source analytical composition, with each source’s inspected limitations.

**Response and current judgement.** Carry material claim conditions and check receiver compatibility; narrow or interrupt on mismatch. EPM-084 added during composition, explicitly not academic consensus or a validated organisational protocol. **GENERALISED**.

**Residual uncertainty.** The minimal effective handoff and its cost require prospective evaluation.


## EVOLVED_PROCESS_MINING_EVOLUTION_UNDER_CRITICISM

The transitions are changes to mechanism, assumptions or accepted claims, not cosmetic renaming. Some remain alternatives. The table compresses the full criticism ledger; each candidate also records its own transition and rationale.

| Branch | Original problem/response | Changed mature mechanism | Transition |
| --- | --- | --- | --- |
| Event data | Treat execution records as available inputs. | Test event meanings and transformations; retain uncertainty rather than forcing perfect logs. | REFINED |
| Alpha lineage | Recover a workflow net under formal assumptions. | Preserve the theorem/baseline but replace the unrestricted operational default with guarded method choice. | REPLACED_WITHIN_DEFAULT_SCOPE |
| Noise and abstraction | Reduce noisy or unreadable behaviour. | Inspect material exceptions and expose sensitivity and recoverable detail. | REFINED |
| Declarative discovery | Mine high-support constraints. | Distinguish activation from vacuous satisfaction and assess interacting constraints. | REFINED |
| Conformance | Quantify or explain model–log mismatch. | Preserve cost/reference semantics and rival causes; separate descriptive repair from normative authority. | GENERALISED_AND_NARROWED |
| Evaluation | Rank models by quality metrics. | Keep separate targets and compatible operationalisations; account for selection and missing computations. | REFINED |
| Performance/social mining | Infer bottlenecks and resource relations. | Validate interval and identity meaning; seek contextual explanation before attribution. | NARROWED |
| Drift/streams | Adapt to changing observations. | Investigate instrumentation alternatives and retain separate reference continuity. | REFINED |
| Prediction/prescription | Predict outcomes and recommend actions. | Reconstruct available information, identify causal effects, constrain feasibility and re-evaluate after feedback. | HYBRIDISED_AND_NARROWED |
| Object-centric methods | Retain interacting entities and shared events. | Add exact identity/formalism obligations; retain alternatives and unresolved broad transfer. | GENERALISED_WITH_UNRESOLVED_BOUNDARIES |
| Privacy/federation | Protect data while retaining analytical use. | Specify attacker and processing/release boundary, with utility and cost trade-offs. | DOMAIN_SPECIFIC_REFINEMENT |
| LLM/text assistance | Automate interpretation or event extraction. | Keep generated records as checkable hypotheses and version-specific benchmark evidence. | NARROWED |
| Whole-system composition | Join useful methods. | Carry material validity conditions across handoffs and reopen affected claims on changed assumptions. | NEW_ANALYTICAL_COMPOSITION_OBLIGATION |


## EVOLVED_PROCESS_MINING_INTERNAL_TENSIONS

### EPM-T001 — Adequate and challengeable evidence versus Privacy and proportionate collection

Affected: EPM-002, EPM-008, EPM-009, EPM-069, EPM-076. **Cost:** More detail and retention increase exposure; minimisation can obstruct rare-event or historical checks.

**Discriminator.** The first side is favoured when: Consequential disputed findings requiring trace-back and evidence that identifiers are necessary. The second is favoured when: Low-risk aggregate question or disproportionate re-identification risk.

**Supported selection or hybrid.** Retain protected source mappings and release only necessary aggregates; document where exact reproduction is unavailable.

**Hybrid failure and remaining limit.** Pseudonymous keys remain linkable; excessive suppression destroys the intended distinction. No universal privacy/utility scalar resolves institutional values.

### EPM-T002 — Comprehensibility versus Preservation of material exceptions

Affected: EPM-004, EPM-016, EPM-026, EPM-027, EPM-042. **Cost:** Detail burdens users; simplification can hide consequential behaviour.

**Discriminator.** The first side is favoured when: The consumer needs a high-level orientation and exceptions do not change the decision. The second is favoured when: Rare behaviours determine a rule, harm or disputed diagnosis.

**Supported selection or hybrid.** A simple main view with a traceable, explicitly scoped exception view.

**Hybrid failure and remaining limit.** Users treat the main map as complete or exceptions become an unread annex. The appropriate view depends on actual user task performance.

### EPM-T003 — Scoped formal guarantees versus Expressiveness for actual work

Affected: EPM-019, EPM-022, EPM-024, EPM-030. **Cost:** Restricted languages can misrepresent reality; expressive ones can be difficult to analyse.

**Discriminator.** The first side is favoured when: Executable structured behaviour is needed and the lost distinctions are immaterial. The second is favoured when: Flexible constraints, non-structured relations or a useful local question are central.

**Supported selection or hybrid.** Use distinct views with explicit translations and no unsupported global guarantee.

**Hybrid failure and remaining limit.** An informal cross-view mapping silently claims semantic equivalence. Some combinations remain incompatible rather than hybridisable.

### EPM-T004 — Robust frequent-behaviour fit versus Generalisation and important rare behaviour

Affected: EPM-021, EPM-027, EPM-039, EPM-041. **Cost:** Noise tolerance competes with preserving valid but infrequent cases.

**Discriminator.** The first side is favoured when: The target is typical operational flow and known recording artefacts dominate. The second is favoured when: Exception analysis or unseen-but-valid behaviour is consequential.

**Supported selection or hybrid.** Inspect material filtered cases and test thresholds; select by target rather than a fixed noise percentage.

**Hybrid failure and remaining limit.** Tuning against held-out test results leaks evaluation; exception checks retain all errors. Rare genuine behaviour may be indistinguishable from corruption.

### EPM-T005 — Adaptive descriptive accuracy versus Continuity of authorised expectations

Affected: EPM-031, EPM-038, EPM-054, EPM-058, EPM-059. **Cost:** Fixed references become obsolete; adaptive references can normalise harmful change.

**Discriminator.** The first side is favoured when: The model is explicitly descriptive and the recording regime is understood. The second is favoured when: The model represents a continuing obligation or historically comparable standard.

**Supported selection or hybrid.** Maintain separate descriptive/reference identities with an explicit authorised revision route.

**Hybrid failure and remaining limit.** A nominally separate reference is auto-updated by the same trigger without substantive decision. Disputed authority can leave revision unresolved.

### EPM-T006 — Diagnostic fidelity versus Cost and timely intelligibility

Affected: EPM-032, EPM-033, EPM-034, EPM-035. **Cost:** Exact, rich comparison increases computation and semantic inputs.

**Discriminator.** The first side is favoured when: Multiple plausible explanations have materially different consequences. The second is favoured when: A simple check or replay already answers the bounded question.

**Supported selection or hybrid.** Escalate only the ambiguous consequential subset to richer comparison and expose approximations.

**Hybrid failure and remaining limit.** Cheap screening removes exactly the cases needing richer analysis. There is no universal escalation threshold independent of consequence.

### EPM-T007 — Contextual fairness versus Interpretability and adequate sample size

Affected: EPM-046, EPM-048, EPM-051, EPM-077. **Cost:** Adjustment fragments samples and can hide structural inequities.

**Discriminator.** The first side is favoured when: Case mix and shared-resource context demonstrably change a comparison. The second is favoured when: Context is poorly measured or adjusted rankings would imply unwarranted causal fairness.

**Supported selection or hybrid.** Report stratified descriptions and limits instead of forced individual rankings.

**Hybrid failure and remaining limit.** Aggregates mask affected groups; adjustment conditions on a consequence of unfair treatment. Normative fairness is not identified by event statistics alone.

### EPM-T008 — Timely adaptation versus Stable, investigateable evidence

Affected: EPM-055, EPM-056, EPM-057, EPM-058. **Cost:** Fast windows forget history and increase alarms; slow updates retain obsolete models.

**Discriminator.** The first side is favoured when: Consequential decisions require fast response and investigations are feasible. The second is favoured when: Changes are slow or alarms cannot be acted upon in time.

**Supported selection or hybrid.** Use bounded online indicators with periodic retained snapshots and targeted investigation.

**Hybrid failure and remaining limit.** Snapshots miss critical short-lived events or retention violates privacy limits. Detection/response benefit depends on actual operational capacity.

### EPM-T009 — Actionable support versus Honest uncertainty and causal restraint

Affected: EPM-062, EPM-063, EPM-064, EPM-065, EPM-066. **Cost:** Abstention burdens humans; aggressive action can amplify error or confounding.

**Discriminator.** The first side is favoured when: A feasible action has credible effect evidence and uncertainty is useful to the recipient. The second is favoured when: Intervention effect is not identified, support is weak or action cannot be safely evaluated.

**Supported selection or hybrid.** Offer bounded options or a pilot with a known comparison and review route.

**Hybrid failure and remaining limit.** Human review becomes automatic acceptance and unchanged benchmark claims persist after feedback. Wide uncertainty may correctly make the desired recommendation unavailable.

### EPM-T010 — Relational completeness versus Computational, privacy and interpretive economy

Affected: EPM-013, EPM-015, EPM-016, EPM-078, EPM-082. **Cost:** Object-centric and federated approaches add identity, protocol and validation burdens.

**Discriminator.** The first side is favoured when: Cross-object or cross-organisation relations materially change the question. The second is favoured when: One case notion or local aggregate already suffices.

**Supported selection or hybrid.** Preserve only needed typed relations and use protocol variants matched to disclosed threat models.

**Hybrid failure and remaining limit.** Incompatible identity mappings or released outputs defeat the intended benefit. Broad interoperability and external validity remain incomplete.

### EPM-T011 — Reviewable evidence versus Avoidance of analytical bureaucracy

Affected: EPM-069, EPM-070, EPM-071, EPM-073, EPM-074, EPM-084. **Cost:** Extensive documentation and repeated checks can cost more than the decision warrants.

**Discriminator.** The first side is favoured when: High consequence, contested interpretation or long-lived reuse. The second is favoured when: A small, stable, low-consequence question with a directly checkable result.

**Supported selection or hybrid.** Use existing scripts and communications to carry material assumptions; no required one-document or one-owner per property.

**Hybrid failure and remaining limit.** Templates are completed without understanding or the cheap path omits a crucial assumption. The least costly effective handoff needs field testing.

### EPM-T012 — Reduced extraction and explanation effort versus Grounded validity and proportionate exposure

Affected: EPM-079, EPM-081, EPM-075. **Cost:** LLM checking, private-data handling and version drift can erase automation savings.

**Discriminator.** The first side is favoured when: Large textual evidence with checkable source spans and a real downstream consumer. The second is favoured when: Small stable task, highly ambiguous text or inability to independently check generated output.

**Supported selection or hybrid.** Use assisted candidate extraction plus sampled/high-consequence verification and deterministic checks.

**Hybrid failure and remaining limit.** Selective checking misses systematic errors; benchmark gains derive from synthetic text patterns. Net benefit and reliability in fully operational settings remain incompletely measured.


## EVOLVED_PROCESS_MINING_COMPOSED_SYSTEM

### Purpose and environment

The composed system answers a bounded question about process behaviour using event evidence and explicit process representations, then supports only the decisions that evidence warrants. Its environment includes source systems, recording practices, organisational participants, external rules, resource limits and changing work. These are not all under the analyst’s control. Events are observations through a recording mechanism; models are representations under a formalism; findings are claims with assumptions; and real interventions are actions of actors with actual authority and capability.

This composition is analytical. It reconciles the inspected mechanisms without asserting that the complete design is a recognised academic protocol or has already produced measured organisational benefit. Component formal results and field cases remain evidence about their own scopes. The 70 machine-readable relations make the proposed connections and new costs explicit.

### Objects, state and claim identity

The smallest relevant state contains a question and receiving use, source/event identity, an analysis unit and time scope, the chosen process relation or model, and a record of the result’s interpretation and limitations. Richer configurations add object relationships, uncertainty sets, reference authority, calibration data, policies or streaming state only when needed. The presence of these optional objects is not a maturity score.

A model’s identity includes its semantics and provenance, not just a file name. A process tree with a construction guarantee is not interchangeable with a type-level object net or an identifier-aware model. A current descriptive model is not automatically the current authorised reference. A prediction trained under one policy is not automatically valid after that policy changes. EPM-054 records temporal identity; EPM-031 records reference status; EPM-019 records representation bias. EPM-084 makes their material conditions survive a handoff. [EPM-S007; EPM-S022; EPM-S026; EPM-S043; EPM-S044; EPM-S047]

### The central composition-induced property

**EPM-084—Validity-preserving analytical handoffs** was added because the system cannot be made coherent by unioning individually useful techniques. A downstream method can silently strengthen an upstream result even when both components are competently implemented. It may interpret a flattened trace count as a count of real events, a replay optimum as a causal diagnosis, a conformal prediction set as individual certainty, or a descriptive update as an authorised rule change. The error is at the connection, not necessarily inside either algorithm.

The proposed mechanism is deliberately small: carry the material unit, event interpretation, population/time scope, model or reference semantics, uncertainty and supported use to the receiver. The receiver checks the assumptions its own claim needs. Incompatibility produces additional evidence, an explicit translation, a narrower claim or non-use. A later material change to those assumptions invalidates or reopens affected downstream claims. This need not create a new form, service or owner; an existing result note, script or conversation can be the adequate carrier.

The reasoning is conditional rather than a new formal guarantee. When a receiving claim depends on an upstream meaning, changing that meaning without checking the dependency defeats the receiving justification. This supports a boundary invariant. It does not prove that every relevant assumption can be enumerated, that participants understand the note or that the resulting system improves outcomes. Those are residual field obligations, and the overhead of the handoff is itself a possible failure. [Component grounds: EPM-S014; EPM-S022; EPM-S026; EPM-S046; EPM-S050; EPM-S056. The invariant and its proposed operation are this study’s synthesis.]

### Branching operation, not a forced serial pipeline

An inquiry can enter through a question, a surprising trace, a conformance mismatch, a timing pattern, a drift alarm or a proposed intervention. It need not begin by discovering a complete model. An independently supplied reference can go directly to conformance after event interpretation. A local question can be answered with a fragment or constraint. A descriptive relation can be sufficient without prediction. A generic data query or interview may be a better non-mining alternative.

Several analyses can run concurrently on a common evidence base. Discovery, performance and conformance may each reveal a different defect. Their outputs are not automatically mutually validating: two methods can share the same mistaken extraction. The dependency is therefore expressed through common evidence identity and explicit limits, not through a claim that more corroborating visualisations are independent replications. [EPM-S016; EPM-S019; EPM-S049; EPM-S056]

The important loops are substantive. A surprising duration returns to lifecycle and source interpretation. A domain challenge returns to event or activity meaning. A drift alarm returns to instrumentation, population and work-change alternatives. A confirmed mismatch can return to extraction, descriptive model repair, process correction or authorised reference revision. An acted-upon recommendation returns to the temporal and causal evaluation of the changed regime. These loops can stop at an unresolved or no-action disposition when further evidence is unavailable or not worth its cost.

Interrupts are also legitimate. If event meaning fails, an affected process claim stops or narrows. If reference authority is disputed, normative inference stops even while descriptive comparison continues. If a privacy boundary prevents necessary linkage, an object-aware question can be declined without pretending a flattened view preserves it. If calibration assumptions fail or no timely action is available, prediction can abstain or be retired. The system does not require all work to stop because one branch is unsupported; it prevents unsupported branches from lending unwarranted authority to others.

### Communication and real action

Source custodians exchange recording definitions, query boundaries and version information with analysts. Domain participants examine concrete traces, explain unlogged prerequisites and challenge attribution. Reference owners explain intended behaviour and the scope of authorised change. Operational actors receive findings or recommendations, decide within their mandate and act on actual cases, resources or policies. Affected people and data-governance participants can constrain collection, disclosure and interpretation. These interactions are functional only when they change a justified claim or a real decision; attendance and sign-off alone do not satisfy them. [EPM-S016; EPM-S017; EPM-S032; EPM-S045]

A useful separation has three steps that must not be collapsed: **distinguishing**, **being authorised and able to act**, and **achieving a consequence**. An alignment distinguishes a discrepancy under its semantics. A process owner may be authorised to change a procedure, but an analyst is not necessarily that owner. An agreed priority change still needs implementation and outcome evidence before it can be called an achieved reduction in delay. The RWS case is important precisely because it documents a real communication and response step while leaving the stronger causal claim unestablished. [EPM-S010; EPM-S032]

For recommendations, actual action records matter. Advice can be ignored, delayed, applied to a different case or constrained by shared resources. The action taken is therefore an observed input to the next evaluation, not something inferred from the existence of a recommendation. Intervention feedback may also change which cases are observed and how outcomes are generated. EPM-066 reopens claims affected by that change rather than continuing to display a historical score as current validation. [EPM-S027; EPM-S030; analytical composition EPM-053, EPM-065–EPM-066]

### Selection and incompatibility

Not all branches should be unified into one compulsory representation. A block-structured model is attractive when its guaranteed execution properties answer the question and its restrictions are acceptable. Declarative constraints can be better for flexible work, but need meaningful activation and joint interpretation. A local fragment can be enough for a bounded question without supporting a global model. An object-centric representation is warranted when relevant interaction would otherwise be lost. A readable map may be enough for communication even though it does not support execution. [EPM-S007; EPM-S011; EPM-S013; EPM-S041; EPM-S042; EPM-S049]

Some apparently desirable combinations conflict. Strict bounded-memory streaming and indefinite raw-history replay cannot both be assumed without a separate, authorised storage arrangement. Maximum relational detail can undermine privacy. A rapidly adaptive descriptive model cannot silently serve as a stable normative reference. A fully expressive object model may not support the same efficient guarantees as a restricted construction. An intervention policy can improve a modelled objective while disadvantaging other cases sharing the resource. The system preserves these as selection conditions and unresolved obligations rather than resolving them with the word “balance”. [EPM-S017; EPM-S027; EPM-S033; EPM-S034; EPM-S043; EPM-S044]

### Smallest coherent form and richer triggers

A minimal process-mining inquiry needs a real question, interpretable event evidence, a justified case/object or trace unit, one explicit process relation or reference, a relevant validity check and a consumer who can use the bounded result. It needs enough custody to investigate a material conclusion. It does not require an enterprise platform, an executable whole-process model, a predictive model, streaming or a new organisational role. The same person can legitimately perform several functions where authority, competence and challenge remain adequate.

Richer forms are triggered by additional consequential distinctions. Shared-event distortion motivates object-aware relations. Ambiguous or high-consequence mismatch motivates alignments or multi-perspective checking. Bounded event uncertainty motivates realisation-based comparison when useful. A timely action opportunity motivates prediction or streaming. A causal redesign claim motivates an identification strategy and intervention evaluation. A cross-organisational trust boundary motivates a suitable privacy or federated configuration. Richness without such a trigger is not evidence of maturity.

### Self-revision and continuity

The established literature supports revising models and responding to change. It does not supply a general right for the analysis to rewrite its own external obligations. In this composition, revision has a trigger, an object, an actor and a continuity condition. Source reinterpretation changes derived evidence and its dependent claims. Model repair changes a description under its declared purpose. Authorised rule revision changes an intended reference through the appropriate external decision. Policy changes create a new evaluation regime. Retirement removes a mechanism whose protected function or consumer no longer warrants it.

Self-application is consequently limited. A mining analysis may examine its own recorded analytical activity, but that new log would need the same event, selection and authority analysis as any other. There is no source-grounded exemption by which an analysis certifies its own assumptions or grants itself operative powers. This is a boundary of the synthesis, not a claim that reflexive analysis is impossible.

### Adversarial result of the composition tests

The analytical probes exercise favourable, non-trigger, conflict, changed-assumption and failed-observation cases. They show that the proposed distinctions have consequences: the system must refuse specific stronger claims, select cheaper branches, reopen invalidated evaluation or preserve unresolved alternatives. They do not measure productivity, human comprehension, error rates or institutional effectiveness. The complete composed system remains an argued research synthesis whose practical value would need prospective testing in an independently specified setting.


### Relational model: complete relation index

The formal direction is **FROM RELATION_TYPE TO**. A `REQUIRES` edge is guarded: it does not require an absent analysis branch to be created. Alternative relations do not assert universal interchangeability. Full assumptions, costs, sources and unresolved obligations resolve by ID in [COMPOSITION_MODEL.json](EVOLVED_PROCESS_MINING_COMPOSITION_MODEL.json). All 70 relations are analytical composition judgements grounded in component research, not independently measured effects of this whole architecture.

| Relation | From → type → to | Guard and mechanism |
| --- | --- | --- |
| EPM-R001 | EPM-003 → REQUIRES → EPM-001, EPM-002 | Extraction supports a claim about recorded work. Source trace-back and tested event meanings make a join/filter result interpretable rather than merely repeatable. |
| EPM-R002 | EPM-004, EPM-005, EPM-006 → CONSTRAINS → EPM-019, EPM-032, EPM-046 | The receiving analysis depends on label, lifecycle or order semantics. The allowable downstream claim is bounded by the abstraction and temporal evidence supplied. |
| EPM-R003 | EPM-007 → FEEDBACK_TO → EPM-001, EPM-003, EPM-008 | A suspected quality defect changes a material conclusion. Repair investigation returns to source semantics and population selection rather than only improving model fit. |
| EPM-R004 | EPM-009, EPM-076 → CONSTRAINS → EPM-002, EPM-003, EPM-013, EPM-069 | Data retention or linkage creates material disclosure risk. Preserve enough evidence for the question while limiting collection and release under a stated privacy model. |
| EPM-R005 | EPM-011 → ENABLES → EPM-003, EPM-013, EPM-069 | Data cross formats, tools or organisations. Versioned interchange carries required fields and relations; explicit mappings expose losses. |
| EPM-R006 | EPM-010 → CONFLICTS_WITH → EPM-001, EPM-003, EPM-074 | Syntactic validity is promoted into process truth. Reject the promotion while preserving syntax checks as limited technical evidence. |
| EPM-R007 | EPM-012 → REQUIRES → EPM-001, EPM-003, EPM-008 | Several case notions are plausible. Case selection is grounded in event relationships and the target unit rather than a convenient key. |
| EPM-R008 | EPM-014 → CONSTRAINS → EPM-012, EPM-026, EPM-046, EPM-048 | A relational/object log is flattened. Cardinality and shared-event checks identify duplicated work and spurious timing or succession. |
| EPM-R009 | EPM-013 → ENABLES → EPM-015, EPM-048 | Object interaction is consequential and identities are meaningful. Typed participation and relation history support object-aware models and performance questions. |
| EPM-R010 | EPM-016 → CONSTRAINS → EPM-013, EPM-015, EPM-024, EPM-030 | Richer representation is being considered. Select expressiveness according to decision value and validation/computation burden. |
| EPM-R011 | EPM-017 → SHARES_ANCESTRY_WITH → EPM-004 | Activity refinement is encountered in both event-data and case/object analysis. Resolve the duplicate to the same abstraction mechanism without deleting its candidate history. |
| EPM-R012 | EPM-018 → CONFLICTS_WITH → EPM-012, EPM-016 | Object-centricity is proposed without a relevant interaction or adequate source semantics. Reject the universal requirement and retain conditional representational selection. |
| EPM-R013 | EPM-019 → REQUIRES → EPM-001, EPM-004, EPM-006, EPM-008, EPM-012 | Discovery output is interpreted as process evidence. The inference binds to the input’s event vocabulary, ordering, population and case/object unit. |
| EPM-R014 | EPM-021 → ALTERNATIVE_TO → EPM-022, EPM-023, EPM-024, EPM-025, EPM-030 | The chosen model class and task permit a meaningful comparison. Heuristic discovery is one guarded choice alongside structured, region-based, declarative, evolutionary or local methods. Select among branches only where each can answer the actual question; this relation does not assert universal semantic interchangeability. |
| EPM-R015 | EPM-019, EPM-021, EPM-022, EPM-023, EPM-024, EPM-025 → SUPERSEDES → EPM-020 | An unrestricted alpha default is proposed for heterogeneous logs. Replace the default-selection practice with explicit bias and guarded alternatives; original alpha remains a scoped baseline. |
| EPM-R016 | EPM-024 → REQUIRES → EPM-028, EPM-031 | Mined declarative constraints are interpreted as necessary or obligatory. Activation-aware descriptive evidence is kept distinct from structural necessity and reference authority. |
| EPM-R017 | EPM-027 → CONSTRAINS → EPM-004, EPM-021, EPM-026, EPM-057 | Filtering, simplification or forgetting can remove material rare behaviour. Retain a relevant exception view or bound the conclusion rather than treating low frequency as irrelevance. |
| EPM-R018 | EPM-029, EPM-071 → FEEDBACK_TO → EPM-001, EPM-004, EPM-012, EPM-019 | Participants reveal missing context or a plausible alternative interpretation. Domain evidence can revise the input meaning or model hypothesis; source attribution prevents it from becoming silently mined fact. |
| EPM-R019 | EPM-028 → CONSTRAINS → EPM-019, EPM-031, EPM-064 | Several processes or causal structures fit the observed data. Keep observational support separate from uniqueness, normative force and interventional effect. |
| EPM-R020 | EPM-030 → CONSTRAINS → EPM-084 | Local fragments are passed to an end-to-end consumer. Carry fragment boundaries and unresolved shared-event/interaction obligations; do not infer whole-process validity from local success. |
| EPM-R021 | EPM-032, EPM-033, EPM-034, EPM-035 → REQUIRES → EPM-031 | A model comparison is performed. The reference’s meaning, scope and origin determine what any resulting mismatch establishes. |
| EPM-R022 | EPM-032 → ALTERNATIVE_TO → EPM-033 | Replay diagnostics adequately answer the question at lower cost. Choose bounded replay rather than an exact alignment; use alignment when competing explanations or global optimality under stated costs matter. |
| EPM-R023 | EPM-034 → REFINES → EPM-033 | Data/resource/time constraints materially affect mismatch. Joint multi-perspective comparison changes the diagnostic search rather than bolting attributes onto a control-flow-first verdict. |
| EPM-R024 | EPM-035 → REFINES → EPM-033 | Event uncertainty is represented by defensible alternatives. Compare costs over admitted realisations to distinguish robust from interpretation-dependent mismatch. |
| EPM-R025 | EPM-032, EPM-033, EPM-034, EPM-035 → PROVIDES_EVIDENCE_FOR → EPM-036 | A comparison identifies a consequential mismatch. Diagnostics produce discriminating questions about data, model, execution and exceptions, not a final fault assignment. |
| EPM-R026 | EPM-036 → COMMUNICATES_TO → EPM-038, EPM-053, EPM-071 | A mismatch has an operational or reference consequence. Transfer competing explanations and traceable examples to participants and actors able to choose a remedy. |
| EPM-R027 | EPM-037 → CONFLICTS_WITH → EPM-031, EPM-036, EPM-077 | Conformance is asserted to establish legality, fairness or desirability. Reject the sufficiency claim and keep normative evaluation external and explicit. |
| EPM-R028 | EPM-038 → FEEDBACK_TO → EPM-003, EPM-019, EPM-031, EPM-054 | A cause supports correction of data, description or an authorised reference. Route the revision to the object actually shown deficient and preserve the identity of prior states where comparison matters. |
| EPM-R029 | EPM-039 → CONSTRAINS → EPM-019, EPM-038 | Models are selected or repaired for a defined purpose. Independent quality questions prevent a fitness-improving change from being accepted as overall improvement without considering relevant losses. |
| EPM-R030 | EPM-040, EPM-041, EPM-042 → REFINES → EPM-039 | Precision, unseen behaviour and human use matter to the decision. Apply measure-specific semantics, representativeness and consumer-relative simplicity rather than one universal scoring package. |
| EPM-R031 | EPM-043 → REQUIRES → EPM-008, EPM-054, EPM-069, EPM-072 | An empirical ranking or predictive claim is exported. Population, temporal identity, repeatable computation and dependence accounting establish what the comparison can support. |
| EPM-R032 | EPM-044, EPM-045 → CONFLICTS_WITH → EPM-039, EPM-040, EPM-041, EPM-042 | Aggregate quality or perfect fitness is used as sufficient validity. Reject shortcut sufficiency, retaining task-specific utility and fitness as narrower constructs. |
| EPM-R033 | EPM-046 → REQUIRES → EPM-001, EPM-005, EPM-006, EPM-008 | Timing is interpreted beyond recorded milestone differences. Lifecycle, order and population assumptions define the observed interval and its permissible attribution. |
| EPM-R034 | EPM-047 → REQUIRES → EPM-046, EPM-048, EPM-071 | A delay pattern is proposed as a redesign target. Operational context and participant challenge test whether the observed location supports the proposed explanation. |
| EPM-R035 | EPM-049 → CONSTRAINS → EPM-050, EPM-051, EPM-077 | Resource data are used for social or personal comparison. Restrict the unit of attribution to verified account/person/role semantics. |
| EPM-R036 | EPM-048, EPM-051 → CONSTRAINS → EPM-047, EPM-052, EPM-063 | Shared resources, case mix or different contexts affect the decision. Check contextual comparability and interference before assigning cause or allocating resources. |
| EPM-R037 | EPM-052 → PROVIDES_EVIDENCE_FOR → EPM-064, EPM-065 | A simulation explores a specified intervention. Provide conditional scenario evidence, not observed causal success; its assumptions become explicit obligations for a pilot. |
| EPM-R038 | EPM-053 → ACTS_THROUGH → EPM-065, EPM-071 | A finding can inform a legitimate real-world decision. The analyst communicates evidence; participants interpret it; an authorised capable actor decides and acts. Mining itself does not mutate the organisation. |
| EPM-R039 | EPM-054 → ENABLES → EPM-055, EPM-057, EPM-061, EPM-066 | Results span time or model/policy revisions. Temporal identity makes drift, prospective evaluation and post-intervention reassessment interpretable. |
| EPM-R040 | EPM-055 → PROVIDES_EVIDENCE_FOR → EPM-056 | A detector alarms. Treat the alarm as a changed-feature observation; investigate instrumentation and process alternatives. |
| EPM-R041 | EPM-056 → FEEDBACK_TO → EPM-001, EPM-003, EPM-019, EPM-054 | The change explanation is supported or remains ambiguous. Revisit source semantics, extraction or the model according to the actual cause rather than automatically retraining everything. |
| EPM-R042 | EPM-057 → CONSTRAINS → EPM-069 | Near-real-time processing cannot retain all history. Bounded streaming state limits what raw history can later be replayed. Preserve algorithm/settings and enough state/provenance to explain the declared result; disclose exact-reproduction limits rather than treating streaming as a substitute for reproducibility. |
| EPM-R043 | EPM-058 → CONSTRAINS → EPM-038, EPM-055, EPM-057, EPM-066 | Adaptation could affect intended or authorised behaviour. Keep descriptive updates and normative reference changes on separate, explicitly linked revision paths. |
| EPM-R044 | EPM-059 → CONFLICTS_WITH → EPM-031, EPM-058 | Detected behaviour change is proposed as an automatic new obligation. Refuse the authority inference; permit only separately authorised adaptive policies within stated bounds. |
| EPM-R045 | EPM-060 → REQUIRES → EPM-001, EPM-003, EPM-005, EPM-054 | A prospective prediction is evaluated. Feature meaning and availability are reconstructed at the actual decision time, not from final case rows. |
| EPM-R046 | EPM-061 → CONSTRAINS → EPM-063, EPM-067, EPM-068 | Predictive performance is used to justify selection or action. Keep case/prefix dependence, future information and censoring out of unsupported comparisons. |
| EPM-R047 | EPM-062 → CONSTRAINS → EPM-063, EPM-065 | Uncertainty affects action selection. Translate calibration/coverage into a usable decision or abstention signal without claiming individual certainty or unconditional drift robustness. |
| EPM-R048 | EPM-063 → REQUIRES → EPM-053, EPM-065 | A score is claimed to be operationally useful. There must be a recipient, feasible timely response and resource-aware decision objective. |
| EPM-R049 | EPM-064 → CONSTRAINS → EPM-052, EPM-063, EPM-065 | A recommendation asserts an improvement from intervention. Require an identification argument or label the effect as a hypothesis; predictive association is not enough. |
| EPM-R050 | EPM-065 → ACTS_THROUGH → EPM-053 | Advice is accepted and an authorised actor has capacity. Real actions change cases, resources or policies outside the analytical representation; record what was actually done and by whom. |
| EPM-R051 | EPM-066 → FEEDBACK_TO → EPM-054, EPM-060, EPM-061, EPM-062, EPM-064 | Recommendations or policies alter the data-generating regime. Renew evaluation of inputs, predictive reliability and causal effects after feedback; retain old evidence as historical, not current certification. |
| EPM-R052 | EPM-067 → CONFLICTS_WITH → EPM-043, EPM-061, EPM-063 | Novel or deep architecture is asserted to be universally superior. Reject architecture-as-evidence and require task-specific comparisons including cost and timing. |
| EPM-R053 | EPM-068 → CONSTRAINS → EPM-065, EPM-084 | A local prescription method is transferred as general deployed benefit. Export the unresolved transfer obligation, preserving narrower formal and simulated evidence. |
| EPM-R054 | EPM-069 → ENABLES → EPM-070, EPM-071, EPM-074 | A result is reviewed or challenged. Executable custody and traceable outputs make sensitivity tests and participant challenge possible. |
| EPM-R055 | EPM-070 → PROVIDES_EVIDENCE_FOR → EPM-028, EPM-039, EPM-074 | Plausible analytical alternatives are tested. Reveals which findings depend on arbitrary choices without treating stability as truth. |
| EPM-R056 | EPM-072 → CONSTRAINS → EPM-041, EPM-068, EPM-079, EPM-083 | Evidence breadth or external validity is inferred. Count shared datasets and programmes honestly; multiple methods on one log are not independent organisational replications. |
| EPM-R057 | EPM-073 → CONFLICTS_WITH → EPM-053, EPM-069, EPM-074 | Artefact possession substitutes for valid inquiry and a consumer. Strip dashboard-as-proof while preserving functional tools and useful communication. |
| EPM-R058 | EPM-074 → CONSTRAINS → EPM-069, EPM-071, EPM-084 | Custody or agreement is promoted into substantive correctness. Use auditability and participation as evidence-enabling mechanisms, not automatic validators. |
| EPM-R059 | EPM-075 → CONSTRAINS → EPM-009, EPM-015, EPM-025, EPM-033, EPM-052, EPM-057, EPM-065, EPM-078, EPM-079 | Expected value or adequate evidence is absent or disappears. Permit omission, simpler methods, suspended inference and retirement instead of mandatory machinery. |
| EPM-R060 | EPM-076 → CONSTRAINS → EPM-049, EPM-050, EPM-069, EPM-078, EPM-079, EPM-081 | Identity, linked data or text cross a sensitive boundary. Match collection/processing/release to a threat model and preserve analytical utility limits. |
| EPM-R061 | EPM-077 → CONSTRAINS → EPM-050, EPM-051, EPM-063, EPM-065 | People or groups are affected by a mining-based decision. Provide bounded, contestable interpretation and accountable use rather than automatic personal ranking. |
| EPM-R062 | EPM-078 → REQUIRES → EPM-011, EPM-076 | A joint inquiry cannot centralise raw data but compatible local semantics are available. Joint discovery requires compatible event/case/activity meanings and an explicit privacy/processing/release boundary. Federation may replace central raw-data transfer in a configuration, but it does not replace semantic interoperability or proportionate collection. |
| EPM-R063 | EPM-079 → ENABLES → EPM-029, EPM-081 | Generated assistance can be checked and reduce a real burden. Use bounded language generation to propose interpretations or extracted records, with source and execution checking. |
| EPM-R064 | EPM-080 → CONFLICTS_WITH → EPM-031, EPM-053, EPM-065, EPM-077, EPM-084 | Model competence is used to claim operative authority. Block the promotion from evidence to permission and preserve the external actor/capability/consequence distinctions. |
| EPM-R065 | EPM-081 → REQUIRES → EPM-001, EPM-002, EPM-003, EPM-006, EPM-007 | Narrative-derived events are used as structured evidence. Carry text spans and extraction hypotheses into event-data validation rather than treating generated OCEL as directly observed truth. |
| EPM-R066 | EPM-082 → CONSTRAINS → EPM-015, EPM-035, EPM-084 | Uncertain events and object/identity semantics are combined. Require compatibility and external validation rather than assuming component theorems compose automatically. |
| EPM-R067 | EPM-083 → CONFLICTS_WITH → EPM-053, EPM-072, EPM-075 | Selected useful cases are presented as guaranteed economic return. Reject universality and retain local value/cost assessment and negative outcomes. |
| EPM-R068 | EPM-084 → REQUIRES → EPM-001, EPM-008, EPM-019, EPM-031, EPM-054, EPM-074 | A claim crosses a method, representation, actor or temporal boundary. Each listed prerequisite applies to the corresponding dependency actually used: event meaning, population, discovered-model semantics, reference semantics, temporal validity or custody. An absent model/reference is explicitly non-applicable, not a requirement to create one. Carry the material unit, interpretation, scope, formal semantics, authority status and validity conditions; the receiver checks compatibility. |
| EPM-R069 | EPM-084 → CONSTRAINS → EPM-015, EPM-033, EPM-046, EPM-063, EPM-065, EPM-079 | The receiver would strengthen or alter an upstream claim. Block silent promotion from syntax to truth, fit to cause, description to authority or prediction to achieved effect; ask for evidence, narrow or stop. |
| EPM-R070 | EPM-001, EPM-008, EPM-012, EPM-019, EPM-031, EPM-054, EPM-064 → FEEDBACK_TO → EPM-084 | A material upstream assumption is revised. Identify dependent conclusions and mark their prior validity as historical or unresolved until compatible evidence is restored. |

### Alternative configurations

**EPM-A01 — Minimal descriptive process inquiry.** One tested case notion and a narrow question about recorded process relations suffice. A question, interpretable events, one explicit process relation/model or constraint, a relevant validation check and a receiving use. A generic aggregate query with no process relation is an alternative method, not relabelled as a full mining system. **Omit:** No mandatory object-centric executable model, alignment, prediction, streaming, simulator or new institution. **Retire:** Consumer disappears or a simpler non-mining inquiry sufficiently answers the question.

**EPM-A02 — Independent-reference conformance.** A meaningful reference and relevant mismatch question exist. Reference origin/authority, compatible events, least costly adequate comparison and plural deviation interpretation. **Omit:** Discovery can be absent because the model may be externally supplied. **Retire:** Reference or decision ceases to apply; do not maintain a checker merely for ceremony.

**EPM-A03 — Object-aware diagnosis.** Shared/interacting objects materially change the question and identity evidence is adequate. Typed event/object evidence, explicit model semantics and flattening checks. Executable nets require separate model obligations. **Omit:** Predictive, causal and normative claims are not automatically included. **Retire:** A simpler projection is adequate or identity/interpretation cost defeats the purpose.

**EPM-A04 — Online descriptive/diagnostic support.** A real timely decision or resource limit justifies stream processing. Window/forgetting and prefix semantics; investigated alarms; versioned descriptive and reference identities. **Omit:** No automatic normative updating merely because observations change. **Retire:** Latency has no consequential consumer or alert/retention costs dominate.

**EPM-A05 — Predictive human decision support.** Valid decision-time inputs and useful feasible responses exist. Leakage/censoring-aware evaluation, uncertainty where useful, resource/timing context and accountable recipient. **Omit:** Prediction alone does not include a causal improvement claim or authority to execute advice. **Retire:** No useful action window, invalidated evaluation or simpler adequate baseline.

**EPM-A06 — Conditional interventional evaluation.** An action is feasible and authorised and its effect can be credibly identified or explicitly tested. Intervention/target/comparison, causal assumptions, actual action/outcome measurement and feedback-sensitive evaluation. **Omit:** No automatic claim of general deployed benefit; EPM-068 remains unresolved. **Retire:** Effect evidence fails, harms/costs dominate, or valid evaluation is no longer feasible.

**EPM-A07 — No mining or bounded alternative.** Event semantics, purpose, consumer or proportionality fails, or a simpler method dominates. A stated evidence/value reason and a reconsideration condition; alternatives can include queries, interviews or direct observation. **Omit:** No obligation to manufacture a process model or data collection programme. **Retire:** This is itself a terminal disposition, reopened only by a changed question or evidence.

### Analytical composition probes

These are invented or explicitly adapted reasoning probes, not new empirical validation. Published cases are separately identified in the source/evidence table. Expected dispositions were checked for logical consistency with the property and relation records; no live mining or organisational trial is implied.

**EPM-PROBE01 — Changing case identifier changes apparent repetition (CHANGED_ASSUMPTION).** One order has two items. A single shared approval event concerns both; each item has one packing event. Item projection copies approval into two traces; order projection has one approval and two packing events. **Required disposition:** Distinguish event identity from trace occurrence count; report the selected unit and preserve the source relation. **Why it discriminates:** The source events have not changed. Calling two projected approval occurrences two approval executions is false under the stipulated setup. **Limit:** This is an invented cardinality probe, not a measurement of a particular business.

**EPM-PROBE02 — Omitted manual check explains an apparent violation (FAILED_OBSERVATION).** The reference requires a manual check before payment, but the logging system never records manual checks. A trace contains payment without check. **Required disposition:** Retain log/model mismatch; do not infer that the worker skipped the check. Seek external evidence or report unresolved execution. **Why it discriminates:** Both performed-but-unlogged and omitted-work worlds produce the same observed trace. **Limit:** No claim about any real deployment; demonstrates underdetermination under stated assumptions.

**EPM-PROBE03 — Perfect fitness in a flower model (ADVERSARIAL_COUNTEREXAMPLE).** The reference language is every finite word over the observed activity alphabet. **Required disposition:** Accept that each observed trace is admitted; reject this as sufficient process validity or useful precision. **Why it discriminates:** L is a subset of the universal trace language regardless of how informative the model is. **Limit:** This is a mathematical counterexample to sufficiency, not evidence that all high-fitness models are poor.

**EPM-PROBE04 — Instrumentation drift (CHANGED_ASSUMPTION).** A logging release splits one recorded activity into started and completed labels while the work itself is unchanged. **Required disposition:** Investigate source/version change; repair interpretation or comparison and do not automatically revise the normative process. **Why it discriminates:** The observation function changed while the stipulated work did not. **Limit:** Real changes can affect both instrumentation and work; the probe isolates one cause.

**EPM-PROBE05 — Future information masquerades as early prediction (FAILED_EVALUATION).** A final outcome code is stored in the case row and supplied to a predictor evaluated as if it predicted from the first event. **Required disposition:** Remove or temporally reconstruct the unavailable feature and repeat the prospective evaluation; old score is not evidence for the claimed task. **Why it discriminates:** The feature becomes known after the declared prediction occasion. **Limit:** Does not assert that every final-row attribute is late; availability must be established.

**EPM-PROBE06 — Recommendations change their own evaluation regime (FEEDBACK).** A policy prioritises cases predicted to be delayed; the intervention changes observed completion times and resource competition. **Required disposition:** Record the policy, action and new regime; re-evaluate predictive and interventional claims without recycling the prior benchmark. **Why it discriminates:** The distribution and action selection differ from those that generated the earlier score. **Limit:** Direction and magnitude of benefit are not stipulated or inferred.

**EPM-PROBE07 — Appropriate minimal descriptive inquiry (FAVOURABLE).** A tested single-case log answers a narrow question about whether a recorded escalation sequence occurs; one process relation and selected traces suffice. **Required disposition:** Use the small explicit process comparison, retain scope and communicate it; omit object-centric nets, prediction and continuous streaming. **Why it discriminates:** The richer methods add no decision-relevant distinction in the stipulated setting. **Limit:** A ordinary aggregate count with no process relation would be an alternative data query, not relabelled as a full mining system.

**EPM-PROBE08 — No consequential consumer (NON_TRIGGER).** A proposed dashboard has no decision, learning question or responsible recipient and requires additional personal logging. **Required disposition:** Do not collect or build it on the basis of method enthusiasm; state what concrete question would justify reconsideration. **Why it discriminates:** There is no stipulated informational or operative payoff to offset added collection cost. **Limit:** Pure methodological research can itself be a legitimate consumer; the probe explicitly excludes one.

**EPM-PROBE09 — Conformance reference conflicts with an adaptive model (INTERNAL_CONFLICT).** A learned model increasingly accepts skipping a step that remains required by an independently authorised reference. **Required disposition:** Update descriptive knowledge as warranted, retain the reference, investigate the discrepancy and use an authorised revision or process-correction route. **Why it discriminates:** Observed frequency does not alter the reference’s stipulated authority. **Limit:** Does not decide whether the rule ought to persist; that needs external judgement.

**EPM-PROBE10 — Shared account creates a false personal ranking (FAILED_INTERPRETATION).** Many employees record work through one shared account; a network metric ranks that account as a single central person. **Required disposition:** Correct the attribution unit or omit individual interpretation; invite source and participant challenge. **Why it discriminates:** The resource identifier is not one person under the setup. **Limit:** Inspired by a documented issue in S012 but the test fixture is analytical, not a new empirical result.

**EPM-PROBE11 — Private computation with revealing output (BOUNDARY_CONFLICT).** A protocol protects raw event contents but exposes case identifiers and trace lengths to a participant. **Required disposition:** State exactly what remains revealed; assess whether the threat model accepts it or choose a different protocol/no release. **Why it discriminates:** Confidential processing and confidential output are separate predicates. **Limit:** The protocol trade-off is documented in S033; the acceptance decision is an analytical hypothetical.

**EPM-PROBE12 — Sound components with incompatible identities (COMPOSITION_FAILURE).** One component treats tokens as object types; another assumes persistent individual identifiers with changing relations. Their local guarantees are both quoted as certifying the combined system. **Required disposition:** Reject the combined guarantee until a compatible translation and its obligations are established; retain the narrower component claims. **Why it discriminates:** The quantified objects and invariants differ. A shared label “object-centric” does not prove semantic compatibility. **Limit:** No claim that all such translations are impossible; broad compatibility remains researched but unresolved.

**EPM-PROBE13 — Text extraction invents an event (FRONTIER_FAILURE).** A narrative says approval might occur tomorrow; the extractor outputs a completed approval event today. **Required disposition:** Mark the record unsupported and correct or exclude it; do not let a valid OCEL serialization launder the hypothetical event into observed evidence. **Why it discriminates:** Modality and tense are part of source meaning, not cosmetic wording. **Limit:** An invented probe; no allegation that a particular named model produced this record.

**EPM-PROBE14 — Same observed language, different internal mechanism (IDENTIFIABILITY_COUNTEREXAMPLE).** Observed traces are ab and ba. One candidate executes a and b concurrently; another chooses exclusively between sequential branches ab and ba. **Required disposition:** Retain the common observable behaviour; do not claim unique internal structure without additional model restrictions or evidence. **Why it discriminates:** The candidates have the same stipulated finite trace language but different internal construction. **Limit:** This does not refute a rediscovery theorem whose admissible class excludes one candidate; the example is analytical, not a historical deployment.


## EVOLVED_PROCESS_MINING_HYBRIDISATION_AND_EXTERNAL_RELATIONS

The following are documented intersections or explicitly labelled analytical boundaries, not conclusions borrowed from an unread sibling corpus.

| External relation | Classification | Preserved boundary and evidence |
| --- | --- | --- |
| Petri nets, automata, grammars and Markov approaches | DOCUMENTED_IMPORT | Primary discovery papers explicitly use these foundations. This study does not claim to have reconstructed every original precursor document. [EPM-S002; EPM-S005; EPM-S008] |
| Database/data engineering | DOCUMENTED_IMPORT_AND_NATIVE_REFINEMENT | Relational extraction supplies event evidence; case and event semantics remain analytical choices. [EPM-S014; EPM-S024] |
| Business Process Management | DOCUMENTED_INTERSECTION | The Manifesto relates mining to process understanding and improvement. How a separate BPM corpus supplies purpose, ownership or redesign authority is a later question, not answered here. [EPM-S001; EPM-S032] |
| Workflow Management | SHARED_OBJECTS_AND_DOCUMENTED_INTERSECTION | Execution records and process models connect the fields, but enactment capability and mining evidence are not interchangeable. A later workflow corpus must establish its own operative semantics. [EPM-S003; EPM-S005; EPM-S009] |
| Statistics and machine learning | DOCUMENTED_IMPORT_OR_HYBRIDISATION | Prediction and calibration import statistical assumptions. S058 is an external primary qualification, not asserted as a direct citation ancestor of S057. [EPM-S022; EPM-S023; EPM-S057; EPM-S058] |
| Causal inference and sequential decision-making | DOCUMENTED_IMPORT_OR_HYBRIDISATION | Interventional claims require identification and policy-specific evaluation beyond prediction. [EPM-S027; EPM-S030] |
| Privacy and cryptography | DOCUMENTED_IMPORT_OR_HYBRIDISATION | Threat models, protocol leakage and output release must remain explicit. [EPM-S033; EPM-S040] |
| Large language models and text extraction | HYBRIDISATION | Generated event or process claims remain checked hypotheses; benchmarking is not operative authority. [EPM-S029; EPM-S055] |
| A self-governing autonomous organisational agent | ONLY_ANALOGOUS_WITHOUT_EXTRA_AUTHORITY | This corpus establishes no such system or right to act. A model of the organisation is not an independently authorised actor. [EPM-080; EPM-084] |


## EVOLVED_PROCESS_MINING_STRONGEST_SURVIVING_PROPERTIES

The strongest core protects the meaning and permitted use of evidence. Strong retention is not a universal measured-payoff claim. These candidates can often be supplied by a small existing mechanism rather than new infrastructure.

**EPM-001 — Meaningful event identity.** For each event class, establish what happened or was recorded, by whom or what, at which lifecycle phase, and with what relation to an actual work episode. Test a small number of material examples against source-system behaviour and domain testimony; preserve unresolved alternatives rather than inventing execution semantics. [EPM-S001; EPM-S014; EPM-S039; EPM-S045]

**EPM-002 — Source provenance and trace-back.** Retain a feasible trace-back from a consequential output through selected events, source identifiers and extraction versions. Use protected pseudonymous keys where direct identifiers are unnecessary. Record which lineage edges cannot be reconstructed. [EPM-S001; EPM-S014; EPM-S036]

**EPM-003 — Semantically justified extraction.** State extraction predicates, join cardinalities, event-to-source mappings and inclusion/exclusion rules. Check material counts and sample reconciliations against the operational sources; preserve a route back to excluded or unresolved records. [EPM-S014; EPM-S024; EPM-S045]

**EPM-005 — Lifecycle-aware event interpretation.** Identify lifecycle phases and pairing rules; separate enabled, started, suspended, resumed and completed states where actually observed. Compute service or waiting intervals only from phases whose meaning supports them, and label unobserved intervals as unknown. [EPM-S001; EPM-S039; EPM-S048; EPM-S050]

**EPM-008 — Question-relative population adequacy.** Declare the target population and observation window; distinguish cases, events, objects and decision occasions; examine inclusion, censoring, unlogged work and changes in capture. Match the strength of a conclusion to the actual observation process. [EPM-S001; EPM-S020; EPM-S022; EPM-S053]

**EPM-012 — Question-dependent case notion.** Select a case notion according to the question and unit of responsibility; test relevant alternative correlations. When one case cannot retain required object interactions, keep a relational/object-centric representation instead of forcing a convenient identifier. [EPM-S014; EPM-S035; EPM-S050]

**EPM-014 — Flattening distortion checks.** Inspect shared-event multiplicities, object-to-case cardinalities and artificial directly-follows edges before interpreting a flattened log. Compare the relevant counts or timing in the original relation structure and the flattened view. [EPM-S014; EPM-S035; EPM-S050]

**EPM-019 — Explicit discovery and representation bias.** State the model language, search space, objective, noise handling and assumptions before interpreting discovered structure. Separate properties guaranteed by construction from properties inferred from the sample and from domain claims requiring external evidence. [EPM-S002; EPM-S005; EPM-S007; EPM-S008; EPM-S011; EPM-S038]

**EPM-027 — Protection of material infrequent behaviour.** Classify low-frequency behaviour by relevance to the question before suppressing it; retain or separately analyse material exceptions and expose the effect of filtering on the conclusion. Do not require keeping every rare record in every main view. [EPM-S001; EPM-S006; EPM-S013]

**EPM-028 — Non-identifiability-aware inference.** State observational equivalence and the limits of the sampled behaviour. Where competing models make different consequential predictions, seek discriminating data or domain evidence; otherwise retain alternatives or a weaker conclusion rather than asserting unique recovery. [EPM-S002; EPM-S005; EPM-S019; EPM-S053]

**EPM-031 — Defensible reference origin and authority.** Record whether the reference is descriptive, intended, contractual, technical or otherwise externally authorised; identify its version, scope and approving actor. Limit conformance conclusions to the actual reference semantics and route normative judgements to the actor entitled to make them. [EPM-S001; EPM-S009; EPM-S010; EPM-S017]

**EPM-036 — Plural explanations of deviation.** For a consequential deviation, keep plausible data, reference, execution and exception explanations separate; gather discriminating evidence and state which alternatives remain. Match the remedy to the supported cause rather than automatically correcting the process. [EPM-S009; EPM-S017; EPM-S045; EPM-S047]

**EPM-039 — Separate model-quality dimensions.** Evaluate fitness, precision, generalisation and simplicity as distinct questions, naming each operational measure and its assumptions. Report trade-offs and missing measurements rather than compressing them into an unexplained total. [EPM-S001; EPM-S009; EPM-S018; EPM-S019]

**EPM-043 — Evaluation units and splits matched to the claim.** Match the experimental unit, split and comparison to the intended inference; isolate test information from tuning, preserve appropriate temporal availability, include meaningful baselines and account for failures/timeouts. State exactly what the dataset collection can and cannot represent. [EPM-S019; EPM-S022; EPM-S053; EPM-S056]

**EPM-046 — Elapsed time distinguished from effort.** Define each duration by its observed endpoints and lifecycle semantics; distinguish throughput, waiting, service and unobserved time. Attribute elapsed intervals only where the data and model support the attribution, and retain missing intervals as missing. [EPM-S039; EPM-S048; EPM-S050]

**EPM-049 — Verified resource identity semantics.** Establish what each resource identifier denotes and when the mapping changes; distinguish people, roles, teams, systems and accounts. Do not make individual-level claims from a coarser or ambiguous identifier. [EPM-S012; EPM-S017; EPM-S045]

**EPM-054 — Temporal identity of logs models and expectations.** Keep observation windows, event-schema versions, model versions and reference expectations distinguishable; tie a result to the regime in which its assumptions were assessed. Preserve enough prior identity to compare changes or reconstruct a past decision. [EPM-S037; EPM-S021; EPM-S034]

**EPM-056 — Instrumentation change distinguished from process change.** On an apparent drift, compare instrumentation, extraction, population and process explanations; inspect the change history and selected raw examples. Revise the process hypothesis only after distinguishing or explicitly retaining these alternatives. [EPM-S021; EPM-S039; EPM-S045]

**EPM-058 — Adaptive description separated from stable obligations.** Maintain a distinction between the model describing recent behaviour and any stable or separately authorised reference. Compare them, diagnose change and obtain the relevant decision before amending obligations; adaptation of description is not self-authorising revision. [EPM-S037; EPM-S047; EPM-S017]

**EPM-060 — Prediction-time information availability.** Define the prediction occasion and information available at that moment, including attribute update histories and cross-case state. Construct features and labels accordingly; keep post-outcome or future-derived information outside the predictor and its tuning. [EPM-S022; EPM-S023]

**EPM-061 — Leakage- and censoring-aware predictive evaluation.** Split at the unit and time boundary appropriate to the deployment claim; ensure training outcomes were available then, keep dependent prefixes together where required, and disclose censoring, length restrictions and exclusions. Report performance by meaningful decision horizon and compare an adequate simple baseline. [EPM-S022; EPM-S023]

**EPM-064 — Causal identification before interventional claims.** Define the intervention, outcome and comparison; state the identification assumptions and assess confounding, treatment availability, temporal order and support. Use experimental or suitably justified causal evidence for interventional claims, and otherwise present recommendations as hypotheses requiring evaluation. [EPM-S027; EPM-S030]

**EPM-066 — Evaluation renewal after intervention feedback.** Record when recommendations or interventions alter exposure, action selection or outcomes; reassess predictive, calibration and causal claims against the new regime. Preserve the prior evaluation as historical evidence and explicitly test the revised policy or narrow its use. [EPM-S027; EPM-S030; EPM-S037]

**EPM-069 — Reproducible executable analysis.** Preserve the executable transformation/analysis recipe, relevant data identity, parameters, tool and dependency versions, random seeds and excluded or failed runs. Where raw data cannot be shared, expose the limitation and provide lawful substitutes that support only their stated claims. [EPM-S036; EPM-S019; EPM-S056]

**EPM-070 — Robustness to plausible analytical alternatives.** Vary plausible consequential analytical choices and identify which findings survive; treat changed conclusions as evidence about assumption sensitivity rather than selecting the preferred run. Include simple baselines and report computational failures. [EPM-S019; EPM-S020; EPM-S053; EPM-S056]

**EPM-072 — Dependence-aware evidence accounting.** Record shared datasets, sites, experimental generators, author programmes and repeated cases; distinguish sample size within one study from independent replication. Preserve materially different versions without counting them as new field settings. [EPM-S019; EPM-S021; EPM-S023; EPM-S056]

**EPM-074 — Auditability distinguished from correctness.** Separate traceability and computational reproducibility from semantic, population, model and causal validity. Use auditability to expose assumptions and reproduce a challenge, not as a replacement for evidence about them. [EPM-S014; EPM-S016; EPM-S056]

**EPM-075 — Non-use and retirement when mining has no adequate purpose.** Permit non-use, narrowed use and retirement when the data cannot support the question, the result cannot affect a legitimate decision, or the harm/cost exceeds its plausible value. State what evidence or changed condition would justify reconsideration. [EPM-S001; EPM-S016; EPM-S017]

EPM-084 is retained in evolved form rather than presented as a proved universal theorem: it is the new connection-level mechanism that makes this conditional core cohere. Its minimal form and cost still require application-specific testing.

## EVOLVED_PROCESS_MINING_CONTEXT_SPECIFIC_PROPERTIES

The remaining crosswalk-worthy methods are genuine capabilities whose trigger, data/model assumptions or costs prevent an unconditional obligation. A relevant property can be already addressed, inapplicable, supplied more cheaply or unsupported by the target’s evidence.

| ID | Disposition | Trigger | Cheaper adequate path |
| --- | --- | --- | --- |
| EPM-004 | RETAINED_IN_EVOLVED_FORM | Raw logs are too fine, labels combine distinct tasks, or analysis must cross systems with different granularity. | Use the native activity labels when they already answer the question. A small manually checked mapping can dominate an automated abstraction model. |
| EPM-006 | ASSUMPTION_SENSITIVE | Timestamp ties, mixed granularity, asynchronous systems, uncertain timestamps or consequential order-sensitive findings. | Ignore order for an order-insensitive question, or flag the few ambiguous pairs instead of enumerating every possible trace. |
| EPM-007 | RETAINED_IN_EVOLVED_FORM | Detected defects materially threaten the stated question, not merely because a quality metric is nonzero. | Annotate an isolated uncertain record, narrow a claim, or tolerate a known harmless defect rather than rebuild the whole log. |
| EPM-009 | CONTEXT_DEPENDENT | Proposed new instrumentation, richer identity attributes, prolonged retention or cross-organisational linkage. | Use an existing coarse extract, a small sample, aggregates or no mining if they sufficiently answer the question. |
| EPM-011 | RETAINED_IN_EVOLVED_FORM | An analysis crosses tool, organisation, version or serialization boundaries. | A simple documented table is adequate within a bounded analysis where no interchange requires a larger standard. |
| EPM-013 | RETAINED_IN_EVOLVED_FORM | Interaction itself is needed to answer the question, including synchronisation, multi-object waiting or cross-case dependencies. | A relational join or explicit shared-event table may be enough; an executable object-centric net is not mandatory. |
| EPM-015 | ASSUMPTION_SENSITIVE | The consumer needs executable or formally analysable object interactions rather than a descriptive relation map. | Use an object-centric directly-follows view or a relational diagnostic when sound executable behaviour is not required. |
| EPM-016 | CONTEXT_DEPENDENT | Choice between case-centric, object-centric, declarative, local, high-level or executable representations. | Retain a tested existing view when added expressiveness would not change a decision. |
| EPM-021 | CONTEXT_DEPENDENT | Noisy event logs where frequent behaviour is the object of analysis and approximate discovery is acceptable. | A transparent frequency table or unfiltered directly-follows graph may be enough for a descriptive question. |
| EPM-022 | ASSUMPTION_SENSITIVE | A sound executable model is needed and a block-structured model is an acceptable abstraction. | Use a relation map or selected constraints when executable semantics add no useful distinction. |
| EPM-023 | DOMAIN_SPECIFIC | The process question benefits from a Petri-net representation and the available computational budget permits region/ILP search. | A simpler structured or heuristic miner is adequate when it preserves the relevant behaviour at lower cost. |
| EPM-024 | ASSUMPTION_SENSITIVE | Flexible or knowledge-intensive processes where a small set of behavioural restrictions is more informative than a procedural model. | A few manually specified, authorised constraints can be sufficient; mining a complete template universe is unnecessary. |
| EPM-025 | CONTEXT_DEPENDENT | The search objective captures the needed behaviour and additional computation can plausibly improve a consequential model. | A deterministic structured or heuristic method may dominate when it already supplies an adequate result. |
| EPM-026 | CONTEXT_DEPENDENT | The full view is too dense for a specified diagnostic or communication task. | Filter a small relevant segment, annotate a few events or use a table rather than adopting a large map-building ritual. |
| EPM-029 | CONTEXT_DEPENDENT | Multiple plausible interpretations, incomprehensible models, unlogged activities or known policies materially affect the inquiry. | A focused conversation about one ambiguous event class may suffice; a standing modelling committee is unnecessary. |
| EPM-030 | CONTEXT_DEPENDENT | A local pattern or sub-process answers the question more economically than a full end-to-end model. | Analyse the relevant event subset or a single constraint without promising whole-process reconstruction. |
| EPM-032 | CONTEXT_DEPENDENT | A Petri-net-style reference and log permit useful low-cost replay diagnostics. | For a simple precedence rule, a direct trace check may be clearer and cheaper than a replay engine. |
| EPM-033 | ASSUMPTION_SENSITIVE | The mismatch needs a principled comparison against executable model behaviour and the computational cost is justified. | Use a simple constraint check or replay when it answers the question with acceptable ambiguity. |
| EPM-034 | ASSUMPTION_SENSITIVE | A consequential rule depends on more than activity sequence, such as a data guard or resource condition. | Use a single-perspective check for a genuinely single-perspective question; do not add attributes merely because they are available. |
| EPM-035 | ASSUMPTION_SENSITIVE | Material uncertainty is bounded well enough to express meaningful alternatives and conformance remains decision-relevant. | Flag a local ambiguity or withhold the affected judgement when full realisation analysis would not change a decision. |
| EPM-038 | RETAINED_IN_EVOLVED_FORM | Confirmed mismatch reveals an inadequate descriptive model or a legitimately approved change in intended behaviour. | Correct one extraction rule or annotate one justified exception when this closes the issue; rediscovery is not obligatory. |
| EPM-040 | USEFUL_BUT_EASILY_GAMED | Precision influences model choice, claimed superiority or the rejection of a permissive model. | For an obvious flower model or simple local question, an explicit behavioural counterexample may be clearer than a fragile aggregate metric. |
| EPM-041 | ASSUMPTION_SENSITIVE | A model will be used beyond the observed cases or is claimed to recover a generating process. | Restrict the model to descriptive use when unseen-behaviour inference is not needed; use a simple estimate if a richer estimator has no demonstrated advantage. |
| EPM-042 | CONTEXT_DEPENDENT | A model must support human reasoning, communication, maintenance or an operational decision. | A short trace, constraint or table may communicate the result better than any general process model. |
| EPM-047 | RETAINED_IN_EVOLVED_FORM | A timing pattern could lead to process redesign, escalation or attribution of responsibility. | A targeted examination of a few delayed cases may answer the question; a complete simulation or staffing model is unnecessary if the prerequisite is directly verifiable. |
| EPM-048 | CONTEXT_DEPENDENT | Observed delay depends on shared resources, priority rules, batches or multiple interacting objects. | A small load or queue stratification may suffice; a full queueing or object-centric executable model is not always needed. |
| EPM-050 | CONTEXT_DEPENDENT | The inquiry genuinely concerns organisational coordination and the log can support a relevant relation. | A process-level handoff count may be enough; do not construct a personal social network for an unrelated performance question. |
| EPM-051 | RETAINED_IN_EVOLVED_FORM | Performance comparisons across people, units, time periods, demographic groups or process variants. | Report separate descriptive distributions or refrain from ranking rather than fit an unjustified adjustment model. |
| EPM-052 | ASSUMPTION_SENSITIVE | The decision concerns a counterfactual change that cannot yet be tested directly and a model can represent its relevant mechanism. | A transparent analytical bound or small controlled pilot can dominate an elaborate simulator; no simulation is necessary for an already observable factual question. |
| EPM-053 | RETAINED_IN_EVOLVED_FORM | Mining is proposed as decision support or as an improvement programme rather than purely methodological research. | A bounded explanation or confirmation that no change is needed can be a valid result; another dashboard is not obligatory. |
| EPM-055 | ASSUMPTION_SENSITIVE | The process may change in a way that invalidates a model or decision and timely detection would matter. | A scheduled comparison of a few interpretable indicators can suffice for slow or low-consequence change. |
| EPM-057 | CONTEXT_DEPENDENT | Data volume or required latency makes bounded online processing preferable to complete batch analysis. | Periodic batch analysis with explicit windows is adequate when near-real-time decisions are unnecessary. |
| EPM-062 | ASSUMPTION_SENSITIVE | Prediction uncertainty materially affects the cost or safety of a decision and a consumer can use an uncertainty-aware output. | A conservative rule, broad interval or human review may be preferable to a complex calibration layer whose assumptions cannot be justified. |
| EPM-063 | CONTEXT_DEPENDENT | Predictions are intended to allocate attention, resources or interventions to running cases. | A simple prioritisation rule may be adequate, or no prediction is warranted if no timely action is possible. |
| EPM-065 | CONTEXT_DEPENDENT | A system offers case-level or process-level advice intended to change behaviour. | Present a small set of options or a human-reviewed hypothesis rather than automatic execution. |
| EPM-071 | RETAINED_IN_EVOLVED_FORM | Interpretation depends on unlogged context, event meaning, intended practice or consequences for participants. | One well-chosen knowledgeable participant or a small targeted check can be adequate for a narrow question; broad meetings are not mandatory. |
| EPM-076 | ASSUMPTION_SENSITIVE | Personal, commercially sensitive or linkable event data are collected, shared or analysed across trust boundaries. | Use access restriction, aggregation, a smaller lawful extract or no release when these meet the purpose more safely than elaborate transformation. |
| EPM-077 | RETAINED_IN_EVOLVED_FORM | Analysis affects individuals or groups through evaluation, resource allocation, monitoring or recommendations. | Use non-identifying process-level evidence or refrain from personal ranking when individual attribution is unnecessary. |
| EPM-078 | ASSUMPTION_SENSITIVE | A legitimate cross-organisational analysis cannot lawfully or acceptably centralise the required raw data. | Separate local analyses or a negotiated aggregate may suffice; federation is not a default for a single trusted dataset. |
| EPM-079 | CONTEXT_DEPENDENT | Language assistance can reduce a demonstrated interpretation or construction burden and checking is feasible. | A deterministic query, template or manual review may be cheaper and more reliable for a small stable task. |
| EPM-081 | ASSUMPTION_SENSITIVE | Relevant process evidence exists in text and a structured event log is unavailable or incomplete. | Manual annotation of a small corpus or a simple deterministic extraction can be adequate; full generative extraction is not mandatory. |
| EPM-084 | RETAINED_IN_EVOLVED_FORM | A finding or model crosses method, representation, actor or time-regime boundaries and the receiving claim depends on its meaning. | A short explicit qualification in the existing result or conversation may suffice. No dedicated new protocol, service, committee or form is required for every property. |


## EVOLVED_PROCESS_MINING_REJECTED_OR_SUPERSEDED_PRACTICES

**EPM-010 — Syntactic validity as sufficient process truth (REJECTED_OR_DISFAVOURED).** Reject the overclaim while preserving EPM-001, EPM-003 and EPM-011 as distinct mechanisms. Interoperability is valuable; the rejected proposition is its elevation into semantic sufficiency, not the standard itself. **What remains useful:** Keep lightweight syntax checks as prerequisites and state their limited result; no replacement bureaucracy is needed.

**EPM-017 — Activity-level refinement as a separate obligation (DUPLICATE_CANDIDATE).** Duplicate recorded, not erased or renumbered. Case identity and activity abstraction are not duplicates of each other. Only this second activity-refinement entry is merged. **What remains useful:** Reuse EPM-004 and keep the additional contextual link.

**EPM-018 — Universal superiority of object-centricity (NO_GENERAL_PROPERTY).** Reject a universal obligation while retaining the native object-centric mechanisms and their guards. Recent formal advances show conditional strengths, not economic or cognitive dominance in all settings. **What remains useful:** Use EPM-012 and EPM-016 to select the representation without an obligatory migration.

**EPM-020 — Alpha as the default general-purpose miner (SUPERSEDED_BY_STRONGER_FORM).** Replace the unrestricted-default practice with EPM-019 and guarded alternatives EPM-021 to EPM-025; preserve historical and theoretical contribution. Failure outside assumptions does not refute the original theorem. No single later miner universally replaces alpha on every objective. **What remains useful:** Alpha can remain adequate for a small didactic or controlled log within its assumptions; replacement is not mandatory merely because a method is old.

**EPM-037 — Conformance as sufficient legality or fairness (REJECTED_OR_DISFAVOURED).** Reject the overclaim and preserve EPM-031, EPM-033 and EPM-036 as distinct supporting mechanisms. Models can encode applicable rules and supply useful evidence; rejection of sufficiency does not imply that conformance is irrelevant to a compliance inquiry. **What remains useful:** Retain the narrow, useful comparison and state that further normative assessment is outside it.

**EPM-044 — Universal aggregate model-quality ranking (NO_GENERAL_PROPERTY).** Reject universality while preserving multi-dimensional assessment and task-specific choice. Aggregation is not inherently invalid. The rejected claim is universal authority and comparability, not purposeful optimisation. **What remains useful:** Use a transparent trade-off account or dominance comparison rather than forced aggregation.

**EPM-045 — Perfect fitness as sufficient validity (REJECTED_OR_DISFAVOURED).** Reject the sufficiency implication and retain fitness as one separately interpreted dimension. Perfect fitness can be a useful prerequisite in some analyses; rejection does not mean that fitting the data is undesirable. **What remains useful:** One counterexample showing indiscriminate permitted behaviour may be enough to defeat the sufficiency claim.

**EPM-059 — Automatic normative normalisation of detected drift (REJECTED_OR_DISFAVOURED).** Reject an unwarranted authority transfer, preserving conditional descriptive adaptation. The rejection must not prevent explicitly authorised adaptive policies; such policies require their own bounded decision rules and evaluation. **What remains useful:** Keep the existing reference and record a change hypothesis while the appropriate actor investigates.

**EPM-067 — Universal superiority of deep predictive models (NO_GENERAL_PROPERTY).** Reject universality while retaining learned prediction as a conditional capability. The inspected predictive benchmarks and current collaborative preprint support task-bounded comparisons, not a universal ranking of all architectures. **What remains useful:** Use a simple rule or conventional model when it meets the decision need with less cost and uncertainty.

**EPM-073 — Dashboard possession as evidence of analytical quality (CEREMONY_NOT_GENERAL_PROPERTY).** Strip the artefact-as-proof assumption while retaining functional visualisation and reproducible tools. Dashboards can be genuinely useful; the ceremonial candidate is their unconditioned presence as proof of quality. **What remains useful:** A query, table, script or focused conversation can satisfy the real analytical function.

**EPM-080 — Autonomous operative authority inferred from event logs (REJECTED_OR_DISFAVOURED).** Reject self-authorisation while retaining separately mandated operational support. Authorised automation is possible in specific settings, but it requires an independently justified scope and controls; the rejected claim is authority inferred from logs alone. **What remains useful:** Deliver a bounded analysis or reviewed recommendation without automatic mutation of work or rules.

**EPM-083 — Universal positive economic return on mining (NO_GENERAL_PROPERTY).** Reject universal economic benefit while preserving evidence of conditional analytical and organisational usefulness. The inspected RWS case reports a meaningful organisational response but no controlled post-change effect. Interviews reveal effort and obstacles without estimating a universal failure rate. **What remains useful:** A low-cost bounded inquiry or an alternative method may dominate; do not require a business case model when a small safe exploratory cost is already justified.


## EVOLVED_PROCESS_MINING_CURRENT_STATE_AND_RESEARCH_FRONTIER

As of the cut-off, the inspected frontier includes dynamic object identities and identifier-aware guarantees; richer object-centric process conceptualisation; collaborative predictive monitoring; sequential causal policy optimisation; text-derived object-centric event records; uncertainty-aware prediction; and federated analysis. These are differentiated developments. No evidence here establishes that all their assumptions are compatible, that they form one recognised methodology, or that their combination is independently validated. [EPM-S026–EPM-S028; EPM-S033; EPM-S044; EPM-S055; EPM-S057]

Dates and versions matter. S026’s nominal October 2026 issue is future relative to this cut-off; the accessible manuscript is what was inspected. S027 and S028 are exact preprint versions, with S028 under review. S054 and S055 are a conference/journal programme, not independent replications. S029 cannot certify an untested current model. S015 supplies only the official scope/metadata of the exact standard, not unseen normative text.

The research agenda that survives criticism is therefore not “make everything transparent and autonomous”. It is to improve representational compatibility, practical uncertainty handling, privacy/utility understanding, valid experiment design, causal evaluation and usable human participation while measuring their actual costs. New methods can justify more machinery, but the evidence can also justify a narrower model, a cheaper view or no mining.

## EVOLVED_PROCESS_MINING_ADVERSARIAL_SYNTHESIS_VERDICT

**Accepted conditional core.** Process mining coheres around interpretable event evidence linked to explicit process representations, scoped inference/comparison, relevant validation, a real consumer and feedback from changed assumptions or action. EPM-084 makes the connection-level validity conditions explicit. The architecture is relational, with branches, loops and legitimate stops, not a serial checklist.

**Strongest objection to unification.** Methods do not always share units, semantics or objectives. A case-centric trace, object-type token, persistent identifier, local fragment, declarative constraint and predictive feature vector cannot be assumed to express the same process. A universal unified execution model would require translations not established here. The synthesis therefore unifies the conditions of responsible inquiry and communication while preserving alternative model classes and unresolved interfaces.

**What would falsify a claimed payoff.** A selected representation may fail the consumer’s task; a result may reverse under a plausible extraction; a needed event may be unobservable; a richer method may offer no advantage over a simple baseline; a privacy mechanism may leak the protected information; or an intervention may not produce the predicted benefit after its actual costs and effects. In those cases, narrower use, substitution or retirement is the correct disposition—not declaring the adverse case “not really process mining”.

**What is not established.** This corpus does not establish universal positive return, the best miner, universal object-centric or deep-model superiority, normative correctness from conformance, causal benefit from prediction, arbitrary-drift reliability from calibration, privacy from encryption alone, or autonomous operative authority from model competence. Nor does it claim empirical validation of the full Evolved system. Strong formal component validity can coexist with weak external validity, and an informative field case can coexist with missing causal outcome evidence.

**Adversarial outcome.** The criticism changed the population: five claims rejected, four denied general-property status, one ceremony stripped, one duplicate linked, one default superseded and two broad transfer questions left unresolved. The result is not an advocacy catalogue with decorative caveats. It is a conditional system whose most important capability is sometimes to keep a useful narrow finding while refusing its unwarranted promotion.

## EVOLVED_PROCESS_MINING_OPEN_QUESTIONS_AND_EVIDENCE_LIMITS

**EPM-068 — General deployed causal benefit of prescription.** Would prospective multi-site studies with credible counterfactuals retain the estimated benefit after costs, adverse effects and human adaptation? Narrow current acceptance to bounded methods and preserve broad transfer as an examined unresolved question. The inspected corpus includes valuable causal methods but not enough independent real-deployment evidence to settle this general claim. Absence here is not proof that no such study exists anywhere.

**EPM-082 — Broad external validity of uncertain object-centric analysis.** Which uncertainty representations remain sound and useful for dynamic object identity relations at realistic scale? Preserve conditional component capabilities while withholding the universal composition claim. Different object soundness notions and uncertainty-set semantics cannot be joined by terminology alone. Current theory and demonstrations do not settle broad deployment generality.

**EPM-084’s distinct empirical burden.** The validity-preserving handoff is an argued composition invariant. A later study must determine what minimal information reliably prevents interpretation/authority/temporal overreach, whether people actually use it, and when its cost exceeds its benefit. It is not certified by the mere existence of this ledger.

**Access limits.** EPM-S003: Historical problem formulation and publication identity inspected; no omitted methods/theorems/experiments inferred. EPM-S004: Historical probabilistic/algorithmic AS-IS discovery identity only; no detailed result claims. EPM-S015: IEEE 1849-2023 exact standard identity and scope verified; full normative text not inspected and no unseen clause obligations invented. EPM-S051: 2016 second-edition monograph supplies contextual organisation; detailed mechanisms grounded in inspected primary papers, not an implied full monograph reading. EPM-S054: Conference identity and high-level contribution bounded; full 2026 journal extension S055 supplies inspected method/evaluation, not retroactively all 2025 details. Suriadi et al. event-log imperfection pattern literature: A sought full copy was inaccessible. Timestamp-quality and digital-hospital primary studies S039/S045 supply directly inspected evidence; no unseen pattern taxonomy or number is asserted. 2026 object-centric event-data imperfection lead: No detailed claims extracted from inaccessible publisher text. Current object semantics and uncertainty are covered by S026/S043/S044 and primary uncertainty/performance work. 2023 extended All That Glitters journal version: The accessible 2020 v1 S053 is preserved as a materially distinct inspected version; journal additions are not attributed to it. EPM-S055: Publisher route was unavailable; the lawful institutional PDF was inspected and supplied actual claim locators. EPM-S057: Publisher route failed; author-uploaded full text inspected. The retrospective clinical paper is research evidence, not medical advice. EPM-S026: Available manuscript and 2026 DOI inspected by the cut-off; the nominal 1 October 2026 issue date is not treated as an event already occurring or evidence of replication. EPM-S027 and EPM-S028: Exact accessible versions examined; S028 is under review and not represented as a completed peer-reviewed publication or independent field replication. EPM-S043: An ambiguity in the inspected preprint’s proof/decidability presentation prevents certifying that contested point. Only explicitly scoped model semantics are used. EPM-S048 figures: A requested figure rendering did not succeed; claims used here are grounded in readable text, not inferred from the unavailable graphic. Current conference coverage: Current research includes accessible 2025 conference and 2026 journal/preprint evidence. Future 2026 proceedings are not assumed to exist or counted as inspected.

**Empirical limits.** Field/practitioner reports, benchmarks, resamples, synthetic generators and preprints remain distinct. Negative and null deployment outcomes are difficult to retrieve and often unpublished or private; this corpus does not estimate their frequency or claim that no contrary study exists outside it. Source-table evidence units and dependence groups prevent treating repeated datasets as independent replication.

**Boundary of the freeze.** The declared scope, 84 dispositions and their sources are stable in this revision. There are no unexamined mandatory families or candidates. The unresolved questions are inside the freeze as explicit uncertainty. New evidence can warrant a later revision, but packaging does not silently alter these judgements.

**Later use.** `SIBLING_CORPORA_NOT_CONSULTED`. `CROSS_TRIFECTA_SYNTHESIS_NOT_PERFORMED`. Preserve the lineage keys, denominator, source versions, rejected candidates and evidence limits during any later reconciliation. This packet authorises no target mutation or adoption.

## Evidence bibliography and access register

Source IDs are durable within this packet. Claims above resolve to the following exact works and their inspected locators. Full empirical units and dependence notes are in [SOURCE_TABLE.json](EVOLVED_PROCESS_MINING_SOURCE_TABLE.json).

### EPM-S001 — Process Mining Manifesto

IEEE Task Force on Process Mining; W.M.P. van der Aalst and co-authors. **Date/version:** 2011; proceedings publication 2012; Official English brochure; related chapter DOI 10.1007/978-3-642-28108-2_19. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Brochure pp. 1–3: scope and three mining types; pp. 6–9: L* life-cycle and guiding principles GP1–GP6; pp. 10–14: challenges. **Inspected claim:** A community statement connects event data and explicit process models through discovery, conformance and enhancement; purpose, concurrency, event/model linkage and repeated use are guiding concerns. **Limit:** Guidance and community formulation, not comparative proof of benefit. Brochure pagination differs from the Springer chapter.

**URL/DOI:** https://www.tf-pm.org/upload/1580737614108.pdf

### EPM-S002 — Discovering Models of Software Processes from Event-Based Data

Jonathan E. Cook; Alexander L. Wolf. **Date/version:** 1998-07; Author manuscript, 35 PDF pages; TOSEM 7(3), 215–249. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Abstract and §§1–3: event-based process inference; algorithm sections: RNet, Ktail and Markov; §8: industrial software process application. **Inspected claim:** State merging, statistical and connectionist approaches addressed reconstructing software processes from event histories before the alpha formulation. **Limit:** One software-process application and constructed experiments; no claim of unique field origin or general organisational benefit.

**URL/DOI:** https://www.doc.ic.ac.uk/~alw/doc/papers/tosem0798.pdf; DOI 10.1145/287000.287001

### EPM-S003 — Mining process models from workflow logs

Rakesh Agrawal; Dimitrios Gunopulos; Frank Leymann. **Date/version:** 1998; EDBT 1998, LNCS 1377, pp. 467–483. **Access:** ABSTRACT_AND_METADATA, 2026-09-06.

**Locator:** Publisher abstract; Bibliographic information and references. **Inspected claim:** Workflow executions motivate discovering dependency graphs; the abstract reports synthetic experiments and an IBM FlowMark application. **Limit:** Abstract and bibliographic record only. No algorithmic guarantees, sample counts or effectiveness estimates extracted. First-online 2006 is not the original publication date.

**URL/DOI:** https://link.springer.com/chapter/10.1007/BFb0101003; DOI 10.1007/BFb0101003

### EPM-S004 — Automating the Discovery of AS-IS Business Process Models: Probabilistic and Algorithmic Approaches

Anindya Datta. **Date/version:** 1998-09-01; Information Systems Research 9(3), 275–301. **Access:** ABSTRACT_AND_METADATA, 2026-09-06.

**Locator:** Publisher abstract and bibliographic record. **Inspected claim:** AS-IS reconstruction for business process reengineering is framed as grammar discovery, with probabilistic and algorithmic approaches. **Limit:** Abstract-only access; reduction of modelling cost is a motivation, not an independently established causal effect.

**URL/DOI:** https://pubsonline.informs.org/doi/10.1287/isre.9.3.275; DOI 10.1287/isre.9.3.275

### EPM-S005 — Workflow Mining: Discovering Process Models from Event Logs

W.M.P. van der Aalst; A.J.M.M. Weijters; Laura Maruster. **Date/version:** 2004-09; 38-page author manuscript; published TKDE 16(9), 1128–1142. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Definitions of log relations and alpha algorithm; Rediscovery theorem and its structural/completeness assumptions; Discussion of limitations and examples. **Inspected claim:** The alpha approach connects directly-follows and parallel relations to workflow nets under explicit structural and logging conditions. **Limit:** A rediscovery result is conditional; real logs need not be complete and equal labels, short loops or non-free-choice dependencies can defeat inference.

**URL/DOI:** https://www.vdaalst.com/publications/p245.pdf; DOI 10.1109/TKDE.2004.47

### EPM-S006 — Process mining with the HeuristicsMiner algorithm

A.J.M.M. Weijters; W.M.P. van der Aalst; A.K. Alves de Medeiros. **Date/version:** 2006; BETA working paper 166, 34 pages plus repository cover. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §2: event logs and order; Dependency measures, thresholds and algorithm; Experiments and conclusions. **Inspected claim:** Frequency-sensitive dependency measures and thresholds address noisy logs and yield heuristic causal structures. **Limit:** Thresholds encode preference for common behaviour; frequency is not importance. Report experiments do not establish a universal optimal threshold.

**URL/DOI:** https://pure.tue.nl/ws/files/2388011/615595.pdf

### EPM-S007 — Discovering Block-Structured Process Models from Event Logs – A Constructive Approach

Sander J.J. Leemans; Dirk Fahland; W.M.P. van der Aalst. **Date/version:** 2013; Author manuscript; PETRI NETS 2013, pp. 311–329. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Recursive cut construction; §5 and Theorem 14: rediscovery conditions; Evaluation and limitations. **Inspected claim:** Recursive decomposition builds sound block-structured models; rediscovery depends on the specified process-tree class and log completeness. **Limit:** Soundness of the generated model is not truth of its environmental interpretation; unsupported structures may be overgeneralised.

**URL/DOI:** https://dfahland.win.tue.nl/publications/LeemansFA_2013_blockstructured.pdf; DOI 10.1007/978-3-642-38697-8_17

### EPM-S008 — Process discovery using integer linear programming

Jan Martijn E.M. van der Werf; Boudewijn F. van Dongen; Kees M. van Hee; Cor A.J. Hurkens; Alexander Serebrenik. **Date/version:** 2008; TU/e Computer Science Report 08-04; repository PDF 21 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Region/linear constraint formulation; Algorithm and experiments. **Inspected claim:** Region-based discovery uses linear constraints to construct Petri-net places consistent with specified event behaviour. **Limit:** Solver effort and objective choices constrain applicability; this five-author report is distinct from the four-author conference version.

**URL/DOI:** https://pure.tue.nl/ws/files/3092412/633716.pdf

### EPM-S009 — Conformance checking of processes based on monitoring real behavior

Anne Rozinat; W.M.P. van der Aalst. **Date/version:** 2008; online 2007; 44-page author manuscript; Information Systems 33(1), 64–95. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Fitness/replay definitions; Behavioural and structural appropriateness; Evaluation and discussion. **Inspected claim:** Token-based replay and appropriateness distinguish fitting observed traces from excessively permissive or complicated models. **Limit:** Token placement and silent/duplicate activities complicate diagnosis; aggregate fitness does not uniquely identify a real-world fault.

**URL/DOI:** https://www.vdaalst.com/publications/p436.pdf; DOI 10.1016/j.is.2007.07.001

### EPM-S010 — Conformance Checking Using Cost-Based Fitness Analysis

Arya Adriansyah; Boudewijn F. van Dongen; W.M.P. van der Aalst. **Date/version:** 2011; EDOC 2011, pp. 55–64. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §IV: deviations and moves; Cost-based alignment/search definitions; Evaluation. **Inspected claim:** Alignments seek a least-cost correspondence between trace events and model executions, permitting model and log moves. **Limit:** Optimality is relative to model, mapping, cost function and search completion. A cheapest explanation need not be a unique or causally correct explanation.

**URL/DOI:** https://www.vdaalst.com/publications/p630.pdf; DOI 10.1109/EDOC.2011.12

### EPM-S011 — Efficient Discovery of Understandable Declarative Process Models from Event Logs

Fabrizio Maria Maggi; R.P. Jagadeesh Chandra Bose; W.M.P. van der Aalst. **Date/version:** 2012; CAiSE 2012, pp. 270–285; author PDF 16 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §1: flexible processes; Constraint discovery/pruning sections; Evaluation. **Inspected claim:** Declarative discovery learns constraints rather than enumerating procedural paths, with techniques to control redundancy and understandability. **Limit:** Constraint templates restrict what can be found; satisfiability or high support need not establish a meaningful active obligation.

**URL/DOI:** https://www.vdaalst.com/publications/p669.pdf

### EPM-S012 — Discovering Social Networks from Event Logs

W.M.P. van der Aalst; Hajo A. Reijers; Minseok Song. **Date/version:** 2005; Computer Supported Cooperative Work 14, 549–593; author manuscript 43 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Metrics for handover, subcontracting, working together and similar tasks; Case study; PDF p. 33, shared user account example. **Inspected claim:** Alternative event-derived relations expose different organisational perspectives; a shared user account distorted an apparent central actor in the case. **Limit:** Logged identities and co-occurrence do not directly measure people, collaboration quality or culpability. Shared research team with other Eindhoven work; identity of field programmes must not be assumed from authorship.

**URL/DOI:** https://www.vdaalst.com/publications/p300.pdf

### EPM-S013 — Fuzzy Mining: Adaptive Process Simplification Based on Multi-perspective Metrics

Christian W. Günther; W.M.P. van der Aalst. **Date/version:** 2007; BPM 2007, pp. 328–343; author manuscript. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Significance and correlation metrics; Simplification and visualisation mechanisms; Examples. **Inspected claim:** A map-oriented view suppresses and aggregates less significant behaviour to make unstructured processes explorable. **Limit:** Readable maps may hide exceptional behaviour and do not acquire executable semantics merely by being displayed.

**URL/DOI:** https://www.vdaalst.com/publications/p400.pdf

### EPM-S014 — Extracting Event Data from Databases to Unleash Process Mining

W.M.P. van der Aalst. **Date/version:** 2015; BPM: Driving Innovation in a Digital World, pp. 105–128. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Database-to-event-log construction; Case notions and convergence/divergence examples. **Inspected claim:** Relational extraction requires event and case choices; data joins can duplicate or fragment behaviour and change the inferred process. **Limit:** Worked examples and conceptual treatment; not a validated automatic inference of database semantics.

**URL/DOI:** https://www.vdaalst.com/publications/p817.pdf

### EPM-S015 — IEEE Standard for eXtensible Event Stream (XES) for Achieving Interoperability in Event Logs and Event Streams

IEEE Standards Association. **Date/version:** 2023-09-08; IEEE 1849-2023; replaces 2016 edition. **Access:** OFFICIAL_SCOPE_AND_METADATA, 2026-09-06.

**Locator:** Official standard scope and bibliographic record. **Inspected claim:** IEEE 1849-2023 specifies an interchange grammar and extension mechanism for event logs and streams. **Limit:** Official scope/metadata inspected, not paywalled normative clauses. No claim of certification, actual adoption or semantic correctness.

**URL/DOI:** https://standards.ieee.org/ieee/1849/10907/; DOI 10.1109/IEEESTD.2023.10267858

### EPM-S016 — What makes life for process mining analysts difficult? A reflection of challenges

Lisa Zimmermann; Francesca Zerbato; Barbara Weber. **Date/version:** Online 2023-11-17; issue 2024; Software and Systems Modeling 23, 1345–1373. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: interviews and survey sampling; §4.1: 23 challenges; §4.3: mitigation strategies; Limitations. **Inspected claim:** The study analyses 41 analyst interviews and a follow-up survey with 24 eligible respondents; challenges include questions, extraction, interpretation and organisational work. **Limit:** Self-report and purposive participation, variable per-question denominators; no population failure rate. Earlier publications using the same interviews are not independent replications.

**URL/DOI:** https://link.springer.com/article/10.1007/s10270-023-01134-0; DOI 10.1007/s10270-023-01134-0

### EPM-S017 — Responsible Process Mining

Felix Mannhardt. **Date/version:** 2022; Process Mining Handbook, chapter 12. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** FACT framework; Fairness, accuracy, confidentiality and transparency sections; Examples and research challenges. **Inspected claim:** Responsible use requires separate consideration of fairness, accuracy, confidentiality and transparency; a visible model is not automatically understandable or harmless. **Limit:** Framework and illustrative examples, not a trial establishing effectiveness or legal compliance.

**URL/DOI:** https://link.springer.com/chapter/10.1007/978-3-031-08848-3_12; DOI 10.1007/978-3-031-08848-3_12

### EPM-S018 — The Imprecisions of Precision Measures in Process Mining

Niek Tax; Xixi Lu; Natalia Sidorova; Dirk Fahland; W.M.P. van der Aalst. **Date/version:** Preprint 2017; journal 2018; arXiv 1705.03303; Information Processing Letters 135, 1–8. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Proposed axioms; Counterexamples for analysed precision measures; Conclusion. **Inspected claim:** The analysed precision measures violate at least one of the proposed desirable properties. **Limit:** A critique of specified measures against proposed axioms; not a universal impossibility theorem for all precision measures or definitions.

**URL/DOI:** https://arxiv.org/pdf/1705.03303; DOI 10.1016/j.ipl.2018.01.013

### EPM-S019 — Automated Discovery of Process Models from Event Logs: Review and Benchmark

Adriano Augusto; Raffaele Conforti; Marlon Dumas; Marcello La Rosa; Fabrizio Maria Maggi; Andrea Marrella; Massimo Mecella; Allar Soo. **Date/version:** Inspected v3 2018-01-30; journal 2019; arXiv 1705.02288v3; later TKDE 31(4), 686–705. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §4: setup and metrics; Tables 3–4 log characteristics; §5: results and timeouts; §§7–8: comparisons and limitations. **Inspected claim:** Comparative evaluation covers 12 public and 12 proprietary real-life logs and nine metrics; ranking and scalability differ across dimensions. **Limit:** Logs are not 24 independent random organisations; private half is not fully reproducible. Implementation/parameter versions and three-fold evaluation limit transfer.

**URL/DOI:** https://arxiv.org/pdf/1705.02288; DOI 10.1109/TKDE.2018.2841877

### EPM-S020 — Generalization estimation in process mining: the impact of event data quality

Anandi Karunaratne; Artem Polyvyanyy; Alistair Moffat. **Date/version:** 2025-10-20; Process Science 2, article 20. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§3–4: representativeness and bootstrap reasoning; Experiments, phases 1 and 2; Discussion and data availability. **Inspected claim:** Ground-truth experiments show that representativeness changes the accuracy of generalisation estimation; an additional estimate can worsen already representative data. **Limit:** Constructed ground-truth settings, selected sizes/noise and estimator assumptions; external representativeness still needs evidence.

**URL/DOI:** https://link.springer.com/article/10.1007/s44311-025-00027-3; DOI 10.1007/s44311-025-00027-3

### EPM-S021 — An Experimental Evaluation of Process Concept Drift Detection

Jan Niklas Adams; Christopher Pitsch; Tobias Brockhoff; W.M.P. van der Aalst. **Date/version:** 2023; Proceedings of the VLDB Endowment 16; 14-page paper. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Experimental setup; Detection/localisation evaluation; Discussion and recommendations. **Inspected claim:** A common evaluation examines drift detectors across multiple drift and noise settings rather than assuming detection from one benchmark transfers. **Limit:** Synthetic drift ground truth and tested implementations constrain conclusions; schema change and authorised organisational change require external interpretation.

**URL/DOI:** https://www.vldb.org/pvldb/vol16/p1856-adams.pdf

### EPM-S022 — Creating Unbiased Public Benchmark Datasets with Data Leakage Prevention for Predictive Process Monitoring

Hans Weytjens; Jochen De Weerdt. **Date/version:** 2021 preprint; 2022 proceedings; arXiv 2107.01905; 12-page inspected manuscript. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§2–3: comparison and nine-dataset design; §§5.3–5.7: end censoring, strict temporal split and long-case exclusions; §6 and §7: predictive comparison and conclusions. **Inspected claim:** Temporal leakage and duration-related selection can distort predictive monitoring benchmarks; split design must respect the prediction-time information set. **Limit:** Same public-log families recur elsewhere. Trimming long cases changes the population; this proposal is not a universal debiasing procedure or a requirement to use its 20% split or 5% cap.

**URL/DOI:** https://arxiv.org/pdf/2107.01905

### EPM-S023 — Outcome-Oriented Predictive Process Monitoring: Review and Benchmark

Irene Teinemaa; Marlon Dumas; Marcello La Rosa; Fabrizio Maria Maggi. **Date/version:** 2017 preprint; journal 2019; ACM TKDD 13(2), article 17; inspected 59-page arXiv manuscript. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Benchmark setup and encodings; 24 tasks from nine source event logs; Evaluation and limitations. **Inspected claim:** The benchmark compares 11 methods across 24 outcome-prediction tasks drawn from nine real event logs. **Limit:** Tasks sharing logs are not independent deployments; classification quality is not an intervention effect. Encodings, prefixes and parameters condition results.

**URL/DOI:** https://arxiv.org/pdf/1707.06766; DOI 10.1145/3301300

### EPM-S024 — OCEL (Object-Centric Event Log) 2.0 Specification

Alessandro Berti; Istvan Koren; Jan Niklas Adams; Gyunam Park; Benedikt Knopp; Nina Graves; Majid Rafiei; Lukas Liß; Leah Tacke genannt Unterberg; Yisong Zhang; Christopher Schwanen; Marco Pegoraro; W.M.P. van der Aalst. **Date/version:** 2024-03-04; OCEL 2.0; arXiv 2403.01975v1. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Data model and definitions; Event/object and object/object relationships; XML, JSON and SQLite serialisations. **Inspected claim:** OCEL 2.0 represents multiple object associations, qualified relations and changing object attributes rather than forcing one case per event. **Limit:** Specification is not proof of extraction correctness, completeness or practical superiority. Version 2.0 and the 2024 explanatory publication have different dates.

**URL/DOI:** https://arxiv.org/html/2403.01975v1

### EPM-S025 — Mining Uncertain Event Data in Process Mining

Marco Pegoraro; W.M.P. van der Aalst. **Date/version:** 2019; Extended manuscript arXiv 1910.00089v1, dated 20 September 2019 in PDF. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: uncertainty taxonomy; §4: realisations; §5: conformance bounds; §6: experiments. **Inspected claim:** Set-valued event uncertainty leads to sets of possible traces and minimum/maximum conformance costs rather than arbitrary total-order repairs. **Limit:** Bounds depend on whether the uncertainty representation includes the true event possibilities; constructed experiments do not verify real logging semantics.

**URL/DOI:** https://www.vdaalst.com/publications/p1065.pdf

### EPM-S026 — Object-centric Process Management: A Research Manifesto

Anjo Seidel; Mathias Weske; Marco Montali; Andrey Rivkin; Manfred Reichert; Jan Martijn E.M. van der Werf; W.M.P. van der Aalst and co-authors. **Date/version:** 2026; accessible author manuscript before cutoff; nominal journal issue 2026-10; 26-page available author manuscript; Information Systems 141, 102728. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Introduction: independent modelling/mining developments; Conceptualisation; Research challenges and conclusion. **Inspected claim:** Object-centric modelling and mining developed with partly incompatible assumptions; the manifesto proposes common conceptual ground and research obligations. **Limit:** Community research agenda, not proof of completed unification or independent efficacy. The institutional record gives a future 1 October 2026 issue date; this packet uses the available manuscript, not future event evidence.

**URL/DOI:** https://leemans.ch/publications/papers/is2025seidl.pdf; DOI 10.1016/j.is.2026.102728

### EPM-S027 — SCOPE: Sequential Causal Optimization of Process Interventions

Jakob De Moor; Hans Weytjens; Johannes De Smedt; Jochen De Weerdt. **Date/version:** 2026-01-09; arXiv 2512.17629v3; first preprint 2025. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: sequential causal estimation and backward induction; §4: SimBank and SimBPIC17 experiments; §4.6: limitations. **Inspected claim:** Sequential intervention recommendations can account for interactions between decision points rather than treating actions independently. **Limit:** Evaluation uses synthetic/semi-synthetic processes; causal identification and simulator-to-world validity remain assumptions. No real-world randomised benefit established.

**URL/DOI:** https://arxiv.org/html/2512.17629v3

### EPM-S028 — A Framework for Object-Centric Predictive Monitoring of Collaborative Processes

Daniel Calegari; Andrea Delgado; Leonel Peña; Martín Rubio. **Date/version:** 2026-08-27; arXiv 2608.27671v1; submitted to Information Systems, under review; not a published journal result. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§3–4: mapping and task reformulation; §6: validation; §§7–8: costs and validity threats. **Inspected claim:** Typed collaborative representations support differentiated predictive viewpoints; experiments distinguish label preservation from model predictive performance. **Limit:** Four public collaborative logs plus a reinterpreted BPI 2013 log; synthetic interpretation and limited domains constrain generality. Very recent preprint, not independent replication.

**URL/DOI:** https://arxiv.org/html/2608.27671v1

### EPM-S029 — PM-LLM-Benchmark: Evaluating Large Language Models on Process Mining Tasks

Alessandro Berti; Humam Kourani; W.M.P. van der Aalst. **Date/version:** Workshop 2024; published 2025; ICPM 2024 Workshops, LNBIP 533, pp. 610–623, 2025. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: benchmark and evaluation design; §4, Tables 4–5: evaluation dependence; Discussion of biases. **Inspected claim:** Language models assist some analysis and code tasks; evaluations depend on task prompts and the evaluating model. **Limit:** LLM-as-judge, public-data contamination risk and dated model versions prevent treating the scores as current autonomous-analysis reliability.

**URL/DOI:** https://www.alessandroberti.it/new_papers/2024_Berti_PMLLMBenchmark.pdf; DOI 10.1007/978-3-031-82225-4_45

### EPM-S030 — Prescriptive Process Monitoring Under Resource Constraints: A Causal Inference Approach

Mahmoud Shoush; Marlon Dumas. **Date/version:** 2021 preprint; 2022 proceedings; arXiv 2109.02894. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Treatment-effect and resource-aware prescription; Evaluation with costs and resource constraints; Conclusion. **Inspected claim:** Estimated treatment effects and scarce intervention resources alter which cases should receive recommendations. **Limit:** Net gain depends on estimated counterfactuals and assumed costs; offline evaluation is not a deployed randomised trial.

**URL/DOI:** https://arxiv.org/pdf/2109.02894

### EPM-S031 — Mining Process Models with Non-Free-Choice Constructs

Lijie Wen; Jianmin Wang; W.M.P. van der Aalst; Jiaguang Sun. **Date/version:** 2007; 36-page author manuscript. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Problem examples; Alpha++ and implicit dependencies; Correctness scope and evaluation. **Inspected claim:** Longer-distance and implicit dependencies extend discovery beyond the local relations sufficient for restricted alpha cases. **Limit:** Broader representational support still depends on completeness and structural assumptions; not a universal inverse of process execution.

**URL/DOI:** https://www.vdaalst.com/publications/p394.pdf

### EPM-S032 — Business Process Mining: An Industrial Application

W.M.P. van der Aalst; Hajo A. Reijers; A.J.M.M. Weijters; Boudewijn F. van Dongen; A.K. Alves de Medeiros; Minseok Song; H.M.W. Verbeek. **Date/version:** 2007; Information Systems 32; inspected 30-page manuscript. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Case description and preparation; Mining results; Discussion and conclusions. **Inspected claim:** A provincial office of Dutch national public works agency RWS analysed invoice handling. Control-flow, performance and organisational findings were discussed with participants; project leaders were informed and agreed to higher invoice priority. **Limit:** A single RWS programme, not a municipality. The reported management response is not a measured post-intervention causal benefit. Shared authors do not establish that this is the same case as the social-network paper.

**URL/DOI:** https://www.vdaalst.com/publications/p373.pdf

### EPM-S033 — Your Secret Is Safe With Me: Federated Directly-Follows Graph Discovery

Christian Rennert; Julian Albers; Sander J.J. Leemans; W.M.P. van der Aalst. **Date/version:** 2025-10; ICPM 2025, 8 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Security/setting assumptions; Encrypted discovery protocol; Evaluation and limitations. **Inspected claim:** A two-organisation protocol uses homomorphic encryption to compute a directly-follows graph while limiting disclosure of underlying activities and timestamps. **Limit:** Two organisations with shared case identifiers and negotiated activity mapping. Brute-force and trace-based variants trade computation against disclosure: the faster trace-based approach discloses shared case identities/trace lengths. Output DFG privacy is a separate obligation.

**URL/DOI:** https://leemans.ch/publications/papers/icpm2025rennert.pdf; DOI 10.1109/ICPM66919.2025.11220699

### EPM-S034 — Streaming Process Mining

Andrea Burattin. **Date/version:** 2022; Process Mining Handbook, chapter 11. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Stream assumptions and challenges; Discovery and conformance mechanisms; Limitations and research directions. **Inspected claim:** Streaming methods trade finite memory and timely results against incomplete cases, ordering and forgetting; discovery and prefix-conformance require different summaries. **Limit:** Chapter synthesises mechanisms; it does not establish broad production deployment or validate all stream assumptions.

**URL/DOI:** https://link.springer.com/chapter/10.1007/978-3-031-08848-3_11; DOI 10.1007/978-3-031-08848-3_11

### EPM-S035 — Discovering Object-Centric Petri Nets

W.M.P. van der Aalst; Alessandro Berti. **Date/version:** 2020; Author manuscript; Fundamenta Informaticae 175(1–4), 1–40. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Object-centric event-log and Petri-net definitions; Discovery algorithm using per-type projections; Examples, evaluation and concluding limitations. **Inspected claim:** Typed objects and shared events permit discovery without forcing all observations into one case identifier. **Limit:** Object identity, type assignment and projection assumptions remain necessary; conventional soundness cannot be silently transferred to every object-centric net.

**URL/DOI:** https://arxiv.org/pdf/2010.02047; DOI 10.3233/FI-2020-1946

### EPM-S036 — The ProM Framework: A New Era in Process Mining Tool Support

Boudewijn F. van Dongen; A.K. Alves de Medeiros; H.M.W. Verbeek; A.J.M.M. Weijters; W.M.P. van der Aalst. **Date/version:** 2005; PETRI NETS 2005, pp. 444–454. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Framework architecture and plug-in categories; Import/export and examples. **Inspected claim:** A plug-in research framework connects event-log import, mining, analysis and conversion. **Limit:** Historical implementation architecture only; no present-version claim or proof that using the framework improves an organisation.

**URL/DOI:** https://www.vdaalst.com/publications/p264.pdf; DOI 10.1007/11494744_25

### EPM-S037 — Dealing With Concept Drifts in Process Mining

R.P. Jagadeesh Chandra Bose; W.M.P. van der Aalst; Indrė Žliobaitė; Mykola Pechenizkiy. **Date/version:** Online 2013; issue 2014-01; IEEE TNNLS 25(1), 154–171. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Feature-based drift framework; Change-point and drift-type discussion; Experimental evaluation and real-life application. **Inspected claim:** Process-specific features and statistical tests address change over time rather than fitting one timeless model. **Limit:** Feature choice bounds detectable change; original work and later reuse of public or municipal logs are not independent organisational outcomes.

**URL/DOI:** https://mpechen.win.tue.nl/publications/pubs/JCBoseTNNLS.pdf; DOI 10.1109/TNNLS.2013.2278313

### EPM-S038 — Genetic process mining: an experimental evaluation

A.K. Alves de Medeiros; A.J.M.M. Weijters; W.M.P. van der Aalst. **Date/version:** 2007-01-31; Data Mining and Knowledge Discovery 14, 245–304. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Genetic representation and genetic operators; Fitness function and experiment design; Discussion of results and limitations. **Inspected claim:** Population-based global search explores process structures using a log-dependent fitness objective. **Limit:** Search cost, stochastic variation and objective design matter. Finite experiments do not establish a global optimum or general superiority.

**URL/DOI:** https://link.springer.com/content/pdf/10.1007/s10618-006-0061-7.pdf; DOI 10.1007/s10618-006-0061-7

### EPM-S039 — Enhancing Event Log Quality: Detecting and Quantifying Timestamp Imperfections

Dominik A. Fischer; K. Goel; Robert Andrews; Christopher G.J. van Dun; Moe T. Wynn; Maximilian Röglinger. **Date/version:** 2020; 17-page institutional author manuscript. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §2 and PDF p. 4: mixed granularity and form-based capture; §3: metrics and levels of analysis; Evaluation on three real-life logs and expert feedback. **Inspected claim:** Timestamp diagnostics distinguish completeness, accuracy, consistency and uniqueness across levels; coarse or copied times can fabricate event order. **Limit:** Metrics detect symptoms and do not by themselves recover the actual execution time. Three logs and expert evaluation do not establish universal data-repair validity.

**URL/DOI:** https://www.fim-rc.de/Paperbibliothek/Veroeffentlicht/1060/wi-1060.pdf

### EPM-S040 — Group-based privacy preservation techniques for process mining

Majid Rafiei; W.M.P. van der Aalst. **Date/version:** 2021; Data & Knowledge Engineering 134, 101908. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: logs and attacker background knowledge; TLKC privacy model and transformations; Evaluation and utility across perspectives. **Inspected claim:** Trace structure can identify people even when identifiers are removed; protection depends on attacker knowledge and sacrifices some utility. **Limit:** Group-based guarantees cover specified attacks, not all auxiliary information or output-inference risks; altered traces can change mining conclusions.

**URL/DOI:** https://publications.rwth-aachen.de/record/824789/files/824789.pdf; DOI 10.1016/j.datak.2021.101908

### EPM-S041 — On the Discovery of Declarative Control Flows for Artful Processes

Claudio Di Ciccio; Massimo Mecella. **Date/version:** 2015; Author manuscript uploaded by an author; bibliographic version ACM TMIS 5(4), 24:1–37. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** MINERful framework and knowledge base; Support, confidence, interest and pruning; Evaluation and discussion. **Inspected claim:** A two-stage counting and constraint-query approach discovers declarative behaviour in flexible processes. **Limit:** Inspected author manuscript contains unresolved publication placeholders; bibliography identifies ACM TMIS 5(4), article 24 (2015). Do not use manuscript placeholder dates/DOIs.

**URL/DOI:** https://www.researchgate.net/publication/276164466_On_the_Discovery_of_Declarative_Control_Flows_for_Artful_Processes; DOI 10.1145/2629447

### EPM-S042 — Semantical Vacuity Detection in Declarative Process Mining

Fabrizio Maria Maggi; Marco Montali; Claudio Di Ciccio; Jan Mendling. **Date/version:** 2016; BPM 2016 author manuscript, 16 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§2–3: finite-trace semantics and motivation; §§4–5: activation and automata; Evaluation on real-life logs. **Inspected claim:** Semantic activation distinguishes meaningful satisfaction from constraints that hold because their antecedents never activate. **Limit:** Activation semantics do not establish that a learned constraint is normatively desirable; expensive or redundant constraints still require selection.

**URL/DOI:** https://www.inf.unibz.it/~montali/papers/diciccio-etal-BPM2016-vacuity-declare.pdf

### EPM-S043 — Soundness in Object-centric Workflow Petri Nets

Irina A. Lomazova; Alexey A. Mitsyuk; Andrey Rivkin. **Date/version:** 2021-12-30; arXiv 2112.14994v1; formal claim status retained with evidence limit. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§4–5: OC-net and object-type projection semantics; §6: object-centric soundness definition and Theorem 1; §7: relationships to other object-aware models. **Inspected claim:** Object-centric completion requires a stated notion of soundness rather than simply importing a single-case criterion. **Limit:** The inspected preprint has inconsistent proof-status phrasing (conjecture in introduction versus theorem later); this packet does not certify the decidability claim. Type-level tokens and availability of supporting objects matter.

**URL/DOI:** https://arxiv.org/html/2112.14994v1

### EPM-S044 — Noise-resistant discovery of identifier-sound object-centric process models with dynamic identity relations

Jan Niklas van Detten; Pol Schumacher; Benedikt Knopp; Sander J.J. Leemans. **Date/version:** 2026-06-21; Process Science 3, article 17. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Dynamic identity relation definitions; Extended object-centric Petri nets and identifier soundness; Discovery, evaluation and future work. **Inspected claim:** Identity relations and constrained process trees support richer object behaviour with a stated identifier-sound construction. **Limit:** Tree class and noise thresholds limit coverage; evaluation is not independent deployed validation. Further conformance support for identity relations remains a research direction.

**URL/DOI:** https://link.springer.com/article/10.1007/s44311-026-00052-w; DOI 10.1007/s44311-026-00052-w

### EPM-S045 — Digital Health Data Imperfection Patterns and Their Manifestations in an Australian Digital Hospital

Kanika Goel; Arthur H.M. ter Hofstede; Sander J.J. Leemans; Andrew Staib; Sareh Sadeghianasl; Moe T. Wynn; James McGree; Rob Eley; Robert Andrews; Dakshi Kapugama Geeganage; Rebekah Eden; Raelene Donovan. **Date/version:** 2023; HICSS 2023 author manuscript, 10 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§2–3: six imperfection patterns; §§4–5: site and approach, PDF p. 6; §6: findings and member checking. **Inspected claim:** An emergency-department study connects recorded data imperfections with recording practices and stakeholder interpretation. **Limit:** One hospital and retrospective extraction; demonstration of imperfections is not a measured patient-outcome benefit. This is a domain translation, not proof all sectors have identical defect frequencies.

**URL/DOI:** https://leemans.ch/publications/papers/hicss2023goel.pdf

### EPM-S046 — Balanced multi-perspective checking of process conformance

Felix Mannhardt; Massimiliano de Leoni; Hajo A. Reijers; W.M.P. van der Aalst. **Date/version:** Online 2015; issue 2016; 32-page institutional copy; Computing 98, 407–437. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §2: control-flow-first diagnostic counterexample; §§3–4: data Petri nets and balanced alignments; §6: Italian road-traffic-fines case and synthetic experiments. **Inspected claim:** Joint data and control-flow alignment can avoid misleading diagnoses produced by optimising perspectives in isolation. **Limit:** Guard, data-domain and cost assumptions remain. Repository cover and manuscript version descriptions differ; the inspected copy is identified, not asserted byte-identical to final publication. Road Traffic Fines data are reused elsewhere.

**URL/DOI:** https://pure.tue.nl/ws/files/4020941/377779004839577.pdf; DOI 10.1007/s00607-015-0441-1

### EPM-S047 — Repairing Process Models to Reflect Reality

Dirk Fahland; W.M.P. van der Aalst. **Date/version:** 2012; BPM 2012, pp. 229–245. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §1 and Fig. 1: repair instead of whole-model rediscovery; Alignment-based local repair construction; Evaluation and discussion. **Inspected claim:** Local model repair combines alignments with discovered submodels to regain log fit while retaining useful original structure. **Limit:** A better fit to recorded work does not authorise alteration of a prescriptive rule; same observation may warrant correcting data or work rather than the model.

**URL/DOI:** https://www.vdaalst.com/publications/p681.pdf; DOI 10.1007/978-3-642-32885-5_19

### EPM-S048 — Unbiased, Fine-Grained Description of Processes Performance from Event Data

Vadim Denisov; Dirk Fahland; W.M.P. van der Aalst. **Date/version:** 2018; BPM 2018, pp. 139–157. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§3–4: performance spectrum and pattern context; §5: public-log analysis and baggage-handling case; Conclusion. **Inspected claim:** Fine-grained performance spectra expose batching, overtaking and temporal patterns hidden by averages. **Limit:** The title does not establish absence of selection or recording bias. Public-log reuse and one logistics programme do not give independent benefit estimates. Figure-render access partly failed; conclusions use inspected text, not unread diagrams.

**URL/DOI:** https://www.vdaalst.rwth-aachen.de/publications/p1027.pdf; DOI 10.1007/978-3-319-98648-7_9

### EPM-S049 — Mining Local Process Models

Niek Tax; Natalia Sidorova; Reinder Haakma; W.M.P. van der Aalst. **Date/version:** 2016; Author manuscript; Journal of Innovation in Digital Ecosystems 3, 183–196. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §1 and Fig. 1: local patterns versus whole-process flower model; Local model quality and discovery algorithm; Experiments. **Inspected claim:** Local models can represent recurrent structured fragments without pretending to describe all end-to-end behaviour. **Limit:** Coverage and relevance are task-specific; separate local fragments do not prove whole-process completion or compatibility.

**URL/DOI:** https://arxiv.org/pdf/1606.06066

### EPM-S050 — OPerA: Object-Centric Performance Analysis

Gyunam Park; Jan Niklas Adams; W.M.P. van der Aalst. **Date/version:** 2022-06-27; arXiv 2204.10662v2. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: event and OCPN semantics; §4: timed replay and performance measures; §5.2: filtered loan-log comparison; §6: non-conformance limitation. **Inspected claim:** Object-aware timed replay distinguishes waiting, synchronisation, pooling and lagging; flattening changes reported counts and durations. **Limit:** The case uses a filtered loan log, not a new deployment trial. Correct calculations presuppose a suitable model and event semantics; missing non-conforming events can misplace timing.

**URL/DOI:** https://arxiv.org/html/2204.10662v2

### EPM-S051 — Process Mining: Data Science in Action

W.M.P. van der Aalst. **Date/version:** 2016; Second edition. **Access:** METADATA_AND_CONTENTS, 2026-09-06.

**Locator:** Publisher overview and table of contents; Edition and bibliographic metadata. **Inspected claim:** The second-edition monograph consolidates event data, discovery, conformance, enhancement and operational support. **Limit:** Book metadata and contents inspected, not the entire monograph. Substantive mechanisms in this packet rely on separately accessed primary papers or open handbook chapters.

**URL/DOI:** https://link.springer.com/book/10.1007/978-3-662-49851-4; DOI 10.1007/978-3-662-49851-4

### EPM-S052 — Streaming Process Discovery and Conformance Checking

Andrea Burattin. **Date/version:** 2018; Encyclopedia chapter author manuscript, 11 pages. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** Stream processing definitions; Discovery and conformance approaches; Application and research challenges. **Inspected claim:** Streaming mining adapts bounded-memory and incremental analysis to event arrival. **Limit:** The author reports limited deployment awareness at that historical date; this cannot establish absence of deployments in 2026.

**URL/DOI:** https://andrea.burattin.net/public-files/publications/2018-encyclopedia.pdf

### EPM-S053 — All That Glitters Is Not Gold: Towards Process Discovery Techniques with Guarantees

Jan Martijn E.M. van der Werf; Artem Polyvyanyy; Bart R. van Wensveen; Matthieu Brinkhuis; Hajo A. Reijers. **Date/version:** 2020-12-23; arXiv 2012.12764v1; related CAiSE 2021 publication. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §3: event-log sampling; §4: proposed maturity stages; §4.3.1 and Table 1: controlled experiment. **Inspected claim:** Applicability, input/output quality relationships and effectiveness are distinct claims; better sampled log quality need not improve every model metric. **Limit:** Inspected early preprint, not the materially extended 2023 journal work. Proposed stages are an argument, not a universally accepted maturity standard.

**URL/DOI:** https://arxiv.org/pdf/2012.12764

### EPM-S054 — From Words to Workflows: Extracting Object-Centric Event Logs from Textual Data

Alina Buss; Christoph Kecht; Wolfgang Kratsch; Maximilian Röglinger; Sareh Sadeghianasl; Moe T. Wynn. **Date/version:** 2025-06-07; CAiSE 2025 Forum, pp. 37–44. **Access:** ABSTRACT_AND_METADATA, 2026-09-06.

**Locator:** Publisher abstract and bibliographic record. **Inspected claim:** A collector/refiner design combines heuristic and generative extraction of object-centric event data from text. **Limit:** Abstract-only access; detailed measurements and later changes are taken from the separately inspected 2026 extension. Same programme is not independent replication.

**URL/DOI:** https://link.springer.com/chapter/10.1007/978-3-031-94590-8_5; DOI 10.1007/978-3-031-94590-8_5

### EPM-S055 — Process mining between the lines: Extracting object-centric event logs from textual data

Alina Buss; Christoph Kecht; Wolfgang Kratsch; Maximilian Röglinger; Sareh Sadeghianasl; Moe T. Wynn. **Date/version:** 2026-03-06; Information Systems 140, 102713; available online 6 March 2026. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §4: collector/refiner architecture and implementation; §5.3: six-log synthetic-text evaluation and Table 4; §5.4: two naturally occurring corpora; §6: limitations and organisational validation gap. **Inspected claim:** Generative and heuristic components have different extraction, control and cost trade-offs; a 2026 extension adds natural-text demonstrations and revised implementations. **Limit:** Six OCEL-derived corpora include three used during development; two natural corpora illustrate use, not organisational benefit. Changed models and matching code confound a simple year-to-year progress claim.

**URL/DOI:** https://www.fim-rc.de/Paperbibliothek/Veroeffentlicht/5180/id-5180.pdf; DOI 10.1016/j.is.2026.102713

### EPM-S056 — On Process Discovery Experimentation: Addressing the Need for Research Methodology in Process Discovery

Jana-Rebecca Rehse; Sander J.J. Leemans; Peter Fettke; Jan Martijn E.M. van der Werf. **Date/version:** 2024-12; repository issue date 2025-01; ACM TOSEM 34(1), article 3, 29 pages plus repository cover. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §1 and Table 1: incompatible comparison premises; §§3–4: research methodology and experimentation checklist; §5: example experiment; §6.2–6.3: generality, usability and guarantees limits. **Inspected claim:** Experimental design must connect concepts, hypotheses, operationalisations and conclusions; checklist completion alone does not guarantee validity. **Limit:** Authors demonstrate their own methodology, not independent effectiveness of the checklist. Version dates reflect print/repository conventions, not two studies.

**URL/DOI:** https://research-portal.uu.nl/ws/portalfiles/portal/252437297/3672447.pdf; DOI 10.1145/3672447

### EPM-S057 — Uncertainty-Aware Predictive Process Monitoring in Healthcare: Explainable Insights into Probability Calibration for Conformal Prediction

Maxim Majlatow; Fahim Ahmed Shakil; Andreas Emrich; Nijat Mehdiyev. **Date/version:** 2025-07-16; Applied Sciences 15(14), 7925; author-uploaded full text. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§3–4: calibration and conformal prediction methods; §4.6: 995 preprocessed cases, 200 bootstrap iterations, disjoint out-of-bag calibration/test sets; §6: single-hospital, static-data and deployment limitations. **Inspected claim:** A retrospective sepsis-log study compares probability calibration and prediction-set behaviour. Probability calibration, set coverage and explanation are different evaluation targets. **Limit:** Single reused public sepsis dataset, not 200 independent deployments. Bootstrap partitions do not establish temporal transport or clinical benefit. Authors disclaim deployment readiness. No claim that a well-calibrated base classifier is necessary for conformal marginal coverage. Publisher full-text access failed; lawful author text inspected.

**URL/DOI:** https://www.researchgate.net/publication/393764204_Uncertainty-Aware_Predictive_Process_Monitoring_in_Healthcare_Explainable_Insights_into_Probability_Calibration_for_Conformal_Prediction; DOI 10.3390/app15147925

### EPM-S058 — Conformal prediction beyond exchangeability

Rina Foygel Barber; Emmanuel J. Candès; Aaditya Ramdas; Ryan J. Tibshirani. **Date/version:** 2022-02-27 preprint; 2023 journal; Author manuscript; Annals of Statistics 51(2), 816–845. **Access:** FULL_TEXT_CLAIM_RELEVANT_SECTIONS, 2026-09-06.

**Locator:** §§1–2 and Theorem 1, manuscript p.7: exchangeability and symmetry conditions; §§3–4: weighted non-exchangeable coverage bounds and interpretation. **Inspected claim:** Conformal prediction supplies marginal coverage under explicit data/algorithm conditions; extensions quantify a coverage loss under non-exchangeability rather than guaranteeing nominal coverage under arbitrary drift. **Limit:** External statistical theory, not process-mining field validation. Marginal coverage is not individual conditional certainty, probability calibration or causal benefit. This exact paper is used as an analytical qualification, not asserted to be directly cited by S057.

**URL/DOI:** https://www.stat.berkeley.edu/~ryantibs/papers/nexcp.pdf; DOI 10.1214/23-AOS2276

