#!/bin/bash
# round 2: show a disagreeing universe. usage: r2_show.sh <sweep> <seed> <target> <by>
D=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/$1/r$2
cat $D/diff.tsv
echo "--- decisions"; awk -F'\t' -v a=$3 -v b=$4 '$1==a||$1==b' $D/data/decisions2.tsv | cut -f1-7
echo "--- treatments"; awk -F'\t' -v a=$3 -v b=$4 '$3==a&&$2==b' $D/data/treatments.tsv | cut -f1-8
for c in $(awk -F'\t' -v a=$3 -v b=$4 '$1==a||$1==b{print $2}' $D/data/decisions2.tsv | sort -u); do echo "--- court $c"; awk -F'\t' -v c=$c '$1==c' $D/data/courts2.tsv; awk -F'\t' -v c=$c '$1==c||$2==c' $D/data/adoption.tsv $D/data/succession.tsv; awk -F'\t' -v c=-$c '$1==c' $D/data/system_rules.tsv; done
echo "--- lean status"; awk -F'\t' -v a=$3 '$1==a' $D/lean/status.tsv $D/lean/status_lines.tsv
echo "--- ref status"; awk -F'\t' -v a=$3 '$1==a' $D/ref/status.tsv $D/ref/status_lines.tsv
echo "--- certs"; grep -h "treatment" $D/lean/certs.tsv | head -0
