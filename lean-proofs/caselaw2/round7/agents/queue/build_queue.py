"""Round 7, agent `queue`: inventory of the recognised-overruling reading (round 5) and the reading queue for B1.

    python -X utf8 build_queue.py [--size 50] [--shard 4]

Inventory (inventory.json; INVENTORY.md is written from it by hand):
  every pack of round5/recog/packs/ and packs_unused/ with tier, items, items answered by the main model (ans/),
  items pre-screened only (ans_prescreen/), unread; the feed funnel (stats.json, dropped_stats.json); the pattern
  tier; and, counted only, the other queues (round5/opwords, work/round3/queue, work/round3/implicit,
  work/round2/recall).

Queue (items never read by the main model, never certified by pattern, and certifiable in principle):
  OG   T2 items whose feed note says "other grounds" and that certify_pattern.py did not certify (no strict match,
       or refused by the certifier)
  T3   T3 items (pair explicit-all-ok in the round-4 model)
  CUT  feed statements dropped by the "3 earliest W per (Y, X, scope group)" cut (items_dropped.jsonl.gz)
  T1F  T1f items (loose Supreme Court scan, cut to the certifiable) that only the smaller pre-screen model read
  MISS items of an answered pack with no answer line (none expected)
Not queued (and counted): items answered by the main model; pattern-certified items; T1s loose items that
build_t1f.py proved uncertifiable (T1f_dropped.tsv); statements whose W has no power, Y shown to lack power,
dates, a dissent / concurrence / head-matter part, repeats of the same (W, X, Y, scope) in one W.

Priority (speaker power and pair novelty only; no answer key, no held-out note):
  every queued W has power over X (reference can_change(W, X) = yes, recomputed here);
  P1 = the (Y, X) pair has no admitted row (treatments row by Y on X, kind overruled / abrogated / disapproved /
       recededFrom, result_all ok*) in the base build round6/history/stage/final2 (+ out/final2/certs.tsv);
  P2 = it has admitted rows, none of scope `all`;  P3 = it has an admitted scope-`all` row.
  Inside a priority: source order CUT, OG, T3, T1F (typed feed notes first, the loose scan last); then Y's power
  known before unknown; then by pair (a pair's statements together, by W's date).

Leak check on every packed item: a feed-derived item's statement id is in round5/tests/split/feed_ids.tsv with the
same (note_node, target_node, by_node) = (W, X, Y); every item's W has power over X (can_change = yes) or sits in
X's court. The holdout file is never opened (DESIGN7 0.2).

Writes (this folder): packs/pack_<P>_<SRC>_<nnn>.md (round-5 item format, build_packs.render), packs/index.tsv
(pack, items, tier, priority, source), packs/items_index.tsv (round-5 index columns: item id, pack, tier, W, X, Y,
note scope; then priority, source), items_queue.jsonl.gz (every queued item, for certify_recog.py --items),
inventory.json, leak_check.json, leak_check_failures.tsv, SHARDS.md.
"""
import argparse
import collections
import glob
import gzip
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RECOG = os.path.join(C2, "round5", "recog")
sys.path.insert(0, RECOG)
import recog_common as R  # noqa: E402
import build_packs  # noqa: E402  (render only; its main() is never called)

BASE = os.path.join(C2, "round6", "history", "stage", "final2")
BASE_OUT = os.path.join(C2, "round6", "history", "out", "final2")
PACKS = os.path.join(HERE, "packs")
SRC_ORDER = ("CUT", "OG", "T3", "T1F", "MISS")


