# EVOLVED_STATISTICAL_ENGINEERING_AUDIT_INTAKE

- **Freeze date:** 2026-08-11
- **Purpose:** external property intake for a later, independent target-system audit.
- **Boundary:** this intake asks questions only; it makes no target-system ownership, compatibility, redundancy, adoption or implementation judgement.

## Population

```text
PROPERTY_POPULATION_TOTAL: 65
PROPERTY_POPULATION_EXAMINED: 65
PROPERTY_COVERAGE: 65/65
CROSSWALK_WORTHY_PROPERTY_POPULATION: 57
CEREMONIAL_REJECTED_OR_SUPERSEDED_POPULATION: 8
```

## SOURCE_POPULATION_SUMMARY

| Measure | Count / distribution |
| --- | --- |
| Total curated source records | 110 |
| Source classes | authoritative edited monograph=1; authoritative handbook=20; authoritative index=1; authoritative metrology guidance=1; authoritative monograph=3; authoritative professional statement=2; authoritative technical procedure=1; authoritative technical text=2; consensus report=1; editorial/synthesis=1; historical analysis=1; historical engineering handbook=1; historical monograph=4; historical primary-document analysis=1; historical technical handbook=1; historical technical monograph=1; international metrology guide=2; international standard=8; international vocabulary/standard=1; management/statistical monograph=1; official institutional history=1; peer-reviewed analysis=1; peer-reviewed conceptual paper=1; peer-reviewed critical paper=4; peer-reviewed empirical paper=3; peer-reviewed empirical/method paper=1; peer-reviewed historical/review article=1; peer-reviewed methods paper=1; peer-reviewed panel/review=1; peer-reviewed review=1; peer-reviewed technical paper / NIST publication=1; peer-reviewed theory paper=1; peer-reviewed tutorial/critical paper=1; primary applied-method paper=1; primary critical note=1; primary critical paper=1; primary decision-analysis paper=1; primary methodological note=1; primary methods paper=3; primary paper=21; primary policy paper=1; primary professional paper=1; primary technical paper=1; professional association guidance=1; professional reference=1; systematic review=1; systematic/critical review=1; technical monograph=2 |
| Access status | CLOSED=14; LIMITED=3; MIXED=41; OPEN=52 |
| Claim classifications | CONTESTED=4; EMPIRICAL_OR_DOMAIN_FINDING=6; FORMAL_OR_MODEL_DEPENDENT=34; HISTORICAL_INFERENCE=5; SOURCE_ESTABLISHED=44; SOURCE_INTERPRETATION=17 |
| Historical primary/core sources | S001–S032 and school-specific historical records S088–S096 |
| Current NIST/metrology/standards spine | S043–S078, S100–S110 |
| Programme/organisational evidence | S079–S087 |
| Modern adaptive/proxy/domain evidence | S036–S040, S097–S099 |

## EVIDENCE_STRENGTH_PARTITIONS

These counts describe property-level judgements. Strong mathematical validity under assumptions is not counted as evidence that an engineering population satisfies those assumptions.

| Partition | Distribution across 65 properties |
| --- | --- |
| HISTORICAL_PROVENANCE_STRENGTH | VERY_HIGH=12; HIGH=41; MODERATE=11; LOW=1 |
| FORMAL_OR_THEORETICAL_STRENGTH | VERY_HIGH=26; HIGH=31; MODERATE=5; LOW=3 |
| MEASUREMENT_SCIENCE_STRENGTH | VERY_HIGH=8; HIGH=30; MODERATE=23; LOW=4 |
| EMPIRICAL_CAUSAL_STRENGTH | VERY_HIGH=1; HIGH=11; MODERATE=27; LOW=26 |
| EMPIRICAL_ASSOCIATIONAL_STRENGTH | VERY_HIGH=4; HIGH=52; MODERATE=9 |
| DOMAIN_CASE_STRENGTH | VERY_HIGH=28; HIGH=35; MODERATE=2 |
| REPLICATION_STRENGTH | VERY_HIGH=3; HIGH=40; MODERATE=18; LOW=4 |
| TRANSFERABILITY_STRENGTH | VERY_HIGH=14; HIGH=33; MODERATE=11; LOW=7 |
| ASSUMPTION_SENSITIVITY | VERY_HIGH=30; HIGH=18; MODERATE=15; LOW=2 |
| CONTRARY_EVIDENCE_STRENGTH | VERY_HIGH=4; HIGH=26; MODERATE=17; LOW=18 |

## TOP_CROSSWALK_PROPERTIES

All P001–P057 are crosswalk-worthy because each is either retained, evolved, a precondition, a conditional design/control/reliability property, or a transferable anti-gaming/proportionality boundary. The audit must not infer that all should trigger in every target system.

### P001 — Define the decision-relevant measurand or construct before quantification

- **PROPERTY_ID:** `P001`
- **PROPERTY_NAME:** Define the decision-relevant measurand or construct before quantification
- **FAILURE_MODE:** Construct substitution, category drift, metric availability being mistaken for decision relevance.
- **MATURE_FORM:** No metric governs until its intended property, scope, consumer, and admissible interpretation are fixed enough to be challenged.
- **TRIGGER:** Any measurement used to accept, reject, optimise, compare, or monitor an engineering state.
- **CHEAP_PATH:** When an authoritative deterministic fact directly answers the decision, record that fact rather than inventing a surrogate score.
- **MEASUREMENT_PRECONDITIONS:** The operational definition must preserve the distinctions the decision actually requires; an evaluator must not collapse relevant states.
- **ASSUMPTIONS:** The construct is sufficiently coherent for the intended decision and its operationalisation does not change materially across samples.
- **DECISION_OR_CONSUMER:** Design authority, test owner, regulator, operator, or other consumer of the decision.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** MODERATE
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** MODERATE
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** Metrology can define a measurand precisely while still leaving broader validity contested; formal latent constructs add model dependence. Contrary evidence/limit: Construct-validity evidence is domain-dependent; no universal statistical test establishes that a metric means what stakeholders intend.
- **ANTI_CEREMONY_BOUNDARY:** A template or ontology is optional; the property is the explicit decision-linked definition.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact property is the target system claiming to measure?
  - Would two materially different states receive the same score?
  - Is an authoritative deterministic discriminator already available?

### P002 — Establish measurement-system fitness before metric governance

- **PROPERTY_ID:** `P002`
- **PROPERTY_NAME:** Establish measurement-system fitness before metric governance
- **FAILURE_MODE:** Governing a candidate or process with a measurement system unable to discriminate decision-relevant states.
- **MATURE_FORM:** Demonstrate enough discrimination for the intended decision, not abstract “good measurement,” and recheck after material evaluator change.
- **TRIGGER:** Metrics near thresholds, comparisons whose expected effect is small, multi-operator/evaluator systems, or costly decisions.
- **CHEAP_PATH:** For a deterministic binary check with an authoritative oracle and negligible ambiguity, verify the oracle and use it directly rather than perform full MSA.
- **MEASUREMENT_PRECONDITIONS:** The study must span the real operating range and relevant operators, instruments, environments and preprocessing paths.
- **ASSUMPTIONS:** Measurement error is reasonably estimable over the intended range and the study itself has not selected unusually easy samples.
- **DECISION_OR_CONSUMER:** Anyone relying on a metric, threshold, trend or experiment outcome.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide whether observed process/candidate differences exceed measurement variation.
  - **ASSUMED_DATA_GENERATING_PROCESS:** True state plus instrument/operator/environment/evaluator error, possibly heteroscedastic or drifting.
  - **MEASUREMENT_PRECONDITIONS:** Representative range, repeated measures, reference comparisons and version control.
  - **SIGNAL_OR_DISCRIMINATOR:** Variance/bias/uncertainty small enough relative to the decision margin.
  - **FALSE_POSITIVE_COST:** Unnecessary redesign or rejection caused by measurement noise.
  - **FALSE_NEGATIVE_COST:** A real defect hidden by poor resolution or attenuation.
  - **NONSTATIONARITY_RISK:** Calibration/evaluator drift can invalidate earlier decomposition.
  - **INTERVENTION_RISK:** Changing the candidate to chase evaluator noise; changing the evaluator to erase a candidate failure.
  - **CHEAP_PATH:** Direct authoritative check or coarse decision with a very wide margin.
  - **MATURE_FORM:** Decision-specific measurement-capability gate with ongoing checks.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** Gauge R&R is only one design; destructive, automated, subjective and probabilistic evaluators require other designs. Contrary evidence/limit: No single GR&R threshold is universally optimal; measurement investment depends on decision loss and achievable resolution.
- **ANTI_CEREMONY_BOUNDARY:** The form, software package, fixed 10×3×3 design or percentage cutoff is ceremony; decision-linked discrimination is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can the target measurement system discriminate the states that change the decision?
  - How much observed variation is evaluator rather than candidate variation?
  - Would the conclusion survive another competent operator, fixture or evaluator version?

### P003 — Calibration and metrological traceability where decision-relevant

- **PROPERTY_ID:** `P003`
- **PROPERTY_NAME:** Calibration and metrological traceability where decision-relevant
- **FAILURE_MODE:** False comparability, hidden bias, ungrounded units and calibration labels treated as universal validity.
- **MATURE_FORM:** Require the level of traceability needed for comparability and decision risk, alongside—not instead of—fitness validation.
- **TRIGGER:** Physical/chemical measurements, regulated tolerances, interlaboratory exchange, or any decision requiring comparability to a standard.
- **CHEAP_PATH:** For purely ordinal/local decisions with a verified internal reference and no cross-context claim, full national/international traceability may add no value.
- **MEASUREMENT_PRECONDITIONS:** Calibration points and standards must cover the range, matrix and conditions of use.
- **ASSUMPTIONS:** The reference hierarchy and calibration model remain applicable; no unmodelled transport or nonlinear effects dominate.
- **DECISION_OR_CONSUMER:** Laboratory, manufacturer, customer, regulator and downstream analysts.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** LOW
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** NIST explicitly rejects treating traceability as a guarantee of fitness for purpose or absence of mistakes. Contrary evidence/limit: Some digital/subjective measurements lack a meaningful SI chain; analogous provenance does not equal metrological traceability.
- **ANTI_CEREMONY_BOUNDARY:** A certificate, logo or fixed interval is not the property; the evidence chain and decision fitness are.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the result—not merely the instrument—have a documented reference chain and uncertainty?
  - Is cross-site or cross-version comparability actually required for this decision?
  - Could a local deterministic reference provide a cheaper adequate path?

### P004 — Keep bias/accuracy distinct from precision

- **PROPERTY_ID:** `P004`
- **PROPERTY_NAME:** Keep bias/accuracy distinct from precision
- **FAILURE_MODE:** False confidence from tight distributions, many decimals, or repeated agreement around the wrong value.
- **MATURE_FORM:** Decision-specific decomposition of systematic and random error, with correction only when validated.
- **TRIGGER:** Whenever magnitude or direction relative to truth/standard matters, especially near limits.
- **CHEAP_PATH:** If the decision is invariant to a known constant offset and only ranks within one stable system, bias correction may be unnecessary—but must be explicit.
- **MEASUREMENT_PRECONDITIONS:** Enough resolution and coverage to detect both offset and dispersion; uncertainty in the reference included.
- **ASSUMPTIONS:** Bias is reasonably stable or modelled over range/context; reference is more informative than the system under test.
- **DECISION_OR_CONSUMER:** Measurement owner and decision consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** LOW
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Using correlation as accuracy; reporting only standard deviation; reference standard shares the same bias. Contrary evidence/limit: For complex construct measures, “true value” may be unavailable; bias must then be bounded through convergent/criterion evidence rather than asserted. Contrary evidence/limit: For complex construct measures, “true value” may be unavailable; bias must then be bounded through convergent/criterion evidence rather than asserted.
- **ANTI_CEREMONY_BOUNDARY:** Extra decimal places and repeated readings are ceremony when the dominant error is systematic.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Could the target evaluator be consistently wrong despite excellent repeatability?
  - What independent reference or triangulation checks bias?
  - Would more repetitions reduce the dominant uncertainty component?

### P005 — Distinguish repeatability, reproducibility and validity

- **PROPERTY_ID:** `P005`
- **PROPERTY_NAME:** Distinguish repeatability, reproducibility and validity
- **FAILURE_MODE:** Treating identical reruns as independent corroboration or interpreting consistency as truth.
- **MATURE_FORM:** Claim only the level of stability actually tested, and never infer validity from repeatability alone.
- **TRIGGER:** Multi-operator, multi-site, automated evaluator, stochastic test or claimed general result.
- **CHEAP_PATH:** For one-use, one-instrument local control with no transfer claim and a wide margin, a limited stability check may suffice.
- **MEASUREMENT_PRECONDITIONS:** Measurement outputs are comparable and evaluator versions are fixed/documented during the study.
- **ASSUMPTIONS:** Factor effects and interactions can be estimated; repeated conditions approximate intended routine use.
- **DECISION_OR_CONSUMER:** Measurement owner, experimenter and anyone claiming portability.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Determine whether measurement conclusions survive relevant changes of operator/instrument/site/context.
  - **EXPERIMENTAL_UNIT:** Measured item under a specified factor combination.
  - **INDEPENDENCE_ASSUMPTION:** Repeated items or clusters must be modelled; repeated readings on one item are not independent items.
  - **RANDOMISATION_OR_CONTROL:** Randomise order where drift/learning/carryover is possible.
  - **BLOCKING_OR_STRATIFICATION:** Block by item/batch/context when nuisance variation is large.
  - **REPLICATION_MEANING:** Replication means new independent items or justified repeated-measures modelling, not duplicated records.
  - **INTERACTION_RISK:** Operator×item and context×method interactions can dominate.
  - **STOPPING_RULE:** Pre-specify precision/agreement targets and analysis before inspecting favourable subsets.
  - **EXPECTED_INFORMATION_GAIN:** Quantifies which variation source threatens the decision.
  - **COST:** Additional operators/sites/items and possibly destructive samples.
  - **FAILURE_IF_OVER_APPLIED:** A maximal study may be wasteful for a narrow local use.
  - **MATURE_FORM:** Factor-matched reproducibility study plus separate validity evidence.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Confusing reproducibility with exact equality; narrow sample range; no validity criterion; treating reruns as new evidence. Contrary evidence/limit: Definitions of “reproducibility” vary across metrology and science; the factors changed must always be stated. Contrary evidence/limit: Definitions of “reproducibility” vary across metrology and science; the factors changed must always be stated.
- **ANTI_CEREMONY_BOUNDARY:** A standard GR&R worksheet is optional; the factor-appropriate variance/agreement design is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Are repeated results same-condition repeatability or genuinely cross-condition reproducibility?
  - Which operator, site, seed, environment or evaluator factors were varied?
  - What evidence addresses validity rather than consistency?

### P006 — Match resolution, sensitivity, specificity and threshold discrimination to the decision

- **PROPERTY_ID:** `P006`
- **PROPERTY_NAME:** Match resolution, sensitivity, specificity and threshold discrimination to the decision
- **FAILURE_MODE:** False passes/fails hidden by a precise-looking continuous score or an arbitrary threshold.
- **MATURE_FORM:** Use the cheapest discriminator whose error profile is adequate for the decision and freeze/version its threshold unless independent recalibration evidence exists.
- **TRIGGER:** Threshold decisions, defect detection, rare-event screens, small expected improvements, or changing class prevalence.
- **CHEAP_PATH:** When a deterministic authoritative predicate directly distinguishes states, use it instead of estimating sensitivity/specificity.
- **MEASUREMENT_PRECONDITIONS:** Reference labels are sufficiently accurate and the validation set represents intended use; resolution is not inflated by preprocessing leakage.
- **ASSUMPTIONS:** Future cases are drawn from a relevant population or shift is monitored; class definitions remain stable.
- **DECISION_OR_CONSUMER:** Decision owner, safety/quality gate, monitoring operator.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Choose and maintain an action threshold under measurement error and changing prevalence.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Latent state observed through a noisy score/classifier with class-conditional errors.
  - **MEASUREMENT_PRECONDITIONS:** Representative reference labels, uncertainty and threshold versioning.
  - **SIGNAL_OR_DISCRIMINATOR:** Stable separation/calibration sufficient for consequence-weighted decision.
  - **FALSE_POSITIVE_COST:** Alert burden, needless rejection or process tampering.
  - **FALSE_NEGATIVE_COST:** Missed defect or false assurance.
  - **NONSTATIONARITY_RISK:** Prevalence/concept drift changes predictive values and optimal threshold.
  - **INTERVENTION_RISK:** Post-failure threshold movement can reward-hack the metric.
  - **CHEAP_PATH:** Authoritative deterministic predicate with negligible ambiguity.
  - **MATURE_FORM:** Guard-banded/versioned threshold with periodic independent validation.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Selecting threshold on the same test set; ignoring prevalence; changing expected answers after failures; resolution below tolerance width. Contrary evidence/limit: ROC-like summaries may obscure calibration, prevalence shift and heterogeneous costs; no single threshold is universally optimal. Contrary evidence/limit: ROC-like summaries may obscure calibration, prevalence shift and heterogeneous costs; no single threshold is universally optimal.
- **ANTI_CEREMONY_BOUNDARY:** A universal “90% accuracy” or fixed sigma cutoff is ceremony; the decision-specific error surface is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What false-pass and false-fail rates matter at the actual threshold?
  - Is the evaluator’s resolution small enough relative to the decision margin?
  - Can a threshold change be justified on evidence independent of the failed candidate?

### P007 — Carry measurement uncertainty into engineering decisions

- **PROPERTY_ID:** `P007`
- **PROPERTY_NAME:** Carry measurement uncertainty into engineering decisions
- **FAILURE_MODE:** False precision, unsupported conformance, and treating reference or model uncertainty as zero.
- **MATURE_FORM:** Use proportionate uncertainty analysis sufficient to show whether the next action is discriminated.
- **TRIGGER:** Measurements close to specifications, comparisons with small effects, extrapolations, and regulated claims.
- **CHEAP_PATH:** When the result is far from every relevant boundary and a conservative worst-case bound suffices, a detailed budget may be unnecessary.
- **MEASUREMENT_PRECONDITIONS:** Inputs and correlations are characterised over the intended regime; software/preprocessing uncertainty included when material.
- **ASSUMPTIONS:** The propagation model is adequate; uncertainty is not silently conditional on fixed but uncertain calibration/model choices.
- **DECISION_OR_CONSUMER:** Conformance authority, designer, customer or risk owner.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Double-counted components; omitted covariance; confidence interval mislabeled as tolerance interval; uncertainty reported without decision use. Contrary evidence/limit: GUM-style propagation can be strained by nonlinearity, asymmetric tails, model uncertainty and adaptive algorithms; simulation/Bayesian or interval methods may be needed. Contrary evidence/limit: GUM-style propagation can be strained by nonlinearity, asymmetric tails, model uncertainty and adaptive algorithms; simulation/Bayesian or interval methods may be needed.
- **ANTI_CEREMONY_BOUNDARY:** A long budget is ceremony if a dominant bound already resolves the decision; conversely, “±” without a model is decorative.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Would plausible measurement uncertainty cross the action boundary?
  - Which uncertainty component dominates, and can it be reduced economically?
  - Is the interval about a parameter, future observation, or population content?

### P008 — Evaluate inter-rater/evaluator agreement with a design matched to use

- **PROPERTY_ID:** `P008`
- **PROPERTY_NAME:** Evaluate inter-rater/evaluator agreement with a design matched to use
- **FAILURE_MODE:** Stable-looking scores that vary by evaluator, rubric interpretation, operator or model version.
- **MATURE_FORM:** Report disagreement structure, not only one coefficient; block governance where disagreement crosses decision boundaries.
- **TRIGGER:** Subjective ratings, manual inspection, model judging, multi-laboratory tests, or operator-dependent measurements.
- **CHEAP_PATH:** A deterministic reference rule with auditable outputs may need spot verification rather than a full agreement study.
- **MEASUREMENT_PRECONDITIONS:** Raters/evaluators are independent enough to expose variation rather than copied or trained on identical answers.
- **ASSUMPTIONS:** The selected agreement statistic matches fixed/random raters, absolute agreement/consistency and scale properties.
- **DECISION_OR_CONSUMER:** Test owner, adjudicator, quality gate and downstream experimenter.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Determine whether evaluator identity changes the engineering conclusion.
  - **EXPERIMENTAL_UNIT:** Item×evaluator judgement, with item as the generalisation unit.
  - **INDEPENDENCE_ASSUMPTION:** Multiple ratings of one item are clustered; evaluators may share training/rubric dependence.
  - **RANDOMISATION_OR_CONTROL:** Randomise/blind order and candidate identity where possible.
  - **BLOCKING_OR_STRATIFICATION:** Stratify by item difficulty/context and evaluator type.
  - **REPLICATION_MEANING:** Independent items and independently formed judgements, not duplicated outputs.
  - **INTERACTION_RISK:** Evaluator×item interactions identify ambiguous regions.
  - **STOPPING_RULE:** Predefine agreement target and adjudication protocol.
  - **EXPECTED_INFORMATION_GAIN:** Separates stable decisions from evaluator-sensitive ones.
  - **COST:** Rater time, adjudication and representative case construction.
  - **FAILURE_IF_OVER_APPLIED:** Excessive panels can create consensus bureaucracy and common-mode bias.
  - **MATURE_FORM:** Decision-linked agreement study plus construct-validity checks.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Using Pearson correlation; prevalence-sensitive kappa without context; shared rubric bias; adjudicating after seeing candidate identity. Contrary evidence/limit: Agreement can be high because cases are homogeneous or decisions trivial; validity and representativeness remain separate. Contrary evidence/limit: Agreement can be high because cases are homogeneous or decisions trivial; validity and representativeness remain separate.
- **ANTI_CEREMONY_BOUNDARY:** A fashionable reliability coefficient or arbitrary cutoff is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Do evaluators agree on the actual action, not just rank ordering?
  - Were difficult and boundary cases represented?
  - Could shared training data or rubric bias make agreement non-independent?

### P009 — Test measurement invariance and transport across contexts

- **PROPERTY_ID:** `P009`
- **PROPERTY_NAME:** Test measurement invariance and transport across contexts
- **FAILURE_MODE:** Invalid cross-context comparisons, hidden subgroup bias and false trend attribution.
- **MATURE_FORM:** Claim equivalence only over tested contexts; otherwise maintain context-specific calibration or explicit uncertainty.
- **TRIGGER:** Cross-site benchmarking, longitudinal monitoring, heterogeneous users, distribution shift or environment changes.
- **CHEAP_PATH:** No invariance study is needed for an explicitly local, one-time decision that makes no comparison beyond its validated context.
- **MEASUREMENT_PRECONDITIONS:** The measurement process and sampling frame are observable enough to distinguish construct shift from composition shift.
- **ASSUMPTIONS:** Observed contexts span the intended deployment; unobserved effect modifiers are bounded or acknowledged.
- **DECISION_OR_CONSUMER:** Benchmark owner, product/system decision maker, regulator or cross-site analyst.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide whether a change in score reflects a changed target state or changed measurement context.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Context-indexed latent property observed through context-sensitive measurement and sampling.
  - **MEASUREMENT_PRECONDITIONS:** Comparable anchors/reference outcomes and context metadata.
  - **SIGNAL_OR_DISCRIMINATOR:** Stable calibration/construct relation or an identified context effect.
  - **FALSE_POSITIVE_COST:** False process intervention due to composition/evaluator shift.
  - **FALSE_NEGATIVE_COST:** Failure to detect real subgroup/context degradation.
  - **NONSTATIONARITY_RISK:** High: deployment populations and instruments evolve.
  - **INTERVENTION_RISK:** Global recalibration can erase local failures; local tuning can destroy comparability.
  - **CHEAP_PATH:** Restrict the claim to the validated context.
  - **MATURE_FORM:** Versioned context-specific calibration with transport tests and drift alarms.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Aggregate invariance hiding subgroup failure; recalibration on contaminated outcomes; using identical preprocessing as proof of meaning. Contrary evidence/limit: No finite study guarantees future invariance under open-ended distribution shift; monitoring and bounded claims are required. Contrary evidence/limit: No finite study guarantees future invariance under open-ended distribution shift; monitoring and bounded claims are required.
- **ANTI_CEREMONY_BOUNDARY:** One global score or normalisation recipe is ceremony when meanings differ.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Has the score retained calibration and meaning across the contexts being compared?
  - Could a changed population mix explain the apparent process change?
  - Is a context-specific metric safer than forced global invariance?

