"""Capture local output from two pinned, read-only PRELUDE Python blocks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory

root = Path(__file__).resolve().parents[3]
registry = (root / "scripts/verify-package.sh").read_bytes()
assert hashlib.sha256(registry).hexdigest() == "65c7b6939c7bf9396f83cdad58c735cabbc7e28232ceff816e7a8909bf625878"
blocks = list(re.finditer(rb"""(?ms)^"\$\{py_cmd\[@\]\}" - <<'PY'\n(.*?)^PY\n""", registry))
assert len(blocks) == 3
paths = {
    "skill": "skills/implementaudit/SKILL.md",
    "plugin": ".claude-plugin/plugin.json",
    "market": ".claude-plugin/marketplace.json",
    "readme": "README.md",
    "site": "docs/portal/site.json",
}
pins = {
    "skill": "a6b0e2801147508766572c7dc44599da1e8a804967bc4a0a0fb8427ac21600ef",
    "plugin": "858a0c4751581c08964d52bcd47bd04cc805e91abf672a6711a58acda34aaf70",
    "market": "baa07799a3061c8b99d286472e43ce1263655f4064447c07141d9503ab24b544",
    "readme": "2267eeb5948de8842d5aecb8d6207de509e3ccd41dee9d14c8be650781555de4",
    "site": "bbe81072627be8ef1c349dda3faa8a62b457362990758933b0fab561cae494a6",
}
defaults = {key: (root / value).read_bytes() for key, value in paths.items()}


def descriptor(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


assert all(descriptor(raw)["sha256"] == pins[key] for key, raw in defaults.items())


def edit_json(key, fn):
    doc = json.loads(defaults[key])
    fn(doc)
    return json.dumps(doc).encode()

claim_block = re.search(rb"(?m)^.*Current project milestone:.*$", defaults["readme"])[0]
isolate = [
    (1, "skill-frontmatter", "skill", b"no frontmatter\n", b"SKILL.md must have YAML frontmatter"),
    (1, "skill-version-present", "skill", b"---\nmetadata:\n  name: demo\n---\n", b"SKILL.md metadata.version is missing"),
    (1, "skill-plugin-version-equal", "skill", b"---\nmetadata:\n  version: 0.4.1\n---\n",
     b"SKILL.md metadata.version '0.4.1' != plugin.json version '0.4.0'"),
    (2, "plugin-name", "plugin", edit_json("plugin", lambda d: d.update(name="foreign")), b"plugin name must be implementaudit"),
    (2, "plugin-source-skills-path", "plugin", edit_json("plugin", lambda d: d.update(skills="./foreign/")), b"source plugin skills path must be ./skills/"),
    (2, "plugin-version-present", "plugin", edit_json("plugin", lambda d: d.pop("version")), b"plugin version is required"),
    (2, "plugin-family-version", "plugin", edit_json("plugin", lambda d: d.update(version="0.4.1")), b"plugin version must be 0.4.0"),
    (2, "marketplace-list-nonempty", "market", edit_json("market", lambda d: d.update(plugins=[])), b"marketplace plugins list is required"),
    (2, "marketplace-source-root", "market", edit_json("market", lambda d: d["plugins"][0].update(source="./foreign/")), b"source marketplace entry should point at plugin source root"),
    (2, "marketplace-path-absent", "market", edit_json("market", lambda d: d["plugins"][0].update(path="./skills/")), b"source marketplace entry must not use archive-only path"),
    (2, "milestone-shape", "site", edit_json("site", lambda d: d["release"].update(milestone="0.4.0")), b"release milestone must be v-prefixed with four numeric components"),
    (2, "milestone-family", "site", edit_json("site", lambda d: d["release"].update(milestone="v0.4.1.1")), b"does not belong to runtime family 0.4.0"),
    (2, "readme-claim-present", "readme", defaults["readme"].replace(b"Current project milestone:", b"Other milestone:"), b"README must state 'Current project milestone:'"),
    (2, "each-readme-claim-matches", "readme", defaults["readme"] + b"\n" + claim_block.replace(b"`0.4.0`", b"`0.4.1`") + b"\n",
     b"README version claim does not match milestone"),
]

collector_path = root / "scripts/qualify-work-graph-verifier-properties.py"
collector_pin = descriptor(collector_path.read_bytes())
assert collector_pin["sha256"] == "5d8c57d047c4ad4eb256db7fed948639712ce7cff75ec33413b9953f24ba521d"
spec = importlib.util.spec_from_file_location("property_capture", collector_path)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
executable = Path(sys.executable).resolve()
args = [str(executable), *collector.PYTHON_ARGS]


def execute(directory, index, files):
    for key, data in files.items():
        file = directory / paths[key]
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
    stdout, stderr, exit_code = collector.collect_checker(args, blocks[index][1], directory)
    return {"exit": exit_code, "stdout": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8")}


def main():
    cases = []
    with TemporaryDirectory(prefix="dg16-v02-prelude-") as name:
        directory = Path(name)
        for index in (1, 2):
            observed = execute(directory, index, defaults)
            assert observed == {"exit": 0, "stdout": "", "stderr": ""}
            cases.append({"id": f"unchanged-inputs-{index + 1}", "body": index + 1,
                          "alteration": None, **observed})
        for index, label, key, changed, message in isolate:
            assert changed != defaults[key], label
            observed = execute(directory, index, dict(defaults, **{key: changed}))
            assert observed["exit"] == 1 and not observed["stdout"], label
            assert message.decode("utf-8") in observed["stderr"], label
            assert observed["stderr"].count("\n") == 1 and observed["stderr"].endswith("\n"), label
            cases.append({"id": label, "body": index + 1, **observed,
                          "alteration": {"path": paths[key], **descriptor(changed)}})
    at = registry.index(b"bash scripts/generate-readme-diagrams.sh --check\n")
    evidence = {
        "schema": "dg16.v02.inline-version-control.v1",
        "authority": "NONE",
        "scope": "TWO_ISOLATED_READ_ONLY_PRELUDE_BODIES",
        "prelude": descriptor(registry[:at]),
        "registry": descriptor(registry),
        "capture_owner": collector_pin,
        "bodies": {index + 1: descriptor(blocks[index][1]) for index in (1, 2)},
        "inputs": {paths[key]: descriptor(data) for key, data in defaults.items()},
        "interpreter": {"version": list(sys.version_info[:3]), **descriptor(executable.read_bytes())},
        "python_args": list(collector.PYTHON_ARGS),
        "child_environment": collector.CHILD_ENV,
        "capture_bytes_limit": collector.OBSERVATION_LIMIT,
        "observations": cases,
        "canonical_execution": False,
    }
    sys.stdout.buffer.write((json.dumps(evidence, sort_keys=True, indent=2) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
