"""infra12: hand edits of the generated wsl/r12_run.sh (base v11d mirror, frozen round-11 binary s51, slots that
respect round-11 runs, decisions2 for --nodes stages = corpus rows of the mirror + decisions2_nodes.tsv)."""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "wsl", "r12_run.sh")
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


i = s.index("export PATH=")
s = r'''#!/bin/bash
# round 12 (agent infra12; = wsl/r11_run.sh on round-12 paths, base v11d, frozen round-11 binary s51): run the Lean
# runner (and optionally the Python reference + diff) on a staged variant.
#   usage: r12_run.sh <name> [ref]    <name> = folder under round12/stage/ on Windows (built by round12/stage12.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r12_run.sh <name> [ref]'
#   NOBUILD=1 r12_run.sh <name>        no sync, no build: runs the FROZEN round-11 checker
#                                      ~/caselaw2/r12_bin/caselaw2_r11v11d (a hard link to, or copy of,
#                                      ~/caselaw2/r11_bin/caselaw2_lean11_s51, the binary of the round-11 frozen run v11d
#                                      (round11/out/v11d/RUN.txt), sha1 a1cc4296022b1bd07401cc64b04e50449d0de9b3;
#                                      checked before each run). Allowed without LEAN_READY.
#   R12BIN=<path> NOBUILD=1 r12_run.sh selects another binary (copied aside to ~/caselaw2/r12_bin/run_<name> first).
#   (no NOBUILD)                       refuses unless round12/LEAN_READY exists; syncs the code (wsl/sync.sh code),
#                                      builds LegalProofs.CaseLaw2.Run and the runner under ~/caselaw2/r6_build.lock,
#                                      copies the new runner to ~/caselaw2/r12_bin/caselaw2_<name> and runs that copy.
#   ref                                also runs the Python reference (tools/caselaw2/ref/precedent_ref.py of the
#                                      synced tree) on the same data dir and diffs it, in difftest/r12_<name>/
#                                      (ref/, ref.log, diff.txt, diff.tsv); diff.txt is copied to round12/out/<name>/.
# Disk: prints `df -h /mnt/c` first and refuses (exit 5) when C: has under 8 GB free (WSL's disk lives on C:).
# Machine-wide limit: at most TWO runs at once, round-11 and round-12 together (flock slots ~/caselaw2/r12_slot1.lock,
# r12_slot2.lock; a held ~/caselaw2/r11_slot*.lock counts against the two; a run that finds no room prints that it
# waits and polls every 10 s). One run per variant name at a time (~/caselaw2/r12_name_<name>.lock; a second run of
# the same name is refused, exit 4).
# Base mirror: base_r12_v11d/ in the mirror = round11/stage/v11d (its *.tsv), built once from the round-11 data dir
# data_r11_v11d (a hard link to the real file behind each of its regular files and symlinks: no table is copied; the
# few v11d files that data dir lacks, decisions2_nodes.tsv and nodes_map.tsv, are copied from Windows) and checked
# file by file with cmp against Windows round11/stage/v11d (marker .verified, sha1 of every table in .sha1). The
# variant's data dir is data_r12_<name>: symlinks to base_r12_v11d (except decisions2_nodes.tsv / nodes_map.tsv,
# which are not runner tables), and every table listed in round12/stage/<name>/TABLES.txt put over it: a table whose
# sha1 equals the base mirror's is a symlink to the mirror, any other is copied from Windows; an EMPTY
# history_anchor / history_claim / joined or extra table is left out (earlier-round mode). Lean output goes to
# Windows round12/out/<name>/ (+ RUN.txt). Same runner call as wsl/r11_run.sh (asOf 20261112, 8 shards).
# Node count: round12/stage/<name>/nodes.count (stage12 always writes or links it; v11d's is 6,893,499), else
# ../graph/nodes.count. A stage built with --nodes DIR lists decisions2 in TABLES.txt (how = nodes) and has
# decisions2_nodes.tsv: the data dir's decisions2.tsv is then the first (nodes.count - rows of decisions2_nodes.tsv)
# lines of the mirror's decisions2 (= the corpus rows) + decisions2_nodes.tsv, sha1-checked against TABLES.txt
# (about 0.9 GB in WSL until r12_clean.sh). Without --nodes decisions2 is the mirror's (v11d's, with its 1,045 nodes).
''' + s[i:]

