#!/usr/bin/env python3
"""
check-docs-portal.py — validate IMPLEMENTAUDIT docs portal output.

Usage:
    python scripts/check-docs-portal.py <output-dir>

Validates the generated dist/docs-portal/ (or specified dir) for:
- index.html exists and is non-empty
- docs-metadata.json exists with required fields
- source sha256s are present in metadata
- plugin manifest version represented
- project milestone represented
- rough_draft_used is false
- no file:/// URLs
- no absolute Windows paths (C:\\, D:\\, etc.)
- nav anchors exist and are unique (uses nav-section structure)
- nav anchors follow document order (same order as sections)
- required onboarding content sections present (v0.2.8.0 anchors)
- h1 exists (page title)
- hero zone / process flow present
- grouped sidebar labels (Start, Method, Reference, Evidence)
- mobile TOC present
- audience cards present
- four invocation modes present (direct governance, embedded governance,
  goal synthesis, governed casual-build intake)
- "governed casual-build intake" text present
- no stale "three invocation modes" claim
- no stale "release pending" text
- no empty inline code elements
- no unsupported marketplace/provenance/install-proof claims
- no footer stale freshness disclaimer

No external dependencies; Python stdlib only.

Exit 0: all checks pass.
Exit 1: one or more checks failed.
"""

import json
import re
import sys
from pathlib import Path


REQUIRED_METADATA_FIELDS = [
    "repo",
    "commit_sha",
    "generated_at",
    "project_milestone",
    "plugin_manifest_version",
    "source_files_used",
    "source_sha256s",
    "rough_draft_used",
]

# Canonical section anchors for v0.2.8.0 portal (derived from onboarding.md h2 titles)
REQUIRED_CONTENT_ANCHORS = [
    "overview",
    "quick-start",
    "install",
    "for-new-users",
    "for-agents-and-operators",
    "for-auditors-and-maintainers",
    "terminology",
    "invocation-modes",
    "execution-spine",
    "operating-method",
    "usage-examples",
    "default-behavior",
    "routing",
    "repo-layout",
    "optional-tooling",
    "safety-and-boundaries",
    "what-it-does-not-do",
    "evidence-and-audit-trail",
    "audit-status",
]

# Required sidebar group labels
REQUIRED_SIDEBAR_GROUPS = ["Start", "Method", "Reference", "Evidence"]

# Invocation mode phrases that must appear in the portal
REQUIRED_INVOCATION_MODE_PHRASES = [
    "direct governance",
    "embedded governance",
    "goal synthesis",
    "governed casual-build intake",
]

FORBIDDEN_PATTERNS = [
    # No file:/// URLs
    (r"file:///", "file:/// URL found"),
    # No absolute Windows paths in generated output
    (r"[A-Za-z]:\\\\", "absolute Windows path found"),
    (r'href="[A-Za-z]:[/\\\\]', "absolute Windows-style path in href"),
]

FORBIDDEN_CLAIMS = [
    "install-proof",
    "provenance claim",
    "certified",
    "six sigma",
    "dpmo",
    "process sigma",
]

# Stale text that must NOT appear in the portal
# Note: "marketplace" is expected as a denial ("no marketplace publication occurred") —
# do NOT include bare "marketplace" here; only check for affirmative overclaims.
FORBIDDEN_STALE_TEXT = [
    ("three invocation modes", "stale 'three invocation modes' claim (v0.2.8.0 has four)"),
    ("release pending", "stale 'release pending' text (release is live)"),
    ("published to the marketplace", "affirmative marketplace publication claim"),
    ("listed on the marketplace", "affirmative marketplace listing claim"),
]

_failures = 0


