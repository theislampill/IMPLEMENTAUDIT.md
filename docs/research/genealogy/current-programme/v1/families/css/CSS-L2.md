# CSS-L2 — Statistical Engineering

> **Current scientific reading route — 13 November 2026:** the substantial [CSS-L2 account](current/CSS-L2.md) and [full scientific readers](current/README.md) now provide the normalized current interpretation. Disclosure and withholding statements in the retained record below describe its earlier cutoff; immutable programme and increment records remain historical.


[Family](README.md) · [Genealogy](GENEALOGY.md) · [Synthesis](CSS-S.md) · [Rough work outlines](RLGWO_OUTLINES.md) · [Completeness](COMPLETENESS.md)

## Two evidence layers

This reader explains the **65-property historical public corpus**. The separately qualified current CSS-L2 subject has **65 selected property identities**. The original history and dispositions below remain attached to the historical source; they are not relabelled as the corrected study or as current implementation acceptance. [Current identities and exact review pins](../../PROGRAMME.json) · [Original family overview](../css.md).

The corrected current study and its accepted reviews are documented in the private family interpretation. Detailed current scientific publication awaits a source-specific disclosure decision. The public reader does not fill that gap with historical text. The [component assessment](COMPLETENESS.md) keeps those limits explicit.

## Explanation from the public predecessor

### What the public predecessor supports

Measurement starts with the intended property, unit, context and decision. P001 specifies the quantity or construct; P002 asks whether the measurement system can discriminate at the relevant margin. P004/005 separate accuracy from precision and repeatability/reproducibility from validity. A score can be stable and still answer the wrong question. More narrow numerical uncertainty around that score does not repair the property mapping. [Statistical ledger, P001–P007][s-ledger]

**Illustrative case: a repaired candidate and a repaired test.** If both change after a failure, the new green result does not itself show which change mattered. P052 requires independent, prospective justification for evaluator changes and preservation of the original witness; P053 asks for stable reference cases or crossed evaluators/candidates that distinguish product variation from measurement variation. A direct inspection proving a deterministic bug can be sufficient. A larger experiment is warranted only when it resolves remaining decision-relevant ambiguity. [Statistical ledger, P052–P053][s-ledger]

Comparison needs the right unit and claim. P030 concerns randomised assignment and analysis consistent with how assignment actually occurred. P032 concerns independent experimental units; repeated observations of one unit can inform measurement precision without becoming independent replication of the intervention. P036 concerns magnitude, uncertainty and the engineering margin, including equivalence or noninferiority when interchangeability is the decision. These distinctions are why generic reviewer independence cannot substitute for all statistical requirements. [Statistical ledger, P030–P032 and P036][s-ledger]

Context matters after a successful test. P049 separates performance on held-out observations from validity under distribution shift or operational stress. P050 distinguishes mean performance, variability, tails, reliability over time and robustness. P038 protects sequential inference from unplanned repeated looks; P041/057 stop or retire measurement when additional evidence cannot change a capable consumer's action. None of these properties creates a fixed run count or a requirement to use statistics when P042's authoritative deterministic discriminator already settles the question. [Statistical ledger, P038–P050 and P057][s-ledger]

### Relationship to IMPLEMENTAUDIT

R002B/#195's original integration distinguished measurement fitness, variation attribution and sequential information value, and explicitly refused to equate four partial statistical predicates with generic existing-owner similarity. Its later terminal receipt accepts the original 65-row contract at a named v0.4 subject. The present phase-design and acceptance-instrument owners retain evaluator-change and state-synthesis rules; current fixture classification is narrower than validating a real-world construct or deployment population. The historical partials, the later bounded terminal receipt and any current residual therefore need separate treatment. [R002B issue][195] · [R002B terminal receipt][195-receipt] · [Native phase source][phase-source]

