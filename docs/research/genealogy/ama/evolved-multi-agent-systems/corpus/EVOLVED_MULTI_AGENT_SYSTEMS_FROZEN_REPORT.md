# Evolved Multi-Agent Systems
## Independent tradition study and criticism-tested composition

**Analytical lineage:** `EVOLVED_MULTI_AGENT_SYSTEMS`  
**Frozen revision:** `EMAS-R1`  
**Research run date and cut-off:** 6 September 2026  
**State:** `FROZEN`, subject to the exact scope and evidence limits below.  
**Lane:** 7.2 in provisional candidate trifecta #7, Autonomous Agents / Multi-Agent Systems / Agent-Oriented Software Engineering.

“Evolved Multi-Agent Systems” is the name of this report’s analytical synthesis. It is not a claim that an academic school bearing that compound name exists. The established subject is Multi-Agent Systems (MAS). The study does not depend on the proposed trifecta and does not claim to have reconciled the other two traditions.

## Research judgement

MAS is not, at bottom, the multiplication of intelligent components. Its distinctive engineering question is how partially separate decision makers can coordinate or coexist when their information, capabilities, control, objectives and obligations do not automatically coincide. The useful unit of analysis is therefore not only an agent, but an **interdependence among agents, their environment and the people or institutions that control consequential resources**. Wooldridge and Jennings’ plural treatment of agency and the MAS foundations manuscript support a field broader than human-like cognition, decentralised optimisation alone or text-based collectives. [EMAS-S001, weak/strong agency and social aspects; EMAS-S023, foundations and taxonomy]

The strongest surviving core is conditional. Define the distributed boundary and objective; identify the dependency; select a compatible communication and coordination mechanism; distinguish a proposal, an undertaking, an action and its consequence; and evaluate the collective result under the information, incentive and failure assumptions that actually hold. This is an analytical composition, not a theorem or a compulsory architecture. An authorised scheduler can be the right answer. So can an open commitment protocol, a cooperative team, a constrained optimiser or an adaptive population. The selection conditions are part of the system, not exceptions to an otherwise universal mechanism.

Three conclusions organise the report. First, different traditions within MAS have different semantic objects. A private intention, a public commitment, a preference ordering, a norm and a constraint assignment cannot simply be renamed “agent state” and treated as interchangeable. Second, a component’s guarantee does not supply the guarantees of its neighbours: a legal message can remain false; an allocation can remain unperformed; a stable strategy can remain harmful; a correct optimiser can optimise an inappropriate objective. Third, criticism often produces a smaller or narrower mechanism rather than an ever larger architecture. The packet retains distinct negative and unresolved candidates so that these limits remain visible during later synthesis.

## What was examined, and what the evidence means

The complete registered candidate population is **76**, all examined. It includes **16 STRONGLY_RETAINED**, **28 RETAINED_IN_EVOLVED_FORM**, **10 CONTEXT_DEPENDENT**, **8 ASSUMPTION_SENSITIVE**, **3 DOMAIN_SPECIFIC**, **1 USEFUL_BUT_EASILY_GAMED**, **7 REJECTED_OR_DISFAVOURED**, **2 CEREMONY_NOT_GENERAL_PROPERTY** and **1 UNRESOLVED**. All ten mandatory domain families were examined; several carry explicit evidence limits. No candidate or mandatory family is `NOT_EXAMINED`. Retention does not mean every property must be implemented in every system.

The source table contains **56 exact-work/version records**: **52 with targeted full-text inspection**, one inspected institutional history page, one inspected proceedings index/contents, and two unavailable final-specification leads. “Targeted full-text inspection” means the actual relevant body sections were read, not that every page, cited reference or appendix was independently re-proved. Fifty-six records therefore do not mean fifty-six fully read monographs or fifty-six independent empirical studies. The report’s assertions are located in the source table; the two inaccessible specification records support only the stated access/version limit.

The evidence register separates conceptual/historical provenance, theoretical claims, standard or implementation semantics, comparison, field use, criticism and researcher interpretation. In particular, model correctness is not empirical external validity; a working implementation is not adoption; adoption is not a causal benefit estimate. The recorded airport programme and staged disaster exercises illustrate why those partitions matter. The source-dependence groups preserve shared programmes and benchmarks without pretending to estimate their statistical correlation. [EMAS-S042, original deployment report; EMAS-S043, field-trial and practitioner-feedback sections]

Research followed primary and lawful institutional/author copies backwards to foundational formulations and forwards through limitations, derivatives and current work. The current-year search covered selected AAMAS 2026 research and extended-abstract papers, as well as identified 2026 preprints. An index entry was never treated as a read paper. The coverage register records normalised search themes, access attempts, decision effects and the bounded saturation judgement. The stopping criterion was coverage of decision-relevant mechanisms and criticisms inside the declared scope, not a preset number of papers, properties or search rounds. No claim is made to have exhaustively indexed every publication appearing before the cut-off.

No requester repository, sibling research corpus or earlier Evolved crosswalk was consulted. The attachment supplied the assignment, not evidence about MAS. The externally researched corpus is independent of any later host system.

## Reconstructing the field without a linear progress story

### Distributed problems before an all-purpose agent metaphor

Smith’s December 1980 Contract Net paper is a canonical formulation of high-level distributed task connection. The distinction between task sharing and result sharing is made explicit in the related 1981 work. These were responses to distributed problem-solving needs, not an argument that every task should become an auction or that every awarded task had thereby been completed. Earlier formulations mentioned by these works are ancestry leads, not separately inspected evidence of the earliest origin of the entire field. [EMAS-S004, protocol and task connection; EMAS-S005, task/result sharing]

Durfee and Lesser’s Partial Global Planning changes the object of coordination. Local planning and execution continue while agents exchange selected information about activities and dependencies. A partial global plan is not an omniscient central schedule. That enables useful adaptation, but also makes the age and distribution of information consequential. A stale local account can produce duplicated effort or mutual waiting. Their setting supplies evidence about such mechanisms and costs, not a general empirical law for every organisation. [EMAS-S006, §§II–IV and experimental discussion]

The historical point is not that planning superseded contracting. Contracting can decide who should take responsibility; planning can decide how interdependent contributions fit together. Sometimes one eliminates the need for the other. Sometimes both are needed. The mature analytical question is which dependency remains after a cheaper decomposition, direct assignment or task bundle has been considered. This selection relation is represented explicitly rather than forcing all methods into one pipeline.

### Several accounts of cooperation

Joint-intention work asks what makes an undertaking persist as a team activity when one participant discovers that the goal has been achieved, become impossible or ceased to matter. Jennings distinguishes a commitment from the conventions that govern its reconsideration. SharedPlans gives a different account of collaboration with partially settled recipes and contributions. These theories do not all assert the same internal state or impose a fully detailed plan at the outset. [EMAS-S007, joint persistent goals; EMAS-S011, commitment/convention distinction; EMAS-S008, partial/full SharedPlans]

STEAM is an important documented hybrid: it uses selected ideas from joint intentions and SharedPlans, with operational monitoring and repair. COM-MTDP then exposes communication prescriptions to explicit decision-theoretic costs. This history supports the combination of persistence, useful notification and repair, not the maxim that everyone must continuously tell everyone everything. It also does not erase the distinction between a formal account of a joint plan and an implemented observer of material actions. [EMAS-S009, architecture and §4; EMAS-S010, COM-MTDP analysis]

The common-knowledge branch supplies another limit. Under its communication assumptions, an ideal shared-knowledge requirement can be unattainable. That does not establish that all useful cooperation is impossible. A practical protocol may deliberately protect a weaker property with a bounded residual risk. The choice must be declared rather than disguising an operational convention as a proof of unlimited mutual belief. [EMAS-S047, knowledge and communication model]

### Communication meaning is a substantive disagreement

KQML separates aspects of interchange through language architecture and performatives. The inspected FIPA communicative-act library provides a specified semantic account of acts such as informing and requesting. Neither the presence of a performative nor the fact that a message parses can certify the factual truth of its content, an external action or an interlocutor’s sincere internal state. [EMAS-S012, language architecture; EMAS-S014, §§2–3 and semantic annex]

Singh’s criticism targets the public use of private mental-state assumptions across opaque participants. A public commitment is a relation about what parties owe one another under specified conditions; it need not depend on an observer reading the debtor’s belief state. Commitment alignment and information-protocol work consequently operate on identifiable interactions and locally observable events. The result is not a blanket defeat of mental-state semantics. Inspectable agents can still be analysed using such semantics. The alternatives protect different claims under different observability assumptions. [EMAS-S013, especially p.44; EMAS-S044, local observations and alignment; EMAS-S016, information causality]

Version identity is itself material. The readable FIPA specimen is **XC00037H, experimental, status dated 10 August 2001**, approved earlier in 2001 and bearing a 2000 copyright. It is not the final SC00037J communicative-act profile. The requested final communicative-act and Contract Net profiles could not be read in this run. This supports an unresolved current-version/conformance question, not a claim that FIPA has disappeared or that no implementation conforms. [EMAS-S014, cover/foreword; EMAS-S015 and EMAS-S053, access records]

### Economics, logic and institutions are not interchangeable imports

MAS applies game theory, mechanism design and social choice to participants who can have private information and conflicting goals. Their imported theorems remain attached to their original domains. In bilateral trade, a desired bundle of incentive, participation, budget and full-efficiency conditions can be incompatible under the specified private-value assumptions. The result does not say that every market is impossible or choose which social sacrifice is acceptable. Voting results likewise depend on the preference domain and mechanism class. [EMAS-S024, model and efficiency result; EMAS-S025, manipulation theorem]

Task-exchange work adapts such concerns to computational decisions. Marginal costs, interactions among tasks, the contracts considered and the cost of deliberation all matter. A locally beneficial trade is not automatically globally optimal or strategyproof. Open strategic exchange therefore cannot inherit the honesty assumption of a cooperative optimiser merely by reusing its messages. [EMAS-S045, marginal-cost Contract Net; EMAS-S046, contract types and decommitment]

Organisation models add another level. Gaia relates roles, permissions and interaction responsibilities at an analysis/design intersection. MOISE+ explicitly distinguishes structural, functional and deontic dimensions. Neither a role chart nor a list of norms ensures that an agent adopts the role, can perform its mission or faces an effective response to violation. Normative-program and enforceability work make that gap concrete: preventing an act, observing it, classifying a violation, imposing a consequence and possessing legitimate authority are separate matters. [EMAS-S018, original scope and role models; EMAS-S019, organisational dimensions; EMAS-S020 and EMAS-S021, operational norms]

The organisation can itself be revised in a bounded model, but revision does not create external authority. Reorganisation also cannot repair every cause of failure: an impossible objective does not become possible merely because roles change. The synthesis therefore preserves a decision boundary for revision and continuity of existing undertakings, rather than assuming an organisation can automatically authorise any transformation of itself. [EMAS-S050, reorganisation phases and limitations]

## What mathematical guarantees protect—and what they leave open

A distributed constraint satisfaction or optimisation model defines variables, domains, constraints or costs and an information/communication structure. ADOPT and DPOP offer different ways of managing quality, search, memory and communication. DPOP’s structural message-size dependence is a reason to inspect graph width, not a reason to repeat a generic claim that distribution scales. Privacy is likewise a property of a specified disclosure protocol and adversary, not a consequence of storing information on different machines. [EMAS-S026, formulation/transport assumptions; EMAS-S027, bounds; EMAS-S028, Theorem 1; EMAS-S029, privacy definitions]

These methods establish properties of the modelled assignment. An engineer must still establish that the model represents the relevant resource problem, that the implementation meets the message assumptions, that the selected assignment can be enacted and that the actual collective consequence is acceptable. Adding a resource-changing actor is therefore not a clerical final step; it introduces a new composition obligation. This report’s separation of assignment and consequence is an analytical inference about that boundary, not an additional theorem attributed to ADOPT or DPOP.

Abstract argumentation establishes acceptability relative to an argument/attack graph and a chosen semantics. Some semantics can yield no stable extension; choosing another semantics changes the question answered. A voted alternative or accepted argument is not thereby an independent observation of the world. The synthesis retains these decision procedures while rejecting the conversion of consensus into factual certainty. [EMAS-S031, §2; EMAS-S025, mechanism domain]

The import into a specific MAS dialogue is documented, not inferred from the presence of argumentation in a general field taxonomy. Amgoud, Maudet and Parsons explicitly identify Dung as an inspiration, then couple preference-sensitive arguments to assertion, challenge, acceptance and public store updates. That coupling supplies an operating method for a reasoning criterion. It does not, by itself, supply relevance or useful termination: the authors acknowledge that legal repeated moves can continue indefinitely. Their basic two-party account also omits withdrawal and requires extension for negotiation or deliberation. [EMAS-S055, §§2–5]

McBurney and Parsons distinguish public protocol conformance from private reasoning preconditions and separate kinds of dialogical and action commitment. Consequently, this synthesis neither treats every argument dialogue as a Singh-style external obligation nor assumes that a public trace exposes private sincerity. A disputed fact may need direct investigation rather than another round of dialogue. These findings refine EMAS-046 and its coupling to communication and useful-progress criteria; they do not create one compulsory control for every dialogue formalism. [EMAS-S056, §§4–6; researcher composition]

The 2026 fault-tolerant DCOP branch illustrates how criticism should refine rather than inflate a guarantee. Its replication/knowledge conditions apply to relevant groups, not merely to the global number of agents. The construction seeks to reproduce the underlying optimiser’s fault-free messages. If the underlying method is approximate, replication does not make its answer globally optimal; if all replicas share a wrong objective, agreement does not correct it. The main paper’s argument and experiment were inspected, but its supplementary impossibility proof was not independently reconstructed. [EMAS-S051, Theorem 4.2, §5 and §6]

## Learning, emergence and changing partners

In multi-agent learning, the other learners partly constitute the environment. A policy that was adequate against yesterday’s partners can fail after they update. Centralised training/decentralised execution addresses one information arrangement, not every deployment. A training critic may see information that the deployed actor cannot. QMIX’s monotonic construction constrains which joint value functions can be represented; it does not assert that every useful joint behaviour lies within that class. [EMAS-S032, multi-agent actor-critic formulation; EMAS-S033, monotonic mixing]

Other-Play makes partner compatibility an explicit target under known symmetries. That is a substantive response to self-play conventions that do not transfer, but it is not a universal solution for unseen people or arbitrary institutions. The later benchmarking corpus reinforces task, seed and configuration sensitivity. The mature retained criterion is to evaluate the population and information regime actually claimed, including cross-play or changed partners where relevant. [EMAS-S034, coordination and cross-play; EMAS-S035, evaluation protocol]

Emergence describes a pattern arising through interaction. It is not an endorsement of that pattern. A convention can coordinate a group while disadvantaging others; a stable equilibrium can sustain collusion; resource use can look locally profitable while destroying the shared resource. Recent norm-formation and pricing studies make these questions experimentally concrete within their controlled models. They do not transform simulated voting into institutional legitimacy or establish the prevalence of such behaviour in real markets. [EMAS-S039, common-pool model; EMAS-S040, restricted meta-game]

Norm-aware BDI in 2026 represents a different integration: norm-related steps, consequences and non-applicability can enter plan choice. That is more operative than merely attaching a norm document. Yet being able to represent a violation does not authorise it, and a running example does not establish large-scale or changing-norm performance. The packet retains this as a domain-specific mechanism, separate from norm enforcement and from general autonomous revision. [EMAS-S052, §§2–3]

## Contemporary LLM collectives: neither a universal upgrade nor a universal mistake

Positive debate studies, failure analyses, equal-budget comparisons and genuine interactive coordination environments address different claims. The original inspected debate preprint provides selected positive evidence, but not a general guarantee. MAST’s larger trace analysis is not a sample of independent production organisations; its manual coding and larger assisted analysis have different denominators. Equal-thinking-budget work improves the comparator, but thinking tokens, actual compute, latency, tools and training cost are not interchangeable currencies. [EMAS-S048, experiment discussion; EMAS-S036, methods; EMAS-S037, comparison design]

The important contemporary counterweight to simple answer-debate evaluations is an environment where agents must actually combine resources and synchronise actions. The alem benchmark separates base-task progress from coordination reward. Its trained MARL references and zero-shot language agents have different training budgets, so their juxtaposition is not a causal matched-compute superiority result. It nevertheless provides component evidence that individual competence and collective coordination can diverge. [EMAS-S038, §§3–4]

Communication is a particularly useful discriminator. Removing a channel that carries timing or handover information can harm coordination. Additional specialists or coalition messages can instead introduce a bottleneck. A human-facing status explanation can be accurate yet fail to improve the recipient’s performance. These findings do not contradict one another: the consumer, dependency, task and cost differ. The retained requirement is to show which action or expectation the communication changes. [EMAS-S038, §4.2.2; EMAS-S041, simulation; EMAS-S054, §§2–3]

Human participation is not automatically a cure. People need feasible decisions, usable information, actual control and a way to contest or stop consequential action. Staged human-agent trials and current exploratory experiments identify useful questions about those interfaces, but do not establish universal oversight effectiveness. Conversely, limited power or a non-significant result does not establish that explanations are useless. [EMAS-S022, ethical/human-agent argument; EMAS-S043, participant/practitioner findings; EMAS-S054, limitations]

## An adversarial mathematical check of a convenient negative claim

The study did not treat criticism of MAS as immune to criticism. Section 3 of EMAS-S037 models messages as a function of an available context and invokes information loss to support a strict error comparison. The following is **this report’s mathematical analysis**, not a published correction or an empirical replication.

Let C take two equally probable values c₁ and c₂. Set P(Y=1|c₁)=0.9 and P(Y=1|c₂)=0.6, and let M be constant. A Bayes-optimal classifier predicts 1 under either value of C, and also under M. Both errors are 0.25. Nevertheless,

`I(Y; C) = H₂(0.75) − [H₂(0.9) + H₂(0.6)]/2 ≈ 0.091305 bits > 0 = I(Y; M)`.

Thus strict loss of mutual information need not strictly increase classification error. More generally, lower bounds on two errors do not by themselves order the errors. A **weak** Bayes-risk ordering under M=g(C) follows for an unrestricted decision maker because a C-based rule can emulate any M-based rule. That observation does not prove that a particular finite LLM, under a compute budget, uses C as well as another architecture uses its intermediate representations. It also does not address new information gathered through tools outside the assumed channel.

The disposition change is deliberate: retain the study’s bounded comparative evidence and budget discipline, but reject a universal single-agent-superiority theorem and the strict-information-loss implication. This is criticism ledger EMAS-K018. It prevents the synthesis from replacing “more agents are always better” with the equally unwarranted opposite slogan.

## Reading the frozen packet

The JSON property ledger is the authoritative complete candidate register. Each record carries history, mechanism, trigger/non-trigger, preconditions, all ten domain-profile dimensions, authority/interaction/effect distinctions, criticism, evolution, evidence partitions, disposition and linked composition relations. Domain-profile pointers resolve within that same JSON. The composition model carries 12 analytical nodes, 61 guarded relations, six alternative configurations, external/revision boundaries, 24 criticisms, 12 ceremony analyses, ten tensions and 15 discriminating tests. The coverage file carries the dated genealogy, evolution transitions and explicit empirical/formal evidence registers.

The audit intake asks neutral questions of an unspecified later system. The public-documentation intake supplies bounded citation-ready claims without claiming host adoption. The synthesis intake exports all candidate keys and selection conditions for later independent reconciliation. A later integrator must preserve the denominator, adverse findings and source ancestry even when one mechanism satisfies several concerns.

## EVOLVED_MULTI_AGENT_SYSTEMS_TIMELINE

Dates below are publication or identified version dates unless the entry explicitly says otherwise. They are not a claim that each work is the earliest possible precursor. See the coverage JSON for the structured timeline.

| Date | Examined development | Sources |
|---|---|---|
| 1973; 1983 | Economic and social-choice antecedents (EMAS-G001) | EMAS-S024; EMAS-S025 |
| 1980; 1981 | Distributed problem solving and Contract Net (EMAS-G002) | EMAS-S004; EMAS-S005 |
| 1987 | Partial Global Planning / Durfee–Lesser (EMAS-G003) | EMAS-S006 |
| 1990 | Common-knowledge limits (EMAS-G004) | EMAS-S047 |
| 1990; 1993 | Joint intentions, commitments and conventions (EMAS-G005) | EMAS-S007; EMAS-S011 |
| 1996 | SharedPlans (EMAS-G006) | EMAS-S008 |
| 1997; 2002 | STEAM and COM-MTDP (EMAS-G007) | EMAS-S009; EMAS-S010 |
| 1994; 2001 inspected version | KQML and FIPA communicative acts (EMAS-G008) | EMAS-S012; EMAS-S014 |
| 1998; 2009 | Public commitments and alignment (EMAS-G009) | EMAS-S013; EMAS-S044 |
| 2012; 2025 | Information protocols and BSPL implementation (EMAS-G010) | EMAS-S016; EMAS-S017 |
| 1993; 1995 | Economic task exchange and contract structures (EMAS-G011) | EMAS-S045; EMAS-S046 |
| 2000 | Gaia organisation/engineering intersection (EMAS-G012) | EMAS-S018 |
| 2002; 2004 | MOISE+ and cooperative reorganisation (EMAS-G013) | EMAS-S019; EMAS-S050 |
| 2008; 2011 publication of COIN 2010 work | Normative programs and enforceability (EMAS-G014) | EMAS-S020; EMAS-S021 |
| 1998; 2005; 2014; 2018 | Distributed constraint satisfaction/optimisation (EMAS-G015) | EMAS-S026; EMAS-S027; EMAS-S028; EMAS-S029; EMAS-S030 |
| 1995 | Abstract argumentation (EMAS-G016) | EMAS-S031 |
| 2009/2010 inspected manuscript | Consolidated MAS foundations (EMAS-G017) | EMAS-S023 |
| 2017; 2018; 2020 | Deep MARL, CTDE, factorisation and Other-Play (EMAS-G018) | EMAS-S032; EMAS-S033; EMAS-S034 |
| 2008 report of 2007 deployment; 2016; 2022 | Strategic decision aids and human-agent collectives (EMAS-G019) | EMAS-S042; EMAS-S043; EMAS-S022 |
| 2009 | Trust under strategic manipulation (EMAS-G020) | EMAS-S049 |
| 2023 inspected preprint; 2025; 2026 | Language-model collective translation (EMAS-G021) | EMAS-S048; EMAS-S036; EMAS-S037; EMAS-S038 |
| 2026 | Norm formation, collusion and specialist bottlenecks (EMAS-G022) | EMAS-S039; EMAS-S040; EMAS-S041 |
| 2026 | Fault-tolerant DCOP and norm-aware BDI (EMAS-G023) | EMAS-S051; EMAS-S052 |
| 2026 | Triggered explanations in human-agent collaboration (EMAS-G024) | EMAS-S054 |
| 2000; 2002 | Argumentation-based inter-agent dialogue and protocol critique (EMAS-G025) | EMAS-S055; EMAS-S056 |

## EVOLVED_MULTI_AGENT_SYSTEMS_GENEALOGY

The genealogy is plural. Imported economics and AI logic, distributed problem solving, teamwork semantics, organisational systems and learning remain distinguishable branches. An edge labelled analogy is not silently upgraded to influence. The machine-readable nodes and edges are in `RESEARCH_COVERAGE.json → genealogy`.

### EMAS-G001 — Economic and social-choice antecedents (1973; 1983)

Strategic reports and incompatible allocative desiderata. Restricted mechanism/choice models with explicit impossibility results. Results imported into MAS reasoning, not invented by MAS.

**Limit and reception:** Different domain, participation or randomisation assumptions change applicability. Systematic treatment in the inspected MAS foundations manuscript; native allocation work requires additional engineering assumptions. [EMAS-S024; EMAS-S025]

### EMAS-G002 — Distributed problem solving and Contract Net (1980; 1981)

Loosely coupled processors must find suitable recipients for distributed tasks and share results. Task announcements, bids, awards; task-sharing/result-sharing distinction. A canonical high-level distributed control protocol and decomposition vocabulary.

**Limit and reception:** Not proof of task completion, truthful reporting or universal optimality. The 1977 predecessor is mentioned but not independently read. Later marginal-cost and contract-type work changes allocative mechanisms; not a single linear replacement. [EMAS-S004; EMAS-S005]

### EMAS-G003 — Partial Global Planning / Durfee–Lesser (1987)

Concurrent local plans interact under incomplete information. Selected local plans, partial global views and continuing activity coordination. Interleaves planning, communication and execution rather than requiring one complete prior plan.

