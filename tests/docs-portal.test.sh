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
bad_release_label="$tmp/bad-release-label"
bad_overview_release="$tmp/bad-overview-release"
bad_marker_taxonomy="$tmp/bad-marker-taxonomy"
bad_slash_boundary="$tmp/bad-slash-boundary"
bad_helper_path_boundary="$tmp/bad-helper-path-boundary"
bad_comparison_spotlight="$tmp/bad-comparison-spotlight"
bad_magnet_contract="$tmp/bad-magnet-contract"
bad_card_glass="$tmp/bad-card-glass"
bad_card_shimmer="$tmp/bad-card-shimmer"
bad_top_tabs="$tmp/bad-top-tabs"
bad_sidebar_tree="$tmp/bad-sidebar-tree"
bad_sidecar_freshness="$tmp/bad-sidecar-freshness"
bad_stage_sequence="$tmp/bad-stage-sequence"

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
assert list(groups) == ["Overview", "First run", "Audience", "Core model", "Evidence", "Closure", "Repository", "Research & Engineering Lineage", "References"]
assert "References" in groups
assert "Reference" not in groups
assert "Maintainers" not in groups
assert groups["First run"] == ["quick-start", "installation", "possible-endings", "comparison"]
assert groups["Audience"] == ["for-new-users", "for-agents-and-operators", "for-auditors-and-maintainers"]
assert groups["Core model"] == ["runtime-model", "audit-gate-model", "invocation-shapes", "usage-examples", "planning-and-phases", "routing", "operating-method"]
assert groups["Evidence"] == ["state-and-artifacts", "repo-state-comparison", "error-handling", "evidence-boundaries", "optional-tooling", "child-agent-review-loops"]
assert groups["Closure"] == ["completion-semantics", "continuity-and-sidecars"]
assert groups["Repository"] == ["repo-layout", "package-contents", "audit-trail"]
assert groups["Research & Engineering Lineage"] == [
    "research-lineage-overview",
    "research-lineage-lean",
    "research-lineage-agile",
    "research-lineage-waterfall",
    "research-lineage-evolved-law",
    "research-lineage-systems-engineering",
    "research-lineage-systems-security-engineering",
    "research-lineage-decision-operations-engineering",
    "research-lineage-evolved-ssd",
    "research-lineage-distributed-systems-engineering",
    "research-lineage-reliability-maintainability-engineering",
    "research-lineage-formal-methods-verification-engineering",
    "research-lineage-evolved-drf",
    "research-lineage-cognitive-systems-engineering",
    "research-lineage-statistical-engineering",
    "research-lineage-systems-safety",
    "research-lineage-evolved-css",
    "research-lineage-s3e",
]
assert groups["References"] == ["terminology", "reference-index"]
assert len(ordered) == meta["page_count"]
assert meta["portal_version"] == "v2-multipage"
assert meta["rough_draft_used"] is False
assert meta["worktree_state"] in {"clean", "dirty", "unknown"}
assert isinstance(meta["worktree_dirty"], bool)
assert meta["project_milestone"] == site["release"]["milestone"]
assert meta["plugin_manifest_version"] == site["release"]["manifest_version"]
assert meta["package_identity"]["logical_package"] == "IMPLEMENTAUDIT_PLUGIN"
assert meta["package_identity"]["required_skills"] == [
    "implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"
]
assert meta["package_identity"]["internal_skills"] == [
    {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
    {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
]
assert meta["package_identity"]["generated_projections"] == {
    "canonical_plugin": {"artifact": "IMPLEMENTAUDIT.plugin.zip", "layout": "plugin-root"},
    "standalone_compatibility": {"artifact": "IMPLEMENTAUDIT.skill", "layout": "flattened-skill"},
}
assert meta["release_url"] == site["release"]["url"]
assert meta["release_publication_state"] == "published"
assert site["release"]["milestone"] == "v0.4.0.0"
assert site["release"]["manifest_version"] == "0.4.0"
assert site["release"]["audit_ledger_url"].endswith("/v0.4.0.0-release-report.md")
audit_trail_source = Path("docs/portal/pages/audit-trail.html").read_text(encoding="utf-8")
assert "39bf3006df81a12d3c2a32e956cab00c3b3384d9" in audit_trail_source
assert "e7a733be10338a398d0112454088ae3dc2b56f60" in audit_trail_source
assert "6d57060aeab3aeec1d0ad090c2fa7ab66ca9de67" not in audit_trail_source
assert "3b5c300..." not in audit_trail_source
required = {
    "docs/portal/site.json",
    "docs/portal/pages/overview.html",
    "docs/portal/pages/quick-start.html",
    "docs/portal/pages/runtime-model.html",
    "docs/portal/pages/reference-index.html",
    "docs/portal/pages/research-lineage-evolved-css.html",
    "docs/portal/pages/research-lineage-evolved-ssd.html",
    "docs/portal/pages/research-lineage-evolved-drf.html",
    "docs/portal/pages/research-lineage-systems-engineering.html",
    "docs/portal/pages/research-lineage-systems-security-engineering.html",
    "docs/portal/pages/research-lineage-decision-operations-engineering.html",
    "docs/portal/pages/research-lineage-distributed-systems-engineering.html",
    "docs/portal/pages/research-lineage-reliability-maintainability-engineering.html",
    "docs/portal/pages/research-lineage-formal-methods-verification-engineering.html",
    "docs/portal/pages/research-lineage-cognitive-systems-engineering.html",
    "docs/portal/pages/research-lineage-statistical-engineering.html",
    "docs/portal/pages/research-lineage-systems-safety.html",
    "docs/portal/pages/research-lineage-s3e.html",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "package/implementaudit-package.json",
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
    assert "<dt>Release</dt>" in text
    assert "<dt>Candidate release</dt>" not in text
overview = (out / "index.html").read_text(encoding="utf-8")
assert "<em>Release</em>" in overview
assert "<em>Candidate release</em>" not in overview
PY
then
  ok "metadata, site nav, and page shell agree"
else
  fail_check "metadata/site nav/page shell mismatch"
fi

if "${py_cmd[@]}" - <<'PY'
import json
from pathlib import Path

contract = json.loads(Path("package/implementaudit-package.json").read_text(encoding="utf-8"))
report = Path("docs/audits/archive/v0.4.0.0-release-report.md").read_text(encoding="utf-8")
page = Path("docs/portal/pages/audit-trail.html").read_text(encoding="utf-8")
report_flat = " ".join(report.split())
expected = {
    contract["generated_projections"]["canonical_plugin"]["artifact"],
    contract["generated_projections"]["standalone_compatibility"]["artifact"],
}
for artifact in expected:
    if artifact not in report or artifact not in page:
        raise SystemExit(f"release report or portal omits projection {artifact}")
if "exact members, bytes, SHA-256, source commit/tree, and clean-state binding `PENDING`" not in report:
    raise SystemExit("release report does not preserve exact-candidate identity as pending")
if "attach exactly `IMPLEMENTAUDIT.plugin.zip`,\n`IMPLEMENTAUDIT.skill`, and `CHECKSUMS.txt`" not in report:
    raise SystemExit("release report does not require the exact three public assets")
nonclaim = (
    "no v0.4.0.0 tag, GitHub Release, public asset, Pages deployment, public download, "
    "marketplace state, native Codex or Claude plugin load, provenance, signature, "
    "attestation, SBOM, licence, or universal host behaviour is claimed."
)
if nonclaim not in report_flat:
    raise SystemExit("release report does not preserve the native-host nonclaim")
required_skills = contract["required_skills"]
governor = contract["public_governor"]
children = [skill["name"] for skill in contract["internal_skills"]]
if required_skills != [governor, *children] or len(children) != 4:
    raise SystemExit("package contract does not expose one governor plus four children")
for surface_name, surface in (("release report", report_flat), ("audit trail", page)):
    if "one public/default governor and four child skills" not in surface:
        raise SystemExit(f"{surface_name} does not state the current governor/child population")
    for skill in required_skills:
        if skill not in surface:
            raise SystemExit(f"{surface_name} omits required skill {skill}")
    if "zero v0.4 child skills" in surface or "one required skill" in surface:
        raise SystemExit(f"{surface_name} retains the superseded zero-child topology")
PY
then
  ok "release report and portal bind both projections without preclaiming final bytes or native hosts"
else
  fail_check "release report or portal projection/currentness boundary is stale"
fi

if "${py_cmd[@]}" - <<'PY'
from pathlib import Path

sources = {
    "s3e": Path("docs/portal/pages/research-lineage-s3e.html").read_text(encoding="utf-8"),
    "css": Path("docs/portal/pages/research-lineage-evolved-css.html").read_text(encoding="utf-8"),
}
anchors = {
    "canonical-title": (
        "s3e", "State Synthesis Substrate Engineering: Evolved-SSDDRFCSS"),
    "one-substrate-no-methodology-mode": (
        "s3e", "They do not create nine runtimes, selectable methodology modes, or a fixed ceremony."),
    "ordinary-work-cheap-path": (
        "css", "When one authoritative deterministic discriminator settles ordinary bounded work, use it and stop. No trigger means no added ceremony, record, or family machinery."),
}

def missing(text_by_owner):
    return [key for key, (owner, literal) in anchors.items()
            if literal not in text_by_owner[owner]]

if missing(sources):
    raise SystemExit(f"live S³E docs anchors missing: {missing(sources)}")
for key, (owner, literal) in anchors.items():
    mutated = dict(sources)
    mutated[owner] = mutated[owner].replace(literal, "CORRUPTED", 1)
    if key not in missing(mutated):
        raise SystemExit(f"held-out S³E docs mutation false-passed: {key}")
PY
then
  ok "source-coupled S³E title/no-mode/cheap-path held-outs fail docs acceptance"
else
  fail_check "source-coupled S³E public boundary held-out failed"
fi

if "${py_cmd[@]}" - <<'PY'
import json
from pathlib import Path

site = json.loads(Path("docs/portal/site.json").read_text(encoding="utf-8"))
release = site["release"]
assert release["publication_state"] == "published"
status = release["status"].lower()
assert "published" in status and "independently read back" in status
for stale in ("candidate public identity", "prepublication", "remain pending"):
    assert stale not in status, stale

for path, forbidden in {
    "README.md": (
        "candidate public identity is `v0.4.0.0`",
        "Current project milestone: prepublication `v0.4.0.0` candidate",
        "Only after v0.4.0.0 is published and independently read back",
        "future tagged `v0.4.0.0` asset",
    ),
    "CHANGELOG.md": (
        "No changes are currently assigned beyond the v0.4.0.0 candidate.",
        "This source entry is a prepublication candidate",
        "Final artifact bytes, SHA-256 values, native-host results, hosted checks, and public readbacks remain pending",
    ),
    "docs/portal/pages/overview.html": (
        "v0.4.0.0 candidate",
        "Candidate release",
    ),
    "docs/portal/pages/installation.html": (
        "candidate release routes, not evidence that a public release already exists",
        "release-page, checksum, and fresh-download digests remain pending",
    ),
    "docs/portal/pages/audit-trail.html": (
        "Prepublication <code>v0.4.0.0</code> candidate",
        "v0.4.0.0 final-main Pages qualification and public readback remain pending",
    ),
}.items():
    text = Path(path).read_text(encoding="utf-8")
    for stale in forbidden:
        assert stale not in text, f"{path}: {stale}"
PY
then
  ok "maintained v0.4 public owners reject stale candidate and pending-publication truth"
else
  fail_check "maintained v0.4 public owners retain stale candidate or pending-publication truth"
fi

if "${py_cmd[@]}" - "$tmp/portal-release-identity" <<'PY'
import json
import shutil
import subprocess
import sys
from pathlib import Path

source_root = Path.cwd()
fixture_root = Path(sys.argv[1])
shutil.copytree(source_root / "docs" / "portal", fixture_root / "docs" / "portal")
(fixture_root / "scripts").mkdir(parents=True)
shutil.copy2(source_root / "scripts" / "build-docs-portal.py", fixture_root / "scripts" / "build-docs-portal.py")
shutil.copy2(source_root / "scripts" / "check-docs-portal.py", fixture_root / "scripts" / "check-docs-portal.py")

site_path = fixture_root / "docs" / "portal" / "site.json"
site = json.loads(site_path.read_text(encoding="utf-8"))
rel_sources = set(site.get("semantic_sources", []))
for page in site["pages"].values():
    rel_sources.update(page.get("sources", []))
rel_sources.update({
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "package/implementaudit-package.json",
})
for rel in rel_sources:
    source = source_root / rel
    target = fixture_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

site["release"]["milestone"] = "v0.4.0.0"
site["release"]["manifest_version"] = "0.4.0"
site["release"]["publication_state"] = "published"
site["release"]["status"] = "v0.4.0.0 is published and independently read back"
site["release"]["audit_ledger_url"] = (
    "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/"
    "docs/audits/archive/v0.4.0.0-release-report.md"
)
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
valid = subprocess.run(
    [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert valid.returncode == 0, valid.stderr
metadata = json.loads((fixture_root / "dist" / "docs-portal" / "docs-metadata.json").read_text(encoding="utf-8"))
assert metadata["project_milestone"] == "v0.4.0.0", metadata["project_milestone"]
assert metadata["package_identity"]["required_skills"] == [
    "implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"
]
for owner in (
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "package/implementaudit-package.json",
):
    assert owner in metadata["source_files_used"]
    assert owner in metadata["source_sha256s"]

def run_build():
    return subprocess.run(
        [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def run_check():
    return subprocess.run(
        [sys.executable, str(fixture_root / "scripts" / "check-docs-portal.py"), str(fixture_root / "dist" / "docs-portal")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

codex_path = fixture_root / ".codex-plugin" / "plugin.json"
claude_path = fixture_root / ".claude-plugin" / "plugin.json"
codex = json.loads(codex_path.read_text(encoding="utf-8"))
claude = json.loads(claude_path.read_text(encoding="utf-8"))
assert "interface" in codex
assert "interface" not in claude

codex["codex_only_heldout"] = {"allowed": True}
codex_path.write_text(json.dumps(codex) + "\n", encoding="utf-8")
codex_extension = run_build()
assert codex_extension.returncode == 0, codex_extension.stderr
codex_extension_check = run_check()
assert codex_extension_check.returncode == 0, codex_extension_check.stderr
shutil.copy2(source_root / ".codex-plugin" / "plugin.json", codex_path)

claude["claude_only_heldout"] = {"allowed": True}
claude_path.write_text(json.dumps(claude) + "\n", encoding="utf-8")
claude_extension = run_build()
assert claude_extension.returncode == 0, claude_extension.stderr
claude_extension_check = run_check()
assert claude_extension_check.returncode == 0, claude_extension_check.stderr
shutil.copy2(source_root / ".claude-plugin" / "plugin.json", claude_path)

published_status = site["release"]["status"]
site["release"]["status"] = "v0.4.0.0 is the candidate public identity"
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
wrong_publication_status = run_build()
assert wrong_publication_status.returncode != 0
assert "published release status must describe published current truth" in wrong_publication_status.stderr
site["release"]["status"] = published_status
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")

codex = json.loads(codex_path.read_text(encoding="utf-8"))
codex["version"] = "9.9.9"
codex_path.write_text(json.dumps(codex) + "\n", encoding="utf-8")
host_drift = run_build()
assert host_drift.returncode != 0
assert "Codex and Claude plugin manifests must preserve equal shared semantics" in host_drift.stderr
shutil.copy2(source_root / ".codex-plugin" / "plugin.json", codex_path)

contract_path = fixture_root / "package" / "implementaudit-package.json"
contract = json.loads(contract_path.read_text(encoding="utf-8"))
contract["runtime_version"] = "9.9.9"
contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
contract_drift = run_build()
assert contract_drift.returncode != 0
assert "package contract runtime version" in contract_drift.stderr
shutil.copy2(source_root / "package" / "implementaudit-package.json", contract_path)

site["release"]["milestone"] = "v0.4.1.0"
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
wrong_family = subprocess.run(
    [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert wrong_family.returncode != 0
assert "does not belong to runtime family 0.4.0" in wrong_family.stderr

site["release"]["milestone"] = "v0.4.0.0"
site["release"]["audit_ledger_url"] = (
    "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/"
    "docs/audits/archive/v0.3.3.3-release-report.md"
)
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
stale_ledger = subprocess.run(
    [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert stale_ledger.returncode != 0, "generator accepted a v0.3.3.3 audit ledger for v0.4.0.0"
assert "must name a non-placeholder v0.4.0.0 markdown ledger" in stale_ledger.stderr

site["release"]["audit_ledger_url"] = "unknown"
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
placeholder_ledger = subprocess.run(
    [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert placeholder_ledger.returncode != 0, "generator accepted a placeholder audit ledger"
assert "must name a non-placeholder v0.4.0.0 markdown ledger" in placeholder_ledger.stderr

site["release"]["audit_ledger_url"] = (
    "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/"
    "docs/audits/archive/placeholder-v0.4.0.0-TBD.md"
)
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
exact_tag_placeholder_ledger = subprocess.run(
    [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert exact_tag_placeholder_ledger.returncode != 0, (
    "generator accepted placeholder-v0.4.0.0-TBD.md instead of the canonical ledger basename"
)
assert "must name a non-placeholder v0.4.0.0 markdown ledger" in exact_tag_placeholder_ledger.stderr

site["release"]["audit_ledger_url"] = (
    "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/"
    "docs/audits/archive/v0.4.0.00-release-report.md"
)
site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
prefix_collision_ledger = subprocess.run(
    [sys.executable, str(fixture_root / "scripts" / "build-docs-portal.py"), "--out", str(fixture_root / "dist" / "docs-portal")],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert prefix_collision_ledger.returncode != 0, "generator accepted a v0.4.0.00 ledger for v0.4.0.0"
assert "must name a non-placeholder v0.4.0.0 markdown ledger" in prefix_collision_ledger.stderr
PY
then
  ok "explicit portal milestone and matching non-placeholder ledger control release metadata"
else
  fail_check "portal release milestone, runtime-family, or audit-ledger validation failed"
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

if "${py_cmd[@]}" - "$out" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
meta = json.loads((root / "docs-metadata.json").read_text(encoding="utf-8"))
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
    "bash scripts/write-release-checksums.sh --check --all dist dist/CHECKSUMS.txt",
    "IMPLEMENTAUDIT.plugin.zip",
    "package/implementaudit-package.json",
    ".codex-plugin/plugin.json",
    "exactly four child skills",
    "audit-implement",
    "audit-andon",
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit(f"missing parity concepts: {missing}")
required_patterns = [
    r"IMPLEMENTAUDIT\.skill/(?:<br>|\s+)SKILL\.md",
    r"IMPLEMENTAUDIT\.plugin\.zip/(?:<br>|\s+)\.codex-plugin/plugin\.json",
]
missing_patterns = [pattern for pattern in required_patterns if not re.search(pattern, html, re.IGNORECASE)]
if missing_patterns:
    raise SystemExit(f"missing parity concept patterns: {missing_patterns}")
if "IMPLEMENTAUDIT.skill/<br>skills/implementaudit/SKILL.md" in html:
    raise SystemExit("stale nested package tree returned")
PY
then
  ok "v2 parity concepts exceed legacy reference density"
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

cp -R "$out" "$bad_release_label"
"${py_cmd[@]}" - "$bad_release_label" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    text = text.replace("<dt>Release</dt>", "<dt>Candidate release</dt>")
    text = text.replace("<em>Release</em>", "<em>Candidate release</em>")
    path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_release_label" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted a candidate label for published output"
else
  ok "check-docs-portal.py rejects a candidate label for published output"
fi

cp -R "$out" "$bad_overview_release"
"${py_cmd[@]}" - "$bad_overview_release/index.html" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
current_ledger = json.loads(Path("docs/portal/site.json").read_text(encoding="utf-8"))["release"]["audit_ledger_url"]
assert current_ledger in text
text = text.replace(
    current_ledger,
    "https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/main/docs/audits/archive/v0.2.9.0-andon-escalation-jidoka-repair.md",
)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_overview_release" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted stale overview release evidence link"
else
  ok "check-docs-portal.py rejects stale overview release evidence link"
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

cp -R "$out" "$bad_stage_sequence"
"${py_cmd[@]}" - "$bad_stage_sequence/reference/planning-and-phases/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = 'data-label="Stage">6.i</td>'
assert old in text
path.write_text(text.replace(old, 'data-label="Stage">6.x</td>', 1), encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_stage_sequence" >/dev/null 2>&1; then
  fail_check "checker accepted portal with missing Stage 6.i enumeration"
else
  ok "checker rejects portal with missing Stage 6.i enumeration"
fi

cp -R "$out" "$bad_sidecar_freshness"
"${py_cmd[@]}" - "$bad_sidecar_freshness/reference/continuity-and-sidecars/index.html" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("built_at_commit", "recorded freshness", 1)
text = text.replace("stale-sidecar", "stale terrain", 1)
path.write_text(text, encoding="utf-8")
PY
if "${py_cmd[@]}" scripts/check-docs-portal.py "$bad_sidecar_freshness" >/dev/null 2>&1; then
  fail_check "check-docs-portal.py accepted hand-judged sidecar freshness"
else
  ok "check-docs-portal.py rejects hand-judged sidecar freshness"
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
    text = text.replace("${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}/scripts/", "skills/implementaudit/scripts/")
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
if bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  ok "check-public-claim-boundaries.sh allows negative local install update context"
else
  fail_check "check-public-claim-boundaries.sh rejected negative local install update context"
fi

if grep -Fq 'S³E held-out source mutation false-passed' \
     scripts/check-public-claim-boundaries.sh &&
   bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  ok "public-claim acceptance guards S³E title/no-mode/cheap-path held-outs"
else
  fail_check "public-claim acceptance lacks S³E source-coupled held-outs"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

Path(sys.argv[1]).write_text("This package " + "auto-" + "updates from a host.\n", encoding="utf-8")
PY
if bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  fail_check "check-public-claim-boundaries.sh accepted a positive host update claim"
else
  ok "check-public-claim-boundaries.sh rejects positive host update claims"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

stale = (
    "The last release-gate verified live public release "
    "remains `v0.2.9.0`; source changes are not a release by themselves.\n"
)
Path(sys.argv[1]).write_text(stale, encoding="utf-8")
PY
if bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  fail_check "check-public-claim-boundaries.sh accepted a stale current-release claim"
else
  ok "check-public-claim-boundaries.sh rejects stale current-release claims"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

stale = (
    "The current release-gate-verified public release is `v0.3.3" + ".0`, "
    "with plugin/runtime version `0.3.3`.\n"
)
Path(sys.argv[1]).write_text(stale, encoding="utf-8")
PY
if bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  fail_check "check-public-claim-boundaries.sh accepted the superseded v0.3.3.0 current-release claim"
else
  ok "check-public-claim-boundaries.sh rejects the superseded v0.3.3.0 current-release claim"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(
    "R0024 / #167 remains open and was not "
    + "shipped or qualified in this release.\n",
    encoding="utf-8",
)
PY
if bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  fail_check "check-public-claim-boundaries.sh accepted the stale pre-R0024 release claim"
else
  ok "check-public-claim-boundaries.sh rejects the stale pre-R0024 release claim"
fi

if "${py_cmd[@]}" - <<'PY'
from pathlib import Path

text = " ".join(Path("CONTRIBUTING.md").read_text(encoding="utf-8").split())
raise SystemExit(0 if "An in-place correction requires explicit owner authority" in text else 1)
PY
then
  ok "CONTRIBUTING.md states the bounded same-identity correction authority"
else
  fail_check "CONTRIBUTING.md is missing the bounded same-identity correction authority"
fi

"${py_cmd[@]}" - "$host_claim_fixture" <<'PY'
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(
    "Do not replace bytes under an already-" + "published tag. "
    "Correct forward under a fresh identity.\n",
    encoding="utf-8",
)
PY
if bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1; then
  fail_check "check-public-claim-boundaries.sh accepted an absolute forward-only release policy"
else
  ok "check-public-claim-boundaries.sh rejects an absolute forward-only release policy"
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
