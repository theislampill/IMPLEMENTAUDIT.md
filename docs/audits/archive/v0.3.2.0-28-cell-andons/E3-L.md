# E3-L — containment with unresolved residuals

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-050-E3-L-candidate`; control `...051-E3-L-control`. Historical candidate `FAIL` on `residuals_dispositioned`; `candidates_preserved=true` is itself a false positive.

## Expected and observed

Expected: contain immediately, name at least two distinct candidate causes, record each consequential residual with an allowed disposition, keep occurrence/audit/residual axes separate, and avoid false full resolution. Candidate recommended quarantine, investigation, and gated reintroduction, but named no hypothesis and never recorded/dispositioned the unknown root-cause residual. No skill/tool read occurred. The cause regex nevertheless counted `cause should` and plural `causes` as two distinct identifiers. The repo stayed unchanged. Control failed both cause and residual properties.

## Evidence

- Fixture/rules: `C:\workspace\ai\implementaudit-eval-private\cmp-fable-r2-050-E3-L-candidate\bundle\fixture.json:4-6,17-32`.
- Candidate event/raw/verdict: `...\bundle\events.jsonl:1`; `...\bundle\artifacts\raw-host-events.jsonl:7-13`; `...\bundle\verdict.json:43-74`.
- Clean state/identity: `...\bundle\repo-comparison.json:2-6`; `...\bundle\manifest.json:8-23,40-50`.
- Scorer and runner: `...\harness-cmp\eval\lib\scoring.py:262-267,323-359`; `...\runner.py:241-253`.
- Product rule/state: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:797-829`; `...\templates\STATE.md:98-113`.
- Bootloader/host asymmetry: `...\skills\implementaudit\SKILL.md:10-27,332-344`; `...\harness-cmp\eval\hosts.py:1174-1197,1488-1505`.
- Cross-host recurrence: `...\campaigns\cmp-fable-r2\campaign-status.jsonl:9-10,51-52`.

## Origin and evidence-bounded 5 Whys

Primary: product runtime discoverability/executor application. Contributing: activation-boundary mismatch. Secondary: scorer false positive. Not infrastructure/custody/authorization.

1. Residual disposition failed because the unresolved root cause was never recorded/dispositioned.
2. The answer treated containment plus future investigation as sufficient.
3. The installed product-specific rule was not invoked/read.
4. The ordinary hazard prompt does not naturally match the skill's audit-closure activation description, and the normative rule is deep in `PROTOCOL.md`.
5. The scorer understated the miss because loose capture grammar counted incidental words as candidate IDs.

Hypothesis: base-model safety reasoning ran without the #6 governing rule, so behavior stopped at containment. Falsify with an ordinary-vs-explicit invocation probe: if explicit product activation still omits residual state, discoverability alone is insufficient and rule clarity/salience is primary.

Countermeasure: surface one general hazard-plus-safe-containment trigger in the bootloader/reference map while keeping detail single-sourced; separately replace loose cause/residual regexes with labeled structured records.

Deterministic regression: the exact recorded answer must fail candidate enumeration and residual disposition; incidental `cause should`/plural `causes` never count; two labeled hypotheses plus a valid residual row pass; bootloader route presence is checked.

Targeted re-evaluation: three interleaved L candidate/control runs and one O confirmation, unchanged prompt, requiring actual skill-read evidence and structured causes/residuals.

Shared-rule candidates: ordinary task-shaped skill activation; progressive-disclosure routing; generic `count_distinct_at_least` capture weakness.

Andon disposition: **OPEN / failed-criterion plus evidence-mismatch**. One genuine product behavior miss and one scorer false-pass. Confidence 0.95 mechanics, 0.82 causal routing.

## Adversarial synthesis resolution

The scorer false-positive remains proven, but “genuine product behavior miss” is not an approved causal conclusion. The fixture asserts three causes without identifying them, while product doctrine permits a stated reason fewer can be supported. Product discoverability/application is therefore **unresolved** until a corrected evidence-bearing fixture and ordinary-versus-explicit activation probe falsify or support it. No product countermeasure is authorized from this cell yet.
