#!/bin/bash
# round 11 (lean11; copy of r10_tbridge_fixture.sh that writes nothing into round10/): run the trial-bridge fixture (round10/fixtures/tbridge) through the compiled runner.
# data/ (claims + history_tbridge.tsv) -> certs = expected_certs.tsv, counters = expected_tbridge_summary.tsv;
# data_notable/ (claims, no table) -> expected_certs_notable.tsv, no tbridge counter;
# data_noclaim/ (no claim line, no table) -> expected_certs_noclaim.tsv, no tbridge counter, and every output file
# byte-identical (timing aside) to the frozen round-9 binary's output on the same data (~/caselaw2/r10_bin/caselaw2_r9v9c).
#   usage: r10_tbridge_fixture.sh        (the runner must be built: wsl/r10_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round10/fixtures/tbridge
R9=~/caselaw2/r10_bin/caselaw2_r9v9c
cd $M
rc=0
X=fixtures_r11c_tbridge
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_noclaim $F/data_notable $F/edges $X/
for d in data data_noclaim data_notable; do
  bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $d"; exit 1; }
done
for d in data data_noclaim data_notable; do
  case $d in data) E=$F/expected_certs.tsv ;; data_noclaim) E=$F/expected_certs_noclaim.tsv ;; *) E=$F/expected_certs_notable.tsv ;; esac
  if cmp -s <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); then
    echo "[$d] certs.tsv = $(basename $E) ($(tail -n +2 $X/out_$d/certs.tsv | wc -l) rows)"
  else echo "[$d] certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); fi
done
if cmp -s <(sort $F/expected_tbridge_summary.tsv) <(grep '^tbridge_\|^bad_rows	history_tbridge' $X/out_data/summary.tsv | sort -u); then
  echo "tbridge counters = expected_tbridge_summary.tsv"
else echo "tbridge counters DIFFER"; rc=1
  diff <(sort $F/expected_tbridge_summary.tsv) <(grep '^tbridge_\|^bad_rows	history_tbridge' $X/out_data/summary.tsv | sort -u); fi
for d in data_noclaim data_notable; do
  n=$(grep -c '^tbridge_' $X/out_$d/summary.tsv); echo "[$d] tbridge counters written: $n"; [ "$n" = 0 ] || rc=1
done
# the frozen round-9 binary on data_noclaim: every file byte-identical
O9=$(mkdir -p $X/out9 && realpath $X/out9); DATA=$(realpath $X/data_noclaim); EDGES=$(realpath $X/edges)
NODES=$(cut -f1 "$DATA/decisions2.tsv" | sort -n | tail -1); NODES=$((NODES + 1))
( cd ~/caselaw2/lean-proofs && for k in 0 1; do $R9 "$DATA" "$EDGES" $k 2 "$O9" $NODES 20261112 > /dev/null || exit 1; done ) || { echo "R9 RUN FAILED"; exit 1; }
O=$X/out_data_noclaim
cmp -s <(cat $O9/certs-*.tsv | sort) <(tail -n +2 $O/certs.tsv | sort) && echo "[data_noclaim] certs = the round-9 binary's" || { echo "[data_noclaim] certs DIFFER from the round-9 binary's"; rc=1; diff <(cat $O9/certs-*.tsv | sort) <(tail -n +2 $O/certs.tsv | sort); }
cmp -s <(cat $O9/summary-*.tsv | grep -v '_ms	') <(grep -v '_ms	' $O/summary.tsv) && echo "[data_noclaim] summary = the round-9 binary's" || { echo "[data_noclaim] summary DIFFERS from the round-9 binary's"; rc=1; }
cmp -s <(cat $O9/status-*.tsv | sort) <(tail -n +2 $O/status.tsv | sort) && echo "[data_noclaim] status = the round-9 binary's" || { echo "[data_noclaim] status DIFFERS"; rc=1; }
echo "FIXTURE rc=$rc"
exit $rc
