#!/bin/bash
# round 11, ref11: a wider self-check (main seeds, probe seeds) in WSL scratch, deleted after.
#   wide11.sh <tag> <main seed> <main rounds> <probe seed> <probe rounds>
B=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round11/agents/ref11/gen11.sh
tag=$1
bash $B gen $tag $2 $3 2>&1 | grep -v '^  at_' | tail -8
bash $B gen ${tag}q $4 $5 --probe 2>&1 | grep -v '^  at_' | tail -8
rm -rf ~/caselaw2/r11ref/$tag ~/caselaw2/r11ref/${tag}q
