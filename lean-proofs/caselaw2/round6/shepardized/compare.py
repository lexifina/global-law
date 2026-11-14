#!/usr/bin/env python3
"""Compare the Lean model's decision status with the Shepardized Courts of Appeals Database.

Usage (standard library only; run isolated):
  python -I compare.py [--out OUT_DIR] [--data DATA_DIR] [--asof YYYYMMDD] [--tag NAME]

  --out   model output directory holding status.tsv and certs.tsv   (default ../../out)
  --data  data directory holding history.tsv                        (default ../../data)
  --asof  the date the model status is read at                      (default 20101119)
  --tag   results are written to results/<tag>/                     (default asof<date>, with _dev / _sealed)
  --results DIR   write the results to DIR instead of results/<tag>/
  --split dev|sealed|all   score only the cases of that half of round6/history/split (default all)

Needs work/shepardized.tsv (convert.py) and results/links.tsv (link.py). The mapping is MAPPING.md; the functions
shep_class() and model_class() below are that mapping and nothing else.

Round 6 (same-case history) additions; the mapping and the tables of the first run are unchanged, and the default
(--split all) writes a tables.tsv byte-identical to compare.pre_round6_history.py:
  * --split dev      tables.tsv, headline.tsv and the per-case file cases_dev.tsv for the dev half.
  * --split sealed   refuses unless round6/history/FREEZE.md exists (and every "<sha1>  <path>" line in it still
                     matches); writes aggregate tables only (no per-case file, no per-case line); appends one line
                     to round6/history/SEALED_LOG.md.
  * headline.tsv     every headline figure twice: raw, and with the documented database errors listed in
                     round6/history/shep_errors.tsv (casenum, reason, evidence) set aside, i.e. left out of the
                     numerator and the denominator. With a split the same section is also appended to tables.tsv.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = os.path.join(HERE, "..", "..", "..", "graph")
ROOT = os.path.join(HERE, "..", "..")  # caselaw-lean-2
R6H = os.path.join(HERE, "..", "history")
SPLIT_DIR = os.path.join(R6H, "split")
FREEZE = os.path.join(R6H, "FREEZE.md")
SEALED_LOG = os.path.join(R6H, "SEALED_LOG.md")
SHEP_ERRORS = os.path.join(R6H, "shep_errors.tsv")


def split_half(cite_key):
    """The round-6 split rule (round6/history/split/SPLIT.md): 0 = dev, 1 = sealed."""
    return ("dev", "sealed")[int(hashlib.sha1(("r6split:" + cite_key).encode()).hexdigest(), 16) % 2]


def file_sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_freeze():
    """Sealed runs only. Exit unless FREEZE.md exists and each '<sha1>  <path>' line in it matches the file
    (path relative to caselaw-lean-2). -> number of hashes checked."""
    if not os.path.exists(FREEZE):
        sys.exit("refused: --split sealed needs round6/history/FREEZE.md (the lead writes it once the rules are "
                 "frozen). Nothing was read or written.")
    n = 0
    bad = []
    with open(FREEZE, encoding="utf-8") as f:
        for line in f:
            m = re.search(r"(?<![0-9a-f])([0-9a-f]{40})(?![0-9a-f])[\s*`|]+([^\s`|]+)", line)
            if not m:
                continue
            n += 1
            p = os.path.join(ROOT, m.group(2).replace("\\", "/"))
            if not os.path.isfile(p):
                bad.append("missing: " + m.group(2))
            elif file_sha1(p) != m.group(1):
                bad.append("changed: " + m.group(2))
    if bad:
        sys.exit("refused: FREEZE.md hashes do not match\n  " + "\n  ".join(bad))
    return n


def read_errors():
    """round6/history/shep_errors.tsv -> set of casenums (documented database errors)."""
    if not os.path.exists(SHEP_ERRORS):
        return set()
    return {r["casenum"].strip() for r in rows(SHEP_ERRORS) if (r.get("casenum") or "").strip()}


def headline(L):
    """Headline figures of a list of linked case records -> ordered list of (group, value, k, n)."""
    S = [c for c in L if c["agree"] != ""]
    NEG = [c for c in L if c["sclass"] == "NEG"]
    PART = [c for c in L if c["sclass"] == "PART"]
    MOD = [c for c in L if c["sclass"] == "MOD"]
    CL = [c for c in L if c["sclass"] == "CLEAN"]
    MN = [c for c in L if c["mclass"] == "NEG_HIST"]
    MNs = [c for c in MN if c["sclass"] != "AMBIG"]
    H = [
        ("agreement", "overall, scored classes (NEG, PART, MOD, CLEAN)", sum(c["agree"] for c in S), len(S)),
        ("(a) recall", "NEG: model NEG_HIST (strict)", sum(c["mclass"] == "NEG_HIST" for c in NEG), len(NEG)),
        ("(a) recall", "NEG: model NEG_HIST or UNK_HIST (lenient)",
         sum(c["mclass"] in ("NEG_HIST", "UNK_HIST") for c in NEG), len(NEG)),
        ("(a) recall", "PART: model NEG_HIST or UNK_HIST",
         sum(c["mclass"] in ("NEG_HIST", "UNK_HIST") for c in PART), len(PART)),
        ("(a) recall", "NEG and PART together: model as expected",
         sum(c["agree"] for c in NEG) + sum(c["agree"] for c in PART), len(NEG) + len(PART)),
        ("(b) precision", "of model NEG_HIST: Shepardized NEG (strict; AMBIG left out)",
         sum(c["sclass"] == "NEG" for c in MNs), len(MNs)),
        ("(b) precision", "of model NEG_HIST: Shepardized NEG or PART (lenient; AMBIG left out)",
         sum(c["sclass"] in ("NEG", "PART") for c in MNs), len(MNs)),
        ("(c) clean", "CLEAN: model shows no same-case negative", sum(c["mcol"] == "CLEAN" for c in CL), len(CL)),
        ("(c) clean", "MOD: model CLEAN or UNK_HIST", sum(c["agree"] for c in MOD), len(MOD)),
    ]
    return H


def by_subclass(L):
    """Model as expected by Shepardized sub-class (for NEG: recall, strict) -> {(class, sub): (k, n)}."""
    d = {}
    for c in L:
        if c["agree"] == "":
            continue
        k, n = d.get((c["sclass"], c["ssub"]), (0, 0))
        d[(c["sclass"], c["ssub"])] = (k + c["agree"], n + 1)
    return d


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(k, n):
    if n == 0:
        return "%d/%d\t-\t-\t-" % (k, n)
    lo, hi = wilson(k, n)
    return "%d/%d\t%.1f%%\t%.1f%%\t%.1f%%" % (k, n, 100 * k / n, 100 * lo, 100 * hi)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


# ---------------------------------------------------------------- Shepardized side (MAPPING.md)
def shep_class(r):
    """-> (class, subclass)."""
    ap = r["appeal"]
    if "1" not in ap:
        return ("CLEAN", "none" if ap == "0" else "related_only")
    cr, eb, sa, sr = r["coarehear"], r["coaenbanc"], r["scappeal"], r["scresult"]
    if cr == "" and eb == "" and sa == "" and sr == "":
        return ("AMBIG", "uncoded")
    neg = []
    if sr in ("2", "3"):
        neg.append("sc_reversed")
    if sr in ("4", "7"):
        neg.append("sc_vacated")
    if cr in ("6", "3"):
        neg.append("panel_withdrawn")
    if eb == "3":
        neg.append("enbanc_different")
    if neg:
        return ("NEG", "+".join(neg))
    if sr in ("5", "6"):
        return ("PART", "sc_part")
    amb = []
    if eb in ("2", "4", "5"):
        amb.append("enbanc_granted")
    if cr in ("2", "7"):
        amb.append("rehearing_granted")
    if sa in ("3", "5") and sr in ("99", ""):
        amb.append("sc_granted_no_result")
    if sr in ("0", "9"):
        amb.append("sc_other_result")
    if sa == "6":
        amb.append("sc_other")
    if amb:
        return ("AMBIG", "+".join(amb))
    if cr in ("4", "5"):
        return ("MOD", "modified")
    if sr == "1":
        return ("CLEAN", "sc_affirmed")
    if sa in ("1", "2", "12", "4") or sr == "8":
        return ("CLEAN", "cert_denied")
    if cr == "1" or eb == "1":
        return ("CLEAN", "rehearing_denied")
    return ("CLEAN", "other_history")


EXPECT = {  # scored classes -> accepted collapsed model classes
    "NEG": {"NEG_HIST"},
    "PART": {"NEG_HIST", "UNK_HIST"},
    "MOD": {"CLEAN", "UNK_HIST"},
    "CLEAN": {"CLEAN"},
}
KIND_OK = {
    "sc_reversed": {"neg:reversed"},
    "sc_vacated": {"neg:vacated"},
    "panel_withdrawn": {"neg:withdrawn", "neg:vacated", "neg:reversed"},
    "enbanc_different": {"neg:vacated", "neg:withdrawn", "neg:reversed"},
}


# ---------------------------------------------------------------- model side (MAPPING.md)
def model_class(status, path):
    if status.startswith("neg:"):
        return "NEG_HIST" if path == "history" else "NEG_OTHER"
    if status.startswith("unknown:"):
        return "UNK_HIST" if path == "history" else "UNK_OTHER"
    return "GOOD"


def collapse(mc):
    return "CLEAN" if mc in ("GOOD", "NEG_OTHER", "UNK_OTHER") else mc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "out"))
    ap.add_argument("--data", default=os.path.join(HERE, "..", "..", "data"))
    ap.add_argument("--asof", type=int, default=20101119)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--results", default=None, help="output folder (default results/<tag>/)")
    ap.add_argument("--split", choices=("dev", "sealed", "all"), default="all")
    a = ap.parse_args()
    sealed = a.split == "sealed"
    n_freeze = check_freeze() if sealed else 0  # before anything is read
    tag = a.tag or ("asof%d" % a.asof + ("" if a.split == "all" else "_" + a.split))
    res = a.results or os.path.join(HERE, "results", tag)
    os.makedirs(res, exist_ok=True)

    links = {r["casenum"]: r for r in rows(os.path.join(HERE, "results", "links.tsv"))}
    shep = list(rows(os.path.join(HERE, "work", "shepardized.tsv")))
    n_shep_all = len(shep)
    if a.split != "all":
        sp = os.path.join(SPLIT_DIR, a.split + ".tsv")
        if not os.path.exists(sp):
            sys.exit("no %s: run round6/history/split/make_split.py first" % sp)
        keep = {r["casenum"] for r in rows(sp)}
        rule = {cn for cn, l in links.items() if split_half(l["cite_key"]) == a.split}
        if keep != rule:
            sys.exit("refused: %s does not agree with the split rule (%d cases in the file, %d by the rule); "
                     "re-run make_split.py" % (sp, len(keep), len(rule)))
        shep = [r for r in shep if r["casenum"] in keep]
        links = {cn: l for cn, l in links.items() if cn in keep}
    elif os.path.exists(os.path.join(SPLIT_DIR, "sealed.tsv")) and not os.path.exists(FREEZE):
        sys.stderr.write("note: --split all scores the sealed half too and writes its rows to cases.tsv; before "
                         "FREEZE.md, read only the aggregate tables of this run (round6/history/DESIGN6.md 0.1)\n")
    node_of = {cn: l["node"] for cn, l in links.items() if l["link"].startswith("linked")}
    wanted = set(node_of.values())

    # decision-level status at the as-of date
    st = {}
    with open(os.path.join(a.out, "status.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] in wanted and p[1] == "-" and p[2] == "-" and int(p[3]) <= a.asof <= int(p[4]):
                st[p[0]] = p
    # admitted same-case history rows (secondary check, and for the disagreement reading)
    okh = set()
    with open(os.path.join(a.out, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] == "history":
                if p[2] == "ok":
                    okh.add(p[1])
    hist = collections.defaultdict(list)
    with open(os.path.join(a.data, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] in wanted:
                hist[p[1]].append((p[0], p[2], p[3], p[4], p[5], "ok" if p[0] in okh else "rejected"))

    # U.S. Reports citations named by Shepardized -> corpus node (for the actor check)
    uskeys = {}
    for r in shep:
        for v in ("us1", "us2"):
            m = re.match(r"^0*(\d+)/0*(\d+)$", r[v])
            if m:
                uskeys["%s us %s" % (m.group(1), m.group(2))] = None
    ci = os.path.join(GRAPH, "cite_index.tsv")
    if os.path.exists(ci) and uskeys:
        with open(ci, encoding="utf-8") as f:
            for line in f:
                if " us " in line:
                    k, _, n = line.rstrip("\n").partition("\t")
                    if k in uskeys:
                        uskeys[k] = n

    cases = []
    for r in shep:
        cn = r["casenum"]
        l = links[cn]
        sc, sub = shep_class(r)
        node = node_of.get(cn, "")
        rec = dict(casenum=cn, cite=l["cite_key"], circuit=r["circuit"], date=l["songer_date"], link=l["link"],
                   node=node, name=l["node_name"], sclass=sc, ssub=sub, appeal=r["appeal"], coarehear=r["coarehear"],
                   coaenbanc=r["coaenbanc"], scappeal=r["scappeal"], scresult=r["scresult"], appaftre1=r["appaftre1"],
                   us1=r["us1"], us2=r["us2"], method=r["method"])
        if node:
            p = st.get(node)
            status, path, wit, actor = (p[5], p[10], p[8], p[9]) if p else ("good", "-", "-", "-")
            mc = model_class(status, path)
            rec.update(mstatus=status, mpath=path, mwitness=wit, mactor=actor, mclass=mc, mcol=collapse(mc))
            hs = [h for h in hist.get(node, []) if int(h[2] or 0) <= a.asof]
            rec["hist_rows"] = ";".join("%s:%s:%s:%s:%s" % (h[3], h[1], h[2], h[4], h[5]) for h in hs)
            rec["hidden_hist_neg"] = int(mc in ("NEG_OTHER", "UNK_OTHER") and any(
                h[3] in ("reversed", "vacated", "withdrawn") and h[5] == "ok" for h in hs))
            if sc in EXPECT:
                rec["agree"] = int(rec["mcol"] in EXPECT[sc])
            else:
                rec["agree"] = ""
        cases.append(rec)

    cols = ["casenum", "cite", "circuit", "date", "link", "node", "name", "sclass", "ssub", "appeal", "coarehear",
            "coaenbanc", "scappeal", "scresult", "appaftre1", "us1", "us2", "method", "mstatus", "mpath", "mwitness",
            "mactor", "mclass", "mcol", "agree", "hidden_hist_neg", "hist_rows"]
    if a.split == "dev":
        # dev per-case file: the same columns plus the U.S. Reports citation named by Shepardized as a reader key
        # and the corpus node it resolves to
        for c in cases:
            for v in ("us1", "us2"):
                m = re.match(r"^0*(\d+)/0*(\d+)$", c[v])
                k = "%s us %s" % (m.group(1), m.group(2)) if m else ""
                c[v + "_key"] = k
                c[v + "_node"] = (uskeys.get(k) or "") if k else ""
        cols = cols + ["us1_key", "us1_node", "us2_key", "us2_node"]
    if not sealed:  # a sealed run writes no per-case file
        with open(os.path.join(res, "cases_dev.tsv" if a.split == "dev" else "cases.tsv"), "w", encoding="utf-8",
                  newline="\n") as o:
            o.write("\t".join(cols) + "\n")
            for c in cases:
                o.write("\t".join(str(c.get(k, "")) for k in cols) + "\n")

    L = [c for c in cases if c["node"]]
    out = []
    w = out.append
    w("# as-of %d; model out dir %s" % (a.asof, os.path.abspath(a.out)))
    if a.split != "all":
        w("# split %s: %d of the %d Shepardized cases (round6/history/split/SPLIT.md)" %
          (a.split, len(cases), n_shep_all))
    w("cases\t%d\tlinked\t%d" % (len(cases), len(L)))

    # 1 confusion table
    MC = ["NEG_HIST", "UNK_HIST", "NEG_OTHER", "UNK_OTHER", "GOOD"]
    SC = ["NEG", "PART", "AMBIG", "MOD", "CLEAN"]
    w("\n## confusion: Shepardized class (rows) x model class (columns), linked cases")
    w("class\t" + "\t".join(MC) + "\ttotal")
    conf = collections.Counter((c["sclass"], c["mclass"]) for c in L)
    for s in SC:
        w(s + "\t" + "\t".join(str(conf[(s, m)]) for m in MC) + "\t%d" % sum(conf[(s, m)] for m in MC))
    w("total\t" + "\t".join(str(sum(conf[(s, m)] for s in SC)) for m in MC) + "\t%d" % len(L))
    w("\n## confusion by Shepardized sub-class")
    w("class\tsubclass\t" + "\t".join(MC) + "\ttotal")
    conf2 = collections.Counter((c["sclass"], c["ssub"], c["mclass"]) for c in L)
    for s, sub in sorted({(c["sclass"], c["ssub"]) for c in L}, key=lambda x: (SC.index(x[0]), x[1])):
        w("%s\t%s\t" % (s, sub) + "\t".join(str(conf2[(s, sub, m)]) for m in MC) +
          "\t%d" % sum(conf2[(s, sub, m)] for m in MC))

    # 2 agreement
    S = [c for c in L if c["agree"] != ""]
    w("\n## agreement (scored classes NEG, PART, MOD, CLEAN; AMBIG excluded: %d cases)" % (len(L) - len(S)))
    w("group\tvalue\tagree/n\tshare\tlo95\thi95")
    w("overall\tall\t" + pct(sum(c["agree"] for c in S), len(S)))
    for s in ("NEG", "PART", "MOD", "CLEAN"):
        g = [c for c in S if c["sclass"] == s]
        w("class\t%s\t" % s + pct(sum(c["agree"] for c in g), len(g)))
    for s, sub in sorted({(c["sclass"], c["ssub"]) for c in S}):
        g = [c for c in S if (c["sclass"], c["ssub"]) == (s, sub)]
        w("subclass\t%s/%s\t" % (s, sub) + pct(sum(c["agree"] for c in g), len(g)))
    for dec in sorted({c["date"][:3] for c in S}):
        g = [c for c in S if c["date"][:3] == dec]
        w("decade\t%s0s\t" % dec + pct(sum(c["agree"] for c in g), len(g)))
    for ci_ in sorted({c["circuit"] for c in S}, key=int):
        g = [c for c in S if c["circuit"] == ci_]
        w("circuit\t%s\t" % ("DC" if ci_ == "0" else ci_) + pct(sum(c["agree"] for c in g), len(g)))

    # 3 recall / precision / clean
    NEG = [c for c in L if c["sclass"] == "NEG"]
    w("\n## (a) recall on negative history: of Shepardized NEG, model NEG_HIST")
    w("group\tvalue\tk/n\tshare\tlo95\thi95")
    w("recall\tstrict (NEG_HIST)\t" + pct(sum(c["mclass"] == "NEG_HIST" for c in NEG), len(NEG)))
    w("recall\tlenient (NEG_HIST or UNK_HIST)\t" + pct(sum(c["mclass"] in ("NEG_HIST", "UNK_HIST") for c in NEG), len(NEG)))
    for sub in sorted({c["ssub"] for c in NEG}):
        g = [c for c in NEG if c["ssub"] == sub]
        w("recall by subclass\t%s\t" % sub + pct(sum(c["mclass"] == "NEG_HIST" for c in g), len(g)))
    for dec in sorted({c["date"][:3] for c in NEG}):
        g = [c for c in NEG if c["date"][:3] == dec]
        w("recall by decade\t%s0s\t" % dec + pct(sum(c["mclass"] == "NEG_HIST" for c in g), len(g)))
    for ci_ in sorted({c["circuit"] for c in NEG}, key=int):
        g = [c for c in NEG if c["circuit"] == ci_]
        w("recall by circuit\t%s\t" % ("DC" if ci_ == "0" else ci_) + pct(sum(c["mclass"] == "NEG_HIST" for c in g), len(g)))
    PARTc = [c for c in L if c["sclass"] == "PART"]
    w("recall\tPART: model NEG_HIST or UNK_HIST\t" + pct(sum(c["mclass"] in ("NEG_HIST", "UNK_HIST") for c in PARTc), len(PARTc)))

    MN = [c for c in L if c["mclass"] == "NEG_HIST"]
    MNs = [c for c in MN if c["sclass"] != "AMBIG"]
    w("\n## (b) precision: of model NEG_HIST (same-case negative), Shepardized agrees")
    w("group\tvalue\tk/n\tshare\tlo95\thi95")
    w("model NEG_HIST linked\tall\t%d" % len(MN))
    w("model NEG_HIST linked\tShepardized AMBIG (left out)\t%d" % (len(MN) - len(MNs)))
    w("precision\tstrict (Shepardized NEG)\t" + pct(sum(c["sclass"] == "NEG" for c in MNs), len(MNs)))
    w("precision\tlenient (Shepardized NEG or PART)\t" + pct(sum(c["sclass"] in ("NEG", "PART") for c in MNs), len(MNs)))
    w("precision\tAMBIG counted as agreeing\t" + pct(sum(c["sclass"] in ("NEG", "PART", "AMBIG") for c in MN), len(MN)))
    MU = [c for c in L if c["mclass"] == "UNK_HIST"]
    w("model UNK_HIST linked\tall\t%d" % len(MU))
    w("model UNK_HIST\tShepardized NEG or PART\t" + pct(sum(c["sclass"] in ("NEG", "PART") for c in MU), len(MU)))
    for s in SC:
        w("model NEG_HIST by Shepardized class\t%s\t%d" % (s, sum(c["sclass"] == s for c in MN)))
    for (s, sub), v in collections.Counter((c["sclass"], c["ssub"]) for c in MN).most_common():
        w("model NEG_HIST by Shepardized subclass\t%s/%s\t%d" % (s, sub, v))

    CL = [c for c in L if c["sclass"] == "CLEAN"]
    w("\n## (c) of Shepardized CLEAN, model shows no same-case negative")
    w("group\tvalue\tk/n\tshare\tlo95\thi95")
    w("clean\tmodel CLEAN (GOOD, NEG_OTHER, UNK_OTHER)\t" + pct(sum(c["mcol"] == "CLEAN" for c in CL), len(CL)))
    w("clean\tmodel GOOD only\t" + pct(sum(c["mclass"] == "GOOD" for c in CL), len(CL)))
    for sub in sorted({c["ssub"] for c in CL}):
        g = [c for c in CL if c["ssub"] == sub]
        w("clean by subclass\t%s\t" % sub + pct(sum(c["mcol"] == "CLEAN" for c in g), len(g)))

    # 4 kind and actor checks
    both = [c for c in NEG if c["mclass"] == "NEG_HIST"]
    w("\n## kind check: Shepardized NEG and model NEG_HIST (%d cases)" % len(both))
    w("group\tvalue\tk/n\tshare\tlo95\thi95")
    ok = 0
    kk = collections.Counter()
    for c in both:
        allowed = set()
        for s in c["ssub"].split("+"):
            allowed |= KIND_OK[s]
        good = c["mstatus"] in allowed
        ok += good
        kk[(c["ssub"], c["mstatus"])] += 1
    w("kind\tmodel kind is an expected kind\t" + pct(ok, len(both)))
    for (s, m), v in sorted(kk.items(), key=lambda x: -x[1]):
        w("kind pair\t%s -> %s\t%d" % (s, m, v))

    w("\n## actor/date check: Shepardized names a U.S. Reports decision and the model names an actor")
    w("(the Shepardized file has no event dates; the check is whether the model's actor is the named Supreme Court decision)")
    w("group\tvalue\tk/n\tshare\tlo95\thi95")
    # the citation column of every model actor (several decisions can share a U.S. Reports page, so the actor is
    # compared by its own citations, not through the one-node-per-citation index)
    actors = {c["mactor"] for c in L if c["mclass"] in ("NEG_HIST", "UNK_HIST") and c["mactor"] not in ("-", "")}
    actor_cites = {}
    npath = os.path.join(GRAPH, "nodes.tsv")
    if actors and os.path.exists(npath):
        with open(npath, encoding="utf-8", newline="") as f:
            for line in f:
                i = line.find("\t")
                if line[:i] in actors:
                    p = line.rstrip("\r\n").split("\t")
                    actor_cites[p[0]] = {re.sub(r"\s+", " ", x.replace("U.S.", "us").replace("U. S.", "us")).strip().lower()
                                         for x in p[5].split("|")}
    n_named = n_res = n_cmp = n_same = 0
    diff = []
    for c in L:
        ks = []
        for v in ("us1", "us2"):
            m = re.match(r"^0*(\d+)/0*(\d+)$", c[v])
            if m:
                ks.append("%s us %s" % (m.group(1), m.group(2)))
        if not ks:
            continue
        n_named += 1
        ns = {uskeys.get(k) for k in ks} - {None}
        if not ns:
            continue
        n_res += 1
        if c["mclass"] in ("NEG_HIST", "UNK_HIST") and c["mactor"] not in ("-", ""):
            n_cmp += 1
            if c["mactor"] in ns or (set(ks) & actor_cites.get(c["mactor"], set())):
                n_same += 1
            else:
                diff.append(c)
    w("named\tlinked cases where Shepardized gives a U.S. cite\t%d" % n_named)
    w("named\t... and that cite resolves to a corpus node\t%d" % n_res)
    w("actor\tmodel history actor is the named decision\t" + pct(n_same, n_cmp))
    if sealed:  # no per-case line in a sealed run
        w("actor differs\tcases (not listed: sealed)\t%d" % len(diff))
    else:
        for c in diff:
            w("actor differs\t%s\tcasenum %s node %s model actor %s us1 %s us2 %s" %
              (c["cite"], c["casenum"], c["node"], c["mactor"], c["us1"], c["us2"]))

    w("\n## secondary: same-case event hidden behind a non-history status")
    w("hidden\tNEG_OTHER/UNK_OTHER with an admitted reversed/vacated/withdrawn history row\t%d" %
      sum(c["hidden_hist_neg"] for c in L))
    for s in SC:
        w("hidden by Shepardized class\t%s\t%d" % (s, sum(c["hidden_hist_neg"] for c in L if c["sclass"] == s)))

    # round 6: every headline figure raw and with the documented database errors set aside
    errs = read_errors()
    Lx = [c for c in L if c["casenum"] not in errs]
    hd = []
    h = hd.append
    h("\n## headline figures: raw, and with documented Shepardized database errors set aside")
    h("(errors: round6/history/shep_errors.tsv, %d listed; %d of them among the %d cases scored here, %d linked; a "
      "case set aside is left out of numerator and denominator)" %
      (len(errs), sum(c["casenum"] in errs for c in cases), len(cases), len(L) - len(Lx)))
    h("group\tvalue\traw k/n\traw share\traw lo95\traw hi95\tset-aside k/n\tset-aside share\tset-aside lo95\t"
      "set-aside hi95")
    Hr, Hx = headline(L), headline(Lx)
    for (g, v, k, n), (_, _, kx, nx) in zip(Hr, Hx):
        h("%s\t%s\t%s\t%s" % (g, v, pct(k, n), pct(kx, nx)))
    Br, Bx = by_subclass(L), by_subclass(Lx)
    for s, sub in sorted(Br, key=lambda x: (SC.index(x[0]), x[1])):
        k, n = Br[(s, sub)]
        kx, nx = Bx.get((s, sub), (0, 0))
        h("%s by subclass\t%s/%s\t%s\t%s" % ("recall" if s in ("NEG", "PART") else "as expected", s, sub,
                                              pct(k, n), pct(kx, nx)))
    h("model NEG_HIST linked\tall\t%d\t\t\t\t%d" % (sum(c["mclass"] == "NEG_HIST" for c in L),
                                                    sum(c["mclass"] == "NEG_HIST" for c in Lx)))
    h("model UNK_HIST linked\tall\t%d\t\t\t\t%d" % (sum(c["mclass"] == "UNK_HIST" for c in L),
                                                    sum(c["mclass"] == "UNK_HIST" for c in Lx)))

    with open(os.path.join(res, "tables.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\n".join(out if a.split == "all" else out + hd) + "\n")
    with open(os.path.join(res, "headline.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\n".join([out[0]] + ([out[1]] if a.split != "all" else []) + hd) + "\n")
    print("\n".join(out + hd))

    if sealed:
        log_sealed(SEALED_LOG, sys.argv[1:], a.out, a.data, res, Hr, Hx, n_freeze)


def log_sealed(log_path, argv, out_dir, data_dir, res, Hr, Hx, n_freeze):
    """Append one line for a sealed run: time, arguments, sha1 of the model files, headline numbers (raw, and in
    brackets with the documented database errors set aside)."""
    def kn(i):
        return "%d/%d (%d/%d)" % (Hr[i][2], Hr[i][3], Hx[i][2], Hx[i][3])

    def sha(p):
        return file_sha1(p) if os.path.isfile(p) else "absent"
    new = not os.path.exists(log_path)
    with open(log_path, "a", encoding="utf-8", newline="\n") as o:
        if new:
            o.write("# Sealed scoring log\n\nAppended by `round6/shepardized/compare.py --split sealed`, one line "
                    "per run. Figures are k/n raw, then in brackets with `shep_errors.tsv` set aside.\n\n")
        o.write("- %s | args: %s | status.tsv sha1 %s | certs.tsv sha1 %s | history.tsv sha1 %s | FREEZE.md sha1 %s, "
                "%d file hashes checked | results %s | recall NEG strict %s | recall NEG lenient %s | PART %s | "
                "precision strict %s | precision lenient %s | CLEAN %s | MOD %s | agreement %s\n" % (
                    datetime.datetime.now().astimezone().isoformat(timespec="seconds"), " ".join(argv),
                    sha(os.path.join(out_dir, "status.tsv")), sha(os.path.join(out_dir, "certs.tsv")),
                    sha(os.path.join(data_dir, "history.tsv")), sha(FREEZE), n_freeze, os.path.abspath(res),
                    kn(1), kn(2), kn(3), kn(5), kn(6), kn(7), kn(8), kn(0)))


if __name__ == "__main__":
    main()
