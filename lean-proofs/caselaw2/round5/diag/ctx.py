"""diag reading aid: sentences of a cached decision text that match a pattern, with the part label.

    python ctx.py <node> -x <regex> [-c N] [-m MAX] [-a]     sentences matching the regex (+N sentences each side)
    python ctx.py <node> -k [-m MAX] [-a]                    sentences with an operative / overruling cue
    python ctx.py <node> -o <offset> [-w WIDTH]              raw text around an offset
    python ctx.py <node> -p                                  the part map

By default only parts that are not head matter / separate opinions are shown; -a shows all parts.
Text comes from round5/diag/text/<node>.md (written by prep.py).
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader"))
import common as RC  # noqa: E402

CUE = (r"overrul|overturn|repudiat|disapprov|disavow|discard|abandon|reject|no longer|not survive|cannot survive|"
       r"cannot stand|can not stand|overthrown|not to be followed|decline to follow|declined to follow|"
       r"depart(?:ed|s|ure)? from|erroneous|unsound|wrongly decided|not be regarded|inconsistent with|"
       r"must be regarded|must be considered|not controlling|not bound|no place|modif|qualif|limited to|doubted|"
       r"untenable|not tenable|recede|withdraw|we now hold|to the contrary|contrary to")
SPLIT = re.compile(r"(?<=[.?!”\"])\s+(?=[A-Z“\"(\[])")
MAJ = ("majority", "perCuriam", "majority~", "lead", "plurality", "combined", "unknown", "majority?")


def sentences(text, a, b):
    out = []
    i = a
    seg = text[a:b]
    pos = 0
    for m in SPLIT.finditer(seg):
        w = re.search(r"([A-Za-z]+)\.$", seg[max(0, m.start() - 12):m.start()])
        if w and (w.group(1) in RC.ABBR or w.group(1) in ("vs", "v", "U", "S", "Wall", "How", "Pet", "Wheat",
                                                           "Cranch", "Dall", "Mr", "Id", "id", "Ibid", "cf", "Cf")
                  or len(w.group(1)) == 1):
            continue
        out.append((a + pos, a + m.start()))
        pos = m.end()
    out.append((a + pos, b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("node")
    ap.add_argument("-x")
    ap.add_argument("-k", action="store_true")
    ap.add_argument("-o", type=int)
    ap.add_argument("-w", type=int, default=1200)
    ap.add_argument("-c", type=int, default=0)
    ap.add_argument("-m", type=int, default=25)
    ap.add_argument("-a", action="store_true")
    ap.add_argument("-p", action="store_true")
    ap.add_argument("-l", type=int, default=700, help="max chars per sentence")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(HERE, "text", a.node + ".md"), encoding="utf-8", newline="") as f:
        text = f.read()
    pm, body0 = RC.part_map2(text)
    if a.p:
        print("len", len(text))
        for s, e, p, sec in pm:
            print(s, e, p, sec[:70])
        return
    if a.o is not None:
        p, sec = RC.part_at(pm, a.o)
        print("[%s | %s]" % (p, sec[:50]))
        print(text[max(0, a.o - a.w // 2):a.o + a.w // 2])
        return
    rx = re.compile(a.x) if a.x else re.compile(CUE, re.I)
    shown = 0
    total = 0
    for s, e, p, sec in pm:
        if p in ("front", "title"):
            continue
        base = p.lower()
        is_maj = any(base.startswith(m.lower()) for m in MAJ) and not base.startswith(("dissent", "concur", "head"))
        if not a.a and not is_maj:
            n = len(rx.findall(text, s, e))
            if n:
                print("  (skipped part %s %d-%d: %d hits)" % (p, s, e, n))
            continue
        # paragraphs = lines
        off = s
        for line in text[s:e].split("\n"):
            la, lb = off, off + len(line)
            off = lb + 1
            if not rx.search(line):
                continue
            sents = sentences(text, la, lb)
            hit = [i for i, (x, y) in enumerate(sents) if rx.search(text[x:y])]
            keep = sorted({j for i in hit for j in range(max(0, i - a.c), min(len(sents), i + a.c + 1))})
            for j in keep:
                total += 1
                if shown >= a.m:
                    continue
                x, y = sents[j]
                t = text[x:y]
                if len(t) > a.l:
                    m = rx.search(t)
                    c = m.start() if m else 0
                    t = ("…" if c > a.l // 2 else "") + t[max(0, c - a.l // 2):c + a.l // 2] + "…"
                print("@%d [%s]%s %s" % (x, p, "*" if j in hit else " ", t))
                shown += 1
    print("-- %d shown of %d" % (shown, total))


if __name__ == "__main__":
    main()
