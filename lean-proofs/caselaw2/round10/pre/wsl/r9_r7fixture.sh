#!/bin/bash
# round 9 (lean9 agent; copy of r7_joined_fixture.sh that leaves round7/fixtures/joined/out untouched): run the joined / doctrine / history-claim fixture (round7/fixtures/joined) through the compiled
# runner and compare certs.tsv, the round-7 counters of summary.tsv and the doctrine/operative lines of classes.tsv
# with the expected files; then the same data without the round-7 tables (data_nojoined) against
# expected_certs_nojoined.tsv, with no round-7 counter.
#   usage: r7_joined_fixture.sh        (the runner must be built: wsl/r7_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round7/fixtures/joined
bash $W/wsl/sync.sh code >/dev/null
cd $M
X=fixtures_r9_r7joined
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_nojoined $F/edges $X/
rc=0
bash run_lean.sh 2 $X/data $X/edges $X/out > $X/lean.log 2>&1 || { tail -20 $X/lean.log; echo RUN FAILED; exit 1; }
if cmp -s <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $X/out/certs.tsv | sort); then
  echo "certs.tsv = expected_certs.tsv ($(tail -n +2 $X/out/certs.tsv | wc -l) rows)"
else echo "certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $X/out/certs.tsv | sort); fi
# every shard writes the same counters (each shard checks every row)
if cmp -s <(sort $F/expected_summary.tsv) <(grep '^joined_\|^hclaim_\|^doctrine_\|^bad_rows' $X/out/summary.tsv | sort -u); then
  echo "summary counters = expected_summary.tsv"
else echo "summary counters DIFFER"; rc=1; diff <(sort $F/expected_summary.tsv) <(grep '^joined_\|^hclaim_\|^doctrine_\|^bad_rows' $X/out/summary.tsv | sort -u); fi
if cmp -s <(sort $F/expected_classes.tsv) <(grep -F -f <(cut -f1 $F/expected_classes.tsv) $X/out/classes.tsv | sort); then
  echo "classes.tsv lines = expected_classes.tsv ($(wc -l < $F/expected_classes.tsv) rows)"
else echo "classes.tsv DIFFERS"; rc=1; diff <(sort $F/expected_classes.tsv) <(grep -F -f <(cut -f1 $F/expected_classes.tsv) $X/out/classes.tsv | sort); fi
# effects: the doctrine row's target (node 2) is never negative; the antecedent row's target (node 0) is overruled
echo "status of node 2 (doctrine target): $(awk -F'\t' '$1==2 && $2=="-" {print $4"-"$5":"$6":"$12}' $X/out/status.tsv | tr '\n' ' ')"
echo "status of node 0 (antecedent target): $(awk -F'\t' '$1==0 && $2=="-" {print $4"-"$5":"$6":"$12}' $X/out/status.tsv | tr '\n' ' ')"
awk -F'\t' '$1==2 && $6 ~ /^neg/ {bad=1} END {exit bad}' $X/out/status.tsv || { echo "node 2 NEGATIVE"; rc=1; }
# the same data without the round-7 tables: the round-6 checks, no round-7 counter
bash run_lean.sh 2 $X/data_nojoined $X/edges $X/out_nojoined >> $X/lean.log 2>&1 || { tail -20 $X/lean.log; echo RUN FAILED; exit 1; }
if cmp -s <(tail -n +2 $F/expected_certs_nojoined.tsv | sort) <(tail -n +2 $X/out_nojoined/certs.tsv | sort); then
  echo "without the round-7 tables: certs.tsv = expected_certs_nojoined.tsv"
else echo "without the round-7 tables: certs.tsv DIFFERS"; rc=1
  diff <(tail -n +2 $F/expected_certs_nojoined.tsv | sort) <(tail -n +2 $X/out_nojoined/certs.tsv | sort); fi
n7=$(grep -c '^joined_\|^hclaim_\|^doctrine_' $X/out_nojoined/summary.tsv)
echo "without the round-7 tables: round-7 counters written: $n7"; [ "$n7" = 0 ] || rc=1
echo "FIXTURE rc=$rc"
exit $rc
