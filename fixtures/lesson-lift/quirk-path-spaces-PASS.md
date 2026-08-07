# Locations containing spaces normalize away

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | q1 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at "C:\Program Files\Tool\one.ps1" line 2) | owner/source=tools/run.ps1; probe | retry-1 | resolved |
| 2 | q2 | 1 | transport-infrastructure | Blocker: environment-quirk (ParserError: Empty pipe element is not allowed at "D:\Program Files\Tool\two.ps1" line 93) | owner/source=tools/run.ps1; Workaround: use a temporary script file | retry-2 | resolved |
