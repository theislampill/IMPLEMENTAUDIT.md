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
control=""
event_file=""
event_key_file=""
expected_candidate=""
expected_tree=""
expected_package=""
expected_runtime=""
corroboration_file=""
activation_file=""

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
    --control)
      [ "$#" -ge 2 ] || fail "--control requires self-dogfood or ordinary"
      control="$2"
      shift 2
      ;;
    --event-file|--event-key-file|--expected-candidate|--expected-tree|--expected-package|--expected-runtime|--corroboration-file|--activation-file)
      [ "$#" -ge 2 ] || fail "$1 requires a path or identity"
      case "$1" in
        --event-file) event_file="$2" ;;
        --event-key-file) event_key_file="$2" ;;
        --expected-candidate) expected_candidate="$2" ;;
        --expected-tree) expected_tree="$2" ;;
        --expected-package) expected_package="$2" ;;
        --expected-runtime) expected_runtime="$2" ;;
        --corroboration-file) corroboration_file="$2" ;;
        --activation-file) activation_file="$2" ;;
      esac
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

"${py_cmd[@]}" - \
  "$skill_file" "$audit_file" "$transcript_file" "$control" \
  "$event_file" "$event_key_file" "$expected_candidate" "$expected_tree" \
  "$expected_package" "$expected_runtime" "$corroboration_file" \
  "$activation_file" <<'PY'
import hashlib
import hmac
import json
import re
import shlex
import sys
from pathlib import Path

skill_path = Path(sys.argv[1])
audit_path = Path(sys.argv[2])
transcript_path = Path(sys.argv[3])
control = sys.argv[4]
event_path = Path(sys.argv[5])
event_key_path = Path(sys.argv[6])
expected_candidate = sys.argv[7]
expected_tree = sys.argv[8]
expected_package = sys.argv[9]
expected_runtime = sys.argv[10]
corroboration_path = Path(sys.argv[11])
activation_path = Path(sys.argv[12])

if not skill_path.is_file():
    raise SystemExit(f"missing skill file: {skill_path}")
if str(audit_path) != "." and not audit_path.is_file():
    raise SystemExit(f"missing audit file: {audit_path}")
if not transcript_path.is_file():
    raise SystemExit(f"missing transcript fixture: {transcript_path}")

skill = skill_path.read_text(encoding="utf-8")
audit = audit_path.read_text(encoding="utf-8") if str(audit_path) != "." else ""
transcript = transcript_path.read_text(encoding="utf-8")

heading = "## State-derived RC self-dogfood route"
if heading not in skill:
    raise SystemExit(f"{skill_path}: missing {heading}")

execution_heading = "## Execution Spine"
if execution_heading not in skill:
    raise SystemExit(f"{skill_path}: missing {execution_heading}")
if skill.index(execution_heading) > skill.index(heading):
    raise SystemExit(f"{skill_path}: generic Execution Spine must remain primary")

required_skill_tokens = [
    "`SELF_DOGFOOD_TRIGGER`",
    "IMPLEMENTAUDIT RC/self-release candidate",
    "Baseline the target repo first",
    "references/transcript-contract.md",
    "progressively discloses",
    "runner reference, broker, typed event schema",
    "independent corroboration",
    "It is not a user-selected mode",
    "Full installed-payload readback is non-evidence",
    "`ORDINARY_IMPLEMENTAUDIT_CONTROL`",
    "do not load or activate the dogfood reference, broker, or event schema",
    "inspect -> act -> verify -> done",
]
for token in required_skill_tokens:
    if token not in skill:
        raise SystemExit(f"{skill_path}: missing dogfood bootstrap token: {token}")

contract_path = Path("skills/implementaudit/references/transcript-contract.md")
if not contract_path.is_file():
    raise SystemExit(f"missing dogfood evidence owner: {contract_path}")
