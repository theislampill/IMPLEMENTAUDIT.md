# EVOLVED_STATISTICAL_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

## Source-grounded explanation

Statistical reasoning entered engineering through several distinct but interacting traditions. Bell Labs work used statistical control and acceptance sampling to make economically defensible decisions under manufacturing variation; Fisherian design developed randomisation, blocking, replication and factorial experimentation; metrology formalised measurands, calibration, traceability and uncertainty; and reliability/robust-design practice addressed lifetime, stress, degradation and nuisance sensitivity. Later statistical engineering describes the system-level combination of methods and subject knowledge for complex problems. Six Sigma is one later management-programme translation of earlier quality and statistical tools, not the origin or definition of the whole tradition. [S001–S015, S051–S081, S082–S096]

After criticism and modern extension, the defensible core is not “more statistics.” It is evidence proportional to a decision: define what is being measured; establish that the measurement/evaluator can discriminate the relevant states; model variation, dependence and drift enough to avoid reacting to noise; design the smallest informative causal or design contrast; preserve multiplicity and stopping boundaries; separate mean, variability, tails, time reliability and context robustness; and prevent metric/evaluator mutation from manufacturing a pass. Formal tools are omitted when a cheaper authoritative deterministic discriminator already settles the decision. [S015–S042, S061–S078, S097–S110]

## Strongest surviving engineering properties suitable for public explanation

| ID | Property | Public explanation | Sources |
| --- | --- | --- | --- |
| P001 | Define the decision-relevant measurand or construct before quantification | No metric governs until its intended property, scope, consumer, and admissible interpretation are fixed enough to be challenged. | S052, S055, S056 |
| P002 | Establish measurement-system fitness before metric governance | Demonstrate enough discrimination for the intended decision, not abstract “good measurement,” and recheck after material evaluator change. | S015, S055, S058 |
| P004 | Keep bias/accuracy distinct from precision | Decision-specific decomposition of systematic and random error, with correction only when validated. | S015, S052, S057 |
| P005 | Distinguish repeatability, reproducibility and validity | Claim only the level of stability actually tested, and never infer validity from repeatability alone. | S057, S058, S059 |
| P007 | Carry measurement uncertainty into engineering decisions | Use proportionate uncertainty analysis sufficient to show whether the next action is discriminated. | S051, S053, S100 |
| P010 | Monitor evaluator/instrument drift and require independent recalibration evidence | Recalibrate when independent evidence shows measurement defect or context change; preserve old/new bridge and re-evaluate prior conclusions where material. | S015, S060, S056 |
| P012 | Preserve data provenance, preprocessing, version and lineage | Preserve the minimum complete lineage needed to reconstruct the evidence and its dependence structure. | S056, S038, S110 |
| P015 | Discriminate routine/common variation from evidence of a changed process | Use the lightest calibrated discriminator that separates expected variation from actionable change, then require causal investigation before intervention. | S001, S002, S003 |
| P017 | Keep statistical control limits separate from engineering specifications and tolerances | Use control limits for change detection, specifications for requirements, and guard bands/decision rules for uncertain conformance. | S001, S053, S062 |
| P020 | Prevent tampering and overadjustment to routine variation | No reactive adjustment without a discriminator or planned experiment whose expected value exceeds intervention risk. | S002, S003, S089 |
| P025 | Design sampling to represent the decision population and selection process | Use the cheapest design that either represents the target or honestly limits the claim; retain all attempted-unit provenance. | S045, S020, S068 |
| P030 | Use randomisation to protect causal comparisons against assignment bias and support valid error assessment | Randomise when it materially reduces causal ambiguity; preserve assignment integrity and analyse the design actually run. | S005, S006, S018 |
| P032 | Require independent replication at the experimental-unit level; treat technical repeats as measurement information | Count independent decision-relevant units, disclose dependence, and stop treating correlated reruns as corroboration. | S005, S006, S023 |
| P036 | Report effect magnitude, uncertainty and engineering significance; use equivalence/noninferiority when “no important difference” is the decision | Show effect, uncertainty, smallest consequential magnitude, and decision; reserve “equivalent” for designs that test a justified margin. | S007, S029, S041 |
| P038 | Plan sequential evidence and stopping so repeated looks do not manufacture confidence | Another observation is justified only when it is expected to change the decision and the stopping/error framework remains valid. | S011, S012, S036, S037 |

