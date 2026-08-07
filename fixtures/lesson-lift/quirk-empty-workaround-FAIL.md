# Empty workaround is not a durable remedy

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | q1 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at line 2) | owner/source=tools/run.ps1; probe | retry-1 | resolved |
| 2 | q2 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at line 93) | owner/source=tools/run.ps1; Workaround: | retry-2 | resolved |
