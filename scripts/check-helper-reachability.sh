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
import ast
import json
import hashlib
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
from pathlib import Path
from pathlib import PurePosixPath

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

# The invocation checkout is the selected evaluator authority; --repo-root is
# data only. A package-owner change needs a newly reviewed committed authority.
# Capture once, authenticate against that fixed source blob, execute that buffer.
trusted_builder = authority_root / "scripts" / "package-contract.py"
try:
    authority_commit = subprocess.check_output(
        ["git", "-C", str(authority_root), "rev-parse", "HEAD"], text=True).strip()
    owner_object = authority_commit + ":scripts/package-contract.py"
    owner_blob = subprocess.check_output(
        ["git", "-C", str(authority_root), "rev-parse", owner_object], text=True).strip()
    expected_builder = subprocess.check_output(
        ["git", "-C", str(authority_root), "cat-file", "blob", owner_blob])
    builder_buffer = trusted_builder.read_bytes()
    if builder_buffer != expected_builder:
        raise SystemExit("check-helper-reachability: selected package owner is not its committed authority")
    if builder.read_bytes() != builder_buffer:
        raise SystemExit("check-helper-reachability: package owner differs from selected checker owner")
except (OSError, subprocess.SubprocessError) as exc:
    raise SystemExit(f"check-helper-reachability: package owner authority unavailable: {exc}") from exc
package_owner = types.ModuleType("_helper_census_package_owner")
package_owner.__file__ = str(trusted_builder)
exec(compile(builder_buffer, str(trusted_builder), "exec"), package_owner.__dict__)
try:
    package = package_owner.validate_contract(root)
except (OSError, ValueError) as exc:
    raise SystemExit(f"check-helper-reachability: package contract is invalid: {exc}") from exc

# Membership comes only from each builder projection's executable metadata.
# Invocation types are checked AFTER membership; unknown executables stay in it.
projection_prefixes = {"canonical_plugin": "skills/implementaudit/",
                       "standalone_compatibility": ""}
projection_members, projection_payloads, projection_entries = {}, {}, {}
for role, prefix in projection_prefixes.items():
    try:
        entries = package_owner.artifact_payload_entries(root, role, package)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"check-helper-reachability: package population unavailable: {role}: {exc}") from exc
    names = [path for path, _data, _mode in entries]
    if len(names) != len(set(names)):
        raise SystemExit(f"check-helper-reachability: duplicate package member: {role}")
    projection_entries[role] = entries
    projection_payloads[role] = {path: data for path, data, _mode in entries}
    projection_members[role] = {path for path, _data, mode in entries
                                if path.startswith(prefix + "scripts/") and mode & 0o111}
canonical_relative = {path.removeprefix("skills/implementaudit/")
                      for path in projection_members["canonical_plugin"]}
if canonical_relative != projection_members["standalone_compatibility"]:
    raise SystemExit("check-helper-reachability: executable projection parity differs")
archive_entries = set(projection_payloads["standalone_compatibility"])
helpers = sorted(path.removeprefix("scripts/") for path in canonical_relative)
for helper in helpers:
    if PurePosixPath(helper).suffix not in {".sh", ".py"}:
        raise SystemExit(f"check-helper-reachability: UNKNOWN_EXECUTABLE_TYPE: scripts/{helper}")

def read_rows(contract_text):
  rows, mode_rows = {}, {}
  for line_number, line in enumerate(contract_text.splitlines(), 1):
    if line.startswith("helper-mode: "):
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
        if (not member.startswith("scripts/") or member == "scripts/"
                or chr(92) in member or ".." in PurePosixPath(member).parts
                or PurePosixPath(member).as_posix() != member):
            raise SystemExit(f"check-helper-reachability: route is not a full package member path: {member}")
        helper = member.removeprefix("scripts/")
        if helper in rows:
            raise SystemExit(f"check-helper-reachability: duplicate applicability row: {helper}")
        rows[helper] = {"class": parts[1], "trigger": parts[2], "owner": parts[3],
                        "caller": parts[4], "arguments": parts[5], "boundary": parts[6]}
    elif line.startswith("helper-role: "):
        raise SystemExit("check-helper-reachability: unowned projection-specific classification")
  return rows, mode_rows

