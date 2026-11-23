"""Assemble only the Root-admitted 17 public projections as inert data."""
import ast
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("held_scope_trial", HERE / "probe_g3_held_scope_projection.py")
g3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g3)
public = g3.public
DECISION = "a2e9fb082af2804286ffe12c2e7914e077039605"
INDEX = "JOINT_AFTER_BASIS_INPUTS.json"
MAINTAINED = {
    "compose": ("composer", None),
    "g3": ("owners", "g3_receiving.py"),
    "profile": ("owners", "host_utility.py"),
    "proof": ("owners", "proof_consumer.py"),
    "run": ("owners", "run.py"),
}


def inputs(admission, index_raw):
    manifest_raw = (HERE / "INERT_MANIFEST.json").read_bytes()
    manifest = json.loads(manifest_raw)
    index = json.loads(index_raw)
    public.require(public.pin(index_raw) == {"bytes": admission["index_bytes"],
                                            "sha256": admission["index_sha256"]}, "admitted index pin")
    public.require(public.pin(manifest_raw) == index["inert_manifest"] and
                   public.pin(manifest_raw)["sha256"] == public.MANIFEST_SHA256, "exact input manifest pin")
    public.require(len(manifest["members"]) == index["public_input_roles"] ==
                   admission["public_input_roles"] == 190, "input manifest population")
    rows = {(r["role"], r["member"]): r for r in manifest["members"]}
    public.require(len(rows) == 190, "duplicate input role")
    cache = {}

    def read(role, member=None):
        row = rows[role, member]
        kind, _, locator, *trail = row["locator"]
        if kind == "public_git_blob":
            public.require(not trail, "blob trail")
            raw = public.git_blob(locator)
        else:
            public.require(kind == "public_git_archive" and 0 < len(locator) <= 40, "archive locator")
            key = tuple(locator)
            if key not in cache:
                cache[key] = b"".join(public.git_blob(part) for part in locator)
            raw = cache[key]
            public.require(len(raw) <= public.ARCHIVE_MAX, "Git archive size")
            for fmt, ordinal in trail:
                raw = public.archived_member(raw, fmt, ordinal)
        public.require(public.pin(raw) == row["input"], "selected input role digest")
        return raw

    return index, read


def runtime_suppliers(raw, families):
    cls = next(node for node in ast.parse(raw).body
               if isinstance(node, ast.ClassDef) and node.name == "CurrentSources")
    module = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "module")
    initial = next(node.value for node in module.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "namespace" for t in node.targets))
    public.require(isinstance(initial, ast.Call) and ast.unparse(initial.func) == "dict", "fixed runtime namespace")
    common = {item.arg for item in initial.keywords}
    bindings = {family: set() for family in families}
    for branch in module.body:
        if not isinstance(branch, ast.If):
            continue
        added = set()
        for statement in branch.body:
            for node in ast.walk(statement):
                if (isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store)
                        and isinstance(node.value, ast.Name) and node.value.id == "namespace"):
                    added.add(ast.literal_eval(node.slice))
                if isinstance(node, ast.Call) and ast.unparse(node.func) == "namespace.update":
                    public.require(not node.args and all(k.arg for k in node.keywords), "fixed supplier update")
                    added.update(k.arg for k in node.keywords)
        if not added:
            continue
        test = branch.test
        public.require(isinstance(test, ast.Compare) and ast.unparse(test.left) == "name"
                       and len(test.ops) == 1 and isinstance(test.ops[0], (ast.Eq, ast.In)), "supplier selection")
        target = ast.literal_eval(test.comparators[0])
        for family in (target,) if isinstance(test.ops[0], ast.Eq) else target:
            public.require(family in bindings, "unknown supplier family")
            bindings[family].update(added)
    return common, bindings


