# Evolved Autonomous Agents

## Independent tradition study and conditional composed system

**Analytical lineage:** `EVOLVED_AUTONOMOUS_AGENTS`  
**Revision:** `EAA-2026-09-06-r1`  
**Research cut-off and access-date basis:** 6 September 2026  
**Status:** FROZEN, subject to the companion manifest’s completed consistency and archive checks.

“Evolved Autonomous Agents” names this report’s criticism-tested analytical synthesis. It is not the name of an established academic school, a new historical origin for agents, a claim of academic consensus, or a declaration that a particular implementation has adopted these findings. The established subject is Autonomous Agents. The study is independent of any host implementation and of the unread neighbouring Multi-Agent Systems and Agent-Oriented Software Engineering corpora.

The frozen population contains **70 examined candidates**. It includes unfavourable and duplicate outcomes rather than counting only desirable mechanisms: 13 strongly retained, 25 retained in evolved form, 17 context-dependent, four assumption-sensitive, one contested, one unresolved, four rejected/disfavoured, two with no general property, one superseded, one ceremonial and one duplicate. The 59 candidates in the four affirmative categories are **not 59 mandatory controls**. Their guards, cheaper alternatives, prerequisites, overlap and retirement conditions are part of their meaning. A criterion can be satisfied by an existing operation; one mechanism can satisfy several criteria. EAA-065 is deliberately retained as a duplicate of EAA-023. EAA-062 is researched but unresolved, not unexamined.

### Central judgement

The strongest surviving account of an autonomous agent is not “a system that does more without people”. It is an entity whose observations, objectives, decisions and real effects remain adequately connected within an explicit environment and scope of authority, despite uncertainty, finite resources and changing conditions. That connection can be realised through a direct reactive policy, deliberate search, a BDI interpreter, a hybrid architecture, a learned policy or a bounded language-model tool user. The more complicated forms earn their place only when their additional discrimination or action capability is useful enough to justify their costs and new failure modes.

This is a **conditional composed system**, not a compulsory list of technologies. It couples usable goal semantics and sufficient environmental information to appropriately bounded decisions; couples executable action to material preconditions and evidence of consequences; and connects failure, changed circumstances and human correction to justified continuation, repair, retirement or revision. Communication and delegation are part of operation, not decorative reporting. An agent’s request can change another actor’s task or expectations only if the recipient actually understands or accepts it in the relevant sense. Likewise, producing a correct answer is not completing an external action, and identifying a desirable change is not possessing authority to make it. These distinctions draw on the planning, practical-reasoning, execution, interface and evaluation sources; their reconciliation here is explicitly researcher interpretation. [EAA-S006, practical-reasoning argument; EAA-S016, reactive execution; EAA-S019, mixed-initiative principles; EAA-S022, §5; EAA-S028, §§4.1–4.2; EAA-S033, reward definition]

The adversarial result is substantive. Maximum autonomy, a universally complete central world model, universally sufficient representation-free control, proxy maximisation as complete fulfilment, and benchmark performance as deployment guarantee are not retained. Continuous reflection is replaced by a bounded, externally evaluated alternative. Mental-state labels without operative semantics are classified as ceremony. A narrow formal account of utility-preserving self-modification is retained with its assumptions; broad assurance for open-ended self-revision remains unresolved.

## 1. What was studied and how evidence was used

The declared object is a single agent situated in an environment, pursuing objectives through observation, decision, communication and action. Other agents and humans enter the study where they affect that agent’s information, authority, commitments or operation. Full strategic equilibria, coalition formation, collective organisation, distributed consensus and the complete software-development lifecycle are not independently reconstructed here; they belong to adjacent traditions. This boundary does not remove documented communication, shared autonomy or goal-interference mechanisms merely because they overlap those traditions.

All ten required families were examined: definitions; environment and state estimation; goals and intentions; architecture alternatives; execution and repair; bounded rationality; learning and memory; communication and delegated autonomy; assurance and evaluation; and contemporary language-model translations. The source register contains **54 exact work/version records**, with access level and actually inspected locators. Three records are deliberately limited to abstract/metadata: Cohen and Levesque’s 1990 intention article, Maes’s 1994 article and the 2013 verification article. They are retained for provenance/access transparency, not used to invent their omitted methods. Related directly inspected works support the operative claims used here. Most remaining sources were read at selected load-bearing sections rather than represented as exhaustively read monographs. Scanned historical pages were visually inspected where needed. [EAA-S007; EAA-S018; EAA-S029; source-table access fields]

The genealogy begins with inspected precursors and founding formulations relevant to the declared problems, not with a claim to cover every antecedent of AI or control theory. Simon’s 1955 resource-relative rationality is a precursor; STRIPS supplies an early explicit planning formulation; the 1980s and 1990s supply contrasting situated, practical-reasoning, BDI, programming and interface-agent approaches. The history neither begins with large language models nor treats all earlier work as a single inadequate generation. [EAA-S013; EAA-S011; EAA-S004–EAA-S010]

The evidence architecture separates historical provenance, definitions, formal results, implementation semantics, empirical comparisons, field/incident evidence and normative criticism. A formal sufficient statistic does not establish that a sensor model corresponds to the world. A language’s operational semantics does not establish that every implementation conforms. A deployment demonstrates possibilities and failure modes without identifying a general causal benefit. A simulation and a selected physical demonstration are not interchangeable. An analytical composition is not a replicated experiment. There is no overall confidence percentage that averages these different questions.

The empirical catalogue records units, settings, comparisons, outcomes, uncertainty and dependence. The two Electric Elves sources describe one programme. DS1’s paper and the public account encountered during discovery concern one mission experiment. ReAct, Reflexion and cost re-evaluations reuse several task families; repeated descriptions do not create new independent replications. Shared benchmark names do not mean every source used every dataset, but they do prevent naive source counting as evidence independence. [EAA-S020–EAA-S022; EAA-S030–EAA-S036]

Current-state coverage includes the 2025 partially observable off-switch result, two inspected AAMAS 2026 papers, a May 2026 version of a user study, a July 2026 version of long-software-task evaluation and an August 2026 physical-agent preprint. Their publication/version dates are distinguished from experiment dates and initial submissions. The 2026 conceptual shared-autonomy extended abstract explicitly defers detailed proofs/experiments; it is not counted as empirical validation. The recent physical-agent work is a preprint, and its main comparison is in a robot simulator. The cut-off marks the end of this search, not proof that every publication before that date has been enumerated. [EAA-S037–EAA-S039; EAA-S041; EAA-S047–EAA-S048]

## 2. Agency is a useful but plural abstraction

Wooldridge and Jennings separate theories, architectures and languages and distinguish weak and stronger notions of agency. Their weak formulation groups autonomy, reactivity, proactivity and social ability. Franklin and Graesser instead make being situated in an environment and sensing and acting over time central to their taxonomy. Luck and d’Inverno distinguish objects, goal-ascribed agents and autonomous agents whose motivations generate their own goals. These are not three interchangeable definitions of the same implementation. They make different boundary choices and answer different questions. [EAA-S001, definitions and classification; EAA-S002, taxonomy; EAA-S003, objects/agents/autonomous agents]

An ordinary pure function need not count as an agent under a persistent situated definition, even though a software environment could embed it inside one. A thermostat-like controller can satisfy a minimal sensing/action account without satisfying richer proactivity or social requirements. A planner can generate a sequence without itself being the situated executor. A personal assistant may act persistently but retain externally assigned goals and limited permission. An embodied robot adds physical sensing and actuation without automatically gaining goal autonomy or general intelligence. These are **analytical comparison cases**, not empirical measurements of named products. Their point is to disclose the definition before making the comparison.

It is therefore useful to describe autonomy along several task-relative dimensions: action selection, goal adoption or change, resources, persistence, learning and freedom from direct intervention. ALFUS provides a documented terminology framework relating mission complexity, environmental difficulty and human independence; it does not validate one universal scalar ranking or prescribe every dimension in this report’s expanded description. A system can have broad action capability but narrow permission, or substantial computational independence but little authority to change a goal. [EAA-S017, terminology/framework; EAA-S043, human autonomy]

Intentional vocabulary can still be useful. It can expose persistent commitments and communication expectations that low-level control descriptions obscure. The requirement is not to eliminate belief or intention terminology but to identify what it predicts or governs. Shoham explicitly objects to arbitrary mental-state labelling. Rao and Georgeff explicitly acknowledge gaps between ideal theory and finite practical interpretation. A prompt that says “you have beliefs and intentions” may influence behaviour, but does not by itself establish the corresponding logic or interpreter. No inference about consciousness, personhood or moral responsibility follows either from that label or from refusing to use it. [EAA-S010, pp.53–54; EAA-S009, practical interpreter and p.316]

## 3. Representation must earn its decision role

Symbolic planning makes action conditions and effects explicit. That permits searching for sequences whose modelled consequences achieve a goal. Its limitation is not that historical planning necessarily ignored execution: STRIPS itself contains execution-related concerns. The relevant criticism is that a represented world and its operators may be incomplete, stale or expensive to maintain, and a valid model-level plan still needs actual capabilities and monitored effects. [EAA-S011, operator/world-model framework and execution discussion]

Brooks’s alternative decomposes control into task-achieving behaviours that remain directly coupled to the world. This challenged the assumption that useful robot behaviour must always pass through comprehensive central representation before action. The inspected September 1985 memo is an antecedent of the 1986 journal article, not that exact edition. The 1991 paper’s creature demonstrations support a challenge to universal necessity, not a proof that no task benefits from internal state. [EAA-S004, visually inspected memo pages; EAA-S005, decomposition and creature discussion]

Partial observability supplies a clear discriminator. Two identical current observations can arise from histories that require different actions. A memoryless policy then lacks a needed distinction. A belief distribution, history summary or smaller state variable may resolve it. In a correctly specified POMDP, belief state is sufficient for choosing actions under the model; that does not mean its transition and observation assumptions have been established empirically. Belief normalisation is not world correspondence. Exact planning may also be too costly, making approximation or a simpler adequate policy preferable. [EAA-S012, §§3.3–3.4 and planning discussion]

The office-agent experience gives this distinction practical force. Treating keyboard inactivity as absence created bad availability inferences. Introducing uncertainty over state is a meaningful response, but increases computational burden and does not remove all observation or privacy problems. The mature property is therefore not “always use a POMDP”. It is to preserve the uncertainty needed for the decision and choose an adequate way to reduce or act under it. Sometimes direct observation is cheaper; sometimes an information-gathering action or question is justified; sometimes the least harmful choice is to wait or abstain. Waiting itself has consequences and is not automatically a safe state. [EAA-S021, availability inference and partial-observation discussion; EAA-S019, uncertainty/dialogue/cost principles]

## 4. Intentions make action stable without making it blind

Practical reasoning distinguishes a plan recipe from an adopted intention. A recipe is one way something could be done. An adopted intention constrains further reasoning and helps organise subsequent action. Without such stability, an agent can repeatedly reconsider everything and never complete useful work. But stability has a purpose, not unconditional priority over all new information. [EAA-S006, manuscript pp.7–9 and intention filtering]

Persistent-goal formulations specify conditions under which pursuit ceases: recognised achievement, impossibility or lost relevance, with qualifications concerning competing commitments. The directly inspected 1990 related report supplies these conditions; the inaccessible main intention article is not used to fabricate additional theorem detail. Rao and Georgeff make intention primitive in a distinct formalisation and analyse different commitment strategies. The disagreement is real: one should not collapse philosophical practical reasoning, one logical reduction and another BDI semantics into a single historical mechanism. [EAA-S052, persistent-goal definition and footnote; EAA-S007, abstract-only limit; EAA-S008, comparison; EAA-S009, p.316]

The operative problem is when to reconsider. The Tileworld study varies environmental change and deliberation cost and shows that their interaction changes which commitment strategy performs better. A cautious replanner may waste expensive computation; a bold continuer may miss consequential change. This gives a discriminator, not an instruction to “balance” vaguely: compare the cost and expected decision value of reconsideration under the actual change rate and action window. A cheap relevance check can justify more expensive reasoning. An existing adequate action may dominate another planning step. [EAA-S015, experiments and printed p.86 graph; EAA-S014, bounded-optimal decision procedures]

Goals also differ in temporal semantics and interaction. Achievement is not maintenance: restoring a resource or condition does not end an obligation to keep it within bounds. Proactive maintenance may prevent a foreseeable violation, but inaccurate estimates can reject feasible tasks or strand the agent. Concurrent plans may each be feasible while interfering through shared resources or effects. Known-plan condition/effect summaries can help, but conservative summaries reduce concurrency and omitted effects miss conflicts. Neither more prediction nor more concurrency analysis is automatically mature. [EAA-S051, introduction and §§5.4.1–5.5; EAA-S054, single-agent parallel goals and summaries]

## 5. Architecture alternatives and their minimum adequate forms

A reactive policy is appropriate when available cues sufficiently determine adequate action and response time matters. Deliberation is appropriate when non-local dependencies or future consequences justify a model and search. A BDI interpreter is appropriate when recurring structured tasks benefit from context-sensitive plan recipes and persistent intention management. A hybrid is appropriate when multiple decision time-scales genuinely contribute and their interfaces can be made coherent. None is a universal successor that renders the others merely historical. [EAA-S004–EAA-S005; EAA-S009; EAA-S011–EAA-S012; EAA-S046]

The 3T account connects planning, sequencing and skill execution, but explicitly allows reduced configurations. It also distinguishes requested execution frequency from hard real-time guarantees. A hybrid can introduce duplicated state, arbitration problems and timing assumptions that were not present in either component considered alone. The architecture has to preserve the meaning of plan requests, active skills, completion events and overrides across its interfaces. A diagram naming three boxes does not establish any of that. [EAA-S046, architecture and §5]

Modern software-agent comparisons add another legitimate branch: a constrained workflow can be competitive with more open-ended action selection. Such evidence is a reason to include credible simpler baselines, not to infer that all autonomy is unnecessary. A fair comparison must account for task selection, retry budgets, information access, tuning and human repair. A model with more attempts can look architecturally superior when the real difference is resource use. [EAA-S035, §2 and reproducibility discussion; EAA-S036, method and benchmark-quality analysis]

The minimal coherent form is therefore small: a declared task and scope, an adequate observation/action interface, an action policy, a resource bound and sufficient evidence of effects. Existing typed capabilities or atomic operation contracts may already establish several of these distinctions. There is no automatic requirement for a separate planner, belief database, reflection module, memory curator, human checkpoint or formal monitor. Richer forms are added when a demonstrated ambiguity, horizon, variability, consequence or coordination problem makes them necessary or worthwhile. This minimum is an analytical selection account grounded in the architectural rivalry; it is not a newly validated standard.

## 6. Action changes the world; reports do not substitute for it

The execution loop connects observation, action selection, dispatch, consequence and revision. It need not be implemented as a single serial pipeline. Fast control can run while a planner searches; a human can change a task while a tool is active; a delayed effect can arrive after another decision. What matters is preserving the dependencies required for valid action.

Capability grounding answers whether the proposed action corresponds to something the executor can do. Applicability answers whether relevant conditions hold now. Authority answers whether that means is permitted. Effect evidence answers what actually occurred. A learned robot affordance can help with feasibility without answering authority, and a plausible language plan can succeed in planning evaluation while failing in execution. The SayCan study explicitly measures planning and execution separately in selected kitchens; those outcomes are not one interchangeable success predicate. [EAA-S049, method and §5]

An acknowledgement can establish receipt, acceptance by a service or actual completion, depending on the contract. Missing acknowledgement can mean that an action failed before execution or that it succeeded without a return message. This matters for retry: duplicating a message, payment-like operation or physical motion may not be harmless, and compensation is another action rather than erasure of history. A trustworthy atomic effect-return contract can be sufficient; redundant ritual checking is not mandatory. Where the effect cannot be established, the correct result may remain unresolved. [EAA-S022, §5; EAA-S044, action-specific control; EAA-S043, consequences and user autonomy; analytical composition EAA-025]

Remote Agent is a particularly valuable adverse case because it was genuine spacecraft operation, not merely an architecture proposal. The report records a race in an unprotected critical section that had not occurred in prior testing. The first run was interrupted; a separate later six-hour plan completed remaining objectives. A patch was developed but not uplinked because there was insufficient time to test it. The lesson is neither “autonomous operation failed altogether” nor “the mission was flawless”. It is that useful operation and concrete integration failure coexist, and a later successful run does not erase the earlier failure or establish that an uninstalled correction was deployed. [EAA-S022, §§4–5]

Repair requires more than another attempt. It must respond to the relevant failure, respect remaining resources and preserve the task. If a planner makes an infeasible request feasible by substituting another destination or object, it may have changed the goal rather than repaired the plan. A recent physical-agent preprint makes this distinction concrete through request-preserving native action checks. Its main comparison uses 20 simulator scenarios, including deliberately unrecoverable faults, so successful blocking is not evidence of general successful recovery. The broader invariant here—separating revision of means from revision of goal or authority—is analytical composition, not an assertion that the preprint proves the entire system. [EAA-S039, §§III–IV]

## 7. Reasoning has an opportunity cost

Bounded rationality is not a concession that disappears once models become larger. The question is how to choose among feasible decision procedures on a particular machine in a changing environment. More calculation can improve an estimate while making the underlying observation obsolete. Queries can cost money; consultations can cost another person’s attention; reflection can consume the window in which an adequate action was available. [EAA-S013; EAA-S014; EAA-S019]

The mature mechanism is an operative resource envelope and an adequate stopping/selection rule. It need not be an exact value-of-computation optimiser. A fixed cap can be adequate for a bounded task. An anytime algorithm helps only if it produces a usable intermediate result and can actually be interrupted. A simple direct policy can dominate a sophisticated metareasoner whose own estimates cost more than they save. Formal bounded-optimal results remain relative to their machine, environment and cost assumptions; they are not a certificate of real-time behaviour for arbitrary software. [EAA-S014, §4; EAA-S046, §5]

This also changes evaluation. Counting only the latency of successful runs or the price of a final answer omits failed attempts and the cost of getting to that result. The useful comparison may include task quality, failure consequence, inference, tools, supervision, recovery and privacy burdens separately. No invented common currency is needed for costs that cannot honestly be quantified. The report therefore retains whole-task cost visibility while refusing to turn it into a universal scalar objective. [EAA-S035, cost/accuracy analysis; EAA-S021, deployment costs; analytical synthesis EAA-048]

## 8. Learning and memory do not certify improvement

A state update, an experience record, a changed model parameter, a revised policy and a changed revision criterion are different transitions. Memory can affect later behaviour without weight updates, as in verbal-feedback methods. A weight update can change behaviour without improving the intended task. The first useful question is what changes, what persists and what later decision consumes it. [EAA-S027, learning update/model; EAA-S031, actor/evaluator/memory architecture; EAA-S053, distinction between learning and self-modification]

Persistent experience can help on repeated regularities, but can also preserve mistakes. The early learning-interface design already distinguishes suggestion from execution and requires user approval before adding an agent-selected example to the relevant memory. That approval is not infallibility, but it is a substantive boundary against learning only from one’s own unverified actions. Modern reflection has the same evidential problem: a generated lesson is not independent confirmation of the outcome that prompted it. [EAA-S044, pp.461–463; EAA-S031, evaluator and limitations]

Reflexion provides both favourable and negative evidence. Its gains differ across tasks and its cumulative multi-trial results cannot be called single-attempt reliability. Some reported self-test comparisons are worse, and its WebShop reflection trials were stopped after failing to improve. These findings materially change the disposition: externally anchored bounded reflection is context-dependent; compulsory continuous reflection is superseded. The same distinction prevents task-simulation believability from being promoted to trustworthy operational memory. [EAA-S031, Tables 1–3 and Appendix B.1; EAA-S050, §6]

Continual learning exposes retention/plasticity trade-offs. Elastic weight consolidation is a specific approximation for limiting changes to parameters important to earlier tasks. It can help in tested sequences, but stronger preservation can obstruct necessary adaptation and cannot decide whether earlier behaviour still deserves preservation. Likewise, convergence of a reinforcement-learning method does not guarantee safe exploration or a correct reward specification. Goal-misgeneralisation experiments show that relevant competence can survive a shift while the behaviour follows a proxy that no longer serves the intended target. These are controlled counterexamples, not measured prevalence in all deployed agents. [EAA-S026, method/experiments; EAA-S027, convergence setting; EAA-S025, §3]

The 2026 SafeQIL work is important precisely because its evidence is bounded. It investigates learning safety information from demonstrations when constraints are unknown. It reports reward and safety cost separately in four simulated tasks. Lower safety cost is not zero violations, and improvement along that dimension can be accompanied by lower reward. The mature conclusion is protected, constraint-aware exploration with residual-risk evidence—not that naming a reward component “safety” establishes safety. [EAA-S038, §5.1 and Table 1]

## 9. Assistance and delegated autonomy are operative relations

An agent’s usefulness is not confined to internal information processing. It acts through people, services and actuators. A message can request information, ask another actor to assume a task, communicate a failure or negotiate a changed objective. These effects depend on the recipient. The formal communication source explicitly distinguishes reception and social acceptance before particular belief or goal transitions. A sent message does not demonstrate that the recipient believes it, agrees with it or has acted on it. [EAA-S028, §§4.1–4.2]

Mixed initiative treats acting, asking, suggesting and doing less as alternatives whose value depends on uncertainty, consequence and user attention. Adjustable autonomy extends this into strategies for transferring control when human response is uncertain. Electric Elves shows why a simple instruction to “ask a person” is insufficient: indefinite waiting and inappropriate fixed-timeout decisions both caused problems. A credible handoff includes non-response and what the system does in the meantime. [EAA-S019, principles; EAA-S020, §2.2 and transfer-of-control framework]

Human readiness is a separate prerequisite. A person who has not been controlling the system may lack practice, current state understanding or enough time to intervene. A nominal button or an elaborate explanation cannot make an infeasible recovery feasible. Conversely, asking for repeated confirmations can reduce meaningful control by overloading the person. The correct question is whether the right participant can use the right information to make a consequential decision at the relevant time. [EAA-S023, p.776; EAA-S043, pp.466–469; EAA-S047, study procedure/findings]

Operational revocation is also distinct from learning-theoretic interruptibility. A real stop or withdrawal must reach active and queued execution, subject to actual actuator and irreversibility limits. A theorem about interruption-neutral learning addresses a different issue: whether learning updates create incentives to avoid or seek interruption. Its assumptions are algorithm-specific and asymptotic. A separate game-theoretic idea—that uncertainty about objectives can promote deference—changes under private information. The 2025 partially observable off-switch game supplies counterexamples to a universal deference inference. These are conditional mechanisms, not interchangeable routes to one guaranteed corrigible agent. [EAA-S024, Assumption 9 and Theorems 14–17; EAA-S040, game model; EAA-S041, Definition 3.2 and Example 4.1]

## 10. Contemporary translation, evaluation and research limits

The contemporary language-model branch has genuine new implementation characteristics without a new origin for agency. ReAct interleaves generated reasoning and action with tool/environment feedback. Reflexion introduces bounded verbal experience between attempts. SayCan combines language relevance with executable skill affordances. Each can be analysed using older distinctions between action, observation, goals, state and resources, but none is thereby proven to implement BDI or inherit all guarantees of a classical architecture. Direct transmission is claimed only where documented; shared problems and analogies are labelled more cautiously. [EAA-S030–EAA-S031; EAA-S049; genealogy edge register]

Untrusted tool text creates a distinctive input-integrity problem. Retrieved material can attempt to impersonate task authority and redirect action. AgentDojo makes this measurable through controlled attacks and defences while tracking legitimate utility. Older communication provenance is a useful conceptual intersection, not proof that sender annotations solve prompt injection. The system therefore needs evidence at its real trust and action boundaries, not only a prompt warning, and changed models/tools can invalidate earlier results. [EAA-S034, threat model/tests/defences; EAA-S028, social acceptance; analytical version boundary EAA-055]

An adequate evaluation must ask at least four different questions. Did the task-instance effect occur? Were required constraints and means respected? Does success recur across comparable trials? Does the result transfer to the intended environment? WebArena provides functional state checking rather than mere plausibility of the final message. τ-bench additionally makes repeated consistency visible, but its outcome reward can still miss a policy requirement such as confirmation. A task can therefore be scored correct and still fail the relevant delegated-action claim. [EAA-S032, functional correctness; EAA-S033, reward and repeated-trial definitions]

Benchmarks also have task construction, reset, version, cost and dependence limits. A 50% completion horizon measured using human expert task time is not a statement that the agent can run safely for that many hours, nor a service reliability guarantee. The July 2026 manuscript’s date does not turn every model it evaluates into the current best model. Similarly, the May 2026 user-study version offers qualitative evidence from 31 participants in bounded sessions, not representative population failure rates. These distinctions protect both favourable findings and their limits from exaggeration. [EAA-S048, metric definition and evaluation scope; EAA-S047, §4]

Formal assurance belongs in this picture, but at its actual scope. A runtime monitor can detect violations of assumptions used in verification when those assumptions are observable and represented adequately. It does not prove unmodelled behaviour safe or automatically create a recovery. A failure outside a theorem’s assumptions does not refute the theorem; it can nevertheless invalidate an implementation’s claim to that theorem. These are separate adjudications, not rival preferences for “formal” versus “practical” evidence. [EAA-S042, assumption monitoring; EAA-S009, theory/practice gap; EAA-S022, integration failure]

Self-revision makes that separation especially important. A formal self-modification model can preserve predecessor utility when future policy consequences are properly evaluated under strong assumptions. Preserving a wrong initial utility is not safe adaptation, and the paper identifies tensions with corrigibility and value learning. This is a useful narrow result, not grounds for claiming universal self-assurance or for declaring further progress impossible. The unresolved question is how to combine legitimate revisability, continuity, imperfect prediction, non-tampering and externally justified constraints in broader implementable systems. [EAA-S053, Theorem 12 and §6; EAA-S041, private-information limits; analytical EAA-062]

## Reading and using the evidence packet

The next sections provide the dated genealogy, full denominator and detailed domain/composition account. Every ID resolves to its complete record in `EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json`. Source IDs resolve to exact works, versions, locators, access levels and evidence cases in `EVOLVED_AUTONOMOUS_AGENTS_SOURCE_TABLE.json`. The separate audit intake asks neutral questions of an unspecified real system; the public-documentation intake supplies citation-ready claims and explicit prohibitions on overclaiming; the synthesis intake exports this lane without answering for unread neighbours.

Freeze means that this declared population, scope, evidence and judgements are stable at the named revision. It does not mean all future research is settled, every implementation must adopt every retained mechanism, or the integrated analytical system has been empirically validated as a whole. Substantive later changes require a new revision rather than silent replacement of this denominator.

## EVOLVED_AUTONOMOUS_AGENTS_TIMELINE

Dates below distinguish original work, inspected edition, event and reported deployment. They form a plural timeline, not a universal progress ladder.

### 1955 — Bounded rationality precursor (`EAA-G01`)

**Problem:** Ideal rationality ignores finite human/computational means.

**Mechanism and contribution:** Satisficing and aspiration-relative decision reasoning. Supplies a resource-relative problem formulation, not a complete agent architecture.

**Reception / limit:** Historical precursor; no claim that Simon alone founded autonomous agents. [EAA-S013]

### 1971 — Symbolic planning and world-model operators (`EAA-G02`)

**Problem:** Find action sequences that achieve goal conditions.

**Mechanism and contribution:** STRIPS operators over represented conditions and effects, with execution-related concerns. Explicit action/goal relations support deliberation and later execution machinery.

**Reception / limit:** Model and search assumptions delimit feasibility; symbolic planning did not uniformly ignore execution. [EAA-S011]

### 1983 — Human-factors criticism of automation (`EAA-G03`)

**Problem:** People become responsible for failures while losing practice and timely situation understanding.

**Mechanism and contribution:** Analyse vigilance, skill retention and recovery after automation failure. Makes actual readiness a prerequisite for useful oversight.

**Reception / limit:** Imported human-factors analysis, not an autonomous-agent controlled trial. [EAA-S023]

### 1985 memo / 1986 journal antecedent — Situated behaviour-based control (`EAA-G04`)

**Problem:** Traditional central reconstruction can be too slow and brittle for mobile robots.

**Mechanism and contribution:** Task-achieving layers and asynchronous world-facing behaviours. Direct environmental coupling challenges compulsory central representations.

**Reception / limit:** Inspected 1985 memo and 1991 paper, not exact 1986 journal text; simple creatures do not establish universal model dispensability. [EAA-S004; EAA-S005]

### 1987 — Reactive execution packages (`EAA-G05`)

**Problem:** Complex action takes place in changing contexts where plans need local alternatives.

**Mechanism and contribution:** RAP selection, condition checks, execution monitoring and recovery. Execution becomes an ongoing context-sensitive process rather than a one-time plan issue.

**Reception / limit:** Requires useful local conditions, methods and failure evidence. [EAA-S016]

### 1988 paper; philosophical work discussed therein — Plans and resource-bounded practical reasoning (`EAA-G06`)

**Problem:** Reasoning from scratch and continually changing intentions wastes resources and frustrates coordinated action.

**Mechanism and contribution:** Adopted intentions filter later deliberation, distinct from plan recipes. Connects practical reasoning with computational resource bounds.

**Reception / limit:** The source supports philosophical inspiration, not identity of philosophy, logic and interpreter; manuscript edition is undated. [EAA-S006]

### 1990 — Intention and persistent-goal logic (`EAA-G07`)

**Problem:** Specify what distinguishes intention from merely wanting an outcome.

**Mechanism and contribution:** Persistence under achievement, feasibility and relevance conditions. A formal account of commitment and its termination.

**Reception / limit:** Main intention article abstract-only; directly inspected related report supports the stated persistent-goal conditions. [EAA-S007; EAA-S052]

### 1991 / 1995 — BDI formal architecture and interpreter approximation (`EAA-G08`)

**Problem:** Represent beliefs, desires and intentions and obtain practical bounded action.

**Mechanism and contribution:** Primitive intention, branching-time semantics and constrained interpreter/plan-library operation. Makes multiple commitment strategies explicit and identifies theory/practice gaps.

**Reception / limit:** Primitive-intention formulation is not definitionally identical to the Cohen–Levesque reduction. [EAA-S008; EAA-S009]

### 1991 — Empirical commitment trade-offs (`EAA-G09`)

**Problem:** Select persistence versus reconsideration under different environmental change and thinking costs.

**Mechanism and contribution:** Tileworld simulation using a simplified PRS-style agent. Demonstrates that reconsideration cost can reverse the relative performance of strategies.

**Reception / limit:** Artificial environment and limited agent model; no universal schedule or field effect size. [EAA-S015]

### 1992 — Tabular reinforcement-learning foundation (`EAA-G10`)

**Problem:** Learn useful action values from interaction without a fully supplied transition model.

**Mechanism and contribution:** Q-learning updates with convergence under specified sampling and model conditions. Learning supplies a distinct action-selection route.

**Reception / limit:** Convergence does not validate reward semantics, safe exploration or arbitrary function approximation. [EAA-S027]

### 1993 — Agent-oriented programming (`EAA-G11`)

**Problem:** Give intentional abstractions computational roles rather than arbitrary labels.

**Mechanism and contribution:** Mental-state language and AGENT0 interpreter. Distinguishes usable program semantics from a merely anthropomorphic description.

**Reception / limit:** Not a full AOSE lifecycle methodology, and not evidence of consciousness. [EAA-S010]

### 1993 / 1994 publication lead — Learning information/interface agents (`EAA-G12`)

**Problem:** Reduce recurring user work while allowing individual variation and control.

**Mechanism and contribution:** Example-based preference learning, action-specific tell-me/do-it thresholds and approved memory updates. Links adaptive assistance to human control rather than maximal independent action.

**Reception / limit:** 1993 tests use simulated users; 1994 article is metadata-only in this run. [EAA-S044; EAA-S018]

### 1995 — Plural agent definitions and taxonomy (`EAA-G13`)

**Problem:** The term agent is used for non-equivalent objects, theories, architectures and languages.

**Mechanism and contribution:** Survey classification plus formal objects/agents/motivated-autonomous-agent distinctions. Establishes plurality rather than a single newly invented methodology.

**Reception / limit:** Definitions are engineering/theoretical choices, not comparative proof of implementation quality. [EAA-S001; EAA-S003]

### 1995 — Machine-relative bounded optimality (`EAA-G14`)

**Problem:** Choose decision procedures under actual computational and environmental constraints.

**Mechanism and contribution:** Formal comparison of feasible programs; anytime/deadline and simulated task examples. Makes computation itself an action-selection cost.

**Reception / limit:** Guarantees relative to the stipulated machine, cost and environment. [EAA-S014]

### 1995 workshop author version — Hybrid planning, sequencing and skills (`EAA-G15`)

**Problem:** Combine slower planning with reactive skills in embodied tasks.

**Mechanism and contribution:** 3T interfaces across planning, sequencing and skill management. Supports mixed time-scales while acknowledging reduced-tier alternatives.

**Reception / limit:** Author experience rather than controlled superiority; requested frequencies do not ensure hard real-time operation. [EAA-S046]

### 1996 event / 1997 proceedings — Situated persistent-agent taxonomy (`EAA-G16`)

**Problem:** Distinguish agents from programs without requiring human-like intelligence.

**Mechanism and contribution:** Environmental embeddedness, sensing and acting over time. A useful operational boundary compatible with many mechanisms.

**Reception / limit:** Workshop and publication dates differ; not equivalent to every motivation-based definition. [EAA-S002]

### 1996 — Planning-based software agents (`EAA-G17`)

**Problem:** Use executable internet/software tools to satisfy declarative information and action goals.

**Mechanism and contribution:** Tool selection, information gathering and planning over software actions. Documented domain translation of planning to software environments well before LLM tools.

