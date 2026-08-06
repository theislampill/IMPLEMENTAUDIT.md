IMPLEMENTAUDIT_RESPEC_IMPACT_SET
Change: <old value -> new value>
Declared by: <owner message ref or plan step>
Population size: <deduplicated carrier count>
Enumeration method: literal + stem/dirname
Literal carriers: <deduplicated literal-search output or none>
Literal count: <count>
Stem/dirname additional carriers: <additional carriers found only by stem/dirname search or none>
Stem/dirname additional count: <count>
Replacement: <yes | no>
Replacement path: <repo-relative inspectable replacement path | none>

| # | Carrier | Kind | Status | Evidence |
|---|---|---|---|---|
| 1 | <path or external object> | <code/doc/memory/issue/milestone/manifest> | <applied/out-of-scope(reason)/deferred(disposition: ref)/owner-assigned> | <command and diff/object ref> |

## Invariants carried forward

Required only when `Replacement: yes`. Derive the list from validators and
harnesses that the prior file satisfied.

| # | Invariant | Enforced by | Present in replacement? | Evidence |
|---|---|---|---|---|
| 1 | <load-bearing marker or behavior> | <validator/test> | <yes> | contains:<literal marker proved in replacement> |
