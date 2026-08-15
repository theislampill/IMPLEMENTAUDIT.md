#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$ROOT/scripts/check-genealogy-corpus.py"

python "$CHECKER" --root "$ROOT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fresh_fixture() {
  rm -rf "$TMP/repo"
  mkdir -p "$TMP/repo/docs/research"
  cp -R "$ROOT/docs/research/genealogy" "$TMP/repo/docs/research/genealogy"
}

expect_failure() {
  local expected="$1"
  shift
  local output
  if output="$("$@" 2>&1)"; then
    echo "expected failure containing: $expected" >&2
    exit 1
  fi
  grep -F "$expected" <<<"$output" >/dev/null || {
    echo "missing expected diagnostic: $expected" >&2
    echo "$output" >&2
    exit 1
  }
}

fresh_fixture
python - "$TMP/repo/docs/research/genealogy/law/evolved-lean/packet/EVOLVED_LEAN_FROZEN_PACKET.zip" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
data = bytearray(p.read_bytes())
data[0] ^= 1
p.write_bytes(data)
PY
expect_failure "packet SHA-256 mismatch" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
rm "$TMP/repo/docs/research/genealogy/law/evolved-lean/corpus/EVOLVED_LEAN_FROZEN_REPORT.md"
expect_failure "missing extracted member" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
rm -rf "$TMP/repo/docs/research/genealogy/css/evolved-systems-safety"
expect_failure "lineage population mismatch" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
rm "$TMP/repo/docs/research/genealogy/css/evolved-systems-safety/README.md"
expect_failure "missing required genealogy documentation" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
python - "$TMP/repo/docs/research/genealogy/PROPERTY_MASTER_INDEX.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["properties"].append(d["properties"][0])
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "duplicate global property key" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
python - "$TMP/repo/docs/research/genealogy/PROPERTY_MASTER_INDEX.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["properties"][0]["source_locator"]["member"] = "DOES_NOT_EXIST.json"
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "dangling source locator" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
python - "$TMP/repo/docs/research/genealogy/CORPUS_MANIFEST.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["files"][0]["path"] = "C:/Users/example/private.txt"
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "absolute local path" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
printf '\nCurrent RXX owner is R51.\n' >> "$TMP/repo/docs/research/genealogy/law/evolved-lean/README.md"
expect_failure "IMPLEMENTAUDIT-specific disposition in neutral README" python "$CHECKER" --root "$TMP/repo"

fresh_fixture
python - "$TMP/fake-package.zip" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], "w") as archive:
    archive.writestr("docs/research/genealogy/README.md", "must not ship")
PY
expect_failure "genealogy content entered distributable package" python "$CHECKER" --root "$ROOT" --package "$TMP/fake-package.zip"

echo "genealogy corpus positive and negative controls: PASS"
