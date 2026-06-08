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
#   7. Nav anchors exist and are unique (authoritative count from check-docs-portal.py)
#   8. Required onboarding sections present (24 academic-model anchors)
#   9. Generated output is excluded from .skill package (verify-package.sh still passes)
#  10. Generator writes to any writable out dir (negative test)
#  11. h1 page title present in index.html
#  12. Hero zone present
#  13. Process flow present with all six steps
#  14. Grouped sidebar labels present (Start, Concepts, Method, Reference)
#  15. Mobile TOC present
#  16. Audience cards present (card-grid and audience-card)
#  17. Four invocation shapes present in content
#  18. "governed casual-build intake" phrase present
#  19. No stale "three invocation modes" claim
#  20. No stale "release pending" text
#  21. No empty inline code elements
#  22. No forbidden claims (marketplace, provenance claim, certified)
#  23. Skip link present (accessibility)
#  24. docs-metadata.json: rough_draft_used is false
#  25. Sidebar nav-section anchors follow document section order
#  26. docs-metadata.json: rough_draft_used is explicitly false (boolean)
#  27. Academic: bottleneck framing present
#  28. Academic: tdqyq-audit-object and ydqyq-audit-action identifiers present
#  29. Academic: AUDIT_COMPLETE and IMPLEMENTAUDIT_RUN_COMPLETE markers present
#  30. Academic: DMADV and DMAIC routing methodology terms present
#  31. Academic: G5 STRENGTHENED status present
#  32. Academic: no stale "--version 0.2.4" install command
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
if re.search(r'(?<!\\\\)[A-Za-z]:\\\\\\\\', html) or re.search(r'href=\"[A-Za-z]:', html):
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "no absolute Windows paths in index.html"
else
  fail_check "index.html contains absolute Windows paths"
fi

