#!/bin/bash
# round 2: compare two Lean output directories file by file (sorted rows). usage: r2_cmp.sh <dirA> <dirB>
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
for f in status findings certs splits; do
  sort $1/$f.tsv > /tmp/a.$f; sort $2/$f.tsv > /tmp/b.$f
  echo "$f: only in A $(comm -23 /tmp/a.$f /tmp/b.$f | wc -l), only in B $(comm -13 /tmp/a.$f /tmp/b.$f | wc -l)"
done
echo "--- findings only in A (first 12)"; comm -23 /tmp/a.findings /tmp/b.findings | head -12
echo "--- findings only in B (first 12)"; comm -13 /tmp/a.findings /tmp/b.findings | head -12
echo "--- splits only in A"; comm -23 /tmp/a.splits /tmp/b.splits | head -8
echo "--- splits only in B"; comm -13 /tmp/a.splits /tmp/b.splits | head -8
echo "--- status only in A"; comm -23 /tmp/a.status /tmp/b.status | head -6
echo "--- status only in B"; comm -13 /tmp/a.status /tmp/b.status | head -6
