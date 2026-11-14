#!/bin/bash
# WSL side of run_lean_wsl.sh (run with: wsl.exe -d Ubuntu -- bash -l /mnt/c/.../wsl/do.sh <cmd> ...).
# Commands are kept in this file because `wsl.exe -- bash -lc '<inline>'` re-parses the line in an outer shell.
set -e
export PATH="$HOME/.elan/bin:$PATH"
WHERE=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
WLP=/mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
LP=~/caselaw2/lean-proofs
cmd=$1; shift || true
case "$cmd" in
  sync)  bash $WHERE/wsl/sync.sh "${1:-code}" ;;
  build) bash $WHERE/wsl/sync.sh code >/dev/null
         flt () { grep -v '^✔\|^ℹ\|^⚠\|deprecated\|^Hint\|̵\|^trace\|^$' | cut -c1-1500 || true; }
         rc=0
         (cd $LP && lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run > ~/caselaw2/build.log 2>&1) || rc=1
         flt < ~/caselaw2/build.log; [ $rc = 0 ] || exit 1
         (cd $M/runner && lake build caselaw2 > ~/caselaw2/build_runner.log 2>&1) || rc=1
         flt < ~/caselaw2/build_runner.log; [ $rc = 0 ] || exit 1
         ls -la $M/runner/.lake/build/bin/caselaw2; echo BUILD OK ;;
  audit) bash $WHERE/wsl/sync.sh code >/dev/null
         # `audit lock`: the reason is read from wsl/lock_reason.txt (spaces do not survive the wsl.exe command line)
         cd $M; rc=0
         if [ "$1" = lock ]; then python3 audit/audit.py lock --reason "$(cat $WHERE/wsl/lock_reason.txt)" || rc=$?
         else python3 audit/audit.py "${@:-check}" || rc=$?; fi
         cp -p audit/statements.lock $WHERE/audit/; cp -p STATEMENTS.log $WHERE/
         cp -p $LP/LegalProofs/CaseLaw2/Registry.lean $LP/LegalProofs/CaseLaw2/Audit.lean $WLP/LegalProofs/CaseLaw2/
         exit $rc ;;
  run)   bash $WHERE/wsl/sync.sh code >/dev/null
         cd $M && bash run_lean.sh "$@"
         OUT=${4:-out}; mkdir -p "$WHERE/$OUT" && cp -p "$OUT"/*.tsv "$WHERE/$OUT/" ;;
  sh)    cd $M && bash -c "$*" ;;
  *) echo "usage: do.sh sync|build|audit|run|sh ..." >&2; exit 2 ;;
esac
