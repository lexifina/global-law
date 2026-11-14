#!/bin/bash
# round-5 fuzz: look at the WSL mirror (read-only)
export PATH="$HOME/.elan/bin:$PATH"
echo "--- lake/lean processes"; pgrep -a lake; pgrep -a lean | cut -c1-200 | head -5
echo "--- mirror"; ls ~/caselaw2 | head -30
du -sh ~/caselaw2/lean-proofs/.lake 2>/dev/null
ls ~/caselaw2/lean-proofs/.lake/build/lib/lean/LegalProofs/CaseLaw2/ 2>/dev/null | grep -c olean
ls -la --time-style=+%H:%M:%S ~/caselaw2/lean-proofs/.lake/build/lib/lean/LegalProofs/CaseLaw2/Run.olean ~/caselaw2/lean-proofs/LegalProofs/CaseLaw2/Run.lean ~/caselaw2/lean-proofs/LegalProofs/CaseLaw2/Certificate.lean
ls -la --time-style=+%H:%M:%S ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/runner/.lake/build/bin/ 2>/dev/null
cat ~/caselaw2/lean-proofs/lakefile.* 2>/dev/null | head -30
cat ~/caselaw2/lean-proofs/lean-toolchain
nproc; free -g | head -2; df -h ~ | tail -1
date +%H:%M:%S
