#!/usr/bin/env bash
# Round 8: the single sealed run (LEAD ONLY, once, after round8/FREEZE.md). Written by agent infra; NOT run by it.
#   bash round8/score_sealed8.sh <frozen name>
# 1. fresh lists, sealed half (fourth use; burned, D8-2), both date views: round7/score_fresh7.py --split test
# 2. Shepardized, sealed half (third use; burned, D8-2): round6/shepardized/compare.py --split sealed through
#    round8/shep_sealed8.py (freeze check = round8/FREEZE.md)
# 3. the four new keys, h1 (and h0 / all) halves, first and only use: benchmarks/<key>/score.py --out round8/out/<name>
#    --data round8/stage/<name> --label round8 (each writes its own benchmarks/<key>/results/round8.*: the single
#    sanctioned write into benchmarks/, by the lead only)
# Never the round-7 time split (round7/heldout/). Refuses unless round8/FREEZE.md names <name> and
# `round8/freeze8.py --check` passes; refuses a second run of step 3 (results/round8.h1.json present).
# Only aggregate output is printed; every run is appended to round8/SEALED_LOG.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
C2="$(cd "$HERE/.." && pwd)"
N="${1:?usage: score_sealed8.sh <frozen name>}"
[ -f "$HERE/FREEZE.md" ] || { echo "refused: round8/FREEZE.md missing"; exit 3; }
grep -q "Variant \`$N\`" "$HERE/FREEZE.md" || { echo "refused: FREEZE.md does not name $N"; exit 3; }
cd "$C2"
python -X utf8 round8/freeze8.py --check || { echo "refused: freeze8.py --check failed"; exit 3; }
for k in fjc_idb_appeals shadow_docket scdb_disposition state_overruled_tables; do
  [ ! -f "benchmarks/$k/results/round8.h1.json" ] || { echo "refused: benchmarks/$k/results/round8.h1.json exists (h1 already scored)"; exit 3; }
done
OUT="round8/out/$N"; DATA="round8/stage/$N"; R="round8/results/$N/sealed"; mkdir -p "$R"
LOG="$HERE/SEALED_LOG.md"
[ -f "$LOG" ] || printf '# Round 8 sealed runs (one line per run)\n\n' > "$LOG"
ts=$(date '+%Y-%m-%d %H:%M:%S')
echo "== fresh lists, sealed half (fourth use)"
python -X utf8 round7/score_fresh7.py --split test --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" \
  --data "$DATA" --label "r8-$N" > "$R/fresh_test.txt" 2>&1
grep -E "strict|lenient|view" "$R/fresh_test.txt" | head -20
echo "- $ts fresh sealed, 4th use (score_fresh7 --split test, label r8-$N): $(grep -E 'view (model|attributed)' "$R/fresh_test.txt" | tr '\n' ' ')" >> "$LOG"
echo "== Shepardized, sealed half (third use)"
python -I round8/shep_sealed8.py --split sealed --out "$C2/$OUT" --data "$C2/$DATA" --results "$C2/$R/shep" > "$R/shep_sealed.txt" 2>&1
grep -E "recall|precision|clean|subclass" "$R/shep_sealed.txt" | head -20
echo "- $ts Shepardized sealed, 3rd use (compare.py --split sealed, $N): $(grep -E '\(a\) recall +NEG: model NEG_HIST \(strict\)|\(b\) precision +of model NEG_HIST: Shepardized NEG \(strict' "$R/shep_sealed.txt" | tr -s ' ' | tr '\n' ' ')" >> "$LOG"
echo "== the four new keys, h1 (first and only use; label round8)"
for k in fjc_idb_appeals shadow_docket scdb_disposition state_overruled_tables; do
  python -I -B "benchmarks/$k/score.py" --out "$C2/$OUT" --data "$C2/$DATA" --label round8 > "$R/bench_$k.txt" 2>&1
  python -I - "$k" >> "$R/bench_h1_summary.txt" <<'EOF'
import json, sys
k = sys.argv[1]
r = json.load(open("benchmarks/%s/results/round8.h1.json" % k, encoding="utf-8"))
m = r["metrics"]
print(k, "h1", " ".join("%s %d/%d" % (n, v["k"], v["n"]) for n, v in m.items()))
EOF
  echo "- $ts $k h1 (benchmarks/$k/score.py --label round8, $N): $(tail -1 "$R/bench_h1_summary.txt")" >> "$LOG"
done
cat "$R/bench_h1_summary.txt"
echo "SEALED $N done"