### P010 — Monitor evaluator/instrument drift and require independent recalibration evidence

- **PROPERTY_ID:** `P010`
- **PROPERTY_NAME:** Monitor evaluator/instrument drift and require independent recalibration evidence
- **FAILURE_MODE:** Attributing measurement change to the object; changing the evaluator after failure until a pass appears.
- **MATURE_FORM:** Recalibrate when independent evidence shows measurement defect or context change; preserve old/new bridge and re-evaluate prior conclusions where material.
- **TRIGGER:** Long-lived controls, automated scoring, model-based evaluators, changing laboratories or any metric with material maintenance.
- **CHEAP_PATH:** For a one-shot destructive test with contemporaneous references, ongoing drift monitoring may be impossible; preserve calibration evidence and uncertainty instead.
- **MEASUREMENT_PRECONDITIONS:** Check samples represent important ranges and are protected from optimisation/contamination.
- **ASSUMPTIONS:** Reference drift is slower or independently detectable; repeated checks are not all affected by the same environmental cause.
- **DECISION_OR_CONSUMER:** Measurement owner, release/acceptance authority and audit consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Detect whether the measurement process, rather than the object, has changed.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Stable/slowly varying references observed through a potentially drifting evaluator.
  - **MEASUREMENT_PRECONDITIONS:** Protected check samples, version metadata and bridge overlap.
  - **SIGNAL_OR_DISCRIMINATOR:** Reference/control deviation beyond a consequence-weighted drift boundary.
  - **FALSE_POSITIVE_COST:** Unnecessary recalibration and broken comparability.
  - **FALSE_NEGATIVE_COST:** Persistent biased governance or hidden evaluator degradation.
  - **NONSTATIONARITY_RISK:** Reference populations and constructs may drift too.
  - **INTERVENTION_RISK:** Rebaselining to current outputs can erase evidence.
  - **CHEAP_PATH:** Manual reference comparison before a high-stakes decision.
  - **MATURE_FORM:** Independent bridge study, versioned change control and bounded revalidation.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Rebaselining after alarms; editing expected answers after seeing failures; check-set overfitting; no version bridge. Contrary evidence/limit: Reference materials and holdouts can themselves age, leak or become unrepresentative; drift detection has no absolute anchor without external refresh. Contrary evidence/limit: Reference materials and holdouts can themselves age, leak or become unrepresentative; drift detection has no absolute anchor without external refresh.
- **ANTI_CEREMONY_BOUNDARY:** A calendar recalibration interval or automatic threshold refresh is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What evidence distinguishes evaluator drift from candidate/process change?
  - Was recalibration justified using evidence independent of the failed candidate?
  - Is there a bridge allowing old and new evaluator versions to be compared?

### P011 — Use representative reference standards and challenge shared-reference bias

- **PROPERTY_ID:** `P011`
- **PROPERTY_NAME:** Use representative reference standards and challenge shared-reference bias
- **FAILURE_MODE:** False validation from easy, narrow, contaminated or common-mode reference samples.
- **MATURE_FORM:** Reference evidence is valid only for the covered range/context and must be protected from optimisation.
- **TRIGGER:** Calibration transfer, evaluator validation, threshold setting and cross-site comparison.
- **CHEAP_PATH:** For a single known artefact or exact digital identity check, one authoritative reference may be enough.
- **MEASUREMENT_PRECONDITIONS:** Reference uncertainty and commutability/representativeness are known; reference items are not leaked into optimisation.
- **ASSUMPTIONS:** Sampled references cover decision-relevant variability and do not share all defects with the candidate measurement.
- **DECISION_OR_CONSUMER:** Calibration laboratory, evaluator owner and downstream decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** MODERATE
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Using only pristine standards; treating consensus as truth; reusing public benchmarks until memorised; excluding failures from the reference pool. Contrary evidence/limit: Representativeness cannot be proven exhaustively; rare or emerging failure modes may be absent. Contrary evidence/limit: Representativeness cannot be proven exhaustively; rare or emerging failure modes may be absent.
- **ANTI_CEREMONY_BOUNDARY:** A named standard material or benchmark is not sufficient if it is nonrepresentative.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Do reference samples span actual boundary and failure cases?
  - Could candidate and reference share the same systematic defect?
  - Has optimisation exposure contaminated the reference set?

### P012 — Preserve data provenance, preprocessing, version and lineage

- **PROPERTY_ID:** `P012`
- **PROPERTY_NAME:** Preserve data provenance, preprocessing, version and lineage
- **FAILURE_MODE:** Irreproducible evidence, hidden leakage, duplicate evidence and inability to separate data change from process change.
- **MATURE_FORM:** Preserve the minimum complete lineage needed to reconstruct the evidence and its dependence structure.
- **TRIGGER:** Any multi-stage analysis, reused benchmark, merged source, adaptive evaluation or longitudinal comparison.
- **CHEAP_PATH:** A small manually inspectable deterministic dataset may need only a concise signed record, not a full data platform.
- **MEASUREMENT_PRECONDITIONS:** Preprocessing is deterministic or its randomness/configuration is recorded; lineage captures duplication and dependence.
- **ASSUMPTIONS:** Recorded provenance is complete enough to reconstruct decision-relevant transformations.
- **DECISION_OR_CONSUMER:** Analyst, reviewer, regulator, future maintainer and experiment consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** MODERATE
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Overwriting raw data; undocumented manual fixes; copied observations counted as independent; changing labels without bridge. Contrary evidence/limit: Provenance proves what happened, not that the recorded process was unbiased or valid. Contrary evidence/limit: Provenance proves what happened, not that the recorded process was unbiased or valid.
- **ANTI_CEREMONY_BOUNDARY:** A particular tool, schema or immutable ledger is optional; reconstructability and identity are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can every reported result be tied to exact data, preprocessing, evaluator and threshold versions?
  - Are duplicated or derived observations being counted as independent evidence?
  - Can excluded measurements be audited with reasons?

### P013 — Model missingness, censoring, exclusions and selection mechanisms

- **PROPERTY_ID:** `P013`
- **PROPERTY_NAME:** Model missingness, censoring, exclusions and selection mechanisms
- **FAILURE_MODE:** Survivorship bias, complete-case bias, favourable subgroup selection and underreported failure tails.
- **MATURE_FORM:** Make the observation/selection process auditable and report conclusions conditional on or robust to plausible missingness mechanisms.
- **TRIGGER:** Dropout, time-limited tests, incomplete logs, destructive failures, filtered benchmark items or unobserved outcomes.
- **CHEAP_PATH:** If missingness is demonstrably negligible and unrelated to outcome/exposure, transparent complete-case treatment may be adequate.
- **MEASUREMENT_PRECONDITIONS:** The system distinguishes “not observed,” “not applicable,” “failed before measurement,” and deliberate exclusion.
- **ASSUMPTIONS:** Chosen MAR/MCAR/censoring/selection assumptions approximate reality; sensitivity bounds cover uncertainty.
- **DECISION_OR_CONSUMER:** Reliability analyst, experimenter, quality gate and consumer of aggregate metrics.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate effect/performance despite incomplete outcomes without hiding selection.
  - **EXPERIMENTAL_UNIT:** Originally eligible experimental or observational unit, including censored units.
  - **INDEPENDENCE_ASSUMPTION:** Missingness can induce dependence/selection; clusters remain clusters.
  - **RANDOMISATION_OR_CONTROL:** Randomisation protects assignment but not post-assignment missingness.
  - **BLOCKING_OR_STRATIFICATION:** Stratify/design follow-up around predictors of missingness.
  - **REPLICATION_MEANING:** Replication counts eligible independent units, not only completed observations.
  - **INTERACTION_RISK:** Treatment/context can interact with dropout/censoring.
  - **STOPPING_RULE:** Pre-specify exclusion and censoring rules; document deviations.
  - **EXPECTED_INFORMATION_GAIN:** Recovers or bounds decision-relevant estimates and exposes uncertainty.
  - **COST:** Follow-up, instrumentation and larger sample requirements.
  - **FAILURE_IF_OVER_APPLIED:** Complex imputation can become decorative if assumptions are unknowable.
  - **MATURE_FORM:** Transparent mechanism model plus sensitivity/bounds and all-unit accounting.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Calling failures “invalid”; censoring at different risk states; post-hoc subgroup restriction; imputation model trained on outcome leakage. Contrary evidence/limit: Missing-not-at-random mechanisms are generally not identified from observed data alone; sensitivity/partial identification may be the honest endpoint. Contrary evidence/limit: Missing-not-at-random mechanisms are generally not identified from observed data alone; sensitivity/partial identification may be the honest endpoint.
- **ANTI_CEREMONY_BOUNDARY:** Automatic imputation or a missing-data checklist is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which attempted units or outcomes are absent, censored or excluded?
  - Could exclusion probability depend on failure severity or candidate identity?
  - Would plausible missing-not-at-random scenarios change the decision?

### P014 — Account for measurement intervention, destruction and contamination

- **PROPERTY_ID:** `P014`
- **PROPERTY_NAME:** Account for measurement intervention, destruction and contamination
- **FAILURE_MODE:** Pseudo-replication, induced failures, test-set learning and claiming non-destructive evidence from altered units.
- **MATURE_FORM:** Use fresh or counterbalanced units where material; otherwise model and report intervention history and limit claims.
- **TRIGGER:** Destructive material tests, accelerated stress, human/agent learning, repeated benchmark exposure, cache/warm-up effects.
- **CHEAP_PATH:** When a verified measurement is genuinely non-invasive and order-invariant, ordinary repeated-measures methods may suffice.
- **MEASUREMENT_PRECONDITIONS:** Provenance records prior exposures and distinguishes unit reuse from independent replication.
- **ASSUMPTIONS:** Carryover/washout model is plausible or fresh independent units are available.
- **DECISION_OR_CONSUMER:** Experiment designer, reliability/test engineer and benchmark owner.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Determine performance/effect without confounding it with prior measurement exposure.
  - **EXPERIMENTAL_UNIT:** Fresh unit or explicitly exposure-indexed repeated unit.
  - **INDEPENDENCE_ASSUMPTION:** Repeated observations on altered units are dependent.
  - **RANDOMISATION_OR_CONTROL:** Randomise test order/exposure; use controls or fresh units.
  - **BLOCKING_OR_STRATIFICATION:** Block by batch, order, prior exposure or stress level.
  - **REPLICATION_MEANING:** Independent replication requires unexposed units or a correct carryover model.
  - **INTERACTION_RISK:** Exposure×candidate/context interactions may be the main effect.
  - **STOPPING_RULE:** Predefine retest/washout and stopping rules.
  - **EXPECTED_INFORMATION_GAIN:** Separates intrinsic behaviour from measurement-induced adaptation/damage.
  - **COST:** Fresh samples, destructive loss, washout time.
  - **FAILURE_IF_OVER_APPLIED:** Full fresh-unit designs may be prohibitive.
  - **MATURE_FORM:** Exposure-aware design with fresh-unit cheap path only where decision consequences justify it.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** MODERATE
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Calling warmed/cached retries independent; destructive test sample not representative; training on failed benchmark items; inadequate washout. Contrary evidence/limit: In adaptive systems, measurement and improvement may be inseparable by design; the goal becomes explicit online-learning evaluation rather than pretending independence. Contrary evidence/limit: In adaptive systems, measurement and improvement may be inseparable by design; the goal becomes explicit online-learning evaluation rather than pretending independence.
- **ANTI_CEREMONY_BOUNDARY:** A blanket ban on retesting is not the property; exposure-aware evidence is.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 evidence proportionality and P042 deterministic precedence can limit measurement burden; P009 context specificity can conflict with universal standardisation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does running the measurement change the unit, evaluator, cache, operator or future candidate?
  - Are retries fresh independent units or exposed repetitions?
  - Is test exposure part of the intended deployment, and if so is it evaluated as such?

### P015 — Discriminate routine/common variation from evidence of a changed process

- **PROPERTY_ID:** `P015`
- **PROPERTY_NAME:** Discriminate routine/common variation from evidence of a changed process
- **FAILURE_MODE:** Tampering, alert fatigue, blame, missed assignable mechanisms and invalid prediction from unstable data.
- **MATURE_FORM:** Use the lightest calibrated discriminator that separates expected variation from actionable change, then require causal investigation before intervention.
- **TRIGGER:** Repeated process output where a stable-enough reference regime and actionable changes are plausible.
- **CHEAP_PATH:** For a deterministic failure with an authoritative cause, repair it directly; for one-off heterogeneous work with no repeatable unit, causal case analysis may dominate charting.
- **MEASUREMENT_PRECONDITIONS:** Measurement error is small enough and evaluator drift is separated from process drift.
- **ASSUMPTIONS:** The baseline is sufficiently homogeneous/stable for the chosen chart/model; dependence and mixtures are handled.
- **DECISION_OR_CONSUMER:** Process owner and investigator—not a mechanism-free automated punishment system.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide when a process departure warrants investigation or intervention.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Approximately stable baseline plus occasional changes, or an explicitly modelled dynamic process.
  - **MEASUREMENT_PRECONDITIONS:** Time-ordered comparable measurements with controlled evaluator variation.
  - **SIGNAL_OR_DISCRIMINATOR:** A signal with known/estimated operating characteristics relative to a target change.
  - **FALSE_POSITIVE_COST:** Wasted investigation, alert fatigue and tampering.
  - **FALSE_NEGATIVE_COST:** Undetected degradation or delayed containment.
  - **NONSTATIONARITY_RISK:** High if the baseline, population or operating policy changes.
  - **INTERVENTION_RISK:** Immediate adjustment to noise can increase variation and obscure causes.
  - **CHEAP_PATH:** Direct mechanism evidence or a simple visual/time-order check for large changes.
  - **MATURE_FORM:** Calibrated monitoring plus investigation, error costs and rebaseline governance.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The two-cause vocabulary can oversimplify continuous, interacting and drifting sources; “special” is statistical, not moral or personal. Contrary evidence/limit: In highly adaptive or nonstationary systems there may be no enduring common-cause baseline; change detection must be reframed around local regimes or forecasts.
- **ANTI_CEREMONY_BOUNDARY:** The property is discrimination and response discipline, not putting every metric on a three-sigma chart.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system distinguish expected variation from evidence of a changed process?
  - Is a chart signal being mistaken for a proven causal mechanism?
  - Could the apparent change instead be evaluator or population drift?

### P016 — Choose rational subgroups and model dependence rather than count correlated observations as sample size

- **PROPERTY_ID:** `P016`
- **PROPERTY_NAME:** Choose rational subgroups and model dependence rather than count correlated observations as sample size
- **FAILURE_MODE:** Wrong control limits, attenuated/expanded uncertainty, false replication and concealed between-batch/time effects.
- **MATURE_FORM:** Match the unit of evidence and correlation model to the unit of action; disclose residual dependence.
- **TRIGGER:** Batch, lot, repeated-run, time-series, nested, clustered or same-seed/same-environment observations.
- **CHEAP_PATH:** When observations are demonstrably independent and identically produced at the decision scale, ordinary independent analysis is adequate.
- **MEASUREMENT_PRECONDITIONS:** Measurement repeats are labelled separately from production units; common-source dependence is observable.
- **ASSUMPTIONS:** Within-subgroup homogeneity and between-subgroup opportunity for relevant change, or a valid dependence model.
- **DECISION_OR_CONSUMER:** Monitoring designer, experimenter and evidence consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Set limits/uncertainty at the correct process and intervention unit.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Nested/clustered/time-correlated observations with within- and between-group variation.
  - **MEASUREMENT_PRECONDITIONS:** Identifiers for cluster, order, batch, seed, operator and repeated measurement.
  - **SIGNAL_OR_DISCRIMINATOR:** Between/within decomposition or dependence-adjusted statistic.
  - **FALSE_POSITIVE_COST:** False alarms or apparent significance from underestimated variance.
  - **FALSE_NEGATIVE_COST:** Hidden shifts if inappropriate averaging dilutes between-group change.
  - **NONSTATIONARITY_RISK:** Correlation structure itself can drift.
  - **INTERVENTION_RISK:** Adjusting individual readings when the actionable cause is batch/system-level.
  - **CHEAP_PATH:** Use cluster summaries or conservative effective sample size when modelling is not worth the cost.
  - **MATURE_FORM:** Rational grouping or explicit hierarchical/time-series analysis tied to action.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** “Rational subgroup” is not a magic recipe; it encodes a causal/process judgement and may fail in low-volume/high-mix work. Contrary evidence/limit: Dependence can be difficult to estimate with few clusters or changing correlation; conservative bounds may be preferable to elaborate fitted models.
- **ANTI_CEREMONY_BOUNDARY:** Fixed subgroup sizes or an X-bar/R worksheet are implementation choices, not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What is the independent experimental/process unit?
  - Are repeated same-seed, same-batch or same-evaluator observations being counted as independent?
  - Do subgroup boundaries correspond to plausible variation mechanisms?

### P017 — Keep statistical control limits separate from engineering specifications and tolerances

- **PROPERTY_ID:** `P017`
- **PROPERTY_NAME:** Keep statistical control limits separate from engineering specifications and tolerances
- **FAILURE_MODE:** False assurance, inappropriate alarms and using customer limits as if statistically calibrated.
- **MATURE_FORM:** Use control limits for change detection, specifications for requirements, and guard bands/decision rules for uncertain conformance.
- **TRIGGER:** Any monitored characteristic with both process history and an external requirement.
- **CHEAP_PATH:** For an exact deterministic requirement checked once, a control chart may be unnecessary; use the specification directly with measurement uncertainty.
- **MEASUREMENT_PRECONDITIONS:** Uncertainty near specifications is quantified; specification source/version is fixed.
- **ASSUMPTIONS:** Control-limit estimation reflects the intended baseline; specs are independent of recent sample behaviour.
- **DECISION_OR_CONSUMER:** Process owner, design authority, customer/regulator and conformance decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Separate detection of process change from conformance to an external requirement.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Process distribution over time plus independent specification boundaries.
  - **MEASUREMENT_PRECONDITIONS:** Stable measurement scale and uncertainty near boundaries.
  - **SIGNAL_OR_DISCRIMINATOR:** Control signal for change; guard-banded result for conformance.
  - **FALSE_POSITIVE_COST:** Investigating common variation or rejecting conforming output.
  - **FALSE_NEGATIVE_COST:** Failing to improve a stable but incapable process.
  - **NONSTATIONARITY_RISK:** Specs or process regimes may change and require separately versioned baselines.
  - **INTERVENTION_RISK:** Widening either limit after failure can erase evidence.
  - **CHEAP_PATH:** Direct deterministic spec check where monitoring adds no decision value.
  - **MATURE_FORM:** Semantically separate control, specification and uncertainty decision rules.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** Three-sigma conventions are not tolerances, and neither system identifies root cause. Contrary evidence/limit: Specifications themselves may be poorly justified or gamed; statistical separation does not validate the requirement.
- **ANTI_CEREMONY_BOUNDARY:** One dashboard may display all limits, but their meanings must not be merged.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Are requirements/specifications being confused with statistical control limits?
  - Could the process be stable but incapable, or unstable but currently in specification?
  - Is measurement uncertainty included in conformance decisions?

### P018 — Establish process stability before interpreting capability or long-run prediction

- **PROPERTY_ID:** `P018`
- **PROPERTY_NAME:** Establish process stability before interpreting capability or long-run prediction
- **FAILURE_MODE:** Predicting future conformance from an unstable historical mixture.
- **MATURE_FORM:** State the regime and prediction horizon; no unconditional capability claim from unresolved drift/mixture.
- **TRIGGER:** Capability, tolerance yield, long-run defect rate or predictive performance claims.
- **CHEAP_PATH:** For a deterministic design proof or 100% authoritative inspection, a statistical capability index may be irrelevant.
- **MEASUREMENT_PRECONDITIONS:** Evaluator/measurement process is itself stable and capable enough to observe process change.
- **ASSUMPTIONS:** Future conditions reasonably resemble the characterised regime or are explicitly modelled.
- **DECISION_OR_CONSUMER:** Process/design owner, supplier/customer and regulator.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide whether historical output supports future capability prediction.
  - **ASSUMED_DATA_GENERATING_PROCESS:** A stable or explicitly regime-indexed process distribution.
  - **MEASUREMENT_PRECONDITIONS:** Chronological, comparable measurements and stable evaluator.
  - **SIGNAL_OR_DISCRIMINATOR:** No material unresolved shifts/mixtures for the stated horizon, or a validated dynamic model.
  - **FALSE_POSITIVE_COST:** Delaying a useful conditional claim through excessive stationarity demands.
  - **FALSE_NEGATIVE_COST:** False long-run conformance assurance from unstable pooled data.
  - **NONSTATIONARITY_RISK:** Central risk; local stability may expire.
  - **INTERVENTION_RISK:** Rebaselining can convert instability into apparent capability.
  - **CHEAP_PATH:** Use conditional descriptive yield without predictive claim.
  - **MATURE_FORM:** Capability explicitly conditional on regime, horizon and measurement fitness.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** Finite data cannot prove permanent stability; “stable enough for this prediction horizon” is the mature claim. Contrary evidence/limit: Some systems are intentionally nonstationary; capability may need scenario/conditional performance rather than a single process distribution.
- **ANTI_CEREMONY_BOUNDARY:** A mandatory chart is not necessary if equivalent stability evidence exists; the prerequisite is evidential.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Was stability assessed in time order before capability was reported?
  - Does the capability number pool distinct products, regimes, populations or evaluator versions?
  - What prediction horizon and operating conditions does the claim cover?

### P019 — Use capability indices only conditionally on stability, distribution and measurement fitness

- **PROPERTY_ID:** `P019`
- **PROPERTY_NAME:** Use capability indices only conditionally on stability, distribution and measurement fitness
- **FAILURE_MODE:** Sigma-score theatre, unsupported defect-rate conversion and supplier ranking on invalid indices.
- **MATURE_FORM:** A conditional summary—not evidence of control, causality or universal “sigma level.”
- **TRIGGER:** High-volume repeatable processes where a stable distribution and specification-based decision exist.
- **CHEAP_PATH:** Use direct yield/tolerance evidence, deterministic limits, or scenario-specific performance when assumptions fail or sample is tiny.
- **MEASUREMENT_PRECONDITIONS:** Measurement variation is small or incorporated; rounding/censoring do not dominate.
- **ASSUMPTIONS:** Selected index/distribution describes the regime and tail behaviour; sample size supports intended precision.
- **DECISION_OR_CONSUMER:** Process engineer, supplier/customer and quality planner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Summarise whether a stable process can meet specifications.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Stable/regime-specific distribution with known specification limits.
  - **MEASUREMENT_PRECONDITIONS:** Adequate resolution, low enough measurement error and representative samples.
  - **SIGNAL_OR_DISCRIMINATOR:** Estimated margin/yield with uncertainty under an adequate model.
  - **FALSE_POSITIVE_COST:** Gaming a scalar target or rejecting acceptable conditional performance.
  - **FALSE_NEGATIVE_COST:** False assurance in tails or under drift.
  - **NONSTATIONARITY_RISK:** Invalidates static indices unless modelled.
  - **INTERVENTION_RISK:** Changing limits/specs or excluding tails to improve index.
  - **CHEAP_PATH:** Direct empirical yield/margin or deterministic tolerance analysis.
  - **MATURE_FORM:** Conditional index with raw plots, uncertainty and assumption checks.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Cpk on unstable data; normal DPMO conversion under skew/dependence; ignoring confidence intervals; choosing the most favourable index. Contrary evidence/limit: Tail defect-rate claims can be dominated by model error far beyond observed data; index precision is not tail certainty. Contrary evidence/limit: Tail defect-rate claims can be dominated by model error far beyond observed data; index precision is not tail certainty.
- **ANTI_CEREMONY_BOUNDARY:** The index and threshold are optional tools; margin/yield evidence under valid assumptions is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Are capability prerequisites—stability, measurement fitness and distribution—demonstrated?
  - Is a sigma/DPMO conversion extrapolating far beyond observed data?
  - Would direct yield or deterministic margin communicate the decision more honestly?

### P020 — Prevent tampering and overadjustment to routine variation

