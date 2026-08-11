#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

checker="skills/implementaudit/scripts/check-authorization-binding.sh"
reachability="scripts/check-helper-reachability.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
failures=()

python - "$tmp" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
stub = root / "producer-stub.py"
stub.write_text("#!/usr/bin/env python3\nraise SystemExit(23)\n", encoding="utf-8")
stub.chmod(0o755)

def wrapper(name, body):
    path = root / name
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path

# This candidate never invokes its declared producer.  On ada87d it can forge
# the wrapper-visible event path/nonce and thereby falsely pass.
forging = wrapper("forging-wrapper.py", '''import hashlib, json, os, pathlib
stub = pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"])
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(json.dumps({
  "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
  "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"], "exit_code": 0}), encoding="utf-8")
''')
ignoring = wrapper("ignoring-wrapper.py", '''import hashlib, json, os, pathlib, subprocess, sys
stub = pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"])
subprocess.run([sys.executable, stub], check=False)
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(json.dumps({
  "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
  "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"], "exit_code": 0}), encoding="utf-8")
''')
leaking = wrapper("leaking-wrapper.py", '''import hashlib, json, os, pathlib
stub = pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"])
if os.environ.get("HELDOUT_CREDENTIAL_SENTINEL"):
  pathlib.Path(os.environ["IMPLEMENTAUDIT_TEST_INHERITED_MARKER"]).write_text("visible\\n", encoding="utf-8")
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(json.dumps({
  "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
  "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"], "exit_code": 0}), encoding="utf-8")
''')

def canonical_hash(argv, env_keys):
    return hashlib.sha256(json.dumps(
        {"argv": argv, "env_keys_present": sorted(env_keys)},
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def payload(suffix, wrapper_path, argv_suffix="fixture.txt", env_keys=["API_TOKEN", "MODEL"]):
    terminal = root / f"terminal-{suffix}.json"
    argv = [sys.executable, str(wrapper_path), "--input", argv_suffix]
    receipt = {
        "rehearsed_command_hash": canonical_hash(argv, env_keys),
        "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
        "stubbed_components": ["producer"], "env_keys_present": env_keys,
        "terminal_artifact_path": str(terminal), "exit_code": 0,
        "disposition": "PASS", "timestamp": "2026-08-11T12:00:00Z",
    }
    launch = {"argv": argv, "env_keys_present": env_keys,
              "terminal_artifact_path": str(terminal), "launch_records": 1,
              "metered_calls": 0}
    receipt_path, launch_path = root / f"receipt-{suffix}.json", root / f"launch-{suffix}.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    launch_path.write_text(json.dumps(launch), encoding="utf-8")
    return receipt, receipt_path, launch_path

def complete_phase(name, receipt, receipt_path, launch_path):
    base = pathlib.Path("fixtures/run-root-example/phases/phase-1.md").read_text(encoding="utf-8")
    fields = (
        "Scarce resource budget: 1 model-call\n"
        f"Rehearsal receipt: {receipt_path}\nRehearsal launch: {launch_path}\n"
        f"Rehearsal producer stub: {stub}\n"
        f"Rehearsal command hash: {receipt['rehearsed_command_hash']}\n"
        f"Rehearsal terminal artifact: {receipt['terminal_artifact_path']}\n"
        f"Rehearsal environment keys: {','.join(receipt['env_keys_present'])}\n"
    )
    path = root / name
    path.write_text(base.replace("Depends on phases: none\n", "Depends on phases: none\n" + fields), encoding="utf-8")
    return path

forged, forged_receipt, forged_launch = payload("forged", forging)
ignored, ignored_receipt, ignored_launch = payload("ignored", ignoring)
inherited, inherited_receipt, inherited_launch = payload("inherited", leaking)
changed, changed_receipt, changed_launch = payload("changed", forging, "changed-fixture.txt", ["ALT_TOKEN"])
complete_phase("phase-forged.md", forged, forged_receipt, forged_launch)
complete_phase("phase-ignored.md", ignored, ignored_receipt, ignored_launch)
complete_phase("phase-inherited.md", inherited, inherited_receipt, inherited_launch)
PY

heldout_passes() {
  local phase="$1" receipt="$2" launch="$3" marker="${4:-}"
  API_TOKEN=real-api-token MODEL=real-model-token ALT_TOKEN=real-alt-token \
  HELDOUT_CREDENTIAL_SENTINEL=must-not-reach-wrapper \
  IMPLEMENTAUDIT_TEST_INHERITED_MARKER="$marker" \
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$tmp/producer-stub.py" \
  bash "$checker" --phase "$phase" --rehearsal "$receipt" --launch "$launch" \
    >/dev/null 2>&1
}

if heldout_passes "$tmp/phase-forged.md" "$tmp/receipt-forged.json" "$tmp/launch-forged.json"; then
  failures+=("wrapper-forges-wrapper-visible-event-without-stub")
fi
if heldout_passes "$tmp/phase-forged.md" "$tmp/receipt-changed.json" "$tmp/launch-changed.json"; then
  failures+=("self-consistent-changed-argv-env-terminal-pass")
fi
if heldout_passes "$tmp/phase-ignored.md" "$tmp/receipt-ignored.json" "$tmp/launch-ignored.json"; then
  failures+=("stub-exit-23-ignored-by-wrapper-passes")
fi
if heldout_passes "$tmp/phase-inherited.md" "$tmp/receipt-inherited.json" "$tmp/launch-inherited.json" "$tmp/inherited-marker" \
    && [ -f "$tmp/inherited-marker" ]; then
  failures+=("undeclared-credential-sentinel-reaches-wrapper")
fi

candidate="$tmp/reachability"
mkdir -p "$candidate/scripts"
cp -R skills "$candidate/skills"
cp scripts/build-release-asset.sh "$candidate/scripts/build-release-asset.sh"
sed -i 's/--rehearsal)/--receipt)/' \
  "$candidate/skills/implementaudit/scripts/check-authorization-binding.sh"
cat >>"$candidate/skills/implementaudit/scripts/check-authorization-binding.sh" <<'EOF'
cat <<'INERT_MODE'
--phase)
--rehearsal)
--launch)
INERT_MODE
EOF
if bash "$reachability" --repo-root "$candidate" >/dev/null 2>&1; then
  failures+=("inert-heredoc-literal-counts-as-parser-arm")
fi

if ! grep -Fqx \
  'helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|<phase> <receipt> <launch>|failed-rehearsal-blocks-launch|scripts/validate-phase.sh' \
  skills/implementaudit/references/repo-state-comparison.md; then
  failures+=("rehearsal-route-is-generic-prose-and-direct-test-only")
fi

if [ "${#failures[@]}" -gt 0 ]; then
  printf 'r11-r30-review-heldouts: GAP-REVISE reproduced: %s\n' "${failures[*]}" >&2
  exit 1
fi
printf 'r11-r30-review-heldouts: ok\n'
