#!/bin/bash
# round 13 lead: the Lean tree (unchanged this round) still builds in WSL; theorem count; audit.py check.
# Run in WSL: bash /mnt/c/.../round13/lead/lean_check13.sh
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
LP=~/caselaw2/lean-proofs
exec 9> ~/caselaw2/r6_build.lock
flock 9
date '+start %F %T'
bash $W/wsl/sync.sh code
( cd $LP && lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run > ~/caselaw2/r13_build.log 2>&1 ) && echo "LEAN BUILD OK" || { tail -30 ~/caselaw2/r13_build.log; echo "LEAN BUILD FAILED"; }
tail -3 ~/caselaw2/r13_build.log
echo "theorems (^theorem / ^lemma, LegalProofs/CaseLaw2/**.lean):"
grep -rhoE "^(private )?(theorem|lemma) " $LP/LegalProofs/CaseLaw2 | wc -l
echo "sorry / native_decide / axiom occurrences:"
grep -rnwE "sorry|native_decide" $LP/LegalProofs/CaseLaw2 | wc -l
grep -rnE "^axiom " $LP/LegalProofs/CaseLaw2 | wc -l
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2 && python3 audit/audit.py check 2>&1 | tail -5
date '+end %F %T'
