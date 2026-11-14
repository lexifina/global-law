"""b4sc: local copies of round 6's guard feature pass and new-row guard (rules unchanged; only paths differ).

    python -X utf8 mkguard.py      -> gfeat7.py, guard7.py in this folder (work files under work/guard/)
Then:
    python -X utf8 gfeat7.py --base <history_delta.tsv> --tag <t>_ --procs 22
    python -X utf8 guard7.py <t> <history_delta.tsv>      -> work/guard/<t>_flags.tsv, <t>_drop_ids.txt, <T>_GUARD.md
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GD = os.path.join(C2, "round6", "history", "rules", "guard")


def main():
    s = open(os.path.join(GD, "gfeat.py"), encoding="utf-8").read()
    a = 'R6 = os.path.dirname(os.path.dirname(HERE))'
    b = 'WORK = os.path.join(HERE, "work")'
    assert a in s and b in s
    s = s.replace(a, 'R6 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "round6", "history")')
    s = s.replace(b, 'WORK = os.path.join(HERE, "work", "guard")')
    s = "# b4sc copy of round6/history/rules/guard/gfeat.py (paths only)\n" + s
    open(os.path.join(HERE, "gfeat7.py"), "w", encoding="utf-8", newline="\n").write(s)
    v = open(os.path.join(GD, "vx_guard.py"), encoding="utf-8").read()
    a = 'sys.path.insert(0, HERE)'
    assert a in v
    v = v.replace(a, 'GD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "round6", "history", '
                     '"rules", "guard")\nsys.path.insert(0, os.path.dirname(os.path.dirname(GD)))\nsys.path.insert(0, GD)')
    v = v.replace('os.path.join(HERE, "work", TAG + "_features.jsonl.gz")',
                  'os.path.join(HERE, "work", "guard", TAG + "_features.jsonl.gz")')
    v = v.replace('os.path.join(HERE, TAG + "_flags.tsv")', 'os.path.join(HERE, "work", "guard", TAG + "_flags.tsv")')
    v = v.replace('os.path.join(HERE, TAG + "_drop_ids.txt")', 'os.path.join(HERE, "work", "guard", TAG + "_drop_ids.txt")')
    v = v.replace('os.path.join(HERE, TAG.upper() + "_GUARD.md")', 'os.path.join(HERE, "work", "guard", TAG.upper() + "_GUARD.md")')
    v = "# b4sc copy of round6/history/rules/guard/vx_guard.py (paths only)\n" + v
    open(os.path.join(HERE, "guard7.py"), "w", encoding="utf-8", newline="\n").write(v)
    os.makedirs(os.path.join(HERE, "work", "guard"), exist_ok=True)
    print("ok")


if __name__ == "__main__":
    main()
