#!/usr/bin/env python3
"""Complete original node85 inputs and fixed private effects; no native claim."""
import ast
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
spec = importlib.util.spec_from_file_location("installed_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
PROFILE = "CONTROLLED_TASK_INSTALLED_PAYLOAD_V1"
PROGRAM = "tests/installed-payload-self-contained.test.sh"
CHECKER = "scripts/check-installed-payload-self-contained.sh"


def literal_route_cases():
    """Expand only the pinned wrapper's literal run rows; never execute a body."""
    raw = (ROOT / PROGRAM).read_text(encoding="utf-8")
    body = raw.split('<<\'PY\'\n', 1)[1].split('\nPY\n', 1)[0]
    tree, values, cases = ast.parse(body), {}, []

    def value(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, (ast.List, ast.Tuple)):
            return tuple(value(item) for item in node.elts)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return value(node.left) + value(node.right)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -value(node.operand)
        if isinstance(node, ast.Subscript):
            return value(node.value)[value(node.slice)]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner, args = value(node.func.value), [value(arg) for arg in node.args]
            if type(owner) is str and not node.keywords and node.func.attr in ("replace", "rsplit"):
                return getattr(owner, node.func.attr)(*args)
        raise AssertionError("unsupported literal fixture expression: " + ast.dump(node))

    def bind(target, item):
        if isinstance(target, ast.Name):
            values[target.id] = item
        elif isinstance(target, ast.Tuple):
            assert len(target.elts) == len(item)
            for child, part in zip(target.elts, item):
                bind(child, part)
        else:
            raise AssertionError("unsupported literal fixture target")

    def rows(nodes):
        for node in nodes:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "valid":
                bind(node.targets[0], value(node.value))
            elif isinstance(node, ast.For):
                assert not node.orelse
                for item in value(node.iter):
                    bind(node.target, item)
                    rows(node.body)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "run":
                call = node.value
                result = dict(member="scripts/check-fixture.sh", source="owner", directory=False)
                result.update(zip(("name", "row", "expected", "member", "source", "directory"), map(value, call.args)))
                result.update((item.arg, value(item.value)) for item in call.keywords)
                cases.append(result)
    rows(tree.body)
    return cases


def private_population():
    """Static path/byte inventory of pinned literals, not an original result."""
    files, directories = {}, set()

    def directory(path):
        path = PurePosixPath(path)
        directories.add(str(path))
        directories.update(str(parent) for parent in path.parents if str(parent) != ".")

    def file(path, raw):
        files[str(path)] = len(raw)
        directory(PurePosixPath(path).parent)

    for row in literal_route_cases():
        root = PurePosixPath("private/route-" + row["name"])
        skill = root / "skills/implementaudit"
        target = skill / row["member"]
        if row["directory"]:
            directory(target)
        else:
            file(target, b"#!/usr/bin/env bash\ntrue\n")
        if row["name"] == "root-only":
            file(root / CHECKER, (ROOT / CHECKER).read_bytes())
        owner = skill / ("references/repo-state-comparison.md" if row["source"] == "owner" else "SKILL.md")
        file(owner, (row["row"] + "\n").encode())
    hardlink = PurePosixPath("private/route-hardlink")
    file(hardlink / "outside.sh", b"true\n")
    file(hardlink / "skills/implementaudit/scripts/check-fixture.sh", b"true\n")
    file(hardlink / "skills/implementaudit/references/repo-state-comparison.md",
         ("helper-route: scripts/check-fixture.sh|S|diagnosis|R|-|none|not-auto\n").encode())
    raw = (ROOT / PROGRAM).read_bytes()
    file("private/skills/implementaudit/SKILL.md", raw.split(b"<<'BAD'\n", 1)[1].split(b"\nBAD\n", 1)[0] + b"\n")
    file("private/backslash/skills/implementaudit/SKILL.md", b"Use skills\\implementaudit\\scripts\\repo-state.sh after install.\n")
    file("private/mixed/skills/implementaudit/SKILL.md", b"Use skills/implementaudit\\scripts/repo-state.sh after install.\n")
    return files, directories


class CatalogCases(unittest.TestCase):
    def test_complete_original85_has_explicit_profile_and_public_mode(self):
        A, _ = shared.load("installed_catalog", ROOT / "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = A.contract_for(PROFILE)
        except ValueError as error:
            self.fail("missing exact original85 profile: " + str(error))
        graph, scope, node = A.select_node(Q.WG, H.original("scripts/verify-package.sh"), P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][85]))
        self.assertEqual(node["source"], "bash " + PROGRAM + "\n")
        self.assertEqual(scope["nodes"], ["COMMAND:" + PROGRAM + ":0"])
        self.assertEqual(len(scope["omitted_nodes"]), 116)
        self.assertEqual(Q._FINITE_MODES["installed-payload"], PROFILE)
        self.assertEqual(set(contract["programs"]), {PROGRAM, CHECKER})
        self.assertEqual(contract["data"], ())
        self.assertEqual(contract["recursive"]["roots"], ("skills",))
        self.assertFalse(contract["recursive"]["optional"])


