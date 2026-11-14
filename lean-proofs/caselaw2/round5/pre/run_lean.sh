#!/bin/bash
# caselaw-lean-2 runner, sharded like v1, compiled (runner/ package, lean_exe caselaw2).
#   usage: run_lean.sh <shards> [data-dir] [edges-dir] [out-dir] [asOf yyyymmdd]
# defaults: data = data, edges = ../lean-in-v3, out = out, asOf = 20261112
# fixtures: ./run_lean.sh 2 fixtures/data fixtures/edges fixtures/out
# interpreted fallback: set INTERP=1 (lake env lean --run LegalProofs/CaseLaw2/Run.lean)
# parallel shards: PAR (default 8). Runs unchanged under Linux (WSL): see run_lean_wsl.sh.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
N=${1:-8}
DATA=$(cd "$HERE" && realpath "${2:-data}")
EDGES=$(cd "$HERE" && realpath "${3:-../lean-in-v3}")
OUT=$(cd "$HERE" && mkdir -p "${4:-out}" && realpath "${4:-out}")
ASOF=${5:-20261112}
# the node count: graph/nodes.tsv, or its line count in graph/nodes.count (the WSL mirror ships only the count)
if [ -f "$HERE/../graph/nodes.count" ]; then NODES=$(tr -d ' 
' < "$HERE/../graph/nodes.count"); else NODES=$(wc -l < "$HERE/../graph/nodes.tsv"); fi
if [ -f "$DATA/decisions2.tsv" ] && [ "$(wc -l < "$DATA/decisions2.tsv")" -lt 100000 ]; then
  # FB-L8: only digit ids below 10^8 count (a huge id must not print as 1e+40, nor allocate 10^9 entries; the
  # loader then reports such rows as out of range)
  NODES=$(awk -F'\t' 'BEGIN{m=0} $1 ~ /^[0-9]+$/ && length($1) <= 8 && $1+1>m {m=$1+1} END{printf "%d\n", m}' "$DATA/decisions2.tsv")
fi
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
# lean-proofs sits beside us-caselaw-lean-work on Windows and in the WSL mirror (wsl/sync.sh)
LP="$(cd "$HERE/../../global-law-lean/lean-proofs" && pwd)"
EXT=.exe; [ "$(uname -s)" = Linux ] && EXT=
RUN="lake env lean --run LegalProofs/CaseLaw2/Run.lean"
if [ -z "$INTERP" ]; then
  (cd "$HERE/runner" && lake build caselaw2 >/dev/null)
  EXE="$HERE/runner/.lake/build/bin/caselaw2$EXT"
  # Windows Application Control may block locally built executables: fall back to the interpreter
  if "$EXE" >/dev/null 2>&1 || [ $? -eq 2 ]; then RUN="$EXE"; else echo "compiled runner blocked; using lake env lean --run" >&2; fi
fi
cd "$LP"
rm -f "$OUT"/*.tsv
seq 0 $((N-1)) | xargs -P ${PAR:-8} -I{} $RUN "$DATA" "$EDGES" {} "$N" "$OUT" "$NODES" "$ASOF"
# merge the per-shard files, with headers
merge () {  # name header
  { printf '%s\n' "$2"; cat "$OUT"/"$1"-*.tsv 2>/dev/null; } > "$OUT/$1.tsv"
}
merge status  $'node\tissue\tholding\tfrom\tto\tstatus\tclass\tfirm\twitness_row\tactor\tpath'
merge findings $'finding\tciting\tcited\tissue\tdetail\tfirm\tpath'
merge certs   $'table\tid\tresult_all\tresult_firm'
merge splits  $'kind	issue\tcourt1\tcourt2\tanswers1\tanswers2\tholdings1\tholdings2\tasOf\tfirm'
# round 2: per-line status rows (DEVIATIONS 75) and Horty bases (DEVIATIONS 78)
merge status_lines $'node	issue	holding	from	to	status	class	firm	witness_row	actor	path	line'
merge horty   $'family	court	verdict	cases	firm'
cat "$OUT"/summary-*.tsv > "$OUT/summary.tsv"
rm -f "$OUT"/status_lines-*.tsv "$OUT"/horty-*.tsv "$OUT"/status-*.tsv "$OUT"/findings-*.tsv "$OUT"/certs-*.tsv "$OUT"/splits-*.tsv "$OUT"/summary-*.tsv
echo LEANDONE
