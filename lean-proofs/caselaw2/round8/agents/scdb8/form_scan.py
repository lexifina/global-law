"""scdb8: corpus count (no key) of judgment-line forms that round 6/7's disposition reader does not take, in the opinion
of the Court of Supreme Court decisions where round 7 found no disposition (no_disposition / disp_not_strong).

    python -X utf8 form_scan.py [--procs 10]   -> work/form_scan.json, work/form_scan_ex.tsv
"""
import collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "below_sc"))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import link  # noqa: E402

L, C = link.L, link.C
NL = chr(10)
WORK = os.path.join(HERE, "work")
FORMS = {
    "it_pron": re.compile(r"\b(?:It|it|They|they|Each|each|Both|both)\s+(?:is|are|must\s+be|will\s+be)[\s,]+(?:(?:therefore|accordingly|hereby|thus)[\s,]+)?(?:reversed|vacated)\b"),
    "ocr_rev": re.compile(r"\b(?:R|r)e[vyu][ec][rn]s[ec][dl]\b|\b[Rr]eveised\b|\b[Rr]ever[s5]ed\b"),
    "gvr_line": re.compile(r"\b[Cc]ertiorari\s+granted[,;]?\s+(?:the\s+)?judgments?\s+vacated\b"),
    "reinstated": re.compile(r"\b(?:should|must|is|are)\s+be\s+reinstated\b|\bis\s+reinstated\b"),
    "set_aside": re.compile(r"\b(?:judgments?|decrees?|orders?)\b[^.;]{0,120}\b(?:is|are|be|must\s+be)\s+set\s+aside\b"),
    "reversed_word": re.compile(r"\b(?:reversed|vacated)\b", re.I),
}
OK = {}


def work(path):
    link.init()
    idx = OK["idx"] if "idx" in OK else None
    if idx is None:
        OK["idx"] = idx = json.load(open(os.path.join(WORK, "nodisp_ids.json")))
        OK["idx"] = idx = set(idx)
    st = collections.Counter()
    ex = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["n"] not in idx:
                continue
            text = r["text"]
            body0 = 0
            if text.startswith("---"):
                e = text.find(NL + "---", 3)
                if e >= 0:
                    nl = text.find(NL, e + 4)
                    body0 = nl + 1 if nl >= 0 else len(text)
            hw = C.hard_wrapped(text, body0)
            view = C.unwrap_view(text, body0) if hw else text
            pm, _ = (C.part_map2(text) if hw else C.part_map(text))
            ops = [(a, b) for a, b, p, _s in pm if p in ("majority", "perCuriam", "plurality", "majority~")]
            if not ops:
                continue
            st["decisions"] += 1
            a, b = ops[-1]
            seg = view[a:b]
            for k, rx in FORMS.items():
                ms = list(rx.finditer(seg))
                if ms:
                    st[k] += 1
                    m = ms[-1]
                    if len(ex) < 4000:
                        ex.append((r["n"], r["date"], k, L.norm(seg[max(0, m.start() - 160):m.end() + 60])))
    return st, ex


def main():
    procs = 10
    if "--procs" in sys.argv:
        procs = int(sys.argv[sys.argv.index("--procs") + 1])
    idx = json.load(open(os.path.join(WORK, "diag7_index.json"), encoding="utf-8"))
    ids = [int(k) for k, d in idx.items() if d.get("reason") in ("no_disposition", "disp_not_strong")]
    json.dump(ids, open(os.path.join(WORK, "nodisp_ids.json"), "w"))
    st = collections.Counter()
    exs = []
    for s, ex in L.pmap(work, link.shard_files(), procs=procs):
        st.update(s)
        exs.extend(ex)
    json.dump(st, open(os.path.join(WORK, "form_scan.json"), "w"), indent=1)
    with open(os.path.join(WORK, "form_scan_ex.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for e in exs:
            f.write("%d\t%d\t%s\t%s\n" % e)
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
