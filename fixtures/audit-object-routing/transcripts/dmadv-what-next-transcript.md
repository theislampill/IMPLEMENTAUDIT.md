# Transcript Fixture: DMADV What Next

AUDIT_START

Input:

```text
Using /implementaudit, what next should this repo build?
```

Expected route:

- DMADV direction/design
- separated from defects
- spike / phase / defer / reject or owner decision

Evidence row:

| Field | Value |
|---|---|
| Direction question | repo-grounded future capability |
| Source evidence | README, CHANGELOG, AGENTS, validators, package boundary |
| Alternatives | grounded design candidates |
| Selected outcome | spike / phase / defer / reject |

Forbidden behavior:

- Do not advertise `/implementaudit next`, `/implementaudit features`, or `/implementaudit roadmap`.
- Do not return generic roadmap prose.

AUDIT_VERIFY

Expected close: each candidate has owner/source, acceptance, risk,
verification, rollback, and route label.