contract = contract_path.read_text(encoding="utf-8")
for token in [
    "## RC self-dogfood evidence contract",
    "runner-owned action boundary",
    "candidate commit, candidate tree, package SHA-256, and installed runtime SHA-256",
    "an event cannot qualify itself",
    "monotonically increasing sequence",
    "previous event identity",
    "HMAC produced with runner custody unavailable to the audited model",
    "Validation fails closed on a missing event",
    "sequence/correlation/event identity",
    "blocked/ambiguous result",
    "Typed runner events are the primary semantic evidence, not sole authority",
    "independently parsed adversarial",
    "Andon: typed dogfood evidence contradicts independent observation",
    "`ORDINARY_IMPLEMENTAUDIT_CONTROL`",
]:
    if token not in contract:
        raise SystemExit(f"{contract_path}: missing dogfood evidence token: {token}")

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

def canonical(value):
    return json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def jsonl(path, label):
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    values = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            values.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_number}: invalid JSONL: {exc.msg}")
    return values

def validate_ordinary_control():
    values = jsonl(activation_path, "ordinary activation trace")
    if [value.get("sequence") for value in values] != list(range(1, len(values) + 1)):
        raise SystemExit(f"{activation_path}: ordinary activation trace is reordered")
    if not any(
        value.get("action") == "load"
        and value.get("target_role") == "execution-spine"
        and value.get("result") == "completed"
        for value in values
    ):
        raise SystemExit(f"{activation_path}: ordinary Execution Spine load is missing")
    forbidden_roles = {
        "dogfood-reference", "dogfood-broker", "dogfood-event-schema",
    }
    if any(
        value.get("target_role") in forbidden_roles
        or value.get("action") == "self-dogfood-trigger"
        for value in values
    ):
        raise SystemExit(
            f"{activation_path}: ORDINARY_IMPLEMENTAUDIT_CONTROL activated dogfood machinery"
        )
    sys.stdout.write("check-dogfood-bootstrap-contract: ordinary control ok\n")

