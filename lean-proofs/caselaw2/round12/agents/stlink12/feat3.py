"""stlink12 step 1: third-tie features over the full-names-only pool (work/pool.jsonl) and, as a reference, over the
installed U2 pairs (round 11 rows_u2c / rows_u2w: full names + second tie).  -> work/feat3.jsonl

    python -X utf8 feat3.py [--procs 8]
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import L  # noqa: E402
import ties, ties3  # noqa: E402

NL = chr(10)
R11 = os.path.join(HERE, "..", "..", "..", "round11", "agents", "stlink11")


def run_chunk(chunk):
    nodes = set()
    for it in chunk:
        nodes |= {it["n"], it["j"]}
    texts = L.fetch_texts(sorted(nodes))
    out = []
    for it in chunk:
        if it["n"] not in texts or it["j"] not in texts:
            it["err"] = "no_text"
            out.append(it)
            continue
        D = ties.parse(texts[it["n"]][1])
        T = ties.parse(texts[it["j"]][1])
        if it["src"] == "u2":
            nm, nd = ties.names_tie(D["front"].get("parties"), T["front"].get("parties"))
            it["ents"] = [e for e in nd.split("|") if e]
        it["strict"] = ties3.strict_names("|".join(it.get("ents") or []))
        it["ties3"] = ties3.all_ties(D, T)
        out.append(it)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    items = []
    for l in open(os.path.join(HERE, "work", "pool.jsonl"), encoding="utf-8"):
        d = json.loads(l)
        d["src"] = "pool"
        items.append(d)
    for f in ("rows_u2c.jsonl", "rows_u2w.jsonl"):
        for l in open(os.path.join(R11, f), encoding="utf-8"):
            r = json.loads(l)
            items.append({"n": r["by"], "j": r["target"], "src": "u2", "ka": r["kind"]})
    chunks = [items[i:i + 300] for i in range(0, len(items), 300)]
    st = collections.Counter()
    with open(os.path.join(HERE, "work", "feat3.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for res in L.pmap(run_chunk, chunks, procs=a.procs):
            for it in res:
                f.write(json.dumps(it, ensure_ascii=False) + NL)
                if "err" in it:
                    st[it["src"] + ":err"] += 1
                    continue
                s = it["src"] + (":strict" if it["strict"] else ":loose")
                st[s] += 1
                for k in it["ties3"]:
                    st[s + ":" + k] += 1
                st[s + ":any" if it["ties3"] else s + ":none"] += 1
    for k in sorted(st):
        print(k, st[k])


if __name__ == "__main__":
    main()
