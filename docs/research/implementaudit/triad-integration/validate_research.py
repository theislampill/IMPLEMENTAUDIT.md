#!/usr/bin/env python3
"""Check triad accounting and custody links; this is not semantic acceptance."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(root: Path) -> dict:
    def read(name):
        return json.loads((root / name).read_text(encoding="utf-8"))

    def indexed(rows, field, count):
        values = {row[field]: row for row in rows}
        require(len(values) == len(rows) == count, f"{field}: population or duplicate")
        return values

    source = indexed(read("PROPERTY_INDEX.json"), "key", 747)
    target = indexed(read("DISPOSITIONS.json")["properties"], "key", 747)
    require(source.keys() == target.keys(), "property key coverage")
    for key, row in target.items():
        original = source[key]
        for field in ("source_pointer", "source_row_sha256", "criterion", "trigger", "inherited_disposition"):
            require(row[field] == original[field], f"{key}: changed protected {field}")
        require(row["source_semantic_disposition"] == original["inherited_disposition"],
                f"{key}: source disposition lost")
        require(not row["new_property_identity_admitted"], f"{key}: unreviewed new identity")
        require("proposal_disposition" not in row, f"{key}: obsolete proposal in active decision")
        require(bool(row["rationale"]) and bool(row["owner_refs"]), f"{key}: absent reasoning or owner")

    source_context = indexed(read("CONTEXT_INDEX.json"), "id", 268)
    contexts = indexed(read("CONTEXT_DISPOSITIONS.json")["contexts"], "id", 268)
    require(source_context.keys() == contexts.keys(), "context key coverage")
    for key, row in contexts.items():
        for field in ("trifecta", "kind", "source_pointer", "source_row_sha256"):
            require(row[field] == source_context[key][field], f"{key}: context custody {field}")
        require(set(row["property_keys"]) <= source.keys(), f"{key}: unknown property")
        require(row["closure_credit"] == 0 and not row["dependency_edges_added"], f"{key}: authority upgrade")

    def lines(name):
        return [json.loads(line) for line in (root / name).read_text(encoding="utf-8").splitlines()]

    relations = indexed(lines("RELATION_INDEX.jsonl"), "id", 34052)
    dispositions = indexed(lines("RELATION_DISPOSITIONS.jsonl"), "id", 34052)
    require(relations.keys() == dispositions.keys(), "relation key coverage")
    policy = read("RELATION_POLICY.json")
    typed = {kind: decision for decision, kinds in policy["classification_by_inherited_type"].items()
             for kind in kinds}
    for key, row in dispositions.items():
        original = relations[key]
        require(row["classification"] == typed[original["type"]], f"{key}: relation policy mismatch")
        require(not row["hard_dependency_admitted"], f"{key}: unauthorized scheduling edge")
        for side in ("source", "target"):
            require(row[side + "_disposition"] == target[original[side]]["disposition"],
                    f"{key}: stale endpoint disposition")
    require(dict(Counter(r["classification"] for r in dispositions.values())) == policy["counts"],
            "relation count mismatch")
    bridges = indexed(read("EXPLICIT_BRIDGE_DISPOSITIONS.json")["bridges"], "id", 317)
    for key, row in bridges.items():
        for field in ("source", "target", "source_pointer", "source_row_sha256"):
            require(row[field] == relations[key][field], f"{key}: bridge custody mismatch")

    findings = indexed(read("COMPOSITION_FINDINGS.json")["findings"], "id", 12)
    require(set(findings) == {f"TC{i:02}" for i in range(1, 13)}, "case identity mismatch")
    for row in findings.values():
        require(set(row["parents"]) <= source.keys(), "unknown composition parent")
        require({source[k]["trifecta"] for k in row["parents"]} == {"SSS", "BWP", "AMA"},
                f"{row['id']}: absent trifecta")
        require(not row["new_normative_property_admitted"], "unexpected novelty admission")
    athruk = indexed(read("ATHRUK_IMPLICATIONS.json")["families"], "letter", 11)
    require(set(athruk) == set("ABCDEFGHIJK"), "A-K coverage")
    for key, row in findings.items():
        require(set(row["athruk"]) == {letter for letter, family in athruk.items()
                                      if key in family["composition_cases"]}, f"{key}: A-K asymmetry")

    baseline = read("BASELINE_SCOPE.json")["release_frontier"]
    frontier = indexed(read("FRONTIER_IMPLICATIONS.json")["rows"], "cell", 32)
    expected = set(baseline["required_cells_in_ordered_ledger"]) | {baseline["conditional_cell"], "MIC"}
    expected.update(baseline["deferred_or_optional_rows"])
    require(frontier.keys() == expected, "frozen frontier coverage")
    for row in frontier.values():
        require(row["closure_credit"] == 0 and not row["dependency_edges_added_here"]
                and not row["post_triad_execution_dag_derived"], "frontier authority upgrade")

    expected_layout = Path("docs/research/implementaudit/triad-integration")
    candidates = [parent for parent in root.parents
                  if parent / expected_layout == root
                  and (parent / "package/implementaudit-package.json").is_file()]
    require(len(candidates) == 1, "complete repository and canonical research directory layout required")
    repository = candidates[0]
    for row in read("SOURCE_RECONCILIATION.json")["paths"]:
        raw = (repository / row["path"]).read_bytes()
        require({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()} == row["integration_postimage"],
                f"{row['path']}: stale integration postimage")
    issues = read("ISSUE_ADJUDICATION.json")
    issue_rows = indexed(issues["rows"], "identity", 58)
    require(Counter(row["frozen_state"] for row in issue_rows.values()) == {"CLOSED": 44, "OPEN": 14},
            "frozen issue state population")
    require(not issues["new_issue_identities_admitted"]
            and all(not row["state_change"] for row in issue_rows.values()), "issue authority upgrade")
    return {"properties": 747, "relations": 34052, "contexts": 268, "explicit_bridges": 317,
            "composition_cases": 12, "frontier_rows": 32, "athruk_families": 11,
            "proof_limit": "ACCOUNTING_AND_CUSTODY_LINKS_ONLY"}


if __name__ == "__main__":
    json.dump(validate(Path(__file__).resolve().parent), sys.stdout, indent=2)
    sys.stdout.write("\n")