- **PROPERTY_ID:** `P020`
- **PROPERTY_NAME:** Prevent tampering and overadjustment to routine variation
- **FAILURE_MODE:** Operator blame, parameter chasing, endless threshold tuning and regression-to-the-mean misread as improvement.
- **MATURE_FORM:** No reactive adjustment without a discriminator or planned experiment whose expected value exceeds intervention risk.
- **TRIGGER:** Feedback-controlled processes, manual tuning, metric dashboards, repeated reviews and near-threshold variation.
- **CHEAP_PATH:** Correct an authoritative deterministic defect immediately; no statistical wait is needed when mechanism/effect is known.
- **MEASUREMENT_PRECONDITIONS:** The metric is stable enough that an adjustment response is not triggered by evaluator noise.
- **ASSUMPTIONS:** Unadjusted process has a meaningful baseline and feedback dynamics are understood enough to avoid instability.
- **DECISION_OR_CONSUMER:** Operator, process owner and change authority.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide whether to adjust a process after an observation.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Stable process plus feedback response to interventions, possibly with drift.
  - **MEASUREMENT_PRECONDITIONS:** Reliable time-ordered metric and known action latency.
  - **SIGNAL_OR_DISCRIMINATOR:** Calibrated signal or mechanism evidence beyond routine variation.
  - **FALSE_POSITIVE_COST:** Adjustment-induced variance, oscillation and wasted investigation.
  - **FALSE_NEGATIVE_COST:** Delayed response to real deterioration.
  - **NONSTATIONARITY_RISK:** Changes optimal sensitivity and action cadence.
  - **INTERVENTION_RISK:** Core risk: feedback to noise destabilises the process.
  - **CHEAP_PATH:** Direct correction for a known deterministic defect.
  - **MATURE_FORM:** Predefined response rules plus post-intervention evaluation.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** “Do not tamper” must not become “never improve”; designed experiments deliberately change a process under controlled learning. Contrary evidence/limit: In rapidly drifting environments, delayed adaptation can be worse than overadjustment; adaptive control must model that trade-off.
- **ANTI_CEREMONY_BOUNDARY:** A fixed run rule is not the property; disciplined response to evidence is.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target system change the candidate/process because of noise rather than a discriminating signal?
  - Could regression to the mean explain the apparent improvement after intervention?
  - Is the intervention a controlled experiment or untracked parameter chasing?

### P021 — Design monitoring economically around false-alarm, missed-shift and delay costs

- **PROPERTY_ID:** `P021`
- **PROPERTY_NAME:** Design monitoring economically around false-alarm, missed-shift and delay costs
- **FAILURE_MODE:** Run-rule ritual, alert fatigue, hidden detection delay and sampling costs exceeding prevention value.
- **MATURE_FORM:** Select the smallest monitoring design that detects decision-relevant change at acceptable false-alarm/delay cost.
- **TRIGGER:** Ongoing monitoring with repeated opportunities, finite response capacity and quantifiable consequences.
- **CHEAP_PATH:** For rare high-consequence events with a deterministic safety interlock, use the interlock; for low-cost obvious defects, direct inspection may dominate statistical detection.
- **MEASUREMENT_PRECONDITIONS:** Sampling/measurement burden and false-alarm mechanisms are known; alerts can be investigated.
- **ASSUMPTIONS:** Operating-characteristic calculations approximate real dependence/nonstationarity and cost model includes tail consequences.
- **DECISION_OR_CONSUMER:** Monitoring designer, operator and risk/economic decision owner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Choose monitoring cadence/statistic/threshold.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Baseline and specified change scenarios with repeated sampling.
  - **MEASUREMENT_PRECONDITIONS:** Stable measurement and estimated sampling/response costs.
  - **SIGNAL_OR_DISCRIMINATOR:** Operating-characteristic or simulated detection performance.
  - **FALSE_POSITIVE_COST:** Alert load, investigation cost and tampering.
  - **FALSE_NEGATIVE_COST:** Damage accumulated before detection.
  - **NONSTATIONARITY_RISK:** Can invalidate expected ARL/delay and cost optimum.
  - **INTERVENTION_RISK:** Rules tuned after incidents can overfit and trigger churn.
  - **CHEAP_PATH:** Manual periodic review or deterministic interlock for obvious/high-consequence states.
  - **MATURE_FORM:** Scenario-robust, capacity-aware monitoring with explicit error costs.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** Economic design is powerful but assumption-sensitive and must incorporate non-economic constraints where relevant. Contrary evidence/limit: Cost and shift distributions are often uncertain; robust/minimax or scenario designs may be more honest than a single optimum.
- **ANTI_CEREMONY_BOUNDARY:** Three sigma, eight run rules or a dashboard cadence are not universal properties.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What shift is the monitor designed to detect, with what delay and false-alarm burden?
  - Can the organisation investigate the alerts generated by added run rules?
  - Does another measurement have positive expected decision value?

### P022 — Adapt monitoring to autocorrelation, seasonality, drift and nonstationarity

- **PROPERTY_ID:** `P022`
- **PROPERTY_NAME:** Adapt monitoring to autocorrelation, seasonality, drift and nonstationarity
- **FAILURE_MODE:** False alarms, missed shifts, invalid limits and rebaselining every natural cycle.
- **MATURE_FORM:** Use a transparent dynamic baseline with validated detection properties and explicit rebaseline/change-control rules.
- **TRIGGER:** Metrics with temporal dependence, seasonality, learning curves, policy changes or concept drift.
- **CHEAP_PATH:** A large deterministic discontinuity can be handled directly; sparse heterogeneous events may need case-based analysis rather than fitted time series.
- **MEASUREMENT_PRECONDITIONS:** Evaluator/context changes are versioned; missingness and changing exposure denominators are handled.
- **ASSUMPTIONS:** Dynamic model/residuals capture enough structure; change-point method’s calibration approximates deployment.
- **DECISION_OR_CONSUMER:** Process owner, forecasting/monitoring team and policy controller.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Detect harmful change in a temporally structured process.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Autocorrelated/seasonal/regime-switching process with interventions.
  - **MEASUREMENT_PRECONDITIONS:** Stable timestamped measurement and denominator/context metadata.
  - **SIGNAL_OR_DISCRIMINATOR:** Forecast residual, change-point score or regime-conditioned statistic with calibrated delay/error.
  - **FALSE_POSITIVE_COST:** Persistent spurious alerts and overfitting.
  - **FALSE_NEGATIVE_COST:** Slow or model-conforming degradation missed.
  - **NONSTATIONARITY_RISK:** Defining feature; calibration expires under unmodelled shifts.
  - **INTERVENTION_RISK:** Rebaselining or model refit may erase incidents.
  - **CHEAP_PATH:** Stratify by obvious season/regime or use a deterministic event rule.
  - **MATURE_FORM:** Validated local/dynamic monitor plus independent model-drift checks.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** No universal evolved chart exists; classical methods are narrowed, not simply replaced. Contrary evidence/limit: Under adversarial or abrupt concept change, historical calibration may fail exactly when needed; guarantees are local/conditional.
- **ANTI_CEREMONY_BOUNDARY:** “Use an AI anomaly detector” is not the property; calibrated discrimination and interpretable response remain required.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Are iid/stationarity assumptions plausible for the monitored sequence?
  - Has seasonality or policy change been modelled rather than called a defect?
  - Could residual modelling be hiding a materially changed mechanism?

### P023 — Stratify mixtures, high-mix/low-volume and changing populations before aggregation

- **PROPERTY_ID:** `P023`
- **PROPERTY_NAME:** Stratify mixtures, high-mix/low-volume and changing populations before aggregation
- **FAILURE_MODE:** Simpson-type reversals, impossible common limits, false capability and aggregate metric gaming.
- **MATURE_FORM:** Show both relevant strata and an explicitly weighted aggregate; freeze/justify weighting and monitor composition.
- **TRIGGER:** High-mix low-volume production, heterogeneous workloads, changing severity/population or sparse per-type data.
- **CHEAP_PATH:** If all units share the same decision distribution and mixture is stable/irrelevant, aggregate monitoring may be the cheapest valid path.
- **MEASUREMENT_PRECONDITIONS:** Measurement is invariant or separately calibrated across strata.
- **ASSUMPTIONS:** Within-stratum models or standardisation preserve relevant tail/interaction behaviour; no hidden confounding remains.
- **DECISION_OR_CONSUMER:** Portfolio/process owner and consumers of aggregate dashboards.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Detect change without confusing it with mixture/composition change.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Mixture of heterogeneous strata with possibly changing weights.
  - **MEASUREMENT_PRECONDITIONS:** Stratum identity, invariant measurement and denominators.
  - **SIGNAL_OR_DISCRIMINATOR:** Within-stratum or mix-standardised change plus composition monitor.
  - **FALSE_POSITIVE_COST:** Multiple alerts and false subgroup discoveries.
  - **FALSE_NEGATIVE_COST:** Local degradation hidden by favourable mix.
  - **NONSTATIONARITY_RISK:** Mixture weights and strata can evolve.
  - **INTERVENTION_RISK:** Changing weights/exclusions can manufacture improvement.
  - **CHEAP_PATH:** Monitor the dominant/high-risk strata and a transparent aggregate.
  - **MATURE_FORM:** Hierarchical or stratified monitoring with fixed/justified weights.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** Short-run charts help but are domain-specific and assumption-sensitive; hierarchical pooling may be preferable. Contrary evidence/limit: With very sparse strata, estimates depend strongly on hierarchical priors/model sharing; no purely data-driven partition is definitive.
- **ANTI_CEREMONY_BOUNDARY:** A mandatory chart per SKU or one universal standardised score are both ceremonial extremes.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Could a changed product/user/case mix explain the aggregate trend?
  - Are hard strata being excluded or down-weighted after failures?
  - Does standardisation preserve the absolute engineering requirement?

### P024 — Use context-adapted multivariate, rare-event, short-run or change-point monitoring only when its added discrimination pays

- **PROPERTY_ID:** `P024`
- **PROPERTY_NAME:** Use context-adapted multivariate, rare-event, short-run or change-point monitoring only when its added discrimination pays
- **FAILURE_MODE:** Tool mismatch, multiplicity across dashboards, tail overconfidence and opaque anomaly scores.
- **MATURE_FORM:** Adopt only after showing incremental decision value over a cheap baseline, with interpretable follow-up and recalibration rules.
- **TRIGGER:** Multivariate correlated measurements, rare defects, variable exposure, small shifts, low volume or abrupt change points.
- **CHEAP_PATH:** Use a direct rule or simple stratified count when the event is obvious and data too sparse to estimate a complex model.
- **MEASUREMENT_PRECONDITIONS:** Input variables retain meaning and covariance/event models are adequate enough for threshold calibration.
- **ASSUMPTIONS:** Selected detector’s null/change model or robust calibration approximates use; multiplicity across monitored features is controlled.
- **DECISION_OR_CONSUMER:** Monitoring team and incident/process owner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Select a detector for multivariate, sparse, small-shift or low-volume change.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Context-specific joint/event/regime model, often with limited baseline data.
  - **MEASUREMENT_PRECONDITIONS:** Stable features, denominators, covariance/event definitions and protected calibration data.
  - **SIGNAL_OR_DISCRIMINATOR:** Detector score calibrated to target change and error costs.
  - **FALSE_POSITIVE_COST:** Opaque alert burden, multiple-testing inflation and overfit.
  - **FALSE_NEGATIVE_COST:** Joint/rare harmful shift missed by simple marginal rules.
  - **NONSTATIONARITY_RISK:** Model/calibration particularly fragile under shift.
  - **INTERVENTION_RISK:** Retraining after incidents can absorb failures.
  - **CHEAP_PATH:** Direct count/rule or expert review when data cannot support a complex detector.
  - **MATURE_FORM:** Incremental-value-tested specialised monitor with interpretable diagnosis.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Hotelling score without diagnosis; Poisson chart under overdispersion; zero-event reassurance; model retrained after every alarm. Contrary evidence/limit: Rare-event detector performance is often weakly estimable; simulation depends on an assumed tail/model and can create false certainty. Contrary evidence/limit: Rare-event detector performance is often weakly estimable; simulation depends on an assumed tail/model and can create false certainty.
- **ANTI_CEREMONY_BOUNDARY:** Having a multivariate/anomaly model is not a general property; validated added discrimination is.
- **POSSIBLE_CONFLICTING_PROPERTY:** P021 sensitivity competes with false-alarm cost; P030–P035 deliberate experimentation can intentionally disturb stability; P057 can retire low-value controls.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What specific change does the specialised detector find that a cheaper rule misses?
  - Are rare-event or covariance assumptions supported?
  - Can an alert be translated into an actionable investigation rather than an opaque score?

### P025 — Design sampling to represent the decision population and selection process

- **PROPERTY_ID:** `P025`
- **PROPERTY_NAME:** Design sampling to represent the decision population and selection process
- **FAILURE_MODE:** Selection bias, survivorship bias, spectrum restriction and false precision from nonprobability coverage.
- **MATURE_FORM:** Use the cheapest design that either represents the target or honestly limits the claim; retain all attempted-unit provenance.
- **TRIGGER:** Any inference beyond the exactly observed units, especially acceptance, prevalence, reliability or benchmark claims.
- **CHEAP_PATH:** For exhaustive authoritative enumeration of the entire relevant population, statistical sampling is unnecessary; verify completeness/identity instead.
- **MEASUREMENT_PRECONDITIONS:** Measurement meaning is invariant enough across sampled and target contexts; duplicates and clusters are identified.
- **ASSUMPTIONS:** Probability or selection-model assumptions hold sufficiently; unobserved selection is bounded or disclosed.
- **DECISION_OR_CONSUMER:** Experimenter, quality/reliability analyst, customer/regulator and benchmark consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate or compare performance for a defined target population.
  - **EXPERIMENTAL_UNIT:** Independently sampled unit or explicitly clustered unit from the frame.
  - **INDEPENDENCE_ASSUMPTION:** Sampling clusters/duplicates and repeated units must be modelled.
  - **RANDOMISATION_OR_CONTROL:** Random selection or transparent risk/stratified design; treatment randomisation is a separate issue.
  - **BLOCKING_OR_STRATIFICATION:** Stratify by expected heterogeneity, rarity or decision loss.
  - **REPLICATION_MEANING:** Replication means new sampled units, not repeated measurement of the same unit.
  - **INTERACTION_RISK:** Sample composition can interact with candidate/treatment performance.
  - **STOPPING_RULE:** Pre-specify frame, inclusion/exclusion and replacement rules.
  - **EXPECTED_INFORMATION_GAIN:** Provides population-relevant uncertainty and exposes coverage gaps.
  - **COST:** Frame construction, oversampling and follow-up.
  - **FAILURE_IF_OVER_APPLIED:** Overengineered probability sampling may waste effort for local deterministic decisions.
  - **MATURE_FORM:** Explicit target/frame with representative or claim-limited sampling.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** Probability sampling does not repair invalid measurement, and nonprobability samples can still support bounded local decisions if claims are restricted. Contrary evidence/limit: Open-ended deployment populations cannot be fully represented in advance; monitoring and scenario coverage remain necessary.
- **ANTI_CEREMONY_BOUNDARY:** A sample-size quota without a target/frame is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P013 selection/missingness can defeat nominal sample size; P042 exhaustive/deterministic evidence and P057 cost can make sampling unnecessary.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact population and opportunity frame does the sample represent?
  - Could selection, survival or duplication explain the result?
  - Would exhaustive deterministic checking be cheaper or more authoritative?

### P026 — Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it

- **PROPERTY_ID:** `P026`
- **PROPERTY_NAME:** Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it
- **FAILURE_MODE:** Arbitrary lot release, hidden risk transfer and pretending a sample proves every item conforms.
- **MATURE_FORM:** A domain-specific decision procedure with transparent OC/risk—not a universal quality property.
- **TRIGGER:** Incoming/outgoing lots with meaningful lot identity, relatively stable supply and costly/destructive inspection.
- **CHEAP_PATH:** Use 100% deterministic inspection when cheap/reliable; use process control/improvement when the goal is future quality rather than one-lot disposition.
- **MEASUREMENT_PRECONDITIONS:** Inspection error is small or included; sample selection cannot be manipulated.
- **ASSUMPTIONS:** Within-lot heterogeneity and production history are compatible with the plan; standard’s switching rules/context apply.
- **DECISION_OR_CONSUMER:** Purchaser/supplier, release authority and regulator.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Accept/reject a finite lot under inspection cost and error risk.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Finite lot with random sampled items and specified defect model/OC curve.
  - **MEASUREMENT_PRECONDITIONS:** Reliable item classification and auditable random sample.
  - **SIGNAL_OR_DISCRIMINATOR:** Acceptance number/plan with stated producer and consumer risks.
  - **FALSE_POSITIVE_COST:** Rejecting good lot, delay and destructive cost.
  - **FALSE_NEGATIVE_COST:** Accepting bad lot or catastrophic defective item.
  - **NONSTATIONARITY_RISK:** Lot heterogeneity/formation changes nominal risks.
  - **INTERVENTION_RISK:** Switching or relabelling lots after failure can game the plan.
  - **CHEAP_PATH:** 100% reliable automated inspection or direct supplier process evidence.
  - **MATURE_FORM:** Prespecified OC-based plan restricted to lot disposition.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** LOW
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: AQL interpreted as a guarantee; nonrandom sample; lot splitting; plan chosen after results; inspection error ignored. Contrary evidence/limit: Changing lot composition, adversarial suppliers and severe item heterogeneity can invalidate nominal OC risks. Contrary evidence/limit: Changing lot composition, adversarial suppliers and severe item heterogeneity can invalidate nominal OC risks.
- **ANTI_CEREMONY_BOUNDARY:** ISO table use or a named MIL-STD plan is an implementation; bounded risk-based lot disposition is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P013 selection/missingness can defeat nominal sample size; P042 exhaustive/deterministic evidence and P057 cost can make sampling unnecessary.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is the decision one-lot disposition, rather than process improvement or a universal quality claim?
  - Are sample selection, lot identity and inspection error controlled?
  - Would 100% authoritative inspection now be cheaper or safer?

### P027 — Do not use acceptance sampling as a substitute for process understanding, prevention or improvement

- **PROPERTY_ID:** `P027`
- **PROPERTY_NAME:** Do not use acceptance sampling as a substitute for process understanding, prevention or improvement
- **FAILURE_MODE:** Inspection dependence, hidden scrap/rework, no learning and claims that accepted samples establish process capability.
- **MATURE_FORM:** Use sampling for the decision it can make; do not infer control, capability or cause from acceptance alone.
- **TRIGGER:** Repeated supply/production where future quality matters, not merely one isolated transaction.
- **CHEAP_PATH:** For a one-off purchase with no leverage or future process, bounded acceptance sampling may be all that is rational.
- **MEASUREMENT_PRECONDITIONS:** Measurement system distinguishes defects and records failure modes rather than only pass/fail totals.
- **ASSUMPTIONS:** Lot outcomes contain some information about process, but causal diagnosis requires additional evidence.
- **DECISION_OR_CONSUMER:** Supplier/process owner, procurement and improvement team.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Discarding rejected-lot data; treating AQL as target; supplier adjusts lot formation; no root-cause evidence. Contrary evidence/limit: For highly regulated or destructive products, acceptance evidence may remain necessary even with excellent process control. Contrary evidence/limit: For highly regulated or destructive products, acceptance evidence may remain necessary even with excellent process control.
- **ANTI_CEREMONY_BOUNDARY:** Acceptance forms/tables are not process-improvement properties.
- **POSSIBLE_CONFLICTING_PROPERTY:** P013 selection/missingness can defeat nominal sample size; P042 exhaustive/deterministic evidence and P057 cost can make sampling unnecessary.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is lot acceptance being mistaken for evidence of process stability or cause?
  - Are rejected and sampled defects fed back into process learning?
  - Is future process improvement economically relevant to this decision?

### P028 — Size samples around effect/precision, dependence and decision loss—not a universal count

- **PROPERTY_ID:** `P028`
- **PROPERTY_NAME:** Size samples around effect/precision, dependence and decision loss—not a universal count
- **FAILURE_MODE:** Underpowered/equivocal experiments, inflated cost, post-hoc stopping and “large n” used to excuse bad design.
- **MATURE_FORM:** Plan for the independent information needed to discriminate the decision, update only under a valid sequential/adaptive protocol.
- **TRIGGER:** Sampling/experiment/reliability decisions where uncertainty influences action.
- **CHEAP_PATH:** No sample-size calculation is needed when a deterministic proof/check resolves the decision or when a pilot’s only goal is feasibility discovery.
- **MEASUREMENT_PRECONDITIONS:** Measurement error and missingness are included in effective information; pilot estimates are not treated as exact.
- **ASSUMPTIONS:** Planning model approximates design; effect threshold is engineering-justified; clusters/dependence known enough.
- **DECISION_OR_CONSUMER:** Experiment owner, risk owner and resource allocator.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Obtain enough independent information to choose among actions or bound risk.
  - **EXPERIMENTAL_UNIT:** Independent experimental/sample unit at the decision scale.
  - **INDEPENDENCE_ASSUMPTION:** Clusters, repeated measures and common seeds reduce effective n.
  - **RANDOMISATION_OR_CONTROL:** Assignment/sampling design determines variance and bias; randomisation where causal.
  - **BLOCKING_OR_STRATIFICATION:** Use stratification/blocking when it reduces nuisance variance without hiding heterogeneity.
  - **REPLICATION_MEANING:** New independent units; technical repeats mainly estimate measurement error.
  - **INTERACTION_RISK:** Interactions/heterogeneity increase required coverage and can invalidate one average effect.
  - **STOPPING_RULE:** Fixed horizon or formally planned sequential/adaptive rule.
  - **EXPECTED_INFORMATION_GAIN:** Decision discrimination or interval precision per unit cost.
  - **COST:** Units, measurement, delay and opportunity cost.
  - **FAILURE_IF_OVER_APPLIED:** Formulaic power can become a quota and reward trivial-effect detection.
  - **MATURE_FORM:** Simulation/sensitivity-based planning with explicit effect, dependence, loss and stopping.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Counting repeated readings as n; planning on observed pilot effect; stopping when significant; ignoring multiplicity/attrition. Contrary evidence/limit: Rare catastrophic outcomes may require physical/structural evidence, conservative bounds or stress models because feasible samples cannot directly validate target rates. Contrary evidence/limit: Rare catastrophic outcomes may require physical/structural evidence, conservative bounds or stress models because feasible samples cannot directly validate target rates.
- **ANTI_CEREMONY_BOUNDARY:** “30 samples,” “10 runs,” or “80% power” without a decision model is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P013 selection/missingness can defeat nominal sample size; P042 exhaustive/deterministic evidence and P057 cost can make sampling unnecessary.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What independent sample size—not raw observation count—supports the decision?
  - What smallest engineering-relevant effect or precision target was used?
  - Would a sequential or deterministic path reach the decision more cheaply?

### P029 — Frame experiments around an explicit engineering decision, estimand and rival alternatives

- **PROPERTY_ID:** `P029`
- **PROPERTY_NAME:** Frame experiments around an explicit engineering decision, estimand and rival alternatives
- **FAILURE_MODE:** Significance-test ritual, moving hypotheses, post-hoc target selection and experiments that generate numbers but no decision.
- **MATURE_FORM:** No experiment begins as “run a test”; it begins with the decision it can change and the cheapest evidence that discriminates it.
- **TRIGGER:** Any nontrivial comparison or intervention whose result may change design, release, allocation or policy.
- **CHEAP_PATH:** For an exact authoritative check or exploratory feasibility probe, a formal estimand/test may be unnecessary; label the evidence accordingly.
- **MEASUREMENT_PRECONDITIONS:** Outcome is valid and sensitive enough; unit/assignment/exposure can be identified.
- **ASSUMPTIONS:** The chosen estimand maps to the decision and potential outcomes/comparisons are meaningful.
- **DECISION_OR_CONSUMER:** Design authority, product/process owner and risk/resource decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Choose among stated engineering alternatives using a defined effect/estimand.
  - **EXPERIMENTAL_UNIT:** Unit receiving the intervention/design condition.
  - **INDEPENDENCE_ASSUMPTION:** The unit—not each output—is the independent replication basis unless a justified hierarchy is modelled.
  - **RANDOMISATION_OR_CONTROL:** Randomise or justify a controlled quasi-experimental assignment.
  - **BLOCKING_OR_STRATIFICATION:** Block nuisance variation relevant to precision/validity.
  - **REPLICATION_MEANING:** New independently assigned units across decision-relevant conditions.
  - **INTERACTION_RISK:** Specify interactions that could reverse the average decision.
  - **STOPPING_RULE:** Fixed or planned sequential rule tied to the estimand.
  - **EXPECTED_INFORMATION_GAIN:** Expected reduction in uncertainty between rival actions.
  - **COST:** Experiment units, delay, risk and opportunity.
  - **FAILURE_IF_OVER_APPLIED:** Over-formal framing can suppress exploratory learning.
  - **MATURE_FORM:** Staged exploratory/confirmatory design with explicit estimand, decision margin and scope.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** No universal formalism resolves normative loss or construct definition; exploratory and confirmatory phases may differ. Contrary evidence/limit: Some engineering discovery is necessarily open-ended; the mature boundary is transparent separation of exploration from decision-confirming evidence.