The corpus rejects universal p-value thresholds and ritual methods while preserving conditional inference. It does not claim that all p-values are useless, randomisation cures every validity problem, zero failures means zero risk, or metrology/manufacturing evidence transfers unchanged to software or agents. [Statistical public intake limits][s-intake] · [Four rough outlines](RLGWO_OUTLINES.md#css-l2--statistical-engineering)

## Historical property reader

Every one of the 65 rows is represented below, including rejected, contextual and unresolved dispositions. Wording under the labelled fields is transcribed from the public ledger. The evidence profile is the corpus author’s assessment at that freeze, not a new evidence review. Packet-local source identities resolve through the [source table](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json). The [machine-readable map](PUBLIC_PROPERTY_SOURCE_MAP.json) binds each entry to its exact ledger field and rendered anchor.

The full ledger retains additional structured profiles and source context: [immutable ledger](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json).

[P001](#p001) · [P002](#p002) · [P003](#p003) · [P004](#p004) · [P005](#p005) · [P006](#p006) · [P007](#p007) · [P008](#p008) · [P009](#p009) · [P010](#p010) · [P011](#p011) · [P012](#p012) · [P013](#p013) · [P014](#p014) · [P015](#p015) · [P016](#p016) · [P017](#p017) · [P018](#p018) · [P019](#p019) · [P020](#p020) · [P021](#p021) · [P022](#p022) · [P023](#p023) · [P024](#p024) · [P025](#p025) · [P026](#p026) · [P027](#p027) · [P028](#p028) · [P029](#p029) · [P030](#p030) · [P031](#p031) · [P032](#p032) · [P033](#p033) · [P034](#p034) · [P035](#p035) · [P036](#p036) · [P037](#p037) · [P038](#p038) · [P039](#p039) · [P040](#p040) · [P041](#p041) · [P042](#p042) · [P043](#p043) · [P044](#p044) · [P045](#p045) · [P046](#p046) · [P047](#p047) · [P048](#p048) · [P049](#p049) · [P050](#p050) · [P051](#p051) · [P052](#p052) · [P053](#p053) · [P054](#p054) · [P055](#p055) · [P056](#p056) · [P057](#p057) · [P058](#p058) · [P059](#p059) · [P060](#p060) · [P061](#p061) · [P062](#p062) · [P063](#p063) · [P064](#p064) · [P065](#p065)

<a id="p001"></a>
### P001 — Define the decision-relevant measurand or construct before quantification

**Historical origin:** Metrology’s measurand discipline, experimental operationalisation, and later construct-validity/invariance work.

**Original form:** State what quantity or property is intended, under which conditions, before assigning a number.

**Development:** Evolved from physical quantity definition toward explicit construct, context and decision-use validation.

**Evolved form in this historical corpus:** No metric governs until its intended property, scope, consumer, and admissible interpretation are fixed enough to be challenged.

**Problem:** A precise, reproducible number can answer the wrong question or represent an unstable proxy.

**Mechanism:** Bind each metric to a stated measurand/construct, unit of analysis, operating conditions, intended use, and disconfirming observations.

**Trigger and context:** Any measurement used to accept, reject, optimise, compare, or monitor an engineering state.

**Preconditions:** Domain definition, decision owner, scope, and an explicit mapping from observations to the property of interest.

**Measurement preconditions:** The operational definition must preserve the distinctions the decision actually requires; an evaluator must not collapse relevant states.

**Assumptions:** The construct is sufficiently coherent for the intended decision and its operationalisation does not change materially across samples.

**Decision or consumer:** Design authority, test owner, regulator, operator, or other consumer of the decision.

**Nontrigger or cheaper adequate path:** When an authoritative deterministic fact directly answers the decision, record that fact rather than inventing a surrogate score.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Ambiguous labels; changing definitions between baseline and candidate; composite scores whose weights hide trade-offs.

**Criticism:** Metrology can define a measurand precisely while still leaving broader validity contested; formal latent constructs add model dependence.

**Contrary evidence:** Construct-validity evidence is domain-dependent; no universal statistical test establishes that a metric means what stakeholders intend.

**Unresolved questions:** How should construct adequacy be stress-tested when the desired property is partly normative or changes with deployment context?

**Property versus ceremony:** A template or ontology is optional; the property is the explicit decision-linked definition.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: MODERATE; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S052; S055; S056

**Critical source identities:** S027; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/0`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p002"></a>
### P002 — Establish measurement-system fitness before metric governance

**Historical origin:** Eisenhart/NBS calibration-system evaluation, measurement assurance, gauge R&R, GUM and laboratory-quality systems.

**Original form:** Characterise the measurement process before treating its outputs as facts about the production process.

**Development:** Evolved from instrument calibration and variance decomposition to decision-specific evaluator capability and versioned validation.

**Evolved form in this historical corpus:** Demonstrate enough discrimination for the intended decision, not abstract “good measurement,” and recheck after material evaluator change.

**Problem:** Observed variation may be dominated by instrument, operator, environment, fixture, algorithm, or evaluator variation.

**Mechanism:** Estimate bias, repeatability, reproducibility, resolution, stability and uncertainty relative to the decision margin; block use when discrimination is inadequate.

**Trigger and context:** Metrics near thresholds, comparisons whose expected effect is small, multi-operator/evaluator systems, or costly decisions.

**Preconditions:** Defined measurand, representative items/conditions, reference or comparison basis, and a stated decision margin.

**Measurement preconditions:** The study must span the real operating range and relevant operators, instruments, environments and preprocessing paths.

**Assumptions:** Measurement error is reasonably estimable over the intended range and the study itself has not selected unusually easy samples.

**Decision or consumer:** Anyone relying on a metric, threshold, trend or experiment outcome.

**Nontrigger or cheaper adequate path:** For a deterministic binary check with an authoritative oracle and negligible ambiguity, verify the oracle and use it directly rather than perform full MSA.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Narrow part range; nonrepresentative operators; stable repeatability but unknown bias; passing a generic GR&R percentage unrelated to the decision.

**Criticism:** Gauge R&R is only one design; destructive, automated, subjective and probabilistic evaluators require other designs.

**Contrary evidence:** No single GR&R threshold is universally optimal; measurement investment depends on decision loss and achievable resolution.

**Unresolved questions:** How should measurement fitness be quantified for adaptive, generative or partly subjective evaluators?

**Property versus ceremony:** The form, software package, fixed 10×3×3 design or percentage cutoff is ceremony; decision-linked discrimination is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S015; S055; S058

**Critical source identities:** S032; S053

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/1`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p003"></a>
### P003 — Calibration and metrological traceability where decision-relevant

**Historical origin:** Physical metrology, calibration hierarchies, VIM/GUM and ISO/IEC 17025.

**Original form:** Relate measurement results to references through a documented calibration chain with stated uncertainty.

**Development:** Evolved from periodic instrument adjustment to result-specific traceability plus ongoing measurement assurance.

**Evolved form in this historical corpus:** Require the level of traceability needed for comparability and decision risk, alongside—not instead of—fitness validation.

**Problem:** A stable instrument can be consistently offset, incomparable across sites, or anchored to an obsolete reference.

**Mechanism:** Use suitable standards/reference methods, record calibration state and uncertainty contributions, and maintain traceability at the result level.

**Trigger and context:** Physical/chemical measurements, regulated tolerances, interlaboratory exchange, or any decision requiring comparability to a standard.

**Preconditions:** Valid calibration method, competent execution, suitable reference, environmental controls, and an uncertainty chain.

**Measurement preconditions:** Calibration points and standards must cover the range, matrix and conditions of use.

**Assumptions:** The reference hierarchy and calibration model remain applicable; no unmodelled transport or nonlinear effects dominate.

**Decision or consumer:** Laboratory, manufacturer, customer, regulator and downstream analysts.

**Nontrigger or cheaper adequate path:** For purely ordinal/local decisions with a verified internal reference and no cross-context claim, full national/international traceability may add no value.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** “NIST-traceable” asserted for an organisation; calibration certificate without uncertainty; traceability outside the working range.

**Criticism:** NIST explicitly rejects treating traceability as a guarantee of fitness for purpose or absence of mistakes.

**Contrary evidence:** Some digital/subjective measurements lack a meaningful SI chain; analogous provenance does not equal metrological traceability.

**Unresolved questions:** What is the minimum defensible reference chain for nonphysical evaluators and rapidly changing benchmarks?

**Property versus ceremony:** A certificate, logo or fixed interval is not the property; the evidence chain and decision fitness are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: LOW; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S052; S054; S056

**Critical source identities:** S060; S103

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/2`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p004"></a>
### P004 — Keep bias/accuracy distinct from precision

**Historical origin:** Classical measurement error, NBS measurement evaluation, ISO 5725 and VIM.

**Original form:** Separate systematic displacement from random dispersion and estimate each against a reference/use case.

**Development:** Modern practice reports trueness/bias, precision and uncertainty rather than one undifferentiated “accuracy” score.

**Evolved form in this historical corpus:** Decision-specific decomposition of systematic and random error, with correction only when validated.

**Problem:** Highly repeatable measurements can be systematically wrong; averaging reduces random error but not shared bias.

**Mechanism:** Compare to suitable references/alternatives for bias while estimating dispersion under repeatability and reproducibility conditions.

**Trigger and context:** Whenever magnitude or direction relative to truth/standard matters, especially near limits.

**Preconditions:** Reference value or defensible triangulation, representative operating range and stable calibration/evaluator state.

**Measurement preconditions:** Enough resolution and coverage to detect both offset and dispersion; uncertainty in the reference included.

**Assumptions:** Bias is reasonably stable or modelled over range/context; reference is more informative than the system under test.

**Decision or consumer:** Measurement owner and decision consumer.

**Nontrigger or cheaper adequate path:** If the decision is invariant to a known constant offset and only ranks within one stable system, bias correction may be unnecessary—but must be explicit.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Using correlation as accuracy; reporting only standard deviation; reference standard shares the same bias.

**Criticism:** The property is bounded by its stated assumptions and known failures: Using correlation as accuracy; reporting only standard deviation; reference standard shares the same bias. Contrary evidence/limit: For complex construct measures, “true value” may be unavailable; bias must then be bounded through convergent/criterion evidence rather than asserted.

**Contrary evidence:** For complex construct measures, “true value” may be unavailable; bias must then be bounded through convergent/criterion evidence rather than asserted.

**Unresolved questions:** How can shared-method bias be detected when all available reference systems inherit common training data or assumptions?

**Property versus ceremony:** Extra decimal places and repeated readings are ceremony when the dominant error is systematic.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: LOW; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S015; S052; S057

**Critical source identities:** S024; S032

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/3`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p005"></a>
### P005 — Distinguish repeatability, reproducibility and validity

**Historical origin:** Interlaboratory measurement science, ISO 5725, gauge R&R, rater reliability and reproducibility debates.

**Original form:** Estimate same-condition variation separately from operator/site/instrument/context variation.

**Development:** Evolved from instrument precision to interlaboratory, computational and evaluator-version reproducibility, while retaining validity as a separate burden.

**Evolved form in this historical corpus:** Claim only the level of stability actually tested, and never infer validity from repeatability alone.

**Problem:** A result may repeat under one setup but fail across competent operators or contexts; both may repeat an invalid construct.

**Mechanism:** Design crossed/nested comparisons over relevant operators, instruments, sites, times and methods; assess validity separately.

**Trigger and context:** Multi-operator, multi-site, automated evaluator, stochastic test or claimed general result.

**Preconditions:** Representative factors and levels, randomisation/order control, clear agreement target and adequate item range.

**Measurement preconditions:** Measurement outputs are comparable and evaluator versions are fixed/documented during the study.

**Assumptions:** Factor effects and interactions can be estimated; repeated conditions approximate intended routine use.

**Decision or consumer:** Measurement owner, experimenter and anyone claiming portability.

**Nontrigger or cheaper adequate path:** For one-use, one-instrument local control with no transfer claim and a wide margin, a limited stability check may suffice.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Confusing reproducibility with exact equality; narrow sample range; no validity criterion; treating reruns as new evidence.

**Criticism:** The property is bounded by its stated assumptions and known failures: Confusing reproducibility with exact equality; narrow sample range; no validity criterion; treating reruns as new evidence. Contrary evidence/limit: Definitions of “reproducibility” vary across metrology and science; the factors changed must always be stated.

**Contrary evidence:** Definitions of “reproducibility” vary across metrology and science; the factors changed must always be stated.

**Unresolved questions:** How should reproducibility be defined for non-deterministic systems whose output distribution, not individual output, is the object?

**Property versus ceremony:** A standard GR&R worksheet is optional; the factor-appropriate variance/agreement design is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S057; S058; S059

**Critical source identities:** S024; S027

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/4`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p006"></a>
### P006 — Match resolution, sensitivity, specificity and threshold discrimination to the decision

**Historical origin:** Instrument resolution/metrology, diagnostic classification, ROC analysis and conformity-assessment decision rules.

**Original form:** Ensure the measurement/classifier can separate states on opposite sides of the action boundary.

**Development:** Evolved from instrument least count and fixed cutoffs to calibrated decision rules, guard bands, ROC/utility analysis and drift checks.

**Evolved form in this historical corpus:** Use the cheapest discriminator whose error profile is adequate for the decision and freeze/version its threshold unless independent recalibration evidence exists.

**Problem:** A coarse or poorly discriminating evaluator makes candidate and measurement variation observationally inseparable.

**Mechanism:** Characterise resolution and class-conditional error across the operating range; choose thresholds using consequence-weighted false-positive/false-negative risks.

**Trigger and context:** Threshold decisions, defect detection, rare-event screens, small expected improvements, or changing class prevalence.

**Preconditions:** Stable labels/reference adjudication, representative prevalence/spectrum, stated loss asymmetry and threshold version.

**Measurement preconditions:** Reference labels are sufficiently accurate and the validation set represents intended use; resolution is not inflated by preprocessing leakage.

**Assumptions:** Future cases are drawn from a relevant population or shift is monitored; class definitions remain stable.

**Decision or consumer:** Decision owner, safety/quality gate, monitoring operator.

**Nontrigger or cheaper adequate path:** When a deterministic authoritative predicate directly distinguishes states, use it instead of estimating sensitivity/specificity.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Selecting threshold on the same test set; ignoring prevalence; changing expected answers after failures; resolution below tolerance width.

**Criticism:** The property is bounded by its stated assumptions and known failures: Selecting threshold on the same test set; ignoring prevalence; changing expected answers after failures; resolution below tolerance width. Contrary evidence/limit: ROC-like summaries may obscure calibration, prevalence shift and heterogeneous costs; no single threshold is universally optimal.

**Contrary evidence:** ROC-like summaries may obscure calibration, prevalence shift and heterogeneous costs; no single threshold is universally optimal.

**Unresolved questions:** How should threshold uncertainty be propagated when both labels and prevalence drift?

**Property versus ceremony:** A universal “90% accuracy” or fixed sigma cutoff is ceremony; the decision-specific error surface is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S052; S053; S103

**Critical source identities:** S024; S039

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/5`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p007"></a>
### P007 — Carry measurement uncertainty into engineering decisions

**Historical origin:** GUM uncertainty budgets, calibration science and conformity-assessment decision rules.

**Original form:** Identify material uncertainty components, combine them appropriately and report their relation to the decision boundary.

**Development:** Evolved from error margins to structured budgets and decision rules linking uncertainty to false accept/reject risks.

**Evolved form in this historical corpus:** Use proportionate uncertainty analysis sufficient to show whether the next action is discriminated.

**Problem:** Point estimates and binary labels can conceal that the decision is not actually discriminated.

**Mechanism:** Build an uncertainty model/budget, propagate components and use intervals, guard bands or explicit loss-based rules.

**Trigger and context:** Measurements close to specifications, comparisons with small effects, extrapolations, and regulated claims.

**Preconditions:** Defined measurand/model, traceable components where applicable, covariance handling, and a stated coverage/decision rule.

**Measurement preconditions:** Inputs and correlations are characterised over the intended regime; software/preprocessing uncertainty included when material.

**Assumptions:** The propagation model is adequate; uncertainty is not silently conditional on fixed but uncertain calibration/model choices.

**Decision or consumer:** Conformance authority, designer, customer or risk owner.

**Nontrigger or cheaper adequate path:** When the result is far from every relevant boundary and a conservative worst-case bound suffices, a detailed budget may be unnecessary.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Double-counted components; omitted covariance; confidence interval mislabeled as tolerance interval; uncertainty reported without decision use.

**Criticism:** The property is bounded by its stated assumptions and known failures: Double-counted components; omitted covariance; confidence interval mislabeled as tolerance interval; uncertainty reported without decision use. Contrary evidence/limit: GUM-style propagation can be strained by nonlinearity, asymmetric tails, model uncertainty and adaptive algorithms; simulation/Bayesian or interval methods may be needed.

**Contrary evidence:** GUM-style propagation can be strained by nonlinearity, asymmetric tails, model uncertainty and adaptive algorithms; simulation/Bayesian or interval methods may be needed.

**Unresolved questions:** How should epistemic model uncertainty and evaluator retraining uncertainty be integrated without false numerical precision?

**Property versus ceremony:** A long budget is ceremony if a dominant bound already resolves the decision; conversely, “±” without a model is decorative.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S051; S053; S100

**Critical source identities:** S054; S103

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/6`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p008"></a>
### P008 — Evaluate inter-rater/evaluator agreement with a design matched to use

**Historical origin:** Interlaboratory precision, ICC families, method-comparison and modern evaluator studies.

**Original form:** Quantify agreement, not merely correlation, under the exact rater/evaluator sampling and decision target.

**Development:** Evolved from precision/reproducibility studies to versioned evaluator ensembles and explicit adjudication.

**Evolved form in this historical corpus:** Report disagreement structure, not only one coefficient; block governance where disagreement crosses decision boundaries.

**Problem:** Evaluators can rank cases similarly while disagreeing materially in level or pass/fail outcome.

**Mechanism:** Use paired/crossed items, blinded/randomised order, agreement-appropriate ICC/kappa/difference analyses, disagreement adjudication and subgroup checks.

**Trigger and context:** Subjective ratings, manual inspection, model judging, multi-laboratory tests, or operator-dependent measurements.

**Preconditions:** Representative difficult/easy items, sufficient rater diversity, stable rubric, and a declared agreement target.

**Measurement preconditions:** Raters/evaluators are independent enough to expose variation rather than copied or trained on identical answers.

**Assumptions:** The selected agreement statistic matches fixed/random raters, absolute agreement/consistency and scale properties.

**Decision or consumer:** Test owner, adjudicator, quality gate and downstream experimenter.

**Nontrigger or cheaper adequate path:** A deterministic reference rule with auditable outputs may need spot verification rather than a full agreement study.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Using Pearson correlation; prevalence-sensitive kappa without context; shared rubric bias; adjudicating after seeing candidate identity.

**Criticism:** The property is bounded by its stated assumptions and known failures: Using Pearson correlation; prevalence-sensitive kappa without context; shared rubric bias; adjudicating after seeing candidate identity. Contrary evidence/limit: Agreement can be high because cases are homogeneous or decisions trivial; validity and representativeness remain separate.

**Contrary evidence:** Agreement can be high because cases are homogeneous or decisions trivial; validity and representativeness remain separate.

**Unresolved questions:** How much independent evaluator diversity is needed before agreement adds evidence rather than multiplicity theatre?

**Property versus ceremony:** A fashionable reliability coefficient or arbitrary cutoff is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S024; S059; S057

**Critical source identities:** S027; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/7`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p009"></a>
### P009 — Test measurement invariance and transport across contexts

**Historical origin:** Interlaboratory comparison, psychometric invariance, dataset-shift analysis and robust measurement practice.

**Original form:** Check whether the same score has the same interpretation across sites, populations, environments, versions or time.

**Development:** Evolved from interlaboratory reproducibility to formal invariance, calibration transport and shift monitoring.

**Evolved form in this historical corpus:** Claim equivalence only over tested contexts; otherwise maintain context-specific calibration or explicit uncertainty.

**Problem:** A metric may be stable locally yet change meaning under population mix, language, hardware, operator or deployment context.

**Mechanism:** Specify transport claim, compare calibration/error/construct structure across contexts, and restrict claims or recalibrate when invariance fails.

**Trigger and context:** Cross-site benchmarking, longitudinal monitoring, heterogeneous users, distribution shift or environment changes.

**Preconditions:** Comparable reference outcomes, sufficient overlap/coverage, versioned context metadata and a plausible transport model.

**Measurement preconditions:** The measurement process and sampling frame are observable enough to distinguish construct shift from composition shift.

**Assumptions:** Observed contexts span the intended deployment; unobserved effect modifiers are bounded or acknowledged.

**Decision or consumer:** Benchmark owner, product/system decision maker, regulator or cross-site analyst.

**Nontrigger or cheaper adequate path:** No invariance study is needed for an explicitly local, one-time decision that makes no comparison beyond its validated context.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Aggregate invariance hiding subgroup failure; recalibration on contaminated outcomes; using identical preprocessing as proof of meaning.

**Criticism:** The property is bounded by its stated assumptions and known failures: Aggregate invariance hiding subgroup failure; recalibration on contaminated outcomes; using identical preprocessing as proof of meaning. Contrary evidence/limit: No finite study guarantees future invariance under open-ended distribution shift; monitoring and bounded claims are required.

**Contrary evidence:** No finite study guarantees future invariance under open-ended distribution shift; monitoring and bounded claims are required.

**Unresolved questions:** Which context dimensions must be covered before a metric can support a general engineering claim?

**Property versus ceremony:** One global score or normalisation recipe is ceremony when meanings differ.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S027; S057; S099

**Critical source identities:** S039; S038

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/8`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p010"></a>
### P010 — Monitor evaluator/instrument drift and require independent recalibration evidence

**Historical origin:** Check standards and measurement assurance, control of calibration systems, longitudinal rater/benchmark stability.

**Original form:** Treat the measurement system as a process that can drift, not a one-time certified constant.

**Development:** Evolved from physical check standards to benchmark holdouts, blind audits, bridge datasets and change-control evidence.

**Evolved form in this historical corpus:** Recalibrate when independent evidence shows measurement defect or context change; preserve old/new bridge and re-evaluate prior conclusions where material.

**Problem:** Apparent candidate/process change may be caused by aging sensors, changed operators, rubric edits, data refreshes or threshold movement.

**Mechanism:** Use stable check/reference samples, bridge studies, version control, drift limits and independent change justification before recalibration.

**Trigger and context:** Long-lived controls, automated scoring, model-based evaluators, changing laboratories or any metric with material maintenance.

**Preconditions:** Reference/check material stable enough to detect drift, bridge overlap between versions, and governance independent of candidate outcome.

**Measurement preconditions:** Check samples represent important ranges and are protected from optimisation/contamination.

**Assumptions:** Reference drift is slower or independently detectable; repeated checks are not all affected by the same environmental cause.

**Decision or consumer:** Measurement owner, release/acceptance authority and audit consumer.

**Nontrigger or cheaper adequate path:** For a one-shot destructive test with contemporaneous references, ongoing drift monitoring may be impossible; preserve calibration evidence and uncertainty instead.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Rebaselining after alarms; editing expected answers after seeing failures; check-set overfitting; no version bridge.

**Criticism:** The property is bounded by its stated assumptions and known failures: Rebaselining after alarms; editing expected answers after seeing failures; check-set overfitting; no version bridge. Contrary evidence/limit: Reference materials and holdouts can themselves age, leak or become unrepresentative; drift detection has no absolute anchor without external refresh.

**Contrary evidence:** Reference materials and holdouts can themselves age, leak or become unrepresentative; drift detection has no absolute anchor without external refresh.

**Unresolved questions:** How should old conclusions be revisited after a material evaluator recalibration?

**Property versus ceremony:** A calendar recalibration interval or automatic threshold refresh is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S015; S060; S056

**Critical source identities:** S038; S039; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/9`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p011"></a>
### P011 — Use representative reference standards and challenge shared-reference bias

**Historical origin:** Calibration artefacts, measurement assurance samples, proficiency testing and method-comparison practice.

**Original form:** Validate against references/check samples spanning the real operating range and difficult conditions.

**Development:** Evolved from physical reference artefacts to commutable samples, proficiency tests, blind holdouts and multi-method triangulation.

**Evolved form in this historical corpus:** Reference evidence is valid only for the covered range/context and must be protected from optimisation.

**Problem:** A measurement system can perform well on ideal standards while failing on routine matrices, edge cases or degraded specimens.

**Mechanism:** Select reference items by intended-use strata and failure mechanisms; use independent methods/sources where shared bias is plausible.

**Trigger and context:** Calibration transfer, evaluator validation, threshold setting and cross-site comparison.

**Preconditions:** Stable assigned values with uncertainty, representative coverage and documented provenance.

**Measurement preconditions:** Reference uncertainty and commutability/representativeness are known; reference items are not leaked into optimisation.

**Assumptions:** Sampled references cover decision-relevant variability and do not share all defects with the candidate measurement.

**Decision or consumer:** Calibration laboratory, evaluator owner and downstream decision maker.

**Nontrigger or cheaper adequate path:** For a single known artefact or exact digital identity check, one authoritative reference may be enough.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Using only pristine standards; treating consensus as truth; reusing public benchmarks until memorised; excluding failures from the reference pool.

**Criticism:** The property is bounded by its stated assumptions and known failures: Using only pristine standards; treating consensus as truth; reusing public benchmarks until memorised; excluding failures from the reference pool. Contrary evidence/limit: Representativeness cannot be proven exhaustively; rare or emerging failure modes may be absent.

**Contrary evidence:** Representativeness cannot be proven exhaustively; rare or emerging failure modes may be absent.

**Unresolved questions:** How can reference sets be refreshed without destroying longitudinal comparability or leaking the target?

**Property versus ceremony:** A named standard material or benchmark is not sufficient if it is nonrepresentative.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: MODERATE; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S060; S105; S055

**Critical source identities:** S038; S039

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/10`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p012"></a>
### P012 — Preserve data provenance, preprocessing, version and lineage

**Historical origin:** Laboratory records/traceability, reproducible analysis, adaptive-data concerns and modern data governance.

**Original form:** Record where observations came from, how they were selected/transformed, and which evaluator/code/threshold version produced each result.

**Development:** Evolved from laboratory notebooks/calibration certificates to executable pipelines, dataset/evaluator cards and contamination controls.

**Evolved form in this historical corpus:** Preserve the minimum complete lineage needed to reconstruct the evidence and its dependence structure.

**Problem:** Untracked filtering, deduplication, relabelling or evaluator changes can manufacture an apparent effect.

**Mechanism:** Use immutable identifiers, transformation logs, selection/exclusion reasons, versioned code/configuration and lineage-aware aggregation.

**Trigger and context:** Any multi-stage analysis, reused benchmark, merged source, adaptive evaluation or longitudinal comparison.

**Preconditions:** Stable identifiers, access controls, timestamp/version semantics and retention of raw or authoritative source where lawful.

**Measurement preconditions:** Preprocessing is deterministic or its randomness/configuration is recorded; lineage captures duplication and dependence.

**Assumptions:** Recorded provenance is complete enough to reconstruct decision-relevant transformations.

**Decision or consumer:** Analyst, reviewer, regulator, future maintainer and experiment consumer.

**Nontrigger or cheaper adequate path:** A small manually inspectable deterministic dataset may need only a concise signed record, not a full data platform.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Overwriting raw data; undocumented manual fixes; copied observations counted as independent; changing labels without bridge.

**Criticism:** The property is bounded by its stated assumptions and known failures: Overwriting raw data; undocumented manual fixes; copied observations counted as independent; changing labels without bridge. Contrary evidence/limit: Provenance proves what happened, not that the recorded process was unbiased or valid.

**Contrary evidence:** Provenance proves what happened, not that the recorded process was unbiased or valid.

**Unresolved questions:** What lineage granularity is sufficient to detect common-source dependence without imposing prohibitive cost?

**Property versus ceremony:** A particular tool, schema or immutable ledger is optional; reconstructability and identity are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: MODERATE; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S056; S038; S110

**Critical source identities:** S039; S040; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/11`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p013"></a>
### P013 — Model missingness, censoring, exclusions and selection mechanisms

**Historical origin:** Sampling theory, Rubin missing-data framework, reliability censoring and selective-reporting criticism.

**Original form:** Treat absence/exclusion as part of the data-generating and observation process rather than silently deleting it.

**Development:** Evolved from simple complete-case analysis to explicit missingness mechanisms, survival methods, inverse weighting/bounds and sensitivity analysis.

**Evolved form in this historical corpus:** Make the observation/selection process auditable and report conclusions conditional on or robust to plausible missingness mechanisms.

**Problem:** Failures may be missing, censored or excluded non-randomly, biasing rates, lifetimes and comparisons.

**Mechanism:** Record reasons/timing, define censoring, analyse sensitivity under plausible mechanisms, and use design/model methods only when assumptions are defensible.

**Trigger and context:** Dropout, time-limited tests, incomplete logs, destructive failures, filtered benchmark items or unobserved outcomes.

**Preconditions:** Provenance of attempted units, exposure time/opportunity, selection rule and reason codes.

**Measurement preconditions:** The system distinguishes “not observed,” “not applicable,” “failed before measurement,” and deliberate exclusion.

**Assumptions:** Chosen MAR/MCAR/censoring/selection assumptions approximate reality; sensitivity bounds cover uncertainty.

**Decision or consumer:** Reliability analyst, experimenter, quality gate and consumer of aggregate metrics.

**Nontrigger or cheaper adequate path:** If missingness is demonstrably negligible and unrelated to outcome/exposure, transparent complete-case treatment may be adequate.

**Disposition at the historical freeze:** MEASUREMENT_PRECONDITION_PROPERTY

**Failure modes:** Calling failures “invalid”; censoring at different risk states; post-hoc subgroup restriction; imputation model trained on outcome leakage.

**Criticism:** The property is bounded by its stated assumptions and known failures: Calling failures “invalid”; censoring at different risk states; post-hoc subgroup restriction; imputation model trained on outcome leakage. Contrary evidence/limit: Missing-not-at-random mechanisms are generally not identified from observed data alone; sensitivity/partial identification may be the honest endpoint.

**Contrary evidence:** Missing-not-at-random mechanisms are generally not identified from observed data alone; sensitivity/partial identification may be the honest endpoint.

**Unresolved questions:** Which missingness mechanisms are distinguishable with available auxiliary/process data?

**Property versus ceremony:** Automatic imputation or a missing-data checklist is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S020; S071; S077

**Critical source identities:** S040; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/12`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p014"></a>
### P014 — Account for measurement intervention, destruction and contamination

**Historical origin:** Destructive inspection/acceptance sampling, test-effect/carryover design, measurement assurance and sensor intrusiveness.

**Original form:** Recognise that observing can consume, stress, train, prime, cache or otherwise alter the unit/system and later evidence.

**Development:** Evolved from destructive sampling and crossover design to explicit benchmark exposure and adaptive-system contamination controls.

**Evolved form in this historical corpus:** Use fresh or counterbalanced units where material; otherwise model and report intervention history and limit claims.

**Problem:** Repeated measurements may not be exchangeable because the first test changes the candidate, operator or environment.

**Mechanism:** Classify measurement as destructive/intrusive, randomise order, use fresh units or washout/holdouts, and model carryover when unavoidable.

**Trigger and context:** Destructive material tests, accelerated stress, human/agent learning, repeated benchmark exposure, cache/warm-up effects.

**Preconditions:** Defined experimental unit, exposure history, test order, fresh-unit availability and a mechanism for intervention effects.

**Measurement preconditions:** Provenance records prior exposures and distinguishes unit reuse from independent replication.

**Assumptions:** Carryover/washout model is plausible or fresh independent units are available.

**Decision or consumer:** Experiment designer, reliability/test engineer and benchmark owner.

**Nontrigger or cheaper adequate path:** When a verified measurement is genuinely non-invasive and order-invariant, ordinary repeated-measures methods may suffice.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Calling warmed/cached retries independent; destructive test sample not representative; training on failed benchmark items; inadequate washout.

**Criticism:** The property is bounded by its stated assumptions and known failures: Calling warmed/cached retries independent; destructive test sample not representative; training on failed benchmark items; inadequate washout. Contrary evidence/limit: In adaptive systems, measurement and improvement may be inseparable by design; the goal becomes explicit online-learning evaluation rather than pretending independence.

**Contrary evidence:** In adaptive systems, measurement and improvement may be inseparable by design; the goal becomes explicit online-learning evaluation rather than pretending independence.

**Unresolved questions:** When is reuse acceptable because the deployment itself includes learning from feedback?

**Property versus ceremony:** A blanket ban on retesting is not the property; exposure-aware evidence is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S068; S048; S038

**Critical source identities:** S039; S040

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/13`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p015"></a>
### P015 — Discriminate routine/common variation from evidence of a changed process

**Historical origin:** Shewhart’s Bell Labs statistical control and later common/special-cause translation.

**Original form:** Use time-ordered evidence to distinguish an approximately stable pattern from departures worth investigation.

**Development:** Evolved from Shewhart charts to CUSUM/EWMA, time-series/residual, change-point and context-specific monitoring with explicit costs.

**Evolved form in this historical corpus:** Use the lightest calibrated discriminator that separates expected variation from actionable change, then require causal investigation before intervention.

**Problem:** Treating every fluctuation as actionable or averaging away a real process change.

**Mechanism:** Establish a relevant baseline, plot/model observations in time order, use calibrated signals, and investigate mechanisms rather than equate alarms with causes.

**Trigger and context:** Repeated process output where a stable-enough reference regime and actionable changes are plausible.

**Preconditions:** Defined process/stream, chronological data, adequate measurement, comparable opportunities and a consequence-linked response plan.

**Measurement preconditions:** Measurement error is small enough and evaluator drift is separated from process drift.

**Assumptions:** The baseline is sufficiently homogeneous/stable for the chosen chart/model; dependence and mixtures are handled.

**Decision or consumer:** Process owner and investigator—not a mechanism-free automated punishment system.

**Nontrigger or cheaper adequate path:** For a deterministic failure with an authoritative cause, repair it directly; for one-off heterogeneous work with no repeatable unit, causal case analysis may dominate charting.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Control limits treated as specs; alarms treated as causes; retrospective cherry-picking; rebaselining away failures; worker blame.

**Criticism:** The two-cause vocabulary can oversimplify continuous, interacting and drifting sources; “special” is statistical, not moral or personal.

**Contrary evidence:** In highly adaptive or nonstationary systems there may be no enduring common-cause baseline; change detection must be reframed around local regimes or forecasts.

**Unresolved questions:** What level of local stability is sufficient for useful monitoring in continuously changing systems?

**Property versus ceremony:** The property is discrimination and response discipline, not putting every metric on a three-sigma chart.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S001; S002; S003

**Critical source identities:** S030; S031; S032

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/14`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p016"></a>
### P016 — Choose rational subgroups and model dependence rather than count correlated observations as sample size

**Historical origin:** Shewhart subgroup logic, time-series SPC and pseudoreplication criticism.

**Original form:** Arrange within/between-group comparisons so the statistic reflects the variation source relevant to the decision.

**Development:** Evolved from subgroup construction rules to hierarchical/time-series/cluster-robust modelling and explicit effective sample size.

**Evolved form in this historical corpus:** Match the unit of evidence and correlation model to the unit of action; disclose residual dependence.

**Problem:** Subgroups can mix different regimes or repeated readings can masquerade as independent evidence.

**Mechanism:** Define the process unit and correlation structure; subgroup items exposed to common short-term conditions when that answers the decision, or use cluster/time-series models.

**Trigger and context:** Batch, lot, repeated-run, time-series, nested, clustered or same-seed/same-environment observations.

**Preconditions:** Process map, timestamps/batch/seed/operator identifiers, enough clusters/subgroups and a defensible within/between variation interpretation.

**Measurement preconditions:** Measurement repeats are labelled separately from production units; common-source dependence is observable.

**Assumptions:** Within-subgroup homogeneity and between-subgroup opportunity for relevant change, or a valid dependence model.

**Decision or consumer:** Monitoring designer, experimenter and evidence consumer.

**Nontrigger or cheaper adequate path:** When observations are demonstrably independent and identically produced at the decision scale, ordinary independent analysis is adequate.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Convenience subgroups; averaging across shifts; treating multiple outputs from one run as independent; one cluster per condition.

**Criticism:** “Rational subgroup” is not a magic recipe; it encodes a causal/process judgement and may fail in low-volume/high-mix work.

**Contrary evidence:** Dependence can be difficult to estimate with few clusters or changing correlation; conservative bounds may be preferable to elaborate fitted models.

**Unresolved questions:** How should evidence be discounted when shared prompts, seeds, fixtures or upstream data create partially known dependence?

**Property versus ceremony:** Fixed subgroup sizes or an X-bar/R worksheet are implementation choices, not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S002; S023; S026

**Critical source identities:** S030; S031; S067

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/15`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p017"></a>
### P017 — Keep statistical control limits separate from engineering specifications and tolerances

**Historical origin:** Shewhart control charts, engineering tolerancing and metrological conformity assessment.

**Original form:** Control limits describe expected process behaviour; specifications define required/allowed performance.

**Development:** Evolved toward explicit uncertainty-aware conformity rules and capability conditional on stability.

**Evolved form in this historical corpus:** Use control limits for change detection, specifications for requirements, and guard bands/decision rules for uncertain conformance.

**Problem:** A process can be stable yet unacceptable, or unstable while all observed outputs remain inside specification.

**Mechanism:** Maintain separate provenance and semantics for natural-process limits, specification/tolerance limits and uncertainty/guard bands.

**Trigger and context:** Any monitored characteristic with both process history and an external requirement.

**Preconditions:** Authoritative specification, stable-enough process baseline, adequate measurement and explicit conformance decision rule.

**Measurement preconditions:** Uncertainty near specifications is quantified; specification source/version is fixed.

**Assumptions:** Control-limit estimation reflects the intended baseline; specs are independent of recent sample behaviour.

**Decision or consumer:** Process owner, design authority, customer/regulator and conformance decision maker.

**Nontrigger or cheaper adequate path:** For an exact deterministic requirement checked once, a control chart may be unnecessary; use the specification directly with measurement uncertainty.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Setting control limits equal to specs; widening limits to keep data “in control”; treating any in-spec point as evidence of stability.

**Criticism:** Three-sigma conventions are not tolerances, and neither system identifies root cause.

**Contrary evidence:** Specifications themselves may be poorly justified or gamed; statistical separation does not validate the requirement.

**Unresolved questions:** How should dynamic/adaptive specifications be governed without turning every threshold movement into process redefinition?

**Property versus ceremony:** One dashboard may display all limits, but their meanings must not be merged.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S001; S053; S062

**Critical source identities:** S031; S103

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/16`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p018"></a>
### P018 — Establish process stability before interpreting capability or long-run prediction

**Historical origin:** Shewhart statistical control, process characterisation and modern capability standards.

**Original form:** Assess whether the process exhibits sufficiently consistent behaviour before summarising its capability against specifications.

**Development:** Evolved from a binary in/out-of-control prerequisite to local, conditional and time-dependent capability models.

**Evolved form in this historical corpus:** State the regime and prediction horizon; no unconditional capability claim from unresolved drift/mixture.

**Problem:** A single capability index can average multiple regimes, trends or special causes into a misleading number.

**Mechanism:** Use time order, change/mixture checks and process knowledge; if unstable, model regimes or improve/contain before issuing a capability claim.

**Trigger and context:** Capability, tolerance yield, long-run defect rate or predictive performance claims.

**Preconditions:** Adequate measurement, chronological data, stable specification and enough observations across normal operating conditions.

**Measurement preconditions:** Evaluator/measurement process is itself stable and capable enough to observe process change.

**Assumptions:** Future conditions reasonably resemble the characterised regime or are explicitly modelled.

**Decision or consumer:** Process/design owner, supplier/customer and regulator.

**Nontrigger or cheaper adequate path:** For a deterministic design proof or 100% authoritative inspection, a statistical capability index may be irrelevant.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Shuffled data; pooled shifts/products; one favourable window; rebaselined outliers; no evaluator-stability check.

**Criticism:** Finite data cannot prove permanent stability; “stable enough for this prediction horizon” is the mature claim.

**Contrary evidence:** Some systems are intentionally nonstationary; capability may need scenario/conditional performance rather than a single process distribution.

**Unresolved questions:** What constitutes adequate local stability for adaptive systems with planned policy changes?

**Property versus ceremony:** A mandatory chart is not necessary if equivalent stability evidence exists; the prerequisite is evidential.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S002; S062; S109

**Critical source identities:** S031; S064

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/17`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p019"></a>
### P019 — Use capability indices only conditionally on stability, distribution and measurement fitness

**Historical origin:** Process capability analysis, normal-theory indices and ISO 22514 evolution.

**Original form:** Compare process location/spread with specification width using indices such as Cp/Cpk under stated conditions.

**Development:** NIST and ISO narrow capability to stable/in-control or time-dependent models; modern practice reports conditions and uncertainty.

**Evolved form in this historical corpus:** A conditional summary—not evidence of control, causality or universal “sigma level.”

**Problem:** A convenient scalar can hide skew, tails, drift, measurement error, centring and subgroup structure.

**Mechanism:** Verify prerequisites; report distribution-free/empirical or model-based alternatives and uncertainty; keep indices subordinate to raw/time-ordered evidence.

**Trigger and context:** High-volume repeatable processes where a stable distribution and specification-based decision exist.

**Preconditions:** P018 stability, P002 measurement fitness, representative independent data, stable specification and an adequate distribution/tail model.

**Measurement preconditions:** Measurement variation is small or incorporated; rounding/censoring do not dominate.

**Assumptions:** Selected index/distribution describes the regime and tail behaviour; sample size supports intended precision.

**Decision or consumer:** Process engineer, supplier/customer and quality planner.

**Nontrigger or cheaper adequate path:** Use direct yield/tolerance evidence, deterministic limits, or scenario-specific performance when assumptions fail or sample is tiny.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Cpk on unstable data; normal DPMO conversion under skew/dependence; ignoring confidence intervals; choosing the most favourable index.

**Criticism:** The property is bounded by its stated assumptions and known failures: Cpk on unstable data; normal DPMO conversion under skew/dependence; ignoring confidence intervals; choosing the most favourable index. Contrary evidence/limit: Tail defect-rate claims can be dominated by model error far beyond observed data; index precision is not tail certainty.

**Contrary evidence:** Tail defect-rate claims can be dominated by model error far beyond observed data; index precision is not tail certainty.

**Unresolved questions:** When should capability be expressed as scenario-specific prediction intervals rather than a scalar index?

**Property versus ceremony:** The index and threshold are optional tools; margin/yield evidence under valid assumptions is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S062; S063; S064

**Critical source identities:** S031; S032; S084

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/18`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p020"></a>
### P020 — Prevent tampering and overadjustment to routine variation

**Historical origin:** Shewhart economic control and Deming’s later funnel/tampering translation.

**Original form:** Do not alter a stable process in response to fluctuations lacking evidence of an actionable change.

**Development:** Evolved into explicit feedback design, intervention analysis and separation of monitoring from experimentation.

**Evolved form in this historical corpus:** No reactive adjustment without a discriminator or planned experiment whose expected value exceeds intervention risk.

**Problem:** Feedback to noise adds variance, oscillation, bias and instability.

**Mechanism:** Define when adjustment is authorised, use calibrated signals/mechanism evidence, and evaluate interventions against a stable baseline or experiment.

**Trigger and context:** Feedback-controlled processes, manual tuning, metric dashboards, repeated reviews and near-threshold variation.

**Preconditions:** Measurement fitness, action rule, process response knowledge, and ability to distinguish intervention from observation noise.

**Measurement preconditions:** The metric is stable enough that an adjustment response is not triggered by evaluator noise.

**Assumptions:** Unadjusted process has a meaningful baseline and feedback dynamics are understood enough to avoid instability.

**Decision or consumer:** Operator, process owner and change authority.

**Nontrigger or cheaper adequate path:** Correct an authoritative deterministic defect immediately; no statistical wait is needed when mechanism/effect is known.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Changing settings after every bad point; rewarding short regression-to-mean; retuning evaluator after candidate failure; local optimisation.

**Criticism:** “Do not tamper” must not become “never improve”; designed experiments deliberately change a process under controlled learning.

**Contrary evidence:** In rapidly drifting environments, delayed adaptation can be worse than overadjustment; adaptive control must model that trade-off.

**Unresolved questions:** How should tampering risk be balanced against concept drift when the optimal policy is itself nonstationary?

**Property versus ceremony:** A fixed run rule is not the property; disciplined response to evidence is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S002; S003; S089

**Critical source identities:** S031; S066

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/19`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p021"></a>
### P021 — Design monitoring economically around false-alarm, missed-shift and delay costs

**Historical origin:** Shewhart economic control, Duncan economic chart design, CUSUM/EWMA operating characteristics and decision analysis.

**Original form:** Choose sampling frequency, statistic and threshold according to consequential shifts and error/delay costs.

**Development:** Evolved from fixed three-sigma practice to target-shift optimisation, simulations, Bayesian/decision rules and service-capacity-aware alerting.

**Evolved form in this historical corpus:** Select the smallest monitoring design that detects decision-relevant change at acceptable false-alarm/delay cost.

**Problem:** More sensitive rules can flood operators; conservative rules can miss costly small shifts.

**Mechanism:** Define target changes, in-control/out-of-control models or simulations, ARL/delay/precision and consequence-weighted action costs.

**Trigger and context:** Ongoing monitoring with repeated opportunities, finite response capacity and quantifiable consequences.

**Preconditions:** Actionable response plan, baseline, measurement capability, realistic shift scenarios and cost/risk owner.

**Measurement preconditions:** Sampling/measurement burden and false-alarm mechanisms are known; alerts can be investigated.

**Assumptions:** Operating-characteristic calculations approximate real dependence/nonstationarity and cost model includes tail consequences.

**Decision or consumer:** Monitoring designer, operator and risk/economic decision owner.

**Nontrigger or cheaper adequate path:** For rare high-consequence events with a deterministic safety interlock, use the interlock; for low-cost obvious defects, direct inspection may dominate statistical detection.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Stacking Western Electric rules without capacity; tuning on known incidents; no alert disposition; sampling quota detached from value.

**Criticism:** Economic design is powerful but assumption-sensitive and must incorporate non-economic constraints where relevant.

**Contrary evidence:** Cost and shift distributions are often uncertain; robust/minimax or scenario designs may be more honest than a single optimum.

**Unresolved questions:** How should monitoring be tuned when missed rare events have poorly quantifiable catastrophic loss?

**Property versus ceremony:** Three sigma, eight run rules or a dashboard cadence are not universal properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S014; S013; S065

**Critical source identities:** S031; S066

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/20`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p022"></a>
### P022 — Adapt monitoring to autocorrelation, seasonality, drift and nonstationarity

**Historical origin:** Time-series SPC, residual charts, dynamic models, change-point methods and updated time-dependent capability standards.

**Original form:** Replace naive iid chart assumptions with a model or discriminator appropriate to temporal structure and evolving regimes.

**Development:** Evolved from stationary Shewhart limits to local/regime-aware monitoring, forecast residuals, CUSUM/EWMA and online change detection.

**Evolved form in this historical corpus:** Use a transparent dynamic baseline with validated detection properties and explicit rebaseline/change-control rules.

**Problem:** Serial dependence changes false-alarm/detection properties; trends and seasonality can look like special causes or mask them.

**Mechanism:** Model/stratify predictable structure, monitor residuals/forecast errors or use robust change-point methods; validate under simulation/backtests and maintain drift governance.

**Trigger and context:** Metrics with temporal dependence, seasonality, learning curves, policy changes or concept drift.

**Preconditions:** Enough history/regimes, stable measurement versions, time metadata, intervention records and a prediction/action horizon.

**Measurement preconditions:** Evaluator/context changes are versioned; missingness and changing exposure denominators are handled.

**Assumptions:** Dynamic model/residuals capture enough structure; change-point method’s calibration approximates deployment.

**Decision or consumer:** Process owner, forecasting/monitoring team and policy controller.

**Nontrigger or cheaper adequate path:** A large deterministic discontinuity can be handled directly; sparse heterogeneous events may need case-based analysis rather than fitted time series.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Fitting seasonality after every alarm; residuals with hidden model failure; changing mixtures; no intervention annotation.

**Criticism:** No universal evolved chart exists; classical methods are narrowed, not simply replaced.

**Contrary evidence:** Under adversarial or abrupt concept change, historical calibration may fail exactly when needed; guarantees are local/conditional.

**Unresolved questions:** How can drift detectors distinguish benign adaptation, population change, evaluator change and harmful process degradation?

**Property versus ceremony:** “Use an AI anomaly detector” is not the property; calibrated discrimination and interpretable response remain required.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S026; S030; S067

**Critical source identities:** S031; S064

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/21`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p023"></a>
### P023 — Stratify mixtures, high-mix/low-volume and changing populations before aggregation

**Historical origin:** Rational subgrouping, stratification, short-run SPC and mixture-distribution criticism.

**Original form:** Do not pool unlike products, contexts, users or opportunity structures unless the aggregate answers the decision.

**Development:** Evolved from physical product family grouping to hierarchical/partial-pooling and mix-adjusted monitoring.

**Evolved form in this historical corpus:** Show both relevant strata and an explicitly weighted aggregate; freeze/justify weighting and monitor composition.

**Problem:** Composition change can create or hide trends even when every component is unchanged.

**Mechanism:** Define comparable strata or standardise/model mix; use short-run/standardised charts only with justified transformations and preserve component views.

**Trigger and context:** High-mix low-volume production, heterogeneous workloads, changing severity/population or sparse per-type data.

**Preconditions:** Product/context identifiers, enough data or engineering standards for normalisation, and a clear aggregate decision.

**Measurement preconditions:** Measurement is invariant or separately calibrated across strata.

**Assumptions:** Within-stratum models or standardisation preserve relevant tail/interaction behaviour; no hidden confounding remains.

**Decision or consumer:** Portfolio/process owner and consumers of aggregate dashboards.

**Nontrigger or cheaper adequate path:** If all units share the same decision distribution and mixture is stable/irrelevant, aggregate monitoring may be the cheapest valid path.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Dropping hard categories; changing denominator; z-scoring incomparable tails; one global control limit; post-hoc subgroup hunting.

**Criticism:** Short-run charts help but are domain-specific and assumption-sensitive; hierarchical pooling may be preferable.

**Contrary evidence:** With very sparse strata, estimates depend strongly on hierarchical priors/model sharing; no purely data-driven partition is definitive.

**Unresolved questions:** How should partial pooling be governed when local safety tails matter more than overall efficiency?

**Property versus ceremony:** A mandatory chart per SKU or one universal standardised score are both ceremonial extremes.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S002; S067; S107

**Critical source identities:** S031; S099

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/22`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p024"></a>
### P024 — Use context-adapted multivariate, rare-event, short-run or change-point monitoring only when its added discrimination pays

**Historical origin:** CUSUM/EWMA, multivariate SPC, attribute/rare-event charts, short-run methods and modern change detection.

**Original form:** Choose a monitoring statistic matched to event type, dimension, baseline size and target change rather than force a classical chart.

**Development:** Extensions retain the underlying discrimination property but remain domain/model-specific.

**Evolved form in this historical corpus:** Adopt only after showing incremental decision value over a cheap baseline, with interpretable follow-up and recalibration rules.

**Problem:** Univariate normal charts can miss joint shifts, mis-handle sparse events, or be unusable with one-off/high-mix output.

**Mechanism:** Specify the change/event to detect, compare candidate methods by simulated/empirical operating characteristics, and keep a causal/actionable interpretation.

**Trigger and context:** Multivariate correlated measurements, rare defects, variable exposure, small shifts, low volume or abrupt change points.

**Preconditions:** Stable measurement, exposure denominators, enough baseline or engineering prior, response plan and computational/interpretive capacity.

**Measurement preconditions:** Input variables retain meaning and covariance/event models are adequate enough for threshold calibration.

**Assumptions:** Selected detector’s null/change model or robust calibration approximates use; multiplicity across monitored features is controlled.

**Decision or consumer:** Monitoring team and incident/process owner.

**Nontrigger or cheaper adequate path:** Use a direct rule or simple stratified count when the event is obvious and data too sparse to estimate a complex model.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Hotelling score without diagnosis; Poisson chart under overdispersion; zero-event reassurance; model retrained after every alarm.

**Criticism:** The property is bounded by its stated assumptions and known failures: Hotelling score without diagnosis; Poisson chart under overdispersion; zero-event reassurance; model retrained after every alarm. Contrary evidence/limit: Rare-event detector performance is often weakly estimable; simulation depends on an assumed tail/model and can create false certainty.

**Contrary evidence:** Rare-event detector performance is often weakly estimable; simulation depends on an assumed tail/model and can create false certainty.

**Unresolved questions:** What evidence threshold is sufficient to deploy a complex detector when incidents are too rare for direct validation?

**Property versus ceremony:** Having a multivariate/anomaly model is not a general property; validated added discrimination is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S013; S061; S107; S108

**Critical source identities:** S030; S031; S073

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/23`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p025"></a>
### P025 — Design sampling to represent the decision population and selection process

**Historical origin:** Probability sampling, industrial inspection, survey/experimental design and modern dataset-shift analysis.

**Original form:** Define the target population/opportunity frame and select units so inclusion supports the intended inference.

**Development:** Evolved toward risk-stratified, cluster-aware, importance-weighted and shift-monitored sampling while preserving explicit target definition.

**Evolved form in this historical corpus:** Use the cheapest design that either represents the target or honestly limits the claim; retain all attempted-unit provenance.

**Problem:** A large convenient sample can be systematically unrepresentative, duplicated or selected after outcomes are visible.

**Mechanism:** Specify frame, inclusion probabilities or explicit selection model; stratify high-risk/rare groups; document exclusions and compare sample to target.

**Trigger and context:** Any inference beyond the exactly observed units, especially acceptance, prevalence, reliability or benchmark claims.

**Preconditions:** Defined target population, unit/opportunity, frame coverage, provenance and a plan for nonresponse/missingness.

**Measurement preconditions:** Measurement meaning is invariant enough across sampled and target contexts; duplicates and clusters are identified.

**Assumptions:** Probability or selection-model assumptions hold sufficiently; unobserved selection is bounded or disclosed.

**Decision or consumer:** Experimenter, quality/reliability analyst, customer/regulator and benchmark consumer.

**Nontrigger or cheaper adequate path:** For exhaustive authoritative enumeration of the entire relevant population, statistical sampling is unnecessary; verify completeness/identity instead.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Public/easy cases only; post-failure exclusion; duplicated source records; favourable time window; target population left implicit.

**Criticism:** Probability sampling does not repair invalid measurement, and nonprobability samples can still support bounded local decisions if claims are restricted.

**Contrary evidence:** Open-ended deployment populations cannot be fully represented in advance; monitoring and scenario coverage remain necessary.

**Unresolved questions:** How should rare catastrophic strata be oversampled while preserving interpretable overall estimates?

**Property versus ceremony:** A sample-size quota without a target/frame is ceremony.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S045; S020; S068

**Critical source identities:** S039; S099

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/24`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p026"></a>
### P026 — Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it

**Historical origin:** Dodge–Romig Bell Labs sampling inspection, wartime/industrial standards and current ISO 2859.

**Original form:** Accept or reject a lot using a prespecified sampling plan with producer/consumer operating risks.

**Development:** Modern standards retain the tool but explicitly limit it to acceptance decisions, not process estimation or prevention.

**Evolved form in this historical corpus:** A domain-specific decision procedure with transparent OC/risk—not a universal quality property.

**Problem:** 100% inspection may be destructive, too slow, too expensive or itself error-prone.

**Mechanism:** Choose plan by lot structure, AQL/LQ or OC requirements, inspection error and cost; preserve switching/traceability and disposition semantics.

**Trigger and context:** Incoming/outgoing lots with meaningful lot identity, relatively stable supply and costly/destructive inspection.

**Preconditions:** Defined lot, random sample, valid attribute/variable measurement, prespecified plan and clear producer/consumer risk.

**Measurement preconditions:** Inspection error is small or included; sample selection cannot be manipulated.

**Assumptions:** Within-lot heterogeneity and production history are compatible with the plan; standard’s switching rules/context apply.

**Decision or consumer:** Purchaser/supplier, release authority and regulator.

**Nontrigger or cheaper adequate path:** Use 100% deterministic inspection when cheap/reliable; use process control/improvement when the goal is future quality rather than one-lot disposition.

**Disposition at the historical freeze:** DOMAIN_SPECIFIC

**Failure modes:** AQL interpreted as a guarantee; nonrandom sample; lot splitting; plan chosen after results; inspection error ignored.

**Criticism:** The property is bounded by its stated assumptions and known failures: AQL interpreted as a guarantee; nonrandom sample; lot splitting; plan chosen after results; inspection error ignored. Contrary evidence/limit: Changing lot composition, adversarial suppliers and severe item heterogeneity can invalidate nominal OC risks.

**Contrary evidence:** Changing lot composition, adversarial suppliers and severe item heterogeneity can invalidate nominal OC risks.

**Unresolved questions:** When do modern automated inspections make classical sampling economically obsolete?

**Property versus ceremony:** ISO table use or a named MIL-STD plan is an implementation; bounded risk-based lot disposition is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S008; S068; S069

**Critical source identities:** S070; S027

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/25`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p027"></a>
### P027 — Do not use acceptance sampling as a substitute for process understanding, prevention or improvement

**Historical origin:** Limits recognised in acceptance-sampling handbooks and the shift from end inspection toward process control/prevention.

**Original form:** Separate transaction screening from evidence about why a process generates defects and how future output will behave.

**Development:** The evolved form retains acceptance sampling only as one control layer, subordinated to prevention and feedback.

**Evolved form in this historical corpus:** Use sampling for the decision it can make; do not infer control, capability or cause from acceptance alone.

**Problem:** Passing lots can coexist with a poor, drifting or gamed process; rejected lots do not identify the cause.

**Mechanism:** Pair lot disposition with supplier/process feedback, time-ordered defect analysis, corrective action or designed improvement where economically justified.

**Trigger and context:** Repeated supply/production where future quality matters, not merely one isolated transaction.

**Preconditions:** Lot and process identities linked, defect provenance retained, and process owner able to act.

**Measurement preconditions:** Measurement system distinguishes defects and records failure modes rather than only pass/fail totals.

**Assumptions:** Lot outcomes contain some information about process, but causal diagnosis requires additional evidence.

**Decision or consumer:** Supplier/process owner, procurement and improvement team.

**Nontrigger or cheaper adequate path:** For a one-off purchase with no leverage or future process, bounded acceptance sampling may be all that is rational.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Discarding rejected-lot data; treating AQL as target; supplier adjusts lot formation; no root-cause evidence.

**Criticism:** The property is bounded by its stated assumptions and known failures: Discarding rejected-lot data; treating AQL as target; supplier adjusts lot formation; no root-cause evidence. Contrary evidence/limit: For highly regulated or destructive products, acceptance evidence may remain necessary even with excellent process control.

**Contrary evidence:** For highly regulated or destructive products, acceptance evidence may remain necessary even with excellent process control.

**Unresolved questions:** What combination of process evidence and lot inspection minimises total risk under supplier/adversarial uncertainty?

**Property versus ceremony:** Acceptance forms/tables are not process-improvement properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S068; S070; S090

**Critical source identities:** S031; S084

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/26`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p028"></a>
### P028 — Size samples around effect/precision, dependence and decision loss—not a universal count

**Historical origin:** Neyman–Pearson power, estimation precision, sampling theory, cluster design and reliability bounds.

**Original form:** Choose information volume from the smallest meaningful effect or required precision, error costs, variance, design and stopping plan.

**Development:** Evolved from fixed-horizon power calculations toward precision, simulation, sequential/decision-theoretic and assurance approaches.

**Evolved form in this historical corpus:** Plan for the independent information needed to discriminate the decision, update only under a valid sequential/adaptive protocol.

**Problem:** Too few independent units miss meaningful effects; many dependent or biased units create only false precision.

**Mechanism:** Specify decision margin, alpha/beta or interval width/utility, estimate design effects, use simulation/sensitivity, and distinguish units from repeated measurements.

**Trigger and context:** Sampling/experiment/reliability decisions where uncertainty influences action.

**Preconditions:** Defined estimand/decision, plausible variance/effect range, independent-unit structure, multiplicity/stopping plan and feasible measurement.

**Measurement preconditions:** Measurement error and missingness are included in effective information; pilot estimates are not treated as exact.

**Assumptions:** Planning model approximates design; effect threshold is engineering-justified; clusters/dependence known enough.

**Decision or consumer:** Experiment owner, risk owner and resource allocator.

**Nontrigger or cheaper adequate path:** No sample-size calculation is needed when a deterministic proof/check resolves the decision or when a pilot’s only goal is feasibility discovery.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Counting repeated readings as n; planning on observed pilot effect; stopping when significant; ignoring multiplicity/attrition.

**Criticism:** The property is bounded by its stated assumptions and known failures: Counting repeated readings as n; planning on observed pilot effect; stopping when significant; ignoring multiplicity/attrition. Contrary evidence/limit: Rare catastrophic outcomes may require physical/structural evidence, conservative bounds or stress models because feasible samples cannot directly validate target rates.

**Contrary evidence:** Rare catastrophic outcomes may require physical/structural evidence, conservative bounds or stress models because feasible samples cannot directly validate target rates.

**Unresolved questions:** How should sample planning combine epistemic uncertainty in variance/effect with asymmetric catastrophic loss?

**Property versus ceremony:** “30 samples,” “10 runs,” or “80% power” without a decision model is ceremony.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S007; S046; S075

**Critical source identities:** S023; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/27`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p029"></a>
### P029 — Frame experiments around an explicit engineering decision, estimand and rival alternatives

**Historical origin:** Fisherian experiment purpose, Neyman–Pearson specified alternatives, causal estimands and statistical engineering.

**Original form:** State what contrast/effect/population and action the experiment is intended to discriminate before selecting a test.

**Development:** Evolved from hypothesis testing toward explicit estimands, decision margins, rival models and staged exploration/confirmation.

**Evolved form in this historical corpus:** No experiment begins as “run a test”; it begins with the decision it can change and the cheapest evidence that discriminates it.

**Problem:** A technically valid analysis can answer an irrelevant null, average over decisive heterogeneity, or lack an action consequence.

**Mechanism:** Define decision, estimand, experimental unit, rival explanations, smallest consequential effect, validity scope and stopping/analysis plan.

**Trigger and context:** Any nontrivial comparison or intervention whose result may change design, release, allocation or policy.

**Preconditions:** Stakeholder/engineering loss, target population, manipulable treatment/design alternatives and measurable outcome.

**Measurement preconditions:** Outcome is valid and sensitive enough; unit/assignment/exposure can be identified.

**Assumptions:** The chosen estimand maps to the decision and potential outcomes/comparisons are meaningful.

**Decision or consumer:** Design authority, product/process owner and risk/resource decision maker.

**Nontrigger or cheaper adequate path:** For an exact authoritative check or exploratory feasibility probe, a formal estimand/test may be unnecessary; label the evidence accordingly.

**Disposition at the historical freeze:** EXPERIMENTAL_DESIGN_PROPERTY

**Failure modes:** Null of exactly zero; endpoint switched after results; no target population; average effect hides catastrophic subgroup.

**Criticism:** No universal formalism resolves normative loss or construct definition; exploratory and confirmatory phases may differ.

**Contrary evidence:** Some engineering discovery is necessarily open-ended; the mature boundary is transparent separation of exploration from decision-confirming evidence.

**Unresolved questions:** How should multi-objective engineering decisions state estimands without hiding value trade-offs in a scalar?

**Property versus ceremony:** A preregistration form or test name is optional; frozen decision/estimand boundaries are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S005; S007; S018

**Critical source identities:** S033; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/28`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p030"></a>
### P030 — Use randomisation to protect causal comparisons against assignment bias and support valid error assessment

**Historical origin:** Fisher’s field experiments, randomised experiments and potential-outcomes causal inference.

**Original form:** Allocate experimental units by a known chance mechanism so treatment is not systematically confounded with observed/unobserved pre-treatment factors.

**Development:** Evolved into cluster, stratified, covariate-adaptive and online randomisation with transparent assignment logs.

**Evolved form in this historical corpus:** Randomise when it materially reduces causal ambiguity; preserve assignment integrity and analyse the design actually run.

**Problem:** Convenient or outcome-informed assignment can make association look causal.

**Mechanism:** Randomise at the correct unit, conceal/record allocation, account for restrictions/clusters, and analyse according to the actual assignment.

**Trigger and context:** When interventions are feasible and the causal effect matters.

**Preconditions:** Defined experimental unit, feasible comparable conditions, stable measurement, compliance/exposure records and enough independent assignments.

**Measurement preconditions:** Outcome ascertainment is blinded or otherwise protected from allocation bias where possible.

**Assumptions:** No unmodelled interference/carryover; randomisation is implemented, not merely planned; attrition does not undo comparability.

**Decision or consumer:** Experimenter, design/process owner and causal decision consumer.

**Nontrigger or cheaper adequate path:** Randomisation is unnecessary for deterministic mechanism verification and may be infeasible/unethical; strong natural/quasi-experimental or mechanistic evidence can be used with narrower claims.

**Disposition at the historical freeze:** EXPERIMENTAL_DESIGN_PROPERTY

**Failure modes:** Randomising observations instead of units; deterministic seed reused; allocation predictable; post-randomisation exclusions; interference ignored.

**Criticism:** Randomisation does not solve invalid measurement, low power, noncompliance, spillover, external validity or poor estimands.

**Contrary evidence:** Randomised effects may not transport beyond sampled units/context, and operational noncompliance can change the estimand.

**Unresolved questions:** When is mechanism-plus-observational evidence decision-sufficient despite infeasible randomisation?

**Property versus ceremony:** “A/B test” branding or a random seed alone is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: VERY_HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: VERY_HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S005; S006; S018

**Critical source identities:** S047; S048

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/29`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p031"></a>
### P031 — Block or stratify known nuisance variation without erasing interactions

**Historical origin:** Fisher’s local control/blocking, factorial design and modern stratified/randomised experiments.

**Original form:** Group or balance experimental units on nuisance factors before randomisation/analysis to reduce unexplained variance and confounding.

**Development:** Modern practice combines blocking with regression/hierarchical adjustment but retains design-stage protection.

**Evolved form in this historical corpus:** Block what is known and costly, randomise what remains, and report context interactions rather than only an adjusted average.

**Problem:** Batch, time, operator, hardware, site or baseline severity can obscure or mimic treatment effects.

**Mechanism:** Select a few consequential pre-treatment factors, block/stratify randomisation and estimate block/treatment interactions when relevant.

**Trigger and context:** Heterogeneous units or expensive experiments where nuisance variation is large relative to target effect.

**Preconditions:** Known pre-treatment covariates, enough units per block or matched-pair structure, and stable measurement.

**Measurement preconditions:** Blocking variables are measured before intervention without candidate-induced bias.

**Assumptions:** Within-block comparisons remain meaningful; block definitions are not chosen after outcomes.

**Decision or consumer:** Experimenter and engineering decision owner.

**Nontrigger or cheaper adequate path:** Do not block on post-treatment variables or add complexity when units are already homogeneous and the effect is obvious.

**Disposition at the historical freeze:** EXPERIMENTAL_DESIGN_PROPERTY

**Failure modes:** Blocking treatment with time unintentionally; post-hoc subgrouping; using seed as “replication” but not block; forgetting block interactions.

**Criticism:** The property is bounded by its stated assumptions and known failures: Blocking treatment with time unintentionally; post-hoc subgrouping; using seed as “replication” but not block; forgetting block interactions. Contrary evidence/limit: When nuisance variables are numerous/high-dimensional, model-based adjustment may overfit; design-stage balance remains finite.

**Contrary evidence:** When nuisance variables are numerous/high-dimensional, model-based adjustment may overfit; design-stage balance remains finite.

**Unresolved questions:** Which factors merit blocking versus deliberate exploration as potential interactions?

**Property versus ceremony:** A Latin square or mandatory stratification table is optional; nuisance-control efficiency is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S005; S006; S043

**Critical source identities:** S047; S048

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/30`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p032"></a>
### P032 — Require independent replication at the experimental-unit level; treat technical repeats as measurement information

**Historical origin:** Fisherian replication, hierarchical experimental design and Hurlbert’s pseudoreplication critique.

**Original form:** Repeat treatments on genuinely independent units so variability relevant to generalisation is observed.

**Development:** Evolved into multilevel models, cluster-robust inference, multisite replication and explicit technical/biological/system-level replication labels.

**Evolved form in this historical corpus:** Count independent decision-relevant units, disclose dependence, and stop treating correlated reruns as corroboration.

**Problem:** Many outputs, seeds, subsamples or repeated readings from one unit can look like a large experiment while providing one treatment assignment.

**Mechanism:** Define unit/cluster, allocate multiple independent units per condition, model nesting/repeated measures and label technical replication explicitly.

**Trigger and context:** Any claim intended to generalise beyond one specimen, run, model instance, batch, site or environment.

**Preconditions:** Multiple independent units, provenance showing common sources, and a stable treatment/evaluator protocol.

**Measurement preconditions:** Repeated measurement error is separated from between-unit variation; evaluator exposures do not couple units.

**Assumptions:** Units are exchangeable/representative enough for intended scope; clusters and interference are modelled.

**Decision or consumer:** Experimenter, reviewer and engineering decision authority.

**Nontrigger or cheaper adequate path:** For deterministic proof or exact exhaustive checks, replication is unnecessary; for measurement precision, technical repeats remain useful but answer a different question.

**Disposition at the historical freeze:** EXPERIMENTAL_DESIGN_PROPERTY

**Failure modes:** Same seed/environment; multiple metrics from one run; split observations from one batch; repeated test after adaptation; duplicated data lineage.

**Criticism:** Replication count is not enough: independence, representativeness and measurement validity remain prerequisites.

**Contrary evidence:** For singular large engineered systems, evidence may need component replication, simulation validation and mechanistic argument rather than classical independent system copies.

**Unresolved questions:** What constitutes independent replication for stochastic software/agent systems sharing training data, code and evaluator?

**Property versus ceremony:** A fixed “number of replications” is ceremony; independence at the right level is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: VERY_HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S005; S006; S023

**Critical source identities:** S032; S038

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/31`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p033"></a>
### P033 — Use factorial structure to discover interactions and avoid one-factor-at-a-time ambiguity

**Historical origin:** Fisherian factorial designs and industrial DOE.

**Original form:** Vary multiple factors jointly so main effects and interactions can be estimated efficiently.

**Development:** Evolved into screening, optimal/computer designs, sequential augmentation and hierarchical modelling.

**Evolved form in this historical corpus:** Use factorial structure when interaction ambiguity is decision-relevant; confirm in the intended operating region.

**Problem:** One-factor-at-a-time trials miss synergies/antagonisms and can recommend settings that fail in combination.

**Mechanism:** Use full or suitable fractional factorial designs, randomisation/blocking and hierarchy/sparsity only as stated assumptions; confirm consequential interactions.

**Trigger and context:** Multiple controllable factors with plausible interactions and experiments costly enough that structured coverage matters.

**Preconditions:** Stable factor levels, adequate measurement, feasible combinations, enough units, and a response meaningful over the design region.

**Measurement preconditions:** Outcome/evaluator remains comparable across combinations; invalid/impossible combinations identified before randomisation.

**Assumptions:** Model hierarchy/sparsity or sufficient full design; no uncontrolled time/batch confounding.

**Decision or consumer:** Design/process engineer and optimiser.

**Nontrigger or cheaper adequate path:** For one known dominant factor, deterministic mechanism or a tiny safe search space that can be exhaustively tested, formal factorial DOE may be excessive.

**Disposition at the historical freeze:** EXPERIMENTAL_DESIGN_PROPERTY

**Failure modes:** OFAT; no randomisation; main effects interpreted despite strong interactions; multiple responses cherry-picked; no confirmation.

**Criticism:** Factorial design is not synonymous with all experimentation; interactions outside tested levels/context remain unknown.

**Contrary evidence:** High-dimensional systems may violate effect sparsity/hierarchy and contain discontinuities; adaptive or mechanistic designs may outperform classical factorials.

**Unresolved questions:** How should factor screening incorporate safety constraints and rare catastrophic interactions?

**Property versus ceremony:** A full 2^k table is optional; efficient interaction-identifying contrast structure is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S006; S043; S049

**Critical source identities:** S010; S050

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/32`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p034"></a>
### P034 — Use fractional factorial/screening designs only with explicit alias and sparsity assumptions

**Historical origin:** Plackett–Burman, fractional factorial resolution theory and industrial screening.

**Original form:** Screen many factors with fewer runs by accepting known confounding/alias structure.

**Development:** Modern practice uses sequential augmentation, Bayesian/sparsity models and optimal designs but cannot eliminate aliasing without information.

**Evolved form in this historical corpus:** Treat screening results as provisional, report aliases, and resolve any ambiguity that could change the decision.

**Problem:** A low-resolution design can mistake interactions for main effects or declare inactive factors under false sparsity.

**Mechanism:** Choose resolution by plausible interactions, inspect alias matrix, randomise/block, use foldover/augmentation or independent confirmation.

**Trigger and context:** Early screening with many candidate factors, limited runs and a credible effect-sparsity/hierarchy hypothesis.

**Preconditions:** Known factor ranges, stable measurement, feasible design matrix, predeclared alias tolerance and resources for follow-up.

**Measurement preconditions:** Measurement error small enough that sparse effects are not buried; factor settings are reproducible.

**Assumptions:** Few active effects, high-order interactions negligible or follow-up can resolve ambiguity.

**Decision or consumer:** Screening experiment owner and design team.

**Nontrigger or cheaper adequate path:** Use full factorial, mechanistic screening or direct elimination when interactions are dense/critical or factors are few.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Resolution III main effects treated as clean; no foldover; factors dropped before interaction check; no confirmation.

**Criticism:** The property is bounded by its stated assumptions and known failures: Resolution III main effects treated as clean; no foldover; factors dropped before interaction check; no confirmation. Contrary evidence/limit: When effect sparsity fails or factors are adaptive/continuous, screening rankings can be unstable and model-dependent.

**Contrary evidence:** When effect sparsity fails or factors are adaptive/continuous, screening rankings can be unstable and model-dependent.

**Unresolved questions:** How should alias risk be priced when a missed interaction has severe safety consequences?

**Property versus ceremony:** A Plackett–Burman array or “DOE software result” is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S010; S043; S044

**Critical source identities:** S049; S050

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/33`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p035"></a>
### P035 — Use response surfaces and iterative experimentation as local learning, with confirmation and boundary discipline

**Historical origin:** Box–Wilson response-surface methodology, Box/Hunter sequential experimentation and Shewhart/Box iterative science.

**Original form:** Build local empirical models, move toward promising regions, augment the design and confirm the selected operating point.

**Development:** Modern practice hybridises RSM with Bayesian optimisation/adaptive design, but still needs protected validation and decision costs.

**Evolved form in this historical corpus:** Iterate models as provisional maps; require confirmation in the intended context and robustness around the selected point.

**Problem:** A one-shot optimum from sparse data can be a model artefact; unstructured trial-and-error wastes runs and hides stopping bias.

**Mechanism:** Start with screening/local design, check curvature/residuals, proceed sequentially under a stated rule, respect constraints, and reserve independent confirmation/robustness tests.

**Trigger and context:** Continuous controllable factors, expensive runs and an objective surface smooth enough locally.

**Preconditions:** Stable measurement, controllable factors, safe region, adequate local design, model diagnostics and fresh confirmation capacity.

**Measurement preconditions:** Outcome definition/threshold remains stable across stages; process drift is monitored.

**Assumptions:** Local low-order approximation is adequate within each step; sequential data reuse is reflected in uncertainty.

**Decision or consumer:** Design/process engineer and optimisation decision owner.

**Nontrigger or cheaper adequate path:** For discrete deterministic search spaces that are cheap to enumerate or when a mechanistic model fixes the optimum, RSM is unnecessary.

**Disposition at the historical freeze:** EXPERIMENTAL_DESIGN_PROPERTY

**Failure modes:** Reporting fitted optimum without confirmation; extrapolating beyond design; stopping after favourable stage; no noise-factor test.

**Criticism:** The property is bounded by its stated assumptions and known failures: Reporting fitted optimum without confirmation; extrapolating beyond design; stopping after favourable stage; no noise-factor test. Contrary evidence/limit: Adaptive optimisers can exploit evaluator noise and drift; repeated use of the same validation surface erodes confirmation value.

**Contrary evidence:** Adaptive optimisers can exploit evaluator noise and drift; repeated use of the same validation surface erodes confirmation value.

**Unresolved questions:** What degree of fresh confirmation is needed after highly adaptive optimisation?

**Property versus ceremony:** RSM contour plots or a fixed phase sequence are tools; sequential information-efficient learning is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S009; S021; S049

**Critical source identities:** S044; S050

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/34`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p036"></a>
### P036 — Report effect magnitude, uncertainty and engineering significance; use equivalence/noninferiority when “no important difference” is the decision

**Historical origin:** Neyman–Pearson power, estimation/tolerance practice, modern p-value criticism and equivalence testing.

**Original form:** Interpret estimated magnitude and uncertainty against a predeclared engineering consequence/margin, not only a null-test threshold.

**Development:** ASA-era guidance preserved inferential tools but rejected single-threshold interpretation; equivalence methods sharpen negative claims.

**Evolved form in this historical corpus:** Show effect, uncertainty, smallest consequential magnitude, and decision; reserve “equivalent” for designs that test a justified margin.

**Problem:** Tiny effects become “significant” with large n, while meaningful effects are dismissed after inconclusive small studies; non-significance is called equivalence.

**Mechanism:** Define smallest effect of interest or acceptance margin; report interval/distribution and decision consequences; use equivalence/noninferiority design where appropriate.

**Trigger and context:** Comparisons where action depends on magnitude, not merely direction, and negative results may support interchangeability.

**Preconditions:** Valid measurement, meaningful scale/margin, representative units, adequate information and multiplicity/stopping control.

**Measurement preconditions:** Metric resolution and uncertainty are small enough relative to the engineering margin.

**Assumptions:** Model/interval coverage is adequate; equivalence margin is fixed independently of observed results.

**Decision or consumer:** Design/process owner, customer, regulator and risk decision maker.

**Nontrigger or cheaper adequate path:** For deterministic threshold compliance or an overwhelming effect far from uncertainty, a p-value may add nothing.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** p<.05 presented without units; CI crossing zero called “same”; post-hoc equivalence margin; relative change hiding absolute harm.

**Criticism:** The property is bounded by its stated assumptions and known failures: p<.05 presented without units; CI crossing zero called “same”; post-hoc equivalence margin; relative change hiding absolute harm. Contrary evidence/limit: Engineering-significance margins can be multi-dimensional and context-dependent; scalar margins may conceal trade-offs or rare harms.

**Contrary evidence:** Engineering-significance margins can be multi-dimensional and context-dependent; scalar margins may conceal trade-offs or rare harms.

**Unresolved questions:** How should practical-significance criteria aggregate average benefit and catastrophic tail risk?

**Property versus ceremony:** A particular effect-size statistic or ban on p-values is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S007; S029; S041

**Critical source identities:** S033; S034; S035; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/35`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p037"></a>
### P037 — Control multiplicity, analyst degrees of freedom and selective inference across the actual family of opportunities

**Historical origin:** Multiple-comparison theory, FDR, preregistration/transparent reporting and empirical research on undisclosed flexibility.

**Original form:** Account for the number and adaptivity of outcomes, subgroups, models, thresholds and looks that could have generated a favourable claim.

**Development:** Evolved from fixed families to FDR, hierarchical testing, selective inference, reusable holdouts and explicit exploration/confirmation separation.

**Evolved form in this historical corpus:** Protect the claim-generating opportunity set, not merely the final table; use fresh confirmation when adaptivity is complex.

**Problem:** Trying enough analyses almost guarantees an apparently strong result even when no stable effect exists.

**Mechanism:** Define confirmatory families, preserve all analyses, use FWER/FDR/selective methods as appropriate, split/external validation, and label exploration.

**Trigger and context:** Many metrics, variants, subgroups, prompts, models, thresholds or parallel experiments.

**Preconditions:** Complete analysis provenance, stable outcome definitions, independent/protected validation data and a meaningful error criterion.

**Measurement preconditions:** Evaluator/threshold versions and excluded outputs are retained; duplicates/dependence are known.

**Assumptions:** Chosen correction matches dependence and decision loss; unreported researcher flexibility is bounded.

**Decision or consumer:** Experiment owner, reviewer, portfolio decision maker and public evidence consumer.

**Nontrigger or cheaper adequate path:** When one authoritative predeclared deterministic discriminator exists, multiplicity machinery is unnecessary; report any exploratory alternatives separately.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Correcting only final p-values while selecting endpoints/models; post-hoc “primary” metric; repeated benchmark variants; favourable subgroup only.

**Criticism:** The property is bounded by its stated assumptions and known failures: Correcting only final p-values while selecting endpoints/models; post-hoc “primary” metric; repeated benchmark variants; favourable subgroup only. Contrary evidence/limit: The true adaptive analysis family may be impossible to enumerate; fresh independent replication/holdout protection may be more credible than retrospective correction.

**Contrary evidence:** The true adaptive analysis family may be impossible to enumerate; fresh independent replication/holdout protection may be more credible than retrospective correction.

**Unresolved questions:** How should multiplicity be controlled when agents dynamically generate hypotheses and evaluators during the campaign?

**Property versus ceremony:** A preregistration badge, Bonferroni-by-default or “one metric” slogan is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: VERY_HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S028; S038; S040

**Critical source identities:** S033; S034; S035; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/36`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p038"></a>
### P038 — Plan sequential evidence and stopping so repeated looks do not manufacture confidence

**Historical origin:** Wald sequential analysis, alpha-spending/group-sequential methods, confidence sequences and always-valid online inference.

**Original form:** Permit data-dependent continuation/stopping only under a rule whose error/coverage or decision risk remains valid over time.

**Development:** Evolved from model-specific SPRT to group-sequential, alpha spending, confidence sequences and decision-theoretic adaptive designs.

**Evolved form in this historical corpus:** Another observation is justified only when it is expected to change the decision and the stopping/error framework remains valid.

**Problem:** Peeking and sampling until favourable inflates false positives; fixed quotas can waste measurements after a decision is already discriminated.

**Mechanism:** Choose fixed horizon, group-sequential/alpha-spending, SPRT, confidence sequence, Bayesian decision rule or explicit noninferential learning cadence; preserve stopping metadata.

**Trigger and context:** Repeated monitoring/experiments where results are reviewed before collection ends or cost accumulates over time.

**Preconditions:** Defined outcome/estimand, valid time/dependence model, precommitted boundaries or anytime-valid method, complete history and action loss.

**Measurement preconditions:** Measurement/evaluator is stable over the sequence; repeated observations add identifiable information.

**Assumptions:** Procedure’s martingale/likelihood/independence conditions hold or robust alternatives are used; adaptive outcome switching is excluded.

**Decision or consumer:** Experiment/monitoring owner and resource/risk decision maker.

**Nontrigger or cheaper adequate path:** Stop immediately when an authoritative deterministic discriminator settles the decision; no statistical stopping machinery is needed.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Restarting tests after failure; treating every review as independent; stopping at first green; continuing only negative arms; changing metric midstream.

**Criticism:** The property is bounded by its stated assumptions and known failures: Restarting tests after failure; treating every review as independent; stopping at first green; continuing only negative arms; changing metric midstream. Contrary evidence/limit: No universal stopping rule exists across discovery, safety, optimisation and governance; information value and consequence determine the boundary.

**Contrary evidence:** No universal stopping rule exists across discovery, safety, optimisation and governance; information value and consequence determine the boundary.

**Unresolved questions:** How should sequential validity be preserved when both candidate and evaluator adapt between looks?

**Property versus ceremony:** A universal number of rounds or a confidence-sequence library is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S011; S012; S036; S037

**Critical source identities:** S040; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/37`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p039"></a>
### P039 — Bound causal claims by external validity, interference, carryover and order effects

**Historical origin:** Causal inference, cross-over design, cluster/interference methods and transportability concerns.

**Original form:** Separate internal comparison validity from applicability to new contexts and from one unit affecting another or later periods.

**Development:** Evolved into cluster/network experiments, crossover diagnostics, multisite replication and explicit transport/sensitivity analysis.

**Evolved form in this historical corpus:** State the local causal estimand and separately justify transport; design around interference/order when materially plausible.

**Problem:** A clean experiment can estimate the wrong deployment effect when units interfere, learn, carry over, or differ from the target population.

**Mechanism:** Define exposure mapping/population, design clusters/washouts/counterbalancing, measure effect modifiers, replicate across contexts and restrict claims.

**Trigger and context:** Networked/shared-resource systems, sequential treatments, adaptive users, multi-site deployment or any generalisation claim.

**Preconditions:** Target population/context, unit/exposure graph, period/order history, representative sampling and stable measurement across contexts.

**Measurement preconditions:** Outcome remains comparable; contamination/exposure is observable enough to model.

**Assumptions:** No hidden interference/carryover beyond the specified structure; sampled contexts cover intended use or extrapolation is bounded.

**Decision or consumer:** Deployment owner, system architect, regulator and experiment consumer.

**Nontrigger or cheaper adequate path:** For an exact local deterministic mechanism with no scope extension, external-validity statistics may be unnecessary; state the local claim.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Users share treatments; same system state across arms; inadequate washout; one site; aggregate effect hides vulnerable context.

**Criticism:** Randomisation is preserved but narrowed: it supports the assigned comparison, not automatic transport.

**Contrary evidence:** General transport under unmeasured effect modification is not identified from one experiment; mechanistic and multi-context evidence remain necessary.

**Unresolved questions:** What minimum context diversity is needed before an engineering effect can be treated as robust rather than local?

**Property versus ceremony:** A “randomised” label is not the property if exposure or deployment scope differs.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S018; S047; S048

**Critical source identities:** S039; S099

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/38`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p040"></a>
### P040 — Use robustness and sensitivity analysis to expose dependence on model, confounding and nuisance assumptions

**Historical origin:** Robust statistics, model criticism, causal sensitivity and industrial robustness practice.

**Original form:** Recompute or bound conclusions under plausible alternative distributions, nuisance values, confounding, preprocessing and analysis choices.

**Development:** Evolved from single-model checks to decision-focused robustness, influence analysis, partial identification and stress scenarios.

**Evolved form in this historical corpus:** Challenge the assumptions capable of changing the decision; do not confuse robust-to-one-model feature with universal validity.

**Problem:** A conclusion may exist only under one fragile model or arbitrary analytic choice.

**Mechanism:** Specify plausible perturbation set, inspect residuals/influence, use robust/nonparametric/model-averaged/bounded analyses and report decision stability.

**Trigger and context:** Small samples, heavy tails, observational comparisons, extrapolation, complex models or high-consequence decisions.

**Preconditions:** Domain-informed alternative models/ranges, adequate measurement/provenance and a fixed decision criterion.

**Measurement preconditions:** Measurement error and evaluator variants are included among perturbations where material.

**Assumptions:** Perturbation set spans credible alternatives rather than only convenient ones; robust method’s loss/neighbourhood matches consequence.

**Decision or consumer:** Analyst, reviewer, risk owner and design authority.

**Nontrigger or cheaper adequate path:** When a deterministic mechanism/proof settles the decision, statistical sensitivity may be redundant; verify mechanism assumptions instead.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Only normality test; deleting “outliers” post hoc; robust estimator treated as assumption-free; sensitivity range chosen to preserve result.

**Criticism:** The property is bounded by its stated assumptions and known failures: Only normality test; deleting “outliers” post hoc; robust estimator treated as assumption-free; sensitivity range chosen to preserve result. Contrary evidence/limit: Sensitivity conclusions are only as broad as the considered perturbations; unknown unknowns and structural model error remain.

**Contrary evidence:** Sensitivity conclusions are only as broad as the considered perturbations; unknown unknowns and structural model error remain.

**Unresolved questions:** How should plausible perturbation sets be governed so they are neither result-preserving nor impossibly broad?

**Property versus ceremony:** A mandatory normality test or a menu of every model is ceremony.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S016; S017; S021

**Critical source identities:** S042; S099

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/39`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p041"></a>
### P041 — Choose experiments and measurements by expected information or decision value relative to cost

**Historical origin:** Shewhart/Duncan economic control, decision analysis/value of information and sequential industrial experimentation.

**Original form:** Collect evidence when its expected effect on the next decision is worth its monetary, time, risk and opportunity cost.

**Development:** Evolved from economic chart/sample design toward general evidence portfolios, adaptive design and qualitative decision-value gates.

**Evolved form in this historical corpus:** Ask whether the next observation is independently informative enough to change action; choose the cheapest valid discriminator.

**Problem:** Measurement quotas, full DOE or repeated review can consume more than the uncertainty they resolve; cheap tests may be omitted despite high value.

**Mechanism:** List current alternatives/uncertainty, possible outcomes and changed actions; estimate information gain/EVSI or use qualitative dominance; stop when no plausible result changes action enough.

**Trigger and context:** Costly/slow/destructive measurement, adaptive experimentation, competing tests or staged engineering decisions.

**Preconditions:** Explicit decision/action set, consequence ranges, credible outcome model and measurement/experiment cost.

**Measurement preconditions:** Measurement can actually discriminate the uncertain states and does not repeat shared bias.

**Assumptions:** Utility/probability model or qualitative ranking is sufficiently credible; option value and irreversible harm are considered.

**Decision or consumer:** Resource allocator, design/test owner and risk decision maker.

**Nontrigger or cheaper adequate path:** Take the direct authoritative fact immediately when cost is negligible; do not build a probabilistic model merely to justify an obvious check.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** “More data” default; full factorial despite deterministic discriminator; no action change after result; cost omitted; catastrophic risk monetised casually.

**Criticism:** The property is bounded by its stated assumptions and known failures: “More data” default; full factorial despite deterministic discriminator; no action change after result; cost omitted; catastrophic risk monetised casually. Contrary evidence/limit: Deep uncertainty and irreversible tail harms can defeat expected-value summaries; robust/safety constraints may override average information value.

**Contrary evidence:** Deep uncertainty and irreversible tail harms can defeat expected-value summaries; robust/safety constraints may override average information value.

**Unresolved questions:** How should option/discovery value and catastrophic constraints be combined with expected information value?

**Property versus ceremony:** A formal Bayesian model is optional; evidence proportionality is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S014; S098; S009

**Critical source identities:** S021; S080

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/40`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p042"></a>
### P042 — Give precedence to an authoritative deterministic discriminator when it settles the decision

**Historical origin:** Not a single historical statistical school; a convergent anti-overapplication boundary implicit in measurement science, engineering proof and evidence economy.

**Original form:** When a valid exact check, identity, proof, specification comparison or mechanism directly decides the case, use it before stochastic inference.

**Development:** Modern evidence-efficient practice treats statistical methods as conditional tools, not obligatory proof decorations.

**Evolved form in this historical corpus:** First ask whether the decision is already logically or physically discriminated; if yes, stop statistical collection and document the decisive evidence.

**Problem:** Statistical machinery can obscure a decisive fact, introduce model assumptions and waste samples.

**Mechanism:** Verify authority, identity, applicability and measurement; execute the direct check; use statistics only for residual uncertainty, frequency, transfer or noisy observation.

**Trigger and context:** Exact configuration/identity, complete enumeration, formal proof, direct physical interlock or unambiguous requirement violation.

**Preconditions:** Authoritative source, exact scope/identity, reliable implementation and no hidden measurement ambiguity.

**Measurement preconditions:** The discriminator’s input and output are verifiable and its resolution covers the decision.

**Assumptions:** The rule truly entails the decision under current conditions; completeness/authority have been established.

**Decision or consumer:** Engineering decision owner and evidence reviewer.

**Nontrigger or cheaper adequate path:** Do not invoke this property when the “deterministic” rule is an unvalidated proxy, incomplete oracle, stale reference or only one sample from a stochastic population.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Running significance tests on exhaustive results; rerunning a deterministic failure until green; using source count over authoritative identity; stale oracle.

**Criticism:** The property is bounded by its stated assumptions and known failures: Running significance tests on exhaustive results; rerunning a deterministic failure until green; using source count over authoritative identity; stale oracle. Contrary evidence/limit: Whether a discriminator is complete and authoritative is itself an evidence question; probabilistic residual risk may remain.

**Contrary evidence:** Whether a discriminator is complete and authoritative is itself an evidence question; probabilistic residual risk may remain.

**Unresolved questions:** How can systems prevent “deterministic” gates from becoming stale or proxy-captured while retaining their cheap decisiveness?

**Property versus ceremony:** The absence of statistical analysis is not a defect when uncertainty is not the decision problem.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: LOW; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S098; S079; S110

**Critical source identities:** S051; S054; S080

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/41`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p043"></a>
### P043 — Design robustness to nuisance factors and context variation, not only nominal mean performance

**Historical origin:** Industrial parameter/robust design, Taguchi influence, classical factorial/RSM and robust statistics.

**Original form:** Choose designs/settings whose performance remains acceptable as uncontrollable noise factors vary.

**Development:** Later statistical criticism retained parameter/noise-factor design but narrowed or replaced universal S/N analyses with direct modelling and standard DOE.

**Evolved form in this historical corpus:** Test and optimise decision-relevant performance across plausible nuisance contexts, with transparent loss and confirmation.

**Problem:** A nominal optimum can be fragile to temperature, operator, load, population, supplier or environment.

**Mechanism:** Identify realistic noise factors, cross them with control factors or stress them, model mean/variance/tails separately, and confirm in representative contexts.

**Trigger and context:** Products/processes deployed across variable environments or with costly field failures.

**Preconditions:** Valid noise-factor ranges/distributions, controllable factors, measurement fitness, feasible stress combinations and consequence criteria.

**Measurement preconditions:** Measurement remains valid across noise conditions and can resolve dispersion/tail changes.

**Assumptions:** Tested noise factors represent deployment; interactions/model form are adequate; accelerated stresses do not introduce irrelevant mechanisms.

**Decision or consumer:** Designer, reliability/quality engineer and deployment owner.

**Nontrigger or cheaper adequate path:** For a fixed, tightly controlled environment or a deterministic design margin proven against all relevant variation, elaborate robust DOE may be unnecessary.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Using Taguchi S/N ratio automatically; unrealistic noise ranges; no confirmation; averaging away context-specific failures.

**Criticism:** The property is bounded by its stated assumptions and known failures: Using Taguchi S/N ratio automatically; unrealistic noise ranges; no confirmation; averaging away context-specific failures. Contrary evidence/limit: No finite noise-factor set guarantees open-world robustness; field monitoring and conservative design margins remain necessary.

**Contrary evidence:** No finite noise-factor set guarantees open-world robustness; field monitoring and conservative design margins remain necessary.

**Unresolved questions:** How should robust design cover rare combinations and adversarial contexts without combinatorial explosion?

**Property versus ceremony:** Taguchi orthogonal arrays, S/N ratios and loss slogans are optional/historically contingent; robustness is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S025; S049; S095

**Critical source identities:** S096; S102; S016

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/42`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p044"></a>
### P044 — Model reliability over time with explicit failure definitions, exposure, censoring and degradation

**Historical origin:** Life-testing, survival analysis, reliability engineering and degradation modelling.

**Original form:** Estimate time-to-failure or degradation processes using all exposure and censoring information under a defined mission/failure criterion.

**Development:** Evolved from failure-count summaries to censored survival, recurrent/repairable systems, covariates, degradation and predictive uncertainty.

**Evolved form in this historical corpus:** Make reliability conditional on mission, time/exposure, failure definition and context; report bounds and model sensitivity.

**Problem:** Snapshot pass rates do not describe reliability duration; censored survivors and varying duty cycles can bias estimates.

**Mechanism:** Define failure/missions, record time/exposure and interventions, use survival/degradation models with uncertainty, stratify failure modes and validate fit.

**Trigger and context:** Components/systems where ageing, wear, cumulative use or time-dependent failure changes the decision.

**Preconditions:** Representative units/duty cycles, failure-mode taxonomy, censoring records, stable measurement, sufficient time/failures or degradation surrogate.

**Measurement preconditions:** Failure detection threshold is stable and degradation measure is linked to actual failure.

**Assumptions:** Independent/appropriately clustered lifetimes, censoring mechanism acceptable, distribution/regression model adequate over prediction horizon.

**Decision or consumer:** Reliability engineer, maintainer, design authority and risk owner.

**Nontrigger or cheaper adequate path:** For a purely timeless deterministic property or rapidly replaceable low-consequence component, full life modelling may not pay.

**Disposition at the historical freeze:** DOMAIN_SPECIFIC

**Failure modes:** Removing early failures; right-censored units treated as nonfailures forever; mixed modes pooled; uptime denominator changed; threshold drift.

**Criticism:** The property is bounded by its stated assumptions and known failures: Removing early failures; right-censored units treated as nonfailures forever; mixed modes pooled; uptime denominator changed; threshold drift. Contrary evidence/limit: Complex software/agent failure opportunities may not map cleanly to lifetime distributions; reliability methods transfer only where exposure/failure processes are coherent.

**Contrary evidence:** Complex software/agent failure opportunities may not map cleanly to lifetime distributions; reliability methods transfer only where exposure/failure processes are coherent.

**Unresolved questions:** How should reliability be defined for continually updated systems whose configuration and workload change during exposure?

**Property versus ceremony:** A Weibull plot or MTBF number is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S071; S077; S104

**Critical source identities:** S078; S072

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/43`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p045"></a>
### P045 — Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty

**Historical origin:** Accelerated life testing, physics-of-failure models and reliability statistics.

**Original form:** Apply elevated stress to obtain failures sooner, then translate to use conditions through an acceleration/life model.

**Development:** Mature ALT integrates physics, multiple stresses, model diagnostics and conservative uncertainty rather than a generic acceleration factor.

**Evolved form in this historical corpus:** Acceleration is an assumption-heavy bridge whose physical continuity must be evidenced, not a shortcut to certainty.

**Problem:** Use-stress tests may produce too few failures, but high stress can create different failure modes or nonlinear extrapolation.

**Mechanism:** Select physically justified stresses, include multiple levels/use-level anchors, diagnose failure modes, fit and challenge acceleration models, report prediction intervals/sensitivity.

**Trigger and context:** Long-lived products where timely direct life testing is infeasible and a credible acceleration mechanism exists.

**Preconditions:** Mechanistic knowledge, representative specimens, stable failure definition, stress control, enough failures/levels and use-condition data/anchors.

**Measurement preconditions:** Stress/temperature/load measurement is calibrated; failure detection remains comparable across levels.

**Assumptions:** Same relevant failure mechanisms and adequate acceleration/life distributions across tested-to-use range.

**Decision or consumer:** Reliability/design owner and release/risk authority.

**Nontrigger or cheaper adequate path:** Do not accelerate when stress changes the mechanism or when conservative deterministic margin/field data already decide the question.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** One stress level; no use anchor; pooled failure modes; extrapolation without interval; treating high-stress pass as field proof.

**Criticism:** The property is bounded by its stated assumptions and known failures: One stress level; no use anchor; pooled failure modes; extrapolation without interval; treating high-stress pass as field proof. Contrary evidence/limit: Extreme acceleration and sparse failures make model uncertainty dominant; there may be no defensible high-reliability extrapolation.

**Contrary evidence:** Extreme acceleration and sparse failures make model uncertainty dominant; there may be no defensible high-reliability extrapolation.

**Unresolved questions:** How much use-condition anchoring is enough to falsify an acceleration model before release?

**Property versus ceremony:** A standard Arrhenius/Weibull fit is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S072; S076; S077

**Critical source identities:** S078; S104

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/44`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p046"></a>
### P046 — Treat reliability growth as intervention-conditioned evidence, not an automatically improving trend

**Historical origin:** Reliability growth testing, Crow–AMSAA/Duane-type models and test-analyse-fix programmes.

**Original form:** Evaluate whether documented design/process fixes change failure intensity over exposure while accounting for configuration and environment.

**Development:** Consensus guidance narrows claims and stresses configuration/test-environment assumptions and independent verification.

**Evolved form in this historical corpus:** Attribute change to documented fixes only when comparable exposure and fresh validation support it; otherwise call it an observed trend.

**Problem:** A downward failure trend can arise from easier tests, survivor populations, changed definitions or selective fixes rather than durable growth.

**Mechanism:** Version configurations, log every intervention/exposure/failure mode, use growth models as summaries, and validate fixes on fresh representative tests/field data.

**Trigger and context:** Development programmes with repeated failures and deliberate corrective modifications.

**Preconditions:** Configuration control, comparable exposure/test environments, stable failure definitions, independent validation and enough events.

**Measurement preconditions:** Measurement/evaluator thresholds are stable across versions or bridged.

**Assumptions:** Model form approximates the repair/improvement process; changes other than intended fixes are documented.

**Decision or consumer:** Reliability programme manager, design authority and acquisition/release decision maker.

**Nontrigger or cheaper adequate path:** When no modifications occur, use ordinary reliability estimation; when one deterministic defect/fix is proven, validate that mechanism directly.

**Disposition at the historical freeze:** DOMAIN_SPECIFIC

**Failure modes:** Test difficulty decreases; failures reclassified; exposure resets; fixes not independently verified; one programme curve pooled across modes.

**Criticism:** The property is bounded by its stated assumptions and known failures: Test difficulty decreases; failures reclassified; exposure resets; fixes not independently verified; one programme curve pooled across modes. Contrary evidence/limit: Growth models are particularly vulnerable when few failures, many simultaneous changes or rapidly changing test environments exist.

**Contrary evidence:** Growth models are particularly vulnerable when few failures, many simultaneous changes or rapidly changing test environments exist.

**Unresolved questions:** How can causal contribution be allocated among bundled fixes without an infeasible factorial programme?

**Property versus ceremony:** A Crow–AMSAA plot or target slope is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S078; S071; S077

**Critical source identities:** S040; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/45`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p047"></a>
### P047 — Translate zero observed failures into an upper risk bound, never “perfect reliability”

**Historical origin:** Binomial/Poisson reliability demonstration and the rule of three.

**Original form:** Use one-sided confidence/credible bounds on failure probability/rate when no events are observed.

**Development:** Modern practice uses exact/Bayesian/Poisson/exposure bounds and combines test with mechanistic/field evidence for very high reliability.

**Evolved form in this historical corpus:** Report the strongest upper bound supported by independent representative exposure and state what remains unobserved.

**Problem:** Zero events in finite exposure is compatible with nonzero—sometimes material—failure rates.

**Mechanism:** Define independent opportunities/exposure and target confidence; calculate bound, include heterogeneity/censoring, and compare with required risk.

**Trigger and context:** Reliability/safety claims based on zero failures or no detected rare defects.

**Preconditions:** Clear failure opportunity, independent/representative trials, stable detection threshold, complete event capture and fixed stopping.

**Measurement preconditions:** Failures would be detected with sufficient sensitivity; no excluded/censored near-failures.

**Assumptions:** Bernoulli/Poisson/exposure model and homogeneity or conservative stratification are adequate.

**Decision or consumer:** Safety/reliability/release authority and customer/regulator.

**Nontrigger or cheaper adequate path:** When a formal proof/physical impossibility establishes zero risk within scope, statistical zero-event bounds are secondary; verify proof scope.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Counting repeated same-condition trials as independent; optional stopping after a clean run; changing failure definition; hiding near misses.

**Criticism:** The property is bounded by its stated assumptions and known failures: Counting repeated same-condition trials as independent; optional stopping after a clean run; changing failure definition; hiding near misses. Contrary evidence/limit: Extremely low target rates are rarely demonstrable by direct testing alone; model/mechanism/operational evidence must be combined without pretending equivalence.

**Contrary evidence:** Extremely low target rates are rarely demonstrable by direct testing alone; model/mechanism/operational evidence must be combined without pretending equivalence.

**Unresolved questions:** How should heterogeneous stress, common-mode failures and changing exposure be incorporated into zero-event bounds?

**Property versus ceremony:** “0 defects” and a green dashboard are not properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S073; S075; S071

**Critical source identities:** S045; S078

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/46`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p048"></a>
### P048 — Treat rare-event and tail claims as distinct, data-hungry and model-sensitive

**Historical origin:** Extreme-value/tolerance/reliability theory, rare-event sampling and safety/reliability practice.

**Original form:** Analyse high quantiles, exceedance probabilities and catastrophic modes separately from means and ordinary variance.

**Development:** Evolved toward explicit tolerance/exceedance bounds, extreme-value methods, stress testing and mechanism-informed conservative evidence.

**Evolved form in this historical corpus:** Separate central performance from tail claims; calibrate claim strength to observed/validated tail information and consequence.

**Problem:** Good averages and even stable central behaviour can coexist with unacceptable tails; finite data contain little direct tail information.

**Mechanism:** Define tail event/consequence, preserve maxima/near misses, use tolerance/extreme/reliability models with diagnostics and conservative bounds, stress/importance sample, and combine mechanism evidence.

**Trigger and context:** High-consequence low-frequency failures, tight population-content guarantees or asymmetric loss.

**Preconditions:** Stable event definition/detection, representative exposure including stress contexts, enough tail observations or justified physical model, and no selective deletion.

**Measurement preconditions:** Resolution captures near-tail behaviour and censoring/thresholds are stable.

**Assumptions:** Tail family/extrapolation and dependence are adequate; stress sampling is correctly reweighted; unobserved modes acknowledged.

**Decision or consumer:** Safety/reliability/design authority and risk owner.

**Nontrigger or cheaper adequate path:** For bounded deterministic systems with proven hard limits, direct worst-case analysis can dominate statistical tail estimation.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Normal six-sigma extrapolation; dropping outliers; zero events called zero risk; tail metric tuned after incident; pooled modes.

**Criticism:** The property is bounded by its stated assumptions and known failures: Normal six-sigma extrapolation; dropping outliers; zero events called zero risk; tail metric tuned after incident; pooled modes. Contrary evidence/limit: Unknown failure modes and dependence can dominate beyond-sample tails; precise numerical estimates may be less honest than conservative bounds/scenarios.

**Contrary evidence:** Unknown failure modes and dependence can dominate beyond-sample tails; precise numerical estimates may be less honest than conservative bounds/scenarios.

**Unresolved questions:** What combination of stress, mechanism and operational data justifies a claim at a failure rate never directly observed?

**Property versus ceremony:** A “six sigma” label or one worst-case anecdote is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: VERY_HIGH

**Primary source identities:** S074; S075; S071

**Critical source identities:** S062; S078; S099

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/47`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p049"></a>
### P049 — Test distribution shift and stress contexts; do not equate held-out performance with deployment validity

**Historical origin:** Measurement invariance, robust/reliability testing, dataset-shift science and refreshed benchmark evidence.

**Original form:** Evaluate whether performance/calibration persists under plausible population, environment, workload, adversarial or temporal shifts.

**Development:** Modern practice combines protected holdouts, fresh test sets, shift taxonomy, stress scenarios and ongoing field monitoring.

**Evolved form in this historical corpus:** A held-out score is local evidence; deployment claims require context coverage, shift sensitivity and evaluator integrity.

**Problem:** A model/process can succeed on a fixed holdout while failing after deployment composition, context or incentives change.

**Mechanism:** Map shift scenarios, reserve protected/refresh samples, stress test mechanism-relevant changes, monitor calibration and restrict claims to covered regions.

**Trigger and context:** Adaptive software/ML/agent systems, long-lived processes, changing customers/suppliers, or field environments beyond lab conditions.

**Preconditions:** Context metadata, representative or deliberately stressed samples, stable evaluator/construct, fresh data source and shift-response plan.

**Measurement preconditions:** Labels/references remain valid under shift or are independently adjudicated.

**Assumptions:** Stress scenarios are plausible and not merely convenient; deployment monitoring can detect uncovered shifts.

**Decision or consumer:** Deployment owner, reliability/quality engineer and benchmark/evaluator owner.

**Nontrigger or cheaper adequate path:** For a closed deterministic domain fully enumerated by an authoritative test, distribution-shift analysis may be unnecessary; verify closure.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Repeated public benchmark tuning; no fresh collection; adversarial examples counted as prevalence; aggregate shift hides subgroup collapse.

**Criticism:** The property is bounded by its stated assumptions and known failures: Repeated public benchmark tuning; no fresh collection; adversarial examples counted as prevalence; aggregate shift hides subgroup collapse. Contrary evidence/limit: Open-world shifts are unbounded; no finite suite proves universal robustness, and fresh sets may still share collection artefacts.

**Contrary evidence:** Open-world shifts are unbounded; no finite suite proves universal robustness, and fresh sets may still share collection artefacts.

**Unresolved questions:** How should shift suites be refreshed independently without making longitudinal progress incomparable?

**Property versus ceremony:** A benchmark leaderboard or one stress suite is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S099; S039; S038

**Critical source identities:** S027; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/48`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p050"></a>
### P050 — Keep mean performance, variability, tail behaviour, reliability over time and model robustness as separate claims

**Historical origin:** Quality variation, robust design, tolerance/reliability theory and modern multi-metric evaluation.

**Original form:** Decompose performance dimensions instead of compressing them into one average or sigma score.

**Development:** Evolved from mean/variance quality metrics toward explicit reliability, robustness, tails and context-separated evidence.

**Evolved form in this historical corpus:** Make one claim per dimension and combine them only through a transparent consequence model.

**Problem:** An improvement in mean can worsen variability, tails, durability or context sensitivity; a composite can hide the trade.

**Mechanism:** Report decision-relevant central effect, dispersion, quantiles/tails, time/exposure reliability and assumption/context sensitivity separately; use explicit multi-criteria decisions.

**Trigger and context:** Systems with heterogeneous outcomes, repeated operation, rare harms or multiple stakeholders.

**Preconditions:** Valid metrics for each dimension, declared weighting/priority, representative units/contexts and enough tail/time evidence for any claim.

**Measurement preconditions:** Measurement error is separated by dimension and thresholds remain stable.

**Assumptions:** Dimensions are not falsely treated as independent; composite utility, if used, is explicit and decision-owned.

**Decision or consumer:** Design/release authority, risk owner and public evidence consumer.

**Nontrigger or cheaper adequate path:** For a single exact binary requirement with no temporal/context dimension, one authoritative result may be sufficient.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Mean-only benchmark; variance ignored; uptime without severity; composite weights changed; tail based on one anecdote.

**Criticism:** The property is bounded by its stated assumptions and known failures: Mean-only benchmark; variance ignored; uptime without severity; composite weights changed; tail based on one anecdote. Contrary evidence/limit: Multi-criteria trade-offs are partly normative and may resist statistical aggregation; unresolved conflicts must remain visible.

**Contrary evidence:** Multi-criteria trade-offs are partly normative and may resist statistical aggregation; unresolved conflicts must remain visible.

**Unresolved questions:** What minimal dimension set prevents harmful substitution without producing unmanageable reporting?

**Property versus ceremony:** A mandatory giant dashboard is not the property; non-substitution among materially different risk dimensions is.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S062; S071; S074

**Critical source identities:** S039; S084

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/49`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p051"></a>
### P051 — Treat optimised metrics as vulnerable proxies and monitor for gaming/surrogation

**Historical origin:** Goodhart/Campbell/Strathern indicator criticism, quality-target experience and modern benchmark overfitting.

**Original form:** Assume a metric’s relation to the underlying goal can weaken when rewards, release or status depend on it.

**Development:** The social-science laws are treated as convergent warning mechanisms, strengthened in digital domains by adaptive-data/benchmark evidence.

**Evolved form in this historical corpus:** Use metrics as defeasible sensors: preserve an independent construct/outcome path and investigate divergence under optimisation.

**Problem:** Optimisers learn to improve the measurement surface rather than the real property.

**Mechanism:** Keep construct/outcome checks independent, use multiple non-substitutable indicators where justified, audit exclusions/denominators, refresh protected evidence and inspect mechanisms.

**Trigger and context:** High-stakes target metrics, leaderboards, incentives, automated optimisation or repeated candidate exposure.

**Preconditions:** Defined underlying goal, provenance, stable denominators, independent outcome/reference evidence and the ability to observe optimisation response.

**Measurement preconditions:** Metric and construct are distinguishable; evaluator changes and candidate exposures are versioned.

**Assumptions:** A plausible behavioural/optimisation mechanism links targeting to metric degradation; independent checks are not co-optimised.

**Decision or consumer:** Metric owner, incentive/release authority and system outcome owner.

**Nontrigger or cheaper adequate path:** For a direct authoritative physical/logical property that cannot be cheaply manipulated, proxy safeguards may be minimal; maintain authority/integrity checks.

**Disposition at the historical freeze:** USEFUL_BUT_EASILY_GAMED

**Failure modes:** Dropping hard cases; changing denominator; teaching to test; benchmark leakage; proxy chosen for availability; outcome not independently checked.

**Criticism:** The property is bounded by its stated assumptions and known failures: Dropping hard cases; changing denominator; teaching to test; benchmark leakage; proxy chosen for availability; outcome not independently checked. Contrary evidence/limit: Goodhart/Campbell claims are not universal formal theorems; some metrics remain useful under targeting if causal alignment and integrity controls are strong.

**Contrary evidence:** Goodhart/Campbell claims are not universal formal theorems; some metrics remain useful under targeting if causal alignment and integrity controls are strong.

**Unresolved questions:** How can independent outcome checks remain independent when the whole organisation can observe and optimise them?

**Property versus ceremony:** “Use multiple KPIs” is not itself the property; independent construct evidence and anti-substitution boundaries are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: MODERATE; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S019; S022; S097

**Critical source identities:** S038; S039; S040

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/50`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p052"></a>
### P052 — Require independent, prospective justification before changing an evaluator, fixture, expected answer or threshold after failure

**Historical origin:** Measurement assurance/calibration change control, conformity decision rules, adaptive-data safeguards and proxy-gaming criticism.

**Original form:** Treat post-failure evaluator change as a new measurement intervention needing evidence independent of the candidate outcome.

**Development:** Evolved from calibration/check-standard discipline to versioned benchmark/evaluator governance and reusable-holdout independence.

**Evolved form in this historical corpus:** Change only on independent evidence that the measurement/construct—not merely the candidate—is defective or context has legitimately changed.

**Problem:** An organisation can make failures disappear by editing the instrument rather than fixing the object.

**Mechanism:** Classify suspected defect (candidate/measurement/construct/sampling), reproduce on references, use blinded bridge studies, obtain independent authority, version change and re-evaluate affected claims.

**Trigger and context:** Any proposed evaluator/threshold/fixture/answer change triggered by an unfavourable result.

**Preconditions:** Frozen prior version, external reference/construct evidence, bridge sample, change rationale and authority separate from candidate optimisation.

**Measurement preconditions:** Reference cases include failures/boundaries and are protected from the candidate change.

**Assumptions:** The bridge can distinguish measurement defect from candidate defect; updated rule better represents the underlying construct.

**Decision or consumer:** Measurement/evaluator owner, release authority and independent reviewer.

**Nontrigger or cheaper adequate path:** Correct a provable transcription/specification error immediately, preserving evidence and authority; no large statistical study is needed.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Changing expected output after seeing candidate; threshold chosen to include current score; deleting failed case; no old/new bridge; circular validation.

**Criticism:** The property is bounded by its stated assumptions and known failures: Changing expected output after seeing candidate; threshold chosen to include current score; deleting failed case; no old/new bridge; circular validation. Contrary evidence/limit: Independent reference truth may be unavailable for evolving constructs; legitimate change can remain unresolved rather than forced.

**Contrary evidence:** Independent reference truth may be unavailable for evolving constructs; legitimate change can remain unresolved rather than forced.

**Unresolved questions:** Who can supply independent construct authority when the evaluator and target system co-evolve?

**Property versus ceremony:** A fixed change-request form is optional; independence, bridge and retrospective impact assessment are the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: HIGH; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S015; S053; S060

**Critical source identities:** S038; S039; S097

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/51`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p053"></a>
### P053 — Separate candidate/process variation from evaluator/measurement variation before assigning corrective action

**Historical origin:** Measurement-system analysis, method agreement, measurement-error effects on control/experiments and evaluator drift governance.

**Original form:** Use crossed/replicated reference and candidate observations to locate variation source before changing either side.

**Development:** Evolved from physical gauge R&R to general crossed evaluator/candidate/reference designs and configuration bridges.

**Evolved form in this historical corpus:** Hold one side fixed while testing the other against independent references; leave unresolved when evidence cannot distinguish.

**Problem:** A changed score alone cannot identify whether candidate, evaluator, fixture, environment or sample changed.

**Mechanism:** Maintain reference cases and stable candidates, cross evaluators/versions/operators, decompose variation and test specific mechanism hypotheses.

**Trigger and context:** Unexpected regression/improvement, disagreement across evaluators, near-threshold failures or repeated nonreproducibility.

**Preconditions:** Stable reference/candidate artefacts, versioned evaluators, repeat/cross-over design and protected provenance.

**Measurement preconditions:** Measurement runs are comparable; reference cases cover the disputed region.

**Assumptions:** Variance components/interactions are estimable enough to discriminate source or else conclusion remains unresolved.

**Decision or consumer:** Engineer, measurement owner and independent review authority.

**Nontrigger or cheaper adequate path:** If a direct inspection proves a deterministic candidate defect or evaluator bug, repair that source immediately and document it.

**Disposition at the historical freeze:** STRONGLY_RETAINED

**Failure modes:** Only rerunning candidate; only checking easy references; evaluator and candidate changed together; no interaction analysis; regression to mean.

**Criticism:** The property is bounded by its stated assumptions and known failures: Only rerunning candidate; only checking easy references; evaluator and candidate changed together; no interaction analysis; regression to mean. Contrary evidence/limit: Variance decomposition can identify where variability resides but not automatically which construct is correct or why the interaction occurs.

**Contrary evidence:** Variance decomposition can identify where variability resides but not automatically which construct is correct or why the interaction occurs.

**Unresolved questions:** How should source discrimination proceed when the evaluator is learned from candidate-generated data?

**Property versus ceremony:** A GR&R percentage is not required; discriminating source of variation is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: VERY_HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S058; S032; S024

**Critical source identities:** S010; S052

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/52`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p054"></a>
### P054 — Protect holdouts, reproduce analyses and prevent adaptive evaluation reuse from masquerading as fresh evidence

**Historical origin:** Reproducible statistical analysis, multiple testing, reusable holdouts and modern benchmark-refresh evidence.

**Original form:** Keep confirmation data/evaluators sufficiently independent of adaptive development and make the full analysis executable/reviewable.

**Development:** Evolved from train/test splitting toward adaptive-data safeguards, access accounting, refreshed benchmarks and reproducibility packages.

**Evolved form in this historical corpus:** State what was reused, what was protected, and what evidence is genuinely fresh; use independent confirmation for final claims.

**Problem:** Repeated tuning on a holdout leaks information; rerunning the same pipeline is reproducibility, not independent validation.

**Mechanism:** Separate development/exploration/confirmation, restrict feedback, log access, use reusable-holdout methods where applicable, refresh externally and reproduce exact computation.

**Trigger and context:** Iterative software/ML/agent development, repeated benchmark submissions, many model/analysis variants or long campaigns.

**Preconditions:** Versioned data/code/evaluator, access/provenance controls, representative fresh samples and a defined confirmation claim.

**Measurement preconditions:** Evaluation pipeline itself is stable/validated; contamination/duplication detectable.

**Assumptions:** Protected sample remains sufficiently independent; reusable-holdout privacy/model conditions or fresh-data assumptions hold.

**Decision or consumer:** Developer, benchmark owner, reviewer and deployment authority.

**Nontrigger or cheaper adequate path:** For a deterministic exhaustive authoritative test, repeated execution may verify implementation but does not need a statistical holdout.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Calling same holdout reruns “replications”; public test labels; leaderboard tuning; analysis not executable; fresh test collected differently.

**Criticism:** The property is bounded by its stated assumptions and known failures: Calling same holdout reruns “replications”; public test labels; leaderboard tuning; analysis not executable; fresh test collected differently. Contrary evidence/limit: Fresh data can differ for reasons unrelated to overfitting; holdout protection trades off feedback, shift and sample efficiency.

**Contrary evidence:** Fresh data can differ for reasons unrelated to overfitting; holdout protection trades off feedback, shift and sample efficiency.

**Unresolved questions:** How can adaptive systems receive useful diagnostic feedback while preserving independent final evaluation?

**Property versus ceremony:** A fixed split percentage or preregistration badge is not the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: VERY_HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S038; S039; S040

**Critical source identities:** S033; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/53`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p055"></a>
### P055 — Check model adequacy and misspecification against the decision, not through ritual assumption tests

**Historical origin:** Residual diagnostics, Box model criticism, robust statistics, time-series/SPC and modern predictive checking.

**Original form:** Ask whether model errors materially affect the action, using residual structure, calibration, predictive checks and sensitivity.

**Development:** Evolved from pass/fail assumption tests to graphical/predictive/sensitivity assessment of decision consequences.

**Evolved form in this historical corpus:** Use the simplest adequate model and report which guarantees are conditional; switch/robustify when a departure changes the decision.

**Problem:** Mathematical validity under assumptions is mistaken for evidence those assumptions hold; normality-test rituals can reject harmless deviations or miss dependence.

**Mechanism:** Inspect time/order/residual/influence/calibration plots, compare plausible models, simulate operating characteristics and use robust/design-based alternatives where needed.

**Trigger and context:** Any inferential/control/reliability method whose operating characteristics depend materially on distribution, independence, link or functional form.

**Preconditions:** Adequate data over intended region, stable measurement, model purpose and known decision-sensitive assumptions.

**Measurement preconditions:** Measurement artefacts/censoring/rounding are modelled or ruled out before diagnosing process distribution.

**Assumptions:** Diagnostics have power for material deviations; alternative models are plausible and not chosen only for desired results.

**Decision or consumer:** Analyst, monitoring/experiment owner and reviewer.

**Nontrigger or cheaper adequate path:** For deterministic checks or methods robust by design to the relevant deviation, skip irrelevant normality tests and document why.

**Disposition at the historical freeze:** ASSUMPTION_SENSITIVE

**Failure modes:** Mandatory Shapiro–Wilk; accepting model because p>.05; residuals not time-ordered; transformation after seeing desired significance; no out-of-sample check.

**Criticism:** The property is bounded by its stated assumptions and known failures: Mandatory Shapiro–Wilk; accepting model because p>.05; residuals not time-ordered; transformation after seeing desired significance; no out-of-sample check. Contrary evidence/limit: Model adequacy is never globally established; it is conditional on data region and purpose, and diagnostics can share blind spots.

**Contrary evidence:** Model adequacy is never globally established; it is conditional on data region and purpose, and diagnostics can share blind spots.

**Unresolved questions:** How should model uncertainty be communicated when several models are adequate centrally but diverge in the decision tail?

**Property versus ceremony:** A normality test checklist is ceremony; decision-sensitive adequacy is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S017; S021; S110

**Critical source identities:** S026; S031; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/54`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p056"></a>
### P056 — Integrate multiple statistical and engineering methods into a system-level evidence strategy

**Historical origin:** Quality planning/control traditions, Steiner–MacKay variation reduction and Hoerl–Snee/ISEA statistical engineering.

**Original form:** Structure large, complex, unstructured problems; sequence measurement, process, experiment, reliability and decision tools around a mission.

**Development:** Broader statistical engineering generalises beyond a 2005 manufacturing algorithm and beyond Six Sigma, but remains an emerging discipline with case-heavy evidence.

**Evolved form in this historical corpus:** A problem-structuring and integration property: right evidence, right order, right scale, with assumptions and consumer decisions explicit.

**Problem:** A toolkit used piecemeal can optimise local metrics, repeat work, miss dependencies or apply the right method at the wrong time.

**Mechanism:** Define mission/system, map evidence dependencies, identify dominant uncertainty, select/integrate the smallest valid methods, iterate with governance and sustain the solution.

**Trigger and context:** Cross-disciplinary problems too large for one model/test and with multiple linked decisions.

**Preconditions:** Decision authority, cross-disciplinary domain knowledge, measurement integrity, provenance, resource model and explicit interfaces among methods.

**Measurement preconditions:** Every input measurement/evaluator has sufficient fitness and common identities/units are maintained.

**Assumptions:** Integration logic is auditable; no method’s assumptions are silently contradicted by another stage; organisational cooperation exists.

**Decision or consumer:** System/problem owner, cross-functional engineering team and decision governance.

**Nontrigger or cheaper adequate path:** For a well-structured local question solved by one authoritative method/check, use that method; system-level statistical engineering would be overhead.

**Disposition at the historical freeze:** RETAINED_IN_EVOLVED_FORM

**Failure modes:** Framework phases treated as deliverables; tool count mistaken for rigour; no dominant uncertainty; local Cpk improvement harms system outcome.

**Criticism:** The property is bounded by its stated assumptions and known failures: Framework phases treated as deliverables; tool count mistaken for rigour; no dominant uncertainty; local Cpk improvement harms system outcome. Contrary evidence/limit: Evidence is strong for component methods and plausible for integration, but weak for a unique discipline-wide causal effect independent of competent engineering management.

**Contrary evidence:** Evidence is strong for component methods and plausible for integration, but weak for a unique discipline-wide causal effect independent of competent engineering management.

**Unresolved questions:** Which integration patterns are distinctively statistical engineering rather than good systems engineering with statistics?

**Property versus ceremony:** The label, framework diagram or consultancy is not the property; integration and sustainable decision improvement are.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: MODERATE; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: LOW; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S079; S080; S081

**Critical source identities:** S082; S084

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/55`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p057"></a>
### P057 — Make measurement and controls economically proportional; retire, revalidate or recalibrate stale controls

**Historical origin:** Shewhart/Duncan economic control, value-of-information reasoning, calibration intervals and modern monitoring governance.

**Original form:** Maintain evidence only while it changes decisions at acceptable cost; reassess controls when process, risk, measurement or cheaper discriminators change.

**Development:** Evolved from economic chart design to lifecycle governance across measurements, experiments, thresholds and benchmark controls.

**Evolved form in this historical corpus:** Every recurring control has a current decision, validity evidence and proportional cost; otherwise simplify, replace, revalidate or retire with risk sign-off.

**Problem:** Legacy dashboards/tests continue by habit, creating noise and cost; obsolete thresholds can govern a changed system.

**Mechanism:** Track each control’s decision consumer, failure mode, operating characteristics, cost and last validation; trigger retirement/recalibration when value or validity decays.

**Trigger and context:** Long-lived quality systems, recurring tests, duplicated reviews, low-yield monitoring or changed process/evaluator context.

**Preconditions:** Control inventory/ownership, event/decision history, cost, process/evaluator version, replacement/retirement authority and risk constraints.

**Measurement preconditions:** Control outcomes and false alarms/misses are measurable enough to assess utility; reference standards remain available.

**Assumptions:** Past yield predicts some future value or scenario analysis captures uncertainty; retirement does not violate unmodelled catastrophic safeguards.

**Decision or consumer:** Control owner, risk authority, resource allocator and downstream consumer.

**Nontrigger or cheaper adequate path:** Keep cheap high-value controls and legal/safety requirements even if failures are rare; deterministic checks may remain near-zero cost.

**Disposition at the historical freeze:** CONTEXT_DEPENDENT

**Failure modes:** Quota retained with no consumer; threshold never revalidated; duplicated tests treated as corroboration; control removed because it catches failures.

**Criticism:** The property is bounded by its stated assumptions and known failures: Quota retained with no consumer; threshold never revalidated; duplicated tests treated as corroboration; control removed because it catches failures. Contrary evidence/limit: Rare-event controls may have high option value despite little observed use; absence of catches is not sufficient retirement evidence.

**Contrary evidence:** Rare-event controls may have high option value despite little observed use; absence of catches is not sufficient retirement evidence.

**Unresolved questions:** How can stale-control retirement be distinguished from gaming away inconvenient evidence?

**Property versus ceremony:** A periodic review ceremony is not the property unless it can actually retire/change controls on evidence.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: MODERATE

**Primary source identities:** S002; S014; S098

**Critical source identities:** S060; S084

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/56`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p058"></a>
### P058 — Universal p < 0.05 threshold as an engineering decision rule

**Historical origin:** Later textbook/journal/managerial simplification of significance testing, not a property asserted by Fisher or Neyman–Pearson as a universal engineering rule.

**Original form:** Dichotomise results at a conventional significance threshold and treat crossing it as sufficient for action or truth.

**Development:** ASA statements criticise misuse while the 2021 task force explicitly preserves properly applied p-values; the evidence rejects universal threshold ritual, not all tests.

**Evolved form in this historical corpus:** Use error thresholds only when tied to a declared family, effect/decision and consequence; otherwise report continuous evidence and uncertainty.

**Problem:** Originally offered a convenient convention, but it fails to encode effect size, measurement validity, multiplicity, model adequacy or decision loss.

**Mechanism:** No defensible general mechanism; replace with decision/effect/uncertainty design and use p-values only as one calibrated diagnostic where appropriate.

**Trigger and context:** No universal trigger. A predeclared alpha can be useful inside a specific confirmatory error-control design.

**Preconditions:** If used: valid model/design, prespecified family/stopping, effect/margin and consequence-aware threshold.

**Measurement preconditions:** Measurement and sampling validity must already hold.

**Assumptions:** The test statistic/reference model and error family are correct; the chosen alpha reflects decision consequences—which 0.05 usually does not by default.

**Decision or consumer:** Specific confirmatory protocol owner, not general management branding.

**Nontrigger or cheaper adequate path:** For deterministic checks, descriptive estimation, Bayesian/decision designs, equivalence or safety constraints, the convention may be irrelevant.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Optional stopping; unreported multiplicity; p=0.049 vs 0.051 treated qualitatively different; effect size absent.

**Criticism:** The property is bounded by its stated assumptions and known failures: Optional stopping; unreported multiplicity; p=0.049 vs 0.051 treated qualitatively different; effect size absent. Contrary evidence/limit: There remains legitimate disagreement over when significance language/thresholds are useful; the rejected claim is universality and sufficiency.

**Contrary evidence:** There remains legitimate disagreement over when significance language/thresholds are useful; the rejected claim is universality and sufficiency.

**Unresolved questions:** Which engineering decision contexts genuinely benefit from a fixed error threshold rather than an explicit loss/interval rule?

**Property versus ceremony:** The universal rule is ceremony/rejected; calibrated hypothesis tests remain conditional tools.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: LOW; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: VERY_HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: VERY_HIGH

**Primary source identities:** S033; S034; S035

**Critical source identities:** S007; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/57`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p059"></a>
### P059 — Control-chart-everything and automatic run-rule escalation

**Historical origin:** Textbook/quality-programme simplification of Shewhart SPC and later dashboard practice.

**Original form:** Place every recurring metric on a classical chart and treat every rule violation as an intervention mandate.

**Development:** SPC literature itself documents assumptions and controversies; evolved practice narrows and adapts chart use.

**Evolved form in this historical corpus:** Monitor only where the stream, signal, cost and response are defensible; otherwise choose a cheaper direct/qualitative method.

**Problem:** Attempts to make variation visible, but assumes a meaningful stream, baseline, measurement and action response that often do not exist.

**Mechanism:** No universal mechanism; retain P015–P024 only where a calibrated monitor changes an actionable decision.

**Trigger and context:** Only repeatable, adequately measured processes with an interpretable baseline and response plan.

**Preconditions:** Stable measurement, process identity, dependence model, error costs and response capacity.

**Measurement preconditions:** Metric must be decision-relevant and evaluator-stable.

**Assumptions:** Chart/model assumptions and baseline are adequate; alerts are investigated rather than punished.

**Decision or consumer:** Specific process owner, never a generic surveillance layer.

**Nontrigger or cheaper adequate path:** One-off heterogeneous work, exact deterministic checks, sparse changing mixtures or metrics without an owner should not trigger classical charting.

**Disposition at the historical freeze:** CEREMONY_NOT_GENERAL_PROPERTY

**Failure modes:** Specs used as limits; many supplementary rules; no action plan; rebaselining; individual ranking on system variation.

**Criticism:** The property is bounded by its stated assumptions and known failures: Specs used as limits; many supplementary rules; no action plan; rebaselining; individual ranking on system variation. Contrary evidence/limit: Some broad monitoring programmes work organisationally, but benefit cannot be inferred from chart count and may reflect improved attention/process definition.

**Contrary evidence:** Some broad monitoring programmes work organisationally, but benefit cannot be inferred from chart count and may reflect improved attention/process definition.

**Unresolved questions:** What minimum evidence shows a new chart adds discrimination rather than alert volume?

**Property versus ceremony:** The chart/tool is ceremony when detached from a decision; variation discrimination is the property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S001; S061; S107

**Critical source identities:** S030; S031; S066

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/58`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p060"></a>
### P060 — Universal 3.4 DPMO or “six-sigma level” as the definition of quality

**Historical origin:** Motorola/GE-era Six Sigma rhetoric and capability-index conversion conventions, including the contested 1.5-sigma shift.

**Original form:** Express quality as a universal defects-per-million target associated with a nominal shifted normal process.

**Development:** Mature quality engineering retains conditional capability/yield and abandons the number as a universal definition.

**Evolved form in this historical corpus:** Set targets from customer/safety/economic consequences and observed/modelled risk, not brand numerology.

**Problem:** Provides a memorable aspiration but compresses defect opportunity, severity, dependence, distribution, stability and measurement into one number.

**Mechanism:** No general mechanism; use direct consequence-specific defect/reliability/tail evidence and conditional capability only where prerequisites hold.

**Trigger and context:** A project may choose a defect-rate target when opportunities and consequences are coherent; the branded universal number is not required.

**Preconditions:** Stable process, valid measurement, fixed opportunity definition, adequate distribution/tail evidence and consequence-relevant target.

**Measurement preconditions:** Defect classification and opportunity denominators must be stable and resistant to gaming.

**Assumptions:** Normal/shift model and independence would need support; extrapolation far beyond data remains weak.

**Decision or consumer:** Programme/project owner only after risk justification.

**Nontrigger or cheaper adequate path:** Do not trigger for continuous performance, changing opportunities, unstable/non-normal processes, rare catastrophic modes or deterministic requirements.

**Disposition at the historical freeze:** CEREMONY_NOT_GENERAL_PROPERTY

**Failure modes:** Counting opportunities strategically; Cpk converted to DPMO under instability; 1.5 shift asserted as law; average defect severity ignored.

**Criticism:** The property is bounded by its stated assumptions and known failures: Counting opportunities strategically; Cpk converted to DPMO under instability; 1.5 shift asserted as law; average defect severity ignored. Contrary evidence/limit: Historical details of the 1.5-sigma convention vary across practitioner accounts; no strong general evidence makes it a physical/statistical law.

**Contrary evidence:** Historical details of the 1.5-sigma convention vary across practitioner accounts; no strong general evidence makes it a physical/statistical law.

**Unresolved questions:** In which narrowly defined high-volume processes is a DPMO target more decision-useful than direct yield/severity/tail reporting?

**Property versus ceremony:** 3.4 DPMO and “sigma level” are programme rhetoric/conditional conversion, not a surviving general property.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: LOW; MEASUREMENT_SCIENCE_STRENGTH: LOW; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: MODERATE; REPLICATION_STRENGTH: LOW; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: VERY_HIGH

**Primary source identities:** S082; S062; S063

**Critical source identities:** S084; S031; S048

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/59`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p061"></a>
### P061 — DMAIC/DMADV phase names and tollgates as a general statistical property

**Historical origin:** Six Sigma management-programme translation of earlier problem-solving, quality-control and product-design cycles.

**Original form:** Require work to pass named phases and prescribed tollgates/templates.

**Development:** Research characterises DMAIC as a problem-solving structure and Six Sigma’s distinctive element as organisational architecture, not unique statistics.

**Evolved form in this historical corpus:** Retain evidence dependencies and governance where useful; strip mandatory branding and tailor path to problem risk/uncertainty.

**Problem:** Can coordinate roles, preserve sequencing and prevent premature solutioning in large programmes.

**Mechanism:** Underlying properties—problem definition, measurement validation, analysis, intervention, confirmation/control—can be implemented in many forms.

**Trigger and context:** Useful when many teams/projects need common governance and handoffs.

**Preconditions:** Real authority at gates, evidence criteria, proportionate templates and ability to iterate/skip non-value steps.

**Measurement preconditions:** Measurement validity cannot be conferred by reaching the Measure phase.

**Assumptions:** Programme fit and organisational coordination are adequate; phases permit iteration and exceptions.

**Decision or consumer:** Programme/project governance.

**Nontrigger or cheaper adequate path:** Small/local/deterministic decisions, exploratory science, or established competent workflows need not adopt the names or fixed order.

**Disposition at the historical freeze:** CEREMONY_NOT_GENERAL_PROPERTY

**Failure modes:** Tollgate passed on documents; analysis forced after answer known; no iteration; every project uses same tool menu.

**Criticism:** The property is bounded by its stated assumptions and known failures: Tollgate passed on documents; analysis forced after answer known; no iteration; every project uses same tool menu. Contrary evidence/limit: Observational evidence cannot cleanly separate structured problem solving from brand, training, leadership and selection effects.

**Contrary evidence:** Observational evidence cannot cleanly separate structured problem solving from brand, training, leadership and selection effects.

**Unresolved questions:** Which coordination benefits persist after removing DMAIC names and mandatory artefacts?

**Property versus ceremony:** Phase names/tollgates are artefacts, not general properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: LOW; MEASUREMENT_SCIENCE_STRENGTH: LOW; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: LOW; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S082; S083; S091

**Critical source identities:** S084; S087

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/60`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p062"></a>
### P062 — Belt hierarchy and certification as a general engineering property

**Historical origin:** Six Sigma organisational role structure and certification market.

**Original form:** Assign improvement authority/competence through belt ranks and certified tool curricula.

**Development:** Organisational research treats role structure as distinctive to Six Sigma, while criticism shows resource/rigidity/theatre risks.

**Evolved form in this historical corpus:** Use role/competence systems proportionate to need and assess actual decisions/work products; no required belt taxonomy.

**Problem:** Can create trained specialists, common language, mentoring and protected project capacity.

**Mechanism:** Underlying properties are demonstrated competence, role clarity, independence and capacity—not belt names.

**Trigger and context:** Potentially useful in large deployments needing specialist career/role architecture.

**Preconditions:** Validated competence assessment, domain integration, project evidence, role authority and ongoing learning.

**Measurement preconditions:** Certification must include measurement/design reasoning, not merely software/tool recall.

**Assumptions:** Curriculum/assessment predicts competent practice and role structure fits the organisation.

**Decision or consumer:** Organisational leadership and project portfolio governance.

**Nontrigger or cheaper adequate path:** Small teams, mature statistical functions, regulated laboratories or domain specialists may use different competence systems.

**Disposition at the historical freeze:** CEREMONY_NOT_GENERAL_PROPERTY

**Failure modes:** Certificate accepted as evidence of method validity; belt owns statistics without process knowledge; project quotas; expired skills.

**Criticism:** The property is bounded by its stated assumptions and known failures: Certificate accepted as evidence of method validity; belt owns statistics without process knowledge; project quotas; expired skills. Contrary evidence/limit: Some evidence links experienced teams/structured roles to project success, but credential effects are confounded with selection, resources and leadership.

**Contrary evidence:** Some evidence links experienced teams/structured roles to project success, but credential effects are confounded with selection, resources and leadership.

**Unresolved questions:** What competence evidence predicts high-quality statistical engineering better than course completion?

**Property versus ceremony:** Belt titles/certificates are programme artefacts.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: LOW; MEASUREMENT_SCIENCE_STRENGTH: LOW; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: MODERATE; DOMAIN_CASE_STRENGTH: MODERATE; REPLICATION_STRENGTH: LOW; TRANSFERABILITY_STRENGTH: LOW; ASSUMPTION_SENSITIVITY: MODERATE; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S082; S085; S086

**Critical source identities:** S084; S087

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/61`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p063"></a>
### P063 — More samples, more reruns or repeated green tests automatically mean more truth

**Historical origin:** A recurring statistical caricature contradicted by sampling, measurement error, dependence, missingness, sequential and adaptive-data theory.

**Original form:** Treat raw observation count or repeated pass count as monotonically increasing confidence regardless of source/dependence/bias.

**Development:** Modern practice distinguishes technical repeatability, independent replication, effective sample size, sequential validity and value of information.

**Evolved form in this historical corpus:** Another observation earns weight only through identifiable independent/conditional information and positive decision value.

**Problem:** Averaging can reduce independent random error, but cannot remove shared bias, selection, invalid constructs or common-mode dependence.

**Mechanism:** Count independent information, model dependence/bias, protect stopping and ask whether the next observation can change the decision.

**Trigger and context:** No universal trigger; more evidence helps only when it is valid, sufficiently independent and decision-relevant.

**Preconditions:** Valid measurement, representative sampling, independent/new units or valid dependence/sequential model.

**Measurement preconditions:** Measurement bias and evaluator drift must be bounded; repeated runs are provenance-distinct.

**Assumptions:** Information increments satisfy the planning model and no outcome-contingent selection/stopping invalidates inference.

**Decision or consumer:** Experiment/measurement owner.

**Nontrigger or cheaper adequate path:** Stop when deterministic evidence settles the decision or when another correlated rerun has negligible value.

**Disposition at the historical freeze:** REJECTED_OR_DISFAVOURED

**Failure modes:** Same data reanalysed; same unit reread; same seed; same evaluator bias; stop at green; failed runs dropped.

**Criticism:** The property is bounded by its stated assumptions and known failures: Same data reanalysed; same unit reread; same seed; same evaluator bias; stop at green; failed runs dropped. Contrary evidence/limit: Information dependence can be only partly known; conservative effective sample sizes or fresh-source confirmation may be required.

**Contrary evidence:** Information dependence can be only partly known; conservative effective sample sizes or fresh-source confirmation may be required.

**Unresolved questions:** How should shared upstream training/data/evaluator dependence be discounted when nominal runs are distinct?

**Property versus ceremony:** Raw run count and streaks are not properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: VERY_HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: VERY_HIGH; DOMAIN_CASE_STRENGTH: VERY_HIGH; REPLICATION_STRENGTH: VERY_HIGH; TRANSFERABILITY_STRENGTH: VERY_HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: LOW

**Primary source identities:** S023; S028; S032; S038

**Critical source identities:** S040; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/62`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p064"></a>
### P064 — Mandatory normality tests, fixed gauge R&R cutoffs and full MSA paperwork for every metric

**Historical origin:** Quality-training/checklist simplification of model diagnostics and measurement-system analysis.

**Original form:** Require standard assumption tests and form thresholds regardless of decision, scale, sample size or measurement mechanism.

**Development:** Mature practice evaluates fitness relative to use and consequential departures, not universal checklist thresholds.

**Evolved form in this historical corpus:** Use the smallest diagnostic/MSA design that can falsify decision adequacy.

**Problem:** Attempts to standardise due diligence but confuses a procedure with evidence of adequacy.

**Mechanism:** Replace with decision-sensitive measurement capability, graphical/predictive diagnostics and methods robust to relevant departures.

**Trigger and context:** Use formal tests/designs when a specific assumption or variance component can change the decision.

**Preconditions:** Defined decision margin, measurement mechanism, model purpose and representative validation conditions.

**Measurement preconditions:** Measurement study must cover actual range/operators/context rather than satisfy a form.

**Assumptions:** Diagnostic/test operating characteristics and cutoff relevance are understood.

**Decision or consumer:** Measurement/analysis owner and reviewer.

**Nontrigger or cheaper adequate path:** Skip irrelevant tests for deterministic checks, categorical authoritative outcomes or robust methods; use a concise rationale.

**Disposition at the historical freeze:** CEREMONY_NOT_GENERAL_PROPERTY

**Failure modes:** p>0.05 called normal; 10% GR&R used universally; easy part range; exact digital check forced into variance study.

**Criticism:** The property is bounded by its stated assumptions and known failures: p>0.05 called normal; 10% GR&R used universally; easy part range; exact digital check forced into variance study. Contrary evidence/limit: Some regulated contexts legitimately require standardised evidence for comparability; the critique is indiscriminate use, not all standard protocols.

**Contrary evidence:** Some regulated contexts legitimately require standardised evidence for comparability; the critique is indiscriminate use, not all standard protocols.

**Unresolved questions:** Which standardised diagnostics provide enough cross-site governance value to justify occasional local over-testing?

**Property versus ceremony:** The mandatory form/cutoff is ceremony; measurement fitness/model adequacy are retained properties.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: MODERATE; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: HIGH; EMPIRICAL_CAUSAL_STRENGTH: LOW; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: MODERATE; TRANSFERABILITY_STRENGTH: HIGH; ASSUMPTION_SENSITIVITY: VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH: HIGH

**Primary source identities:** S055; S058; S110

**Critical source identities:** S032; S042

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/63`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

<a id="p065"></a>
### P065 — Universal Taguchi signal-to-noise ratios and orthogonal-array recipes as the definition of robust design

**Historical origin:** Taguchi quality-engineering programme and later statistical critique/refinement.

**Original form:** Use prescribed S/N criteria and orthogonal arrays as generally optimal robust-design analysis.

**Development:** Box/Bisgaard/Fung, León/Shoemaker/Kackar, Nair panel and later practice retained robust parameter design while narrowing/replacing universal S/N methods.

**Evolved form in this historical corpus:** Model the actual mean, variance, tails and noise-factor interactions; use a Taguchi criterion only when demonstrably appropriate.

**Problem:** Promoted explicit noise-factor design and off-line quality improvement but often imposed inefficient or condition-specific analyses.

**Mechanism:** Retain P043 robust/noise-factor experimentation; use standard factorial/RSM/direct mean–variance/tail models suited to the objective.

**Trigger and context:** Particular S/N ratios may be useful only when their mean-variance/performance relation matches the engineering loss.

**Preconditions:** Explicit loss/objective, factor/noise structure, alias analysis, measurement fitness and confirmation.

**Measurement preconditions:** Response scale and variance can be estimated separately across representative noise conditions.

**Assumptions:** Chosen criterion has a justified relation to adjustment, mean and variance; array resolution supports interactions of interest.

**Decision or consumer:** Design/quality engineer.

**Nontrigger or cheaper adequate path:** Do not trigger automatically because a problem mentions robustness or noise.

**Disposition at the historical freeze:** SUPERSEDED_BY_STRONGER_FORM

**Failure modes:** S/N used without loss relation; no interaction/alias analysis; array selected from menu; confirmation absent.

**Criticism:** The property is bounded by its stated assumptions and known failures: S/N used without loss relation; no interaction/alias analysis; array selected from menu; confirmation absent. Contrary evidence/limit: Taguchi’s organisational influence and practical success cases are real but do not establish statistical optimality of every prescribed method.

**Contrary evidence:** Taguchi’s organisational influence and practical success cases are real but do not establish statistical optimality of every prescribed method.

**Unresolved questions:** Which Taguchi-specific criteria remain preferable under clearly stated loss/mean-variance structures?

**Property versus ceremony:** Universal S/N/array recipe is superseded; robust design remains retained in evolved form.

**Evidence profile at the historical freeze:** HISTORICAL_PROVENANCE_STRENGTH: HIGH; FORMAL_OR_THEORETICAL_STRENGTH: HIGH; MEASUREMENT_SCIENCE_STRENGTH: MODERATE; EMPIRICAL_CAUSAL_STRENGTH: MODERATE; EMPIRICAL_ASSOCIATIONAL_STRENGTH: HIGH; DOMAIN_CASE_STRENGTH: HIGH; REPLICATION_STRENGTH: HIGH; TRANSFERABILITY_STRENGTH: MODERATE; ASSUMPTION_SENSITIVITY: HIGH; CONTRARY_EVIDENCE_STRENGTH: VERY_HIGH

**Primary source identities:** S094; S095; S096

**Critical source identities:** S025; S102

Source: [EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json), JSON pointer `/properties/64`. [Complete source context](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json).

## Source references

[c-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-cognitive-systems-engineering.html
[s-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-statistical-engineering.html
[h-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-systems-safety.html
[css-page]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/portal/pages/research-lineage-evolved-css.html
[css-readme]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/README.md
[c-ledger]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-cognitive-systems-engineering/corpus/EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_PROPERTY_LEDGER.json
[c-sources]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-cognitive-systems-engineering/corpus/EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_SOURCE_TABLE.json
[c-intake]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-cognitive-systems-engineering/corpus/EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE.md
[s-ledger]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PROPERTY_LEDGER.json
[s-sources]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_SOURCE_TABLE.json
[s-intake]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-statistical-engineering/corpus/EVOLVED_STATISTICAL_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE.md
[h-ledger]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PROPERTY_LEDGER.json
[h-sources]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_SOURCE_TABLE.json
[h-intake]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/e78f7cb21af4197d490f10bc95917a4c75f748aa/docs/research/genealogy/css/evolved-systems-safety/corpus/EVOLVED_SYSTEMS_SAFETY_PUBLIC_DOCUMENTATION_INTAKE.md
[current-css]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/docs/research/genealogy/current-programme/v1/families/css.md
[194-receipt]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/194#issuecomment-5312867827
[195]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/195
[195-receipt]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/195#issuecomment-5312877164
[196-census]: https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/196#issuecomment-5312877705
[effect-source]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/skills/implementaudit/references/repo-state-comparison.md
[phase-source]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/skills/implementaudit/references/phase-design.md
[planning-source]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/22dfa6efec0dc5532b0a37f0de5bd92b3686db7f/skills/implementaudit/references/planning-depth.md
[active-safety]: https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/ed2c060daa41b6b88c1d49b325a3aa920088aed8/docs/maintenance/four-rockstar-integration.md
[203]: https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/203
[206]: https://github.com/theislampill/IMPLEMENTAUDIT.md/pull/206
