#!/bin/bash
# infra10: compare a round-10 Lean output folder with a reference one (default round9/out/v9c): every output table
# cmp, summary.tsv also with the timing lines (load_ms / run_ms) removed. (= round9/agents/infra9/cmp_out.sh)
#   bash round10/agents/infra10/cmp_out.sh <round10/out/name> [ref dir]
C2="$(cd "$(dirname "$0")/../../.." && pwd)"
A="$C2/$1"; B="$C2/${2:-round9/out/v9c}"
bad=0
for f in "$B"/*.tsv; do
  b=$(basename "$f")
  if [ "$b" = summary.tsv ]; then
    if cmp -s "$f" "$A/$b"; then echo "same      $b"
    elif cmp -s <(grep -v -E $'^(load_ms|run_ms)\t' "$f") <(grep -v -E $'^(load_ms|run_ms)\t' "$A/$b"); then echo "same      $b (timing lines excepted)"
    else echo "DIFFERENT $b"; bad=1; fi
  elif cmp -s "$f" "$A/$b"; then echo "same      $b"
  else echo "DIFFERENT $b"; bad=1; fi
done
for f in "$A"/*.tsv; do [ -e "$B/$(basename "$f")" ] || { echo "EXTRA     $(basename "$f")"; bad=1; }; done
[ $bad = 0 ] && echo "ALL SAME" || echo "MISMATCH"
exit $bad
