# Verify-Package Shadow Keep-Going and Resume Design

## Status and authority

This design governs an isolated engineering experiment based on
`62507de00e16cc2ada0e7546273988c387a20390` in worktree
`C:\workspace\ai\improveimplementaudit\IMPLEMENTAUDIT-verify-package-shadow-resume`
on branch `experiment/verify-package-shadow-resume`.

The product is a non-authoritative shadow verifier. It does not replace
`scripts/verify-package.sh`, modify the active Thread6.10 campaign, launch or
qualify HBASE, install a plugin, merge, tag, release, publish, or claim package
authority.

```text
SHADOW_MODE_AUTHORITY=NONE
CANONICAL_VERIFY_PACKAGE_REMAINS_ORACLE=YES
SAFE_FOR_AUTHORITATIVE_USE=NO_BY_DEFAULT
```

## Current verifier architecture

The canonical verifier is a 780-line `set -euo pipefail` Bash program. It has a
large inline preflight followed by 104 top-level Bash invocations: 24 checker
scripts, 78 registered shell tests, `scripts/check-validation-registry.sh`, and
`scripts/build-release-asset.sh --check`. The registry meta-gate proves that
all 78 `tests/*.test.sh` files are invoked exactly once and CI invokes the
canonical verifier exactly once.

The current list order is not a dependency graph. Most tests create and clean
their own temporary fixtures and do not consume prior check output. The
rendered README diagram check has a real generated-parity prerequisite because
it invokes and requires `generate-readme-diagrams.sh --check` before rendering.
Required inputs and material tools are prerequisites of the checks that use
them, not controller-wide serialisation edges. Fixed `/tmp` names and process
fixtures make parallel execution unsafe without a separate resource analysis,
so the first shadow scheduler is serial, deterministic, and keep-going.

## Strangler boundary

The canonical verifier remains byte-for-byte available as the oracle. The
shadow implementation adds:

```text
scripts/verify-package-shadow.py
scripts/verify-package-shadow-registry.json
tests/verify_package_shadow_test.py
tests/fixtures/verify-package-shadow/
```

The large inline preflight is one approved composite check. Its exact canonical
source range and command population are digest-bound. The shadow registry is
rejected as infrastructure-invalid when the canonical script digest, composite
boundary anchors, or extracted top-level command population no longer matches.
This prevents a stale shadow registry from silently omitting canonical checks.

## Check model and dependency rules

Every check has a stable ID, logical order, exact argv, dependencies,
applicability contract, material tools, implementation sources, and input
contract. A dependency edge is admitted only when a downstream result cannot
be trustworthy without an upstream PASS.

Initial hard result edge:

```text
script.generate-readme-diagrams
  -> script.verify-readme-diagrams-rendered
```

All other initial command nodes are independent unless their own declared
contract proves otherwise. Shared inputs, duplicated coverage, or later list
position are not result dependencies.

The composite inline preflight may fail without suppressing independent command
nodes. A missing material tool is classified before process execution as an
infrastructure error. Process-start failure, timeout, malformed registry, or
malformed checkpoint is also infrastructure failure. A completed check process
with a non-zero product-verification result is FAIL.

## Keep-going execution

The engine validates the registry, walks nodes in stable logical order, and
executes ready nodes serially. A failed node blocks only descendants connected
by explicit result dependencies. Independent nodes continue.

Terminal status vocabulary:

```text
PASS
FAIL
BLOCKED_BY_FAILED_DEPENDENCY
SKIPPED_NOT_APPLICABLE
INFRASTRUCTURE_ERROR
```

The JSON report records the run identity, mode, exact candidate identity,
ordered check records, passes, primary failures, blocked checks and causes,
infrastructure errors, checkpoint decisions, earliest failure, whether the
safe frontier is complete, timing/work counters, and `authority: "NONE"`.
Human output is a deterministic compact projection of the JSON.

Milestone 1 freezes after tests prove registry drift detection, deterministic
ordering, independent execution after failure, genuine blocking, distinct
infrastructure errors, multiple failures in one pass, and oracle non-suppression.

## Checkpoint validity contract

Only PASS is reusable. Each checkpoint record binds:

- schema and engine-semantics version;
- registry digest and check ID;
- exact argv and implementation-source digest;
- canonical candidate identity where the check declares it material;
- declared input manifest with path kind, mode, size, and SHA-256/tree digest;
- dependency PASS fingerprints;
- applicability fingerprint;
- allowlisted material environment values;
- resolved material tool identity and version output;
- execution-mode semantics;
- complete terminal record and canonical JSON fingerprint.

Reuse occurs only when the current recomputed fingerprint exactly equals the
stored PASS fingerprint. Corrupt, incomplete, unknown, or incompatible state
reruns. A changed dependency PASS invalidates descendants. A changed unrelated
file preserves a checkpoint only for a reviewed explicit input contract.
Unaudited checks use a conservative tracked-tree contract, preserving soundness
at the cost of reuse.

Checkpoint files are written atomically to a caller-selected directory and are
not tracked. The report explains each reuse or invalidation decision.

## Equivalence and performance

Synthetic fixtures provide deterministic fast tests for scheduler and
checkpoint semantics. Representative current verifier commands provide local
integration evidence. Oracle comparison runs the canonical verifier and the
shadow verifier over the same controlled clean and failing candidates; the
shadow may discover more independent failures but must not suppress a failure
that the canonical run reaches.

Resume equivalence compares fresh and resumed semantic terminal results over
the same candidate. Performance evidence records fresh, keep-going, and resumed
wall time; executed and reused counts; invalidation counts and reasons;
checkpoint-validation overhead; and primary failures discovered per run.

## Acceptance and stopping boundary

The experiment stops with an unmerged, uninstalled worktree containing source,
tests, measurements, review notes, and a compact engineering handoff. It is
safe for non-authoritative shadow use only if the fail-closed, equivalence, and
residue controls pass. Any future canonical or authoritative admission requires
a separate owner decision.
