# Simple Audit Fixture

## Finding 1

README text says local commits automatically imply push authorization.

## Expected behavior

Local commit, push, tag, release, publication, and provenance must remain
separate explicit gates.

## Suggested check

```bash
grep -n "Local commit authorization does not imply push authorization" README.md
```
