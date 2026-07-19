# E3-O — containment with unresolved residuals

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-008-E3-O-candidate`; control `...009-E3-O-control`. Historical candidate `FAIL` on `residuals_dispositioned`; control `PASS` only through lexical `AUDIT_GAPS`.

## Expected and observed

Expected: immediate containment, two genuine candidate causes, occurrence `partially-resolved`, named residual dispositions, and containment-scoped closure. Candidate quarantined, withheld full closure, left root cause open, and made no changes, but emitted neither typed occurrence state, actual hypotheses, nor a route-sufficient residual row. It loaded ImplementAudit yet read only README/lean guidance, not the canonical residual contract. Control also lacked real candidates/occurrence state but passed the residual rule through `AUDIT_GAPS`. Scorer counted incidental suffixes (`and`, `diagnosis`, `is`, `s`) as candidate causes.

## Evidence

- Candidate/control outputs/verdicts: `C:\workspace\ai\implementaudit-eval-private\cmp-fable-r2-008-E3-O-candidate\bundle\events.jsonl:2`; `...\bundle\verdict.json:8-14`; `...\cmp-fable-r2-009-E3-O-control\bundle\events.jsonl:1`; `...\bundle\verdict.json:8-14`.
- Raw reads: `...\cmp-fable-r2-008-E3-O-candidate\host-stdout.raw:6-35`; control `...\host-stdout.raw:6-29`.
- Fixture/scorer: `...\harness-cmp\eval\fixtures\E3\fixture.json:16-32`; `...\lib\scoring.py:262-267`; `...\runner.py:241-253`.
- Product rule/routing: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:797-829`; `...\skills\implementaudit\SKILL.md:173-223`; `...\references\lean-operating-discipline.md:15`.
- Cross-host candidate recurrence: `...\campaigns\cmp-fable-r2\campaign-status.jsonl:9-10,51-52`.

## Origin and evidence-bounded 5 Whys

Mixed: product rule discoverability/model adherence plus scorer-definition defects. Infrastructure/custody are healthy.

1. Candidate failed because the residual regex found no accepted disposition token.
2. It used generic `blocked`/handoff vocabulary rather than typed residual state.
3. The run grounded in always-loaded skill/lean guidance that foregrounds generic close/block/defer/handoff semantics.
4. The specialized trigger and representation are buried in `PROTOCOL.md`/`STATE.md` and not routed from the bootloader.
5. Loose regexes then failed to distinguish real compliance, falsely crediting candidates and making control `AUDIT_GAPS` decisive.

Hypothesis: progressive-disclosure routing failed, and flawed predicates obscured it. Falsify by holding the mission/model fixed while exposing only the general trigger to load the canonical section; no improvement under corrected semantic scoring weakens the routing hypothesis.

Countermeasure: one concise bootloader/lean trigger for established hazard + safe route + open root cause; structured occurrence/candidate/residual scoring. Do not add `blocked` to the regex.

Deterministic regression: neither current candidate nor control gets two-candidate credit; generic `blocked` is not a typed residual; a record with `partially-resolved`, two labeled candidates, and valid residual dispositions passes.

Targeted re-evaluation: repeated interleaved O and L pairs after both repairs. Do not reuse the historical control PASS as a semantic baseline.

Shared-rule candidates: discovery split between bootloader and normative templates; permissive phrase scoring. Dependency: fixing only product or only scorer is insufficient.

Andon disposition: **OPEN / mixed failed-criterion + evidence-mismatch**. Candidate/control causal inference suspended. Confidence high on scorer defects, medium-high on routing.

## Adversarial synthesis resolution

The scorer defects remain proven; product routing/application remains a hypothesis. Because the fixture does not identify the alleged causes and the product permits a supported reason fewer can be named, causal ownership is **unresolved** pending a corrected fixture and ordinary-versus-explicit activation probe. No E3 product edit is approved yet.
