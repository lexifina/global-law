"""Round 5, agent `recog`: reader packs from items.jsonl.gz and items_t1s.jsonl.gz.

    python -X utf8 build_packs.py [--size 50] [--seed 20261113]

packs/pack_T0_<nnn>.md    the 179 round-4 witness rows (re-read under the round-5 rule)
packs/pack_T1_<nnn>.md    X is a US Supreme Court decision, from the feed notes (pairs not yet explicit first)
packs/pack_T1s_<nnn>.md   X, Y, W Supreme Court decisions, from our own scan of the Supreme Court's opinions; order:
                          strict-form statements of pairs not yet explicit, strict-form of explicit pairs, then the
                          loose ones (two decisions near an overruling word; mostly not statements)
packs/pack_T2_<nnn>.md    other X, notes of scope `all`, then `partialUnknown`; inside each group the (Y, X) pairs
                          in a seeded random order, a pair's candidates together by W's date
packs/index.tsv           item id, pack, tier, W, X, Y, note scope
packs/summary.json        packs and items per tier
Not packed: T2 notes of scope otherGrounds (tier T2p: certify_pattern.py, no reader) and T3 (candidates.tsv).
The other-grounds packs of the first build are in packs_unused/ (stale: no INTRO field).
"""
import argparse
import collections
import glob
import json
import math
import os
import random
import sys

import recog_common as R


def fdate(d):
    return "%04d-%02d-%02d" % (d // 10000, d // 100 % 100, d % 100) if d else "unknown date"


def case(d, year=True):
    nm = " ".join((d["name"] or "(no caption)").split())
    if len(nm) > 170:
        nm = nm[:170] + "..."
    # the corpus lists parallel citations joined by "|"; show up to three reporter citations (no LEXIS / WL / database
    # ids, which never stand in an opinion's text)
    cs = [c.strip() for c in (d["cite"] or "").split("|")]
    cs = [c for c in cs if c and "LEXIS" not in c and not c.startswith("SCDB") and " WL " not in c][:3]
    s = nm + (", " + "; ".join(cs) if cs else "")
    return s + (" (%d)" % (d["date"] // 10000) if year and d["date"] else "")


def render(it):
    a, b = it["d0"] - it["s0"], it["d1"] - it["s0"]
    win = R.clean(it["text"][a:b])
    na = it["off"] - it["s0"]
    nb = (it.get("note_end") or it["off"] + 40) - it["s0"]
    focus = R.clean(it["text"][max(a, na - 90):min(b, nb + 90)])
    lines = ["### ITEM %s" % it["id"],
             "W (the stating decision): %s; %s, %s. Opinion part at the note: %s" % (
                 case(it["W"], False), it["W"]["court"], fdate(it["W"]["date"]), it["part"]),
             "X (the earlier decision): %s" % case(it["X"]),
             "Y (the decision said to have done it): %s" % case(it["Y"])]
    others = sorted({p[2] for p in it.get("parts", []) if p[0] < it["d1"] and p[1] > it["d0"]} - {it["part"]})
    if others:
        lines.append("CAUTION: the window also holds text of another part (%s). Quote only the part that holds the "
                     "NOTE AT text." % ", ".join(others))
    if it.get("intro"):
        lines.append("INTRO (how the paragraph, footnote or list that holds the note begins; context only, never "
                     "quoted):\n" + it["intro"])
    lines.append("WINDOW:\n" + win)
    lines.append("NOTE AT:\n" + focus)
    return "\n".join(lines)


def chunks(items, size):
    n = max(1, math.ceil(len(items) / size))
    per = math.ceil(len(items) / n)
    return [items[i:i + per] for i in range(0, len(items), per)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261113)
    a = ap.parse_args()
    items = R.load_items()
    out = os.path.join(R.HERE, "packs")
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "pack_*.md")):
        if not os.path.basename(f).startswith("pack_T1f_"):      # tier T1f belongs to build_t1f.py
            os.remove(f)
    tiers = collections.defaultdict(list)
    for it in items.values():
        tiers[it["tier"]].append(it)
    index, summary = [], collections.OrderedDict()

    def emit(tier, packs):
        for k, pk in enumerate(packs):
            name = "pack_%s_%03d.md" % (tier, k + 1)
            R.write_text(os.path.join(out, name), "\n\n".join(render(it) for it in pk) + "\n")
            for it in pk:
                index.append([it["id"], name, tier, it["w"], it["x"], it["y"], it["note_scope"]])
        summary[tier] = {"packs": len(packs), "items": sum(len(p) for p in packs),
                         "items_with_intro": sum(1 for p in packs for it in p if it.get("intro"))}

    emit("T0", chunks(sorted(tiers["T0"], key=lambda it: it["id"]), a.size))
    emit("T1", chunks(sorted(tiers["T1"], key=lambda it: (it["pair_explicit"], it["X"]["date"], it["x"], it["y"],
                                                          it["rank"])), a.size))

    t1s = sorted(tiers["T1s"], key=lambda it: (0 if it["strict"] and not it["pair_explicit"] else
                                               1 if it["strict"] else 2, it["X"]["date"], it["x"], it["y"],
                                               it["rank"]))
    groups = [[it for it in t1s if it["strict"] and not it["pair_explicit"]],
              [it for it in t1s if it["strict"] and it["pair_explicit"]],
              [it for it in t1s if not it["strict"]]]
    packs, first = [], {}
    for name, g in zip(("strict, pair not explicit", "strict, pair already explicit", "loose"), groups):
        if g:
            first[name] = "pack_T1s_%03d.md" % (len(packs) + 1)
            packs.extend(chunks(g, a.size))
    emit("T1s", packs)
    summary["T1s"]["groups"] = {n: len(g) for n, g in zip(("strict_not_explicit", "strict_explicit", "loose"), groups)}
    summary["T1s"]["first_pack_of_group"] = first

    rnd = random.Random(a.seed)
    packs, first = [], {}
    for sc in ("all", "partialUnknown"):
        pairs = collections.defaultdict(list)
        for it in tiers["T2"]:
            if it["note_scope"] == sc:
                pairs[(it["y"], it["x"])].append(it)
        keys = sorted(pairs)
        rnd.shuffle(keys)
        order = []
        for k in keys:
            order.extend(sorted(pairs[k], key=lambda it: it["rank"]))
        if order:
            first[sc] = "pack_T2_%03d.md" % (len(packs) + 1)
            packs.extend(chunks(order, a.size))
    emit("T2", packs)
    summary["T2"]["first_pack_of_scope_group"] = first
    summary["T2"]["not_packed_other_grounds (tier T2p)"] = sum(1 for it in tiers["T2"]
                                                               if it["note_scope"] == "otherGrounds")
    summary["T3"] = {"packs": 0, "items": 0, "not_packed": len(tiers["T3"])}
    R.write_rows(os.path.join(out, "index.tsv"), index)
    old = os.path.join(out, "unpacked_T2.tsv")
    if os.path.exists(old):
        os.remove(old)
    R.write_text(os.path.join(out, "summary.json"), json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
