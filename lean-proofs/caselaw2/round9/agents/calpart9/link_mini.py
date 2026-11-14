"""calpart9: run the round-6 linker `below_other` (round6/history/rules/below_other/link.py, unchanged, imported) on
the mini cache of r6mini.py (decisions whose part map rule PJ fixes). One process (the module globals are pointed at
this folder; spawned workers would not see that).

    python -X utf8 link_mini.py

Out: work/r6mini/below_other/rows.jsonl (+ work/*.rows.jsonl, link_counts.json). No answer-key file is read.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_other"))
import r6lib as L  # noqa: E402
import link as LK  # noqa: E402

OUT = os.path.join(HERE, "work", "r6mini", "below_other")
L.CACHE = os.path.join(HERE, "work", "r6mini", "cache")
LK.HERE = OUT
LK.WORK = os.path.join(OUT, "work")

if __name__ == "__main__":
    os.makedirs(LK.WORK, exist_ok=True)
    sys.argv = [sys.argv[0], "--procs", "1"]
    LK.main()
