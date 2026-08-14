#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-dogfood-bootstrap-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skill_file="skills/implementaudit/SKILL.md"
audit_file=""
transcript_file="fixtures/dogfood-bootstrap/positive/baseline-first-transcript.jsonl"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skill-file)
      [ "$#" -ge 2 ] || fail "--skill-file requires a path"
      skill_file="$2"
      shift 2
      ;;
    --audit-file)
      [ "$#" -ge 2 ] || fail "--audit-file requires a path"
      audit_file="$2"
      shift 2
      ;;
    --transcript-file)
      [ "$#" -ge 2 ] || fail "--transcript-file requires a path"
      transcript_file="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$skill_file" "$audit_file" "$transcript_file" <<'PY'
import json
import re
import shlex
import sys
from pathlib import Path

skill_path = Path(sys.argv[1])
audit_path = Path(sys.argv[2])
transcript_path = Path(sys.argv[3])

if not skill_path.is_file():
    raise SystemExit(f"missing skill file: {skill_path}")
if str(audit_path) != "." and not audit_path.is_file():
    raise SystemExit(f"missing audit file: {audit_path}")
if not transcript_path.is_file():
    raise SystemExit(f"missing transcript fixture: {transcript_path}")

skill = skill_path.read_text(encoding="utf-8")
audit = audit_path.read_text(encoding="utf-8") if str(audit_path) != "." else ""
transcript = transcript_path.read_text(encoding="utf-8")

heading = "## Dogfood Bootstrap / Read Map"
if heading not in skill:
    raise SystemExit(f"{skill_path}: missing {heading}")

line_no = skill[: skill.index(heading)].count("\n") + 1
if line_no > 40:
    raise SystemExit(f"{skill_path}: dogfood bootstrap must appear before line 40")

required_skill_tokens = [
    "First executable dogfood rule: Before any model tool reads the installed",
    "skill/payload, the runner records target status and identity",
    "Host activation",
    "model-visible dogfood readback",
    "Before runner baseline, no model tool reads or chunks this entire installed",
    "host activation is not readback",
    "After baseline",
    "progressive disclosure",
    "owner/source sections",
    "`rg`/grep for live owner/source files",
    "Package proof uses deterministic checks",
    "not model-visible full-file",
    "Full installed-payload readback is non-evidence",
    "### Dogfood Runner Contract",
    "Baseline/read-only checks first",
    "Repo-local validation after the read map is satisfied",
    "`--ask-for-approval never` is valid only when every required command is already",
    "`--ask-for-approval on-request` with `--sandbox workspace-write`",
    "Do not use `--dangerously-bypass-approvals-and-sandbox`",
    "Real-home installed skill readback is non-evidence",
    "temp `CODEX_HOME`",
    "installed skill path under that temp home",
    "installed `SKILL.md` line/byte count",
    "exact command proving Codex used that temp home",
    "stale-installed-skill /",
    "real-home-contamination",
]
for token in required_skill_tokens:
    if token not in skill:
        raise SystemExit(f"{skill_path}: missing dogfood bootstrap token: {token}")

if audit:
    for token in [
        "temp",
        "Dogfood",
        "baseline",
    ]:
        if token not in audit:
            raise SystemExit(f"{audit_path}: missing optional dogfood token: {token}")

builder = Path("scripts/build-release-asset.sh").read_text(encoding="utf-8")
for token in ['"skills/implementaudit/SKILL.md"', '"SKILL.md"']:
    if token not in builder:
        raise SystemExit(f"scripts/build-release-asset.sh: missing archive token: {token}")

baseline_tokens = [
    "git status --short --branch --untracked-files=all",
    "git rev-parse HEAD",
]
readback_narrative_tokens = [
    "installed skill is long, chunking remaining readback before baseline",
    "The installed skill file is long and the first read was truncated by the tool display",
]
readback_narrative_tokens_casefold = [
    token.casefold() for token in readback_narrative_tokens
]
def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from strings(nested)

events = []
for line_no, line in enumerate(transcript.splitlines(), 1):
    if not line.strip():
        continue
    try:
        event = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{transcript_path}:{line_no}: invalid JSONL: {exc.msg}")
    event_text = "\n".join(strings(event))
    events.append((line_no, event, event_text))

def model_visible(event):
    event_type = event.get("type")
    if event_type == "item.completed":
        return event.get("item", {}).get("type") in {"command_execution", "agent_message"}
    return event_type in {"tool_call", "message", "agent_message", "command_execution"}

def completed_command(event):
    event_type = event.get("type")
    item = event.get("item", {}) if event_type == "item.completed" else event
    if item.get("type") != "command_execution" or item.get("exit_code") != 0:
        return None
    command = item.get("command")
    return command.strip() if isinstance(command, str) else None

