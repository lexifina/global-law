#!/bin/bash
# round 12 (agent infra12; = round11/clean11.sh on round-12 paths): delete one variant's intermediates.   usage (Git Bash): bash round12/clean12.sh <name> [--dry-run]
#   deletes round12/stage/<name>/, round12/out/<name>/ and, in WSL, ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/
#   data_r12_<name>/ + difftest/r12_<name>/ + ~/caselaw2/r12_bin/run_<name> (the R12BIN copy; built binaries
#   ~/caselaw2/r12_bin/caselaw2_<name> are kept). Keeps round12/results/<name>/.
#   Refused: a name listed in round12/KEEP.txt (one name per line, first word; the lead writes base / best / frozen
#   names there), a bad name, and a name whose r12_run.sh is running (its name lock is held).
#   Only round12/ folders and the round-12 WSL dirs of that name are touched; stage tables that are hard links to
#   round11/stage/v11d lose only this directory entry (the base file stays).
C2="$(cd "$(dirname "$0")/.." && pwd)"
N=$1; DRY=$2
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ "${N//./}" != "" ] || { echo "usage: clean12.sh <name> [--dry-run]"; exit 2; }
if [ -f "$C2/round12/KEEP.txt" ] && awk -v n="$N" '{sub(/\r$/,"")} $1==n{f=1} END{exit !f}' "$C2/round12/KEEP.txt"; then
  echo "refused: $N is listed in round12/KEEP.txt"; exit 3
fi
WR=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r12_clean.sh  # the WSL side (a script file:
# a multi-line command passed through wsl.exe loses its newlines and is expanded by the outer shell)
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash "$WR" "$N" lock || exit 4
S="$C2/round12/stage/$N"; O="$C2/round12/out/$N"
echo "clean $N:"
for d in "$S" "$O"; do
  if [ -d "$d" ]; then
    own=$(find "$d" -type f -exec stat -c '%h %s' {} + 2>/dev/null | awk '$1==1{s+=$2} END{printf "%.1f MB", s/1048576}')
    echo "  ${d#$C2/} (own files, not hard links to the base: $own)"
    [ "$DRY" = --dry-run ] || rm -rf -- "$d"
  else
    echo "  (none) ${d#$C2/}"
  fi
done
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash "$WR" "$N" clean "$DRY"
[ -d "$C2/round12/results/$N" ] && echo "  kept round12/results/$N/"
[ "$DRY" = --dry-run ] && echo "dry run: nothing deleted" || echo "CLEANED $N"
