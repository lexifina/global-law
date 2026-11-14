#!/bin/bash
# Copy the final WSL results back to the Windows work tree: out/ (the Lean outputs) and the difftest summaries.
set -e
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
R=${1:-real17}
mkdir -p $W/out $W/difftest/$R $W/difftest/wsl
cp $M/difftest/$R/lean/*.tsv $W/out/
cp $M/difftest/$R/{diff.txt,diff.tsv,rates.tsv,sample.tsv,lean.log,ref.log} $W/difftest/$R/ 2>/dev/null || true
cp $M/difftest/$R/ref/ref_stats.tsv $W/difftest/$R/ 2>/dev/null || true
for f in regress5 drt5k regress8 drt6b drt6c drt6d fuzz_check fixtures_diff regress12 regress13 drt8 drt9; do cp $M/difftest/$f.txt $W/difftest/wsl/ 2>/dev/null || true; done
ls -la $W/out
