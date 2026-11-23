"""Read-only M5 package dependency bridge from exact accepted 205aeab to c53ed7de."""

import ast
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile


BEFORE = "205aeab7c93299b0666b261485ab5658d8e183de"
BEFORE_TREE = "9ffbaf95080092bf4a45b8772a97ed16068544a7"
AFTER = "c53ed7de85de22ce313233472c8d8f02ad8e9d02"
AFTER_TREE = "d60733459425a059d961b6adc2aae9811bbb761c"
EARLIER = "e76a07b2bae7c945e5a9d529ed8cf9069f4c9064"
ARCHIVES = "c073689e315b4db7c26e5a95c9024a34b1e560b7"
PACKAGE_ROOT = "handoff/dg16-m5-source-20261115/validation/new-package-fixture-build/artifacts"
RESULTS = "6431a1d1e067ab37e4f461caa4a61890d69e7c14"
SCOPE = "handoff/pro-executor-results-20261115"
RECEIVER = (SCOPE + "/continuing-execution-20261122-45-recovery3/source-snapshots/"
            "qualification/dg16-r5-g1-hosted-episode/g3_receiving.py")
M5 = SCOPE + "/continuation-recovery/m5/ROOT_ORIGINAL_RECEIVING.md"
CONTRACT = "package/implementaudit-package.json"
BUILDER = "scripts/package-contract.py"
INVENTORY = "IMPLEMENTAUDIT_INVENTORY.json"
GENERATED = "IMPLEMENTAUDIT_PACKAGE.json"
APPROVAL = "package/budgets/pr255-v4-owner-approval.md"
TOOL_SOURCES = (
    "requirements-release.txt",
    "scripts/install-plugin-from-release.sh",
    "scripts/install-codex-from-release.sh",
    "scripts/install-claude-from-release.sh",
)


def require(condition, label):
    if not condition:
        raise ValueError(label)


def git(*args):
    return subprocess.check_output(["git", *args])


def blob(ref, path):
    return git("cat-file", "blob", f"{ref}:{path}")


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(raw):
    return {"bytes": len(raw), "sha256": sha(raw)}


def git_tree(commit):
    rows = {}
    for raw in git("ls-tree", "-r", "-l", "-z", commit).split(b"\0"):
        if not raw:
            continue
        header, path = raw.split(b"\t", 1)
        mode, kind, oid, size = header.decode().split()
        require(kind == "blob", "expected regular Git product blob")
        rows[path.decode("utf-8")] = (mode, oid, int(size))
    return rows


def tree_byte_pins(trees):
    requested = {oid: size for tree in trees for _, oid, size in tree.values()}
    pins = {}
    with subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE) as read:
        for oid, size in sorted(requested.items()):
            read.stdin.write(oid.encode() + b"\n")
            read.stdin.flush()
            header = read.stdout.readline().decode().split()
            require(header == [oid, "blob", str(size)], "immutable Git body identity")
            body = read.stdout.read(size)
            require(len(body) == size and read.stdout.read(1) == b"\n", "bounded Git blob receiving")
            pins[oid] = sha(body)
        read.stdin.close()
        require(read.wait() == 0, "read-only exact Git blob census")
    return [{path: {"path": path, "mode": mode, "git_blob": oid, "bytes": size, "sha256": pins[oid]}
             for path, (mode, oid, size) in tree.items()} for tree in trees]


def deltas(before, after):
    return [{"path": path, "before": before.get(path), "after": after.get(path)}
            for path in sorted(set(before) | set(after)) if before.get(path) != after.get(path)]


def owning_relation():
    raw = blob(RESULTS, RECEIVER)
    require(sha(raw) == "2e4477cf1fc8705e528a88491144212756920aca4a2dbbc2b62e8b47c2851c6a",
            "maintained receiver bytes differ")
    symbols = {"MAINTAINED_MEMBERS_SHA256", "M5_TO_MAINTAINED_SHA256", "E76_TO_MAINTAINED_SHA256",
               "CANONICAL_PACKAGE_PATHS_SHA256", "BUILD_OWNERS"}
    constants = {}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in symbols:
                constants[node.targets[0].id] = ast.literal_eval(node.value)
    require(set(constants) == symbols, "maintained owning source fingerprints")
    return pin(raw), constants


def portable_projection():
    exact = blob(BEFORE, BUILDER)
    require(exact == blob(AFTER, BUILDER), "source projection owner changed")
    tree = ast.parse(exact)
    group = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name == "standalone_internal_procedure_entries"]
    require(len(group) == 1, "pure source projection owner")
    ns = {"PurePosixPath": PurePosixPath, "re": re, "ContractError": ValueError}
    exec(compile(ast.Module(body=group, type_ignores=[]), "<exact pure package projection>", "exec"), ns)
    return ns["standalone_internal_procedure_entries"], pin(exact)


