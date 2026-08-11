#!/usr/bin/env bash
set -euo pipefail

# Parameter-bound authorization drift check (#12). Read-only. Compares a
# runtime invocation's consequential parameters against the parameters an
# authorization record binds.
#
#   check-authorization-binding.sh --auth <auth-file> --invocation <inv-file>
#
# Both files are `key: value` lists. The auth file declares:
#   binds: <k1>,<k2>,...        (the consequential parameters governed)
#   <k>: <value-or-range>       (bound value; a range like 1..1000 or a set
#                                a|b|c is honored)
# The invocation file supplies actual runtime `<k>: <value>` lines.
#
# AUTHORITY DRIFT (exit 1) when a consequential parameter present in the
# invocation is NOT in `binds`, or its value conflicts with the bound
# value/range. A matching invocation exits 0 with no added ceremony. If the
# auth binds nothing (no `binds:` line), any consequential invocation
# parameter is unbound => drift.

fail() { printf 'check-authorization-binding: %s\n' "$*" >&2; exit 1; }
drift() {
  printf 'check-authorization-binding: AUTHORITY DRIFT (%s) — class owner-unclear/authority; STOP the governed action and request an owner decision\n' "$*" >&2
  exit 1
}

# Scarce-resource preflight rehearsal (#84). This mode is deliberately
# separate from the legacy authorization-record comparison below. It executes
# the declared production wrapper once, but only after replacing its producer
# endpoint with the bounded substitute supplied by the caller.
if [ "${1:-}" = "--phase" ]; then
  phase=""; rehearsal=""; launch=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --phase) [ "$#" -ge 2 ] || fail "--phase requires a file"; phase="$2"; shift 2;;
      --rehearsal) [ "$#" -ge 2 ] || fail "--rehearsal requires a file"; rehearsal="$2"; shift 2;;
      --launch) [ "$#" -ge 2 ] || fail "--launch requires a file"; launch="$2"; shift 2;;
      *) fail "unknown rehearsal arg $1";;
    esac
  done
  [ -f "$phase" ] || fail "phase file not found: $phase"
  python - "$phase" "$rehearsal" "$launch" <<'PY'
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

def fail(message):
    print(f"check-authorization-binding: rehearsal rejected ({message})", file=sys.stderr)
    raise SystemExit(1)

phase_path, rehearsal_path, launch_path = sys.argv[1:]
phase_text = pathlib.Path(phase_path).read_text(encoding="utf-8")
budget_lines = re.findall(r"(?mi)^Scarce resource budget:[ \t]*(.*?)[ \t]*$", phase_text)
if len(budget_lines) != 1:
    fail("phase must contain exactly one Scarce resource budget field")
budget = budget_lines[0]
if budget == "none":
    if rehearsal_path or launch_path:
        fail("a none budget accepts no rehearsal or launch artifact")
    print("check-authorization-binding: ok — scarce resource budget is none")
    raise SystemExit(0)
if not re.fullmatch(r"[1-9][0-9]* [^\s]+", budget):
    fail("budget must be 'none' or 'N <resource>' with positive N")
if not rehearsal_path or not launch_path:
    fail("non-none budget requires --rehearsal and --launch")

