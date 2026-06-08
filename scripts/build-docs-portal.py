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


# ---------------------------------------------------------------------------
# Sidebar structure — maps group names to (id, icon, label) tuples
# ---------------------------------------------------------------------------
SIDEBAR_GROUPS = [
    ("Start", [
        ("overview", "◈", "Overview"),
        ("quick-start", "⚡", "Quick Start"),
        ("install", "⬇", "Install"),
        ("for-new-users", "◎", "For New Users"),
        ("for-agents-and-operators", "⚙", "For Agents &amp; Operators"),
        ("for-auditors-and-maintainers", "◇", "For Auditors &amp; Maintainers"),
    ]),
    ("Concepts", [
        ("mental-model", "⟶", "Mental Model"),
        ("invocation-model", "⇄", "Invocation Model"),
        ("audit-gate-model", "⊢", "Audit Gate Model"),
        ("what-audit-complete-means", "✓", "AUDIT_COMPLETE"),
        ("state-and-artifact-model", "⧉", "State &amp; Artifacts"),
        ("continuity-and-sidecars", "◐", "Continuity &amp; Sidecars"),
    ]),
    ("Method", [
        ("operating-method", "⟳", "Operating Method"),
        ("routing", "◒", "Routing"),
        ("comparison", "≡", "Comparison"),
        ("default-behavior", "●", "Default Behavior"),
        ("usage-examples", "〈/〉", "Examples"),
    ]),
    ("Reference", [
        ("terminology", "Aa", "Terminology"),
        ("repo-layout", "⊞", "Repo Layout"),
        ("optional-tooling", "⊕", "Optional Tooling"),
        ("safety-and-boundaries", "⚠", "Safety &amp; Boundaries"),
        ("what-it-does-not-do", "×", "What It Doesn&#39;t Do"),
        ("evidence-and-audit-trail", "§", "Evidence &amp; Audit Trail"),
        ("audit-status", "i", "Audit Status"),
    ]),
]

HERO_SUBTITLE = (
    "An audit-governed implementation method. Every mutation is bounded "
    "by an audit contract, verified by ten explicit gates, and closed "
    "by terminal evidence — not sentiment."
)

PROCESS_STEPS = ["Input", "Gemba", "Smoke A", "Patch", "Smoke B", "Final Audit"]

AUDIENCE_SECTIONS = {
    "for-new-users",
    "for-agents-and-operators",
    "for-auditors-and-maintainers",
}

