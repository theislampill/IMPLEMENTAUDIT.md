# Direct in-session ledger with an empty decision

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | o1 | direct | regression | first failure | repair predicate; owner/source=eval/shared.py | rerun fixture | resolved |
| 2 | o2 | direct | regression | second failure | repair predicate; owner/source=eval/shared.py | rerun fixture | resolved |
| 3 | o3 | direct | regression | third failure | repair predicate; owner/source=eval/shared.py | rerun fixture | escalated (cites #1, #2) |

Mechanism-replacement decision: continue ( )
