#!/bin/bash
# usage: gen.sh <checkout-dir> <commit> <tree> <outdir> <pred-slots> <pred-roles>
export PATH=/home/agent/.venv-ia-release/bin:/usr/local/bin:/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1
B=/mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/v03regen
mkdir -p /home/agent/opus-tmp
cd "$B"
/usr/bin/python3 -I -B regen.py --source "$1" --commit "$2" --tree "$3" --out "$4" \
  --predecessor-report-slots "$5" --predecessor-output-roles "$6" \
  --git-dir /mnt/c/Users/theis/AppData/Local/Temp/claude/444e85c66277a305/f388a28a-ca5c-4c89-be28-32fc8ef43b71/scratchpad/adv3/full/src/.git \
  --python /usr/bin/python3 --work /home/agent/opus-tmp