def load_object(path, label):
    def reject_duplicate_members(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate object member {key!r}")
            value[key] = item
        return value
    try:
        value = json.loads(
            pathlib.Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_members,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        fail(f"invalid {label} JSON: {exc}")
    if type(value) is not dict:
        fail(f"{label} must be one JSON object")
    return value

receipt = load_object(rehearsal_path, "REHEARSAL_TERMINAL")
launch = load_object(launch_path, "launch record")
receipt_keys = {
    "rehearsed_command_hash", "stub_identity", "stubbed_components",
    "env_keys_present", "terminal_artifact_path", "exit_code",
    "disposition", "timestamp",
}
launch_keys = {
    "argv", "env_keys_present", "terminal_artifact_path",
    "launch_records", "metered_calls",
}
if set(receipt) != receipt_keys:
    fail(f"REHEARSAL_TERMINAL fields must be exactly {sorted(receipt_keys)}")
if set(launch) != launch_keys:
    fail(f"launch record fields must be exactly {sorted(launch_keys)}")

def nonempty_string(value, label):
    if type(value) is not str or not value:
        fail(f"{label} must be a nonempty string")

def string_array(value, label, *, nonempty=True):
    if type(value) is not list or (nonempty and not value):
        fail(f"{label} must be a nonempty string array")
    if any(type(item) is not str or not item for item in value):
        fail(f"{label} contains an invalid string")

def env_keys(value, label):
    string_array(value, label)
    if value != sorted(value) or len(value) != len(set(value)):
        fail(f"{label} must be sorted and unique")
    if any(not re.fullmatch(r"[A-Z_][A-Z0-9_]*", item) for item in value):
        fail(f"{label} may contain environment key names only")

nonempty_string(receipt["rehearsed_command_hash"], "rehearsed_command_hash")
if not re.fullmatch(r"[0-9a-f]{64}", receipt["rehearsed_command_hash"]):
    fail("rehearsed_command_hash must be lowercase SHA-256")
nonempty_string(receipt["stub_identity"], "stub_identity")
string_array(receipt["stubbed_components"], "stubbed_components")
if len(receipt["stubbed_components"]) != len(set(receipt["stubbed_components"])):
    fail("stubbed_components must be unique")
env_keys(receipt["env_keys_present"], "receipt env_keys_present")
nonempty_string(receipt["terminal_artifact_path"], "receipt terminal_artifact_path")
if type(receipt["exit_code"]) is not int:
    fail("exit_code must be an integer")
if receipt["disposition"] not in {"PASS", "PASS_WITH_SCOPE_GAP", "FAIL"}:
    fail("invalid disposition")
nonempty_string(receipt["timestamp"], "timestamp")
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", receipt["timestamp"]):
    fail("timestamp must be UTC ISO-8601 ending Z")
try:
    datetime.datetime.fromisoformat(receipt["timestamp"].replace("Z", "+00:00"))
except ValueError:
    fail("timestamp is not a real UTC instant")

string_array(launch["argv"], "argv")
nonempty_string(launch["argv"][0], "production wrapper argv[0]")
env_keys(launch["env_keys_present"], "launch env_keys_present")
nonempty_string(launch["terminal_artifact_path"], "launch terminal_artifact_path")
for key in ("launch_records", "metered_calls"):
    if type(launch[key]) is not int or launch[key] < 0:
        fail(f"{key} must be a nonnegative integer")
if launch["metered_calls"] != 0:
    fail("a rehearsal must consume zero metered calls")

if receipt["env_keys_present"] != launch["env_keys_present"]:
    fail("receipt and launch environment-key sets differ")
if receipt["terminal_artifact_path"] != launch["terminal_artifact_path"]:
    fail("receipt and launch terminal artifact paths differ")
preimage = json.dumps(
    {"argv": launch["argv"], "env_keys_present": sorted(launch["env_keys_present"])},
    ensure_ascii=False,
    separators=(",", ":"),
).encode("utf-8")
actual_hash = hashlib.sha256(preimage).hexdigest()
if receipt["rehearsed_command_hash"] != actual_hash:
    fail("rehearsed command hash does not match exact argv/environment-key identity")
if receipt["exit_code"] != 0 or receipt["disposition"] == "FAIL":
    fail("nonzero or FAIL rehearsal never authorizes launch")

components = receipt["stubbed_components"]
if "producer" not in components:
    fail("producer must be stubbed")
extras = [item for item in components if item != "producer"]
if not extras:
    if receipt["disposition"] != "PASS" or components != ["producer"]:
        fail("PASS requires exactly the producer stub")
else:
    if receipt["disposition"] != "PASS_WITH_SCOPE_GAP":
        fail("interposed stubs require PASS_WITH_SCOPE_GAP")
    residuals = re.findall(r"(?mi)^Residual risk:[ \t]*(.*?)[ \t]*$", phase_text)
    missing = [item for item in extras if not any(item in line for line in residuals)]
    if missing:
        fail(f"Residual risk must name every interposed stub: {missing}")

# A receipt/launch pair is only a declaration until the declared wrapper has
# traversed its real transport with a substitute producer. The substitute is
# supplied out of band so neither a secret nor a producer endpoint is captured
# in the receipt. The wrapper receives only bounded control paths and the
# already-derived non-secret identity fields below.
stub_raw = os.environ.get("IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB")
if not stub_raw:
    fail("missing bounded producer stub environment")
stub_path = pathlib.Path(stub_raw)
if not stub_path.is_file() or not os.access(stub_path, os.X_OK):
    fail("bounded producer stub must be an executable regular file")
stub_identity = "sha256:" + hashlib.sha256(stub_path.read_bytes()).hexdigest()
if receipt["stub_identity"] != stub_identity:
    fail("receipt stub identity does not match bounded producer stub")

for key in launch["env_keys_present"]:
    if key not in os.environ:
        fail(f"declared environment key is absent for rehearsal: {key}")

terminal_path = pathlib.Path(launch["terminal_artifact_path"])
if not terminal_path.parent.is_dir():
    fail("terminal artifact parent directory does not exist")
if terminal_path.exists() or terminal_path.is_symlink():
    fail("terminal artifact must be absent before wrapper execution")

proof_fd, proof_raw = tempfile.mkstemp(
    prefix=".implementaudit-rehearsal-stub-",
    dir=terminal_path.parent,
)
os.close(proof_fd)
proof_path = pathlib.Path(proof_raw)
proof_path.unlink()

run_env = os.environ.copy()
run_env.update({
    "IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB": str(stub_path.resolve()),
    "IMPLEMENTAUDIT_REHEARSAL_TERMINAL": launch["terminal_artifact_path"],
    "IMPLEMENTAUDIT_REHEARSAL_STUB_PROOF": str(proof_path),
    "IMPLEMENTAUDIT_REHEARSAL_COMMAND_HASH": actual_hash,
    "IMPLEMENTAUDIT_REHEARSAL_STUB_IDENTITY": stub_identity,
    "IMPLEMENTAUDIT_REHEARSAL_ENV_KEYS": json.dumps(
        launch["env_keys_present"], separators=(",", ":")
    ),
})
try:
    completed = subprocess.run(launch["argv"], env=run_env, check=False)
except OSError as exc:
    fail(f"production wrapper could not execute: {exc}")
if completed.returncode != 0:
    fail(f"production wrapper exited {completed.returncode}")
if not proof_path.is_file() or proof_path.read_text(encoding="utf-8") != stub_identity + "\n":
    fail("bounded producer stub did not produce its identity proof")
if not terminal_path.is_file() or terminal_path.is_symlink():
    fail("production wrapper did not produce the declared terminal artifact")
observed = load_object(str(terminal_path), "execution terminal")
if observed != receipt:
    fail("execution terminal does not match the supplied rehearsal receipt")

print("check-authorization-binding: ok — rehearsal identity and terminal receipt are bound")
PY
  exit $?
fi

auth=""; inv=""; state=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --auth) auth="$2"; shift 2;;
    --invocation) inv="$2"; shift 2;;
    --state) state="$2"; shift 2;;
    *) fail "unknown arg $1";;
  esac
