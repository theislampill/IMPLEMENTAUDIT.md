#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$ROOT/scripts/check-genealogy-corpus.py"
HISTORICAL_CHECKER="$ROOT/scripts/check-historical-absorption-baseline.py"

python "$CHECKER" --root "$ROOT"
python "$HISTORICAL_CHECKER" --root "$ROOT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fresh_fixture() {
  rm -rf "$TMP/repo"
  mkdir -p "$TMP/repo/docs/research"
  cp -R "$ROOT/docs/research/genealogy" "$TMP/repo/docs/research/genealogy"
}

fresh_historical_fixture() {
  fresh_fixture
  cp -R "$ROOT/docs/research/implementaudit" "$TMP/repo/docs/research/implementaudit"
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

fresh_historical_fixture
python - "$TMP/repo/docs/research/implementaudit/historical-absorption-baseline/HISTORICAL_ABSORPTION_BASELINE.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["rows"].pop()
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "historical baseline property denominator mismatch" python "$HISTORICAL_CHECKER" --root "$TMP/repo"

fresh_historical_fixture
python - "$TMP/repo/docs/research/implementaudit/historical-absorption-baseline/HISTORICAL_ABSORPTION_BASELINE.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
d["rows"][0]["V0400_CHANGE_DISPOSITION"] = "CHANGED_WITHOUT_BASELINE"
p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_failure "non-deferred v0.4 disposition" python "$HISTORICAL_CHECKER" --root "$TMP/repo"

fresh_fixture
python - "$TMP/fake-package.zip" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], "w") as archive:
    archive.writestr("docs/research/genealogy/README.md", "must not ship")
PY
expect_failure "genealogy content entered distributable package" python "$CHECKER" --root "$ROOT" --package "$TMP/fake-package.zip"

mkdir -p "$TMP/claims/scripts" \
  "$TMP/claims/docs/research/genealogy/law/evolved-lean/corpus" \
  "$TMP/claims/docs/portal/pages"
cp "$ROOT/scripts/check-public-claim-boundaries.sh" "$TMP/claims/scripts/check-public-claim-boundaries.sh"
cp "$ROOT/docs/portal/pages/research-lineage-s3e.html" \
  "$TMP/claims/docs/portal/pages/research-lineage-s3e.html"
cp "$ROOT/docs/portal/pages/research-lineage-evolved-css.html" \
  "$TMP/claims/docs/portal/pages/research-lineage-evolved-css.html"
cp "$ROOT/docs/portal/pages/reference-index.html" \
  "$TMP/claims/docs/portal/pages/reference-index.html"
cp "$ROOT/README.md" "$TMP/claims/README.md"
printf 'historical discussion of a signed %s\n' 'release' > "$TMP/claims/docs/research/genealogy/law/evolved-lean/corpus/source.md"
bash "$TMP/claims/scripts/check-public-claim-boundaries.sh" >/dev/null

printf 'the current product has a signed %s\n' 'release' > "$TMP/claims/docs/research/genealogy/law/evolved-lean/README.md"
expect_failure "signing claim requires a signature artifact" bash "$TMP/claims/scripts/check-public-claim-boundaries.sh"

corpus_whitespace="$(git check-attr whitespace -- \
  docs/research/genealogy/drf/evolved-distributed-systems-engineering/corpus/EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING_FROZEN_REPORT.md)"
case "$corpus_whitespace" in
  *'whitespace: -trailing-space') ;;
  *) fail "exact frozen corpus is not exempt from trailing-space normalization" ;;
esac

authored_whitespace="$(git check-attr whitespace -- docs/research/genealogy/README.md)"
case "$authored_whitespace" in
  *'whitespace: unspecified') ;;
  *) fail "authored genealogy documentation lost normal whitespace enforcement" ;;
esac

echo "genealogy corpus positive and negative controls: PASS"
