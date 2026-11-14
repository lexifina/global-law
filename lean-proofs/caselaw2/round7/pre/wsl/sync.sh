#!/bin/bash
# Run INSIDE WSL Ubuntu: copy the Windows source of truth into the WSL filesystem (fast builds and runs).
#   wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/sync.sh [code|data|all]'
# Layout mirrors Windows so relative paths (runner/lakefile.toml -> ../../../global-law-lean/lean-proofs) hold:
#   ~/caselaw2/lean-proofs                                  (global-law-lean/lean-proofs is a symlink to it)
#   ~/caselaw2/us-caselaw-lean-work/{caselaw-lean-2,lean-in-v3,graph}
set -e
W=/mnt/c/Users/$USER/Documents
R=~/caselaw2
WHAT=${1:-code}
mkdir -p $R/lean-proofs $R/global-law-lean $R/us-caselaw-lean-work/caselaw-lean-2 $R/us-caselaw-lean-work/lean-in-v3 $R/us-caselaw-lean-work/graph
[ -e $R/global-law-lean/lean-proofs ] || ln -s ../lean-proofs $R/global-law-lean/lean-proofs
# the tools address the work as ~/Documents/...: in WSL that is this mirror
[ -e ~/Documents ] || ln -s $R ~/Documents
C=$R/us-caselaw-lean-work/caselaw-lean-2
if [ "$WHAT" = code ] || [ "$WHAT" = all ]; then
  rsync -a --delete --exclude .lake --exclude data --exclude video --exclude __pycache__ $W/global-law-lean/lean-proofs/ $R/lean-proofs/
  rsync -a --exclude .lake $W/us-caselaw-lean-work/caselaw-lean-2/runner/ $C/runner/
  rsync -a $W/us-caselaw-lean-work/caselaw-lean-2/audit/ $C/audit/
  rsync -a --delete $W/us-caselaw-lean-work/caselaw-lean-2/fixtures/ $C/fixtures/
  rsync -a $W/us-caselaw-lean-work/caselaw-lean-2/wsl/ $C/wsl/
  cp -p $W/us-caselaw-lean-work/caselaw-lean-2/run_lean.sh $C/
  cp -p $W/us-caselaw-lean-work/caselaw-lean-2/STATEMENTS.log $C/ 2>/dev/null || true
fi
if [ "$WHAT" = data ] || [ "$WHAT" = all ]; then
  mkdir -p $C/data
  rsync -a --exclude '*.pre_*.tsv' --exclude '*.v1.tsv' --include '*.tsv' --exclude '*' $W/us-caselaw-lean-work/caselaw-lean-2/data/ $C/data/
  rsync -a --include 'edges-*.tsv' --exclude '*' $W/us-caselaw-lean-work/lean-in-v3/ $R/us-caselaw-lean-work/lean-in-v3/
  wc -l < $W/us-caselaw-lean-work/graph/nodes.tsv > $R/us-caselaw-lean-work/graph/nodes.count
fi
echo SYNCED $WHAT
