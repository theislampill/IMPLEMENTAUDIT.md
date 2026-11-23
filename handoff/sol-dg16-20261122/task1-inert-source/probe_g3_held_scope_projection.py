"""Run only the admitted public-fixture G3 projection trial."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("inert_public_inputs", HERE / "receive_posix.py")
public = importlib.util.module_from_spec(spec)
spec.loader.exec_module(public)
PLAN = "dependencies/installation/PURE_SOURCE_PLAN.json"
OLD_PROJECTION = "dependencies/installation/pure/g3.py"
EXPECTED_ROOTS = (
    "receive_exact_m4", "validate_decision", "validate_effect_state", "validate_final_decision",
    "validate_original_receipt", "validate_public_final_request", "validate_public_request",
    "validate_public_scope",
)
SUPPLIED = ["current_original_scope_body"]
OLD_READ = b"    raw = read_file(Path(__file__).with_name('ORIGINAL_SCOPE.json'), 8192)\n"
NEW_READ = (
    b"    raw = current_original_scope_body()\n"
    b"    need(type(raw) is bytes and len(raw) <= 8192, 'ORIGINAL_SCOPE_BYTES')\n"
)


def input_roles():
    manifest_raw = (HERE / "INERT_MANIFEST.json").read_bytes()
    public.require(public.pin(manifest_raw)["sha256"] == public.MANIFEST_SHA256, "input manifest pin")
    wanted = {("baseline", PLAN), ("baseline", OLD_PROJECTION),
              ("owners", "g3_receiving.py"), ("generator", None)}
    found = {}
    for row in json.loads(manifest_raw)["members"]:
        key = row["role"], row["member"]
        if key not in wanted:
            continue
        kind, _, locator, *trail = row["locator"]
        if kind == "public_git_blob":
            public.require(not trail, "blob has archive trail")
            raw = public.git_blob(locator)
        else:
            public.require(kind == "public_git_archive" and 0 < len(locator) <= 40, "archive locator")
            raw = b"".join(public.git_blob(part) for part in locator)
            public.require(len(raw) <= public.ARCHIVE_MAX, "archive size")
            for fmt, index in trail:
                raw = public.archived_member(raw, fmt, index)
        public.require(public.pin(raw) == row["input"] and key not in found, "public role pin")
        found[key] = raw
    public.require(found.keys() == wanted, "public role population")
    return found


def declaration_map(source, raw):
    return {name: node for node in ast.parse(raw).body for name in source._declared(node)}


def check_scope(projection, source):
    selected = declaration_map(source, projection)
    names = (
        "FILE_LIMIT", "Refusal", "need", "sha", "parse", "exact", "digest", "integer", "scope_basis",
        "ORIGINAL", "OWNER_ARRANGEMENT", "NATURAL_SCOPE", "SCOPE_INPUT_NAMES", "SCOPE_SHA",
        "MAINTAINED_SOURCE_COMMIT", "MAINTAINED_SOURCE_TREE",
    )
    included = {id(selected[name]) for name in names}
    ordered = list(dict.fromkeys(node for node in selected.values() if id(node) in included))
    namespace = dict(hashlib=hashlib, json=json, re=re)
    narrowed = ast.Module(body=ordered, type_ignores=[])
    exec(compile(narrowed, "<disposable public scope parser>", "exec"), namespace)
    historical = subprocess.check_output(["git", "show",
        "4ef93671:qualification/dg16-r5-g1-hosted-episode/ORIGINAL_SCOPE.json"])
    public.require(hashlib.sha256(historical).hexdigest() == namespace["SCOPE_SHA"], "public historical scope pin")
    fixture = json.loads(historical)
    fixture["current_subject"] = {
        "commit": namespace["MAINTAINED_SOURCE_COMMIT"], "tree": namespace["MAINTAINED_SOURCE_TREE"],
    }
    fixture_bytes = public.canonical(fixture)

    def use(raw):
        namespace["current_original_scope_body"] = lambda: raw
        return namespace["scope_basis"]()

    def refusal(raw, expected):
        try:
            use(raw)
        except namespace["Refusal"] as error:
            public.require(str(error) == expected, "unexpected public scope refusal: " + str(error))
            return str(error)
        raise ValueError("unexpected public scope acceptance")

    old_subject = refusal(historical, "ORIGINAL_POPULATION")
    old_pin = refusal(fixture_bytes, "ORIGINAL_SCOPE_PIN")
    namespace["SCOPE_SHA"] = hashlib.sha256(fixture_bytes).hexdigest()
    public.require(use(fixture_bytes) == (fixture_bytes, fixture), "fixture-bound positive")
    return {
        "unchanged_published_pin_with_public_historical_body": old_subject,
        "unchanged_published_pin_with_maintained_subject_fixture": old_pin,
        "fixture_bound_positive": True,
        "fixture_bytes": public.pin(fixture_bytes),
        "altered_byte": refusal(fixture_bytes[:-1] + b" ", "ORIGINAL_SCOPE_PIN"),
        "oversized": refusal(b" " * 8193, "ORIGINAL_SCOPE_BYTES"),
        "non_bytes": refusal(fixture_bytes.decode(), "ORIGINAL_SCOPE_BYTES"),
    }


def main():
    inputs = input_roles()
    plan = json.loads(inputs["baseline", PLAN])["g3"]
    historical = inputs["baseline", OLD_PROJECTION]
    raw = inputs["owners", "g3_receiving.py"]
    source = public.load_r2(inputs["generator", None])
    public.require(tuple(plan["roots"]) == EXPECTED_ROOTS and plan["supplied"] == SUPPLIED, "receiving population")
    public.require(public.pin(historical)["sha256"] == plan["projection_sha256"], "historical projection pin")
    try:
        source.projection_basis(raw, plan["roots"], plan["supplied"])
    except source.Refusal as error:
        original_refusal = str(error)
        public.require(original_refusal == "unexplained or unsupported external: Path", "original refusal changed")
    else:
        raise ValueError("original refusal disappeared")

    old_read = OLD_READ.replace(b"\n", b"\r\n")
    new_read = NEW_READ.replace(b"\n", b"\r\n")
    public.require(raw.count(old_read) == 1, "one original scope read")
    revised = raw.replace(old_read, new_read)
    public.require(revised.replace(new_read, old_read) == raw, "only authorized source delta")
    record = {
        "schema": "dg16.g3.held-scope-projection-trial.v1",
        "authority": "NONE",
        "root_decision": "31a317780f46dabd287372a88e46d6160618cca9",
        "original_refusal": original_refusal,
        "source": public.pin(raw),
        "disposable_source": public.pin(revised),
        "roots": list(EXPECTED_ROOTS),
        "supplied": SUPPLIED,
    }
    try:
        basis = source.projection_basis(revised, plan["roots"], plan["supplied"])
    except source.Refusal as error:
        record["disposition"] = "STOPPED_AT_FURTHER_RESOLVER_REFUSAL"
        record["resolver_refusal"] = str(error)
    else:
        old, new = (declaration_map(source, body) for body in (historical, basis.projection))
        record.update(
            disposition="PUBLIC_FIXTURE_PROJECTION_AND_SCOPE_CONTROLS",
            projection=dict(basis.projection_pin),
            external_names=list(basis.external_names),
            declarations=list(basis.declarations),
            added=sorted(new.keys() - old.keys()),
            removed=sorted(old.keys() - new.keys()),
            changed=sorted(key for key in old.keys() & new.keys() if ast.dump(old[key]) != ast.dump(new[key])),
            scope_controls=check_scope(basis.projection, source),
        )
    sys.stdout.buffer.write(public.canonical(record))


if __name__ == "__main__":
    main()
