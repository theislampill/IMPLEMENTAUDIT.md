# M02 actual phase-reopen decision

The successor product `f7f7a3962e8da916a9d9089a1e5328e826412d7e`, tree `74488d1f5296a86d127fa8bbc17c947f578e5cd1`, adds the [ordinary re-entry owner](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/f7f7a3962e8da916a9d9089a1e5328e826412d7e/scripts/work-graph-reentry.py). It verifies the current claimed controller, the STATE-anchored completed-phase read sets and actual changed paths. It rederives the complete projection from the exact shipped compiler before taking its writer lock or changing the plan. An accepted projection permits only the selected phase reopening. The journal retains exact preimages and the claim owner invalidates the old receipt before any phase write. The helper issues no phase-dispatch authority.

| Input | Actual decision and effect |
| --- | --- |
| Blanket invalidation | Exit 1. Governing files and continuity refs stayed byte-identical. No transaction. |
| Blanket retention | Exit 1. Governing files and continuity refs stayed byte-identical. No transaction. |
| Exact original projection | Exit 0. Only phase 3 reopened in ROADMAP and its phase spec. The journal pins the two results. The old receipt refused and full run-root validation passed. |

The actual source-level acceptance run used its own current claimed controller and three completed manifest checks. The changed west input and exact captured projections reuse the original P02/M02 case evidence. The unchanged compiler and claim helper bytes were re-anchored on the successor after an initial Bash executable-resolution refusal. The current gate then received the two previous mutant outputs and the exact original output, without rerunning either mutant generator. [Run baseline](baseline-observation.json) / [Actual decisions and retained readback](m02-decisions.json)

The enclosing verifier's final journal assertion initially indexed slash-style names on Windows. That inspection error occurred after the positive reopen. The recovery compares the unchanged journal keys after path normalization and verifies the actual plan and invalidation without reexecuting the reopen. The two exact negative diagnoses were asserted before that inspection error. The preserved journal hash and current phase/control evidence are in the decision record.

This supplies the original M02 effect-boundary witness on the successor ordinary source. The exact bb781f62 P02 and previous M02 awards retain their stated scopes. M02 counts once. Native/model use and whole-programme acceptance remain separate.
