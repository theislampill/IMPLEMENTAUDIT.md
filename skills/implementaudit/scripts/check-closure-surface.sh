#!/usr/bin/env bash
set -euo pipefail


fail() { printf 'check-closure-surface: %s\n' "$*" >&2; exit 1; }

file="${1:-}"
[ -f "$file" ] || fail "record file not found: ${file:-<none>}"
shift
impact_set=""
closure_evidence=""
superseded_plans=()
steer_dir=""
plan_cycle_records=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --impact-set)
      [ "$#" -ge 2 ] || fail "--impact-set requires a file"
      impact_set="$2"; shift 2 ;;
    --closure-evidence)
      [ "$#" -ge 2 ] || fail "--closure-evidence requires a file"
      closure_evidence="$2"; shift 2 ;;
    --superseded-plan)
      [ "$#" -ge 2 ] || fail "--superseded-plan requires a file"
      superseded_plans+=("$2"); shift 2 ;;
    --steer-dir)
      [ "$#" -ge 2 ] || fail "--steer-dir requires a directory"
      steer_dir="$2"; shift 2 ;;
    --plan-cycle-record)
      [ "$#" -ge 2 ] || fail "--plan-cycle-record requires a file"
      plan_cycle_records+=("$2"); shift 2 ;;
    *) fail "unknown argument: $1" ;;
  esac
done

py_cmd=()
ensure_python() {
  [ "${#py_cmd[@]}" -eq 0 ] || return 0
  if command -v python >/dev/null 2>&1; then py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
  else fail "python, python3, or py -3 is required for structured closure validation"
  fi
}

rank() {
  case "$1" in
    source) echo 0;; generated-artifact) echo 1;; package) echo 2;;
    installed-payload) echo 3;; running-local-service) echo 4;;
    deployed-service) echo 5;; api) echo 6;; user-visible) echo 7;;
    publication) echo 8;; *) echo -1;;
  esac
}

field() {
  printf '%s\n' "$1" | tr '|' '\n' | while IFS= read -r seg; do
    k="$(printf '%s' "$seg" | sed -n 's/^[[:space:]]*\([a-z_-]*\):.*/\1/p')"
    if [ "$k" = "$2" ]; then
      printf '%s' "$seg" | sed "s/^[[:space:]]*$2:[[:space:]]*//; s/[[:space:]]*$//"
      return
    fi
  done
}

field_count() {
  printf '%s\n' "$1" | tr '|' '\n' | sed -n "s/^[[:space:]]*$2:[[:space:]].*/x/p" | wc -l | tr -d '[:space:]'
}

rows=0
coverage_rows=0
seen_ids=""
while IFS= read -r line; do
  case "$line" in resource-exhausted:*)
    qid="$(field "$line" resource-exhausted)"
    qclass="$(field "$line" class)"
    blocker="$(field "$line" blocker)"
    reported="$(field "$line" reported_reset)"
    backoff="$(field "$line" backoff_probe_at)"
    next_probe="$(field "$line" next_probe_at)"
    capacity="$(field "$line" capacity_probe)"
    probe_evidence="$(field "$line" probe_evidence)"
    terminal="$(field "$line" terminal)"
    [ -n "$qid" ] || fail "resource-exhausted row has no identity"
    [ "$qclass" = transport-infrastructure ] \
      || fail "resource-exhausted $qid: class must be transport-infrastructure"
    [ "$blocker" = resource-exhausted ] \
      || fail "resource-exhausted $qid: blocker must be resource-exhausted"
    printf '%s' "$reported" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z ADVISORY$' \
      || fail "resource-exhausted $qid: reported_reset must be canonical UTC and labelled ADVISORY"
    reported_ts="${reported%% *}"
    printf '%s' "$backoff" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$' \
      || fail "resource-exhausted $qid: invalid backoff_probe_at"
    expected_next="$reported_ts"
    if [[ "$backoff" < "$expected_next" ]]; then expected_next="$backoff"; fi
    [ "$next_probe" = "$expected_next" ] \
      || fail "resource-exhausted $qid: next_probe_at must equal min(reported_reset, backoff_probe_at)"
    case "$capacity" in succeeded|failed) : ;;
      *) fail "resource-exhausted $qid: blocked/resume decision requires a completed cheap capacity probe";;
    esac
    [ -n "$probe_evidence" ] && [ "$probe_evidence" != none ] \
      || fail "resource-exhausted $qid: capacity probe has no checkable evidence"
    case "$capacity:$terminal" in
      succeeded:resumed|failed:blocked) : ;;
      succeeded:blocked) fail "resource-exhausted $qid: successful probe must resume before an advisory reset";;
      failed:resumed) fail "resource-exhausted $qid: failed probe cannot justify resumption";;
      *) fail "resource-exhausted $qid: invalid terminal '$terminal'";;
    esac
    continue
    ;;
  esac
  if printf '%s' "$line" | grep -qiE '^[[:space:]]*claim:'; then
    case "$line" in claim:*) : ;; *)
      fail "malformed claim row (key must be exactly lowercase 'claim:'): ${line%%|*}";;
    esac
  fi
  case "$line" in claim:*) : ;; *) continue;; esac
  rows=$((rows + 1))
  cid="$(field "$line" claim)"
  case " $seen_ids " in *" $cid "*)
    fail "duplicate Claim-ID '$cid' — each closure claim has one row";;
  esac
  seen_ids="$seen_ids $cid"
  surface="$(field "$line" surface)"
  status="$(field "$line" status)"
  esurface="$(field "$line" 'evidence-surface')"
  coverage="$(field "$line" coverage)"
  range_note="$(field "$line" range)"
  omission="$(field "$line" omission)"
  if [ -n "$coverage" ]; then
    coverage_rows=$((coverage_rows + 1))
    case "$coverage" in full|partial) : ;;
      *) fail "claim $cid: invalid coverage '$coverage' (expected full or partial)";;
    esac
  fi
  if [ "$coverage" = partial ]; then
    [ -n "$range_note" ] && [ -n "$omission" ] \
      || fail "claim $cid: partial coverage requires range and omission"
    [ "$status" != verified ] \
      || fail "claim $cid: partial coverage cannot support verified closure"
  fi
  if [ "$coverage" = full ] \
     && printf '%s' "$line" | grep -qi 'warning:[[:space:]]*truncated output'; then
    fail "claim $cid: truncation marker contradicts coverage full"
  fi
  [ "$(rank "$surface")" -ge 0 ] || fail "claim $cid: unknown required surface '$surface'"
  case "$status" in
    verified|failed|unverified|not-applicable) : ;;
    *) fail "claim $cid: invalid verification status '$status'";;
  esac
  if [ "$status" = verified ]; then
    [ -n "$esurface" ] || fail "claim $cid: verified with no evidence-surface — an uninspectable surface must be unverified/deferred"
    er="$(rank "$esurface")"
    sr="$(rank "$surface")"
    [ "$er" -ge 0 ] || fail "claim $cid: unknown evidence-surface '$esurface'"
    if [ "$er" -lt "$sr" ]; then
      fail "claim $cid: layer promotion — '$surface' claim verified only by lower-layer '$esurface' evidence"
    fi
  fi
