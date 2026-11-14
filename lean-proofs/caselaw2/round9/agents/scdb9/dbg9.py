"""scdb9 debug: the opinion parts and the disposition sentences sc9 finds in one decision (diagnosis only).

    python -X utf8 dbg9.py <node> [<node> ...]
"""
import sys
import sc9

link, L, C, sc7 = sc9.link, sc9.L, sc9.C, sc9.sc7
NL = chr(10)


def main():
    sc7.init7()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ns = [int(x) for x in sys.argv[1:]]
    texts = L.fetch_texts(ns)
    for n in ns:
        text = texts[n][1]
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
        print(n, "hard_wrapped", hw, "len", len(text), len(view))
        for a, b, p, _s in pm:
            print("  part", p, a, b, "|", L.norm(view[a:a + 80]), "...", L.norm(view[max(a, b - 120):b]))
        op_parts = [(a, b, p.rstrip("~")) for a, b, p, _s in pm if p in ("majority", "perCuriam", "plurality", "majority~")]
        disps = link.find_dispositions(view, op_parts)
        for d in disps:
            print("  disp", d["form"], d["strong"], d["part"], d["q"], "|", L.norm(view[d["q"][0]:d["q"][1]])[:200])
        print("  read:", sc7.read_disposition7(view, op_parts, disps)[1:])


if __name__ == "__main__":
    main()
