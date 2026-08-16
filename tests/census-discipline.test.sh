#!/usr/bin/env bash
# census-discipline.test.sh - issue #79 deterministic controls
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fixture="fixtures/census-discipline/cases.json"
public_projection_fixture="fixtures/public-projection/cases.json"
semantic_fixture="fixtures/public-projection/semantic-preservation.json"
lineage_fixture="fixtures/public-projection/lineage-reader-questions.json"
base="fixtures/phase-validation/valid-full-spec.md"
eval_fixture="eval/fixtures/E5d-census-discipline"
r29_eval_fixture="eval/fixtures/R001D-public-projection"
r29_dogfood_input="fixtures/public-projection/installed-dogfood-input.json"
checker="scripts/check-census-discipline.sh"
pass=0
fail=0

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'census-discipline.test: Python is required\n' >&2
  exit 2
fi

record_pass() {
  pass=$((pass + 1))
}

record_fail() {
  printf 'census-discipline.test: %s\n' "$1" >&2
  fail=$((fail + 1))
}

if [ -f "$checker" ] && bash "$checker" "$fixture"; then
  record_pass
else
  record_fail "deterministic checker is missing or rejected R6-F1..R6-F11"
fi

if [ -f "$public_projection_fixture" ] &&
   bash "$checker" "$public_projection_fixture"; then
  record_pass
else
  record_fail "reused census checker rejected R29-F1..R29-F39"
fi

# Source-coupled S³E held-outs: changing a public owner and the declarative
# fixture together must still fail against independent checker anchors.
s3e_source_coupling_ok=true
for mutation in canonical-title no-methodology-mode cheap-path package-projection; do
  root="$tmp/s3e-source-coupling-$mutation"
  mkdir -p "$root/scripts" "$root/fixtures/public-projection" "$root/docs/portal/pages"
  cp "$checker" "$root/scripts/check-census-discipline.sh"
  cp "$public_projection_fixture" "$root/fixtures/public-projection/cases.json"
  cp docs/portal/pages/research-lineage-s3e.html "$root/docs/portal/pages/"
  cp docs/portal/pages/research-lineage-evolved-css.html "$root/docs/portal/pages/"
  "${py_cmd[@]}" - "$root" "$mutation" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
mutation = sys.argv[2]
bank_path = root / "fixtures/public-projection/cases.json"
bank = json.loads(bank_path.read_text(encoding="utf-8"))
by_id = {row["id"]: row for row in bank["controls"]}
s3e = root / "docs/portal/pages/research-lineage-s3e.html"
css = root / "docs/portal/pages/research-lineage-evolved-css.html"
if mutation == "canonical-title":
    s3e.write_text(s3e.read_text(encoding="utf-8").replace(
        "State Synthesis Substrate Engineering: Evolved-SSDDRFCSS",
        "State System Substrate Engineering: Evolved-SSDDRFCSS"), encoding="utf-8")
    by_id["S3E-W04-F1"]["public_copy"] = by_id["S3E-W04-F1"]["public_copy"].replace(
        "State Synthesis", "State System")
elif mutation == "no-methodology-mode":
    s3e.write_text(s3e.read_text(encoding="utf-8").replace(
        "They do not create nine runtimes, selectable methodology modes, or a fixed ceremony.",
        "They create nine runtimes, selectable methodology modes, and a fixed ceremony."), encoding="utf-8")
    for field in ("readme_wording", "docs_wording"):
        by_id["S3E-W04-F2"][field] = "The lineage families create selectable methodology modes."
    by_id["S3E-W04-F2"]["readme_facts"] = ["selectable-methodology-modes"]
    by_id["S3E-W04-F2"]["docs_facts"] = ["selectable-methodology-modes"]
elif mutation == "cheap-path":
    css.write_text(css.read_text(encoding="utf-8").replace(
        "When one authoritative deterministic discriminator settles ordinary bounded work, use it and stop. No trigger means no added ceremony, record, or family machinery.",
        "Every bounded task requires added lineage ceremony, records, and family machinery."), encoding="utf-8")
    for field in ("readme_wording", "docs_wording"):
        by_id["S3E-W04-F2"][field] = "Every bounded task requires lineage ceremony."
    by_id["S3E-W04-F2"]["readme_facts"] = ["ceremony-required"]
    by_id["S3E-W04-F2"]["docs_facts"] = ["ceremony-required"]
else:
    s3e.write_text(s3e.read_text(encoding="utf-8").replace(
        "The canonical plugin and standalone compatibility projections are mechanically checked independently; they are not literal member-for-member copies.",
        "The two projections are interchangeable and have identical members."), encoding="utf-8")
    for field in ("readme_wording", "docs_wording"):
        by_id["S3E-W04-F4"][field] = "The two projections are interchangeable and have identical members."
    by_id["S3E-W04-F4"]["readme_facts"] = ["identical-members"]
    by_id["S3E-W04-F4"]["docs_facts"] = ["identical-members"]
bank_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
  if (cd "$root" && bash scripts/check-census-discipline.sh fixtures/public-projection/cases.json >/dev/null 2>&1); then
    record_fail "source-coupled $mutation corruption false-passed the public census checker"
    s3e_source_coupling_ok=false
  fi
