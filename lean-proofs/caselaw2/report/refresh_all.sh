#!/bin/bash
# Refresh every generated artefact of the report, once, after the final Lean build and runs (Git Bash on Windows).
#   bash report/refresh_all.sh
# Steps (each fails loudly and stops the script):
#   1. WSL: wsl/r3_artefacts.sh  -> caselaw-anatomy.jsonl (declaration graph of the compiled environment; no build)
#   2. tools/caselaw/caselaw_v1v2_anatomy.py -> caselaw-v1-v2.svg and .json
#   3. heatmaps/compute.py, heatmaps/plot.py (venv python with matplotlib) -> heatmaps/*.png, .svg, .webp, *.json
#   4. make_report.py -> the HTML report
# Environment overrides (defaults write the real files):
#   OUT=<dir>        artefact folder instead of report/ (figure in <dir>, heatmaps in <dir>/heatmaps, the jsonl and
#                    the HTML in <dir>). Used for dry runs: OUT=work/round3/artefacts bash report/refresh_all.sh
#   REPORT_HTML=<f>  the HTML file (default ~/Documents/html-reports/caselaw-lean-2.html, or <OUT>/caselaw-lean-2.html)
#   SKIP_WSL=1       reuse the existing jsonl (step 1 skipped)
#   HM_PY=<python>   python with matplotlib, numpy, Pillow for step 3
#   PY=<python>      python for steps 2 and 4 (default: python)
# Needs first, from the coordinator: the final WSL build (oleans in ~/caselaw2/lean-proofs), out/*.tsv copied back
# (wsl/collect.sh), data/*.tsv final, eval/results.json (score.py), and the docs the report reads (ROUND3.md, LEAN.md,
# DIFFTEST.md, DEVIATIONS.md, LIMITS.md, TRUST.md, STATEMENTS.log, hunt/summary.json).
set -euo pipefail
export MSYS_NO_PATHCONV=1
HERE="$(cd "$(dirname "$0")" && pwd)"
C2="$(dirname "$HERE")"
LP="$HOME/Documents/global-law-lean/lean-proofs"
PY=${PY:-python}
HM_PY=${HM_PY:-$HOME/AppData/Local/Temp/claude/ac2e06910e878915/d3a415f9-df9d-4894-ba8f-d56429e7699a/scratchpad/hm/Scripts/python.exe}
win() { cygpath -m "$1"; }            # C:/... for Windows programs
mnt() { cygpath -u "$1" | sed -E 's#^/([a-zA-Z])/#/mnt/\L\1/#'; }   # /mnt/c/... for WSL
step() { echo; echo "=== [$1] $2 ($(date +%H:%M:%S))"; }
die() { echo "refresh_all: FAILED at step $1: $2" >&2; exit 1; }
need() { [ -s "$2" ] || die "$1" "missing or empty: $2"; }
newer() { [ "$2" -nt "$STAMP" ] || die "$1" "not rewritten by this run: $2"; }

if [ -n "${OUT:-}" ]; then
  mkdir -p "$OUT"; ART="$(cd "$OUT" && pwd)"
  JSONL="$ART/caselaw-anatomy.jsonl"
  HTML=${REPORT_HTML:-$ART/caselaw-lean-2.html}
  export HEATMAPS_OUT="$(win "$ART/heatmaps")"
else
  ART="$HERE"
  JSONL="$(dirname "$LP")/caselaw-anatomy.jsonl"
  HTML=${REPORT_HTML:-$HOME/Documents/html-reports/caselaw-lean-2.html}
  unset HEATMAPS_OUT
fi
mkdir -p "$ART/heatmaps"
STAMP="$ART/.refresh_stamp"; : > "$STAMP"; sleep 1
T0=$(date +%s)
echo "refresh_all: artefacts -> $ART ; report -> $HTML"

for f in out/findings.tsv out/status.tsv data/decisions2.tsv data/treatments.tsv data/history.tsv data/holdings.tsv; do
  need 0 "$C2/$f"
done
[ -x "$HM_PY" ] || die 0 "no heatmap python at $HM_PY (set HM_PY)"

step 1 "WSL: declaration graph of the compiled environment"
if [ "${SKIP_WSL:-}" = 1 ]; then
  echo "SKIP_WSL=1: reusing $JSONL"
else
  wsl.exe -d Ubuntu -- bash -l "$(mnt "$C2/wsl/r3_artefacts.sh")" "$(mnt "$JSONL")" || die 1 "wsl/r3_artefacts.sh"
  newer 1 "$JSONL"