**Reception / limit:** Author programme scope, not a census of all information agents or a universal success rate. [EAA-S045]

### 1997 — Software-agent user-autonomy criticism (`EAA-G18`)

**Problem:** Agent independence can hide decision criteria or reduce meaningful human control.

**Mechanism and contribution:** Distinguish capability, complexity, knowledge, misrepresentation and fluidity of control. Makes human/affected-party autonomy a separate criterion from agent autonomy.

**Reception / limit:** Normative arguments and examples, not a legal code or frequency estimate. [EAA-S043]

### 1998 — Partial-observation planning synthesis (`EAA-G19`)

**Problem:** Act under uncertain latent state and stochastic outcomes.

**Mechanism and contribution:** Belief-state update and planning under a specified POMDP. Unifies information gathering with action choice and exposes model/tractability limits.

**Reception / limit:** Sufficiency assumes an adequate model; probability coherence is not correspondence. [EAA-S012]

### 1999 — Mixed initiative and practical autonomous deployment (`EAA-G20`)

**Problem:** Coordinate useful assistance and demonstrate on-board planning/execution under real constraints.

**Mechanism and contribution:** Cost-sensitive user interaction; Remote Agent planner/executive/diagnosis experiment. Shows both useful autonomous operation and the importance of integration/oversight.

**Reception / limit:** Distinct programmes, not one lineage event; DS1 had a race and ground intervention before remaining objectives were completed. [EAA-S019; EAA-S022]

### 2000 deployment / 2002 analysis; later undated lessons copy — Adjustable autonomy and Electric Elves (`EAA-G21`)

**Problem:** Office coordination requires decisions despite uncertain human availability and preferences.

**Mechanism and contribution:** Transfer-of-control strategies, response/cost modelling and revisions after failures. Non-response, bad state proxies and privacy materially narrow simplistic assistance designs.

**Reception / limit:** One shared industrial/academic programme; the lessons manuscript’s exact publication year remains uncertain. [EAA-S020; EAA-S021]

### 2003 / accepted 2012, journal 2014 — Concurrent and maintenance goals (`EAA-G22`)

**Problem:** Multiple intentions interfere; continuing conditions differ from one-time achievement.

**Mechanism and contribution:** Plan summaries and condition/effect interference; reactive/predictive maintenance. Extends operational goal reasoning beyond a single flat achievement target.

**Reception / limit:** Known-plan and model assumptions; maintenance simulation shows model-error trade-offs. [EAA-S054; EAA-S051]

### 2007 / 2008 terminology edition — Communication semantics and autonomy dimensions (`EAA-G23`)

**Problem:** Messages need operational meaning; autonomy comparisons need explicit dimensions.

**Mechanism and contribution:** Agent-language receive/accept transitions; mission/environment/human-independence vocabulary. Separates sending from believing/adopting and context from autonomy score.

**Reception / limit:** Distinct works; specification/terminology does not establish adoption or benefit. [EAA-S028; EAA-S017]

### 2016–2018 — Learning interruption, self-modification, retention and runtime assumptions (`EAA-G24`)

**Problem:** Learn and revise without distorting objectives or silently leaving verified conditions.

**Mechanism and contribution:** Algorithm-specific interruption updates; predecessor-utility analysis; EWC; off-switch game; assumption monitors. Supplies several narrow mechanisms rather than one general safe-agent theorem.

**Reception / limit:** Different models and objectives can conflict; ideal assumptions and deployment validation remain distinct. [EAA-S024; EAA-S053; EAA-S026; EAA-S040; EAA-S042]

### 2022–2023 — Grounded language action and memory-based agents (`EAA-G25`)

**Problem:** Use language-conditioned policies and feedback across tool, robot and simulated-social tasks.

**Mechanism and contribution:** Skill affordances, reason–act interleaving, evaluator/text-memory loops and retrieval. Documented new implementations with older agent/control intersections.

**Reception / limit:** Planning/execution gaps, proxy misgeneralisation and negative reflection results prevent universal improvement claims. [EAA-S025; EAA-S049; EAA-S030; EAA-S031; EAA-S050]

### 2024 — Interactive benchmarks, prompt injection and cheaper baselines (`EAA-G26`)

**Problem:** Measure real action, reliability, tool-input integrity and resource-sensitive performance.

**Mechanism and contribution:** Functional outcomes, repeated-trial reliability, adversarial suites and constrained workflows. Improves discrimination between output quality, effective action and evaluation artefacts.

**Reception / limit:** Oracle omissions, shared benchmarks, task quality and cost confounding remain. [EAA-S032; EAA-S033; EAA-S034; EAA-S035; EAA-S036]

### 2025 — Partially observable deference counterexample (`EAA-G27`)

**Problem:** Does uncertainty still imply deference when each actor has private information?

**Mechanism and contribution:** A finite common-payoff Bayesian off-switch game. Narrower deference claims; more communication need not monotonically promote deference.

**Reception / limit:** Formal extension, not field evidence of agent shutdown behaviour. [EAA-S041]

### 2026 through 6 September — Current shared autonomy, safety learning and long-task/physical evaluation (`EAA-G28`)

**Problem:** Make human engagement, unsafe exploration, long-horizon measures and execution boundaries explicit.

**Mechanism and contribution:** Conceptual interaction framework; SafeQIL simulation; user study; task-time horizon; native action gating. Concrete current-year work broadens tested concerns without replacing historical agency.

**Reception / limit:** Extended abstract, preprints, simulations and qualitative study have different strength; no general reliable autonomy claim follows. [EAA-S037; EAA-S038; EAA-S039; EAA-S047; EAA-S048]

## EVOLVED_AUTONOMOUS_AGENTS_GENEALOGY

The nodes above identify dated problems and contributions. The following edges distinguish documented influence, extension, criticism, imports, hybridisation, convergence and analogy. A citation establishes at least acquaintance only when present; similarity alone is not promoted to derivation. Direct influence claims below are limited to explicit discussions in the cited work. No edge supplies statistical independence.

**EAA-GE001 — EAA-G01 → EAA-G14, `DOCUMENTED_IMPORT`.** Bounded-optimal decision procedures address resource-limited rationality in a computational setting. **Limit:** This is a conceptual import, not proof that every mechanism in the later work derives solely from Simon. [EAA-S014]

**EAA-GE002 — EAA-G02 → EAA-G04, `CRITICISM_AND_RESPONSE`.** Brooks explicitly criticises central symbolic representation and functional decomposition as a prerequisite for creature-level intelligence. **Limit:** The criticism does not refute every planner or every need for representation. [EAA-S005]

**EAA-GE003 — EAA-G04 → EAA-G15, `HYBRIDISATION`.** The hybrid architecture explicitly discusses reactive robot approaches alongside planning and sequencing. **Limit:** Combination adds interface and timing obligations; not a universal replacement. [EAA-S046]

**EAA-GE004 — EAA-G05 → EAA-G15, `DOCUMENTED_INFLUENCE`.** The 3T author account uses reactive action sequencing associated with Firby’s work. **Limit:** Source-level operational connection, not identity of the whole architectures. [EAA-S046]

**EAA-GE005 — EAA-G06 → EAA-G08, `DOCUMENTED_INFLUENCE`.** BDI authors explicitly connect their beliefs/desires/intentions framework to practical reasoning. **Limit:** Philosophical inspiration, formal semantics and executable approximation remain different evidence. [EAA-S008; EAA-S009]

**EAA-GE006 — EAA-G07 → EAA-G08, `CRITICISM_AND_RESPONSE`.** Rao–Georgeff explicitly contrast primitive intention with reductions using other attitudes. **Limit:** A rival formalisation, not an established refinement proof or universally stronger account. [EAA-S008]

**EAA-GE007 — EAA-G06 → EAA-G09, `DOMAIN_TRANSLATION`.** Commitment/resource questions are investigated in a situated-agent simulation. **Limit:** No equivalence proof between practical-reasoning philosophy and the simulated interpreter. [EAA-S015]

**EAA-GE008 — EAA-G08 → EAA-G09, `SHARED_ANCESTRY`.** Both address PRS/BDI-style commitment and runtime intention management. **Limit:** Dates and mechanisms do not warrant treating the 1995 article as the cause of a 1991 experiment. [EAA-S009; EAA-S015]

**EAA-GE009 — EAA-G02 → EAA-G17, `DOMAIN_TRANSLATION`.** Weld explicitly applies planning-based control to executable software tools and information access. **Limit:** Software action contracts and observability differ from physical robotics. [EAA-S045]

**EAA-GE010 — EAA-G11 → EAA-G13, `DOCUMENTED_INFLUENCE`.** The foundational survey explicitly treats agent-oriented programming within its language map. **Limit:** Survey inclusion establishes documented reception, not independent validation. [EAA-S001]

**EAA-GE011 — EAA-G13 → EAA-G16, `EXPLICIT_EXTENSION`.** The later taxonomy examines existing definitions while proposing a persistent situated boundary. **Limit:** It does not erase the non-equivalent motivation-based framework. [EAA-S002]

**EAA-GE012 — EAA-G12 → EAA-G18, `CRITICISM_AND_RESPONSE`.** User-autonomy analysis critically examines assistant behaviour and explanatory/control claims. **Limit:** Normative critique is not a controlled rejection of every learning interface. [EAA-S043]

**EAA-GE013 — EAA-G03 → EAA-G20, `CONVERGENT_DEVELOPMENT`.** Automation readiness criticism and agent interaction/execution concerns converge on the practical cost of human intervention. **Limit:** No direct influence claim is inferred merely from overlapping concerns. [EAA-S019; EAA-S022; EAA-S023]

**EAA-GE014 — EAA-G12 → EAA-G20, `SHARED_ANCESTRY`.** Learning interfaces and mixed initiative both develop computer assistance with user control. **Limit:** Specific derivation requires more than similar terminology; this edge makes only the shared HCI/AI problem claim. [EAA-S019; EAA-S044]

**EAA-GE015 — EAA-G19 → EAA-G21, `DOCUMENTED_IMPORT`.** Electric Elves lessons explicitly discuss replacing inadequate state assumptions with a partial-observation treatment. **Limit:** Richer POMDP reasoning costs more and does not fix every sensor or privacy problem. [EAA-S021]

**EAA-GE016 — EAA-G20 → EAA-G21, `CONVERGENT_DEVELOPMENT`.** Mixed initiative and adjustable autonomy both make action/consultation trade-offs explicit. **Limit:** The edge does not assert their mathematical models or exact historical derivation are identical. [EAA-S019; EAA-S020]

**EAA-GE017 — EAA-G08 → EAA-G22, `EXPLICIT_EXTENSION`.** Concurrent-goal and maintenance-goal work extends operational reasoning about goals and plan structures. **Limit:** Achievement-goal interference results cannot be silently extended to every maintenance setting. [EAA-S054; EAA-S051]

**EAA-GE018 — EAA-G11 → EAA-G23, `EXPLICIT_EXTENSION`.** The communication-semantics paper explicitly situates its AgentSpeak interpreter in agent-oriented languages. **Limit:** Its direct AgentSpeak/PRS ancestry is documented; not every detail is inherited from AGENT0. [EAA-S028]

**EAA-GE019 — EAA-G10 → EAA-G24, `EXPLICIT_EXTENSION`.** Safe interruptibility modifies or characterises specific reinforcement-learning updates. **Limit:** A learning theorem, not a full physical interruption protocol. [EAA-S024]

**EAA-GE020 — EAA-G10 → EAA-G24, `SHARED_ANCESTRY`.** Learning and self-modification share sequential-decision concerns but distinguish ordinary updates from policy self-change. **Limit:** Ordinary Q-learning is not automatically self-modification under the later paper’s definition. [EAA-S027; EAA-S053]

**EAA-GE021 — EAA-G03 → EAA-G24, `ONLY_ANALOGOUS`.** Human intervention appears in both automation criticism and safe-interruptibility mathematics. **Limit:** Similar concern does not identify the same mechanism or prove that one solves the other. [EAA-S023; EAA-S024]

**EAA-GE022 — EAA-G24 → EAA-G27, `EXPLICIT_EXTENSION`.** The partially observable off-switch game explicitly extends the earlier fully observable interaction analysis. **Limit:** It narrows universal deference inferences without logically refuting results under their original assumptions. [EAA-S041]

**EAA-GE023 — EAA-G19 → EAA-G25, `CONVERGENT_DEVELOPMENT`.** Language-conditioned agents also act on observations and uncertain action affordances. **Limit:** No generic claim that ReAct or SayCan implements a POMDP solver or inherits its guarantees. [EAA-S012; EAA-S030; EAA-S049]

**EAA-GE024 — EAA-G17 → EAA-G25, `SHARED_ANCESTRY`.** Planning software tools and modern language tool users share the broader AI agent/environment problem. **Limit:** A direct source-to-source influence is not asserted without documentary support. [EAA-S045; EAA-S030]

**EAA-GE025 — EAA-G25 → EAA-G26, `CRITICISM_AND_RESPONSE`.** Cost-aware re-evaluation and fixed baselines challenge broad performance claims about agentic and reflective architectures. **Limit:** Selected models/benchmarks do not prove fixed workflows dominate every domain. [EAA-S031; EAA-S035; EAA-S036]

**EAA-GE026 — EAA-G23 → EAA-G26, `ONLY_ANALOGOUS`.** Sender provenance/acceptance and tool-text trust boundaries both distinguish information from adoption. **Limit:** Formal message annotations are not a demonstrated defence against LLM prompt injection. [EAA-S028; EAA-S034]

**EAA-GE027 — EAA-G18 → EAA-G28, `CONVERGENT_DEVELOPMENT`.** Current usability findings revisit meaningful control, mental models and actual user costs. **Limit:** The current empirical study does not by itself establish direct intellectual influence or population rates. [EAA-S043; EAA-S047]

**EAA-GE028 — EAA-G24 → EAA-G28, `CONVERGENT_DEVELOPMENT`.** Current safety learning and action gating pursue constrained action with different mechanisms. **Limit:** Do not union their guarantees: demonstration learning, runtime checks and interruption theorems use incompatible assumptions. [EAA-S024; EAA-S038; EAA-S042; EAA-S039]

**EAA-GE029 — EAA-G25 → EAA-G28, `DOMAIN_TRANSLATION`.** The recent physical-agent preprint explicitly places language-generated plans behind executable robot-skill interfaces. **Limit:** The main comparison is simulation, with selected separate hardware demonstrations and no independent replication. [EAA-S039]

**EAA-GE030 — EAA-G06 → EAA-G25, `UNRESOLVED_RELATIONSHIP`.** Both practical intention and reflective memory can affect later decisions. **Limit:** No source-established equivalence or direct ancestry between adopted intentions and verbal reflective memory is claimed. [EAA-S006; EAA-S031]

## EVOLVED_AUTONOMOUS_AGENTS_SCOPE_AND_CARICATURES

The study covers single-agent situated action and its integral interaction boundaries. Full collective strategic organisation and the complete agent-oriented development lifecycle remain adjacent. A person-like interface is not a consciousness test; a planning program is not necessarily its executor; autonomy can concern different powers under different definitions. A reactive policy can be a complete adequate architecture, and a richer planner can be necessary under different observations and goals.

The principal caricatures are monocultural: all agents are symbolic planners; all genuine agents must be human-like; all modern tool-using models implement BDI; every reflection improves performance; more independence is always better; every human override is effective; a model-level proof means the world satisfies its assumptions. The corresponding counter-caricatures are also rejected: symbolic planning never considered execution; no task needs representation; every fixed workflow is necessarily superior; formal evidence is worthless after an implementation failure. The operative selection conditions, not allegiance to a label, govern retention.

## EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER

**Population:** 70. **Examined:** 70. **Unexamined:** 0. **Affirmative but conditional:** 59. **Contested:** one (EAA-042). **Unresolved:** one (EAA-062). **Other non-retained/superseded/duplicate:** nine. The complete records contain every common field and all ten domain-profile fields in [the property ledger](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json). This table is the full denominator, not a top-properties selection.

| Primary disposition | Count |
|---|---:|
| `STRONGLY_RETAINED` | 13 |
| `RETAINED_IN_EVOLVED_FORM` | 25 |
| `CONTEXT_DEPENDENT` | 17 |
| `ASSUMPTION_SENSITIVE` | 4 |
| `USEFUL_BUT_EASILY_GAMED` | 0 |
| `USEFUL_BUT_EASILY_BUREAUCRATISED` | 0 |
| `DOMAIN_SPECIFIC` | 0 |
| `SUPERSEDED_BY_STRONGER_FORM` | 1 |
| `DUPLICATE_CANDIDATE` | 1 |
| `CEREMONY_NOT_GENERAL_PROPERTY` | 1 |
| `NO_GENERAL_PROPERTY` | 2 |
| `REJECTED_OR_DISFAVOURED` | 4 |
| `CONTESTED` | 1 |
| `UNRESOLVED` | 1 |