**Limit and reception:** Original meta-organisation and vehicle-monitoring simulation constrain generality; stale plans can cause failures. Its explicit coordination costs remain relevant to later teamwork and modern multi-agent claims; direct influence is not inferred solely from similar terms. [EMAS-S006]

### EMAS-G004 — Common-knowledge limits (1990)

What agents can know jointly with uncertain communication. Epistemic models distinguish shared knowledge levels and their attainable conditions. A formal boundary on idealised coordination requirements.

**Limit and reception:** Not a theorem against all cooperation or all asynchronous protocols. Helps discriminate ideal semantics from practical notification requirements; does not replace teamwork theories. [EMAS-S047]

### EMAS-G005 — Joint intentions, commitments and conventions (1990; 1993)

Parallel intentions do not explain persistence and repair of a joint undertaking. Joint persistent goals; commitment and reconsideration/notification conventions. Joint activity includes duties about changed feasibility and goal status.

**Limit and reception:** Ideal mental-state assumptions; centrality is a school’s thesis, not field consensus. STEAM operationalises selected ideas; social-commitment work chooses a different public semantic object. [EMAS-S007; EMAS-S011]

### EMAS-G006 — SharedPlans (1996)

A team can act before recipes and allocations are fully settled. Partial shared plans, intentions towards others and reconciliation. Represents incomplete collaborative planning without collapsing it into one aggregate intention.

**Limit and reception:** Does not by itself provide continuous monitoring of external action. Explicitly drawn upon, alongside joint intentions, in STEAM; remains an alternative explanatory account. [EMAS-S008]

### EMAS-G007 — STEAM and COM-MTDP (1997; 2002)

Formal teamwork must be operational and communication has a cost. Team monitoring/repair, selective communication and decision-theoretic analysis. Turns team commitments into action-relevant monitoring and notification choices.

**Limit and reception:** Simulation/application programmes and finite decision models do not establish universal superiority. Refines rather than eliminates the theoretical distinction between intention, communication and observed success. [EMAS-S009; EMAS-S010]

### EMAS-G008 — KQML and FIPA communicative acts (1994; 2001 inspected version)

Heterogeneous agents need a language/protocol for knowledge and action requests. Performatives, content separation and specified communicative-act semantics. Makes communication layers and intended effects explicit.

**Limit and reception:** The inspected FIPA specimen is experimental XC00037H dated 2001-08-10, not the inaccessible later final texts. Singh’s critique disputes private mental-state foundations for open systems; standardisation does not settle the dispute. [EMAS-S012; EMAS-S014]

### EMAS-G009 — Public commitments and alignment (1998; 2009)

Opaque agents cannot publicly verify one another’s private beliefs. Social obligations and lifecycle rules; alignment under specified transport and local-observation conditions. Public interaction can be specified without assuming shared implementation internals.

**Limit and reception:** Alignment at quiescence under the paper’s assumptions is neither instant omniscience nor fulfilled external work. Continues a distinct social-semantic approach; not a universally stronger replacement for inspectable mental-state models. [EMAS-S013; EMAS-S044]

### EMAS-G010 — Information protocols and BSPL implementation (2012; 2025)

Rigid control-flow descriptions poorly capture distributed enactment. Information causality, keys/bindings and legal local message steps. Permits flexible interaction while analysing enactability and model-level completion possibility.

**Limit and reception:** Protocol liveness has a precise weaker meaning than eventual work completion; later implementation is short-form evidence. The 2025 SARL work explicitly translates the BSPL mechanism into an implementation environment. [EMAS-S016; EMAS-S017]

### EMAS-G011 — Economic task exchange and contract structures (1993; 1995)

Task bundles, costs and incomplete deliberation complicate naive bidding. Marginal-cost exchange; decommitment and richer contract neighbourhoods. Bridges distributed control with economic and bounded-rational decision assumptions.

**Limit and reception:** Cost/pricing regimes do not automatically establish honesty, social welfare or arbitrary resource externalities. Preserves several branches: central allocation, cooperative estimates, strategic mechanisms and limited search. [EMAS-S045; EMAS-S046]

### EMAS-G012 — Gaia organisation/engineering intersection (2000)

Analysis and design need roles, permissions and interaction responsibilities. Role/protocol models and documented adaptation of object-oriented methodological ideas. Documents an intersection of MAS organisational concepts with agent-oriented engineering.

**Limit and reception:** Original scope restricts changing abilities/services and open strategic participation. Useful genealogy for a later AOSE comparison, not a substitute for independently studying that tradition. [EMAS-S018]

### EMAS-G013 — MOISE+ and cooperative reorganisation (2002; 2004)

Organisation must connect structural roles to goals and obligations, and sometimes change. Structural, functional and deontic models; monitored design/select/implement revision. Makes different organisational dimensions and revision responsibilities explicit.

**Limit and reception:** Early examples are simulated; reorganisation cannot repair every failed goal or environment. Later normative and plan-integration work addresses enforcement and operational gaps without proving general self-government. [EMAS-S019; EMAS-S050]

### EMAS-G014 — Normative programs and enforceability (2008; 2011 publication of COIN 2010 work)

A declared obligation can be violated and the event may not be observable. Institutional state, norm monitoring, prevention, sanctions and grievance-based handling. Separates normative specification from enforceable operational effects.

**Limit and reception:** Formal guarantees assume observable/modelled actions; computational authority is not external jurisdiction. Norm-aware BDI is a different 2026 branch: planning with norms rather than merely imposing controls. [EMAS-S020; EMAS-S021]

### EMAS-G015 — Distributed constraint satisfaction/optimisation (1998; 2005; 2014; 2018)

Distributed agents must choose consistent or low-cost assignments. Asynchronous search, bounds, pseudo-tree dynamic programming and privacy-preserving protocol variants. Provides precise feasibility/quality/computation trade-offs.

**Limit and reception:** Transport, graph width, leakage and model correctness constrain guarantees. A 2026 fault-tolerant extension addresses a specific corruption model; it is not generic consensus. [EMAS-S026; EMAS-S027; EMAS-S028; EMAS-S029; EMAS-S030]

### EMAS-G016 — Abstract argumentation (1995)

Conflicting arguments require semantics for acceptability. Argument/attack structures and admissible, preferred, stable and grounded semantics. AI/non-monotonic-logic contribution reused in MAS deliberation.

**Limit and reception:** Graph acceptance does not independently warrant the truth of premises; some semantics can have no extension. A documented interdisciplinary import, not evidence that all social agreement is factual knowledge. [EMAS-S031]

### EMAS-G017 — Consolidated MAS foundations (2009/2010 inspected manuscript)

A plural field needs a systematic conceptual and mathematical account. Distributed problem solving, strategic games, social choice and mechanism design presented with distinct assumptions. Documents the coexistence of computational and economic approaches.

**Limit and reception:** The inspected revision is an uncorrected manuscript, not every later corrected edition. A taxonomy/definition source; original theorems were sought separately for load-bearing impossibility claims. [EMAS-S023]

### EMAS-G018 — Deep MARL, CTDE, factorisation and Other-Play (2017; 2018; 2020)

Learning agents face non-stationarity, credit assignment and conventions that do not transfer. Centralised training/local execution, monotonic value mixing, symmetry-based cross-play preparation. Makes learning and partner dependence explicit operational design objects.

**Limit and reception:** Controlled games, representation classes and known symmetries limit claims. 2025 benchmarking and 2026 coordination environments test generalisation and cost without establishing universal open-world competence. [EMAS-S032; EMAS-S033; EMAS-S034]

### EMAS-G019 — Strategic decision aids and human-agent collectives (2008 report of 2007 deployment; 2016; 2022)

People and algorithms must combine recommendations, information and real action. Human-constrained security schedules; mixed-initiative task assignment and participant control. Shows different forms of applied MAS and external participation.

**Limit and reception:** An airport deployment report and staged disaster trials are different evidence kinds; neither proves the full field’s causal effectiveness. Current human-agent experiments ask when explanations aid collaboration; human involvement is not automatically useful or ceremonial. [EMAS-S042; EMAS-S043; EMAS-S022]

### EMAS-G020 — Trust under strategic manipulation (2009)

Participants can rebuild good reputation and then defect again. Explicit con-man histories and modified direct-trust dynamics. Negative evidence against unqualified reputation-based safety.

**Limit and reception:** Simplified two-agent histories; first defection is not prevented. Supports bounded exposure and threat-specific evidence, not elimination of trust as a useful heuristic. [EMAS-S049]

### EMAS-G021 — Language-model collective translation (2023 inspected preprint; 2025; 2026)

Language agents can exchange reasoning but incur costs and coupled failures. Debate, trace analysis, equal-budget comparisons and long-horizon coordination benchmarks. Positive component evidence and increasingly discriminating negative comparisons.

**Limit and reception:** Shared sources, judges, models and unmatched training/inference budgets restrict independence and generality. Retain actual mechanisms; neither a universal MAS benefit nor universal single-agent superiority is warranted. [EMAS-S048; EMAS-S036; EMAS-S037; EMAS-S038]

### EMAS-G022 — Norm formation, collusion and specialist bottlenecks (2026)

Stable cooperation, strategic adaptation and specialisation can have adverse collective effects. Controlled common-pool norms, finite pricing meta-games and kitchen collaboration simulation. Recent tests differentiate behavioural stability from social value and expose coordination costs.

**Limit and reception:** Simulated populations, finite strategies and short-form reports limit transfer. Requires explicit normative criteria and task-specific alternatives rather than a progress narrative. [EMAS-S039; EMAS-S040; EMAS-S041]

### EMAS-G023 — Fault-tolerant DCOP and norm-aware BDI (2026)

Existing mechanisms need robustness or normative action integration. Replicated Max-Sum messages under a fault/knowledge model; norm-related plan alternatives. Two specific extensions with different objects and guarantees.

**Limit and reception:** Approximate optimisation remains approximate; running-example norm awareness is not universal compliance. Retained as domain-specific additions, not compulsory new layers for every MAS. [EMAS-S051; EMAS-S052]

### EMAS-G024 — Triggered explanations in human-agent collaboration (2026)

Useful team transparency competes with attention and action speed. Hierarchical policy subtask explanations compared across text/audio/control conditions. Adds a current null result and recipient-specific communication question.

**Limit and reception:** Small experienced convenience sample and one layout; no significant difference is not equivalence. Refines selective communication and human participation rather than creating a universal explanation requirement. [EMAS-S054]

### EMAS-G025 — Argumentation-based inter-agent dialogue and protocol critique (2000; 2002)

Agents must exchange and challenge reasons, not merely calculate acceptability privately. Preference-sensitive argument generation plus dialogue moves, public stores and private rationality preconditions. Documents an explicit Dung-inspired MAS adaptation and a criticism-led distinction between trace legality, private conformance and termination.

**Limit and reception:** Basic model is two-party, omits retraction and relies on relevance/useful-stopping assumptions; it is not a general negotiation or truth guarantee. The 2002 analysis distinguishes commitment meanings and the open protocol-design obligations. No current-day research frontier is inferred from its historical claims. [EMAS-S055; EMAS-S056]

### Material genealogy edges

| Edge | From → to | Classification | Documentary basis and boundary |
|---|---|---|---|
| EMAS-GE001 | EMAS-G002 → EMAS-G011 | EXPLICIT_EXTENSION | The later papers explicitly analyse/implement Contract Net and change cost/contract assumptions. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S045; EMAS-S046] |
| EMAS-GE002 | EMAS-G002 → EMAS-G003 | SHARED_ANCESTRY | Both address distributed problem-solving control; PGP targets interleaving local plans rather than merely task connection. No exact derivation of PGP from one Contract Net implementation is asserted. [EMAS-S005; EMAS-S006] |
| EMAS-GE003 | EMAS-G005 → EMAS-G007 | DOCUMENTED_INFLUENCE | STEAM explicitly builds its team model using joint-intention ideas. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S009] |
| EMAS-GE004 | EMAS-G006 → EMAS-G007 | HYBRIDISATION | STEAM explicitly combines selected SharedPlans concepts with joint intentions. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S009] |
| EMAS-GE005 | EMAS-G007 → EMAS-G007 | CRITICISM_AND_RESPONSE | COM-MTDP analyses teamwork prescriptions, including communication costs, within the same programme. A self-edge denotes development within this grouped school, not circular provenance. [EMAS-S009; EMAS-S010] |
| EMAS-GE006 | EMAS-G004 → EMAS-G005 | SHARED_ANCESTRY | Both analyse knowledge conditions for coordinated action. A direct influence edge is not inferred merely from temporal proximity. [EMAS-S007; EMAS-S047] |
| EMAS-GE007 | EMAS-G008 → EMAS-G009 | CRITICISM_AND_RESPONSE | Singh explicitly criticises ACL semantic principles and argues for public social commitments. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S013] |
| EMAS-GE008 | EMAS-G009 → EMAS-G010 | CONVERGENT_DEVELOPMENT | Public commitments and information protocols both address open distributed enactment with observable interaction. Their semantic objects differ; an exact derivation is not claimed. [EMAS-S013; EMAS-S016; EMAS-S044] |
| EMAS-GE009 | EMAS-G010 → EMAS-G010 | DOMAIN_TRANSLATION | The 2025 implementation paper explicitly applies BSPL in SARL. Implementation demonstration is not independent effectiveness replication. [EMAS-S016; EMAS-S017] |
| EMAS-GE010 | EMAS-G001 → EMAS-G011 | DOCUMENTED_IMPORT | Economic marginal-cost, contracting and bounded-rational considerations are explicit in task exchange. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S045; EMAS-S046] |
| EMAS-GE011 | EMAS-G001 → EMAS-G017 | DOCUMENTED_IMPORT | The foundations manuscript discusses imported economic and social-choice results; original theorem sources inspected. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S023; EMAS-S024; EMAS-S025] |
| EMAS-GE012 | EMAS-G012 → EMAS-G013 | CONVERGENT_DEVELOPMENT | Both organise agents through roles and interactions but use different structural/functional constructs. Conceptual overlap is not proof of direct derivation or semantic equivalence. [EMAS-S018; EMAS-S019] |
| EMAS-GE013 | EMAS-G013 → EMAS-G013 | EXPLICIT_EXTENSION | The 2004 reorganisation paper explicitly extends the organisational programme to organisation change. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S019; EMAS-S050] |
| EMAS-GE014 | EMAS-G013 → EMAS-G014 | CRITICISM_AND_RESPONSE | Normative-program and enforceability analyses discuss operational limitations in organisational/normative approaches. Criticism applies to the identified versions, not every future descendant. [EMAS-S020; EMAS-S021] |
| EMAS-GE015 | EMAS-G014 → EMAS-G023 | HYBRIDISATION | Norm-aware BDI explicitly adds norm-related steps/alternatives to goal-plan reasoning. It does not prove that enforcement and autonomous deliberation are interchangeable. [EMAS-S052] |
| EMAS-GE016 | EMAS-G015 → EMAS-G023 | EXPLICIT_EXTENSION | FT-DCOP explicitly extends distributed optimisation to a bounded corruption and replicated-computation model. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S051] |
| EMAS-GE017 | EMAS-G016 → EMAS-G025 | DOCUMENTED_IMPORT | EMAS-S055 §2 explicitly states that its argumentation model is inspired by Dung and goes further by treating preferences; §§4–5 adapt it to agent dialogue. This is a documented specific adaptation, not evidence of a Dung-derived chapter in EMAS-S023. Additional philosophical precursors mentioned by the authors are not separately claimed as fully inspected. [EMAS-S031; EMAS-S055] |
| EMAS-GE018 | EMAS-G018 → EMAS-G021 | DOMAIN_TRANSLATION | The alem work tests language agents alongside MARL references in coordination environments. Language-model agents and trained MARL agents have different training and information budgets. [EMAS-S038] |
| EMAS-GE019 | EMAS-G018 → EMAS-G024 | HYBRIDISATION | A learned hierarchical policy is coupled to human-facing explanations in a teamwork experiment. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S054] |
| EMAS-GE020 | EMAS-G019 → EMAS-G024 | CONVERGENT_DEVELOPMENT | Human control and useful communication recur across different human-agent settings. Different studies/populations are not replications of one intervention. [EMAS-S022; EMAS-S043; EMAS-S054] |
| EMAS-GE021 | EMAS-G021 → EMAS-G022 | DOMAIN_TRANSLATION | Classical strategic and normative interaction questions are tested with language-agent populations. No causal effectiveness or universal superiority follows from this relationship. [EMAS-S039; EMAS-S040] |
| EMAS-GE022 | EMAS-G011 → EMAS-G022 | ONLY_ANALOGOUS | Both expose costs of specialisation/allocation, but the 2026 kitchen simulation is not a new Contract Net implementation. Resembling a task-allocation problem does not establish inherited protocol guarantees. [EMAS-S041; EMAS-S045] |
| EMAS-GE023 | EMAS-G017 → EMAS-G021 | ONLY_ANALOGOUS | Terms such as agent, debate and society resemble classical vocabulary but require mechanism-level validation. No direct academic inheritance is assumed for an arbitrary LLM framework. [EMAS-S023; EMAS-S036; EMAS-S048] |
| EMAS-GE024 | EMAS-G008 → EMAS-G008 | UNRESOLVED_RELATIONSHIP | The historical experimental library and inaccessible final profiles are distinct version records. Current equivalence, conformance and use are not certified. [EMAS-S014; EMAS-S015; EMAS-S053] |
| EMAS-GE025 | EMAS-G020 → EMAS-G022 | CONVERGENT_DEVELOPMENT | Both study strategic adaptation that exploits an interaction history. Con-man trust models and pricing meta-games are not the same attack model. [EMAS-S049; EMAS-S040] |

## EVOLVED_MULTI_AGENT_SYSTEMS_SCOPE_AND_CARICATURES

The field includes cooperative, competitive and mixed-motive agents, centralised and decentralised decision points, homogeneous and heterogeneous populations, and fixed and changing membership. An ordinary distributed service is not automatically an autonomous strategic agent; a MAS need not have human-like cognition, natural-language messages or equality of authority. Agent-based simulation is an evidence method and modelling form, not a synonym for the whole field. AOSE is a documented intersection, not a substitute for coordination theory. [EMAS-S001; EMAS-S005; EMAS-S018; EMAS-S023]

The central caricatures rejected here are that more agents imply capability, decentralisation implies resilience, naming roles establishes organisation, negotiation is mandatory, consensus proves truth, local improvement guarantees collective progress, and more communication ensures robustness. The negative candidates preserve these tested propositions rather than removing them from the denominator. Favourable evidence for a particular team remains admissible; an adverse case is not dismissed as “not really MAS”.

The bounded study does not include every economic mechanism, every robotics controller, every implementation of an agent platform or every AAMAS paper. Those omissions are scope boundaries, not claims that adjacent work is unimportant. The unresolved current FIPA question is specifically an examined access/version limit. Detailed access limitations and alternative readable coverage are recorded in the coverage file.


## EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER

**Full denominator: 76. Examined: 76.** The following is every registered ID, not a top-properties list. Complete records are in [the property ledger](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json); fragments identify JSON Pointers into `properties`. `STRONGLY_RETAINED` denotes a robust distinction or bounded criterion, not a universal empirically established payoff.

| Disposition | Count |
|---|---:|
| RETAINED_IN_EVOLVED_FORM | 28 |
| STRONGLY_RETAINED | 16 |
| REJECTED_OR_DISFAVOURED | 7 |
| ASSUMPTION_SENSITIVE | 8 |
| CONTEXT_DEPENDENT | 10 |
| UNRESOLVED | 1 |
| CEREMONY_NOT_GENERAL_PROPERTY | 2 |
| DOMAIN_SPECIFIC | 3 |
| USEFUL_BUT_EASILY_GAMED | 1 |

