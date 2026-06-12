#!/usr/bin/env bash
# docs-portal.test.sh - smoke and structural tests for the v2 docs portal.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  printf 'docs-portal.test: ok: %s\n' "$1"
}

fail_check() {
  fail=$((fail + 1))
  printf 'docs-portal.test: FAIL: %s\n' "$1" >&2
}

tmp="$(mktemp -d)"
host_claim_fixture=".host-claim-fixture.md"

cleanup() {
  rm -rf "$tmp"
  rm -f "$host_claim_fixture"
}
trap cleanup EXIT
out="$tmp/portal-out"
out2="$tmp/portal-out-2"
bad="$tmp/bad-portal"
bad_meta="$tmp/bad-meta"
bad_meta_extra="$tmp/bad-meta-extra"
bad_single="$tmp/bad-single-quoted"
bad_unquoted="$tmp/bad-unquoted"
bad_nav="$tmp/bad-nav"
bad_extra="$tmp/bad-extra-output"
bad_raw_command="$tmp/bad-raw-command"
bad_table_classes="$tmp/bad-table-classes"
bad_footer_proof="$tmp/bad-footer-proof"
bad_marker_taxonomy="$tmp/bad-marker-taxonomy"
bad_slash_boundary="$tmp/bad-slash-boundary"
bad_helper_path_boundary="$tmp/bad-helper-path-boundary"
bad_comparison_spotlight="$tmp/bad-comparison-spotlight"
bad_magnet_contract="$tmp/bad-magnet-contract"
bad_card_glass="$tmp/bad-card-glass"
bad_card_shimmer="$tmp/bad-card-shimmer"
bad_top_tabs="$tmp/bad-top-tabs"
bad_sidebar_tree="$tmp/bad-sidebar-tree"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'docs-portal.test: FAIL: python, python3, or py -3 is required\n' >&2
  exit 1
fi

if "${py_cmd[@]}" scripts/build-docs-portal.py --out "$out" >/dev/null; then
  ok "build-docs-portal.py exits 0"
else
  fail_check "build-docs-portal.py failed"
fi

if "${py_cmd[@]}" scripts/check-docs-portal.py "$out" >/dev/null; then
  ok "check-docs-portal.py passes generated output"
else
  fail_check "check-docs-portal.py failed generated output"
fi

if "${py_cmd[@]}" - "$out" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
site = json.loads(Path("docs/portal/site.json").read_text(encoding="utf-8"))
meta = json.loads((out / "docs-metadata.json").read_text(encoding="utf-8"))
ordered = []
for group in site["nav"]:
    ordered.extend(group["pages"])
assert site["nav"][0]["group"] == "Overview"
assert ordered[0] == "overview"
groups = {group["group"]: group["pages"] for group in site["nav"]}
assert list(groups) == ["Overview", "First run", "Audience", "Core model", "Evidence", "Closure", "Repository", "References"]
assert "References" in groups
assert "Reference" not in groups
assert "Maintainers" not in groups
assert groups["First run"] == ["quick-start", "installation", "possible-endings", "comparison"]
assert groups["Audience"] == ["for-new-users", "for-agents-and-operators", "for-auditors-and-maintainers"]
assert groups["Core model"] == ["runtime-model", "audit-gate-model", "invocation-shapes", "usage-examples", "planning-and-phases", "routing", "operating-method"]
assert groups["Evidence"] == ["state-and-artifacts", "repo-state-comparison", "error-handling", "evidence-boundaries", "optional-tooling", "child-agent-review-loops"]
assert groups["Closure"] == ["completion-semantics", "continuity-and-sidecars"]
assert groups["Repository"] == ["repo-layout", "package-contents", "audit-trail"]
assert groups["References"] == ["terminology", "reference-index"]
assert len(ordered) == meta["page_count"]
assert meta["portal_version"] == "v2-multipage"
assert meta["rough_draft_used"] is False
assert meta["worktree_state"] in {"clean", "dirty", "unknown"}
assert isinstance(meta["worktree_dirty"], bool)
assert meta["project_milestone"] == site["release"]["milestone"]
assert meta["plugin_manifest_version"] == site["release"]["manifest_version"]
assert meta["release_url"] == site["release"]["url"]
required = {
    "docs/portal/site.json",
    "docs/portal/pages/overview.html",
    "docs/portal/pages/quick-start.html",
    "docs/portal/pages/runtime-model.html",
    "docs/portal/pages/reference-index.html",
}
assert required.issubset(set(meta["source_files_used"]))
for page_id in ordered:
    page = site["pages"][page_id]
    rel = page["path"].strip("/")
    html = out / ("index.html" if not rel else f"{rel}/index.html")
    assert html.is_file(), html
    text = html.read_text(encoding="utf-8")
    assert 'class="page-context"' not in text
    assert 'class="page-proof-strip"' in text
    assert text.find('class="page-proof-strip"') > text.find("<footer>")
