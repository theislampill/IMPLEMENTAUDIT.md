# R35-V02 inline prelude version properties

Two original inline Python blocks in the exact PR #255 verifier prelude have a bounded property census. Positive runs on unchanged candidate inputs produced exit 0 with empty stdout and stderr. Fourteen isolated source-data controls each produced exit 1, empty stdout and the expected guard diagnostic. These are local observations of the exact extracted bodies. Whole-prelude execution, full toolchain closure, canonical property receipt and original acceptance remain open. [Original V02](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/585012cbc6b47cb332222c2784481567a482c8a5/recovery/contracts/original/R0035_209_CRITERIA_INDEX.md#r35-v02)

## Association and inputs

Both bodies belong to `PRELUDE`, the first node of the existing serial graph. Its 38,792 bytes have SHA-256 `702f64905d0c9ef8afbeb84ca494ec393f26b3ce3c7388374b95cc48dfdcd07e`. The bodies execute in source order under the prelude's shared shell and repository writer constraint. The local control invokes each body independently and never runs a registry command, conditional release build or neighboring block. [Canonical compiler](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/skills/implementaudit/scripts/compile-work-graph.py#L3570-L3590) · [Exact registry prelude](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/51416b2f156b341c4a5f09029e2c6ceb5b30b1e7/scripts/verify-package.sh#L492-L564)

| Exact body lines | SHA-256, including final LF | Actual file inputs |
| --- | --- | --- |
| 493–511 | `20302168e982d5fe8233553a51fc42bd6b552029201f2058fa4bd4c4f7147f65` | `.claude-plugin/plugin.json`, `skills/implementaudit/SKILL.md` |
| 515–563 | `c6b370561d1469cf478a68f38873915770f777611387bc20ed975822ab03cc8d` | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md`, `docs/portal/site.json` |

The exact five tracked inputs matched product `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7`. WSL Ubuntu ran CPython 3.12.3 with interpreter SHA-256 `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f`, arguments `-I -S -B -X utf8 -`, and only `LC_ALL=C` in the child environment. Observations here are owner-level raw local stdout, stderr and exit. A change to an applicable input, the body or its order, the prelude/registry identity or the observed interpreter/environment invalidates the affected association. The canonical runner's own environment and outcome need their own observation.

| Declared guard | Isolated input change that reached it |
| --- | --- |
| Skill has YAML frontmatter | Supply plain text without frontmatter |
| Skill declares metadata version | Supply frontmatter without a version field |
| Skill metadata and manifest versions agree | Supply a skill version of `0.4.1` against the unchanged manifest |
| Plugin name is `implementaudit` | Substitute a foreign plugin name |
| Plugin source skills path is `./skills/` | Substitute `./foreign/` |
| Plugin version is present | Remove manifest version |
| Plugin version is in the exact `0.4.0` runtime family | Substitute `0.4.1` in the plugin-only block |
| Marketplace plugin list is nonempty | Use an empty list |
| First marketplace entry points to source root | Substitute its source with `./foreign/` |
| First marketplace entry omits the archive-only path key | Add `path` to the first entry |
| Portal milestone has four numeric components and a `v` prefix | Use `0.4.0` |
| Portal milestone belongs to manifest runtime family | Use `v0.4.1.1` against the unchanged manifest |
| README declares a current milestone | Replace the declaration label |
| All matching README lines contain both identities | Keep the valid claim and append a second claim with a wrong runtime version |

A declared guard may be masked by an earlier refusal in the canonical composed route. For example, an altered manifest version can first fail the skill/manifest equality block. The isolated negative shows the later guard exists. It does not imply that a full prelude with that fixture reaches it, or that guard outcomes are independently reusable.

## Canonical task opt-in

`scripts/work-graph-verifier-task.py dag <new-evidence-directory> --include-version-prelude` binds the supported registry and the five regular file inputs before dispatch. Its v2 task record derives fourteen ordered rows from the exact composed PRELUDE and preserves the five registry-checker rows. A verified PRELUDE PASS is sufficient for those fourteen rows. A failed, interrupted, unsettled or legacy node leaves them unverified. The default v1 record remains available. Retained comparison rederives each population and requires matching issued scopes.

The existing named verifier checks passed. They exercise the exact prelude mapping and refuse a changed span and an unsupported registry without output. A separate real legacy/DAG control in a temporary checkout introduced one stale generated-diagram line after preserving the README version claim. Both routes exited 1 with identical raw stdout and stderr, JOIN FAIL and NEXT BLOCKED. The DAG passed PRELUDE and recorded all fourteen version properties as PASS. The later checker stayed unsettled and all five of its rows remained unverified. The legacy record had no node trace, so all nineteen properties remained unverified. The comparator accepted the raw relation and the README was restored exactly.

The retained DAG and legacy capture digests are `321d98a41c2d17339d1e4e580d05e99dc5eb18dd165f04126390e25426491716` and `b4c7083796c3fcf6fcdf1a8f3c231d7b122a86beb3f8b31d6120f4d92bc32fe7`. This associates the fourteen properties with a real canonical node occurrence in the controlled subject. Complete V02 and final-candidate receiving remain open.

## Retained local executions

An independent source review corroborated the two body descriptors and the 14 explicit guard cases. The subsequent bounded execution retains each exact stdout, stderr and exit, the unmodified source descriptors, and each reproducibly altered input's descriptor in [the captured record](PRELUDE_VERSION_CAPTURE.json). [The harness](capture_prelude_version.py) deterministically derives each altered input from the five pinned file bodies and uses the existing 64 KiB combined-output collector. It can be run on the pinned local source with POSIX Python 3.12 using `python3 -I -B handoff/sol-dg16-20261122/original-v02/capture_prelude_version.py`. These observations have pending independent receiving.

## Remaining verifier work

The first inline block covers Git-tracked shell line endings. The prelude also has release-selection, required-file, marker, documentation and custody-dependent branches. Other checker/test nodes and terminal normalization still need their property bindings. The version census neither changes the canonical source nor completes the property population. A next candidate can attach the version observations to the exact prelude occurrence under the canonical receiver without weakening the prelude's serial composition.
