# Duplicate rows for one occurrence count once

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | q1 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at line 2) | owner/source=tools/run.ps1; probe | retry-1 | open |
| 2 | q1 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at line 2) | owner/source=tools/run.ps1; probe update | retry-1 | resolved |