done
if [ "$s3e_source_coupling_ok" = true ]; then
  record_pass
fi

# Bind the S³E projection semantics to freshly built artifact bytes rather than
# a synchronized prose/fixture count. Member totals may evolve; these semantic
# distinctions must not.
projection_out="$tmp/current-package-projections"
if bash scripts/build-release-asset.sh "$projection_out" >/dev/null &&
   "${py_cmd[@]}" - "$projection_out/IMPLEMENTAUDIT.plugin.zip" \
     "$projection_out/IMPLEMENTAUDIT.skill" <<'PY'
import sys
import zipfile

plugin_path, standalone_path = sys.argv[1:]
with zipfile.ZipFile(plugin_path) as archive:
    plugin = {name for name in archive.namelist() if not name.endswith("/")}
with zipfile.ZipFile(standalone_path) as archive:
    standalone = {name for name in archive.namelist() if not name.endswith("/")}

plugin_manifests = {
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
}
plugin_skills = {
    "skills/implementaudit/SKILL.md",
    "skills/audit-state/SKILL.md",
    "skills/audit-assess/SKILL.md",
    "skills/audit-implement/SKILL.md",
    "skills/audit-andon/SKILL.md",
}
standalone_children = {
    "internal-procedures/audit-state.md",
    "internal-procedures/audit-assess.md",
    "internal-procedures/audit-implement.md",
    "internal-procedures/audit-andon.md",
}
if not plugin_manifests <= plugin:
    raise SystemExit("canonical plugin lost dual-host manifest population")
if not plugin_skills <= plugin:
    raise SystemExit("canonical plugin lost governor/four-child skill population")
if any(name.startswith(".claude-plugin/") for name in standalone):
    raise SystemExit("standalone compatibility projection retained plugin manifests")
if "SKILL.md" not in standalone or not standalone_children <= standalone:
    raise SystemExit("standalone projection lost governor/four internal procedures")
if plugin == standalone:
    raise SystemExit("canonical and standalone projections became identical")
PY
then
  record_pass
else
  record_fail "fresh artifact projection semantics are not mechanically bound"
fi

# Package-pressure compaction once weakened the omission assertion to generic
# overclaim/omission wording. R0021/R0023 review rejected that evaluator mutation;
# keep the material owner-sourced omission predicate exact here.
if grep -Fq "### Public capability projection" \
     skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '| Topic | Audience/job | Authority and placements | Abstraction/route | Current-state transition | Evidence |' \
     skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '`prepublication-current`' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '`postpublication-current`' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '`stale`' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq 'rendered-consumer' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq 'governed-detail preservation' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq 'source/generator green' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq 'Ordinary prose' skills/implementaudit/references/audit-playbook.md &&
   grep -Fq '"kind": "rendered-consumer-boundary"' \
     fixtures/public-projection/cases.json &&
   grep -Fq 'material owner-sourced capabilities omitted' \
     skills/implementaudit/SKILL.md &&
   grep -Fq 'audience/authority/abstraction mismatch' skills/implementaudit/SKILL.md &&
   grep -Fq 'Public projection challenge: overclaim / omission / audience-owner-abstraction mismatch / duplicate authority / hidden route / not applicable with owner evidence' \
     fixtures/child-agents/read-only-contract-auditor.md &&
   grep -Fq '## Public Capability Projection (when activated)' \
     skills/implementaudit/templates/final-report.md &&
   grep -Fq '| Topic | Audience/job | Authority and placements | Abstraction/route | Current-state transition | Evidence |' \
     skills/implementaudit/templates/final-report.md; then
  record_pass
else
  record_fail "public-projection runtime, reviewer, or report owner is incomplete"
fi

if "${py_cmd[@]}" - "$semantic_fixture" <<'PY'
import json
import sys
from pathlib import Path

bank = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if set(bank) != {"schema", "bindings"} or bank["schema"] != \
        "implementaudit-public-projection-semantic-preservation-v1":
    raise SystemExit("semantic-preservation schema invalid")
bindings = bank["bindings"]
if not bindings or len({row["id"] for row in bindings}) != len(bindings):
    raise SystemExit("semantic-preservation bindings invalid")

def contains_all(path, tokens, override=None):
    text = override if override is not None else Path(path).read_text(encoding="utf-8")
    return all(token in text for token in tokens)

for row in bindings:
    if not contains_all(row["projection_owner"], row["projection_tokens"]):
        raise SystemExit(f"{row['id']}: projection owner lost a predicate")
    for owner in row["canonical_owners"]:
        if not contains_all(owner["path"], owner["tokens"]):
            raise SystemExit(f"{row['id']}: canonical owner lost a predicate")
        original = Path(owner["path"]).read_text(encoding="utf-8")
        held_out = original.replace(owner["tokens"][0], "")
        if contains_all(owner["path"], owner["tokens"], held_out):
            raise SystemExit(f"{row['id']}: held-out owner mutation false-passed")
    consumer = row["consumer"]
    if not contains_all(consumer["path"], consumer["tokens"]):
        raise SystemExit(f"{row['id']}: reachable consumer binding missing")
PY
then
  record_pass
else
  record_fail "package semantic-preservation owner/consumer binding failed"
fi

