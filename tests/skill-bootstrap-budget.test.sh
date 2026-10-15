#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-skill-bootstrap-budget.sh

if bash scripts/check-skill-bootstrap-budget.sh \
  --skill-file fixtures/skill-bootstrap-budget/negative-full-read-installed-payload.md \
  --max-lines 450 \
  --max-bytes 22000 \
  >"$tmp/negative.out" 2>&1; then
  printf 'skill-bootstrap-budget.test: negative installed-payload fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "forbidden installed-payload readback instruction" "$tmp/negative.out" >/dev/null || {
  printf 'skill-bootstrap-budget.test: expected installed-payload readback diagnostic\n' >&2
  cat "$tmp/negative.out" >&2
  exit 1
}

cp skills/implementaudit/SKILL.md "$tmp/oversized.md"
for _ in $(seq 1 500); do
  printf 'padding line for budget regression\n' >>"$tmp/oversized.md"
done

if bash scripts/check-skill-bootstrap-budget.sh \
  --skill-file "$tmp/oversized.md" \
  --max-lines 450 \
  --max-bytes 22000 \
  >"$tmp/oversized.out" 2>&1; then
  printf 'skill-bootstrap-budget.test: oversized fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "bootloader too long" "$tmp/oversized.out" >/dev/null || {
  printf 'skill-bootstrap-budget.test: expected size budget diagnostic\n' >&2
  cat "$tmp/oversized.out" >&2
  exit 1
}

# The unchanged ceiling must also leave room for one complete moved stage.
# This is a bounded restoration allowance, not a promise about future growth.
if command -v python >/dev/null 2>&1; then py_cmd=(python); else py_cmd=(python3); fi
"${py_cmd[@]}" - "$tmp" "$BASH" <<'PY'
import json
from pathlib import Path
import shutil
import subprocess
import sys

source = Path.cwd()
target = Path(sys.argv[1]) / "bootstrap"
target.mkdir()
shutil.copytree(source / "skills", target / "skills")
for name in ("scripts/check-skill-bootstrap-budget.sh", "scripts/package-contract.py",
             "package/implementaudit-package.json", "fixtures/semantic-preservation/cases.json",
             "fixtures/semantic-preservation/evaluate.py", "fixtures/semantic-preservation/test-cases.sh"):
    dest = target / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / name, dest)
governor = target / "skills/implementaudit/SKILL.md"
owner = target / "skills/implementaudit/references/plan-lifecycle.md"
original_governor = governor.read_bytes()
original_owner = owner.read_bytes()

def check(label, expected):
    result = subprocess.run([sys.argv[2], "scripts/check-skill-bootstrap-budget.sh"],
                            cwd=target, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if expected is None:
        assert result.returncode == 0, (label, output)
    else:
        assert result.returncode != 0 and expected in output, (label, result.returncode, output)
    print("bootstrap-control: " + label)

# Retain this original defect even after the source becomes smaller.
assert len(original_governor) <= 21999
governor.write_bytes(original_governor + b" " * (21999 - len(original_governor)))
check("under-ceiling-one-byte-reserve", "semantic reserve")
governor.write_bytes(original_governor)
check("complete-progressive-route", None)

binding = json.loads((target / "fixtures/semantic-preservation/cases.json").read_text())["bootstrap_route"]
route = binding["governor_route"]
text = original_governor.decode()
assert route in text
for label, replacement in (
    ("missing-trigger-reference-still-present", ""),
    ("commented-trigger", "<!--\n" + route + "\n-->"),
    ("quoted-trigger", "> " + route.replace("\n", "\n> ")),
    ("inert-trigger", "```text\n" + route + "\n```"),
    ("wrong-owner-route", route.replace("references/plan-lifecycle.md#", "references/routing.md#")),
):
    governor.write_text(text.replace(route, replacement), encoding="utf-8", newline="")
    check(label, "active planner route")
run_root_edge = route.split("\n\n")[-1]
assert run_root_edge.startswith("When a run root is needed, claim it with")
governor.write_text(text.replace(run_root_edge, "<!--\n" + run_root_edge + "\n-->"),
                   encoding="utf-8", newline="")
check("inert-run-root-edge-with-stage-owner-retained", "active planner route")
governor.write_text(text.replace(route, " ".join(route.split())), encoding="utf-8", newline="")
check("equivalent-route-reflow", None)
governor.write_bytes(original_governor)

for label, content in (
    ("missing-owner", None),
    ("wrong-version-owner", original_owner.replace(b"### Stage 5 -", b"### Stage X -", 1)),
    ("mixed-owner", original_owner + b"\nConflicting foreign stage owner.\n"),
):
    if content is None:
        owner.unlink()
    else:
        owner.write_bytes(content)
    check(label, "planner owner")
    owner.write_bytes(original_owner)
check("restored-complete-route", None)
PY

printf 'skill-bootstrap-budget.test: ok\n'
