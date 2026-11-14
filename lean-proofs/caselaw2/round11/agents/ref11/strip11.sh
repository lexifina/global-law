#!/bin/bash
# round 11, ref11: copies of failing universes (fail/<tag>/) with every round-11 input removed (well-formed
# anchorTribunal claim lines, history_identity.tsv), run against the frozen ROUND-10 binary (caselaw2_lean10 e7e32592)
# with the current reference: a disagreement that remains is pre-existing.   strip11.sh <tag> <newtag>
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round11/agents/ref11
S=~/caselaw2/r11ref
rm -rf $S/strip/$2; mkdir -p $S/strip/$2
rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $ME/fail/$1/ $S/strip/$2/
for u in $S/strip/$2/*/; do
  rm -f $u/data/history_identity.tsv
  python3 - $u/data/history_claim.tsv <<'PY'
import sys
p = sys.argv[1]
ls = open(p, 'rb').read().split(b'\n')
def at(l):
    try:
        l.decode('utf-8')
    except UnicodeDecodeError:
        return False
    q = l.rstrip(b'\r').split(b'\t')
    return len(q) == 3 and q[1] == b'anchorTribunal'
open(p, 'wb').write(b'\n'.join(l for l in ls if not at(l)))
PY
done
BIN=~/caselaw2/r10_bin/caselaw2_lean10 bash $ME/difftest11.sh dirs $2 $S/strip/$2 | head -20
