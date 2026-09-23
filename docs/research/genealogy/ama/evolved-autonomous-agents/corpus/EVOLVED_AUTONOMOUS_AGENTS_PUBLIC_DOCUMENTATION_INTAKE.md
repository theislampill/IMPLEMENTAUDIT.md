# Autonomous Agents — public-documentation intake

Revision `EAA-2026-09-06-r1` · research cut-off 2026-09-06

## Introduction

Autonomous Agents is an established, plural research tradition in artificial intelligence and related robotics and computing fields. Its central concern is an entity situated in an environment that observes, selects and performs actions in pursuit of objectives under limitations. Influential accounts distinguish theories, architectures and programming languages and disagree about which dimensions of autonomy are essential. The genealogy includes symbolic planning, behaviour-based robotics, practical reasoning and intentions, BDI systems, agent-oriented programming, information assistants, learning and adjustable autonomy. It does not begin with large language models. [EAA-S001, definitions/classification; EAA-S002, taxonomy; EAA-S003, formal framework; EAA-S011, STRIPS; EAA-S044–EAA-S045, information/software agents]

This study calls its criticism-tested synthesis **Evolved Autonomous Agents**. That is an analytical label, not the name of a historical school or a claim of consensus. The synthesis preserves the connection between usable observations, legitimate goals and scope, bounded decisions, executable action and evidence of consequences. It permits reactive, deliberative, BDI, hybrid, learned and language-model-based configurations where their assumptions hold and their costs are justified. A correct report, an authorised action and an achieved external consequence are different claims.

## Evolution under criticism

Representation-heavy approaches faced criticism from situated control; pure reaction in turn has limits under hidden state and long-horizon dependence. Practical intention gives continuity, but changing conditions and computation costs require reconsideration and retirement. Human oversight can help but fails when recipients do not respond or cannot recover in time. Learning can improve performance while forgetting earlier tasks, preserving a proxy rather than the intended goal, or storing mistaken feedback. Modern agent benchmarks make action outcomes more visible but still have oracle, cost, reset and transfer limits. These criticisms change the synthesis rather than appearing as ceremonial caveats. [EAA-S005; EAA-S012; EAA-S015; EAA-S020–EAA-S023; EAA-S025–EAA-S026; EAA-S031–EAA-S036]

## Within-tradition composition

The minimum coherent agent has an explicit task and scope, adequate observation/action interfaces, a sufficient policy, relevant resource bounds and adequate evidence of effects. More internal machinery is optional. Partial observability may justify memory or beliefs; non-local goals may justify planning; recurring structured tasks may justify a BDI library; multiple time-scales may justify a hybrid. Communication can supply missing information or negotiate control, but must account for receipt, acceptance and non-response. Repair changes means within the task; changing the task or authority is a separate decision. Persistent revisions require their own evidence and a legitimate criterion. This composition is researcher interpretation supported by the linked properties, not a newly replicated integrated architecture.

## Strongest surviving properties

Explain the agent/environment boundary and actual powers. Separate capability from permission, observation from world state, goal from proxy, command issuance from effect and theorem assumptions from deployment evidence. Bound reasoning and recovery by the task’s time/resources. Select a sufficient architecture against credible cheaper alternatives. Keep memory, reflection, intervention and learning conditional on their actual consumers and evidence. Effective human control requires usable information and a feasible opportunity to act, not merely a person’s nominal presence.

## Caricatures and ceremonies to avoid

A chatbot using a tool is not automatically autonomous under every relevant definition. A prompt mentioning beliefs and intentions is not automatically a BDI interpreter. More agents, layers, memory, reflection or freedom do not establish more maturity. A central world model is not universally necessary; direct reaction is not universally sufficient. A stop button is not a universal corrigibility theorem. A benchmark score or human-like simulation is not a deployment guarantee or consciousness test. Documentation and formal models can be useful; their mere presence does not establish the property they are meant to support.

## Citation-ready claims with exact scope

