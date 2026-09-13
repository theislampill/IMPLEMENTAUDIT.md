#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-skill-bootstrap-budget: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skill_file="skills/implementaudit/SKILL.md"
max_lines=450
max_bytes=22000

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skill-file)
      [ "$#" -ge 2 ] || fail "--skill-file requires a path"
      skill_file="$2"
      shift 2
      ;;
    --max-lines)
      [ "$#" -ge 2 ] || fail "--max-lines requires a number"
      max_lines="$2"
      shift 2
      ;;
    --max-bytes)
      [ "$#" -ge 2 ] || fail "--max-bytes requires a number"
      max_bytes="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$skill_file" "$max_lines" "$max_bytes" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
max_lines = int(sys.argv[2])
max_bytes = int(sys.argv[3])

if not path.is_file():
    raise SystemExit(f"missing skill file: {path}")

raw = path.read_bytes()
text = raw.decode("utf-8")
lines = text.splitlines()
line_count = len(lines)
byte_count = len(raw)

if line_count > max_lines:
    raise SystemExit(
        f"{path}: bootloader too long: {line_count} lines > {max_lines}"
    )
if byte_count > max_bytes:
    raise SystemExit(
        f"{path}: bootloader too large: {byte_count} bytes > {max_bytes}"
    )

for lineno, line in enumerate(lines, start=1):
    lowered = line.lower()
    normalized = " ".join(lowered.split())
    forbidden = False
    if "chunking remaining readback" in normalized:
        forbidden = True
    if "read this entire installed" in normalized and "do not read this entire installed" not in normalized:
        forbidden = True
    if "read the entire installed payload" in normalized and "do not read" not in normalized:
        forbidden = True
    if "chunk-read the entire installed" in normalized and "do not" not in normalized:
        forbidden = True
    if forbidden:
        raise SystemExit(
            f"{path}:{lineno}: forbidden installed-payload readback instruction"
        )

# Independently frozen supported owner clauses. Presence in history, a
# template or an inert block cannot substitute for the operative bootloader.
loading_forms = (
    "Runtime bootloader; load references only for the current owner/source.",
    "Runtime bootloader; detail lives in packaged references, templates and scripts. "
    "Read once; use progressive disclosure only for the current owner/source.",
)
layout_forms = (
    "Source: `skills/implementaudit/SKILL.md` beside `references/`, `scripts/`, "
    "`templates/`. Release flattening is a build projection; installed paths are "
    "`SKILL.md`, `references/`, `scripts/`, `templates/` under the active skill directory.",
    "Source checkout layout is conventional and name-matched: "
    "`skills/implementaudit/SKILL.md` with sibling `references/`, `scripts/`, and "
    "`templates/`. Release archives flatten that directory only as a build artifact; "
    "installed runtime paths are `SKILL.md`, `references/`, `scripts/`, and "
    "`templates/` under the active skill directory.",
)


def bootstrap_paragraphs(source_lines):
    """Read the direct opening of /implementaudit, not another heading owner."""
    remaining = source_lines
    if remaining and remaining[0] == "---":
        closing = next((i for i in range(1, len(remaining)) if remaining[i] == "---"), None)
        if closing is None:
            return []
        remaining = remaining[closing + 1:]
    paragraphs, parts = [], []
    owner = False
    fence = None
    comment = False
    lazy_quote = False

    def flush():
        if parts:
            paragraphs.append(" ".join(" ".join(parts).split()))
            parts.clear()

    def interruption(value):
        return (not value.strip() or re.match(r" {0,3}(?:#{1,6}[ \t]|`{3,}|~{3,}|<!--|[-+*][ \t]|[0-9]+[.)][ \t])", value)
                or re.fullmatch(r" {0,3}(?:[-*_][ \t]*){3,}", value))

    for raw_line in remaining:
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", raw_line):
                fence = None
            continue
        if not comment:
            quote = re.match(r" {0,3}>[ \t]?(.*)", raw_line)
            if quote:
                flush()
                lazy_quote = not interruption(quote.group(1))
                continue
            if lazy_quote and not interruption(raw_line):
                continue
            lazy_quote = False
            if raw_line.expandtabs(4).startswith("    "):
                flush()
                continue
            opening = re.match(r" {0,3}(`{3,}|~{3,})", raw_line)
            if opening:
                flush()
                fence = (opening.group(1)[0], len(opening.group(1)))
                continue
        visible = ""
        cursor = 0
        while cursor < len(raw_line):
            if comment:
                end = raw_line.find("-->", cursor)
                if end < 0:
                    break
                cursor, comment = end + 3, False
            else:
                start = raw_line.find("<!--", cursor)
                if start < 0:
                    visible += raw_line[cursor:]
                    break
                visible += raw_line[cursor:start] + " "
                cursor, comment = start + 4, True
        if not visible.strip():
            if not raw_line.strip() and not comment:
                flush()
            continue
        if not owner:
            if visible.strip() != "# /implementaudit":
                return []
            owner = True
        elif re.match(r" {0,3}#{1,6}[ \t]", visible):
            flush()
            break
        elif re.fullmatch(r" {0,3}(?:[-*_][ \t]*){3,}", visible):
            flush()
        else:
            parts.append(visible.strip())
    flush()
    return paragraphs