# Bind each owner-supplied reader question to a named public owner and a small
# evidence set.  The existing R001D positive/negative/cheap/held-out controls
# remain the generic semantic discriminator; this cell owns lineage routing,
# classifications, non-claims, and native-control distinctions.
if "${py_cmd[@]}" - "$lineage_fixture" <<'PY'
import json
import sys
from pathlib import Path

fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
site = json.loads(Path("docs/portal/site.json").read_text(encoding="utf-8"))

if fixture.get("schema") != "implementaudit-research-lineage-reader-questions-v2":
    raise SystemExit("lineage reader-question schema invalid")
questions = fixture.get("questions", [])
if len(questions) != 23 or len({row.get("id") for row in questions}) != 23:
    raise SystemExit("lineage reader-question population must be exactly twenty-three unique owner questions")
if [row.get("id") for row in questions] != [f"R29-LQ{i}" for i in range(1, 24)]:
    raise SystemExit("lineage reader-question identity/order drift")

groups = [group.get("group") for group in site.get("nav", [])]
if "Research & Engineering Lineage" not in groups:
    raise SystemExit("lineage navigation group missing")
if groups.index("Research & Engineering Lineage") != groups.index("Repository") + 1:
    raise SystemExit("lineage navigation must sit between Repository and References")
lineage_group = next(group for group in site["nav"]
                     if group.get("group") == "Research & Engineering Lineage")
if lineage_group.get("pages") != fixture.get("public_pages"):
    raise SystemExit("lineage page order/denominator drift")

page_text = {}
for page_id in fixture["public_pages"]:
    page = site.get("pages", {}).get(page_id)
    if not page:
        raise SystemExit(f"lineage page missing from site owner: {page_id}")
    source = Path("docs/portal/pages") / page["source"]
    if not source.is_file():
        raise SystemExit(f"lineage source missing: {source}")
    page_text[page_id] = source.read_text(encoding="utf-8")

for row in questions:
    text = page_text[row["page"]]
    missing = [token for token in row["evidence"] if token not in text]
    if missing:
        raise SystemExit(f"{row['id']}: reader answer missing {missing}")

contract = fixture.get("first_reader_contract", {})
section_ids = contract.get("section_ids")
if section_ids != ["contribution", "changed", "already-native", "rejected", "unverified", "provenance"]:
    raise SystemExit("lineage first-reader section order drift")
individual_pages = contract.get("individual_pages", [])
if len(individual_pages) != 9 or len({row.get("page") for row in individual_pages}) != 9:
    raise SystemExit("lineage individual-page population must be exactly nine")
if [row.get("review_tier") for row in individual_pages].count("cold-review") != 3:
    raise SystemExit("lineage cold-review population must be exactly three")
if [row.get("review_tier") for row in individual_pages].count("shared-template-census") != 6:
    raise SystemExit("lineage shared-template census population must be exactly six")
for row in individual_pages:
    page = site["pages"].get(row["page"], {})
    if page.get("title") != row["title"] or page.get("path") != row["route"]:
        raise SystemExit(f"{row['page']}: title or route drift")
    text = page_text[row["page"]]
    positions = [text.find(f'id="{section_id}"') for section_id in section_ids]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise SystemExit(f"{row['page']}: first-reader section population/order drift")
    visible = __import__("re").sub(r"<[^>]+>", " ", text)
    if len(visible.split()) < contract["minimum_visible_words"]:
        raise SystemExit(f"{row['page']}: substantive first-reader content is too short")

def held_out_failures(candidate_site, candidate_text):
    failures = set()
    lineage_pages = next(
        (group.get("pages") for group in candidate_site.get("nav", [])
         if group.get("group") == "Research & Engineering Lineage"), None)
    if lineage_pages != fixture["public_pages"]:
        failures.add("nav-population")
    for row in individual_pages:
        page = candidate_site.get("pages", {}).get(row["page"])
        if not page:
            failures.add("page-owner-population")
            continue
        text = candidate_text.get(row["page"], "")
        positions = [text.find(f'id="{section_id}"') for section_id in section_ids]
        visible = __import__("re").sub(r"<[^>]+>", " ", text)
        if (any(position < 0 for position in positions)
                or positions != sorted(positions)
                or len(visible.split()) < contract["minimum_visible_words"]):
            failures.add("first-reader-substance")
    return failures

import copy
nav_mutant = copy.deepcopy(site)
next(group for group in nav_mutant["nav"]
     if group["group"] == "Research & Engineering Lineage")["pages"].pop(5)
if "nav-population" not in held_out_failures(nav_mutant, page_text):
    raise SystemExit("held-out missing lineage nav member false-passed")
page_mutant = copy.deepcopy(site)
page_mutant["pages"].pop(individual_pages[0]["page"])
if "page-owner-population" not in held_out_failures(page_mutant, page_text):
    raise SystemExit("held-out missing lineage page owner false-passed")
text_mutant = dict(page_text)
text_mutant[individual_pages[0]["page"]] = "<h1>Collapsed lineage page</h1>"
if "first-reader-substance" not in held_out_failures(site, text_mutant):
    raise SystemExit("held-out collapsed lineage prose false-passed")

synthesis = page_text["research-lineage-evolved-law"]
for literal in fixture["classification_literals"]:
    if literal not in synthesis:
        raise SystemExit(f"lineage synthesis missing classification {literal}")
