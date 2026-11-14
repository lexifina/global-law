"""scdb8: print the parts of a Supreme Court decision (labels, sizes) and the tail of each opinion-of-the-Court part.

    python -X utf8 tail8.py <node> [...] [--chars 700] [--head 0]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L, C = link.L, link.C
NL = chr(10)


def show(n, chars, head):
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
    print(n, L.node_row(n)[6][:100], "| len", len(text), "| hw", hw)
    for a, b, p, s in pm:
        print("  part", p, a, b, b - a)
    if head:
        print("  HEAD:", L.norm(view[body0:body0 + head]))
    for a, b, p, s in pm:
        if p in ("majority", "perCuriam", "plurality", "majority~", "combined", "unknown", "opinion"):
            print("  TAIL[%s]:" % p, L.norm(view[max(a, b - chars):b]))


def main():
    args = sys.argv[1:]
    chars, head = 700, 0
    if "--chars" in args:
        i = args.index("--chars")
        chars = int(args[i + 1])
        del args[i:i + 2]
    if "--head" in args:
        i = args.index("--head")
        head = int(args[i + 1])
        del args[i:i + 2]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for x in args:
        show(int(x), chars, head)


if __name__ == "__main__":
    main()
