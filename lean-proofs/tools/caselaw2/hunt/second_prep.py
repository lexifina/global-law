"""Second reads by Claude subagents after the blind audits of patterns 2 and 3.

    python second_prep.py p2   -> work/p2b_in.jsonl : citations of Federal Appendix decisions by the same circuit with a
                                  binding-language cue (the audit showed decisions2.pub marks many reporter-published
                                  opinions 'unpublished', so the first candidate set was mostly not unpublished at all)
    python second_prep.py p3   -> work/p3b_in.jsonl : the 409 first-read violations, with the judges line and every
                                  passage about the bench or circulation
"""
import csv, json, os, re, sys
from collections import Counter
import hcommon as C
import tasks as T
import claude_batches as B

BENCH = re.compile(r"en banc|in banc|in bank|full court|whole court|all (?:the )?(?:active )?(?:judges|justices|members)|"
                   r"circulated|entire court|court sitting|irons|rule 40\(e\)|mini[- ]en banc", re.I)
FAPPX = re.compile(r"F\. ?App")


def p2():
    rows = []
    for l in open(os.path.join(C.HWORK, "p2_passages.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["hits"] > 0 and r["binding_lang"]:
            rows.append(r)
    meta = C.nodes({r["cited"] for r in rows} | {r["citing"] for r in rows})
    keep = []
    for r in rows:
        md, mc = meta[r["cited"]], meta[r["citing"]]
        cites = [c for c in md["cite"].split("|") if c]
        if not cites or not all(FAPPX.search(c) for c in cites):
            continue
        r.update(hkey="unpub|%s|%s" % (r["citing"], r["cited"]), stratum="fappx", weight=1,
                 cited_name=md["name"], cited_cite=cites[0], cited_court_name=md["court_name"], cited_date=md["date"],
                 citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0], citing_court_name=mc["court_name"],
                 citing_date=mc["date"])
        keep.append(r)
    with open(os.path.join(C.HWORK, "p2b_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in keep:
            f.write(json.dumps(r) + "\n")
    C.log("binding-cue passages", len(rows), "citing a Federal Appendix decision", len(keep),
          Counter((r["unpub_lang"], r["force"]) for r in keep).most_common(8),
          Counter(r["citing_court_name"] for r in keep).most_common(8))


def p3():
    ins = {}
    for l in open(os.path.join(C.HWORK, "p3_in.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        ins[r["hkey"]] = r
    rows = list(csv.DictReader(open(os.path.join(C.HUNT, "data", "p3_panel.tsv"), encoding="utf-8"), delimiter="\t"))
    sel = [ins["panel|%s|%s" % (x["citing"], x["cited"])] for x in rows if x["violation_final"] == "1"]
    meta = C.nodes({r["citing"] for r in sel})
    texts = C.fetch(meta)
    with open(os.path.join(C.HWORK, "p3b_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in sel:
            t = texts.get(r["citing"], "")
            b = C.body(t)
            fm = "\n".join(l for l in C.front(t).splitlines() if l.split(":")[0] in ("judges", "court"))
            snips, last = [], -1000
            for m in BENCH.finditer(b):
                if m.start() - last < 500:
                    continue
                last = m.start()
                snips.append(b[max(0, m.start() - 250):m.end() + 350].replace("\n", " "))
                if len(snips) >= 4:
                    break
            r = B.trim(r, cut=1000)
            r["_text"] = (T.panel_user(dict(r, head=(r.get("head") or "")[:1500]))
                          + "\nJUDGES LINE: %s\nBENCH PASSAGES (every mention of en banc / full court / circulation):\n%s\n"
                          % (fm[:500], "\n- ".join([""] + snips) if snips else "(none found)"))
            f.write(json.dumps(r) + "\n")
    C.log("p3 second read rows", len(sel))


if __name__ == "__main__":
    {"p2": p2, "p3": p3}[sys.argv[1]]()
