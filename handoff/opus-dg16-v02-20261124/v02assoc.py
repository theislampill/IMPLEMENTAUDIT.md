"""DG16 V02 association: every registry obligation -> exactly one node or the SETTLE JOIN, derived from A2.

Read-only. Inputs: the A2 retained occurrence directory and the pristine b30ef328 checkout.
Usage: python3 -I v02assoc.py <a2-output-dir> <checkout> <out.json>
"""
import hashlib, json, re, sys
from pathlib import Path

A2, SRC, OUT = (Path(p) for p in sys.argv[1:4])
REGISTRY_SHA = "ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978"
OFFSET = 2  # PRELUDE_REGISTRIES[REGISTRY_SHA][1] in scripts/work-graph-verifier-task.py
sha = lambda b: hashlib.sha256(b).hexdigest()

mapping = json.loads((A2 / "capture/mapping.json").read_bytes())
record = json.loads((A2 / "task-result.json").read_bytes())
registry = (SRC / "scripts/verify-package.sh").read_bytes()
assert sha(registry) == mapping["registry_sha256"] == REGISTRY_SHA, "registry is not the exact A2 registry"
assert mapping["covered_bytes"] == len(registry) == 44184
nodes = mapping["nodes"]
observed = {row["node"]: row for row in record["nodes"]}
assert [n["id"] for n in nodes] == [row["node"] for row in record["nodes"]], "A2 node order differs from mapping"
assert all(row["status"] == "PASS" for row in record["nodes"]) and record["result"]["status"] == "PASS"
existing = {p["id"]: p for p in record["properties"]}
assert len(existing) == len(record["properties"]) == 399

def base(node):
    return {"node": node["id"], "node_kind": node["kind"], "node_bytes": [node["byte_start"], node["byte_end"]],
            "node_source_sha256": node["source_sha256"], "requires": node["requires"],
            "environment_digest": node["environment_digest"],
            "writer_resource_constraint": node["writer_resource_constraint"], "evidence": node["evidence"],
            "invalidators": node["invalidators"], "normalization": node["result_contract"],
            "observed_node_status": observed[node["id"]]["status"], "dispatch_id": record["result"]["dispatch_id"]}

rows = []
def add(ident, node, lines, kind, outcome, **extra):
    rows.append({"id": ident, "obligation_kind": kind, "registry_lines": lines, "outcome": outcome, **base(node), **extra})

# ---- PRELUDE (composed node 0): classify every one of its 669 lines exactly once ----------------
pre = nodes[0]
assert pre["id"] == "PRELUDE" and pre["byte_start"] == 0
text = pre["source"].splitlines()
assert len(text) == 669
cls = {}  # registry line -> obligation id or structural tag
def claim(lines, tag):
    for ln in lines:
        assert ln not in cls, ("line classified twice", ln, cls[ln], tag)
        cls[ln] = tag
passed = observed["PRELUDE"]["status"] == "PASS"
ok = "PASS" if passed else "UNVERIFIED"

# existing A2 rows: required files and the 14 version-prelude properties (exactly once, reused)
req_lines = {}
for i, l in enumerate(text, 1):
    m = re.fullmatch(r"require_file ([A-Za-z0-9._/-]+)", l)
    if m:
        req_lines.setdefault(m[1], []).append(i)
for path, lines in req_lines.items():
    assert existing["required-file:" + path]["source_lines"] == lines
    claim(lines, "required-file:" + path)
version_rows = [p for p in record["properties"] if p["node"] == "PRELUDE" and not p["id"].startswith("required-file:")]
assert len(version_rows) == 14
heredoc_ranges = {"skill-version-block": range(494, 515), "plugin-marketplace-readme-block": range(516, 567)}
for p in version_rows:
    lo, hi = p["source_lines"]
    claim(range(lo, hi + 1), p["id"])
# the heredoc scaffolding around the 14 rows (imports, reads, delimiters) is structural
for ln in list(heredoc_ranges["skill-version-block"]) + list(heredoc_ranges["plugin-marketplace-readme-block"]):
    cls.setdefault(ln, "structural:heredoc-scaffold")

def single(ident, lines, kind="INLINE_GUARD", outcome=None, **extra):
    claim(lines, ident)
    add(ident, pre, list(lines), kind, outcome or ok, **extra)

