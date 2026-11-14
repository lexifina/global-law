#!/bin/bash
# round 6 (lean agent): run the anchored-history fixture (round6/history/fixtures/anchor) through the compiled runner
# and compare certs.tsv and the anchor counters of summary.tsv with the expected files.
#   usage: r6_anchor_fixture.sh        (the runner must be built: wsl/r6_lean_base.sh or run_lean_wsl.sh build)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round6/history/fixtures/anchor
bash $W/wsl/sync.sh code >/dev/null
cd $M
rm -rf fixtures_r6_anchor; mkdir -p fixtures_r6_anchor
cp -r $F/data $F/edges fixtures_r6_anchor/
rc=0
bash run_lean.sh 2 fixtures_r6_anchor/data fixtures_r6_anchor/edges fixtures_r6_anchor/out > fixtures_r6_anchor/lean.log 2>&1 || { tail -20 fixtures_r6_anchor/lean.log; echo RUN FAILED; exit 1; }
if cmp -s <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 fixtures_r6_anchor/out/certs.tsv | sort); then
  echo "certs.tsv = expected_certs.tsv ($(tail -n +2 fixtures_r6_anchor/out/certs.tsv | wc -l) rows)"
else echo "certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 fixtures_r6_anchor/out/certs.tsv | sort); fi
# every shard writes the same counters (each shard checks every row)
if cmp -s <(sort $F/expected_summary.tsv) <(grep 'anchor\|bad_rows' fixtures_r6_anchor/out/summary.tsv | sort -u); then
  echo "summary counters = expected_summary.tsv"
else echo "summary counters DIFFER"; rc=1; diff <(sort $F/expected_summary.tsv) <(grep 'anchor\|bad_rows' fixtures_r6_anchor/out/summary.tsv | sort -u); fi
# the same data without the anchor table: every anchored row falls back to the one-quote check
rm -rf fixtures_r6_anchor/data_noanchor; cp -r fixtures_r6_anchor/data fixtures_r6_anchor/data_noanchor; rm fixtures_r6_anchor/data_noanchor/history_anchor.tsv
bash run_lean.sh 2 fixtures_r6_anchor/data_noanchor fixtures_r6_anchor/edges fixtures_r6_anchor/out_noanchor >> fixtures_r6_anchor/lean.log 2>&1
echo "without history_anchor.tsv: $(tail -n +2 fixtures_r6_anchor/out_noanchor/certs.tsv | cut -f3 | sort | uniq -c | tr '\n' ' ')"
grep -c 'anchor' fixtures_r6_anchor/out_noanchor/summary.tsv
mkdir -p $F/out $F/out_noanchor
cp fixtures_r6_anchor/out/*.tsv $F/out/; cp fixtures_r6_anchor/out_noanchor/*.tsv $F/out_noanchor/
echo "FIXTURE rc=$rc"
exit $rc
