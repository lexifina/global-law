#!/bin/bash
# round 9 (lean9 agent; copy of r8_bridge_fixture.sh that leaves round8/fixtures/bridge/out untouched): run the bridge / anchorWide / oldCircuit fixture (round8/fixtures/bridge) through the compiled
# runner and compare certs.tsv and the round-8 counters of summary.tsv with the expected files; then the same data
# without the round-8 tables and claims (data_nor8) against expected_certs_nor8.tsv, with no round-8 counter.
#   usage: r8_bridge_fixture.sh        (the runner must be built: wsl/r8_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round8/fixtures/bridge
bash $W/wsl/sync.sh code >/dev/null
cd $M
X=fixtures_r9_r8bridge
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_nor8 $F/edges $X/
rc=0
bash run_lean.sh 2 $X/data $X/edges $X/out > $X/lean.log 2>&1 || { tail -20 $X/lean.log; echo RUN FAILED; exit 1; }
if cmp -s <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $X/out/certs.tsv | sort); then
  echo "certs.tsv = expected_certs.tsv ($(tail -n +2 $X/out/certs.tsv | wc -l) rows)"
else echo "certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $X/out/certs.tsv | sort); fi
# every shard writes the same counters (each shard checks every row)
if cmp -s <(sort $F/expected_summary.tsv) <(grep '^bridge_\|^hclaim_\|^anchor\|^bad_rows' $X/out/summary.tsv | sort -u); then
  echo "summary counters = expected_summary.tsv"
else echo "summary counters DIFFER"; rc=1; diff <(sort $F/expected_summary.tsv) <(grep '^bridge_\|^hclaim_\|^anchor\|^bad_rows' $X/out/summary.tsv | sort -u); fi
bash run_lean.sh 2 $X/data_nor8 $X/edges $X/out_nor8 >> $X/lean.log 2>&1 || { tail -20 $X/lean.log; echo RUN FAILED; exit 1; }
if cmp -s <(tail -n +2 $F/expected_certs_nor8.tsv | sort) <(tail -n +2 $X/out_nor8/certs.tsv | sort); then
  echo "without the round-8 tables: certs.tsv = expected_certs_nor8.tsv"
else echo "without the round-8 tables: certs.tsv DIFFERS"; rc=1
  diff <(tail -n +2 $F/expected_certs_nor8.tsv | sort) <(tail -n +2 $X/out_nor8/certs.tsv | sort); fi
n8=$(grep -c '^bridge_\|^hclaim_anchorwide\|^hclaim_oldcircuit' $X/out_nor8/summary.tsv)
echo "without the round-8 tables: round-8 counters written: $n8"; [ "$n8" = 0 ] || rc=1
echo "FIXTURE rc=$rc"
exit $rc