## Famous caricatures and ceremonies not to present as the property itself

- Statistics is just a significance test.
- SPC means putting every metric on a control chart.
- Six Sigma is the universal 3.4-defects-per-million rule.
- More samples or repeated green tests automatically mean more truth.
- A precise or repeatable metric is necessarily accurate and valid.
- A process inside specification is statistically controlled.
- A statistically significant difference is automatically engineering-significant.
- Randomisation and replication repair every validity, measurement and transfer problem.
- DMAIC/DMADV phase names and belt credentials are the underlying statistical property.
- A fixed Taguchi S/N ratio or orthogonal-array recipe is synonymous with robust design.

## Important criticisms and limits

- Control limits can be badly calibrated under autocorrelation, mixtures, seasonality or nonstationarity.
- Measurement error can hide shifts or make evaluator variation look like process variation.
- Control signals do not prove a causal mechanism and can become blame or surveillance instruments.
- Capability indices are misleading for unstable, poorly measured or misspecified processes.
- P-value thresholds omit effect magnitude, uncertainty, multiplicity, stopping and consequence.
- Repeated observations can be pseudoreplication when units, seeds, batches, sites or evaluators are shared.
- Gauge studies and normality tests can become ritual when unrelated to the decision margin.
- Zero failures and accelerated tests can support extreme overconfidence when mechanisms/exposure are weak.
- Metrics and benchmarks can be gamed, contaminated or redefined after failure.
- Branded programme performance evidence is more confounded and heterogeneous than the formal evidence for component methods.

## What evolved

The tradition evolved by separating properties that early or later programmes often collapsed: control from specification compliance; stability from capability; bias from precision; repeatability from reproducibility and validity; independent replication from repeated observation; significance from engineering consequence; fixed-horizon from planned sequential inference; local fit from transfer; average performance from tails and lifetime; and metric improvement from construct improvement. Classical tools were preserved where their assumptions and decision roles remain sound, specialised for dependence/nonstationarity/rare events, or narrowed when they became recipes. Taguchi’s robustness aim survives more strongly than universal S/N recipes; Six Sigma’s structured coordination can survive without belt/tollgate ceremony; and adaptive evaluation now requires protected data, versioned evaluators and explicit drift/contamination controls.

## Citation-ready factual claims

