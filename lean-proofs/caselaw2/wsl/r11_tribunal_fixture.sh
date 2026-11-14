#!/bin/bash
# round 11 (lean11): run the anchorTribunal fixture (round11/fixtures/tribunal) through the compiled runner.
# data/ (claims incl. anchorTribunal) -> certs = expected_certs.tsv, history-claim counters = expected_hclaim_summary.tsv;
# data_noclaim/ (no anchorTribunal line) -> expected_certs_noclaim.tsv, no tribunal counter, and every output file
# byte-identical (timing aside) to the frozen round-10 binary's output on the same data (~/caselaw2/r10_bin/run_v10d).
#   usage: r11_tribunal_fixture.sh        (the runner must be built: wsl/r11_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round11/fixtures/tribunal
R10=~/caselaw2/r10_bin/run_v10d
cd $M
rc=0
X=fixtures_r11_tribunal
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_noclaim $F/edges $X/
for d in data data_noclaim; do
  bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $d"; exit 1; }
done
for d in data data_noclaim; do
  case $d in data) E=$F/expected_certs.tsv ;; *) E=$F/expected_certs_noclaim.tsv ;; esac
  if cmp -s <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); then
    echo "[$d] certs.tsv = $(basename $E) ($(tail -n +2 $X/out_$d/certs.tsv | wc -l) rows)"
  else echo "[$d] certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); fi
done
if cmp -s <(sort $F/expected_hclaim_summary.tsv) <(grep '^hclaim_' $X/out_data/summary.tsv | sort -u); then
  echo "hclaim counters = expected_hclaim_summary.tsv"
else echo "hclaim counters DIFFER"; rc=1
  diff <(sort $F/expected_hclaim_summary.tsv) <(grep '^hclaim_' $X/out_data/summary.tsv | sort -u); fi
grep -q '^bad_rows	history_claim' $X/out_data/summary.tsv && { echo "[data] history_claim bad rows reported"; rc=1; }
n=$(grep -c '^hclaim_anchortribunal' $X/out_data_noclaim/summary.tsv); echo "[data_noclaim] tribunal counters written: $n"; [ "$n" = 0 ] || rc=1
# the frozen round-10 binary on data_noclaim: every file byte-identical
O10=$(mkdir -p $X/out10 && realpath $X/out10); DATA=$(realpath $X/data_noclaim); EDGES=$(realpath $X/edges)
NODES=$(cut -f1 "$DATA/decisions2.tsv" | sort -n | tail -1); NODES=$((NODES + 1))
( cd ~/caselaw2/lean-proofs && for k in 0 1; do $R10 "$DATA" "$EDGES" $k 2 "$O10" $NODES 20261112 > /dev/null || exit 1; done ) || { echo "R10 RUN FAILED"; exit 1; }
O=$X/out_data_noclaim
cmp -s <(cat $O10/certs-*.tsv | sort) <(tail -n +2 $O/certs.tsv | sort) && echo "[data_noclaim] certs = the round-10 binary's" || { echo "[data_noclaim] certs DIFFER from the round-10 binary's"; rc=1; diff <(cat $O10/certs-*.tsv | sort) <(tail -n +2 $O/certs.tsv | sort); }
cmp -s <(cat $O10/summary-*.tsv | grep -v '_ms	') <(grep -v '_ms	' $O/summary.tsv) && echo "[data_noclaim] summary = the round-10 binary's" || { echo "[data_noclaim] summary DIFFERS from the round-10 binary's"; rc=1; }
cmp -s <(cat $O10/status-*.tsv | sort) <(tail -n +2 $O/status.tsv | sort) && echo "[data_noclaim] status = the round-10 binary's" || { echo "[data_noclaim] status DIFFERS"; rc=1; }
rm -rf $F/out; mkdir -p $F/out; cp $X/out_data/*.tsv $F/out/
echo "FIXTURE rc=$rc"
exit $rc
