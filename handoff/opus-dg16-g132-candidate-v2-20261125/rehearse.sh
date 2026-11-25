set -eu
R=/home/agent/opus-tmp/g132v2-reh
rm -rf "$R"; mkdir -p "$R"
cp -r /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/wt-g132v2/qualification/dg16-r5-g1-hosted-episode "$R/episode"
find "$R/episode" -type f -exec chmod 0644 {} +; find "$R/episode" -type d -exec chmod 0755 {} +
cp /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/g132gen2/sender_rehearsal_v2.py "$R/sender_rehearsal_v2.py"
id; cd /
env -i HOME=/home/agent PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3.12 -I -B "$R/sender_rehearsal_v2.py" "$R/episode" "$R/scratch"
rc=$?
rm -rf "$R"; echo "cleaned rc=$rc"
