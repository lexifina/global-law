"""scdb8: for anatomy rows of given stages, print the contexts in which the SC opinion cites the decision below
(diagnosis; the below node comes from the h0 cases file).

    python -X utf8 ctx8.py <stage prefix> [--n 15] [--seed 1] [--w 260] [--diag PATH] [--anat work/anatomy.tsv]
"""
import csv, gzip, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L, C = link.L, link.C
NL = chr(10)


def opt(args, k, d, f=str):
    if k in args:
        i = args.index(k)
        v = f(args[i + 1])
        del args[i:i + 2]
        return v
    return d


def main():
    args = sys.argv[1:]
    n = opt(args, "--n", 15, int)
    seed = opt(args, "--seed", 1, int)
    w = opt(args, "--w", 260, int)
    dpath = opt(args, "--diag", os.path.join(HERE, "work", "diag8.jsonl.gz"))
    anat = opt(args, "--anat", os.path.join(HERE, "work", "anatomy.tsv"))
    pre = args[0]
    rows = [x for x in csv.DictReader(open(anat, encoding="utf-8"), delimiter="\t") if x["stage"].startswith(pre)]
    random.seed(seed)
    pick = random.sample(rows, min(n, len(rows)))
    want = {int(x["sc"]): int(x["below"]) for x in pick}
    diag = {}
    with gzip.open(dpath, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["n"] in want:
                diag[d["n"]] = d
    texts = L.fetch_texts(list(want))
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for x in pick:
        s, b = int(x["sc"]), int(x["below"])
        d = diag.get(s, {})
        text = texts[s][1]
        body0 = 0
        if text.startswith("---"):
            e = text.find(NL + "---", 3)
            if e >= 0:
                nl = text.find(NL, e + 4)
                body0 = nl + 1 if nl >= 0 else len(text)
        hw = C.hard_wrapped(text, body0)
        view = C.unwrap_view(text, body0) if hw else text
        print("=" * 110)
        print(x["caseId"], x["era"], x["group"], "sc", s, L.node_row(s)[6][:60], "| below", b, L.node_row(b)[6][:60],
              "|", x["stage"], "|", d.get("reasons"))
        print("  DISP:", (d.get("disp_text") or "")[:200])
        for c in d.get("cands", []) or []:
            if c["j"] != b:
                continue
            for o in c["occ"][:3]:
                print("  OCC", o[1:], "|", L.norm(view[max(0, o[0] - w):o[0] + 60]))


if __name__ == "__main__":
    main()
