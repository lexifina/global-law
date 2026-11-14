#!/bin/bash
# round 10: every DEV-side score for one variant + the four round-8 keys on h0.   usage: bash round10/score10.sh <name> [beh] [noold] [nobench]
#   reads round10/out/<name>/ (Lean output, wsl/r10_run.sh) and round10/stage/<name>/ (its data folder, stage10.py);
#   writes round10/results/<name>/ and a one-page summary.txt there (round10/summary10.py).
#   = round9/score9.sh on round-10 paths (agent infra10); the h0 scorer is still round8/bench_h0/score_h0.py,
#   which scores only the four round-8 keys (fjc_idb_appeals, shadow_docket, scdb_disposition,
#   state_overruled_tables) and only their h0 half.
#   beh      also run the behaviour test (slow; off by default)
#   noold    skip the burned SCDB / CRS lists
#   nobench  skip the h0 benchmark step
# = round7/score7.sh on round-8 paths, plus the h0 benchmark step (round8/bench_h0/score_h0.py -> results/<name>/bench/).
# Never runs a sealed / test split or an h1 half: fresh lists --split dev, Shepardized --split dev, new keys h0 only,
# never the round-7 time split (round7/heldout/), never the round-9 keys (Songer / Brace & Hall), never a round-10
# fresh key. The sealed halves are scored once, by the lead, after round10/FREEZE.md (round10/score_sealed10.sh).
C2="$(cd "$(dirname "$0")/.." && pwd)"
N=$1
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "usage: score10.sh <name> [beh] [noold] [nobench]"; exit 2; }
OUT="$C2/round10/out/$N"; DATA="$C2/round10/stage/$N"
R="$C2/round10/results/$N"; mkdir -p "$R"
for f in "$OUT/status.tsv" "$OUT/certs.tsv" "$DATA/treatments.tsv" "$DATA/history.tsv"; do
  [ -f "$f" ] || { echo "missing $f"; exit 2; }
done
BEH=0; OLD=1; BENCH=1
for x in "$2" "$3" "$4"; do [ "$x" = beh ] && BEH=1; [ "$x" = noold ] && OLD=0; [ "$x" = nobench ] && BENCH=0; done
cd "$C2"
date '+scored %F %T' > "$R/run.log"
if [ $BENCH = 1 ]; then
  echo "== new keys, h0 half (round8/bench_h0/score_h0.py, in the background)"
  python -B round8/bench_h0/score_h0.py --out "$OUT" --data "$DATA" --label "$N" --results "$R/bench" > "$R/bench_h0.txt" 2>&1 &
  BPID=$!
fi
echo "== fresh lists, dev (round5 score_fresh.py; its files are moved from round5/gold_fresh/dev/results/ to here)"
L="r10_$N"
python round5/gold_fresh/score_fresh.py --split dev --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" --label "$L" > "$R/fresh_dev.txt" 2>&1
echo "exit $?" >> "$R/fresh_dev.txt"
for s in .json .pairs.tsv .unlisted_sample.tsv; do
  [ -f "round5/gold_fresh/dev/results/$L$s" ] && mv -f "round5/gold_fresh/dev/results/$L$s" "$R/fresh_dev$s"
done
grep -E "^all |^burned_crs|^precision" "$R/fresh_dev.txt"
echo "== fresh lists, dev, both date views (round7/score_fresh7.py --out round10/results/<name>/fresh7)"
python round7/score_fresh7.py --split dev --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" --data "$DATA" --label "$N" --view both --out "$R/fresh7" > "$R/fresh7_dev.txt" 2>&1
echo "exit $?" >> "$R/fresh7_dev.txt"; tail -8 "$R/fresh7_dev.txt"
cd "$C2/round5/tests"
echo "== no-leak"
python check_no_leak.py "$DATA/treatments.tsv" "$DATA/treatment_witness.tsv" --certs "$OUT/certs.tsv" --data "$DATA" --tsv "$R/leak.tsv" > "$R/leak.txt" 2>&1; echo "exit $?" >> "$R/leak.txt"; tail -3 "$R/leak.txt"
echo "== holdout notes"
python score_holdout.py --status "$OUT/status.tsv" --label "$N" --data "$DATA" --out "$R/holdout" --pool "$C2/round5/tests/results/testable_pool_baseline-round4.tsv" > "$R/holdout.txt" 2>&1; echo "exit $?" >> "$R/holdout.txt"
grep -n "pool\|Testable\|reverse\|Reverse\|precedent" "$R/holdout.txt" | head -12
if [ $BEH = 1 ]; then
  echo "== behaviour"
  python behaviour.py --status "$OUT/status.tsv" --label "$N" --data "$DATA" --classes "$C2/round5/classes_r5.tsv" --out "$R/behaviour" > "$R/behaviour.txt" 2>&1; echo "exit $?" >> "$R/behaviour.txt"
  grep -n "k = 10" "$R/behaviour.txt" | head
fi
cd "$C2"
if [ $OLD = 1 ]; then
  echo "== old lists (burned, non-blind): SCDB / CRS"
  mkdir -p "$R/old"
  python ~/Documents/global-law-lean/lean-proofs/tools/caselaw2/eval/score.py --out "$OUT" --data "$DATA" --results "$R/old" > "$R/old.txt" 2>&1
  python round10/old_by_class10.py "$N" > "$R/old_by_class.txt" 2>&1
  tail -3 "$R/old_by_class.txt"
fi
echo "== Shepardized, dev half (round7/score_hist_dev.py --out/--data/--res round-10 paths -> round6/shepardized/compare.py --split dev)"
python -I round7/score_hist_dev.py "$N" --out "$OUT" --data "$DATA" --res "$R/shepardized" > "$R/shepardized_dev.txt" 2>&1; echo "exit $?" >> "$R/shepardized_dev.txt"
grep -E "^\(a\)|^\(b\)|^\(c\) clean	CLEAN" "$R/shepardized_dev.txt" | cut -f1-6
if [ $BENCH = 1 ]; then
  wait $BPID; echo "exit $?" >> "$R/bench_h0.txt"
  echo "== new keys, h0 half"; cat "$R/bench_h0.txt"
fi
python round10/summary10.py "$N" > "$R/summary.txt" 2>&1
echo; cat "$R/summary.txt"
echo "SCORED $N"
