# Independent receiving of the two ordinary publications

**PASS — exact ordinary publication receiving only.** Recorded 2026-11-15
22:07:15 UTC by `/root/dg18_recovery`, independently of Root's publication.

I fetched both exact published commits read-only, read their actual Git commit
and tree objects, and compared the complete parent-to-commit path populations
against the retained publication payloads. Every published file matches its
expected UTF-8 body, byte length, SHA-256, Git blob ID and ordinary `100644`
mode. Both live remote branch heads equal the received commits.

| Publication | Exact commit | Exact tree | Sole parent | Complete change population |
| --- | --- | --- | --- | --- |
| G2 pin correction and retained evidence | `3312e5abfd1bbcf37feb22156598c2ba123c30d7` | `39c33ccab1eaa10e7518e1a6d174590b1df56fad` | `bc3c8e6feca551d7eaafea071b5d4a6e5868de36` | 58 paths: one modified workflow, 57 new evidence files |
| W-FULL continuation source | `a9a7b019e2bf867ba45a2b68e704c2860929d240` | `6369ab94fafba8b43d9ddf3569bc31850fe8056d` | `095ed1623d5fa22ac6f2e306702142d071135db6` | Exactly three paths: one modified workflow, two new continuation files |

The G2 branch is
`engineering/pro-executor-original-completion-20261115`. Its only source
change is the previously reviewed 19 adapter-digest substitutions in
`.github/workflows/dg16-r5-full-g2.yml`. Reversing those substitutions reproduces
the complete parent workflow byte for byte. The unchanged published adapter
has SHA-256
`e8576425bcbb260e3d2c21c11e510d51f0549756ab0b8dcc14cfdce7a96de15b`.
All other 57 paths are evidence under
`handoff/pro-executor-results-20261115/continued-execution-20261115/`.

The W-FULL branch is
`engineering/pro-dg18-w-full-continuation-source-20261115`. Its actual published
files match the final independently reviewed freeze:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/dg18-w-full-minimal-prepare.yml` | 13,815 | `97454ea282a06547b97241e8abbf17cc7f61ef583c10d1e3c4fc4c35ae22a613` |
| `handoff/pro-executor-results-20261115/hosted-w-full-continuation/restore.py` | 11,983 | `6b6f0a1601525c61630d5521458be0c341e5709d023b7803ba0c13560fc0bd80` |
| `handoff/pro-executor-results-20261115/hosted-w-full-continuation/README.md` | 11,299 | `8fffaf03b6123653851f1065fe937220c3c17c180515b0c5a571e6a0e4b0670d` |

The complete source tree contains none of the four launch inputs. The source
branch is absent from the W-FULL workflow's push branch list. The separate
`engineering/pro-dg18-w-full-once-20261115` ref is currently absent in the
read-only remote-ref observation. This receiving supplies no grant, interval,
availability, native execution, currentness or measured result for operation
`e0ac5d2992e44b45e838802c571fa84e27542aa72afab6ebb05c015e3207ec23`.

## Retained exact publication payloads

- `received/publication-g2-pin-closure.json`: 266,667 bytes, SHA-256
  `e9548d948a44fb1a87d87c6fd001429dde70b914b9eab911cb79c486e4837055`.
- `received/publication-dg18-wfull-continuation.json`: 39,099 bytes, SHA-256
  `418f240c7376b20cfd2aa7bf223002f9cb47693d0922c983cfa0b5eed00136d9`.

The existing independent source reviews and actual DG17/G132/installed
receiving remain separate evidence at their original scopes. This check
verifies their publication bytes; it does not repeat or expand their
acceptance. The reviewer made no remote mutation, launched no workflow or
protected effect, and reran no qualification suite. Historical failed-relation
limits, N1 LOST/UNKNOWN, criterion-5 and whole-cell dispositions are unchanged.
