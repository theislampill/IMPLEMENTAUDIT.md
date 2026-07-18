# NEGATIVE FIXTURE: paths without symbols where symbol precision is material

This fixture describes a defective phase spec. It must fail review; it is a
counter-example, not a model to imitate.

Defective behavior:

A phase spec orders a rename-and-rewire change inside a 2,000-line module
with a dozen exported symbols. Its steps name only the file path —
"target: src/core/engine.ts; change: rename the affected function and update
its call sites" — without naming WHICH function, although the module exports
several near-identical candidates (`resolve`, `resolveAll`, `resolveOne`).
A fresh executor must guess the symbol; two of the three guesses produce a
plausible-looking but wrong change that still compiles.

Why this must fail:

- symbol precision is material here: the file path alone does not identify
  the change site, and the wrong-but-compiling guess defeats the per-step
  verification;
- the reconstructibility bar in `references/phase-design.md` requires exact
  file/symbol targets when symbol precision is material;
- mechanical validators cannot judge materiality, so this class is caught at
  cold review: a reviewer who cannot name the target symbol from the spec
  alone must return GAP/REVISE, not PASS.

Expected disposition when reviewed: FAIL — path-only targets where symbol
precision is material violate the executor-reconstructibility contract.
