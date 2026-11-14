"""b4sc: document frequency of caption party tokens over every decision (graph/nodes.tsv titles), and the
"institutional" tokens: those of a caption side of two or more tokens printed in >= 300 titles (an agency, a board,
a county), -> work/inst_tokens.json.

    python -X utf8 tokdf.py [--procs 22]   -> work/tokdf.json  {token: number of titles carrying it}
Tokens as round 6 compares them: reader name_tokens | short_name_tokens, lower-cased, trailing "s" dropped.
Used by R3 (a shared caption token must be distinctive). No answer key.
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

C = L.reader_common()
import re  # noqa: E402
SIDE = re.compile(r"\s+vs?\.?\s+", re.I)


def work(job):
    a, b = job
    cnt = collections.Counter()
    with open(L.NODES, "rb") as f:
        f.seek(a)
        if a:
            f.readline()
        while f.tell() <= b:
            line = f.readline()
            if not line:
                break
            p = line.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            t = p[6]
            cnt.update({w.lower().rstrip("s") for w in (C.name_tokens(t) | C.short_name_tokens(t))})
            for side in SIDE.split(t, maxsplit=1):
                st = sorted({w.lower().rstrip("s") for w in (C.name_tokens(side) | C.short_name_tokens(side))})
                if len(st) >= 2:
                    cnt["\x00" + " ".join(st)] += 1
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=22)
    a = ap.parse_args()
    size = os.path.getsize(L.NODES)
    k = 200
    jobs = [(size * i // k, size * (i + 1) // k - 1) for i in range(k)]
    tot = collections.Counter()
    for c in L.pmap(work, jobs, procs=a.procs):
        tot.update(c)
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    sides = {k[1:]: v for k, v in tot.items() if k.startswith("\x00")}
    tok = {k: v for k, v in tot.items() if not k.startswith("\x00")}
    inst = sorted({w for k, v in sides.items() if v >= 300 for w in k.split(" ")})
    json.dump(tok, open(os.path.join(HERE, "work", "tokdf.json"), "w", encoding="utf-8"))
    json.dump(inst, open(os.path.join(HERE, "work", "inst_tokens.json"), "w", encoding="utf-8"))
    print("institutional tokens (in a multi-token side printed >= 300 times):", len(inst), inst[:80])
    tot = collections.Counter(tok)
    print("tokens", len(tot), tot.most_common(30))


if __name__ == "__main__":
    main()