def invoked_command(event):
    event_type = event.get("type")
    if event_type == "item.completed":
        item = event.get("item", {})
        command = item.get("command") if item.get("type") == "command_execution" else None
    elif event_type == "command_execution":
        command = event.get("command")
    elif event_type == "tool_call":
        command = event.get("arguments", {}).get("command")
    else:
        command = None
    return command if isinstance(command, str) else ""

def command_tokens(command):
    try:
        punctuation = ";&|(){}"
        lexer = shlex.shlex(command, posix=True, punctuation_chars=punctuation)
        lexer.whitespace_split = True
        tokens = []
        for token in lexer:
            if token and all(character in punctuation for character in token):
                tokens.extend(token)
            else:
                tokens.append(token)
        return tokens
    except ValueError:
        return []

def lexical_path_segments(operand):
    normalized = re.sub(r"/+", "/", operand.casefold().replace("\\", "/"))
    segments = []
    for segment in normalized.split("/"):
        if not segment or segment == ".":
            continue
        if segment == "..":
            if segments and segments[-1] != "..":
                segments.pop()
            else:
                segments.append(segment)
            continue
        segments.append(segment)
    return segments

def installed_payload_operand(operand):
    segments = lexical_path_segments(operand)
    return any(
        segments[index : index + 2] == ["skills", "implementaudit"]
        for index in range(len(segments) - 1)
    )

read_actions = {
    "cat",
    "dir",
    "gc",
    "gci",
    "get-childitem",
    "get-content",
    "grep",
    "head",
    "ls",
    "more",
    "rg",
    "select-string",
    "tail",
    "type",
}

command_separators = {";", "&&", "||", "|", "&", "(", ")", "{", "}"}
shell_wrappers = {
    "bash": {"-c"},
    "cmd": {"/c"},
    "powershell": {"-c", "-command"},
    "pwsh": {"-c", "-command"},
    "sh": {"-c"},
}
execution_prefixes = {"command", "env"}

def normalized_action(token):
    action = token.casefold().replace("\\", "/").rsplit("/", 1)[-1]
    return action[:-4] if action.endswith(".exe") else action

def command_segments(tokens):
    segments = []
    current = []
    for token in tokens:
        if token in command_separators:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments

def positional_operands(tokens, value_options=(), casefold_options=True):
    operands = []
    if casefold_options:
        value_options = {option.casefold() for option in value_options}
    else:
        value_options = set(value_options)
    skip_value = False
    for token in tokens:
        if skip_value:
            skip_value = False
            continue
        option_token = token.casefold() if casefold_options else token
        option_name = option_token.split("=", 1)[0]
        if option_name in value_options:
            skip_value = "=" not in token
            continue
        if token.startswith("-"):
            continue
        operands.append(token)
    return operands

def reader_targets(action, arguments):
    folded = [argument.casefold() for argument in arguments]
    explicit_paths = []
    for index, argument in enumerate(folded[:-1]):
        if argument in {"-path", "-literalpath"}:
            explicit_paths.append(arguments[index + 1])
    if explicit_paths:
        return explicit_paths

    if action == "rg":
        pattern_options = {"-e", "--regexp", "-f", "--file"}
        value_options = pattern_options | {
            "-A", "--after-context", "-B", "--before-context", "-C",
            "--context", "-g", "--glob", "-m", "--max-count", "-r",
            "--replace", "--sort", "--sortr", "-t", "--type",
            "--type-add", "--encoding", "--pre",
        }
        explicit_pattern = any(
            token.split("=", 1)[0] in pattern_options
            or (token.startswith(("-e", "-f")) and len(token) > 2)
            for token in arguments
        )
        operands = positional_operands(
            arguments, value_options, casefold_options=False
        )
        if "--files" in arguments:
            return operands
        return operands if explicit_pattern else operands[1:]

    if action == "grep":
        pattern_options = {"-e", "--regexp", "-f", "--file"}
        value_options = pattern_options | {
            "-A", "--after-context", "-B", "--before-context", "-C",
            "--context", "-m", "--max-count", "--exclude", "--include",
            "--exclude-from", "--include-from",
        }
        explicit_pattern = any(
            token.split("=", 1)[0] in pattern_options
            or (token.startswith(("-e", "-f")) and len(token) > 2)
            for token in arguments
        )
        operands = positional_operands(
            arguments, value_options, casefold_options=False
        )
        return operands if explicit_pattern else operands[1:]

    if action == "select-string":
        explicit_pattern = "-pattern" in folded
        operands = positional_operands(
            arguments,
            {"-pattern", "-encoding", "-context", "-culture"},
        )
        return operands if explicit_pattern else operands[1:]

    return positional_operands(
        arguments,
        {
            "-encoding", "-filter", "-include", "-exclude", "-readcount",
            "-tail", "-totalcount", "-wait", "-first", "-last", "-skip",
        },
    )

