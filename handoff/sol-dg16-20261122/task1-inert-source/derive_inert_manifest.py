"""Reproduce a prospective inert Task 1 manifest from exact public Git data."""

import ast
from collections import Counter, defaultdict
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys
import tarfile
import types
import unittest
import zipfile


RESULTS = "6431a1d1e067ab37e4f461caa4a61890d69e7c14"
RESULTS_TREE = "24ac6f1625d19e3f33c94c1ef6cdf352f293ec6e"
RESULTS_ROOT = "handoff/pro-executor-results-20261115"
RECOVERY = f"{RESULTS_ROOT}/continuing-execution-20261122-45-recovery3"
RESTORATION = f"{RESULTS_ROOT}/continuing-execution-20261122-46-task1-r2"
SUBJECT = "test-support/g132-original-joint-source"
SPEC = f"{RECOVERY}/source-snapshots/{SUBJECT}/SOURCE_ONLY_INPUT_SPEC.json"
R2 = f"{RESTORATION}/{SUBJECT}/restoration/derive_joint_source.py"
TEST = f"{RESTORATION}/{SUBJECT}/tests/test_joint_source.py"
SPEC_PIN = {"bytes": 73228, "sha256": "d85b1c8a68e46b917595511a720efe0e0d26ba85c3d81eef9c7ceb23c14758a7"}
R2_PIN = {"bytes": 23942, "sha256": "081a844e9d5a9877439a2f6490a9452b4dea73f2dfec059adeeda365ec9a30e4"}
TEST_PIN = {"bytes": 23009, "sha256": "3f13a9575ec75ee3aad3a9e1f2fa9baf82ff44e96a9f6eab3d86f06c6c5e8457"}
PLAN = "dependencies/installation/PURE_SOURCE_PLAN.json"
OLD = ("compose", "g3", "profile", "proof", "run")
GROUPS = ("baseline", "owners", "full_before")
SINGLES = ("composer", "runtime", "reverse_map", "generator")
ARCHIVE = re.compile(r"\.(zip|tar\.(?:gz|xz)|tgz)(?:\.part(\d+))?$", re.I)
ARCHIVE_SCOPE = re.compile(r"g132|source[-_ ](?:baseline|custody|receiving|evidence)|"
                           r"public[-_ ]qualification|original[-_ ]public[-_ ]source", re.I)
MAX_CONTAINER = 32 * 1024 ** 2
MAX_EXPANDED = 128 * 1024 ** 2


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(["git", *args])


def pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def blob(ref_path):
    return git("cat-file", "blob", ref_path)


def exact(path, expected):
    raw = blob(f"{RESULTS}:{path}")
    require(pin(raw) == expected, f"public pin mismatch: {path}")
    return raw


class PublicCorpus:
    """Read only Git tree members and matching archive payloads as data."""

    def __init__(self, pins):
        self.pins = defaultdict(set)
        for row in pins:
            self.pins[row["bytes"]].add(row["sha256"])
        self.members = {}
        self.counts = Counter()

    def add(self, raw, locator):
        if len(raw) in self.pins:
            digest = pin(raw)["sha256"]
            if digest in self.pins[len(raw)]:
                self.members.setdefault(digest, (raw, locator))

    def member(self, size, name, depth):
        return size in self.pins or (depth > 0 and size <= MAX_CONTAINER and ARCHIVE.search(name))

    def read_zip(self, stream, locator, depth):
        with zipfile.ZipFile(stream) as archive:
            entries = archive.infolist()
            if len(entries) > 5000 or sum(x.file_size for x in entries) > MAX_EXPANDED:
                self.counts["bounded_container"] += 1
                return
            self.counts["zip"] += 1
            for ordinal, row in enumerate(entries):
                if row.is_dir() or row.flag_bits & 1:
                    continue
                self.counts["entries"] += 1
                if self.member(row.file_size, row.filename, depth):
                    with archive.open(row) as reader:
                        content = reader.read(row.file_size + 1)
                    self.inspect(content, row.filename, [*locator, ["zip", ordinal]], depth)

    def read_tar(self, stream, locator, depth):
        with tarfile.open(fileobj=stream, mode="r|*") as archive:
            self.counts["tar"] += 1
            expanded = 0
            for ordinal, row in enumerate(archive):
                expanded += row.size
                if ordinal >= 5000 or expanded > MAX_EXPANDED:
                    self.counts["bounded_container"] += 1
                    return
                if row.isfile():
                    self.counts["entries"] += 1
                    if self.member(row.size, row.name, depth):
                        with archive.extractfile(row) as reader:
                            content = reader.read(row.size + 1)
                        self.inspect(content, row.name, [*locator, ["tar", ordinal]], depth)

    def inspect(self, raw, name, locator, depth):
        self.add(raw, locator)
        if depth > 0 and ARCHIVE.search(name):
            self.scan(raw, locator, depth - 1)

    def scan(self, raw, locator, depth):
        if len(raw) > MAX_CONTAINER:
            self.counts["bounded_container"] += 1
            return
        stream = io.BytesIO(raw)
        try:
            if zipfile.is_zipfile(stream):
                self.read_zip(stream, locator, depth)
            else:
                stream.seek(0)
                self.read_tar(stream, locator, depth)
        except (tarfile.TarError, zipfile.BadZipFile, EOFError, RuntimeError, OSError):
            self.counts["unreadable_format"] += 1

    def receive(self):
        require(git("rev-parse", f"{RESULTS}^{{tree}}").decode().strip() == RESULTS_TREE,
                "historical results tree changed or absent")
        archives = defaultdict(list)
        tree = git("ls-tree", "-r", "--long", RESULTS, "--", RESULTS_ROOT).decode()
        for row in tree.splitlines():
            header, name = row.split("\t", 1)
            mode, kind, oid, size = header.split()
            if kind != "blob":
                continue
            size = int(size)
            if size in self.pins and mode in ("100644", "100755"):
                self.counts["same_size_tree_blobs"] += 1
                self.add(blob(oid), ["public_git_blob", name, oid])
            match = ARCHIVE.search(name)
            if match and ARCHIVE_SCOPE.search(name):
                key = re.sub(r"\.part\d+$", "", name)
                archives[key].append((int(match[2] or 0), oid, size))
        self.counts["public_archive_groups"] = len(archives)
        for name, parts in sorted(archives.items()):
            parts.sort()
            if len(parts) > 40 or sum(row[2] for row in parts) > MAX_CONTAINER:
                self.counts["bounded_container"] += 1
                continue
            oids = [row[1] for row in parts]
            self.scan(b"".join(blob(oid) for oid in oids), ["public_git_archive", name, oids], 2)