done < "$file"

# #78 blocker rows are prospective and coexist with legacy claim-only records.
# Scope and still-runnable work are always explicit. A negative-capability
# assertion needs two case-normalized method identities, distinct method
# classes, and evidence bound to every method. Repeating or merely renaming a
# probe never manufactures confidence.
while IFS= read -r line; do
  if printf '%s' "$line" | grep -qiE '^[[:space:]]*blocker:'; then
    case "$line" in blocker:*) : ;; *)
      fail "malformed blocker row (key must be exactly lowercase 'blocker:'): ${line%%|*}";;
    esac
  fi
  case "$line" in blocker:*) : ;; *) continue;; esac
  bid="$(field "$line" blocker)"
  [ "$(field_count "$line" blocker)" = 1 ] && [ -n "$bid" ] \
    || fail "blocker row requires exactly one identity"
  for key in justification negative-capability probe_methods probe_evidence falsification_attempted terminal next_probe_or_abandon; do
    [ "$(field_count "$line" "$key")" -le 1 ] \
      || fail "blocker $bid: duplicate $key"
  done
  for key in blocked_scope unblocked_work; do
    [ "$(field_count "$line" "$key")" = 1 ] \
      || fail "blocker $bid: requires exactly one $key"
    [ -n "$(field "$line" "$key")" ] \
      || fail "blocker $bid: $key must be nonempty"
  done
  unblocked="$(field "$line" unblocked_work)"
  if [ "$unblocked" = none ]; then
    justification="$(field "$line" justification)"
    [ "$(field_count "$line" justification)" = 1 ] \
      && [ -n "$justification" ] && [ "$justification" != none ] \
      || fail "blocker $bid: unblocked_work none requires justification"
  fi
  negative="$(field "$line" negative-capability)"
  if [ -n "$negative" ] && [ "$negative" != true ] && [ "$negative" != false ]; then
    fail "blocker $bid: negative-capability must be true or false"
  fi
  if [ "$negative" = true ]; then
    methods="$(field "$line" probe_methods)"
    [ "$(field_count "$line" probe_methods)" = 1 ] && [ -n "$methods" ] \
      || fail "blocker $bid: negative capability requires probe_methods"
    probe_evidence="$(field "$line" probe_evidence)"
    [ "$(field_count "$line" probe_evidence)" = 1 ] && [ -n "$probe_evidence" ] \
      || fail "blocker $bid: negative capability requires probe_evidence"
    ensure_python
    probe_error=""
    if ! probe_error="$("${py_cmd[@]}" - "$methods" "$probe_evidence" <<'PY'
import re
import sys

methods = [part.strip() for part in sys.argv[1].split(",")]
if len(methods) < 2 or any(not part for part in methods):
    raise SystemExit("requires at least two nonempty probe methods")
normalized_methods = [part.casefold() for part in methods]
if len(set(normalized_methods)) != len(normalized_methods):
    raise SystemExit("probe methods must be distinct after case normalization")

entries = [part.strip() for part in sys.argv[2].split(";")]
if len(entries) != len(methods) or any(not part for part in entries):
    raise SystemExit("probe evidence must bind exactly one entry to every method")