projected_rows = {}
for role, prefix in projection_prefixes.items():
    text = projection_payloads[role][prefix + "references/repo-state-comparison.md"].decode("utf-8")
    projected_rows[role] = read_rows(text)
if projected_rows["canonical_plugin"] != projected_rows["standalone_compatibility"]:
    raise SystemExit("check-helper-reachability: classification projection parity differs")
rows, mode_rows = projected_rows["canonical_plugin"]
contract_text = projection_payloads["standalone_compatibility"]["references/repo-state-comparison.md"].decode("utf-8")

missing, extra = sorted(set(helpers) - set(rows)), sorted(set(rows) - set(helpers))
if missing:
    suffix = f" (population={len(helpers)} examined={len(rows)})" if len(helpers) != len(rows) else ""
    raise SystemExit("check-helper-reachability: missing applicability rows: " + ", ".join(missing) + suffix)
if extra:
    raise SystemExit("check-helper-reachability: applicability rows not in package: " + ", ".join(extra))
for role, prefix in projection_prefixes.items():
    if {prefix + "scripts/" + helper for helper in projected_rows[role][0]} != projection_members[role]:
        raise SystemExit("check-helper-reachability: full-path classification set differs: " + role)

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

def python_command(helper, arguments, content):
    """Typed source command, not a substring inside echo, -c, -m or a comment."""
    expected = [] if arguments == "none" else shlex.split(arguments)
    commands = re.findall(r"(?<!`)`(?!`)([^`]+)(?<!`)`(?!`)", content, re.S)
    commands.extend(line for line in content.splitlines() if "`" not in line)
    for command in commands:
        try:
            words = shlex.split(re.sub(r"\\\s*\n\s*", " ", command), comments=True)
        except ValueError:
            continue
        if not words or words[0] not in {"python", "python3", "py"}:
            continue
        index = 1
        if words[0] == "py":
            if words[1:2] != ["-3"]:
                continue
            index = 2
        options = []
        while index < len(words) and words[index] in {"-I", "-S", "-B"}:
            options.append(words[index]); index += 1
        if index >= len(words):
            continue
        operand = words[index]
        member = "scripts/" + helper
        if operand in {member, "<skill-dir>/" + member} and words[index + 1:] == expected:
            return options, operand, words[index + 1:], member
    return None

def selected_owner(raw, helper, role):
    base, _mark, fragment = raw.partition("#")
    base = owner_aliases.get(base, base)
    packaged_path(base, helper, role)
    canonical = projection_payloads["canonical_plugin"]["skills/implementaudit/" + base]
    standalone = projection_payloads["standalone_compatibility"][base]
    if canonical != standalone:
        raise SystemExit(f"check-helper-reachability: route owner projection parity differs: {base}")
    content = canonical.decode("utf-8")
    if fragment:
        lines = content.splitlines()
        def slug(line):
            return re.sub(r"[^a-z0-9 -]", "", line.lstrip("#").strip().lower()).replace(" ", "-")
        starts = [n for n, line in enumerate(lines) if re.match(r"^#{1,6} ", line) and slug(line) == fragment]
        if len(starts) != 1:
            raise SystemExit(f"check-helper-reachability: owner section absent/ambiguous: {raw}")
        start = starts[0]
        level = len(lines[start]) - len(lines[start].lstrip("#"))
        end = next((n for n in range(start + 1, len(lines)) if re.match(r"^#{1," + str(level) + r"} ", lines[n])), len(lines))
        content = "\n".join(lines[start:end])
    return base, content

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

