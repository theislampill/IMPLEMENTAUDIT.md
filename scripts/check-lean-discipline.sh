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


def table_row(text, term):
    needle = f"| {term.lower()} |"
    for line in text.splitlines():
        if line.strip().startswith(needle):
            return line
    failures.append(f"missing Lean table row: {term}")
    return ""


def require_row(row, needle, label, path):
    if row and needle.lower() not in row:
        failures.append(f"{path}: {label} missing in row: {needle}")


def reject_row(row, phrase, label, path):
    if row and phrase.lower() in row:
        failures.append(f"{path}: {label}: {phrase}")


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
    "andon_probe",
    "andon log",
    "andon.probe.recorded",
    "custody.db",
    "hansei",
    "kaizen standardization",
]:
    require(proto, needle, "Jidoka chain", proto_path)

# 3b2. The sidecars run-root template must ship with its contract content
sidecars_path = "skills/templates/sidecars.md"
sidecars = read(sidecars_path)
for needle in [
    "orientation only",
    "custody.db",
    "historical_backfill",
    "query log",
]:
    require(sidecars, needle, "sidecars template contract", sidecars_path)

# 3c. Andon custody events must exist in the lean reference event table
for needle in [
    "andon.probe.recorded",
    "andon.escalated",
    "andon.handoff.recorded",
]:
    require(lean, needle, "Andon custody events", lean_ref)

# 3c2. Lean terms must keep concrete runtime force.
jidoka_row = table_row(lean, "jidoka")
require_row(jidoka_row, "stop-the-line", "Jidoka stop-the-line behavior", lean_ref)
require_row(jidoka_row, "andon", "Jidoka Andon chain", lean_ref)
require_row(jidoka_row, "owner/source", "Jidoka owner/source routing", lean_ref)
reject_row(jidoka_row, "generic error", "Jidoka reduced to a generic error label", lean_ref)

andon_row = table_row(lean, "andon")
require_row(andon_row, "visible abnormality", "Andon visible abnormality signal", lean_ref)
require_row(andon_row, "owner/source", "Andon owner/source routing", lean_ref)
require_row(andon_row, "next concrete action", "Andon next-action requirement", lean_ref)
reject_row(andon_row, "generic error", "Andon reduced to a generic error label", lean_ref)

poka_yoke_row = table_row(lean, "poka-yoke")
require_row(poka_yoke_row, "structural mistake-proofing", "Poka-yoke concrete prevention", lean_ref)
if poka_yoke_row and not any(token in poka_yoke_row for token in ("checker", "fixture", "template", "ci gate", "validation", ".sh")):
    failures.append(
        f"{lean_ref}: Poka-yoke row lacks a concrete checker/template/fixture/CI/validation mechanism"
    )

standard_work_row = table_row(lean, "standard work")
require_row(standard_work_row, "stable", "Standard Work stability boundary", lean_ref)
if standard_work_row and not any(token in standard_work_row for token in ("template", "checker", "fixture", "agents.md", "ci gate", "rule")):
    failures.append(
        f"{lean_ref}: Standard Work row lacks a stable repo-specific template/checker/rule"
    )

# 3a. Andon class + version-skew discipline must exist in the canonical skill
skill_path = "skills/SKILL.md"
skill = read(skill_path)
for needle in [
    "andon:",
    "class:",
    "abnormality class",
    "version skew",
]:
    require(skill, needle, "Andon class / version-skew discipline", skill_path)

# 3b. Andon log substrate must exist in the STATE.md template
state_path = "skills/templates/STATE.md"
state = read(state_path)
for needle in [
    "## andon log",
    "abnormality class",
    "rerun evidence",
    "status values:",
]:
    require(state, needle, "Andon log substrate", state_path)

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

category_path = "skills/references/audit-category-matrix.md"
category_matrix = read(category_path)
for needle in [
    "security review is also a default pressure",
    "direction analysis routes through dmadv",
    "deep analysis is a default pressure",
]:
    require(category_matrix, needle, "audit-object-routing default pressure", category_path)

plan_lifecycle_path = "skills/references/plan-lifecycle.md"
plan_lifecycle = read(plan_lifecycle_path)
for needle in [
    "no arbitrary revision cap",
    "continue until terminal closure or audited handoff",
    "issue publication deferred",
]:
    require(plan_lifecycle, needle, "audit-object-routing lifecycle boundary", plan_lifecycle_path)

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