structural = {1: "shebang", 2: "shell-options", 4: "environment", 6: "fail-definition", 7: "fail-definition",
              8: "fail-definition", 9: "fail-definition", 11: "repo-root", 12: "repo-root", 14: "state", 15: "state",
              16: "state", 17: "exit-trap", 18: "exit-trap", 44: "require-file-definition",
              45: "require-file-definition", 46: "require-file-definition", 568: "comment"}
for ln, tag in structural.items():
    claim([ln], "structural:" + tag)
single("release-identity-arguments", range(19, 42), "ARGUMENT_MODE", "INAPPLICABLE_NO_ARGUMENTS_SUPPLIED",
       note="the canonical route supplies no arguments; every branch of the case is unexecuted")
single("no-unknown-arguments", [42], "ARGUMENT_GUARD")
single("root-implementaudit-md-absent", range(48, 51))
single("release-identity-build-and-check", range(66, 72), "CONDITIONAL_COMMANDS", "INAPPLICABLE_NO_ARGUMENTS_SUPPLIED")
reports = ["skills/implementaudit/templates/child-agent-report.md", "fixtures/child-agents/read-only-contract-auditor.md",
           "fixtures/child-agents/adversarial-behavioral-auditor.md",
           "fixtures/child-agents/read-only-contract-auditor-report.md",
           "fixtures/child-agents/adversarial-behavioral-auditor-report.md"]
sections = [(446, "Verdict:"), (447, "Files inspected:"), (448, "Commands run:"), (449, "Andon registration check:"),
            (450, "Required patches"), (451, "Required fixtures / canaries"), (452, "What closes"),
            (453, "What remains"), (454, "Next smallest safe action")]
fields = ["Finding title", "Category", "Evidence", "Impact", "Effort", "Risk", "Confidence",
          "Fix sketch / implementation route", "Owner/source", "Verification", "Rejected/deferred rationale",
          "Remaining risk", "Route"]
assert [l.strip() for l in text[438:444]][1:6] == [r + " \\" if i < 4 else r for i, r in enumerate(reports)]
claim(range(439, 446), "structural:child-report-loop-header"); claim([455, 457, 458], "structural:child-report-loop")
claim([446, 447, 448, 449, 450, 451, 452, 453, 454], "child-report-section-guards")
claim([456], "child-report-field-guards")
for r in reports:
    for ln, s in sections:
        add(f"child-report-section:{r}:{s}", pre, [ln], "LOOP_EXPANDED_GUARD", ok, inputs={"file": r, "pattern": s})
    for f in fields:
        add(f"child-report-field:{r}:{f}", pre, [456], "LOOP_EXPANDED_GUARD", ok, inputs={"file": r, "pattern": f})
single("child-agents-andon-registration-invariant", [460])
single("child-agents-false-green-rerun-rule", [461])
single("python-interpreter-available", range(463, 472), "INTERPRETER_SELECTION")
single("plugin-json-valid", [473], "SET_E_COMMAND")
single("marketplace-json-valid", [474], "SET_E_COMMAND")
single("tracked-shell-lf-line-endings", range(476, 493), "INLINE_PYTHON_GUARD")
single("installed-payload-self-contained", [569], "SET_E_COMMAND",
       note="nested maintained owner; its own internal checks compose into this exit obligation")
markers = [text[i - 1].strip().rstrip(" \\") for i in range(572, 588)]
assert len(markers) == 16 and markers[-1] == "IMPLEMENTAUDIT_RUN_COMPLETE"
claim(range(571, 589), "structural:marker-loop"); claim([590], "structural:marker-loop")
claim([589], "transcript-marker-guards")
for mk in markers:
    add("transcript-marker:" + mk, pre, [589], "LOOP_EXPANDED_GUARD", ok, inputs={"pattern": mk, "tree": "skills"})
for ln in range(592, 620):
    single(f"documented-claim:L{ln}", [ln], inputs={"guard": text[ln - 1].split("|| fail")[-1].strip()})
claim(range(621, 634), "structural:require-absent-matches-definition")
single("scan-output-directory", [635], "INLINE_GUARD")
single("absent-root-behavior-source-direction", range(636, 645), "ABSENCE_SCAN")
single("canonical-skill-source-documented", [646])
claim(range(648, 654), "structural:absence-pattern-assembly")
single("absent-nonstandard-child-agent-filename", range(654, 658), "ABSENCE_SCAN")
single("scan-output-cleanup", [658, 659], "SET_E_COMMAND")
for ln in range(661, 669):
    single(f"documented-claim:L{ln}", [ln], inputs={"guard": text[ln - 1].split("|| fail")[-1].strip()})
