#!/bin/bash
# waitlean.sh [seconds]: wait (in WSL) until round10/LEAN_READY exists or ref10's INBOX.md grows, at most [seconds].
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
n=${1:-540}
n0=$(wc -l < $W/round10/agents/ref10/INBOX.md)
for i in $(seq 1 $((n / 10))); do
  [ -f $W/round10/LEAN_READY ] && { echo "LEAN_READY: $(head -c 400 $W/round10/LEAN_READY)"; exit 0; }
  n1=$(wc -l < $W/round10/agents/ref10/INBOX.md)
  [ "$n1" != "$n0" ] && { echo "INBOX: $(tail -n $((n1 - n0)) $W/round10/agents/ref10/INBOX.md | cut -c1-600)"; exit 0; }
  sleep 10
done
echo "still waiting $(date +%H:%M)"; exit 1
