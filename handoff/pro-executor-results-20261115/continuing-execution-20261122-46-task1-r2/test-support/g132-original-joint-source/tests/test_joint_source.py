"""New, source-only receiver and projector controls. No historical owner is imported."""

import __future__
import ast
import hashlib
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

try:
    from restoration import derive_joint_source as source
except ImportError as exc:
    if exc.name != "restoration" and "cannot import name 'derive_joint_source'" not in str(exc):
        raise
    source = None


HEADER = b"# Exact bounded source projection; source module is never imported.\n"
FAMILIES = ("compose", "g3", "profile", "proof", "run")
OWNERS = ("g3_receiving.py", "host_utility.py", "nss_configuration.py",
          "operation.py", "proof_consumer.py", "run.py")
PLAN = "dependencies/installation/PURE_SOURCE_PLAN.json"
CONTEXT_PIN = "31900d5c98869e6a159febb380ff90187d1c5ea25eb25aba0b844462c6608f7f"


def pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def document(value):
    return json.dumps(value, sort_keys=True).encode()


class ContractCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(source, "the new restoration module must expose the Task 1 API")


class Receiver(ContractCase):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dest = self.root / "out"
        self.locations = {"destination": str(self.dest)}
        self.spec = {}
        self.paths = {}
        groups = {
            "baseline": [f"nested/item-{i}" for i in range(175)],
            "full_before": FAMILIES, "owners": OWNERS,
        }
        for group, names in groups.items():
            directory = self.root / group
            self.locations[group] = str(directory)
            self.spec[group] = {}
            for name in names:
                path = directory / (name + ".py" if group == "full_before" else name)
                path.parent.mkdir(parents=True, exist_ok=True)
                raw = f"{group}/{name}".encode()
                path.write_bytes(raw)
                self.paths[raw] = path
                self.spec[group][name] = pin(raw)
        for role in ("composer", "runtime", "reverse_map", "generator"):
            path = self.root / ("reverse_map.json" if role == "reverse_map" else role + ".py")
            raw = b'{"rows":[]}' if role == "reverse_map" else role.encode()
            path.write_bytes(raw)
            self.locations[role] = str(path)
            self.paths[raw] = path
            self.spec[role] = pin(raw)

    def receive(self):
        return source.receive_inputs(document(self.spec), document(self.locations))

    def assert_refused(self):
        with self.assertRaises(source.Refusal):
            self.receive()
        self.assertFalse(self.dest.exists())

    def test_exact_population_is_frozen_and_inputs_unchanged(self):
        def observe():
            return {raw: (path.stat().st_ino, path.stat().st_ctime_ns, pin(path.read_bytes()))
                    for raw, path in self.paths.items()}

        before = observe()
        bundle = self.receive()
        self.assertEqual(len(bundle.baseline), 175)
        self.assertEqual(set(bundle.owners), set(OWNERS))
        self.assertEqual(set(bundle.full_before), set(FAMILIES))
        self.assertEqual(bundle.full_before["profile"], b"full_before/profile")
        self.assertEqual(bundle.baseline["nested/item-21"], b"baseline/nested/item-21")
        self.assertEqual(bundle.generator, b"generator")
        self.assertEqual(bundle.reverse_map, b'{"rows":[]}')
        self.assertEqual(bundle.runtime, b"runtime")
        self.assertEqual(bundle.composer, b"composer")
        with self.assertRaises(TypeError):
            bundle.owners["run.py"] = b"other"
        self.assertEqual(observe(), before)
        self.assertFalse(self.dest.exists())

    def test_one_changed_byte(self):
        self.paths[b"composer"].write_bytes(b"composeR")
        self.assert_refused()

    def test_missing_location(self):
        del self.locations["runtime"]
        self.assert_refused()

    def test_extra_location(self):
        self.locations["spare"] = self.locations["runtime"]
        self.assert_refused()

    def test_missing_declared_role(self):
        del self.spec["owners"]["host_utility.py"]
        self.assert_refused()

    def test_undeclared_physical_member(self):
        (self.root / "baseline/unlisted").write_bytes(b"extra")
        self.assert_refused()

    def test_missing_physical_member(self):
        self.paths[b"baseline/nested/item-2"].unlink()
        self.assert_refused()

    def test_duplicate_keys_in_both_contracts(self):
        for spec, loc in (
            (b'{"owners":{},' + document(self.spec)[1:], document(self.locations)),
            (document(self.spec), b'{"owners":"/",'+ document(self.locations)[1:]),
        ):
            with self.subTest(), self.assertRaisesRegex(source.Refusal, "duplicate"):
                source.receive_inputs(spec, loc)
        self.assertFalse(self.dest.exists())

    def test_duplicate_key_in_authenticated_json_body(self):
        raw = b'{"rows":[{"k":1,"k":2}]}'
        Path(self.locations["reverse_map"]).write_bytes(raw)
        self.spec["reverse_map"] = pin(raw)
        self.assert_refused()

    def test_integer_descriptor_excludes_boolean(self):
        self.spec["runtime"]["bytes"] = True
        self.assert_refused()

    def test_path_aliases(self):
        actual = self.paths[b"composer"]
        for path in (str(actual) + "/../" + actual.name,
                     str(actual.parent) + "//" + actual.name, self.locations["runtime"]):
            with self.subTest(path=path):
                self.locations["composer"] = path
                self.assert_refused()

    def test_directory_symlink(self):
        alias = self.root / "aliased"
        alias.symlink_to(self.root / "owners", target_is_directory=True)
        self.locations["owners"] = str(alias)
        self.assert_refused()

    def test_single_hard_link_alias_outside_roster(self):
        os.link(self.paths[b"composer"], self.root / "another-name")
        self.assert_refused()

    def test_existing_destination(self):
        self.dest.mkdir()
        with self.assertRaises(source.Refusal):
            self.receive()
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_output_inside_declared_input_directory(self):
        self.locations["destination"] = str(self.root / "owners/unwritten")
        self.assert_refused()
        self.assertFalse(Path(self.locations["destination"]).exists())

    def test_output_alias_through_symlink_parent(self):
        alias = self.root / "output-parent"
        alias.symlink_to(self.root / "owners", target_is_directory=True)
        self.locations["destination"] = str(alias / "unwritten")
        self.assert_refused()
        self.assertFalse(Path(self.locations["destination"]).exists())

    def test_input_changed_after_its_read_is_refused_at_close(self):
        # Alter an already received synthetic member while a later member is read.
        real_read = os.read
        seen = []

        def displace_first(fd, size):
            data = real_read(fd, size)
            if data in self.paths and data not in seen:
                if len(seen) == 1:
                    self.paths[seen[0]].write_bytes(b"!" * len(seen[0]))
                seen.append(data)
            return data

        with patch.object(os, "read", displace_first):
            with self.assertRaisesRegex(source.Refusal, "changed"):
                self.receive()
        self.assertGreaterEqual(len(seen), 2)
        self.assertFalse(self.dest.exists())