def assemble(admission, index_raw):
    index, read = inputs(admission, index_raw)
    historical_plan = read("baseline", g3.PLAN)
    public.require(public.pin(historical_plan) == index["historical_plan"], "historical plan")
    plan = json.loads(historical_plan)
    families = index["families"]
    changed = admission["permitted_rederivations"]
    retained = set(admission["reuse_exact_bodies"])
    public.require(set(changed) == set(MAINTAINED) and not retained.intersection(changed)
                   and retained.union(changed) == set(families) == set(plan) and len(families) == 17,
                   "exact 17 admitted families")
    source = public.load_r2(read("generator"))
    common, bindings = runtime_suppliers(read("runtime"), families)
    archive_bodies, results = {}, {}
    for family, row in sorted(families.items()):
        historical = plan[family]
        roots, supplied = row["existing_roots"], row["supplied"]
        public.require((roots, supplied) == (historical["roots"], historical["supplied"])
                       and bindings[family] <= set(supplied) <= common.union(bindings[family]),
                       "declared and supplied runtime interfaces: " + family)
        original = read("baseline", "dependencies/installation/pure/" + family + ".py")
        public.require(public.pin(original) == row["historical_projection"], "historical projection: " + family)
        if family in retained:
            data = original
            mode = "REUSED_EXACT_BODY"
        else:
            raw = read(*MAINTAINED[family])
            if family == "g3":
                public.require(public.pin(raw) == row["maintained_source"], "exact maintained G3 source")
                old_read, new_read = (part.replace(b"\n", b"\r\n") for part in (g3.OLD_READ, g3.NEW_READ))
                public.require(raw.count(old_read) == 1 and new_read not in raw, "one reviewed G3 read")
                raw = raw.replace(old_read, new_read)
                old_pin = next(ast.literal_eval(n.value) for n in ast.parse(raw).body
                               if isinstance(n, ast.Assign) and any(
                                   isinstance(t, ast.Name) and t.id == "SCOPE_SHA" for t in n.targets))
                public.require(old_pin == "8c08f2aecd34f582f3662b5bc83b3d3a27cee33d2f17711ced868a1d7b11c96a",
                               "published G3 scope pin")
            elif family == "compose":
                corrections = row["prospective_supplied_only"]
                public.require(corrections == ["W", "templates"] and set(roots).intersection(supplied) ==
                               set(corrections), "fixed compose root correction")
                roots = [name for name in roots if name not in corrections]
            public.require(public.pin(raw) == row["after_source"], "admitted after-source: " + family)
            basis = source.projection_basis(raw, roots, supplied)
            public.require(list(basis.roots) == roots and set(basis.supplied) == set(supplied),
                           "projected interface: " + family)
            data = basis.projection
            public.require(public.pin(data) == changed[family], "Root-admitted output pin: " + family)
            mode = "REDERIVED_DECLARATIONS_ONLY"
        public.require(public.pin(data) == row["expected_projection"], "after-basis digest: " + family)
        parsed = ast.parse(data)
        public.require(all(isinstance(n, (ast.Assign, ast.FunctionDef, ast.ClassDef)) for n in parsed.body)
                       and not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(parsed)),
                       "inert declaration shape: " + family)
        key = family + ".source"
        archive_bodies[key] = data
        results[family] = {"path": key, **public.pin(data), "construction": mode, "roots": roots,
                           "supplied": supplied, "runtime_family_bindings": sorted(bindings[family])}
    body_bytes = sum(len(body) for body in archive_bodies.values())
    public.require(body_bytes == admission["expected_body_bytes_before_container_overhead"], "exact body total")
    archive_bodies["MANIFEST.json"] = public.canonical({
        "schema": "dg16.g3.inert-joint-projection-assembly.v1",
        "admission": DECISION, "input_index": public.pin(index_raw), "authority": "NONE",
        "source_body_count": len(results), "source_body_bytes": body_bytes,
        "projected_module_execution": False, "families": results,
    })
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_STORED) as z:
        for path, data in sorted(archive_bodies.items()):
            z.writestr(zipfile.ZipInfo(path), data)
    payload = output.getvalue()
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        public.require(z.testzip() is None and z.namelist() == sorted(archive_bodies),
                       "archive population and CRC")
        public.require(all(z.read(path) == data for path, data in archive_bodies.items()), "archive body readback")
    return payload


if __name__ == "__main__":
    raw = subprocess.check_output(["git", "show", DECISION + ":handoff/astra-dg16-dg18/CONTINUATION.json"])
    decision = json.loads(raw)["dependent_frontiers"]["DG16"]["joint_after_basis_trial"]
    public.require(decision["root_decision"] == "ADMIT_ONE_INERT_PUBLIC_SOURCE_ASSEMBLY" and
                   decision["state"] == "ADMITTED_RESULT_PENDING", "exact assembly admission")
    try:
        payload = assemble(decision, (HERE / INDEX).read_bytes())
    except ValueError as error:
        print("Assembly stopped: " + str(error), file=sys.stderr)
        raise SystemExit(1)
    sys.stdout.buffer.write(payload)