PY
then
  ok "metadata, site nav, and page shell agree"
else
  fail_check "metadata/site nav/page shell mismatch"
fi

if "${py_cmd[@]}" - "$out" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
needle = "\u00b7 Artifact:"
for path in root.rglob("*.html"):
    if needle in path.read_text(encoding="utf-8"):
        raise SystemExit(1)
PY
then
  ok "proof metadata split prevents Artifact orphan pattern"
else
  fail_check "proof metadata still has inline Artifact orphan pattern"
fi

if grep -R "docs/portal_old/onboarding.md" "$out" --include='*.html' >/dev/null 2>&1; then
  fail_check "generated v2 pages expose legacy portal source"
else
  ok "generated v2 pages do not expose legacy portal source"
fi

if "${py_cmd[@]}" - "$out" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
meta = json.loads((root / "docs-metadata.json").read_text(encoding="utf-8"))
if "docs/portal_old/onboarding.md" in meta["source_files_used"]:
    raise SystemExit("legacy portal source still drives v2 metadata")
html = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.html"))
required = [
    "P0 -&gt; P1 -&gt; P2",
    "OWNER DECISION",
    "ANDON_ESCALATE",
    "Polish and Harden",
    "IMPLEMENTAUDIT_CONTINUITY_SAVED",
    "New evidence:",
    "Changed approach:",
    "failed-criterion",
    "generated-artifact-mismatch",
    "applied-context.md",
    "repo-map.md",
    "tools.md",
    "context.md",
    "tdqyq-audit-object",
    "live runtime",
    "local generated-runtime",
    "package-bound",
    "visual/browser",
    "--onboard-tools",
    "bash scripts/write-release-checksums.sh --check dist/IMPLEMENTAUDIT.skill dist/CHECKSUMS.txt",
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit(f"missing parity concepts: {missing}")
required_patterns = [
    r"IMPLEMENTAUDIT\.skill/(?:<br>|\s+)SKILL\.md",
]
missing_patterns = [pattern for pattern in required_patterns if not re.search(pattern, html, re.IGNORECASE)]
if missing_patterns:
    raise SystemExit(f"missing parity concept patterns: {missing_patterns}")
if "IMPLEMENTAUDIT.skill/<br>skills/SKILL.md" in html:
    raise SystemExit("stale nested package tree returned")
PY
then
  ok "v2 parity concepts surpass legacy reference density"
else
  fail_check "v2 parity concepts missing or stale package tree returned"
fi

if grep -R "class=\"kdetails\"" "$out" --include='*.html' >/dev/null 2>&1; then
  fail_check "collapsed deep-reference drawer returned"
else
  ok "full runtime model is not a collapsed overview drawer"
fi

if "${py_cmd[@]}" scripts/build-docs-portal.py --out "$out2" >/dev/null; then
  ok "second portal build exits 0"
else
  fail_check "second portal build failed"
fi

if "${py_cmd[@]}" - "$out" "$out2" <<'PY'
import json
import sys
from pathlib import Path

first = Path(sys.argv[1])
second = Path(sys.argv[2])
files1 = sorted(p.relative_to(first).as_posix() for p in first.rglob("*") if p.is_file())
files2 = sorted(p.relative_to(second).as_posix() for p in second.rglob("*") if p.is_file())
assert files1 == files2
for rel in files1:
    p1 = first / rel
    p2 = second / rel
    if rel == "docs-metadata.json":
        m1 = json.loads(p1.read_text(encoding="utf-8"))
        m2 = json.loads(p2.read_text(encoding="utf-8"))
        m1["generated_at"] = "<normalized>"
        m2["generated_at"] = "<normalized>"
        assert m1 == m2
    else:
        assert p1.read_bytes() == p2.read_bytes(), rel
PY
then
  ok "generated output is reproducible after timestamp normalization"
else
  fail_check "generated output is not reproducible"
fi

cp -R "$out" "$bad"
"${py_cmd[@]}" - "$bad/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace("start-here/quick-start/", "missing/page/", 1), encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted a broken local link"
else
  ok "check-docs-portal.py rejects broken local links"
fi

cp -R "$out" "$bad_single"
"${py_cmd[@]}" - "$bad_single/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace('href="start-here/quick-start/"', "href='missing/single-quoted/'", 1)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_single" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted a single-quoted broken local link"
else
  ok "check-docs-portal.py rejects single-quoted broken local links"
fi

cp -R "$out" "$bad_unquoted"
"${py_cmd[@]}" - "$bad_unquoted/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace('href="start-here/quick-start/"', "href=missing/unquoted/", 1)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_unquoted" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted an unquoted broken local link"
else
  ok "check-docs-portal.py rejects unquoted broken local links"
fi

cp -R "$out" "$bad_raw_command"
"${py_cmd[@]}" - "$bad_raw_command/start-here/installation/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("</article>", "<pre><code>$ /implementaudit raw prompt should fail</code></pre></article>", 1)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_raw_command" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted a raw prompted runnable command pre"
else
  ok "check-docs-portal.py rejects raw prompted runnable command pre blocks"
fi

cp -R "$out" "$bad_table_classes"
"${py_cmd[@]}" - \
  "$bad_table_classes/reference/planning-and-phases/index.html" \
  "$bad_table_classes/reference/runtime-model/index.html" \
  "$bad_table_classes/reference/continuity-and-sidecars/index.html" <<'PY'
import sys
from pathlib import Path

replacements = {
    ' class="stage-table"': "",
    ' class="stage-num"': "",
    ' class="layer-table"': "",
    ' class="layer-num"': "",
    ' class="priority-table"': "",
    ' class="priority-num"': "",
}
for arg in sys.argv[1:]:
    path = Path(arg)
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_table_classes" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted cramped-header table markup without required classes"
else
  ok "check-docs-portal.py rejects cramped-header table markup without required classes"
fi

cp -R "$out" "$bad_footer_proof"
"${py_cmd[@]}" - "$bad_footer_proof/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace(
    '<dd class="release-proof-links">',
    '<dd class="release-proof-links"><span>Boundary</span> ',
    1,
)
text = text.replace(">Source</a> - <a", ">Changelog</a> - <a", 1)
text = text.replace(">Changelog</a></dd>", ">Source</a></dd>", 1)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_footer_proof" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted footer proof Boundary cell or release-link order drift"
else
  ok "check-docs-portal.py rejects footer proof Boundary cell and release-link order drift"
