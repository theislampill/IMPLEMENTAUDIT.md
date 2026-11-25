# G132 v3 whole-sender qualification on the nominated sender host (WSL Ubuntu, user agent), disposable inputs.
# Usage: bash qualify.sh <candidate tree (Windows path under /mnt/c)> <output dir (under /mnt/c)>
# Creates and removes only /home/agent/opus-tmp/g132v3-q-<pid>. No sudo, no install, no GitHub token, no push.
set -u
TREE=$1; OUT=$2; CODE=$(dirname "$(readlink -f "$0")")
Q=/home/agent/opus-tmp/g132v3-q-$$
mkdir -p "$OUT" "$Q/code" "$Q/src/qualification" "$Q/src/.github/workflows"
cp "$CODE"/qual_*.py "$Q/code/"
cp -r "$TREE/qualification/dg16-r5-g1-hosted-episode" "$Q/src/qualification/"
cp "$TREE/.github/workflows/dg16-r5-g1-hosted-episode.yml" "$Q/src/.github/workflows/"
EP=$Q/src/qualification/dg16-r5-g1-hosted-episode
PY="env -i PATH=/usr/bin:/bin /usr/bin/python3.12 -I -B"
PK=dg16-r5-g1-hosted-episode
cd /
id > "$OUT/00_identity.txt"
echo "== 1. end to end: whole sender in the sandbox, dispatcher stand-in outside"
$PY "$Q/code/qual_setup.py" "$EP" "$Q/p1" "$Q/w1" 424201 --qual > "$OUT/10_setup.json"
$PY "$Q/code/qual_dispatcher.py" "$Q/p1/$PK" "$Q/w1" > "$OUT/11_dispatcher.out" 2>&1 &
DISP=$!
$PY "$Q/code/qual_outer.py" e2e "$Q/p1/$PK" "$Q/w1" > "$OUT/12_e2e_inner.json" 2> "$OUT/12_e2e_outer.stderr"
echo "e2e rc=$?"
wait $DISP; echo "dispatcher rc=$?"
cp "$Q/w1/dispatcher.json" "$OUT/11_dispatcher.json" 2>/dev/null
$PY "$Q/code/qual_outer.py" verify "$Q/p1/$PK" "$Q/w1" > "$OUT/13_verify.json"; echo "verify rc=$?"
echo "== 2. production entry carrier/sender_launch.py (outer + inner), stops at the issued-record seam"
$PY "$Q/code/qual_setup.py" "$EP" "$Q/p2" "$Q/w2" 424202 > "$OUT/20_setup.json"
set -- $($PY -c "import json,sys;c=json.load(open('$Q/w2/config-424202.json'));print(c['context']['run_id'],c['context']['workflow_commit'],c['artifact_id'])")
env -i PATH=/usr/bin:/bin /usr/bin/python3.12 -I -S -B "$Q/p2/$PK/carrier/sender_launch.py" "$1" "$2" "$3" "$Q/w2/request.zip" > "$OUT/21_production.out" 2> "$OUT/21_production.err"
echo "production rc=$?" | tee "$OUT/21_production.rc"
ls -la "$Q/p2" > "$OUT/21_production_placement_after.txt"
echo "== 3. negative controls"
$PY "$Q/code/qual_setup.py" "$EP" "$Q/p3" "$Q/w3" 424203 > /dev/null
$PY "$Q/code/qual_outer.py" negpin "$Q/p3/$PK" "$Q/w3" > "$OUT/30_negpin.json"; echo "negpin rc=$?"
$PY "$Q/code/qual_outer.py" unsandboxed "$Q/p3/$PK" "$Q/w3" > "$OUT/31_unsandboxed.json"; echo "unsandboxed rc=$?"
$PY "$Q/code/qual_setup.py" "$EP" "$Q/p4" "$Q/w4" 424204 --qual > /dev/null
$PY "$Q/code/qual_outer.py" variants "$Q/p4/$PK" "$Q/w4" > "$OUT/32_variants.json"; echo "variants rc=$?"
ls -la "$Q/p3" "$Q/p4" > "$OUT/33_negative_placements_after.txt"
echo "== 4. contrast: the same account unsandboxed"
$PY "$Q/code/qual_outer.py" contrast "$Q/p3/$PK" "$Q/w3" > "$OUT/40_contrast.json"; echo "contrast rc=$?"
echo "harmless public HTTPS HEAD to github.com from OUTSIDE the sandbox (no token):" > "$OUT/41_github_head_outside.txt"
/usr/bin/curl -sS -I --max-time 15 https://github.com/ 2>&1 | head -1 >> "$OUT/41_github_head_outside.txt"
echo "entries under /usr (the only host tree in the sandbox view) whose group is a supplementary group of this account, by group (names withheld):" > "$OUT/42_usr_group_owned.txt"
/usr/bin/find /usr -xdev \( -group adm -o -group cdrom -o -group sudo -o -group dip -o -group plugdev -o -group users -o -group ollama -o -group docker \) -printf '%g %M\n' 2>/dev/null | /usr/bin/sort | /usr/bin/uniq -c >> "$OUT/42_usr_group_owned.txt"
chmod -R u+rwX "$Q"; rm -rf "$Q"; echo "removed $Q: $(test -e "$Q" && echo NO || echo yes)" | tee "$OUT/99_cleanup.txt"