rep("FROZEN=~/caselaw2/r12_bin/caselaw2_r10v10d\nFROZEN_SRC=~/caselaw2/r10_bin/run_v10d\n"
    "FROZEN_SHA=e7e32592cc6c6393506e25dc9654d4254af218ea",
    "FROZEN=~/caselaw2/r12_bin/caselaw2_r11v11d\nFROZEN_SRC=~/caselaw2/r11_bin/caselaw2_lean11_s51\n"
    "FROZEN_SHA=a1cc4296022b1bd07401cc64b04e50449d0de9b3")
rep("B=$M/base_r12_v10d\n", "B=$M/base_r12_v11d\n")
rep(r'''SLOT=; waited=
while :; do
  for s in 1 2; do
    exec 7> ~/caselaw2/r12_slot$s.lock
    if flock -n 7; then SLOT=$s; break 2; fi
  done
  exec 7>&-
  [ -z "$waited" ] && { echo "two round-12 runs are active: $N waits for a run slot ($(date '+%T'))"; waited=1; }
  sleep 10
done''', r'''# round 12: a held round-11 slot counts against the two (r11_run.sh runs may still be active)
held () { [ -e "$1" ] && ! flock -n "$1" true 2>/dev/null; }
SLOT=; waited=
while :; do
  for s in 1 2; do
    exec 7> ~/caselaw2/r12_slot$s.lock
    if flock -n 7; then
      busy=0
      for o in ~/caselaw2/r11_slot1.lock ~/caselaw2/r11_slot2.lock ~/caselaw2/r12_slot$((3-s)).lock; do
        held $o && busy=$((busy+1))
      done
      if [ $busy -le 1 ]; then SLOT=$s; break 2; fi
      exec 7>&-
    fi
  done
  exec 7>&-
  [ -z "$waited" ] && { echo "two runs (round 11 / round 12) are active: $N waits for a run slot ($(date '+%T'))"; waited=1; }
  sleep 10
done''')
rep('''  [ -d $M/data_r10_v10d ] || { echo "no $M/data_r10_v10d to build the base mirror from"; exit 2; }
  echo "building the base mirror $B from data_r10_v10d (hard links)"''',
    '''  [ -d $M/data_r11_v11d ] || { echo "no $M/data_r11_v11d to build the base mirror from"; exit 2; }
  echo "building the base mirror $B from data_r11_v11d (hard links)"''')
rep("    b=$(basename $f); m=$M/data_r10_v10d/$b", "    b=$(basename $f); m=$M/data_r11_v11d/$b")
rep('      echo "  $b: not in data_r10_v10d or different; copied from Windows"; cp $f $B.tmp/$b',
    '      echo "  $b: not in data_r11_v11d or different; copied from Windows"; cp $f $B.tmp/$b')
rep('''    if [ ! -x $EXE ] && [ -x $FROZEN_SRC ] && [ "$(sha1sum < $FROZEN_SRC | cut -c1-40)" = $FROZEN_SHA ]; then
      cp $FROZEN_SRC $EXE.tmp && mv $EXE.tmp $EXE
    fi''', '''    if [ ! -x $EXE ] && [ -x $FROZEN_SRC ] && [ "$(sha1sum < $FROZEN_SRC | cut -c1-40)" = $FROZEN_SHA ]; then
      ln $FROZEN_SRC $EXE 2>/dev/null || { cp $FROZEN_SRC $EXE.tmp && mv $EXE.tmp $EXE; }
    fi''')
rep('    HOW="NOBUILD frozen r10v10d"', '    HOW="NOBUILD frozen r11v11d"')
rep("(NOBUILD=1 runs the frozen round-10 binary)", "(NOBUILD=1 runs the frozen round-11 binary)")
rep('''for f in $B/*.tsv; do ln -s "$(realpath $f)" $D/$(basename $f); done''',
    '''for f in $B/*.tsv; do
  case $(basename $f) in decisions2_nodes.tsv|nodes_map.tsv) continue ;; esac  # stage files, not runner tables
  ln -s "$(realpath $f)" $D/$(basename $f)
done''')
rep('''    cat $B/decisions2.tsv $S/decisions2_nodes.tsv > $D/decisions2.tsv''',
    '''    # round 12: the mirror's decisions2 is v11d's (corpus + its 1,045 nodes): take its corpus rows only
    NC=$(tr -d ' \\r\\n' < $S/nodes.count); NN=$(wc -l < $S/decisions2_nodes.tsv | tr -d ' ')
    [[ "$NC" =~ ^[0-9]+$ ]] && [ "$NC" -gt "$NN" ] || { echo "bad nodes.count / decisions2_nodes.tsv in $S"; exit 2; }
    { head -n $((NC - NN)) $B/decisions2.tsv; cat $S/decisions2_nodes.tsv; } > $D/decisions2.tsv''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", p)