for issue in ("R0025 / #186", "R0026 / #187", "R0027 / #188"):
    if issue not in synthesis:
        raise SystemExit(f"lineage synthesis missing evidence owner {issue}")

combined = "\n".join(page_text.values())
for forbidden in ("Semantica", "Semantica-main", "three methodology modes"):
    if forbidden in combined:
        raise SystemExit(f"internal comparative branding leaked publicly: {forbidden}")
for boundary in (
        "non-cooperating same-principal writer",
        "work-conserving",
        "shared issue, milestone, branch train, eventual package, or public surface is not itself a dependency",
        "not universally validated"):
    if boundary not in combined:
        raise SystemExit(f"lineage public boundary missing: {boundary}")

readme = Path("README.md").read_text(encoding="utf-8")
changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
report = Path("docs/audits/archive/v0.4.0.0-release-report.md").read_text(encoding="utf-8")
title = fixture["release_title"]
if title not in changelog or title not in report:
    raise SystemExit("S³E canonical release title is not owned by changelog/report")
if "Research & Engineering Lineage" not in readme:
    raise SystemExit("README does not route readers to lineage owners")
lineage_hosted_route = (
    "https://theislampill.github.io/IMPLEMENTAUDIT.md/"
    "research-engineering-lineage/"
)
lineage_source_route = "docs/portal/pages/research-lineage-overview.html"
lineage_pending = (
    "This source entry does not claim that the hosted portal or GitHub release "
    "body contains the new projection until a separate publication and "
    "readback gate records that state"
)
if lineage_pending in " ".join(changelog.split()):
    if lineage_hosted_route in readme:
        raise SystemExit("README preclaims the pending hosted lineage route")
    if lineage_source_route not in readme:
        raise SystemExit("README does not route pending lineage readers to repository source")
if fixture["compact_label"] not in page_text["research-lineage-s3e"]:
    raise SystemExit("protected S³E label missing from synthesis")
if "Semantica" in readme + changelog + report:
    raise SystemExit("internal comparative corpus branding leaked to public owners")

unreleased = changelog.split("## [Unreleased]", 1)[1].split("\n## [", 1)[0]
for forbidden in (
    "/improve",
    "63-property comparator",
    "source-stronger",
    "reverse-dominance",
    "strict superset",
):
    if forbidden in unreleased.casefold():
        raise SystemExit(
            f"internal comparison framing leaked into active public projection: {forbidden}"
        )
PY
then
  record_pass
else
  record_fail "R001D twenty-three-question research-lineage comprehension contract failed"
fi

# Bind the repaired repository projection as a positive example without
# prescribing a README template, section count, or length.  The reusable
# fixture bank above owns the generic classification; this cell proves that a
# substantial, diagram-rich README can pass while contributor procedure,
# chronology, and exact release evidence retain distinct discoverable owners.
if "${py_cmd[@]}" - <<'PY'
import json
from pathlib import Path

readme = Path("README.md").read_text(encoding="utf-8")
contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
site = json.loads(Path("docs/portal/site.json").read_text(encoding="utf-8"))
diagrams = {
    path.name: path.read_text(encoding="utf-8")
    for path in Path("docs/diagrams").glob("*.mmd")
}

def projection_fits(readme_text, contributing_text, site_data, diagram_texts):
    readme_routes = (
        "[`CONTRIBUTING.md`](CONTRIBUTING.md)",
        "[`CHANGELOG.md`](CHANGELOG.md)",
        "[`v0.4.0.0` release report](docs/audits/archive/v0.4.0.0-release-report.md)",
        "[`docs portal`](https://theislampill.github.io/IMPLEMENTAUDIT.md/)",
    )
    readme_model = (
        "reusable meta-engineering",
        "skills-about-skills",
        "## Why IMPLEMENTAUDIT is stronger than a bare `/goal`",
        "## Invocation modes",
        "## Evidence boundaries",
        "## Install notes",
        "Graphify output is orientation evidence, not proof",
        "ActiveGraph custody is not correctness proof",
    )
    contributor_contract = (
        "## Canonical and generated owners",
        "## Environment and file discipline",
        "## Implementation and validation flow",
        "## Review, commits and public mutations",
        "bash scripts/generate-readme-diagrams.sh --check",
        "bash scripts/verify-docs-portal.sh",
    )
    diagram_contract = (
        "tooling-architecture.mmd",
        "invocation-modes.mmd",
        "execution-spine.mmd",
    )
    def github_readme_diagram_fits(source):
        first_line = next(
            (line.strip() for line in source.splitlines() if line.strip()), "")
        return (
            not any(tag in source for tag in (
                "<br", "<span", "</span", "<div", "</div", "<p", "</p"))
            and first_line in ("flowchart TB", "flowchart TD")
        )
    return (
        all(token in readme_text for token in readme_routes + readme_model)
        and "OWNER_ACCEPTED_PARTIAL" not in readme_text
        and "v0.3.3.3 candidate countermeasures" not in readme_text
        and all(token in contributing_text for token in contributor_contract)
        and "Current contract essentials (v0.3.0.0 line)" not in contributing_text
        and "CONTRIBUTING.md" in site_data.get("semantic_sources", [])
        and all(name in diagram_texts for name in diagram_contract)
        and all(github_readme_diagram_fits(diagram_texts[name])
                for name in diagram_contract)
        and all("authoritative" in diagram_texts[name].lower()
                or "authority" in diagram_texts[name].lower()
                or "evidence" in diagram_texts[name].lower()
                for name in diagram_contract)
    )