def roles(spec):
    for group in GROUPS:
        for key, row in sorted(spec[group].items()):
            yield group, key, {k: row[k] for k in ("bytes", "sha256")}
    for key in SINGLES:
        yield key, None, {k: spec[key][k] for k in ("bytes", "sha256")}


def checked_module(raw, name):
    loaded = types.ModuleType(name)
    sys.modules[name] = loaded
    # Only the exact reviewed R2 source and unit-test module reach this call.
    exec(compile(raw, name, "exec", dont_inherit=True), loaded.__dict__)
    return loaded


def test_pure_r2(source, test_raw, runtime):
    package = types.ModuleType("restoration")
    package.derive_joint_source = source
    sys.modules["restoration"] = package
    tests = checked_module(test_raw, "pinned_task1_r2_tests")
    suite = unittest.TestSuite()
    names = ("Projection", "ProjectionRepair")
    for name in names:
        for method in unittest.defaultTestLoader.getTestCaseNames(getattr(tests, name)):
            if method != "test_pinned_method_inherits_compiler_context_without_running_it":
                suite.addTest(getattr(tests, name)(method))
    log = io.StringIO()
    outcome = unittest.TextTestRunner(stream=log, verbosity=1).run(suite)
    require(outcome.wasSuccessful(), log.getvalue())
    parsed = ast.parse(runtime)
    cls = next(node for node in parsed.body if isinstance(node, ast.ClassDef) and
               node.name == "CurrentSources")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and
                  node.name == "module")
    calls = [node for node in ast.walk(method) if isinstance(node, ast.Call) and
             isinstance(node.func, ast.Name) and node.func.id == "compile"]
    compile_args = [(len(node.args), len(node.keywords)) for node in calls]
    require(compile_args == [(3, 0)], "pinned runtime compile context changed")
    code = compile(runtime, "<inert pinned runtime>", "exec", dont_inherit=True)
    for name in ("CurrentSources", "module"):
        code = next(const for const in code.co_consts if isinstance(const, types.CodeType)
                    and const.co_name == name)
    flag = source._COMPILER_FLAGS
    require(code.co_flags & flag == flag, "pinned runtime future annotations flag changed")
    return {"tests": outcome.testsRun, "failures": len(outcome.failures), "errors": len(outcome.errors),
            "compiler_inherits_via_three_argument_call": True}


def derive(source, inventory):
    plan = json.loads(inventory["baseline", PLAN])
    outcomes = {}
    for family in OLD:
        recipe = plan[family]
        full = inventory["full_before", family]
        expected = inventory["baseline", f"dependencies/installation/pure/{family}.py"]
        require(pin(full) == {"bytes": recipe["source_bytes"], "sha256": recipe["source_sha256"]}
                and pin(expected) == {"bytes": recipe["projection_bytes"], "sha256": recipe["projection_sha256"]},
                f"historical plan byte descriptors differ: {family}")
        comparison = source.project_exact(full, recipe["declarations"])
        require(comparison == expected, f"historical bounded projection differed: {family}")
        outcomes[family] = {"source": pin(full), "projection": pin(comparison),
                            "byte_equal_to_published_projection": True}
    return outcomes, plan


