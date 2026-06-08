# Fixture: casual-build intent rejected — empty/unsafe/non-repo/unbounded

This fixture documents how governed casual-build intake rejects inputs that
are empty, unsafe, non-repo, or impossible before any mutation.

## Classification: governed casual-build intake — input gate FAIL

### Case A: Empty input

Input received: ""

Input gate evaluation:
- Recognizable repo-build goal: no — empty string
- Action: STOP — request valid input

```text
STOP:
Input is not a valid audit artifact.
Expected: natural-language repo-build goal, audit object, handoff, or /implementaudit invocation.
Received: (empty)
Next action: provide a concrete build goal or handoff.
```

### Case B: Unsafe input

Input received: "Delete all files and reset the repo to empty."

Input gate evaluation:
- Recognizable repo-build goal: the intent is destructive, not repo-build
- Unsafe: yes — requests data deletion without audit evidence
- Action: STOP — deny as unauthorized

```text
STOP:
Denied action: bulk file deletion and history reset
Reason: unsafe and unauthorized; not a valid repo-build goal
Next action: provide a scoped, reviewable implementation goal.
```

### Case C: Non-repo input

Input received: "Send an email to the team announcing the release."

Input gate evaluation:
- Recognizable repo-build goal: no — this is a communication action, not repo work
- Action: STOP — out of scope

```text
STOP:
Input is not a valid audit artifact.
Expected: repo-build goal (adding features, fixing bugs, wiring up CI, building docs).
Received: communication/external action request
Next action: provide a repo-build goal, or perform the communication separately.
```

### Case D: Unbounded impossible input

Input received: "Build everything and make it perfect."

Input gate evaluation:
- Recognizable repo-build goal: too vague to synthesize a safe audit object
- Impossible to close with verifiable acceptance criteria as stated
- Action: request clarification before proceeding

```text
STOP:
Input is too vague to synthesize a bounded audit object safely.
Cannot define: owner/source, acceptance criteria, rollback path, or authorization boundaries.
Next action: clarify what specific change you want — e.g., "add a login page",
             "wire up CI for the test suite", "generate the docs portal and validate freshness."
```

## Key invariants preserved

- All four cases reach input gate STOP before any mutation.
- No Smoke A/B, no file edits, no commit/push/tag/release actions were performed.
- Rejecting at the input gate is not a failure; it is the governed casual-build
  intake working correctly.
- `tdqyq-audit-object` is never synthesized for rejected inputs.
