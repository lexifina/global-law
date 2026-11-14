#!/usr/bin/env bash
# Round 11: the single sealed run (LEAD ONLY, once, after round11/FREEZE.md). Written by agent infra11; NOT run by it.
#   bash round11/score_sealed11.sh <frozen name>
#   bash round11/score_sealed11.sh --plan <name>    prints the steps and the refusal checks' targets; scores nothing,
#                                                    reads no key or result file
# (= round10/score_sealed10.sh on round-11 paths, SEALED_LOG figures from the scorers' own files by round11/sealed_lines11.py)
# 1. fresh lists, sealed half (SEVENTH use; burned, D11-2), both date views: round7/score_fresh7.py --split test
# 2. Shepardized, sealed half (SIXTH use; burned, D11-2): round6/shepardized/compare.py --split sealed through
#    round11/shep_sealed11.py (freeze check = round11/FREEZE.md)
# 3. the four round-8 keys, h1 halves, FOURTH use: benchmarks/<key>/score.py --out round11/out/<name>
#    --data round11/stage/<name> --label round11 (refused when benchmarks/<key>/results/round11.h1.json exists)
# 4. the closed keys: songer_treat and brace_hall_state (THIRD use) and fedcir_dataset (SECOND use), frozen build
#    only, --label round11; h0, h1 and all logged (refused when benchmarks/<k>/results/round11.* exists). v10d's
#    figures exist from round 10 (round10.*); v10d is not re-run. Their score.py is run by the CLI of
#    benchmarks/CONTRACT.md; this script never opens their folders otherwise (only the results/round11.* refusal test
#    and the json files the scorer itself writes, read by sealed_lines11.py).
# 5. the round-11 fresh keys, first and only use: for every folder name in round11/FRESH_KEYS.txt (one per line, written
#    by the lead), benchmarks/<k>/score.py twice: on round10/out/v10d + round10/stage/v10d with --label round10v10d, and on
#    the frozen build with --label round11 (refused when benchmarks/<k>/results/round10v10d.* or round11.* exists).
#    `python -I benchmarks/<k>/score.py --out <dir> --data <dir> --label <x>` writes results/<label>.{h0,h1,all}.json;
#    all three are printed and logged. No FRESH_KEYS.txt: step 5 is skipped and logged.
# Never the round-7 time split (round7/heldout/). Refuses unless round11/FREEZE.md names <name> and
# `round11/freeze11.py --check` passes. Every refusal check runs before anything is scored. Only aggregate output is
# printed; every run is appended to round11/SEALED_LOG.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
C2="$(cd "$HERE/.." && pwd)"
PLAN=
if [ "${1:-}" = --plan ]; then PLAN=1; shift; fi
N="${1:?usage: score_sealed11.sh [--plan] <frozen name>}"
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "refused: bad name $N"; exit 3; }
KEYS8="fjc_idb_appeals shadow_docket scdb_disposition state_overruled_tables"
KEYS9="songer_treat brace_hall_state fedcir_dataset"
OUT="round11/out/$N"; DATA="round11/stage/$N"; R="round11/results/$N/sealed"
if [ -n "$PLAN" ]; then
  cat <<EOF
