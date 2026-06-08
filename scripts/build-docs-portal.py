#!/usr/bin/env python3
"""
build-docs-portal.py — IMPLEMENTAUDIT docs portal generator.

Usage:
    python scripts/build-docs-portal.py [--out <output-dir>]

Defaults output to dist/docs-portal/ relative to the repo root.
Reads source files from the repo. Produces index.html + docs-metadata.json.
No external dependencies; Python stdlib only.

Authorization: generate and build only. No deploy, publish, tag, or release.
Pages deployment requires the GitHub Actions workflow (pages.yml) to succeed.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    script = Path(__file__).resolve()
    return script.parent.parent


def git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root()),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def sha256_of(path: Path) -> str:
    if not path.is_file():
        return "absent"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def plugin_version(root: Path) -> str:
    plugin_json = root / ".claude-plugin" / "plugin.json"
    if not plugin_json.is_file():
        plugin_json = root / "plugin.json"
    if plugin_json.is_file():
        try:
            data = json.loads(plugin_json.read_text(encoding="utf-8"))
            return data.get("version", "unknown")
        except Exception:
            pass
    return "unknown"


def project_milestone(root: Path) -> str:
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        return "unknown"
    text = changelog.read_text(encoding="utf-8")
    m = re.search(r"##\s+\[?(v[\d.]+)\]?", text)
    if m:
        return m.group(1)
    return "unknown"


def markdown_to_html_sections(md_text: str) -> list[dict]:
    """
    Parse Markdown into sections. Each ## heading becomes a section with:
    {id, title, content_html}
    Content is rendered as basic HTML (paragraphs, lists, code, tables).
    Returns list of section dicts.
    """
    sections = []
    current_title = None
    current_lines: list[str] = []

    def flush():
        if current_title is not None:
            sections.append({
                "id": title_to_id(current_title),
                "title": current_title,
                "content_html": lines_to_html(current_lines),
            })

    for line in md_text.splitlines():
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_lines = []
        elif line.startswith("# "):
            # Top-level heading is metadata; skip
            pass
        else:
            current_lines.append(line)

    flush()
    return sections


def title_to_id(title: str) -> str:
    """Convert a section title to an HTML id anchor."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def lines_to_html(lines: list[str]) -> str:
    """Minimally render Markdown lines to HTML."""
    html_parts = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Table: detect | ... | pattern
        if "|" in line and i + 1 < len(lines) and re.match(r"\s*\|[-| :]+\|\s*$", lines[i + 1]):
            rows = []
            # header row
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2  # skip separator
            rows.append("<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>")
            body_rows = []
            while i < len(lines) and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                body_rows.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in cells) + "</tr>")
                i += 1
            rows.append("<tbody>" + "".join(body_rows) + "</tbody>")
            html_parts.append('<div class="table-wrap"><table>' + "".join(rows) + "</table></div>")
            continue

        # Fenced code block
        if line.strip().startswith("```") or line.strip().startswith("    "):
            code_lines = []
            if line.strip().startswith("```"):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing ```
            else:
                # 4-space indent
                while i < len(lines) and (lines[i].startswith("    ") or lines[i] == ""):
                    code_lines.append(lines[i][4:] if lines[i].startswith("    ") else "")
                    i += 1
            code_content = "\n".join(code_lines)
            html_parts.append(f"<pre><code>{escape_html(code_content)}</code></pre>")
            continue

        # Unordered list
        if line.startswith("- ") or line.startswith("* "):
            list_items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                item = lines[i][2:].strip()
                list_items.append(f"<li>{inline_md(item)}</li>")
                i += 1
            html_parts.append("<ul>" + "".join(list_items) + "</ul>")
            continue

        # Numbered list
        if re.match(r"^\d+\. ", line):
            list_items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                item = re.sub(r"^\d+\. ", "", lines[i]).strip()
                list_items.append(f"<li>{inline_md(item)}</li>")
                i += 1
            html_parts.append("<ol>" + "".join(list_items) + "</ol>")
            continue

        # H3 heading
        if line.startswith("### "):
            html_parts.append(f"<h3>{inline_md(line[4:].strip())}</h3>")
            i += 1
            continue

        # H4 heading
        if line.startswith("#### "):
            html_parts.append(f"<h4>{inline_md(line[5:].strip())}</h4>")
            i += 1
            continue

        # Blank line
        if line.strip() == "":
            i += 1
            continue

        # Paragraph accumulator
        para_lines = []
        while i < len(lines) and lines[i].strip() != "" and not lines[i].startswith(
            ("## ", "### ", "#### ", "- ", "* ", "```", "    ")
        ) and not re.match(r"^\d+\. ", lines[i]) and "|" not in lines[i]:
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            html_parts.append(f"<p>{inline_md(' '.join(para_lines))}</p>")
        else:
            i += 1

    return "\n".join(html_parts)