class InstalledFixture(shared.ProfileFixture):
    PROFILE = PROFILE

    def setUp(self):
        super().setUp()
        shutil.copytree(ROOT / "skills", self.source / "skills", dirs_exist_ok=True)
        self.restore_historical_inputs()
        if self.SOURCE_ADMISSION_ONLY:
            # The original29-route fixture binds the original route-owner data.
            name = "skills/implementaudit/references/repo-state-comparison.md"
            H.copy_input(name, self.source / name)

    def session(self, name="evidence", **options):
        return self.source_admission_session(Q.create_finite_leaf_session(
            self.source, self.base / name, profile=self.profile, **options))

    def new_member(self, raw=b"ordinary added input\n", name=".added/.member"):
        path = self.source / "skills" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path


class AdmissionCases(InstalledFixture, unittest.TestCase):
    def test_all_persistent_private_routes_and_spools_fit_unchanged_capacity(self):
        cases = literal_route_cases()
        self.assertEqual((len(cases), len({row["name"] for row in cases}), sum(row["expected"] for row in cases)), (21, 21, 3))
        files, directories = private_population()
        self.assertEqual((len(files), len(directories)), (48, 121))
        self.assertIn("private/route-root-only/" + CHECKER, files)
        self.assertIn("private/route-directory/skills/implementaudit/scripts/check-fixture.sh", directories)
        self.assertIn("private/route-hardlink/outside.sh", files)
        self.assertIn("private/route-hardlink/skills/implementaudit/scripts/check-fixture.sh", files)
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual(reservation["original_checker_calls"], 1 + 3 + len(cases) + 1)
        self.assertEqual(reservation["files"], len(files) + 3 + 2 + reservation["original_checker_calls"])
        self.assertEqual((reservation["private_payload_entries"], reservation["private_payload_inodes"], reservation["directories"]), (len(files), len(files) - 1, len(directories)))
        self.assertGreaterEqual(max(state["files"][PROGRAM]["bytes"], state["files"][CHECKER]["bytes"]), max(files.values()))
        session = self.session()
        self.assertEqual(session.LIMITS["scratch_bytes"], 32 * 1024**2)
        self.assertEqual(session.LIMITS["file_bytes"], 16 * 1024**2)
        self.A.require_resource_capacity(reservation, session.LIMITS)

    def test_complete_skills_bytes_and_declared_physical_routes_are_captured(self):
        path = self.new_member(b"\x00\xff\xfeopaque\n")
        (path.parent / ".empty").mkdir()
        state, stamps, objects = self.snapshot()
        expected = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in (self.source / "skills").rglob("*") if p.is_file()}
        actual = {name: objects[row["sha256"]] for name, row in state["files"].items() if name.startswith("skills/")}
        self.assertEqual(actual, expected)
        self.assertIn("skills/.added/.empty", state["directories"])
        owner = self.source / "skills/implementaudit/references/repo-state-comparison.md"
        routes = [line.split("|", 1)[0].removeprefix("helper-route: ") for line in owner.read_text().splitlines() if line.startswith("helper-route: ")]
        self.assertEqual(len(routes), 29)
        for route in routes:
            name = "skills/implementaudit/" + route
            self.assertIn(name, state["files"])
            self.assertEqual((self.source / name).stat().st_nlink, 1)
            for parent in PurePosixPath(name).parents:
                self.assertIn(str(parent), state["directories"])
        self.assertIn("recursive_inputs", stamps)
        self.assertFalse((self.source / ".git").exists())

    def test_unknown_program_or_registry_refuses_before_runtime(self):
        for number, name in enumerate((PROGRAM, CHECKER, "scripts/verify-package.sh")):
            path = self.source / name
            raw = path.read_bytes()
            path.write_bytes(raw + b"\n")
            session = self.session("changed-" + str(number))
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "executable|registry"):
                session.run()
            self.assertEqual(session.dispatch_count, 0)
            self.assertFalse((session.output / "objects").exists())
            path.write_bytes(raw)

    def test_required_governor_and_route_owner_absence_refuse(self):
        for name in self.A.contract_for(PROFILE)["recursive"]["required_members"]:
            path = self.source / name
            raw, mode = path.read_bytes(), path.stat().st_mode & 0o777
            path.unlink()
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "required"):
                self.snapshot()
            path.write_bytes(raw)
            path.chmod(mode)

    def test_added_member_and_missing_declared_target_remain_original_inputs(self):
        before, _, _ = self.snapshot()
        path = self.new_member(b"bash scripts/check-new-semantic-violation.sh\n", ".added/unqualified.txt")
        added, _, _ = self.snapshot()
        self.assertNotEqual(before, added)
        self.assertIn(path.relative_to(self.source).as_posix(), added["files"])
        owner = self.source / "skills/implementaudit/references/repo-state-comparison.md"
        owner.write_bytes(owner.read_bytes() + b"\nhelper-route: scripts/absent-declared-helper.sh|S|diagnosis|R|-|none|not-auto\n")
        changed, _, _ = self.snapshot()
        self.assertNotEqual(changed, added)
        self.assertNotIn("skills/implementaudit/scripts/absent-declared-helper.sh", changed["files"])
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual(session._issued, {})

    def test_source_hardlink_refuses_despite_private_hardlink_negative(self):
        path = self.source / "skills/implementaudit/scripts/check-authorization-binding.sh"
        outside = self.base / "outside"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        os.link(outside, path)
        session = self.session()
        with self.assertRaises(ValueError):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())
        self.assertIn("private/route-hardlink/skills/implementaudit/scripts/check-fixture.sh", private_population()[0])

    def test_non_lf_and_full_invalid_declaration_output_are_reserved(self):
        before, _, _ = self.snapshot()
        initial = before["recursive_inputs"]["resources"]
        raw = b"scripts/check-one.sh\rtests/two.sh\vhelper-route: scripts/" + b"x" * 10000 + b"\n"
        self.new_member(raw, "unicode-\u00e9/\u2603.txt")
        state, _, _ = self.snapshot()
        bound = state["recursive_inputs"]["resources"]
        self.assertEqual(bound["installed_possible_messages"] - initial["installed_possible_messages"], 6)
        self.assertGreaterEqual(bound["installed_diagnostic_bytes"] - initial["installed_diagnostic_bytes"], 4 * (len(raw) - 3))
        self.A.require_resource_capacity(self.A.temporary_requirements(state, profile=PROFILE), self.session().LIMITS)

    def test_large_diagnostic_refuses_unchanged_capacity_before_runtime(self):
        self.new_member(b"scripts/check-large.sh\n" * 30000, "x" * 180 + "/" + "y" * 180)
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        session = self.session()
        self.assertGreater(reservation["largest_file_bytes"], session.LIMITS["file_bytes"])
        with self.assertRaisesRegex(ValueError, "capacity"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())

    def test_valid_source_reaches_runtime_tripwire_without_result(self):
        session = self.session()
        with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertFalse((session.output / "objects").exists())