| ID and complete record | Candidate | Kind | Primary disposition | Examination |
|---|---|---|---|---|
| [EMAS-001](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/0) | Interdependence-justified agent decomposition | SELECTION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-002](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/1) | Explicit population and environment boundary | MODELLING_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-003](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/2) | Explicit goal alignment and incentive regime | MODELLING_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-004](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/3) | Separate information, capability, control and authority | BOUNDARY_INVARIANT | STRONGLY_RETAINED | EXAMINED |
| [EMAS-005](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/4) | Decentralisation inherently guarantees resilience | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-006](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/5) | More agents automatically add capability | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-007](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/6) | Layered communication contract | COMMUNICATION_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-008](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/7) | Publicly verifiable communicative effects | SEMANTIC_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-009](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/8) | Private mental-state sincerity as a universal compliance test | SEMANTIC_ALTERNATIVE | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-010](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/9) | Conversation identity and information causality | PROTOCOL_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-011](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/10) | Protocol enactability and completion possibility | FORMAL_PROTOCOL_PROPERTY | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-012](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/11) | Delivery, interpretation, acceptance and consequence are separate | OBSERVATION_INVARIANT | STRONGLY_RETAINED | EXAMINED |
| [EMAS-013](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/12) | Current FIPA profile and implementation equivalence | VERSION_AND_TRANSFER_CLAIM | UNRESOLVED | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-014](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/13) | Performatives or role prompts constitute cooperation | CEREMONIAL_SUBSTITUTE | CEREMONY_NOT_GENERAL_PROPERTY | EXAMINED |
| [EMAS-015](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/14) | Capability- and cost-aware task allocation | ALLOCATION_MECHANISM | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-016](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/15) | Award, acceptance, execution and task completion are distinct | TASK_LIFECYCLE_INVARIANT | STRONGLY_RETAINED | EXAMINED |
| [EMAS-017](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/16) | Marginal-cost bargaining improves global allocation under a stated regime | NEGOTIATION_MECHANISM | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-018](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/17) | Partial global planning with revisable local views | COORDINATION_MECHANISM | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-019](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/18) | Dependency elimination can substitute for coordination | SUBSTITUTION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-020](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/19) | Shared-resource and temporal dependency constraints | COORDINATION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-021](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/20) | Conditional decommitment and recontracting | CONTRACT_MECHANISM | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-022](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/21) | Negotiate every task | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-023](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/22) | Joint-goal persistence with explicit reconsideration | TEAMWORK_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-024](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/23) | Partial SharedPlans and capability-directed collaboration | TEAM_PLANNING_MODEL | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-025](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/24) | Public conditional commitments | SOCIAL_PROTOCOL_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-026](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/25) | Commitment alignment and bounded delegation | LIFECYCLE_PROTOCOL_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-027](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/26) | Team monitoring, notification and repair | FEEDBACK_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-028](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/27) | Selective decision-theoretic communication | COMMUNICATION_POLICY | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-029](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/28) | Full mutual belief is mandatory for all cooperation | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-030](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/29) | Strategic model and solution-concept selection | MODELLING_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-031](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/30) | Incentive-compatible reporting mechanisms | MECHANISM_DESIGN_OPTION | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-032](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/31) | Participation, budget and efficiency feasibility | FEASIBILITY_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-033](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/32) | Equilibrium, welfare, fairness and legitimacy remain distinct | INTERPRETIVE_INVARIANT | STRONGLY_RETAINED | EXAMINED |
| [EMAS-034](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/33) | Deviation, collusion and opponent-shift testing | ADVERSARIAL_EVALUATION_METHOD | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-035](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/34) | Contract and coalition search scope limits | NEGOTIATION_SEARCH_PROPERTY | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-036](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/35) | Couple organisational structure, function and norms | ORGANISATIONAL_MODEL | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-037](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/36) | Norm declaration, detection and enforcement are distinct | NORMATIVE_INVARIANT | STRONGLY_RETAINED | EXAMINED |
| [EMAS-038](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/37) | Select regimentation, enforcement or voluntary norm reasoning | NORM_IMPLEMENTATION_ALTERNATIVES | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-039](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/38) | Role adoption and capability/permission compatibility | ADMISSION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-040](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/39) | Organisational revision with continuity constraints | REVISION_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-041](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/40) | Computational institution versus external legitimacy | AUTHORITY_BOUNDARY | STRONGLY_RETAINED | EXAMINED |
| [EMAS-042](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/41) | Role charts alone establish organisation | CEREMONIAL_SUBSTITUTE | CEREMONY_NOT_GENERAL_PROPERTY | EXAMINED |
| [EMAS-043](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/42) | Distributed constraint satisfaction under explicit transport and search assumptions | DISTRIBUTED_REASONING_ALGORITHM | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-044](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/43) | Exact DCOP quality versus structural resource cost | OPTIMISATION_ALGORITHM_FAMILY | DOMAIN_SPECIFIC | EXAMINED |
| [EMAS-045](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/44) | Privacy as a protocol-level disclosure property | INFORMATION_PROTECTION_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-046](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/45) | Argument acceptability relative to an explicit semantics | COLLECTIVE_REASONING_MODEL | CONTEXT_DEPENDENT | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-047](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/46) | Voting with explicit domain and manipulation limits | COLLECTIVE_CHOICE_MECHANISM | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-048](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/47) | Evidence provenance and dependence-aware aggregation | EVIDENCE_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-049](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/48) | Consensus establishes factual truth | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-050](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/49) | Non-stationarity-sensitive learning evaluation | LEARNING_EVALUATION_METHOD | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-051](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/50) | Centralised training with decentralised execution information contract | LEARNING_ARCHITECTURE | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-052](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/51) | Collective credit assignment and reward alignment | LEARNING_OBJECTIVE_MECHANISM | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-053](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/52) | Local-to-joint value factorisation under representational restrictions | FORMAL_LEARNING_PROPERTY | ASSUMPTION_SENSITIVE | EXAMINED |
| [EMAS-054](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/53) | Unseen-partner and cross-play evaluation | GENERALISATION_METHOD | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-055](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/54) | Emergent conventions are evaluated, not presumed legitimate norms | EMERGENCE_INTERPRETATION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-056](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/55) | Individual policy improvement guarantees collective progress | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-057](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/56) | Explicit simulation-to-deployment transfer claim | TRANSFER_CRITERION | STRONGLY_RETAINED | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-058](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/57) | Failure, deception and common-mode threat model | THREAT_MODELLING_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-059](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/58) | Recovery from abandoned obligations | RECOVERY_MECHANISM | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-060](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/59) | Risk-limited trust and reputation | PARTNER_SELECTION_MECHANISM | USEFUL_BUT_EASILY_GAMED | EXAMINED |
| [EMAS-061](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/60) | Collective progress separate from local compliance | LIVENESS_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-062](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/61) | Coordination-layer failure and fallback | ROBUSTNESS_CONFIGURATION | CONTEXT_DEPENDENT | EXAMINED |
| [EMAS-063](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/62) | Open membership and version-compatible admission | ADMISSION_AND_CHANGE_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-064](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/63) | Unrestricted communication guarantees robustness | OVERGENERALISATION | REJECTED_OR_DISFAVOURED | EXAMINED |
| [EMAS-065](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/64) | Matched-budget and credible simpler baselines | COMPARATIVE_EVALUATION_METHOD | STRONGLY_RETAINED | EXAMINED |
| [EMAS-066](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/65) | Mechanism-level translation of LLM collectives | TRANSLATION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-067](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/66) | Multi-seed, task, population and version evaluation | EMPIRICAL_METHOD | RETAINED_IN_EVOLVED_FORM | EXAMINED |
| [EMAS-068](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/67) | Mixed human-agent participation and decision boundaries | SOCIO_TECHNICAL_INTERACTION_CRITERION | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-069](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/68) | End-to-end collective consequence evaluation | OUTCOME_CRITERION | STRONGLY_RETAINED | EXAMINED |
| [EMAS-070](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/69) | Deployment, adoption and causal benefit are separate evidence | EVIDENCE_INTERPRETATION_CRITERION | STRONGLY_RETAINED | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-071](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/70) | Observation–obligation–action closure | COMPOSITION_INDUCED_INVARIANT | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-072](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/71) | Regime-change guards and explicit handoff | COMPOSITION_INDUCED_REVISION_RULE | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-073](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/72) | Minimum adequate coordination with omission and retirement | COMPOSITION_INDUCED_SELECTION_RULE | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-074](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/73) | Dependency-coupled adaptation | COMPOSITION_INDUCED_FEEDBACK_RULE | RETAINED_IN_EVOLVED_FORM | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-075](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/74) | Fault-model-specific replicated optimisation | FAULT_TOLERANT_ALGORITHM | DOMAIN_SPECIFIC | EXAMINED_WITH_EVIDENCE_LIMIT |
| [EMAS-076](EVOLVED_MULTI_AGENT_SYSTEMS_PROPERTY_LEDGER.json#/properties/75) | Norm-aware plan augmentation and deliberation | AGENT_NORM_REASONING_MECHANISM | DOMAIN_SPECIFIC | EXAMINED_WITH_EVIDENCE_LIMIT |

No exact duplicate or whole-candidate supersession was adjudicated. Similar concerns remain distinct where triggers, semantic objects or prerequisites differ. In particular, EMAS-016 is the lifecycle of a task; EMAS-069 evaluates the collective consequence. EMAS-058 defines the threat; EMAS-075 is a specific replicated optimiser. EMAS-037 concerns enforcement; EMAS-076 concerns norm-related plan choice. Zero counts in unused disposition categories are not evidence of forgotten candidates.

## EVOLVED_MULTI_AGENT_SYSTEMS_DOMAIN_MODELS

These models are coupled views, not ten mandatory subsystems. A view is useful only where its objects and consumer exist. Each property’s `DOMAIN_PROFILE` binds the shared dimensions below to the actual candidate. No notation is attributed to a source merely because this report uses it to expose a dependency.

### Population and interdependence

An analytical population model identifies included agents A, external principals, environment objects, each agent’s observations and available actions, and the interdependencies among contributions. A dependency may be a shared resource, a necessary handover, a private-information trade, a joint timing condition or an obligation. If removing a proposed agent leaves all required capability and rights intact at lower cost, the decomposition has not yet earned its place. This model distinguishes genuinely separate control from artificial role proliferation. [EMAS-001–006; sources EMAS-S001, EMAS-S004, EMAS-S045]

### Communication semantics

Represent an interaction by its participants, identity/bindings, local histories and the agreed informational or social effects of messages. Sending, delivery, interpretation, acceptance and consequence are separate relations. Mental-state semantics can be selected inside a justified inspectable model; public commitment/information semantics can be selected at an opaque boundary. Neither creates evidence for an unobserved world event by itself. Protocol “liveness” must be labelled with the exact definition being used. [EMAS-007–014; EMAS-S013, EMAS-S014, EMAS-S016, EMAS-S044]

### Task coordination

A task model identifies task identity, required capability, resource/time constraints, proposed assignment, acceptance and evidence of execution/completion. Economic models may add cost, bundle interaction and withdrawal conditions. A joint assignment can be feasible on paper yet not enacted. Where a dependency can be eliminated by bundling or resource separation, that is an alternative to repeated negotiation rather than a failure to implement MAS. [EMAS-015–022; EMAS-S004, EMAS-S006, EMAS-S045, EMAS-S046]

### Cooperation and commitments

A team model describes a shared undertaking and the circumstances that make persistence, notification or repair appropriate. A public commitment model instead describes a debtor, creditor, conditions and consequences recognised by the selected semantics. The synthesis keeps these objects distinct. A team can use public commitments at its boundary; that coupling needs a justified mapping from intended contribution to public obligation and then to evidence. Cancellation, delegation and fulfilment cannot all be represented as deletion of a task row without losing responsibility. [EMAS-023–029; EMAS-S007–011, EMAS-S044]

### Strategic interaction

The strategic model declares utilities or preferences, information, allowed strategies, participation, transfers and the equilibrium or mechanism property under assessment. Truthfulness, efficiency, individual rationality and fairness are separate predicates. The model also records who is absent from the objective and which deviations were not considered. A cooperative cost optimisation can be selected only when the actual participants satisfy its behavioural assumptions, or a separate mechanism makes the needed reporting property defensible. [EMAS-030–035; EMAS-S023–025, EMAS-S040]

### Organisations and norms

A role model links responsibilities and permissions to adoption and capability. A mission/goal model describes contribution dependencies. Norms add conditions and normative consequences; an institutional model specifies which events can be observed and which effects it can impose. External authority and contested facts remain interfaces to real participants and institutions. Norm-aware planning is an optional actor-level integration, not proof that all violations are prevented. [EMAS-036–042, EMAS-076; EMAS-S018–022, EMAS-S050, EMAS-S052]

### Distributed reasoning

For CSP/DCOP, distinguish the formal variables/domains/constraints or objective from where data and decisions reside, the algorithm’s message model, complexity and any privacy definition. For argumentation and voting, distinguish the decision object and semantics from the evidence warranting input assertions. Combining outcomes from these procedures does not create an independent observation of truth. The actual reasoning model may be central, distributed, exact, bounded-quality or deliberately minimal. [EMAS-043–049; EMAS-S025–031]

### Adaptation and emergence

A learning model records local observations, training-only information, rewards, partner population, update rules and evaluation distributions. A global criterion remains separate from local training objectives. Population change, strategy learning, context adaptation and institutional rule change are different events. An observed convention can be stabilising without being desirable. A revision must be judged against dependent partners and resources, not solely its local reward. [EMAS-050–057, EMAS-074; EMAS-S032–035, EMAS-S039–040]

### Collective failure

A failure model distinguishes unavailability, communication faults, deception, strategic deviation, arbitrary corruption and shared bad knowledge. It identifies what can be observed, what is trusted and what the collective must preserve. Recovery must account for work that might already have occurred. Replication may preserve an algorithm under one corruption model without protecting its objective or fixing a coordinator’s common dependency. Useful progress and actual completion need their own observations. [EMAS-058–064, EMAS-075; EMAS-S009, EMAS-S016, EMAS-S043–044, EMAS-S049, EMAS-S051]

### Evaluation and modern translation

An evaluation model identifies the unit of comparison, total relevant resources, information/tool access, training/inference distinction, tasks, seeds, partners, versions, judges, uncertain outcomes and shared evidence ancestry. Human participation adds usability and real control, not just a user-interface label. LLM mechanisms must be mapped to these actual objects before inheriting classical terminology. A benchmark score, a field trial and deployment evidence answer different questions. [EMAS-065–070; EMAS-S035–043, EMAS-S048, EMAS-S054]

### Complete domain-profile dimensions

The ten dimensions below are instantiated for every candidate, including non-retained candidates. Shared profiles are not substitutes for candidate-specific applications; a JSON Pointer and its `APPLICATION` must be read together.

#### MAS1 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Candidate system includes autonomous decision loci and the environment they affect; a service collection is not assumed to be a MAS merely because it is distributed.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Classify common-purpose, mixed-motive and competitive participation before importing cooperation or utility assumptions.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Identify who knows each relevant fact, controls each action and bears consequences; physical distribution does not imply equal authority.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Specify which dependencies require messages and whether a fixed direct interface suffices; natural language is optional.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Decomposition is justified by genuine capability, information, resource, ownership or strategic interdependence, not agent count.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** Authority may remain central even where observation and execution are distributed; rights are separate from technical access.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Assess the collective task, not an aggregate of unrelated local successes; compare alternative decompositions.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Changing population or capabilities can invalidate a once-useful partition and require reassessment.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Common models, data, networks and controllers remain correlated failure sources after decomposition.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Comparator includes one capable agent, a scheduler and deterministic distributed services, matched to the same work and information.

#### MAS2 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Communicating participants may be heterogeneous and internally opaque; observers see message histories, not private beliefs.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Message sincerity and protocol compliance are assumptions or separately evidenced behaviours, never consequences of a performative name.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Each party has a local observation sequence; an omniscient shared transcript is not the default execution model.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Separate transport, syntax, ontology, conversation identity, information causality and social effects; choose a stated semantic profile.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** A message may propose, create or report an obligation; none of these automatically performs the underlying task.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** An institution or agreement determines who may create, release or delegate obligations; language syntax alone does not.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Local admissibility must be related to enactability, alignment or completion possibility under the selected semantics.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Joining parties and changed ontologies need compatible interpretation and treatment of in-flight conversations.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Delivery failure, duplicate or reordered messages, false reports and shared misunderstandings require distinct handling assumptions.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Measure interoperability by correct consequential interaction; include translation, verification and conversation-state costs.

#### MAS3 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Workers, managers or peer allocators control tasks and resources; granularity may be dispatch-centre rather than vehicle or primitive action.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Cooperative cost minimisation differs from privately profitable bidding; truthfulness is not supplied by an auction-shaped exchange.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Capabilities, workloads and marginal task costs may be local; central scheduling is an admissible alternative when rights and information allow it.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Announcements, bids, awards, withdrawals and completion reports need task correlation and agreed acceptance semantics.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Task bundles, precedence, outstanding offers, deadlines and shared resources change feasible allocations and costs.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** An award cannot grant permissions that the awarding party lacks; subcontracting and resource transfer have explicit limits.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Allocation quality and actual completed work are separate properties; local cost decreases need not resolve external resource conflicts.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** New tasks, departed workers and stale bids require expiry, reconsideration or replanning under an explicit responsibility model.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Lost workers, deceptive bids and concurrent acceptance can strand or duplicate work; a shared allocator may itself fail.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Count planning, negotiation, waiting and execution together; compare central or direct allocation and dependency elimination.

#### MAS4 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** A team has identifiable participants and a joint activity; an observer grouping independent agents does not create membership commitments.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Joint-intention and SharedPlans accounts normally presume cooperative commitments, with rules for legitimate reconsideration.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Partial plans and local beliefs are permitted; what others must learn about changed circumstances is an explicit obligation.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Team communication can notify achievement, impossibility, irrelevance, delegation or repair; some changes require recipients rather than broadcast.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Intentions, public conditional commitments and actual performance are distinct objects that may be coupled but not equated.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** Create, delegate, cancel and release have different actors; becoming aware of failure does not automatically authorise abandoning another party.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Collective persistence must coexist with achievable completion, repair and justified termination; local good intentions are insufficient.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Goal changes and partner departures can trigger commitment reconsideration; continuation under obsolete assumptions can harm the team.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Silent abandonment, stale commitment views and unverifiable completion remain possible outside the theory’s behavioural assumptions.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Compare selective communication and partial planning with their cost; teamwork simulations do not establish all-domain superiority.

#### MAS5 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Strategic agents represent distinct decision makers, possibly with private values and outside options; a cooperative benchmark is a different population.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** State utility, rationality, equilibrium concept, information, transfers and participation assumptions; ethical value is not identical to utility.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Types, bids and feasible allocations have specified visibility; an economic planner may be central without removing strategic interdependence.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Bids and offers are strategic messages within a mechanism, not automatically accurate statements of need or cost.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Allocation, payments, coalition formation and contract enforcement determine whether locally preferred actions support an objective.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** Institutional permission and enforceable transfers must exist independently of equilibrium analysis; sanctions are not legitimate by optimisation alone.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Incentive compatibility, efficiency, individual rationality, budget balance and fairness are distinct, sometimes incompatible requirements.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Entry, changing learning rules or a new opponent distribution can change equilibrium selection and stability.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Collusion, non-modelled objectives, deception, incomplete computation and refusal to comply can defeat predicted behaviour.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Evaluate welfare distribution, exploitability, solution-selection cost and computation; distinguish toy price games from real markets.

#### MAS6 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Organisations contain role players, organisational artefacts and possibly external human institutions; closed simulated institutions have narrower control.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Agents may reason about norms or merely be constrained by infrastructure; compliance and shared goals are separate.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Role specifications, local plans and institutional facts reside at different levels and need explicit access boundaries.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Role adoption, mission acceptance, normative changes and violations have identifiable communicative or environmental evidence.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Structural roles, functional goals and normative obligations must be linked where they jointly govern work.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** Capability, permission, obligation, enforcement and external legitimacy are separate predicates; a plan’s violation option is not an ethical endorsement.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Permitted local transitions must be connected to organisational objectives and recovery, not only a well-formed role diagram.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Reorganisation can change roles, missions or rules; existing obligations and affected participants constrain the transition.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Off-platform acts, incomplete observation, norm conflict and self-serving monitors can defeat declared regulation.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Assess compliance costs, lost flexibility, enforcement error and participation burden; prototypes are not proof of real institutional legitimacy.

#### MAS7 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Agents hold variables, constraints, arguments, preferences or observations; the object being aggregated must be stated before choosing an algorithm.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** DCOP commonly assumes cooperative objective evaluation; voting may instead face strategic preference reports.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Variable ownership and graph structure determine information requirements; preserving local storage does not automatically preserve privacy.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Constraint, utility, vote or argument messages have formally stated interpretations and transport assumptions.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Coupled constraints and mutually attacking arguments create interdependence; factual corroboration additionally depends on evidence provenance.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** A solution, acceptable extension or vote winner does not grant authority to implement it.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Completeness, optimality, acceptance and agreement refer to different models and should not be exchanged as guarantees.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Changing constraints, participants or objectives invalidate static-model assurances unless the update mechanism is analysed.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Incorrect utility messages, shared source errors, strategic votes and knowledge leakage are distinct threats.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Include induced width, computation, bytes, disclosure and solution quality; algorithmic cycle counts are not end-to-end latency.

#### MAS8 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Learning populations may be fixed teams, competitive opponents or changing partners; state which agents and environment dynamics are adapted.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Local reward, team return and social welfare need not coincide; a simulator’s reward is an authored objective.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Centralised training may use joint state/actions unavailable to decentralised execution; this is an information contract, not a deployment privilege.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Learned signalling or text communication must be tested for partner-compatible meaning and overhead, not assumed from fluency.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Joint rewards, credit assignment and resource dependencies couple learning across agents and time.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** A learning update can change behaviour but cannot itself confer permission to revise institutional rules.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Policy improvement, factorisation consistency and desirable emergence are different claims; test the collective trajectory.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Other learners change the effective environment; cross-play and unseen-partner tests target failures hidden by self-play.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Non-stationarity, correlated policies, exploitative equilibria and reward misspecification can produce collective failure.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Evaluate seeds, tasks, partner populations, observation constraints and training cost; simulation-to-deployment transfer remains a separate claim.

#### MAS9 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Open populations may depart, be replaced, misbehave or share infrastructure; membership and identity assumptions are explicit.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Accidental failure, rational defection and arbitrary malicious behaviour require different response models.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Observers may suspect failure without knowing whether another agent is slow; recovery must account for hidden ongoing work.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Failure notices, state reconciliation and retry messages require correlation; network partitions do not create new authority.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Recovery handles outstanding tasks, commitments and resources, not merely restarting processes.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** Reassignment and quarantine must stay within the designated parties’ powers; reputation is evidence for a bounded decision, not a universal licence.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Local compliance, availability and collective progress are checked separately; fault tolerance is scoped to a stated invariant.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Admission, software changes and repaired participants can alter evidence and fault assumptions.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Common-mode errors, colluding actors and abandoned obligations are not neutralised by naming more agents.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Measure degradation and recovery cost, false suspicion and failure-layer bottlenecks; redundancy is justified against a specific threat.

#### MAS10 shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** Evaluated collectives may be software-only, LLM-based, human-agent or mixed; population and task sampling are explicit.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** An evaluation contract specifies useful outcomes, costs and unacceptable harms; benchmark score is not institutional approval.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Baselines receive comparable information, tools and budgets; different access conditions must be reported rather than hidden.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Trace review separates valid messages, consequential understanding and actual progress; shared prompts and models create evidence dependence.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Coordination-specific outcomes must be separable from base-model competence and isolated task completion.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** Humans retain whatever decision rights the external setting establishes; an evaluation does not transfer them to the system.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** End-to-end outcomes and uncertainty qualify local or benchmark success; one programme does not provide independent replications.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Changing models, prompts, partners and APIs require versioned evaluation; historical benchmarks do not certify later versions.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Correlated judging, selected tasks, omitted failures and missing ground truth limit inference even from large trace collections.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** Compare matched reasoning, tool, latency and cost budgets and disclose unavoidable mismatches; include simpler non-agent alternatives.

#### COMPOSED shared profile

**AGENT_POPULATION_AND_SYSTEM_BOUNDARY:** The analytical system is a conditional configuration of actual decision participants, task objects, commitments, protocols and external interfaces.

**GOAL_ALIGNMENT_AND_INCENTIVE_ASSUMPTIONS:** Cooperative, strategic, normative and learning branches retain different assumptions rather than being forced into one unanimous utility model.

**INFORMATION_AND_CONTROL_DISTRIBUTION:** Each composition boundary identifies who may observe, decide and act; no omniscient central state is presumed.

**COMMUNICATION_AND_PROTOCOL_SEMANTICS:** Communication couples local evidence to relevant consumers and actions; successful reporting is not successful operation.

**TASK_COMMITMENT_OR_RESOURCE_INTERDEPENDENCE:** Relations connect tasks, commitments, resources, objectives and revision dependencies without requiring every candidate mechanism.

**ORGANISATIONAL_AUTHORITY_AND_NORMS:** External principals and participants supply authority; the composed model grants no rights and cannot warrant its own adoption.

**GLOBAL_PROPERTY_AND_LOCAL_COMPOSITION:** Whole-system properties arise from specific coupling and remain analytical until tested; constituent evidence alone does not validate the composition.

**DYNAMIC_MEMBERSHIP_LEARNING_AND_NONSTATIONARITY:** Changed membership, incentive regime or policy invalidates dependent assumptions and triggers scoped reconsideration, not automatic global redesign.

**FAILURE_DECEPTION_AND_COMMON_MODE_ASSUMPTIONS:** Observation gaps, incompatible guarantees and coordination-layer failures can defeat the entire composition despite locally correct parts.

**COLLECTIVE_EVALUATION_AND_COORDINATION_COST:** The minimum adequate configuration competes with simpler alternatives; total coordination cost and outstanding uncertainty remain visible.


## EVOLVED_MULTI_AGENT_SYSTEMS_CEREMONY_STRIPPING_LEDGER

Every candidate has an individual cheaper-path and omission/retirement examination in its JSON record. The following cross-cutting artefacts illustrate how simplification preserves a function rather than merely deletes documentation. These are analytical judgements about sourced mechanisms, not claims that the sources coined an “anti-ceremony” doctrine.

### EMAS-Z001 — Many named agents or specialists

**Protected properties / consumer:** EMAS-001; EMAS-006; EMAS-073; Recipient of the collective outcome.

**Failure and prerequisites:** Artificially fine-grained workers add negotiation and translation costs; a biased baseline manufactures benefit.; Serial bottlenecks, correlated errors and context fragmentation can worsen outcomes. A defined task, explicit rights and comparable information/cost accounting.; Comparable task, information and total resource budget.

**Minimum and escalation:** One actor, a scheduler or ordinary services with the necessary rights and information. Fuller form: Irreducibly separate capabilities, information, incentives or control.

**Simplification cost / retirement:** May lose parallelism, autonomy or unique capabilities. Remove the extra agent when its contribution disappears and obligations can be transferred. [EMAS-S001; EMAS-S037; EMAS-S041]

### EMAS-Z002 — Performatives, role prompts and ontology documents

**Protected properties / consumer:** EMAS-007; EMAS-008; EMAS-012; EMAS-014; Actual message recipient and obligation counterparty.

**Failure and prerequisites:** Correct parsing can mask different meanings of task, completion or permission.; Public records can still be false about the world or too coarse to establish fulfilment. Both sides can map fields and effects to the same declared interpretation.; Agreed event interpretation, participant identities and observable messages or consequences.

**Minimum and escalation:** A small agreed vocabulary and explicit effects for the interaction. Fuller form: Heterogeneous open participants or many evolving message types.

**Simplification cost / retirement:** Less expressive semantics may reduce interoperability or detect fewer errors. Omit unused vocabularies; preserve bindings relied upon by live conversations. [EMAS-S012; EMAS-S013; EMAS-S014]

### EMAS-Z003 — Full conversation diagrams and protocol verification

**Protected properties / consumer:** EMAS-010; EMAS-011; EMAS-061; Implementers and participants who rely on legal interaction.

**Failure and prerequisites:** Correct sequencing with the wrong task identifier remains an unsafe interaction.; Completion possibility is confused with actual eventual willingness, delivery or fulfilled work. Identity binding, data integrity and local history sufficient for the selected protocol.; Finite or analysable protocol state; valid information assumptions and a specified environment model.

**Minimum and escalation:** A direct protocol with a few explicit information dependencies. Fuller form: Concurrency, open enactment or costly dead ends justify formal analysis.

**Simplification cost / retirement:** Manual reasoning may miss reachable dead ends. Retire unused protocol branches only after in-flight interactions are resolved. [EMAS-S016; EMAS-S044]

### EMAS-Z004 — Contract Net bidding on every task

**Protected properties / consumer:** EMAS-015; EMAS-016; EMAS-017; EMAS-022; Allocator and affected workers.

**Failure and prerequisites:** Stale bids, hidden costs and interacting tasks make a locally cheap award infeasible.; Premature completion, abandoned awards and duplicate execution on retry. Comparable suitability criteria, current capacity and an agreed award/acceptance protocol.; Task identity, completion criterion, responsible parties and an observation path.

**Minimum and escalation:** Direct authorised assignment or a simple posted offer. Fuller form: Uncertain suitability, consent or material alternative costs.

**Simplification cost / retirement:** May miss a better or willing provider. Drop bidding when allocation is predetermined and comparison confirms no lost value. [EMAS-S004; EMAS-S045; EMAS-S046]

### EMAS-Z005 — Complete shared plans and constant team meetings/messages

**Protected properties / consumer:** EMAS-023; EMAS-024; EMAS-027; EMAS-028; Contributors whose actions depend on others.

**Failure and prerequisites:** Stubborn persistence under harmful goals; cost-prohibitive attempts to establish ideal mutual belief.; Unrecognised resource conflict and incomplete monitoring remain outside a purely intentional specification. Joint objective, participant set, persistence conditions and a viable notification path.; Understandable action recipes, relevant capabilities and reconciliation of subplan obligations.

**Minimum and escalation:** Partial plans and event-relevant notifications. Fuller form: Critical dependencies, uncertainty or failure consequences justify richer shared state.

**Simplification cost / retirement:** Insufficient disclosure can hide conflicts or obsolete assumptions. Remove meetings/updates that no longer change an action or expectation. [EMAS-S008; EMAS-S009; EMAS-S010; EMAS-S054]

### EMAS-Z006 — Role charts and large organisational models

**Protected properties / consumer:** EMAS-036; EMAS-039; EMAS-042; Participants assigning and accepting missions.

**Failure and prerequisites:** Well-formed diagrams conceal missing performers or unreachable organisational goals.; A title persists after capability loss; permissions are broader than actual assignment. Interpretable goals, role definitions and a mechanism linking role adoption to actual responsibilities.; Current capabilities, identity, compatibility rules and an authorised assignment process.

**Minimum and escalation:** A few explicit roles, permissions and task relations. Fuller form: Open roles, complex mission dependencies or institutional obligations.

**Simplification cost / retirement:** Too little structure can hide incompatible roles or unclear accountability. Retire models with no decision consumer, preserving necessary responsibilities. [EMAS-S018; EMAS-S019; EMAS-S050]

### EMAS-Z007 — Norm text, sanction labels and human approval boxes

**Protected properties / consumer:** EMAS-004; EMAS-037; EMAS-038; EMAS-041; EMAS-068; Affected participants and legitimate decision makers.

**Failure and prerequisites:** Powerful tools bypass the intended decision maker; formal norms are mistaken for legal authority.; Unseen external acts and ambiguous rules render a norm operationally inert or falsely enforced. Named action/resource and an identifiable source of authority.; Norm meaning, observable facts, legitimate response powers and a fallible-observation policy.

**Minimum and escalation:** A usable constraint or decision rule with an observable action and real authority. Fuller form: Violations must be detected/contested or meaningful discretion exercised.

**Simplification cost / retirement:** Removing records may impair contestation and accountability. Do not retain unenforceable or authority-free observance as proof of control. [EMAS-S020; EMAS-S021; EMAS-S022; EMAS-S043; EMAS-S054]

### EMAS-Z008 — Universal auctions, voting or equilibrium claims

**Protected properties / consumer:** EMAS-030; EMAS-031; EMAS-032; EMAS-033; EMAS-047; Participants in a real allocation/preference decision.

**Failure and prerequisites:** One computed equilibrium is non-unique, inaccessible or irrelevant to bounded actors.; Collusion, externalities, non-modelled values, approximate computation or unenforceable payments defeat the claim. Feasible actions, payoffs or preference model, information and participation assumptions.; Declared type domain, transfer powers, utility assumptions and the exact equilibrium or dominance condition.

**Minimum and escalation:** Direct agreement, restricted-domain choice or a simpler authorised rule. Fuller form: Private information or divergent preferences create a genuine mechanism-design problem.

**Simplification cost / retirement:** Simpler rules can reduce participation, efficiency or resistance to manipulation. Omit formal mechanism machinery when no strategic choice requires it. [EMAS-S023; EMAS-S024; EMAS-S025]

### EMAS-Z009 — Exact distributed optimisation everywhere

**Protected properties / consumer:** EMAS-043; EMAS-044; EMAS-045; EMAS-075; Resource/assignment decision maker.

**Failure and prerequisites:** Dropped messages, false constraints or changed variables invalidate completeness claims.; Exponential messages, stale objectives or incomplete utility specification erase practical value. Finite domains, identified neighbours/agents and the algorithm’s reliable ordered-delivery assumptions.; Finite DCOP, correct utility/cost functions, compatible ownership and algorithm-specific transport.

**Minimum and escalation:** Central computation, decomposition or bounded-quality search. Fuller form: Distributed information/rights, quality requirements or privacy/fault needs justify it.

**Simplification cost / retirement:** Approximation or centralisation may sacrifice required guarantees or privacy. Retire expensive distribution when its protected constraint disappears. [EMAS-S026; EMAS-S027; EMAS-S028; EMAS-S029; EMAS-S051]

### EMAS-Z010 — Debate rounds, majority votes and multiple judges

**Protected properties / consumer:** EMAS-048; EMAS-049; EMAS-065; EMAS-066; Consumer of a factual decision.

**Failure and prerequisites:** Unknown shared training or hidden data reuse prevents reliable independence estimates.; All agents share one mistaken premise or one persuasive but false explanation. Provenance sufficient to distinguish shared sources from genuinely distinct observations.; The rejected claim would require a defensible error/independence model and truthful evidence, not just agreement.

**Minimum and escalation:** Independent evidence checks or a single capable agent with the same resources. Fuller form: A tested complementary information/error structure produces net improvement.

**Simplification cost / retirement:** Reducing diversity may remove genuine correction opportunities. Stop rounds without new independent evidence or outcome gain. [EMAS-S036; EMAS-S037; EMAS-S048]

### EMAS-Z011 — Continuous learning or autonomous reorganisation

**Protected properties / consumer:** EMAS-040; EMAS-050; EMAS-054; EMAS-074; Partners affected by changes.

**Failure and prerequisites:** Self-revision conceals self-authorisation; redesign cannot fix an impossible external goal.; A policy improves against an obsolete partner or destabilises mutual adaptation. Change authority, assessment criterion, current obligation state and an implementation path.; Declared update schedules, partner populations and evaluation horizon.

**Minimum and escalation:** Stable policy/protocol plus bounded explicit revision. Fuller form: Drift or new tasks demonstrably make the fixed system inadequate.

**Simplification cost / retirement:** A fixed policy may respond too slowly to changed circumstances. Retire adaptation with no persistent collective gain or controllable interface. [EMAS-S032; EMAS-S034; EMAS-S050; EMAS-S052]

### EMAS-Z012 — Reputation dashboards and blanket redundancy

**Protected properties / consumer:** EMAS-058; EMAS-060; EMAS-062; EMAS-075; Party bearing the next exposure.

**Failure and prerequisites:** Multiple role names conceal one model or one compromised information source.; Con strategies rebuild reputation before costly defection; strict penalties punish noisy honest actors. A stated invariant, fault scope, trusted components and observation limits.; Identity continuity, relevant observations and an explicit model of noise and strategic manipulation.

**Minimum and escalation:** A bounded direct check, narrow redundancy or explicit safe suspension. Fuller form: Repeat interaction or a specified fault warrants the added mechanism.

**Simplification cost / retirement:** May lose availability or useful historical risk information. Retire scores/replicas that lack predictive/protective value under the actual threat model. [EMAS-S049; EMAS-S051]


## EVOLVED_MULTI_AGENT_SYSTEMS_CRITICISM_LEDGER

Criticism has changed dispositions and configuration selection. It has not been confined to obsolete practices or conveniently pro-synthesis objections. In particular, EMAS-K018 challenges a negative MAS argument, while EMAS-K019 preserves evidence that communication can be indispensable. Source-grounded criticism is distinguished from the researcher’s inference or counterexample.

### EMAS-K001 — EMAS-001; EMAS-006; EMAS-019; EMAS-022; EMAS-073

**Strongest objection:** Coordination may consume more value than it creates.

**Evidence and locator:** Both reports expose structure-dependent overhead rather than universal team superiority. [EMAS-S006; EMAS-S041]; PGP experiments; 2026 specialist simulation §§2–3.

**Response / current judgement:** Choose granularity, selected information and direct alternatives. Reject monotonic agent count and compulsory negotiation; retain conditional decomposition.

**Residual uncertainty:** A simplified design may still lose capability under untested workloads. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K002 — EMAS-007; EMAS-008; EMAS-009; EMAS-014

**Strongest objection:** Opaque mental-state semantics cannot serve as a universal public compliance test.

**Evidence and locator:** Private belief/sincerity is unavailable to an external party merely receiving messages. [EMAS-S013; EMAS-S014]; Singh pp.40–47; FIPA experimental semantics.

**Response / current judgement:** Social commitments and observable information effects provide a different semantic object. Retain both branches conditionally, not mental-state semantics as a universal standard.

**Residual uncertainty:** The bridge from public obligation to actual intention remains contingent. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K003 — EMAS-010; EMAS-011; EMAS-012; EMAS-061

**Strongest objection:** A protocol can offer a completion without making it occur.

**Evidence and locator:** The formal liveness definition concerns legal completions from reachable enactments. [EMAS-S016]; BSPL §3.5.

**Response / current judgement:** Pair model checks with environment/participant assumptions and useful-progress observation. Reject the inference from protocol liveness to real completed work.

**Residual uncertainty:** Termination or recovery thresholds can misclassify slow but useful work. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K004 — EMAS-013; EMAS-063

**Strongest objection:** Historical standardisation does not establish current compatibility.

**Evidence and locator:** Only the identified experimental communicative-act library was readable. [EMAS-S014; EMAS-S015; EMAS-S053]; XC00037H cover; unsuccessful final-version retrievals.

**Response / current judgement:** Keep exact version identity and ask for runtime-specific conformance evidence. Current FIPA equivalence remains UNRESOLVED, not disproved.

**Residual uncertainty:** Final texts, current implementations and adoption prevalence remain access/evidence limits. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K005 — EMAS-015; EMAS-016; EMAS-017; EMAS-035

**Strongest objection:** An award need not mean acceptance or performance, and local trades can miss globally valuable bundles.

**Evidence and locator:** The mechanisms address allocation/search under specified cost and contract structures. [EMAS-S004; EMAS-S045; EMAS-S046]; Contract connection; TRACONET bargaining; contract types.

**Response / current judgement:** Separate lifecycle evidence and enlarge exchange neighbourhoods only when justified. Retain allocation conditionally; no general truthful or globally optimal Contract Net claim.

**Residual uncertainty:** Real cost misreports, external resource effects and execution failures remain possible. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K006 — EMAS-023; EMAS-024; EMAS-027; EMAS-029

**Strongest objection:** Ideal collective beliefs are costly, and formal plans do not by themselves monitor real action.

**Evidence and locator:** Incomplete plans and communication uncertainty leave coordination obligations. [EMAS-S008; EMAS-S009; EMAS-S047]; SharedPlans pp.307,334–336; STEAM; common knowledge analysis.

**Response / current judgement:** Operational monitoring and selective notification supplement, rather than redefine, formal intention models. Reject full common belief as mandatory for every practical cooperative act.

**Residual uncertainty:** Weaker informational conditions retain residual coordination risk. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K007 — EMAS-021; EMAS-023; EMAS-059

**Strongest objection:** Persistence becomes harmful when goals or capabilities change; unrestricted withdrawal destroys predictability.

**Evidence and locator:** Commitment and reconsideration conventions address distinct functions. [EMAS-S011; EMAS-S046]; Jennings conclusions; decommitment discussion.

**Response / current judgement:** Specify agreed release/compensation and notify dependants. Decommitment remains context-dependent, not a universal automatic escape.

**Residual uncertainty:** Legal or economic enforceability of withdrawal terms requires separate evidence. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K008 — EMAS-031; EMAS-032; EMAS-033

**Strongest objection:** Desirable mechanism properties can be jointly infeasible.

**Evidence and locator:** The bilateral private-value theorem has specific independence, participation and budget premises. [EMAS-S024]; Model and efficiency result.

**Response / current judgement:** Narrow the domain or relax a named desideratum. Retain the feasibility boundary; reject an unqualified promise of truthful efficient voluntary budget-balanced trade.

**Residual uncertainty:** The theory does not decide whose losses are acceptable. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K009 — EMAS-030; EMAS-033; EMAS-034; EMAS-055

**Strongest objection:** Strategic stability can support collusive outcomes.

**Evidence and locator:** Repeated-pricing results are conditional on a finite meta-strategy and payoff model. [EMAS-S040]; Meta-game construction and restricted empirical games.

**Response / current judgement:** Test alternative strategies and evaluate welfare independently of equilibrium. Equilibrium and stable convention are not ethical or institutional warrants.

**Residual uncertainty:** The experiment does not estimate actual market incidence or cover every opponent. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K010 — EMAS-036; EMAS-037; EMAS-038; EMAS-041; EMAS-042

**Strongest objection:** Norms cannot be enforced when violations are unobservable or sanctions lack effect/authority.

**Evidence and locator:** The formal institutional environment assumes observable actions; the enforceability work identifies off-platform and grievance problems. [EMAS-S020; EMAS-S021]; Normative-program assumptions; enforceability §1.

**Response / current judgement:** Separate norm declaration, detection, prevention, sanction and external jurisdiction. Retain explicit enforcement boundaries, reject role-chart and norm-text sufficiency.

**Residual uncertainty:** Observation may remain partial or contested; legitimate enforcement may require external institutions. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K011 — EMAS-040; EMAS-072; EMAS-074

**Strongest objection:** Self-reorganisation can be costly and cannot fix every cause of failure.

**Evidence and locator:** An impossible goal is not repaired merely by changing organisation. [EMAS-S050]; Reorganisation phases and limitations.

**Response / current judgement:** Bound revision by observable cause, candidate evaluation and continuity of responsibilities. Reorganisation is context-dependent; the composed change guard is analytical rather than self-authorising.

**Residual uncertainty:** General stable autonomous institutional revision is not established. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K012 — EMAS-043; EMAS-044; EMAS-045

**Strongest objection:** Distributed optimisation may be expensive, leaky or inapplicable to unreliable/strategic execution.

**Evidence and locator:** Exactness is model-relative; DPOP complexity depends on induced width, and privacy is a protocol property. [EMAS-S026; EMAS-S027; EMAS-S028; EMAS-S029]; DCSP transport assumptions; ADOPT bounds; DPOP Theorem 1; privacy definitions.

**Response / current judgement:** Choose bounded quality, narrower decomposition or a central method and explicit privacy protection. Retain domain-bound guarantees, not generic decentralised optimality/privacy.

**Residual uncertainty:** Real objectives, communication time and attack models may violate the formal model. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K013 — EMAS-046; EMAS-047; EMAS-048; EMAS-049; EMAS-061

**Strongest objection:** Agreement and acceptability are not factual truth.

**Evidence and locator:** Voting restrictions concern strategy; argumentation depends on supplied graph semantics. The inspected dialogue additionally admits legally repetitive exchanges unless relevance and stopping assumptions hold. Public stores do not by themselves establish private rationality. [EMAS-S025; EMAS-S031; EMAS-S055; EMAS-S056]; Voting theorem; abstract argumentation semantics; EMAS-S055 §4.3 p.6; EMAS-S056 §§5–6.

**Response / current judgement:** Keep preference aggregation, dialectical status and evidence warrant distinct. Reject consensus-as-truth; retain the methods for their actual decision objects.

**Residual uncertainty:** Input warrant and the selected dialogue’s useful stopping remain independent burdens. The inspected branch is not a general multiparty negotiation guarantee. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K014 — EMAS-050; EMAS-051; EMAS-052; EMAS-053; EMAS-056

**Strongest objection:** Policies and partners co-adapt, and representational restrictions can exclude useful joint policies.

**Evidence and locator:** Controlled benchmarks and factored value models support bounded results only. [EMAS-S032; EMAS-S033; EMAS-S035]; MADDPG setting; QMIX monotonicity; 2025 benchmark.

**Response / current judgement:** Preserve execution information contracts and evaluate joint outcomes across settings. Reject local improvement as a general convergence/welfare guarantee.

**Residual uncertainty:** No general efficient solution for arbitrary open mixed-motive learning is established. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K015 — EMAS-054; EMAS-057; EMAS-068

**Strongest objection:** Self-play and simulation performance can fail with unseen people or partners.

**Evidence and locator:** Different conventions, resources, observations and participant expertise change the task. [EMAS-S034; EMAS-S038; EMAS-S043]; Other-Play cross-play; alem; staged field trials.

**Response / current judgement:** Cross-play and deployment-specific participant tests examine transfer. Retain transfer as a separate claim, not an automatic maturity stage.

**Residual uncertainty:** Finite partner samples do not cover an open population. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K016 — EMAS-048; EMAS-060; EMAS-058

**Strongest objection:** Trust can be rebuilt strategically before another defection.

**Evidence and locator:** Direct-trust simulations distinguish repeated con cycles from trustworthy service; the first con is not eliminated. [EMAS-S049]; Con-man model and §3 limitation.

**Response / current judgement:** Limit exposure and use appropriate direct evidence. Reputation is useful but easily gamed, not a completion certificate.

**Residual uncertainty:** Noise, new identities and costly false accusations remain concerns. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K017 — EMAS-065; EMAS-066; EMAS-067; EMAS-069

**Strongest objection:** LLM teams can fail through interactions even when individual outputs look plausible.

**Evidence and locator:** Grounded-theory and larger trace analyses identify distinct coordination/termination failure modes. [EMAS-S036]; MAST methods and failure taxonomy.

**Response / current judgement:** Inspect actual histories, failure units, judges and final consequences. Mechanism-level translation survives; slogans about societies or debate do not suffice.

**Residual uncertainty:** Selected frameworks/tasks do not establish production failure prevalence. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K018 — EMAS-001; EMAS-006; EMAS-065; EMAS-070

**Strongest objection:** The negative comparison overstates what its information argument proves.

**Evidence and locator:** Researcher counterexample: C has equally likely states with P(Y=1|C)=0.9 and 0.6; constant M loses mutual information but both Bayes errors are 0.25. [EMAS-S037]; §3 Theoretical justification, especially strict-inequality claim.

**Response / current judgement:** Bayes weak dominance follows by emulating an M-based rule with C, not by comparing Fano lower bounds; finite LLM performance needs experiments. Retain the paper’s bounded empirical comparisons; reject strict error-loss and universal single-agent superiority claims.

**Residual uncertainty:** This is an explicit analytical criticism, not an independently published correction. Model-specific compute/information constraints still matter. **Attribution:** `RESEARCHER_MATHEMATICAL_CRITICISM_OF_INSPECTED_SOURCE`.

### EMAS-K019 — EMAS-028; EMAS-064; EMAS-073

**Strongest objection:** Both maximal messaging and maximal silence can be harmful.

**Evidence and locator:** Removing communication hurts selected coordination tasks; other simulations show overhead, and the human trial found no significant explanation benefit. [EMAS-S038; EMAS-S041; EMAS-S054]; alem §4.2.2; specialist simulation; XAI §§2–3.

**Response / current judgement:** Discriminate by information needed for timing/action, recipient workload and measurable consequences. Selective communication is retained; neither anti-communication nor always-communicate is adopted.

**Residual uncertainty:** The optimal disclosure/modality policy remains population- and task-specific. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K020 — EMAS-057; EMAS-065; EMAS-067; EMAS-070

**Strongest objection:** A large number of runs or a deployment story does not establish independent replicated causal benefit.

**Evidence and locator:** Benchmarks share code/data; the airport report documents use, while disaster trials are staged. [EMAS-S035; EMAS-S038; EMAS-S042; EMAS-S043]; Experimental protocols and case reports.

**Response / current judgement:** Partition provenance, theory, comparison, field use and replication. No whole-synthesis effectiveness claim is made.

**Residual uncertainty:** Independent field comparisons remain sparse in this inspected corpus. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K021 — EMAS-005; EMAS-058; EMAS-062; EMAS-075

**Strongest objection:** Replication cannot repair insufficient correct utility knowledge or upgrade an approximate optimiser to exactness.

**Evidence and locator:** The construction has per-relevant-group thresholds and reproduces underlying messages. [EMAS-S051]; Theorem 4.2; §5 replication; §6 experiments.

**Response / current judgement:** State the local knowledge/fault/round assumptions and communication expansion. Keep a domain-specific replicated-optimisation branch, not generic Byzantine resilience.

**Residual uncertainty:** Supplementary proof not independently checked; shared bad knowledge and out-of-model faults remain. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K022 — EMAS-037; EMAS-038; EMAS-040; EMAS-076

**Strongest objection:** Norm awareness is not compliance, legitimacy or proven scalable adaptation.

**Evidence and locator:** The extended abstract demonstrates a running example and leaves larger studies/dynamic norms open. [EMAS-S052]; §§2–3; discussion of future evaluation.

**Response / current judgement:** Treat compliant, violating and inapplicable plans as represented choices subject to actual constraints. Retain domain-specific plan augmentation; do not claim automatic safe norm following.

**Residual uncertainty:** Conflicts, valuation validity, changing norms and overhead need further evidence. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K023 — EMAS-016; EMAS-059; EMAS-061; EMAS-069; EMAS-071

**Strongest objection:** Every local state machine may be legal while the collective objective remains unmet.

**Evidence and locator:** Permitted completion, coherent commitment accounts and accepted tasks establish different things. [EMAS-S016; EMAS-S043; EMAS-S044]; Protocol completion; commitment alignment; field task evaluation.

**Response / current judgement:** Couple these models to material effects, progress observation and an authorised response. Observation–obligation–action closure survives as a composition-induced obligation with no whole-system theorem.

**Residual uncertainty:** Residual uncertainty about unobserved effects may require waiting or external adjudication. **Attribution:** `SOURCED_CRITICISM_WITH_RESEARCHER_ADJUDICATION`.

### EMAS-K024 — EMAS-028; EMAS-065; EMAS-067; EMAS-068

**Strongest objection:** No significant difference is not evidence of equivalence, and exploratory faster adaptation is not a confirmed benefit.

**Evidence and locator:** Small unequal groups and limited power in one game layout constrain inference. [EMAS-S054]; §3 preliminary findings and Figure 2.

**Response / current judgement:** Preserve the null result and uncertainty; test outcome, attention and expertise with adequate design. Explanation is conditional assistance to a real decision, not mandatory narration or evidence of oversight.

**Residual uncertainty:** Effects in less experienced or operational populations are unestablished. **Attribution:** `SOURCE_NULL_FINDING_AND_RESEARCHER_INFERENCE_LIMIT`.


## EVOLVED_MULTI_AGENT_SYSTEMS_EVOLUTION_UNDER_CRITICISM

The transition labels describe documented component changes and separately labelled analytical changes in assumptions or evidential scope. They do not imply that every later work supersedes every earlier alternative. Shorthand overgeneralisations are tested propositions, not automatically claims made by the original authors. The final row is explicitly this report’s composition, not a historical consensus.

**EMAS-E001 — Generic task connection — `REFINED`.** Marginal-cost evaluation, task-bundle contracts and conditional decommitment extend task connection. Keeping an award distinct from fulfilment is an analytical safeguard, not a claim that Smith equated the two. Allocation/search and actual fulfilment remain distinct. Properties: EMAS-015; EMAS-016; EMAS-017; EMAS-021; EMAS-035. Criticisms: EMAS-K005; EMAS-K007. [EMAS-S004; EMAS-S045; EMAS-S046]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E002 — Distributed problem solving with expensive coordination — `NARROWED`.** Use partial plan information or remove dependencies when full coordination is wasteful. Coordination is selected by actual interdependence and cost, not added for its own sake. Properties: EMAS-001; EMAS-018; EMAS-019; EMAS-028; EMAS-073. Criticisms: EMAS-K001; EMAS-K019. [EMAS-S006; EMAS-S041]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E003 — Joint-intention and SharedPlans accounts — `HYBRIDISED`.** Operational monitoring, repair and communication-cost analysis supplement selected formal ideas. No full plan or unlimited common-belief requirement for every team; semantics remain conditional. Properties: EMAS-023; EMAS-024; EMAS-027; EMAS-028. Criticisms: EMAS-K006; EMAS-K007. [EMAS-S007; EMAS-S008; EMAS-S009; EMAS-S010]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E004 — Private semantic tests for open ACLs — `STILL_CONTESTED`.** Public social obligations and local information enactments replace inaccessible sincerity as public evidence in the open branch. Closed mental-state models remain useful; neither publicness nor intention implies external truth. Properties: EMAS-008; EMAS-009; EMAS-025; EMAS-026. Criticisms: EMAS-K002; EMAS-K003. [EMAS-S013; EMAS-S014; EMAS-S016; EMAS-S044]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E005 — Version/brand equals interoperability — `REJECTED`.** Require exact semantic and implementation profiles instead of inferring them from historic standards. Final/current FIPA equivalence remains unresolved in this packet. Properties: EMAS-007; EMAS-013; EMAS-014; EMAS-063. Criticisms: EMAS-K004. [EMAS-S014; EMAS-S015; EMAS-S053]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E006 — Unqualified incentive/welfare promise — `NARROWED`.** Declare mechanism assumptions and incompatible desiderata; test undesirable equilibria separately. Strategic stability is not a normative endorsement. Properties: EMAS-030; EMAS-031; EMAS-032; EMAS-033; EMAS-034. Criticisms: EMAS-K008; EMAS-K009. [EMAS-S023; EMAS-S024; EMAS-S025; EMAS-S040]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E007 — Organisation as structure or norm text — `GENERALISED`.** Relate roles to goals, obligations, observability and actual enforcement alternatives. More dimensions are not automatically better; computational authority remains bounded. Properties: EMAS-036; EMAS-037; EMAS-038; EMAS-039; EMAS-042. Criticisms: EMAS-K010. [EMAS-S018; EMAS-S019; EMAS-S020; EMAS-S021]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E008 — Fixed organisations — `DOMAIN_SPECIFIC`.** A monitored, selected and implemented reorganisation can respond to bounded changes. Reorganisation does not fix impossible goals or self-authorise new powers. Properties: EMAS-040; EMAS-063; EMAS-072; EMAS-074. Criticisms: EMAS-K011. [EMAS-S050]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E009 — Distributed optimisation as automatically scalable/private — `NARROWED`.** Select algorithm/quality according to structural complexity and protocol-specific privacy. Exact model quality may be too expensive or based on a wrong objective. Properties: EMAS-043; EMAS-044; EMAS-045. Criticisms: EMAS-K012. [EMAS-S026; EMAS-S027; EMAS-S028; EMAS-S029; EMAS-S030]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E010 — Unqualified decentralised fault tolerance — `DOMAIN_SPECIFIC`.** Use per-knowledge-group replication under an explicit corruption model. Underlying approximation remains and common incorrect knowledge is not repaired. Properties: EMAS-005; EMAS-058; EMAS-062; EMAS-075. Criticisms: EMAS-K021. [EMAS-S051]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E011 — Self-play and local reward improvement — `REFINED`.** Respect decentralised information restrictions and test partner change/collective trajectories. Controlled training results do not establish general open-population coordination. Properties: EMAS-050; EMAS-051; EMAS-052; EMAS-053; EMAS-054; EMAS-056. Criticisms: EMAS-K014; EMAS-K015. [EMAS-S032; EMAS-S033; EMAS-S034; EMAS-S035]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E012 — Emergent norm equals beneficial institution — `NARROWED`.** Separate behavioural persistence, explicit rules, sanctions and independent legitimacy. Simulated social learning can stabilise unwanted patterns. Properties: EMAS-033; EMAS-037; EMAS-055. Criticisms: EMAS-K009; EMAS-K010. [EMAS-S020; EMAS-S039; EMAS-S040]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E013 — Reputation as safety certificate — `NARROWED`.** Model strategic history manipulation and limit future exposure. The first con and out-of-model strategies remain possible. Properties: EMAS-048; EMAS-058; EMAS-060. Criticisms: EMAS-K016. [EMAS-S049]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E014 — Universal multi-agent LLM superiority or its inverse — `STILL_CONTESTED`.** Use stronger budget comparators, interaction traces and genuine coordination tasks; reject overly broad arguments on both sides. Task-specific gains coexist with costs and shared-error failure. Properties: EMAS-001; EMAS-006; EMAS-065; EMAS-066; EMAS-067; EMAS-069. Criticisms: EMAS-K017; EMAS-K018; EMAS-K019; EMAS-K020. [EMAS-S036; EMAS-S037; EMAS-S038; EMAS-S041; EMAS-S048]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E015 — Narration equals useful human oversight — `NARROWED`.** Evaluate triggered explanations with actual users and distinguish non-significance from equivalence. Attention, expertise, modality and real powers remain material. Properties: EMAS-028; EMAS-068. Criticisms: EMAS-K024. [EMAS-S022; EMAS-S043; EMAS-S054]

**Evidence status:** `SOURCE_GROUNDED_ANALYTICAL_NARROWING`. The original-branch label names a proposition tested in this study, not an assertion that the cited authors or the field unanimously advocated it. The sources supply the mechanism, counterevidence or bounded result used for adjudication.

**EMAS-E016 — Norm-awareness added to plans — `HYBRIDISED`.** Represent compliance, violation consequences and non-applicability in BDI plan choices. Running-example support does not establish scale, dynamic norms or legitimacy. Properties: EMAS-037; EMAS-038; EMAS-076. Criticisms: EMAS-K022. [EMAS-S052]

**Evidence status:** `DOCUMENTED_COMPONENT_DEVELOPMENT_WITH_RESEARCHER_SYNTHESIS`. The cited work establishes the identified mechanism or explicit extension/criticism; the selection rule and wider engineering limit are this study’s adjudication. A shorthand overgeneralisation is not attributed as the original authors’ own claim.

**EMAS-E017 — Independent component correctness — `GENERALISED`.** Analytical composition adds consequence closure, assumption handoff, minimum adequacy and dependency-coupled revision. These four additions are this study’s synthesis, not a newly proven historical school. Properties: EMAS-016; EMAS-026; EMAS-061; EMAS-069; EMAS-071; EMAS-072; EMAS-073; EMAS-074. Criticisms: EMAS-K003; EMAS-K023. [EMAS-S016; EMAS-S020; EMAS-S043; EMAS-S044; EMAS-S050]

**Evidence status:** `RESEARCHER_COMPOSITION`. This transition belongs to the present synthesis, not to a documented historical school or a validated new architecture.


## EVOLVED_MULTI_AGENT_SYSTEMS_INTERNAL_TENSIONS

### EMAS-T001 — Autonomy versus coordination

**Protected values:** Participant freedom and predictable joint contribution. Properties: EMAS-003; EMAS-016; EMAS-021; EMAS-023; EMAS-025; EMAS-030.

**Discriminator:** Independent principals or rapidly changing opportunities need refusal/withdrawal. In contrast, Dependent work needs stable undertakings and notice.

**Selection or supported hybrid:** Use bounded commitments with agreed release, not total control or unrestricted abandonment.

**Failure and uncertainty:** Strategic withdrawal or over-rigid commitment harms others. How much stability must each party purchase or accept? [EMAS-S011; EMAS-S023; EMAS-S046]

### EMAS-T002 — Privacy versus shared information

**Protected values:** Confidentiality and verifiable interaction. Properties: EMAS-008; EMAS-018; EMAS-026; EMAS-045.

**Discriminator:** Private utility or sensitive state has a real protection requirement. In contrast, Feasibility, public obligation or repair needs shared evidence.

**Selection or supported hybrid:** Share/protect exactly the information required by a defined protocol; keep privacy claims adversary-specific.

**Failure and uncertainty:** Residual inference or opaque obligations remain. Can the needed guarantee be obtained under the actual leakage budget? [EMAS-S013; EMAS-S029; EMAS-S044]

### EMAS-T003 — Individual incentives versus collective value

**Protected values:** Voluntary participation, strategic stability and collective outcomes. Properties: EMAS-017; EMAS-020; EMAS-030; EMAS-031; EMAS-032; EMAS-033; EMAS-069.

**Discriminator:** Open principals may refuse or manipulate. In contrast, Scarce resources and affected outsiders make global consequences important.

**Selection or supported hybrid:** Declare the mechanism trade-off; change assumptions or relax a named desideratum when necessary.

**Failure and uncertainty:** A welfare-improving mechanism can exclude participants or stabilise harmful collusion. Who is entitled to choose the trade-off? [EMAS-S024; EMAS-S040; EMAS-S045]

### EMAS-T004 — Flexibility versus protocol guarantees

**Protected values:** Open participation and analysable meaning. Properties: EMAS-007; EMAS-010; EMAS-011; EMAS-021; EMAS-026; EMAS-063.

**Discriminator:** Tasks and participants change beyond a rigid pre-scripted sequence. In contrast, High-cost interactions need fixed information and commitment invariants.

**Selection or supported hybrid:** Use flexible enactments constrained by information identity and explicit revision/handoff.

**Failure and uncertainty:** Admission/revision can break earlier obligations or become too expensive. How permissive can the protocol be while retaining the required property? [EMAS-S016; EMAS-S044; EMAS-S046]

### EMAS-T005 — Local responsiveness versus global consistency

**Protected values:** Fast adaptation and joint feasibility. Properties: EMAS-018; EMAS-020; EMAS-026; EMAS-050; EMAS-061.

**Discriminator:** Local observations become stale quickly or communication is expensive. In contrast, Conflicting actions can cause irreversible joint failure.

**Selection or supported hybrid:** Identify the specific cross-agent invariant; reconcile only dependencies that can violate it.

**Failure and uncertainty:** Global checks can delay response; local updates can oscillate or double act. No universal communication interval or update schedule is established.  [EMAS-S006; EMAS-S032; EMAS-S044]

### EMAS-T006 — Diversity versus integration cost

**Protected values:** Complementary capability and economical coordination. Properties: EMAS-007; EMAS-054; EMAS-063; EMAS-065; EMAS-066; EMAS-069.

**Discriminator:** Unseen partners or heterogeneous resources supply unique value. In contrast, Shared formats or specialised extra agents cause overhead.

**Selection or supported hybrid:** Compare task-specific heterogeneous teams with their credible homogeneous/simple alternatives.

**Failure and uncertainty:** Shared model ancestry may preserve common errors despite role diversity. When does diversity change the error structure rather than only the labels? [EMAS-S034; EMAS-S038; EMAS-S041]

### EMAS-T007 — Enforcement versus discretion

**Protected values:** Compliance, autonomy and legitimate exceptions. Properties: EMAS-037; EMAS-038; EMAS-040; EMAS-041; EMAS-076.

**Discriminator:** Preventable high-consequence acts justify restricting capability. In contrast, Uncertain norms and exceptions require interpretation and accountable judgement.

**Selection or supported hybrid:** Regiment only suitable acts; model remaining obligations and dispute/decision rights explicitly.

**Failure and uncertainty:** Excess control blocks useful acts; deliberation permits harmful choices. External legitimacy and contested facts remain independent burdens.  [EMAS-S020; EMAS-S021; EMAS-S052]

### EMAS-T008 — Exact quality versus time, messages and privacy

**Protected values:** Optimal modelled objective and feasible operation. Properties: EMAS-019; EMAS-044; EMAS-045; EMAS-065; EMAS-073.

**Discriminator:** Small structured problems require certified optimum or privacy. In contrast, Dynamic or large problems make exact distributed search unaffordable.

**Selection or supported hybrid:** Select bounded-quality/central/local alternatives and state the sacrificed guarantee.

**Failure and uncertainty:** The optimum can arrive after its assumptions expire. What quality loss is acceptable for the actual consequence? [EMAS-S027; EMAS-S028; EMAS-S029; EMAS-S030]

### EMAS-T009 — Transparency versus human attention

**Protected values:** Actionable knowledge and limited cognitive bandwidth. Properties: EMAS-012; EMAS-028; EMAS-068; EMAS-069.

**Discriminator:** People need timely information about a blocking or changed action. In contrast, Experienced users already infer status and narration interferes.

**Selection or supported hybrid:** Trigger useful explanations and test actual outcomes/attention rather than mere display.

**Failure and uncertainty:** No explanation may hide a conflict; excessive explanation may obscure the task. The small 2026 null study does not settle modality or expertise effects.  [EMAS-S022; EMAS-S043; EMAS-S054]

### EMAS-T010 — Adaptation versus continuity

**Protected values:** Learning/reorganisation and dependable partner expectations. Properties: EMAS-023; EMAS-026; EMAS-039; EMAS-040; EMAS-050; EMAS-074; EMAS-076.

**Discriminator:** Changed goals or populations make the old policy inadequate. In contrast, Existing obligations and jointly feasible actions must persist.

**Selection or supported hybrid:** Evaluate dependent interfaces and make a bounded transition or renegotiation.

**Failure and uncertainty:** Locally useful revisions can induce collective instability or permanent review. Stable general self-revision remains unproved for the combined system.  [EMAS-S034; EMAS-S050; EMAS-S052]


## EVOLVED_MULTI_AGENT_SYSTEMS_COMPOSED_SYSTEM

### Purpose, objects and operational organisation

The composed system enables interacting decision makers to coordinate or coexist while preserving an explicit connection between what is known, what is owed or permitted, what can be done and what actually happens. The object is a defensible collective interaction—not an inventory of agents or a single numerical performance score. Its environment contains independent participants and resource controllers whose powers are not created by the model.

Objects include participants and admission conditions; local observations and message histories; task and resource state; private plans and public obligations kept distinct; roles and norms; strategy/policy parameters; and evidence of consequences. These are analytical views. They need not be separate databases, processes or owners. One simple mechanism may serve several views without erasing their different claims or genealogy.

Agents exchange proposals, information, acceptances, warnings and commitment-changing events. Capable actors use actual permissions to allocate or alter resources, provide services, perform tasks or refuse/withdraw within agreed terms. An observer, beneficiary, counterparty or authorised human establishes the consequential postcondition. Other actors may contest it. A sent message establishes at most the transition that the selected semantics and observation support; it cannot silently stand in for all subsequent transitions.

### Concurrency, loops and interrupts

This account is not a serial workflow. Planning and execution may proceed concurrently with selected communication. A resource conflict can trigger replanning; a missing contribution can trigger team repair; a changed private objective can trigger an agreed withdrawal; a disputed message meaning can block a commitment transition; and a changed transport or participant can invalidate a formerly adequate guarantee. An outcome observation feeds back into allocation and policy evaluation. The response may be repair, renegotiation, an alternative mechanism, human decision or suspension—not necessarily automatic continuation.

The composition has no mandatory universal monitor or central controller. Where a collective property requires a consumer of progress or a legitimate revision decision, that responsibility must be established in the actual configuration. In a small team it may be one existing participant. In an institution it may be distributed or external. Requiring one new control or owner per property would be a new, unsupported design prescription.

### Four composition-induced properties

**EMAS-071, observation–obligation–action closure**, arises because communication semantics, normative relations and material execution have different postconditions. Their conjunction is insufficient unless the bindings between them are correct. Its requirement is to keep missing evidence or authority visible rather than treating a neighbouring success as proof.

**EMAS-072, regime-change guards and explicit handoff**, arises because different component guarantees depend on different assumptions. A new strategic participant, changed message ordering or replacement role can invalidate selected dependencies while leaving others intact. The system must identify the affected claims and dispose of in-flight obligations before treating the new regime as equivalent.

**EMAS-073, minimum adequate coordination**, arises because individually useful mechanisms accumulate interacting costs. A source catalogue alone cannot choose the appropriate configuration. The selection must retain the protected dependency, actual consumer and cheaper alternative, including omission and retirement. This is not minimisation of machinery at any cost.

**EMAS-074, dependency-coupled adaptation**, arises because local policy or organisational changes alter other participants’ expectations. A local improvement is accepted as a collective revision only after its relevant dependent obligations and constraints have been considered. No general safe-self-modification theorem is claimed.

These four properties are analytical consequences of combining the identified distinctions; no source is represented as having evaluated this complete system. They have `EXAMINED_WITH_EVIDENCE_LIMIT` status and explicit unresolved transfer obligations.

### Smallest coherent form and richer branches

The smallest coherent form has an actual interdependence, a declared population and rights boundary, a minimally adequate interaction, a capable actor, a consequence criterion and an observation/response path for material failures or changes. It may consist of a direct request and authorised action with a simple completion check. It does not require auctions, comprehensive shared plans, formal norms, a learned policy or a distributed optimiser.

**EMAS-CFG01 — Smallest coherent direct coordination.** Guard: A few participants have clear rights and a simple shared dependency. A principal/peer expresses a concrete dependency; a capable participant acts; the relevant recipient observes the outcome. Only consequential exceptions cause messages or repair.

Omissions and substitutions: No general auction, full SharedPlans representation, norm institution, learning or DCOP is required. A direct authorised scheduler may dominate. Omit agent coordination entirely if ordinary services or one actor satisfy the boundary and requirements. Properties: EMAS-001; EMAS-002; EMAS-003; EMAS-004; EMAS-007; EMAS-012; EMAS-016; EMAS-020; EMAS-058; EMAS-061; EMAS-065; EMAS-069; EMAS-071; EMAS-073.

**EMAS-CFG02 — Cooperative team with revisable plans.** Guard: Shared objective and enough inspectability/notification to maintain a joint undertaking. Local work and partial-plan exchange run concurrently; changed goals or failed members interrupt, trigger notification and revise contribution plans.

Omissions and substitutions: Closed mental-state reasoning and partial plans do not imply open-market incentive compatibility. Public commitments can be added at opaque boundaries. Use direct coordination when plan uncertainty or role interaction no longer justifies team machinery. Properties: EMAS-018; EMAS-020; EMAS-023; EMAS-024; EMAS-027; EMAS-028; EMAS-054; EMAS-059; EMAS-061; EMAS-069; EMAS-072; EMAS-074.

**EMAS-CFG03 — Open strategic interaction.** Guard: Distinct principals exchange services/resources while retaining their own objectives. Public commitments track obligations; the selected mechanism governs offers/acceptance; authorised observers establish effects and disputes, not private-belief access.

Omissions and substitutions: Do not assume joint intentions, truth-telling, shared utility or enforceable penalties merely because agents participate. Replace bargaining with a simpler posted/direct protocol when it satisfies consent, incentives and allocation needs. Properties: EMAS-002; EMAS-003; EMAS-007; EMAS-008; EMAS-010; EMAS-012; EMAS-015; EMAS-016; EMAS-017; EMAS-021; EMAS-025; EMAS-026; EMAS-030; EMAS-031; EMAS-032; EMAS-033; EMAS-034; EMAS-035; EMAS-058; EMAS-060; EMAS-063; EMAS-071; EMAS-072.

**EMAS-CFG04 — Structured distributed optimisation.** Guard: Finite decomposable objective and a justifiable need to keep decisions or information distributed. Select exact or approximate search according to graph structure and costs; translate assignments into actions separately; measure actual joint consequences.

Omissions and substitutions: Privacy protection and fault-tolerant replication are independent optional extensions with extra assumptions. CTDE or auctions are not mandatory. Use central or local deterministic optimisation if privacy, locality or ownership does not justify distributed computation. Properties: EMAS-002; EMAS-003; EMAS-020; EMAS-043; EMAS-044; EMAS-045; EMAS-058; EMAS-065; EMAS-069; EMAS-075.

**EMAS-CFG05 — Adaptive collective in a controlled environment.** Guard: Repeated experience can improve policies and the population/dynamics are sufficiently testable. Policies update within a declared experimental regime; partner/cost/constraint tests determine whether a local change is a permissible collective revision.

Omissions and substitutions: CTDE and monotonic factorisation are choices, not the definition of learning or emergence. A learned convention is not an externally legitimate institution. Prefer a fixed protocol if learning offers no robust gain or prevents maintenance of required constraints. Properties: EMAS-003; EMAS-020; EMAS-050; EMAS-051; EMAS-052; EMAS-053; EMAS-054; EMAS-055; EMAS-057; EMAS-058; EMAS-065; EMAS-067; EMAS-069; EMAS-074.

**EMAS-CFG06 — Human-agent and organisational overlay.** Guard: Human participants or an institution retain material decisions, responsibilities or vetoes. People receive actionable information and exercise actual powers; norm detection and enforcement use available observability; revision preserves participant commitments.

Omissions and substitutions: An approval checkbox, role chart or norm-aware planner is not meaningful oversight. This overlay can couple to other configurations. Remove redundant explanations/structures when the human consumer and risk no longer require them, without silently deleting accountability. Properties: EMAS-004; EMAS-028; EMAS-036; EMAS-037; EMAS-038; EMAS-039; EMAS-040; EMAS-041; EMAS-063; EMAS-068; EMAS-070; EMAS-071; EMAS-072; EMAS-076.

### Precise relational model

The complete guarded relation records are in [the composition model](EVOLVED_MULTI_AGENT_SYSTEMS_COMPOSITION_MODEL.json). `FROM REQUIRES TO` means the former depends on the latter under the stated guard. `PROVIDES_EVIDENCE_FOR` can be partial; it never silently transfers a stronger guarantee. Alternatives and conflicts do not prescribe simultaneous use. Every relation records shared/incompatible assumptions, mechanism, new costs, source IDs, evidence status and unresolved obligations.

| Relation | From → to | Type | Guard and operative coupling |
|---|---|---|---|
| EMAS-REL-001 | EMAS-001 → EMAS-002; EMAS-003; EMAS-004; EMAS-020 | REQUIRES | Selecting an agent boundary. Define what is distributed and which dependency agent decomposition actually addresses. |
| EMAS-REL-002 | EMAS-005 → EMAS-058; EMAS-075 | CONFLICTS_WITH | A robustness claim relies solely on decentralisation. Replace the rejected universal claim with the chosen fault-specific construction. |
| EMAS-REL-003 | EMAS-006 → EMAS-001; EMAS-065; EMAS-069 | CONFLICTS_WITH | An extra participant is proposed as automatic improvement. Retain an added participant only for an evidenced marginal contribution. |
| EMAS-REL-004 | EMAS-007 → EMAS-010; EMAS-012 | REQUIRES | Multiple interactions or consequential messages. Bind messages to an interaction and distinguish the transitions each message can evidence. |
| EMAS-REL-005 | EMAS-008 → EMAS-009 | ALTERNATIVE_TO | Choosing public semantics for opaque participants versus mental-state semantics for inspectable agents. Use commitment/information effects at an open boundary; retain mental-state reasoning within a justified closed implementation. |
| EMAS-REL-006 | EMAS-014 → EMAS-007; EMAS-008; EMAS-012 | CONFLICTS_WITH | Roles or performatives are used as evidence of cooperation. Treat the label as syntax until an operative semantic relation and observation support it. |
| EMAS-REL-007 | EMAS-013 → EMAS-007; EMAS-063 | CONSTRAINS | A design claims FIPA compatibility today. Leave current equivalence unresolved until the exact profile and conformance evidence are available. |
| EMAS-REL-008 | EMAS-011 → EMAS-016; EMAS-061 | PROVIDES_EVIDENCE_FOR | The selected protocol admits a model-level completion analysis. Model analysis excludes a class of protocol dead ends, but an execution/progress observer is still needed. |
| EMAS-REL-009 | EMAS-015 → EMAS-016; EMAS-020 | ACTS_THROUGH | An allocator assigns work involving shared resources. The allocation becomes a proposal or commitment through the task lifecycle and resource controls. |
| EMAS-REL-010 | EMAS-017 → EMAS-003; EMAS-030; EMAS-031; EMAS-032; EMAS-035 | REQUIRES | Economic task exchange is selected. Choose the compatible bargaining or incentive model before asserting welfare properties. |
| EMAS-REL-011 | EMAS-019 → EMAS-015; EMAS-017; EMAS-018 | ALTERNATIVE_TO | Dependencies can be removed or bundled without violating requirements. Eliminate the conflict rather than repeatedly negotiating it. |
| EMAS-REL-012 | EMAS-018 → EMAS-020; EMAS-027 | COMMUNICATES_TO | Interleaved local planning needs selected global dependencies. Exchange partial plans to adjust timing and detect team assumptions requiring repair. |
| EMAS-REL-013 | EMAS-022 → EMAS-019; EMAS-073 | CONFLICTS_WITH | Negotiation is required even though a suitable authorised owner is known. Use direct assignment or no coordination unless negotiation earns its cost. |
| EMAS-REL-014 | EMAS-021 → EMAS-025; EMAS-026; EMAS-059 | FEEDBACK_TO | A party seeks justified withdrawal or cannot perform. Reconcile compensation, delegation and remaining work before recontracting. |
| EMAS-REL-015 | EMAS-023 → EMAS-024; EMAS-027; EMAS-028 | ENABLES | A joint undertaking persists despite incomplete knowledge. Partial plans specify contribution; monitoring detects reconsideration; selective messages repair expectations. |
| EMAS-REL-016 | EMAS-024 → EMAS-018 | SHARES_ANCESTRY_WITH | Both mechanisms address incompletely specified distributed activity. Preserve their shared distributed-planning problem while keeping their state representations distinct. |
| EMAS-REL-017 | EMAS-025 → EMAS-008; EMAS-010; EMAS-012 | REQUIRES | Obligations are assessed from public interaction. Use observable lifecycle events to assess the relevant conditional commitment. |
| EMAS-REL-018 | EMAS-026 → EMAS-063; EMAS-058 | CONSTRAINS | Delegation or assignment crosses principals or versions. Preserve responsibility and compatible commitment state across the transfer. |
| EMAS-REL-019 | EMAS-027 → EMAS-023; EMAS-059 | FEEDBACK_TO | A team assumption, member or capability changes. Notify and revise plans, reallocate or terminate the affected undertaking. |
| EMAS-REL-020 | EMAS-028 → EMAS-064 | CONFLICTS_WITH | Communication is selected by information value and recipient cost. Send information that changes an action or expectation; test omission where it does not. |
| EMAS-REL-021 | EMAS-029 → EMAS-023; EMAS-024; EMAS-028 | CONFLICTS_WITH | Universal common belief is demanded before cooperation. Retain sufficient explicit notification or partial shared plans under the chosen model. |
| EMAS-REL-022 | EMAS-030 → EMAS-033; EMAS-034 | ENABLES | The population can deviate strategically. Evaluate both strategic stability and the independently selected collective criterion. |
| EMAS-REL-023 | EMAS-031 → EMAS-032 | CONFLICTS_WITH | Truthfulness, participation, budget and full efficiency are demanded together in bilateral trade. Relax a specified requirement or domain assumption instead of promising an impossible mechanism. |
| EMAS-REL-024 | EMAS-034 → EMAS-055; EMAS-060 | CONSTRAINS | Stable behaviour or trust is used to justify open interaction. Use adversarial histories and changed opponents to test purported stability. |
| EMAS-REL-025 | EMAS-035 → EMAS-017; EMAS-020 | CONSTRAINS | Contracts are restricted to a limited exchange neighbourhood. Match the contract language/search scope to interactions necessary for improvement. |
| EMAS-REL-026 | EMAS-036 → EMAS-039; EMAS-037; EMAS-076 | ENABLES | An organisation relates roles, goals and normative responsibilities. Connect structural permission and functional goals to applicable obligations and feasible plans. |
| EMAS-REL-027 | EMAS-037 → EMAS-038; EMAS-041 | REQUIRES | A norm is claimed to control behaviour. Choose prevention, detection/sanction or voluntary reasoning within actual institutional powers. |
| EMAS-REL-028 | EMAS-038 → EMAS-076 | ALTERNATIVE_TO | A norm must influence an agent. Use regimentation when prevention is possible/appropriate; use norm-aware choice where autonomy remains. |
| EMAS-REL-029 | EMAS-040 → EMAS-063; EMAS-072; EMAS-074 | FEEDBACK_TO | Goals, roles or capabilities change. Monitor, propose, select and implement a bounded organisational change, then evaluate dependent interactions. |
| EMAS-REL-030 | EMAS-042 → EMAS-036; EMAS-039; EMAS-037 | CONFLICTS_WITH | Role charts are offered as proof of organisation. Require a usable mapping from role to decisions and interaction; otherwise omit the chart. |
| EMAS-REL-031 | EMAS-043 → EMAS-044; EMAS-058 | CONSTRAINS | Distributed search is used under unreliable communication. Separate the optimisation guarantee from the execution substrate obligations. |
| EMAS-REL-032 | EMAS-044 → EMAS-020; EMAS-065 | ALTERNATIVE_TO | Joint resource/assignment decisions can be modelled as a finite DCOP. Choose ADOPT, DPOP or a cheaper alternative according to memory, time, messages and quality demands. |
| EMAS-REL-033 | EMAS-045 → EMAS-044; EMAS-008 | CONSTRAINS | Costs or beliefs must be kept private. Minimise/protect disclosures consistent with the optimisation and public accountability needs. |
| EMAS-REL-034 | EMAS-046 → EMAS-048; EMAS-049 | CONSTRAINS | An argumentation outcome is used as knowledge. Separate dialectical acceptability from provenance, observation and factual warrant. |
| EMAS-REL-035 | EMAS-047 → EMAS-033; EMAS-049 | CONSTRAINS | A voting rule selects a collective alternative. State which social-choice limitations and domain restrictions apply to the decision rule. |
| EMAS-REL-036 | EMAS-048 → EMAS-049; EMAS-065; EMAS-067 | CONFLICTS_WITH | Many agreeing reports are treated as independent corroboration. Track shared inputs/models/judges and assess the evidential claim at the actual independent unit. |
| EMAS-REL-037 | EMAS-050 → EMAS-051; EMAS-054; EMAS-067 | REQUIRES | Policies are learned among changing agents. Test decentralised execution, partner shifts and repeated training variability separately. |
| EMAS-REL-038 | EMAS-051 → EMAS-004; EMAS-053 | CONSTRAINS | Centralised training is followed by local execution. Keep the training/execution information contract and representation restrictions explicit. |
| EMAS-REL-039 | EMAS-052 → EMAS-053; EMAS-056; EMAS-069 | CONSTRAINS | Local rewards or factored values guide updates. Evaluate credit assignment and the representable joint value before accepting local optimisation as global progress. |
| EMAS-REL-040 | EMAS-054 → EMAS-068; EMAS-063 | PROVIDES_EVIDENCE_FOR | An agent encounters unseen machine or human partners. Evaluate cross-play or representative human interaction before transferring a policy to the new team. |
| EMAS-REL-041 | EMAS-055 → EMAS-037; EMAS-033 | CONSTRAINS | A learned convention is presented as an institution. Distinguish recurrence, explicit rule formation, enforcement and external justification. |
| EMAS-REL-042 | EMAS-056 → EMAS-050; EMAS-069; EMAS-074 | CONFLICTS_WITH | Interacting policy updates improve individual metrics. Measure collective trajectories and retain a revision only under declared joint criteria. |
| EMAS-REL-043 | EMAS-057 → EMAS-070; EMAS-065 | REQUIRES | A simulation or benchmark is used to justify deployment. Treat transfer as a distinct hypothesis with deployment-specific observations and comparators. |
| EMAS-REL-044 | EMAS-058 → EMAS-059; EMAS-062; EMAS-075 | ENABLES | A known failure threatens a collective obligation. Choose recovery, fallback or replication according to the specific failure and protected property. |
| EMAS-REL-045 | EMAS-059 → EMAS-016; EMAS-026; EMAS-020 | FEEDBACK_TO | Work is abandoned or completion uncertain. Reconcile existing effects and obligations before delegating or repeating resource-changing work. |
| EMAS-REL-046 | EMAS-060 → EMAS-008; EMAS-069 | ALTERNATIVE_TO | Direct verification is costly but bounded risk is acceptable. Use trust to choose limited exposure, retaining direct checks for consequences that need them. |
| EMAS-REL-047 | EMAS-061 → EMAS-027; EMAS-059; EMAS-069 | FEEDBACK_TO | Local compliance continues without useful progress. Raise a repair or termination decision based on collective observations. |
| EMAS-REL-048 | EMAS-062 → EMAS-063; EMAS-072 | REQUIRES | A coordinator or common service fails. Re-establish compatible coordination and handle in-flight obligations or suspend. |
| EMAS-REL-049 | EMAS-063 → EMAS-007; EMAS-026; EMAS-039; EMAS-050 | CONSTRAINS | A participant or implementation changes. Selectively re-establish the dependencies actually affected by the change. |
| EMAS-REL-050 | EMAS-065 → EMAS-001; EMAS-017; EMAS-028; EMAS-044; EMAS-066; EMAS-068 | CONSTRAINS | A mechanism claims superiority. Use a defensible comparator and state unmatched quantities; narrow claims after negative or null results. |
| EMAS-REL-051 | EMAS-066 → EMAS-007; EMAS-016; EMAS-025; EMAS-055 | REFINES | Established MAS vocabulary is used for an LLM collective. Map implemented interactions to the classical mechanisms or label the resemblance as analogy. |
| EMAS-REL-052 | EMAS-067 → EMAS-065; EMAS-070 | PROVIDES_EVIDENCE_FOR | Comparisons are reported across runs or programmes. Attach results to the true units, shared sources and uncertainty. |
| EMAS-REL-053 | EMAS-068 → EMAS-004; EMAS-028; EMAS-041 | ACTS_THROUGH | People participate in consequential teamwork. Present decision-relevant information and preserve actual human control and accountability. |
| EMAS-REL-054 | EMAS-069 → EMAS-016; EMAS-020; EMAS-033; EMAS-061 | REQUIRES | Local activities are composed into a collective claim. Check timing, compatibility, resource effects and the independent collective objective. |
| EMAS-REL-055 | EMAS-071 → EMAS-004; EMAS-008; EMAS-012; EMAS-016; EMAS-025; EMAS-037; EMAS-069 | REQUIRES | A consequential interaction is accepted as complete. Close only the justified links from observation through normative/decision change to authorised act and observed effect. |
| EMAS-REL-056 | EMAS-072 → EMAS-002; EMAS-003; EMAS-026; EMAS-058; EMAS-063; EMAS-074 | REQUIRES | A model-defining assumption changes during operation. Identify affected guarantees, choose a compatible branch and dispose of outstanding work. |
| EMAS-REL-057 | EMAS-073 → EMAS-001; EMAS-019; EMAS-022; EMAS-028; EMAS-065 | REQUIRES | Choosing, simplifying or retiring a mechanism. Retain the least costly adequate configuration while preserving necessary evidence and obligations. |
| EMAS-REL-058 | EMAS-074 → EMAS-020; EMAS-026; EMAS-039; EMAS-050; EMAS-054; EMAS-069 | FEEDBACK_TO | A policy, protocol or organisational revision is evaluated. Test dependent constraints and expectations, then preserve, negotiate or explicitly replace them. |
| EMAS-REL-059 | EMAS-075 → EMAS-043; EMAS-044; EMAS-058; EMAS-065 | REFINES | FT-DCOP replication is feasible for the selected optimiser. Preserve fault-free algorithm messages through the studied replicated computation and account for added messages. |
| EMAS-REL-060 | EMAS-076 → EMAS-036; EMAS-037; EMAS-038; EMAS-039; EMAS-074 | ACTS_THROUGH | Norm-related plans are constructed in a BDI implementation. Augment goal-plan alternatives with compliance steps and consequences; evaluate the resulting choice within institutional constraints. |
| EMAS-REL-061 | EMAS-046 → EMAS-007; EMAS-010; EMAS-061 | ACTS_THROUGH | Argument acceptability is established or contested by an inter-agent dialogue rather than entirely within a single reasoner.. Couple the reasoning criterion to move and state-update rules, then assess useful stopping independently of move legality. Preserve disagreement or absence of sufficient reasons. |

### Discriminating tests

The first twelve are invented analytical cases, not observations or experimental validation. The final three use published component cases but do not validate the entire composition. A case passes only in the sense that the relational account gives a non-contradictory, assumption-explicit disposition; it is not a measured deployment pass.

**EMAS-CASE001 — Many agents share one mistaken source (`ANALYTICAL`).** Input/change: Ten roles all repeat the same false database entry. Response: Preserve one evidence origin; agreement does not multiply support. Seek independent observation or leave the answer unverified.

Discriminating observation: Whether any additional report has an independent evidential path. Judgement: Reject consensus-as-truth and agent-count confidence. Remaining burden: Independent ground truth may be unavailable. Properties: EMAS-048; EMAS-049; EMAS-065; EMAS-069; EMAS-071.

**EMAS-CASE002 — Syntactically accepted message, different meanings (`ANALYTICAL`).** Input/change: One version uses complete to mean dispatched, another to mean delivered. Response: Prevent the completion claim from crossing the mismatched semantic boundary; reconcile meaning and live conversations.

Discriminating observation: The recipient’s state and the actual delivery event. Judgement: Parsing is not semantic acceptance or performance. Remaining burden: A migration rule must preserve earlier commitments. Properties: EMAS-007; EMAS-010; EMAS-012; EMAS-063; EMAS-071.

**EMAS-CASE003 — Task awarded but no completed work (`ANALYTICAL`).** Input/change: An award is accepted but the worker disappears after possibly changing a resource. Response: Treat responsibility and effects separately, observe uncertain work, then retry/reassign/terminate only within recovery rights.

Discriminating observation: Material task state, not the award message. Judgement: Allocation does not discharge the obligation. Remaining burden: Irreversible unobserved effects may block a safe retry. Properties: EMAS-015; EMAS-016; EMAS-059; EMAS-061; EMAS-069.

**EMAS-CASE004 — Cooperative protocol meets a strategic entrant (`ANALYTICAL`).** Input/change: A participant begins inflating cost reports for private gain. Response: Suspend the honest-cost welfare claim; choose compatible incentives/public commitments or decline the interaction.

Discriminating observation: Outcome under deviating reports and actual enforcement. Judgement: A cooperative benchmark no longer warrants the claim. Remaining burden: No selected mechanism may satisfy all desired goals. Properties: EMAS-003; EMAS-017; EMAS-025; EMAS-030; EMAS-034; EMAS-063; EMAS-072.

**EMAS-CASE005 — Individually improving policies oscillate collectively (`ANALYTICAL`).** Input/change: Agents simultaneously adapt to yesterday’s congestion and chase the same alternate resource. Response: Measure the joint trajectory and resource constraints; assess a coupled policy/update change rather than accepting local reward improvements.

Discriminating observation: Stability, throughput and resource use over complete cycles. Judgement: Local improvement is insufficient. Remaining burden: No universal damping parameter is supplied. Properties: EMAS-020; EMAS-050; EMAS-052; EMAS-056; EMAS-069; EMAS-074.

**EMAS-CASE006 — Single scheduler beats negotiation-heavy MAS (`ANALYTICAL`).** Input/change: One authorised scheduler has the same information, feasible control and lower total cost. Response: Use the scheduler; preserve task/effect observations and any genuine principal boundaries.

Discriminating observation: Matched quality, time, resources and rights. Judgement: A non-agent or central path is a valid selected outcome. Remaining burden: A hidden privacy or authority constraint could invalidate the comparator. Properties: EMAS-001; EMAS-019; EMAS-022; EMAS-065; EMAS-073.

**EMAS-CASE007 — Favourable complementary team handover (`ANALYTICAL`).** Input/change: Different agents control necessary complementary resources and share a feasible objective. Response: Coordinate acceptance, timing and handover; notify only changes affecting dependent action.

Discriminating observation: The joined resource/action consequence occurs within its window. Judgement: A justified cooperative configuration survives the cheap-path test. Remaining burden: New costs or failures may still remove its advantage. Properties: EMAS-015; EMAS-020; EMAS-023; EMAS-027; EMAS-028; EMAS-069.

**EMAS-CASE008 — No coordination trigger (`ANALYTICAL`).** Input/change: Independent deterministic services have no shared resource or strategic dependency. Response: Do not add negotiation, norms or team beliefs; retain only required service interfaces.

Discriminating observation: No consequential cross-service dependency is lost. Judgement: MAS machinery is inapplicable, not missing. Remaining burden: Revisit if the actual workload introduces shared constraints. Properties: EMAS-001; EMAS-019; EMAS-073.

**EMAS-CASE009 — Delivery assumptions change (`ANALYTICAL`).** Input/change: A reliable FIFO channel is replaced by one that drops/reorders messages. Response: Withdraw alignment/search claims dependent on that transport; add a justified compatible layer or change mechanism.

Discriminating observation: Message histories against the original model obligations. Judgement: A theorem is not refuted merely because its assumptions were removed. Remaining burden: The replacement needs its own evidence. Properties: EMAS-010; EMAS-026; EMAS-043; EMAS-058; EMAS-072.

**EMAS-CASE010 — Goal becomes obsolete and continued effort harmful (`ANALYTICAL`).** Input/change: A joint target is no longer wanted or feasible. Response: Notify, reconsider and settle dependent obligations rather than maximising persistence.

Discriminating observation: Acknowledged changed goal and disposition of outstanding actions. Judgement: Persistence is conditional, not blind loyalty. Remaining burden: Who may declare irrelevance may be disputed. Properties: EMAS-021; EMAS-023; EMAS-027; EMAS-040; EMAS-074.

**EMAS-CASE011 — Norm violation occurs outside the institution’s observations (`ANALYTICAL`).** Input/change: A prohibited physical action is not visible to the norm engine. Response: Record the enforcement gap; use an authorised external observation/dispute route or narrow the claim.

Discriminating observation: An independently established action and an effective permitted response. Judgement: Declared norms and norm-aware plans do not establish enforcement. Remaining burden: Privacy and legitimate jurisdiction may preclude full observation. Properties: EMAS-004; EMAS-037; EMAS-038; EMAS-041; EMAS-076.

**EMAS-CASE012 — Replicas share wrong utility knowledge (`ANALYTICAL`).** Input/change: Replicas all consistently use an incorrect common cost function. Response: Do not infer correctness from replica agreement; distinguish message consistency from objective validity.

Discriminating observation: Utility provenance and correspondence to the actual objective. Judgement: Fault-free behaviour can preserve a wrong model. Remaining burden: No replication scheme here supplies truth of the utility input. Properties: EMAS-005; EMAS-058; EMAS-075.

**EMAS-CASE013 — Airport security scheduling (`PUBLISHED`).** Input/change: ARMOR documents operational scheduling at LAX beginning in 2007. Response: Use as evidence that a strategic decision aid operated with human constraints, not proof of universal decentralisation or prevented attacks.

Discriminating observation: Documented use and modelled schedule behaviour. Judgement: Deployment is supported; causal security benefit is not established by the short demo report. Remaining burden: Independent outcome counterfactual remains absent. Properties: EMAS-030; EMAS-033; EMAS-068; EMAS-070. [EMAS-S042]

**EMAS-CASE014 — Staged human-agent disaster exercise (`PUBLISHED`).** Input/change: Four outdoor trials examined human-agent task allocation in a simulated disaster. Response: Treat participant decisions, connectivity and completion observations as part of the system, not as external afterthoughts.

Discriminating observation: Task outcomes and participant/practitioner feedback in the reported setting. Judgement: Field-trial evidence informs components; it is not a real-disaster deployment claim. Remaining burden: Representativeness and operational transfer remain open. Properties: EMAS-016; EMAS-027; EMAS-057; EMAS-059; EMAS-068; EMAS-069; EMAS-070. [EMAS-S043]

**EMAS-CASE015 — Communication ablation versus explanation null result (`PUBLISHED`).** Input/change: alem agents need explicit messages for coordination; a small human game study found no significant explanation benefit. Response: Select communication by dependency and consumer rather than applying one global message rule.

Discriminating observation: Collective outcome with and without the particular channel/content. Judgement: Different results discriminate different mechanisms, not a universal contradiction. Remaining burden: No generic optimal explanation frequency or modality follows. Properties: EMAS-028; EMAS-065; EMAS-067; EMAS-068. [EMAS-S038; EMAS-S054]

### Revision and external accountability

The revision boundary is predecessor-authorised: affected participants or principals must already possess the right to change the interaction. A monitor’s discovery is evidence for a decision, not a new grant of authority. Revisions must preserve, assign, renegotiate or terminate live commitments and handle possible executed effects. Selected reorganisation work supports bounded revision mechanisms; the wider continuity rule is analytical. External institutions remain responsible for powers and legitimacy not supplied by computational semantics. [EMAS-S020; EMAS-S021; EMAS-S044; EMAS-S050; EMAS-S052]

## EVOLVED_MULTI_AGENT_SYSTEMS_HYBRIDISATION_AND_EXTERNAL_RELATIONS

The field has real imports, not merely analogies. Economic and social-choice results enter with their domain assumptions. AI/non-monotonic-logic argumentation supplies a formal decision object. Organisation/role modelling intersects with engineering methodologies. Distributed computing contributes execution constraints, but this study does not indiscriminately import every distributed-systems theorem. [EMAS-S018; EMAS-S023–025; EMAS-S031]

STEAM is a documented hybrid of teamwork ideas, whereas calling an LLM role prompt a joint intention is only an analogy until its mechanism is established. BSPL’s later implementation translation does not erase its original semantics. Norm-aware BDI combines norms and plan choice without making norm enforcement redundant. Replicated optimisation adds fault assumptions to a particular computational branch rather than furnishing a generic social institution. [EMAS-S009; EMAS-S016–017; EMAS-S051–052]

Later reconciliation with Autonomous Agents should examine agent boundaries, information and actual autonomy assumptions. Reconciliation with Agent-Oriented Software Engineering should examine modelling, implementation and evidence obligations at the documented role/protocol intersection. Neither question is answered for an unread sibling. Shared sources and mechanisms must not be counted as independent empirical support merely because they appear in different traditions.

`SIBLING_CORPORA_NOT_CONSULTED`  
`CROSS_TRIFECTA_SYNTHESIS_NOT_PERFORMED`


## EVOLVED_MULTI_AGENT_SYSTEMS_STRONGEST_SURVIVING_PROPERTIES

The strongest core consists of distinctions and bounded obligations with clear consumers, not a universal bundle of techniques. The table identifies all strongly retained candidates; the other retained mechanisms remain part of the composition under their own guards.

| ID | Strongly retained criterion | Why strength is bounded |
|---|---|---|
| EMAS-002 | Explicit population and environment boundary | Identifiable decision participants and external dependencies. |
| EMAS-003 | Explicit goal alignment and incentive regime | Observable incentives or defensible behavioural assumptions, including outside options. |
| EMAS-004 | Separate information, capability, control and authority | Named action/resource and an identifiable source of authority. |
| EMAS-012 | Delivery, interpretation, acceptance and consequence are separate | An explicit consequence criterion and a recipient or external observer able to establish it. |
| EMAS-016 | Award, acceptance, execution and task completion are distinct | Task identity, completion criterion, responsible parties and an observation path. |
| EMAS-030 | Strategic model and solution-concept selection | Feasible actions, payoffs or preference model, information and participation assumptions. |
| EMAS-033 | Equilibrium, welfare, fairness and legitimacy remain distinct | Declared welfare/distribution criteria and independent authority boundary. |
| EMAS-037 | Norm declaration, detection and enforcement are distinct | Norm meaning, observable facts, legitimate response powers and a fallible-observation policy. |
| EMAS-041 | Computational institution versus external legitimacy | Identifiable external principals, affected participants and the relevant real-world authorisation process. |
| EMAS-048 | Evidence provenance and dependence-aware aggregation | Provenance sufficient to distinguish shared sources from genuinely distinct observations. |
| EMAS-057 | Explicit simulation-to-deployment transfer claim | Target-environment evidence for the assumptions relevant to the claimed effect. |
| EMAS-058 | Failure, deception and common-mode threat model | A stated invariant, fault scope, trusted components and observation limits. |
| EMAS-061 | Collective progress separate from local compliance | A useful-progress definition, waiting assumptions and a consumer empowered to respond. |
| EMAS-065 | Matched-budget and credible simpler baselines | Valid task measures, comparable capability/access and clearly accounted training versus inference costs. |
| EMAS-069 | End-to-end collective consequence evaluation | A declared collective objective and an observation method independent of local self-certification where required. |
| EMAS-070 | Deployment, adoption and causal benefit are separate evidence | Exact programme, setting, comparator and outcome identification. |

A strong distinction can coexist with sparse direct comparative evidence. For example, separating an award from performance is not an estimated percentage gain from a particular workflow. The question is whether the inference being made is warranted; selecting a specific implementation still requires context and cost evidence.

## EVOLVED_MULTI_AGENT_SYSTEMS_CONTEXT_SPECIFIC_PROPERTIES

The conditional configurations preserve useful mechanisms without universalising them. Economic contracting needs a model of reports, participation and enforcement. Full or partial teamwork models need their information and goal assumptions. Distributed optimisation needs a suitable objective/graph/substrate; privacy and fault-tolerant replication add separate conditions. Learning needs justified population and information contracts. Norm-aware plan augmentation has running-example rather than broad field support.

The following IDs are explicitly context-, assumption-, domain- or gaming-sensitive:

**CONTEXT_DEPENDENT:** EMAS-011 (Protocol enactability and completion possibility); EMAS-015 (Capability- and cost-aware task allocation); EMAS-018 (Partial global planning with revisable local views); EMAS-021 (Conditional decommitment and recontracting); EMAS-024 (Partial SharedPlans and capability-directed collaboration); EMAS-028 (Selective decision-theoretic communication); EMAS-038 (Select regimentation, enforcement or voluntary norm reasoning); EMAS-046 (Argument acceptability relative to an explicit semantics); EMAS-051 (Centralised training with decentralised execution information contract); EMAS-062 (Coordination-layer failure and fallback).

**ASSUMPTION_SENSITIVE:** EMAS-009 (Private mental-state sincerity as a universal compliance test); EMAS-017 (Marginal-cost bargaining improves global allocation under a stated regime); EMAS-031 (Incentive-compatible reporting mechanisms); EMAS-035 (Contract and coalition search scope limits); EMAS-043 (Distributed constraint satisfaction under explicit transport and search assumptions); EMAS-047 (Voting with explicit domain and manipulation limits); EMAS-052 (Collective credit assignment and reward alignment); EMAS-053 (Local-to-joint value factorisation under representational restrictions).

**DOMAIN_SPECIFIC:** EMAS-044 (Exact DCOP quality versus structural resource cost); EMAS-075 (Fault-model-specific replicated optimisation); EMAS-076 (Norm-aware plan augmentation and deliberation).

**USEFUL_BUT_EASILY_GAMED:** EMAS-060 (Risk-limited trust and reputation).


## EVOLVED_MULTI_AGENT_SYSTEMS_REJECTED_OR_SUPERSEDED_PRACTICES

**EMAS-005 — Decentralisation inherently guarantees resilience — `REJECTED_OR_DISFAVOURED`.** No such unconditional mechanism is retained; replace the claim with a threat-specific account of dependencies, replication and recovery. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-006 — More agents automatically add capability — `REJECTED_OR_DISFAVOURED`.** Reject monotonic agent-count claims; require marginal capability or outcome gains net of coordination and integration cost. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-014 — Performatives or role prompts constitute cooperation — `CEREMONY_NOT_GENERAL_PROPERTY`.** Reject message labels and role prose as substitutes for an agreed effect, consumer and operative commitment. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-022 — Negotiate every task — `REJECTED_OR_DISFAVOURED`.** Reject compulsory negotiation when ownership and a suitable executor are already determined. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-029 — Full mutual belief is mandatory for all cooperation — `REJECTED_OR_DISFAVOURED`.** Reject universal necessity of full mutual belief; select sufficient knowledge or public-obligation conditions for the actual cooperative task. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-042 — Role charts alone establish organisation — `CEREMONY_NOT_GENERAL_PROPERTY`.** Reject role diagrams or natural-language job labels as evidence of functioning responsibilities, communications or enforcement. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-049 — Consensus establishes factual truth — `REJECTED_OR_DISFAVOURED`.** Reject truth-by-agreement; require evidence appropriate to the factual question independent of the group’s selection rule. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-056 — Individual policy improvement guarantees collective progress — `REJECTED_OR_DISFAVOURED`.** Reject the general implication; measure joint trajectories, resource stocks and stability under interacting updates. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

**EMAS-064 — Unrestricted communication guarantees robustness — `REJECTED_OR_DISFAVOURED`.** Reject the inference from more messages to greater robustness; identify the information and timing actually required by the failure model. This rejects the unconditional/ceremonial proposition, not every bounded implementation associated with its vocabulary.

No whole candidate was assigned `SUPERSEDED_BY_STRONGER_FORM`: the principal historical responses often narrow a claim or provide alternatives rather than replace every prior mechanism. Current FIPA equivalence, EMAS-013, is unresolved rather than rejected.

## EVOLVED_MULTI_AGENT_SYSTEMS_CURRENT_STATE_AND_RESEARCH_FRONTIER

The inspected 2025–2026 frontier is more specific than “agent societies are improving”. It tests coordination under changing tasks and partners, distinguishes base competence from joint timing/resources, studies social rules and adverse strategic equilibria, and extends older formalisms under explicit failure or normative assumptions. AAMAS 2026 itself separates research and extended-abstract tracks; a three-page implementation or preliminary study is not silently promoted to mature deployment evidence. [EMAS-S003; EMAS-S035–041; EMAS-S051–054]

Several open research questions are consequential. How can policies maintain compatibility with unseen partners without giving up useful specialisation? Which information must be communicated, to whom and at what cost? Can a dynamically changing organisation maintain the semantic and normative continuity of its ongoing interactions? Which threat models adequately represent correlated model/source failures? How should benchmark environments distinguish cheap repeated answers from genuine distributed action? These are questions shaped by the inspected mechanisms, not claims that one common solution already exists.

There is also a live measurement problem: token budgets, training steps, wall time, human attention, communication and external risk can move in different directions. A fair comparison may need to disclose several unmatched quantities rather than conceal them in one score. The report retains both positive coordination evidence and negative/null findings, with the exact scope of each.


## EVOLVED_MULTI_AGENT_SYSTEMS_ADVERSARIAL_SYNTHESIS_VERDICT

**Verdict: retain a conditional within-tradition system, not a universal multi-agent architecture.** Its strongest contribution is the disciplined coupling of distributed interdependence, meaningful interaction, assumption-bound guarantees and observed collective consequences. The surviving core remains useful when the selected outcome is a central scheduler, a simpler protocol or no agent-specific coordination at all.

The strongest objection to unification is that the schools do not agree on one semantic object or set of rationality assumptions. Public commitments do not describe the same thing as joint intentions; equilibrium does not answer a norm-enforcement question; DCOP objective quality does not settle legitimacy; and a learned policy may invalidate a static protocol model. This report resolves that objection only conditionally: it supplies alternative configurations and explicit cross-boundary obligations, not a theorem that every combination is compatible.

The next strongest objection is evidential. The full composition has not been independently deployed or compared. Some retained distinctions are logically well motivated but have little direct causal field evidence. Some methods have strong theoretical support only inside narrow models. Other branches have a useful running example or field programme without representative comparative support. The packet therefore does not claim a quantified payoff, universal optimality, generic robustness or mature autonomous self-government.

Adversarial cases changed the outcome. Agent-count and decentralisation shortcuts were rejected. Mental-state sincerity was narrowed to a justified branch. Norm text and role charts lost status as properties. FIPA current equivalence stayed unresolved. Communication was neither maximised nor minimised by slogan. A negative single-agent argument was itself narrowed by an explicit counterexample. These are operative dispositions preserved in the denominator, not decorative objections.

The proper later use is a neutral audit or independent reconciliation that can conclude **already addressed, inapplicable, simpler mechanism sufficient, evidence insufficient, or a demonstrated gap**. None of the source properties establishes adoption in an unspecified host system.


## EVOLVED_MULTI_AGENT_SYSTEMS_OPEN_QUESTIONS_AND_EVIDENCE_LIMITS

### Examined uncertainties, not unread mandatory families

EMAS-013 remains the sole `UNRESOLVED` candidate disposition: historical readable evidence cannot establish exact current final-profile equivalence or implementation prevalence. Other properties retain explicit theory, deployment or transfer limits without being unexamined. The five composition obligations include whole-system validation, semantic bridging, external authority and out-of-model dynamic behaviour. Uncertainty in these areas is part of the frozen judgement.

The current research includes late-2025 and 2026 primary work, not an exhaustive census of every publication through September. Some original precursors or later comparison papers were inaccessible; they are not cited as substantive evidence. The readable replacement coverage and remaining attribution limits are documented. No supplementary proof, figure, result count or source version was invented to fill an access gap.

### Formal evidence register

**EMAS-F001 — Logical joint intention / SharedPlans.** Precisely distinguishes joint persistence or partial collaborative plans from coincident individual goals. Assumptions: Chosen mental-state operators, agents and persistence/recipe conditions. Implementation burden: Establish that implementation states/observations satisfy the semantics; add external monitoring when needed. Limit: Selected definitions/arguments read; no blanket assertion that all real teamwork instantiates them. [EMAS-S007; EMAS-S008]

**EMAS-F002 — Knowledge in distributed communication.** Shows limits on attaining ideal shared knowledge under stated communication uncertainty. Assumptions: Specific channel, timing and knowledge model. Implementation burden: Do not substitute a practical confidence heuristic for a formal common-knowledge claim. Limit: Bounded impossibility, not a theorem against all cooperative action. [EMAS-S047]

**EMAS-F003 — BSPL information protocols.** Enactability and existence of legal completions under the exact liveness definition. Assumptions: Information bindings, local knowledge and protocol constraints. Implementation burden: Implement keys/causality and distinguish available completion from actual willing execution. Limit: Selected proof/example inspected; no eventual-work guarantee inferred. [EMAS-S016]

**EMAS-F004 — Conditional commitments and local observations.** Alignment at quiescence under the specified lifecycle/rule conditions. Assumptions: Point-to-point messages, serial local observations, reliable transport and FIFO per pair in the inspected account. Implementation burden: Respect delivery/order assumptions and event interpretations; preserve commitments through delegation. Limit: Model guarantee does not prove external task truth, instant shared state or arbitrary loss tolerance. [EMAS-S044]

**EMAS-F005 — Bilateral private-value trade.** Certain combinations of incentive, participation, budget and full efficiency requirements cannot all be achieved. Assumptions: Independent private values with relevant overlapping support, interim participation and the stated mechanism class. Implementation burden: Verify the real market lies within the model before importing the impossibility. Limit: Original formulation and result inspected; no universal impossibility for other domains or subsidy regimes. [EMAS-S024]

**EMAS-F006 — Deterministic voting/choice.** Unrestricted strategyproof onto choice among at least three outcomes faces dictatorship. Assumptions: Unrestricted preference domain and stated deterministic mechanism assumptions. Implementation burden: Identify outcome set, preference restrictions and strategic model. Limit: Domain changes and other mechanism classes are not covered by the unqualified slogan. [EMAS-S025]

**EMAS-F007 — Normative multi-agent programs.** Models obligations, violations and institutional transitions formally. Assumptions: Observable actions and model-determined effects within the institutional environment. Implementation burden: Connect external events to the model and establish actual powers independently. Limit: No external legal legitimacy or observability of off-platform action follows. [EMAS-S020]

**EMAS-F008 — Distributed CSP search.** Completeness/correct search behaviour under the selected finite-domain and message assumptions. Assumptions: Known participants and finite-delay reliable FIFO communication as specified. Implementation burden: Implementation transport and local state must respect the algorithm model. Limit: Calculation-cycle experiments do not include all real communication cost. [EMAS-S026]

**EMAS-F009 — Finite DCOP search and dynamic programming.** ADOPT quality bounds; DPOP optimisation with graph-structural message complexity. Assumptions: Correct objective decomposition, finite domains and algorithm-specific communication/ordering. Implementation burden: Supply correct costs and a feasible substrate; translate chosen assignments to actions separately. Limit: Optimal model result is not model validity, privacy or practical cheapness. [EMAS-S027; EMAS-S028]

**EMAS-F010 — Privacy-aware DCOP interaction.** Privacy/leakage claims belong to specific definitions and protocols. Assumptions: Declared adversary/security notion and protocol restrictions. Implementation burden: Assess implementation disclosures and inference rather than inferring privacy from distribution. Limit: No uninspected arbitrary-malicious/collusion guarantee is claimed. [EMAS-S029]

**EMAS-F011 — Abstract argumentation graph.** Defines several acceptability semantics; stable extensions need not exist. Assumptions: Supplied arguments and attack relation plus the selected semantics. Implementation burden: Ground inputs and avoid equating extension membership with truth. Limit: Formal semantics do not provide an independent evidential oracle. [EMAS-S031]

**EMAS-F012 — Monotonic joint-value mixing.** Local argmax selections agree with the represented monotonic joint-value maximisation. Assumptions: Monotonic factorisation and the specified local information/functions. Implementation burden: Respect representability and distinguish learned approximation from the real optimal value. Limit: Not all joint value functions are representable and training is not globally guaranteed. [EMAS-S033]

**EMAS-F013 — FT-DCOP and replicated Max-Sum.** Necessary knowledge coverage and fault-model-specific reproduction of underlying messages. Assumptions: Per-relevant-group knowledge/replicas, at most k faults, 2k+1 construction and synchronous message-passing and round discipline. Implementation burden: Correct utility knowledge, identity/sequence binding and replication at relevant computations. Limit: Main-paper reasoning inspected; supplementary impossibility proof not independently checked. Approximation remains approximation. [EMAS-S051]

**EMAS-F014 — Information channel from full context C to messages M.** Weak Bayes-risk dominance is recoverable by emulation; strict information loss does not imply strict classification-error loss. Assumptions: M is generated from C and predictors are unrestricted Bayes-optimal for the weak comparison. Implementation burden: Do not transfer the unrestricted-information result to finite LLMs without resource/model analysis. Limit: The packet supplies its own explicit strictness counterexample; no published correction is claimed. [EMAS-S037]

### Empirical, field and implementation evidence register

These records preserve actual units and comparators. A denominator is not invented when no quantitative claim from that experiment is used. Shared programmes and benchmark inheritance remain visible in the machine source-dependence register.

**EMAS-EMP001 — Distributed vehicle-monitoring testbed — `EMPIRICAL_COMPARISON`.** Units: Simulated coordination runs and node plans. Comparison: Coordination/communication organisations and less coordinated alternatives. Sample: Four-node difficult vehicle-monitoring scenario; no numerical effect is extracted here. Measures: Solution behaviour and coordination costs.

Outcome: Useful in some interdependent cases, with overhead/stale-view failure boundaries. Uncertainty: Not a representative task-population estimate. Threats: Original meta-organisation, simulated environment and scenario selection. [EMAS-S006]

**EMAS-EMP002 — TRACONET implementation — `EMPIRICAL_COMPARISON`.** Units: Task reallocations and routing instances. Comparison: Marginal-cost task exchange and candidate allocations. Sample: Application/routing instances discussed; no general field sample claimed. Measures: Allocation costs and feasibility.

Outcome: Demonstrates model-driven exchange, not universal optimum or truthful bidding. Uncertainty: No population-wide causal effect extracted. Threats: Cost model, contract neighbourhood and routing heuristics constrain transfer. [EMAS-S045]

**EMAS-EMP003 — n-queens and random networks — `EMPIRICAL_COMPARISON`.** Units: Synthetic distributed CSP instances. Comparison: Asynchronous search variants. Sample: Reported 100 trials in experimental settings; not independent deployments. Measures: Calculation cycles and search behaviour.

Outcome: Comparative algorithm behaviour depends on problem setting. Uncertainty: No converted wall-clock speedup claimed. Threats: Communication cost is excluded from calculation-cycle measures. [EMAS-S026]

**EMAS-EMP004 — Controlled optimisation problems — `EMPIRICAL_COMPARISON`.** Units: Finite DCOP instances. Comparison: Distributed search/dynamic programming alternatives. Sample: Algorithm-specific experimental instances; this packet relies primarily on formal/complexity results, not a pooled effect. Measures: Objective quality, search/messages/memory.

Outcome: Different structural trade-offs, not one universally cheapest method. Uncertainty: No meta-analytic effect or invented combined denominator. Threats: Different instance generators, complexity metrics and implementations. [EMAS-S027; EMAS-S028]

**EMAS-EMP005 — Particle environments and cooperative game benchmarks — `EMPIRICAL_COMPARISON`.** Units: Training runs in controlled games. Comparison: Actor-critic/value-factorised methods and stated baselines. Sample: Source-specific tasks; no pooled sample or current-state score quoted. Measures: Return and modelled collective performance.

Outcome: Supports bounded learning mechanisms; not arbitrary open strategic competence. Uncertainty: Method-specific stochasticity and tasks limit extrapolation. Threats: Shared benchmark ancestry; training/execution information and reward design. [EMAS-S032; EMAS-S033]

**EMAS-EMP006 — Hanabi and coordination tasks — `EMPIRICAL_COMPARISON`.** Units: Learned policies paired with other policies/people in game settings. Comparison: Other-Play versus self-play/alternative preparation. Sample: Known-symmetry game experiments; no representative population claim. Measures: Cross-play coordination.

Outcome: Conventions can be made more compatible under known symmetries. Uncertainty: Preliminary human comparison is limited. Threats: Known symmetry group and selected games; not arbitrary partner adaptation. [EMAS-S034]

**EMAS-EMP007 — Complex fully cooperative benchmarks — `EMPIRICAL_COMPARISON`.** Units: Algorithm–task–seed experiments. Comparison: Eleven cooperative MARL algorithms. Sample: Five seeds; 100 test episodes at a checkpoint. Measures: Selected-policy returns and reported 75% intervals.

Outcome: Rankings and success vary substantially by task/configuration. Uncertainty: Limited seeds/tuning and checkpoint selection. Threats: Shared code/testbed lineage; not strategic or deployment evidence. [EMAS-S035]

**EMAS-EMP008 — Selected LLM-agent tasks/frameworks — `EMPIRICAL_COMPARISON`.** Units: Framework task traces and coded failure patterns. Comparison: Failure patterns across seven frameworks and selected interventions. Sample: 1,642 analysed traces; grounded-theory manual set 150 traces from five frameworks with six experts. Measures: Fourteen failure modes in three categories.

Outcome: Interaction/termination failures are material, not only individual model mistakes. Uncertainty: Scaling uses automated assistance; agreement estimates do not make all traces manually or independently labelled. Threats: Selection, correlated framework/model ancestry and judge dependence; not production failure frequency. [EMAS-S036]

**EMAS-EMP009 — Multi-hop factual reasoning — `EMPIRICAL_COMPARISON`.** Units: Question–architecture–model runs. Comparison: Single-agent and multi-agent designs under thinking-token controls. Sample: FRAMES and MuSiQue four-hop with selected model families; task counts are not extrapolated here. Measures: Answer accuracy and bootstrap uncertainty under budget/context variations.

Outcome: Single-agent designs are strong comparators; selected exceptions and budget caveats remain. Uncertainty: Thinking budgets imperfectly match total compute/cost; no universal effect inferred. Threats: LLM judge, task selection, shared inputs and the overbroad theoretical strictness argument. [EMAS-S037]

**EMAS-EMP010 — Procedural Craftax-derived alem environment — `EMPIRICAL_COMPARISON`.** Units: Team–environment–seed episodes. Comparison: Thirteen LLMs; four trained MARL references; harness and team ablations. Sample: 20 seeds/difficulty open-weight, 10 closed; training/inference budgets explicitly differ. Measures: Separate base and coordination rewards.

Outcome: Base task competence and coordination separate; selected communication ablations impair coordination. Uncertainty: 95% stratified bootstrap; limited closed-model seed budget. Threats: Zero-shot versus billion-step training is not a matched-compute comparison; one constructed environment. [EMAS-S038]

**EMAS-EMP011 — Common-pool resource game — `EMPIRICAL_COMPARISON`.** Units: Simulated ten-agent common-pool groups. Comparison: LLM social learning/norm formation with rule-based comparisons. Sample: Ten interacting agents in the studied model; no real institution sample. Measures: Resource survival, cooperation and utility measures.

Outcome: Supports context-specific norm/convention effects. Uncertainty: Model-specific payoff and removal/intervention conditions. Threats: Context adaptation is not necessarily model-weight learning; simulated voting does not confer legitimacy. [EMAS-S039]

**EMAS-EMP012 — Two-player pricing with logit demand — `EMPIRICAL_COMPARISON`.** Units: Repeated pricing games and restricted meta-strategies. Comparison: Selected LLM meta-strategies and Q-learning variants. Sample: Finite strategy library; LLM analysis restricts model/history/price/horizon choices; no market sample. Measures: Payoffs, empirical meta-game equilibria and collusive behaviour.

Outcome: Adverse stable outcomes can occur in the stated setting. Uncertainty: Restricted meta-game and cost-information assumptions. Threats: Not an exhaustive strategy search or evidence of actual market incidence. [EMAS-S040]

**EMAS-EMP013 — Serial steak versus more parallel soup tasks — `EMPIRICAL_COMPARISON`.** Units: Rule-based kitchen-agent simulations. Comparison: Team size/specialisation and communication constraints. Sample: Reported configurations, not a human or production LLM sample. Measures: Completion and coordination bottlenecks.

Outcome: More specialisation/coalition activity can become inefficient. Uncertainty: Three-page extended abstract gives limited replication detail. Threats: Task structure and simulated behaviour; not a generic headcount threshold. [EMAS-S041]

**EMAS-EMP014 — LAX security checkpoint/canine scheduling — `FIELD_OR_DEPLOYMENT_EVIDENCE`.** Units: Operational decision-support programme. Comparison: No independent counterfactual impact comparison established by this demo. Sample: One airport programme; deployed from August 2007. Measures: Use of strategic scheduling with human constraints.

Outcome: Demonstrates implementation and operational use. Uncertainty: Cannot identify attacks prevented or universal causal benefit. Threats: Single programme, strategic-model assumptions and absence of the relevant outcome counterfactual. [EMAS-S042]

**EMAS-EMP015 — Staged disaster-response exercises — `FIELD_OR_DEPLOYMENT_EVIDENCE`.** Units: Human-agent outdoor exercise participants. Comparison: Reported system versions, task decisions and practitioner feedback. Sample: Four trials, 40 participants, predominantly university students/staff. Measures: Task acceptance/completion and participant/practitioner feedback.

Outcome: Human choices and connectivity matter to end-to-end operation. Uncertainty: Small programme and evolving versions. Threats: Staged trials, training, participant selection; not a real-disaster deployment. [EMAS-S043]

**EMAS-EMP016 — Synthetic trust interaction — `EMPIRICAL_COMPARISON`.** Units: Two-agent interaction histories. Comparison: Direct trust/reputation methods under con cycles. Sample: 400 interactions and five selected con-cycle parameters. Measures: Defection/trust recovery behaviour.

Outcome: Historical good conduct can be manipulated; first con is not prevented. Uncertainty: Simplified threat/noise model. Threats: Direct components are not whole reputation frameworks; no open deployment. [EMAS-S049]

**EMAS-EMP017 — Synthetic FT-DCOP experiment — `EMPIRICAL_COMPARISON`.** Units: Random graph-colouring instances with faults. Comparison: Repl-Max-Sum and the studied comparison variants. Sample: 50 graphs at each n=12,24,36,48; average degree 3; three-colourable instances. Measures: Utility/robustness and message behaviour.

Outcome: Evidence concerns fault-model-specific preservation, not improved global optimality. Uncertainty: Main argument inspected; supplementary impossibility proof not reconstructed. Threats: Replica/knowledge/round model and synthetic instances; no arbitrary MAS threat coverage. [EMAS-S051]

**EMAS-EMP018 — Existing BDI platform implementation — `IMPLEMENTATION_SEMANTICS`.** Units: Norm-aware BDI running example. Comparison: Operational choices with augmented plans. Sample: One presented running example; no comparative evaluation sample. Measures: Represented compliance/violation/non-applicability choices.

Outcome: Implementation feasibility, not established deployment effect. Uncertainty: Extended-abstract scale and evaluation limit. Threats: Larger populations, overhead, dynamic norms and value validity remain open. [EMAS-S052]

**EMAS-EMP019 — One Overcooked layout, experienced convenience sample — `EMPIRICAL_COMPARISON`.** Units: Human participants in short collaborative game sessions. Comparison: Control versus text versus audio explanations. Sample: 38 analysed of 41 recruits; groups 14/14/10; four 80-second sessions. Measures: Scores, workload, subjective collaboration and exploratory adaptation.

Outcome: No statistically significant performance benefit established. Uncertainty: Limited power; non-significance is not equivalence or no effect. Threats: One layout, expertise imbalance/generalisation and exploratory interpretation. [EMAS-S054]

### Access and attribution limits

**EMAS-A01 — FIPA SC00037J communicative acts and SC00029H Contract Net final-profile leads.** Official HTTP/HTTPS and available lawful mirrors attempted; no readable exact final/current text obtained. Retain separate unavailable source rows; EMAS-013 UNRESOLVED. The readable XC00037H experimental specimen does not stand in for either final work.

**EMAS-A02 — Gaia Southampton discovery record.** Institutional discovery link did not yield the needed text; lawful Oxford author PDF was read. Substantive original-paper coverage recovered; no dependency on repository or sibling output.

**EMAS-A03 — Cohen–Levesque 1991 Teamwork; Littman 1994 Markov games original.** Publisher/lead records and lawful-copy searches did not yield the full needed original text. Do not invent their methods. Joint teamwork examined through 1990/1996/1997 primary works; multi-agent learning through primary later models and explicit imported foundations. Earlier exact origins remain limited.

**EMAS-A04 — Norm enforceability PDF page image.** Primary text was readable; one screenshot retrieval failed. No numerical or figure-derived claim depends on that unavailable image.

**EMAS-A05 — FT-DCOP supplementary proof.** Main paper including theorem statement, construction, main argument and experiments inspected; supplemental impossibility proof not independently checked. Theory/inspection partition explicitly limited; no machine-checked proof claim.

**EMAS-A06 — Unsuccessful secondary leads on agent-death recovery, human crowd influence and later protocol comparisons.** Lawful primary-copy attempts included inaccessible/captcha or empty-viewer results. Those unread studies are not substantive evidence and their apparent findings were not used. Required families are covered through the identified readable sources.

### Citation and exact-work register

Stable source IDs below resolve to the full JSON source table, including per-property links, access dates, evidence roles and programme dependence. URLs identify the inspected work or explicitly unavailable lead, not an assertion that an inaccessible work was read. Every access date is 6 September 2026.

**EMAS-S001. Intelligent Agents: Theory and Practice.** Michael Wooldridge; Nicholas R. Jennings. 1995-06. Knowledge Engineering Review 10(2); author HTML.

Source: <https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/ker95/ker95-html.html>. DOI: `10.1017/S0269888900008122`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Opening; weak and strong notions of agency; Social aspects of agency subsections.

**EMAS-S002. International Foundation for Autonomous Agents and Multiagent Systems: About.** IFAAMAS. undated; accessed 2026-09-06. Live community page.

Source: <https://ifaamas.org/>. Access: `FULL_PAGE`. Locators: About IFAAMAS / AAMAS history.

**EMAS-S003. Proceedings of the 25th International Conference on Autonomous Agents and Multiagent Systems.** Christopher Amato; Louise Dennis; Viviana Mascardi; John Thangarajah (editors); IFAAMAS. 2026-05-25/2026-05-29. AAMAS 2026; ISBN 979-8-4007-2317-9.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/>. Access: `INDEX_AND_CONTENTS`. Locators: Publisher index; complete contents page.

**EMAS-S004. The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver.** Reid G. Smith. 1980-12. IEEE Transactions on Computers C-29(12), 1104–1113; author copy.

Source: <https://www.reidgsmith.com/The_Contract_Net_Protocol_Dec-1980.pdf>. DOI: `10.1109/TC.1980.1675516`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: pp. 1104–1113: introduction, protocol and task-connection discussion; first-page image.

**EMAS-S005. Frameworks for Cooperation in Distributed Problem Solving.** Reid G. Smith; Randall Davis. 1981-01. IEEE Transactions on Systems, Man, and Cybernetics; author copy.

Source: <https://www.reidgsmith.com/Frameworks_for_Cooperation_in_Distributed_Problem_Solving_Jan-1981.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Opening and task-sharing/result-sharing sections.

**EMAS-S006. Using Partial Global Plans to Coordinate Distributed Problem Solvers.** Edmund H. Durfee; Victor R. Lesser. 1987. IJCAI-87, pp. 875–883.

Source: <https://www.ijcai.org/Proceedings/87-2/Papers/065.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§II–IV; Figure 1; experimental discussion pp. 881–882.

**EMAS-S007. On Acting Together.** Hector J. Levesque; Philip R. Cohen; José H. T. Nunes. 1990. AAAI-90 primary paper.

Source: <https://cse-robotics.engr.tamu.edu/dshell/cs631/papers/Levesque-AAAI90.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Joint persistent goals and joint intention definitions; concluding discussion.

**EMAS-S008. Collaborative Plans for Complex Group Action.** Barbara J. Grosz; Sarit Kraus. 1996. Artificial Intelligence 86(2), 269–357.

Source: <https://jmvidal.cse.sc.edu/library/grosz96a.pdf>. DOI: `10.1016/0004-3702(95)00103-4`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §4.3; §6 partial/full SharedPlans; pp. 307, 334–336.

**EMAS-S009. Towards Flexible Teamwork.** Milind Tambe. 1997. Journal of Artificial Intelligence Research 7, 83–124; arXiv cs/9709101.

Source: <https://arxiv.org/pdf/cs/9709101>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: STEAM architecture; §4 decision-theoretic communication; teamwork monitoring and repair discussion.

**EMAS-S010. Team Coordination among Distributed Agents: Analyzing Key Teamwork Theories and Models.** David V. Pynadath; Milind Tambe. 2002. AAAI Spring Symposium technical paper.

Source: <https://cdn.aaai.org/Symposia/Spring/2002/SS-02-04/SS02-04-013.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: COM-MTDP formulation and communication analysis.

**EMAS-S011. Commitments and conventions: The foundation of coordination in multi-agent systems.** Nicholas R. Jennings. 1993. Knowledge Engineering Review 8(3), 223–250; publisher PDF.

Source: <https://maxapress.com/data/article/ker/preview/pdf/S0269888900000205.pdf>. DOI: `10.1017/S0269888900000205`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Commitment/convention distinction; conclusions pp. 246–247.

**EMAS-S012. KQML—A Language and Protocol for Knowledge and Information Exchange.** Tim Finin; Rich Fritzson; Don McKay; Robin McEntire. 1994. AAAI workshop WS-94-02 paper; not the distinct CIKM edition.

Source: <https://cdn.aaai.org/Workshops/1994/WS-94-02/WS94-02-007.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Opening; language architecture and example performatives.

**EMAS-S013. Agent Communication Languages: Rethinking the Principles.** Munindar P. Singh. 1998-12. Computer 31(12), 40–47; author PDF.

Source: <https://www.csc2.ncsu.edu/faculty/mpsingh/papers/mas/computer-acl-98.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: pp. 40–47; especially p. 44 public versus private semantics.

**EMAS-S014. FIPA Communicative Act Library Specification.** Foundation for Intelligent Physical Agents. 2001-08-10. XC00037H; EXPERIMENTAL; approved 2001-01-29; copyright 2000.

Source: <https://jmvidal.cse.sc.edu/library/XC00037H.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Cover and foreword; §§2–3; Inform and Request entries; informative semantic annex.

**EMAS-S015. FIPA Communicative Act Library Specification (SC00037J retrieval lead).** Foundation for Intelligent Physical Agents. 2002 (lead; final cover not inspected). Purported SC00037J standard version; current issuer access unavailable.

Source: <http://www.fipa.org/specs/fipa00037/SC00037J.html>. Access: `UNAVAILABLE`. Locators: No accessible final-version text; official HTML/PDF retrieval attempts and alternate mirror attempts.

**EMAS-S016. Semantics and Verification of Information-Based Protocols.** Munindar P. Singh. 2012. AAMAS 2012 primary paper.

Source: <https://www.csc2.ncsu.edu/faculty/mpsingh/papers/mas/AAMAS-12-BSPL.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Protocol/information definitions; §3.5 enactability and liveness; PurchaseNoShip example.

**EMAS-S017. Interaction Protocols in an Imperative Agent-Oriented Programming Language: the case of BSPL and SARL.** Matteo Baldoni; Cristina Baroglio; Stéphane Galland; Roberto Micalizio; Fatma Outay; Stefano Tedeschi. 2025-05. AAMAS 2025 extended abstract, 2426–2427.

Source: <https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p2426.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Both pages: translation and implementation approach.

**EMAS-S018. The Gaia Methodology for Agent-Oriented Analysis and Design.** Michael Wooldridge; Nicholas R. Jennings; David Kinny. 2000. Autonomous Agents and Multi-Agent Systems 3, 285–312; author manuscript.

Source: <https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/jaamas2000b.pdf>. DOI: `10.1023/A:1010071910869`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §1 scope; role/interaction models; conclusion.

**EMAS-S019. MOISE+: towards a structural, functional, and deontic model for MAS organization.** Jomi Fred Hübner; Jaime Simão Sichman; Olivier Boissier. 2002. AAMAS 2002 short paper, 501–502.

Source: <https://www.researchgate.net/publication/221456372_MOISE_Towards_a_Structural_Functional_and_Deontic_model_for_MAS_organization>. DOI: `10.1145/544741.544858`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Author-posted paper text: structural, functional and deontic specifications; soccer example.

**EMAS-S020. Normative Multi-Agent Programs and Their Logics.** Mehdi Dastani; Davide Grossi; John-Jules Ch. Meyer; Nick Tinnemeier. 2008. Dagstuhl Seminar Proceedings 08361.9.

Source: <https://drops.dagstuhl.de/storage/16dagstuhl-seminar-proceedings/dsp-vol08361/DagSemProc.08361.9/DagSemProc.08361.9.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§2–4; one-based PDF pp. 3–5 assumptions and operational semantics.

**EMAS-S021. Norm Enforceability in Electronic Institutions?.** Natalia Criado; Estefania Argente; Antonio Garrido; Juan A. Gimeno; Francesc Igual; Vicente Botti; Pablo Noriega; Adriana Giret. 2011 (published volume); COIN 2010 event. Author/institutional manuscript corresponding to LNCS 6541, 250–267.

Source: <https://www.iiia.csic.es/media/filer_public/b1/d3/b1d3d503-7cad-44c8-97dc-f3e4e8bfb547/4547.pdf>. DOI: `10.1007/978-3-642-21268-0_14`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§1–3; mWater example and grievance scene; publisher bibliographic record.

**EMAS-S022. Multi-Agent Systems: Technical & Ethical Challenges of Functioning in a Mixed Group.** Ya’akov Gal; Barbara J. Grosz. 2022. Daedalus 151(2), author/publisher PDF.

Source: <https://www.amacad.org/sites/default/files/publication/downloads/Daedalus_Sp22_08_Gal&Grosz.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Mixed-group technical and ethical challenges discussion.

**EMAS-S023. Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations.** Yoav Shoham; Kevin Leyton-Brown. 2009; manuscript revision also ©2010. Uncorrected manuscript Revision 1.1, not a silently substituted later edition.

Source: <https://www.masfoundations.org/mas.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Game/solution concept definitions; repeated games; social choice and mechanism-design chapters.

**EMAS-S024. Efficient Mechanisms for Bilateral Trading.** Roger B. Myerson; Mark A. Satterthwaite. 1983. Journal of Economic Theory 29(2), 265–281.

Source: <https://www.cs.princeton.edu/courses/archive/spr08/cos444/papers/myerson_satterthwaite83.pdf>. DOI: `10.1016/0022-0531(83)90048-0`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §2 model, theorem and efficiency corollary; p. 268 definitions.

**EMAS-S025. Manipulation of Voting Schemes: A General Result.** Allan Gibbard. 1973. Econometrica 41(4), 587–601.

Source: <https://rohitvaish.in/data/Papers/%5BGibbard%5D%20Manipulation%20of%20Voting%20Schemes%20-%20A%20General%20Result.pdf>. DOI: `10.2307/1914083`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Voting-scheme definitions and main theorem; opening model.

**EMAS-S026. The Distributed Constraint Satisfaction Problem: Formalization and Algorithms.** Makoto Yokoo; Edmund H. Durfee; Toru Ishida; Kazuhiro Kuwabara. 1998-09/1998-10. IEEE Transactions on Knowledge and Data Engineering 10(5), 673–685.

Source: <https://jmvidal.cse.sc.edu/library/yokoo98a.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §2 communication assumptions; asynchronous backtracking/weak-commitment search; experimental metric footnote.

**EMAS-S027. ADOPT: Asynchronous Distributed Constraint Optimization with Quality Guarantees.** Pragnesh Jay Modi; Wei-Min Shen; Milind Tambe; Makoto Yokoo. 2005. Artificial Intelligence 161, 149–180.

Source: <https://robots.isi.edu/prl/modi2005adopt-asynchronous-distributed-constraint.pdf>. DOI: `10.1016/j.artint.2004.09.003`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Algorithm and lower/upper-bound quality guarantees; formulation and conclusions.

**EMAS-S028. A Scalable Method for Multiagent Constraint Optimization.** Adrian Petcu; Boi Faltings. 2005. IJCAI-05 DPOP primary paper.

Source: <https://www.ijcai.org/Proceedings/05/Papers/0445.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Pseudotree/UTIL/VALUE algorithm; Theorem 1.

**EMAS-S029. A Privacy-Preserving Algorithm for DCOP.** Tal Grinshpoun; Tamir Tassa. 2014. AAMAS 2014 primary paper.

Source: <https://www.openu.ac.il/Lists/MediaServer_Documents/PersonalSites/TamirTassa/dcops_aamas.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§2–5 privacy definition, secure subprotocols and costs.

**EMAS-S030. Distributed Constraint Optimization Problems and Applications: A Survey.** Ferdinando Fioretto; Enrico Pontelli; William Yeoh. 2018. JAIR 61, 623–698; journal version, not 2016 preprint.

Source: <https://www.jair.org/index.php/jair/article/download/11185/26392/20715>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Taxonomy of classical, dynamic and probabilistic DCOPs; algorithm trade-offs.

**EMAS-S031. On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games.** Phan Minh Dung. 1995. Artificial Intelligence 77, 321–357.

Source: <https://jmvidal.cse.sc.edu/library/dung95a.pdf>. DOI: `10.1016/0004-3702(94)00041-X`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §2, pp. 325–330: admissible, preferred, stable and grounded extensions.

**EMAS-S032. Multi-Agent Actor-Critic for Mixed Cooperative–Competitive Environments.** Ryan Lowe; Yi Wu; Aviv Tamar; Jean Harb; Pieter Abbeel; Igor Mordatch. 2017. NeurIPS 2017 (MADDPG).

Source: <https://papers.neurips.cc/paper/7217-multi-agent-actor-critic-for-mixed-cooperative-competitive-environments.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Centralised critic/decentralised actor formulation; mixed cooperative-competitive particle tasks.

**EMAS-S033. QMIX: Monotonic Value Function Factorisation for Deep Multi-Agent Reinforcement Learning.** Tabish Rashid; Mikayel Samvelyan; Christian Schroeder de Witt; Gregory Farquhar; Jakob Foerster; Shimon Whiteson. 2018. ICML / PMLR 80, 4295–4304.

Source: <https://proceedings.mlr.press/v80/rashid18a/rashid18a.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Monotonic mixing condition and decentralised argmax; experimental sections.

**EMAS-S034. “Other-Play” for Zero-Shot Coordination.** Hengyuan Hu; Adam Lerer; Alex Peysakhovich; Jakob Foerster. 2020. ICML / PMLR 119, 4399–4410.

Source: <https://proceedings.mlr.press/v119/hu20a/hu20a.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Symmetry-randomised objective; cross-play and Hanabi experiments; §7 failed alternative approaches.

**EMAS-S035. An Extended Benchmarking of Multi-Agent Reinforcement Learning Algorithms in Complex Fully Cooperative Tasks.** George Papadopoulos; Andreas Kontogiannis; Foteini Papadopoulou; Chaido Poulianou; Ioannis Koumentis; George Vouros. 2025-05. AAMAS 2025, pp. 1613–1622.

Source: <https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1613.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§4–5; experimental protocol; Tables 4–9 and associated discussion.

**EMAS-S036. Why Do Multi-Agent LLM Systems Fail?.** Mert Cemri; Melissa Z. Pan; Shuyi Yang; Lakshya A Agrawal; Bhavya Chopra; Rishabh Tiwari; Kurt Keutzer; Aditya Parameswaran; Dan Klein; Kannan Ramchandran; Matei Zaharia; Joseph E. Gonzalez; Ion Stoica. 2025-10-26. arXiv:2503.13657v3; original March 2025; v3 inspected.

Source: <https://arxiv.org/html/2503.13657v3>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§3–5; taxonomy development and annotation details; appendices on scaling/limitations.

**EMAS-S037. Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets.** Dat Tran; Douwe Kiela. 2026-04-02. arXiv:2604.02460v1.

Source: <https://arxiv.org/html/2604.02460v1>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§3–5; Table 1; context-degradation argument and budget caveats.

**EMAS-S038. Benchmarking Open-Ended Multi-Agent Coordination in Language Agents.** Kale-ab Abebe Tessera; Andras Szecsenyi; Cameron Barker; Alexander Rutherford; Davide Paglieri; Aidan Scannell; Henry Gouk; Elliot J. Crowley; Tim Rocktäschel; Amos Storkey. 2026-06-06. arXiv:2606.08340v1; alem benchmark.

Source: <https://arxiv.org/html/2606.08340v1>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§3–4; evaluation protocol; reward decomposition and environment interface; §4.2.2 communication ablation, body paragraphs; §4.1 evaluation protocol.

**EMAS-S039. The Role of Social Learning and Collective Norm Formation in Fostering Cooperation in LLM Multi-Agent Systems.** Prateek Gupta; Qiankun Zhong; Hiromu Yakura; Thomas Eisenmann; Iyad Rahwan. 2026-05. AAMAS 2026 research paper, pp. 1238–1246.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/CZDC3237.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§3–4 common-pool-resource model, adaptation/norm procedures and measures.

**EMAS-S040. Algorithmic Collusion at Test Time: A Meta-game Design and Evaluation.** Yuhong Luo; Daniel Schoepflin; Xintong Wang. 2026-05. AAMAS 2026 research paper; DOI SVWG7670.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/SVWG7670.pdf>. DOI: `10.65109/SVWG7670`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§3–4: meta-game construction; §4.3 LLM pricing; Table 3.

**EMAS-S041. Too Many Specialists: Emergent Inefficiencies and Bottlenecks for Multi-agent Ad-hoc Collaboration.** Benjamin Panny; Shashank Mehrotra; Zahra Zahedi; Teruhisa Misu; Kumar Akash. 2026-05. AAMAS 2026 EXTENDED ABSTRACT, 3609–3611.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/CYXP1261.pdf>. DOI: `10.65109/CYXP1261`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: All three pages; Figure 1 and task/trait definitions.

**EMAS-S042. ARMOR Security for Los Angeles International Airport.** James Pita; Manish Jain; Fernando Ordóñez; Christopher Portway; Milind Tambe; Craig Western; Praveen Paruchuri; Sarit Kraus. 2008. AAAI-08 demonstration paper, 1884–1885.

Source: <https://cdn.aaai.org/AAAI/2008/AAAI08-331.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Both pages: deployment date, security-game approach and human constraints.

**EMAS-S043. A Disaster Response System based on Human-Agent Collectives.** Sarvapali D. Ramchurn; Trung Dong Huynh; Feng Wu; Yuki Ikuno; Jack Flann; Luc Moreau; Joel E. Fischer; Wenchao Jiang; Tom Rodden; Edwin Simpson; Steven Reece; Stephen Roberts; Nicholas R. Jennings. 2016-12. JAIR 57, 661–708; PDF filename contains 2017.

Source: <https://www.robots.ox.ac.uk/~sjrob/Pubs/jair_disaster_response_2017.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Mixed-initiative allocation and replanning; field trials; expert feedback; one-based PDF pp. 33, 40–41.

**EMAS-S044. Multiagent Commitment Alignment.** Amit K. Chopra; Munindar P. Singh. 2009. AAMAS 2009 author manuscript.

Source: <https://www.lancaster.ac.uk/staff/chopraak/pdfs/alignment-2009.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Assumptions A1–A4; quiescence/valid observations; integrity rules R1–R8; Theorem 1.

**EMAS-S045. An Implementation of the Contract Net Protocol Based on Marginal Cost Calculations.** Tuomas Sandholm. 1993. AAAI-93, 256–262.

Source: <https://cdn.aaai.org/AAAI/1993/AAAI93-039.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Introduction; bidding/award marginal-cost model; task clustering and TRACONET tests.

**EMAS-S046. Issues in Automated Negotiation and Electronic Commerce: Extending the Contract Net Framework.** Tuomas Sandholm; Victor R. Lesser. 1995. ICMAS-95, 328–335; original concept paper, not later reprint.

Source: <https://cdn.aaai.org/ICMAS/1995/ICMAS95-044.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§1–5: conditional decommitment penalties, costly reasoning, task linkage and multiagent contracts.

**EMAS-S047. Knowledge and Common Knowledge in a Distributed Environment.** Joseph Y. Halpern; Yoram Moses. 1990. Journal of the ACM 37(3), 549–587; not the 2000 arXiv deposit date.

Source: <https://groups.csail.mit.edu/tds/papers/Halpern/JACM90.pdf>. DOI: `10.1145/79147.79161`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Communication/knowledge model; coordinated attack and common-knowledge limitations.

**EMAS-S048. Improving Factuality and Reasoning in Language Models through Multiagent Debate.** Yilun Du; Shuang Li; Antonio Torralba; Joshua B. Tenenbaum; Igor Mordatch. 2023-05-23. arXiv:2305.14325v1; not the later conference version.

Source: <https://arxiv.org/pdf/2305.14325v1>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Debate procedure and evaluation sections; self-consistency comparison.

**EMAS-S049. Towards Con-resistant Trust Models for Distributed Agent Systems.** Amirali Salehi-Abari; Tony White. 2009. IJCAI-09 primary paper.

Source: <https://www.cs.toronto.edu/~abari/papers/SalehiAbariWhiteIJCAI09.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Direct-trust attack model; §3 revised update rule; experimental setup.

**EMAS-S050. Using the Moise+ for a Cooperative Framework of MAS Reorganisation.** Jomi Fred Hübner; Jaime Simão Sichman; Olivier Boissier. 2004. SBIA 2004; author-posted text.

Source: <https://www.researchgate.net/publication/220974542_Using_the_mathcalM_oise_for_a_Cooperative_Framework_of_MAS_Reorganisation>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: Original paper text: reorganisation phases and controlled organisational change.

**EMAS-S051. Byzantine Fault Tolerance in Distributed Constraint Optimization Problems.** Koji Noshiro; Koji Hasebe. 2026-05. AAMAS 2026 research paper, 1183–1191.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/JZVR6522.pdf>. DOI: `10.65109/JZVR6522`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: FT-DCOP model; Theorem 4.2; §5 replication and Proposition 5.1; §6 evaluation.

**EMAS-S052. Engineering Norm-aware BDI Agents.** Michael Winikoff; Frank Dignum; Sebastian Rodriguez; John Thangarajah. 2026-05. AAMAS 2026 EXTENDED ABSTRACT, 3307–3309.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/SEJS3352.pdf>. DOI: `10.65109/SEJS3352`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §§2–4; goal-plan-tree figures; implementation/evaluation paragraph.

**EMAS-S053. FIPA Contract Net Interaction Protocol Specification (SC00029H retrieval lead).** Foundation for Intelligent Physical Agents. 2002 (lead; final cover not inspected). Purported SC00029H version; current issuer access unavailable.

Source: <http://www.fipa.org/specs/fipa00029/SC00029H.html>. Access: `UNAVAILABLE`. Locators: No accessible specification text; issuer and mirror retrieval attempts.

**EMAS-S054. Evaluating XAI Support From A Hierarchical Reinforcement Learning Policy in Human-Agent Collaboration.** Mateus Levi Simões Fernandes; Alberto Sardinha. 2026-05. AAMAS 2026 extended abstract, 3259–3261; study ethics approval dated 2025-06-11.

Source: <https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/HDMG2174.pdf>. DOI: `10.65109/HDMG2174`. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §2 methodology and §3 preliminary findings, pp. 3259–3260; Figure 2 page image inspected.

**EMAS-S055. Modelling dialogues using argumentation.** Leila Amgoud; Nicolas Maudet; Simon Parsons. 2000. ICMAS 2000, pp. 31–38; inspected author manuscript paginated 1–8.

Source: <https://www.sci.brooklyn.cuny.edu/~parsons/publications/conferences/icmas00.pdf>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §2, manuscript pp.1–2; §§3–4, manuscript pp.2–6; p.4 and p.6 images inspected; End of §4.3, manuscript p.6; §5 and conclusion, pp.6–8.

**EMAS-S056. Dialogue Games in Multi-Agent Systems.** Peter McBurney; Simon Parsons. 2002. Informal Logic 22(3), pp.257–274; issue date as printed, not digitisation date.

Source: <https://informallogic.ca/index.php/informal_logic/article/view/2592/2033>. Access: `FULL_TEXT_TARGETED_INSPECTION`. Locators: §4, pp.261–262; §5, pp.263–264; §6.1, pp.265–267; §§6.2–6.3, pp.267–269.

### Frozen-state interpretation

The freeze stabilises this scope, candidate population, evidence and judgements; it does not declare universal certainty or mandate adoption. Subsequent substantive changes require a new revision and refreshed payload hashes. The manifest inventories these payloads, not itself or the enclosing ZIP. Archive integrity and semantic-reference checks are necessary delivery checks, not additional empirical validation of MAS.
