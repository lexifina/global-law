#!/bin/bash
# lead monitor: markers, LEAN_REQUESTs, disk, silent agents. Prints only changes.
R=~/Documents/us-caselaw-lean-work/caselaw-lean-2/round12
declare -A seen
for m in INFRA_READY NODES_READY LEAN_READY FREEZE.md FRESH_KEYS.txt audit/READY data_orders/DATA_READY_A data_orders/LIGATURE_READY data_orders/DATA_READY data_orders/FEASIBILITY.md data_orders/FORMAT.md; do [ -e "$R/$m" ] && seen[$m]=1; done
for f in "$R"/agents/*/LEAN_REQUEST.md; do [ -e "$f" ] && seen["lr:$f:$(stat -c %Y "$f")"]=1; done
while true; do
  now=$(date +%s)
  for m in INFRA_READY NODES_READY LEAN_READY FREEZE.md FRESH_KEYS.txt audit/READY data_orders/DATA_READY_A data_orders/LIGATURE_READY data_orders/DATA_READY data_orders/FEASIBILITY.md data_orders/FORMAT.md; do
    if [ -e "$R/$m" ] && [ -z "${seen[$m]}" ]; then seen[$m]=1; echo "$(date +%H:%M) marker $m"; fi
  done
  for f in "$R"/agents/*/LEAN_REQUEST.md; do
    [ -e "$f" ] || continue
    k="lr:$f:$(stat -c %Y "$f")"
    if [ -z "${seen[$k]}" ]; then seen[$k]=1; echo "$(date +%H:%M) LEAN_REQUEST $(basename $(dirname $f))"; fi
  done
  av=$(df -Pk /c | awk 'NR==2{print int($4/1048576)}')
  if [ "$av" -lt 12 ]; then
    b=$(( now / 600 ))
    if [ -z "${seen[disk$b]}" ]; then seen[disk$b]=1; echo "$(date +%H:%M) DISK low: ${av} GB free"; fi
  fi
  for d in "$R"/agents/*/; do
    a=$(basename "$d"); grep -qx "$a" "$R/lead/done.txt" 2>/dev/null && continue
    n="$d/NOTES.md"
    [ -e "$n" ] || continue
    age=$(( now - $(stat -c %Y "$n") ))
    if [ $age -gt 1200 ]; then
      b=$(( now / 1200 ))
      if [ -z "${seen[sil$a$b]}" ]; then seen[sil$a$b]=1; echo "$(date +%H:%M) SILENT $a NOTES.md ${age}s"; fi
    fi
  done
  sleep 60
done
