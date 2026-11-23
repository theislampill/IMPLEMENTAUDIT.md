"""Exercise optional child selection through the pinned product CLI."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from structural_checks import CANDIDATE, ROOT, git

COMPILER = "skills/implementaudit/scripts/compile-work-graph.py"
RESOLVER = "skills/implementaudit/scripts/resolve-internal-skill.py"
GOVERNOR = "skills/implementaudit/SKILL.md"
CHILD = "skills/audit-andon/SKILL.md"

CELL = {
    "id": "stocktake", "dependency": "NONE", "predecessors": [], "writes": [],
    "impact": "KNOWN", "state": "READY", "resource_demand": 1, "rank": 0,
    "acceptance_boundary": "NONE", "resource_boundary": "NONE", "effect": "REVERSIBLE",
    "authority_boundary": "NONE", "authorization_current": True, "currentness_current": True,
}
BASE = {
    "schema": "implementaudit.native-a-g.request.v1",
    "dependency": {"cells": [CELL], "joins": [{"id": "review-stocktake", "requires": ["stocktake"]}],
                   "host_capacity": 1, "operator_ceiling": 1},
    "invalidation": {"changed_paths": ["inventory.txt"], "change_kind": "SOURCE", "consumers": []},
}
MECHANICAL = {"id": "checksum", "identity_known": True, "evidence_contradictory": False,
              "substantive_cognition": False, "work": ["hash"],
              "requester_role": "GOVERNOR", "requested_action": "ASSIGN"}
SPECIALIST = dict(MECHANICAL, id="inventory-discrepancy", substantive_cognition=True,
                  work=["diagnose contradictory physical inventory measurements"],
                  specialist_holon="audit-andon")


def main():
    git("diff", "--exit-code", CANDIDATE, "--", "skills")
    print(json.dumps({"candidate": CANDIDATE, "tree": git("rev-parse", CANDIDATE + "^{tree}"),
                      "scope": "constructed request through product CLI",
                      "source_blobs": {name: git("rev-parse", f"{CANDIDATE}:{name}")
                                       for name in (COMPILER, RESOLVER, GOVERNOR, CHILD)}}))
    cases = [
        ("zero-child", [MECHANICAL], ["GOVERNOR_MECHANICAL"]),
        ("one-selected-child-without-predecessors", [SPECIALIST], ["CHILD_SKILL:audit-andon"]),
        ("independent-decisions", [SPECIALIST, MECHANICAL], ["CHILD_SKILL:audit-andon", "GOVERNOR_MECHANICAL"]),
        ("reverse-independent-decisions", [MECHANICAL, SPECIALIST], ["GOVERNOR_MECHANICAL", "CHILD_SKILL:audit-andon"]),
        ("fixed-itinerary-is-not-a-specialist", [dict(SPECIALIST,
            specialist_holon="audit-state -> audit-assess -> audit-implement -> audit-andon")], ["BLOCK"]),
    ]
    matches = []
    with tempfile.TemporaryDirectory(prefix="sol-dg17-routing-") as scratch:
        path = Path(scratch) / "request.json"
        for name, items, expected in cases:
            request = dict(BASE, execution_owner=items)
            raw = json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
            path.write_bytes(raw)
            result = subprocess.run([sys.executable, "-B", str(ROOT / COMPILER), "--native-a-g", str(path)],
                                    cwd=ROOT, capture_output=True, timeout=30)
            projection = json.loads(result.stdout) if result.returncode == 0 else {}
            observed = projection.get("execution_owner", [])
            want = [{"id": item["id"], "owner": owner, "authority": "SOLE_GOVERNOR"}
                    for item, owner in zip(items, expected, strict=True)]
            same_input = path.read_bytes() == raw
            matched = result.returncode == 0 and observed == want and same_input
            print(json.dumps({"case": name, "matched": matched, "request": request,
                              "request_sha256": hashlib.sha256(raw).hexdigest(),
                              "request_unchanged": same_input, "expected": want, "observed": observed,
                              "exit": result.returncode}))
            matches.append(matched)

    result = subprocess.run([sys.executable, "-B", str(ROOT / RESOLVER),
                             "--governor", str(ROOT / GOVERNOR), "--child", "audit-andon"],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    observed = Path(result.stdout.strip())
    matched = result.returncode == 0 and observed == ROOT / CHILD
    print(json.dumps({"case": "resolve-the-one-selected-child", "expected": CHILD,
                      "observed": observed.relative_to(ROOT).as_posix() if matched else None,
                      "exit": result.returncode, "matched": matched}))
    matches.append(matched)
    print(json.dumps({"checks": len(matches), "matches": sum(matches)}))
    return 0 if all(matches) else 1


if __name__ == "__main__":
    sys.exit(main())
