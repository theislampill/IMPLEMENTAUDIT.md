# Compact report candidate for independent receiving

The candidate fits a complete generated public fixture under the original selected inner limit and the outer uncompressed delivery limit. It also reconstructs the exact legacy bytes under the existing 2 MiB receiver cap. This is prospective ordinary transport evidence for Root review. The current report producer, receiver, and release paths remain authoritative.

| Fixture measurement | Bytes |
| --- | ---: |
| Exact accepted v1 representation | 2,021,387 |
| Selected inner limit, which refused the v1 representation | 1,823,337 |
| Prospective compact wire | 1,475,114 |
| Compact uncompressed delivery including fixture contract and manifest | 1,476,035 |
| Fixed expansion and uncompressed delivery ceiling | 2,097,152 |

The 2,050 records are deterministic inert public fixture text with generated descriptors and bookends. The fixture calls the pinned source's actual six derivations, shape checks, completeness predicate, and v1 receiving function. It uses a fixture-specific selection contract without a wheel or host cache join. The source test loads only a reviewed set of pure public functions from the exact runtime source. It performs no host capture or native episode. On Python 3.11.9, the pinned receiver accepted the complete fixture and produced the same result after compact expansion. The reconstructed v1 bytes are identical. [Pinned runtime source](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/7cbad948f54216617bfa46f3548917104e8f650f/engineering/g132-host-runtime-static-operation/runtime_static.py).

The encoder uses the current receiver on its exact canonical v1 input. It preserves every nonderived field and stores the six canonical derived values as length and SHA-256 commitments, plus the commitment to the whole v1 body. The decoder checks the canonical wire, exact schema, descriptor census, descriptor lengths, observation shapes and resource ledger before independently deriving the six values. It checks each section within its declared length and applies a fixed expansion limit before returning the bytes to the existing v1 receiver. An embedded commitment verifies byte correspondence. Authenticity and custody still depend on the delivery's independent evidence.

The test suite retains nine controls, including the successful round trip, wrong and missing commitments, missing observed closing evidence with old and rebound commitments, logical observation budget overflow, duplicate keys, noncanonical JSON, v1 rejection of the draft wire, and exact and one-byte-over delivery thresholds. The initial 2,250-record fixture yielded 2,218,589 v1 bytes and remains a negative control for both receivers. The ordinary historical run's stated 2,589,544-byte v1 body also exceeds this candidate's fixed expansion limit. A source owner would need to decide separately whether a future compact-only semantic format can operate within the original contract. No historical fit, original custody or DG16 award follows.

## Reproduce the fixture

Use a verified copy of the pinned public source at the link above. `MANIFEST.json` records the exact source hash, code bytes and fixture output. Set `DG16_PINNED_RUNTIME` to the local copy and run the tests from the repository root.

```powershell
$env:DG16_PINNED_RUNTIME = (Resolve-Path -LiteralPath '<verified-local-copy>').Path
python -B handoff/sol-dg16-20261122/compact-report/test_compact_report.py
```

Independent receiving should check the source hash and fixture outputs, rerun the suite and review the resource caps and old-wire equivalence. Production integration and exact candidate applicability are separate decisions.
