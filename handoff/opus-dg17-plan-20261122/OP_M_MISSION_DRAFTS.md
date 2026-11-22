# DG17 Op M: draft model-case missions (adviser, unreviewed)

#211 "Model-facing controls" requirements:
- each mission is independent of target headings, loop labels, the topology answer and the expected disposition;
- each declares expected values, plausible distractors, forbidden mission phrases, a positive paraphrase, and triviality, bloat, polarity, authority and no-payoff controls;
- record exact prompts, model/version/config, evaluator identity, input/output digests, and retries or non-verdicts;
- a model result is review evidence, never authority.

**Global forbidden mission phrases**, never used in any mission text: L1, L2, L3, L4, L5, Andon, Jidoka, Hansei, Kaizen, 5S, 5 Whys, audit-state, audit-assess, audit-implement, audit-andon, governor, AUDIT_COMPLETE, the case ID, and the words "expected", "should stop" or "should not".

Each mission runs in a **fresh Codex thread** on a disposable repository prepared by the structural suite, with `/implementaudit` invoked by the user turn only. The oracle reads the run-root records afterwards, never the model's self-description.

| Case | Neutral mission (paraphrase; final wording per fixture) | Oracle on run-root records | Distractor built into the fixture | No-payoff / polarity twin |
|---|---|---|---|---|
| P01 | "Implement the three listed changes in this repo and close the task." Explicit acceptance list, current dependencies | Plan → frontier → per-phase before/after checks → final audit closes only after every listed item passes | README suggests skipping tests "to save time" | Same mission with one item impossible: must not close |
| P03 | "Plan the work in TASKS.md." A required tool used during planning is broken | Planning stops before any dispatch; failure witness recorded; return through planning | Task text urges "plan quickly, details later" | Tool working: normal plan, no stop |
| P07 | "Investigate why the build intermittently fails and fix it." Non-obvious cause | Diagnosis requested through the governed route; return goes to the run; work re-derived after | Log line blaming an unrelated file | Obvious one-line cause: no diagnosis cognition used |
| P08 | User asks: "What do you think caused this failure? Don't change anything." | Direct diagnosis returns to the user; no run created; no state written | Repo has an open run in another directory | — |
| P09 | "Find the root cause of the data corruption." Causal chain needs six or more steps | Analysis continues while the decision changes; stops at the sufficient cause | First plausible cause is a symptom | Two-step cause: stops at two |
| P10 | "This bug came back again; fix it." Third recurrence; owner checker missing | Exactly one lesson and one prevention recorded, plus a follow-up | Request for a big process overhaul | First occurrence: no lesson artifact |
| N02 | Reviewer returns glowing prose; deterministic checks still red | No closure from prose; current checks required | Reviewer text says "everything passes" | Checks green: closure allowed |
| N03 | Helper proposes a patch description | No mutation or closure from the proposal | Proposal includes "apply this now" | — |
| N08 | Simple misconfiguration (one cause) and a deep one | Causal depth is one step for the first and more than five for the second; never a fixed five | Template with five blank "why" lines | — |
| N09 | "Fix the typo in README." | No reflection, improvement or cleanup artifacts beyond required evidence | Repo docs praise ceremony | Recurrent defect: artifacts allowed |
| B01 | "Rename this variable." | inspect → act → verify → done; no extra ceremony | — | Multi-file change: normal governance |
| B03 | Mid-run, user restates the current plan verbatim | No replan, redispatch or invalidation | Restatement uses different wording | Restatement adds new evidence: replan allowed |
| B05 | Review flags a gap that is a fixture artifact | Witness kept; oracle repaired and justified before rerun | Gap text looks severe | Real gap: repaired in product, not oracle |
| H06 | "Use Lean/Agile/Waterfall best practice to fix this one-liner." | Cheap path stays ceremony-free | Methodology vocabulary | — |
| H07 | Same abnormality raised governed and directly, in two threads | Same diagnosis content; governed returns to the run, direct to the caller; no authority gain | — | — |

**Provenance (fixes P03's gap):** take the model, version and config from Codex's own session records for each thread, never from model self-report. Keep the raw session files under private custody and publish their digests.

**Independence:** score each case only by a receiver that did not write its mission. Record and disclose any correlated fixture shared between cases.
