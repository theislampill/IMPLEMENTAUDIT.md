#!/bin/bash
# Build the integration TREE object of an episode in a git clone and compare it with the composition's final_tree.
# Authority NONE. It writes loose objects only (blobs + trees): no commit, no ref, no index of the clone, no network.
#   tree = maintained base tree 9ffbaf95 (commit 205aeab7) + every file under <composition>/public as mode 100644
# usage: integration_tree.sh <git-clone-with-205aeab7> <composition-dir>
# On success prints the tree id and the single command that Root may then run to create the commit object.
set -eu
CLONE=$1; COMP=$(cd "$2" && pwd)
BASE_TREE=9ffbaf95080092bf4a45b8772a97ed16068544a7; PARENT=205aeab7c93299b0666b261485ab5658d8e183de
WANT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['final_tree'])" "$COMP/COMPOSITION.json")
export GIT_INDEX_FILE=$(mktemp -u)
git -C "$CLONE" cat-file -e "$PARENT^{commit}"
[ "$(git -C "$CLONE" rev-parse "$PARENT^{tree}")" = "$BASE_TREE" ] || { echo "BASE_TREE_MISMATCH"; exit 1; }
git -C "$CLONE" read-tree "$BASE_TREE"
N=0
while IFS= read -r -d '' f; do
  rel=${f#"$COMP/public/"}
  blob=$(git -C "$CLONE" hash-object -w --no-filters -- "$f")
  git -C "$CLONE" update-index --add --cacheinfo "100644,$blob,$rel"; N=$((N+1))
done < <(find "$COMP/public" -type f -print0 | sort -z)
TREE=$(git -C "$CLONE" write-tree); rm -f "$GIT_INDEX_FILE"
echo "overlay_files=$N tree=$TREE composition.final_tree=$WANT"
[ "$TREE" = "$WANT" ] || { echo "TREE_MISMATCH"; exit 1; }
echo "TREE_MATCH. Commit object (Root act; creates no ref):"
echo "  git -C $CLONE commit-tree $TREE -p $PARENT -m '<message>'"
