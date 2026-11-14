#!/usr/bin/env python3
"""Score one build against the Federal Circuit Dataset Project key (MAPPING.md).

    python score.py --out <build out dir> --data <build data dir> --label <x> [--asof 20261112]

Writes results/<label>.<split>.json for split in h0, h1, all (benchlib.write_result) and results/<label>.cases.tsv.
Primary population: linked decisions below cited by the linked Federal Circuit decision (`cited`); the `*_all`
metrics use every linked decision below (cited or caption-only).
"""
import argparse
import collections
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import benchlib  # noqa: E402

DS = "fedcir_dataset"
CLEAN_M = ("GOOD", "NEG_OTHER", "UNK_OTHER")
ORIGINS = ("DCT", "CFC", "CIT", "CAVC")


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def agree_of(c, m):
    return {"NEG": m == "NEG_HIST", "PART": m in ("NEG_HIST", "UNK_HIST"), "CLEAN": m in CLEAN_M}.get(c)


def metrics_for(units):
    """units: list of (class, mclass). Returns metric dict (benchlib.metric)."""
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


def frac(m):
    return "%d/%d" % (m["k"], m["n"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)
    ap.add_argument("--key", default=HERE, help="folder holding key.tsv and key_nodes.tsv (default: this folder)")
    ap.add_argument("--results", default=os.path.join(HERE, "results"))
    a = ap.parse_args()
    out_dir, data_dir = os.path.abspath(a.out), os.path.abspath(a.data)

    units = list(rows(os.path.join(a.key, "key_nodes.tsv")))
    items = [r for r in rows(os.path.join(a.key, "key.tsv")) if r["key_item"] == "1"]
    nodes = {u["below_node"] for u in units}
    st = benchlib.load_status(out_dir, nodes=nodes, asof=a.asof)
    hist = benchlib.load_history(out_dir, data_dir, nodes)
    status_sha1 = benchlib.file_sha1(os.path.join(out_dir, "status.tsv"))

    os.makedirs(a.results, exist_ok=True)
    cols = ["below_node", "half", "class", "cited", "origin", "mclass", "status", "path", "witness", "actor", "agree",
            "hist_rows", "record_classes", "fc_uids", "cafc_nodes", "via", "below_repo", "below_court", "below_date",
            "below_name"]
    with open(os.path.join(a.results, "%s.cases.tsv" % a.label), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for u in units:
            s = benchlib.status_of(st, u["below_node"])
            u["_m"] = s["mclass"]
            agree = agree_of(u["class"], s["mclass"])
            hr = ";".join("%s:%s:%s:%s" % (h["kind"], h["by"], h["date"], "ok" if h["admitted"] else "no")
                          for h in hist.get(u["below_node"], []))
            o.write("\t".join([u["below_node"], u["half"], u["class"], u["cited"], u["origin"], s["mclass"],
                               s["status"], s["path"], s["witness"], s["actor"],
                               "-" if agree is None else str(int(agree)), hr or "-", u["record_classes"],
                               u["fc_uids"], u["cafc_nodes"], u["via"], u["below_repo"], u["below_court"],
                               u["below_date"], u["below_name"]]) + "\n")

    for split in ("h0", "h1", "all"):
        us = [u for u in units if split == "all" or u["half"] == split]
        its = [r for r in items if split == "all" or r["half"] == split]
        pre = [r for r in its if r["doc_date"] < "20190101"]
        m = dict(metrics_for([(u["class"], u["_m"]) for u in us if u["cited"] == "1"]))
        m["link_rate"] = benchlib.metric(sum(r["status"] == "linked" for r in its), len(its))
        m["link_rate_cited"] = benchlib.metric(sum(r["status"] == "linked" and r["cited"] == "1" for r in its),
                                               len(its))
        m["link_rate_pre2019"] = benchlib.metric(sum(r["status"] == "linked" for r in pre), len(pre))
        for k, v in metrics_for([(u["class"], u["_m"]) for u in us]).items():
            m[k + "_all"] = v
        by_origin = {}
        for og in ORIGINS:
            mo = metrics_for([(u["class"], u["_m"]) for u in us if u["cited"] == "1" and u["origin"] == og])
            by_origin[og] = "recall %s, clean %s" % (frac(mo["recall"]), frac(mo["clean"]))
        linked = sum(r["status"] == "linked" for r in its)
        fails = collections.Counter(r["reason"] for r in its if r["status"] != "linked")
        cls_n = collections.Counter((u["class"], u["cited"]) for u in us)
        mdist = collections.Counter((u["class"], u["_m"]) for u in us if u["cited"] == "1")
        notes = ("Primary population: linked decisions below (district court, Court of Federal Claims, Court of "
                 "International Trade, Court of Appeals for Veterans Claims) cited by the linked Federal Circuit "
                 "decision (MAPPING.md). recall/precision/clean/part on that population; *_all = every linked "
                 "decision below (cited or caption-only). recall_lenient counts UNK_HIST as negative; "
                 "precision_lenient counts PART as source-negative. link_rate: key items linked to one Federal "
                 "Circuit and one decision-below node; link_rate_pre2019: items dated before 2019 (lower-court corpus "
                 "ends 2017-2019). Cited units by tribunal: %s. Units by class/cited: %s. Cited units class>model: %s."
                 % (by_origin, dict(sorted(("%s/%s" % k, v) for k, v in cls_n.items())),
                    dict(sorted(("%s>%s" % k, v) for k, v in mdist.items()))))
        res = {
            "dataset": DS, "label": a.label, "split": split,
            "row_label": "Federal Circuit: decision below reversed/vacated (Fed. Cir. Dataset Project)",
            "tests": "same-case", "court": "federal", "blind": True, "primary": "recall",
            "metrics": m,
            "link": {"n_items": len(its), "linked": linked, "fail_reasons": dict(fails.most_common())},
            "build": {"out": out_dir, "data": data_dir, "status_sha1": status_sha1},
            "asof": a.asof, "generated": benchlib.now(), "notes": notes,
        }
        benchlib.write_result(os.path.join(a.results, "%s.%s.json" % (a.label, split)), res)
        print(split, {k: frac(v) for k, v in m.items()})


if __name__ == "__main__":
    main()
