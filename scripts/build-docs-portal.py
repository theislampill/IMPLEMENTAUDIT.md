#!/usr/bin/env python3
'''
build-docs-portal.py - IMPLEMENTAUDIT docs portal generator.

Usage:
    python scripts/build-docs-portal.py [--out <output-dir>]

Defaults output to dist/docs-portal/ relative to the repo root.
Reads source files from docs/portal/. Produces a multipage docs portal plus
assets and docs-metadata.json. No external dependencies; Python stdlib only.

Authorization: generate and build only. No deploy, publish, tag, or release.
Pages deployment requires the GitHub Actions workflow (pages.yml) to succeed.
'''

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_URL = "https://github.com/theislampill/IMPLEMENTAUDIT.md"
CHANGELOG_URL = "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/CHANGELOG.md"
DEFAULT_RELEASE = {
    "milestone": "unknown",
    "manifest_version": "unknown",
    "url": REPO_URL,
    "audit_ledger_url": f"{REPO_URL}/tree/main/docs/audits",
    "checksum_boundary": "checksum manifest verifies artifact integrity; release provenance still needs a separate authorized gate",
}

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

RESERVED_OUTPUT_ROOTS = {"assets"}


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_no_duplicates(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except ValueError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc


def normalize_page_path(page_id: str, raw_path: object) -> str:
    if not isinstance(raw_path, str):
        raise SystemExit(f"page {page_id}: path must be a string")
    if raw_path == "":
        return ""
    if "\\" in raw_path:
        raise SystemExit(f"page {page_id}: path must use forward slashes: {raw_path!r}")
    if raw_path.startswith("/") or re.match(r"^[A-Za-z]:", raw_path) or "://" in raw_path:
        raise SystemExit(f"page {page_id}: path must be repo-relative: {raw_path!r}")
    if "//" in raw_path:
        raise SystemExit(f"page {page_id}: path must not contain empty segments: {raw_path!r}")
    if not raw_path.endswith("/"):
        raise SystemExit(f"page {page_id}: path must end with /: {raw_path!r}")
    parts = [part for part in raw_path.strip("/").split("/") if part]
    if not parts:
        raise SystemExit(f"page {page_id}: only overview may use empty path")
    if parts[0].lower() in RESERVED_OUTPUT_ROOTS:
        raise SystemExit(f"page {page_id}: path cannot live under reserved root {parts[0]!r}")
    for part in parts:
        if part in {".", ".."}:
            raise SystemExit(f"page {page_id}: path must not contain {part!r}: {raw_path!r}")
        if posixpath.splitext(part)[1]:
            raise SystemExit(f"page {page_id}: path segments must not have extensions: {raw_path!r}")
    return "/".join(parts) + "/"


def validate_page_source(page_id: str, raw_source: object, pages_dir: Path) -> str:
    if not isinstance(raw_source, str) or not raw_source:
        raise SystemExit(f"page {page_id}: source must be a non-empty string")
    if "/" in raw_source or "\\" in raw_source or raw_source in {".", ".."} or ".." in raw_source:
        raise SystemExit(f"page {page_id}: source must be a file name under docs/portal/pages: {raw_source!r}")
    if Path(raw_source).suffix != ".html":
        raise SystemExit(f"page {page_id}: source must be .html: {raw_source!r}")
    if not (pages_dir / raw_source).is_file():
        raise SystemExit(f"page {page_id}: source file missing: {raw_source!r}")
    return raw_source


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def git_worktree_state(root: Path) -> str:
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"
    return "dirty" if status else "clean"


def plugin_version(root: Path) -> str:
    try:
        data = load_json_no_duplicates(root / ".claude-plugin" / "plugin.json")
        return str(data.get("version", "unknown"))
    except Exception:
        return "unknown"


def project_milestone(version: str) -> str:
    if version == "unknown":
        return "unknown"
    parts = version.split(".")
    if len(parts) == 3:
        return f"v{parts[0]}.{parts[1]}.{parts[2]}.0"
    return f"v{version}"


def load_site(source_dir: Path) -> tuple[list[dict], dict]:
    site_path = source_dir / "site.json"
    site = load_json_no_duplicates(site_path)
    pages = site["pages"]
    pages_dir = source_dir / "pages"
    output_routes = {}
    for page_id, page in pages.items():
        if not isinstance(page, dict):
            raise SystemExit(f"page {page_id}: page entry must be an object")
        if not isinstance(page.get("title"), str) or not page.get("title"):
            raise SystemExit(f"page {page_id}: title must be a non-empty string")
        page["path"] = normalize_page_path(page_id, page.get("path", ""))
        page["source"] = validate_page_source(page_id, page.get("source"), pages_dir)
        route_key = (page["path"] or ".").lower()
        if route_key in output_routes:
            raise SystemExit(f"pages {output_routes[route_key]} and {page_id} generate the same output route")
        output_routes[route_key] = page_id
    referenced_sources = {page["source"] for page in pages.values()}
    orphan_sources = sorted(path.name for path in pages_dir.glob("*.html") if path.name not in referenced_sources)
    if orphan_sources:
        raise SystemExit(f"docs portal page source(s) are not referenced by site.json: {orphan_sources}")
    ordered = []
    seen = set()
    for group in site["nav"]:
        for page_id in group["pages"]:
            if page_id not in pages:
                raise SystemExit(f"nav references missing page: {page_id}")
            if page_id in seen:
                raise SystemExit(f"page appears twice in nav: {page_id}")
            item = dict(pages[page_id])
            item["id"] = page_id
            item["group"] = group["group"]
            ordered.append(item)
            seen.add(page_id)
    missing = set(pages) - seen
    if missing:
        raise SystemExit(f"pages missing from nav: {sorted(missing)}")
    return ordered, site


def page_output_path(out_dir: Path, page: dict) -> Path:
    rel = page["path"]
    if rel == "":
        return out_dir / "index.html"
    return out_dir / rel / "index.html"


def page_dir(page: dict) -> str:
    rel = page["path"].strip("/")
    return rel if rel else "."


def rel_href(current: dict, target: dict | str) -> str:
    if isinstance(target, str):
        target_path = target.strip("/") or "."
    else:
        target_path = target["path"].strip("/") or "."
    start = page_dir(current)
    rel = posixpath.relpath(target_path, start)
    if rel == ".":
        return "./"
    if not rel.endswith("/") and not posixpath.splitext(rel)[1]:
        rel += "/"
    return rel


def asset_versions(source_dir: Path) -> dict[str, str]:
    asset_dir = source_dir / "assets"
    return {
        path.name: sha256_file(path)[:12]
        for path in sorted(asset_dir.iterdir())
        if path.is_file()
    }


def asset_href(current: dict, asset: str, versions: dict[str, str]) -> str:
    href = rel_href(current, f"assets/{asset}")
    version = versions.get(asset)
    if version:
        href = f"{href}?v={version}"
    return href


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def source_url(rel_path: str) -> str:
    return f"{REPO_URL}/blob/main/{rel_path}"


def release_info(site: dict, root: Path) -> dict:
    version = plugin_version(root)
    release = dict(DEFAULT_RELEASE)
    release.update(site.get("release", {}))
    if release.get("manifest_version") in (None, "unknown"):
        release["manifest_version"] = version
    if release.get("milestone") in (None, "unknown"):
        release["milestone"] = project_milestone(str(release["manifest_version"]))
    return release


def h2_entries(content: str) -> list[tuple[str, str]]:
    # Page-local TOCs should survive harmless attribute ordering changes such as
    # `<h2 class="..." id="...">`. The source pages are intentionally plain
    # HTML, so this bounded extraction is enough and avoids a dependency.
    entries = []
    for match in re.finditer(r"<h2\b([^>]*)>([\s\S]*?)</h2>", content):
        attrs = match.group(1)
        id_match = re.search(r'\bid="([^"]+)"', attrs)
        if id_match:
            entries.append((id_match.group(1), strip_tags(match.group(2))))
    return entries


def section_entries(content: str) -> list[tuple[str, str]]:
    labels = {"top": "Splash", "paths": "Overview pages"}
    entries = []
    for match in re.finditer(r'<section[^>]+id="([^"]+)"', content):
        sid = match.group(1)
        entries.append((sid, labels.get(sid, sid.replace("-", " ").title())))
    return entries


def top_nav_state(current: dict, target_id: str) -> str | None:
    if current["id"] == target_id:
        return "page"
    if TOP_NAV_BUCKET_TARGETS.get(current["id"]) == target_id:
        return "location"
    return None


GITHUB_MARK = (
    '<svg aria-hidden="true" viewBox="0 0 16 16" focusable="false">'
    '<path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 '
    '7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94'
    '-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 '
    '1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 '
    '0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 '
    '2.2.82A7.65 7.65 0 0 1 8 4.58c.68 0 1.36.09 2 .24 1.53-1.04 '
    '2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 '
    '0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 '
    '1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/>'
    '</svg>'
)


def top_nav(current: dict, pages_by_id: dict) -> str:
    links = []
    active_index = 0
    for idx, (label, page_id) in enumerate(TOP_NAV):
        target = pages_by_id[page_id]
        state = top_nav_state(current, page_id)
        attrs = f' aria-current="{state}"' if state else ""
        if state == "page":
            attrs += ' class="top-tab active"'
            active_index = idx
        else:
            attrs += ' class="top-tab"'
            if state == "location":
                active_index = idx
        links.append(f'<a{attrs} href="{html.escape(rel_href(current, target))}">{html.escape(label)}</a>')
    nav_tabs = (
        f'<div class="top-tabs" style="--active-index: {active_index}; --tab-count: {len(TOP_NAV)}">'
        f'{"".join(links)}<span class="top-tab-indicator" aria-hidden="true"></span></div>'
    )
    links = [nav_tabs]
    links.append(
        f'<a class="gh" href="{REPO_URL}" aria-label="GitHub repository">'
        f'{GITHUB_MARK}<span class="sr-only">GitHub</span></a>'
    )
    return "".join(links)


def side_nav(current: dict, site: dict, pages_by_id: dict) -> str:
    groups = []
    for group in site["nav"]:
        links = []
        for page_id in group["pages"]:
            target = pages_by_id[page_id]
            attrs = ' aria-current="page" class="nav-file active"' if page_id == current["id"] else ' class="nav-file"'
            links.append(
                f'<a{attrs} href="{html.escape(rel_href(current, target))}">'
                f'<span class="nav-file-label">{html.escape(target["title"])}</span></a>'
            )
        groups.append(
            f'<details class="nav-group" open><summary class="nav-title">'
            f'<span class="nav-caret" aria-hidden="true"></span>'
            f'<span>{html.escape(group["group"])}</span></summary>'
            f'<div class="nav-list">{"".join(links)}</div></details>'
        )
    return (
        '<div class="nav-docs-head" aria-hidden="true">'
        '<span class="nav-window-dots"><i></i><i></i><i></i></span><span>Docs</span></div>\n    '
        + "\n    ".join(groups)
    )


def toc(entries: list[tuple[str, str]]) -> str:
    links = "\n".join(f'    <a href="#{html.escape(anchor)}">{html.escape(label)}</a>' for anchor, label in entries)
    return f'''  <aside class="toc" aria-label="On this page">
    <h2>On this page</h2>
{links}
  </aside>'''


def mobile_toc(entries: list[tuple[str, str]]) -> str:
    if not entries:
        return ""
    links = "".join(
        f'<li><a href="#{html.escape(anchor)}">{html.escape(label)}</a></li>'
        for anchor, label in entries
    )
    return f'<details class="mobile-toc"><summary>On this page</summary><ol>{links}</ol></details>'


def page_nav(current: dict, ordered: list[dict], overview: bool = False) -> str:
    idx = [p["id"] for p in ordered].index(current["id"])
    prev_page = ordered[idx - 1] if idx > 0 else None
    next_page = ordered[idx + 1] if idx + 1 < len(ordered) else None
    longest_title = max((len(p["title"]) for p in ordered), default=24)
    nav_card_ch = min(max((longest_title * 12 + 9) // 10 + 6, 28), 44)
    prev_html = (
        f'<a class="page-prev magnet-link" href="{html.escape(rel_href(current, prev_page))}"><small>Previous</small><span>{html.escape(prev_page["title"])}</span></a>'
        if prev_page else ''
    )
    next_html = (
        f'<a class="page-next magnet-link" href="{html.escape(rel_href(current, next_page))}"><small>Next</small><span>{html.escape(next_page["title"])}</span></a>'
        if next_page else ''
    )
    nav = f'<nav class="page-nav" aria-label="Page navigation" style="--page-nav-card-max: {nav_card_ch}ch;">{prev_html}{next_html}</nav>'
    if overview:
        return f'<section class="shell overview-page-nav" aria-label="Page navigation">{nav}</section>'
    return nav


def page_proof_strip(current: dict, release: dict) -> str:
    rel_source = f'docs/portal/pages/{current["source"]}'
    milestone = str(release.get("milestone", "unknown"))
    release_url = str(release.get("url", REPO_URL))
    return (
        '<dl class="page-proof-strip" aria-label="Page source and release links">'
        f'<div><dt>Page source</dt><dd><code>{html.escape(rel_source)}</code></dd></div>'
        f'<div><dt>Release</dt><dd class="release-proof-links">'
        f'<span class="release-version"><a href="{html.escape(release_url)}">{html.escape(milestone)}</a></span>'
        f'<span class="release-secondary"><a href="{html.escape(REPO_URL)}">Source</a> - <a href="{html.escape(CHANGELOG_URL)}">Changelog</a></span>'
        f'</dd></div>'
        '</dl>'
    )


def add_table_data_labels(content: str) -> str:
    # Preserve real tables for desktop readers, but annotate cells with their
    # header text so narrow mobile layouts can stack rows without losing
    # meaning. This is a generator concern because source pages should stay
    # readable and avoid hand-maintained duplicate labels.
    def label_table(match: re.Match) -> str:
        table = match.group(0)
        headers = [strip_tags(item) for item in re.findall(r"<th\b[^>]*>([\s\S]*?)</th>", table)]
        if not headers:
            return table

        def label_row(row_match: re.Match) -> str:
            row = row_match.group(0)
            if re.search(r"<th\b", row):
                return row
            index = 0

            def label_cell(cell_match: re.Match) -> str:
                nonlocal index
                tag = cell_match.group(0)
                if "data-label=" in tag:
                    index += 1
                    return tag
                label = headers[min(index, len(headers) - 1)]
                index += 1
                return tag[:-1] + f' data-label="{html.escape(label, quote=True)}">'

            return re.sub(r"<td\b[^>]*>", label_cell, row)

        return re.sub(r"<tr\b[^>]*>[\s\S]*?</tr>", label_row, table)

    return re.sub(r"<table\b[\s\S]*?</table>", label_table, content)


def normalize_source_content(content: str) -> str:
    content = re.sub(
        r'(<section\b(?=[^>]*\bclass="[^"]*\bcomparison-winner\b[^"]*")[^>]*)\s+tabindex=["\']0["\']',
        r"\1",
        content,
    )
    return content


def footer(release: dict, current: dict) -> str:
    return f'''<footer><div class="shell foot-inner">
  <div><b>IMPLEMENTAUDIT</b> &mdash; plan deeply, audit everything, hand off honestly.</div>
</div><div class="shell foot-proof">
  {page_proof_strip(current, release)}
</div></footer>'''


def render_page(
    current: dict,
    ordered: list[dict],
    site: dict,
    pages_by_id: dict,
    source_dir: Path,
    release: dict,
    versions: dict[str, str],
) -> str:
    content_path = source_dir / "pages" / current["source"]
    content = content_path.read_text(encoding="utf-8")
    content = normalize_source_content(content)
    content = add_table_data_labels(content)
    entries = section_entries(content) if current.get("kind") == "overview" else h2_entries(content)
    title = "IMPLEMENTAUDIT - auditable agent edits" if current["id"] == "overview" else f'{current["title"]} - IMPLEMENTAUDIT docs'
    frame_class = "docs-frame overview-frame" if current.get("kind") == "overview" else "docs-frame"
    if current.get("kind") == "overview":
        main = f'<main id="main" class="overview-main">\n{mobile_toc(entries)}\n{content}\n{page_nav(current, ordered, overview=True)}\n</main>'
    else:
        main = f'<main id="main" class="docs-main">\n  <article class="article">\n{mobile_toc(entries)}\n{content}\n{page_nav(current, ordered)}\n  </article>\n</main>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{html.escape(asset_href(current, "draft-v2.css", versions))}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="docs-topbar">
  <a class="docs-brand" href="{html.escape(rel_href(current, pages_by_id["overview"]))}">IMPLEMENTAUDIT</a>
  <nav class="top-actions" aria-label="Main">
    {top_nav(current, pages_by_id)}
  </nav>
</header>
<div class="{frame_class}">
  <button class="docs-menu-toggle" type="button" aria-expanded="false" aria-controls="docs-navigation">Docs menu</button>
  <aside id="docs-navigation" class="side-nav" aria-label="Docs navigation">
    {side_nav(current, site, pages_by_id)}
  </aside>
{main}
{toc(entries)}
</div>
{footer(release, current)}
<script src="{html.escape(asset_href(current, "draft-v2.js", versions))}"></script>
</body>
</html>
'''


def assert_safe_out_dir(root: Path, source_dir: Path, out_dir: Path) -> None:
    root = root.resolve()
    source_dir = source_dir.resolve()
    out_dir = out_dir.resolve()
    dist_dir = (root / "dist").resolve()

    if out_dir == root or out_dir in root.parents:
        raise SystemExit(f"refusing to delete repo root or ancestor as docs output: {out_dir}")
    if out_dir == source_dir or source_dir in out_dir.parents or out_dir in source_dir.parents:
        raise SystemExit(f"refusing to use docs portal source tree as output: {out_dir}")
    if root in out_dir.parents and not (out_dir == dist_dir or dist_dir in out_dir.parents):
        raise SystemExit(f"refusing to delete a non-dist path inside the repo: {out_dir}")
    if out_dir.exists() and any(out_dir.iterdir()):
        marker = out_dir / "docs-metadata.json"
        if not marker.exists() and not (out_dir == dist_dir or dist_dir in out_dir.parents):
            raise SystemExit(f"refusing to overwrite non-portal output directory: {out_dir}")


def collect_source_files(root: Path, source_dir: Path, site: dict, ordered: list[dict]) -> list[Path]:
    # The metadata manifest is the portal's stale-output tripwire. Include the
    # design contract as source even though it is not rendered, because changes
    # there affect the generator/checker obligations future maintainers rely on.
    source_files = [source_dir / "site.json", root / "scripts" / "build-docs-portal.py"]
    source_files.extend(sorted(source_dir.glob("*.md")))
    source_files.extend(sorted((source_dir / "pages").glob("*.html")))
    source_files.extend(sorted((source_dir / "assets").glob("*")))

    rel_sources = list(site.get("semantic_sources", []))
    for page in ordered:
        rel_sources.extend(page.get("sources", []))

    for rel in rel_sources:
        source_files.append(root / rel)

    unique = []
    seen = set()
    missing = []
    for path in source_files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not path.exists():
            missing.append(str(path.relative_to(root)).replace(os.sep, "/"))
            continue
        unique.append(path)
    if missing:
        raise SystemExit(f"docs portal source file(s) missing: {missing}")
    return unique


def build_portal(out_dir: Path) -> None:
    root = repo_root()
    source_dir = root / "docs" / "portal"
    ordered, site = load_site(source_dir)
    pages_by_id = {p["id"]: p for p in ordered}
    release = release_info(site, root)
    versions = asset_versions(source_dir)
    manifest_version = plugin_version(root)
    if release.get("manifest_version") != manifest_version:
        raise SystemExit(
            f"site release manifest_version {release.get('manifest_version')!r} "
            f"does not match .claude-plugin/plugin.json {manifest_version!r}"
        )

    assert_safe_out_dir(root, source_dir, out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    asset_out = out_dir / "assets"
    asset_out.mkdir(parents=True, exist_ok=True)
    for asset in (source_dir / "assets").iterdir():
        if asset.is_file():
            shutil.copy2(asset, asset_out / asset.name)

    for page in ordered:
        path = page_output_path(out_dir, page)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_page(page, ordered, site, pages_by_id, source_dir, release, versions), encoding="utf-8")

    source_files = collect_source_files(root, source_dir, site, ordered)
    version = plugin_version(root)
    # Store every input and hash that can affect the generated portal. The
    # checker compares this back to the current tree so local dist output cannot
    # masquerade as fresh after source, asset, or design-contract changes.
    worktree_state = git_worktree_state(root)
    metadata = {
        "repo": "theislampill/IMPLEMENTAUDIT.md",
        "head_commit_sha": git_commit(root),
        "worktree_state": worktree_state,
        "worktree_dirty": worktree_state == "dirty",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_milestone": project_milestone(version),
        "plugin_manifest_version": version,
        "release_url": release.get("url", REPO_URL),
        "audit_ledger_url": release.get("audit_ledger_url", DEFAULT_RELEASE["audit_ledger_url"]),
        "checksum_boundary": release.get("checksum_boundary", DEFAULT_RELEASE["checksum_boundary"]),
        "portal_version": "v2-multipage",
        "page_count": len(ordered),
        "source_files_used": [str(p.relative_to(root)).replace(os.sep, "/") for p in source_files if p.exists()],
        "source_sha256s": {str(p.relative_to(root)).replace(os.sep, "/"): sha256_file(p) for p in source_files if p.exists()},
        "rough_draft_used": False,
    }
    (out_dir / "docs-metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(f"build-docs-portal: wrote {out_dir}\n")
    sys.stdout.write(
        "build-docs-portal: "
        f"{len(ordered)} pages, head={metadata['head_commit_sha']}, "
        f"worktree={metadata['worktree_state']}, "
        f"milestone={metadata['project_milestone']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build IMPLEMENTAUDIT docs portal")
    parser.add_argument("--out", default=None, help="Output directory (default: dist/docs-portal)")
    args = parser.parse_args()
    root = repo_root()
    out_dir = Path(args.out) if args.out else root / "dist" / "docs-portal"
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    build_portal(out_dir)


if __name__ == "__main__":
    main()