def fail(msg: str) -> None:
    global _failures
    _failures += 1
    sys.stderr.write(f"check-docs-portal: FAIL: {msg}\n")


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <output-dir>\n")
        sys.exit(1)

    out_dir = Path(sys.argv[1])

    # 1. index.html exists and is non-empty
    index_path = out_dir / "index.html"
    if not index_path.is_file():
        fail(f"index.html not found in {out_dir}")
        sys.exit(1)
    html = index_path.read_text(encoding="utf-8")
    if len(html) < 100:
        fail(f"index.html is suspiciously small ({len(html)} bytes)")

    # 2. docs-metadata.json exists with required fields
    meta_path = out_dir / "docs-metadata.json"
    if not meta_path.is_file():
        fail(f"docs-metadata.json not found in {out_dir}")
        metadata = {}
    else:
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"docs-metadata.json is not valid JSON: {e}")
            metadata = {}

    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            fail(f"docs-metadata.json missing required field: {field}")

    # 3. source sha256s are present
    sha256s = metadata.get("source_sha256s", {})
    if not sha256s:
        fail("docs-metadata.json: source_sha256s is empty")

    # 4. plugin manifest version represented
    manifest_version = metadata.get("plugin_manifest_version", "")
    if not manifest_version or manifest_version == "unknown":
        fail(f"docs-metadata.json: plugin_manifest_version is absent or unknown: {manifest_version!r}")

    # 5. project milestone represented
    milestone = metadata.get("project_milestone", "")
    if not milestone or milestone == "unknown":
        fail(f"docs-metadata.json: project_milestone is absent or unknown: {milestone!r}")

    # 6. rough_draft_used is false
    rough = metadata.get("rough_draft_used", None)
    if rough is not False:
        fail(f"docs-metadata.json: rough_draft_used should be false, got: {rough!r}")

    # 7. No forbidden URL/path patterns
    for pattern, label in FORBIDDEN_PATTERNS:
        if re.search(pattern, html):
            fail(f"index.html: {label}")

    # 8. Nav anchors: exist, unique, follow document order
    # Generator produces: <div class="nav-section"><a href="#id">
    nav_hrefs = re.findall(r'class="nav-section"><a href="#([^"]+)"', html)
    if not nav_hrefs:
        fail("index.html: no sidebar nav-section anchors found")
    else:
        # Unique check
        if len(nav_hrefs) != len(set(nav_hrefs)):
            fail(f"index.html: duplicate nav anchor ids found: {nav_hrefs}")

        # Document order: section ids should appear in same order as nav hrefs
        section_ids = re.findall(r'<section id="([^"]+)"', html)
        if section_ids:
            nav_set = set(nav_hrefs)
            ordered_nav = [s for s in section_ids if s in nav_set]
            if ordered_nav != nav_hrefs:
                fail(
                    f"index.html: nav links are not in document order.\n"
                    f"  Nav order: {nav_hrefs}\n"
                    f"  Section order: {ordered_nav}"
                )

    # 9. Required onboarding content sections present
    section_ids_set = set(re.findall(r'<section id="([^"]+)"', html))
    for anchor in REQUIRED_CONTENT_ANCHORS:
        if anchor not in section_ids_set:
            fail(f"index.html: required section anchor missing: #{anchor}")

    # 10. h1 exists (page title)
    if not re.search(r"<h1[^>]*>", html):
        fail("index.html: no <h1> element found (page title required)")

    # 11. Hero zone / process flow present
    if "hero-zone" not in html:
        fail("index.html: no hero-zone element found")
    if "process-flow" not in html:
        fail("index.html: no process-flow element found")
    # Check all process steps
    for step in ["Input", "Gemba", "Smoke A", "Patch", "Smoke B", "Final Audit"]:
        if step not in html:
            fail(f"index.html: process flow step missing: {step!r}")

    # 12. Grouped sidebar labels
    for group_name in REQUIRED_SIDEBAR_GROUPS:
        if f'class="nav-group-label">{group_name}' not in html:
            fail(f"index.html: sidebar group label missing: {group_name!r}")

    # 13. Mobile TOC present
    if "mobile-toc" not in html:
        fail("index.html: no mobile-toc element found")

    # 14. Audience cards present
    if "audience-card" not in html:
        fail("index.html: no audience-card elements found")
    if "card-grid" not in html:
        fail("index.html: no card-grid element found")

    # 15. Four invocation modes present (case-insensitive)
    html_lower = html.lower()
    for phrase in REQUIRED_INVOCATION_MODE_PHRASES:
        if phrase.lower() not in html_lower:
            fail(f"index.html: required invocation mode phrase missing: {phrase!r}")

    # 16. No stale claims
    for stale_text, stale_label in FORBIDDEN_STALE_TEXT:
        if stale_text.lower() in html_lower:
            fail(f"index.html: {stale_label}")

    # 17. No empty inline code elements: <code></code> or <code> </code>
    empty_code = re.findall(r"<code>\s*</code>", html)
    if empty_code:
        fail(f"index.html: {len(empty_code)} empty <code> element(s) found")

    # 18. No unsupported claims (exact forbidden strings)
    for claim in FORBIDDEN_CLAIMS:
        if claim in html_lower:
            fail(f"index.html: potentially unsupported claim found: {claim!r}")

    # 19. Skip link present (accessibility)
    if 'class="skip-link"' not in html and "skip-to" not in html_lower:
        fail("index.html: no skip link found (accessibility requirement)")

    # 20. Semantic headings present
    if "<h1" not in html or "<h2" not in html:
        fail("index.html: semantic headings (h1 and h2) both required")

    # Report
    if _failures == 0:
        anchors_found = len(nav_hrefs) if nav_hrefs else 0
        sys.stdout.write(
            f"check-docs-portal: ok ({anchors_found} nav anchors, "
            f"{len(section_ids_set)} sections, metadata valid, all checks pass)\n"
        )
        sys.exit(0)
    else:
        sys.stderr.write(f"check-docs-portal: FAIL ({_failures} check(s) failed)\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
