#!/bin/bash
# lean9: copy the batch-2 staging tree (built and checked in ~/caselaw2/b2) into the Windows Lean tree.
# Run only after section 4's LEAN_READY was written and then removed (the tree is being edited).
set -e
S=~/Documents/us-caselaw-lean-work/caselaw-lean-2/round9/agents/lean9/b2/tree
LP=~/Documents/global-law-lean/lean-proofs
[ ! -f ~/Documents/us-caselaw-lean-work/caselaw-lean-2/round9/LEAN_READY ] || { echo "LEAN_READY present: remove it first"; exit 1; }
for f in LegalProofs/CaseLaw2/Certificate.lean LegalProofs/CaseLaw2/Examples.lean LegalProofs/CaseLaw2/Mutants.lean \
         LegalProofs/CaseLaw2/Run.lean LegalProofs/CaseLaw2/CueTable.lean LegalProofs/CaseLaw2/Spec/AuthorityThms.lean \
         tools/caselaw2/cues/cue_table.json tools/caselaw2/cues/gen_cues.py tools/caselaw2/reader/cue_table.py; do
  cp -p $S/$f $LP/$f
  echo "copied $f"
done
cd $LP && python -X utf8 tools/caselaw2/cues/gen_cues.py --check --skip-ref && echo "generated files current"