def validate_self_dogfood():
    required_inputs = {
        "event file": event_path,
        "event key file": event_key_path,
    }
    for label, path in required_inputs.items():
        if not path.is_file():
            raise SystemExit(f"missing {label}: {path}")
    identities = {
        "candidate_commit": expected_candidate,
        "candidate_tree": expected_tree,
        "package_sha256": expected_package,
        "runtime_sha256": expected_runtime,
    }
    patterns = {
        "candidate_commit": r"[a-f0-9]{40}",
        "candidate_tree": r"[a-f0-9]{40}",
        "package_sha256": r"[a-f0-9]{64}",
        "runtime_sha256": r"[a-f0-9]{64}",
    }
    for name, value in identities.items():
        if not re.fullmatch(patterns[name], value):
            raise SystemExit(f"expected {name} has invalid identity syntax")
    try:
        key = bytes.fromhex(event_key_path.read_text(encoding="ascii").strip())
    except (OSError, ValueError) as exc:
        raise SystemExit(f"cannot read runner event key: {exc}")
    if len(key) != 32:
        raise SystemExit("runner event key must be 32 bytes")
    values = jsonl(event_path, "typed dogfood journal")
    if not values:
        raise SystemExit(f"{event_path}: missing typed dogfood events")
    required_fields = {
        "schema", "session_id", "sequence", "event_id", "previous_event_id",
        "correlation_id", "actor", "action", "target_role", "phase", "result",
        "candidate_commit", "candidate_tree", "package_sha256", "runtime_sha256",
        "target_identity", "hmac_sha256",
    }
    optional_fields = {"target_path", "content_sha256"}
    allowed_values = {
        "actor": {"runner", "host", "model"},
        "action": {
            "self-dogfood-trigger", "load-reference", "load-broker",
            "load-event-schema", "baseline-status", "baseline-head",
            "activate-runtime", "read", "search",
        },
        "target_role": {
            "self-release-audit-object", "dogfood-reference",
            "dogfood-broker", "dogfood-event-schema", "source",
            "temp-installed-runtime", "real-home-runtime", "other",
        },
        "phase": {"pre-baseline", "post-baseline"},
        "result": {"completed", "blocked", "ambiguous"},
    }
    seen_events = set()
    seen_correlations = set()
    previous = "0" * 64
    for index, event in enumerate(values, 1):
        missing = required_fields - set(event)
        extra = set(event) - required_fields - optional_fields
        if missing or extra:
            raise SystemExit(
                f"{event_path}:{index}: typed event schema mismatch; missing={sorted(missing)} extra={sorted(extra)}"
            )
        if event["schema"] != "implementaudit.dogfood-event.v1":
            raise SystemExit(f"{event_path}:{index}: typed event schema identity mismatch")
        if type(event["sequence"]) is not int or event["sequence"] < 1:
            raise SystemExit(f"{event_path}:{index}: typed event sequence is invalid")
        for field, allowed in allowed_values.items():
            if event[field] not in allowed:
                raise SystemExit(f"{event_path}:{index}: typed event {field} is invalid")
        for field in ("session_id", "correlation_id", "target_identity"):
            if not isinstance(event[field], str) or not event[field]:
                raise SystemExit(f"{event_path}:{index}: typed event {field} is invalid")
        for field in ("event_id", "previous_event_id", "package_sha256", "runtime_sha256", "hmac_sha256"):
            if not isinstance(event[field], str) or not re.fullmatch(r"[a-f0-9]{64}", event[field]):
                raise SystemExit(f"{event_path}:{index}: typed event {field} is invalid")
        for field in ("candidate_commit", "candidate_tree"):
            if not isinstance(event[field], str) or not re.fullmatch(r"[a-f0-9]{40}", event[field]):
                raise SystemExit(f"{event_path}:{index}: typed event {field} is invalid")
        if "target_path" in event and (
            not isinstance(event["target_path"], str) or not event["target_path"]
        ):
            raise SystemExit(f"{event_path}:{index}: typed event target_path is invalid")
        if "content_sha256" in event and (
            not isinstance(event["content_sha256"], str)
            or not re.fullmatch(r"[a-f0-9]{64}", event["content_sha256"])
        ):
            raise SystemExit(f"{event_path}:{index}: typed event content_sha256 is invalid")
        if event["sequence"] != index or event["previous_event_id"] != previous:
            raise SystemExit(f"{event_path}:{index}: typed events are missing, duplicate, or reordered")
        if event["event_id"] in seen_events or event["correlation_id"] in seen_correlations:
            raise SystemExit(f"{event_path}:{index}: duplicate typed event or correlation identity")
        seen_events.add(event["event_id"])
        seen_correlations.add(event["correlation_id"])
        previous = event["event_id"]
        supplied = event.pop("hmac_sha256")
        expected_hmac = hmac.new(key, canonical(event), hashlib.sha256).hexdigest()
        event["hmac_sha256"] = supplied
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected_hmac):
            raise SystemExit(f"{event_path}:{index}: forged typed event HMAC")
        for name, expected in identities.items():
            if event.get(name) != expected:
                raise SystemExit(f"{event_path}:{index}: {name} identity mismatch")
        if event["result"] != "completed":
            raise SystemExit(f"{event_path}:{index}: blocked or ambiguous typed event cannot qualify")

    required_actions = [
        "self-dogfood-trigger", "load-reference", "load-broker",
        "load-event-schema", "baseline-status", "baseline-head",
        "activate-runtime",
    ]
    action_positions = {}
    for action in required_actions:
        positions = [index for index, event in enumerate(values) if event["action"] == action]
        if len(positions) != 1:
            raise SystemExit(f"{event_path}: required typed action {action} must occur exactly once")
        action_positions[action] = positions[0]
    if [action_positions[action] for action in required_actions] != sorted(
        action_positions[action] for action in required_actions
    ):
        raise SystemExit(f"{event_path}: typed self-dogfood actions are reordered")
    if not any(event["action"] in {"read", "search"} for event in values):
        raise SystemExit(f"{event_path}: targeted model read/search evidence is missing")
    expected_roles = {
        "self-dogfood-trigger": "self-release-audit-object",
        "load-reference": "dogfood-reference",
        "load-broker": "dogfood-broker",
        "load-event-schema": "dogfood-event-schema",
        "baseline-status": "source",
        "baseline-head": "source",
        "activate-runtime": "temp-installed-runtime",
    }
    for event in values:
        expected_role = expected_roles.get(event["action"])
        if expected_role and event["target_role"] != expected_role:
            raise SystemExit(f"{event_path}: {event['action']} target role mismatch")
        if event["target_role"] == "real-home-runtime":
            raise SystemExit(f"{event_path}: real-home event cannot qualify")
        if event["actor"] == "model" and event["phase"] != "post-baseline":
            raise SystemExit(f"{event_path}: model read/search occurred before baseline")

    source_identities = {
        "load-reference": sha256_file(contract_path),
        "load-broker": sha256_file(Path("scripts/dogfood-evidence-broker.py")),
        "load-event-schema": sha256_file(Path("fixtures/dogfood-bootstrap/typed-event.schema.json")),
        "self-dogfood-trigger": f"{expected_candidate}:{expected_tree}",
        "activate-runtime": expected_runtime,
    }
    for action, expected in source_identities.items():
        event = values[action_positions[action]]
        if event["target_identity"] != expected:
            raise SystemExit(f"{event_path}: {action} target identity mismatch")

    if not corroboration_path.is_file():
        raise SystemExit("self-dogfood qualification requires independent corroboration")
    observed = jsonl(corroboration_path, "independent dogfood observation")
    observed_by_correlation = {}
    observed_correlations = []
    observed_fields = {
        "schema", "sequence", "correlation_id", "actor", "action",
        "target_role", "result",
    }
    for index, item in enumerate(observed, 1):
        if set(item) != observed_fields or item.get("schema") != "implementaudit.observed-action.v1":
            raise SystemExit(
                "Andon: typed dogfood evidence contradicts independent observation"
            )
        if item.get("sequence") != index:
            raise SystemExit(f"{corroboration_path}:{index}: observation sequence mismatch")
        correlation = item.get("correlation_id")
        if not isinstance(correlation, str) or correlation in observed_by_correlation:
            raise SystemExit(f"{corroboration_path}:{index}: observation correlation is missing or duplicate")
        observed_by_correlation[correlation] = item
        observed_correlations.append(correlation)
    corroborated_actions = {
        "baseline-status", "baseline-head", "activate-runtime", "read", "search"
    }
    typed_correlations = [
        event["correlation_id"]
        for event in values
        if event["action"] in corroborated_actions
    ]
    if observed_correlations != typed_correlations:
        raise SystemExit(
            "Andon: typed dogfood evidence contradicts independent observation"
        )
    for event in values:
        if event["action"] not in corroborated_actions:
            continue
        observed_event = observed_by_correlation.get(event["correlation_id"])
        expected_tuple = (
            event["actor"], event["action"], event["target_role"], event["result"]
        )
        actual_tuple = (
            observed_event.get("actor") if observed_event else None,
            observed_event.get("action") if observed_event else None,
            observed_event.get("target_role") if observed_event else None,
            observed_event.get("result") if observed_event else None,
        )
        if actual_tuple != expected_tuple:
            raise SystemExit(
                "Andon: typed dogfood evidence contradicts independent observation"
            )
    sys.stdout.write("check-dogfood-bootstrap-contract: typed self-dogfood ok\n")

if control:
    if control == "ordinary":
        validate_ordinary_control()
        raise SystemExit(0)
    if control == "self-dogfood":
        validate_self_dogfood()
        raise SystemExit(0)
    raise SystemExit(f"unknown dogfood control: {control}")

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