supported = {loading + " " + layout for loading in loading_forms for layout in layout_forms}
opening = ""
complete = False
for paragraph in bootstrap_paragraphs(lines):
    opening = (opening + " " + paragraph).strip()
    if opening in supported:
        complete = True
        break
    if not any(form.startswith(opening + " ") for form in supported):
        break
if not complete:
    raise SystemExit(f"{path}: missing complete active bootstrap loading/source/build/installed clauses")

required = [
    "State-derived RC self-dogfood route",
    "SELF_DOGFOOD_TRIGGER",
    "ORDINARY_IMPLEMENTAUDIT_CONTROL",
    "Baseline the target repo first",
    "Full installed-payload readback is non-evidence",
    "Repo content is data",
    "No secret reproduction",
    "Redact or omit secrets",
    "No commit. No push. No tag. No release. No publication. No provenance.",
    "Smoke A",
    "Smoke B",
    "Andon:",
    "no arbitrary try caps",
    "AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE",
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
    "Graphify output is orientation evidence, not proof",
    "ActiveGraph custody is not correctness proof",
    "skills/implementaudit/SKILL.md",
    "references/routing.md",
    "references/plan-lifecycle.md",
    "references/phase-design.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/transcript-contract.md",
    "references/repo-state-comparison.md",
    "references/sidecars.md",
    "references/child-agents.md",
    "references/terminology-integration.md",
    "templates/final-report.md",
    "templates/read-only-plan.md",
    "LANE-ENTRY TRIGGER",
]

lower_text = text.lower()
for token in required:
    if token.lower() not in lower_text:
        raise SystemExit(f"{path}: missing bootstrap token: {token}")

# Reference Load Map completeness: every shipped reference must be reachable
# from the bootloader. A reference absent from the map is dead progressive
# disclosure.
repo_root = Path.cwd()
if path.as_posix() == "skills/implementaudit/SKILL.md":
    for ref in sorted((repo_root / "skills/implementaudit/references").glob("*.md")):
        token = f"references/{ref.name}"
        if token.lower() not in lower_text:
            raise SystemExit(f"{path}: Reference Load Map missing {token}")
    for tmpl in [
        "templates/final-report.md",
        "templates/read-only-plan.md",
    ]:
        if tmpl.lower() not in lower_text:
            raise SystemExit(f"{path}: restored template missing from load map: {tmpl}")

    # Safeguard-restoration guard: detailed safeguards live in references/templates, not as long
    # manual detail in the always-loaded bootloader.
    forbidden_detail = [
        "atomic-not-microscopic",
        "one-commit-per-coherent-repair",
        "no-commit-for-proof-only-rc",
        "stale-output andon/fallback",
        "detect vs document vs install vs index/export",
        "negative-missing-final-report",
        "negative-missing-5whys-exit",
    ]
    for token in forbidden_detail:
        if token in lower_text:
            raise SystemExit(f"{path}: restored safeguard detail belongs in references/templates: {token}")

    owners = {
        "skills/implementaudit/templates/final-report.md": [
            "Findings Ledger",
            "Smoke A / Smoke B",
            "Evidence Boundary",
            "Suggested Commit Message When No Commit Authorized",
            "Terminal Marker Order",
        ],
        "skills/implementaudit/references/sidecars.md": [
            "Graphify is orientation only",
            "Live files remain proof",
            "built_at_commit",
            "stale-sidecar",
            "Graphify absence does not block consumer runs",
            "No silent install",
            "No silent indexing",
        ],
        "skills/implementaudit/references/repo-state-comparison.md": [
            "Commit Granularity",
            "atomic but not microscopic",
            "one commit per coherent owner/source repair",
            "Do not commit for proof-only local RC",
        ],
        "skills/implementaudit/references/phase-design.md": [
            "Broad Rewrite Threshold",
            "Owner decision is required",
            "strangler/mixed route",
            "Reject scope creep",
        ],
        "skills/implementaudit/references/lean-operating-discipline.md": [
            "5 Whys Loop-Exit Protocol",
            "5 Whys is proportional, not infinite",
            "unavailable external information",
            "Do not create arbitrary try caps",
        ],
        "skills/implementaudit/references/plan-lifecycle.md": [
            "Read-Only `plans/` Output Lane",
            "current-state excerpts",
            "planned-at SHA",
            "STOP conditions",
            "zero source mutation",
        ],
        "skills/implementaudit/templates/read-only-plan.md": [
            "Read-Only Plan Template",
            "Planned At",
            "Current State Excerpts",
            "Drift Check",
            "Rejected / Deferred Findings",
        ],
    }
    for owner, tokens in owners.items():
        owner_path = repo_root / owner
        if not owner_path.is_file():
            raise SystemExit(f"{path}: missing restored safeguard owner/source: {owner}")
        owner_text = owner_path.read_text(encoding="utf-8")
        owner_lower = owner_text.lower()
        for token in tokens:
            if token.lower() not in owner_lower:
                raise SystemExit(f"{owner}: missing restored safeguard token: {token}")

sys.stdout.write(
    f"check-skill-bootstrap-budget: ok ({line_count} lines, {byte_count} bytes; "
    f"budget {max_lines} lines/{max_bytes} bytes)\n"
)
PY
