"""scdb8: every citation of a Supreme Court decision's head matter + opinion of the Court, with what it resolves to.

    python -X utf8 cites8.py <node> [...]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L, C, G = link.L, link.C, link.G
NL = chr(10)


def show(n):
    link.init()
    F = G["F"]
    sha, text = L.fetch_texts([n])[n]
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    print("=" * 100)
    print(n, F.date[n], L.node_row(n)[6][:100], "| parts:", [(p, b - a) for a, b, p, s in pm])
    rx = link.r6cite.WIDE_RX if link.r6cite else C.CITE_RX
    for a, b, p, s in pm:
        if p not in ("headmatter", "headmatter~", "title", "majority", "perCuriam", "plurality", "majority~"):
            continue
        for m in rx.finditer(view, a, b):
            j, ikey, rkey, form = link.resolve(m)
            ctx = L.norm(view[max(a, m.start() - 110):m.end() + 25])
            if j is None:
                print("  [%s] UNRES key=%s known=%s | %s" % (p, rkey, form, ctx))
                continue
            jc = int(F.court[j])
            if jc == L.SCOTUS2:
                continue
            multi = ikey in G["multi"]
            print("  [%s] %s -> %d %d %s | %s%s | %s" % (p, ikey, j, F.date[j], F.court_name(jc)[:40],
                                                    L.node_row(j)[6][:50], " MULTI" if multi else "", ctx))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for x in sys.argv[1:]:
        show(int(x))


if __name__ == "__main__":
    main()
