# v3 checks on the sender host: syntax, host decrypt argv, policy refusal, v2 profile check and v2 provisioning
# dry run against the v3 tree. Usage: bash checks.sh <tree (under /mnt/c)> <git .deb> <output dir>
# Creates and removes only /home/agent/opus-tmp/g132v3-chk-<pid>. Installs nothing; no sudo.
set -u
TREE=$1; DEB=$2; OUT=$3; CODE=$(dirname "$(readlink -f "$0")")
D=/home/agent/opus-tmp/g132v3-chk-$$
mkdir -p "$OUT" "$D/tree/qualification" "$D/tree/.github/workflows" "$D/pkg" "$D/code"
cp -r "$TREE/qualification/dg16-r5-g1-hosted-entry" "$TREE/qualification/dg16-r5-g1-hosted-episode" "$D/tree/qualification/"
cp "$TREE/.github/workflows/dg16-r5-g1-hosted-episode.yml" "$D/tree/.github/workflows/"
find "$D/tree" -type f -exec chmod 0644 {} +; find "$D/tree" -type d -exec chmod 0755 {} +
cp "$CODE"/*.py "$CODE"/qual/*.py "$D/code/"
rm "$D/code/v3_sender_sandbox.py"  # a fragment with @ENTRY@ placeholders; compiled as part of sender_capture.py
PY="env -i PATH=/usr/bin:/bin /usr/bin/python3.12 -I -B"
cd /
$PY "$D/code/check_v3_static.py" "$D/tree" "$D"/code/*.py > "$OUT/check_v3_static.out" 2>&1; echo "static rc=$?" | tee -a "$OUT/check_v3_static.out"
$PY "$D/code/check_profile_v2.py" "$D/tree/qualification/dg16-r5-g1-hosted-episode" > "$OUT/check_profile_v3.out" 2>&1; echo "profile rc=$?" | tee -a "$OUT/check_profile_v3.out"
cp "$DEB" "$D/pkg/git.deb"
$PY "$D/code/check_provision_v2.py" "$D/pkg/git.deb" "$D/tree/.github/workflows/dg16-r5-g1-hosted-episode.yml" > "$OUT/provcheck_v3.out" 2>&1; echo "provision pins rc=$?" | tee -a "$OUT/provcheck_v3.out"
echo '--- bash dry run of the step body (stops before install)' >> "$OUT/provcheck_v3.out"
mkdir -p "$D/dry" && cd "$D/dry"
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC DRY_RUN=1 DRY_RUN_PACKAGE="$D/pkg/git.deb" /usr/bin/bash "$CODE/provision-inner.sh" >> "$OUT/provcheck_v3.out" 2>&1; echo "dry run rc=$?" >> "$OUT/provcheck_v3.out"
cd /
rm -rf "$D"; echo "removed $D: $(test -e "$D" && echo NO || echo yes)" >> "$OUT/provcheck_v3.out"
