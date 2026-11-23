"""Qualify only the published pure historical G3 scope-body transform."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).parent
SCOPE_SHA = "8c08f2aecd34f582f3662b5bc83b3d3a27cee33d2f17711ced868a1d7b11c96a"
BODY_ROLES = (
    ("baseline", "dependencies/installation/phase/tree/qualification/dg16-r5-g1-hosted-episode/ORIGINAL_SCOPE.json"),
    ("baseline", "dependencies/installation/sender-author/templates/core/ORIGINAL_SCOPE.json"),
)
PROJECTION = ("baseline", "dependencies/installation/pure/g3.py")
OWNER = ("owners", "g3_receiving.py")
RUNTIME = ("runtime", None)
FULL_BEFORE = ("full_before", "g3")
TARGETS = {*BODY_ROLES, PROJECTION, OWNER, RUNTIME, FULL_BEFORE}
EXPECTED_POPULATION = {"DG16": 48, "DG17": 95, "DG18": 14, "total": 157}


def require(value, label):
    if not value:
        raise ValueError(label)


def receipt_inputs():
    spec = importlib.util.spec_from_file_location("posix_helpers", HERE / "receive_posix.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    raw = (HERE / "INERT_MANIFEST.json").read_bytes()
    require(helpers.pin(raw)["sha256"] == helpers.MANIFEST_SHA256, "published inert manifest mismatch")
    manifest = json.loads(raw)
    selected = {}
    for row in manifest["members"]:
        identity = row["role"], row["member"]
        if identity not in TARGETS:
            continue
        kind, _, literal, *trail = row["locator"]
        if kind == "public_git_blob":
            require(not trail, "unexpected blob trail")
            content = helpers.git_blob(literal)
        else:
            require(kind == "public_git_archive" and 0 < len(literal) <= 40, "corpus locator")
            content = b"".join(helpers.git_blob(oid) for oid in literal)
            require(len(content) <= helpers.ARCHIVE_MAX, "archive aggregate bound")
            for format_name, ordinal in trail:
                content = helpers.archived_member(content, format_name, ordinal)
        require(helpers.pin(content) == row["input"] and identity not in selected, "scope input role or pin mismatch")
        selected[identity] = content
    require(set(selected) == TARGETS, "scope source role population")
    return selected, helpers


def function(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def assignment(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == name for target in n.targets))


def literal(tree, name):
    return ast.literal_eval(assignment(tree, name).value)


def verified_historical_consumer(projection, raw):
    names = ("need", "sha", "parse", "exact", "digest", "integer", "scope_basis")
    constants = ("SOURCE_COMMIT", "SOURCE_TREE", "SCOPE_SHA", "OWNER_ARRANGEMENT",
                 "NATURAL_SCOPE", "SCOPE_INPUT_NAMES", "ORIGINAL")
    functions = [function(projection, name) for name in names]
    refusal = next(n for n in projection.body if isinstance(n, ast.ClassDef) and n.name == "Refusal")
    limits = next(n for n in projection.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Tuple) and any(isinstance(x, ast.Name) and x.id == "FILE_LIMIT"
                                                         for x in t.elts) for t in n.targets))
    require(ast.unparse(limits) ==
            "FILE_LIMIT, TOTAL_LIMIT, ENTRY_LIMIT, DEPTH_LIMIT = (16 * 1024 ** 2, 64 * 1024 ** 2, 4096, 16)",
            "historical literal limits changed")
    body = [limits, *[assignment(projection, name) for name in constants], refusal, *functions]
    pure = dict(hashlib=hashlib, re=re, json=json, current_original_scope_body=lambda: raw)
    # These exact, pinned declarations consist only of data validation and an injected byte source.
    exec(compile(ast.Module(body=body, type_ignores=[]), "<exact historical scope basis>", "exec"), pure)
    original, accepted = pure["scope_basis"]()
    require(original == raw and accepted["original_population"] == EXPECTED_POPULATION,
            "historical scope consumer output mismatch")
    pure["current_original_scope_body"] = lambda: bytes([raw[0] ^ 1]) + raw[1:]
    try:
        pure["scope_basis"]()
    except pure["Refusal"] as error:
        require(str(error) == "ORIGINAL_SCOPE_PIN", "wrong scope negative discriminator")
    else:
        raise ValueError("historical exact scope pin accepted corrupted bytes")
    return accepted


def main():
    blobs, helpers = receipt_inputs()
    raw = blobs[BODY_ROLES[0]]
    require(raw == blobs[BODY_ROLES[1]] and helpers.pin(raw) == {"bytes": 5443, "sha256": SCOPE_SHA},
            "exact original scope bodies disagree")
    before, projection, current, runtime = (ast.parse(blobs[key]) for key in
                                            (FULL_BEFORE, PROJECTION, OWNER, RUNTIME))
    old_basis = function(projection, "scope_basis")
    require(ast.dump(function(before, "scope_basis")) == ast.dump(old_basis),
            "published whole and projection G3 basis disagree")
    current_basis = function(current, "scope_basis")
    require("current_original_scope_body()" in ast.unparse(old_basis) and "Path(" not in ast.unparse(old_basis)
            and "current_original_scope_body()" not in ast.unparse(current_basis)
            and "Path(" in ast.unparse(current_basis), "historical/current scope source discriminator")
    cls = next(n for n in runtime.body if isinstance(n, ast.ClassDef) and n.name == "CurrentSources")
    supplier = next(n for n in function(cls, "module").body if isinstance(n, ast.If)
                    and ast.unparse(n.test) == "name == 'g3'")
    require(ast.unparse(supplier.body[0]) ==
            "namespace['current_original_scope_body'] = lambda: self.body(CORE + 'ORIGINAL_SCOPE.json')",
            "exact runtime held-body binding changed")
    accepted = verified_historical_consumer(projection, raw)
    old_subject = {"commit": literal(projection, "SOURCE_COMMIT"), "tree": literal(projection, "SOURCE_TREE")}
    current_subject = {"commit": literal(current, "MAINTAINED_SOURCE_COMMIT"),
                       "tree": literal(current, "MAINTAINED_SOURCE_TREE")}
    require(literal(projection, "SCOPE_SHA") == literal(current, "SCOPE_SHA") == SCOPE_SHA
            and accepted["current_subject"] == old_subject != current_subject,
            "exact subject mismatch no longer discriminates")
    result = {
        "schema": "dg16.task1-r2.g3-historical-scope-transform.v1",
        "scope": "PURE_HISTORICAL_SCOPE_TRANSFORM_ONLY",
        "body": helpers.pin(raw),
        "body_roles_byte_equal": True,
        "body_git_blob": hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest(),
        "historical_full_before": helpers.pin(blobs[FULL_BEFORE]),
        "historical_projection": helpers.pin(blobs[PROJECTION]),
        "current_owner": helpers.pin(blobs[OWNER]),
        "runtime": helpers.pin(blobs[RUNTIME]),
        "same_historical_scope_basis_ast": True,
        "externally_bound_historical_consumer_accepted_exact_bytes": True,
        "opener_executed": False,
        "pinned_scope_corruption_refused": True,
        "population": accepted["original_population"],
        "original_id_population_received": {key: len(value) for key, value in accepted["original_ids"].items()},
        "received_input_descriptors": accepted["received_inputs"],
        "received_input_bodies_authenticated_here": False,
        "historical_scope_subject": old_subject,
        "maintained_owner_expects_subject": current_subject,
        "maintained_owner_pins_historical_body": True,
        "maintained_owner_subject_matches_historical_body": False,
        "owning_runtime_held_body_binding_line": supplier.lineno,
        "current_scope_rebound": False,
        "source_adoption": False,
        "protected_readiness": False,
        "original_awards": [],
    }
    sys.stdout.buffer.write(helpers.canonical(result))


if __name__ == "__main__":
    main()
