#!/bin/bash
# round 11 (anchorTribunal DESIGN11 §5.1; later sections by INBOX): a compiled Lean runner binary against the
# Python reference. Run INSIDE WSL Ubuntu:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round11/agents/ref11/difftest11.sh <cmd> ...'
#   BIN=<binary> (default ~/caselaw2/r11_bin/caselaw2_lean11; copied to ~/caselaw2/r11ref/bin/ and its sha1 logged)
#   kept <tag>                       the kept universes round11/agents/ref11/universes/*
#   sweep <tag> <seed> <rounds> [--probe|--fuzz K]   fresh make_r11 universes + self-check + the run
#   regress <tag>                    the 552 earlier universes (r8ref 534 + round-9 kept 9 + round-10 kept 9), no anchorTribunal claim
#   dirs <tag> <root>                any universe root
# Summaries: round11/agents/ref11/results/<tag>.txt (+ .report.txt); disagreeing universes: fail/<tag>/.
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round11/agents/ref11
S=~/caselaw2/r11ref
R8=~/caselaw2/r8ref
mkdir -p $S/cur/tools/caselaw2 $S/bin $S/out $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
export CASELAW2_REF=$S/cur/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
SRC=${BIN:-$HOME/caselaw2/r11_bin/caselaw2_lean11}
[ -x "$SRC" ] || { echo "no binary $SRC"; exit 3; }
cp -p "$SRC" $S/bin/runner
EXE=$S/bin/runner
cmd=$1; shift
df -h /mnt/c | tail -1

run_dirs () {   # tag root...
  local tag=$1; shift
  local roots=""; for r in "$@"; do roots="$roots --root $r"; done
  # NO52=1: a binary without DESIGN11 §5.2 (the §5.1 LEAN_READY): the copies lose history_identity.tsv first
  if [ "$NO52" = 1 ]; then for r in "$@"; do find $r -name history_identity.tsv -delete; done; fi
  { echo "NO52=${NO52:-0}"; echo "binary $SRC sha1 $(sha1sum < $EXE | cut -c1-40); ref $(sha1sum < $CASELAW2_REF/precedent_ref.py | cut -c1-40); cue_table $(sha1sum < $S/cur/tools/caselaw2/cues/cue_table.json | cut -c1-40); $(date '+%F %T')"; } > $S/out/$tag.txt
  python3 -X utf8 $W/round10/agents/ref10/bin_drt10.py --bin $EXE $roots --out $S/out/$tag --jobs ${JOBS:-8} >> $S/out/$tag.txt 2>&1
  echo "rc=$?" >> $S/out/$tag.txt
  python3 -X utf8 $ME/make_r11.py report "$@" > $S/out/$tag.report.txt 2>&1
  cp $S/out/$tag.txt $ME/results/$tag.txt; cp $S/out/$tag.report.txt $ME/results/$tag.report.txt
  for r in "$@"; do for d in $r/*/; do
    if [ -s $d/diff.tsv ] || [ ! -f $d/lean/certs.tsv ]; then
      mkdir -p $ME/fail/$tag; rsync -a --exclude 'ref_check' $d $ME/fail/$tag/$(basename $d)/
    fi
  done; done
  tail -n 40 $S/out/$tag.txt
  echo "--- by case"; head -60 $S/out/$tag.report.txt
}

case "$cmd" in
  kept)
    tag=$1
    rm -rf $S/kept_run; mkdir -p $S/kept_run
    rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $ME/universes/ $S/kept_run/
    run_dirs $tag $S/kept_run ;;
  sweep)
    tag=$1; seed=$2; rounds=$3; shift 3
    rm -rf $S/sweep/$tag; mkdir -p $S/sweep/$tag
    python3 -X utf8 $ME/make_r11.py gen --seed $seed --rounds $rounds --out $S/sweep/$tag "$@" | grep -v '^  ' | tail -3
    python3 -X utf8 $ME/make_r11.py check $S/sweep/$tag > $S/out/$tag.selfcheck.txt 2>&1
    grep -v '^  ' $S/out/$tag.selfcheck.txt | tail -6
    cp $S/out/$tag.selfcheck.txt $ME/results/$tag.selfcheck.txt
    run_dirs $tag $S/sweep/$tag ;;
  regress)
    tag=$1
    rm -rf $S/regress; mkdir -p $S/regress
    for src in regress/regress_regress regress/regress_fixed regress/regress_sweep_r6sw2 regress/regress_sweep_r6sw2p \
               regress/regress_sweep_r6sw2f regress/kept regress/sweep_r7sw3 regress/sweep_r7sw3p regress/sweep_r7sw3n \
               regress/sweep_r7sw3f kept sweep/r8sw1 sweep/r8sw1p sweep/r8sw1f; do
      n=$(echo $src | tr / _); mkdir -p $S/regress/$n
      rsync -a --exclude out --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $R8/$src/ $S/regress/$n/
    done
    mkdir -p $S/regress/r9kept
    rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $W/round9/agents/ref9/universes/ $S/regress/r9kept/
    mkdir -p $S/regress/r10kept
    rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $W/round10/agents/ref10/universes/ $S/regress/r10kept/
    run_dirs $tag $S/regress/* ;;
  dirs)
    tag=$1; root=$2
    rm -rf $S/dirs/$tag; mkdir -p $S/dirs/$tag
    rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $root/ $S/dirs/$tag/
    run_dirs $tag $S/dirs/$tag ;;
  *) echo "usage: difftest11.sh kept <tag> | sweep <tag> <seed> <rounds> [--probe|--fuzz K] | regress <tag> | dirs <tag> <root>" >&2; exit 2 ;;
esac
