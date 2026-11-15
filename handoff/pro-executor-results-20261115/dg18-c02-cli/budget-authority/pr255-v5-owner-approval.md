# PR255 prospective bounded reserve exception (revision 5)

Transcribed by Claude from the owner's chat; Root must confirm before adoption.
Source record: RETURN/OWNER_DECISION_DG17_RESERVE_20261113.md, sha256
8b4536c2edddecf2f10dda5b86e03951f6d2eec44b65c55c7754d4cd771ee389.

On November 13, 2026, the human owner decided, as recorded there verbatim:

> A 734-byte exception to the 2,000-byte package reserve, exclusively for adopting the independently reviewed DG17 outer Stop interlock correction. The 589,824-byte hard limit is unchanged. At least 1,266 bytes of reserve must remain. The 10 s containment, descendant termination, failure handling and cleanup are not relaxed. The exception does not generalize. Route C is not pursued. This is not authorization for native execution, publication, merging or acceptance certification.

The final decision below supersedes the initial reserve for this correction only.
The canonical plugin required reserve is 1,240 bytes (588,584 usable); the standalone role keeps the mandatory
2,000-byte reserve. The 589,824-byte caps of revision 4 are unchanged for both
roles, as are ZIP/member/installation integrity requirements and every
historical failure.

Historical candidate named by the initial owner decision: skills/implementaudit/scripts/
host-stop-interlock.py 49f972f57ee997148d69915090ecbc3cc680c40ad95d61067ebf79fc68da79e9
(31,541 bytes) against PR ed2c060d / tree f8ce5c14, measured at 588,558 bytes
before this record existed. This contract file is itself packaged, so recording
revision 5 adds 19 bytes. The interlock submitted with this record is
8ad392459f9c8cff07fe8b25045dd2604f4866e91c6a6452f7f580ef7d46b37b (31,464 bytes):
the same code by AST, with the owner function's docstring merged into the
comment below it. The final owner decision below confirms this variant and its bounded reserve.
Earlier measurements are indicative only; Root must independently confirm the
exact final integration commit against the 588,584-byte usable limit.

Revision 5 is prospective, under the existing PR255 composite commission;
PR255_COMPOSITE is an owner label, not a new Rockstar or controller. Preserve
budget revisions 1, 2, 3 and 4, their approval records and all previous
failures. The package inventory embeds the commit and tree ids, so the plugin
must be re-measured at the actual integration commit; a result above the
usable limit is not covered and returns to the owner. Final deterministic
both-role builds, integrity checks, isolated installs and affected
qualification are still required on the exact submitted source.

## Final owner decision (verbatim)

# Owner decision record: DG17 final reserve adjustment (2026-11-13). Commission closed
Recorded by Claude Opus 5.5 from the owner's chat. This supersedes the 1,266 B minimum in OWNER_DECISION_DG17_RESERVE_20261113.md for this exact correction only. The final archive (a29f35ad) and the addenda (88d799e3, 92d110f1) are preserved unchanged.

Decision: the DG17-specific minimum package reserve is 1,240 B, limited to this reviewed interlock correction and its necessary package-contract (revision 5) integration. Hard limit 589,824 B unchanged, so the final integrated canonical plugin must be at most 588,584 B. The 10 s containment, descendant termination, failure handling and cleanup are preserved. No silent further lowering; no weakened tests. Not authorization for native execution, publication, merging or acceptance certification.

Candidate: interlock 8ad39245 (31,464 B; FABLE/DG17Z), preferred over 49f972f5. Opus independent confirmation:
- AST identical to the reviewed 49f972f5 except windows_owner's removed docstring, merged into the adjacent comment with every safety statement kept.
- No introspection dependency: no file that references host-stop-interlock uses __doc__ / inspect.getdoc / ast.get_docstring, and the removed text is asserted nowhere in the tree.
- Controls on 8ad39245: interlock_containment_controls 5/5; constructed reparented-grandchild outer control 10.02 s with the descendant ended.

Root's integration steps (from FABLE/DG17Z PATCH.diff as the base):
1. In package/budgets/pr255-v5-owner-approval.md and scripts/package-contract.py / package/implementaudit-package.json, set the canonical_plugin reserve to 1,240 (not 1,266), name interlock 8ad39245, and append this decision verbatim to the transcribed approval text (Root confirms it). Standalone keeps 2,000; caps unchanged.
2. Update the revision-4 expectations in tests/package-contract.test.sh, tests/plugin-release-asset.test.sh:157 and tests/release-asset.test.sh:1183, and the scripts/package-contract.py digest references in fixtures/semantic-preservation/cases.json and the two work-graph c5 execution fixtures.
3. Integrate with DG17-10 (FABLE/DG17/PATCH.diff) and DG17X (tests plus IMPLICIT_STATES).
4. Measure the canonical plugin at the ACTUAL final integration commit (embedded commit/tree ids and all changes included). It must be at most 588,584 B; otherwise stop and return to the owner. Intermediate measurements (588,550 / 588,565 B) are indicative only.

Claude engineering commission: CLOSED. Next owners: Astra/Root for G2 first (R1 reseal; witness approval; part B start by 2026-11-13T23:04:29Z), then G1 and DG17 integration; Sol per existing responsibilities; the DG18 custodian for the zero-authority questions in ASTRA_SOL_HANDOFF_20261113.md.

## Docstring-dependency verification for 8ad39245 (technical; resolved, no owner decision needed)
- Fable (FABLE/DG17Z/DOCSTRING_CHECK.txt): no material dependency. The only docstring-API uses in the tree are eval/adapters.py:192 and eval/hosts.py:3285, each printing its own module docstring. There is no docstring lint configuration (no pyproject/setup.cfg/tox/ruff/flake8/pylint/pydocstyle/pre-commit), no quote of the removed text, no interlock digest anywhere, and no semantic-preservation reference. Tests import or patch the interlock but never read docstrings. 18 of the file's 28 functions/classes already have none.
- Opus, independently, on the exact candidate tree: confirmed no lint config and no help()/pydoc in the interlock or its tests. None of the interlock's base/reviewed/reduced/8ad39245 digests appears in fixtures, tests, scripts or skills. The eight work-graph c5 fixtures list it only as a path. Opus confirmed both of Fable's docstring-API hits are module-local.
- Residual: interactive help(windows_owner) shows no summary line; the same text is in the comment at the top of the function.
Result: proceed with 8ad39245 and the 1,240 B floor as approved.