if not projection_fits(readme, contributing, site, diagrams):
    raise SystemExit("current substantial public projection is not audience/owner fit")

mutations = {
    "missing-contributor-route": (
        readme.replace("[`CONTRIBUTING.md`](CONTRIBUTING.md)", "CONTRIBUTING"),
        contributing, site, diagrams),
    "campaign-jargon-in-onboarding": (
        readme + "\nOWNER_ACCEPTED_PARTIAL\n", contributing, site, diagrams),
    "stale-contributor-authority": (
        readme,
        contributing + "\nCurrent contract essentials (v0.3.0.0 line)\n",
        site, diagrams),
    "missing-portal-owner": (
        readme, contributing,
        {**site, "semantic_sources": [
            value for value in site.get("semantic_sources", [])
            if value != "CONTRIBUTING.md"]},
        diagrams),
    "github-collapsed-self-closing-breaks": (
        readme, contributing, site,
        {**diagrams, "invocation-modes.mmd":
            diagrams["invocation-modes.mmd"] +
            '\n  Broken["left<br/>right"]\n'}),
    "github-html-wrapper-label-layout": (
        readme, contributing, site,
        {**diagrams, "invocation-modes.mmd":
            diagrams["invocation-modes.mmd"] +
            '\n  Broken["<span>left right</span>"]\n'}),
    "github-overwide-horizontal-public-diagram": (
        readme, contributing, site,
        {**diagrams, "tooling-architecture.mmd":
            diagrams["tooling-architecture.mmd"].replace(
                "flowchart TB", "flowchart LR", 1)}),
}
for name, values in mutations.items():
    if projection_fits(*values):
        raise SystemExit(f"current public projection accepted {name}")
PY
then
  record_pass
else
  record_fail "current substantial README/contributor projection binding failed"
fi

case_ids="$("${py_cmd[@]}" - "$fixture" <<'PY'
import json
import sys
from pathlib import Path

fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for case in fixture["phase_cases"]:
    print(case["id"])
PY
)" || {
  record_fail "could not enumerate phase cases"
  case_ids=""
}

while IFS= read -r case_id; do
  case_id="${case_id//$'\r'/}"
  [ -n "$case_id" ] || continue
  spec="$tmp/$case_id.md"
  meta="$tmp/$case_id.meta"
  "${py_cmd[@]}" - "$fixture" "$base" "$case_id" "$spec" "$meta" <<'PY'
import json
import sys
from pathlib import Path

fixture_path, base_path, case_id, output_path, meta_path = sys.argv[1:]
fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
case = next(row for row in fixture["phase_cases"] if row["id"] == case_id)
lines = Path(base_path).read_text(encoding="utf-8").splitlines()
start = next(i for i, line in enumerate(lines)
             if line.startswith("## Evidence required"))
end = next(i for i in range(start + 1, len(lines))
           if lines[i].startswith("## "))
body = [lines[start], ""] + case["evidence"] + [""]
Path(output_path).write_text(
    "\n".join(lines[:start] + body + lines[end:]) + "\n",
    encoding="utf-8", newline="\n")
Path(meta_path).write_text(
    case["expected"] + "\n" + case.get("diagnostic", "") + "\n",
    encoding="utf-8", newline="\n")
PY
  expected="$(sed -n '1p' "$meta")"
  diagnostic="$(sed -n '2p' "$meta")"
  out="$tmp/$case_id.out"
  bash skills/implementaudit/scripts/validate-phase.sh "$spec" >"$out" 2>&1
  status=$?
  if [ "$expected" = "PASS" ] && [ "$status" -eq 0 ]; then
    record_pass
  elif [ "$expected" = "FAIL" ] && [ "$status" -ne 0 ] &&
       grep -Fq "$diagnostic" "$out"; then
    record_pass
  else
    record_fail "$case_id expected $expected with diagnostic '$diagnostic'"
    cat "$out" >&2
  fi
done <<< "$case_ids"

if "${py_cmd[@]}" - "$eval_fixture" <<'PY'
import json
import sys
from pathlib import Path

fixture_dir = Path(sys.argv[1])
sys.path.insert(0, str(Path("eval/lib").resolve()))
import scoring

fixture = json.loads((fixture_dir / "fixture.json").read_text(encoding="utf-8"))
mission = fixture["mission"].casefold()
for phrase in ("population", "denominator", "census", "true count"):
    if phrase in mission:
        raise SystemExit(f"mission leaks forbidden phrase: {phrase}")
contract_phrases = {
    phrase.casefold()
    for field in fixture["matrix_instruction_contract"]["fields"]
    for phrase in field["forbidden_mission_phrases"]
}
if not {"population", "denominator", "census", "true count"} <= contract_phrases:
    raise SystemExit("P4-13 forbidden phrase set is incomplete")

