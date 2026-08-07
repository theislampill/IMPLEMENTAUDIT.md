# One error signature can have different workaround spellings

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | q1 | 1 | transport-infrastructure | Blocker: environment-quirk (UnicodeEncodeError: charmap codec can't encode characters at C:\work\one.py line 18) | owner/source=tools/run.py; Workaround: set process encoding | retry-1 | resolved |
| 2 | q2 | 1 | transport-infrastructure | Blocker: environment-quirk (UnicodeEncodeError: charmap codec can't encode characters at D:\lane\two.py line 921) | owner/source=tools/run.py; Workaround: select UTF-8 mode | retry-2 | resolved |
