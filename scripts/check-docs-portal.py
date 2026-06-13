#!/usr/bin/env python3
'''
check-docs-portal.py - validate generated IMPLEMENTAUDIT docs portal output.

Usage:
    python scripts/check-docs-portal.py <output-dir>

The portal is generated from docs/portal/. This checker validates the
multipage shell, not the legacy single-page portal shape.
'''

import hashlib
import html as html_lib
import json
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED_METADATA_FIELDS = [
    "repo",
    "head_commit_sha",
    "worktree_state",
    "worktree_dirty",
    "generated_at",
    "project_milestone",
    "plugin_manifest_version",
    "release_url",
    "audit_ledger_url",
    "checksum_boundary",
    "portal_version",
    "page_count",
    "source_files_used",
    "source_sha256s",
    "rough_draft_used",
]

REQUIRED_GROUPS = [
    "Overview",
    "First run",
    "Audience",
    "Core model",
    "Evidence",
    "Closure",
    "Repository",
    "References",
]

TOP_NAV = [
    ("Overview", "overview"),
    ("Quick Start", "quick-start"),
    ("Install", "installation"),
    ("Runtime model", "runtime-model"),
]

TOP_NAV_BUCKET_TARGETS = {
    "plain-english": "overview",
    "what-it-is": "overview",
    "workflow": "overview",
    "success-and-proof": "overview",
    "possible-endings": "quick-start",
    "comparison": "quick-start",
    "audit-gate-model": "runtime-model",
    "invocation-shapes": "runtime-model",
    "usage-examples": "runtime-model",
    "planning-and-phases": "runtime-model",
    "routing": "runtime-model",
    "operating-method": "runtime-model",
}

REQUIRED_PAGES = [
    "overview",
    "plain-english",
    "what-it-is",
    "workflow",
    "success-and-proof",
    "quick-start",
    "installation",
    "possible-endings",
    "for-new-users",
    "for-agents-and-operators",
    "for-auditors-and-maintainers",
    "runtime-model",
    "audit-gate-model",
    "invocation-shapes",
    "planning-and-phases",
    "routing",
    "state-and-artifacts",
    "repo-state-comparison",
    "error-handling",
    "evidence-boundaries",
    "completion-semantics",
    "continuity-and-sidecars",
    "operating-method",
    "comparison",
    "usage-examples",
    "repo-layout",
    "terminology",
    "child-agent-review-loops",
    "optional-tooling",
    "package-contents",
    "audit-trail",
    "reference-index",
]

REQUIRED_CONCEPTS = [
    "run folder",
    "STATE.md",
    "phase checklist",
    "before/after",
    "AUDIT_COMPLETE",
    "IMPLEMENTAUDIT_RUN_COMPLETE",
    "AUDIT_WARNING",
    "ANDON_PROBE",
    "ANDON_ESCALATE",
    "ANDON_HANDOFF",
    "IMPLEMENTAUDIT_PAUSE",
    "tdqyq-audit-object",
    "ydqyq-audit-action",
    "direct governance",
    "embedded governance",
    "goal synthesis",
    "governed casual-build intake",
    "DMAIC",
    "DMADV",
    "install-codex-from-release.sh",
    "install-claude-from-release.sh",
    "PREFLIGHT_GREEN",
    "PREFLIGHT_RED",
    "Self-critique:",
    "Annotated ten gates",
    "Helper failure semantics",
    "What belongs in AGENTS.md",
    "P0 -&gt; P1 -&gt; P2",
    "OWNER DECISION",
    "Polish and Harden",
    "IMPLEMENTAUDIT_CONTINUITY_SAVED",
    "CONTINUITY_DECISION",
    "applied-context.md",
    "applied-memories.md",
    "repo-map.md",
    "tools.md",
    "context.md",
    "five-source priority",
    "New evidence:",
    "Changed approach:",
    "failed-criterion",
    "generated-artifact-mismatch",
    "tdqyq-audit-object",
    "live runtime",
    "local generated-runtime",
    "package-bound",
    "visual/browser",
    "--onboard-tools",
    "Scope-creep register",
    "Local git trace",
    "Marker contract",
    "Per-phase execution loop",
    "Lean terms as behavior",
    "ActiveGraph precision",
    "Review invariants",
    "Release maintenance gates",
    "Docs portal generation",
    "local installs do not auto-update",
    "Slash commands fire only when the user submits them.",
    "IMPLEMENTAUDIT_SKILL_DIR",
]

REQUIRED_CONCEPT_PATTERNS = [
    re.compile(r"IMPLEMENTAUDIT\.skill/(?:<br>|\s+)SKILL\.md", re.IGNORECASE),
    re.compile(r"\$\{IMPLEMENTAUDIT_SKILL_DIR:-skills\}/scripts/", re.IGNORECASE),
]

RESERVED_OUTPUT_ROOTS = {"assets"}

FORBIDDEN_VISIBLE_TEXT = [
    ("three invocation modes", "stale invocation-count claim"),
    ("three invocation shapes", "stale invocation-count claim"),
    ("release pending", "stale release-pending claim"),
    ("--version 0.2.4", "stale install version"),
    ("published to the marketplace", "affirmative marketplace publication claim"),
    ("listed on the marketplace", "affirmative marketplace listing claim"),
    ("provenance claim", "unsupported provenance wording"),
    ("class=\"kdetails\"", "collapsed runtime drawer should not return"),
    ("Open the full runtime model", "collapsed runtime drawer summary should not return"),
    ("docs/portal_old/onboarding.md", "legacy portal source should not be visible in v2 pages"),
    ("/plugin marketplace add", "unverified Claude Code marketplace command"),
    ("/plugin install implementaudit@implementaudit", "unverified Claude Code marketplace command"),
    ("release asset ships the runtime payload under <code>skills/</code>", "stale package-layout claim"),
    ("skills: \"./skills/\"", "stale plugin manifest skills path claim"),
    ("IMPLEMENTAUDIT.skill/<br>skills/SKILL.md", "stale nested package tree claim"),
    ("/implementdocs", "future docs-system project should not be claimed in generated pages"),
    ("IMPLEMENTDOCS", "future docs-system project should not be claimed in generated pages"),
    ("Pages is live", "unsupported GitHub Pages publication claim"),
    ("GitHub Pages is live", "unsupported GitHub Pages publication claim"),
    ("Pages is deployed", "unsupported GitHub Pages publication claim"),
    ("GitHub Pages is deployed", "unsupported GitHub Pages publication claim"),
    ("Pages is publicly accessible", "unsupported GitHub Pages publication claim"),
    ("GitHub Pages is publicly accessible", "unsupported GitHub Pages publication claim"),
    ("A docs page should cite release and audit evidence", "stray current-status placeholder copy"),
]

_failures = 0


def fail(msg: str) -> None:
    global _failures
    _failures += 1
    sys.stderr.write(f"check-docs-portal: FAIL: {msg}\n")


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")
    return {}


def normalize_page_path(page_id: str, raw_path: object) -> str | None:
    if not isinstance(raw_path, str):
        fail(f"page {page_id}: path must be a string")
        return None
    if raw_path == "":
        return ""
    if "\\" in raw_path:
        fail(f"page {page_id}: path must use forward slashes: {raw_path!r}")
        return None
    if raw_path.startswith("/") or re.match(r"^[A-Za-z]:", raw_path) or "://" in raw_path:
        fail(f"page {page_id}: path must be repo-relative: {raw_path!r}")
        return None
    if "//" in raw_path:
        fail(f"page {page_id}: path must not contain empty segments: {raw_path!r}")
        return None
    if not raw_path.endswith("/"):
        fail(f"page {page_id}: path must end with /: {raw_path!r}")
        return None
    parts = [part for part in raw_path.strip("/").split("/") if part]
    if not parts:
        fail(f"page {page_id}: only overview may use empty path")
        return None
    if parts[0].lower() in RESERVED_OUTPUT_ROOTS:
        fail(f"page {page_id}: path cannot live under reserved root {parts[0]!r}")
        return None
    for part in parts:
        if part in {".", ".."}:
            fail(f"page {page_id}: path must not contain {part!r}: {raw_path!r}")
            return None
        if posixpath.splitext(part)[1]:
            fail(f"page {page_id}: path segments must not have extensions: {raw_path!r}")
            return None
    return "/".join(parts) + "/"


