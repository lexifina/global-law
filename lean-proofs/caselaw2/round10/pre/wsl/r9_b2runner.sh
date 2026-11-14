#!/bin/bash
# round 9 (lean9): build the runner against the batch-2 staging copy (~/caselaw2/b2) and run the batch-2 fixture and
# the zone fixture with it, without touching the main mirror.
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
B=~/caselaw2/b2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
C=$B/us-caselaw-lean-work/caselaw-lean-2
mkdir -p $B/global-law-lean $C
[ -e $B/global-law-lean/lean-proofs ] || ln -s ../lean-proofs $B/global-law-lean/lean-proofs
rsync -a --exclude .lake $M/runner/ $C/runner/
cp -p $M/run_lean.sh $C/
mkdir -p $B/us-caselaw-lean-work/graph; cp -p ~/caselaw2/us-caselaw-lean-work/graph/nodes.count $B/us-caselaw-lean-work/graph/
(cd $C/runner && lake build caselaw2 > ~/caselaw2/b2_runner.log 2>&1) || { tail -20 ~/caselaw2/b2_runner.log; echo RUNNER BUILD FAILED; exit 1; }
echo "staging runner sha1 $(sha1sum < $C/runner/.lake/build/bin/caselaw2 | cut -c1-40)"
cd $C
F=$W/round9/fixtures/farimplicit
X=fx_farimplicit; rm -rf $X; mkdir -p $X; cp -r $F/data $F/data_noclaim $F/edges $X/
rc=0
for d in data data_noclaim; do
  bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $d"; exit 1; }
  E=$F/expected_certs.tsv; [ $d = data_noclaim ] && E=$F/expected_certs_noclaim.tsv
  if cmp -s <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); then echo "[$d] certs = $(basename $E)"
  else echo "[$d] certs DIFFER"; rc=1; diff <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); fi
done
cut -f1-4 $X/out_data/classes.tsv
awk -F'\t' '$1==7' $X/out_data/status.tsv | cut -f1-7 | head -5
grep -h '^atRisk' $X/out_data/findings.tsv | cut -f1-3,5 | sort | uniq -c | head
echo "rc=$rc"
