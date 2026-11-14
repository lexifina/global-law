#!/bin/bash
# round 5: audit.py check with its own exit code (do.sh's exit code also reflects the copy-back step)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
python3 audit/audit.py check | tail -3
echo "AUDIT_EXIT=${PIPESTATUS[0]}"
grep -rn "sorry\|native_decide\|^axiom \|^ *admit" ~/caselaw2/lean-proofs/LegalProofs/CaseLaw2 --include=*.lean | grep -v "no .sorry\|sorry.,\|no sorry\|\-\-\|/-\|sorry, \|native_decide\` \|Do not\|no \`sorry" | head -5
echo "GREP_DONE"
