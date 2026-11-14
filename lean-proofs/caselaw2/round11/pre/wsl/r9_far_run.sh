#!/bin/bash
# round 9 (lean9): real-data check of batch 2 on state9's claimed rows: after r9_final2's v8e run, run stage
# round9/stage/lean9_far (v8e + state9 B/cert_far 52 joinedFar rows + A/cert2_claim 21 implicitReject rows) with the
# batch-2 binary (PAR=4) and list the verdicts of the claimed rows and every other verdict change against v8e.
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
until grep -q '^rc=' ~/caselaw2/r9_final2_logs/v8e.log 2>/dev/null; do sleep 10; done
echo "start $(date '+%T')"
PAR=4 NOBUILD=1 R9BIN=$HOME/caselaw2/r9_bin/caselaw2_lean9 bash $W/wsl/r9_run.sh lean9_far > ~/caselaw2/r9_far.log 2>&1 || { tail -20 ~/caselaw2/r9_far.log; exit 1; }
O=$W/round9/out/lean9_far
head -1 $O/RUN.txt
echo "claimed rows (treatment_class claims joinedFar / implicitReject):"
cut -f1,2 $W/round9/stage/lean9_far/treatment_class.tsv | awk -F'\t' '$2=="joinedFar"||$2=="implicitReject"{print $1"\t"$2}' | sort > /tmp/lean9_claims.tsv
awk -F'\t' 'NR>1{print $2"\t"$3"\t"$4}' $O/certs.tsv | sort > /tmp/lean9_certs.tsv
join -t $'\t' /tmp/lean9_claims.tsv /tmp/lean9_certs.tsv | awk -F'\t' '{print $2" "$3" "$4}' | sort | uniq -c
echo "rows of v8e whose verdict changed:"
join -t $'\t' <(awk -F'\t' 'NR>1{print $2"\t"$3"\t"$4}' $W/round8/out/v8e/certs.tsv | sort) /tmp/lean9_certs.tsv | awk -F'\t' '$2!=$4 || $3!=$5' | head
echo "done $(date '+%T')"
