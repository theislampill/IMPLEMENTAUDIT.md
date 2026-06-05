# Zero Optional Tool Complete Run Example

This worked example shows a complete small `/implementaudit` run when Graphify
and ActiveGraph are absent. Missing optional tools are recorded, not treated as
errors.

## Optional tooling ledger

| Tool | Status | Action | Authorization | Evidence | Remaining risk |
|---|---|---|---|---|---|
| Graphify | absent | skipped; ordinary Gemba used | none | `GRAPHIFY_ABSENT` | dependency paths may require manual inspection |
| ActiveGraph | absent | skipped; Markdown ledger/final report used | none | `ACTIVEGRAPH_ABSENT` | no custody event export |

## Findings ledger

| # | Finding | Priority | Owner/source | Action | Status | Evidence |
|---|---|---:|---|---|---|---|
| 1 | README safety wording drifted from the skill contract | P1 | `skills/SKILL.md`, `README.md` | patched README wording only | changed | `git diff --check -- README.md` |

## Smoke A

| Check | Command | Result | Evidence type | Classification |
|---|---|---|---|---|
| Read source contract | manual inspection of `skills/SKILL.md` and `README.md` | drift found | manual inspection | target |
| Whitespace check | `git diff --check -- README.md` | clean baseline | static checker | target |

## Smoke B

| Check | Command | Result | Evidence type | Remaining risk |
|---|---|---|---|---|
| README source consistency | manual inspection against `skills/SKILL.md` | pass | manual inspection | prose could still age |
| Whitespace check | `git diff --check -- README.md` | pass | static checker | no runtime host install proof |

## Proposed commit body

```text
Finding:
- README safety wording drifted from the canonical skill contract.

Countermeasure:
- Updated README wording to match `skills/SKILL.md`.

Smoke B:
- git diff --check -- README.md
- manual README/source consistency inspection

Boundaries preserved:
- No Graphify install or indexing.
- No ActiveGraph setup or export.
- No commit, push, tag, release, publication, or provenance.
```

## Final report excerpt

```text
Graphify-assisted Gemba:
- Graphify was absent.
- Ordinary Gemba fallback was used.
- No graph output was treated as proof.

Capability Ledger:
- ActiveGraph was absent.
- No Capability Ledger events were derived.
- Markdown ledger and final report fallback were used.

AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
```