class Projection(ContractCase):
    def test_shared_tuple_emits_once_in_source_order(self):
        raw = b"B, A = (1, 2)  # trailing\n\nOMIT = 7\n\ndef root():\n    return A + B\n"
        expected = HEADER + b"B, A = (1, 2)\n\ndef root():\n    return A + B\n"
        self.assertEqual(source.project_exact(raw, ["root", "A", "B"]), expected)
        basis = source.projection_basis(raw, ["root"], [])
        self.assertEqual(basis.projection, expected)
        self.assertEqual(set(basis.declarations), {"B", "A", "root"})

    def test_unicode_offsets_and_multiline_decorators(self):
        raw = "@(\n    decorate\n)\ndef f(x='café'):\n    return x   # tail\n".encode()
        basis = source.projection_basis(raw, ["f"], ["decorate"])
        self.assertEqual(basis.projection, HEADER + raw.split(b"   # tail")[0] + b"\n")
        self.assertEqual(basis.external_names, ("decorate",))
        self.assertEqual(basis.functions["f"], hashlib.sha256(
            ast.dump(ast.parse(raw).body[0]).encode()).hexdigest())
        self.assertEqual(dict(basis.source_pin), pin(raw))
        self.assertEqual(dict(basis.projection_pin), pin(basis.projection))

    def test_duplicate_name_including_unrequested_tuple_sibling(self):
        for raw in (b"A=0\nA,B=(1,2)\n", b"A,B=(1,2)\nif enabled:\n    A=0\n"):
            with self.subTest(raw=raw), self.assertRaisesRegex(source.Refusal, "ambiguous"):
                source.project_exact(raw, ["B"])

    def test_reject_runtime_unsupported_selected_construct(self):
        for raw in (b"A: int = 1\n", b"async def A(): pass\n", b"if enabled:\n    A=1\n"):
            with self.subTest(raw=raw), self.assertRaises(source.Refusal):
                source.project_exact(raw, ["A"])

    def test_import_in_selected_nested_body(self):
        raw = b"def root():\n    def inner():\n        import json\n    return inner\n"
        with self.assertRaisesRegex(source.Refusal, "import"):
            source.projection_basis(raw, ["root"], [])

    def test_shadowing_and_definition_time_dependencies(self):
        raw = b"""UNUSED = 0
SHADOW = 0
ITEM = 0
LEXICAL = 0
BASE = object
ANN = int
DEFAULT = 4
DECORATE = decorator
GLOBAL = 2
SUPPLIED = 88

@DECORATE
class Scope(BASE):
    def call(self, SHADOW: ANN=DEFAULT):
        LEXICAL = SHADOW
        def inner():
            return [ITEM + LEXICAL + GLOBAL for ITEM in range(SUPPLIED)]
        return inner()
"""
        result = source.projection_basis(raw, ["Scope"], ["SUPPLIED", "decorator"])
        self.assertEqual(result.declarations, ("BASE", "DEFAULT", "DECORATE", "GLOBAL", "Scope"))
        self.assertEqual(set(result.external_names), {"object", "decorator", "range", "SUPPLIED"})
        self.assertEqual(result.roots, ("Scope",))
        self.assertEqual(result.supplied, ("SUPPLIED", "decorator"))
        self.assertEqual(set(result.functions), {"Scope", "Scope.call", "Scope.call.inner"})

    def test_name_read_before_class_local_assignment_uses_module(self):
        raw = b"X=9\nclass Scope:\n    X=X\n    Y=X\n"
        self.assertEqual(source.projection_basis(raw, ["Scope"], []).declarations, ("X", "Scope"))

    def test_module_comprehension_index_is_a_local_binding(self):
        raw = b"ITEM=19\nITEMS=(3,4)\nVALUES={ITEM: ITEM*2 for ITEM in ITEMS}\n"
        self.assertEqual(source.projection_basis(raw, ["VALUES"], []).declarations, ("ITEMS", "VALUES"))
        self.assertEqual(source.project_exact(raw, ["ITEM"]), HEADER + b"ITEM=19\n")

    def test_outer_iterable_of_comprehension_still_reads_global(self):
        raw = b"ITEM=(1,2)\nVALUES=[ITEM for ITEM in ITEM]\n"
        self.assertEqual(source.projection_basis(raw, ["VALUES"], []).declarations, ("ITEM", "VALUES"))

    def test_class_body_can_capture_function_local(self):
        raw = b"outer=9\ndef root(outer):\n    class Nested:\n        result=outer\n    return Nested\n"
        self.assertEqual(source.projection_basis(raw, ["root"], []).declarations, ("root",))

    def test_class_annotation_without_value_leaves_lookup_unbound(self):
        raw = b"A=9\nclass Root:\n    A: int\n    result=A\n"
        self.assertEqual(source.projection_basis(raw, ["Root"], []).declarations, ("A", "Root"))

    def test_assignment_cannot_smuggle_an_extra_module_binding(self):
        with self.assertRaises(source.Refusal):
            source.project_exact(b"X=(Y:=1)\n", ["X"])

    def test_ambiguous_import_bindings_in_one_statement(self):
        raw = b"import os as hashlib, hashlib\ndef f(): return hashlib\n"
        with self.assertRaisesRegex(source.Refusal, "ambiguous"):
            source.projection_basis(raw, ["f"], [])

    def test_missing_external_refuses(self):
        with self.assertRaisesRegex(source.Refusal, "mystery"):
            source.projection_basis(b"def f(v=mystery): return v\n", ["f"], [])

    def test_import_is_external_only_for_actual_namespace(self):
        raw = b"import hashlib\ndef f(x): return hashlib.sha256(x)\n"
        self.assertEqual(source.projection_basis(raw, ["f"], []).external_names, ("hashlib",))
        for statement in (b"import absent", b"import os as hashlib"):
            name = statement.split()[-1]
            body = statement + b"\ndef f(): return " + name + b"\n"
            with self.subTest(statement=statement), self.assertRaises(source.Refusal):
                source.projection_basis(body, ["f"], [])

    def test_tuple_must_not_rebind_supplied_sibling(self):
        with self.assertRaisesRegex(source.Refusal, "supplied"):
            source.projection_basis(b"A,B=(1,2)\n", ["A"], ["B"])


