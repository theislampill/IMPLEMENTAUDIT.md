# G132 host and operator: independent publication receiving

**PASS — exact ordinary source publications received.** Recorded 2026-11-15
22:22:34 UTC by `/root/dg18_recovery`, independently of Root's publication.
This is byte/tree/parent/ref receiving. It reuses DG17's completed semantic and
final binding reviews and does not repeat them.

| Publication | Actual commit | Actual tree | Sole parent |
| --- | --- | --- | --- |
| Host continuation source | `2f6a96427a307dc57ed88664aeb8224918fe6bf5` | `8a8023d6db96fb7adbc3d65ddf042ce0760ecea8` | `434f12f038da9420f9addaf2fed7178e1e41e20f` |
| Operator continuation source | `198a0495e486a5cc79534aa42fa984516ad16d67` | `e7024697702307712798501554a894c2fe94d0d0` | `68bb72ecd2ec082cb7e358d7c0e28c94c94d6bbf` |

I fetched the two exact published commits read-only and inspected their actual
Git commit/tree/blob objects. For each publication, its actual sole parent and
tree equal the expected payload, and its complete parent-to-commit changed-path
population equals the payload inventory. Every changed published body matches
the exact expected content, byte length, SHA-256, Git blob ID and file mode.

The host tree contains 1,815 files and changes exactly 14 existing paths. The
operator changes exactly 47 paths: 44 modifications and three additions. Its
published `OPERATOR_PINS.json` is 27,159 bytes, SHA-256
`c7ac3f5a95dec2c05f10201d96429c27d3e9d5e19f6d1a8051c3c14912b90309`.
I also read and hashed all 144 selected published member bodies against that
actual index; every length and SHA-256 matches. No source program, role,
operator, generator or qualification test was invoked.

## Actual provider refs

A fresh read-only remote-ref query after both publications observed:

| Ref | Observed head |
| --- | --- |
| `refs/heads/engineering/pro-g132-continuation-host-20261115` | `2f6a96427a307dc57ed88664aeb8224918fe6bf5` |
| `refs/heads/engineering/pro-g132-continuation-operator-20261115` | `198a0495e486a5cc79534aa42fa984516ad16d67` |
| `refs/heads/pro/dg16-g1-original-g3-32-20261114` — protected host32 | `434f12f038da9420f9addaf2fed7178e1e41e20f` |

The two ordinary refs name their exact received commits. The protected ref
remains at its original 434 predecessor in this observation. This receipt
does not move that ref or transfer an exact-434 grant to the changed 2f host.

## Retained bindings

Paths below are relative to `recovery/received/g132/`.

| Record | Bytes | SHA-256 |
| --- | ---: | --- |
| `HOST_CONTINUATION_PUBLICATION.json` | 214,137 | `47812997c6785486fecb7d1d84b54c3fc4a39d8d78fb6eaff57f459f45ee3759` |
| `OPERATOR_CONTINUATION_PUBLICATION.json` | 2,767,455 | `b69f6786e3bc7812b384fe94471bd089a1afbd4a7e10a36bdc2a01bbf909d90b` |
| Root's `HOST_SOURCE_REF_READBACK.json` | 1,776 | `bb7f669aeb55d50450e6a04327f90c647b4393728e86102126e92c1e6ee015dd` |
| Root's `OPERATOR_PUBLICATION_READBACK.json` | 5,925 | `35c50ea6fda39afb8b84395853b4a64610b83daa7d89e6bdec22c101ae36453b` |
| `continuation-build/INDEPENDENT_FINAL_BINDING_REVIEW.md` | 7,192 | `b86e4d5e25c6e349eafd9d1396904760a8a9aab5a5c24279f366ad81527a850e` |

The existing final source review records PASS for the G132-CONT-01 correction
at its exact freeze; the earlier GAP and original source reviews remain
separate. This publication receipt adds no semantic or runtime qualification.

The reviewer performed no remote mutation, protected-ref update, live grant,
workflow launch, native operation or test rerun. Fresh live-window/provider/run
facts, any protected publication/effect, actual native outcome and original
receiving retain their separate authority and evidence requirements. No G1,
G3, full-G2, natural-native or whole-programme acceptance follows here.
