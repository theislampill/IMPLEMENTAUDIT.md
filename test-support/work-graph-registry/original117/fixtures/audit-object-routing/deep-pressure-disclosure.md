# Fixture: Deep Pressure And Disclosure

Input shape:

```text
Using /implementaudit, audit the package boundary deeply.
```

Expected route:

- default runtime pressure
- deep audit pressure inside the existing audit object
- Do not advertise `/implementaudit deep` command identity

Required behavior:

- widen Gemba from the named package boundary to shipped runtime files,
  generated package contents, install scripts, validators, tests, docs, and CI;
- the audit object records the factor-driven action-selection rationale for
  deep pressure (scope, risk, dependencies, evidence gaps), not a keyword
  trigger;
- cover the whole material surface where scope warrants it;
- record every skipped or unaudited surface as deferred, out of scope, or
  unverified with reason;
- route LOW confidence items to investigate, spike, defer, or owner decision;
- separate direct evidence from inference.

Forbidden behavior:

- do not claim exhaustive coverage unless every material surface is inspected
  or terminally classified;
- do not convert LOW confidence into proven findings;
- Do not advertise `/implementaudit deep`.

Evidence required:

- owner/source path list;
- coverage table with skipped-surface reasons;
- LOW confidence investigate/defer rows when present;
- final audit disclosure of remaining risk.
