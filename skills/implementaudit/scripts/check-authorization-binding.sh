#!/usr/bin/env bash
set -euo pipefail

# Parameter-bound authorization drift (#12): auth `binds:` values/ranges must
# cover every consequential invocation parameter or the action default-denies.

fail() { printf 'check-authorization-binding: %s\n' "$*" >&2; exit 1; }
drift() {
  printf 'check-authorization-binding: AUTHORITY DRIFT (%s) — class owner-unclear/authority; STOP the governed action and request an owner decision\n' "$*" >&2
  exit 1
}

# Scarce-resource preflight rehearsal (#84).
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
import datetime as dt,hashlib,json,os
from pathlib import Path as P
import re,socket,stat,subprocess,sys,tempfile,threading

def fail(message):
    print(f"check-authorization-binding: rehearsal rejected ({message})", file=sys.stderr); raise SystemExit(1)

def require(value, label):
    if not value: fail(label)

phase_path, rehearsal_path, launch_path = sys.argv[1:]
phase_text = P(phase_path).read_text(encoding="utf-8")

def phase_value(name):
    values = re.findall(rf"(?mi)^{re.escape(name)}:[ \\t]*(.*?)[ \\t]*$", phase_text)
    require(len(values) == 1 and values[0] and values[0].casefold() != "none", f"invalid {name}")
    return values[0]

budget_lines = re.findall(r"(?mi)^Scarce resource budget:[ \t]*(.*?)[ \t]*$", phase_text)
require(len(budget_lines) == 1, "invalid Scarce resource budget")
budget = budget_lines[0]
if budget == "none":
    if rehearsal_path or launch_path:
        fail("a none budget accepts no rehearsal or launch artifact")
    print("check-authorization-binding: ok — scarce resource budget is none")
    raise SystemExit(0)
require(re.fullmatch(r"[1-9][0-9]* [^\s]+", budget), "invalid budget")
require(rehearsal_path and launch_path, "missing rehearsal or launch")

R,L,S,H,T,E = (
    phase_value(name) for name in ("Rehearsal receipt", "Rehearsal launch", "Rehearsal producer stub", "Rehearsal command hash", "Rehearsal terminal artifact", "Rehearsal environment keys"))
require(P(rehearsal_path).resolve() == P(R).resolve(), "rehearsal path differs from phase")
require(P(launch_path).resolve() == P(L).resolve(), "launch path differs from phase")

def load_object(path, label):
    def reject_duplicate_members(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, f"duplicate {key}")
            value[key] = item
        return value
    try: value = json.loads(P(path).read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_members)
    except (OSError, UnicodeError, ValueError) as exc: fail(f"invalid {label}: {exc}")
    require(type(value) is dict, f"invalid {label}")
    return value

r = load_object(rehearsal_path, "REHEARSAL_TERMINAL")
launch = load_object(launch_path, "launch record")
require(set(r) == set("rehearsed_command_hash stub_identity stubbed_components env_keys_present terminal_artifact_path exit_code disposition timestamp".split()), "invalid REHEARSAL_TERMINAL fields")
require(set(launch) == set("argv env_keys_present terminal_artifact_path launch_records metered_calls".split()), "invalid launch fields")

def text(value): return type(value) is str and bool(value)
def strings(value): return type(value) is list and bool(value) and all(text(item) for item in value)
def env(value): return strings(value) and value == sorted(value) and len(value) == len(set(value)) and all(re.fullmatch(r"[A-Z_][A-Z0-9_]*", item) for item in value)

