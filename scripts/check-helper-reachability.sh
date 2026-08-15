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
helpers = sorted(path.name for path in (skill_root / "scripts").glob("*.sh") if path.is_file())
if len(helpers) != len(set(helpers)):
    raise SystemExit("check-helper-reachability: duplicate helper in package shared root")

contract_text = contract.read_text(encoding="utf-8")
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
        helper = parts[0].removeprefix("helper-route: ")
        if helper in rows:
            raise SystemExit(f"check-helper-reachability: duplicate applicability row: {helper}")
        rows[helper] = {"class": parts[1], "trigger": parts[2], "owner": parts[3],
                        "caller": parts[4], "arguments": parts[5], "boundary": parts[6]}

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
                      if helper in line and "`" not in line and re.match(r"\s*(?:bash|source|exec)\b", line, re.I))
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

implemented_mode_sets = {}
graph_helper = "validate-run-root.sh"
graph_text = (skill_root / "scripts" / graph_helper).read_text(encoding="utf-8")
implemented_mode_sets[graph_helper] = sorted(set(re.findall(r"--graph-[a-z0-9-]+", graph_text)))
rehearsal_helper, rehearsal_mode = "check-authorization-binding.sh", "--phase --rehearsal --launch"
# R32: static census records the declared mode; candidate-bound F10 below is
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
        caller_content = shell_code(packaged_path(row["caller"], helper, "mode caller").read_text(encoding="utf-8"))
        if not caller_invokes(helper, caller_content):
            raise SystemExit(f"check-helper-reachability: mode caller does not invoke {helper}: {row['caller']}")
        flags = r"\s+" + r"\s+".join(re.escape(flag) + r"\s+[^\s]+" for flag in mode.split())
        if not re.search(re.escape(helper) + r"[\"']?" + flags, caller_content):
            raise SystemExit(f"check-helper-reachability: mode caller does not invoke exact mode: {helper} {mode}")

for helper in helpers:
    row = rows[helper]
    if row["class"] not in class_names:
        raise SystemExit(f"check-helper-reachability: invalid applicability class {row['class']} for {helper}")
    applicability = class_names[row["class"]]
    for field in ("trigger", "arguments", "boundary"):
        if not row[field] or row[field] == "-":
            raise SystemExit(f"check-helper-reachability: empty {field} for {helper}")
    owner_text = owner_aliases.get(row["owner"], row["owner"])
    if Path(owner_text) == Path("scripts") / helper:
        raise SystemExit(f"check-helper-reachability: dispatch owner cannot be the helper itself: {helper}")
    owner_lines = packaged_path(owner_text, helper, "dispatch owner").read_text(encoding="utf-8").splitlines()
    non_route_lines = [line for line in owner_lines if not line.startswith(("helper-route: ", "helper-mode: "))]
    owner_content = "\n".join(non_route_lines)
    helper_lines = [index for index, line in enumerate(non_route_lines) if helper in line]
    if not helper_lines:
        raise SystemExit(f"check-helper-reachability: dispatch owner does not name helper {helper}: {owner_text}")
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
    if applicability in {"optional-advisory", "standalone-diagnostic"}:
        advisory = " ".join((row["trigger"], row["arguments"], row["boundary"]))
        if mandatory_re.search(advisory):
            raise SystemExit(f"check-helper-reachability: advisory/standalone row implies mandatory enforcement: {helper}")
        if any(mandatory_re.search(" ".join(non_route_lines[max(0, i - 1):i + 2])) for i in helper_lines):
            raise SystemExit(f"check-helper-reachability: advisory owner overclaim: {helper}")
    caller_rel = owner_aliases.get(row["caller"], row["caller"])
    if applicability in {"automatic", "internal-library"}:
        if caller_rel == "-":
            raise SystemExit(f"check-helper-reachability: {applicability} helper lacks caller: {helper}")
        caller_path = packaged_path(caller_rel, helper, "caller")
        if not (Path(caller_rel).as_posix().startswith("scripts/") and Path(caller_rel).suffix == ".sh"):
            raise SystemExit(f"check-helper-reachability: caller is not a shipped script: {helper}: {caller_rel}")
        if not caller_invokes(helper, caller_path.read_text(encoding="utf-8")):
            raise SystemExit(f"check-helper-reachability: caller does not invoke {helper}: {caller_rel}")
    elif caller_rel != "-":
        raise SystemExit(f"check-helper-reachability: nonautomatic helper declares caller: {helper}")

if not census_only:
    # The evaluated candidate supplies skills and fixtures, never the probe
    # program.  The checker invocation root is the authority for F10 behavior.
    r30_probe = authority_root / "tests" / "scarce-resource-rehearsal-contract.test.sh"
    if not r30_probe.is_file():
        raise SystemExit("check-helper-reachability: missing independently rooted R30 rehearsal probe")
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
            "check-helper-reachability: candidate-bound R30 rehearsal probe "
            f"timed out after {outer_probe_timeout}s" +
                         ("\n" + diagnostic if diagnostic else ""))
    if probe.returncode != 0:
        raise SystemExit("check-helper-reachability: candidate-bound R30 rehearsal probe failed" +
                         ("\n" + diagnostic if diagnostic else ""))

print(("HELPER_REACHABILITY_CENSUS=PASS " if census_only else "HELPER_REACHABILITY=PASS ") +
      f"population={len(helpers)} examined={len(rows)} "
      f"modes={len(mode_rows)}/{sum(len(modes) for modes in implemented_mode_sets.values())} "
      "enumeration=package-contract.shared_resource_roots")
PY
