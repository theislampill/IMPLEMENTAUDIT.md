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
success_stub = root / "producer-success.py"
success_stub.write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n", encoding="utf-8")
success_stub.chmod(0o755)

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
victim = root / "hardlink-victim.txt"
victim.write_text("do-not-overwrite\n", encoding="utf-8")
hardlinking = wrapper("hardlinking-wrapper.py", f'''import os, pathlib, subprocess, sys
target = pathlib.Path(sys.argv[sys.argv.index("--terminal") + 1])
subprocess.run([sys.executable, os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"]], check=True)
os.link({str(victim)!r}, target)
''')

def canonical_hash(argv, env_keys):
    return hashlib.sha256(json.dumps(
        {"argv": argv, "env_keys_present": sorted(env_keys)},
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def payload(suffix, wrapper_path, argv_suffix="fixture.txt", env_keys=["API_TOKEN", "MODEL"], stub_path=stub, extra_argv=[]):
    terminal = root / f"terminal-{suffix}.json"
    argv = [sys.executable, str(wrapper_path), "--input", argv_suffix] + extra_argv
    receipt = {
        "rehearsed_command_hash": canonical_hash(argv, env_keys),
        "stub_identity": "sha256:" + hashlib.sha256(stub_path.read_bytes()).hexdigest(),
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

def complete_phase(name, receipt, receipt_path, launch_path, stub_path=stub):
    base = pathlib.Path("fixtures/run-root-example/phases/phase-1.md").read_text(encoding="utf-8")
    fields = (
        "Scarce resource budget: 1 model-call\n"
        f"Rehearsal receipt: {receipt_path}\nRehearsal launch: {launch_path}\n"
        f"Rehearsal producer stub: {stub_path}\n"
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
hardlinked, hardlinked_receipt, hardlinked_launch = payload(
    "hardlinked", hardlinking, stub_path=success_stub,
    extra_argv=["--terminal", str(root / "terminal-hardlinked.json")],
)
complete_phase("phase-forged.md", forged, forged_receipt, forged_launch)
complete_phase("phase-ignored.md", ignored, ignored_receipt, ignored_launch)
complete_phase("phase-inherited.md", inherited, inherited_receipt, inherited_launch)
complete_phase("phase-hardlinked.md", hardlinked, hardlinked_receipt, hardlinked_launch, success_stub)
PY

heldout_passes() {
  local phase="$1" receipt="$2" launch="$3" marker="${4:-}" stub_path="${5:-$tmp/producer-stub.py}"
  API_TOKEN=real-api-token MODEL=real-model-token ALT_TOKEN=real-alt-token \
  HELDOUT_CREDENTIAL_SENTINEL=must-not-reach-wrapper \
  IMPLEMENTAUDIT_TEST_INHERITED_MARKER="$marker" \
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$stub_path" \
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
if heldout_passes "$tmp/phase-hardlinked.md" "$tmp/receipt-hardlinked.json" "$tmp/launch-hardlinked.json" "" "$tmp/producer-success.py"; then
  failures+=("hardlink-terminal-alias-passes")
fi
if [ "$(<"$tmp/hardlink-victim.txt")" != "do-not-overwrite" ]; then
  failures+=("hardlink-terminal-alias-overwrites-victim")
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

inert_mediator="$tmp/inert-mediator"
mkdir -p "$inert_mediator/scripts"
cp -R skills "$inert_mediator/skills"
cp scripts/build-release-asset.sh "$inert_mediator/scripts/build-release-asset.sh"
sed -i 's/^[[:space:]]*mediator_thread\.start()/# mediator_thread.start()/' \
  "$inert_mediator/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$inert_mediator" >/dev/null 2>&1; then
  failures+=("inert-mediator-comment-counts-as-transport")
fi

dead_start="$tmp/dead-start"
mkdir -p "$dead_start/scripts"
cp -R skills "$dead_start/skills"
cp scripts/build-release-asset.sh "$dead_start/scripts/build-release-asset.sh"
sed -i 's/^[[:space:]]*mediator_thread\.start()/if False: mediator_thread.start()/' \
  "$dead_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_start" >/dev/null 2>&1; then
  failures+=("dead-start-control-flow-counts-as-transport")
fi

dead_join="$tmp/dead-join"
mkdir -p "$dead_join/scripts"
cp -R skills "$dead_join/skills"
cp scripts/build-release-asset.sh "$dead_join/scripts/build-release-asset.sh"
sed -i 's/^[[:space:]]*mediator_thread\.join(3)/if False: mediator_thread.join(3)/' \
  "$dead_join/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_join" >/dev/null 2>&1; then
  failures+=("dead-join-control-flow-counts-as-transport")
fi

dead_not_start="$tmp/dead-not-start"
mkdir -p "$dead_not_start/scripts"
cp -R skills "$dead_not_start/skills"
cp scripts/build-release-asset.sh "$dead_not_start/scripts/build-release-asset.sh"
sed -i 's/^[[:space:]]*mediator_thread\.start()/if not True: mediator_thread.start()/' \
  "$dead_not_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_not_start" >/dev/null 2>&1; then
  failures+=("dead-not-start-control-flow-counts-as-transport")
fi

dead_not_join="$tmp/dead-not-join"
mkdir -p "$dead_not_join/scripts"
cp -R skills "$dead_not_join/skills"
cp scripts/build-release-asset.sh "$dead_not_join/scripts/build-release-asset.sh"
sed -i 's/^[[:space:]]*mediator_thread\.join(3)/if not True: mediator_thread.join(3)/' \
  "$dead_not_join/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_not_join" >/dev/null 2>&1; then
  failures+=("dead-not-join-control-flow-counts-as-transport")
fi

dead_launch="$tmp/dead-launch"
mkdir -p "$dead_launch/scripts"
cp -R skills "$dead_launch/skills"
cp scripts/build-release-asset.sh "$dead_launch/scripts/build-release-asset.sh"
sed -E -i '/completed = subprocess\.run\(launch/ s/^([[:space:]]*)/\1if False: /' \
  "$dead_launch/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_launch" >/dev/null 2>&1; then
  failures+=("dead-launch-control-flow-counts-as-transport")
fi

dead_not_launch="$tmp/dead-not-launch"
mkdir -p "$dead_not_launch/scripts"
cp -R skills "$dead_not_launch/skills"
cp scripts/build-release-asset.sh "$dead_not_launch/scripts/build-release-asset.sh"
sed -E -i '/completed = subprocess\.run\(launch/ s/^([[:space:]]*)/\1if not True: /' \
  "$dead_not_launch/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_not_launch" >/dev/null 2>&1; then
  failures+=("dead-not-launch-control-flow-counts-as-transport")
fi

dead_not_producer="$tmp/dead-not-producer"
mkdir -p "$dead_not_producer/scripts"
cp -R skills "$dead_not_producer/skills"
cp scripts/build-release-asset.sh "$dead_not_producer/scripts/build-release-asset.sh"
sed -E -i '/result = subprocess\.run\(command/ s/^([[:space:]]*)/\1if not True: /' \
  "$dead_not_producer/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$dead_not_producer" >/dev/null 2>&1; then
  failures+=("dead-not-producer-control-flow-counts-as-transport")
fi

conditional_start="$tmp/conditional-start"
mkdir -p "$conditional_start/scripts"
cp -R skills "$conditional_start/skills"
cp scripts/build-release-asset.sh "$conditional_start/scripts/build-release-asset.sh"
sed -E -i '/mediator_thread\.start\(\)/ s/^([[:space:]]*)/\1if os.environ.get("OPTIONAL_MEDIATOR"): /' \
  "$conditional_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$conditional_start" >/dev/null 2>&1; then
  failures+=("conditional-start-counts-as-mandatory-transport")
fi

conditional_launch="$tmp/conditional-launch"
mkdir -p "$conditional_launch/scripts"
cp -R skills "$conditional_launch/skills"
cp scripts/build-release-asset.sh "$conditional_launch/scripts/build-release-asset.sh"
sed -E -i '/completed = subprocess\.run\(launch/ s/^([[:space:]]*)/\1if os.environ.get("OPTIONAL_LAUNCH"): /' \
  "$conditional_launch/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$conditional_launch" >/dev/null 2>&1; then
  failures+=("conditional-launch-counts-as-mandatory-transport")
fi

terminated_before_start="$tmp/terminated-before-start"
mkdir -p "$terminated_before_start/scripts"
cp -R skills "$terminated_before_start/skills"
cp scripts/build-release-asset.sh "$terminated_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i raise SystemExit(0)' \
  "$terminated_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$terminated_before_start" >/dev/null 2>&1; then
  failures+=("terminated-path-before-start-counts-as-transport")
fi

exited_before_start="$tmp/exited-before-start"
mkdir -p "$exited_before_start/scripts"
cp -R skills "$exited_before_start/skills"
cp scripts/build-release-asset.sh "$exited_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i sys.exit(0)' \
  "$exited_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$exited_before_start" >/dev/null 2>&1; then
  failures+=("system-exit-before-start-counts-as-transport")
fi

terminated_before_launch="$tmp/terminated-before-launch"
mkdir -p "$terminated_before_launch/scripts"
cp -R skills "$terminated_before_launch/skills"
cp scripts/build-release-asset.sh "$terminated_before_launch/scripts/build-release-asset.sh"
sed -i '/completed = subprocess\.run(launch/i\    raise SystemExit(0)' \
  "$terminated_before_launch/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$terminated_before_launch" >/dev/null 2>&1; then
  failures+=("terminated-path-before-launch-counts-as-transport")
fi

reversed_sequence="$tmp/reversed-sequence"
mkdir -p "$reversed_sequence/scripts"
cp -R skills "$reversed_sequence/skills"
cp scripts/build-release-asset.sh "$reversed_sequence/scripts/build-release-asset.sh"
sed -i 's/^mediator_thread\.start()$/IMPLEMENTAUDIT_SWAP_START/' \
  "$reversed_sequence/skills/implementaudit/scripts/check-authorization-binding.sh"
sed -i 's/^mediator_thread\.join(3)$/mediator_thread.start()/' \
  "$reversed_sequence/skills/implementaudit/scripts/check-authorization-binding.sh"
sed -i 's/^IMPLEMENTAUDIT_SWAP_START$/mediator_thread.join(3)/' \
  "$reversed_sequence/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$reversed_sequence" >/dev/null 2>&1; then
  failures+=("reversed-start-join-counts-as-transport")
fi

split_error_path="$tmp/split-error-path"
mkdir -p "$split_error_path/scripts"
cp -R skills "$split_error_path/skills"
cp scripts/build-release-asset.sh "$split_error_path/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.join(3)$/d' \
  "$split_error_path/skills/implementaudit/scripts/check-authorization-binding.sh"
sed -i '/^except OSError as exc:$/a\    mediator_thread.join(3)' \
  "$split_error_path/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$split_error_path" >/dev/null 2>&1; then
  failures+=("normal-start-error-only-join-counts-as-transport")
fi

conditional_expression_start="$tmp/conditional-expression-start"
mkdir -p "$conditional_expression_start/scripts"
cp -R skills "$conditional_expression_start/skills"
cp scripts/build-release-asset.sh "$conditional_expression_start/scripts/build-release-asset.sh"
sed -i 's/^mediator_thread\.start()$/mediator_thread.start() if OPTIONAL else None/' \
  "$conditional_expression_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$conditional_expression_start" >/dev/null 2>&1; then
  failures+=("conditional-expression-start-counts-as-transport")
fi

short_circuit_start="$tmp/short-circuit-start"
mkdir -p "$short_circuit_start/scripts"
cp -R skills "$short_circuit_start/skills"
cp scripts/build-release-asset.sh "$short_circuit_start/scripts/build-release-asset.sh"
sed -i 's/^mediator_thread\.start()$/OPTIONAL and mediator_thread.start()/' \
  "$short_circuit_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$short_circuit_start" >/dev/null 2>&1; then
  failures+=("short-circuit-start-counts-as-transport")
fi

inert_class_start="$tmp/inert-class-start"
mkdir -p "$inert_class_start/scripts"
cp -R skills "$inert_class_start/skills"
cp scripts/build-release-asset.sh "$inert_class_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/c\class DeferredStart:\n    def run(self):\n        mediator_thread.start()' \
  "$inert_class_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$inert_class_start" >/dev/null 2>&1; then
  failures+=("uninstantiated-class-method-counts-as-transport")
fi

asserted_before_start="$tmp/asserted-before-start"
mkdir -p "$asserted_before_start/scripts"
cp -R skills "$asserted_before_start/skills"
cp scripts/build-release-asset.sh "$asserted_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i assert False' \
  "$asserted_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$asserted_before_start" >/dev/null 2>&1; then
  failures+=("assert-false-before-start-counts-as-transport")
fi

conditional_expression_launch="$tmp/conditional-expression-launch"
mkdir -p "$conditional_expression_launch/scripts"
cp -R skills "$conditional_expression_launch/skills"
cp scripts/build-release-asset.sh "$conditional_expression_launch/scripts/build-release-asset.sh"
sed -i 's/completed = subprocess\.run(launch\["argv"\], env=run_env, check=False)/completed = subprocess.run(launch["argv"], env=run_env, check=False) if OPTIONAL else None/' \
  "$conditional_expression_launch/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$conditional_expression_launch" >/dev/null 2>&1; then
  failures+=("conditional-expression-launch-counts-as-transport")
fi

assigned_exit_before_start="$tmp/assigned-exit-before-start"
mkdir -p "$assigned_exit_before_start/scripts"
cp -R skills "$assigned_exit_before_start/skills"
cp scripts/build-release-asset.sh "$assigned_exit_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i terminated = sys.exit(0)' \
  "$assigned_exit_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$assigned_exit_before_start" >/dev/null 2>&1; then
  failures+=("assigned-exit-before-start-counts-as-transport")
fi

exit_test_before_start="$tmp/exit-test-before-start"
mkdir -p "$exit_test_before_start/scripts"
cp -R skills "$exit_test_before_start/skills"
cp scripts/build-release-asset.sh "$exit_test_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i if sys.exit(0): pass' \
  "$exit_test_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$exit_test_before_start" >/dev/null 2>&1; then
  failures+=("terminating-if-test-before-start-counts-as-transport")
fi

empty_assert_before_start="$tmp/empty-assert-before-start"
mkdir -p "$empty_assert_before_start/scripts"
cp -R skills "$empty_assert_before_start/skills"
cp scripts/build-release-asset.sh "$empty_assert_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i assert ()\nassert []' \
  "$empty_assert_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$empty_assert_before_start" >/dev/null 2>&1; then
  failures+=("empty-literal-assert-before-start-counts-as-transport")
fi

assigned_exit_before_producer="$tmp/assigned-exit-before-producer"
mkdir -p "$assigned_exit_before_producer/scripts"
cp -R skills "$assigned_exit_before_producer/skills"
cp scripts/build-release-asset.sh "$assigned_exit_before_producer/scripts/build-release-asset.sh"
sed -i '/result = subprocess\.run(command/i\            terminated = sys.exit(0)' \
  "$assigned_exit_before_producer/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$assigned_exit_before_producer" >/dev/null 2>&1; then
  failures+=("assigned-exit-before-producer-counts-as-live-stub")
fi

short_circuit_compare_start="$tmp/short-circuit-compare-start"
mkdir -p "$short_circuit_compare_start/scripts"
cp -R skills "$short_circuit_compare_start/skills"
cp scripts/build-release-asset.sh "$short_circuit_compare_start/scripts/build-release-asset.sh"
sed -i 's/^mediator_thread\.start()$/0 == 1 == mediator_thread.start()/' \
  "$short_circuit_compare_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$short_circuit_compare_start" >/dev/null 2>&1; then
  failures+=("short-circuit-comparison-start-counts-as-transport")
fi

short_circuit_compare_launch="$tmp/short-circuit-compare-launch"
mkdir -p "$short_circuit_compare_launch/scripts"
cp -R skills "$short_circuit_compare_launch/skills"
cp scripts/build-release-asset.sh "$short_circuit_compare_launch/scripts/build-release-asset.sh"
sed -i 's/completed = subprocess\.run(launch\["argv"\], env=run_env, check=False)/completed = (0 == 1 == subprocess.run(launch["argv"], env=run_env, check=False))/' \
  "$short_circuit_compare_launch/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$short_circuit_compare_launch" >/dev/null 2>&1; then
  failures+=("short-circuit-comparison-launch-counts-as-transport")
fi

short_circuit_compare_producer="$tmp/short-circuit-compare-producer"
mkdir -p "$short_circuit_compare_producer/scripts"
cp -R skills "$short_circuit_compare_producer/skills"
cp scripts/build-release-asset.sh "$short_circuit_compare_producer/scripts/build-release-asset.sh"
sed -i 's/result = subprocess\.run(command, env=stub_env, check=False)/result = (0 == 1 == subprocess.run(command, env=stub_env, check=False))/' \
  "$short_circuit_compare_producer/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$short_circuit_compare_producer" >/dev/null 2>&1; then
  failures+=("short-circuit-comparison-producer-counts-as-live-stub")
fi

constant_assert_before_start="$tmp/constant-assert-before-start"
mkdir -p "$constant_assert_before_start/scripts"
cp -R skills "$constant_assert_before_start/skills"
cp scripts/build-release-asset.sh "$constant_assert_before_start/scripts/build-release-asset.sh"
sed -i '/^mediator_thread\.start()$/i assert 1 - 1\nassert 1 == 1 == 2' \
  "$constant_assert_before_start/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$constant_assert_before_start" >/dev/null 2>&1; then
  failures+=("constant-expression-assert-before-start-counts-as-transport")
fi

if ! grep -Fqx \
  'helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|<phase> <receipt> <launch>|failed-rehearsal-blocks-launch|scripts/validate-phase.sh' \
  skills/implementaudit/references/repo-state-comparison.md; then
  failures+=("rehearsal-route-is-generic-prose-and-direct-test-only")
fi

asset_dir="$tmp/r33-asset"
bash scripts/build-release-asset.sh "$asset_dir" >/dev/null
if [ "$(wc -c < "$asset_dir/IMPLEMENTAUDIT.skill")" -gt 228000 ]; then
  failures+=("r33-package-capacity-over-228000")
fi

if [ "${#failures[@]}" -gt 0 ]; then
  printf 'r11-r30-review-heldouts: GAP-REVISE reproduced: %s\n' "${failures[*]}" >&2
  exit 1
fi
printf 'r11-r30-review-heldouts: ok\n'
