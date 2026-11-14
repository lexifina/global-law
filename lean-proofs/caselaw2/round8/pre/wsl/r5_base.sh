#!/bin/bash
# round 5: baseline identity. Build everything, run the new runner on the round-4 data (no treatment_class.tsv)
# and compare byte for byte with the round-4 final output (difftest/real20/lean in the WSL mirror).
#   usage: r5_base.sh [data-dir relative to the mirror's caselaw-lean-2, default data_r4]
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/lean-proofs && lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run > ~/caselaw2/r5_build.log 2>&1 || { grep -A12 '^error' ~/caselaw2/r5_build.log | head -60; echo BUILD FAILED; exit 1; }
cd $M/runner && lake build caselaw2 > ~/caselaw2/r5_build_runner.log 2>&1 || { tail -30 ~/caselaw2/r5_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
cd $M
D=${1:-data_r4}
if [ ! -d $D ]; then
  # the round-4 data: the mirror's data/ as it stood at the round-4 final run (no file has changed since), frozen here
  mkdir -p $D && cp -p data/*.tsv $D/ && rm -f $D/treatment_class.tsv
fi
ls $D | wc -l; [ -f $D/treatment_class.tsv ] && echo "WARNING: class table present in $D"
rm -rf difftest/r5_base; mkdir -p difftest/r5_base
( time PAR=8 bash run_lean.sh 8 $D ../lean-in-v3 difftest/r5_base/lean ) > difftest/r5_base/lean.log 2>&1
tail -4 difftest/r5_base/lean.log
rc=0
for f in status findings certs splits status_lines horty; do
  if cmp -s <(sort difftest/real20/lean/$f.tsv) <(sort difftest/r5_base/lean/$f.tsv); then echo "IDENTICAL(sorted) $f $(wc -l < difftest/r5_base/lean/$f.tsv)"; else echo "DIFFERENT $f"; rc=1; diff <(sort difftest/real20/lean/$f.tsv) <(sort difftest/r5_base/lean/$f.tsv) | head -8; fi
  cmp -s difftest/real20/lean/$f.tsv difftest/r5_base/lean/$f.tsv && echo "  byte-identical $f"
done
ls difftest/r5_base/lean/
grep -v 'ms' difftest/real20/lean/summary.tsv | sort > /tmp/s4; grep -v 'ms' difftest/r5_base/lean/summary.tsv | sort > /tmp/s5; cmp -s /tmp/s4 /tmp/s5 && echo "IDENTICAL summary (without timings)" || { echo DIFFERENT summary; diff /tmp/s4 /tmp/s5 | head; }
echo "BASE rc=$rc"
