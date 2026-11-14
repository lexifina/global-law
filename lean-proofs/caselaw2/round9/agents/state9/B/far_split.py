"""state9 part B: rows_raw.jsonl (far_rows.py) -> rows_far.jsonl (claim joinedFar) / rows_other.jsonl + stats.

    python -X utf8 far_split.py [--max 1200]

A joined row with gap (start - j_end) > 300 gets claim `joinedFar` when gap <= --max and the gap text holds no
citation that the index (round-7 resolver: staged index first, else the graph index uniquely) maps to a node other
than the row's target; else it is counted and left out (`gap_over_max`, `other_key`). Paragraph breaks are counted
only (`xpara`), not a condition (see NOTES.md). Rows with gap <= 300 or one-sentence rows go to rows_other.jsonl
(certifiable without a claim). No answer key is read.
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round7", "agents", "antecedent"))
import r6lib as L  # noqa: E402
import antecands as AC  # noqa: E402
C = L.reader_common()
NL = chr(10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=1200)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows_raw.jsonl"), encoding="utf-8")]
    texts = {}
    nodes = sorted({r["by"] for r in rows})
    texts.update(L.fetch_texts(nodes))
    gaps = {}
    keys = set()
    for r in rows:
        if not r["joined"]:
            continue
        t = texts[r["by"]][1]
        j1 = r["joined"][0]["span"][1]
        m0 = r["main"][0]
        g = t[j1:m0]
        cs = []
        for cm in C.CITE_RX.finditer(g):
            k = C.cite_key(cm)
            if k:
                cs.append(k)
                keys.add(k)
        gaps[id(r)] = (m0 - j1, int(NL in g), cs)
    res = AC.resolver(keys)
    st = collections.Counter()
    far, other = [], []
    for r in rows:
        if not r["joined"]:
            other.append(r)
            st["onesentence"] += 1
            continue
        gap, xp, cs = gaps[id(r)]
        if gap <= 300:
            other.append(r)
            st["joined_le300"] += 1
            continue
        st["far_all"] += 1
        if gap > a.max:
            st["gap_over_max"] += 1
            continue
        ok = [k for k in cs if res.get(k) is not None and res[k] != r["target"]]
        if ok:
            st["other_key"] += 1
            continue
        st["far_admitted"] += 1
        st["far_xpara_%d" % xp] += 1
        st["far_gap_%d" % ((gap // 300) * 300)] += 1
        r["claim"] = "joinedFar"
        r["rule"] = r["rule"].replace("far9:joined", "far9:joinedFar")
        r["note"] += " xpara=%d" % xp
        far.append(r)
    for name, rs in (("rows_far.jsonl", far), ("rows_other.jsonl", other)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline=NL) as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "split_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
