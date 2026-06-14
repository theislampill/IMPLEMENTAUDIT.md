# Sidecar fixture: sidecar boundary overclaim — rejected

This fixture documents the overclaim patterns that check-sidecar-boundaries.sh
detects and rejects. It does NOT contain any rejected overclaim itself; it
documents what those claims are and why they are disallowed.

## Disallowed overclaim examples (detected by check-sidecar-boundaries.sh)

The following phrases must NOT appear in tracked skills, README.md, or AGENTS.md:

- "Graphify output proves correctness" — upgrades orientation evidence to proof
- "ActiveGraph is proof" — upgrades custody to correctness proof
- Any phrase claiming Graphify or ActiveGraph as proof rather than orientation/custody

## Required boundary language (must appear in tracked skills)

The following constraints must appear in skills/implementaudit/SKILL.md:

- "Graphify output is orientation evidence, not proof"
- "ActiveGraph custody is not correctness proof"
- "Missing, stale, or unauthorized sidecars must route to Markdown fallback"

## How check-sidecar-boundaries.sh enforces this

check-sidecar-boundaries.sh verifies that the required boundary language is
present in skills/implementaudit/SKILL.md and that no overclaim phrases appear in tracked
native surfaces (skills/, README.md, AGENTS.md).

An overclaim violation fails the check immediately. The test in sidecars.test.sh
verifies that mutating SKILL.md to say "proves correctness" causes the check
to fail (negative test).

## Rule confirmed by this fixture

- Graphify = orientation evidence (not proof)
- ActiveGraph = custody evidence (not correctness proof)
- Both sidecars have documented "not proof" language in native surfaces
- check-sidecar-boundaries.sh enforces these boundaries automatically