def jsonl_ids(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            out[str(r["id"]).strip()] = r
        except Exception:
            pass
    return out


def pack_items(path):
    return re.findall(r"(?m)^### ITEM (\S+)", open(path, encoding="utf-8").read())


def pack_blocks(path):
    t = open(path, encoding="utf-8").read()
    out = {}
    for b in re.split(r"(?m)^### ITEM ", t)[1:]:
        out[b.split("\n", 1)[0].strip()] = "### ITEM " + b.rstrip("\n")
    return out


def chunks(items, size):
    n = max(1, math.ceil(len(items) / size))
    per = math.ceil(len(items) / n)
    return [items[i:i + per] for i in range(0, len(items), per)]


def count_queue(dirpath, pack_glob, ans_name):
    """(packs, answered, unread names) for a queue whose answers sit next to or under the packs."""
    packs = sorted(glob.glob(os.path.join(dirpath, pack_glob)))
    unread = []
    for p in packs:
        if not os.path.exists(ans_name(p)):
            unread.append(os.path.basename(p))
    return len(packs), len(packs) - len(unread), unread


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--shard", type=int, default=4)
    a = ap.parse_args()
    inv = collections.OrderedDict()

    # ---------------------------------------------------------------- round-5 items and what was read
    items = R.load_items()                               # items.jsonl.gz + items_t1s.jsonl.gz
    dropped_items = R.load_items(os.path.join(HERE, "items_dropped.jsonl.gz"))
    assert not set(items) & set(dropped_items), "dropped ids collide with round-5 items"
    main_ans = {}
    for f in sorted(glob.glob(os.path.join(RECOG, "ans", "ans_*.jsonl"))):
        for i, r in jsonl_ids(f).items():
            main_ans[i] = r
    pre_ans = {}
    for f in sorted(glob.glob(os.path.join(RECOG, "ans_prescreen", "ans_*.jsonl"))):
        for i, r in jsonl_ids(f).items():
            pre_ans[i] = r

    def is_true(r):
        return r.get("states") in (True, 1, "true", "True", "yes")

    # pack inventory
    rows = []
    packed_ids = {}
    for d, label in ((os.path.join(RECOG, "packs"), "packs"), (os.path.join(RECOG, "packs_unused"), "packs_unused")):
        for p in sorted(glob.glob(os.path.join(d, "pack_*.md"))):
            name = os.path.basename(p)
            ids = pack_items(p)
            tiers = collections.Counter(items[i]["tier"] if i in items else "?" for i in ids)
            tier = name.split("_")[1]
            ansf = os.path.join(RECOG, "ans", "ans_" + name[:-3] + ".jsonl")
            pref = os.path.join(RECOG, "ans_prescreen", "ans_" + name[:-3] + ".jsonl")
            n_main = sum(1 for i in ids if i in main_ans)
            n_pre = sum(1 for i in ids if i in pre_ans and i not in main_ans)
            n_pre_pos = sum(1 for i in ids if i in pre_ans and is_true(pre_ans[i]))
            n_pre_pos_reread = sum(1 for i in ids if i in pre_ans and is_true(pre_ans[i]) and i in main_ans)
            rows.append({"dir": label, "pack": name, "tier": tier, "item_tiers": dict(tiers), "items": len(ids),
                         "answer_file_main": os.path.exists(ansf), "answered_main": n_main,
                         "answer_file_prescreen": os.path.exists(pref), "prescreen_only": n_pre,
                         "prescreen_pos": n_pre_pos, "prescreen_pos_reread_main": n_pre_pos_reread,
                         "unread": len(ids) - n_main - n_pre})
            if label == "packs":
                for i in ids:
                    packed_ids.setdefault(i, name)
    inv["packs"] = rows
    agg = collections.OrderedDict()
    for r in rows:
        k = "%s/%s" % (r["dir"], r["tier"])
        g = agg.setdefault(k, collections.Counter())
        g["packs"] += 1
        g["items"] += r["items"]
        g["answered_main"] += r["answered_main"]
        g["prescreen_only"] += r["prescreen_only"]
        g["unread"] += r["unread"]
        g["packs_with_main_answer_file"] += int(r["answer_file_main"])
        g["packs_with_prescreen_file"] += int(r["answer_file_prescreen"])
        g["packs_fully_unread"] += int(r["answered_main"] == 0 and r["prescreen_only"] == 0)
        g["prescreen_pos"] += r["prescreen_pos"]
        g["prescreen_pos_reread_main"] += r["prescreen_pos_reread_main"]
    inv["packs_by_dir_tier"] = {k: dict(v) for k, v in agg.items()}
    inv["main_answer_ids"] = len(main_ans)
    inv["main_answer_ids_without_item"] = sorted(set(main_ans) - set(items))[:20]
    inv["main_answers_by_tier"] = dict(collections.Counter(items[i]["tier"] for i in main_ans if i in items))
    inv["main_answers_states_true_by_tier"] = dict(collections.Counter(
        items[i]["tier"] for i in main_ans if i in items and is_true(main_ans[i])))
    inv["prescreen_ids"] = len(pre_ans)
    inv["prescreen_states_true"] = sum(1 for r in pre_ans.values() if is_true(r))

    # packs_unused: which of its items are T2 other-grounds, pattern status
    unused_ids = set()
    for p in glob.glob(os.path.join(RECOG, "packs_unused", "pack_*.md")):
        unused_ids.update(pack_items(p))

    # pattern tier
    pat_matched = set(jsonl_ids(os.path.join(RECOG, "pattern", "ans", "ans_pattern.jsonl")))
    pat_refused = {p[0] for p in R.read_rows(os.path.join(RECOG, "cert_pattern", "rejects.tsv"), 2)}
    pat_cert = pat_matched - pat_refused
    pat_nomatch = {p[0]: p[1] for p in R.read_rows(os.path.join(RECOG, "pattern", "pattern_rejects.tsv"), 2)}
    og = [it for it in items.values() if it["tier"] == "T2" and it["note_scope"] == "otherGrounds"]
    inv["pattern"] = {"T2_other_grounds_items": len(og), "matched": len(pat_matched),
                      "refused_by_certifier": len(pat_refused & pat_matched), "certified": len(pat_cert),
                      "no_match": len(pat_nomatch),
                      "no_match_reasons": dict(collections.Counter(pat_nomatch.values())),
                      "refused_reasons": dict(collections.Counter(
                          p[2].split(":")[0] for p in R.read_rows(os.path.join(RECOG, "cert_pattern", "rejects.tsv"), 3))),
                      "staged_rows": len(R.read_rows(os.path.join(RECOG, "cert_pattern", "rows_info.tsv"), 2)) - 1,
                      "spare_rows": len(R.read_rows(os.path.join(RECOG, "cert_pattern", "rows_spare.tsv"), 2))}
    unused_t2og = {i for i in unused_ids if i in items and items[i]["tier"] == "T2" and items[i]["note_scope"] == "otherGrounds"}
    inv["packs_unused_items"] = {
        "distinct_ids": len(unused_ids), "in_round5_items": len(unused_ids & set(items)),
        "T2_other_grounds": len(unused_t2og), "of_which_pattern_certified": len(unused_t2og & pat_cert),
        "of_which_not_certified": len(unused_t2og - pat_cert),
        "not_in_round5_items (stale first build)": len(unused_ids - set(items)),
        "T2_other_grounds_items_not_in_packs_unused": len({it["id"] for it in og} - unused_ids)}

    t1f_dropped = {p[0]: p[1] for p in R.read_rows(os.path.join(RECOG, "packs", "T1f_dropped.tsv"), 2)}
    t1f_index = {p[0]: p[1] for p in R.read_rows(os.path.join(RECOG, "packs", "index_T1f.tsv"), 2)}

    # ---------------------------------------------------------------- queue selection
    queue = []
    why_not = collections.Counter()
    t1f_blocks = {}
    for p in sorted(glob.glob(os.path.join(RECOG, "packs", "pack_T1f_*.md"))):
        t1f_blocks.update(pack_blocks(p))
    for i, it in items.items():
        tier = it["tier"]
        if i in main_ans:
            why_not["answered-main:" + tier] += 1
            continue
        if tier == "T0":
            why_not["T0-unanswered"] += 1
            continue
        if tier == "T2" and it["note_scope"] == "otherGrounds":
            if i in pat_cert:
                why_not["T2-otherGrounds-pattern-certified"] += 1
                continue
            queue.append(("OG", it))
            continue
        if tier == "T3":
            queue.append(("T3", it))
            continue
        if tier == "T1s":
            if i in t1f_index:
                queue.append(("T1F", it))
                continue
            if i in t1f_dropped:
                why_not["T1s-loose-uncertifiable:" + t1f_dropped[i]] += 1
                continue
            if not it.get("strict"):
                why_not["T1s-loose-other"] += 1
                continue
        # T1, T2 (all / partial), T1s strict that were packed but have no answer line
        if i in packed_ids:
            queue.append(("MISS", it))
        else:
            why_not["unpacked-other:" + tier] += 1
    for i, it in dropped_items.items():
        queue.append(("CUT", it))
    inv["not_queued"] = dict(sorted(why_not.items()))
    inv["t1f"] = {"items": len(t1f_index), "prescreened": sum(1 for i in t1f_index if i in pre_ans),
                  "prescreen_true": sum(1 for i in t1f_index if i in pre_ans and is_true(pre_ans[i])),
                  "prescreen_true_reread_main": sum(1 for i in t1f_index if i in pre_ans and is_true(pre_ans[i])
                                                    and i in main_ans),
                  "reread_main_states_true": sum(1 for i in t1f_index if i in main_ans and is_true(main_ans[i])),
                  "prescreen_false_never_main": sum(1 for i in t1f_index if i in pre_ans and not is_true(pre_ans[i])
                                                    and i not in main_ans),
                  "not_prescreened_not_main": sum(1 for i in t1f_index if i not in pre_ans and i not in main_ans),
                  "dropped_uncertifiable": len(t1f_dropped)}

    # ---------------------------------------------------------------- power, leak check, pair novelty
    C = R.tests_common()
    E, _pr, _meta = C.lite_engine(R.DATA)
    D = E.D
    feed = {}
    with open(R.FEED, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {h: k for k, h in enumerate(head)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            feed[int(p[ix["id"]])] = (int(p[ix["note_node"]]), int(p[ix["target_node"]]), int(p[ix["by_node"]]))
    leak = collections.Counter()
    fails = []
    pw = {}
    for src, it in queue:
        w, x, y = it["w"], it["x"], it["y"]
        if "sid" in it:
            fr = feed.get(int(it["sid"]))
            if fr is None:
                fails.append([it["id"], src, "statement-not-in-feed", w, x, y])
                leak["statement-not-in-feed"] += 1
            elif fr != (w, x, y):
                fails.append([it["id"], src, "feed-row-differs:%s" % (fr,), w, x, y])
                leak["feed-row-differs"] += 1
            else:
                leak["feed-statement-ok"] += 1
        else:
            leak["own-scan-no-statement-id"] += 1
        if (w, x) not in pw:
            pw[(w, x)] = E.can_change(w, x, "unknown")
        cc = pw[(w, x)]
        same_court = D.has(w) and D.has(x) and D.court[w] == D.court[x]
        if cc[0] == "yes":
            leak["w-power-yes"] += 1
        elif same_court:
            leak["w-same-court-power-%s" % cc[0]] += 1
        else:
            fails.append([it["id"], src, "w-power-%s:%s" % cc, w, x, y])
            leak["w-power-not-yes"] += 1
        if (y, x) not in pw:
            pw[(y, x)] = E.can_change(y, x, "unknown")
        it["_ypower"] = pw[(y, x)][0]
    bad = {f[0] for f in fails}
    inv["leak_check"] = dict(leak)
    inv["leak_check_failures"] = len(fails)
    R.write_rows(os.path.join(HERE, "leak_check_failures.tsv"), [["id", "src", "why", "w", "x", "y"]] + fails)
    queue = [(s, it) for s, it in queue if it["id"] not in bad]

    certs = {}
    with open(os.path.join(BASE_OUT, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] == "treatment":
                certs[p[1]] = p[2]
    admitted = collections.defaultdict(set)
    for p in R.read_rows(os.path.join(BASE, "treatments.tsv"), 16):
        if p[4] in R.NEG_KINDS and certs.get(p[0], "").startswith("ok"):
            admitted[(int(p[1]), int(p[2]))].add(p[5])
    inv["base_admitted_pairs"] = len(admitted)

    def prio(it):
        sc = admitted.get((it["y"], it["x"]))
        if not sc:
            return "P1"
        return "P3" if "all" in sc else "P2"

    groups = collections.defaultdict(list)
    for src, it in queue:
        it["priority"] = prio(it)
        it["queue_src"] = src
        groups[(it["priority"], src, it["tier"])].append(it)

    # ---------------------------------------------------------------- packs
    os.makedirs(PACKS, exist_ok=True)
    for f in glob.glob(os.path.join(PACKS, "pack_*.md")):
        os.remove(f)
    tier_order = {"T1": 0, "T2": 1, "T3": 2, "T1s": 3}
    keys = sorted(groups, key=lambda k: (k[0], SRC_ORDER.index(k[1]), tier_order.get(k[2], 9)))
    index, iindex, out_items, render_mismatch = [], [], [], 0
    seq = collections.Counter()
    for (pri, src, tier) in keys:
        g = groups[(pri, src, tier)]
        bypair = collections.defaultdict(list)
        for it in g:
            bypair[(it["y"], it["x"])].append(it)
        pk = sorted(bypair, key=lambda k: (0 if bypair[k][0]["_ypower"] == "yes" else 1,
                                           min(t["X"]["date"] for t in bypair[k]), k))
        order = []
        for k in pk:
            order.extend(sorted(bypair[k], key=lambda t: (t["W"]["date"], t["w"], t["id"])))
        label = src if src in ("T1F", "MISS") else "%s%s" % (src, "" if src in ("OG", "T3") else "-" + tier)
        for chunk in chunks(order, a.size):
            seq[(pri, label)] += 1
            name = "pack_%s_%s_%03d.md" % (pri, label.replace("-", ""), seq[(pri, label)])
            blocks = []
            for it in chunk:
                b = build_packs.render(it)
                if it["id"] in t1f_blocks:
                    if t1f_blocks[it["id"]] != b:
                        render_mismatch += 1
                    b = t1f_blocks[it["id"]]          # T1f: the round-5 pack text, copied
                blocks.append(b)
                iindex.append([it["id"], name, tier, it["w"], it["x"], it["y"], it["note_scope"], pri, src])
            R.write_text(os.path.join(PACKS, name), "\n\n".join(blocks) + "\n")
            index.append([name, len(chunk), tier, pri, src])
        out_items.extend(order)
    inv["t1f_render_mismatch"] = render_mismatch
    R.write_rows(os.path.join(PACKS, "index.tsv"), [["pack", "items", "tier", "priority", "source"]] + index)
    R.write_rows(os.path.join(PACKS, "items_index.tsv"), iindex)
    with gzip.open(os.path.join(HERE, "items_queue.jsonl.gz.part"), "wt", encoding="utf-8", newline="\n") as f:
        for it in out_items:
            o = {k: v for k, v in it.items() if not k.startswith("_")}
            o["y_power"] = it["_ypower"]
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    os.replace(os.path.join(HERE, "items_queue.jsonl.gz.part"), os.path.join(HERE, "items_queue.jsonl.gz"))

    q = collections.OrderedDict()
    for (pri, src, tier) in keys:
        q["%s|%s|%s" % (pri, src, tier)] = len(groups[(pri, src, tier)])
    inv["queue_items"] = q
    inv["queue_total"] = len(out_items)
    inv["queue_by_priority"] = dict(collections.Counter(it["priority"] for it in out_items))
    inv["queue_by_source"] = dict(collections.Counter(it["queue_src"] for it in out_items))
    inv["queue_by_tier"] = dict(collections.Counter(it["tier"] for it in out_items))
    inv["queue_by_note_scope"] = dict(collections.Counter(
        "%s|%s" % (it["queue_src"], it["note_scope"]) for it in out_items))
    inv["queue_pairs"] = len({(it["y"], it["x"]) for it in out_items})
    inv["queue_pairs_P1"] = len({(it["y"], it["x"]) for it in out_items if it["priority"] == "P1"})
    inv["queue_ypower"] = dict(collections.Counter(it["_ypower"] for it in out_items))
    inv["packs_written"] = len(index)

    # ---------------------------------------------------------------- other queues (counted only)
    oth = collections.OrderedDict()
    ow = os.path.join(C2, "round5", "opwords", "packs")
    n, done, unread = count_queue(ow, "pack_*.md", lambda p: os.path.join(
        C2, "round5", "opwords", "ans", "ans_" + os.path.basename(p)[:-3] + ".jsonl"))
    oth["round5/opwords (agent opwords)"] = {"packs": n, "answered": done, "unread": unread,
                                             "items_unpacked_L": len(R.read_rows(os.path.join(ow, "unpacked_L.tsv")))}
    rq = os.path.join(C2, "work", "round3", "queue", "packs")
    n, done, unread = count_queue(rq, "pack_*.txt", lambda p: os.path.join(
        rq, "ans_" + os.path.basename(p)[5:-4] + ".jsonl"))
    oth["work/round3/queue (own-act, READER_BRIEF2)"] = {"packs": n, "answered": done, "unread_n": len(unread),
                                                        "partial": sorted(os.path.basename(x) for x in glob.glob(os.path.join(rq, "*.partial"))),
                                                        "unread_first_last": [unread[:1], unread[-1:]]}
    for d in ("work/round3/implicit", "work/round2/recall"):
        pd = os.path.join(C2, *d.split("/"), "packs")
        n, done, unread = count_queue(pd, "pack_*.txt", lambda p, d=d: os.path.join(
            os.path.dirname(p) if d.endswith("recall") else os.path.join(C2, *d.split("/"), "ans"),
            "ans_" + os.path.basename(p)[5:-4] + ".jsonl"))
        oth[d] = {"packs": n, "answered": done, "unread": unread}
    inv["other_queues"] = oth

    shards = chunks(index, a.shard)      # balanced: 3-4 packs each when there are 6 or more packs
    lines = ["# Shards of the B1 reading queue (agent `queue`, round 7)", "",
             "Each shard is 3-4 packs for one reader sub-agent, in priority order (P1 first). Brief: "
             "`round7/agents/queue/READER_BRIEF_RECOG.md`; packs in `round7/agents/queue/packs/`; answers to "
             "`round7/agents/queue/ans/ans_<pack name without .md>.jsonl`; then `bash round7/agents/queue/certify.sh`.",
             "", "| shard | packs | items | priority | sources |", "|---|---|---|---|---|"]
    for k, sh in enumerate(shards):
        lines.append("| S%03d | %s | %d | %s | %s |" % (k + 1, " ".join(p[0] for p in sh), sum(p[1] for p in sh),
                                                       "/".join(sorted({p[3] for p in sh})),
                                                       "/".join(sorted({p[4] for p in sh}))))
    R.write_text(os.path.join(HERE, "SHARDS.md"), "\n".join(lines) + "\n")
    inv["shards"] = len(shards)
    R.write_text(os.path.join(HERE, "inventory.json"), json.dumps(inv, indent=1) + "\n")
    R.write_text(os.path.join(HERE, "leak_check.json"), json.dumps(
        {"checked_items": len(out_items) + len(fails), "failures": len(fails), "counts": dict(leak),
         "holdout_file_opened": False}, indent=1) + "\n")
    print(json.dumps({k: v for k, v in inv.items() if k != "packs"}, indent=1))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
