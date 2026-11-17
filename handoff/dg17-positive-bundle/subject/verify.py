#!/usr/bin/env python3
"""Read-only acceptance of actual report files; does not import the generator."""
import argparse
import hashlib
import json
from pathlib import Path


def identity(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=("integrity", "inventory", "owners", "guide", "all"))
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    args = parser.parse_args()
    names = ("inventory", "owners", "guide")
    paths = {name: Path("output") / (name + ".json") for name in names}
    reports = {name: json.loads(path.read_text()) for name, path in paths.items()}
    declarations = json.loads(Path("inputs/package-members.json").read_text())
    failures = []
    for row in declarations:
        actual = identity(args.package_root / row["path"])
        if actual != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            failures.append("Package byte identity differs: " + row["path"])
    if len(declarations) != 78 or len({row["path"] for row in declarations}) != 78:
        failures.append("Package declaration population differs")
    for name, value in reports.items():
        if not isinstance(value, dict) or not value:
            failures.append("Report is not a nonempty object: " + name)
        if not paths[name].read_bytes().endswith(b"\n"):
            failures.append("Report lacks its final newline: " + name)
    checks = names if args.check == "all" else (args.check,)
    if "inventory" in checks:
        value = reports["inventory"]
        required = {"schema", "member_count", "total_bytes", "members"}
        if set(value) != required or value.get("schema") != "package-inventory.v1":
            failures.append("Inventory schema differs")
        else:
            members = value["members"]
            expected_paths = sorted(row["path"] for row in declarations)
            if [row.get("path") for row in members] != expected_paths:
                failures.append("Inventory path population/order differs")
            for row in members:
                if set(row) != {"path", "bytes", "sha256"} or row != dict(path=row["path"], **identity(args.package_root / row["path"])):
                    failures.append("Inventory row differs: " + str(row.get("path")))
            if value["member_count"] != len(members) or value["total_bytes"] != sum(row["bytes"] for row in members):
                failures.append("Inventory accounting differs")
    if "owners" in checks:
        value = reports["owners"]
        names_expected = ["apply-observed-mutation.sh", "check-closure-surface.sh", "check-evidence-anchor.sh", "claim-run.sh", "detect-env.sh", "repo-state.sh", "validate-phase.sh", "validate-run-root.sh"]
        if set(value) != {"schema", "owners"} or value.get("schema") != "operating-owner-index.v1":
            failures.append("Owner-index schema differs")
        elif [row.get("name") for row in value["owners"]] != names_expected:
            failures.append("Operating owner population/order differs")
        else:
            for row in value["owners"]:
                source_path = "skills/implementaudit/scripts/" + row["name"]
                if row != dict(name=row["name"], path=source_path, **identity(args.package_root / source_path)):
                    failures.append("Operating owner identity differs: " + row["name"])
    if "guide" in checks:
        value = reports["guide"]
        profile = json.loads(args.profile.read_text())
        required = {"schema", "profile_revision", "profile_sha256", "purpose", "inventory_sha256", "owner_index_sha256", "selected_owners"}
        if set(value) != required or value.get("schema") != "operating-guide.v1":
            failures.append("Guide schema differs")
        else:
            if value["profile_revision"] != profile["revision"] or value["purpose"] != profile["purpose"]:
                failures.append("Guide profile content differs")
            if value["profile_sha256"] != identity(args.profile)["sha256"]:
                failures.append("Guide profile dependency is stale")
            for output_name, field in (("inventory", "inventory_sha256"), ("owners", "owner_index_sha256")):
                if value[field] != identity(paths[output_name])["sha256"]:
                    failures.append("Guide report dependency differs: " + output_name)
            selected = value["selected_owners"]
            index = {row["name"]: row for row in reports["owners"].get("owners", [])}
            if [row.get("name") for row in selected] != profile["owners"]:
                failures.append("Guide requested owner population/order differs")
            for row in selected:
                if row != index.get(row["name"]):
                    failures.append("Guide selected owner differs: " + row["name"])
    result = {"check": args.check, "passed": not failures, "failures": failures,
              "outputs": {name: identity(path) for name, path in paths.items()},
              "profile": identity(args.profile)}
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
