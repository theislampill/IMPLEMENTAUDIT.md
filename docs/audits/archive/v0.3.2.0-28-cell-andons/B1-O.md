# B1-O — durable-state resume

Investigator/provenance: Sol, read-only. Cell: `cmp-fable-r2-010-B1-O-candidate`; paired control: `...011-B1-O-control`. Historical result: candidate `FAIL` on `resume_acknowledged`; `no_phase1_restart=true`.

## Expected and observed

The mission expected a durable run root proving phases 1–2 complete, a `RESUME_ACK` naming phase 3, no phase-1 restart, and eventual `AUDIT_COMPLETE`. The rendered repository contained no run root: B1 has no `seed/`, so `seed_fixture_repo` created only a README. The candidate exhaustively searched the fixture repo, parent work tree, environment, and temporary home; found no state; refused to fabricate a phase-3 resume or completion; emitted an evidence-mismatch handoff; and made no repository change. The control reached the same live-state conclusion and failed the same property.

## Evidence

- Fixture assertion and rules: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\B1\fixture.json:3,8-29`.
- Missing-seed fallback: `...\harness-cmp\eval\adapters.py:95-117`.
- Candidate searches/final response: `...\cmp-fable-r2-010-B1-O-candidate\host-stdout.raw:16-17,25-26,34-35,51-52,61-62`; normalized text: `...\bundle\events.jsonl:3-5`.
- Clean repository comparison: `...\bundle\repo-comparison.json:2-3`.
- Verdict and scorer path: `...\bundle\verdict.json:42-60`; `...\harness-cmp\eval\lib\scoring.py:139-216,323-359`; `...\runner.py:110-130,241-253`.
- Product continuity contract: `...\product-v0320-candidate\skills\implementaudit\references\continuity.md:30-54`.
- Paired corroboration: `...\campaigns\cmp-fable-r2\campaign-status.jsonl:11-12`.

## Origin and evidence-bounded 5 Whys

Primary: fixture. Secondary: fixture validation/scorer adjudication. Product, host, and authorization are not causal.

1. FAIL occurred because no authoritative line named phase 3.
2. The candidate withheld it because live searches found no durable phase evidence.
3. The evidence was absent because B1 has no seed and the adapter created a README-only repo.
4. Formal scoring still emitted product `FAIL` because no host-observed state precondition validates the mission assertion.
5. The frozen evidence does not establish why B1 omitted the materialized-state protection already recognized for B3; causal analysis stops there.

## Hypothesis, falsifier, and countermeasure

Hypothesis: the missing seed caused a prompt/live-state contradiction, and evidence-faithful behavior was mislabeled as failure. Falsify by materializing and host-attesting a valid run root with phases 1–2 terminal and phase 3 next; if the unchanged candidate reads it but still refuses phase 3, product/model behavior becomes causal.

Smallest coherent countermeasure: add an authentic B1 seed plus a generic preflight schema for stateful fixtures; missing/corrupt prerequisites become `INVALID`, not product `FAIL`; score the declared completion/order requirement too.

Deterministic regression: seed B1 in a temporary repo, validate one active run root, phases 1–2 terminal, phase 3 next, and the run-root schema; prove missing/corrupt state is `INVALID`; prove phase-1 restart or missing completion fails.

Targeted re-evaluation: fresh interleaved B1-O candidate/control runs on the same Opus host/model, with raw reads of the seeded state preserved.

Shared-rule candidate: every mission asserting live filesystem state needs a host-attested precondition. Dependency: B1 fixture validity precedes any continuity comparison.

Andon disposition: **OPEN / evidence-mismatch / fixture-confounded**. Historical verdict preserved; product attribution quarantined. Confidence 0.99; inference risk high.
