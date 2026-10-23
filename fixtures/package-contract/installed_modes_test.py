#!/usr/bin/env python3
"""Exercise real installed verifiers with modeled platform metadata.

This portable bank is not native Windows qualification. It retains real file
contents/populations and substitutes only the platform's stat representation.
"""
import argparse
import ast
import hashlib
import json
import os
import stat
import tempfile
import types
from pathlib import Path


class MetadataPath(type(Path())):
    platform = "posix"
    mutation = ""

    def stat(self, *, follow_symlinks=True):
        original = os.stat(self, follow_symlinks=follow_symlinks)
        if not stat.S_ISREG(original.st_mode):
            return original
        # Keep both declared metadata models independent of the executing host.
        mode = 0o755 if self.name == "probe.py" else 0o644
        attributes = stat.FILE_ATTRIBUTE_NORMAL
        if self.platform == "nt":
            mode = 0o666
        changed = self.name == "probe.py"
        if changed:
            if self.mutation == "readonly-attribute":
                attributes |= stat.FILE_ATTRIBUTE_READONLY
            elif self.mutation == "readonly-mode":
                mode = 0o444
            elif self.mutation == "unreadable-mode":
                mode = 0o222
            elif self.mutation == "reparse":
                attributes |= stat.FILE_ATTRIBUTE_REPARSE_POINT
            elif self.mutation == "posix-nonexecutable":
                mode = 0o644
            elif self.mutation == "posix-setuid":
                mode |= stat.S_ISUID
            elif self.mutation == "posix-setgid":
                mode |= stat.S_ISGID
            elif self.mutation == "posix-sticky":
                mode |= stat.S_ISVTX
        metadata = types.SimpleNamespace(st_mode=stat.S_IFREG | mode,
                                         st_file_attributes=attributes)
        if changed and self.mutation == "missing-attributes":
            del metadata.st_file_attributes
        if changed and self.mutation == "false-attributes":
            metadata.st_file_attributes = False
        if changed and self.mutation == "nonregular":
            metadata.st_mode = stat.S_IFDIR | mode
        if self.name == "IMPLEMENTAUDIT_INVENTORY.json" and self.mutation == "reparse-inventory":
            metadata.st_file_attributes |= stat.FILE_ATTRIBUTE_REPARSE_POINT
        return metadata


def load_owners(repo, contract):
    owners = []
    path = repo / "scripts/package-contract.py"
    module = types.ModuleType("package_contract_mode_fixture")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    owners.append((path.name, module, module.read_installed_inventory, "canonical_plugin"))
    for name in ("install-codex-from-release.sh", "install-claude-from-release.sh"):
        path = repo / "scripts" / name
        python_source = path.read_text().split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        parsed = ast.parse(python_source, str(path))
        # Load the actual imports/functions, without executing an installation.
        parsed.body = [node for node in parsed.body
                       if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        module = types.ModuleType(name)
        exec(compile(parsed, str(path), "exec"), module.__dict__)
        module.expected_required = contract["required_skills"]
        module.expected_internal = contract["internal_skills"]
        owners.append((name, module, module.read_installed_standalone,
                       "standalone_compatibility"))
    return owners


def make_fixture(root, contract, role):
    prefix = "skills/implementaudit/" if role == "canonical_plugin" else ""
    contents = {
        "IMPLEMENTAUDIT_PACKAGE.json": (json.dumps(contract) + "\n").encode(),
        prefix + "SKILL.md": b"Fixture governor\n",
        prefix + "scripts/probe.py": b"#!/usr/bin/env python3\n",
    }
    fields = ("package_name", "runtime_version", "release_family", "public_governor",
              "required_skills", "internal_skills")
    inventory = {key: contract[key] for key in fields}
    inventory.update({
        "schema": "implementaudit.package-inventory.v1", "artifact_role": role,
        "source": {"commit": "0" * 40, "tree": "1" * 40, "worktree_state": "clean"},
        "members": [{"path": name, "bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest()}
                    for name, data in sorted(contents.items())],
    })
    contents["IMPLEMENTAUDIT_INVENTORY.json"] = (json.dumps(inventory) + "\n").encode()
    for name, data in contents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o755 if name.endswith("probe.py") else 0o644)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    contract = json.loads((args.repo_root / "package/implementaudit-package.json").read_text())
    cases = [
        ("posix", "", True), ("nt", "", True),
        ("posix", "posix-nonexecutable", False),
        ("posix", "posix-setuid", False), ("posix", "posix-setgid", False),
        ("posix", "posix-sticky", False),
        ("nt", "readonly-attribute", False), ("nt", "readonly-mode", False),
        ("nt", "unreadable-mode", False), ("nt", "reparse", False),
        ("nt", "reparse-inventory", False), ("nt", "missing-attributes", False),
        ("nt", "false-attributes", False), ("nt", "nonregular", False),
        ("unsupported", "", False),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="installed-mode-fixture-") as temp:
        for owner, module, reader, role in load_owners(args.repo_root, contract):
            root = Path(temp) / owner
            make_fixture(root, contract, role)
            for platform, mutation, expected in cases:
                modeled_os = types.SimpleNamespace(**os.__dict__)
                modeled_os.name = platform
                module.os = modeled_os
                MetadataPath.platform, MetadataPath.mutation = platform, mutation
                try:
                    reader(MetadataPath(root))
                    accepted, message = True, ""
                except (ValueError, SystemExit) as exc:
                    accepted, message = False, str(exc)
                passed = accepted == expected
                results.append({"owner": owner, "platform_model": platform,
                                "mutation": mutation or "positive-control",
                                "expected_accept": expected, "accepted": accepted,
                                "passed": passed, "message": message})
                print(f"{'PASS' if passed else 'FAIL'} {owner} {platform} "
                      f"{mutation or 'positive-control'}: {message or 'accepted'}")
    report = {"proof": "SOURCE_AND_SIMULATED_METADATA_ONLY_NO_NATIVE_WINDOWS_PASS",
              "cases": results, "passed": sum(row["passed"] for row in results),
              "total": len(results)}
    if args.json_output:
        args.json_output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"installed-mode-portability: {report['passed']}/{report['total']} "
          "(modeled platform metadata; no native Windows qualification)")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
