#!/usr/bin/env bash
# Round 9: the single sealed run (LEAD ONLY, once, after round9/FREEZE.md). Written by agent infra9; NOT run by it.
#   bash round9/score_sealed9.sh <frozen name>
# (= round8/score_sealed8.sh on round-9 paths, with the SEALED_LOG figures taken from the scorers' own output files by
#  round9/sealed_lines9.py (round 8's grep patterns matched nothing and left two empty log lines), plus step 4.)
# 1. fresh lists, sealed half (FIFTH use; burned, D9-2), both date views: round7/score_fresh7.py --split test
# 2. Shepardized, sealed half (FOURTH use; burned, D9-2): round6/shepardized/compare.py --split sealed through
#    round9/shep_sealed9.py (freeze check = round9/FREEZE.md)
# 3. the four round-8 keys, h1 halves, SECOND use: benchmarks/<key>/score.py --out round9/out/<name>
#    --data round9/stage/<name> --label round9 (refused when benchmarks/<key>/results/round9.h1.json exists)
# 4. the round-9 fresh keys, first and only use: for every folder name in round9/FRESH_KEYS.txt (one per line, written
#    by the lead), benchmarks/<k>/score.py twice: on round8/out/v8e + round8/stage/v8e with --label round8v8e, and on
#    the frozen build with --label round9 (refused when benchmarks/<k>/results/round9.* or round8v8e.* exists).
#    `python -I benchmarks/<k>/score.py --out <dir> --data <dir> --label <x>` writes results/<label>.{h0,h1,all}.json;
#    all three (both halves are untouched) are printed and logged. No FRESH_KEYS.txt: step 4 is skipped and says so.
# Never the round-7 time split (round7/heldout/). Refuses unless round9/FREEZE.md names <name> and
# `round9/freeze9.py --check` passes. Only aggregate output is printed; every run is appended to round9/SEALED_LOG.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
C2="$(cd "$HERE/.." && pwd)"
N="${1:?usage: score_sealed9.sh <frozen name>}"
[ -f "$HERE/FREEZE.md" ] || { echo "refused: round9/FREEZE.md missing"; exit 3; }
grep -q "Variant \`$N\`" "$HERE/FREEZE.md" || { echo "refused: FREEZE.md does not name $N"; exit 3; }
cd "$C2"
python -X utf8 round9/freeze9.py --check || { echo "refused: freeze9.py --check failed"; exit 3; }
KEYS8="fjc_idb_appeals shadow_docket scdb_disposition state_overruled_tables"
for k in $KEYS8; do
  [ ! -f "benchmarks/$k/results/round9.h1.json" ] || { echo "refused: benchmarks/$k/results/round9.h1.json exists (round-9 h1 already scored)"; exit 3; }
done
FRESH=
if [ -f round9/FRESH_KEYS.txt ]; then
  FRESH=$(grep -v '^#' round9/FRESH_KEYS.txt | tr -d '\r' | awk 'NF{print $1}')
  for k in $FRESH; do
    [[ "$k" =~ ^[A-Za-z0-9_.-]+$ ]] || { echo "refused: bad folder name '$k' in FRESH_KEYS.txt"; exit 3; }
    [ -f "benchmarks/$k/score.py" ] || { echo "refused: benchmarks/$k/score.py missing"; exit 3; }
    if compgen -G "benchmarks/$k/results/round9.*" > /dev/null || compgen -G "benchmarks/$k/results/round8v8e.*" > /dev/null; then
      echo "refused: benchmarks/$k/results/ already holds round9.* or round8v8e.* (fresh key already scored)"; exit 3
    fi
  done
fi
OUT="round9/out/$N"; DATA="round9/stage/$N"; R="round9/results/$N/sealed"; mkdir -p "$R"
LOG="$HERE/SEALED_LOG.md"
[ -f "$LOG" ] || printf '# Round 9 sealed runs (one line per run)\n\n' > "$LOG"
ts=$(date '+%Y-%m-%d %H:%M:%S')
ext () { python -I round9/sealed_lines9.py "$@" || true; }
echo "== 1. fresh lists, sealed half (fifth use)"
rc=0; python -X utf8 round7/score_fresh7.py --split test --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" \
  --data "$DATA" --label "r9-$N" > "$R/fresh_test.txt" 2>&1 || rc=$?
line=$(ext fresh "$R/fresh_test.txt"); echo "$line"
echo "- $ts fresh sealed, 5th use (score_fresh7 --split test, label r9-$N, exit $rc): $line" >> "$LOG"
echo "== 2. Shepardized, sealed half (fourth use)"
rc=0; python -I round9/shep_sealed9.py --split sealed --out "$C2/$OUT" --data "$C2/$DATA" --results "$C2/$R/shep" > "$R/shep_sealed.txt" 2>&1 || rc=$?
line=$(ext shep "$R/shep/headline.tsv"); echo "$line"
echo "- $ts Shepardized sealed, 4th use (compare.py --split sealed, $N, exit $rc): $line" >> "$LOG"
echo "== 3. the four round-8 keys, h1 halves (second use; label round9)"
for k in $KEYS8; do
  rc=0; python -I -B "benchmarks/$k/score.py" --out "$C2/$OUT" --data "$C2/$DATA" --label round9 > "$R/bench_$k.txt" 2>&1 || rc=$?
  line=$(ext half "$R/bench_$k.txt" h1); echo "$k: $line"
  echo "- $ts $k h1, 2nd use (benchmarks/$k/score.py --label round9, $N, exit $rc): $line" >> "$LOG"
done
echo "== 4. round-9 fresh keys (first and only use; v8e as round8v8e, $N as round9)"
if [ -z "$FRESH" ]; then
  echo "no round9/FRESH_KEYS.txt (or empty): step 4 skipped"
  echo "- $ts round-9 fresh keys: skipped (no round9/FRESH_KEYS.txt)" >> "$LOG"
fi
fresh_one () {  # key, out, data, label, tag
  local k=$1 o=$2 d=$3 lab=$4 tag=$5 rc=0 line
  python -I -B "benchmarks/$k/score.py" --out "$C2/$o" --data "$C2/$d" --label "$lab" > "$R/fresh_${k}_$tag.txt" 2>&1 || rc=$?
  # both halves and all (h0 and h1 are both untouched): results/<label>.{h0,h1,all}.json; stdout lines as fallback
  line=$(ext json "benchmarks/$k/results/$lab.h0.json" "benchmarks/$k/results/$lab.h1.json" "benchmarks/$k/results/$lab.all.json")
  case "$line" in EXTRACTION*) line="$line; stdout: $(ext lines "$R/fresh_${k}_$tag.txt")" ;; esac
  echo "$k $tag: $line"
  echo "- $ts $k fresh key, 1st use, $tag (benchmarks/$k/score.py --label $lab, exit $rc): $line" >> "$LOG"
}
for k in $FRESH; do
  fresh_one "$k" round8/out/v8e round8/stage/v8e round8v8e v8e
  fresh_one "$k" "$OUT" "$DATA" round9 "$N"
done
echo "SEALED $N done (log: round9/SEALED_LOG.md)"
