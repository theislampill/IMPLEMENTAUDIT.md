# Fixture: ActiveGraph present — Lean/DMAIC custody events emitted and read back

Route: DMAIC (brownfield — ActiveGraph custody scenario)

## Scenario

ActiveGraph is configured and authorized. A temporary custody store is created in
.IMPLEMENTAUDIT/ (gitignored). Lean/DMAIC custody events are emitted, read back,
and used to derive one narrow Capability Ledger entry.

## Custody run

Run ID: v0270-sidecar-smoke
Custody store: .IMPLEMENTAUDIT/runs/v0270-sidecar-smoke/custody-trace.jsonl (gitignored)
Custody mode: live_release_gate

Events emitted (IMPLEMENTAUDIT-defined custom events):
- implementaudit.run.opened
- audit.input.normalized
- gemba.graphify.queried
- lean.5s.sort.recorded
- lean.5s.set_in_order.recorded
- lean.5s.shine.recorded
- dmaic.define.recorded
- dmaic.measure.recorded
- dmaic.analyze.recorded
- dmaic.improve.recorded
- lean.standard_work.updated
- dmaic.control.recorded
- muda_mura_muri.register.updated
- poka_yoke.check.recorded
- nemawashi.owner_decision.recorded
- smoke.baseline.recorded
- audit.verify.recorded
- implementaudit.run.finalized

## Readback

Events readable from custody-trace.jsonl: yes (18 events confirmed)

## Capability Ledger entry (derived from readback — narrow)

- repo: theIslampill/IMPLEMENTAUDIT.md
- run_id: v0270-sidecar-smoke
- milestone: v0.2.7.0
- owner_source: skills/references/lean-operating-discipline.md
- quality_route: DMAIC
- lean_principles_applied: 5S (Seiri/Seiton/Seiso), Muda/Mura/Muri, DMAIC, Poka-yoke, Nemawashi
- graphify_terrain_used: yes (794 nodes, 724 links, 5 queries, 3 candidates confirmed)
- graphify_evidence_type: orientation only, not proof
- activegraph_event_ids: 18 (v7-001 through v7-018)
- activegraph_note: IMPLEMENTAUDIT-defined custom events; not upstream ActiveGraph built-ins
- checks_run: check-lean-discipline.sh ok, lean-discipline.test.sh 9/9
- final_status: sidecar-leverage-pass
- remaining_risk: none

## What must NOT happen

- Do not include custody stores in the .skill package.
- Do not commit custody JSONL, .db, or graph exports to tracked source.
- Do not derive broad competence claims from this run's custody evidence.
- Do not treat ActiveGraph custody as correctness proof.

## PHASE_VERIFY stub

IMPLEMENTAUDIT_PHASE_VERIFY
- [pass] ActiveGraph custody used: yes — 18 events written to gitignored run root
- [pass] Events read back: yes — all 18 events confirmed in readback
- [pass] Capability Ledger entry narrow: yes — repo/run/owner/route/principles/checks/status/risk only
- [pass] Custody store outside tracked source: yes — .IMPLEMENTAUDIT/ gitignored
- [pass] No custody outputs in .skill package: yes — verify-package.sh and build-release-asset.sh confirm
- [pass] ActiveGraph note: IMPLEMENTAUDIT-defined custom events
Sidecar: Graphify present (orientation); ActiveGraph authorized (custody); Markdown fallback yes
Remaining risk: none
