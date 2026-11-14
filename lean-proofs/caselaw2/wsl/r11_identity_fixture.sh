#!/bin/bash
# round 11 (lean11): run the identity-tie fixture (round11/fixtures/identity) through the compiled runner.
# data/ (with history_identity.tsv) -> certs = expected_certs.tsv, counters = expected_identity_summary.tsv;
# data_noident/ (no table) -> expected_certs_noident.tsv, no identity counter, and every output file byte-identical
# (timing aside) to the section-5.1 binary's output on the same data (~/caselaw2/r11_bin/caselaw2_lean11_s51);
# data_emptyident/ (an empty table) -> every output file byte-identical to data_noident's.
#   usage: r11_identity_fixture.sh        (the runner must be built: wsl/r11_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round11/fixtures/identity
R51=~/caselaw2/r11_bin/caselaw2_lean11_s51
cd $M
rc=0
X=fixtures_r11_identity
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_noident $F/data_emptyident $F/edges $X/
for d in data data_noident data_emptyident; do
  bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $d"; exit 1; }
done
for d in data data_noident; do
  case $d in data) E=$F/expected_certs.tsv ;; *) E=$F/expected_certs_noident.tsv ;; esac
  if cmp -s <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); then
    echo "[$d] certs.tsv = $(basename $E) ($(tail -n +2 $X/out_$d/certs.tsv | wc -l) rows)"
  else echo "[$d] certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); fi
done
if cmp -s <(sort $F/expected_identity_summary.tsv) <(grep '^identity_\|^bad_rows	history_identity' $X/out_data/summary.tsv | sort -u); then
  echo "identity counters = expected_identity_summary.tsv"
else echo "identity counters DIFFER"; rc=1
  diff <(sort $F/expected_identity_summary.tsv) <(grep '^identity_\|^bad_rows	history_identity' $X/out_data/summary.tsv | sort -u); fi
# every other counter of data/ = data_noident's
if cmp -s <(grep -v '_ms	\|^identity_\|^bad_rows	history_identity\|^rows_admitted\|^rows_rejected\|^status_rows\|^hclaim_admitted\|^hclaim_rejected\|^anchored_admitted\|^anchored_rejected\|^bridge_admitted' $X/out_data/summary.tsv) \
          <(grep -v '_ms	\|^rows_admitted\|^rows_rejected\|^status_rows\|^hclaim_admitted\|^hclaim_rejected\|^anchored_admitted\|^anchored_rejected\|^bridge_admitted' $X/out_data_noident/summary.tsv); then
  echo "other counters = data_noident's (verdict-dependent counters aside)"
else echo "other counters DIFFER"; rc=1; diff <(grep -v '_ms	' $X/out_data_noident/summary.tsv) <(grep -v '_ms	' $X/out_data/summary.tsv); fi
n=$(grep -c '^identity_' $X/out_data_noident/summary.tsv); echo "[data_noident] identity counters written: $n"; [ "$n" = 0 ] || rc=1
n=0
for f in $(cd $X/out_data_noident && ls *.tsv); do
  if [ $f = summary.tsv ]; then cmp -s <(grep -v '_ms	' $X/out_data_noident/$f) <(grep -v '_ms	' $X/out_data_emptyident/$f) || { echo "[empty] $f differs"; rc=1; }
  else cmp -s $X/out_data_noident/$f $X/out_data_emptyident/$f || { echo "[empty] $f differs"; rc=1; }; fi; n=$((n+1))
done
echo "empty history_identity.tsv vs none: $n files compared"
# the section-5.1 binary on data_noident: every file byte-identical
O51=$(mkdir -p $X/out51 && realpath $X/out51); DATA=$(realpath $X/data_noident); EDGES=$(realpath $X/edges)
NODES=$(cut -f1 "$DATA/decisions2.tsv" | sort -n | tail -1); NODES=$((NODES + 1))
( cd ~/caselaw2/lean-proofs && for k in 0 1; do $R51 "$DATA" "$EDGES" $k 2 "$O51" $NODES 20261112 > /dev/null || exit 1; done ) || { echo "R51 RUN FAILED"; exit 1; }
O=$X/out_data_noident
cmp -s <(cat $O51/certs-*.tsv | sort) <(tail -n +2 $O/certs.tsv | sort) && echo "[data_noident] certs = the 5.1 binary's" || { echo "[data_noident] certs DIFFER from the 5.1 binary's"; rc=1; }
cmp -s <(cat $O51/summary-*.tsv | grep -v '_ms	') <(grep -v '_ms	' $O/summary.tsv) && echo "[data_noident] summary = the 5.1 binary's" || { echo "[data_noident] summary DIFFERS from the 5.1 binary's"; rc=1; }
cmp -s <(cat $O51/status-*.tsv | sort) <(tail -n +2 $O/status.tsv | sort) && echo "[data_noident] status = the 5.1 binary's" || { echo "[data_noident] status DIFFERS"; rc=1; }
rm -rf $F/out; mkdir -p $F/out; cp $X/out_data/*.tsv $F/out/
echo "FIXTURE rc=$rc"
exit $rc