# ---------------------------------------------------------------------------
# CSS — embedded in the generator
# ---------------------------------------------------------------------------
PORTAL_CSS = """\
*, *::before, *::after { box-sizing: border-box; }
:root {
  --bg-base: #0b1120;
  --bg-card: #111827;
  --bg-sidebar: #0f172a;
  --bg-hover: #1e293b;
  --bg-active: #1e3a5f;
  --border: #1e293b;
  --border-light: #334155;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-cyan: #22d3ee;
  --accent-emerald: #34d399;
  --accent-violet: #a78bfa;
  --accent-amber: #fbbf24;
  --accent-rose: #fb7185;
  --accent-blue: #60a5fa;
  --code-bg: #1e293b;
  --code-border: #334155;
  --sidebar-width: 260px;
  --prose-max: 78ch;
  --content-max: 820px;
}
html { font-size: 17px; scroll-behavior: smooth; }
body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.7;
  font-size: 1rem;
  display: flex;
  min-height: 100vh;
  background-image:
    radial-gradient(ellipse at 20% 20%, rgba(34,211,238,0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(167,139,250,0.04) 0%, transparent 50%);
}
/* Skip link */
.skip-link {
  position: absolute; top: -100%; left: 0; z-index: 999;
  padding: 0.5rem 1rem; background: var(--accent-cyan); color: #0b1120;
  font-size: 0.85rem; font-weight: 600; text-decoration: none;
  border-radius: 0 0 6px 0; transition: top 0.15s;
}
.skip-link:focus { position: fixed; top: 0; }
/* Sidebar */
.sidebar {
  position: fixed; left: 0; width: var(--sidebar-width); height: 100vh;
  background: var(--bg-sidebar); border-right: 1px solid var(--border);
  overflow-y: hidden; z-index: 100; padding-bottom: 2rem;
}
.sidebar:hover, .sidebar:focus-within { overflow-y: auto; }
.sidebar-header {
  padding: 1.25rem 1.25rem 0.75rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.5rem;
}
.sidebar-title {
  font-size: 0.95rem; font-weight: 700;
  color: var(--accent-cyan); letter-spacing: -0.01em;
}
.sidebar-subtitle {
  font-size: 0.72rem; color: var(--text-muted);
  margin-top: 0.2rem; font-family: monospace;
}
.sidebar-nav { padding: 0 0.75rem; }
.nav-group { margin-bottom: 0.15rem; }
.nav-group-label {
  padding: 0.45rem 0.5rem; font-size: 0.72rem; font-weight: 700;
  letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--text-muted); cursor: pointer; display: flex;
  align-items: center; border-radius: 5px; user-select: none;
  list-style: none; transition: background 0.12s, color 0.12s;
}
.nav-group-label:hover { background: var(--bg-hover); color: var(--text-secondary); }
.nav-group[open] > summary::after { content: '▾'; margin-left: auto; font-size: 0.65em; opacity: 0.5; }
.nav-group:not([open]) > summary::after { content: '▸'; margin-left: auto; font-size: 0.65em; opacity: 0.5; }
.nav-group-label::-webkit-details-marker { display: none; }
.nav-group-label::marker { display: none; content: ''; }
.nav-section a {
  display: flex; align-items: center; gap: 0.45rem;
  padding: 0.38rem 0.55rem; color: var(--text-secondary);
  text-decoration: none; font-size: 0.875rem; font-weight: 500;
  border-radius: 5px; transition: background 0.12s, color 0.12s;
  border: 1px solid transparent;
}
.nav-section a:hover, .nav-section a:focus-visible {
  background: rgba(30,41,59,0.95); color: var(--text-primary);
  border-color: rgba(96,165,250,0.15);
  box-shadow: inset 2px 0 0 rgba(34,211,238,0.3);
}
.nav-section a:focus-visible { outline: 2px solid var(--accent-cyan); outline-offset: 2px; }
.nav-section a.active-nav {
  background: var(--bg-active) !important; color: var(--accent-cyan) !important;
  font-weight: 600; box-shadow: inset 3px 0 0 var(--accent-cyan);
}
.nav-icon { width: 1.1em; text-align: center; flex-shrink: 0; opacity: 0.7; font-size: 0.95em; }
.nav-section a:hover .nav-icon, .nav-section a.active-nav .nav-icon { opacity: 1; }
/* Main */
.main { margin-left: var(--sidebar-width); flex: 1; min-width: 0; }
.content { max-width: var(--content-max); margin: 0 auto; padding: 2.5rem 2.5rem 6rem; }
/* Hero */
.hero-zone { position: relative; margin-bottom: 1.5rem; }
.hero-zone::before {
  content: ''; position: absolute; top: 0; left: -2.5rem; right: -2.5rem; bottom: 0;
  background-image:
    linear-gradient(rgba(30,41,59,0.4) 1px, transparent 1px),
    linear-gradient(90deg, rgba(30,41,59,0.4) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at 50% 40%, black 30%, transparent 60%);
  -webkit-mask-image: radial-gradient(ellipse at 50% 40%, black 30%, transparent 60%);
  pointer-events: none; z-index: 0;
}
.hero-zone > * { position: relative; z-index: 1; }
h1.page-title {
  font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em;
  line-height: 1.15; margin-bottom: 0.6rem;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-violet));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-subtitle {
  font-size: 1rem; color: var(--text-secondary);
  margin-bottom: 1.5rem; line-height: 1.65; max-width: var(--prose-max);
}
/* Process flow */
.process-flow {
  display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;
  margin-bottom: 0.5rem; padding: 0.875rem 1rem;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; max-width: fit-content;
}
.process-step {
  background: var(--bg-hover); border: 1px solid var(--border-light);
  border-radius: 5px; padding: 0.3rem 0.65rem;
  font-size: 0.82rem; font-weight: 600; color: var(--accent-cyan);
  white-space: nowrap; font-family: monospace;
}
.process-arrow { color: var(--text-muted); font-size: 0.75rem; }
/* Mobile TOC */
.mobile-toc {
  display: none; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 0.875rem 1.125rem; margin-bottom: 1.5rem;
}
.mobile-toc summary {
  cursor: pointer; font-weight: 600; font-size: 0.85rem;
  color: var(--accent-cyan); padding: 0.2rem 0; user-select: none;
}
.mobile-toc ol { margin: 0.4rem 0 0; padding-left: 1.2rem; font-size: 0.82rem; }
.mobile-toc ol li { margin-bottom: 0.18rem; }
.mobile-toc ol li a { color: var(--text-secondary); text-decoration: none; }
.mobile-toc ol li a:hover { color: var(--accent-cyan); }
/* Section headings */
h2 {
  font-size: 1.45rem; font-weight: 700; letter-spacing: -0.02em;
  color: var(--text-primary); margin-top: 3rem; margin-bottom: 0.875rem;
  padding-bottom: 0.45rem; border-bottom: 1px solid var(--border); line-height: 1.3;
}
h3 {
  font-size: 1.05rem; font-weight: 600; color: var(--accent-cyan);
  margin-top: 1.75rem; margin-bottom: 0.625rem; line-height: 1.3;
}
h4 {
  font-size: 0.9rem; font-weight: 600; color: var(--text-secondary);
  margin-top: 1.25rem; margin-bottom: 0.4rem;
}
/* Prose */
p { margin-bottom: 0.875rem; color: var(--text-secondary); max-width: var(--prose-max); }
ul, ol { margin-bottom: 0.875rem; padding-left: 1.5rem; max-width: var(--prose-max); }
li { margin-bottom: 0.3rem; color: var(--text-secondary); }
a { color: var(--accent-blue); text-decoration: none; transition: color 0.15s; }
a:hover { color: var(--accent-cyan); }
/* Code */
code {
  font-family: 'SF Mono', 'Menlo', monospace; font-size: 0.82em;
  background: var(--code-bg); padding: 0.12em 0.38em;
  border-radius: 4px; border: 1px solid var(--code-border);
  color: var(--accent-emerald);
}
pre {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 0.875rem 1.1rem; overflow-x: auto;
  margin-bottom: 1rem; font-size: 0.84rem; line-height: 1.6;
  max-width: var(--content-max);
}
pre code { background: none; border: none; padding: 0; font-size: inherit; color: var(--text-primary); }
/* Tables */
table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.875rem; }
thead th {
  background: var(--bg-hover); border: 1px solid var(--border);
  padding: 0.55rem 0.75rem; text-align: left; font-weight: 600;
  color: var(--text-primary); font-size: 0.82rem;
}
tbody td { border: 1px solid var(--border); padding: 0.55rem 0.75rem; color: var(--text-secondary); vertical-align: top; }
tbody tr:hover { background: rgba(30,41,59,0.4); }
/* Callouts */
.callout {
  border-left: 3px solid; border-radius: 6px; padding: 0.875rem 1.1rem;
  margin: 1.25rem 0; font-size: 0.875rem; max-width: var(--prose-max);
}
.callout-info { background: rgba(34,211,238,0.06); border-color: var(--accent-cyan); }
.callout-info .callout-title { color: var(--accent-cyan); }
.callout-warning { background: rgba(251,191,36,0.06); border-color: var(--accent-amber); }
.callout-warning .callout-title { color: var(--accent-amber); }
.callout-danger { background: rgba(251,113,133,0.06); border-color: var(--accent-rose); }
.callout-danger .callout-title { color: var(--accent-rose); }
.callout-success { background: rgba(52,211,153,0.06); border-color: var(--accent-emerald); }
.callout-success .callout-title { color: var(--accent-emerald); }
.callout p { margin: 0; max-width: none; color: var(--text-secondary); }
.callout p + p { margin-top: 0.35rem; }
.callout-title { font-weight: 700; }
/* Cards */
.card-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1rem; margin: 1.25rem 0;
}
.audience-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; padding: 1.1rem; position: relative;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.audience-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 3px; border-radius: 10px 10px 0 0;
  background: var(--accent-cyan);
}
.audience-card:hover {
  border-color: var(--border-light); box-shadow: 0 4px 20px rgba(0,0,0,0.18);
}
.audience-card h4 { margin-top: 0.3rem; margin-bottom: 0.35rem; color: var(--text-primary); font-size: 0.875rem; }
.audience-card p { font-size: 0.82rem; color: var(--text-muted); margin: 0 0 0.5rem; }
.audience-card ul { font-size: 0.8rem; margin: 0.35rem 0 0; padding-left: 0; list-style: none; }
.audience-card ul li { margin-bottom: 0.15rem; }
.audience-card ul li a { color: var(--accent-blue); }
.audience-card ul li a:hover { color: var(--accent-cyan); }
/* Method cards (PDCA, Gemba, etc.) */
.method-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 1rem 1.1rem;
  transition: border-color 0.2s;
}
.method-card:hover { border-color: var(--border-light); }
.method-card h4 { margin-top: 0; margin-bottom: 0.3rem; color: var(--text-primary); font-size: 0.875rem; }
.method-card p { font-size: 0.82rem; color: var(--text-muted); margin: 0; }
/* Audit status list */
.audit-status-list { list-style: none; padding: 0; margin: 0; }
.audit-status-list li {
  display: flex; gap: 0.75rem; padding: 0.5rem 0;
  border-bottom: 1px solid var(--border); font-size: 0.875rem;
  color: var(--text-secondary); align-items: baseline;
}
.audit-status-list li:last-child { border-bottom: none; }
.audit-status-label {
  font-weight: 600; color: var(--text-muted); min-width: 9em;
  flex-shrink: 0; font-size: 0.8rem;
}
/* Evidence links */
.evidence-links { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; margin: 0.75rem 0; }
.evidence-links a { font-size: 0.875rem; }
/* Footer */
.site-footer {
  border-top: 1px solid var(--border); padding: 1.25rem 2.5rem 1.5rem;
  color: var(--text-muted); font-size: 0.8rem;
}
.site-footer-inner {
  max-width: var(--content-max); margin: 0 auto;
  display: flex; flex-wrap: wrap; justify-content: space-between;
  align-items: center; gap: 0.5rem 1.25rem;
}
/* Responsive */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { margin-left: 0; }
  .content { padding: 1.5rem 1rem 4rem; }
  h1.page-title { font-size: 1.75rem; }
  .mobile-toc { display: block; }
  .process-flow { max-width: 100%; }
}
@media (min-width: 1440px) {
  .content { max-width: 1000px; }
  .site-footer-inner { max-width: 1000px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
/* Scrollbar */
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-track { background: transparent; }
.sidebar::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 2px; }
"""

