#!/bin/bash
# compile LegalProofs/CaseLaw2/Hunt.lean against the built CaseLaw2 oleans (WSL)
export PATH="$HOME/.elan/bin:$PATH"
cd ~/caselaw2/lean-proofs || exit 9
cp /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Hunt.lean LegalProofs/CaseLaw2/Hunt.lean
lake env lean LegalProofs/CaseLaw2/Hunt.lean > "$HOME/hunt_lean.log" 2>&1
rc=$?
echo "rc=$rc lines=$(wc -l < "$HOME/hunt_lean.log") guards=$(grep -c '^#guard' LegalProofs/CaseLaw2/Hunt.lean) theorems=$(grep -c '^theorem' LegalProofs/CaseLaw2/Hunt.lean)"
cut -c1-400 "$HOME/hunt_lean.log" | head -40
