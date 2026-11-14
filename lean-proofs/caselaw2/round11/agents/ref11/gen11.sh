#!/bin/bash
# round 11, ref11: generate / self-check round-11 universes in WSL scratch (~/caselaw2/r11ref), reference = the
# current Windows reference synced to ~/caselaw2/r11ref/cur; expectations from round11/pre/ref (round-10 final).
#   gen11.sh gen <dir> <seed> <rounds> [--probe | --fuzz K]     -> ~/caselaw2/r11ref/<dir>, then the self-check
#   gen11.sh check <dir> | empty <dir>
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round11/agents/ref11
S=~/caselaw2/r11ref
mkdir -p $S/cur/tools/caselaw2 $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
export CASELAW2_REF=$S/cur/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
cmd=$1; dir=$2; shift 2
case "$cmd" in
  gen)
    seed=$1; rounds=$2; shift 2
    rm -rf $S/$dir; mkdir -p $S/$dir
    python3 -X utf8 $ME/make_r11.py gen --seed $seed --rounds $rounds --out $S/$dir "$@" 2>&1 | grep -v '^  ' | tail -40
    python3 -X utf8 $ME/make_r11.py check $S/$dir > $S/$dir.selfcheck.txt 2>&1
    cp $S/$dir.selfcheck.txt $ME/results/$dir.selfcheck.txt
    grep -v '^  ' $S/$dir.selfcheck.txt | tail -n 30; grep '^  at_' $S/$dir.selfcheck.txt | head -80 ;;
  check)
    python3 -X utf8 $ME/make_r11.py check $S/$dir > $S/$dir.selfcheck.txt 2>&1
    cp $S/$dir.selfcheck.txt $ME/results/$dir.selfcheck.txt
    grep -v '^  ' $S/$dir.selfcheck.txt | tail -n 30 ;;
  empty)
    python3 -X utf8 $ME/make_r11.py empty $S/$dir 2>&1 | tail -20 ;;
esac
