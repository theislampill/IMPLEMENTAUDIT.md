#!/usr/bin/env python3
"""Generate one of three fixed reports from the admitted package and profile."""
import argparse
import hashlib
import json
from pathlib import Path

OWNERS = (
    "apply-observed-mutation.sh", "check-closure-surface.sh",
    "check-evidence-anchor.sh", "claim-run.sh", "detect-env.sh",
    "repo-state.sh", "validate-phase.sh", "validate-run-root.sh",
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", choices=("inventory", "owners", "guide"))
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    args = parser.parse_args()
    rows = json.loads(Path("inputs/package-members.json").read_text())
    if args.report == "inventory":
        members = []
        for row in sorted(rows, key=lambda row: row["path"]):
            raw = (args.package_root / row["path"]).read_bytes()
            if len(raw) != row["bytes"] or digest(raw) != row["sha256"]:
                raise SystemExit("Admitted package member changed")
            members.append({"path": row["path"], "bytes": len(raw), "sha256": digest(raw)})
        result = {"schema": "package-inventory.v1", "member_count": len(members),
                  "total_bytes": sum(row["bytes"] for row in members), "members": members}
    elif args.report == "owners":
        entries = []
        for name in OWNERS:
            path = "skills/implementaudit/scripts/" + name
            raw = (args.package_root / path).read_bytes()
            entries.append({"name": name, "path": path, "bytes": len(raw), "sha256": digest(raw)})
        result = {"schema": "operating-owner-index.v1", "owners": entries}
    else:
        profile_raw = args.profile.read_bytes()
        profile = json.loads(profile_raw)
        inventory_raw = Path("output/inventory.json").read_bytes()
        index_raw = Path("output/owners.json").read_bytes()
        index = {row["name"]: row for row in json.loads(index_raw)["owners"]}
        result = {"schema": "operating-guide.v1", "profile_revision": profile["revision"],
                  "profile_sha256": digest(profile_raw), "purpose": profile["purpose"],
                  "inventory_sha256": digest(inventory_raw), "owner_index_sha256": digest(index_raw),
                  "selected_owners": [index[name] for name in profile["owners"]]}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