def retained_artifact(name, expected, members, projection):
    raw = blob(ARCHIVES, f"{PACKAGE_ROOT}/{name}")
    require(pin(raw) == expected, "actual retained M5 archive")
    canonical_sources = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) == members and archive.testzip() is None, "archive exact population and CRC")
        entries = {path: archive.read(path) for path in names}
        require(stat.S_IMODE(archive.getinfo(INVENTORY).external_attr >> 16) == 0o644
                and all(item.compress_type == zipfile.ZIP_DEFLATED for item in archive.infolist()),
                "exact retained archive mode and method")
        inventory_raw = entries.pop(INVENTORY)
        inventory = json.loads(inventory_raw)
        require(inventory["source"] == {"commit": BEFORE, "tree": BEFORE_TREE, "worktree_state": "clean"},
                "historical embedded retained artifact source")
        entries_pins = {row["path"]: {k: row[k] for k in ("bytes", "sha256")} for row in inventory["members"]}
        require(entries_pins == {name: pin(value) for name, value in entries.items()}, "actual member identities")
        shared = {name: value for name, value in entries.items() if name != GENERATED}
        for path, value in entries.items():
            if path == GENERATED:
                owner = CONTRACT
            elif name.endswith(".skill") and path.startswith("internal-procedures/"):
                owner = f"skills/{PurePosixPath(path).stem}/SKILL.md"
            elif name.endswith(".skill"):
                owner = "skills/implementaudit/" + path
            else:
                owner = path
            source = blob(BEFORE, owner)
            require(source == blob(AFTER, owner), "maintained package source changed")
            role_mode = 0o755 if owner.startswith("skills/implementaudit/scripts/") else 0o644
            if name.endswith(".skill") and path.startswith("internal-procedures/"):
                require(projection([(owner, source, role_mode)]) == [(path, value, role_mode)],
                        "exact standalone four child skill projection")
            else:
                require(value == source, "exact archive member source identity")
            require(stat.S_IMODE(archive.getinfo(path).external_attr >> 16) == role_mode,
                    "retained package mode")
            canonical_sources.append(owner)
        require(len(shared) == (70 if name.endswith(".skill") else 73), "member source roles")
    return {"artifact": pin(raw), "embedded_source": inventory["source"], "members": members,
            "inventory": pin(inventory_raw), "noninventory_members_source_identical_at_both_refs": members - 1}, sorted(canonical_sources)


def main():
    require(git("rev-parse", f"{BEFORE}^{{tree}}", f"{AFTER}^{{tree}}").decode().splitlines() ==
            [BEFORE_TREE, AFTER_TREE], "exact source identities")
    rel_pin, owner = owning_relation()
    trees = [git_tree(ref) for ref in (BEFORE, AFTER, EARLIER)]
    before, after, earlier = tree_byte_pins(trees)
    require((len(before), sum(row["bytes"] for row in before.values())) == (1766, 167023692)
            and (len(after), sum(row["bytes"] for row in after.values())) == (1778, 167283667)
            and sha(encode([after[p] for p in sorted(after)]))
            == owner["MAINTAINED_MEMBERS_SHA256"], "sealed maintained source members")
    changed, prior = deltas(before, after), deltas(earlier, after)
    require(len(changed) == 16 and len(prior) == 14
            and sha(encode(changed)) == owner["M5_TO_MAINTAINED_SHA256"]
            and sha(encode(prior)) == owner["E76_TO_MAINTAINED_SHA256"], "owning exact cumulative source deltas")

    projection, builder = portable_projection()
    plugin, closure = retained_artifact("IMPLEMENTAUDIT.plugin.zip", {"bytes":584971,
        "sha256":"a43f018d4d3cc6d6257eeacfd8b5b834588410564ac33b0c8022d01a0ca71e58"}, 75, projection)
    standalone, compatible_sources = retained_artifact("IMPLEMENTAUDIT.skill", {"bytes":580360,
        "sha256":"d1b89ec4113b0c57d925e2f5aeec16c1baa471985b918e6fc3e54e808fad7f1e"}, 72, projection)
    require(len(closure) == len(set(closure)) == 74
            and sha(encode(closure)) == owner["CANONICAL_PACKAGE_PATHS_SHA256"]
            and set(compatible_sources) <= set(closure), "exact owning package source population")
    extra = [*owner["BUILD_OWNERS"], *TOOL_SOURCES, APPROVAL]
    require(all(before[p] == after[p] for p in [*closure, *extra]), "exact package dependency drift")
    policy = json.loads(blob(AFTER, CONTRACT))
    require(policy["budget_revision"]["revision"] == 4
            and policy["budget_revision"]["owner_approval"]["sha256"] == after[APPROVAL]["sha256"]
            and all(r["cap_bytes"] == 589824 and r["reserve_bytes"] == 2000 for r in policy["budgets"].values()),
            "maintained original v4 budget pins")

    decision = blob(RESULTS, M5)
    require(all(value in decision for value in (BEFORE.encode(), BEFORE_TREE.encode(),
                                                plugin["artifact"]["sha256"].encode(),
                                                standalone["artifact"]["sha256"].encode())),
            "original M5 Root source/package decision")
    output = {
        "schema": "dg16.m5.maintained-source-package-dependency-receiving.v1",
        "old": {"commit": BEFORE, "tree": BEFORE_TREE}, "maintained": {"commit": AFTER, "tree": AFTER_TREE},
        "actual_original_M5_decision": pin(decision), "maintained_receiving_source": rel_pin, "canonical_builder": builder,
        "owning_fingerprints": owner, "canonical_package_source_paths": closure,
        "exact_unchanged_build_install_and_policy_source_owners": {p: after[p] for p in extra},
        "changed_maintained_source_paths": [r["path"] for r in changed],
        "unchanged_product_git_members": sum(before.get(p) == r for p, r in after.items()),
        "historical_package_bodies": {"canonical_plugin": plugin, "standalone_compatibility": standalone},
        "static_dependency_relation_recommended": "EXACT_NONPACKAGE_SOURCE_RELATION_ONLY",
        "source_only_package_leg": "NOT_TRIGGERED_BY_THIS_DIFF",
        "maintained_archive_built_here": False, "maintained_installed_or_host_occurrence": False,
        "maintained_v5_binding_issued_here": False, "protected_operation_or_original_award": False,
    }
    sys.stdout.buffer.write((json.dumps(output, sort_keys=True, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
