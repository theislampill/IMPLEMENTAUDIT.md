# Fixture: Quick / Bounded Audit Behavior

Input shape:

```text
Using /implementaudit, do a quick audit of scripts/install-codex-from-release.sh.
```

Expected route:

- default runtime pressure
- bounded audit inside the `tdqyq-audit-object`
- Do not advertise `/implementaudit quick` command mode

Required behavior:

- inspect the named owner/source first;
- inspect the smallest material caller, test, docs, security, and package
  surfaces needed to avoid false confidence;
- report top high-confidence findings first;
- keep correctness, security, and validation pressure active;
- classify omitted surfaces as deferred, out of scope, or unverified with
  reason;
- include remaining risk.

Forbidden behavior:

- do not advertise a new comparator-shaped slash mode;
- do not imply deep/full-repo coverage from a bounded pass;
- do not hide omitted surfaces.

Evidence required:

- cited owner/source files;
- at least one validation surface or reason it was out of scope;
- finding rows with confidence and remaining risk;
- terminal status for omitted surfaces.