def validate_page_source(page_id: str, raw_source: object, pages_dir: Path) -> str | None:
    if not isinstance(raw_source, str) or not raw_source:
        fail(f"page {page_id}: source must be a non-empty string")
        return None
    if "/" in raw_source or "\\" in raw_source or raw_source in {".", ".."} or ".." in raw_source:
        fail(f"page {page_id}: source must be a file name under docs/portal/pages: {raw_source!r}")
        return None
    if Path(raw_source).suffix != ".html":
        fail(f"page {page_id}: source must be .html: {raw_source!r}")
        return None
    if not (pages_dir / raw_source).is_file():
        fail(f"page {page_id}: source file missing: {raw_source!r}")
        return None
    return raw_source


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_site(root: Path) -> tuple[dict, list[dict], dict]:
    site_path = root / "docs" / "portal" / "site.json"
    site = read_json(site_path)
    if not site:
        return {}, [], {}
    pages = site.get("pages", {})
    pages_dir = root / "docs" / "portal" / "pages"
    output_routes = {}
    referenced_sources = set()
    if not isinstance(pages, dict):
        fail("site pages must be an object")
        return site, [], {}
    for page_id, page in pages.items():
        if not isinstance(page, dict):
            fail(f"page {page_id}: page entry must be an object")
            continue
        if not isinstance(page.get("title"), str) or not page.get("title"):
            fail(f"page {page_id}: title must be a non-empty string")
        normalized_path = normalize_page_path(page_id, page.get("path", ""))
        if normalized_path is not None:
            page["path"] = normalized_path
            route_key = (normalized_path or ".").lower()
            if route_key in output_routes:
                fail(f"pages {output_routes[route_key]} and {page_id} generate the same output route")
            output_routes[route_key] = page_id
        source = validate_page_source(page_id, page.get("source"), pages_dir)
        if source:
            page["source"] = source
            referenced_sources.add(source)
    orphan_sources = sorted(path.name for path in pages_dir.glob("*.html") if path.name not in referenced_sources)
    if orphan_sources:
        fail(f"docs portal page source(s) are not referenced by site.json: {orphan_sources}")
    ordered = []
    seen = set()
    for group in site.get("nav", []):
        for page_id in group.get("pages", []):
            if page_id not in pages:
                fail(f"site nav references missing page: {page_id}")
                continue
            if page_id in seen:
                fail(f"page appears twice in site nav: {page_id}")
                continue
            page = dict(pages[page_id])
            page["id"] = page_id
            page["group"] = group.get("group", "")
            ordered.append(page)
            seen.add(page_id)
    missing = sorted(set(pages) - seen)
    if missing:
        fail(f"site pages missing from nav: {missing}")
    return site, ordered, {page["id"]: page for page in ordered}


def page_output(out_dir: Path, page: dict) -> Path:
    rel = page.get("path", "")
    return out_dir / "index.html" if rel == "" else out_dir / rel / "index.html"


def page_dir(page: dict) -> str:
    rel = page.get("path", "").strip("/")
    return rel if rel else "."


def rel_href(current: dict, target: dict | str) -> str:
    target_path = target.strip("/") if isinstance(target, str) else target.get("path", "").strip("/")
    target_path = target_path or "."
    rel = posixpath.relpath(target_path, page_dir(current))
    if rel == ".":
        return "./"
    if not rel.endswith("/") and not posixpath.splitext(rel)[1]:
        rel += "/"
    return rel


class AttrCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {name.lower(): value or "" for name, value in attrs}
        if "id" in data:
            self.ids.append(data["id"])
        for key in ("href", "src"):
            if key in data:
                self.refs.append(data[key])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


class H2Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "h2":
            return
        data = {name.lower(): value or "" for name, value in attrs}
        if "id" in data:
            self.ids.append(data["id"])


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict] = []
        self._current: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._current = {
            "attrs": {name.lower(): value or "" for name, value in attrs},
            "text_parts": [],
        }

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text_parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current is None:
            return
        attrs = self._current["attrs"]
        text = " ".join("".join(self._current["text_parts"]).split())
        self.links.append({"attrs": attrs, "href": attrs.get("href", ""), "text": text})
        self._current = None


def collect_attrs(html: str) -> AttrCollector:
    collector = AttrCollector()
    collector.feed(html)
    return collector


def ids_in(html: str) -> list[str]:
    return collect_attrs(html).ids


def refs_in(html: str) -> list[str]:
    return collect_attrs(html).refs


def h2_ids_in(html: str) -> list[str]:
    collector = H2Collector()
    collector.feed(html)
    return collector.ids


def links_in(html: str) -> list[dict]:
    collector = LinkCollector()
    collector.feed(html)
    return collector.links


def text_content(fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(without_tags)).strip()


RAW_RUNNABLE_COMMAND_RE = re.compile(
    r"^(?:[$>]\s*|(?:PS|C:\\[^>\r\n]*)>\s*)?"
    r"(?:/implementaudit|/goal|bash |mkdir |cp |New-Item|Copy-Item)",
    re.IGNORECASE,
)


def has_raw_runnable_command_pre(html_text: str) -> bool:
    for match in re.finditer(r"<pre(?:\s+[^>]*)?><code>([\s\S]*?)</code></pre>", html_text, flags=re.IGNORECASE):
        body = html_lib.unescape(match.group(1))
        for line in body.splitlines():
            if RAW_RUNNABLE_COMMAND_RE.search(line.strip()):
                return True
    return False


def first_region(html_text: str, class_name: str, tag: str = r"[a-z0-9]+") -> str:
    match = re.search(
        rf'<(?P<tag>{tag})\b[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[\s\S]*?</(?P=tag)>',
        html_text,
        flags=re.IGNORECASE,
    )
    return match.group(0) if match else ""


def rendered_sidebar_model(side: str) -> list[tuple[str, list[tuple[str, str]]]]:
    rendered = []
    for group_match in re.finditer(r'<details class="nav-group" open>([\s\S]*?)</details>', side):
        block = group_match.group(1)
        title_match = re.search(r'<summary class="nav-title">([\s\S]*?)</summary>', block)
        title = text_content(title_match.group(1)) if title_match else ""
        links = [
            (text_content(label), href)
            for href, label in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', block)
        ]
        rendered.append((title, links))
    return rendered


def expected_top_nav_target(page: dict) -> str | None:
    if page["id"] in {page_id for _, page_id in TOP_NAV}:
        return page["id"]
    return TOP_NAV_BUCKET_TARGETS.get(page["id"])


def local_target(out_dir: Path, html_path: Path, href: str) -> tuple[Path | None, str | None, bool]:
    split = urlsplit(href)
    if split.scheme or split.netloc:
        return None, None, False
    path_part = unquote(split.path)
    fragment = unquote(split.fragment) if split.fragment else None
    if path_part == "":
        return html_path, fragment, True
    base = html_path.parent.relative_to(out_dir).as_posix()
    if base == ".":
        base = ""
    normalized = posixpath.normpath(posixpath.join(base, path_part))
    if normalized.startswith("../"):
        return Path(normalized), fragment, True
    suffix = posixpath.splitext(normalized)[1]
    if path_part.endswith("/") or suffix == "":
        normalized = "index.html" if normalized == "." else posixpath.join(normalized, "index.html")
    return out_dir / Path(normalized), fragment, True


