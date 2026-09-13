#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'durable-identity-contract.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

registry="skills/implementaudit/references/identity-namespaces.json"
resolver="skills/implementaudit/scripts/resolve-durable-identity.py"
checker="scripts/check-durable-identities.py"
campaign_plan="docs/superpowers/plans/2026-08-20-v041-thread5-autodag.md"

[ -f "$registry" ] || fail "missing canonical namespace registry"
[ -f "$resolver" ] || fail "missing packaged durable-identity resolver"
[ -f "$checker" ] || fail "missing maintained-source identity checker"
[ -f "$campaign_plan" ] || fail "missing maintained Thread-5 campaign plan"

grep -Fq 'Derived population: 68 total cells, comprising 10 control/planning cells and 58 execution cells. Exactly 38 execution cells are admitted implementation/action cells.' "$campaign_plan" \
  || fail "Thread-5 plan has stale derived implementation population"
grep -Fq '## Admitted implementation/action cells (38)' "$campaign_plan" \
  || fail "Thread-5 plan has stale admitted implementation heading"
grep -Fq 'It is not in the 38 implementation count.' "$campaign_plan" \
  || fail "Thread-5 plan has stale deferred-cell implementation population"
if grep -Fq 'not in the 37 implementation count' "$campaign_plan"; then
  fail "Thread-5 plan retained the stale 37-cell implementation population"
fi

"${py_cmd[@]}" "$resolver" --validate

assert_eq() {
  local expected="$1"; shift
  local observed
  observed="$("${py_cmd[@]}" "$resolver" "$@")" || fail "resolver failed: $*"
  [ "$observed" = "$expected" ] || fail "$*: expected $expected, got $observed"
}

assert_eq R0001 --canonical R01
assert_eq R000A --canonical R10
assert_eq R001C --canonical R28
assert_eq R0032 --canonical R50
assert_eq R0037 --canonical R55
assert_eq G003D --canonical e61
assert_eq G003E --canonical e62
assert_eq G003F --canonical e63
assert_eq G0040 --canonical e64
assert_eq R28 --legacy R001C
assert_eq e61 --legacy G003D
assert_eq 28 --ordinal R001C
assert_eq 40 --ordinal R0028
assert_eq R0038 --format R 56

for invalid in R1 r28 R000a R00001 G040 e0 X0001; do
  if "${py_cmd[@]}" "$resolver" --canonical "$invalid" >/dev/null 2>&1; then
    fail "malformed identity accepted: $invalid"
  fi
done

assert_eq R0037 --require-allocated R0037
assert_eq R0038 --require-allocated R0038
assert_eq R0039 --require-allocated R0039
assert_eq R003A --require-allocated R003A
if "${py_cmd[@]}" "$resolver" --require-allocated R003B >/dev/null 2>&1; then
  fail "the next unreserved Rockstar was silently allocated"
fi

for canonical_born in R0038 R0039 R003A; do
  if "${py_cmd[@]}" "$resolver" --legacy "$canonical_born" >/dev/null 2>&1; then
    fail "canonical-born Rockstar gained a fabricated legacy alias: $canonical_born"
  fi
done

"${py_cmd[@]}" - "$resolver" <<'PY'
import subprocess
import sys

resolver = sys.argv[1]
seen = {}
for ordinal in range(1, 56):
    alias = f"R{ordinal:02d}"
    expected = f"R{ordinal:04X}"
    canonical = subprocess.check_output(
        [sys.executable, resolver, "--canonical", alias], text=True
    ).strip()
    if canonical != expected:
        raise SystemExit(f"wrong mapping: {alias} -> {canonical}, expected {expected}")
    if canonical in seen:
        raise SystemExit(f"duplicate canonical identity: {canonical}")
    seen[canonical] = alias
    reverse = subprocess.check_output(
        [sys.executable, resolver, "--legacy", canonical], text=True
    ).strip()
    if reverse != alias:
        raise SystemExit(f"wrong reverse mapping: {canonical} -> {reverse}")
if len(seen) != 55:
    raise SystemExit("Rockstar bijection lost or minted an identity")
PY

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Current changelog selection must inspect the maintained sections, while
# archived release sections keep their original identities. Exercise main();
# only the Git membership boundary is replaced by the declared fixture file.
"${py_cmd[@]}" - "$checker" "$tmp" <<'PY'
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

