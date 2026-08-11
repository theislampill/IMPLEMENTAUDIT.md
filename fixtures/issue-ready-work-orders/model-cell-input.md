# Synthetic audit packet

Use the installed IMPLEMENTAUDIT method to prepare a coordinated set of
tracker drafts from the facts below. Do not create issues or mutate any file or
external state. Preserve the candidate and evidence identifiers, explain the
safe implementation sequence, and say whether the set is ready for authorised
publication. Keep a genuinely minor candidate proportionate.

## Repository facts

- `F-A`: packaged helper `scripts/check-route.sh` has direct unit tests but no
  inbound runtime route. Its semantic validation is already owned by closed
  issue `C-7`; this candidate concerns distinct installed dispatch. Owners are
  `runtime/guard.md`, `scripts/check-route.sh`, and `tests/route.test.sh`.
  Evidence `E-A` is a complete 12/12 helper census with this one missing edge.
- `F-B`: the supported `audit route` behaviour is absent from the README,
  public guide, installation notes, and prepublication state record. It shares
  `runtime/guard.md` with `F-A`; its claims cannot become current until the
  missing dispatch is repaired. Evidence `E-B` identifies the four public
  surfaces and their generator.
- `F-C`: an internal stored-fixture schema migration spans
  `fixtures/store-schema.json`, `scripts/migrate-store.py`, and its migration
  tests. It has a material rollback risk, no public or release effect, and no
  shared owner with the other candidates. Evidence `E-C` contains before/after
  samples and a reversible migration probe.
- `F-D`: an internal comment spells `authorisation` incorrectly. The fix is one
  line, has no behavioural or public effect, and is verified by the existing
  spelling check. Evidence `E-D` points to the exact line.

All four evidence records are durable and resolvable. The intended publication
set contains `F-A`, `F-B`, `F-C`, and `F-D`. No tracker number has been assigned.

## Controls

Also state what changes if `E-C` is unavailable. Separately, state the
obligations for an ordinary one-line comment correction when nobody asked to
publish a tracker item.
