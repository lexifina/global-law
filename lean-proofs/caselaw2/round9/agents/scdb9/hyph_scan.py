"""scdb9: how many Supreme Court opinions without a judgment reading (diag reason no_disposition / disp_not_strong)
print a judgment word split by a line-break hyphen ("re- versed", "va- cated", "af- firmed", "judg- ment")
in the last 3,000 characters of the text? (form count only; no rows)

    python -X utf8 hyph_scan.py [diag]  -> prints counts + 15 examples
"""
import collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

SPLIT = re.compile(r"\b(re|rev|af|aff|affirm|va|vac|vacat|judg|judgm|de|dis|dismiss|reman|re-\s*man)-[ \t]*\n?[ \t]*"
                   r"(versed|ersed|firmed|irmed|ed|cated|ated|ment|cree|missed|ded|manded)\b", re.I)
WORDS = {"reversed", "affirmed", "vacated", "judgment", "decree", "dismissed", "remanded"}


def main():
    dpath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "work", "diag9.jsonl.gz")
    ns = []
    with gzip.open(dpath, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("reason") in ("no_disposition", "disp_not_strong") and d.get("type", "opinion") == "opinion":
                ns.append(d["n"])
    st = collections.Counter()
    ex = []
    for i in range(0, len(ns), 2000):
        texts = L.fetch_texts(ns[i:i + 2000])
        for n, (_sha, t) in texts.items():
            tail = t[-6000:]
            hits = [m for m in SPLIT.finditer(tail) if (m.group(1) + m.group(2)).lower().replace("-", "") in WORDS]
            if hits:
                st["with_split"] += 1
                if any(m.group(2).lower() in ("versed", "ersed", "cated", "ated", "firmed", "irmed") for m in hits):
                    st["with_split_verb"] += 1
                    if len(ex) < 15:
                        m = hits[0]
                        ex.append((n, L.norm(tail[max(0, m.start() - 120):m.end() + 60])))
        st["scanned"] += len(texts)
    print(dict(st))
    for e in ex:
        print(e)


if __name__ == "__main__":
    main()
