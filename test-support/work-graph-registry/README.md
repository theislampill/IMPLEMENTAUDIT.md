# Historical qualification inputs

This repository-only collection preserves exact source specimens from
PR246 commit `cbb616cc7e0f9abafebe9bbdeee202ede7feb94e`.
`original117-manifest.json` binds every original path, byte count, SHA256
and mode. It is test input, not current source, receipt or acceptance.

The original registry remains byte-identical at
`original117/verify-package.sh` (SHA256
77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698).
Its117 nodes/89 tests and the existing finite contracts are unchanged.
The retained package owner has SHA256
f3fa90f6c1e7b75527eddd988a6977f27db669bec337f65ff9c2b1ceae50621f.

The tests use three explicit subjects:

- Current finite driver/compiler/helper, copied into an actual private engine,
  with the exact historical prefix dependency required by that helper.
- Historical positive inputs: pinned original programs/data, original90's
  fixed arithmetic population, and the original29-route reference. Other
  unpinned inputs are explicitly variable fixture data, not a claim of a full
  historical checkout.
- Actual current source and engine: old selectors/factories must refuse them.
  The separate composite profile and ordinary canonical verifier qualify
  current execution. No historical receipt becomes current.

The fixed README-effect loader additionally requires its complete historical
engine closure. Every existing pin is checked before a specimen is selected.
Its old driver/compiler are only that selected dependency fixture; the current
driver/compiler are tested in the ordinary/current finite engine banks.

`tests/work-graph-historical-fixture.py` copies verified bytes during fixture
construction, never during acquisition. Post-construction drift stays visible
and must fail. Opt-in live fixtures retain their explicit current source and
refuse if the old contract is not applicable.

This corpus lives outside the acquired `tests/` and `fixtures/` namespaces
so an original subject does not recursively acquire its own reference corpus.
No product reader exclusion, input/resource bound, source pin or verifier is
changed. The original specimens previously under `fixtures/work-graph-registry`
are retained here without byte changes. None is shipped in either artifact.