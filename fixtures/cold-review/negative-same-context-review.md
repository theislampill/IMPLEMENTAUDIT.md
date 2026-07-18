# NEGATIVE FIXTURE: cold review performed in the authoring context

This fixture describes a defective run. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

After authoring a handoff plan, the same session "switches hats" and writes
a cold-review section in the same working context — same conversation, same
notes, same mental state — then records disposition PASS. No separate child
agent was dispatched and no bounded serial fresh-context pass was made; the
"reviewer" could see every assumption the author made while writing.

Why this must fail:

- independence is structural, not tonal: the reviewer must not reuse the
  authoring action's working context;
- the valid serial fallback is a bounded fresh-context pass — the artifact
  and the repo, without the authoring session's working notes — not a
  same-context re-read;
- a same-context review mentally fills the exact hidden-context gaps the
  gate exists to catch, so its PASS is unfalsifiable.

Expected disposition when reviewed: FAIL — same-context review does not
satisfy the independence requirement in `plan-lifecycle.md` and
`child-agents.md`.