done
[ -z "$state" ] || [ -f "$state" ] || fail "STATE file not found: $state"

# Durable intake mode (#137). An ungranted STATE stays cheap default-deny.
# A claimed authorization supplies the full record -> STATE -> invocation
# chain; partial carriers fail closed.
if [ -n "$state" ] && [ -z "$auth$inv" ]; then
  if grep -qiE '^.+ authorized:[[:space:]]*yes[[:space:]]*$' "$state" \
    || { grep -E '\|[[:space:]]*standing-authorization[[:space:]]*\|' "$state" \
      | grep -Eq '\|[[:space:]]*active[[:space:]]*\|'; }; then
    fail "missing grant source for authorized STATE action"
  fi
  printf 'check-authorization-binding: ok — durable STATE is default deny\n'
  exit 0
fi
if [ -n "$state" ] && { [ -z "$auth" ] || [ -z "$inv" ]; }; then
  fail "durable intake requires --auth and --invocation"
fi
[ -f "$auth" ] || fail "auth file not found: $auth"
[ -f "$inv" ] || fail "invocation file not found: $inv"

# An absent key (e.g. no `binds:` line) is a real case that must be
# EVALUATED (unbound => drift), not an early script death under
# `set -euo pipefail`. Swallow grep's no-match to empty output.
val() { { grep -iE "^$2:" "$1" || true; } | head -n1 | sed "s/^[^:]*: *//" | tr -d '\r' | sed 's/[[:space:]]*$//'; }

# Duplicate keys in the AUTHORIZATION record are ambiguous authority —
# a permissive spec listed first would silently shadow a stricter one
# (Fable review of PR #32). One value per key, malformed otherwise.
dup_check() {
  n="$({ grep -ciE "^$1:" "$auth" || true; })"
  [ "${n:-0}" -le 1 ] || fail "malformed authorization: key '$1' appears $n times — one value per key"
}
dup_check binds
binds="$(val "$auth" binds)"
for k in $(printf '%s' "$binds" | tr ',' ' '); do
  dup_check "$k"
done