def patterns(rule):
    if rule["kind"] in {"all_of", "any_of"}:
        for child in rule["rules"]:
            yield from patterns(child)
    elif "pattern" in rule:
        yield rule["pattern"]

for prop in fixture["properties"]:
    for pattern in patterns(prop["rule"]):
        if "|" in pattern:
            raise SystemExit("scoring uses a synonym/alternative list")

controls = json.loads((fixture_dir / "controls.json").read_text(encoding="utf-8"))
if [row["id"] for row in controls] != [
        "paraphrase-must-pass", "polarity-inversion-must-fail"]:
    raise SystemExit("paired controls are incomplete")
for row in controls:
    actual = scoring.overall(scoring.score(fixture, row["transcript"], {}), fixture)
    if actual is not row["expected_pass"]:
        raise SystemExit(f"{row['id']} scored {actual}")
PY
then
  record_pass
else
  record_fail "supplementary E5 metamorphic fixture contract failed"
fi

if "${py_cmd[@]}" - "$r29_eval_fixture" "$r29_dogfood_input" <<'PY'
import copy
import json
import sys
from pathlib import Path

fixture_dir, dogfood_path = map(Path, sys.argv[1:])
sys.path.insert(0, str(Path("eval/lib").resolve()))
import scoring

fixture = json.loads((fixture_dir / "fixture.json").read_text(encoding="utf-8"))
controls = json.loads((fixture_dir / "controls.json").read_text(encoding="utf-8"))
dogfood = json.loads(dogfood_path.read_text(encoding="utf-8"))
required_tuples = [
    ("ITEMS", "owner_topic_derivation", True, "contains",
     "^ITEMS=recovery-replay,offline-archive-install$",
     "recovery-replay,offline-archive-install",
     frozenset({"audit-sequencing", "none"}),
     frozenset({"projection", "population", "denominator",
                "recovery replay", "offline archive install"})),
    ("HISTORY", "historical_preservation", True, "contains",
     "^HISTORY=PRESERVE$", "PRESERVE", frozenset({"REWRITE", "DELETE"}),
     frozenset({"preserve the historical statement", "historical-intentional"})),
    ("GAPS", "omission_detection", True, "contains",
     "^GAPS=recovery-replay,offline-archive-install$",
     "recovery-replay,offline-archive-install",
     frozenset({"none", "cache-compaction"}),
     frozenset({"missing capability", "missing installation route",
                "recovery replay", "offline archive install"})),
    ("EDIT", "owner_source_correction", True, "contains",
     "^EDIT=OWNER_SOURCE$", "OWNER_SOURCE",
     frozenset({"GENERATED_OUTPUT", "NONE"}),
     frozenset({"owner source", "generated output"})),
    ("STATE", "postpublication_refusal", True, "contains",
     "^STATE=REFUSE$", "REFUSE", frozenset({"CLOSE"}),
     frozenset({"postpublication readback", "refuse closure"})),
    ("DETAIL", "concise_delegation", True, "contains",
     "^DETAIL=LEGAL$", "LEGAL", frozenset({"DUPLICATE"}),
     frozenset({"concise delegation", "discoverably delegated"})),
]
property_ids = {row[1] for row in required_tuples}


def validate_model_contract(candidate):
    if candidate.get("id") != "R29-public-projection":
        raise SystemExit("R001D model-cell identity invalid")
    mission = candidate.get("mission", "").casefold()
    fields = candidate.get("matrix_instruction_contract", {}).get("fields", [])
    properties = candidate.get("properties", [])
    if [row.get("field") for row in fields] != [row[0] for row in required_tuples]:
        raise SystemExit("R001D model-cell field identity set invalid")
    if [row.get("name") for row in properties] != [row[1] for row in required_tuples]:
        raise SystemExit("R001D model-cell scorer property set invalid")
    for field, prop, required in zip(fields, properties, required_tuples):
        label = required[0]
        distractors, forbidden = required[6:]
        actual = (
            field.get("field"), field.get("property"), prop.get("required"),
            prop.get("rule", {}).get("kind"), prop.get("rule", {}).get("pattern"),
            field.get("expected"), frozenset(field.get("distractors", [])),
            frozenset(field.get("forbidden_mission_phrases", [])))
        if (actual != required or prop.get("required") is not True or
                set(prop.get("rule", {})) != {"kind", "pattern"} or
                len(field.get("distractors", [])) != len(distractors) or
                len(field.get("forbidden_mission_phrases", [])) != len(forbidden)):
            raise SystemExit(f"{label}: exact acceptance tuple invalid")
        for phrase in forbidden:
            if phrase.casefold() in mission:
                raise SystemExit(f"R001D model-cell mission leaks forbidden phrase: {phrase}")
    for prop in properties:
        rule = prop.get("rule", {})
        patterns = [rule.get("pattern", "")]
        patterns += [child.get("pattern", "") for child in rule.get("rules", [])]
        if any("|" in pattern for pattern in patterns):
            raise SystemExit("R001D model-cell scorer uses a synonym list")


validate_model_contract(fixture)


def require_rejection(candidate, mutation):
    try:
        validate_model_contract(candidate)
    except SystemExit:
        return
    raise SystemExit(f"R001D model-cell accepted {mutation}")


