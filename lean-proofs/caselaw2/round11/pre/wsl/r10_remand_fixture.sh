#!/bin/bash
# round 10 (lean10 agent): run the remand fixture (round10/fixtures/remand) through the compiled runner.
# data/ (with history_remand.tsv) -> certs = expected_certs.tsv, remand counters = expected_remand_summary.tsv, the
# other counters = data_noremand's (rows_admitted / rows_rejected moved by remand_failed_rows);
# data_noremand/ (no history_remand.tsv) -> certs = expected_certs_noremand.tsv, no remand counter;
# data_emptyremand/ (an empty history_remand.tsv) -> every output file byte-identical to data_noremand's (timing aside).
#   usage: r10_remand_fixture.sh        (the runner must be built: wsl/r10_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round10/fixtures/remand
bash $W/wsl/sync.sh code >/dev/null
cd $M
rc=0
X=fixtures_r10_remand
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_noremand $F/data_emptyremand $F/edges $X/
for d in data data_noremand data_emptyremand; do
  bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $d"; exit 1; }
done
O=$X/out_data
if cmp -s <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $O/certs.tsv | sort); then
  echo "certs.tsv = expected_certs.tsv ($(tail -n +2 $O/certs.tsv | wc -l) rows)"
else echo "certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $O/certs.tsv | sort); fi
# every shard writes the same counters (each shard checks every row)
if cmp -s <(sort $F/expected_remand_summary.tsv) <(grep '^remand_\|^bad_rows	history_remand' $O/summary.tsv | sort -u); then
  echo "remand counters = expected_remand_summary.tsv"
else echo "remand counters DIFFER"; rc=1
  diff <(sort $F/expected_remand_summary.tsv) <(grep '^remand_\|^bad_rows	history_remand' $O/summary.tsv | sort -u); fi
flt () { grep -v '_ms	\|^remand_\|^bad_rows	history_remand\|^rows_' | sort -u; }
if cmp -s <(flt < $X/out_data_noremand/summary.tsv) <(flt < $O/summary.tsv); then
  echo "other counters = data_noremand's"
else echo "other counters DIFFER"; rc=1; diff <(flt < $X/out_data_noremand/summary.tsv) <(flt < $O/summary.tsv); fi
fail=$(grep '^remand_failed_rows' $O/summary.tsv | head -1 | cut -f2)
a0=$(awk -F'\t' '$1=="rows_admitted"{s+=$2} END{print s}' $X/out_data_noremand/summary.tsv)
a1=$(awk -F'\t' '$1=="rows_admitted"{s+=$2} END{print s}' $O/summary.tsv)
sh=$(grep -c '^shard' $O/summary.tsv)
echo "rows_admitted (summed over $sh shards): without $a0, with $a1; remand_failed_rows $fail"
[ $((a0 - a1)) = $((fail * sh)) ] || { echo "rows_admitted delta is not remand_failed_rows per shard"; rc=1; }
if cmp -s <(tail -n +2 $F/expected_certs_noremand.tsv | sort) <(tail -n +2 $X/out_data_noremand/certs.tsv | sort); then
  echo "without history_remand.tsv: certs.tsv = expected_certs_noremand.tsv"
else echo "without history_remand.tsv: certs.tsv DIFFERS"; rc=1
  diff <(tail -n +2 $F/expected_certs_noremand.tsv | sort) <(tail -n +2 $X/out_data_noremand/certs.tsv | sort); fi
nr=$(grep -c '^remand_' $X/out_data_noremand/summary.tsv)
echo "without history_remand.tsv: remand counters written: $nr"; [ "$nr" = 0 ] || rc=1
for f in $(cd $X/out_data_noremand && ls *.tsv); do
  if [ $f = summary.tsv ]; then
    cmp -s <(grep -v '_ms	' $X/out_data_noremand/$f) <(grep -v '_ms	' $X/out_data_emptyremand/$f) || { echo "empty history_remand.tsv: DIFFERENT $f"; rc=1; }
  else cmp -s $X/out_data_noremand/$f $X/out_data_emptyremand/$f || { echo "empty history_remand.tsv: DIFFERENT $f"; rc=1; }; fi
done
[ "$(cd $X/out_data_noremand && ls *.tsv)" = "$(cd $X/out_data_emptyremand && ls *.tsv)" ] || { echo "empty history_remand.tsv: file lists differ"; rc=1; }
echo "empty history_remand.tsv vs none: $(cd $X/out_data_emptyremand && ls *.tsv | wc -l) files compared"
rm -rf $F/out; mkdir -p $F/out; cp $O/*.tsv $F/out/
echo "FIXTURE rc=$rc"
exit $rc
