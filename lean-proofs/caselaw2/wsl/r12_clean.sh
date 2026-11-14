#!/bin/bash
# round 12 (agent infra12; = wsl/r11_clean.sh on round-12 names): WSL side of round12/clean12.sh (called by it; not meant to be run alone).
#   bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r12_clean.sh <name> lock|clean [--dry-run]
#   lock   exit 4 when a r12_run.sh of <name> holds ~/caselaw2/r12_name_<name>.lock, else 0
#   clean  deletes data_r12_<name>/, difftest/r12_<name>/ (in the mirror) and ~/caselaw2/r12_bin/run_<name>
N=$1; WHAT=$2; DRY=$3
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ "${N//./}" != "" ] || { echo "bad name"; exit 2; }
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
exec 6> ~/caselaw2/r12_name_$N.lock
flock -n 6 || { echo "refused: a run of $N is active (WSL name lock held)"; exit 4; }
[ "$WHAT" = lock ] && exit 0
[ "$WHAT" = clean ] || { echo "usage: r12_clean.sh <name> lock|clean [--dry-run]"; exit 2; }
for d in "$M/data_r12_$N" "$M/difftest/r12_$N" ~/caselaw2/r12_bin/run_$N; do
  if [ -e "$d" ]; then
    echo "  WSL $(du -sh "$d" | cut -f1) $d"
    [ "$DRY" = --dry-run ] || rm -rf -- "$d"
  else
    echo "  WSL (none) $d"
  fi
done
[ "$DRY" = --dry-run ] || rm -f ~/caselaw2/r12_name_$N.lock
exit 0