def python_array_invokes(helper, content):
    # Recognize an actual selected-Python command, never a comment, echo or -c.
    arrays = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)=\((?:python3?|py(?: -3)?)(?: -[BIS])*\)", content))
    aliases = set()
    for line in content.splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)=\".*?/" + re.escape(helper) + r"\"\s*$", line)
        if match:
            aliases.add(match.group(1))
    for line in content.splitlines():
        match = re.match(r'^\s*(?:PYTHONDONTWRITEBYTECODE=1\s+)?"\$\{([A-Za-z_][A-Za-z0-9_]*)\[@\]\}"\s+(?:-[BIS]\s+)*(.+)$', line)
        if not match or match.group(1) not in arrays:
            continue
        operands = ['"$' + alias + '"' for alias in aliases]
        operands += ['"$(dirname "$0")/' + helper + '"']
        if any(match.group(2) == operand or match.group(2).startswith(operand + " ") for operand in operands):
            return True
    return False


def captured_python_library(helper, content):
    # A package library must be loaded from the physical sibling and executed
    # from the captured buffer. Merely mentioning a filename is not a route.
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False
    constants = {target.id: node.value.value for node in tree.body if isinstance(node, ast.Assign)
                 and isinstance(node.value, ast.Constant) for target in node.targets if isinstance(target, ast.Name)}
    for function in (node for node in tree.body if isinstance(node, ast.FunctionDef)):
        nodes = list(ast.walk(function))
        calls = [node for node in nodes if isinstance(node, ast.Call)]
        if not any(isinstance(node, ast.Constant) and node.value == helper for node in nodes):
            continue
        if not any(isinstance(node, ast.Name) and node.id == "__file__" for node in nodes):
            continue
        captured = set()
        for node in nodes:
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if ((isinstance(call.func, ast.Name) and call.func.id == "read_regular")
                    or (isinstance(call.func, ast.Attribute) and call.func.attr == "read")):
                captured.update(target.id for target in node.targets if isinstance(target, ast.Name))
                # read_regular returns captured bytes followed by file metadata.
                # Only its first tuple target can supply the executed buffer.
                if isinstance(call.func, ast.Name) and call.func.id == "read_regular":
                    captured.update(target.elts[0].id for target in node.targets
                                    if isinstance(target, ast.Tuple) and len(target.elts) == 2
                                    and all(isinstance(value, ast.Name) for value in target.elts)
                                    and target.elts[0].id != target.elts[1].id)
        executed = any(isinstance(call.func, ast.Name) and call.func.id == "exec" and call.args
                       and isinstance(call.args[0], ast.Call) and isinstance(call.args[0].func, ast.Name)
                       and call.args[0].func.id == "compile" and len(call.args[0].args) == 3
                       and isinstance(call.args[0].args[0], ast.Name) and call.args[0].args[0].id in captured
                       and isinstance(call.args[0].args[2], ast.Constant) and call.args[0].args[2].value == "exec"
                       for call in calls)
        invoked = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                      and node.func.id == function.name and not function.lineno <= node.lineno <= function.end_lineno
                      for node in ast.walk(tree))
        sibling = any(isinstance(call.func, ast.Attribute) and call.func.attr in {"with_name", "join"}
                      and any(isinstance(arg, ast.Constant) and arg.value == helper for arg in call.args)
                      for call in calls)
        if not (captured and executed and invoked and sibling):
            continue
        if helper == "canonical_hot_projection.py":
            raw = projection_payloads["standalone_compatibility"]["scripts/" + helper]
            if (constants.get("_HOT_PROJECTION_MODULE_BYTES") != len(raw)
                    or constants.get("_HOT_PROJECTION_MODULE_SHA256") != hashlib.sha256(raw).hexdigest()):
                return False
            guards = [node for node in nodes if isinstance(node, ast.If)
                      and any(isinstance(child, ast.Raise) for child in node.body)]
            if not any(all(token in ast.unparse(guard.test) for token in
                           ("len(_source)", "_HOT_PROJECTION_MODULE_BYTES", "sha256(_source)", "_HOT_PROJECTION_MODULE_SHA256"))
                       for guard in guards):
                return False
        if helper == "canonical_rotation_inputs.py":
            raw = projection_payloads["standalone_compatibility"]["scripts/" + helper]
            if (constants.get("NATIVE_INPUT_MODULE_BYTES") != len(raw)
                    or constants.get("NATIVE_INPUT_MODULE_SHA256") != hashlib.sha256(raw).hexdigest()):
                return False
            guards = [node for node in nodes if isinstance(node, ast.If)
                      and any(isinstance(child, ast.Raise) for child in node.body)]
            if not any(all(token in ast.unparse(guard.test) for token in
                           ("len(raw)", "NATIVE_INPUT_MODULE_BYTES", "sha256(raw)", "NATIVE_INPUT_MODULE_SHA256"))
                       for guard in guards):
                return False
        return True
    return False