def source_contract(source, inventory, manifest):
    pins = {}
    for row in manifest:
        group, member = row["role"], row["member"]
        if member is None:
            pins[group] = row["input"]
        else:
            pins.setdefault(group, {})[member] = row["input"]
    logical = pathlib.PurePosixPath("/inert-roles-unmaterialized")
    locations = {role: str(logical / role) for role in (*GROUPS, *SINGLES, "destination")}
    host_path = source.Path
    try:
        # Only the pure POSIX role grammar is checked. The filesystem receiver is never called.
        source.Path = pathlib.PurePosixPath
        entries, trees, _ = source._contract(source._json(canonical(pins)), source._json(canonical(locations)))
    finally:
        source.Path = host_path
    require(set(entries) == set(inventory) and len(trees) == 3, "R2 role contract mismatch")
    require(all(pin(inventory[key]) == expected for key, (_, expected) in entries.items()),
            "R2 checked pin table mismatches public bytes")
    return {"entries": len(entries), "group_trees": len(trees), "destination_materialized": False, "path_model": "PurePosixPath"}


def module_policy(runtime, family):
    tree = ast.parse(runtime)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "CurrentSources")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "module")
    branch = next(node for node in method.body if isinstance(node, ast.If)
                  and ast.unparse(node.test) == f"name == '{family}'")
    bindings = set()
    for node in ast.walk(branch):
        if isinstance(node, ast.keyword) and node.arg:
            bindings.add(node.arg)
        if (isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store)
                and isinstance(node.value, ast.Name) and node.value.id == "namespace"
                and isinstance(node.slice, ast.Constant)):
            bindings.add(node.slice.value)
    return {"line": branch.lineno, "bindings": sorted(bindings)}


def uses_name(source, raw, declaration, dependency):
    module = source._Module(raw)
    node = module.declaration(declaration)
    table = source._symbols(module.segment(node).decode("utf-8"))
    require(dependency in source._references(table), "G3 dependency chain changed")
    return node.lineno

def compare_selected_declarations(source, historical, prospective):
    left, right = (ast.parse(raw).body for raw in (historical, prospective))
    left_names, right_names = ([tuple(source._declared(node)) for node in group] for group in (left, right))
    left_nodes = {name: ast.dump(node) for node, names in zip(left, left_names) for name in names}
    right_nodes = {name: ast.dump(node) for node, names in zip(right, right_names) for name in names}
    return {
        "same_source_ordered_declaration_groups": left_names == right_names,
        "added_declarations": sorted(right_nodes.keys() - left_nodes.keys()),
        "removed_declarations": sorted(left_nodes.keys() - right_nodes.keys()),
        "changed_declaration_ast": sorted(name for name in left_nodes.keys() & right_nodes.keys()
                                          if left_nodes[name] != right_nodes[name]),
        "raw_projection_equal": historical == prospective,
        "semantic_or_original_equivalence_qualified": False,
    }

