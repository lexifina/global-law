#!/usr/bin/env python3
"""Score one build against the en banc key (Beim, Hirsch & Kastellec; MAPPING.md).

    python score.py --out <build out dir> --data <build data dir> --label <x> [--asof 20261112]

Writes results/<label>.<split>.json for split in h0, h1, all (benchlib.write_result) and results/<label>.cases.tsv.
Every unit is source-negative (a panel decision later reheard en banc): expected NEG_HIST. Node ids that the key does not
hold (e.g. extra staged order nodes) are never read: status/history rows are filtered to the key's panel nodes.
"""
import argparse
import collections
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import benchlib  # noqa: E402

DS = "bhk_enbanc"


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


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
    items = list(rows(os.path.join(a.key, "key.tsv")))
    nodes = {u["panel_node"] for u in units}
    st = benchlib.load_status(out_dir, nodes=nodes, asof=a.asof)
    hist = benchlib.load_history(out_dir, data_dir, nodes)
    status_sha1 = benchlib.file_sha1(os.path.join(out_dir, "status.tsv"))

    os.makedirs(a.results, exist_ok=True)
    cols = ["panel_node", "half", "class", "sub", "confirmed", "mclass", "status", "path", "witness", "actor", "agree",
            "by_enbanc", "hist_rows", "eb_nodes", "item_uids", "source", "via", "panel_repo", "panel_court",
            "panel_date", "panel_name"]
    with open(os.path.join(a.results, "%s.cases.tsv" % a.label), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for u in units:
            s = benchlib.status_of(st, u["panel_node"])
            u["_m"] = s["mclass"]
            hs = hist.get(u["panel_node"], [])
            ebs = set(u["eb_confirmed"].split(";")) - {"-", ""}
            u["_by"] = (s["mclass"] == "NEG_HIST" and any(h["admitted"] and h["by"] in ebs for h in hs))
            hr = ";".join("%s:%s:%s:%s" % (h["kind"], h["by"], h["date"], "ok" if h["admitted"] else "no") for h in hs)
            o.write("\t".join([u["panel_node"], u["half"], u["class"], u["sub"], u["confirmed"], s["mclass"],
                               s["status"], s["path"], s["witness"], s["actor"], str(int(s["mclass"] == "NEG_HIST")),
                               str(int(u["_by"])), hr or "-", u["eb_nodes"], u["item_uids"], u["source"], u["via"],
                               u["panel_repo"], u["panel_court"], u["panel_date"], u["panel_name"]]) + "\n")

    def rec(us):
        return benchlib.metric(sum(u["_m"] == "NEG_HIST" for u in us), len(us))

    for split in ("h0", "h1", "all"):
        us = [u for u in units if split == "all" or u["half"] == split]
        its = [r for r in items if split == "all" or r["half"] == split]
        conf = [u for u in us if u["confirmed"] == "1"]
        m = {
            "recall": rec(us),
            "recall_lenient": benchlib.metric(sum(u["_m"] in ("NEG_HIST", "UNK_HIST") for u in us), len(us)),
            "recall_R": rec([u for u in us if u["sub"] == "R"]),
            "recall_S": rec([u for u in us if u["sub"] == "S"]),
            "recall_U": rec([u for u in us if u["sub"] == "U"]),
            "recall_confirmed": rec(conf),
            "recall_by_enbanc": benchlib.metric(sum(u["_by"] for u in conf), len(conf)),
            "link_rate": benchlib.metric(sum(r["status"] == "linked" for r in its), len(its)),
        }
        linked = sum(r["status"] == "linked" for r in its)
        fails = collections.Counter(r["reason"] for r in its if r["status"] != "linked")
        mdist = collections.Counter((u["sub"], u["_m"]) for u in us)
        notes = ("Every unit is a published court of appeals panel decision (1986-2002) that the full court later reheard "
                 "en banc (Beim, Hirsch & Kastellec 2016 + Clark 2009 en banc lists; Songer-sample rows excluded): "
                 "expected NEG_HIST. No source-clean items, so precision/clean are not reported. recall_R / recall_S / "
                 "recall_U: en banc decision of opposite / same / uncoded ideological direction. recall_confirmed: units "
                 "whose linked en banc decision cites the panel decision in the corpus graph. recall_by_enbanc: of those, "
                 "NEG_HIST with an admitted history row by that en banc decision. Units sub>model: %s."
                 % dict(sorted(("%s>%s" % k, v) for k, v in mdist.items())))
        res = {
            "dataset": DS, "label": a.label, "split": split,
            "row_label": "Courts of appeals: panel decision reheard en banc (Beim-Hirsch-Kastellec)",
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
