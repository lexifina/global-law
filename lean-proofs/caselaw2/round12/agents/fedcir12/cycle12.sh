#!/bin/sh
# fedcir12: rows_<tag>_<lean|trib>.jsonl -> certify12 (lean) / certify12_claims (trib, claim anchorTribunal)
#           -> round-6 guard -> delta_<tag>_<part>/
set -e
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
T=$1
P=$2
mkdir -p work/guard
cd "$C2"
if [ "$P" = trib ]; then
  python -X utf8 round12/certify12_claims.py --rows "$B/rows_${T}_$P.jsonl" --out "$B/cert_${T}_$P" --procs 8 $XARGS > "$B/work/cert_${T}_$P.log" 2>&1
else
  python -X utf8 round12/certify12.py --rows "$B/rows_${T}_$P.jsonl" --out "$B/cert_${T}_$P" --procs 8 $XARGS > "$B/work/cert_${T}_$P.log" 2>&1
fi
cd "$B"
G=${T}_$P
cp "cert_$G/history_delta.tsv" "work/guard/${G}_delta.tsv"
rm -f work/guard/${G}_feat.*.jsonl.gz work/guard/${G}_features.jsonl.gz
python -X utf8 gfeat8.py --base "work/guard/${G}_delta.tsv" --tag "${G}_" --procs 8 > "work/guard/${G}_gfeat.log" 2>&1
python -X utf8 guard8.py "$G" "work/guard/${G}_delta.tsv" > "work/guard/${G}_guard.log" 2>&1
python -X utf8 deltas.py "delta_$G" "cert_$G" --drop "work/guard/${G}_drop_ids.txt"
echo cycle-done $G
