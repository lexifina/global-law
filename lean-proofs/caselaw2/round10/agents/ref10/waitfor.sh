#!/bin/bash
# waitfor.sh <file> [seconds]: wait (in WSL) until <file> exists and is non-empty, at most [seconds] (default 540).
f=$1; n=${2:-540}
for i in $(seq 1 $((n / 5))); do
  [ -s "$f" ] && { echo "ready: $f"; exit 0; }
  sleep 5
done
echo "timeout: $f"; exit 1
