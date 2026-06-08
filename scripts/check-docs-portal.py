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
- no file:/// URLs
- no absolute Windows paths (C:\\, D:\\, etc.)
- nav anchors exist and are unique
- nav anchors follow document order (same order as sections)
- required onboarding content sections present
- no unsupported marketplace/provenance/install-proof claims
- No external dependencies; Python stdlib only.

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

REQUIRED_CONTENT_ANCHORS = [
    "what-is-implementaudit",
    "when-should-i-use-it",
    "when-should-i-not-use-it",
    "normal-prompt-vs-goal-vs-implementaudit",
    "three-invocation-modes",
    "compared-with-a-generic-staged-goal-runner",
    "what-graphify-and-activegraph-do",
    "what-completion-means",
    "install-and-update",
]

FORBIDDEN_PATTERNS = [
    # No file:/// URLs
    (r"file:///", "file:/// URL found"),
    # No absolute Windows paths in generated output
    (r"[A-Za-z]:\\\\", "absolute Windows path found"),
    (r"[A-Za-z]:/[A-Za-z]", "absolute Windows-style path found"),
]

FORBIDDEN_CLAIMS = [
    "marketplace",
    "install-proof",
    "provenance claim",
    "certified",
    "six sigma",
    "dpmo",
    "process sigma",
]


def fail(msg: str) -> None:
    sys.stderr.write(f"check-docs-portal: FAIL: {msg}\n")


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <output-dir>\n")
        sys.exit(1)

    out_dir = Path(sys.argv[1])
    failures = 0

    # 1. index.html exists and is non-empty
    index_path = out_dir / "index.html"
    if not index_path.is_file():
        fail(f"index.html not found in {out_dir}")
        sys.exit(1)
    html = index_path.read_text(encoding="utf-8")
    if len(html) < 100:
        fail(f"index.html is suspiciously small ({len(html)} bytes)")
        failures += 1

    # 2. docs-metadata.json exists with required fields
    meta_path = out_dir / "docs-metadata.json"
    if not meta_path.is_file():
        fail(f"docs-metadata.json not found in {out_dir}")
        failures += 1
        metadata = {}
    else:
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"docs-metadata.json is not valid JSON: {e}")
            failures += 1
            metadata = {}

    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            fail(f"docs-metadata.json missing required field: {field}")
            failures += 1

    # 3. source sha256s are present
    sha256s = metadata.get("source_sha256s", {})
    if not sha256s:
        fail("docs-metadata.json: source_sha256s is empty")
        failures += 1

    # 4. plugin manifest version represented
    manifest_version = metadata.get("plugin_manifest_version", "")
    if not manifest_version or manifest_version == "unknown":
        fail(f"docs-metadata.json: plugin_manifest_version is absent or unknown: {manifest_version!r}")
        failures += 1

    # 5. project milestone represented
    milestone = metadata.get("project_milestone", "")
    if not milestone or milestone == "unknown":
        fail(f"docs-metadata.json: project_milestone is absent or unknown: {milestone!r}")
        failures += 1

    # 6. rough_draft_used is false
    rough = metadata.get("rough_draft_used", None)
    if rough is not False:
        fail(f"docs-metadata.json: rough_draft_used should be false, got: {rough!r}")
        failures += 1

    # 7. No file:/// URLs, no absolute Windows paths
    for pattern, label in FORBIDDEN_PATTERNS:
        if re.search(pattern, html):
            fail(f"index.html: {label}")
            failures += 1

    # 8. Nav anchors: exist, unique, follow document order
    # Find all href="#..." in nav links
    nav_hrefs = re.findall(r'class="nav-link"[^>]*href="#([^"]+)"', html)
    if not nav_hrefs:
        # Also try href first
        nav_hrefs = re.findall(r'href="#([^"]+)"[^>]*class="nav-link"', html)
    if not nav_hrefs:
        fail("index.html: no nav-link anchors found")
        failures += 1
    else:
        # Unique check
        if len(nav_hrefs) != len(set(nav_hrefs)):
            fail(f"index.html: duplicate nav anchor ids found: {nav_hrefs}")
            failures += 1

        # Document order: section ids should appear in same order as nav hrefs
        section_ids = re.findall(r'<section id="([^"]+)"', html)
        if section_ids:
            # nav_hrefs order should match section_ids order
            nav_set = set(nav_hrefs)
            ordered_nav = [s for s in section_ids if s in nav_set]
            if ordered_nav != nav_hrefs:
                fail(
                    f"index.html: nav links are not in document order.\n"
                    f"  Nav order: {nav_hrefs}\n"
                    f"  Section order: {ordered_nav}"
                )
                failures += 1

    # 9. Required onboarding content sections present
    section_ids_set = set(re.findall(r'<section id="([^"]+)"', html))
    for anchor in REQUIRED_CONTENT_ANCHORS:
        if anchor not in section_ids_set:
            fail(f"index.html: required section anchor missing: #{anchor}")
            failures += 1

    # 10. No unsupported claims
    html_lower = html.lower()
    for claim in FORBIDDEN_CLAIMS:
        if claim in html_lower:
            fail(f"index.html: potentially unsupported claim found: {claim!r}")
            failures += 1

    # 11. Skip link present (accessibility)
    if 'class="skip-link"' not in html and "skip-to" not in html.lower():
        fail("index.html: no skip link found (accessibility requirement)")
        failures += 1

    # 12. Semantic headings present
    if "<h1" not in html and "<h2" not in html:
        fail("index.html: no semantic headings (h1/h2) found")
        failures += 1

    if failures == 0:
        anchors_found = len(nav_hrefs)
        sys.stdout.write(f"check-docs-portal: ok ({anchors_found} nav anchors, metadata valid, all checks pass)\n")
        sys.exit(0)
    else:
        sys.stderr.write(f"check-docs-portal: FAIL ({failures} check(s) failed)\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
