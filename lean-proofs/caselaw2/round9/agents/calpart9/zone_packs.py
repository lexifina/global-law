"""calpart9: stratified sample of the decisions whose part map rule PJ / PJ-V changes (work/scan/*.jsonl), plus
controls (marks the rule keeps, from the same scan's decisions and their sections), as reader packs for
READER_BRIEF_ZONES.md.

    python -X utf8 zone_packs.py --n 40 --controls 8 --seed 9 --out zread

Strata: form (index | join | vote) x court group (ca9 | other federal | state). The key (item -> form / changed or
control) goes to <out>/key.tsv, never into the packs. No answer-key file is read.
"""
import argparse
import collections
import glob
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partzone as PZ  # noqa: E402

L = PZ.L
NL = "\n"


def group(repo):
    if repo == "ca9":
        return "ca9"
    if re.fullmatch(r"ca(\d+|dc|fc)(-district)?", repo) or repo in ("supreme-court", "bankruptcy"):
        return "fed"
    return "state"


def passage(text, sec0, m0, stop):
    hl_end = text.find(NL, sec0)
    head = text[sec0:hl_end]
    pre = text[hl_end:m0]
    if len(pre) > 900:
        pre = pre[:300] + "\n[...]\n" + pre[-500:]
    ml_end = text.find(NL, m0)
    ml_end = len(text) if ml_end < 0 else ml_end
    after = text[ml_end:min(stop, ml_end + 1200)]
    tail = "\n[... passage ends: next heading or judge's line follows]" if stop <= ml_end + 1200 and stop < len(text) \
        else ("\n[...]" if ml_end + 1200 < len(text) else "\n[end of text]")
    return head + pre + "▶MARK◀ " + text[m0:ml_end] + after + tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--controls", type=int, default=8)
    ap.add_argument("--seed", type=int, default=9)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pack-size", type=int, default=12)
    a = ap.parse_args()
    out = os.path.join(HERE, a.out)
    os.makedirs(os.path.join(out, "answers"), exist_ok=True)
    recs = []
    for p in sorted(glob.glob(os.path.join(HERE, "work", "scan", "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["kind"] == "PJ" and "pm2" in r:
                recs.append(r)
    strata = collections.defaultdict(list)
    for r in recs:
        form = r["pm2"]["changes"][0][5]
        strata[(form, group(r["repo"]))].append(r)
    rnd = random.Random(a.seed)
    keys = sorted(strata)
    per = max(1, a.n // len(keys))
    pick = []
    for k in keys:
        rs = sorted(strata[k], key=lambda r: r["n"])
        pick += [(k, r) for r in rnd.sample(rs, min(per, len(rs)))]
    rest = [(k, r) for k in keys for r in strata[k] if (k, r) not in pick]
    rnd.shuffle(rest)
    pick += rest[:max(0, a.n - len(pick))]
    texts = L.fetch_texts([r["n"] for _, r in pick])
    items = []
    for k, r in pick:
        t = texts[r["n"]][1]
        _hw, pm, new, ch = PZ.part_maps(t)
        if not ch:
            continue
        c = ch[0]
        nxt = [x[0] for x in new if x[0] > c[1]]
        stop = min(nxt) if nxt else len(t)
        items.append({"n": r["n"], "repo": r["repo"], "date": r["date"], "kind": "changed", "form": c[5],
                      "stratum": "%s/%s" % k, "text": passage(t, c[0], c[1], stop)})
    # controls: separate-opinion marks right after a short opening of a court section that the rule keeps
    cands = []
    for p in sorted(glob.glob(os.path.join(HERE, "work", "scan", "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["kind"] in ("cut_only", "dissent_note"):
                cands.append(r)
    rnd.shuffle(cands)
    ctl = 0
    for r in cands:
        if ctl >= a.controls:
            break
        t = L.fetch_texts([r["n"]])[r["n"]][1]
        _hw, pm, new, ch = PZ.part_maps(t)
        for i, (x0, x1, p, s) in enumerate(new):
            if p in ("concurrence~", "dissent~") and i and new[i - 1][2] in PZ.PF.BASE_PARTS:
                sec0 = t.rfind("\n## ", 0, x0) + 1
                if x0 - sec0 > 1500:
                    continue
                items.append({"n": r["n"], "repo": r["repo"], "date": r["date"], "kind": "control", "form": "-",
                              "stratum": "control", "text": passage(t, sec0, x0, x1)})
                ctl += 1
                break
    rnd.shuffle(items)
    with open(os.path.join(out, "key.tsv"), "w", encoding="utf-8", newline=NL) as fk:
        for i, it in enumerate(items):
            it["id"] = "p%03d" % (i + 1)
            fk.write("\t".join([it["id"], str(it["n"]), it["repo"], it["kind"], it["form"], it["stratum"]]) + NL)
    F = L.Facts()
    for k in range(0, len(items), a.pack_size):
        with open(os.path.join(out, "pack_%02d.md" % (k // a.pack_size + 1)), "w", encoding="utf-8",
                  newline=NL) as f:
            f.write("# Pack %d\n\n" % (k // a.pack_size + 1))
            for it in items[k:k + a.pack_size]:
                f.write("### ITEM %s\n\nCOURT: %s; DATE: %s\n\nTEXT:\n\n````\n%s\n````\n\n" % (
                    it["id"], F.court_name(int(F.court[it["n"]])), it["date"], it["text"]))
    print("items", len(items), collections.Counter(it["stratum"] for it in items))


if __name__ == "__main__":
    main()
