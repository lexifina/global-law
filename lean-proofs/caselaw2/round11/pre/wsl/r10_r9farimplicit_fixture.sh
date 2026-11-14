#!/bin/bash
# round 10 (lean10): copy of wsl/r9_farimplicit_fixture.sh that writes nothing back into round9/ (its out/ copy step removed).
# round 9 (lean9 agent): the batch-2 fixture (round9/fixtures/farimplicit: joinedFar, DESIGN9 section 5;
# implicitReject, section 7) through the compiled runner: data/ -> certs = expected_certs.tsv; data_noclaim/ (no claim
# line) -> certs = expected_certs_noclaim.tsv; the claim column of classes.tsv; no status effect of the soft rows.
#   usage: r9_farimplicit_fixture.sh        (the runner must be built: wsl/r9_lean.sh all)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
F=$W/round9/fixtures/farimplicit
bash $W/wsl/sync.sh code >/dev/null
cd $M
X=fixtures_r10_r9farimplicit
rm -rf $X; mkdir -p $X
cp -r $F/data $F/data_noclaim $F/edges $X/
rc=0
for d in data data_noclaim; do
  bash run_lean.sh 2 $X/$d $X/edges $X/out_$d > $X/lean_$d.log 2>&1 || { tail -20 $X/lean_$d.log; echo "RUN FAILED $d"; exit 1; }
done
for d in data data_noclaim; do
  E=$F/expected_certs.tsv; [ $d = data_noclaim ] && E=$F/expected_certs_noclaim.tsv
  if cmp -s <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); then
    echo "[$d] certs.tsv = $(basename $E) ($(tail -n +2 $X/out_$d/certs.tsv | wc -l) rows)"
  else echo "[$d] certs.tsv DIFFERS"; rc=1; diff <(tail -n +2 $E | sort) <(tail -n +2 $X/out_$d/certs.tsv | sort); fi
done
echo "classes (claims):"; cut -f1-4 $X/out_data/classes.tsv
# the soft rows' target (node 7, Green v. Black) keeps a good status
neg7=$(awk -F'\t' '$1==7 && $6 !~ /^good/' $X/out_data/status.tsv | wc -l)
echo "status rows of node 7 that are not good: $neg7"; [ "$neg7" = 0 ] || rc=1
grep -h '^atRisk' $X/out_data/findings.tsv | cut -f1-3,5 | sort | uniq -c | head
echo "FIXTURE rc=$rc"
exit $rc