| Claim ID | Claim | Durable source IDs |
| --- | --- | --- |
| C01 | Shewhart’s 1926 paper and 1931 book established industrial control-chart/economic-control reasoning around variation rather than mere conformance inspection. | S001, S002 |
| C02 | Fisher’s 1926 and 1935 work made randomisation, replication, local control/blocking and factorial arrangement central to valid efficient experiments. | S005, S006 |
| C03 | Neyman–Pearson testing explicitly treats alternatives and error probabilities; it does not itself determine engineering consequence or practical importance. | S007 |
| C04 | Dodge–Romig acceptance sampling governs lot decisions under producer/consumer risk; it is not evidence of process stability or causal improvement. | S008, S068–S070 |
| C05 | Box–Wilson response-surface work framed optimisation as sequential experimentation with local models rather than a single final test. | S009 |
| C06 | Modern metrology distinguishes the measurand, calibration/traceability, bias, precision and measurement uncertainty; traceability alone is not fitness for purpose. | S015, S051–S057 |
| C07 | Measurement error can materially impair control-chart shift detection, so process monitoring depends on evaluator capability. | S032 |
| C08 | Control limits, specification limits and capability answer different questions; capability requires qualified stability/model and measurement conditions. | S061–S064, S109 |
| C09 | Autocorrelation and nonstationarity require time-series, residual, local-regime or specialised monitoring rather than blind classical limits. | S026, S030–S031, S067 |
| C10 | A p-value does not measure effect importance or hypothesis truth, and a non-significant result does not establish equivalence. | S029, S033–S035, S041–S042 |
| C11 | Planned sequential tests, confidence sequences and always-valid methods can support repeated looks under stated conditions; ordinary optional stopping remains invalid. | S011–S012, S036–S037 |
| C12 | Adaptive reuse of a holdout can invalidate ordinary guarantees; reusable/protected validation and fresh data are evolved responses. | S038–S039 |
| C13 | Zero observed failures imply a finite upper confidence bound conditional on exposure and assumptions—not perfect reliability. | S073, S075 |
| C14 | Taguchi’s noise-factor/robust-design contribution survives, while universal S/N criteria and recipe arrays were substantially criticised and narrowed. | S025, S094–S096, S102 |
| C15 | Six Sigma is an organisational/problem-solving programme that recombines earlier quality/statistical tools; causal evidence for programme-wide effects is context-dependent. | S082–S087 |
| C16 | Goodhart/Campbell-style effects explain why a metric can lose evidential value when it becomes a high-stakes optimisation target. | S019, S022, S097 |
| C17 | Information-value reasoning supports buying another measurement only when it can improve the decision enough to justify its cost. | S014, S098 |
| C18 | Current statistical engineering is described as system-level integration of statistical and domain knowledge, not one fixed toolkit. | S079–S081 |

## Explicit evidence limits and claims that must not be made

- Do not claim that one historical school formally called “Evolved Statistical Engineering” exists.
- Do not claim that statistical engineering is a synonym for Six Sigma, SPC, DOE or a software tool menu.
- Do not claim that every control-chart signal identifies a cause, or that no signal establishes no defect.
- Do not claim that calibration/traceability, repeatability, agreement or narrow uncertainty alone establish construct validity.
- Do not claim that randomisation, replication or a held-out set solves measurement error, interference, missingness, drift or external validity automatically.
- Do not claim that p-values are universally useless; reject threshold ritual while preserving conditional inferential use.
- Do not claim that Six Sigma programme effects are universally causal or that all observed benefits arise from statistical tools.
- Do not claim that zero failures prove zero risk or that accelerated testing automatically preserves use-condition failure mechanisms.
- Do not claim that every reliability, manufacturing or metrology property transfers unchanged to software, machine learning or agent systems.
- Do not claim that more measurements always add information or that formal statistics should displace an authoritative deterministic discriminator.

## Suggested public page outline

- 1. What statistical engineering is—and is not
- 2. Multiple historical lineages: control, sampling, experimentation, metrology, reliability and programme translation
- 3. Measurement before measurement-based governance
- 4. Variation, stability, capability and specifications
- 5. Designed experiments and causal discrimination
- 6. Repeated evidence, dependence and stopping
- 7. Robustness, reliability and tail humility
- 8. Metrics, evaluator drift and proxy capture
- 9. What survives after stripping Six Sigma/statistical ceremony
- 10. Evidence limits and domain-transfer cautions
- 11. Sources and claim-level locators

## Direct lineage versus convergence/analogy

Use direct-lineage language only where documentary transmission exists—for example Shewhart control-chart descendants, Dodge–Romig acceptance sampling, Fisherian DOE, Wald sequential analysis, GUM/VIM metrology, or Taguchi robust-design debate. Goodhart/Campbell metric effects, reusable holdouts, dataset-shift work and stochastic software evaluation are convergent or modern domain translations unless a specific transmission path is documented. Similarity of vocabulary or function is not historical descent.

## Intake state

```text
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
CITATION_READY_CLAIMS: 18
PUBLIC_PROPERTIES: 15
```