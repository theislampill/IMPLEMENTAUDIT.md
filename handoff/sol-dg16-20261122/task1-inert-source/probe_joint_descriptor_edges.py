"""Compare Root-admitted DG16 descriptor edges entirely in memory."""
import ast
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("joint_inputs", HERE / "assemble_joint_after_basis.py")
joint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joint)
public = joint.public
ROOT = "82c365eee5bd4d5276a85897580b4d5a34b130c2"
PREFIX = "dependencies/installation/"
DISPUTED = {"assignments", "loader_bind", "parse"}


def document(ref):
    raw = subprocess.check_output(["git", "show", ref + ":handoff/astra-dg16-dg18/CONTINUATION.json"])
    return json.loads(raw)["dependent_frontiers"]["DG16"]


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def pinned_json(read, name):
    raw = read("baseline", name)
    parsed = json.loads(raw)
    public.require(wire(parsed) == raw, "original encoding: " + name)
    return raw, parsed


def exact_fields(before, after, permitted):
    public.require(set(before) == set(after), "field population drift")
    actual = {key for key in before if before[key] != after[key]}
    public.require(actual <= set(permitted), "unexpected fields: " + ", ".join(sorted(actual)))
    return sorted(actual)


def owner_pin_change(raw, field, before, after):
    tree = ast.parse(raw)
    candidates = [n for n in tree.body if isinstance(n, ast.Assign)
                  and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == field]
    public.require(len(candidates) == 1 and ast.literal_eval(candidates[0].value) == before, "owner index literal: " + field)
    old = before.encode()
    public.require(raw.count(old) == 1, "non-unique owner index literal: " + field)
    revised = raw.replace(old, after.encode())
    next_tree = ast.parse(revised)
    next_node = next(n for n in next_tree.body if isinstance(n, ast.Assign)
                     and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == field)
    public.require(ast.literal_eval(next_node.value) == after, "wrong replacement literal: " + field)
    next_node.value = candidates[0].value
    public.require(ast.dump(tree) == ast.dump(next_tree), "unrelated owner AST change: " + field)
    return public.pin(revised)


def projection_metadata(source, payload, suppliers):
    module = source._Module(payload)
    declarations = {name for n in module.tree.body for name in source._declared(n)}
    names = set()
    for node in module.tree.body:
        table = source._symbols(module.segment(node).decode())
        names.update(source._namespace_keys(node, table, module, set(suppliers)))
        names.update(source._references(table))
        names.update(source._class_fallbacks(node))
    return dict(declarations=sorted(declarations), external_names=sorted(names - declarations),
                functions=dict(source._function_hashes(module.tree.body)))


def lineage(read, historical, maintained, entry):
    def current_methods(raw):
        cls, = [c for c in ast.parse(raw).body if isinstance(c, ast.ClassDef) and c.name == "CurrentSources"]
        return {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    before, now = (current_methods(raw) for raw in (historical, maintained))
    public.require(ast.dump(before["_check_git_identity"]) == ast.dump(now["_check_git_identity"]),
                   "root entry lineage guard differs on selected runtime")
    roots = {ast.unparse(n.func) for n in ast.walk(ast.parse(entry))
             if isinstance(n, ast.Call) and ast.unparse(n.func).endswith(".CurrentSources")}
    public.require(roots == {"C.CurrentSources", "modules['current_pro_interfaces'].CurrentSources"},
                   "root entry CurrentSources route")
    for key in ("__init__", "_check_git_identity", "context", "receive_public", "work_root"):
        public.require(ast.dump(before[key].args) == ast.dump(now[key].args), "entry runtime signature: " + key)
    original = json.loads(read("baseline", PREFIX + "HOST_IDENTITY_UNISSUED.json"))
    public.require(original["state"] == "UNISSUED" and original["authority"] == "NONE", "historical host state")
    identity = [original["commit"], original["tree"], original["parent"]]
    commit = read("baseline", PREFIX + "git-candidate/" + identity[0] + ".commit")
    tree = read("baseline", PREFIX + "git-candidate/" + identity[1] + ".tree")
    def oid(kind, raw):
        return hashlib.sha1(f"{kind} {len(raw)}\0".encode() + raw).hexdigest()
    public.require(oid("commit", commit) == identity[0] and oid("tree", tree) == identity[1],
                   "historical candidate object identity")
    public.require(commit.splitlines()[0] == b"tree " + identity[1].encode()
                   and [x[7:].decode() for x in commit.splitlines() if x.startswith(b"parent ")] == [identity[2]],
                   "historical candidate parent edge")
    chain, = [ast.literal_eval(n.value) for n in ast.walk(now["_check_git_identity"])
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "chain" for t in n.targets)]
    public.require(chain[0] == identity[2], "historical lineage head")
    for index, name in enumerate(chain):
        ancestor = read("baseline", PREFIX + "git-lineage/" + name + ".commit")
        public.require(oid("commit", ancestor) == name, "historical lineage object")
        if index + 1 < len(chain):
            public.require([row[7:].decode() for row in ancestor.splitlines() if row.startswith(b"parent ")]
                           == [chain[index + 1]], "historical ancestor edge")
    return {"candidate_commit": identity[0], "candidate_tree": identity[1], "parent": identity[2],
            "historical_ancestors_checked": len(chain), "identical_lineage_guard_ast": True,
            "scope": "EXACT_HISTORICAL_UNISSUED_ENTRY_WITH_STATIC_MAINTAINED_RUNTIME_INTERFACE"}


