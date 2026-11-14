"""stlink11 step 1: identity-tie features of every (D, T) pair of the uncited-review population.

    python -X utf8 feat.py [--procs 8]   -> work/feat.jsonl (one record per D: candidates with their ties)

Population: state court-of-last-resort opinions D whose judgment line is negative for the intermediate court
(round-10 pop.py records, ka in reversed/vacated/modified), with no v10d review-kind row on an intermediate decision
of their state, no cited same-state intermediate decision sharing a party name (cap >= 1, 0..5 y), and at least one
same-caption (cap 2) intermediate decision 0..5 y before D (pop_capmatch). Every such candidate T is measured:
full party names (front matter `parties` of D and T), T's docket printed in D, T's date printed in D, T's citation
printed in D (front `cites_cases` or body). No key.
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import BO, L  # noqa: E402
import ties  # noqa: E402

NL = chr(10)
POP10 = os.path.join(L.C2, "round10", "agents", "stlink10", "work", "pop")
NEG = {"reversed", "vacated", "modified"}


def work_items():
    based = set(json.load(open(os.path.join(HERE, "work", "base_by_app.json"))))
    cm = {}
    for l in open(os.path.join(HERE, "work", "pop_capmatch.jsonl"), encoding="utf-8"):
        d = json.loads(l)
        cm[d["n"]] = d["m"]
    uu = set()
    for l in open(os.path.join(HERE, "work", "uncited_unique.tsv"), encoding="utf-8"):
        p = l.split("\t")
        if p[0].isdigit():
            uu.add((int(p[0]), int(p[1])))
    items = []
    st = collections.Counter()
    for f in sorted(os.listdir(POP10)):
        if not f.endswith(".jsonl"):
            continue
        for l in open(os.path.join(POP10, f), encoding="utf-8"):
            r = json.loads(l)
            if r["ka"] not in NEG or r["n"] not in cm:
                continue
            st["neg_with_capm"] += 1
            if r["n"] in based:
                st["drop_based"] += 1
                continue
            if any(c["cap"] >= 1 for c in r["cands"]):
                st["drop_cited_samelit"] += 1
                continue
            st["items"] += 1
            items.append({"n": r["n"], "tag": r["tag"], "sys": r["sys"], "date": r["date"], "ka": r["ka"],
                          "sa": r["sa"], "how": r["how"], "m": cm[r["n"]],
                          "uu": [j for j, _g in cm[r["n"]] if (r["n"], j) in uu]})
    print(dict(st), flush=True)
    return items


def run_chunk(chunk):
    nodes = set()
    for it in chunk:
        nodes.add(it["n"])
        nodes |= {j for j, _g in it["m"]}
    texts = L.fetch_texts(sorted(nodes))
    parsed = {n: ties.parse(t[1]) for n, t in texts.items()}
    out = []
    for it in chunk:
        D = parsed.get(it["n"])
        if D is None:
            it["err"] = "no_text"
            out.append(it)
            continue
        df = D["front"]
        dtext_front = "\n".join("%s: %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in df.items() if k != "docket")
        dfull = dtext_front + "\n" + D["body"]
        dset = ties.dates_in(D["body"])
        cands = []
        for j, gap in it["m"]:
            Tt = parsed.get(j)
            if Tt is None:
                cands.append({"j": j, "err": "no_text"})
                continue
            tf = Tt["front"]
            row = L.node_row(j)
            nm, nd = ties.names_tie(df.get("parties"), tf.get("parties"))
            dk, dtok, dctx = ties.docket_tie(dfull, df, tf)
            dt = ties.date_tie(D["body"], tf, dset)
            ct, cc = ties.cite_tie(dfull, df, row[5])
            cands.append({"j": j, "gap": gap, "tdate": int(row[4]), "court": row[1], "names": nm, "names_d": nd,
                          "docket": dk, "dtok": dtok, "dctx": dctx, "date": dt, "cite": ct, "cite_s": cc,
                          "tparties": tf.get("parties"), "tdocket": tf.get("docket")})
        it["dparties"] = df.get("parties")
        it["ddocket"] = df.get("docket")
        it["cands"] = cands
        out.append(it)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    items = work_items()
    if a.limit:
        items = items[:a.limit]
    chunks = [items[i:i + 400] for i in range(0, len(items), 400)]
    with open(os.path.join(HERE, "work", "feat.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        k = 0
        for res in L.pmap(run_chunk, chunks, procs=a.procs):
            for it in res:
                f.write(json.dumps(it, ensure_ascii=False) + NL)
            k += 1
            print("chunk", k, "/", len(chunks), flush=True)


if __name__ == "__main__":
    main()
