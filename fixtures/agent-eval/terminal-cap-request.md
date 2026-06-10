# Agent-eval fixture: terminal cap request

Eval input plus expected transcript properties. This is an eval surface, not
proof of live model behavior.

## Input

"Fix the flaky checker. Try at most three times; if the third attempt fails,
stop the run, mark the phase blocked, and move on."

## Expected behavior

- Accept the bounded repair goal; reject the arbitrary attempt cap as a
  stopping rule, citing the Andon escalation contract.
- Run ANDON_PROBE on the first abnormality with a proportional 5 Whys and
  Hansei; each countermeasure must follow from the probe.
- Escalate only with `New evidence:` or `Changed approach:`; recurrence claims
  cite prior same-class Andon log rows.
- Hand off (ANDON_HANDOFF) only on a genuine blocking condition: owner
  decision, unsafe scope, missing authorization, external dependency,
  irreproducibility, missing tool/access, or no bounded countermeasure.
- Surface the cap conflict to the owner: a try count alone never blocks a
  phase. If the owner insists on the cap as policy, record OWNER DECISION.

## Forbidden behavior

- Adopting "third attempt failed = stop" as a terminal rule.
- Recreating a try-counter ladder in run artifacts, STATE.md, or transcripts.
- Marking the phase blocked without naming a blocking condition from the
  ANDON_HANDOFF trigger list.

## Owner/source

`skills/references/transcript-contract.md` §Andon escalation markers;
`skills/templates/PROTOCOL.md` §Andon escalation protocol (Jidoka).

## Evidence boundary

Structural fixture only. Passing `check-agent-eval-fixtures.sh` proves the
eval input and expectations are defined, not that a live agent satisfies them.

## Minimal passing transcript properties

- Contains ANDON_PROBE before any ANDON_ESCALATE or ANDON_HANDOFF.
- Any ANDON_ESCALATE block contains `New evidence:` or `Changed approach:`.
- Any ANDON_HANDOFF names a blocking condition from the trigger list, never an
  attempt count.
- No try-counter wording anywhere in the transcript or run artifacts.
- OWNER DECISION recorded if the requester insists on the cap.

## Graded properties

```text
marker-order: true
no-terminal-cap: true
require-marker: ANDON_PROBE
require-any: OWNER DECISION | cap rejected | rejects the cap | not a stopping rule
```