for ln in range(1, 670):
    if ln not in cls and not text[ln - 1].strip():
        cls[ln] = "structural:blank"
missing = [ln for ln in range(1, 670) if ln not in cls]
assert not missing, ("unclassified prelude lines", missing)

# ---- every downstream node: its registry obligation is its own exit under the node contract ------
checker_id = "COMMAND:scripts/check-validation-registry.sh:0"
for node in nodes[1:]:
    if node["id"] == checker_id:
        assert {p["id"] for p in record["properties"] if p["node"] == checker_id} == {
            "registry_nonempty", "fixed_python_runner_image", "registry_once", "canonical_route_exactly_once",
            "no_direct_ci_test_dispatch"}
        add("checker-auxiliary:repo-root-argument", node, None, "ARGUMENT_MODE", "INAPPLICABLE_NO_ARGUMENTS_SUPPLIED",
            checker_lines=[18])
        add("checker-auxiliary:python-available", node, None, "INTERPRETER_SELECTION",
            "PASS" if observed[node["id"]]["status"] == "PASS" else "UNVERIFIED", checker_lines=[30])
        continue
    kind = {"TEST": "TEST_NODE_EXIT", "CHECK": "CHECK_NODE_EXIT", "FINAL_CHECK": "FINAL_CHECK_EXIT",
            "TERMINAL": "TERMINAL_REPORT"}[node["kind"]]
    add("node-exit:" + node["id"], node, None, kind, "PASS" if observed[node["id"]]["status"] == "PASS" else "UNVERIFIED",
        command=node["command"],
        note=("composed obligation: internal assertions of this command are qualified by the command's own suite; "
              "the registry obligation is the command exit under its contract") if node["kind"] in ("TEST", "CHECK") else None)

# ---- terminal semantics on the SETTLE JOIN --------------------------------------------------------
join = record["join"]
rows.append({"id": "terminal:settle-requires-all-registry-obligations", "obligation_kind": "JOIN_SEMANTICS",
             "node": "SETTLE", "consumer": join["consumer"], "join_schema": join["schema"],
             "join_status": join["status"], "requires": join["required"], "missing": join["missing"],
             "completion_digest": join["completion_digest"], "successor": record["successor"],
             "outcome": "PASS" if join["all_required_settled"] and not join["missing"] and record["successor"] == "READY"
             else "UNVERIFIED",
             "normalization": "PASS_REQUIRES_VERIFY_PASS_AND_ALL_REQUIRED_SETTLED",
             "invalidators": ["task_input", "journal_history", "completion_digest"]})

ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)) and not set(ids) & set(existing)
mapped_nodes = {r["node"] for r in rows} | {p["node"] for p in record["properties"]}
assert mapped_nodes >= {n["id"] for n in nodes}, sorted({n["id"] for n in nodes} - mapped_nodes)
summary = {
    "schema": "dg16.v02-association.v1", "authority": "NONE", "subject": "b30ef328c9a22f68ab420c84dc87e849fd4e4599",
    "registry_sha256": REGISTRY_SHA, "mapping_digest": mapping["digest"], "a2_dispatch": record["result"]["dispatch_id"],
    "a2_task_result_sha256": sha((A2 / "task-result.json").read_bytes()),
    "existing_a2_rows": len(existing), "new_rows": len(rows), "total_obligations": len(existing) + len(rows),
    "nodes_covered": f"{len(mapped_nodes & {n['id'] for n in nodes})}/{len(nodes)}",
    "prelude_lines_classified": "669/669",
    "new_outcomes": {o: sum(r["outcome"] == o for r in rows) for o in sorted({r["outcome"] for r in rows})},
    "new_kinds": {k: sum(r["obligation_kind"] == k for r in rows) for k in sorted({r["obligation_kind"] for r in rows})},
    "prelude_line_classes": {k: sum(1 for v in cls.values() if v.startswith("structural:") == (k == "structural"))
                             for k in ("obligation_or_existing_row", "structural")},
}
OUT.write_text(json.dumps({"summary": summary, "prelude_line_classification": {str(k): v for k, v in sorted(cls.items())},
                           "rows": rows}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=1))