for index, required in enumerate(required_tuples):
    label = required[0]
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["field"] += "_RENAMED"
    require_rejection(mutated, f"renamed field {label}")
    mutated = copy.deepcopy(fixture)
    del mutated["properties"][index]
    require_rejection(mutated, f"removal of {label} property")
    mutated = copy.deepcopy(fixture)
    mutated["properties"][index]["required"] = False
    require_rejection(mutated, f"optional {label} property")
    mutated = copy.deepcopy(fixture)
    mutated["properties"][index]["required"] = 1
    require_rejection(mutated, f"integer-true {label} property")
    mutated = copy.deepcopy(fixture)
    mutated["properties"][index]["rule"] = {"kind": "contains", "pattern": ".*"}
    require_rejection(mutated, f"permissive {label} rule")
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["expected"] += "-renamed"
    require_rejection(mutated, f"replaced {label} expected value")
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["distractors"].pop()
    require_rejection(mutated, f"removed {label} distractor")
    mutated = copy.deepcopy(fixture)
    mutated["matrix_instruction_contract"]["fields"][index]["distractors"][0] += "-renamed"
    require_rejection(mutated, f"replaced {label} distractor")
    for phrase in required[7]:
        mutated = copy.deepcopy(fixture)
        forbidden = mutated["matrix_instruction_contract"]["fields"][index][
            "forbidden_mission_phrases"]
        forbidden.remove(phrase)
        require_rejection(mutated, f"removal of {label} phrase {phrase}")
        forbidden.append(f"{phrase} renamed")
        require_rejection(mutated, f"replacement of {label} phrase {phrase}")

properties = fixture["properties"]

base_seed = {
    "runtime/public-method.md": "Supported user-facing behaviours: audit sequencing; recovery replay.",
    "install/routes.json": "{\"supported\":[\"package manager\",\"offline archive install\"]}",
    "release/state.json": "{\"phase\":\"prepublication\",\"required_next\":\"published-route readback\"}",
    "README.md": "The tool sequences an audit. Details: docs/public-guide.md.",
    "docs/public-guide.md": "The public guide explains audit sequencing. Historical: release-1 retains alias old-runner for host 6.2.",
    "docs/generated.txt": "The public guide explains audit sequencing. Historical: release-1 retains alias old-runner for host 6.2.",
    "docs/generated-owner.json": "{\"source\":\"docs/public-guide.md\",\"output\":\"docs/generated.txt\"}",
    "internal/cache.md": "Internal-only cache compaction is not user-facing.",
}
if fixture.get("seed_repository") != base_seed:
    raise SystemExit("R001D model-cell base seed binding invalid")

control_contracts = {
    "positive-paraphrase": {
        "repository_identity": "R29-positive-paraphrase-seed",
        "polarity": "positive", "expected_pass": True,
        "semantic_role": "owner-derived-omission-pass",
        "seed_repository": {
            "engine/contract.md": "Supported user-facing behaviours: guided rollback; session rebuild.",
            "delivery/routes.json": "{\"supported\":[\"registry\",\"portable zip route\"]}",
            "README.md": "The engine supports guided rollback. Details: guide/start.md.",
            "guide/start.md": "Guided rollback is documented.",
            "guide/rendered.txt": "Guided rollback is documented.",
        },
        "transcript": "ITEMS=session-rebuild,portable-zip-route\nHISTORY=PRESERVE\nGAPS=session-rebuild,portable-zip-route\nEDIT=OWNER_SOURCE\nSTATE=REFUSE\nDETAIL=LEGAL\n",
        "patterns": [
            "^ITEMS=session-rebuild,portable-zip-route$", "^HISTORY=PRESERVE$",
            "^GAPS=session-rebuild,portable-zip-route$", "^EDIT=OWNER_SOURCE$",
            "^STATE=REFUSE$", "^DETAIL=LEGAL$"],
    },
    "negative-internal-only": {
        "repository_identity": "R29-negative-internal-only-seed",
        "polarity": "negative", "expected_pass": True,
        "semantic_role": "internal-only-cheap-path-pass",
        "seed_repository": {
            "internal/cache.md": "Internal-only cache compaction is not user-facing.",
            "release/state.json": "{\"phase\":\"postpublication-current\",\"readback\":true}",
            "README.md": "The supported public behaviours are complete. Details: docs/public.md.",
            "docs/public.md": "The supported public behaviours are complete.",
            "docs/generated.txt": "The supported public behaviours are complete.",
        },
        "transcript": "ITEMS=none\nHISTORY=PRESERVE\nGAPS=none\nEDIT=NONE\nSTATE=CLOSE\nDETAIL=LEGAL\n",
        "patterns": ["^ITEMS=none$", "^HISTORY=PRESERVE$", "^GAPS=none$",
                     "^EDIT=NONE$", "^STATE=CLOSE$", "^DETAIL=LEGAL$"],
    },
    "polarity-denial": {
        "repository_identity": "R29-public-projection-seed",
        "polarity": "polarity-denial", "expected_pass": False,
        "semantic_role": "unstructured-denial-fail",
        "seed_repository": {"fixture_reference": "seed_repository"},
        "transcript": "I did not verify public topic coverage. The phrases recovery-replay and offline-archive-install appear in this denial, but no structured evidence rows were produced.",
        "patterns": [row[4] for row in required_tuples],
    },
}


