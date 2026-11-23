"""Run the one admitted codec-only R2 comparison using public source data."""
import ast
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("inert_assembly_inputs", HERE / "assemble_joint_after_basis.py")
assembly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembly)
public = assembly.public
ROOT = "f36376817df03d070549cd1cb77306cbc8dbe355"
ROOTS = ["check_index", "encode", "need", "sha"]
DISPUTED = {"assignments", "loader_bind", "parse"}
EXPECTED = {"bytes": 1445, "sha256": "a1141fc0ff2357b381dbed98b2055889bdf7eab10cb937336b88f263ee6563f5"}


def decision(ref):
    raw = subprocess.check_output(["git", "show", ref + ":handoff/astra-dg16-dg18/CONTINUATION.json"])
    return json.loads(raw)["dependent_frontiers"]["DG16"]


def compare():
    base = decision(assembly.DECISION)["joint_after_basis_trial"]
    index_raw = (HERE / assembly.INDEX).read_bytes()
    _, read = assembly.inputs(base, index_raw)
    prefix = "dependencies/installation/"
    full = read("baseline", prefix + "phase/tree/qualification/dg16-r5-g1-hosted-episode/carrier/bundle_codec.py")
    retained = read("baseline", prefix + "pure/codec.py")
    plan = json.loads(read("baseline", assembly.g3.PLAN))["codec"]
    source = public.load_r2(read("generator"))
    order = [name for node in ast.parse(retained).body for name in source._declared(node)]
    public.require(public.pin(full) == {"bytes": plan["source_bytes"], "sha256": plan["source_sha256"]},
                   "exact historical codec source")
    public.require(public.pin(retained) == EXPECTED, "retained codec member")
    zip_body = subprocess.check_output(["git", "show", "99868c1e:handoff/sol-dg16-20261122/"
                                        "task1-inert-source/JOINT_AFTER_BASIS.zip"])
    with zipfile.ZipFile(BytesIO(zip_body)) as archive:
        public.require(archive.read("codec.source") == retained, "retained inert codec equals old body")
    public.require(set(plan["roots"]) == set(ROOTS) | DISPUTED and plan["supplied"] == [], "historical seven roots")
    public.require(set(order) == set(plan["declarations"]), "historical declaration census")
    externals = sorted(set(plan["external_names"]) - DISPUTED)
    record = {
        "schema": "dg16.g3.codec-only-r2-comparison.v1", "admission": ROOT,
        "authority": "NONE", "projected_module_execution": False,
        "full_codec_source": public.pin(full), "historical_roots": plan["roots"], "roots": ROOTS, "supplied": [],
        "expected_declaration_order": order, "expected_external_names": externals, "retained_codec": EXPECTED,
    }
    try:
        actual = source.projection_basis(full, ROOTS, [])
    except source.Refusal as error:
        return dict(record, disposition="RESOLVER_REFUSAL", first_refusal=str(error))
    record.update(actual_declaration_order=list(actual.declarations), actual_external_names=list(actual.external_names),
                  actual_codec=public.pin(actual.projection))
    if list(actual.declarations) != order:
        return dict(record, disposition="DECLARATION_ORDER_MISMATCH")
    if list(actual.external_names) != externals:
        return dict(record, disposition="EXTERNAL_NAME_MISMATCH")
    if actual.projection != retained:
        offset = next((i for i, (a, b) in enumerate(zip(actual.projection, retained)) if a != b),
                      min(len(actual.projection), len(retained)))
        return dict(record, disposition="BYTE_MISMATCH", first_differing_offset=offset)
    return dict(record, disposition="BYTE_EXACT_CODEC_PROJECTION")


if __name__ == "__main__":
    front = decision(ROOT)
    admitted = front["codec_recipe"]
    public.require(admitted["decision"] ==
                   "RECEIVE_PROSPECTIVE_METADATA_RECONCILIATION_AND_ADMIT_ONE_CODEC_ONLY_BYTE_COMPARISON"
                   and admitted["state"] == "ADMITTED_RESULT_PENDING"
                   and admitted["prospective_roots"] == ROOTS and admitted["supplied"] == []
                   and admitted["expected_body"] == EXPECTED, "exact codec-only admission")
    sys.stdout.buffer.write(public.canonical(compare()))
