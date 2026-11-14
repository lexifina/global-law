#!/bin/bash
# strip10.sh <src root> <dst root>: copy universes without their round-10 inputs (history_remand.tsv,
# history_tbridge.tsv, trialBridge claim lines), to test a disagreement against the round-9 binary.
src=$1; dst=$2
rm -rf $dst; mkdir -p $dst
for d in $src/*/; do
  n=$(basename $d)
  mkdir -p $dst/$n
  rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $d $dst/$n/
  rm -f $dst/$n/data/history_remand.tsv $dst/$n/data/history_tbridge.tsv
  [ -f $dst/$n/data/history_claim.tsv ] && grep -v -P '\ttrialBridge(\t|$)' $dst/$n/data/history_claim.tsv > $dst/$n/hc.tmp; [ -f $dst/$n/hc.tmp ] && mv $dst/$n/hc.tmp $dst/$n/data/history_claim.tsv
done
ls $dst | wc -l
