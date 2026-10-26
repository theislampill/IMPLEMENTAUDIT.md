"""Exact historical test inputs and physical engines; no current acceptance.

Only fixture construction selects these bytes. Acquisition never repairs or
restores a subject. Current source/engine refusal tests use ROOT explicitly.
"""
import atexit
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "test-support/work-graph-registry"
MANIFEST = json.loads((COLLECTION / "original117-manifest.json").read_bytes())
assert MANIFEST["source_commit"] == "cbb616cc7e0f9abafebe9bbdeee202ede7feb94e"
assert MANIFEST["scope"] == "HISTORICAL_INPUTS_ONLY_NOT_CURRENT_ACCEPTANCE"
# Previously unchanged files absent from the original fixture manifest.
# Retain exact cbb616cc bytes without editing that manifest or its source pins.
SUPPLEMENTAL = {
    "scripts/run-work-graph-verifier.sh": {
        "specimen": "original117-runner/run-work-graph-verifier.sh", "bytes": 14452,
        "sha256": "532b06dbe91298bf71d44c88ecf20186adc93b4e3fb16ee2c4d12bc2edee45ff", "mode": 0o644,
    },
    "scripts/work-graph-completion.py": {
        "specimen": "original117-completion/work-graph-completion.py", "bytes": 27353,
        "sha256": "1a73009c7085c66797d9310258b2b1d723f304a0034cbc6a7ce16e1c97283b92", "mode": 0o644,
    },
}
ENGINE_NAMES = ("scripts/qualify-work-graph-verifier.py",
                "scripts/run-work-graph-verifier.sh",
                "skills/implementaudit/scripts/compile-work-graph.py",
                "scripts/qualify-work-graph-finite-leaf.py",
                "scripts/qualify-work-graph-prefix.py")


def original(name):
    record = MANIFEST["files"][name] if name in MANIFEST["files"] else SUPPLEMENTAL[name]
    relative = Path(record["specimen"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("invalid historical specimen path")
    raw = (COLLECTION / relative).read_bytes()
    if len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("historical specimen changed: " + name)
    return raw


def input_bytes(name):
    """Pinned historical specimens; all other inputs are current variable data."""
    return original(name) if name in MANIFEST["files"] or name in SUPPLEMENTAL else (ROOT / name).read_bytes()


def input_mode(name):
    if name in MANIFEST["files"] or name in SUPPLEMENTAL:
        return (MANIFEST["files"].get(name) or SUPPLEMENTAL[name])["mode"]
    return (ROOT / name).stat().st_mode & 0o777


def copy_input(name, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(input_bytes(name))
    destination.chmod(input_mode(name))


def selected_input_bytes(name, expected):
    """An explicit successor runner selection never changes historical defaults."""
    if (name == "scripts/run-work-graph-verifier.sh" and expected ==
            "6f6d2bdbcf8350d6b370d37a5e15f4ddb73d336b5bc42d941540f3269613150f"):
        raw = (ROOT / name).read_bytes()
    else:
        raw = input_bytes(name)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("fixture does not supply selected source pin: " + name)
    return raw


def populate_pins(destination, contract):
    """Call only at construction, after copies; never during snapshot or run."""
    pins = dict(contract["programs"], **contract.get("pinned_data", {}),
                **{"scripts/verify-package.sh": MANIFEST["files"]["scripts/verify-package.sh"]["sha256"]})
    for name, expected in pins.items():
        raw = selected_input_bytes(name, expected)
        target = Path(destination) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        target.chmod(input_mode(name))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(Path(path).read_bytes(), str(path), "exec"), module.__dict__)
    return module


def copy_engine(destination):
    """Current driver/compiler/finite helper plus its exact historical dependency."""
    destination = Path(destination)
    for name in ENGINE_NAMES:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = original(name) if name == "scripts/qualify-work-graph-prefix.py" else (ROOT / name).read_bytes()
        path.write_bytes(raw)
        path.chmod((ROOT / name).stat().st_mode & 0o777)
    return destination


def copy_continuity_engine(destination):
    """Current compiler/receiver/transport over the exact historical six sources."""
    destination = Path(destination)
    for name in ("scripts/operational-evidence.py", "scripts/operational_query_policy.py",
                 "scripts/work-graph-continuity-transport.py",
                 "skills/implementaudit/scripts/compile-work-graph.py"):
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
        path.chmod((ROOT / name).stat().st_mode & 0o777)
    for name in ("claim-run.sh", "validate-run-root.sh", "claim-run-rotation.py",
                 "rotate-canonical-state.py", "canonical_hot_projection.py", "canonical_custody.py"):
        copy_input("skills/implementaudit/scripts/" + name,
                   destination / "skills/implementaudit/scripts" / name)
    return destination


def copy_readme_engine(destination):
    """Current fixed loader/owner tested against its complete exact selected closure."""
    destination = Path(destination)
    loader = load("historical_loader_catalog", ROOT / "scripts/load-work-graph-readme-effect.py")
    for name in (*loader.PINS, loader.LOADER):
        raw = input_bytes(name) if name in loader.PINS else (ROOT / name).read_bytes()
        if name in loader.PINS and hashlib.sha256(raw).hexdigest() != loader.PINS[name]:
            raise ValueError("historical README engine pin mismatch: " + name)
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod((ROOT / name).stat().st_mode & 0o777)
    return destination


_engine_directory = tempfile.TemporaryDirectory(prefix="r0035-historical-fixture-engine-")
atexit.register(_engine_directory.cleanup)
ENGINE_ROOT = copy_engine(Path(_engine_directory.name))
Q = load("historical_input_current_qualifier", ENGINE_ROOT / ENGINE_NAMES[0])
P = load("historical_prefix_dependency", ENGINE_ROOT / ENGINE_NAMES[-1])