def segment_reads_installed_payload(tokens):
    if not tokens:
        return False
    action_index = 1 if tokens[0] == "&" and len(tokens) > 1 else 0
    action = normalized_action(tokens[action_index])
    arguments = tokens[action_index + 1 :]

    if action in execution_prefixes:
        index = 0
        if action == "env":
            value_options = {"-C", "--chdir", "-S", "--split-string", "-u", "--unset"}
            skip_value = False
            while index < len(arguments):
                token = arguments[index]
                if skip_value:
                    skip_value = False
                    index += 1
                    continue
                option = token.split("=", 1)[0]
                if option in value_options:
                    skip_value = "=" not in token
                    index += 1
                    continue
                if token.startswith("-") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", token):
                    index += 1
                    continue
                break
        else:
            while index < len(arguments) and arguments[index].startswith("-"):
                index += 1
        return segment_reads_installed_payload(arguments[index:])

    if action in shell_wrappers:
        command_flags = shell_wrappers[action]
        for index, argument in enumerate(arguments):
            folded = argument.casefold()
            combined_shell_command = (
                action in {"bash", "sh"}
                and folded.startswith("-")
                and not folded.startswith("--")
                and "c" in folded[1:]
            )
            if (folded in command_flags or combined_shell_command) and index + 1 < len(arguments):
                return command_reads_installed_payload(" ".join(arguments[index + 1 :]))
        return False

    if action not in read_actions:
        return False
    return any(
        installed_payload_operand(target)
        for target in reader_targets(action, arguments)
    )

def command_reads_installed_payload(command):
    tokens = command_tokens(command)
    return any(
        segment_reads_installed_payload(segment)
        for segment in command_segments(tokens)
    )

model_events = [
    (line_no, event, event_text)
    for line_no, event, event_text in events
    if model_visible(event)
]

baseline_positions = {}
for token in baseline_tokens:
    positions = [
        line_no
        for line_no, event, _event_text in events
        if completed_command(event) == token
    ]
    if not positions:
        raise SystemExit(
            f"{transcript_path}: missing successful baseline command completion: {token}"
        )
    baseline_positions[token] = min(positions)
baseline_complete = max(baseline_positions.values())

readback_positions = [
    line_no
    for line_no, event, event_text in model_events
    if command_reads_installed_payload(invoked_command(event))
    or any(
        token in event_text.casefold()
        for token in readback_narrative_tokens_casefold
    )
]
if readback_positions:
    first_readback = min(readback_positions)
    if first_readback <= baseline_complete:
        raise SystemExit(
            f"{transcript_path}: installed skill readback occurred before baseline"
        )

real_home_patterns = [
    re.compile(r"(?i)[a-z]:\\users\\[^\\\r\n'\"]+\\\.codex\\skills\\implementaudit"),
    re.compile(r"(?i)/[a-z]/users/[^/\r\n'\"]+/\.codex/skills/implementaudit"),
    re.compile(r"(?i)/(?:home|users)/[^/\r\n'\"]+/\.codex/skills/implementaudit"),
    re.compile(r"(?i)(?:\$\{?home\}?|~|%userprofile%)[/\\]\.codex[/\\]skills[/\\]implementaudit"),
]
real_home_positions = [
    line_no
    for line_no, event, event_text in events
    if any(
        pattern.search(
            event.get("skill_path", "")
            if event.get("type") == "host.skill.loaded"
            else event_text
        )
        for pattern in real_home_patterns
    )
]
if real_home_positions:
    first_real_home = min(real_home_positions)
    temp_home_patterns = [
        re.compile(r"(?i)[a-z]:\\users\\[^\\\s'\"]+\\appdata\\local\\temp\\[^\n]*[/\\]skills[/\\]implementaudit"),
        re.compile(r"(?i)/[a-z]/users/[^/\s'\"]+/appdata/local/temp/[^\n]*/skills/implementaudit"),
        re.compile(r"(?i)/tmp/[^\n]*/skills/implementaudit"),
    ]
    temp_positions = [
        line_no
        for line_no, event, event_text in events
        if (
            event.get("type") == "host.skill.loaded"
            and any(
                pattern.search(event.get("skill_path", ""))
                for pattern in temp_home_patterns
            )
        )
        or (
            completed_command(event) is not None
            and "install-codex-from-release.sh" in completed_command(event)
            and any(
                pattern.search(completed_command(event))
                for pattern in temp_home_patterns
            )
        )
    ]
    if not temp_positions or min(temp_positions) >= first_real_home:
        raise SystemExit(
            f"{transcript_path}: real-home skill readback occurred before structured temp-home installation or activation evidence"
        )

sys.stdout.write("check-dogfood-bootstrap-contract: ok\n")
PY
