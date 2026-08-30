# Verify-Package Shadow Checkpoint/Resume Functional Milestone

```text
MILESTONE=CHECKPOINT_RESUME_FUNCTIONAL
STATUS=PASS
AUTHORITY=NONE
SAFE_FOR_AUTHORITATIVE_USE=NO_BY_DEFAULT
BASE_HEAD=62507de00e16cc2ada0e7546273988c387a20390
```

## Product identity

```text
ENGINE=scripts/verify-package-shadow.py
ENGINE_BYTES=46386
ENGINE_SHA256=1b0e8cdcc6e47b51afa31b86e4a715da548cecd63d46e1ef8dfec01085f6f9fd
REGISTRY=scripts/verify-package-shadow-registry.json
REGISTRY_BYTES=794
REGISTRY_SHA256=40d87eb792d6cfe14ae914723e9b3d61d27c3abeb0f0dbeba07403fe02ccf0e8
```

## Functional evidence

Fresh verification on 2026-08-30:

```text
COMMAND=python -m unittest tests.verify_package_shadow_test -v
TESTS=35
RESULT=PASS
```

The suite proves exact PASS reuse, relevant/unrelated input discrimination,
dependency-fingerprint invalidation, generated-artifact invalidation,
implementation/tool/environment invalidation, directory-tree hashing, corrupt
and incomplete record rejection, fingerprint-tamper rejection, unknown
applicability rerun, prior FAIL non-reuse, semantic resume equivalence, and CLI
resume behaviour.

The live registry drift guard also passes with the canonical verifier digest,
105 nodes, and 104 command nodes.

## Fail-closed admission boundary

Checkpoint reuse requires the exact per-check policy:

```json
{"mode":"exact_declared_inputs"}
```

The live 105-node registry currently has:

```text
CHECKPOINT_ENABLED_COUNT=0
```

That is deliberate. The engine and controlled contracts are functional, but no
real canonical check receives reuse until its input, implementation, generated
artifact, material tool, environment, applicability, and dependency contract
is reviewed. A disabled check executes normally and neither writes nor reuses a
checkpoint.

## Still open

- representative canonical-oracle integration evidence;
- reproducible performance measurements;
- serial fresh-context review and final handoff.
