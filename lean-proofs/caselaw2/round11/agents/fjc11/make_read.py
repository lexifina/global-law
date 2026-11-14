"""fjc11: reader packs over the X2 rows (corpus text only; readers never see the row's kind / scope / rule).

    python -X utf8 make_read.py rows_x2.jsonl work/feat_n2.tsv work/read PER_GROUP PER_PACK [--exclude FILE ...]

Groups by tie combination: HK* (any K), HU, HT, HUT. Per group PER_GROUP rows (seeded random; up to a third status
kinds). Writes work/read/pack_<i>.md and work/read/items.tsv (item id -> row; reader-blind).
"""
import collections, csv, hashlib, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)
STATUS = ("reversed", "vacated", "modified")


def group(t):
    if "K" in t:
        return "HK*"
    if "U" in t and "T" in t:
        return "HUT"
    return "HU" if "U" in t else "HT"


def front(T):
    m = re.match(r"---\n(.*?)\n---\n", T, re.S)
    return (m.group(1), T[m.end():]) if m else ("", T)


def main():
    src, feat, out, per_group, per_pack = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    excl = set()
    for i, a in enumerate(sys.argv):
        if a == "--exclude":
            excl |= {l.split("\t")[0].strip() for l in open(sys.argv[i + 1], encoding="utf-8") if l.strip()}
    os.makedirs(out, exist_ok=True)
    rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    F = {(int(r["by"]), int(r["target"])): r for r in csv.DictReader(open(feat, encoding="utf-8"), delimiter="\t")}
    by = collections.defaultdict(list)
    for r in rows:
        rid = "%d:%d" % (r["by"], r["target"])
        if rid in excl:
            continue
        by[group(F[(r["by"], r["target"])]["ties"])].append(r)
    rnd = random.Random(1111)
    pick = []
    for g in sorted(by):
        rs = by[g][:]
        rnd.shuffle(rs)
        st = [r for r in rs if r["kind"] in STATUS][:per_group // 3]
        ot = [r for r in rs if r not in st][:per_group - len(st)]
        pick += [(g, r) for r in st + ot]
    rnd.shuffle(pick)
    texts = L.fetch_texts({x for _, r in pick for x in (r["by"], r["target"])})
    with open(os.path.join(out, "items.tsv"), "w", encoding="utf-8", newline=NL) as fi:
        fi.write("item\tpack\tgroup\tby\ttarget\tkind\tscope\tties\tflags" + NL)
        packs = collections.defaultdict(list)
        for i, (g, r) in enumerate(pick):
            item = "r" + hashlib.sha1(("fjc11read%d:%d" % (r["by"], r["target"])).encode()).hexdigest()[:6]
            p = i // per_pack + 1
            f = F[(r["by"], r["target"])]
            fi.write("\t".join(map(str, [item, p, g, r["by"], r["target"], r["kind"], r["scope"], f["ties"],
                                         f["flags"]])) + NL)
            dfm, dbody = front(texts.get(r["by"], ("", ""))[1])
            jfm, jbody = front(texts.get(r["target"], ("", ""))[1])
            T = L.norm(texts.get(r["by"], ("", ""))[1])
            a0, a1 = r["anchor"]
            q0, q1 = r["disp"]
            jn = L.node_row(r["target"])
            dn = L.node_row(r["by"])
            s = ["## Item %s" % item, "",
                 "### Decision X (the decision to check)", "- file: %s" % jn[2], "- name: %s" % jn[6],
                 "- date: %s" % jn[4], "- citation: %s" % jn[5],
                 "- front matter:", "```", jfm[:900], "```", "- opening of X's text:", "```",
                 jbody.strip()[:1200], "```", "",
                 "### Acting opinion Y (court of appeals)", "- file: %s" % dn[2], "- name: %s" % dn[6],
                 "- date: %s" % dn[4], "- front matter:", "```", dfm[:700], "```",
                 "- Y head matter / opening (first 2,500 characters):", "```", dbody.strip()[:2500], "```",
                 "- Y passage around its citation of X:", "```", T[max(0, a0 - 900):a1 + 900], "```",
                 "- Y passage around its disposition:", "```", T[max(0, q0 - 700):q1 + 500], "```",
                 "- Y closing (last 1,200 characters):", "```", T[-1200:], "```", ""]
            packs[p].append(NL.join(s))
    for p, items in packs.items():
        with open(os.path.join(out, "pack_%d.md" % p), "w", encoding="utf-8", newline=NL) as f:
            f.write(("# fjc11 reader pack %d (%d items)" % (p, len(items))) + NL + NL + (NL + NL).join(items) + NL)
        print("pack", p, len(items))


if __name__ == "__main__":
    main()
