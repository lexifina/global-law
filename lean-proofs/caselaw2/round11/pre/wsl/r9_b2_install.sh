#!/bin/bash
# round 9 (lean9): after the batch-2 tree copy (round9/agents/lean9/apply_batch2.sh), sync the mirror, reuse the
# staging copy's build products (~/caselaw2/b2/lean-proofs/.lake: built from the same sources), build, audit check.
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code > /dev/null || { echo SYNC FAILED; exit 1; }
for f in LegalProofs/CaseLaw2/Certificate.lean LegalProofs/CaseLaw2/Examples.lean LegalProofs/CaseLaw2/Mutants.lean \
         LegalProofs/CaseLaw2/Run.lean LegalProofs/CaseLaw2/CueTable.lean LegalProofs/CaseLaw2/Spec/AuthorityThms.lean \
         LegalProofs/CaseLaw2/Audit.lean LegalProofs/CaseLaw2/Registry.lean; do
  cmp -s ~/caselaw2/lean-proofs/$f ~/caselaw2/b2/lean-proofs/$f || { echo "staging differs from the tree: $f"; exit 1; }
done
rsync -a ~/caselaw2/b2/lean-proofs/.lake/ ~/caselaw2/lean-proofs/.lake/
echo "== build $(date '+%T')"; bash $W/wsl/do.sh build | tail -3
echo "== audit check $(date '+%T')"; bash $W/wsl/do.sh audit check | head -30
