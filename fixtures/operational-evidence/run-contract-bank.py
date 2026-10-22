"""Run the original contract bank with exact, fixture-only native dependencies.

The staged producer files are historical format/control inputs, never production
admission or native qualification. No dependency is added to skills/ in source.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    root = Path(sys.argv[1]).resolve()
    bash = sys.argv[2]
    fixture = root / "fixtures/operational-evidence"
    source = fixture / "native-source"
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest["scope"] != "FIXTURE_ONLY_NOT_NATIVE_ADMISSION" or len(manifest["files"]) != 11:
        raise SystemExit("R0038 fixture dependency population differs")
    verified = []
    for item in manifest["files"]:
        relative = Path(item["path"])
        if relative.is_absolute() or relative.drive or ".." in relative.parts:
            raise SystemExit("R0038 fixture dependency path refused")
        path = source / (item["path"] + ".fixture")
        raw = path.read_bytes()
        if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise SystemExit("R0038 fixture dependency identity differs: " + item["path"])
        verified.append((relative, raw))
    with tempfile.TemporaryDirectory(prefix="r0038-contract-fixture-") as directory:
        stage = Path(directory).resolve()
        for name in ("scripts/operational-evidence.py", "scripts/operational_query_policy.py",
                     "docs/operational-evidence-schema.json", "docs/operational-evidence.md",
                     "tests/operational-evidence-contract.test.sh"):
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
        shutil.copytree(fixture, stage / "fixtures/operational-evidence",
                        ignore=shutil.ignore_patterns("native-source", "__pycache__"))
        for relative, raw in verified:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        environment = os.environ.copy()
        environment["IMPLEMENTAUDIT_R0038_FIXTURE_STAGE"] = "1"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        print("R0038 default contract bank: eleven pinned dependencies; FIXTURE ONLY", flush=True)
        return subprocess.run([bash, str(stage / "tests/operational-evidence-contract.test.sh"),
                               *sys.argv[3:]], cwd=stage, env=environment).returncode


if __name__ == "__main__":
    raise SystemExit(main())