class ProjectionRepair(ContractCase):
    def test_augmented_global_and_local_bindings(self):
        raw = b"""COUNT=1
LOCAL=2
CLOSED=3
def root(LOCAL):
    CLOSED=4
    def increment():
        global COUNT
        nonlocal CLOSED
        COUNT+=1
        CLOSED+=1
    LOCAL+=1
    return increment
"""
        result = source.projection_basis(raw, ["root"], [])
        self.assertEqual(result.declarations, ("COUNT", "root"))
        self.assertEqual(result.external_names, ())

    def test_unbound_augmented_global_requires_explicit_supply(self):
        raw = b"def root():\n    global COUNT\n    COUNT+=1\n"
        with self.assertRaisesRegex(source.Refusal, "COUNT"):
            source.projection_basis(raw, ["root"], [])
        self.assertEqual(source.projection_basis(raw, ["root"], ["COUNT"]).external_names, ("COUNT",))

    def test_actual_runtime_postpones_annotations_with_or_without_source_directive(self):
        body = b"Marker=1\nDEFAULT=3\ndef root(x: Marker=DEFAULT) -> Unknown: return x\n"
        for prefix in (b"", b"from __future__ import annotations\n"):
            with self.subTest(prefix=prefix):
                result = source.projection_basis(prefix + body, ["root"], [])
                self.assertEqual(result.declarations, ("DEFAULT", "root"))
                self.assertEqual(result.external_names, ())
                self.assertEqual(result.compiler_flags, __future__.annotations.compiler_flag)
                self.assertEqual(dict(result.runtime_pin), {
                    "bytes": 38161, "sha256": "46a3e27dccb0b30dc75b4d20b7dca659ec5f4f8ae2a3e04c9ec175e577d3b743"})
                for raw in (prefix + body, result.projection):
                    module = compile(raw, "<inert>", "exec", flags=result.compiler_flags, dont_inherit=True)
                    method = next(c for c in module.co_consts if isinstance(c, types.CodeType))
                    self.assertEqual(method.co_flags & result.compiler_flags, result.compiler_flags)
                    self.assertIn(("x", "Marker", "return", "Unknown"), module.co_consts)
                    self.assertNotIn("Unknown", module.co_names)

    def test_unrepresentable_module_compiler_feature_refuses(self):
        with self.assertRaisesRegex(source.Refusal, "compiler"):
            source.projection_basis(b"from __future__ import barry_as_FLUFL\ndef f(): return 1\n", ["f"], [])

    def test_literal_namespace_key_ignores_parameter_shadow(self):
        raw = b"LABEL=9\ndef root(LABEL): return globals()['LABEL']\n"
        result = source.projection_basis(raw, ["root"], [])
        self.assertEqual(result.declarations, ("LABEL", "root"))
        self.assertEqual(result.external_names, ("globals",))

    def test_literal_namespace_key_requires_real_dictionary_entry(self):
        for key in ("ABSENT", "len"):
            raw = f"def root(): return globals()[{key!r}]\n".encode()
            with self.subTest(key=key), self.assertRaisesRegex(source.Refusal, key):
                source.projection_basis(raw, ["root"], [])
            self.assertEqual(set(source.projection_basis(raw, ["root"], [key]).external_names), {"globals", key})
        raw = b"def root(): return globals()['json']\n"
        self.assertEqual(source.projection_basis(raw, ["root"], []).external_names, ("globals", "json"))

    def test_unspecified_namespace_operations_refuse(self):
        bodies = ("globals()[key]", "dict(globals(), LABEL=1)", "globals",
                  "root.__globals__['LABEL']", "globals().get('LABEL')")
        for expr in bodies:
            raw = f"def root(key): return {expr}\n".encode()
            with self.subTest(expr=expr), self.assertRaisesRegex(source.Refusal, "namespace"):
                source.projection_basis(raw, ["root"], [])

    def test_literal_namespace_entry_cannot_be_mutated_or_hidden_behind_a_shadow(self):
        for raw in (b"def root(): globals()['LABEL']=2\n",
                    b"def root(globals): return globals()['LABEL']\n",
                    b"globals=dict\ndef root(): return globals()['LABEL']\n"):
            with self.subTest(raw=raw), self.assertRaisesRegex(source.Refusal, "namespace"):
                source.projection_basis(raw, ["root"], [])

    def test_other_explicit_namespace_copies_and_function_rebinding_refuse(self):
        forms = ("vars()['LABEL']", "locals()['LABEL']", "vars", "types.FunctionType(root.__code__, ns)")
        for expr in forms:
            raw = f"def root(): return {expr}\n".encode()
            with self.subTest(expr=expr), self.assertRaisesRegex(source.Refusal, "namespace"):
                source.projection_basis(raw, ["root"], ["types", "ns"])
        pattern = b"""def receiver(): return LABEL
def root():
    environment = dict(globals(), LABEL=7)
    return types.FunctionType(receiver.__code__, environment, 'prior')
"""
        with self.assertRaisesRegex(source.Refusal, "namespace"):
            source.projection_basis(pattern, ["root"], ["types"])

    def test_postponed_namespace_annotation_is_never_a_runtime_lookup(self):
        raw = b"def root(x: globals()['OnlyAnnotation']): return x\n"
        result = source.projection_basis(raw, ["root"], [])
        self.assertEqual(result.declarations, ("root",))
        self.assertEqual(result.external_names, ())

    def test_pinned_method_inherits_compiler_context_without_running_it(self):
        context_raw = Path(os.environ["G132_TASK1_CONTEXT"]).read_bytes()
        self.assertEqual(pin(context_raw), {"bytes": 10536, "sha256": CONTEXT_PIN})
        raw = Path(json.loads(context_raw)["location_map"]["runtime"]).read_bytes()
        result = source.projection_basis(b"def synthetic(): return 1\n", ["synthetic"], [])
        self.assertEqual(pin(raw), dict(result.runtime_pin))
        code = compile(raw, "<inert pinned method>", "exec", dont_inherit=True)
        for name in ("CurrentSources", "module"):
            code = next(c for c in code.co_consts if isinstance(c, types.CodeType) and c.co_name == name)
        self.assertEqual(code.co_flags & __future__.annotations.compiler_flag, result.compiler_flags)
        cls = next(n for n in ast.parse(raw).body if isinstance(n, ast.ClassDef) and n.name == "CurrentSources")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "module")
        calls = [n for n in ast.walk(method) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "compile"]
        self.assertEqual([(len(n.args), n.keywords) for n in calls], [(3, [])])


