#!/bin/bash
# round 2: holdings on an issue in a disagreeing universe. usage: r2_show2.sh <sweep> <seed> <issue>
D=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/$1/r$2
cat $D/diff.tsv
echo "--- holdings on $3 (id node answer | court date bench)"
awk -F'\t' -v k=$3 '$3==k{print $1"\t"$2"\t"$5}' $D/data/holdings.tsv | while IFS=$'\t' read h n a; do echo "$h $n $a | $(awk -F'\t' -v n=$n '$1==n{print $2, $3, $5}' $D/data/decisions2.tsv) | $(awk -F'\t' -v n=$n '$1==n' $D/lean/status.tsv | cut -f2,4,6 | tr '\t\n' ' ;') | LINES $(awk -F'\t' -v n=$n '$1==n' $D/lean/status_lines.tsv | cut -f2,4,6,12 | tr '\t\n' ' ;')"; done
echo "--- lean splits"; grep -P "\t$3\t" $D/lean/splits.tsv
echo "--- ref conflicts/splits"; grep -P "^$3\t" $D/ref/conflicts_asof.tsv $D/ref/splits_asof.tsv
echo "--- courts"; cut -f1-9 $D/data/courts2.tsv | awk -F'\t' '$1>=1200'
echo "--- adoption"; awk -F'\t' '$1>=1200' $D/data/adoption.tsv
