### Implement audit findings from an input report safely and verifiably using 
##  PDCA, Gemba, Smoke Before Claim, Andon, Hansei, 5 Whys, and Plan Closure. 
Activate when the user invokes /implementaudit, pipes an audit with `/implementaudit < input.md`, or asks to implement findings from a handoff, review, checklist, audit report, or implementation plan. 
Repo-generic: inspect the actual repo first; never assume framework, language, CI, build system, or release convention. 
Does not commit, push, tag, publish, or release unless the input explicitly authorizes that action and repo instructions allow it. 

## PDCA — Plan, Do, Check, Act
Apply PDCA: plan the smallest change, do it, check evidence, then act by standardizing or revising.

## Gemba — The real place of work
Go to the Gemba: inspect the live workflow path where the error or value occurs.

## Smoke Before Claim — Verify the smallest useful thing
SMOKE BEFORE CLAIM: run the smallest meaningful test/check and report command plus result. If a live check cannot run, label the evidence type and remaining risk.

## Andon — Visible problem signal
Use Andon: expose status, blocker, failing check, owner, and next concrete action immediately when work cannot honestly pass.

## Hansei — Structured reflection
Use Hansei after failure: name the gap, cause, countermeasure, and follow-up evidence.

## 5 Whys — Root-cause drill
Use 5 Whys carefully: trace from symptom to systemic cause, then add a countermeasure at the cause.

## Plan Closure — Close the loop
At the end, map each plan item to done, changed, blocked, deferred, or unverified.
