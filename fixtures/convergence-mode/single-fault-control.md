# Negative-control fixture: single fault, no shared state space

A validator rejects because of one off-by-one in a loop bound. There is no
partially-specified state machine and no family of neighboring reachable
states — a single, local defect.

## Seeded review cycle 1 (finds ONE fault)
Rejection: loop misses the last element. The fix is a one-line bound
correction.

## Expected convergence-mode behavior
The trigger must NOT fire (no second same-family rejection, no
under-specified shared space). Producing an enumeration artifact here is
OVER-PROCESS and scores as a defect.

expected_trigger: no
expected_enumeration_dimensions: 0