checker = Path(sys.argv[1]).resolve()
scratch = Path(sys.argv[2]).resolve() / "current-changelog"
scratch.mkdir()
spec = importlib.util.spec_from_file_location("current_identity_checker", checker)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
family = json.loads((checker.parent.parent / "package/implementaudit-package.json").read_text())["release_family"]
history = "\n## [v0.4.0.0] - 2026-08-16\n\nCurrent owner R001C.\n\n## [v0.3.3.3] - 2026-08-11\n\nHistorical owner R28.\n"
bad_history = "\n## [v0.4.0.0] - 2026-08-16\n\nCurrent owner R28 and RFFFF.\nCurrent epoch: e61\n\n## [v0.3.3.3] - 2026-08-11\n\nHistorical owner R28.\n"
valid_current = "## [Unreleased]\n\nCurrent owner R001C.\n"
cases = [
    ("unreleased_legacy", "## [Unreleased]\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("current_release_legacy", valid_current + f"\n## [{family}] - 2026-09-11\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("unreleased_unallocated", "## [Unreleased]\n\nCurrent owner RFFFF.\n" + history, 1, "unallocated Rockstar presented as current RFFFF"),
    ("current_release_unallocated", f"## [{family}]\n\nCurrent owner RFFFF.\n" + history, 1, "unallocated Rockstar presented as current RFFFF"),
    ("current_generation", "## [Unreleased]\n\nCurrent epoch: e61\n" + history, 1, "stale maintained continuity generation"),
    ("current_subsection", "## [Unreleased]\n\n### Changed\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("fenced_heading_does_not_end_current", "## [Unreleased]\n\n```text\n## [v0.3.3.3]\n```\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("comment_heading_does_not_end_current", "## [Unreleased]\n\n<!--\n## [v0.3.3.3]\n-->\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("inline_heading_comment_retains_current_body", "## [Unreleased] <!-- current source -->\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("valid_inline_heading_comment", "## [Unreleased] <!-- current source -->\n\nCurrent owner R001C.\n" + bad_history, 0, ""),
    ("current_release_heading_suffix_retains_body", valid_current + f"\n## [{family}] - source candidate\n\nCurrent owner R28.\n" + history, 1, "stale maintained Rockstar R28"),
    ("valid_current_release_heading_suffix", valid_current + f"\n## [{family}] - source candidate\n\nCurrent owner R001C.\n" + bad_history, 0, ""),
    ("valid_current_and_history", valid_current + f"\n## [{family}]\n\nCurrent owner R001C.\n" + bad_history, 0, ""),
    ("explicit_current_exceptions", "## [Unreleased]\n\nLegacy alias R28 maps to R001C.\nHistorical epoch e61.\nRFFFF is unallocated.\n" + bad_history, 0, ""),
    ("current_release_without_unreleased", f"## [{family}]\n\nCurrent owner R001C.\n" + bad_history, 0, ""),
    ("missing_current_section", "## [v0.3.3.3]\n\nHistorical owner R28.\n", 1, "no maintained changelog section"),
    ("duplicate_unreleased", valid_current + "\n" + valid_current + history, 1, "duplicate maintained changelog section"),
    ("duplicate_current_release", f"## [{family}]\n\nCurrent owner R001C.\n\n## [{family}]\n\nCurrent owner R001C.\n" + history, 1, "duplicate maintained changelog section"),
]
results = []
for label, text, expected, diagnostic in cases:
    root = scratch / label
    root.mkdir()
    path = root / "CHANGELOG.md"
    raw = ("# Changelog\n\n" + text).encode("utf-8")
    path.write_bytes(raw)
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch.object(module, "tracked_files", return_value=["CHANGELOG.md"]), \
            patch.object(sys, "argv", [str(checker), "--scan-root", str(root)]), \
            contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        observed = module.main()
    assert path.read_bytes() == raw, label + ": checker mutated historical input"
    passed = observed == expected and diagnostic in stderr.getvalue()
    results.append({"case": label, "expected_exit": expected, "actual_exit": observed,
                    "stderr": stderr.getvalue(), "passed": passed})
print(json.dumps({"current_changelog_controls": results}, sort_keys=True))
if not all(row["passed"] for row in results):
    raise SystemExit("current changelog selection controls failed")
PY

git -C "$tmp" init -q
git -C "$tmp" config user.email identity-test@example.invalid
git -C "$tmp" config user.name identity-test
mkdir -p "$tmp/docs/audits/archive" "$tmp/docs"
printf '%s\n' 'Current owner R001C.' > "$tmp/README.md"
printf '%s\n' 'Legacy alias R28 maps to canonical R001C.' > "$tmp/docs/identity.md"
printf '%s\n' 'Historical R28 wording remains immutable.' > "$tmp/docs/audits/archive/legacy.md"
mkdir -p "$tmp/tests"
printf '%s\n' 'Fixture labels R35-F1, DOG-R01-combined-cell-timeout, and R36_TEST_GATE remain local identifiers.' > "$tmp/tests/local-labels.txt"
git -C "$tmp" add README.md docs tests
"${py_cmd[@]}" "$checker" --scan-root "$tmp" >/dev/null

printf '%s\n' 'Current owner R28.' > "$tmp/README.md"
if "${py_cmd[@]}" "$checker" --scan-root "$tmp" >/dev/null 2>&1; then
  fail "unmarked maintained legacy Rockstar spelling was accepted"
fi

printf '%s\n' 'Current owner R001C.' > "$tmp/README.md"
mkdir -p "$tmp/docs/R28"
printf '%s\n' 'current path owner' > "$tmp/docs/R28/index.md"
git -C "$tmp" add README.md docs/R28/index.md
if "${py_cmd[@]}" "$checker" --scan-root "$tmp" >/dev/null 2>&1; then
  fail "bare maintained legacy Rockstar path segment was accepted"
fi

"${py_cmd[@]}" "$checker"

printf 'durable-identity-contract.test: ok\n'