def after_basis(source, inventory, plan):
    selected = {"compose": ("composer", None), "g3": ("owners", "g3_receiving.py"),
                "profile": ("owners", "host_utility.py"), "proof": ("owners", "proof_consumer.py"),
                "run": ("owners", "run.py")}
    runtime = inventory["runtime", None]
    compose_policy = module_policy(runtime, "compose")
    g3_policy = module_policy(runtime, "g3")
    require(compose_policy["bindings"] == ["W", "compile", "templates"], "changed compose namespace contract")
    require(g3_policy["bindings"] == ["current_original_scope_body"], "changed G3 namespace contract")
    results = {}
    for family, role in selected.items():
        raw, recipe = inventory[role], plan[family]
        roots, supplied = recipe["roots"], recipe["supplied"]
        changed_roots = []
        if family == "compose":
            require(source_refusal(source, raw, roots, supplied) == "empty roots or root also supplied",
                    "unlabelled compose baseline change")
            changed_roots = sorted(set(roots).intersection(supplied))
            require(changed_roots == ["W", "templates"] and set(supplied) == set(compose_policy["bindings"]),
                    "compose supplied-only provenance missing")
            roots = [root for root in roots if root not in supplied]
        if family == "g3":
            refusal = source_refusal(source, raw, roots, supplied)
            require(refusal == "unexplained or unsupported external: Path", "G3 red discriminator changed")
            bad_root = "validate_public_scope"
            require(source_refusal(source, raw, [bad_root], supplied) == refusal,
                    "isolated G3 root no longer discriminates")
            checked = 0
            for root in roots:
                if root != bad_root:
                    source.projection_basis(raw, [root], supplied)
                    checked += 1
            results[family] = {"disposition": "REFUSED_UNBOUND_EXTERNAL",
                               "first_refusal": refusal, "root": bad_root,
                               "dependency_chain": [bad_root, "scope_basis", "Path"],
                               "root_line": uses_name(source, raw, bad_root, "scope_basis"),
                               "use_line": uses_name(source, raw, "scope_basis", "Path"),
                               "other_roots_individually_derived": checked,
                               "runtime_branch": g3_policy, "source": pin(raw),
                               "root_selections_equal": True, "supplied_names_equal": True,
                               "declaration_and_semantic_comparison": "WITHHELD_NO_COMPLETE_PROJECTION"}
        else:
            basis = source.projection_basis(raw, roots, supplied)
            historical = inventory["baseline", f"dependencies/installation/pure/{family}.py"]
            comparison = compare_selected_declarations(source, historical, basis.projection)
            require(comparison["same_source_ordered_declaration_groups"], f"changed declaration selection: {family}")
            results[family] = {"disposition": "BOUNDED_STATIC_DIGEST_ONLY", "source": pin(raw),
                               "projection": dict(basis.projection_pin), "roots": len(basis.roots),
                               "declarations": len(basis.declarations),
                               "external_names": len(basis.external_names),
                               "root_selections_equal": list(basis.roots) == recipe["roots"],
                               "supplied_names_equal": set(basis.supplied) == set(recipe["supplied"]),
                               "declaration_comparison": comparison}
            if family == "compose":
                results[family].update(historical_recipe_refusal="empty roots or root also supplied",
                                       prospective_supplied_only=changed_roots,
                                       runtime_branch=compose_policy)
    return results


def source_refusal(source, raw, roots, supplied):
    try:
        source.projection_basis(raw, roots, supplied)
    except source.Refusal as error:
        return str(error)
    raise ValueError("expected source refusal")

def assemble():
    spec_raw = exact(SPEC, SPEC_PIN)
    spec = json.loads(spec_raw)
    r2 = exact(R2, R2_PIN)
    test = exact(TEST, TEST_PIN)
    bindings = list(roles(spec))
    require(Counter(g for g, _, _ in bindings) ==
            {"baseline": 175, "owners": 6, "full_before": 5, "composer": 1,
             "runtime": 1, "reverse_map": 1, "generator": 1}, "wrong historical role population")
    corpus = PublicCorpus(pin for _, _, pin in bindings)
    corpus.receive()
    inventory, manifest = {}, []
    for group, key, wanted in bindings:
        if group == "generator":
            require(wanted["sha256"] not in corpus.members, "historical generator candidate needs review")
            raw, locator = r2, ["public_git_blob", R2, "74324a975abbaaa46b666773b3eda175452c52c2"]
        else:
            require(wanted["sha256"] in corpus.members, f"unresolved exact input: {group}/{key}")
            raw, locator = corpus.members[wanted["sha256"]]
            require(pin(raw) == wanted, "public corpus byte binding changed")
        inventory[group, key] = raw
        manifest.append({"role": group, "member": key, "input": pin(raw), "locator": locator,
                         "exact_historical": group != "generator"})
    source = checked_module(r2, "pinned_task1_r2")
    controls = test_pure_r2(source, test, inventory["runtime", None])
    outcomes, plan = derive(source, inventory)
    return inventory, manifest, outcomes, controls, dict(corpus.counts), plan


def main():
    inventory, manifest, outcomes, controls, counts, plan = assemble()
    source = sys.modules["pinned_task1_r2"]
    role_contract = source_contract(source, inventory, manifest)
    after = after_basis(source, inventory, plan)
    out = {
        "schema": "dg16.prospective-task1-r2.inert-manifest.v1",
        "results_commit": RESULTS, "results_tree": RESULTS_TREE, "spec": SPEC_PIN, "generator": R2_PIN,
        "scope": "OFFLINE_PUBLIC_INPUT_BYTES_AND_HISTORICAL_PROJECTION_COMPARISON",
        "historical_input_roles_matched": 189, "prospective_roles": len(inventory),
        "prospective_bytes": sum(map(len, inventory.values())),
        "scan": counts, "derived_historical_projection_checks": outcomes, "pure_controls": controls,
        "actual_r2_role_contract": role_contract, "prospective_static_after_basis": after,
        "members": manifest, "historical_generator_recovered": False,
        "physical_receiver_run": False, "full_after_basis_derived": False,
        "source_adoption": False, "protected_readiness": False, "original_awards": [],
    }
    sys.stdout.buffer.write(canonical(out))


if __name__ == "__main__":
    main()
