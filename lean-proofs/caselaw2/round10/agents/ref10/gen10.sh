#!/bin/bash
# round 10, ref10: generate / self-check round-10 universes in WSL scratch (~/caselaw2/r10ref), reference = the
# current Windows reference synced to ~/caselaw2/r10ref/cur.
#   gen10.sh gen <dir> <seed> <rounds> [--probe | --fuzz K]     -> ~/caselaw2/r10ref/<dir>, then the self-check
#   gen10.sh check <dir> | empty <dir>
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round10/agents/ref10
S=~/caselaw2/r10ref
mkdir -p $S/cur/tools/caselaw2 $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
export CASELAW2_REF=$S/cur/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
cmd=$1; dir=$2; shift 2
case "$cmd" in
  gen)
    seed=$1; rounds=$2; shift 2
    rm -rf $S/$dir; mkdir -p $S/$dir
    python3 -X utf8 $ME/make_r10.py gen --seed $seed --rounds $rounds --out $S/$dir "$@" 2>&1 | grep -v '^  ' | tail -40
    python3 -X utf8 $ME/make_r10.py check $S/$dir > $S/$dir.selfcheck.txt 2>&1
    cp $S/$dir.selfcheck.txt $ME/results/$dir.selfcheck.txt
    tail -n 25 $S/$dir.selfcheck.txt ;;
  check)
    python3 -X utf8 $ME/make_r10.py check $S/$dir > $S/$dir.selfcheck.txt 2>&1
    cp $S/$dir.selfcheck.txt $ME/results/$dir.selfcheck.txt
    tail -n 25 $S/$dir.selfcheck.txt ;;
  empty)
    mkdir -p $S/pre/tools/caselaw2
    rsync -a --delete --exclude __pycache__ $W/round10/pre/ref/ $S/pre/tools/caselaw2/ref/
    python3 -X utf8 $ME/make_r10.py empty $S/$dir --pre $S/pre/tools/caselaw2/ref/precedent_ref.py 2>&1 | tail -20 ;;
esac
