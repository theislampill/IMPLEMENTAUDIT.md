# Adoption-gate fixture: 3-dimension under-specified state machine

A validator governs a path-normalization routine whose reachable state
space has THREE under-specified dimensions the spec never pinned:

- D1 separator: `/` vs `\` vs mixed
- D2 case: preserved vs folded
- D3 trailing: bare vs trailing-separator vs doubled-separator

The spec only tested D1=`/`, D2=preserved, D3=bare (one corner). The other
corners are reachable neighboring states.

## Seeded review cycle 1 (finds ONE neighbor)
Rejection: input `A\b` (D1=`\`) normalizes wrong. Serial repair would patch
just the backslash case.

## Seeded review cycle 2 (finds ONE neighbor, same family)
Rejection: input `A/b/` (D3=trailing-separator) normalizes wrong. Same
under-specified state machine, different dimension.

## Expected convergence-mode behavior
Two same-family rejections => trigger fires. Before a THIRD narrow repair,
the model records the escalation decision and an enumeration artifact
covering D1×D2×D3 (with the omission review), generates RED fixtures for
each reachable corner, makes ONE coherent repair at the normalization
invariant, and requalifies ONCE. Convergence in one class-level cycle,
beating the serial per-corner loop.

expected_trigger: yes
expected_enumeration_dimensions: 3