def caller_invokes(helper, content):
    content = shell_code(content)
    if python_array_invokes(helper, content):
        return True
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

def claim_public_modes(content):
    dispatch = re.search(r'^case "\$\{1:-\}" in\n(.*?)^esac$', content, re.M | re.S)
    if dispatch is None:
        raise SystemExit("check-helper-reachability: claim public dispatch is unavailable")
    labels = re.findall(r"^  ([^\n ]+)\)", dispatch.group(1), re.M)
    if not labels or any(not re.fullmatch(r"--[a-z0-9-]+(?:\|--[a-z0-9-]+)*", label) for label in labels):
        raise SystemExit("check-helper-reachability: unknown claim public dispatch shape")
    # --controller is the claim constructor already covered by its required
    # procedural route. Every distinct native operation has an exact mode row.
    return sorted({mode for label in labels for mode in label.split("|")} - {"--controller"})


implemented_mode_sets = {}
implemented_mode_sets["claim-run.sh"] = claim_public_modes((skill_root / "scripts/claim-run.sh").read_text(encoding="utf-8"))
graph_helper = "validate-run-root.sh"
graph_text = (skill_root / "scripts" / graph_helper).read_text(encoding="utf-8")
implemented_mode_sets[graph_helper] = sorted(set(re.findall(r"--graph-[a-z0-9-]+", graph_text)))
# The additive record mode is dispatched by the ordinary argument parser,
# outside the graph case. Require that actual parser branch, not a prose token.
if re.search(r'^elif \[ "\$\{1:-\}" = "--nonterminal-yield" \]; then$', graph_text, re.M):
    implemented_mode_sets[graph_helper].append("--nonterminal-yield")
if re.search(r'^if \[ "\$\{1:-\}" = "--turn-disposition" \]; then$', graph_text, re.M):
    implemented_mode_sets[graph_helper].append("--turn-disposition")

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
                       if not line.startswith(("helper-route: ", "helper-mode: ")))
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
        caller_content = shell_code(selected_owner(row["caller"], helper, "mode caller")[1])
        if not caller_invokes(helper, caller_content):
            raise SystemExit(f"check-helper-reachability: mode caller does not invoke {helper}: {row['caller']}")
        flags = r"\s+" + r"\s+".join(re.escape(flag) + r"\s+[^\s]+" for flag in mode.split())
        if not re.search(re.escape(helper) + r"[\"']?" + flags, caller_content):
            raise SystemExit(f"check-helper-reachability: mode caller does not invoke exact mode: {helper} {mode}")