def compare(admission, record):
    base = document(joint.DECISION)["joint_after_basis_trial"]
    _, read = joint.inputs(base, (HERE / joint.INDEX).read_bytes())
    plan_raw, plan = pinned_json(read, PREFIX + "PURE_SOURCE_PLAN.json")
    installation_raw, installation = pinned_json(read, PREFIX + "SOURCE_INDEX.json")
    composition_raw, composition = pinned_json(read, "COMPOSITION_SOURCE_INDEX.json")
    plan_pin = public.pin(plan_raw)
    public.require(installation["pure_plan"] == installation["files"]["PURE_SOURCE_PLAN.json"] == plan_pin,
                   "two exact historical plan references")
    source = public.load_r2(read("generator"))
    newer_plan = copy.deepcopy(plan)
    newer_installation = copy.deepcopy(installation)
    with zipfile.ZipFile(HERE / "JOINT_AFTER_BASIS.zip") as archive:
        manifest = json.loads(archive.read("MANIFEST.json"))
        public.require(set(manifest["families"]) == set(plan) == set(base["reuse_exact_bodies"])
                       .union(base["permitted_rederivations"]), "exact projection roster")
        changed_rows = {}
        codec = newer_plan["codec"]
        codec["roots"] = [name for name in codec["roots"] if name not in DISPUTED]
        codec["external_names"] = [name for name in codec["external_names"] if name not in DISPUTED]
        for family, expected in base["permitted_rederivations"].items():
            row = manifest["families"][family]
            payload = archive.read(row["path"])
            path = "pure/" + family + ".py"
            before = dict(bytes=plan[family]["projection_bytes"], sha256=plan[family]["projection_sha256"])
            public.require(before == installation["files"][path], "historical pure entry: " + family)
            public.require(public.pin(payload) == expected, "admitted changed body: " + family)
            input_row = json.loads((HERE / joint.INDEX).read_bytes())["families"][family]
            replacement = newer_plan[family]
            replacement.update(projection_bytes=expected["bytes"], projection_sha256=expected["sha256"],
                               source_bytes=input_row["after_source"]["bytes"],
                               source_sha256=input_row["after_source"]["sha256"],
                               roots=row["roots"], supplied=row["supplied"],
                               **projection_metadata(source, payload, row["supplied"]))
            newer_installation["files"][path] = expected
            changed_rows[family] = {
                "old": before, "new": expected,
                "plan_fields_changed": exact_fields(plan[family], replacement, plan[family]),
            }
    plan_changes = exact_fields(plan, newer_plan, set(changed_rows) | {"codec"})
    public.require(set(plan_changes) == set(changed_rows) | {"codec"}, "exact changed plan family set")
    codec_fields = exact_fields(plan["codec"], newer_plan["codec"], {"roots", "external_names"})
    public.require(codec_fields == ["external_names", "roots"], "codec metadata only")
    new_plan_pin = public.pin(wire(newer_plan))
    newer_installation["pure_plan"] = new_plan_pin
    newer_installation["files"]["PURE_SOURCE_PLAN.json"] = new_plan_pin
    changed_files = {"PURE_SOURCE_PLAN.json"} | {"pure/" + family + ".py" for family in changed_rows}
    public.require(set(exact_fields(installation["files"], newer_installation["files"], changed_files)) == changed_files
                   and exact_fields(installation, newer_installation, {"files", "pure_plan"}) == ["files", "pure_plan"],
                   "installation index field boundary")
    public.require(newer_installation["pure_plan"] == newer_installation["files"]["PURE_SOURCE_PLAN.json"],
                   "two prospective plan references")
    old_index, new_index = public.pin(installation_raw), public.pin(wire(newer_installation))
    record.update(plan={"old": plan_pin, "new": new_plan_pin, "changed_families": plan_changes,
                        "codec_fields": codec_fields, "changed_outputs": changed_rows},
                  installation={"old": old_index, "new": new_index,
                                "plan_locations": ["pure_plan", "files/PURE_SOURCE_PLAN.json"],
                                "changed_file_entries": sorted(changed_files)})
    entry = read("baseline", "source/current_root_entry.py")
    historical_runtime = read("baseline", "source/current_pro_interfaces.py")
    maintained = read("runtime")
    selected = admission["selected_maintained_runtime"]
    public.require(public.pin(maintained) == {"bytes": selected["bytes"], "sha256": selected["sha256"]}
                   and maintained == subprocess.check_output(["git", "show", selected["source"]]),
                   "exact selected maintained runtime")
    public.require(composition["installation_index_sha256"] == old_index["sha256"]
                   and composition["files"]["current_root_entry.py"] == public.pin(entry)
                   and composition["files"]["current_pro_interfaces.py"] == public.pin(historical_runtime),
                   "historical composition owner provenance")
    record["root_entry_lineage"] = lineage(read, historical_runtime, maintained, entry)
    digest = new_index["sha256"]
    newer_composition = copy.deepcopy(composition)
    entry_pin = owner_pin_change(entry, "INDEX", old_index["sha256"], digest)
    runtime_pin = owner_pin_change(maintained, "INDEX_SHA256", old_index["sha256"], digest)
    newer_composition["files"]["current_root_entry.py"] = entry_pin
    newer_composition["files"]["current_pro_interfaces.py"] = runtime_pin
    newer_composition["installation_index_sha256"] = digest
    public.require(exact_fields(composition["files"], newer_composition["files"],
                                {"current_root_entry.py", "current_pro_interfaces.py"}) ==
                   ["current_pro_interfaces.py", "current_root_entry.py"], "composition owner entries")
    public.require(exact_fields(composition, newer_composition, {"files", "installation_index_sha256"}) ==
                   ["files", "installation_index_sha256"], "composition field boundary")
    record.update(composition={"old": public.pin(composition_raw), "new": public.pin(wire(newer_composition)),
                               "root_entry": {"old": public.pin(entry), "after_literal": entry_pin},
                               "runtime": {"historical": public.pin(historical_runtime),
                                           "admitted_maintained": public.pin(maintained), "after_literal": runtime_pin}},
                  disposition="DESCRIPTOR_EDGES_CLOSED_AS_DATA")


if __name__ == "__main__":
    admission = document(ROOT)["joint_descriptor_check"]
    public.require(admission["decision"] == "ADMIT_ONE_DISPOSABLE_NONEXECUTING_DESCRIPTOR_CHECK",
                   "exact descriptor admission")
    result = {"schema": "dg16.g3.inert-descriptor-comparison.v1", "authority": "NONE", "admission": ROOT,
              "replacement_metadata_retained": False, "projected_module_execution": False}
    try:
        compare(admission, result)
    except (ValueError, KeyError) as error:
        result.update(disposition="STOPPED_AT_FIRST_UNRESOLVED_EDGE", first_unresolved_edge=str(error))
    sys.stdout.buffer.write(public.canonical(result))
