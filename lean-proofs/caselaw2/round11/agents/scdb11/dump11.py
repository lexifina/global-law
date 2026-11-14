"""scdb11: dump the pairs (SC node, earlier decision T, later decision T') of the same-court other-target misses: the
SC text around each citation of T and T', and the opening of T' (diagnosis only).

    python -X utf8 dump11.py  -> work/pairs_dump.txt
"""
import csv, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")


def cites(n):
    r = L.node_row(n)
    return [c for c in r[5].split("|") if c and "LEXIS" not in c and "SCDB" not in c]


def occ(text, c):
    vol, rest = c.split(" ", 1)
    rep, page = rest.rsplit(" ", 1)
    pat = re.escape(vol) + r"\s+" + r"\s*".join(re.escape(x) for x in rep.replace(" ", "")) + r"\s+" + re.escape(page)
    return [m.start() for m in re.finditer(pat, text)]


def main():
    rows = [x for x in csv.DictReader(open(os.path.join(WORK, "othertgt_v10d.tsv"), encoding="utf-8"), delimiter="\t")
            if x["rel"].startswith("same_court")]
    nodes = set()
    for x in rows:
        nodes |= {int(x["sc"]), int(x["below"]), int(x["target"])}
    tx = L.fetch_texts(nodes)
    out = []
    for x in rows:
        n, b, t = int(x["sc"]), int(x["below"]), int(x["target"])
        st = tx.get(n, ("", ""))[1]
        out.append("=" * 100)
        out.append("%s sc=%s %s | T=%s %s %s | T'=%s %s %s" % (x["caseId"], n, L.node_row(n)[6], b, x["b_date"],
                   "|".join(cites(b)), t, x["t_date"], "|".join(cites(t))))
        for lab, m in (("T", b), ("T'", t)):
            for c in cites(m):
                for o in occ(st, c)[:3]:
                    out.append("  [%s %s @%d] ...%s..." % (lab, c, o, L.norm(st[max(0, o - 350):o + 150])))
        tt = tx.get(t, ("", ""))[1]
        out.append("  T' opening: " + L.norm(tt[:900]))
        bt = tx.get(b, ("", ""))[1]
        out.append("  T len %d; T' len %d" % (len(bt), len(tt)))
    with open(os.path.join(WORK, "pairs_dump.txt"), "w", encoding="utf-8", newline=NL) as f:
        f.write(NL.join(out) + NL)


if __name__ == "__main__":
    main()
