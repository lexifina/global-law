#!/usr/bin/env bash
# Round 10: the single sealed run (LEAD ONLY, once, after round10/FREEZE.md). Written by agent infra10; NOT run by it.
#   bash round10/score_sealed10.sh <frozen name>
#   bash round10/score_sealed10.sh --plan <name>    prints the steps and the refusal checks' targets; scores nothing,
#                                                    reads no key or result file
# (= round9/score_sealed9.sh on round-10 paths, SEALED_LOG figures from the scorers' own files by round10/sealed_lines10.py)
# 1. fresh lists, sealed half (SIXTH use; burned, D10-2), both date views: round7/score_fresh7.py --split test
# 2. Shepardized, sealed half (FIFTH use; burned, D10-2): round6/shepardized/compare.py --split sealed through
#    round10/shep_sealed10.py (freeze check = round10/FREEZE.md)
# 3. the four round-8 keys, h1 halves, THIRD use: benchmarks/<key>/score.py --out round10/out/<name>
#    --data round10/stage/<name> --label round10 (refused when benchmarks/<key>/results/round10.h1.json exists)
# 4. songer_treat and brace_hall_state (the round-9 keys), SECOND use, frozen build only, --label round10; h0, h1 and
#    all logged (refused when benchmarks/<k>/results/round10.* exists). v9c's figures exist from round 9 (round9.*);
#    v9c is not re-run.
# 5. the round-10 fresh keys, first and only use: for every folder name in round10/FRESH_KEYS.txt (one per line, written
#    by the lead), benchmarks/<k>/score.py twice: on round9/out/v9c + round9/stage/v9c with --label round9v9c, and on
#    the frozen build with --label round10 (refused when benchmarks/<k>/results/round9v9c.* or round10.* exists).
#    `python -I benchmarks/<k>/score.py --out <dir> --data <dir> --label <x>` writes results/<label>.{h0,h1,all}.json;
#    all three are printed and logged. No FRESH_KEYS.txt: step 5 is skipped and logged.
# Never the round-7 time split (round7/heldout/). Refuses unless round10/FREEZE.md names <name> and
# `round10/freeze10.py --check` passes. Every refusal check runs before anything is scored. Only aggregate output is
# printed; every run is appended to round10/SEALED_LOG.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
C2="$(cd "$HERE/.." && pwd)"
PLAN=
if [ "${1:-}" = --plan ]; then PLAN=1; shift; fi
N="${1:?usage: score_sealed10.sh [--plan] <frozen name>}"
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "refused: bad name $N"; exit 3; }
KEYS8="fjc_idb_appeals shadow_docket scdb_disposition state_overruled_tables"
KEYS9="songer_treat brace_hall_state"
OUT="round10/out/$N"; DATA="round10/stage/$N"; R="round10/results/$N/sealed"
if [ -n "$PLAN" ]; then
  cat <<EOF
