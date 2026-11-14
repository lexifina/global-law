#!/bin/bash
# triage: the two New Jersey real-data witness rows of r5_it2 (read only)
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
D=$M/data_r5_it2
cd $M
for trip in "4018149 4006682 4061823" "3991335 4086271 4089451"; do
  set -- $trip; Y=$1; X=$2; Wn=$3
  echo "######## Y=$Y X=$X W=$Wn"
  awk -F'\t' -v y=$Y -v x=$X '$2==y && $3==x' $D/treatments.tsv | cut -c1-400
  for n in $X $Y $Wn; do
    awk -F'\t' -v n=$n '$1==n{print "  dec: " $0}' $D/decisions2.tsv | cut -c1-140
    c=$(awk -F'\t' -v n=$n '$1==n{print $2}' $D/decisions2.tsv)
    awk -F'\t' -v c=$c '$1==c{print "     court: " $0}' $D/courts2.tsv | cut -c1-220
    awk -F'\t' -v c=$c '$1==c || $2==c {print "     succ: " $0}' $D/succession.tsv | cut -c1-220
    awk -F'\t' -v c=$c '$1==c || $2==c {print "     adopt: " $0}' $D/adoption.tsv | cut -c1-220
  done
  grep -h "$Y:$X" difftest/r5_it2/lean/certs.tsv difftest/r5_it2/ref/certs.tsv difftest/r5_it2/lean/classes.tsv difftest/r5_it2/ref/classes.tsv 2>/dev/null | cut -c1-300
done
echo "== headers"; head -2 $D/adoption.tsv; head -2 $D/succession.tsv
echo "== NJ rules"; S=$(awk -F'\t' '$4 ~ /Supreme Court of New Jersey/{print $5}' $D/courts2.tsv | head -1); echo "system $S"
awk -F'\t' -v s=$S '$5==s' $D/courts2.tsv | cut -c1-200
awk -F'\t' -v s=$S '$1==s' $D/system_rules.tsv | cut -c1-200
