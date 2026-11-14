# DRF-L2 — Reliability and Maintainability Engineering

> **Current scientific account — 13 November 2026.** This derived account explains the original qualified constituent study. Earlier private-disclosure or review-pending wording belongs to its recorded source cutoff. The scientific predicates, guards, negative results and uncertainty below retain their original scope.

[Family overview](README.md) · [Original qualification and review identities](QUALIFICATION_AND_REVIEW_BINDINGS.json) · [Scientific source catalogue](SOURCE_MAP.md)



## 1. Required function is the organizing object

Reliability concerns a declared function under conditions over a mission, interval or demand population. Maintainability concerns restoring that function under specified maintenance conditions; supportability concerns whether the required tools, resources, skills and authority are available. The discipline connects prevention, detection, containment, degradation, repair and replacement without treating them as one predicate.

A success event can be written S(X,C,E,D): a bearer X supplies the required function for consumer C in environment/profile E over interval or demand D. Defining that event makes a probability meaningful; it does not measure it or determine the consumer's values. A binary local function can be legitimate. An internal restore may satisfy its byte and invariant postconditions while credentials or counterparties needed for a larger transaction remain absent. Both the local truth and wider incompleteness must survive.

The lineage retains 55 historical identities, 85 historical source records, 40 native fields per property, six profile families and ten evidence partitions. The public August population and the accepted November current propositions remain different layers. Native ERM-P001–P040 received detailed audit treatment; ERM-P041–P055 had a bounded table. All 55 belong in both historical and current readers, and the native records have no CROSSWALK_WORTHY Boolean to fabricate. Counts establish coverage of identities, not realized reliability. [Report introduction and §§4–5](SOURCE_MAP.md#s-734dd662fb85249e), [current reader](DRF-L2-PROPERTIES.json).

## 2. A plural genealogy, with unresolved origins left unresolved

Nine strands are needed to represent the accepted genealogy: life-data statistics; institutional electronics reliability; mechanical maintenance; repairable-system processes; failure analysis; fault-tolerant computing; software reliability; diagnostic/PHM inference; and continuing service reliability. Their problems overlap, but their bearers and evidence differ. A software restart is not physical renewal merely because both can restore function. Software Reliability Engineering and Site Reliability Engineering also share an acronym without establishing ancestry.

The 20 typed edges distinguish documentary uptake, criticism, mathematical relationship, domain translation and analogy. Randell's recovery-block account explicitly identifies earlier recovery structure. NASA's later guide documents uptake of Nowlan–Heap; that is not a fresh reading of the original 1978 report. Knight–Leveson's multiversion evidence challenges an independence assumption without disproving all useful diversity. The 1949 FMECA attribution remains unresolved because the accessed owner metadata labels the date as cancellation and has an anomalous classification; no invented priority claim fills the missing original.

The historical native material, r1 study, material r1 adverse review and corrected r2 form a second, documentary genealogy. R2 restores live spare service capacity/headroom to tension T-09 after replacement-parts logistics displaced it. It preserves the valid supportability discussion in C020 and capacity argument in C036. It also reconciles cumulative F014/F018 access and corrects a configuration-count sentence. Those changes do not create a fresh r2 external-source reading or case execution. [Report §§1–3,23](SOURCE_MAP.md#s-734dd662fb85249e), [genealogy](records/S-d6ec151b928f5142-DRF-L2-GENEALOGY.json), [correction record](SOURCE_MAP.md#s-af980aef2b4d6e51).

## 3. Reliability, availability and process models

For a nonrepairable item, R(t)=P(T>t) is a survival probability with a specified failure event. Point availability, observed interval availability and a long-run up-time fraction are different quantities. A high mean or high availability can conceal an unacceptable interruption pattern. C01's two stipulated histories both have 99% observed availability, but one has many short interruptions and the other a single long outage. No consumer tolerance follows from that equality.

Under finite-mean regenerative cycles, a long-run up-time fraction can be E[U]/(E[U]+E[D]). This is broader than a two-state exponential model and is not automatically convergence of point availability. Within-cycle dependence need not defeat the ratio, while nonregeneration, infinite means or changing operation can. Definitions matter: adding repair time twice because MTBF already contains a full calendar cycle is an accounting error. Using hands-on repair time while omitting logistics, diagnosis and validation can miss the operational denominator; overlapping delays require an interval or critical-path account.

Lifetime hazard, recurring-event intensity, failures per demand and reported-incident counts are distinct. Independent censoring in the accepted exponential example retains the censored unit's exposure; discarding it changes the estimate. An exactly fitted mean curve also does not identify a process. The constructed N(t)=floor(√t+U), with U uniform on [0,1), has mean √t but deterministic N(4)=2. An NHPP of mean two has variance two. The countermodel defeats the inference from a power-law mean to an NHPP while leaving appropriately conditional modeling useful.

These arguments separate parameter, model, transfer and observation uncertainty. More observations can reduce one without resolving the others. A precise model remains valid within its premises even when field correspondence is weak. [Report §§5–8,19](SOURCE_MAP.md#s-734dd662fb85249e), [recorded cases C01,C06,C08,C13](SOURCE_MAP.md#s-3a4918109a517475).

## 4. Redundancy under dependence

For ideal OR success events A and B, with no new interaction or control failure,

\[
P(A\cup B)=P(A)+P(B\cap\neg A).
\]

The added path benefits the model exactly when it rescues a positive-probability part of A's failure set. Statistical independence is unnecessary for this identity. It is needed for the familiar product shortcut for joint failure.

C02 makes the distinction concrete: both paths succeed with probability .89, only each individual path succeeds with .01, and both fail with .09. Each alone succeeds .90; the pair succeeds .91 despite positive dependence. The independence shortcut would incorrectly produce .99. Add an independently successful .95 serial controller and the example architecture falls to .8645, worse than the initial .90. The benefit of a rescue path and the burden of a changed architecture must therefore be assessed separately.

Common causes, dormant faults, state compatibility, transfer behavior, capacity and maintenance can all change those premises. Different teams or power supplies do not logically establish independence. Conversely, treating all copies as one failure domain can be a conservative decision bound without being an observed fact. Native P009's common-cause discussion remains valid; the current clarification rejects only the strict interpretation that every benefit requires statistical independence. Its multiplication-like list is not retroactively labeled a numerical formula.

The 27 versions in Knight–Leveson's selected application experiment are not 27 independent domain replications. The result is consequential for its tested assumption, with its reference/oracle and population limits preserved. A simpler single system with competent repair, a manual spare, or a restricted mission can remain an adequate alternative. [Report §9](SOURCE_MAP.md#s-734dd662fb85249e), [current C008–C009 and C040–C051 records](DRF-L2-PROPERTIES.json).

## 5. Detection, diagnosis, action and restoration

The denominator is part of a coverage claim. In C03's stipulated population, 60 of 100 fault opportunities are signaled and 99 of 9,900 healthy opportunities produce alarms. Detection coverage is .60; the false-alarm rate is .01; the positive predictive value is 60/159. Exact isolation, containment and restoration have different numerators and conditioning sets. Unrecovered true detections do not disappear from detection coverage merely because recovery failed.

An informative signal also need not justify automatic action. The case's stipulated action losses make one automatic policy harmful while a specified confirming inspection is useful. Those assumed values are not field estimates. Native P012 already allowed ambiguity groups and symptom-directed remedies; the accepted correction clarifies recovery versus detection denominators rather than rejecting the entire native diagnostic argument.

Restoration closes the asserted postcondition. A restart, retry, rollback, backup restore and reconstitution have different guards. A bounded internal success can coexist with missing external state or unresolved root cause. Waiting for complete causal knowledge can be unnecessary when a supported symptom-level remedy exists; declaring a whole mission restored from a successful command is too strong.

Even a recovery acceptance test needs the right strength. C14's order-and-sum check accepts [0,3,3] for input [1,2,3], although the intended permutation property fails. A stronger check may be necessary, or the claim must remain explicitly weaker. The lesson preserves cheap adequate checks and rejects the promotion of a cheap inadequate one. [Report §§10–13](SOURCE_MAP.md#s-734dd662fb85249e), [recorded cases C03,C04,C14](SOURCE_MAP.md#s-3a4918109a517475).

## 6. Capacity, maintenance and useful evidence

Live service headroom is not spare-parts inventory. T-09 concerns usable capacity against current demand, bursts, correlated failover, retries, restarts and backlog replay, balanced against cost, energy, efficiency and consumer harm. C020's logistics concern addresses restoration waiting. A reserve lost through the same dependency is not available protection. Manual shedding, staged recovery, tolerated delay or justified no change may be appropriate; the accepted account establishes no universal reserve percentage.

C10's fluid example has capacity 100 and incoming work 90. One additional attempt for 20% of requests makes offered work 108. The constant-rate model cannot drain under that load. It does not prove that every later retry is harmful after conditions change, and the rejected reviewer equality-backlog objection remains an adjudicated nonfinding, not a hidden defect.

Maintenance policies similarly depend on mechanism and consequence. Under the accepted renewal assumptions and stipulated costs, age replacement can lose against run-to-failure in the exponential example and win for the selected Weibull example. Neither interval is a universal optimum. Prediction adds a further interface: a useful forecast needs a viable intervention window, support and action whose false positives and costs are acceptable. Intervention changes later observations and censoring, so predictive accuracy alone does not establish policy utility.

Failure-free observations require their sampling model. The accepted zero-event HPP and Bernoulli bounds are conditional confidence procedures, not posterior probabilities or zero risk. Accelerating two competing failure modes by different factors also defeats division of the total by one mode's factor. A fitted growth curve does not establish causal repair, and a closed failure ticket does not establish recurrence reduction. Existing valid tests or a focused deterministic correction may suffice for a narrower question. [Report §§12,14–16,23](SOURCE_MAP.md#s-734dd662fb85249e).

## 7. Directions, configurations and removal tests

The accepted within-lineage register selects thirteen unordered pairs and separately examines both directions: 26 directions out of the 2,970 possible non-self directions. The remaining 2,944 are unexamined as pairs, not rejected. The [complete composition records](records/S-5aa201881c05d02b-DRF-L2-COMPOSITION.json) retains all original directions and fields.

| Selected relationship | Receiving use | Independent reverse or limit |
|---|---|---|
| Mission → demonstration | Defines the failure event, exposure and intended denominator. | Observations can expose an omitted consequential state; they cannot determine stakeholder values or repair unrepresentative sampling. |
| Common cause → redundancy | Constrains the joint law and changes the protection claim. | Cofailure evidence can inform investigation, but correlation does not by itself identify a causal mechanism. |
| Detection → containment | A signal can enable a supported safe action over the remaining ambiguity. | Manual restoration can occur without that detector; detection alone proves no safe action. |
| Restoration → diagnosis | Preserved before/after evidence can distinguish competing hypotheses. | A successful restart alone does not establish a cause. |

Four whole configurations compare direct check/rebuild; a simpler system with repair/support; supported redundant continuity; and stateful service with bounded degradation and staged restoration. Each has its own mission, incompatibility, cumulative cost and retirement conditions. Removing detection from one automatic containment route removes that route, while removing it from an independent manual restore need not defeat restoration. Removing a profile from a statistical demonstration loses its intended population interpretation; adding a duplicate record does not create new protection.

Five removal/subsumption tests admit zero new general property identities. The combinations are useful realizations of existing predicates, not an indivisible universal maturity bundle. A bijective reencoding of the same conditions changes no outcome. These native constituent configurations must not be labeled the later accepted DRF family synthesis. [Composition](records/S-5aa201881c05d02b-DRF-L2-COMPOSITION.json), [Report §§22–24](SOURCE_MAP.md#s-734dd662fb85249e).

## 8. Negatives, frontier and evidence limits

The negative population remains complete: six ceremonial universal inferences and eight rejected universal claims occupy P041–P054; P055 is a domain-bounded AI/ML mechanism. MTBF, nines, filled FMEA, handbook prediction, green health, backup existence, one exercise and incident counts are not universal proof. Their valid bounded uses remain available. More redundancy need not help, predictive maintenance need not beat simpler policies, and zero observed failures need not mean zero probability.

Modern operator accounts supply event-specific mechanisms, not independently verified prevalence or effects of promised remedies. The chaos paper and its dataset metadata share one study. NIST handbook pages, NRC chapters and Google guidance are not independent replications merely because they have separate citations. The CrowdStrike account expressly distinguishes the implicated content from AI. Workshop, abstract, paid-clause and selected-passage access limits remain attached to the actual source.

The fourteen authored constructions are finite analytical evidence. R2 added no new scientific execution. The prior failed 205-payload candidate, erroneous SRC048 expectation, source failures and subsequent correction remain preserved. The final qualification accepts the complete corrected subject with no open material or nonblocking findings; it does not erase this history.

Current unknowns include sparse common-cause inference, intervention-dependent data, heterogeneous consumer effects, evidence inheritance after change and full lifecycle comparisons. The original executed prompt binding remains UNKNOWN; no failure of an unverified historical contract is invented. [Qualification](SOURCE_MAP.md#s-18fb9309de1e93eb), [Report §§17–29](SOURCE_MAP.md#s-734dd662fb85249e).


## Prospective engineering use

The current findings can help a future consumer compare an actual mechanism with an actual required function. Existing adequate controls, a partial contribution, a research question or no change are legitimate outcomes. The existing responsibility route is R0031/#201. The [existing owner map](../OWNER_MAP.json) and [preliminary responsibility outlines](../RLGWO_OUTLINES.md) preserve the relevant shared owners; they do not establish a present implementation defect, appoint a new owner or qualify native behavior.

R0031/#201 was closed at its historical v0.4 scope. That receipt does not assess these later scientific propositions or a new target configuration.

## Complete public scientific records

The [complete property records](DRF-L2-PROPERTIES.json) retain all historical/current fields, current claims and their conditions. The maintained public page also provides an expandable complete current reader. Composition, genealogy, cases and source registers are available through the [source catalogue](SOURCE_MAP.md).