- **ANTI_CEREMONY_BOUNDARY:** A preregistration form or test name is optional; frozen decision/estimand boundaries are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact decision and rival alternatives will the experiment discriminate?
  - Is the estimand aligned with the unit/population that will receive the action?
  - Would a cheaper authoritative observation settle the question?

### P030 — Use randomisation to protect causal comparisons against assignment bias and support valid error assessment

- **PROPERTY_ID:** `P030`
- **PROPERTY_NAME:** Use randomisation to protect causal comparisons against assignment bias and support valid error assessment
- **FAILURE_MODE:** Selection bias, time/order confounding and invalid reference distributions.
- **MATURE_FORM:** Randomise when it materially reduces causal ambiguity; preserve assignment integrity and analyse the design actually run.
- **TRIGGER:** When interventions are feasible and the causal effect matters.
- **CHEAP_PATH:** Randomisation is unnecessary for deterministic mechanism verification and may be infeasible/unethical; strong natural/quasi-experimental or mechanistic evidence can be used with narrower claims.
- **MEASUREMENT_PRECONDITIONS:** Outcome ascertainment is blinded or otherwise protected from allocation bias where possible.
- **ASSUMPTIONS:** No unmodelled interference/carryover; randomisation is implemented, not merely planned; attrition does not undo comparability.
- **DECISION_OR_CONSUMER:** Experimenter, design/process owner and causal decision consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate the causal effect of an intervention/design alternative.
  - **EXPERIMENTAL_UNIT:** Unit assigned to treatment/control.
  - **INDEPENDENCE_ASSUMPTION:** Units are independent or clustering/interference is designed and analysed.
  - **RANDOMISATION_OR_CONTROL:** Known recorded random allocation; concealment/blinding where relevant.
  - **BLOCKING_OR_STRATIFICATION:** Restricted/stratified randomisation for major nuisance factors.
  - **REPLICATION_MEANING:** Independent assigned units; repeated outcomes are within-unit data.
  - **INTERACTION_RISK:** Treatment effects may vary by block/context; pre-specify important modifiers.
  - **STOPPING_RULE:** Fixed or design-valid sequential boundaries.
  - **EXPECTED_INFORMATION_GAIN:** Removes assignment confounding in expectation and supports randomisation inference.
  - **COST:** Exposure to alternatives, sample/time and operational disruption.
  - **FAILURE_IF_OVER_APPLIED:** Randomising trivial questions can waste resources or violate safety constraints.
  - **MATURE_FORM:** Correct-unit randomisation plus measurement, compliance, interference and transport safeguards.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** VERY_HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** Randomisation does not solve invalid measurement, low power, noncompliance, spillover, external validity or poor estimands. Contrary evidence/limit: Randomised effects may not transport beyond sampled units/context, and operational noncompliance can change the estimand.
- **ANTI_CEREMONY_BOUNDARY:** “A/B test” branding or a random seed alone is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Was allocation randomised at the actual intervention unit?
  - Could order, selection, attrition or exposure violate the assignment comparison?
  - What causal ambiguity remains despite randomisation?

### P031 — Block or stratify known nuisance variation without erasing interactions

- **PROPERTY_ID:** `P031`
- **PROPERTY_NAME:** Block or stratify known nuisance variation without erasing interactions
- **FAILURE_MODE:** Low precision, imbalance, order effects and effects confounded with known nuisance structure.
- **MATURE_FORM:** Block what is known and costly, randomise what remains, and report context interactions rather than only an adjusted average.
- **TRIGGER:** Heterogeneous units or expensive experiments where nuisance variation is large relative to target effect.
- **CHEAP_PATH:** Do not block on post-treatment variables or add complexity when units are already homogeneous and the effect is obvious.
- **MEASUREMENT_PRECONDITIONS:** Blocking variables are measured before intervention without candidate-induced bias.
- **ASSUMPTIONS:** Within-block comparisons remain meaningful; block definitions are not chosen after outcomes.
- **DECISION_OR_CONSUMER:** Experimenter and engineering decision owner.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate an effect with reduced nuisance variance and confounding.
  - **EXPERIMENTAL_UNIT:** Unit within a pre-treatment block/stratum.
  - **INDEPENDENCE_ASSUMPTION:** Independence across units/blocks or explicit cluster model.
  - **RANDOMISATION_OR_CONTROL:** Randomise within blocks or use justified matched assignment.
  - **BLOCKING_OR_STRATIFICATION:** Core mechanism: predefine blocks on consequential nuisance factors.
  - **REPLICATION_MEANING:** Independent units within/among blocks; technical repeats do not replace units.
  - **INTERACTION_RISK:** Treatment×block interactions may limit generalisation.
  - **STOPPING_RULE:** Predefine block construction and stopping.
  - **EXPECTED_INFORMATION_GAIN:** Higher precision per run and protection from known imbalance.
  - **COST:** Design complexity and need for enough units per block.
  - **FAILURE_IF_OVER_APPLIED:** Overblocking/empty cells and post-hoc stratification.
  - **MATURE_FORM:** Sparse, pre-treatment blocking plus interaction-aware analysis.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Blocking treatment with time unintentionally; post-hoc subgrouping; using seed as “replication” but not block; forgetting block interactions. Contrary evidence/limit: When nuisance variables are numerous/high-dimensional, model-based adjustment may overfit; design-stage balance remains finite. Contrary evidence/limit: When nuisance variables are numerous/high-dimensional, model-based adjustment may overfit; design-stage balance remains finite.
- **ANTI_CEREMONY_BOUNDARY:** A Latin square or mandatory stratification table is optional; nuisance-control efficiency is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Were known batch, time, operator, site or severity effects blocked/stratified?
  - Was any block defined after outcomes or affected by treatment?
  - Could the treatment effect reverse across blocks?

### P032 — Require independent replication at the experimental-unit level; treat technical repeats as measurement information

- **PROPERTY_ID:** `P032`
- **PROPERTY_NAME:** Require independent replication at the experimental-unit level; treat technical repeats as measurement information
- **FAILURE_MODE:** Underestimated uncertainty, false significance, fragile “6/6” claims and inability to distinguish unit effects from treatment effects.
- **MATURE_FORM:** Count independent decision-relevant units, disclose dependence, and stop treating correlated reruns as corroboration.
- **TRIGGER:** Any claim intended to generalise beyond one specimen, run, model instance, batch, site or environment.
- **CHEAP_PATH:** For deterministic proof or exact exhaustive checks, replication is unnecessary; for measurement precision, technical repeats remain useful but answer a different question.
- **MEASUREMENT_PRECONDITIONS:** Repeated measurement error is separated from between-unit variation; evaluator exposures do not couple units.
- **ASSUMPTIONS:** Units are exchangeable/representative enough for intended scope; clusters and interference are modelled.
- **DECISION_OR_CONSUMER:** Experimenter, reviewer and engineering decision authority.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Generalise a treatment/design effect beyond one realised unit.
  - **EXPERIMENTAL_UNIT:** Independent specimen/run/site/model instance/batch receiving a condition.
  - **INDEPENDENCE_ASSUMPTION:** Technical repeats and outputs nested within units are correlated.
  - **RANDOMISATION_OR_CONTROL:** Randomise conditions across independent units when causal.
  - **BLOCKING_OR_STRATIFICATION:** Block by known shared source while retaining multiple units per condition.
  - **REPLICATION_MEANING:** New units with independent exposure and natural variation.
  - **INTERACTION_RISK:** Treatment×unit/context interactions reveal transfer limits.
  - **STOPPING_RULE:** Set independent-unit target or valid sequential rule before outcome review.
  - **EXPECTED_INFORMATION_GAIN:** Estimates between-unit variability and robustness.
  - **COST:** Independent units may dominate total cost.
  - **FAILURE_IF_OVER_APPLIED:** Mechanical replication quotas or fake seed replication.
  - **MATURE_FORM:** Hierarchical design that labels technical, unit, batch and site replication separately.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** VERY_HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** Replication count is not enough: independence, representativeness and measurement validity remain prerequisites. Contrary evidence/limit: For singular large engineered systems, evidence may need component replication, simulation validation and mechanistic argument rather than classical independent system copies.
- **ANTI_CEREMONY_BOUNDARY:** A fixed “number of replications” is ceremony; independence at the right level is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What is the actual independently assigned or sampled unit?
  - Are multiple outputs, seeds or reviews from one underlying unit being counted as separate experiments?
  - Does shared data, evaluator or environment create common-mode dependence?

### P033 — Use factorial structure to discover interactions and avoid one-factor-at-a-time ambiguity

- **PROPERTY_ID:** `P033`
- **PROPERTY_NAME:** Use factorial structure to discover interactions and avoid one-factor-at-a-time ambiguity
- **FAILURE_MODE:** Confounded design choices, local conclusions and excessive runs for weak information.
- **MATURE_FORM:** Use factorial structure when interaction ambiguity is decision-relevant; confirm in the intended operating region.
- **TRIGGER:** Multiple controllable factors with plausible interactions and experiments costly enough that structured coverage matters.
- **CHEAP_PATH:** For one known dominant factor, deterministic mechanism or a tiny safe search space that can be exhaustively tested, formal factorial DOE may be excessive.
- **MEASUREMENT_PRECONDITIONS:** Outcome/evaluator remains comparable across combinations; invalid/impossible combinations identified before randomisation.
- **ASSUMPTIONS:** Model hierarchy/sparsity or sufficient full design; no uncontrolled time/batch confounding.
- **DECISION_OR_CONSUMER:** Design/process engineer and optimiser.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate main effects and interactions among controllable factors.
  - **EXPERIMENTAL_UNIT:** Independent run/unit at a specified factor combination.
  - **INDEPENDENCE_ASSUMPTION:** Runs independent or blocked; repeated readings nested.
  - **RANDOMISATION_OR_CONTROL:** Randomise run order subject to safety/logistics.
  - **BLOCKING_OR_STRATIFICATION:** Block batch/day/machine or use split-plot structure when factor changes differ in cost.
  - **REPLICATION_MEANING:** Independent runs across combinations; confirmatory runs at chosen settings.
  - **INTERACTION_RISK:** Core target; hierarchy/sparsity assumptions must be explicit.
  - **STOPPING_RULE:** Preplan analysis and reserve confirmation; sequential augmentation allowed by rule.
  - **EXPECTED_INFORMATION_GAIN:** High information per run about combinations and robustness.
  - **COST:** Number of combinations, setup changes and unsafe regions.
  - **FAILURE_IF_OVER_APPLIED:** Overbuilt factorials and spurious high-order interactions.
  - **MATURE_FORM:** Smallest design that identifies decision-relevant interactions plus confirmation.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** Factorial design is not synonymous with all experimentation; interactions outside tested levels/context remain unknown. Contrary evidence/limit: High-dimensional systems may violate effect sparsity/hierarchy and contain discontinuities; adaptive or mechanistic designs may outperform classical factorials.
- **ANTI_CEREMONY_BOUNDARY:** A full 2^k table is optional; efficient interaction-identifying contrast structure is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Could interactions reverse the conclusion drawn from isolated factor changes?
  - Is the design able to separate main effects from important interactions?
  - Would exhaustive/deterministic testing be cheaper than a formal DOE here?

### P034 — Use fractional factorial/screening designs only with explicit alias and sparsity assumptions

- **PROPERTY_ID:** `P034`
- **PROPERTY_NAME:** Use fractional factorial/screening designs only with explicit alias and sparsity assumptions
- **FAILURE_MODE:** Confident but aliased conclusions, discarded causal factors and optimisation on a contaminated screening model.
- **MATURE_FORM:** Treat screening results as provisional, report aliases, and resolve any ambiguity that could change the decision.
- **TRIGGER:** Early screening with many candidate factors, limited runs and a credible effect-sparsity/hierarchy hypothesis.
- **CHEAP_PATH:** Use full factorial, mechanistic screening or direct elimination when interactions are dense/critical or factors are few.
- **MEASUREMENT_PRECONDITIONS:** Measurement error small enough that sparse effects are not buried; factor settings are reproducible.
- **ASSUMPTIONS:** Few active effects, high-order interactions negligible or follow-up can resolve ambiguity.
- **DECISION_OR_CONSUMER:** Screening experiment owner and design team.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Screen many factors to select a smaller follow-up set.
  - **EXPERIMENTAL_UNIT:** Independent run/unit at a design row.
  - **INDEPENDENCE_ASSUMPTION:** Runs independent/blocked; no hidden batch alias.
  - **RANDOMISATION_OR_CONTROL:** Randomise rows subject to restrictions.
  - **BLOCKING_OR_STRATIFICATION:** Account for hard-to-change factors with split-plot/blocks.
  - **REPLICATION_MEANING:** Usually limited; follow-up/foldover supplies discrimination.
  - **INTERACTION_RISK:** Aliasing with interactions is the central risk.
  - **STOPPING_RULE:** Precommit alias interpretation and follow-up trigger.
  - **EXPECTED_INFORMATION_GAIN:** Broad factor information per run under sparsity.
  - **COST:** Follow-up burden and risk of missed factors.
  - **FAILURE_IF_OVER_APPLIED:** Treating provisional aliases as causal truths.
  - **MATURE_FORM:** Resolution-aware screening plus sequential de-aliasing and confirmation.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Resolution III main effects treated as clean; no foldover; factors dropped before interaction check; no confirmation. Contrary evidence/limit: When effect sparsity fails or factors are adaptive/continuous, screening rankings can be unstable and model-dependent. Contrary evidence/limit: When effect sparsity fails or factors are adaptive/continuous, screening rankings can be unstable and model-dependent.
- **ANTI_CEREMONY_BOUNDARY:** A Plackett–Burman array or “DOE software result” is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What effects are aliased, and which assumptions make the reported effect interpretable?
  - Was ambiguous screening evidence independently confirmed or augmented?
  - Could a plausible interaction contaminate the selected main effect?

### P035 — Use response surfaces and iterative experimentation as local learning, with confirmation and boundary discipline

- **PROPERTY_ID:** `P035`
- **PROPERTY_NAME:** Use response surfaces and iterative experimentation as local learning, with confirmation and boundary discipline
- **FAILURE_MODE:** Overfit optima, extrapolation, hill-climbing into unsafe regions and confirmation on reused data.
- **MATURE_FORM:** Iterate models as provisional maps; require confirmation in the intended context and robustness around the selected point.
- **TRIGGER:** Continuous controllable factors, expensive runs and an objective surface smooth enough locally.
- **CHEAP_PATH:** For discrete deterministic search spaces that are cheap to enumerate or when a mechanistic model fixes the optimum, RSM is unnecessary.
- **MEASUREMENT_PRECONDITIONS:** Outcome definition/threshold remains stable across stages; process drift is monitored.
- **ASSUMPTIONS:** Local low-order approximation is adequate within each step; sequential data reuse is reflected in uncertainty.
- **DECISION_OR_CONSUMER:** Design/process engineer and optimisation decision owner.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Locate/compare an operating region or optimum under continuous factors.
  - **EXPERIMENTAL_UNIT:** Independent run/unit at selected settings.
  - **INDEPENDENCE_ASSUMPTION:** Sequential runs may be dependent through adaptation; observation noise independent conditional on design or modelled.
  - **RANDOMISATION_OR_CONTROL:** Randomise/localise run order where drift permits; adaptive selection is recorded.
  - **BLOCKING_OR_STRATIFICATION:** Block nuisance factors and include centre/replicate points.
  - **REPLICATION_MEANING:** Independent runs and protected confirmation at final settings.
  - **INTERACTION_RISK:** Curvature and interactions are core; unknown high-order behaviour outside region.
  - **STOPPING_RULE:** Stage/decision rule plus independent confirmation, not “stop when best.”
  - **EXPECTED_INFORMATION_GAIN:** High local information gain and efficient movement toward useful region.
  - **COST:** Runs, setup changes, risk near boundaries and confirmation.
  - **FAILURE_IF_OVER_APPLIED:** Adaptive overfit, local optimum and ceremonial contour fitting.
  - **MATURE_FORM:** Constraint-aware sequential local modelling with model checks, robustness and fresh confirmation.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Reporting fitted optimum without confirmation; extrapolating beyond design; stopping after favourable stage; no noise-factor test. Contrary evidence/limit: Adaptive optimisers can exploit evaluator noise and drift; repeated use of the same validation surface erodes confirmation value. Contrary evidence/limit: Adaptive optimisers can exploit evaluator noise and drift; repeated use of the same validation surface erodes confirmation value.
- **ANTI_CEREMONY_BOUNDARY:** RSM contour plots or a fixed phase sequence are tools; sequential information-efficient learning is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Was the reported optimum independently confirmed in the intended operating region?
  - Did sequential adaptation preserve a stopping/validation boundary?
  - Could the optimiser be exploiting evaluator noise or an unsafe extrapolation?

### P036 — Report effect magnitude, uncertainty and engineering significance; use equivalence/noninferiority when “no important difference” is the decision

- **PROPERTY_ID:** `P036`
- **PROPERTY_NAME:** Report effect magnitude, uncertainty and engineering significance; use equivalence/noninferiority when “no important difference” is the decision
- **FAILURE_MODE:** Statistical/practical-significance confusion, false “no difference,” and optimisation of trivial changes.
- **MATURE_FORM:** Show effect, uncertainty, smallest consequential magnitude, and decision; reserve “equivalent” for designs that test a justified margin.
- **TRIGGER:** Comparisons where action depends on magnitude, not merely direction, and negative results may support interchangeability.
- **CHEAP_PATH:** For deterministic threshold compliance or an overwhelming effect far from uncertainty, a p-value may add nothing.
- **MEASUREMENT_PRECONDITIONS:** Metric resolution and uncertainty are small enough relative to the engineering margin.
- **ASSUMPTIONS:** Model/interval coverage is adequate; equivalence margin is fixed independently of observed results.
- **DECISION_OR_CONSUMER:** Design/process owner, customer, regulator and risk decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Decide whether an effect is large enough, or small enough, to matter.
  - **EXPERIMENTAL_UNIT:** Independent unit at the action scale.
  - **INDEPENDENCE_ASSUMPTION:** Design-appropriate independence/cluster structure.
  - **RANDOMISATION_OR_CONTROL:** Randomise/control if causal; otherwise limit claim.
  - **BLOCKING_OR_STRATIFICATION:** Block major nuisance factors and examine consequential strata.
  - **REPLICATION_MEANING:** Enough independent units for interval precision around the decision margin.
  - **INTERACTION_RISK:** Subgroup/tail interactions may defeat average equivalence.
  - **STOPPING_RULE:** Fixed or valid sequential rule using the same margin.
  - **EXPECTED_INFORMATION_GAIN:** Directly discriminates engineering-relevant alternatives.
  - **COST:** Sample and measurement cost.
  - **FAILURE_IF_OVER_APPLIED:** Overformal effect metrics or arbitrary margins can game decisions.
  - **MATURE_FORM:** Magnitude-plus-uncertainty decision, with equivalence/noninferiority only when prejustified.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: p<.05 presented without units; CI crossing zero called “same”; post-hoc equivalence margin; relative change hiding absolute harm. Contrary evidence/limit: Engineering-significance margins can be multi-dimensional and context-dependent; scalar margins may conceal trade-offs or rare harms. Contrary evidence/limit: Engineering-significance margins can be multi-dimensional and context-dependent; scalar margins may conceal trade-offs or rare harms.
- **ANTI_CEREMONY_BOUNDARY:** A particular effect-size statistic or ban on p-values is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What effect magnitude would actually change the engineering decision?
  - Is a negative result merely inconclusive, or was equivalence against a justified margin tested?
  - Could a statistically significant change be operationally trivial?

### P037 — Control multiplicity, analyst degrees of freedom and selective inference across the actual family of opportunities

- **PROPERTY_ID:** `P037`
- **PROPERTY_NAME:** Control multiplicity, analyst degrees of freedom and selective inference across the actual family of opportunities
- **FAILURE_MODE:** False discoveries, cherry-picking, hidden file drawers and post-hoc subgroup/evaluator selection.
- **MATURE_FORM:** Protect the claim-generating opportunity set, not merely the final table; use fresh confirmation when adaptivity is complex.
- **TRIGGER:** Many metrics, variants, subgroups, prompts, models, thresholds or parallel experiments.
- **CHEAP_PATH:** When one authoritative predeclared deterministic discriminator exists, multiplicity machinery is unnecessary; report any exploratory alternatives separately.
- **MEASUREMENT_PRECONDITIONS:** Evaluator/threshold versions and excluded outputs are retained; duplicates/dependence are known.
- **ASSUMPTIONS:** Chosen correction matches dependence and decision loss; unreported researcher flexibility is bounded.
- **DECISION_OR_CONSUMER:** Experiment owner, reviewer, portfolio decision maker and public evidence consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Select or confirm effects while controlling false claims across many opportunities.
  - **EXPERIMENTAL_UNIT:** Independent unit within each experiment; the claim family spans analyses/experiments.
  - **INDEPENDENCE_ASSUMPTION:** Dependence among tests affects error control; shared data is not independent replication.
  - **RANDOMISATION_OR_CONTROL:** Randomisation protects each causal contrast but not unreported multiplicity.
  - **BLOCKING_OR_STRATIFICATION:** Use hierarchical families/strata where decision structure justifies them.
  - **REPLICATION_MEANING:** Independent confirmatory units/data after exploration.
  - **INTERACTION_RISK:** Post-hoc interaction/subgroup searches are major multiplicity sources.
  - **STOPPING_RULE:** Predefine looks or use valid sequential/multiple-testing procedure.
  - **EXPECTED_INFORMATION_GAIN:** Protects credibility of selected winners.
  - **COST:** Power cost and need for fresh holdout/replication.
  - **FAILURE_IF_OVER_APPLIED:** Blanket corrections can be wasteful and obscure exploratory learning.
  - **MATURE_FORM:** Transparent family definition, suitable error criterion, and protected confirmation.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** VERY_HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Correcting only final p-values while selecting endpoints/models; post-hoc “primary” metric; repeated benchmark variants; favourable subgroup only. Contrary evidence/limit: The true adaptive analysis family may be impossible to enumerate; fresh independent replication/holdout protection may be more credible than retrospective correction. Contrary evidence/limit: The true adaptive analysis family may be impossible to enumerate; fresh independent replication/holdout protection may be more credible than retrospective correction.
- **ANTI_CEREMONY_BOUNDARY:** A preregistration badge, Bonferroni-by-default or “one metric” slogan is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - How many outcomes, subgroups, models, thresholds and looks could have produced the selected claim?
  - Were unfavourable measurements or analyses retained?
  - Is fresh independent confirmation needed because the adaptive family cannot be reconstructed?

### P038 — Plan sequential evidence and stopping so repeated looks do not manufacture confidence

- **PROPERTY_ID:** `P038`
- **PROPERTY_NAME:** Plan sequential evidence and stopping so repeated looks do not manufacture confidence
- **FAILURE_MODE:** Optional-stopping abuse, confirmation loops, repeated review inflation and needless evidence collection.
- **MATURE_FORM:** Another observation is justified only when it is expected to change the decision and the stopping/error framework remains valid.
- **TRIGGER:** Repeated monitoring/experiments where results are reviewed before collection ends or cost accumulates over time.
- **CHEAP_PATH:** Stop immediately when an authoritative deterministic discriminator settles the decision; no statistical stopping machinery is needed.
- **MEASUREMENT_PRECONDITIONS:** Measurement/evaluator is stable over the sequence; repeated observations add identifiable information.
- **ASSUMPTIONS:** Procedure’s martingale/likelihood/independence conditions hold or robust alternatives are used; adaptive outcome switching is excluded.
- **DECISION_OR_CONSUMER:** Experiment/monitoring owner and resource/risk decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Stop/continue an experiment while preserving evidential validity and minimising expected cost.
  - **EXPERIMENTAL_UNIT:** Sequentially observed independent/conditionally modelled units.
  - **INDEPENDENCE_ASSUMPTION:** Time dependence/adaptive assignment must meet the chosen procedure.
  - **RANDOMISATION_OR_CONTROL:** Randomisation continues under the protocol; adaptive allocation accounted for.
  - **BLOCKING_OR_STRATIFICATION:** Stratification can be maintained; information fractions may guide looks.
  - **REPLICATION_MEANING:** New units/information increments, not repeated reinterpretation of the same data.
  - **INTERACTION_RISK:** Adaptive subgroup/outcome switching is outside ordinary boundaries.
  - **STOPPING_RULE:** Fixed horizon or explicit sequential boundary/decision rule.
  - **EXPECTED_INFORMATION_GAIN:** Expected decision-value gain per next observation.
  - **COST:** Delay, samples, exposure and analysis burden.
  - **FAILURE_IF_OVER_APPLIED:** Using advanced sequential tools ceremonially where a simple fixed design suffices.
  - **MATURE_FORM:** Method matched to dependence and decision, with full look/stopping provenance.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** VERY_HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Restarting tests after failure; treating every review as independent; stopping at first green; continuing only negative arms; changing metric midstream. Contrary evidence/limit: No universal stopping rule exists across discovery, safety, optimisation and governance; information value and consequence determine the boundary. Contrary evidence/limit: No universal stopping rule exists across discovery, safety, optimisation and governance; information value and consequence determine the boundary.
