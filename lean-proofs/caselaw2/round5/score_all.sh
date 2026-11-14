#!/bin/bash
# round 5: every DEV-side score for one variant.   usage: round5/score_all.sh <name> [nobeh] [noold]
#   reads round5/out/<name>/ (Lean output) and round5/stage/<name>/ (its data folder)
# The sealed test (score_fresh.py --split test) is NOT run here: it is run once, by hand, after FREEZE.md.
C2="$(cd "$(dirname "$0")/.." && pwd)"
N=$1
OUT="$C2/round5/out/$N"; DATA="$C2/round5/stage/$N"
R="$C2/round5/results/$N"; mkdir -p "$R"
cd "$C2"
echo "== fresh lists, dev"
python round5/gold_fresh/score_fresh.py --split dev --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" --label "$N" > "$R/fresh_dev.txt" 2>&1; tail -25 "$R/fresh_dev.txt" | head -40
cd "$C2/round5/tests"
echo "== no-leak"
python check_no_leak.py "$DATA/treatments.tsv" "$DATA/treatment_witness.tsv" --certs "$OUT/certs.tsv" --data "$DATA" --tsv "$R/leak.tsv" > "$R/leak.txt" 2>&1; echo "exit $?" >> "$R/leak.txt"; tail -12 "$R/leak.txt"
echo "== holdout notes"
python score_holdout.py --status "$OUT/status.tsv" --label "$N" --data "$DATA" > "$R/holdout.txt" 2>&1; grep -n "pool\|Testable\|reverse\|Reverse\|precedent" "$R/holdout.txt" | head -30
if [ "$2" != nobeh ] && [ "$3" != nobeh ]; then
  echo "== behaviour"
  python behaviour.py --status "$OUT/status.tsv" --label "$N" --data "$DATA" --classes "$C2/round5/classes_r5.tsv" > "$R/behaviour.txt" 2>&1; grep -n "k=10\|k = 10\| 10 " "$R/behaviour.txt" | head -30
fi
if [ "$2" != noold ] && [ "$3" != noold ]; then
  echo "== old lists (burned, non-blind): SCDB / CRS"
  mkdir -p "$R/old"
  cd "$C2"
  python ~/Documents/global-law-lean/lean-proofs/tools/caselaw2/eval/score.py --out "$OUT" --data "$DATA" --results "$R/old" > "$R/old.txt" 2>&1
  python -c "
import json,sys
d=json.load(open(sys.argv[1]))
s=d['scdb']; c=d['crs']
print('SCDB', s['flagged_with_admitted_overruling'], '/', s['flagged_decisions'], 'precision', s['of_which_flagged'], '/', s['scotus_decisions_with_admitted_overruling_of_scotus'])
print('CRS current', c['current_table']['found'], '/', c['current_table']['resolved'], ' 2016 express', c['2016_express']['found'], '/', c['2016_express']['resolved'], ' 2016 all', c['2016_all']['found'], '/', c['2016_all']['resolved'])
" "$R/old/results.json" 2>&1 | tail -3
  # the same by class, counting recognised rows too (score.py counts explicit rows only); the last two lines of
  # old.txt are what the report page shows
  python round5/old_by_class.py "$N" > "$R/old_by_class.txt" 2>&1
  python -c "
import json,sys
d=json.load(open(sys.argv[1]))
e=d['selfAnnounced+operativeWords']; f=d['selfAnnounced+operativeWords+recognised']
print('SCDB %d / %d (explicit rows), %d / %d with recognised rows' % (e['scdb_found'], e['scdb_flagged'], f['scdb_found'], f['scdb_flagged']))
print('CRS current %d / %d (explicit rows), %d / %d with recognised rows' % (e['crs_current_table'][0], e['crs_current_table'][1], f['crs_current_table'][0], f['crs_current_table'][1]))
" "$R/old_by_class.json" >> "$R/old.txt" 2>&1
  tail -2 "$R/old.txt"
fi
echo "SCORED $N"