plan for $N (nothing scored, no key or result file read):
 0. refuse unless round11/FREEZE.md names \`$N\` and round11/freeze11.py --check passes;
    refuse if benchmarks/<k>/results/round11.h1.json exists for: $KEYS8
    refuse if benchmarks/<k>/results/round11.* exists for: $KEYS9
    refuse if benchmarks/<k>/results/round10v10d.* or round11.* exists for the keys in round11/FRESH_KEYS.txt
 1. round7/score_fresh7.py --split test --status $OUT/status.tsv --treatments $DATA/treatments.tsv --data $DATA --label r11-$N  (7th use)
 2. round11/shep_sealed11.py --split sealed --out $OUT --data $DATA --results $R/shep  (6th use)
 3. benchmarks/<k>/score.py --out $OUT --data $DATA --label round11, k in: $KEYS8  (h1, 4th use; h1 lines logged)
 4. benchmarks/<k>/score.py --out $OUT --data $DATA --label round11, k in: $KEYS9  (songer / brace & hall 3rd use, fedcir 2nd use; h0/h1/all logged)
 5. per key in round11/FRESH_KEYS.txt ($( [ -f "$HERE/FRESH_KEYS.txt" ] && echo present || echo 'absent: skipped')):
    --out round10/out/v10d --data round10/stage/v10d --label round10v10d, then --out $OUT --data $DATA --label round11  (1st use)
 log: round11/SEALED_LOG.md (lines from round11/sealed_lines11.py); outputs in $R/
EOF
  exit 0
fi
[ -f "$HERE/FREEZE.md" ] || { echo "refused: round11/FREEZE.md missing"; exit 3; }
grep -q "Variant \`$N\`" "$HERE/FREEZE.md" || { echo "refused: FREEZE.md does not name $N"; exit 3; }
cd "$C2"
python -X utf8 round11/freeze11.py --check || { echo "refused: freeze11.py --check failed"; exit 3; }
for k in $KEYS8; do
  [ ! -f "benchmarks/$k/results/round11.h1.json" ] || { echo "refused: benchmarks/$k/results/round11.h1.json exists (round-11 h1 already scored)"; exit 3; }
done
for k in $KEYS9; do
  [ -f "benchmarks/$k/score.py" ] || { echo "refused: benchmarks/$k/score.py missing"; exit 3; }
  if compgen -G "benchmarks/$k/results/round11.*" > /dev/null; then
    echo "refused: benchmarks/$k/results/ already holds round11.* (closed key already scored in round 11)"; exit 3
  fi
done
FRESH=
if [ -f round11/FRESH_KEYS.txt ]; then
  FRESH=$(grep -v '^#' round11/FRESH_KEYS.txt | tr -d '\r' | awk 'NF{print $1}')
  for k in $FRESH; do
    [[ "$k" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "refused: bad folder name '$k' in FRESH_KEYS.txt"; exit 3; }
    case " $KEYS8 $KEYS9 " in *" $k "*) echo "refused: $k in FRESH_KEYS.txt is not a round-11 key"; exit 3 ;; esac
    [ -f "benchmarks/$k/score.py" ] || { echo "refused: benchmarks/$k/score.py missing"; exit 3; }
    if compgen -G "benchmarks/$k/results/round11.*" > /dev/null || compgen -G "benchmarks/$k/results/round10v10d.*" > /dev/null; then
      echo "refused: benchmarks/$k/results/ already holds round11.* or round10v10d.* (fresh key already scored)"; exit 3
    fi
  done
fi
mkdir -p "$R"
LOG="$HERE/SEALED_LOG.md"
[ -f "$LOG" ] || printf '# Round 11 sealed runs (one line per run)\n\n' > "$LOG"
ts=$(date '+%Y-%m-%d %H:%M:%S')
ext () { python -I round11/sealed_lines11.py "$@" || true; }
echo "== 1. fresh lists, sealed half (seventh use)"
rc=0; python -X utf8 round7/score_fresh7.py --split test --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" \
  --data "$DATA" --label "r11-$N" > "$R/fresh_test.txt" 2>&1 || rc=$?
line=$(ext fresh "$R/fresh_test.txt"); echo "$line"
echo "- $ts fresh sealed, 7th use (score_fresh7 --split test, label r11-$N, exit $rc): $line" >> "$LOG"
echo "== 2. Shepardized, sealed half (sixth use)"
rc=0; python -I round11/shep_sealed11.py --split sealed --out "$C2/$OUT" --data "$C2/$DATA" --results "$C2/$R/shep" > "$R/shep_sealed.txt" 2>&1 || rc=$?
line=$(ext shep "$R/shep/headline.tsv"); echo "$line"
echo "- $ts Shepardized sealed, 6th use (compare.py --split sealed, $N, exit $rc): $line" >> "$LOG"
echo "== 3. the four round-8 keys, h1 halves (fourth use; label round11)"
for k in $KEYS8; do
  rc=0; python -I -B "benchmarks/$k/score.py" --out "$C2/$OUT" --data "$C2/$DATA" --label round11 > "$R/bench_$k.txt" 2>&1 || rc=$?
  line=$(ext half "$R/bench_$k.txt" h1); echo "$k: $line"
  echo "- $ts $k h1, 4th use (benchmarks/$k/score.py --label round11, $N, exit $rc): $line" >> "$LOG"
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
echo "== 4. songer_treat, brace_hall_state (third use) and fedcir_dataset (second use); $N as round11"
for k in $KEYS9; do
  case $k in fedcir_dataset) use="closed key, 2nd use" ;; *) use="closed key, 3rd use" ;; esac
  key_one "$k" "$OUT" "$DATA" round11 "$N" "$use"
done
echo "== 5. round-11 fresh keys (first and only use; v10d as round10v10d, $N as round11)"
if [ -z "$FRESH" ]; then
  echo "no round11/FRESH_KEYS.txt (or empty): step 5 skipped"
  echo "- $ts round-11 fresh keys: skipped (no round11/FRESH_KEYS.txt)" >> "$LOG"
fi
for k in $FRESH; do
  key_one "$k" round10/out/v10d round10/stage/v10d round10v10d v10d "fresh key, 1st use"
  key_one "$k" "$OUT" "$DATA" round11 "$N" "fresh key, 1st use"
done
echo "SEALED $N done (log: round11/SEALED_LOG.md)"