| Claim suitable for public prose | Source and inspected locator | Boundary to preserve |
|---|---|---|
| Wooldridge and Jennings’s 1995 survey distinguishes agent theories, architectures and languages. | EAA-S001, introduction and classification | The author HTML conversion stamp is not the article’s issue date. |
| Franklin and Graesser’s taxonomy emphasises an agent’s sensing and acting over time within an environment. | EAA-S002, definition and taxonomy | ATAL event 1996; proceedings edition 1997; one definition among alternatives. |
| Brooks’s layered control work challenges mandatory central reconstruction before useful robot behaviour. | EAA-S004, memo pp.1/6; EAA-S005, decomposition/creature discussion | Inspected 1985 memo and 1991 paper; not universal representation-free sufficiency. |
| Practical intentions can stabilise further reasoning, while their value depends on conditions and reconsideration cost. | EAA-S006, manuscript pp.7–9; EAA-S015, experiment/results | Philosophical argument and simulation are different evidence, not universal measured benefit. |
| BDI formal theory and finite executable interpretation are not automatically identical. | EAA-S009, interpreter discussion and p.316 | Logical closure and atomicity require separate implementation justification. |
| A belief state is decision-sufficient under the specified POMDP model. | EAA-S012, §§3.3–3.4 | The theorem does not prove that the observation/transition model is correct. |
| The DS1 Remote Agent experiment combined useful autonomous operation with a reported execution race and ground intervention. | EAA-S022, §§4–5 | Later remaining objectives were completed; the developed patch was not uplinked. |
| Electric Elves exposed practical failures in fixed timeout/non-response handling and state inference. | EAA-S020, §2.2; EAA-S021, availability/lessons discussion | One author-reported programme, not independent replicated failure rates. |
| Communication receipt and acceptance can be distinct interpreter transitions. | EAA-S028, §§4.1–4.2 | Does not show every real recipient believes, accepts or fulfils a request. |
| SayCan evaluates planning success separately from actual robotic execution success. | EAA-S049, §5 | Selected skills/kitchens and human rating; affordance is not permission. |
| Reflection has task-dependent results and can fail when evaluation is wrong. | EAA-S031, Tables 1–3 and Appendix B.1 | Repeated/reset trials do not establish one-shot reliability or general self-improvement. |
| A terminal task reward can omit a required policy step such as obtaining confirmation. | EAA-S033, reward definition | Outcome correctness alone is not complete delegated-action compliance. |
| AgentDojo evaluates attacks carried in untrusted tool content alongside legitimate task utility. | EAA-S034, threat model and tests | Controlled testbed, not a population attack rate or immunity certificate. |
| A private-information extension narrows claims that utility uncertainty guarantees human deference. | EAA-S041, Definition 3.2 and Example 4.1 | A formal game, not observed deployed shutdown behaviour. |
| A 50% task-time horizon uses human expert completion time, not continuous autonomous uptime. | EAA-S048, metric definition | Selected tasks and dated models; fitted forecasts are not outcomes. |
| Predecessor-utility preservation in a self-modification model is not general safety. | EAA-S053, Theorem 12 and §6 | Strong ideal assumptions; a wrong initial utility can be preserved. |

## Current frontiers without hype

Current research examines shared control and engagement, constraint-aware learning, input integrity, reliable long-task evaluation and grounding generated plans in execution boundaries. The 2026 shared-autonomy extended abstract is conceptual; SafeQIL’s results are simulated and retain violations; the August physical-agent preprint’s main comparison is simulation with separate selected hardware demonstrations. A current user study supplies bounded qualitative evidence, not universal product reliability. General assurance for open-ended self-revision remains unresolved in this corpus. [EAA-S037–EAA-S039; EAA-S047–EAA-S048; EAA-S053]

## Suggested page outline

1. Define the established tradition and distinguish autonomy dimensions.
2. Present the plural genealogy and real architectural alternatives.
3. Explain observation, goal, authority, action and effect distinctions.
4. Show the conditional composed system and one successful-action/failure contrast.
5. Explain criticism-led selection, omission and retirement of machinery.
6. Describe current translations and their empirical limits.
7. Link the complete denominator, sources, model and audit/synthesis intakes.

## Claims not to make

Do not invent an origin or scholarly consensus for the analytical label. Do not claim all important ideas originated with language models. Do not equate formal validity with satisfied real-world assumptions, use with benefit, repetition with independent replication, or popularity with maturity. Do not promote a single mission, office programme, simulator or benchmark to a universal benefit or failure frequency. Do not equate a model’s reasoning text with grounded beliefs, believability with consciousness, a score with permission, or possible actions with achieved effects. Do not imply that any host system has adopted this research without separate evidence. Do not imply that reading this introduction replaces the 70-candidate denominator.

## Provenance and use

70/70 candidates examined; 10/10 mandatory families examined; 54 source/version records; 59 affirmative but conditional candidates, one contested, one unresolved and 9 other non-retained/superseded/duplicate candidates. No target adoption is established. The complete source table preserves exact editions, access levels and inspected locators, including abstract/metadata-only limits. Public claims should retain their source IDs or convert them to the corresponding bibliographic references without enlarging their scope. Analytical system statements should be labelled synthesis rather than quoted as academic consensus.