fi

cp -R "$out" "$bad_marker_taxonomy"
"${py_cmd[@]}" - "$bad_marker_taxonomy" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    text = text.replace("AUDIT_WARNING", "AUDIT_NOTICE")
    text = text.replace("IMPLEMENTAUDIT_PAUSE", "IMPLEMENTAUDIT_STOP")
    path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_marker_taxonomy" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted marker taxonomy without AUDIT_WARNING and IMPLEMENTAUDIT_PAUSE"
else
  ok "check-docs-portal.py rejects marker taxonomy missing AUDIT_WARNING and IMPLEMENTAUDIT_PAUSE"
fi

cp -R "$out" "$bad_slash_boundary"
"${py_cmd[@]}" - "$bad_slash_boundary" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "Slash commands fire only when the user submits them.",
        "Slash commands may be printed as examples.",
    )
    path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_slash_boundary" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing slash-command handoff boundary text"
else
  ok "check-docs-portal.py rejects missing slash-command handoff boundary text"
fi

cp -R "$out" "$bad_helper_path_boundary"
"${py_cmd[@]}" - "$bad_helper_path_boundary" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    text = text.replace("${IMPLEMENTAUDIT_SKILL_DIR:-skills}/scripts/", "skills/scripts/")
    text = text.replace("IMPLEMENTAUDIT_SKILL_DIR", "SKILL_DIR")
    path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_helper_path_boundary" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing IMPLEMENTAUDIT_SKILL_DIR helper path boundary"
