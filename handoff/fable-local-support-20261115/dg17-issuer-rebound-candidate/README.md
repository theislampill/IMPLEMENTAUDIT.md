# DG17 issuer-rebound operation record: CANDIDATE for PRO-EXECUTOR-01 (2026-11-15)

Status: candidate only. Issuer succession for DG17 is Pro's to resolve (owner,
2026-11-15: "Pro is authorized to resolve the prospective issuer succession
within its existing engineering scope; a new protected native episode still
requires its legitimate grant"). Nothing here is adopted, granted or launched.

Why it exists: the record must be built on 3701Media, which Pro cannot reach,
and the obvious rebind fails once before it works.

- **Trap.** The issuer appears in exactly one place in the frozen base
  (`OPERATION_A.json`). But the base `parent_launch_a.py` and `bind_stage_b.py`
  each embed the base operation's SHA-256, and the builder replaces that literal
  exactly once. Editing only the issuer makes `build_release_acl.py` stop with
  `Expected exactly one pinned literal: parent_launch_a.py`.
- **Working route, no builder or test change.** `make_rebound_base.py` copies the
  ten-member base, sets `issuer` to `PRO-EXECUTOR-01`, adds an explicit
  `issuer_rebinding` field, and forwards the new base hash into those two
  literals. The unchanged builder then runs with `--base-author`.
- **Result on 3701Media**, source `a297957b`, same package `706afde4…`:
  `OPERATION_A.json` 19,215 bytes, SHA-256
  `aa93fda5c8335a892e0dcd1f022375f53aeab53a1350ab54cc943de182234cf7`;
  `PINS.json` `c79ec08d91d19a8f2bce397f237f2e5e77dbdf7841624361e3915c48e5fa9fa2`.
  Limits identical to the retained-issuer record `ec5051dd…`. Readback through
  the generated parents' own `capture()`: 34 of 34 PASS. Fixed native locations
  still absent.
- Final author directory:
  `C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\issuer-rebound\author`.

If Pro wants a different successor string, a different `issuer_rebinding` text,
or no such field, say which and the record is rebuilt in one run; the hash will
change. Whichever record Pro selects is the one the owner's grant must name.
The retained-issuer record `ec5051dd…` in `../dg17-final-operation/` is unchanged.
