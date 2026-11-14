"""scdb8: for Supreme Court decisions with no disposition found by round 6/7 (reason no_disposition / disp_not_strong),
print or count the last lines of the opinion of the Court (diagnosis only; no key).

    python -X utf8 nodisp_scan.py sample <n> [--seed s] [--reason no_disposition]
"""
import gzip, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L, C = link.L, link.C
NL = chr(10)
WORK = os.path.join(HERE, "work")


def op_tail(text, chars):
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    ops = [(a, b, p) for a, b, p, _s in pm if p in ("majority", "perCuriam", "plurality", "majority~")]
    if not ops:
        return None
    a, b, p = ops[-1]
    return L.norm(view[max(a, b - chars):b])


def main():
    args = sys.argv[1:]
    seed = 8
    reason = "no_disposition"
    if "--seed" in args:
        i = args.index("--seed"); seed = int(args[i + 1]); del args[i:i + 2]
    if "--reason" in args:
        i = args.index("--reason"); reason = args[i + 1]; del args[i:i + 2]
    k = int(args[1])
    idx = json.load(open(os.path.join(WORK, "diag7_index.json"), encoding="utf-8"))
    pool = sorted(int(x) for x, d in idx.items() if d.get("reason") == reason and d["len"] > 4000)
    random.seed(seed)
    pick = random.sample(pool, k)
    texts = L.fetch_texts(pick)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for n in pick:
        t = op_tail(texts[n][1], 260)
        print(n, idx[str(n)]["date"], "|", t)


if __name__ == "__main__":
    main()
