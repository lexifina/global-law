#!/bin/sh
# Build the kernel and every country package in this folder. Needs elan (Lean 4 v4.35.0 is pinned per project).
# Usage: ./build_all.sh [jobs]   (default 4 parallel builds)
cd "$(dirname "$0")" || exit 1
jobs=${1:-4}
(cd kernel && lake build) || { echo "kernel: FAILED"; exit 1; }
find . -path ./kernel -prune -o -name lakefile.toml -print | sed 's#/lakefile.toml$##' | sort |
  xargs -P "$jobs" -I{} sh -c 'cd "{}" && lake build >/dev/null 2>&1 && echo "ok     {}" || echo "FAILED {}"' |
  tee build_all.log
if grep -q '^FAILED' build_all.log; then echo "some packages failed (build_all.log)"; exit 1; fi
echo "all $(grep -c '^ok' build_all.log) packages built"