plan for $N (nothing scored, no key or result file read):
 0. refuse unless round10/FREEZE.md names \`$N\` and round10/freeze10.py --check passes;
    refuse if benchmarks/<k>/results/round10.h1.json exists for: $KEYS8
    refuse if benchmarks/<k>/results/round10.* exists for: $KEYS9
    refuse if benchmarks/<k>/results/round9v9c.* or round10.* exists for the keys in round10/FRESH_KEYS.txt
 1. round7/score_fresh7.py --split test --status $OUT/status.tsv --treatments $DATA/treatments.tsv --data $DATA --label r10-$N  (6th use)
 2. round10/shep_sealed10.py --split sealed --out $OUT --data $DATA --results $R/shep  (5th use)
 3. benchmarks/<k>/score.py --out $OUT --data $DATA --label round10, k in: $KEYS8  (h1, 3rd use; h1 lines logged)
 4. benchmarks/<k>/score.py --out $OUT --data $DATA --label round10, k in: $KEYS9  (2nd use; h0/h1/all logged)
 5. per key in round10/FRESH_KEYS.txt ($( [ -f "$HERE/FRESH_KEYS.txt" ] && echo present || echo 'absent: skipped')):
    --out round9/out/v9c --data round9/stage/v9c --label round9v9c, then --out $OUT --data $DATA --label round10  (1st use)
 log: round10/SEALED_LOG.md (lines from round10/sealed_lines10.py); outputs in $R/
EOF
  exit 0
fi
[ -f "$HERE/FREEZE.md" ] || { echo "refused: round10/FREEZE.md missing"; exit 3; }
grep -q "Variant \`$N\`" "$HERE/FREEZE.md" || { echo "refused: FREEZE.md does not name $N"; exit 3; }
cd "$C2"
python -X utf8 round10/freeze10.py --check || { echo "refused: freeze10.py --check failed"; exit 3; }
for k in $KEYS8; do
  [ ! -f "benchmarks/$k/results/round10.h1.json" ] || { echo "refused: benchmarks/$k/results/round10.h1.json exists (round-10 h1 already scored)"; exit 3; }
done
for k in $KEYS9; do
  [ -f "benchmarks/$k/score.py" ] || { echo "refused: benchmarks/$k/score.py missing"; exit 3; }
  if compgen -G "benchmarks/$k/results/round10.*" > /dev/null; then
    echo "refused: benchmarks/$k/results/ already holds round10.* (second use already scored)"; exit 3
  fi
done
FRESH=
if [ -f round10/FRESH_KEYS.txt ]; then
  FRESH=$(grep -v '^#' round10/FRESH_KEYS.txt | tr -d '\r' | awk 'NF{print $1}')
  for k in $FRESH; do
    [[ "$k" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "refused: bad folder name '$k' in FRESH_KEYS.txt"; exit 3; }
    case " $KEYS8 $KEYS9 " in *" $k "*) echo "refused: $k in FRESH_KEYS.txt is not a round-10 key"; exit 3 ;; esac
    [ -f "benchmarks/$k/score.py" ] || { echo "refused: benchmarks/$k/score.py missing"; exit 3; }
    if compgen -G "benchmarks/$k/results/round10.*" > /dev/null || compgen -G "benchmarks/$k/results/round9v9c.*" > /dev/null; then
      echo "refused: benchmarks/$k/results/ already holds round10.* or round9v9c.* (fresh key already scored)"; exit 3
    fi
  done
fi
mkdir -p "$R"
LOG="$HERE/SEALED_LOG.md"
[ -f "$LOG" ] || printf '# Round 10 sealed runs (one line per run)\n\n' > "$LOG"
ts=$(date '+%Y-%m-%d %H:%M:%S')
ext () { python -I round10/sealed_lines10.py "$@" || true; }
echo "== 1. fresh lists, sealed half (sixth use)"
rc=0; python -X utf8 round7/score_fresh7.py --split test --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" \
  --data "$DATA" --label "r10-$N" > "$R/fresh_test.txt" 2>&1 || rc=$?
line=$(ext fresh "$R/fresh_test.txt"); echo "$line"
echo "- $ts fresh sealed, 6th use (score_fresh7 --split test, label r10-$N, exit $rc): $line" >> "$LOG"
echo "== 2. Shepardized, sealed half (fifth use)"
rc=0; python -I round10/shep_sealed10.py --split sealed --out "$C2/$OUT" --data "$C2/$DATA" --results "$C2/$R/shep" > "$R/shep_sealed.txt" 2>&1 || rc=$?
line=$(ext shep "$R/shep/headline.tsv"); echo "$line"
echo "- $ts Shepardized sealed, 5th use (compare.py --split sealed, $N, exit $rc): $line" >> "$LOG"
echo "== 3. the four round-8 keys, h1 halves (third use; label round10)"
for k in $KEYS8; do
  rc=0; python -I -B "benchmarks/$k/score.py" --out "$C2/$OUT" --data "$C2/$DATA" --label round10 > "$R/bench_$k.txt" 2>&1 || rc=$?
  line=$(ext half "$R/bench_$k.txt" h1); echo "$k: $line"
  echo "- $ts $k h1, 3rd use (benchmarks/$k/score.py --label round10, $N, exit $rc): $line" >> "$LOG"
done
key_one () {  # key, out, data, label, tag, what
  local k=$1 o=$2 d=$3 lab=$4 tag=$5 what=$6 rc=0 line
  python -I -B "benchmarks/$k/score.py" --out "$C2/$o" --data "$C2/$d" --label "$lab" > "$R/key_${k}_$tag.txt" 2>&1 || rc=$?
  # h0, h1 and all: results/<label>.{h0,h1,all}.json; stdout lines as fallback
  line=$(ext json "benchmarks/$k/results/$lab.h0.json" "benchmarks/$k/results/$lab.h1.json" "benchmarks/$k/results/$lab.all.json")
  case "$line" in EXTRACTION*) line="$line; stdout: $(ext lines "$R/key_${k}_$tag.txt")" ;; esac
  echo "$k $tag: $line"
  echo "- $ts $k $what, $tag (benchmarks/$k/score.py --label $lab, exit $rc): $line" >> "$LOG"
}
echo "== 4. songer_treat and brace_hall_state (second use; $N as round10)"
for k in $KEYS9; do
  key_one "$k" "$OUT" "$DATA" round10 "$N" "round-9 key, 2nd use"
done
echo "== 5. round-10 fresh keys (first and only use; v9c as round9v9c, $N as round10)"
if [ -z "$FRESH" ]; then
  echo "no round10/FRESH_KEYS.txt (or empty): step 5 skipped"
  echo "- $ts round-10 fresh keys: skipped (no round10/FRESH_KEYS.txt)" >> "$LOG"
fi
for k in $FRESH; do
  key_one "$k" round9/out/v9c round9/stage/v9c round9v9c v9c "fresh key, 1st use"
  key_one "$k" "$OUT" "$DATA" round10 "$N" "fresh key, 1st use"
done
echo "SEALED $N done (log: round10/SEALED_LOG.md)"
