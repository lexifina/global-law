"""infra10: wsl/r10_run.sh from wsl/r9_run.sh by exact replacements (r9_run.sh is only read).

    python -X utf8 round10/agents/infra10/mk_r10run.py
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
s = open(os.path.join(C2, "wsl", "r9_run.sh"), "rb").read().decode("utf-8")
assert "\r" not in s
head_end = s.index("export PATH=")
old_head = s[:head_end]
new_head = """#!/bin/bash
# round 10 (agent infra10; = wsl/r9_run.sh on round-10 paths, base v9c): run the Lean runner (and optionally the
# Python reference + diff) on a staged variant.
#   usage: r10_run.sh <name> [ref]    <name> = folder under round10/stage/ on Windows (built by round10/stage10.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r10_run.sh <name> [ref]'
#   NOBUILD=1 r10_run.sh <name>        no sync, no build: runs the FROZEN round-9 checker
#                                      ~/caselaw2/r10_bin/caselaw2_r9v9c (a copy of ~/caselaw2/r9_bin/run_v9c, the
#                                      binary of the round-9 frozen run v9c (round9/out/v9c/RUN.txt, round9/FREEZE.md),
#                                      sha1 22bab5cdc71237876c807a8c9354cad7a47c6e1f; checked before each run), so a
#                                      build by `lean10` cannot change it mid-round. Allowed without LEAN_READY.
#   R10BIN=<path> NOBUILD=1 r10_run.sh selects another binary (copied aside to ~/caselaw2/r10_bin/run_<name> first).
#   (no NOBUILD)                       refuses unless round10/LEAN_READY exists; syncs the code (wsl/sync.sh code),
#                                      builds LegalProofs.CaseLaw2.Run and the runner under ~/caselaw2/r6_build.lock,
#                                      copies the new runner to ~/caselaw2/r10_bin/caselaw2_<name> and runs that copy.
#   ref                                also runs the Python reference (tools/caselaw2/ref/precedent_ref.py of the
#                                      synced tree) on the same data dir and diffs it (as r9_run.sh), in
#                                      difftest/r10_<name>/ (ref/, ref.log, diff.txt, diff.tsv); diff.txt is copied
#                                      to round10/out/<name>/.
# Disk: prints `df -h /mnt/c` first and refuses (exit 5) when C: has under 8 GB free (WSL's disk lives on C:).
# Machine-wide limit: at most TWO round-10 runs at once (flock slots ~/caselaw2/r10_slot1.lock, r10_slot2.lock; a
# third run prints that it waits and polls every 10 s until a slot is free). One run per variant name at a time
# (~/caselaw2/r10_name_<name>.lock; a second run of the same name is refused, exit 4): data_r10_<name> and
# difftest/r10_<name> belong to that name only (round 9 had a collision of two runs of one name).
# Base mirror: base_r10_v9c/ in the mirror = round9/stage/v9c, built once from the round-9 mirror data_r9_v9c (a hard
# link to the real file behind each of its regular files and symlinks: no table is copied, and the mirror does not
# depend on earlier data dirs staying) and checked file by file with cmp against Windows round9/stage/v9c (marker
# .verified, with the sha1 of every table in .sha1). The variant's data dir is data_r10_<name>: symlinks to
# base_r10_v9c, and every table listed in round10/stage/<name>/TABLES.txt (stage10.py: the ten staged tables +
# EXTRA_TABLES history_bridge, part_zone, history_remand + adoption, succession) put over it: a table whose sha1
# equals the base mirror's is a symlink to the mirror, any other is copied from Windows; an EMPTY history_anchor /
# history_claim / joined or extra table (e.g. history_remand) is left out (the runner reads that as "no lines":
# earlier-round mode). Lean output goes to Windows round10/out/<name>/ (+ RUN.txt). Same runner call as
# wsl/r9_run.sh (asOf 20261112, 8 shards).
"""
s = new_head + s[head_end:]
REPS = [
    ("""FROZEN=~/caselaw2/r9_bin/caselaw2_r8v8e
