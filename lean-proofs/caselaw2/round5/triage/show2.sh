#!/bin/bash
# triage: rows of the (2)/(3) universes (read only)
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest/r5_drt_a
T=/mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref
cd $M
show() {
  u=$1; shift
  echo "################ $u $*"
  python3 $T/drt_show.py r$u "$@"
  echo "== succession"; cat r$u/data/succession.tsv
  echo "== witness"; cat r$u/data/treatment_witness.tsv
  echo "== class"; cat r$u/data/treatment_class.tsv 2>/dev/null
}
show 73028 201 202
show 73048 177 178
show 73124 $(awk -F'\t' '$1=="tr4"{print $2, $3}' r73124/data/treatments.tsv)
show 73060 185 186
show 73158 187 189
