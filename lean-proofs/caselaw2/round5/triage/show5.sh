#!/bin/bash
# triage: do explicit rows by a non-last-resort successor court (1205 after 1201, replace) over its predecessor's
# decisions occur in the sweep, and what do both sides say? (read only)
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/r5_drt_a
cd $M
n=0
for d in r73*/; do
  u=${d%/}
  grep -q $'^1201\t1205\t[0-9]*\treplace' $u/data/succession.tsv 2>/dev/null || continue
  awk -F'\t' 'NR==FNR{c[$1]=$2; dt[$1]=$3; next} (c[$2]==1205 && c[$3]==1201 && $8==1){print FILENAME, $1, "Y="$2, "X="$3, $5, $6, "xdate="dt[$3], "ydate="dt[$2]}' $u/data/decisions2.tsv $u/data/treatments.tsv > /tmp/triage_s5.$$
  [ -s /tmp/triage_s5.$$ ] || continue
  while read f id y x rest; do
    n=$((n+1))
    [ $n -gt 6 ] && break
    echo "## $u $id $y $x $rest"
    grep -h "^1201\|^1205" $u/data/succession.tsv $u/data/adoption.tsv | cut -c1-80 | sed 's/^/   s\/a: /'
    X=${x#X=}
    grep -P "\t$id\t" $u/lean/certs.tsv | sed 's/^/   lean cert: /'
    grep -P "^$X\t" $u/lean/status.tsv | cut -c1-140 | sed 's/^/   lean st: /'
    grep -P "^$X\t" $u/ref/status.tsv | cut -c1-140 | sed 's/^/   ref  st: /'
  done < /tmp/triage_s5.$$
done
rm -f /tmp/triage_s5.$$
echo "rows shown: $n"