else
  ok "check-docs-portal.py rejects missing IMPLEMENTAUDIT_SKILL_DIR helper path boundary"
fi

cp -R "$out" "$bad_comparison_spotlight"
"${py_cmd[@]}" - \
  "$bad_comparison_spotlight/start-here/comparison/index.html" \
  "$bad_comparison_spotlight/assets/draft-v2.css" \
  "$bad_comparison_spotlight/assets/draft-v2.js" <<'PY'
import sys
from pathlib import Path

html_path, css_path, js_path = [Path(arg) for arg in sys.argv[1:]]
html = html_path.read_text(encoding="utf-8")
html = html.replace("comparison-winner card-spotlight", "comparison-winner", 1)
html_path.write_text(html, encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
for token in ("--mouse-x", "--mouse-y", "--spotlight-color", "circle 25px", "rgba(251,191,36,0.08)", "@keyframes shiny-title"):
    css = css.replace(token, token.replace("-", "_"))
css_path.write_text(css, encoding="utf-8")
js = js_path.read_text(encoding="utf-8")
js = js.replace(".card-spotlight", ".comparison-winner", 1)
js_path.write_text(js, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_comparison_spotlight" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing comparison spotlight/shiny card contract"
else
  ok "check-docs-portal.py rejects missing comparison spotlight/shiny card contract"
fi

cp -R "$out" "$bad_magnet_contract"
"${py_cmd[@]}" - "$bad_magnet_contract" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    text = text.replace(" magnet-link", "")
    path.write_text(text, encoding="utf-8")
css_path = root / "assets" / "draft-v2.css"
css = css_path.read_text(encoding="utf-8")
for token in (".magnet-link", "--magnet-x", "--magnet-y", ".magnet-link.is-magnet-active", "(pointer: coarse)"):
    css = css.replace(token, token.replace("-", "_"))
css_path.write_text(css, encoding="utf-8")
js_path = root / "assets" / "draft-v2.js"
js = js_path.read_text(encoding="utf-8")
for token in (".magnet-link", "--magnet-x", "--magnet-y", "is-magnet-active", "matchMedia('(pointer: coarse)')"):
    js = js.replace(token, token.replace("-", "_"))
js_path.write_text(js, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_magnet_contract" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing magnetic-link contract"
else
  ok "check-docs-portal.py rejects missing magnetic-link contract"
fi

cp -R "$out" "$bad_card_glass"
"${py_cmd[@]}" - "$bad_card_glass/assets/draft-v2.css" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
css = path.read_text(encoding="utf-8")
for token in (
    ".comparison-cards section:not(.comparison-winner)",
    ".surface-strip div",
    ".compare-card",
    ".proto-card",
    ".hero-card",
    ".callout",
    "background: rgba(255,255,255,0.82)",
    "backdrop-filter: blur(6px)",
    "transform: scale(1.012)",
    "transform: scale(0.992)",
    "box-shadow: 12px 17px 51px rgba(15,23,42,0.10)",
    "border-left: 4px solid var(--cyan)",
    "border-left: 4px solid var(--blue)",
    "border-left: 4px solid var(--amber)",
    ".compare-good:hover",
    "background: var(--emerald-soft)",
    ".example-terminal-grid",
):
    css = css.replace(token, token.replace("-", "_"))
path.write_text(css, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_card_glass" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing reusable glass card treatment"
else
  ok "check-docs-portal.py rejects missing reusable glass card treatment"
fi

cp -R "$out" "$bad_card_shimmer"
"${py_cmd[@]}" - "$bad_card_shimmer/assets/draft-v2.css" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
css = path.read_text(encoding="utf-8")
css += "\n.result-grid div::before { content: ''; }\n@keyframes card-label-shine { from { opacity: 0; } to { opacity: 1; } }\n"
path.write_text(css, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_card_shimmer" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted ordinary card shimmer treatment"
else
  ok "check-docs-portal.py rejects ordinary card shimmer treatment"
fi

cp -R "$out" "$bad_top_tabs"
"${py_cmd[@]}" - "$bad_top_tabs" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    text = text.replace(' class="top-tabs"', ' class="top-links"', 1)
    text = text.replace('class="top-tab-indicator" aria-hidden="true"', 'class="top-tab-marker" aria-hidden="true"', 1)
    text = text.replace(' style="--active-index:', ' style="--current-index:', 1)
    path.write_text(text, encoding="utf-8")
css_path = root / "assets" / "draft-v2.css"
css = css_path.read_text(encoding="utf-8")
for token in (".top-tabs", "--active-index", "--tab-count", ".top-tab-indicator", ".top-tab[aria-current=\"location\"]"):
    css = css.replace(token, token.replace("-", "_"))
css_path.write_text(css, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_top_tabs" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing top navigation tabs treatment"
else
  ok "check-docs-portal.py rejects missing top navigation tabs treatment"
fi

cp -R "$out" "$bad_sidebar_tree"
"${py_cmd[@]}" - "$bad_sidebar_tree" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    for token in (
        'class="nav-docs-head"',
        '<details class="nav-group" open>',
        '<summary class="nav-title">',
        'class="nav-caret" aria-hidden="true"',
    ):
        text = text.replace(token, token.replace("-", "_"))
    text = text.replace('<span>Docs</span>', '<span>explorer</span>')
    path.write_text(text, encoding="utf-8")
css_path = root / "assets" / "draft-v2.css"
css = css_path.read_text(encoding="utf-8")
for token in (".nav-docs-head", ".nav-caret", ".nav-group[open] .nav-caret"):
    css = css.replace(token, token.replace("-", "_"))
css_path.write_text(css, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_sidebar_tree" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted missing file-tree sidebar treatment"
else
  ok "check-docs-portal.py rejects missing file-tree sidebar treatment"
fi

cp -R "$out" "$bad_nav"
"${py_cmd[@]}" - "$bad_nav/reference/audit-gate-model/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace('aria-current="location"', 'aria-current="page"', 1)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_nav" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted bucket navigation marked as current page"
else
  ok "check-docs-portal.py rejects incorrect top-nav current state"
fi

cp -R "$out" "$bad_extra"
printf 'stale\n' > "$bad_extra/assets/stale.txt"
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_extra" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted stale generated output files"
else
  ok "check-docs-portal.py rejects stale generated output files"
fi

cp -R "$out" "$bad_meta"
"${py_cmd[@]}" - "$bad_meta/docs-metadata.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
meta = json.loads(path.read_text(encoding="utf-8"))
source = "README.md"
meta["source_sha256s"][source] = "0" * 64
path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_meta" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted stale source metadata"
else
  ok "check-docs-portal.py rejects stale source metadata"
fi

cp -R "$out" "$bad_meta_extra"
"${py_cmd[@]}" - "$bad_meta_extra/docs-metadata.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
meta = json.loads(path.read_text(encoding="utf-8"))
meta["source_files_used"].append("docs/portal/pages/stale-extra.html")
meta["source_sha256s"]["docs/portal/pages/stale-extra.html"] = "0" * 64
path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_meta_extra" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted extra stale source metadata"
else
  ok "check-docs-portal.py rejects extra stale source metadata"
fi

if "${py_cmd[@]}" scripts/build-docs-portal.py --out . >/dev/null 2>&1; then
  fail_check "build-docs-portal.py accepted repo root as output"
else
  ok "build-docs-portal.py refuses unsafe output directories"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

Path(sys.argv[1]).write_text("Local installs do not " + "auto-" + "update.\n", encoding="utf-8")
PY
if bash scripts/check-host-claims.sh >/dev/null 2>&1; then
  ok "check-host-claims.sh allows negative local install update context"
else
  fail_check "check-host-claims.sh rejected negative local install update context"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

Path(sys.argv[1]).write_text("This package " + "auto-" + "updates from a host.\n", encoding="utf-8")
PY
if bash scripts/check-host-claims.sh >/dev/null 2>&1; then
  fail_check "check-host-claims.sh accepted a positive host update claim"
else
  ok "check-host-claims.sh rejects positive host update claims"
fi
rm -f "$host_claim_fixture"

if bash scripts/verify-docs-portal.sh >/dev/null; then
  ok "verify-docs-portal.sh passes generated output"
else
  fail_check "verify-docs-portal.sh failed"
fi

total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'docs-portal.test: FAIL - %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'docs-portal.test: ok (%d/%d)\n' "$pass" "$total"
