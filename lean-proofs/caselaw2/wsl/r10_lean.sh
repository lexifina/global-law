#!/bin/bash
# round 10 (lean10 agent): sync the Windows tree into the WSL mirror and build Lean targets, errors only.
#   usage: r10_lean.sh <lake target> ...      e.g. r10_lean.sh LegalProofs.CaseLaw2.Certificate
#          r10_lean.sh all                    LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run and the native runner
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null || { echo SYNC FAILED; exit 1; }
T="$*"; [ "$T" = all ] && T="LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run"
cd ~/caselaw2/lean-proofs
rc=0
lake build $T > ~/caselaw2/r10l_build.log 2>&1 || rc=1
grep -v '^✔\|^ℹ\|^⚠\|deprecated\|^trace\|linter\|^Note: This linter\|^Hint\|Omit it from\|\[apply\]' ~/caselaw2/r10l_build.log | grep -v '^\s*$' | cut -c1-400 | head -${LINES_MAX:-120}
if [ $rc = 0 ] && [ "$*" = all ]; then
  (cd $M/runner && lake build caselaw2 > ~/caselaw2/r10l_build_runner.log 2>&1) || { tail -30 ~/caselaw2/r10l_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
  ls -la $M/runner/.lake/build/bin/caselaw2
fi
[ $rc = 0 ] && echo BUILD OK || echo BUILD FAILED
exit $rc
