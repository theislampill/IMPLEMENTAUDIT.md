#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-terminology-integration: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = "--repo-root" ]; then
  [ "$#" -ge 2 ] || fail "--repo-root requires a directory argument"
  repo_root="$2"
fi
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

"${py_cmd[@]}" - <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(".")
failures: list[str] = []


def read(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        failures.append(f"missing required file: {path}")
        return ""
    return p.read_text(encoding="utf-8")


def contains(text: str, needle: str) -> bool:
    normalize = lambda value: re.sub(r"\s+", " ", value.lower()).strip()
    return normalize(needle) in normalize(text)


def require(path: str, needle: str, label: str) -> None:
    text = read(path)
    if not contains(text, needle):
        failures.append(f"{path}: missing {label}: {needle}")


if (ROOT / "skills/references/runtime-terminology.md").exists():
    failures.append(
        "TERMINOLOGY_GLOSSARY_FILE: skills/references/runtime-terminology.md must not exist; "
        "use the thin terminology-integration.md contract"
    )

integration_path = "skills/references/terminology-integration.md"
integration = read(integration_path)
if integration:
    line_count = len(integration.splitlines())
    if line_count > 120:
        failures.append(
            f"{integration_path}: too large for KISS contract ({line_count} lines; max 120)"
        )
    forbidden_shapes = [
        "## Term Entries",
        "### VOC",
        "### FMEA",
        "### Poka-yoke",
        "### A3",
        "Native Terminology Map",
        "- Term:",
        "- Plain behavior:",
        "- Formal label:",
    ]
    for shape in forbidden_shapes:
        if shape.lower() in integration.lower():
            failures.append(
                f"TERMINOLOGY_TERM_ENTRY_DRIFT: {integration_path}: "
                f"second-glossary shape found: {shape}"
            )

for needle in [
    "## Precedence",
    "`tdqyq-audit-object` and `ydqyq-audit-action` own the audit ontology",
    "`skills/references/routing.md` owns greenfield/brownfield/mixed routing",
    "`skills/references/lean-operating-discipline.md` owns A3, Poka-yoke",
    "## Retained Hooks",
    "VOC / CTQ / SIPOC",
    "FMEA-lite",
    "Strangler / ACL",
    "Bounded Context / Ubiquitous Language",
    "STRIDE / trust boundary",
    "SOLID / GRASP",
    "C4 is deferred for v0.3.0.0",
    "## Orphan-term Rejection",
    "## Glossary-theater Rejection",
    "## Compact Runtime Flow",
]:
    if not contains(integration, needle):
        failures.append(f"{integration_path}: missing required KISS content: {needle}")

required_owner_hooks = {
    "skills/references/routing.md": [
        "VOC/CTQ/SIPOC as native field refinements",
        "Strangler Fig and Anti-Corruption Layer are",
        "The outer shell remains DMAIC; the new or replacement design remains DMADV",
        "Terminology Integration Guardrail",
        "SOLID/GRASP are not routing hooks in v0.3.0.0",
    ],
    "skills/references/phase-design.md": [
        "Terminology cannot be orphaned",
        "Existing references own their concepts",
        "numeric RPN theater",
    ],
    "skills/references/planning-depth.md": [
        "Do not add external terminology merely because it is familiar",
        "terminology integration fires",
        "SOLID/GRASP remains a checker/fixture negative guard only",
    ],
    "skills/references/plan-lifecycle.md": [
        "Control Plan / Standard Work / Poka-yoke sustain mechanism",
        "Strangler/ACL replacement work",
        'generic terminology requests such as "apply SOLID", "run STRIDE", or "do an',
        "SOLID/GRASP specifically remains a checker/fixture negative guard only",
    ],
    "skills/references/audit-category-matrix.md": [
        "STRIDE/trust-boundary checks where material",
        "repo-content-as-data handling",
        "SOLID/GRASP as checker-guarded negative design-advice controls",
    ],
    "skills/references/lean-operating-discipline.md": [
        "check-terminology-integration.sh",
        "Control Plan",
        "Terminology integration",
    ],
    "skills/SKILL.md": [
        "terminology-integration.md",
        "FMEA-lite fields when risk is material",
        "STRIDE/trust-boundary notes when a material security surface exists",
        "SOLID/GRASP generic-advice guard",
        "terminology integration attachment when used",
    ],
}

for path, needles in required_owner_hooks.items():
    text = read(path)
    for needle in needles:
        if not contains(text, needle):
            failures.append(f"{path}: missing owner hook: {needle}")

for path in [
    "fixtures/terminology-integration/full-stack-integration.md",
    "fixtures/terminology-integration/negative-glossary-orphan.md",
    "fixtures/terminology-integration/negative-generic-advice.md",
]:
    text = read(path)
    for needle in [
        "Fixture status:",
        "Native parent:",
        "Runtime phase:",
        "Route",
        "Evidence boundary:",
        "Andon",
        "scripts/check-terminology-integration.sh",
    ]:
        if not contains(text, needle):
            if needle == "Native parent:":
                failures.append(
                    f"TERMINOLOGY_MISSING_NATIVE_PARENT: {path}: "
                    f"missing fixture field: {needle}"
                )
            else:
                failures.append(f"{path}: missing fixture field: {needle}")

positive = read("fixtures/terminology-integration/full-stack-integration.md")
for needle in [
    "no orphan terms",
    "no duplicate authorities",
    "no glossary-only list",
    "no separate terminology lane",
]:
    if not contains(positive, needle):
        failures.append(f"full-stack fixture missing proof assertion: {needle}")

negative_glossary = read("fixtures/terminology-integration/negative-glossary-orphan.md")
for needle in [
    "Expected Rejection",
    "glossary theater",
    "no native parent",
]:
    if not contains(negative_glossary, needle):
        failures.append(f"negative glossary fixture missing rejection proof: {needle}")

negative_generic = read("fixtures/terminology-integration/negative-generic-advice.md")
for needle in [
    "Apply SOLID",
    "run FMEA",
    "use STRIDE",
    "numeric RPN",
    "Expected Rejection",
]:
    if not contains(negative_generic, needle):
        failures.append(f"negative generic fixture missing bad prompt/rejection: {needle}")

scan_paths: list[Path] = []
for base in ["skills"]:
    scan_paths.extend(p for p in (ROOT / base).rglob("*") if p.is_file())
portal_terminology = ROOT / "docs/portal/pages/terminology.html"
if portal_terminology.is_file():
    scan_paths.append(portal_terminology)
scan_paths.extend(
    p
    for p in (ROOT / "fixtures/terminology-integration").glob("*.md")
    if not p.name.startswith("negative-")
)

term_pattern = re.compile(
    r"\b(VOC|CTQ|SIPOC|FMEA(?:-lite)?|Strangler|Anti-Corruption|ACL|"
    r"Bounded Context|Ubiquitous Language|STRIDE|trust boundary|SOLID|GRASP|"
    r"Control Plan|C4)\b",
    re.IGNORECASE,
)
anchor_pattern = re.compile(
    r"(native parent|owner/source|phase|route|lens|evidence boundary|andon|"
    r"andon/control hook|plan closure|sustain|dmaic|dmadv|security pressure|"
    r"checker|fixture|final audit|acceptance criteria|deferred|source repo|"
    r"source-of-truth)",
    re.IGNORECASE,
)
bad_generic = re.compile(
    r"(apply SOLID|use GRASP|run FMEA|do an FMEA|use STRIDE|run STRIDE)",
    re.IGNORECASE,
)
rpn_theater = re.compile(
    r"(compute numeric RPN|numeric RPN|severity, occurrence, or detection scores)",
    re.IGNORECASE,
)
negative_context = re.compile(
    r"(reject|forbidden|without measured evidence|generic|negative guard|must not|do not invent)",
    re.IGNORECASE,
)

for path in sorted(scan_paths):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    rel = path.as_posix()
    paragraphs = re.split(r"\n\s*\n", text)
    for idx, para in enumerate(paragraphs, 1):
        if not term_pattern.search(para):
            continue
        if "C4" in para and "deferred for v0.3.0.0" not in para and integration_path not in rel:
            failures.append(
                f"TERMINOLOGY_DEFERRED_C4_ACTIVE: {rel}: paragraph {idx}: "
                "C4 is deferred for v0.3.0.0"
            )
        if rpn_theater.search(para) and not negative_context.search(para):
            failures.append(
                f"TERMINOLOGY_RPN_THEATER: {rel}: paragraph {idx}: "
                "numeric RPN theater without measured evidence"
            )
        if bad_generic.search(para) and not negative_context.search(para):
            failures.append(
                f"TERMINOLOGY_GENERIC_ADVICE: {rel}: paragraph {idx}: "
                "generic terminology advice is not rejected"
            )
        if not anchor_pattern.search(para):
            sample = " ".join(para.strip().split())[:140]
            term_count = len(term_pattern.findall(para))
            code = "TERMINOLOGY_GLOSSARY_ONLY" if term_count >= 4 else "TERMINOLOGY_ORPHAN_TERM"
            failures.append(
                f"{code}: {rel}: paragraph {idx}: terminology without native attachment: {sample}"
            )

if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-terminology-integration: ok\n")
PY
