"""Stage of each traced pair (trace.py output) -> counts. Prints counts only (and, with --show, the per-pair line for
the agent's own reading in this folder; nothing is fed to any rule).

    python -X utf8 anatomy.py work/h0_trace.jsonl [--show]
"""
import collections, json, sys


def stage(r):
    if r.get("stage"):
        return r["stage"], "-"
    if r["rows"]:
        oks = [t for t in r["rows"] if t["verdict"] in ("ok", "okRecognised")]
        if not oks:
            return "d:cert_fail", ",".join(sorted(set(str(t["verdict"]) + ":" + t["kind"] for t in r["rows"])))
        return "e:admitted_not_status", ",".join(t["kind"] for t in oks)
    cite = bool(r["cite_hits"])
    name = r["name_hits"] > 0
    if not cite and not name:
        return ("b:reporter_form_only" if r["vp_miss"] else "b:no_mention"), "-"
    expl = [c for c in r["cue_sents"] if c["explicit"]]
    if not expl:
        return "c:no_explicit_cue_near_mention", ("cite" if cite else "name") + ("+form" if r["vp_miss"] else "")
    # explicit sentence near a mention: what did the reader do?
    rd = r["reader"]
    if not rd:
        return "c:explicit_not_candidate", ("cite" if cite else "name")
    why = []
    for x in rd:
        if x["reject"]:
            why.append("rej:" + x["reject"] + (":Q" if x["in_queue"] else ""))
        elif "llm_main" in x or "llm_hard" in x:
            a = x.get("llm_hard") or x.get("llm_main")
            why.append("llm:" + ("own" if a["own"] else "notown") + ":" + str(a["kind"]))
        elif x["item_targets"] is not None:
            why.append("item:" + ("X" if r["x"] in x["item_targets"] else "noX"))
        else:
            why.append("cand:" + x["sub"])
    return "c:explicit_reader", ";".join(sorted(set(why)))


def main():
    recs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
    show = "--show" in sys.argv
    c1 = collections.Counter()
    c2 = collections.Counter()
    per_x = collections.defaultdict(list)
    for r in recs:
        s, d = stage(r)
        c1[s] += 1
        c2[(s, d)] += 1
        per_x[r["x"]].append(s)
        if show:
            print(s, d, r["x"], r["y"], r["x_name"][:30], "|", r["y_name"][:30], r["y_date"], r["y_repo"],
                  "cite=%d name=%d form=%d" % (len(r["cite_hits"]), r["name_hits"], len(r["vp_miss"])), sep="\t")
    print("pairs", len(recs))
    for k, v in c1.most_common():
        print(v, k, sep="\t")
    print("-- detail")
    for k, v in sorted(c2.items(), key=lambda kv: (kv[0][0], -kv[1])):
        print(v, *k, sep="\t")
    # per X: best (furthest) stage among its Ys
    order = ["a", "b", "c", "d", "e"]
    cx = collections.Counter()
    for x, ss in per_x.items():
        best = max(ss, key=lambda s: (order.index(s[0]), s))
        cx[best] += 1
    print("-- per X (furthest stage over its listed Ys)", len(per_x))
    for k, v in cx.most_common():
        print(v, k, sep="\t")


if __name__ == "__main__":
    main()
