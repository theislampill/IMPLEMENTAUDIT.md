"""Bounded offline fixture for the prospective compact report format."""

import ast
from collections import defaultdict
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import struct
import types
import unittest
from zipfile import ZipFile

import compact_report as compact


OWNER_SHA256 = "4eec99e3185f42d4128b74cab3b21b73359cb4ce07ad5cdbd8eeb41a13d53ec1"
SELECTED_BYTES = 1823337
DELIVERY_BYTES = 2097152
CACHE = b"public fixture cache descriptor, parsing not selected\n"
WHEEL = b""


def pure_owner(raw):
    if hashlib.sha256(raw).hexdigest() != OWNER_SHA256:
        raise ValueError("pinned source SHA-256 mismatch")
    functions = {
        "need", "sha", "canonical", "strict_json", "pin", "path_token", "elf_public_path",
        "public_path", "bounded_limits", "elf_string", "parse_elf", "classify",
        "virtual_resolve", "expected_layer", "population_selection", "budget_counts",
        "make_layout", "compare_pins", "cache_join", "cache_rows", "join_graph",
        "complete_predicate", "validate_export_shapes", "encode_report", "receive",
    }
    constants = {"SCHEMA", "LIMITS", "SKIPS", "TOKEN", "NAME", "PYNAME", "PRIVATE", "PROVIDER"}
    nodes = []
    for node in ast.parse(raw).body:
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            nodes.append(node)
        if isinstance(node, ast.ClassDef) and node.name == "Refusal":
            nodes.append(node)
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in constants:
                nodes.append(node)
    if len(nodes) != len(functions) + len(constants) + 1:
        raise ValueError("pinned pure source population changed")
    # The supplied namespace has no host OS API. This never loads Capture.
    safe = dict(hashlib=hashlib, json=json, re=re, io=io, posixpath=posixpath,
                stat=stat, struct=struct, PurePosixPath=PurePosixPath, ZipFile=ZipFile,
                defaultdict=defaultdict)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<reviewed public data helpers>", "exec"), safe)
    return types.SimpleNamespace(**safe)


def fixture(owner, rows):
    root = "/usr/lib/python3.12"
    cache_pin = owner.pin(CACHE)
    contract = {
        "schema": "dg16.compact-report.offline-fixture.v1",
        "fixed_files": [], "optional_aliases": [], "git_directories": [],
        "stdlib_root": root, "python_target": "/usr/bin/python3.12",
        "directory_mode_policy": {"default": 0o755, "exceptions": {}},
        "provider": {"root": "/opt/public-fixture-provider", "files": {}, "file_aliases": {},
                     "directory_links": {}, "directories": {}},
        "pins": {}, "public_absences": [],
        "retained_cache": cache_pin, "maintained_cache_pin": dict(cache_pin, mode=0o644),
    }
    objects, selected, members = {}, {}, {}
    total = 0
    for i in range(1, rows + 1):
        name = f"public-text-{i:04}.txt"
        path = f"{root}/{name}"
        body = f"Public test record {i}\n".encode("ascii")
        identity = ["1", str(i), stat.S_IFREG | 0o644, 1, len(body), 1000, 1000, 1, 1]
        descriptor = dict(owner.pin(body), mode=0o644)
        selected[path] = dict(kind="FILE", resolved=path, closing=dict(kind="FILE", resolved=path))
        members[name] = dict(kind="FILE", identity=identity)
        objects[path] = dict(identity=identity, descriptor=descriptor, evidence="OBSERVED",
                             classification="NON_ELF_DATA", closing_identity=identity,
                             closing_descriptor=descriptor)
        total += len(body)
    identity = ["1", "0", stat.S_IFDIR | 0o755, 2, 0, 1000, 1000, 1, 1]
    directories = {str(p): dict(identity=identity, closing_identity=identity)
                   for p in [PurePosixPath(root), *PurePosixPath(root).parents]}
    population = dict(rule="STDLIB_REAL_DIRECTORY", identity=identity, members=members,
                      closing_identity=identity, closing_population_count=len(members),
                      closing_population_sha256=owner.sha(owner.canonical(members)))
    report = dict(
        schema=owner.SCHEMA, authority="NONE", contract_sha256=owner.sha(owner.canonical(contract)),
        selected=selected, objects=objects, links={}, directories=directories,
        populations={root: population}, absences={}, issues=[],
        observed_provider=False, actual_runtime_constructed=False, cache_pin_adopted=False,
        source_profile_adopted=False, original_awards=0, census_complete=True,
        complete_selected_public_static_surface=True, read_bytes=2 * total,
        evidence_scope="SELECTED_PUBLIC_STATIC_DATA_AND_EXPECTED_PROVIDER_ONLY",
        limits=owner.bounded_limits(contract), opening_aborted=False,
    )
    # Real pinned derivations, fed exclusively generated public fixture descriptors.
    report["expected_provider"] = owner.expected_layer(contract, WHEEL, objects)
    report["layout"] = owner.make_layout(report, contract)
    report["cache"] = owner.cache_join(report, contract, CACHE)
    report["graph"] = owner.join_graph(report, contract, CACHE)
    report["pin_comparisons"] = owner.compare_pins(report, contract)
    report["counters"] = dict(owner.budget_counts(report, contract), edges=len(report["graph"]["edges"]))
    return contract, report


class CompactReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner = pure_owner(Path(os.environ["DG16_PINNED_RUNTIME"]).read_bytes())
        cls.contract, cls.report = fixture(cls.owner, 2050)
        cls.legacy = cls.owner.canonical(cls.report)

    def test_m3_complete_observer_report_retains_evidence_under_existing_wire_limit(self):
        path = Path(__file__).resolve().parents[3] / "engineering/g132-host-runtime-static-operation/runtime_static.py"
        spec = importlib.util.spec_from_file_location("product_runtime_static", path)
        owner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(owner)
        contract, report = fixture(self.owner, 2600)
        legacy = self.owner.canonical(report)
        self.assertGreater(len(legacy), DELIVERY_BYTES)
        self.assertEqual(self.owner.strict_json(self.owner.encode_report(report, SELECTED_BYTES))["code"],
                         "REPORT_BOUND")
        wire = owner.encode_report(report, SELECTED_BYTES)
        self.assertLessEqual(len(wire), SELECTED_BYTES)
        compact = owner.strict_json(wire)
        self.assertEqual(compact["schema"], owner.COMPACT_SCHEMA)
        self.assertEqual(compact["original"], owner.pin(legacy))
        self.assertTrue(owner.receive(wire, contract, WHEEL, CACHE)["complete_selected_public_static_surface"])
        compact["original"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(owner.Refusal, "COMPACT_ORIGINAL_COMMITMENT"):
            owner.receive(owner.canonical(compact), contract, WHEEL, CACHE)

    def pack(self):
        return compact.pack(self.legacy, self.owner, self.contract, WHEEL, CACHE, SELECTED_BYTES)

    def unpack(self, raw, cap=SELECTED_BYTES):
        return compact.expand(raw, self.owner, self.contract, WHEEL, CACHE, cap)

    def test_exact_legacy_fidelity_under_both_unchanged_caps(self):
        legacy_result = self.owner.receive(self.legacy, self.contract, WHEEL, CACHE)
        self.assertIs(legacy_result["complete_selected_public_static_surface"], True)
        self.assertGreater(len(self.legacy), SELECTED_BYTES)
        self.assertLessEqual(len(self.legacy), DELIVERY_BYTES)
        self.assertEqual(self.owner.strict_json(self.owner.encode_report(self.report, SELECTED_BYTES))["code"],
                         "REPORT_BOUND")
        packed = self.pack()
        self.assertLessEqual(len(packed), SELECTED_BYTES)
        expanded, received = self.unpack(packed)
        self.assertEqual(expanded, self.legacy)
        self.assertEqual(received, legacy_result)
        support = {"inputs.json": packed, "source.json": self.owner.canonical(self.contract)}
        manifest = compact.delivery_manifest(support, DELIVERY_BYTES)
        self.assertLessEqual(sum(map(len, support.values())) + len(manifest), DELIVERY_BYTES)
        sizes = {name: len(self.owner.canonical(self.report[name])) for name in compact.DERIVED}
        print(json.dumps({"fixture_legacy": self.owner.pin(self.legacy),
                          "fixture_wire": self.owner.pin(packed),
                          "fixture_delivery_bytes": sum(map(len, support.values())) + len(manifest),
                          "derived_section_bytes": sizes, "population": len(self.report["objects"]),
                          "selected_inner_limit": SELECTED_BYTES, "outer_limit": DELIVERY_BYTES},
                         sort_keys=True))

    def test_wrong_or_missing_commitments_refuse(self):
        wire = self.owner.strict_json(self.pack())
        wire["derived"]["layout"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "DERIVED_COMMITMENT"):
            self.unpack(self.owner.canonical(wire))
        del wire["derived"]["layout"]
        with self.assertRaisesRegex(ValueError, "DERIVED_POPULATION"):
            self.unpack(self.owner.canonical(wire))

    def test_omitted_observation_refuses(self):
        wire = self.owner.strict_json(self.pack())
        path = next(iter(wire["report"]["selected"]))
        del wire["report"]["selected"][path]["closing"]
        with self.assertRaisesRegex(ValueError, "LEGACY_COMMITMENT"):
            self.unpack(self.owner.canonical(wire))

    def test_rebound_but_incomplete_bookend_refuses_in_actual_receiver(self):
        wire = self.owner.strict_json(self.pack())
        raw = self.owner.strict_json(self.legacy)
        path = next(iter(wire["report"]["selected"]))
        del wire["report"]["selected"][path]["closing"]
        del raw["selected"][path]["closing"]
        wire["legacy"] = self.owner.pin(self.owner.canonical(raw))
        with self.assertRaisesRegex(ValueError, "SELECTOR_CLOSING"):
            self.unpack(self.owner.canonical(wire))

    def test_wire_and_expansion_limits(self):
        packed = self.pack()
        self.assertEqual(self.unpack(packed, len(packed))[0], self.legacy)
        with self.assertRaisesRegex(ValueError, "WIRE_BOUND"):
            self.unpack(packed, len(packed) - 1)
        wire = self.owner.strict_json(packed)
        wire["legacy"]["bytes"] = DELIVERY_BYTES + 1
        with self.assertRaisesRegex(ValueError, "DESCRIPTOR_BOUND"):
            self.unpack(self.owner.canonical(wire))
        wire["legacy"]["bytes"] = len(self.legacy) - 1
        with self.assertRaisesRegex(ValueError, "LEGACY_BOUND"):
            self.unpack(self.owner.canonical(wire))

    def test_strict_json_and_v1_reject_prospective_wire(self):
        packed = self.pack()
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            self.unpack(b'{"schema":"other",' + packed[1:])
        with self.assertRaisesRegex(ValueError, "NONCANONICAL_WIRE"):
            self.unpack(b" " + packed)
        with self.assertRaisesRegex(ValueError, "REPORT_SCHEMA_OR_INCOMPLETE_STUB"):
            self.owner.receive(packed, self.contract, WHEEL, CACHE)

    def test_over_receiver_cap_remains_refused(self):
        contract, report = fixture(self.owner, 2250)
        raw = self.owner.canonical(report)
        self.assertGreater(len(raw), DELIVERY_BYTES)
        with self.assertRaisesRegex(ValueError, 'REPORT_BOUND'):
            self.owner.receive(raw, contract, WHEEL, CACHE)
        with self.assertRaisesRegex(ValueError, 'LEGACY_BOUND'):
            compact.pack(raw, self.owner, contract, WHEEL, CACHE, SELECTED_BYTES)

    def test_observation_budget_refuses_before_recomputation(self):
        wire = self.owner.strict_json(self.pack())
        wire["report"]["read_bytes"] = self.owner.bounded_limits(self.contract)["read_bytes"] + 1
        with self.assertRaisesRegex(ValueError, "OBSERVATION_BOUND"):
            self.unpack(self.owner.canonical(wire))

    def test_outer_bound_includes_manifest(self):
        payload = self.pack()
        members = {"inputs.json": payload}
        manifest = compact.delivery_manifest(members, DELIVERY_BYTES)
        total = len(payload) + len(manifest)
        self.assertEqual(compact.delivery_manifest(members, total), manifest)
        with self.assertRaisesRegex(ValueError, "DELIVERY_BOUND"):
            compact.delivery_manifest(members, total - 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
