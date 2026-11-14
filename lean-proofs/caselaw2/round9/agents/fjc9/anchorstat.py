"""fjc9: for pairs whose F1 drop is anchor:head_no_line, measure the forms near the citation.

    python -X utf8 anchorstat.py work/f1why.tsv REASON_SUBSTR
"""
import collections, csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fjc_link as FL  # noqa: E402
from fjc_link import BO, L, diag, C  # noqa: E402

CUE = re.compile(r"\b(district\s+court|trial\s+court|court\s+below|lower\s+court)s?\b", re.I)
JUDGE = re.compile(r"\b(?:district|trial)\s+judge\b|\bJudge\s+[A-Z][a-z]+|\bthe\s+judge\b|\bthe\s+court\b|\bmagistrate\b", re.I)


def main():
    rows = [r for r in csv.reader(open(sys.argv[1], encoding="utf-8"), delimiter="\t") if sys.argv[2] in r[3]]
    sidx = diag.shard_index()
    by = collections.defaultdict(list)
    for r in rows:
        by[sidx[int(r[1])]].append((int(r[0]), int(r[1])))
    st = collections.Counter()
    for tag, items in by.items():
        want = {a for _, a in items}
        path = os.path.join(L.CACHE, tag + ".jsonl.gz")
        groups = {n: g for n, g in L.decisions(path) if n in want}
        texts = L.fetch_texts(sorted(want))
        for d, a in items:
            g = groups[a]
            T = L.norm(texts[a][1])
            z = g["z"]
            best = None
            for cw in g["cw"]:
                if cw["j"] != d:
                    continue
                c0 = cw["c"][0]
                s0, s1 = cw["s"]
                pb = FL.part_bounds(z, c0)
                p0 = pb[0] if pb else 0
                para0 = T.rfind("\n", 0, c0) + 1
                ms = list(CUE.finditer(T, p0, c0))
                dist = c0 - ms[-1].start() if ms else -1
                ncites = 0
                if ms:
                    for m in C.CITE_RX.finditer(T, ms[-1].end(), c0):
                        ncites += 1
                inpara = bool(ms) and ms[-1].start() >= para0
                jd = bool(JUDGE.search(T[max(p0, s0 - 600):s1]))
                fwd = bool(CUE.search(T[s1:s1 + 600]))
                rec = (dist, ncites, inpara, jd, fwd, cw["part"], c0 - para0)
                if best is None or (0 <= dist < (best[0] if best[0] >= 0 else 10 ** 9)):
                    best = rec
            if best is None:
                st["no_cw"] += 1
                continue
            dist, nc, inpara, jd, fwd, part, pos = best
            b = "none" if dist < 0 else ("<1500" if dist < 1500 else "<4000" if dist < 4000 else ">=4000")
            st["dist " + b] += 1
            st["inpara %s" % inpara] += 1
            st["cites_between %s" % ("0" if nc == 0 else "1-2" if nc <= 2 else "3+")] += 1
            st["judge_or_court_near %s" % jd] += 1
            st["cue_fwd600 %s" % fwd] += 1
            st["part " + part] += 1
    for k in sorted(st):
        print(st[k], k)


if __name__ == "__main__":
    main()
