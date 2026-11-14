#!/usr/bin/env bash
# Round 7: the single sealed run (lead only, once, after round7/FREEZE.md).
#   bash round7/score_sealed7.sh <frozen name>
# 1. fresh lists, sealed half (third use), both date views: round7/score_fresh7.py --split test
# 2. Shepardized, sealed half (second use): round6/shepardized/compare.py --split sealed on round7 outputs
# 3. time-split held-out key (first use): round7/heldout/score_heldout.py on round6 final2 and on the frozen build
# Only aggregate output is printed; every run is appended to round7/SEALED_LOG.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
C2="$(cd "$HERE/.." && pwd)"
N="${1:?usage: score_sealed7.sh <frozen name>}"
[ -f "$HERE/FREEZE.md" ] || { echo "refused: round7/FREEZE.md missing"; exit 3; }
grep -q "Variant \`$N\`" "$HERE/FREEZE.md" || { echo "refused: FREEZE.md does not name $N"; exit 3; }
cd "$C2"
python -X utf8 round7/freeze7.py --check
OUT="round7/out/$N"; DATA="round7/stage/$N"; R="round7/results/$N/sealed"; mkdir -p "$R"
LOG="$HERE/SEALED_LOG.md"
[ -f "$LOG" ] || printf '# Round 7 sealed runs (one line per run)\n\n' > "$LOG"
ts=$(date '+%Y-%m-%d %H:%M:%S')
echo "== fresh lists, sealed half"
python -X utf8 round7/score_fresh7.py --split test --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" \
  --data "$DATA" --label "r7-$N" > "$R/fresh_test.txt" 2>&1
grep -E "strict|lenient|view" "$R/fresh_test.txt" | head -20
echo "- $ts fresh sealed (score_fresh7 --split test, label r7-$N): $(grep -E 'view (model|attributed)' "$R/fresh_test.txt" | tr '\n' ' ')" >> "$LOG"
echo "== Shepardized, sealed half"
python -I round7/shep_sealed7.py --split sealed --out "$C2/$OUT" --data "$C2/$DATA" --results "$C2/$R/shep" > "$R/shep_sealed.txt" 2>&1
grep -E "recall|precision|clean|subclass" "$R/shep_sealed.txt" | head -20
echo "- $ts Shepardized sealed (compare.py --split sealed, $N): $(grep -E '\(a\) recall +NEG: model NEG_HIST \(strict\)|\(b\) precision +of model NEG_HIST: Shepardized NEG \(strict' "$R/shep_sealed.txt" | tr -s ' ' | tr '\n' ' ')" >> "$LOG"
echo "== time-split held-out key"
python -I round7/heldout/score_heldout.py --status round6/history/out/final2/status.tsv \
  --history round6/history/stage/final2/history.tsv --certs round6/history/out/final2/certs.tsv --label r6-final2 > "$R/heldout_r6.txt" 2>&1 || true
python -I round7/heldout/score_heldout.py --status "$OUT/status.tsv" \
  --history "$DATA/history.tsv" --certs "$OUT/certs.tsv" --label "r7-$N" > "$R/heldout_r7.txt" 2>&1 || true
tail -30 "$R/heldout_r6.txt"; tail -30 "$R/heldout_r7.txt"
echo "- $ts time-split key scored once on r6-final2 and r7-$N (round7/results/$N/sealed/heldout_*.txt)" >> "$LOG"
echo "SEALED $N done"