governor_command = None
diagnostic_command = None
for helper in helpers:
    row = rows[helper]
    if row["class"] not in class_names:
        raise SystemExit(f"check-helper-reachability: invalid applicability class {row['class']} for {helper}")
    applicability = class_names[row["class"]]
    for field in ("trigger", "arguments", "boundary"):
        if not row[field] or row[field] == "-":
            raise SystemExit(f"check-helper-reachability: empty {field} for {helper}")
    owner_text, owner_source = selected_owner(row["owner"], helper, "dispatch owner")
    if Path(owner_text) == Path("scripts") / helper:
        raise SystemExit(f"check-helper-reachability: dispatch owner cannot be the helper itself: {helper}")
    owner_lines = owner_source.splitlines()
    non_route_lines = [line for line in owner_lines if not line.startswith(("helper-route: ", "helper-mode: "))]
    owner_content = "\n".join(non_route_lines)
    helper_lines = [index for index, line in enumerate(non_route_lines) if helper in line]
    if not helper_lines:
        raise SystemExit(f"check-helper-reachability: dispatch owner does not name helper {helper}: {owner_text}")
    if helper == "resolve-internal-skill.py" and applicability == "internal-library":
        expected_owner = "S#governor-routed-internal-cognition"
        expected_arguments = "--governor SKILL.md --child <child>"
        command = python_command(helper, row["arguments"], owner_content)
        if (row["owner"] != expected_owner or row["caller"] != expected_owner
                or row["arguments"] != expected_arguments or command is None
                or row["trigger"] != "child-resolution" or row["boundary"] != "no-load-credit"
                or not all(token in owner_content for token in
                    ("Before loading one child", "The resolver refuses missing/extra children",
                     "governor re-derives current state", "source/canonical layouts load"))):
            raise SystemExit("check-helper-reachability: governor resolver command/trigger/consequence absent")
        governor_command = command
        continue
    if applicability == "required-procedural":
        action = r"(?:bash|run|supply|dispatch(?:es)?|invoke|enforce|requires?|claim(?: it)? with)"
        contexts = ["\n".join(non_route_lines[max(0, i - 4):i + 5]) for i in helper_lines]
        procedural = [context for context in contexts if re.search(
            rf"(?:{action}.{{0,120}}{re.escape(helper)}|{re.escape(helper)}.{{0,120}}{action})", context, re.I | re.S)]
        if not procedural:
            raise SystemExit(f"check-helper-reachability: procedural route absent: {helper}")
        field_contexts = [context.lower().replace("artefact", "artifact").replace(helper.lower(), "") for context in procedural]
        for field in ("trigger", "boundary"):
            if not any(field_is_anchored(row[field], context) for context in field_contexts):
                raise SystemExit(f"check-helper-reachability: unanchored {field}: {helper}: {row[field]}")
        if not any(arguments_are_anchored(row["arguments"], helper, context) for context in procedural):
            raise SystemExit(f"check-helper-reachability: unanchored arguments: {helper}: {row['arguments']}")
        if not any(field_is_anchored(row["trigger"], context.lower().replace("artefact", "artifact").replace(helper.lower(), ""))
                   and field_is_anchored(row["boundary"], context.lower().replace("artefact", "artifact").replace(helper.lower(), ""))
                   and arguments_are_anchored(row["arguments"], helper, context) for context in procedural):
            raise SystemExit(f"check-helper-reachability: route fields do not co-occur: {helper}")
        if helper.endswith(".py") and not any(
                python_command(helper, row["arguments"], context) is not None
                and all(field_is_anchored(row[field], context.lower().replace(helper.lower(), ""))
                        for field in ("trigger", "boundary")) for context in procedural):
            raise SystemExit(f"check-helper-reachability: Python procedural invocation absent: {helper}")
    if applicability in {"optional-advisory", "standalone-diagnostic"}:
        advisory = " ".join((row["trigger"], row["arguments"], row["boundary"]))
        if mandatory_re.search(advisory):
            raise SystemExit(f"check-helper-reachability: advisory/standalone row implies mandatory enforcement: {helper}")
        if any(mandatory_re.search(" ".join(non_route_lines[max(0, i - 1):i + 2])) for i in helper_lines):
            raise SystemExit(f"check-helper-reachability: advisory owner overclaim: {helper}")
        if helper.endswith(".py"):
            contexts = ["\n".join(non_route_lines[max(0, i - 4):i + 5]) for i in helper_lines]
            commands = [python_command(helper, row["arguments"], context) for context in contexts
                        if applicability in context and field_is_anchored(row["boundary"], context.lower())]
            command = next((value for value in commands if value is not None), None)
            if command is None:
                raise SystemExit(f"check-helper-reachability: advisory/standalone role or exact invocation absent: {helper}")
            if helper == "resolve-durable-identity.py":
                if (row["arguments"] != "--canonical <identity>" or row["boundary"] != "no-allocation"
                        or "no allocation" not in owner_content.lower()):
                    raise SystemExit("check-helper-reachability: advisory/standalone durable boundary absent")
                diagnostic_command = command
    caller_rel = owner_aliases.get(row["caller"], row["caller"])
    if applicability in {"automatic", "internal-library"}:
        if caller_rel == "-":
            raise SystemExit(f"check-helper-reachability: {applicability} helper lacks caller: {helper}")
        caller_path = packaged_path(caller_rel, helper, "caller")
        if not Path(caller_rel).as_posix().startswith("scripts/"):
            raise SystemExit(f"check-helper-reachability: caller is not a shipped script: {helper}: {caller_rel}")
        caller_source = selected_owner(row["caller"], helper, "caller")[1]
        if applicability == "internal-library" and Path(caller_rel).suffix == ".py":
            if not captured_python_library(helper, caller_source):
                raise SystemExit(f"check-helper-reachability: caller does not capture/load {helper}: {caller_rel}")
        elif Path(caller_rel).suffix != ".sh" or not caller_invokes(helper, caller_source):
            raise SystemExit(f"check-helper-reachability: caller does not invoke {helper}: {caller_rel}")
    elif caller_rel != "-":
        raise SystemExit(f"check-helper-reachability: nonautomatic helper declares caller: {helper}")

