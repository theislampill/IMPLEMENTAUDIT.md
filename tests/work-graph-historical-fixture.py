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
ENGINE_NAMES = ("scripts/qualify-work-graph-verifier.py",
                "scripts/run-work-graph-verifier.sh",
                "skills/implementaudit/scripts/compile-work-graph.py",
                "scripts/qualify-work-graph-finite-leaf.py",
                "scripts/qualify-work-graph-prefix.py")


def original(name):
    record = MANIFEST["files"][name]
    relative = Path(record["specimen"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("invalid historical specimen path")
    raw = (COLLECTION / relative).read_bytes()
    if len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("historical specimen changed: " + name)
    return raw


def input_bytes(name):
    """Pinned historical specimens; all other inputs are current variable data."""
    return original(name) if name in MANIFEST["files"] else (ROOT / name).read_bytes()


def input_mode(name):
    return MANIFEST["files"][name]["mode"] if name in MANIFEST["files"] else (ROOT / name).stat().st_mode & 0o777


def copy_input(name, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(input_bytes(name))
    destination.chmod(input_mode(name))


def populate_pins(destination, contract):
    """Call only at construction, after copies; never during snapshot or run."""
    pins = dict(contract["programs"], **contract.get("pinned_data", {}),
                **{"scripts/verify-package.sh": MANIFEST["files"]["scripts/verify-package.sh"]["sha256"]})
    for name, expected in pins.items():
        if hashlib.sha256(input_bytes(name)).hexdigest() != expected:
            raise ValueError("fixture does not supply selected historical pin: " + name)
        copy_input(name, Path(destination) / name)


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