# ---------------------------------------------------------------------------
# Repo helpers
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    script = Path(__file__).resolve()
    return script.parent.parent


def git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root()),
            capture_output=True, text=True, timeout=5,
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
    for p in [root / ".claude-plugin" / "plugin.json", root / "plugin.json"]:
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
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


# ---------------------------------------------------------------------------
# Markdown parser helpers
# ---------------------------------------------------------------------------

def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def title_to_id(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def inline_md(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def parse_sections(md_text: str):
    """Parse markdown into (page_title, page_subtitle, sections[]).

    Each section is {id, title, lines[]}.
    """
    lines = md_text.splitlines()
    page_title = ""
    page_subtitle = ""
    current_title = None
    current_lines: list = []
    sections = []

    past_header_comment = False

    for line in lines:
        if line.startswith("# "):
            page_title = line[2:].strip()
            continue
        # Skip the source-file metadata comment block at the top
        if (not past_header_comment and not page_title
                and not line.startswith("#")):
            continue
        if page_title and not past_header_comment:
            # The blank line or first paragraph after h1 is subtitle
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not page_subtitle:
                # Accept as subtitle if it's not a section heading
                if not stripped.startswith("Source"):
                    page_subtitle = stripped
                past_header_comment = True
            elif stripped.startswith("Source"):
                past_header_comment = True
            continue

        if line.startswith("## "):
            if current_title is not None:
                sections.append({
                    "id": title_to_id(current_title),
                    "title": current_title,
                    "lines": current_lines,
                })
            current_title = line[3:].strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append({
            "id": title_to_id(current_title),
            "title": current_title,
            "lines": current_lines,
        })

    return page_title, HERO_SUBTITLE, sections


def render_callout(callout_type: str, lines: list) -> str:
    cls = f"callout callout-{callout_type.lower()}"
    inner = "\n".join(lines).strip()
    # First line may be a title (starts with **)
    first_line_match = re.match(r"\*\*(.+?)\*\*\.?\s*(.*)", inner, re.DOTALL)
    if first_line_match:
        title_text = esc(first_line_match.group(1))
        rest = first_line_match.group(2).strip()
        content_html = f'<p><span class="callout-title">{title_text}.</span>'
        if rest:
            content_html += " " + inline_md(rest)
        content_html += "</p>"
    else:
        content_html = f"<p>{inline_md(inner)}</p>"
    return f'<div class="{cls}">{content_html}</div>'


def lines_to_html(lines: list) -> str:
    """Render markdown lines to HTML, handling callouts, tables, code, lists, paragraphs."""
    parts = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Callout block: :::type
        if re.match(r"^:::(info|warning|danger|success)\s*$", line.strip()):
            callout_type = line.strip()[3:].strip()
            callout_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                callout_lines.append(lines[i])
                i += 1
            i += 1  # skip closing :::
            parts.append(render_callout(callout_type, callout_lines))
            continue

        # Fenced code block
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code_content = "\n".join(code_lines)
            parts.append(f"<pre><code>{esc(code_content)}</code></pre>")
            continue

        # 4-space or tab indented code block
        if line.startswith("    ") or (line.startswith("\t") and line.strip()):
            code_lines = []
            while i < len(lines) and (lines[i].startswith("    ") or lines[i].startswith("\t") or lines[i] == ""):
                if lines[i] == "" and code_lines:
                    code_lines.append("")
                elif lines[i].startswith("    "):
                    code_lines.append(lines[i][4:])
                elif lines[i].startswith("\t"):
                    code_lines.append(lines[i][1:])
                i += 1
            # Strip trailing blanks
            while code_lines and code_lines[-1] == "":
                code_lines.pop()
            code_content = "\n".join(code_lines)
            parts.append(f"<pre><code>{esc(code_content)}</code></pre>")
            continue

        # Table: detect | ... | with separator on next line
        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|[-| :]+\|\s*$", lines[i + 1]):
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            header_html = "<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr></thead>"
            body_rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                body_rows.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in cells) + "</tr>")
                i += 1
            parts.append(f'<table>{header_html}<tbody>{"".join(body_rows)}</tbody></table>')
            continue

        # Unordered list
        if re.match(r"^[-*] ", line):
            list_items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i]):
                item = lines[i][2:].strip()
                list_items.append(f"<li>{inline_md(item)}</li>")
                i += 1
            parts.append("<ul>" + "".join(list_items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\. ", line):
            list_items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                item = re.sub(r"^\d+\. ", "", lines[i]).strip()
                list_items.append(f"<li>{inline_md(item)}</li>")
                i += 1
            parts.append("<ol>" + "".join(list_items) + "</ol>")
            continue

        # H3 (skip card: headings — handled separately)
        if line.startswith("### ") and not line.startswith("### card: "):
            parts.append(f"<h3>{inline_md(line[4:].strip())}</h3>")
            i += 1
            continue

        # H4
        if line.startswith("#### "):
            parts.append(f"<h4>{inline_md(line[5:].strip())}</h4>")
            i += 1
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph accumulator
        para_lines = []
        while i < len(lines):
            l = lines[i]
            if not l.strip():
                break
            if re.match(r"^(#{1,4} |[-*] |\d+\. |    |\t|:::|```|\|)", l):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            para_text = " ".join(para_lines)
            parts.append(f"<p>{inline_md(para_text)}</p>")
        else:
            i += 1

    return "\n".join(parts)


def render_audience_section(section_id: str, lines: list) -> str:
    """Render a section that may contain ### card: blocks as a card grid."""
    intro_lines = []
    cards = []
    current_card = None

    for line in lines:
        if line.startswith("### card: "):
            if current_card is not None:
                cards.append(current_card)
            current_card = {"title": line[10:].strip(), "lines": []}
        elif current_card is not None:
            current_card["lines"].append(line)
        else:
            intro_lines.append(line)

    if current_card is not None:
        cards.append(current_card)

    html = lines_to_html(intro_lines)

    if cards:
        card_html_parts = []
        for card in cards:
            card_content = lines_to_html(card["lines"])
            card_html_parts.append(
                f'<div class="audience-card">'
                f'<h4>{esc(card["title"])}</h4>'
                f'{card_content}'
                f'</div>'
            )
        html += f'<div class="card-grid">{"".join(card_html_parts)}</div>'

    return html


def render_section(section: dict) -> str:
    """Render a single section's content to HTML."""
    sid = section["id"]
    lines = section["lines"]

    if sid in AUDIENCE_SECTIONS:
        return render_audience_section(sid, lines)

    return lines_to_html(lines)


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def build_sidebar(sections: list, all_section_ids: set) -> str:
    nav_html = ""
    for group_name, group_items in SIDEBAR_GROUPS:
        # Only include items that exist in the parsed sections
        visible_items = [(sid, icon, label) for sid, icon, label in group_items if sid in all_section_ids]
        if not visible_items:
            continue
        items_html = "".join(
            f'<div class="nav-section">'
            f'<a href="#{sid}">'
            f'<span class="nav-icon" aria-hidden="true">{esc(icon)}</span>'
            f'<span>{label}</span>'
            f'</a></div>'
            for sid, icon, label in visible_items
        )
        nav_html += (
            f'<details class="nav-group" open>'
            f'<summary class="nav-group-label">{esc(group_name)}</summary>'
            f'{items_html}'
            f'</details>'
        )
    return f'<nav class="sidebar" aria-label="Documentation navigation">' \
           f'<div class="sidebar-header">' \
           f'<div class="sidebar-title">IMPLEMENTAUDIT.md</div>' \
           f'<div class="sidebar-subtitle">audit-governed implementation</div>' \
           f'</div>' \
           f'<div class="sidebar-nav">{nav_html}</div>' \
           f'</nav>'


def build_hero() -> str:
    process_html = "".join(
        f'<span class="process-step">{esc(s)}</span>'
        + (f'<span class="process-arrow">&#8594;</span>' if i < len(PROCESS_STEPS) - 1 else "")
        for i, s in enumerate(PROCESS_STEPS)
    )
    return (
        f'<div class="hero-zone">'
        f'<h1 class="page-title">IMPLEMENTAUDIT.md</h1>'
        f'<p class="hero-subtitle">{esc(HERO_SUBTITLE)}</p>'
        f'<div class="process-flow">{process_html}</div>'
        f'</div>'
    )


def build_mobile_toc(sections: list, all_section_ids: set) -> str:
    # Use sidebar order for TOC
    ordered = []
    seen = set()
    for group_name, group_items in SIDEBAR_GROUPS:
        for sid, icon, label in group_items:
            if sid in all_section_ids and sid not in seen:
                # Find the real section title
                ordered.append((sid, label))
                seen.add(sid)
    # Append any sections not in sidebar
    for s in sections:
        if s["id"] not in seen:
            ordered.append((s["id"], s["title"]))
            seen.add(s["id"])

    items_html = "".join(
        f'<li><a href="#{sid}">{label}</a></li>'
        for sid, label in ordered
    )
    return (
        f'<details class="mobile-toc">'
        f'<summary>&#128209; Page Contents</summary>'
        f'<ol>{items_html}</ol>'
        f'</details>'
    )


def build_content_sections(sections: list) -> str:
    html = ""
    for section in sections:
        section_html = render_section(section)
        anchor_icon = f'<span class="anchor-icon" aria-hidden="true">&#182;</span>'
        html += (
            f'<section id="{esc(section["id"])}" class="content-section">'
            f'<h2>{esc(section["title"])} {anchor_icon}</h2>'
            f'{section_html}'
            f'</section>\n'
        )
    return html


def build_footer(sha: str, milestone: str, manifest_version: str, generated_at: str) -> str:
    return (
        f'<footer class="site-footer" aria-label="Site footer">'
        f'<div class="site-footer-inner">'
        f'<span><strong>IMPLEMENTAUDIT.md</strong> &mdash; audit-governed implementation skill.</span>'
        f'<span>v{esc(milestone)} &middot; manifest {esc(manifest_version)} &middot; commit {esc(sha)}</span>'
        f'<span>Source: <code>skills/SKILL.md</code> &middot; <code>AGENTS.md</code></span>'
        f'</div>'
        f'</footer>'
    )


JS_SCROLLSPY = """\
(function(){
  var targets = [];
  document.querySelectorAll('.sidebar-nav .nav-section a[href^="#"]').forEach(function(link){
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if(el) targets.push({id:id, el:el, link:link});
  });
  targets.sort(function(a,b){ return a.el.compareDocumentPosition(b.el) & 4 ? -1 : 1; });
  var activeId = null;
  var ticking = false;
  function update(){
    var threshold = 130;
    var found = targets.length ? targets[0] : null;
    for(var i=0;i<targets.length;i++){
      if(targets[i].el.getBoundingClientRect().top <= threshold) found = targets[i];
      else break;
    }
    if(!found || found.id === activeId) return;
    activeId = found.id;
    targets.forEach(function(t){ t.link.classList.remove('active-nav'); });
    found.link.classList.add('active-nav');
    var group = found.link.closest('.nav-group');
    if(group && !group.open) group.open = true;
  }
  window.addEventListener('scroll', function(){
    if(!ticking){ requestAnimationFrame(function(){ ticking=false; update(); }); ticking=true; }
  }, {passive:true});
  window.addEventListener('resize', update, {passive:true});
  update();
})();
"""


def assemble_page(sidebar_html: str, hero_html: str, mobile_toc_html: str,
                  content_html: str, footer_html: str,
                  sha: str, milestone: str, manifest_version: str) -> str:
    css = PORTAL_CSS
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IMPLEMENTAUDIT.md — Docs Portal</title>
  <meta name="description" content="IMPLEMENTAUDIT.md: audit-governed implementation skill. v{esc(milestone)}.">
  <style>
{css}
  </style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
{sidebar_html}
<div class="main">
  <div class="content" id="main-content">
    {hero_html}
    {mobile_toc_html}
    {content_html}
  </div>
  {footer_html}
</div>
<script>
{JS_SCROLLSPY}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------

def build_portal(out_dir: Path) -> None:
    root = repo_root()
    out_dir.mkdir(parents=True, exist_ok=True)

    source_files = {
        "onboarding": root / "docs" / "portal" / "onboarding.md",
        "readme": root / "README.md",
        "changelog": root / "CHANGELOG.md",
        "index": root / "docs" / "audits" / "INDEX.md",
        "plugin_json": root / ".claude-plugin" / "plugin.json",
    }

    onboarding_text = read_text(source_files["onboarding"])
    page_title, page_subtitle, sections = parse_sections(onboarding_text)

    all_section_ids = {s["id"] for s in sections}

    # Collect sections in sidebar order for the nav
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

    meta_path = out_dir / "docs-metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    sidebar_html = build_sidebar(sections, all_section_ids)
    hero_html = build_hero()
    mobile_toc_html = build_mobile_toc(sections, all_section_ids)
    content_html = build_content_sections(sections)
    footer_html = build_footer(sha, milestone, manifest_version, generated_at)

    html = assemble_page(
        sidebar_html, hero_html, mobile_toc_html, content_html, footer_html,
        sha, milestone, manifest_version,
    )

    index_path = out_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    sys.stdout.write(f"build-docs-portal: wrote {index_path}\n")
    sys.stdout.write(f"build-docs-portal: wrote {meta_path}\n")
    sys.stdout.write(
        f"build-docs-portal: {len(sections)} sections, commit={sha}, milestone={milestone}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build IMPLEMENTAUDIT docs portal")
    parser.add_argument("--out", default=None, help="Output directory")
    args = parser.parse_args()

    root = repo_root()
    out_dir = Path(args.out) if args.out else root / "dist" / "docs-portal"
    build_portal(out_dir)
    sys.exit(0)


if __name__ == "__main__":
    main()