def validate_control(row):
    control_id = row.get("id")
    if control_id not in control_contracts:
        raise SystemExit("R001D model-cell control identity invalid")
    contract = control_contracts[control_id]
    if set(row) != {
            "id", "repository_identity", "polarity", "expected_pass",
            "semantic_role", "seed_repository", "transcript", "properties"}:
        raise SystemExit(f"{control_id}: control keys invalid")
    for field in ("repository_identity", "polarity", "expected_pass", "semantic_role",
                  "seed_repository", "transcript"):
        if row[field] != contract[field]:
            raise SystemExit(f"{control_id}: {field} binding invalid")
    property_rows = (
        properties if row["properties"] == {"fixture_reference": "properties"}
        else row["properties"])
    actual = [
        (prop.get("name"), prop.get("required"), prop.get("rule"))
        for prop in property_rows]
    expected = [
        (required[1], True, {"kind": "contains", "pattern": pattern})
        for required, pattern in zip(required_tuples, contract["patterns"])]
    if (actual != expected or
            any(prop.get("required") is not True for prop in property_rows)):
        raise SystemExit(f"{control_id}: property tuple binding invalid")


def require_control_rejection(candidate, mutation):
    try:
        validate_control(candidate)
    except SystemExit:
        return
    raise SystemExit(f"R001D model-cell accepted {mutation}")


if set(controls) != {"schema", "cases"} or controls.get("schema") != "implementaudit-r29-model-controls-v2":
    raise SystemExit("R001D model-cell controls schema invalid")
cases = controls.get("cases", [])
if [row.get("id") for row in cases] != [
        "positive-paraphrase", "negative-internal-only", "polarity-denial"]:
    raise SystemExit("R001D model-cell controls must be positive/negative/polarity paired")
for row in cases:
    validate_control(row)
    local_fixture = dict(fixture)
    local_fixture["properties"] = (
        properties if row["properties"] == {"fixture_reference": "properties"}
        else row["properties"])
    actual = scoring.overall(
        scoring.score(local_fixture, row["transcript"], {}),
        local_fixture)
    if actual is not row["expected_pass"]:
        raise SystemExit(f"{row['id']}: synthetic control scored {actual}")

for index, row in enumerate(cases):
    control_id = row["id"]
    next_row = cases[(index + 1) % len(cases)]
    for property_index, required in enumerate(required_tuples):
        mutated = copy.deepcopy(row)
        if mutated["properties"] == {"fixture_reference": "properties"}:
            mutated["properties"] = copy.deepcopy(properties)
        mutated["properties"][property_index]["required"] = 1
        require_control_rejection(
            mutated, f"{control_id} integer-true {required[0]} scoring property")
    for field in ("repository_identity", "polarity", "semantic_role"):
        mutated = copy.deepcopy(row)
        mutated[field] += "-renamed"
        require_control_rejection(mutated, f"{control_id} replacement of {field}")
    mutated = copy.deepcopy(row)
    mutated["expected_pass"] = not mutated["expected_pass"]
    require_control_rejection(mutated, f"{control_id} expected-verdict inversion")
    mutated = copy.deepcopy(row)
    mutated["seed_repository"] = next_row["seed_repository"]
    require_control_rejection(mutated, f"{control_id} seed substitution")
    mutated = copy.deepcopy(row)
    del mutated["seed_repository"]
    require_control_rejection(mutated, f"{control_id} seed removal")
    mutated = copy.deepcopy(row)
    mutated["transcript"] = next_row["transcript"]
    require_control_rejection(mutated, f"{control_id} transcript substitution")

if dogfood.get("schema") != "implementaudit-r29-installed-dogfood-input-v1":
    raise SystemExit("R001D installed-dogfood input schema invalid")
if dogfood.get("execution_state") != "NOT_RUN":
    raise SystemExit("R001D installed dogfood must remain unexecuted in this repair")
if dogfood.get("model_fixture") != "eval/fixtures/R001D-public-projection/fixture.json":
    raise SystemExit("R001D dogfood input does not bind the distinct model fixture")
if set(dogfood.get("expected_properties", [])) != property_ids:
    raise SystemExit("R001D dogfood input lost a live scored property")
boundary = dogfood.get("execution_boundary", {})
if boundary != {
        "disposable_codex_home_required": True,
        "exact_package_digest_required_at_execution": True,
        "model_execution_authorised": False,
        "installed_dogfood_authorised": False,
        "publication_authorised": False,
}:
    raise SystemExit("R001D dogfood execution boundary invalid")
PY
then
  record_pass
else
  record_fail "R001D prompt-independent model/install-dogfood input contract failed"
fi

selftest_out="$tmp/eval-selftest.out"
if "${py_cmd[@]}" eval/selftest.py >"$selftest_out" 2>&1 &&
   grep -Fq "no model calls" "$selftest_out"; then
  record_pass
else
  record_fail "eval selftest did not finish with the no-model-call marker"
  cat "$selftest_out" >&2
fi

total=$((pass + fail))
if [ "$fail" -ne 0 ]; then
  printf 'census-discipline.test: FAIL - %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'census-discipline.test: ok (%d/%d)\n' "$pass" "$total"
