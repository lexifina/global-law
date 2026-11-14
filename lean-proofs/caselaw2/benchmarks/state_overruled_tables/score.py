"""Score one model build against the state overruled-tables key (see MAPPING.md).

    python -X utf8 score.py --out <dir> --data <dir> --label <x> [--asof yyyymmdd]

Reads key.tsv (built by scripts/link.py). Writes results/<label>.<h0|h1|all>.json (benchlib.write_result) and
results/<label>.cases.tsv (one row per overruled decision X).
Model side: <out>/status.tsv rows of X (any issue/holding level, any interval starting on or before --asof) with
status neg:* / unknown:* and path in {treatment, prospective}; admitted (<out>/certs.tsv ok) rows of
<data>/treatments.tsv targeting X with kind overruled / abrogated / disapproved / recededFrom.
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import benchlib  # noqa: E402

DATASET = "state_overruled_tables"
PATHS = {"treatment", "prospective"}
TKINDS = {"overruled", "abrogated", "disapproved", "recededFrom"}
PUB_END = {"georgia1922": 19221231, "labatt1860": 18601231, "desty1874": 18741231, "greenleaf1838": 18381231,
           "benjamin1893": 18931231}


def read_key():
    rows = []
    with open(os.path.join(HERE, "key.tsv"), encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(hdr, line.rstrip("\n").split("\t"))))
    return rows


def node_dates(ids):
    ids = {str(i) for i in ids}
    out = {}
    with open(os.path.join(benchlib.GRAPH, "nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            i = line.find("\t")
            if line[:i] in ids:
                p = line.split("\t", 6)
                try:
                    out[int(p[0])] = int(p[4])
                except ValueError:
                    out[int(p[0])] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)
    a = ap.parse_args()
    key = read_key()
    cases = {}
    link_n = collections.Counter()
    link_k = collections.Counter()
    fails = collections.defaultdict(collections.Counter)
    for r in key:
        half = r["half"] if r["half"] in ("h0", "h1") else None
        ok = r["pair_status"] == "linked"
        for sp in ("all", half):
            if sp is None:
                continue
            link_n[sp] += 1
            if ok:
                link_k[sp] += 1
            else:
                fails[sp][r["pair_status"]] += 1
        if not ok:
            continue
        x = int(r["x_node"])
        c = cases.setdefault(x, {"x": x, "key": r["x_key"], "half": r["half"], "ys": set(), "tables": set(),
                                 "partial": 0, "rows": [], "xdate": int(r["x_date"]), "name": r["x_corpus_name"],
                                 "pub_end": 0})
        c["ys"].add(int(r["y_node"]))
        c["tables"].add(r["table"])
        c["partial"] = max(c["partial"], int(r["partial"]))
        c["rows"].append(r["row_id"])
        c["pub_end"] = max(c["pub_end"], PUB_END[r["table"]])
    X = set(cases)
    # ---- model rows
    st = collections.defaultdict(list)
    sp_path = os.path.join(a.out, "status.tsv")
    with open(sp_path, encoding="utf-8") as f:
        next(f)
        for line in f:
            i = line.find("\t")
            n = line[:i]
            if not n.isdigit() or int(n) not in X:
                continue
            p = line.rstrip("\n").split("\t")
            s = p[5]
            if not (s.startswith("neg:") or s.startswith("unknown:")):
                continue
            if p[10] not in PATHS:
                continue
            if int(p[3]) > a.asof:
                continue
            try:
                actor = int(p[9])
            except ValueError:
                actor = -1
            st[int(n)].append({"status": s, "path": p[10], "actor": actor, "from": int(p[3]), "issue": p[1]})
    tr = benchlib.load_treatments(a.out, a.data, {str(x) for x in X})
    actors = set()
    for x in X:
        actors.update(e["actor"] for e in st.get(x, []) if e["actor"] >= 0)
        actors.update(int(t["by"]) for t in tr.get(str(x), []) if t["admitted"] and t["kind"] in TKINDS)
    adate = node_dates(actors)
    # ---- per case
    out_rows = []
    agg = collections.defaultdict(collections.Counter)
    for x, c in sorted(cases.items()):
        S = st.get(x, [])
        T = [t for t in tr.get(str(x), []) if t["admitted"] and t["kind"] in TKINDS]
        hit_s = [e for e in S if e["actor"] in c["ys"]]
        hit_t = [t for t in T if int(t["by"]) in c["ys"]]
        hit = bool(hit_s or hit_t)
        anym = bool(S or T)
        acts = {e["actor"] for e in S if e["actor"] >= 0} | {int(t["by"]) for t in T}
        early = {y for y in acts if 0 < adate.get(y, 99999999) <= c["pub_end"]}
        agree = bool(early & c["ys"])
        via = ("status" if hit_s else "") + ("+treatment" if hit_t else "")
        if hit:
            outc = "hit"
        elif anym:
            outc = "other_actor"
        else:
            outc = "nothing"
        for sp in ("all", c["half"]):
            g = agg[sp]
            g["n"] += 1
            g["hit"] += hit
            g["any"] += anym
            if early:
                g["aa_n"] += 1
                g["aa_k"] += agree
        out_rows.append([x, c["key"], c["half"], c["name"], c["xdate"], ",".join(sorted(c["tables"])),
                         ",".join(str(y) for y in sorted(c["ys"])), c["partial"], outc, via.strip("+") or "-",
                         int(anym), ";".join(sorted({"%s@%d:%s:by%d" % (e["status"], e["from"], e["path"], e["actor"])
                                                     for e in S}))[:400] or "-",
                         ";".join(sorted({"%s:by%s:%s" % (t["kind"], t["by"], t["scope"]) for t in T}))[:300] or "-",
                         ",".join(str(y) for y in sorted(early)) or "-", int(agree) if early else "-",
                         ",".join(c["rows"])])
    rd = os.path.join(HERE, "results")
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, a.label + ".cases.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(["x_node", "x_key", "half", "x_name", "x_date", "tables", "listed_overrulers", "partial",
                           "outcome", "hit_via", "model_any", "model_status_rows", "model_admitted_treatments",
                           "model_actors_before_pub_end", "actor_agrees", "key_rows"]) + "\n")
        for r in out_rows:
            o.write("\t".join(str(v) for v in r) + "\n")
    ssha = benchlib.file_sha1(sp_path)
    for sp in ("h0", "h1", "all"):
        g = agg[sp]
        res = {
            "dataset": DATASET, "label": a.label, "split": sp,
            "row_label": "State tables of overruled cases (GA 1922, CA 1860/1874, NY 1893, Greenleaf 1838)",
            "tests": "overruling", "court": "state", "blind": True, "primary": "recall",
            "metrics": {"recall": benchlib.metric(g["hit"], g["n"]),
                        "recall_any": benchlib.metric(g["any"], g["n"]),
                        "actor_agreement": benchlib.metric(g["aa_k"], g["aa_n"]),
                        "link_rate": benchlib.metric(link_k[sp], link_n[sp])},
            "link": {"n_items": link_n[sp], "linked": link_k[sp], "fail_reasons": dict(fails[sp])},
            "build": {"out": os.path.abspath(a.out), "data": os.path.abspath(a.data), "status_sha1": ssha},
            "asof": a.asof, "generated": benchlib.now(),
            "notes": ("Unit = overruled decision X (linked); recall = model negative/unknown via treatment/prospective "
                      "path with actor among the listed overruling decisions, or an admitted overruled/abrogated/"
                      "disapproved/recededFrom treatment by one of them; recall_any = same by any actor; "
                      "actor_agreement = of X with a model overruling actor dated by the end of the table's "
                      "publication year, share where such an actor is listed. link_rate counts primary table rows "
                      "((treated, treating) citation pairs); h0/h1 link counts exclude rows whose treated side did "
                      "not link (no split key). No precision metric (positives-only key; see MAPPING.md)."),
        }
        benchlib.write_result(os.path.join(rd, "%s.%s.json" % (a.label, sp)), res)
        m = res["metrics"]
        print(sp, " ".join("%s=%d/%d" % (k, v["k"], v["n"]) for k, v in m.items()))


if __name__ == "__main__":
    main()
