"""syl10: print the zone-refused rows (v9c verdict partZone) with their quote, the text owner's zones (v9c
part_zone.tsv) and the opinion-zone text, for diagnosis. No answer-key file is read.

    python -X utf8 show.py work/pz_ids.txt > work/show.txt
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL, TAB = "\n", "\t"
STAGE = os.path.join(C2, "round9", "stage", "v9c")


def load_rows(ids):
    out = {}
    for tab in ("history", "treatments"):
        for ln in open(os.path.join(STAGE, tab + ".tsv"), encoding="utf-8"):
            p = ln.rstrip(NL).split(TAB)
            if p[0] in ids:
                out[p[0]] = (tab, p)
    return out


def load_zones(nodes):
    zs = {}
    for ln in open(os.path.join(STAGE, "part_zone.tsv"), encoding="utf-8"):
        p = ln.rstrip(NL).split(TAB)
        n = int(p[0])
        if n in nodes:
            zs.setdefault(n, []).append((int(p[1]), int(p[2]), p[3]))
    return zs


def row_span(tab, p):
    """(by, target, kind, start, end, quote, ev, part)"""
    if tab == "history":
        return int(p[2]), int(p[1]), p[4], int(p[7]), int(p[8]), p[9], p[10], p[11]
    return int(p[1]), int(p[2]), p[4], int(p[9]), int(p[10]), p[11], p[12], p[13]


def main():
    ids = set(x.strip() for x in open(sys.argv[1], encoding="utf-8") if x.strip())
    rows = load_rows(ids)
    nodes = set(row_span(*v)[0] for v in rows.values())
    texts = L.fetch_texts(nodes)
    zs = load_zones(nodes)
    for i in sorted(rows, key=lambda x: (rows[x][0], x)):
        tab, p = rows[i]
        by, tg, kind, s, e, q, ev, part = row_span(tab, p)
        t = texts[by][1]
        print("=" * 100)
        print(i, tab, "by", by, "target", tg, kind, "ev", ev, "part", part, "span", s, e, "len", len(t))
        print("ZONES", [(a, b, z) for a, b, z in sorted(zs.get(by, []))])
        print("QUOTE:", L.norm(t[s:e])[:700])
        for a, b, z in sorted(zs.get(by, [])):
            if z in ("majority", "perCuriam", "plurality"):
                seg = t[a:b]
                print("  --[%s %d-%d]--" % (z, a, b))
                print("  " + (seg if len(seg) < 1800 else seg[:900] + "\n  [...]\n  " + seg[-700:]).replace(NL, NL + "  "))


if __name__ == "__main__":
    main()
