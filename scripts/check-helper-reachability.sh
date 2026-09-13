#!/usr/bin/env bash
set -euo pipefail

authority_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$authority_root"
census_only=0
if [ "${1:-}" = "--census-only" ]; then
  census_only=1
  shift
fi
if [ "${1:-}" = "--repo-root" ]; then
  [ "$#" -eq 2 ] || { printf 'check-helper-reachability: usage: [--census-only] [--repo-root <dir>]\n' >&2; exit 2; }
  repo_root="$(cd "$2" && pwd)"
elif [ "$#" -ne 0 ]; then
  printf 'check-helper-reachability: usage: [--census-only] [--repo-root <dir>]\n' >&2
  exit 2
fi

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'check-helper-reachability: python, python3, or py -3 is required\n' >&2
  exit 2
fi

"${py_cmd[@]}" - "$repo_root" "$authority_root" "$BASH" "$census_only" <<'PY'
import os
import json
import re
import signal
import subprocess
import sys
from pathlib import Path

if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    class _BasicLimit(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]
    class _IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]
    class _ExtendedLimit(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", _BasicLimit), ("IoInfo", _IoCounters),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]
    class _KillOnCloseJob:
        def __init__(self):
            self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            self.handle = self.kernel32.CreateJobObjectW(None, None)
            if not self.handle: raise OSError(ctypes.get_last_error(), "CreateJobObjectW")
            limits = _ExtendedLimit()
            limits.BasicLimitInformation.LimitFlags = 0x00002000  # KILL_ON_JOB_CLOSE
            if not self.kernel32.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
                self.close(); raise OSError(ctypes.get_last_error(), "SetInformationJobObject")
        def assign(self, process):
            if not self.kernel32.AssignProcessToJobObject(self.handle, wintypes.HANDLE(process._handle)):
                self.close(); raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject")
        def close(self):
            if self.handle:
                self.kernel32.CloseHandle(self.handle)
                self.handle = None

root = Path(sys.argv[1]).resolve()
authority_root = Path(sys.argv[2]).resolve()
bash_runner = sys.argv[3]
census_only = sys.argv[4] == "1"
builder = root / "scripts" / "package-contract.py"
package_contract = root / "package" / "implementaudit-package.json"
skill_root = root / "skills" / "implementaudit"
contract = skill_root / "references" / "repo-state-comparison.md"
for path in (builder, package_contract, skill_root, contract):
    if not path.exists():
        raise SystemExit(f"check-helper-reachability: missing owner: {path}")

builder_text = builder.read_text(encoding="utf-8")
try:
    package = json.loads(package_contract.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"check-helper-reachability: package contract is unreadable: {exc}") from exc
shared_roots = package.get("shared_resource_roots")
if not isinstance(shared_roots, list) or "skills/implementaudit/scripts" not in shared_roots:
    raise SystemExit("check-helper-reachability: package contract omits the shared helper root")
if "EXPECTED_SHARED_ROOTS" not in builder_text or "contract.get(\"shared_resource_roots\")" not in builder_text:
    raise SystemExit("check-helper-reachability: package builder does not enforce shared resources")
archive_entries = {"SKILL.md"}
for shared_root in shared_roots:
    prefix = "skills/implementaudit/"
    if not isinstance(shared_root, str) or not shared_root.startswith(prefix):
        raise SystemExit("check-helper-reachability: package shared root escapes the governor")
    source_root = root / shared_root
    if not source_root.is_dir():
        raise SystemExit(f"check-helper-reachability: missing package shared root: {shared_root}")
    archive_entries.update(
        path.relative_to(skill_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file()
    )
# The selected checker root supplies executable package-owner code; the
# candidate supplies data only. Execute the exact buffer whose identity was
# checked, never a candidate-selected builder or a later unchecked reread.
import types
trusted_builder = authority_root / "scripts" / "package-contract.py"
builder_raw = trusted_builder.read_bytes()
if builder.read_bytes() != builder_raw:
    raise SystemExit("check-helper-reachability: package owner differs from selected checker owner")
package_owner = types.ModuleType("_helper_census_package_owner")
package_owner.__file__ = str(trusted_builder)
sys.modules[package_owner.__name__] = package_owner
exec(compile(builder_raw, str(trusted_builder), "exec"), package_owner.__dict__)

# The existing builder emits modes and paths separately for both projections.
# No suffix or route declaration selects membership. Unknown types remain in
# this executable denominator and are refused below.
projection_prefixes = {"canonical_plugin": "skills/implementaudit/",
                       "standalone_compatibility": ""}
projection_members = {}
projection_payloads = {}
for role, prefix in projection_prefixes.items():
    try:
        entries = package_owner.artifact_payload_entries(root, role, package)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(f"check-helper-reachability: package population unavailable: {role}: {error}")
    members = [path for path, _data, mode in entries
               if path.startswith(prefix + "scripts/") and mode & 0o111]
    if len(members) != len(set(members)):
        raise SystemExit(f"check-helper-reachability: duplicate executable package member: {role}")
    projection_members[role] = set(members)
    projection_payloads[role] = {path:data for path,data,_mode in entries}

canonical_relative = {path.removeprefix("skills/implementaudit/")
                      for path in projection_members["canonical_plugin"]}
if canonical_relative != projection_members["standalone_compatibility"]:
    raise SystemExit("check-helper-reachability: executable projection parity differs")
helpers = sorted(path.removeprefix("scripts/") for path in canonical_relative)
for helper in helpers:
    path = skill_root / "scripts" / helper
    if path.suffix not in {".sh", ".py"}:
        raise SystemExit(f"check-helper-reachability: UNKNOWN_EXECUTABLE_TYPE: scripts/{helper}")
    # Suffix identifies an explicitly supported interpreter after enumeration.
    # It never admits a pathname into, or excludes it from, the population.

contract_text = contract.read_text(encoding="utf-8")
rows, mode_rows, role_rows = {}, {}, {}
for line_number, line in enumerate(contract_text.splitlines(), 1):
    if line.startswith("helper-role: "):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 8:
            raise SystemExit(f"check-helper-reachability: malformed role row at line {line_number}")
        role = parts[0].removeprefix("helper-role: ")
        member = parts[1]
        if role not in projection_prefixes or not member.startswith("scripts/") or ".." in Path(member).parts or chr(92) in member:
            raise SystemExit(f"check-helper-reachability: invalid role/member: {role}: {member}")
        helper = member.removeprefix("scripts/")
        if helper in role_rows.setdefault(role, {}):
            raise SystemExit(f"check-helper-reachability: duplicate role row: {role}: {helper}")
        role_rows[role][helper] = dict(zip(("class","trigger","owner","caller","arguments","boundary"),parts[2:]))
    elif line.startswith("helper-mode: "):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) not in {4, 5}:
            raise SystemExit(f"check-helper-reachability: malformed helper mode at line {line_number}")
        helper = parts[0].removeprefix("helper-mode: ")
        key = (helper, parts[1])
        if key in mode_rows:
            raise SystemExit(f"check-helper-reachability: duplicate mode applicability row: {' '.join(key)}")
        mode_rows[key] = {"arguments": parts[2], "boundary": parts[3],
                          "caller": parts[4] if len(parts) == 5 else "-"}
    elif line.startswith("helper-route: "):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 7:
            raise SystemExit(f"check-helper-reachability: malformed helper route at line {line_number}")
        member = parts[0].removeprefix("helper-route: ")
        if (not member.startswith("scripts/") or "\\\\" in member
                or Path(member).as_posix() != member or ".." in Path(member).parts
                or member == "scripts/"):
            raise SystemExit(f"check-helper-reachability: route is not a full package member path: {member}")
        helper = member.removeprefix("scripts/")
        if helper in rows:
            raise SystemExit(f"check-helper-reachability: duplicate applicability row: {helper}")
        rows[helper] = {"class": parts[1], "trigger": parts[2], "owner": parts[3],
                        "caller": parts[4], "arguments": parts[5], "boundary": parts[6]}

# Compare exact role-specific full paths; equal cardinality is insufficient.
for role, prefix in projection_prefixes.items():
    classified = {prefix + "scripts/" + helper for helper in rows}
    if classified == projection_members[role]:
        continue
    # Existing diagnostics below distinguish missing and extra relative paths.
    break
missing, extra = sorted(set(helpers) - set(rows)), sorted(set(rows) - set(helpers))
if missing:
    suffix = f" (population={len(helpers)} examined={len(rows)})" if len(helpers) != len(rows) else ""
    raise SystemExit("check-helper-reachability: missing applicability rows: " + ", ".join(missing) + suffix)
if extra:
    raise SystemExit("check-helper-reachability: applicability rows not in package: " + ", ".join(extra))

class_names = {"A": "automatic", "R": "required-procedural", "O": "optional-advisory",
               "S": "standalone-diagnostic", "I": "internal-library"}
owner_aliases = {"P": "templates/PROTOCOL.md", "R": "references/repo-state-comparison.md",
                 "C": "references/child-agents.md", "S": "SKILL.md",
                 "V": "scripts/validate-run-root.sh"}
mandatory_re = re.compile(r"(?i)(?:^|[-_ ])(?:must|mandatory|required|block|gate)(?:$|[-_ .,;:`])")

def field_is_anchored(value, content):
    for part in value.lower().replace("artefact", "artifact").split("/"):
        words = [word for word in re.split(r"[^a-z0-9]+", part)
                 if len(word) >= 3 and word not in {"none", "only", "never", "automatic"}]
        if words and all(word in content for word in words):
            return True
    return False

def arguments_are_anchored(value, helper, content):
    token_re = re.compile(r"--[a-z0-9][a-z0-9-]*|<[^>]+>|\.\.\.|[a-z0-9][a-z0-9-]*")
    expected = [] if value.lower() == "none" else token_re.findall(value.lower())
    candidates = re.findall(r"`([^`]*" + re.escape(helper) + r"[^`]*)`", content, re.I | re.S)
    candidates.extend(line.split("#", 1)[0] for line in content.splitlines()
                      if helper in line and "`" not in line and re.match(r"\s*(?:bash|source|exec|python3?|py)\b", line, re.I))
    for candidate in candidates:
        found = re.search(re.escape(helper), candidate, re.I)
        actual = token_re.findall(candidate[found.end():].lower()) if found else []
        if actual == expected:
            return True
    return False

def shell_code(content):
    cleaned = []
    for line in content.splitlines():
        quote, escaped, kept = None, False, []
        for index, char in enumerate(line):
            if escaped:
                kept.append(char); escaped = False; continue
            if char == "\\" and quote != "'":
                kept.append(char); escaped = True; continue
            if char in {"'", '"'}:
                quote = None if quote == char else (char if quote is None else quote)
                kept.append(char); continue
            if char == "#" and quote is None and (index == 0 or line[index - 1].isspace()):
                break
            kept.append(char)
        cleaned.append("".join(kept))
    return "\n".join(cleaned)

def caller_invokes(helper, content):
    content = shell_code(content)
    def command_uses(target, path_prefix=False):
        prefix = r"(?:[^\s\"']*/)?" if path_prefix else ""
        operand = rf"[\"']?{prefix}{target}[\"']?(?=\s|$)"
        direct = rf"(?m)^\s*(?:[A-Za-z_][A-Za-z0-9_]*=(?:[^\s]+|\"[^\"]*\"|'[^']*')\s+)*(?:(?:if|while|until|!)\s+)?(?:bash|source|exec)?\s*{operand}"
        substitution = rf"(?mx)^\s*[a-z_][a-z0-9_]*\s*=\s*[\"']?\$\(\s*(?:bash|source|exec)\s+{operand}"
        return bool(re.search(direct, content, re.I) or re.search(substitution, content, re.I))
    if command_uses(re.escape(helper), path_prefix=True):
        return True
    assignment = None
    for line in content.splitlines():
        candidate = re.match(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*(.+?)\s*$", line, re.I)
        if candidate:
            value = candidate.group(2)
            value = value[1:-1] if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'} else value
            if re.search(rf"(?:^|/){re.escape(helper)}$", value):
                assignment = candidate
                break
    return bool(assignment and command_uses(rf"\${{?{re.escape(assignment.group(1))}}}?"))

def packaged_path(raw, helper, role):
    rel = Path(raw)
    if rel.is_absolute() or ".." in rel.parts:
        raise SystemExit(f"check-helper-reachability: invalid {role}: {helper}: {raw}")
    if rel.as_posix() not in archive_entries:
        raise SystemExit(f"check-helper-reachability: unshipped {role}: {helper}: {raw}")
    path = skill_root / rel
    try:
        path.resolve().relative_to(skill_root.resolve())
    except (OSError, ValueError):
        raise SystemExit(f"check-helper-reachability: invalid {role}: {helper}: {raw}")
    if not path.is_file():
        raise SystemExit(f"check-helper-reachability: missing {role}: {helper}: {raw}")
    return path

# Bounded source-edge reader. It never imports or executes candidate helpers.
# Only literal paths, named local loader calls and the supported Python
# spec/compile/subprocess forms can establish an edge. Unknown values are not
# guessed into paths or executable identities.
import ast
import posixpath
from pathlib import PurePosixPath

class SourceValue:
    def __init__(self, kind, value=None):
        self.kind, self.value = kind, value

def unknown():
    return SourceValue("unknown")

class PythonEdges:
    def __init__(self, payload):
        self.payload = payload
        self.modules = {}
        self.loader_functions = set()
        self.loaded = set()
        self.apis = set()
        self.cli = set()
        self.depth = 0
        self.steps = 0
        self.active = set()

    def canonical(self, value):
        if not isinstance(value, PurePosixPath):
            return None
        name = posixpath.normpath(value.as_posix())
        return name if name in self.payload and name.endswith(".py") else None

    def module(self, name):
        if name in self.modules:
            return self.modules[name]
        try:
            tree = ast.parse(self.payload[name].decode("utf-8"), filename=name)
        except (UnicodeError, SyntaxError):
            raise SystemExit("check-helper-reachability: invalid Python caller source: " + name)
        env = {"__file__": PurePosixPath(name), "__name__": "_r001e_static_source_"}
        funcs = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for key, node in funcs.items():
            env[key] = SourceValue("function", (name, node))
        seeds = {key for key, node in funcs.items() if any(
            isinstance(call, ast.Call) and (
                isinstance(call.func, ast.Name) and call.func.id in {"exec", "compile"} or
                isinstance(call.func, ast.Attribute) and call.func.attr in {"spec_from_file_location", "exec_module"})
            for call in ast.walk(node))}
        for _ in range(len(funcs)):
            expanded = seeds | {key for key, node in funcs.items() if any(
                isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in seeds
                for call in ast.walk(node))}
            if expanded == seeds: break
            seeds = expanded
        self.loader_functions.update((name, key) for key in seeds)
        self.modules[name] = (tree, env, funcs)
        self.block(tree.body, env, name, define=True)
        return self.modules[name]

    def assign(self, node, value, env, source):
        if isinstance(node, ast.Name):
            env[node.id] = value
        elif isinstance(node, (ast.Tuple, ast.List)) and isinstance(value, (tuple, list)):
            if len(node.elts) == len(value):
                for target, item in zip(node.elts, value):
                    self.assign(target, item, env, source)
        elif isinstance(node, ast.Attribute):
            obj = self.value(node.value, env, source)
            if isinstance(obj, SourceValue) and obj.kind == "module" and node.attr == "__file__":
                path = self.canonical(value)
                if path:
                    obj.value = path
        elif isinstance(node, ast.Subscript):
            obj, key = self.value(node.value, env, source), self.value(node.slice, env, source)
            if isinstance(obj, dict):
                try: obj[key] = value
                except TypeError: pass

    def call_function(self, function, args, kwargs):
        source, node = function.value
        identity = (source, node.name)
        if self.depth >= 12 or identity in self.active:
            return unknown()
        tree, global_env, funcs = self.module(source)
        env = dict(global_env)
        params = list(node.args.posonlyargs) + list(node.args.args)
        for index, param in enumerate(params):
            env[param.arg] = args[index] if index < len(args) else kwargs.get(param.arg, unknown())
        for param in node.args.kwonlyargs:
            env[param.arg] = kwargs.get(param.arg, unknown())
        self.active.add(identity); self.depth += 1
        try:
            returned, value = self.block(node.body, env, source)
            return value if returned else unknown()
        finally:
            self.depth -= 1; self.active.remove(identity)

    def value(self, node, env, source):
        self.steps += 1
        if self.steps > 30000:
            raise SystemExit("check-helper-reachability: Python caller analysis bound exceeded: " + source)
        if node is None:
            return None
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return env.get(node.id, SourceValue("symbol", node.id) if node.id in {
                "str","compile","exec","list","dict","set","len","all","any","getattr",
                "isinstance","range","enumerate","zip","bool","type","sorted"} else unknown())
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return [self.value(item, env, source) for item in node.elts]
        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                if key is None: continue
                k = self.value(key, env, source)
                try: result[k] = self.value(value, env, source)
                except TypeError: pass
            return result
        if isinstance(node, ast.BinOp):
            left, right = self.value(node.left, env, source), self.value(node.right, env, source)
            if isinstance(node.op, ast.Div) and isinstance(left, PurePosixPath) and isinstance(right, str):
                return left / right
            if isinstance(node.op, ast.Add) and isinstance(left, str) and isinstance(right, str):
                return left + right
            return unknown()
        if isinstance(node, ast.IfExp):
            condition=self.value(node.test,env,source)
            if condition is True or condition is False:
                return self.value(node.body if condition else node.orelse,env,source)
            left=self.value(node.body,env,source);right=self.value(node.orelse,env,source)
            return left if left is right else unknown()
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            a, b = self.value(node.left, env, source), self.value(node.comparators[0], env, source)
            if isinstance(a, SourceValue) or isinstance(b, SourceValue): return unknown()
            try:
                op=node.ops[0]
                if isinstance(op, ast.Eq): return a == b
                if isinstance(op, ast.NotEq): return a != b
                if isinstance(op, ast.Is): return a is b
                if isinstance(op, ast.IsNot): return a is not b
                if isinstance(op, ast.In): return a in b
                if isinstance(op, ast.NotIn): return a not in b
            except TypeError: pass
            return unknown()
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            item=self.value(node.operand,env,source)
            return not item if isinstance(item, (bool,type(None))) else unknown()
        if isinstance(node, ast.Attribute):
            obj = self.value(node.value, env, source)
            if isinstance(obj, PurePosixPath):
                if node.attr == "parent": return obj.parent
                if node.attr == "parents": return list(obj.parents)
                if node.attr == "name": return obj.name
                if node.attr == "stem": return obj.stem
                return SourceValue("path-method", (obj, node.attr))
            if isinstance(obj, SourceValue):
                if obj.kind == "symbol":
                    return SourceValue("symbol", obj.value + "." + node.attr)
                if obj.kind == "spec" and node.attr == "loader":
                    return SourceValue("loader", obj.value)
                if obj.kind == "loader" and node.attr == "exec_module":
                    return SourceValue("exec-module", obj.value)
                if obj.kind == "module":
                    if node.attr == "__dict__": return SourceValue("namespace", obj)
                    if obj.value:
                        module = self.module(obj.value)
                        exports = set(module[1]) | {item.name for item in module[0].body if isinstance(item, ast.ClassDef)}
                        if node.attr not in exports:
                            return unknown()
                        self.apis.add((obj.value, node.attr))
                        if node.attr in module[2]:
                            return SourceValue("function", (obj.value, module[2][node.attr]))
                        return module[1].get(node.attr, unknown())
                    return unknown()
            if isinstance(obj, list):
                return SourceValue("list-method", (obj,node.attr))
            if isinstance(obj, dict):
                return SourceValue("dict-method", (obj,node.attr))
            return unknown()
        if isinstance(node, ast.Subscript):
            obj,key=self.value(node.value,env,source),self.value(node.slice,env,source)
            try: return obj[key] if isinstance(obj,(dict,list,tuple)) else unknown()
            except (KeyError,IndexError,TypeError): return unknown()
        if isinstance(node, ast.Call):
            fn=self.value(node.func,env,source)
            args=[self.value(arg,env,source) for arg in node.args]
            kwargs={arg.arg:self.value(arg.value,env,source) for arg in node.keywords if arg.arg is not None}
            if not isinstance(fn,SourceValue): return unknown()
            if fn.kind == "function":
                identity = (fn.value[0], fn.value[1].name)
                if identity in self.loader_functions or any(self.canonical(arg) for arg in args):
                    return self.call_function(fn,args,kwargs)
                return unknown()
            if fn.kind == "path-method":
                path, method=fn.value
                if method in {"resolve","absolute"}: return path
                if method == "with_name" and args and isinstance(args[0],str):
                    try: return path.with_name(args[0])
                    except ValueError: return unknown()
                if method == "read_bytes":
                    target=self.canonical(path)
                    return SourceValue("buffer",target) if target else unknown()
                if method in {"as_posix","__str__"}: return path
                return unknown()
            if fn.kind == "list-method":
                obj,method=fn.value
                if method == "append" and args and len(obj)<128: obj.append(args[0])
                elif method == "extend" and args and isinstance(args[0],list) and len(obj)+len(args[0])<=128: obj.extend(args[0])
                return None
            if fn.kind == "dict-method":
                obj,method=fn.value
                if method == "items": return list(obj.items())
                if method == "get" and args:
                    try: return obj.get(args[0],args[1] if len(args)>1 else None)
                    except TypeError: return unknown()
                return unknown()
            if fn.kind == "exec-module":
                if args and isinstance(args[0],SourceValue) and args[0].kind=="module" and args[0].value==fn.value:
                    self.loaded.add(fn.value)
                return None
            if fn.kind != "symbol": return unknown()
            name=fn.value
            if name in {"pathlib.Path","pathlib.PurePosixPath"}:
                return args[0] if args and isinstance(args[0],PurePosixPath) else unknown()
            if name in {"str","os.fspath"} and args:
                return args[0] if isinstance(args[0],(str,PurePosixPath)) else unknown()
            if name == "importlib.util.spec_from_file_location" and len(args)>=2:
                target=self.canonical(args[1])
                return SourceValue("spec",target) if target else unknown()
            if name == "importlib.util.module_from_spec" and args and isinstance(args[0],SourceValue) and args[0].kind=="spec":
                return SourceValue("module",args[0].value)
            if name in {"types.ModuleType"}:
                return SourceValue("module")
            if name == "compile" and len(args)>=3 and args[2]=="exec":
                if isinstance(args[0],SourceValue) and args[0].kind=="buffer" and self.canonical(args[1])==args[0].value:
                    return SourceValue("compiled",args[0].value)
                return unknown()
            if name == "exec" and len(args)>=2:
                if (isinstance(args[0],SourceValue) and args[0].kind=="compiled" and
                    isinstance(args[1],SourceValue) and args[1].kind=="namespace"):
                    target=args[0].value; module=args[1].value
                    if module.value is None or module.value==target:
                        module.value=target;self.loaded.add(target)
                return None
            if name in {"subprocess.run","subprocess.check_output","subprocess.Popen"} and args and isinstance(args[0],list):
                argv=args[0]
                if argv and isinstance(argv[0],SourceValue) and argv[0].kind=="symbol" and argv[0].value=="sys.executable":
                    for index,value in enumerate(argv[1:],1):
                        target=self.canonical(value)
                        if target:
                            self.cli.add((target,tuple(value for value in argv[index+1:] if isinstance(value,str))))
                            break
                return unknown()
            return unknown()
        return unknown()

    def block(self, statements, env, source, define=False):
        for node in statements:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                continue
            if isinstance(node,ast.Import):
                for alias in node.names:
                    env[alias.asname or alias.name.split(".")[0]]=SourceValue("symbol",alias.name if alias.asname else alias.name.split(".")[0])
            elif isinstance(node,ast.ImportFrom):
                for alias in node.names:
                    env[alias.asname or alias.name]=SourceValue("symbol",(node.module+"." if node.module else "")+alias.name)
            elif isinstance(node,(ast.Assign,ast.AnnAssign)):
                value=self.value(node.value,env,source)
                for target in node.targets if isinstance(node,ast.Assign) else [node.target]:
                    self.assign(target,value,env,source)
            elif isinstance(node,ast.Expr):
                self.value(node.value,env,source)
            elif isinstance(node,ast.Return):
                return True,self.value(node.value,env,source)
            elif isinstance(node,ast.Raise):
                return True,unknown()
            elif isinstance(node,ast.If):
                condition=self.value(node.test,env,source)
                if condition is True or condition is False:
                    result=self.block(node.body if condition else node.orelse,env,source)
                    if result[0]: return result
                else:
                    # Conditional source edges are possibilities, never evidence
                    # that the live trigger or an authorization predicate held.
                    left,right=dict(env),dict(env)
                    self.block(node.body,left,source);self.block(node.orelse,right,source)
                    for key in set(left)|set(right):
                        if left.get(key) is right.get(key):env[key]=left.get(key)
                        else:env[key]=unknown()
            elif isinstance(node,ast.For):
                values=self.value(node.iter,env,source)
                if isinstance(values,(list,tuple)) and len(values)<=128:
                    for value in values:
                        self.assign(node.target,value,env,source);self.block(node.body,env,source)
                else:
                    self.block(node.body,dict(env),source)
            elif isinstance(node,ast.Try):
                result=self.block(node.body,env,source)
                self.block(node.finalbody,env,source)
                if result[0]:return result
            elif isinstance(node,(ast.With,ast.AsyncWith)):
                for item in node.items:
                    value=self.value(item.context_expr,env,source)
                    if item.optional_vars:self.assign(item.optional_vars,value,env,source)
                result=self.block(node.body,env,source)
                if result[0]:return result
        return False,unknown()

    def inspect(self, source, selector):
        self.steps = 0
        tree,env,funcs=self.module(source)
        if selector:
            if selector not in funcs:
                raise SystemExit("check-helper-reachability: Python caller function absent: "+source+"#"+selector)
            self.call_function(SourceValue("function",(source,funcs[selector])),[],{})
        else:
            for name,node in funcs.items():
                self.call_function(SourceValue("function",(source,node)),[],{})
        return self.loaded,self.apis,self.cli



implemented_mode_sets = {}
graph_helper = "validate-run-root.sh"
graph_text = (skill_root / "scripts" / graph_helper).read_text(encoding="utf-8")
implemented_mode_sets[graph_helper] = sorted(set(re.findall(r"--graph-[a-z0-9-]+", graph_text)))
rehearsal_helper, rehearsal_mode = "check-authorization-binding.sh", "--phase --rehearsal --launch"
# R0020: static census records the declared mode; candidate-bound F10 below is
# the only execution authority for its parser, mediator, wrapper, and stub.
implemented_mode_sets[rehearsal_helper] = [rehearsal_mode]
implemented_mode_sets["check-evidence-anchor.sh"] = ["--window-transition"]

for helper, mode in mode_rows:
    if helper not in helpers or mode not in implemented_mode_sets.get(helper, []):
        raise SystemExit(f"check-helper-reachability: mode applicability not implemented: {helper} {mode}")
for helper, implemented_modes in implemented_mode_sets.items():
    declared_modes = sorted(mode for row_helper, mode in mode_rows if row_helper == helper)
    missing_modes = sorted(set(implemented_modes) - set(declared_modes))
    if missing_modes:
        raise SystemExit("check-helper-reachability: missing mode applicability rows: " + ", ".join(
            f"{helper} {mode}" for mode in missing_modes))

mode_owner = "\n".join(line for line in contract_text.splitlines()
                       if not line.startswith(("helper-route: ", "helper-role: ", "helper-mode: ")))
for helper, mode in mode_rows:
    row = mode_rows[(helper, mode)]
    mode_flags, mode_args = mode.split(), row["arguments"].split()
    mode_command = f"{mode} {row['arguments']}"
    if len(mode_flags) > 1:
        if len(mode_flags) != len(mode_args):
            raise SystemExit(f"check-helper-reachability: mode argument arity mismatch: {helper} {mode}")
        mode_command = " ".join(f"{flag} {argument}" for flag, argument in zip(mode_flags, mode_args))
    if not arguments_are_anchored(mode_command, helper, mode_owner):
        raise SystemExit(f"check-helper-reachability: mode arguments absent: {helper} {mode}")
    if not field_is_anchored(row["boundary"], mode_owner.lower()):
        raise SystemExit(f"check-helper-reachability: mode boundary absent: {helper} {mode}")
    if row["caller"] != "-":
        caller_content = shell_code(packaged_path(row["caller"], helper, "mode caller").read_text(encoding="utf-8"))
        if not caller_invokes(helper, caller_content):
            raise SystemExit(f"check-helper-reachability: mode caller does not invoke {helper}: {row['caller']}")
        flags = r"\s+" + r"\s+".join(re.escape(flag) + r"\s+[^\s]+" for flag in mode.split())
        if not re.search(re.escape(helper) + r"[\"']?" + flags, caller_content):
            raise SystemExit(f"check-helper-reachability: mode caller does not invoke exact mode: {helper} {mode}")

role_python_payloads = {}
for role, payload in projection_payloads.items():
    canonical = {}
    for path, data in payload.items():
        if path.endswith(".py"):
            name = path if role == "canonical_plugin" else "skills/implementaudit/" + path
            canonical[name] = data
    role_python_payloads[role] = canonical
for role, overrides in role_rows.items():
    extra_roles = set(overrides) - set(rows)
    if extra_roles:
        raise SystemExit("check-helper-reachability: role row has no base member: " + ", ".join(sorted(extra_roles)))

def owner_record(raw, role, helper, label):
    base, marker, fragment = raw.partition("#")
    base = owner_aliases.get(base, base)
    path = PurePosixPath(base)
    if (not base or path.is_absolute() or ".." in path.parts or chr(92) in base
            or path.as_posix() != base):
        raise SystemExit(f"check-helper-reachability: invalid {label}: {helper}: {raw}")
    if base.startswith("skills/"):
        canonical = base
        if role == "canonical_plugin":
            member = canonical
        elif canonical.startswith("skills/implementaudit/"):
            member = canonical.removeprefix("skills/implementaudit/")
        else:
            parts = path.parts
            if len(parts) != 3 or parts[0] != "skills" or parts[2] != "SKILL.md" or parts[1] not in package["required_skills"]:
                raise SystemExit(f"check-helper-reachability: unsupported role owner: {raw}")
            member = f"internal-procedures/{parts[1]}.md"
    elif base == "hooks/hooks.json":
        canonical = member = base
    else:
        canonical = "skills/implementaudit/" + base
        member = projection_prefixes[role] + base
    if member not in projection_payloads[role]:
        raise SystemExit(f"check-helper-reachability: unshipped {label}: {helper}: {raw}: {role}")
    data = projection_payloads[role][member]
    try:
        content = data.decode("utf-8")
    except UnicodeError:
        raise SystemExit(f"check-helper-reachability: non-text {label}: {raw}")
    if fragment and canonical.endswith(".py"):
        try:
            tree=ast.parse(content,filename=canonical)
        except SyntaxError:
            raise SystemExit(f"check-helper-reachability: invalid Python {label} source: {raw}")
        selected=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
                  and node.name==fragment]
        if len(selected)!=1:
            raise SystemExit(f"check-helper-reachability: Python {label} function absent/ambiguous: {raw}")
    elif fragment:
        lines = content.splitlines()
        def slug(text):
            return re.sub(r"[^a-z0-9 -]", "", text.lower()).replace(" ", "-")
        candidates = [n for n,line in enumerate(lines)
                      if re.match(r"^#{1,6} ", line) and slug(line.lstrip("#").strip()) == fragment]
        if len(candidates) != 1:
            raise SystemExit(f"check-helper-reachability: owner section absent/ambiguous: {raw}")
        start=candidates[0];level=len(lines[start])-len(lines[start].lstrip("#"))
        end=next((n for n in range(start+1,len(lines)) if re.match(r"^#{1,"+str(level)+r"} ",lines[n])),len(lines))
        content="\n".join(lines[start:end])
    content="\n".join(line for line in content.splitlines()
                      if not line.startswith(("helper-route: ","helper-role: ","helper-mode: ")))
    return canonical,member,content,fragment

def explicit_command(helper, arguments, content):
    import shlex
    content=re.sub(r"\\\s*\n\s*", " ", content)
    if not arguments_are_anchored(arguments, helper, content):
        return False
    commands=re.findall(chr(96)+r"([^"+chr(96)+r"]*"+re.escape(helper)+r"[^"+chr(96)+r"]*)"+chr(96), content,re.S)
    commands.extend(line for line in content.splitlines() if helper in line)
    interpreter=r"(?:python3?|py\s+-3)" if helper.endswith(".py") else r"bash"
    for command in commands:
        for line in command.splitlines():
            if re.match(r"^\s*"+interpreter+r"\s+",line) and "scripts/"+helper in line:
                prefix=line.split("scripts/"+helper,1)[0]
                if helper.endswith(".py"):
                    try: words=shlex.split(line,comments=True)
                    except ValueError: continue
                    if not words or words[0] not in {"python","python3","py"}:continue
                    index=1
                    if words[0]=="py":
                        if words[1:2]!=["-3"]:continue
                        index=2
                    while index<len(words) and words[index] in {"-B","-I","-S"}:
                        index+=1
                    # Only the script operand establishes invocation. -c/-m,
                    # unknown options and earlier scripts cannot be skipped.
                    if index>=len(words) or words[index].startswith("-") or not (words[index]=="scripts/"+helper
                            or words[index].endswith("/scripts/"+helper)):
                        continue
                if not re.search(r"(?:;|&&|\|\||\$\()", prefix) and arguments_are_anchored(arguments, helper, line):
                    return True
    return False

def contexts_for(content, helper, fragment):
    if fragment:
        return [content]
    lines=content.splitlines()
    return ["\n".join(lines[max(0,index-4):index+5]) for index,line in enumerate(lines) if helper in line]

def hook_route(role, helper, event_spec):
    import shlex
    event, separator, matcher = event_spec.partition(":")
    if "hooks/hooks.json" not in projection_payloads[role]:
        return False
    try:
        hooks=json.loads(projection_payloads[role]["hooks/hooks.json"])["hooks"][event]
    except (KeyError,TypeError,ValueError):
        return False
    expected=projection_prefixes[role]+"scripts/"+helper
    seen=False
    for group in hooks:
        if (group.get("matcher","") != matcher):
            continue
        for hook in group.get("hooks",[]):
            if hook.get("type")!="command":
                continue
            commands=[hook.get("command"),hook.get("commandWindows")]
            if not all(isinstance(value,str) and value for value in commands):
                continue
            targets=[]
            for command in commands:
                dollar=chr(36)
                normalized=command.replace(dollar+"{env:PLUGIN_ROOT}","ROOT").replace(dollar+"{PLUGIN_ROOT}","ROOT").replace("%PLUGIN_ROOT%","ROOT").replace(chr(92),"/")
                try: words=shlex.split(normalized)
                except ValueError: words=[]
                if not words or not re.fullmatch(r"(?:.*/)?(?:python3?|py(?:\.exe)?)",words[0],re.I):
                    targets.append(False);continue
                while len(words)>1 and words[1] in {"-3","-I","-S","-B"}:
                    words.pop(1)
                targets.append(len(words)==2 and words[1]=="ROOT/"+expected)
            if any(targets) and not all(targets):
                return False
            seen = seen or all(targets)
    return seen

def shell_python_route(helper, mode, content):
    content=shell_code(content)
    escaped=re.escape(helper)
    commands=re.findall(r'(?m)^\s*"\$\{([A-Za-z_][A-Za-z0-9_]*)\[@\]\}"\s+"\$\(dirname "\$0"\)/'+escaped+r'"\s+([a-zA-Z0-9-]+)(?:\s|$)',content)
    for variable,observed in commands:
        assignments=re.findall(re.escape(variable)+r"=\(([^)]*)\)",content)
        if observed==mode and assignments and all(value in {"python","python3","py -3"} for value in assignments):
            return True
    return False

def validate_one(helper, row, role):
    if row["class"] not in class_names:
        raise SystemExit(f"check-helper-reachability: invalid applicability class {row['class']} for {helper}")
    applicability=class_names[row["class"]]
    for field in ("trigger","arguments","boundary"):
        if not row[field] or row[field]=="-":
            raise SystemExit(f"check-helper-reachability: empty {field} for {helper}")
    helper_canonical="skills/implementaudit/scripts/"+helper
    owner,owner_member,content,fragment=owner_record(row["owner"],role,helper,"dispatch owner")
    if owner==helper_canonical:
        raise SystemExit(f"check-helper-reachability: dispatch owner cannot be the helper itself: {helper}")
    contexts=contexts_for(content,helper,fragment)
    dormant=row["arguments"].startswith("dormant:")
    if dormant:
        if (role!="standalone_compatibility" or applicability!="internal-library"
                or row["caller"]!="hooks/hooks.json" or "hooks/hooks.json" in projection_payloads[role]
                or rows[helper]["class"]!="A"
                or rows[helper]["arguments"]!="hook:"+row["arguments"].removeprefix("dormant:")
                or not hook_route("canonical_plugin",helper,row["arguments"].removeprefix("dormant:"))
                or not any(all(word in context.lower() for word in
                    ("internal","dormant","standalone","canonical","shared","retained","no host activation"))
                    and helper in context for context in contexts)):
            raise SystemExit(f"check-helper-reachability: unproved dormant role: {helper}: {role}")
        return
    if applicability=="automatic" and row["arguments"].startswith("hook:"):
        if row["caller"]!="hooks/hooks.json" or owner!="hooks/hooks.json" or not hook_route(role,helper,row["arguments"].removeprefix("hook:")):
            raise SystemExit(f"check-helper-reachability: hook caller does not invoke exact member: {helper}: {role}")
        return
    if applicability in {"automatic","internal-library"}:
        if row["caller"]=="-":
            raise SystemExit(f"check-helper-reachability: {applicability} helper lacks caller: {helper}")
        caller,caller_member,caller_content,selector=owner_record(row["caller"],role,helper,"caller")
        if caller==helper_canonical:
            raise SystemExit(f"check-helper-reachability: helper cannot be its own caller: {helper}")
        if not caller.startswith("skills/implementaudit/scripts/"):
            raise SystemExit(f"check-helper-reachability: caller is not a shipped script: {helper}: {owner_aliases.get(row['caller'], row['caller'])}")
        if caller.endswith(".py"):
            engine=PythonEdges(role_python_payloads[role])
            loaded,apis,commands=engine.inspect(caller,selector)
            if row["arguments"].startswith("api:"):
                valid=(helper_canonical,row["arguments"].removeprefix("api:")) in apis and helper_canonical in loaded
            elif row["arguments"].startswith("cli:"):
                declared = tuple(row["arguments"].removeprefix("cli:").split())
                valid=(helper_canonical,declared) in commands
                callee = ast.parse(role_python_payloads[role][helper_canonical].decode("utf-8"))
                # A simple parser has one shared required-option population.
                # Do not mistake a first flag for the complete resolver call.
                calls = [node for node in ast.walk(callee) if isinstance(node,ast.Call)]
                if not any(isinstance(node.func,ast.Attribute) and node.func.attr=="add_subparsers" for node in calls):
                    required = {node.args[0].value for node in calls
                        if isinstance(node.func,ast.Attribute) and node.func.attr=="add_argument"
                        and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str)
                        and node.args[0].value.startswith("--") and any(
                            key.arg=="required" and isinstance(key.value,ast.Constant) and key.value.value is True
                            for key in node.keywords)}
                    valid = valid and required.issubset(declared)
            elif row["arguments"] in {"module","none"}:
                valid=helper_canonical in loaded
            else:
                valid=False
            if not valid:
                raise SystemExit(f"check-helper-reachability: Python caller edge unresolved: {helper}: {row['caller']}")
        elif caller.endswith(".sh"):
            if helper.endswith(".py"):
                valid=row["arguments"].startswith("cli:") and shell_python_route(helper,row["arguments"].removeprefix("cli:"),caller_content)
            else:
                valid=caller_invokes(helper,caller_content)
            if not valid:
                raise SystemExit(f"check-helper-reachability: caller does not invoke {helper}: {row['caller']}")
        else:
            raise SystemExit(f"check-helper-reachability: UNKNOWN_CALLER_TYPE: {row['caller']}")
        return
    if row["caller"]!="-":
        raise SystemExit(f"check-helper-reachability: nonautomatic helper declares caller: {helper}")
    if not contexts:
        raise SystemExit(f"check-helper-reachability: dispatch owner does not name helper {helper}: {row['owner']}")
    if applicability=="required-procedural":
        action=r"(?:bash|python3?|run|supply|dispatch(?:es)?|invoke|enforce|requires?|claim(?: it)? with)"
        procedural=[context for context in contexts if re.search(
            rf"(?:{action}.{{0,120}}{re.escape(helper)}|{re.escape(helper)}.{{0,120}}{action})",context,re.I|re.S)]
        if not procedural:
            raise SystemExit(f"check-helper-reachability: procedural route absent: {helper}")
        for field in ("trigger","boundary"):
            if not any(field_is_anchored(row[field], context.lower().replace("artefact","artifact").replace(helper.lower(),"")) for context in procedural):
                raise SystemExit(f"check-helper-reachability: unanchored {field}: {helper}: {row[field]}")
        if not any(arguments_are_anchored(row["arguments"],helper,context) for context in procedural):
            raise SystemExit(f"check-helper-reachability: unanchored arguments: {helper}: {row['arguments']}")
        if not any(field_is_anchored(row["trigger"],context.lower().replace("artefact","artifact").replace(helper.lower(),""))
                   and field_is_anchored(row["boundary"],context.lower().replace("artefact","artifact").replace(helper.lower(),""))
                   and arguments_are_anchored(row["arguments"],helper,context) for context in procedural):
            raise SystemExit(f"check-helper-reachability: route fields do not co-occur: {helper}")
        if helper.endswith(".py") and not any(explicit_command(helper,row["arguments"],context) for context in procedural):
            raise SystemExit(f"check-helper-reachability: Python procedural invocation absent: {helper}")
    elif applicability in {"optional-advisory","standalone-diagnostic"}:
        advisory=" ".join((row["trigger"],row["arguments"],row["boundary"]))
        if mandatory_re.search(advisory):
            raise SystemExit(f"check-helper-reachability: advisory/standalone row implies mandatory enforcement: {helper}")
        lines=content.splitlines()
        if any(mandatory_re.search(" ".join(lines[max(0,n-1):n+2])) for n,line in enumerate(lines) if helper in line):
            raise SystemExit(f"check-helper-reachability: advisory owner overclaim: {helper}")
        role_pattern=r"\boptional[- ]advisory\b" if applicability=="optional-advisory" else r"\bstandalone[- ]diagnostic\b"
        if not any(re.search(role_pattern,context,re.I) and explicit_command(helper,row["arguments"],context)
                   and field_is_anchored(row["boundary"],context.lower()) for context in contexts):
            raise SystemExit(f"check-helper-reachability: advisory/standalone role or exact invocation absent: {helper}")

