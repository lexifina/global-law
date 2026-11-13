"""Pattern 3: a panel overrules (or recedes from) its own court's precedent without en banc, in a court with a strong
horizontal rule. Source: the runner's panelDepartsWithoutEnBanc findings (Spec.panelDepartsWithoutEnBanc: an admitted
status-changing treatment whose power check failed for want of an en banc bench).

    python p3_panel.py prep    -> work/p3_in.jsonl (treatment quote, opinion head and tail, passages)
    python llm_run.py panel work/p3_in.jsonl work/p3_out.jsonl
    python p3_panel.py score   -> data/p3_panel.tsv + summary on stderr
"""
import json, os, re, sys
from collections import Counter, defaultdict
import hcommon as C
import passages as P


def prep():
    pairs = {}
    for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")):
        if r[0] == "panelDepartsWithoutEnBanc":
            pairs[(int(r[1]), int(r[2]))] = (r[4], r[5], r[6])
    quotes = {}
    for p in C.read_tsv(os.path.join(C.DATA, "treatments.tsv"), header=False):
        k = (int(p[1]), int(p[2]))
        if k in pairs:
            quotes.setdefault(k, []).append((p[4], p[5], p[11]))
    items = [dict(citing=a, cited=b, actor=None, detail=v[0], firm=v[1], path=v[2]) for (a, b), v in pairs.items()]
    tmp = os.path.join(C.HWORK, "p3_passages.jsonl")
    P.run(items, tmp, workers=8)
    rows = [json.loads(l) for l in open(tmp, encoding="utf-8")]
    meta = C.nodes({r["citing"] for r in rows} | {r["cited"] for r in rows})
    texts = C.fetch({r["citing"]: meta[r["citing"]] for r in rows})
    with open(os.path.join(C.HWORK, "p3_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            mc, md = meta[r["citing"]], meta[r["cited"]]
            t = texts.get(r["citing"], "")
            fm = "\n".join(l for l in C.front(t).splitlines() if l.split(":")[0] in ("judges", "court", "docket"))
            b = C.body(t)
            q = quotes.get((r["citing"], r["cited"]), [("-", "-", "-")])
            r.update(hkey="panel|%s|%s" % (r["citing"], r["cited"]), court_name=mc["court_name"],
                     court2=mc["court2"], unit=mc["unit"], bench=mc["bench"], cited_unit=md["unit"],
                     cited_name=md["name"], cited_cite=md["cite"].split("|")[0], cited_date=md["date"],
                     citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0], citing_date=mc["date"],
                     quote=" / ".join("%s(%s): %s" % x for x in q)[:700],
                     head=(fm + "\n" + b[:900] + "\n...\n[END OF OPINION] " + b[-500:]))
            f.write(json.dumps(r) + "\n")
    C.log("panel rows", len(rows))


CONCUR = re.compile(r"((?:[A-Z][A-Za-z'\-]+(?:, (?:C\. ?J|P\. ?J|Sr\. ?J|J)\.?)?,? (?:and )?){2,})(?:JJ?\.?,? )?(?:all )?concur", re.S)
# courts that hear every case with all their judges (Ala. Code 12-3-1 and 12-3-15 history: five-judge courts)
WHOLE = {"Alabama Court of Criminal Appeals", "Alabama Court of Civil Appeals", "Alabama Court of Appeals"}
# intermediate courts with no en banc procedure at all: a strong within-unit rule cannot be met by any bench
NO_EN_BANC = {"New York Supreme Court, Appellate Division"}


STOPW = {"Judgment", "Judgments", "Chief", "Presiding", "Justice", "Justices", "Judges", "Judge", "All", "The",
         "Affirmed", "Reversed", "Remanded", "Vacated", "And", "Specially", "Concur", "Concurs", "In", "Part",
         "Dissent", "Dissents", "Senior", "Appeal", "Dismissed", "Order", "Court", "We", "It", "Is", "So", "Ordered"}


def judges_concurring(text):
    """Most surnames named in one 'X, Y and Z, JJ., concur' line (the court's bench for that decision)."""
    best = 0
    for m in re.finditer(r"concur", text):
        seg = text[max(0, m.start() - 220):m.start()]
        seg = re.split(r"(?:affirmed|reversed|remanded|dismissed|vacated|granted|denied)\.\s", seg, flags=re.I)[-1]
        names = {n for n in re.findall(r"([A-Z][a-z][A-Za-z'\-]+)", seg) if n not in STOPW}
        best = max(best, len(names))
    return best


def score():
    ins = {json.loads(l)["hkey"]: json.loads(l) for l in open(os.path.join(C.HWORK, "p3_in.jsonl"), encoding="utf-8")}
    outs = [json.loads(l) for l in open(os.path.join(C.HWORK, "p3_out.jsonl"), encoding="utf-8")]
    rows = []
    for o in outs:
        a, r = o["ans"], ins[o["key"]]
        if "error" in a:
            continue
        nj = judges_concurring(r["head"])
        whole = int(nj >= 5 or r["court_name"] in WHOLE)
        noeb = int(r["court_name"] in NO_EN_BANC)
        final = int(a["violation"] and not whole and not noeb)
        rows.append([r["citing"], r["citing_name"][:70], r["citing_cite"], r["citing_date"], r["court_name"],
                     r["cited"], r["cited_name"][:70], r["cited_cite"], r["cited_date"], r["detail"], r["path"],
                     int(a["departs"]), a["bench"], a["justification"], int(a["violation"]), a["reason"],
                     r["quote"][:300], nj, whole, noeb, final])
    rows.sort(key=lambda x: (-x[20], -x[14], x[4], -x[3]))
    C.write_tsv(os.path.join(C.HUNT, "data", "p3_panel.tsv"), rows,
                ["citing", "citing_name", "citing_cite", "citing_date", "court", "cited", "cited_name", "cited_cite",
                 "cited_date", "detail", "path", "departs", "bench_llm", "justification", "violation", "reason",
                 "quote", "judges_concurring", "whole_court", "no_en_banc_mechanism", "violation_final"])
    c = Counter((r[14], r[12], r[13]) for r in rows)
    C.log("classified", len(rows), "llm violations", sum(r[14] for r in rows), "whole-court", sum(r[14] and r[18] for r in rows),
          "no en banc mechanism", sum(r[14] and r[19] for r in rows), "final", sum(r[20] for r in rows))
    for k, v in c.most_common(20):
        C.log(k, v)
    byc = Counter(r[4] for r in rows if r[20])
    C.log("violations by court", byc.most_common(15))


if __name__ == "__main__":
    {"prep": prep, "score": score}[sys.argv[1]]()