classes = []
evidence_values = []
for index, entry in enumerate(entries):
    match = re.fullmatch(r"([^:;=]+)::([a-z0-9][a-z0-9-]*)=>(.+)", entry)
    if not match:
        raise SystemExit("probe evidence entries require method::method-class=>evidence")
    method, method_class, evidence = (part.strip() for part in match.groups())
    if method.casefold() != normalized_methods[index]:
        raise SystemExit("probe evidence method does not match probe_methods order")
    if not evidence or evidence.casefold() == "none":
        raise SystemExit("probe evidence must be nonempty and checkable")
    classes.append(method_class.casefold())
    evidence_values.append(evidence.casefold())
if len(set(classes)) != len(classes):
    raise SystemExit("probe method classes must be structurally distinct")
if len(set(evidence_values)) != len(evidence_values):
    raise SystemExit("probe evidence values must be distinct")
PY
)"; then
      [ -n "$probe_error" ] || probe_error="probe evidence validation failed"
      fail "blocker $bid: $probe_error"
    fi
    falsification="$(field "$line" falsification_attempted)"
    [ "$(field_count "$line" falsification_attempted)" = 1 ] \
      && [ -n "$falsification" ] && [ "$falsification" != none ] \
      || fail "blocker $bid: negative capability requires falsification_attempted"
  fi
  if [ "$(field "$line" terminal)" = blocked-non-verdict ]; then
    next_action="$(field "$line" next_probe_or_abandon)"
    [ "$(field_count "$line" next_probe_or_abandon)" = 1 ] \
      && [ -n "$next_action" ] && [ "$next_action" != none ] \
      || fail "blocker $bid: blocked-non-verdict requires next_probe_or_abandon"
  fi
done < "$file"

# #78 plan-cycle accounting is explicit only when a plan declares it. `none`
# carries no implicit cap. A numeric overrun needs a recorded OWNER_DECISION.
if [ "${#plan_cycle_records[@]}" -gt 0 ]; then
  ensure_python
  for cycle_file in "${plan_cycle_records[@]}"; do
    [ -f "$cycle_file" ] || fail "plan cycle record not found: $cycle_file"
    cycle_error=""
    if ! cycle_error="$("${py_cmd[@]}" - "$cycle_file" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

def values(key):
    near = [line for line in lines if re.match(rf"^\s*{re.escape(key)}\s*:", line, re.I)]
    exact = [line.split(":", 1)[1].strip() for line in lines
             if line.startswith(key + ":")]
    if len(near) != len(exact):
        raise SystemExit(f"{key} must use exact uppercase grammar")
    if len(exact) != 1:
        raise SystemExit(f"{key} must appear exactly once")
    return exact[0]

bound = values("CYCLE_BOUND")
consumed_text = values("CYCLES_CONSUMED")
if not re.fullmatch(r"[0-9]+", consumed_text):
    raise SystemExit("CYCLES_CONSUMED must be a nonnegative integer")
consumed = int(consumed_text)
if bound == "none":
    pass
elif re.fullmatch(r"[0-9]+", bound):
    if consumed > int(bound):
        decisions = [line.split(":", 1)[1].strip() for line in lines
                     if line.startswith("BOUND_OVERRUN:")]
        if decisions != ["OWNER_DECISION"]:
            raise SystemExit("declared cycle-bound overrun requires BOUND_OVERRUN: OWNER_DECISION")
else:
    raise SystemExit("CYCLE_BOUND must be none or a nonnegative integer")
PY
)"; then
      [ -n "$cycle_error" ] || cycle_error="plan cycle validation failed"
      fail "$cycle_file: $cycle_error"
    fi
  done
fi

[ "$rows" -gt 0 ] || fail "no closure claim rows found"
[ "$coverage_rows" -eq 0 ] || [ "$coverage_rows" -eq "$rows" ] \
  || fail "closure record mixes coverage-tagged and untagged claim rows"

# #88 external-state schemas are prospective: only the new record prefixes,
# explicit #88 claim fields, and schema headings enter this validator. Existing
# claim rows and the source-to-publication rank ladder above retain their behavior.
schema_required=0
if grep -Eqi '^[[:space:]]*(external-mutation-record|artifact-identity|collision-receipt|external-evidence):|external-(kind|mutation|mutation-record):[[:space:]]|^## Suggested Commit Message When No Commit Authorized$' "$file"; then
  schema_required=1
fi
if [ "$schema_required" -eq 1 ]; then
  ensure_python
  schema_error=""
  if ! schema_error="$("${py_cmd[@]}" - "$file" <<'PY'
import ast
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import sys


path = os.path.abspath(sys.argv[1])
with open(path, "r", encoding="utf-8") as handle:
    lines = handle.read().splitlines()


def die(message):
    print(message)
    raise SystemExit(1)


def parse_segments(line, prefix, label, expected_fields):
    parts = line.split("|")
    identity = parts[0][len(prefix):].strip()
    if not identity:
        die(f"{label} has no identity")
    fields = {}
    order = []
    for segment in parts[1:]:
        if ":" not in segment:
            die(f"{label} {identity}: malformed field '{segment.strip()}'")
        raw_key, raw_value = segment.split(":", 1)
        key = raw_key.strip()
        value = raw_value.strip()
        if key in fields:
            die(f"{label} {identity}: duplicate field '{key}'")
        fields[key] = value
        order.append(key)
    for key in expected_fields:
        if key not in fields:
            die(f"{label} {identity}: missing {key}")
    unexpected = [key for key in order if key not in expected_fields]
    if unexpected:
        die(f"{label} {identity}: unexpected field '{unexpected[0]}'")
    if order != expected_fields:
        die(f"{label} {identity}: fields must use the canonical one-line order")
    return identity, fields


