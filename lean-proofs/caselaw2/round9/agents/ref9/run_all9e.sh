#!/bin/bash
# ref9: after the D9-13 reference change: refsync, then kept / sweeps (same seeds, tag suffix 2) / regress
D=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round9/agents/ref9/difftest9b.sh
L=~/caselaw2/r9ref
export JOBS=${JOBS:-8} BATCHES=${BATCHES:-8}
bash $D refsync > $L/run_refsync.log 2>&1; echo "refsync done $(date +%T) $(grep precedent_ref $L/run_refsync.log)"
bash $D kept r9kept4 > $L/run_kept2.log 2>&1; echo "kept done $(date +%T)"
bash $D sweep r9sw4 94000 20 > $L/run_sw2.log 2>&1; echo "sweep main done $(date +%T)"
bash $D sweep r9sw4p 95000 10 probe > $L/run_sw2p.log 2>&1; echo "sweep probe done $(date +%T)"
bash $D sweep r9sw4f 96000 10 fuzz=8 > $L/run_sw2f.log 2>&1; echo "sweep fuzz done $(date +%T)"
