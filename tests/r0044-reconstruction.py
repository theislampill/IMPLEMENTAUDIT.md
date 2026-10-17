"""Controls for the published, canonically unallocated R0044 source projection."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/r0044-reconstruct.py"
INDEX = ROOT / "docs/research/implementaudit/r0044-member-dispositions.json"


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def reseal(value):
    value.pop("projection_sha256", None)
    value["projection_sha256"] = hashlib.sha256(canonical(value)).hexdigest()
    return value


def run(*args, success=True):
    result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                            text=True, capture_output=True)
    if success:
        assert result.returncode == 0, result.stdout + result.stderr
    else:
        assert result.returncode != 0, "corruption was accepted: " + result.stdout
        assert "R0044_REJECTED" in result.stderr, result.stderr  # unallocated scope
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--custody-root", type=Path)
    args = parser.parse_args()
    assert SCRIPT.is_file(), "required public reconstruction consumer is absent"
    result = run("check", "--index", INDEX)
    assert json.loads(result.stdout)["scope"] == "INDEX_STRUCTURE_ONLY"
    original = json.loads(INDEX.read_text())
    assert len(original["rows"]) == 76
    rows = {r["id"]: r for r in original["rows"]}
    assert rows["EMAS-013"]["source_status"] == "UNRESOLVED"
    assert "historical_target_candidate" in rows["EMAS-013"], "public predecessor record is missing"
    assert json.loads(rows["EMAS-013"]["historical_target_candidate"]["record_json_unallocated"])["disposition"] == "UNRESOLVED_DISCRIMINATOR"
    assert rows["EMAS-013"]["prepared_target_absorption"] is None
    assert rows["EMAS-001"]["groups"] == ["AMA-K009", "AMA-K022", "AMA-K028"]
    assert original["relation_reconstruction"]["incident_direction_count"] == 11960
    assert original["relation_reconstruction"]["explicit_pair_count"] == 15352
    assert original["relation_reconstruction"]["explicit_no_material_count"] == 9694
    assert original["relation_reconstruction"]["hand_adjudicated_bridge_count"] == 75
    assert original["receiving_route"]["sibling_EAA"] == \
        "https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/232#issuecomment-6204277607", \
        "EAA host receipt must resolve at its actual issue, as bound by comment metadata"
    assert json.loads(original["TC10"]["public_antecedent_record_json_unallocated"])["parents"] == [
        "ESPLE:ESPLE-023", "EBPM:EBPM-022", "EPM:EPM-043", "EPM:EPM-064", "EMAS:EMAS-072", "EAOSE:EAOSE-C124"]
    controls = 1
    with tempfile.TemporaryDirectory(prefix="r0044-controls-") as tmp:
        target = Path(tmp) / "altered.json"

        def reject(change, *, seal=True, source=False):
            nonlocal controls
            data = copy.deepcopy(original)
            change(data)
            if seal:
                reseal(data)
            target.write_text(json.dumps(data, ensure_ascii=False) + "\n")
            extra = ["--custody-root", args.custody_root] if source else []
            run("check", "--index", target, *extra, success=False)
            controls += 1

        reject(lambda d: d["rows"].pop(12))
        reject(lambda d: d["rows"].__setitem__(13, d["rows"][12]))
        reject(lambda d: d["rows"][12].__setitem__("prepared_target_absorption", "RESEARCH_ONLY"))
        reject(lambda d: d["rows"][12].__setitem__("prepared_primary_or_secondary", "SECONDARY"))
        reject(lambda d: d["rows"][12]["source_obligation"].__setitem__("trigger", ""))
        reject(lambda d: d["rows"][12]["source_obligation"].__setitem__("required_evidence", []))
        reject(lambda d: d["rows"][12]["full_original"].__setitem__("pointer", "/properties/11"))
        reject(lambda d: d["rows"][0].__setitem__("original_global_key", "EMAS:EMAS-001"))
        reject(lambda d: d["rows"][0]["source_obligation"].__setitem__("trigger", "altered"), seal=False)
        reject(lambda d: d["relation_reconstruction"].__setitem__("missing_bridge_means_no_relation", True))
        if args.custody_root:
            result = run("check", "--index", INDEX, "--custody-root", args.custody_root)
            assert json.loads(result.stdout)["scope"] == "PINNED_PUBLIC_SOURCE_RECONSTRUCTION"
            controls += 1
            reject(lambda d: d["rows"][0]["source_obligation"].__setitem__("trigger", "plausible but invented"), source=True)
            reject(lambda d: d["rows"][71]["groups"].__setitem__(0, "AMA-K001"), source=True)
            reject(lambda d: d["receiving_route"].__setitem__("sibling_EAA",
                   "https://github.com/theislampill/IMPLEMENTAUDIT.md/issues/233#issuecomment-6204277607"), source=True)
            view = Path(tmp) / "member.json"
            run("member", "--index", INDEX, "--custody-root", args.custody_root,
                "--id", "EMAS-013", "--output", view)
            member = json.loads(view.read_text())
            assert member["original"]["PROPERTY_ID"] == "EMAS-013"
            assert member["original"]["CURRENT_STATUS"] == "UNRESOLVED"
            assert member["target_preparation"]["prepared_target_absorption"] is None
            assert member["incident_relations"] and member["explicit_pairs"]
            assert member["source_records"] and member["domain_profile_definitions"]
            assert all("joint_guard" in r["assumptions"] for r in member["incident_relations"])
            assert any(p["relation_status"] == "NO_MATERIAL_RELATION" for p in member["explicit_pairs"])
            assert all(p[field] in member["independent_endpoint_records"]
                       for p in member["explicit_pairs"] for field in ["left_property", "right_property"]), \
                "a no-material pair lost the full independent endpoint record"
            run("member", "--index", INDEX, "--custody-root", args.custody_root,
                "--id", "EMAS-999", "--output", view, success=False)
            controls += 2
    print(f"r0044-reconstruction: {controls} controls passed; "
          + ("pinned public corpus checked" if args.custody_root else "offline structure only"))


if __name__ == "__main__":
    main()
