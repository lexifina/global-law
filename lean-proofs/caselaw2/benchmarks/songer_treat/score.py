#!/usr/bin/env python3
"""Score one build against the Songer / Kuersten-Haire TREAT key (MAPPING.md).

    python score.py --out <build out dir> --data <build data dir> --label <x> [--asof 20261112] [--results <dir>]
    python score.py --label round6            (out/data default to benchlib.BUILDS[label])

Writes <results>/<label>.<split>.json for split in h0, h1, all (benchlib.write_result) and
<results>/<label>.cases.tsv. Primary population: linked decisions below cited by the linked appellate decision
(`cited`); the `*_any` metrics use every linked decision below.
"""
import argparse
import collections
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import benchlib  # noqa: E402

DS = "songer_treat"
CLEAN_M = ("GOOD", "NEG_OTHER", "UNK_OTHER")


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def metrics_for(units):
    """units: list of (class, mclass)."""
    neg = [m for c, m in units if c == "NEG"]
    part = [m for c, m in units if c == "PART"]
    clean = [m for c, m in units if c == "CLEAN"]
    mneg = [c for c, m in units if m == "NEG_HIST" and c in ("NEG", "PART", "CLEAN")]
    return {
        "recall": benchlib.metric(sum(m == "NEG_HIST" for m in neg), len(neg)),
        "recall_lenient": benchlib.metric(sum(m in ("NEG_HIST", "UNK_HIST") for m in neg), len(neg)),
        "precision": benchlib.metric(sum(c == "NEG" for c in mneg), len(mneg)),
        "precision_lenient": benchlib.metric(sum(c in ("NEG", "PART") for c in mneg), len(mneg)),
        "clean": benchlib.metric(sum(m in CLEAN_M for m in clean), len(clean)),
        "part": benchlib.metric(sum(m in ("NEG_HIST", "UNK_HIST") for m in part), len(part)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--data")
    ap.add_argument("--label", required=True)
    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)
    ap.add_argument("--results", default=os.path.join(HERE, "results"))
    ap.add_argument("--blind", default="1", help="1 (default) unless the build was tuned on this key")
    a = ap.parse_args()
    out_dir = a.out or benchlib.BUILDS[a.label][0]
    data_dir = a.data or benchlib.BUILDS[a.label][1]
    out_dir, data_dir = os.path.abspath(out_dir), os.path.abspath(data_dir)

    units = list(rows(os.path.join(HERE, "key_nodes.tsv")))
    items = [r for r in rows(os.path.join(HERE, "key.tsv")) if r["key_item"] == "1"]
    nodes = {u["below_node"] for u in units}
    st = benchlib.load_status(out_dir, nodes=nodes, asof=a.asof)
    hist = benchlib.load_history(out_dir, data_dir, nodes)
    status_sha1 = benchlib.file_sha1(os.path.join(out_dir, "status.tsv"))

    os.makedirs(a.results, exist_ok=True)
    cols = ["below_node", "half", "class", "cited", "mclass", "status", "path", "witness", "actor", "agree",
            "hist_rows", "case_classes", "treats", "casenums", "app_nodes", "below_date", "below_name"]
    with open(os.path.join(a.results, "%s.cases.tsv" % a.label), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for u in units:
            s = benchlib.status_of(st, u["below_node"])
            u["_m"] = s["mclass"]
            c = u["class"]
            agree = {"NEG": s["mclass"] == "NEG_HIST", "PART": s["mclass"] in ("NEG_HIST", "UNK_HIST"),
                     "CLEAN": s["mclass"] in CLEAN_M}.get(c)
            hr = ";".join("%s:%s:%s:%s" % (h["kind"], h["by"], h["date"], "ok" if h["admitted"] else "no")
                          for h in hist.get(u["below_node"], []))
            o.write("\t".join([u["below_node"], u["half"], c, u["cited"], s["mclass"], s["status"], s["path"],
                               s["witness"], s["actor"], "-" if agree is None else str(int(agree)), hr or "-",
                               u["case_classes"], u["treats"], u["casenums"], u["app_nodes"], u["below_date"],
                               u["below_name"]]) + "\n")

    for split in ("h0", "h1", "all"):
        us = [u for u in units if split == "all" or u["half"] == split]
        its = [r for r in items if split == "all" or r["half"] == split]
        prim = metrics_for([(u["class"], u["_m"]) for u in us if u["cited"] == "1"])
        sec = metrics_for([(u["class"], u["_m"]) for u in us])
        linked = sum(r["status"] == "linked" for r in its)
        fails = collections.Counter(r["reason"] for r in its if r["status"] != "linked")
        excluded = collections.Counter(r["excluded"] for r in its if r["status"] == "linked" and r["excluded"])
        m = dict(prim)
        m["link_rate"] = benchlib.metric(linked, len(its))
        for k, v in sec.items():
            m[k + "_any"] = v
        cls_n = collections.Counter((u["class"], u["cited"]) for u in us)
        mdist = collections.Counter((u["class"], u["_m"]) for u in us if u["cited"] == "1")
        notes = ("Primary population: linked decisions below (named by Songer/Kuersten-Haire PRIORPUB) cited by the "
                 "linked appellate decision (MAPPING.md). recall/precision/clean/part on that population; *_any = "
                 "every linked decision below. recall_lenient counts UNK_HIST as negative; precision_lenient counts "
                 "PART as source-negative. link_rate: Songer cases with TREAT class NEG/PART/CLEAN and a PRIORPUB, "
                 "linked to one appellate and one district/bankruptcy decision. Linked items excluded for freshness "
                 "(FJC key overlap): %s. Units by class/cited: %s. Cited units class x model: %s."
                 % (dict(excluded), dict(sorted(("%s/%s" % k, v) for k, v in cls_n.items())),
                    dict(sorted(("%s>%s" % k, v) for k, v in mdist.items()))))
        res = {
            "dataset": DS, "label": a.label, "split": split,
            "row_label": "Songer appeals: district decision reversed/vacated",
            "tests": "same-case", "court": "federal", "blind": a.blind == "1", "primary": "recall",
            "metrics": m,
            "link": {"n_items": len(its), "linked": linked, "fail_reasons": dict(fails.most_common())},
            "build": {"out": out_dir, "data": data_dir, "status_sha1": status_sha1},
            "asof": a.asof, "generated": benchlib.now(), "notes": notes,
        }
        benchlib.write_result(os.path.join(a.results, "%s.%s.json" % (a.label, split)), res)
        print(split, {k: "%d/%d" % (v["k"], v["n"]) for k, v in m.items()})


if __name__ == "__main__":
    main()
