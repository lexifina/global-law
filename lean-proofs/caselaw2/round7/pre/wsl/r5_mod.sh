#!/bin/bash
# round 5: sync the code and build the given Lean modules (default: all of CaseLaw2 + Run), errors only
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/lean-proofs
MODS="${@:-LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run}"
lake build $MODS > ~/caselaw2/r5_build.log 2>&1; rc=$?
grep -v '^✔\|^ℹ\|^⚠\|deprecated\|^Hint\|^trace\|^$\|unused variable\|linter\|^  *\[' ~/caselaw2/r5_build.log | cut -c1-900 | head -${LINES_MAX:-120}
echo "BUILD rc=$rc"
