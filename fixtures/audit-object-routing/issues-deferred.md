# Fixture: Native Compatibility Issue Publication Deferred

Classification: deferred behavior for v0.3.0.0.

Allowed:

- Produce issue-ready rows inside the audit object.
- Mark issue publication as deferred or not applicable.
- State the future owner gate required before publication.

Forbidden:

- Forbidden: create GitHub issues.
- Publish to a tracker.
- Claim issue creation happened.
- Treat `--issues` as an implemented publication mode.

Future gate requirements:

- explicit authorization
- destination
- title policy
- body policy
- duplicate check
- readback evidence
