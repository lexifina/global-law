#!/bin/bash
# Round 3, WSL part of report/refresh_all.sh: extract the declaration graph of case-law v1 and v2 from the COMPILED
# environment (tools/CaseLawAnatomy.lean) as JSON lines. Read-only on the mirror: no sync, no `lake build`. Run it
# after the final build (the oleans of LegalProofs.USCaseLaw and LegalProofs.CaseLaw2 must exist in the mirror).
#   wsl.exe -d Ubuntu -- bash -l /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r3_artefacts.sh [OUT.jsonl]
# OUT defaults to /mnt/c/Users/$USER/Documents/global-law-lean/caselaw-anatomy.jsonl (where the generator's docstring
# puts it). The extraction file is read from the Windows tree (the source of truth), the oleans from the mirror.
set -euo pipefail
export PATH="$HOME/.elan/bin:$PATH"
WLP=/mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs
LP=~/caselaw2/lean-proofs
OUT=${1:-/mnt/c/Users/$USER/Documents/global-law-lean/caselaw-anatomy.jsonl}
SRC=$WLP/tools/CaseLawAnatomy.lean
TMP=$(mktemp /tmp/caselaw-anatomy.XXXXXX)
trap 'rm -f "$TMP" "$TMP.err"' EXIT
[ -f "$SRC" ] || { echo "r3_artefacts: FAILED: missing $SRC" >&2; exit 1; }
[ -d "$LP/.lake/build/lib" ] || { echo "r3_artefacts: FAILED: no build in $LP (run the final build first)" >&2; exit 1; }
t0=$(date +%s)
cd "$LP"
if ! lake env lean "$SRC" > "$TMP" 2> "$TMP.err"; then
  echo "r3_artefacts: FAILED: lake env lean $SRC" >&2
  head -c 3000 "$TMP.err" >&2; head -c 3000 "$TMP" | grep -v '^{' >&2 || true
  exit 1
fi
# every line must be a JSON object; anything else is a Lean message (error or warning) and fails the step
if grep -vq '^{"n":' "$TMP"; then
  echo "r3_artefacts: FAILED: non-JSON lines in the output:" >&2; grep -v '^{"n":' "$TMP" | head -20 >&2; exit 1
fi
n=$(wc -l < "$TMP")
[ "$n" -ge 1000 ] || { echo "r3_artefacts: FAILED: only $n declarations" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"
cp "$TMP" "$OUT.tmp" && mv "$OUT.tmp" "$OUT"
echo "r3_artefacts: $n declarations, $(cut -d'"' -f8 "$OUT" | sort -u | wc -l) modules, $(( $(date +%s) - t0 )) s"
cut -d'"' -f8 "$OUT" | sort | uniq -c | sed 's/^/  /'
echo "r3_artefacts: wrote $OUT"