class LiveCases(InstalledFixture, shared.RetainedFixture, unittest.TestCase):
    LIVE_ENV = "R0035_FINITE_INSTALLED_LIVE"
    EVIDENCE_ENV = "R0035_FINITE_INSTALLED_EVIDENCE"
    OBJECTS_ENV = "R0035_FINITE_INSTALLED_OBJECTS"
    TEST_SOURCE = "tests/work-graph-installed-cases.py"

    def actual(self, session):
        self.assertFalse(self.SOURCE_ADMISSION_ONLY)
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual((receipt["node"], receipt["scope"]), ("COMMAND:" + PROGRAM + ":0", PROFILE))
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        acquisition = json.loads((session.output / ("generation-%06d" % result["generation"]) / "acquisition.json").read_bytes())
        image = json.loads((session.output / "objects" / acquisition["inputs"][receipt["node"]]["image_digest"]).read_bytes())
        self.assertEqual(image["source_materialization"], "SINGLE_LINK_FILES_READ_ONLY_ROOT")
        self.assertIs(image["root_read_only"], True)
        self.assertEqual((result["canonical_acceptance"], result["authority"]), ("UNQUALIFIED", "NONE"))
        return result, stdout, stderr

    def test_actual_original_positive_reuse_and_added_member_refusal(self):
        session = self.session()
        first, stdout, stderr = self.actual(session)
        expected = "check-installed-payload-self-contained: ok\n"
        expected += "".join("installed-payload-self-contained: " + row["name"] + " ok\n" for row in literal_route_cases())
        expected += "installed-payload-self-contained: hardlink refusal ok\ninstalled-payload-self-contained.test: ok\n"
        self.assertEqual((first["exit"], first["complete"], stdout, stderr), (0, True, expected.encode(), b""))
        second, _, _ = self.actual(session)
        self.assertEqual((first["disposition"], second["disposition"], session.dispatch_count), ("EXECUTED", "REUSED", 1))
        for field in ("receipt_digest", "key", "producer"):
            self.assertEqual(first[field], second[field])
        self.new_member()
        with self.assertRaisesRegex(ValueError, "prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_added_semantic_violation_fails_original_and_is_not_reused(self):
        self.new_member(b"bash scripts/check-unqualified-new-member.sh\n", ".added/unqualified.txt")
        session = self.session()
        result, stdout, stderr = self.actual(session)
        self.assertEqual((result["exit"], result["complete"], stdout), (1, True, b""))
        self.assertIn(b"unqualified.txt:1: repo-only path reference without 'source repo' label", stderr)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