FROZEN_SRC=~/caselaw2/r8_bin/caselaw2_lean8
FROZEN_SHA=3b8d3e4d45fb60a84c5cfb00c2f6729ebc2bfa6b
N=$1; REF=$2
S=$W/round9/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
B=$M/base_r9_v8e
WB=$W/round8/stage/v8e
""", """FROZEN=~/caselaw2/r10_bin/caselaw2_r9v9c
FROZEN_SRC=~/caselaw2/r9_bin/run_v9c
FROZEN_SHA=22bab5cdc71237876c807a8c9354cad7a47c6e1f
N=$1; REF=$2
S=$W/round10/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
B=$M/base_r10_v9c
WB=$W/round9/stage/v9c
# ---- disk (C: also holds the WSL disk): refuse under 8 GB free
df -h /mnt/c
AVAIL_KB=$(df -Pk /mnt/c | awk 'NR==2{print $4}')
[ -n "$AVAIL_KB" ] && [ "$AVAIL_KB" -ge $((8*1024*1024)) ] || { echo "refused: C: has under 8 GB free ($((${AVAIL_KB:-0}/1024/1024)) GB); nothing run; tell the lead"; exit 5; }
# ---- one run per variant name (its data dir and difftest dir are its own)
exec 6> ~/caselaw2/r10_name_$N.lock
flock -n 6 || { echo "refused: a run of $N is already active (data_r10_$N / difftest/r10_$N are in use)"; exit 4; }
"""),
    ("""    exec 7> ~/caselaw2/r9_slot$s.lock""", """    exec 7> ~/caselaw2/r10_slot$s.lock"""),
    ("""echo "two round-9 runs are active""", """echo "two round-10 runs are active"""),
    ("""exec 8> ~/caselaw2/r9_base.lock
flock 8
if [ ! -f $B/.verified ]; then
  [ -d $M/data_r8_v8e ] || { echo "no $M/data_r8_v8e to build the base mirror from"; exit 2; }
  echo "building the base mirror $B"
  rm -rf $B.tmp; mkdir -p $B.tmp
  for f in $WB/*.tsv; do
    b=$(basename $f); m=$M/data_r8_v8e/$b
    if [ -e $m ] && cmp -s $m $f; then
      if [ -L $m ]; then ln -s "$(realpath $m)" $B.tmp/$b; else ln $m $B.tmp/$b 2>/dev/null || cp $m $B.tmp/$b; fi
    else
      echo "  $b: not in data_r8_v8e or different; copied from Windows"; cp $f $B.tmp/$b
    fi
  done""", """exec 8> ~/caselaw2/r10_base.lock
flock 8
if [ ! -f $B/.verified ]; then
  [ -d $M/data_r9_v9c ] || { echo "no $M/data_r9_v9c to build the base mirror from"; exit 2; }
  echo "building the base mirror $B from data_r9_v9c (hard links)"
  rm -rf $B.tmp; mkdir -p $B.tmp
  for f in $WB/*.tsv; do
    b=$(basename $f); m=$M/data_r9_v9c/$b
    if [ -e $m ] && cmp -s $m $f; then
      ln "$(realpath $m)" $B.tmp/$b 2>/dev/null || ln -s "$(realpath $m)" $B.tmp/$b
    else
      echo "  $b: not in data_r9_v9c or different; copied from Windows"; cp $f $B.tmp/$b
    fi
  done"""),
    ("""mkdir -p ~/caselaw2/r9_bin
if [ "$NOBUILD" = 1 ]; then
  if [ -n "$R9BIN" ]; then
    [ -x "$R9BIN" ] || { echo "no runner binary at $R9BIN"; exit 2; }
    EXE=~/caselaw2/r9_bin/run_$N
    cp "$R9BIN" $EXE
    HOW="NOBUILD R9BIN=$R9BIN\"""", """mkdir -p ~/caselaw2/r10_bin
if [ "$NOBUILD" = 1 ]; then
  if [ -n "$R10BIN" ]; then
    [ -x "$R10BIN" ] || { echo "no runner binary at $R10BIN"; exit 2; }
    EXE=~/caselaw2/r10_bin/run_$N
    cp "$R10BIN" $EXE
    HOW="NOBUILD R10BIN=$R10BIN\""""),
    ('''    HOW="NOBUILD frozen r8v8e"''', '''    HOW="NOBUILD frozen r9v9c"'''),
    ("""  [ -f $W/round9/LEAN_READY ] || { echo "round9/LEAN_READY is missing: the Lean tree is being edited; nothing synced, built or run (NOBUILD=1 runs the frozen round-8 binary)"; exit 3; }""",
     """  [ -f $W/round10/LEAN_READY ] || { echo "round10/LEAN_READY is missing: the Lean tree is being edited; nothing synced, built or run (NOBUILD=1 runs the frozen round-9 binary)"; exit 3; }"""),
    ("""~/caselaw2/r9_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r9_build.log""",
     """~/caselaw2/r10_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r10_build.log"""),
    ("""~/caselaw2/r9_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r9_build_runner.log""",
     """~/caselaw2/r10_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r10_build_runner.log"""),
    ("""  EXE=~/caselaw2/r9_bin/caselaw2_$N""", """  EXE=~/caselaw2/r10_bin/caselaw2_$N"""),
    ("""D=data_r9_$N""", """D=data_r10_$N"""),
    ("""R=difftest/r9_$N""", """R=difftest/r10_$N"""),
    ("""bridge\\|zone' $R/lean/summary.tsv""", """bridge\\|zone\\|remand' $R/lean/summary.tsv"""),
    ("""echo "history verdicts, round-9 rows (h9:):"
awk -F'\\t' '$1=="history" && $2 ~ /^h9:/""", """echo "history verdicts, round-10 rows (h10:):"
awk -F'\\t' '$1=="history" && $2 ~ /^h10:/"""),
    ("""echo "treatment verdicts, round-9 rows (t9:):"
awk -F'\\t' '$1=="treatment" && $2 ~ /^t9:/""", """echo "treatment verdicts, round-10 rows (t10:):"
awk -F'\\t' '$1=="treatment" && $2 ~ /^t10:/"""),
    ("$W/round9/out/$N", "$W/round10/out/$N", 8),
    ("""  echo "stage round9/stage/$N;""", """  echo "stage round10/stage/$N;"""),
]
for r in REPS:
    a, b = r[0], r[1]
    n = r[2] if len(r) > 2 else 1
    assert s.count(a) == n, (a[:80], s.count(a), n)
    s = s.replace(a, b)
left = [ln for ln in s.splitlines() if ("r9" in ln or "R9" in ln or "round9" in ln or "v8e" in ln)
        and "round9/stage/v9c" not in ln and "data_r9_v9c" not in ln and "r9_bin/run_v9c" not in ln
        and "r9_run.sh" not in ln and "round9/out/v9c" not in ln and "r9v9c" not in ln]
assert not left, left
open(os.path.join(C2, "wsl", "r10_run.sh"), "wb").write(s.encode("utf-8"))
print("written wsl/r10_run.sh (old header %d lines)" % old_head.count("\n"))
