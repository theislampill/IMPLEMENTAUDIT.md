#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-lean-discipline: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" <<'PY'
from pathlib import Path

ROOT = Path(".")
failures = []


def read(path):
    p = ROOT / path
    if not p.is_file():
        failures.append(f"missing required file: {path}")
        return ""
    return p.read_text(encoding="utf-8").lower()


def require(text, needle, label, path):
    if needle.lower() not in text:
        failures.append(f"{path}: missing {label}: {needle}")


# 1. lean-operating-discipline.md must exist and be runtime-load-bearing
lean_ref = "skills/references/lean-operating-discipline.md"
lean = read(lean_ref)
for needle in [
    "gemba",
    "kaizen",
    "hansei",
    "jidoka",
    "5s",
    "muda",
    "mura",
    "muri",
    "dmaic",
    "dmadv",
    "poka-yoke",
    "evidence bound",
    "not decorative",
]:
    require(lean, needle, "lean reference content", lean_ref)

# 2. 5S must appear in PROTOCOL.md
proto_path = "skills/templates/PROTOCOL.md"
proto = read(proto_path)
for needle in [
    "5s_check",
    "seiri",
    "seiton",
    "seiso",
    "seiketsu",
    "shitsuke",
]:
    require(proto, needle, "5S gate", proto_path)

# 3. Jidoka stop-the-line chain must appear in PROTOCOL.md
for needle in [
    "jidoka",
    "jidoka trigger",
    "failure_probe",
    "hansei",
    "kaizen standardization",
]:
    require(proto, needle, "Jidoka chain", proto_path)

# 4. Nemawashi must appear in PROTOCOL.md
require(proto, "nemawashi", "Nemawashi gate", proto_path)

# 5. Muda/Mura/Muri register must appear in THINKING.md
thinking_path = "skills/templates/THINKING.md"
thinking = read(thinking_path)
for needle in [
    "muda",
    "mura",
    "muri",
]:
    require(thinking, needle, "Muda/Mura/Muri register", thinking_path)

# 6. DMAIC/DMADV must appear in THINKING.md and routing.md
require(thinking, "dmaic", "DMAIC route", thinking_path)
require(thinking, "dmadv", "DMADV route", thinking_path)

routing_path = "skills/references/routing.md"
routing = read(routing_path)
require(routing, "dmaic", "DMAIC routing", routing_path)
require(routing, "dmadv", "DMADV routing", routing_path)

# 7. Quality route field must appear in phase-goal.txt
phase_goal_path = "skills/templates/phase-goal.txt"
phase_goal = read(phase_goal_path)
require(phase_goal, "quality route", "Quality route field", phase_goal_path)

# 8. lean-operating-discipline.md must NOT claim sigma level, DPMO,
#    or certification beyond repo-local runtime behavior.
#    Negative-context sentences (e.g. "Do not claim sigma level") are allowed.
forbidden_claims = [
    "six sigma certification",
    "sigma level",
    "dpmo",
    "statistical process control",
    "certified lean",
    "lean certification",
]
negative_context = (
    "do not claim",
    "not claim",
    "no ",
    "does not claim",
    "must not claim",
    "is not claimed",
    "are not claimed",
    "without claiming",
    "cannot be claimed",
    "no sigma",
    "no dpmo",
    "no certification",
    "not six sigma",
    "not a six sigma",
    "are not claimed",
    "certification claim",
    "not claimed",
)
for phrase in forbidden_claims:
    for line in lean.splitlines():
        if phrase in line and not any(ctx in line for ctx in negative_context):
            failures.append(
                f"{lean_ref}: forbidden overclaim found: '{phrase}' — "
                "lean-operating-discipline.md must not claim certification or statistical proof"
            )
            break

# 9. Lean fixtures must exist
required_fixtures = [
    "fixtures/lean/brownfield-dmaic-release-repair.md",
    "fixtures/lean/brownfield-dmaic-stale-docs.md",
    "fixtures/lean/greenfield-dmadv-new-runtime-helper.md",
    "fixtures/lean/mixed-dmaic-dmadv-package-boundary.md",
    "fixtures/lean/sidecar-graphify-absent-markdown-fallback.md",
    "fixtures/lean/sidecar-graphify-dmaic-analyze.md",
    "fixtures/lean/sidecar-activegraph-dmaic-custody.md",
]
for f in required_fixtures:
    if not (ROOT / f).is_file():
        failures.append(f"missing required fixture: {f}")

# 10. Package payload must not contain general Lean essays
#     (lean-operating-discipline.md ships because it is runtime-load-bearing;
#      audit ledgers under docs/ do not ship)
docs_in_skills = [
    p for p in (ROOT / "skills").rglob("*.md")
    if "lean-operating-discipline" not in p.name
    and "lean" in p.name.lower()
    and p.is_file()
]
if docs_in_skills:
    for p in docs_in_skills:
        failures.append(
            f"package payload bloat: unexpected Lean doc in skills/: {p} — "
            "audit ledgers and general Lean essays must not ship in the package"
        )

# 11. lean-operating-discipline.md must include Graphify terrain leverage section
for needle in [
    "graphify terrain leverage",
    "seiri",
    "seiton",
    "seiso",
    "orientation only, not proof",
    "live-file confirmation",
    "dmaic",
    "dmadv",
]:
    require(lean, needle, "Graphify terrain leverage section", lean_ref)

# 12. lean-operating-discipline.md must include ActiveGraph custody events section
for needle in [
    "activegraph custody events",
    "implementaudit.run.opened",
    "gemba.graphify.queried",
    "dmaic.define.recorded",
    "poka_yoke.check.recorded",
    "implementaudit-defined custom events",
    "custody stores",
    "never committed",
    "narrow",
]:
    require(lean, needle, "ActiveGraph custody events section", lean_ref)

if failures:
    raise SystemExit("\n".join(failures))
PY

printf 'check-lean-discipline: ok\n'
