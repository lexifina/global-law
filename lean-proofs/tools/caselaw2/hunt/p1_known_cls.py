"""Pattern 1, recall of the classification step on the known call-out instances: build zombie-task inputs for every
call-out where the relying decision cites the overruled one and the LLM read the call-out as reliance after the
overruling (or our status says so).

    python p1_known_cls.py  -> work/p1_known_passages.jsonl, work/p1_known_zombie_in.jsonl
    python llm_run.py zombie work/p1_known_zombie_in.jsonl work/p1_known_zombie_out.jsonl
"""
import csv, json, os
import hcommon as C
import passages as P


def main():
    rows = list(csv.DictReader(open(os.path.join(C.HUNT, "data", "p1_known_callouts.tsv"), encoding="utf-8"),
                               delimiter="\t"))
    ins = {}
    for l in open(os.path.join(C.HWORK, "p1_callout_in.jsonl"), encoding="utf-8"):
        j = json.loads(l)
        ins[j["note_node"]] = j
    keep = [r for r in rows if r["relier_cites_target"] == "1" and (r["llm_after"] == "yes" or r["relier_after_neg"] == "1")]
    seen, items = set(), []
    for r in keep:
        k = (int(r["relier"]), int(r["target"]))
        if k in seen:
            continue
        seen.add(k)
        note = ins.get(int(r["note_node"]), {})
        items.append(dict(citing=k[0], cited=k[1], actor=None, note_node=int(r["note_node"]),
                          wquote="(a later court, %s, says: ) %s" % (r["note_name"], (note.get("window") or "")[900:1500])))
    out = os.path.join(C.HWORK, "p1_known_passages.jsonl")
    P.run(items, out, workers=4)
    rows2 = [json.loads(l) for l in open(out, encoding="utf-8")]
    meta = C.nodes({r["citing"] for r in rows2} | {r["cited"] for r in rows2})
    with open(os.path.join(C.HWORK, "p1_known_zombie_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows2:
            mc, md = meta[r["citing"]], meta[r["cited"]]
            r.update(hkey="known|%s|%s" % (r["citing"], r["cited"]), kind="citesOverruled", wkind="overruled",
                     neg_from="(before the citing opinion, per the later court)", actor_name="-", actor_cite="-",
                     cited_name=md["name"], cited_cite=md["cite"].split("|")[0], cited_court_name=md["court_name"],
                     cited_date=md["date"], citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0],
                     citing_court_name=mc["court_name"], citing_date=mc["date"])
            f.write(json.dumps(r) + "\n")
    C.log("known instances", len(rows2))


if __name__ == "__main__":
    main()
