#!/bin/bash
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/difftest
for f in "$@"; do echo "== $f"; cat $f; done