# ---------------------------------------------------------------------------
# Test 7: nav anchors exist and are unique
# SC-2 fix: use authoritative nav-section regex matching the generator output
# (generator produces class="nav-section"><a href="#id">, not class="nav-link")
# ---------------------------------------------------------------------------
nav_count=$(python -c "
import re, sys
html = open(sys.argv[1], encoding='utf-8').read()
hrefs = re.findall(r'class=\"nav-section\"><a href=\"#([^\"]+)\"', html)
unique = set(hrefs)
if len(hrefs) != len(unique):
    sys.stderr.write('duplicate nav anchors: %s\n' % str(hrefs))
    sys.exit(1)
print(len(hrefs))
" "$out/index.html" 2>/dev/null)
if [ "${nav_count:-0}" -gt 0 ]; then
  ok "nav anchors present and unique ($nav_count found)"
else
  fail_check "nav anchors missing or duplicate in index.html (nav-section regex)"
fi

# ---------------------------------------------------------------------------
# Test 8: required onboarding sections present (24 academic-model anchors)
# ---------------------------------------------------------------------------
required_anchors="overview quick-start install for-new-users for-agents-and-operators for-auditors-and-maintainers mental-model invocation-model audit-gate-model what-audit-complete-means state-and-artifact-model continuity-and-sidecars operating-method routing comparison default-behavior usage-examples terminology repo-layout optional-tooling safety-and-boundaries what-it-does-not-do evidence-and-audit-trail audit-status"
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
# Test 10: negative — generator with a new dir should not crash
# ---------------------------------------------------------------------------
bad_out="$tmp/bad-portal-out"
if python scripts/build-docs-portal.py --out "$bad_out" >/dev/null 2>&1; then
  ok "negative test: generator writes to any writable out dir (ok)"
else
  fail_check "negative test: generator crashed on new output dir"
fi

# ---------------------------------------------------------------------------
# Test 11: h1 page title present
# ---------------------------------------------------------------------------
if grep -qE "<h1[^>]*>" "$out/index.html" 2>/dev/null; then
  ok "h1 page title present"
else
  fail_check "h1 page title missing"
fi

# ---------------------------------------------------------------------------
# Test 12: hero zone present
# ---------------------------------------------------------------------------
if grep -qF "hero-zone" "$out/index.html" 2>/dev/null; then
  ok "hero-zone element present"
else
  fail_check "hero-zone element missing"
fi

# ---------------------------------------------------------------------------
# Test 13: process flow present with all six steps
# ---------------------------------------------------------------------------
process_ok=1
for step in "Input" "Gemba" "Smoke A" "Patch" "Smoke B" "Final Audit"; do
  if ! grep -qF "$step" "$out/index.html" 2>/dev/null; then
    fail_check "process flow step missing: $step"
    process_ok=0
  fi
done
if [ "$process_ok" -eq 1 ]; then
  ok "process flow present with all six steps (Input → Gemba → Smoke A → Patch → Smoke B → Final Audit)"
fi

# ---------------------------------------------------------------------------
# Test 14: grouped sidebar labels present (Start, Concepts, Method, Reference)
# ---------------------------------------------------------------------------
sidebar_ok=1
for group in "Start" "Concepts" "Method" "Reference"; do
  if ! grep -qF "class=\"nav-group-label\">$group" "$out/index.html" 2>/dev/null; then
    fail_check "sidebar group label missing: $group"
    sidebar_ok=0
  fi
done
if [ "$sidebar_ok" -eq 1 ]; then
  ok "grouped sidebar labels present (Start, Concepts, Method, Reference)"
fi

# ---------------------------------------------------------------------------
# Test 15: mobile TOC present
# ---------------------------------------------------------------------------
if grep -qF "mobile-toc" "$out/index.html" 2>/dev/null; then
  ok "mobile-toc element present"
else
  fail_check "mobile-toc element missing"
fi

# ---------------------------------------------------------------------------
# Test 16: audience cards present
# ---------------------------------------------------------------------------
cards_ok=1
if ! grep -qF "card-grid" "$out/index.html" 2>/dev/null; then
  fail_check "card-grid element missing"
  cards_ok=0
fi
if ! grep -qF "audience-card" "$out/index.html" 2>/dev/null; then
  fail_check "audience-card element(s) missing"
  cards_ok=0
fi
if [ "$cards_ok" -eq 1 ]; then
  ok "audience cards present (card-grid and audience-card elements)"
fi

# ---------------------------------------------------------------------------
# Test 17: four invocation shapes present (case-insensitive)
# ---------------------------------------------------------------------------
modes_ok=1
for phrase in "direct governance" "embedded governance" "goal synthesis" "governed casual-build intake"; do
  if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
phrase = sys.argv[2].lower()
if phrase not in html:
    sys.exit(1)
" "$out/index.html" "$phrase" 2>/dev/null; then
    ok "invocation shape phrase present: '$phrase'"
  else
    fail_check "invocation shape phrase missing: '$phrase'"
    modes_ok=0
  fi
done

# ---------------------------------------------------------------------------
# Test 18: "governed casual-build intake" phrase present (explicit)
# ---------------------------------------------------------------------------
if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if 'governed casual-build intake' not in html:
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "'governed casual-build intake' phrase present in portal"
else
  fail_check "'governed casual-build intake' phrase missing from portal"
fi

# ---------------------------------------------------------------------------
# Test 19: no stale "three invocation modes" claim
# ---------------------------------------------------------------------------
if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if 'three invocation modes' in html:
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "no stale 'three invocation modes' claim"
else
  fail_check "stale 'three invocation modes' claim found (v0.2.8.0 has four invocation shapes)"
fi

# ---------------------------------------------------------------------------
# Test 20: no stale "release pending" text
# ---------------------------------------------------------------------------
if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if 'release pending' in html:
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "no stale 'release pending' text"
else
  fail_check "stale 'release pending' text found (release is live)"
fi

# ---------------------------------------------------------------------------
# Test 21: no empty inline code elements
# ---------------------------------------------------------------------------
if python -c "
import re, sys
html = open(sys.argv[1], encoding='utf-8').read()
empty = re.findall(r'<code>\s*</code>', html)
if empty:
    sys.stderr.write('empty code elements: %d\n' % len(empty))
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "no empty inline code elements"
else
  fail_check "empty <code></code> elements found in index.html"
fi

# ---------------------------------------------------------------------------
# Test 22: no forbidden claims (marketplace, provenance claim, certified)
# ---------------------------------------------------------------------------
# Note: "marketplace" appears in denial context ("no marketplace publication occurred") —
# only check for affirmative overclaims, not the bare word.
claims_ok=1
for claim in "published to the marketplace" "provenance claim" "certified" "six sigma" "dpmo"; do
  if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if sys.argv[2].lower() in html:
    sys.exit(1)
" "$out/index.html" "$claim" 2>/dev/null; then
    ok "forbidden claim absent: '$claim'"
  else
    fail_check "forbidden claim found: '$claim'"
    claims_ok=0
  fi
done

# ---------------------------------------------------------------------------
# Test 23: skip link present (accessibility)
# ---------------------------------------------------------------------------
if grep -qF 'class="skip-link"' "$out/index.html" 2>/dev/null; then
  ok "skip link present (accessibility)"
else
  fail_check "skip link missing (accessibility requirement)"
fi

# ---------------------------------------------------------------------------
# Test 24: docs-metadata.json rough_draft_used is false
# ---------------------------------------------------------------------------
if python -c "import json,sys; d=json.load(open(sys.argv[1])); assert d.get('rough_draft_used') is False" "$out/docs-metadata.json" 2>/dev/null; then
  ok "docs-metadata.json: rough_draft_used is false"
else
  fail_check "docs-metadata.json: rough_draft_used is not false"
fi

# ---------------------------------------------------------------------------
# Test 25: nav-section anchor order matches document section order
# ---------------------------------------------------------------------------
if python -c "
import re, sys
html = open(sys.argv[1], encoding='utf-8').read()
nav_hrefs = re.findall(r'class=\"nav-section\"><a href=\"#([^\"]+)\"', html)
section_ids = re.findall(r'<section id=\"([^\"]+)\"', html)
nav_set = set(nav_hrefs)
ordered = [s for s in section_ids if s in nav_set]
if ordered != nav_hrefs:
    sys.stderr.write('nav order: %s\n' % nav_hrefs)
    sys.stderr.write('doc order: %s\n' % ordered)
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "nav-section anchor order matches document section order"
else
  fail_check "nav-section anchor order does not match document section order"
fi

# ---------------------------------------------------------------------------
# Test 26: docs-metadata.json rough_draft_used is explicitly boolean false
# (not string 'false', not null, not absent)
# ---------------------------------------------------------------------------
if python -c "
import json, sys
d = json.load(open(sys.argv[1]))
val = d.get('rough_draft_used')
assert val is False, 'got: %r' % val
" "$out/docs-metadata.json" 2>/dev/null; then
  ok "docs-metadata.json: rough_draft_used is boolean false (not string/null)"
else
  fail_check "docs-metadata.json: rough_draft_used is not boolean false"
fi

# ---------------------------------------------------------------------------
# Test 27: Academic: bottleneck framing present
# (must contain "review discipline" or "faster than")
# ---------------------------------------------------------------------------
if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if 'review discipline' not in html and 'faster than' not in html:
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "academic: bottleneck framing present"
else
  fail_check "academic: bottleneck framing missing ('review discipline' or 'faster than')"
fi

# ---------------------------------------------------------------------------
# Test 28: Academic: tdqyq-audit-object and ydqyq-audit-action identifiers
# ---------------------------------------------------------------------------
ids_ok=1
for identifier in "tdqyq-audit-object" "ydqyq-audit-action"; do
  if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if sys.argv[2].lower() not in html:
    sys.exit(1)
" "$out/index.html" "$identifier" 2>/dev/null; then
    ok "academic: identifier present: '$identifier'"
  else
    fail_check "academic: identifier missing: '$identifier'"
    ids_ok=0
  fi
done

# ---------------------------------------------------------------------------
# Test 29: Academic: AUDIT_COMPLETE and IMPLEMENTAUDIT_RUN_COMPLETE markers
# ---------------------------------------------------------------------------
markers_ok=1
for marker in "AUDIT_COMPLETE" "IMPLEMENTAUDIT_RUN_COMPLETE"; do
  if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if sys.argv[2].lower() not in html:
    sys.exit(1)
" "$out/index.html" "$marker" 2>/dev/null; then
    ok "academic: marker present: '$marker'"
  else
    fail_check "academic: marker missing: '$marker'"
    markers_ok=0
  fi
done

# ---------------------------------------------------------------------------
# Test 30: Academic: DMADV and DMAIC routing methodology terms
# ---------------------------------------------------------------------------
routing_ok=1
for term in "DMADV" "DMAIC"; do
  if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if sys.argv[2].lower() not in html:
    sys.exit(1)
" "$out/index.html" "$term" 2>/dev/null; then
    ok "academic: routing methodology term present: '$term'"
  else
    fail_check "academic: routing methodology term missing: '$term'"
    routing_ok=0
  fi
done

# ---------------------------------------------------------------------------
# Test 31: Academic: G5 STRENGTHENED status
# ---------------------------------------------------------------------------
if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read().lower()
if 'strengthened' not in html:
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "academic: G5 STRENGTHENED status present"
else
  fail_check "academic: G5 STRENGTHENED status missing from portal"
fi

# ---------------------------------------------------------------------------
# Test 32: Academic: no stale "--version 0.2.4" install command
# ---------------------------------------------------------------------------
if python -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read()
if '--version 0.2.4' in html:
    sys.exit(1)
" "$out/index.html" 2>/dev/null; then
  ok "academic: no stale '--version 0.2.4' install command"
else
  fail_check "academic: stale '--version 0.2.4' install command found"
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
