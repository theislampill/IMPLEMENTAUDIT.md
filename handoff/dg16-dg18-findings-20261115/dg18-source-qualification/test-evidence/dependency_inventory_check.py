#!/usr/bin/env python3
"""Check only the exact workflow's metadata fragments with constructed inputs."""
import argparse
import builtins
import contextlib
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import shlex
import sys
import types
from unittest import mock


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True, type=Path)
    args = parser.parse_args()
    raw = args.workflow.read_bytes()
    lines = raw.decode().splitlines()
    required = next(line.strip() for line in lines
                    if "/usr/bin/python3 -I -c" in line and "assert" in line)
    argv = shlex.split(required)
    required_code = compile(argv[argv.index("-c") + 1], "workflow-required-tokenizer", "exec")
    first = next(i for i, line in enumerate(lines)
                 if "/usr/bin/python3 -I - <<'PY' >" in line and "DEPENDENCIES.txt" in line)
    last = next(i for i in range(first + 1, len(lines)) if lines[i] == "          PY")
    inventory_code = compile("\n".join(line[10:] for line in lines[first + 1:last]),
                             "workflow-dependency-inventory", "exec")
    names = ("tiktoken", "regex", "requests", "charset_normalizer", "idna", "urllib3", "certifi")
    present = {name: "0.13.0" if name == "tiktoken" else "fixture-present" for name in names}
    outcomes = []

    def check(label, *, missing=None, wrong_version=False, import_missing=False,
              disappears=False, unexpected=False, expected_error=None):
        calls = {}
        actual_import = builtins.__import__

        def version(name):
            calls[name] = calls.get(name, 0) + 1
            if name == missing or (disappears and name == "tiktoken" and calls[name] > 1):
                raise importlib.metadata.PackageNotFoundError(name)
            if unexpected and name == "regex":
                raise RuntimeError("constructed metadata reader failure")
            return "0.12.0" if wrong_version and name == "tiktoken" else present[name]

        def importing(name, *arguments, **keywords):
            if import_missing and name == "tiktoken":
                raise ImportError("constructed required tokenizer import failure")
            return actual_import(name, *arguments, **keywords)

        output = io.StringIO()
        error = None
        try:
            with mock.patch.object(importlib.metadata, "version", side_effect=version), \
                 mock.patch.dict(sys.modules, {"tiktoken": types.ModuleType("tiktoken")}), \
                 mock.patch.object(builtins, "__import__", side_effect=importing), \
                 contextlib.redirect_stdout(output):
                exec(required_code, {})
                exec(inventory_code, {})
        except Exception as exc:
            error = type(exc).__name__
        assert error == expected_error, (label, error, expected_error)
        if expected_error is None:
            expected = dict(present)
            if missing is not None:
                expected[missing] = "UNAVAILABLE"
            assert json.loads(output.getvalue()) == expected, label
        else:
            assert output.getvalue() == "", label
        outcomes.append({"case": label, "result": "PASS", "observed_error": error})

    check("all_seven_inventory_names_present")
    for name in names[1:]:
        check("missing_diagnostic_metadata:" + name, missing=name)
    check("missing_required_tiktoken_metadata_refuses", missing="tiktoken",
          expected_error="PackageNotFoundError")
    check("wrong_required_tiktoken_version_refuses", wrong_version=True,
          expected_error="AssertionError")
    check("required_tiktoken_import_failure_refuses", import_missing=True,
          expected_error="ImportError")
    check("required_metadata_disappears_during_inventory_refuses", disappears=True,
          expected_error="PackageNotFoundError")
    check("unexpected_diagnostic_error_refuses", unexpected=True,
          expected_error="RuntimeError")
    print(json.dumps({"schema": "implementaudit.dg18.dependency-inventory-checks.v1",
                      "workflow_sha256": hashlib.sha256(raw).hexdigest(),
                      "scope": "Only extracted metadata fragments; explicit constructed package metadata/imports; no install, source fixtures, native operation or hosted job.",
                      "cases": outcomes, "passed": len(outcomes)}, indent=2))


if __name__ == "__main__":
    main()
