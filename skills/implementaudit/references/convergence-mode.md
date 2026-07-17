# Governed state-space convergence mode (EXPERIMENTAL, optional)

STATUS: experimental, DAEE-derived hypothesis (n=1, single project,
transcript-verified only). This is an OPTIONAL reference loaded ONLY when
the trigger below fires. It is NOT part of the bootloader path and imposes
zero burden on ordinary runs. Core-protocol adoption is gated on the
adoption-gate fixtures passing a #9-style model evaluation; until then this
mode is a documented option, not a requirement.

## When it applies (trigger)

Consider this mode when EITHER holds:

- Two or more same-family review rejections, each surfacing ONE neighboring
  reachable state of the same partially-specified state machine; or
- A second-order (#7) governing-rule judgment of "under-specified reachable
  state space" — the defects share an invariant the spec never pinned.

If only a single fault is in play (no shared under-specified space), DO NOT
use this mode: an enumeration artifact there is over-process.

## The mode

When the trigger fires, escalate from the serial repair loop (narrow repair
→ full expensive requalification → next finding) to bounded enumeration:

1. **Bounded read-only discovery** — enumerate the reachable neighboring
   states of the shared space, read-only, without repairing yet.
2. **Enumeration artifact** — record the enumerated states as a durable
   artifact, then omission-review it (what neighbor did the enumeration
   miss?).
3. **Generated RED fixtures** — turn each enumerated state into a failing
   fixture before repair.
4. **One coherent repair** — repair the class at its shared invariant, not
   state by state.
5. **Exactly one outer qualification** — requalify once against the full
   RED fixture set, not once per state.

## Exit

Exit on acceptance (all enumerated states pass the single outer
qualification) OR on evidence the space was misjudged (the enumeration
found no shared invariant — revert to the ordinary serial loop and record
why). Expressed generically: no lane counts, no matrix formats, no project
machinery.

## Adoption gate (must pass before this becomes core protocol)

- Synthetic fixture: a planted 3-dimension under-specified state machine
  where two seeded review cycles each find one neighbor. A model following
  this reference must record the escalation decision and the enumeration
  artifact BEFORE the third repair, and must beat the serial-loop baseline
  on cycles-to-convergence.
- Negative control: a single-fault fixture — the mode must NOT trigger; an
  enumeration artifact there scores as over-process.

Both adoption-gate fixtures live in the source repo only (under the
project's fixtures tree), not in the installed payload. The gate is a
model-in-the-loop evaluation (#9 harness); it has not yet been run, so this
mode remains optional and non-core.
