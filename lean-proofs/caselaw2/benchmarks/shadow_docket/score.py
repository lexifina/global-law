#!/usr/bin/env python3
"""Score one model build against the Shadow Docket key (MAPPING.md).

    python score.py --out <build out dir> --data <build data dir> --label <round4|round6|round7...> [--asof yyyymmdd]

Reads key.tsv (link.py) and <out>/status.tsv. Writes results/<label>.<split>.json for split in h0, h1, all (dataset
`shadow_docket`, court mixed), results/<label>.federal.all.json and results/<label>.state.all.json (datasets
`shadow_docket_federal` / `shadow_docket_state`: the same metrics restricted by the court of the decision below),
and the per-node table results/<label>.cases.tsv.
"""
import argparse
import collections
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sdlib  # noqa: E402
from sdlib import benchlib  # noqa: E402

SCORE = ("NEG", "PART", "CLEAN")


def plus_days(d, n):
    d = int(d)
    x = datetime.date(d // 10000, d // 100 % 100, d % 100) + datetime.timedelta(days=n)
    return int(x.strftime("%Y%m%d"))


def load_intervals(out_dir, nodes):
    iv = collections.defaultdict(list)
    with open(os.path.join(out_dir, "status.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] != "-" or p[2] != "-" or p[0] not in nodes:
                continue
            iv[p[0]].append((int(p[3]), int(p[4]), p[5], p[10], p[9], p[8]))
    return iv


def status_at(iv, node, d):
    for a, b, st, path, actor, wit in iv.get(node, ()):
        if a <= d <= b:
            return {"status": st, "path": path, "actor": actor, "witness": wit,
                    "mclass": benchlib.model_class(st, path)}
    return {"status": "good", "path": "-", "actor": "-", "witness": "-", "mclass": "GOOD"}


def court_kind(label):
    if label.startswith("state:"):
        return "state"
    if label in ("-", ""):
        return "-"
    return "federal"


def pool(items):
    cls = [it["class"] for it in items]
    if "PART" in cls or ("NEG" in cls and "CLEAN" in cls):
        return "PART", "mixed" if "PART" not in cls else "affirmed_in_part"
    if "NEG" in cls:
        return "NEG", next(it["sub"] for it in items if it["class"] == "NEG")
    return "CLEAN", items[-1]["sub"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)
    a = ap.parse_args()

    items = []
    with open(os.path.join(HERE, "key.tsv"), encoding="utf-8") as f:
        hdr = next(f).rstrip("\n").split("\t")
        for line in f:
            it = dict(zip(hdr, line.rstrip("\n").split("\t")))
            if it["class"] in SCORE:
                items.append(it)
    bynode = collections.defaultdict(list)
    for it in items:
        if it["link"] == "linked":
            bynode[it["node"]].append(it)
    iv = load_intervals(a.out, set(bynode))
    cases = []
    for node, its in bynode.items():
        its.sort(key=lambda x: x["sc_docket"])
        cls, sub = pool(its)
        half = benchlib.split_half(sdlib.DATASET, its[0]["sc_docket"])
        neg_dates = [int(x["order_date"]) for x in its if x["class"] in ("NEG", "PART")]
        od = min(neg_dates) if neg_dates else max(int(x["order_date"]) for x in its)
        s = status_at(iv, node, a.asof)
        s2 = status_at(iv, node, plus_days(od, 90))
        cases.append({"node": node, "half": half, "class": cls, "sub": sub, "order_date": od,
                      "court": court_kind(its[0]["court_label"]), "court_label": its[0]["court_label"],
                      "sc_in_corpus": "yes" if any(x["sc_in_corpus"] == "yes" for x in its) else "no",
                      "dockets": ",".join(x["sc_docket"] for x in its), "node_date": its[0]["node_date"],
                      "title": its[0]["node_title"], "m": s, "m_at_order": s2})

    def metrics(cs, its):
        neg = [c for c in cs if c["class"] == "NEG"]
        cln = [c for c in cs if c["class"] == "CLEAN"]
        mneg = [c for c in cs if c["m"]["mclass"] == "NEG_HIST"]
        linked = sum(1 for x in its if x["link"] == "linked")
        m = {"recall": benchlib.metric(sum(c["m"]["mclass"] == "NEG_HIST" for c in neg), len(neg)),
             "precision": benchlib.metric(sum(c["class"] == "NEG" for c in mneg), len(mneg)),
             "clean": benchlib.metric(sum(c["m"]["mclass"] not in ("NEG_HIST", "UNK_HIST") for c in cln), len(cln)),
             "link_rate": benchlib.metric(linked, len(its))}
        ex = {"recall_lenient": benchlib.metric(sum(c["m"]["mclass"] in ("NEG_HIST", "UNK_HIST") for c in neg),
                                                len(neg)),
              "precision_lenient": benchlib.metric(sum(c["class"] in ("NEG", "PART") for c in mneg), len(mneg)),
              "recall_at_order_plus_90d": benchlib.metric(
                  sum(c["m_at_order"]["mclass"] == "NEG_HIST" for c in neg), len(neg)),
              "recall_sc_order_in_corpus": benchlib.metric(
                  sum(c["m"]["mclass"] == "NEG_HIST" for c in neg if c["sc_in_corpus"] == "yes"),
                  sum(1 for c in neg if c["sc_in_corpus"] == "yes")),
              "recall_sc_order_not_in_corpus": benchlib.metric(
                  sum(c["m"]["mclass"] == "NEG_HIST" for c in neg if c["sc_in_corpus"] == "no"),
                  sum(1 for c in neg if c["sc_in_corpus"] == "no")),
              "part_neg_or_unk": benchlib.metric(
                  sum(c["m"]["mclass"] in ("NEG_HIST", "UNK_HIST") for c in cs if c["class"] == "PART"),
                  sum(1 for c in cs if c["class"] == "PART"))}
        for sb in ("gvr", "vacated", "reversed"):
            ns = [c for c in neg if c["sub"] == sb]
            ex["recall_" + sb] = benchlib.metric(sum(c["m"]["mclass"] == "NEG_HIST" for c in ns), len(ns))
        for sb in ("cert_denied", "cert_dismissed", "dig", "affirmed"):
            ns = [c for c in cln if c["sub"] == sb]
            ex["clean_" + sb] = benchlib.metric(
                sum(c["m"]["mclass"] not in ("NEG_HIST", "UNK_HIST") for c in ns), len(ns))
        fr = collections.Counter(x["link"] for x in its if x["link"] != "linked")
        link = {"n_items": len(its), "linked": linked, "fail_reasons": dict(fr.most_common())}
        return m, ex, link

    sha = benchlib.file_sha1(os.path.join(a.out, "status.tsv"))
    res_dir = os.path.join(HERE, "results")
    gen = benchlib.now()

    def emit(path, dataset, split, court, row_label, cs, its, note):
        m, ex, link = metrics(cs, its)
        benchlib.write_result(path, {
            "dataset": dataset, "label": a.label, "split": split, "row_label": row_label, "tests": "same-case",
            "court": court, "blind": True, "primary": "recall", "metrics": m, "extra_metrics": ex, "link": link,
            "build": {"out": a.out, "data": a.data, "status_sha1": sha}, "asof": a.asof, "generated": gen,
            "notes": note})
        return m, ex

    base_note = ("Supreme Court orders 1993-2025 terms (Kastellec & Taboni v2.0). NEG = GVR / judgment vacated / "
                 "summary reversal; CLEAN = cert denied / dismissed / DIG / summarily affirmed. Linked by lower-court "
                 "docket number + court + date window (link.py); unit = linked lower decision. Recall: model NEG_HIST; "
                 "clean: model not NEG_HIST/UNK_HIST. extra_metrics: lenient, by sub-class, status at order+90d, "
                 "and split by whether the Supreme Court order text is in the corpus. See REPORT.md.")
    summary = {}
    for split in ("h0", "h1", "all"):
        cs = [c for c in cases if split == "all" or c["half"] == split]
        its = [x for x in items if split == "all" or x["half"] == split]
        summary[split] = emit(os.path.join(res_dir, "%s.%s.json" % (a.label, split)), "shadow_docket", split,
                              "mixed", "Shadow docket: lower decision vacated (GVR) / summarily reversed",
                              cs, its, base_note)
    for ck in ("federal", "state"):
        cs = [c for c in cases if c["court"] == ck]
        its = [x for x in items if court_kind(x["court_label"]) == ck or
               (ck == "federal" and court_kind(x["court_label"]) == "-" and False)]
        summary[ck] = emit(os.path.join(res_dir, "%s.%s.all.json" % (a.label, ck)), "shadow_docket_" + ck, "all",
                           ck, "Shadow docket (%s court below): vacated / summarily reversed" % ck, cs, its,
                           base_note + " Restricted to items whose court below is %s (link_rate over items with a "
                           "mapped court of that kind only)." % ck)
    with open(os.path.join(res_dir, "%s.cases.tsv" % a.label), "w", encoding="utf-8", newline="\n") as o:
        o.write("node\thalf\tclass\tsub\tcourt\tcourt_label\torder_date\tnode_date\tsc_dockets\tsc_in_corpus\t"
                "model_class\tmodel_status\tmodel_path\tmodel_actor\tmodel_witness\tmodel_class_at_order90\t"
                "agree\ttitle\n")
        for c in sorted(cases, key=lambda c: (c["class"], c["node"])):
            mc = c["m"]["mclass"]
            if c["class"] == "NEG":
                ag = mc == "NEG_HIST"
            elif c["class"] == "PART":
                ag = mc in ("NEG_HIST", "UNK_HIST")
            else:
                ag = mc not in ("NEG_HIST", "UNK_HIST")
            o.write("\t".join(str(x) for x in [
                c["node"], c["half"], c["class"], c["sub"], c["court"], c["court_label"], c["order_date"],
                c["node_date"], c["dockets"], c["sc_in_corpus"], mc, c["m"]["status"], c["m"]["path"],
                c["m"]["actor"], c["m"]["witness"], c["m_at_order"]["mclass"], int(ag), c["title"]]) + "\n")
    for k, (m, ex) in summary.items():
        print(a.label, k, " ".join("%s=%d/%d" % (n, v["k"], v["n"]) for n, v in m.items()),
              "| lenient %d/%d at_order %d/%d sc_in %d/%d sc_out %d/%d" % (
                  ex["recall_lenient"]["k"], ex["recall_lenient"]["n"], ex["recall_at_order_plus_90d"]["k"],
                  ex["recall_at_order_plus_90d"]["n"], ex["recall_sc_order_in_corpus"]["k"],
                  ex["recall_sc_order_in_corpus"]["n"], ex["recall_sc_order_not_in_corpus"]["k"],
                  ex["recall_sc_order_not_in_corpus"]["n"]))


if __name__ == "__main__":
    main()