def validate_links(out_dir: Path, html_files: list[Path]) -> None:
    for html_path in html_files:
        html_text = html_path.read_text(encoding="utf-8")
        for href in refs_in(html_text):
            target, fragment, is_local = local_target(out_dir, html_path, href)
            if not is_local:
                continue
            if target is None:
                continue
            if not target.is_absolute():
                fail(f"{html_path.relative_to(out_dir).as_posix()}: local link escapes output: {href}")
                continue
            if not target.exists():
                fail(f"{html_path.relative_to(out_dir).as_posix()}: broken local link: {href}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_ids = set(ids_in(target.read_text(encoding="utf-8")))
                if fragment not in target_ids:
                    fail(
                        f"{html_path.relative_to(out_dir).as_posix()}: "
                        f"broken hash link {href} (#{fragment} missing)"
                    )


def validate_page_shell(out_dir: Path, site: dict, ordered: list[dict], pages_by_id: dict) -> list[Path]:
    html_files = []
    expected_html = {page_output(out_dir, page).resolve() for page in ordered}
    actual_html = {path.resolve() for path in out_dir.rglob("*.html")}
    extra_html = sorted(path.relative_to(out_dir).as_posix() for path in actual_html - expected_html)
    missing_html = sorted(path.relative_to(out_dir).as_posix() for path in expected_html - actual_html)
    if extra_html:
        fail(f"unexpected generated HTML files: {extra_html}")
    if missing_html:
        fail(f"expected generated HTML files missing: {missing_html}")
    asset_dir = repo_root() / "docs" / "portal" / "assets"
    expected_files = set(expected_html)
    expected_files.add((out_dir / "docs-metadata.json").resolve())
    expected_files.update((out_dir / "assets" / path.name).resolve() for path in asset_dir.iterdir() if path.is_file())
    actual_files = {path.resolve() for path in out_dir.rglob("*") if path.is_file()}
    extra_files = sorted(path.relative_to(out_dir).as_posix() for path in actual_files - expected_files)
    missing_files = sorted(path.relative_to(out_dir).as_posix() for path in expected_files - actual_files)
    if extra_files:
        fail(f"unexpected generated files: {extra_files}")
    if missing_files:
        fail(f"expected generated files missing: {missing_files}")
    ordered_ids = [page["id"] for page in ordered]
    for idx, page in enumerate(ordered):
        path = page_output(out_dir, page)
        if not path.is_file():
            fail(f"missing generated page: {page['id']} at {path}")
            continue
        html_text = path.read_text(encoding="utf-8")
        html_files.append(path)
        rel = path.relative_to(out_dir).as_posix()
        if page["id"] == "overview":
            release = site.get("release", {})
            milestone = str(release.get("milestone", ""))
            audit_ledger_url = str(release.get("audit_ledger_url", ""))
            hero = first_region(html_text, "hero", tag="section")
            meta_row = first_region(hero, "meta-row", tag="div")
            if not meta_row:
                fail(f"{rel}: overview hero missing current release metadata row")
            else:
                if milestone and milestone not in meta_row:
                    fail(f"{rel}: overview hero current release does not match docs/portal/site.json")
                if audit_ledger_url and audit_ledger_url not in hero:
                    fail(f"{rel}: overview hero evidence link does not match docs/portal/site.json")
        if len(html_text) < 800:
            fail(f"{rel}: suspiciously small HTML")
        if "<h1" not in html_text:
            fail(f"{rel}: missing h1")
        if 'class="side-nav"' not in html_text:
            fail(f"{rel}: missing side navigation")
        if 'class="mobile-toc"' not in html_text:
            fail(f"{rel}: missing mobile table of contents")
        if 'class="toc"' not in html_text:
            fail(f"{rel}: missing desktop table of contents")
        if 'class="page-nav"' not in html_text:
            fail(f"{rel}: missing previous/next page navigation")
        if 'class="skip"' not in html_text:
            fail(f"{rel}: missing skip link")
        if not re.search(r'<link rel="stylesheet" href="(?:\.\./)*assets/draft-v2\.css\?v=[0-9a-f]{12}">', html_text):
            fail(f"{rel}: stylesheet URL should include a source-hash cache buster")
        if not re.search(r'<script src="(?:\.\./)*assets/draft-v2\.js\?v=[0-9a-f]{12}"></script>', html_text):
            fail(f"{rel}: script URL should include a source-hash cache buster")
        top = first_region(html_text, "top-actions", tag="nav")
        if not top:
            fail(f"{rel}: cannot inspect top navigation region")
        else:
            if 'class="top-tabs"' not in top or 'class="top-tab-indicator" aria-hidden="true"' not in top:
                fail(f"{rel}: top navigation should render as a tab group with an active indicator")
            if 'style="--active-index:' not in top or '--tab-count: 4' not in top:
                fail(f"{rel}: top navigation tab group missing active-index/tab-count style contract")
            if len(re.findall(r'<a\b[^>]*class="top-tab(?:\s+active)?"', top)) != len(TOP_NAV):
                fail(f"{rel}: top navigation should render exactly {len(TOP_NAV)} tab links")
            if re.search(r'<a class="gh"[^>]*>\s*GitHub\s*</a>', top):
                fail(f"{rel}: GitHub topbar link must be icon-only with sr-only text")
            if 'aria-label="GitHub repository"' not in top or "<svg" not in top or 'class="sr-only">GitHub</span>' not in top:
                fail(f"{rel}: GitHub topbar link missing icon, aria-label, or sr-only label")
            for removed_label in ("Proof", "References"):
                if re.search(rf">\s*{removed_label}\s*</a>", top):
                    fail(f"{rel}: top navigation should not include {removed_label}; use the sidebar instead")
            top_links = links_in(top)
            page_current = [link for link in top_links if link["attrs"].get("aria-current") == "page"]
            location_current = [link for link in top_links if link["attrs"].get("aria-current") == "location"]
            expected_target_id = expected_top_nav_target(page)
            expected_top_href = rel_href(page, pages_by_id[expected_target_id]) if expected_target_id else None
            if page["id"] in {page_id for _, page_id in TOP_NAV}:
                if len(page_current) != 1 or page_current[0]["href"] != expected_top_href:
                    fail(f"{rel}: top navigation exact page should have one aria-current=page link to itself")
                elif "active" not in page_current[0]["attrs"].get("class", "").split():
                    fail(f"{rel}: top navigation exact page link should use active styling")
                if location_current:
                    fail(f"{rel}: top navigation exact page should not also mark a bucket as current")
            else:
                if page_current:
                    fail(f"{rel}: top navigation bucket page should not use aria-current=page")
                if expected_target_id is None:
                    if location_current:
                        fail(f"{rel}: top navigation should not mark a bucket for unrepresented sidebar group")
                elif len(location_current) != 1 or location_current[0]["href"] != expected_top_href:
                    fail(f"{rel}: top navigation should mark one containing bucket with aria-current=location")
                elif "active" in location_current[0]["attrs"].get("class", "").split():
                    fail(f"{rel}: top navigation bucket link should not use active styling")
        side = first_region(html_text, "side-nav", tag="aside")
        if not side:
            fail(f"{rel}: cannot inspect side navigation region")
        else:
            for token in (
                'class="nav-docs-head"',
                'class="nav-window-dots"',
                '<details class="nav-group" open>',
                '<summary class="nav-title">',
                'class="nav-caret" aria-hidden="true"',
            ):
                if token not in side:
                    fail(f"{rel}: sidebar file-tree navigation missing {token}")
            if "<span>Docs</span>" not in side or "<span>explorer</span>" in side:
                fail(f"{rel}: sidebar file-tree header should be labeled Docs")
            if 'nav-folder-icon' in side or 'nav-file-icon' in side:
                fail(f"{rel}: sidebar should not render sheet or folder icons")
            active_links = re.findall(r'<a\b[^>]*aria-current="page"[^>]*>', side)
            if len(active_links) != 1:
                fail(f"{rel}: sidebar should have exactly one active page, found {len(active_links)}")
            else:
                active_match = re.search(r'<a\b[^>]*aria-current="page"[^>]*>([\s\S]*?)</a>', side)
                active_text = text_content(active_match.group(1)) if active_match else ""
                active_class = re.search(r'\bclass="([^"]*)"', active_links[0])
                active_classes = active_class.group(1).split() if active_class else []
                if f'href="{rel_href(page, page)}"' not in active_links[0] or active_text != page["title"]:
                    fail(f"{rel}: sidebar active page does not match current route")
                if "nav-file" not in active_classes or "active" not in active_classes:
                    fail(f"{rel}: sidebar active page should use nav-file active classes")
            expected_sidebar = []
            for group in site.get("nav", []):
                expected_sidebar.append((
                    group.get("group", ""),
                    [
                        (pages_by_id[page_id]["title"], rel_href(page, pages_by_id[page_id]))
                        for page_id in group.get("pages", [])
                        if page_id in pages_by_id
                    ],
                ))
            if rendered_sidebar_model(side) != expected_sidebar:
                fail(f"{rel}: rendered sidebar order does not match docs/portal/site.json")

        if 'class="page-context"' in html_text:
            fail(f"{rel}: duplicate top page context trail should not be rendered")
        proof_index = html_text.find('class="page-proof-strip"')
        footer_index = html_text.find("<footer>")
        if proof_index == -1:
            fail(f"{rel}: missing page source/release proof strip")
        elif footer_index == -1 or proof_index < footer_index:
            fail(f"{rel}: page source/release proof strip should render in the footer region")
        else:
            proof = first_region(html_text[footer_index:], "page-proof-strip", tag="dl")
            release = site.get("release", {})
            rel_source = f"docs/portal/pages/{page['source']}"
            if release and str(release.get("milestone", "")) not in proof:
                fail(f"{rel}: proof strip missing release milestone")
            if f"<code>{rel_source}</code>" not in proof:
                fail(f"{rel}: proof strip missing exact page source")
            if release and str(release.get("checksum_boundary", "")) in proof:
                fail(f"{rel}: proof strip should not render redundant checksum boundary text")
            if "<dt>Boundary</dt>" in proof:
                fail(f"{rel}: proof strip should not render a redundant Boundary cell")
            if "Changelog" not in proof or "Source" not in proof:
                fail(f"{rel}: proof strip release cell should carry Changelog and Source links")
            if proof.find("<dt>Page source</dt>") > proof.find("<dt>Release</dt>"):
                fail(f"{rel}: proof strip should place Page source before Release")
            if proof.find(">Source</a>") > proof.find(">Changelog</a>"):
                fail(f"{rel}: proof strip should place Source before Changelog")
            foot_inner = first_region(html_text[footer_index:], "foot-inner", tag="div")
            if release and str(release.get("checksum_boundary", "")) in foot_inner:
                fail(f"{rel}: checksum boundary should not render in compact footer metadata")
            if "Changelog" in foot_inner or "Source" in foot_inner or re.search(r">\s*Release\s+v", foot_inner):
                fail(f"{rel}: compact footer links should not duplicate release proof metadata")

        ids = ids_in(html_text)
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        if duplicates:
            fail(f"{rel}: duplicate ids: {duplicates}")

        prev_page = ordered[idx - 1] if idx > 0 else None
        next_page = ordered[idx + 1] if idx + 1 < len(ordered) else None
        expected_prev = rel_href(page, prev_page) if prev_page else None
        expected_next = rel_href(page, next_page) if next_page else None
        page_nav_block = first_region(html_text, "page-nav", tag="nav")
        if not page_nav_block:
            fail(f"{rel}: cannot inspect previous/next page navigation region")
        if expected_prev and 'class="page-prev magnet-link"' not in page_nav_block:
            fail(f"{rel}: previous-page link should use page-prev magnet-link classes")
        if expected_next and 'class="page-next magnet-link"' not in page_nav_block:
            fail(f"{rel}: next-page link should use page-next magnet-link classes")
        if expected_prev and f'href="{expected_prev}"' not in page_nav_block:
            fail(f"{rel}: missing expected previous-page link to {ordered_ids[idx - 1]}")
        if expected_next and f'href="{expected_next}"' not in page_nav_block:
            fail(f"{rel}: missing expected next-page link to {ordered_ids[idx + 1]}")

        for nav_page in ordered:
            expected = rel_href(page, nav_page)
            if side and f'href="{expected}"' not in side:
                fail(f"{rel}: sidebar missing route to {nav_page['id']}")
        if page["id"] in {"continuity-and-sidecars", "routing", "evidence-boundaries", "package-contents"}:
            expected_optional_href = rel_href(page, pages_by_id["optional-tooling"])
            article_region = first_region(html_text, "article", tag="article") or html_text
            if f'href="{expected_optional_href}"' not in article_region:
                fail(f"{rel}: article missing local link to Optional tooling")
        if page["id"] == "reference-index":
            article_region = first_region(html_text, "article", tag="article")
            index_links = [
                link
                for link in links_in(article_region)
                if "index-card" in link["attrs"].get("class", "").split()
            ]
            expected_hrefs = [
                rel_href(page, nav_page)
                for nav_page in ordered
            ]
            actual_hrefs = [link["href"] for link in index_links]
            if actual_hrefs != expected_hrefs:
                fail(f"{rel}: reference index cards should mirror full sidebar order")
        if page["id"] == "usage-examples":
            article_region = first_region(html_text, "article", tag="article")
            pre_blocks = re.findall(r"<pre[\s\S]*?</pre>", article_region)
            if article_region.count('class="term-window example-console"') < 3:
                fail(f"{rel}: usage examples command blocks should use terminal wrappers")
            if 'class="example-terminal-grid"' not in article_region:
                fail(f"{rel}: usage examples first-run commands should render as a terminal grid")
            if any(
                "$ /implementaudit fix the findings in AUDIT.md" in pre_block
                and "$ /implementaudit &lt; audit.md" in pre_block
                and "$ /goal using /implementaudit, close the findings in AUDIT.md" in pre_block
                for pre_block in pre_blocks
            ):
                fail(f"{rel}: usage examples first-run commands must be separate alternative terminal inputs")
            if re.search(r"<pre><code>/implementaudit", article_region):
                fail(f"{rel}: usage examples should not render raw slash-command pre blocks")
        if page["id"] == "invocation-shapes":
            article_region = first_region(html_text, "article", tag="article")
            pre_blocks = re.findall(r"<pre[\s\S]*?</pre>", article_region)
            if article_region.count('class="term-window example-console"') < 6:
                fail(f"{rel}: invocation-shape command examples should use terminal wrappers")
            if 'class="shape-command-grid"' not in article_region:
                fail(f"{rel}: invocation shapes should group command examples by shape")
            if (
                any(
                    "$ /implementaudit add tests for the login timeout bug" in pre_block
                    and "$ /implementaudit close the findings in AUDIT.md" in pre_block
                    for pre_block in pre_blocks
                )
                or "paste one concrete request" not in article_region
                or "separate request instead" not in article_region
            ):
                fail(f"{rel}: What to paste examples must be separate alternative terminal inputs")
            if "Slash commands fire only when the user submits them." not in article_region:
                fail(f"{rel}: slash-command handoff boundary text is missing")
        if page["id"] == "repo-state-comparison":
            article_region = first_region(html_text, "article", tag="article")
            if article_region.count('class="term-window example-console"') < 1:
                fail(f"{rel}: repo-state helper commands should use a terminal wrapper")
            if re.search(r'<pre class="panel"><code>bash "\$\{IMPLEMENTAUDIT_SKILL_DIR', article_region):
                fail(f"{rel}: repo-state helper commands should not render as a plain panel")
            if "${IMPLEMENTAUDIT_SKILL_DIR:-skills}" not in article_region:
                fail(f"{rel}: repo-state helper examples must keep IMPLEMENTAUDIT_SKILL_DIR fallback")
            if "/path/to/loaded/IMPLEMENTAUDIT.skill" in article_region:
                fail(f"{rel}: IMPLEMENTAUDIT_SKILL_DIR must not point at the .skill archive")
            if "IMPLEMENTAUDIT_BASE" not in article_region:
                fail(f"{rel}: repo-state helper boundary should distinguish IMPLEMENTAUDIT_BASE")
        if page["id"] == "installation":
            article_region = first_region(html_text, "article", tag="article")
            if article_region.count('class="term-window example-console"') < 6:
                fail(f"{rel}: installation command blocks should use terminal wrappers")
        if page["id"] == "planning-and-phases":
            article_region = first_region(html_text, "article", tag="article")
            if 'class="stage-table"' not in article_region or 'class="stage-num"' not in article_region:
                fail(f"{rel}: stage table must keep stage-table and stage-num colgroup classes")
            for option in ("Start now", "Adjust assumption", "Tweak a phase", "Restructure phases", "Abort"):
                if option not in article_region:
                    fail(f"{rel}: stage synthesis owner-choice menu missing {option}")
        if page["id"] == "runtime-model":
            article_region = first_region(html_text, "article", tag="article")
            if 'class="layer-table"' not in article_region or 'class="layer-num"' not in article_region:
                fail(f"{rel}: runtime controls table must keep layer-table and layer-num colgroup classes")
            for marker in ("AUDIT_WARNING", "IMPLEMENTAUDIT_PAUSE"):
                if marker not in article_region:
                    fail(f"{rel}: marker taxonomy missing {marker}")
            if "Runtime-supplied forbidden identity checks" not in article_region:
                fail(f"{rel}: runtime model missing release-gate identity hygiene contract")
        if page["id"] == "continuity-and-sidecars":
            article_region = first_region(html_text, "article", tag="article")
            if 'class="priority-table"' not in article_region or 'class="priority-num"' not in article_region:
                fail(f"{rel}: preload priority table must keep priority-table and priority-num colgroup classes")
            for token in ("graphify-out/graph.json", "source", "target", "stale"):
                if token not in article_region:
                    fail(f"{rel}: sidecar continuity should document graph schema and staleness")
        if page["id"] == "error-handling":
            article_region = first_region(html_text, "article", tag="article")
            for option in ("Resume", "Revise spec", "Skip phase", "Stop"):
                if option not in article_region:
                    fail(f"{rel}: interruption resume menu missing {option}")
        if page["id"] == "comparison":
            article_region = first_region(html_text, "article", tag="article")
            if 'class="comparison-winner card-spotlight"' not in article_region:
                fail(f"{rel}: IMPLEMENTAUDIT comparison card should use distinct winner styling")
            if re.search(r'<section\s+class="comparison-winner card-spotlight"[^>]*\stabindex=', article_region):
                fail(f"{rel}: non-action comparison spotlight card should not be keyboard focusable")
        if page["id"] == "package-contents":
            article_region = first_region(html_text, "article", tag="article")
            if "${IMPLEMENTAUDIT_SKILL_DIR:-skills}/scripts/" not in article_region:
                fail(f"{rel}: installed helper path boundary must use IMPLEMENTAUDIT_SKILL_DIR fallback")
            for token in ('skills: "./"', "release-asset-install.test.sh", "release-asset-install-claude.test.sh"):
                if token not in article_region:
                    fail(f"{rel}: package contents missing release asset import/smoke boundary {token}")
            if '<h2 id="templates">' not in article_region or '<h2 id="source-surfaces">' not in article_region:
                fail(f"{rel}: package contents missing templates/source-surfaces section anchors")
            else:
                template_region = article_region.split('<h2 id="templates">', 1)[1].split('<h2 id="source-surfaces">', 1)[0]
                if 'class="artifact-card-grid"' not in template_region:
                    fail(f"{rel}: package templates should render as an artifact card grid")
                if template_region.count('class="artifact-card"') < 9:
                    fail(f"{rel}: package templates should render each shipped template surface as a card")
                if "Templates include" in template_region:
                    fail(f"{rel}: package templates should not collapse back to a plain include sentence")
                for token in (
                    "STATE.md",
                    "ROADMAP.md",
                    "THINKING.md",
                    "PROTOCOL.md",
                    "sidecars.md",
                    "tools.md",
                    "context.md",
                    "phase-goal.txt",
                    "child-agent-report.md",
                    "Proof boundary",
                ):
                    if token not in template_region:
                        fail(f"{rel}: package template cards missing {token}")
        if page["id"] == "for-auditors-and-maintainers":
            article_region = first_region(html_text, "article", tag="article")
            expected_hrefs = {
                rel_href(page, pages_by_id["repo-layout"]),
                rel_href(page, pages_by_id["package-contents"]),
                rel_href(page, pages_by_id["optional-tooling"]),
                rel_href(page, pages_by_id["audit-trail"]),
            }
            actual_hrefs = {
                link["href"]
                for link in links_in(article_region)
                if "index-card" in link["attrs"].get("class", "").split()
            }
            if not expected_hrefs.issubset(actual_hrefs):
                fail(f"{rel}: maintainer surface cards should link to their reference pages")
        if page.get("kind") != "overview":
            article = first_region(html_text, "article", tag="article")
            toc_region = first_region(html_text, "toc", tag="aside")
            mobile_toc_region = first_region(html_text, "mobile-toc", tag="details")
            for anchor in h2_ids_in(article):
                if f'href="#{anchor}"' not in toc_region:
                    fail(f"{rel}: desktop TOC missing h2 anchor #{anchor}")
                if f'href="#{anchor}"' not in mobile_toc_region:
                    fail(f"{rel}: mobile TOC missing h2 anchor #{anchor}")
    if pages_by_id.get("overview") and ordered and ordered[0]["id"] != "overview":
        fail("overview is not the first generated page")
    return html_files


def validate_metadata(out_dir: Path, site: dict, ordered: list[dict]) -> None:
    meta_path = out_dir / "docs-metadata.json"
    if not meta_path.is_file():
        fail("docs-metadata.json not found")
        return
    metadata = read_json(meta_path)
    if not metadata:
        return
    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            fail(f"docs-metadata.json missing required field: {field}")
    if metadata.get("portal_version") != "v2-multipage":
        fail(f"docs-metadata.json portal_version should be v2-multipage, got {metadata.get('portal_version')!r}")
    if metadata.get("page_count") != len(ordered):
        fail(f"docs-metadata.json page_count mismatch: {metadata.get('page_count')!r} vs {len(ordered)}")
    if metadata.get("rough_draft_used") is not False:
        fail(f"docs-metadata.json rough_draft_used should be false, got {metadata.get('rough_draft_used')!r}")
    if metadata.get("worktree_state") not in {"clean", "dirty", "unknown"}:
        fail(f"docs-metadata.json worktree_state should be clean, dirty, or unknown, got {metadata.get('worktree_state')!r}")
    if not isinstance(metadata.get("worktree_dirty"), bool):
        fail(f"docs-metadata.json worktree_dirty should be boolean, got {metadata.get('worktree_dirty')!r}")
    if metadata.get("worktree_state") in {"clean", "dirty"} and metadata.get("worktree_dirty") != (metadata.get("worktree_state") == "dirty"):
        fail("docs-metadata.json worktree_dirty does not match worktree_state")
    release = site.get("release", {})
    if release:
        if metadata.get("project_milestone") != release.get("milestone"):
            fail("docs-metadata.json project_milestone does not match docs/portal/site.json release")
        if metadata.get("plugin_manifest_version") != release.get("manifest_version"):
            fail("docs-metadata.json plugin_manifest_version does not match docs/portal/site.json release")
        if metadata.get("release_url") != release.get("url"):
            fail("docs-metadata.json release_url does not match docs/portal/site.json release")
        release_url = str(release.get("url", ""))
        release_status = str(release.get("status", "")).lower()
        expected_release_prefix = "https://github.com/theislampill/IMPLEMENTAUDIT.md/releases/tag/"
        source_checkout_only = (
            release_url == ""
            and "source checkout only" in release_status
            and "no tag" in release_status
            and "no release" in release_status
            and "no publication" in release_status
            and "no provenance" in release_status
        )
        if source_checkout_only:
            pass
        elif not release_url.startswith(expected_release_prefix):
            fail("docs/portal/site.json release url must point at the public GitHub release tag or declare source-checkout-only no-release status")
        elif str(release.get("milestone", "")) and not release_url.endswith(str(release.get("milestone"))):
            fail("docs/portal/site.json release url must end with the release milestone")
        if metadata.get("audit_ledger_url") != release.get("audit_ledger_url"):
            fail("docs-metadata.json audit_ledger_url does not match docs/portal/site.json release")
        audit_ledger_url = str(release.get("audit_ledger_url", ""))
        expected_ledger_prefix = "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/"
        local_ledger = audit_ledger_url.startswith("docs/audits/") and Path(audit_ledger_url).is_file()
        if not (audit_ledger_url.startswith(expected_ledger_prefix) or local_ledger):
            fail("docs/portal/site.json audit ledger url must point at tracked docs/audits/")
        if not audit_ledger_url.endswith(".md"):
            fail("docs/portal/site.json audit ledger url must point at a markdown ledger")
        if metadata.get("checksum_boundary") != release.get("checksum_boundary"):
            fail("docs-metadata.json checksum_boundary does not match docs/portal/site.json release")
    sources = set(metadata.get("source_files_used", []))
    if "docs/portal_old/onboarding.md" in sources:
        fail("docs-metadata.json should not treat legacy docs/portal_old/onboarding.md as a v2 semantic source")
    # Keep the unrendered DESIGN.md under freshness protection too. It explains
    # the portal contract that the generator and checker are enforcing.
    required_sources = {
        "docs/portal/site.json",
        "docs/portal/DESIGN.md",
        "docs/portal/assets/draft-v2.css",
        "docs/portal/assets/draft-v2.js",
        "scripts/build-docs-portal.py",
    }
    for page in ordered:
        required_sources.add(f"docs/portal/pages/{page['source']}")
        required_sources.update(page.get("sources", []))
    required_sources.update(site.get("semantic_sources", []))
    missing = sorted(required_sources - sources)
    if missing:
        fail(f"docs-metadata.json source_files_used missing: {missing}")
    extra = sorted(sources - required_sources)
    if extra:
        fail(f"docs-metadata.json source_files_used has stale extra entries: {extra}")
    sha256s = metadata.get("source_sha256s", {})
    if not isinstance(sha256s, dict):
        fail("docs-metadata.json source_sha256s must be an object")
        sha256s = {}
    extra_hashes = sorted(set(sha256s) - required_sources)
    if extra_hashes:
        fail(f"docs-metadata.json source_sha256s has stale extra entries: {extra_hashes}")
    for source in required_sources:
        if source not in sha256s:
            fail(f"docs-metadata.json source_sha256s missing: {source}")
            continue
        source_path = repo_root() / source
        if not source_path.is_file():
            fail(f"docs-metadata.json references missing source file: {source}")
            continue
        actual = sha256_file(source_path)
        if sha256s.get(source) != actual:
            fail(f"docs-metadata.json stale hash for {source}")


def validate_site_model(site: dict, ordered: list[dict]) -> None:
    groups = [group.get("group") for group in site.get("nav", [])]
    if groups != REQUIRED_GROUPS:
        fail(f"sidebar group order mismatch: {groups}")
    ids = [page["id"] for page in ordered]
    removed_pages = {
        "default-behavior",
        "shipped-scripts",
        "safety-boundaries",
        "what-it-does-not-do",
        "audit-status",
    }
    unexpected = sorted(removed_pages & set(ids))
    if unexpected:
        fail(f"redundant DRY-violation pages returned to nav: {unexpected}")
    missing = [page_id for page_id in REQUIRED_PAGES if page_id not in ids]
    if missing:
        fail(f"required pages missing from nav: {missing}")
    titles_by_id = {page["id"]: page.get("title", "") for page in ordered}
    if titles_by_id.get("terminology") != "Terminology":
        fail("terminology page title must be Terminology")
    if ids[:5] != ["overview", "plain-english", "what-it-is", "workflow", "success-and-proof"]:
        fail(f"overview group page order mismatch: {ids[:5]}")
    if ids[5:9] != ["quick-start", "installation", "possible-endings", "comparison"]:
        fail(f"first-run page order mismatch: {ids[5:9]}")
    if ids[9:12] != ["for-new-users", "for-agents-and-operators", "for-auditors-and-maintainers"]:
        fail(f"audience page order mismatch: {ids[9:12]}")
    expected_by_group = {
        "Core model": [
            "runtime-model",
            "audit-gate-model",
            "invocation-shapes",
            "usage-examples",
            "planning-and-phases",
            "routing",
            "operating-method",
        ],
        "Evidence": [
            "state-and-artifacts",
            "repo-state-comparison",
            "error-handling",
            "evidence-boundaries",
            "optional-tooling",
            "child-agent-review-loops",
        ],
        "Closure": ["completion-semantics", "continuity-and-sidecars"],
        "Repository": ["repo-layout", "package-contents", "audit-trail"],
        "References": ["terminology", "reference-index"],
    }
    groups_by_name = {group.get("group"): group.get("pages", []) for group in site.get("nav", [])}
    for group_name, expected_pages in expected_by_group.items():
        actual_pages = groups_by_name.get(group_name)
        if actual_pages != expected_pages:
            fail(f"{group_name} page order mismatch: {actual_pages}")
    reference_group = next((group for group in site.get("nav", []) if group.get("group") == "References"), None)
    evidence_group = next((group for group in site.get("nav", []) if group.get("group") == "Evidence"), None)
    repository_group = next((group for group in site.get("nav", []) if group.get("group") == "Repository"), None)
    if not evidence_group:
        fail("Evidence group missing from sidebar")
    else:
        evidence_pages = evidence_group.get("pages", [])
        if "optional-tooling" not in evidence_pages:
            fail("optional-tooling should live in Evidence group")
        if "child-agent-review-loops" not in evidence_pages:
            fail("child-agent-review-loops should live in Evidence group")
    if not repository_group:
        fail("Repository group missing from sidebar")
    if not reference_group:
        fail("References group missing from sidebar")
    else:
        pages = reference_group.get("pages", [])
        if pages != ["terminology", "reference-index"]:
            fail(f"References should contain only Terminology and Index: {pages}")
    if repository_group:
        repo_pages = repository_group.get("pages", [])
        if repo_pages != ["repo-layout", "package-contents", "audit-trail"]:
            fail(f"Repository should contain Repo layout, Package contents, Repo record: {repo_pages}")


def validate_content(out_dir: Path, html_files: list[Path]) -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in html_files)
    combined_lower = combined.lower()
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        bad = next((ch for ch in text if ord(ch) > 127), None)
        if bad:
            fail(f"{path.relative_to(out_dir).as_posix()}: generated HTML contains non-ASCII character U+{ord(bad):04X}")
        for table_match in re.finditer(r"<table\b[\s\S]*?</table>", text, flags=re.IGNORECASE):
            table = table_match.group(0)
            headers = re.findall(r"<th\b[^>]*>", table, flags=re.IGNORECASE)
            if not headers:
                continue
            for row in re.findall(r"<tr\b[^>]*>[\s\S]*?</tr>", table, flags=re.IGNORECASE):
                if re.search(r"<th\b", row, flags=re.IGNORECASE):
                    continue
                for cell in re.findall(r"<td\b[^>]*>", row, flags=re.IGNORECASE):
                    if "data-label=" not in cell:
                        fail(f"{path.relative_to(out_dir).as_posix()}: table cell missing mobile data-label")
        for item_match in re.finditer(r"<li\b[^>]*>(?P<body>[\s\S]*?)</li>", text, flags=re.IGNORECASE):
            plain_item = re.sub(r"<[^>]+>", "", item_match.group("body")).strip()
            if re.search(r"(?:,\s*|(?:^|\s)(?:and|or)\s*)$", plain_item, flags=re.IGNORECASE):
                fail(
                    f"{path.relative_to(out_dir).as_posix()}: list item should not end as a sentence fragment: {plain_item!r}"
                )
    for text, label in FORBIDDEN_VISIBLE_TEXT:
        if text.lower() in combined_lower:
            fail(f"generated portal contains {label}: {text!r}")
    if "file:///" in combined_lower:
        fail("generated portal contains file:/// URL")
    if re.search(r"[A-Za-z]:\\\\", combined) or re.search(r'href="[A-Za-z]:[/\\\\]', combined):
        fail("generated portal contains absolute Windows path")
    if re.search(r"<code>\s*</code>", combined):
        fail("generated portal contains empty inline code element")
    if has_raw_runnable_command_pre(combined):
        fail("generated portal contains raw runnable command pre block; use terminal wrapper")
    if " \u00b7 Artifact:" in combined:
        fail("proof-card metadata still contains inline middle-dot Artifact pattern")
    what_it_is_path = out_dir / "overview" / "what-it-is" / "index.html"
    if what_it_is_path.is_file():
        what_it_is = what_it_is_path.read_text(encoding="utf-8")
        if 'id="why-safer"' in what_it_is:
            fail("What it is page should not duplicate the Comparison page's safer-than-normal-agent section")
    audit_trail_path = out_dir / "reference" / "repo-record" / "index.html"
    if audit_trail_path.is_file():
        audit_trail = audit_trail_path.read_text(encoding="utf-8")
        if 'id="current-status"' in audit_trail:
            fail("Repo record page should not render the stray Current status placeholder section")
    for concept in REQUIRED_CONCEPTS:
        if concept.lower() not in combined_lower:
            fail(f"required source-backed concept missing from generated portal: {concept}")
    for pattern in REQUIRED_CONCEPT_PATTERNS:
        if not pattern.search(combined):
            fail(f"required source-backed concept pattern missing from generated portal: {pattern.pattern}")
    success_path = out_dir / "overview" / "proof" / "index.html"
    if success_path.is_file():
        success = success_path.read_text(encoding="utf-8")
        artifact_lines = re.findall(r'<p class="artifact-line">([\s\S]*?)</p>', success)
        if len(artifact_lines) < 4:
            fail("success proof page should contain four artifact-line metadata blocks")
        for i, line in enumerate(artifact_lines, start=1):
            if line.count("<span") < 4:
                fail(f"artifact-line {i} is not split into structural spans")
            if 'class="artifact-value"' not in line:
                fail(f"artifact-line {i} must put metadata values on structural lines")

    css = out_dir / "assets" / "draft-v2.css"
    if not css.is_file():
        fail("draft-v2.css missing from generated assets")
    else:
        css_text = css.read_text(encoding="utf-8")
        bad = next((ch for ch in css_text if ord(ch) > 127), None)
        if bad:
            fail(f"draft-v2.css contains non-ASCII character U+{ord(bad):04X}")
        if ".mobile-toc" not in css_text:
            fail("draft-v2.css missing mobile-toc styles")
        if ".toc a.is-active" not in css_text:
            fail("draft-v2.css missing active right-TOC style")
        if ".mobile-toc a.is-active" not in css_text:
            fail("draft-v2.css missing active mobile-TOC style")
        for class_name in (
            ".lead-list",
            ".hero-lede-list",
            ".artifact-card-grid",
            ".artifact-card",
            ".comparison-cards",
            ".marker-cards",
            ".gate-cards",
            ".step-list",
        ):
            if class_name not in css_text:
                fail(f"draft-v2.css missing generated page class style: {class_name}")
        if ".kdetails" in css_text:
            fail("draft-v2.css still contains collapsed runtime drawer styles")
        if "overflow-x: hidden" in css_text:
            fail("draft-v2.css must not hide horizontal overflow in code/proof blocks")
        if "td::before" not in css_text or "data-label" not in css_text:
            fail("draft-v2.css missing mobile table data-label styles")
        if ".nav-title::after" in css_text:
            fail("sidebar group chevrons must not appear on inert headings")
        if ".page-proof-strip" not in css_text:
            fail("draft-v2.css missing page proof strip styles")
        if ".top-tab.active" not in css_text:
            fail("draft-v2.css missing active top navigation style")
        if "calc((100vw - 1180px) / 2)" in css_text:
            fail("draft-v2.css still aligns chrome to the deprecated 1180px shell")
        if "padding: 14px max(20px, calc((100vw - 1680px) / 2));" not in css_text:
            fail("draft-v2.css topbar must align to the 1680px docs frame")
        if ".overview-frame { width: min(1480px" in css_text:
            fail("draft-v2.css overview frame still uses the deprecated narrow shell")
        if ".overview-frame { width: min(1680px, calc(100vw - 40px));" not in css_text:
            fail("draft-v2.css overview frame must align to the docs frame")
        if "footer .shell" not in css_text or "width: min(1680px, calc(100vw - 40px));" not in css_text:
            fail("draft-v2.css footer shell must align to the docs frame")
        if "justify-content: flex-end" in css_text:
            fail("draft-v2.css footer proof strip should not push proof metadata to the far right")
        if ".page-proof-strip" not in css_text or "width: 100%" not in css_text:
            fail("draft-v2.css footer proof strip must span the footer metadata width")
        if ".page-proof-strip div:nth-child(2)" not in css_text or ".page-proof-strip div:nth-child(3)" in css_text:
            fail("draft-v2.css footer proof strip must align Page source left and Release centered without a visible Boundary cell")
        if ".release-proof-links a" not in css_text:
            fail("draft-v2.css missing release proof link wrapping guard")
        if "table.stage-table col:first-child.stage-purpose { width: 160px; }" not in css_text:
            fail("draft-v2.css optional source table must reserve enough first-column width")
        if "table.source-current-table col.source-surface { width: 240px; }" not in css_text:
            fail("draft-v2.css source-current table must reserve enough surface-column width")
        if "--page-nav-card-max" not in css_text or "grid-template-columns: repeat(2, minmax(0, var(--page-nav-card-max)))" not in css_text:
            fail("draft-v2.css page navigation cards must use a content-based max width")
        if ".sr-only" not in css_text or ".top-actions .gh svg" not in css_text:
            fail("draft-v2.css missing icon-only GitHub topbar support")
        for token in (
            ".nav-docs-head",
            ".nav-window-dots",
            ".nav-caret",
            ".nav-group[open] .nav-caret",
        ):
            if token not in css_text:
                fail(f"draft-v2.css missing file-tree sidebar treatment: {token}")
        if ".nav-folder-icon" in css_text or ".nav-file-icon" in css_text or ".nav-file-dot" in css_text:
            fail("draft-v2.css sidebar should not keep sheet or folder icon styles")
        for token in (
            ".top-tabs",
            "--active-index",
            "--tab-count",
            ".top-tab-indicator",
            ".top-tab[aria-current=\"location\"]",
            "transition: left 220ms ease, width 220ms ease",
        ):
            if token not in css_text:
                fail(f"draft-v2.css missing top navigation tabs treatment: {token}")
        hero_actions_match = re.search(r"\.hero-actions\s*\{(?P<body>[^}]*)\}", css_text)
        if not hero_actions_match or "justify-content: space-between" not in hero_actions_match.group("body"):
            fail("draft-v2.css hero actions must separate the primary and install actions")
        if ".proof-card-grid" not in css_text or ".artifact-value" not in css_text:
            fail("draft-v2.css missing segmented proof-card metadata styles")
        if ".proto-grid.proof-card-grid" not in css_text or "gap: 0" not in css_text:
            fail("draft-v2.css proof cards must be a segmented group, not separated cards")
        artifact_label_match = re.search(r"\.artifact-line b\s*\{(?P<body>[^}]*)\}", css_text)
        if not artifact_label_match or "display: block" not in artifact_label_match.group("body"):
            fail("draft-v2.css artifact metadata labels must be block-level to prevent label/value wrapping")
        if ".page-prev" not in css_text or ".page-next" not in css_text:
            fail("draft-v2.css missing explicit previous/next page navigation styles")
        page_next_match = re.search(r"\.page-next\s*\{(?P<body>[^}]*)\}", css_text)
        if not page_next_match:
            fail("draft-v2.css missing .page-next declaration block")
        else:
            page_next_body = page_next_match.group("body")
            for declaration in ("grid-column: 2", "align-items: flex-end", "text-align: right"):
                if declaration not in page_next_body:
                    fail(f"draft-v2.css .page-next block missing {declaration}")
        if ".page-nav a:only-child" not in css_text:
            fail("draft-v2.css missing single-link page-nav span rule")
        if "--cyan-soft" not in css_text:
            fail("draft-v2.css missing cyan-soft color token")
        if ".term-window pre code { display: inline; padding: 0; font-size: inherit; background: transparent; color: inherit; }" not in css_text:
            fail("draft-v2.css missing terminal inline-code reset")
        if ".example-console" not in css_text or ".shape-command-grid" not in css_text:
            fail("draft-v2.css missing terminal wrapper styles for examples")
        if ".comparison-winner" not in css_text or "audit-grade" not in css_text:
            fail("draft-v2.css missing distinct IMPLEMENTAUDIT comparison-card styling")
        for token in (
            "--mouse-x",
            "--mouse-y",
            "--spotlight-color",
            "circle 25px",
            "rgba(251,191,36,0.08)",
            "@keyframes shiny-title",
            "transition: background-position 760ms ease",
            "120% 120%",
            "animation: none",
            "prefers-reduced-motion: reduce",
        ):
            if token not in css_text:
                fail(f"draft-v2.css missing comparison winner spotlight/shiny guard: {token}")
        for token in (
            ".magnet-link",
            "--magnet-x",
            "--magnet-y",
            ".magnet-link.is-magnet-active",
            "(pointer: coarse)",
        ):
            if token not in css_text:
                fail(f"draft-v2.css missing magnetic-link interaction guard: {token}")
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
            if token not in css_text:
                fail(f"draft-v2.css missing reusable glass card treatment: {token}")
        for token in (
            "card-label-shine",
            ".result-grid div::before",
            ".loop-stack > div::before",
            ".index-card::before",
            ".comparison-cards section:not(.comparison-winner)::before",
        ):
            if token in css_text:
                fail(f"draft-v2.css ordinary cards must not use reusable shimmer treatment: {token}")
        if ".shape-command p { min-height: 3.2em;" not in css_text:
            fail("draft-v2.css invocation-shape cards must align terminal wrappers")
        if "table.stage-table col.stage-num { width: 74px; }" not in css_text:
            fail("draft-v2.css stage table first column must fit the Stage header")
        if "table.layer-table col.layer-num { width: 78px; }" not in css_text:
            fail("draft-v2.css layer table first column must fit the Layer header")
        if "table.priority-table col.priority-num { width: 96px; }" not in css_text:
            fail("draft-v2.css priority table first column must fit the Priority header")
        if ".hero-card > p" not in css_text or "max-width: 100%" not in css_text:
            fail("draft-v2.css missing full-width article prose rule")
        if "h2[id]" not in css_text or "h3[id]" not in css_text:
            fail("draft-v2.css missing scroll margin for article heading anchors")
        if ".page-context" in css_text:
            fail("draft-v2.css should not keep redundant page context styles")

    js = out_dir / "assets" / "draft-v2.js"
    if not js.is_file():
        fail("draft-v2.js missing from generated assets")
    else:
        js_text = js.read_text(encoding="utf-8")
        if '.toc a[href^="#"], .mobile-toc a[href^="#"]' not in js_text:
            fail("draft-v2.js active-section script must cover desktop and mobile TOC links")
        if "addEventListener('click'" not in js_text:
            fail("draft-v2.js active-section script must update TOC state on link click")
        if "scrollIntoView" in js_text:
            fail("draft-v2.js must not use scrollIntoView for sidebar active-link centering")
        if "sideNav.scrollTop" not in js_text:
            fail("draft-v2.js missing sidebar-local active-link centering")
        for token in (".card-spotlight", "--mouse-x", "--mouse-y"):
            if token not in js_text:
                fail(f"draft-v2.js missing comparison spotlight pointer tracking: {token}")
        for token in (
            ".magnet-link",
            "--magnet-x",
            "--magnet-y",
            "is-magnet-active",
            "matchMedia('(prefers-reduced-motion: reduce)')",
            "matchMedia('(pointer: coarse)')",
        ):
            if token not in js_text:
                fail(f"draft-v2.js missing magnetic-link pointer tracking: {token}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <output-dir>\n")
        sys.exit(1)

    out_dir = Path(sys.argv[1]).resolve()
    if not out_dir.is_dir():
        fail(f"output directory not found: {out_dir}")
        sys.exit(1)

    site, ordered, pages_by_id = load_site(repo_root())
    validate_site_model(site, ordered)
    validate_metadata(out_dir, site, ordered)
    html_files = validate_page_shell(out_dir, site, ordered, pages_by_id)
    validate_links(out_dir, html_files)
    validate_content(out_dir, html_files)

    if _failures:
        sys.stderr.write(f"check-docs-portal: FAIL ({_failures} check(s) failed)\n")
        sys.exit(1)

    sys.stdout.write(
        f"check-docs-portal: ok ({len(ordered)} pages, {len(html_files)} html files, links resolved)\n"
    )


if __name__ == "__main__":
    main()
