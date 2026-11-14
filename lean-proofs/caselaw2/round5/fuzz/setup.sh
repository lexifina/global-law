#!/bin/bash
# round-5 fuzz: the fuzzer's own snapshot of the Lean tree inside the WSL mirror, so that a fuzz run never reads
# oleans the lead is rebuilding. Run inside WSL:
#   bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/fuzz/setup.sh [r4]
#   ~/caselaw2/r5fuzz/lp    the current Windows Lean tree (round 5), built here (LegalProofs.CaseLaw2.Run)
#   ~/caselaw2/r5fuzz/lp4   (with `r4`) the same tree with LegalProofs/CaseLaw2 replaced by round5/pre/lean, the
#                           round-4 final sources: the baseline runner for the "class file absent" property
#   ~/caselaw2/r5fuzz/w     fixtures (FUZZ_W)
# Nothing outside ~/caselaw2/r5fuzz is written. The main mirror's .lake is only copied (once), and only while no
# lake process is running.
export PATH="$HOME/.elan/bin:$PATH"
WIN=/mnt/c/Users/$USER/Documents
C2=$WIN/us-caselaw-lean-work/caselaw-lean-2
S=~/caselaw2/r5fuzz
mkdir -p $S/lp $S/w
if [ ! -d $S/lp/.lake ]; then
  while pgrep -x lake >/dev/null; do sleep 5; done
  cp -a ~/caselaw2/lean-proofs/.lake $S/lp/.lake
fi
rsync -a --delete --exclude .lake --exclude data --exclude video --exclude __pycache__ $WIN/global-law-lean/lean-proofs/ $S/lp/
rsync -a --delete $C2/fixtures/ $S/w/fixtures/
( cd $S/lp && lake build LegalProofs.CaseLaw2.Run > $S/build.log 2>&1 ); rc=$?
grep -A8 '^error' $S/build.log | head -30
echo "BUILD lp rc=$rc $(date +%H:%M:%S)"
if [ "$1" = r4 ]; then
  mkdir -p $S/lp4
  rsync -a --delete $S/lp/ $S/lp4/
  rsync -a --delete $C2/round5/pre/lean/ $S/lp4/LegalProofs/CaseLaw2/
  ( cd $S/lp4 && lake build LegalProofs.CaseLaw2.Run > $S/build4.log 2>&1 ); rc4=$?
  grep -A8 '^error' $S/build4.log | head -30
  echo "BUILD lp4 rc=$rc4 $(date +%H:%M:%S)"
fi
