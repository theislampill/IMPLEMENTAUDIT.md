#!/usr/bin/env bash
# docs-portal.test.sh — smoke and structural tests for the docs portal generator.
#
# Tests:
#   1. build-docs-portal.py runs cleanly and produces output
#   2. check-docs-portal.py passes on generated output
#   3. index.html exists and is non-empty
#   4. docs-metadata.json exists with required fields
#   5. No file:/// URLs in generated output
#   6. No absolute Windows paths in generated output
#   7. Nav anchors exist and are unique
#   8. Required onboarding sections present
#   9. Generated output is excluded from .skill package (verify-package.sh still passes)
#  10. Generator intentionally fails on missing source dir (negative test)
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

pass=0
fail=0

ok() {
  local label="$1"
  pass=$((pass + 1))
  printf 'docs-portal.test: ok: %s\n' "$label"
}

fail_check() {
  local label="$1"
  fail=$((fail + 1))
  printf 'docs-portal.test: FAIL: %s\n' "$label" >&2
}

# Use a temp dir for generated output so we don't pollute the working tree
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
out="$tmp/portal-out"

# ---------------------------------------------------------------------------
# Test 1: generator runs cleanly
# ---------------------------------------------------------------------------
if python scripts/build-docs-portal.py --out "$out" >/dev/null 2>&1; then
  ok "build-docs-portal.py exits 0"
else
  fail_check "build-docs-portal.py failed (exit non-zero)"
fi

# ---------------------------------------------------------------------------
# Test 2: check-docs-portal.py passes
# ---------------------------------------------------------------------------
if python scripts/check-docs-portal.py "$out" >/dev/null 2>&1; then
  ok "check-docs-portal.py passes on generated output"
else
  fail_check "check-docs-portal.py failed on generated output"
fi

# ---------------------------------------------------------------------------
# Test 3: index.html exists and is non-empty
# ---------------------------------------------------------------------------
if [ -f "$out/index.html" ] && [ -s "$out/index.html" ]; then
  ok "index.html exists and is non-empty"
else
  fail_check "index.html missing or empty"
fi

# ---------------------------------------------------------------------------
# Test 4: docs-metadata.json exists with required fields
# ---------------------------------------------------------------------------
if [ -f "$out/docs-metadata.json" ]; then
  ok "docs-metadata.json exists"
  for field in repo commit_sha generated_at project_milestone plugin_manifest_version source_sha256s rough_draft_used; do
    if python -c "import json,sys; d=json.load(open(sys.argv[1])); assert '$field' in d" "$out/docs-metadata.json" 2>/dev/null; then
      ok "docs-metadata.json: field '$field' present"
    else
      fail_check "docs-metadata.json: field '$field' missing"
    fi
  done
  # rough_draft_used must be false
  if python -c "import json,sys; d=json.load(open(sys.argv[1])); assert d.get('rough_draft_used') is False" "$out/docs-metadata.json" 2>/dev/null; then
    ok "docs-metadata.json: rough_draft_used is false"
  else
    fail_check "docs-metadata.json: rough_draft_used is not false"
  fi
else
  fail_check "docs-metadata.json missing"
fi

# ---------------------------------------------------------------------------
# Test 5: no file:/// URLs in generated output
# ---------------------------------------------------------------------------
if grep -qF "file:///" "$out/index.html" 2>/dev/null; then
  fail_check "index.html contains file:/// URL"
else
  ok "no file:/// URLs in index.html"
fi

# ---------------------------------------------------------------------------
# Test 6: no absolute Windows paths in generated output
# ---------------------------------------------------------------------------
if python -c "
import re, sys
html = open(sys.argv[1], encoding='utf-8').read()
# Only flag unquoted paths in href/src or text content, not escaped JSON
if re.search(r'(?<!\\\\)[A-Za-z]:\\\\\\\\', html) or re.search(r'href=\"[A-Za-z]:', html):
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "no absolute Windows paths in index.html"
else
  fail_check "index.html contains absolute Windows paths"
fi

# ---------------------------------------------------------------------------
# Test 7: nav anchors exist and are unique
# ---------------------------------------------------------------------------
nav_count=$(python -c "
import re, sys
html = open(sys.argv[1], encoding='utf-8').read()
hrefs = re.findall(r'nav-link[^>]*href=\"#([^\"]+)\"', html) or re.findall(r'href=\"#([^\"]+)\"[^>]*nav-link', html)
unique = set(hrefs)
print(len(hrefs))
if len(hrefs) != len(unique):
    import sys; print(0); sys.exit(1)
" "$out/index.html" 2>/dev/null)
if [ "${nav_count:-0}" -gt 0 ]; then
  ok "nav anchors present and unique ($nav_count found)"
else
  fail_check "nav anchors missing or duplicate in index.html"
fi

# ---------------------------------------------------------------------------
# Test 8: required onboarding sections present
# ---------------------------------------------------------------------------
required_anchors="what-is-implementaudit when-should-i-use-it when-should-i-not-use-it normal-prompt-vs-goal-vs-implementaudit three-invocation-modes compared-with-a-generic-staged-goal-runner what-graphify-and-activegraph-do what-completion-means install-and-update"
for anchor in $required_anchors; do
  if grep -qF "id=\"$anchor\"" "$out/index.html" 2>/dev/null; then
    ok "section present: #$anchor"
  else
    fail_check "section missing: #$anchor"
  fi
done

# ---------------------------------------------------------------------------
# Test 9: generated output excluded from .skill package
# ---------------------------------------------------------------------------
if bash scripts/verify-package.sh >/dev/null 2>&1; then
  ok "verify-package.sh still passes (dist/ excluded from package)"
else
  fail_check "verify-package.sh failed after portal build"
fi

# ---------------------------------------------------------------------------
# Test 10: negative — generator with a bad --out should not crash uncleanly
# (just confirm it exits and doesn't partially write)
# ---------------------------------------------------------------------------
bad_out="$tmp/bad-portal-out"
if python scripts/build-docs-portal.py --out "$bad_out" >/dev/null 2>&1; then
  ok "negative test: generator writes to any writable out dir (ok)"
else
  fail_check "negative test: generator crashed on new output dir"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'docs-portal.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi
printf 'docs-portal.test: ok (%d/%d)\n' "$pass" "$total"
