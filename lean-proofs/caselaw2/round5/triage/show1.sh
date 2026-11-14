#!/bin/bash
# triage: list the (2)/(3) universes of r5_drt_a and show a few of them (read only)
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/r5_drt_a
T=/mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref
cd $M
echo "== drt_diff rows (not recognised/atRiskWitness)"
head -1 drt_diff.tsv
grep -v 'recognised/atRiskWitness\|recognised_rows' drt_diff.tsv | head -60
for u in 73028 73060 73158; do
  echo "######## $u"
  cat r$u/diff.tsv | grep -v 'recognised_rows'
  ls r$u/data
done