- **ANTI_CEREMONY_BOUNDARY:** A universal number of rounds or a confidence-sequence library is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Was the stopping/continuation rule defined before outcomes were reviewed?
  - Does each additional test add independent or conditionally valid information?
  - Is collection continuing because the decision remains ambiguous or merely because a quota exists?

### P039 — Bound causal claims by external validity, interference, carryover and order effects

- **PROPERTY_ID:** `P039`
- **PROPERTY_NAME:** Bound causal claims by external validity, interference, carryover and order effects
- **FAILURE_MODE:** Overgeneralisation, contaminated controls, order confounding and deployment failure despite a significant trial.
- **MATURE_FORM:** State the local causal estimand and separately justify transport; design around interference/order when materially plausible.
- **TRIGGER:** Networked/shared-resource systems, sequential treatments, adaptive users, multi-site deployment or any generalisation claim.
- **CHEAP_PATH:** For an exact local deterministic mechanism with no scope extension, external-validity statistics may be unnecessary; state the local claim.
- **MEASUREMENT_PRECONDITIONS:** Outcome remains comparable; contamination/exposure is observable enough to model.
- **ASSUMPTIONS:** No hidden interference/carryover beyond the specified structure; sampled contexts cover intended use or extrapolation is bounded.
- **DECISION_OR_CONSUMER:** Deployment owner, system architect, regulator and experiment consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate a causal effect under deployment-relevant exposure and context.
  - **EXPERIMENTAL_UNIT:** Unit or cluster under a defined exposure mapping/period sequence.
  - **INDEPENDENCE_ASSUMPTION:** Interference/carryover explicitly absent or modelled.
  - **RANDOMISATION_OR_CONTROL:** Randomise clusters/sequences or use appropriate controls.
  - **BLOCKING_OR_STRATIFICATION:** Stratify sites/contexts and counterbalance order.
  - **REPLICATION_MEANING:** Independent clusters/period sequences and multisite confirmation.
  - **INTERACTION_RISK:** Treatment×context and spillover interactions are central.
  - **STOPPING_RULE:** Stopping rule respects clusters/periods and delayed outcomes.
  - **EXPECTED_INFORMATION_GAIN:** Distinguishes direct, spillover, carryover and transported effects.
  - **COST:** Clusters/sites, washout, longer follow-up.
  - **FAILURE_IF_OVER_APPLIED:** Overly broad designs may be infeasible; local claims may suffice.
  - **MATURE_FORM:** Scope-bounded causal estimate plus interference/carryover and transport evidence.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** Randomisation is preserved but narrowed: it supports the assigned comparison, not automatic transport. Contrary evidence/limit: General transport under unmeasured effect modification is not identified from one experiment; mechanistic and multi-context evidence remain necessary.
- **ANTI_CEREMONY_BOUNDARY:** A “randomised” label is not the property if exposure or deployment scope differs.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can units influence one another or retain effects across periods?
  - Does the experimental population/context match deployment?
  - What evidence supports transporting the local effect beyond the tested conditions?

### P040 — Use robustness and sensitivity analysis to expose dependence on model, confounding and nuisance assumptions

- **PROPERTY_ID:** `P040`
- **PROPERTY_NAME:** Use robustness and sensitivity analysis to expose dependence on model, confounding and nuisance assumptions
- **FAILURE_MODE:** Model-driven false certainty, hidden leverage/outliers, unmeasured confounding and specification-search overfit.
- **MATURE_FORM:** Challenge the assumptions capable of changing the decision; do not confuse robust-to-one-model feature with universal validity.
- **TRIGGER:** Small samples, heavy tails, observational comparisons, extrapolation, complex models or high-consequence decisions.
- **CHEAP_PATH:** When a deterministic mechanism/proof settles the decision, statistical sensitivity may be redundant; verify mechanism assumptions instead.
- **MEASUREMENT_PRECONDITIONS:** Measurement error and evaluator variants are included among perturbations where material.
- **ASSUMPTIONS:** Perturbation set spans credible alternatives rather than only convenient ones; robust method’s loss/neighbourhood matches consequence.
- **DECISION_OR_CONSUMER:** Analyst, reviewer, risk owner and design authority.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Determine whether an experimental conclusion is stable to plausible violations/heterogeneity.
  - **EXPERIMENTAL_UNIT:** Same independent units, reanalysed or augmented under alternative assumptions.
  - **INDEPENDENCE_ASSUMPTION:** Dependence alternatives explicitly considered.
  - **RANDOMISATION_OR_CONTROL:** Randomisation protects assignment but sensitivity addresses noncompliance/missingness/model choices.
  - **BLOCKING_OR_STRATIFICATION:** Assess block/context heterogeneity and alternative stratifications.
  - **REPLICATION_MEANING:** Fresh confirmation may be required when sensitivity reveals overfit.
  - **INTERACTION_RISK:** Unmodelled interactions are a key robustness target.
  - **STOPPING_RULE:** Sensitivity plan ideally prespecified; exploratory analyses fully reported.
  - **EXPECTED_INFORMATION_GAIN:** Identifies which assumption/new experiment has highest value.
  - **COST:** Analysis and possible follow-up runs.
  - **FAILURE_IF_OVER_APPLIED:** Sensitivity theatre via many irrelevant models.
  - **MATURE_FORM:** Decision-focused perturbation/bounds with independent follow-up for fragile drivers.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Only normality test; deleting “outliers” post hoc; robust estimator treated as assumption-free; sensitivity range chosen to preserve result. Contrary evidence/limit: Sensitivity conclusions are only as broad as the considered perturbations; unknown unknowns and structural model error remain. Contrary evidence/limit: Sensitivity conclusions are only as broad as the considered perturbations; unknown unknowns and structural model error remain.
- **ANTI_CEREMONY_BOUNDARY:** A mandatory normality test or a menu of every model is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which model or nuisance assumption could reverse the decision?
  - Was the perturbation range justified independently of the desired result?
  - Does a robust conclusion survive evaluator, sampling and preprocessing alternatives—not only distribution choice?

### P041 — Choose experiments and measurements by expected information or decision value relative to cost

- **PROPERTY_ID:** `P041`
- **PROPERTY_NAME:** Choose experiments and measurements by expected information or decision value relative to cost
- **FAILURE_MODE:** Evidence theatre, analysis paralysis, overmeasurement and underinvestment in decisive discriminators.
- **MATURE_FORM:** Ask whether the next observation is independently informative enough to change action; choose the cheapest valid discriminator.
- **TRIGGER:** Costly/slow/destructive measurement, adaptive experimentation, competing tests or staged engineering decisions.
- **CHEAP_PATH:** Take the direct authoritative fact immediately when cost is negligible; do not build a probabilistic model merely to justify an obvious check.
- **MEASUREMENT_PRECONDITIONS:** Measurement can actually discriminate the uncertain states and does not repeat shared bias.
- **ASSUMPTIONS:** Utility/probability model or qualitative ranking is sufficiently credible; option value and irreversible harm are considered.
- **DECISION_OR_CONSUMER:** Resource allocator, design/test owner and risk decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Select the next experiment or decide to stop based on decision value.
  - **EXPERIMENTAL_UNIT:** Depends on candidate experiment; independent information unit must be explicit.
  - **INDEPENDENCE_ASSUMPTION:** Expected information must discount correlation/shared bias.
  - **RANDOMISATION_OR_CONTROL:** Prefer designs that discriminate alternatives; randomise when causal.
  - **BLOCKING_OR_STRATIFICATION:** Block/stratify if it cheaply improves information.
  - **REPLICATION_MEANING:** Value comes from new independent information, not repeated looks.
  - **INTERACTION_RISK:** Experiments should target uncertain interactions capable of changing action.
  - **STOPPING_RULE:** Stop when expected net decision value is nonpositive or boundary reached.
  - **EXPECTED_INFORMATION_GAIN:** Core criterion: expected reduction in decision loss/uncertainty.
  - **COST:** Measurement, delay, risk, setup and opportunity.
  - **FAILURE_IF_OVER_APPLIED:** False numerical precision or bureaucracy around EVSI.
  - **MATURE_FORM:** Qualitative/quantitative value-of-information gate with safety/robust constraints.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** MODERATE
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: “More data” default; full factorial despite deterministic discriminator; no action change after result; cost omitted; catastrophic risk monetised casually. Contrary evidence/limit: Deep uncertainty and irreversible tail harms can defeat expected-value summaries; robust/safety constraints may override average information value. Contrary evidence/limit: Deep uncertainty and irreversible tail harms can defeat expected-value summaries; robust/safety constraints may override average information value.
- **ANTI_CEREMONY_BOUNDARY:** A formal Bayesian model is optional; evidence proportionality is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which possible result of the next measurement would change the next decision?
  - Is the evidence independent enough to reduce the dominant uncertainty?
  - Does a cheaper test, sample or deterministic check dominate the proposed study?

### P042 — Give precedence to an authoritative deterministic discriminator when it settles the decision

- **PROPERTY_ID:** `P042`
- **PROPERTY_NAME:** Give precedence to an authoritative deterministic discriminator when it settles the decision
- **FAILURE_MODE:** Decorative statistics, false uncertainty, repeated green tests replacing source authority, and averaging over a deterministic defect.
- **MATURE_FORM:** First ask whether the decision is already logically or physically discriminated; if yes, stop statistical collection and document the decisive evidence.
- **TRIGGER:** Exact configuration/identity, complete enumeration, formal proof, direct physical interlock or unambiguous requirement violation.
- **CHEAP_PATH:** Do not invoke this property when the “deterministic” rule is an unvalidated proxy, incomplete oracle, stale reference or only one sample from a stochastic population.
- **MEASUREMENT_PRECONDITIONS:** The discriminator’s input and output are verifiable and its resolution covers the decision.
- **ASSUMPTIONS:** The rule truly entails the decision under current conditions; completeness/authority have been established.
- **DECISION_OR_CONSUMER:** Engineering decision owner and evidence reviewer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Determine whether experimentation is needed at all.
  - **EXPERIMENTAL_UNIT:** Not applicable when the direct discriminator is complete; otherwise define residual unit.
  - **INDEPENDENCE_ASSUMPTION:** No replication requirement for a logically decisive exact fact.
  - **RANDOMISATION_OR_CONTROL:** Not applicable unless residual causal uncertainty remains.
  - **BLOCKING_OR_STRATIFICATION:** Not applicable unless context scope is uncertain.
  - **REPLICATION_MEANING:** Replication addresses implementation/transfer reliability, not the already settled exact fact.
  - **INTERACTION_RISK:** Potential context exceptions must be tested if they limit entailment.
  - **STOPPING_RULE:** Stop immediately once authoritative discrimination is verified.
  - **EXPECTED_INFORMATION_GAIN:** Maximum information at minimum cost when valid.
  - **COST:** Verification of authority/identity and maintenance.
  - **FAILURE_IF_OVER_APPLIED:** Misclassifying a probabilistic proxy as deterministic.
  - **MATURE_FORM:** Deterministic precedence with explicit residual-uncertainty check.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** LOW
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** MODERATE
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Running significance tests on exhaustive results; rerunning a deterministic failure until green; using source count over authoritative identity; stale oracle. Contrary evidence/limit: Whether a discriminator is complete and authoritative is itself an evidence question; probabilistic residual risk may remain. Contrary evidence/limit: Whether a discriminator is complete and authoritative is itself an evidence question; probabilistic residual risk may remain.
- **ANTI_CEREMONY_BOUNDARY:** The absence of statistical analysis is not a defect when uncertainty is not the decision problem.
- **POSSIBLE_CONFLICTING_PROPERTY:** P037 multiplicity and P038 sequential learning constrain one another; P039 transport can limit local validity; P042/P057 can make formal experimentation disproportionate.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is there an authoritative deterministic check that already settles the decision?
  - Has the check’s identity, completeness and applicability been verified?
  - What residual uncertainty, if any, actually requires statistical evidence?

### P043 — Design robustness to nuisance factors and context variation, not only nominal mean performance

- **PROPERTY_ID:** `P043`
- **PROPERTY_NAME:** Design robustness to nuisance factors and context variation, not only nominal mean performance
- **FAILURE_MODE:** Local optimisation, high variance, field failure and “best average” designs with poor context tolerance.
- **MATURE_FORM:** Test and optimise decision-relevant performance across plausible nuisance contexts, with transparent loss and confirmation.
- **TRIGGER:** Products/processes deployed across variable environments or with costly field failures.
- **CHEAP_PATH:** For a fixed, tightly controlled environment or a deterministic design margin proven against all relevant variation, elaborate robust DOE may be unnecessary.
- **MEASUREMENT_PRECONDITIONS:** Measurement remains valid across noise conditions and can resolve dispersion/tail changes.
- **ASSUMPTIONS:** Tested noise factors represent deployment; interactions/model form are adequate; accelerated stresses do not introduce irrelevant mechanisms.
- **DECISION_OR_CONSUMER:** Designer, reliability/quality engineer and deployment owner.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Select settings/designs that remain acceptable across nuisance contexts.
  - **EXPERIMENTAL_UNIT:** Independent run/unit at control×noise condition.
  - **INDEPENDENCE_ASSUMPTION:** Runs independent/blocked; repeated observations nested.
  - **RANDOMISATION_OR_CONTROL:** Randomise feasible order; deliberate noise-factor assignment.
  - **BLOCKING_OR_STRATIFICATION:** Block hard-to-change factors or use split-plot designs.
  - **REPLICATION_MEANING:** Independent confirmation across representative noise contexts.
  - **INTERACTION_RISK:** Control×noise interactions are central.
  - **STOPPING_RULE:** Predefine robustness loss/criteria and confirmation.
  - **EXPECTED_INFORMATION_GAIN:** Information on sensitivity and variance reduction per run.
  - **COST:** Expanded design/stress cost.
  - **FAILURE_IF_OVER_APPLIED:** Ceremonial S/N optimisation or unrealistic stress matrix.
  - **MATURE_FORM:** Direct mean/variance/tail modelling over plausible noise contexts plus confirmation.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Using Taguchi S/N ratio automatically; unrealistic noise ranges; no confirmation; averaging away context-specific failures. Contrary evidence/limit: No finite noise-factor set guarantees open-world robustness; field monitoring and conservative design margins remain necessary. Contrary evidence/limit: No finite noise-factor set guarantees open-world robustness; field monitoring and conservative design margins remain necessary.
- **ANTI_CEREMONY_BOUNDARY:** Taguchi orthogonal arrays, S/N ratios and loss slogans are optional/historically contingent; robustness is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Were nuisance/noise factors representative of deployment and crossed with controllable factors?
  - Is robustness claimed from average performance or from dispersion/tail/context evidence?
  - Would a direct engineering margin prove robustness more cheaply?

### P044 — Model reliability over time with explicit failure definitions, exposure, censoring and degradation

- **PROPERTY_ID:** `P044`
- **PROPERTY_NAME:** Model reliability over time with explicit failure definitions, exposure, censoring and degradation
- **FAILURE_MODE:** Confusing current performance with lifetime reliability, dropping early failures, and ignoring degradation paths.
- **MATURE_FORM:** Make reliability conditional on mission, time/exposure, failure definition and context; report bounds and model sensitivity.
- **TRIGGER:** Components/systems where ageing, wear, cumulative use or time-dependent failure changes the decision.
- **CHEAP_PATH:** For a purely timeless deterministic property or rapidly replaceable low-consequence component, full life modelling may not pay.
- **MEASUREMENT_PRECONDITIONS:** Failure detection threshold is stable and degradation measure is linked to actual failure.
- **ASSUMPTIONS:** Independent/appropriately clustered lifetimes, censoring mechanism acceptable, distribution/regression model adequate over prediction horizon.
- **DECISION_OR_CONSUMER:** Reliability engineer, maintainer, design authority and risk owner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Predict/monitor failure risk over time and decide maintenance/release.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Time-to-event or degradation process with censoring, covariates and possible competing modes.
  - **MEASUREMENT_PRECONDITIONS:** Stable failure detection, exposure records and representative duty cycles.
  - **SIGNAL_OR_DISCRIMINATOR:** Hazard/survival/degradation estimate with uncertainty and mode diagnostics.
  - **FALSE_POSITIVE_COST:** Premature maintenance/rejection.
  - **FALSE_NEGATIVE_COST:** Unexpected field failure or underestimated wear-out.
  - **NONSTATIONARITY_RISK:** Configuration/context drift can make historical lifetimes obsolete.
  - **INTERVENTION_RISK:** Changing failure threshold or dropping early failures improves apparent reliability.
  - **CHEAP_PATH:** Deterministic wear limit or conservative life bound when available.
  - **MATURE_FORM:** Mission-specific censored/degradation model with sensitivity and ongoing field update.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Removing early failures; right-censored units treated as nonfailures forever; mixed modes pooled; uptime denominator changed; threshold drift. Contrary evidence/limit: Complex software/agent failure opportunities may not map cleanly to lifetime distributions; reliability methods transfer only where exposure/failure processes are coherent. Contrary evidence/limit: Complex software/agent failure opportunities may not map cleanly to lifetime distributions; reliability methods transfer only where exposure/failure processes are coherent.
- **ANTI_CEREMONY_BOUNDARY:** A Weibull plot or MTBF number is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is the reliability claim tied to a mission, time/exposure and stable failure definition?
  - Were censored, early and competing-mode observations retained?
  - Does the model represent deployment duty cycles and configuration changes?

### P045 — Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty

- **PROPERTY_ID:** `P045`
- **PROPERTY_NAME:** Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty
- **FAILURE_MODE:** Overstated lifetime, irrelevant stress failures, parameter uncertainty hidden by large acceleration factors.
- **MATURE_FORM:** Acceleration is an assumption-heavy bridge whose physical continuity must be evidenced, not a shortcut to certainty.
- **TRIGGER:** Long-lived products where timely direct life testing is infeasible and a credible acceleration mechanism exists.
- **CHEAP_PATH:** Do not accelerate when stress changes the mechanism or when conservative deterministic margin/field data already decide the question.
- **MEASUREMENT_PRECONDITIONS:** Stress/temperature/load measurement is calibrated; failure detection remains comparable across levels.
- **ASSUMPTIONS:** Same relevant failure mechanisms and adequate acceleration/life distributions across tested-to-use range.
- **DECISION_OR_CONSUMER:** Reliability/design owner and release/risk authority.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Estimate use-condition life from elevated-stress tests.
  - **EXPERIMENTAL_UNIT:** Independent specimen/system at a stress level.
  - **INDEPENDENCE_ASSUMPTION:** Lifetimes independent/clustered; censoring and common batch effects modelled.
  - **RANDOMISATION_OR_CONTROL:** Randomise specimens/run order where feasible; stress deliberately assigned.
  - **BLOCKING_OR_STRATIFICATION:** Block batch/manufacturing lot and include use-level anchors.
  - **REPLICATION_MEANING:** Independent specimens across multiple stress levels and confirmation.
  - **INTERACTION_RISK:** Stress×failure-mode/material interactions can invalidate extrapolation.
  - **STOPPING_RULE:** Predefine censoring/test termination and model-selection/validation rule.
  - **EXPECTED_INFORMATION_GAIN:** Large time acceleration if model is valid.
  - **COST:** Specimens, chambers, destructive failures and model risk.
  - **FAILURE_IF_OVER_APPLIED:** Routine ALT without physics or anchors creates false certainty.
  - **MATURE_FORM:** Physics-informed multi-level ALT with failure-mode checks, sensitivity and conservative prediction.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** LOW
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: One stress level; no use anchor; pooled failure modes; extrapolation without interval; treating high-stress pass as field proof. Contrary evidence/limit: Extreme acceleration and sparse failures make model uncertainty dominant; there may be no defensible high-reliability extrapolation. Contrary evidence/limit: Extreme acceleration and sparse failures make model uncertainty dominant; there may be no defensible high-reliability extrapolation.
- **ANTI_CEREMONY_BOUNDARY:** A standard Arrhenius/Weibull fit is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What physical evidence shows the accelerated and use conditions share failure mechanisms?
  - How far beyond observed stress/time is the reliability claim extrapolated?
  - Would a conservative design bound or degradation measure be more credible?

### P046 — Treat reliability growth as intervention-conditioned evidence, not an automatically improving trend

- **PROPERTY_ID:** `P046`
- **PROPERTY_NAME:** Treat reliability growth as intervention-conditioned evidence, not an automatically improving trend
- **FAILURE_MODE:** Trend worship, double-counting fixes, uncontrolled configuration changes and claiming causality from calendar order.
- **MATURE_FORM:** Attribute change to documented fixes only when comparable exposure and fresh validation support it; otherwise call it an observed trend.
- **TRIGGER:** Development programmes with repeated failures and deliberate corrective modifications.
- **CHEAP_PATH:** When no modifications occur, use ordinary reliability estimation; when one deterministic defect/fix is proven, validate that mechanism directly.
- **MEASUREMENT_PRECONDITIONS:** Measurement/evaluator thresholds are stable across versions or bridged.
- **ASSUMPTIONS:** Model form approximates the repair/improvement process; changes other than intended fixes are documented.
- **DECISION_OR_CONSUMER:** Reliability programme manager, design authority and acquisition/release decision maker.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide whether reliability is improving after interventions and whether readiness targets are credible.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Failure process over exposure with discrete design/process interventions and configuration changes.
  - **MEASUREMENT_PRECONDITIONS:** Stable failure definitions, exposure accounting and versioned configurations.
  - **SIGNAL_OR_DISCRIMINATOR:** Mode-specific post-fix reduction confirmed under comparable/fresh tests.
  - **FALSE_POSITIVE_COST:** Credit to ineffective fixes and premature release.
  - **FALSE_NEGATIVE_COST:** Failure to recognise genuine learning or recurring modes.
  - **NONSTATIONARITY_RISK:** Test environment and configuration changes are major nonstationarity.
  - **INTERVENTION_RISK:** Relabelling or easier testing can manufacture growth.
  - **CHEAP_PATH:** Direct proof/validation of a specific deterministic fix.
  - **MATURE_FORM:** Intervention-conditioned trend plus fresh validation and configuration control.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** LOW
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Test difficulty decreases; failures reclassified; exposure resets; fixes not independently verified; one programme curve pooled across modes. Contrary evidence/limit: Growth models are particularly vulnerable when few failures, many simultaneous changes or rapidly changing test environments exist. Contrary evidence/limit: Growth models are particularly vulnerable when few failures, many simultaneous changes or rapidly changing test environments exist.
- **ANTI_CEREMONY_BOUNDARY:** A Crow–AMSAA plot or target slope is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Are reliability improvements tied to documented fixes and comparable exposure?
  - Did failure definitions, thresholds, test difficulty or configuration change?
  - Was the claimed fix validated on fresh representative units?

### P047 — Translate zero observed failures into an upper risk bound, never “perfect reliability”

