#!/bin/bash
# ref9: the round-9 synthetic differential after LEAN_READY (setup done separately). Run inside WSL.
D=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round9/agents/ref9/difftest9.sh
L=~/caselaw2/r9ref
export JOBS=${JOBS:-8} BATCHES=${BATCHES:-8}
bash $D kept r9kept1 > $L/run_kept.log 2>&1; echo "kept done $(date +%T)"
bash $D sweep r9sw1 94000 20 > $L/run_sw1.log 2>&1; echo "sweep main done $(date +%T)"
bash $D sweep r9sw1p 95000 10 probe > $L/run_sw1p.log 2>&1; echo "sweep probe done $(date +%T)"
bash $D sweep r9sw1f 96000 10 fuzz=8 > $L/run_sw1f.log 2>&1; echo "sweep fuzz done $(date +%T)"
bash $D regress r9reg1 > $L/run_reg.log 2>&1; echo "regress done $(date +%T)"