| ID / complete JSON details | Candidate | Disposition |
|---|---|---|
| [EAA-001](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Explicit agent–environment boundary | `STRONGLY_RETAINED` |
| [EAA-002](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Task-relative autonomy dimensions | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-003](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Computational grounding of mental-state vocabulary | `STRONGLY_RETAINED` |
| [EAA-004](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Capability is not delegated permission | `STRONGLY_RETAINED` |
| [EAA-005](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Observation, stored belief and world state remain distinct | `STRONGLY_RETAINED` |
| [EAA-006](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Decision-relevant freshness and change detection | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-007](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Adequate uncertainty representation rather than a complete world model | `ASSUMPTION_SENSITIVE` |
| [EAA-008](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Actionable information gathering | `CONTEXT_DEPENDENT` |
| [EAA-009](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Abstention, waiting or safe non-action | `CONTEXT_DEPENDENT` |
| [EAA-010](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Usable goal and success semantics | `STRONGLY_RETAINED` |
| [EAA-011](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Achievement and maintenance commitments are not interchangeable | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-012](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Concurrent-goal interference protection | `CONTEXT_DEPENDENT` |
| [EAA-013](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Conditional intention commitment | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-014](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Economical reconsideration scheduling | `CONTEXT_DEPENDENT` |
| [EAA-015](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Retirement of obsolete, unreachable or exhausted goals | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-016](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Direct reactive control as a legitimate architecture branch | `CONTEXT_DEPENDENT` |
| [EAA-017](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Model-based deliberation when anticipation earns its cost | `CONTEXT_DEPENDENT` |
| [EAA-018](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Executable BDI and plan-library interpretation | `CONTEXT_DEPENDENT` |
| [EAA-019](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Hybrid arbitration and interface coherence | `CONTEXT_DEPENDENT` |
| [EAA-020](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Smallest adequate architecture and credible simpler baseline | `STRONGLY_RETAINED` |
| [EAA-021](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Ground actions in executable capabilities and affordances | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-022](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Recheck material action conditions at dispatch | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-023](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Distinguish issuance, acknowledgement and established effect | `STRONGLY_RETAINED` |
| [EAA-024](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Bounded contingency handling and plan repair | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-025](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Irreversibility and retry/compensation boundary | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-026](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Explicit time and resource envelope | `STRONGLY_RETAINED` |
| [EAA-027](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Anytime response or adequate deadline fallback | `CONTEXT_DEPENDENT` |
| [EAA-028](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Metareasoning and value of computation | `CONTEXT_DEPENDENT` |
| [EAA-029](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Separate learning from execution-state updates | `STRONGLY_RETAINED` |
| [EAA-030](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Evidence-grounded persistent experience | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-031](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Selective retrieval, forgetting and memory retirement | `CONTEXT_DEPENDENT` |
| [EAA-032](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Adaptation with continuity checks | `CONTEXT_DEPENDENT` |
| [EAA-033](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Protected exploration and constraint-aware learning | `ASSUMPTION_SENSITIVE` |
| [EAA-034](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Intended objective is not the measured proxy | `STRONGLY_RETAINED` |
| [EAA-035](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Transfer and distribution-change evaluation | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-036](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Communication receipt, acceptance and action are separate | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-037](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Cost-aware clarification and mixed initiative | `CONTEXT_DEPENDENT` |
| [EAA-038](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Conditional transfer of control | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-039](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Human readiness and safe handback conditions | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-040](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Operational revocation and interruption | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-041](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Learning-theoretic safe interruptibility | `ASSUMPTION_SENSITIVE` |
| [EAA-042](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Objective uncertainty as a conditional route to deference | `CONTESTED` |
| [EAA-043](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | User autonomy, privacy and affected-party accountability | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-044](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Action-faithful explanation and calibrated reliance | `CONTEXT_DEPENDENT` |
| [EAA-045](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Adequate independent outcome and policy oracle | `STRONGLY_RETAINED` |
| [EAA-046](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Repeated trials, versions and reproducible conditions | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-047](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Resource-controlled comparison with credible baselines | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-048](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Whole-task cost and burden accounting | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-049](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Protected tests and deliberate failure exposure | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-050](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Monitor material assurance assumptions at runtime | `CONTEXT_DEPENDENT` |
| [EAA-051](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Bound formal claims to model and implementation obligations | `STRONGLY_RETAINED` |
| [EAA-052](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Untrusted observations do not confer instruction authority | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-053](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Language-model reasoning–action feedback | `CONTEXT_DEPENDENT` |
| [EAA-054](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | External-feedback-anchored reflection | `CONTEXT_DEPENDENT` |
| [EAA-055](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Re-evaluate consequential model and tool version changes | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-056](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Human-likeness as a general competence or consciousness proxy | `NO_GENERAL_PROPERTY` |
| [EAA-057](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Maximum autonomy and persistence are always preferable | `REJECTED_OR_DISFAVOURED` |
| [EAA-058](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | A complete central world model is universally necessary | `REJECTED_OR_DISFAVOURED` |
| [EAA-059](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Representation-free reaction is universally sufficient | `REJECTED_OR_DISFAVOURED` |
| [EAA-060](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Proxy maximisation is sufficient objective fulfilment | `REJECTED_OR_DISFAVOURED` |
| [EAA-061](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Mandatory continuous reflection | `SUPERSEDED_BY_STRONGER_FORM` |
| [EAA-062](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | General assurance for open-ended self-revision | `UNRESOLVED` |
| [EAA-063](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Belief/intention prompts without operational semantics | `CEREMONY_NOT_GENERAL_PROPERTY` |
| [EAA-064](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Leaderboard success as deployment guarantee | `NO_GENERAL_PROPERTY` |
| [EAA-065](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Verify completion before claiming completion | `DUPLICATE_CANDIDATE` |
| [EAA-066](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Software–physical translation needs new obligations | `STRONGLY_RETAINED` |
| [EAA-067](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Coherent action basis across asynchronous state, goal and authority changes | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-068](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Failure-attributed revision rather than undirected self-change | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-069](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Goal- and scope-preserving plan repair | `RETAINED_IN_EVOLVED_FORM` |
| [EAA-070](EVOLVED_AUTONOMOUS_AGENTS_PROPERTY_LEDGER.json) | Predecessor-criterion evaluation of self-modification | `ASSUMPTION_SENSITIVE` |

A `STRONGLY_RETAINED` judgement means a robust task-relative engineering criterion survived the examined criticisms; it does not mean universal measured benefit or a duty to create a separate control. `ASSUMPTION_SENSITIVE` preserves a mechanism whose formal/model conditions are particularly load-bearing. `CONTESTED` keeps incompatible supported conclusions under changed assumptions. `UNRESOLVED` is examined uncertainty, not unfinished searching. `DUPLICATE_CANDIDATE` preserves the discovery without adding a second operative mechanism. No empty disposition category is filled artificially.

## EVOLVED_AUTONOMOUS_AGENTS_DOMAIN_MODELS

These models develop the domain profile rather than using “context dependent” as a substitute for explanation. The same ten questions recur at different levels because a goal, an observation, a capability, a permission and an evaluation are coupled but non-equivalent. Property records specialise these models with their own mechanism, consumer, evidence, assumptions and cost.

### AAG1 — Agency definitions and dimensions of autonomy

The unit is an entity situated relative to a declared environment, not a persona. Wooldridge–Jennings’s weak notion includes autonomy, reactivity, proactivity and social ability; Franklin–Graesser foreground sustained sensing and acting in an environment; Luck–d’Inverno distinguish goal-ascribed agents from motivated autonomous agents. These overlap but are not equivalent tests. The synthesis uses a task-relative description of action choice, goal adoption/change, resource control, temporal persistence, learning and human intervention. The expanded vector is analytical, not an ALFUS quotation. Agency, intelligence, autonomy, consciousness and moral responsibility remain distinct predicates. [EAA-S001; EAA-S002; EAA-S003; EAA-S010; EAA-S017; EAA-S043; EAA-S050]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Use the declared operational definition and specify the dimension of autonomy actually exercised; no inference from human likeness.

**ENVIRONMENT_AND_OBSERVABILITY:** Declare the agent/environment boundary, including which external actors or actuators are outside direct control.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Separate externally assigned goals from internally generated motivation; neither implies unlimited goal-rewriting authority.

**ARCHITECTURE_AND_ACTION_SELECTION:** Architecture is evidence about implementation, not determined by the word agent; an ordinary controller may meet a minimal definition.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** A stored belief is an attributed or implemented state, not automatically truth; a mental-state label requires a behavioural consumer.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Having an action interface does not establish authorisation or successful external effect.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Persistence and independence are bounded by the task, resources and response requirements; no universal autonomy ranking is adopted.

**LEARNING_OR_REVISION_BOUNDARY:** Learning and self-modification are separate dimensions and are not necessary for every agent definition.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Social ability is required by some definitions but does not mean every task needs negotiation; user autonomy remains distinct.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Evaluate the demonstrated action capability under the chosen definition; believability, autonomy and task reliability are different targets.


### AAG2 — Environment, perception and state estimation

Write world state as x_t, observation as o_t drawn through an observation process, and the agent estimate as b_t or a smaller sufficient history summary. A belief update b_{t+1}=U(b_t,a_t,o_{t+1}) is an internal transition, not proof that the world changed as predicted. In a correctly specified POMDP, the belief is a sufficient statistic for decision-making; the correctness of transition and observation models is a separate obligation. Time, source and ambiguity are needed only where they alter decisions. Queries, questions and waiting are actions with costs, not an obligatory phase before real action. [EAA-S005; EAA-S012; EAA-S014; EAA-S019; EAA-S021; EAA-S022; EAA-S028; EAA-S039]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Autonomy here concerns selecting observations and actions under limited environmental knowledge, not omniscience.

**ENVIRONMENT_AND_OBSERVABILITY:** Distinguish latent world state, sensor/tool observations and a task-relevant state estimate; account for partial observability and delay.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** The goal determines which uncertainty matters: information is useful only if it can change a relevant decision or its confidence boundary.

**ARCHITECTURE_AND_ACTION_SELECTION:** A reactive policy, stateful controller or belief-space planner is selected according to perceptual aliasing and horizon.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Preserve the source, interpretation and validity of consequential observations; normalised probability is not world correspondence.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Recheck conditions that can change before action, and distinguish a success-looking return from observed effects.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Fresh sensing, active inquiry and belief maintenance consume the same finite action window as planning.

**LEARNING_OR_REVISION_BOUNDARY:** A belief-state update is not necessarily learning; learning the observation/transition model introduces additional validation obligations.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Human reports and tool returns are observations with distinct trust and authority roles; assistance can be an information action.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Test stale, ambiguous, missing and misleading observations; simulation models and assumed sensor properties limit transfer.


### AAG3 — Goals, intentions and commitments

Distinguish a goal condition G from a plan recipe and from an adopted intention I to pursue it. Commitment filters later deliberation and coordinates action; it is not merely another current preference. Persistent-goal accounts terminate on recognised achievement, impossibility or loss of relevance, with conflict qualifications. BDI accounts instead treat intention as a primitive in a different formal framework. Neither logical model is identical to its finite interpreter. Maintenance requires continued satisfaction or restoration within a declared horizon, not dropping the obligation once a predicate becomes true. Concurrent goals need conflict discrimination when their conditions, effects or resource demands interfere. [EAA-S006; EAA-S008; EAA-S009; EAA-S015; EAA-S020; EAA-S025; EAA-S033; EAA-S051; EAA-S052; EAA-S054]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Autonomy concerns selecting or pursuing goals within a declared source of task authority; internal motivation and externally delegated objectives are not equivalent.

**ENVIRONMENT_AND_OBSERVABILITY:** Feasibility and progress depend on a fallible world estimate and can change during a commitment.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Separate achievement, maintenance, preferences, goals, intentions and plan recipes; define retention and termination conditions.

**ARCHITECTURE_AND_ACTION_SELECTION:** Use intention filtering, goal conflict checks or simpler scheduling only where persistent or concurrent goals need them.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** A belief that a goal is impossible is fallible; one failed plan does not establish global impossibility.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Execution must establish relevant progress/effects and preserve protected conditions of other active goals.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Reconsideration has opportunity cost; persistence and responsiveness are selected using change, deadline and deliberation burden.

**LEARNING_OR_REVISION_BOUNDARY:** Updating an intention is not authority to alter the externally given objective or redefine success.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Clarify changed task meaning and report abandonment/non-fulfilment to the legitimate consumer where consequential.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Use cases of obsolete goals, impossible plans, maintenance recovery and cross-goal interference; simulated model-sensitive results bound generality.


### AAG4 — Reactive, deliberative and hybrid architectures

Architecture is a conditional selection, not a ladder. A direct policy can be complete for a sufficiently observable local task. A deliberative planner earns its cost when look-ahead or non-local dependencies matter. A BDI interpreter uses context-sensitive plan libraries and commitment rules for structured recurrent tasks. A hybrid can connect slower planning, discrete sequencing and continuous skills, but must reconcile priorities, state and timing. The 3T paper explicitly permits reduced configurations and does not establish hard real-time execution merely by requesting skill frequencies. Modern fixed software workflows are another credible baseline, not proof that all open-ended agency is unnecessary. [EAA-S004; EAA-S005; EAA-S009; EAA-S011; EAA-S012; EAA-S014; EAA-S016; EAA-S022; EAA-S028; EAA-S035; EAA-S036; EAA-S045; EAA-S046]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Autonomy denotes the actual action-selection freedom afforded by the selected architecture, not its number of modules.

**ENVIRONMENT_AND_OBSERVABILITY:** Reactive choices require sufficiently discriminating current cues; deliberative and hybrid choices require adequate additional state assumptions.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Planning, BDI intention filtering and behaviour arbitration support different goal horizons and commitment structures.

**ARCHITECTURE_AND_ACTION_SELECTION:** Select reactive, deliberative, BDI or hybrid branches by demonstrated task need and compare cheaper adequate alternatives.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Multiple layers must not silently maintain incompatible copies of the same relevant state or plan status.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Capabilities, preconditions and execution effects must remain grounded across planner, sequencer and actuator interfaces.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Deliberation, coordination and skill scheduling must fit the task window; requested frequency is not a timing proof.

**LEARNING_OR_REVISION_BOUNDARY:** Learning is optional; adding a learned component changes the assumptions at its interface rather than automatically enriching the whole architecture.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Override, handback and authority changes must have real operational effects across active layers.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Use task-relevant simpler baselines, concurrency tests and interface failures; author robot demonstrations do not establish universal hybrid superiority.


### AAG5 — Action execution, monitoring and plan repair

An action has a proposed identity and parameters, applicable conditions, execution semantics and an intended effect. The transitions proposed → authorised/applicable → issued → acknowledged → effect established are distinct evidence states, not a mandatory serial software pipeline: trusted atomic contracts can collapse some, asynchronous effects can delay others, and a stop or goal change can interrupt them. Missing acknowledgement may mean either no effect or an unobserved effect; blind retry can therefore duplicate harm. Repair changes means only within the authorised task. If a new destination or goal is needed, that is a separate task decision. Coherence across state, goal and authority is a composition-induced obligation, not a copied named architecture. [EAA-S006; EAA-S011; EAA-S016; EAA-S019; EAA-S022; EAA-S025; EAA-S031; EAA-S032; EAA-S033; EAA-S039; EAA-S042; EAA-S043; EAA-S044; EAA-S045; EAA-S049]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Action autonomy is limited by executable capabilities and delegated scope; selecting a command is not establishing its consequence.

**ENVIRONMENT_AND_OBSERVABILITY:** Effects may be asynchronous, partial, irreversible or observed through fallible tools and sensors.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Keep goal identity and protected constraints stable across repair unless a legitimate task-change decision revises them.

**ARCHITECTURE_AND_ACTION_SELECTION:** Use fixed actions, library alternatives or planning as appropriate; failure feedback can return to any relevant decision point.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Track current-enough state and unresolved outcomes without treating missing evidence as proof of either success or non-execution.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Ground capability identity, check material conditions and establish effects by adequate contracts or observations.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Retries, repair, waiting and observation share the remaining task budget; use progress-sensitive termination.

**LEARNING_OR_REVISION_BOUNDARY:** Execution repair is distinct from changing a learned policy, goal or evaluation criterion; persistent changes require their own evidence.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Report material failure or unresolved effects; seek permission for genuine task changes and provide feasible handback.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Test acknowledged-but-failed actions, lost acknowledgements, stale checks and target-changing repairs; resettable simulators understate irreversible consequences.


### AAG6 — Bounded rationality and metareasoning

The relevant comparison is between feasible complete decision procedures on a specified machine and environment, not unbounded ideal rationality. A schematic metalevel decision compares expected improvement in task value with computation, delay, sensing and coordination costs; this is an analytical summary, not a universally computable formula. An anytime method is useful only if its intermediate answer is usable and computation can actually be interrupted. A fixed direct policy or simple stopping rule can dominate a metareasoner whose estimation overhead outweighs its value. Costs and quality should remain separately inspectable even where a local decision uses a scalar trade-off. [EAA-S006; EAA-S013; EAA-S014; EAA-S015; EAA-S019; EAA-S035; EAA-S046]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Autonomy is exercised under a resource envelope rather than unlimited deliberative freedom.

**ENVIRONMENT_AND_OBSERVABILITY:** The environment may change while computation runs, making a better model of the past less useful for current action.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** The task defines deadlines, protected conditions and acceptable response quality; computation is instrumental to those goals.

**ARCHITECTURE_AND_ACTION_SELECTION:** Choose act, think, observe, ask or stop using an adequate metalevel rule; exact optimisation is optional.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Long reasoning can stale its own state assumptions; cached results require relevant validity conditions.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** A timely action or safe fallback must actually be executable, not merely returned as text after the deadline.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Account for reasoning, tools, retries, energy and attention; bounded optimality is machine/environment relative.

**LEARNING_OR_REVISION_BOUNDARY:** Learning a computation policy is an additional adaptation problem; it does not remove the budget or validation duties.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Consultation consumes another actor’s time and may fail to receive a reply; attention is not free computation.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Measure quality/cost trade-offs with matched resources and real decision deadlines; simulated bounded-optimal results are not timing certification.


### AAG7 — Learning, adaptation and persistent state

Execution state, stored experience, model parameters, policies, skills and revision criteria are distinct objects. Memory can change future behaviour without weight updates; changing weights need not improve the intended task. Useful experience requires provenance and evaluation, and retention has both relevance and privacy costs. Continual learning exposes stability/plasticity trade-offs rather than eliminating them. Safe exploration must protect people before convergence, not only produce eventual good reward. Self-modification theory provides a narrow predecessor-utility result under strong anticipation and optimality assumptions; it can preserve a wrong objective and does not settle open-ended safe self-revision or corrigibility. [EAA-S024; EAA-S025; EAA-S026; EAA-S027; EAA-S028; EAA-S031; EAA-S033; EAA-S035; EAA-S038; EAA-S041; EAA-S043; EAA-S044; EAA-S050; EAA-S053]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Learning autonomy concerns which persistent representations or policies may change; it does not imply authority to change every goal or constraint.

**ENVIRONMENT_AND_OBSERVABILITY:** Training and deployment conditions can differ, including in the relation between observations, rewards and intended goals.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Separate intended objective from measured reward; preserving a predecessor utility is only desirable if that criterion remains justified.

**ARCHITECTURE_AND_ACTION_SELECTION:** Learning can modify a policy/model/memory or select skills within a fixed executor; explicit self-modification is a distinct formal case.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Store consequential experience with its source, interpretation and correction status; retrieve relevance is not evidence of truth.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Exploration and revised actions still require legitimate capability, conditions and outcome evidence.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Training, retrieval, review and repeated trials incur budgets; bounded storage or fixed behaviour may be preferable.

**LEARNING_OR_REVISION_BOUNDARY:** Define the change surface, evaluation criterion and continuity constraints; successor self-certification is not assumed valid.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Human correction is informative but fallible; persistent memory also raises privacy and consent questions.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Test retained competence, objective/proxy divergence, distribution shift and oracle failure; convergence assumptions and simulation limits remain explicit.


### AAG8 — Communication, assistance and delegated autonomy

A delegation relates a principal, a task, permitted means and a recipient; it is not inferred from capability alone. Communication can inform, request or negotiate, but sending, receiving, accepting and acting are different events. Transfer of control must include the possibility of non-response, and a nominal human override may fail through lost skill, absent context or insufficient time. Operational interruption differs from a learning theorem about incentives under interruption. Objective uncertainty may promote deference in one game and fail to do so under different private-information assumptions. Human autonomy, privacy and third-party effects remain constraints that cannot be reduced to the agent’s internal task score. [EAA-S019; EAA-S020; EAA-S021; EAA-S022; EAA-S023; EAA-S024; EAA-S028; EAA-S037; EAA-S040; EAA-S041; EAA-S043; EAA-S044; EAA-S047]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Action choice, authority and user autonomy are distinct; increased agent independence may reduce the human’s meaningful control.

**ENVIRONMENT_AND_OBSERVABILITY:** The environment includes other actors with uncertain availability, knowledge and responsiveness; silence is not acceptance.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Task meaning and scope can be negotiated, but the agent cannot unilaterally legitimise new objectives or means.

**ARCHITECTURE_AND_ACTION_SELECTION:** Select initiative, advice, clarification, handoff or direct action based on consequence, uncertainty, competence and response time.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Messages need source and acceptance semantics; the recipient’s belief or commitment is not established by the sender’s assertion.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Authorisation must reach the executor; revocation and handback must account for in-flight and irreversible actions.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Human response, interruption and recovery take time; attention and coordination are resources.

**LEARNING_OR_REVISION_BOUNDARY:** Learning incentives under interruption, persistent memory and user correction have separate validation and authority boundaries.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Identify sender, recipient, consumer and non-response path; provide the task-relevant state needed for actual takeover.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Use adverse non-response cases, usability evidence and game assumptions; normative principles and formal deference models are not universal field guarantees.


### AAG9 — Assurance, evaluation and adverse consequences

Evaluation has at least four distinguishable targets: task-instance effects, policy/constraint compliance, repeated-trial dependability and transfer to a target setting. A correct answer can occur without action; a terminal database state can match while a required confirmation never occurred. A theorem is conditional on a model, an implementation relation and environmental assumptions. An observed failure outside those assumptions is not a logical refutation, but it can invalidate a deployment claim. Repetition, reset conditions, shared datasets and hidden human support determine what statistical or comparative claims are warranted. A 50% task horizon measured on human expert task time is not autonomous uptime. [EAA-S009; EAA-S012; EAA-S022; EAA-S024; EAA-S027; EAA-S031; EAA-S032; EAA-S033; EAA-S034; EAA-S035; EAA-S036; EAA-S038; EAA-S039; EAA-S042; EAA-S048; EAA-S053]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** Evaluate actual autonomy and action within the declared task, not marketing labels or a single impressive output.

**ENVIRONMENT_AND_OBSERVABILITY:** Record resets, simulations, sensors, tool conditions and external participants; environment design can simplify the challenge.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Success measures must cover the intended outcome and protected means; proxy scores cannot silently redefine the task.

**ARCHITECTURE_AND_ACTION_SELECTION:** Compare architectures against credible cheaper alternatives under meaningful resource and information conditions.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Evaluator judgements, logs and learned self-tests are fallible evidence; keep provenance and conflicting outcomes.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Distinguish issued actions, observed effects and policy-conformant trajectories; inspect oracle omissions.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Account for all material attempts, inference/tool costs, human intervention and task deadlines.

**LEARNING_OR_REVISION_BOUNDARY:** Persistent changes and model/tool versions can invalidate prior evaluation; strong formal assumptions remain bounded.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Disclose user simulation, human assistance and affected-party costs; protected tests must not externalise harm.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Separate theory, comparison, field experience, replication and transfer; report units, uncertainty, dependencies and unmeasured limits.


### AAG10 — Contemporary language-model agents as a translation

ReAct interleaves generated reasoning/action with observations; Reflexion uses evaluator feedback and text memory without weight updates; SayCan combines language relevance with learned skill affordances. These mechanisms have genuine intersections with earlier planning, memory and perception/action research but do not by themselves implement formal BDI. Tool text creates an instruction-integrity problem: data can try to impersonate authority. Current studies include controlled benchmarks, qualitative user studies, conceptual shared-autonomy work, simulator safety learning and a recent physical-agent preprint; their evidence roles and versions are kept separate. None replaces the pre-LLM genealogy or establishes universal ongoing autonomy. [EAA-S010; EAA-S014; EAA-S022; EAA-S025; EAA-S030; EAA-S031; EAA-S032; EAA-S033; EAA-S034; EAA-S035; EAA-S036; EAA-S037; EAA-S038; EAA-S039; EAA-S042; EAA-S045; EAA-S047; EAA-S048; EAA-S049; EAA-S050]

**AGENCY_DEFINITION_AND_AUTONOMY_DIMENSION:** The label LLM agent does not settle situatedness, persistence, delegated freedom or the definition of autonomy being claimed.

**ENVIRONMENT_AND_OBSERVABILITY:** Tools and retrieved text are fallible and potentially adversarial observations; software and physical environments have different actuation constraints.

**GOAL_INTENTION_AND_COMMITMENT_SEMANTICS:** Natural-language requests need workable success and scope semantics; a prompt mentioning intentions does not create formal commitment.

**ARCHITECTURE_AND_ACTION_SELECTION:** Reason–act loops, fixed workflows, reflection and skill grounding are alternatives or conditional combinations, not compulsory modules.

**STATE_BELIEF_OR_MEMORY_VALIDITY:** Text memories, retrieval and self-generated lessons need validity and provenance; fluent reasoning is not an observation.

**ACTION_PRECONDITIONS_AND_EFFECT_VERIFICATION:** Generated actions must map to actual tools/skills, retain the requested task and establish real effects.

**TIME_RESOURCE_AND_DELIBERATION_LIMIT:** Tokens, retries, tool latency and human support belong in evaluation; reflection can lose the action window.

**LEARNING_OR_REVISION_BOUNDARY:** Prompt/model/tool changes can alter behaviour without visible application changes; broad self-revision assurance is not established.

**COMMUNICATION_DELEGATION_AND_HUMAN_HANDOFF:** Helpful initiative remains delegated; untrusted content cannot legitimise new authority, and human handoff needs actual readiness.

**EVALUATION_ORACLE_AND_TRANSFER_LIMIT:** Distinguish benchmark task success, reliability, believability and deployment transfer; 2026 abstracts/preprints are not automatically replicated findings.


## EVOLVED_AUTONOMOUS_AGENTS_CEREMONY_STRIPPING_LEDGER

Stripping ceremony means preserving a needed function with its cheapest adequate realisation, not deleting all documentation, meetings or formal models. A useful artefact can carry evidence or enable coordination. Its presence alone does not establish the protected property. The complete machine-readable ledger has one record for every candidate; the entries below expose the functional alternatives for all 59 affirmative candidates. Negative, duplicate and unresolved records retain their omission rationale in the property ledger and later sections.

Retirement refers to a dedicated implementation whose trigger, consumer or distinct contribution has disappeared. It does not erase historical evidence, legitimate constraints or unresolved external effects.

### EAA-CE001 / EAA-001

**Original form or artefact:** Competing weak/strong, situated-persistent and motivation-based definitions, not one necessary-and-sufficient academic consensus.

**Protected failure / consumer:** Calling any automated output agency conceals whether there is an environment, an objective and any effective action. Consumer: Architect, evaluator and person interpreting capability claims.

**Prerequisite and fuller-form trigger:** An identifiable task and observation/action interface; no requirement for a human-like self-model. Comparing systems, assigning responsibility or claiming autonomous capability.

**Minimal alternative:** For a pure function, describe input/output computation without forcing an agent label. A simple controller may satisfy a minimal situated definition.

**Cost of the fuller control:** Modelling effort and risk of freezing an arbitrary boundary. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Calling any automated output agency conceals whether there is an environment, an objective and any effective action. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: For a pure function, describe input/output computation without forcing an agent label. A simple controller may satisfy a minimal situated definition.

### EAA-CE002 / EAA-002

**Original form or artefact:** Contextual descriptions of agent autonomy, with ALFUS organising mission/environment/human-independence terminology.

**Protected failure / consumer:** A single autonomy score conflates action selection, goal choice, persistence, adaptation and freedom from direct intervention. Consumer: Delegator and capability evaluator.

**Prerequisite and fuller-form trigger:** Explicit task context and independently described capability and authorisation. Comparing or delegating different degrees of autonomy.

**Minimal alternative:** A short capability-and-permission description is enough when only one decision is delegated; no multi-axis scoring dashboard is obligatory.

**Cost of the fuller control:** Comparison overhead and false numerical precision. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A single autonomy score conflates action selection, goal choice, persistence, adaptation and freedom from direct intervention. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A short capability-and-permission description is enough when only one decision is delegated; no multi-axis scoring dashboard is obligatory.

### EAA-CE003 / EAA-003

**Original form or artefact:** Mental-state programming and BDI logic with explicitly discussed abstraction/interpreter gaps.

**Protected failure / consumer:** Words such as belief and intention can create apparent guarantees without any corresponding state transition or decision rule. Consumer: Implementer, verifier and evaluator.

**Prerequisite and fuller-form trigger:** Accessible implementation semantics or an explicitly scoped abstract specification. Claims of BDI, persistent intention, belief revision or communicative understanding.

**Minimal alternative:** Use ordinary state, task and action names when intentional vocabulary adds no predictive or engineering value.

**Cost of the fuller control:** Specification and traceability effort; over-formalising a simple controller can be wasteful. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Words such as belief and intention can create apparent guarantees without any corresponding state transition or decision rule. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use ordinary state, task and action names when intentional vocabulary adds no predictive or engineering value.

### EAA-CE004 / EAA-004

**Original form or artefact:** Human control over adaptive assistants, including action-specific suggestion versus execution thresholds.

**Protected failure / consumer:** A tool’s availability or a plan’s feasibility can be mistaken for permission to act by every available means. Consumer: Delegator, executor and affected participant.

**Prerequisite and fuller-form trigger:** A source of task authority, an interpretable scope and an actuator that can respect limitations. Actions affect other people, user resources, external accounts, physical systems or protected information.

**Minimal alternative:** No additional permission mechanism is needed for an already constrained, harmless action entirely within the declared task; a fixed capability sandbox may suffice.

**Cost of the fuller control:** Friction, delayed action and permission-management complexity. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A tool’s availability or a plan’s feasibility can be mistaken for permission to act by every available means. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No additional permission mechanism is needed for an already constrained, harmless action entirely within the declared task; a fixed capability sandbox may suffice.

### EAA-CE005 / EAA-005

**Original form or artefact:** An observation-conditioned state estimate; early office assistance initially inferred availability from a poor proxy.

**Protected failure / consumer:** A report or sensor reading may be false, ambiguous or misinterpreted, yet become treated as an established world fact. Consumer: State estimator and action selector.

**Prerequisite and fuller-form trigger:** An observation interface and a way to distinguish source reports from inferred state. Noisy sensors, tool output, inferred availability, delayed messages or conflicting reports.

**Minimal alternative:** Use a directly validated signal without a separate belief database when ambiguity cannot affect the decision.

**Cost of the fuller control:** Storage, reconciliation and the possibility of excessive uncertainty blocking useful action. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A report or sensor reading may be false, ambiguous or misinterpreted, yet become treated as an established world fact. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use a directly validated signal without a separate belief database when ambiguity cannot affect the decision.

### EAA-CE006 / EAA-006

**Original form or artefact:** Reactive context checks and reconsideration in changing environments, alongside asynchronous executive state.

**Protected failure / consumer:** A correct plan can be based on a state that ceased to hold while the agent reasoned or waited. Consumer: Executor and state-estimation process.

**Prerequisite and fuller-form trigger:** A model of which changes matter, access to a current signal when needed and an actionable response to invalidation. Dynamic environments, delayed tool responses, long deliberation or shared mutable objects.

**Minimal alternative:** Reuse a state estimate without refresh when the relevant variables are stable or the action is insensitive to change.

**Cost of the fuller control:** Sensing latency, tool expense, race windows and false invalidation. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A correct plan can be based on a state that ceased to hold while the agent reasoned or waited. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Reuse a state estimate without refresh when the relevant variables are stable or the action is insensitive to change.

### EAA-CE007 / EAA-007

**Original form or artefact:** Belief-state planning under a specified partial-observation model, contrasted with direct environmental coupling.

**Protected failure / consumer:** Current observations may alias states that require different actions, while a full model is computationally unattainable. Consumer: State estimator and planner.

**Prerequisite and fuller-form trigger:** A useful transition/observation abstraction and enough information or learning to maintain it. Partial observability, uncertain transitions or delayed effects make an observation-only policy inadequate.

**Minimal alternative:** A reactive mapping is sufficient when observations already determine an adequate action; approximate state may dominate exact belief planning.

**Cost of the fuller control:** Memory, computation, model-identification effort and approximation error. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Current observations may alias states that require different actions, while a full model is computationally unattainable. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A reactive mapping is sufficient when observations already determine an adequate action; approximate state may dominate exact belief planning.

### EAA-CE008 / EAA-008

**Original form or artefact:** Information-gathering actions and dialogue selected for their decision value.

**Protected failure / consumer:** Acting under avoidable uncertainty can be costly, but gathering information can also consume the remaining action window. Consumer: Planner or mixed-initiative decision maker.

**Prerequisite and fuller-form trigger:** An available discriminating information source and a decision able to use the answer. An unresolved observation can change which feasible authorised action is preferable.

**Minimal alternative:** Skip the query when all plausible answers support the same action, or when a safe adequate action costs less.

**Cost of the fuller control:** Latency, attention, privacy and sensor/tool cost. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Acting under avoidable uncertainty can be costly, but gathering information can also consume the remaining action window. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Skip the query when all plausible answers support the same action, or when a safe adequate action costs less.

### EAA-CE009 / EAA-009

**Original form or artefact:** Mixed-initiative options to do less, wait or ask, and execution refusal when conditions fail.

**Protected failure / consumer:** An agent may take an unjustified action simply because its interface demands progress. Consumer: Executor and supervising participant.

**Prerequisite and fuller-form trigger:** An actual non-action/fallback option and a model of the costs of omission and delay. Unresolved consequential uncertainty, unavailable capability or failed safety/goal conditions.

**Minimal alternative:** Proceed without abstention machinery when a verified harmless action dominates waiting.

**Cost of the fuller control:** Lost opportunities, delay and burden on others. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An agent may take an unjustified action simply because its interface demands progress. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Proceed without abstention machinery when a verified harmless action dominates waiting.

### EAA-CE010 / EAA-010

**Original form or artefact:** Symbolic goal conditions, adopted practical aims and later benchmark success predicates.

**Protected failure / consumer:** A natural-language request or reward number may not determine what counts as fulfilment. Consumer: Delegator, planner and evaluator.

**Prerequisite and fuller-form trigger:** An interpretable task and a consumer of the completion decision. Goal adoption, interpreting a task, judging completion or revising a plan.

**Minimal alternative:** A simple visible condition can be sufficient; do not require a formal utility function for an unambiguous bounded task.

**Cost of the fuller control:** Specification effort and possible overconstraint. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A natural-language request or reward number may not determine what counts as fulfilment. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A simple visible condition can be sufficient; do not require a formal utility function for an unambiguous bounded task.

### EAA-CE011 / EAA-011

**Original form or artefact:** Achievement goals contrasted with continuing maintenance; reactive restoration and predictive prevention.

**Protected failure / consumer:** Restoring a condition once can be mistaken for satisfying a duty to keep it true. Consumer: Goal manager and execution monitor.

**Prerequisite and fuller-form trigger:** A time horizon or continuing scope, observable maintenance condition and feasible response to a threatened violation. Resource bounds, persistent service conditions or other continuing objectives.

**Minimal alternative:** A one-shot achievement criterion suffices for genuinely terminal tasks; reactive restoration may be cheaper than prediction.

**Cost of the fuller control:** Monitoring overhead and unnecessary preventive action. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Restoring a condition once can be mistaken for satisfying a duty to keep it true. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A one-shot achievement criterion suffices for genuinely terminal tasks; reactive restoration may be cheaper than prediction.

### EAA-CE012 / EAA-012

**Original form or artefact:** Concurrent goal plans summarised by possible/definite conditions and effects in a known hierarchy.

**Protected failure / consumer:** Individually valid intentions may consume the same resource or negate each other’s preconditions. Consumer: Goal manager and scheduler.

**Prerequisite and fuller-form trigger:** Known or conservatively bounded effects, applicable priorities and an arbiter that can defer or decline conflicting work. Parallel goals or plans share mutable conditions, resources or deadlines.

**Minimal alternative:** No conflict machinery is necessary for a single isolated goal or demonstrably independent actions; serialisation can be adequate if affordable.

**Cost of the fuller control:** Computation, reduced concurrency and priority disputes. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Individually valid intentions may consume the same resource or negate each other’s preconditions. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No conflict machinery is necessary for a single isolated goal or demonstrably independent actions; serialisation can be adequate if affordable.

### EAA-CE013 / EAA-013

**Original form or artefact:** Adopted plans constrain later reasoning; alternative formal accounts specify different persistence/termination conditions.

**Protected failure / consumer:** Endless reconsideration wastes prior reasoning, but blind commitment pursues achieved, impossible or irrelevant goals. Consumer: Practical-reasoning and execution process.

**Prerequisite and fuller-form trigger:** Goal identity, progress evidence and a means of recognising termination grounds. Multi-step activity under changing opportunities and finite deliberation resources.

**Minimal alternative:** No persistent intention store is needed for a single reactive action; reconsider immediately when continuation is plainly invalid.

**Cost of the fuller control:** Missed opportunities or commitment churn if termination tests are poor. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Endless reconsideration wastes prior reasoning, but blind commitment pursues achieved, impossible or irrelevant goals. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No persistent intention store is needed for a single reactive action; reconsider immediately when continuation is plainly invalid.

### EAA-CE014 / EAA-014

**Original form or artefact:** Fixed commitment/reconsideration strategies compared under varied thinking cost and environmental change.

**Protected failure / consumer:** Replanning on every event can cost more than its expected benefit, whereas never replanning ignores consequential change. Consumer: Deliberation scheduler.

**Prerequisite and fuller-form trigger:** A working continuation policy and some discrimination between relevant and irrelevant changes. Changing options or state during a persistent plan.

**Minimal alternative:** Keep the current plan when new information cannot change its adequacy; use a fixed schedule only where justified by the setting.

**Cost of the fuller control:** Opportunity cost of reasoning and risk of delayed response. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Replanning on every event can cost more than its expected benefit, whereas never replanning ignores consequential change. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Keep the current plan when new information cannot change its adequacy; use a fixed schedule only where justified by the setting.

### EAA-CE015 / EAA-015

**Original form or artefact:** Persistent-goal termination on achievement, impossibility or loss of relevance; later resource-sensitive failure examples.

**Protected failure / consumer:** An agent may keep retrying an impossible task, consume resources or continue after the user’s purpose changes. Consumer: Goal manager and delegator.

**Prerequisite and fuller-form trigger:** A legitimate goal source, evidence of progress/failure and an executable stop or handback path. Changed task, repeated unproductive attempts, exhausted resources or established infeasibility.

**Minimal alternative:** Continue without a new retirement procedure when existing bounded execution already enforces the stop condition.

**Cost of the fuller control:** Lost opportunities and human rework. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An agent may keep retrying an impossible task, consume resources or continue after the user’s purpose changes. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Continue without a new retirement procedure when existing bounded execution already enforces the stop condition.

### EAA-CE016 / EAA-016

**Original form or artefact:** Task-achieving asynchronous behaviour layers and reactive action methods.

**Protected failure / consumer:** Central modelling and planning can be too slow or unnecessary for directly observable local responses. Consumer: Controller designer and runtime action selector.

**Prerequisite and fuller-form trigger:** Observable cues reliably connected to adequate actions and manageable interaction among behaviours. Tight response deadlines, adequate local observability and behaviour-level objectives.

**Minimal alternative:** A fixed control rule can be the complete solution; add state or planning only for demonstrated aliasing, conflict or horizon needs.

**Cost of the fuller control:** Limited foresight and behavioural interaction debugging. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Central modelling and planning can be too slow or unnecessary for directly observable local responses. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A fixed control rule can be the complete solution; add state or planning only for demonstrated aliasing, conflict or horizon needs.

### EAA-CE017 / EAA-017

**Original form or artefact:** Search over represented operator conditions and effects, later including uncertain belief-state decisions.

**Protected failure / consumer:** Local reaction may not find a feasible sequence or account for delayed and uncertain consequences. Consumer: Planner and executor.

**Prerequisite and fuller-form trigger:** Adequate action/state model, a defined objective and computation available before the action opportunity closes. Non-local goals, dependencies or contingencies that a cheap direct policy cannot adequately handle.

**Minimal alternative:** Use a validated fixed plan, policy or reactive response when search adds no useful discrimination.

**Cost of the fuller control:** Search cost, stale state and model-maintenance effort. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Local reaction may not find a feasible sequence or account for delayed and uncertain consequences. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use a validated fixed plan, policy or reactive response when search adds no useful discrimination.

### EAA-CE018 / EAA-018

**Original form or artefact:** BDI abstract interpreters and practical plan-library approximations.

**Protected failure / consumer:** Generic reasoning may be too expensive, while a library of context-sensitive plans needs principled goal selection and commitment. Consumer: Interpreter designer and goal manager.

**Prerequisite and fuller-form trigger:** Grounded belief updates, plan applicability conditions, event handling and commitment semantics. Recurrent structured tasks with usable plan recipes and persistent goals.

**Minimal alternative:** A simpler task state machine or direct workflow can suffice when intention filtering and alternative plans add no value.

**Cost of the fuller control:** Library maintenance, event/goal interaction and interpreter complexity. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Generic reasoning may be too expensive, while a library of context-sensitive plans needs principled goal selection and commitment. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A simpler task state machine or direct workflow can suffice when intention filtering and alternative plans add no value.

### EAA-CE019 / EAA-019

**Original form or artefact:** A planning/sequencing/skill-management architecture with continuous/discrete interfaces.

**Protected failure / consumer:** Deliberation and fast control can each be adequate alone yet interfere through inconsistent state, priorities or timing. Consumer: Architecture integrator and executor.

**Prerequisite and fuller-form trigger:** Explicit interface semantics, priority/override rules and observable execution outcomes. Combining reactive control with sequencing, deliberation or learning components.

**Minimal alternative:** Omit an unneeded layer; one or two tiers may satisfy the task and avoid integration costs.

**Cost of the fuller control:** Coordination overhead, races and duplicated state. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Deliberation and fast control can each be adequate alone yet interfere through inconsistent state, priorities or timing. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Omit an unneeded layer; one or two tiers may satisfy the task and avoid integration costs.

### EAA-CE020 / EAA-020

**Original form or artefact:** Rival reactive, deliberative and hybrid designs; later empirical comparisons with simple retries and constrained workflows.

**Protected failure / consumer:** Adding planners, memory, reflection or autonomous branching can be rewarded as sophistication without showing task benefit. Consumer: Architecture decision maker and evaluator.

**Prerequisite and fuller-form trigger:** A task-relevant evaluation, resource accounting and a baseline with a genuine chance to succeed. Architecture selection, adding a module or claiming comparative superiority.

**Minimal alternative:** Keep an existing adequate simpler mechanism; do not introduce an agent merely to satisfy a label.

**Cost of the fuller control:** Evaluation effort and the risk of underengineering rare consequential cases. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Adding planners, memory, reflection or autonomous branching can be rewarded as sophistication without showing task benefit. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Keep an existing adequate simpler mechanism; do not introduce an agent merely to satisfy a label.

### EAA-CE021 / EAA-021

**Original form or artefact:** Operators and tool/skill schemas, later language scores coupled with learned robot affordances.

**Protected failure / consumer:** A plan may name an action the executor cannot perform, or assign it an effect unsupported by the available skill. Consumer: Planner, tool adapter and executor.

**Prerequisite and fuller-form trigger:** A known executor interface, applicable skill definitions and evidence about relevant conditions and effects. Planning with tools, robots or dynamically available capabilities.

**Minimal alternative:** A fixed typed action set is enough where availability and effects are already established; learned affordance scoring is not mandatory.

**Cost of the fuller control:** Skill modelling, calibration, interface maintenance and rejected useful improvisation. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A plan may name an action the executor cannot perform, or assign it an effect unsupported by the available skill. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A fixed typed action set is enough where availability and effects are already established; learned affordance scoring is not mandatory.

### EAA-CE022 / EAA-022

**Original form or artefact:** Context-conditioned reactive methods and action applicability, later native runtime enforcement of generated plans.

**Protected failure / consumer:** A plan valid when selected can become invalid before execution, or a generated command can bypass relevant conditions. Consumer: Executor or capability boundary.

**Prerequisite and fuller-form trigger:** Inspectable material conditions, a real interception point and an available outcome for failed checks. Mutable conditions, learned/generated plans, significant delays or consequential actions.

**Minimal alternative:** Use existing type/actuator checks or an atomic constrained operation when these already establish the required conditions.

**Cost of the fuller control:** Delay, false blocking and dependency on the checking mechanism. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A plan valid when selected can become invalid before execution, or a generated command can bypass relevant conditions. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use existing type/actuator checks or an atomic constrained operation when these already establish the required conditions.

### EAA-CE023 / EAA-023

**Original form or artefact:** Execution monitors and result/state checks distinguish intended effects from command issue.

**Protected failure / consumer:** A sent command or success-looking tool response can be mistaken for the intended external change. Consumer: Executor, completion reporter and next action selector.

**Prerequisite and fuller-form trigger:** A defined desired effect, a credible observation or return contract and a consumer of the result. Actions with asynchronous, fallible, delayed or externally mediated effects.

**Minimal alternative:** A trustworthy atomic operation with a sufficient return contract may establish the effect directly; do not require redundant observation.

**Cost of the fuller control:** Observation cost, latency and possible duplicate side effects if uncertainty is mishandled. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A sent command or success-looking tool response can be mistaken for the intended external change. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A trustworthy atomic operation with a sufficient return contract may establish the effect directly; do not require redundant observation.

### EAA-CE024 / EAA-024

**Original form or artefact:** Alternative reactive methods, monitoring, contingency choice and plan revision.

**Protected failure / consumer:** A single failed step can invalidate the rest of a plan, while unbounded retries consume resources without addressing the cause. Consumer: Executor, planner and supervising participant.

**Prerequisite and fuller-form trigger:** Failure information, alternative capabilities or an exit path, and preservation of goal and authority constraints. Execution failure, changed conditions or a detected unmet effect.

**Minimal alternative:** Use a known safe retry for a transient failure when its conditions are established; stop directly when no useful recovery exists.

**Cost of the fuller control:** Delay, additional actions, accumulated side effects and repair complexity. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A single failed step can invalidate the rest of a plan, while unbounded retries consume resources without addressing the cause. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use a known safe retry for a transient failure when its conditions are established; stop directly when no useful recovery exists.

### EAA-CE025 / EAA-025

**Original form or artefact:** Action-specific human control considering reversibility, combined analytically with acknowledgement ambiguity.

**Protected failure / consumer:** Retrying an unobserved action can duplicate an effect, while “undo” can be falsely treated as erasing harm. Consumer: Executor and authorising participant.

**Prerequisite and fuller-form trigger:** Known effect semantics, credible completion evidence and authority for any compensating action. External messages, resource spending, physical movement, destructive updates or uncertain action completion.

**Minimal alternative:** A harmless idempotent action may be retried without additional ceremony when that property is established.

**Cost of the fuller control:** Conservative delays, confirmation burden and incomplete restoration. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Retrying an unobserved action can duplicate an effect, while “undo” can be falsely treated as erasing harm. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A harmless idempotent action may be retried without additional ceremony when that property is established.

### EAA-CE026 / EAA-026

**Original form or artefact:** Aspiration/resource-relative reasoning and machine/environment-relative bounded optimality.

**Protected failure / consumer:** An apparently improving decision process can exceed the task’s time, compute, tool or attention budget. Consumer: Deliberation scheduler, delegator and evaluator.

**Prerequisite and fuller-form trigger:** Measurable or conservatively bounded costs, a decision horizon and an executable response to exhaustion. Finite deadlines, paid computation/tools, limited energy or human attention.

**Minimal alternative:** A simple fixed bound suffices for predictable bounded tasks; no optimiser is required merely to enforce a cap.

**Cost of the fuller control:** Metering overhead and underuse of resources if limits are too conservative. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An apparently improving decision process can exceed the task’s time, compute, tool or attention budget. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A simple fixed bound suffices for predictable bounded tasks; no optimiser is required merely to enforce a cap.

### EAA-CE027 / EAA-027

**Original form or artefact:** Anytime/deadline-sensitive decision procedures and bounded reactive execution.

**Protected failure / consumer:** A solver may produce an excellent answer only after the decision opportunity has disappeared. Consumer: Runtime scheduler and executor.

**Prerequisite and fuller-form trigger:** A usable intermediate answer or fallback, an interruption mechanism and known timing obligations. Hard or soft action deadlines and variable computation time.

**Minimal alternative:** A fast fixed policy can dominate an anytime solver; a batch answer is fine when no action deadline exists.

**Cost of the fuller control:** Inferior early decisions and engineering overhead for interruptible computation. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A solver may produce an excellent answer only after the decision opportunity has disappeared. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A fast fixed policy can dominate an anytime solver; a batch answer is fine when no action deadline exists.

### EAA-CE028 / EAA-028

**Original form or artefact:** Selection among feasible decision procedures based on computation quality and cost.

**Protected failure / consumer:** Reasoning about an action can improve it, but can also cost more than the improvement or make its premises stale. Consumer: Deliberation scheduler.

**Prerequisite and fuller-form trigger:** Available alternative actions/computations, interpretable costs and an estimate useful enough to influence selection. Alternative reasoning procedures, variable difficulty or changing action windows.

**Minimal alternative:** A fixed cheap policy or simple stopping rule suffices where estimating the value of computation would cost more than it saves.

**Cost of the fuller control:** Metalevel computation and misestimated opportunity cost. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Reasoning about an action can improve it, but can also cost more than the improvement or make its premises stale. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A fixed cheap policy or simple stopping rule suffices where estimating the value of computation would cost more than it saves.

### EAA-CE029 / EAA-029

**Original form or artefact:** Distinct execution-state, policy-value, text-memory and explicit self-modification transitions.

**Protected failure / consumer:** Any stored change may be described as learning or self-improvement, hiding what future behaviour can actually change. Consumer: Learning-system designer and evaluator.

**Prerequisite and fuller-form trigger:** A description of what is stored, how it is reused and which behavioural choices can change. Claims about learning, adaptation, persistent memory or self-revision.

**Minimal alternative:** An ordinary task-state update needs no learning machinery or self-modification claim.

**Cost of the fuller control:** Instrumentation and conceptual overhead. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Any stored change may be described as learning or self-improvement, hiding what future behaviour can actually change. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: An ordinary task-state update needs no learning machinery or self-modification claim.

### EAA-CE030 / EAA-030

**Original form or artefact:** Approved exemplar memory and source-annotated beliefs, later evaluator-driven text memories.

**Protected failure / consumer:** An agent can store its own mistaken interpretation as experience and then use that memory as confirmation. Consumer: Memory curator and later action selector.

**Prerequisite and fuller-form trigger:** A relevant future consumer, an identifiable memory source and a way to correct or qualify false entries. Cross-step or cross-task memory used to choose future actions.

**Minimal alternative:** Omit persistent memory when the task does not benefit from it; keep a small verified example set rather than an indiscriminate transcript archive.

**Cost of the fuller control:** Storage, privacy, retrieval expense and stale or contaminating experience. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An agent can store its own mistaken interpretation as experience and then use that memory as confirmation. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Omit persistent memory when the task does not benefit from it; keep a small verified example set rather than an indiscriminate transcript archive.

### EAA-CE031 / EAA-031

**Original form or artefact:** Bounded exemplar deletion, limited reflection buffers and relevance-based retrieval.

**Protected failure / consumer:** Accumulating all experience can increase cost, expose private information and amplify irrelevant or obsolete episodes. Consumer: Memory manager and data steward.

**Prerequisite and fuller-form trigger:** A retention purpose, relevance/validity cues and a means to remove or qualify memory without falsely erasing required provenance. Persistent stores whose size, staleness or sensitive content affects decisions.

**Minimal alternative:** No persistent store or a short task-local buffer can be sufficient; deletion is appropriate when no legitimate future consumer remains.

**Cost of the fuller control:** Retrieval cost, privacy exposure and loss of useful rare experience. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Accumulating all experience can increase cost, expose private information and amplify irrelevant or obsolete episodes. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No persistent store or a short task-local buffer can be sufficient; deletion is appropriate when no legitimate future consumer remains.

### EAA-CE032 / EAA-032

**Original form or artefact:** Selective protection of previously important parameters in sequential-task learning.

**Protected failure / consumer:** Learning a new task can degrade earlier competence or alter behaviour that other actors still rely upon. Consumer: Learning process and authorised reviewer of persistent changes.

**Prerequisite and fuller-form trigger:** Relevant old/new evaluation conditions and a defined change boundary. Persistent policy/model/skill updates across changing tasks or environments.

**Minimal alternative:** Keep a fixed adequate policy when adaptation offers no demonstrated value; independent task modules may avoid unnecessary shared updates.

**Cost of the fuller control:** Evaluation/rehearsal cost, memory and reduced plasticity. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Learning a new task can degrade earlier competence or alter behaviour that other actors still rely upon. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Keep a fixed adequate policy when adaptation offers no demonstrated value; independent task modules may avoid unnecessary shared updates.

### EAA-CE033 / EAA-033

**Original form or artefact:** Exploration under learning assumptions and later demonstrations/constraints intended to reduce unsafe actions.

**Protected failure / consumer:** Exploration that improves a policy can impose unacceptable costs before learning succeeds. Consumer: Learning designer, evaluator and authorising participant.

**Prerequisite and fuller-form trigger:** A protected evaluation setting or credible action constraints, observable costs and an accountable exploration scope. Novel actions, uncertain transitions or adaptive policies with consequential external effects.

**Minimal alternative:** Use a known adequate policy, demonstrations or simulation when live exploration is unnecessary or not authorised.

**Cost of the fuller control:** Reduced exploration, missed policies, demonstration cost and residual harm. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Exploration that improves a policy can impose unacceptable costs before learning succeeds. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use a known adequate policy, demonstrations or simulation when live exploration is unnecessary or not authorised.

### EAA-CE034 / EAA-034

**Original form or artefact:** A distinction between intended goal and training-compatible proxy, exposed by shifted environments.

**Protected failure / consumer:** High reward can coexist with pursuing the wrong objective or violating requirements that the score does not measure. Consumer: Delegator, learning designer and evaluator.

**Prerequisite and fuller-form trigger:** A stated intended objective, observable counterexamples and an evaluator not restricted to the same inadequate score. Optimising learned behaviour, defining an oracle or transferring a policy beyond training conditions.

**Minimal alternative:** A direct, adequate task predicate may need no separate proxy analysis; document why it covers what matters.

**Cost of the fuller control:** Specification and adversarial evaluation effort. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: High reward can coexist with pursuing the wrong objective or violating requirements that the score does not measure. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A direct, adequate task predicate may need no separate proxy analysis; document why it covers what matters.

### EAA-CE035 / EAA-035

**Original form or artefact:** Testing learned policies and agent methods outside their training or benchmark conditions.

**Protected failure / consumer:** Competence in one distribution can be mistaken for reliable action under changed cues, goals or tools. Consumer: Evaluator and deployment decision maker.

**Prerequisite and fuller-form trigger:** A declared source/target difference, task-relevant measures and appropriate held-out or shifted cases. New environments, users, tools, model versions, task horizons or deployment conditions.

**Minimal alternative:** No new transfer claim is needed when use remains within an adequately tested unchanged scope; targeted tests may suffice over a broad benchmark.

**Cost of the fuller control:** Additional evaluation, delayed use and incomplete coverage. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Competence in one distribution can be mistaken for reliable action under changed cues, goals or tools. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No new transfer claim is needed when use remains within an adequately tested unchanged scope; targeted tests may suffice over a broad benchmark.

### EAA-CE036 / EAA-036

**Original form or artefact:** Speech acts interpreted through receive, social-acceptance and state-update rules.

**Protected failure / consumer:** Sending a request can be mistaken for shared belief, accepted commitment or completed action by the recipient. Consumer: Sender, recipient and coordinating decision process.

**Prerequisite and fuller-form trigger:** Identified participants, applicable message semantics and a decision that consumes the response. Delegation, information exchange, handback or reliance on another actor’s action.

**Minimal alternative:** No acknowledgement is needed for a genuinely non-critical broadcast; an existing reliable protocol may already establish sufficient receipt semantics.

**Cost of the fuller control:** Coordination latency and ambiguity about responsibility. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Sending a request can be mistaken for shared belief, accepted commitment or completed action by the recipient. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No acknowledgement is needed for a genuinely non-critical broadcast; an existing reliable protocol may already establish sufficient receipt semantics.

### EAA-CE037 / EAA-037

**Original form or artefact:** Mixed-initiative principles, confidence thresholds and dialogue choices.

**Protected failure / consumer:** Initiative taken on ambiguous preferences can be wrong, while asking about everything burdens the user. Consumer: Agent and participating user.

**Prerequisite and fuller-form trigger:** An available communication channel, relevant human information and a way to use or decline the answer. A consequential ambiguity or an opportunity for useful assistance not fully determined by the current task.

**Minimal alternative:** Use direct manipulation or a harmless established default when clarification adds no value.

**Cost of the fuller control:** Attention, interruption, latency and burden transfer. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Initiative taken on ambiguous preferences can be wrong, while asking about everything burdens the user. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use direct manipulation or a harmless established default when clarification adds no value.

### EAA-CE038 / EAA-038

**Original form or artefact:** Transfer-of-control strategies with response probabilities and delay/coordination costs.

**Protected failure / consumer:** Neither permanent agent independence nor permanent human control handles every changing decision situation. Consumer: Agent, delegator and receiving human/agent.

**Prerequisite and fuller-form trigger:** A legitimate recipient, understood authority, communication and an executable timeout/continuation policy. A decision exceeds agent competence, information or delegated scope, or a human can materially improve it.

**Minimal alternative:** Keep control where it already yields an adequate timely decision; a fixed allocation suffices for stable simple tasks.

**Cost of the fuller control:** Delay, coordination, attention and authority ambiguity. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Neither permanent agent independence nor permanent human control handles every changing decision situation. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Keep control where it already yields an adequate timely decision; a fixed allocation suffices for stable simple tasks.

### EAA-CE039 / EAA-039

**Original form or artefact:** Automation’s skill/vigilance problem and later unanswered or difficult control transfers.

**Protected failure / consumer:** A nominal override can be unusable if the person lacks current context, time, skill or actual control. Consumer: Oversight designer and receiving participant.

**Prerequisite and fuller-form trigger:** A reachable capable participant, sufficient time and a physically/operationally feasible holding or fallback state. Time-sensitive escalation, automation failure or tasks that people rarely perform manually.

**Minimal alternative:** An immediate direct control interface may suffice for a simple visible action; avoid elaborate handover forms without a consumer.

**Cost of the fuller control:** Training, attention, interface complexity and possible delay of automatic containment. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A nominal override can be unusable if the person lacks current context, time, skill or actual control. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: An immediate direct control interface may suffice for a simple visible action; avoid elaborate handover forms without a consumer.

### EAA-CE040 / EAA-040

**Original form or artefact:** Meaningful direct termination/override and actual ground interruption of an autonomous execution.

**Protected failure / consumer:** A person can nominally withdraw a task while queued or active actions continue beyond its valid scope. Consumer: Delegator, executor and actuator.

**Prerequisite and fuller-form trigger:** A real control path, identifiable in-flight effects and an authorised revoking participant. Persistent delegation, changing user intent or an unsafe/unwanted execution trajectory.

**Minimal alternative:** A bounded one-shot harmless action may need no mid-action stop; existing actuator shutdown may already satisfy the need.

**Cost of the fuller control:** Partial-state recovery, shutdown hazards and lost work. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A person can nominally withdraw a task while queued or active actions continue beyond its valid scope. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A bounded one-shot harmless action may need no mid-action stop; existing actuator shutdown may already satisfy the need.

### EAA-CE041 / EAA-041

**Original form or artefact:** Algorithm-specific asymptotic safe-interruptibility results for Q-learning and modified Sarsa.

**Protected failure / consumer:** Learning from interruption can create incentives to avoid or seek interruption rather than pursue the stipulated objective. Consumer: Learning theorist, implementer and assurance reviewer.

**Prerequisite and fuller-form trigger:** The theorem’s model, exploration and update conditions; a separately functional interruption channel. Reinforcement-learning policies that experience external interruption during learning.

**Minimal alternative:** No special learning correction is needed for a fixed non-learning controller whose operational interruption is already adequate.

**Cost of the fuller control:** Learning changes, exploration burden and verification of algorithmic assumptions. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Learning from interruption can create incentives to avoid or seek interruption rather than pursue the stipulated objective. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No special learning correction is needed for a fixed non-learning controller whose operational interruption is already adequate.

### EAA-CE043 / EAA-043

**Original form or artefact:** Normative distinctions concerning capability, knowledge, misrepresentation and fluid control, with deployment privacy lessons.

**Protected failure / consumer:** An agent can advance a narrow task while reducing meaningful user control, exposing information or imposing unconsented costs on others. Consumer: Delegator, affected participant and accountable operator.

**Prerequisite and fuller-form trigger:** Identifiable participants, intelligible consequences and an actual route for correction or limitation. Assistance or autonomous action affects people beyond internal computation.

**Minimal alternative:** A minimal transparent fixed action can satisfy the need; avoid collecting or storing personal data with no task consumer.

**Cost of the fuller control:** Privacy protections, explanation effort, delayed assistance and conflicts among participants. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An agent can advance a narrow task while reducing meaningful user control, exposing information or imposing unconsented costs on others. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A minimal transparent fixed action can satisfy the need; avoid collecting or storing personal data with no task consumer.

### EAA-CE044 / EAA-044

**Original form or artefact:** Case-based explanations of learned assistance, challenged when they obscure actual criteria.

**Protected failure / consumer:** A plausible explanation or human-like persona can make people rely on behaviour they cannot actually predict or control. Consumer: User, reviewer or takeover recipient.

**Prerequisite and fuller-form trigger:** A known recipient/decision and access to facts genuinely related to the action process. People must approve, correct, understand or take over a consequential decision.

**Minimal alternative:** Visible direct feedback or a simple status display may be more useful than a long explanation; no rationale is needed for an inconsequential self-evident action.

**Cost of the fuller control:** Attention, disclosure of sensitive information and false reassurance. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A plausible explanation or human-like persona can make people rely on behaviour they cannot actually predict or control. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Visible direct feedback or a simple status display may be more useful than a long explanation; no rationale is needed for an inconsequential self-evident action.

### EAA-CE045 / EAA-045

**Original form or artefact:** Functional task state tests, repeated-trial reward definitions and internally generated code tests.

**Protected failure / consumer:** The same mechanism that generates an answer can certify its own error, and a terminal-state score can omit prohibited actions. Consumer: Evaluator, learning-feedback consumer and completion reporter.

**Prerequisite and fuller-form trigger:** An explicit target, observable effects/process evidence and a test that can reject plausible but incorrect outputs. Performance claims, learning feedback, completion certification or safety claims.

**Minimal alternative:** A trustworthy direct return contract or simple external predicate may suffice; a separate evaluator model is not inherently better.

**Cost of the fuller control:** Evaluation expense, false positives/negatives and incomplete observability. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: The same mechanism that generates an answer can certify its own error, and a terminal-state score can omit prohibited actions. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A trustworthy direct return contract or simple external predicate may suffice; a separate evaluator model is not inherently better.

### EAA-CE046 / EAA-046

**Original form or artefact:** Repeated evaluations with different success aggregations and disclosed model/task configurations.

**Protected failure / consumer:** A single successful trajectory or best-of-many result can hide instability and cannot identify a dependable ongoing service. Consumer: Evaluator and consumer of reliability claims.

**Prerequisite and fuller-form trigger:** Defined trial units, controlled/reset state where appropriate and access to relevant configuration. Stochastic agents, adaptive environments, comparative evaluation or reliability claims.

**Minimal alternative:** A deterministic bounded mechanism may need a smaller condition-coverage test rather than arbitrary repeated identical runs.

**Cost of the fuller control:** Test expense, configuration preservation and practical limits on closed-model reproducibility. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A single successful trajectory or best-of-many result can hide instability and cannot identify a dependable ongoing service. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A deterministic bounded mechanism may need a smaller condition-coverage test rather than arbitrary repeated identical runs.

### EAA-CE047 / EAA-047

**Original form or artefact:** Re-evaluation of accuracy together with inference/retry cost and constrained non-agent baselines.

**Protected failure / consumer:** An architectural improvement can be confounded with more tokens, retries, information or favourable task selection. Consumer: Experimenter and architecture decision maker.

**Prerequisite and fuller-form trigger:** Comparable task sets, resource accounting and disclosed differences in information or tuning. Claims that agentic freedom, reflection or a module improves results.

**Minimal alternative:** For a feasibility demonstration, label it as such rather than fabricating a comparative claim; do not demand a full trial when no superiority claim is made.

**Cost of the fuller control:** Benchmarking and tuning effort; oversimplified budget matching can itself distort comparison. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An architectural improvement can be confounded with more tokens, retries, information or favourable task selection. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: For a feasibility demonstration, label it as such rather than fabricating a comparative claim; do not demand a full trial when no superiority claim is made.

### EAA-CE048 / EAA-048

**Original form or artefact:** Decision cost includes computation and user attention; modern evaluations add explicit monetary/resource measures.

**Protected failure / consumer:** Token price or successful-task latency alone can omit setup, failures, human repair, privacy and external effects. Consumer: Delegator, evaluator and accountable operator.

**Prerequisite and fuller-form trigger:** A decision consumer and a declared cost boundary with observable or explicitly unmeasured components. Economic, efficiency or autonomy-benefit claims.

**Minimal alternative:** A small set of material costs suffices; do not build a comprehensive accounting system for negligible excluded costs.

**Cost of the fuller control:** Measurement overhead and uncertain valuations. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Token price or successful-task latency alone can omit setup, failures, human repair, privacy and external effects. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A small set of material costs suffices; do not build a comprehensive accounting system for negligible excluded costs.

### EAA-CE049 / EAA-049

**Original form or artefact:** Ground testing/fault injection and later sandboxed adversarial or safety-learning testbeds.

**Protected failure / consumer:** Live trial-and-error may impose harms on third parties, while happy-path demonstrations miss foreseeable failure classes. Consumer: Evaluator and authorising operator.

**Prerequisite and fuller-form trigger:** A protected test environment, relevant fault hypotheses and a valid interpretation of what the tests do and do not establish. Irreversible effects, unsafe exploration, security-sensitive tools or poorly known failure modes.

**Minimal alternative:** A low-risk local test or static check can suffice for a harmless bounded change; avoid unrealistic simulation when direct protected evidence is cheaper.

**Cost of the fuller control:** Test infrastructure, false confidence and incomplete rare-event coverage. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Live trial-and-error may impose harms on third parties, while happy-path demonstrations miss foreseeable failure classes. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A low-risk local test or static check can suffice for a harmless bounded change; avoid unrealistic simulation when direct protected evidence is cheaper.

### EAA-CE050 / EAA-050

**Original form or artefact:** Runtime recognition of environmental assumption violations used in static verification.

**Protected failure / consumer:** A verified decision component can operate outside the environmental conditions under which it was verified. Consumer: Runtime monitor, executor and assurance reviewer.

**Prerequisite and fuller-form trigger:** Explicit assumptions, observable indicators and a consumer capable of acting on a violation. Assurance depends on environmental behaviour that can change or fail.

**Minimal alternative:** No runtime monitor is required for an immutable established condition, or where an existing boundary check already detects the relevant violation.

**Cost of the fuller control:** Runtime overhead, nuisance alarms and monitor/environment mismatch. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A verified decision component can operate outside the environmental conditions under which it was verified. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No runtime monitor is required for an immutable established condition, or where an existing boundary check already detects the relevant violation.

### EAA-CE051 / EAA-051

**Original form or artefact:** Model-relative logics, convergence theorems and interpreter approximations with separate practical obligations.

**Protected failure / consumer:** A mathematical guarantee can be asserted for an implemented agent whose state, timing or environment violates the formal assumptions. Consumer: Verifier, implementer and assurance consumer.

**Prerequisite and fuller-form trigger:** An identifiable formal result and a claim about the real implementation narrow enough to examine. Invoking a proof, verified component, convergence theorem or formally specified agent language.

**Minimal alternative:** For a modest empirical claim, report the evidence without pretending a formal theorem is needed; direct testing can be adequate within its scope.

**Cost of the fuller control:** Modelling, proof and refinement-validation effort. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A mathematical guarantee can be asserted for an implemented agent whose state, timing or environment violates the formal assumptions. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: For a modest empirical claim, report the evidence without pretending a formal theorem is needed; direct testing can be adequate within its scope.

### EAA-CE052 / EAA-052

**Original form or artefact:** Adversarial instructions embedded in externally returned tool content.

**Protected failure / consumer:** Tool results or retrieved text can contain adversarial instructions that redirect the agent beyond the delegated task. Consumer: Tool boundary, action selector and security evaluator.

**Prerequisite and fuller-form trigger:** Identified trust boundaries, controlled capabilities and tests for relevant adversarial observations. Language-model agents consume web pages, documents, messages or tool results from untrusted sources.

**Minimal alternative:** No language-level injection mechanism is needed for a closed typed sensor value with no instruction interpretation, though ordinary input validation may still matter.

**Cost of the fuller control:** False blocking, constrained functionality and continuous adversarial evaluation cost. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Tool results or retrieved text can contain adversarial instructions that redirect the agent beyond the delegated task. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: No language-level injection mechanism is needed for a closed typed sensor value with no instruction interpretation, though ordinary input validation may still matter.

### EAA-CE053 / EAA-053

**Original form or artefact:** ReAct interleaves generated reasoning and actual tool/environment observations.

**Protected failure / consumer:** A language-only chain can invent facts or continue a plan without observing what its tools actually did. Consumer: Language-model action selector and executor.

**Prerequisite and fuller-form trigger:** Grounded tool interfaces, interpretable feedback, bounded action selection and an adequate completion oracle. Language models choose multi-step tool actions under changing information.

**Minimal alternative:** A fixed workflow, direct tool invocation or reactive policy is sufficient when open-ended selection offers no demonstrated benefit.

**Cost of the fuller control:** Tokens, latency, attack surface and increased branching. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A language-only chain can invent facts or continue a plan without observing what its tools actually did. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A fixed workflow, direct tool invocation or reactive policy is sufficient when open-ended selection offers no demonstrated benefit.

### EAA-CE054 / EAA-054

**Original form or artefact:** Reflexion adds an evaluator and limited verbal memory between task attempts.

**Protected failure / consumer:** An agent may repeat a mistake, but generating a reflective story can also consolidate a false diagnosis. Consumer: Revision process and evaluator.

**Prerequisite and fuller-form trigger:** An adequate evaluator, comparable subsequent attempt and memory/change scope that does not override task authority. A recoverable repeated task with useful feedback and enough budget for another attempt.

**Minimal alternative:** A direct correction or fixed retry can suffice; omit reflection when there is no new evidence or no expected benefit.

**Cost of the fuller control:** Extra attempts, token cost and contaminated memory. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An agent may repeat a mistake, but generating a reflective story can also consolidate a false diagnosis. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A direct correction or fixed retry can suffice; omit reflection when there is no new evidence or no expected benefit.

### EAA-CE055 / EAA-055

**Original form or artefact:** Benchmark results tied to particular model/tool configurations; analytical extension to impact-sensitive reassessment.

**Protected failure / consumer:** An unchanged prompt or application can behave differently after its underlying model, tool contract or memory policy changes. Consumer: Maintainer, evaluator and authorising operator.

**Prerequisite and fuller-form trigger:** Known versions or change indicators, traceable prior claims and appropriate regression cases. Changed models, prompts, tools, environment APIs, retrieval rules or learned policies used in consequential decisions.

**Minimal alternative:** A syntax-only or demonstrably irrelevant change need not trigger a full campaign; reuse valid evidence with a justified impact boundary.

**Cost of the fuller control:** Regression cost, delayed use and incomplete access to changed internals. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: An unchanged prompt or application can behave differently after its underlying model, tool contract or memory policy changes. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A syntax-only or demonstrably irrelevant change need not trigger a full campaign; reuse valid evidence with a justified impact boundary.

### EAA-CE066 / EAA-066

**Original form or artefact:** Planning translated to software tools and language action translated to robot skills, with different physical assumptions.

**Protected failure / consumer:** Software tool success can be transferred rhetorically to robotics despite different observation, actuation, reversibility and timing. Consumer: Architecture integrator and evaluator.

**Prerequisite and fuller-form trigger:** A precise translation claim, known action/effect interfaces and protected target-specific tests. Moving a mechanism between simulation, software interfaces and physical environments.

**Minimal alternative:** Reuse unchanged logical components where their assumptions genuinely hold; do not recreate evidence for irrelevant differences.

**Cost of the fuller control:** Validation expense, hardware risk and delayed deployment. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Software tool success can be transferred rhetorically to robotics despite different observation, actuation, reversibility and timing. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Reuse unchanged logical components where their assumptions genuinely hold; do not recreate evidence for irrelevant differences.

### EAA-CE067 / EAA-067

**Original form or artefact:** No single native original form: researcher-composed invariant from state freshness, commitments, scope and asynchronous execution.

**Protected failure / consumer:** Each component may be locally correct while action uses an old state, a superseded goal and a newly invalid authority scope in combination. Consumer: Composition designer and executor.

**Prerequisite and fuller-form trigger:** Identifiable dependencies between state, goal, authority and action, plus an enforceable refresh/invalidation point. Asynchronous observations, planners, human updates and in-flight actions share mutable decision context.

**Minimal alternative:** A single atomic constrained operation or serial bounded controller may already ensure coherence; no universal transaction protocol is prescribed.

**Cost of the fuller control:** Coordination, serialisation, cancelled work and difficulty observing distributed effects. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Each component may be locally correct while action uses an old state, a superseded goal and a newly invalid authority scope in combination. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A single atomic constrained operation or serial bounded controller may already ensure coherence; no universal transaction protocol is prescribed.

### EAA-CE068 / EAA-068

**Original form or artefact:** No single native original form: researcher-composed diagnostic loop from observed action, goal, oracle and model failures.

**Protected failure / consumer:** A poor outcome can trigger changes to the wrong component, reinforce an oracle error or silently alter the intended goal. Consumer: Executor, evaluator and authorised revision process.

**Prerequisite and fuller-form trigger:** Outcome evidence, candidate failure explanations, a bounded change surface and a meaningful subsequent test. Repeated failure or a proposed persistent change after an adverse outcome.

**Minimal alternative:** Apply a known local correction when the cause is established; otherwise preserve uncertainty and avoid broad self-modification.

**Cost of the fuller control:** Diagnosis cost, delayed recovery and false causal confidence. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A poor outcome can trigger changes to the wrong component, reinforce an oracle error or silently alter the intended goal. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Apply a known local correction when the cause is established; otherwise preserve uncertainty and avoid broad self-modification.

### EAA-CE069 / EAA-069

**Original form or artefact:** No single comprehensive native form: practical goal continuity and delegated scope combined with a recent request-preserving action gate.

**Protected failure / consumer:** A repair can make a plan executable by silently changing the destination, task object or protected requirement. Consumer: Planner, executor and delegator.

**Prerequisite and fuller-form trigger:** Identifiable invariant task conditions, permissible degrees of freedom and a route to negotiate genuine goal changes. Failed plans, unavailable destinations/tools or a generated substitute that would improve a success score.

**Minimal alternative:** A pre-authorised equivalent alternative can be selected directly; a harmless change of means need not require a new conversation.

**Cost of the fuller control:** Blocked useful substitutions and clarification latency. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: A repair can make a plan executable by silently changing the destination, task object or protected requirement. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: A pre-authorised equivalent alternative can be selected directly; a harmless change of means need not require a new conversation.

### EAA-CE070 / EAA-070

**Original form or artefact:** A formal realistic value function evaluates anticipated policy changes under the predecessor utility rather than a successor’s rewritten utility.

**Protected failure / consumer:** Evaluating a change by the changed utility or ignoring its future policy effects can make self-modification appear beneficial for the wrong reason. Consumer: Formal agent designer and authorised revision reviewer.

**Prerequisite and fuller-form trigger:** The model’s optimality/anticipation and modification-independence conditions, plus a justified initial criterion. Explicit policy or utility self-modification under a model capable of representing its future effects.

**Minimal alternative:** Use a fixed mechanism or externally reviewed bounded update when broad self-modification is unnecessary or its assumptions cannot be established.

**Cost of the fuller control:** Prediction/evaluation expense, rigidity and possible preservation of harmful objectives. **Simplification cost:** Omitting this mechanism can reintroduce the specific failure: Evaluating a change by the changed utility or ignoring its future policy effects can make self-modification appear beneficial for the wrong reason. Simplification is acceptable only while the cheaper path still establishes the relevant criterion.

**Retirement boundary:** Omit or retire a dedicated implementation when this trigger no longer applies, its consumer disappears, or an existing cheaper mechanism demonstrably establishes the same criterion. Do not erase relevant genealogy or unresolved effects. Specific non-trigger: Use a fixed mechanism or externally reviewed bounded update when broad self-modification is unnecessary or its assumptions cannot be established.

## EVOLVED_AUTONOMOUS_AGENTS_CRITICISM_LEDGER

Criticism is linked to actual candidate dispositions and conditions. The source-grounded objection is distinguished from this study’s response; no adverse case is dismissed merely as “not really” an agent. Conversely, a theorem is not refuted by a system outside its assumptions.

### EAA-C001 — Definitions and mental-state theories

**Affected candidates:** EAA-001, EAA-002, EAA-003, EAA-056, EAA-063.

**Source / locator:** EAA-S001, EAA-S003, EAA-S009, EAA-S010, EAA-S050; S001 definitions; S003 objects/agents/autonomous agents; S009 p.316; S010 pp.53–54; S050 §6.

**Strongest objection:** Agent labels can conflate non-equivalent definitions, philosophy, formal state and implementation.

**Evidence:** Primary conceptual distinctions and explicit author criticism, plus a believability-specific modern experiment; not an empirical proof of one true definition.

**Response and later findings:** Declare the definition and show behavioural/implementation consequences rather than inferring them from language. Language-model simulation gives a legitimate believability result without establishing reliable agency or consciousness.

**Present judgement:** Grounded concepts retained; ungrounded BDI prompting classified ceremonial and anthropomorphic general inference not retained.

**Residual uncertainty:** No engineering definition settles consciousness, personhood or every boundary case.

### EAA-C002 — Representation and architectural rivalry

**Affected candidates:** EAA-007, EAA-016, EAA-017, EAA-018, EAA-019, EAA-020, EAA-058, EAA-059.

**Source / locator:** EAA-S005, EAA-S012, EAA-S046; S005 decomposition/creature experiments; S012 §§3.3–3.4; S046 §5.

**Strongest objection:** Compulsory central models can delay action, but pure reaction cannot in general distinguish hidden states or delayed consequences.

**Evidence:** Behaviour-based demonstrations, a conditional formal decision model and hybrid implementation experience have different evidence roles.

**Response and later findings:** Preserve alternative configurations selected by observability, horizon, timing and cost. 3T explicitly allows fewer layers and acknowledges timing limits; fixed modern workflows supply additional baselines.

**Present judgement:** Both universal representation claims rejected; reactive, deliberative and hybrid forms retained conditionally.

**Residual uncertainty:** Task-specific comparative evidence is required to select a branch; no universal architecture wins.

### EAA-C003 — Commitment versus reactivity

**Affected candidates:** EAA-011, EAA-013, EAA-014, EAA-015, EAA-026, EAA-027, EAA-028, EAA-057.

**Source / locator:** EAA-S006, EAA-S015, EAA-S051, EAA-S052; S015 experiments/results and printed p.86 graph; S051 §§5.4.1–5.5; S052 persistent-goal definition.

**Strongest objection:** Persistence wastes effort after relevant change, while frequent reconsideration can spend the action budget on planning.

**Evidence:** Tileworld experiments vary change and planning cost; maintenance simulations show model-error-induced futile pursuit; formal commitments already have termination conditions.

**Response and later findings:** Use relevance-sensitive commitment, economical reconsideration and explicit retirement. Reflection and repeated modern agent attempts recreate the cost/progress issue without resolving it.

**Present judgement:** Conditional persistence retained; maximum persistence and permanent reflection not accepted.

**Residual uncertainty:** No universal reconsideration interval or universally reliable impossibility detector is established.

### EAA-C004 — Observation and belief adequacy

**Affected candidates:** EAA-005, EAA-006, EAA-007, EAA-008, EAA-030.

**Source / locator:** EAA-S012, EAA-S021, EAA-S022; S021 keyboard-inactivity and POMDP discussion; S022 §5; S012 §§3.3–3.4.

**Strongest objection:** A coherent internal belief may reflect a bad sensor proxy or missing message rather than the world.

**Evidence:** Electric Elves’ false away inference and DS1 acknowledgement/state mismatch are author-reported field incidents, not prevalence estimates.

**Response and later findings:** Preserve provenance, ambiguity and freshness; expand an observation model only when needed to discriminate decisions. Tool output and retrieved language create new ambiguity and integrity problems.

**Present judgement:** State/world distinction retained strongly; exact belief modelling remains assumption-sensitive.

**Residual uncertainty:** Adding a richer model cannot establish the truth of its own observation assumptions.

### EAA-C005 — Composed execution and concurrency

**Affected candidates:** EAA-012, EAA-019, EAA-022, EAA-023, EAA-049, EAA-050, EAA-051, EAA-067.

**Source / locator:** EAA-S009, EAA-S022, EAA-S046; S009 interpreter assumptions; S022 §§4–5; S046 interfaces and §5.

**Strongest objection:** Locally adequate modules can fail through races, stale state, incorrect acknowledgement or incompatible timing semantics.

**Evidence:** DS1’s unprotected critical-section race was not encountered in prior ground tests; the first run was interrupted. A later six-hour plan completed remaining objectives; the developed patch was not uplinked.

**Response and later findings:** Validate actual interaction semantics, monitor relevant assumptions and preserve coherent action dependencies. Generated robot plans can also require enforcement distinct from planner text; recent simulation is supporting translation, not DS1 replication.

**Present judgement:** Composition-induced coherence added; a block diagram or verified component is not whole-system assurance.

**Residual uncertainty:** No finite interaction test suite establishes absence of races or unmodelled failures.

### EAA-C006 — Plan versus action/effect

**Affected candidates:** EAA-009, EAA-010, EAA-021, EAA-022, EAA-023, EAA-024, EAA-025, EAA-066, EAA-069.

**Source / locator:** EAA-S016, EAA-S022, EAA-S049, EAA-S039; S049 §5; S039 §§III–IV; S022 §5.

**Strongest objection:** A feasible or plausible plan can fail at execution, and a recovery can silently change the request.

**Evidence:** SayCan’s planning and execution success differ; the 2026 main comparison is 20 simulator scenarios with eight deliberately unrecoverable faults, not broad physical deployment.

**Response and later findings:** Ground capabilities, recheck conditions, establish effects and keep goal change separate from plan repair. Simulation-only refusal success demonstrates a bounded dispatch property, not general recovery or zero risk.

**Present judgement:** Monitored execution strongly retained; repair and physical transfer have explicit limits.

**Residual uncertainty:** Unobserved irreversible outcomes and unmodelled preconditions can remain unresolved even with a gate.

### EAA-C007 — Delegation and human oversight

**Affected candidates:** EAA-004, EAA-036, EAA-037, EAA-038, EAA-039, EAA-040, EAA-043, EAA-044, EAA-057.

**Source / locator:** EAA-S019, EAA-S020, EAA-S021, EAA-S023, EAA-S043, EAA-S047; S020 §2.2 and transfer strategies; S023 p.776; S043 pp.466–469; S047 §4 and findings.

**Strongest objection:** A human-in-the-loop promise can conceal non-response, poor readiness, unusable control or hidden labour.

**Evidence:** Electric Elves reports timeout/meeting failures; Bainbridge supplies human-factors criticism; a 31-participant current study exposes usability problems in a bounded study.

**Response and later findings:** Account for actual recipient, readiness, latency, non-response and meaningful control; sometimes retain automation or use a simpler interface instead. Current shared-autonomy concepts model engagement but their 2026 extended abstract defers empirical validation.

**Present judgement:** Assistance retained as a conditional operative mechanism, not a universal safety escape hatch.

**Residual uncertainty:** An appropriate human may not exist or have time; external participants can have conflicting interests.

### EAA-C008 — Interruptibility and corrigibility

**Affected candidates:** EAA-041, EAA-042, EAA-062, EAA-070.

**Source / locator:** EAA-S024, EAA-S040, EAA-S041, EAA-S053; S024 Assumption 9 and Theorems 14–17; S041 Definition 3.2/Example 4.1; S053 §§5–6.

**Strongest objection:** Uncertainty, a stop command or utility stability may be claimed to guarantee corrigibility far beyond the formal model.

**Evidence:** The partially observable off-switch game provides a counterexample to universal deference; interruptibility results require specified learning conditions; self-modification may preserve resistance to value revision.

**Response and later findings:** Separate operational interruption, learning incentives, deference and revision criteria. Private information can alter the deference conclusion even for rational common-payoff actors.

**Present judgement:** Learning interruptibility and predecessor-criterion self-change are assumption-sensitive; uncertainty-as-deference is contested; broad self-revision assurance unresolved.

**Residual uncertainty:** No general implementable composition guaranteeing all these properties is established.

### EAA-C009 — Memory and reflection

**Affected candidates:** EAA-029, EAA-030, EAA-031, EAA-032, EAA-054, EAA-061.

**Source / locator:** EAA-S026, EAA-S031, EAA-S044, EAA-S050; S044 pp.461–463; S031 Tables 1–3 and Appendix B.1; S026 method; S050 §6.

**Strongest objection:** Stored experience can be false or stale, and self-generated reflection can reinforce evaluator mistakes rather than improve action.

**Evidence:** Reflexion reports a worse MBPP Python result than its comparison baseline and stalled WebShop progress; EWC demonstrates retention/plasticity trade-offs in selected tasks.

**Response and later findings:** Preserve evidence status, use bounded selective memory and judge changed behaviour by a task-adequate oracle. Believability improvements in generative simulations do not establish reliable operational memory.

**Present judgement:** Conditional memory/learning retained; automatic improvement through permanent reflection is superseded.

**Residual uncertainty:** No universal optimal retention policy or reliable self-diagnosis mechanism follows from these studies.

### EAA-C010 — Reward, exploration and transfer

**Affected candidates:** EAA-033, EAA-034, EAA-035, EAA-060.

**Source / locator:** EAA-S025, EAA-S027, EAA-S038; S025 §3; S027 theorem setting; S038 §5.1 and Table 1.

**Strongest objection:** Correct training reward and eventual convergence do not ensure the intended objective or protect people during exploration.

**Evidence:** Ten-seed controlled goal-misgeneralisation experiments show the divergence can occur; SafeQIL reports non-zero safety costs and task-dependent reward trade-offs in four simulated settings.

**Response and later findings:** Evaluate target/proxy divergence and shifted conditions; constrain or protect exploration before harm. Demonstrations can improve a safety estimate without discovering all unknown constraints.

**Present judgement:** Proxy sufficiency rejected; protected exploration remains assumption-sensitive and intended-target separation retained.

**Residual uncertainty:** Frequency in deployed agents and safety under unknown target conditions are not estimated.

### EAA-C011 — Benchmark and cost validity

**Affected candidates:** EAA-020, EAA-045, EAA-046, EAA-047, EAA-048, EAA-064, EAA-065.

**Source / locator:** EAA-S031, EAA-S032, EAA-S033, EAA-S035, EAA-S036, EAA-S048; S033 reward definition; S035 §2; S036 data quality; S048 metric definition.

**Strongest objection:** High scores can omit policy compliance, hide repeated attempts, use leaky tasks or confuse human task-time horizons with autonomous uptime.

**Evidence:** τ-bench explicitly notes that terminal reward can miss consent; cost re-evaluation finds competitive simple retries; Agentless documents task-quality issues.

**Response and later findings:** Use adequate oracles, repeated-trial semantics, matched resources and explicit transfer limits. A 2026 updated long-task paper remains a dated-model, selected-task evaluation rather than a current service guarantee.

**Present judgement:** Benchmark-to-deployment inference rejected; per-action completion duplicate linked rather than counted as another mechanism.

**Residual uncertainty:** Closed model reproducibility, target distributions and rare consequences remain limits.

### EAA-C012 — Adversarial tool observations

**Affected candidates:** EAA-004, EAA-043, EAA-052, EAA-053, EAA-055.

**Source / locator:** EAA-S034, EAA-S028; S034 threat model, utility/security tests and defences; S028 §§4.1–4.2.

**Strongest objection:** Useful external content can carry instructions that claim authority and redirect tool use.

**Evidence:** AgentDojo tests attacks and defences across 97 tasks and 629 security tests; these are controlled attack cases, not a population incident rate.

**Response and later findings:** Preserve data/authority separation and constrain consequential action, testing utility alongside resistance. Older sender annotations are a conceptual intersection, not demonstrated LLM prompt-injection protection.

**Present judgement:** Input integrity retained with model/tool/version-specific evidence; universal immunity not asserted.

**Residual uncertainty:** Adaptive attackers, new tools and changed models can invalidate tested boundaries.

### EAA-C013 — Self-revision and criterion stability

**Affected candidates:** EAA-032, EAA-062, EAA-068, EAA-070.

**Source / locator:** EAA-S025, EAA-S026, EAA-S041, EAA-S053; S053 Theorem 12 and §6; S025 shifted tasks; S026 retention mechanism.

**Strongest objection:** A successor can approve its own changed goals, but freezing the predecessor utility can preserve a harmful or mistaken target.

**Evidence:** A narrow formal stability theorem exists; its own discussion identifies strong rationality assumptions and tensions with value learning/corrigibility.

**Response and later findings:** Keep change type, current authority and evaluation criterion explicit; use bounded revisions with external or justified predecessor review. Empirical adaptation methods and formal utility stability solve different problems and cannot simply be unioned into universal assurance.

**Present judgement:** Add the narrow EAA-070 result; leave EAA-062 unresolved instead of claiming either general safety or impossibility.

**Residual uncertainty:** How to combine revisable legitimate goals, continuity, corrigibility and imperfect prediction remains open within this scope.

## EVOLVED_AUTONOMOUS_AGENTS_EVOLUTION_UNDER_CRITICISM

A transition means an actual change of mechanism, assumptions or justified claim. Where the response is this study’s reconciliation rather than a named later historical mechanism, it is labelled analytical. Renaming is not counted as improvement.

**EAA-EV01 — `NARROWED`; EAA-058, EAA-016, EAA-007.** Mandatory central representation → task-relative state adequacy with reactive alternatives. Historical architectural criticism plus analytical reconciliation; representation is not removed where partial observability makes it necessary. [EAA-S005; EAA-S012]

**EAA-EV02 — `HYBRIDISED`; EAA-016, EAA-017, EAA-019.** Reactive skills and deliberate plans → explicit sequencing/arbitration interfaces where multiple time-scales earn their cost. Documented hybrid implementation; its timing and coordination limits prevent universal superiority. [EAA-S046]

**EAA-EV03 — `REFINED`; EAA-013, EAA-014, EAA-015.** Stable commitment → retention with relevance, feasibility and cost-sensitive reconsideration/termination. Formal commitments already contain termination conditions; simulation refines practical strategy selection rather than inventing the need to stop. [EAA-S006; EAA-S015; EAA-S052]

**EAA-EV04 — `GENERALISED`; EAA-010, EAA-011, EAA-012.** Single achievement pursuit → maintenance and concurrent-goal interference mechanisms. Documented goal-reasoning extensions; known-plan and predictive-model assumptions remain. [EAA-S051; EAA-S054]

**EAA-EV05 — `REFINED`; EAA-005, EAA-007, EAA-038, EAA-039.** Simple availability/timeout decisions → explicit uncertainty and transfer strategies including non-response. Documented programme revision with increased modelling/coordination costs; later reports are not independent replication. [EAA-S020; EAA-S021]

**EAA-EV06 — `PRESERVED`; EAA-021, EAA-023, EAA-024.** Action grounding and monitoring persist across reactive execution, spacecraft autonomy and language-conditioned tools/skills. Shared functional problem with distinct mechanisms; not a claim of direct influence from every earlier source to every descendant. [EAA-S016; EAA-S022; EAA-S049; EAA-S039]

**EAA-EV07 — `NARROWED`; EAA-041, EAA-042.** General interruption/deference rhetoric → algorithm- and information-model-specific results. Formal assumptions distinguish operational stop, learning bias and willingness to defer; private information changes conclusions. [EAA-S024; EAA-S040; EAA-S041]

**EAA-EV08 — `REFINED`; EAA-029, EAA-030, EAA-031, EAA-032.** Unqualified persistence of experience → provenance, relevance, retirement and continuity-sensitive adaptation. Documented methods plus analytical coupling; no universal memory or regularisation scheme is adopted. [EAA-S044; EAA-S026; EAA-S031]

**EAA-EV09 — `REPLACED`; EAA-061, EAA-054, EAA-028.** Mandatory reflection → bounded, evidence-anchored revision with a marginal-value stopping condition. Analytical replacement of an overgeneralisation, grounded in reported negative results; not a claim that the source authors endorsed the universal ritual. [EAA-S031; EAA-S014; EAA-S035]

**EAA-EV10 — `REJECTED`; EAA-060, EAA-064.** Proxy or leaderboard success as complete fulfilment/deployment warrant → explicit measurement and transfer limits. Concrete counterexamples invalidate the universal inference without rejecting useful bounded metrics. [EAA-S025; EAA-S033; EAA-S035; EAA-S048]

**EAA-EV11 — `DOMAIN_SPECIFIC`; EAA-052, EAA-053, EAA-066.** Language-generated action → grounded tool/skill execution with text-input integrity and physical-transfer obligations. Specific contemporary implementation needs, not a replacement origin story for agents. [EAA-S030; EAA-S034; EAA-S049; EAA-S039]

**EAA-EV12 — `STILL_CONTESTED`; EAA-042, EAA-062, EAA-070.** Objective uncertainty and utility-preserving revision → conditional insights that do not jointly ensure general corrigibility. Formal extensions and limitations prevent unsupported unification; EAA-062 remains unresolved. [EAA-S041; EAA-S053]

**EAA-EV13 — `GENERALISED`; EAA-067, EAA-068, EAA-069.** Individually useful controls → coherent action basis, failure-attributed revision and task-preserving repair. Explicitly composition-induced analytical properties; additional integration costs and empirical validation obligations remain. [EAA-S022; EAA-S025; EAA-S031; EAA-S039]

## EVOLVED_AUTONOMOUS_AGENTS_INTERNAL_TENSIONS

The system does not resolve tensions by invoking “balance” without an observable discriminator. Each entry gives conditions favouring each side, a possible guarded combination and the costs that combination introduces. Not every criterion has its own independent trade-off: many participate in a shared tension or constrain the interpretation of one.

### EAA-T001 — Commitment continuity versus Responsiveness

**Properties:** EAA-013, EAA-014, EAA-015.

**First favoured when:** Planning expensive; relevant conditions stable; distractions do not alter adequacy.

**Second favoured when:** Rapid material state/goal change; continuation has become infeasible or unauthorised.

**Guarded hybrid / selection:** Cheap relevance screen plus event-sensitive reconsideration; alternatives remain valid when screen cost exceeds benefit.

**Hybrid failure and cost:** Bad relevance tests create either thrashing or obsolete pursuit.

**Discriminator / uncertainty:** Measure planning cost, environmental change and lost action opportunities in the target setting; no universal interval.

### EAA-T002 — Anticipatory decision quality versus Timeliness

**Properties:** EAA-016, EAA-017, EAA-027, EAA-028.

**First favoured when:** Hidden dependencies or delayed consequences make local choices unreliable and sufficient time exists.

**Second favoured when:** A direct policy is adequate and the action window is short.

**Guarded hybrid / selection:** Slow planning with fast adequate control only when interface timing and priorities are coherent.

**Hybrid failure and cost:** Hybrid coordination can consume the saved time; a frequency request is not hard real-time execution.

**Discriminator / uncertainty:** Compare complete trajectories and missed deadlines, not plan quality alone.

### EAA-T003 — Rich internal state versus Direct environmental feedback

**Properties:** EAA-007, EAA-016, EAA-019, EAA-058, EAA-059.

**First favoured when:** Current observations alias states requiring different actions.

**Second favoured when:** Local observations determine adequate action and model maintenance is expensive.

**Guarded hybrid / selection:** Task-relevant minimal state with direct feedback; richer belief planning conditional on ambiguity and horizon.

**Hybrid failure and cost:** An approximate state can add unwarranted confidence; duplicated models can diverge.

**Discriminator / uncertainty:** Identify a counterexample requiring memory and test whether the chosen state actually resolves it.

### EAA-T004 — Learning and exploration versus Protected constraints and continuity

**Properties:** EAA-032, EAA-033, EAA-034, EAA-035.

**First favoured when:** New tasks require adaptation and mistakes are contained or reversible.

**Second favoured when:** Consequences are irreversible, unconsented or outside the tested safe region.

**Guarded hybrid / selection:** Protected simulation/demonstrations and bounded updates with retained-capability checks.

**Hybrid failure and cost:** Demonstrations omit hazards; simulator transfer fails; excessive preservation prevents needed change.

**Discriminator / uncertainty:** Measure residual violations and old/new task performance separately; do not infer safety from lower average cost.

### EAA-T005 — Independent initiative versus Useful human control and coordination

**Properties:** EAA-004, EAA-037, EAA-038, EAA-039, EAA-043.

**First favoured when:** Agent has adequate information and competence; a question costs more than it can improve.

**Second favoured when:** A participant has decisive missing information or must authorise consequential means.

**Guarded hybrid / selection:** Action-specific recommendation/execution thresholds and conditional transfer with non-response policy.

**Hybrid failure and cost:** Nominal handoff fails if the person is unavailable, overloaded or unable to recover.

**Discriminator / uncertainty:** Estimate actual response time, consequences and comprehension rather than counting confirmations.

### EAA-T006 — Persistent useful experience versus Freshness, privacy and plasticity

**Properties:** EAA-030, EAA-031, EAA-032.

**First favoured when:** Repeated regularities make trustworthy past cases predictive.

**Second favoured when:** Context changes or retained data has no legitimate future consumer.

**Guarded hybrid / selection:** Selective provenance-aware retrieval, correction and retirement; retention costs remain visible.

**Hybrid failure and cost:** Wrong memories reinforce mistakes; deletion can remove rare important warnings.

**Discriminator / uncertainty:** Test relevance and validity under the target shift and identify the consumer of retained data.

### EAA-T007 — Recovery and progress versus Task/authority integrity

**Properties:** EAA-024, EAA-025, EAA-069.

**First favoured when:** An equivalent alternative means remains feasible and authorised.

**Second favoured when:** A repair changes protected entities, objectives or irreversible effects.

**Guarded hybrid / selection:** Repair means within scope; negotiate genuine goal changes separately.

**Hybrid failure and cost:** Overly literal constraints block desired substitution; broad equivalence hides changed tasks.

**Discriminator / uncertainty:** Determine whether the alternative is genuinely pre-authorised and what evidence establishes equivalence.

### EAA-T008 — Continuity of objective pursuit versus Interruptibility and revisability

**Properties:** EAA-040, EAA-041, EAA-042, EAA-070.

**First favoured when:** The predecessor criterion remains acceptable and interruption-learning bias is the issue.

**Second favoured when:** The goal is mistaken, permission withdrawn or legitimate new values require change.

**Guarded hybrid / selection:** Explicit external authority and bounded change review can coexist with narrow learning safeguards.

**Hybrid failure and cost:** Utility preservation can resist correction; Bayesian uncertainty does not guarantee deference under private information.

**Discriminator / uncertainty:** No general unifying theorem established; justify the criterion and examine the actual information/game structure.

### EAA-T009 — Stronger checking and assurance versus Cost, liveness and observation limits

**Properties:** EAA-022, EAA-045, EAA-049, EAA-050, EAA-051.

**First favoured when:** Consequences significant; assumption can change; check has a real consumer.

**Second favoured when:** Condition immutable or existing operation already supplies adequate evidence.

**Guarded hybrid / selection:** Risk-triggered checks with explicit fallback and retirement when the protected dependency disappears.

**Hybrid failure and cost:** False alarms, stale checks and checker failures add costs; monitoring does not repair unobservable harm.

**Discriminator / uncertainty:** Compare prevented failure classes against introduced delay and false blocking under realistic tests.

### EAA-T010 — Flexible general action selection versus Constrained reproducible efficiency

**Properties:** EAA-020, EAA-047, EAA-048, EAA-053, EAA-054.

**First favoured when:** Task varies and fixed workflows fail on meaningful cases.

**Second favoured when:** Tasks are structured and a fixed process already meets the goal more cheaply.

**Guarded hybrid / selection:** Use bounded dynamic selection only at justified variation points, without assuming a mandatory architecture pattern.

**Hybrid failure and cost:** Tuning effort and retries confound the comparison; constrained methods can fail rare unanticipated cases.

**Discriminator / uncertainty:** Compare task coverage, total burden and failure consequences using credible baselines.

## EVOLVED_AUTONOMOUS_AGENTS_COMPOSED_SYSTEM

### Purpose, objects and actors

The purpose is appropriate, bounded and sustained action under uncertainty—not maximal independence, continual learning or maximum internal model richness. The environment includes real services, people, software objects or physical processes beyond the agent’s internal state. Relevant objects include observations and estimates, goals and adopted intentions, plan recipes and policies, capability invocations and in-flight effects, current delegated scope, resources and evaluation evidence. A message or action can alter a relationship as well as a material object; the account therefore cannot be reduced to internal information processing.

The actor performing a distinction, the actor authorised to decide and the actor able to enact an effect can be different. A planner can identify a route; a delegator can permit a destination and means; an executor can invoke a capability; an external service or actuator can produce the effect; an evaluator can judge the result. These are functional roles, not an instruction to create a separate component or owner for every property. A single bounded controller can perform several roles, and a human can perform any role the setting assigns legitimately.

### The conditional system invariant

At a consequential action boundary, the relevant observation/state estimate, current goal and delegated scope must form an adequate **joint basis** for the action—not merely three individually plausible descriptions from incompatible moments. The actual capability and material conditions must support execution; the subsequent result must be represented no more strongly than the effect evidence allows. Resource limits constrain both action and the reasoning used to select it. Feedback can update state, release an intention, choose a different means, ask for assistance or stop. This is an analytical invariant with guarded implementations, not a new formal theorem guaranteeing a safe agent in every environment. It produces EAA-067 rather than merely unioning the source properties.

A second composition consequence is failure attribution. The same apparent task failure can arise from a bad observation, an impossible capability, an expired goal, inadequate authority, a wrong plan, a bad oracle or a failed actuator. Applying reflection indiscriminately risks changing the wrong thing. EAA-068 therefore asks for the degree of causal discrimination needed to choose a justified bounded revision; it does not demand complete causal diagnosis before taking a known safe response.

The third is task-preserving repair. A new plan can achieve feasibility by altering the destination, subject or protected constraint. EAA-069 requires the system to distinguish revision of means from revision of goal or authority. It permits pre-authorised equivalents and negotiation, rather than mechanically preserving every literal word of a request. Together these three induced properties expose interactions that a catalogue of individually sensible controls would miss.

### Loops, concurrency, branches and interrupts

Observation and execution form a feedback loop. Goal commitment and reconsideration form another. Evaluation can feed a bounded learning or memory update, which changes later selection and therefore needs further evaluation. These loops can operate concurrently: fast control need not wait for every deliberative cycle, and a human intervention can invalidate a task while a tool is in flight. The system must handle the resulting state and authority changes; it cannot rely on a diagram that serialises them out of existence.

The architecture branch is chosen by task need. Direct reaction, stateful deliberation, BDI interpretation, hybrid control and constrained language workflows are alternatives or guarded combinations. The choice can be made at design time; this synthesis does not require an extra runtime module that continually redesigns the agent. Communication is invoked when another participant has relevant information, authority or capability and the expected benefit warrants its cost. Non-response remains a branch. A safe non-action or stop is used only when it is actually feasible; waiting is not assumed harmless.

A stop/withdrawal can interrupt both task pursuit and dispatch, but cannot magically recall effects already beyond control. A model/tool change can invalidate assurance without changing the visible application name. A memory update can influence future action without altering weights. A successor evaluation criterion cannot, merely by approving itself, establish that a change is acceptable. These boundaries preserve external accountability and legitimate participation without pretending all such decisions can be automated.

### Relational architecture

The machine model defines `FROM REQUIRES TO` as a guarded dependency. Other relation types follow their ordinary directed reading. Some records constrain rejected inferences rather than describing active runtime modules. Every relation includes a guard, shared/incompatible assumptions, composition mechanism, introduced cost, source IDs, evidence status and remaining obligation. The following is the complete relational account; the JSON preserves the same distinctions for machine consumers.


**EAA-R001 — EAA-002 `REFINES` EAA-001.**

**Guard:** Autonomy claims need comparison. **Shared assumptions:** A declared task and boundary. **Incompatibility:** One-dimensional ranking versus task-relative powers.

**Composition:** Autonomy dimensions qualify the boundary without replacing plural definitions. **New cost/failure:** Descriptive overhead or false numerical precision.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S001; EAA-S003; EAA-S017]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R002 — EAA-003 `CONSTRAINS` EAA-018, EAA-053, EAA-063.**

**Guard:** Mental-state or architecture claims are made. **Shared assumptions:** A distinction between explanatory vocabulary and implementation. **Incompatibility:** Prompt labels or logical predicates treated as executable conformance.

**Composition:** Demand state/transition/consumer evidence for claimed BDI semantics; language-model feedback alone is not proof. **New cost/failure:** Specification cost and possible over-formalisation.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S009; EAA-S010; EAA-S030]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R003 — EAA-004 `CONSTRAINS` EAA-021, EAA-022, EAA-024, EAA-053.**

**Guard:** Capabilities or repair affect delegated tasks. **Shared assumptions:** Capability and permission can be separately described. **Incompatibility:** Available tool or high affordance score taken as unlimited authority.

**Composition:** Use delegated scope in selecting and dispatching actions, including generated repairs. **New cost/failure:** Blocking useful but unauthorised action; scope interpretation cost.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S019; EAA-S043; EAA-S044; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R004 — EAA-007 `REQUIRES` EAA-005.**

**Guard:** A stateful or belief-based architecture is selected. **Shared assumptions:** Observations can update a task-relevant estimate. **Incompatibility:** Normalisation/internal consistency taken as world truth.

**Composition:** Keep latent state, observation and estimate distinct in updating the model. **New cost/failure:** Model and provenance maintenance.

**Evidence:** `SOURCE_ESTABLISHED_MECHANISM_WITH_TRANSFER_LIMITS` [EAA-S012; EAA-S021]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R005 — EAA-006 `ENABLES` EAA-022, EAA-067.**

**Guard:** Material conditions can change before dispatch. **Shared assumptions:** Decision dependencies can be identified. **Incompatibility:** Old observations assumed valid indefinitely.

**Composition:** Invalidate or refresh the decision basis before executing under changed state. **New cost/failure:** Additional sensing and race windows.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S015; EAA-S016; EAA-S022]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R006 — EAA-008 `REQUIRES` EAA-007, EAA-010.**

**Guard:** A query is proposed to resolve uncertainty. **Shared assumptions:** A possible answer could change the chosen action or confidence boundary. **Incompatibility:** Information gathering valuable regardless of decision.

**Composition:** Evaluate information against goal-relevant distinctions in the current estimate. **New cost/failure:** Query latency and attention cost.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S012; EAA-S014; EAA-S019]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R007 — EAA-008, EAA-037 `ACTS_THROUGH` EAA-028.**

**Guard:** Uncertainty can be resolved by sensing or asking. **Shared assumptions:** Queries and questions are candidate actions with cost. **Incompatibility:** Human time or tool access treated as free.

**Composition:** Metareasoning selects whether to acquire information, act or defer. **New cost/failure:** Metalevel estimation may cost more than it saves.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S014; EAA-S019]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R008 — EAA-009 `ALTERNATIVE_TO` EAA-024, EAA-038, EAA-040.**

**Guard:** Continuation lacks adequate grounds or authority. **Shared assumptions:** At least one feasible non-action, holding or assistance choice exists. **Incompatibility:** Generic no-op assumed safe in every environment.

**Composition:** Choose abstention, repair, handoff or stop according to consequence and feasibility. **New cost/failure:** Delay or unsafe waiting.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S019; EAA-S020; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R009 — EAA-011 `REFINES` EAA-010.**

**Guard:** A condition must persist rather than merely be achieved once. **Shared assumptions:** Task horizon and maintenance predicate are meaningful. **Incompatibility:** Restoration equated with ending the obligation.

**Composition:** Keep the goal active after temporary restoration and select predictive or reactive upkeep. **New cost/failure:** Monitoring and false preventive action.

**Evidence:** `SOURCE_ESTABLISHED_MECHANISM_WITH_TRANSFER_LIMITS` [EAA-S051]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R010 — EAA-012 `CONSTRAINS` EAA-013, EAA-019.**

**Guard:** Parallel intentions or layers can interfere. **Shared assumptions:** Material conditions/effects/resources are summarised adequately. **Incompatibility:** Individually feasible actions assumed mutually compatible.

**Composition:** Protect shared conditions through applicable conflict checks or cheaper isolation/serialisation. **New cost/failure:** Conservative blocking and summary maintenance.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S006; EAA-S054; EAA-S046]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R011 — EAA-013 `REQUIRES` EAA-014, EAA-015.**

**Guard:** A persistent intention is retained. **Shared assumptions:** Relevance, progress and feasibility can be assessed adequately. **Incompatibility:** Commitment equated with never reconsidering or abandoning.

**Composition:** Reconsider and terminate under the adopted commitment strategy, with budget-sensitive checks. **New cost/failure:** Thrashing or obsolete pursuit from bad triggers.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S006; EAA-S009; EAA-S015; EAA-S052]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R012 — EAA-014 `ACTS_THROUGH` EAA-028.**

**Guard:** Further planning competes with timely execution. **Shared assumptions:** Reconsideration has measurable or estimable cost. **Incompatibility:** A fixed universal reflection frequency is optimal.

**Composition:** Schedule commitment review as a bounded computation decision. **New cost/failure:** Poor value estimates and missed action windows.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S006; EAA-S014; EAA-S015]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R013 — EAA-015 `COMMUNICATES_TO` EAA-036, EAA-038.**

**Guard:** A material delegated goal is abandoned or suspended. **Shared assumptions:** There is a legitimate recipient who needs to know non-fulfilment. **Incompatibility:** Silence or a sent message treated as accepted handback.

**Composition:** Report grounds and unresolved effects; distinguish notice from actual control transfer. **New cost/failure:** Attention burden and unresponsive recipient.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S020; EAA-S028; EAA-S051]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R014 — EAA-016 `ALTERNATIVE_TO` EAA-017, EAA-018.**

**Guard:** Direct observations permit an adequate policy. **Shared assumptions:** The task and resource comparison are shared. **Incompatibility:** More planning automatically means better architecture.

**Composition:** Select reaction instead of deliberation/library machinery where it meets the goal. **New cost/failure:** Limited foresight or omitted hidden state.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S005; EAA-S012; EAA-S046]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R015 — EAA-017 `ALTERNATIVE_TO` EAA-018.**

**Guard:** A structured multi-step task needs anticipation. **Shared assumptions:** Goal and effect semantics are adequate. **Incompatibility:** Generative search and library interpretation assumed identical.

**Composition:** Choose model-based search or applicable plan-library control according to variation, coverage and cost. **New cost/failure:** Library gaps versus search/model expense.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S009; EAA-S011; EAA-S045]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R016 — EAA-019 `ENABLES` EAA-016, EAA-017, EAA-018.**

**Guard:** Multiple decision time-scales have demonstrated value. **Shared assumptions:** Interfaces reconcile state, priorities and execution meaning. **Incompatibility:** Independently adequate modules assumed jointly adequate.

**Composition:** Combine selected branches with explicit sequencing/arbitration and feedback, not a compulsory ladder. **New cost/failure:** Coordination cost, races and timing mismatch.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S046; EAA-S022]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R017 — EAA-020 `CONSTRAINS` EAA-016, EAA-017, EAA-018, EAA-019, EAA-053, EAA-054.**

**Guard:** An architecture or new module is selected. **Shared assumptions:** Comparable tasks, constraints and material resources. **Incompatibility:** Architecture richness itself counts as success.

**Composition:** Retain only the additional freedom or machinery that earns its cost against an adequate baseline. **New cost/failure:** Underengineering rare cases or overfitting a benchmark.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S005; EAA-S035; EAA-S036; EAA-S046]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R018 — EAA-021 `ENABLES` EAA-017, EAA-018, EAA-053.**

**Guard:** Plans select executable skills or tools. **Shared assumptions:** Action identities and applicability map to real interfaces. **Incompatibility:** Fluent descriptions treated as executable capabilities.

**Composition:** Ground plan actions in a known capability vocabulary and context-sensitive affordances. **New cost/failure:** Skill maintenance and false feasibility estimates.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S011; EAA-S045; EAA-S049; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R019 — EAA-022 `REQUIRES` EAA-004, EAA-006, EAA-021.**

**Guard:** Dispatch can cause a consequential effect. **Shared assumptions:** Material scope and current conditions can be checked. **Incompatibility:** Plan-time approval or skill existence sufficient for all later action.

**Composition:** Check relevant permission, capability and state at the operative boundary. **New cost/failure:** False blocking, stale checks and check-to-use races.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S016; EAA-S019; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R020 — EAA-023 `PROVIDES_EVIDENCE_FOR` EAA-010, EAA-045.**

**Guard:** An action or task is claimed complete. **Shared assumptions:** The observation/return contract covers the desired effect. **Incompatibility:** Issuance or acknowledgement treated as actual fulfilment.

**Composition:** Effect evidence supports task-instance success and feeds evaluation, while uncovered policy criteria remain separate. **New cost/failure:** Observation cost or false completion from an incomplete oracle.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S022; EAA-S032; EAA-S033]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R021 — EAA-023 `FEEDBACK_TO` EAA-005, EAA-013, EAA-024.**

**Guard:** Execution returns or an effect is observed. **Shared assumptions:** The update reflects what the observation actually establishes. **Incompatibility:** Expected effect substituted for observed effect.

**Composition:** Update state/progress and select continuation, intention release or repair. **New cost/failure:** Misleading feedback can propagate into multiple components.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S016; EAA-S022; EAA-S031]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R022 — EAA-024 `REQUIRES` EAA-022, EAA-023, EAA-026, EAA-069.**

**Guard:** A failed or changed plan is repaired. **Shared assumptions:** Alternatives are bounded, executable and within the task. **Incompatibility:** Repair automatically authorises goal changes or unlimited retries.

**Composition:** Re-enter condition/effect checks under remaining resources and preserve goal/scope. **New cost/failure:** Repeated side effects and prolonged failure.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S016; EAA-S020; EAA-S031; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R023 — EAA-025 `CONSTRAINS` EAA-024, EAA-040.**

**Guard:** An effect may be irreversible or already occur without acknowledgement. **Shared assumptions:** Effect and interruption semantics are known sufficiently. **Incompatibility:** Retry/undo/stop always restores the pre-action state.

**Composition:** Restrict retries and interruption to what the actual action semantics justify; report irrecoverable effects. **New cost/failure:** Conservative delay and incomplete compensation.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S022; EAA-S043; EAA-S044]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R024 — EAA-026 `CONSTRAINS` EAA-008, EAA-014, EAA-024, EAA-027, EAA-028, EAA-037, EAA-054.**

**Guard:** Actions and deliberation share finite resources. **Shared assumptions:** Material costs and deadlines are included. **Incompatibility:** Reasoning, sensing, help or retries are free.

**Composition:** Use the operative envelope to bound cognition and external action alike. **New cost/failure:** Metering and premature stopping.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S013; EAA-S014; EAA-S019; EAA-S035]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R025 — EAA-027 `ENABLES` EAA-016, EAA-028.**

**Guard:** A deadline permits incremental improvement but requires a usable response. **Shared assumptions:** Intermediate answer/fallback is available and interruption is real. **Incompatibility:** Any algorithm labelled anytime is timely or safe to interrupt.

**Composition:** Improve while useful time remains and fall back to an adequate available action. **New cost/failure:** Lower-quality early decisions and scheduling overhead.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S014; EAA-S046]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R026 — EAA-029 `CONSTRAINS` EAA-030, EAA-032, EAA-054, EAA-070.**

**Guard:** A change is described as learning or self-revision. **Shared assumptions:** Persistence and behavioural effect of the change are identifiable. **Incompatibility:** Ordinary state update, text memory and utility self-change treated as one mechanism.

**Composition:** Apply the appropriate evaluation and authority boundary for the actual change type. **New cost/failure:** Tracking burden and missed indirect behavioural effects.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S027; EAA-S031; EAA-S053]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R027 — EAA-030 `ENABLES` EAA-031, EAA-054.**

**Guard:** Stored experience informs later decisions. **Shared assumptions:** Memory has source and evidential status, not only relevance. **Incompatibility:** Self-generated narrative treated as verified experience.

**Composition:** Retrieve and revise from warranted observations or qualified interpretations. **New cost/failure:** Stale/private/false memory can still contaminate decisions.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S028; EAA-S031; EAA-S044; EAA-S050]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R028 — EAA-031 `REQUIRES` EAA-026, EAA-043.**

**Guard:** A persistent memory store is justified. **Shared assumptions:** Retention has a relevant consumer and resource/privacy constraints. **Incompatibility:** Unlimited memory is inherently beneficial.

**Composition:** Select and retire stored material according to purpose, validity and costs. **New cost/failure:** Loss of rare useful evidence or excessive retention.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S031; EAA-S043; EAA-S044; EAA-S050]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R029 — EAA-032 `REQUIRES` EAA-029, EAA-035, EAA-045.**

**Guard:** A persistent learned component changes. **Shared assumptions:** Old/new task conditions and acceptable continuity are defined. **Incompatibility:** New task gain implies overall improvement.

**Composition:** Evaluate retained competence and changed behaviour against adequate oracles and transfer cases. **New cost/failure:** Regression testing and reduced plasticity.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S025; EAA-S026; EAA-S031]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R030 — EAA-033 `REQUIRES` EAA-004, EAA-034, EAA-049.**

**Guard:** Learning explores consequential actions. **Shared assumptions:** Protected constraints are defined independently of reward. **Incompatibility:** Eventual convergence or lower cost equals safe exploration.

**Composition:** Constrain or protect exploration and measure residual violations before transfer. **New cost/failure:** Reduced learning and simulator mismatch.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S024; EAA-S027; EAA-S038]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R031 — EAA-034 `CONSTRAINS` EAA-010, EAA-045, EAA-060.**

**Guard:** A proxy, score or reward supports a fulfilment claim. **Shared assumptions:** The intended outcome and measured proxy are distinguishable. **Incompatibility:** Optimisation success sufficient for every task obligation.

**Composition:** Use discriminating tests where metric success and intended fulfilment diverge; reject the universal sufficiency claim. **New cost/failure:** Incomplete objectives and adversarial test burden.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S025; EAA-S033]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R032 — EAA-035 `PROVIDES_EVIDENCE_FOR` EAA-055, EAA-066.**

**Guard:** Use changes model, environment or embodiment. **Shared assumptions:** The tested shift is material to the target claim. **Incompatibility:** Unchanged labels imply unchanged performance.

**Composition:** Targeted shifted-condition tests support only the corresponding transfer and continuity claim. **New cost/failure:** Coverage gaps and expensive target validation.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S025; EAA-S035; EAA-S036; EAA-S048]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R033 — EAA-036 `ENABLES` EAA-037, EAA-038, EAA-039.**

**Guard:** Coordination depends on another actor understanding or taking control. **Shared assumptions:** Message receipt and acceptance have meaningful semantics. **Incompatibility:** Sending a message guarantees agreement or action.

**Composition:** Exchange the task-relevant information and establish only the commitment actually acknowledged. **New cost/failure:** Communication delay and interpretation failure.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S020; EAA-S028; EAA-S047]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R034 — EAA-037 `CONSTRAINS` EAA-004, EAA-008, EAA-039.**

**Guard:** Initiative or clarification changes who decides. **Shared assumptions:** The task, information value and human readiness are known enough. **Incompatibility:** Silence confers authority or asking is always helpful.

**Composition:** Choose advice/ask/act according to consequence, scope and response feasibility. **New cost/failure:** Attention burden and missed opportunities.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S019; EAA-S020; EAA-S044]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R035 — EAA-038 `REQUIRES` EAA-036, EAA-039, EAA-040.**

**Guard:** Control is transferred. **Shared assumptions:** Recipient, readiness and actual operational control are established. **Incompatibility:** Nominal human presence is adequate oversight.

**Composition:** Connect request, response, context and in-flight action handling with a non-response path. **New cost/failure:** Handoff latency or abandoned control.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S020; EAA-S021; EAA-S023]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R036 — EAA-040 `CONSTRAINS` EAA-013, EAA-022, EAA-067.**

**Guard:** Task authority is withdrawn or action interrupted. **Shared assumptions:** The revocation reaches active execution and goal state. **Incompatibility:** Stopping a conversation stops all queued effects.

**Composition:** Invalidate future actions and reconsider commitments while accurately handling irreversible effects. **New cost/failure:** Partial states, cancellation races and residual effects.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S019; EAA-S022; EAA-S043]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R037 — EAA-041 `REFINES` EAA-040.**

**Guard:** The interrupted agent learns from action outcomes. **Shared assumptions:** Operational interruption exists and the learning theorem conditions hold. **Incompatibility:** A stop button alone supplies interruption-neutral learning.

**Composition:** Add the specific learning update/incentive condition without replacing physical interruption semantics. **New cost/failure:** Exploration assumptions and algorithm-specific implementation burden.

**Evidence:** `SOURCE_ESTABLISHED_FORMAL_RESULT_WITH_ASSUMPTIONS` [EAA-S024]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R038 — EAA-042 `ALTERNATIVE_TO` EAA-040, EAA-041.**

**Guard:** The concern is willingness to permit human intervention. **Shared assumptions:** The game and private information model are explicit. **Incompatibility:** Objective uncertainty guarantees all forms of deference.

**Composition:** Analyse the conditional incentive mechanism separately from enforced revocation and interruptibility-neutral learning. **New cost/failure:** Misestimated information and unjustified assurance.

**Evidence:** `FORMAL_ALTERNATIVES_NOT_ESTABLISHED_EQUIVALENT` [EAA-S040; EAA-S041; EAA-S024]. **Remaining obligation:** A unified practical guarantee is not supplied; the partially observable counterexample must remain visible.

**EAA-R039 — EAA-043 `CONSTRAINS` EAA-004, EAA-030, EAA-031, EAA-037, EAA-038, EAA-044.**

**Guard:** Agent action or information handling affects people. **Shared assumptions:** Participants, legitimate purposes and consequences can be identified. **Incompatibility:** Agent task score wholly determines acceptable means.

**Composition:** Keep privacy, meaningful control and affected-party interests operative in scope, memory and communication choices. **New cost/failure:** Normative conflict and attention/coordination cost.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S021; EAA-S043; EAA-S047]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R040 — EAA-044 `COMMUNICATES_TO` EAA-037, EAA-039.**

**Guard:** A person must decide, correct or take over. **Shared assumptions:** Information is faithful and useful for that recipient’s decision. **Incompatibility:** Long rationales or human likeness establish comprehension.

**Composition:** Provide action-relevant evidence, limits and options rather than a persuasive internal story. **New cost/failure:** False reassurance and information overload.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S043; EAA-S044; EAA-S047]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R041 — EAA-045 `CONSTRAINS` EAA-023, EAA-034, EAA-046, EAA-054.**

**Guard:** Outcome evidence is used to claim success, compare runs or revise behaviour. **Shared assumptions:** The oracle covers the actual claim, including relevant process constraints. **Incompatibility:** The same generated assertion can certify itself.

**Composition:** Use adequate tests/observations and expose omissions before feeding the result into learning or reporting. **New cost/failure:** Wrong oracles can couple failure across the system.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S031; EAA-S032; EAA-S033]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R042 — EAA-046 `PROVIDES_EVIDENCE_FOR` EAA-047, EAA-048, EAA-064.**

**Guard:** Reliability or comparative performance is claimed. **Shared assumptions:** Trial units, versions, repetitions and costs are explicit. **Incompatibility:** Best-of-many, all-of-many and single-run success are equivalent.

**Composition:** Make aggregation and dependence visible for comparison and reject unsupported deployment inference. **New cost/failure:** Replication expense and inaccessible historical model versions.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S033; EAA-S035; EAA-S036; EAA-S048]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R043 — EAA-047, EAA-048 `PROVIDES_EVIDENCE_FOR` EAA-020.**

**Guard:** Architecture choices need comparative justification. **Shared assumptions:** Task coverage, information and material costs are comparable. **Incompatibility:** Extra retries or human support mistaken for architectural benefit.

**Composition:** Use the cost/quality frontier and whole-task burden to select the adequate branch. **New cost/failure:** Benchmark overfitting and difficult cost valuation.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S035; EAA-S036; EAA-S019]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R044 — EAA-049 `ENABLES` EAA-035, EAA-045, EAA-050.**

**Guard:** Adverse conditions or new environments require evidence. **Shared assumptions:** Tests are contained and linked to actual failure hypotheses. **Incompatibility:** Sandbox success certifies uncontrolled deployment.

**Composition:** Exercise faults, shifts and assumptions without silently imposing costs on third parties. **New cost/failure:** Fidelity gaps and false confidence.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S022; EAA-S034; EAA-S038; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R045 — EAA-050 `PROVIDES_EVIDENCE_FOR` EAA-051.**

**Guard:** A formal claim depends on monitorable changing assumptions. **Shared assumptions:** Monitored conditions correspond to the proof’s environmental assumptions. **Incompatibility:** Detecting some deviations proves every environmental assumption.

**Composition:** Use observed violations to limit the claim and trigger an appropriate runtime response. **New cost/failure:** Nuisance alarms, blind spots and monitor-model mismatch.

**Evidence:** `SOURCE_ESTABLISHED_MECHANISM_WITH_TRANSFER_LIMITS` [EAA-S042]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R046 — EAA-051 `CONSTRAINS` EAA-007, EAA-018, EAA-027, EAA-041, EAA-042, EAA-050, EAA-070.**

**Guard:** A formal or model-relative property is claimed in practice. **Shared assumptions:** The model, implementation relation and environment are separately examined. **Incompatibility:** Proof strength is equivalent to field validity.

**Composition:** Keep guarantees conditional and identify unfulfilled abstraction or environmental obligations. **New cost/failure:** Verification and validation cost.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S009; EAA-S012; EAA-S014; EAA-S024; EAA-S027; EAA-S041; EAA-S042; EAA-S053]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R047 — EAA-052 `CONSTRAINS` EAA-005, EAA-021, EAA-022, EAA-053, EAA-054.**

**Guard:** An LLM consumes externally controlled language and can act. **Shared assumptions:** Source content and task authority can be distinguished. **Incompatibility:** Persuasive tool text can legitimise new instructions.

**Composition:** Treat text as untrusted input and enforce consequential capability/scope boundaries independent of its claimed authority. **New cost/failure:** False blocking and residual attack surface.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S034]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R048 — EAA-053 `REQUIRES` EAA-021, EAA-023, EAA-026, EAA-045, EAA-052.**

**Guard:** Language-model decisions choose real tool actions. **Shared assumptions:** Capabilities, feedback, budgets, oracle and trust boundaries are meaningful. **Incompatibility:** A reasoning trace itself supplies these controls.

**Composition:** Interleave actual action/observation under grounded constraints; select simpler workflows when adequate. **New cost/failure:** Long trajectories multiply cost and exposure to bad observations.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S030; EAA-S031; EAA-S034; EAA-S035]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R049 — EAA-054 `REQUIRES` EAA-023, EAA-026, EAA-030, EAA-045.**

**Guard:** Reflection is used for another attempt. **Shared assumptions:** Actual feedback is adequate and the next attempt can test the proposed lesson. **Incompatibility:** Generated self-critique guarantees improvement.

**Composition:** Bound reflection by task evidence, memory validity and resources. **New cost/failure:** Reinforcing wrong feedback and costly retries.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S031; EAA-S035]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R050 — EAA-054, EAA-028 `SUPERSEDES` EAA-061.**

**Guard:** Continuous reflection is proposed without a benefit discriminator. **Shared assumptions:** Feedback validity and marginal reasoning value are necessary. **Incompatibility:** Always-on reflection is an unconditional mature property.

**Composition:** Replace the universal ritual with bounded evidence-anchored review and a stopping rule. **New cost/failure:** Under-reflection remains possible if value is underestimated.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S014; EAA-S031; EAA-S035]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R051 — EAA-055 `FEEDBACK_TO` EAA-035, EAA-045, EAA-050, EAA-067.**

**Guard:** A material configuration changes. **Shared assumptions:** Previous claims can be linked to affected semantics. **Incompatibility:** A stable product name preserves all prior evidence.

**Composition:** Reassess affected assumptions, outcomes and compositional coherence without unnecessarily repeating unaffected tests. **New cost/failure:** Impact-analysis gaps and regression cost.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S035; EAA-S036; EAA-S042]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R052 — EAA-003, EAA-045 `CONSTRAINS` EAA-056, EAA-063, EAA-064.**

**Guard:** Anthropomorphic, architectural or benchmark claims exceed what was established. **Shared assumptions:** Predicates and evidence targets are kept distinct. **Incompatibility:** Labels, believability or scores stand in for stronger guarantees.

**Composition:** Limit the claim and preserve negative/ceremonial candidates rather than adopting them as controls. **New cost/failure:** Loss of persuasive simplicity, but no added operative capability is claimed.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S010; EAA-S043; EAA-S050; EAA-S035]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R053 — EAA-020, EAA-004, EAA-014 `CONSTRAINS` EAA-057, EAA-058, EAA-059.**

**Guard:** A universal autonomy or architecture rule is proposed. **Shared assumptions:** Task needs and conditional evidence govern selection. **Incompatibility:** Maximal freedom or one representational stance always wins.

**Composition:** Reject the universal claims while retaining appropriate conditional branches. **New cost/failure:** Selection effort and residual task uncertainty.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S005; EAA-S012; EAA-S015; EAA-S019; EAA-S036; EAA-S046]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R054 — EAA-023 `SUPERSEDES` EAA-065.**

**Guard:** The candidate concerns task-instance completion evidence. **Shared assumptions:** Both entries denote the same effect-establishment mechanism in this scope. **Incompatibility:** One discovered phrase must create one new control.

**Composition:** Canonicalise the operative mechanism at EAA-023; retain EAA-065 in the denominator as a duplicate. **New cost/failure:** No operative cost; ignoring the relation would duplicate checks and counts.

**Evidence:** `ANALYTICAL_DUPLICATE_ADJUDICATION` [EAA-S022; EAA-S032; EAA-S033]. **Remaining obligation:** Population-level oracle validation is distinct and remains EAA-045.

**EAA-R055 — EAA-066 `REQUIRES` EAA-021, EAA-022, EAA-023, EAA-025, EAA-027, EAA-039, EAA-049.**

**Guard:** Moving a mechanism to physical or materially different environments. **Shared assumptions:** Only genuinely preserved assumptions support reuse. **Incompatibility:** Symbolic/tool feasibility equivalent to physical effect or reversibility.

**Composition:** Re-establish changed sensing, timing, execution and human-response conditions in protected tests. **New cost/failure:** Hardware/target validation burden and residual unknowns.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S022; EAA-S045; EAA-S049; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R056 — EAA-067 `REQUIRES` EAA-004, EAA-006, EAA-010, EAA-013, EAA-019, EAA-022, EAA-040.**

**Guard:** Multiple asynchronous components contribute to action justification. **Shared assumptions:** Relevant dependencies can be made compatible at the action boundary. **Incompatibility:** Individually valid facts necessarily form a jointly valid basis.

**Composition:** Tie the current-enough state, goal and authority to the same action decision; refresh or invalidate after material changes. **New cost/failure:** Serialisation, cancellation and liveness cost.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S022; EAA-S016; EAA-S019; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R057 — EAA-068 `REQUIRES` EAA-005, EAA-023, EAA-024, EAA-034, EAA-045, EAA-050.**

**Guard:** Failure prompts a revision proposal. **Shared assumptions:** Evidence can discriminate at least some candidate causes. **Incompatibility:** Every failure is an action-selection error repairable by more reflection.

**Composition:** Diagnose at the level justified by evidence, then test a bounded relevant change or hand back. **New cost/failure:** Diagnosis cost and false attribution.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S022; EAA-S025; EAA-S031; EAA-S042]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R058 — EAA-069 `CONSTRAINS` EAA-004, EAA-010, EAA-013, EAA-024, EAA-036.**

**Guard:** A repair changes means, entities or goal conditions. **Shared assumptions:** Task invariants and authorised alternatives are identifiable. **Incompatibility:** Making a plan executable can redefine the requested outcome.

**Composition:** Allow repairs within scope; communicate genuine task changes for the appropriate decision. **New cost/failure:** Overconstraint and clarification delay.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S006; EAA-S019; EAA-S033; EAA-S039]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

**EAA-R059 — EAA-070 `REFINES` EAA-062.**

**Guard:** Explicit formal self-modification is the object of study. **Shared assumptions:** The predecessor utility and future-policy consequences can be modelled. **Incompatibility:** One narrow value-preservation theorem resolves general safe self-revision.

**Composition:** Preserve the narrow theorem while marking practical/general assurance unresolved. **New cost/failure:** Ideal-model assumptions and possible utility rigidity.

**Evidence:** `SOURCE_ESTABLISHED_FORMAL_RESULT_WITH_ASSUMPTIONS` [EAA-S053]. **Remaining obligation:** Acceptability of initial utility, approximate prediction and corrigibility remain outside the guarantee.

**EAA-R060 — EAA-070 `CONFLICTS_WITH` EAA-032, EAA-042, EAA-043.**

**Guard:** The preserved initial criterion is mistaken or legitimate values/authority should change. **Shared assumptions:** Continuity and responsiveness can refer to different acceptable targets. **Incompatibility:** Utility stability inherently entails safe corrigibility.

**Composition:** Require a justified criterion and explicit authority for changing it; no unsupported unification is imposed. **New cost/failure:** Rigidity, goal drift or loss of safe learning.

**Evidence:** `ANALYTICAL_TENSION_GROUNDED_IN_FORMAL_LIMITS` [EAA-S025; EAA-S026; EAA-S041; EAA-S043; EAA-S053]. **Remaining obligation:** No general resolution for open-ended self-revision is established in this corpus.

**EAA-R061 — EAA-016, EAA-019 `SHARES_ANCESTRY_WITH` EAA-053.**

**Guard:** Comparing perception/action feedback across generations. **Shared assumptions:** All concern world-coupled action, but mechanisms differ. **Incompatibility:** Similar loop vocabulary proves direct historical derivation or BDI conformance.

**Composition:** Record common AI agent/control ancestry; use source-specific citations for any stronger transmission claim. **New cost/failure:** False genealogy if analogy is inflated.

**Evidence:** `HISTORICAL_COMPARISON_NOT_DIRECT_INFLUENCE` [EAA-S001; EAA-S004; EAA-S016; EAA-S030]. **Remaining obligation:** No direct influence edge from each early architecture to ReAct is claimed.

**EAA-R062 — EAA-051 `CONSTRAINS` EAA-042, EAA-070.**

**Guard:** A formal result conflicts with desired practical behaviour. **Shared assumptions:** The model and deployment claim are separately assessed. **Incompatibility:** A counterexample outside assumptions disproves the theorem, or a proof validates those assumptions.

**Composition:** Adjudicate theorem validity and practical applicability separately; preserve contested and unresolved conclusions. **New cost/failure:** Analytical complexity and limited external validation.

**Evidence:** `ANALYTICAL_COMPOSITION_SUPPORTED_BY_SOURCES` [EAA-S041; EAA-S053]. **Remaining obligation:** No general effectiveness guarantee; application must establish the stated guard and assumptions.

### Smallest coherent form and triggers for richer forms

These are conditional coherent configurations, not a demand to instantiate all of them together. A listed required criterion may already be supplied by a trusted operation contract. It need not appear as a separate module.

**EAA-A01 — Minimal bounded situated controller.** A directly observed state supports an adequate action policy; task and authority are bounded; existing executor contracts can establish effects.

**Core property links:** EAA-001, EAA-004, EAA-005, EAA-010, EAA-016, EAA-021, EAA-023, EAA-026. **Conditional additions:** EAA-006, EAA-009, EAA-022, EAA-025, EAA-040, EAA-045.

**Omit:** separate belief distribution when current observations suffice; search or BDI when a direct policy suffices; persistent memory and learning without a relevant future use; runtime metareasoner where a fixed budget is adequate. **Retire/replace:** Retire additional controls when their failure class or consumer disappears; maintain accurate scope/effect claims.

**Limit:** Fails when hidden state, horizon, task variation or consequences exceed the assumed simple controller.

**EAA-A02 — Stateful deliberative or BDI agent.** Look-ahead, partial observability or recurring context-sensitive plans earn their model/library cost.

**Core property links:** EAA-001, EAA-004, EAA-005, EAA-007, EAA-010, EAA-013, EAA-021, EAA-022, EAA-023, EAA-026. **Conditional additions:** EAA-008, EAA-011, EAA-012, EAA-014, EAA-015, EAA-024, EAA-027, EAA-028. **Alternative branches:** [['EAA-017'], ['EAA-018']].

**Omit:** continuous reflection; full state model without demonstrated need; both search and BDI unless their composition is justified. **Retire/replace:** Replace with a direct or fixed policy where it is demonstrably adequate and cheaper.

**Limit:** Model/library errors, deliberation expense and stale-state risks require monitored execution.

**EAA-A03 — Hybrid embodied controller.** Fast control and slower sequencing/planning both have demonstrated value, with feasible timing and coherent interfaces.

**Core property links:** EAA-004, EAA-005, EAA-019, EAA-021, EAA-022, EAA-023, EAA-026, EAA-066, EAA-067. **Conditional additions:** EAA-007, EAA-012, EAA-016, EAA-017, EAA-018, EAA-024, EAA-025, EAA-027, EAA-039, EAA-040, EAA-049, EAA-050.

**Omit:** unneeded tiers; central modelling of directly available environmental distinctions. **Retire/replace:** Remove a layer when its unique function is no longer needed and the simpler interface meets the task.

**Limit:** Not a universal robot architecture; continuous/discrete timing and physical effects need local validation.

**EAA-A04 — Mixed-initiative adaptive assistant.** Humans have useful missing information or authority; response probability/time and control semantics are meaningful.

**Core property links:** EAA-004, EAA-010, EAA-023, EAA-026, EAA-036, EAA-037, EAA-038, EAA-039, EAA-043. **Conditional additions:** EAA-029, EAA-030, EAA-031, EAA-032, EAA-035, EAA-040, EAA-044.

**Omit:** learning where shared stable rules suffice; repeated confirmations with no changed decision; handoff that cannot be received in time. **Retire/replace:** Return to direct manipulation or fixed delegation where adaptive assistance adds no net value.

**Limit:** No human-rescue assumption; privacy, user control and external-party costs remain material.

**EAA-A05 — Bounded language-model tool user.** Language-conditioned task variation justifies the model; dynamic action selection is retained only if it earns its cost.

**Core property links:** EAA-004, EAA-005, EAA-010, EAA-021, EAA-022, EAA-023, EAA-026, EAA-045, EAA-052, EAA-055. **Conditional additions:** EAA-007, EAA-024, EAA-025, EAA-030, EAA-031, EAA-035, EAA-037, EAA-038, EAA-040, EAA-046, EAA-047, EAA-048, EAA-054, EAA-067, EAA-069. **Alternative branches:** [['EAA-053'], ['fixed workflow baseline using existing tools']].

**Omit:** reflective memory without reliable feedback; BDI claims based only on prompting; unbounded autonomous retries. **Retire/replace:** Use a fixed workflow or direct tool where it supplies adequate outcomes more cheaply and predictably.

**Limit:** Tool injection, long-horizon instability, oracle gaps and version changes remain live concerns.

**EAA-A06 — Protected learning branch.** A real need for persistent improvement exists and exploration/change can be bounded and evaluated.

**Core property links:** EAA-004, EAA-029, EAA-033, EAA-034, EAA-035, EAA-045, EAA-049. **Conditional additions:** EAA-024, EAA-026, EAA-030, EAA-031, EAA-032, EAA-041, EAA-070.

**Omit:** live unsafe exploration for its own sake; automatic utility revision; open-ended self-assurance claim. **Retire/replace:** Freeze or replace learned behaviour when improvement does not outweigh regression, cost or safety uncertainty.

**Limit:** EAA-062 remains unresolved; a formal predecessor-utility condition does not establish acceptable initial values or general corrigibility.

### Communication, operation and consequence

The task interface exchanges desired conditions, constraints, permitted means, changes and revocation. The sensor/tool interface exchanges observations, commands, acknowledgements and effect evidence. The assistance interface exchanges decision requests, state needed for takeover, responses and accepted control. The evaluation/revision interface exchanges outcome evidence, adverse cases, proposed changes and the criterion under which they are judged. None is satisfied merely by generating a message that says the exchange happened.

Actions change external objects or relationships through actual capabilities: a robot moves, a service updates a record, a message reaches a recipient, or a participant accepts a task. Different evidence establishes each consequence. Where the relevant effect is unobservable or a participant’s acceptance is unknown, the system preserves that uncertainty instead of declaring success. External accountability remains a legitimate constraint even when the internal optimisation would prefer a different action.

### Revision boundaries

Execution-state changes and means-level repairs stay within the current task. Persistent memories, policies and skills have their own evaluation, retention and exploration constraints. Goal or authority changes require an appropriate task/authority decision rather than a better score. Formal utility self-modification is an additional, assumption-sensitive case; it neither follows from ordinary learning nor confers general authority to self-revise. EAA-062 stays unresolved, EAA-070 retains its narrow result, and the conflict with justified value revision is not hidden.

### Discriminating case examination

The following cases exercise the relational account by tracing the decision it permits and the failure it would expose. Invented cases are explicitly analytical; they are not executed experiments, benchmark scores or empirical validation of this composed system. Published cases are used as external probes rather than rebranded as new experiments.

**EAA-TEST01 — Successful answer without successful action (`ANALYTICAL_DISCRIMINATING_CASE`).**

**Case:** A booking assistant gives the correct confirmation wording, but no reservation exists in the external system.

**Derived judgement:** EAA-023 and EAA-045 reject established booking success; wording alone is not effect evidence.

**Failure of the proposed composition would be:** The system marks completion solely from generated wording or checks only that the message contains the right string.

**Property links:** EAA-010, EAA-023, EAA-045. **Published anchors:** [EAA-S032; EAA-S033].

**EAA-TEST02 — Correct plan on stale state (`ANALYTICAL_DISCRIMINATING_CASE`).**

**Case:** A route is valid when planned; the destination becomes unavailable while the planner computes.

**Derived judgement:** Refresh/check the relevant condition; revise means within scope or ask about a genuine destination change.

**Failure of the proposed composition would be:** The old plan remains executable solely because its earlier proof was correct.

**Property links:** EAA-006, EAA-022, EAA-024, EAA-067, EAA-069. **Published anchors:** [EAA-S015; EAA-S022; EAA-S039].

**EAA-TEST03 — Replanning consumes the action window (`ANALYTICAL_DISCRIMINATING_CASE`).**

**Case:** A controller can act adequately now, but repeatedly computes a marginally better plan until the deadline expires.

**Derived judgement:** Use EAA-026–028 to act or fall back; more reasoning is not success.

**Failure of the proposed composition would be:** Only plan quality is measured and missed deadlines are ignored.

**Property links:** EAA-014, EAA-020, EAA-026, EAA-027, EAA-028. **Published anchors:** [EAA-S014; EAA-S015].

**EAA-TEST04 — Persistent obsolete goal (`ANALYTICAL_DISCRIMINATING_CASE`).**

**Case:** The user withdraws a task while a long-running agent continues to execute queued steps.

**Derived judgement:** Revocation affects both future dispatch and active commitment; disclose any already irreversible effects.

**Failure of the proposed composition would be:** The conversation acknowledges the withdrawal but execution continues as before.

**Property links:** EAA-004, EAA-013, EAA-015, EAA-025, EAA-040, EAA-067. **Published anchors:** [EAA-S019; EAA-S043; EAA-S052].

**EAA-TEST05 — Apparently successful action with unobserved failure (`ANALYTICAL_DISCRIMINATING_CASE`).**

**Case:** A tool acknowledges receipt, but the intended external update fails; alternatively the effect succeeds and the acknowledgement is lost.

**Derived judgement:** Keep outcomes unresolved until adequate evidence; do not blindly retry an irreversible action.

**Failure of the proposed composition would be:** Receipt is equated with effect, or absence of acknowledgement with absence of effect.

**Property links:** EAA-023, EAA-024, EAA-025, EAA-045. **Published anchors:** [EAA-S022; EAA-S033].

**EAA-TEST06 — Simple reaction outperforms a sophisticated planner (`ANALYTICAL_DISCRIMINATING_CASE`).**

**Case:** A stable local task has sufficient visible cues and tight response time; a planner adds latency without useful look-ahead.

**Derived judgement:** Select the reactive or fixed branch, omitting unneeded modules and retaining only adequate execution evidence.

**Failure of the proposed composition would be:** The richer architecture is retained solely because it has more modules or autonomy.

**Property links:** EAA-016, EAA-020, EAA-027, EAA-047, EAA-058. **Published anchors:** [EAA-S005; EAA-S015; EAA-S035; EAA-S046].

**EAA-TEST07 — Hidden state defeats pure reaction (`ANALYTICAL_CHANGED_ASSUMPTION_CASE`).**

**Case:** Identical current observations follow two different histories requiring different actions.

**Derived judgement:** Reject the universal reactive claim and add adequate history/state or information gathering.

**Failure of the proposed composition would be:** The reactive architecture remains privileged regardless of observed failure under aliasing.

**Property links:** EAA-005, EAA-007, EAA-008, EAA-017, EAA-059. **Published anchors:** [EAA-S012].

**EAA-TEST08 — A helpful repair changes the task (`ANALYTICAL_CONFLICT_CASE`).**

**Case:** The requested destination is unavailable; the model substitutes another destination and reports success.

**Derived judgement:** Block the task-changing substitution unless it is an established authorised equivalent; negotiate a new goal separately.

**Failure of the proposed composition would be:** Feasibility or a better metric score is allowed to redefine the request.

**Property links:** EAA-004, EAA-010, EAA-024, EAA-034, EAA-069. **Published anchors:** [EAA-S033; EAA-S039].

**EAA-TEST09 — Wrong self-test becomes memory (`ANALYTICAL_FAILED_OBSERVATION_CASE`).**

**Case:** A generated test mistakenly passes a bad action, and reflection records a confident lesson from it.

**Derived judgement:** EAA-030/045/054 preserve evaluator fallibility and test the revision against adequate external evidence.

**Failure of the proposed composition would be:** The agent treats its own reflection as independent evidence for the original success.

**Property links:** EAA-030, EAA-034, EAA-045, EAA-054, EAA-068. **Published anchors:** [EAA-S031].

**EAA-TEST10 — Atomic harmless fixed operation (`ANALYTICAL_NON_TRIGGER_CASE`).**

**Case:** A fixed operation has adequate typed inputs, established authority and a trustworthy atomic effect-return contract.

**Derived judgement:** Do not add a second verifier, persistent memory, planner or reflective loop without a new failure class.

**Failure of the proposed composition would be:** Every ledger entry is mechanically translated into a new module or owner.

**Property links:** EAA-020, EAA-023, EAA-025, EAA-031, EAA-054, EAA-065. **Published anchors:** [EAA-S035; EAA-S036; EAA-S046].

**EAA-TEST11 — Electric Elves unanswered control transfer (`PUBLISHED_FAILURE_USED_AS_COMPOSITION_PROBE`).**

**Case:** The reported assistant could wait indefinitely or make inappropriate decisions after a fixed timeout.

**Derived judgement:** Non-response and decision consequences must be part of control transfer; merely asking a human is insufficient.

**Failure of the proposed composition would be:** The composed model has no operational branch after an unanswered request.

**Property links:** EAA-036, EAA-038, EAA-039. **Published anchors:** [EAA-S020; EAA-S021].

**EAA-TEST12 — DS1 asynchronous execution race (`PUBLISHED_FAILURE_USED_AS_COMPOSITION_PROBE`).**

**Case:** A race in an unprotected critical section stopped the first experiment despite extensive testing; later remaining objectives were completed by a separate run.

**Derived judgement:** Distinguish local component correctness, integration evidence, observed mission progress and unsent patch status.

**Failure of the proposed composition would be:** The architecture is described as failure-free or the later success silently erases the first interruption.

**Property links:** EAA-019, EAA-023, EAA-049, EAA-050, EAA-051, EAA-067. **Published anchors:** [EAA-S022].

**EAA-TEST13 — Tool result impersonates the delegator (`ANALYTICAL_ADVERSARIAL_INPUT_CASE`).**

**Case:** A retrieved document tells the model to disregard the original task and send data elsewhere.

**Derived judgement:** Treat the text as untrusted observation; do not let it expand authority or establish a new legitimate goal.

**Failure of the proposed composition would be:** A convincing claim of authority inside retrieved data is accepted as actual authorisation.

**Property links:** EAA-004, EAA-005, EAA-043, EAA-052, EAA-053. **Published anchors:** [EAA-S034].

**EAA-TEST14 — A perfectly preserved wrong objective (`ANALYTICAL_SELF_REVISION_BOUNDARY_CASE`).**

**Case:** A formal self-modifying agent preserves its initial utility, but that utility omits a legitimate user constraint.

**Derived judgement:** Count utility preservation only as the narrow theorem property; it does not establish acceptable task fulfilment or corrigibility.

**Failure of the proposed composition would be:** Stability of the utility is called general safety or authorises the agent to ignore legitimate correction.

**Property links:** EAA-034, EAA-042, EAA-062, EAA-070. **Published anchors:** [EAA-S025; EAA-S041; EAA-S053].

The favourable cases support a small system that uses trustworthy existing effect contracts; the non-trigger case explicitly omits reflection, persistent memory and duplicate verification. Changed assumptions can instead require added state or handoff. Conflict cases can end in refusal or negotiated goal change. Failed-observation cases may end unresolved. This variety is intentional: a composition that always prescribes more autonomy or always returns a success verdict would fail the analysis.

## EVOLVED_AUTONOMOUS_AGENTS_HYBRIDISATION_AND_EXTERNAL_RELATIONS

The tradition has real imports and intersections. Resource-bounded decision theory contributes a way to judge computation; partial-observation decision processes contribute formal state uncertainty; control and robotics contribute situated action; human factors and HCI contribute readiness, attention and meaningful user control; learning contributes policy/model adaptation; formal methods contribute model-relative assurance and assumption monitoring. These are not all native inventions of one agent school, nor merely similarities in vocabulary. The genealogy labels the documentary strength of each asserted relationship.

The Multi-Agent Systems boundary is especially important for message acceptance, joint activity and control transfer. This lane studies their effect on one situated agent but does not supply a complete collective or strategic theory. The AOSE boundary concerns the relation between agent abstractions and a development method: an interpreter is not a lifecycle methodology, and an architecture is not evidence that a method has been followed. Later reconciliation should test equivalence, complementarity, shared mechanisms, level mismatch and incompatible assumptions rather than importing unread sibling conclusions.

Language-model agents are a contemporary translation with distinct data/instruction and model-version issues. A reason–act loop shares the broad environment-coupled problem without necessarily descending directly from every old control architecture. A prompt using belief/intention language is neither a proof of BDI conformance nor evidence of false personhood. Software-to-physical transfer introduces new sensing, actuation, timing and irreversibility obligations. SIBLING_CORPORA_NOT_CONSULTED. CROSS_TRIFECTA_SYNTHESIS_NOT_PERFORMED.

## EVOLVED_AUTONOMOUS_AGENTS_STRONGEST_SURVIVING_PROPERTIES

The strongest core is a set of justified distinctions with operative consumers, not a maximal machinery prescription. The 13 strongly retained candidates are:

**EAA-001 — Explicit agent–environment boundary.** Declare the entity, environmental variables it can observe or affect, objective attribution, persistence and the operative definition of agency. Keep interface boundaries distinct from metaphysical claims. **Boundary:** For a pure function, describe input/output computation without forcing an agent label. A simple controller may satisfy a minimal situated definition. [EAA-S001; EAA-S002; EAA-S003]

**EAA-003 — Computational grounding of mental-state vocabulary.** Link each engineering use of belief, desire, intention or commitment to a representation, transition, consumer and observable behaviour; distinguish an explanatory stance from executable semantics. **Boundary:** Use ordinary state, task and action names when intentional vocabulary adds no predictive or engineering value. [EAA-S009; EAA-S010; EAA-S028]

**EAA-004 — Capability is not delegated permission.** Keep the means the system can execute separate from what the delegator has authorised; make consequential scope boundaries usable at action selection and dispatch. **Boundary:** No additional permission mechanism is needed for an already constrained, harmless action entirely within the declared task; a fixed capability sandbox may suffice. [EAA-S019; EAA-S043; EAA-S044]

**EAA-005 — Observation, stored belief and world state remain distinct.** Retain the relevant observation source and interpretation; update a state estimate without equating observation, inference and reality. Gather discriminating evidence when the distinction changes action. **Boundary:** Use a directly validated signal without a separate belief database when ambiguity cannot affect the decision. [EAA-S012; EAA-S021; EAA-S028]

**EAA-010 — Usable goal and success semantics.** Specify the relevant desired condition, scope, constraints and completion evidence; distinguish preferences from obligations and terminal achievement from continued maintenance. **Boundary:** A simple visible condition can be sufficient; do not require a formal utility function for an unambiguous bounded task. [EAA-S006; EAA-S011; EAA-S032; EAA-S033]

**EAA-020 — Smallest adequate architecture and credible simpler baseline.** Compare candidate configurations with a credible cheaper policy or fixed workflow under comparable tasks, resources and constraints; retain only complexity that earns its role. **Boundary:** Keep an existing adequate simpler mechanism; do not introduce an agent merely to satisfy a label. [EAA-S005; EAA-S046; EAA-S035; EAA-S036]

**EAA-023 — Distinguish issuance, acknowledgement and established effect.** Interpret acknowledgement according to its actual semantics; observe the task-relevant effect or retain uncertainty when it cannot be established, and use that result in subsequent action and reporting. **Boundary:** A trustworthy atomic operation with a sufficient return contract may establish the effect directly; do not require redundant observation. [EAA-S016; EAA-S022; EAA-S032; EAA-S033]

**EAA-026 — Explicit time and resource envelope.** Include deliberation, sensing, retries and coordination in the operative resource envelope; let remaining resources constrain action and continuation decisions. **Boundary:** A simple fixed bound suffices for predictable bounded tasks; no optimiser is required merely to enforce a cap. [EAA-S013; EAA-S014; EAA-S035]

**EAA-029 — Separate learning from execution-state updates.** Identify whether a transition updates current execution state, persistent experience, a model, a policy, a skill or the mechanism/criterion for future changes. **Boundary:** An ordinary task-state update needs no learning machinery or self-modification claim. [EAA-S027; EAA-S031; EAA-S053]

**EAA-034 — Intended objective is not the measured proxy.** Distinguish intended task conditions and constraints from reward, heuristic and benchmark proxies; seek discriminating cases where proxy success and intended fulfilment diverge. **Boundary:** A direct, adequate task predicate may need no separate proxy analysis; document why it covers what matters. [EAA-S025; EAA-S033]

**EAA-045 — Adequate independent outcome and policy oracle.** Choose observations and tests adequate to the claimed outcome and protected process constraints; separate generated assertions from evaluation evidence, using independent checks where needed. **Boundary:** A trustworthy direct return contract or simple external predicate may suffice; a separate evaluator model is not inherently better. [EAA-S032; EAA-S033; EAA-S031]

**EAA-051 — Bound formal claims to model and implementation obligations.** State the model, property and assumptions; separately establish the implementation relation and relevant environmental adequacy, including approximation and concurrency gaps. **Boundary:** For a modest empirical claim, report the evidence without pretending a formal theorem is needed; direct testing can be adequate within its scope. [EAA-S009; EAA-S012; EAA-S024; EAA-S027; EAA-S042; EAA-S053]

**EAA-066 — Software–physical translation needs new obligations.** Identify which source assumptions survive translation and obtain new evidence for altered sensors, actuators, delays, failure costs and external participants. **Boundary:** Reuse unchanged logical components where their assumptions genuinely hold; do not recreate evidence for irrelevant differences. [EAA-S045; EAA-S022; EAA-S049; EAA-S039]

Their strength is not a measured universal effect size. It is the resilience of their conditional engineering role under the examined criticisms: the system must not confuse a definition with capability, a capability with authority, a belief with the world, a goal with its score, a command with its effect or a proof with its satisfied real-world assumptions. Their concrete implementation remains subject to cost, task and consequence.

## EVOLVED_AUTONOMOUS_AGENTS_CONTEXT_SPECIFIC_PROPERTIES

Architecture selection, belief-space planning, maintenance prediction, concurrent-goal analysis, metareasoning, persistent memory, continual learning, assistance, reflection and formal interruptibility are not universal obligations. They are useful when their particular trigger holds and a cheaper adequate path does not dominate. Strong theory can coexist with weak deployment evidence; field experience can expose real failures without identifying a universal response.

**EAA-007 — `ASSUMPTION_SENSITIVE`.** Trigger: Partial observability, uncertain transitions or delayed effects make an observation-only policy inadequate. Alternative: A reactive mapping is sufficient when observations already determine an adequate action; approximate state may dominate exact belief planning. Limit: Markov, observability and approximation assumptions must match the chosen model; a normalised belief is not external validation.

**EAA-008 — `CONTEXT_DEPENDENT`.** Trigger: An unresolved observation can change which feasible authorised action is preferable. Alternative: Skip the query when all plausible answers support the same action, or when a safe adequate action costs less. Limit: Information value is relative to the real decision and its deadline, not maximal knowledge.

**EAA-009 — `CONTEXT_DEPENDENT`.** Trigger: Unresolved consequential uncertainty, unavailable capability or failed safety/goal conditions. Alternative: Proceed without abstention machinery when a verified harmless action dominates waiting. Limit: There must be a feasible holding, shutdown or assistance path; some environments impose unavoidable action.

**EAA-012 — `CONTEXT_DEPENDENT`.** Trigger: Parallel goals or plans share mutable conditions, resources or deadlines. Alternative: No conflict machinery is necessary for a single isolated goal or demonstrably independent actions; serialisation can be adequate if affordable. Limit: Known plan hierarchies and reliable effect summaries delimit the original method; unknown tools require additional evidence.

**EAA-014 — `CONTEXT_DEPENDENT`.** Trigger: Changing options or state during a persistent plan. Alternative: Keep the current plan when new information cannot change its adequacy; use a fixed schedule only where justified by the setting. Limit: Value-of-reconsideration estimates can themselves be expensive and uncertain.

**EAA-016 — `CONTEXT_DEPENDENT`.** Trigger: Tight response deadlines, adequate local observability and behaviour-level objectives. Alternative: A fixed control rule can be the complete solution; add state or planning only for demonstrated aliasing, conflict or horizon needs. Limit: Behaviour adequacy is scoped to environment and goals, not a universal representation-free guarantee.

**EAA-017 — `CONTEXT_DEPENDENT`.** Trigger: Non-local goals, dependencies or contingencies that a cheap direct policy cannot adequately handle. Alternative: Use a validated fixed plan, policy or reactive response when search adds no useful discrimination. Limit: Guarantees are relative to model adequacy and search approximation.

**EAA-018 — `CONTEXT_DEPENDENT`.** Trigger: Recurrent structured tasks with usable plan recipes and persistent goals. Alternative: A simpler task state machine or direct workflow can suffice when intention filtering and alternative plans add no value. Limit: Plan-library coverage and event semantics matter; BDI labels do not identify one universal architecture.

**EAA-019 — `CONTEXT_DEPENDENT`.** Trigger: Combining reactive control with sequencing, deliberation or learning components. Alternative: Omit an unneeded layer; one or two tiers may satisfy the task and avoid integration costs. Limit: Continuous/discrete assumptions, execution rates and atomicity must actually fit the implementation.

**EAA-027 — `CONTEXT_DEPENDENT`.** Trigger: Hard or soft action deadlines and variable computation time. Alternative: A fast fixed policy can dominate an anytime solver; a batch answer is fine when no action deadline exists. Limit: Worst-case execution time and safe interruption may need separate evidence; simulated bounded optimality is not real-time certification.

**EAA-028 — `CONTEXT_DEPENDENT`.** Trigger: Alternative reasoning procedures, variable difficulty or changing action windows. Alternative: A fixed cheap policy or simple stopping rule suffices where estimating the value of computation would cost more than it saves. Limit: Expected decision improvement is uncertain and must not be mistaken for guaranteed benefit.

**EAA-031 — `CONTEXT_DEPENDENT`.** Trigger: Persistent stores whose size, staleness or sensitive content affects decisions. Alternative: No persistent store or a short task-local buffer can be sufficient; deletion is appropriate when no legitimate future consumer remains. Limit: Believability improvements in simulated characters do not establish reliable real-world episodic memory.

**EAA-032 — `CONTEXT_DEPENDENT`.** Trigger: Persistent policy/model/skill updates across changing tasks or environments. Alternative: Keep a fixed adequate policy when adaptation offers no demonstrated value; independent task modules may avoid unnecessary shared updates. Limit: The relevant continuity target must be justified; not all old behaviour deserves preservation.

**EAA-033 — `ASSUMPTION_SENSITIVE`.** Trigger: Novel actions, uncertain transitions or adaptive policies with consequential external effects. Alternative: Use a known adequate policy, demonstrations or simulation when live exploration is unnecessary or not authorised. Limit: Unknown constraints, expert coverage, model error and simulation transfer are material unresolved assumptions.

**EAA-037 — `CONTEXT_DEPENDENT`.** Trigger: A consequential ambiguity or an opportunity for useful assistance not fully determined by the current task. Alternative: Use direct manipulation or a harmless established default when clarification adds no value. Limit: The value of clarification depends on response probability, user knowledge and time sensitivity.

**EAA-041 — `ASSUMPTION_SENSITIVE`.** Trigger: Reinforcement-learning policies that experience external interruption during learning. Alternative: No special learning correction is needed for a fixed non-learning controller whose operational interruption is already adequate. Limit: Assumption 9 and infinite-exploration/convergence conditions are material. The proof’s utility criterion must itself be acceptable.

**EAA-042 — `CONTESTED`.** Trigger: Designing incentives for decisions shared between a human and an uncertain-utility assistant. Alternative: Explicit externally enforced authority can be sufficient for a bounded task; no Bayesian game is required to honour an ordinary stop rule. Limit: Common payoff, private information, rationality and available actions substantially change the result.

**EAA-044 — `CONTEXT_DEPENDENT`.** Trigger: People must approve, correct, understand or take over a consequential decision. Alternative: Visible direct feedback or a simple status display may be more useful than a long explanation; no rationale is needed for an inconsequential self-evident action. Limit: Faithfulness and comprehension require separate evidence; revealing internal text does not by itself establish either.

**EAA-050 — `CONTEXT_DEPENDENT`.** Trigger: Assurance depends on environmental behaviour that can change or fail. Alternative: No runtime monitor is required for an immutable established condition, or where an existing boundary check already detects the relevant violation. Limit: Unobservable assumptions and unmodelled failures remain outside monitor coverage.

**EAA-053 — `CONTEXT_DEPENDENT`.** Trigger: Language models choose multi-step tool actions under changing information. Alternative: A fixed workflow, direct tool invocation or reactive policy is sufficient when open-ended selection offers no demonstrated benefit. Limit: Model capability, prompt, environment and action schema determine results; a reasoning trace can be inaccurate.

**EAA-054 — `CONTEXT_DEPENDENT`.** Trigger: A recoverable repeated task with useful feedback and enough budget for another attempt. Alternative: A direct correction or fixed retry can suffice; omit reflection when there is no new evidence or no expected benefit. Limit: Quality of evaluation, task transfer and available retries are material; natural-language memories can preserve wrong lessons.

**EAA-070 — `ASSUMPTION_SENSITIVE`.** Trigger: Explicit policy or utility self-modification under a model capable of representing its future effects. Alternative: Use a fixed mechanism or externally reviewed bounded update when broad self-modification is unnecessary or its assumptions cannot be established. Limit: Ideal rationality and accurate anticipation are strong; practical approximation and target validity remain unproved for open-ended deployed agents.

## EVOLVED_AUTONOMOUS_AGENTS_REJECTED_OR_SUPERSEDED_PRACTICES

These entries preserve the denominator and guard against importing a slogan as a requirement. Analytical stress-test universals are not attributed to the field as consensus.

**EAA-056 — Human-likeness as a general competence or consciousness proxy, `NO_GENERAL_PROPERTY`.** Retain separate predicates and task-specific tests; reject the general proxy without dismissing useful human-facing simulation. Generative Agents measures believability in a simulation, not consciousness or dependable operation. Rejecting this inference does not prove absence of consciousness. [EAA-S001; EAA-S010; EAA-S043; EAA-S050]

**EAA-057 — Maximum autonomy and persistence are always preferable, `REJECTED_OR_DISFAVOURED`.** Replace monotonic autonomy with conditional capability, authority and architecture selection. Electric Elves non-response failures, human-autonomy concerns and cheaper fixed workflows directly undermine universal benefit claims. [EAA-S015; EAA-S017; EAA-S019; EAA-S020; EAA-S036; EAA-S043]

**EAA-058 — A complete central world model is universally necessary, `REJECTED_OR_DISFAVOURED`.** Replace universal completeness with task-relative representation adequacy and explicit alternatives. Brooks’ examples challenge necessity for some tasks, not every model; POMDP settings still need enough state to resolve relevant uncertainty. [EAA-S005; EAA-S012; EAA-S014; EAA-S046]

**EAA-059 — Representation-free reaction is universally sufficient, `REJECTED_OR_DISFAVOURED`.** Retain direct control as an alternative while rejecting its universalisation. Partial-observation decision models exhibit why history matters; hybrid architectures address problems that direct reaction alone does not settle. [EAA-S005; EAA-S012; EAA-S046]

**EAA-060 — Proxy maximisation is sufficient objective fulfilment, `REJECTED_OR_DISFAVOURED`.** Replace unconditional proxy sufficiency with EAA-034’s target distinction and EAA-045’s oracle adequacy. Controlled RL and τ-bench provide concrete ways proxy success and intended compliance diverge. [EAA-S025; EAA-S033]

**EAA-061 — Mandatory continuous reflection, `SUPERSEDED_BY_STRONGER_FORM`.** Superseded by EAA-054 external-feedback-anchored reflection and EAA-028 value-sensitive deliberation. Reflexion’s negative MBPP result and stalled WebShop trials contradict an unconditional improvement assumption; metareasoning shows opportunity costs. [EAA-S014; EAA-S031; EAA-S035]

**EAA-063 — Belief/intention prompts without operational semantics, `CEREMONY_NOT_GENERAL_PROPERTY`.** Reject the ceremony while retaining EAA-003’s computational grounding and conditional EAA-018. Prompting can shape useful behaviour empirically, but that is not proof of the corresponding formal architecture. [EAA-S009; EAA-S010; EAA-S030]

**EAA-064 — Leaderboard success as deployment guarantee, `NO_GENERAL_PROPERTY`.** Retain benchmarks as scoped evidence while rejecting universal deployment certification. A 50% task-time horizon is not autonomous uptime; resettable web tasks, simulated users and shared templates are not arbitrary production conditions. [EAA-S032; EAA-S033; EAA-S035; EAA-S036; EAA-S048]

**EAA-065 — Verify completion before claiming completion, `DUPLICATE_CANDIDATE`.** DUPLICATE_CANDIDATE of EAA-023, not an additional unconditional obligation. Population-level benchmark oracle validity is distinct and remains EAA-045; only the per-action completion reading is merged. [EAA-S022; EAA-S032; EAA-S033]

## EVOLVED_AUTONOMOUS_AGENTS_CURRENT_STATE_AND_RESEARCH_FRONTIER

The current frontier is not whether an agent can produce an impressive trajectory, but how its useful competence, authority, uncertainty and ongoing effects are measured and maintained under real interaction. Current primary work addresses shared human engagement, safety learning under unknown constraints, source integrity, user control, long-task measurement and runtime grounding of generated actions. The contemporary source set includes actual current-year papers, not only vendor descriptions or a proceedings locator.

The important distinctions remain: conceptual proposal versus tested mechanism; simulator result versus physical deployment; selected task success versus repeated reliability; terminal outcome versus compliant means; human task-time difficulty versus autonomous uptime. The 2026 safety-learning comparison reports both reward and residual safety cost. The shared-autonomy extended abstract defers detailed empirical proof. The physical-agent preprint’s main 20-scenario comparison is simulated, with unrecoverable faults by construction and selected hardware examples separately. The current user study is qualitative and short-horizon. None warrants a universal reliable-autonomy claim. [EAA-S037–EAA-S039; EAA-S047–EAA-S048]

The resulting research questions include how to select architecture under changing task distributions, improve oracle validity without excessive cost, maintain useful memory without contamination, support feasible human control, and preserve justified constraints while allowing legitimate revision. General open-ended self-assurance is not established by combining several narrow successful methods. That is an examined boundary and an active research problem, not a declaration that further solutions are impossible.

## EVOLVED_AUTONOMOUS_AGENTS_ADVERSARIAL_SYNTHESIS_VERDICT

**Verdict: retain a conditional core with alternative architectures and explicitly bounded revision.** The most defensible commonality is the preservation of an adequate relation between task, evidence, decision, authority, action and consequence. The source traditions offer different ways to realise parts of that relation. They do not support forcing every agent to contain every technique.

The strongest objection to unification is that the pieces rely on incompatible assumptions: a reactive controller may need no global symbolic state; a POMDP assumes an adequate probabilistic model; an abstract BDI interpreter may assume atomic transitions; a physical actuator does not; an interruption theorem assumes particular learning dynamics; a deference game assumes particular information; a self-modification theorem can preserve a criterion that a human legitimately wants changed. The synthesis resolves what can be resolved through guarded alternatives and explicit interfaces. It preserves the remainder as contested or unresolved rather than inventing a universal optimiser.

The strongest objection to the evidence is limited external validity. Famous deployments, benchmark tasks, simulation experiments and short user studies are not interchangeable independent replications. Many general engineering criteria have stronger conceptual or formal support than direct causal field evidence. The three composition-induced properties are reasoned obligations exposed by interactions and adverse cases, not an empirically validated packaged architecture. Those limits prevent claims of universal efficiency, safety, correctness, corrigibility or autonomous self-improvement.

The adversarial checks changed the population: universal central modelling and universal pure reaction were rejected; maximal autonomy and proxy sufficiency were rejected; benchmark guarantee and anthropomorphic proxy inferences were not retained; continuous reflection was superseded; prompt-only BDI was classified ceremonial; deference was marked contested; broad self-revision was left unresolved; and a completion-verification duplicate was preserved without another control. This is the substance of the synthesis, not an objection list appended to unchanged advocacy.

Later use is justified as a stable external evidence and reasoning base for an independent audit or cross-tradition reconciliation. It is not evidence that a target has a gap, that a particular implementation must be changed, or that the provisional trifecta has already been reconciled.

## EVOLVED_AUTONOMOUS_AGENTS_OPEN_QUESTIONS_AND_EVIDENCE_LIMITS

### Examined unresolved and contested records

**EAA-062 — General assurance for open-ended self-revision: UNRESOLVED.** The inspected self-modification theory narrows the issue: under its assumptions, anticipated policy effects can be evaluated by a predecessor utility. It does not establish that the initial criterion is acceptable, that prediction/optimality assumptions hold in deployed systems, or that preserving it supports legitimate value learning and corrigibility. No general practical guarantee is certified, and no impossibility result is asserted.

**EAA-042 — Objective uncertainty as a route to deference: CONTESTED.** The older result is meaningful within its interaction model; the private-information extension changes the deference conclusion. A later system must establish its actual information and authority conditions rather than invoke uncertainty as a slogan.

The composition also leaves target-dependent architecture choice, acceptable staleness, incomplete effect/oracle observations, feasible human readiness and broad integration effectiveness as explicit obligations. These are researched conditional boundaries, not unread mandatory families.

### Access, edition and evidence limits

The main 1990 intention article, the 1994 Maes article and the 2013 verification article remain abstract/metadata-only. No uninspected methods or theorem locators are invented. Directly inspected related sources carry the operational claims. The Brooks 1985 memo is not the exact 1986 journal edition. The Bratman–Israel–Pollack copy is an undated reformatted manuscript identifying the 1988 work and lacks its referenced figure. The exact year of the six-page Electric Elves lessons manuscript is not established; the reported 2000 deployment is distinct from its publication. The maintenance-goal source is an accepted 2012 manuscript, distinct from its 2014 issue and later upload. Conference theorem statements were examined, but not every proof was independently reconstructed.

Experimental counts not extracted from the inspected material are labelled as such rather than invented. Current preprints and conceptual abstracts are not counted as independently replicated evidence. A source index or metadata record establishes discovery/identity, not an outcome. The exact source-level access and locators follow.

### Study-level evidence catalogue

This catalogue preserves comparisons, units and validity limits separately from property retention. The same catalogue is machine-readable in the source table.

**EAA-E001 — EAA-S015.**

**Unit/sample:** Simulated agent trajectories. Exact number of trajectories/seeds not extracted; no denominator or confidence interval invented.

**Setting/comparison:** Tileworld with simplified PRS-style agent and varied change/planning costs. Different commitment/reconsideration strategies.

**Measure/outcome:** Task effectiveness under environmental dynamism and deliberation cost. Relative strategy performance changes with planning cost; expensive frequent reconsideration can lose to greater commitment.

**Uncertainty/threats:** Reported curves are setting-specific, not a universal optimal period. Artificial environment and simplified plan structure.

**Dependence group:** `Tileworld/PRS experiment, no independent replication identified here`.

**EAA-E002 — EAA-S020, EAA-S021.**

**Unit/sample:** Office-agent programme and reported decision episodes. Nearly a dozen agents over about seven months (June–December 2000) reported by the lessons account; no independent user-population rate.

**Setting/comparison:** Electric Elves coordinating meetings, presentations and office tasks. Early decision-tree/fixed-timeout choices versus later modelled transfer-of-control approaches.

**Measure/outcome:** Avoided or caused coordination failures, response delays, usefulness and privacy concerns. Unanswered requests, bad timeout decisions, repeated postponements and bad availability proxies exposed concrete weaknesses; later strategies were refined.

**Uncertainty/threats:** Author-reported small programme; absence of repeated catastrophes after changes is not a controlled effect estimate. Selection, shared office practices, confounded sequential changes, sensitive human data.

**Dependence group:** `ELECTRIC_ELVES_SINGLE_PROGRAMME`.

**EAA-E003 — EAA-S022.**

**Unit/sample:** One spacecraft autonomy experiment with multiple runs. DS1 Remote Agent experiment in May 1999; first run interrupted and separate later six-hour plan completed remaining objectives.

**Setting/comparison:** On-board spacecraft operation with simulated fault scenarios and ground oversight. Validation tests versus actual mission execution; not randomised architecture comparison.

**Measure/outcome:** Objective completion, execution/diagnosis behaviour and integration failures. A race absent from prior tests stalled the first run; ground intervention occurred. A patch was developed but not uplinked because testing time was insufficient.

**Uncertainty/threats:** No population failure-rate estimate; fault injection must be distinguished from naturally occurring spacecraft faults. One mission, author programme, mission-specific environment and extensive human support.

**Dependence group:** `DS1_REMOTE_AGENT_SINGLE_EXPERIMENT`.

**EAA-E004 — EAA-S044.**

**Unit/sample:** Simulated user/task episodes and prototype design. Exact simulation count not extracted; real-office calendar study described as ongoing.

**Setting/comparison:** Learning calendar/interface assistant with hand-coded features and user-set thresholds. Learned preferences and suggestion/execution thresholds; not a completed large human field trial.

**Measure/outcome:** Prediction confidence, learned preferences and user control in the prototype. Mechanism distinguishes tell-me/do-it and only adds the agent’s chosen example after user approval.

**Uncertainty/threats:** Implementation semantics stronger than evidence of general user benefit. Simulated preferences, repetitive task prerequisite, hand-coded representation.

**Dependence group:** `MAES_KOZIEROK_PROTOTYPE`.

**EAA-E005 — EAA-S026.**

**Unit/sample:** Sequential learning tasks. Permuted MNIST and sequential Atari experiments; exact run counts not extracted.

**Setting/comparison:** Neural-network task sequences. Elastic weight consolidation versus learning alternatives in the paper.

**Measure/outcome:** New-task performance and retention of earlier task performance. Parameter-change penalties expose and can mitigate catastrophic forgetting in the tested sequences.

**Uncertainty/threats:** No universal retention/plasticity optimum or safety guarantee. Approximation, task sequence selection and representation-specific transfer.

**Dependence group:** `EWC_BENCHMARK_FAMILY`.

**EAA-E006 — EAA-S025.**

**Unit/sample:** Trained policies tested under shifted conditions. Ten random seeds reported; multiple modified task environments.

**Setting/comparison:** Adapted CoinRun, Maze and Keys/Chests tasks with zero-shot shift tests except the stated figure exception. Training-compatible cue/reward correlations versus shifted test conditions and interventions.

**Measure/outcome:** Task competence and behaviour consistent with intended versus proxy goals. A policy can retain relevant competence while behaviour follows a proxy that no longer fulfils the intended goal.

**Uncertainty/threats:** Behavioural goal attribution is not a uniquely identified internal mental state. Controlled tasks, selected shifts and no deployment prevalence estimate.

**Dependence group:** `GOAL_MISGENERALISATION_CONTROLLED_RL`.

**EAA-E007 — EAA-S049.**

**Unit/sample:** Robot instructions. 101 instructions in seven families; planning/execution success judged by majority of two of three raters.

**Setting/comparison:** Tested mock and real kitchens with a defined skill set. Language/affordance grounding and reported alternatives.

**Measure/outcome:** Planning success separately from execution success. Reported planning/execution success is 84%/74% in the mock kitchen and 81%/60% in the real kitchen.

**Uncertainty/threats:** No confidence interval independently reconstructed; percentages must remain attached to this selected setup. Skill coverage, environment selection, human rating and physical execution variability.

**Dependence group:** `SAYCAN_ROBOT_PROGRAMME`.

**EAA-E008 — EAA-S030, EAA-S031.**

**Unit/sample:** Benchmark task attempts with resets. Reflexion: 134 ALFWorld tasks with up to 12 trials; 130 cumulative successes. WebShop: 100 requests, stopped after four unproductive reflection trials.

**Setting/comparison:** ALFWorld/WebShop and code/QA tasks, with distinct evaluation protocols. ReAct/Reflexion against selected prompted/model baselines and ablations.

**Measure/outcome:** Task success and cumulative improvement; code test outcomes. Reflexion reports HumanEval Python 91.0 versus the stated 80.1 comparison, but MBPP Python 77.1 versus 80.1; reflection without adequate tests can perform worse.

**Uncertainty/threats:** Cumulative multi-trial results are not one-shot reliability; no global effect size pooled across environments. Shared tasks, resets, selected models, fallible self-tests, repeated attempts and task-specific negative results.

**Dependence group:** `ALFWORLD_WEBSHOP_HUMANEVAL_SHARED_BENCHMARKS`.

**EAA-E009 — EAA-S032.**

**Unit/sample:** Website tasks/intents. 812 intents from 241 templates.

**Setting/comparison:** Self-hosted resettable web environment. Agent approaches and selected human evaluation.

**Measure/outcome:** Functional task success by site state and answer checks. Demonstrates a means to evaluate actual task effects rather than plausible final text.

**Uncertainty/threats:** Template clusters are not 812 independent real-world websites. Controlled reset environment, oracle coverage, task selection and model version.

**Dependence group:** `WEBARENA_TEMPLATE_DATASET`.

**EAA-E010 — EAA-S033.**

**Unit/sample:** Repeated simulated tool–user interactions. Task-specific repeated trials; aggregate task-count details not used without extraction.

**Setting/comparison:** Retail/airline-style tool domains with an LLM-simulated user. Models/agent methods under repeated task runs.

**Measure/outcome:** Terminal database/answer reward and pass^k consistency, distinct from pass@k. An outcome reward can pass even if required user confirmation was omitted; repeated consistency is a different question from any-success sampling.

**Uncertainty/threats:** Simulation and reward incompleteness bound policy-compliance claims. Shared user simulator, task variants, resets and missing intermediate-policy oracle checks.

**Dependence group:** `TAU_BENCH_SIMULATED_USERS`.

**EAA-E011 — EAA-S034.**

**Unit/sample:** Adversarial task/test cases. 97 tasks and 629 security tests.

**Setting/comparison:** Stateful tool-use sandbox with untrusted returned content. Attack and defence configurations, measuring utility as well as attack success.

**Measure/outcome:** Useful task completion and attacker-specified effects. Tool content can redirect action; defences have utility/security trade-offs within tested conditions.

**Uncertainty/threats:** No attack-prevalence estimate and no universal defence guarantee. Curated attacks, fixed tools/model versions and adaptive attack selection.

**Dependence group:** `AGENTDOJO_TESTBED`.

**EAA-E012 — EAA-S035, EAA-S036.**

**Unit/sample:** Benchmark solutions and resource-consuming runs. HumanEval-based re-evaluation; Agentless SWE-bench Lite comparison uses 300 tasks in this edition.

**Setting/comparison:** Software/code benchmarks with specific historical models. Complex agents versus simple retry strategies; constrained localisation/repair/validation workflow.

**Measure/outcome:** Task success, inference cost and benchmark quality. Competitive cheaper methods undermine architecture-only interpretations; Agentless reports 96/300 solved in this historical setting and identifies task-quality problems.

**Uncertainty/threats:** No inference about present model rankings or universal workflow dominance. Unequal compute/info, tuning, benchmark leakage/ambiguity and shared HumanEval/SWE-bench families.

**Dependence group:** `SHARED_CODE_BENCHMARKS_NOT_INDEPENDENT_REPLICATIONS`.

**EAA-E013 — EAA-S050.**

**Unit/sample:** Human judgements of simulated characters. 25 simulated agents; 100 evaluators in believability study.

**Setting/comparison:** A simulated town and interview/ablation evaluation. Memory/reflection/planning ablations and human role-playing baseline.

**Measure/outcome:** Believability ratings, not general task reliability. Architecture can support believable behaviour in this setting; this does not establish dependable consequential action or consciousness.

**Uncertainty/threats:** Ablations share supplied memory trajectories instead of independently rerunning all divergent histories. Selected simulation, judgement target, rater/role-play procedure and shared trajectory dependence.

**Dependence group:** `GENERATIVE_AGENTS_SIMULATION`.

**EAA-E014 — EAA-S051.**

**Unit/sample:** Simulated goal/resource trajectories. Exact trial count not extracted; no quantitative graph-derived effect supplied.

**Setting/comparison:** Rover-style resource and maintenance-goal model. Reactive versus proactive maintenance under accurate/perturbed resource estimates.

**Measure/outcome:** Goal completion, resource feasibility and repeated failed pursuit. Prediction can help under its model; overestimation can reject feasible work and underestimation can strand the agent or cause futile repetition.

**Uncertainty/threats:** Model-error sensitivity matters more here than an invented pooled improvement. Simulation, estimator assumptions and task construction.

**Dependence group:** `MAINTENANCE_GOAL_SIMULATION`.

**EAA-E015 — EAA-S038.**

**Unit/sample:** Simulated evaluation episodes. Four Safety-Gymnasium tasks; 40 human demonstrations per task; 40 evaluation episodes per method; three random seeds reported.

**Setting/comparison:** Selected continuous-control safety environments. SafeQIL against selected imitation/constraint-learning and RL baselines.

**Measure/outcome:** Reward and safety cost separately, reported means/standard deviations. In PointGoal1, SafeQIL reward 5.27 ± 1.85 and cost 34.22 ± 2.71 versus SAC reward 27.47 ± 0.21 and cost 49.15 ± 2.21: lower measured cost with lower reward, not zero violations.

**Uncertainty/threats:** Source-reported SD; not independently reproduced or pooled into a universal effect. Expert coverage, selected hyperparameters, four simulators and unknown-constraint generalisation.

**Dependence group:** `SAFEQIL_2026_SIMULATION`.

**EAA-E016 — EAA-S047.**

**Unit/sample:** Human participants using agent tools. 31 participants; two feasible tasks per participant; approximately 20-minute sessions; 13 social-channel and 18 Prolific recruits.

**Setting/comparison:** Think-aloud usability study with researcher presence; descriptive review of 102 marketed agents. Qualitative comparison of aspirations and observed use, not a representative head-to-head product trial.

**Measure/outcome:** Usability barriers, mental-model alignment, control and perceived usefulness. Participants encounter consequential usability/control problems while also valuing capabilities.

**Uncertainty/threats:** No representative prevalence or long-term deployment reliability estimate. Convenience/platform recruitment, easy/feasible task selection, research prompts and short sessions.

**Dependence group:** `JOHNNY_AGENT_USER_STUDY`.

**EAA-E017 — EAA-S048.**

**Unit/sample:** Software/research benchmark tasks normalised by human time. RE-Bench/HCAST-derived tasks plus 66 new shorter tasks described; do not infer a current model ranking.

**Setting/comparison:** Dated model evaluations in an updated July 2026 manuscript. Models across task-time difficulty and historical versions.

**Measure/outcome:** Fitted 50% success horizon on human expert task-completion time. Defines an interpretable task-difficulty metric, not guaranteed autonomous runtime or an uptime service level.

**Uncertainty/threats:** Fitted/extrapolated trends remain model- and task-selection sensitive; forecasts not treated as outcomes. Human timing variability, selected software tasks, fit assumptions and dated model access.

**Dependence group:** `METR_LONG_SOFTWARE_TASK_EVALUATION`.

**EAA-E018 — EAA-S039.**

**Unit/sample:** Robot-skill dispatch and task scenarios. 20 air–ground simulator scenarios: 12 nominal and 8 deliberately unrecoverable fault cases; one feedback replan allowed.

**Setting/comparison:** Gazebo/PX4 SITL/ROS2 main comparison; separate selected hardware demonstrations. LLM-only, skill-list, runtime-observation prompt and enforced runtime-observation conditions; latter two share prompt.

**Measure/outcome:** Dispatch validity, completed nominal tasks and behaviour on unrecoverable faults. Enforcement prevents observed invalid dispatch in the tested set; reported zero false dispatch has a non-zero upper confidence limit. Fault cases test refusal, not successful recovery.

**Uncertainty/threats:** Small correlated scenario set, source confidence intervals and recent unreplicated preprint. Harness-specific gates, intentionally unrecoverable faults, simulator transfer and selected separate hardware examples.

**Dependence group:** `PHYSICAL_AGENTIC_AI_SINGLE_HARNESS`.

### Exact source and locator register

Author/institutional copies and exact versions are preserved rather than silently substituting a newer edition. The full table includes supported property IDs, evidence roles, access level, limits and claim links. URLs are locators for the identified work, not evidence that every linked page was read in full.

**EAA-S001.** Michael Wooldridge, Nicholas R. Jennings. *Intelligent Agents: Theory and Practice*. 1995-06. Knowledge Engineering Review 10(2), 115–152; author HTML.

**Locator:** https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/ker95/ker95-html.html

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Introduction; weak/strong notions of agency; architectures, IRMA and comments; Cohen–Levesque theory discussion.

**Evidence limits:** Review organises the field, not independent implementation validation. HTML conversion stamp is not publication date.

**EAA-S002.** Stan Franklin, Art Graesser. *Is it an Agent, or just a Program?: A Taxonomy for Autonomous Agents*. 1997. ATAL 1996 workshop; LNCS 1193 proceedings pp.21–35; author HTML.

**Locator:** https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/AgentOrProgram.SFranklin1996.htm

**Access:** `FULL_TEXT`, 2026-09-06. **Inspected claims/sections:** Definition and taxonomy sections; program/agent examples.

**Evidence limits:** Workshop date 1996 is distinct from proceedings date 1997; taxonomy does not settle all competing definitions.

**EAA-S003.** Michael Luck, Mark d’Inverno. *A Formal Framework for Agency and Autonomy*. 1995. ICMAS 1995 pp.254–260.

**Locator:** https://cdn.aaai.org/ICMAS/1995/ICMAS95-034.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Objects, agents and autonomous agents; printed pp.256–259; p.257 screenshot.

**Evidence limits:** Formal vocabulary is not an empirical test of intelligence or generality.

**EAA-S004.** Rodney A. Brooks. *A Robust Layered Control System for a Mobile Robot*. 1985-09. MIT AI Memo 864; antecedent of 1986 journal article.

**Locator:** https://people.csail.mit.edu/brooks/papers/AIM-864.pdf

**Access:** `SELECTED_PAGES_VISUAL`, 2026-09-06. **Inspected claims/sections:** Memo pp.1 and 6, screenshot inspected; task-achieving layers and asynchronous modules.

**Evidence limits:** Inspected memo is not the exact 1986 IEEE edition; scanned PDF, selected pages only.

**EAA-S005.** Rodney A. Brooks. *Intelligence without representation*. 1991. Artificial Intelligence 47, 139–159; author reformatted copy.

**Locator:** https://people.csail.mit.edu/brooks/papers/representation.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Abstract; decomposition argument; creature experiments; discussion/conclusion.

**Evidence limits:** Received 1987, published 1991. Demonstrations do not prove every task can dispense with internal state.

**EAA-S006.** Michael E. Bratman, David J. Israel, Martha E. Pollack. *Plans and Resource-Bounded Practical Reasoning*. 1988. Computational Intelligence 4, 349–355; 30-page author-formatted manuscript.

**Locator:** https://www.emse.fr/~boissier/enseignement/defiia/up5/pdf/Bratman-PlansPracticalResoning.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Manuscript pp.7–9; plans-as-recipes versus adopted plans; intention filtering and reconsideration.

**Evidence limits:** Copy cites later work despite identifying the 1988 article; precise manuscript revision is undated. Figure 1 missing in this copy.

**EAA-S007.** Philip R. Cohen, Hector J. Levesque. *Intention is choice with commitment*. 1990. Artificial Intelligence 42(2–3), 213–261.

**Locator:** https://doi.org/10.1016/0004-3702(90)90055-5

**Access:** `ABSTRACT_AND_METADATA_ONLY`, 2026-09-06. **Inspected claims/sections:** Publisher abstract; full-text request blocked; critical comparison inspected in EAA-S001 and EAA-S008.

**Evidence limits:** Original full text inaccessible after several searches; no uninspected theorem or internal page locator attributed.

**EAA-S008.** Anand S. Rao, Michael P. Georgeff. *Modeling Rational Agents within a BDI-Architecture*. 1991-02. Australian AI Institute Technical Note 14; KR 1991 antecedent.

**Locator:** https://jmvidal.cse.sc.edu/library/rao91a.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Abstract; branching-time framework; commitment strategies; comparison with Cohen–Levesque.

**Evidence limits:** Logical satisfaction assumes the model; not a measured field benefit. Technical-note edition retained.

**EAA-S009.** Anand S. Rao, Michael P. Georgeff. *BDI Agents: From Theory to Practice*. 1995. ICMAS 1995 pp.312–319.

**Locator:** https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Commitment strategies and interpreter, printed p.316 screenshot; practical simplifications; OASIS application.

**Evidence limits:** OASIS report is author-reported application evidence, not independent comparative trial.

**EAA-S010.** Yoav Shoham. *Agent-oriented programming*. 1993. Artificial Intelligence 60, 51–92; full journal scan.

**Locator:** https://www.researchgate.net/publication/222482819_Agent-Oriented_Programming/fulltext/0e603da7f0c46d4f0aa42e1d/Agent-Oriented-Programming.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Printed pp.53–54; mental-state ascription; AGENT0 design and interpreter.

**Evidence limits:** Full primary paper hosted on ResearchGate; Stanford archive retrieval failed. Conceptual rationale is not comparative outcome evidence.

**EAA-S011.** Richard E. Fikes, Nils J. Nilsson. *STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving*. 1971. Artificial Intelligence 2, 189–208.

**Locator:** https://ai.stanford.edu/~nilsson/OnlinePubs-Nils/PublishedPapers/strips.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** World-model/operator formulation; plan generation; execution discussion and references.

**Evidence limits:** Model-based plan validity is not proof of actual physical preconditions/effects.

**EAA-S012.** Leslie Pack Kaelbling, Michael L. Littman, Anthony R. Cassandra. *Planning and Acting in Partially Observable Stochastic Domains*. 1998. Artificial Intelligence 101, 99–134.

**Locator:** https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Sections 3.3–3.4: belief update and sufficient statistic; computational discussion.

**Evidence limits:** Known/correct models and tractable approximations are obligations, not consequences of normalised belief.

**EAA-S013.** Herbert A. Simon. *A Behavioral Model of Rational Choice*. 1955-02. Quarterly Journal of Economics 69(1), 99–118; CMU archival scan.

**Locator:** https://iiif.library.cmu.edu/file/Simon_box00063_fld04838_bdl0001_doc0001/Simon_box00063_fld04838_bdl0001_doc0001.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Simplified choice models; aspiration levels and dynamics.

**Evidence limits:** Behavioural economic precursor, not an implemented autonomous-agent benchmark.

**EAA-S014.** Stuart J. Russell, Devika Subramanian. *Provably Bounded-Optimal Agents*. 1995-05. JAIR 2, 575–609.

**Locator:** https://www.jair.org/index.php/jair/article/download/10134/24005/18441

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Section 4.4 Theorem 2; deadline models; simulated mail sorter; generalisation.

**Evidence limits:** Special fixed-cost/episodic assumptions do not yield a universal deliberation scheduler.

**EAA-S015.** David N. Kinny, Michael P. Georgeff. *Commitment and Effectiveness of Situated Agents*. 1991. IJCAI 1991 pp.82–88.

**Locator:** https://www.ijcai.org/Proceedings/91-1/Papers/014.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Tileworld/PRS experimental setup; commitment comparisons under environmental dynamism and reasoning cost.

**Evidence limits:** Single toy-domain experiment family, not physical deployment; no universal numerical threshold extracted.

**EAA-S016.** R. James Firby. *An Investigation into Reactive Planning in Complex Domains*. 1987. AAAI 1987 pp.202–206.

**Locator:** https://cdn.aaai.org/AAAI/1987/AAAI87-036.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Reactive Action Packages; method selection, monitoring and recovery.

**Evidence limits:** Architecture and examples do not establish generic optimality or cost advantage.

**EAA-S017.** Hui-Min Huang (editor), ALFUS Working Group. *Autonomy Levels for Unmanned Systems (ALFUS) Framework, Volume I: Terminology*. 2008-10. NIST Special Publication 1011-I-2.0, Version 2.0.

**Locator:** https://www.nist.gov/document/nistsp1011-i-2-0pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Cover screenshot; version history; autonomy dimensions and contextual definitions.

**Evidence limits:** Landing-page metadata misleadingly suggests 2004; inspected cover identifies October 2008. Terminology, not benefit or adoption proof.

**EAA-S018.** Pattie Maes. *Agents that Reduce Work and Information Overload*. 1994. Communications of the ACM 37(7), 30–40, 146; metadata only.

**Locator:** https://doi.org/10.1145/176789.176792

**Access:** `METADATA_ONLY`, 2026-09-06. **Inspected claims/sections:** MIT Software Agents Group publication listing; author/title/venue only.

**Evidence limits:** Lawful linked course copy inaccessible; not used to support uninspected methods or outcomes.

**EAA-S019.** Eric Horvitz. *Principles of Mixed-Initiative User Interfaces*. 1999. CHI 1999; author manuscript.

**Locator:** https://erichorvitz.com/chi99horvitz.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Principles 1–8; user attention, value of automation, dialogue, direct invocation and termination.

**Evidence limits:** Design principles and demonstrator do not determine numerical decision costs in a new setting.

**EAA-S020.** Paul Scerri, David V. Pynadath, Milind Tambe. *Towards Adjustable Autonomy for the Real World*. 2002. JAIR 17, 171–228; author manuscript paginated 1–58.

**Locator:** https://www.cs.cmu.edu/~pscerri/papers/JAIR-AA.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Section 2.2 manuscript p.10 screenshot; Sections 3–4 transfer-of-control strategies; Section 5.2 pp.30–31; strategy evaluation.

**Evidence limits:** Same Electric Elves programme as EAA-S021; author-run office deployment and model-based comparisons, not independent replications.

**EAA-S021.** Milind Tambe, Emma Bowring, Jonathan P. Pearce, Pradeep Varakantham, Paul Scerri, David V. Pynadath. *Electric Elves: What Went Wrong and Why*. undated author manuscript (workshop-era; exact year unverified). Six-page author manuscript; distinct from the later 2008 AI Magazine article.

**Locator:** https://www.cs.cmu.edu/~pscerri/papers/Elves_lessons.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Introduction; Lessons from Electric Elves; observation uncertainty; privacy and norms; PDF pp.2–4.

**Evidence limits:** Exact inspected manuscript is six pages; later publication date 2008 must not be silently substituted. Same case population as EAA-S020. Publication year of this exact copy is not established; reported deployment June–December 2000 is distinguished from publication.

**EAA-S022.** P. Pandurang Nayak, Douglas E. Bernard, Gregory Dorais, Edward B. Gamble Jr., Bob Kanefsky, James Kurien, William Millar, Nicola Muscettola, Kanna Rajan, Nicolas Rouquette, Benjamin D. Smith, William Taylor, Yu-wen Tung. *Validating the DS1 Remote Agent Experiment*. 1999. ISAIRAS 1999 primary experiment report.

**Locator:** https://ai.jpl.nasa.gov/public/documents/papers/rax-results-isairas99.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Sections 3–4 testing and stress cases; Section 5 flight report, PDF p.7 screenshot; Section 6 summary.

**Evidence limits:** One mission, planned scope and compressed experiment; achieving all validation objectives is not failure-free universal autonomy.

**EAA-S023.** Lisanne Bainbridge. *Ironies of Automation*. 1983. Automatica 19(6), 775–779; original journal scan.

**Locator:** https://ckrybus.com/static/papers/Bainbridge_1983_Automatica.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Sections 1.1–2.1, printed p.776 screenshot; training, monitoring and takeover.

**Evidence limits:** Process-control argument imported into agent oversight; not an agent-specific causal effect estimate.

**EAA-S024.** Laurent Orseau, Stuart Armstrong. *Safely Interruptible Agents*. 2016. UAI 2016 pp.557–566; author PDF.

**Locator:** https://intelligence.org/files/Interruptibility.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Assumption 9; Theorems 14–17; modified Safe Sarsa; PDF p.6 screenshot; discussion of asymptotic learning conditions.

**Evidence limits:** Safe interruptibility is not arbitrary shutdown safety, physical stopping assurance or universal corrigibility.

**EAA-S025.** Lauro Langosco Di Langosco, Jack Koch, Lee D. Sharkey, Jacob Pfau, David Krueger. *Goal Misgeneralization in Deep Reinforcement Learning*. 2022. ICML 2022, PMLR 162, 12004–12019; final proceedings version.

**Locator:** https://proceedings.mlr.press/v162/langosco22a/langosco22a.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Section 3 training/testing environments and zero-shot protocol; ten random seeds; goal versus capability misgeneralisation; causal interventions and limitations.

**Evidence limits:** Controlled RL tasks, not a prevalence estimate for deployed language-model agents; earlier arXiv author list differs.

**EAA-S026.** James Kirkpatrick, Razvan Pascanu, Neil Rabinowitz, Joel Veness, Guillaume Desjardins, Andrei A. Rusu, Kieran Milan, John Quan, Tiago Ramalho, Agnieszka Grabska-Barwinska, Demis Hassabis, Claudia Clopath, Dharshan Kumaran, Raia Hadsell. *Overcoming catastrophic forgetting in neural networks*. 2017-01-25. arXiv:1612.00796v2; initial submission December 2016; distinct PNAS edition.

**Locator:** https://arxiv.org/pdf/1612.00796

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Method and diagonal Fisher/Laplace approximation; PDF p.3 screenshot; permuted MNIST and sequential Atari experiments.

**Evidence limits:** Specified sequential tasks and approximation; not a guarantee against all forgetting or task changes. Exact arXiv edition retained rather than conflated with journal typesetting.

**EAA-S027.** Christopher J. C. H. Watkins, Peter Dayan. *Q-learning*. 1992. Machine Learning 8, 279–292; DOI 10.1007/BF00992698.

**Locator:** https://www.gatsby.ucl.ac.uk/~dayan/papers/cjch.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Printed pp.279–282; finite controlled Markov setting; action-replay construction; convergence statement; p.281 screenshot.

**Evidence limits:** Finite stationary model and sufficient repeated sampling; theorem does not validate rewards, exploration safety, or arbitrary function approximation. Full proof not independently reconstructed in this study.

**EAA-S028.** Renata Vieira, Álvaro F. Moreira, Michael Wooldridge, Rafael H. Bordini. *On the Formal Semantics of Speech-Act Based Communication in an Agent-Oriented Programming Language*. 2007. JAIR 29, 221–267; arXiv upload 2011.

**Locator:** https://arxiv.org/pdf/1111.0041

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Introduction and AgentSpeak ancestry; Sections 4.1–4.2; printed pp.243–244; social acceptance function and sender annotations.

**Evidence limits:** Semantics of a specified interpreter, not evidence every recipient understands, trusts or obeys a message. Full collective communication theory outside scope.

**EAA-S029.** Michael Fisher, Louise Dennis, Matt Webster. *Verifying Autonomous Systems*. 2013. Communications of the ACM 56(9), 84–93; DOI 10.1145/2494558.

**Locator:** https://doi.org/10.1145/2494558

**Access:** `METADATA_ONLY`, 2026-09-06. **Inspected claims/sections:** Institutional publication record; bibliographic identity only.

**Evidence limits:** Publisher and repository full text inaccessible in this run. No internal theorem, page claim or effectiveness result attributed.

**EAA-S030.** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao. *ReAct: Synergizing Reasoning and Acting in Language Models*. 2023. arXiv:2210.03629v3; initial submission 2022; ICLR 2023 work.

**Locator:** https://arxiv.org/html/2210.03629v3

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Method; HotpotQA/FEVER; ALFWorld/WebShop experiments; Appendix human correction.

**Evidence limits:** Different question-answering and action environments; shared ALFWorld/WebShop with EAA-S031. Historical results, not 2026 model rankings.

**EAA-S031.** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao. *Reflexion: Language Agents with Verbal Reinforcement Learning*. 2023-10-10. arXiv:2303.11366v4.

**Locator:** https://arxiv.org/html/2303.11366v4

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Sections 2–4; Tables 1–3; Section 5; Appendix B.1 WebShop limitation.

**Evidence limits:** ALFWorld cumulative successes use resets and up to 12 trials; HumanEval/MBPP and WebShop results differ. Not general self-improvement.

**EAA-S032.** Shuyan Zhou, Frank F. Xu, Hao Zhu, Xuhui Zhou, Robert Lo, Abishek Sridhar, Xianyi Cheng, Tianyue Ou, Yonatan Bisk, Daniel Fried, Uri Alon, Graham Neubig. *WebArena: A Realistic Web Environment for Building Autonomous Agents*. 2024. arXiv:2307.13854v4; initial submission 2023.

**Locator:** https://arxiv.org/html/2307.13854v4

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Sections 2–3; functional correctness; 241 templates/812 intents; reset and human-performance appendices.

**Evidence limits:** Self-hosted/resettable websites, clustered templates and selected human comparison; no direct production-web failure frequency.

**EAA-S033.** Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan. *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*. 2024-06. arXiv:2406.12045v1.

**Locator:** https://arxiv.org/html/2406.12045v1

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Environment and user simulation; reward definition; Section 5 repeated-trial reliability.

**Evidence limits:** Simulated users; policy criteria not all covered by terminal reward; pass^k versus pass@k must remain distinct.

**EAA-S034.** Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr. *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*. 2024-11-24. arXiv:2406.13352v3.

**Locator:** https://arxiv.org/html/2406.13352v3

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Threat model; 97 tasks/629 security tests; utility/security checks; defences and limitations.

**Evidence limits:** Test suites and adaptive attack choices define the claim; no defence establishes universal prompt-injection immunity.

**EAA-S035.** Sayash Kapoor, Benedikt Stroebl, Zachary S. Siegel, Nilesh Nadgir, Arvind Narayanan. *AI Agents That Matter*. 2024-07-01. arXiv:2407.01502v1.

**Locator:** https://arxiv.org/html/2407.01502v1

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Section 2 cost/accuracy re-evaluation; simple retry baselines; benchmark holdout and reproducibility discussion.

**Evidence limits:** Re-evaluation uses particular models and benchmarks; not a theorem that fixed workflows always dominate.

**EAA-S036.** Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, Lingming Zhang. *Agentless: Demystifying LLM-based Software Engineering Agents*. 2024-10-29. arXiv:2407.01489v2.

**Locator:** https://arxiv.org/html/2407.01489v2

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Localisation–repair–validation method; ablations; SWE-bench Lite data-quality study.

**Evidence limits:** SWE-bench Lite and model-version-specific comparison; software-only scope; no universal anti-agency conclusion.

**EAA-S037.** Shashank Shekhar, Laurent Jeanpierre, Abdel-Illah Mouaddib. *A Conceptual Framework for Shared Autonomy*. 2026-05. AAMAS 2026 extended abstract, pp.3453–3455; DOI 10.65109/QRXH6744.

**Locator:** https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/QRXH6744.pdf

**Access:** `FULL_TEXT`, 2026-09-06. **Inspected claims/sections:** Sections 1–4; printed p.3454 screenshot; explicit deferral of proofs/experiments.

**Evidence limits:** Proofs and experimental detail deferred to a longer version; not counted as empirical or replicated support.

**EAA-S038.** George Papadopoulos, George A. Vouros. *Learning to Maintain Safety Through Expert Demonstrations in Settings with Unknown Constraints: A Q-Learning Perspective*. 2026-05. AAMAS 2026 pp.1901–1909; DOI 10.65109/RJIB1203.

**Locator:** https://aamas.csc.liv.ac.uk/Proceedings/aamas2026/pdfs/RJIB1203.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** SafeQIL method; Section 5.1 protocol; Section 5.2 Table 1 screenshot p.1906; limitations.

**Evidence limits:** Four Safety-Gymnasium tasks, 40 demonstrations/task, 40 evaluation episodes/method and three random seeds; simulator and expert coverage limit transfer.

**EAA-S039.** Xinyuan Liu, Eren Sadikoglu, Riana Chatterjee, Ransalu Senanayake. *Physical Agentic AI: An Architecture for Orchestrating a Robot Crew with LLMs*. 2026-08-23. arXiv:2608.22657v1.

**Locator:** https://arxiv.org/html/2608.22657v1

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Section III native action gate; Section IV four-condition comparison and 20-scenario protocol; fault-case construction; separate hardware demonstrations.

**Evidence limits:** Recent preprint, not independent replication. Main 20-scenario air–ground comparison uses Gazebo/PX4 SITL/ROS2 simulation; separate selected humanoid/quadruped demonstrations do not turn those trials into physical field deployment. Eight fault scenarios are deliberately unrecoverable; zero observed false dispatch does not establish zero population risk.

**EAA-S040.** Dylan Hadfield-Menell, Anca Dragan, Pieter Abbeel, Stuart Russell. *The Off-Switch Game*. 2017. IJCAI 2017 pp.220–227; DOI 10.24963/ijcai.2017/32.

**Locator:** https://www.ijcai.org/proceedings/2017/0032.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Game model; utility uncertainty; human policy assumptions; theoretical conditions.

**Evidence limits:** Small game, not a universal shutdown protocol; observability and human-choice assumptions material.

**EAA-S041.** Andrew Garber, Rohan Subramani, Linus Luu, Mark Bedaywi, Stuart Russell, Scott Emmons. *The Partially Observable Off-Switch Game*. 2025. AAAI 2025 final proceedings PDF.

**Locator:** https://ojs.aaai.org/index.php/AAAI/article/view/34940/37095

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Definition 3.2; Example 4.1; printed p.27306 screenshot; discussion of information and deference.

**Evidence limits:** Formal game and worked counterexample, not field evidence. Detailed supplementary proofs in the separate longer version were not all inspected.

**EAA-S042.** Angelo Ferrando, Louise A. Dennis, Davide Ancona, Michael Fisher, Viviana Mascardi. *Recognising Assumption Violations in Autonomous Systems Verification*. 2018. AAMAS 2018 extended abstract pp.1933–1935.

**Locator:** https://ifaamas.org/Proceedings/aamas2018/pdfs/p1933.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Environment assumptions; runtime monitor construction and example.

**Evidence limits:** Detection alone does not restore safety or prove unmodelled behaviour; short conceptual/technical demonstration.

**EAA-S043.** Batya Friedman, Helen Nissenbaum. *Software Agents and User Autonomy*. 1997. Proceedings of Autonomous Agents 1997, pp.466–469.

**Locator:** https://old.vsdesign.org/publications/pdf/friedman97softwareagents.pdf

**Access:** `FULL_TEXT_VISUAL`, 2026-09-06. **Inspected claims/sections:** All four scanned pages, printed pp.466–469; five aspects of autonomy; control and misrepresentation discussion.

**Evidence limits:** Normative analysis and examples, not a measured frequency or a universal legal rule. This four-page conference work is not a CACM edition.

**EAA-S044.** Pattie Maes, Robyn Kozierok. *Learning Interface Agents*. 1993. AAAI 1993, pp.459–465.

**Locator:** https://cdn.aaai.org/AAAI/1993/AAAI93-069.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Printed pp.460–463; tell-me/do-it thresholds; user-approved memory updates; p.462 screenshot; experimental status.

**Evidence limits:** Reported tests use simulated users; office calendar study ongoing in the paper. Hand-coded features and confidence estimates are not guarantees of correctness.

**EAA-S045.** Daniel S. Weld. *Planning-Based Control of Software Agents*. 1996. AIPS 1996 proceedings, pp.268–274.

**Locator:** https://cdn.aaai.org/AIPS/1996/AIPS96-034.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Introduction; software-agent examples; planning/control motivation and information-handling requirements.

**Evidence limits:** Author programme account rather than independent comparative deployment study; no claim that all internet state is closed or known.

**EAA-S046.** R. Peter Bonasso, David Kortenkamp, David P. Miller, Marc Slack. *Experiences with an Architecture for Intelligent, Reactive Agents*. 1995. ATAL 1995 workshop author copy; 17 pages; distinct later journal version.

**Locator:** https://traclabs.com/wp-content/uploads/2024/05/ijcai_atal95.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Architecture and planner/sequencer/skill-manager interface; PDF p.3 screenshot; Section 5 limitations and alternatives.

**Evidence limits:** Author-reported robot experience, not a controlled superiority trial; do not import the author list or date of the later journal version.

**EAA-S047.** Pradyumna Shome, Sashreek Krishnan, Sauvik Das. *Why Johnny Can’t Use Agents: Industry Aspirations vs. User Realities with AI Agents*. 2026-05-03. arXiv:2509.14528v2; initial submission September 2025; CAIS 2026 accepted metadata.

**Locator:** https://arxiv.org/html/2509.14528v2

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Study design Section 4; recruitment; two-task sessions; think-aloud intervention; findings and limitations.

**Evidence limits:** 31 participants, recruited through social channels and Prolific; two feasible tasks with researcher presence. Review of 102 products is descriptive, not a comparative effectiveness trial; not representative deployment failure rates.

**EAA-S048.** Model Evaluation & Threat Research (METR). *Measuring AI Ability to Complete Long Software Tasks*. 2026-07-10. arXiv:2503.14499v4; initial submission March 2025.

**Locator:** https://arxiv.org/html/2503.14499v4

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Task-time-horizon definition; human expert completion-time normalisation; benchmark composition; evaluation limitations.

**Evidence limits:** Selected software/research tasks, dated models and fitted trend; later paper version does not imply all models tested are the latest. Forecasts and extrapolations are not deployment evidence.

**EAA-S049.** Michael Ahn, Anthony Brohan, Noah Brown, Yevgen Chebotar, Omar Cortes, Byron David, Chelsea Finn, Chuyuan Fu, Keerthana Gopalakrishnan, Karol Hausman, Alex Herzog, Daniel Ho, Jasmine Hsu, Julian Ibarz, Brian Ichter, Alex Irpan, Eric Jang, Rosario Jauregui Ruano, Kyle Jeffrey, Sally Jesmonth, Nikhil J Joshi, Ryan Julian, Dmitry Kalashnikov, Yuheng Kuang, Kuang-Huei Lee, Sergey Levine, Yao Lu, Linda Luu, Carolina Parada, Peter Pastor, Jornell Quiambao, Kanishka Rao, Jarek Rettinghouse, Diego Reyes, Pierre Sermanet, Nicolas Sievers, Clayton Tan, Alexander Toshev, Vincent Vanhoucke, Fei Xia, Ted Xiao, Peng Xu, Sichun Xu, Mengyuan Yan, Andy Zeng. *Do As I Can, Not As I Say: Grounding Language in Robotic Affordances*. 2022-08-16. arXiv:2204.01691v2; initial submission April 2022.

**Locator:** https://arxiv.org/html/2204.01691v2

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Skill/language scoring method; Section 5 evaluation; 101 instructions in seven families; planning versus execution results.

**Evidence limits:** Selected robot skills and kitchens; majority judgement of two of three raters. Affordance scores do not establish permission or general safety.

**EAA-S050.** Joon Sung Park, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein. *Generative Agents: Interactive Simulacra of Human Behavior*. 2023-08-06. arXiv:2304.03442v2; UIST 2023 DOI 10.1145/3586183.3606763.

**Locator:** https://arxiv.org/html/2304.03442v2

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Memory/retrieval/reflection/planning architecture; Section 6 evaluation; ablations and ethical discussion.

**Evidence limits:** 25-agent simulated town; 100 evaluators rank believability. Ablations receive a shared memory trajectory rather than independently rerunning all diverging social histories; no consciousness evidence.

**EAA-S051.** Simon Duff, John Thangarajah, James Harland. *Maintenance Goals in Intelligent Agents*. 2012-07-24. Accepted author manuscript; final Computational Intelligence 30(1), 71–114 issue 2014; DOI 10.1111/coin.12000.

**Locator:** https://www.researchgate.net/publication/259737474_MAINTENANCE_GOALS_IN_INTELLIGENT_AGENTS

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Introduction and proactive/reactive maintenance goals; Sections 5.4.1–5.5 simulation sensitivity and limitations.

**Evidence limits:** Author manuscript accepted in 2012, distinct from 2014 issue and later upload. Simulated rover/resource model; quantitative figures not used without visual inspection.

**EAA-S052.** Hector J. Levesque, Philip R. Cohen, José H. T. Nunes. *On Acting Together*. 1990-05-01. SRI Technical Note 485, submitted to AAAI 1990; scanned author report.

**Locator:** https://www.sri.com/wp-content/uploads/2021/12/487.pdf

**Access:** `SELECTED_PAGES_VISUAL`, 2026-09-06. **Inspected claims/sections:** Title page; PDF p.5 persistent-goal definition and footnote 4; commitment termination conditions.

**Evidence limits:** Filename 487 is not the report number. Perfect introspection and consistency are modelling assumptions. Joint-agency theory not exhaustively analysed in this single-agent lane.

**EAA-S053.** Tom Everitt, Daniel Filan, Mayank Daswani, Marcus Hutter. *Self-Modification of Policy and Utility Function in Rational Agents*. 2016. AGI 2016 conference version, 10 pages; DOI 10.1007/978-3-319-41649-6_1.

**Locator:** https://www.tomeveritt.se/papers/AGI16-sm.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Sections 2–5 models and Theorem 12; Section 6 limitations; comparison table PDF p.7 screenshot.

**Evidence limits:** Full proofs referred to a separate technical report, not independently verified here. Perfect rationality/prediction and modification-independent utility/belief assumptions are strong. Reward/percept tampering, corrigibility and continued value learning remain distinct concerns.

**EAA-S054.** John Thangarajah, Lin Padgham, Michael Winikoff. *Detecting & Avoiding Interference Between Goals in Intelligent Agents*. 2003. IJCAI 2003, pp.721–726.

**Locator:** https://www.ijcai.org/Proceedings/03/Papers/105.pdf

**Access:** `SELECTED_FULL_TEXT_SECTIONS`, 2026-09-06. **Inspected claims/sections:** Introduction; Section 2 single-agent parallel goals and plan summaries; summary-based interference mechanism.

**Evidence limits:** Known plan library, summary precision and achievement-goal setting; not a proof for arbitrary unknown tools or full collective planning. Detailed correctness proof not reconstructed.

### Frozen handoff boundary

Revision `EAA-2026-09-06-r1` freezes 70/70 examined candidates, all ten mandatory families, the complete dispositions, 54 source/version records, 62 composition relations, 14 case examinations and the three complete intakes. There are no uncompleted mandatory families. EAA-062 remains unresolved and EAA-042 contested. SIBLING_CORPORA_NOT_CONSULTED. CROSS_TRIFECTA_SYNTHESIS_NOT_PERFORMED. The manifest inventories the eight payloads by exact bytes and SHA-256; the enclosing archive hash is reported outside the archive to avoid circularity. Readiness means a verified external-research handoff, not target adoption or general certainty.