if [ -n "$state" ]; then
  for k in source issued_at grant_quote scope lifecycle action; do
    dup_check "$k"
    [ -n "$(val "$auth" "$k")" ] \
      || fail "missing grant source metadata: $k"
  done
  source_ref="$(val "$auth" source)"
  lifecycle="$(val "$auth" lifecycle)"
  action="$(val "$auth" action)"
  [ "$lifecycle" = standing-authorization ] \
    || fail "authorization lifecycle must be standing-authorization"
  printf '%s\n' "$(val "$auth" issued_at)" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' \
    || fail "authorization issued_at must be YYYY-MM-DD"

  state_rows="$(awk -F '|' -v ref="$source_ref" -v kind="$lifecycle" \
    -v action="$action" -v evidence="$auth" '
    function trim(s) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", s); return s }
    NF >= 11 && trim($3) == ref && trim($4) == kind && trim($5) == "owner" \
      && trim($6) == action && trim($8) == "active" \
      && trim($9) == evidence { print }
  ' "$state")"
  [ "$(printf '%s\n' "$state_rows" | sed '/^$/d' | wc -l | tr -d ' ')" = 1 ] \
    || { printf 'check-authorization-binding: AUTHORIZATION INCONSISTENT (STATE lacks one active source-bound authorization row)\n' >&2; exit 1; }

  state_flag() {
    local label="$1" line
    line="$({ grep -iE "^$label authorized:" "$state" || true; })"
    [ "$(printf '%s\n' "$line" | sed '/^$/d' | wc -l | tr -d ' ')" = 1 ] \
      || { printf 'check-authorization-binding: AUTHORIZATION INCONSISTENT (STATE field %s authorized is missing or duplicated)\n' "$label" >&2; exit 1; }
    printf '%s' "$line" | sed 's/^[^:]*:[[:space:]]*//' | tr '[:upper:]' '[:lower:]' | sed 's/[[:space:]]*$//'
  }
  check_state_action() {
    local label="$1" token="$2" actual expected=no
    case "$action" in *"$token"*) expected=yes;; esac
    actual="$(state_flag "$label")"
    [ "$actual" = "$expected" ] \
      || { printf 'check-authorization-binding: AUTHORIZATION INCONSISTENT (%s authorized: %s, source action: %s)\n' "$label" "$actual" "$action" >&2; exit 1; }
  }
  check_state_action Commit commit
  check_state_action Push push
  actual_release="$(state_flag 'Tag/release/publication/provenance')"
  expected_release=no
  case "$action" in *tag*|*release*|*publish*|*publication*|*provenance*) expected_release=yes;; esac
  [ "$actual_release" = "$expected_release" ] \
    || { printf 'check-authorization-binding: AUTHORIZATION INCONSISTENT (release/publication authorized: %s, source action: %s)\n' "$actual_release" "$action" >&2; exit 1; }
fi

in_range() {  # value, spec
  local v="$1" spec="$2"
  case "$spec" in
    *..*) local lo="${spec%%..*}" hi="${spec##*..}"
          [ "$v" -ge "$lo" ] 2>/dev/null && [ "$v" -le "$hi" ] 2>/dev/null ;;
    *"|"*) printf '%s' "|$spec|" | grep -qF "|$v|" ;;
    *) [ "$v" = "$spec" ] ;;
  esac
}

# Every consequential parameter the INVOCATION supplies must be bound and
# in-range. Consequential params are those the invocation marks with a
# leading `param.` prefix (so ordinary metadata lines are ignored).
drifted=""
# `|| [ -n "$line" ]` keeps a final line WITHOUT a trailing newline in
# scope — a drifting parameter on an unterminated last line was silently
# dropped by plain `while read` (Fable review of PR #32).
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in param.*) : ;; *) continue;; esac
  key="$(printf '%s' "$line" | sed -n 's/^\(param\.[a-zA-Z0-9_-]*\):.*/\1/p')"
  short="${key#param.}"
  v="$(printf '%s' "$line" | sed "s/^[^:]*: *//" | tr -d '\r' | sed 's/[[:space:]]*$//')"
  case ",$binds," in
    *",$short,"*) : ;;
    *) drifted="$drifted $short(unbound)"; continue;;
  esac
  spec="$(val "$auth" "$short")"
  if [ -n "$spec" ] && ! in_range "$v" "$spec"; then
    drifted="$drifted $short(=$v vs bound $spec)"
  fi
done < "$inv"

# Every parameter the authorization BINDS must actually be supplied by
# the invocation: a bound-but-unsupplied parameter means the governed
# action would run on a source/tool default the owner never saw —
# defaults are never implicitly adopted (Fable review of PR #32).
for k in $(printf '%s' "$binds" | tr ',' ' '); do
  grep -qiE "^param\.$k:" "$inv" \
    || drifted="$drifted $k(bound-but-unsupplied — runtime value unknown; defaults are never implicitly adopted)"
done

[ -z "$drifted" ] || drift "$drifted"
printf 'check-authorization-binding: ok — all consequential parameters bound and in range\n'
