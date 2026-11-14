#!/bin/bash
# triage: X, Y, W decision rows + court epochs for every witnessNoStanding universe (read only)
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/r5_drt_a
cd $M
grep 'witnessNoStanding' drt_diff.tsv | grep certs | while IFS=$'\t' read u f a b key va vb; do
  tr=${key#treatment:}
  echo "######## $u $tr lean=$va ref=$vb"
  awk -F'\t' -v t=$tr '$1==t{print "  row: " $1, "Y=" $2, "X=" $3, $4, $5, $6, $7, "expl=" $8}' r$u/data/treatments.tsv
  Y=$(awk -F'\t' -v t=$tr '$1==t{print $2}' r$u/data/treatments.tsv)
  X=$(awk -F'\t' -v t=$tr '$1==t{print $3}' r$u/data/treatments.tsv)
  Wn=$(awk -F'\t' -v t=$tr '$1==t{print $2}' r$u/data/treatment_witness.tsv)
  for n in $X $Y $Wn; do
    awk -F'\t' -v n=$n '$1==n{print "  dec: " $0}' r$u/data/decisions2.tsv | cut -c1-120
    c=$(awk -F'\t' -v n=$n '$1==n{print $2}' r$u/data/decisions2.tsv)
    awk -F'\t' -v c=$c '$1==c{print "     court: " $0}' r$u/data/courts2.tsv | cut -c1-200
  done
  echo "  succession:"; sed 's/^/     /' r$u/data/succession.tsv
  grep -h "inferred\|$tr" r$u/diff.tsv | sed 's/^/  diff: /'
done
echo "######## header courts2"; head -3 r73028/data/courts2.tsv
