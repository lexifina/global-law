#!/bin/bash
# usage: tools/run_lean.sh <in.tsv> <out.tsv>   (runs the Lean runner with our private olean on LEAN_PATH)
W="$HOME/Documents/us-caselaw-lean-work/uses/amendments"
P="$HOME/Documents/global-law-lean/lean-proofs"
TC="C:\Users\alany\.elan\toolchains\leanprover--lean4---v4.35.0"
export LEAN_SYSROOT="$TC"
export LEAN_PATH="$(cygpath -w "$W/olean");$TC\lib\lean"
IN="$(cygpath -w "$(realpath "$1")")"; OUT="$(cygpath -w "$(realpath -m "$2")")"
cd "$P"
exec "/c/Users/alany/.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean" --run LegalProofs/USCaseLaw/RunAmendmentCheck.lean "$IN" "$OUT"
