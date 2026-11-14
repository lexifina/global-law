#!/bin/bash
# round 9 (lean9): build the batch-2 staging tree (round9/agents/lean9/b2/tree) in a separate WSL copy
# (~/caselaw2/b2/lean-proofs), so the main mirror and its runner stay untouched while the section-4 gates run.
#   usage: r9_b2build.sh <lake target> ...
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
B=~/caselaw2/b2/lean-proofs
rsync -a $W/round9/agents/lean9/b2/tree/ $B/
cd $B
rc=0
lake build "$@" > ~/caselaw2/b2_build.log 2>&1 || rc=1
grep -v '^✔\|^ℹ\|^⚠\|deprecated\|^trace\|linter\|^Note: This linter\|^Hint\|Omit it from\|\[apply\]\|i̵\|^ *(\"\|^ *\[\"' ~/caselaw2/b2_build.log | grep -v '^\s*$' | cut -c1-300 | head -${LINES_MAX:-80}
[ $rc = 0 ] && echo BUILD OK || echo BUILD FAILED
exit $rc
