set -u
D=/home/agent/opus-tmp/g132v2-prov; rm -rf $D; mkdir -p $D/pkg $D/code
cp /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/review-g132/dl/git.deb $D/pkg/; cp /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/g132gen2/check_provision_v2.py $D/code/; cp /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/wt-g132v2/.github/workflows/dg16-r5-g1-hosted-episode.yml $D/pkg/wf.json
cd /
env -i HOME=/home/agent PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3.12 -I -B $D/code/check_provision_v2.py $D/pkg/git.deb $D/pkg/wf.json; echo rc=$?
echo '--- bash dry run of the step body (stops before install)'
bash /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/g132gen2/dryrun.sh
echo '--- negative: wrong tree digest'
bash /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/g132gen2/dryrun.sh 0000000000000000000000000000000000000000000000000000000000000000 2>&1 | tail -2
rm -rf $D /home/agent/opus-tmp/g132v2-dry