def loose_fields(line):
    fields = {}
    raw_keys = []
    for segment in line.split("|")[1:]:
        if ":" not in segment:
            continue
        raw_key, raw_value = segment.split(":", 1)
        key = raw_key.strip()
        raw_keys.append(key)
        if key not in fields:
            fields[key] = raw_value.strip()
    return fields, raw_keys


def token_in(command, token):
    return re.search(r"(?<![A-Za-z0-9_-])" + re.escape(token) + r"(?![A-Za-z0-9_-])", command) is not None


def valid_timestamp(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value):
        return False
    try:
        dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def scalar_text(value):
    if isinstance(value, (dict, list)):
        return None
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


class DuplicateKey(ValueError):
    pass


class NonStandardConstant(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def reject_constant(value):
    raise NonStandardConstant(value)


def readback_argv(command, runner):
    if runner == "python":
        try:
            expression = ast.parse(command, mode="eval").body
            if not isinstance(expression, ast.Call):
                return None
            function = expression.func
            if not (
                isinstance(function, ast.Attribute)
                and function.attr == "run"
                and isinstance(function.value, ast.Name)
                and function.value.id == "subprocess"
            ):
                return None
            if len(expression.args) != 1:
                return None
            argv = ast.literal_eval(expression.args[0])
            if not isinstance(argv, (list, tuple)) or not argv or not all(isinstance(item, str) for item in argv):
                return None
            keywords = {item.arg: ast.literal_eval(item.value) for item in expression.keywords if item.arg}
            if len(keywords) != len(expression.keywords):
                return None
            if set(keywords) - {"capture_output", "text", "check"}:
                return None
            if keywords.get("capture_output") is not True:
                return None
            return list(argv)
        except (SyntaxError, ValueError):
            return None

    shell_command = command.strip()
    if runner == "powershell" and shell_command.startswith("& "):
        shell_command = shell_command[2:].lstrip()
    if runner == "powershell" and re.search(r"[@$(){}\[\]]", shell_command):
        return None
    if re.search(r"[;&|`<>\r\n]|\$\(", shell_command):
        return None
    try:
        return shlex.split(shell_command, posix=True)
    except ValueError:
        return None


def api_endpoint_matches(endpoint, target_kind, target_id):
    escaped_id = re.escape(target_id)
    patterns = {
        "issue": rf"(?:^|/)issues/{escaped_id}(?:$|[/?])",
        "pr": rf"(?:^|/)pulls/{escaped_id}(?:$|[/?])",
        "milestone": rf"(?:^|/)milestones/{escaped_id}(?:$|[/?])",
        "label": rf"(?:^|/)labels/{escaped_id}(?:$|[/?])",
        "release": rf"(?:^|/)releases/(?:tags/)?{escaped_id}(?:$|[/?])",
        "release-asset": rf"(?:^|/)releases/assets/{escaped_id}(?:$|[/?])",
    }
    return re.search(patterns[target_kind], endpoint) is not None


def parse_readonly_options(arguments, value_flags, switch_flags):
    parsed = []
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in switch_flags:
            parsed.append((argument, None))
            index += 1
            continue
        if argument in value_flags:
            if index + 1 >= len(arguments):
                return None
            parsed.append((argument, arguments[index + 1]))
            index += 2
            continue
        equal_flag = next((
            flag for flag in value_flags
            if flag.startswith("--")
            and argument.startswith(flag + "=")
            and argument != flag + "="
        ), None)
        if equal_flag is not None:
            parsed.append((equal_flag, argument[len(equal_flag) + 1:]))
            index += 1
            continue
        return None
    return parsed


def approved_readback_query(command, runner, target_kind, target_id):
    argv = readback_argv(command, runner)
    if not argv:
        return False
    write_flags = {"--method", "-X", "--input", "--field", "-f", "--raw-field", "-F"}
    for argument in argv:
        if argument in write_flags:
            return False
        if any(argument.startswith(flag + "=") for flag in {"--method", "--input", "--field", "--raw-field"}):
            return False
        if any(argument.startswith(flag) and argument != flag for flag in {"-X", "-f", "-F"}):
            return False
    direct_forms = {
        "issue": ["gh", "issue", "view", target_id],
        "pr": ["gh", "pr", "view", target_id],
        "release": ["gh", "release", "view", target_id],
    }
    if target_kind in direct_forms and argv[:4] == direct_forms[target_kind]:
        return parse_readonly_options(
            argv[4:],
            {"--json", "--jq", "--template"},
            {"--comments", "--web"},
        ) is not None
    if target_kind == "label" and argv[:3] == ["gh", "label", "list"]:
        label_args = argv[3:]
        label_options = parse_readonly_options(
            label_args,
            {"--search", "--json", "--jq", "--template", "--limit", "--order", "--sort"},
            {"--web"},
        )
        if label_options is None:
            return False
        search_values = [value for flag, value in label_options if flag == "--search"]
        return search_values == [target_id]
    if len(argv) >= 3 and argv[:2] == ["gh", "api"]:
        endpoint = argv[2]
        if endpoint.startswith("-"):
            return False
        return api_endpoint_matches(endpoint, target_kind, target_id) and parse_readonly_options(
            argv[3:],
            {"--jq", "--template", "--hostname", "--cache"},
            {"--paginate", "--slurp", "--include", "--verbose"},
        ) is not None
    return False


prefix_labels = {
    "external-mutation-record:": "external-mutation-record",
    "artifact-identity:": "artifact-identity",
    "collision-receipt:": "collision-receipt",
    "external-evidence:": "external-evidence",
}
for line in lines:
    stripped = line.lstrip()
    for prefix, label in prefix_labels.items():
        if stripped.lower().startswith(prefix.lower()) and not line.startswith(prefix):
            die(f"malformed {label} row (key must be exactly lowercase '{prefix}')")


claims = {}
claim_order = []
for line in lines:
    if not line.startswith("claim:"):
        continue
    claim_id = line.split("|", 1)[0][len("claim:"):].strip()
    fields, raw_keys = loose_fields(line)
    claims[claim_id] = fields
    claim_order.append(claim_id)
    external_key_variants = [key for key in raw_keys if key.lower() in {"external-kind", "external-mutation", "external-mutation-record"}]
    for key in external_key_variants:
        if key not in {"external-kind", "external-mutation", "external-mutation-record"}:
            die(f"claim {claim_id}: malformed external field '{key}'")
    for key in ("external-kind", "external-mutation", "external-mutation-record"):
        if len([raw_key for raw_key in raw_keys if raw_key == key]) > 1:
            die(f"claim {claim_id}: duplicate field '{key}'")


mutation_fields = [
    "runner", "target-kind", "target-id", "mutation-command",
    "mutation-exit", "mutation-evidence", "readback-command",
    "readback-exit", "readback-file", "readback-sha256",
    "readback-field", "expected-value", "observed-value",
    "readback-evidence",
]
mutation_records = {}
record_dir = os.path.realpath(os.path.dirname(path))
mutating_verbs = ("close", "create", "edit", "delete", "merge", "label", "comment", "transfer", "publish", "upload")
target_kinds = {"issue", "pr", "milestone", "label", "release", "release-asset"}
for line in lines:
    if not line.startswith("external-mutation-record:"):
        continue
    record_id, fields = parse_segments(
        line, "external-mutation-record:", "external mutation", mutation_fields
    )
    if record_id in mutation_records:
        die(f"duplicate external-mutation-record ID '{record_id}'")
    mutation_records[record_id] = fields

    runner = fields["runner"]
    if runner not in {"python", "bash", "powershell"}:
        die(f"external mutation {record_id}: invalid runner '{runner}'")
    target_kind = fields["target-kind"]
    if target_kind not in target_kinds:
        die(f"external mutation {record_id}: invalid target-kind '{target_kind}'")
    target_id = fields["target-id"]
    if not re.fullmatch(r"\S+", target_id):
        die(f"external mutation {record_id}: target-id must be one nonempty token")
    command_mutating_verbs = tuple(
        verb for verb in mutating_verbs
        if not (target_kind == "label" and verb == "label")
    )

    mutation_command = fields["mutation-command"]
    readback_command = fields["readback-command"]
    if re.search(r"\becho\b", mutation_command, re.IGNORECASE):
        die(f"external mutation {record_id}: mutation-command cannot use echo as evidence")
    if not token_in(mutation_command, target_kind) or not token_in(mutation_command, target_id):
        die(f"external mutation {record_id}: mutation-command does not target {target_kind} '{target_id}'")
    if not any(token_in(mutation_command.lower(), verb) for verb in command_mutating_verbs):
        die(f"external mutation {record_id}: mutation-command has no approved mutating verb")
    if runner == "python" and "subprocess.run" not in mutation_command:
        die(f"external mutation {record_id}: python mutation-command must use subprocess.run")
    if fields["mutation-exit"] != "0":
        die(f"external mutation {record_id}: mutation-exit must be 0, got '{fields['mutation-exit']}'")
    if not fields["mutation-evidence"]:
        die(f"external mutation {record_id}: mutation-evidence must be nonempty")

    if mutation_command == readback_command:
        die(f"external mutation {record_id}: readback-command must be distinct from mutation-command")
    if re.search(r"\becho\b", readback_command, re.IGNORECASE):
        die(f"external mutation {record_id}: readback-command cannot use echo")
    if not approved_readback_query(readback_command, runner, target_kind, target_id):
        die(f"external mutation {record_id}: readback-command is not an approved read-only {target_kind} query")
    if fields["readback-exit"] != "0":
        die(f"external mutation {record_id}: readback-exit must be 0, got '{fields['readback-exit']}'")
    if not fields["readback-evidence"]:
        die(f"external mutation {record_id}: readback-evidence must be nonempty")
    if fields["readback-evidence"] == fields["mutation-evidence"]:
        die(f"external mutation {record_id}: readback-evidence must differ from mutation-evidence")

    witness_name = fields["readback-file"]
    if not re.fullmatch(r"[^/\\]+\.json", witness_name) or witness_name in {".", ".."}:
        die(f"external mutation {record_id}: readback-file must be a bare relative JSON basename, got '{witness_name}'")
    witness_path = os.path.abspath(os.path.join(record_dir, witness_name))
    try:
        contained = os.path.commonpath([record_dir, witness_path]) == record_dir
    except ValueError:
        contained = False
    if not contained:
        die(f"external mutation {record_id}: readback-file escapes the record directory")
    if os.path.islink(witness_path):
        die(f"external mutation {record_id}: readback-file '{witness_name}' must not be a symlink")
    if not os.path.isfile(witness_path):
        die(f"external mutation {record_id}: readback-file '{witness_name}' is not a regular file")
    canonical_witness = os.path.realpath(witness_path)
    try:
        canonical_contained = os.path.commonpath([record_dir, canonical_witness]) == record_dir
    except ValueError:
        canonical_contained = False
    if not canonical_contained:
        die(f"external mutation {record_id}: canonical readback-file escapes the record directory")

    expected_sha = fields["readback-sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        die(f"external mutation {record_id}: readback-sha256 must be 64 lowercase hex")
    try:
        with open(canonical_witness, "rb") as witness:
            witness_bytes = witness.read()
    except OSError:
        die(f"external mutation {record_id}: readback-file '{witness_name}' is not readable")
    actual_sha = hashlib.sha256(witness_bytes).hexdigest()
    if actual_sha != expected_sha:
        die(f"external mutation {record_id}: readback SHA-256 does not match {witness_name}")

    readback_field = fields["readback-field"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", readback_field):
        die(f"external mutation {record_id}: readback-field must name one top-level field")
    try:
        payload = json.loads(
            witness_bytes.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except DuplicateKey as error:
        die(f"external mutation {record_id}: readback JSON contains duplicate object key '{error.args[0]}'")
    except NonStandardConstant as error:
        die(f"external mutation {record_id}: readback JSON contains non-standard constant '{error.args[0]}'")
    except (UnicodeError, json.JSONDecodeError):
        die(f"external mutation {record_id}: readback-file is not valid UTF-8 JSON")
    if not isinstance(payload, dict):
        die(f"external mutation {record_id}: readback JSON must be a top-level object")
    if readback_field not in payload:
        die(f"external mutation {record_id}: readback JSON has no top-level field '{readback_field}'")
    parsed = scalar_text(payload[readback_field])
    if parsed is None:
        die(f"external mutation {record_id}: readback field '{readback_field}' must be scalar")
    observed = fields["observed-value"]
    expected = fields["expected-value"]
    if parsed != observed:
        die(f"external mutation {record_id}: parsed readback field '{readback_field}' value '{parsed}' does not match observed '{observed}'")
    if observed != expected:
        die(f"external mutation {record_id}: observed value '{observed}' does not match expected '{expected}'")


for claim_id in claim_order:
    fields = claims[claim_id]
    opted_in = any(key in fields for key in ("external-kind", "external-mutation", "external-mutation-record"))
    if not opted_in:
        continue
    explicit_mutation = fields.get("external-mutation") == "true"
    external_kind = fields.get("external-kind")
    if external_kind not in {"observation", "mutation"}:
        die(f"claim {claim_id}: verified external surface requires external-kind observation or mutation")
    if explicit_mutation and external_kind != "mutation":
        die(f"claim {claim_id}: external-mutation true requires external-kind mutation")
    if external_kind == "mutation":
        record_id = fields.get("external-mutation-record", "")
        if not record_id:
            die(f"claim {claim_id}: external mutation requires external-mutation-record")
        if record_id not in mutation_records:
            die(f"claim {claim_id}: external-mutation-record '{record_id}' does not resolve exactly once")


artifact_fields = ["sha256"]
artifacts = {}
for line in lines:
    if not line.startswith("artifact-identity:"):
        continue
    name, fields = parse_segments(line, "artifact-identity:", "artifact identity", artifact_fields)
    digest = fields["sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        die(f"artifact identity '{name}': sha256 must be 64 lowercase hex")
    artifacts.setdefault(name, []).append(digest)


receipt_fields = ["hashes", "reason"]
receipts = {}
for line in lines:
    if not line.startswith("collision-receipt:"):
        continue
    name, fields = parse_segments(line, "collision-receipt:", "collision receipt", receipt_fields)
    if name in receipts:
        die(f"duplicate collision-receipt for '{name}'")
    hashes = fields["hashes"].split(",") if fields["hashes"] else []
    if any(not re.fullmatch(r"[0-9a-f]{64}", item) for item in hashes):
        die(f"collision receipt '{name}': hashes must be comma-separated 64 lowercase hex values")
    if len(hashes) != len(set(hashes)):
        die(f"collision receipt '{name}' hash set does not exactly match observed hashes")
    if not fields["reason"]:
        die(f"collision receipt '{name}': reason must be nonempty")
    receipts[name] = set(hashes)


for name, hashes in artifacts.items():
    observed_hashes = set(hashes)
    if len(observed_hashes) > 1 and name not in receipts:
        die(f"artifact identity '{name}' has {len(observed_hashes)} distinct hashes but no collision receipt")
    if name in receipts and receipts[name] != observed_hashes:
        die(f"collision receipt '{name}' hash set does not exactly match observed hashes")
for name in receipts:
    if name not in artifacts or len(set(artifacts[name])) < 2:
        die(f"collision receipt '{name}' does not name an observed collision")


external_evidence_fields = [
    "bytes", "mtime", "liveness", "still-producing", "use",
    "closure-bytes", "closure-mtime",
]
evidence_ids = set()
for line in lines:
    if not line.startswith("external-evidence:"):
        continue
    evidence_id, fields = parse_segments(
        line, "external-evidence:", "external evidence", external_evidence_fields
    )
    if evidence_id in evidence_ids:
        die(f"duplicate external-evidence ID '{evidence_id}'")
    evidence_ids.add(evidence_id)
    if not re.fullmatch(r"[0-9]+", fields["bytes"]):
        die(f"external evidence {evidence_id}: bytes must be a nonnegative integer")
    if not valid_timestamp(fields["mtime"]):
        die(f"external evidence {evidence_id}: invalid mtime '{fields['mtime']}' (expected RFC3339 UTC whole-second timestamp)")
    if fields["liveness"] not in {"snapshot", "terminal"}:
        die(f"external evidence {evidence_id}: invalid liveness '{fields['liveness']}'")
    if fields["still-producing"] not in {"true", "false"}:
        die(f"external evidence {evidence_id}: still-producing must be true or false")
    if fields["use"] not in {"orientation", "terminal"}:
        die(f"external evidence {evidence_id}: use must be orientation or terminal")
    closure_bytes = fields["closure-bytes"]
    closure_mtime = fields["closure-mtime"]
    if closure_bytes != "none" and not re.fullmatch(r"[0-9]+", closure_bytes):
        die(f"external evidence {evidence_id}: closure-bytes must be a nonnegative integer or none")
    if closure_mtime != "none" and not valid_timestamp(closure_mtime):
        die(f"external evidence {evidence_id}: invalid closure-mtime '{closure_mtime}'")
    if fields["use"] == "terminal":
        if fields["liveness"] == "snapshot" and fields["still-producing"] == "true":
            die(f"external evidence {evidence_id}: still-producing snapshot cannot support terminal use")
        if closure_bytes == "none" or closure_mtime == "none":
            die(f"external evidence {evidence_id}: terminal use requires closure bytes and mtime")
        if closure_bytes != fields["bytes"] or closure_mtime != fields["mtime"]:
            die(f"external evidence {evidence_id}: closure re-stat does not match original bytes and mtime")


heading = "## Suggested Commit Message When No Commit Authorized"
heading_indexes = [index for index, line in enumerate(lines) if line == heading]
if len(heading_indexes) > 1:
    die("proposed commit message: duplicate canonical headings")
if heading_indexes:
    index = heading_indexes[0] + 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines) or not re.fullmatch(r"```[A-Za-z0-9_-]*", lines[index]):
        die("proposed commit message: missing fenced block boundaries")
    index += 1
    block = []
    while index < len(lines) and lines[index] != "```":
        block.append(lines[index])
        index += 1
    if index >= len(lines):
        die("proposed commit message: missing fenced block boundaries")
    block_text = "\n".join(block)
    makes_claim = bool(re.search(r"[0-9]|\b(?:pass|fail|fixed|verified|closed|refuted|machine-checked)\b", block_text, re.IGNORECASE))
    anchors = []
    malformed_anchor = False
    for block_line in block:
        if "Evidence anchor:" not in block_line:
            continue
        match = re.fullmatch(r"Evidence anchor: claim:([A-Za-z0-9._-]+)", block_line)
        if match:
            anchors.append(match.group(1))
        else:
            malformed_anchor = True
    if malformed_anchor and not makes_claim:
        die("proposed commit message: exactly one well-formed Evidence anchor is allowed")
    if makes_claim and (malformed_anchor or len(anchors) != 1):
        die("proposed commit message: digit or verdict claim requires exactly one Evidence anchor: claim:<Claim-ID>")
    if anchors:
        if malformed_anchor or len(anchors) != 1:
            die("proposed commit message: exactly one well-formed Evidence anchor is allowed")
        claim_id = anchors[0]
        if claim_id not in claims:
            die(f"proposed commit message: Evidence anchor claim '{claim_id}' is unresolved")
        claim = claims[claim_id]
        if claim.get("status") != "verified":
            die(f"proposed commit message: Evidence anchor claim '{claim_id}' is not verified")
        if claim.get("evidence-surface") not in {"source", "generated-artifact", "package", "installed-payload", "running-local-service", "deployed-service", "api", "user-visible", "publication"}:
            die(f"proposed commit message: Evidence anchor claim '{claim_id}' has no checkable evidence surface")
PY
)"; then
    [ -n "$schema_error" ] || schema_error="external-state schema validation failed without a diagnostic"
    fail "$schema_error"
  fi
fi

# #78 decision-time ledger. Absence means no decision was declared. When the
# sibling ledger exists, validate each append-only JSONL row strictly and
# refuse terminal closure while a row remains pending or unresolved.
deferrals_file="$(dirname "$file")/deferrals.jsonl"
if [ -e "$deferrals_file" ]; then
  [ -f "$deferrals_file" ] && [ ! -L "$deferrals_file" ] \
    || fail "deferrals ledger must be a regular non-symlink file: $deferrals_file"
  ensure_python
  deferral_error=""
  if ! deferral_error="$("${py_cmd[@]}" - "$deferrals_file" <<'PY'
import datetime as dt
import json
import sys

path = sys.argv[1]
keys = ["ts", "phase", "what", "why", "owner", "unblock", "disposition"]
allowed = {
    "pending", "unresolved", "deferred", "transferred", "owner-assigned",
    "risk-accepted", "validated-resolved",
}
owners = {"this-run", "executor", "owner", "other"}


def die(message):
    print(message)
    raise SystemExit(1)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            die(f"duplicate key '{key}'")
        result[key] = value
    return result


with open(path, "r", encoding="utf-8") as handle:
    for line_number, raw in enumerate(handle, 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(
                raw,
                object_pairs_hook=unique_object,
                parse_constant=lambda value: die(f"non-standard constant '{value}'"),
            )
        except (UnicodeError, json.JSONDecodeError) as error:
            die(f"row {line_number}: invalid UTF-8 JSON: {error}")
        if not isinstance(row, dict):
            die(f"row {line_number}: expected one JSON object")
        if list(row) != keys:
            die(f"row {line_number}: keys must use the canonical order")
        if not all(isinstance(row[key], str) and row[key].strip() for key in keys):
            die(f"row {line_number}: every field must be a nonempty string")
        if not row["phase"].isdigit():
            die(f"row {line_number}: phase must be a nonnegative integer string")
        try:
            dt.datetime.strptime(row["ts"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            die(f"row {line_number}: ts must be RFC3339 UTC whole seconds")
        if row["owner"] not in owners:
            die(f"row {line_number}: invalid owner '{row['owner']}'")
        disposition = row["disposition"]
        if disposition not in allowed:
            die(f"row {line_number}: invalid disposition '{disposition}'")
        if disposition == "risk-accepted" and not row["unblock"].startswith("policy:"):
            die(f"row {line_number}: risk-accepted requires a policy: reference")
        if disposition == "transferred" and row["owner"] == "this-run":
            die(f"row {line_number}: transferred disposition must name a receiving owner")
        if disposition in {"pending", "unresolved"}:
            die(f"row {line_number}: nonterminal disposition '{disposition}' blocks closure")
PY
)"; then
    [ -n "$deferral_error" ] || deferral_error="deferrals ledger validation failed without a diagnostic"
    fail "deferrals.jsonl: $deferral_error"
  fi
fi
if grep -E -q "Name[[:space:]]*=[[:space:]]*['\"][^'\"]*\\.exe|pkill[[:space:]]+-f|taskkill([.]exe)?[[:space:]].*/IM|Get-CimInstance[[:space:]]+Win32_Process" "$file"; then
  fail "kill authority uses executable name, image, pattern, or broad host-process enumeration instead of process-started.json identity"
fi
if grep -E 'Get-Process([[:space:]]|$)' "$file" |
   grep -Evq 'Get-Process[[:space:]]+-Id([[:space:]]|$)'; then
  fail "kill authority uses broad Get-Process enumeration without -Id"
fi
if [ -n "$impact_set" ]; then
  checker="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-respec-impact-set.sh"
  bash "$checker" "$impact_set" >/dev/null \
    || fail "impact set is not terminal"
fi
if [ -n "$closure_evidence" ]; then
  [ -f "$closure_evidence" ] || fail "closure evidence not found: $closure_evidence"
  if grep -Eqi '(^|[|:[:space:]])(Pending\.|remains pending|IN PROGRESS|TBD)([|[:space:]]|$)' "$closure_evidence"; then
    fail "closure evidence retains a pending or in-progress marker: $closure_evidence"
  fi
fi

for plan in "${superseded_plans[@]}"; do
  [ -f "$plan" ] || fail "superseded plan not found: $plan"
  grep -Eq '^SUPERSEDED_BY: [^[:space:]].* — .+' "$plan" \
    || fail "superseded plan lacks SUPERSEDED_BY path and reason: $plan"
  bad_unchecked="$(grep -nE '^[[:space:]]*-[[:space:]]+\[[[:space:]]\]' "$plan" \
    | grep -Ev '\|[[:space:]]*RECONCILIATION:[[:space:]]*(STALE|TODO|BLOCKED)[[:space:]]*$' \
    | head -n 1 || true)"
  [ -z "$bad_unchecked" ] \
    || fail "superseded plan has unchecked item without reconciliation: $bad_unchecked"
done

if [ -n "$steer_dir" ]; then
  [ -d "$steer_dir" ] || fail "steer directory not found: $steer_dir"
  undeclared=0
  while IFS= read -r -d '' steer; do
    if ! grep -Eqi '^supersedes:[[:space:]]+[^[:space:]]' "$steer"; then
      undeclared=$((undeclared + 1))
    fi
  done < <(find "$steer_dir" -maxdepth 1 -type f \( -iname '*steer*.md' -o -iname '*advisory*.md' \) -print0)
  if [ "$undeclared" -gt 2 ]; then
    printf 'check-closure-surface: warning: %d steer/advisory artifacts lack declared precedence\n' "$undeclared" >&2
  fi
fi
printf 'check-closure-surface: ok (%d claim row(s))\n' "$rows"
