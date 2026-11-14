"""calpart9: run the round-6 linker `rehear` (round6/history/rules/rehear/link.py + rehear_rules + rehear_link, unchanged,
imported) on the mini cache of r6mini.py, with the reader part map replaced by the PJ-fixed one (rehear_rules reads
the part map itself). One process (module globals are pointed at this folder).

    python -X utf8 rehear_mini.py

Out: work/r6mini/rehear/rows.jsonl (+ work/). No answer-key file is read.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RH = os.path.join(C2, "round6", "history", "rules", "rehear")
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, RH)
sys.path.insert(0, HERE)
import r6lib as L  # noqa: E402
import partfix as PF  # noqa: E402

C = L.reader_common()
ORIG = {"pm1": C.part_map, "pm2": C.part_map2}


def fixed1(text):
    pm, b0 = ORIG["pm1"](text)
    return PF.fix_parts(text, pm)[0], b0


def fixed2(text):
    pm, b0 = ORIG["pm2"](text)
    return PF.fix_parts(text, pm)[0], b0


C.part_map = fixed1
C.part_map2 = fixed2
import link as LK  # noqa: E402
import rehear_link as K  # noqa: E402

OUT = os.path.join(HERE, "work", "r6mini", "rehear")
L.CACHE = os.path.join(HERE, "work", "r6mini", "cache")
LK.WORK = os.path.join(OUT, "work")
K.WORK = LK.WORK
K.HERE = OUT

if __name__ == "__main__":
    os.makedirs(LK.WORK, exist_ok=True)
    src = os.path.join(RH, "work", "enbanc_nodes.txt")
    if os.path.exists(src) and not os.path.exists(os.path.join(LK.WORK, "enbanc_nodes.txt")):
        shutil.copy(src, LK.WORK)
    sys.argv = [sys.argv[0], "all", "--procs", "1"]
    LK.main()
