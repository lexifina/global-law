#!/bin/bash
# round 11 (agent infra11; = round10/clean10.sh on round-11 paths): delete one variant's intermediates.   usage (Git Bash): bash round11/clean11.sh <name> [--dry-run]
#   deletes round11/stage/<name>/, round11/out/<name>/ and, in WSL, ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/
#   data_r11_<name>/ + difftest/r11_<name>/ + ~/caselaw2/r11_bin/run_<name> (the R11BIN copy; built binaries
#   ~/caselaw2/r11_bin/caselaw2_<name> are kept). Keeps round11/results/<name>/.
#   Refused: a name listed in round11/KEEP.txt (one name per line, first word; the lead writes base / best / frozen
#   names there), a bad name, and a name whose r11_run.sh is running (its name lock is held).
#   Only round11/ folders and the round-11 WSL dirs of that name are touched; stage tables that are hard links to
#   round10/stage/v10d lose only this directory entry (the base file stays).
C2="$(cd "$(dirname "$0")/.." && pwd)"
N=$1; DRY=$2
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ "${N//./}" != "" ] || { echo "usage: clean11.sh <name> [--dry-run]"; exit 2; }
if [ -f "$C2/round11/KEEP.txt" ] && awk -v n="$N" '{sub(/\r$/,"")} $1==n{f=1} END{exit !f}' "$C2/round11/KEEP.txt"; then
  echo "refused: $N is listed in round11/KEEP.txt"; exit 3
fi
WR=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r11_clean.sh  # the WSL side (a script file:
# a multi-line command passed through wsl.exe loses its newlines and is expanded by the outer shell)
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash "$WR" "$N" lock || exit 4
S="$C2/round11/stage/$N"; O="$C2/round11/out/$N"
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
[ -d "$C2/round11/results/$N" ] && echo "  kept round11/results/$N/"
[ "$DRY" = --dry-run ] && echo "dry run: nothing deleted" || echo "CLEANED $N"