require(text(r["rehearsed_command_hash"]) and re.fullmatch(r"[0-9a-f]{64}", r["rehearsed_command_hash"]), "invalid rehearsed_command_hash")
require(text(r["stub_identity"]), "invalid stub_identity")
require(strings(r["stubbed_components"]) and len(r["stubbed_components"]) == len(set(r["stubbed_components"])), "invalid stubbed_components")
require(env(r["env_keys_present"]), "invalid receipt env_keys_present")
require(text(r["terminal_artifact_path"]), "invalid receipt terminal_artifact_path")
require(type(r["exit_code"]) is int, "invalid exit_code")
require(r["disposition"] in {"PASS", "PASS_WITH_SCOPE_GAP", "FAIL"}, "invalid disposition")
require(text(r["timestamp"]) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", r["timestamp"]), "invalid timestamp")
try:
    dt.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
except ValueError:
    fail("invalid timestamp")

require(strings(launch["argv"]), "invalid argv")
require(env(launch["env_keys_present"]), "invalid launch env_keys_present")
require(text(launch["terminal_artifact_path"]), "invalid launch terminal_artifact_path")
for key in ("launch_records", "metered_calls"):
    require(type(launch[key]) is int and launch[key] >= 0, f"invalid {key}")
require(launch["metered_calls"] == 0, "rehearsal must consume zero metered calls")

if r["env_keys_present"] != launch["env_keys_present"] or r["terminal_artifact_path"] != launch["terminal_artifact_path"]: fail("receipt/launch identity mismatch")
h = hashlib.sha256(json.dumps({"argv": launch["argv"], "env_keys_present": sorted(launch["env_keys_present"])}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
if r["rehearsed_command_hash"] != h or H != h: fail("command hash mismatch")
if P(T).resolve() != P(launch["terminal_artifact_path"]).resolve() or E != ",".join(launch["env_keys_present"]): fail("phase identity mismatch")
if r["exit_code"] != 0 or r["disposition"] == "FAIL": fail("nonzero or failed rehearsal")

components = r["stubbed_components"]
if "producer" not in components: fail("producer not stubbed")
extras = [item for item in components if item != "producer"]
if not extras:
    if r["disposition"] != "PASS" or components != ["producer"]: fail("invalid PASS components")
else:
    if r["disposition"] != "PASS_WITH_SCOPE_GAP": fail("scope-gap disposition required")
    residuals = re.findall(r"(?mi)^Residual risk:[ \t]*(.*?)[ \t]*$", phase_text)
    missing = [item for item in extras if not any(item in line for line in residuals)]
    if missing: fail(f"residual risk omits {missing}")

stub_raw = os.environ.get("IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB")
if not stub_raw: fail("missing producer stub")
s = P(stub_raw)
if s.resolve() != P(S).resolve(): fail("producer stub differs from phase")
if not s.is_file() or not os.access(s, os.X_OK): fail("invalid producer stub")
if r["stub_identity"] != "sha256:" + hashlib.sha256(s.read_bytes()).hexdigest(): fail("producer identity mismatch")

t = P(launch["terminal_artifact_path"])
if not t.parent.is_dir(): fail("missing terminal parent")

def require_absent_terminal(stage):
    try:
        existing = t.lstat()
    except FileNotFoundError:
        return
    kind = "symlink" if stat.S_ISLNK(existing.st_mode) else "existing owner"
    fail(f"terminal exists {stage}: {kind}")

require_absent_terminal("before wrapper execution")

bridge_fd, bridge_raw = tempfile.mkstemp(prefix=".implementaudit-rehearsal-mediator-bridge-", dir=t.parent)
os.close(bridge_fd)
bridge_path = P(bridge_raw)

mediator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mediator.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mediator.bind(("127.0.0.1", 0))
mediator.listen(1)
mediator.settimeout(2)
mediator_endpoint = f"127.0.0.1:{mediator.getsockname()[1]}"
bridge_path.write_text(f'''#!/usr/bin/env python3
import json,socket
h,p={mediator_endpoint!r}.rsplit(":",1)
with socket.create_connection((h,int(p)),timeout=2) as c:
 c.sendall(b"IMPLEMENTAUDIT_REHEARSAL_MEDIATOR\\n");r=json.loads(c.recv(1024))
raise SystemExit(r["exit_code"])
''', encoding="utf-8")
bridge_path.chmod(0o700)
mediated = {}

def run_bounded_stub():
    try:
        connection, _ = mediator.accept()
        with connection:
            if connection.recv(64) != b"IMPLEMENTAUDIT_REHEARSAL_MEDIATOR\n":
                raise ValueError("invalid mediator request")
            command = ([sys.executable, str(s)] if s.suffix.casefold() == ".py" else [str(s)])
            result = subprocess.run(command, env=stub_env, check=False)
            mediated["exit_code"] = result.returncode
            connection.sendall(json.dumps({"exit_code": result.returncode}).encode("utf-8"))
    except Exception as exc:
        mediated["error"] = str(exc)

mediator_thread = threading.Thread(target=run_bounded_stub, daemon=True)
mediator_thread.start()

safe_parent_keys = {"COMSPEC", "PATH", "PATHEXT", "SYSTEMROOT", "SystemDrive", "SystemRoot", "TEMP", "TMP", "WINDIR"}
run_env = {key: os.environ[key] for key in safe_parent_keys if key in os.environ}
for key in launch["env_keys_present"]:
    run_env[key] = ""
stub_env = dict(run_env)
run_env.update({
    "IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB": str(bridge_path),
})
try:
    completed = subprocess.run(launch["argv"], env=run_env, check=False)
except OSError as exc:
    mediator.close()
    bridge_path.unlink(missing_ok=True)
    fail(f"wrapper could not execute: {exc}")

mediator_thread.join(3)
mediator.close()
bridge_path.unlink(missing_ok=True)
if mediator_thread.is_alive() or "exit_code" not in mediated: fail("wrapper did not traverse mediator")
if "error" in mediated: fail(f"mediator failed: {mediated['error']}")
if mediated["exit_code"] != 0: fail(f"producer exited {mediated['exit_code']}")
if completed.returncode != 0: fail(f"wrapper exited {completed.returncode}")

require_absent_terminal("when publishing the rehearsal terminal")
try:
    terminal_fd = os.open(t, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError: fail("terminal appeared before publication")
with os.fdopen(terminal_fd, "w", encoding="utf-8") as terminal_file:
    terminal_file.write(json.dumps(r, indent=2) + "\n")
published = t.lstat()
if not stat.S_ISREG(published.st_mode) or published.st_nlink != 1: fail("terminal lost exclusive identity")
observed = load_object(str(t), "execution terminal")
if observed != r: fail("terminal receipt mismatch")

print("check-authorization-binding: ok — wrapper transport, mediated stub, and terminal receipt are bound")
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

val() { { grep -iE "^$2:" "$1" || true; } | head -n1 | sed "s/^[^:]*: *//" | tr -d '\r' | sed 's/[[:space:]]*$//'; }

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

drifted=""
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

for k in $(printf '%s' "$binds" | tr ',' ' '); do
  grep -qiE "^param\.$k:" "$inv" \
    || drifted="$drifted $k(bound-but-unsupplied — runtime value unknown; defaults are never implicitly adopted)"
done

[ -z "$drifted" ] || drift "$drifted"
printf 'check-authorization-binding: ok — all consequential parameters bound and in range\n'
