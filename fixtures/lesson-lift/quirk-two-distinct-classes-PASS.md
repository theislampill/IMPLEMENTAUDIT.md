# Distinct signatures do not trigger memoization

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | q1 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at line 2) | owner/source=tools/run.ps1; probe | retry-1 | resolved |
| 2 | q2 | 1 | transport-infrastructure | Blocker: environment-quirk (UnicodeEncodeError: charmap codec cannot encode character at line 3) | owner/source=tools/run.py; probe | retry-2 | resolved |
