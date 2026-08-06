# Direct ledger with duplicated rows for one occurrence

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | o1 | direct | regression | first row | repair predicate; owner/source=eval/shared.py | rerun fixture | resolved |
| 2 | o1 | direct | regression | duplicate row | repair predicate; owner/source=eval/shared.py | rerun fixture | resolved |
| 3 | o2 | direct | regression | second occurrence | repair predicate; owner/source=eval/shared.py | rerun fixture | resolved |
