#!/bin/bash
# round 10 (lean10): copy of wsl/r9_zone_fixture.sh that writes nothing back into round9/ (its out/ copy step removed).
# round 9 (lean9 agent): run the part-zone fixture (round9/fixtures/partzone/{j,b}) through the compiled runner.
# For each set: data/ (with part_zone.tsv) -> certs = expected_certs.tsv, zone counters = expected_zone_summary.tsv,
# the earlier counters = data_nozone's except expected_summary_changes.tsv; data_nozone/ (no part_zone.tsv) -> every
# output file byte-identical to the earlier fixture's stored out/ (summary timing lines aside) and no zone counter;
# data_emptyzone/ (an empty part_zone.tsv) -> byte-identical to data_nozone's output.
#   usage: r9_zone_fixture.sh        (the runner must be built: wsl/r9_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null
cd $M
rc=0
same_dir () {  # $1 expected dir, $2 got dir, $3 label
  for f in $(cd $1 && ls *.tsv); do
    if [ ! -f $2/$f ]; then echo "$3 MISSING $f"; rc=1
    elif [ $f = summary.tsv ]; then
      if cmp -s <(grep -v '_ms	' $1/$f) <(grep -v '_ms	' $2/$f); then :; else echo "$3 DIFFERENT $f"; rc=1
        diff <(grep -v '_ms	' $1/$f) <(grep -v '_ms	' $2/$f) | head; fi
    elif ! cmp -s $1/$f $2/$f; then echo "$3 DIFFERENT $f"; rc=1; fi
  done
  for f in $(cd $2 && ls *.tsv); do [ -f $1/$f ] || { echo "$3 EXTRA $f"; rc=1; }; done
  echo "$3: $(cd $2 && ls *.tsv | wc -l) files compared"
}
for S in j b; do
  F=$W/round9/fixtures/partzone/$S
  case $S in j) E=$W/round7/fixtures/joined/out ;; b) E=$W/round8/fixtures/bridge/out ;; esac
  X=fixtures_r10_r9zone_$S
  rm -rf $X; mkdir -p $X
  cp -r $F/data $F/data_nozone $F/data_emptyzone $F/edges $X/
  for d in data data_nozone data_emptyzone; do
    bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $S $d"; exit 1; }
  done
  O=$X/out_data
  if cmp -s <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $O/certs.tsv | sort); then
    echo "[$S] certs.tsv = expected_certs.tsv ($(tail -n +2 $O/certs.tsv | wc -l) rows)"
  else echo "[$S] certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $F/expected_certs.tsv | sort) <(tail -n +2 $O/certs.tsv | sort); fi
  # every shard writes the same counters (each shard checks every row)
  if cmp -s <(sort $F/expected_zone_summary.tsv) <(grep '^zone_\|^bad_rows	part_zone' $O/summary.tsv | sort -u); then
    echo "[$S] zone counters = expected_zone_summary.tsv"
  else echo "[$S] zone counters DIFFER"; rc=1
    diff <(sort $F/expected_zone_summary.tsv) <(grep '^zone_\|^bad_rows	part_zone' $O/summary.tsv | sort -u); fi
  # the other counters: data_nozone's, except the listed changes
  keys=$(cut -f1 $F/expected_summary_changes.tsv | paste -sd'|')
  flt () { grep -v '_ms	\|^zone_\|^bad_rows	part_zone\|^shard\|^asOf\|^status_\|^findings\|^splits\|^edges\|^horty\|^rows_' | grep -Ev "^($keys)	" | sort -u; }
  if cmp -s <(flt < $X/out_data_nozone/summary.tsv) <(flt < $O/summary.tsv) && \
     cmp -s <(sort $F/expected_summary_changes.tsv) <(grep -E "^($keys)	" $O/summary.tsv | sort -u); then
    echo "[$S] earlier counters = data_nozone's but for expected_summary_changes.tsv"
  else echo "[$S] earlier counters DIFFER"; rc=1
    diff <(flt < $X/out_data_nozone/summary.tsv) <(flt < $O/summary.tsv)
    diff <(sort $F/expected_summary_changes.tsv) <(grep -E "^($keys)	" $O/summary.tsv | sort -u); fi
  if [ -f $O/classes.tsv ]; then echo "[$S] classes.tsv vs data_nozone:"; diff $X/out_data_nozone/classes.tsv $O/classes.tsv; fi
  same_dir $E $X/out_data_nozone "[$S] without part_zone.tsv vs the earlier fixture's out/"
  nz=$(grep -c '^zone_' $X/out_data_nozone/summary.tsv)
  echo "[$S] without part_zone.tsv: zone counters written: $nz"; [ "$nz" = 0 ] || rc=1
  same_dir $X/out_data_nozone $X/out_data_emptyzone "[$S] empty part_zone.tsv vs none"
done
echo "FIXTURE rc=$rc"
exit $rc
