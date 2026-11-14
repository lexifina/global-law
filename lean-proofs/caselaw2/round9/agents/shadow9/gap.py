"""shadow9: the data gap - h0 NEG orders whose Supreme Court order is not in the corpus (counts only; diagnosis,
reads the sanctioned h0 cases file). Writes work/gap_counts.txt.
    python -X utf8 round9/agents/shadow9/gap.py
"""
import collections, csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
rows = list(csv.DictReader(open(os.path.join(C2, "round8/results/v8e/bench/shadow_docket.h0.cases.tsv"),
                                encoding="utf-8"), delimiter="\t"))
neg = [r for r in rows if r["class"] == "NEG"]
gap = [r for r in neg if r["sc_in_corpus"] != "yes"]
out = ["h0 NEG nodes %d; order not in corpus %d (model NEG_HIST among them %d)" % (
    len(neg), len(gap), sum(r["model_class"] == "NEG_HIST" for r in gap))]


def dtype(r):
    d = r["sc_dockets"].replace(",", " ").split()
    t = set()
    for x in d:
        m = re.match(r"\d{2}-(\d+)$", x.strip())
        if not m:
            t.add("other")
        elif len(m.group(1)) >= 4 and int(m.group(1)) >= 5000:
            t.add("ifp")
        elif x.strip().upper().endswith("A"):
            t.add("application")
        else:
            t.add("paid")
    return "+".join(sorted(t))


def term(r):
    y, m = int(r["order_date"][:4]), int(r["order_date"][4:6])
    return y if m >= 10 else y - 1


for name, f in (("order year", lambda r: r["order_date"][:4]), ("term (Oct-Sep)", term),
                ("sub-class", lambda r: r["sub"]), ("court below system", lambda r: r["court"]),
                ("docket type (paid / in forma pauperis)", dtype),
                ("year x sub", lambda r: r["order_date"][:4] + " " + r["sub"]),
                ("court label (top 15)", lambda r: r["court_label"])):
    c = collections.Counter(f(r) for r in gap)
    out.append("")
    out.append("## " + name)
    items = sorted(c.items()) if "top" not in name else c.most_common(15)
    for k, v in items:
        out.append("%s\t%d" % (k, v))
txt = "\n".join(out) + "\n"
open(os.path.join(HERE, "work", "gap_counts.txt"), "w", encoding="utf-8", newline="\n").write(txt)
print(txt)
