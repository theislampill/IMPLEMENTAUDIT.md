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

wrapper = root / "forging-wrapper.py"
wrapper.write_text('''#!/usr/bin/env python3
import json, os, pathlib
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_PROOF"]).write_text(
    os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_IDENTITY"] + "\\n", encoding="utf-8")
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_TERMINAL"]).write_text(
    os.environ["IMPLEMENTAUDIT_TEST_RECEIPT"] + "\\n", encoding="utf-8")
if os.environ.get("HELDOUT_CREDENTIAL_SENTINEL"):
    pathlib.Path(os.environ["IMPLEMENTAUDIT_TEST_INHERITED_MARKER"]).write_text("visible\\n", encoding="utf-8")
''', encoding="utf-8")
wrapper.chmod(0o755)

def payload(suffix, argv_suffix="fixture.txt", env_keys=["API_TOKEN", "MODEL"]):
    terminal = root / f"terminal-{suffix}.json"
    argv = [sys.executable, str(wrapper), "--input", argv_suffix]
    command_hash = hashlib.sha256(json.dumps(
        {"argv": argv, "env_keys_present": sorted(env_keys)},
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    receipt = {
        "rehearsed_command_hash": command_hash,
        "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
        "stubbed_components": ["producer"],
        "env_keys_present": env_keys,
        "terminal_artifact_path": str(terminal),
        "exit_code": 0,
        "disposition": "PASS",
        "timestamp": "2026-08-11T12:00:00Z",
    }
    launch = {
        "argv": argv,
        "env_keys_present": env_keys,
        "terminal_artifact_path": str(terminal),
        "launch_records": 1,
        "metered_calls": 0,
    }
    (root / f"receipt-{suffix}.json").write_text(json.dumps(receipt), encoding="utf-8")
    (root / f"launch-{suffix}.json").write_text(json.dumps(launch), encoding="utf-8")
    return receipt

(root / "phase.md").write_text("Scarce resource budget: 1 model-call\nResidual risk: none\n", encoding="utf-8")
for suffix, argv_suffix, keys in (
    ("forged", "fixture.txt", ["API_TOKEN", "MODEL"]),
    ("changed", "changed-fixture.txt", ["ALT_TOKEN"]),
    ("nonzero", "fixture.txt", ["API_TOKEN", "MODEL"]),
    ("inherited", "fixture.txt", ["API_TOKEN", "MODEL"]),
):
    receipt = payload(suffix, argv_suffix, keys)
    (root / f"receipt-env-{suffix}.txt").write_text(json.dumps(receipt), encoding="utf-8")
PY

heldout_passes() {
  local suffix="$1" marker="${2:-}"
  local receipt
  receipt="$(<"$tmp/receipt-env-$suffix.txt")"
  API_TOKEN=real-api-token MODEL=real-model-token ALT_TOKEN=real-alt-token \
  HELDOUT_CREDENTIAL_SENTINEL=must-not-reach-wrapper \
  IMPLEMENTAUDIT_TEST_INHERITED_MARKER="$marker" \
  IMPLEMENTAUDIT_TEST_RECEIPT="$receipt" \
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$tmp/producer-stub.py" \
  bash "$checker" --phase "$tmp/phase.md" \
    --rehearsal "$tmp/receipt-$suffix.json" --launch "$tmp/launch-$suffix.json" \
    >/dev/null 2>&1
}

if heldout_passes forged "$tmp/forged-inherited"; then
  failures+=("wrapper-forges-proof-and-terminal-without-stub")
fi
if heldout_passes changed "$tmp/changed-inherited"; then
  failures+=("self-consistent-changed-argv-env-terminal-pass")
fi
if heldout_passes nonzero "$tmp/nonzero-inherited"; then
  failures+=("stub-exit-23-ignored-by-wrapper-passes")
fi
if heldout_passes inherited "$tmp/inherited-marker" \
    && [ -f "$tmp/inherited-marker" ]; then
  failures+=("undeclared-credential-sentinel-reaches-wrapper")
fi

candidate="$tmp/reachability"
mkdir -p "$candidate/scripts"
cp -R skills "$candidate/skills"
cp scripts/build-release-asset.sh "$candidate/scripts/build-release-asset.sh"
sed -i 's/--rehearsal)/--receipt)/' \
  "$candidate/skills/implementaudit/scripts/check-authorization-binding.sh"
printf '\n# inert --rehearsal literal retained by a comment\n' \
  >>"$candidate/skills/implementaudit/scripts/check-authorization-binding.sh"
if bash "$reachability" --repo-root "$candidate" >/dev/null 2>&1; then
  failures+=("inert-rehearsal-literal-counts-as-implemented-mode")
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
