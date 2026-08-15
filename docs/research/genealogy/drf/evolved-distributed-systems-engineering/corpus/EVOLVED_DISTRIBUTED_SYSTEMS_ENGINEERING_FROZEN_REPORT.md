# EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING — FROZEN EXTERNAL RESEARCH REPORT

**Analytical label:** `EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING`  
**Run and access date:** 2026-08-12  
**Research state:** `FROZEN`  
**Property denominator:** 54 examined / 54 total  
**Source table:** 102 records  
**Informational-independence boundary:** no repository and no sibling Evolved-* report or frozen packet was inspected or relied upon.

## Scope and non-claim

`EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING` is an analytical construct, not a claim that one historical school used this name. The report traces plural lineages—causality and time, replication and consistency, consensus and membership, distributed transactions, message delivery, fault tolerance, distributed databases, event logs/streaming, workflow orchestration, overload/service resilience and cloud/domain translations—and extracts only the engineering properties that survive criticism, failure evidence and assumption analysis.

The source corpus deliberately separates formal correctness under a model from deployment evidence. A theorem, protocol proof, standard, product feature or demonstration establishes only its stated boundary. Operational transfer additionally requires the actual membership, storage, clocks, network, configuration, external effects, recovery path and observability to satisfy that boundary.

## Executive synthesis

The evidence supports the proposed hypothesis with three important tightenings.

First, mature distributed-systems engineering begins not with microservices, consensus or cloud topology, but with **partial failure and epistemic uncertainty**. A remote timeout does not establish nonexecution; a live component does not establish useful service; a timestamp does not establish causal order; and a majority does not establish current membership or semantic truth. These are not rhetorical cautions: they follow from foundational communication, causality, impossibility, failure-detector, transaction and recovery results, and they recur in production incidents. [S003], [S006]–[S008], [S017], [S043], [S044], [S073]–[S076], [S102].

Second, the strongest surviving properties are **boundary- and assumption-bound**. Strong coordination pays when independent valid operations can jointly violate a non-compensatable invariant. Coordination avoidance pays when operations are commutative, partitionable, escrow-bounded or invariant-confluent. Exactly-once processing is defensible inside a closed runtime/transaction boundary; business-effect uniqueness still needs semantic identity, idempotency, fencing, transaction participation or compensation. Durable workflow state survives orchestrator failure; it does not make an external system deterministic or current. [S019], [S030], [S036], [S038]–[S043], [S046], [S049]–[S056].

Third, modern operational evidence adds a **capacity and recovery-stability layer** that protocol folklore often omits. Queues do not manufacture throughput, retries consume shared capacity, failover can double load, repair can propagate corruption, and positive-feedback loops can sustain failure after the initiating fault disappears. Current authority must be re-established and fenced before mutation; restore must be exercised at realistic scale and reconciled with external effects; telemetry must report its own missingness. [S062]–[S069], [S073]–[S076], [S083], [S088]–[S091].

The resulting candidate description is:

> **An engineering discipline that assumes partial failure and uncertain timing; makes causal order, currentness, consistency, membership, authority, delivery and recovery contracts explicit; binds retry, re-dispatch and failover to semantic identity, fencing, idempotency, transactional closure or compensation; controls finite queues, backpressure and overload feedback; persists enough work state to recover without silently duplicating effects; re-establishes current authority and external postconditions after failure; and uses distribution and strong coordination only where a named invariant, failure-domain, latency, scale, ownership or lifecycle consumer warrants their cost.**

This is not “make everything a microservice and add consensus.” It is closer to **eliminating accidental distributed problems, then governing the unavoidable ones**.

## Research protocol, source standard and stop rule

Search proceeded by plural lineage and by adversarial burden rather than by famous-system list. It covered foundational primary papers; formal results and algorithms; distributed database/stream/workflow systems; current 2024–2026 transaction, overload, workflow, observability, integrity and fault-reproduction work; authoritative implementation documentation only for exact behaviour; serious technical criticism; and incident postmortems. Sources were admitted only when they could change a property, assumption, trigger, cheap path, criticism or current-frontier conclusion.

The saturation stop rule was met when repeated searches across the major lineages and criticism families produced either:

1. a source already represented by an admitted property and assumption boundary;
2. a new implementation of an existing property without a new general mechanism;
3. a domain translation marked as such; or
4. an unresolved question that no located evidence could close.

The frozen denominator includes retained, context-dependent, assumption-sensitive, ceremonial, rejected, superseded, domain-specific and unresolved candidates. No failed candidate was silently deleted.

## Epistemic labels

- `SOURCE_ESTABLISHED`: the source directly states or demonstrates the cited proposition.
- `SOURCE_INTERPRETATION`: the report interprets a source-established result across the corpus.
- `FORMAL_OR_THEORETICAL_RESULT`: true under the formal model; deployment preconditions remain separate.
- `EMPIRICAL_OR_DOMAIN_FINDING`: measured/observed within a stated sample or system.
- `INCIDENT_OR_OUTAGE_EVIDENCE`: mechanism established by a postmortem; not a controlled prevalence estimate.
- `HISTORICAL_INFERENCE`: influence/context inferred cautiously rather than documentary transmission.
- `IMPLEMENTATION_OR_CASE_EVIDENCE`: establishes one implementation's semantics, not universal payoff.
- `STANDARD_OR_GUIDANCE_REQUIREMENT`: establishes prescribed/current practice, not effectiveness.
- `CONTESTED` / `UNVERIFIED`: evidence is conflicting, sparse or too recent for mature transfer.

## Denominator construction

The population is not a checklist of products. A candidate entered the denominator if literature or failure evidence presented it as a potentially transferable response to partial failure, ordering, replication, authority, delivery, transaction, workflow, overload, recovery, evolution, observability or testing. It remained even if final disposition was rejection or ceremony. Two superficially similar candidates were kept separate when their protected consumer differed—for example, causal ordering versus freshness; consensus agreement versus fenced mutation; durable workflow state versus external completion; queue durability versus capacity.

## Source population summary

- Total source records: **102**
- Source classes: PEER_REVIEWED_SYSTEMS: 30; PEER_REVIEWED_FORMAL_RESULT: 7; PEER_REVIEWED_FOUNDATIONAL: 7; PEER_REVIEWED_ALGORITHM: 6; AUTHORITATIVE_INDUSTRIAL_GUIDANCE: 5; VENDOR_IMPLEMENTATION_DOCUMENTATION: 5; INCIDENT_POSTMORTEM: 4; PEER_REVIEWED_EMPIRICAL_SYSTEMS: 4; PEER_REVIEWED_FORMAL_AND_SYSTEMS: 3; HISTORICAL_PRIMARY: 2; PEER_REVIEWED_SURVEY: 2; AUTHORITATIVE_INDUSTRIAL_EXPERIMENT: 1; DOCTORAL_MONOGRAPH: 1; DOCTORAL_TECHNICAL_REPORT: 1; EMPIRICAL_PREPRINT: 1; FOUNDATIONAL_MONOGRAPH_CHAPTER: 1; HISTORICAL_TECHNICAL_REPORT: 1; INDUSTRIAL_SYSTEMS_REPORT: 1; PEER_REVIEWED_ANALYSIS: 1; PEER_REVIEWED_CONCEPTUAL_SYSTEMS: 1; PEER_REVIEWED_CRITIQUE: 1; PEER_REVIEWED_DOMAIN_TRANSLATION: 1; PEER_REVIEWED_EMPIRICAL_AND_SYSTEMS: 1; PEER_REVIEWED_INDUSTRIAL_PERSPECTIVE: 1; PEER_REVIEWED_INDUSTRIAL_SYSTEMS: 1; PEER_REVIEWED_POSITION_AND_PROTOTYPE: 1; PEER_REVIEWED_PRACTICE_ARTICLE: 1; PEER_REVIEWED_RETROSPECTIVE: 1; PEER_REVIEWED_TUTORIAL: 1; RECENT_PREPRINT_DOMAIN_TRANSLATION: 1; RECENT_REVIEW_PREPRINT: 1; SERIOUS_PRACTITIONER_CRITIQUE: 1; SERIOUS_TECHNICAL_CRITIQUE: 1; STANDARD: 1; SYSTEMATIC_MULTIVOCAL_REVIEW: 1; TECHNICAL_REPORT_PRIMARY: 1; TECHNICAL_REPORT_SYSTEMS: 1; VENDOR_IMPLEMENTATION_SPECIFICATION: 1
- Foundational/formal density is highest for causality, consistency, consensus, transactions and snapshots.
- Empirical/outage density is highest for recovery, common-mode failure, overload, configuration and observability limits.
- Vendor documentation is used only to establish implementation semantics and is never treated as independent effectiveness evidence.

## Source catalogue

The machine-readable source table is authoritative for exact fields. The catalogue below preserves the same frozen records.

### S001 — A Universal Modular ACTOR Formalism for Artificial Intelligence

- **Author/organisation:** Carl Hewitt, Peter Bishop, Richard Steiger
- **Date/version:** 1973
- **Class / epistemic label:** `HISTORICAL_PRIMARY` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://ijcai.org/Proceedings/73/Papers/027B.pdf
- **Publisher locator:** https://ijcai.org/Proceedings/73/Papers/027B.pdf
- **Exact locator used:** pp. 235–245
- **Claim supported:** Early actor lineage: independently executing actors communicate by messages.
- **Property relation:** P01, P02, P45
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S002 — Communicating Sequential Processes

- **Author/organisation:** C. A. R. Hoare
- **Date/version:** 1978
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/359576.359585
- **Publisher locator:** doi:10.1145/359576.359585
- **Exact locator used:** CACM 21(8), pp. 666–677, §§1–6
- **Claim supported:** Defines an explicit process-and-communication model rather than shared implicit control.
- **Property relation:** P01, P45
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S003 — Time, Clocks, and the Ordering of Events in a Distributed System

- **Author/organisation:** Leslie Lamport
- **Date/version:** 1978
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/359545.359563
- **Publisher locator:** doi:10.1145/359545.359563
- **Exact locator used:** CACM 21(7), pp. 558–565, §§1–4
- **Claim supported:** Defines happens-before and logical clocks; distinguishes causal partial order from an imposed total order.
- **Property relation:** P04, P05, P06, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S004 — Distributed Snapshots: Determining Global States of Distributed Systems

- **Author/organisation:** K. Mani Chandy, Leslie Lamport
- **Date/version:** 1985
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/214451.214456
- **Publisher locator:** doi:10.1145/214451.214456
- **Exact locator used:** ACM TOCS 3(1), pp. 63–75, Abstract and §§1–4
- **Claim supported:** Records a consistent global state without stopping an asynchronous message-passing computation under stated channel assumptions.
- **Property relation:** P35, P42, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S005 — The Byzantine Generals Problem

- **Author/organisation:** Leslie Lamport, Robert Shostak, Marshall Pease
- **Date/version:** 1982
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/357172.357176
- **Publisher locator:** doi:10.1145/357172.357176
- **Exact locator used:** ACM TOPLAS 4(3), pp. 382–401, §§1–4
- **Claim supported:** Formalises agreement with arbitrary faulty participants and derives fault-threshold conditions.
- **Property relation:** P01, P52
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S006 — Impossibility of Distributed Consensus with One Faulty Process

- **Author/organisation:** Michael J. Fischer, Nancy A. Lynch, Michael S. Paterson
- **Date/version:** 1985
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/3149.214121
- **Publisher locator:** doi:10.1145/3149.214121
- **Exact locator used:** JACM 32(2), pp. 374–382, Theorem 1
- **Claim supported:** Deterministic consensus cannot guarantee termination in full asynchrony with one crash failure.
- **Property relation:** P01, P11
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S007 — Consensus in the Presence of Partial Synchrony

- **Author/organisation:** Cynthia Dwork, Nancy Lynch, Larry Stockmeyer
- **Date/version:** 1988
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/42282.42283
- **Publisher locator:** doi:10.1145/42282.42283
- **Exact locator used:** JACM 35(2), pp. 288–323, §§1–5
- **Claim supported:** Defines partial-synchrony models and consensus protocols with eventual timing bounds.
- **Property relation:** P01, P11, P12
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S008 — Unreliable Failure Detectors for Reliable Distributed Systems

- **Author/organisation:** Tushar Deepak Chandra, Sam Toueg
- **Date/version:** 1996
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/226643.226647
- **Publisher locator:** doi:10.1145/226643.226647
- **Exact locator used:** JACM 43(2), pp. 225–267, §§2–6
- **Claim supported:** Separates failure-detector completeness from accuracy and characterises detectors sufficient for consensus.
- **Property relation:** P01, P02, P11, P41
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S009 — Implementing Fault-Tolerant Services Using the State Machine Approach: A Tutorial

- **Author/organisation:** Fred B. Schneider
- **Date/version:** 1990
- **Class / epistemic label:** `PEER_REVIEWED_TUTORIAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/98163.98167
- **Publisher locator:** doi:10.1145/98163.98167
- **Exact locator used:** ACM Computing Surveys 22(4), pp. 299–319, §§2–4
- **Claim supported:** Explains deterministic replicated state-machine execution, agreement and ordering requirements.
- **Property relation:** P07, P11, P12
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S010 — Viewstamped Replication: A New Primary Copy Method to Support Highly-Available Distributed Systems

- **Author/organisation:** Brian M. Oki, Barbara H. Liskov
- **Date/version:** 1988
- **Class / epistemic label:** `PEER_REVIEWED_ALGORITHM` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/62546.62549
- **Publisher locator:** doi:10.1145/62546.62549
- **Exact locator used:** PODC 1988, pp. 8–17, §§2–5
- **Claim supported:** Presents primary-copy replication with views and view changes.
- **Property relation:** P11, P12, P13, P37
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S011 — The Part-Time Parliament

- **Author/organisation:** Leslie Lamport
- **Date/version:** 1998
- **Class / epistemic label:** `PEER_REVIEWED_ALGORITHM` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/279227.279229
- **Publisher locator:** doi:10.1145/279227.279229
- **Exact locator used:** ACM TOCS 16(2), pp. 133–169, §§2–4
- **Claim supported:** Presents the Paxos lineage with ballots and intersecting majorities.
- **Property relation:** P10, P11, P12
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S012 — In Search of an Understandable Consensus Algorithm

- **Author/organisation:** Diego Ongaro, John Ousterhout
- **Date/version:** 2014
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro
- **Publisher locator:** USENIX ATC 2014
- **Exact locator used:** USENIX ATC 2014, pp. 305–319, §§2–6
- **Claim supported:** Presents Raft leader election, log replication, safety and a joint-consensus membership-change design.
- **Property relation:** P10, P11, P12, P13
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S013 — Lightweight Causal and Atomic Group Multicast

- **Author/organisation:** Kenneth P. Birman, André Schiper, Pat Stephenson
- **Date/version:** 1991
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/ABCD+91.pdf
- **Publisher locator:** https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/ABCD+91.pdf
- **Exact locator used:** ACM TOCS 9(3), pp. 272–314, §§1–5
- **Claim supported:** Develops causal and atomic multicast within a group-membership/virtual-synchrony model.
- **Property relation:** P04, P11, P12, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S014 — Vertical Paxos and Primary-Backup Replication

- **Author/organisation:** Leslie Lamport, Dahlia Malkhi, Lidong Zhou
- **Date/version:** 2009
- **Class / epistemic label:** `PEER_REVIEWED_ALGORITHM` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.microsoft.com/en-us/research/publication/vertical-paxos-and-primary-backup-replication/
- **Publisher locator:** https://www.microsoft.com/en-us/research/publication/vertical-paxos-and-primary-backup-replication/
- **Exact locator used:** PODC 2009, pp. 312–321, §§2–5
- **Claim supported:** Separates configuration authority from data-plane consensus and analyses reconfiguration.
- **Property relation:** P10, P12, P40
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S015 — Weighted Voting for Replicated Data

- **Author/organisation:** David K. Gifford
- **Date/version:** 1979
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.cs.cornell.edu/courses/cs5414/2017fa/papers/gifford79.pdf
- **Publisher locator:** https://www.cs.cornell.edu/courses/cs5414/2017fa/papers/gifford79.pdf
- **Exact locator used:** SOSP 1979, pp. 150–162, §§2–5
- **Claim supported:** Introduces read/write quorum intersection conditions relative to a configured vote population.
- **Property relation:** P07, P10
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S016 — Epidemic Algorithms for Replicated Database Maintenance

- **Author/organisation:** Alan Demers et al.
- **Date/version:** 1987
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/41840.41841
- **Publisher locator:** doi:10.1145/41840.41841
- **Exact locator used:** PODC 1987, pp. 1–12, §§1–5
- **Claim supported:** Studies epidemic propagation and anti-entropy for replica maintenance.
- **Property relation:** P08, P09
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S017 — Notes on Data Base Operating Systems

- **Author/organisation:** Jim Gray
- **Date/version:** 1978
- **Class / epistemic label:** `FOUNDATIONAL_MONOGRAPH_CHAPTER` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1007/3-540-08755-9_9
- **Publisher locator:** doi:10.1007/3-540-08755-9_9
- **Exact locator used:** LNCS 60, pp. 393–481, transaction/log/recovery sections
- **Claim supported:** Systematises transactions, logging, locking, recovery and failure assumptions.
- **Property relation:** P23, P35, P36, P38
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S018 — Nonblocking Commit Protocols

- **Author/organisation:** Dale Skeen
- **Date/version:** 1981
- **Class / epistemic label:** `PEER_REVIEWED_ALGORITHM` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/582318.582339
- **Publisher locator:** doi:10.1145/582318.582339
- **Exact locator used:** SIGMOD 1981, pp. 133–142, §§2–5
- **Claim supported:** Analyses two-phase-commit blocking and nonblocking commit conditions.
- **Property relation:** P23, P37
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S019 — Sagas

- **Author/organisation:** Hector Garcia-Molina, Kenneth Salem
- **Date/version:** 1987
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/38713.38742
- **Publisher locator:** doi:10.1145/38713.38742
- **Exact locator used:** SIGMOD 1987, pp. 249–259, §§1–5
- **Claim supported:** Defines long-lived transactions as subtransactions with compensating transactions.
- **Property relation:** P24, P25, P27
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S020 — Concurrency Control in Distributed Database Systems

- **Author/organisation:** Philip A. Bernstein, Nathan Goodman
- **Date/version:** 1981
- **Class / epistemic label:** `PEER_REVIEWED_SURVEY` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/356842.356846
- **Publisher locator:** doi:10.1145/356842.356846
- **Exact locator used:** ACM Computing Surveys 13(2), pp. 185–221
- **Claim supported:** Surveys distributed concurrency control and serialisability mechanisms.
- **Property relation:** P07, P15, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S021 — Linearizability: A Correctness Condition for Concurrent Objects

- **Author/organisation:** Maurice P. Herlihy, Jeannette M. Wing
- **Date/version:** 1990
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/78969.78972
- **Publisher locator:** doi:10.1145/78969.78972
- **Exact locator used:** ACM TOPLAS 12(3), pp. 463–492, §§2–4
- **Claim supported:** Defines linearizability as a locality-preserving real-time correctness condition.
- **Property relation:** P06, P07
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S022 — A Critique of ANSI SQL Isolation Levels

- **Author/organisation:** Hal Berenson et al.
- **Date/version:** 1995
- **Class / epistemic label:** `PEER_REVIEWED_CRITIQUE` / `CRITIQUE_OF_ASSUMPTION_OR_IMPLEMENTATION`
- **Stable locator:** https://doi.org/10.1145/223784.223785
- **Publisher locator:** doi:10.1145/223784.223785
- **Exact locator used:** SIGMOD 1995, pp. 1–10, §§2–4
- **Claim supported:** Shows isolation labels omit anomalies and distinguishes snapshot isolation from serialisability.
- **Property relation:** P07, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S023 — Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions

- **Author/organisation:** Atul Adya
- **Date/version:** 1999
- **Class / epistemic label:** `DOCTORAL_MONOGRAPH` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://pmg.csail.mit.edu/papers/adya-phd.pdf
- **Publisher locator:** https://pmg.csail.mit.edu/papers/adya-phd.pdf
- **Exact locator used:** MIT PhD thesis, Chapters 2–4
- **Claim supported:** Provides graph-based definitions of isolation anomalies and weak consistency.
- **Property relation:** P07, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S024 — Serializable Isolation for Snapshot Databases

- **Author/organisation:** Michael J. Cahill, Uwe Röhm, Alan D. Fekete
- **Date/version:** 2008
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/1376616.1376690
- **Publisher locator:** doi:10.1145/1376616.1376690
- **Exact locator used:** SIGMOD 2008, pp. 729–738, §§2–5
- **Claim supported:** Shows how dangerous structures under snapshot isolation can be detected to provide serialisable execution.
- **Property relation:** P07, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S025 — Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services

- **Author/organisation:** Seth Gilbert, Nancy Lynch
- **Date/version:** 2002
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/564585.564601
- **Publisher locator:** doi:10.1145/564585.564601
- **Exact locator used:** SIGACT News 33(2), pp. 51–59, §§2–4
- **Claim supported:** Formalises an asynchronous partition-case impossibility for atomic consistency and availability.
- **Property relation:** P01, P07, P15
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S026 — CAP Twelve Years Later: How the 'Rules' Have Changed

- **Author/organisation:** Eric Brewer
- **Date/version:** 2012
- **Class / epistemic label:** `PEER_REVIEWED_RETROSPECTIVE` / `SOURCE_INTERPRETATION`
- **Stable locator:** https://doi.org/10.1109/MC.2012.37
- **Publisher locator:** doi:10.1109/MC.2012.37
- **Exact locator used:** IEEE Computer 45(2), pp. 23–29
- **Claim supported:** Rejects the simplistic permanent 'pick two' reading and treats partition handling/recovery as a continuum.
- **Property relation:** P01, P07, P15
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S027 — Consistency Tradeoffs in Modern Distributed Database System Design: CAP is Only Part of the Story

- **Author/organisation:** Daniel J. Abadi
- **Date/version:** 2012
- **Class / epistemic label:** `PEER_REVIEWED_ANALYSIS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1109/MC.2012.33
- **Publisher locator:** doi:10.1109/MC.2012.33
- **Exact locator used:** IEEE Computer 45(2), pp. 37–42
- **Claim supported:** PACELC frames normal-operation latency/consistency tradeoffs as well as partition tradeoffs.
- **Property relation:** P07, P15, P16
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S028 — Eventually Consistent

- **Author/organisation:** Werner Vogels
- **Date/version:** 2009
- **Class / epistemic label:** `PEER_REVIEWED_INDUSTRIAL_PERSPECTIVE` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/1435417.1435432
- **Publisher locator:** doi:10.1145/1435417.1435432
- **Exact locator used:** CACM 52(1), pp. 40–44
- **Claim supported:** Explains eventual consistency and client-visible consistency variants.
- **Property relation:** P06, P07, P09
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S029 — Session Guarantees for Weakly Consistent Replicated Data

- **Author/organisation:** Douglas B. Terry et al.
- **Date/version:** 1994
- **Class / epistemic label:** `PEER_REVIEWED_ALGORITHM` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1109/PDIS.1994.331722
- **Publisher locator:** doi:10.1109/PDIS.1994.331722
- **Exact locator used:** PDIS 1994, pp. 140–149
- **Claim supported:** Defines read-your-writes, monotonic reads/writes and writes-follow-reads guarantees.
- **Property relation:** P06, P07
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S030 — A Comprehensive Study of Convergent and Commutative Replicated Data Types

- **Author/organisation:** Marc Shapiro, Nuno Preguiça, Carlos Baquero, Marek Zawirski
- **Date/version:** 2011
- **Class / epistemic label:** `TECHNICAL_REPORT_PRIMARY` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://inria.hal.science/inria-00555588/document
- **Publisher locator:** https://inria.hal.science/inria-00555588/document
- **Exact locator used:** INRIA RR-7506, §§2–7
- **Claim supported:** Defines state- and operation-based CRDT convergence conditions under stated delivery assumptions.
- **Property relation:** P08, P09, P16
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S031 — Don't Settle for Eventual: Scalable Causal Consistency for Wide-Area Storage with COPS

- **Author/organisation:** Wyatt Lloyd, Michael J. Freedman, Michael Kaminsky, David G. Andersen
- **Date/version:** 2011
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/2043556.2043593
- **Publisher locator:** doi:10.1145/2043556.2043593
- **Exact locator used:** SOSP 2011, pp. 401–416, §§2–5
- **Claim supported:** Demonstrates a geo-replicated causal-consistency design and its dependency-tracking tradeoffs.
- **Property relation:** P04, P06, P07
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S032 — Timestamps in Message-Passing Systems That Preserve the Partial Ordering

- **Author/organisation:** Colin J. Fidge
- **Date/version:** 1988
- **Class / epistemic label:** `HISTORICAL_TECHNICAL_REPORT` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/Fidge.pdf
- **Publisher locator:** https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/Fidge.pdf
- **Exact locator used:** Australian National University Technical Report 88/4, §§2–4
- **Claim supported:** Develops vector-clock timestamps preserving distributed partial order.
- **Property relation:** P04, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S033 — Logical Physical Clocks and Consistent Snapshots in Globally Distributed Databases

- **Author/organisation:** Sandeep S. Kulkarni, Murat Demirbas, Deepak Madappa, Bharadwaj Avva, Marcelo Leone
- **Date/version:** 2014
- **Class / epistemic label:** `TECHNICAL_REPORT_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://cse.buffalo.edu/tech-reports/2014-04.pdf
- **Publisher locator:** https://cse.buffalo.edu/tech-reports/2014-04.pdf
- **Exact locator used:** University at Buffalo TR 2014-04, §§2–5
- **Claim supported:** Presents hybrid logical clocks combining close-to-physical timestamps with logical causality.
- **Property relation:** P04, P05, P06
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S034 — An Upper and Lower Bound for Clock Synchronization

- **Author/organisation:** Jennifer Lundelius, Nancy Lynch
- **Date/version:** 1984
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_RESULT` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1016/S0019-9958(84)80033-9
- **Publisher locator:** doi:10.1016/S0019-9958(84)80033-9
- **Exact locator used:** Information and Control 62(2–3), pp. 190–204
- **Claim supported:** Establishes limits on clock synchronisation under uncertain message delay.
- **Property relation:** P05
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S035 — Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency

- **Author/organisation:** Cary G. Gray, David R. Cheriton
- **Date/version:** 1989
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/74851.74870
- **Publisher locator:** doi:10.1145/74851.74870
- **Exact locator used:** SOSP 1989, pp. 202–210, §§2–5
- **Claim supported:** Introduces time-bounded leases and their clock/network assumptions.
- **Property relation:** P05, P13, P37
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S036 — Spanner: Google's Globally-Distributed Database

- **Author/organisation:** James C. Corbett et al.
- **Date/version:** 2012
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
- **Publisher locator:** https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
- **Exact locator used:** OSDI 2012, pp. 251–264, §§2–4 and 6
- **Claim supported:** Demonstrates synchronously replicated geo-transactions and external consistency using bounded clock uncertainty.
- **Property relation:** P05, P07, P10, P15, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S037 — Dynamo: Amazon's Highly Available Key-value Store

- **Author/organisation:** Giuseppe DeCandia et al.
- **Date/version:** 2007
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
- **Publisher locator:** doi:10.1145/1294261.1294281
- **Exact locator used:** SOSP 2007, pp. 205–220, §§2–6
- **Claim supported:** Documents vector clocks, sloppy quorums, hinted handoff and anti-entropy in an always-writeable key-value design.
- **Property relation:** P03, P06, P08, P09, P10
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S038 — Coordination Avoidance in Database Systems

- **Author/organisation:** Peter Bailis, Alan Fekete, Michael J. Franklin, Ali Ghodsi, Joseph M. Hellerstein, Ion Stoica
- **Date/version:** 2014
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_AND_SYSTEMS` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://www.vldb.org/pvldb/vol8/p185-bailis.pdf
- **Publisher locator:** https://www.vldb.org/pvldb/vol8/p185-bailis.pdf
- **Exact locator used:** PVLDB 8(3), pp. 185–196, §§2–5
- **Claim supported:** Defines invariant confluence as a condition for preserving invariants without coordination.
- **Property relation:** P15, P16
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S039 — Highly Available Transactions: Virtues and Limitations

- **Author/organisation:** Peter Bailis, Aaron Davidson, Alan Fekete, Ali Ghodsi, Joseph M. Hellerstein, Ion Stoica
- **Date/version:** 2014
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_AND_SYSTEMS` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://www.vldb.org/pvldb/vol7/p181-bailis.pdf
- **Publisher locator:** https://www.vldb.org/pvldb/vol7/p181-bailis.pdf
- **Exact locator used:** PVLDB 7(3), pp. 181–192, §§2–5
- **Claim supported:** Characterises transaction guarantees achievable with high availability under partitions.
- **Property relation:** P07, P15, P16, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S040 — Calvin: Fast Distributed Transactions for Partitioned Database Systems

- **Author/organisation:** Alexander Thomson et al.
- **Date/version:** 2012
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/2213836.2213838
- **Publisher locator:** doi:10.1145/2213836.2213838
- **Exact locator used:** SIGMOD 2012, pp. 1–12, §§2–5
- **Claim supported:** Uses deterministic transaction ordering to reduce distributed commit/concurrency-control overhead.
- **Property relation:** P15, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S041 — Fast Commitment for Geo-Distributed Transactions via Decentralized Co-coordinators

- **Author/organisation:** Zihao Zhang, Huiqi Hu, Xuan Zhou, Yaofeng Tu, Weining Qian, Aoying Zhou
- **Date/version:** 2024
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.vldb.org/pvldb/vol17/p2555-hu.pdf
- **Publisher locator:** doi:10.14778/3675034.3675046
- **Exact locator used:** PVLDB 17(10), pp. 2555–2567
- **Claim supported:** D2PC reduces cross-region transaction commit latency under its protocol assumptions.
- **Property relation:** P15, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S042 — Chablis: Fast and General Transactions in Geo-Distributed Systems

- **Author/organisation:** Yunhao Chen et al.
- **Date/version:** 2024
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://www.cidrdb.org/cidr2024/papers/p18-chen.pdf
- **Publisher locator:** https://www.cidrdb.org/cidr2024/papers/p18-chen.pdf
- **Exact locator used:** CIDR 2024, full paper
- **Claim supported:** Explores lower-latency geo-transaction design while preserving explicit transaction semantics.
- **Property relation:** P15, P23
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S043 — End-to-End Arguments in System Design

- **Author/organisation:** Jerome H. Saltzer, David P. Reed, David D. Clark
- **Date/version:** 1984
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/357401.357402
- **Publisher locator:** doi:10.1145/357401.357402
- **Exact locator used:** ACM TOCS 2(4), pp. 277–288, §§1–4
- **Claim supported:** Shows why correctness functions often cannot be completely supplied by lower layers alone.
- **Property relation:** P18, P21, P22, P27
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S044 — Implementing Remote Procedure Calls

- **Author/organisation:** Andrew D. Birrell, Bruce Jay Nelson
- **Date/version:** 1984
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/2080.357392
- **Publisher locator:** doi:10.1145/2080.357392
- **Exact locator used:** ACM TOCS 2(1), pp. 39–59, §§2–5
- **Claim supported:** Documents RPC retransmission, duplicate suppression and crash uncertainty.
- **Property relation:** P02, P17, P19, P21
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S045 — Kafka: A Distributed Messaging System for Log Processing

- **Author/organisation:** Jay Kreps, Neha Narkhede, Jun Rao
- **Date/version:** 2011
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://notes.stephenholiday.com/Kafka.pdf
- **Publisher locator:** https://notes.stephenholiday.com/Kafka.pdf
- **Exact locator used:** NetDB 2011, §§2–5
- **Claim supported:** Introduces partitioned durable logs, consumer offsets and broker/consumer architecture.
- **Property relation:** P17, P20, P22, P25, P35
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S046 — MillWheel: Fault-Tolerant Stream Processing at Internet Scale

- **Author/organisation:** Tyler Akidau et al.
- **Date/version:** 2013
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.14778/2536222.2536229
- **Publisher locator:** doi:10.14778/2536222.2536229
- **Exact locator used:** PVLDB 6(11), pp. 1033–1044, §§2–5
- **Claim supported:** Presents persistent per-key state, timers, low watermarks and exactly-once processing within its defined boundary.
- **Property relation:** P17, P20, P22, P25, P35
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S047 — The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing

- **Author/organisation:** Tyler Akidau et al.
- **Date/version:** 2015
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf
- **Publisher locator:** https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf
- **Exact locator used:** PVLDB 8(12), pp. 1792–1803
- **Claim supported:** Separates event time, processing time, windowing, watermarks, triggers and accumulation.
- **Property relation:** P04, P06, P17, P25
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S048 — Lightweight Asynchronous Snapshots for Distributed Dataflows

- **Author/organisation:** Paris Carbone, Gyula Fóra, Stephan Ewen, Seif Haridi, Kostas Tzoumas
- **Date/version:** 2015
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://arxiv.org/abs/1506.08603
- **Publisher locator:** https://arxiv.org/abs/1506.08603
- **Exact locator used:** arXiv:1506.08603; Abstract and §§2–5
- **Claim supported:** Adapts consistent snapshots to cyclic and acyclic distributed dataflow execution.
- **Property relation:** P22, P35, P36
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S049 — KIP-98: Exactly Once Delivery and Transactional Messaging

- **Author/organisation:** Apache Kafka Project
- **Date/version:** 2017; current page accessed 2026-08-12
- **Class / epistemic label:** `VENDOR_IMPLEMENTATION_SPECIFICATION` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging
- **Publisher locator:** https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging
- **Exact locator used:** Motivation, Proposed Changes, Semantics
- **Claim supported:** Specifies producer idempotence and transactions over Kafka records and offsets.
- **Property relation:** P17, P20, P22, P49
- **Contrary evidence / limit:** Does not independently establish exactly-once effects in arbitrary external systems.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S050 — Fault-Tolerant and Transactional Stateful Serverless Workflows

- **Author/organisation:** Haoran Zhang, Adney Cardoza, Peter Baile Chen, Sebastian Angel, Vincent Liu
- **Date/version:** 2020
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/osdi20/presentation/zhang-haoran
- **Publisher locator:** https://www.usenix.org/conference/osdi20/presentation/zhang-haoran
- **Exact locator used:** OSDI 2020, pp. 1187–1204, §§2–6
- **Claim supported:** Introduces Beldi, combining durable invocation logs, concurrency control and transactional workflows.
- **Property relation:** P19, P22, P25, P26, P28
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S051 — Boki: Stateful Serverless Computing with Shared Logs

- **Author/organisation:** Zhipeng Jia, Emmett Witchel
- **Date/version:** 2021
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/3477132.3483541
- **Publisher locator:** doi:10.1145/3477132.3483541
- **Exact locator used:** SOSP 2021, design and evaluation sections
- **Claim supported:** Uses a shared log and metalog to provide durable, consistent state for serverless applications.
- **Property relation:** P25, P26, P28, P35
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S052 — Durable Functions: Semantics for Stateful Serverless

- **Author/organisation:** Sebastian Burckhardt, Chris Gillum, David Justo, Konstantinos Kallas, Connor McMahon, Christopher S. Meiklejohn
- **Date/version:** 2021
- **Class / epistemic label:** `PEER_REVIEWED_FORMAL_AND_SYSTEMS` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/3485510
- **Publisher locator:** doi:10.1145/3485510
- **Exact locator used:** PACMPL 5(OOPSLA), Article 133, §§2–5
- **Claim supported:** Formalises durable-orchestration replay and stateful-function semantics.
- **Property relation:** P25, P26, P28
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S053 — Netherite: Efficient Execution of Serverless Workflows

- **Author/organisation:** Sebastian Burckhardt et al.
- **Date/version:** 2022
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.microsoft.com/en-us/research/publication/netherite-efficient-execution-of-serverless-workflows/
- **Publisher locator:** https://www.microsoft.com/en-us/research/publication/netherite-efficient-execution-of-serverless-workflows/
- **Exact locator used:** PVLDB 15, design/recovery/evaluation sections
- **Claim supported:** Uses partitioned recovery logs, pipelined persistence, snapshots and partition movement for durable workflows.
- **Property relation:** P25, P26, P28, P35, P36
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S054 — ExoFlow: A Universal Workflow System for Exactly-Once DAGs

- **Author/organisation:** Siyuan Zhuang, Stephanie Wang, Eric Liang, Yi Cheng, Ion Stoica
- **Date/version:** 2023
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/osdi23/presentation/zhuang
- **Publisher locator:** https://www.usenix.org/conference/osdi23/presentation/zhuang
- **Exact locator used:** OSDI 2023, pp. 269–286, §§2–6
- **Claim supported:** Separates workflow execution from recovery and annotates recovery semantics for heterogeneous DAG tasks.
- **Property relation:** P25, P26, P27, P28, P49
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S055 — Consistency and Correctness in Data-Oriented Workflow Systems

- **Author/organisation:** Michael Stonebraker, Xinjing Zhou, Peter Kraft, Qian Li
- **Date/version:** CIDR 2026 (paper dated 2025)
- **Class / epistemic label:** `PEER_REVIEWED_POSITION_AND_PROTOTYPE` / `SOURCE_INTERPRETATION`
- **Stable locator:** https://www.cidrdb.org/cidr2026/papers/p9-stonebraker.pdf
- **Publisher locator:** https://www.cidrdb.org/cidr2026/papers/p9-stonebraker.pdf
- **Exact locator used:** 7 pages; Abstract, §§1–5
- **Claim supported:** Argues durable execution alone is insufficient; compares transaction backout with saga compensation and proposes workflow-level AC/DC semantics.
- **Property relation:** P23, P24, P25, P27
- **Contrary evidence / limit:** Position/prototype evidence is early and does not settle the best abstraction for all workflows.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S056 — Distributed Speculative Execution for Resilient Cloud Applications

- **Author/organisation:** Tianyu Li, Badrish Chandramouli, Philip A. Bernstein, Sam Madden
- **Date/version:** 2026
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://www.usenix.org/conference/osdi26/presentation/li-tianyu
- **Publisher locator:** https://www.usenix.org/conference/osdi26/presentation/li-tianyu
- **Exact locator used:** OSDI 2026, pp. 2027–2045
- **Claim supported:** Uses reactive repair and speculative persistence to reduce durable-execution latency while preserving a defined programming model.
- **Property relation:** P25, P28, P36
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S057 — Durable orchestrator code constraints

- **Author/organisation:** Microsoft
- **Date/version:** Current documentation accessed 2026-08-12
- **Class / epistemic label:** `VENDOR_IMPLEMENTATION_DOCUMENTATION` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-code-constraints
- **Publisher locator:** https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-code-constraints
- **Exact locator used:** Deterministic APIs, replay behaviour and versioning cautions
- **Claim supported:** Documents deterministic-orchestrator constraints caused by replay.
- **Property relation:** P28
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S058 — Durable Functions types and features overview

- **Author/organisation:** Microsoft
- **Date/version:** Current documentation accessed 2026-08-12
- **Class / epistemic label:** `VENDOR_IMPLEMENTATION_DOCUMENTATION` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview
- **Publisher locator:** https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-types-features-overview
- **Exact locator used:** Activity functions, reliability and idempotency notes
- **Claim supported:** Documents that activities may be retried and should be duplicate-safe.
- **Property relation:** P19, P25, P26, P27
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S059 — Choosing workflow type in Step Functions

- **Author/organisation:** Amazon Web Services
- **Date/version:** Current documentation accessed 2026-08-12
- **Class / epistemic label:** `VENDOR_IMPLEMENTATION_DOCUMENTATION` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html
- **Publisher locator:** https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html
- **Exact locator used:** Standard versus Express execution semantics
- **Claim supported:** Documents differing at-most-once/at-least-once workflow execution claims and scope.
- **Property relation:** P17, P25, P49
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S060 — Workflow Definition

- **Author/organisation:** Temporal Technologies
- **Date/version:** Current documentation accessed 2026-08-12
- **Class / epistemic label:** `VENDOR_IMPLEMENTATION_DOCUMENTATION` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://docs.temporal.io/workflow-definition
- **Publisher locator:** https://docs.temporal.io/workflow-definition
- **Exact locator used:** Deterministic constraints, replay and versioning
- **Claim supported:** Documents durable workflow replay and deterministic-code constraints in one implementation.
- **Property relation:** P25, P26, P28
- **Contrary evidence / limit:** Vendor documentation establishes implementation behaviour, not independent effectiveness.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S061 — The Tail at Scale

- **Author/organisation:** Jeffrey Dean, Luiz André Barroso
- **Date/version:** 2013
- **Class / epistemic label:** `PEER_REVIEWED_INDUSTRIAL_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/2408776.2408794
- **Publisher locator:** doi:10.1145/2408776.2408794
- **Exact locator used:** CACM 56(2), pp. 74–80
- **Claim supported:** Shows tail-latency amplification across fan-out and mitigation costs.
- **Property relation:** P02, P32, P33
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S062 — Metastable Failures in Distributed Systems

- **Author/organisation:** Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, Timothy Zhu
- **Date/version:** 2021
- **Class / epistemic label:** `PEER_REVIEWED_CONCEPTUAL_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/3458336.3465286
- **Publisher locator:** doi:10.1145/3458336.3465286
- **Exact locator used:** HotOS 2021, pp. 221–227
- **Claim supported:** Defines failures sustained by positive feedback after the initiating disturbance is removed.
- **Property relation:** P29, P30, P31, P32, P33
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S063 — Metastable Failures in the Wild

- **Author/organisation:** Lexiang Huang et al.
- **Date/version:** 2022
- **Class / epistemic label:** `PEER_REVIEWED_EMPIRICAL_SYSTEMS` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://www.usenix.org/conference/osdi22/presentation/huang-lexiang
- **Publisher locator:** https://www.usenix.org/conference/osdi22/presentation/huang-lexiang
- **Exact locator used:** OSDI 2022, pp. 73–90, §§2–6
- **Claim supported:** Analyses 22 metastable failures across 11 organisations and recurring amplification mechanisms.
- **Property relation:** P29, P30, P31, P32, P33
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S064 — Overload Control for Scaling WeChat Microservices

- **Author/organisation:** Hong Zhang et al.
- **Date/version:** 2018
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/3267809.3267823
- **Publisher locator:** doi:10.1145/3267809.3267823
- **Exact locator used:** SoCC 2018, design and evaluation sections
- **Claim supported:** Presents DAGOR using business priority and user fairness across call chains.
- **Property relation:** P29, P30, P31, P33
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S065 — Rajomon: Decentralized and Coordinated Overload Control for Latency-Sensitive Microservices

- **Author/organisation:** Jiali Xing et al.
- **Date/version:** 2025
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/nsdi25/presentation/xing
- **Publisher locator:** https://www.usenix.org/conference/nsdi25/presentation/xing
- **Exact locator used:** NSDI 2025, pp. 21–36
- **Claim supported:** Combines per-service overload decisions with distributed coordination.
- **Property relation:** P29, P30, P31, P33
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S066 — Addressing Cascading Failures

- **Author/organisation:** Google
- **Date/version:** 2016 online edition accessed 2026-08-12
- **Class / epistemic label:** `AUTHORITATIVE_INDUSTRIAL_GUIDANCE` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://sre.google/sre-book/addressing-cascading-failures/
- **Publisher locator:** https://sre.google/sre-book/addressing-cascading-failures/
- **Exact locator used:** Server Overload, Queue Management, Retry and Load Shedding sections
- **Claim supported:** Documents queue growth, retry amplification, cascading failure and mitigation practices.
- **Property relation:** P29, P30, P31, P32, P33, P34, P41
- **Contrary evidence / limit:** Field-derived guidance, not a controlled comparative effectiveness study.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S067 — Timeouts, Retries, and Backoff with Jitter

- **Author/organisation:** Marc Brooker / Amazon Web Services
- **Date/version:** Current edition dated 2026-06-12
- **Class / epistemic label:** `AUTHORITATIVE_INDUSTRIAL_GUIDANCE` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
- **Publisher locator:** https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
- **Exact locator used:** Timeouts, Retries and backoff, Jitter
- **Claim supported:** Explains why timeout is not proof of nonexecution and why bounded retries/backoff/jitter matter.
- **Property relation:** P02, P19, P32, P33
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S068 — Exponential Backoff and Jitter

- **Author/organisation:** Marc Brooker / Amazon Web Services
- **Date/version:** 2015; updated 2023
- **Class / epistemic label:** `AUTHORITATIVE_INDUSTRIAL_EXPERIMENT` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- **Publisher locator:** https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- **Exact locator used:** Simulation figures and algorithm comparison
- **Claim supported:** Simulation shows jitter reduces synchronised retry work and contention.
- **Property relation:** P32, P33
- **Contrary evidence / limit:** Simulation supports the mechanism under its model, not universal field effectiveness.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S069 — Making retries safe with idempotent APIs

- **Author/organisation:** Malcolm Featonby / Amazon Web Services
- **Date/version:** Current edition accessed 2026-08-12
- **Class / epistemic label:** `AUTHORITATIVE_INDUSTRIAL_GUIDANCE` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- **Publisher locator:** https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- **Exact locator used:** Semantic equivalence, client request identifiers and late-arriving requests
- **Claim supported:** Explains parameter-bound request identity, duplicate handling and the limits of inferred equivalence.
- **Property relation:** P18, P19, P20
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S070 — Leader election in distributed systems

- **Author/organisation:** Amazon Web Services
- **Date/version:** Current edition dated 2026-06-12
- **Class / epistemic label:** `AUTHORITATIVE_INDUSTRIAL_GUIDANCE` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://aws.amazon.com/builders-library/leader-election-in-distributed-systems/
- **Publisher locator:** https://aws.amazon.com/builders-library/leader-election-in-distributed-systems/
- **Exact locator used:** Leases, local time and lock caveats
- **Claim supported:** Documents lease reliance on time, pauses and the need to treat leader election as a scoped mechanism.
- **Property relation:** P05, P13, P50
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S071 — A Survey of Rollback-Recovery Protocols in Message-Passing Systems

- **Author/organisation:** Elmootazbellah N. Elnozahy, Lorenzo Alvisi, Yi-Min Wang, David B. Johnson
- **Date/version:** 2002
- **Class / epistemic label:** `PEER_REVIEWED_SURVEY` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/survey.pdf
- **Publisher locator:** doi:10.1145/568522.568525
- **Exact locator used:** ACM Computing Surveys 34(3), pp. 375–408, §§2–6
- **Claim supported:** Classifies checkpointing/message-logging recovery, orphan processes and domino effects.
- **Property relation:** P35, P36, P38
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S072 — Checkpointing and Rollback-Recovery for Distributed Systems

- **Author/organisation:** Richard Koo, Sam Toueg
- **Date/version:** 1987
- **Class / epistemic label:** `PEER_REVIEWED_ALGORITHM` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1109/TSE.1987.232562
- **Publisher locator:** doi:10.1109/TSE.1987.232562
- **Exact locator used:** IEEE TSE 13(1), pp. 23–31, §§2–5
- **Claim supported:** Provides coordinated checkpoint and recovery algorithms avoiding inconsistent recovery lines.
- **Property relation:** P35, P36
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S073 — October 21 post-incident analysis

- **Author/organisation:** Jason Warner / GitHub
- **Date/version:** 2018-10-30; updated 2021-12-19
- **Class / epistemic label:** `INCIDENT_POSTMORTEM` / `INCIDENT_OR_OUTAGE_EVIDENCE`
- **Stable locator:** https://github.blog/news-insights/company-news/oct21-post-incident-analysis/
- **Publisher locator:** https://github.blog/news-insights/company-news/oct21-post-incident-analysis/
- **Exact locator used:** Background; incident timeline; recovery; next steps
- **Claim supported:** A 43-second network partition triggered divergent database writes, stale reads, multi-hour restore/catch-up and backlog risks.
- **Property relation:** P02, P03, P06, P29, P32, P37, P38, P41
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S074 — Postmortem of database outage of January 31

- **Author/organisation:** GitLab
- **Date/version:** 2017
- **Class / epistemic label:** `INCIDENT_POSTMORTEM` / `INCIDENT_OR_OUTAGE_EVIDENCE`
- **Stable locator:** https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/
- **Publisher locator:** https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/
- **Exact locator used:** Timeline, recovery attempts and backup findings
- **Claim supported:** Configured backup/replication mechanisms did not produce a usable timely restore path.
- **Property relation:** P03, P36, P38
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S075 — More Details About the October 4 Outage

- **Author/organisation:** Santosh Janardhan / Meta
- **Date/version:** 2021-10-05
- **Class / epistemic label:** `INCIDENT_POSTMORTEM` / `INCIDENT_OR_OUTAGE_EVIDENCE`
- **Stable locator:** https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/
- **Publisher locator:** https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/
- **Exact locator used:** Backbone, BGP/DNS withdrawal and recovery-access sections
- **Claim supported:** A backbone configuration change removed reachability, withdrew DNS and impaired internal recovery tooling.
- **Property relation:** P03, P40, P41, P42
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S076 — Cloudflare outage on November 18, 2025

- **Author/organisation:** Cloudflare
- **Date/version:** 2025-11-18
- **Class / epistemic label:** `INCIDENT_POSTMORTEM` / `INCIDENT_OR_OUTAGE_EVIDENCE`
- **Stable locator:** https://blog.cloudflare.com/18-november-2025-outage/
- **Publisher locator:** https://blog.cloudflare.com/18-november-2025-outage/
- **Exact locator used:** Database permissions change, feature-file propagation, process failure and recovery timeline
- **Claim supported:** A configuration interaction generated an oversized file that propagated globally, caused failures and complicated diagnosis/recovery.
- **Property relation:** P03, P33, P39, P40, P41
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S077 — Why Do Upgrades Fail and What Can We Do about It? Toward Dependable, Online Upgrades in Enterprise Systems

- **Author/organisation:** Tudor Dumitraș, Priya Narasimhan
- **Date/version:** 2009
- **Class / epistemic label:** `PEER_REVIEWED_EMPIRICAL_AND_SYSTEMS` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://doi.org/10.1007/978-3-642-10445-9_18
- **Publisher locator:** doi:10.1007/978-3-642-10445-9_18
- **Exact locator used:** Middleware 2009, pp. 349–372, §§2–6
- **Claim supported:** Develops an upgrade-centric fault model from field data and analyses hidden dependencies/mixed versions.
- **Property relation:** P39, P40
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S078 — Updating A Message Type

- **Author/organisation:** Protocol Buffers Project / Google
- **Date/version:** Current documentation accessed 2026-08-12
- **Class / epistemic label:** `VENDOR_IMPLEMENTATION_DOCUMENTATION` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://protobuf.dev/programming-guides/proto3/#updating
- **Publisher locator:** https://protobuf.dev/programming-guides/proto3/#updating
- **Exact locator used:** Binary wire-safe and unsafe changes
- **Claim supported:** Documents concrete forward/backward wire-compatibility constraints.
- **Property relation:** P39
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S079 — Ensuring rollback safety during deployments

- **Author/organisation:** Amazon Web Services
- **Date/version:** Current edition dated 2026-06-12
- **Class / epistemic label:** `AUTHORITATIVE_INDUSTRIAL_GUIDANCE` / `IMPLEMENTATION_OR_CASE_EVIDENCE`
- **Stable locator:** https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/
- **Publisher locator:** https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/
- **Exact locator used:** Backward compatibility and rollback sections
- **Claim supported:** Explains why deployments and rollback require mixed-version compatibility across control/data boundaries.
- **Property relation:** P39, P40
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S080 — Dapper, a Large-Scale Distributed Systems Tracing Infrastructure

- **Author/organisation:** Benjamin H. Sigelman et al.
- **Date/version:** 2010
- **Class / epistemic label:** `INDUSTRIAL_SYSTEMS_REPORT` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://research.google.com/archive/papers/dapper-2010-1.pdf
- **Publisher locator:** https://research.google.com/archive/papers/dapper-2010-1.pdf
- **Exact locator used:** Abstract and §§2–6
- **Claim supported:** Reports large-scale tracing design, context propagation, sampling and operational experience.
- **Property relation:** P42, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S081 — X-Trace: A Pervasive Network Tracing Framework

- **Author/organisation:** Rodrigo Fonseca, George Porter, Randy H. Katz, Scott Shenker
- **Date/version:** 2007
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/nsdi-07/x-trace-pervasive-network-tracing-framework
- **Publisher locator:** https://www.usenix.org/conference/nsdi-07/x-trace-pervasive-network-tracing-framework
- **Exact locator used:** NSDI 2007, §§2–6
- **Claim supported:** Demonstrates cross-layer request tracing via propagated metadata.
- **Property relation:** P42, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S082 — Trace Context

- **Author/organisation:** World Wide Web Consortium
- **Date/version:** W3C Recommendation; current text accessed 2026-08-12
- **Class / epistemic label:** `STANDARD` / `STANDARD_OR_GUIDANCE_REQUIREMENT`
- **Stable locator:** https://www.w3.org/TR/trace-context/
- **Publisher locator:** https://www.w3.org/TR/trace-context/
- **Exact locator used:** §§2–4
- **Claim supported:** Standardises interoperable propagation of trace identity and vendor state.
- **Property relation:** P43
- **Contrary evidence / limit:** Correlation context does not prove complete capture, causality, current authority or semantic completion.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S083 — The Benefit of Hindsight: Tracing Edge-Cases in Distributed Systems

- **Author/organisation:** Lei Zhang, Zhiqiang Xie, Vaastav Anand, Ymir Vigfusson, Jonathan Mace
- **Date/version:** 2023
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/conference/nsdi23/presentation/zhang-lei
- **Publisher locator:** https://www.usenix.org/conference/nsdi23/presentation/zhang-lei
- **Exact locator used:** NSDI 2023, pp. 319–334, §§2–6
- **Claim supported:** Shows head sampling misses rare paths and tail sampling can lose coherent traces under overload; proposes retroactive tracing.
- **Property relation:** P42, P43
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S084 — Chaos Engineering

- **Author/organisation:** Ali Basiri et al.
- **Date/version:** 2016
- **Class / epistemic label:** `PEER_REVIEWED_PRACTICE_ARTICLE` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1109/MS.2016.60
- **Publisher locator:** doi:10.1109/MS.2016.60
- **Exact locator used:** IEEE Software 33(3), pp. 35–41
- **Claim supported:** Articulates controlled failure experimentation and blast-radius discipline.
- **Property relation:** P44
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S085 — Chaos Engineering: A Multi-Vocal Literature Review

- **Author/organisation:** Joshua Owotogbe et al.
- **Date/version:** 2025/2026 online publication
- **Class / epistemic label:** `SYSTEMATIC_MULTIVOCAL_REVIEW` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://doi.org/10.1145/3777375
- **Publisher locator:** doi:10.1145/3777375
- **Exact locator used:** ACM Computing Surveys 58(7), methods, taxonomy and gaps
- **Claim supported:** Synthesises academic/industrial evidence and identifies heterogeneous terminology and limited rigorous outcome evidence.
- **Property relation:** P44, P51
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S086 — Chaos Engineering in the Wild: Findings from GitHub

- **Author/organisation:** Joshua Owotogbe et al.
- **Date/version:** 2025
- **Class / epistemic label:** `EMPIRICAL_PREPRINT` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://arxiv.org/abs/2505.13654
- **Publisher locator:** https://arxiv.org/abs/2505.13654
- **Exact locator used:** arXiv:2505.13654, methods and results
- **Claim supported:** Studies 971 repositories; network/instance faults dominate while application-level faults are underrepresented.
- **Property relation:** P44, P51
- **Contrary evidence / limit:** Repository presence is a proxy for adoption, not proof of resilience improvement.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S087 — Elle: Inferring Isolation Anomalies from Experimental Observations

- **Author/organisation:** Kyle Kingsbury, Peter Alvaro
- **Date/version:** 2021
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/3465084.3467483
- **Publisher locator:** doi:10.1145/3465084.3467483
- **Exact locator used:** Model and evaluation sections
- **Claim supported:** Builds consistency histories and anomaly checking from observed transactions.
- **Property relation:** P07, P42, P44
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S088 — When Amnesia Strikes: Understanding and Reproducing Data Loss Bugs with Fault Injection

- **Author/organisation:** Maria Ramos et al.
- **Date/version:** 2024
- **Class / epistemic label:** `PEER_REVIEWED_EMPIRICAL_SYSTEMS` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://doi.org/10.14778/3681954.3681980
- **Publisher locator:** doi:10.14778/3681954.3681980
- **Exact locator used:** PVLDB 17(11), pp. 3017–3030
- **Claim supported:** Analyses and reproduces data-loss bugs caused by persistence-ordering and recovery assumptions.
- **Property relation:** P01, P35, P36, P44
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S089 — Rose: Reproducing External-Fault-Induced Failures in Distributed Systems with Lightweight Instrumentation

- **Author/organisation:** Sebastião Amaro, Pedro Fonseca, Miguel Matos
- **Date/version:** 2026
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://doi.org/10.1145/3767295.3803625
- **Publisher locator:** doi:10.1145/3767295.3803625
- **Exact locator used:** EuroSys 2026, pp. 2093–2108
- **Claim supported:** Reproduces production external-fault-induced failures using lightweight tracing and generated schedules.
- **Property relation:** P42, P44
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S090 — Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems

- **Author/organisation:** Ding Yuan et al.
- **Date/version:** 2014
- **Class / epistemic label:** `PEER_REVIEWED_EMPIRICAL_SYSTEMS` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://www.usenix.org/conference/osdi14/technical-sessions/presentation/yuan
- **Publisher locator:** https://www.usenix.org/conference/osdi14/technical-sessions/presentation/yuan
- **Exact locator used:** OSDI 2014, pp. 249–265
- **Claim supported:** Analyses production failures and reports many could have been exposed by targeted tests.
- **Property relation:** P01, P44
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S091 — Redundancy Does Not Imply Fault Tolerance: Analysis of Distributed Storage Reactions to Single Errors and Corruptions

- **Author/organisation:** Aishwarya Ganesan, Ramnatthan Alagappan, Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau
- **Date/version:** 2017
- **Class / epistemic label:** `PEER_REVIEWED_EMPIRICAL_SYSTEMS` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://www.usenix.org/conference/fast17/technical-sessions/presentation/ganesan
- **Publisher locator:** https://www.usenix.org/conference/fast17/technical-sessions/presentation/ganesan
- **Exact locator used:** FAST 2017, pp. 149–166
- **Claim supported:** Across eight storage systems, single file-system faults caused loss, corruption, unavailability or corruption propagation despite replication.
- **Property relation:** P01, P03, P08, P36, P44
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S092 — Aletheia: Automated Detection of Data Integrity Violations in Microservices

- **Author/organisation:** Mafalda Sofia Ferreira, João Ferreira Loff, João Garcia, Rodrigo Rodrigues
- **Date/version:** 2026
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://www.usenix.org/conference/osdi26/presentation/ferreira
- **Publisher locator:** https://www.usenix.org/conference/osdi26/presentation/ferreira
- **Exact locator used:** OSDI 2026, pp. 721–737
- **Claim supported:** Detects application-level data-integrity violations across partitioned microservice data stores.
- **Property relation:** P07, P21, P41, P47, P53
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S093 — Microservice Trade-Offs

- **Author/organisation:** Martin Fowler
- **Date/version:** 2015
- **Class / epistemic label:** `SERIOUS_PRACTITIONER_CRITIQUE` / `SOURCE_INTERPRETATION`
- **Stable locator:** https://martinfowler.com/articles/microservice-trade-offs.html
- **Publisher locator:** https://martinfowler.com/articles/microservice-trade-offs.html
- **Exact locator used:** Distribution, consistency and operational complexity sections
- **Claim supported:** Documents both deployment/fault-boundary benefits and distribution/consistency/operational costs.
- **Property relation:** P34, P45, P47, P51
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S094 — The Chubby Lock Service for Loosely-Coupled Distributed Systems

- **Author/organisation:** Mike Burrows
- **Date/version:** 2006
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf
- **Publisher locator:** https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf
- **Exact locator used:** OSDI 2006, pp. 335–350, §§2–5
- **Claim supported:** Documents a lease-based replicated lock/name service and lock-delay/failure semantics.
- **Property relation:** P10, P12, P13, P50
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S095 — How to Do Distributed Locking

- **Author/organisation:** Martin Kleppmann
- **Date/version:** 2016
- **Class / epistemic label:** `SERIOUS_TECHNICAL_CRITIQUE` / `CRITIQUE_OF_ASSUMPTION_OR_IMPLEMENTATION`
- **Stable locator:** https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
- **Publisher locator:** https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
- **Exact locator used:** Efficiency vs correctness; fencing tokens; GC pauses
- **Claim supported:** Explains delayed-client stale-writer hazards and resource-enforced fencing.
- **Property relation:** P05, P13, P50
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S096 — Practical Byzantine Fault Tolerance

- **Author/organisation:** Miguel Castro, Barbara Liskov
- **Date/version:** 1999
- **Class / epistemic label:** `PEER_REVIEWED_SYSTEMS` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://pmg.csail.mit.edu/papers/osdi99.pdf
- **Publisher locator:** https://pmg.csail.mit.edu/papers/osdi99.pdf
- **Exact locator used:** OSDI 1999, pp. 173–186, §§2–6
- **Claim supported:** Demonstrates Byzantine state-machine replication under authenticated communication and 3f+1 assumptions.
- **Property relation:** P52
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S097 — SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning

- **Author/organisation:** Edward Y. Chang, Longling Geng
- **Date/version:** 2026
- **Class / epistemic label:** `PEER_REVIEWED_DOMAIN_TRANSLATION` / `EMPIRICAL_OR_DOMAIN_FINDING`
- **Stable locator:** https://doi.org/10.14778/3750601.3750611
- **Publisher locator:** doi:10.14778/3750601.3750611
- **Exact locator used:** PVLDB 18, architecture and evaluation sections
- **Claim supported:** Translates context persistence, validation and saga-like safeguards into multi-agent LLM workflows.
- **Property relation:** P24, P25, P27, P53
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S098 — AgentChaos: Chaos Engineering for Agent Systems via Programmatic Fault Injection

- **Author/organisation:** Gou Tan et al.
- **Date/version:** 2026-08-07
- **Class / epistemic label:** `RECENT_PREPRINT_DOMAIN_TRANSLATION` / `UNVERIFIED`
- **Stable locator:** https://arxiv.org/abs/2608.06790
- **Publisher locator:** https://arxiv.org/abs/2608.06790
- **Exact locator used:** arXiv:2608.06790
- **Claim supported:** Applies crash, omission and value-fault injection to agent API responses.
- **Property relation:** P44, P53
- **Contrary evidence / limit:** Very recent preprint; independent replication and field transfer are not established.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S099 — How to Evaluate Distributed Coordination Systems?

- **Author/organisation:** Barış Turkkan et al.
- **Date/version:** 2024
- **Class / epistemic label:** `RECENT_REVIEW_PREPRINT` / `SOURCE_INTERPRETATION`
- **Stable locator:** https://arxiv.org/abs/2403.09445
- **Publisher locator:** https://arxiv.org/abs/2403.09445
- **Exact locator used:** arXiv:2403.09445, evaluation taxonomy
- **Claim supported:** Reviews benchmark dimensions for coordination services and identifies comparability gaps.
- **Property relation:** P01, P10, P11, P44, P51
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S100 — Algebraic Approaches to Distributed Data Systems

- **Author/organisation:** C. Power
- **Date/version:** 2025
- **Class / epistemic label:** `DOCTORAL_TECHNICAL_REPORT` / `SOURCE_ESTABLISHED`
- **Stable locator:** https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-103.pdf
- **Publisher locator:** https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-103.pdf
- **Exact locator used:** Berkeley EECS-2025-103, CRDT/consistency chapters
- **Claim supported:** Synthesises algebraic foundations for convergent replicated state and hybrid consistency.
- **Property relation:** P08, P09, P15, P16
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S101 — RFC 1: Host Software

- **Author/organisation:** Steve Crocker
- **Date/version:** 1969-04-07
- **Class / epistemic label:** `HISTORICAL_PRIMARY` / `HISTORICAL_INFERENCE`
- **Stable locator:** https://www.rfc-editor.org/info/rfc1/
- **Publisher locator:** RFC 1; doi:10.17487/RFC0001
- **Exact locator used:** RFC 1, full document
- **Claim supported:** Documents early ARPANET host software and the networked-computing context in which remote communication became an engineering substrate.
- **Property relation:** P01, P45
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

### S102 — Some Constraints and Tradeoffs in the Design of Network Communications

- **Author/organisation:** E. A. Akkoyunlu, K. Ekanadham, R. V. Huber
- **Date/version:** 1975
- **Class / epistemic label:** `PEER_REVIEWED_FOUNDATIONAL` / `FORMAL_OR_THEORETICAL_RESULT`
- **Stable locator:** https://doi.org/10.1145/800213.806523
- **Publisher locator:** doi:10.1145/800213.806523
- **Exact locator used:** SOSP 1975, pp. 67–74; coordinated-acknowledgement example on pp. 72–73
- **Claim supported:** Shows the limits of acknowledgement-based common knowledge under unreliable communication, the lineage later called Two Generals.
- **Property relation:** P02, P17, P21
- **Contrary evidence / limit:** No source-internal contrary result; limitations are recorded in the property ledger.
- **Access / OA:** 2026-08-12 / OPEN OR PUBLIC METADATA

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_TIMELINE

| Date | Development | Engineering significance | Lineage class | Sources |
| --- | --- | --- | --- | --- |
| 1969 | ARPANET host software context | RFC 1 records early host-to-host network software. This is context, not a complete distributed-systems methodology. | NETWORKING_IMPORT_OR_SHARED_ANCESTRY | [S101] |
| 1973 | Actor message-passing lineage | Actors make independently executing message-receiving entities explicit. | MESSAGE_DELIVERY_LINEAGE | [S001] |
| 1975 | Coordinated-acknowledgement limit | The paper later associated with the Two Generals problem shows that repeated acknowledgements cannot create certainty over an unreliable channel. | MESSAGE_DELIVERY_LINEAGE | [S102] |
| 1978 | Communicating Sequential Processes | CSP supplies a formal process/communication vocabulary distinct from shared-memory execution. | MESSAGE_DELIVERY_LINEAGE | [S002] |
| 1978 | Happens-before and logical clocks | Lamport separates causal partial order from physical clock order and arbitrary total order. | CAUSALITY_AND_TIME_LINEAGE | [S003] |
| 1978 | Transaction/log/recovery synthesis | Gray systematises transactions, logging, locking, recovery and communication uncertainty. | DISTRIBUTED_TRANSACTION_LINEAGE | [S017] |
| 1979 | Weighted quorum replication | Read/write voting makes quorum intersection relative to a configured vote population explicit. | REPLICATION_AND_CONSISTENCY_LINEAGE | [S015] |
| 1981 | Distributed concurrency control and nonblocking commit | Serialisability/concurrency-control survey and Skeen's commit analysis establish transaction and blocking lineages. | DISTRIBUTED_TRANSACTION_LINEAGE | [S018], [S020] |
| 1982 | Byzantine agreement | Arbitrary-fault agreement becomes a distinct formal model with explicit thresholds. | FAULT_TOLERANCE_LINEAGE | [S005] |
| 1984 | Clock-synchronisation limit; RPC; end-to-end argument | Physical-time bounds, remote-call retry ambiguity and effect-boundary reasoning become explicit. | HYBRID | [S034], [S043], [S044] |
| 1985 | Consistent snapshot and FLP | One lineage captures a coherent cut of distributed state; another proves deterministic consensus termination impossible in full asynchrony with one crash. | HYBRID | [S004], [S006] |
| 1987 | Sagas, epidemic repair and coordinated rollback recovery | Long-running compensation, anti-entropy and coherent recovery lines develop as separate responses to partial failure. | HYBRID | [S016], [S019], [S072] |
| 1988 | Partial synchrony, vector time and Viewstamped Replication | Timing assumptions, causal metadata and primary-copy view change mature in parallel. | HYBRID | [S007], [S010], [S032] |
| 1989 | Leases | Time-bounded authority/caching appears with explicit clock/network assumptions. | CONSENSUS_AND_MEMBERSHIP_LINEAGE | [S035] |
| 1990 | Linearizability and state-machine replication tutorial | Real-time object histories and deterministic replicated services become canonical correctness forms. | HYBRID | [S009], [S021] |
| 1991 | Causal and atomic group multicast | Virtual-synchrony/group communication links membership, causal order and atomic delivery. | CONSENSUS_AND_MEMBERSHIP_LINEAGE | [S013] |
| 1994 | Session guarantees | Read-your-writes and monotonic client-visible guarantees refine weak consistency. | REPLICATION_AND_CONSISTENCY_LINEAGE | [S029] |
| 1995–1999 | Isolation critique, weak-consistency theory, failure detectors, Paxos and PBFT | The field sharpens anomalies, asynchrony oracles, crash consensus and adversarial replication rather than one monolithic model. | HYBRID | [S022], [S023], [S008], [S011], [S096] |
| 2002 | CAP formalisation and rollback-recovery survey | Partition-case impossibility and systematic recovery taxonomy become stable reference points. | HYBRID | [S025], [S071] |
| 2006–2007 | Chubby, Dynamo and X-Trace | Production systems expose lock/lease services, highly available reconciliation and cross-layer observability. | CLOUD_NATIVE_TRANSLATION | [S037], [S081], [S094] |
| 2008–2009 | Serializable snapshot, eventual consistency and upgrade failure model | Isolation repair, consistency-spectrum practice and mixed-version risk become explicit. | HYBRID | [S024], [S028], [S077] |
| 2010–2011 | Dapper, Kafka, COPS and CRDTs | Tracing, durable logs, causal geo-storage and algebraic convergence mature as separate lineages. | HYBRID | [S030], [S031], [S045], [S080] |
| 2012 | Spanner, Calvin and CAP/PACELC clarification | Strong geo-transactions, deterministic ordering and more precise tradeoff framing coexist. | DISTRIBUTED_DATABASE_LINEAGE | [S026], [S027], [S036], [S040] |
| 2013–2015 | MillWheel/Dataflow/Flink; coordination avoidance; tail latency | Streaming semantics, event vs processing time, asynchronous snapshots, invariant-confluence and fan-out latency deepen operational design. | HYBRID | [S038], [S039], [S046], [S047], [S048], [S061] |
| 2014 | Raft and failure-test evidence | Understandability/reconfiguration receive attention while field studies show many distributed failures are testable. | HYBRID | [S012], [S090] |
| 2016–2018 | Chaos engineering, semantic fencing critique and overload control | Fault injection becomes explicit practice; stale-lock hazards and microservice overload control refine resilience. | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE | [S064], [S084], [S095] |
| 2017 | Replication is not automatic fault tolerance | Fault injection across eight storage systems shows replicated systems can lose or corrupt data under single storage faults. | FAULT_TOLERANCE_LINEAGE | [S091] |
| 2020–2023 | Durable serverless workflows, Boki/Netherite/ExoFlow, metastability and hindsight tracing | Durable execution, shared logs, workflow recovery semantics, overload feedback and rare-path tracing become active systems research. | HYBRID | [S050], [S051], [S052], [S053], [S054], [S062], [S063], [S083] |
| 2024 | Geo-transaction refinement and persistence/recovery fault injection | Recent work reduces commit latency while separately reproducing data-loss bugs from persistence assumptions. | HYBRID | [S041], [S042], [S088] |
| 2025 | Coordinated overload control and chaos-engineering evidence reviews | Rajomon and empirical/review work shift focus from tools to distributed policy, adoption patterns and evidence gaps. | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE | [S065], [S085], [S086] |
| 2025 outages | Configuration propagation and recovery remain common-mode hazards | Cloudflare's global file propagation incident supplies contemporary evidence that control/configuration and recovery load can be system-wide failure mechanisms. | CLOUD_NATIVE_TRANSLATION | [S076] |
| 2026 | Workflow correctness, speculative durability, microservice integrity and failure reproduction | Current research treats durable execution as necessary but not sufficient, reduces persistence cost, detects cross-service semantic violations and reproduces external-fault schedules. | HYBRID | [S055], [S056], [S089], [S092] |
| 2026 | Distributed AI/agentic translation | Agent workflows import durable state, saga/validation and fault-injection ideas, but operational transfer remains unresolved. | DOMAIN_SPECIFIC | [S097], [S098] |

The timeline is intentionally plural. ARPANET is treated as networked-computing context, not as the sole origin. Transactions, causality, agreement, replication, recovery, messaging and overload developed through partially independent literatures and later converged in production services.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_GENEALOGY

| Lineage | Genealogy | Transmission status | Surviving properties | Boundary | Sources |
| --- | --- | --- | --- | --- | --- |
| CAUSALITY_AND_TIME_LINEAGE | Lamport happens-before → vector/dependency clocks → causal multicast/storage → hybrid/bounded physical time and event-time processing. | Direct conceptual and citation transmission is strong from Lamport into vector clocks, causal consistency and snapshot/tracing work. | P04, P05, P06, P43 | Causality, total order, wall-clock order, freshness and semantic correctness remain distinct. | [S003], [S004], [S013], [S029], [S031], [S032], [S033], [S034], [S036], [S047] |
| REPLICATION_AND_CONSISTENCY_LINEAGE | Primary/backup and quorum voting → epidemic repair and session guarantees → Dynamo/geo-replication → CRDTs, causal systems and hybrid strong/weak access. | Direct within database/storage literature; CRDT and coordination-avoidance branches share ancestry but are not one method. | P03, P06, P07, P08, P09, P10, P14, P16 | Replica convergence does not establish semantic validity, current membership or independent failure domains. | [S015], [S016], [S029], [S030], [S031], [S037], [S038], [S039], [S091], [S100] |
| CONSENSUS_AND_MEMBERSHIP_LINEAGE | Agreement problems and virtual synchrony → Viewstamped Replication/Paxos → failure detectors and partial synchrony → Raft, reconfiguration and lock/lease services. | Direct protocol lineage with multiple independent families; Raft is not simply 'Paxos renamed', and VR precedes modern leader/log presentations. | P01, P10, P11, P12, P13, P37 | Consensus safety does not imply liveness, semantic validity, correct membership or resource fencing. | [S006], [S007], [S008], [S010], [S011], [S012], [S013], [S014], [S035], [S094] |
| DISTRIBUTED_TRANSACTION_LINEAGE | Atomicity/logging/concurrency control → 2PC and nonblocking commit → sagas → deterministic and geo-distributed transactions → bounded transaction-plus-compensation hybrids. | Direct database lineage; saga is a response to long duration/independent commits, not proof that atomic commit is obsolete. | P07, P15, P23, P24 | Rollback covers only participating resources; compensation is not necessarily inverse. | [S017], [S018], [S019], [S020], [S023], [S036], [S040], [S041], [S042], [S055] |
| MESSAGE_DELIVERY_LINEAGE | Early network communication limits and RPC retry semantics → durable messaging/logs → transactional messaging, offsets and workflow task delivery. | Direct on retransmission/duplicate suppression; later broker terms often broadened the claim beyond the original effect boundary. | P02, P17, P18, P19, P20, P21, P22 | Message delivery, processing, state transition and real-world effect are different nouns. | [S102], [S043], [S044], [S045], [S046], [S049], [S069] |
| FAULT_TOLERANCE_LINEAGE | Crash/arbitrary fault models → state-machine replication/snapshots/rollback recovery → empirical fault injection, recovery rehearsal and common-mode analysis. | Formal and systems branches converge on explicit assumptions but provide different evidence: proof inside a model versus field integration evidence. | P01, P03, P11, P35, P36, P37, P38, P44, P52 | Redundancy and proof do not establish recovery-path or implementation correctness automatically. | [S004], [S005], [S006], [S009], [S071], [S072], [S084], [S088], [S090], [S091], [S096] |
| DISTRIBUTED_DATABASE_LINEAGE | Distributed serialisability/quorums → isolation models → eventual/session/causal consistency → Dynamo, Spanner, HATs, Calvin and current geo-transaction systems. | Direct database lineage with persistent tension between invariant protection, latency and availability. | P06, P07, P08, P09, P10, P15, P16, P23, P39 | No consistency level is generally superior; the protected invariant and failure response decide. | [S015], [S020], [S022], [S023], [S025], [S027], [S029], [S036], [S037], [S038], [S039], [S040], [S041], [S042] |
| EVENT_LOG_AND_STREAMING_LINEAGE | Append-only transaction/event logs → Kafka-style partitioned logs → MillWheel/Dataflow/Flink processing and snapshots → replay-aware workflows. | Direct log/stream lineage; event sourcing as an application pattern is only one translation. | P04, P17, P20, P22, P25, P28, P29, P35, P36, P39 | Log order is partition-/sequencer-specific and replay does not automatically reconcile external effects. | [S017], [S045], [S046], [S047], [S048], [S054] |
| WORKFLOW_ORCHESTRATION_LINEAGE | Sagas and process managers → durable workflow histories/state machines → stateful serverless and exactly-once-DAG runtimes → current workflow-correctness research. | Sagas are direct ancestry; durable serverless work also imports log, state-machine and transaction ideas. | P24, P25, P26, P27, P28 | Durable replay is not external-world correctness; compensation and exactly-once remain boundary-scoped. | [S019], [S050], [S051], [S052], [S053], [S054], [S055], [S056] |
| OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE | Queueing/flow control and fault containment → service overload/cascading-failure practice → metastability research and coordinated microservice admission. | Imports queueing/control concepts while systems research adds dependency graphs, retries and recovery feedback. | P29, P30, P31, P32, P33, P34 | Queueing, retries and failover are dynamic load generators, not just reliability mechanisms. | [S061], [S062], [S063], [S064], [S065], [S066], [S067], [S068] |
| CLOUD_NATIVE_TRANSLATION | Service-oriented/microservice, multi-zone/region, serverless and control-plane architectures translate older properties into larger dynamic operational graphs. | Often documentary through industrial systems and postmortems; branding itself creates no guarantee. | P03, P25, P33, P34, P39, P40, P41, P44, P45, P46 | Microservices, Kubernetes, service meshes and regions are implementation contexts, not general properties. | [S036], [S050], [S063], [S065], [S073], [S075], [S076], [S092], [S093] |
| DOMAIN_SPECIFIC | Byzantine/adversarial replication and distributed AI/agent workflows branch from general distributed state but add distinct adversary or semantic-value failure. | BFT has a mature direct formal lineage; agentic translation is recent and not yet mature. | P52, P53 | Do not import adversarial or agent terminology when crash/common-mode/workflow failures are the actual problem. | [S005], [S096], [S097], [S098] |
| CONVERGENT_ENGINEERING | End-to-end arguments, single-writer/local transactions, fencing, capacity control and recovery evidence recur across otherwise distinct lineages. | Sometimes direct, sometimes independent convergence around the same failure mechanism. | P02, P13, P14, P18, P21, P27, P38, P41, P44, P45, P46 | Similarity is not asserted as one historical school; provenance is marked per property. | [S043], [S044], [S073], [S074], [S075], [S090], [S091], [S095] |

Where a source directly cites or builds on an earlier algorithm, the report treats that as documentary transmission. Where two traditions independently converge on the same mechanism—such as end-to-end effect verification or explicit failure models—the relationship is labelled `CONVERGENT_ENGINEERING`, not one asserted school.

## DISTRIBUTED_SYSTEMS_VS_CLOUD_NATIVE_CARICATURE

| Caricature | Evidence-backed correction | Classification | Properties | Sources |
| --- | --- | --- | --- | --- |
| CAP means choose any two of consistency, availability and partition tolerance. | The formal result is a partition/asynchrony impossibility for specific definitions; normal-operation latency/consistency and partition-recovery choices remain design decisions. | TEXTBOOK_SIMPLIFICATION | P01,P07,P15 | S025,S026,S027 |
| Exactly-once delivery means a business action happens exactly once. | Exactly-once claims are scoped to a transaction/runtime boundary; arbitrary external effects require identity, idempotency, participation, fencing or compensation. | DISTRIBUTED_SYSTEMS_CEREMONY | P17,P18,P19,P20,P21,P22,P49 | S043,S046,S049,S054,S055 |
| Retries are harmless. | Retries consume capacity, can race an unknown original, duplicate effects and create metastable overload; they require semantic safety, budget, backoff, jitter and deadline. | CRITIQUE_OF_ASSUMPTION_OR_IMPLEMENTATION | P02,P19,P32,P33 | S063,S067,S068,S069 |
| An ACK means the intended effect occurred. | An acknowledgement proves only its declared durable boundary; downstream and real-world postconditions remain separate. | RELIABILITY_OR_CONSISTENCY_PROXY | P21,P27 | S043,S044,S055 |
| A distributed lock makes concurrent work safe. | A delayed former holder may still act. Correctness-critical mutation needs resource-enforced fencing/version authority or semantic duplicate protection. | SUPERSEDED_IMPLEMENTATION_TECHNIQUE | P13,P50 | S035,S094,S095 |
| Majority quorum means the state is automatically current. | Quorum is configuration-, term- and state-position-specific; it also does not establish semantic validity or independent failure domains. | TEXTBOOK_SIMPLIFICATION | P03,P06,P10,P11 | S011,S012,S015 |
| A timestamp gives the true order. | Wall-clock time can be skewed and does not establish causal or semantic order; bounded-time designs must state uncertainty. | TEXTBOOK_SIMPLIFICATION | P04,P05 | S003,S034,S036 |
| Eventual consistency means the system will eventually be correct. | It may guarantee convergence under assumptions, not a convergence deadline or semantic validity of the converged state. | RELIABILITY_OR_CONSISTENCY_PROXY | P06,P07,P08,P09 | S028,S030,S037 |
| Microservices automatically improve resilience. | They can create useful ownership and fault boundaries, but also add remote uncertainty, distributed invariants and coordination debt. | CLOUD_TRANSLATION | P34,P45,P47 | S092,S093 |
| If a service is healthy, its dependencies are healthy. | Process liveness is not end-to-end readiness, current authority, capacity or an effect-path check. | RELIABILITY_OR_CONSISTENCY_PROXY | P41 | S064,S073,S075 |
| A queue absorbs overload. | A queue stores deferred work; without finite drain capacity, age/depth bounds, backpressure and consequence policy it hides and amplifies overload. | DISTRIBUTED_SYSTEMS_CEREMONY | P29,P30,P31,P33,P48 | S063,S066,S073 |
| Timeout means failure. | Timeout is a local policy threshold and can mean slow, partitioned, paused, committed-with-lost-reply or failed. | TEXTBOOK_SIMPLIFICATION | P02,P32 | S008,S044,S067 |
| Leader elected means split brain is impossible. | Old actors can resume and resources can accept stale writes unless current membership, state and fencing are enforced. | RELIABILITY_OR_CONSISTENCY_PROXY | P10,P12,P13,P37 | S010,S012,S095 |
| Idempotency means add a request ID. | Identity must be semantic and parameter-bound; the effect/result record and all downstream boundaries must share the closure or compensate. | DISTRIBUTED_SYSTEMS_CEREMONY | P18,P19,P20 | S044,S069 |
| A snapshot or backup means recovery works. | A consistent internal cut, compatible restore path, authority re-establishment and external-state reconciliation are distinct obligations. | RELIABILITY_OR_CONSISTENCY_PROXY | P35,P36,P37,P38 | S004,S071,S073,S074 |
| Chaos engineering means randomly kill things. | The transferable property is a bounded empirical challenge of one current failure/recovery claim with representative conditions, evidence and stop rules. | DISTRIBUTED_SYSTEMS_CEREMONY | P44,P51 | S084,S085,S086,S090 |
| Consensus on a value means the value is correct. | Consensus supplies agreement/order under a model; application semantic validity remains separate. | TEXTBOOK_SIMPLIFICATION | P11,P15 | S009,S011,S092 |
| Event sourcing makes the system auditable and recoverable. | Only if identity, schema evolution, replay determinism, log integrity and external-effect reconciliation are established. | DISTRIBUTED_SYSTEMS_CEREMONY | P20,P25,P28,P36,P39 | S045,S048,S054 |

The correction is not that every caricature is the exact opposite. Queues, locks, retries, microservices and exactly-once runtimes can be valuable. The error is promoting an implementation technique or scoped guarantee into a universal engineering property.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_PROPERTY_LEDGER

### Frozen population summary

| ID | Property | Lineage | Status | Trigger | Cheap path | Mature form | Primary sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | Explicit distributed failure, timing, network, storage and recovery model | FAULT_TOLERANCE_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE, CONVERGENT_ENGINEERING | FAILURE_MODEL_PROPERTY | Any correctness or completion claim spanning independently failing processes, stores, networks or administrative components. | A local call, local transaction or one durable process when no independent remote failure boundary is required. | An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path. | [S005], [S006], [S007], [S008], [S034], [S071], [S088], [S091] |
| P02 | Partial failure and unknown-outcome semantics | MESSAGE_DELIVERY_LINEAGE, FAULT_TOLERANCE_LINEAGE, CONVERGENT_ENGINEERING | STRONGLY_RETAINED | Remote mutation, distributed commit, task dispatch or external side effect whose response can be lost. | Local atomic mutation with a definitive return, or a harmless repeatable read. | Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it. | [S008], [S043], [S044], [S061], [S067] |
| P03 | Failure-domain independence and common-mode awareness | REPLICATION_AND_CONSISTENCY_LINEAGE, FAULT_TOLERANCE_LINEAGE, CLOUD_NATIVE_TRANSLATION | FAILURE_MODEL_PROPERTY | Replication, quorum, backup, multi-zone/region, control-plane or failover claim. | One durable copy plus tested backup where hot availability is unnecessary and consequence permits it. | Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths. | [S009], [S015], [S036], [S037], [S091] |
| P04 | Causal order distinguished from wall-clock and arbitrary total order | CAUSALITY_AND_TIME_LINEAGE, REPLICATION_AND_CONSISTENCY_LINEAGE | CAUSALITY_CURRENTNESS_PROPERTY | Correctness depends on whether one event could have influenced another, read-your-writes or dependency application. | Single-thread/local transaction order, or independent commutative operations with no causal consumer. | Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately. | [S003], [S013], [S031], [S032], [S033], [S047] |
| P05 | Bounded-clock use and time-based authority with uncertainty margin | CAUSALITY_AND_TIME_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | ASSUMPTION_SENSITIVE | Leases, TTLs, freshness SLAs, event-time windows or external-consistency designs. | Logical/causal clocks, non-time-based generations, or local timeout used only as a heuristic. | Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters. | [S003], [S033], [S034], [S035], [S036], [S070] |
| P06 | Currentness, freshness and session guarantees as explicit evidence | CAUSALITY_AND_TIME_LINEAGE, REPLICATION_AND_CONSISTENCY_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | CAUSALITY_CURRENTNESS_PROPERTY | Read result drives mutation, completion, failover, user-visible monotonicity or safety-sensitive decision. | Immutable content, best-effort analytics or explicitly stale cache with no authority claim. | A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown. | [S021], [S029], [S031], [S036], [S037] |
| P07 | Consistency level and isolation as an operation-scoped contract | DISTRIBUTED_TRANSACTION_LINEAGE, REPLICATION_AND_CONSISTENCY_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | REPLICATION_CONSISTENCY_PROPERTY | Shared mutable state with concurrent actors or replicas. | Single-thread/local immutable data, or commutative/invariant-confluent operations tolerating declared anomalies. | Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised. | [S020], [S021], [S022], [S023], [S024], [S025], [S027], [S029], [S031], [S039] |
| P08 | Semantic conflict resolution beyond replica byte convergence | REPLICATION_AND_CONSISTENCY_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | REPLICATION_CONSISTENCY_PROPERTY | Offline, geo or multi-writer state where concurrent progress is valuable. | One current writer, local transaction or coordination when the invariant is non-confluent. | Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination. | [S016], [S030], [S037], [S038], [S100] |
| P09 | Anti-entropy, convergence and repair with corruption/lag safeguards | REPLICATION_AND_CONSISTENCY_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | REPLICATION_CONSISTENCY_PROPERTY | Eventually or asynchronously replicated state with a lag/disconnected-replica path. | Synchronous replicated object with no lag path, or immutable artefact verified at write time. | Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation. | [S016], [S030], [S037] |
| P10 | Quorum validity bound to current membership and configuration | REPLICATION_AND_CONSISTENCY_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE | CONSENSUS_AUTHORITY_PROPERTY | Replicated decision, leader election, lock service or strong database read/write. | One current durable owner or local transaction. | A quorum certificate identifies current configuration, epoch and state position. | [S011], [S012], [S014], [S015], [S036], [S094] |
| P11 | Consensus safety separated from liveness and semantic validity | CONSENSUS_AND_MEMBERSHIP_LINEAGE, FAULT_TOLERANCE_LINEAGE | CONSENSUS_AUTHORITY_PROPERTY | Replicated exclusive decision or ordered log whose divergence would violate an invariant. | Local durable owner, commutative/partitionable state or explicit manual arbitration. | Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately. | [S006], [S007], [S008], [S009], [S010], [S011], [S012] |
| P12 | Versioned membership and safe reconfiguration | CONSENSUS_AND_MEMBERSHIP_LINEAGE, FAULT_TOLERANCE_LINEAGE | CONSENSUS_AUTHORITY_PROPERTY | Dynamic replica set, shard movement, autoscaling or disaster rebuild participating in authority. | Static single owner or whole-system offline replacement under an exclusive boundary. | Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff. | [S010], [S012], [S013], [S014], [S094] |
| P13 | Current mutation authority enforced by epochs or fencing | CONSENSUS_AND_MEMBERSHIP_LINEAGE, FAULT_TOLERANCE_LINEAGE, CONVERGENT_ENGINEERING | CONSENSUS_AUTHORITY_PROPERTY | Exclusive writer, task lease, distributed lock, failover, shard ownership or maintenance handoff. | Local mutex/process ownership; commutative operation; local transaction with version check. | Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised. | [S010], [S012], [S035], [S070], [S094] |
| P14 | Single-writer or local-transaction cheap path | REPLICATION_AND_CONSISTENCY_LINEAGE, DISTRIBUTED_TRANSACTION_LINEAGE, CONVERGENT_ENGINEERING | STRONGLY_RETAINED | Low write scale, central invariant, tightly coupled data, modest availability demand or easy recovery. | This property is the cheap path; distribution triggers only after a concrete consumer appears. | Start local or single-writer; distribute only the dimension with demonstrated need. | [S002], [S009], [S017], [S020], [S093] |
| P15 | Strong coordination for non-confluent invariants | DISTRIBUTED_TRANSACTION_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | STRONGLY_RETAINED | Demonstrated non-confluence, globally scarce resource or irreversible action requiring an exclusive current decision. | Independent commutative operations, ownership partitioning, escrowed budgets or one local owner. | Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation. | [S017], [S020], [S023], [S025], [S036], [S038], [S040], [S041], [S042] |
| P16 | Coordination avoidance for invariant-confluent, commutative or partitionable operations | REPLICATION_AND_CONSISTENCY_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE, CONVERGENT_ENGINEERING | CONTEXT_DEPENDENT | High-latency or partitioned environment where operation semantics support safe independent execution. | Non-confluent uniqueness/conservation/exclusive authority or irreversible global effects should coordinate instead. | Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones. | [S030], [S038], [S039], [S100] |
| P17 | Duplicate-aware delivery semantics | MESSAGE_DELIVERY_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE | DELIVERY_IDEMPOTENCY_PROPERTY | Asynchronous transfer, queue, event log, task dispatch or producer/consumer retry. | Direct local call/transaction or fire-and-forget telemetry where loss is accepted. | Name semantics at every boundary and independently close the business-effect boundary. | [S043], [S044], [S045], [S046], [S047], [S049] |
| P18 | End-to-end business-operation and effect identity | MESSAGE_DELIVERY_LINEAGE, WORKFLOW_ORCHESTRATION_LINEAGE, CONVERGENT_ENGINEERING | DELIVERY_IDEMPOTENCY_PROPERTY | Retriable mutation, long-running workflow, external irreversible action or cross-service transaction. | Pure read, locally atomic mutation with no reply-loss concern, or disposable telemetry. | Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent. | [S043], [S044], [S046], [S050], [S069] |
| P19 | Semantic idempotency, not request-ID ritual | MESSAGE_DELIVERY_LINEAGE, DISTRIBUTED_TRANSACTION_LINEAGE, WORKFLOW_ORCHESTRATION_LINEAGE | DELIVERY_IDEMPOTENCY_PROPERTY | Any mutation or activity that may be retried, redelivered, replayed or concurrently submitted. | Pure read, commutative accumulation with duplicate identity, or one local transaction. | The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay. | [S044], [S050], [S058], [S067], [S069] |
| P20 | Bounded deduplication and replay horizon | MESSAGE_DELIVERY_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE, WORKFLOW_ORCHESTRATION_LINEAGE | ASSUMPTION_SENSITIVE | Finite dedup cache, TTL, log retention, replay, delayed replica rejoin or disaster restore. | No retries/replay and bounded local execution, or effect is naturally harmless under repetition. | Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals. | [S030], [S045], [S046], [S049], [S069] |
| P21 | Acknowledgement separated from verified external effect | MESSAGE_DELIVERY_LINEAGE, DISTRIBUTED_TRANSACTION_LINEAGE, WORKFLOW_ORCHESTRATION_LINEAGE | DELIVERY_IDEMPOTENCY_PROPERTY | Multi-hop action, asynchronous processing, third-party/physical effect or workflow completion. | Single local transaction whose return covers the entire required state change. | Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated. | [S043], [S044], [S046], [S050], [S055] |
| P22 | Transactional messaging or outbox/inbox closure | MESSAGE_DELIVERY_LINEAGE, DISTRIBUTED_TRANSACTION_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE | DELIVERY_IDEMPOTENCY_PROPERTY | A local transaction must reliably cause or record an asynchronous message, or a consumed event must update state exactly once within the closure. | Direct local state change with no asynchronous notification requirement. | The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit. | [S043], [S045], [S046], [S048], [S049], [S050] |
| P23 | Explicit transactional boundary and atomic-commit choice | DISTRIBUTED_TRANSACTION_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | TRANSACTION_COMPENSATION_PROPERTY | A non-compensatable invariant requires all-or-nothing across multiple transactional participants. | One local transaction; or independently commit compensatable steps with a durable saga. | Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation. | [S017], [S018], [S020], [S023], [S036], [S040], [S041], [S042] |
| P24 | Compensation and forward recovery with semantic limits | DISTRIBUTED_TRANSACTION_LINEAGE, WORKFLOW_ORCHESTRATION_LINEAGE | TRANSACTION_COMPENSATION_PROPERTY | Long-running, cross-service or external workflow whose effects are compensatable or repairable but not globally atomic. | One atomic local/distributed transaction when the whole closure can and should commit together. | Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated. | [S019], [S050], [S055], [S097] |
| P25 | Durable workflow state as a recoverable distributed state machine | WORKFLOW_ORCHESTRATION_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE, FAULT_TOLERANCE_LINEAGE | WORKFLOW_STATE_PROPERTY | Long-running, multi-step, retrying or externally signalled work that must survive process/platform restart. | Synchronous local call/transaction whose whole lifetime fits one reliable execution boundary. | Workflow history is authoritative for orchestration, while external state is independently validated where required. | [S019], [S045], [S046], [S050], [S051], [S052], [S053], [S054], [S055], [S056] |
| P26 | Task ownership, lease expiry and duplicate-safe re-dispatch | WORKFLOW_ORCHESTRATION_LINEAGE, MESSAGE_DELIVERY_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE | WORKFLOW_STATE_PROPERTY | Task queue, visibility timeout, worker lease, heartbeat or automatic re-dispatch. | One local worker under a process-local lock, or harmless repeatable calculation with no effect. | Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation. | [S035], [S050], [S052], [S053], [S054], [S058] |
| P27 | Completion defined by durable state plus verified postcondition | WORKFLOW_ORCHESTRATION_LINEAGE, MESSAGE_DELIVERY_LINEAGE, CONVERGENT_ENGINEERING | WORKFLOW_STATE_PROPERTY | Completion drives user notification, billing, next workflow, resource release or irreversible decision. | Local transaction return covers the complete required postcondition. | DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN. | [S043], [S050], [S054], [S055], [S092] |
| P28 | Deterministic replay with explicit workflow/code version evolution | WORKFLOW_ORCHESTRATION_LINEAGE, HYBRID | ASSUMPTION_SENSITIVE | Replay-based durable workflow, event sourcing or state reconstruction across code versions. | Persist explicit current state without replay, or finish short-lived work before incompatible deployment. | History, code and schema versions are explicit; every deployed version can replay or migrate all live histories. | [S052], [S053], [S054], [S056], [S057], [S060] |
| P29 | Bounded queues with explicit work-age and capacity semantics | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE, HYBRID | OVERLOAD_BACKPRESSURE_PROPERTY | Asynchronous buffering between independently varying producer and consumer demand. | Direct synchronous flow with natural backpressure, or small fixed local buffer where overload consequence is acceptable. | Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour. | [S045], [S062], [S063], [S064], [S065], [S066] |
| P30 | Backpressure propagated to the source of demand | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE | OVERLOAD_BACKPRESSURE_PROPERTY | Producer can outpace consumer or fan-out multiplies work. | In-process bounded channel or naturally demand-driven iterator when no remote graph exists. | Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin. | [S047], [S062], [S063], [S064], [S065] |
| P31 | Admission control and load shedding with consequence policy | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, CLOUD_NATIVE_TRANSLATION, HYBRID | OVERLOAD_BACKPRESSURE_PROPERTY | Demand can exceed sustainable service or shared bottlenecks can saturate. | Fixed small system with hard external demand limit and no shared saturation risk. | Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate. | [S063], [S064], [S065], [S066] |
| P32 | Retry budgets, exponential backoff, jitter and deadline propagation | MESSAGE_DELIVERY_LINEAGE, OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE | OVERLOAD_BACKPRESSURE_PROPERTY | Transient failure can plausibly recover within the remaining deadline and retry is semantically safe. | No retry for permanent errors, expired work, non-idempotent effect without closure or already-overloaded dependency. | A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity. | [S061], [S063], [S066], [S067], [S068], [S069] |
| P33 | Metastable and cascading-overload containment | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, FAULT_TOLERANCE_LINEAGE, CLOUD_NATIVE_TRANSLATION | OVERLOAD_BACKPRESSURE_PROPERTY | Fan-out, shared bottleneck, retry/cache/failover/backlog loop or recovery surge can feed on itself. | Low-utilisation local system with no feedback path and trivial restart. | The failure model includes amplification and a tested path out of the degraded state. | [S062], [S063], [S064], [S065], [S066] |
| P34 | Dependency isolation and bulkheads with end-to-end verification | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, CLOUD_NATIVE_TRANSLATION | CONTEXT_DEPENDENT | Shared resource pool or dependency whose slowness/failure can block unrelated work. | One small dependency path with no shared-resource contention or acceptable full-stop behaviour. | Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour. | [S061], [S064], [S066], [S093] |
| P35 | Consistent distributed snapshot or checkpoint | FAULT_TOLERANCE_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE | RECOVERY_RECONSTITUTION_PROPERTY | Recovery, migration, rescaling or audit requires a cross-component state cut. | One local transactional snapshot or reconstructable stateless workers. | Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects. | [S004], [S017], [S048], [S071], [S072] |
| P36 | Replay and restore with external-state reconciliation | FAULT_TOLERANCE_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE, WORKFLOW_ORCHESTRATION_LINEAGE | RECOVERY_RECONSTITUTION_PROPERTY | Disaster restore, log replay, workflow history recovery or regional failover with external effects. | All state and effects are inside one local transactional restore boundary. | Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible. | [S017], [S046], [S048], [S050], [S053], [S056], [S071] |
| P37 | Failover re-establishes current authority before mutation | FAULT_TOLERANCE_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE, REPLICATION_AND_CONSISTENCY_LINEAGE | RECOVERY_RECONSTITUTION_PROPERTY | Leader/primary/site/region failover or ownership transfer after suspected failure. | Manual offline recovery with verified old owner stopped, or one local process restart without concurrent actor. | Failover completes only after authority fencing, current-state selection and post-failover validation. | [S010], [S012], [S035], [S036], [S094] |
| P38 | Tested restore and recovery-path evidence | FAULT_TOLERANCE_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE, CLOUD_NATIVE_TRANSLATION | STRONGLY_RETAINED | Any availability, durability, disaster recovery or rollback claim with material consequence. | Low-consequence disposable state that can be regenerated and whose loss is explicitly accepted. | Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals. | [S017], [S071], [S072] |
| P39 | Schema, wire protocol and event evolution under mixed versions | MESSAGE_DELIVERY_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE, CLOUD_NATIVE_TRANSLATION | RETAINED_IN_EVOLVED_FORM | Rolling deployment, long-lived event/log data, external clients, multiple regions or replayable workflow history. | Atomic offline upgrade of one local process/store with no concurrent old reader/writer and acceptable downtime. | Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier. | [S052], [S057], [S077], [S078], [S079] |
| P40 | Configuration and control-plane/data-plane currentness | CONSENSUS_AND_MEMBERSHIP_LINEAGE, CLOUD_NATIVE_TRANSLATION, CONVERGENT_ENGINEERING | RETAINED_IN_EVOLVED_FORM | Configuration affects routing, membership, schemas, resource limits, feature behaviour or authority across components. | Local static configuration changed atomically with the single process. | Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid. | [S014], [S077], [S079] |
| P41 | Current dependency topology and end-to-end readiness | OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, CLOUD_NATIVE_TRANSLATION, CONVERGENT_ENGINEERING | RETAINED_IN_EVOLVED_FORM | Service depends on remote components or dynamic routing/ownership. | Standalone local process with no remote effect path, where process liveness is the whole service. | Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy. | [S008], [S064], [S080], [S081] |
| P42 | Distributed observability treated as partial, sampled evidence | HYBRID, CLOUD_NATIVE_TRANSLATION | USEFUL_BUT_EASILY_GAMED | Diagnosis, currentness, completion, failure-model validation or causal reconstruction depends on distributed telemetry. | Local deterministic operation with direct authoritative state inspection. | Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available. | [S080], [S081], [S082], [S083] |
| P43 | Causal trace reconstruction and event provenance | CAUSALITY_AND_TIME_LINEAGE, HYBRID, CONVERGENT_ENGINEERING | RETAINED_IN_EVOLVED_FORM | Debugging, audit, recovery or completion requires cross-component reconstruction. | One local process with deterministic logs and no remote effects. | Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence. | [S003], [S004], [S013], [S032], [S080], [S081], [S082] |
| P44 | Hypothesis-bound fault injection and recovery challenge | FAULT_TOLERANCE_LINEAGE, CLOUD_NATIVE_TRANSLATION, CONVERGENT_ENGINEERING | USEFUL_BUT_EASILY_BUREAUCRATISED | Material claim about tolerance, failover, retry, restore, overload or state integrity whose assumptions can be safely challenged. | Static analysis/model checking/unit/integration test when the claim does not require distributed runtime failure; low-consequence system with no material uncertainty. | A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action. | [S084], [S085], [S086], [S087], [S088], [S089], [S090], [S091] |
| P45 | Distribution requires a named consumer and retains a cheap local path | CONVERGENT_ENGINEERING, CLOUD_NATIVE_TRANSLATION | STRONGLY_RETAINED | Independent scaling, fault containment, geographic latency, ownership/autonomy or deployment lifecycle demonstrably outweighs coordination cost. | Co-locate code/state, use in-process calls and local transactions, or one durable owner. | Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it. | [S002], [S043], [S044], [S093] |
| P46 | Retire distributed machinery when its coordination consumer disappears | CONVERGENT_ENGINEERING, CLOUD_NATIVE_TRANSLATION | RETAINED_IN_EVOLVED_FORM | Mechanism has no current decision, invariant, workload or failure-domain consumer. | Keep mechanism only when removal would reintroduce a demonstrated failure or violate a current requirement. | Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics. | [S043], [S077], [S079], [S093] |
| P47 | Microservices automatically improve resilience | CLOUD_NATIVE_TRANSLATION, ONLY_ANALOGOUS | REJECTED_OR_DISFAVOURED | Retain a service boundary only when it creates a real independently operable/failing/owned capability. | Modular monolith, local module or co-located state when independent runtime failure is unnecessary. | A service boundary is justified by a named lifecycle, ownership, scale or failure-containment property and bears its distributed obligations. | [S092], [S093] |
| P48 | A queue absorbs overload | EVENT_LOG_AND_STREAMING_LINEAGE, OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE, ONLY_ANALOGOUS | REJECTED_OR_DISFAVOURED | A queue is justified for decoupling, durability or burst smoothing only with a capacity/consequence model. | Synchronous backpressured call or small bounded local buffer. | Queue value is stated—durability, decoupling or bounded burst absorption—and completion capacity remains explicit. | [S045], [S062], [S063], [S066] |
| P49 | Exactly-once delivery implies the business action occurs exactly once | MESSAGE_DELIVERY_LINEAGE, EVENT_LOG_AND_STREAMING_LINEAGE, ONLY_ANALOGOUS | REJECTED_OR_DISFAVOURED | Retain platform exactly-once semantics only for operations inside its documented transaction boundary. | At-least-once plus semantic idempotency, or one local transaction, when simpler and sufficient. | Say exactly once only with the noun and boundary: record processing, state transition or verified effect under stated assumptions. | [S046], [S049], [S054], [S059] |
| P50 | Distributed lock alone makes concurrent mutation safe | CONSENSUS_AND_MEMBERSHIP_LINEAGE, FAULT_TOLERANCE_LINEAGE, ONLY_ANALOGOUS | SUPERSEDED_BY_STRONGER_FORM | A lock may still coordinate efficiency or reduce contention, but correctness-critical mutation requires stale rejection. | Local mutex/local transaction, one durable writer, commutative operation or resource-native compare-and-swap. | Lock is advisory evidence; the mutation is safe because stale generations cannot take effect. | [S035], [S070], [S094] |
| P51 | Named infrastructure or repeated ritual as an engineering property | CLOUD_NATIVE_TRANSLATION, ONLY_ANALOGOUS | CEREMONY_NOT_GENERAL_PROPERTY | Only when the artefact implements a named property whose payoff exceeds its own lifecycle cost. | Local code/state, existing transactional store, simpler ownership or targeted test. | Infrastructure is replaceable; the property, assumptions and evidence survive substitution. | [S085], [S086], [S093], [S099] |
| P52 | Byzantine/adversarial fault tolerance only under an explicit adversarial model | FAULT_TOLERANCE_LINEAGE, CONSENSUS_AND_MEMBERSHIP_LINEAGE, DOMAIN_SPECIFIC | DOMAIN_SPECIFIC | Actual threat model includes mutually distrustful or compromise-prone participants and the cost is justified. | Crash-fault consensus, single authority, audited replication or simpler integrity checks when adversarial participants are not a credible failure. | BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate. | [S005], [S096] |
| P53 | Distributed AI and agentic systems as a bounded domain translation | DOMAIN_SPECIFIC, WORKFLOW_ORCHESTRATION_LINEAGE, CLOUD_NATIVE_TRANSLATION | UNRESOLVED | Autonomous or multi-agent system coordinates persistent work or external effects across independently failing services. | One model call with human review and no durable/external effect; deterministic local program where suitable. | Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property. | [S092], [S097], [S098] |
| P54 | Default global consensus or coordination for all distributed state | CONSENSUS_AND_MEMBERSHIP_LINEAGE, DISTRIBUTED_DATABASE_LINEAGE, ONLY_ANALOGOUS | REJECTED_OR_DISFAVOURED | Strong coordination triggers only for an explicit invariant/current authority that cannot be preserved by local ownership, partitioning, commutativity, escrow or compensation. | Local transaction, single writer, CRDT/invariant-confluent operation, partitioned ownership or asynchronous durable handoff. | Coordinate only the state/effect closure whose independent execution would violate the named invariant. | [S025], [S027], [S038], [S039] |

### Full disposition cards

### P01 — Explicit distributed failure, timing, network, storage and recovery model

**Status:** `FAILURE_MODEL_PROPERTY`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Byzantine agreement (1982), asynchronous impossibility (1985), partial synchrony (1988) and failure-detector theory (1996).

**Original form.** State the process, communication, clock and storage faults an algorithm tolerates and the timing assumptions under which it progresses.

**Problem and distributed failure.** Protocol names are often repeated after the assumptions that make their guarantees true have been dropped. Crash, omission, delay, partition, corruption, clock and recovery faults are conflated; a proved algorithm is deployed outside its model.

**Failure prevented.** Invalid inference from algorithm identity to deployed safety, liveness, consistency or recoverability.

**Mechanism.** Attach every guarantee to an explicit model; check implementation primitives, failure domains and recovery transitions against it.

**Trigger.** Any correctness or completion claim spanning independently failing processes, stores, networks or administrative components.

**Cheap path / non-trigger.** A local call, local transaction or one durable process when no independent remote failure boundary is required.

**Dependencies and preconditions.** Known component boundary; declared synchrony; stable-storage semantics; restart behaviour; membership; clock assumptions; common-mode inventory.

**Failure/timing/consistency boundary.** Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable. The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout. No consistency claim is accepted without a named history/observation model and operation boundary.

**Authority/delivery/recovery/observability boundary.** Membership, configuration and ownership identity are explicit wherever they affect the claim. Loss, duplication, reordering and retry are either in scope or explicitly excluded. Restart, stable-storage, rollback and rejoin semantics are declared. Evidence distinguishes suspicion from established failure and reports coverage gaps.

**Payoff and consumer.** Prevents model-free folklore, focuses tests on the actual fault envelope and makes evidence comparable. Consumer: Architect, protocol implementer, operator, reviewer and consumer of a distributed guarantee.

**Known failure modes.**
- Storage corruption omitted
- Timing bound assumed but unmonitored
- Recovery changes membership outside the proof
- Common control plane defeats independence
- Implementation primitive is weaker than the model

**Important criticisms.**
- Models can be unrealistically clean
- Enumerating assumptions is not proof they hold
- Byzantine language can distract from ordinary crash/common-mode failures

**Evolution.** From generic 'node failure' to layered profiles covering process, network, clock, storage, restart, configuration, operator and common-mode coupling.

**Mature form.** An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.

**Ceremony boundary.** Using a protocol or topology label is ceremony; the retained property is the checked model.

**Evidence.** Primary: [S005], [S006], [S007], [S008], [S034], [S071], [S088], [S091]. Critical: [S090], [S099]. Empirical/outage: [S073], [S074], [S075], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should correlated operator/control-plane faults be represented without making the model intractable?

### P02 — Partial failure and unknown-outcome semantics

**Status:** `STRONGLY_RETAINED`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `VERY_HIGH`

**Historical origin.** RPC retransmission and end-to-end semantics, failure detectors and later retry/reconciliation practice.

**Original form.** A missing response means the caller lacks evidence about remote execution; it does not prove nonexecution.

**Problem and distributed failure.** One component can continue or commit while another is slow, paused, partitioned, restarted or unable to receive the reply. The caller times out after the remote effect may already have committed or may still be executing.

**Failure prevented.** Timeout-triggered duplicate action, abandoned committed work or unsafe failover.

**Mechanism.** Represent UNKNOWN/PENDING outcomes; query by stable operation identity; reconcile, retry safely or compensate; propagate deadlines separately.

**Trigger.** Remote mutation, distributed commit, task dispatch or external side effect whose response can be lost.

**Cheap path / non-trigger.** Local atomic mutation with a definitive return, or a harmless repeatable read.

**Dependencies and preconditions.** Stable operation identity, authoritative status/reconciliation interface, durable outcome state and duplicate-safe or compensatable effect.

**Failure/timing/consistency boundary.** Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable. The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout. No consistency claim is accepted without a named history/observation model and operation boundary.

**Authority/delivery/recovery/observability boundary.** Membership, configuration and ownership identity are explicit wherever they affect the claim. Loss, duplication, reordering and retry are either in scope or explicitly excluded. Restart, stable-storage, rollback and rejoin semantics are declared. Evidence distinguishes suspicion from established failure and reports coverage gaps.

**Payoff and consumer.** Makes epistemic uncertainty explicit and prevents timeout from becoming a false semantic verdict. Consumer: Caller, orchestrator, operator and business decision deciding whether to retry, wait or compensate.

**Known failure modes.**
- Retry races the original slow execution
- Cancellation stops waiting but not work
- Status record is lost with worker
- Operation identity reused for changed parameters
- Unknown is prematurely mapped to failed

**Important criticisms.**
- Unknown-state handling adds latency and durable state
- Some external effects cannot be queried or reversed
- Aggressive timeouts can create the uncertainty they detect

**Evolution.** From RPC retry rules to durable unknown states, semantic operation identity, deadline propagation and reconciliation.

**Mature form.** Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.

**Ceremony boundary.** Turning timeout into an error code is not the property.

**Evidence.** Primary: [S008], [S043], [S044], [S061], [S067]. Critical: [S006], [S095]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How long may an outcome remain unknown before policy must escalate or compensate?

### P03 — Failure-domain independence and common-mode awareness

**Status:** `FAILURE_MODEL_PROPERTY`  
**Lineage:** `REPLICATION_AND_CONSISTENCY_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Primary/backup and quorum replication, refined by geo-distributed placement and field studies of correlated failure.

**Original form.** Place redundant state and decision paths across failure domains independent for the failures being claimed.

**Problem and distributed failure.** Replicas share power, network, storage software, configuration, control plane, credentials, operator or region. A common cause removes or corrupts nominally redundant copies and the recovery/control path.

**Failure prevented.** Replica count being mistaken for independent availability or durability coverage.

**Mechanism.** Map physical and logical shared fate; place replicas/witnesses/control paths accordingly; bound corruption propagation and test correlated failure.

**Trigger.** Replication, quorum, backup, multi-zone/region, control-plane or failover claim.

**Cheap path / non-trigger.** One durable copy plus tested backup where hot availability is unnecessary and consequence permits it.

**Dependencies and preconditions.** Failure-domain inventory, placement evidence, recovery-path independence, integrity checks and out-of-band access.

**Failure/timing/consistency boundary.** Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable. The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout. No consistency claim is accepted without a named history/observation model and operation boundary.

**Authority/delivery/recovery/observability boundary.** Membership, configuration and ownership identity are explicit wherever they affect the claim. Loss, duplication, reordering and retry are either in scope or explicitly excluded. Restart, stable-storage, rollback and rejoin semantics are declared. Evidence distinguishes suspicion from established failure and reports coverage gaps.

**Payoff and consumer.** Turns 'N replicas' into a defensible fault-coverage claim and reveals shared recovery dependencies. Consumer: Storage/platform owner, resilience architect, incident commander and recovery planner.

**Known failure modes.**
- Bad configuration reaches all replicas
- Repair propagates corruption
- Witness shares failed network
- Recovery credentials/DNS depend on failed system
- Administrative labels overstate independence

**Important criticisms.**
- Perfect independence is impossible
- Cross-region independence costs latency and complexity
- Provider labels are not empirical proof

**Evolution.** From hardware redundancy to multi-layer common-mode analysis including software, configuration, control and operator.

**Mature form.** Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.

**Ceremony boundary.** Three replicas or three zones is ceremony without a shared-fate model.

**Evidence.** Primary: [S009], [S015], [S036], [S037], [S091]. Critical: [S073], [S074], [S075], [S076]. Empirical/outage: [S073], [S074], [S075], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can tenants independently verify cloud failure-domain claims?

### P04 — Causal order distinguished from wall-clock and arbitrary total order

**Status:** `CAUSALITY_CURRENTNESS_PROPERTY`  
**Lineage:** `CAUSALITY_AND_TIME_LINEAGE`, `REPLICATION_AND_CONSISTENCY_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Lamport's happens-before relation (1978), vector clocks, causal multicast and causal consistency.

**Original form.** Represent causal precedence and concurrency without assuming a perfect global clock.

**Problem and distributed failure.** Wall-clock skew, log merge order or arbitrary tie-breaking reverses or invents dependencies. Events are delayed, reordered and concurrent across independently progressing processes.

**Failure prevented.** Conflict resolution, replay, audit or a decision using an order that does not preserve the relation it needs.

**Mechanism.** Use logical/vector/dependency clocks, causal delivery or a deliberately authoritative sequencer; preserve concurrency instead of fabricating a winner.

**Trigger.** Correctness depends on whether one event could have influenced another, read-your-writes or dependency application.

**Cheap path / non-trigger.** Single-thread/local transaction order, or independent commutative operations with no causal consumer.

**Dependencies and preconditions.** Stable event identity, propagation of dependency metadata, stated sequencer/log semantics and retention of causal context.

**Failure/timing/consistency boundary.** Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation. No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design. Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation.

**Authority/delivery/recovery/observability boundary.** Sequencers, leases and readers identify the current term/configuration where that affects currentness. Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order. Replay and failover preserve required dependencies and do not present older state as newer without signalling. Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.

**Payoff and consumer.** Prevents false temporal inference and enables safe concurrency where total coordination is unnecessary. Consumer: Database designer, event processor, workflow author, auditor and debugger.

**Known failure modes.**
- Dependency metadata dropped at a boundary
- Vector metadata pruned unsafely
- Log order mistaken for real-world causality
- LWW chooses wrong semantic winner
- External-world causality is unobserved

**Important criticisms.**
- Causal metadata can grow
- Causality does not supply semantic conflict resolution
- Some invariants genuinely require total order

**Evolution.** From wall-clock/process-local sequence to explicit partial order, causal/session guarantees and hybrid logical time.

**Mature form.** Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.

**Ceremony boundary.** Adding a timestamp or correlation ID is not causal engineering.

**Evidence.** Primary: [S003], [S013], [S031], [S032], [S033], [S047]. Critical: [S034], [S083]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can causal metadata be bounded without silently losing dependencies?

### P05 — Bounded-clock use and time-based authority with uncertainty margin

**Status:** `ASSUMPTION_SENSITIVE`  
**Lineage:** `CAUSALITY_AND_TIME_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** Clock-synchronisation bounds, leases and systems using bounded time uncertainty.

**Original form.** Use physical time only with a declared uncertainty/drift model; never infer exact global order or current authority from local time alone.

**Problem and distributed failure.** Clock drift, jumps, VM/GC pauses and uncertain network delay cause overlapping perceived leases or false freshness. Different nodes observe incompatible time and liveness while delayed actors remain able to execute.

**Failure prevented.** Stale owners mutating after handoff, premature TTL/dedup expiry and false timestamp order.

**Mechanism.** Use monotonic clocks for durations, uncertainty intervals for ordering, conservative expiry, and resource-enforced generations/fencing.

**Trigger.** Leases, TTLs, freshness SLAs, event-time windows or external-consistency designs.

**Cheap path / non-trigger.** Logical/causal clocks, non-time-based generations, or local timeout used only as a heuristic.

**Dependencies and preconditions.** Measured bound, uncertainty excursion policy, pause/restart handling, lease issuer identity and fenced effect boundary.

**Failure/timing/consistency boundary.** Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation. No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design. Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation.

**Authority/delivery/recovery/observability boundary.** Sequencers, leases and readers identify the current term/configuration where that affects currentness. Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order. Replay and failover preserve required dependencies and do not present older state as newer without signalling. Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.

**Payoff and consumer.** Allows low-latency time-based mechanisms while retaining explicit safety margins. Consumer: Database, lock/lease service, scheduler, cache and operator.

**Known failure modes.**
- NTP step or long pause violates bound
- Monotonic clock resets on restart
- Old partition renews/acts
- Uncertainty exceeded unnoticed
- TTL treated as proof of nonexecution

**Important criticisms.**
- Conservative margins reduce availability
- Clock infrastructure is common-mode
- Bounded time does not create semantic causality

**Evolution.** From timestamp folklore to intervals, monotonic duration clocks, hybrid clocks and fencing-backed leases.

**Mature form.** Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.

**Ceremony boundary.** A timestamp or lease API without uncertainty and stale-writer rejection is ceremony.

**Evidence.** Primary: [S003], [S033], [S034], [S035], [S036], [S070]. Critical: [S095]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should the system degrade when clock uncertainty exceeds the design bound?

### P06 — Currentness, freshness and session guarantees as explicit evidence

**Status:** `CAUSALITY_CURRENTNESS_PROPERTY`  
**Lineage:** `CAUSALITY_AND_TIME_LINEAGE`, `REPLICATION_AND_CONSISTENCY_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Session guarantees, linearizability, causal consistency and geo-replicated database practice.

**Original form.** Specify what a reader may observe relative to its own writes, causal dependencies, real time and a staleness bound.

**Problem and distributed failure.** A reachable replica is alive but lagging, in an old configuration or unable to substantiate currentness. Replica lag, failover and partition let a reachable component serve stale or divergent state.

**Failure prevented.** Stale reads triggering duplicate action, apparent rollback, unsafe failover or wrong decisions.

**Mechanism.** Expose operation-scoped consistency/session/freshness contract; carry version/dependency evidence; route, block, fail or mark uncertainty when currentness is unproven.

**Trigger.** Read result drives mutation, completion, failover, user-visible monotonicity or safety-sensitive decision.

**Cheap path / non-trigger.** Immutable content, best-effort analytics or explicitly stale cache with no authority claim.

**Dependencies and preconditions.** Version/commit index or causal token, replica lag and membership knowledge, retention and consumer-defined tolerance.

**Failure/timing/consistency boundary.** Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation. No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design. Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation.

**Authority/delivery/recovery/observability boundary.** Sequencers, leases and readers identify the current term/configuration where that affects currentness. Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order. Replay and failover preserve required dependencies and do not present older state as newer without signalling. Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.

**Payoff and consumer.** Separates reachability from authoritative currentness and prevents stale-but-green state from driving action. Consumer: Application consumer, user session, operator, workflow and failover controller.

**Known failure modes.**
- Lag metric is stale or clock-skewed
- Session token lost across service boundary
- Failover chooses older branch
- Read quorum uses old membership
- Cache age mistaken for source authority

**Important criticisms.**
- Stronger currentness costs latency/availability
- Freshness telemetry is delayed
- Many reads do not need the strongest model

**Evolution.** From consistent/eventual binaries to per-operation session, causal, linearizable and bounded-staleness contracts.

**Mature form.** A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.

**Ceremony boundary.** A green replica or recent timestamp is not currentness evidence by itself.

**Evidence.** Primary: [S021], [S029], [S031], [S036], [S037]. Critical: [S025], [S027], [S083]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- Can bounded staleness be certified during prolonged partition without reducing availability?

### P07 — Consistency level and isolation as an operation-scoped contract

**Status:** `REPLICATION_CONSISTENCY_PROPERTY`  
**Lineage:** `DISTRIBUTED_TRANSACTION_LINEAGE`, `REPLICATION_AND_CONSISTENCY_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Serialisability and concurrency-control theory, linearizability, isolation critique, CAP/PACELC, causal and highly available transactions.

**Original form.** Name the history property, operation boundary and failure behaviour instead of saying 'strong', 'ACID' or 'eventual'.

**Problem and distributed failure.** Different models prevent different anomalies and impose different latency, availability and coordination costs. Concurrent operations and replicas produce histories whose anomalies are hidden by vague labels.

**Failure prevented.** Application invariants being assumed protected by a weaker model, or stronger semantics bought without a consumer.

**Mechanism.** Derive the model from invariants and observations; document permitted anomalies; test histories and failure cases.

**Trigger.** Shared mutable state with concurrent actors or replicas.

**Cheap path / non-trigger.** Single-thread/local immutable data, or commutative/invariant-confluent operations tolerating declared anomalies.

**Dependencies and preconditions.** Operation/transaction boundaries, anomaly model, client/session semantics, implementation verification and failure response.

**Failure/timing/consistency boundary.** Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership. Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement. The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.

**Authority/delivery/recovery/observability boundary.** Replica set, writer authority and configuration identity are current and durable. Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. Catch-up, repair, rejoin, compaction and corruption handling are tested. Lag, divergence, repair source, membership and invariant checks are observable.

**Payoff and consumer.** Aligns coordination cost with the invariant and blocks consistency-by-brand. Consumer: Application/data designer, database owner, reviewer and consumer.

**Known failure modes.**
- Snapshot-isolation write skew
- External effect not covered by DB consistency
- Failover violates session guarantee
- Vendor label differs from definition
- Converged state violates invariant

**Important criticisms.**
- Formal labels are hard to apply
- History checking samples workloads
- Stronger consistency can reduce availability without protecting a real invariant

**Evolution.** From ACID/BASE slogans to named per-operation models, session guarantees, invariant-based selection and anomaly checks.

**Mature form.** Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.

**Ceremony boundary.** Selecting a product tier labelled 'strong' is ceremony.

**Evidence.** Primary: [S020], [S021], [S022], [S023], [S024], [S025], [S027], [S029], [S031], [S039]. Critical: [S087], [S092]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should application invariants be translated into checkable consistency obligations across systems?

### P08 — Semantic conflict resolution beyond replica byte convergence

**Status:** `REPLICATION_CONSISTENCY_PROPERTY`  
**Lineage:** `REPLICATION_AND_CONSISTENCY_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** Epidemic replication, Dynamo reconciliation, CRDTs and invariant-confluence/hybrid designs.

**Original form.** Concurrent updates must merge according to operation semantics and invariants, not merely produce identical bytes.

**Problem and distributed failure.** Partitioned or multi-writer replicas diverge; deterministic convergence can still produce a business-invalid state. Concurrent writes, delayed replicas and reordering produce conflicts whose resolution is application-sensitive.

**Failure prevented.** Lost updates, resurrected deletes, negative inventory, broken uniqueness or arbitrary LWW decisions.

**Mechanism.** Use application-specific merge, CRDT with stated algebraic conditions, escrow/reservation, or coordinate the non-confluent invariant.

**Trigger.** Offline, geo or multi-writer state where concurrent progress is valuable.

**Cheap path / non-trigger.** One current writer, local transaction or coordination when the invariant is non-confluent.

**Dependencies and preconditions.** Operation algebra, identity/tombstone policy, causal metadata, invariant argument and compaction horizon.

**Failure/timing/consistency boundary.** Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership. Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement. The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.

**Authority/delivery/recovery/observability boundary.** Replica set, writer authority and configuration identity are current and durable. Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. Catch-up, repair, rejoin, compaction and corruption handling are tested. Lag, divergence, repair source, membership and invariant checks are observable.

**Payoff and consumer.** Permits available multi-writer progress only where merge semantics are defensible. Consumer: Data-type/application owner and replication layer.

**Known failure modes.**
- LWW loses causally important update
- Tombstone collected before delayed replica returns
- CRDT converges to invalid state
- Schema change alters merge semantics
- Identity collision merges different intents

**Important criticisms.**
- CRDTs do not solve arbitrary invariants
- Metadata/tombstones cost storage
- Middleware often lacks domain semantics

**Evolution.** From syntactic reconciliation to algebraic convergence plus separate semantic-invariant preservation and selective coordination.

**Mature form.** Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.

**Ceremony boundary.** 'Eventually all replicas match' is not the property if the matched state is wrong.

**Evidence.** Primary: [S016], [S030], [S037], [S038], [S100]. Critical: [S091], [S092]. Empirical/outage: [S091].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can merge invariants survive schema and operation evolution?

### P09 — Anti-entropy, convergence and repair with corruption/lag safeguards

**Status:** `REPLICATION_CONSISTENCY_PROPERTY`  
**Lineage:** `REPLICATION_AND_CONSISTENCY_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** Epidemic database maintenance, read repair/anti-entropy, log catch-up and CRDT replication.

**Original form.** Detect and repair divergence after disconnection or partial write without blindly spreading bad state.

**Problem and distributed failure.** Replicas remain stale indefinitely; repair selects an obsolete/corrupt source or overloads foreground work. Long-disconnected or corrupted replicas rejoin and exchange state under uncertain currentness.

**Failure prevented.** Silent stale failover, data loss, resurrection or corruption propagation.

**Mechanism.** Use version/digest comparison, authorised source selection, integrity/semantic validation, rate-limited repair and guarded rejoin.

**Trigger.** Eventually or asynchronously replicated state with a lag/disconnected-replica path.

**Cheap path / non-trigger.** Synchronous replicated object with no lag path, or immutable artefact verified at write time.

**Dependencies and preconditions.** Stable identity/version, current membership, repair-source policy, integrity checks, capacity budget and tombstone horizon.

**Failure/timing/consistency boundary.** Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership. Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement. The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.

**Authority/delivery/recovery/observability boundary.** Replica set, writer authority and configuration identity are current and durable. Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. Catch-up, repair, rejoin, compaction and corruption handling are tested. Lag, divergence, repair source, membership and invariant checks are observable.

**Payoff and consumer.** Restores intended redundancy and consistency without turning repair into a new failure amplifier. Consumer: Storage/replication operator and failover controller.

**Known failure modes.**
- Read repair copies corruption
- Repair saturates foreground capacity
- Replica catches up from stale source
- Deleted data resurrects
- Obsolete member rejoins

**Important criticisms.**
- No inherent convergence deadline
- Checksums show difference, not correct source
- Repair can create metastable overload

**Evolution.** From blind background copying to fenced, integrity-aware, capacity-bounded repair workflows.

**Mature form.** Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.

**Ceremony boundary.** Running a periodic repair command is ceremony unless authority and result are established.

**Evidence.** Primary: [S016], [S030], [S037]. Critical: [S063], [S091]. Empirical/outage: [S091].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How is the correct source selected under divergent memberships?

### P10 — Quorum validity bound to current membership and configuration

**Status:** `CONSENSUS_AUTHORITY_PROPERTY`  
**Lineage:** `REPLICATION_AND_CONSISTENCY_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Weighted voting, Paxos-family quorums, consensus and strongly consistent databases.

**Original form.** An intersecting decision set is meaningful only relative to the same legitimate configuration and state/version.

**Problem and distributed failure.** A numeric majority forms from the wrong, stale, duplicated or non-independent member set. Partitions and reconfiguration allow conflicting views of who may vote or serve state.

**Failure prevented.** Two configurations each forming majority, stale state winning or restored identity voting twice.

**Mechanism.** Version membership; bind votes to term/configuration/log position; preserve intersection through reconfiguration; validate durable identities and placement.

**Trigger.** Replicated decision, leader election, lock service or strong database read/write.

**Cheap path / non-trigger.** One current durable owner or local transaction.

**Dependencies and preconditions.** Authoritative configuration identity, unique durable member ID, persisted vote/log and proven transitional overlap.

**Failure/timing/consistency boundary.** Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults. Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum. Agreement/order does not itself establish application semantic validity.

**Authority/delivery/recovery/observability boundary.** Terms, views, ballots, configurations and durable member identity bind every decision and mutation. Protocol messages are term/configuration bound and stale messages are rejected. Votes, log position, snapshots and configuration state survive restart without rollback of authority. Current term, configuration, quorum and commit position can be reconstructed.

**Payoff and consumer.** Prevents majority folklore from masking split authority. Consumer: Consensus/database implementer, operator and failover controller.

**Known failure modes.**
- Split configuration
- Reused node identity
- Witness shares failed domain
- Read quorum returns stale state
- Durable vote/log rolled back

**Important criticisms.**
- Larger quorums reduce availability and raise latency
- Dynamic reconfiguration is difficult
- Intersection does not validate application values

**Evolution.** From static vote counts to configuration-indexed quorum certificates and safe reconfiguration.

**Mature form.** A quorum certificate identifies current configuration, epoch and state position.

**Ceremony boundary.** 'Three nodes, therefore safe' is ceremony.

**Evidence.** Primary: [S011], [S012], [S014], [S015], [S036], [S094]. Critical: [S099]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should decommissioned identities be prevented from reappearing after restore?

### P11 — Consensus safety separated from liveness and semantic validity

**Status:** `CONSENSUS_AUTHORITY_PROPERTY`  
**Lineage:** `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** FLP, partial synchrony, failure detectors, state-machine replication, Viewstamped Replication, Paxos and Raft.

**Original form.** Agreement/non-divergence, progress/termination and validity of the chosen value are distinct obligations.

**Problem and distributed failure.** A protocol remains safe but unavailable, or all replicas agree on a syntactically valid yet semantically wrong value. Partitions, slow links and failures prevent progress while agreement remains intact; agreement can choose bad input.

**Failure prevented.** Unsafe manual fail-open, false continuous-availability claim or consensus-as-business-oracle.

**Mechanism.** State safety invariant, liveness assumptions and input/application validity separately; expose quorum loss rather than violating safety.

**Trigger.** Replicated exclusive decision or ordered log whose divergence would violate an invariant.

**Cheap path / non-trigger.** Local durable owner, commutative/partitionable state or explicit manual arbitration.

**Dependencies and preconditions.** Fault/timing model, durable vote/log, membership, deterministic application and input validation.

**Failure/timing/consistency boundary.** Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults. Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum. Agreement/order does not itself establish application semantic validity.

**Authority/delivery/recovery/observability boundary.** Terms, views, ballots, configurations and durable member identity bind every decision and mutation. Protocol messages are term/configuration bound and stale messages are rejected. Votes, log position, snapshots and configuration state survive restart without rollback of authority. Current term, configuration, quorum and commit position can be reconstructed.

**Payoff and consumer.** Provides replicated decisions without pretending to guarantee continuous availability or semantic correctness. Consumer: Protocol implementer, state-machine validator and operator.

**Known failure modes.**
- Liveness stalls under partition
- Manual dual-primary violates safety
- Nondeterministic state machine
- Invalid command agreed
- Snapshot omits term/vote metadata

**Important criticisms.**
- Consensus is overused
- Leader implementations can bottleneck
- Proofs may not cover storage/reconfiguration/integration bugs

**Evolution.** From 'elect a leader' folklore to separate safety, liveness, validity and implementation evidence.

**Mature form.** Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.

**Ceremony boundary.** A leader dashboard is not the property.

**Evidence.** Primary: [S006], [S007], [S008], [S009], [S010], [S011], [S012]. Critical: [S090], [S099]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can deployments continuously check that storage and membership still satisfy the proof model?

### P12 — Versioned membership and safe reconfiguration

**Status:** `CONSENSUS_AUTHORITY_PROPERTY`  
**Lineage:** `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Virtual synchrony/views, Viewstamped Replication, Paxos/Raft reconfiguration and Vertical Paxos.

**Original form.** Membership change is a distributed state transition requiring continuity of authority and quorum intersection.

**Problem and distributed failure.** Nodes join, leave, rebuild or move while old messages, leaders and configurations remain live. Multiple configurations remain actionable across partition, delayed messaging or restore.

**Failure prevented.** Split brain, two quorums, data loss during replacement or resurrected stale member.

**Mechanism.** Use configuration versions/epochs, joint/overlap or equivalent transition, catch-up before voting and retirement/fencing of old identities.

**Trigger.** Dynamic replica set, shard movement, autoscaling or disaster rebuild participating in authority.

**Cheap path / non-trigger.** Static single owner or whole-system offline replacement under an exclusive boundary.

**Dependencies and preconditions.** Unique durable identity, configuration log, state transfer/catch-up, overlap proof and operator-visible transition.

**Failure/timing/consistency boundary.** Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults. Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum. Agreement/order does not itself establish application semantic validity.

**Authority/delivery/recovery/observability boundary.** Terms, views, ballots, configurations and durable member identity bind every decision and mutation. Protocol messages are term/configuration bound and stale messages are rejected. Votes, log position, snapshots and configuration state survive restart without rollback of authority. Current term, configuration, quorum and commit position can be reconstructed.

**Payoff and consumer.** Allows elasticity and maintenance without invalidating quorum/consensus assumptions. Consumer: Cluster manager, operator and shard/replica controller.

**Known failure modes.**
- Too many members removed at once
- Joining member votes before catch-up
- Old identity reused
- Config state restored behind data
- Control and data planes disagree

**Important criticisms.**
- Safe reconfiguration can reduce availability
- Tooling often bypasses protocol
- Proofs assume reliable identity/storage

**Evolution.** From static groups to logged, epoch-bound, jointly safe reconfiguration.

**Mature form.** Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.

**Ceremony boundary.** Editing a node list or scaling a controller is not safe reconfiguration.

**Evidence.** Primary: [S010], [S012], [S013], [S014], [S094]. Critical: [S099]. Empirical/outage: [S073], [S075].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should data and membership logs be reconciled when restored independently?

### P13 — Current mutation authority enforced by epochs or fencing

**Status:** `CONSENSUS_AUTHORITY_PROPERTY`  
**Lineage:** `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Views, terms, ballots, lease-based lock services and fencing-token practice.

**Original form.** Once-valid leadership, lock or lease must not permit mutation after authority transfers.

**Problem and distributed failure.** An old leader or worker pauses/partitions, a new owner is chosen, then the old actor resumes. Stale actors remain live and delayed writes arrive after handoff.

**Failure prevented.** Split-brain mutation, duplicate external action, corruption during failover or concurrent maintenance.

**Mechanism.** Issue a monotone generation/epoch; attach it to each mutation; protected resource atomically rejects stale generations.

**Trigger.** Exclusive writer, task lease, distributed lock, failover, shard ownership or maintenance handoff.

**Cheap path / non-trigger.** Local mutex/process ownership; commutative operation; local transaction with version check.

**Dependencies and preconditions.** Durable monotone generation, resource-side compare/reject, ownership-transfer protocol and effect identity.

**Failure/timing/consistency boundary.** Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults. Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum. Agreement/order does not itself establish application semantic validity.

**Authority/delivery/recovery/observability boundary.** Terms, views, ballots, configurations and durable member identity bind every decision and mutation. Protocol messages are term/configuration bound and stale messages are rejected. Votes, log position, snapshots and configuration state survive restart without rollback of authority. Current term, configuration, quorum and commit position can be reconstructed.

**Payoff and consumer.** Converts advisory ownership into enforceable non-stale mutation safety. Consumer: Lock service, scheduler, storage/API owner and failover controller.

**Known failure modes.**
- Resource ignores token
- Generation rolls back on restore
- External side effect cannot be fenced
- Actor obtains new token for old intent
- Multi-resource action fences only one sink

**Important criticisms.**
- Every sink must cooperate
- Physical/third-party effects may not accept tokens
- Authority service can be unavailable

**Evolution.** From leases and locks to end-to-end resource-enforced fencing and versioned handoff.

**Mature form.** Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.

**Ceremony boundary.** Owning a lock object or seeing oneself as leader is not the property.

**Evidence.** Primary: [S010], [S012], [S035], [S070], [S094]. Critical: [S095]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can fencing cover physical or third-party effects that do not accept generations?

### P14 — Single-writer or local-transaction cheap path

**Status:** `STRONGLY_RETAINED`  
**Lineage:** `REPLICATION_AND_CONSISTENCY_LINEAGE`, `DISTRIBUTED_TRANSACTION_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `HIGH`

**Historical origin.** Primary-copy and local transaction lineages, retained as an anti-overengineering conclusion.

**Original form.** Eliminate unnecessary distributed concurrency by placing an invariant under one current durable owner or one local transaction.

**Problem and distributed failure.** Distribution is introduced without a scale, latency, autonomy or availability consumer. Remote uncertainty, coordination and recovery machinery are created where local atomicity would suffice.

**Failure prevented.** Consensus/commit failure and coordination debt exceeding any benefit.

**Mechanism.** Co-locate state and operation; use one durable writer/local atomicity; replicate behind the writer only if needed.

**Trigger.** Low write scale, central invariant, tightly coupled data, modest availability demand or easy recovery.

**Cheap path / non-trigger.** This property is the cheap path; distribution triggers only after a concrete consumer appears.

**Dependencies and preconditions.** Clear ownership, local durability, tested backup and fenced promotion if automatic failover exists.

**Failure/timing/consistency boundary.** Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership. Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement. The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.

**Authority/delivery/recovery/observability boundary.** Replica set, writer authority and configuration identity are current and durable. Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. Catch-up, repair, rejoin, compaction and corruption handling are tested. Lag, divergence, repair source, membership and invariant checks are observable.

**Payoff and consumer.** Reduces state space, remote unknown outcomes and operational burden. Consumer: Architect and application/data owner.

**Known failure modes.**
- Owner becomes bottleneck
- Failover lacks fencing
- Local durability insufficient
- Async replicas lose accepted writes
- Ownership hidden behind load balancer

**Important criticisms.**
- Centralisation may fail latency/availability goals
- Future scaling can be difficult
- One process is not automatically durable

**Evolution.** From primary-copy replication to an explicit design-first cheap path.

**Mature form.** Start local or single-writer; distribute only the dimension with demonstrated need.

**Ceremony boundary.** A monolith is not automatically good, but distribution is not maturity.

**Evidence.** Primary: [S002], [S009], [S017], [S020], [S093]. Critical: [S043]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should a design detect that the cheap path no longer meets demand?

### P15 — Strong coordination for non-confluent invariants

**Status:** `STRONGLY_RETAINED`  
**Lineage:** `DISTRIBUTED_TRANSACTION_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Distributed serialisability, atomic commit, consensus and invariant-confluence analysis.

**Original form.** Coordinate operations whose independent execution can jointly violate a named invariant.

**Problem and distributed failure.** Locally valid concurrent decisions violate global uniqueness, conservation, bounds or exclusive ownership. Partitioned or concurrent actors each act on incomplete state and jointly break the invariant.

**Failure prevented.** Double allocation, oversell, duplicate uniqueness, inconsistent atomic transition or divergent ownership.

**Mechanism.** Use serialisable transaction, consensus, conditional write, reservation/escrow or authoritative sequencer over the minimal invariant boundary.

**Trigger.** Demonstrated non-confluence, globally scarce resource or irreversible action requiring an exclusive current decision.

**Cheap path / non-trigger.** Independent commutative operations, ownership partitioning, escrowed budgets or one local owner.

**Dependencies and preconditions.** Invariant definition, operation set, consistency target, current authority/membership, failure and recovery model.

**Failure/timing/consistency boundary.** Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation. Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome. Atomicity/isolation covers only the declared transaction boundary; external effects need another closure.

**Authority/delivery/recovery/observability boundary.** Participants/coordinator/owners and transaction generation are durable and current. Transaction messages and external calls have stable identity and duplicate-safe recovery. Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable. Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.

**Payoff and consumer.** Preserves a real invariant while containing coordination cost. Consumer: Application/data owner and the consumer harmed by invariant violation.

**Known failure modes.**
- Invariant boundary incomplete
- External side effect outside transaction
- Global lock bottleneck
- Availability fallback violates invariant
- Consensus agrees on invalid input

**Important criticisms.**
- Coordination hurts latency/availability
- Some invariants can be redesigned or escrowed
- Blanket 2PC/consensus overcoordinates

**Evolution.** From global transactions and locks to invariant-scoped coordination and hybrid strong/weak designs.

**Mature form.** Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.

**Ceremony boundary.** Consensus everywhere is ceremony; invariant-scoped coordination is the property.

**Evidence.** Primary: [S017], [S020], [S023], [S025], [S036], [S038], [S040], [S041], [S042]. Critical: [S027], [S039]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can physical or third-party effects safely join the coordinated decision?

### P16 — Coordination avoidance for invariant-confluent, commutative or partitionable operations

**Status:** `CONTEXT_DEPENDENT`  
**Lineage:** `REPLICATION_AND_CONSISTENCY_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `HIGH`

**Historical origin.** CRDT, highly available transaction and invariant-confluence lineages.

**Original form.** Allow independent progress when all valid independently produced states merge without violating the invariant.

**Problem and distributed failure.** Global coordination is used even though operations commute, are ownership-partitioned, escrow-bounded or merge safely. Unnecessary cross-node coordination turns delay/partition into availability and latency cost.

**Failure prevented.** Avoidable quorum waits, global bottlenecks and lost availability.

**Mechanism.** Prove or test invariant confluence/commutativity; use CRDT, escrow/reservation, monotonic dataflow or partition ownership; coordinate only the non-confluent subset.

**Trigger.** High-latency or partitioned environment where operation semantics support safe independent execution.

**Cheap path / non-trigger.** Non-confluent uniqueness/conservation/exclusive authority or irreversible global effects should coordinate instead.

**Dependencies and preconditions.** Operation algebra, merge rule, invariant, duplicate/reorder semantics, metadata retention and ownership boundaries.

**Failure/timing/consistency boundary.** Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership. Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement. The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.

**Authority/delivery/recovery/observability boundary.** Replica set, writer authority and configuration identity are current and durable. Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. Catch-up, repair, rejoin, compaction and corruption handling are tested. Lag, divergence, repair source, membership and invariant checks are observable.

**Payoff and consumer.** Improves availability, latency and scale without sacrificing the named invariant. Consumer: Data/application designer and geo/offline client.

**Known failure modes.**
- Incorrect confluence argument
- Hidden cross-object invariant
- Metadata collection breaks merge
- Schema change breaks commutativity
- External effect is non-commutative

**Important criticisms.**
- Application semantics are hard to formalise
- Complexity can move into reconciliation
- Not every converged state is meaningful

**Evolution.** From generic eventual consistency to invariant-justified autonomy and hybrid strong/weak access.

**Mature form.** Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.

**Ceremony boundary.** 'Use a CRDT' is ceremony without invariant and lifecycle proof.

**Evidence.** Primary: [S030], [S038], [S039], [S100]. Critical: [S025], [S027]. Empirical/outage: [S091].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can confluence arguments remain valid as operation sets evolve?

### P17 — Duplicate-aware delivery semantics

**Status:** `DELIVERY_IDEMPOTENCY_PROPERTY`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** RPC retransmission/duplicate suppression, durable logs, stream processing and broker semantics.

**Original form.** Declare at-most-once, at-least-once and processing/effect semantics per boundary, including crash, rebalance and replay.

**Problem and distributed failure.** Messages can be lost, duplicated, reordered or redelivered after acknowledgement, visibility timeout or consumer failover. Producer, broker and consumer fail independently; acknowledgement and state updates are separated.

**Failure prevented.** Lost work or duplicate processing/effects caused by hidden transport defaults.

**Mechanism.** Define attempt and event identity; persist acknowledgement/offset relative to state; design retry, poison and replay paths; make duplicates safe or explicit.

**Trigger.** Asynchronous transfer, queue, event log, task dispatch or producer/consumer retry.

**Cheap path / non-trigger.** Direct local call/transaction or fire-and-forget telemetry where loss is accepted.

**Dependencies and preconditions.** Durable event identity, producer/consumer state, retention, ordering partition and failure/rebalance semantics.

**Failure/timing/consistency boundary.** Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay. Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs. State/effect and acknowledgement/offset atomicity are explicit where claimed.

**Authority/delivery/recovery/observability boundary.** Producer/consumer/task ownership generations are current for ordered or exclusive processing. Transport attempt, message, processing, business operation and external effect identities are distinct. Replay, poison handling, dedup retention and unknown outcomes survive restart. Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.

**Payoff and consumer.** Prevents delivery labels from being promoted into false business-effect guarantees. Consumer: Producer, consumer, workflow and effect owner.

**Known failure modes.**
- Ack lost after processing
- Offset committed before effect
- Effect committed before offset
- Duplicate outside dedup window
- Partition order mistaken for global order

**Important criticisms.**
- At-most-once may lose work
- At-least-once shifts burden to consumer
- Platform-scoped exactly-once can be costly and narrow

**Evolution.** From transport retry semantics to end-to-end processing/effect contracts and transactional offset-state integration.

**Mature form.** Name semantics at every boundary and independently close the business-effect boundary.

**Ceremony boundary.** A broker checkbox labelled exactly-once is not an end-to-end guarantee.

**Evidence.** Primary: [S043], [S044], [S045], [S046], [S047], [S049]. Critical: [S054], [S059]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- Can terminology consistently distinguish delivery, processing and external effect across platforms?

### P18 — End-to-end business-operation and effect identity

**Status:** `DELIVERY_IDEMPOTENCY_PROPERTY`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `WORKFLOW_ORCHESTRATION_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `HIGH`

**Historical origin.** End-to-end argument, RPC/request identity, transaction-log and workflow lineages.

**Original form.** Distinguish transport attempts, messages, tasks, workflow steps, business operations and external effects.

**Problem and distributed failure.** One intent is represented by multiple retries/messages, or one key is reused for semantically changed intent. Independent components retry and replay without a shared semantic identifier.

**Failure prevented.** Duplicate charge/order/action, wrong deduplication, orphan status and unreconcilable effects.

**Mechanism.** Assign stable semantic operation ID plus immutable parameter/effect fingerprint; map every attempt/effect; persist status at the authoritative boundary.

**Trigger.** Retriable mutation, long-running workflow, external irreversible action or cross-service transaction.

**Cheap path / non-trigger.** Pure read, locally atomic mutation with no reply-loss concern, or disposable telemetry.

**Dependencies and preconditions.** Canonical operation definition, parameter binding, tenant/principal scope, retention and effect ledger/status query.

**Failure/timing/consistency boundary.** Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay. Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs. State/effect and acknowledgement/offset atomicity are explicit where claimed.

**Authority/delivery/recovery/observability boundary.** Producer/consumer/task ownership generations are current for ordered or exclusive processing. Transport attempt, message, processing, business operation and external effect identities are distinct. Replay, poison handling, dedup retention and unknown outcomes survive restart. Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.

**Payoff and consumer.** Provides the join key for idempotency, reconciliation, audit and compensation. Consumer: Client, orchestrator, service and external-effect owner.

**Known failure modes.**
- New ID per retry
- Same key reused after parameter change
- Key scoped too broadly or narrowly
- Effect system drops metadata
- Retention expires before replay

**Important criticisms.**
- Global identity can cost privacy/cardinality
- Canonicalisation is application-specific
- Identity alone does not prevent duplicates

**Evolution.** From packet/message identifiers to parameter-bound business intent and effect ledgers.

**Mature form.** Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.

**Ceremony boundary.** Adding a UUID header is ceremony if semantics, scope and retention are undefined.

**Evidence.** Primary: [S043], [S044], [S046], [S050], [S069]. Critical: [S049], [S095]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should identity span third parties that do not preserve supplied keys?

### P19 — Semantic idempotency, not request-ID ritual

**Status:** `DELIVERY_IDEMPOTENCY_PROPERTY`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `DISTRIBUTED_TRANSACTION_LINEAGE`, `WORKFLOW_ORCHESTRATION_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** RPC duplicate suppression, transaction identifiers, idempotent APIs and durable workflow retries.

**Original form.** Repeated execution of the same semantic operation must produce an acceptable state/effect, not merely reuse a key.

**Problem and distributed failure.** A request ID suppresses one duplicate path while downstream, external or changed-parameter effects still repeat. Retries, redelivery and late arrivals reach several independently failing effect boundaries.

**Failure prevented.** Duplicate payment, email, provision, deletion or state transition despite superficial deduplication.

**Mechanism.** Bind identity to semantic parameters; atomically record accepted outcome with effect when possible; make operation naturally idempotent or use guarded state transition/compensation.

**Trigger.** Any mutation or activity that may be retried, redelivered, replayed or concurrently submitted.

**Cheap path / non-trigger.** Pure read, commutative accumulation with duplicate identity, or one local transaction.

**Dependencies and preconditions.** Operation identity, canonical parameters, current precondition/version, durable result record, downstream closure and retention horizon.

**Failure/timing/consistency boundary.** Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay. Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs. State/effect and acknowledgement/offset atomicity are explicit where claimed.

**Authority/delivery/recovery/observability boundary.** Producer/consumer/task ownership generations are current for ordered or exclusive processing. Transport attempt, message, processing, business operation and external effect identities are distinct. Replay, poison handling, dedup retention and unknown outcomes survive restart. Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.

**Payoff and consumer.** Makes retries safe at the real effect boundary and exposes operations that cannot be made idempotent. Consumer: API owner, workflow author, client and external-effect owner.

**Known failure modes.**
- Key stored after effect
- Key collision across parameters
- Downstream call not idempotent
- Key window expires too soon
- Old success returned after semantics changed

**Important criticisms.**
- Natural idempotency is rare for many physical effects
- Dedup storage grows
- A cached response may hide changed external state

**Evolution.** From duplicate request suppression to semantic equivalence, atomic effect/result recording and end-to-end closure.

**Mature form.** The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.

**Ceremony boundary.** 'We add a request ID' is not idempotency.

**Evidence.** Primary: [S044], [S050], [S058], [S067], [S069]. Critical: [S043], [S049]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How long must idempotency evidence be retained for late replay and legal/business dispute?

### P20 — Bounded deduplication and replay horizon

**Status:** `ASSUMPTION_SENSITIVE`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`, `WORKFLOW_ORCHESTRATION_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** RPC duplicate caches, broker retention, event logs and workflow histories.

**Original form.** Duplicate suppression remains valid only while identity and result evidence outlive every permitted retry, replay and delayed delivery.

**Problem and distributed failure.** Deduplication records, tombstones, offsets or idempotency keys expire while old work can still arrive. Long partitions, restore from old backup, delayed queues and operator replay exceed the assumed window.

**Failure prevented.** Ancient duplicate effects, deletion resurrection and false 'new' work after restore.

**Mechanism.** Define maximum retry/replay/rejoin horizon; retain identity/tombstone/result evidence at least that long; reject or manually reconcile older arrivals.

**Trigger.** Finite dedup cache, TTL, log retention, replay, delayed replica rejoin or disaster restore.

**Cheap path / non-trigger.** No retries/replay and bounded local execution, or effect is naturally harmless under repetition.

**Dependencies and preconditions.** End-to-end maximum delay, restore age, retention policy, compaction rules and explicit post-expiry consequence.

**Failure/timing/consistency boundary.** Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay. Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs. State/effect and acknowledgement/offset atomicity are explicit where claimed.

**Authority/delivery/recovery/observability boundary.** Producer/consumer/task ownership generations are current for ordered or exclusive processing. Transport attempt, message, processing, business operation and external effect identities are distinct. Replay, poison handling, dedup retention and unknown outcomes survive restart. Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.

**Payoff and consumer.** Makes exactly-once/effect claims falsifiable in time instead of implicitly permanent. Consumer: Broker/storage owner, API owner, workflow and recovery planner.

**Known failure modes.**
- Late message after TTL
- Old backup resurrects consumed ID
- Tombstone compacted before replica returns
- Consumer offset retained less than data
- Key eviction under load

**Important criticisms.**
- Worst-case retention can be expensive
- Unbounded partitions make finite guarantees impossible
- Legal/business horizons may exceed technical retry windows

**Evolution.** From implementation-local duplicate caches to end-to-end replay-horizon contracts tied to restore and rejoin.

**Mature form.** Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.

**Ceremony boundary.** A seven-day idempotency window is not a permanent exactly-once guarantee.

**Evidence.** Primary: [S030], [S045], [S046], [S049], [S069]. Critical: [S037], [S091]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can systems economically retain proof for very long-lived external effects?

### P21 — Acknowledgement separated from verified external effect

**Status:** `DELIVERY_IDEMPOTENCY_PROPERTY`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `DISTRIBUTED_TRANSACTION_LINEAGE`, `WORKFLOW_ORCHESTRATION_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** End-to-end arguments, RPC ambiguity, transaction commit records and workflow completion semantics.

**Original form.** An ACK proves only the exact durable boundary that emitted it; it does not prove the intended downstream or real-world postcondition.

**Problem and distributed failure.** Callers treat receipt, queue acceptance, worker DONE or DB commit as proof the whole intended action occurred. Effects cross several independent systems and some acknowledgements are lost or emitted before downstream completion.

**Failure prevented.** False completion, lost external action, duplicate retry and unreconciled partial effects.

**Mechanism.** Name ACK boundary; link it to operation identity; verify required external postcondition or atomically close/compensate the remaining boundary.

**Trigger.** Multi-hop action, asynchronous processing, third-party/physical effect or workflow completion.

**Cheap path / non-trigger.** Single local transaction whose return covers the entire required state change.

**Dependencies and preconditions.** Declared postcondition, authoritative observation, provenance, effect identity and uncertainty/compensation policy.

**Failure/timing/consistency boundary.** Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay. Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs. State/effect and acknowledgement/offset atomicity are explicit where claimed.

**Authority/delivery/recovery/observability boundary.** Producer/consumer/task ownership generations are current for ordered or exclusive processing. Transport attempt, message, processing, business operation and external effect identities are distinct. Replay, poison handling, dedup retention and unknown outcomes survive restart. Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.

**Payoff and consumer.** Makes completion meaningful to the consumer rather than transport-local. Consumer: Caller, orchestrator, business owner and incident responder.

**Known failure modes.**
- Queue ACK before processing
- Worker DONE before durable effect
- DB commit before third-party response
- Success cached while downstream rolled back
- Observation is stale

**Important criticisms.**
- Independent verification may be expensive or impossible
- Observation can race later reversal
- Some effects are only probabilistically observable

**Evolution.** From transport receipt to end-to-end effect evidence and explicit residual uncertainty.

**Mature form.** Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.

**Ceremony boundary.** A 200 response, broker ACK or worker DONE is not completion by itself.

**Evidence.** Primary: [S043], [S044], [S046], [S050], [S055]. Critical: [S092]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should completion be expressed when the external world has no authoritative query?

### P22 — Transactional messaging or outbox/inbox closure

**Status:** `DELIVERY_IDEMPOTENCY_PROPERTY`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `DISTRIBUTED_TRANSACTION_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** Transaction logs, reliable messaging, stream-processing checkpoint/offset integration and outbox/inbox practice.

**Original form.** Close the atomicity gap between local state change and message publication/consumption.

**Problem and distributed failure.** A service commits state but fails to publish, publishes but rolls back, or applies an effect and crashes before advancing acknowledgement. Database and broker fail independently; network/retry separates commit from message acknowledgement.

**Failure prevented.** Lost event, duplicate state transition, offset/effect skew and inconsistent downstream projection.

**Mechanism.** Atomically write state plus outbox, or transactionally commit broker records/offsets and local state; consumers use inbox/dedup and replay.

**Trigger.** A local transaction must reliably cause or record an asynchronous message, or a consumed event must update state exactly once within the closure.

**Cheap path / non-trigger.** Direct local state change with no asynchronous notification requirement.

**Dependencies and preconditions.** Stable event identity, publisher relay/recovery, ordering assumptions, dedup horizon and explicit external-effect boundary.

**Failure/timing/consistency boundary.** Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay. Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs. State/effect and acknowledgement/offset atomicity are explicit where claimed.

**Authority/delivery/recovery/observability boundary.** Producer/consumer/task ownership generations are current for ordered or exclusive processing. Transport attempt, message, processing, business operation and external effect identities are distinct. Replay, poison handling, dedup retention and unknown outcomes survive restart. Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.

**Payoff and consumer.** Creates a recoverable handoff between local atomicity and asynchronous delivery. Consumer: Service owner, broker/stream operator, projection and workflow.

**Known failure modes.**
- Outbox relay publishes duplicates
- Consumer effect outside transaction
- Event order differs from state order
- Outbox never drained
- Schema evolution breaks replay

**Important criticisms.**
- Adds storage/relay complexity
- Still not atomic with arbitrary third parties
- Ordering across partitions is limited

**Evolution.** From distributed transaction aspiration to bounded local transaction plus durable handoff and duplicate-safe consumption.

**Mature form.** The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.

**Ceremony boundary.** Having a broker and an outbox table is not closure if relay, dedup and replay are unowned.

**Evidence.** Primary: [S043], [S045], [S046], [S048], [S049], [S050]. Critical: [S054]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- When is full distributed commit preferable to outbox/inbox plus compensation?

### P23 — Explicit transactional boundary and atomic-commit choice

**Status:** `TRANSACTION_COMPENSATION_PROPERTY`  
**Lineage:** `DISTRIBUTED_TRANSACTION_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Transactions, distributed serialisability, two-phase/nonblocking commit and later deterministic/geo transaction systems.

**Original form.** Identify exactly which participants and effects commit atomically, and the failure/blocking model of that choice.

**Problem and distributed failure.** Atomicity is assumed across databases, messages and external systems that are not in one commit protocol. Coordinator or participant fails between prepare/commit; partitions leave in-doubt participants or partial external effects.

**Failure prevented.** Partial commit, contradictory participant outcomes and false rollback expectations.

**Mechanism.** Use local transaction, 2PC/consensus-backed transaction, deterministic ordering or another atomic protocol only for participating resources; persist in-doubt state.

**Trigger.** A non-compensatable invariant requires all-or-nothing across multiple transactional participants.

**Cheap path / non-trigger.** One local transaction; or independently commit compensatable steps with a durable saga.

**Dependencies and preconditions.** Participant durability, coordinator log, isolation, recovery protocol, timeout semantics and explicit exclusion of nonparticipants.

**Failure/timing/consistency boundary.** Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation. Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome. Atomicity/isolation covers only the declared transaction boundary; external effects need another closure.

**Authority/delivery/recovery/observability boundary.** Participants/coordinator/owners and transaction generation are durable and current. Transaction messages and external calls have stable identity and duplicate-safe recovery. Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable. Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.

**Payoff and consumer.** Makes atomicity real within a defensible boundary and exposes blocking/availability cost. Consumer: Database/application designer, coordinator and recovery operator.

**Known failure modes.**
- Coordinator log lost
- Participant heuristic decision
- External effect outside protocol
- Prepared transaction blocks resources
- Isolation weaker than invariant

**Important criticisms.**
- 2PC can block and add latency
- Blanket rejection ignores cases where atomicity is worth cost
- Blanket adoption extends scope too far

**Evolution.** From global transaction aspiration to scoped atomicity, replicated coordinators, deterministic ordering and hybrid saga boundaries.

**Mature form.** Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.

**Ceremony boundary.** 'ACID' or '2PC' without participant/effect boundary is ceremony.

**Evidence.** Primary: [S017], [S018], [S020], [S023], [S036], [S040], [S041], [S042]. Critical: [S019], [S039], [S055]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- Which modern workloads justify the latency/availability cost of cross-region atomic commit?

### P24 — Compensation and forward recovery with semantic limits

**Status:** `TRANSACTION_COMPENSATION_PROPERTY`  
**Lineage:** `DISTRIBUTED_TRANSACTION_LINEAGE`, `WORKFLOW_ORCHESTRATION_LINEAGE`  
**Evidence:** `HIGH`

**Historical origin.** Sagas and long-running transaction practice, later durable workflow systems.

**Original form.** Recover a long-running distributed operation through ordered compensating or forward actions when global rollback is unavailable.

**Problem and distributed failure.** Steps commit independently and some effects cannot be transactionally rolled back. Later step fails after earlier durable/internal/external effects; compensation can also fail or be non-inverse.

**Failure prevented.** Permanent unowned partial business state and false claim that rollback restores the past.

**Mechanism.** Persist saga state; define compensations/reservations/semantic locks; order and retry them safely; use forward recovery when reversal is impossible; escalate residuals.

**Trigger.** Long-running, cross-service or external workflow whose effects are compensatable or repairable but not globally atomic.

**Cheap path / non-trigger.** One atomic local/distributed transaction when the whole closure can and should commit together.

**Dependencies and preconditions.** Effect identity, compensation semantics, ordering, duplicate safety, durable orchestration, current external-state observation and manual path.

**Failure/timing/consistency boundary.** Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation. Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome. Atomicity/isolation covers only the declared transaction boundary; external effects need another closure.

**Authority/delivery/recovery/observability boundary.** Participants/coordinator/owners and transaction generation are durable and current. Transaction messages and external calls have stable identity and duplicate-safe recovery. Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable. Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.

**Payoff and consumer.** Provides a governed recovery path for partial effects without pretending compensation is a true inverse. Consumer: Workflow/business owner, service teams and operations.

**Known failure modes.**
- Compensation is not inverse
- Compensation order wrong
- Compensation itself duplicates/fails
- External state changed meanwhile
- Irreversible effect remains

**Important criticisms.**
- Sagas expose intermediate state
- Compensations demand domain knowledge
- Complexity may exceed a scoped transaction

**Evolution.** From named compensating transactions to durable, observable, idempotent compensation/forward-recovery plans with residual-state handling.

**Mature form.** Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.

**Ceremony boundary.** A compensating endpoint on a diagram is not recovery evidence.

**Evidence.** Primary: [S019], [S050], [S055], [S097]. Critical: [S023], [S043]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can systems validate compensation semantics as business rules change?

### P25 — Durable workflow state as a recoverable distributed state machine

**Status:** `WORKFLOW_STATE_PROPERTY`  
**Lineage:** `WORKFLOW_ORCHESTRATION_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Sagas, workflow systems, durable logs and modern serverless durable execution.

**Original form.** Persist enough workflow history/state that orchestration survives process loss and resumes deterministically or by explicit repair.

**Problem and distributed failure.** Request/worker memory is lost on restart; timers, child work, retries and compensation become orphaned. Orchestrator and workers fail independently while tasks and external effects continue.

**Failure prevented.** Lost long-running work, duplicate restart, forgotten timers/compensations and operator guesswork.

**Mechanism.** Persist workflow transitions/history, task identities, timers, signals and terminal state; replay or recover from snapshot/log; expose manual intervention.

**Trigger.** Long-running, multi-step, retrying or externally signalled work that must survive process/platform restart.

**Cheap path / non-trigger.** Synchronous local call/transaction whose whole lifetime fits one reliable execution boundary.

**Dependencies and preconditions.** Durable ordered history, stable workflow/run identity, deterministic/versioned orchestration and external-effect reconciliation.

**Failure/timing/consistency boundary.** Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty. Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped. Durable workflow state is distinct from correctness/currentness of external systems.

**Authority/delivery/recovery/observability boundary.** Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. Workflow state, task attempts, effect status and version are reconstructable.

**Payoff and consumer.** Makes distributed work state recoverable and inspectable rather than implicit in transient processes. Consumer: Workflow author, orchestration runtime, operator and business owner.

**Known failure modes.**
- History lost or corrupted
- External effect not in history
- Replay code changed
- Duplicate task after recovery
- Terminal state set before effect verified

**Important criticisms.**
- Persistence adds latency/cost
- History can grow
- Durability does not guarantee semantic correctness of external world

**Evolution.** From ad hoc retry scripts and sagas to durable state machines with history, timers, signals and explicit effect boundaries.

**Mature form.** Workflow history is authoritative for orchestration, while external state is independently validated where required.

**Ceremony boundary.** Deploying a workflow engine is not the property if workflow/effect state is not durable and reconcilable.

**Evidence.** Primary: [S019], [S045], [S046], [S050], [S051], [S052], [S053], [S054], [S055], [S056]. Critical: [S043], [S092]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should long-lived workflow histories be compacted without losing replay or audit correctness?

### P26 — Task ownership, lease expiry and duplicate-safe re-dispatch

**Status:** `WORKFLOW_STATE_PROPERTY`  
**Lineage:** `WORKFLOW_ORCHESTRATION_LINEAGE`, `MESSAGE_DELIVERY_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Leases, task queues, workflow activity retries and fencing generations.

**Original form.** A task may be re-dispatched only with a policy for the prior worker that may still be alive and acting.

**Problem and distributed failure.** Heartbeat/lease expires because a worker is slow or partitioned; new worker starts while old worker resumes. Two attempts concurrently believe they own one task or external effect.

**Failure prevented.** Double execution, conflicting writes, duplicate external side effect and lost progress.

**Mechanism.** Give attempts stable operation identity and attempt generation; fence protected resources or make effects idempotent/compensatable; retain unknown prior attempt state.

**Trigger.** Task queue, visibility timeout, worker lease, heartbeat or automatic re-dispatch.

**Cheap path / non-trigger.** One local worker under a process-local lock, or harmless repeatable calculation with no effect.

**Dependencies and preconditions.** Task/run/attempt identity, current ownership generation, timeout policy, effect closure, heartbeat semantics and durable retry record.

**Failure/timing/consistency boundary.** Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty. Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped. Durable workflow state is distinct from correctness/currentness of external systems.

**Authority/delivery/recovery/observability boundary.** Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. Workflow state, task attempts, effect status and version are reconstructable.

**Payoff and consumer.** Allows recovery from lost workers without converting slowness into duplicate harm. Consumer: Orchestrator, scheduler, worker and effect owner.

**Known failure modes.**
- Lease expiry does not stop worker
- New attempt uses new operation ID
- External sink ignores generation
- Heartbeat delayed under overload
- Cancellation races completion

**Important criticisms.**
- Fencing every external effect can be impossible
- Long leases slow recovery
- Short leases create false failover

**Evolution.** From visibility timeout/redelivery to generation-bound attempts, unknown-state handling and effect-specific duplicate protection.

**Mature form.** Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.

**Ceremony boundary.** A visibility timeout or heartbeat is not proof the old worker cannot act.

**Evidence.** Primary: [S035], [S050], [S052], [S053], [S054], [S058]. Critical: [S095]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should lease duration adapt without amplifying overload or stale-worker risk?

### P27 — Completion defined by durable state plus verified postcondition

**Status:** `WORKFLOW_STATE_PROPERTY`  
**Lineage:** `WORKFLOW_ORCHESTRATION_LINEAGE`, `MESSAGE_DELIVERY_LINEAGE`, `CONVERGENT_ENGINEERING`  
**Evidence:** `VERY_HIGH`

**Historical origin.** End-to-end correctness, transaction commit semantics, sagas and durable workflow systems.

**Original form.** A distributed action is complete only at a declared consumer-relevant postcondition, not merely because a worker returned.

**Problem and distributed failure.** Workflow state says DONE while downstream, external or physical state is absent, stale or later rolled back. Worker report, orchestrator commit and external observation occur in different failure domains.

**Failure prevented.** False terminal state, premature notification, duplicate re-execution and unreconciled real-world action.

**Mechanism.** Define terminal invariant; persist transition; link required effect identities; independently query/observe or transactionally enclose them; record PARTIAL/UNKNOWN when not proved.

**Trigger.** Completion drives user notification, billing, next workflow, resource release or irreversible decision.

**Cheap path / non-trigger.** Local transaction return covers the complete required postcondition.

**Dependencies and preconditions.** Consumer-defined postcondition, authoritative evidence source, operation/effect identity, currentness and residual uncertainty policy.

**Failure/timing/consistency boundary.** Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty. Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped. Durable workflow state is distinct from correctness/currentness of external systems.

**Authority/delivery/recovery/observability boundary.** Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. Workflow state, task attempts, effect status and version are reconstructable.

**Payoff and consumer.** Makes DONE auditable and meaningful, preserving uncertainty instead of hiding it. Consumer: Business process owner, caller, orchestrator and operator.

**Known failure modes.**
- Worker report treated as effect proof
- Observation is stale
- External state changes after check
- Terminal state cannot be reopened
- One of several effects omitted

**Important criticisms.**
- Independent verification costs latency
- Some real-world postconditions are not exactly observable
- Continuous conditions can later become false

**Evolution.** From process return codes to durable terminal-state contracts with postcondition evidence and explicit uncertainty.

**Mature form.** DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.

**Ceremony boundary.** Green task status is not completion.

**Evidence.** Primary: [S043], [S050], [S054], [S055], [S092]. Critical: [S044]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should completion be represented for continuous or probabilistic external conditions?

### P28 — Deterministic replay with explicit workflow/code version evolution

**Status:** `ASSUMPTION_SENSITIVE`  
**Lineage:** `WORKFLOW_ORCHESTRATION_LINEAGE`, `HYBRID`  
**Evidence:** `HIGH`

**Historical origin.** Event sourcing, replay-based workflow runtimes and durable-functions semantics.

**Original form.** Re-executing orchestration logic against recorded history must reproduce compatible decisions, or migration/version logic must deliberately translate it.

**Problem and distributed failure.** Code, dependencies, nondeterministic APIs or schemas change while old histories are replayed. Restarted orchestrator executes a different decision path from the one that produced persisted events.

**Failure prevented.** Non-deterministic replay, stuck histories, duplicate task scheduling and semantic corruption after deployment.

**Mechanism.** Restrict orchestrator nondeterminism; record decisions; version branches/patches; test old histories; migrate or pin incompatible workflows; separate external activities.

**Trigger.** Replay-based durable workflow, event sourcing or state reconstruction across code versions.

**Cheap path / non-trigger.** Persist explicit current state without replay, or finish short-lived work before incompatible deployment.

**Dependencies and preconditions.** Immutable history/event semantics, version identifiers, deterministic APIs, compatibility tests and migration/rollback plan.

**Failure/timing/consistency boundary.** Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty. Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped. Durable workflow state is distinct from correctness/currentness of external systems.

**Authority/delivery/recovery/observability boundary.** Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. Workflow state, task attempts, effect status and version are reconstructable.

**Payoff and consumer.** Allows durable execution to survive code evolution without rewriting history accidentally. Consumer: Workflow/runtime developer, deployer and recovery operator.

**Known failure modes.**
- Wall-clock/random call during replay
- Changed loop schedules new task
- Removed activity type
- Event schema incompatible
- Old binary unavailable for rollback

**Important criticisms.**
- Determinism constraints complicate programming
- Version branches accumulate
- External dependencies remain nondeterministic

**Evolution.** From replay assuming static code to versioned histories, compatibility APIs, migration and alternative speculative/current-state approaches.

**Mature form.** History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.

**Ceremony boundary.** 'The engine replays deterministically' is not enough without code-evolution evidence.

**Evidence.** Primary: [S052], [S053], [S054], [S056], [S057], [S060]. Critical: [S055], [S079]. Empirical/outage: [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- Which migration methods minimise long-term version-branch debt?

### P29 — Bounded queues with explicit work-age and capacity semantics

**Status:** `OVERLOAD_BACKPRESSURE_PROPERTY`  
**Lineage:** `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`, `HYBRID`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Queueing/service systems, staged event-driven architectures and production overload experience.

**Original form.** A queue is finite deferred work against finite service capacity, not an infinite availability reservoir.

**Problem and distributed failure.** Acceptance continues after completion capacity is exhausted; backlog age and memory/storage grow until service or recovery collapses. Producers and consumers scale/fail independently; queue hides demand from upstream while downstream saturates.

**Failure prevented.** Unbounded memory/disk growth, extreme latency, expired work, recovery surge and hidden overload.

**Mechanism.** Bound depth/age/bytes; attach deadlines and priority; reject/shed/spill according to consequence policy; size from service rate and recovery capacity.

**Trigger.** Asynchronous buffering between independently varying producer and consumer demand.

**Cheap path / non-trigger.** Direct synchronous flow with natural backpressure, or small fixed local buffer where overload consequence is acceptable.

**Dependencies and preconditions.** Measured arrival/service distributions, deadline/value policy, storage limit, drain/recovery capacity and rejection semantics.

**Failure/timing/consistency boundary.** Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback. Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns. Consequence policy defines which work may be rejected, degraded, delayed or shed.

**Authority/delivery/recovery/observability boundary.** Admission and priority policy has a defined owner; no implicit per-hop policy conflict. Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. Backlog drain, retry release and recovery surge are capacity-bounded and observed. Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.

**Payoff and consumer.** Makes queueing a deliberate latency/capacity trade rather than overload concealment. Consumer: Service owner, queue/stream operator, capacity planner and business owner.

**Known failure modes.**
- Depth bounded but age unbounded
- Disk fills
- Old work no longer useful
- Priority starvation
- Backlog overwhelms dependency during recovery

**Important criticisms.**
- Hard limits reject work
- Burst absorption needs headroom
- Capacity estimates vary and can be wrong

**Evolution.** From unbounded buffering to multidimensional limits on count, bytes, age and consequence, tied to drain/recovery tests.

**Mature form.** Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.

**Ceremony boundary.** 'We put a queue in front' is not resilience.

**Evidence.** Primary: [S045], [S062], [S063], [S064], [S065], [S066]. Critical: [S073]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should shared queues preserve fairness and critical work under shifting demand?

### P30 — Backpressure propagated to the source of demand

**Status:** `OVERLOAD_BACKPRESSURE_PROPERTY`  
**Lineage:** `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Flow control, bounded-buffer systems, stream processing and service-overload control.

**Original form.** A saturated consumer communicates a rate/credit/refusal signal upstream before queues and retries amplify demand.

**Problem and distributed failure.** Local queues fill while producers continue at an unconstrained rate; overload moves rather than resolves. Each hop sees only local capacity and can amplify or buffer requests independently.

**Failure prevented.** Cascading queue growth, wasted work, timeout storms and downstream collapse.

**Mechanism.** Credit/rate/window control, demand signalling, concurrency limits, propagated deadline/refusal, or producer throttling across the dependency graph.

**Trigger.** Producer can outpace consumer or fan-out multiplies work.

**Cheap path / non-trigger.** In-process bounded channel or naturally demand-driven iterator when no remote graph exists.

**Dependencies and preconditions.** Current dependency topology, demand accounting, admission semantics, retry integration and fairness policy.

**Failure/timing/consistency boundary.** Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback. Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns. Consequence policy defines which work may be rejected, degraded, delayed or shed.

**Authority/delivery/recovery/observability boundary.** Admission and priority policy has a defined owner; no implicit per-hop policy conflict. Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. Backlog drain, retry release and recovery surge are capacity-bounded and observed. Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.

**Payoff and consumer.** Aligns offered load with bottleneck capacity and stops overload migration. Consumer: Producer, intermediary, downstream owner and platform traffic controller.

**Known failure modes.**
- Signal stops at one hop
- Retry bypasses backpressure
- Buffer masks saturation
- Control loop oscillates
- One tenant monopolises credits

**Important criticisms.**
- Coordination adds latency/state
- Topology changes
- Backpressure can reduce utilisation or create unfairness

**Evolution.** From hop-local flow control to dependency-aware end-to-end demand propagation and adaptive limits.

**Mature form.** Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.

**Ceremony boundary.** A local queue watermark with unconstrained upstream retries is not backpressure.

**Evidence.** Primary: [S047], [S062], [S063], [S064], [S065]. Critical: [S061], [S066]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can multi-tenant systems coordinate backpressure without central bottlenecks?

### P31 — Admission control and load shedding with consequence policy

**Status:** `OVERLOAD_BACKPRESSURE_PROPERTY`  
**Lineage:** `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`, `HYBRID`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Overload control, queueing/admission theory and production service practice.

**Original form.** Decline, degrade or defer work before accepted load exceeds the capacity needed to preserve critical service.

**Problem and distributed failure.** Systems accept every request and fail all of them slowly, or shed indiscriminately without preserving critical/fair work. Capacity and demand vary across dependencies; overload signals arrive late and partial.

**Failure prevented.** Overload collapse, tail amplification, critical-work starvation and invisible business loss.

**Mechanism.** Concurrency/rate limits, priority and fairness, deadline-aware admission, graceful degradation and explicit rejection/deferral semantics.

**Trigger.** Demand can exceed sustainable service or shared bottlenecks can saturate.

**Cheap path / non-trigger.** Fixed small system with hard external demand limit and no shared saturation risk.

**Dependencies and preconditions.** Capacity model, criticality/value classes, fairness policy, caller-visible rejection semantics, retry budget and telemetry.

**Failure/timing/consistency boundary.** Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback. Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns. Consequence policy defines which work may be rejected, degraded, delayed or shed.

**Authority/delivery/recovery/observability boundary.** Admission and priority policy has a defined owner; no implicit per-hop policy conflict. Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. Backlog drain, retry release and recovery surge are capacity-bounded and observed. Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.

**Payoff and consumer.** Preserves useful work and system recoverability instead of maximising accepted-but-doomed work. Consumer: Traffic controller, service owner, product/business owner and clients.

**Known failure modes.**
- Clients retry shed work
- Wrong priority starves critical work
- Admission signal is stale
- Global bottleneck unseen
- Fallback overloads another dependency

**Important criticisms.**
- Shedding loses service
- Priority can encode unfairness
- Capacity estimates and value classification are imperfect

**Evolution.** From generic 503/refusal to deadline-, value-, fairness- and dependency-aware admission with explicit consequence ownership.

**Mature form.** Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.

**Ceremony boundary.** A circuit breaker that drops unknown work without consequence policy is not mature load shedding.

**Evidence.** Primary: [S063], [S064], [S065], [S066]. Critical: [S062], [S067]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should fairness, criticality and business value be reconciled under prolonged scarcity?

### P32 — Retry budgets, exponential backoff, jitter and deadline propagation

**Status:** `OVERLOAD_BACKPRESSURE_PROPERTY`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** RPC retry practice, congestion/overload control and production guidance on coordinated retries.

**Original form.** Retries consume bounded capacity and time; they are not free availability.

**Problem and distributed failure.** Every layer retries independently, synchronously and after the operation's useful deadline. Partial failures/timeouts cause many clients to retransmit into a degraded shared dependency.

**Failure prevented.** Retry storms, duplicate effects, wasted work, thundering herd and deadline overrun.

**Mechanism.** Centralise/allocate retry budget; cap attempts; use exponential backoff with jitter; honour end-to-end deadline; retry only classified/transient/duplicate-safe operations.

**Trigger.** Transient failure can plausibly recover within the remaining deadline and retry is semantically safe.

**Cheap path / non-trigger.** No retry for permanent errors, expired work, non-idempotent effect without closure or already-overloaded dependency.

**Dependencies and preconditions.** Error classification, operation identity/idempotency, timeout distribution, downstream capacity signal, deadline and attempt accounting.

**Failure/timing/consistency boundary.** Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback. Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns. Consequence policy defines which work may be rejected, degraded, delayed or shed.

**Authority/delivery/recovery/observability boundary.** Admission and priority policy has a defined owner; no implicit per-hop policy conflict. Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. Backlog drain, retry release and recovery surge are capacity-bounded and observed. Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.

**Payoff and consumer.** Retains availability benefit of selective retries without amplifying failure. Consumer: Client library, service owner, workflow and traffic controller.

**Known failure modes.**
- Retries at every stack layer
- No jitter
- Timeout shorter than tail latency
- Retry after deadline
- Retry non-idempotent operation
- Hedging doubles overload

**Important criticisms.**
- Backoff delays recovery
- Error classification is imperfect
- Retries can hide systemic faults

**Evolution.** From blind immediate retry to budgeted, jittered, deadline-aware and semantically qualified retries.

**Mature form.** A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.

**Ceremony boundary.** 'We use exponential backoff' is insufficient without attempt/deadline/idempotency/capacity bounds.

**Evidence.** Primary: [S061], [S063], [S066], [S067], [S068], [S069]. Critical: [S062]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should retry budgets adapt during metastable recovery without causing synchronised release?

### P33 — Metastable and cascading-overload containment

**Status:** `OVERLOAD_BACKPRESSURE_PROPERTY`  
**Lineage:** `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Cascading-failure practice and the metastable-failure research programme.

**Original form.** Prevent positive feedback from sustaining overload after the initial trigger disappears.

**Problem and distributed failure.** Backlog, retries, cache misses, failover traffic or recovery work reduces effective capacity and generates more of itself. Independent components adapt locally in ways that amplify global demand and state transition.

**Failure prevented.** Persistent degraded equilibrium, recovery failure and system-wide collapse.

**Mechanism.** Identify amplification loop; cap queues/retries/concurrency; reserve recovery capacity; shed early; warm/ramp gradually; break feedback and validate exit path.

**Trigger.** Fan-out, shared bottleneck, retry/cache/failover/backlog loop or recovery surge can feed on itself.

**Cheap path / non-trigger.** Low-utilisation local system with no feedback path and trivial restart.

**Dependencies and preconditions.** Dependency graph, demand/capacity telemetry, feedback-loop hypothesis, safe shedding and tested recovery ramp.

**Failure/timing/consistency boundary.** Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback. Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns. Consequence policy defines which work may be rejected, degraded, delayed or shed.

**Authority/delivery/recovery/observability boundary.** Admission and priority policy has a defined owner; no implicit per-hop policy conflict. Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. Backlog drain, retry release and recovery surge are capacity-bounded and observed. Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.

**Payoff and consumer.** Restores the ability to recover instead of assuming removal of the initiating fault is sufficient. Consumer: Service/platform architect, incident commander and capacity owner.

**Known failure modes.**
- Backlog drain overloads dependency
- Cache flush creates misses
- Failover doubles load
- Autoscaling lags
- Retries keep failed service hot
- Recovery releases herd

**Important criticisms.**
- Loops are difficult to identify before failure
- Mitigations may reduce normal utilisation
- Incident samples are selective

**Evolution.** From isolated component availability to dynamic-system stability, positive-feedback diagnosis and recovery-capacity reservation.

**Mature form.** The failure model includes amplification and a tested path out of the degraded state.

**Ceremony boundary.** Restarting failed instances is not recovery if the feedback loop persists.

**Evidence.** Primary: [S062], [S063], [S064], [S065], [S066]. Critical: [S061], [S067]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can metastable precursors be detected reliably without excessive false alarms?

### P34 — Dependency isolation and bulkheads with end-to-end verification

**Status:** `CONTEXT_DEPENDENT`  
**Lineage:** `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `HIGH`

**Historical origin.** Fault-containment, bulkhead/circuit-breaker and service-dependency engineering.

**Original form.** Limit one dependency, tenant, queue or failure mode from exhausting shared resources needed by unrelated critical work.

**Problem and distributed failure.** Threads, connections, memory, CPU, queues or retry budget are shared across dependency paths and fail together. A slow/unavailable dependency consumes local resources while callers continue fan-out or fallback.

**Failure prevented.** Cascading starvation and loss of all service due to one degraded path.

**Mechanism.** Per-dependency/tenant concurrency pools, budgets, timeouts/deadlines, circuit state, isolation boundaries and tested degraded path.

**Trigger.** Shared resource pool or dependency whose slowness/failure can block unrelated work.

**Cheap path / non-trigger.** One small dependency path with no shared-resource contention or acceptable full-stop behaviour.

**Dependencies and preconditions.** Current topology, resource accounting, critical-path classification, fallback capacity and consequence policy.

**Failure/timing/consistency boundary.** Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback. Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns. Consequence policy defines which work may be rejected, degraded, delayed or shed.

**Authority/delivery/recovery/observability boundary.** Admission and priority policy has a defined owner; no implicit per-hop policy conflict. Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. Backlog drain, retry release and recovery surge are capacity-bounded and observed. Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.

**Payoff and consumer.** Contains blast radius while preserving selected useful service. Consumer: Service owner, platform runtime and incident responder.

**Known failure modes.**
- Fallback shares same dependency
- Bulkhead too small
- Circuit opens on false suspicion
- Isolation boundary leaks shared DB/CPU
- Recovery herd after close

**Important criticisms.**
- Fragmented pools waste capacity
- Static limits age poorly
- Circuit state can oscillate or hide root cause

**Evolution.** From fixed pools and circuit breakers to dependency-aware budgets, adaptive isolation and end-to-end readiness tests.

**Mature form.** Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.

**Ceremony boundary.** A circuit-breaker library annotation is not containment.

**Evidence.** Primary: [S061], [S064], [S066], [S093]. Critical: [S062]. Empirical/outage: [S073], [S075].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- When should isolation limits be adaptive versus fixed for predictability?

### P35 — Consistent distributed snapshot or checkpoint

**Status:** `RECOVERY_RECONSTITUTION_PROPERTY`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Chandy–Lamport snapshots, coordinated checkpointing and stream-processing snapshots.

**Original form.** Capture a recovery cut that is consistent with message/channel and state transitions, not an arbitrary set of local copies.

**Problem and distributed failure.** Independent checkpoints combine states that never coexisted; in-flight messages/effects are lost or duplicated. Components checkpoint at different times while messages and transactions continue.

**Failure prevented.** Impossible restored state, orphan messages, domino rollback and duplicate/lost processing.

**Mechanism.** Marker/barrier/coordinated checkpoint or equivalent protocol records local state plus required channel/log position; validate completeness and durability.

**Trigger.** Recovery, migration, rescaling or audit requires a cross-component state cut.

**Cheap path / non-trigger.** One local transactional snapshot or reconstructable stateless workers.

**Dependencies and preconditions.** Declared channel/order assumptions, checkpoint metadata, atomic durable write, log position and compatible application state.

**Failure/timing/consistency boundary.** Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence. Recovery point/time objectives are evidence-backed, not inferred from backup existence. The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.

**Authority/delivery/recovery/observability boundary.** Restored configuration, ownership generation and membership are current; old writers are fenced. Replay/redelivery uses original identities and does not duplicate unclosed effects. Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. Recovery progress, gaps, validation, divergence and residual unknowns are visible.

**Payoff and consumer.** Provides a coherent internal recovery point without stopping the system where assumptions permit. Consumer: Storage/stream/workflow runtime and recovery operator.

**Known failure modes.**
- External side effect outside snapshot
- Checkpoint corrupted
- Barrier stalls under backpressure
- Log truncated too early
- Membership changes mid-snapshot

**Important criticisms.**
- Snapshot consistency is model-specific
- Large snapshots cost I/O/latency
- Internal consistency does not guarantee external world consistency

**Evolution.** From global coordinated checkpoints to asynchronous barriers, incremental snapshots and log/snapshot hybrids.

**Mature form.** Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.

**Ceremony boundary.** Having periodic snapshots is not a consistent recovery cut.

**Evidence.** Primary: [S004], [S017], [S048], [S071], [S072]. Critical: [S088]. Empirical/outage: [S074].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can large geo-distributed snapshots remain cheap without weakening recovery semantics?

### P36 — Replay and restore with external-state reconciliation

**Status:** `RECOVERY_RECONSTITUTION_PROPERTY`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`, `WORKFLOW_ORCHESTRATION_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Write-ahead logging, rollback recovery, event logs and durable workflows.

**Original form.** Reconstruct internal state from snapshot/log and then reconcile effects not enclosed by that history.

**Problem and distributed failure.** Log replay finishes while third-party, physical, cached or downstream state reflects a different prefix or duplicate effects. Internal durable history and external systems fail/recover independently.

**Failure prevented.** Internally clean but externally inconsistent recovery, duplicate irreversible effects and hidden residual state.

**Mechanism.** Restore a validated cut, replay with original identities, enumerate external effects/status, compare authoritative postconditions, compensate/forward-repair or mark unknown.

**Trigger.** Disaster restore, log replay, workflow history recovery or regional failover with external effects.

**Cheap path / non-trigger.** All state and effects are inside one local transactional restore boundary.

**Dependencies and preconditions.** Complete logs, compatible code/schema, operation/effect identity, external query/ledger, authority fencing and manual residual path.

**Failure/timing/consistency boundary.** Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence. Recovery point/time objectives are evidence-backed, not inferred from backup existence. The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.

**Authority/delivery/recovery/observability boundary.** Restored configuration, ownership generation and membership are current; old writers are fenced. Replay/redelivery uses original identities and does not duplicate unclosed effects. Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. Recovery progress, gaps, validation, divergence and residual unknowns are visible.

**Payoff and consumer.** Turns replay into end-to-end reconstitution rather than internal state reconstruction only. Consumer: Recovery operator, workflow owner, application/data owner and third-party integration.

**Known failure modes.**
- Log gap
- Replay duplicates external effect
- External state cannot be queried
- Schema/code cannot read old event
- Old writer remains live

**Important criticisms.**
- External reconciliation can be manual and slow
- Some effects are irreversible/unobservable
- Logs may preserve bugs as well as facts

**Evolution.** From database restore to cross-boundary recovery plans combining replay, effect ledgers, compensation and validation.

**Mature form.** Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.

**Ceremony boundary.** 'Replay completed' is not externally consistent recovery.

**Evidence.** Primary: [S017], [S046], [S048], [S050], [S053], [S056], [S071]. Critical: [S043], [S088], [S091]. Empirical/outage: [S073], [S074].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can organisations precompute reconciliation plans for effects controlled by third parties?

### P37 — Failover re-establishes current authority before mutation

**Status:** `RECOVERY_RECONSTITUTION_PROPERTY`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `REPLICATION_AND_CONSISTENCY_LINEAGE`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Primary/backup views, leases, consensus terms and disaster failover practice.

**Original form.** Promoting a replacement is incomplete until former authority is excluded and the selected state/configuration is current enough.

**Problem and distributed failure.** New primary is promoted while old primary can still write or the chosen replica is stale/divergent. Partition and false suspicion create simultaneous actors with incompatible state and authority.

**Failure prevented.** Split brain, lost accepted writes, stale takeover and divergent recovery branches.

**Mechanism.** Establish current membership/state position, issue higher epoch/fencing, block stale resources/writers, validate replication/recovery point, then reopen writes.

**Trigger.** Leader/primary/site/region failover or ownership transfer after suspected failure.

**Cheap path / non-trigger.** Manual offline recovery with verified old owner stopped, or one local process restart without concurrent actor.

**Dependencies and preconditions.** Authoritative config/quorum, current data version, fenced sinks, durable generation, client routing and reconciliation of divergent writes.

**Failure/timing/consistency boundary.** Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence. Recovery point/time objectives are evidence-backed, not inferred from backup existence. The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.

**Authority/delivery/recovery/observability boundary.** Restored configuration, ownership generation and membership are current; old writers are fenced. Replay/redelivery uses original identities and does not duplicate unclosed effects. Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. Recovery progress, gaps, validation, divergence and residual unknowns are visible.

**Payoff and consumer.** Makes failover a safe authority transition rather than mere traffic redirection. Consumer: Failover controller, database operator and incident commander.

**Known failure modes.**
- Old primary resumes
- DNS/routing sends writes to both
- New primary missing writes
- Epoch rolls back
- Application cannot tolerate cross-region topology

**Important criticisms.**
- Conservative fencing delays availability
- Determining most-current state can be expensive
- Manual disaster actions can bypass controls

**Evolution.** From heartbeat-triggered promotion to configuration-indexed, state-validated and resource-fenced authority transfer.

**Mature form.** Failover completes only after authority fencing, current-state selection and post-failover validation.

**Ceremony boundary.** 'Leader elected' or 'traffic switched' is not safe failover.

**Evidence.** Primary: [S010], [S012], [S035], [S036], [S094]. Critical: [S073], [S095]. Empirical/outage: [S073], [S075].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should automatic failover balance recovery speed against false-suspicion and stale-state risk?

### P38 — Tested restore and recovery-path evidence

**Status:** `STRONGLY_RETAINED`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Backup/recovery practice, rollback-recovery research and repeated outage evidence.

**Original form.** A backup, replica or runbook is only potential recovery; evidence comes from restoring the current system within consequence limits.

**Problem and distributed failure.** Backups are absent, corrupt, incomplete, too slow, incompatible or inaccessible during the incident. Recovery tooling, credentials, network, schemas, logs and capacity fail separately from the production data path.

**Failure prevented.** Discovering during disaster that recovery point/time objectives and authority reconstruction are fictional.

**Mechanism.** Regular full restore/failover rehearsal using current artefacts, code, configuration, identities and realistic scale; validate data/effects/authority and measure residuals.

**Trigger.** Any availability, durability, disaster recovery or rollback claim with material consequence.

**Cheap path / non-trigger.** Low-consequence disposable state that can be regenerated and whose loss is explicitly accepted.

**Dependencies and preconditions.** Immutable backups/logs, independent access, compatible tooling, capacity, validation oracle, runbook and ownership.

**Failure/timing/consistency boundary.** Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence. Recovery point/time objectives are evidence-backed, not inferred from backup existence. The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.

**Authority/delivery/recovery/observability boundary.** Restored configuration, ownership generation and membership are current; old writers are fenced. Replay/redelivery uses original identities and does not duplicate unclosed effects. Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. Recovery progress, gaps, validation, divergence and residual unknowns are visible.

**Payoff and consumer.** Converts recovery design into current empirical evidence and exposes hidden dependencies before crisis. Consumer: Data owner, operator, incident commander and assurance reviewer.

**Known failure modes.**
- Sample restore not full scale
- Credentials expire
- Restore tooling obsolete
- RPO/RTO omit replay/catch-up
- Recovered data not semantically validated

**Important criticisms.**
- Rehearsals cost time and resources
- Destructive tests need isolation
- Passing one scenario does not cover all common modes

**Evolution.** From backup existence checks to end-to-end restore, failover, reconciliation and return-to-service exercises.

**Mature form.** Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.

**Ceremony boundary.** A backup job marked successful is not a restore path.

**Evidence.** Primary: [S017], [S071], [S072]. Critical: [S074], [S073], [S091]. Empirical/outage: [S073], [S074].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- What minimum rehearsal frequency is justified for low-frequency but catastrophic common modes?

### P39 — Schema, wire protocol and event evolution under mixed versions

**Status:** `RETAINED_IN_EVOLVED_FORM`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Database schema evolution, protocol negotiation, online upgrades and event-log replay.

**Original form.** Old and new producers, consumers, stored events and replicas must interoperate during rollout, rollback and replay.

**Problem and distributed failure.** Rolling upgrades create a mixed-version distributed system even when every binary is individually healthy. Components observe incompatible schemas/protocols at different times and old events outlive the code that wrote them.

**Failure prevented.** Decode failure, silent field loss, semantic reinterpretation, replay breakage and rollback impossibility.

**Mechanism.** Version schemas/protocols; define backward/forward compatibility; use additive/staged changes; negotiate capabilities; retain old-reader/writer tests and migration/rollback plan.

**Trigger.** Rolling deployment, long-lived event/log data, external clients, multiple regions or replayable workflow history.

**Cheap path / non-trigger.** Atomic offline upgrade of one local process/store with no concurrent old reader/writer and acceptable downtime.

**Dependencies and preconditions.** Version inventory, compatibility matrix, contract tests using real historical data, field semantics and rollback/downgrade policy.

**Failure/timing/consistency boundary.** Mixed versions, incompatible wire/schema changes, stale configuration, control-plane/data-plane skew and rollback incompatibility. Propagation is asynchronous; 'flag set' or 'deployment complete' is not proof every component observed it. Readers/writers define compatibility across old/new schemas and replayed historical events.

**Authority/delivery/recovery/observability boundary.** Current configuration/version authority and staged rollout state are reconstructable. Messages/events are versioned and unknown fields/semantics handled deliberately. Rollback and replay paths are compatible with new writes; downgrade limits are explicit. Version distribution, configuration convergence and compatibility errors are visible.

**Payoff and consumer.** Allows continuous change without turning version skew into hidden partial failure. Consumer: Service/API owner, data platform, deployer, client and recovery operator.

**Known failure modes.**
- Field reused with new meaning
- Old writer overwrites new field
- New leader emits unreadable data
- Event replay invokes removed schema
- Rollback cannot parse new writes

**Important criticisms.**
- Compatibility layers accumulate debt
- Additive change is not always possible
- Syntactic compatibility can hide semantic incompatibility

**Evolution.** From stop-the-world migration to staged expand/migrate/contract, capability negotiation and replay-aware versioning.

**Mature form.** Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.

**Ceremony boundary.** 'Rolling deployment succeeded' is not protocol compatibility.

**Evidence.** Primary: [S052], [S057], [S077], [S078], [S079]. Critical: [S028]. Empirical/outage: [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should very long-lived event histories be retired without retaining every old semantic forever?

### P40 — Configuration and control-plane/data-plane currentness

**Status:** `RETAINED_IN_EVOLVED_FORM`  
**Lineage:** `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`, `CONVERGENT_ENGINEERING`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Versioned membership/configuration, online control systems and outage evidence from global configuration propagation.

**Original form.** Configuration is distributed state with identity, version, authority, propagation and rollback semantics.

**Problem and distributed failure.** A control plane accepts a change while data-plane components observe different versions or a bad value propagates globally. Asynchronous propagation, partial failure and rollback create configuration skew and stale control decisions.

**Failure prevented.** Split policy, incompatible membership, global common-mode outage and false belief that a flag is universally active.

**Mechanism.** Version and validate configuration; staged/canary propagation; monotone generations; convergence evidence; data-plane acknowledgements; safe rollback/kill switch; bound blast radius.

**Trigger.** Configuration affects routing, membership, schemas, resource limits, feature behaviour or authority across components.

**Cheap path / non-trigger.** Local static configuration changed atomically with the single process.

**Dependencies and preconditions.** Authoritative source, config version/provenance, validation, propagation topology, compatibility, rollback and independent emergency access.

**Failure/timing/consistency boundary.** Mixed versions, incompatible wire/schema changes, stale configuration, control-plane/data-plane skew and rollback incompatibility. Propagation is asynchronous; 'flag set' or 'deployment complete' is not proof every component observed it. Readers/writers define compatibility across old/new schemas and replayed historical events.

**Authority/delivery/recovery/observability boundary.** Current configuration/version authority and staged rollout state are reconstructable. Messages/events are versioned and unknown fields/semantics handled deliberately. Rollback and replay paths are compatible with new writes; downgrade limits are explicit. Version distribution, configuration convergence and compatibility errors are visible.

**Payoff and consumer.** Makes configuration changes observable, reversible state transitions rather than instantaneous intent. Consumer: Control-plane owner, deployer, operator and every data-plane consumer.

**Known failure modes.**
- Control plane says applied while nodes stale
- Bad config replicated globally
- Rollback incompatible with new data
- Node accepts old generation
- Recovery tool depends on failed control plane

**Important criticisms.**
- Staged rollout slows change
- Canaries may not represent global edge cases
- More control logic is itself a failure source

**Evolution.** From file distribution to versioned, observed, staged and bounded configuration state with currentness checks.

**Mature form.** Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.

**Ceremony boundary.** 'The feature flag is set' is not evidence every replica observed it.

**Evidence.** Primary: [S014], [S077], [S079]. Critical: [S075], [S076]. Empirical/outage: [S075], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can global configuration systems reduce common-mode blast radius without intolerable propagation delay?

### P41 — Current dependency topology and end-to-end readiness

**Status:** `RETAINED_IN_EVOLVED_FORM`  
**Lineage:** `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`, `CONVERGENT_ENGINEERING`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Distributed monitoring, service-dependency practice and outages where local health diverged from usable service.

**Original form.** A component is ready only for a declared effect path, with current dependencies, capacity and authority—not because its process answers.

**Problem and distributed failure.** Health endpoint is green while database, DNS, queue, credential, control plane or downstream effect path is stale/unusable. Dependencies fail independently and topology changes dynamically; local checks cover only one process.

**Failure prevented.** Traffic sent to unusable instances, false completion, cascading retries and delayed diagnosis.

**Mechanism.** Discover/version topology; separate liveness/readiness; exercise synthetic end-to-end paths; check dependency currentness/capacity and effect boundary; degrade by capability.

**Trigger.** Service depends on remote components or dynamic routing/ownership.

**Cheap path / non-trigger.** Standalone local process with no remote effect path, where process liveness is the whole service.

**Dependencies and preconditions.** Current topology, dependency contracts, credentials/routing, representative probes, consequence-safe synthetic operations and freshness bounds.

**Failure/timing/consistency boundary.** Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects. Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown. Telemetry consistency does not imply application-state consistency.

**Authority/delivery/recovery/observability boundary.** Source identity, configuration and topology provenance accompany observations. Trace context/correlation may be dropped, duplicated or sampled. Evidence survives or is intentionally preserved through failure and recovery. Coverage, sampling, missingness and uncertainty are first-class data.

**Payoff and consumer.** Routes and declares service based on usable capabilities rather than process existence. Consumer: Load balancer, orchestrator, operator and calling service.

**Known failure modes.**
- Probe bypasses real dependency
- Probe cached
- Synthetic path lacks write effect
- Dependency topology stale
- Probe load worsens incident

**Important criticisms.**
- End-to-end probes cost capacity and can mutate data
- No finite probe covers all paths
- Dependency awareness can create tight coupling

**Evolution.** From ping/process checks to capability-specific readiness, topology reconstruction and black-box effect tests.

**Mature form.** Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.

**Ceremony boundary.** A `/health` 200 response is not service readiness.

**Evidence.** Primary: [S008], [S064], [S080], [S081]. Critical: [S073], [S075], [S076], [S092]. Empirical/outage: [S073], [S075], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can end-to-end probes remain representative without causing harmful side effects or excess load?

### P42 — Distributed observability treated as partial, sampled evidence

**Status:** `USEFUL_BUT_EASILY_GAMED`  
**Lineage:** `HYBRID`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Distributed logs/metrics/traces, Dapper/X-Trace and later adaptive/retroactive tracing.

**Original form.** Telemetry helps reconstruct behaviour but carries missingness, delay, sampling and observer limits.

**Problem and distributed failure.** Complete-looking traces, stable aggregates or correlated logs are used as proof of a complete causal history or current state. Telemetry pipelines fail, sample, reorder and lag independently from the system observed.

**Failure prevented.** False diagnosis, missed rare failure, false authority/currentness and overconfident completion claims.

**Mechanism.** Record sampling/coverage/provenance; preserve high-value triggers; correlate but do not conflate clocks; combine black-box and white-box evidence; mark unknown spans/state.

**Trigger.** Diagnosis, currentness, completion, failure-model validation or causal reconstruction depends on distributed telemetry.

**Cheap path / non-trigger.** Local deterministic operation with direct authoritative state inspection.

**Dependencies and preconditions.** Trace-context propagation, source identity, clock/ingestion bounds, sampling design, retention, privacy/security and telemetry-outage handling.

**Failure/timing/consistency boundary.** Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects. Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown. Telemetry consistency does not imply application-state consistency.

**Authority/delivery/recovery/observability boundary.** Source identity, configuration and topology provenance accompany observations. Trace context/correlation may be dropped, duplicated or sampled. Evidence survives or is intentionally preserved through failure and recovery. Coverage, sampling, missingness and uncertainty are first-class data.

**Payoff and consumer.** Makes observability useful without treating a lossy observer as omniscient. Consumer: Operator, debugger, auditor, automated detector and incident commander.

**Known failure modes.**
- Head sample misses rare path
- Tail sample drops trace under overload
- Missing span looks like nonexecution
- Metric aggregate hides one unsafe operation
- Telemetry outage coincides with incident

**Important criticisms.**
- Full capture is expensive and privacy-sensitive
- Instrumentation changes timing
- Sampling strategies bias evidence

**Evolution.** From per-node logs to cross-layer traces, exemplars, triggered/retroactive collection and explicit coverage metadata.

**Mature form.** Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.

**Ceremony boundary.** A trace that looks complete is not a complete causal history.

**Evidence.** Primary: [S080], [S081], [S082], [S083]. Critical: [S089]. Empirical/outage: [S075], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can rare-path observability be improved without unacceptable cost, privacy risk or observer effect?

### P43 — Causal trace reconstruction and event provenance

**Status:** `RETAINED_IN_EVOLVED_FORM`  
**Lineage:** `CAUSALITY_AND_TIME_LINEAGE`, `HYBRID`, `CONVERGENT_ENGINEERING`  
**Evidence:** `HIGH`

**Historical origin.** Logical clocks, distributed snapshots, X-Trace/Dapper and trace-context standards.

**Original form.** Reconstruct enough causal and authority provenance to explain an operation across components, not merely correlate similar timestamps.

**Problem and distributed failure.** Logs share IDs/times but lack parentage, message/effect identity, configuration and authority generation. Events are reordered, sampled and emitted by processes with skewed clocks and changing topology.

**Failure prevented.** Incorrect root-cause order, inability to link retries/effects, and false claim that correlation proves causation.

**Mechanism.** Propagate trace and operation identity, parent/links, config/term/version and event source; preserve causal edges; annotate gaps and sampled branches.

**Trigger.** Debugging, audit, recovery or completion requires cross-component reconstruction.

**Cheap path / non-trigger.** One local process with deterministic logs and no remote effects.

**Dependencies and preconditions.** Stable identity, context propagation, causal model, clock uncertainty, sampling metadata, source provenance and retention.

**Failure/timing/consistency boundary.** Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects. Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown. Telemetry consistency does not imply application-state consistency.

**Authority/delivery/recovery/observability boundary.** Source identity, configuration and topology provenance accompany observations. Trace context/correlation may be dropped, duplicated or sampled. Evidence survives or is intentionally preserved through failure and recovery. Coverage, sampling, missingness and uncertainty are first-class data.

**Payoff and consumer.** Improves fault discrimination and links retries, authority changes and effects without inventing total order. Consumer: Debugger, incident investigator, recovery planner and auditor.

**Known failure modes.**
- Context dropped at async boundary
- Retry creates unrelated trace
- Clock order contradicts causality
- Sampling removes parent
- Same correlation ID reused

**Important criticisms.**
- Trace context can leak data
- High cardinality/cost
- Causal provenance cannot include unobserved physical events automatically

**Evolution.** From timestamped logs to explicit parent/link graphs, operation/effect identity and authority/configuration provenance.

**Mature form.** Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.

**Ceremony boundary.** Correlation IDs plus sorted timestamps are not causal proof.

**Evidence.** Primary: [S003], [S004], [S013], [S032], [S080], [S081], [S082]. Critical: [S083]. Empirical/outage: [S073], [S075].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can provenance cross organisations while respecting privacy and trust boundaries?

### P44 — Hypothesis-bound fault injection and recovery challenge

**Status:** `USEFUL_BUT_EASILY_BUREAUCRATISED`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`, `CONVERGENT_ENGINEERING`  
**Evidence:** `HIGH`

**Historical origin.** Software fault injection, production failure testing and chaos-engineering practice.

**Original form.** Empirically challenge a specific current failure/recovery claim under bounded, observable conditions.

**Problem and distributed failure.** Failure assumptions and runbooks remain untested, or chaos exercises become repetitive spectacle without decision consequence. Real distributed failures depend on timing, topology, load, persistence and recovery interaction that unit tests miss.

**Failure prevented.** Unknown failover/recovery behaviour, false confidence and discovery of critical coupling only during outage.

**Mechanism.** State hypothesis/invariant; choose representative fault schedule/load; bound blast radius; predeclare evidence/stop conditions; test recovery/reconciliation; record decision.

**Trigger.** Material claim about tolerance, failover, retry, restore, overload or state integrity whose assumptions can be safely challenged.

**Cheap path / non-trigger.** Static analysis/model checking/unit/integration test when the claim does not require distributed runtime failure; low-consequence system with no material uncertainty.

**Dependencies and preconditions.** Representative environment/configuration, observability, rollback, safety authority, current topology, consequence assessment and independent expected result.

**Failure/timing/consistency boundary.** Unexercised failure assumptions, non-representative injections, uncontrolled blast radius, missing observability and untested recovery. Injection timing/order and stop conditions are part of the experiment. The tested invariant/postcondition is explicit; steady-state proxy alone is insufficient.

**Authority/delivery/recovery/observability boundary.** Experiment authority, scope and rollback are bounded. Injected faults include loss, delay, duplicate/reorder where relevant. The experiment tests recovery and post-recovery reconciliation, not merely failure onset. Predeclared evidence and abort conditions must be available.

**Payoff and consumer.** Provides current empirical evidence and discovers integration faults outside formal or design models. Consumer: System owner, operator, assurance reviewer and incident-response planner.

**Known failure modes.**
- Injected fault not representative
- No load during test
- Test stops before recovery
- Observability misses failure
- Blast radius escapes
- Repeated ritual yields no change

**Important criticisms.**
- Production experiments carry risk
- Staging may not reproduce common modes
- Evidence for broad effectiveness remains heterogeneous

**Evolution.** From random process killing to hypothesis-, invariant-, load-, recovery- and decision-bound experiments plus systematic schedule generation.

**Mature form.** A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.

**Ceremony boundary.** 'Run chaos experiments' is not a general property.

**Evidence.** Primary: [S084], [S085], [S086], [S087], [S088], [S089], [S090], [S091]. Critical: [S099]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can chaos-engineering benefit be measured independently of adoption theatre and reporting bias?

### P45 — Distribution requires a named consumer and retains a cheap local path

**Status:** `STRONGLY_RETAINED`  
**Lineage:** `CONVERGENT_ENGINEERING`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Repeated contrast between local atomicity and the costs introduced by RPC, partial failure, microservices and distributed transactions.

**Original form.** Distribute only for a concrete need—failure independence, latency locality, scale, ownership/autonomy or separate lifecycle—and preserve the simpler non-trigger.

**Problem and distributed failure.** Remote boundaries are introduced because the architecture is fashionable rather than because they serve a requirement. Every unnecessary boundary adds delay, unknown outcomes, version skew, partial failure, observability and recovery state.

**Failure prevented.** Overengineering small/local problems and making correctness depend on infrastructure with no consumer.

**Mechanism.** Name the consumer, quantify its need, compare local/single-owner alternative, and keep distribution out of paths where it adds no payoff.

**Trigger.** Independent scaling, fault containment, geographic latency, ownership/autonomy or deployment lifecycle demonstrably outweighs coordination cost.

**Cheap path / non-trigger.** Co-locate code/state, use in-process calls and local transactions, or one durable owner.

**Dependencies and preconditions.** Workload/consequence evidence, ownership model, availability/latency target and explicit cost/complexity comparison.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Preserves engineering value while stripping cloud-native fashion and accidental distribution. Consumer: Architect, product owner, operations and the team bearing lifecycle cost.

**Known failure modes.**
- Future scale invoked without evidence
- Organisational boundary mistaken for runtime boundary
- Local path removed too early
- Remote API hides shared database/common mode
- Distribution consumer later disappears

**Important criticisms.**
- Needs can change
- Local design may create migration cost
- No universal threshold separates local from distributed

**Evolution.** From default networked decomposition to deliberate distribution with explicit trigger and reversible cheap path.

**Mature form.** Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.

**Ceremony boundary.** Microservices, queues, service mesh or consensus are not maturity indicators.

**Evidence.** Primary: [S002], [S043], [S044], [S093]. Critical: [S073], [S092]. Empirical/outage: [S073], [S075], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can teams preserve future optionality without paying distributed-system cost prematurely?

### P46 — Retire distributed machinery when its coordination consumer disappears

**Status:** `RETAINED_IN_EVOLVED_FORM`  
**Lineage:** `CONVERGENT_ENGINEERING`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `HIGH`

**Historical origin.** Operational experience with long-lived middleware, consensus, queues and service decompositions.

**Original form.** Coordination mechanisms are contingent means, not permanent institutions.

**Problem and distributed failure.** A queue, lock service, replica set, workflow, service boundary or global transaction remains after the invariant, scale or ownership need has vanished. Obsolete machinery continues generating partial failure, upgrade, recovery and observability burden.

**Failure prevented.** Ceremonial complexity, stale authority paths, unowned retries/backlogs and hidden single points of failure.

**Mechanism.** Periodically restate consumer and trigger; measure use; plan drain/migration; preserve evidence and rollback; collapse to local/simple path when justified.

**Trigger.** Mechanism has no current decision, invariant, workload or failure-domain consumer.

**Cheap path / non-trigger.** Keep mechanism only when removal would reintroduce a demonstrated failure or violate a current requirement.

**Dependencies and preconditions.** Usage/dependency inventory, migration/replay plan, retained data/identity semantics and safe decommission evidence.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Prevents coordination debt from becoming an irreversible part of the system. Consumer: Architecture owner, platform owner and operational teams.

**Known failure modes.**
- Hidden client remains
- Old events need replay
- Removing quorum changes failure coverage
- Dual-write migration creates divergence
- No owner for retirement

**Important criticisms.**
- Retirement itself is risky
- Latent future need may return
- Benefits are hard to quantify before removal

**Evolution.** From infrastructure accumulation to lifecycle ownership with explicit retirement conditions and evidence.

**Mature form.** Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.

**Ceremony boundary.** 'Standard platform component' is not a permanent justification.

**Evidence.** Primary: [S043], [S077], [S079], [S093]. Critical: [S073]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can retirement value be measured when avoided future incidents are counterfactual?

### P47 — Microservices automatically improve resilience

**Status:** `REJECTED_OR_DISFAVOURED`  
**Lineage:** `CLOUD_NATIVE_TRANSLATION`, `ONLY_ANALOGOUS`  
**Evidence:** `HIGH`

**Historical origin.** Service-oriented and microservice architecture advocacy, contradicted by distributed coordination and integrity evidence.

**Original form.** Decompose into independently deployable services and infer resilience from separation.

**Problem and distributed failure.** Deployment boundaries are mistaken for independent failure domains and semantic isolation. Calls, data and retries cross more failure boundaries while dependencies and shared control planes remain coupled.

**Failure prevented.** This candidate prevents no general failure; it can create coordination debt unless real isolation/ownership is established.

**Mechanism.** NO_GENERAL_PROPERTY. Evaluate each boundary for independent failure/deployment/ownership benefit, data integrity, retries, capacity and recovery.

**Trigger.** Retain a service boundary only when it creates a real independently operable/failing/owned capability.

**Cheap path / non-trigger.** Modular monolith, local module or co-located state when independent runtime failure is unnecessary.

**Dependencies and preconditions.** Independent data/authority, API semantics, capacity/isolation, end-to-end observability and recovery ownership.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Rejecting the automatic claim avoids architecture-by-brand while preserving useful service boundaries. Consumer: Architect, service owner and operations.

**Known failure modes.**
- Shared database/control plane
- Chatty synchronous fan-out
- Cross-service invariant lost
- Retry cascade
- Distributed transaction/saga complexity
- Version skew

**Important criticisms.**
- Microservices can genuinely improve autonomy and fault containment
- Monoliths can also be fragile
- Evidence is context-sensitive

**Evolution.** From decomposition as default modernity to boundary-by-boundary evaluation and selective recombination.

**Mature form.** A service boundary is justified by a named lifecycle, ownership, scale or failure-containment property and bears its distributed obligations.

**Ceremony boundary.** The rejected proposition is itself a cloud-native caricature.

**Evidence.** Primary: [S092], [S093]. Critical: [S073], [S075], [S076]. Empirical/outage: [S073], [S075], [S076].

**Contrary evidence / transfer limit.** Microservices can deliver real independent deployment and scaling; the rejected element is the automatic, general resilience inference.

**Open questions.**
- Which comparative empirical designs can isolate architecture shape from organisational maturity and workload?

### P48 — A queue absorbs overload

**Status:** `REJECTED_OR_DISFAVOURED`  
**Lineage:** `EVENT_LOG_AND_STREAMING_LINEAGE`, `OVERLOAD_AND_SERVICE_RESILIENCE_LINEAGE`, `ONLY_ANALOGOUS`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Simplified messaging/cloud architecture advice, contradicted by queueing limits and incident evidence.

**Original form.** Insert a durable queue and treat acceptance as availability/capacity.

**Problem and distributed failure.** Buffering delays visibility of overload but cannot create service capacity; backlog age and recovery work accumulate. Producer and consumer rates diverge under partial failure or demand spike.

**Failure prevented.** This candidate prevents no general overload failure; an unbounded queue can worsen it.

**Mechanism.** NO_GENERAL_PROPERTY. Use P29–P33: bound queue, propagate backpressure, admit/shed, budget retries and control recovery surge.

**Trigger.** A queue is justified for decoupling, durability or burst smoothing only with a capacity/consequence model.

**Cheap path / non-trigger.** Synchronous backpressured call or small bounded local buffer.

**Dependencies and preconditions.** Arrival/service rates, queue limits, deadlines, rejection semantics and drain capacity.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Rejects the false transformation of storage into throughput. Consumer: Service owner, queue operator and capacity planner.

**Known failure modes.**
- Disk exhaustion
- Expired work
- Head-of-line blocking
- Backlog recovery overload
- Caller retries accepted backlog

**Important criticisms.**
- Queues do absorb bounded bursts and decouple availability
- The problem is the unqualified claim, not queueing itself

**Evolution.** From buffering-as-resilience to bounded deferred work with backpressure and consequence policy.

**Mature form.** Queue value is stated—durability, decoupling or bounded burst absorption—and completion capacity remains explicit.

**Ceremony boundary.** Queue presence is not capacity.

**Evidence.** Primary: [S045], [S062], [S063], [S066]. Critical: [S073]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** A bounded queue can provide real durability and temporal decoupling; it cannot manufacture downstream capacity.

**Open questions.**
- How should queue value be estimated when service time and demand are heavy-tailed?

### P49 — Exactly-once delivery implies the business action occurs exactly once

**Status:** `REJECTED_OR_DISFAVOURED`  
**Lineage:** `MESSAGE_DELIVERY_LINEAGE`, `EVENT_LOG_AND_STREAMING_LINEAGE`, `ONLY_ANALOGOUS`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Transport/broker/stream-processing terminology promoted beyond its transactional boundary.

**Original form.** Treat an exactly-once processing/delivery feature as proof of one real-world effect.

**Problem and distributed failure.** Platform transactions close records, offsets or internal state but not arbitrary databases, APIs, payments, emails or physical actions. The external effect and platform commit fail independently; replies and retries remain ambiguous.

**Failure prevented.** This candidate prevents no general duplicate business effect outside the enclosed boundary.

**Mechanism.** NO_GENERAL_PROPERTY. State the exact atomic closure; use semantic operation identity, idempotency, transaction participation, fencing or compensation for remaining effects.

**Trigger.** Retain platform exactly-once semantics only for operations inside its documented transaction boundary.

**Cheap path / non-trigger.** At-least-once plus semantic idempotency, or one local transaction, when simpler and sufficient.

**Dependencies and preconditions.** Precise delivery/processing/effect boundary, operation identity, dedup horizon, external effect semantics and recovery.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Prevents vendor terms from silently widening into false business guarantees. Consumer: Application owner, broker/stream operator, workflow and business owner.

**Known failure modes.**
- External API called twice
- Offset committed separately
- Key expires
- Retry changes parameters
- Side effect irreversible

**Important criticisms.**
- Some integrated platforms genuinely provide exactly-once processing within scope
- Terminology is overloaded rather than always false

**Evolution.** From delivery slogan to boundary-qualified exactly-once processing/effect and explicit end-to-end closure.

**Mature form.** Say exactly once only with the noun and boundary: record processing, state transition or verified effect under stated assumptions.

**Ceremony boundary.** Unqualified 'exactly once' is ceremony.

**Evidence.** Primary: [S046], [S049], [S054], [S059]. Critical: [S043], [S044], [S055]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Exactly-once processing is attainable inside carefully closed transactional/runtime boundaries; the rejected claim is automatic promotion to arbitrary external effects.

**Open questions.**
- Can industry converge on non-misleading terminology for scoped exactly-once guarantees?

### P50 — Distributed lock alone makes concurrent mutation safe

**Status:** `SUPERSEDED_BY_STRONGER_FORM`  
**Lineage:** `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `FAULT_TOLERANCE_LINEAGE`, `ONLY_ANALOGOUS`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Distributed mutual exclusion and lock-service practice, refined by leases, epochs and fencing.

**Original form.** Acquire a distributed lock and assume no other actor can mutate.

**Problem and distributed failure.** A delayed or paused former holder resumes after lease expiry or ownership transfer; the protected resource cannot distinguish it. Lock service and protected resource have separate failure/timing domains.

**Failure prevented.** The lock alone does not prevent stale writes after handoff.

**Mechanism.** Supersede with P13: monotone fencing generation enforced at every protected resource, or use semantic idempotency/conditional versioning.

**Trigger.** A lock may still coordinate efficiency or reduce contention, but correctness-critical mutation requires stale rejection.

**Cheap path / non-trigger.** Local mutex/local transaction, one durable writer, commutative operation or resource-native compare-and-swap.

**Dependencies and preconditions.** Current lock/lease authority, generation, resource enforcement, pause/partition model and multi-resource closure.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Preserves useful coordination while removing unsafe reliance on client self-restraint. Consumer: Lock-service user, scheduler, storage/API owner.

**Known failure modes.**
- GC pause
- Lease expiry unnoticed
- Network partition
- External sink ignores token
- Lock token rolls back

**Important criticisms.**
- Some lock services integrate fencing/conditional writes
- Not every efficiency lock needs correctness-level fencing

**Evolution.** From mutual exclusion/lease ownership to resource-enforced generation and effect-boundary analysis.

**Mature form.** Lock is advisory evidence; the mutation is safe because stale generations cannot take effect.

**Ceremony boundary.** 'Lock acquired' is not proof of current mutation authority.

**Evidence.** Primary: [S035], [S070], [S094]. Critical: [S095]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** A lock can be sufficient inside a single failure/timing boundary or when the resource and lock service share an atomic generation check.

**Open questions.**
- How can legacy/third-party resources be wrapped with effective fencing?

### P51 — Named infrastructure or repeated ritual as an engineering property

**Status:** `CEREMONY_NOT_GENERAL_PROPERTY`  
**Lineage:** `CLOUD_NATIVE_TRANSLATION`, `ONLY_ANALOGOUS`  
**Evidence:** `HIGH`

**Historical origin.** Cloud-native tooling, consensus folklore, event-sourcing fashion and chaos-engineering ritual.

**Original form.** Install a consensus cluster, message broker, service mesh, workflow engine or chaos platform and infer the corresponding property.

**Problem and distributed failure.** Artefact presence substitutes for a protected invariant, failure model, evidence consumer and completion/recovery semantics. Tooling adds new partial failures and dependencies while leaving the intended property unestablished.

**Failure prevented.** NO_GENERAL_PROPERTY; the named artefact may help implement a property but prevents nothing by mere presence.

**Mechanism.** Map artefact to property, assumptions, trigger, cheap path, evidence and retirement condition; remove or narrow when no consumer exists.

**Trigger.** Only when the artefact implements a named property whose payoff exceeds its own lifecycle cost.

**Cheap path / non-trigger.** Local code/state, existing transactional store, simpler ownership or targeted test.

**Dependencies and preconditions.** Property owner, invariant/consumer, failure model, integration evidence, operational capacity and exit plan.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Strips branding while retaining mechanisms that actually establish authority, delivery, recovery or resilience. Consumer: Architect, reviewer, operator and budget owner.

**Known failure modes.**
- Dashboard-driven compliance
- Unused consensus service
- Event sourcing without replay semantics
- Chaos without recovery claim
- Service mesh hiding retry storms

**Important criticisms.**
- Standardised infrastructure can reduce implementation risk
- Shared platforms can amortise expertise
- Ceremony is contextual, not inherent in a tool

**Evolution.** From product/architecture labels to evidence-backed mechanism selection and lifecycle ownership.

**Mature form.** Infrastructure is replaceable; the property, assumptions and evidence survive substitution.

**Ceremony boundary.** This property is explicitly the ceremony-stripping rule.

**Evidence.** Primary: [S085], [S086], [S093], [S099]. Critical: [S073], [S076]. Empirical/outage: [S073], [S076].

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How can organisations distinguish healthy standardisation from cargo-cult platform adoption?

### P52 — Byzantine/adversarial fault tolerance only under an explicit adversarial model

**Status:** `DOMAIN_SPECIFIC`  
**Lineage:** `FAULT_TOLERANCE_LINEAGE`, `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `DOMAIN_SPECIFIC`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Byzantine agreement and practical Byzantine state-machine replication.

**Original form.** Replicate/agree despite arbitrary or malicious replica behaviour under authentication and threshold assumptions.

**Problem and distributed failure.** Crash-fault systems are described with Byzantine terminology without modelling compromised replicas, identities, cryptographic trust or correlated implementation faults. Participants can send conflicting, malformed or strategically adversarial messages rather than merely stop.

**Failure prevented.** Agreement/safety loss caused by up to the modelled number of arbitrary faulty participants.

**Mechanism.** Use authenticated BFT protocol, 3f+1-style or protocol-specific threshold, independent administrative/failure domains, key/identity governance and deterministic validation.

**Trigger.** Actual threat model includes mutually distrustful or compromise-prone participants and the cost is justified.

**Cheap path / non-trigger.** Crash-fault consensus, single authority, audited replication or simpler integrity checks when adversarial participants are not a credible failure.

**Dependencies and preconditions.** Adversary/corruption model, authentication, identity/key lifecycle, independence, quorum threshold, denial-of-service/liveness assumptions and implementation assurance.

**Failure/timing/consistency boundary.** Domain-specific crash, omission, arbitrary/value, model, scheduling and external-service failures. Domain workload and latency model must be stated. Domain semantic validity remains separate from replicated agreement or durable execution.

**Authority/delivery/recovery/observability boundary.** Agent/service/model/tool authority and version are explicit. Calls can be duplicated, omitted, delayed or return malformed/semantically invalid values. State/context, tool effects and human escalation are durable and reconcilable. Prompt/model/tool version, causal provenance and validation evidence are captured within privacy/security limits.

**Payoff and consumer.** Provides a distinct agreement property where arbitrary faults are genuinely in scope. Consumer: Adversarially exposed replicated service, multi-party system or high-consequence integrity owner.

**Known failure modes.**
- Common software exploit compromises >f replicas
- Key theft collapses identity model
- DoS breaks liveness
- Clients/gateways outside model
- Economic/social adversary differs from protocol model

**Important criticisms.**
- High cost/latency/complexity
- Often misapplied to ordinary common-mode failures
- Formal protocol does not secure implementation or operations

**Evolution.** From oral-message impossibility/thresholds to authenticated practical protocols and application-specific BFT designs.

**Mature form.** BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.

**Ceremony boundary.** 'Byzantine' is not a synonym for severe outage.

**Evidence.** Primary: [S005], [S096]. Critical: [S091], [S099]. Empirical/outage: None.

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- How should correlated supply-chain/implementation compromise be represented beyond the classic independent-fault threshold?

### P53 — Distributed AI and agentic systems as a bounded domain translation

**Status:** `UNRESOLVED`  
**Lineage:** `DOMAIN_SPECIFIC`, `WORKFLOW_ORCHESTRATION_LINEAGE`, `CLOUD_NATIVE_TRANSLATION`  
**Evidence:** `LOW`

**Historical origin.** Multi-agent planning, agent workflows, tool-calling systems and recent attempts to apply sagas, validation and chaos testing.

**Original form.** Treat agents/models/tools as independently failing distributed actors with durable context, operation identity, validation and effect reconciliation.

**Problem and distributed failure.** Probabilistic outputs, tool calls and context versions add semantic/value failure beyond crash/omission while familiar retry and workflow risks remain. Agents, models, retrieval stores and tools can omit, duplicate, delay, hallucinate or semantically conflict while external effects persist.

**Failure prevented.** Duplicate tools/effects, stale context, unvalidated plan execution, lost workflow state and false completion.

**Mechanism.** Durable workflow state, versioned context/model/tool provenance, constrained authority, semantic validation, idempotent/fenced tool effects, compensation and targeted fault injection.

**Trigger.** Autonomous or multi-agent system coordinates persistent work or external effects across independently failing services.

**Cheap path / non-trigger.** One model call with human review and no durable/external effect; deterministic local program where suitable.

**Dependencies and preconditions.** Agent/task identity, model/prompt/tool versions, validator authority, external effect closure, human escalation and privacy/security constraints.

**Failure/timing/consistency boundary.** Domain-specific crash, omission, arbitrary/value, model, scheduling and external-service failures. Domain workload and latency model must be stated. Domain semantic validity remains separate from replicated agreement or durable execution.

**Authority/delivery/recovery/observability boundary.** Agent/service/model/tool authority and version are explicit. Calls can be duplicated, omitted, delayed or return malformed/semantically invalid values. State/context, tool effects and human escalation are durable and reconcilable. Prompt/model/tool version, causal provenance and validation evidence are captured within privacy/security limits.

**Payoff and consumer.** Transfers proven distributed-state disciplines while acknowledging probabilistic semantic uncertainty. Consumer: Agent-platform owner, workflow designer, tool/effect owner and human supervisor.

**Known failure modes.**
- Validation shares model failure
- Context fork/staleness
- Tool call duplicated
- Agent retries amplify cost/load
- Model update changes replay
- Goal completion self-reported

**Important criticisms.**
- Evidence is very recent and mostly prototypes/preprints
- Anthropomorphic 'agent' framing can obscure ordinary workflow design
- Semantic correctness lacks stable oracle

**Evolution.** Current translation is moving from chat/session memory to durable, validated, transaction-like agent workflows and fault injection.

**Mature form.** Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.

**Ceremony boundary.** 'Multi-agent' does not imply distributed-systems maturity.

**Evidence.** Primary: [S092], [S097], [S098]. Critical: [S055], [S056]. Empirical/outage: None.

**Contrary evidence / transfer limit.** Formal or implementation correctness does not establish that the deployed assumptions, external effects and operational boundary satisfy the claim.

**Open questions.**
- Whether agent-specific reliability mechanisms form genuinely new general properties remains unresolved.
- Operational field evidence and independent replication are sparse.

### P54 — Default global consensus or coordination for all distributed state

**Status:** `REJECTED_OR_DISFAVOURED`  
**Lineage:** `CONSENSUS_AND_MEMBERSHIP_LINEAGE`, `DISTRIBUTED_DATABASE_LINEAGE`, `ONLY_ANALOGOUS`  
**Evidence:** `VERY_HIGH`

**Historical origin.** Consensus folklore and overgeneralisation from strong consistency/transactions.

**Original form.** Put every state transition through one global order or distributed lock because distribution exists.

**Problem and distributed failure.** Coordination is used without a non-confluent invariant or current-authority consumer. Global quorum/leader becomes latency, availability and throughput dependency; failure domain expands.

**Failure prevented.** No general failure is prevented when operations commute, partition safely, tolerate staleness or can be locally owned.

**Mechanism.** NO_GENERAL_PROPERTY. Start with P14/P45; use P16 for safe autonomy and P15 only for the minimal non-confluent invariant.

**Trigger.** Strong coordination triggers only for an explicit invariant/current authority that cannot be preserved by local ownership, partitioning, commutativity, escrow or compensation.

**Cheap path / non-trigger.** Local transaction, single writer, CRDT/invariant-confluent operation, partitioned ownership or asynchronous durable handoff.

**Dependencies and preconditions.** Invariant analysis, operation algebra, failure/latency target, membership and recovery evidence.

**Failure/timing/consistency boundary.** Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer. No general timing model; the claim fails because a named artefact is substituted for an engineering property. No guarantee follows from branding alone.

**Authority/delivery/recovery/observability boundary.** No authority follows from deployment labels alone. No delivery/effect semantics follow from tooling labels alone. No recovery evidence follows from having a component installed. Dashboards and green checks are proxies unless tied to a claim.

**Payoff and consumer.** Avoids global bottlenecks and availability loss while retaining coordination where it actually buys correctness. Consumer: Application/data architect and invariant owner.

**Known failure modes.**
- Global leader bottleneck
- Quorum loss stops unrelated work
- Cross-region latency
- Huge reconfiguration blast radius
- Lock ordering deadlock

**Important criticisms.**
- Under-coordination can silently violate invariants
- Simplicity of one order can outweigh cost at modest scale

**Evolution.** From one-size-fits-all strong ordering to invariant-scoped coordination and hybrid systems.

**Mature form.** Coordinate only the state/effect closure whose independent execution would violate the named invariant.

**Ceremony boundary.** 'Distributed means consensus' is the rejected caricature.

**Evidence.** Primary: [S025], [S027], [S038], [S039]. Critical: [S011], [S036], [S040]. Empirical/outage: [S073].

**Contrary evidence / transfer limit.** Global ordering can be the simplest correct choice at modest scale when a central invariant dominates; the rejected element is defaulting without that consumer.

**Open questions.**
- How can teams reliably discover hidden non-confluent invariants before removing coordination?

The JSON property ledger contains the same 54 records plus all failure, causality/currentness, replication/consistency, delivery/idempotency, authority/fencing, recovery and evidence-strength profiles.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_FAILURE_MODEL

### Failure taxonomy and consequences

| Failure | Meaning | What can still be guaranteed | Common mistaken inference | Properties | Sources |
| --- | --- | --- | --- | --- | --- |
| CRASH_STOP | Process halts and never returns. | Consensus/replication may tolerate bounded failures; no restart-state problem. | Real systems often restart, so crash-stop alone can overstate transfer. | P01,P11 | S006,S007,S009 |
| CRASH_RECOVERY | Process halts and later returns, possibly with only durable state. | Protocol state, identity and epochs must survive; rejoin/catch-up is explicit. | Lost/rolled-back vote, config or dedup state can violate assumptions. | P01,P10,P12,P20,P37 | S008,S010,S012 |
| OMISSION | Send/receive/storage operation is omitted. | Retry/reconciliation may restore progress; omission cannot be distinguished from delay immediately. | Blind retry can duplicate effects or overload. | P02,P17,P32 | S044,S067 |
| DELAY_OR_SLOW_PROCESS | Messages or computation take arbitrarily/very long. | Safety should not require a correct timeout; liveness may rely on eventual bounds. | Timeout/lease may falsely suspect; paused actor can resume stale. | P02,P05,P11,P13,P26 | S007,S008,S035 |
| MESSAGE_LOSS | A request, reply or acknowledgement disappears. | Delivery/retry semantics and operation identity govern recovery. | Lost reply after effect creates unknown outcome. | P02,P17,P18,P21 | S043,S044,S102 |
| DUPLICATION | Request/message/activity is delivered more than once. | Semantic idempotency/dedup/fencing/compensation. | Finite dedup horizon and external effects remain risks. | P17,P18,P19,P20,P26 | S044,S049,S069 |
| REORDERING | Messages/events arrive in a different order. | Protocol sequence numbers, causal metadata or commutative operations. | Transport/log order may not match causality or semantics. | P04,P08,P17 | S003,S030,S047 |
| NETWORK_PARTITION | Some components communicate internally but not across a cut. | Safety/availability choice is model-specific; authority and currentness must be explicit. | Split brain, stale reads and recovery backlogs can outlast the partition. | P02,P06,P10,P11,P13,P37 | S025,S026,S073 |
| PAUSE_OR_GC | Process retains state/credentials but stops making progress, then resumes. | Lease expiry is suspicion; fencing or semantic duplicate protection is required. | Former owner may mutate after handoff. | P05,P13,P26,P50 | S035,S070,S095 |
| CLOCK_DRIFT_OR_JUMP | Clock rate/offset changes or time steps. | Use uncertainty bounds/monotonic clocks; avoid sole reliance for authority. | TTL, lease and freshness claims can fail silently. | P05,P06 | S034,S035,S036 |
| STORAGE_OMISSION_OR_CORRUPTION | Durable state is lost, reordered, corrupted or returns an error. | Checks, replicated/validated recovery, fault injection and source selection. | Replication can propagate bad state; protocol proofs may assume stable storage. | P01,P03,P09,P35,P36,P38 | S088,S091 |
| COORDINATOR_FAILURE | Transaction/workflow/leader coordinator fails mid-state. | Durable coordinator state, election/recovery protocol and in-doubt status. | Blocking, duplicated dispatch or heuristic decisions. | P11,P23,P25,P26 | S018,S050,S052 |
| STALE_CACHE_OR_REPLICA | Reachable component serves old state. | Session/currentness contract and version/membership evidence. | Green health and low age are weak proxies. | P06,P07,P09,P41 | S029,S031,S073 |
| CORRELATED_INFRASTRUCTURE_FAILURE | Multiple replicas/control paths share a common cause. | Explicit failure-domain and recovery-path independence. | Zones/regions/software/control plane may share fate. | P03,P38 | S075,S076,S091 |
| OPERATOR_OR_CONFIGURATION_FAILURE | Human/tool emits a bad change or recovery action. | Versioned staged config, validation, bounded propagation and independent rollback. | Configuration is often a highly connected common mode. | P03,P39,P40,P44 | S075,S076,S077 |
| RETRY_INDUCED_OVERLOAD | Failures/timeouts cause demand amplification. | Retry budget, jitter, backpressure, shedding and metastability analysis. | Local retry logic can create global persistent failure. | P29,P30,P31,P32,P33 | S062,S063,S067 |
| PARTIAL_REGION_FAILURE | Some regional dependencies/control/data paths fail while others remain. | Current topology, failure domains, authority transfer and capacity-aware failover. | Failover can double load or select stale state. | P03,P33,P37,P41 | S036,S073,S075 |
| BYZANTINE_OR_ARBITRARY | Participant sends conflicting/malicious/invalid messages. | BFT protocol under explicit threshold/authentication/identity assumptions. | Common-mode compromise and DoS may exceed classic model. | P52 | S005,S096 |
| SEMANTIC_VALUE_FAILURE | Component returns a syntactically successful but wrong/invalid value. | Application validation and invariant/effect checks; relevant in agentic systems too. | Consensus/durability can preserve a wrong value perfectly. | P07,P11,P27,P53 | S092,S097,S098 |

### Core failure-model properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P01 | Explicit distributed failure, timing, network, storage and recovery model | FAILURE_MODEL_PROPERTY | Any correctness or completion claim spanning independently failing processes, stores, networks or administrative components. | A local call, local transaction or one durable process when no independent remote failure boundary is required. | An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path. |
| P02 | Partial failure and unknown-outcome semantics | STRONGLY_RETAINED | Remote mutation, distributed commit, task dispatch or external side effect whose response can be lost. | Local atomic mutation with a definitive return, or a harmless repeatable read. | Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it. |
| P03 | Failure-domain independence and common-mode awareness | FAILURE_MODEL_PROPERTY | Replication, quorum, backup, multi-zone/region, control-plane or failover claim. | One durable copy plus tested backup where hot availability is unnecessary and consequence permits it. | Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths. |

### Required distinctions

```text
no response != failed
timeout expired != operation did not commit
component alive != component useful
network reachable != dependency state current
failure detector suspects != failure established
independent replicas != independent failure domains
```

The mature model is layered. A protocol may tolerate crash-stop while the deployed system actually has crash-recovery, storage corruption, clock jumps, configuration skew and shared control-plane failures. Progress assumptions must be stated separately from safety, and recovery transitions must remain inside the model.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_CAUSALITY_AND_TIME_MODEL

| Mechanism/model | What it establishes | Payoff | Does not establish | Properties |
| --- | --- | --- | --- | --- |
| Wall-clock timestamp | Physical clock reading at a node. | Useful for age/order only under error/drift and observation assumptions. | Not automatically causal, globally exact or current authority. | P04,P05 |
| Lamport logical clock | Order consistent with happens-before; may order concurrent events arbitrarily when totalised. | Causal-compatible sequencing and tie-breaking. | Cannot detect concurrency alone or give physical freshness. | P04 |
| Vector/dependency clock | Captures causal precedence/concurrency for known participants/events. | Conflict detection, causal delivery and session dependencies. | Metadata growth, pruning and membership challenges. | P04 |
| Hybrid logical clock | Physical-like timestamp with logical causality component. | Close-to-wall time plus causality for database operations. | Still relies on implementation/clock assumptions and does not supply semantic merge. | P04,P05 |
| Bounded-time interval | Physical time plus uncertainty bound. | External-consistency/lease/freshness designs when bound is monitored. | If uncertainty exceeds bound, claimed order/authority must degrade or stop. | P05 |
| Sequencer/log order | Order established by current authoritative log/leader/partition. | Deterministic replay or invariant requiring that order. | Not real-world causal order across independent sources unless linked. | P04,P10,P11 |
| Event time | Timestamp assigned to the event domain. | Windowing and business-time analysis. | May arrive late/out of order and can be wrong/untrusted. | P04 |
| Processing/observation time | When a system processed/observed an event. | Operational latency and watermarks. | Does not prove when external event occurred. | P04 |
| Freshness/currentness | Evidence that observed state is new enough/current for a decision. | Reads, failover, completion and session monotonicity. | Separate from causality and reachability. | P06 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P04 | Causal order distinguished from wall-clock and arbitrary total order | CAUSALITY_CURRENTNESS_PROPERTY | Correctness depends on whether one event could have influenced another, read-your-writes or dependency application. | Single-thread/local transaction order, or independent commutative operations with no causal consumer. | Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately. |
| P05 | Bounded-clock use and time-based authority with uncertainty margin | ASSUMPTION_SENSITIVE | Leases, TTLs, freshness SLAs, event-time windows or external-consistency designs. | Logical/causal clocks, non-time-based generations, or local timeout used only as a heuristic. | Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters. |
| P06 | Currentness, freshness and session guarantees as explicit evidence | CAUSALITY_CURRENTNESS_PROPERTY | Read result drives mutation, completion, failover, user-visible monotonicity or safety-sensitive decision. | Immutable content, best-effort analytics or explicitly stale cache with no authority claim. | A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown. |

### Required distinctions

```text
later wall-clock timestamp != causally later
log order != real-world causal order unless established
clock synchronized != exact global time
last writer wins != semantically correct conflict resolution
lease not expired locally != authority current globally
```

A mature system uses the weakest order that satisfies its consumer. Causality, freshness, total order, external consistency, event time and observation time are named independently. Physical time is useful when uncertainty is bounded and monitored; logical/causal mechanisms avoid pretending time is exact.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_REPLICATION_AND_CONSISTENCY_MODEL

| Replication form | Property | Useful context | Critical boundary | Properties |
| --- | --- | --- | --- | --- |
| Primary/backup or leader/follower | One current writer, replicated followers. | Simple mutation order; strong reads if current leader/follower conditions hold. | Failover needs state validation and fencing; followers may be stale. | P03,P06,P13,P37 |
| Active/state-machine replication | Replicas execute same ordered deterministic commands. | Strong replicated service under protocol model. | Nondeterminism, invalid commands and membership/storage bugs remain. | P07,P11 |
| Quorum replication | Read/write/decision sets intersect under configuration. | Flexible availability/consistency tradeoff. | Intersection is configuration-specific; currentness and semantic validity separate. | P10 |
| Multi-leader | Several authorised writers accept work. | Geo latency/autonomy. | Conflict semantics, causality and authority handoff become central. | P04,P08,P16 |
| Epidemic/anti-entropy | Replicas exchange version/digest/state until convergence. | Disconnected/highly available operation. | No inherent deadline; repair can propagate corruption or overload. | P09 |
| CRDT | Operations/state satisfy algebraic convergence conditions. | Coordination-free merge under stated operation/delivery model. | Arbitrary business invariants and schema evolution are not solved. | P08,P16 |
| Synchronous geo transaction | Replicated commit and concurrency control across regions. | Strong global invariant and external order where cost is justified. | Latency, clock/quorum assumptions and common modes matter. | P05,P15,P23 |
| Session/causal replica contract | Client dependencies constrain which replica/version may serve. | User-visible monotonicity without full global order. | Tokens/dependencies must propagate across boundaries. | P04,P06,P07 |
| Eventual convergence | Absent new writes and with delivery/repair assumptions, replicas converge. | Availability and loose coupling. | No bounded staleness or semantic correctness follows. | P06,P07,P08,P09 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P07 | Consistency level and isolation as an operation-scoped contract | REPLICATION_CONSISTENCY_PROPERTY | Shared mutable state with concurrent actors or replicas. | Single-thread/local immutable data, or commutative/invariant-confluent operations tolerating declared anomalies. | Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised. |
| P08 | Semantic conflict resolution beyond replica byte convergence | REPLICATION_CONSISTENCY_PROPERTY | Offline, geo or multi-writer state where concurrent progress is valuable. | One current writer, local transaction or coordination when the invariant is non-confluent. | Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination. |
| P09 | Anti-entropy, convergence and repair with corruption/lag safeguards | REPLICATION_CONSISTENCY_PROPERTY | Eventually or asynchronously replicated state with a lag/disconnected-replica path. | Synchronous replicated object with no lag path, or immutable artefact verified at write time. | Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation. |

### Required distinctions

```text
replicated != available under common-mode failure
converged bytes != semantically valid state
quorum intersection != current authority under wrong membership/configuration
eventual convergence != bounded staleness
stronger consistency != always better system outcome
```

No single point on the consistency spectrum is the evolved answer. The retained property is a precise operation-scoped contract derived from the invariant and consumer, plus evidence that membership, storage and implementation satisfy it.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_CONSENSUS_MEMBERSHIP_AUTHORITY_MODEL

| Concept | Establishes | Condition | Does not establish | Properties |
| --- | --- | --- | --- | --- |
| Safety | No two correct participants decide incompatible values/logs. | Must hold despite modelled faults. | Does not imply progress or application validity. | P11 |
| Liveness | A decision/progress eventually occurs. | Requires timing/failure-detector/reachability assumptions. | Can be lost while safety holds. | P11 |
| Validity | Chosen value meets protocol/application predicate. | Needs input/state validation outside agreement. | Consensus can agree on bad value. | P11,P15 |
| Leader election | Chooses a coordinator in a term/view. | Simplifies ordering and replication. | Election alone does not fence prior leader or establish current data. | P12,P13,P37 |
| Membership | Defines legitimate participants and vote population. | Foundation of quorum/authority. | Stale or duplicated configuration invalidates majority reasoning. | P10,P12 |
| Reconfiguration | Changes membership while preserving decision continuity. | Elasticity, maintenance, replacement. | Needs overlap/joint/vertical or equivalent safe transition. | P12 |
| Fencing generation | Resource rejects mutations from older term/owner. | Protects against paused/partitioned stale actors. | Every sink must enforce or effect must be neutralised. | P13 |
| Quorum loss | Insufficient current members to decide. | Safe unavailability is often correct. | Manual fail-open can create split brain. | P10,P11 |
| BFT threshold | Agreement with up to modelled arbitrary faulty participants. | Adversarial/mutually distrustful setting. | Authentication, independence and DoS/implementation assumptions remain. | P52 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P10 | Quorum validity bound to current membership and configuration | CONSENSUS_AUTHORITY_PROPERTY | Replicated decision, leader election, lock service or strong database read/write. | One current durable owner or local transaction. | A quorum certificate identifies current configuration, epoch and state position. |
| P11 | Consensus safety separated from liveness and semantic validity | CONSENSUS_AUTHORITY_PROPERTY | Replicated exclusive decision or ordered log whose divergence would violate an invariant. | Local durable owner, commutative/partitionable state or explicit manual arbitration. | Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately. |
| P12 | Versioned membership and safe reconfiguration | CONSENSUS_AUTHORITY_PROPERTY | Dynamic replica set, shard movement, autoscaling or disaster rebuild participating in authority. | Static single owner or whole-system offline replacement under an exclusive boundary. | Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff. |
| P13 | Current mutation authority enforced by epochs or fencing | CONSENSUS_AUTHORITY_PROPERTY | Exclusive writer, task lease, distributed lock, failover, shard ownership or maintenance handoff. | Local mutex/process ownership; commutative operation; local transaction with version check. | Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised. |
| P14 | Single-writer or local-transaction cheap path | STRONGLY_RETAINED | Low write scale, central invariant, tightly coupled data, modest availability demand or easy recovery. | This property is the cheap path; distribution triggers only after a concrete consumer appears. | Start local or single-writer; distribute only the dimension with demonstrated need. |
| P15 | Strong coordination for non-confluent invariants | STRONGLY_RETAINED | Demonstrated non-confluence, globally scarce resource or irreversible action requiring an exclusive current decision. | Independent commutative operations, ownership partitioning, escrowed budgets or one local owner. | Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation. |
| P16 | Coordination avoidance for invariant-confluent, commutative or partitionable operations | CONTEXT_DEPENDENT | High-latency or partitioned environment where operation semantics support safe independent execution. | Non-confluent uniqueness/conservation/exclusive authority or irreversible global effects should coordinate instead. | Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones. |

### Required distinctions

```text
leader elected != leader still current
lock held != stale holder cannot mutate
majority reachable != intended membership/configuration is correct
consensus on value != value is semantically valid
safety proved != liveness guaranteed under current timing
```

The central mature form is not “run consensus.” It is **configuration-indexed authority for a named invariant**, with safety/liveness/validity separated and stale mutation rejected at the protected resource.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_DELIVERY_IDEMPOTENCY_MODEL

| Mechanism/claim | Establishes | Useful context | Boundary/limit | Properties |
| --- | --- | --- | --- | --- |
| At-most-once attempt | Runtime suppresses duplicates or does not retry. | No duplicate processing from that mechanism. | May lose work; external effect scope can differ. | P17 |
| At-least-once delivery | Runtime retries/redelivers until acknowledged. | Higher chance work reaches consumer. | Consumer/effect must tolerate duplicates; overload risk. | P17,P19,P32 |
| Exactly-once processing | State/offset transition occurs once inside a closed runtime transaction. | Useful within integrated broker/state boundary. | Not arbitrary business effect exactly once. | P17,P22,P49 |
| Operation identity | Stable semantic ID binds attempts to one intent. | Basis for dedup, status, reconciliation. | Uniqueness alone is insufficient; parameters/scope matter. | P18 |
| Semantic idempotency | Repeated same operation leaves acceptable effect. | Safe retries/replay. | Downstream and expiry boundary must be closed. | P19 |
| Dedup window | Retention period for seen IDs/results/tombstones. | Finite-cost duplicate suppression. | Claims expire after the horizon. | P20 |
| Acknowledgement | Evidence a specific layer durably accepted/committed. | Progress and retry decision at that layer. | Does not prove downstream or real-world effect. | P21 |
| Outbox/inbox | Local transaction records state-message handoff and consumer dedup. | Reliable asynchronous bridge. | External third-party effect remains separate. | P22 |
| Poison/dead-letter path | Quarantines work that repeatedly fails. | Prevents infinite retry loop. | Can become unowned silent loss unless consequence/recovery defined. | P17,P31 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P17 | Duplicate-aware delivery semantics | DELIVERY_IDEMPOTENCY_PROPERTY | Asynchronous transfer, queue, event log, task dispatch or producer/consumer retry. | Direct local call/transaction or fire-and-forget telemetry where loss is accepted. | Name semantics at every boundary and independently close the business-effect boundary. |
| P18 | End-to-end business-operation and effect identity | DELIVERY_IDEMPOTENCY_PROPERTY | Retriable mutation, long-running workflow, external irreversible action or cross-service transaction. | Pure read, locally atomic mutation with no reply-loss concern, or disposable telemetry. | Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent. |
| P19 | Semantic idempotency, not request-ID ritual | DELIVERY_IDEMPOTENCY_PROPERTY | Any mutation or activity that may be retried, redelivered, replayed or concurrently submitted. | Pure read, commutative accumulation with duplicate identity, or one local transaction. | The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay. |
| P20 | Bounded deduplication and replay horizon | ASSUMPTION_SENSITIVE | Finite dedup cache, TTL, log retention, replay, delayed replica rejoin or disaster restore. | No retries/replay and bounded local execution, or effect is naturally harmless under repetition. | Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals. |
| P21 | Acknowledgement separated from verified external effect | DELIVERY_IDEMPOTENCY_PROPERTY | Multi-hop action, asynchronous processing, third-party/physical effect or workflow completion. | Single local transaction whose return covers the entire required state change. | Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated. |
| P22 | Transactional messaging or outbox/inbox closure | DELIVERY_IDEMPOTENCY_PROPERTY | A local transaction must reliably cause or record an asynchronous message, or a consumed event must update state exactly once within the closure. | Direct local state change with no asynchronous notification requirement. | The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit. |

### Required distinctions

```text
message exactly once != business side effect exactly once
duplicate message suppressed != duplicate external effect impossible
ACK returned != downstream world state established
retry-safe endpoint != whole workflow retry-safe
same idempotency key != same semantic operation after changed parameters
```

The mature form separates attempts, messages, processing, operations and effects. Each acknowledgement states its boundary; every deduplication claim states its retention horizon; retries preserve semantic identity and are safe at every effect boundary they can reach.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_TRANSACTION_AND_COMPENSATION_MODEL

| Mechanism | What it provides | Where it pays | Critical limit | Properties |
| --- | --- | --- | --- | --- |
| Local transaction | Atomicity/isolation in one database/resource. | Cheapest strong closure. | Remote/external effects excluded. | P14,P23 |
| Two-phase commit | Prepare then commit/abort across participants. | Atomicity for participating resources. | Blocking/availability and in-doubt state under failures. | P23 |
| Nonblocking/replicated commit variants | Add states, redundancy or consensus to improve recovery/progress. | Reduce selected blocking/latency under model. | More protocol/implementation complexity; still boundary-scoped. | P23 |
| Deterministic transaction ordering | Preorder transactions to simplify execution/commit. | High throughput under suitable workload/partitioning. | Ordering bottleneck and cross-partition cost remain. | P15,P23 |
| Saga | Sequence local commits with compensation. | Long-running/autonomous services. | Intermediate state and non-inverse/failed compensation. | P24 |
| Reservation/semantic lock | Reserve resource before later commit/cancel. | Reduces overcommit while retaining long workflow. | Reservation expiry/currentness and abandoned holds. | P15,P24 |
| Forward recovery | Apply new action to reach acceptable state rather than undo history. | Irreversible or changed external world. | Requires domain policy and residual validation. | P24 |
| Transactional message handoff | Local state plus outbox/offset-state closure. | Reliable event-driven transition. | Does not make arbitrary external effect atomic. | P22,P23 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P23 | Explicit transactional boundary and atomic-commit choice | TRANSACTION_COMPENSATION_PROPERTY | A non-compensatable invariant requires all-or-nothing across multiple transactional participants. | One local transaction; or independently commit compensatable steps with a durable saga. | Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation. |
| P24 | Compensation and forward recovery with semantic limits | TRANSACTION_COMPENSATION_PROPERTY | Long-running, cross-service or external workflow whose effects are compensatable or repairable but not globally atomic. | One atomic local/distributed transaction when the whole closure can and should commit together. | Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated. |

### Required distinctions

```text
database rollback != external side effect undone
compensation exists != original state restored
saga completed != all invariants globally atomic
transaction committed != downstream observation current
```

Atomic commit and compensation are neither universal substitutes nor enemies. Atomicity is retained for a small non-compensatable closure; compensation/forward recovery is retained where independent committed steps and external effects make rollback impossible.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_DURABLE_WORKFLOW_MODEL

| Workflow element | Role | Payoff | Failure boundary | Properties |
| --- | --- | --- | --- | --- |
| Workflow history/state | Durable transitions, timers, signals and task IDs. | Orchestration survives restart. | External world may diverge. | P25 |
| Orchestrator code | Replays or advances history. | Deterministic control decisions. | Version/nondeterminism can break replay. | P28 |
| Activity/task | Performs nondeterministic/external work. | Isolates effects from deterministic orchestration. | May execute more than once. | P26 |
| Lease/heartbeat | Evidence a worker is recently responsive. | Scheduling/re-dispatch heuristic. | Does not prove prior worker stopped. | P26 |
| Cancellation | Intent to stop waiting/work. | Controls future scheduling. | Cannot automatically retract committed/external effect. | P02,P24,P26 |
| Signal/timer | Durable external input or scheduled wake-up. | Long-running coordination. | Duplicate/late signal and version semantics matter. | P25 |
| Compensation | Balancing/repair step. | Recover partial workflow. | May fail or not restore original state. | P24 |
| Terminal state | Declared completion/failure/partial/unknown. | Downstream decision point. | DONE needs consumer-relevant postcondition evidence. | P27 |
| History migration/versioning | Keeps old runs compatible with new code/schema. | Continuous deployment. | Version debt and semantic drift. | P28,P39 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P25 | Durable workflow state as a recoverable distributed state machine | WORKFLOW_STATE_PROPERTY | Long-running, multi-step, retrying or externally signalled work that must survive process/platform restart. | Synchronous local call/transaction whose whole lifetime fits one reliable execution boundary. | Workflow history is authoritative for orchestration, while external state is independently validated where required. |
| P26 | Task ownership, lease expiry and duplicate-safe re-dispatch | WORKFLOW_STATE_PROPERTY | Task queue, visibility timeout, worker lease, heartbeat or automatic re-dispatch. | One local worker under a process-local lock, or harmless repeatable calculation with no effect. | Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation. |
| P27 | Completion defined by durable state plus verified postcondition | WORKFLOW_STATE_PROPERTY | Completion drives user notification, billing, next workflow, resource release or irreversible decision. | Local transaction return covers the complete required postcondition. | DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN. |
| P28 | Deterministic replay with explicit workflow/code version evolution | ASSUMPTION_SENSITIVE | Replay-based durable workflow, event sourcing or state reconstruction across code versions. | Persist explicit current state without replay, or finish short-lived work before incompatible deployment. | History, code and schema versions are explicit; every deployed version can replay or migrate all live histories. |

### Required distinctions

```text
worker report DONE != workflow effect verified
task lease expired != prior worker cannot still act
re-dispatched task != duplicate side effect safe
durable state persisted != current external world reconstructed
workflow replay deterministic != external dependency deterministic
```

Current durable-execution research confirms that persisting orchestration state is necessary but not sufficient. The evolved workflow carries semantic operation/effect identity, current task authority, versioned replay, compensation or transactional closure, and a consumer-relevant terminal postcondition.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_BACKPRESSURE_OVERLOAD_MODEL

| Mechanism | Role | Payoff | Limit | Properties |
| --- | --- | --- | --- | --- |
| Bounded queue | Finite deferred work by count/bytes/age. | Absorbs bounded bursts. | Cannot create service capacity. | P29 |
| Backpressure | Demand signal propagates upstream. | Prevents overload migration. | Can oscillate or stop at async/retry boundary. | P30 |
| Admission control | Decide before accepting work. | Preserves useful service/capacity. | Needs capacity and consequence model. | P31 |
| Load shedding | Reject/degrade work under scarcity. | Prevents all-work collapse. | Can be unfair or trigger retries. | P31 |
| Retry budget | Bounds attempts across layers. | Retains selective retry benefit. | Requires shared accounting and semantic safety. | P32 |
| Backoff + jitter | Spreads retries over time. | Reduces synchronised contention/herd. | Does not solve permanent error or insufficient capacity. | P32 |
| Deadline propagation | Stops work after value expires. | Avoids wasted downstream work. | Clock/currentness and cancellation semantics matter. | P02,P32 |
| Bulkhead | Separates resource pools/tenants/dependencies. | Contains blast radius. | May waste capacity and leak through shared bottlenecks. | P34 |
| Metastability control | Break positive feedback and reserve recovery capacity. | Enables exit after trigger removed. | Loops/topology may be unknown. | P33 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P29 | Bounded queues with explicit work-age and capacity semantics | OVERLOAD_BACKPRESSURE_PROPERTY | Asynchronous buffering between independently varying producer and consumer demand. | Direct synchronous flow with natural backpressure, or small fixed local buffer where overload consequence is acceptable. | Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour. |
| P30 | Backpressure propagated to the source of demand | OVERLOAD_BACKPRESSURE_PROPERTY | Producer can outpace consumer or fan-out multiplies work. | In-process bounded channel or naturally demand-driven iterator when no remote graph exists. | Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin. |
| P31 | Admission control and load shedding with consequence policy | OVERLOAD_BACKPRESSURE_PROPERTY | Demand can exceed sustainable service or shared bottlenecks can saturate. | Fixed small system with hard external demand limit and no shared saturation risk. | Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate. |
| P32 | Retry budgets, exponential backoff, jitter and deadline propagation | OVERLOAD_BACKPRESSURE_PROPERTY | Transient failure can plausibly recover within the remaining deadline and retry is semantically safe. | No retry for permanent errors, expired work, non-idempotent effect without closure or already-overloaded dependency. | A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity. |
| P33 | Metastable and cascading-overload containment | OVERLOAD_BACKPRESSURE_PROPERTY | Fan-out, shared bottleneck, retry/cache/failover/backlog loop or recovery surge can feed on itself. | Low-utilisation local system with no feedback path and trivial restart. | The failure model includes amplification and a tested path out of the degraded state. |
| P34 | Dependency isolation and bulkheads with end-to-end verification | CONTEXT_DEPENDENT | Shared resource pool or dependency whose slowness/failure can block unrelated work. | One small dependency path with no shared-resource contention or acceptable full-stop behaviour. | Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour. |

### Required distinctions

```text
queue accepting work != capacity exists to finish it
retries increase availability != retries always improve availability
more workers != more throughput under shared bottleneck
circuit open != dependency failure root cause resolved
load shed != request lost without explicit consequence policy
```

The model treats demand, retries, repair, failover and recovery as load. A system is not resilient merely because it survives the initial fault; it must avoid or escape the feedback loop that can sustain degradation.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_SNAPSHOT_CHECKPOINT_RECOVERY_MODEL

| Mechanism | Establishes | Payoff | Residual boundary | Properties |
| --- | --- | --- | --- | --- |
| Consistent snapshot | Coherent cut of internal state and in-flight messages/log positions. | Recovery point. | External effects and later corruption excluded. | P35 |
| Write-ahead/event log | Durable ordered record for redo/reconstruction. | Fine-grained recovery/audit. | Log gaps/schema changes and external effects remain. | P36 |
| Checkpoint + log | Bound replay by snapshot then apply later log. | Practical recovery speed. | Snapshot/log compatibility and truncation policy matter. | P35,P36 |
| Rollback recovery | Return distributed state to a consistent recovery line. | Recovers from crash. | Can lose accepted work; orphan/duplicate external effects. | P35,P36 |
| Failover | Move authority to surviving/restored state. | Availability. | Requires current state, membership and fencing. | P37 |
| Restore rehearsal | Empirical proof of artefact/tool/capacity path. | Current recovery evidence. | Covers only tested scenarios and scale. | P38 |
| External reconciliation | Compare/repair effects outside restored history. | End-to-end recovery. | May be manual or impossible. | P36 |
| Return to service | Validate data, authority, capacity and clients after recovery. | Avoids second outage. | Backlog/retry surge can destabilise. | P33,P37,P38 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P35 | Consistent distributed snapshot or checkpoint | RECOVERY_RECONSTITUTION_PROPERTY | Recovery, migration, rescaling or audit requires a cross-component state cut. | One local transactional snapshot or reconstructable stateless workers. | Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects. |
| P36 | Replay and restore with external-state reconciliation | RECOVERY_RECONSTITUTION_PROPERTY | Disaster restore, log replay, workflow history recovery or regional failover with external effects. | All state and effects are inside one local transactional restore boundary. | Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible. |
| P37 | Failover re-establishes current authority before mutation | RECOVERY_RECONSTITUTION_PROPERTY | Leader/primary/site/region failover or ownership transfer after suspected failure. | Manual offline recovery with verified old owner stopped, or one local process restart without concurrent actor. | Failover completes only after authority fencing, current-state selection and post-failover validation. |
| P38 | Tested restore and recovery-path evidence | STRONGLY_RETAINED | Any availability, durability, disaster recovery or rollback claim with material consequence. | Low-consequence disposable state that can be regenerated and whose loss is explicitly accepted. | Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals. |

### Required distinctions

```text
snapshot loaded != system externally consistent
log replay complete != irreversible external effects reconciled
backup exists != restore path works
failover happened != authority fencing completed
```

Recovery is a distributed state transition. It selects a coherent internal state, preserves or reconstructs membership and authority, fences obsolete actors, replays with original identities, reconciles external effects, validates postconditions and controls the recovery surge.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_SCHEMA_CONFIGURATION_EVOLUTION_MODEL

| Evolution dimension | Requirement | Payoff | Limit | Properties |
| --- | --- | --- | --- | --- |
| Wire compatibility | Old/new message decoders preserve fields and parsing. | Mixed-version transport. | Semantic meaning can still change. | P39 |
| Schema compatibility | Readers/writers tolerate added/removed/transformed data. | Rolling data migration. | Old writer can destroy new state. | P39 |
| Event compatibility | Historical events remain interpretable/replayable. | Long-lived logs/workflows. | Every old semantic cannot be retained forever. | P28,P39 |
| Protocol negotiation | Peers agree capabilities/version. | Avoid incompatible interaction. | Negotiation path can itself diverge. | P39 |
| Configuration generation | Applied config is versioned and attributable. | Current policy/membership evidence. | Control plane intent may not reach data plane. | P40 |
| Staged rollout | Canary/ring/region limits blast radius. | Safer change. | Canary may not represent global edge case. | P39,P40 |
| Rollback compatibility | Old code can read/process new writes/config. | Recovery from bad deploy. | Irreversible schema/data changes block rollback. | P39,P40 |
| Control/data-plane skew | Different components observe different config versions. | Must be detected and policy-defined. | Flag set is not global completion. | P40 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P39 | Schema, wire protocol and event evolution under mixed versions | RETAINED_IN_EVOLVED_FORM | Rolling deployment, long-lived event/log data, external clients, multiple regions or replayable workflow history. | Atomic offline upgrade of one local process/store with no concurrent old reader/writer and acceptable downtime. | Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier. |
| P40 | Configuration and control-plane/data-plane currentness | RETAINED_IN_EVOLVED_FORM | Configuration affects routing, membership, schemas, resource limits, feature behaviour or authority across components. | Local static configuration changed atomically with the single process. | Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid. |

### Required distinctions

```text
all binaries healthy != protocol compatible
schema migration complete != old consumers safe
new leader version != cluster configuration coherent
feature flag set != every replica observed it
```

Mixed-version operation is normal during rolling change and replay. Configuration is itself distributed state. Completion therefore requires population/version evidence, not merely control-plane intent.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_OBSERVABILITY_AND_STATE_RECONSTRUCTION_MODEL

| Evidence type | Strength | Use | Limit | Properties |
| --- | --- | --- | --- | --- |
| Logs | Detailed local events. | Forensics and semantic detail. | Clock order, missing records and volume. | P42,P43 |
| Metrics | Aggregates/rates/distributions. | Capacity and trend. | Can hide individual unsafe operation and causal path. | P29,P33,P42 |
| Traces | Cross-service request graph. | Latency/path attribution. | Sampling and missing context; not full causal history. | P42,P43 |
| Correlation ID | Join hint for related records. | Searchability. | Reuse/drop does not prove causality. | P18,P43 |
| Trace context | Interoperable propagation metadata. | Cross-vendor correlation. | Does not establish authority or completion. | P43 |
| Synthetic check | Black-box exercise of a capability. | End-to-end readiness. | May be unrepresentative or unsafe to mutate. | P41 |
| Authoritative state dump/query | Direct version/config/effect status. | Currentness/completion evidence. | May be unavailable/stale and needs provenance. | P06,P21,P41 |
| Sampling metadata | Probability/strategy/trigger and missingness. | Bounds inference. | Often omitted from incident conclusions. | P42 |
| Topology discovery | Current dependency/ownership graph. | Root-cause and readiness. | Topology itself is eventually consistent. | P41,P43 |

### Retained properties

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P41 | Current dependency topology and end-to-end readiness | RETAINED_IN_EVOLVED_FORM | Service depends on remote components or dynamic routing/ownership. | Standalone local process with no remote effect path, where process liveness is the whole service. | Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy. |
| P42 | Distributed observability treated as partial, sampled evidence | USEFUL_BUT_EASILY_GAMED | Diagnosis, currentness, completion, failure-model validation or causal reconstruction depends on distributed telemetry. | Local deterministic operation with direct authoritative state inspection. | Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available. |
| P43 | Causal trace reconstruction and event provenance | RETAINED_IN_EVOLVED_FORM | Debugging, audit, recovery or completion requires cross-component reconstruction. | One local process with deterministic logs and no remote effects. | Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence. |

### Required distinctions

```text
trace complete-looking != complete causal history
health endpoint green != dependency effect path healthy
metric aggregate stable != individual operation safe
logs correlated != authority/currentness established
```

Operators rarely have an automatically authoritative global view. Mature reconstruction combines current topology/configuration, versioned authoritative state where available, operation/effect identity and telemetry whose sampling, freshness and gaps are explicit.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_FAULT_INJECTION_AND_RESILIENCE_TEST_MODEL

| Injected condition | Claim challenged | Key question | Properties |
| --- | --- | --- | --- |
| Process kill/restart | Crash/recovery state and rejoin. | Does durable protocol/workflow state survive? | P01,P12,P25 |
| Delay/partition | Suspicion, split authority and backlog. | Does safety hold and recovery fence/reconcile? | P02,P10,P13,P37 |
| Message loss/duplicate/reorder | Delivery/idempotency/causality. | Can effects duplicate or dependencies break? | P17,P19,P20 |
| Clock jump/pause | Lease/TTL/currentness. | Does safety rely on local clock or timely actor? | P05,P13,P26 |
| Storage error/corruption | Durability/repair/recovery. | Does redundancy detect or spread bad state? | P03,P09,P36 |
| Overload/retry surge | Capacity feedback. | Can queues/retries drive metastability? | P29,P32,P33 |
| Regional/control-plane failure | Common mode/failover. | Are authority, capacity and recovery access independent? | P03,P37,P40 |
| Mixed-version/config skew | Compatibility/currentness. | Can old/new participants interoperate and rollback? | P28,P39,P40 |
| Restore/replay | Full recovery path. | Are external effects and authority reconciled? | P35,P36,P38 |
| Semantic/value fault | Application invariant/agent output. | Can agreement/durability preserve an invalid value? | P07,P11,P53 |

### Retained property

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P44 | Hypothesis-bound fault injection and recovery challenge | USEFUL_BUT_EASILY_BUREAUCRATISED | Material claim about tolerance, failover, retry, restore, overload or state integrity whose assumptions can be safely challenged. | Static analysis/model checking/unit/integration test when the claim does not require distributed runtime failure; low-consequence system with no material uncertainty. | A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action. |

The transferable property is **bounded empirical challenge of a specific current failure/recovery claim under representative configuration and load**. Randomness, production placement or repetition are not inherently mature. Evidence requires a hypothesis, protected invariant, observability, blast-radius and stop rules, recovery/reconciliation and a decision consequence.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_CEREMONY_STRIPPING_LEDGER

| Artefact or ritual | Transferable property | Always required? | Trigger | Cheap path | Anti-ceremony test | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| Consensus cluster | Mutually exclusive current authority or replicated decision under stated fault/timing/membership assumptions. | NO | Named non-confluent invariant or authority decision. | One durable owner/local transaction/commutative state. | Can the invariant and proof obligations be named without the product? | P10, P11, P12, P13, P15, P54 |
| Distributed lock | Prevent concurrent/stale writers from violating an invariant. | NO | Exclusive current mutation across failure boundaries. | Local mutex, local transaction, single writer, CAS. | Does the resource enforce a fencing generation? | P13, P50 |
| Message broker | Durable asynchronous transfer/queueing under declared delivery and retention semantics. | NO | Temporal decoupling, buffering or durable fan-out has a consumer. | Direct local/synchronous call with backpressure. | Are delivery, ACK, capacity, replay and effect boundaries stated? | P17, P22, P29, P48 |
| Event log / event sourcing | Ordered durable event identity supports reconstruction, replay and projections. | NO | History/replay/audit or stream processing requires it. | Current-state table plus audit entries where sufficient. | Can old histories replay through schema/code changes and reconcile external effects? | P20, P25, P28, P35, P36, P39 |
| Microservices | Independent deployment, ownership, scale or failure boundary where real. | NO | A boundary has a concrete independent consumer. | Modular monolith/coarse service/local transaction. | Does the boundary reduce shared fate or just add RPC and distributed invariants? | P34, P45, P47 |
| Service mesh | Standardised transport identity, policy, telemetry and traffic control. | NO | Many service paths need common transport controls and the mesh's own failure mode is accepted. | Library/gateway/local networking. | Does it own retry budgets, semantics and capacity—or merely hide them? | P32, P34, P41, P42, P51 |
| Workflow engine | Durable work state, retry/replay ownership, timers, signals, compensation and terminal semantics. | NO | Long-running distributed work must survive restart. | One synchronous local transaction/process. | Are external effects, code versions and DONE semantics closed? | P24, P25, P26, P27, P28 |
| Exactly-once setting | A specifically scoped processing/state transition occurs once under declared assumptions. | NO | Integrated state/offset transaction warrants cost. | At-least-once + semantic idempotency. | Exactly once *what*, at which boundary, for how long? | P17, P19, P20, P22, P49 |
| Three replicas / multi-AZ | Tolerate an explicit set of independent failures while preserving state/authority. | NO | Availability/durability consequence justifies replication. | One durable copy + independent tested backup. | Which common modes and recovery paths remain shared? | P03, P10, P38 |
| Leader election | Select a coordination point within a term/view. | NO | Protocol/invariant benefits from one current coordinator. | Static owner/local process. | Is data current and is stale authority fenced? | P11, P13, P37 |
| Health endpoint | Evidence that a declared capability/effect path is ready now. | CONTEXTUAL | Automated routing/recovery needs a signal. | Direct local check where process is the entire service. | Does it exercise dependencies, authority and capacity with known freshness? | P41, P42 |
| Chaos experiment / game day | Bounded empirical challenge of a current failure/recovery claim. | RISK_DEPENDENT | Material uncertainty cannot be closed by cheaper tests/evidence. | Unit/integration/model/property test. | What hypothesis, evidence, stop rule and decision change? | P44, P51 |
| Circuit breaker | Contain resource consumption and provide explicit degraded behaviour. | NO | Slow/failing dependency threatens shared capacity. | Simple concurrency/deadline limit. | Does open/half-open behaviour preserve critical work and avoid retry/recovery herd? | P31, P34 |
| Global transaction | Atomicity/isolation across a declared participant closure. | NO | Non-compensatable non-confluent invariant. | Local transaction + outbox/saga or ownership partition. | Which external resources actually participate and what blocks under failure? | P15, P23, P24 |
| Global timestamp / LWW | Deterministic tie-breaking or bounded-time order for a named consumer. | NO | Consumer truly needs that order and its assumptions hold. | Causal metadata, explicit merge, single writer. | Does timestamp order preserve causality and semantic conflict resolution? | P04, P05, P08 |
| Multi-region active-active | Regional availability/latency with multi-writer or ownership semantics. | NO | Geo availability/latency outweighs consistency and recovery complexity. | One active region + tested failover/read replicas. | How are ownership, consistency, common modes and failover capacity established? | P03, P06, P08, P10, P37 |

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_CRITICISM_LEDGER

| Criticism | Target | Evidence | Disposition | Surviving form | Sources |
| --- | --- | --- | --- | --- | --- |
| CAP reduced to permanent 'pick two' menu | CONSISTENCY_MODEL | Formal theorem is partition/asynchrony-specific; later analysis adds normal-operation latency tradeoffs and recovery design. | REFINED | P01/P07/P15: precise consistency, availability and partition behaviour per operation. | [S025], [S026], [S027] |
| Exactly-once promoted from platform processing to business effects | DELIVERY_OR_IDEMPOTENCY | Broker/workflow transactions close only declared records/state; external effects remain independent. | NARROWED | P17–P22; P49 rejected. | [S043], [S046], [S049], [S054], [S055] |
| Distributed locks leave stale writers | CONSENSUS_OR_MEMBERSHIP | Pauses/partitions can outlive leases; resource-side generation rejection is required. | SUPERSEDED_BY_STRONGER_FORM | P13 fencing; P50 rejected as general guarantee. | [S035], [S070], [S094], [S095] |
| Quorum arithmetic ignores membership/configuration and failure domains | CONSENSUS_OR_MEMBERSHIP | Intersection is relative to a configured population; reconfiguration and durable identity matter. | REFINED | P03/P10/P12. | [S011], [S012], [S014], [S015] |
| Leader election conflated with current authority | CONSENSUS_OR_MEMBERSHIP | Election does not fence stale actors or prove current data. | REFINED | P13/P37. | [S010], [S012], [S095] |
| Wall-clock/LWW conflict resolution gives semantic correctness | CONSISTENCY_MODEL | Clock limits and causality distinguish order; deterministic convergence can lose meaning. | NARROWED | P04/P05/P08. | [S003], [S030], [S034], [S037] |
| Eventual consistency used without convergence or anomaly contract | CONSISTENCY_MODEL | Eventual convergence and session/causal guarantees have distinct conditions; no semantic validity follows. | REFINED | P06–P09. | [S028], [S029], [S030], [S031] |
| Replication assumed to imply durability/fault tolerance | FAILURE_MODEL | Fault-injection and outages show common-mode, corruption propagation and unusable recovery paths. | REFINED | P03/P09/P38. | [S074], [S075], [S091] |
| Network partitions treated as rare impossibilities | FAILURE_MODEL | Short partitions can trigger long divergent recovery and stale reads. | PRESERVED | P01/P02/P37 explicitly model partition and aftermath. | [S025], [S073] |
| Two-phase commit universally rejected as obsolete | TRANSACTION_OR_COMPENSATION | Blocking/cost are real, but strong atomicity remains valuable for non-compensatable closures and modern systems continue to optimise it. | NARROWED | P23, with P24 alternative where semantics permit. | [S018], [S036], [S041], [S042], [S055] |
| Two-phase/global transactions adopted everywhere | TRANSACTION_OR_COMPENSATION | Coordination avoidance and sagas show valid cheaper forms under explicit conditions. | NARROWED | P15/P16/P23/P24. | [S019], [S038], [S039] |
| Compensation treated as rollback/inverse | TRANSACTION_OR_COMPENSATION | Sagas compensate committed subtransactions; external state and failed compensations remain. | REFINED | P24 semantic compensation/forward recovery. | [S019], [S055] |
| Durable replay treated as external-world correctness | WORKFLOW_ORCHESTRATION | Workflow research and end-to-end arguments leave external effects outside unless enclosed/reconciled. | REFINED | P25/P27/P36. | [S043], [S052], [S054], [S055], [S056] |
| Workflow lease expiry treated as worker death | WORKFLOW_ORCHESTRATION | Delay/pause/partition produce overlapping attempts. | REFINED | P26 generation, idempotency or compensation. | [S035], [S052], [S095] |
| Unbounded queues hide overload | OVERLOAD_CONTROL | Metastable field evidence and postmortems show backlog/retry/recovery feedback. | REJECTED | P29–P33; P48 rejected. | [S062], [S063], [S066], [S073] |
| Retries always improve availability | DELIVERY_OR_IDEMPOTENCY | Retries can duplicate effects and amplify degraded dependencies. | NARROWED | P02/P19/P32. | [S063], [S067], [S068], [S069] |
| Circuit breakers/load shedding are self-justifying | OVERLOAD_CONTROL | They can oscillate, shift overload or lose important work without consequence policy. | REFINED | P31/P34. | [S064], [S066] |
| More workers always increase throughput | OVERLOAD_CONTROL | Shared bottlenecks and contention make concurrency part of overload. | NARROWED | P29–P34 capacity model. | [S063], [S065] |
| Health checks prove service usability | OBSERVABILITY | Local process health can coexist with dependency/control-path failure. | REFINED | P41 capability-specific end-to-end readiness. | [S064], [S075] |
| Complete-looking trace is complete evidence | OBSERVABILITY | Sampling, missing spans and overload can selectively erase edge cases. | REFINED | P42/P43 coverage and provenance. | [S080], [S081], [S082], [S083] |
| Backups/checkpoints equal recoverability | RECOVERY_MODEL | Restore may be absent, incompatible, too slow or externally inconsistent. | REFINED | P35–P38. | [S071], [S073], [S074] |
| Event log replay restores irreversible external effects | RECOVERY_MODEL | External effects are not inside the log unless atomically enclosed. | REFINED | P36 effect reconciliation. | [S043], [S048], [S054] |
| Rolling upgrade means binaries healthy | CLOUD_ARCHITECTURE_TRANSLATION | Mixed versions and semantic schema changes can fail despite process health. | REFINED | P39/P40. | [S077], [S078], [S079] |
| Chaos engineering theatre | OBSERVABILITY | Reviews find heterogeneous evidence and underrepresentation of application-level faults. | NARROWED | P44 hypothesis/recovery/decision-bound challenge. | [S084], [S085], [S086] |
| Microservices automatically isolate failure | CEREMONIAL_DISTRIBUTION | Data integrity, dependency and operational coupling can increase. | REJECTED | P34/P45 and contextual boundaries; P47 rejected. | [S092], [S093] |
| Byzantine terminology for ordinary outages | FAILURE_MODEL | BFT addresses arbitrary participants under threshold/authentication assumptions, not every common-mode crash/configuration issue. | DOMAIN_SPECIFIC | P52. | [S005], [S096] |
| Agentic systems are wholly novel and exempt from distributed-state discipline | CLOUD_ARCHITECTURE_TRANSLATION | Recent work imports saga, durable context and fault injection, but semantic validation remains unsettled. | STILL_CONTESTED | P53 provisional domain translation. | [S097], [S098] |

Criticism is not treated as evidence that the entire field failed. It is used to determine whether a property was preserved, narrowed, generalised, replaced, hybridised, made domain-specific or rejected.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_EVOLUTION_UNDER_CRITICISM

| Earlier form | Later/evolved form | Disposition | Properties | Residual caution |
| --- | --- | --- | --- | --- |
| Wall-clock order | Causal/logical order or bounded-uncertainty time where needed | REFINED | P04,P05 | Physical time remains useful when uncertainty and failure response are explicit. |
| Lease/lock ownership | Epoch/fencing-bound resource authority | SUPERSEDED_BY_STRONGER_FORM | P13,P50 | A lease may still improve efficiency; it is not sole stale-writer defence. |
| Blind retry | Semantic identity/idempotency plus budgets, backoff, jitter and deadline | REFINED | P02,P18,P19,P32 | Retries remain selective availability mechanisms. |
| Replica count | Failure-domain and corruption-aware redundancy | REFINED | P03,P09,P38 | Replication survives, but its claim is fault-specific. |
| Eventual consistency slogan | Explicit convergence, session, causal and semantic contracts | REFINED | P06,P07,P08,P09 | Weaker consistency remains valuable where consumer permits. |
| Static majority | Configuration-indexed quorum and safe reconfiguration | REFINED | P10,P12 | Quorum arithmetic survives with identity/configuration. |
| Leader election | Current, state-validated and fenced authority | GENERALIZED | P13,P37 | Election is one step in authority transfer. |
| One global transaction | Scoped atomic commit plus saga/compensation or coordination avoidance | HYBRIDISED | P15,P16,P23,P24 | No blanket winner; invariant and effect closure decide. |
| Request/response workflow | Durable workflow history/state machine | GENERALIZED | P25 | External effects remain separate. |
| Worker DONE | Consumer-relevant verified postcondition | REFINED | P21,P27 | Unknown/partial terminal states are retained. |
| Visibility timeout | Attempt generation plus fencing/idempotency/compensation | REFINED | P26 | Timeout remains scheduling evidence, not death proof. |
| Unbounded queue | Bounded deferred work, backpressure and load shedding | REJECTED | P29,P30,P31,P48 | Queue still useful for durability and bounded bursts. |
| Uncoordinated retries | End-to-end retry budget and jitter | REFINED | P32 | Retries remain if transient, timely and safe. |
| Component failure view | Metastable positive-feedback system view | GENERALIZED | P33 | Removing trigger may not restore service. |
| Backup exists | Tested restore, authority and external reconciliation | REFINED | P35,P36,P37,P38 | Backup remains one artefact in the path. |
| Monolithic health | Capability-specific dependency-aware readiness | REFINED | P41 | Local liveness remains a lower-level signal. |
| Complete trace assumption | Coverage-, freshness- and missingness-aware evidence | REFINED | P42,P43 | Sampling remains necessary but bounded. |
| Random chaos | Hypothesis-, invariant-, load-, recovery- and decision-bound fault injection | REFINED | P44 | Fault injection remains context-dependent. |
| Rolling deployment | Mixed-version protocol/schema/configuration transition | GENERALIZED | P39,P40 | Deployment completion is population/version evidence. |
| Microservices as default | Boundary justified by concrete failure/scale/ownership consumer | NARROWED | P34,P45,P47 | Microservices remain valid in selected contexts. |
| Byzantine as severe failure synonym | Explicit adversarial threshold/identity model | NARROWED | P52 | BFT remains a distinct domain property. |
| Agent novelty | Durable workflow/effect disciplines plus unresolved semantic validation | DOMAIN_SPECIFIC | P53 | Evidence remains early. |

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_INTERNAL_TENSIONS

| Tension | Side A property | Side B property | Context favouring A | Context favouring B | Known hybrid | Unresolved risk |
| --- | --- | --- | --- | --- | --- | --- |
| Consistency versus availability/latency | P07/P15 strong consistency/coordination | P06/P16 available causal/session/mergeable operation | Non-compensatable, non-confluent invariant; consequence of anomaly exceeds outage/latency cost. | Partitioned/geo/offline operation with commutative or invariant-confluent updates and explicit staleness tolerance. | Operation-scoped strong paths alongside causal/CRDT paths; escrow/reservation; bounded staleness. | Hidden cross-object invariant or unexpected dependency can invalidate the weak path. |
| Coordination versus scalability | P10/P11/P15 | P14/P16 | Shared exclusive decision or globally scarce resource. | Partitionable ownership or mergeable state. | Shard ownership plus consensus only for ownership changes. | Resharding and cross-shard operations recreate global coordination. |
| Strong ordering versus throughput | P04/P11/P23 | P04/P16/P17 | Order itself is the protected invariant or required for deterministic transaction execution. | Concurrent operations commute or consumers require only causal/partition order. | Per-key/partition order plus explicit cross-key coordination. | Consumers silently infer a global order from partitioned logs. |
| Retries versus overload and duplication | P02/P17/P19 | P29/P31/P32/P33 | Transient failure, safe duplicate semantics, spare capacity and remaining deadline. | Dependency overloaded, operation non-idempotent or deadline expired. | Budgeted, jittered retries admitted by capacity and operation identity. | Independent stack layers exceed the global budget. |
| Timeout sensitivity versus false failure | P02/P26/P37 fast detection | P05/P13 conservative authority | High cost of waiting and effects safely fenced/idempotent. | High cost of stale dual execution and weak fencing. | Adaptive suspicion for scheduling plus hard resource-side generations for safety. | Overload lengthens latency, causing more false failover. |
| Local autonomy versus global invariant | P16 | P15 | Invariant-confluent operations or escrowed resource shares. | Uniqueness, conservation, referential or exclusive-authority invariant. | Local reservations/escrow with coordinated rebalancing. | Business rule changes can invalidate confluence. |
| Durability versus latency | P23/P25/P35 | P25/P28 with S056-style speculative durability mechanisms | High consequence of lost state/work and strict recovery point. | Latency-sensitive operation with recoverable or reconstructable state. | Batching, replicated logs, snapshots, reactive/speculative persistence under an explicit model. | Optimisation weakens the durability boundary or complicates repair. |
| Replication versus common-mode complexity | P03/P09 | P14/P45 | Availability/durability consequence justifies independent replicas. | Low consequence, easy restore, or replicas share too many common modes. | One primary plus independently tested backups/read replicas; diversify only required domains. | Repair/control software remains common across diverse placement. |
| Quorum size versus availability | P10 stronger intersection/fault margin | P11 liveness under reachable set | Safety/durability dominates and enough independent members are reachable. | Latency/availability dominates and weaker operation-specific semantics are acceptable. | Flexible/read-write quorums or operation-specific consistency with explicit assumptions. | Complex quorum rules become operationally misunderstood. |
| Deterministic replay versus code evolution | P28 deterministic history | P39 rapid schema/protocol evolution | Long-lived workflow must reproduce old decisions. | Rapid iteration and breaking semantic change. | Version markers, compatibility branches, migrations, history pinning or explicit current-state repair. | Version debt and historical code retention grow without bound. |
| Synchronous transaction versus compensation complexity | P23 | P24 | Small participant set, non-compensatable invariant and acceptable blocking/latency. | Long duration, autonomous services or external effects with meaningful compensation. | Local transactions plus outbox and saga; reserve/commit critical resource transactionally. | Intermediate states or compensation semantics remain unsafe. |
| Observability versus overhead/privacy | P42/P43 richer evidence | Sampling/minimisation | Rare high-consequence failures and difficult causal reconstruction. | High traffic, sensitive data and predictable low-risk paths. | Adaptive/triggered/retroactive sampling and privacy-aware provenance. | The rare failure is absent from the sample or collection itself fails. |
| Global coordination versus coordination avoidance | P15 | P16 | Operation set is demonstrably non-confluent. | Confluent/commutative or safely partitioned state. | Hybrid data types/operations with explicit strong path. | Application developers accidentally use weak path for strong operation. |
| Fast failover versus stale-writer risk | P37 rapid recovery | P13 fencing/currentness checks | Spare capacity and strong fencing permit rapid promotion. | External sinks cannot fence or most-current state is uncertain. | Fast traffic shift for read-only/degraded mode, delayed write authority until fencing/validation. | Clients bypass routing and reach stale owner. |
| Queue buffering versus overload concealment | P29 bounded burst absorption | P30/P31 immediate backpressure/shedding | Short burst within known drain capacity and deadlines. | Persistent overload or time-sensitive work. | Small bounded queue with age limits and upstream admission. | Burst model ages as workload changes. |
| Load shedding versus fairness/critical-work preservation | P31 throughput/stability | Priority/fairness constraints | System survival and critical core service. | Rights/fairness or heterogeneous business consequence. | Per-tenant quotas, ageing, criticality tiers and explicit rejected-work handling. | Priority policy encodes hidden inequity or can be gamed. |
| Generic middleware versus application semantic knowledge | P17/P25 generic runtime | P08/P19/P24/P27 domain semantics | Common transport, scheduling and durability concerns. | Conflict, idempotency, compensation and completion depend on business meaning. | Runtime supplies identities/history/hooks; application supplies invariant/effect/compensation validators. | Ownership falls between platform and application teams. |
| Strong failure assumptions versus implementation cost | P52 BFT or wide fault model | P01/P14 minimal model | Credible adversary or catastrophic arbitrary-fault consequence. | Crash/common-mode risks dominate and extra complexity reduces reliability. | Crash consensus plus integrity checks/audits; isolate high-risk boundary. | Threat model changes or supply-chain compromise creates correlated Byzantine behaviour. |
| Microservice isolation versus coordination debt | P34/P47 contextual isolation | P45 local path | Real independent ownership, deployment, scale or fault containment. | Tightly coupled invariant/data and shared operations. | Modular monolith, service consolidation, or coarse services with local transactions. | Organisational incentives prevent recombination. |
| Automatic recovery versus forensic preservation | P36/P37 rapid repair | P42/P43 evidence preservation | High availability and well-understood reversible fault. | Unknown corruption/security/semantic failure where repair may erase evidence. | Snapshot evidence before mutation, immutable audit log, staged read-only recovery. | Evidence capture delays urgent recovery or itself is incomplete. |

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_HYBRIDISATION_PRESSURES

| Pressure | Hybrid resolution | Properties | Residual risk |
| --- | --- | --- | --- |
| Invariant scope | Strong transaction/consensus for non-confluent core + CRDT/causal/async path for remaining state. | P15,P16,P23 | Hidden invariant crossing the boundary. |
| Authority and time | Lease for efficient ownership + resource fencing for stale-writer safety. | P05,P13 | Sink cannot enforce generation. |
| Messaging and state | Local transaction + outbox/inbox + at-least-once delivery + semantic idempotency. | P17,P19,P22 | External effect remains outside closure. |
| Workflow and transactions | Durable orchestration + local atomic steps + saga compensation + selected transactional reservation. | P23,P24,P25 | Compensation is not a valid inverse. |
| Replication and recovery | Synchronous/consensus replication for recent availability + independent immutable backup + tested restore. | P03,P09,P35,P38 | Shared corruption/configuration reaches every copy. |
| Overload and reliability | Retries/failover only behind admission, backpressure, budgets and recovery-capacity reservation. | P32,P33,P37 | Local policies interact into global positive feedback. |
| Observability and authority | Traces/metrics for diagnosis + direct authoritative state query for currentness/completion. | P06,P21,P42,P43 | Authoritative query itself is stale or unavailable. |
| Schema and replay | Backward-compatible staged rollout + versioned workflow/event history + migration or pinning. | P28,P39,P40 | Semantic compatibility differs from wire compatibility. |
| Microservice and locality | Independent service where lifecycle/failure consumer exists + local transaction/modular monolith within invariant boundary. | P14,P45,P47 | Service ownership conflicts with data/invariant ownership. |
| Fault injection and formal model | Proof/model checking of protocol safety + targeted distributed fault/recovery experiments of implementation/integration. | P01,P11,P44 | Tests do not cover model or formal proof omits real primitive. |
| Geo distribution | Per-region local ownership/transactions + explicit cross-region coordination only for shared invariant + asynchronous read replicas. | P06,P15,P16,P23 | Failover and resharding blur ownership. |
| Agentic translation | Durable workflow/effect identity/fencing + semantic validator/human escalation. | P25,P27,P53 | Validator shares model failure or no stable oracle. |

The dominant current pattern is not one mechanism replacing all others. It is selective combination: strong coordination for the non-confluent core, autonomous/mergeable paths elsewhere; durable workflow state around local transactions; leases for efficiency backed by fencing; asynchronous delivery backed by identity/idempotency; and recovery backed by tested external reconciliation.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_STRONGEST_SURVIVING_PROPERTIES

| ID | Property | Why it survives | Evidence |
| --- | --- | --- | --- |
| P01 | Explicit distributed failure, timing, network, storage and recovery model | An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path. | [S005], [S006], [S007], [S008], [S034], [S071], [S088], [S091], [S073], [S074], [S075], [S076] |
| P02 | Partial failure and unknown-outcome semantics | Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it. | [S008], [S043], [S044], [S061], [S067], [S073] |
| P04 | Causal order distinguished from wall-clock and arbitrary total order | Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately. | [S003], [S013], [S031], [S032], [S033], [S047], [S073] |
| P06 | Currentness, freshness and session guarantees as explicit evidence | A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown. | [S021], [S029], [S031], [S036], [S037], [S073] |
| P07 | Consistency level and isolation as an operation-scoped contract | Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised. | [S020], [S021], [S022], [S023], [S024], [S025], [S027], [S029], [S031], [S039], [S073] |
| P10 | Quorum validity bound to current membership and configuration | A quorum certificate identifies current configuration, epoch and state position. | [S011], [S012], [S014], [S015], [S036], [S094], [S073] |
| P11 | Consensus safety separated from liveness and semantic validity | Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately. | [S006], [S007], [S008], [S009], [S010], [S011], [S012], [S073] |
| P13 | Current mutation authority enforced by epochs or fencing | Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised. | [S010], [S012], [S035], [S070], [S094], [S073] |
| P15 | Strong coordination for non-confluent invariants | Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation. | [S017], [S020], [S023], [S025], [S036], [S038], [S040], [S041], [S042], [S073] |
| P17 | Duplicate-aware delivery semantics | Name semantics at every boundary and independently close the business-effect boundary. | [S043], [S044], [S045], [S046], [S047], [S049], [S073] |
| P19 | Semantic idempotency, not request-ID ritual | The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay. | [S044], [S050], [S058], [S067], [S069], [S073] |
| P27 | Completion defined by durable state plus verified postcondition | DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN. | [S043], [S050], [S054], [S055], [S092], [S073] |
| P32 | Retry budgets, exponential backoff, jitter and deadline propagation | A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity. | [S061], [S063], [S066], [S067], [S068], [S069], [S073], [S076] |
| P36 | Replay and restore with external-state reconciliation | Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible. | [S017], [S046], [S048], [S050], [S053], [S056], [S071], [S073], [S074] |
| P44 | Hypothesis-bound fault injection and recovery challenge | A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action. | [S084], [S085], [S086], [S087], [S088], [S089], [S090], [S091], [S073] |

These properties survive tool substitution and architecture fashion. They either follow from deep formal limits/definitions or recur across independent systems and failure evidence. Their mature forms are still assumption-sensitive.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_CONTEXT_SPECIFIC_PROPERTIES

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P05 | Bounded-clock use and time-based authority with uncertainty margin | ASSUMPTION_SENSITIVE | Leases, TTLs, freshness SLAs, event-time windows or external-consistency designs. | Logical/causal clocks, non-time-based generations, or local timeout used only as a heuristic. | Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters. |
| P08 | Semantic conflict resolution beyond replica byte convergence | REPLICATION_CONSISTENCY_PROPERTY | Offline, geo or multi-writer state where concurrent progress is valuable. | One current writer, local transaction or coordination when the invariant is non-confluent. | Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination. |
| P09 | Anti-entropy, convergence and repair with corruption/lag safeguards | REPLICATION_CONSISTENCY_PROPERTY | Eventually or asynchronously replicated state with a lag/disconnected-replica path. | Synchronous replicated object with no lag path, or immutable artefact verified at write time. | Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation. |
| P14 | Single-writer or local-transaction cheap path | STRONGLY_RETAINED | Low write scale, central invariant, tightly coupled data, modest availability demand or easy recovery. | This property is the cheap path; distribution triggers only after a concrete consumer appears. | Start local or single-writer; distribute only the dimension with demonstrated need. |
| P16 | Coordination avoidance for invariant-confluent, commutative or partitionable operations | CONTEXT_DEPENDENT | High-latency or partitioned environment where operation semantics support safe independent execution. | Non-confluent uniqueness/conservation/exclusive authority or irreversible global effects should coordinate instead. | Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones. |
| P22 | Transactional messaging or outbox/inbox closure | DELIVERY_IDEMPOTENCY_PROPERTY | A local transaction must reliably cause or record an asynchronous message, or a consumed event must update state exactly once within the closure. | Direct local state change with no asynchronous notification requirement. | The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit. |
| P23 | Explicit transactional boundary and atomic-commit choice | TRANSACTION_COMPENSATION_PROPERTY | A non-compensatable invariant requires all-or-nothing across multiple transactional participants. | One local transaction; or independently commit compensatable steps with a durable saga. | Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation. |
| P24 | Compensation and forward recovery with semantic limits | TRANSACTION_COMPENSATION_PROPERTY | Long-running, cross-service or external workflow whose effects are compensatable or repairable but not globally atomic. | One atomic local/distributed transaction when the whole closure can and should commit together. | Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated. |
| P28 | Deterministic replay with explicit workflow/code version evolution | ASSUMPTION_SENSITIVE | Replay-based durable workflow, event sourcing or state reconstruction across code versions. | Persist explicit current state without replay, or finish short-lived work before incompatible deployment. | History, code and schema versions are explicit; every deployed version can replay or migrate all live histories. |
| P34 | Dependency isolation and bulkheads with end-to-end verification | CONTEXT_DEPENDENT | Shared resource pool or dependency whose slowness/failure can block unrelated work. | One small dependency path with no shared-resource contention or acceptable full-stop behaviour. | Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour. |
| P39 | Schema, wire protocol and event evolution under mixed versions | RETAINED_IN_EVOLVED_FORM | Rolling deployment, long-lived event/log data, external clients, multiple regions or replayable workflow history. | Atomic offline upgrade of one local process/store with no concurrent old reader/writer and acceptable downtime. | Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier. |
| P40 | Configuration and control-plane/data-plane currentness | RETAINED_IN_EVOLVED_FORM | Configuration affects routing, membership, schemas, resource limits, feature behaviour or authority across components. | Local static configuration changed atomically with the single process. | Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid. |
| P42 | Distributed observability treated as partial, sampled evidence | USEFUL_BUT_EASILY_GAMED | Diagnosis, currentness, completion, failure-model validation or causal reconstruction depends on distributed telemetry. | Local deterministic operation with direct authoritative state inspection. | Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available. |
| P44 | Hypothesis-bound fault injection and recovery challenge | USEFUL_BUT_EASILY_BUREAUCRATISED | Material claim about tolerance, failover, retry, restore, overload or state integrity whose assumptions can be safely challenged. | Static analysis/model checking/unit/integration test when the claim does not require distributed runtime failure; low-consequence system with no material uncertainty. | A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action. |
| P46 | Retire distributed machinery when its coordination consumer disappears | RETAINED_IN_EVOLVED_FORM | Mechanism has no current decision, invariant, workload or failure-domain consumer. | Keep mechanism only when removal would reintroduce a demonstrated failure or violate a current requirement. | Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics. |
| P52 | Byzantine/adversarial fault tolerance only under an explicit adversarial model | DOMAIN_SPECIFIC | Actual threat model includes mutually distrustful or compromise-prone participants and the cost is justified. | Crash-fault consensus, single authority, audited replication or simpler integrity checks when adversarial participants are not a credible failure. | BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate. |
| P53 | Distributed AI and agentic systems as a bounded domain translation | UNRESOLVED | Autonomous or multi-agent system coordinates persistent work or external effects across independently failing services. | One model call with human review and no durable/external effect; deterministic local program where suitable. | Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property. |

Context dependence is not weakness. It means the property has a real trigger and a real non-trigger. The audit burden is to prove the trigger, not to adopt every retained mechanism.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_REJECTED_OR_SUPERSEDED_PRACTICES

| ID | Property | Status | Trigger | Cheap path | Mature form |
| --- | --- | --- | --- | --- | --- |
| P47 | Microservices automatically improve resilience | REJECTED_OR_DISFAVOURED | Retain a service boundary only when it creates a real independently operable/failing/owned capability. | Modular monolith, local module or co-located state when independent runtime failure is unnecessary. | A service boundary is justified by a named lifecycle, ownership, scale or failure-containment property and bears its distributed obligations. |
| P48 | A queue absorbs overload | REJECTED_OR_DISFAVOURED | A queue is justified for decoupling, durability or burst smoothing only with a capacity/consequence model. | Synchronous backpressured call or small bounded local buffer. | Queue value is stated—durability, decoupling or bounded burst absorption—and completion capacity remains explicit. |
| P49 | Exactly-once delivery implies the business action occurs exactly once | REJECTED_OR_DISFAVOURED | Retain platform exactly-once semantics only for operations inside its documented transaction boundary. | At-least-once plus semantic idempotency, or one local transaction, when simpler and sufficient. | Say exactly once only with the noun and boundary: record processing, state transition or verified effect under stated assumptions. |
| P50 | Distributed lock alone makes concurrent mutation safe | SUPERSEDED_BY_STRONGER_FORM | A lock may still coordinate efficiency or reduce contention, but correctness-critical mutation requires stale rejection. | Local mutex/local transaction, one durable writer, commutative operation or resource-native compare-and-swap. | Lock is advisory evidence; the mutation is safe because stale generations cannot take effect. |
| P51 | Named infrastructure or repeated ritual as an engineering property | CEREMONY_NOT_GENERAL_PROPERTY | Only when the artefact implements a named property whose payoff exceeds its own lifecycle cost. | Local code/state, existing transactional store, simpler ownership or targeted test. | Infrastructure is replaceable; the property, assumptions and evidence survive substitution. |
| P54 | Default global consensus or coordination for all distributed state | REJECTED_OR_DISFAVOURED | Strong coordination triggers only for an explicit invariant/current authority that cannot be preserved by local ownership, partitioning, commutativity, escrow or compensation. | Local transaction, single writer, CRDT/invariant-confluent operation, partitioned ownership or asynchronous durable handoff. | Coordinate only the state/effect closure whose independent execution would violate the named invariant. |

- **P47:** service decomposition is not automatic resilience.
- **P48:** queue presence is not capacity.
- **P49:** exactly-once processing is not automatically one external business effect.
- **P50:** a distributed lock without stale-resource rejection is superseded for correctness-critical mutation.
- **P51:** named tools and recurring rituals are not general properties.
- **P54:** global consensus/coordination is not the default merely because the system is distributed.

Each rejected proposition preserves a narrower valid mechanism elsewhere in the ledger.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_CURRENT_STATE_AND_RESEARCH_FRONTIER

### Current state as of 2026-08-12

1. **Consensus and transactions:** the frontier largely refines latency, reconfiguration and geo-commit while retaining classic safety/membership/atomicity assumptions. D2PC and Chablis are examples of optimisation within—not abolition of—the transaction model. [S041], [S042]
2. **Consistency and coordination avoidance:** algebraic convergence and invariant-confluence remain active, increasingly hybridised with selected stronger operations. [S030], [S038], [S039], [S100]
3. **Durable workflows:** current work explicitly recognises that durable execution and exactly-once-DAG claims do not by themselves define end-to-end correctness; workflow-level transaction, compensation, version and external-effect semantics remain open design space. [S054]–[S056]
4. **Overload:** research has moved from isolated local limits toward metastable feedback and coordinated admission across dependency graphs. [S062], [S063], [S065]
5. **Recovery:** recent fault-injection work targets persistence-order/data-loss failures and external-fault schedule reproduction, reinforcing the gap between nominal durability and exercised recovery. [S088], [S089], [S091]
6. **Observability:** rare-path and retroactive tracing improve evidence collection while confirming that sampling and overload create systematic missingness. [S083]
7. **Cross-service semantic integrity:** systems such as Aletheia target invariants that no individual microservice/database can see, evidence that service decomposition moves—not removes—coordination burdens. [S092]
8. **Configuration and multi-region failure:** 2025 outage evidence shows global configuration/data propagation and restoration demand remain high-impact common modes. [S076]
9. **Chaos/fault injection evidence:** systematic and repository-scale reviews find broader adoption but heterogeneous methods, underrepresented application-level faults and limited independent effectiveness evidence. [S085], [S086]
10. **Distributed AI/agents:** recent work imports sagas, durable context, validation and fault injection, but the semantic-validity oracle and field evidence are immature; P53 remains `UNRESOLVED`. [S097], [S098]

### Frontier claims not made

The report does not claim that the newest protocol is the mature answer, that a benchmark transfers to every workload, that one cloud provider's semantics are universal, that fault-injection adoption proves resilience, or that agentic systems create a wholly new distributed-systems foundation.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_OPEN_QUESTIONS

1. How can deployed systems continuously attest that storage, clock, membership and failure-domain assumptions still match a protocol proof?
2. How can semantic operation identity and idempotency evidence span third parties and physical effects that do not accept caller tokens?
3. How should finite dedup/tombstone retention be chosen when disaster restore or disconnected replicas can be arbitrarily old?
4. What practical methods translate business invariants into checkable confluence/consistency obligations and keep them valid through schema evolution?
5. How can safe automatic failover minimise downtime when external sinks cannot fence stale actors?
6. How should compensation semantics be validated and versioned as business rules and external state change?
7. How can workflow histories be compacted while preserving deterministic replay, provenance and unresolved effects?
8. How can systems detect metastable precursors and feedback loops without unstable control or excessive false alarms?
9. How should admission control balance fairness, criticality and business consequence under prolonged scarcity?
10. How can restore/fault-injection evidence cover rare correlated/control-plane faults without unacceptable cost or blast radius?
11. How can distributed observability communicate causal uncertainty and missingness in machine-actionable form?
12. Which comparative empirical designs can separate architecture shape—microservices, serverless, multi-region—from organisational maturity and workload?
13. How should common software/supply-chain compromise be modelled when it correlates more replicas than classic BFT thresholds assume?
14. Do agentic systems add a genuinely new general property beyond durable workflow, semantic validation and effect governance, or only a domain-specific failure/value model? `UNRESOLVED`.
15. How can a system preserve forensic evidence while automated repair, rollback and reconciliation mutate the failing state?

Unresolved questions do not reopen the frozen denominator. They are explicit evidence limits for later research or audit.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_AUDIT_INTAKE

**Frozen run date:** 2026-08-12  
**Analytical label:** `EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING`  
**Independence boundary:** external distributed-systems research only; no repository or sibling Evolved-* packet was inspected.

## Population receipt

- `PROPERTY_POPULATION_TOTAL`: **54**
- `PROPERTY_POPULATION_EXAMINED`: **54**
- `PROPERTY_COVERAGE`: **54/54**
- `SOURCE_POPULATION_SUMMARY`: **102 source records** spanning foundational papers, formal results, peer-reviewed systems/empirical work, standards/guidance, implementation documentation used only for behaviour, and incident postmortems.
- `EVIDENCE_STRENGTH_PARTITIONS`: formal strength is highest for causality, consensus, consistency and convergence definitions; operational transfer is most assumption-sensitive at membership, storage, clock, external-effect and common-mode boundaries; outage/field strength is highest for partial failure, recovery, overload, configuration and observability limits.
- `TOP_CROSSWALK_PROPERTIES`: all **48** entries below are crosswalk-worthy. Rejected/ceremonial candidates remain in the frozen denominator but are not converted into adoption candidates.

This intake is deliberately interrogative. It does not answer questions about any target system.

## TOP_CROSSWALK_PROPERTIES

### P01 — Explicit distributed failure, timing, network, storage and recovery model
- **DISTRIBUTED_FAILURE_MODE:** Crash, omission, delay, partition, corruption, clock and recovery faults are conflated; a proved algorithm is deployed outside its model.
- **MATURE_FORM:** An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **TRIGGER:** Any correctness or completion claim spanning independently failing processes, stores, networks or administrative components.
- **CHEAP_PATH:** A local call, local transaction or one durable process when no independent remote failure boundary is required.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable.; TIMING_MODEL=The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout.; NETWORK_ASSUMPTIONS=Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable.; STORAGE_ASSUMPTIONS=Restart, stable-storage, rollback and rejoin semantics are declared.; RECOVERY_ASSUMPTIONS=Restart, stable-storage, rollback and rejoin semantics are declared.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Evidence distinguishes suspicion from established failure and reports coverage gaps.; CHEAP_PATH=A local call, local transaction or one durable process when no independent remote failure boundary is required.; MATURE_FORM=An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout.; MEMBERSHIP_LINK=Membership, configuration and ownership identity are explicit wherever they affect the claim.; MATURE_FORM=An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=No consistency claim is accepted without a named history/observation model and operation boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Loss, duplication, reordering and retry are either in scope or explicitly excluded.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Membership, configuration and ownership identity are explicit wherever they affect the claim.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Restart, stable-storage, rollback and rejoin semantics are declared.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path.
- **REQUIRED_PRECONDITIONS:** Known component boundary; declared synchrony; stable-storage semantics; restart behaviour; membership; clock assumptions; common-mode inventory. | No consistency claim is accepted without a named history/observation model and operation boundary. | Membership, configuration and ownership identity are explicit wherever they affect the claim. | Loss, duplication, reordering and retry are either in scope or explicitly excluded. | Restart, stable-storage, rollback and rejoin semantics are declared. | Evidence distinguishes suspicion from established failure and reports coverage gaps.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Models can be unrealistically clean; Enumerating assumptions is not proof they hold; Byzantine language can distract from ordinary crash/common-mode failures
- **ANTI_CEREMONY_BOUNDARY:** Using a protocol or topology label is ceremony; the retained property is the checked model.
- **POSSIBLE_CONFLICTING_PROPERTY:** P45: a full distributed model should not trigger where the operation is local.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact crash, restart, storage, timing, network and common-mode failures are in scope?
  - Which claims fail if a timeout is a false suspicion or storage returns corrupted—not merely absent—data?

### P02 — Partial failure and unknown-outcome semantics
- **DISTRIBUTED_FAILURE_MODE:** The caller times out after the remote effect may already have committed or may still be executing.
- **MATURE_FORM:** Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **TRIGGER:** Remote mutation, distributed commit, task dispatch or external side effect whose response can be lost.
- **CHEAP_PATH:** Local atomic mutation with a definitive return, or a harmless repeatable read.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable.; TIMING_MODEL=The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout.; NETWORK_ASSUMPTIONS=Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable.; STORAGE_ASSUMPTIONS=Restart, stable-storage, rollback and rejoin semantics are declared.; RECOVERY_ASSUMPTIONS=Restart, stable-storage, rollback and rejoin semantics are declared.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Evidence distinguishes suspicion from established failure and reports coverage gaps.; CHEAP_PATH=Local atomic mutation with a definitive return, or a harmless repeatable read.; MATURE_FORM=Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout.; MEMBERSHIP_LINK=Membership, configuration and ownership identity are explicit wherever they affect the claim.; MATURE_FORM=Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=No consistency claim is accepted without a named history/observation model and operation boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Loss, duplication, reordering and retry are either in scope or explicitly excluded.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Membership, configuration and ownership identity are explicit wherever they affect the claim.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Restart, stable-storage, rollback and rejoin semantics are declared.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it.
- **REQUIRED_PRECONDITIONS:** Stable operation identity, authoritative status/reconciliation interface, durable outcome state and duplicate-safe or compensatable effect. | No consistency claim is accepted without a named history/observation model and operation boundary. | Membership, configuration and ownership identity are explicit wherever they affect the claim. | Loss, duplication, reordering and retry are either in scope or explicitly excluded. | Restart, stable-storage, rollback and rejoin semantics are declared. | Evidence distinguishes suspicion from established failure and reports coverage gaps.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Unknown-state handling adds latency and durable state; Some external effects cannot be queried or reversed; Aggressive timeouts can create the uncertainty they detect
- **ANTI_CEREMONY_BOUNDARY:** Turning timeout into an error code is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P32/P37: fast retry/failover pressure conflicts with preserving UNKNOWN and stale-actor safety.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - When a timeout expires, can the target still commit or act?
  - Where is UNKNOWN represented, and what authoritative observation resolves it?
  - Can cancellation prevent the old actor from acting?

### P03 — Failure-domain independence and common-mode awareness
- **DISTRIBUTED_FAILURE_MODE:** A common cause removes or corrupts nominally redundant copies and the recovery/control path.
- **MATURE_FORM:** Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **TRIGGER:** Replication, quorum, backup, multi-zone/region, control-plane or failover claim.
- **CHEAP_PATH:** One durable copy plus tested backup where hot availability is unnecessary and consequence permits it.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable.; TIMING_MODEL=The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout.; NETWORK_ASSUMPTIONS=Crash-stop, crash-recovery, omission, delay, partition, storage corruption, clock error and correlated/common-mode failure as applicable.; STORAGE_ASSUMPTIONS=Restart, stable-storage, rollback and rejoin semantics are declared.; RECOVERY_ASSUMPTIONS=Restart, stable-storage, rollback and rejoin semantics are declared.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Evidence distinguishes suspicion from established failure and reports coverage gaps.; CHEAP_PATH=One durable copy plus tested backup where hot availability is unnecessary and consequence permits it.; MATURE_FORM=Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=The claim states whether it is asynchronous, partially synchronous, synchronous, or merely bounded by a local policy timeout.; MEMBERSHIP_LINK=Membership, configuration and ownership identity are explicit wherever they affect the claim.; MATURE_FORM=Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=No consistency claim is accepted without a named history/observation model and operation boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Loss, duplication, reordering and retry are either in scope or explicitly excluded.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Membership, configuration and ownership identity are explicit wherever they affect the claim.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Restart, stable-storage, rollback and rejoin semantics are declared.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Claim tolerance only for explicit independent domains; include data, authority, observability and recovery paths.
- **REQUIRED_PRECONDITIONS:** Failure-domain inventory, placement evidence, recovery-path independence, integrity checks and out-of-band access. | No consistency claim is accepted without a named history/observation model and operation boundary. | Membership, configuration and ownership identity are explicit wherever they affect the claim. | Loss, duplication, reordering and retry are either in scope or explicitly excluded. | Restart, stable-storage, rollback and rejoin semantics are declared. | Evidence distinguishes suspicion from established failure and reports coverage gaps.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Perfect independence is impossible; Cross-region independence costs latency and complexity; Provider labels are not empirical proof
- **ANTI_CEREMONY_BOUNDARY:** Three replicas or three zones is ceremony without a shared-fate model.
- **POSSIBLE_CONFLICTING_PROPERTY:** P14/P45: independence cost may exceed consequence where a simple restore path suffices.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which replicas share software, configuration, network, storage, credentials, DNS, control plane or operator?
  - Can anti-entropy, repair or global configuration spread one bad state everywhere?

### P04 — Causal order distinguished from wall-clock and arbitrary total order
- **DISTRIBUTED_FAILURE_MODE:** Events are delayed, reordered and concurrent across independently progressing processes.
- **MATURE_FORM:** Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **TRIGGER:** Correctness depends on whether one event could have influenced another, read-your-writes or dependency application.
- **CHEAP_PATH:** Single-thread/local transaction order, or independent commutative operations with no causal consumer.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation.; TIMING_MODEL=No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design.; NETWORK_ASSUMPTIONS=Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation.; STORAGE_ASSUMPTIONS=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; RECOVERY_ASSUMPTIONS=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.; CHEAP_PATH=Single-thread/local transaction order, or independent commutative operations with no causal consumer.; MATURE_FORM=Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=PRIMARY; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design.; MEMBERSHIP_LINK=Sequencers, leases and readers identify the current term/configuration where that affects currentness.; MATURE_FORM=Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Sequencers, leases and readers identify the current term/configuration where that affects currentness.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately.
- **REQUIRED_PRECONDITIONS:** Stable event identity, propagation of dependency metadata, stated sequencer/log semantics and retention of causal context. | Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation. | Sequencers, leases and readers identify the current term/configuration where that affects currentness. | Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order. | Replay and failover preserve required dependencies and do not present older state as newer without signalling. | Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Causal metadata can grow; Causality does not supply semantic conflict resolution; Some invariants genuinely require total order
- **ANTI_CEREMONY_BOUNDARY:** Adding a timestamp or correlation ID is not causal engineering.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P15: partial/causal order conflicts with invariants that require one total decision order.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Where does the system rely on wall-clock or log order, and does that order preserve the needed causal relation?
  - Can concurrent events remain concurrent, or are they silently collapsed by last-write-wins?

### P05 — Bounded-clock use and time-based authority with uncertainty margin
- **DISTRIBUTED_FAILURE_MODE:** Different nodes observe incompatible time and liveness while delayed actors remain able to execute.
- **MATURE_FORM:** Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **TRIGGER:** Leases, TTLs, freshness SLAs, event-time windows or external-consistency designs.
- **CHEAP_PATH:** Logical/causal clocks, non-time-based generations, or local timeout used only as a heuristic.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation.; TIMING_MODEL=No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design.; NETWORK_ASSUMPTIONS=Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation.; STORAGE_ASSUMPTIONS=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; RECOVERY_ASSUMPTIONS=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.; CHEAP_PATH=Logical/causal clocks, non-time-based generations, or local timeout used only as a heuristic.; MATURE_FORM=Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=PRIMARY; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design.; MEMBERSHIP_LINK=Sequencers, leases and readers identify the current term/configuration where that affects currentness.; MATURE_FORM=Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Sequencers, leases and readers identify the current term/configuration where that affects currentness.; GENERATION_OR_EPOCH=Monotone term/view/fencing token accompanies time-bound authority.; STALE_REJECTION=The protected resource rejects lower generations; expiry is not the sole defence.; MATURE_FORM=Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Physical time contributes evidence only inside its bound; stale mutation is rejected by generation where correctness matters.
- **REQUIRED_PRECONDITIONS:** Measured bound, uncertainty excursion policy, pause/restart handling, lease issuer identity and fenced effect boundary. | Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation. | Sequencers, leases and readers identify the current term/configuration where that affects currentness. | Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order. | Replay and failover preserve required dependencies and do not present older state as newer without signalling. | Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Conservative margins reduce availability; Clock infrastructure is common-mode; Bounded time does not create semantic causality
- **ANTI_CEREMONY_BOUNDARY:** A timestamp or lease API without uncertainty and stale-writer rejection is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P13: efficiency from time-based leases conflicts with the need for non-time-based stale rejection.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What clock error, pause and restart assumptions support every lease, TTL or freshness claim?
  - Does the protected resource reject stale generations, or does safety depend on the old holder's clock?

### P06 — Currentness, freshness and session guarantees as explicit evidence
- **DISTRIBUTED_FAILURE_MODE:** Replica lag, failover and partition let a reachable component serve stale or divergent state.
- **MATURE_FORM:** A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **TRIGGER:** Read result drives mutation, completion, failover, user-visible monotonicity or safety-sensitive decision.
- **CHEAP_PATH:** Immutable content, best-effort analytics or explicitly stale cache with no authority claim.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation.; TIMING_MODEL=No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design.; NETWORK_ASSUMPTIONS=Delay, reordering, concurrency, partition, clock skew/jumps, replica lag and incomplete propagation.; STORAGE_ASSUMPTIONS=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; RECOVERY_ASSUMPTIONS=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.; CHEAP_PATH=Immutable content, best-effort analytics or explicitly stale cache with no authority claim.; MATURE_FORM=A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=PRIMARY; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=No exact global clock is assumed unless a measured uncertainty bound and failure response are part of the design.; MEMBERSHIP_LINK=Sequencers, leases and readers identify the current term/configuration where that affects currentness.; MATURE_FORM=A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Sequencers, leases and readers identify the current term/configuration where that affects currentness.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay and failover preserve required dependencies and do not present older state as newer without signalling.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown.
- **REQUIRED_PRECONDITIONS:** Version/commit index or causal token, replica lag and membership knowledge, retention and consumer-defined tolerance. | Causal, session, linearizable, snapshot or bounded-staleness semantics are named per operation. | Sequencers, leases and readers identify the current term/configuration where that affects currentness. | Event identity and dependency metadata survive retry/replay; transport order is not promoted to causal order. | Replay and failover preserve required dependencies and do not present older state as newer without signalling. | Clock uncertainty, lag, missing dependencies and sampled evidence remain visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Stronger currentness costs latency/availability; Freshness telemetry is delayed; Many reads do not need the strongest model
- **ANTI_CEREMONY_BOUNDARY:** A green replica or recent timestamp is not currentness evidence by itself.
- **POSSIBLE_CONFLICTING_PROPERTY:** P07/P15: stronger currentness can conflict with availability and latency.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What proves a read is current enough for the decision consuming it?
  - Are read-your-writes and monotonic guarantees preserved across failover and service boundaries?

### P07 — Consistency level and isolation as an operation-scoped contract
- **DISTRIBUTED_FAILURE_MODE:** Concurrent operations and replicas produce histories whose anomalies are hidden by vague labels.
- **MATURE_FORM:** Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **TRIGGER:** Shared mutable state with concurrent actors or replicas.
- **CHEAP_PATH:** Single-thread/local immutable data, or commutative/invariant-confluent operations tolerating declared anomalies.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; TIMING_MODEL=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; NETWORK_ASSUMPTIONS=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; STORAGE_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; RECOVERY_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Lag, divergence, repair source, membership and invariant checks are observable.; CHEAP_PATH=Single-thread/local immutable data, or commutative/invariant-confluent operations tolerating declared anomalies.; MATURE_FORM=Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; MEMBERSHIP_LINK=Replica set, writer authority and configuration identity are current and durable.; MATURE_FORM=Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=PRIMARY; CONSISTENCY_MODEL=The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Replica set, writer authority and configuration identity are current and durable.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Catch-up, repair, rejoin, compaction and corruption handling are tested.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised.
- **REQUIRED_PRECONDITIONS:** Operation/transaction boundaries, anomaly model, client/session semantics, implementation verification and failure response. | The replica model, permitted anomalies, convergence rule and semantic invariant are explicit. | Replica set, writer authority and configuration identity are current and durable. | Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. | Catch-up, repair, rejoin, compaction and corruption handling are tested. | Lag, divergence, repair source, membership and invariant checks are observable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Formal labels are hard to apply; History checking samples workloads; Stronger consistency can reduce availability without protecting a real invariant
- **ANTI_CEREMONY_BOUNDARY:** Selecting a product tier labelled 'strong' is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P16: explicit strong consistency may be unnecessary for invariant-confluent operations.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which anomalies are prevented, permitted or detectable for each operation?
  - Does the model cover messaging and external effects, or only a database history?

### P08 — Semantic conflict resolution beyond replica byte convergence
- **DISTRIBUTED_FAILURE_MODE:** Concurrent writes, delayed replicas and reordering produce conflicts whose resolution is application-sensitive.
- **MATURE_FORM:** Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **TRIGGER:** Offline, geo or multi-writer state where concurrent progress is valuable.
- **CHEAP_PATH:** One current writer, local transaction or coordination when the invariant is non-confluent.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; TIMING_MODEL=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; NETWORK_ASSUMPTIONS=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; STORAGE_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; RECOVERY_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Lag, divergence, repair source, membership and invariant checks are observable.; CHEAP_PATH=One current writer, local transaction or coordination when the invariant is non-confluent.; MATURE_FORM=Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; MEMBERSHIP_LINK=Replica set, writer authority and configuration identity are current and durable.; MATURE_FORM=Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=PRIMARY; CONSISTENCY_MODEL=The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Application invariants are separately proved or challenged; converged bytes are insufficient.; MATURE_FORM=Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Replica set, writer authority and configuration identity are current and durable.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Catch-up, repair, rejoin, compaction and corruption handling are tested.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Prove or test merge/invariant compatibility; otherwise use ownership, reservation or coordination.
- **REQUIRED_PRECONDITIONS:** Operation algebra, identity/tombstone policy, causal metadata, invariant argument and compaction horizon. | The replica model, permitted anomalies, convergence rule and semantic invariant are explicit. | Replica set, writer authority and configuration identity are current and durable. | Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. | Catch-up, repair, rejoin, compaction and corruption handling are tested. | Lag, divergence, repair source, membership and invariant checks are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** CRDTs do not solve arbitrary invariants; Metadata/tombstones cost storage; Middleware often lacks domain semantics
- **ANTI_CEREMONY_BOUNDARY:** 'Eventually all replicas match' is not the property if the matched state is wrong.
- **POSSIBLE_CONFLICTING_PROPERTY:** P15: semantic merge conflicts with invariants that cannot be preserved without coordination.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does convergence preserve the business invariant, or only identical state?
  - What happens when a delayed replica returns after causal/tombstone metadata is compacted?

### P09 — Anti-entropy, convergence and repair with corruption/lag safeguards
- **DISTRIBUTED_FAILURE_MODE:** Long-disconnected or corrupted replicas rejoin and exchange state under uncertain currentness.
- **MATURE_FORM:** Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **TRIGGER:** Eventually or asynchronously replicated state with a lag/disconnected-replica path.
- **CHEAP_PATH:** Synchronous replicated object with no lag path, or immutable artefact verified at write time.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; TIMING_MODEL=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; NETWORK_ASSUMPTIONS=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; STORAGE_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; RECOVERY_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Lag, divergence, repair source, membership and invariant checks are observable.; CHEAP_PATH=Synchronous replicated object with no lag path, or immutable artefact verified at write time.; MATURE_FORM=Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; MEMBERSHIP_LINK=Replica set, writer authority and configuration identity are current and durable.; MATURE_FORM=Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=PRIMARY; CONSISTENCY_MODEL=The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Replica set, writer authority and configuration identity are current and durable.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Catch-up, repair, rejoin, compaction and corruption handling are tested.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Repair has source authority, bounded resource use, rejoin gates and post-repair semantic/integrity validation.
- **REQUIRED_PRECONDITIONS:** Stable identity/version, current membership, repair-source policy, integrity checks, capacity budget and tombstone horizon. | The replica model, permitted anomalies, convergence rule and semantic invariant are explicit. | Replica set, writer authority and configuration identity are current and durable. | Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. | Catch-up, repair, rejoin, compaction and corruption handling are tested. | Lag, divergence, repair source, membership and invariant checks are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** No inherent convergence deadline; Checksums show difference, not correct source; Repair can create metastable overload
- **ANTI_CEREMONY_BOUNDARY:** Running a periodic repair command is ceremony unless authority and result are established.
- **POSSIBLE_CONFLICTING_PROPERTY:** P29/P33: aggressive repair can conflict with foreground capacity and stable recovery.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can repair spread corruption or obsolete state into healthy replicas?
  - What source-authority, capacity and rejoin checks bound catch-up?

### P10 — Quorum validity bound to current membership and configuration
- **DISTRIBUTED_FAILURE_MODE:** Partitions and reconfiguration allow conflicting views of who may vote or serve state.
- **MATURE_FORM:** A quorum certificate identifies current configuration, epoch and state position.
- **TRIGGER:** Replicated decision, leader election, lock service or strong database read/write.
- **CHEAP_PATH:** One current durable owner or local transaction.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; TIMING_MODEL=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; NETWORK_ASSUMPTIONS=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; STORAGE_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; RECOVERY_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Current term, configuration, quorum and commit position can be reconstructed.; CHEAP_PATH=One current durable owner or local transaction.; MATURE_FORM=A quorum certificate identifies current configuration, epoch and state position.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; MEMBERSHIP_LINK=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; MATURE_FORM=A quorum certificate identifies current configuration, epoch and state position.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Agreement/order does not itself establish application semantic validity.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=A quorum certificate identifies current configuration, epoch and state position.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Protocol messages are term/configuration bound and stale messages are rejected.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=A quorum certificate identifies current configuration, epoch and state position.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=A quorum certificate identifies current configuration, epoch and state position.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=A quorum certificate identifies current configuration, epoch and state position.
- **REQUIRED_PRECONDITIONS:** Authoritative configuration identity, unique durable member ID, persisted vote/log and proven transitional overlap. | Agreement/order does not itself establish application semantic validity. | Terms, views, ballots, configurations and durable member identity bind every decision and mutation. | Protocol messages are term/configuration bound and stale messages are rejected. | Votes, log position, snapshots and configuration state survive restart without rollback of authority. | Current term, configuration, quorum and commit position can be reconstructed.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Larger quorums reduce availability and raise latency; Dynamic reconfiguration is difficult; Intersection does not validate application values
- **ANTI_CEREMONY_BOUNDARY:** 'Three nodes, therefore safe' is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11: larger/more constrained quorums improve safety margin but reduce liveness.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What is the authoritative membership for each quorum claim?
  - Can old and new configurations each form a decision set or restored identities vote twice?

### P11 — Consensus safety separated from liveness and semantic validity
- **DISTRIBUTED_FAILURE_MODE:** Partitions, slow links and failures prevent progress while agreement remains intact; agreement can choose bad input.
- **MATURE_FORM:** Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **TRIGGER:** Replicated exclusive decision or ordered log whose divergence would violate an invariant.
- **CHEAP_PATH:** Local durable owner, commutative/partitionable state or explicit manual arbitration.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; TIMING_MODEL=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; NETWORK_ASSUMPTIONS=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; STORAGE_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; RECOVERY_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Current term, configuration, quorum and commit position can be reconstructed.; CHEAP_PATH=Local durable owner, commutative/partitionable state or explicit manual arbitration.; MATURE_FORM=Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; MEMBERSHIP_LINK=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; MATURE_FORM=Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Agreement/order does not itself establish application semantic validity.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Protocol messages are term/configuration bound and stale messages are rejected.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately.
- **REQUIRED_PRECONDITIONS:** Fault/timing model, durable vote/log, membership, deterministic application and input validation. | Agreement/order does not itself establish application semantic validity. | Terms, views, ballots, configurations and durable member identity bind every decision and mutation. | Protocol messages are term/configuration bound and stale messages are rejected. | Votes, log position, snapshots and configuration state survive restart without rollback of authority. | Current term, configuration, quorum and commit position can be reconstructed.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Consensus is overused; Leader implementations can bottleneck; Proofs may not cover storage/reconfiguration/integration bugs
- **ANTI_CEREMONY_BOUNDARY:** A leader dashboard is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P45/P54: consensus can conflict with the cheap path where no exclusive invariant exists.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which claim is safety, which is liveness, and what timing assumptions support each?
  - Can every participant agree on a semantically invalid command or stale external reference?

### P12 — Versioned membership and safe reconfiguration
- **DISTRIBUTED_FAILURE_MODE:** Multiple configurations remain actionable across partition, delayed messaging or restore.
- **MATURE_FORM:** Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **TRIGGER:** Dynamic replica set, shard movement, autoscaling or disaster rebuild participating in authority.
- **CHEAP_PATH:** Static single owner or whole-system offline replacement under an exclusive boundary.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; TIMING_MODEL=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; NETWORK_ASSUMPTIONS=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; STORAGE_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; RECOVERY_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Current term, configuration, quorum and commit position can be reconstructed.; CHEAP_PATH=Static single owner or whole-system offline replacement under an exclusive boundary.; MATURE_FORM=Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; MEMBERSHIP_LINK=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; MATURE_FORM=Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Agreement/order does not itself establish application semantic validity.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Protocol messages are term/configuration bound and stale messages are rejected.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Membership is authoritative replicated state; decisions and mutations carry configuration/epoch through handoff.
- **REQUIRED_PRECONDITIONS:** Unique durable identity, configuration log, state transfer/catch-up, overlap proof and operator-visible transition. | Agreement/order does not itself establish application semantic validity. | Terms, views, ballots, configurations and durable member identity bind every decision and mutation. | Protocol messages are term/configuration bound and stale messages are rejected. | Votes, log position, snapshots and configuration state survive restart without rollback of authority. | Current term, configuration, quorum and commit position can be reconstructed.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Safe reconfiguration can reduce availability; Tooling often bypasses protocol; Proofs assume reliable identity/storage
- **ANTI_CEREMONY_BOUNDARY:** Editing a node list or scaling a controller is not safe reconfiguration.
- **POSSIBLE_CONFLICTING_PROPERTY:** P11/P37: safe reconfiguration can delay recovery or maintenance.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - How is membership changed and reconstructed after restart or restore?
  - Can a joining/restored member vote before current state and configuration are established?

### P13 — Current mutation authority enforced by epochs or fencing
- **DISTRIBUTED_FAILURE_MODE:** Stale actors remain live and delayed writes arrive after handoff.
- **MATURE_FORM:** Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **TRIGGER:** Exclusive writer, task lease, distributed lock, failover, shard ownership or maintenance handoff.
- **CHEAP_PATH:** Local mutex/process ownership; commutative operation; local transaction with version check.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; TIMING_MODEL=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; NETWORK_ASSUMPTIONS=Crash-recovery, network partition, delayed/stale messages, duplicated identity, reconfiguration and—only when declared—arbitrary faults.; STORAGE_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; RECOVERY_ASSUMPTIONS=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Current term, configuration, quorum and commit position can be reconstructed.; CHEAP_PATH=Local mutex/process ownership; commutative operation; local transaction with version check.; MATURE_FORM=Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Safety and liveness assumptions are separated; progress usually relies on partial synchrony and a reachable quorum.; MEMBERSHIP_LINK=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; MATURE_FORM=Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Agreement/order does not itself establish application semantic validity.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Protocol messages are term/configuration bound and stale messages are rejected.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Terms, views, ballots, configurations and durable member identity bind every decision and mutation.; GENERATION_OR_EPOCH=Monotone term/view/fencing token generated at ownership transfer.; STALE_REJECTION=Atomic rejection at each protected sink, not voluntary stopping by the actor.; MATURE_FORM=Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Votes, log position, snapshots and configuration state survive restart without rollback of authority.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised.
- **REQUIRED_PRECONDITIONS:** Durable monotone generation, resource-side compare/reject, ownership-transfer protocol and effect identity. | Agreement/order does not itself establish application semantic validity. | Terms, views, ballots, configurations and durable member identity bind every decision and mutation. | Protocol messages are term/configuration bound and stale messages are rejected. | Votes, log position, snapshots and configuration state survive restart without rollback of authority. | Current term, configuration, quorum and commit position can be reconstructed.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Every sink must cooperate; Physical/third-party effects may not accept tokens; Authority service can be unavailable
- **ANTI_CEREMONY_BOUNDARY:** Owning a lock object or seeing oneself as leader is not the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P37: conservative fencing/currentness checks can slow failover.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does every mutation carry a generation enforced by the protected resource?
  - Can a paused former leader or expired worker resume after ownership transfers?

### P14 — Single-writer or local-transaction cheap path
- **DISTRIBUTED_FAILURE_MODE:** Remote uncertainty, coordination and recovery machinery are created where local atomicity would suffice.
- **MATURE_FORM:** Start local or single-writer; distribute only the dimension with demonstrated need.
- **TRIGGER:** Low write scale, central invariant, tightly coupled data, modest availability demand or easy recovery.
- **CHEAP_PATH:** This property is the cheap path; distribution triggers only after a concrete consumer appears.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; TIMING_MODEL=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; NETWORK_ASSUMPTIONS=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; STORAGE_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; RECOVERY_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Lag, divergence, repair source, membership and invariant checks are observable.; CHEAP_PATH=This property is the cheap path; distribution triggers only after a concrete consumer appears.; MATURE_FORM=Start local or single-writer; distribute only the dimension with demonstrated need.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; MEMBERSHIP_LINK=Replica set, writer authority and configuration identity are current and durable.; MATURE_FORM=Start local or single-writer; distribute only the dimension with demonstrated need.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=PRIMARY; CONSISTENCY_MODEL=The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Start local or single-writer; distribute only the dimension with demonstrated need.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Start local or single-writer; distribute only the dimension with demonstrated need.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Replica set, writer authority and configuration identity are current and durable.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Start local or single-writer; distribute only the dimension with demonstrated need.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Catch-up, repair, rejoin, compaction and corruption handling are tested.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Start local or single-writer; distribute only the dimension with demonstrated need.
- **REQUIRED_PRECONDITIONS:** Clear ownership, local durability, tested backup and fenced promotion if automatic failover exists. | The replica model, permitted anomalies, convergence rule and semantic invariant are explicit. | Replica set, writer authority and configuration identity are current and durable. | Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. | Catch-up, repair, rejoin, compaction and corruption handling are tested. | Lag, divergence, repair source, membership and invariant checks are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=MEDIUM; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Centralisation may fail latency/availability goals; Future scaling can be difficult; One process is not automatically durable
- **ANTI_CEREMONY_BOUNDARY:** A monolith is not automatically good, but distribution is not maturity.
- **POSSIBLE_CONFLICTING_PROPERTY:** P03/P45: centralisation may conflict with required failure independence or latency locality.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Could one durable writer or local transaction own the invariant?
  - What concrete requirement justifies distributing this state?

### P15 — Strong coordination for non-confluent invariants
- **DISTRIBUTED_FAILURE_MODE:** Partitioned or concurrent actors each act on incomplete state and jointly break the invariant.
- **MATURE_FORM:** Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **TRIGGER:** Demonstrated non-confluence, globally scarce resource or irreversible action requiring an exclusive current decision.
- **CHEAP_PATH:** Independent commutative operations, ownership partitioning, escrowed budgets or one local owner.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation.; TIMING_MODEL=Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome.; NETWORK_ASSUMPTIONS=Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation.; STORAGE_ASSUMPTIONS=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; RECOVERY_ASSUMPTIONS=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.; CHEAP_PATH=Independent commutative operations, ownership partitioning, escrowed budgets or one local owner.; MATURE_FORM=Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome.; MEMBERSHIP_LINK=Participants/coordinator/owners and transaction generation are durable and current.; MATURE_FORM=Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Atomicity/isolation covers only the declared transaction boundary; external effects need another closure.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Transaction messages and external calls have stable identity and duplicate-safe recovery.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Participants/coordinator/owners and transaction generation are durable and current.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation.
- **REQUIRED_PRECONDITIONS:** Invariant definition, operation set, consistency target, current authority/membership, failure and recovery model. | Atomicity/isolation covers only the declared transaction boundary; external effects need another closure. | Participants/coordinator/owners and transaction generation are durable and current. | Transaction messages and external calls have stable identity and duplicate-safe recovery. | Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable. | Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Coordination hurts latency/availability; Some invariants can be redesigned or escrowed; Blanket 2PC/consensus overcoordinates
- **ANTI_CEREMONY_BOUNDARY:** Consensus everywhere is ceremony; invariant-scoped coordination is the property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P16/P54: strong coordination conflicts with safe autonomy and scale.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which invariant would independent concurrent operations violate?
  - Is coordination scoped to the smallest closure that protects it, including external effects?

### P16 — Coordination avoidance for invariant-confluent, commutative or partitionable operations
- **DISTRIBUTED_FAILURE_MODE:** Unnecessary cross-node coordination turns delay/partition into availability and latency cost.
- **MATURE_FORM:** Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **TRIGGER:** High-latency or partitioned environment where operation semantics support safe independent execution.
- **CHEAP_PATH:** Non-confluent uniqueness/conservation/exclusive authority or irreversible global effects should coordinate instead.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; TIMING_MODEL=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; NETWORK_ASSUMPTIONS=Replica divergence, stale reads, concurrent writes, partition, corruption, repair error, common-mode failure and obsolete membership.; STORAGE_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; RECOVERY_ASSUMPTIONS=Catch-up, repair, rejoin, compaction and corruption handling are tested.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Lag, divergence, repair source, membership and invariant checks are observable.; CHEAP_PATH=Non-confluent uniqueness/conservation/exclusive authority or irreversible global effects should coordinate instead.; MATURE_FORM=Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Availability and convergence may be asynchronous; bounded staleness requires a separate bound and measurement.; MEMBERSHIP_LINK=Replica set, writer authority and configuration identity are current and durable.; MATURE_FORM=Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=PRIMARY; CONSISTENCY_MODEL=The replica model, permitted anomalies, convergence rule and semantic invariant are explicit.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Replica set, writer authority and configuration identity are current and durable.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Catch-up, repair, rejoin, compaction and corruption handling are tested.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Coordinate only the non-confluent subset and retain strong operations alongside mergeable ones.
- **REQUIRED_PRECONDITIONS:** Operation algebra, merge rule, invariant, duplicate/reorder semantics, metadata retention and ownership boundaries. | The replica model, permitted anomalies, convergence rule and semantic invariant are explicit. | Replica set, writer authority and configuration identity are current and durable. | Replication messages tolerate duplicate/reorder according to the protocol and retain required version metadata. | Catch-up, repair, rejoin, compaction and corruption handling are tested. | Lag, divergence, repair source, membership and invariant checks are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=MEDIUM; OUTAGE_OR_FAILURE_CASE_STRENGTH=MEDIUM; INDUSTRIAL_PRACTICE_STRENGTH=MEDIUM; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=MEDIUM; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Application semantics are hard to formalise; Complexity can move into reconciliation; Not every converged state is meaningful
- **ANTI_CEREMONY_BOUNDARY:** 'Use a CRDT' is ceremony without invariant and lifecycle proof.
- **POSSIBLE_CONFLICTING_PROPERTY:** P15: coordination avoidance conflicts with hidden non-confluent invariants.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What proof or counterexample search shows independently valid states merge without violating the invariant?
  - Do schema changes, external effects or cross-object constraints invalidate partitionability?

### P17 — Duplicate-aware delivery semantics
- **DISTRIBUTED_FAILURE_MODE:** Producer, broker and consumer fail independently; acknowledgement and state updates are separated.
- **MATURE_FORM:** Name semantics at every boundary and independently close the business-effect boundary.
- **TRIGGER:** Asynchronous transfer, queue, event log, task dispatch or producer/consumer retry.
- **CHEAP_PATH:** Direct local call/transaction or fire-and-forget telemetry where loss is accepted.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; TIMING_MODEL=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; NETWORK_ASSUMPTIONS=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; STORAGE_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; RECOVERY_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.; CHEAP_PATH=Direct local call/transaction or fire-and-forget telemetry where loss is accepted.; MATURE_FORM=Name semantics at every boundary and independently close the business-effect boundary.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; MEMBERSHIP_LINK=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; MATURE_FORM=Name semantics at every boundary and independently close the business-effect boundary.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=State/effect and acknowledgement/offset atomicity are explicit where claimed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Name semantics at every boundary and independently close the business-effect boundary.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=PRIMARY; DELIVERY_MODEL=Transport attempt, message, processing, business operation and external effect identities are distinct.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Name semantics at every boundary and independently close the business-effect boundary.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Name semantics at every boundary and independently close the business-effect boundary.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay, poison handling, dedup retention and unknown outcomes survive restart.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Name semantics at every boundary and independently close the business-effect boundary.
- **REQUIRED_PRECONDITIONS:** Durable event identity, producer/consumer state, retention, ordering partition and failure/rebalance semantics. | State/effect and acknowledgement/offset atomicity are explicit where claimed. | Producer/consumer/task ownership generations are current for ordered or exclusive processing. | Transport attempt, message, processing, business operation and external effect identities are distinct. | Replay, poison handling, dedup retention and unknown outcomes survive restart. | Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** At-most-once may lose work; At-least-once shifts burden to consumer; Platform-scoped exactly-once can be costly and narrow
- **ANTI_CEREMONY_BOUNDARY:** A broker checkbox labelled exactly-once is not an end-to-end guarantee.
- **POSSIBLE_CONFLICTING_PROPERTY:** P21/P49: transport semantics conflict with unqualified end-to-end effect claims.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What delivery semantics hold after producer retry, broker restart, consumer crash and rebalance?
  - Does acknowledgement advance atomically with the state/effect it is claimed to cover?

### P18 — End-to-end business-operation and effect identity
- **DISTRIBUTED_FAILURE_MODE:** Independent components retry and replay without a shared semantic identifier.
- **MATURE_FORM:** Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **TRIGGER:** Retriable mutation, long-running workflow, external irreversible action or cross-service transaction.
- **CHEAP_PATH:** Pure read, locally atomic mutation with no reply-loss concern, or disposable telemetry.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; TIMING_MODEL=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; NETWORK_ASSUMPTIONS=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; STORAGE_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; RECOVERY_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.; CHEAP_PATH=Pure read, locally atomic mutation with no reply-loss concern, or disposable telemetry.; MATURE_FORM=Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; MEMBERSHIP_LINK=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; MATURE_FORM=Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=State/effect and acknowledgement/offset atomicity are explicit where claimed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=PRIMARY; DELIVERY_MODEL=Transport attempt, message, processing, business operation and external effect identities are distinct.; IDENTITY_SCOPE=Principal/tenant, immutable semantic parameters and intended effect; attempts are many-to-one with the operation.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay, poison handling, dedup retention and unknown outcomes survive restart.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Identity is semantic and lifecycle-scoped; every attempt and effect is linked without conflating changed intent.
- **REQUIRED_PRECONDITIONS:** Canonical operation definition, parameter binding, tenant/principal scope, retention and effect ledger/status query. | State/effect and acknowledgement/offset atomicity are explicit where claimed. | Producer/consumer/task ownership generations are current for ordered or exclusive processing. | Transport attempt, message, processing, business operation and external effect identities are distinct. | Replay, poison handling, dedup retention and unknown outcomes survive restart. | Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Global identity can cost privacy/cardinality; Canonicalisation is application-specific; Identity alone does not prevent duplicates
- **ANTI_CEREMONY_BOUNDARY:** Adding a UUID header is ceremony if semantics, scope and retention are undefined.
- **POSSIBLE_CONFLICTING_PROPERTY:** P42: high-cardinality identity/provenance conflicts with privacy and telemetry cost.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is the key bound to immutable semantic parameters, actor and intended effect?
  - Can every attempt and external effect be traced to one business operation without conflating changed intent?

### P19 — Semantic idempotency, not request-ID ritual
- **DISTRIBUTED_FAILURE_MODE:** Retries, redelivery and late arrivals reach several independently failing effect boundaries.
- **MATURE_FORM:** The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **TRIGGER:** Any mutation or activity that may be retried, redelivered, replayed or concurrently submitted.
- **CHEAP_PATH:** Pure read, commutative accumulation with duplicate identity, or one local transaction.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; TIMING_MODEL=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; NETWORK_ASSUMPTIONS=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; STORAGE_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; RECOVERY_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.; CHEAP_PATH=Pure read, commutative accumulation with duplicate identity, or one local transaction.; MATURE_FORM=The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; MEMBERSHIP_LINK=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; MATURE_FORM=The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=State/effect and acknowledgement/offset atomicity are explicit where claimed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=PRIMARY; DELIVERY_MODEL=Transport attempt, message, processing, business operation and external effect identities are distinct.; IDENTITY_SCOPE=Semantic operation plus immutable parameter/effect fingerprint.; ACK_BOUNDARY=A stored idempotency result proves only the effects atomically enclosed with it.; MATURE_FORM=The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay, poison handling, dedup retention and unknown outcomes survive restart.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay.
- **REQUIRED_PRECONDITIONS:** Operation identity, canonical parameters, current precondition/version, durable result record, downstream closure and retention horizon. | State/effect and acknowledgement/offset atomicity are explicit where claimed. | Producer/consumer/task ownership generations are current for ordered or exclusive processing. | Transport attempt, message, processing, business operation and external effect identities are distinct. | Replay, poison handling, dedup retention and unknown outcomes survive restart. | Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Natural idempotency is rare for many physical effects; Dedup storage grows; A cached response may hide changed external state
- **ANTI_CEREMONY_BOUNDARY:** 'We add a request ID' is not idempotency.
- **POSSIBLE_CONFLICTING_PROPERTY:** P20: semantic idempotency conflicts with finite evidence retention and evolving semantics.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact semantic effect is duplicate-safe, and at which boundary?
  - Can changed parameters reuse a key or can a downstream effect repeat even when the endpoint deduplicates?

### P20 — Bounded deduplication and replay horizon
- **DISTRIBUTED_FAILURE_MODE:** Long partitions, restore from old backup, delayed queues and operator replay exceed the assumed window.
- **MATURE_FORM:** Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **TRIGGER:** Finite dedup cache, TTL, log retention, replay, delayed replica rejoin or disaster restore.
- **CHEAP_PATH:** No retries/replay and bounded local execution, or effect is naturally harmless under repetition.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; TIMING_MODEL=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; NETWORK_ASSUMPTIONS=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; STORAGE_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; RECOVERY_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.; CHEAP_PATH=No retries/replay and bounded local execution, or effect is naturally harmless under repetition.; MATURE_FORM=Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; MEMBERSHIP_LINK=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; MATURE_FORM=Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=State/effect and acknowledgement/offset atomicity are explicit where claimed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=PRIMARY; DELIVERY_MODEL=Transport attempt, message, processing, business operation and external effect identities are distinct.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay, poison handling, dedup retention and unknown outcomes survive restart.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Every dedup/compaction expiry has an explicit maximum-age assumption and behaviour for older arrivals.
- **REQUIRED_PRECONDITIONS:** End-to-end maximum delay, restore age, retention policy, compaction rules and explicit post-expiry consequence. | State/effect and acknowledgement/offset atomicity are explicit where claimed. | Producer/consumer/task ownership generations are current for ordered or exclusive processing. | Transport attempt, message, processing, business operation and external effect identities are distinct. | Replay, poison handling, dedup retention and unknown outcomes survive restart. | Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Worst-case retention can be expensive; Unbounded partitions make finite guarantees impossible; Legal/business horizons may exceed technical retry windows
- **ANTI_CEREMONY_BOUNDARY:** A seven-day idempotency window is not a permanent exactly-once guarantee.
- **POSSIBLE_CONFLICTING_PROPERTY:** P39: long retention conflicts with schema/version retirement.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can any retry, queue, restore or replica rejoin occur after dedup/tombstone evidence expires?
  - What happens to arrivals older than the supported horizon?

### P21 — Acknowledgement separated from verified external effect
- **DISTRIBUTED_FAILURE_MODE:** Effects cross several independent systems and some acknowledgements are lost or emitted before downstream completion.
- **MATURE_FORM:** Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **TRIGGER:** Multi-hop action, asynchronous processing, third-party/physical effect or workflow completion.
- **CHEAP_PATH:** Single local transaction whose return covers the entire required state change.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; TIMING_MODEL=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; NETWORK_ASSUMPTIONS=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; STORAGE_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; RECOVERY_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.; CHEAP_PATH=Single local transaction whose return covers the entire required state change.; MATURE_FORM=Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; MEMBERSHIP_LINK=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; MATURE_FORM=Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=State/effect and acknowledgement/offset atomicity are explicit where claimed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=PRIMARY; DELIVERY_MODEL=Transport attempt, message, processing, business operation and external effect identities are distinct.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=Explicit durable boundary; downstream/physical effects remain separate until observed or atomically enclosed.; MATURE_FORM=Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay, poison handling, dedup retention and unknown outcomes survive restart.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Completion is defined by the consumer's postcondition, with the evidence boundary and remaining uncertainty stated.
- **REQUIRED_PRECONDITIONS:** Declared postcondition, authoritative observation, provenance, effect identity and uncertainty/compensation policy. | State/effect and acknowledgement/offset atomicity are explicit where claimed. | Producer/consumer/task ownership generations are current for ordered or exclusive processing. | Transport attempt, message, processing, business operation and external effect identities are distinct. | Replay, poison handling, dedup retention and unknown outcomes survive restart. | Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Independent verification may be expensive or impossible; Observation can race later reversal; Some effects are only probabilistically observable
- **ANTI_CEREMONY_BOUNDARY:** A 200 response, broker ACK or worker DONE is not completion by itself.
- **POSSIBLE_CONFLICTING_PROPERTY:** P27: cheap acknowledgement conflicts with expensive external postcondition verification.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact state does each ACK establish?
  - Does DONE mean report received, durable workflow transition, or independently observed required effect?

### P22 — Transactional messaging or outbox/inbox closure
- **DISTRIBUTED_FAILURE_MODE:** Database and broker fail independently; network/retry separates commit from message acknowledgement.
- **MATURE_FORM:** The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **TRIGGER:** A local transaction must reliably cause or record an asynchronous message, or a consumed event must update state exactly once within the closure.
- **CHEAP_PATH:** Direct local state change with no asynchronous notification requirement.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; TIMING_MODEL=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; NETWORK_ASSUMPTIONS=Message loss, duplication, reordering, redelivery, acknowledgement loss, producer/consumer crash, rebalance and late replay.; STORAGE_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; RECOVERY_ASSUMPTIONS=Replay, poison handling, dedup retention and unknown outcomes survive restart.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.; CHEAP_PATH=Direct local state change with no asynchronous notification requirement.; MATURE_FORM=The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Asynchronous delay is possible; visibility timeouts and retry deadlines are policy bounds, not outcome proofs.; MEMBERSHIP_LINK=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; MATURE_FORM=The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=State/effect and acknowledgement/offset atomicity are explicit where claimed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=PRIMARY; DELIVERY_MODEL=Transport attempt, message, processing, business operation and external effect identities are distinct.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Producer/consumer/task ownership generations are current for ordered or exclusive processing.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Replay, poison handling, dedup retention and unknown outcomes survive restart.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=The state-to-message boundary has a durable recovery record; any remaining external boundary is explicit.
- **REQUIRED_PRECONDITIONS:** Stable event identity, publisher relay/recovery, ordering assumptions, dedup horizon and explicit external-effect boundary. | State/effect and acknowledgement/offset atomicity are explicit where claimed. | Producer/consumer/task ownership generations are current for ordered or exclusive processing. | Transport attempt, message, processing, business operation and external effect identities are distinct. | Replay, poison handling, dedup retention and unknown outcomes survive restart. | Attempts, duplicates, redeliveries, lag, acknowledgement boundary and effect status are observable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Adds storage/relay complexity; Still not atomic with arbitrary third parties; Ordering across partitions is limited
- **ANTI_CEREMONY_BOUNDARY:** Having a broker and an outbox table is not closure if relay, dedup and replay are unowned.
- **POSSIBLE_CONFLICTING_PROPERTY:** P23/P24: local handoff closure conflicts with a need for full atomicity or domain compensation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can state commit without publication, or consumption/effect occur without durable acknowledgement?
  - Where is the atomic closure and where does it stop?

### P23 — Explicit transactional boundary and atomic-commit choice
- **DISTRIBUTED_FAILURE_MODE:** Coordinator or participant fails between prepare/commit; partitions leave in-doubt participants or partial external effects.
- **MATURE_FORM:** Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **TRIGGER:** A non-compensatable invariant requires all-or-nothing across multiple transactional participants.
- **CHEAP_PATH:** One local transaction; or independently commit compensatable steps with a durable saga.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation.; TIMING_MODEL=Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome.; NETWORK_ASSUMPTIONS=Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation.; STORAGE_ASSUMPTIONS=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; RECOVERY_ASSUMPTIONS=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.; CHEAP_PATH=One local transaction; or independently commit compensatable steps with a durable saga.; MATURE_FORM=Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome.; MEMBERSHIP_LINK=Participants/coordinator/owners and transaction generation are durable and current.; MATURE_FORM=Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Atomicity/isolation covers only the declared transaction boundary; external effects need another closure.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Transaction messages and external calls have stable identity and duplicate-safe recovery.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Participants/coordinator/owners and transaction generation are durable and current.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Choose atomic commit for a named non-compensatable closure; otherwise prefer local transactions plus durable handoff/compensation.
- **REQUIRED_PRECONDITIONS:** Participant durability, coordinator log, isolation, recovery protocol, timeout semantics and explicit exclusion of nonparticipants. | Atomicity/isolation covers only the declared transaction boundary; external effects need another closure. | Participants/coordinator/owners and transaction generation are durable and current. | Transaction messages and external calls have stable identity and duplicate-safe recovery. | Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable. | Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** 2PC can block and add latency; Blanket rejection ignores cases where atomicity is worth cost; Blanket adoption extends scope too far
- **ANTI_CEREMONY_BOUNDARY:** 'ACID' or '2PC' without participant/effect boundary is ceremony.
- **POSSIBLE_CONFLICTING_PROPERTY:** P24: synchronous atomicity conflicts with long-duration autonomy and compensation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which resources actually participate in one atomic commit?
  - What state remains in-doubt after coordinator or network failure, and how is it resolved?

### P24 — Compensation and forward recovery with semantic limits
- **DISTRIBUTED_FAILURE_MODE:** Later step fails after earlier durable/internal/external effects; compensation can also fail or be non-inverse.
- **MATURE_FORM:** Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **TRIGGER:** Long-running, cross-service or external workflow whose effects are compensatable or repairable but not globally atomic.
- **CHEAP_PATH:** One atomic local/distributed transaction when the whole closure can and should commit together.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation.; TIMING_MODEL=Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome.; NETWORK_ASSUMPTIONS=Concurrent updates, coordinator/participant crash, partition, partial commit, blocked in-doubt state, duplicate side effect and failed compensation.; STORAGE_ASSUMPTIONS=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; RECOVERY_ASSUMPTIONS=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.; CHEAP_PATH=One atomic local/distributed transaction when the whole closure can and should commit together.; MATURE_FORM=Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Blocking and latency under partition/long-running work are explicit; timeout does not resolve atomic outcome.; MEMBERSHIP_LINK=Participants/coordinator/owners and transaction generation are durable and current.; MATURE_FORM=Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Atomicity/isolation covers only the declared transaction boundary; external effects need another closure.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Transaction messages and external calls have stable identity and duplicate-safe recovery.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Participants/coordinator/owners and transaction generation are durable and current.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Compensation states what it restores, what it cannot restore and how unresolved residuals are detected and escalated.
- **REQUIRED_PRECONDITIONS:** Effect identity, compensation semantics, ordering, duplicate safety, durable orchestration, current external-state observation and manual path. | Atomicity/isolation covers only the declared transaction boundary; external effects need another closure. | Participants/coordinator/owners and transaction generation are durable and current. | Transaction messages and external calls have stable identity and duplicate-safe recovery. | Coordinator logs, participant states, compensation/forward-recovery ordering and manual resolution are durable. | Prepared/in-doubt/committed/compensating states and unresolved external effects are discoverable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Sagas expose intermediate state; Compensations demand domain knowledge; Complexity may exceed a scoped transaction
- **ANTI_CEREMONY_BOUNDARY:** A compensating endpoint on a diagram is not recovery evidence.
- **POSSIBLE_CONFLICTING_PROPERTY:** P23: compensation complexity conflicts with a small non-compensatable atomic closure.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is each compensation a true inverse, a new balancing action, or only a status adjustment?
  - Can compensation fail, duplicate or race changed external state?

### P25 — Durable workflow state as a recoverable distributed state machine
- **DISTRIBUTED_FAILURE_MODE:** Orchestrator and workers fail independently while tasks and external effects continue.
- **MATURE_FORM:** Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **TRIGGER:** Long-running, multi-step, retrying or externally signalled work that must survive process/platform restart.
- **CHEAP_PATH:** Synchronous local call/transaction whose whole lifetime fits one reliable execution boundary.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; TIMING_MODEL=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; NETWORK_ASSUMPTIONS=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; STORAGE_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; RECOVERY_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Workflow state, task attempts, effect status and version are reconstructable.; CHEAP_PATH=Synchronous local call/transaction whose whole lifetime fits one reliable execution boundary.; MATURE_FORM=Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; MEMBERSHIP_LINK=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; MATURE_FORM=Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Durable workflow state is distinct from correctness/currentness of external systems.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Workflow history is authoritative for orchestration, while external state is independently validated where required.
- **REQUIRED_PRECONDITIONS:** Durable ordered history, stable workflow/run identity, deterministic/versioned orchestration and external-effect reconciliation. | Durable workflow state is distinct from correctness/currentness of external systems. | Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. | Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. | History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. | Workflow state, task attempts, effect status and version are reconstructable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Persistence adds latency/cost; History can grow; Durability does not guarantee semantic correctness of external world
- **ANTI_CEREMONY_BOUNDARY:** Deploying a workflow engine is not the property if workflow/effect state is not durable and reconcilable.
- **POSSIBLE_CONFLICTING_PROPERTY:** P45: durable orchestration conflicts with a simple synchronous/local operation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What workflow state survives orchestrator restart?
  - Can the durable history reconstruct task ownership, retries, timers, signals and unresolved external effects?

### P26 — Task ownership, lease expiry and duplicate-safe re-dispatch
- **DISTRIBUTED_FAILURE_MODE:** Two attempts concurrently believe they own one task or external effect.
- **MATURE_FORM:** Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **TRIGGER:** Task queue, visibility timeout, worker lease, heartbeat or automatic re-dispatch.
- **CHEAP_PATH:** One local worker under a process-local lock, or harmless repeatable calculation with no effect.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; TIMING_MODEL=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; NETWORK_ASSUMPTIONS=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; STORAGE_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; RECOVERY_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Workflow state, task attempts, effect status and version are reconstructable.; CHEAP_PATH=One local worker under a process-local lock, or harmless repeatable calculation with no effect.; MATURE_FORM=Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; MEMBERSHIP_LINK=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; MATURE_FORM=Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Durable workflow state is distinct from correctness/currentness of external systems.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; GENERATION_OR_EPOCH=Workflow task attempt generation or ownership epoch.; STALE_REJECTION=Each mutable sink fences old attempts or the operation is semantically duplicate-safe.; MATURE_FORM=Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Re-dispatch is safe even if the prior actor resumes; the mechanism is fencing, semantic idempotency or explicit compensation.
- **REQUIRED_PRECONDITIONS:** Task/run/attempt identity, current ownership generation, timeout policy, effect closure, heartbeat semantics and durable retry record. | Durable workflow state is distinct from correctness/currentness of external systems. | Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. | Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. | History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. | Workflow state, task attempts, effect status and version are reconstructable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Fencing every external effect can be impossible; Long leases slow recovery; Short leases create false failover
- **ANTI_CEREMONY_BOUNDARY:** A visibility timeout or heartbeat is not proof the old worker cannot act.
- **POSSIBLE_CONFLICTING_PROPERTY:** P37: quick re-dispatch conflicts with stale-worker risk.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can a task be re-dispatched after lease/timeout without allowing the prior actor to perform a stale side effect?
  - What generation or semantic identity protects each effect?

### P27 — Completion defined by durable state plus verified postcondition
- **DISTRIBUTED_FAILURE_MODE:** Worker report, orchestrator commit and external observation occur in different failure domains.
- **MATURE_FORM:** DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **TRIGGER:** Completion drives user notification, billing, next workflow, resource release or irreversible decision.
- **CHEAP_PATH:** Local transaction return covers the complete required postcondition.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; TIMING_MODEL=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; NETWORK_ASSUMPTIONS=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; STORAGE_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; RECOVERY_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Workflow state, task attempts, effect status and version are reconstructable.; CHEAP_PATH=Local transaction return covers the complete required postcondition.; MATURE_FORM=DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; MEMBERSHIP_LINK=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; MATURE_FORM=DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Durable workflow state is distinct from correctness/currentness of external systems.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=Terminal state records the exact evidence boundary and residual unverified effects.; MATURE_FORM=DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN.
- **REQUIRED_PRECONDITIONS:** Consumer-defined postcondition, authoritative evidence source, operation/effect identity, currentness and residual uncertainty policy. | Durable workflow state is distinct from correctness/currentness of external systems. | Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. | Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. | History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. | Workflow state, task attempts, effect status and version are reconstructable.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Independent verification costs latency; Some real-world postconditions are not exactly observable; Continuous conditions can later become false
- **ANTI_CEREMONY_BOUNDARY:** Green task status is not completion.
- **POSSIBLE_CONFLICTING_PROPERTY:** P42: strong completion evidence conflicts with observability cost/unavailable external oracle.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does DONE mean worker report, durable workflow transition, or required external state independently observed?
  - Can terminal state remain PARTIAL/UNKNOWN until evidence arrives?

### P28 — Deterministic replay with explicit workflow/code version evolution
- **DISTRIBUTED_FAILURE_MODE:** Restarted orchestrator executes a different decision path from the one that produced persisted events.
- **MATURE_FORM:** History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **TRIGGER:** Replay-based durable workflow, event sourcing or state reconstruction across code versions.
- **CHEAP_PATH:** Persist explicit current state without replay, or finish short-lived work before incompatible deployment.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; TIMING_MODEL=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; NETWORK_ASSUMPTIONS=Worker/orchestrator crash, task redelivery, lease expiry, orphaned work, replay, cancellation race, code-version change and external side-effect uncertainty.; STORAGE_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; RECOVERY_ASSUMPTIONS=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Workflow state, task attempts, effect status and version are reconstructable.; CHEAP_PATH=Persist explicit current state without replay, or finish short-lived work before incompatible deployment.; MATURE_FORM=History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Timers, heartbeats and leases are policy evidence; they do not prove prior execution stopped.; MEMBERSHIP_LINK=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; MATURE_FORM=History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Durable workflow state is distinct from correctness/currentness of external systems.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=History, code and schema versions are explicit; every deployed version can replay or migrate all live histories.
- **REQUIRED_PRECONDITIONS:** Immutable history/event semantics, version identifiers, deterministic APIs, compatibility tests and migration/rollback plan. | Durable workflow state is distinct from correctness/currentness of external systems. | Workflow run, task attempt and worker generation identify current ownership; stale effects are fenced or neutralised. | Activity dispatch is assumed duplicable unless the entire effect boundary is atomically closed. | History/snapshot replay, versioning, unknown-effect reconciliation and manual intervention are retained. | Workflow state, task attempts, effect status and version are reconstructable.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Determinism constraints complicate programming; Version branches accumulate; External dependencies remain nondeterministic
- **ANTI_CEREMONY_BOUNDARY:** 'The engine replays deterministically' is not enough without code-evolution evidence.
- **POSSIBLE_CONFLICTING_PROPERTY:** P39: deterministic replay conflicts with rapid incompatible code/schema evolution.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can every live history replay under the deployed code and schemas?
  - What happens when deterministic workflow logic or an activity signature changes?

### P29 — Bounded queues with explicit work-age and capacity semantics
- **DISTRIBUTED_FAILURE_MODE:** Producers and consumers scale/fail independently; queue hides demand from upstream while downstream saturates.
- **MATURE_FORM:** Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **TRIGGER:** Asynchronous buffering between independently varying producer and consumer demand.
- **CHEAP_PATH:** Direct synchronous flow with natural backpressure, or small fixed local buffer where overload consequence is acceptable.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; TIMING_MODEL=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; NETWORK_ASSUMPTIONS=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; STORAGE_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; RECOVERY_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.; CHEAP_PATH=Direct synchronous flow with natural backpressure, or small fixed local buffer where overload consequence is acceptable.; MATURE_FORM=Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; MEMBERSHIP_LINK=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; MATURE_FORM=Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Consequence policy defines which work may be rejected, degraded, delayed or shed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Retries preserve operation identity and consume an explicit budget; shedding has visible consequence.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Queue admission is governed by the probability and value of completing work before its deadline, with explicit shed/defer behaviour.
- **REQUIRED_PRECONDITIONS:** Measured arrival/service distributions, deadline/value policy, storage limit, drain/recovery capacity and rejection semantics. | Consequence policy defines which work may be rejected, degraded, delayed or shed. | Admission and priority policy has a defined owner; no implicit per-hop policy conflict. | Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. | Backlog drain, retry release and recovery surge are capacity-bounded and observed. | Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Hard limits reject work; Burst absorption needs headroom; Capacity estimates vary and can be wrong
- **ANTI_CEREMONY_BOUNDARY:** 'We put a queue in front' is not resilience.
- **POSSIBLE_CONFLICTING_PROPERTY:** P31: buffering conflicts with early rejection and deadline preservation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Is queue capacity bounded by count, bytes and age, and by actual drain capacity?
  - What happens to work that cannot finish before its deadline?

### P30 — Backpressure propagated to the source of demand
- **DISTRIBUTED_FAILURE_MODE:** Each hop sees only local capacity and can amplify or buffer requests independently.
- **MATURE_FORM:** Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **TRIGGER:** Producer can outpace consumer or fan-out multiplies work.
- **CHEAP_PATH:** In-process bounded channel or naturally demand-driven iterator when no remote graph exists.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; TIMING_MODEL=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; NETWORK_ASSUMPTIONS=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; STORAGE_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; RECOVERY_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.; CHEAP_PATH=In-process bounded channel or naturally demand-driven iterator when no remote graph exists.; MATURE_FORM=Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; MEMBERSHIP_LINK=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; MATURE_FORM=Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Consequence policy defines which work may be rejected, degraded, delayed or shed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Retries preserve operation identity and consume an explicit budget; shedding has visible consequence.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Every admission path—including retries and async queues—consumes an explicit capacity signal that reaches demand origin.
- **REQUIRED_PRECONDITIONS:** Current dependency topology, demand accounting, admission semantics, retry integration and fairness policy. | Consequence policy defines which work may be rejected, degraded, delayed or shed. | Admission and priority policy has a defined owner; no implicit per-hop policy conflict. | Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. | Backlog drain, retry release and recovery surge are capacity-bounded and observed. | Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Coordination adds latency/state; Topology changes; Backpressure can reduce utilisation or create unfairness
- **ANTI_CEREMONY_BOUNDARY:** A local queue watermark with unconstrained upstream retries is not backpressure.
- **POSSIBLE_CONFLICTING_PROPERTY:** P31: backpressure conflicts with work that cannot be delayed and must be shed.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can saturation reach the original demand source, including retry and fan-out paths?
  - Where can work continue accumulating after a downstream backpressure signal?

### P31 — Admission control and load shedding with consequence policy
- **DISTRIBUTED_FAILURE_MODE:** Capacity and demand vary across dependencies; overload signals arrive late and partial.
- **MATURE_FORM:** Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **TRIGGER:** Demand can exceed sustainable service or shared bottlenecks can saturate.
- **CHEAP_PATH:** Fixed small system with hard external demand limit and no shared saturation risk.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; TIMING_MODEL=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; NETWORK_ASSUMPTIONS=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; STORAGE_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; RECOVERY_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.; CHEAP_PATH=Fixed small system with hard external demand limit and no shared saturation risk.; MATURE_FORM=Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; MEMBERSHIP_LINK=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; MATURE_FORM=Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Consequence policy defines which work may be rejected, degraded, delayed or shed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Retries preserve operation identity and consume an explicit budget; shedding has visible consequence.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Admission preserves a declared critical service set and tells callers whether to drop, retry later, degrade or escalate.
- **REQUIRED_PRECONDITIONS:** Capacity model, criticality/value classes, fairness policy, caller-visible rejection semantics, retry budget and telemetry. | Consequence policy defines which work may be rejected, degraded, delayed or shed. | Admission and priority policy has a defined owner; no implicit per-hop policy conflict. | Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. | Backlog drain, retry release and recovery surge are capacity-bounded and observed. | Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Shedding loses service; Priority can encode unfairness; Capacity estimates and value classification are imperfect
- **ANTI_CEREMONY_BOUNDARY:** A circuit breaker that drops unknown work without consequence policy is not mature load shedding.
- **POSSIBLE_CONFLICTING_PROPERTY:** P29: shedding conflicts with bounded burst absorption and fairness.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which work is preserved, delayed, degraded or shed under overload?
  - Will callers retry rejection and thereby defeat shedding?

### P32 — Retry budgets, exponential backoff, jitter and deadline propagation
- **DISTRIBUTED_FAILURE_MODE:** Partial failures/timeouts cause many clients to retransmit into a degraded shared dependency.
- **MATURE_FORM:** A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **TRIGGER:** Transient failure can plausibly recover within the remaining deadline and retry is semantically safe.
- **CHEAP_PATH:** No retry for permanent errors, expired work, non-idempotent effect without closure or already-overloaded dependency.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; TIMING_MODEL=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; NETWORK_ASSUMPTIONS=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; STORAGE_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; RECOVERY_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.; CHEAP_PATH=No retry for permanent errors, expired work, non-idempotent effect without closure or already-overloaded dependency.; MATURE_FORM=A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; MEMBERSHIP_LINK=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; MATURE_FORM=A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Consequence policy defines which work may be rejected, degraded, delayed or shed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Retries preserve operation identity and consume an explicit budget; shedding has visible consequence.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity.
- **REQUIRED_PRECONDITIONS:** Error classification, operation identity/idempotency, timeout distribution, downstream capacity signal, deadline and attempt accounting. | Consequence policy defines which work may be rejected, degraded, delayed or shed. | Admission and priority policy has a defined owner; no implicit per-hop policy conflict. | Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. | Backlog drain, retry release and recovery surge are capacity-bounded and observed. | Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Backoff delays recovery; Error classification is imperfect; Retries can hide systemic faults
- **ANTI_CEREMONY_BOUNDARY:** 'We use exponential backoff' is insufficient without attempt/deadline/idempotency/capacity bounds.
- **POSSIBLE_CONFLICTING_PROPERTY:** P02/P33: retries conflict with unknown outcomes and overload stability.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - How many retries can one original request trigger across all layers?
  - Do retries preserve identity, fit the remaining deadline and respect downstream capacity?

### P33 — Metastable and cascading-overload containment
- **DISTRIBUTED_FAILURE_MODE:** Independent components adapt locally in ways that amplify global demand and state transition.
- **MATURE_FORM:** The failure model includes amplification and a tested path out of the degraded state.
- **TRIGGER:** Fan-out, shared bottleneck, retry/cache/failover/backlog loop or recovery surge can feed on itself.
- **CHEAP_PATH:** Low-utilisation local system with no feedback path and trivial restart.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; TIMING_MODEL=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; NETWORK_ASSUMPTIONS=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; STORAGE_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; RECOVERY_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.; CHEAP_PATH=Low-utilisation local system with no feedback path and trivial restart.; MATURE_FORM=The failure model includes amplification and a tested path out of the degraded state.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; MEMBERSHIP_LINK=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; MATURE_FORM=The failure model includes amplification and a tested path out of the degraded state.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Consequence policy defines which work may be rejected, degraded, delayed or shed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=The failure model includes amplification and a tested path out of the degraded state.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Retries preserve operation identity and consume an explicit budget; shedding has visible consequence.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=The failure model includes amplification and a tested path out of the degraded state.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=The failure model includes amplification and a tested path out of the degraded state.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=The failure model includes amplification and a tested path out of the degraded state.
- **REQUIRED_PRECONDITIONS:** Dependency graph, demand/capacity telemetry, feedback-loop hypothesis, safe shedding and tested recovery ramp. | Consequence policy defines which work may be rejected, degraded, delayed or shed. | Admission and priority policy has a defined owner; no implicit per-hop policy conflict. | Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. | Backlog drain, retry release and recovery surge are capacity-bounded and observed. | Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Loops are difficult to identify before failure; Mitigations may reduce normal utilisation; Incident samples are selective
- **ANTI_CEREMONY_BOUNDARY:** Restarting failed instances is not recovery if the feedback loop persists.
- **POSSIBLE_CONFLICTING_PROPERTY:** P38: rapid automated recovery conflicts with preserving evidence and staged validation.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What positive-feedback loop can sustain degradation after the trigger is removed?
  - Is recovery traffic/backlog release itself capacity-bounded?

### P34 — Dependency isolation and bulkheads with end-to-end verification
- **DISTRIBUTED_FAILURE_MODE:** A slow/unavailable dependency consumes local resources while callers continue fan-out or fallback.
- **MATURE_FORM:** Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **TRIGGER:** Shared resource pool or dependency whose slowness/failure can block unrelated work.
- **CHEAP_PATH:** One small dependency path with no shared-resource contention or acceptable full-stop behaviour.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; TIMING_MODEL=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; NETWORK_ASSUMPTIONS=Queue growth, shared bottleneck saturation, retry amplification, synchronized clients, head-of-line blocking, cascading failure and metastable positive feedback.; STORAGE_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; RECOVERY_ASSUMPTIONS=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.; CHEAP_PATH=One small dependency path with no shared-resource contention or acceptable full-stop behaviour.; MATURE_FORM=Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Deadlines and service-time distributions matter; old work may be worthless even if capacity eventually returns.; MEMBERSHIP_LINK=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; MATURE_FORM=Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Consequence policy defines which work may be rejected, degraded, delayed or shed.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Retries preserve operation identity and consume an explicit budget; shedding has visible consequence.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Admission and priority policy has a defined owner; no implicit per-hop policy conflict.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Backlog drain, retry release and recovery surge are capacity-bounded and observed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Isolation corresponds to real shared resources/failure domains and has verified degraded/recovery behaviour.
- **REQUIRED_PRECONDITIONS:** Current topology, resource accounting, critical-path classification, fallback capacity and consequence policy. | Consequence policy defines which work may be rejected, degraded, delayed or shed. | Admission and priority policy has a defined owner; no implicit per-hop policy conflict. | Retries preserve operation identity and consume an explicit budget; shedding has visible consequence. | Backlog drain, retry release and recovery surge are capacity-bounded and observed. | Queue age/depth, utilization, demand, retry rate, deadlines, drop reasons and dependency saturation are visible.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Fragmented pools waste capacity; Static limits age poorly; Circuit state can oscillate or hide root cause
- **ANTI_CEREMONY_BOUNDARY:** A circuit-breaker library annotation is not containment.
- **POSSIBLE_CONFLICTING_PROPERTY:** P45: isolation machinery conflicts with resource efficiency and architectural simplicity.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which resources remain shared across supposed bulkheads?
  - Does fallback or circuit recovery overload the same dependency?

### P35 — Consistent distributed snapshot or checkpoint
- **DISTRIBUTED_FAILURE_MODE:** Components checkpoint at different times while messages and transactions continue.
- **MATURE_FORM:** Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **TRIGGER:** Recovery, migration, rescaling or audit requires a cross-component state cut.
- **CHEAP_PATH:** One local transactional snapshot or reconstructable stateless workers.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; TIMING_MODEL=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; NETWORK_ASSUMPTIONS=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; STORAGE_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; RECOVERY_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Recovery progress, gaps, validation, divergence and residual unknowns are visible.; CHEAP_PATH=One local transactional snapshot or reconstructable stateless workers.; MATURE_FORM=Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; MEMBERSHIP_LINK=Restored configuration, ownership generation and membership are current; old writers are fenced.; MATURE_FORM=Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replay/redelivery uses original identities and does not duplicate unclosed effects.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Restored configuration, ownership generation and membership are current; old writers are fenced.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **RECOVERY_PROFILE:** APPLICABILITY=PRIMARY; RECOVERY_STATE=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Snapshot identifies membership/configuration, state versions, channel/log positions and excluded external effects.
- **REQUIRED_PRECONDITIONS:** Declared channel/order assumptions, checkpoint metadata, atomic durable write, log position and compatible application state. | The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary. | Restored configuration, ownership generation and membership are current; old writers are fenced. | Replay/redelivery uses original identities and does not duplicate unclosed effects. | Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. | Recovery progress, gaps, validation, divergence and residual unknowns are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Snapshot consistency is model-specific; Large snapshots cost I/O/latency; Internal consistency does not guarantee external world consistency
- **ANTI_CEREMONY_BOUNDARY:** Having periodic snapshots is not a consistent recovery cut.
- **POSSIBLE_CONFLICTING_PROPERTY:** P36: internal snapshot consistency conflicts with external-world reconciliation burden.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can restored local checkpoints and in-flight messages form a state that never existed?
  - Which external effects are outside the snapshot?

### P36 — Replay and restore with external-state reconciliation
- **DISTRIBUTED_FAILURE_MODE:** Internal durable history and external systems fail/recover independently.
- **MATURE_FORM:** Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **TRIGGER:** Disaster restore, log replay, workflow history recovery or regional failover with external effects.
- **CHEAP_PATH:** All state and effects are inside one local transactional restore boundary.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; TIMING_MODEL=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; NETWORK_ASSUMPTIONS=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; STORAGE_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; RECOVERY_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Recovery progress, gaps, validation, divergence and residual unknowns are visible.; CHEAP_PATH=All state and effects are inside one local transactional restore boundary.; MATURE_FORM=Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; MEMBERSHIP_LINK=Restored configuration, ownership generation and membership are current; old writers are fenced.; MATURE_FORM=Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replay/redelivery uses original identities and does not duplicate unclosed effects.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Restored configuration, ownership generation and membership are current; old writers are fenced.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **RECOVERY_PROFILE:** APPLICABILITY=PRIMARY; RECOVERY_STATE=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible.
- **REQUIRED_PRECONDITIONS:** Complete logs, compatible code/schema, operation/effect identity, external query/ledger, authority fencing and manual residual path. | The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary. | Restored configuration, ownership generation and membership are current; old writers are fenced. | Replay/redelivery uses original identities and does not duplicate unclosed effects. | Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. | Recovery progress, gaps, validation, divergence and residual unknowns are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** External reconciliation can be manual and slow; Some effects are irreversible/unobservable; Logs may preserve bugs as well as facts
- **ANTI_CEREMONY_BOUNDARY:** 'Replay completed' is not externally consistent recovery.
- **POSSIBLE_CONFLICTING_PROPERTY:** P38: comprehensive reconciliation conflicts with recovery-time objectives.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - After replay, how are irreversible or third-party effects reconciled?
  - Can the same operation be replayed without duplicating its external effect?

### P37 — Failover re-establishes current authority before mutation
- **DISTRIBUTED_FAILURE_MODE:** Partition and false suspicion create simultaneous actors with incompatible state and authority.
- **MATURE_FORM:** Failover completes only after authority fencing, current-state selection and post-failover validation.
- **TRIGGER:** Leader/primary/site/region failover or ownership transfer after suspected failure.
- **CHEAP_PATH:** Manual offline recovery with verified old owner stopped, or one local process restart without concurrent actor.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; TIMING_MODEL=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; NETWORK_ASSUMPTIONS=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; STORAGE_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; RECOVERY_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Recovery progress, gaps, validation, divergence and residual unknowns are visible.; CHEAP_PATH=Manual offline recovery with verified old owner stopped, or one local process restart without concurrent actor.; MATURE_FORM=Failover completes only after authority fencing, current-state selection and post-failover validation.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; MEMBERSHIP_LINK=Restored configuration, ownership generation and membership are current; old writers are fenced.; MATURE_FORM=Failover completes only after authority fencing, current-state selection and post-failover validation.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Failover completes only after authority fencing, current-state selection and post-failover validation.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replay/redelivery uses original identities and does not duplicate unclosed effects.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Failover completes only after authority fencing, current-state selection and post-failover validation.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Restored configuration, ownership generation and membership are current; old writers are fenced.; GENERATION_OR_EPOCH=Failover issues a durable higher authority epoch.; STALE_REJECTION=All protected sinks and routing paths reject/avoid former authority.; MATURE_FORM=Failover completes only after authority fencing, current-state selection and post-failover validation.
- **RECOVERY_PROFILE:** APPLICABILITY=PRIMARY; RECOVERY_STATE=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; EXTERNAL_STATE_RECONCILIATION=Divergent accepted writes and external effects are reconciled before declaring completion.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Failover completes only after authority fencing, current-state selection and post-failover validation.
- **REQUIRED_PRECONDITIONS:** Authoritative config/quorum, current data version, fenced sinks, durable generation, client routing and reconciliation of divergent writes. | The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary. | Restored configuration, ownership generation and membership are current; old writers are fenced. | Replay/redelivery uses original identities and does not duplicate unclosed effects. | Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. | Recovery progress, gaps, validation, divergence and residual unknowns are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Conservative fencing delays availability; Determining most-current state can be expensive; Manual disaster actions can bypass controls
- **ANTI_CEREMONY_BOUNDARY:** 'Leader elected' or 'traffic switched' is not safe failover.
- **POSSIBLE_CONFLICTING_PROPERTY:** P13: fast failover conflicts with proving stale authority is fenced.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What prevents the former owner from writing after failover?
  - How is the promoted state shown to be current relative to accepted operations and membership?

### P38 — Tested restore and recovery-path evidence
- **DISTRIBUTED_FAILURE_MODE:** Recovery tooling, credentials, network, schemas, logs and capacity fail separately from the production data path.
- **MATURE_FORM:** Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **TRIGGER:** Any availability, durability, disaster recovery or rollback claim with material consequence.
- **CHEAP_PATH:** Low-consequence disposable state that can be regenerated and whose loss is explicitly accepted.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; TIMING_MODEL=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; NETWORK_ASSUMPTIONS=Process/storage crash, partition, inconsistent checkpoint, orphan message/work, log gap, corruption, stale failover authority and external-state divergence.; STORAGE_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; RECOVERY_ASSUMPTIONS=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Recovery progress, gaps, validation, divergence and residual unknowns are visible.; CHEAP_PATH=Low-consequence disposable state that can be regenerated and whose loss is explicitly accepted.; MATURE_FORM=Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Recovery point/time objectives are evidence-backed, not inferred from backup existence.; MEMBERSHIP_LINK=Restored configuration, ownership generation and membership are current; old writers are fenced.; MATURE_FORM=Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Replay/redelivery uses original identities and does not duplicate unclosed effects.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Restored configuration, ownership generation and membership are current; old writers are fenced.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **RECOVERY_PROFILE:** APPLICABILITY=PRIMARY; RECOVERY_STATE=Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Recovery evidence includes current artefact identity, measured RPO/RTO, authority fencing, external reconciliation and unresolved residuals.
- **REQUIRED_PRECONDITIONS:** Immutable backups/logs, independent access, compatible tooling, capacity, validation oracle, runbook and ownership. | The recovery line is internally consistent and reconciled with effects outside the log/transaction boundary. | Restored configuration, ownership generation and membership are current; old writers are fenced. | Replay/redelivery uses original identities and does not duplicate unclosed effects. | Snapshots, logs, backups, restore tooling, capacity and reconciliation are tested as a full path. | Recovery progress, gaps, validation, divergence and residual unknowns are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Rehearsals cost time and resources; Destructive tests need isolation; Passing one scenario does not cover all common modes
- **ANTI_CEREMONY_BOUNDARY:** A backup job marked successful is not a restore path.
- **POSSIBLE_CONFLICTING_PROPERTY:** P44: frequent realistic recovery tests conflict with cost/blast-radius limits.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - When was the exact current system last restored at realistic scale?
  - Did the test include replay, catch-up, authority, external reconciliation and return to service?

### P39 — Schema, wire protocol and event evolution under mixed versions
- **DISTRIBUTED_FAILURE_MODE:** Components observe incompatible schemas/protocols at different times and old events outlive the code that wrote them.
- **MATURE_FORM:** Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **TRIGGER:** Rolling deployment, long-lived event/log data, external clients, multiple regions or replayable workflow history.
- **CHEAP_PATH:** Atomic offline upgrade of one local process/store with no concurrent old reader/writer and acceptable downtime.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Mixed versions, incompatible wire/schema changes, stale configuration, control-plane/data-plane skew and rollback incompatibility.; TIMING_MODEL=Propagation is asynchronous; 'flag set' or 'deployment complete' is not proof every component observed it.; NETWORK_ASSUMPTIONS=Mixed versions, incompatible wire/schema changes, stale configuration, control-plane/data-plane skew and rollback incompatibility.; STORAGE_ASSUMPTIONS=Rollback and replay paths are compatible with new writes; downgrade limits are explicit.; RECOVERY_ASSUMPTIONS=Rollback and replay paths are compatible with new writes; downgrade limits are explicit.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Version distribution, configuration convergence and compatibility errors are visible.; CHEAP_PATH=Atomic offline upgrade of one local process/store with no concurrent old reader/writer and acceptable downtime.; MATURE_FORM=Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Propagation is asynchronous; 'flag set' or 'deployment complete' is not proof every component observed it.; MEMBERSHIP_LINK=Current configuration/version authority and staged rollout state are reconstructable.; MATURE_FORM=Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Readers/writers define compatibility across old/new schemas and replayed historical events.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Messages/events are versioned and unknown fields/semantics handled deliberately.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Current configuration/version authority and staged rollout state are reconstructable.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Rollback and replay paths are compatible with new writes; downgrade limits are explicit.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Every live old/new reader, writer, replica and history has a tested compatibility path or an explicit cutover barrier.
- **REQUIRED_PRECONDITIONS:** Version inventory, compatibility matrix, contract tests using real historical data, field semantics and rollback/downgrade policy. | Readers/writers define compatibility across old/new schemas and replayed historical events. | Current configuration/version authority and staged rollout state are reconstructable. | Messages/events are versioned and unknown fields/semantics handled deliberately. | Rollback and replay paths are compatible with new writes; downgrade limits are explicit. | Version distribution, configuration convergence and compatibility errors are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Compatibility layers accumulate debt; Additive change is not always possible; Syntactic compatibility can hide semantic incompatibility
- **ANTI_CEREMONY_BOUNDARY:** 'Rolling deployment succeeded' is not protocol compatibility.
- **POSSIBLE_CONFLICTING_PROPERTY:** P28: schema evolution conflicts with deterministic replay of long-lived histories.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can every old/new producer, consumer and stored event interoperate during rollout and rollback?
  - Does syntactic compatibility preserve field meaning and invariants?

### P40 — Configuration and control-plane/data-plane currentness
- **DISTRIBUTED_FAILURE_MODE:** Asynchronous propagation, partial failure and rollback create configuration skew and stale control decisions.
- **MATURE_FORM:** Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **TRIGGER:** Configuration affects routing, membership, schemas, resource limits, feature behaviour or authority across components.
- **CHEAP_PATH:** Local static configuration changed atomically with the single process.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Mixed versions, incompatible wire/schema changes, stale configuration, control-plane/data-plane skew and rollback incompatibility.; TIMING_MODEL=Propagation is asynchronous; 'flag set' or 'deployment complete' is not proof every component observed it.; NETWORK_ASSUMPTIONS=Mixed versions, incompatible wire/schema changes, stale configuration, control-plane/data-plane skew and rollback incompatibility.; STORAGE_ASSUMPTIONS=Rollback and replay paths are compatible with new writes; downgrade limits are explicit.; RECOVERY_ASSUMPTIONS=Rollback and replay paths are compatible with new writes; downgrade limits are explicit.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Version distribution, configuration convergence and compatibility errors are visible.; CHEAP_PATH=Local static configuration changed atomically with the single process.; MATURE_FORM=Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Propagation is asynchronous; 'flag set' or 'deployment complete' is not proof every component observed it.; MEMBERSHIP_LINK=Current configuration/version authority and staged rollout state are reconstructable.; MATURE_FORM=Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Readers/writers define compatibility across old/new schemas and replayed historical events.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Messages/events are versioned and unknown fields/semantics handled deliberately.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=PRIMARY; AUTHORITY_SOURCE=Current configuration/version authority and staged rollout state are reconstructable.; GENERATION_OR_EPOCH=Monotone configuration generation with source provenance.; STALE_REJECTION=Data plane rejects obsolete incompatible authority/configuration where required.; MATURE_FORM=Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Rollback and replay paths are compatible with new writes; downgrade limits are explicit.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Configuration change completes only when intended population/version is established, incompatible nodes are handled and rollback remains valid.
- **REQUIRED_PRECONDITIONS:** Authoritative source, config version/provenance, validation, propagation topology, compatibility, rollback and independent emergency access. | Readers/writers define compatibility across old/new schemas and replayed historical events. | Current configuration/version authority and staged rollout state are reconstructable. | Messages/events are versioned and unknown fields/semantics handled deliberately. | Rollback and replay paths are compatible with new writes; downgrade limits are explicit. | Version distribution, configuration convergence and compatibility errors are visible.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Staged rollout slows change; Canaries may not represent global edge cases; More control logic is itself a failure source
- **ANTI_CEREMONY_BOUNDARY:** 'The feature flag is set' is not evidence every replica observed it.
- **POSSIBLE_CONFLICTING_PROPERTY:** P45: global control-plane machinery conflicts with local static configuration.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What is the authoritative configuration generation, and which components have actually applied it?
  - Can rollback or emergency control work if the normal control plane is impaired?

### P41 — Current dependency topology and end-to-end readiness
- **DISTRIBUTED_FAILURE_MODE:** Dependencies fail independently and topology changes dynamically; local checks cover only one process.
- **MATURE_FORM:** Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **TRIGGER:** Service depends on remote components or dynamic routing/ownership.
- **CHEAP_PATH:** Standalone local process with no remote effect path, where process liveness is the whole service.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects.; TIMING_MODEL=Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown.; NETWORK_ASSUMPTIONS=Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects.; STORAGE_ASSUMPTIONS=Evidence survives or is intentionally preserved through failure and recovery.; RECOVERY_ASSUMPTIONS=Evidence survives or is intentionally preserved through failure and recovery.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Coverage, sampling, missingness and uncertainty are first-class data.; CHEAP_PATH=Standalone local process with no remote effect path, where process liveness is the whole service.; MATURE_FORM=Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown.; MEMBERSHIP_LINK=Source identity, configuration and topology provenance accompany observations.; MATURE_FORM=Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Telemetry consistency does not imply application-state consistency.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Trace context/correlation may be dropped, duplicated or sampled.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Source identity, configuration and topology provenance accompany observations.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Evidence survives or is intentionally preserved through failure and recovery.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Readiness states the exact effect path and evidence age; green does not imply every dependency or operation is healthy.
- **REQUIRED_PRECONDITIONS:** Current topology, dependency contracts, credentials/routing, representative probes, consequence-safe synthetic operations and freshness bounds. | Telemetry consistency does not imply application-state consistency. | Source identity, configuration and topology provenance accompany observations. | Trace context/correlation may be dropped, duplicated or sampled. | Evidence survives or is intentionally preserved through failure and recovery. | Coverage, sampling, missingness and uncertainty are first-class data.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** End-to-end probes cost capacity and can mutate data; No finite probe covers all paths; Dependency awareness can create tight coupling
- **ANTI_CEREMONY_BOUNDARY:** A `/health` 200 response is not service readiness.
- **POSSIBLE_CONFLICTING_PROPERTY:** P42: exhaustive end-to-end readiness conflicts with probe cost and observer effect.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Does health test the actual dependency/effect path and current authority?
  - Can an instance be alive yet unable to perform the operation for which traffic is routed to it?

### P42 — Distributed observability treated as partial, sampled evidence
- **DISTRIBUTED_FAILURE_MODE:** Telemetry pipelines fail, sample, reorder and lag independently from the system observed.
- **MATURE_FORM:** Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **TRIGGER:** Diagnosis, currentness, completion, failure-model validation or causal reconstruction depends on distributed telemetry.
- **CHEAP_PATH:** Local deterministic operation with direct authoritative state inspection.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects.; TIMING_MODEL=Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown.; NETWORK_ASSUMPTIONS=Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects.; STORAGE_ASSUMPTIONS=Evidence survives or is intentionally preserved through failure and recovery.; RECOVERY_ASSUMPTIONS=Evidence survives or is intentionally preserved through failure and recovery.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Coverage, sampling, missingness and uncertainty are first-class data.; CHEAP_PATH=Local deterministic operation with direct authoritative state inspection.; MATURE_FORM=Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown.; MEMBERSHIP_LINK=Source identity, configuration and topology provenance accompany observations.; MATURE_FORM=Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Telemetry consistency does not imply application-state consistency.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Trace context/correlation may be dropped, duplicated or sampled.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Source identity, configuration and topology provenance accompany observations.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Evidence survives or is intentionally preserved through failure and recovery.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Every inference states evidence source, coverage, freshness and missingness; authoritative state queries are used where available.
- **REQUIRED_PRECONDITIONS:** Trace-context propagation, source identity, clock/ingestion bounds, sampling design, retention, privacy/security and telemetry-outage handling. | Telemetry consistency does not imply application-state consistency. | Source identity, configuration and topology provenance accompany observations. | Trace context/correlation may be dropped, duplicated or sampled. | Evidence survives or is intentionally preserved through failure and recovery. | Coverage, sampling, missingness and uncertainty are first-class data.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=VERY_HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=VERY_HIGH; INDUSTRIAL_PRACTICE_STRENGTH=VERY_HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Full capture is expensive and privacy-sensitive; Instrumentation changes timing; Sampling strategies bias evidence
- **ANTI_CEREMONY_BOUNDARY:** A trace that looks complete is not a complete causal history.
- **POSSIBLE_CONFLICTING_PROPERTY:** P43: aggressive sampling conflicts with causal reconstruction.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What sampling, missingness and telemetry delay bound each inference?
  - Could the failure path be precisely the path not instrumented or retained?

### P43 — Causal trace reconstruction and event provenance
- **DISTRIBUTED_FAILURE_MODE:** Events are reordered, sampled and emitted by processes with skewed clocks and changing topology.
- **MATURE_FORM:** Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **TRIGGER:** Debugging, audit, recovery or completion requires cross-component reconstruction.
- **CHEAP_PATH:** One local process with deterministic logs and no remote effects.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects.; TIMING_MODEL=Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown.; NETWORK_ASSUMPTIONS=Missing spans/logs, sampling bias, clock skew, telemetry delay/outage, cardinality loss, stale topology and observer effects.; STORAGE_ASSUMPTIONS=Evidence survives or is intentionally preserved through failure and recovery.; RECOVERY_ASSUMPTIONS=Evidence survives or is intentionally preserved through failure and recovery.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Coverage, sampling, missingness and uncertainty are first-class data.; CHEAP_PATH=One local process with deterministic logs and no remote effects.; MATURE_FORM=Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Telemetry has acquisition/ingestion delay and clock uncertainty; currentness is bounded or marked unknown.; MEMBERSHIP_LINK=Source identity, configuration and topology provenance accompany observations.; MATURE_FORM=Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Telemetry consistency does not imply application-state consistency.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Trace context/correlation may be dropped, duplicated or sampled.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Source identity, configuration and topology provenance accompany observations.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=Evidence survives or is intentionally preserved through failure and recovery.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Reconstruction distinguishes known causal edges, concurrent events, inferred links and missing evidence.
- **REQUIRED_PRECONDITIONS:** Stable identity, context propagation, causal model, clock uncertainty, sampling metadata, source provenance and retention. | Telemetry consistency does not imply application-state consistency. | Source identity, configuration and topology provenance accompany observations. | Trace context/correlation may be dropped, duplicated or sampled. | Evidence survives or is intentionally preserved through failure and recovery. | Coverage, sampling, missingness and uncertainty are first-class data.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Trace context can leak data; High cardinality/cost; Causal provenance cannot include unobserved physical events automatically
- **ANTI_CEREMONY_BOUNDARY:** Correlation IDs plus sorted timestamps are not causal proof.
- **POSSIBLE_CONFLICTING_PROPERTY:** P42: rich provenance conflicts with privacy, cardinality and overhead.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Can retries, rebalances, authority changes and external effects be linked causally rather than only by time?
  - Where are trace gaps or inferred—not observed—edges recorded?

### P44 — Hypothesis-bound fault injection and recovery challenge
- **DISTRIBUTED_FAILURE_MODE:** Real distributed failures depend on timing, topology, load, persistence and recovery interaction that unit tests miss.
- **MATURE_FORM:** A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **TRIGGER:** Material claim about tolerance, failover, retry, restore, overload or state integrity whose assumptions can be safely challenged.
- **CHEAP_PATH:** Static analysis/model checking/unit/integration test when the claim does not require distributed runtime failure; low-consequence system with no material uncertainty.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Unexercised failure assumptions, non-representative injections, uncontrolled blast radius, missing observability and untested recovery.; TIMING_MODEL=Injection timing/order and stop conditions are part of the experiment.; NETWORK_ASSUMPTIONS=Unexercised failure assumptions, non-representative injections, uncontrolled blast radius, missing observability and untested recovery.; STORAGE_ASSUMPTIONS=The experiment tests recovery and post-recovery reconciliation, not merely failure onset.; RECOVERY_ASSUMPTIONS=The experiment tests recovery and post-recovery reconciliation, not merely failure onset.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Predeclared evidence and abort conditions must be available.; CHEAP_PATH=Static analysis/model checking/unit/integration test when the claim does not require distributed runtime failure; low-consequence system with no material uncertainty.; MATURE_FORM=A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Injection timing/order and stop conditions are part of the experiment.; MEMBERSHIP_LINK=Experiment authority, scope and rollback are bounded.; MATURE_FORM=A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=The tested invariant/postcondition is explicit; steady-state proxy alone is insufficient.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Injected faults include loss, delay, duplicate/reorder where relevant.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Experiment authority, scope and rollback are bounded.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=The experiment tests recovery and post-recovery reconciliation, not merely failure onset.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action.
- **REQUIRED_PRECONDITIONS:** Representative environment/configuration, observability, rollback, safety authority, current topology, consequence assessment and independent expected result. | The tested invariant/postcondition is explicit; steady-state proxy alone is insufficient. | Experiment authority, scope and rollback are bounded. | Injected faults include loss, delay, duplicate/reorder where relevant. | The experiment tests recovery and post-recovery reconciliation, not merely failure onset. | Predeclared evidence and abort conditions must be available.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Production experiments carry risk; Staging may not reproduce common modes; Evidence for broad effectiveness remains heterogeneous
- **ANTI_CEREMONY_BOUNDARY:** 'Run chaos experiments' is not a general property.
- **POSSIBLE_CONFLICTING_PROPERTY:** P38: production-representative fault injection conflicts with blast-radius control.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What exact failure/recovery claim does the experiment challenge?
  - Does it test the current configuration, load, external effects and post-recovery reconciliation?

### P45 — Distribution requires a named consumer and retains a cheap local path
- **DISTRIBUTED_FAILURE_MODE:** Every unnecessary boundary adds delay, unknown outcomes, version skew, partial failure, observability and recovery state.
- **MATURE_FORM:** Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **TRIGGER:** Independent scaling, fault containment, geographic latency, ownership/autonomy or deployment lifecycle demonstrably outweighs coordination cost.
- **CHEAP_PATH:** Co-locate code/state, use in-process calls and local transactions, or one durable owner.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer.; TIMING_MODEL=No general timing model; the claim fails because a named artefact is substituted for an engineering property.; NETWORK_ASSUMPTIONS=Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer.; STORAGE_ASSUMPTIONS=No recovery evidence follows from having a component installed.; RECOVERY_ASSUMPTIONS=No recovery evidence follows from having a component installed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Dashboards and green checks are proxies unless tied to a claim.; CHEAP_PATH=Co-locate code/state, use in-process calls and local transactions, or one durable owner.; MATURE_FORM=Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=No general timing model; the claim fails because a named artefact is substituted for an engineering property.; MEMBERSHIP_LINK=No authority follows from deployment labels alone.; MATURE_FORM=Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=No guarantee follows from branding alone.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=No delivery/effect semantics follow from tooling labels alone.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=No authority follows from deployment labels alone.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=No recovery evidence follows from having a component installed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Every remote boundary names the property it buys, the assumptions it creates and the condition for collapsing it.
- **REQUIRED_PRECONDITIONS:** Workload/consequence evidence, ownership model, availability/latency target and explicit cost/complexity comparison. | No guarantee follows from branding alone. | No authority follows from deployment labels alone. | No delivery/effect semantics follow from tooling labels alone. | No recovery evidence follows from having a component installed. | Dashboards and green checks are proxies unless tied to a claim.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=MEDIUM; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=MEDIUM; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Needs can change; Local design may create migration cost; No universal threshold separates local from distributed
- **ANTI_CEREMONY_BOUNDARY:** Microservices, queues, service mesh or consensus are not maturity indicators.
- **POSSIBLE_CONFLICTING_PROPERTY:** P03/P15/P25: local simplicity conflicts with real independence, invariant or durable-workflow consumers.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What concrete scale, latency, autonomy, lifecycle or failure-independence consumer justifies each remote boundary?
  - Could the same invariant or workflow be local without losing that consumer?

### P46 — Retire distributed machinery when its coordination consumer disappears
- **DISTRIBUTED_FAILURE_MODE:** Obsolete machinery continues generating partial failure, upgrade, recovery and observability burden.
- **MATURE_FORM:** Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **TRIGGER:** Mechanism has no current decision, invariant, workload or failure-domain consumer.
- **CHEAP_PATH:** Keep mechanism only when removal would reintroduce a demonstrated failure or violate a current requirement.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer.; TIMING_MODEL=No general timing model; the claim fails because a named artefact is substituted for an engineering property.; NETWORK_ASSUMPTIONS=Ceremonial architecture can introduce partial failure, coordination debt and unowned recovery without a protected consumer.; STORAGE_ASSUMPTIONS=No recovery evidence follows from having a component installed.; RECOVERY_ASSUMPTIONS=No recovery evidence follows from having a component installed.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Dashboards and green checks are proxies unless tied to a claim.; CHEAP_PATH=Keep mechanism only when removal would reintroduce a demonstrated failure or violate a current requirement.; MATURE_FORM=Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=No general timing model; the claim fails because a named artefact is substituted for an engineering property.; MEMBERSHIP_LINK=No authority follows from deployment labels alone.; MATURE_FORM=Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=No guarantee follows from branding alone.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=No delivery/effect semantics follow from tooling labels alone.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=No authority follows from deployment labels alone.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=No recovery evidence follows from having a component installed.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Each distributed mechanism has entry, operation and exit criteria; decommission preserves state and effect semantics.
- **REQUIRED_PRECONDITIONS:** Usage/dependency inventory, migration/replay plan, retained data/identity semantics and safe decommission evidence. | No guarantee follows from branding alone. | No authority follows from deployment labels alone. | No delivery/effect semantics follow from tooling labels alone. | No recovery evidence follows from having a component installed. | Dashboards and green checks are proxies unless tied to a claim.
- **EVIDENCE_STRENGTH:** `HIGH`; HISTORICAL_PROVENANCE_STRENGTH=HIGH; FORMAL_OR_THEORETICAL_STRENGTH=LOW; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=MEDIUM; OUTAGE_OR_FAILURE_CASE_STRENGTH=MEDIUM; INDUSTRIAL_PRACTICE_STRENGTH=MEDIUM; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=MEDIUM; TRANSFERABILITY_STRENGTH=HIGH; ASSUMPTION_SENSITIVITY=HIGH; CONTRARY_EVIDENCE_STRENGTH=MEDIUM
- **CRITICISMS:** Retirement itself is risky; Latent future need may return; Benefits are hard to quantify before removal
- **ANTI_CEREMONY_BOUNDARY:** 'Standard platform component' is not a permanent justification.
- **POSSIBLE_CONFLICTING_PROPERTY:** P39: retirement conflicts with old history/schema clients that still require compatibility.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which current invariant or consumer still requires this mechanism?
  - Can it be drained and collapsed without losing replay, authority, identity or recovery evidence?

### P52 — Byzantine/adversarial fault tolerance only under an explicit adversarial model
- **DISTRIBUTED_FAILURE_MODE:** Participants can send conflicting, malformed or strategically adversarial messages rather than merely stop.
- **MATURE_FORM:** BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **TRIGGER:** Actual threat model includes mutually distrustful or compromise-prone participants and the cost is justified.
- **CHEAP_PATH:** Crash-fault consensus, single authority, audited replication or simpler integrity checks when adversarial participants are not a credible failure.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Domain-specific crash, omission, arbitrary/value, model, scheduling and external-service failures.; TIMING_MODEL=Domain workload and latency model must be stated.; NETWORK_ASSUMPTIONS=Domain-specific crash, omission, arbitrary/value, model, scheduling and external-service failures.; STORAGE_ASSUMPTIONS=State/context, tool effects and human escalation are durable and reconcilable.; RECOVERY_ASSUMPTIONS=State/context, tool effects and human escalation are durable and reconcilable.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Prompt/model/tool version, causal provenance and validation evidence are captured within privacy/security limits.; CHEAP_PATH=Crash-fault consensus, single authority, audited replication or simpler integrity checks when adversarial participants are not a credible failure.; MATURE_FORM=BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Domain workload and latency model must be stated.; MEMBERSHIP_LINK=Agent/service/model/tool authority and version are explicit.; MATURE_FORM=BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Domain semantic validity remains separate from replicated agreement or durable execution.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Calls can be duplicated, omitted, delayed or return malformed/semantically invalid values.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Agent/service/model/tool authority and version are explicit.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=State/context, tool effects and human escalation are durable and reconcilable.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=BFT is selected only after a concrete adversarial model and independent identity/failure-domain argument; crash/common-mode controls remain separate.
- **REQUIRED_PRECONDITIONS:** Adversary/corruption model, authentication, identity/key lifecycle, independence, quorum threshold, denial-of-service/liveness assumptions and implementation assurance. | Domain semantic validity remains separate from replicated agreement or durable execution. | Agent/service/model/tool authority and version are explicit. | Calls can be duplicated, omitted, delayed or return malformed/semantically invalid values. | State/context, tool effects and human escalation are durable and reconcilable. | Prompt/model/tool version, causal provenance and validation evidence are captured within privacy/security limits.
- **EVIDENCE_STRENGTH:** `VERY_HIGH`; HISTORICAL_PROVENANCE_STRENGTH=VERY_HIGH; FORMAL_OR_THEORETICAL_STRENGTH=VERY_HIGH; MODEL_CHECKED_OR_PROVED_STRENGTH=MEDIUM; EMPIRICAL_SYSTEMS_STRENGTH=HIGH; OUTAGE_OR_FAILURE_CASE_STRENGTH=HIGH; INDUSTRIAL_PRACTICE_STRENGTH=HIGH; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=HIGH; TRANSFERABILITY_STRENGTH=VERY_HIGH; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** High cost/latency/complexity; Often misapplied to ordinary common-mode failures; Formal protocol does not secure implementation or operations
- **ANTI_CEREMONY_BOUNDARY:** 'Byzantine' is not a synonym for severe outage.
- **POSSIBLE_CONFLICTING_PROPERTY:** P01/P45: BFT cost conflicts with simpler crash/common-mode model when adversary is absent.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - What actor can behave arbitrarily, how many may collude, and which identities/failure domains are independent?
  - Would crash-fault consensus plus common-mode controls address the actual problem more directly?

### P53 — Distributed AI and agentic systems as a bounded domain translation
- **DISTRIBUTED_FAILURE_MODE:** Agents, models, retrieval stores and tools can omit, duplicate, delay, hallucinate or semantically conflict while external effects persist.
- **MATURE_FORM:** Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **TRIGGER:** Autonomous or multi-agent system coordinates persistent work or external effects across independently failing services.
- **CHEAP_PATH:** One model call with human review and no durable/external effect; deterministic local program where suitable.
- **DISTRIBUTED_FAILURE_MODEL_PROFILE:** FAILURE_MODEL=Domain-specific crash, omission, arbitrary/value, model, scheduling and external-service failures.; TIMING_MODEL=Domain workload and latency model must be stated.; NETWORK_ASSUMPTIONS=Domain-specific crash, omission, arbitrary/value, model, scheduling and external-service failures.; STORAGE_ASSUMPTIONS=State/context, tool effects and human escalation are durable and reconcilable.; RECOVERY_ASSUMPTIONS=State/context, tool effects and human escalation are durable and reconcilable.; COMMON_MODE_ASSUMPTIONS=Shared software, configuration, control plane, credentials, operator and infrastructure are considered where relevant.; OBSERVABILITY=Prompt/model/tool version, causal provenance and validation evidence are captured within privacy/security limits.; CHEAP_PATH=One model call with human review and no durable/external effect; deterministic local program where suitable.; MATURE_FORM=Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **CAUSALITY_CURRENTNESS_PROFILE:** APPLICABILITY=SUPPORTING; ORDER_OR_CURRENTNESS_REQUIREMENT=Order/freshness semantics are named where the property depends on them; otherwise not promoted from timestamps or logs.; CLOCK_ASSUMPTION=Domain workload and latency model must be stated.; MEMBERSHIP_LINK=Agent/service/model/tool authority and version are explicit.; MATURE_FORM=Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **REPLICATION_CONSISTENCY_PROFILE:** APPLICABILITY=SUPPORTING; CONSISTENCY_MODEL=Domain semantic validity remains separate from replicated agreement or durable execution.; REPLICA_OR_STATE_BOUNDARY=The state and operation boundary covered by the claim is explicit.; SEMANTIC_VALIDITY=Convergence/agreement is not substituted for application semantic validity.; MATURE_FORM=Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **DELIVERY_IDEMPOTENCY_PROFILE:** APPLICABILITY=SUPPORTING; DELIVERY_MODEL=Calls can be duplicated, omitted, delayed or return malformed/semantically invalid values.; IDENTITY_SCOPE=Transport attempt, operation and external effect identities are distinguished when retries/replay can occur.; ACK_BOUNDARY=An acknowledgement proves only the declared durable boundary.; MATURE_FORM=Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **AUTHORITY_FENCING_PROFILE:** APPLICABILITY=SUPPORTING; AUTHORITY_SOURCE=Agent/service/model/tool authority and version are explicit.; GENERATION_OR_EPOCH=Current term/view/epoch/generation where stale actors can survive.; STALE_REJECTION=Protected resource rejects stale authority where correctness depends on exclusivity.; MATURE_FORM=Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **RECOVERY_PROFILE:** APPLICABILITY=SUPPORTING; RECOVERY_STATE=State/context, tool effects and human escalation are durable and reconcilable.; EXTERNAL_STATE_RECONCILIATION=Effects outside the recovered log/transaction boundary are independently reconciled.; VALIDATION=Recovered authority, data and postconditions are validated before normal service.; MATURE_FORM=Provisional: agentic execution is governed as a durable distributed workflow, but probabilistic semantic validity is not promoted to a solved systems property.
- **REQUIRED_PRECONDITIONS:** Agent/task identity, model/prompt/tool versions, validator authority, external effect closure, human escalation and privacy/security constraints. | Domain semantic validity remains separate from replicated agreement or durable execution. | Agent/service/model/tool authority and version are explicit. | Calls can be duplicated, omitted, delayed or return malformed/semantically invalid values. | State/context, tool effects and human escalation are durable and reconcilable. | Prompt/model/tool version, causal provenance and validation evidence are captured within privacy/security limits.
- **EVIDENCE_STRENGTH:** `LOW`; HISTORICAL_PROVENANCE_STRENGTH=LOW; FORMAL_OR_THEORETICAL_STRENGTH=LOW; MODEL_CHECKED_OR_PROVED_STRENGTH=LOW; EMPIRICAL_SYSTEMS_STRENGTH=LOW; OUTAGE_OR_FAILURE_CASE_STRENGTH=LOW; INDUSTRIAL_PRACTICE_STRENGTH=LOW; MULTI_IMPLEMENTATION_REPLICATION_STRENGTH=MEDIUM; TRANSFERABILITY_STRENGTH=LOW; ASSUMPTION_SENSITIVITY=VERY_HIGH; CONTRARY_EVIDENCE_STRENGTH=HIGH
- **CRITICISMS:** Evidence is very recent and mostly prototypes/preprints; Anthropomorphic 'agent' framing can obscure ordinary workflow design; Semantic correctness lacks stable oracle
- **ANTI_CEREMONY_BOUNDARY:** 'Multi-agent' does not imply distributed-systems maturity.
- **POSSIBLE_CONFLICTING_PROPERTY:** P27/P42: autonomous completion conflicts with weak semantic oracle and incomplete observability.
- **QUESTIONS_FOR_REPOSITORY_AUDIT:**
  - Which agent/tool effects can duplicate or remain unknown after retry?
  - What validates semantic correctness independently of the agent reporting success?
  - Can model/prompt/context versions reproduce or explain an action?

## CEREMONIES_TO_NOT_BLINDLY_ADOPT

- Consensus cluster
- Distributed lock
- Message broker
- Event log / event sourcing
- Microservices
- Service mesh
- Workflow engine
- Exactly-once setting
- Three replicas / multi-AZ
- Leader election
- Health endpoint
- Chaos experiment / game day
- Circuit breaker
- Global transaction
- Global timestamp / LWW
- Multi-region active-active

## CONTEXTS_WHERE_PROPERTY_SHOULD_NOT_TRIGGER

- Purely local operations whose full state/effect boundary is one process or local transaction.
- Immutable/read-only data where stale or repeated reads are harmless and declared.
- Low-consequence disposable state that can be regenerated and has no recovery consumer.
- Commutative or invariant-confluent operations for which global coordination protects no invariant.
- Operations whose deadline has expired, whose error is permanent, or whose retry cannot be made safe.
- Small systems where a distributed mechanism adds more failure and lifecycle surface than the availability/scale/autonomy benefit.
- Adversarial/BFT machinery where crash, corruption and common-mode failure—not mutually distrustful participants—are the actual model.
- Chaos/fault injection where a cheaper static, unit, model or integration test closes the evidence burden.
- Multi-region active-active when one active owner plus tested failover satisfies the consequence.
- Long-lived workflow machinery for a single short local transaction or synchronous computation.

## PROPERTIES_REQUIRING_EXPLICIT_FAILURE_MODEL

- P01
- P02
- P03
- P05
- P06
- P09
- P10
- P11
- P12
- P13
- P15
- P17
- P20
- P23
- P25
- P26
- P29
- P32
- P33
- P35
- P36
- P37
- P38
- P40
- P44
- P52
- P53

## PROPERTIES_REQUIRING_MEMBERSHIP_OR_AUTHORITY_IDENTITY

- P03
- P05
- P06
- P09
- P10
- P11
- P12
- P13
- P15
- P23
- P26
- P35
- P37
- P40
- P41
- P52
- P53

## PROPERTIES_REQUIRING_IDEMPOTENCY_OR_COMPENSATION

- P02
- P17
- P18
- P19
- P20
- P21
- P22
- P23
- P24
- P25
- P26
- P27
- P32
- P36
- P37
- P53

## PROPERTIES_REQUIRING_BACKPRESSURE_OR_CAPACITY_MODEL

- P09
- P17
- P22
- P25
- P29
- P30
- P31
- P32
- P33
- P34
- P37
- P38
- P44
- P53

## PROPERTIES_REQUIRING_DISTRIBUTED_RECOVERY_EVIDENCE

- P01
- P02
- P03
- P09
- P10
- P11
- P12
- P13
- P17
- P20
- P22
- P23
- P24
- P25
- P26
- P27
- P28
- P33
- P35
- P36
- P37
- P38
- P39
- P40
- P41
- P44
- P52
- P53

## PROPERTIES_WITH_STRONG_FORMAL_BUT_WEAK_OPERATIONAL_TRANSFER

- P05
- P08
- P10
- P11
- P12
- P16
- P23
- P52

## PROPERTIES_WITH_STRONG_OUTAGE_OR_FIELD_SUPPORT

- P02
- P03
- P06
- P09
- P13
- P17
- P19
- P29
- P30
- P31
- P32
- P33
- P35
- P36
- P37
- P38
- P39
- P40
- P41
- P42
- P44

## PROPERTIES_WITH_MIXED_OR_WEAK_SUPPORT

- P14
- P16
- P18
- P22
- P24
- P34
- P42
- P43
- P46
- P53

## UNRESOLVED_PROPERTIES

- **P53** is formally `UNRESOLVED`: agentic/distributed-AI systems appear to inherit durable-workflow, retry, provenance and effect-boundary obligations, but independent field evidence and a stable semantic-validity oracle are not established.
- Every property's `OPEN_QUESTIONS` remains an evidence burden even where the property itself is retained.

## EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_PUBLIC_DOCUMENTATION_INTAKE

## Source-grounded explanation

Distributed-systems engineering developed through several lineages rather than one cloud-native method. Early networked/message-passing work made remote communication and uncertain acknowledgement explicit; Lamport's causal-order work, snapshot algorithms, agreement/impossibility results, transaction and recovery theory, quorum replication, group membership, durable logs and database consistency each solved different problems. Later production systems and research—Dynamo/Spanner-style databases, causal/CRDT systems, stream processors, durable workflows, overload control, tracing and fault injection—translated and hybridised those lineages rather than replacing them. [S001]–[S019], [S025], [S030], [S036]–[S055], [S061]–[S090].

The evidence supports `EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING` as an analytical description of engineering that begins with partial failure and uncertain timing; makes causal order, consistency, membership, authority, delivery and recovery contracts explicit; binds retries, re-dispatch and failover to semantic identity, fencing, idempotency or compensation; controls finite capacity and positive feedback; and treats durable state, telemetry and replication as boundary-scoped evidence rather than automatic global truth. It also retains a strong cheap-path rule: do not distribute state or work unless an actual availability, latency, scale, ownership or lifecycle consumer warrants the additional failure surface.

## Strongest surviving engineering properties

| ID | Property | Mature public form | Core sources |
| --- | --- | --- | --- |
| P01 | Explicit distributed failure, timing, network, storage and recovery model | An assumption contract travels with each guarantee, test and recovery path, and names the local cheap path. | [S005], [S006], [S007], [S008], [S034], [S071], [S088], [S091] |
| P02 | Partial failure and unknown-outcome semantics | Timeout/no response yields UNKNOWN until authoritative postcondition, idempotent closure or compensation resolves it. | [S008], [S043], [S044], [S061], [S067] |
| P04 | Causal order distinguished from wall-clock and arbitrary total order | Choose the weakest order that protects the consumer; name causal, sequencer/log, commit, event-time and observation-time separately. | [S003], [S013], [S031], [S032], [S033], [S047] |
| P06 | Currentness, freshness and session guarantees as explicit evidence | A read carries enough version/configuration evidence for its consumer, or is explicitly stale/unknown. | [S021], [S029], [S031], [S036], [S037] |
| P07 | Consistency level and isolation as an operation-scoped contract | Each operation states required history semantics, protected invariant and failure response; stronger coordination is localised. | [S020], [S021], [S022], [S023], [S024], [S025], [S027], [S029], [S031], [S039] |
| P10 | Quorum validity bound to current membership and configuration | A quorum certificate identifies current configuration, epoch and state position. | [S011], [S012], [S014], [S015], [S036], [S094] |
| P11 | Consensus safety separated from liveness and semantic validity | Use consensus only for a named invariant; preserve safety during lost progress; validate values and deployment assumptions separately. | [S006], [S007], [S008], [S009], [S010], [S011], [S012] |
| P13 | Current mutation authority enforced by epochs or fencing | Authority evidence travels to every effect boundary; stale attempts are rejected or semantically neutralised. | [S010], [S012], [S035], [S070], [S094] |
| P15 | Strong coordination for non-confluent invariants | Demonstrate non-confluence, then coordinate the smallest state/effect closure or redesign the operation. | [S017], [S020], [S023], [S025], [S036], [S038], [S040], [S041], [S042] |
| P17 | Duplicate-aware delivery semantics | Name semantics at every boundary and independently close the business-effect boundary. | [S043], [S044], [S045], [S046], [S047], [S049] |
| P19 | Semantic idempotency, not request-ID ritual | The same operation identity and parameters cannot create more than the allowed semantic effect across retry/restart/replay. | [S044], [S050], [S058], [S067], [S069] |
| P27 | Completion defined by durable state plus verified postcondition | DONE identifies the evidence and boundary establishing the required effect; otherwise state remains PARTIAL or UNKNOWN. | [S043], [S050], [S054], [S055], [S092] |
| P32 | Retry budgets, exponential backoff, jitter and deadline propagation | A retry is admitted like new work, consumes one end-to-end budget and carries the same operation identity. | [S061], [S063], [S066], [S067], [S068], [S069] |
| P36 | Replay and restore with external-state reconciliation | Recovery closes or explicitly enumerates every state/effect boundary and preserves UNKNOWN where closure is impossible. | [S017], [S046], [S048], [S050], [S053], [S056], [S071] |
| P44 | Hypothesis-bound fault injection and recovery challenge | A bounded experiment challenges one explicit claim and its recovery path; pass/fail changes evidence or action. | [S084], [S085], [S086], [S087], [S088], [S089], [S090], [S091] |

## Common caricatures and ceremonies to reject

- **CAP means choose any two of consistency, availability and partition tolerance.** The formal result is a partition/asynchrony impossibility for specific definitions; normal-operation latency/consistency and partition-recovery choices remain design decisions.
- **Exactly-once delivery means a business action happens exactly once.** Exactly-once claims are scoped to a transaction/runtime boundary; arbitrary external effects require identity, idempotency, participation, fencing or compensation.
- **Retries are harmless.** Retries consume capacity, can race an unknown original, duplicate effects and create metastable overload; they require semantic safety, budget, backoff, jitter and deadline.
- **An ACK means the intended effect occurred.** An acknowledgement proves only its declared durable boundary; downstream and real-world postconditions remain separate.
- **A distributed lock makes concurrent work safe.** A delayed former holder may still act. Correctness-critical mutation needs resource-enforced fencing/version authority or semantic duplicate protection.
- **Majority quorum means the state is automatically current.** Quorum is configuration-, term- and state-position-specific; it also does not establish semantic validity or independent failure domains.
- **A timestamp gives the true order.** Wall-clock time can be skewed and does not establish causal or semantic order; bounded-time designs must state uncertainty.
- **Eventual consistency means the system will eventually be correct.** It may guarantee convergence under assumptions, not a convergence deadline or semantic validity of the converged state.
- **Microservices automatically improve resilience.** They can create useful ownership and fault boundaries, but also add remote uncertainty, distributed invariants and coordination debt.
- **If a service is healthy, its dependencies are healthy.** Process liveness is not end-to-end readiness, current authority, capacity or an effect-path check.

## Important criticisms and limits

- Formal guarantees are model-dependent; membership, durable storage, clocks, implementation and external effects can violate the proof boundary.
- Strong consistency and coordination protect specific invariants but cost latency/availability and can be overapplied.
- Weaker/mergeable designs preserve availability only when application semantics satisfy their convergence/invariant assumptions.
- Retries and failover can create duplicates, stale authority and overload; they are not unqualified reliability improvements.
- Compensation is usually a new balancing action, not restoration of the historical state.
- Durable execution preserves orchestration state, not necessarily current external-world truth.
- Replication and backups can share corruption/configuration/control-plane faults; restore evidence is separate.
- Tracing and health telemetry are sampled, delayed and incomplete and can fail during the incident.
- Chaos engineering evidence is heterogeneous and can become ritual unless linked to a hypothesis and decision.
- Architecture-shape evidence, especially microservices and emerging agentic systems, is highly context-sensitive.

## How the tradition evolved under criticism

The field did not simply move from weak to strong or from centralised to decentralised systems. It repeatedly narrowed claims and hybridised mechanisms: wall-clock order became causal or uncertainty-bounded time; leases gained fencing; global transactions were retained for non-compensatable invariants while sagas, outboxes, CRDTs and coordination avoidance handled other cases; unbounded queues yielded to backpressure and admission control; component restart yielded to feedback-aware recovery; process health yielded to capability-specific readiness; replay and snapshots gained external-state reconciliation; and random chaos yielded to hypothesis- and recovery-bound fault injection. The mature form is therefore assumption-explicit and boundary-scoped rather than tool-maximal.

## Citation-ready factual claims

| # | Claim | Durable source IDs |
| --- | --- | --- |
| 1 | Distributed systems differ qualitatively from single-process software because a missing response cannot distinguish crash, delay, partition, pause or a committed operation whose reply was lost. | S008,S044,S102 |
| 2 | Lamport's happens-before relation defines a causal partial order; a total order or wall-clock order is an additional construction, not the same fact. | S003 |
| 3 | Deterministic consensus cannot guarantee termination in a fully asynchronous system with one crash failure; practical liveness therefore depends on additional timing/failure-detector assumptions. | S006,S007,S008 |
| 4 | A quorum is meaningful only relative to a membership/configuration and state position whose intersection assumptions hold. | S011,S012,S014,S015 |
| 5 | Consensus safety and liveness are distinct, and agreement does not make the agreed value semantically valid. | S006,S007,S009,S011 |
| 6 | Lease expiry is time-based evidence, not proof the former holder cannot act; correctness-critical mutation needs stale-authority rejection at the resource boundary. | S035,S070,S094,S095 |
| 7 | CAP is not a permanent menu to 'pick any two'; its formal partition-case definitions and later PACELC-style normal-operation tradeoffs must be kept distinct. | S025,S026,S027 |
| 8 | Eventual replica convergence does not by itself supply a convergence deadline, bounded staleness or semantic validity of the converged state. | S028,S030,S037 |
| 9 | CRDT and invariant-confluence results justify coordination avoidance only for operation sets and invariants satisfying their conditions. | S030,S038,S039 |
| 10 | Exactly-once processing can be implemented inside a defined runtime/transaction boundary, but arbitrary external business effects remain separate. | S043,S046,S049,S054,S055 |
| 11 | Idempotency is semantic: a request identifier must be bound to the same operation parameters and effect, and its evidence must outlive the replay horizon. | S044,S069 |
| 12 | An acknowledgement establishes only the layer that durably emitted it; end-to-end completion needs a consumer-relevant postcondition or explicit residual uncertainty. | S043,S044,S055 |
| 13 | Durable workflow history enables recovery after orchestrator failure but does not automatically reconcile nondeterministic or external effects. | S050,S052,S054,S055,S056 |
| 14 | Queues store deferred work; they do not create service capacity, and unbounded backlog can amplify recovery failure. | S062,S063,S066,S073 |
| 15 | Retries can increase availability only when the operation is safe, the error is transient, a deadline remains and a shared capacity budget admits the attempt. | S063,S067,S068,S069 |
| 16 | Metastable failures can persist after the original trigger because backlog, retries, cache effects or recovery work form positive feedback. | S062,S063 |
| 17 | A consistent snapshot is an internally coherent cut under its model; restoring external effects and current authority requires additional reconciliation. | S004,S036,S071 |
| 18 | Replication alone does not imply fault tolerance: empirical storage studies and outages show corruption propagation, common modes and unusable restore paths. | S074,S075,S091 |
| 19 | Distributed traces are sampled, delayed and incomplete evidence; complete-looking traces are not guaranteed complete causal histories. | S080,S081,S082,S083 |
| 20 | Fault injection pays off when it challenges a specific current failure/recovery claim with representative load, evidence and stop conditions—not when it is repeated as theatre. | S084,S085,S086,S089,S090 |

## Evidence limits and claims not to make

- Do not claim that one formal methodology named Evolved Distributed Systems Engineering exists.
- Do not claim that CAP means choose any two under all conditions.
- Do not claim exactly-once business effects from transport, broker or workflow labels alone.
- Do not claim that consensus, a majority or a leader guarantees semantic validity or continuous availability.
- Do not claim that a lock/lease prevents stale mutation unless the resource enforces a current generation.
- Do not claim eventual convergence implies bounded staleness or business correctness.
- Do not claim replication, multi-AZ placement or backups prove recoverability without common-mode and restore evidence.
- Do not claim a trace, dashboard or green health endpoint is a complete/current global view.
- Do not claim microservices, event sourcing, service meshes or chaos tooling are general resilience properties.
- Do not claim recent agentic-system translations are mature or independently validated; P53 remains unresolved.

## Suggested public page outline

- 1. Why partial failure changes the problem
- 2. Plural historical lineages: causality, replication, consensus, transactions, messaging, recovery, streaming, workflows and overload
- 3. Failure and timing models before algorithms
- 4. Causal order, currentness and consistency contracts
- 5. Authority: membership, quorum, reconfiguration and fencing
- 6. Delivery, idempotency and effect boundaries
- 7. Transactions, sagas and durable workflows
- 8. Backpressure, admission, retries and metastability
- 9. Snapshots, replay, failover and tested recovery
- 10. Schema/configuration evolution and observability limits
- 11. Hypothesis-bound fault injection
- 12. Ceremony stripping, cheap paths and retirement
- 13. Current research frontier and unresolved agentic translation
- 14. Source notes and evidence limits

## Direct lineage, convergence and domain translation

- `DISTRIBUTED_SYSTEMS_NATIVE`: partial failure, causal order, message delivery, consensus/membership, replication/consistency, snapshots and recovery.
- `DATABASE_IMPORT_OR_SHARED_ANCESTRY`: serialisability, isolation, atomic commit, logging and geo-transaction designs.
- `NETWORKING_IMPORT_OR_SHARED_ANCESTRY`: unreliable communication and acknowledgement limits; networking is context, not the whole discipline.
- `FAULT_TOLERANCE_IMPORT_OR_SHARED_ANCESTRY`: fault models, state-machine replication, checkpoint/rollback and fault injection.
- `OPERATIONS_OR_QUEUEING_IMPORT`: finite queues, service capacity, backpressure, admission and overload stability.
- `CONVERGENT_PROPERTY`: end-to-end effect verification, cheap local paths, tested recovery and evidence-aware observability recur across lineages.
- `DOMAIN_TRANSLATION`: cloud-native/serverless architectures translate older properties; BFT is domain-specific; distributed AI/agents are a recent unresolved translation.
- `ONLY_ANALOGOUS`: product names, architecture fashions and recurring rituals without a protected consumer.

## Current-state and frontier notes without hype

- Geo-distributed transaction research continues to reduce commit latency; it does not abolish atomicity, membership or failure assumptions. [S041], [S042]
- Workflow research is explicitly questioning whether durable execution alone is sufficient and is exploring stronger correctness/repair semantics. [S055], [S056]
- Overload work increasingly treats cross-service policy and metastable feedback, not just isolated queue depth or autoscaling. [S063], [S065]
- Fault-injection work is moving toward persistence-order bugs and reproducible external-fault schedules. [S088], [S089]
- Observability work is refining triggered and rare-path sampling while retaining the fact that telemetry is incomplete. [S083]
- Cross-service integrity checking is emerging because decomposition leaves application invariants outside individual stores. [S092]
- Agentic/distributed-AI systems appear to inherit workflow, effect and semantic-validation burdens, but the evidence is early and P53 remains `UNRESOLVED`. [S097], [S098]

## Frozen public-intake receipt

- Property population referenced: 54/54
- Source records referenced: 102
- Repository-specific mapping: none
- Sibling packet reliance: none

## FINAL COMPLETION GATES

```text
historical_genealogy_complete = YES
major_school_relationships_dispositioned = YES
major_criticism_families_searched = YES
current_state_and_recent_frontier_searched = YES
failure_model_complete = YES
causality_time_model_complete = YES
replication_consistency_model_complete = YES
consensus_membership_authority_model_complete = YES
delivery_idempotency_model_complete = YES
transaction_compensation_model_complete = YES
durable_workflow_model_complete = YES
backpressure_overload_model_complete = YES
snapshot_checkpoint_recovery_model_complete = YES
schema_configuration_evolution_model_complete = YES
observability_state_reconstruction_model_complete = YES
fault_injection_resilience_test_model_complete = YES
ceremony_stripping_complete = YES
final_property_population_frozen = YES
all_properties_dispositioned = YES
source_table_complete = YES
criticism_ledger_complete = YES
internal_tensions_complete = YES
audit_intake_complete = YES
public_documentation_intake_complete = YES
frozen_artifacts_packaged = YES
manifest_hashes_complete = YES
```

EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_RESEARCH_STATE: FROZEN
PROPERTY_POPULATION_TOTAL: 54
PROPERTY_POPULATION_EXAMINED: 54
PROPERTY_COVERAGE: 54/54
EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_AUDIT_INTAKE: COMPLETE
PUBLIC_DOCUMENTATION_INTAKE: COMPLETE
FROZEN_PACKET_PACKAGED: YES
EXTERNAL_RESEARCH_READY_FOR_REPOSITORY_CROSSWALK: YES
