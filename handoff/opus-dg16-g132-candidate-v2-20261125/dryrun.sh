set -u
mkdir -p /home/agent/opus-tmp/g132v2-dry && cd /home/agent/opus-tmp/g132v2-dry
sed "s/^TREE_SHA256=.*/TREE_SHA256=${1:-fa83107dc7b2465aed4fef67808b0cb70ed2c09c74148cdd78c9ba1838965db3}/" /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/g132gen2/provision-inner.sh > inner.sh
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC DRY_RUN=1 DRY_RUN_PACKAGE=/mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/review-g132/dl/git.deb /usr/bin/bash inner.sh; echo "rc=$?"
