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

[ -f "$registry" ] || fail "missing canonical namespace registry"
[ -f "$resolver" ] || fail "missing packaged durable-identity resolver"
[ -f "$checker" ] || fail "missing maintained-source identity checker"

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

# Published research references do not extend the runtime allocation registry.
# These cases exercise the scanner against real, separately tracked fixtures.
"${py_cmd[@]}" - "$checker" <<'PY'
import json
from pathlib import Path
import subprocess
import sys
import tempfile

checker = str(Path(sys.argv[1]).resolve())
portal = "docs/portal/pages/research-lineage-evolved-bwp.html"
outline = "docs/research/implementaudit/evolved-programme-v1/ROUGH_RLGWO_OUTLINES.md"
receipt = "docs/research/implementaudit/evolved-programme-v1/OWNERSHIP_RECONCILIATION_20261113.json"
# Independently recorded issue identities, not values imported from the checker.
carriers = {
    "R003B": 226, "R003C": 228, "R003D": 227,
    "R003F": 225, "R0040": 229, "R0041": 230,
    "R0043": 232, "R0044": 231, "R0045": 233,
}
cases = []
for identity, issue in carriers.items():
    text = f"Existing published carrier {identity} / #{issue}.\n"
    cases.append((f"published-portal-{identity}", portal, text, None))
    cases.append((f"runtime-refuses-{identity}", "skills/implementaudit/references/current-owner.md", text, identity))
all_carriers = "Published carrier references: " + ", ".join(carriers) + ".\n"
cases.extend([
    ("published-outline", outline, all_carriers, None),
    ("published-receipt", receipt, json.dumps({"published_carriers": list(carriers)}), None),
    ("embedded-carrier", portal, "Existing R003F::BWP-LANE-CONTINUATION.\n", None),
    ("ordinary-readme-refuses", "README.md", "Current owner R003F.\n", "R003F"),
    ("other-portal-refuses", "docs/portal/pages/overview.html", "Current owner R003F.\n", "R003F"),
    ("nested-portal-refuses", "docs/portal/pages/research-lineage-other/entry.html", "Current owner R003F.\n", "R003F"),
    ("non-documentary-suffix-refuses", "docs/research/implementaudit/evolved-programme-v1/owner.py", "Current owner R003F.\n", "R003F"),
    ("unobserved-gap-refuses", portal, "Current owner R003E.\n", "R003E"),
    ("unknown-portal-refuses", portal, "Current owner R0046.\n", "R0046"),
    ("unknown-outline-refuses", outline, "Current owner R0046.\n", "R0046"),
    ("unknown-receipt-refuses", receipt, '{"current_owner": "R0046"}', "R0046"),
])
historical_clauses = [
    "The fourth is an embedded separately accepted component, not a new R0042 issue.",
    "The host is R003F::BWP-LANE-CONTINUATION, not a new R0042.",
    "Old standalone R0042 draft is historical, not a current dependency or proposed new issue here.",
    "The old standalone R0042 draft is explicitly historical, not an issue dependency.",
]
for number, text in enumerate(historical_clauses, 1):
    cases.append((f"historical-container-{number}", outline, text, None))
cases.extend([
    ("positive-container-refuses", outline, "Current owner R0042.\n", "R0042"),
    ("vague-history-refuses", outline, "Historical current owner R0042.\n", "R0042"),
    ("same-line-positive-refuses", outline, historical_clauses[2] + " Current owner R0042.", "R0042"),
    ("historical-runtime-refuses", "skills/implementaudit/references/current-owner.md", historical_clauses[2], "R0042"),
    ("known-and-unknown-refuses", portal, "Published R003F; current owner R0046.\n", "R0046"),
])
cases.extend([
    ("captured-title-alias", receipt, json.dumps({"title": "R0025 (legacy R37) — Evolved-Lean"}, indent=2), None),
    ("captured-title-last-alias", receipt, json.dumps({"title": "R0037 (legacy R55) — original title"}, indent=2), None),
    ("mismatched-title-alias-refuses", receipt, json.dumps({"title": "R0025 (legacy R38) — wrong alias"}, indent=2), "R38"),
    ("extra-title-alias-refuses", receipt, json.dumps({"title": "R0025 (legacy R37) — current owner R28"}, indent=2), "R28"),
    ("other-field-alias-refuses", receipt, json.dumps({"observed_disposition": "R0025 (legacy R37)"}, indent=2), "R37"),
    ("other-document-alias-refuses", "docs/research/implementaudit/evolved-programme-v1/RLGWO_REGISTRY.json", json.dumps({"title": "R0025 (legacy R37)"}, indent=2), "R37"),
    ("runtime-title-alias-refuses", "skills/implementaudit/references/current-owner.json", json.dumps({"title": "R0025 (legacy R37)"}, indent=2), "R37"),
    ("unpaired-title-alias-refuses", receipt, json.dumps({"title": "Current owner R37"}, indent=2), "R37"),
])
failures = []
for name, relative, text, rejected_identity in cases:
    with tempfile.TemporaryDirectory(prefix="documentary-identity-") as temporary:
        root = Path(temporary)
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", temporary, "init", "-q"], check=True, capture_output=True)
        subprocess.run(["git", "-C", temporary, "add", relative], check=True, capture_output=True)
        result = subprocess.run([sys.executable, checker, "--scan-root", temporary], text=True, capture_output=True)
        if rejected_identity is None:
            passed = result.returncode == 0
        else:
            reason = "stale maintained Rockstar" if len(rejected_identity) == 3 else "unallocated Rockstar presented as current"
            passed = result.returncode == 1 and f"{reason} {rejected_identity}" in result.stderr
        print(f"documentary-identity: {'PASS' if passed else 'FAIL'} {name}")
        if not passed:
            failures.append(f"{name}: exit {result.returncode}; {result.stderr.strip()}")
if failures:
    raise SystemExit("\n".join(failures))
print(f"documentary-identity: {len(cases)}/{len(cases)} cases passed")
PY

"${py_cmd[@]}" "$checker"

printf 'durable-identity-contract.test: ok\n'
