# Thread6.11 successor staging toolkit

This directory is a branch-only, non-product engineering aid for the existing
Thread6.10 campaign. It does not create Thread6.11 and has no campaign,
continuity, route, package, HBASE, install, release, or cutover authority.

The builder consumes one explicitly supplied snapshot plus explicitly named
evidence files. It does not discover or modify continuity refs, routes, goals,
STATE, ROADMAP, WORK_GRAPH, HBASE resources, installed plugins, or Git state.
Its output is evidence for later Thread6.10 verification and admission.

## Outputs

`successor_packet.py build` writes exactly three files to the requested output
directory:

- `THREAD6_11_SUCCESSOR_PACKET.json`: compact frontier and exact evidence index;
- `THREAD6_11_LAUNCH_PROMPT.md`: startup prompt bound to the packet content hash;
- `SUCCESSOR_PACKAGE_MANIFEST.json`: byte and SHA-256 identities for both files.

Every evidence entry is read back and bound by absolute path, byte size, and
SHA-256. A later verifier fails if a bound artifact drifts. The generated prompt
states that Thread6.10 must publish the authoritative final handoff and that the
packet itself does not create Thread6.11.

## Provisional workflow

```powershell
py -3 -I -S tools/thread6-successor-staging/successor_packet.py build `
  --snapshot tools/thread6-successor-staging/observed-frontier-G023B.provisional.json `
  --output-dir tools/thread6-successor-staging/provisional-package

py -3 -I -S tools/thread6-successor-staging/successor_packet.py verify `
  --package-dir tools/thread6-successor-staging/provisional-package
```

Provisional mode permits unresolved live-authority slots but forces:

- exact existing controller/claim/run and phase C;
- active `/implementaudit` goal identity and terminal objective;
- `THREAD6_10_IS_THREAD7=NO` semantics;
- A-to-G native closure before Thread7;
- Thread6.9 paused;
- authority ceiling `NONE`;
- entry point `UNSET`;
- the complete do-not-replay inventory.

## Finalization workflow

Thread6.10, not this tool, must evidence one of the two authorized finalization
conditions and supply a refreshed snapshot.

`POST_HBASE` requires:

- exact current continuity receipt, pointer, host binding, route, and source ref;
- one frozen exact candidate identity;
- terminal canonical package evidence;
- qualified HBASE result and Thread6.10 trigger evidence;
- next edge `ORDERED_R30_J0_CONSUMPTION_SELECTIVE_REVALIDATION`.

`PRE_HBASE_EXACT_FRONTIER` requires:

- the same exact current authority and frozen-candidate identities;
- an exact next typed edge;
- explicit `CIRCUIT_BREAKER_EVIDENCED_BY_THREAD6_10` plus its evidence ref;
- truthful package and HBASE status, with no inferred completion.

For either mode set `packet_mode` to
`FINALIZED_FOR_GOVERNOR_VERIFICATION`. The verifier rejects placeholder
authority values and can additionally compare candidate head, tree, branch,
and dirty state against a live checkout:

```powershell
py -3 -I -S tools/thread6-successor-staging/successor_packet.py verify `
  --package-dir <final-package-directory> `
  --repo-root <exact-frozen-candidate-worktree>
```

## Bounded final refresh set

Finalization should refresh only:

1. latest receipt, pointer, host binding, current route, and governor snapshot ref;
2. frozen package/HBASE candidate head, tree, branch, and clean state;
3. correction, focused-control, and review result identities;
4. shadow registry/result status;
5. canonical `verify-package` terminal evidence;
6. HBASE result/qualification identity;
7. exact next typed edge;
8. Thread6.9 paused readback and current goal readback.

Broad worker transcripts, campaign phases A/B, repaired package failures, and
accepted work are intentionally excluded.

## R30/J0 lookahead

`R30_J0_LOOKAHEAD_CAPSULE.json` pre-binds the clean R30/J0 tip, its two
prepared integration commits, and the merge base observed against the staged
HBASE checkout. It is census/preparation only. In particular, it refuses to
infer from a naive Git range that those two commits are the only semantic
delta. Post-HBASE consumption still requires the authoritative 12-path overlap
packet, a freshly frozen HBASE candidate, and invalidation-radius analysis at
the proper JOIN.

## Tests

```powershell
py -3 -I -S -m unittest discover `
  -s tools/thread6-successor-staging/tests -p 'test_*.py' -v
```

The tests exercise the real CLI and cover evidence drift, packet tampering,
duplicate evidence identities, campaign drift, incomplete do-not-replay state,
false post-HBASE finalization, inferred circuit-breaker finalization, and live
candidate drift.