fi
need 1 "$JSONL"

step 2 "v1/v2 declaration figure"
"$PY" -X utf8 "$(win "$LP/tools/caselaw/caselaw_v1v2_anatomy.py")" "$(win "$JSONL")" "$(win "$ART/caselaw-v1-v2.svg")" \
  --json "$(win "$ART/caselaw-v1-v2.json")" --data "$(win "$C2/data")" > "$ART/.anatomy.log" || die 2 "caselaw_v1v2_anatomy.py (see above)"
newer 2 "$ART/caselaw-v1-v2.svg"; newer 2 "$ART/caselaw-v1-v2.json"
"$PY" -X utf8 - "$(win "$ART/caselaw-v1-v2.json")" "$(win "$ART/caselaw-v1-v2.svg")" <<'EOF' || die 2 "figure check"
import json, re, sys
j = json.load(open(sys.argv[1], encoding="utf-8")); svg = open(sys.argv[2], encoding="utf-8").read()
dots = svg.count("<circle"); decl = sum(p["decl"] for p in j["panels"])
assert dots == decl == sum(j["per_column"].values()), (dots, decl, j["per_column"])
for p in j["panels"]:
    assert f">{p['decl']:,}</text>" in svg and f">{p['thm']:,}</text>" in svg, p
print(f"v1: {j['panels'][0]['decl']} declarations, {j['panels'][0]['thm']} theorems; "
      f"v2: {j['panels'][1]['decl']} declarations, {j['panels'][1]['thm']} theorems, {j['panels'][1]['lines']:,} lines, "
      f"{j['panels'][1]['mods']} modules; cross links {j['cross_links']}; dots drawn {dots}")
EOF

step 3 "heatmaps: compute.py"
"$HM_PY" -X utf8 "$(win "$HERE/heatmaps/compute.py")" > "$ART/heatmaps/.compute.log" || die 3 "heatmaps/compute.py"
newer 3 "$ART/heatmaps/series.json"; newer 3 "$ART/heatmaps/series/badlaw.tsv"; newer 3 "$ART/heatmaps/series/broken.tsv"
step 3 "heatmaps: plot.py"
"$HM_PY" -X utf8 "$(win "$HERE/heatmaps/plot.py")" > "$ART/heatmaps/.plot.log" || die 3 "heatmaps/plot.py"
[ -n "${OUT:-}" ] || "$PY" -X utf8 "$(win "$HERE/heatmaps/update_md.py")" || die 3 "heatmaps/update_md.py"
newer 3 "$ART/heatmaps/heatmaps.json"
for s in caselaw_bad_law_by_day caselaw_precedent_broken_by_day uscode_vulnerabilities_by_day uscode_xref_by_day \
         uscode_amend_by_day uscode_dup_by_day; do
  for e in png svg webp; do newer 3 "$ART/heatmaps/$s.$e"; done
done
"$PY" -X utf8 - "$(win "$ART/heatmaps/heatmaps.json")" <<'EOF' || die 3 "heatmaps summary"
import json, sys
j = json.load(open(sys.argv[1], encoding="utf-8"))
for k, v in j.items():
    pk = v["peaks"][0]
    print(f"{k:10s} total {v['total']:>7,}  years {v['years'][0]}-{v['years'][1]}  peak {pk['count']:,} on {pk['day']}")
EOF
echo "(heatmaps/HEATMAPS.md is hand-written: its table and totals must be edited to the figures above)"

step 4 "report"
"$PY" -X utf8 "$(win "$HERE/make_report.py")" --out "$(win "$HTML")" --artefacts "$(win "$ART")" || die 4 "make_report.py"
newer 4 "$HTML"
if grep -q "failed to render" "$HTML"; then die 4 "a report section failed to render (search the HTML for 'failed to render')"; fi
n_pend=$(grep -c 'class="pending"' "$HTML" || true)
echo "pending boxes in the report: $n_pend"
grep -q "predates the last change to the Lean sources" "$HTML" && echo "WARNING: the report says the figure predates the Lean sources (a .lean file changed after step 2)"

rm -f "$STAMP"
echo
echo "refresh_all: done in $(( $(date +%s) - T0 )) s. Outputs:"
ls -la "$JSONL" "$ART/caselaw-v1-v2.svg" "$ART/caselaw-v1-v2.json" "$ART/heatmaps/heatmaps.json" "$ART/heatmaps/series.json" \
       "$ART/heatmaps/"*.webp "$HTML" | awk '{print "  " $5 "\t" $6 " " $7 " " $8 "\t" $9}'