class OldProjections(ContractCase):
    """Read only the five authenticated old bases and their stored projections."""

    def check_old(self, family):
        context_raw = Path(os.environ["G132_TASK1_CONTEXT"]).read_bytes()
        self.assertEqual(pin(context_raw), {"bytes": 10536, "sha256": CONTEXT_PIN})
        locations = json.loads(context_raw)["location_map"]
        baseline = Path(locations["baseline"])
        plan_body = (baseline / PLAN).read_bytes()
        self.assertEqual(pin(plan_body), {
            "bytes": 24504, "sha256": "567a0e69fd20dd875159c427aaa467ee87c1c7cb1cf4aaf517d6cad83ea3c314"})
        plan = json.loads(plan_body)[family]
        full = (Path(locations["full_before"]) / (family + ".py")).read_bytes()
        expected = (baseline / "dependencies/installation/pure" / (family + ".py")).read_bytes()
        self.assertEqual(pin(full), {"bytes": plan["source_bytes"], "sha256": plan["source_sha256"]})
        self.assertEqual(pin(expected), {"bytes": plan["projection_bytes"], "sha256": plan["projection_sha256"]})
        self.assertEqual(source.project_exact(full, plan["declarations"]), expected)

    def test_receive_declared_current_locations_unchanged(self):
        context_raw = Path(os.environ["G132_TASK1_CONTEXT"]).read_bytes()
        self.assertEqual(pin(context_raw), {"bytes": 10536, "sha256": CONTEXT_PIN})
        context = json.loads(context_raw)
        old_raw = Path(context["spec"]["path"]).read_bytes()
        self.assertEqual(pin(old_raw), {k: context["spec"][k] for k in ("bytes", "sha256")})
        historical = json.loads(old_raw)
        spec = {}
        for role in ("baseline", "owners", "full_before"):
            spec[role] = {member: {k: record[k] for k in ("bytes", "sha256")}
                          for member, record in historical[role].items()}
        for role in ("composer", "runtime", "reverse_map"):
            spec[role] = {k: historical[role][k] for k in ("bytes", "sha256")}
        generator = Path(source.__file__).absolute()
        spec["generator"] = pin(generator.read_bytes())
        self.assertNotEqual(spec["generator"]["sha256"], historical["generator"]["sha256"])
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "never-written"
            locations = dict(context["location_map"], generator=str(generator), destination=str(destination))
            bundle = source.receive_inputs(document(spec), document(locations))
            self.assertFalse(destination.exists())
        for role in ("baseline", "owners", "full_before"):
            self.assertEqual({k: pin(v) for k, v in getattr(bundle, role).items()}, spec[role])
        for role in ("composer", "runtime", "reverse_map", "generator"):
            self.assertEqual(pin(getattr(bundle, role)), spec[role])

    def test_old_compose(self):
        self.check_old("compose")

    def test_old_g3(self):
        self.check_old("g3")

    def test_old_profile(self):
        self.check_old("profile")

    def test_old_proof(self):
        self.check_old("proof")

    def test_old_run(self):
        self.check_old("run")
