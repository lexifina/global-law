#!/bin/bash
# Same as caselaw-lean-2/run_lean.sh but without `lake build` (uses the existing compiled runner, so a concurrent
# edit of the Lean sources by another agent cannot break or change this run). usage: run_noBuild.sh N data edges out
set -e
W=~/Documents/us-caselaw-lean-work/caselaw-lean-2
N=$1; DATA=$(realpath "$2"); EDGES=$(realpath "$3"); mkdir -p "$4"; OUT=$(realpath "$4"); ASOF=${5:-20261112}
NODES=$(wc -l < "$W/../graph/nodes.tsv")
if [ "$(wc -l < "$DATA/decisions2.tsv")" -lt 100000 ]; then
  NODES=$(awk -F'\t' 'BEGIN{m=0} $1+1>m{m=$1+1} END{print m}' "$DATA/decisions2.tsv"); fi
EXE="$W/runner/.lake/build/bin/caselaw2.exe"
if [ -n "$INTERP" ]; then EXE="lake env lean --run LegalProofs/CaseLaw2/Run.lean"; export PATH="$HOME/.elan/bin:$PATH"; fi
cd "$(dirname "$0")/../../.."
rm -f "$OUT"/*.tsv
seq 0 $((N-1)) | xargs -P 8 -I{} $EXE "$DATA" "$EDGES" {} "$N" "$OUT" "$NODES" "$ASOF"
{ printf 'finding\tciting\tcited\tissue\tdetail\tfirm\tpath\n'; cat "$OUT"/findings-*.tsv 2>/dev/null; } > "$OUT/findings.tsv"
{ printf 'kind\tissue\tcourt1\tcourt2\tanswers1\tanswers2\tholdings1\tholdings2\tasOf\tfirm\n'; cat "$OUT"/splits-*.tsv 2>/dev/null; } > "$OUT/splits.tsv"
cat "$OUT"/certs-*.tsv > "$OUT/certs.tsv" 2>/dev/null || true
cat "$OUT"/status-*.tsv > "$OUT/status.tsv" 2>/dev/null || true
cat "$OUT"/summary-*.tsv > "$OUT/summary.tsv"
rm -f "$OUT"/findings-*.tsv "$OUT"/splits-*.tsv "$OUT"/summary-*.tsv "$OUT"/status-*.tsv "$OUT"/certs-*.tsv
echo LEANDONE