for role in projection_prefixes:
    effective=dict(rows)
    effective.update(role_rows.get(role,{}))
    expected={projection_prefixes[role]+"scripts/"+helper for helper in effective}
    if expected!=projection_members[role]:
        raise SystemExit("check-helper-reachability: role classification set differs: "+role)
    for helper in helpers:
        validate_one(helper,effective[helper],role)



if not census_only:
    # The evaluated candidate supplies skills and fixtures, never the probe
    # program.  The checker invocation root is the authority for F10 behavior.
    r30_probe = authority_root / "tests" / "scarce-resource-rehearsal-contract.test.sh"
    if not r30_probe.is_file():
        raise SystemExit("check-helper-reachability: missing independently rooted R001E rehearsal probe")
    probe_args = [bash_runner, str(r30_probe), "--r30-probe", "--repo-root", str(root)]
    probe_kwargs = {"cwd": authority_root, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    probe_job = None
    if os.name == "nt":
        probe_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        probe_kwargs["start_new_session"] = True
    probe = subprocess.Popen(probe_args, **probe_kwargs)
    if os.name == "nt":
        probe_job = _KillOnCloseJob()
        probe_job.assign(probe)
    timed_out = False
    # The candidate's production rehearsal remains bounded to 10 seconds by
    # run_phase_with_timeout. This outer envelope also covers copying the
    # packaged skill population and verifier-owned setup/cleanup on slower hosts.
    outer_probe_timeout = 20
    try:
        probe_stdout, probe_stderr = probe.communicate(timeout=outer_probe_timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "nt":
            probe_job.close()
        else:
            try:
                os.killpg(probe.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if os.name != "nt":
            try: probe.kill()
            except ProcessLookupError: pass
        try:
            probe_stdout, probe_stderr = probe.communicate(timeout=2)
        except subprocess.TimeoutExpired as residual:
            # A killed direct child can still have a pipe-owning descendant.
            # Do not let that descendant defeat the outer cleanup deadline.
            probe_stdout = residual.output or b""
            probe_stderr = residual.stderr or b""
            if probe.stdout: probe.stdout.close()
            if probe.stderr: probe.stderr.close()
            try: probe.wait(timeout=2)
            except subprocess.TimeoutExpired: pass
    if probe_job:
        probe_job.close()
    diagnostic = probe_stderr.decode("utf-8", errors="replace")[-8192:]
    diagnostic = re.sub(r"(?im)^([A-Z_]*(?:TOKEN|SECRET|PASSWORD|API_KEY)[A-Z_]*=).*?$", r"\1<redacted>", diagnostic)
    if timed_out:
        raise SystemExit(
            "check-helper-reachability: candidate-bound R001E rehearsal probe "
            f"timed out after {outer_probe_timeout}s" +
                         ("\n" + diagnostic if diagnostic else ""))
    if probe.returncode != 0:
        raise SystemExit("check-helper-reachability: candidate-bound R001E rehearsal probe failed" +
                         ("\n" + diagnostic if diagnostic else ""))

print(("HELPER_REACHABILITY_CENSUS=PASS " if census_only else "HELPER_REACHABILITY=PASS ") +
      f"population={len(helpers)} examined={len(rows)} "
      f"modes={len(mode_rows)}/{sum(len(modes) for modes in implemented_mode_sets.values())} "
      "enumeration=package-contract.artifact_payload_entries full_path_sets=equal projections=2")
PY