if not census_only:
    # These bounded source probes execute the documented Python commands from
    # the actual projected owner. They do not claim an installed agent event,
    # child LOAD/USE, native admission, or that Markdown dispatches itself.
    if governor_command is None or diagnostic_command is None:
        raise SystemExit("check-helper-reachability: Python route probe lacks supported owner commands")
    def run_python(command, governor_dir, values, expected_success, expected_output=None):
        options, operand, arguments, member = command
        substitutions = {"<skill-dir>": str(governor_dir), **values}
        def bind(value):
            for key, replacement in substitutions.items():
                value = value.replace(key, replacement)
            return value
        expected_member = (governor_dir / member).absolute()
        declared_member = Path(bind(operand))
        if not declared_member.is_absolute():
            declared_member = governor_dir / declared_member
        try:
            # Bind the accepted source operand to this staged member, not an
            # external path that happens to end in the same scripts/name.
            if (expected_member.resolve(strict=True) != expected_member
                    or declared_member.resolve(strict=True) != expected_member
                    or not expected_member.is_file()):
                raise ValueError("operand does not identify the staged member")
        except (OSError, ValueError) as exc:
            raise SystemExit("check-helper-reachability: Python route probe member identity differs: " + member) from exc
        argv = [sys.executable, *options, str(expected_member), *map(bind, arguments)]
        # A timeout on only the direct process can leave a child alive (and
        # holding the staged directory or pipes). Use the existing process-family
        # boundary, bounded stream buffers, and retain refusal diagnostics.
        job = _KillOnCloseJob() if os.name == "nt" else None
        kwargs = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if job else {"start_new_session": True}
        process = None
        streams, readers = {}, []
        overflow = threading.Event()
        timed_out = False
        try:
            process = subprocess.Popen(argv, cwd=governor_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       bufsize=0, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, **kwargs)
            if job:
                job.assign(process)
            def drain(pipe, key):
                buffer = streams[key]
                while True:
                    chunk = pipe.read(4096)
                    if not chunk:
                        return
                    available = 65536 - len(buffer)
                    buffer.extend(chunk[:available])
                    if len(chunk) > available:
                        overflow.set()
                        return
            for key, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
                streams[key] = bytearray()
                reader = threading.Thread(target=drain, args=(pipe, key), daemon=True)
                reader.start(); readers.append(reader)
            deadline = time.monotonic() + 10
            while process.poll() is None and not overflow.wait(.02):
                if time.monotonic() >= deadline:
                    timed_out = True
                    break
        except (OSError, subprocess.SubprocessError) as exc:
            raise SystemExit(f"check-helper-reachability: Python route probe failed: {exc}") from exc
        finally:
            if job:
                job.close()
            elif process is not None:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=2)
                for reader in readers:
                    reader.join(timeout=2)
                process.stdout.close(); process.stderr.close()
        stdout = bytes(streams.get("stdout", b"")).decode("utf-8", errors="replace")
        stderr = bytes(streams.get("stderr", b"")).decode("utf-8", errors="replace")
        diagnostic = (stderr or stdout)[-2048:]
        diagnostic = re.sub(r"(?im)^([A-Z_]*(?:TOKEN|SECRET|PASSWORD|API_KEY)[A-Z_]*=).*?$", r"\1<redacted>", diagnostic)
        if timed_out or overflow.is_set() or any(reader.is_alive() for reader in readers):
            reason = "timed out after 10s" if timed_out else ("output limit exceeded" if overflow.is_set() else "stream cleanup incomplete")
            raise SystemExit("check-helper-reachability: Python route probe " + reason + "\n" + diagnostic)
        if ((process.returncode == 0) != expected_success
                or (expected_output is not None and stdout.strip() != expected_output)):
            raise SystemExit("check-helper-reachability: Python route probe result/refusal differs: " +
                             Path(operand).name + "\n" + diagnostic)
    with tempfile.TemporaryDirectory(prefix="r001e-python-routes-") as temporary:
        for role, prefix in projection_prefixes.items():
            projected = Path(temporary) / role
            # Both supported layouts keep the governor directory identity.
            projected = projected / ("plugin" if prefix else "implementaudit")
            for member, data, _mode in projection_entries[role]:
                target = projected / member
                if not target.resolve().is_relative_to(projected.resolve()):
                    raise SystemExit("check-helper-reachability: Python route probe path escapes projection")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            governor_dir = projected / prefix
            for child in package["required_skills"][1:]:
                child_path = (projected / "skills" / child / "SKILL.md" if prefix else
                              governor_dir / "internal-procedures" / (child + ".md"))
                run_python(governor_command, governor_dir, {"<child>": child}, True, str(child_path.resolve()))
            child_path.unlink()  # fixture-only missing-child boundary
            run_python(governor_command, governor_dir, {"<child>": child}, False)
            run_python(diagnostic_command, governor_dir, {"<identity>": "R30"}, True, "R001E")  # legacy alias control
            run_python(diagnostic_command, governor_dir, {"<identity>": "not-an-identity"}, False)
            # Allocation assertions are separate documented diagnostic inputs.
            allocation = python_command("resolve-durable-identity.py", "--require-allocated <identity>",
                                        selected_owner(rows["resolve-durable-identity.py"]["owner"],
                                                       "resolve-durable-identity.py", "dispatch owner")[1])
            if allocation is None:
                raise SystemExit("check-helper-reachability: Python route probe lacks allocation diagnostic")
            for identity in ("R0038", "R0039", "R003A"):
                run_python(allocation, governor_dir, {"<identity>": identity}, True, identity)
            for identity in ("R003B", "G0001"):  # unallocated/run-local refusal controls
                run_python(allocation, governor_dir, {"<identity>": identity}, False)
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
      "enumeration=package-contract.artifact_payload_entries full_path_sets=equal projections=2 " +
      f"owner_commit={authority_commit} owner_blob={owner_blob} " +
      f"owner_sha256={hashlib.sha256(builder_buffer).hexdigest()}")
PY
