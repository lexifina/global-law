"""Round 7, agent doctrine: reader packs from items.jsonl.

    python -X utf8 make_packs.py [--items items.jsonl] [--size 30] [--all]

Takes the items whose rule verdict is ok (with --all: every item that has a tie sentence), orders them by acting
decision (W) and main offset, and writes packs/pack_NNN.md (about --size items each) and packs/index.tsv
(pack, item id, w, x, label, rule reason). The pack holds the text the reader needs and nothing else: no rule verdict,
no reason, no class. Item id = "<w>:<main start>:<x>".
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = "\n"


def ymd(d):
    d = str(d)
    return "%s-%s-%s" % (d[:4], d[4:6], d[6:8]) if len(d) == 8 else d


def item_md(it):
    iid = "%d:%d:%d" % (it["w"], it["main"][0], it["x"])
    return iid, NL.join([
        "### ITEM " + iid,
        "ACTING: %s, %s, %s, %s" % (it["w_name"], it["w_cite"] or "-", it["w_court_name"], ymd(it["w_date"])),
        "TARGET: %s, %s, %s, %s" % (it["x_name"], it["x_cite"] or "-", it["x_court_name"], ymd(it["x_date"])),
        "LABEL: " + it["label"],
        "",
        "MAIN WINDOW: " + it["main_win"],
        "",
        "MAIN: " + it["main_q"],
        "",
        "TIE WINDOW: " + it["tie_win"],
        "",
        "TIE: " + it["joined_q"],
        "", ""])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=os.path.join(HERE, "items.jsonl"))
    ap.add_argument("--size", type=int, default=30)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--start", type=int, default=1)
    a = ap.parse_args()
    its = [json.loads(l) for l in open(a.items, encoding="utf-8")]
    its = [it for it in its if "joined_q" in it and (a.all or it["rule_ok"])]
    its.sort(key=lambda it: (not it["rule_ok"], it["w"], it["main"][0], it["x"]))
    seen = set()
    uniq = []
    for it in its:
        k = (it["w"], it["main"][0], it["x"])
        if k not in seen:
            seen.add(k)
            uniq.append(it)
    os.makedirs(os.path.join(HERE, "packs"), exist_ok=True)
    idx = []
    n = 0
    ok_n = sum(1 for it in uniq if it["rule_ok"])
    # rule-ok items first, in packs of their own (stratum A); the others (stratum B: rule said no) after
    bounds = []
    for lo, hi in ((0, ok_n), (ok_n, len(uniq))):
        k = max(1, round((hi - lo) / a.size)) if hi > lo else 0
        for j in range(k):
            bounds.append((lo + (hi - lo) * j // k, lo + (hi - lo) * (j + 1) // k))
    for i, i2 in bounds:
        n_ = a.start + n
        name = "pack_%03d" % n_
        body = ["# Doctrine pack %s (%d items). Brief: READER_BRIEF_DOCTRINE.md" % (name, i2 - i), ""]
        for it in uniq[i:i2]:
            iid, md = item_md(it)
            body.append(md)
            idx.append([name, iid, it["w"], it["x"], it["label"], "A" if it["rule_ok"] else "B", it["reason"]])
        with open(os.path.join(HERE, "packs", name + ".md"), "w", encoding="utf-8", newline=NL) as f:
            f.write(NL.join(body))
        n += 1
    with open(os.path.join(HERE, "packs", "index.tsv"), "a" if a.start > 1 else "w", encoding="utf-8", newline=NL) as f:
        for r in idx:
            f.write("\t".join(str(x) for x in r) + NL)
    print("packs", n, "items", len(uniq))


if __name__ == "__main__":
    main()