- **PROPERTY_ID:** `P047`
- **PROPERTY_NAME:** Translate zero observed failures into an upper risk bound, never “perfect reliability”
- **FAILURE_MODE:** Infinite-reliability claims, misleading “100% pass,” and underpowered high-reliability demonstrations.
- **MATURE_FORM:** Report the strongest upper bound supported by independent representative exposure and state what remains unobserved.
- **TRIGGER:** Reliability/safety claims based on zero failures or no detected rare defects.
- **CHEAP_PATH:** When a formal proof/physical impossibility establishes zero risk within scope, statistical zero-event bounds are secondary; verify proof scope.
- **MEASUREMENT_PRECONDITIONS:** Failures would be detected with sufficient sensitivity; no excluded/censored near-failures.
- **ASSUMPTIONS:** Bernoulli/Poisson/exposure model and homogeneity or conservative stratification are adequate.
- **DECISION_OR_CONSUMER:** Safety/reliability/release authority and customer/regulator.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Demonstrate that failure probability/rate is below an engineering bound.
  - **EXPERIMENTAL_UNIT:** Independent unit/opportunity or exposure interval.
  - **INDEPENDENCE_ASSUMPTION:** Independence/common-mode assumptions explicitly tested or conservatively adjusted.
  - **RANDOMISATION_OR_CONTROL:** Random sampling of units/conditions where possible.
  - **BLOCKING_OR_STRATIFICATION:** Stratify high-risk contexts and common-mode clusters.
  - **REPLICATION_MEANING:** Independent opportunities; repeats on one unit may not count equally.
  - **INTERACTION_RISK:** Context interactions can concentrate rare failures.
  - **STOPPING_RULE:** Fixed exposure/sample or valid sequential reliability-demonstration plan.
  - **EXPECTED_INFORMATION_GAIN:** Tightens upper risk bound.
  - **COST:** Large sample/exposure burden, especially for rare targets.
  - **FAILURE_IF_OVER_APPLIED:** Massive low-risk testing can crowd out mechanism/stress evidence.
  - **MATURE_FORM:** Bound-based demonstration integrated with mechanistic and stress evidence.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Counting repeated same-condition trials as independent; optional stopping after a clean run; changing failure definition; hiding near misses. Contrary evidence/limit: Extremely low target rates are rarely demonstrable by direct testing alone; model/mechanism/operational evidence must be combined without pretending equivalence. Contrary evidence/limit: Extremely low target rates are rarely demonstrable by direct testing alone; model/mechanism/operational evidence must be combined without pretending equivalence.
- **ANTI_CEREMONY_BOUNDARY:** “0 defects” and a green dashboard are not properties.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What upper failure-rate bound—not pass percentage—follows from the independent exposure?
  - Are trials representative and sufficiently sensitive to detect failure?
  - Could correlation, optional stopping or changed definitions make zero failures uninformative?

### P048 — Treat rare-event and tail claims as distinct, data-hungry and model-sensitive

- **PROPERTY_ID:** `P048`
- **PROPERTY_NAME:** Treat rare-event and tail claims as distinct, data-hungry and model-sensitive
- **FAILURE_MODE:** Rare-event overconfidence, normal extrapolation, benchmark averages hiding catastrophic cases and absence-of-event fallacy.
- **MATURE_FORM:** Separate central performance from tail claims; calibrate claim strength to observed/validated tail information and consequence.
- **TRIGGER:** High-consequence low-frequency failures, tight population-content guarantees or asymmetric loss.
- **CHEAP_PATH:** For bounded deterministic systems with proven hard limits, direct worst-case analysis can dominate statistical tail estimation.
- **MEASUREMENT_PRECONDITIONS:** Resolution captures near-tail behaviour and censoring/thresholds are stable.
- **ASSUMPTIONS:** Tail family/extrapolation and dependence are adequate; stress sampling is correctly reweighted; unobserved modes acknowledged.
- **DECISION_OR_CONSUMER:** Safety/reliability/design authority and risk owner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Detect/limit rare catastrophic events or high quantiles.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Heavy-tail/extreme/event process with possible dependence and heterogeneous exposure.
  - **MEASUREMENT_PRECONDITIONS:** Sensitive event capture, exposure denominator and preserved extremes/near misses.
  - **SIGNAL_OR_DISCRIMINATOR:** Conservative exceedance/tolerance bound or stress-validated mechanism.
  - **FALSE_POSITIVE_COST:** False alarms/overdesign from unstable tails.
  - **FALSE_NEGATIVE_COST:** Catastrophic missed mode or grossly understated rate.
  - **NONSTATIONARITY_RISK:** Tail law and exposure can shift strongly.
  - **INTERVENTION_RISK:** Dropping “outliers” or changing event definitions erases risk.
  - **CHEAP_PATH:** Deterministic worst-case bound/interlock if authoritative.
  - **MATURE_FORM:** Multi-source conservative tail case with explicit evidence limit.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** MODERATE
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** VERY_HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Normal six-sigma extrapolation; dropping outliers; zero events called zero risk; tail metric tuned after incident; pooled modes. Contrary evidence/limit: Unknown failure modes and dependence can dominate beyond-sample tails; precise numerical estimates may be less honest than conservative bounds/scenarios. Contrary evidence/limit: Unknown failure modes and dependence can dominate beyond-sample tails; precise numerical estimates may be less honest than conservative bounds/scenarios.
- **ANTI_CEREMONY_BOUNDARY:** A “six sigma” label or one worst-case anecdote is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is a mean or central interval being used to imply tail safety?
  - How much direct or validated stress/mechanism evidence exists for the claimed tail?
  - Were outliers, near misses and censored failures preserved?

### P049 — Test distribution shift and stress contexts; do not equate held-out performance with deployment validity

- **PROPERTY_ID:** `P049`
- **PROPERTY_NAME:** Test distribution shift and stress contexts; do not equate held-out performance with deployment validity
- **FAILURE_MODE:** Benchmark saturation, test-set overfitting, stale controls and false generalisation from one distribution.
- **MATURE_FORM:** A held-out score is local evidence; deployment claims require context coverage, shift sensitivity and evaluator integrity.
- **TRIGGER:** Adaptive software/ML/agent systems, long-lived processes, changing customers/suppliers, or field environments beyond lab conditions.
- **CHEAP_PATH:** For a closed deterministic domain fully enumerated by an authoritative test, distribution-shift analysis may be unnecessary; verify closure.
- **MEASUREMENT_PRECONDITIONS:** Labels/references remain valid under shift or are independently adjudicated.
- **ASSUMPTIONS:** Stress scenarios are plausible and not merely convenient; deployment monitoring can detect uncovered shifts.
- **DECISION_OR_CONSUMER:** Deployment owner, reliability/quality engineer and benchmark/evaluator owner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Detect performance/calibration degradation under changing deployment distributions.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Context-indexed data distribution with possible covariate, prior, concept and adversarial shifts.
  - **MEASUREMENT_PRECONDITIONS:** Fresh/protected samples, stable labels/evaluator and context metadata.
  - **SIGNAL_OR_DISCRIMINATOR:** Shift-sensitive calibration/performance deviation tied to action.
  - **FALSE_POSITIVE_COST:** Chasing unrealistic stress cases or alarm fatigue.
  - **FALSE_NEGATIVE_COST:** Deployment failure outside the original holdout.
  - **NONSTATIONARITY_RISK:** Defining risk; historical guarantees are local.
  - **INTERVENTION_RISK:** Refreshing/tuning on failures can absorb evidence.
  - **CHEAP_PATH:** Closed-domain exhaustive check or targeted mechanism test.
  - **MATURE_FORM:** Protected fresh evaluation plus scenario stress and field drift monitoring.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Repeated public benchmark tuning; no fresh collection; adversarial examples counted as prevalence; aggregate shift hides subgroup collapse. Contrary evidence/limit: Open-world shifts are unbounded; no finite suite proves universal robustness, and fresh sets may still share collection artefacts. Contrary evidence/limit: Open-world shifts are unbounded; no finite suite proves universal robustness, and fresh sets may still share collection artefacts.
- **ANTI_CEREMONY_BOUNDARY:** A benchmark leaderboard or one stress suite is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does held-out evidence cover deployment populations, contexts and incentives?
  - Could benchmark/test-set reuse or contamination explain the score?
  - What shift would invalidate the current threshold or evaluator calibration?

### P050 — Keep mean performance, variability, tail behaviour, reliability over time and model robustness as separate claims

- **PROPERTY_ID:** `P050`
- **PROPERTY_NAME:** Keep mean performance, variability, tail behaviour, reliability over time and model robustness as separate claims
- **FAILURE_MODE:** False “overall improvement,” weighted-metric gaming and releases that optimise average at the expense of catastrophic modes.
- **MATURE_FORM:** Make one claim per dimension and combine them only through a transparent consequence model.
- **TRIGGER:** Systems with heterogeneous outcomes, repeated operation, rare harms or multiple stakeholders.
- **CHEAP_PATH:** For a single exact binary requirement with no temporal/context dimension, one authoritative result may be sufficient.
- **MEASUREMENT_PRECONDITIONS:** Measurement error is separated by dimension and thresholds remain stable.
- **ASSUMPTIONS:** Dimensions are not falsely treated as independent; composite utility, if used, is explicit and decision-owned.
- **DECISION_OR_CONSUMER:** Design/release authority, risk owner and public evidence consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Mean-only benchmark; variance ignored; uptime without severity; composite weights changed; tail based on one anecdote. Contrary evidence/limit: Multi-criteria trade-offs are partly normative and may resist statistical aggregation; unresolved conflicts must remain visible. Contrary evidence/limit: Multi-criteria trade-offs are partly normative and may resist statistical aggregation; unresolved conflicts must remain visible.
- **ANTI_CEREMONY_BOUNDARY:** A mandatory giant dashboard is not the property; non-substitution among materially different risk dimensions is.
- **POSSIBLE_CONFLICTING_PROPERTY:** P041/P057 cost and P021 false-alarm control can conflict with extreme-tail vigilance; P049 context shift can defeat pooled reliability claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Are mean, variability, tail, time reliability and context robustness being claimed separately?
  - Could a favourable average conceal a serious tail or durability regression?
  - Who owns any composite weighting, and was it frozen before results?

### P051 — Treat optimised metrics as vulnerable proxies and monitor for gaming/surrogation

- **PROPERTY_ID:** `P051`
- **PROPERTY_NAME:** Treat optimised metrics as vulnerable proxies and monitor for gaming/surrogation
- **FAILURE_MODE:** Relabelled defects, denominator shifts, benchmark overfitting, threshold gaming and local metric improvement with system harm.
- **MATURE_FORM:** Use metrics as defeasible sensors: preserve an independent construct/outcome path and investigate divergence under optimisation.
- **TRIGGER:** High-stakes target metrics, leaderboards, incentives, automated optimisation or repeated candidate exposure.
- **CHEAP_PATH:** For a direct authoritative physical/logical property that cannot be cheaply manipulated, proxy safeguards may be minimal; maintain authority/integrity checks.
- **MEASUREMENT_PRECONDITIONS:** Metric and construct are distinguishable; evaluator changes and candidate exposures are versioned.
- **ASSUMPTIONS:** A plausible behavioural/optimisation mechanism links targeting to metric degradation; independent checks are not co-optimised.
- **DECISION_OR_CONSUMER:** Metric owner, incentive/release authority and system outcome owner.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Detect divergence between a governed metric and the underlying system outcome.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Metric and latent goal co-evolve under optimisation/incentives.
  - **MEASUREMENT_PRECONDITIONS:** Independent outcome/reference measures, provenance and stable definitions.
  - **SIGNAL_OR_DISCRIMINATOR:** Metric–outcome divergence, exclusion/denominator anomalies or mechanism failure.
  - **FALSE_POSITIVE_COST:** False accusations of gaming and metric churn.
  - **FALSE_NEGATIVE_COST:** Sustained optimisation of a corrupted proxy.
  - **NONSTATIONARITY_RISK:** Very high because optimisation changes behaviour/data.
  - **INTERVENTION_RISK:** Changing the metric after each exploitation can create evaluator instability.
  - **CHEAP_PATH:** Direct outcome/mechanism check when cheap.
  - **MATURE_FORM:** Protected independent checks, versioning and controlled metric retirement.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** MODERATE
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Dropping hard cases; changing denominator; teaching to test; benchmark leakage; proxy chosen for availability; outcome not independently checked. Contrary evidence/limit: Goodhart/Campbell claims are not universal formal theorems; some metrics remain useful under targeting if causal alignment and integrity controls are strong. Contrary evidence/limit: Goodhart/Campbell claims are not universal formal theorems; some metrics remain useful under targeting if causal alignment and integrity controls are strong.
- **ANTI_CEREMONY_BOUNDARY:** “Use multiple KPIs” is not itself the property; independent construct evidence and anti-substitution boundaries are.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can the target metric be improved without improving the underlying engineering property?
  - Have denominators, labels, exclusions or case mix changed under incentive?
  - What independent outcome or mechanism evidence would expose proxy capture?

### P052 — Require independent, prospective justification before changing an evaluator, fixture, expected answer or threshold after failure

- **PROPERTY_ID:** `P052`
- **PROPERTY_NAME:** Require independent, prospective justification before changing an evaluator, fixture, expected answer or threshold after failure
- **FAILURE_MODE:** Evaluator drift, threshold drift, moving goalposts and reward hacking disguised as recalibration.
- **MATURE_FORM:** Change only on independent evidence that the measurement/construct—not merely the candidate—is defective or context has legitimately changed.
- **TRIGGER:** Any proposed evaluator/threshold/fixture/answer change triggered by an unfavourable result.
- **CHEAP_PATH:** Correct a provable transcription/specification error immediately, preserving evidence and authority; no large statistical study is needed.
- **MEASUREMENT_PRECONDITIONS:** Reference cases include failures/boundaries and are protected from the candidate change.
- **ASSUMPTIONS:** The bridge can distinguish measurement defect from candidate defect; updated rule better represents the underlying construct.
- **DECISION_OR_CONSUMER:** Measurement/evaluator owner, release authority and independent reviewer.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Decide whether an apparent failure warrants candidate correction or evaluator recalibration.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Candidate state and evaluator state both potentially vary; reference bridge observes both versions.
  - **MEASUREMENT_PRECONDITIONS:** Frozen versions, protected reference cases and independent adjudication.
  - **SIGNAL_OR_DISCRIMINATOR:** Reference-based evidence that old evaluator is biased/invalid and new one improves construct fidelity.
  - **FALSE_POSITIVE_COST:** Freezing a defective evaluator or false recalibration alarm.
  - **FALSE_NEGATIVE_COST:** Outcome-contingent evaluator mutation that converts failure to pass.
  - **NONSTATIONARITY_RISK:** Context/construct change may legitimately require revision.
  - **INTERVENTION_RISK:** Core risk: threshold/answer movement after seeing failure.
  - **CHEAP_PATH:** Fix an authoritative clerical/specification error with documented source.
  - **MATURE_FORM:** Independent prospective bridge, versioning and retrospective impact review.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** HIGH
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Changing expected output after seeing candidate; threshold chosen to include current score; deleting failed case; no old/new bridge; circular validation. Contrary evidence/limit: Independent reference truth may be unavailable for evolving constructs; legitimate change can remain unresolved rather than forced. Contrary evidence/limit: Independent reference truth may be unavailable for evolving constructs; legitimate change can remain unresolved rather than forced.
- **ANTI_CEREMONY_BOUNDARY:** A fixed change-request form is optional; independence, bridge and retrospective impact assessment are the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Was the evaluator/threshold change proposed only after a candidate failed?
  - What evidence independent of that candidate shows a measurement or construct defect?
  - Is there a blinded old/new bridge and an assessment of affected prior conclusions?

### P053 — Separate candidate/process variation from evaluator/measurement variation before assigning corrective action

- **PROPERTY_ID:** `P053`
- **PROPERTY_NAME:** Separate candidate/process variation from evaluator/measurement variation before assigning corrective action
- **FAILURE_MODE:** Fixing the wrong component, circular debugging and endless candidate/evaluator oscillation.
- **MATURE_FORM:** Hold one side fixed while testing the other against independent references; leave unresolved when evidence cannot distinguish.
- **TRIGGER:** Unexpected regression/improvement, disagreement across evaluators, near-threshold failures or repeated nonreproducibility.
- **CHEAP_PATH:** If a direct inspection proves a deterministic candidate defect or evaluator bug, repair that source immediately and document it.
- **MEASUREMENT_PRECONDITIONS:** Measurement runs are comparable; reference cases cover the disputed region.
- **ASSUMPTIONS:** Variance components/interactions are estimable enough to discriminate source or else conclusion remains unresolved.
- **DECISION_OR_CONSUMER:** Engineer, measurement owner and independent review authority.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Discriminate whether a changed result arises from candidate, evaluator or their interaction.
  - **EXPERIMENTAL_UNIT:** Candidate/reference item crossed with evaluator/version/condition.
  - **INDEPENDENCE_ASSUMPTION:** Repeated observations nested; independent items required for generalisation.
  - **RANDOMISATION_OR_CONTROL:** Randomise/blind order and candidate identity.
  - **BLOCKING_OR_STRATIFICATION:** Block time/environment and preserve bridge overlap.
  - **REPLICATION_MEANING:** Multiple stable items and independently executed evaluator runs.
  - **INTERACTION_RISK:** Candidate×evaluator interaction is often the decisive finding.
  - **STOPPING_RULE:** Predefine suspected-source comparisons; do not stop at first favourable rerun.
  - **EXPECTED_INFORMATION_GAIN:** Directs corrective action to the varying component.
  - **COST:** Reference construction and crossed reruns.
  - **FAILURE_IF_OVER_APPLIED:** Full crossing can be expensive or impossible for destructive systems.
  - **MATURE_FORM:** Smallest crossed/bridge design that separates source, with unresolved outcome if not identifiable.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** VERY_HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** LOW
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Only rerunning candidate; only checking easy references; evaluator and candidate changed together; no interaction analysis; regression to mean. Contrary evidence/limit: Variance decomposition can identify where variability resides but not automatically which construct is correct or why the interaction occurs. Contrary evidence/limit: Variance decomposition can identify where variability resides but not automatically which construct is correct or why the interaction occurs.
- **ANTI_CEREMONY_BOUNDARY:** A GR&R percentage is not required; discriminating source of variation is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Before changing the candidate, what evidence shows the evaluator is stable and valid?
  - Before changing the evaluator, what evidence shows stable references are mismeasured?
  - Were candidate and evaluator ever varied independently in a crossed design?

### P054 — Protect holdouts, reproduce analyses and prevent adaptive evaluation reuse from masquerading as fresh evidence

- **PROPERTY_ID:** `P054`
- **PROPERTY_NAME:** Protect holdouts, reproduce analyses and prevent adaptive evaluation reuse from masquerading as fresh evidence
- **FAILURE_MODE:** Benchmark saturation, test contamination, hidden analyst flexibility and false replication.
- **MATURE_FORM:** State what was reused, what was protected, and what evidence is genuinely fresh; use independent confirmation for final claims.
- **TRIGGER:** Iterative software/ML/agent development, repeated benchmark submissions, many model/analysis variants or long campaigns.
- **CHEAP_PATH:** For a deterministic exhaustive authoritative test, repeated execution may verify implementation but does not need a statistical holdout.
- **MEASUREMENT_PRECONDITIONS:** Evaluation pipeline itself is stable/validated; contamination/duplication detectable.
- **ASSUMPTIONS:** Protected sample remains sufficiently independent; reusable-holdout privacy/model conditions or fresh-data assumptions hold.
- **DECISION_OR_CONSUMER:** Developer, benchmark owner, reviewer and deployment authority.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Confirm generalisation after adaptive development/analysis.
  - **EXPERIMENTAL_UNIT:** Fresh independently sampled evaluation unit.
  - **INDEPENDENCE_ASSUMPTION:** Shared source/duplicates and repeated holdout use induce dependence.
  - **RANDOMISATION_OR_CONTROL:** Treatment randomisation if causal; data access control for predictive confirmation.
  - **BLOCKING_OR_STRATIFICATION:** Stratify fresh set by decision-relevant contexts.
  - **REPLICATION_MEANING:** Independent fresh units/datasets, not resampling the exposed holdout.
  - **INTERACTION_RISK:** Performance may interact with collection/context shift.
  - **STOPPING_RULE:** Predefine final access/look or use valid reusable-holdout protocol.
  - **EXPECTED_INFORMATION_GAIN:** Unbiased/controlled confirmation after adaptivity.
  - **COST:** Fresh data, secrecy/access governance and reproducible pipeline.
  - **FAILURE_IF_OVER_APPLIED:** Excessive holdout fragmentation or no debugging signal.
  - **MATURE_FORM:** Transparent reuse accounting plus protected/fresh confirmation and shift analysis.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** MODERATE
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** VERY_HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Calling same holdout reruns “replications”; public test labels; leaderboard tuning; analysis not executable; fresh test collected differently. Contrary evidence/limit: Fresh data can differ for reasons unrelated to overfitting; holdout protection trades off feedback, shift and sample efficiency. Contrary evidence/limit: Fresh data can differ for reasons unrelated to overfitting; holdout protection trades off feedback, shift and sample efficiency.
- **ANTI_CEREMONY_BOUNDARY:** A fixed split percentage or preregistration badge is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which results come from fresh protected evidence rather than evaluator reuse?
  - Does exact computational reproduction add independent information or only verify execution?
  - Has test-set access, contamination and feedback been audited?

### P055 — Check model adequacy and misspecification against the decision, not through ritual assumption tests

- **PROPERTY_ID:** `P055`
- **PROPERTY_NAME:** Check model adequacy and misspecification against the decision, not through ritual assumption tests
- **FAILURE_MODE:** Invalid intervals/control limits/extrapolations and false confidence in a convenient fitted model.
- **MATURE_FORM:** Use the simplest adequate model and report which guarantees are conditional; switch/robustify when a departure changes the decision.
- **TRIGGER:** Any inferential/control/reliability method whose operating characteristics depend materially on distribution, independence, link or functional form.
- **CHEAP_PATH:** For deterministic checks or methods robust by design to the relevant deviation, skip irrelevant normality tests and document why.
- **MEASUREMENT_PRECONDITIONS:** Measurement artefacts/censoring/rounding are modelled or ruled out before diagnosing process distribution.
- **ASSUMPTIONS:** Diagnostics have power for material deviations; alternative models are plausible and not chosen only for desired results.
- **DECISION_OR_CONSUMER:** Analyst, monitoring/experiment owner and reviewer.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Validate the model used to set limits, detect shifts or predict capability.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Proposed probabilistic/dynamic model versus observed residual/predictive structure.
  - **MEASUREMENT_PRECONDITIONS:** Stable measurements, time/order and enough baseline coverage.
  - **SIGNAL_OR_DISCRIMINATOR:** Decision-relevant lack-of-fit, calibration or operating-characteristic failure.
  - **FALSE_POSITIVE_COST:** Discarding a useful simple model for trivial deviations.
  - **FALSE_NEGATIVE_COST:** Using invalid limits/predictions under material misspecification.
  - **NONSTATIONARITY_RISK:** Model adequacy can expire as process/context shifts.
  - **INTERVENTION_RISK:** Refitting until alarms vanish can absorb real change.
  - **CHEAP_PATH:** Use distribution-free/direct limits or mechanism-based discriminator.
  - **MATURE_FORM:** Purpose-specific model checks, sensitivity and versioned refit governance.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** VERY_HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** MODERATE
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** HIGH
  - **DOMAIN_CASE_STRENGTH:** VERY_HIGH
  - **REPLICATION_STRENGTH:** HIGH
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** VERY_HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** HIGH
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Mandatory Shapiro–Wilk; accepting model because p>.05; residuals not time-ordered; transformation after seeing desired significance; no out-of-sample check. Contrary evidence/limit: Model adequacy is never globally established; it is conditional on data region and purpose, and diagnostics can share blind spots. Contrary evidence/limit: Model adequacy is never globally established; it is conditional on data region and purpose, and diagnostics can share blind spots.
- **ANTI_CEREMONY_BOUNDARY:** A normality test checklist is ceremony; decision-sensitive adequacy is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which assumption could materially change the decision?
  - Were diagnostics matched to time, dependence, tails and prediction—not only normality?
  - Is a robust or deterministic alternative available that avoids the fragile assumption?

### P056 — Integrate multiple statistical and engineering methods into a system-level evidence strategy