def inline_md(text: str) -> str:
    """Render inline Markdown: bold, italic, code, links."""
    text = escape_html(text)
    # Code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_portal(out_dir: Path) -> None:
    root = repo_root()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Source files to read
    source_files = {
        "onboarding": root / "docs" / "portal" / "onboarding.md",
        "readme": root / "README.md",
        "changelog": root / "CHANGELOG.md",
        "index": root / "docs" / "audits" / "INDEX.md",
        "plugin_json": root / ".claude-plugin" / "plugin.json",
    }

    # Read onboarding content (primary portal source)
    onboarding_text = read_text(source_files["onboarding"])
    sections = markdown_to_html_sections(onboarding_text)

    # Ensure unique anchors
    seen_ids: set[str] = set()
    for s in sections:
        base = s["id"]
        candidate = base
        n = 1
        while candidate in seen_ids:
            candidate = f"{base}-{n}"
            n += 1
        s["id"] = candidate
        seen_ids.add(candidate)

    # Metadata
    sha = git_sha()
    manifest_version = plugin_version(root)
    milestone = project_milestone(root)
    generated_at = datetime.now(timezone.utc).isoformat()

    source_sha256s = {name: sha256_of(path) for name, path in source_files.items()}
    source_paths = {name: str(path.relative_to(root)) for name, path in source_files.items()}

    metadata = {
        "repo": "IMPLEMENTAUDIT",
        "commit_sha": sha,
        "generated_at": generated_at,
        "project_milestone": milestone,
        "plugin_manifest_version": manifest_version,
        "source_files_used": source_paths,
        "source_sha256s": source_sha256s,
        "rough_draft_used": False,
    }

    # Write metadata
    meta_path = out_dir / "docs-metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Build sidebar nav HTML
    nav_items = "".join(
        f'<li><a href="#{s["id"]}" class="nav-link">{escape_html(s["title"])}</a></li>'
        for s in sections
    )

    # Build main content HTML
    content_sections = "".join(
        f'<section id="{s["id"]}" class="content-section">'
        f'<h2>{escape_html(s["title"])}</h2>'
        f'{s["content_html"]}'
        f"</section>\n"
        for s in sections
    )

    # Footer
    footer_html = (
        f"<p>Generated from repo sources &middot; "
        f"Version {escape_html(milestone)} / manifest {escape_html(manifest_version)} "
        f"&middot; Commit {escape_html(sha)} &middot; {escape_html(generated_at)}</p>"
        f"<p>No live deployment freshness is claimed until Pages deploy succeeds in CI.</p>"
    )

    # Full HTML
    html = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>IMPLEMENTAUDIT — Docs Portal</title>
          <style>
            *, *::before, *::after {{ box-sizing: border-box; }}
            :root {{
              --bg: #0f1117;
              --surface: #1a1d27;
              --border: #2d3148;
              --text: #dde1f0;
              --muted: #8890b0;
              --accent: #6c8aff;
              --accent-hover: #8aa4ff;
              --code-bg: #12151f;
              --max-content: 78ch;
            }}
            html {{ scroll-behavior: smooth; }}
            body {{
              margin: 0;
              font-family: system-ui, -apple-system, sans-serif;
              background: var(--bg);
              color: var(--text);
              line-height: 1.65;
              font-size: 1rem;
            }}
            a {{ color: var(--accent); text-decoration: none; }}
            a:hover, a:focus {{ color: var(--accent-hover); text-decoration: underline; }}
            /* Skip link */
            .skip-link {{
              position: absolute;
              left: -9999px;
              top: auto;
              background: var(--accent);
              color: #fff;
              padding: 0.5em 1em;
              z-index: 100;
              border-radius: 0 0 4px 4px;
            }}
            .skip-link:focus {{ left: 1rem; }}
            /* Layout */
            .layout {{
              display: flex;
              min-height: 100vh;
            }}
            /* Sidebar */
            .sidebar {{
              width: 260px;
              flex-shrink: 0;
              background: var(--surface);
              border-right: 1px solid var(--border);
              padding: 1.5rem 0;
              position: sticky;
              top: 0;
              height: 100vh;
              overflow-y: auto;
            }}
            .sidebar h2 {{
              font-size: 0.8rem;
              font-weight: 700;
              text-transform: uppercase;
              letter-spacing: 0.08em;
              color: var(--muted);
              margin: 0 1.25rem 1rem;
            }}
            .sidebar ul {{
              list-style: none;
              margin: 0;
              padding: 0;
            }}
            .sidebar li {{ margin: 0; }}
            .sidebar .nav-link {{
              display: block;
              padding: 0.4rem 1.25rem;
              color: var(--muted);
              font-size: 0.875rem;
              transition: color 0.15s, background 0.15s;
              border-left: 2px solid transparent;
            }}
            .sidebar .nav-link:hover,
            .sidebar .nav-link:focus {{
              color: var(--text);
              background: rgba(108, 138, 255, 0.08);
              border-left-color: var(--accent);
              text-decoration: none;
            }}
            .sidebar .nav-link.active {{
              color: var(--accent);
              border-left-color: var(--accent);
            }}
            /* Main */
            main {{
              flex: 1;
              min-width: 0;
              padding: 2rem 2.5rem;
            }}
            .content-section {{
              max-width: var(--max-content);
              margin-bottom: 3rem;
            }}
            .content-section h2 {{
              font-size: 1.4rem;
              font-weight: 700;
              margin-top: 0;
              padding-top: 1rem;
              border-bottom: 1px solid var(--border);
              padding-bottom: 0.5rem;
              color: var(--text);
            }}
            h3 {{ font-size: 1.1rem; color: var(--text); margin-top: 1.5rem; }}
            h4 {{ font-size: 1rem; color: var(--muted); margin-top: 1.25rem; }}
            p {{ max-width: var(--max-content); margin: 0.75rem 0; }}
            ul, ol {{ max-width: var(--max-content); padding-left: 1.5rem; margin: 0.75rem 0; }}
            li {{ margin: 0.25rem 0; }}
            pre {{
              background: var(--code-bg);
              border: 1px solid var(--border);
              border-radius: 6px;
              padding: 1rem 1.25rem;
              overflow-x: auto;
              font-size: 0.85rem;
              line-height: 1.5;
              max-width: var(--max-content);
            }}
            code {{
              background: var(--code-bg);
              border: 1px solid var(--border);
              border-radius: 3px;
              padding: 0.1em 0.35em;
              font-size: 0.88em;
            }}
            pre code {{ background: none; border: none; padding: 0; font-size: inherit; }}
            .table-wrap {{ overflow-x: auto; max-width: var(--max-content); margin: 0.75rem 0; }}
            table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
            th {{ background: var(--surface); color: var(--muted); text-align: left;
                  padding: 0.5rem 0.75rem; border: 1px solid var(--border); }}
            td {{ padding: 0.5rem 0.75rem; border: 1px solid var(--border); vertical-align: top; }}
            /* Footer */
            footer {{
              border-top: 1px solid var(--border);
              padding: 1.5rem 2.5rem;
              color: var(--muted);
              font-size: 0.8rem;
            }}
            /* Mobile */
            @media (max-width: 700px) {{
              .sidebar {{ display: none; }}
              main {{ padding: 1.25rem 1rem; }}
            }}
          </style>
        </head>
        <body>
          <a class="skip-link" href="#main-content">Skip to content</a>
          <div class="layout">
            <nav class="sidebar" aria-label="Section navigation">
              <h2>IMPLEMENTAUDIT</h2>
              <ul>
                {nav_items}
              </ul>
            </nav>
            <main id="main-content">
              {content_sections}
              <footer>
                {footer_html}
              </footer>
            </main>
          </div>
          <script>
            // IntersectionObserver-based active nav tracking
            const links = document.querySelectorAll('.nav-link');
            const sections = document.querySelectorAll('.content-section');
            const obs = new IntersectionObserver(
              entries => {{
                entries.forEach(e => {{
                  if (e.isIntersecting) {{
                    links.forEach(l => l.classList.remove('active'));
                    const link = document.querySelector('.nav-link[href="#' + e.target.id + '"]');
                    if (link) link.classList.add('active');
                  }}
                }});
              }},
              {{ rootMargin: '-20% 0px -70% 0px', threshold: 0 }}
            );
            sections.forEach(s => obs.observe(s));
          </script>
        </body>
        </html>
    """)

    index_path = out_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    sys.stdout.write(f"build-docs-portal: wrote {index_path}\n")
    sys.stdout.write(f"build-docs-portal: wrote {meta_path}\n")
    sys.stdout.write(f"build-docs-portal: {len(sections)} sections, commit={sha}, milestone={milestone}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build IMPLEMENTAUDIT docs portal")
    parser.add_argument(
        "--out",
        default=None,
        help="Output directory (default: dist/docs-portal/ relative to repo root)",
    )
    args = parser.parse_args()

    root = repo_root()
    out_dir = Path(args.out) if args.out else root / "dist" / "docs-portal"

    build_portal(out_dir)
    sys.exit(0)


if __name__ == "__main__":
    main()
