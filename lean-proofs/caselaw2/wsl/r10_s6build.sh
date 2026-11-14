#!/bin/bash
# round 10 (lean10): build the Windows Lean tree's CaseLaw2 in a SEPARATE WSL copy ~/caselaw2/s6/lean-proofs (made
# once from the mirror ~/caselaw2/lean-proofs, .lake included), without touching the mirror (no wsl/sync.sh), so the
# section-4 gates that read the mirror are not disturbed. Errors only.
#   usage: r10_s6build.sh [targets]     default LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run
export PATH="$HOME/.elan/bin:$PATH"
WLP=/mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs
S=~/caselaw2/s6/lean-proofs
if [ ! -d $S ]; then mkdir -p ~/caselaw2/s6 && cp -a ~/caselaw2/lean-proofs $S; fi
rsync -a --delete $WLP/LegalProofs/CaseLaw2/ $S/LegalProofs/CaseLaw2/
cp -p $WLP/LegalProofs/CaseLaw2.lean $S/LegalProofs/
T="${*:-LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run}"
cd $S
rc=0
lake build $T > ~/caselaw2/s6/build.log 2>&1 || rc=1
grep -v '^✔\|^ℹ\|^⚠\|deprecated\|^trace\|linter\|^Note: This linter\|^Hint\|Omit it from\|\[apply\]\|̵\|̲' ~/caselaw2/s6/build.log | grep -v '^\s*$' | grep -v '^ *("\|^ *\[("' | cut -c1-300 | head -${LINES_MAX:-80}
[ $rc = 0 ] && echo BUILD OK || echo BUILD FAILED
exit $rc