- **PROPERTY_ID:** `P056`
- **PROPERTY_NAME:** Integrate multiple statistical and engineering methods into a system-level evidence strategy
- **FAILURE_MODE:** Cookbook statistics, tool proliferation, local optimisation and unresolved interfaces between measurement, experimentation and action.
- **MATURE_FORM:** A problem-structuring and integration property: right evidence, right order, right scale, with assumptions and consumer decisions explicit.
- **TRIGGER:** Cross-disciplinary problems too large for one model/test and with multiple linked decisions.
- **CHEAP_PATH:** For a well-structured local question solved by one authoritative method/check, use that method; system-level statistical engineering would be overhead.
- **MEASUREMENT_PRECONDITIONS:** Every input measurement/evaluator has sufficient fitness and common identities/units are maintained.
- **ASSUMPTIONS:** Integration logic is auditable; no method’s assumptions are silently contradicted by another stage; organisational cooperation exists.
- **DECISION_OR_CONSUMER:** System/problem owner, cross-functional engineering team and decision governance.
- **VARIATION_CONTROL_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **HYPOTHESIS_OR_DECISION:** Sequence a portfolio of experiments/measurements to resolve a complex system decision.
  - **EXPERIMENTAL_UNIT:** Varies by subproblem; integration must preserve each true experimental unit.
  - **INDEPENDENCE_ASSUMPTION:** Cross-study dependence/common data and shared evaluators must be represented.
  - **RANDOMISATION_OR_CONTROL:** Use randomisation where causal; do not force it on deterministic subproblems.
  - **BLOCKING_OR_STRATIFICATION:** Coordinate blocking/stratification across relevant interfaces.
  - **REPLICATION_MEANING:** Independent confirmation at system-critical claims, not repeated local analyses.
  - **INTERACTION_RISK:** Cross-component interactions and local-to-system trade-offs are central.
  - **STOPPING_RULE:** Mission-level stopping based on remaining decision uncertainty/value.
  - **EXPECTED_INFORMATION_GAIN:** Reduces dominant uncertainty across the whole problem.
  - **COST:** Coordination, data integration and cross-disciplinary time.
  - **FAILURE_IF_OVER_APPLIED:** Framework bureaucracy or endless decomposition.
  - **MATURE_FORM:** Lean problem architecture with explicit evidence dependencies and local method cheap paths.
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** MODERATE
  - **FORMAL_OR_THEORETICAL_STRENGTH:** MODERATE
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** MODERATE
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** LOW
  - **TRANSFERABILITY_STRENGTH:** HIGH
  - **ASSUMPTION_SENSITIVITY:** MODERATE
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Framework phases treated as deliverables; tool count mistaken for rigour; no dominant uncertainty; local Cpk improvement harms system outcome. Contrary evidence/limit: Evidence is strong for component methods and plausible for integration, but weak for a unique discipline-wide causal effect independent of competent engineering management. Contrary evidence/limit: Evidence is strong for component methods and plausible for integration, but weak for a unique discipline-wide causal effect independent of competent engineering management.
- **ANTI_CEREMONY_BOUNDARY:** The label, framework diagram or consultancy is not the property; integration and sustainable decision improvement are.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does the target problem require several evidence methods whose dependencies must be engineered?
  - Is the dominant uncertainty identified before selecting tools?
  - Could a single local method or deterministic check solve the decision more cheaply?

### P057 — Make measurement and controls economically proportional; retire, revalidate or recalibrate stale controls

- **PROPERTY_ID:** `P057`
- **PROPERTY_NAME:** Make measurement and controls economically proportional; retire, revalidate or recalibrate stale controls
- **FAILURE_MODE:** Measurement debt, stale controls, alert fatigue, audit theatre and resources diverted from higher-value evidence.
- **MATURE_FORM:** Every recurring control has a current decision, validity evidence and proportional cost; otherwise simplify, replace, revalidate or retire with risk sign-off.
- **TRIGGER:** Long-lived quality systems, recurring tests, duplicated reviews, low-yield monitoring or changed process/evaluator context.
- **CHEAP_PATH:** Keep cheap high-value controls and legal/safety requirements even if failures are rare; deterministic checks may remain near-zero cost.
- **MEASUREMENT_PRECONDITIONS:** Control outcomes and false alarms/misses are measurable enough to assess utility; reference standards remain available.
- **ASSUMPTIONS:** Past yield predicts some future value or scenario analysis captures uncertainty; retirement does not violate unmodelled catastrophic safeguards.
- **DECISION_OR_CONSUMER:** Control owner, risk authority, resource allocator and downstream consumer.
- **VARIATION_CONTROL_PROFILE:**
  - **DECISION_PROBLEM:** Retain, tune, replace or retire a recurring control.
  - **ASSUMED_DATA_GENERATING_PROCESS:** Control outcomes and underlying risk/process evolve over time.
  - **MEASUREMENT_PRECONDITIONS:** Usage/decision/false-alarm records and current reference validation.
  - **SIGNAL_OR_DISCRIMINATOR:** Positive net decision value and valid calibration for present context.
  - **FALSE_POSITIVE_COST:** Ongoing cost, alert fatigue and tampering.
  - **FALSE_NEGATIVE_COST:** Loss of early warning or rare-event defence.
  - **NONSTATIONARITY_RISK:** Core: process/evaluator/risk drift makes controls stale.
  - **INTERVENTION_RISK:** Retirement after inconvenient failures can be proxy gaming.
  - **CHEAP_PATH:** Retain a cheap deterministic check or consolidate duplicates.
  - **MATURE_FORM:** Lifecycle evidence review with independent retirement authority and risk bounds.
- **EXPERIMENT_DISCRIMINATION_PROFILE:**
  - **APPLICABILITY:** NOT_PRIMARY_FOR_THIS_PROPERTY
- **EVIDENCE_STRENGTH:**
  - **HISTORICAL_PROVENANCE_STRENGTH:** HIGH
  - **FORMAL_OR_THEORETICAL_STRENGTH:** HIGH
  - **MEASUREMENT_SCIENCE_STRENGTH:** HIGH
  - **EMPIRICAL_CAUSAL_STRENGTH:** LOW
  - **EMPIRICAL_ASSOCIATIONAL_STRENGTH:** MODERATE
  - **DOMAIN_CASE_STRENGTH:** HIGH
  - **REPLICATION_STRENGTH:** MODERATE
  - **TRANSFERABILITY_STRENGTH:** VERY_HIGH
  - **ASSUMPTION_SENSITIVITY:** HIGH
  - **CONTRARY_EVIDENCE_STRENGTH:** MODERATE
- **CRITICISMS:** The property is bounded by its stated assumptions and known failures: Quota retained with no consumer; threshold never revalidated; duplicated tests treated as corroboration; control removed because it catches failures. Contrary evidence/limit: Rare-event controls may have high option value despite little observed use; absence of catches is not sufficient retirement evidence. Contrary evidence/limit: Rare-event controls may have high option value despite little observed use; absence of catches is not sufficient retirement evidence.
- **ANTI_CEREMONY_BOUNDARY:** A periodic review ceremony is not the property unless it can actually retire/change controls on evidence.
- **POSSIBLE_CONFLICTING_PROPERTY:** P009/P010 legitimate adaptation can conflict with P052 anti-mutation governance; P057 retirement can conflict with P048 rare-event caution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What current decision does each recurring measurement/control change?
  - When was its measurement validity and threshold last challenged against current context?
  - Would retirement remove rare-event defence or merely ceremony?


## CEREMONIES_TO_NOT_BLINDLY_ADOPT

| Property ID | Practice / artefact | Disposition | Surviving property |
| --- | --- | --- | --- |
| P058 | Universal p < 0.05 threshold as an engineering decision rule | REJECTED_OR_DISFAVOURED | Use error thresholds only when tied to a declared family, effect/decision and consequence; otherwise report continuous evidence and uncertainty. |
| P059 | Control-chart-everything and automatic run-rule escalation | CEREMONY_NOT_GENERAL_PROPERTY | Monitor only where the stream, signal, cost and response are defensible; otherwise choose a cheaper direct/qualitative method. |
| P060 | Universal 3.4 DPMO or “six-sigma level” as the definition of quality | CEREMONY_NOT_GENERAL_PROPERTY | Set targets from customer/safety/economic consequences and observed/modelled risk, not brand numerology. |
| P061 | DMAIC/DMADV phase names and tollgates as a general statistical property | CEREMONY_NOT_GENERAL_PROPERTY | Retain evidence dependencies and governance where useful; strip mandatory branding and tailor path to problem risk/uncertainty. |
| P062 | Belt hierarchy and certification as a general engineering property | CEREMONY_NOT_GENERAL_PROPERTY | Use role/competence systems proportionate to need and assess actual decisions/work products; no required belt taxonomy. |
| P063 | More samples, more reruns or repeated green tests automatically mean more truth | REJECTED_OR_DISFAVOURED | Another observation earns weight only through identifiable independent/conditional information and positive decision value. |
| P064 | Mandatory normality tests, fixed gauge R&R cutoffs and full MSA paperwork for every metric | CEREMONY_NOT_GENERAL_PROPERTY | Use the smallest diagnostic/MSA design that can falsify decision adequacy. |
| P065 | Universal Taguchi signal-to-noise ratios and orthogonal-array recipes as the definition of robust design | SUPERSEDED_BY_STRONGER_FORM | Model the actual mean, variance, tails and noise-factor interactions; use a Taguchi criterion only when demonstrably appropriate. |

Additional artefact-level warnings:

- Universal p < 0.05 gate — REJECTED_AS_UNIVERSAL; conditional tests retained
- Control chart for every metric — USE_ONLY_WITH_POSITIVE_DECISION_VALUE
- Western Electric rule stack by default — CONTEXT_DEPENDENT
- Cpk/sigma score on any data — ASSUMPTION_SENSITIVE
- 3.4 DPMO universal target — CEREMONY_NOT_GENERAL_PROPERTY
- DMAIC/DMADV names and tollgates — OPTIONAL_PROGRAMME_ARTEFACT
- Belt hierarchy/certification — OPTIONAL_PROGRAMME_ARTEFACT
- Fixed 10×3×3 GR&R and universal percentage cutoff — USE_ONLY_WHEN_DESIGN_MATCHES
- Mandatory normality test — REJECTED_AS_UNIVERSAL
- Acceptance sampling as quality programme — DOMAIN_SPECIFIC_AND_NARROWED
- Full factorial/DOE for every change — CONTEXT_DEPENDENT
- Taguchi S/N ratio and orthogonal array recipe — SUPERSEDED_BY_STRONGER_FORM
- Repeated green-run quota — REJECTED_AS_UNIVERSAL
- Single composite quality score — USEFUL_BUT_EASILY_GAMED
- Automatic periodic recalibration/rebaseline — RETAINED_ONLY_WITH_INDEPENDENCE
- Permanent legacy control because “we always measured it” — RETIRE_OR_REVALIDATE

## CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

- An authoritative deterministic proof, exhaustive check, exact specification lookup or direct physical discriminator already settles the decision (P042).
- The decision margin is far wider than plausible measurement/sampling variation and consequence is low (P002, P006–P007).
- There is no coherent time-ordered process, stable regime, response owner or action for a control signal (P015–P024, P059).
- A lot does not need statistical acceptance because 100% reliable inspection is cheaper and non-destructive, or no lot-risk decision exists (P026).
- One-factor or exhaustive search is genuinely cheap, interactions cannot matter to the decision, or a mechanistic model already identifies the choice (P033–P035).
- Sequential monitoring is unnecessary because the outcome is available once at a fixed horizon and interim action has no value (P038).
- Accelerated/reliability inference cannot preserve the use-condition failure mechanism (P044–P048).
- The metric is local/ordinal and no cross-context traceability or invariance claim is made (P003, P009).
- Another measurement is strongly dependent on the same unit, seed, batch, reference and evaluator and cannot change action (P032, P041, P057).
- The named artefact adds no evidential dependency beyond competent existing governance (P061–P062).

## MEASUREMENT_PRECONDITIONS_THAT_CAN_BLOCK_USE

- The measurand/construct does not preserve the decision-relevant distinctions (P001).
- Measurement variation or bias is large enough to cross the action boundary (P002, P004, P007).
- The reference chain is absent, stale, outside range/context, or itself shares the suspected bias (P003, P011).
- Resolution, sensitivity or specificity is inadequate at the required threshold (P006).
- The evaluator is repeatable but not reproducible or valid across required operators/sites/versions (P005, P008–P009).
- Instrument/evaluator/threshold drift is not bridged to the baseline (P010, P052).
- Sampling, missingness, censoring, exclusion or contamination prevents population interpretation (P013–P014, P025).
- Data, preprocessing, evaluator or threshold provenance cannot be reconstructed (P012).
- Process/candidate and evaluator variation changed together and cannot be separated (P053).
- A destructive or intervention-sensitive measurement alters the state being inferred (P014).

## PROPERTIES_WITH_STRONG_FORMAL_BUT_WEAK_TRANSFER_EVIDENCE

| ID | Property | Formal strength | Transferability | Assumption sensitivity | Why transfer is bounded |
| --- | --- | --- | --- | --- | --- |
| P003 | Calibration and metrological traceability where decision-relevant | HIGH | MODERATE | LOW | Some digital/subjective measurements lack a meaningful SI chain; analogous provenance does not equal metrological traceability. |
| P014 | Account for measurement intervention, destruction and contamination | HIGH | MODERATE | VERY_HIGH | In adaptive systems, measurement and improvement may be inseparable by design; the goal becomes explicit online-learning evaluation rather than pretending independence. |
| P015 | Discriminate routine/common variation from evidence of a changed process | HIGH | MODERATE | HIGH | In highly adaptive or nonstationary systems there may be no enduring common-cause baseline; change detection must be reframed around local regimes or forecasts. |
| P019 | Use capability indices only conditionally on stability, distribution and measurement fitness | HIGH | MODERATE | VERY_HIGH | Tail defect-rate claims can be dominated by model error far beyond observed data; index precision is not tail certainty. |
| P022 | Adapt monitoring to autocorrelation, seasonality, drift and nonstationarity | VERY_HIGH | MODERATE | VERY_HIGH | Under adversarial or abrupt concept change, historical calibration may fail exactly when needed; guarantees are local/conditional. |
| P024 | Use context-adapted multivariate, rare-event, short-run or change-point monitoring only when its added discrimination pays | VERY_HIGH | MODERATE | VERY_HIGH | Rare-event detector performance is often weakly estimable; simulation depends on an assumed tail/model and can create false certainty. |
| P026 | Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it | VERY_HIGH | LOW | HIGH | Changing lot composition, adversarial suppliers and severe item heterogeneity can invalidate nominal OC risks. |
| P034 | Use fractional factorial/screening designs only with explicit alias and sparsity assumptions | VERY_HIGH | MODERATE | VERY_HIGH | When effect sparsity fails or factors are adaptive/continuous, screening rankings can be unstable and model-dependent. |
| P044 | Model reliability over time with explicit failure definitions, exposure, censoring and degradation | VERY_HIGH | MODERATE | VERY_HIGH | Complex software/agent failure opportunities may not map cleanly to lifetime distributions; reliability methods transfer only where exposure/failure processes are coherent. |
| P045 | Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty | VERY_HIGH | LOW | VERY_HIGH | Extreme acceleration and sparse failures make model uncertainty dominant; there may be no defensible high-reliability extrapolation. |
| P046 | Treat reliability growth as intervention-conditioned evidence, not an automatically improving trend | HIGH | LOW | VERY_HIGH | Growth models are particularly vulnerable when few failures, many simultaneous changes or rapidly changing test environments exist. |
| P047 | Translate zero observed failures into an upper risk bound, never “perfect reliability” | VERY_HIGH | MODERATE | VERY_HIGH | Extremely low target rates are rarely demonstrable by direct testing alone; model/mechanism/operational evidence must be combined without pretending equivalence. |
| P048 | Treat rare-event and tail claims as distinct, data-hungry and model-sensitive | VERY_HIGH | MODERATE | VERY_HIGH | Unknown failure modes and dependence can dominate beyond-sample tails; precise numerical estimates may be less honest than conservative bounds/scenarios. |

## PROPERTIES_WITH_STRONG_EMPIRICAL_OR_DOMAIN_SUPPORT

| ID | Property | Domain strength | Replication strength | Evidence / sources |
| --- | --- | --- | --- | --- |
| P002 | Establish measurement-system fitness before metric governance | HIGH | HIGH | S015, S055, S058; S105, S024 |
| P003 | Calibration and metrological traceability where decision-relevant | VERY_HIGH | HIGH | S052, S054, S056; S105 |
| P004 | Keep bias/accuracy distinct from precision | HIGH | HIGH | S015, S052, S057; S055 |
| P005 | Distinguish repeatability, reproducibility and validity | HIGH | HIGH | S057, S058, S059; S105, S038 |
| P007 | Carry measurement uncertainty into engineering decisions | VERY_HIGH | HIGH | S051, S053, S100; S015, S055 |
| P008 | Evaluate inter-rater/evaluator agreement with a design matched to use | HIGH | HIGH | S024, S059, S057; S105 |
| P010 | Monitor evaluator/instrument drift and require independent recalibration evidence | HIGH | HIGH | S015, S060, S056; S105, S032 |
| P012 | Preserve data provenance, preprocessing, version and lineage | VERY_HIGH | HIGH | S056, S038, S110; S105 |
| P013 | Model missingness, censoring, exclusions and selection mechanisms | VERY_HIGH | HIGH | S020, S071, S077; S087 |
| P015 | Discriminate routine/common variation from evidence of a changed process | VERY_HIGH | HIGH | S001, S002, S003; S061, S066, S106 |
| P016 | Choose rational subgroups and model dependence rather than count correlated observations as sample size | HIGH | HIGH | S002, S023, S026; S032, S107 |
| P017 | Keep statistical control limits separate from engineering specifications and tolerances | VERY_HIGH | HIGH | S001, S053, S062; S100, S107 |
| P018 | Establish process stability before interpreting capability or long-run prediction | VERY_HIGH | HIGH | S002, S062, S109; S107 |
| P019 | Use capability indices only conditionally on stability, distribution and measurement fitness | HIGH | HIGH | S062, S063, S064; S107, S109 |
| P020 | Prevent tampering and overadjustment to routine variation | HIGH | HIGH | S002, S003, S089; S014 |
| P021 | Design monitoring economically around false-alarm, missed-shift and delay costs | HIGH | HIGH | S014, S013, S065; S061, S107 |
| P025 | Design sampling to represent the decision population and selection process | VERY_HIGH | HIGH | S045, S020, S068; S087 |
| P026 | Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it | VERY_HIGH | HIGH | S008, S068, S069; S061 |
| P028 | Size samples around effect/precision, dependence and decision loss—not a universal count | HIGH | HIGH | S007, S046, S075; S073 |
| P029 | Frame experiments around an explicit engineering decision, estimand and rival alternatives | HIGH | HIGH | S005, S007, S018; S044, S080 |
| P030 | Use randomisation to protect causal comparisons against assignment bias and support valid error assessment | VERY_HIGH | VERY_HIGH | S005, S006, S018; S044, S037 |
| P031 | Block or stratify known nuisance variation without erasing interactions | VERY_HIGH | HIGH | S005, S006, S043; S044, S049 |
| P032 | Require independent replication at the experimental-unit level; treat technical repeats as measurement information | VERY_HIGH | VERY_HIGH | S005, S006, S023; S044, S039 |
| P033 | Use factorial structure to discover interactions and avoid one-factor-at-a-time ambiguity | VERY_HIGH | HIGH | S006, S043, S049; S044 |
| P034 | Use fractional factorial/screening designs only with explicit alias and sparsity assumptions | HIGH | HIGH | S010, S043, S044; S102 |
| P035 | Use response surfaces and iterative experimentation as local learning, with confirmation and boundary discipline | VERY_HIGH | HIGH | S009, S021, S049; S080 |
| P036 | Report effect magnitude, uncertainty and engineering significance; use equivalence/noninferiority when “no important difference” is the decision | VERY_HIGH | HIGH | S007, S029, S041; S046 |
| P037 | Control multiplicity, analyst degrees of freedom and selective inference across the actual family of opportunities | VERY_HIGH | HIGH | S028, S038, S040; S039 |
| P038 | Plan sequential evidence and stopping so repeated looks do not manufacture confidence | HIGH | HIGH | S011, S012, S036, S037; S035 |
| P039 | Bound causal claims by external validity, interference, carryover and order effects | HIGH | HIGH | S018, S047, S048; S037 |
| P040 | Use robustness and sensitivity analysis to expose dependence on model, confounding and nuisance assumptions | HIGH | HIGH | S016, S017, S021; S039 |
| P043 | Design robustness to nuisance factors and context variation, not only nominal mean performance | VERY_HIGH | HIGH | S025, S049, S095; S094 |
| P044 | Model reliability over time with explicit failure definitions, exposure, censoring and degradation | VERY_HIGH | HIGH | S071, S077, S104; S075 |
| P045 | Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty | HIGH | HIGH | S072, S076, S077; S071 |
| P047 | Translate zero observed failures into an upper risk bound, never “perfect reliability” | VERY_HIGH | HIGH | S073, S075, S071; S068 |
| P050 | Keep mean performance, variability, tail behaviour, reliability over time and model robustness as separate claims | VERY_HIGH | HIGH | S062, S071, S074; S043, S099 |
| P052 | Require independent, prospective justification before changing an evaluator, fixture, expected answer or threshold after failure | VERY_HIGH | HIGH | S015, S053, S060; S100, S103 |
| P053 | Separate candidate/process variation from evaluator/measurement variation before assigning corrective action | VERY_HIGH | HIGH | S058, S032, S024; S105 |
| P054 | Protect holdouts, reproduce analyses and prevent adaptive evaluation reuse from masquerading as fresh evidence | VERY_HIGH | HIGH | S038, S039, S040; S037 |
| P055 | Check model adequacy and misspecification against the decision, not through ritual assumption tests | VERY_HIGH | HIGH | S017, S021, S110; S099 |

## PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

| ID | Property | Status | Evidence limit | Open question |
| --- | --- | --- | --- | --- |
| P014 | Account for measurement intervention, destruction and contamination | CONTEXT_DEPENDENT | In adaptive systems, measurement and improvement may be inseparable by design; the goal becomes explicit online-learning evaluation rather than pretending independence. | When is reuse acceptable because the deployment itself includes learning from feedback? |
| P016 | Choose rational subgroups and model dependence rather than count correlated observations as sample size | ASSUMPTION_SENSITIVE | Dependence can be difficult to estimate with few clusters or changing correlation; conservative bounds may be preferable to elaborate fitted models. | How should evidence be discounted when shared prompts, seeds, fixtures or upstream data create partially known dependence? |
| P019 | Use capability indices only conditionally on stability, distribution and measurement fitness | ASSUMPTION_SENSITIVE | Tail defect-rate claims can be dominated by model error far beyond observed data; index precision is not tail certainty. | When should capability be expressed as scenario-specific prediction intervals rather than a scalar index? |
| P021 | Design monitoring economically around false-alarm, missed-shift and delay costs | CONTEXT_DEPENDENT | Cost and shift distributions are often uncertain; robust/minimax or scenario designs may be more honest than a single optimum. | How should monitoring be tuned when missed rare events have poorly quantifiable catastrophic loss? |
| P023 | Stratify mixtures, high-mix/low-volume and changing populations before aggregation | CONTEXT_DEPENDENT | With very sparse strata, estimates depend strongly on hierarchical priors/model sharing; no purely data-driven partition is definitive. | How should partial pooling be governed when local safety tails matter more than overall efficiency? |
| P024 | Use context-adapted multivariate, rare-event, short-run or change-point monitoring only when its added discrimination pays | CONTEXT_DEPENDENT | Rare-event detector performance is often weakly estimable; simulation depends on an assumed tail/model and can create false certainty. | What evidence threshold is sufficient to deploy a complex detector when incidents are too rare for direct validation? |
| P026 | Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it | DOMAIN_SPECIFIC | Changing lot composition, adversarial suppliers and severe item heterogeneity can invalidate nominal OC risks. | When do modern automated inspections make classical sampling economically obsolete? |
| P028 | Size samples around effect/precision, dependence and decision loss—not a universal count | ASSUMPTION_SENSITIVE | Rare catastrophic outcomes may require physical/structural evidence, conservative bounds or stress models because feasible samples cannot directly validate target rates. | How should sample planning combine epistemic uncertainty in variance/effect with asymmetric catastrophic loss? |
| P034 | Use fractional factorial/screening designs only with explicit alias and sparsity assumptions | ASSUMPTION_SENSITIVE | When effect sparsity fails or factors are adaptive/continuous, screening rankings can be unstable and model-dependent. | How should alias risk be priced when a missed interaction has severe safety consequences? |
| P039 | Bound causal claims by external validity, interference, carryover and order effects | CONTEXT_DEPENDENT | General transport under unmeasured effect modification is not identified from one experiment; mechanistic and multi-context evidence remain necessary. | What minimum context diversity is needed before an engineering effect can be treated as robust rather than local? |
| P040 | Use robustness and sensitivity analysis to expose dependence on model, confounding and nuisance assumptions | ASSUMPTION_SENSITIVE | Sensitivity conclusions are only as broad as the considered perturbations; unknown unknowns and structural model error remain. | How should plausible perturbation sets be governed so they are neither result-preserving nor impossibly broad? |
| P041 | Choose experiments and measurements by expected information or decision value relative to cost | CONTEXT_DEPENDENT | Deep uncertainty and irreversible tail harms can defeat expected-value summaries; robust/safety constraints may override average information value. | How should option/discovery value and catastrophic constraints be combined with expected information value? |
| P044 | Model reliability over time with explicit failure definitions, exposure, censoring and degradation | DOMAIN_SPECIFIC | Complex software/agent failure opportunities may not map cleanly to lifetime distributions; reliability methods transfer only where exposure/failure processes are coherent. | How should reliability be defined for continually updated systems whose configuration and workload change during exposure? |
| P045 | Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty | ASSUMPTION_SENSITIVE | Extreme acceleration and sparse failures make model uncertainty dominant; there may be no defensible high-reliability extrapolation. | How much use-condition anchoring is enough to falsify an acceleration model before release? |
| P046 | Treat reliability growth as intervention-conditioned evidence, not an automatically improving trend | DOMAIN_SPECIFIC | Growth models are particularly vulnerable when few failures, many simultaneous changes or rapidly changing test environments exist. | How can causal contribution be allocated among bundled fixes without an infeasible factorial programme? |
| P047 | Translate zero observed failures into an upper risk bound, never “perfect reliability” | ASSUMPTION_SENSITIVE | Extremely low target rates are rarely demonstrable by direct testing alone; model/mechanism/operational evidence must be combined without pretending equivalence. | How should heterogeneous stress, common-mode failures and changing exposure be incorporated into zero-event bounds? |
| P048 | Treat rare-event and tail claims as distinct, data-hungry and model-sensitive | ASSUMPTION_SENSITIVE | Unknown failure modes and dependence can dominate beyond-sample tails; precise numerical estimates may be less honest than conservative bounds/scenarios. | What combination of stress, mechanism and operational data justifies a claim at a failure rate never directly observed? |
| P051 | Treat optimised metrics as vulnerable proxies and monitor for gaming/surrogation | USEFUL_BUT_EASILY_GAMED | Goodhart/Campbell claims are not universal formal theorems; some metrics remain useful under targeting if causal alignment and integrity controls are strong. | How can independent outcome checks remain independent when the whole organisation can observe and optimise them? |
| P055 | Check model adequacy and misspecification against the decision, not through ritual assumption tests | ASSUMPTION_SENSITIVE | Model adequacy is never globally established; it is conditional on data region and purpose, and diagnostics can share blind spots. | How should model uncertainty be communicated when several models are adequate centrally but diverge in the decision tail? |
| P057 | Make measurement and controls economically proportional; retire, revalidate or recalibrate stale controls | CONTEXT_DEPENDENT | Rare-event controls may have high option value despite little observed use; absence of catches is not sufficient retirement evidence. | How can stale-control retirement be distinguished from gaming away inconvenient evidence? |

## ASSUMPTION_SENSITIVE_PROPERTIES

| ID | Property | Status | Assumptions | Known failure modes |
| --- | --- | --- | --- | --- |
| P006 | Match resolution, sensitivity, specificity and threshold discrimination to the decision | MEASUREMENT_PRECONDITION_PROPERTY | Future cases are drawn from a relevant population or shift is monitored; class definitions remain stable. | Selecting threshold on the same test set; ignoring prevalence; changing expected answers after failures; resolution below tolerance width. |
| P008 | Evaluate inter-rater/evaluator agreement with a design matched to use | MEASUREMENT_PRECONDITION_PROPERTY | The selected agreement statistic matches fixed/random raters, absolute agreement/consistency and scale properties. | Using Pearson correlation; prevalence-sensitive kappa without context; shared rubric bias; adjudicating after seeing candidate identity. |
| P009 | Test measurement invariance and transport across contexts | MEASUREMENT_PRECONDITION_PROPERTY | Observed contexts span the intended deployment; unobserved effect modifiers are bounded or acknowledged. | Aggregate invariance hiding subgroup failure; recalibration on contaminated outcomes; using identical preprocessing as proof of meaning. |
| P010 | Monitor evaluator/instrument drift and require independent recalibration evidence | RETAINED_IN_EVOLVED_FORM | Reference drift is slower or independently detectable; repeated checks are not all affected by the same environmental cause. | Rebaselining after alarms; editing expected answers after seeing failures; check-set overfitting; no version bridge. |
| P011 | Use representative reference standards and challenge shared-reference bias | MEASUREMENT_PRECONDITION_PROPERTY | Sampled references cover decision-relevant variability and do not share all defects with the candidate measurement. | Using only pristine standards; treating consensus as truth; reusing public benchmarks until memorised; excluding failures from the reference pool. |
| P013 | Model missingness, censoring, exclusions and selection mechanisms | MEASUREMENT_PRECONDITION_PROPERTY | Chosen MAR/MCAR/censoring/selection assumptions approximate reality; sensitivity bounds cover uncertainty. | Calling failures “invalid”; censoring at different risk states; post-hoc subgroup restriction; imputation model trained on outcome leakage. |
| P014 | Account for measurement intervention, destruction and contamination | CONTEXT_DEPENDENT | Carryover/washout model is plausible or fresh independent units are available. | Calling warmed/cached retries independent; destructive test sample not representative; training on failed benchmark items; inadequate washout. |
| P015 | Discriminate routine/common variation from evidence of a changed process | RETAINED_IN_EVOLVED_FORM | The baseline is sufficiently homogeneous/stable for the chosen chart/model; dependence and mixtures are handled. | Control limits treated as specs; alarms treated as causes; retrospective cherry-picking; rebaselining away failures; worker blame. |
| P016 | Choose rational subgroups and model dependence rather than count correlated observations as sample size | ASSUMPTION_SENSITIVE | Within-subgroup homogeneity and between-subgroup opportunity for relevant change, or a valid dependence model. | Convenience subgroups; averaging across shifts; treating multiple outputs from one run as independent; one cluster per condition. |
| P018 | Establish process stability before interpreting capability or long-run prediction | STRONGLY_RETAINED | Future conditions reasonably resemble the characterised regime or are explicitly modelled. | Shuffled data; pooled shifts/products; one favourable window; rebaselined outliers; no evaluator-stability check. |
| P019 | Use capability indices only conditionally on stability, distribution and measurement fitness | ASSUMPTION_SENSITIVE | Selected index/distribution describes the regime and tail behaviour; sample size supports intended precision. | Cpk on unstable data; normal DPMO conversion under skew/dependence; ignoring confidence intervals; choosing the most favourable index. |
| P021 | Design monitoring economically around false-alarm, missed-shift and delay costs | CONTEXT_DEPENDENT | Operating-characteristic calculations approximate real dependence/nonstationarity and cost model includes tail consequences. | Stacking Western Electric rules without capacity; tuning on known incidents; no alert disposition; sampling quota detached from value. |
| P022 | Adapt monitoring to autocorrelation, seasonality, drift and nonstationarity | RETAINED_IN_EVOLVED_FORM | Dynamic model/residuals capture enough structure; change-point method’s calibration approximates deployment. | Fitting seasonality after every alarm; residuals with hidden model failure; changing mixtures; no intervention annotation. |
| P023 | Stratify mixtures, high-mix/low-volume and changing populations before aggregation | CONTEXT_DEPENDENT | Within-stratum models or standardisation preserve relevant tail/interaction behaviour; no hidden confounding remains. | Dropping hard categories; changing denominator; z-scoring incomparable tails; one global control limit; post-hoc subgroup hunting. |
| P024 | Use context-adapted multivariate, rare-event, short-run or change-point monitoring only when its added discrimination pays | CONTEXT_DEPENDENT | Selected detector’s null/change model or robust calibration approximates use; multiplicity across monitored features is controlled. | Hotelling score without diagnosis; Poisson chart under overdispersion; zero-event reassurance; model retrained after every alarm. |
| P025 | Design sampling to represent the decision population and selection process | STRONGLY_RETAINED | Probability or selection-model assumptions hold sufficiently; unobserved selection is bounded or disclosed. | Public/easy cases only; post-failure exclusion; duplicated source records; favourable time window; target population left implicit. |
| P026 | Use acceptance sampling only for bounded lot-disposition decisions where inspection cost or destruction justifies it | DOMAIN_SPECIFIC | Within-lot heterogeneity and production history are compatible with the plan; standard’s switching rules/context apply. | AQL interpreted as a guarantee; nonrandom sample; lot splitting; plan chosen after results; inspection error ignored. |
| P028 | Size samples around effect/precision, dependence and decision loss—not a universal count | ASSUMPTION_SENSITIVE | Planning model approximates design; effect threshold is engineering-justified; clusters/dependence known enough. | Counting repeated readings as n; planning on observed pilot effect; stopping when significant; ignoring multiplicity/attrition. |
| P032 | Require independent replication at the experimental-unit level; treat technical repeats as measurement information | EXPERIMENTAL_DESIGN_PROPERTY | Units are exchangeable/representative enough for intended scope; clusters and interference are modelled. | Same seed/environment; multiple metrics from one run; split observations from one batch; repeated test after adaptation; duplicated data lineage. |
| P033 | Use factorial structure to discover interactions and avoid one-factor-at-a-time ambiguity | EXPERIMENTAL_DESIGN_PROPERTY | Model hierarchy/sparsity or sufficient full design; no uncontrolled time/batch confounding. | OFAT; no randomisation; main effects interpreted despite strong interactions; multiple responses cherry-picked; no confirmation. |
| P034 | Use fractional factorial/screening designs only with explicit alias and sparsity assumptions | ASSUMPTION_SENSITIVE | Few active effects, high-order interactions negligible or follow-up can resolve ambiguity. | Resolution III main effects treated as clean; no foldover; factors dropped before interaction check; no confirmation. |
| P035 | Use response surfaces and iterative experimentation as local learning, with confirmation and boundary discipline | EXPERIMENTAL_DESIGN_PROPERTY | Local low-order approximation is adequate within each step; sequential data reuse is reflected in uncertainty. | Reporting fitted optimum without confirmation; extrapolating beyond design; stopping after favourable stage; no noise-factor test. |
| P036 | Report effect magnitude, uncertainty and engineering significance; use equivalence/noninferiority when “no important difference” is the decision | STRONGLY_RETAINED | Model/interval coverage is adequate; equivalence margin is fixed independently of observed results. | p<.05 presented without units; CI crossing zero called “same”; post-hoc equivalence margin; relative change hiding absolute harm. |
| P037 | Control multiplicity, analyst degrees of freedom and selective inference across the actual family of opportunities | STRONGLY_RETAINED | Chosen correction matches dependence and decision loss; unreported researcher flexibility is bounded. | Correcting only final p-values while selecting endpoints/models; post-hoc “primary” metric; repeated benchmark variants; favourable subgroup only. |
| P038 | Plan sequential evidence and stopping so repeated looks do not manufacture confidence | RETAINED_IN_EVOLVED_FORM | Procedure’s martingale/likelihood/independence conditions hold or robust alternatives are used; adaptive outcome switching is excluded. | Restarting tests after failure; treating every review as independent; stopping at first green; continuing only negative arms; changing metric midstream. |
| P039 | Bound causal claims by external validity, interference, carryover and order effects | CONTEXT_DEPENDENT | No hidden interference/carryover beyond the specified structure; sampled contexts cover intended use or extrapolation is bounded. | Users share treatments; same system state across arms; inadequate washout; one site; aggregate effect hides vulnerable context. |
| P040 | Use robustness and sensitivity analysis to expose dependence on model, confounding and nuisance assumptions | ASSUMPTION_SENSITIVE | Perturbation set spans credible alternatives rather than only convenient ones; robust method’s loss/neighbourhood matches consequence. | Only normality test; deleting “outliers” post hoc; robust estimator treated as assumption-free; sensitivity range chosen to preserve result. |
| P041 | Choose experiments and measurements by expected information or decision value relative to cost | CONTEXT_DEPENDENT | Utility/probability model or qualitative ranking is sufficiently credible; option value and irreversible harm are considered. | “More data” default; full factorial despite deterministic discriminator; no action change after result; cost omitted; catastrophic risk monetised casually. |
| P043 | Design robustness to nuisance factors and context variation, not only nominal mean performance | RETAINED_IN_EVOLVED_FORM | Tested noise factors represent deployment; interactions/model form are adequate; accelerated stresses do not introduce irrelevant mechanisms. | Using Taguchi S/N ratio automatically; unrealistic noise ranges; no confirmation; averaging away context-specific failures. |
| P044 | Model reliability over time with explicit failure definitions, exposure, censoring and degradation | DOMAIN_SPECIFIC | Independent/appropriately clustered lifetimes, censoring mechanism acceptable, distribution/regression model adequate over prediction horizon. | Removing early failures; right-censored units treated as nonfailures forever; mixed modes pooled; uptime denominator changed; threshold drift. |
| P045 | Use accelerated testing only with validated stress-to-use mechanisms and explicit extrapolation uncertainty | ASSUMPTION_SENSITIVE | Same relevant failure mechanisms and adequate acceleration/life distributions across tested-to-use range. | One stress level; no use anchor; pooled failure modes; extrapolation without interval; treating high-stress pass as field proof. |
| P046 | Treat reliability growth as intervention-conditioned evidence, not an automatically improving trend | DOMAIN_SPECIFIC | Model form approximates the repair/improvement process; changes other than intended fixes are documented. | Test difficulty decreases; failures reclassified; exposure resets; fixes not independently verified; one programme curve pooled across modes. |
| P047 | Translate zero observed failures into an upper risk bound, never “perfect reliability” | ASSUMPTION_SENSITIVE | Bernoulli/Poisson/exposure model and homogeneity or conservative stratification are adequate. | Counting repeated same-condition trials as independent; optional stopping after a clean run; changing failure definition; hiding near misses. |
| P048 | Treat rare-event and tail claims as distinct, data-hungry and model-sensitive | ASSUMPTION_SENSITIVE | Tail family/extrapolation and dependence are adequate; stress sampling is correctly reweighted; unobserved modes acknowledged. | Normal six-sigma extrapolation; dropping outliers; zero events called zero risk; tail metric tuned after incident; pooled modes. |
| P049 | Test distribution shift and stress contexts; do not equate held-out performance with deployment validity | RETAINED_IN_EVOLVED_FORM | Stress scenarios are plausible and not merely convenient; deployment monitoring can detect uncovered shifts. | Repeated public benchmark tuning; no fresh collection; adversarial examples counted as prevalence; aggregate shift hides subgroup collapse. |
| P050 | Keep mean performance, variability, tail behaviour, reliability over time and model robustness as separate claims | STRONGLY_RETAINED | Dimensions are not falsely treated as independent; composite utility, if used, is explicit and decision-owned. | Mean-only benchmark; variance ignored; uptime without severity; composite weights changed; tail based on one anecdote. |
| P051 | Treat optimised metrics as vulnerable proxies and monitor for gaming/surrogation | USEFUL_BUT_EASILY_GAMED | A plausible behavioural/optimisation mechanism links targeting to metric degradation; independent checks are not co-optimised. | Dropping hard cases; changing denominator; teaching to test; benchmark leakage; proxy chosen for availability; outcome not independently checked. |
| P052 | Require independent, prospective justification before changing an evaluator, fixture, expected answer or threshold after failure | STRONGLY_RETAINED | The bridge can distinguish measurement defect from candidate defect; updated rule better represents the underlying construct. | Changing expected output after seeing candidate; threshold chosen to include current score; deleting failed case; no old/new bridge; circular validation. |
| P053 | Separate candidate/process variation from evaluator/measurement variation before assigning corrective action | STRONGLY_RETAINED | Variance components/interactions are estimable enough to discriminate source or else conclusion remains unresolved. | Only rerunning candidate; only checking easy references; evaluator and candidate changed together; no interaction analysis; regression to mean. |
| P054 | Protect holdouts, reproduce analyses and prevent adaptive evaluation reuse from masquerading as fresh evidence | RETAINED_IN_EVOLVED_FORM | Protected sample remains sufficiently independent; reusable-holdout privacy/model conditions or fresh-data assumptions hold. | Calling same holdout reruns “replications”; public test labels; leaderboard tuning; analysis not executable; fresh test collected differently. |
| P055 | Check model adequacy and misspecification against the decision, not through ritual assumption tests | ASSUMPTION_SENSITIVE | Diagnostics have power for material deviations; alternative models are plausible and not chosen only for desired results. | Mandatory Shapiro–Wilk; accepting model because p>.05; residuals not time-ordered; transformation after seeing desired significance; no out-of-sample check. |
| P057 | Make measurement and controls economically proportional; retire, revalidate or recalibrate stale controls | CONTEXT_DEPENDENT | Past yield predicts some future value or scenario analysis captures uncertainty; retirement does not violate unmodelled catastrophic safeguards. | Quota retained with no consumer; threshold never revalidated; duplicated tests treated as corroboration; control removed because it catches failures. |

## PROXY_GAMING_RISKS

- Optimising the score while the intended property is unchanged or worsens (Goodhart/Campbell mechanism).
- Selective exclusion, denominator/opportunity redefinition or relabelling of failures.
- Post-hoc subgroup, endpoint, expected-answer or threshold changes after candidate exposure.
- Benchmark/test-set contamination or repeated adaptive reuse without protected validation.
- Evaluator redesign until a failing candidate passes, without independent reference evidence.
- Silent evaluator/threshold version drift that preserves numeric precision but changes meaning.
- Shared training/reference data causing candidate and evaluator to agree through common bias.
- Composite metrics hiding severity, tails or non-substitutable system outcomes.
- Metric portfolios becoming a larger gaming and bureaucracy surface rather than a validity check.

## RARE_EVENT_OR_HIGH_RELIABILITY_LIMITS

- Zero observed failures imply a one-sided bound conditional on exposure, independence and opportunity definition—not zero risk (P047).
- Finite samples carry little direct information about probabilities many orders of magnitude below 1/n without mechanistic/structural assumptions (P047–P048).
- Accelerated tests can change the dominant failure mechanism and make use-condition extrapolation invalid (P045).
- Censoring, competing risks, repair, degradation thresholds and changing field populations must be modelled (P044–P046).
- Mean performance and ordinary confidence intervals do not establish extreme quantiles or catastrophic loss (P048, P050).
- Rare-event control charts require correct opportunity/exposure and overdispersion/dependence treatment (P024).
- Distribution shift can dominate nominal reliability even when the fitted model is internally precise (P049).
- For very-high-reliability claims, test evidence usually must be combined with physics, design assurance, stress evidence and field surveillance (P044–P049).

## UNRESOLVED_PROPERTIES

No final property has `CURRENT_STATUS: UNRESOLVED`; all 65 candidates are dispositioned. The following bounded questions remain unresolved and must not be converted into silent assumptions:

| ID | Question | Family | Properties | Evidence limit |
| --- | --- | --- | --- | --- |
| OQ01 | How can evaluator fitness be established for generative or partly subjective systems when no stable gold standard exists? | Measurement/evaluator validity | P001–P011, P052–P054 | UNRESOLVED: triangulation and bridge designs help, but construct authority remains external. |
| OQ02 | What is an adequate independence model for stochastic software/agents sharing training data, code, prompts and evaluators? | Replication/dependence | P016, P032, P063 | UNRESOLVED: hierarchical/common-source models are plausible but empirical dependence is often hidden. |
| OQ03 | How should co-adaptive candidate and evaluator changes preserve sequential validity? | Sequential evidence | P038, P052–P054 | UNRESOLVED: classical anytime-valid guarantees generally assume a fixed target/outcome process or controlled adaptation. |
| OQ04 | What evidence justifies changing expected answers when the construct itself evolves? | Construct/evaluator mutation | P001, P009–P010, P052 | UNRESOLVED: independent authority and old/new bridge are necessary but may not identify one correct construct. |
| OQ05 | How much fresh confirmation is necessary after highly adaptive optimisation? | Adaptive experimentation | P035, P037–P038, P054 | CONTESTED/DOMAIN_SPECIFIC. |
| OQ06 | How can rare catastrophic rates be bounded when direct samples are infeasible and stress models are uncertain? | Reliability/tails | P045, P047–P049 | UNRESOLVED: requires combined mechanistic, stress, operational and conservative evidence without false numerical synthesis. |
| OQ07 | When does a local dynamic baseline provide enough “stability” for useful capability in adaptive systems? | Nonstationarity/capability | P018–P024 | CONTESTED and model-dependent. |
| OQ08 | How should value-of-information models incorporate deep uncertainty, irreversibility and discovery option value? | Evidence economy | P041, P048, P057 | UNRESOLVED: expected utility alone may be inadequate. |
| OQ09 | How can reference sets be refreshed without losing longitudinal comparability or becoming optimisation targets? | Reference governance | P010–P011, P049, P054 | UNRESOLVED: overlapping bridge panels and protected access are partial solutions. |
| OQ10 | What monitoring designs work reliably for low-volume, high-mix and rapidly changing software/knowledge work? | Domain transfer | P022–P024 | EVIDENCE LIMITED: strong general cautions, heterogeneous direct evidence. |
| OQ11 | Which Six Sigma organisational practices have causal benefits independent of leadership, selection and resources? | Programme effects | P056, P061–P062 | UNRESOLVED/MIXED: positive observational studies coexist with weak/heterogeneous reviews. |
| OQ12 | Which Taguchi-specific criteria remain optimal for clearly defined loss and mean–variance relationships? | Robust design | P043, P065 | CONTEXT_DEPENDENT: universal claims rejected, some special cases retained. |
| OQ13 | How should multiple non-substitutable metrics be governed without creating multiplicity and dashboard bureaucracy? | Proxy/system metrics | P037, P050–P051, P057 | UNRESOLVED organisational/statistical design problem. |
| OQ14 | When can mechanistic evidence substitute for independent system-level replication? | Evidence synthesis | P032, P040, P042, P047–P048 | DOMAIN_SPECIFIC and consequence-sensitive. |
| OQ15 | How should stale-control retirement be distinguished from gaming away inconvenient tests? | Control lifecycle | P052, P057 | Requires independent risk authority and alternate-coverage evidence; no universal statistic. |
| OQ16 | How should measurement uncertainty include learned-evaluator retraining and model-selection uncertainty without false precision? | Measurement uncertainty | P007, P010, P052–P055 | UNRESOLVED; conventional budgets often underrepresent structural uncertainty. |
| OQ17 | What is the right unit of evidence when interventions alter shared system state for all subsequent units? | Interference/carryover | P014, P030–P032, P039 | Requires explicit exposure mapping; often domain-specific. |
| OQ18 | Can statistical engineering be empirically distinguished from excellent systems engineering that uses statistics? | Discipline identity | P056 | UNRESOLVED; component mechanisms are much better evidenced than unique discipline-wide effect. |
| OQ19 | How should practical significance combine average benefit, tail harm and distributional fairness? | Decision thresholds | P036, P048, P050 | Partly normative; no universal scalar. |
| OQ20 | What evidence is enough to call a deterministic discriminator complete and authoritative in an evolving system? | Deterministic precedence | P042, P052, P057 | UNRESOLVED governance boundary; identity, scope and staleness must be re-established. |

## Audit-question set spanning the corpus

- Does the target system distinguish candidate/process variation from evaluator/measurement variation before changing the candidate?
- When repeated tests are run, what establishes that the repetitions are independently informative rather than correlated re-measurements?
- Are thresholds/specifications being confused with statistical control or process capability?
- Can an evaluator, fixture, reference or threshold be changed after failure without independent justification against the underlying property?
- Is another measurement, review or experiment actually expected to change the next engineering decision?
- Is a deterministic authoritative discriminator available that should make statistical machinery unnecessary?
- Are randomisation, blocking, replication and experimental units defined at the level where causal contrast is claimed?
- Are multiplicity, repeated looks, subgroup selection and analyst/evaluator adaptivity included in the error or decision boundary?
- Could a statistically stable or significant result still be incapable, practically irrelevant, invalid across contexts or dominated by tail risk?
- What event, drift evidence or consequence change would legitimately recalibrate or retire the control?

## Intake completion state

```text
EVOLVED_STATISTICAL_ENGINEERING_AUDIT_INTAKE: COMPLETE
PROPERTY_POPULATION_TOTAL: 65
PROPERTY_POPULATION_EXAMINED: 65
PROPERTY_COVERAGE: 65/65
```